# app/core/config.py
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    # API_V1_PREFIX: str = "/api/v1"
    # SECRET_KEY: str
    # DATABASE_URL: str
    # REDIS_URL: str = "redis://localhost:6379"
    
    # ──────────────────────────── campos ────────────────────────────
    environment: str = Field("dev", alias="ENVIRONMENT")   # fallback → "dev"
    db_url: str = Field(..., alias="DB_URL")               # obrigatório
    redis_url: str | None = Field(None, alias="REDIS_URL") # opcional (exc. prod)
    
    auth_secret_key: str = Field(..., alias="AUTH_SECRET_KEY")
    auth_algorithm: str = "HS256"
    auth_access_token_expire: int = 60 * 24  # min
    
    # ──────────────────────────── legado ────────────────────────────
    database_url: str | None = Field(None, alias="DATABASE_URL")
    secret_key: str | None = Field(None, alias="SECRET_KEY")
    
    # ─────────────────────── configuração Pydantic ─────────────────
    # class Config:
    #     env_file = ".env"
    # No Pydantic v2 a configuração do .env é feita via model_config em vez de class Config
    model_config = SettingsConfigDict(                 # ⬅️  substitui class Config
        env_file=(".env", ".env.prod", ".env.test"),
        env_file_encoding="utf-8",
        extra="forbid",               # var estranha? app aborta.
        case_sensitive=False
    )
    
    # ─────────────────────── validações extras ─────────────────────
    @field_validator("redis_url", mode="after")
    def _require_redis_in_prod(cls, v, info):
        if info.data.get("environment") == "prod" and not v:
            raise ValueError("REDIS_URL é obrigatório em produção")
        return v

@lru_cache
def get_settings() -> Settings: 
    return Settings()
