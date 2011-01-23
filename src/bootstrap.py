#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2011/01/17

@author: aikawa
'''
import logging
#logging.basicConfig(level=logging.INFO)
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


def findSeed(targetCID):
    import vocab
    dictY = []
    dictV = []
    words = defaultdict(int)
    for d in document.iterDoc(targetCID):
        words[d[-1]] += 1
    logging.log(logging.INFO, u'number of unique words:%d' % len(words))
    vocab = vocab.build()
    for word, cnt in sorted(words.iteritems(), key=lambda x:float(x[1])/log(vocab.get(x[0].origin,2)), reverse=True):
        g = vocab.get(word.origin,0)
        if 0 < g < 200000000:
            if word.surface == '(': continue #huristics
            logging.log(logging.INFO, (u'word:%s[%d], cnt:%d, google-cnt:%d' % (word, word.posid, cnt, g)))
            if len(dictY) < initialYMax and word.isNoun(): dictY.append(word.get())
            if len(dictV) < initialVMax and word.isAdj(): dictV.append(word.get())
            if len(dictY) == initialYMax and len(dictV) == initialVMax: break
    print 'seedY:', repr(dictY).decode('unicode-escape')
    print 'seedV', repr(dictV).decode('unicode-escape')
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
    for cid,pid,rid,lid,wid in getPlaces(templateY, phraseDict):
        wid -= len(words)-1
        if wid >= 0:
            candY.append(document.DOC[cid][pid][rid][lid][wid])
    candV = []
    templateV = words[:-1]
    for cid,pid,rid,lid,wid in getPlaces(words[:-1], phraseDict):
        wid += 1
        if wid < len(document.DOC[cid][pid][rid][lid]):
            candV.append(document.DOC[cid][pid][rid][lid][wid])

    if yv == 'vy':
        candY, candV = candV, candY
        templateY, templateV = templateV, templateY
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
    return (scoreY, templateY, tuple(candY)), (scoreV, templateV, tuple(candV))

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

def calcYVScores(candYV, magic=1.5):
    tobeYV = [{},{}]
    for i, cand in enumerate(zip(*candYV)):
        for score, template, vals in sorted(set(cand), reverse=True):
            #print score, ''.join(map(unicode, template)), repr(vals).decode('unicode-escape')
            score *= magic
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

def bootstrap(opts, targetCID=None):
    if opts.outfile: out = codecs.open(opts.outfile, 'w', 'utf-8')
    else: out = sys.stdout

    phraseDict = createPhraseDict(targetCID)
    dictY, dictV = findSeed(targetCID)
    for loop in xrange(opts.maxLoop):
        templates = getTemplates(dictY, dictV, phraseDict, spanMax=3, spanMin=0)
        candYV = calcTemplateScores(dictY, dictV, phraseDict, templates)
        tobeYV = calcYVScores(candYV)
        nextY, nextV = selectNextYV(tobeYV)
        nextY -= dictY
        nextV -= dictV
        print '%d th additionalY'%(loop+1), repr(nextY).decode('unicode-escape')
        print '%d th additionalV'%(loop+1), repr(nextV).decode('unicode-escape')
        if not nextY and not nextV: break
        dictY |= nextY
        dictV |= nextV
    print >>out, repr(dictY).decode('unicode-escape')
    print >>out, repr(dictV).decode('unicode-escape')
    print >>out

    if opts.outfile: out.close()

    return dictY, dictV

if __name__ == '__main__':
    import util
    util.initIO()
    oparser = OptionParser('%prog [OPTIONS]')
    oparser.add_option('-o', '--outfile', dest='outfile', metavar='FILE', help='write.output to FILE')
    oparser.add_option('-l', '--max_loop', dest='maxLoop', metavar='NUM', type='int', default=10, help='indicete maximum loop number.')
    opts, args = oparser.parse_args()
    for cid in xrange(len(document.DOC)):
        print 'Category:', cid, product.SELECTED[cid]
        dictY, dictV = bootstrap(opts, cid)

