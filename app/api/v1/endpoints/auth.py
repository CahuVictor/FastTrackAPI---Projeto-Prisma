from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.services.auth import authenticate, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}
