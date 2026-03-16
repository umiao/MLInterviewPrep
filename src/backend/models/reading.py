"""Reading/TTS models: ReadingProgress, ReadingSession, AudioCache."""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from src.backend.database import Base


class ReadingProgress(Base):
    """Tracks reading/listening progress for a content item."""

    __tablename__ = "reading_progress"
    __table_args__ = (
        UniqueConstraint("content_type", "content_id", name="uq_reading_progress_content"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String, nullable=False)  # framework_node, prep_notes, interview_question
    content_id = Column(Integer, nullable=False)
    last_chunk_index = Column(Integer, default=0)
    char_offset = Column(Integer, default=0)
    total_chars = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    last_read_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ReadingSession(Base):
    """A listening/reading session with duration and item count."""

    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    content_items_read = Column(Integer, default=0)
    total_duration_seconds = Column(Float, default=0.0)
    tts_engine = Column(String, nullable=True)


class AudioCache(Base):
    """Cached TTS audio file metadata for content items."""

    __tablename__ = "audio_cache"
    __table_args__ = (
        UniqueConstraint(
            "content_type", "content_id", "engine", "voice",
            name="uq_audio_cache_content_engine_voice",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String, nullable=False)
    content_id = Column(Integer, nullable=False)
    content_hash = Column(String, nullable=False)  # SHA-256 of source text
    file_path = Column(Text, nullable=False)
    engine = Column(String, nullable=False)  # edge_tts, openai, browser
    voice = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class TTSSummary(Base):
    """Cached LLM-generated TTS-optimized summary for a content item."""

    __tablename__ = "tts_summaries"
    __table_args__ = (
        UniqueConstraint(
            "content_type", "content_id",
            name="uq_tts_summary_content",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_type = Column(String, nullable=False)
    content_id = Column(Integer, nullable=False)
    content_hash = Column(String, nullable=False)  # SHA-256 of source text for invalidation
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
