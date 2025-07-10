# app/core/config.py
import os
from functools import lru_cache
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from structlog import get_logger
from datetime import datetime, timezone

from app.utils.settings_error import abort_with_validation_errors
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
    auth_secret_key: str | None = Field(None, validation_alias="AUTH_SECRET_KEY")
    auth_access_token_expire: int = Field( # access_token_expire_min
        60 * 24, validation_alias="ACCESS_TOKEN_EXPIRE_MIN"
    )
    auth_algorithm:  str = "HS256"
    
    # ── logging ───────────────────────────────────────
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field("plain", validation_alias="LOG_FORMAT")
    log_file: str | None = Field(None, validation_alias="LOG_FILE")

    # ── observabilidade / segurança ───────────────────
    sentry_dsn: str | None = Field(None, validation_alias="SENTRY_DSN")

    # ── CORS ──────────────────────────────────────────
    # allowed_origins: list[str] = Field(default_factory=list, validation_alias="ALLOWED_ORIGINS")  # TODO

    # ── servidor ──────────────────────────────────────
    host: str = Field("0.0.0.0", validation_alias="HOST")
    port: int = Field(8000, validation_alias="PORT")

    # ── filas / tarefas assíncronas ───────────────────
    celery_broker_url: str | None = Field(None, validation_alias="CELERY_BROKER_URL")

    # ── feature flags ─────────────────────────────────
    enable_feature_x: bool = Field(False, validation_alias="ENABLE_FEATURE_X")

    # ── paths ─────────────────────────────────────────
    media_root: str | None = Field(None, validation_alias="MEDIA_ROOT")

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
    
    @field_validator("auth_secret_key", mode="after")
    def _require_key_in_prod(cls, v, info):
        env = info.data.get("environment")
        if info.data.get("environment") == "prod" and not v:
            logger.error(
                "Configuração inválida: AUTH_SECRET_KEY ausente em produção",
                environment=env,
                auth_secret_key=v,
            )
            raise ValueError("AUTH_SECRET_KEY é obrigatório em produção")
        return v

# ──────────────────────────────────────────────────────
# Instância única (importável em toda a app)
# ──────────────────────────────────────────────────────
@lru_cache
def get_settings() -> Settings:
    try:
        settings = Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        abort_with_validation_errors(exc)
    logger.info("Configurações carregadas com sucesso", environment=settings.environment)
    return settings
