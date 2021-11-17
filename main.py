import re
import os
import json
from sys import flags
from pymongo import database
import requests
import requests.exceptions
from urllib.parse import urlsplit, urlparse
from collections import deque
from bs4 import BeautifulSoup
from datetime import datetime

import dbConn

# starting_url = input("Enter the website url [ Along with http:// or https:// ]  : ")
starting_url = "https://www.theverge.com/"

unprocessed_urls = deque([starting_url])
processed_urls = set()
set_emails = set()

global filename

parts = urlsplit(starting_url)
filename = parts.netloc

def saveInDB(insertData):
    # pass
    dbConn.ExplictDetectDB["WordMatch"].insert_one(insertData)

def getTextAndLinks(response):

    soup = BeautifulSoup(response.text, "html.parser")
    bodyContent = soup.find('body')
    if bodyContent == None:
        return

    sentences = bodyContent.get_text().split('\n')
    for sentence in sentences:
        if len(sentence.split(' ')) > 3:
            explicitSet = ["fuck"]
            searchPattern = "[A-Z][^\\.;]*(" + "|".join(explicitSet) + ")[^\\.;]*"
            matches = re.finditer(searchPattern, sentence, re.MULTILINE | re.IGNORECASE)
            for matchNum, match in enumerate(matches, start=1):
                explictContent = match.group()
                url = urlparse(response.url)
                insertData = {
                    "hostname": url.hostname,
                    "url": url.path,
                    "explictContent": explictContent,
                    "metaData": {
                        "title": "",
                        "author": "",
                    },
                    "searchPattern": searchPattern,
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }
                saveInDB(insertData)

    for anchor in soup.find_all("a"):
        link = anchor.attrs["href"] if "href" in anchor.attrs else ''
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            if link.find('..') == -1:
                continue
            else:
                link = path + link

        check_list = ["javascript:void(0)", ".jpeg", ".mp4", ".mp3", ".png", ".gif",".pdf",".svg",".jpg",".docx",".doc",".JPG",".PDF"]
        if link.rfind("#") != -1:
            link = link[0:link.rfind("#")]
        if link.rfind("?") != -1:
            link = link[0:link.rfind("?")]
        if not link in unprocessed_urls and not link in processed_urls and parts.netloc in link and not any(ele in link for ele in check_list):
            unprocessed_urls.append(link)

try:
    while len(unprocessed_urls):
        url = unprocessed_urls.popleft()
        parts = urlsplit(url)
        processed_urls.add(url)
        filename = parts.netloc
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        print("Crawling URL " + url)
        try:
            response = requests.get(url)
            print("Scanned " + url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print("Not Scanned " + url)
            continue
        getTextAndLinks(response)
except Exception as e:
    # Error log
    print(e)