"""Tests for transcript generation: generation, caching, fallback, and deprecated wrappers."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode
from src.backend.models.reading import Transcript
from src.backend.services.content_pipeline import (
    CONTENT_TYPE_FRAMEWORK_NODE,
    CONTENT_TYPE_PREP_NOTES,
    TRANSCRIPT_PROMPT_VERSION,
    compute_content_hash,
    generate_transcript,
    generate_tts_summary,
    get_cached_summary,
    get_cached_transcript,
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
    """Mock LLMService returning a TTS-optimized transcript."""
    mock = MagicMock()
    mock.chat = AsyncMock(
        return_value="Neural networks are computational models inspired by the brain. "
        "They consist of layers of interconnected nodes. Key concepts include "
        "backpropagation, which is the backward pass, activation functions like "
        "rectified linear unit and sigmoid, and loss functions."
    )
    return mock


# ---------------------------------------------------------------------------
# generate_transcript tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio()
async def test_generate_transcript_calls_llm(db_session, seed_node_with_description, mock_llm_summary):
    """generate_transcript calls LLM and caches the result in Transcript table."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert "Neural networks" in result.transcript_text
    assert "backpropagation" in result.transcript_text
    assert result.generation_method == "llm"
    assert result.from_cache is False

    # Verify LLM was called
    mock_llm_summary.chat.assert_awaited_once()

    # Verify cached in Transcript table
    cached = db_session.query(Transcript).filter(
        Transcript.content_type == CONTENT_TYPE_FRAMEWORK_NODE,
        Transcript.content_id == node.id,
        Transcript.is_latest.is_(True),
    ).first()
    assert cached is not None
    assert cached.transcript_text == result.transcript_text
    assert cached.source_hash == compute_content_hash(node.description)
    assert cached.prompt_version == TRANSCRIPT_PROMPT_VERSION


@pytest.mark.asyncio()
async def test_generate_transcript_returns_cache_on_second_call(
    db_session, seed_node_with_description, mock_llm_summary,
):
    """Second call returns cached transcript without calling LLM again."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        first = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
        second = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert first.transcript_text == second.transcript_text
    assert second.from_cache is True
    # LLM called only once (second call uses cache)
    assert mock_llm_summary.chat.await_count == 1


@pytest.mark.asyncio()
async def test_generate_transcript_regenerates_on_content_change(
    db_session, seed_node_with_description, mock_llm_summary,
):
    """When content changes (hash mismatch), transcript is regenerated."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

        # Change the content
        node.description = "# Updated Content\n\nCompletely new material about CNNs."
        db_session.commit()

        mock_llm_summary.chat.return_value = "Updated transcript about convolutional neural networks."
        result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert "convolutional" in result.transcript_text
    assert mock_llm_summary.chat.await_count == 2

    # Old transcript should be marked as not latest
    old = db_session.query(Transcript).filter(
        Transcript.content_type == CONTENT_TYPE_FRAMEWORK_NODE,
        Transcript.content_id == node.id,
        Transcript.is_latest.is_(False),
    ).all()
    assert len(old) == 1


@pytest.mark.asyncio()
async def test_generate_transcript_fallback_on_llm_error(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM returns an error."""
    node = seed_node_with_description
    error_mock = MagicMock()
    error_mock.chat = AsyncMock(return_value={"error": "API rate limit exceeded"})

    with patch("src.backend.services.llm_service.LLMService", return_value=error_mock):
        result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert result.generation_method == "preprocess_fallback"
    expected = preprocess_for_tts(node.description)
    assert result.transcript_text == expected


@pytest.mark.asyncio()
async def test_generate_transcript_fallback_on_llm_exception(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM raises an exception."""
    node = seed_node_with_description
    exc_mock = MagicMock()
    exc_mock.chat = AsyncMock(side_effect=ConnectionError("Network error"))

    with patch("src.backend.services.llm_service.LLMService", return_value=exc_mock):
        result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert result.generation_method == "preprocess_fallback"
    expected = preprocess_for_tts(node.description)
    assert result.transcript_text == expected


@pytest.mark.asyncio()
async def test_generate_transcript_returns_none_for_missing_content(db_session):
    """Returns None when content item does not exist."""
    result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, 9999)
    assert result is None


@pytest.mark.asyncio()
async def test_generate_transcript_for_prep_notes(db_session, seed_company_with_notes, mock_llm_summary):
    """Works for prep_notes content type."""
    company = seed_company_with_notes
    mock_llm_summary.chat.return_value = "Review system design and machine learning basics."

    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        result = await generate_transcript(db_session, CONTENT_TYPE_PREP_NOTES, company.id)

    assert result is not None
    assert "system design" in result.transcript_text


