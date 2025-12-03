# app/schemas/event/event_filters.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import EventStatus, EventEnvironment


class EventFilters(BaseModel):
    """
    HTTP-level filter DTO used to list events.

    All fields are optional and are exposed as query parameters.
    They are later converted into `EventFilterCriteria` for the
    service/repository layer.
    """

    # Pagination
    skip: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            description="How many records to skip (offset).",
        ),
    ] = 0

    limit: Annotated[
        int,
        Field(
            default=20,
            ge=1,
            le=100,
            description="Maximum number of records to return.",
        ),
    ] = 20

    # Core content
    title: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by title (accepts single value or list).",
        ),
    ] = None

    description: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by description (accepts single value or list).",
        ),
    ] = None

    status: Annotated[
        list[EventStatus] | EventStatus | None,
        Field(
            default=None,
            description="Filter events by lifecycle status (single or multiple).",
        ),
    ] = None

    # Scheduling
    start_from: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose start_time is on or after this datetime.",
        ),
    ] = None

    start_to: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose start_time is on or before this datetime.",
        ),
    ] = None

    # Context / classification
    city: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter events by city.",
        ),
    ] = None

    age_restriction: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by age restriction (single or multiple).",
        ),
    ] = None

    expected_audience: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter events by expected audience (exact match).",
        ),
    ] = None

    environment: Annotated[
        list[EventEnvironment] | EventEnvironment | None,
        Field(
            default=None,
            description="Filter events by environment (single or multiple).",
        ),
    ] = None

    # Engagement
    participants: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by participant names (single or multiple).",
        ),
    ] = None

    views_min: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            description="Minimum number of views (inclusive).",
        ),
    ] = None

    views_max: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            description="Maximum number of views (inclusive).",
        ),
    ] = None

    # Audit fields
    created_from: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose created_at is on or after this datetime.",
        ),
    ] = None

    created_to: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose created_at is on or before this datetime.",
        ),
    ] = None

    updated_from: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose updated_at is on or after this datetime.",
        ),
    ] = None

    updated_to: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose updated_at is on or before this datetime.",
        ),
    ] = None

    deleted_from: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose deleted_at is on or after this datetime.",
        ),
    ] = None

    deleted_to: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Filter events whose deleted_at is on or before this datetime.",
        ),
    ] = None

    created_by: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by user who created them (single or multiple).",
        ),
    ] = None

    updated_by: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by user who last updated them (single or multiple).",
        ),
    ] = None

    deleted_by: Annotated[
        list[str] | str | None,
        Field(
            default=None,
            description="Filter events by user who deleted them (single or multiple).",
        ),
    ] = None

    model_config = ConfigDict(extra="forbid")
