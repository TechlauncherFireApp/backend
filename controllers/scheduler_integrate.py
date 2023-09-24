from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from services.optimiser.input_processing import get_input_A, get_input_R, get_input_P, get_input_V, get_input_Q
from services.jwk import requires_auth


scheduler_composite_api_bp = Blueprint('scheduler_composite_api', __name__)
api = Api(scheduler_composite_api_bp)


class SchedulerCompositeAPI(Resource):

    @requires_auth
    def post(self):
        try:
            data = request.json
            request_types = data.get('request_types', [])
            request_id = data.get('requestID')
            other_params = data.get('other_params')

            response_data = {}

            for request_type in request_types:
                if request_type == 'GetInputA':
                    response_data['GetInputA'] = get_input_A(request_id, other_params)
                elif request_type == 'GetInputR':
                    response_data['GetInputR'] = get_input_R(request_id, other_params)
                elif request_type == 'GetInputP':
                    response_data['GetInputP'] = get_input_P(request_id, other_params)
                elif request_type == 'GetInputV':
                    response_data['GetInputV'] = get_input_V(request_id, other_params)
                elif request_type == 'GetInputQ':
                    response_data['GetInputQ'] = get_input_Q(request_id, other_params)
                else:
                    response_data[request_type] = "Invalid request_type"

            return jsonify(response_data), 200
        except Exception as e:
            return {'error': str(e)}, 400


api.add_resource(SchedulerCompositeAPI, '/scheduler_composite_api')


