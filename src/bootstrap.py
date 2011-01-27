#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2011/01/17

@author: aikawa
'''
import logging
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
from math import log
from collections import defaultdict
from util import pairwise
from optparse import OptionParser
import document
import product
import sys
import codecs
logging.basicConfig(level=logging.DEBUG)

initialYMax = 10
initialVMax = 10
seedDictY = [(36,u'デザイン'),(36,u'機能'),(51,u'機能性'),(51,u'操作性'),(38,u'音'),(38,u'音質'),(51,u'使用感'),(38,u'液晶')]
seedDictV = [(10,u'良い'),(36,u'満足'),(37,u'問題')]


def findSeed(targetCID, useTfIdf=True):
    import vocab
    dictY = []
    dictV = []
    words = defaultdict(int)
    for d in document.iterDoc(targetCID):
        words[d[-1]] += 1
    logging.log(logging.INFO, u'number of unique words:%d' % len(words))
    vocab = vocab.build()
    if useTfIdf: sortfunc = lambda x: float(x[1])/log(vocab.get(x[0].origin,2))
    else: sortfunc = lambda x: x[1]
    for word, cnt in sorted(words.iteritems(), key=sortfunc, reverse=True):
        g = vocab.get(word.origin,0)
        if 0 < g < 200000000:
            if word.surface == '(': continue #huristics
            logging.log(logging.INFO, (u'word:%s[%d], cnt:%d, google-cnt:%d' % (word, word.posid, cnt, g)))
            if len(dictY) < initialYMax and word.isIndependentNoun() and word.posid != 40 : dictY.append(word.get())
            if len(dictV) < initialVMax and word.isAdj(): dictV.append(word.get())
            if len(dictY) == initialYMax and len(dictV) == initialVMax: break
    print 'seedY:', repr(dictY).decode('unicode-escape')
    print 'seedV:', repr(dictV).decode('unicode-escape')
    return set(dictY), set(dictV)

def createPhraseDict(targetCID):
    phraseDict = defaultdict(list)
    for val in document.iterDoc(targetCID):
        at, word = tuple(val[:-1]), val[-1]
        phraseDict[word.get()].append(at)
    return phraseDict

def getTemplates(dictY, dictV, phraseDict, spanMax=1, spanMin=0):
    positions = {}
    for y in dictY:
        for p in phraseDict[y]:
            positions[p] = 'y'
    for v in dictV:
        for p in phraseDict[v]:
            positions[p] = 'v'
    templates = []
    for (p1, yv1), (p2, yv2) in pairwise(sorted(positions.iteritems())):
        if yv1 == yv2: continue
        if p1[:-1] != p2[:-1]: continue
        diff = p2[-1] - p1[-1] - 1
        if spanMin <= diff <= spanMax:
            templates.append((p1,p2,yv1+yv2))
    return templates

def getPlaces(words, phraseDict):
    n = len(words)
    if n > 32: raise Exception() #words are too long
    ps = defaultdict(int)
    for id, word in enumerate(words):
        for p in phraseDict[word.get()]:
            ps[p] |= 1<<id
    ret = []
    cand = []
    prevP = None
    for p, v in sorted(ps.iteritems()):
        if prevP is not None:
            if prevP[:-1] != p[:-1] or prevP[-1] != p[-1]-1:
                cand = []
            else:
                for i in xrange(len(cand)-1,-1,-1):
                    if v & 1<<cand[i]:
                        cand[i] += 1
                        if cand[i] == n:
                            ret.append(p)
                            del cand[i]
                    else:
                        del cand[i]
        if v & 1:
            if n == 1: ret.append(p)
            else: cand.append(1)
        prevP = p
    return ret

def findCandidate(dictY, dictV, phraseDict, words, yv, posFilter=True, uniqueFlag=True):
    #before find
    candY = []
    templateY = words[1:]
    originalY = words[0]
    for cid,pid,rid,lid,wid in getPlaces(templateY, phraseDict):
        wid -= len(words)-1
        if wid >= 0:
            candY.append(document.DOC[cid][pid][rid][lid][wid])
    candV = []
    templateV = words[:-1]
    originalV = words[-1]
    for cid,pid,rid,lid,wid in getPlaces(words[:-1], phraseDict):
        wid += 1
        if wid < len(document.DOC[cid][pid][rid][lid]):
            candV.append(document.DOC[cid][pid][rid][lid][wid])

    if yv == 'vy':
        candY, candV = candV, candY
        templateY, templateV = templateV, templateY
        originalY, originalV = originalV, originalY
    if posFilter:
        candY = filter(lambda x: x.willBeEntry(), candY)
        candV = filter(lambda x: x.willBeValue(), candV)
    if uniqueFlag:
        candY = set(candY)
        candV = set(candV)
    scoreY = 0.0
    for cy in candY:
        if cy.get() in dictY:
            scoreY += 1
    scoreY /= len(candY)+1
    scoreV = 0.0
    for cv in candV:
        if cv.get() in dictV:
            scoreV += 1
    scoreV /= len(candV)+1
    return (scoreY, templateY, tuple(candY), originalY), (scoreV, templateV, tuple(candV), originalV)

def calcTemplateScores(dictY, dictV, phraseDict, templates, uniqueFlag=False):
    wordsSet = []
    for p1, p2, yv in templates:
        wordsSet.append((document.getWords(p1,p2), yv))
    if uniqueFlag: wordsSet = set(wordsSet)
    candYV = []
    for words, yv in wordsSet:
        cands = findCandidate(dictY, dictV, phraseDict, words, yv)
        candYV.append(cands)
    return candYV

def calcYVScores(candYV, want):
    tobeYV = [{},{}]
    for i, cand in enumerate(zip(*candYV)):
        for score, template, vals, orig in sorted(set(cand), reverse=True):
            #print score, ''.join(map(unicode, template)), repr(vals).decode('unicode-escape')
            score *= want
            if score > 1: score = 1.0
            for val in set(vals):
                if val in tobeYV[i]:
                    tobeYV[i][val] = tobeYV[i][val] * score / (tobeYV[i][val] * score + (1-tobeYV[i][val]) * (1-score))
                else:
                    tobeYV[i][val] = score
        #print
    return tobeYV

def selectNextYV(tobeYV, thresh=0.5):
    nextYV = [[],[]]
    for i in xrange(2):
        for val, score in sorted(tobeYV[i].iteritems(), key=lambda x:x[1], reverse=True):
            if score >= thresh: nextYV[i].append(val.get())
            #print unicode(val), score
        #print
    return set(nextYV[0]), set(nextYV[1])

def bootstrap(opts, targetCID=None, result=None):
    phraseDict = createPhraseDict(targetCID)
    dictY, dictV = findSeed(targetCID, opts.tfidf)
    print >>result, u' '.join(map(lambda x:unicode(x[1]), sorted(dictY, key=lambda x:x[1], reverse=True)))
    for loop in xrange(opts.maxLoop):
        templates = getTemplates(dictY, dictV, phraseDict, spanMax=3, spanMin=0)
        candYV = calcTemplateScores(dictY, dictV, phraseDict, templates)
        tobeYV = calcYVScores(candYV, opts.want)
        nextY, nextV = selectNextYV(tobeYV)
        nextY -= dictY
        nextV -= dictV
        print '%d th additionalY'%(loop+1), repr(nextY).decode('unicode-escape')
        print '%d th additionalV'%(loop+1), repr(nextV).decode('unicode-escape')
        if not nextY and not nextV: break
        dictY |= nextY
        dictV |= nextV

    correspondDict = [defaultdict(list), defaultdict(list)]
    for (scoreY, templateY, candY, originalY), (scoreV, templateV, candV, originalV) in calcTemplateScores(dictY, dictV, phraseDict, getTemplates(dictY, dictV, phraseDict, spanMax=3, spanMin=0)):
        if scoreY >= 0.5:
            correspondDict[1][originalV] += candY
            for y in candY:
                correspondDict[0][y].append(originalV)
        if scoreV >= 0.5:
            correspondDict[0][originalY] += candV
            for v in candV:
                correspondDict[1][v].append(originalY)

    return dictY, dictV, correspondDict


def findCorrespondance(dict, line, wid, maxDist=None):
    cnt = 1
    ret = []
    while (maxDist is None or cnt <= maxDist) and (wid-cnt >= 0 or wid+cnt < len(line)):
        if wid-cnt >= 0:
            if line[wid-cnt].get() in dict:
                ret.append(line[wid-cnt])
        if wid+cnt < len(line):
            if line[wid+cnt].get() in dict:
                ret.append(line[wid+cnt])
        cnt += 1
    return ret

def findEachYV(dictY, dictV, targetCID=None, minEachReview=1):
    Data = [] #Data[cid][pid] = [y{[v]}]
    Found = [] #Found[cid][pid] = [[ys],[vs]]
    Rank = []
    for cid, category in enumerate(document.DOC):
        if targetCID is not None and targetCID != cid: continue
        Data.append([]); Found.append([])
        rank = [defaultdict(int), defaultdict(int)]
        for pid, product in enumerate(category):
            if len(product) < minEachReview:
                Data[-1].append([]); Found[-1].append([])
                continue
            data = defaultdict(list); found = [[],[]]
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, word in enumerate(line):
                        logging.log(logging.DEBUG, str((cid, pid, rid, lid, wid)) + unicode(word))
                        if word.get() in dictY:
                            vs = findCorrespondance(dictV, line, wid, 10)
                            #print 'y', unicode(word), repr(vs).decode('unicode-escape')
                            if len(vs):
                                data[word] += vs
                                found[0].append(word)
                        if word.get() in dictV:
                            ys = findCorrespondance(dictY, line, wid, 10)
                            #print 'v', unicode(word), repr(ys).decode('unicode-escape')
                            if len(ys):
                                data[ys[0]] += [word]
                                found[1].append(word)
            for i, f in enumerate(found):
                for x in set(f):
                    rank[i][x] += 1
            Data[-1].append(dict(data)); Found[-1].append(found)
        Rank.append([list(sorted(r.iteritems(), key=lambda x:x[1], reverse=True)) for r in rank])
    return Data, Found, Rank

def evaluateCoverage(cid, dictY):
    entries = product.getEntries(cid, minReviewCount=50)
    try: dict = zip(*list(dictY))[1]
    except IndexError: dict = []
    covered = 0
    for i, entry in enumerate(entries):
        if entry in dict: covered += 1
        else: entries[i] += u'*'
    coverage = float(covered)/len(entries)
    return coverage, entries

def mainProc(opts, cid=None, out=None, result=None):
    if cid is None:
        targetCID = document.TARGET_CID
        cid = 0
    else:
        targetCID = cid
    print 'Category-%d:'%targetCID, product.SELECTED[targetCID]
    print >>result, product.SELECTED[targetCID]

    dictY, dictV, correspondDict = bootstrap(opts, cid, result=result)
    print >>out, 'dictY', repr(dictY).decode('unicode-escape')
    print >>out, 'dictV', repr(dictV).decode('unicode-escape')
    print >>out, 'correspondDict', repr(correspondDict).decode('unicode-escape')

    data, found, rank = findEachYV(dictY, dictV, cid) #プロダクトごとのYV対応
    print >>out, 'data:', repr(data).decode('unicode-escape')
    print >>out, 'found:', repr(found).decode('unicode-escape')
    print >>out, 'rank:', repr(rank).decode('unicode-escape')

    coverage_ent = evaluateCoverage(targetCID, dictY) #評価項目の網羅率の測定
    print >>out, 'coverage:', repr(coverage_ent).decode('unicode-escape')
    print

    print >>result, u' '.join(map(lambda x:unicode(x[0]), rank[0][0][:10]))

    return coverage_ent

def optsStr(opts):
    ret = ''
    ret += 'TFIDF' if opts.tfidf else 'TF'
    ret += '-' + 'w%d' % int(opts.want*10)
    ret += '-' + str(opts.maxLoop)
    return ret

if __name__ == '__main__':
    import util
    util.initIO()
    oparser = OptionParser('%prog [OPTIONS]')
    oparser.add_option('-o', '--outfile', dest='outfile', metavar='FILE', help='write.output to FILE')
    oparser.add_option('-T', "--TF", dest="tfidf", default=True, action="store_false", help="use TF but TF-IDF")
    oparser.add_option('-l', '--max_loop', dest='maxLoop', metavar='NUM', type='int', default=10, help='indicete maximum loop number.')
    oparser.add_option('-w', "--want", dest="want", metavar='VAL', type='float', default=2.0, help="use TF but TF-IDF")
    opts, args = oparser.parse_args()

    if opts.outfile: out = codecs.open(opts.outfile, 'w', 'utf-8')
    else: out = sys.stdout

    result = codecs.open('out/result_%s.txt'%optsStr(opts), 'w', 'utf-8')

    if document.TARGET_CID is None:
        eval = codecs.open('out/eval_%s.txt'%optsStr(opts), 'w', 'utf-8')
        totalCoverage = 0.0
        sqTotalCoverage = 0.0
        for cid in xrange(len(document.DOC)):
            coverage_ent = mainProc(opts, cid, out=out, result=result)
            coverage = coverage_ent[0]
            totalCoverage += coverage
            sqTotalCoverage += coverage**2
            print >>eval, 'Category-%d:'%cid, product.SELECTED[cid], 'coverage:', repr(coverage_ent).decode('unicode-escape')
        totalCoverage /= len(document.DOC)
        sqTotalCoverage /= len(document.DOC)
        print 'covarage avg:', totalCoverage, 'varaiance:', (sqTotalCoverage-totalCoverage**2)
        print >>eval, 'covarage avg:', totalCoverage, 'varaiance:', (sqTotalCoverage-totalCoverage**2)
        eval.close()
    else:
        coverage_ent = mainProc(opts, out=out, result=result)

    if opts.outfile: out.close()
    result.close()

