# app/core/security.py  (trecho a adicionar)
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import JWTError, jwt
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

def _get_jwt_secret_key() -> str:
    """
    Resolve the JWT secret key from settings.

    Priority:
    1. Settings.auth_secret_key (AUTH_SECRET_KEY)
    2. Variável de ambiente AUTH_SECRET_KEY diretamente
    3. Fallback gerado em modo não-prod (apenas para dev/test)

    Em ambiente de produção, a ausência da chave dispara um erro explícito.
    """
    # 1) Tentar via Settings (pydantic-settings)
    key = getattr(_settings, "auth_secret_key", None) # _settings.auth_secret_key # "jwt_secret_key"
    if key:
        return key
    
    # 2) Tentar via os.environ diretamente
    import os
    env_key = os.getenv("AUTH_SECRET_KEY")
    if env_key:
        logger.warning(
            "AUTH_SECRET_KEY encontrada apenas em os.environ, mas não em Settings",
            environment=_settings.environment,
        )
        return env_key
    
    # 3) Se ainda assim não tiver, decidir se falha ou gera fallback
    logger.error(
        "AUTH_SECRET_KEY não está configurada",
        environment=_settings.environment,
    )
    
    # Em produção: erro hard
    if _settings.environment == "prod":
        raise RuntimeError("AUTH_SECRET_KEY não configurada em ambiente de produção")

    # Em dev/test: fallback seguro o suficiente para desenvolvimento local
    logger.warning(
        "Gerando AUTH_SECRET_KEY temporária para ambiente de desenvolvimento/teste",
        environment=_settings.environment,
    )
    return "dev-fallback-super-secret-key"


def _get_jwt_algorithm() -> str:
    """
    Resolve the JWT algorithm from settings.

    Defaults to HS256 if not set.
    """
    # return getattr(_settings, "jwt_algorithm", "HS256")
    return getattr(_settings, "auth_algorithm", "HS256") # _settings.auth_algorithm


def create_access_token(
    *,
    subject: str,  # usuário
    # , roles: list[str] | None = None   # (descomente para voltar a embutir papéis)
    expires_delta: timedelta | None = None,
    extra_claims: Dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The subject of the token (typically username or user_id).
        expires_delta: Optional timedelta until expiration.
        extra_claims: Optional extra claims to include in the payload.

    Para voltar a embutir os papéis:
      1. Descomente o parâmetro `roles` acima.
      2. Descomente o bloco comentado mais abaixo.
    
    Returns:
        Encoded JWT string.
    """ 
    if expires_delta is None:
        minutes = getattr(_settings, "jwt_access_token_expires_minutes", 15)
        # minutes=_settings.auth_access_token_expire
        expires_delta = timedelta(minutes=minutes)
    
    # ---- FUTURO: papéis dentro do token ---------------------------------
    # if roles:
    #     payload["roles"] = roles
    # ---------------------------------------------------------------------
    
    now = datetime.utcnow()
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }

    if extra_claims:
        to_encode.update(extra_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        _get_jwt_secret_key(),
        algorithm=_get_jwt_algorithm(),
    )

    logger.info("Token JWT gerado", subject=subject, expires_at=str(now + expires_delta), environment=_settings.environment)
    return encoded_jwt

def create_refresh_token(
    *,
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: Dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT refresh token.

    Args:
        subject: The subject of the token (username or user_id).
        expires_delta: Optional timedelta until expiration.
        extra_claims: Optional extra claims to include in the payload.

    Returns:
        Encoded JWT string.
    """
    if expires_delta is None:
        minutes = getattr(_settings, "jwt_refresh_token_expires_minutes", 60 * 24 * 7)
        expires_delta = timedelta(minutes=minutes)

    now = datetime.utcnow()
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "refresh",
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        _get_jwt_secret_key(),
        algorithm=_get_jwt_algorithm(),
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return its payload.

    Raises:
        JWTError: if the token is invalid or cannot be decoded.
    """
    payload = jwt.decode(
        token,
        _get_jwt_secret_key(),
        algorithms=[_get_jwt_algorithm()],
    )
    return payload