#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys, codecs
import os
import types

def build(filename='data/1gm.txt'):
    vocab = {}
    inputfile = codecs.open(filename, 'r', 'utf-8')
    for lnum, line in enumerate(inputfile):
        key, sep, val = line.rstrip().partition('\t')
        if sep == '\t': vocab[key] = int(val)
    print >>sys.stderr, 'vocab built!'
    return vocab

def system(cmd, out_cmd=False):
    if out_cmd: print '$', cmd
    res = os.popen(cmd).read()
    return res

def googleNgram(keyword, user='aikawa', host='133.9.238.116', index_dir='/work/googlengram/index/'):
    if type(keyword) is types.UnicodeType: keyword = keyword.encode('utf-8')
    command = 'ssh %s@%s "echo %s | ssgnc-search --ssgnc-order=FIXED %s"' % (user, host, keyword, index_dir)
    res = system(command)
    v = res.split()
    if len(v): return int(v[-1])
    else: return 0


if __name__ == '__main__':
    print googleNgram('機能')
    print googleNgram(u'機能性')
    print googleNgram(u'機能 性')

    vocab = build()
    print vocab[u'文字']
    print vocab['文字'] #error