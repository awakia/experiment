#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import codecs
from util import checkMkdir, wrapHtml
from product import iterAllProducts

PLAIN_DIR='out/plain/'
HTML_DIR='html/'

def outputHtml(content, filename):
    checkMkdir(HTML_DIR)
    fout = codecs.open(HTML_DIR+filename, 'w', 'utf-8')
    print >>fout, wrapHtml(content)
    fout.close()

def getHtmlContent(text, docid):
    import wakachi
    aaa = wakachi.parse(text, '\n')
    html = ''
    for wid, word in enumerate(aaa):
        if word.surface == '\n':
            html += '<br />'
            continue
#        template = '%s'
#        if word.pos(detail=False) in [u'形容詞', u'名詞']:
#            template = '<strong class="posid' + str(word.posid) + '">%s</strong>'
        template = '<span id="word' + str(docid+1) + '-' + str(wid+1) + '" class="posid' + str(word.posid) + '" title="' + word.pos(detail=True) + '">%s</span>'
        html += template % unicode(word)
    return html

def products2html(products):
    for prod in products:
        reviews = prod.getReviews()
        content = '<div class="review">'
        for i, review in enumerate(reviews):
            if i: content += '</div>\n\n<div class="review">'
            content += getHtmlContent(review, i)
        content += '</div>'
        outputHtml(content, unicode(prod).replace('/','').replace(' ','_') + '.html')
        
def products2text(products):
    for prod in products:
        content = prod.getReviews(htmlStyle=True)
        filename = unicode(prod).replace('/','').replace(' ','_') + '.txt'
        checkMkdir(PLAIN_DIR)
        fout = codecs.open(HTML_DIR+filename, 'w', 'utf-8')
        print >>fout, wrapHtml(content)
        fout.close()

def doAll(html=False):
    for jsonfile, prods in iterAllProducts():
        print jsonfile
        if html: products2html(prods)
        else: products2text(prods)

if __name__ == '__main__':
    '''
    prods = inputProducts(JSON_DIR+u'プリンタ_343.txt')
    products2html(prods)
    '''
    doAll()