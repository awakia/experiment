#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
from product import iterAllProducts
import wakachi
from serializer import Serializer
from graph import Graph

OUT_DIR='tfidf/'

class NodeMaker:
    def __init__(self):
        self.ser = Serializer()
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
                    lst.append([morph])
                else: lst.append([])
            lst += [[] * 5]
            if line == '': lst += [[] * 5]
    def consume(self, lst, back=3, fore=10): #0:N, 1:V, 2:Y
        size = len(lst)
        for i in xrange(size):
            if lst[i] == []: continue
            posno = self.PosNo(lst[i])
            node = []
            for x in xrange(posno):
                node.append(self.ser.encode((list[i].posid, lst[i].origin(), x)))
                self.graph.addNode(node[x])
            #for node = V
            for j in xrange(max(0,i-fore), min(size,i+back)):
                if lst[j] == [] or self.PosNo(lst[j]) == 2: continue
                ny = self.ser.encode((list[j].posid, lst[j].origin(), 2))
                self.graph.addEdge(node[1], ny)
            #for node = Y
            if posno == 3:
                for j in xrange(max(0,i-back), min(size,i+fore)):
                    if lst[j] == []: continue
                    nv = self.ser.encode((list[j].posid, lst[j].origin(), 1))
                    self.graph.addEdge(node[2],nv)
        print self.graph



def doProducts(products):
    nm = NodeMaker()
    for prod in products:
        for review in prod.getReviews():
            nm.regist(review)

def main():
    cnt = 0
    for filename, products in iterAllProducts():
        print >>sys.stderr, filename
        doProducts(products)
        cnt += 1
        if cnt == 3: break


if __name__ == '__main__':
    main()