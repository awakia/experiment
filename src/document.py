#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import logging
import product
from word import Word

TARGET_CID=None
PKL_FILE='out/filc%d.pkl'

def getWord(position):
    (cid, pid, rid, lid, wid) = position
    return DOC[cid][pid][rid][lid][wid]

def getWords(p1, p2):
    if p1[:-1] != p2[:-1]: return 'ERORR'+str(p1)+'|'+str(p2)
    (cid, pid, rid, lid, wstart) = p1
    wend = p2[-1]+1
    return tuple([DOC[cid][pid][rid][lid][wid] for wid in xrange(wstart,wend)])

def iterDoc(targetCID=None):
    for cid, category in enumerate(DOC):
        if targetCID is not None and targetCID != cid: continue
        for pid, product in enumerate(category):
            for rid, review in enumerate(product):
                for lid, line in enumerate(review):
                    for wid, word in enumerate(line):
                        yield cid, pid, rid, lid, wid, word

def toDocForm(prods, maxReview=10):
    import wakachi
    ret = []
    for prod in prods:
        reviews = prod.getReviews(max=maxReview, htmlStyle=True)
        ret.append([])
        for review in reviews:
            morphslist = wakachi.parseLine(review, '<br />')
            ret[-1].append([])
            for morphs in morphslist:
                ret[-1][-1].append([Word(m.surface,m.original(),m.posid) for m in morphs])
    return ret

def tryToLoadProds(cid, createNew=False):
    import cPickle, os
    filename = PKL_FILE % cid
    if not createNew and os.path.exists(filename):
        file = open(filename, 'rb')
        prods = cPickle.load(file)
        file.close()
        return prods
    else:
        prods = toDocForm(product.getProducts(cid, minReviewCount=50)[1])
        file = open(filename, 'wb')
        cPickle.dump(prods, file)
        file.close()
        return prods

def initDoc(maxReview=10, targetCID=None, createNew=False):
    if targetCID is not None:
        doc = [tryToLoadProds(targetCID, createNew)]
    else:
        doc = []
        for cid, ls in enumerate(product.getCategoryList(minReviewCount=50)):
            doc.append(tryToLoadProds(cid, createNew))
    logging.log(logging.INFO, 'document input completed. categorySize=' + str(len(doc)))
    return doc

def toPhrase(words, posid):
    s = u''.join(map(lambda x: x.surface, words[0:-1]))
    phrase = Word(s+words[-1].surface, s+words[-1].origin, posid)
    return phrase

def combineDoc(doc, combineLine=False):
    combined = []
    for category in doc:
        combined.append([])
        for product in category:
            combined[-1].append([])
            for review in product:
                combined[-1][-1].append([])
                for line in review:
                    combined[-1][-1][-1].append([])
                    wid = 0
                    while wid < len(line):
                        if wid+1 < len(line) and line[wid].posid == 40 and line[wid+1].posid == 20: #「非常/に」など
                            combined[-1][-1][-1][-1].append(Word(line[wid].surface+line[wid+1].surface, line[wid].surface+line[wid+1].origin, 34))
                            wid += 2
                        elif 11 <= line[wid].posid <= 12: #形容接尾語「～っぽい」形容非自立「～やすい、～ない」など
                            combined[-1][-1][-1][-1][-1] += line[wid]
                            combined[-1][-1][-1][-1][-1].posid = 10 #形容詞-自立
                            wid += 2
                        else:
                            combined[-1][-1][-1][-1].append(line[wid])
                            wid += 1
    logging.log(logging.INFO, 'pre-combine completed')

    doc = combined
    combined = []
    for category in doc:
        combined.append([])
        for product in category:
            combined[-1].append([])
            for review in product:
                combined[-1][-1].append([])
                for line in review:
                    combined[-1][-1][-1].append([])
                    wid = 0
                    while wid < len(line):
                        if line[wid].isNoun() or line[wid].isPre(): #add as NounPhrase
                            w = wid + 1
                            while w < len(line) and line[w].isNoun(): w += 1
                            combined[-1][-1][-1][-1].append(toPhrase(line[wid:w], 38)) #名詞-一般
                            wid = w
                        elif wid+1 < len(line) and line[wid].isAdj() and line[wid+1].posid == 57: #「重さ」など
                            combined[-1][-1][-1][-1].append(toPhrase(line[wid:wid+2], 38)) #名詞-一般
                            wid += 2
                        else:
                            combined[-1][-1][-1][-1].append(line[wid])
                            wid += 1
    logging.log(logging.INFO, 'combine completed')

    if combineLine:
        doc = combined
        combined = []
        for category in doc:
            combined.append([])
            for product in category:
                combined[-1].append([])
                for review in product:
                    combined[-1][-1].append([[]])
                    for line in review:
                        if line == []:
                            combined[-1][-1][-1].append([])
                        else:
                            combined[-1][-1][-1][-1] += line
        logging.log(logging.INFO, 'line-combine completed')
    return combined

RAW_DOC = initDoc(targetCID=TARGET_CID) #doc[categoryID][productID][reviewID][lineID][wordID]=word
DOC = combineDoc(RAW_DOC, combineLine=True)
