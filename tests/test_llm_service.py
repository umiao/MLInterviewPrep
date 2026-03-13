"""Tests for LLM service (mocked)."""
import json
from unittest.mock import MagicMock, patch


def test_chat_text_response():
    """chat returns text string for text format."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello world")]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key")
        result = llm.chat("system", [{"role": "user", "content": "hi"}])

    assert result == "Hello world"
    mock_client.messages.create.assert_called_once()


def test_chat_json_response():
    """chat returns parsed dict for json format."""
    data = {"verdict": "optimal", "feedback": "Good"}
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(data))]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key")
        result = llm.chat("system", [{"role": "user", "content": "hi"}], response_format="json")

    assert result == data


def test_chat_invalid_json():
    """Invalid JSON returns error dict with raw text."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="not json {")]

    with patch("src.backend.services.llm_service.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key")
        result = llm.chat("system", [{"role": "user", "content": "hi"}], response_format="json")

    assert "error" in result
    assert "raw" in result


def test_chat_api_error():
    """API exception returns error dict."""
    with patch("src.backend.services.llm_service.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("API down")
        mock_cls.return_value = mock_client

        from src.backend.services.llm_service import LLMService

        llm = LLMService(api_key="test-key")
        result = llm.chat("system", [{"role": "user", "content": "hi"}])

    assert "error" in result
    assert "API down" in result["error"]
