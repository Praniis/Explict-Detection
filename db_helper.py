from pymongo import UpdateOne
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

def upsertInSentenceScores(insertData):
    bulkWriteSS = list()
    for i in insertData:
        if len(bulkWriteSS) < 1000:
            bulkWriteSS.append(UpdateOne({
                'crawledPageId': i['crawledPageId'],
                'text': i['text']
            }, {
                '$set': i
            }, upsert=True))
        else:
            db.ExplictDetect.SentenceScores.bulk_write(bulkWriteSS)
            bulkWriteSS = list()
    if len(bulkWriteSS):
        db.ExplictDetect.SentenceScores.bulk_write(bulkWriteSS)


def addToCrawlURL(urls):
    bulkWrites = list()
    for url in urls:
        bulkWrites.append(UpdateOne({
            'url': url,
        }, {
            '$setOnInsert': {
                'url': url,
                'status': 'queued'
            }
        }, upsert = True))
    db.ExplictDetect.crawledURL.bulk_write(bulkWrites) 


def updateCrawlStatus(url, crawlStatus):
    db.ExplictDetect.crawledURL.update_many({ 'url': url }, {
        '$set': {
            'status': crawlStatus
        }
    })


def getURLFromQueue(nos = 1):
    results = db.ExplictDetect.crawledURL.find({ 'status': 'queued' }).limit(nos)
    urls = set()
    if results:
        for result in results:
            urls.add(result['url'])
        return urls
    else:
        return urls


def isExistsInCrawlURL(url):
    result = db.ExplictDetect.crawledURL.find_one({ 'url': url })
    return True if result else False


def clearCrawledURL():
    db.ExplictDetect.crawledURL.delete_many({})
