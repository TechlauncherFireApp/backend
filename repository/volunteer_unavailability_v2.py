import logging

from flask import jsonify

from repository.unavailability_repository import *
from datetime import datetime

from domain import UnavailabilityTime


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
    now = datetime.now()
    try:
        # only show the unavailability time that is end in the future
        events = session.query(UnavailabilityTime).filter(
            UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1, UnavailabilityTime.end > now).all()
        session.expunge_all()
        event_records = []
        for event in events:
            # if the start time is earlier than now, then show from now to the end time
            start_time = max(event.start, now)
            event_record = {
                "eventId": event.eventId,
                "userId": event.userId,
                "title": event.title,
                "startTime": start_time.isoformat(),
                "endTime": event.end.isoformat(),
                "periodicity": event.periodicity
            }
            event_records.append(event_record)

        return jsonify(event_records)
    except Exception as e:
        logging.error(e)
        return None