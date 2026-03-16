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


class SynthesizeResponse(BaseModel):
    """Response with audio URL after synthesis."""

    audio_url: str
    cache_hit: bool
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
    chunks: list[str]
    content_hash: str
    total_chars: int
