#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
from product import iterAllProducts
import wakachi
from collections import defaultdict
from serializer import Serializer
from graph import Graph, pagerank

OUT_DIR='tfidf/'

class NodeMaker:
    def __init__(self):
        self.ser = Serializer()
        self.words = defaultdict(int)
        self.graph = Graph()
    def PosNo(self, morph):
        for i, p in enumerate([u'形容詞', u'名詞']):
            if p in morph.pos():
                return i+2
        return 0
    def regist(self, text):
        lines = text.split('\n')
        lst = []
        for lnum, line in enumerate(lines):
            morphs = wakachi.parse(text)
            for morph in morphs:
                if self.PosNo(morph):
                    lst.append(morph)
                    self.words[(morph.posid, morph.original)] += 1
                else:
                    lst.append(None)
            lst += [None]*5
            if line == '':
                self.consume(lst)
                lst = []
        self.consume(lst)
    def consume(self, lst, back=3, fore=10): #0:N, 1:V, 2:Y
        size = len(lst)
        for i in xrange(size):
            if lst[i] is None: continue
            posno = self.PosNo(lst[i])
            node = []
            for x in xrange(posno):
                node.append(self.ser.encode((lst[i].posid, lst[i].original(), x)))
                self.graph.registerNode(node[x])
            #for node = V
            for j in xrange(max(0,i-fore), min(size,i+back)):
                if lst[j] is None or self.PosNo(lst[j]) == 2: continue
                ny = self.ser.encode((lst[j].posid, lst[j].original(), 2))
                self.graph.addEdge(node[1], ny)
            #for node = Y
            if posno == 3:
                for j in xrange(max(0,i-back), min(size,i+fore)):
                    if lst[j] is None: continue
                    nv = self.ser.encode((lst[j].posid, lst[j].original(), 1))
                    self.graph.addEdge(node[2],nv)

def doProducts(products, nm=None):
    if nm is None: nm = NodeMaker()
    for prod in products:
        for review in prod.getReviews():
            nm.regist(review)
    return nm

def main():
    nm = NodeMaker()
    cnt = 0
    for category, products in iterAllProducts():
        cnt += 1
        if cnt < 2: continue
        print >>sys.stderr, category
        doProducts(products, nm)
        if cnt == 3: break
    #nm.graph.pack(); print nm.graph
    rank = pagerank(nm.graph)
    result = {}
    for id, pr in enumerate(rank):
        word = nm.ser.decode(id)
        result[word] = pr
    for word, pr in sorted(result.iteritems(), reverse=True):
        print u'(%s,%d) %.3f' % (word[1], word[2], (pr*1000))


if __name__ == '__main__':
    import util
    util.initIO()
    main()