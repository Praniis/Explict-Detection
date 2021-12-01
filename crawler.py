import re
import requests
from urllib.parse import urlsplit, urlparse
from collections import deque
from bs4 import BeautifulSoup
from datetime import datetime

import dbConn

# starting_url = input("Enter the website url [ Along with http:// or https:// ]  : ")
starting_url = "https://medium.com/"

unprocessed_urls = deque([starting_url])
processed_urls = set()
parts = urlsplit(starting_url)

explicitWordList = []
with open('./dataset/explicitWordList.txt', 'r') as wordlist:
    explicitWordList = wordlist.read().splitlines()

def saveInDB(insertData):
    dbConn.ExplictDetectDB.get_collection('matchedContent').update_many({
        'hostname': insertData['hostname'],
        'url': insertData['url'],
        'matchedContent': insertData['matchedContent'],
        'metaData': {
            'title': insertData['metaData']['title'],
            'author': insertData['metaData']['author'],
        }
    }, {
        '$set': insertData
    }, upsert=True)

def getTextAndLinks(response):

    soup = BeautifulSoup(response.text, 'html.parser')
    bodyContent = soup.find('body')
    if bodyContent == None:
        return

    metaData = {
        'title': soup.find('title').get_text(),
        'description': '',
        'author': ''
    }

    for tag in soup.find_all("meta"):
        if tag.get("name", None) == "description":
            metaData['description'] = tag.get("content", None)
        elif tag.get("name", None) == "author":
            metaData['author'] = tag.get("content", None)

    sentences = bodyContent.get_text().split('\n')
    for sentence in sentences:
        if len(sentence.split(' ')) > 3:
            searchPattern = f'[A-Z][^\\.;]*({"|".join(explicitWordList)})[^\\.;]*'
            matches = re.finditer(searchPattern, sentence, re.IGNORECASE | re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                matchedContent = match.group()
                url = urlparse(response.url)
                insertData = {
                    'hostname': url.netloc,
                    'url': url.path,
                    'matchedContent': matchedContent,
                    'metaData': metaData,
                    'updatedAt': datetime.now()
                }
                saveInDB(insertData)

    for a in soup.find_all("a"):
        link = a.get('href') if a.get('href') and not(a.get('rel') and 'nofollow' in a.get('rel')) else ''
        if link == '':
            continue
        elif link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            if link.find('..') == -1:
                continue
            else:
                link = path + link

        check_list = ['javascript:void(0)', '.jpeg', '.mp4', '.mp3', '.png', '.gif','.pdf','.svg','.jpg','.docx','.doc','.JPG','.PDF']
        if link.rfind('#') != -1:
            link = link[0:link.rfind('#')]
        if link.rfind('?') != -1:
            link = link[0:link.rfind('?')]
        if not link in unprocessed_urls and not link in processed_urls and parts.netloc in link and not any(ele in link for ele in check_list):
            unprocessed_urls.append(link)

try:
    while len(unprocessed_urls):
        url = unprocessed_urls.popleft()
        parts = urlsplit(url)
        processed_urls.add(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        print('Crawling URL ' + url)
        try:
            response = requests.get(url)
            print('Scanned ' + url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print('Not Scanned ' + url)
            continue
        getTextAndLinks(response)
except Exception as e:
    print(e)
