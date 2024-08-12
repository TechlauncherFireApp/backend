from flask_restful import reqparse, Resource, marshal_with, inputs

from .response_models import shift
from domain import UserType, session_scope
from repository.shift_repository import ShiftRepository
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api
import logging
from exception import EventNotFoundError, InvalidArgumentError

class ShowShift(Resource):
    shift_repository: ShiftRepository

    def __init__(self, shift_repository: ShiftRepository = ShiftRepository()):
        self.shift_repository = shift_repository

    #@requires_auth
    #@is_user_or_has_role(None, UserType.ROOT_ADMIN)
    @marshal_with(shift)
    def get(self, user_id):
        shift = self.shift_repository.get_shift(user_id)
        if shift is not None and shift != []:
            return shift
        elif shift == []:
            return {"message": "No shift record found."}, 400
        else:
            return {"message": "Internal server error"}, 500

v2_api.add_resource(ShowShift, '/v2/volunteers/<user_id>/shift')