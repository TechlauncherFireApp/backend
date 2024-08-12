from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum, PrimaryKeyConstraint
from datetime import datetime
from domain import Base
from domain.type import UserType


class Shift(Base):
    __tablename__ = 'shift'
    shiftId = Column(Integer, nullable=False)
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(256), nullable=True, default=None)
    start = Column(DateTime, nullable=False, default=datetime.now())
    end = Column(DateTime, nullable=False, default=datetime.now())
    role = Column(Enum(UserType), name='user_type', nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('shiftId', 'userId'),
    )