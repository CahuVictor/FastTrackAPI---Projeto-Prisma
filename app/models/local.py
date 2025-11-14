# app/models/local.py
from __future__ import annotations
from dataclasses import dataclass
from app.models.venue_type import VenueType

@dataclass(slots=True, kw_only=True)
class Local:
    id: int | None = None
    location_name: str
    capacity: int
    venue_type: VenueType | None = None
    is_accessible: bool = False
    address: str | None = None
    manually_edited: bool = False

    # exemplo de regra de negócio
    def can_host(self, people: int) -> bool:
        return people <= self.capacity

    @classmethod
    def create(
        cls,
        *,
        location_name: str,
        capacity: int,
        venue_type: VenueType | None = None,
        is_accessible: bool = False,
        address: str | None = None,
    ) -> "LocalInfo":
        return cls(
            id=None,
            location_name=location_name,
            capacity=capacity,
            venue_type=venue_type,
            is_accessible=is_accessible,
            address=address,
            manually_edited=False,
        )
