# app/models/local_filters.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.models.enums import VenueType, LocalSource


@dataclass(slots=True)
class LocalFilterCriteria:
    """
    Domain model representing the criteria used to query Locals.

    This object is independent from any HTTP or Pydantic concerns and can be
    reused by the service and repository layers.
    """
    skip: int = 0
    limit: int = 20

    name: str | None = None
    capacity: int | None = None
    is_accessible: bool | None = None
    parking_available: bool | None = None

    latitude: float | None = None
    longitude: float | None = None

    external_id: str | None = None
    source: LocalSource | None = None

    is_indoor: bool | None = None
    has_cover: bool | None = None
    capacity_seated: int | None = None
    capacity_standing: int | None = None

    venue_type: List[VenueType] | None = None  
    manually_edited: bool | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
