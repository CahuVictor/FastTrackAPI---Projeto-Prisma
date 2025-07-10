# app/models/models_event.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.orm import relationship # TODO verificar se alteração funcionou
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base

from app.models.models_local_info import LocalInfo
from app.models.models_forecast_info import ForecastInfo

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    city = Column(String, nullable=False)
    # participants = Column(ARRAY(String), nullable=False, server_default="{}") # type: ignore[var-annotated]  # TODO verificar se alteração funcionou
    participants: Mapped[list[str]] = Column(  # type: ignore[assignment]
        ARRAY(String), nullable=False, server_default="{}"
    )
    views = Column(Integer, default=0)

    local_info_id = Column(Integer, ForeignKey('local_infos.id'))
    forecast_info_id = Column(Integer, ForeignKey('forecast_infos.id'))

    # local_info = relationship("LocalInfo", back_populates="events")   # TODO verificar se alteração funcionou
    # forecast_info = relationship("ForecastInfo", back_populates="events")  # TODO verificar se alteração funcionou
    
    # local_info: Mapped["LocalInfo"] = relationship(back_populates="events")
    # forecast_info: Mapped["ForecastInfo"] = relationship(back_populates="events")
    
    local_info: Mapped["LocalInfo"] = relationship(
        "LocalInfo", back_populates="events"  # type: ignore[assignment]
    )
    forecast_info: Mapped["ForecastInfo"] = relationship(
        "ForecastInfo", back_populates="events"  # type: ignore[assignment]
    )