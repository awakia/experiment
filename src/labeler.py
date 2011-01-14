#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import wakachi
from collections import defaultdict

class Candidates:
    def __init__(self):
        self.nounps = defaultdict(list)
        self.adjps = defaultdict(list)
    def registerNounP(self, phrase, p, dlid):
        self.nounps[phrase].append((dlid,p))
    def registerAdjP(self, phrase, p, dlid):
        self.adjps[phrase].append((dlid,p))
    def _addAsNounP(self, morphs, phrase, p, dlid): # [連体詞]?[名詞]+
        i = p[-1]+1
        if i == len(morphs) or not morphs[i].isNoun():
            if morphs[p[-1]].isNoun(): self.registerNounP(phrase, tuple(p), dlid)
            return i
        else:
            return self._addAsNounP(morphs, phrase+morphs[i].surface, p+[i], dlid)
    def _addAsAdjP(self, morphs, phrase, p, dlid): # [副詞]*[形容詞]
        i = p[-1]
        if not morphs[i].isAdv():
            if morphs[i].isAdj(): self.registerAdjP(phrase+morphs[i].original(), tuple(p), dlid)
            return i+1
        else:
            return self._addAsAdjP(morphs, phrase+morphs[i].surface, p+[i+1], dlid)
    
    def check(self, morphs, docid, lid):
        dlid = (docid, lid)
        i = 0
        while i < len(morphs):
            if morphs[i].isNoun() or morphs[i].isPrenoun():
                i = self._addAsNounP(morphs, morphs[i].surface, [i], dlid)
            else:
                i = self._addAsAdjP(morphs, '', [i], dlid)

def getPhrase(text, docid, cand = Candidates()):
    mmm = wakachi.parseLine(text, '<br />')
    for lid, morphs in enumerate(mmm):
        cand.check(morphs, docid, lid)
    return dict(cand.nounps), dict(cand.adjps)

if __name__ == '__main__':
    nounps, adjps = getPhrase('とても小さく美しい花<br />機能性に優れる<br />解像度が高い<br />解像度が低い', 0)
    nounps, adjps = getPhrase('座高が高い', 1)
    print repr(nounps).decode('unicode-escape')
    print repr(adjps).decode('unicode-escape')