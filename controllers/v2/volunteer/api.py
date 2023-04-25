from flask_restful import Resource, marshal_with, reqparse

from controllers.v2.v2_blueprint import v2_bp, v2_api
from controllers.v2.volunteer.response_models import volunteer_personal_info
from domain import session_scope, UserType
from repository.volunteer_repository import get_volunteer_info
from services.jwk import has_role, requires_auth

parser = reqparse.RequestParser()
parser.add_argument('user_id', action='store', type=str)


class VolunteerInfo(Resource):
    """
    Get the personal detail for a specific volunteer
    This information should only be visible for the supervisor and volunteer themselves
    """

    @marshal_with(volunteer_personal_info)
    @has_role(UserType.ROOT_ADMIN)
    @requires_auth
    def get(self):
        args = parser.parse_args()
        if args["user_id"] is None:
            return
        with session_scope() as session:
            return get_volunteer_info(session, args["user_id"])


v2_api.add_resource(VolunteerInfo, '/v2/volunteer')
