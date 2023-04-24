import requests
import json
from FLOG import LOG_INFO
import base64

class API:
    url = ''
    headers = {
        "X-REQUESTED-WITH": "Data Mining Project",
        "USER-AGENT": "TGB DM PROG",
        "Authorization" : "Bearer "
    }
    timeout = 5 # SECOND

    content_type = None
    content = None

    def setUrl(self, url):
        self.url = url

    def addHeader(self, name, value):
        self.headers[name] = value

    def request(self, body = None, log_ok_response = False):
        try:
            if body == None:
                body = "[GET]"
                response = requests.get(self.url, headers = self.headers, timeout = self.timeout)
            else:
                if type(body) is list or type(body) is dict:
                    body = json.dumps(body)
                response = requests.post(self.url, headers = self.headers, timeout = self.timeout, json = str(body))
            # response.ok Returns True if status_code is less than 400, otherwise False
            if (response.status_code != 200 and response.ok == False or log_ok_response == True):
                LOG_INFO("[%d] %s-%s: (%s) %s" % (response.status_code, response.reason, response.text, self.url, str(body)))
            if 'Content-Type' in response.headers:
                self.content_type = response.headers['Content-Type']
            else:
                self.content_type = None
            if "application/octet-stream" in self.content_type:
                self.content = base64.b64encode(response.content).decode()
            elif "application/json" in self.content_type:
                self.content = response.json()
            else:
                self.content = None
                LOG_INFO("The response is invalid: (" + self.url + ") " + response.text)
            response.close()
        except Exception as ex:
            self.content = None
            LOG_INFO(str(ex) + ": (" + self.url + ")")