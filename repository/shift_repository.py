import logging
from typing import List, Optional

from datetime import datetime

from exception.client_exception import ConflictError
from domain import session_scope, ShiftRequestVolunteer, ShiftRequest, ShiftPosition, Role, ShiftRecord, ShiftStatus, UnavailabilityTime, ShiftVolunteerStatus


class ShiftRepository:

    def __init__(self):
        pass

    def post_shift_request(self, user_id: int, title: str, start_time: datetime, end_time: datetime, vehicle_type: int) -> Optional[int]:
        """
            Creates a new shift request and associated shift positions based on the vehicle type.

            Parameters:
            ----------
            user_id : int
                The ID of the user creating the shift request.
            title : str
                The title of the shift request.
            start_time : datetime
                The start time of the shift.
            end_time : datetime
                The end time of the shift.
            vehicle_type : int
                The type of vehicle associated with the shift (determines roles).

            Returns:
            -------
            int or None
                The ID of the newly created shift request if successful, otherwise None.
            """
        now = datetime.now()  # Get the current timestamp
        with session_scope() as session:
            try:
                # Create a new ShiftRequest object and populate its fields
                shift_request = ShiftRequest(
                    user_id=user_id,
                    title=title,
                    startTime=start_time,
                    endTime=end_time,
                    update_date_time=now,  # Update timestamp
                    insert_date_time=now  # Insert timestamp
                )

                # Add the ShiftRequest object to the session and commit
                session.add(shift_request)
                session.commit()
                # Add roles to the position table
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

    def create_positions(self, session, shiftId: int, vehicleType: int) -> bool:
        """
            Creates shift positions based on the vehicle type for a given shift request.

            Parameters:
            ----------
            session : Session
                The active database session.
            shiftId : int
                The ID of the shift request to create positions for.
            vehicleType : int
                The type of vehicle, which determines the roles to be assigned.

            Returns:
            -------
            bool
                True if positions are successfully created, otherwise False.
            """
        try:
            if vehicleType == 1:  # Heavy Tanker
                roleCodes = ['crewLeader', 'driver', 'advanced', 'advanced', 'basic', 'basic']
            elif vehicleType == 2:  # Medium Tanker
                roleCodes = ['crewLeader', 'driver', 'advanced', 'basic']
            elif vehicleType == 3:  # Light Unit
                roleCodes = ['driver', 'basic']
            else:
                logging.error(f"Invalid vehicle type: {vehicleType}")
                return False

            # create record in ShiftPosition
            for roleCode in roleCodes:
                shift_position = ShiftPosition(
                    shift_id=shiftId,
                    role_code=roleCode
                )
                session.add(shift_position)
            return True
        except Exception as e:
            logging.error(f"Error creating positions: {e}")
            return False

    def get_shift(self, userId: int) -> List[ShiftRecord]:
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
                        title=shift.shift_request.title,
                        start=shift.shift_request.startTime,
                        end=shift.shift_request.endTime,
                        status=shift.status.value)
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
                raise

    def update_shift_pending(self, shift_id: int) -> None:
        """
        Updates the status of a shift to 'PENDING'.

        Parameters:
        ----------
        shift_id : int
            The ID of the shift to update.
        """
        with session_scope() as session:
            try:
                # Fetch the ShiftRequest record with the given shift_id
                shift_request = session.query(ShiftRequest).filter_by(id=shift_id).first()

                if shift_request:
                    # Update the status to 'PENDING'
                    shift_request.status = ShiftStatus.PENDING
                    shift_request.last_update_datetime = datetime.now()  # Update the timestamp

                    # Commit the transaction to save changes
                    session.commit()
                    logging.info(f"Shift {shift_id} status updated to PENDING.")
                else:
                    # Handle the case where the shift with the given id does not exist
                    logging.error(f"Shift with id {shift_id} not found.")
                    raise ValueError(f"Shift with id {shift_id} not found.")
            except Exception as e:
                session.rollback()
                logging.error(f"Error updating shift {shift_id} to PENDING: {e}")
                raise

    def update_shift_status(self, user_id: int, shift_id: int, new_status: ShiftVolunteerStatus) -> bool:
        """
            Updates the status of a volunteer's shift request in the database.

            Parameters:
            ----------
            user_id : int
                The ID of the user whose shift request status is to be updated.
            shift_id : int
                The ID of the shift request to be updated.
            new_status : ShiftVolunteerStatus
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
                    is_conflict = self.check_conflict_shifts(session, user_id, shift_id)
                    if is_conflict and new_status == ShiftVolunteerStatus.ACCEPTED:
                        # Raise the ConflictError if there's a conflict
                        raise ConflictError(f"Shift {shift_id} conflicts with other confirmed shifts.")
                    # update status
                    shift_request_volunteer.status = new_status
                    shift_request_volunteer.last_update_datetime = datetime.now()
                    # If the new status is CONFIRMED, add an unavailability time record
                    if new_status == ShiftVolunteerStatus.ACCEPTED:
                        # Fetch start and end times from the ShiftRequest table
                        shift_request = session.query(ShiftRequest).filter_by(id=shift_id).first()
                        if shift_request:
                            unavailability_record = UnavailabilityTime(
                                userId=user_id,
                                title=f"shift {shift_id}",
                                periodicity=3,
                                start=shift_request.startTime,
                                end=shift_request.endTime,
                                is_shift=True
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

    def save_shift_assignments(self, assignments: List[dict]) -> None:
        """
        Saves multiple shift assignments and creates unavailability records in bulk,
        checking for conflicts before saving.

        Parameters:
        ----------
        assignments : List[dict]
            A list of dictionaries containing assignment data.
        """
        with session_scope() as session:
            try:
                shift_volunteers = []
                unavailability_records = []

                for assignment in assignments:
                    user_id = assignment['user_id']
                    shift_id = assignment['shift_id']
                    role_code = assignment['role_code']
                    shift_start = assignment['shift_start']
                    shift_end = assignment['shift_end']

                    # Check for conflicts
                    has_conflict = self.check_conflict_shifts(
                        session=session,
                        user_id=user_id,
                        shift_id=shift_id,
                        shift_start=shift_start,
                        shift_end=shift_end
                    )

                    if has_conflict:
                        logging.info(f"Conflict detected for user {user_id} on shift {shift_id}. Assignment skipped.")
                        continue  # Skip this assignment

                    # Fetch the role ID based on role code
                    role = session.query(Role).filter_by(code=role_code).first()
                    if not role:
                        logging.error(f"Role with code {role_code} not found.")
                        raise ValueError(f"Role with code {role_code} not found.")

                    # Create ShiftRequestVolunteer object
                    shift_volunteer = ShiftRequestVolunteer(
                        user_id=user_id,
                        request_id=shift_id,
                        position_id=role.id,
                        status=ShiftVolunteerStatus.ACCEPTED,
                        update_date_time=datetime.now(),
                        insert_date_time=datetime.now(),
                    )
                    shift_volunteers.append(shift_volunteer)

                    # Create UnavailabilityTime object
                    unavailability_record = UnavailabilityTime(
                        userId=user_id,
                        title=f"Shift {shift_id}",
                        periodicity=3,
                        start=shift_start,
                        end=shift_end,
                        is_shift=True
                    )
                    unavailability_records.append(unavailability_record)

                # Bulk save all records
                session.bulk_save_objects(shift_volunteers)
                session.bulk_save_objects(unavailability_records)

                session.commit()
                logging.info(f"Successfully saved {len(shift_volunteers)} shift assignments.")

            except Exception as e:
                session.rollback()
                logging.error(f"Error saving shift assignments: {e}")
                raise

    def check_conflict_shifts(self, session, user_id: int, shift_id: int, shift_start: datetime, shift_end: datetime) -> bool:
        """
        Check if a given user has any conflicting confirmed shifts with the current shift request.

        :param session: Database session.
        :param user_id: The user ID to check for conflicts.
        :param shift_id: The ID of the current shift request to check for conflicts.
        :param shift_start: Start time of the current shift.
        :param shift_end: End time of the current shift.
        :return: True if there is a conflict, False if no conflicts are found.
        """
        try:
            # Query all confirmed shifts for the user excluding the current shift
            confirmed_shifts = session.query(ShiftRequestVolunteer).join(ShiftRequest).filter(
                ShiftRequestVolunteer.user_id == user_id,
                ShiftRequestVolunteer.status == ShiftVolunteerStatus.ACCEPTED,
                ShiftRequestVolunteer.request_id != shift_id
            ).all()

            # Iterate over all confirmed shifts and check for time conflicts
            for shift_volunteer in confirmed_shifts:
                confirmed_shift = shift_volunteer.shift_request
                if (shift_start < confirmed_shift.endTime and shift_end > confirmed_shift.startTime):
                    # A conflict is found if the time ranges overlap
                    return True

            # If no conflicts are found, return False
            return False
        except Exception as e:
            # Log the error and return False in case of an exception
            logging.error(f"Error checking shift conflicts for user {user_id} and request {shift_id}: {e}")
            return False

