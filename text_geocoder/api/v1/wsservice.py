import json
import os
import time
from urllib import parse
from urllib.request import urlopen, Request

url = "https://ws.clarin-pl.eu/nlprest2/base"


def upload(text):
        return urlopen(Request(url+'/upload/',
                               text.encode('utf-8'),
                               {'Content-Type': 'binary/octet-stream'})).read().decode()


def start_task(doc):
    json_doc = parse.urlencode(json.dumps(doc))

    task_id = urlopen(Request(url + '/startTask/',
                              json_doc.encode('utf-8'),
                              {'Content-Type': 'application/json'})).read()

    time.sleep(0.2)

    resp = urlopen(Request(url + '/getStatus/' + task_id))

    data = json.load(resp)

    while data["status"] == "QUEUE" or data["status"] == "PROCESSING":
        time.sleep(0.5)
        resp = urlopen(Request(url + '/getStatus/' + task_id))
        data = json.load(resp)

    if data["status"] == "ERROR":
        print("Error " + data["value"])
        return None

    return data["value"]


def process(document_id, text):

    file_id = upload(text)
    data = {
        'lpmn': 'any2txt|wcrft2({"morfeusz2":false})|liner2({"model":"5nam"})|serel',
        'user': 'geocoder',
        'file': file_id
    }

    response = start_task(data)

    if response is not None:
        response = response[0]["fileID"]
        content = urlopen(Request(url + '/download' + response)).read()
        with open('downloads/' + os.path.basename(document_id) + '.ccl', "w") as outfile:
            outfile.write(content)
