# app/core/config.py
import os
from datetime import datetime, timezone
from pathlib import Path
from functools import lru_cache
from pydantic import Field, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from structlog import get_logger

from app.utils.settings_error import abort_with_validation_errors
from app.utils.git_info import get_git_sha

logger = get_logger().bind(module="config")

# ──────────────────────────────────────────────────────
# Helpers: env-file discovery / selection
# ──────────────────────────────────────────────────────

KNOWN_ENV_FILES = (".env", ".env.test", ".env.test.inmemory", ".env.prod")

def _env_files() -> tuple[str, ...]:
    """
    Decide which .env files should be loaded for this process.

    Rules:

    1. If ENVIRONMENT is explicitly set:
       * dev   → ('.env',)
       * test  → ('.env', '.env.test', '.env.test.inmemory')
       * prod  → ('.env', '.env.prod')
       * test.inmemory → treated like `test` (same tuple as above)

    2. If ENVIRONMENT is NOT set:
       * Fallback precedence:
         ('.env', '.env.prod', '.env.test', '.env.test.inmemory')
         This allows `.env.test.inmemory`, if present, to override previous
         values later in the chain.

    3. If there are known .env files in the repo that will NOT be loaded
       for the selected environment, log a warning so the developer can
       clean them up and avoid confusion.
    """
    cwd = Path.cwd()
    existing = {name for name in KNOWN_ENV_FILES if (cwd / name).exists()}

    raw_env = os.getenv("ENVIRONMENT")
    selected: tuple[str, ...]
    normalized_env = (raw_env or "").lower().strip() or None

    if normalized_env is None:
        # No ENVIRONMENT set → use generic precedence chain.
        selected = (".env", ".env.prod", ".env.test", ".env.test.inmemory")
        logger.info(
            "ENVIRONMENT not set; using default env-file precedence",
            env_files=selected,
        )
    else:
        if normalized_env == "dev":
            selected = (".env",)
        elif normalized_env in ("test", "test.inmemory"):
            # Treat test.inmemory like "test" for env-file layering:
            # base .env → overlay .env.test → overlay .env.test.inmemory
            selected = (".env", ".env.test", ".env.test.inmemory")
        elif normalized_env == "prod":
            selected = (".env", ".env.prod")
        else:
            # Unknown custom environment → fall back to `.env` only.
            selected = (".env",)
            logger.warning(
                "Unknown ENVIRONMENT value; falling back to base .env only",
                environment=normalized_env,
            )

        logger.info(
            "ENVIRONMENT detected; using targeted env-file chain",
            environment=normalized_env,
            env_files=selected,
        )

    # Warn if there are other known env files that won't be used.
    unused = existing.difference(selected)
    if unused:
        logger.warning(
            "Found env files for other environments that will not be loaded; "
            "consider removing or moving them to avoid configuration confusion",
            unused_env_files=sorted(unused),
            active_env_files=selected,
        )

    return selected


# ──────────────────────────────────────────────────────
# Settings model (central configuration)
# ──────────────────────────────────────────────────────


