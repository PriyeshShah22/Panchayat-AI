"""Application configuration loaded from environment variables."""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings, sourced from environment or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
    SARVAM_STT_MODEL: str = "saaras:v3"
    SARVAM_API_BASE_URL: str = "https://api.sarvam.ai"

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
