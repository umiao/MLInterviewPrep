"""Pydantic schemas for Reading/TTS endpoints."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SynthesizeRequest(BaseModel):
    """Request to synthesize text-to-speech for a content item."""

    content_type: Literal["framework_node"]
    content_id: int
    voice: str | None = None
    rate: str | None = None


class SynthesizeResponse(BaseModel):
    """Response with audio URL after synthesis."""

    audio_url: str
    cache_hit: bool
    content_length: int = Field(description="Length of preprocessed text in characters")
