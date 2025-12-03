# app/models/local_external_query.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.models.enums import VenueType


@dataclass(slots=True)
class ExternalLocalQueryCriteria:
    """
    Domain model representing the criteria for querying the external
    LocalInfo API.

    This model is decoupled from HTTP concerns and can be reused by the
    service and integration layers.
    """

    name: str | None = None
    capacity_min: int | None = None
    capacity_max: int | None = None
    is_accessible: bool | None = None
    parking_available: bool | None = None
    
    latitude: float | None = None
    longitude: float | None = None
    distance: float | None = None
    
    is_indoor: bool | None = None
    has_cover: bool | None = None
    capacity_seated: int | None = None
    capacity_standing: int | None = None
    
    venue_types: List[VenueType] | None = None  

    # Optional pagination controls; for search they are used; for import
    # we typically only use `limit`.
    skip: int | None = None
    limit: int | None = None