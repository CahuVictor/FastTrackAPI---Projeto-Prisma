# app/services/auth_service.py
from __future__ import annotations

from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from structlog import get_logger

from app.repositories.user_repo import UserRepository
from app.core.deps import provide_user_repo

from app.core.config import get_settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.auth_session import AuthSession
from app.models.user import User
from app.repositories.auth_session_repo import AuthSessionRepository
from app.services.user_service import UserService

from app.core.contextvars import request_user

logger = get_logger().bind(module="auth_service")

_settings = get_settings()

_UserRepository = Depends(provide_user_repo)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def authenticate( # TODO desabilitar e usar a classe AuthService
    username: str,
    password: str,
    repo: UserRepository = _UserRepository
):
    user = repo.get_by_username(username)
    if not user:
        logger.warning("Usuário não encontrado", username=username)
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning("Senha inválida", username=username)
        return None

    logger.info("Usuário autenticado com sucesso", username=username)
    return user

def get_current_user( # TODO desabilitar e usar a classe AuthService
    token: str = Depends(oauth2_scheme),
    repo: UserRepository = _UserRepository
) -> User:
    """
    FastAPI dependency that resolves the current authenticated user.

    It expects an Authorization header in the form:
        Authorization: Bearer <access_token>
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if _settings.auth_secret_key is None:
            logger.error("AUTH_SECRET_KEY ausente na configuração", environment=_settings.environment)
            raise RuntimeError("AUTH_SECRET_KEY não configurada")
        payload = jwt.decode(
            token, _settings.auth_secret_key, [_settings.auth_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            logger.warning("Token JWT sem campo 'sub'")
            raise credentials_exception
    except JWTError as e:
        logger.warning("Token JWT inválido", error=str(e))
        raise credentials_exception

    user = repo.get_by_username(username)
    if user is None:
        logger.warning("Usuário do token não encontrado", username=username)
        raise credentials_exception
    logger.info("Usuário autenticado via token", username=username)
    
    # 💡 Aqui salvamos o usuário no contexto da requisiçãorevise o logging
    request_user.set(user.username)
    
    return user

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
    # Login / authenticate
    # ------------------------------------------------------------------ #
    def authenticate_user(self, username: str, password: str) -> User: # , repo: UserRepository = _UserRepository
        """
        Validate user credentials and return the user if successful.

        Raises:
            InvalidCredentialsError: if the username or password are invalid.
        """
        try:
            user = self._user_service.get_user_by_username(username)
        except Exception:
            logger.info("Authentication failed: user not found", username=username)
            raise InvalidCredentialsError("Invalid username or password")

        if not verify_password(password, user.hashed_password):
            logger.info("Authentication failed: bad password", username=username)
            raise InvalidCredentialsError("Invalid username or password")

        logger.info("Usuário autenticado com sucesso", username=username)
        return user

    def login(
        self,
        *,
        username: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str | None, int]:
        """
        Perform login and return (access_token, refresh_token, expires_in).

        This method:
        - validates credentials;
        - creates access and refresh tokens;
        - persists an AuthSession for the refresh token.
        """
        user = self.authenticate_user(username, password)

        # Access token expiration
        access_minutes = getattr(
            _settings, "jwt_access_token_expires_minutes", 15
        )
        access_expires_delta = timedelta(minutes=access_minutes)
        access_expires_in = int(access_expires_delta.total_seconds())

        # Refresh token expiration
        refresh_minutes = getattr(
            _settings, "jwt_refresh_token_expires_minutes", 60 * 24 * 7
        )
        refresh_expires_delta = timedelta(minutes=refresh_minutes)

        access_token = create_access_token(
            subject=str(user.username),
            expires_delta=access_expires_delta,
            extra_claims={"roles": user.roles},
        )
        refresh_token = create_refresh_token(
            subject=str(user.username),
            expires_delta=refresh_expires_delta,
        )

        # Create auth session for refresh token
        now = datetime.utcnow()
        session = AuthSession(
            user_id=user.id or 0,  # if no ID in memory, 0 as placeholder
            refresh_token=refresh_token,
            jti=None,
            created_at=now,
            expires_at=now + refresh_expires_delta,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self._session_repo.create(session)

        logger.info(
            "User logged in",
            username=user.username,
            user_id=user.id,
        )

        return access_token, refresh_token, access_expires_in

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
            payload = decode_token(token)
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
        access_minutes = getattr(
            _settings, "jwt_access_token_expires_minutes", 15
        )
        access_expires_delta = timedelta(minutes=access_minutes)
        access_expires_in = int(access_expires_delta.total_seconds())

        refresh_minutes = getattr(
            _settings, "jwt_refresh_token_expires_minutes", 60 * 24 * 7
        )
        refresh_expires_delta = timedelta(minutes=refresh_minutes)

        new_access_token = create_access_token(
            subject=str(user.username),
            expires_delta=access_expires_delta,
            extra_claims={"roles": user.roles},
        )
        new_refresh_token = create_refresh_token(
            subject=str(user.username),
            expires_delta=refresh_expires_delta,
        )

        now = datetime.utcnow()
        new_session = AuthSession(
            user_id=user_id,
            refresh_token=new_refresh_token,
            jti=None,
            created_at=now,
            expires_at=now + refresh_expires_delta,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self._session_repo.create(new_session)

        logger.info(
            "Tokens refreshed",
            user_id=user_id,
        )

        return new_access_token, new_refresh_token, access_expires_in

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
