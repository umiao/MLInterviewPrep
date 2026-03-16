"""Reading/TTS router -- queue, progress, content, and synthesis endpoints."""
from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.reading import AudioCache, ReadingProgress
from src.backend.schemas.reading import (
    ContentResponse,
    ProgressResponse,
    ProgressUpdateRequest,
    QueueItemResponse,
    QueueResponse,
    SynthesizeAsyncResponse,
    SynthesizeRequest,
    SynthesizeResponse,
)
from src.backend.services.content_pipeline import (
    VALID_CONTENT_TYPES,
    chunk_text,
    compute_content_hash,
    get_content_text,
    get_reading_queue,
    preprocess_for_tts,
)
from src.backend.services.tts_engine import (
    compute_cache_key,
    get_cached_path,
    synthesize_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reading"])

# In-memory async job store (simple dict for MVP; no persistence needed)
_jobs: dict[str, dict] = {}

# Threshold for async synthesis (characters)
ASYNC_THRESHOLD = 2000


def _validate_content_type(content_type: str) -> None:
    """Raise 400 if content_type is invalid.

    Args:
        content_type: The content type string to validate.

    Raises:
        HTTPException: If content_type not in VALID_CONTENT_TYPES.
    """
    if content_type not in VALID_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type: {content_type}. "
            f"Must be one of: {', '.join(sorted(VALID_CONTENT_TYPES))}",
        )


def _get_raw_text_or_404(db: Session, content_type: str, content_id: int) -> str:
    """Retrieve raw text for a content item, raising 404 if not found.

    Args:
        db: Database session.
        content_type: Content type string.
        content_id: Primary key of the content item.

    Returns:
        Raw text content.

    Raises:
        HTTPException: 404 if item not found, 400 if no text.
    """
    text = get_content_text(db, content_type, content_id)
    if text is None:
        raise HTTPException(
            status_code=404,
            detail=f"{content_type} with id {content_id} not found",
        )
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail=f"{content_type} with id {content_id} has no readable content",
        )
    return text


