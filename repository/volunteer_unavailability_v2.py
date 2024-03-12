import logging

from flask import jsonify

from datetime import datetime

from domain import UnavailabilityTime


class EventRepository:
    def __init__(self, session):
        self.session = session

    def edit_event(self, userId, eventId, title=None, start=None, end=None, periodicity=None):
        try:
            event = self.session.query(UnavailabilityTime).filter(UnavailabilityTime.eventId == eventId,
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
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(e)
            return None

    def get_event(self, userId):
        """
        get all the non-availability events of the given user
        :param session: session
        :param userId: Integer, user id, who want to query the events
        """
        now = datetime.now()
        try:
            # only show the unavailability time that is end in the future
            events = self.session.query(UnavailabilityTime).filter(
                UnavailabilityTime.userId == userId, UnavailabilityTime.status == 1, UnavailabilityTime.end > now).all()
            if events:
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
            else:
                return None
        except Exception as e:
            logging.error(e)
            return None