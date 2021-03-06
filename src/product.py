#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: aikawa
'''
import util
import glob
import re
import unicodedata
import logging

#50個以上レビューが存在し、全てがきちんと同じカテゴリのものが取得できている物
SELECTED_FLAG = True
SELECTED=[u'AVアンプ',u'AVセレクター',u'Bluetoothアダプタ',u'CDプレーヤー',u'CPUクーラー',u'DVDドライブ',u'DVDメディア',u'ETC車載器',u'ICカードリーダー・ライター',u'LED電球',u'OSソフト',u'PCケース',u'PCスピーカー',u'PC用ワンセグチューナー',u'PDA',u'SDメモリーカード・MMC',u'USBハブ',u'WEBカメラ',u'その他カメラ関連製品',u'その他ネットワーク機器',u'その他プレーヤー・レシーバー',u'その他車載機器',u'インターフェイスカード',u'エアコン',u'エフェクター',u'カーオーディオ',u'カースピーカー',u'カーナビ',u'ケースファン',u'ゲーム周辺機器',u'コンタクトレンズ 1day',u'コンタクトレンズ 2week',u'コンバージョンレンズ・アダプタ',u'コーヒーメーカー',u'サイクルコンピューター',u'サイクルライト',u'サウンドカード・ユニット',u'シュレッダー',u'スキャンコンバータ',u'スタッドレスタイヤ',u'ズボンプレッサー',u'セキュリティソフト',u'チャイルドシート',u'テレビドアホン',u'テレビリモコン',u'デジタルカメラ',u'デジタルフォトフレーム',u'デジタル一眼レフカメラ',u'デスクトップパソコン',u'トースター',u'ドライヤー・ヘアアイロン',u'ネットワークカメラ',u'ノートパソコン',u'ノートパソコン用クーラー',u'ハードディスク・HDD(2.5インチ)',u'ハードディスク・HDD(3.5インチ)',u'パター',u'ヒーター・ストーブ',u'ビデオカメラ',u'ビデオカード',u'ビデオキャプチャ',u'ビデオデッキ',u'フィルムスキャナ',u'フォトストレージ',u'ブルーレイドライブ',u'ブルーレイプレーヤー',u'ブルーレイ・DVDレコーダー',u'プラズマテレビ',u'プリメインアンプ',u'プリンタ',u'プリントサーバー',u'ヘッドセット',u'ヘッドホン・イヤホン',u'ペンタブレット',u'ホットプレート',u'ホームベーカリー',u'ポータブルAVプレーヤー',u'ポータブルCD',u'ポータブルDVDプレーヤー',u'ポータブルMD',u'マザーボード',u'マッサージ器',u'ミキサー・フードプロセッサー',u'ミシン',u'メンズグルーミング',u'ラジカセ',u'リアプロジェクションテレビ',u'レンズフィルター',u'三脚・一脚',u'体脂肪計・体重計',u'健康器具・医療機器',u'充電池・充電器',u'冷蔵庫・冷凍庫',u'動画編集ソフト',u'地デジアンテナ',u'布団乾燥機',u'扇風機・サーキュレーター',u'掃除機',u'携帯テレビ',u'有線ブロードバンドルーター',u'洗濯機',u'浄水器・整水器',u'液晶テレビ',u'液晶モニタ・液晶ディスプレイ',u'温水洗浄便座',u'炊飯器',u'無線LANブロードバンドルーター',u'生ごみ処理機',u'画像編集ソフト',u'空気清浄機',u'精米機',u'美容器具',u'腕時計',u'衣類乾燥機',u'車載用地デジチューナー',u'防湿庫',u'電子レンジ・オーブンレンジ',u'電子辞書',u'電気ポット・電気ケトル',u'電源ユニット',u'電話機',u'食器洗い機',u'香水']
#SELECTED=[u'Bluetoothアダプタ', u'CDプレーヤー', u'OSソフト', u'PC用ワンセグチューナー', u'SDメモリーカード・MMC', u'WEBカメラ', u'その他ネットワーク機器', u'インターフェイスカード', u'シュレッダー', u'テレビドアホン', u'デジタルフォトフレーム', u'ドライヤー・ヘアアイロン', u'ブルーレイドライブ', u'プリンタ', u'健康器具・医療機器', u'充電池・充電器', u'動画編集ソフト', u'扇風機・サーキュレーター', u'携帯テレビ', u'温水洗浄便座', u'生ごみ処理機', u'画像編集ソフト', u'電子レンジ・オーブンレンジ', u'電気ポット・電気ケトル', u'香水']


class Product:
    '''
    data.keys()=[u'Comment', u'ItemPageUrl', u'ReviewPageUrl', u'TotalScoreAve', u'ImageUrl', u'SaleDate', u'ProductName', u'MakerName', u'NumOfBbs', u'PvRanking', u'LowestPrice', u'BbsPageUrl', u'Review', u'ProductID', u'CategoryName']
    '''
    def __init__(self, dict):
        self.data = dict
    def __getitem__(self, key):
        return self.data.__getitem__(key)
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self['ProductID']
    def __unicode__(self):
        return self['MakerName'] + ' ' + self['ProductName']
    def reviewSize(self):
        return len(self['Review'])
    def getReview(self, index, htmlStyle=False, withTitle=False):
        reviews = self['Review']
        if not (0 <= index < len(reviews)): return ''
        review = reviews[index]
        res = ''
        if withTitle: res += review['title'] + ':'
        res += review['message']
        if not htmlStyle: res = util.html2plain(res)
        return res
    def getReviews(self, max=None, htmlStyle=False, withTitle=False):
        ret = []
        size = self.reviewSize()
        if max is not None: size = min(max,size)
        for i in xrange(size):
            ret.append(self.getReview(i,htmlStyle,withTitle))
        return ret

JSON_DIR=u'kakaku1217/'

def _inputProducts(filename):
    data = util.jsonLoad(filename)
    prods = [Product(x) for x in data]
    return prods

def _extractinfo(filename):
    mo = re.match('(.*/)*?([^/]*)_(\d+).txt', filename)
    category = unicodedata.normalize('NFC', mo.groups()[-2])
    reviewcnt = int(mo.groups()[-1])
    return category, reviewcnt

def getCategoryList(minReviewCount=0, categoryFilter=None):
    ret = []
    if SELECTED_FLAG and categoryFilter is None: categoryFilter = SELECTED
    for filename in glob.glob(JSON_DIR+u'/*.txt'):
        if u'category.txt' in filename: continue
        category, reviewcnt = _extractinfo(filename)
        if reviewcnt < minReviewCount: continue
        if categoryFilter is not None and category not in categoryFilter: continue
        ret.append((filename, category, reviewcnt))
    return ret

def getProducts(index, minReviewCount=0, categoryFilter=None):
    filename, category, reviewcnt = getCategoryList(minReviewCount, categoryFilter)[index]
    logging.log(logging.INFO, category + ' ' + str(reviewcnt))
    prods = _inputProducts(filename)
    return category, prods

def iterAllProducts(minReviewCount=0, categoryFilter=None):
    for filename, category, reviewcnt in getCategoryList(minReviewCount, categoryFilter):
        logging.log(logging.INFO, category + ' ' + str(reviewcnt))
        prods = _inputProducts(filename)
        yield category, prods

def getEntries(index, minReviewCount=0, categoryFilter=None):
    category, prods = getProducts(index, minReviewCount, categoryFilter)
    for prod in prods:
        if len(prod['Review']):
            entries = map(lambda x: x[0], prod['Review'][0]['scores'])
            return entries[:-1] # 最後の一つは「満足度」なので除外
    print 'error at getEntries', category, prods
    return None


def getCategoryName(cid):
    return getProducts(cid)[0]

def getProductNames(cid):
    prods = getProducts(cid)[1]
    return [unicode(prod) for prod in prods]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import json
    jsonstr = '[{"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u6b63\u65b9\u5f62 ", "ItemPageUrl": "http://kakaku.com/item/21584010291/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": "4.50", "ReviewPageUrl": "http://review.kakaku.com/review/21584010291/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/21584010291.jpg ", "SaleDate": null, "ProductName": "MK-758KSH", "MakerName": "\u30e2\u30ea\u30bf", "PvRanking": "1", "Review": [{"message": "\u6628\u65e5\u8cb7\u3044\u307e\u3057\u305f\u3002<br /><br />\u9577\u65b9\u5f62\u306e\u7269\u3068\u8ff7\u3063\u305f\u306e\u3067\u3059\u304c<br />\u5834\u6240\u3092\u53d6\u308a\u3059\u304e\u308b\u306e\u3067\u3001\u3053\u308c\u3092\u8cb7\u3044\u307e\u3057\u305f\u3002<br /><br />\u524d\u4f7f\u3063\u3066\u3044\u305f\u306e\u3088\u308a\u6696\u304b\u3044\u3067\u3059\u2606<br />\u4e00\u756a\u6c17\u306b\u5165\u3063\u305f\u306e\u306f<br />\u9ad8\u3055\u304c\u666e\u901a\u306e\u7269\u3088\u308a\u9ad8\u304f\u306a\u3063\u3066\u305f\u3053\u3068\u3067\u3059\u3002<br /><br />\u6a2a\u3092\u5411\u3044\u3066\u5bdd\u8ee2\u3093\u3067\u3082\u592a\u3082\u3082\u3084\u8170\u3068\u304b\u304c<br />\u30b3\u30bf\u30c4\u306e\u67a0\u306b\u5f53\u305f\u3089\u306a\u304f\u306a\u3063\u305f\u3053\u3068\u3067\u3059\u2606<br /><br />\u5805\u82e6\u3057\u3044\u601d\u3044\u3057\u306a\u304f\u3066\u3044\u3044\u306e\u3067\u5b09\u3057\u3044\u3067\u3059(^^\u266a<br /><br />\u5024\u6bb5\u3082\u5b89\u304f\u3066\u5927\u6e80\u8db3\u3067\u3059\u2606", "scores": [["\u30c7\u30b6\u30a4\u30f3", 4], ["\u8cea\u611f", 4], ["\u6696\u304b\u3055", 5], ["\u30b5\u30a4\u30ba", 5], ["\u6e80\u8db3\u5ea6", 5]], "user": "\u682a\u72ac\u3061\u3083\u3093\u2606\u266a", "postinfo": "2008\u5e7411\u670813\u65e5 20:06  [168323]", "title": "MK-758KSH"}, {"message": "\u5929\u677f\u4ee5\u5916\u304c\u304b\u306a\u308a\u8efd\u304f\u3066\u9a5a\u304d\u307e\u3057\u305f\u304c\u554f\u984c\u3042\u308a\u307e\u305b\u3093\u3002<br />\u3053\u3061\u3089\u306e\u6700\u5b89\uffe55035\u3067\u8cfc\u5165\u3057\u307e\u3057\u305f\uff08\u9001\u6599\u7121\u6599\uff09<br />\u898b\u305f\u76ee\u3084\u8cea\u611f\u3092\u5927\u4e8b\u306b\u3059\u308b\u65b9\u306f\u305c\u3072\u4ed6\u3092\u3069\u3046\u305e\u30fb\u30fb\u30fb\uff08\u6728\u6750\u306f\u4e00\u5207\u4f7f\u7528\u3057\u3066\u304a\u308a\u307e\u305b\u3093\uff09<br />\u305d\u308c\u4ee5\u5916\u306e\u65b9\u3084\u4f7f\u3048\u308c\u3070\u3044\u3044\u4eba\u306b\u306f\u304a\u3059\u3059\u3081\u3067\u304d\u307e\u3059\u3088\uff5e\u3002", "scores": [["\u30c7\u30b6\u30a4\u30f3", 3], ["\u8cea\u611f", 3], ["\u6696\u304b\u3055", 4], ["\u30b5\u30a4\u30ba", 4], ["\u6e80\u8db3\u5ea6", 4]], "user": "\u91d1\u5229\u624b\u6570\u6599\u7121\u6599\uff01\uff01", "postinfo": "2008\u5e7411\u670810\u65e5 15:10  [167802]", "title": "MK-758KSH"}], "LowestPrice": "4450", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21584010291/", "NumOfBbs": "1", "ProductID": "21584010291"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/K0000067219/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000067219/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3197", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "2", "Review": [], "LowestPrice": "14452", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000067219/", "NumOfBbs": null, "ProductID": "K0000067219"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000162328/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000162328/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000162328.jpg", "SaleDate": null, "ProductName": "RSE-751(B) [\u30d6\u30e9\u30c3\u30af]", "MakerName": "YAMAZEN", "PvRanking": "3", "Review": [], "LowestPrice": "4830", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000162328/", "NumOfBbs": null, "ProductID": "K0000162328"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 ", "ItemPageUrl": "http://kakaku.com/item/21584010289/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21584010289/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/21584010289.jpg ", "SaleDate": null, "ProductName": "MK-1058NH", "MakerName": "\u30e2\u30ea\u30bf", "PvRanking": "4", "Review": [], "LowestPrice": "7411", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21584010289/", "NumOfBbs": "1", "ProductID": "21584010289"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/K0000067216/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000067216/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3194", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "5", "Review": [], "LowestPrice": "10900", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000067216/", "NumOfBbs": null, "ProductID": "K0000067216"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/21583210343/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21583210343/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3780", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "6", "Review": [], "LowestPrice": "19800", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21583210343/", "NumOfBbs": null, "ProductID": "21583210343"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u6b63\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/K0000067218/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000067218/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3196", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "7", "Review": [], "LowestPrice": "13453", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000067218/", "NumOfBbs": null, "ProductID": "K0000067218"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/21583210335/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21583210335/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3382", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "8", "Review": [], "LowestPrice": "17300", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21583210335/", "NumOfBbs": "1", "ProductID": "21583210335"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/21583210270/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21583210270/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/21583210270.jpg ", "SaleDate": null, "ProductName": "KTR-3475", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "9", "Review": [], "LowestPrice": "15800", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21583210270/", "NumOfBbs": null, "ProductID": "21583210270"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000163039/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000163039/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000163039.jpg", "SaleDate": null, "ProductName": "RSE-601(B) [\u30d6\u30e9\u30c3\u30af]", "MakerName": "YAMAZEN", "PvRanking": "10", "Review": [], "LowestPrice": "4980", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000163039/", "NumOfBbs": null, "ProductID": "K0000163039"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/21583210331/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21583210331/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3282", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "11", "Review": [], "LowestPrice": "14700", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21583210331/", "NumOfBbs": null, "ProductID": "21583210331"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000158340/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000158340/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000158340.jpg ", "SaleDate": null, "ProductName": "MDK-HT600C", "MakerName": "\u30e2\u30ea\u30bf", "PvRanking": "11", "Review": [], "LowestPrice": "8202", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000158340/", "NumOfBbs": null, "ProductID": "K0000158340"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/21583210332/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/21583210332/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3286", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "13", "Review": [], "LowestPrice": "9480", "BbsPageUrl": "http://bbs.kakaku.com/bbs/21583210332/", "NumOfBbs": null, "ProductID": "21583210332"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000061413/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000061413/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000061413.jpg ", "SaleDate": null, "ProductName": "MR-80SH", "MakerName": "YAMAZEN", "PvRanking": "14", "Review": [], "LowestPrice": "9493", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000061413/", "NumOfBbs": null, "ProductID": "K0000061413"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000061404/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000061404/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000061404.jpg ", "SaleDate": null, "ProductName": "WHS-75", "MakerName": "YAMAZEN", "PvRanking": "14", "Review": [], "LowestPrice": "9900", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000061404/", "NumOfBbs": null, "ProductID": "K0000061404"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000163038/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000163038/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000163038.jpg", "SaleDate": null, "ProductName": "RSE-601(W) [\u30db\u30ef\u30a4\u30c8]", "MakerName": "YAMAZEN", "PvRanking": "16", "Review": [], "LowestPrice": "5078", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000163038/", "NumOfBbs": null, "ProductID": "K0000163038"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/K0000067220/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000067220/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KTR-3393", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "17", "Review": [], "LowestPrice": "20600", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000067220/", "NumOfBbs": "2", "ProductID": "K0000067220"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000158336/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000158336/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000158336.jpg ", "SaleDate": null, "ProductName": "MK-FH105C-C [\u30e9\u30a4\u30c8\u30d9\u30fc\u30b8\u30e5]", "MakerName": "\u30e2\u30ea\u30bf", "PvRanking": "17", "Review": [], "LowestPrice": "7646", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000158336/", "NumOfBbs": null, "ProductID": "K0000158336"}, {"Comment": "\u30bf\u30a4\u30d7\uff1a\u5bb6\u5177\u8abf \u5353\u53f0\u5f62\u72b6\uff1a\u9577\u65b9\u5f62 \u9060\u8d64\u5916\u7dda\u30d2\u30fc\u30bf\u30fc\uff1a\u25cb ", "ItemPageUrl": "http://kakaku.com/item/K0000067210/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000067210/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/nowprinting.gif", "SaleDate": null, "ProductName": "KDR-3298", "MakerName": "\u30b3\u30a4\u30ba\u30df", "PvRanking": "17", "Review": [], "LowestPrice": "16399", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000067210/", "NumOfBbs": null, "ProductID": "K0000067210"}, {"Comment": null, "ItemPageUrl": "http://kakaku.com/item/K0000158338/", "CategoryName": "\u5bb6\u96fb>\u3053\u305f\u3064", "TotalScoreAve": null, "ReviewPageUrl": "http://review.kakaku.com/review/K0000158338/", "ImageUrl": "http://img.kakaku.com/images/productimage/m/K0000158338.jpg ", "SaleDate": null, "ProductName": "MK-FBT75C-H [\u30e9\u30a4\u30c8\u30b0\u30ec\u30fc]", "MakerName": "\u30e2\u30ea\u30bf", "PvRanking": "20", "Review": [], "LowestPrice": "7646", "BbsPageUrl": "http://bbs.kakaku.com/bbs/K0000158338/", "NumOfBbs": null, "ProductID": "K0000158338"}]'
    data = json.loads(jsonstr)
    print data[0].keys()
    prods = [Product(x) for x in data]
    print prods
    print util.pp_str(map(lambda x: x['ProductName'], prods))
    print '\n'.join(prods[0].getReviews())