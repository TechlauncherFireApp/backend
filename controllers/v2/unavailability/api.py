from flask_restful import reqparse, Resource, marshal_with, inputs

from .response_models import volunteer_unavailability_time
from domain import UserType
from repository.volunteer_unavailability_v2 import EventRepository
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api
import logging

edit_parser = reqparse.RequestParser()
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)


class SpecificVolunteerUnavailabilityV2(Resource):
    event_repository: EventRepository

    def __init__(self, event_repository: EventRepository = EventRepository()):
        self.event_repository = event_repository

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def put(self, user_id, event_id):
        args = edit_parser.parse_args()
        success = self.event_repository.edit_event(user_id, event_id, **args)
        if success is True:
            return {"message": "Updated successfully"}, 200
        elif success is False:
            return {"message": "Event not found"}, 404
        else:
            return {"message": "Unexpected Error Occurred"}, 400

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def delete(self, user_id, event_id):
        # logging is used for easier debugging
        try:
            success = self.event_repository.remove_event(user_id, event_id)
            if success:
                logging.info(f"Soft deleted unavailability event {event_id} for user {user_id}.")
                return {"message": "Unavailability event removed successfully."}, 200
            else:
                logging.warning(
                    f"Attempted to remove non-existing or already removed event {event_id} for user {user_id}.")
                return {"message": "Unavailability event not found or already removed."}, 404
        except Exception as e:
            logging.error(f"Error during deletion of event {event_id} for user {user_id}: {str(e)}")
            return {"message": "Internal server error", "error": str(e)}, 500


class VolunteerUnavailabilityV2(Resource):
    event_repository: EventRepository

    def __init__(self, event_repository: EventRepository = EventRepository()):
        self.event_repository = event_repository

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def get(self, user_id):
        volunteer_unavailability_record = self.event_repository.get_event(user_id)
        if volunteer_unavailability_record is not None and volunteer_unavailability_record != []:
            return volunteer_unavailability_record
        elif volunteer_unavailability_record == []:
            return {"message": "No unavailability record found."}, 400
        else:
            return {"message": "Internal server error"}, 500

    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def post(self, user_id):
        try:
            args = edit_parser.parse_args()
            # Check if start time is earlier than end time.
            if args['start'] >= args['end']:
                return {"message": "Start time must be earlier than end time"}, 400  # HTTP 400 Bad Request

            overlapping_events = self.event_repository.check_overlapping_events(user_id, args['start'], args['end'],
                                                                                args['periodicity'])
            if overlapping_events:
                return {"message": "Time frames overlap with existing events",
                        "overlapping events": overlapping_events}, 400


            eventId = self.event_repository.create_event(
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


v2_api.add_resource(SpecificVolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability/<event_id>')

v2_api.add_resource(VolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability')
