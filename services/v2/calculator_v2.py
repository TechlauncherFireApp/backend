import json
from datetime import timedelta, datetime
from typing import List
from sqlalchemy import orm, func, alias

from domain import User, AssetRequestVehicle, AssetType, Role, UserRole, AssetTypeRole


class Calculator:
    # Master list of all volunteers, these fetched once so that the order of the records in the list is deterministic.
    # This matters as the lists passed to Minizinc are not keyed and are instead used by index.
    _users_ = []
    _roles_ = []

    # A single database session is used for all transactions in the optimiser. This is initialised by the calling
    # function.
    _session_ = None

    _time_granularity_ = timedelta(minutes=30)

    # The request to optimise.
    request_id = None

    # Used to map between datetime.datetime().weekday() to the users availability as its agnostic of the time of year.
    _week_map_ = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    def __init__(self, session: orm.session, request_id: int):
        self._session_ = session
        self.request_id = request_id

        # Get all the data to be optimised from database
        self.__get_request_data()

    def get_number_of_roles(self):
        """
        @return: The number of roles to be optimised
        """
        return len(self._roles_)

    def get_number_of_volunteers(self) -> int:
        """
        @return: The number of users to be optimised.
        """
        return len(self._users_)

    def get_volunteer_by_index(self, index) -> User:
        return self._users_[index]

    def get_role_by_index(self, index) -> Role:
        return self._roles_[index]

    def get_roles(self) -> List[Role]:
        return self._roles_

    def __get_request_data(self):
        """
        Initialising function that fetches a list of reference data from the database. This is done to simplify future
        functions as they don't need to be concerned about data fetching.
        @return:
        """
        self._users_ = self._session_.query(User).all()
        self._roles_ = self._session_.query(Role).filter(Role.deleted == False).all()


def calculate_deltas(self, start: datetime, end: datetime) -> List[datetime]:
    """
    Given the start time and end time of a shift, generate a list of shift "blocks" which represent a
    self._time_granularity_ period that the user would need to be available for
    @param start: The start time of the shift.
    @param end: The end time of the shift.
    @return: A list of dates between the two dates.
    """
    deltas = []
    curr = start
    while curr < end:
        deltas.append(curr)
        curr += self._time_granularity_
    return deltas

def calculate_compatibility(self) -> List[List[bool]]:
    """
    Generates a 2D array of compatibilities between volunteers' availabilities and the requirements of the shift.
    This is the critical function of the optimizer as it determines if a user is available for assignment, regardless of role.

    Example 1: The volunteer is available between 2pm to 3pm and the shift is from 2pm to 2:30pm:
        Result: True
    Example 2: The volunteer is unavailable from 1pm to 2pm and the shift is from 1pm to 3pm:
        Result: False
    @return: A 2D array of compatibilities.
    """
    compatibilities = []

    # Iterate through each user
    for user in self._users_:
        # We start by assuming the user is available for all shifts
        user_availability = [True] * len(self._users_)

        # Iterate through each shift block to see if the user is unavailable during any part of the shift
        for idx, shift_block in enumerate(self.calculate_deltas(user.shift_start, user.shift_end)):
            # If the shift block overlaps with any of the user's unavailabilities, mark as unavailable
            for unavailability in user.unavailabilities:
                if unavailability[0] <= shift_block <= unavailability[1]:
                    user_availability[idx] = False
                    break  # No need to check further unavailabilities for this shift block

        compatibilities.append(user_availability)

    # Return the 2D array of compatibilities
    return compatibilities
