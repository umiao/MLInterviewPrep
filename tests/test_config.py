"""Tests for config module."""



def test_settings_with_valid_env(monkeypatch):
    """Settings loads all fields from env vars."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LLM_MODEL", "claude-test")
    monkeypatch.setenv("DEBUG", "true")

    from src.backend.config import Settings

    s = Settings()
    assert s.ANTHROPIC_API_KEY == "sk-test-key"
    assert s.DATABASE_URL == "sqlite:///:memory:"
    assert s.LLM_MODEL == "claude-test"
    assert s.DEBUG is True


def test_settings_missing_api_key_defaults_empty(monkeypatch):
    """Missing ANTHROPIC_API_KEY defaults to empty string."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    from src.backend.config import Settings

    s = Settings(_env_file=None)
    assert s.ANTHROPIC_API_KEY == ""


def test_settings_defaults(monkeypatch):
    """Default values are applied when only required fields are set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from src.backend.config import Settings

    s = Settings(_env_file=None)
    assert s.DATABASE_URL == "sqlite:///data/mle_prep.db"
    assert s.LLM_MODEL == "claude-sonnet-4-20250514"
    assert s.LLM_BACKEND == "auto"
    assert s.CORS_ORIGINS == ["http://localhost:5173"]
    assert s.DEBUG is True


def test_get_settings(monkeypatch):
    """get_settings() returns a valid Settings instance."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")

    from src.backend.config import get_settings

    s = get_settings()
    assert s.ANTHROPIC_API_KEY == "sk-test-key"


def test_settings_cors_origins_from_env(monkeypatch):
    """CORS_ORIGINS can be set from environment variable."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173"]')

    from src.backend.config import Settings

    s = Settings(_env_file=None)
    assert len(s.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in s.CORS_ORIGINS
