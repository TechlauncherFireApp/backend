from flask_restful import reqparse, Resource, marshal_with, inputs

from .response_models import volunteer_unavailability_time
from domain import UserType, session_scope
from repository.volunteer_unavailability_v2 import EventRepository
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api
import logging
from exception import EventNotFoundError, InvalidArgumentError
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
    def put(self, user_id, event_id):
        @is_user_or_has_role(user_id, UserType.ROOT_ADMIN)
        def edit_unavailability():
            with session_scope() as session:
                args = edit_parser.parse_args()
                return self.event_repository.edit_event(session, user_id, event_id, **args)
        try:
            edit_unavailability()
            return {"message": "Updated successfully"}, 200
        except InvalidArgumentError as argumentException:
            logging.warning(argumentException)
            return {"message": "Invalid argument from the payload"}, 400
        except EventNotFoundError as notFoundError:
            logging.warning(notFoundError)
            return {"message": f"Event {event_id} can not be found"}, 404
        except Exception as ex:
            logging.error(ex)
            return {"message": "Unexpected error happened within the database"}, 500


    @requires_auth
    @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def delete(self, user_id, event_id):
        try:
            success = self.event_repository.remove_event(user_id, event_id)
            if success:
                # If the event is successfully removed, return HTTP 200 OK.
                return {"message": "Unavailability event removed successfully."}, 200
            else:
                # If the event does not exist or could not be removed, return HTTP 404 Not Found.
                return {"message": "Unavailability event not found."}, 404
        except Exception as e:
            # HTTP 500 Internal Server Error
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
