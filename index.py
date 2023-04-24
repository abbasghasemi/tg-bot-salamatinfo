#!/usr/bin/python3

import os, sys, json
from FLOG import LOG_INFO
from TGBOT import TelegramBot
from DM import DataMining
from SIAPI import API
ROOT_PATH = '/SalamatInfo/'
TGB_KEY = "981e9f0ad23cfcb682f11d55718aefbd"
GLOBAL_CAN_SET_HEADER = True
GLOBAL_HEADERS = []

def addHeader(name, value):
    global GLOBAL_CAN_SET_HEADER, GLOBAL_HEADERS
    if GLOBAL_CAN_SET_HEADER == False:
        LOG_INFO("Can't set the header [%s: %s]" % (name, value))
        return
    GLOBAL_HEADERS.append({name: str(value).strip()})

def setHeasers():
    global GLOBAL_CAN_SET_HEADER, GLOBAL_HEADERS
    if GLOBAL_CAN_SET_HEADER == True:
        GLOBAL_CAN_SET_HEADER = False
        for header in GLOBAL_HEADERS:
            name = list(header.keys())[0]
            print("%s: %s" % (name, header[name]))
        print()

def server(name):
    if name in os.environ.keys():
        return os.environ[name].strip()
    return ''

def echo(string = ''):
    global GLOBAL_CAN_SET_HEADER
    if GLOBAL_CAN_SET_HEADER == True:
        setHeasers()
    if type(string) is not str:
        string = str(string)
    if string:
        print(string, end='')

def index(content):
    if content:
        try:
            tg = TelegramBot(content)
            dm = DataMining(tg)
            body = {
                "Crawled_ID": dm.getCrawledID(),
                "Lang_ID": 1, "Type_ID": 2,
                "Category_ID": dm.getCategoryID(),
                "Title": dm.getTitle(),
                "ShortText": dm.getText()[:150].split("\n")[0],
                "LongText": '<p>' + '</p><p>'.join(dm.getText().split("\n")) + '</p>',
                "IsActive": True,
                "IsHot": False,
                "Description": dm.getReference() + " | ".join(dm.getLinks())
            }
            if len(dm.getHashTags()) != 0:
                body["Keyword_IDs"] = ",".join(dm.getHashTags())
            body['Pic'] = {}
            imgB64 = tg.getContentFile()
            if imgB64:
                body['Pic'] = {"Name": dm.getTitle().replace(" ", "-"), "Size": imgB64['size'], "Type": "jpg", "Content": imgB64['content']}
            api = API()
            api.setUrl("http://salamatinfo.com/AdminApi/Contents/Add")
            api.addHeader("Content-Type", "application/json")
            api.request(body)
            if '1' == server('Test-Mode'):
                echo(json.dumps(dm.data(), ensure_ascii=True))
        except Exception as e:
            LOG_INFO(str(e) + " " + str(content))

sys.stdin.reconfigure(encoding='utf-8')
input = sys.stdin.read()
REQUEST_URI = server('REQUEST_URI')
if REQUEST_URI and REQUEST_URI[-1] == "/":
    REQUEST_URI = REQUEST_URI[:-1]
if server('REQUEST_METHOD') == 'POST' and server('CONTENT_TYPE') == "application/json" and REQUEST_URI == ROOT_PATH + TGB_KEY:
    try:
        addHeader('Contnent-Type', 'text/html')
        # LOG_INFO(input)
        content = json.loads(input, strict=False)
        # LOG_INFO(content)
        index(content)
    except Exception as e:
        LOG_INFO(str(e) + " " + input)

echo(REQUEST_URI)