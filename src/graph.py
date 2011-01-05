#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
from collections import defaultdict

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
    def append(self, edges):
        self.data.append(edges)
        return len(self.data)-1
    def registerNode(self, n):
        for i in xrange(len(self.data), n):
            self.data.append([])
    def addEdge(self, src, dst, weight=1):
        self.registerNode(max(src,dst)+1)
        self.data[src].append((dst,weight))
    def addBiEdge(self, src, dst, weight=1):
        self.registerNode(max(src,dst)+1)
        self.data[src].append((dst,weight))
        self.data[dst].append((src,weight))
    def pack(self, sum1=False):
        for src, edges in enumerate(self.data):
            d = defaultdict(int)
            totalW = 0.0
            for dst, weight in edges:
                d[dst] += weight
                totalW += weight
            lst = []
            for k, v in sorted(d.iteritems()):
                if sum1: v /= totalW
                lst.append((k,v))
            self.data[src] = lst

def pagerank(graph, initial=None, dweight=1, maxLoop=1):
    graphSize = len(graph)
    if initial is None:
        initial = [(i,1) for i in xrange(graphSize)]
    initID = graph.append(initial)
    for i in xrange(graphSize):
        graph.addEdge(i,initID,dweight)
    graph.pack(sum1=True)
    score = [1.0/graphSize] * graphSize
    score.append(0.0)
    for _ in xrange(maxLoop):
        nextScore = [0.0] * len(graph)
        for src, edges in enumerate(graph):
            if src == initID:
                for dst, weight in edges:
                    nextScore[dst] += weight * nextScore[src]
                continue
            for dst, weight in edges:
                nextScore[dst] += weight * score[src]
        score = nextScore
    del score[initID]
    return score

if __name__ == '__main__':
    g = Graph()
    g.addEdge(0,2)
    g.addEdge(1,2)
    g.addBiEdge(1,3)
    print g
