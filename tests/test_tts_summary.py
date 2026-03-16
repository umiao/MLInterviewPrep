"""Tests for LLM-generated TTS summaries: generation, caching, fallback, and endpoints."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode
from src.backend.models.reading import TTSSummary
from src.backend.services.content_pipeline import (
    CONTENT_TYPE_FRAMEWORK_NODE,
    CONTENT_TYPE_PREP_NOTES,
    compute_content_hash,
    generate_tts_summary,
    get_cached_summary,
    preprocess_for_tts,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def seed_node_with_description(db_session):
    """Insert a framework node with a description for TTS."""
    node = FrameworkNode(
        path="pillar1.nn",
        depth=1,
        title="Neural Networks",
        importance=0.8,
        priority="P1",
        estimated_hours=10,
        description="# Neural Networks\n\nNeural networks are **computational models** "
        "inspired by the brain. They consist of layers of interconnected nodes.\n\n"
        "## Key Concepts\n\n- Backpropagation (i.e. backward pass)\n"
        "- Activation functions e.g. ReLU, sigmoid\n"
        "- Loss functions\n\n```python\nmodel = Sequential()\n```\n",
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return node


@pytest.fixture()
def seed_company_with_notes(db_session):
    """Insert a company with prep notes."""
    company = Company(name="TestCo", prep_notes="Study system design. Review ML basics.")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture()
def mock_llm_summary():
    """Mock LLMService returning a TTS-optimized summary."""
    mock = MagicMock()
    mock.chat = AsyncMock(
        return_value="Neural networks are computational models inspired by the brain. "
        "They consist of layers of interconnected nodes. Key concepts include "
        "backpropagation, which is the backward pass, activation functions like "
        "rectified linear unit and sigmoid, and loss functions."
    )
    return mock


# ---------------------------------------------------------------------------
# generate_tts_summary tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio()
async def test_generate_summary_calls_llm(db_session, seed_node_with_description, mock_llm_summary):
    """generate_tts_summary calls LLM and caches the result."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert "Neural networks" in result
    assert "backpropagation" in result

    # Verify LLM was called
    mock_llm_summary.chat.assert_awaited_once()

    # Verify cached in DB
    cached = db_session.query(TTSSummary).filter(
        TTSSummary.content_type == CONTENT_TYPE_FRAMEWORK_NODE,
        TTSSummary.content_id == node.id,
    ).first()
    assert cached is not None
    assert cached.summary_text == result
    assert cached.content_hash == compute_content_hash(node.description)


@pytest.mark.asyncio()
async def test_generate_summary_returns_cache_on_second_call(
    db_session, seed_node_with_description, mock_llm_summary,
):
    """Second call returns cached summary without calling LLM again."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        first = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
        second = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert first == second
    # LLM called only once (second call uses cache)
    assert mock_llm_summary.chat.await_count == 1


@pytest.mark.asyncio()
async def test_generate_summary_regenerates_on_content_change(
    db_session, seed_node_with_description, mock_llm_summary,
):
    """When content changes (hash mismatch), summary is regenerated."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

        # Change the content
        node.description = "# Updated Content\n\nCompletely new material about CNNs."
        db_session.commit()

        mock_llm_summary.chat.return_value = "Updated summary about convolutional neural networks."
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert "convolutional" in result
    assert mock_llm_summary.chat.await_count == 2


@pytest.mark.asyncio()
async def test_generate_summary_fallback_on_llm_error(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM returns an error."""
    node = seed_node_with_description
    error_mock = MagicMock()
    error_mock.chat = AsyncMock(return_value={"error": "API rate limit exceeded"})

    with patch("src.backend.services.llm_service.LLMService", return_value=error_mock):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    # Should be preprocessed text (fallback)
    expected = preprocess_for_tts(node.description)
    assert result == expected


@pytest.mark.asyncio()
async def test_generate_summary_fallback_on_llm_exception(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM raises an exception."""
    node = seed_node_with_description
    exc_mock = MagicMock()
    exc_mock.chat = AsyncMock(side_effect=ConnectionError("Network error"))

    with patch("src.backend.services.llm_service.LLMService", return_value=exc_mock):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    expected = preprocess_for_tts(node.description)
    assert result == expected


@pytest.mark.asyncio()
async def test_generate_summary_returns_none_for_missing_content(db_session):
    """Returns None when content item does not exist."""
    result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, 9999)
    assert result is None


@pytest.mark.asyncio()
async def test_generate_summary_for_prep_notes(db_session, seed_company_with_notes, mock_llm_summary):
    """Works for prep_notes content type."""
    company = seed_company_with_notes
    mock_llm_summary.chat.return_value = "Review system design and machine learning basics."

    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_PREP_NOTES, company.id)

    assert result is not None
    assert "system design" in result


@pytest.mark.asyncio()
async def test_generate_summary_fallback_on_empty_llm_response(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM returns empty string."""
    node = seed_node_with_description
    empty_mock = MagicMock()
    empty_mock.chat = AsyncMock(return_value="   ")

    with patch("src.backend.services.llm_service.LLMService", return_value=empty_mock):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    expected = preprocess_for_tts(node.description)
    assert result == expected


# ---------------------------------------------------------------------------
# get_cached_summary tests
# ---------------------------------------------------------------------------
def test_get_cached_summary_returns_none_when_no_cache(db_session, seed_node_with_description):
    """Returns None when no cached summary exists."""
    node = seed_node_with_description
    result = get_cached_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result is None


def test_get_cached_summary_returns_cached(db_session, seed_node_with_description):
    """Returns cached summary when hash matches."""
    node = seed_node_with_description
    content_hash = compute_content_hash(node.description)

    entry = TTSSummary(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        content_hash=content_hash,
        summary_text="Cached summary text.",
    )
    db_session.add(entry)
    db_session.commit()

    result = get_cached_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result == "Cached summary text."


def test_get_cached_summary_returns_none_on_stale_hash(db_session, seed_node_with_description):
    """Returns None when content hash no longer matches (stale cache)."""
    node = seed_node_with_description

    entry = TTSSummary(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        content_hash="stale_hash_value",
        summary_text="Old summary.",
    )
    db_session.add(entry)
    db_session.commit()

    result = get_cached_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result is None


def test_get_cached_summary_returns_none_for_missing_content(db_session):
    """Returns None when content item does not exist."""
    result = get_cached_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, 9999)
    assert result is None


# ---------------------------------------------------------------------------
# TTSSummary model tests
# ---------------------------------------------------------------------------
def test_tts_summary_unique_constraint(db_session, seed_node_with_description):
    """Unique constraint on (content_type, content_id) prevents duplicates."""
    node = seed_node_with_description
    entry1 = TTSSummary(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        content_hash="hash1",
        summary_text="Summary 1.",
    )
    db_session.add(entry1)
    db_session.commit()

    entry2 = TTSSummary(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        content_hash="hash2",
        summary_text="Summary 2.",
    )
    db_session.add(entry2)
    with pytest.raises(IntegrityError):
        db_session.commit()
