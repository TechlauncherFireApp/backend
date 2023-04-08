from flask_restful import Resource, marshal_with, reqparse

from controllers.v2 import volunteer_personal_info
from controllers.v2.v2_blueprint import v2_info_api
from domain import session_scope
from repository.volunteer_repository import get_volunteer_info

parser = reqparse.RequestParser()
parser.add_argument('ID', action='store', type=str)


class VolunteerInfo(Resource):

    @marshal_with(volunteer_personal_info)
    def get(self):
        args = parser.parse_args()
        if args["ID"] is None:
            return
        with session_scope() as session:
            return get_volunteer_info(session, args["ID"])


v2_info_api.add_resource(VolunteerInfo, '/info/volunteer/info')
