#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
import codecs
import xml.sax.saxutils
import json
import os

def initIO(stdin=True, stdout=True, stderr=True):
    """
    標準入出力のエンコーディングを調整します
    """
    encoding = sys.getfilesystemencoding()
    if (encoding in [None, 'US-ASCII', 'ascii']): encoding = 'cp932'
    print >>sys.stderr, encoding
    if stdin: sys.stdin  = codecs.getreader(encoding)(sys.stdin)
    if stdout: sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    if stderr: sys.stderr = codecs.getwriter(encoding)(sys.stderr)

def pp_str(obj, indent= None):
    if isinstance(obj, list) or isinstance(obj, dict) or isinstance(obj, tuple):
        orig = json.dumps(obj,indent=indent)
        return eval("u'''%s'''" % orig).encode('utf-8')
    else:
        return obj

def html2plain(data):
    return xml.sax.saxutils.unescape(data, entities={'&quot;':'"', '&apos;':"'", '<br />':'\n', '<br/>':'\n', '<br>':'\n'})
def plain2html(data):
    return xml.sax.saxutils.escape(data, entities={'\n':'<br />'})

def jsonLoad(filename):
    input = open(filename,'r')
    x = json.load(input)
    input.close()
    return x

def checkMkdir(dirname):
    if not os.path.exists(dirname): os.makedirs(dirname)

def toUnicode(str):
    """
    stringのエンコーディングをunicodeに変換します
    @param ``str'' string object.
    @return string object.
    """
    lookup = ('utf-8', 'euc-jp', 'shift-jis', 'shift-jis-2004','cp932',
            'iso2022jp', 'latin-1', 'ascii', 'US-ASCII')
    for encoding in lookup:
        try:
            str = str.decode(encoding)
            print >>sys.stderr, encoding
            break
        except:
            pass
    return str

def wrapHtml(content, title=None, needRoot=False):
    if title is not None: title = '<title>%s</title>' % title
    else: title = ''
    root = '/' if needRoot else ''
    template='''<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8">
''' + title + '''
<link href="''' + root + '''_/styles.css" rel="stylesheet" type="text/css" media="all">
<script type="text/javascript" src="''' + root + '''_/scripts.js"></script>
</head>
<body>
%s
</body>
</html>'''
    return template % content

if __name__ == '__main__':
    print html2plain('aaa<br />f&lt;M<br/><br>bbbr')