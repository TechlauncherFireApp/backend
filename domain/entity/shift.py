from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum
from datetime import datetime
from domain import Base
from domain.type import UserType


class Shift(Base):
    __tablename__ = 'shift'
    shiftId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(256), nullable=True, default=None)
    start = Column(DateTime, nullable=False, default=datetime.now())
    end = Column(DateTime, nullable=False, default=datetime.now())
    role = Column(Enum(UserType), name='user_type', nullable=False)
    UniqueConstraint(shiftId, userId, name='event')