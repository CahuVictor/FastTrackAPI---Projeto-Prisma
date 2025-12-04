# app/schemas/event/event_filters.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import EventStatus, EventEnvironment, AgeRestriction


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
        str | None,
        Field(
            default=None,
            description="Filter events by title (substring match).",
        ),
    ] = None

    description: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter events by description (substring match).",
        ),
    ] = None

    status: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by lifecycle status. "
                "Accepted values: draft,published,cancelled. "
                "Multiple values allowed, separated by commas "
                "(e.g. 'draft,published')."
            ),
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
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by age restriction. "
                "Accepted values: Livre,10+,12+,14+,16+,18+. "
                "Multiple values allowed, separated by commas "
                "(e.g. 'Livre,16+')."
            ),
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
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by environment. "
                "Accepted values: indoor,outdoor,hybrid,unrestricted. "
                "Multiple values allowed, separated by commas "
                "(e.g. 'indoor,hybrid')."
            ),
        ),
    ] = None

    # Engagement
    participants: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by participant names. "
                "Multiple values allowed, separated by commas "
                "(e.g. 'Alice,Bob,Carol')."
            ),
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
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by user who created them. "
                "Multiple values allowed, separated by commas "
                "(e.g. '1,42,99')."
            ),
        ),
    ] = None

    updated_by: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by user who last updated them. "
                "Multiple values allowed, separated by commas."
            ),
        ),
    ] = None

    deleted_by: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Filter events by user who deleted them. "
                "Multiple values allowed, separated by commas."
            ),
        ),
    ] = None

    model_config = ConfigDict(extra="forbid")
