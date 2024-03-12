from flask import jsonify
from flask_restful import reqparse, Resource, marshal_with, inputs

from .response_models import volunteer_unavailability_time
from domain import session_scope, UserType
from repository.volunteer_unavailability_v2 import EventRepository
from repository.unavailability_repository import *
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api

edit_parser = reqparse.RequestParser()
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)


class SpecificVolunteerUnavailabilityV2(Resource):

    def __init__(self, event_repository):
        self.event_repository = event_repository

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def put(self, user_id, event_id):
        args = edit_parser.parse_args()
        with session_scope() as session:
            event_repository = EventRepository(session)
            success = event_repository.edit_event(user_id, event_id, **args)
            # success = edit_event(session, user_id, event_id, **args)
            if success is True:
                return {"message": "Updated successfully"}, 200
            elif success is False:
                return {"message": "Event not found"}, 404
            else:
                return {"message": "Unexpected Error Occurred"}, 400

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def delete(self, user_id, event_id):
        with session_scope() as session:
            try:
                success = remove_event(session, user_id, event_id)
                if success:
                    # If the event is successfully removed, return HTTP 200 OK.
                    return {"message": "Unavailability event removed successfully."}, 200
                else:
                    # If the event does not exist or could not be removed, return HTTP 404 Not Found.
                    return {"message": "Unavailability event not found."}, 404
            except Exception as e:
                # HTTP 500 Internal Server Error
                return {"description": "Internal server error", "error": str(e)}, 500


class VolunteerUnavailabilityV2(Resource):

    def __init__(self, event_repository):
        self.event_repository = event_repository

    @requires_auth
    @marshal_with(volunteer_unavailability_time)
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def get(self, user_id):
        with session_scope() as session:
            event_repository = EventRepository(session)
            volunteer_unavailability_record = event_repository.get_event(user_id)
            # volunteer_unavailability_record = get_event(session, user_id)
            if volunteer_unavailability_record is not None:
                return volunteer_unavailability_record
            else:
                return {"message": "No unavailability record found."}, 400

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def post(self, user_id):
        try:
            args = edit_parser.parse_args()
            with session_scope() as session:
                eventId = create_event(
                    session,
                    user_id,
                    args['title'],
                    args['start'],
                    args['end'],
                    args['periodicity']
                )
                if eventId is not None:
                    return {"eventId": eventId}, 200  # HTTP 200 OK
                else:
                    return {"description": "Failed to create event"}, 400  # HTTP 400 Bad Request
        except Exception as e:
            return {"description": "Internal server error", "error": str(e)}, 500  # HTTP 500 Internal Server Error

with session_scope() as session:
    event_repository = EventRepository(session)
    v2_api.add_resource(SpecificVolunteerUnavailabilityV2, '/v2/volunteers/',
                        '/v2/volunteers/<user_id>/unavailability/<event_id>', resource_class_args=[event_repository])

    v2_api.add_resource(VolunteerUnavailabilityV2, '/v2/volunteers/',
                        '/v2/volunteers/<user_id>/unavailability', resource_class_args=[event_repository])
