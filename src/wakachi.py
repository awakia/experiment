#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
import types
import MeCab

class Morph:
    USE_ORIGIN = False
    USE_POS = 0 # 0-2
    def __init__(self, surface, feature, posid):
        self.surface = surface.decode('utf-8')
        self.features = feature.decode('utf-8').split(',') # len(features) == 7 or 9
        self.posid = posid
    def __repr__(self):
        return self.__unicode__()
    def __str__(self):
        return self.posit
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

def parse(text, delim=None):
    '''
    return: [Morph]
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    res = []
    mecab = MeCab.Tagger()
    if delim is None: txt = [text]
    else: txt = text.split(delim)
    for s in txt:
        tmp = []
        m = mecab.parseToNode(s).next
        while m.next:
            tmp.append(Morph(m.surface, m.feature, m.posid))
            m = m.next
        res.append(tmp)
    if delim is not None: delimMorph = Morph(delim,'記号,空白,*,*,*,*,*',8)
    return reduce(lambda x,y: x+[delimMorph]+y, res)

def parseMecab(text, attr=None):
    '''
    return: the result string of `mecab TEXT`
    '''
    if type(text) is types.UnicodeType: text = text.encode('utf-8')
    mecab = MeCab.Tagger(attr)
    return mecab.parse(text)

def testMecab(sentence="太郎はこの本を二郎を見た女性に渡した。"):
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

if __name__ == '__main__':
    sentence="太郎はこの本を二郎を見た女性に渡した。\nすばらしい。"
    res = parse(unicode(sentence))
    print res
    res = parse(sentence, '\n')
    print res
    Morph.USE_ORIGIN=True
    Morph.USE_POS = 1
    print res
