from functools import lru_cache
from pydantic import Field
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PROJECT_NAME: str = "FastTrackAPI - Projeto Prisma"
    # API_V1_PREFIX: str = "/api/v1"
    # SECRET_KEY: str
    # DATABASE_URL: str
    # REDIS_URL: str = "redis://localhost:6379"

    auth_secret_key: str = Field(
        "CHANGE_ME", env="AUTH_SECRET_KEY"
    )
    auth_algorithm: str = "HS256"
    auth_access_token_expire: int = 60 * 24  # minutos
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings: 
    return Settings()
