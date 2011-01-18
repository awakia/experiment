#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2011/01/17

@author: aikawa
'''
from collections import defaultdict
from util import pairwise
import logging

USE_ORIGIN = True #phraseDictに(posid,origin)で登録するか(posid,surface)で登録するか
phraseDict = defaultdict(list) #origin->[position]

doc = [] #doc[categoryID][productID][reviewID][lineID][wordID]=word

dictY = [(36,u'デザイン'),(36,u'機能'),(51,u'機能性'),(51,u'操作性'),(38,u'音'),(38,u'音質'),(51,u'使用感'),(38,u'液晶')]
dictV = [(10,u'良い'),(36,u'満足'),(37,u'問題')]

class Word:
    POS_LIST=['その他,間投,*,*','フィラー,*,*,*','感動詞,*,*,*','記号,アルファベット,*,*','記号,一般,*,*','記号,括弧開,*,*','記号,括弧閉,*,*','記号,句点,*,*','記号,空白,*,*','記号,読点,*,*','形容詞,自立,*,*','形容詞,接尾,*,*','形容詞,非自立,*,*','助詞,格助詞,一般,*','助詞,格助詞,引用,*','助詞,格助詞,連語,*','助詞,係助詞,*,*','助詞,終助詞,*,*','助詞,接続助詞,*,*','助詞,特殊,*,*','助詞,副詞化,*,*','助詞,副助詞,*,*','助詞,副助詞／並立助詞／終助詞,*,*','助詞,並立助詞,*,*','助詞,連体化,*,*','助動詞,*,*,*','接続詞,*,*,*','接頭詞,形容詞接続,*,*','接頭詞,数接続,*,*','接頭詞,動詞接続,*,*','接頭詞,名詞接続,*,*','動詞,自立,*,*','動詞,接尾,*,*','動詞,非自立,*,*','副詞,一般,*,*','副詞,助詞類接続,*,*','名詞,サ変接続,*,*','名詞,ナイ形容詞語幹,*,*','名詞,一般,*,*','名詞,引用文字列,*,*','名詞,形容動詞語幹,*,*','名詞,固有名詞,一般,*','名詞,固有名詞,人名,一般','名詞,固有名詞,人名,姓','名詞,固有名詞,人名,名','名詞,固有名詞,組織,*','名詞,固有名詞,地域,一般','名詞,固有名詞,地域,国','名詞,数,*,*','名詞,接続詞的,*,*','名詞,接尾,サ変接続,*','名詞,接尾,一般,*','名詞,接尾,形容動詞語幹,*','名詞,接尾,助数詞,*','名詞,接尾,助動詞語幹,*','名詞,接尾,人名,*','名詞,接尾,地域,*','名詞,接尾,特殊,*','名詞,接尾,副詞可能,*','名詞,代名詞,一般,*','名詞,代名詞,縮約,*','名詞,動詞非自立的,*,*','名詞,特殊,助動詞語幹,*','名詞,非自立,一般,*','名詞,非自立,形容動詞語幹,*','名詞,非自立,助動詞語幹,*','名詞,非自立,副詞可能,*','名詞,副詞可能,*,*','連体詞,*,*,*']
    def __init__(self, surface, origin, posid):
        self.surface = surface
        self.origin = origin
        self.posid = posid
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.__unicode__().encode('unicode-escape')
    def __unicode__(self):
        if USE_ORIGIN: return self.origin+'[%d]'%self.posid
        else: return self.surface+'[%d]'%self.posid
    def __cmp__(self, other): # compare with pos and original form
        if cmp(self.posid, other.posid) != 0: return cmp(self.posid, other.posid)
        if USE_ORIGIN: return cmp(self.origin, other.origin)
        else: return cmp(self.surface, other.surface)
    def __hash__(self): # compare with pos and original form
        if USE_ORIGIN: return hash(self.origin) + hash(self.posid)
        else: return hash(self.surface) + hash(self.posid)
    def get(self):
        if USE_ORIGIN: return (self.posid, self.origin)
        else: return (self.posid, self.surface)
    def feature(self):
        return Word.POS_LIST[self.posid]
    def isAdj(self): return 10 <= self.posid <= 12 #形容詞
    def isPart(self): return 13 <= self.posid <= 24 #助詞
    def isAuxverb(self): return self.posid == 25 #助動詞
    def isConj(self): return self.posid == 26 #接続詞
    def isPre(self): return 27 <= self.posid <= 30 #接頭詞
    def isVerb(self): return 31 <= self.posid <= 33 #動詞
    def isAdv(self): return 34 <= self.posid <= 35 #副詞
    def isNoun(self): return 36 <= self.posid <= 67 #名詞
    def isPrenoun(self): return self.posid == 68 #連体詞

def getWord(position):
    (cid, pid, rid, lid, wid) = position
    return doc[cid][pid][rid][lid][wid]
def getWords(p1, p2):
    if p1[:-1] != p2[:-1]: return 'ERORR'+str(p1)+'|'+str(p2)
    (cid, pid, rid, lid, wstart) = p1
    wend = p2[-1]+1
    return tuple([doc[cid][pid][rid][lid][wid] for wid in xrange(wstart,wend)])

def getTemplates(spanMax=1, spanMin=0):
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

def getPlaces(words):
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
        if v & 1: cand.append(1)
        prevP = p
    return ret

def iterDoc():
    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, word in enumerate(line):
                        yield cid, pid, rid, lid, wid, word

def addWordToDict(at, word):
    global phraseDict
    phraseDict[word.get()].append(at)

def addPhraseToDict(at, phrase, posid):
    global phraseDict
    s = u''.join(map(lambda x: x.surface, phrase[0:-1]))
    phrase = Word(s+phrase[-1].surface, s+phrase[-1].origin, posid)
    phraseDict[phrase.get()].append(at)
    return phrase

def init(maxReview=10):
    global doc
    import cPickle, os
    import product
    import wakachi
    if os.path.exists('out/doc.pkl'):
        file = open('out/doc.pkl', 'rb')
        doc = cPickle.load(file)
        file.close()
    else:
        for cid, (category, prods) in enumerate(product.iterAllProducts(minReviewCount=50)):
            doc.append([])
            for pid, prod in enumerate(prods):
                reviews = prod.getReviews(max=maxReview, htmlStyle=True)
                doc[-1].append([])
                for rid, review in enumerate(reviews):
                    morphslist = wakachi.parseLine(review, '<br />')
                    doc[-1][-1].append([])
                    for lid, morphs in enumerate(morphslist):
                        doc[-1][-1][-1].append([Word(m.surface,m.original(),m.posid) for m in morphs])
        logging.log(logging.INFO, 'all product parsed')
        file = open('out/doc.pkl', 'wb')
        cPickle.dump(doc, file)
        file.close()

    logging.log(logging.INFO, 'document input completed')

    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, (wa, wb) in enumerate(pairwise(line)):
                        if wa.posid == 40 and wb.posid == 20: #「非常に」など
                            doc[cid][pid][rid][lid][wid] = Word(wa.surface+wb.surface, wa.surface+wb.origin, 34)
                            #print wa.surface+wb.surface
                            del doc[cid][pid][rid][lid][wid+1]

    logging.log(logging.INFO, 'pre-combine completed')

    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    wid = 0
                    while wid < len(line):
                        if line[wid].isNoun() or line[wid].isPre(): #add as NounPhrase
                            w = wid + 1
                            while w < len(line) and line[w].isNoun(): w += 1
                            line[wid] = addPhraseToDict((cid,pid,rid,lid,wid), line[wid:w], line[w-1].posid)
                            del line[wid+1:w]
                        elif line[wid].isAdj() or line[wid].isAdv(): #add as AdjPhrase
                            w = wid + 1
                            while w < len(line) and (line[w].isAdj() or line[w].isAdv()): w += 1
                            if line[w-1].isAdv():
                                if w < len(line) and line[w].posid == 57: #「重さ」など
                                    w += 1
                                line[wid] = addPhraseToDict((cid,pid,rid,lid,wid), line[wid:w], line[w-1].posid)
                                del line[wid+1:w]
                            else: addWordToDict((cid,pid,rid,lid,wid), line[wid])
                        else: addWordToDict((cid,pid,rid,lid,wid), line[wid])
                        wid += 1

    logging.log(logging.INFO, 'phrase register completed')
    #cnt = 0
    #for _ in iterDoc(): cnt+=1
    #print cnt

    #for cid, pid, rid, lid, wid, word in iterDoc(): print unicode(word),

def findCandidate(words, yv):
    #before find
    print ''.join(map(lambda x: x.origin, words[1:])), yv,
    for cid,pid,rid,lid,wid in getPlaces(words[1:]):
        wid -= len(words)-1
        if wid >= 0:
            cand = doc[cid][pid][rid][lid][wid]
            print cand.origin,
    print
    #after find
    print ''.join(map(lambda x: x.origin, words[:-1])), yv,
    for cid,pid,rid,lid,wid in getPlaces(words[:-1]):
        wid += 1
        if wid < len(doc[cid][pid][rid][lid]):
            cand = doc[cid][pid][rid][lid][wid]
            print cand.origin,
    print


if __name__ == '__main__':
    import util
    util.initIO()
    init()
    templates = getTemplates()
    wordsSet = []
    for p1, p2, yv in templates:
        wordsSet.append((getWords(p1,p2), yv))
    wordsSet = set(wordsSet)
    for words, yv in wordsSet:
        #print ''.join(map(lambda x: x.origin, words)), yv, getPlaces(words)
        findCandidate(words, yv)

