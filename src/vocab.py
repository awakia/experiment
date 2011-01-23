#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys, codecs
import os
import types

VOCAB = None

def build(filename='data/1gm.txt'):
    global VOCAB
    if VOCAB is not None: return VOCAB
    VOCAB = {}
    inputfile = codecs.open(filename, 'r', 'utf-8')
    for lnum, line in enumerate(inputfile):
        key, sep, val = line.rstrip().partition('\t')
        if sep == '\t': VOCAB[key] = int(val)
    print >>sys.stderr, 'vocab built!'
    return VOCAB

def system(cmd, out_cmd=True):
    if out_cmd: print '$', cmd
    if type(cmd) is types.UnicodeType: cmd = cmd.encode('utf-8')
    res = os.popen(cmd).read()
    return res

def googleNgram(keyword, user='aikawa', host='133.9.238.116', index_dir='/work/googlengram/index/'):
    command = 'ssh -i/home/aikawa/.ssh/id_rsa_nopass %s@%s "echo %s | ssgnc-search --ssgnc-order=FIXED %s"' % (user, host, keyword, index_dir)
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
    try:print vocab['文字'] #error
    except Exception, e: print >>sys.stderr, e