"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    DATABASE_URL: str = "sqlite:///data/mle_prep.db"
    ANTHROPIC_API_KEY: str = ""  # optional, default empty string
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_BACKEND: str = "auto"  # 'auto', 'sdk', or 'anthropic'
    OPENAI_API_KEY: str = ""  # optional, for OpenAI TTS engine
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEBUG: bool = True

    # TTS settings
    TTS_ENGINE: str = "edge-tts"
    TTS_VOICE: str = "en-US-AriaNeural"
    TTS_RATE: str = "+0%"  # edge-tts rate string, e.g. "+20%", "-10%"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    """Return application settings instance."""
    return Settings()
