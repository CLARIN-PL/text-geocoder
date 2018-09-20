import asyncio
import datetime
import uuid

from flask import jsonify, request

from text_geocoder.api.v1 import V1FlaskView
from text_geocoder.api.v1.ccl_parser import extract_locations
from text_geocoder.api.v1.geocoder import find_latitude_and_longitude
from text_geocoder.api.v1.schemas import document_schema
from text_geocoder.api.v1.ws_clarin import process
from text_geocoder.api.v1.model_comparator import compare_models


class DocumentView(V1FlaskView):

    def post(self):

        json_data = request.get_json()

        if not json_data:
            response = jsonify({'error': 'Invalid input'})

            return response, 400

        data, errors = document_schema.load(json_data)

        if errors:
            response = {
                'error': errors
            }

            return jsonify(response), 422

        document__id = str(uuid.uuid4())

        loop = asyncio.get_event_loop()

        try:
            finished_tasks = loop.run_until_complete(execute_tasks(document__id, data['text']))
            locations = dict()

            for task in finished_tasks:
                key = task.result()['model']
                path = task.result()['path']
                locations[key] = extract_locations(path, key)

            loc = compare_models(locations)

            location = find_latitude_and_longitude(loc)

            response = {
                'id': document__id,
                'text': data['text'],
                'created_on': datetime.datetime.now(),
                'locations': location
            }

            return jsonify(response), 200

        except WebServiceError:

            response = {
                'error': errors
            }
            return jsonify(response), 400

        finally:
            loop.close()


async def execute_tasks(document__id, text):

    # n82 — rozpoznaje 82 kategorii nazw własnych
    # top9 — rozpoznaje 9 kategorii nazw własnych
    # 5nam - rozpoznaje 5 kategorii nazw własnych (imiona, nazwiska, nazwy państwa, miast i ulic)

    tasks = [
        run_process_task(document__id, text, 'n82'),
        run_process_task(document__id, text, 'top9')
    ]

    while len(tasks):
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task.result()['errors']:
                raise WebServiceError(task.result()['errors'])
    return done


async def run_process_task(document__id, text, model):
    result = await process(document__id, text, model)
    return result


class WebServiceError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
