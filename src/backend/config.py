"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    DATABASE_URL: str = "sqlite:///data/mle_prep.db"
    ANTHROPIC_API_KEY: str  # required, no default
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    """Return application settings instance."""
    return Settings()
