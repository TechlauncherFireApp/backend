from dataclasses import dataclass
from datetime import datetime

from domain.type.shift_volunteer_status import ShiftVolunteerStatus


@dataclass
class ShiftRecord:
    shiftId: int
    roleId: int
    title: str
    start: datetime
    end: datetime
    status: ShiftVolunteerStatus