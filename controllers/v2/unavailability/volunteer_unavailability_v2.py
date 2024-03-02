import logging

from flask import Blueprint, request, jsonify
from flask_restful import reqparse, Resource, fields, marshal_with, Api, inputs

import domain.base
from domain import session_scope
from repository.unavailability_repository import *

from services.jwk import requires_auth

edit_parser = reqparse.RequestParser()
edit_parser.add_argument("userId", type=int, required=True)
edit_parser.add_argument("eventId", type=int, required=True)
edit_parser.add_argument("title", type=str)
edit_parser.add_argument("start", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("end", type=inputs.datetime_from_iso8601)
edit_parser.add_argument("periodicity", type=int)


class volunteer_unavailability(Resource):
    def patch(self):
        args = edit_parser.parse_args()
        with session_scope() as session:
            success = edit_event(session, **args)
            if success:
                return jsonify({"success": True, "message": "updated successfully"})
            else:
                return jsonify({"success": False, "message": "Failed to update"})


def edit_event(session, userId, eventId, title=None, start=None, end=None, periodicity=None):
    try:
        event = session.query(UnavailabilityTime).filter(UnavailabilityTime.eventId == eventId,
                                                         UnavailabilityTime.userId == userId).first()
        if title is not None:
            event.title = title
        if start is not None:
            event.start = start
        if end is not None:
            event.end = end
        if end is not None:
            event.periodicity = periodicity
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logging.error(e)
        return False


volunteer_unavailability_v2_bp = Blueprint('volunteer_unavailability_v2', __name__)
api = Api(volunteer_unavailability_v2_bp, "/unavailability_v2")
api.add_resource(volunteer_unavailability, "/editUnavailableEvent")
