
# app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ========================
    # SECURITY & LOCKOUT
    # ========================
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15
    REQUIRE_EMAIL_VERIFICATION: bool = False

    # ========================
    # RAZORPAY CONFIG
    # ========================
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_SECRET: str = ""

    # ========================
    # REDIS CONFIG
    # ========================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ========================
    # OTP / EMAIL CONFIG
    # ========================
    OTP_EXPIRE_MINUTES: int = 5
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_USE_TLS: bool = True

    # ========================
    # ENV CONFIG
    # ========================
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton instance (recommended)
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Direct access (optional shortcut)
settings = get_settings()
