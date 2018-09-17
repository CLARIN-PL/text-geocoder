import datetime
import uuid

from flask import jsonify, request

from text_geocoder.api.v1 import V1FlaskView
from text_geocoder.api.v1.ccl_parser import extract_locations
from text_geocoder.api.v1.geocoder import find_latitude_and_longitude
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

        result_file_path = process(document__id, data['text'])

        locations = extract_locations(result_file_path)

        locations = find_latitude_and_longitude(locations)

        response = {
            'id': document__id,
            'text': data['text'],
            'created_on': datetime.datetime.now(),
            'locations': locations
        }

        return jsonify(response), 200
