# app/models/event_patch.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.enums import EventStatus, EventEnvironment

@dataclass(slots=True, kw_only=True)
class EventPatch:
    """
    Domain-level patch model for `Event`.

    This entity represents a set of partial changes that can be applied
    to an existing `Event`. All fields are optional and `None` means
    “no change” for that attribute.

    It is meant to be used in the service layer, after converting from
    HTTP-level patch schemas (e.g. `EventUpdate`), so that the domain
    does not depend on Pydantic or FastAPI types.

    Important:
        - `id` is *not* part of this patch model; the target event is
          identified separately (e.g., via a function parameter).
        - Audit fields and view counters are intentionally omitted here:
          they are managed by repositories or specific domain operations.
    """

    # Core content
    title: str | None = None
    description: str | None = None
    status: EventStatus | None = None

    # Scheduling
    start_time: datetime | None = None
    end_time: datetime | None = None
    timezone: str | None = None

    # Context / classification
    city: str | None = None
    age_restriction: str | None = None
    expected_audience: int | None = None
    environment: EventEnvironment | None = None

    # Engagement
    participants: list[str] | None = None