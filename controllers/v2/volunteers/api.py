from flask_restful import Resource, marshal_with

from controllers.v2.v2_blueprint import v2_bp, v2_api
from controllers.v2.volunteers.response_models import volunteer_listing_model
from domain import session_scope
from repository.volunteer_repository import list_volunteers
from services.jwk import requires_auth


class VolunteerV2(Resource):

    @requires_auth
    @marshal_with(volunteer_listing_model)
    def get(self, user_id=None):
        if user_id:
            print("Getting information for individual user with id", user_id)
            # implement functionality for retrieving one user's details here
        else:
            with session_scope() as session:
                return list_volunteers(session)


v2_api.add_resource(VolunteerV2, '/v2/volunteers/', '/v2/volunteers/<user_id>')
