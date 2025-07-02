# app/models/models_event.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    city = Column(String, nullable=False)
    # participants = Column(ARRAY(String), default=list, nullable=False)
    participants = Column(ARRAY(String), nullable=False, server_default="{}")
    views = Column(Integer, default=0)

    local_info_id = Column(Integer, ForeignKey('local_infos.id'))
    forecast_info_id = Column(Integer, ForeignKey('forecast_infos.id'))

    local_info = relationship("LocalInfo", back_populates="events")
    forecast_info = relationship("ForecastInfo", back_populates="events")
