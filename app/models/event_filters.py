# app/models/event_filters.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.event_local_enums import EventStatus, EventEnvironment


@dataclass(slots=True)
class EventFilterCriteria:
    """
    Domain-level filter model for events.

    This model is used by the service layer and can be translated to/from
    HTTP-level schemas or repository-specific filter mechanisms.
    """

    # Pagination
    skip: int = 0
    limit: int = 20

    # Core content
    title: list[str] | str | None = None
    description: list[str] | str | None = None
    status: list[EventStatus] | EventStatus | None = None

    # Scheduling
    start_from: datetime | None = None
    start_to: datetime | None = None

    # Context / classification
    city: str | None = None
    age_restriction: list[str] | str | None = None
    expected_audience: int | None = None
    environment: list[EventEnvironment] | EventEnvironment | None = None

    # Engagement
    participants: list[str] | str | None = None
    views_min: int | None = None
    views_max: int | None = None

    # Audit fields
    created_from: datetime | None = None
    created_to: datetime | None = None
    updated_from: datetime | None = None
    updated_to: datetime | None = None
    deleted_from: datetime | None = None
    deleted_to: datetime | None = None

    created_by: list[str] | str | None = None
    updated_by: list[str] | str | None = None
    deleted_by: list[str] | str | None = None
