from flask_restful import Resource, marshal_with, reqparse

from controllers.v2 import volunteer_personal_info
from controllers.v2.v2_blueprint import v2_api
from domain import session_scope
from repository.volunteer_repository import get_volunteer

parser = reqparse.RequestParser()
parser.add_argument('user_id', action='store', type=str)


class VolunteerInfo(Resource):

    @marshal_with(volunteer_personal_info)
    def get(self):
        args = parser.parse_args()
        if args["volunteerID"] is None:
            return
        with session_scope() as session:
            return get_volunteer(session, args["volunteerID"])


v2_api.add_resource(VolunteerInfo, '/info/volunteer')
