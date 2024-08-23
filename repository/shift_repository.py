import logging

from flask import jsonify

from datetime import datetime, timezone
from exception import EventNotFoundError, InvalidArgumentError
from domain import session_scope, ShiftRequestVolunteer, ShiftRequest


class ShiftRepository:

    def __init__(self):
        pass

    '''def get_shift(self, userId=None):
        """
        Retrieves all shift events for a given user that have not ended yet.

        :param user_id: ID of the user whose shifts are being queried.
        :return: A list of shift records or an empty list if none found.
        """
        now = datetime.now()
        with session_scope() as session:
            try:
                # only show the shift that is end in the future
                #shifts = session.query(Shift).filter(
                #    Shift.userId == userId,
                #    Shift.end > now).all()
                if userId:
                    shifts = session.query(AssetRequestVolunteer).filter_by(user_id=userId).all()
                else:
                    shifts = session.query(AssetRequestVehicle).all()
                shift_records = []
                for shift in shifts:
                    # write shift information into list
                    shift_record = {
                        "shiftId": shift.id,
                        "vehicle_id": shift.vehicle_id,
                        "role_id": shift.role_id,
                        "status": shift.status,
                        "start_time": shift.asset_request_vehicle.from_date_time,
                        "end_time": shift.asset_request_vehicle.to_date_time
                    }
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
                return []'''

    def get_shift(self, userId):
        """
            Retrieves all shift events for a given user that have not ended yet.

            :param user_id: ID of the user whose shifts are being queried.
            :return: A list of shift records or an empty list if none found.
        """
        now = datetime.now()
        with session_scope() as session:
            try:
            #only show the shift that is end in the future
                shifts = session.query(ShiftRequestVolunteer).join(ShiftRequest).filter(
                    ShiftRequestVolunteer.user_id == userId,
                    ShiftRequest.endTime > now).all()
                shift_records = []
                for shift in shifts:
                    # write shift information into list
                    shift_record = {
                        "shiftId": shift.request_id,
                        "status": shift.status,
                        "title": shift.shift_request.title,
                        "start": shift.shift_request.startTime,
                        "end": shift.shift_request.endTime
                    }
                    shift_records.append(shift_record)
                return shift_records
            except Exception as e:
                logging.error(f"Error retrieving shifts for user {userId}: {e}")
            return []