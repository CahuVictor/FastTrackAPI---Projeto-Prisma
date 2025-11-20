# app/models/local.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.models.event_local_enums import VenueType, LocalSource

@dataclass(slots=True, kw_only=True)
class Local:
    id: int | None = None
    name: str
    capacity: int | None = None
    is_accessible: bool = False
    parking_available: bool = False
    
    # Address Block
    address_street: str | None = None
    address_city: str
    address_state: str
    
    # geo & timezone
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    
    # integration and origin metadata
    external_id: str | None = None
    source: LocalSource = LocalSource.INTERNAL_SYNC
    
    # physical characteristics
    is_indoor: bool | None = None
    has_cover: bool | None = None
    capacity_seated: int | None = None
    capacity_standing: int | None = None
    
    contact_phone: str | None = None
    images: list[str] = field(default_factory=list)

    venue_type: VenueType | None = None
    # manually_edited: bool = False
    
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # exemplo de regra de negócio
    def can_host(self, people: int) -> bool:
        return people <= self.capacity

    # TODO entender para que serve essa última parte
    # @classmethod
    # def create(
    #     cls,
    #     *,
    #     location_name: str,
    #     capacity: int,
    #     venue_type: VenueType | None = None,
    #     is_accessible: bool = False,
    #     address: str | None = None,
    # ) -> "Local":
    #     return cls(
    #         id=None,
    #         location_name=location_name,
    #         capacity=capacity,
    #         venue_type=venue_type,
    #         is_accessible=is_accessible,
    #         address=address,
    #         manually_edited=False,
    #     )