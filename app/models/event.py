# app/models/event.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
# from enum import Enum

from app.models.event_local_enums import EventStatus, EventEnvironment
# from app.models.local import Local
# from app.models.forecast import Forecast

@dataclass(slots=True, kw_only=True)
class Event:
    """
    Domain entity that represents an Event in the system.

    This model is pure domain (no ORM, no Pydantic). It expresses how the
    business understands an event: lifecycle status, schedule (start/end),
    timezone context, city, age restriction, participants, and views.

    Persistence (SQLAlchemy) and HTTP representation (Pydantic schemas)
    must map to/from this entity.
    """

    # Identity
    id: int | None = None
    
    # Core content
    title: str
    description: str
    status: EventStatus = EventStatus.DRAFT
    
    # Scheduling
    start_time: datetime
    end_time: datetime
    timezone: str  # e.g. "America/Recife"
    
    # Context / classification
    city: str | None = None # Contexto
    age_restriction: str = "Livre"
    expected_audience: int | None = None
    environment: EventEnvironment = EventEnvironment.UNRESTRICTED

    # Engagement
    participants: list[str] = field(default_factory=list)
    views: int = 0
    
    # Audit fields
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    created_by: str | None = None
    updated_by: str | None = None
    deleted_by: str | None = None

    # ------------------------------------------------------------------ #
    # Domain behavior helpers
    # ------------------------------------------------------------------ #
    def add_view(self) -> None:
        """
        Increment the internal view counter by one.

        This is the domain-level operation; persistence is handled by the
        repository/service layers.
        """
        self.views += 1

    def add_participant(self, name: str) -> None:
        """
        Add a participant to the event if not already present.

        Args:
            name: Participant name to include.
        """
        if name not in self.participants:
            self.participants.append(name)

    @property
    def is_active(self) -> bool:
        """
        Indicates whether the event is currently considered 'active',
        i.e., it was published and not cancelled and not soft-deleted.
        """
        return (
            self.status == EventStatus.PUBLISHED
            and self.deleted_at is None
        )

    @property
    def duration_hours(self) -> float:
        """
        Compute the event duration in hours based on start_time and end_time.
        """
        diff = self.end_time - self.start_time
        return diff.total_seconds() / 3600

    @property
    def is_past(self) -> bool:
        """
        Returns True if the event already finished, comparing end_time with
        the current UTC time.
        """
        now = datetime.now(timezone.utc)
        return self.end_time < now

    # ------------------------------------------------------------------ #
    # Factory method
    # ------------------------------------------------------------------ #
    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        status: EventStatus = EventStatus.DRAFT,
        
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        
        city: str,
        age_restriction: str = "Livre",
        expected_audience: int | None = None,
        environment: EventEnvironment = EventEnvironment.UNRESTRICTED,
        participants: list[str] | None = None,
        created_by: str | None = None,
    ) -> "Event":
        """
        Factory method to create a new Event in memory, with default values
        for views and audit fields. Usually used in services before calling
        a repository to persist the entity.

        Args:
            title: Event title.
            description: Detailed description.
            start_time: Datetime when the event starts (UTC or tz-aware).
            end_time: Datetime when the event ends (UTC or tz-aware).
            timezone: IANA timezone identifier (e.g. "America/Recife").
            status: Initial lifecycle status (defaults to DRAFT).
            city: Optional city name used for filtering/marketing.
            age_restriction: Age classification label (e.g. "Livre").
            participants: Optional list of participant names.
            local_id: Optional foreign key to a Local/Venue entity.
            forecast_id: Optional foreign key to a Forecast entity.

        Returns:
            A new Event instance with id=None and views=0.
        """
        return cls(
            id=None,
            title=title,
            description=description,
            status=status,
            
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            
            city=city,
            age_restriction=age_restriction,
            expected_audience=expected_audience,
            environment=environment,
            
            participants=participants or [],
            views=0,
            
            created_at=None,
            updated_at=None,
            deleted_at=None,
            created_by=created_by,
            updated_by=None,
            deleted_by=None,
        )
