# app/schemas/local/local_external_search.py
from __future__ import annotations

from typing import List, Annotated
from pydantic import BaseModel, Field

from app.models.enums import VenueType


class ExternalLocalSearch(BaseModel):
    """
    HTTP-level schema used to receive search filters for the external
    LocalInfo API via query parameters.

    This schema is meant to be bound by FastAPI in controllers and then
    transformed into the corresponding domain model used by the service.
    """
    skip: Annotated[int, Field(
        ge=0,
        description="How many records to skip (offset) in the external API.",
    )] = 0
    limit: Annotated[int, Field(
        ge=1,
        le=200,
        description="Maximum number of records to retrieve from the external API.",
    )] = 20

    name: Annotated[str | None, Field(
        description=(
            "Name or partial name of the venue. The external API may apply "
            "fuzzy matching strategies."
        ),
    )] = None
    capacity_min: Annotated[int | None,Field(
        ge=0,
        description="Minimum capacity (inclusive).",
    )] = None
    capacity_max: Annotated[int | None,Field(
        ge=0,
        description="Maximum capacity (inclusive).",
    )] = None
    is_accessible: Annotated[bool | None, Field(
        description="Filter by accessibility"
    )] = None
    parking_available: Annotated[bool | None, Field(
        description="Filter by parking availability"
    )] = None
    
    # Geo
    latitude: Annotated[float | None, Field(
        description="Latitude coordinate in decimal degrees"
    )] = None
    longitude: Annotated[float | None, Field(
        description="Longitude coordinate in decimal degrees"
    )] = None

    # Integration / metadata
    external_id: Annotated[str | None, Field(
        description="Filter by external LocalInfo identifier"
    )] = None

    # Physical / capacity details
    is_indoor: Annotated[bool | None, Field(
        description="True if venue is indoors"
    )] = None
    has_cover: Annotated[bool | None, Field(
        description="True if area is covered"
    )] = None
    capacity_seated: Annotated[int | None, Field(
        ge=0,
        description="Maximum seated capacity"
    )] = None
    capacity_standing: Annotated[int | None, Field(
        ge=0,
        description="Maximum standing capacity"
    )] = None
    
    venue_type: Annotated[VenueType | None, Field(
        description="Filter by venue type"
    )] = None
