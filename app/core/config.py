# app/core/config.py
import os
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from structlog import get_logger
from datetime import datetime, timezone
from typing import List, Any

from app.utils.git_info import get_git_sha

logger = get_logger().bind(module="config")

# ──────────────────────────────────────────────────────
# util: decide quais arquivos .env serão carregados
# ──────────────────────────────────────────────────────
def _env_files() -> tuple[str, ...]:
    """
    Sempre carrega `.env` (base) + 1 overlay específico
    ───────────────────────────────────────────────────
    dev   → ('.env',)                  ← nada a sobrepor
    test  → ('.env', '.env.test')
    prod  → ('.env', '.env.prod')
    """
    env = os.getenv("ENVIRONMENT", "dev")
    return (".env",) if env == "dev" else (".env", f".env.{env}")

# ──────────────────────────────────────────────────────
# Settings principal
# ──────────────────────────────────────────────────────
class Settings(BaseSettings):
    # PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    # API_V1_PREFIX: str = "/api/v1"
    
    # ── modo de execução ──────────────────────────────
    environment:     str = Field("dev", validation_alias="ENVIRONMENT")   # fallback → "dev" str | None?
    debug:           bool = Field(False, validation_alias="DEBUG")
    testing:         bool = Field(False, validation_alias="TESTING")
    reload:          bool = Field(False, validation_alias="RELOAD")
    build_timestamp: str = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        validation_alias="BUILD_TIMESTAMP",
    )
    
    # ── banco e cache ─────────────────────────────────
    db_url:          str | None = Field(None, validation_alias="DB_URL")
    redis_url:       str | None = Field(None, validation_alias="REDIS_URL")
    
    # ── auth ──────────────────────────────────────────
    auth_secret_key: str = Field(..., alias="AUTH_SECRET_KEY")
    auth_access_token_expire: int = Field( # access_token_expire_min
        60 * 24, alias="ACCESS_TOKEN_EXPIRE_MIN"
    )
    auth_algorithm:  str = "HS256"
    
    # ── logging ───────────────────────────────────────
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("plain", alias="LOG_FORMAT")
    log_file: str | None = Field(None, alias="LOG_FILE")

    # ── observabilidade / segurança ───────────────────
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")

    # ── CORS ──────────────────────────────────────────
    # allowed_origins: list[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")  # TODO

    # ── servidor ──────────────────────────────────────
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")

    # ── filas / tarefas assíncronas ───────────────────
    celery_broker_url: str | None = Field(None, alias="CELERY_BROKER_URL")

    # ── feature flags ─────────────────────────────────
    enable_feature_x: bool = Field(False, alias="ENABLE_FEATURE_X")

    # ── paths ─────────────────────────────────────────
    media_root: str | None = Field(None, alias="MEDIA_ROOT")

    # ── build info (CI) ───────────────────────────────
    git_sha: str = Field(
        default_factory=lambda: os.getenv("GIT_SHA", get_git_sha()),
        alias="GIT_SHA",
    )
    
    # ─────────────────────── configuração Pydantic ─────────────────
    # No Pydantic v2 a configuração do .env é feita via model_config em vez de class Config
    model_config = SettingsConfigDict(                 # ⬅️  substitui class Config
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="forbid",               # var estranha? app aborta.
        case_sensitive=False,
        validate_default=True          # ⬅ lê variáveis antes de validar
    )
    
    # ─────────────────────── validações extras ─────────────────────
    @field_validator("redis_url", mode="after")
    def _require_redis_in_prod(cls, v, info):
        env = info.data.get("environment")
        if env == "prod" and not v:
            logger.error("Configuração inválida: REDIS_URL não fornecido em ambiente de produção", environment=env, redis_url=v)
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v
    
    def _check_in_prod(self):
        if self.environment == "prod" and not self.auth_secret_key:
            logger.error("Configuração inválida: AUTH_SECRET_KEY ausente em produção", environment=self.environment, auth_secret_key=self.auth_secret_key)
            raise ValueError("AUTH_SECRET_KEY é obrigatório em produção")
        return self

# ──────────────────────────────────────────────────────
# Instância única (importável em toda a app)
# ──────────────────────────────────────────────────────
@lru_cache
def get_settings() -> Settings:
    settings = Settings()  # type: ignore[call-arg]
    logger.info("Configurações carregadas com sucesso", environment=settings.environment)
    return settings
