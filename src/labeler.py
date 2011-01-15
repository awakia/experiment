#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import types
import wakachi
from collections import defaultdict
from itertools import tee, izip
from product import iterAllProducts

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class Candidates:
    def __init__(self):
        self.nounps = defaultdict(list) #map[phrase:str]=[((did,lid),(wid-start,,,wid-end))]
        self.adjps = defaultdict(list)
        self.position = {}
    def registerNounP(self, phrase, p, goupid):
        self.nounps[phrase].append((goupid,p))
        self.position[(goupid, p[0])] = (p[-1], 'N')
    def registerAdjP(self, phrase, p, goupid):
        self.adjps[phrase].append((goupid,p))
        self.position[(goupid, p[0])] = (p[-1], 'A')
    def _addAsNounP(self, morphs, phrase, p, groupid): # [連体詞]?[名詞]+
        i = p[-1]+1
        if i == len(morphs) or not morphs[i].isNoun():
            if morphs[p[-1]].isNoun(): self.registerNounP(phrase, tuple(p), groupid)
            return i
        else:
            return self._addAsNounP(morphs, phrase+morphs[i].surface, p+[i], groupid)
    def _addAsAdjP(self, morphs, phrase, p, groupid): # [副詞]*[形容詞]
        i = p[-1]
        if i+1 == len(morphs) or not morphs[i].isAdv():
            if morphs[i].isAdj():
                if i+1 < len(morphs) and morphs[i+1].posid == 57:
                    self.registerNounP(phrase+morphs[i].surface+morphs[i+1].surface, tuple(p+[i+1]), groupid)
                else:
                    self.registerAdjP(phrase+morphs[i].original(), tuple(p), groupid)
            return i+1
        else:
            return self._addAsAdjP(morphs, phrase+morphs[i].surface, p+[i+1], groupid)
    def check(self, morphs, groupid):
        i = 0
        while i < len(morphs):
            if morphs[i].isNoun() or morphs[i].isPrenoun():
                i = self._addAsNounP(morphs, morphs[i].surface, [i], groupid)
            else:
                i = self._addAsAdjP(morphs, '', [i], groupid)
    def iterAllInternal(self, spanMax=1, spanMin=1):
        for (ak,av), (bk,bv) in pairwise(sorted(self.position.iteritems())):
            if ak[0] != bk[0]: continue #groupids are different
            diff = bk[1] - av[0] - 1 #b-beggining-position - a-ending-position
            if spanMin <= diff <= spanMax:
                yield ak[0], (ak[1],av[0]), (bk[1],bv[0])

def getPhrase(text, docid, cand = Candidates()):
    if type(text) is types.StringTypes: text = wakachi.parseLine(text, '<br />')
    for lid, morphs in enumerate(text):
        cand.check(morphs, (docid, lid))
    return dict(cand.nounps), dict(cand.adjps)

def doAll(maxReview=10):
    cand = Candidates()
    selected = [u'Macノート']#,u'MP3プレーヤー',u'PDA',u'インク',u'カメラ',u'キーボード',u'コンタクトレンズ 1day',u'セキュリティソフト',u'チャイルドシート',u'テレビ',u'テレビリモコン',u'トースター',u'ドライバー',u'パソコン',u'パソコンゲーム',u'ヒーター・ストーブ',u'プリンタ',u'マッサージ器',u'ミシン',u'レンズ',u'冷蔵庫・冷凍庫',u'動画編集ソフト',u'地デジアンテナ',u'女性用シェーバー',u'掃除機',u'洗濯機',u'生ごみ処理機',u'自転車',u'電子ピアノ',u'香水']
    words = []
    for cid, (category, prods) in enumerate(iterAllProducts(minReviewCount=50, categoryFilter=selected)):
        #print category
        words.append([])
        for pid, prod in enumerate(prods):
            reviews = prod.getReviews(max=maxReview, htmlStyle=True)
            words[-1].append([])
            for rid, review in enumerate(reviews):
                morphslist = wakachi.parseLine(review, '<br />')
                words[-1][-1].append(morphslist)
                getPhrase(morphslist, (cid,pid,rid), cand)
    for p, bgn, end in cand.iterAllInternal(spanMax=1, spanMin=0):
        cid, pid, rid, lid = p[0][0], p[0][1], p[0][2], p[1]
        print cid, pid, rid, lid, bgn, end,
        for wid in xrange(bgn[0],end[1]+1):
            print unicode(words[cid][pid][rid][lid][wid]),
            if wid == bgn[1]: print '[',
            if wid ==end[0]-1: print ']',
        print

if __name__ == '__main__':
    wakachi.Morph.USE_POS = 2
    doAll()
    '''
    nounps, adjps = getPhrase('とても小さく美しい花<br />機能性に優れる<br />解像度が高い<br />解像度が低い', 0)
    nounps, adjps = getPhrase('座高が高い', 1)
    print repr(nounps).decode('unicode-escape')
    print repr(adjps).decode('unicode-escape')'''