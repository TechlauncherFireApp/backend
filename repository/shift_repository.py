import logging
from typing import List

from dataclasses import asdict
from flask import jsonify
from datetime import datetime, timezone

from domain import session_scope, ShiftRequestVolunteer, ShiftRequest, ShiftPosition, Role, ShiftRecord, ShiftStatus


class ShiftRepository:

    def __init__(self):
        pass

    def post_shift_request(self, user_id, title, start_time, end_time, vehicle_type):
        now = datetime.now()  # Get the current timestamp
        with session_scope() as session:
            try:
                # Create a new ShiftRequest object and populate its fields
                shift_request = ShiftRequest(
                    user_id=user_id,
                    title=title,
                    startTime=start_time,
                    endTime=end_time,
                    status=ShiftStatus.PENDING,  # need to be changed to submitted after linda pr approved
                    update_date_time=now,  # Update timestamp
                    insert_date_time=now  # Insert timestamp
                )

                # Add the ShiftRequest object to the session and commit
                session.add(shift_request)
                session.commit()
                # Add roles to the table now
                positions_created = self.create_positions(session, shift_request.id, vehicle_type)
                if not positions_created:
                    session.rollback()
                    return None
                session.commit()
                return shift_request.id  # Optionally return the created ShiftRequest object id

            except Exception as e:
                logging.error(f"Error creating new shift request: {e}")
                session.rollback()
                return None




    def create_positions(self, session, shiftId, vehicleType):
        # implement the position creation when posting/creating new shift
        try:
            if vehicleType == 11:  # Heavy Tanker
                roles = ['Crew Leader', 'Driver', 'Advanced', 'Advanced', 'Basic', 'Basic']
            elif vehicleType == 12:  # Medium Tanker
                roles = ['Crew Leader', 'Driver', 'Advanced', 'Basic']
            elif vehicleType == 13:  # Light Unit
                roles = ['Driver', 'Basic']
            else:
                logging.error(f"Invalid vehicle type: {vehicleType}")
                return False

                # create record in ShiftPosition
            for role_name in roles:
                role = session.query(Role).filter_by(name=role_name).first()
                if role:
                    shift_position = ShiftPosition(
                        shift_id=shiftId,
                        role_code=role.code
                    )
                    session.add(shift_position)
                else:
                    logging.error(f"Role not found: {role_name}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Error creating positions: {e}")
            return False


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
                        roleId=shift.position_id,
                        title=shift.shift_request.title,
                        start=shift.shift_request.startTime,
                        end=shift.shift_request.endTime,
                        status=shift.status.value)
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
