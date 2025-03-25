from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
