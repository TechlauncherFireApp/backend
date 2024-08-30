from enum import Enum


class ShiftVolunteerStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"