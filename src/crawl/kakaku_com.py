#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa

references:
http://apiblog.kakaku.com/
http://www.kharakawa.com/kh.log/archives/2006/10/kakakucom_web_api_for_py_1.html
'''
import sys
import os
import types
import urllib
import logging
logging.basicConfig(level=logging.FATAL)
import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup
import json
import time

DATA_DIR = 'data/'

def pp_str(obj, indent= None):
    if isinstance(obj, list) or isinstance(obj, dict) or isinstance(obj, tuple):
        orig = json.dumps(obj,indent=indent)
        return eval("u'''%s'''" % orig).encode('utf-8')
    else:
        return obj

def urlopen(url, data=None, proxies=None, sleeptime=1):
    maxtry = 10
    for _ in xrange(maxtry):
        try:
            return urllib.urlopen(url, data, proxies)
            time.sleep(sleeptime)
        except IOError, e:
            print e, 'url:', url
            time.sleep(10)
    print >> sys.stderr, 'urlopen failed at url:', url

def htmldecode(str):
    codes=[(' ','&nbsp;'),('<','&lt;'),('>','&gt;'),('"','&quot;'),('&','&amp;')]
    for code in codes:
        str = str.replace(code[1], code[0])
    return str

class KakakuComAPI:
    ITEM_SEARCH_URL='http://api.kakaku.com/WebAPI/ItemSearch/Ver1.0/ItemSearch.aspx'
    ITEM_INFO_URL='http://api.kakaku.com/WebAPI/ItemInfo/Ver1.0/ItemInfo.ashx'
    API_KEY_DEFAULT='675dd59583d1c05f23206539a7f530da'
    UNMARSHALLERS = {
        'Item': lambda e: dict([(c.tag, c.text) for c in e]),
        'ProductInfo': lambda e: [c.text for c in e if c.tag == 'Item'],
        'Error': lambda e: e[0].text,
    }

    def __init__(self):
        pass

    def search(self, Keyword, **params):
        if type(Keyword) is types.UnicodeType:
            Keyword = Keyword.encode('utf-8')
        params['Keyword'] = Keyword
        if 'HitNum' not in params:
            params['HitNum'] = 20
        return self.request(KakakuComAPI.ITEM_SEARCH_URL, **params)

    def product(self, ProductID, **params):
        params['ProductID'] = ProductID
        return self.request(KakakuComAPI.ITEM_INFO_URL, **params)

    def request(self, url, **params):
        if 'APiKey' not in params:
            params['ApiKey'] = KakakuComAPI.API_KEY_DEFAULT
        if 'ResultSet' not in params:
            params['ResultSet'] ='Medium'
        params = urllib.urlencode(params)
        logging.debug('Paramaters: '+params)
        xml = urlopen(url+'?'+params)
        logging.info('RequestedUrl: '+xml.geturl())
        result = {'RequestedUrl':xml.geturl()}
        for _, elem in ET.iterparse(xml):
            unmarshal = KakakuComAPI.UNMARSHALLERS.get(elem.tag, lambda e: e.text)
            elem.text = unmarshal(elem)
            if elem.tag in ( 'ProductInfo' , 'Error' , 'NumOfResult' ):
                result[elem.tag] = elem.text
        xml.close()
        return result

class ReviewParser:
    SITE_URL = 'http://review.kakaku.com'
    BASE_URL = SITE_URL + '/review/'
    def parse(self, id):
        url = ReviewParser.BASE_URL + id + '/'
        return self.parseURL(url)
    def parseURL(self,url):
        soup = BeautifulSoup(urlopen(url))
        reviews = soup.findAll('div', {'class':'box05 mTop10'})
        result = []
        for review in reviews:
            leftbox = review.findAll('div', {'class':'floatL'})
            user = leftbox[0].a.text
            postinfo = htmldecode(leftbox[0].span.text)
            starbox = leftbox[1].findAll('table', limit=2)
            scores = []
            for starinfo in starbox:
                stars = starinfo.findAll('tr')
                for star in stars:
                    title = star.th.text
                    try :
                        value = int(star.td.text[-1:])
                    except ValueError: #in case of '無評価'
                        value = - 1
                    scores.append((title, value))
            content = review.find('div', {'class':'box06 w485 mTop5'})
            title = content.find('strong').text
            message = content.find('p', {'class':'mTop10'}).renderContents()
            result.append({'user':user, 'postinfo':postinfo , 'title':title, 'message':message, 'scores':scores})
        try:
            nextpage = soup.find('div', id='pageNavi').find('a', {'class':'arrowNext01'})
            if nextpage:
                result += self.parseURL(ReviewParser.SITE_URL+nextpage['href'])
        except AttributeError: #some pages don't have <div id="pageNavi">
            pass
        return result

def unique(ls):
    used = {}
    res = []
    for l in ls:
        if l in used: continue
        used[l] = 1
        res.append(l)
    return res

def getCategories():
    url='http://kakaku.com/sitemap/category_list.html'
    soup = BeautifulSoup(urlopen(url))
    content = soup.find('div', id='main')
    links = content.findAll('a')
    categories = [x.text for x in links if len(x.attrs) == 1]
    return unique(categories)


def search(keyword):
    api = KakakuComAPI()
    result = api.search(Keyword=keyword)
    return result

def getReview(id):
    rp = ReviewParser()
    review = rp.parse(id)
    return review

def getProducts(keyword):
    result = search(keyword)
    logging.debug('SearchResult:' + pp_str(result))
    if 'Error' in result:
        products = []
    else:
        products = [x for x in result['ProductInfo']]
    logging.debug(products)
    for i, product in enumerate(products):
        id = product['ProductID']
        review = getReview(id)
        products[i]['Review'] = review
    return products

def crawl(start=0):
    categories = getCategories()
    print len(categories), pp_str(categories)
    out = open(DATA_DIR+'category.txt', 'w')
    print >> out, len(categories), pp_str(categories)
    out.close()
    for cid, category in enumerate(categories):
        if start > cid: continue
        review_cnt = 0
        products = getProducts(category)
        for p in products: review_cnt += len(p['Review'])
        out = open(DATA_DIR+category+'_'+str(review_cnt)+'.txt', 'w')
        json.dump(products, out)
        out.close()
        print cid, review_cnt, category
    return products

if __name__ == '__main__' :
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    start = 0
    if (len(sys.argv) > 1): start = int(sys.argv[1])
    crawl(start)