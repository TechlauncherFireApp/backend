from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from domain import Base


class InputShift(Base):
    __tablename__ = 'input_shift'
    shiftId = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=True, default=None)
    start = Column(DateTime, nullable=False, default=datetime.now())
    end = Column(DateTime, nullable=False, default=datetime.now())
    roles = Column(String, nullable=False)