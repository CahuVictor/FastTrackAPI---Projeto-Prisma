# app/schemas/local/local_csv_row.py
from __future__ import annotations

from typing import Mapping, Any
from pydantic import BaseModel, Field

class LocalCsvRow(BaseModel):
    """
    Representation of a single row from the Local CSV import.

    All fields here correspond to CSV columns. Types are already
    partially normalized (int/float where it makes sense), but
    domain-specific conversions (e.g. enums, booleans) are applied
    in a separate mapping function.
    """

    name: str = Field(description="Nome do local, vindo da coluna 'name'")
    capacity: int = Field(description="Capacidade máxima, vindo da coluna 'capacity'")

    venue_type: str | None = Field(
        default=None,
        description="Tipo de local em formato string (será mapeado para VenueType posteriormente)",
    )
    is_accessible_raw: str | None = Field(
        default=None,
        description="Valor bruto da coluna 'is_accessible' (ex: '1', 'true', 'sim')",
    )
    address: str | None = Field(default=None)

    external_id: str | None = Field(default=None)
    source: str | None = Field(
        default=None,
        description="Valor textual da origem (será mapeado para LocalSource)",
    )

    is_indoor_raw: str | None = Field(
        default=None,
        description="Valor bruto da coluna 'is_indoor'",
    )
    has_cover_raw: str | None = Field(
        default=None,
        description="Valor bruto da coluna 'has_cover'",
    )

    capacity_seated: int | None = Field(default=None)
    capacity_standing: int | None = Field(default=None)

    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    timezone: str | None = Field(default=None)

    @classmethod
    def from_csv_row(cls, row: Mapping[str, Any]) -> "LocalCsvRow":
        """
        Build a LocalCsvRow from a raw DictReader row.

        This function is responsible for reading string values from CSV
        and doing only the **minimal** conversions (int/float básicos).

        Any business-specific semantics (enums, booleans, etc.) are handled
        by a separate mapping function (CSV -> LocalCreate).
        """
        def _parse_int(value: str | None) -> int | None:
            if value is None or value.strip() == "":
                return None
            return int(value)

        def _parse_float(value: str | None) -> float | None:
            if value is None or value.strip() == "":
                return None
            return float(value)

        return cls(
            location_name=(row.get("location_name") or "").strip(),
            capacity=int(row.get("capacity") or "0"),
            venue_type=(row.get("venue_type") or None),
            is_accessible_raw=(row.get("is_accessible") or None),
            address=(row.get("address") or None),
            external_id=(row.get("external_id") or None),
            source=(row.get("source") or None),
            is_indoor_raw=(row.get("is_indoor") or None),
            has_cover_raw=(row.get("has_cover") or None),
            capacity_seated=_parse_int(row.get("capacity_seated")),
            capacity_standing=_parse_int(row.get("capacity_standing")),
            latitude=_parse_float(row.get("latitude")),
            longitude=_parse_float(row.get("longitude")),
            timezone=(row.get("timezone") or None),
        )
