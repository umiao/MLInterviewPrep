"""TTS engine service using edge-tts for speech synthesis."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import edge_tts

from src.backend.config import get_settings

logger = logging.getLogger(__name__)

# Default cache directory
TTS_CACHE_DIR = Path("data/tts_cache")


def _ensure_cache_dir() -> None:
    """Create TTS cache directory if it does not exist."""
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def compute_cache_key(text: str, voice: str, rate: str) -> str:
    """Compute a deterministic cache key from text + voice + rate.

    Args:
        text: The text to synthesize.
        voice: The TTS voice name.
        rate: The TTS rate string.

    Returns:
        SHA-256 hex digest used as filename (without extension).
    """
    payload = f"{voice}|{rate}|{text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_cached_path(cache_key: str) -> Path:
    """Return the file path for a cached MP3.

    Args:
        cache_key: The cache key (hex digest).

    Returns:
        Path to the MP3 file in the cache directory.
    """
    return TTS_CACHE_DIR / f"{cache_key}.mp3"


async def synthesize_text(
    text: str,
    voice: str | None = None,
    rate: str | None = None,
) -> Path:
    """Synthesize text to MP3 using edge-tts, with file caching.

    Args:
        text: The text to convert to speech.
        voice: TTS voice name (defaults to settings).
        rate: TTS rate string (defaults to settings).

    Returns:
        Path to the generated/cached MP3 file.
    """
    settings = get_settings()
    voice = voice or settings.TTS_VOICE
    rate = rate or settings.TTS_RATE

    _ensure_cache_dir()

    cache_key = compute_cache_key(text, voice, rate)
    cached = get_cached_path(cache_key)

    if cached.exists() and cached.stat().st_size > 0:
        logger.debug("TTS cache hit: %s", cache_key[:12])
        return cached

    logger.info("TTS synthesizing: voice=%s, rate=%s, len=%d", voice, rate, len(text))

    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(cached))

    logger.info("TTS saved: %s (%d bytes)", cached.name, cached.stat().st_size)
    return cached
