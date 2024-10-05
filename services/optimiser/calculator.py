import json
from datetime import timedelta, datetime
from typing import List
from sqlalchemy import orm, func, alias

from domain import (User, AssetType, Role, UserRole, AssetTypeRole, ShiftRequest, ShiftPosition,
                    UnavailabilityTime, ShiftStatus)


class Calculator:
    """
    Calculates many helper data structures for the optimiser to then use in the actual linear optimiser step. This code
    is split out to enable testing and ease of understanding.
    """

    # Master list of all volunteers, these fetched once so that the order of the records in the list is deterministic.
    # This matters as the lists passed to Minizinc are not keyed and are instead used by index.
    _users_ = []
    _shifts_ = []
    _positions_ = []
    _roles_ = []


    # A single database session is used for all transactions in the optimiser. This is initialised by the calling
    # function.
    _session_ = None


    def __init__(self, session: orm.session):
        self._session_ = session

        # Fetch all the request data that will be used in the optimisation functions once.
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

    def get_shift_count(self) -> int:
        return len(self._shifts_)

    def get_shift_position_count(self) -> int:
        return len(self._positions_)

    def __get_request_data(self):
        """
        Initialising function that fetches a list of reference data from the database. This is done to simplify future
        functions as they don't need to be concerned about data fetching.
        @return:
        """
        self._users_ = self._session_.query(User) \
            .all()
        self._shift_ = self._session_.query(ShiftRequest) \
            .all()
            # .filter(ShiftRequest.status == ShiftStatus.SUBMITTED) \

        self._positions_ = self._session_.query(ShiftPosition) \
            .all()
        # return the roles that have not been deleted for the all shifts
        self._roles_ = self._session_.query(Role) \
            .filter(Role.deleted == False) \
            .all()

    def calculate_compatibility(self) -> List[List[bool]]:
        """
        Generates a 2D array of compatibilities between volunteers' unavailability and the requirements of the shift.
        """
        compatibilities = []

        # Iterate through each shift in the request
        for shift in self._shifts_:
            # Each shift gets its own row in the result set.
            shift_compatibility = []

            # Define the shift start and end times
            shift_start = shift.startTime
            shift_end = shift.endTime

            # Iterate through the users
            for user in self._users_:
                # Start by assuming the user is available
                user_available = True

                # Query unavailability times for the current user
                unavailability_records = self._session_.query(UnavailabilityTime).filter(
                    UnavailabilityTime.userId == user.id
                ).all()

                # Check if any unavailability overlaps with the entire shift period
                for record in unavailability_records:
                    if record.start < shift_end and record.end > shift_start:
                        user_available = False
                        break  # User is unavailable, no need to check further

                # Append the user's availability for this shift
                shift_compatibility.append(user_available)

            # Append the shift compatibilities to the overall result
            compatibilities.append(shift_compatibility)

        # Return the 2D array of compatibilities
        return compatibilities

    def calculate_skill_requirement(self) -> List[List[int]]:
        """
        Returns a 2D array showing the number of people required for each skill in an asset shift. Example:
                            Driver Pilot  Ninja
                          ----------------------
               Shift 1  [[1,       0,      0]
               Shift 2  [0,       1,      1]]
               Shift 3  [0,       2,      2]]
        @return: List of lists containing the required number of people for each role in each shift.
        """
        result = []
        # Iterate through each shift
        for shift in self._shifts_:
            this_position = []
            # Iterate through each shift_position
            for role in self._roles_:
                # Use the get_role_count function to query the number of people required for this role in the current
                # shift
                role_count = self.get_role_count(shift.id, role.code)

                # Append the role count to the current shift's list
                this_position.append(role_count)

            # Append the list of role counts for this shift to the return list
            rtn.append(this_position)

        return rtn

    def get_role_count(self, shift_request_id, role_code):
        """
        given a shift id and a role code, return the number of people required for that specific role
        this is done by counting the entries of shift positions that match the role
        """
        query = self._session_.query(func.count(ShiftPosition.id)) \
            .join(Role, Role.code == ShiftPosition.role_code) \
            .filter(Role.deleted == False) \
            .filter(Role.code == role_code) \
            .filter(ShiftPosition.shift_id == shift_request_id) \

        result = self._session_.query(func.count('*')).select_from(alias(query)).scalar()
        if result is None:
            result = 0
        return result

    def calculate_mastery(self):
        """
        For all active roles, return a 2D array of what user can perform what roles.
        For example, if the database has two users, both can drive but only 1 is advanced, the result would look like:
        name the indexes:
                      Driver   Advanced  CrewLeader
                      ----------------------------
              User 1 [[T,         F,          F]
              User 2  [T,         T,          F]]
        @return: A 2D array explaining what users can perform what roles.
        """
        rtn = []
        for user in self._users_:
            user_role = []
            for role in self._roles_:
                user_has_role = self._session_.query(UserRole) \
                    .filter(UserRole.user == user) \
                    .filter(UserRole.role == role) \
                    .first()
                user_role.append(user_has_role is not None)
            rtn.append(user_role)
        return rtn
