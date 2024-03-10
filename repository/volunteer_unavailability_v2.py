import logging

from repository.unavailability_repository import *

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
    try:
        events = session.query(UnavailabilityTime).filter(
            UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1).all()
        session.expunge_all()
        return events
    except Exception as e:
        logging.error(e)
        return None