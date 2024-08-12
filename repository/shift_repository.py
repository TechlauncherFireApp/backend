import logging

from flask import jsonify

from datetime import datetime, timezone
from exception import EventNotFoundError, InvalidArgumentError
from domain import Shift, session_scope

class ShiftRepository:

    def __init__(self):
        pass

    def get_shift(self, userId):
        """
        get all the shift events of the given user
        :param userId: Integer, user id, who want to query the events
        """
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the shift that is end in the future
                shifts = session.query(Shift).filter(
                    Shift.userId == userId,
                    Shift.end > now).all()
                if shifts:
                    shift_records = []
                    for shift in shifts:
                        # write shift information into list
                        shift_record = {
                            "eventId": shift.eventId,
                            "userId": shift.userId,
                            "title": shift.title,
                            "startTime": shift.start.isoformat(),
                            "endTime": shift.end.isoformat(),
                            "role": shift.role
                        }
                        shift_records.append(shift_record)
                    return shift_records
                else:
                    return []
            except Exception as e:
                logging.error(e)
                return None