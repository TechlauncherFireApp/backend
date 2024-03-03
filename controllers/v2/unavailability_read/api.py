from flask import jsonify
from flask_restful import reqparse, Resource, marshal_with

from controllers.v2.v2_blueprint import v2_api
from controllers.v2.unavailability_read.response_models import volunteer_unavailability_time
from services.jwk import requires_auth
from domain import session_scope
from repository.unavailability_repository import fetch_event

#read_parser = reqparse.RequestParser()
#read_parser.add_argument('userID', required = True, type = int)

# This class is to retrieve all unavailability records of a volunteer from the database
class ReadUnavailability(Resource):
    @requires_auth
    @marshal_with(volunteer_unavailability_time)
    def get(self,user_id):
        with session_scope() as session:
            #userid = read_parser.parse_args()['userID']
            volunteer_unavailability_record = fetch_event(session, user_id)
            if volunteer_unavailability_record != None:
                return volunteer_unavailability_record
            else:
                # If this volunteer has no unavailablility record, return a 400 response.
                return jsonify({'userID': user_id, 'success': False}), 400

v2_api.add_resource(ReadUnavailability, '/v2/unavailability/<int:user_id>')