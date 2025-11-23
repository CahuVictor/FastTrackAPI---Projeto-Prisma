# app/infra/db/tables/auth_session_table.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base


class AuthSessionTable(Base):
    """
    SQLAlchemy model for authentication sessions / refresh tokens.

    Each row represents a logical session that can be used to issue
    new access tokens via the refresh flow.
    """

    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Opaque token or reference to it (depending on strategy).
    refresh_token: Mapped[str] = mapped_column(
        String(length=255), nullable=False, unique=True, index=True
    )

    # Optional JWT ID if using token identifiers.
    jti: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True, unique=True, index=True
    )

    # Audit / lifecycle fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_agent: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(length=64), nullable=True)

    # Optional relationship to UserTable (if you want to use it elsewhere).
    user = relationship("UserTable", backref="auth_sessions")

    @property
    def is_active(self) -> bool:
        """
        Check if the session is currently active (not revoked and not expired).
        """
        now = datetime.utcnow()
        if self.revoked_at is not None:
            return False
        return now < self.expires_at
