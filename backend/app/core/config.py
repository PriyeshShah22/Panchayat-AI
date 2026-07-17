"""Application configuration loaded from environment variables."""
import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings, sourced from environment or `.env`."""

    model_config = SettingsConfigDict(
        env_file=None if os.getenv("VERCEL") else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Smart Society Management System"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database (Postgres preferred; SQLite is the sandbox fallback)
    DATABASE_URL: str = "sqlite:///./smart_society.db"
    # Example production URL: postgresql+psycopg://user:password@localhost:5432/smart_society

    @field_validator("DATABASE_URL")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Use the installed psycopg v3 driver for provider-style Postgres URLs."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # SMTP / Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_DEFAULT_CHAT_ID: Optional[str] = None

    # AI Provider (openai-compatible). Leave blank to use the offline heuristic assistant.
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-5.4-nano"
    AI_PROVIDER: str = "stub"  # "stub" or "openai"

    # Sarvam AI speech-to-text translation (Indic audio -> English text)
    SARVAM_API_KEY: Optional[str] = None
    SARVAM_FALLBACK_API_KEY: Optional[str] = None
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_API_BASE_URL: str = "https://api.sarvam.ai"

    # Razorpay UPI checkout. Online payment stays disabled until all are set.
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = None
    RAZORPAY_API_BASE_URL: str = "https://api.razorpay.com/v1"

    # OCR
    OCR_PROVIDER: str = "stub"  # "stub" or "google_vision"
    GOOGLE_VISION_API_KEY: Optional[str] = None

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

    # Billing defaults
    DEFAULT_MAINTENANCE_AMOUNT: float = 2500.0
    LATE_FEE_PERCENT: float = 2.0  # % applied after due date

    COMPANY_NAME: str = "Smart Society Co."


settings = Settings()
