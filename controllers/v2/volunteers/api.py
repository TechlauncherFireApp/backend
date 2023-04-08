from flask_restful import Resource, marshal_with, reqparse

from controllers.v2.v2_blueprint import v2_api
from controllers.v2.volunteer.response_models import volunteer_listing_model
from domain import session_scope
from repository.volunteer_repository import get_volunteer

parser = reqparse.RequestParser()
parser.add_argument('volunteerID', action='store', type=str)


class VolunteerInfo(Resource):

    @marshal_with(volunteer_listing_model)
    def get(self):
        args = parser.parse_args()
        if args["volunteerID"] is not None:
            with session_scope() as session:
                return get_volunteer(session, args["volunteerID"])


v2_api.add_resource(VolunteerInfo, '/v2/volunteer/info')
