from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, JSON
from datetime import datetime
from domain import Base

# maybe don't need the mergedTimeInterval column

class MergedUnavailabilityTime(Base):
    __tablename__ = 'merged_unavailability_time'
    eventId = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)
    mergedEventId = Column(JSON, nullable=True, default=None)
    mergedTitle = Column(JSON, nullable=True, default=None)
    mergedTimeInterval = Column(JSON, nullable=True, default=None)
    start = Column(DateTime, nullable=False, default=datetime.now())
    end = Column(DateTime, nullable=False, default=datetime.now())
    UniqueConstraint(eventId, userId, name='event')
