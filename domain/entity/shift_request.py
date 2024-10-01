from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from domain import ShiftStatus
from domain.base import Base



class ShiftRequest(Base):
    __tablename__ = 'shift_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), name='user_id', nullable=False)
    title = Column(String(29), name='title', nullable=False)
    startTime = Column(DateTime, name='from', nullable=False)
    endTime = Column(DateTime, name='to', nullable=False)
    status = Column(Enum(ShiftStatus), name='status', default=ShiftStatus.SUBMITTED, nullable=False)
    update_date_time = Column(DateTime, name='last_update_datetime', default=datetime.now(), nullable=False)
    insert_date_time = Column(DateTime, name='created_datetime', default=datetime.now(), nullable=False)


    user = relationship("User")
    # One-to-many relationship: A shift can have multiple positions
    positions = relationship("ShiftPosition", backref="shift_request")
    # One-to-many relationship: A shift can be assigned to many volunteers
    volunteers = relationship("ShiftRequestVolunteer", backref="shift_request")
