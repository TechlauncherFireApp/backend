from flask_restful import reqparse, Resource, marshal_with, inputs, marshal
from .response_models import shift
from domain import UserType
from repository.shift_repository import ShiftRepository
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api
import logging


parser = reqparse.RequestParser()
parser.add_argument('title', type=str)
parser.add_argument('start', type=inputs.datetime_from_iso8601, required=True, help="Start time cannot be blank!")
parser.add_argument('end', type=inputs.datetime_from_iso8601, required=True, help="End time cannot be blank!")
parser.add_argument('vehicle_type', type=int, required=True, help="Vehicle type cannot be blank!")
parser_modify_status = reqparse.RequestParser()
parser_modify_status.add_argument('status', type=str, location='json', required=True, help="Status cannot be blank!")


class VolunteerShiftV2(Resource):
    shift_repository: ShiftRepository

    def __init__(self, shift_repository: ShiftRepository = ShiftRepository()):
        self.shift_repository = shift_repository

    def post(self, user_id):
        try:
            args = parser.parse_args()
            title = args['title']
            start = args['start']
            end = args['end']
            vehicle_type = args['vehicle_type']
            new_shift_id = self.shift_repository.post_shift_request(user_id, title, start, end, vehicle_type)
            if new_shift_id:
                return {"shift_id:", new_shift_id}, 200
            else:
                return {"message": "Failed to create shift."}, 400
        except Exception as e:
            logging.error(f"Error creating new shift request: {e}")
            return {"message": "Internal server error"}, 500


    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def get(self, user_id):
        try:
            shifts = self.shift_repository.get_shift(user_id)
            if shifts:
                return marshal(shifts, shift), 200
            else:
                return {"message": "No shift record found."}, 400
        except Exception as e:
            logging.error(f"Error retrieving shifts for user {user_id}: {e}")
            return {"message": "Internal server error"}, 500


    def put(self, user_id, shift_id):
        args = parser_modify_status.parse_args()
        status = args["status"]
        try:
            success = self.shift_repository.update_shift_status(user_id, shift_id, status)
            if success:
                return {"message": "Status updated successfully"}, 200
            else:
                return {"message": "No user or shift record is found, status not updated."}, 400
        except Exception as e:
            logging.error(f"Error updating shifts for user {user_id}: {e}")
            return {"message": "Internal server error"}, 500

v2_api.add_resource(VolunteerShiftV2,'/v2/volunteers/<user_id>/shift','/v2/volunteers/<user_id>/shift/<shift_id>')
