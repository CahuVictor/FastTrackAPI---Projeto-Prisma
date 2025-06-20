# api/v1/endpoints/auth.py
# from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from structlog import get_logger

from app.schemas.token import Token
from app.deps import provide_user_repo
from app.services.interfaces.user_protocol import AbstractUserRepo
from app.services.auth_service import authenticate # , create_access_token
from app.core.security import create_access_token

# from app.services.auth_service import authenticate, get_current_user # remover

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
        logger.warning("Falha de autenticação", username=form_data.username)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # gera token “enxuto” (sub + exp)
    token = create_access_token(user.username)

    # se quiser voltar a embutir papéis, use:
    # token = create_access_token(user.username, roles=user.roles)
    logger.info("Login bem-sucedido", username=user.username)
    
    return {"access_token": token, "token_type": "bearer"}
