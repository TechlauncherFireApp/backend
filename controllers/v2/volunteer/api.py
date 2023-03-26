from flask_restful import Resource, marshal_with

from controllers.v2.v2_blueprint import v2_api
from controllers.v2.volunteer.response_models import volunteer_listing_model
from domain import session_scope
from repository.volunteer_repository import list_volunteers
from services.jwk import requires_auth


@v2_api.route('/volunteer/all')
class VolunteerV2(Resource):

    @requires_auth
    @marshal_with(volunteer_listing_model)
    def get(self):
        with session_scope() as session:
            return list_volunteers(session)
