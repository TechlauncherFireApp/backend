from flask import Blueprint, request, jsonify
from flask_restful import reqparse, Resource, fields, marshal_with, Api, inputs

from .response_models import volunteer_unavailability_time
from domain import session_scope, UserType
from repository.volunteer_unavailability_v2 import *
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api

edit_parser = reqparse.RequestParser()
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)


class SpecificVolunteerUnavailabilityV2(Resource):

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def put(self, user_id, event_id):
        args = edit_parser.parse_args()
        with session_scope() as session:
            success = edit_event(session, user_id, event_id, **args)
            if success is True:
                return {"message": "Updated successfully"}, 200
            elif success is False:
                return {"message": "Event not found"}, 404
            else:
                return {"message": "Unexpected Error Occurred"}, 400


class VolunteerUnavailabilityV2(Resource):

    @requires_auth
    @marshal_with(volunteer_unavailability_time)
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def get(self, user_id):
        with session_scope() as session:
            volunteer_unavailability_record = fetch_event(session, user_id)
            if volunteer_unavailability_record is not None:
                return volunteer_unavailability_record
            else:
                return jsonify({'userID': user_id, 'success': False}), 400


v2_api.add_resource(SpecificVolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability/<event_id>')

v2_api.add_resource(VolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability')
