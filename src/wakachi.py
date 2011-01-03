#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
@requires: install mecab & mecab-python (ver.0.98)
@requires: [optional] install cabocha & cabocha-python (ver.0.60)
'''
import sys
import types
import MeCab
try: import CaboCha
except ImportError, e: print >>sys.stderr, e

class Morph:
    POS_LIST=['その他,間投,*,*','フィラー,*,*,*','感動詞,*,*,*','記号,アルファベット,*,*','記号,一般,*,*','記号,括弧開,*,*','記号,括弧閉,*,*','記号,句点,*,*','記号,空白,*,*','記号,読点,*,*','形容詞,自立,*,*','形容詞,接尾,*,*','形容詞,非自立,*,*','助詞,格助詞,一般,*','助詞,格助詞,引用,*','助詞,格助詞,連語,*','助詞,係助詞,*,*','助詞,終助詞,*,*','助詞,接続助詞,*,*','助詞,特殊,*,*','助詞,副詞化,*,*','助詞,副助詞,*,*','助詞,副助詞／並立助詞／終助詞,*,*','助詞,並立助詞,*,*','助詞,連体化,*,*','助動詞,*,*,*','接続詞,*,*,*','接頭詞,形容詞接続,*,*','接頭詞,数接続,*,*','接頭詞,動詞接続,*,*','接頭詞,名詞接続,*,*','動詞,自立,*,*','動詞,接尾,*,*','動詞,非自立,*,*','副詞,一般,*,*','副詞,助詞類接続,*,*','名詞,サ変接続,*,*','名詞,ナイ形容詞語幹,*,*','名詞,一般,*,*','名詞,引用文字列,*,*','名詞,形容動詞語幹,*,*','名詞,固有名詞,一般,*','名詞,固有名詞,人名,一般','名詞,固有名詞,人名,姓','名詞,固有名詞,人名,名','名詞,固有名詞,組織,*','名詞,固有名詞,地域,一般','名詞,固有名詞,地域,国','名詞,数,*,*','名詞,接続詞的,*,*','名詞,接尾,サ変接続,*','名詞,接尾,一般,*','名詞,接尾,形容動詞語幹,*','名詞,接尾,助数詞,*','名詞,接尾,助動詞語幹,*','名詞,接尾,人名,*','名詞,接尾,地域,*','名詞,接尾,特殊,*','名詞,接尾,副詞可能,*','名詞,代名詞,一般,*','名詞,代名詞,縮約,*','名詞,動詞非自立的,*,*','名詞,特殊,助動詞語幹,*','名詞,非自立,一般,*','名詞,非自立,形容動詞語幹,*','名詞,非自立,助動詞語幹,*','名詞,非自立,副詞可能,*','名詞,副詞可能,*,*','連体詞,*,*,*']
    USE_ORIGIN = False
    USE_POS = 0 # 0-2
    def __init__(self, surface, feature, posid=-1):
        self.surface = surface.decode('utf-8')
        self.features = feature.decode('utf-8').split(',') # len(features) == 7 or 9
        if posid == -1:
            for i, posf in enumerate(Morph.POS_LIST):
                if feature.startswith(posf):
                    posid = i
                    break
        self.posid = posid
    def __repr__(self):
        return self.__unicode__()
    def __str__(self):
        return str(self.posid)
    def __unicode__(self):
        return self.str(Morph.USE_ORIGIN, Morph.USE_POS)
    def original(self):
        if self.features[6] != '*': return self.features[6]
        else: return self.surface
    def pos(self, detail=True):
        res = self.features[0]
        if detail:
            for i in xrange(1,4):
                if self.features[i] != '*':
                    res += '-' + self.features[i]
        return res
    def str(self, useOrigin=False, usePOS=1):
        if useOrigin: res = self.original()
        else: res = self.surface
        if usePOS: res += '/' + self.pos(usePOS!=1)
        return res

DELIM=('</S>','その他,間投,*,*,*,*,*',0)

class Chunk():
    def __init__(self, id, to):
        self.id = id
        self.to = to
        self.info = []
    def __repr__(self):
        return self.__unicode__()
    def __str__(self):
        return '%d,%d{%s}' % (self.id, self.to, '|'.join(self.info))
    def __unicode__(self):
        return unicode(self.__str__())
    def addInfo(self, val):
        self.info.append(val)

def parse(text, delim=None):
    '''
    return: [Morph]
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    morphs = []
    mecab = MeCab.Tagger()
    if delim is None: txt = [text]
    else: txt = text.split(delim)
    for s in txt:
        tmp = []
        m = mecab.parseToNode(s).next
        while m.next:
            tmp.append(Morph(m.surface, m.feature, m.posid))
            m = m.next
        morphs.append(tmp)
    if delim is not None: delimMorph = Morph(delim,'記号,空白,*,*,*,*,*',8)
    return reduce(lambda x,y: x+[delimMorph]+y, morphs)

