import json
import os
import time
from urllib.request import urlopen, Request

url = "https://ws.clarin-pl.eu/nlprest2/base"


def upload(text):
    file_id = urlopen(Request(url + '/upload/',
                              text.encode('utf-8'),
                              {'Content-Type': 'binary/octet-stream'})).read().decode()
    return file_id


def start_task(doc):
    json_doc = json.dumps(doc).encode('utf-8')

    task_id = urlopen(Request(url + '/startTask/',
                              json_doc,
                              {'Content-Type': 'application/json'})).read().decode()

    time.sleep(0.2)

    resp = urlopen(Request(url + '/getStatus/' + task_id))

    data = json.load(resp)

    while data["status"] == "QUEUE" or data["status"] == "PROCESSING":
        time.sleep(0.5)
        resp = urlopen(Request(url + '/getStatus/' + task_id))
        data = json.load(resp)

    if data["status"] == "ERROR":
        print("Error " + data["value"])
        return None, data['value']

    return data["value"], None


async def process(document_id, text, model, out='downloads/'):
    """
    Processes text by using clarin services
    :param out: path to output directory
    :param model: liner2 model name
    :param document_id: uuid
    :param text: string
    :return: result file path
    """

    file_id = upload(text)
    data = {
        'lpmn': 'any2txt|wcrft2({"morfeusz2":false})|liner2({"model":"'+model+'"})',
        'user': 'geocoder',
        'file': file_id
    }

    response, errors = start_task(data)

    if errors is not None:
        return {'errors': errors}

    if response is not None:
        response = response[0]["fileID"]
        content = urlopen(Request(url + '/download' + response)).read().decode()
        with open(out + os.path.basename(document_id) + '.' + model, "w") as outfile:
            outfile.write(content)

    return {'model': model,
            'path': out + os.path.basename(document_id) + '.' + model,
            'errors': None}
