from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from domain import ShiftStatus
from domain.base import Base

class ShiftRequirements(Base):
    __tablename__ = 'shift_requirements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey('shift_request.id'), name='request_id', nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), name='role.id')

    # title = Column(String(29), name='title', nullable=False)
    # startTime = Column(DateTime, name='from', nullable=False)
    # endTime = Column(DateTime, name='to', nullable=False)
    # status = Column(Enum(ShiftStatus), name='status', default=ShiftStatus.WAITING, nullable=False)
    # update_date_time = Column(DateTime, name='last_update_datetime', default=datetime.now(), nullable=False)
    # insert_date_time = Column(DateTime, name='created_datetime', default=datetime.now(), nullable=False)