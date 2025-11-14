# app/models/event.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass(slots=True, kw_only=True)
class Event:
    id: int | None = None
    title: str
    description: str
    event_date: datetime
    city: str
    participants: List[str] = field(default_factory=list)
    views: int = 0

    # referências às outras entidades (opcionais)
    local_id: int | None = None
    forecast_id: int | None = None
    
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def add_view(self) -> None:
        self.views += 1

    def add_participant(self, name: str) -> None:
        if name not in self.participants:
            self.participants.append(name)

    @property
    def is_past(self) -> bool:
        return self.event_date < datetime.utcnow()

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        event_date: datetime,
        city: str,
        participants: list[str] | None = None,
        local: Local | None = None,
        forecast: Forecast | None = None,
    ) -> "Event":
        return cls(
            id=None,
            title=title,
            description=description,
            event_date=event_date,
            city=city,
            participants=participants or [],
            views=0,
            local_id=local.id if local else None,
            forecast_id=forecast.id if forecast else None,
            local=local,
            forecast=forecast,
        )
