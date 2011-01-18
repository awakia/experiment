#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import codecs
from util import checkMkdir, wrapHtml
from product import iterAllProducts

RANK_DIR='out/rank/'
PLAIN_DIR='out/plain/'
HTML_DIR='out/html/'

def getHtmlContent(text, docid):
    import wakachi
    aaa = wakachi.parseLine(text, '<br />')
    html = ''
    for lid, a in enumerate(aaa):
        if lid: html += '<br />'
        for wid, word in enumerate(a):
            template = '<span id="word' + str(docid) + '-' + str(lid) + '-' + str(wid) + '" class="posid' + str(word.posid) + '" title="' + word.pos(detail=True) + '">%s</span>'
            html += template % unicode(word)
    return html

def products2html(products, category=None, maxReview=None):
    dirname = HTML_DIR
    needRoot = False
    if category is not None:
        dirname += category + '/'
        needRoot = True
    checkMkdir(dirname)
    for prod in products:
        reviews = prod.getReviews(max=maxReview, htmlStyle=True)
        content = '<div class="review">'
        for i, review in enumerate(reviews):
            if i: content += '</div>\n\n<div class="review">'
            content += getHtmlContent(review, i)
        content += '</div>'
        filename = unicode(prod).replace('/','').replace(' ','_') + '.html'
        fout = codecs.open(dirname+filename, 'w', 'utf-8')
        print >>fout, wrapHtml(content, needRoot=needRoot)
        fout.close()

def products2text(products, category):
    dirname = PLAIN_DIR+category+'/'
    checkMkdir(dirname)
    for prod in products:
        content = prod.getReviews(htmlStyle=True)
        filename = unicode(prod).replace('/','').replace(' ','_') + '.txt'
        fout = codecs.open(dirname+filename, 'w', 'utf-8')
        print >>fout, '\n'.join(content)
        fout.close()

def createRank(minReviewCount=0, minProductCount=0, onlyValidCategory=False):
    checkMkdir(RANK_DIR)
    for category, products in iterAllProducts(minReviewCount):
        ranking = []
        if len(products) < minProductCount: continue
        for prod in products:
            prodCategory = prod['CategoryName']
            if onlyValidCategory and category != prodCategory.split('>')[-1]: break
            ranking.append(unicode(prod)+'\t'+prodCategory)
        else:
            fout = codecs.open(RANK_DIR+category, 'w', 'utf-8')
            print >>fout, str(len(products)) + '\n' + '\n'.join(ranking)
            fout.close()

def doAll(html=False):
    selected = [u'Macノート',u'MP3プレーヤー',u'PDA',u'インク',u'カメラ',u'キーボード',u'コンタクトレンズ 1day',u'セキュリティソフト',u'チャイルドシート',u'テレビ',u'テレビリモコン',u'トースター',u'ドライバー',u'パソコン',u'パソコンゲーム',u'ヒーター・ストーブ',u'プリンタ',u'マッサージ器',u'ミシン',u'レンズ',u'冷蔵庫・冷凍庫',u'動画編集ソフト',u'地デジアンテナ',u'女性用シェーバー',u'掃除機',u'洗濯機',u'生ごみ処理機',u'自転車',u'電子ピアノ',u'香水']
    for category, prods in iterAllProducts(minReviewCount=30, categoryFilter=selected):
        if html: products2html(prods, category, 10)
        else: products2text(prods, category)

if __name__ == '__main__':
    '''
    prods = inputProducts(JSON_DIR+u'プリンタ_343.txt')
    products2html(prods)
    '''
    createRank(50, 20, True)
    #doAll(html=True)