"""Reading/TTS router -- queue, progress, content, and synthesis endpoints."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.reading import AudioCache, ReadingProgress, ReadingSession
from src.backend.schemas.reading import (
    ContentResponse,
    ListeningStatsResponse,
    ProgressResponse,
    ProgressUpdateRequest,
    QueueItemResponse,
    QueueResponse,
    SessionCloseRequest,
    SessionCreateRequest,
    SessionResponse,
    SummaryRequest,
    SummaryResponse,
    SynthesizeAsyncResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    TranscriptResponse,
)
from src.backend.services.content_pipeline import (
    VALID_CONTENT_TYPES,
    chunk_text,
    compute_content_hash,
    generate_tts_summary,
    get_cached_summary,
    get_cached_transcript,
    get_content_text,
    get_or_create_transcript,
    get_reading_queue,
    preprocess_for_tts,
)
from src.backend.services.tts_engine import (
    compute_cache_key,
    get_cached_path,
    synthesize_with_fallback,
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
    days_until_interview: int | None = Query(None, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> QueueResponse:
    """Return a ranked reading queue with progress information.

    When company_ids and days_until_interview are omitted, the queue
    auto-detects upcoming interviews and prioritizes accordingly.
    Prep notes for companies with interviews < 3 days away appear first.

    Args:
        db: Database session.
        company_ids: Comma-separated list of company IDs to prioritize.
            When omitted, auto-detects from upcoming interview events.
        days_until_interview: Days until next interview for urgency calc.
            When omitted, auto-detects from soonest interview event.
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

    kwargs: dict = {
        "company_ids": parsed_ids,
        "limit": limit,
    }
    if days_until_interview is not None:
        kwargs["days_until_interview"] = days_until_interview

    items = get_reading_queue(db, **kwargs)

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
    cached_tr = get_cached_transcript(db, content_type, content_id)
    summary = cached_tr.transcript_text if cached_tr else None
    # Use transcript for chunks if available, otherwise preprocessed text
    text_for_chunks = summary if summary else preprocessed
    chunks = chunk_text(text_for_chunks)
    content_hash = compute_content_hash(raw_text)

    return ContentResponse(
        content_type=content_type,
        content_id=content_id,
        raw_text=raw_text,
        preprocessed_text=preprocessed,
        summary_text=summary,
        chunks=chunks,
        content_hash=content_hash,
        total_chars=len(text_for_chunks),
    )


# -----------------------------------------------------------------------
# POST /reading/summary -- generate or retrieve TTS summary
# -----------------------------------------------------------------------
@router.post("/reading/summary", response_model=SummaryResponse)
async def get_or_generate_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """Generate or retrieve a cached LLM-optimized TTS summary.

    If a valid cached summary exists, returns it immediately.
    Otherwise, calls the LLM to generate one, caches it, and returns it.
    Falls back to preprocessed raw text when the LLM is unavailable.

    Args:
        request: Summary request with content type and ID.
        db: Database session.

    Returns:
        TTS-optimized summary text with cache status.
    """
    _validate_content_type(request.content_type)

    # Check cache first
    cached = get_cached_summary(db, request.content_type, request.content_id)
    if cached is not None:
        return SummaryResponse(
            content_type=request.content_type,
            content_id=request.content_id,
            summary_text=cached,
            from_cache=True,
            total_chars=len(cached),
        )

    # Generate via LLM (or fallback)
    summary = await generate_tts_summary(db, request.content_type, request.content_id)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail=f"{request.content_type} with id {request.content_id} not found",
        )

    return SummaryResponse(
        content_type=request.content_type,
        content_id=request.content_id,
        summary_text=summary,
        from_cache=False,
        total_chars=len(summary),
    )


