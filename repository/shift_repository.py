import logging

from flask import jsonify

from datetime import datetime, timezone
from exception import EventNotFoundError, InvalidArgumentError
from domain import session_scope, ShiftRequestVolunteer, ShiftRequest


class ShiftRepository:

    def __init__(self):
        pass

    def get_shift(self, userId):
        """
            Retrieves all shift events for a given user that have not ended yet.

            :param userId: ID of the user whose shifts are being queried.
            :return: A list of shift records or an empty list if none found.
        """
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the shift that is end in the future
                shifts = session.query(ShiftRequestVolunteer).join(ShiftRequest).filter(
                        ShiftRequestVolunteer.user_id == userId,
                        ShiftRequest.endTime > now).all()
                # check if there's some results
                if not shifts:
                    logging.info(f"No active shifts found for user {userId}")
                    return []
                shift_records = []
                # write shift information into list
                for shift in shifts:
                    shift_record = {
                        "shiftId": shift.request_id,
                        "status": shift.status,
                        "title": shift.shift_request.title,
                        "start": shift.shift_request.startTime.isoformat(),
                        "end": shift.shift_request.endTime.isoformat(),
                    }
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
                return []