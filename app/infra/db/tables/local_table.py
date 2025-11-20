# # app/infra/db/tables/local_table.py
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from app.infra.db.base import Base
from app.models.event_local_enums import VenueType

if TYPE_CHECKING:
    from app.infra.db.tables.event_table import EventTable
    # from app.infra.db.tables.event_venue_history_table import EventVenueHistoryTable

class LocalTable(Base):
    __tablename__ = 'locals'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False) # Column(String, nullable=False)
    capacity: Mapped[int] = Column(Integer, nullable=False)
    venue_type: Mapped[VenueType] = Column(Enum(VenueType), nullable=True)
    
    # Address & Geo (Persisted Snapshot)
    address_street: Mapped[str] = mapped_column(String, nullable=True)
    address_number: Mapped[str] = mapped_column(String, nullable=True)
    address_district: Mapped[str] = mapped_column(String, nullable=True) # Bairro
    address_city: Mapped[str] = mapped_column(String, nullable=False)
    address_state: Mapped[str] = mapped_column(String(2), nullable=False) # UF
    address_zip: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    
    # Features
    is_accessible: Mapped[bool] = Column(Boolean, default=False)
    parking_available: Mapped[bool] = mapped_column(Boolean, default=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    
    manually_edited = Column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delete_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    # TODO user_updated

    # Relationship to History
    # events: Mapped[list["EventTable"]] = relationship(
    #     "EventTable", back_populates="locals"  # type: ignore[assignment]
    # )
    # event_history: Mapped[list["EventVenueHistoryTable"]] = relationship(
    #     "EventVenueHistoryTable", back_populates="local"
    # )
