from database import client as db
from datetime import datetime


def upsertInCrawledPage(insertData):
    insertData['updatedAt'] = datetime.now()
    return db.ExplictDetect.crawledPage.update_many({
        'hostname': insertData['hostname'],
        'url': insertData['url'],
    }, {
        '$set': insertData
    }, upsert=True)


def upsertInSentenceScores(insertData, crawledPageId):
    for i in insertData:
        i['crawledPageId'] = crawledPageId
        i['updatedAt'] = datetime.now()
    db.ExplictDetect.SentenceScores.delete_many({
        "crawledPageId": crawledPageId
    })
    db.ExplictDetect.SentenceScores.insert_many(insertData)


def addToCrawlURL(url):
    db.ExplictDetect.crawledURL.update_one({
        'url': url,
    }, {
        '$set': {
            'url': url,
            'status': 'queued'
        }
    }, upsert=True)


def updateCrawlStatus(url, crawlStatus):
    db.ExplictDetect.crawledURL.update_one({ 'url': url }, {
        '$set': {
            'status': crawlStatus
        }
    })


def getURLFromQueue(nos = 1):
    results = db.ExplictDetect.crawledURL.find({ 'status': 'queued' }).limit(nos)
    if results:
        urls = []
        for result in results:
            urls.append(result['url'])
        return urls
    else:
        return []        


def isExistsInCrawlURL(url):
    result = db.ExplictDetect.crawledURL.find_one({ 'url': url })
    return True if result else False


def clearCrawledURL():
    db.ExplictDetect.crawledURL.delete_many({})
