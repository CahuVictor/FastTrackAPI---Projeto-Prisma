# app/utils/security.py
from __future__ import annotations

from typing import Callable, List
from fastapi import Depends, HTTPException, Request, status
from collections.abc import Callable
from structlog import get_logger

from app.services.auth_service import get_current_user # TODO desabilitar get_current_user e usar a classe AuthService

# from app.core.deps import provide_auth_service
# from app.models.user import User
# from app.services.auth_service import AuthService, InvalidTokenError

logger = get_logger().bind(module="security_utils")


# async def get_current_user(
#     request: Request,
#     auth_service: AuthService = Depends(provide_auth_service),
# ) -> User:
#     """
#     FastAPI dependency that resolves the current authenticated user.

#     It expects an Authorization header in the form:
#         Authorization: Bearer <access_token>
#     """
#     auth_header = request.headers.get("Authorization")
#     if not auth_header:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not authenticated",
#         )

#     try:
#         scheme, token = auth_header.split(" ", 1)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authorization header format",
#         )

#     if scheme.lower() != "bearer":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication scheme",
#         )

#     try:
#         user = auth_service.get_current_user_from_token(token)
#     except InvalidTokenError as exc:
#         logger.info("Invalid access token", error=str(exc))
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#         ) from exc

#     return user

# Conveniência para reutilizar como dependency em endpoints
auth_dep = Depends(get_current_user)

def require_roles(*required_roles: str) -> Callable:
    """
    Factory for a dependency that enforces the presence of one of the given roles.

    Usage in a router:
        @router.get("/admin-only", dependencies=[Depends(require_roles("admin"))])
        def admin_only_endpoint(...):
            ...
    """
    
    def _verifier(user = auth_dep): # async def _dependency(user: User = Depends(get_current_user)) -> None:
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
        return user
    return _verifier