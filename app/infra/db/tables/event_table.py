# app/infra/db/tables/event_table.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped

from app.infra.db.base import Base

class EventTable(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    city = Column(String, nullable=False)
    participants: Mapped[list[str]] = Column(  # type: ignore[assignment]
        ARRAY(String), nullable=False, server_default="{}"
    )
    views = Column(Integer, default=0)

    local_id = Column(Integer, ForeignKey('local.id'))
    forecast_id = Column(Integer, ForeignKey('forecast.id'))
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)