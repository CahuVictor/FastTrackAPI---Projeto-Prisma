# app/utils/security.py
from __future__ import annotations

"""
Security helpers for FastAPI layer.

This module is responsible for:
- Defining OAuth2 dependencies (OAuth2PasswordBearer).
- Resolving the current authenticated user from the Authorization header.
- Enforcing role-based access control via dependency factories.

It delegates all core auth logic (token validation, user lookup, etc.)
to the AuthService, keeping this layer focused on HTTP/FastAPI concerns.
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from structlog import get_logger

from app.core.contextvars import request_user
from app.core.deps import provide_auth_service
from app.models.user import User
from app.services.auth_service import AuthService, InvalidTokenError

logger = get_logger().bind(module="security_utils")

# This is the token flow used by Swagger/clients:
#   1. POST /api/v1/auth/login → returns access_token
#   2. Client sends: Authorization: Bearer <access_token>
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(provide_auth_service),
) -> User:
    """
    FastAPI dependency that resolves the current authenticated user.

    It expects an Authorization header in the form:
        Authorization: Bearer <access_token>

    Responsibilities:
    - Delegate token decoding and user lookup to AuthService.
    - Convert domain errors (InvalidTokenError) into HTTP 401 responses.
    - Store the username in the request context (request_user) for logging.
    """
    try:
        user = auth_service.get_current_user_from_token(token)
    except InvalidTokenError:
        logger.info("Invalid access token received")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    # Save user information in the request context for logging, tracing, etc.
    request_user.set(user.username)
    logger.info("User authenticated via token", username=user.username)

    return user


# Convenience dependency to plug into routes:
#     dependencies=[auth_dep]
auth_dep = Depends(get_current_user)


def require_roles(*required_roles: str) -> Callable:
    """
    Factory for a dependency that enforces the presence of one of the given roles.

    Usage in a router:
        @router.get(
            "/admin-only",
            dependencies=[auth_dep, Depends(require_roles("admin"))],
        )
        def admin_only_endpoint(...):
            ...

    Notes:
        - This function assumes that `get_current_user` has already been
          executed (either via `auth_dep` or as a direct dependency).
        - Roles are taken from `user.roles` in the domain User object.
    """

    async def _verifier(user: User = auth_dep) -> User:
        user_roles = set(user.roles)
        needed = set(required_roles)

        if not needed & user_roles:
            logger.info(
                "Permission denied: missing roles",
                user_roles=list(user_roles),
                required=list(needed),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        # Return user in case the endpoint needs it
        return user

    return _verifier
