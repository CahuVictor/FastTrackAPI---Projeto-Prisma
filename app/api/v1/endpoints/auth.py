# api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from structlog import get_logger

from app.schemas.token import Token
from app.deps import provide_user_repo
from app.services.interfaces.user_protocol import AbstractUserRepo
from app.services.auth_service import authenticate
from app.core.security import create_access_token

from app.utils.http import raise_http

logger = get_logger().bind(module="auth")

router = APIRouter(tags=["auth"])

@router.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: AbstractUserRepo = Depends(provide_user_repo)
):
    logger.info("Tentativa de login recebida", username=form_data.username)
    user = authenticate(form_data.username, form_data.password, repo=repo)
    if not user:
        raise_http(logger.warning, 401, "Credenciais inválidas", username=form_data.username)
    
    # gera token “enxuto” (sub + exp)
    token = create_access_token(user.username)

    # se quiser voltar a embutir papéis, use:
    # token = create_access_token(user.username, roles=user.roles)
    logger.info("Login bem-sucedido", username=user.username)
    
    return {"access_token": token, "token_type": "bearer"}
