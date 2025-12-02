# app/schemas/event/event_csv_row.py
from __future__ import annotations

from datetime import datetime
from typing import Mapping

from pydantic import BaseModel, Field


class EventCsvRow(BaseModel):
    """
    Lightweight representation of a CSV row for Event import.

    This schema is used to validate and normalize raw CSV fields
    before they are converted into an `EventCreate` payload.
    """

    # Core content
    title: str = Field(..., description="Event title from CSV.")
    description: str = Field(..., description="Event description from CSV.")
    status: str | None = Field(
        default=None,
        description="Raw status string, expected to match EventStatus values.",
    )

    # Scheduling
    start_time: datetime = Field(
        ...,
        description="Event start time parsed from CSV (ISO-8601, preferably UTC).",
    )
    end_time: datetime = Field(
        ...,
        description="Event end time parsed from CSV (ISO-8601, preferably UTC).",
    )
    timezone: str = Field(
        ...,
        description="IANA timezone name (e.g. 'America/Recife').",
    )

    # Context / classification
    city: str = Field(..., description="City where the event takes place.")
    age_restriction: str | None = Field(
        default="Livre",
        description="Age restriction label (e.g. 'Livre', '16+', '18+').",
    )
    expected_audience: int | None = Field(
        default=None,
        description="Expected/target number of attendees (if provided by CSV).",
    )
    environment: str | None = Field(
        default=None,
        description=(
            "Raw environment string from CSV, expected to match EventEnvironment "
            "values (e.g. 'indoor', 'outdoor', 'unrestricted')."
        ),
    )

    # Engagement
    participants_raw: str | None = Field(
        default=None,
        description="Semicolon separated participants string from CSV.",
    )

    @classmethod
    def from_csv_row(cls, row: Mapping[str, str]) -> "EventCsvRow":
        """
        Build an EventCsvRow instance from a raw CSV dict row.

        This method is resilient to missing optional fields and applies
        simple normalization (e.g., stripping whitespace).
        """
        return cls(
            title=(row.get("title") or "").strip(),
            description=(row.get("description") or "").strip(),
            status=(row.get("status") or None),
            start_time=row.get("start_time", ""),  # Pydantic will parse ISO-8601
            end_time=row.get("end_time", ""),
            timezone=(row.get("timezone") or "").strip(),
            city=(row.get("city") or "").strip(),
            age_restriction=(row.get("age_restriction") or "Livre").strip(),
            expected_audience=int(row["expected_audience"]) if row.get("expected_audience") else None,
            environment=(row.get("environment") or None),
            participants_raw=row.get("participants"),
        )
