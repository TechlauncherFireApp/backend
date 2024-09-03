from enum import Enum


class ShiftStatus(Enum):
    WAITING = "waiting"
    UNSUBMITTED = "un-submitted"
    INPROGRESS = "in-progress"
    COMPLETED = "completed"