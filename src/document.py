#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import logging
from word import Word

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

def initDoc(maxReview=10, targetCID=None, createNew=False):
    import cPickle, os
    filename = 'out/doc'
    if targetCID is not None: filename += str(targetCID)
    filename += '.pkl'
    if not createNew and os.path.exists(filename):
        file = open(filename, 'rb')
        doc = cPickle.load(file)
        file.close()
    else:
        import wakachi, product
        doc = []
        for cid, (category, prods) in enumerate(product.iterAllProducts(minReviewCount=50)):
            if targetCID is not None and cid != targetCID: continue
            logging.log(logging.INFO, u'category:%s parsing' % category)
            doc.append([])
            for pid, prod in enumerate(prods):
                reviews = prod.getReviews(max=maxReview, htmlStyle=True)
                doc[-1].append([])
                for rid, review in enumerate(reviews):
                    morphslist = wakachi.parseLine(review, '<br />')
                    doc[-1][-1].append([])
                    for lid, morphs in enumerate(morphslist):
                        doc[-1][-1][-1].append([Word(m.surface,m.original(),m.posid) for m in morphs])
        logging.log(logging.INFO, 'all product parsed')
        file = open(filename, 'wb')
        cPickle.dump(doc, file)
        file.close()
    logging.log(logging.INFO, 'document input completed. categorySize=' + str(len(doc)))
    return doc

def toPhrase(words, posid):
    s = u''.join(map(lambda x: x.surface, words[0:-1]))
    phrase = Word(s+words[-1].surface, s+words[-1].origin, posid)
    return phrase

def combineDoc(doc):
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
                            combined[-1][-1][-1][-1].append(toPhrase(line[wid:w], line[w-1].posid))
                            wid = w
                        elif wid+1 < len(line) and line[wid].isAdj() and line[wid+1].posid == 57: #「重さ」など
                            combined[-1][-1][-1][-1].append(toPhrase(line[wid:wid+2], 38))
                            wid += 2
                        else:
                            combined[-1][-1][-1][-1].append(line[wid])
                            wid += 1

    logging.log(logging.INFO, 'combine completed')
    return combined

RAW_DOC = initDoc(targetCID=None) #doc[categoryID][productID][reviewID][lineID][wordID]=word
DOC = combineDoc(RAW_DOC)