# -----------------------------------------------------------------------
# GET /reading/transcript/{content_type}/{content_id} -- get/generate transcript
# -----------------------------------------------------------------------
@router.get(
    "/reading/transcript/{content_type}/{content_id}",
    response_model=TranscriptResponse,
)
async def get_transcript(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
) -> TranscriptResponse:
    """Return a faithful spoken-word transcript (generates on demand, no audio).

    Args:
        content_type: Content type string.
        content_id: ID of the content item.
        db: Database session.

    Returns:
        Transcript text with generation metadata.
    """
    _validate_content_type(content_type)
    _get_raw_text_or_404(db, content_type, content_id)

    result = await get_or_create_transcript(db, content_type, content_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"{content_type} with id {content_id} not found",
        )

    return TranscriptResponse(
        content_type=content_type,
        content_id=content_id,
        transcript_text=result.transcript_text,
        transcript_hash=result.transcript_hash,
        generation_method=result.generation_method,
        from_cache=result.from_cache,
        total_chars=len(result.transcript_text),
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

    # Prefer cached transcript over raw preprocessed text
    cached_tr = get_cached_transcript(db, request.content_type, request.content_id)
    processed_text = cached_tr.transcript_text if cached_tr else preprocess_for_tts(raw_text)
    transcript_hash = cached_tr.transcript_hash if cached_tr else compute_content_hash(processed_text)

    if not processed_text.strip():
        raise HTTPException(status_code=400, detail="No speakable text after preprocessing")

    from src.backend.config import get_settings
    from src.backend.services.tts_engine import get_tts_engine

    settings = get_settings()
    engine_name = request.engine or settings.TTS_ENGINE
    engine = get_tts_engine(engine_name)
    voice = request.voice or settings.TTS_VOICE
    rate = request.rate or settings.TTS_RATE
    content_hash = transcript_hash

    # Browser engine: return text immediately, no caching needed
    if engine.name == "browser":
        return SynthesizeResponse(
            mode="browser",
            text=processed_text,
            content_length=len(processed_text),
        )

    # Check AudioCache model for existing cache entry
    cache_entry = (
        db.query(AudioCache)
        .filter(
            AudioCache.content_type == request.content_type,
            AudioCache.content_id == request.content_id,
            AudioCache.engine == engine.name,
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
                result = await synthesize_with_fallback(
                    processed_text, voice=voice, rate=rate, engine_name=engine_name,
                )
                if result.mode == "browser":
                    _jobs[job_id]["status"] = "completed"
                    _jobs[job_id]["mode"] = "browser"
                    _jobs[job_id]["text"] = result.text
                else:
                    audio_url = f"/api/reading/audio/{result.file_path.stem}"
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
    result = await synthesize_with_fallback(
        processed_text, voice=voice, rate=rate, engine_name=engine_name,
    )

    # Browser fallback case
    if result.mode == "browser":
        return SynthesizeResponse(
            mode="browser",
            text=result.text,
            content_length=len(processed_text),
        )

    # Upsert AudioCache entry
    if cache_entry is None:
        cache_entry = AudioCache(
            content_type=request.content_type,
            content_id=request.content_id,
            content_hash=content_hash,
            file_path=str(result.file_path),
            engine=engine.name,
            voice=voice,
        )
        db.add(cache_entry)
        db.commit()

    audio_url = f"/api/reading/audio/{result.file_path.stem}"
    return SynthesizeResponse(
        mode="file",
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


# -----------------------------------------------------------------------
# POST /reading/sessions -- create or close a listening session
# -----------------------------------------------------------------------
@router.post("/reading/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Create a new listening session.

    Args:
        request: Session creation request with optional TTS engine.
        db: Database session.

    Returns:
        The created session record.
    """
    session = ReadingSession(
        tts_engine=request.tts_engine,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=session.id,
        started_at=str(session.started_at),
        ended_at=None,
        content_items_read=session.content_items_read or 0,
        total_duration_seconds=session.total_duration_seconds or 0.0,
        tts_engine=session.tts_engine,
    )


@router.put("/reading/sessions/{session_id}", response_model=SessionResponse)
async def close_session(
    session_id: int,
    request: SessionCloseRequest,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """Close an existing listening session with final stats.

    Args:
        session_id: ID of the session to close.
        request: Close request with items read and duration.
        db: Database session.

    Returns:
        The updated session record.
    """
    session = db.query(ReadingSession).filter(ReadingSession.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = datetime.now(UTC)
    session.content_items_read = request.content_items_read
    session.total_duration_seconds = request.total_duration_seconds
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=session.id,
        started_at=str(session.started_at),
        ended_at=str(session.ended_at) if session.ended_at else None,
        content_items_read=session.content_items_read or 0,
        total_duration_seconds=session.total_duration_seconds or 0.0,
        tts_engine=session.tts_engine,
    )


# -----------------------------------------------------------------------
# GET /reading/stats -- aggregated listening statistics
# -----------------------------------------------------------------------
@router.get("/reading/stats", response_model=ListeningStatsResponse)
async def get_listening_stats(
    db: Session = Depends(get_db),
) -> ListeningStatsResponse:
    """Return aggregated listening statistics.

    Computes total sessions, listening time, items count,
    today's stats, and a streak of consecutive days with sessions.

    Args:
        db: Database session.

    Returns:
        Aggregated listening stats.
    """
    from datetime import date, timedelta

    all_sessions = db.query(ReadingSession).all()
    total_sessions = len(all_sessions)
    total_seconds = sum(s.total_duration_seconds or 0.0 for s in all_sessions)
    total_items = sum(s.content_items_read or 0 for s in all_sessions)

    # Today's stats
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = [
        s for s in all_sessions
        if s.started_at and _to_aware(s.started_at) >= today_start
    ]
    sessions_today = len(today_sessions)
    listening_seconds_today = sum(s.total_duration_seconds or 0.0 for s in today_sessions)

    # Streak: count consecutive days backward from today with at least one session
    session_dates: set[date] = set()
    for s in all_sessions:
        if s.started_at:
            session_dates.add(_to_aware(s.started_at).date())

    streak = 0
    check_date = datetime.now(UTC).date()
    while check_date in session_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return ListeningStatsResponse(
        total_sessions=total_sessions,
        total_listening_seconds=total_seconds,
        total_items_listened=total_items,
        sessions_today=sessions_today,
        listening_seconds_today=listening_seconds_today,
        streak_days=streak,
    )


def _to_aware(dt: datetime) -> datetime:
    """Convert a naive datetime to UTC-aware.

    Args:
        dt: Datetime that may be naive or aware.

    Returns:
        UTC-aware datetime.
    """

    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt
