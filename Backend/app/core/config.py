#app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ========================
    # APP
    # ========================
    APP_NAME: str = "Bike Management System"
    DEBUG: bool = True

    # ========================
    # DATABASE
    # ========================
    DATABASE_URL: str

    # ========================
    # JWT AUTH
    # ========================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ========================
    # OTP CONFIG
    # ========================
    OTP_EXPIRE_MINUTES: int = 5

    # ========================
    # ENV CONFIG
    # ========================
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Singleton instance (recommended)
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Direct access (optional shortcut)
settings = get_settings()