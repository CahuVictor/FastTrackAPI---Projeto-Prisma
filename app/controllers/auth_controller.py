# app/controllers/auth_controller.py
from __future__ import annotations

from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from structlog import get_logger

from app.schemas.auth.token import Token
from app.core.deps import provide_user_repo, provide_auth_service
from app.schemas.auth.auth_login import AuthLogin
from app.schemas.auth.auth_me_view import AuthMeView
from app.schemas.auth.auth_token import AuthToken
from app.repositories.user_repo import UserRepository
from app.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    InvalidTokenError,
    SessionInactiveError,
    SessionNotFoundError,
)
from app.core.security import create_access_token
from app.core.rate_limit_config import limiter
from app.utils.http import raise_http
from app.utils.security import get_current_user

logger = get_logger().bind(module="auth_controller")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

_provide_auth_service = Depends(provide_auth_service)

class RefreshTokenRequest(BaseModel):
    """
    Request body for /auth/refresh endpoint.
    """
    refresh_token: str = Field(
        description="Refresh token used to obtain a new access token."
    )


class LogoutRequest(BaseModel):
    """
    Request body for /auth/logout endpoint.
    """
    refresh_token: str = Field(
        description="Refresh token that should be revoked (logout)."
    )


@router.post(
    "/login",
    summary="Authenticate user and obtain access token",
    response_model=AuthToken,
    status_code=status.HTTP_200_OK,
)
# @limiter.limit("10/minute")
def login(
    request: Request,  # ? Necessário para funcionar com @limiter.limit
    payload: AuthLogin,
    service: AuthService = _provide_auth_service,
) -> AuthToken:
    """
    Perform login with username and password.

    Returns an access token and a refresh token (if enabled).
    """
    access_token, refresh_token, expires_in = service.authenticate_and_issue_token(
        username=payload.username,
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    
    return AuthToken(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type="bearer",
    )

@router.post(
    "/token",
    summary="OAuth2 login for Swagger UI",
    response_model=AuthToken,
)
def login_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = _provide_auth_service,
) -> AuthToken:
    """
    OAuth2 Password Flow endpoint.

    Este endpoint é usado pelo Swagger (OAuth2PasswordBearer.tokenUrl).
    Ele recebe username/password via application/x-www-form-urlencoded
    e devolve um access_token compatível com o padrão OAuth2.
    """
    # Reaproveita sua lógica de login do AuthService
    access_token, refresh_token, expires_in = auth_service.login(
        username=form_data.username,
        password=form_data.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    # Para o fluxo OAuth2, normalmente só usamos o access_token.
    # Se quiser, pode adicionar refresh_token ao schema também.
    return AuthToken(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        # se o seu AuthToken tiver refresh_token, pode passar aqui também:
        # refresh_token=refresh_token,
    )

@router.post(
    "/refresh",
    summary="Refresh access token",
    response_model=AuthToken,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    # auth_service: AuthService = Depends(provide_auth_service),
) -> AuthToken:
    """
    Use a refresh token to obtain a new access token (and new refresh token).
    """
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    try:
        access_token, refresh_token, expires_in = auth_service.refresh_tokens(
            payload.refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    except (SessionNotFoundError, SessionInactiveError, InvalidTokenError) as exc:
        logger.info("Refresh token failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive refresh token",
        ) from exc

    return AuthToken(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type="bearer",
    )


@router.get(
    "/me",
    summary="Return the current authenticated user",
    response_model=AuthMeView,
)
def get_me(
    current_user = Depends(get_current_user),
) -> AuthMeView:
    """
    Return information about the currently authenticated user.
    """
    return AuthMeView(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        roles=current_user.roles,
    )


# @router.post(
#     "/logout",
#     summary="Logout by revoking the given refresh token",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def logout(
#     payload: LogoutRequest,
#     auth_service: AuthService = Depends(provide_auth_service),
# ) -> None:
#     """
#     Revoke the session associated with the provided refresh token.
#     """
#     auth_service.logout(payload.refresh_token)
#     return None
