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

    def update_shift_status(self, user_id, shift_id, new_status):
        """
            Updates the status of a volunteer's shift request in the database.

            Parameters:
            ----------
            user_id : int
                The ID of the user whose shift request status is to be updated.
            shift_id : int
                The ID of the shift request to be updated.
            new_status : str
            The new status to set for the shift request.
            Returns:
            -------
            bool
                Returns `True` if the status was successfully updated, or `False` if the update
                failed due to the shift request not being found or an error occurring during the update.
        """
        with session_scope() as session:
            try:
                # Fetch the shift based on user_id
                shift_request_volunteer = session.query(ShiftRequestVolunteer).filter_by(
                    user_id=user_id, request_id=shift_id).first()

                # If record exists, update the status
                if shift_request_volunteer:
                    shift_request_volunteer.status = new_status
                    shift_request_volunteer.last_update_datetime = datetime.now()
                    session.commit()
                    return True
                else:
                    logging.info(f"No shift request volunteer with user id {user_id} and shift {shift_id} not found")
                    return False
            except Exception as e:
                session.rollback()
                logging.error(f"Error updating shift request for user {user_id} and shift_id {shift_id}: {e}")
                return False
