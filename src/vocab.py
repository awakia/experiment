#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys, codecs

def build(filename='data/1gm.txt'):
    vocab = {}
    inputfile = codecs.open(filename, 'r', 'utf-8')
    for lnum, line in enumerate(inputfile):
        key, sep, val = line.rstrip().partition('\t')
        if sep == '\t': vocab[key] = int(val)
    print >>sys.stderr, 'vocab built!'
    return vocab

if __name__ == '__main__':
    vocab = build()
    print vocab[u'文字']
    print vocab['文字'] #error