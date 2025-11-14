# # app/infra/db/tables/local_table.py
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

from app.infra.db.base import Base

from app.models.venue_type import VenueType

if TYPE_CHECKING:
    from app.infra.db.tables.event_table import EventTable

class LocalTable(Base):
    __tablename__ = 'local_infos'

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    venue_type = Column(Enum(VenueType), nullable=True)
    is_accessible = Column(Boolean, default=False)
    address = Column(String, nullable=True)
    manually_edited = Column(Boolean, default=False)

    events: Mapped[list["EventTable"]] = relationship(
        "EventTable", back_populates="local_info"  # type: ignore[assignment]
        # back_populates="local_info"
    )
