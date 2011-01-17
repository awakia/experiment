#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2011/01/17

@author: aikawa
'''
from collections import defaultdict
from util import pairwise

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
        return self.surface+'[%d]'%self.posid
    def __cmp__(self, other): # compare with pos and original form
        if cmp(self.posid, other.posid) != 0: return cmp(self.posid, other.posid)
        return cmp(self.origin, other.origin)
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


surfaceDict = defaultdict(list) #surface->[position]
originDict = defaultdict(list) #origin->[position]

doc = [] #doc[categoryID][productID][reviewID][lineID][wordID]=word

candY = []
candV = []

def iterDoc():
    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, word in enumerate(line):
                        yield cid, pid, rid, lid, wid, word

def addDict(phrase, posid):
    global surfaceDict, originDict
    s = u''.join(map(lambda x: x.surface, phrase[0:-1]))
    sur = s + phrase[-1].surface
    ori = s + phrase[-1].origin
    surfaceDict[(sur, posid)]
    originDict[(ori, posid)]
    return Word(sur,ori,posid)

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
        selected = [u'Macノート',u'MP3プレーヤー',u'PDA',u'インク',u'カメラ',u'キーボード',u'コンタクトレンズ 1day',u'セキュリティソフト',u'チャイルドシート',u'テレビ',u'テレビリモコン',u'トースター',u'ドライバー',u'パソコン',u'パソコンゲーム',u'ヒーター・ストーブ',u'プリンタ',u'マッサージ器',u'ミシン',u'レンズ',u'冷蔵庫・冷凍庫',u'動画編集ソフト',u'地デジアンテナ',u'女性用シェーバー',u'掃除機',u'洗濯機',u'生ごみ処理機',u'自転車',u'電子ピアノ',u'香水']
        for cid, (category, prods) in enumerate(product.iterAllProducts(minReviewCount=50, categoryFilter=selected)):
            doc.append([])
            for pid, prod in enumerate(prods):
                reviews = prod.getReviews(max=maxReview, htmlStyle=True)
                doc[-1].append([])
                for rid, review in enumerate(reviews):
                    morphslist = wakachi.parseLine(review, '<br />')
                    doc[-1][-1].append([])
                    for lid, morphs in enumerate(morphslist):
                        doc[-1][-1][-1].append([Word(m.surface,m.original(),m.posid) for m in morphs])
        file = open('out/doc.pkl', 'wb')
        cPickle.dump(doc, file)
        file.close()

    print 'document input completed'

    cnt = 0
    for _ in iterDoc(): cnt+=1
    print cnt

    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, (wa, wb) in enumerate(pairwise(line)):
                        if wa.posid == 40 and wb.posid == 20: #「非常に」など
                            doc[cid][pid][rid][lid][wid] = Word(wa.surface+wb.surface, wa.surface+wb.origin, 34)
                            print wa.surface+wb.surface, wid
                            del doc[cid][pid][rid][lid][wid+1]

    print 'pre-combine completed'

    cnt = 0
    for _ in iterDoc(): cnt+=1
    print cnt

    for cid, category in enumerate(doc):
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    wid = 0
                    while wid < len(line):
                        if line[wid].isNoun() or line[wid].isPre():
                            w = wid + 1
                            while w < len(line) and line[w].isNoun(): w += 1
                            line[wid] = addDict(line[wid:w], line[w-1].posid)
                            del line[wid+1:w]
                        elif line[wid].isAdj() or line[wid].isAdv():
                            w = wid + 1
                            while w < len(line) and (line[w].isAdj() or line[w].isAdv()): w += 1
                            if line[w-1].isAdv():
                                line[wid] = addDict(line[wid:w], line[w-1].posid)
                                del line[wid+1:w]
                        wid += 1

    print 'register completed'
    cnt = 0
    for _ in iterDoc(): cnt+=1
    print cnt

    #for cid, pid, rid, lid, wid, word in iterDoc(): print unicode(word),

if __name__ == '__main__':
    import util
    util.initIO()
    init()
