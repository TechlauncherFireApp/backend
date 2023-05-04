from flask_restful import Resource, marshal_with

from controllers.v2.v2_blueprint import v2_bp, v2_api
from controllers.v2.volunteers.response_models import volunteer_listing_model, volunteer_personal_info
from domain import session_scope, UserType
from repository.volunteer_repository import list_volunteers, get_volunteer_info
from services.jwk import requires_auth, has_role


class VolunteerV2(Resource):

    @requires_auth
    @has_role(UserType.ROOT_ADMIN)
    def get(self, user_id=None):
        if user_id:
            @marshal_with(volunteer_personal_info)
            # TODO: Allow the user to view their personal detail
            def get_personal_info():
                with session_scope() as session:
                    return get_volunteer_info(session, user_id)
            return get_personal_info()
        else:
            @marshal_with(volunteer_listing_model)
            def list_all_volunteers():
                with session_scope() as session:
                    return list_volunteers(session)
            return list_all_volunteers()


v2_api.add_resource(VolunteerV2, '/v2/volunteers/', '/v2/volunteers/<user_id>')
