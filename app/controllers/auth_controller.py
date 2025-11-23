# app/controllers/auth_controller.py
from __future__ import annotations

from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from structlog import get_logger

from app.schemas.auth.token import Token
from app.core.deps import provide_user_repo # TODO , provide_auth_service
from app.schemas.auth.auth_login import AuthLogin
from app.schemas.auth.auth_me_view import AuthMeView
from app.schemas.auth.auth_token import AuthToken
from app.repositories.user_repo import UserRepository
from app.services.auth_service import (
    authenticate, # TODO desabilitar authenticate e usar a classe AuthService
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
    # TODO 
    # payload: AuthLogin,
    # auth_service: AuthService = Depends(provide_auth_service),
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(provide_user_repo),
    # TODO 
) -> AuthToken:
    """
    Perform login with username and password.

    Returns an access token and a refresh token (if enabled).
    """
    logger.info("Tentativa de login recebida", username=form_data.username)
    user = authenticate(form_data.username, form_data.password, repo=repo)
    if not user:
        raise_http(logger.warning, 401, "Credenciais inválidas", username=form_data.username)
    # user_agent = request.headers.get("User-Agent")
    # ip_address = request.client.host if request.client else None
    
    # gera token “enxuto” (sub + exp)
    access_token = create_access_token(subject=user.username)
    # se quiser voltar a embutir papéis, use:
    # access_token = create_access_token(user.username, roles=user.roles)
    
    # try:
    #     access_token, refresh_token, expires_in = auth_service.login(
    #         username=payload.username,
    #         password=payload.password,
    #         user_agent=user_agent,
    #         ip_address=ip_address,
    #     )
    # except InvalidCredentialsError as exc:
    #     logger.info("Login failed", username=payload.username)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #     ) from exc

    logger.info("Login bem-sucedido", username=user.username)
    
    return AuthToken(
        access_token=access_token,
        # refresh_token=refresh_token,
        # expires_in=expires_in,
        token_type="bearer",
    )


# @router.post(
#     "/refresh",
#     summary="Refresh access token",
#     response_model=AuthToken,
#     status_code=status.HTTP_200_OK,
# )
# def refresh_token(
#     request: Request,
#     payload: RefreshTokenRequest,
#     auth_service: AuthService = Depends(provide_auth_service),
# ) -> AuthToken:
#     """
#     Use a refresh token to obtain a new access token (and new refresh token).
#     """
#     user_agent = request.headers.get("User-Agent")
#     ip_address = request.client.host if request.client else None

#     try:
#         access_token, refresh_token, expires_in = auth_service.refresh_tokens(
#             payload.refresh_token,
#             user_agent=user_agent,
#             ip_address=ip_address,
#         )
#     except (SessionNotFoundError, SessionInactiveError, InvalidTokenError) as exc:
#         logger.info("Refresh token failed")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or inactive refresh token",
#         ) from exc

#     return AuthToken(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         expires_in=expires_in,
#         token_type="bearer",
#     )


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
