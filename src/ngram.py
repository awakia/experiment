#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
from collections import defaultdict
from product import iterAllProducts
import wakachi
from util import checkMkdir, pp_str
import shelve

OUT_DIR='out/ngram/'

class NgramCounter:
    def __init__(self):
        self.cnt = defaultdict(int)
    def ngram(self, products, n):
        for prod in products:
            for review in prod.getReviews():
                lines = review.split('\n')
                for line in lines:
                    parsed = wakachi.parse(line) + [wakachi.DELIM]*(n-1)
                    for i in xrange(len(parsed)):
                        key = (parsed[i+j+1] for j in xrange(-n,0))
                        self.cnt[key] += 1

def ngram(n):
    nc = NgramCounter()
    for category, products in iterAllProducts():
        print >>sys.stderr, category
        nc.ngram(products, n)
    return dict(nc.cnt)

def outNgram(n, filesuffix='gram.db'):
    filename = str(n)+filesuffix
    wc = ngram(n)
    print len(wc)
    checkMkdir(OUT_DIR)
    out = open(OUT_DIR+filename+'keys.txt', 'w')
    print >>out, pp_str(wc.keys())
    out.close()
    d = shelve.open(OUT_DIR+filename)
    for k, v in wc.iteritems():
        d[u'-'.join(k).encode('utf-8')] = v
    d.close()

def input(filename):
    d = shelve.open(OUT_DIR+filename)
    print len(d.keys())
    for k, v in sorted(d.iteritems(), key=lambda x:x[1], reverse=True):
        #print '(%s,%d)' % (k,v),
        print k, v
    d.close()

if __name__ == '__main__':
    for n in xrange(1,4): outNgram(n)
    input('1gram.db')