def parseWithDependency(text, delim=None):
    '''
    return: [Morph], [group]
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    morphs = []
    chunks = []
    cabocha = CaboCha.Parser()
    if delim is None: txt = [text]
    else: txt = text.split(delim)
    for s in txt:
        tree = cabocha.parse(s)
        tmp = []
        for i in xrange(tree.token_size()):
            token = tree.token(i)
            tmp.append(Morph(token.normalized_surface, token.feature))
        morphs.append(tmp)
        tmp = []
        for i in xrange(tree.chunk_size()):
            chunk = tree.chunk(i)
            for j in xrange(chunk.token_size):
                to = tree.chunk(chunk.link).token_pos if chunk.link != -1 else -1
                c = Chunk(i, to)
                if j == chunk.head_pos: c.addInfo('head')
                if j == chunk.func_pos: c.addInfo('func')
                tmp.append(c)
        chunks.append(tmp)
    if delim is not None:
        delimMorph = Morph(delim,'記号,空白,*,*,*,*,*',8)
        delimChunk = Chunk(-1,-1)
    return reduce(lambda x,y: x+[delimMorph]+y, morphs), reduce(lambda x,y: x+[delimChunk]+y, chunks)

def mecabParse(text, attr=''):
    '''
    return: the result string of `mecab TEXT`
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    mecab = MeCab.Tagger(attr)
    return mecab.parse(text)

def cabochaParse(text, attr=''):
    '''
    return: the result string of `cabocha TEXT`
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    cabocha = CaboCha.Parser(attr)
    return cabocha.parseToString(text)

def _testMecab(sentence="太郎はこの本を二郎を見た女性に渡した。"):
    try:
        print MeCab.VERSION
        t = MeCab.Tagger (" ".join(sys.argv))
        print t.parse (sentence)
        m = t.parseToNode (sentence)
        while m:
            print m.surface, "\t", m.feature
            m = m.next
        print "EOS"
        n = t.parseToNode(sentence)
        len = n.sentence_length;
        for i in range(len + 1):
            b = n.begin_node_list(i)
            e = n.end_node_list(i)
            while b:
                print "B[%d] %s\t%s" % (i, b.surface, b.feature)
                b = b.bnext
            while e:
                print "E[%d] %s\t%s" % (i, e.surface, e.feature)
                e = e.bnext
        print "EOS";
        d = t.dictionary_info()
        while d:
            print "filename: %s" % d.filename
            print "charset: %s" %  d.charset
            print "size: %d" %  d.size
            print "type: %d" %  d.type
            print "lsize: %d" %  d.lsize
            print "rsize: %d" %  d.rsize
            print "version: %d" %  d.version
            d = d.next
    except RuntimeError, e:
        print "RuntimeError:", e;

def _testCabocha(sentence = "太郎はこの本を二郎を見た女性に渡した。"):
    # c = CaboCha.Parser("");
    c = CaboCha.Parser()
    print c.parseToString(sentence)
    tree =  c.parse(sentence)
    print tree.toString(CaboCha.FORMAT_TREE)
    print tree.toString(CaboCha.FORMAT_LATTICE)

if __name__ == '__main__':
    sentence="太郎はこの本を二郎を見た女性に渡した。\nすばらしい。"
    print parse(unicode(sentence))
    res = parse(sentence, '\n')
    print res
    Morph.USE_ORIGIN=True
    Morph.USE_POS = 1
    print res
    #print mecabParse(sentence)
    
    m, c = parseWithDependency(sentence, '\n')
    print len(m), len(c)
    print zip(m,c)
    print cabochaParse(sentence)
