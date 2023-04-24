from flask import Flask, request, jsonify
from TGBOT import TelegramBot
from SIAPI import API
from FLOG import LOG_INFO
from DM import DataMining

app = Flask(__name__)

@app.route('/981e9f0ad23cfcb682f11d55718aefbd', methods=['POST'])
def index():
    content = request.json
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
            if '1' == request.headers.get('Test-Mode'):
                return jsonify(body)
        except Exception as e:
            LOG_INFO(str(e) + " " + str(content))
    return ''