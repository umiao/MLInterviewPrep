"""Reading/TTS router -- synthesize framework node descriptions to audio."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.framework import FrameworkNode
from src.backend.schemas.reading import SynthesizeRequest, SynthesizeResponse
from src.backend.services.content_pipeline import preprocess_for_tts
from src.backend.services.tts_engine import (
    compute_cache_key,
    get_cached_path,
    synthesize_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reading"])


def _get_content_text(db: Session, content_type: str, content_id: int) -> str:
    """Retrieve raw text content for a given content type and ID.

    Args:
        db: Database session.
        content_type: Type of content (currently only 'framework_node').
        content_id: ID of the content item.

    Returns:
        Raw text content.

    Raises:
        HTTPException: If content not found or has no text.
    """
    if content_type == "framework_node":
        node = db.query(FrameworkNode).filter(FrameworkNode.id == content_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Framework node not found")
        text = node.description or ""
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Framework node has no description to read",
            )
        # Prepend title for context
        return f"{node.title}.\n\n{text}"

    raise HTTPException(status_code=400, detail=f"Unknown content type: {content_type}")


@router.post("/reading/synthesize", response_model=SynthesizeResponse)
async def synthesize(
    request: SynthesizeRequest,
    db: Session = Depends(get_db),
) -> SynthesizeResponse:
    """Synthesize content to speech and return audio URL.

    Args:
        request: Synthesis request with content type and ID.
        db: Database session.

    Returns:
        Audio URL and metadata.
    """
    raw_text = _get_content_text(db, request.content_type, request.content_id)
    processed_text = preprocess_for_tts(raw_text)

    if not processed_text.strip():
        raise HTTPException(status_code=400, detail="No speakable text after preprocessing")

    # Check cache before synthesizing
    from src.backend.config import get_settings

    settings = get_settings()
    voice = request.voice or settings.TTS_VOICE
    rate = request.rate or settings.TTS_RATE
    cache_key = compute_cache_key(processed_text, voice, rate)
    cached = get_cached_path(cache_key)
    cache_hit = cached.exists() and cached.stat().st_size > 0

    mp3_path = await synthesize_text(processed_text, voice=request.voice, rate=request.rate)

    audio_url = f"/api/reading/audio/{mp3_path.stem}"
    return SynthesizeResponse(
        audio_url=audio_url,
        cache_hit=cache_hit,
        content_length=len(processed_text),
    )


@router.get("/reading/audio/{cache_key}")
async def get_audio(cache_key: str) -> FileResponse:
    """Serve a cached MP3 audio file.

    Args:
        cache_key: Cache key (SHA-256 hex digest) of the audio file.

    Returns:
        MP3 file response.
    """
    file_path = get_cached_path(cache_key)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        filename=f"{cache_key}.mp3",
    )
