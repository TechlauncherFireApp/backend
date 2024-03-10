import logging

from flask import jsonify

from repository.unavailability_repository import *

from domain import UnavailabilityTime
from datetime import timezone


def edit_event(session, userId, eventId, title=None, start=None, end=None, periodicity=None):
    try:
        event = session.query(UnavailabilityTime).filter(UnavailabilityTime.eventId == eventId,
                                                         UnavailabilityTime.userId == userId).first()
        if event is None:
            return False
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
        return None

def get_event(session, userId):
    """
    get all the non-availability events of the given user
    :param session: session
    :param userId: Integer, user id, who want to query the events
    """
    try:
        events = session.query(UnavailabilityTime).filter(
            UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1).all()
        session.expunge_all()
        '''for event in events:
            print(f"Debug: Event ID: {event.eventId}, Start: {event.start}, End: {event.end}")
        if events is not None:
            event_records = [{
                "eventId": event.eventId,
                "userId": event.userId,
                "title": event.title,
                "startTime": event.start.astimezone(timezone.utc).isoformat() if event.start else None,
                "endTime": event.end.astimezone(timezone.utc).isoformat() if event.end else None,
                "periodicity": event.periodicity
            } for event in events]
            print(event_records)
            return event_records
        else:
            return None'''
        return events
    except Exception as e:
        logging.error(e)
        return None