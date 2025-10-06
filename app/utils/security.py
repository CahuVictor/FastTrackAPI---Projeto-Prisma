# app/utils/security.py
from fastapi import HTTPException, Depends, status
from collections.abc import Callable

from app.services.auth_service import get_current_user

auth_dep = Depends(get_current_user)

def require_roles(*allowed: str) -> Callable:
    def verifier(user = auth_dep):
        if not set(allowed) & set(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente"
            )
        return user
    return verifier