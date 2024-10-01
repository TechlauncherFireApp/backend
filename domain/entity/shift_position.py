from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from domain.base import Base


class ShiftPosition(Base):
    __tablename__ = 'shift_position'
    id = Column(Integer, primary_key=True, autoincrement=True)
    shift_id = Column(Integer, ForeignKey('shift_request.id'), name='shift_id', nullable=False)
    role_code = Column(String(256), ForeignKey('role.code'), name='role_code', nullable=False)

    # Many-to-one relationship with Role
    role = relationship("Role")
    # One-to-one relationship with ShiftRequestVolunteer using backref
    volunteer = relationship("ShiftRequestVolunteer", uselist=False, backref="shift_position")