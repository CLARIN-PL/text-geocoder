import datetime
import uuid

from flask import jsonify, request

from text_geocoder.api.v1 import V1FlaskView
from text_geocoder.api.v1.schemas import document_schema
from text_geocoder.api.v1.ws_clarin import process


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

        process(document__id, data['text'])

        response = {
            'id': document__id,
            'text': data['text'],
            'created_on': datetime.datetime.now()
        }

        return jsonify(response), 200
