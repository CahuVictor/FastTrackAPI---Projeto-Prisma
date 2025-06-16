from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from structlog import get_logger

from app.core.config import get_settings

logger = get_logger().bind(module="config")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_settings = get_settings()

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(subject: str  # usuário
                        # , roles: list[str] | None = None   # (descomente para voltar a embutir papéis)
                        ) -> str:
    """
    Gera um JWT contendo apenas o `sub` (username) e a expiração.

    Para voltar a embutir os papéis:
      1. Descomente o parâmetro `roles` acima.
      2. Descomente o bloco comentado mais abaixo.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=_settings.auth_access_token_expire
    )
    
    payload = {"sub": subject, "exp": expire}
    
    # ---- FUTURO: papéis dentro do token ---------------------------------
    # if roles:
    #     payload["roles"] = roles
    # ---------------------------------------------------------------------
    
    if _settings.auth_secret_key is None:
        logger.error("AUTH_SECRET_KEY não está configurada", environment=_settings.environment)
        raise RuntimeError("AUTH_SECRET_KEY não configurada")
    token = jwt.encode(
        payload,
        _settings.auth_secret_key,
        _settings.auth_algorithm
    )

    logger.info("Token JWT gerado", subject=subject, expires_at=str(expire), environment=_settings.environment)
    return token
