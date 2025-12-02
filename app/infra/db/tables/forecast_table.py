# # app/infra/db/tables/forecast_table.py
from sqlalchemy import Column, Integer, DateTime, Float, String
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.tables.event_table import EventTable

class ForecastTable(Base):
    __tablename__ = 'forecast_infos'

    id = Column(Integer, primary_key=True, index=True)
    
    # Composite Key Candidates for Reuse logic
    target_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Weather Data
    description: Mapped[str] = mapped_column(String, nullable=False)
    temperature: Mapped[float] = Column(Float, nullable=True)
    weather_main: Mapped[str] = Column(String, nullable=False)
    weather_desc = Column(String, nullable=False)
    humidity: Mapped[int] = Column(Integer, nullable=False)
    wind_speed: Mapped[float] = Column(Float, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: Um forecast pode servir a N eventos que ocorrem no mesmo lugar/hora
    events: Mapped[list["EventTable"]] = relationship(
        # "EventTable", back_populates="forecast_info"  # type: ignore[assignment]
        "EventTable", back_populates="forecast"
        # back_populates="forecast_info"
    )

    # Garante unicidade para evitar duplicatas de clima na mesma coordenada/hora
    __table_args__ = (
        UniqueConstraint('target_date', 'latitude', 'longitude', name='uq_forecast_date_geo'),
    )
