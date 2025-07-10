# models_forecast_info.py
from sqlalchemy import Column, Integer, DateTime, Float, String
# from sqlalchemy.orm import relationship  # TODO verificar se alteração funcionou
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.models_event import Event

class ForecastInfo(Base):
    __tablename__ = 'forecast_infos'

    id = Column(Integer, primary_key=True, index=True)
    forecast_datetime = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=True)
    weather_main = Column(String, nullable=False)
    weather_desc = Column(String, nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)

    # events = relationship("Event", back_populates="forecast_info") # TODO verificar se alteração corrigiu
    # events: Mapped[list["Event"]] = relationship(back_populates="forecast_info")
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="forecast_info"  # type: ignore[assignment]
    )
