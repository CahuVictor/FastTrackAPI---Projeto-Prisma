# app/infra/repositories/inmemory/auth_session_repo_inmemory.py
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from structlog import get_logger

from app.models.auth_session import AuthSession
from app.repositories.auth_session_repo import AuthSessionRepository

logger = get_logger().bind(module="auth_session_repo_mem")


class AuthSessionRepoInMemory(AuthSessionRepository):
    """
    In-memory implementation of AuthSessionRepository.

    Suitable for tests and local development without a real database.
    """

    def __init__(self) -> None:
        self._next_id: int = 1
        self._storage: Dict[int, AuthSession] = {}
        self._refresh_index: Dict[str, int] = {}

        logger.info("In-memory AuthSession repository initialized")

    # ------------------- internal helpers ------------------- #
    def _generate_id(self) -> int:
        new_id = self._next_id
        self._next_id += 1
        return new_id

    # ------------------- public API ------------------------- #
    def create(self, session: AuthSession) -> AuthSession:
        """
        Persist a new AuthSession in memory.
        """
        if session.id is None:
            session.id = self._generate_id()

        self._storage[session.id] = session
        self._refresh_index[session.refresh_token] = session.id

        logger.info(
            "AuthSession created in memory",
            session_id=session.id,
            user_id=session.user_id,
        )
        return session

    def get_by_refresh_token(self, refresh_token: str) -> AuthSession | None:
        session_id = self._refresh_index.get(refresh_token)
        if session_id is None:
            logger.info(
                "AuthSession not found for refresh_token",
                refresh_token=refresh_token,
            )
            return None

        session = self._storage.get(session_id)
        if session is None:
            logger.warning(
                "AuthSession index points to missing session_id",
                session_id=session_id,
                refresh_token=refresh_token,
            )
        return session

    def get(self, session_id: int) -> AuthSession | None:
        session = self._storage.get(session_id)
        if session:
            logger.debug(
                "AuthSession fetched from memory",
                session_id=session.id,
                user_id=session.user_id,
            )
        else:
            logger.info(
                "AuthSession not found in memory",
                session_id=session_id,
            )
        return session

    def list_active_for_user(self, user_id: int) -> List[AuthSession]:
        now = datetime.utcnow()
        sessions = [
            s for s in self._storage.values()
            if s.user_id == user_id and s.revoked_at is None and now < s.expires_at
        ]
        logger.debug(
            "Listing active AuthSessions for user",
            user_id=user_id,
            count=len(sessions),
        )
        return sessions

    def revoke(self, session_id: int | None = None, refresh_token: str | None = None) -> None:
        """
        Mark a session as revoked. Either session_id or refresh_token is required.
        """
        if session_id is None and refresh_token is None:
            raise ValueError("Either 'session_id' or 'refresh_token' must be provided")

        session: AuthSession | None = None

        if session_id is not None:
            session = self._storage.get(session_id)
        elif refresh_token is not None:
            session = self.get_by_refresh_token(refresh_token)

        if session is None:
            logger.info(
                "AuthSession not found for revocation",
                session_id=session_id,
                refresh_token=refresh_token,
            )
            return

        session.revoked_at = datetime.utcnow()
        logger.info(
            "AuthSession revoked",
            session_id=session.id,
            user_id=session.user_id,
        )

    def revoke_all_for_user(self, user_id: int) -> None:
        now = datetime.utcnow()
        count = 0
        for session in self._storage.values():
            if session.user_id == user_id and session.revoked_at is None:
                session.revoked_at = now
                count += 1

        logger.info(
            "Revoked all AuthSessions for user",
            user_id=user_id,
            count=count,
        )

    def delete_expired(self, now: datetime | None = None) -> int:
        if now is None:
            now = datetime.utcnow()

        to_delete = [sid for sid, s in self._storage.items() if s.expires_at <= now]
        for sid in to_delete:
            session = self._storage.pop(sid, None)
            if session:
                self._refresh_index.pop(session.refresh_token, None)

        logger.info(
            "Deleted expired AuthSessions",
            deleted=len(to_delete),
        )
        return len(to_delete)
