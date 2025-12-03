# app/schemas/local_filters.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import VenueType, LocalSource


class LocalFilters(BaseModel):
    """
    DTO used to represent all filters supported by the Local listing API.

    It is populated from query parameters in the controller and passed
    down to the service layer as a single object, avoiding endpoints
    with a huge number of parameters.
    
    Strongly-typed filter object for listing Local entities.

    This DTO is used between controller and service so that:
    - The controller can validate incoming query params once.
    - The service deals with a single, cohesive parameter object.
    - We can detect mismatches between endpoint params and filter fields.
    """

    skip: Annotated[int, Field(ge=0, default=0, description="How many records to skip")]
    limit: Annotated[int, Field(ge=0, le=100, default=20, description="Page size (0 = no limit)")]

    # Domain fields
    name: Annotated[str | None, Field(
        default=None,
        description="Filter by name (partial match allowed)"
    )] = None
    capacity: Annotated[int | None, Field(
        default=None,
        ge=0,
        description="Filter by total capacity"
    )] = None
    is_accessible: Annotated[bool | None, Field(
        default=None,
        description="Filter by accessibility"
    )] = None
    parking_available: Annotated[bool | None, Field(
        default=None,
        description="Filter by parking availability"
    )] = None
    
    # Geo
    latitude: Annotated[float | None, Field(
        default=None,
        description="Latitude coordinate in decimal degrees"
    )] = None
    longitude: Annotated[float | None, Field(
        default=None,
        description="Longitude coordinate in decimal degrees"
    )] = None

    # Integration / metadata
    external_id: Annotated[str | None, Field(
        default=None,
        description="Filter by external LocalInfo identifier"
    )] = None
    source: Annotated[LocalSource | None, Field(
        default=None,
        description="Filter by Local origin/source"
    )] = None

    # Physical / capacity details
    is_indoor: Annotated[bool | None, Field(
        default=None,
        description="True if venue is indoors"
    )] = None
    has_cover: Annotated[bool | None, Field(
        default=None,
        description="True if area is covered"
    )] = None
    capacity_seated: Annotated[int | None, Field(
        default=None,
        ge=0,
        description="Maximum seated capacity"
    )] = None
    capacity_standing: Annotated[int | None, Field(
        default=None,
        ge=0,
        description="Maximum standing capacity"
    )] = None

    venue_type: Annotated[VenueType | None, Field(
        default=None,
        description="Filter by venue type"
    )] = None

    manually_edited: Annotated[bool | None, Field(
        default=None,
        description="Filter by manual override flag"
    )] = None

    created_at: Annotated[datetime | None, Field(
        default=None,
        description="Return locals created on or after this datetime (UTC)"
    )] = None
    updated_at: Annotated[datetime | None, Field(
        default=None,
        description="Return locals updated on or after this datetime (UTC)"
    )] = None

    model_config = ConfigDict(extra="forbid")  # rejeita filtros desconhecidos