class Settings(BaseSettings):
    """
    Central application settings.

    All configuration is loaded from environment variables and .env files.
    This model also enforces validation rules and environment-specific
    constraints (e.g., required keys in production).
    """

    # PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    # API_V1_PREFIX: str = "/api/v1"

    # ── runtime mode / metadata ───────────────────────
    environment: str = Field(
        "dev",
        validation_alias="ENVIRONMENT",
        description="Logical environment name: dev / test / test.inmemory / prod.",
    )
    debug: bool = Field(
        False,
        validation_alias="DEBUG",
        description="Enables extra debug logging and diagnostics.",
    )
    testing: bool = Field(
        False,
        validation_alias="TESTING",
        description="Marks this process as a test run (pytest/CI).",
    )
    reload: bool = Field(
        False,
        validation_alias="RELOAD",
        description="Controls Uvicorn's reload flag in local runs.",
    )
    build_timestamp: str = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        ),
        validation_alias="BUILD_TIMESTAMP",
        description=(
            "Build timestamp in ISO8601 with timezone (UTC). "
            "If not provided, defaults to current UTC time."
        ),
    )

    # ── database / cache ──────────────────────────────
    db_url: str | None = Field(
        None,
        validation_alias="DB_URL",
        description="Primary database connection URL (SQLAlchemy style).",
    )
    redis_url: str | None = Field(
        None,
        validation_alias="REDIS_URL",
        description="Redis connection URL used for cache / queues.",
    )

    # ── auth / security ───────────────────────────────
    auth_secret_key: str | None = Field(
        None,
        validation_alias="AUTH_SECRET_KEY",
        description="Secret key used to sign auth tokens (must be set in prod).",
    )
    auth_access_token_expire: int = Field(  # previously: access_token_expire_min
        60 * 24,
        validation_alias="ACCESS_TOKEN_EXPIRE_MIN",
        description="Access token expiration in minutes.",
    )
    auth_algorithm: str = "HS256"

    # ── logging ───────────────────────────────────────
    log_level: str = Field(
        "INFO",
        validation_alias="LOG_LEVEL",
        description="Logging level: DEBUG / INFO / WARNING / ERROR.",
    )
    log_format: str = Field(
        "plain",
        validation_alias="LOG_FORMAT",
        description="Logging format: plain / json / color (depending on implementation).",
    )
    log_file: str | None = Field(
        None,
        validation_alias="LOG_FILE",
        description="Optional path to a log file (if not logging only to stdout).",
    )

    # ── observability / external services ─────────────
    sentry_dsn: str | None = Field(
        None,
        validation_alias="SENTRY_DSN",
        description="Sentry DSN for error tracking (optional).",
    )

    # ── CORS ──────────────────────────────────────────
    # TODO: re-enable CORS handling when needed.
    # allowed_origins: list[str] = Field(
    #     default_factory=list,
    #     validation_alias="ALLOWED_ORIGINS",
    #     description="List of allowed CORS origins.",
    # )

    # ── HTTP server ───────────────────────────────────
    host: str = Field(
        "0.0.0.0",
        validation_alias="HOST",
        description="Host/interface for the ASGI server.",
    )
    port: int = Field(
        8000,
        validation_alias="PORT",
        description="Port for the ASGI server.",
    )

    # ── async queues / background workers ─────────────
    celery_broker_url: str | None = Field(
        None,
        validation_alias="CELERY_BROKER_URL",
        description="Broker URL for Celery (or other queue system).",
    )

    # ── feature flags ─────────────────────────────────
    enable_feature_x: bool = Field(
        False,
        validation_alias="ENABLE_FEATURE_X",
        description="Example feature flag; toggle experimental features here.",
    )

    # ── filesystem paths ──────────────────────────────
    media_root: str | None = Field(
        None,
        validation_alias="MEDIA_ROOT",
        description="Base path for media files (uploads, generated assets, etc.).",
    )

    # ── build / revision info ─────────────────────────
    git_sha: str = Field(
        default_factory=lambda: os.getenv("GIT_SHA", get_git_sha()),
        validation_alias="GIT_SHA",
        description="Git commit SHA for this build (short or full).",
    )

    # ── external service URLs (runtime-configurable) ─
    local_url: str = Field(
        "https://default.local.api",
        validation_alias="LOCAL_URL",
        description="Base URL for the local-info external service.",
    )
    forecast_url: str = Field(
        "https://default.forecast.api",
        validation_alias="FORECAST_URL",
        description="Base URL for the forecast-info external service.",
    )

    # ───────────────── Pydantic Settings config ──────────────────
    # In Pydantic v2, env-file behavior is driven by `model_config` otherwise 'class Config'
    model_config = SettingsConfigDict(                 # ⬅️  substitui class Config
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="forbid",  # unknown variables cause a ValidationError (fail fast).
        case_sensitive=False,
        validate_default=True,  # read env vars before validating defaults.
    )

    # ─────────────────────── extra validations ────────────────────
    @field_validator("redis_url", mode="after")
    def _require_redis_in_prod(cls, v, info):
        """
        Ensure Redis is configured in production.

        In `prod` we require `REDIS_URL` to be set; otherwise we abort
        early with a clear error.
        """
        env = info.data.get("environment")
        if env == "prod" and not v:
            logger.error(
                "Invalid configuration: REDIS_URL is required in production",
                environment=env,
                redis_url=v,
            )
            raise ValueError("REDIS_URL is mandatory when ENVIRONMENT=prod")
        return v

    @field_validator("auth_secret_key", mode="after")
    def _require_key_in_prod(cls, v, info):
        """
        Ensure AUTH_SECRET_KEY is configured in production.

        This prevents the API from booting with an unsafe auth setup in prod.
        """
        env = info.data.get("environment")
        if env == "prod" and not v:
            logger.error(
                "Invalid configuration: AUTH_SECRET_KEY missing in production",
                environment=env,
                auth_secret_key=v,
            )
            raise ValueError("AUTH_SECRET_KEY is mandatory when ENVIRONMENT=prod")
        return v


# ──────────────────────────────────────────────────────
# Singleton accessor (used across the application)
# ──────────────────────────────────────────────────────
@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance for the whole application.

    This ensures environment variables and .env files are parsed only once,
    and that the same configuration object is reused everywhere.

    If any validation error occurs (missing/invalid env vars, unknown fields),
    the error is printed in a friendly way via `abort_with_validation_errors`
    and the process exits with code 1.
    """
    try:
        settings = Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        abort_with_validation_errors(exc)

    logger.info("Settings successfully loaded", environment=settings.environment)
    return settings