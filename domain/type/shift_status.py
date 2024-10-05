from enum import Enum


class ShiftStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"