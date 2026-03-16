"""Tests for LLM question extractor."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.backend.services.question_extractor import extract_questions


@pytest.mark.asyncio
async def test_valid_extraction():
    """Valid LLM response returns question list."""
    mock_llm = MagicMock()
    mock_llm.chat = AsyncMock(return_value=[
        {"question_text": "Design a rec system", "question_type": "ml_system_design"},
        {"question_text": "Implement LRU cache", "question_type": "coding"},
    ])

    result = await extract_questions(mock_llm, "Interview text...")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_llm_error_returns_empty():
    """LLM error returns empty list."""
    mock_llm = MagicMock()
    mock_llm.chat = AsyncMock(return_value={"error": "API failed"})

    result = await extract_questions(mock_llm, "text")
    assert result == []


@pytest.mark.asyncio
async def test_missing_fields_filtered():
    """Questions missing required fields are filtered out."""
    mock_llm = MagicMock()
    mock_llm.chat = AsyncMock(return_value=[
        {"question_text": "Valid Q", "question_type": "coding"},
        {"question_text": "Missing type"},  # no question_type
        {"question_type": "coding"},  # no question_text
    ])

    result = await extract_questions(mock_llm, "text")
    assert len(result) == 1
    assert result[0]["question_text"] == "Valid Q"


@pytest.mark.asyncio
async def test_source_context_prepended():
    """Source context added to user message."""
    mock_llm = MagicMock()
    mock_llm.chat = AsyncMock(return_value=[])

    await extract_questions(mock_llm, "text", {"company": "Google", "role": "MLE"})

    call_args = mock_llm.chat.call_args
    user_msg = call_args[1]["messages"][0]["content"]
    assert "Google" in user_msg
    assert "MLE" in user_msg
