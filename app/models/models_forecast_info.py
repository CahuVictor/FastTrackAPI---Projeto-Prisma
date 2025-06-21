# models_forecast_info.py
from sqlalchemy import Column, Integer, DateTime, Float, String
from sqlalchemy.orm import relationship

from app.db.base import Base

class ForecastInfo(Base):
    __tablename__ = 'forecast_infos'

    id = Column(Integer, primary_key=True, index=True)
    forecast_datetime = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=True)
    weather_main = Column(String, nullable=False)
    weather_desc = Column(String, nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)

    events = relationship("Event", back_populates="forecast_info")
