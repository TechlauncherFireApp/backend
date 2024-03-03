from flask import Blueprint, request, jsonify
from flask_restful import reqparse, Resource, fields, marshal_with, Api, inputs
from domain import session_scope
from repository.unavailability_repository import *

from services.jwk import requires_auth

# Request parser for creating a new unavailability event
create_parser = reqparse.RequestParser()
create_parser.add_argument('userId', type=int, required=True)
create_parser.add_argument('title', type=str, required=True)
create_parser.add_argument('periodicity', type=int, required=True)
create_parser.add_argument('start', type=inputs.datetime_from_iso8601, required=True)
create_parser.add_argument('end', type=inputs.datetime_from_iso8601, required=True)


class CreateNewUnavailabilityEvent_v2(Resource):
    @requires_auth
    def post(self):
        """
        POST method for creating a new unavailability event.

        Expects JSON payload with keys:
        - userId (int): User ID associated with the event.
        - title (str): Title of the event.
        - periodicity (int): Periodicity of the event.
        - start (str): Start date and time in ISO8601 format.
        - end (str): End date and time in ISO8601 format.

        Returns a JSON response with eventId and success indicators.
        """
        try:
            args = create_parser.parse_args()
            with session_scope() as session:
                eventId = create_event(
                    session,
                    args['userId'],
                    args['title'],
                    args['start'],
                    args['end'],
                    args['periodicity']
                )
                response = {
                    "eventId": eventId,
                    "success": eventId is not None
                }
                return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e), "success": False})


volunteer_unavailabilities_bp = Blueprint('unavailabilities', __name__)
api = Api(volunteer_unavailabilities_bp, '/unavailabilities')
api.add_resource(CreateNewUnavailabilityEvent_v2, '/create')