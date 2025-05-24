from fastapi import HTTPException, status, Depends

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_password, create_access_token
from app.core.config import get_settings
from app.services.mock_users import get_user
from app.schemas.user import UserInDB

settings = get_settings()

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def authenticate(username: str, password: str) -> UserInDB | None:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.auth_secret_key, [settings.auth_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user  # pode retornar User sem hashed se preferir
