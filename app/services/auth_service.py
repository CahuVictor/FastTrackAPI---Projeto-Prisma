# app/services/auth_service.py
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from structlog import get_logger

from app.services.interfaces.user_protocol import AbstractUserRepo
from app.core.deps import provide_user_repo

# from app.core.security import verify_password, create_access_token
from app.core.security import verify_password
from app.core.config import get_settings
from app.core.contextvars import request_user

logger = get_logger().bind(module="auth_service")

settings = get_settings()

_AbstractUserRepo = Depends(provide_user_repo)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def authenticate(username: str, password: str, repo: AbstractUserRepo = _AbstractUserRepo):
    user = repo.get_by_username(username)
    if not user:
        logger.warning("Usuário não encontrado", username=username)
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning("Senha inválida", username=username)
        return None

    logger.info("Usuário autenticado com sucesso", username=username)
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
            logger.error("AUTH_SECRET_KEY ausente na configuração", environment=settings.environment)
            raise RuntimeError("AUTH_SECRET_KEY não configurada")
        payload = jwt.decode(
            token, settings.auth_secret_key, [settings.auth_algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            logger.warning("Token JWT sem campo 'sub'")
            raise credentials_exception
    except JWTError as e:
        logger.warning("Token JWT inválido", error=str(e))
        raise credentials_exception

    user = repo.get_by_username(username)
    if user is None:
        logger.warning("Usuário do token não encontrado", username=username)
        raise credentials_exception
    logger.info("Usuário autenticado via token", username=username)
    
    # 💡 Aqui salvamos o usuário no contexto da requisiçãorevise o logging
    request_user.set(user.username)
    
    return user