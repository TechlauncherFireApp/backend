
from flask import Blueprint, request, jsonify
from flask_restful import reqparse, Resource, fields, marshal_with, Api, inputs

from domain import session_scope
from repository.volunteer_unavailability_v2 import *


edit_parser = reqparse.RequestParser()
edit_parser.add_argument("userId", type=int, required=True)
edit_parser.add_argument("eventId", type=int, required=True)
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)

class volunteer_unavailability(Resource):
    def patch(self):
        args = edit_parser.parse_args()
        with session_scope() as session:
            success = edit_event(session, **args)
            if success is True:
                return {"message": "Updated successfully"}, 200
            elif success is False:
                return {"message": "Event not found"}, 404
            else:
                return {"message": "Unexpected Error Occurred"}, 400

volunteer_unavailability_v2_bp = Blueprint('volunteer_unavailability-v2', __name__)
api = Api(volunteer_unavailability_v2_bp, "/event")
api.add_resource(volunteer_unavailability, "/unavailability")
