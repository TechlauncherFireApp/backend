from dataclasses import dataclass
from datetime import datetime

from domain.type.shift_volunteer_status import ShiftVolunteerStatus


@dataclass
class ShiftRecord:
    shiftId: int
    status: ShiftVolunteerStatus
    title: str
    start: datetime
    end: datetime