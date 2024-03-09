import json
import uuid

from flask import jsonify
from flask_restful import reqparse, Resource, marshal_with, inputs

from domain.entity import unavailability_time
from .response_models import volunteer_unavailability_time
from domain import session_scope, UserType
from repository.volunteer_unavailability_v2 import *
from repository.unavailability_repository import *
from services.jwk import requires_auth, is_user_or_has_role
from controllers.v2.v2_blueprint import v2_api

edit_parser = reqparse.RequestParser()
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)


class SpecificVolunteerUnavailabilityV2(Resource):

    # @requires_auth
    # @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def put(self, user_id, event_id):
        args = edit_parser.parse_args()
        with session_scope() as session:
            success = edit_event(session, user_id, event_id, **args)
            if success is True:
                return {"message": "Updated successfully"}, 200
            elif success is False:
                return {"message": "Event not found"}, 404
            else:
                return {"message": "Unexpected Error Occurred"}, 400

    # @requires_auth
    # @is_user_or_has_role(None, UserType.ROOT_ADMIN)
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

    # @requires_auth
    @marshal_with(volunteer_unavailability_time)
    # @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def get(self, user_id):
        with session_scope() as session:
            volunteer_unavailability_record = fetch_event(session, user_id)
            if volunteer_unavailability_record is not None:
                return volunteer_unavailability_record
            else:
                return jsonify({'userID': user_id, 'success': False}), 400

    # @requires_auth
    # @is_user_or_has_role(None, UserType.ROOT_ADMIN)
    def post(self, user_id):
        try:
            args = edit_parser.parse_args()
            # Check if start time is earlier than end time
            if args['start'] >= args['end']:
                return {"description": "Start time must be earlier than end time"}, 400  # HTTP 400 Bad Request

            with session_scope() as session:

                overlapping_events = session.query(UnavailabilityTime).filter(
                    UnavailabilityTime.userId == user_id,
                    UnavailabilityTime.start < args['end'],
                    UnavailabilityTime.end > args['start'],
                    UnavailabilityTime.periodicity == args['periodicity']
                ).all()

                if overlapping_events:
                    return {"description": "Time frames overlap with existing events"}, 400  # HTTP 400 Bad Request

                # duplicate_events = session.query(UnavailabilityTime).filter(UnavailabilityTime.userId == user_id,
                #                                                             UnavailabilityTime.title == args['title'],
                #                                                             UnavailabilityTime.start == args['start'],
                #                                                             UnavailabilityTime.end == args['end'],
                #                                                             UnavailabilityTime.periodicity == args[
                #                                                                 'periodicity']).first()
                # if duplicate_events:
                #     return {"message": "Duplicate unavailability event"}, 400


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


v2_api.add_resource(SpecificVolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability/<event_id>')

v2_api.add_resource(VolunteerUnavailabilityV2, '/v2/volunteers/',
                    '/v2/volunteers/<user_id>/unavailability')
