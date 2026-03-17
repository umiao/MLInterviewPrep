"""Pydantic schemas for Reading/TTS endpoints."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Valid content types across all reading endpoints
ContentType = Literal["framework_node", "prep_notes", "interview_question"]


class SynthesizeRequest(BaseModel):
    """Request to synthesize text-to-speech for a content item."""

    content_type: ContentType
    content_id: int
    voice: str | None = None
    rate: str | None = None
    engine: str | None = None


class SynthesizeResponse(BaseModel):
    """Response with audio URL after synthesis."""

    mode: str = Field(description="'file' for audio URL, 'browser' for client-side TTS")
    audio_url: str | None = None
    text: str | None = None
    cache_hit: bool = False
    content_length: int = Field(description="Length of preprocessed text in characters")


class SynthesizeAsyncResponse(BaseModel):
    """Response for async synthesis of long content (202 Accepted)."""

    job_id: str
    status: str = "pending"
    content_length: int = Field(description="Length of preprocessed text in characters")


class QueueItemResponse(BaseModel):
    """A single item in the reading queue."""

    model_config = ConfigDict(from_attributes=True)

    content_type: str
    content_id: int
    title: str
    urgency: float
    total_chars: int
    last_chunk_index: int = 0
    char_offset: int = 0
    completed: bool = False


class QueueResponse(BaseModel):
    """Ranked reading queue response."""

    items: list[QueueItemResponse]
    total: int


class ProgressResponse(BaseModel):
    """Reading progress for a content item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    content_type: str
    content_id: int
    last_chunk_index: int
    char_offset: int
    total_chars: int
    completed: bool


class ProgressUpdateRequest(BaseModel):
    """Request to update reading progress."""

    last_chunk_index: int = Field(ge=0)
    char_offset: int = Field(ge=0)
    total_chars: int = Field(ge=0, default=0)
    completed: bool = False


class ContentResponse(BaseModel):
    """Preprocessed text content with chunks for a content item."""

    content_type: str
    content_id: int
    raw_text: str
    preprocessed_text: str
    summary_text: str | None = Field(None, description="LLM-generated TTS summary if available")
    chunks: list[str]
    content_hash: str
    total_chars: int


class SummaryRequest(BaseModel):
    """Request to generate or retrieve a TTS summary for a content item."""

    content_type: ContentType
    content_id: int


class SummaryResponse(BaseModel):
    """Response with TTS-optimized summary text."""

    content_type: str
    content_id: int
    summary_text: str
    from_cache: bool = Field(description="True if returned from cache without LLM call")
    total_chars: int = Field(description="Length of summary text in characters")


class SessionCreateRequest(BaseModel):
    """Request to start a new listening session."""

    tts_engine: str | None = None


class SessionCloseRequest(BaseModel):
    """Request to close an active listening session."""

    session_id: int
    content_items_read: int = Field(ge=0, default=0)
    total_duration_seconds: float = Field(ge=0.0, default=0.0)


class SessionResponse(BaseModel):
    """Response for a listening session."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: str
    ended_at: str | None = None
    content_items_read: int
    total_duration_seconds: float
    tts_engine: str | None = None


class ListeningStatsResponse(BaseModel):
    """Aggregated listening statistics."""

    total_sessions: int = Field(description="Total number of listening sessions")
    total_listening_seconds: float = Field(description="Sum of all session durations in seconds")
    total_items_listened: int = Field(description="Sum of items across all sessions")
    sessions_today: int = Field(description="Sessions started today")
    listening_seconds_today: float = Field(description="Listening duration today in seconds")
    streak_days: int = Field(description="Consecutive days with at least one session")


class TranscriptResponse(BaseModel):
    """Response with faithful spoken-word transcript."""

    content_type: str
    content_id: int
    transcript_text: str
    transcript_hash: str
    generation_method: str = Field(description="'llm' or 'preprocess_fallback'")
    from_cache: bool = Field(description="True if returned from cache without LLM call")
    total_chars: int = Field(description="Length of transcript text in characters")
