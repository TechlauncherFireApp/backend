from flask import Blueprint, jsonify, make_response
from flask_restful import reqparse, Resource, Api

from domain import session_scope
from repository.unavailability_repository import remove_event
from services.jwk import requires_auth

# Parser setup for removing an unavailability event
remove_parser = reqparse.RequestParser()
remove_parser.add_argument('userId', type=int, required=True)
remove_parser.add_argument('eventId', type=int, required=True)

class RemoveUnavailabilityEventV2(Resource):
    @requires_auth
    def delete(self):
        args = remove_parser.parse_args()
        with session_scope() as session:
            try:
                success = remove_event(session, args['userId'], args['eventId'])
                if success:
                    # If the event is successfully removed, return HTTP 200 OK.
                    return make_response(jsonify({"message": "Unavailability event removed successfully."}), 200)
                else:
                    # If the event does not exist or could not be removed, return HTTP 404 Not Found.
                    return make_response(jsonify({"message": "Unavailability event not found."}), 404)
            except Exception as e:
                # For other exceptions, return HTTP 500 Internal Server Error.
                return make_response(jsonify({"message": "An error occurred while processing your request.", "error": str(e)}), 500)

# Blueprint setup for Flask application
remove_unavailability_event_bp = Blueprint('remove-unavailability-event', __name__)
api = Api(remove_unavailability_event_bp)
api.add_resource(RemoveUnavailabilityEventV2, '/remove-unavailability-event')
