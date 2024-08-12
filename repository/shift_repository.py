import logging

from flask import jsonify

from datetime import datetime, timezone
from exception import EventNotFoundError, InvalidArgumentError
from domain import Shift, InputShift, session_scope


class ShiftRepository:

    def __init__(self):
        pass

    def get_shift(self, userId):
        """
        Retrieves all shift events for a given user that have not ended yet.

        :param user_id: ID of the user whose shifts are being queried.
        :return: A list of shift records or an empty list if none found.
        """
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the shift that is end in the future
                shifts = session.query(Shift).filter(
                    Shift.userId == userId,
                    Shift.end > now).all()
                shift_records = []
                for shift in shifts:
                    # write shift information into list
                    shift_record = {
                        "shiftId": shift.shiftId,
                        "userId": shift.userId,
                        "title": shift.title,
                        "startTime": shift.start.isoformat(),
                        "endTime": shift.end.isoformat(),
                        "role": shift.role
                    }
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
                return []

    def create_shift(self, title, start, end, roles):
        """
        Create a new shift for the specified user.

        :param user_id: ID of the user the shift is for.
        :param title: Title of the shift.
        :param start: Start time of the shift.
        :param end: End time of the shift.
        :param roles: List of roles associated with the shift.
        :return: The created shift or an error message.
        """
        # Verify that end time is after start time
        if end <= start:
            raise ValueError("End time must be after start time.")

        with session_scope() as session:
            try:
                new_shift = InputShift(
                    title=title,
                    start=start,
                    end=end,
                    roles=roles
                )
                session.add(new_shift)
                session.commit()
                return new_shift
            except Exception as e:
                logging.error(f"Error creating shift: {e}")
                raise