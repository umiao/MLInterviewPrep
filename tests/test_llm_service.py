"""Tests for LLM service (mocked)."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_chat_text_response():
    """chat returns text string for text format."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello world")]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls, \
         patch("src.backend.services.llm_service.SDK_AVAILABLE", False):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key", backend="anthropic")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert result == "Hello world"
    mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_chat_json_response():
    """chat returns parsed dict for json format."""
    data = {"verdict": "optimal", "feedback": "Good"}
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(data))]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls, \
         patch("src.backend.services.llm_service.SDK_AVAILABLE", False):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key", backend="anthropic")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}], response_format="json")

    assert result == data


@pytest.mark.asyncio
async def test_chat_invalid_json():
    """Invalid JSON returns error dict with raw text."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="not json {")]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls, \
         patch("src.backend.services.llm_service.SDK_AVAILABLE", False):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key", backend="anthropic")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}], response_format="json")

    assert "error" in result
    assert "raw" in result


@pytest.mark.asyncio
async def test_chat_api_error():
    """API exception returns error dict."""
    with patch("src.backend.services.llm_service.Anthropic") as mock_cls, \
         patch("src.backend.services.llm_service.SDK_AVAILABLE", False):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("API down")
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key", backend="anthropic")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert "error" in result
    assert "API down" in result["error"]


@pytest.mark.asyncio
async def test_chat_sdk_backend():
    """SDK backend calls run_query and returns text."""
    with patch("src.backend.services.llm_service.SDK_AVAILABLE", True), \
         patch("src.backend.services.llm_service.run_query", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = "SDK response"

        from src.backend.services.llm_service import LLMService

        llm = LLMService(backend="sdk")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert result == "SDK response"
    mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_chat_sdk_json_response():
    """SDK backend parses JSON response."""
    data = {"answer": "42"}
    with patch("src.backend.services.llm_service.SDK_AVAILABLE", True), \
         patch("src.backend.services.llm_service.run_query", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = json.dumps(data)

        from src.backend.services.llm_service import LLMService

        llm = LLMService(backend="sdk")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}], response_format="json")

    assert result == data


@pytest.mark.asyncio
async def test_chat_sdk_error():
    """SDK backend returns error dict on exception."""
    with patch("src.backend.services.llm_service.SDK_AVAILABLE", True), \
         patch("src.backend.services.llm_service.run_query", new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = RuntimeError("SDK failure")

        from src.backend.services.llm_service import LLMService

        llm = LLMService(backend="sdk")
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert "error" in result
    assert "SDK failure" in result["error"]


@pytest.mark.asyncio
async def test_auto_backend_selects_sdk_when_available():
    """Auto backend selects SDK when available."""
    with patch("src.backend.services.llm_service.SDK_AVAILABLE", True), \
         patch("src.backend.services.llm_service.run_query", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = "auto-sdk"

        from src.backend.services.llm_service import LLMService

        llm = LLMService(backend="auto")
        assert llm.actual_backend == "sdk"
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert result == "auto-sdk"


@pytest.mark.asyncio
async def test_auto_backend_falls_back_to_anthropic():
    """Auto backend falls back to anthropic when SDK unavailable."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="fallback")]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls, \
         patch("src.backend.services.llm_service.SDK_AVAILABLE", False):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key", backend="auto")
        assert llm.actual_backend == "anthropic"
        result = await llm.chat("system", [{"role": "user", "content": "hi"}])

    assert result == "fallback"


@pytest.mark.asyncio
async def test_max_tokens_warning_sdk(caplog):
    """SDK backend logs warning when non-default max_tokens is used."""
    import logging

    # Reset warning flag
    from src.backend.services.llm_service import LLMService
    LLMService._max_tokens_warning_logged = False

    with patch("src.backend.services.llm_service.SDK_AVAILABLE", True), \
         patch("src.backend.services.llm_service.run_query", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = "ok"

        llm = LLMService(backend="sdk")
        with caplog.at_level(logging.WARNING, logger="src.backend.services.llm_service"):
            await llm.chat("system", [{"role": "user", "content": "hi"}], max_tokens=2048)

    assert "max_tokens" in caplog.text
    # Reset for other tests
    LLMService._max_tokens_warning_logged = False


def test_sdk_adapter_exports():
    """sdk_adapter exports SDK_AVAILABLE and run_query."""
    from src.backend.services.sdk_adapter import SDK_AVAILABLE, run_query

    assert isinstance(SDK_AVAILABLE, bool)
    assert callable(run_query)


def test_config_defaults():
    """Config has correct defaults for new settings."""
    from src.backend.config import Settings

    s = Settings(ANTHROPIC_API_KEY="")
    assert s.ANTHROPIC_API_KEY == ""
    assert s.LLM_BACKEND == "auto"