@pytest.mark.asyncio()
async def test_generate_transcript_fallback_on_empty_llm_response(db_session, seed_node_with_description):
    """Falls back to preprocessed text when LLM returns empty string."""
    node = seed_node_with_description
    empty_mock = MagicMock()
    empty_mock.chat = AsyncMock(return_value="   ")

    with patch("src.backend.services.llm_service.LLMService", return_value=empty_mock):
        result = await generate_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert result.generation_method == "preprocess_fallback"
    expected = preprocess_for_tts(node.description)
    assert result.transcript_text == expected


# ---------------------------------------------------------------------------
# get_cached_transcript tests
# ---------------------------------------------------------------------------
def test_get_cached_transcript_returns_none_when_no_cache(db_session, seed_node_with_description):
    """Returns None when no cached transcript exists."""
    node = seed_node_with_description
    result = get_cached_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result is None


def test_get_cached_transcript_returns_cached(db_session, seed_node_with_description):
    """Returns cached transcript when source hash matches."""
    node = seed_node_with_description
    source_hash = compute_content_hash(node.description)
    transcript_text = "Cached transcript text."

    entry = Transcript(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        source_hash=source_hash,
        transcript_text=transcript_text,
        transcript_hash=compute_content_hash(transcript_text),
        generation_method="llm",
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=True,
    )
    db_session.add(entry)
    db_session.commit()

    result = get_cached_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result is not None
    assert result.transcript_text == "Cached transcript text."
    assert result.from_cache is True


def test_get_cached_transcript_returns_none_on_stale_hash(db_session, seed_node_with_description):
    """Returns None when source hash no longer matches (stale cache)."""
    node = seed_node_with_description

    entry = Transcript(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        source_hash="stale_hash_value",
        transcript_text="Old transcript.",
        transcript_hash=compute_content_hash("Old transcript."),
        generation_method="llm",
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=True,
    )
    db_session.add(entry)
    db_session.commit()

    result = get_cached_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result is None


def test_get_cached_transcript_returns_none_for_missing_content(db_session):
    """Returns None when content item does not exist."""
    result = get_cached_transcript(db_session, CONTENT_TYPE_FRAMEWORK_NODE, 9999)
    assert result is None


# ---------------------------------------------------------------------------
# Deprecated wrapper tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio()
async def test_generate_tts_summary_wrapper(db_session, seed_node_with_description, mock_llm_summary):
    """Deprecated generate_tts_summary returns transcript text as string."""
    node = seed_node_with_description
    with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm_summary):
        result = await generate_tts_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)

    assert result is not None
    assert isinstance(result, str)
    assert "Neural networks" in result


def test_get_cached_summary_wrapper(db_session, seed_node_with_description):
    """Deprecated get_cached_summary returns transcript text as string."""
    node = seed_node_with_description
    source_hash = compute_content_hash(node.description)
    transcript_text = "Cached via wrapper."

    entry = Transcript(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        source_hash=source_hash,
        transcript_text=transcript_text,
        transcript_hash=compute_content_hash(transcript_text),
        generation_method="llm",
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=True,
    )
    db_session.add(entry)
    db_session.commit()

    result = get_cached_summary(db_session, CONTENT_TYPE_FRAMEWORK_NODE, node.id)
    assert result == "Cached via wrapper."


# ---------------------------------------------------------------------------
# Transcript model constraint tests
# ---------------------------------------------------------------------------
def test_transcript_unique_constraint(db_session, seed_node_with_description):
    """Unique constraint on (content_type, content_id, source_hash, prompt_version)."""
    node = seed_node_with_description
    source_hash = compute_content_hash(node.description)

    entry1 = Transcript(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        source_hash=source_hash,
        transcript_text="Transcript 1.",
        transcript_hash=compute_content_hash("Transcript 1."),
        generation_method="llm",
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=True,
    )
    db_session.add(entry1)
    db_session.commit()

    entry2 = Transcript(
        content_type=CONTENT_TYPE_FRAMEWORK_NODE,
        content_id=node.id,
        source_hash=source_hash,
        transcript_text="Transcript 2.",
        transcript_hash=compute_content_hash("Transcript 2."),
        generation_method="llm",
        prompt_version=TRANSCRIPT_PROMPT_VERSION,
        is_latest=False,
    )
    db_session.add(entry2)
    with pytest.raises(IntegrityError):
        db_session.commit()
