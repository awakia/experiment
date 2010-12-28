#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import sys
import glob
import codecs
from util import *
from product import iterAllProducts

HTML_DIR='html/'

def outputHtml(content, filename):
    checkMkdir(HTML_DIR)
    fout = codecs.open(HTML_DIR+filename, 'w', 'utf-8')
    print >>fout, wrapHtml(content)
    fout.close()

def getHtmlContent(text):
    import wakachi
    aaa = wakachi.parse(html2plain(text), '\n')
    html = ''
    for word in aaa:
        if word.surface == '\n':
            html += '<br />'
            continue
        template = '%s'
        if word.pos(detail=False) in [u'形容詞', u'名詞']:
            template = '<strong class="posid' + str(word.posid) + '">%s</strong>'
        html += template % unicode(word)
    return html

def products2html(products):
    for prod in products:
        reviews = prod.getReviews()
        content = '<div>'
        for i, review in enumerate(reviews):
            if i: content += '</div>\n\n<div>'
            content += getHtmlContent(review)
        content += '</div>'
        outputHtml(content, unicode(prod).replace('/','').replace(' ','_') + '.html')

def doAll():
    for jsonfile, prods in iterAllProducts():
        print jsonfile
        products2html(prods)

if __name__ == '__main__':
    '''
    prods = inputProducts(JSON_DIR+u'プリンタ_343.txt')
    products2html(prods)
    '''
    doAll()