# # app/infra/db/tables/forecast_table.py
from sqlalchemy import Column, Integer, DateTime, Float, String
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.tables.event_table import EventTable

class ForecastTable(Base):
    __tablename__ = 'forecast_infos'

    id = Column(Integer, primary_key=True, index=True)
    forecast_datetime = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=True)
    weather_main = Column(String, nullable=False)
    weather_desc = Column(String, nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)

    events: Mapped[list["EventTable"]] = relationship(
        "EventTable", back_populates="forecast_info"  # type: ignore[assignment]
        # back_populates="forecast_info"
    )