# -----------------------------------------------------------------------
# GET /reading/queue -- ranked reading queue with progress
# -----------------------------------------------------------------------
@router.get("/reading/queue", response_model=QueueResponse)
async def get_queue(
    db: Session = Depends(get_db),
    company_ids: str | None = Query(None, description="Comma-separated company IDs"),
    days_until_interview: int = Query(30, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> QueueResponse:
    """Return a ranked reading queue with progress information.

    Args:
        db: Database session.
        company_ids: Comma-separated list of company IDs to prioritize.
        days_until_interview: Days until next interview for urgency calc.
        limit: Maximum items to return.

    Returns:
        Ranked queue items with progress.
    """
    parsed_ids: list[int] | None = None
    if company_ids:
        try:
            parsed_ids = [int(x.strip()) for x in company_ids.split(",") if x.strip()]
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="company_ids must be comma-separated integers",
            ) from exc

    items = get_reading_queue(
        db,
        company_ids=parsed_ids,
        days_until_interview=days_until_interview,
        limit=limit,
    )

    response_items = [
        QueueItemResponse(
            content_type=item.content_type,
            content_id=item.content_id,
            title=item.title,
            urgency=item.urgency,
            total_chars=item.total_chars,
            last_chunk_index=item.last_chunk_index,
            char_offset=item.char_offset,
            completed=item.completed,
        )
        for item in items
    ]

    return QueueResponse(items=response_items, total=len(response_items))


# -----------------------------------------------------------------------
# GET /reading/progress -- all progress records
# -----------------------------------------------------------------------
@router.get("/reading/progress", response_model=list[ProgressResponse])
async def get_all_progress(
    db: Session = Depends(get_db),
) -> list[ProgressResponse]:
    """Return all reading progress records.

    Args:
        db: Database session.

    Returns:
        List of progress records.
    """
    rows = db.query(ReadingProgress).all()
    return [
        ProgressResponse(
            id=r.id,
            content_type=r.content_type,
            content_id=r.content_id,
            last_chunk_index=r.last_chunk_index or 0,
            char_offset=r.char_offset or 0,
            total_chars=r.total_chars or 0,
            completed=r.completed or False,
        )
        for r in rows
    ]


# -----------------------------------------------------------------------
# PUT /reading/progress/{content_type}/{content_id} -- update progress
# -----------------------------------------------------------------------
@router.put(
    "/reading/progress/{content_type}/{content_id}",
    response_model=ProgressResponse,
)
async def update_progress(
    content_type: str,
    content_id: int,
    request: ProgressUpdateRequest,
    db: Session = Depends(get_db),
) -> ProgressResponse:
    """Create or update reading progress for a content item.

    Args:
        content_type: Content type (framework_node, prep_notes, interview_question).
        content_id: ID of the content item.
        request: Progress update data.
        db: Database session.

    Returns:
        Updated progress record.
    """
    _validate_content_type(content_type)

    progress = (
        db.query(ReadingProgress)
        .filter(
            ReadingProgress.content_type == content_type,
            ReadingProgress.content_id == content_id,
        )
        .first()
    )

    if progress is None:
        progress = ReadingProgress(
            content_type=content_type,
            content_id=content_id,
        )
        db.add(progress)

    progress.last_chunk_index = request.last_chunk_index
    progress.char_offset = request.char_offset
    progress.total_chars = request.total_chars
    progress.completed = request.completed

    db.commit()
    db.refresh(progress)

    return ProgressResponse(
        id=progress.id,
        content_type=progress.content_type,
        content_id=progress.content_id,
        last_chunk_index=progress.last_chunk_index or 0,
        char_offset=progress.char_offset or 0,
        total_chars=progress.total_chars or 0,
        completed=progress.completed or False,
    )


# -----------------------------------------------------------------------
# DELETE /reading/progress -- reset all progress
# -----------------------------------------------------------------------
@router.delete("/reading/progress")
async def reset_progress(
    db: Session = Depends(get_db),
) -> Response:
    """Delete all reading progress records (reset).

    Args:
        db: Database session.

    Returns:
        204 No Content response.
    """
    db.query(ReadingProgress).delete()
    db.commit()
    return Response(status_code=204)


# -----------------------------------------------------------------------
# GET /reading/content/{content_type}/{content_id} -- preprocessed + chunks
# -----------------------------------------------------------------------
@router.get(
    "/reading/content/{content_type}/{content_id}",
    response_model=ContentResponse,
)
async def get_content(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
) -> ContentResponse:
    """Return preprocessed text and chunks for a content item.

    Args:
        content_type: Content type string.
        content_id: ID of the content item.
        db: Database session.

    Returns:
        Raw text, preprocessed text, chunks, and content hash.
    """
    _validate_content_type(content_type)
    raw_text = _get_raw_text_or_404(db, content_type, content_id)
    preprocessed = preprocess_for_tts(raw_text)
    chunks = chunk_text(preprocessed)
    content_hash = compute_content_hash(raw_text)

    return ContentResponse(
        content_type=content_type,
        content_id=content_id,
        raw_text=raw_text,
        preprocessed_text=preprocessed,
        chunks=chunks,
        content_hash=content_hash,
        total_chars=len(preprocessed),
    )


# -----------------------------------------------------------------------
# POST /reading/synthesize -- cache-aware synthesis with async for long content
# -----------------------------------------------------------------------
@router.post("/reading/synthesize", response_model=SynthesizeResponse, responses={202: {"model": SynthesizeAsyncResponse}})
async def synthesize(
    request: SynthesizeRequest,
    db: Session = Depends(get_db),
) -> SynthesizeResponse | SynthesizeAsyncResponse:
    """Synthesize content to speech and return audio URL.

    For short content (<2000 chars), returns audio URL synchronously.
    For long content (>=2000 chars), returns 202 + job_id for polling.

    Uses AudioCache model for cache-aware synthesis with content_hash
    invalidation.

    Args:
        request: Synthesis request with content type and ID.
        db: Database session.

    Returns:
        Audio URL and metadata (200), or job ID (202).
    """
    _validate_content_type(request.content_type)
    raw_text = _get_raw_text_or_404(db, request.content_type, request.content_id)
    processed_text = preprocess_for_tts(raw_text)

    if not processed_text.strip():
        raise HTTPException(status_code=400, detail="No speakable text after preprocessing")

    from src.backend.config import get_settings

    settings = get_settings()
    voice = request.voice or settings.TTS_VOICE
    rate = request.rate or settings.TTS_RATE
    content_hash = compute_content_hash(raw_text)

    # Check AudioCache model for existing cache entry
    cache_entry = (
        db.query(AudioCache)
        .filter(
            AudioCache.content_type == request.content_type,
            AudioCache.content_id == request.content_id,
            AudioCache.engine == "edge_tts",
            AudioCache.voice == voice,
        )
        .first()
    )

    # If cache entry exists but hash differs, content changed -> invalidate
    if cache_entry and cache_entry.content_hash != content_hash:
        db.delete(cache_entry)
        db.commit()
        cache_entry = None

    # Check file-level cache
    cache_key = compute_cache_key(processed_text, voice, rate)
    cached_path = get_cached_path(cache_key)
    cache_hit = (
        cache_entry is not None
        and cached_path.exists()
        and cached_path.stat().st_size > 0
    )

    # Async mode for long content
    if len(processed_text) >= ASYNC_THRESHOLD and not cache_hit:
        job_id = str(uuid.uuid4())
        _jobs[job_id] = {"status": "pending", "audio_url": None, "error": None}

        async def _run_synthesis() -> None:
            """Background synthesis task."""
            try:
                mp3_path = await synthesize_text(processed_text, voice=voice, rate=rate)
                audio_url = f"/api/reading/audio/{mp3_path.stem}"
                _jobs[job_id]["status"] = "completed"
                _jobs[job_id]["audio_url"] = audio_url
            except Exception as exc:
                logger.error("Async synthesis failed for job %s: %s", job_id, exc)
                _jobs[job_id]["status"] = "failed"
                _jobs[job_id]["error"] = str(exc)

        asyncio.create_task(_run_synthesis())

        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=202,
            content=SynthesizeAsyncResponse(
                job_id=job_id,
                status="pending",
                content_length=len(processed_text),
            ).model_dump(),
        )

    # Synchronous synthesis (short content or cache hit)
    mp3_path = await synthesize_text(processed_text, voice=voice, rate=rate)

    # Upsert AudioCache entry
    if cache_entry is None:
        cache_entry = AudioCache(
            content_type=request.content_type,
            content_id=request.content_id,
            content_hash=content_hash,
            file_path=str(mp3_path),
            engine="edge_tts",
            voice=voice,
        )
        db.add(cache_entry)
        db.commit()

    audio_url = f"/api/reading/audio/{mp3_path.stem}"
    return SynthesizeResponse(
        audio_url=audio_url,
        cache_hit=cache_hit,
        content_length=len(processed_text),
    )


# -----------------------------------------------------------------------
# GET /reading/jobs/{job_id} -- poll async synthesis job
# -----------------------------------------------------------------------
@router.get("/reading/jobs/{job_id}")
async def get_job_status(job_id: str) -> dict:
    """Poll status of an async synthesis job.

    Args:
        job_id: UUID of the synthesis job.

    Returns:
        Job status dict with status, audio_url (if completed), error (if failed).
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "audio_url": job.get("audio_url"),
        "error": job.get("error"),
    }


# -----------------------------------------------------------------------
# GET /reading/audio/{cache_key} -- serve cached MP3
# -----------------------------------------------------------------------
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
