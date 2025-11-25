# app/infra/repositories/sqlalchemy/local_repo_sqlalchemy.py
from __future__ import annotations

from sqlalchemy.orm import Session
from structlog import get_logger

from app.infra.db.tables.local_table import LocalTable
from app.models.local import Local
from app.models.event_local_enums import VenueType
from app.repositories.local_repo import LocalRepository


class LocalRepositorySQLAlchemy(LocalRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        location_name: str | None = None,
        capacity: int | None = None,
        venue_type: VenueType | None = None,
        is_accessible: bool | None = None,
        address: str | None = None,
        manually_edited: bool | None = None,
    ) -> list[Local]:
        query = self.session.query(LocalTable)

        if location_name is not None:
            # partial, case-insensitive match
            query = query.filter(LocalTable.location_name.ilike(f"%{location_name}%"))

        if capacity is not None:
            query = query.filter(LocalTable.capacity == capacity)

        if venue_type is not None:
            query = query.filter(LocalTable.venue_type == venue_type)

        if is_accessible is not None:
            query = query.filter(LocalTable.is_accessible == is_accessible)

        if address is not None:
            query = query.filter(LocalTable.address.ilike(f"%{address}%"))

        if manually_edited is not None:
            query = query.filter(LocalTable.manually_edited == manually_edited)

        if limit > 0:
            query = query.offset(skip).limit(limit)

        rows = query.all()

        return [
            Local(
                id=row.id,
                location_name=row.location_name,
                capacity=row.capacity,
                venue_type=row.venue_type,
                is_accessible=row.is_accessible,
                address=row.address,
                manually_edited=row.manually_edited,
            )
            for row in rows
        ]
