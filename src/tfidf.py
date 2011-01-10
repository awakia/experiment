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
from math import *

OUT_DIR='tfidf/'

class WordCounter:
    def __init__(self):
        self.cnt = defaultdict(int)
    def regist(self, products):
        for prod in products:
            for review in prod.getReviews():
                for m in wakachi.parse(review):
                    self.cnt[m.surface] += 1

def tf(products):
    wc = WordCounter()
    wc.regist(products)
    return dict(wc.cnt)


def df():
    wc = WordCounter()
    for category, products in iterAllProducts():
        print >>sys.stderr, category
        wc.regist(products)
    return dict(wc.cnt)

def printDF(filename='df.txt'):
    import json
    wc = df()
    checkMkdir(OUT_DIR)
    out = open(OUT_DIR+filename, 'w')
    json.dump(wc, out)
    out.close()

def outDF(filename='df.db'):
    wc = df()
    print len(wc)
    checkMkdir(OUT_DIR)
    out = open(OUT_DIR+filename+'keys.txt', 'w')
    print >>out, pp_str(wc.keys())
    out.close()
    d = shelve.open(OUT_DIR+filename)
    for k, v in wc.iteritems():
        d[k.encode('utf-8')] = v
    d.close()

def inDF(filename='df.db'):
    d = shelve.open(OUT_DIR+filename)
    print >>sys.stderr, len(d.keys())
    for k, v in sorted(d.iteritems(), key=lambda x:x[1], reverse=True):
        #print '(%s,%d)' % (k,v),
        print k, v
    d.close()

def outRdfGdf(out=sys.stdout): #google ngram based TF-IDF
    import vocab
    vocab = vocab.build()
    filename = 'df.db'
    d = shelve.open(OUT_DIR+filename)
    print >>sys.stderr, len(d.keys())
    for k, v in sorted(d.iteritems(), key=lambda x:float(x[1])/log(vocab.get(x[0].decode('utf-8'),2)), reverse=True):
        g = vocab.get(k.decode('utf-8'),0)
        if 0 < g < 200000000:
            print >>out, k, v, g, float(v)/g
    d.close()

if __name__ == '__main__':
    outDF()
    outRdfGdf()
