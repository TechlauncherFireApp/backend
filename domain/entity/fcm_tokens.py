from datetime import datetime
from domain.base import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class FCMToken(Base):

    __tablename__ = 'fcm_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), name='user_id', nullable=False)
    fcm_token = Column(String(255), name='fcm_token', nullable=False)
    device_type = Column(String(50), name='device_type', nullable=False)
    created_at = Column(TIMESTAMP, name='created_at', default=datetime.now(), nullable=False)
    updated_at = Column(TIMESTAMP, name='updated_at', default=datetime.now(), onupdate=datetime.now, nullable=False)
    is_active = Column(Boolean, name='is_active', default=True, nullable=False)

    user = relationship("User")
