# app/infra/db/tables/event_table.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from app.infra.db.base import Base
from app.models.event_local_enums import EventStatus, EventEnvironment

if TYPE_CHECKING:
    from app.infra.db.tables.local_table import LocalTable
    from app.infra.db.tables.forecast_table import ForecastTable
    # from app.infra.db.tables.event_venue_history_table import EventVenueHistoryTable
    from app.infra.db.tables.event_audit_table import EventAuditTable
    
class EventTable(Base):
    """
    SQLAlchemy ORM table that persists Event data.

    This is the infrastructure representation of the Event domain entity.
    It is responsible only for mapping columns and relationships to the
    underlying database.
    """
    __tablename__ = 'events'

    # Identity
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Core content
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), nullable=False, default=EventStatus.DRAFT)
    
    # Scheduling (stored as UTC datetimes)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False) # UTC
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)   # UTC
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, comment="IANA timezone id (e.g. 'America/Recife').",)
    
    # Context
    city: Mapped[str] = mapped_column(String, nullable=False)
    age_restriction: Mapped[str] = mapped_column(String(20), nullable=False, default="Livre")
    
    # Expected audience size
    expected_audience: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Estimated/target number of attendees.",)

    # Indoor/Outdoor constraints
    environment: Mapped[EventEnvironment] = mapped_column(Enum(EventEnvironment), nullable=False, default=EventEnvironment.UNRESTRICTED, comment="Indoor/outdoor constraints for the event.",)
    
    # Engagement
    participants: Mapped[list[str]] = mapped_column(  # type: ignore[assignment]
        ARRAY(String), nullable=False, server_default="{}"
    )
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Audit fields (who did what/when)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    delete_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="Soft-delete timestamp. Null means not deleted.",)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Username or ID of the creator.",)
    updated_by: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Last user who updated this event.",)
    deleted_by: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="User who soft-deleted this event.",)
    
    # # History Relationship (venue assignment over time)
    # venue_history: Mapped[list["EventVenueHistoryTable"]] = relationship(
    #     "EventVenueHistoryTable",
    #     back_populates="event",
    #     cascade="all, delete-orphan",
    # )

    # Audit logs for this event
    audit_logs: Mapped[list["EventAuditTable"]] = relationship(
        "EventAuditTable",
        back_populates="event",
        cascade="all, delete-orphan",
    )