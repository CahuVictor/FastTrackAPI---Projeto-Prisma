# app/core/config.py
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    # API_V1_PREFIX: str = "/api/v1"
    
    # ──────────────────────────── campos ────────────────────────────
    environment: str | None = Field("dev", validation_alias="ENVIRONMENT")   # fallback → "dev"
    db_url: str = Field("sqlite:///dev.db", validation_alias="DB_URL")       # obrigatório
    redis_url: str = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")
    
    auth_secret_key: str = Field("dummy-secret", validation_alias="AUTH_SECRET_KEY")
    auth_algorithm: str = "HS256"
    auth_access_token_expire: int = 60 * 24  # min
    
    # ──────────────────────────── legado ────────────────────────────
    database_url: str | None = Field(None, validation_alias="DATABASE_URL")
    secret_key: str | None = Field(None, validation_alias="SECRET_KEY")
    
    # ─────────────────────── configuração Pydantic ─────────────────
    # class Config:
    #     env_file = ".env"
    # No Pydantic v2 a configuração do .env é feita via model_config em vez de class Config
    model_config = SettingsConfigDict(                 # ⬅️  substitui class Config
        env_file=(".env", ".env.prod", ".env.test"),
        env_file_encoding="utf-8",
        extra="forbid",               # var estranha? app aborta.
        case_sensitive=False,
        validate_default=True          # ⬅ lê variáveis antes de validar
    )
    
    # ─────────────────────── validações extras ─────────────────────
    @field_validator("redis_url", mode="after")
    def _require_redis_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v
    
    def _check_in_prod(self):
        if self.environment == "prod" and not self.auth_secret_key:
            raise ValueError("AUTH_SECRET_KEY é obrigatório em produção")
        return self

@lru_cache
def get_settings() -> Settings: 
    return Settings()  # type: ignore[call-arg]
