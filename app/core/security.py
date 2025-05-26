from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    expire = datetime.now() + timedelta(
        minutes=settings.auth_access_token_expire
    )
    payload = {"sub": subject, "exp": expire}
    
    # ---- FUTURO: papéis dentro do token ---------------------------------
    # if roles:
    #     payload["roles"] = roles
    # ---------------------------------------------------------------------
    
    return jwt.encode(payload,
                      settings.auth_secret_key,
                      settings.auth_algorithm)
