from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from domain import ShiftVolunteerStatus
from domain.base import Base


class ShiftRequestVolunteer(Base):
    __tablename__ = 'shift_request_volunteer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), name='user_id', nullable=False)
    request_id = Column(Integer, ForeignKey('shift_request.id'), name='request_id', nullable=False)
    position_id = Column(Integer, ForeignKey('shift_position.id'), name="position_id", nullable=False)
    status = Column(Enum(ShiftVolunteerStatus), name='status', nullable=False, default=ShiftVolunteerStatus.PENDING)
    update_date_time = Column(DateTime, name='last_update_datetime', default=datetime.now(), nullable=False)
    insert_date_time = Column(DateTime, name='created_datetime', default=datetime.now(), nullable=False)

    shift_request = relationship("ShiftRequest")
    user = relationship("User")