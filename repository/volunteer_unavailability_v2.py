import logging

from flask import jsonify

from datetime import datetime

from domain import UnavailabilityTime, session_scope



class EventRepository:
    def __init__(self):
        pass
    def edit_event(self, userId, eventId, title=None, start=None, end=None, periodicity=None):
        with session_scope() as session:
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

    def get_event(self, userId):
        """
        get all the non-availability events of the given user
        :param session: session
        :param userId: Integer, user id, who want to query the events
        """
        # now = datetime.now().replace(microsecond=0)
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the unavailability time that is end in the future
                events = session.query(UnavailabilityTime).filter(
                    UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1, UnavailabilityTime.end > now).all()
                if events:
                    event_records = []
                    for event in events:
                        # if the start time is earlier than now, then show from now to the end time
                        # start_time = max(event.start, now)
                        event_record = {
                            "eventId": event.eventId,
                            "userId": event.userId,
                            "title": event.title,
                            "startTime": event.start.isoformat(),
                            "endTime": event.end.isoformat(),
                            "periodicity": event.periodicity
                        }
                        event_records.append(event_record)
                    return event_records
                else:
                    return []
            except Exception as e:
                logging.error(e)
                return None

    # copy from repository.unavailability_repository.py
    def create_event(self, userId, title, startTime, endTime, periodicity):
        """
        Function to create an event
        :param session: session
        :param userId: Integer, user id
        :param title: String, reason why unavailable
        :param startTime: DateTime, from what time is unavailable
        :param endTime: DateTime, to what time is unavailable
        :param periodicity: Integer, Daily = 1, Weekly = 2, One-Off = 3
        """
        event = UnavailabilityTime(userId=userId, title=title, start=startTime, end=endTime,
                                       periodicity=periodicity)
        with session_scope() as session:
            session.add(event)
            # session.expunge(question)
            session.flush()
            return event.eventId

    # copy from repository.unavailability_repository.py
    def remove_event(self, userId, eventId):
        """
        Function to remove an event
        :param session: session
        :param userId: Integer, user id, who want to remove an event
        :param eventId: Integer, event id want to remove
        :return: True: remove successful
                 False: remove failed
        """
        with session_scope() as session:
            existing = session.query(UnavailabilityTime).filter(UnavailabilityTime.userId == userId,
                                                                UnavailabilityTime.eventId == eventId).first()
            if existing is not None and existing.status is True:
                existing.status = False
                return True
            return False

    # copy from post function in api.py written by Steven
    def check_overlapping_events(self, userId, startTime, endTime, periodicity):
        with session_scope() as session:
            # checks if new time frame overlaps with any existing in the database for specific userId
            overlapping_events = session.query(UnavailabilityTime).filter(
                UnavailabilityTime.userId == userId,
                UnavailabilityTime.start < endTime,
                UnavailabilityTime.end > startTime,
                UnavailabilityTime.periodicity == periodicity
            ).all()
            # Convert overlapping events to a list of dictionaries
            overlapping_details = []
            for event in overlapping_events:
                overlapping_details.append({
                    "eventId": event.eventId,
                    # Add any other attributes you need
                })
        return overlapping_details