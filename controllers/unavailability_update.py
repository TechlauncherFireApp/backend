from flask import blueprint, request, jsonify

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

        Returns a response with HTTP codes corresponding to status of operation.
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
                if eventId is not None:
                    return {"eventId": eventId}, 200  # HTTP 200 OK
                else:
                    return {"error": "Failed to create event", "success": False}, 400  # HTTP 400 Bad Request
        except Exception as e:
            return {"error": str(e), "success": False}, 500  # HTTP 500 Internal Server Error


unavailability_v2 = blueprint('v2', __name__)
unavailability_v2_api = Api(unavailability_v2)
unavailability_v2_api.add_resource('volunteer/<user_id>/unavailability')
