import logging
from typing import List

from dataclasses import asdict
from flask import jsonify

from datetime import datetime, timezone

from exception import EventNotFoundError, InvalidArgumentError
from domain import session_scope, ShiftRequestVolunteer, ShiftRequest, ShiftRecord, UnavailabilityTime, ShiftVolunteerStatus
from exception.client_exception import ConflictError


class ShiftRepository:

    def __init__(self):
        pass

    def get_shift(self, userId) -> List[ShiftRecord]:
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
                    shift_record = ShiftRecord(
                        shiftId=shift.request_id,
                        status=shift.status.value,
                        title=shift.shift_request.title,
                        start=shift.shift_request.startTime,
                        end=shift.shift_request.endTime)
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
                return []

    def update_shift_status(self, user_id, shift_id, new_status: ShiftVolunteerStatus):
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
                    # check for conflict
                    is_conflict = self.check_conflict_shifts(session, shift_request_volunteer)
                    if is_conflict and new_status == ShiftVolunteerStatus.CONFIRMED:
                        # Raise the ConflictError if there's a conflict
                        raise ConflictError(f"Shift {shift_id} conflicts with other confirmed shifts.")
                    # update status
                    shift_request_volunteer.status = new_status
                    shift_request_volunteer.last_update_datetime = datetime.now()
                    # If the new status is CONFIRMED, add an unavailability time record
                    if new_status == ShiftVolunteerStatus.CONFIRMED:
                        # Fetch start and end times from the ShiftRequest table
                        shift_request = session.query(ShiftRequest).filter_by(id=shift_id).first()
                        if shift_request:
                            unavailability_record = UnavailabilityTime(
                                userId=user_id,
                                title=f"shift {shift_id}",
                                periodicity=1,
                                start=shift_request.startTime,
                                end=shift_request.endTime
                            )
                            session.add(unavailability_record)
                    session.commit()
                    return True
                else:
                    logging.info(f"No shift request volunteer with user id {user_id} and shift {shift_id} not found")
                    return False
            except ConflictError as e:
                logging.error(f"ConflictError: {e}")
                raise
            except Exception as e:
                session.rollback()
                logging.error(f"Error updating shift request for user {user_id} and shift_id {shift_id}: {e}")
                return False

    def check_conflict_shifts(session, current_shift):
        """
        Check if a given user has any conflicting confirmed shifts with the current shift request.

        :param session: Database session.
        :param current_shift: the current shift request to check for conflicts.
        :return: True if there is a conflict, False if no conflicts are found.
        """
        user_id = current_shift.user_id
        shift_id = current_shift.request_id
        try:
            # Query all confirmed shifts for the user, excluding the current shift
            confirmed_shifts = session.query(ShiftRequestVolunteer).join(ShiftRequest).filter(
                ShiftRequestVolunteer.user_id == user_id,
                ShiftRequestVolunteer.status == ShiftVolunteerStatus.CONFIRMED,  # Use enum for confirmed status
                ShiftRequestVolunteer.request_id != shift_id  # Exclude the current shift request
            ).all()
            # The current shift information with start time and end time
            current_shift_information = session.query(ShiftRequestVolunteer).join(ShiftRequest).filter(
                ShiftRequestVolunteer.user_id == user_id,
                ShiftRequestVolunteer.request_id == shift_id
            ).first()
            # Iterate over all confirmed shifts and check for time conflicts
            for shift in confirmed_shifts:
                if (shift.shift_request.startTime < current_shift_information.shift_request.endTime and
                        current_shift_information.shift_request.startTime < shift.shift_request.endTime):
                    # A conflict is found if the time ranges overlap
                    return True
            # If no conflicts are found, return False
            return False
        except Exception as e:
            # Log the error and return False in case of an exception
            logging.error(f"Error checking shift conflicts for user {user_id} and request {shift_id}: {e}")
            return False