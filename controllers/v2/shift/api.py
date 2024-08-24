from flask_restful import reqparse, Resource, marshal_with, inputs

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
parser.add_argument('roles', type=list, location='json', required=True, help="Roles cannot be blank!")


class VolunteerShiftV2(Resource):
    shift_repository: ShiftRepository

    def __init__(self, shift_repository: ShiftRepository = ShiftRepository()):
        self.shift_repository = shift_repository

    #@requires_auth
    #@is_user_or_has_role(None, UserType.ROOT_ADMIN)
    #@marshal_with(shift)
    def get(self, user_id):
        try:
            shifts = self.shift_repository.get_shift(user_id)
            if shifts:
                return shifts, 200
            else:
                return {"message": "No shift record found."}, 400
        except Exception as e:
            logging.error(f"Error retrieving shifts for user {user_id}: {e}")
            return {"message": "Internal server error"}, 500




v2_api.add_resource(VolunteerShiftV2,'/v2/volunteers/<user_id>/shift')
