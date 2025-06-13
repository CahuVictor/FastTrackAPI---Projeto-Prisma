from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

from app.services.interfaces.user_protocol import AbstractUserRepo
from app.deps import provide_user_repo

# from app.core.security import verify_password, create_access_token
from app.core.security import verify_password
from app.core.config import get_settings

settings = get_settings()

_AbstractUserRepo = Depends(provide_user_repo)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def authenticate(username: str, password: str, repo: AbstractUserRepo = _AbstractUserRepo):
    user = repo.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: AbstractUserRepo = _AbstractUserRepo
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if settings.auth_secret_key is None:
            raise RuntimeError("AUTH_SECRET_KEY não configurada")
        payload = jwt.decode(
            token, settings.auth_secret_key, [settings.auth_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user