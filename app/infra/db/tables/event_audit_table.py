# app/infra/db/tables/event_audit_table.py
from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.tables.event_table import EventTable


class EventAuditAction(str, PyEnum):
    """
    Type of action that generated an audit record.

    Values:
        CREATED:
            The event was created.
        UPDATED:
            The event was modified.
        DELETED:
            The event was soft-deleted (or logically removed).
        RESTORED:
            The event was restored from a deleted state.
    """
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESTORED = "restored"


class EventAuditTable(Base):
    """
    SQLAlchemy ORM table that stores audit logs for events.

    Each row represents a single change operation (create, update,
    delete, restore) performed on a given Event.
    """

    __tablename__ = "event_audit_logs"

    # Identity
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to EventTable
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the event that was modified.",
    )

    # Action metadata
    action: Mapped[EventAuditAction] = mapped_column(
        SAEnum(EventAuditAction),
        nullable=False,
        comment="Type of action performed on the event.",
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When this change was recorded (UTC).",
    )
    changed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Username or ID of the user who performed the change.",
    )

    # Change details
    changes: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Compact diff-like structure describing what changed. "
            "Example: {'status': {'old': 'draft', 'new': 'published'}}"
        ),
    )

    snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Optional snapshot of the event state after the change. "
            "Use it only when you really need a full state copy."
        ),
    )

    # Relationship back to EventTable
    event: Mapped["EventTable"] = relationship(
        "EventTable",
        back_populates="audit_logs",
    )
