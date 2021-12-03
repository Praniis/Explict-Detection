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


def addToURLQueue(url):
    db.ExplictDetect.urlQueue.update_one({'_id': 'urlQueue'}, {
        '$addToSet': {'queuedURL': url}
    })


def moveQueuedURLToProcessed(url):
    db.ExplictDetect.urlQueue.update_one({'_id': 'urlQueue'}, {
        '$pull': {'queuedURL': url},
        '$addToSet': {'processedURL': url}
    })


def moveQueuedURLToUnProcessed(url):
    db.ExplictDetect.urlQueue.update_one({'_id': 'urlQueue'}, {
        '$pull': {'queuedURL': url},
        '$addToSet': {'unProcessedURL': url}
    })


def getURLFromQueue(nos=1):
    result = db.ExplictDetect.urlQueue.find_one({'_id': 'urlQueue'}, {'queuedURL': {'$slice': nos}})
    if result and result['queuedURL'] and len(result['queuedURL']):
        return result['queuedURL']
    else:
        return []


def isExistsInQueuedURL(url):
    result = db.ExplictDetect.urlQueue.find_one({'_id': 'urlQueue', 'queuedURL': url })
    return True if result else False


def isExistsInProcessedURL(url):
    result = db.ExplictDetect.urlQueue.find_one({'_id': 'urlQueue', 'processedURL': url })
    return True if result else False


def isExistsInUnProcessedURL(url):
    result = db.ExplictDetect.urlQueue.find_one({'_id': 'urlQueue', 'unProcessedURL': url })
    return True if result else False


def isExistsInURLQueueCollection(link):
    result = db.ExplictDetect.urlQueue.find_one({
        '$and': [
            { '_id': 'urlQueue' },
            { '$or': [
                { 'queuedURL': link },
                { 'processedURL': link },
                { 'unProcessedURL': link }
            ]}
        ]
    })
    return True if result else False

def clearQueue():
    db.ExplictDetect.urlQueue.update_one({'_id': 'urlQueue'}, {
        '$set': {
            'queuedURL': [],
            'processedURL': [],
            'unProcessedURL': []
        }
    })
