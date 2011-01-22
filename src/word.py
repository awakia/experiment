#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''

USE_ORIGIN = True #phraseDictに(posid,origin)で登録するか(posid,surface)で登録するか

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
        if USE_ORIGIN: return self.origin
        else: return self.surface
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
    def isAdj(self): return 10 <= self.posid <= 12 or self.posid == 40 #形容詞
    def isPart(self): return 13 <= self.posid <= 24 #助詞
    def isAuxverb(self): return self.posid == 25 #助動詞
    def isConj(self): return self.posid == 26 #接続詞
    def isPre(self): return 27 <= self.posid <= 30 #接頭詞
    def isVerb(self): return 31 <= self.posid <= 33 #動詞
    def isAdv(self): return 34 <= self.posid <= 35 #副詞
    def isNoun(self): return 36 <= self.posid <= 67 and self.posid != 40 #名詞
    def isPrenoun(self): return self.posid == 68 #連体詞
