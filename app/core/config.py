from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SECRET_KEY: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    PORTS: int = 5432  # значение по умолчанию

    class Config:
        env_file = ".env"  # опционально


@lru_cache
def get_settings():
    return Settings()