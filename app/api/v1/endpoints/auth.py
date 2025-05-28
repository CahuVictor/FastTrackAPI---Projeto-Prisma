from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.deps import provide_user_repo
from app.services.interfaces.user import AbstractUserRepo
from app.services.auth_service import authenticate, create_access_token


router = APIRouter(tags=["auth"])

@router.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: AbstractUserRepo = Depends(provide_user_repo)
):
    user = authenticate(form_data.username, form_data.password, repo=repo)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # gera token “enxuto” (sub + exp)
    token = create_access_token(user.username)

    # se quiser voltar a embutir papéis, use:
    # token = create_access_token(user.username, roles=user.roles)
    
    return {"access_token": token, "token_type": "bearer"}
