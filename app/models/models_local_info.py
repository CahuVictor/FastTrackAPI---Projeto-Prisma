# app/models/local_info.py
from sqlalchemy import Column, Integer, String, Boolean, Enum
# from sqlalchemy.orm import relationship  # TODO verificar se alteração funcionou
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

from app.db.base import Base

from app.schemas.venue_type import VenueTypes

if TYPE_CHECKING:
    from app.models.models_event import Event

class LocalInfo(Base):
    __tablename__ = 'local_infos'

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    venue_type = Column(Enum(VenueTypes), nullable=True)
    is_accessible = Column(Boolean, default=False)
    address = Column(String, nullable=True)
    manually_edited = Column(Boolean, default=False)

    # events = relationship("Event", back_populates="local_info")  # TODO verificar se alteração funcionou
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="local_info"  # type: ignore[assignment]
    )
