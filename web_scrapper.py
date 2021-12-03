import sys
import validators
from os.path import splitext
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from database import client as db
from db_helper import *
from http_client import makeParallelReq
from text_analyze import processText


BLOCKED_EXTS = [
    'javascript:void(0)', '.jpeg', '.mp4', '.mp3', '.png', '.gif',
    '.pdf', '.svg', '.jpg', '.docx', '.doc', '.JPG', '.PDF'
]


def detectPageContent(url, resText):

    parseResult = urlparse(url)
    baseURL = f'{parseResult.scheme}://{parseResult.netloc}'
    soup = BeautifulSoup(resText, 'html.parser')
    metaData = {
        'title': soup.find('title').get_text() if soup.find('title') else '',
        'description': '',
        'author': ''
    }

    for tag in soup.find_all("meta"):
        if tag.get("name", None) == "description":
            metaData['description'] = tag.get("content", None)
        elif tag.get("name", None) == "author":
            metaData['author'] = tag.get("content", None)

    bodyContent = soup.find('body')
    if bodyContent == None:
        return

    insertData = {
        'hostname': parseResult.netloc,
        'url': parseResult.path,
        'metaData': metaData,
        'rawHTML': resText
    }

    insertedData = upsertInCrawledPage(insertData)
    crawledPageId = insertedData.upserted_id
    if crawledPageId != None:
        pageSentenceScores = processText(str(bodyContent))
        upsertInSentenceScores(pageSentenceScores, crawledPageId)

    for a in soup.find_all('a', href=True):
        link = a.get('href') if not(a.get('rel') and 'nofollow' in a.get('rel')) else ''
        if link == '':
            continue
        elif link.startswith('/'):
            link = baseURL + link
        elif not link.startswith('http') and link.find('..') == -1:
            continue

        parseLink = urlparse(link)
        link = f'{parseLink.scheme}://{parseLink.netloc}{parseLink.path}'
        if not validators.url(link):
            continue

        linkExt = splitext(parseLink.path)[1]
        if (
            parseResult.netloc == parseLink.netloc and
            not linkExt in BLOCKED_EXTS and
            not isExistsInURLQueueCollection(link)
        ):
            addToURLQueue(link)


def scrapQueuedURL():
    MAX_TRESHOLD = 15
    try:
        while True:
            urls = getURLFromQueue(MAX_TRESHOLD)
            totalURLs = len(urls)
            if len(urls) > 0:
                startTime = datetime.now()
                print(f"[CRAWL]  Processing           {totalURLs} URLs")
                responses = makeParallelReq(urls)
                print(f"[CRAWL]  Completed Processing {totalURLs} URLs in    {datetime.now()-startTime}")
                startTimeML = datetime.now()
                print(f"[ML]     Processing           {totalURLs} URLs")
                for response in responses:
                    url, resText = response['url'], response['resText']
                    if response['success']:
                        detectPageContent(url, resText)
                        moveQueuedURLToProcessed(url)
                    else:
                        moveQueuedURLToUnProcessed(url)
                print(f"[ML]     Completed Processing     {totalURLs} URLs in {datetime.now()-startTimeML}")
                print(f"[REPORT] Total Time                                   {datetime.now()-startTime}\n\n")
            else:
                break
    except Exception as e:
        print(e)

    try:
        while True:
            userChoice = input("Do you want to scrap futher (Y/n)? ")
            if userChoice.lower() == 'y':
                getURLAndStartScrap()
            else:
                print('[EXIT] Program Exited successfully... :)')
                sys.exit(0)
    except Exception as e:
        print(e)


def getURLFromUser():
    try:
        url = input("Enter the website url [Along with http:// or https://] (Press Ctrl+C to exit): ")
        parseResult = urlparse(url)
        url = f'{parseResult.scheme}://{parseResult.netloc}{parseResult.path}'
        if not validators.url(url):
            print("[INVALID] Kindly enter a valid url")
            sys.exit(0)
        addToURLQueue(url)
    except KeyboardInterrupt:
        sys.exit(0)


def getURLAndStartScrap():
    getURLFromUser()
    scrapQueuedURL()


if __name__ == '__main__':
    urlQueueCount = db.ExplictDetect.urlQueue.find_one({'_id': 'urlQueue'}, {
        'queuedURL': {'$size': '$queuedURL'},
        'processedURL': {'$size': '$processedURL'},
        'unProcessedURL': {'$size': '$unProcessedURL'}
    })

    if urlQueueCount == None:
        db.ExplictDetect.urlQueue.insert_one({
            '_id': 'urlQueue',
            'queuedURL': [],
            'processedURL': [],
            'unProcessedURL': [],
        })
        getURLAndStartScrap()
    elif urlQueueCount['queuedURL'] == 0:
        getURLAndStartScrap()
    else:
        userChoice = input("Do you want to continue old progress (Y/n)? ")
        if userChoice.lower() == 'y':
            scrapQueuedURL()
        else:
            clearQueue()
            getURLAndStartScrap()
