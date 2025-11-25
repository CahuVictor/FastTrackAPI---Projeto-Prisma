# app/services/auth_service.py
from __future__ import annotations

from datetime import datetime, timedelta
from structlog import get_logger

from app.core.config import get_settings
from app.core.security import (
    verify_password,
    create_access_token as create_access_token_jwt,
    create_refresh_token as create_refresh_token_jwt,
    decode_token as decode_token_jwt,
)
from app.models.auth_session import AuthSession
from app.models.user import User
from app.repositories.auth_session_repo import AuthSessionRepository
from app.services.user_service import UserService

logger = get_logger().bind(module="auth_service")
_settings = get_settings()


class InvalidCredentialsError(Exception):
    """Raised when username or password are invalid."""


class InvalidTokenError(Exception):
    """Raised when a token is invalid or cannot be decoded."""


class SessionNotFoundError(Exception):
    """Raised when a refresh token does not map to a valid session."""


class SessionInactiveError(Exception):
    """Raised when a session is expired or revoked."""


class AuthService:
    """
    Application service responsible for authentication flows.

    Responsibilities:
    - Validate user credentials.
    - Issue access and refresh tokens.
    - Manage AuthSession lifecycle (create/revoke/refresh).
    - Validate access tokens and load the associated user.
    """

    def __init__(
        self,
        user_service: UserService,
        session_repo: AuthSessionRepository,
    ) -> None:
        self._user_service = user_service
        self._session_repo = session_repo

    # ------------------------------------------------------------------ #
    # Helpers for expiration configuration
    # ------------------------------------------------------------------ #
    def _get_access_token_expires_delta(self) -> timedelta:
        """
        Returns the timedelta for access token expiration.

        Uses Settings.auth_access_token_expire (in minutes) as source.
        """
        minutes = getattr(_settings, "auth_access_token_expire", 60 * 24)
        return timedelta(minutes=minutes)

    def _get_refresh_token_expires_delta(self) -> timedelta:
        """
        Returns the timedelta for refresh token expiration.

        You can later move this to Settings (e.g. auth_refresh_token_expire).
        For now, we keep a default of 7 days in minutes.
        """
        minutes = getattr(_settings, "auth_refresh_token_expire", 60 * 24 * 7)
        return timedelta(minutes=minutes)

    # ------------------------------------------------------------------ #
    # Login / authenticate
    # ------------------------------------------------------------------ #
    def authenticate_user(self, username: str, password: str) -> User:
        """
        Validate user credentials and return the user if successful.

        Raises:
            InvalidCredentialsError: if the username or password are invalid.
        """
        try:
            user = self._user_service.get_user_by_username(username)
        except Exception:  # noqa: BLE001
            logger.info("Authentication failed: user not found", username=username)
            raise InvalidCredentialsError("Invalid username or password")

        if not verify_password(password, user.hashed_password):
            logger.info("Authentication failed: bad password", username=username)
            raise InvalidCredentialsError("Invalid username or password")

        logger.info("User authenticated successfully", username=username)
        return user

    def create_access_token(self, user: User) -> tuple[str, int]:
        """
        Create a signed JWT access token for the given user.

        Returns:
            (access_token, expires_in_seconds)
        """
        expires_delta = self._get_access_token_expires_delta()
        expires_in = int(expires_delta.total_seconds())

        access_token = create_access_token_jwt(
            subject=str(user.username),
            expires_delta=expires_delta,
            extra_claims={"roles": user.roles},
        )
        return access_token, expires_in

    def create_session(
        self,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> str:
        """
        Create a new AuthSession and return the refresh token.

        The session is stored via AuthSessionRepository.
        """
        refresh_expires_delta = self._get_refresh_token_expires_delta()

        refresh_token = create_refresh_token_jwt(
            subject=str(user.username),
            expires_delta=refresh_expires_delta,
        )

        now = datetime.utcnow()
        session = AuthSession(
            user_id=user.id or 0,  # For in-memory users without DB ID
            refresh_token=refresh_token,
            jti=None,  # You can wire a JTI generator here in the future
            created_at=now,
            expires_at=now + refresh_expires_delta,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self._session_repo.create(session)

        logger.info(
            "Auth session created",
            username=user.username,
            user_id=user.id,
        )

        return refresh_token

    def authenticate_and_issue_token(
        self,
        *,
        username: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str | None, int]:
        """
        High-level login operation.

        Steps:
        1. Authenticate user credentials.
        2. Create access token.
        3. Create refresh token + session.

        Returns:
            (access_token, refresh_token, access_expires_in_seconds)
        """
        user = self.authenticate_user(username, password)
        access_token, access_expires_in = self.create_access_token(user)
        refresh_token = self.create_session(
            user,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        logger.info(
            "User logged in",
            username=user.username,
            user_id=user.id,
        )

        return access_token, refresh_token, access_expires_in

    # Optional: alias to keep backward compatibility with previous name
    def login(
        self,
        *,
        username: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str | None, int]:
        """
        Backwards-compatible alias for authenticate_and_issue_token.
        """
        return self.authenticate_and_issue_token(
            username=username,
            password=password,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    # ------------------------------------------------------------------ #
    # Token / session validation
    # ------------------------------------------------------------------ #
    def get_current_user_from_token(self, token: str) -> User:
        """
        Decode the access token and return the associated user.

        Raises:
            InvalidTokenError: if token cannot be decoded or user not found.
        """
        try:
            payload = decode_token_jwt(token)
        except Exception as exc:  # noqa: BLE001
            logger.info("Failed to decode token", error=str(exc))
            raise InvalidTokenError("Invalid access token") from exc

        username: str | None = payload.get("sub")
        if username is None:
            logger.info("Token missing 'sub' claim")
            raise InvalidTokenError("Invalid access token")

        try:
            user = self._user_service.get_user_by_username(username)
        except Exception as exc:  # noqa: BLE001
            logger.info("User from token not found", username=username)
            raise InvalidTokenError("User not found") from exc

        return user

    # ------------------------------------------------------------------ #
    # Refresh token flow
    # ------------------------------------------------------------------ #
    def refresh_tokens(
        self,
        refresh_token: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str | None, int]:
        """
        Use a refresh token to obtain a new access token (and a new refresh token).

        Raises:
            SessionNotFoundError: if no session found.
            SessionInactiveError: if session is expired or revoked.
            InvalidTokenError: if refresh token has invalid payload.
        """
        session = self._session_repo.get_by_refresh_token(refresh_token)
        if session is None:
            logger.info("No AuthSession found for refresh token")
            raise SessionNotFoundError("Invalid refresh token")

        if not session.is_active:
            logger.info("AuthSession is not active", session_id=session.id)
            raise SessionInactiveError("Session is no longer active")

        # Load user
        user_id = session.user_id
        # For now, we only have lookup by username in UserService.
        # In a real SQL-backed implementation, we would have get(user_id).
        # Here we keep refresh minimal and rely mostly on username encoded in token.
        # To avoid extra complexity, we'll decode username from old refresh token.
        payload = decode_token(refresh_token)
        username = payload.get("sub")
        if username is None:
            raise InvalidTokenError("Invalid refresh token payload")

        user = self._user_service.get_user_by_username(username)

        # Invalidate old session
        self._session_repo.revoke(session_id=session.id)

        # Issue new tokens
        access_token, access_expires_in = self.create_access_token(user)
        new_refresh_token = self.create_session(
            user,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        logger.info(
            "Tokens refreshed",
            user_id=session.user_id,
        )

        return access_token, new_refresh_token, access_expires_in

    # ------------------------------------------------------------------ #
    # Logout helpers
    # ------------------------------------------------------------------ #
    def logout(self, refresh_token: str) -> None:
        """
        Revoke the session associated with the given refresh token.
        """
        self._session_repo.revoke(refresh_token=refresh_token)

    def logout_all(self, user_id: int) -> None:
        """
        Revoke all sessions for a given user.
        """
        self._session_repo.revoke_all_for_user(user_id=user_id)
