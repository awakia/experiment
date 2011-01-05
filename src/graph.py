#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''

class Graph():
    def __init__(self):
        self.data = []
    def __getitem__(self, key): return self.data.__getitem__(key)
    def __delitem__(self, key): return self.data.__delitem__(key)
    def __setitem__(self, key, val): return self.data.__setitem__(key, val)
    def __len__(self): return self.data.__len__()
    def __repr__(self): return self.data.__repr__()
    def __str__(self): return self.data.__str__()
    def __unicode__(self): return self.data.__unicode__()
    def addNode(self, n):
        print len(self)
        for i in xrange(len(self.data), n):
            self.data.append([])
    def addEdge(self, src, dst, weight=1):
        self.addNode(max(src,dst)+1)
        self.data[src].append((dst,weight))
    def addBiEdge(self, src, dst, weight=1):
        self.__allocate(max(src,dst)+1)
        self.data[src].append((dst,weight))
        self.data[dst].append((src,weight))


if __name__ == '__main__':
    g = Graph()
    g.addEdge(0,2)
    g.addEdge(1,2)
    g.addBiEdge(1,3)
    print g
