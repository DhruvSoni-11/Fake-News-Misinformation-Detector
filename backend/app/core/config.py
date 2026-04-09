"""
app/core/config.py
------------------
Centralised application configuration using Pydantic BaseSettings.
All environment-overridable values live here; nothing else imports os.environ directly.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "Fake News & Misinformation Detector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ── NLP / Scoring ─────────────────────────────────────────────────────────
    # Maximum number of characters accepted in raw-text input
    MAX_TEXT_LENGTH: int = 50_000
    # Timeout (seconds) for URL fetch
    URL_FETCH_TIMEOUT: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance consumed throughout the app
settings = Settings()
