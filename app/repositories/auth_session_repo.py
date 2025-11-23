# app/repositories/auth_session_repo.py
from __future__ import annotations

import abc
from datetime import datetime
from typing import List

from app.models.auth_session import AuthSession


class AuthSessionRepository(abc.ABC):
    """
    Abstraction for AuthSession persistence operations.

    Concrete implementations (SQLAlchemy, in-memory, etc.) must implement
    this interface so that AuthService can remain decoupled from storage.
    """

    @abc.abstractmethod
    def create(self, session: AuthSession) -> AuthSession:
        """
        Persist a new authentication session.

        Args:
            session: AuthSession domain object.

        Returns:
            Persisted AuthSession with ID and any storage-specific fields filled.
        """

    @abc.abstractmethod
    def get_by_refresh_token(self, refresh_token: str) -> AuthSession | None:
        """
        Retrieve a session by its refresh_token.

        Args:
            refresh_token: The opaque refresh token string.

        Returns:
            AuthSession if found, otherwise None.
        """

    @abc.abstractmethod
    def get(self, session_id: int) -> AuthSession | None:
        """
        Retrieve a session by its internal ID.
        """

    @abc.abstractmethod
    def list_active_for_user(self, user_id: int) -> List[AuthSession]:
        """
        Return a list of active sessions for a given user.
        """

    @abc.abstractmethod
    def revoke(self, session_id: int | None = None, refresh_token: str | None = None) -> None:
        """
        Mark a session as revoked.

        Either `session_id` or `refresh_token` must be provided.
        """

    @abc.abstractmethod
    def revoke_all_for_user(self, user_id: int) -> None:
        """
        Revoke all sessions for a given user.

        Useful for full logout from all devices.
        """

    @abc.abstractmethod
    def delete_expired(self, now: datetime | None = None) -> int:
        """
        Delete all expired sessions from storage.

        Returns:
            Number of deleted sessions.
        """
