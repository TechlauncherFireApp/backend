from flask import Blueprint, jsonify
from flask_restful import reqparse, Resource, Api

from domain import session_scope
from repository.unavailability_repository import remove_event
from services.jwk import requires_auth

# Parser for removing an unavailability event
remove_parser = reqparse.RequestParser()
remove_parser.add_argument('userId', type=int, required=True)
remove_parser.add_argument('eventId', type=int, required=True)


class RemoveUnavailabilityEventV2(Resource):
    @requires_auth
    def delete(self):  # Using the DELETE method to indicate resource removal
        args = remove_parser.parse_args()
        with session_scope() as session:
            success = remove_event(session, args['userId'], args['eventId'])
            return jsonify({"success": success})


# Blueprint setup for Flask application
remove_unavailability_event_bp = Blueprint('remove_unavailability_event', __name__)
api = Api(remove_unavailability_event_bp)
api.add_resource(RemoveUnavailabilityEventV2, '/removeUnavailableEventV2')
