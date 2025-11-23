# app/models/auth_session.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class AuthSession:
    """
    Domain model representing an authentication session / refresh token.

    Attributes:
        id: Internal identifier of the session (optional).
        user_id: ID of the associated user.
        refresh_token: Opaque refresh token string stored server-side.
        jti: Unique identifier for the token (JWT ID), if used.
        created_at: When the session was created.
        expires_at: When the session expires.
        revoked_at: When the session was revoked (if ever).
        user_agent: Optional information about the client user agent.
        ip_address: Optional information about the originating IP.
    """

    id: int | None = None
    user_id: int
    refresh_token: str
    jti: str | None = None

    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    user_agent: str | None = None
    ip_address: str | None = None

    @property
    def is_active(self) -> bool:
        """
        Return True if the session is not revoked and not expired.
        """
        now = datetime.utcnow()
        if self.revoked_at is not None:
            return False
        return now < self.expires_at
