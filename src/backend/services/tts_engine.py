"""TTS engine abstraction: EdgeTTS, OpenAI, and Browser engines."""
from __future__ import annotations

import abc
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

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


@dataclass
class VoiceOption:
    """A voice available for a TTS engine."""

    id: str
    name: str
    language: str = "en-US"


@dataclass
class SynthesisResult:
    """Result of a TTS synthesis operation.

    For file-based engines (edge-tts, openai), file_path is set.
    For browser engine, mode='browser' and text is set instead.
    """

    mode: str  # "file" or "browser"
    file_path: Path | None = None
    text: str | None = None


class TTSEngine(abc.ABC):
    """Abstract base class for TTS engines."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the engine name identifier."""

    @abc.abstractmethod
    async def synthesize_to_file(
        self,
        text: str,
        voice: str | None = None,
        rate: str | None = None,
    ) -> SynthesisResult:
        """Synthesize text to speech.

        Args:
            text: The text to convert to speech.
            voice: TTS voice name (engine-specific default if None).
            rate: TTS rate string (engine-specific default if None).

        Returns:
            SynthesisResult with file path or browser text.
        """

    @abc.abstractmethod
    async def voice_options(self) -> list[VoiceOption]:
        """Return available voices for this engine.

        Returns:
            List of available voice options.
        """


class EdgeTTSEngine(TTSEngine):
    """TTS engine using Microsoft Edge TTS (free, no API key)."""

    @property
    def name(self) -> str:
        """Return the engine name."""
        return "edge_tts"

    async def synthesize_to_file(
        self,
        text: str,
        voice: str | None = None,
        rate: str | None = None,
    ) -> SynthesisResult:
        """Synthesize text using edge-tts, with file caching.

        Args:
            text: The text to convert to speech.
            voice: TTS voice name (defaults to settings).
            rate: TTS rate string (defaults to settings).

        Returns:
            SynthesisResult with path to the MP3 file.
        """
        import edge_tts

        settings = get_settings()
        voice = voice or settings.TTS_VOICE
        rate = rate or settings.TTS_RATE

        _ensure_cache_dir()

        cache_key = compute_cache_key(text, voice, rate)
        cached = get_cached_path(cache_key)

        if cached.exists() and cached.stat().st_size > 0:
            logger.debug("TTS cache hit: %s", cache_key[:12])
            return SynthesisResult(mode="file", file_path=cached)

        logger.info(
            "TTS synthesizing (edge-tts): voice=%s, rate=%s, len=%d",
            voice,
            rate,
            len(text),
        )

        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(cached))

        logger.info("TTS saved: %s (%d bytes)", cached.name, cached.stat().st_size)
        return SynthesisResult(mode="file", file_path=cached)

    async def voice_options(self) -> list[VoiceOption]:
        """Return available edge-tts voices (English subset).

        Returns:
            List of English voice options.
        """
        import edge_tts

        voices = await edge_tts.list_voices()
        return [
            VoiceOption(
                id=v["ShortName"],
                name=v["FriendlyName"],
                language=v["Locale"],
            )
            for v in voices
            if v["Locale"].startswith("en-")
        ]


class OpenAITTSEngine(TTSEngine):
    """TTS engine using OpenAI's TTS API."""

    # OpenAI TTS voices
    VOICES = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
    DEFAULT_VOICE = "nova"
    DEFAULT_MODEL = "tts-1"

    @property
    def name(self) -> str:
        """Return the engine name."""
        return "openai"

    async def synthesize_to_file(
        self,
        text: str,
        voice: str | None = None,
        rate: str | None = None,
    ) -> SynthesisResult:
        """Synthesize text using OpenAI TTS API.

        Args:
            text: The text to convert to speech.
            voice: OpenAI voice name (defaults to nova).
            rate: Speed multiplier as string (e.g. "1.0"). Ignored for cache key
                  compatibility but passed as speed param.

        Returns:
            SynthesisResult with path to the MP3 file.

        Raises:
            RuntimeError: If OPENAI_API_KEY is not configured.
        """
        import httpx

        settings = get_settings()
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not configured. Set it in .env or use a different engine."
            )

        voice = voice or self.DEFAULT_VOICE
        rate = rate or "1.0"

        _ensure_cache_dir()

        cache_key = compute_cache_key(text, voice, rate)
        cached = get_cached_path(cache_key)

        if cached.exists() and cached.stat().st_size > 0:
            logger.debug("TTS cache hit (openai): %s", cache_key[:12])
            return SynthesisResult(mode="file", file_path=cached)

        logger.info(
            "TTS synthesizing (openai): voice=%s, speed=%s, len=%d",
            voice,
            rate,
            len(text),
        )

        # Parse rate to float speed (OpenAI accepts 0.25-4.0)
        try:
            speed = float(rate)
        except ValueError:
            speed = 1.0

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.DEFAULT_MODEL,
                    "input": text,
                    "voice": voice,
                    "speed": speed,
                    "response_format": "mp3",
                },
            )
            response.raise_for_status()

            cached.write_bytes(response.content)

        logger.info("TTS saved (openai): %s (%d bytes)", cached.name, cached.stat().st_size)
        return SynthesisResult(mode="file", file_path=cached)

    async def voice_options(self) -> list[VoiceOption]:
        """Return available OpenAI TTS voices.

        Returns:
            List of OpenAI voice options.
        """
        return [
            VoiceOption(id=v, name=v.capitalize(), language="en-US")
            for v in self.VOICES
        ]


class BrowserTTSEngine(TTSEngine):
    """TTS engine that delegates to the browser's Web Speech API.

    Instead of generating audio server-side, returns the text for the
    frontend to speak using SpeechSynthesis.
    """

    @property
    def name(self) -> str:
        """Return the engine name."""
        return "browser"

    async def synthesize_to_file(
        self,
        text: str,
        voice: str | None = None,
        rate: str | None = None,
    ) -> SynthesisResult:
        """Return text for browser-side synthesis.

        Args:
            text: The text for the browser to speak.
            voice: Ignored (browser controls voice selection).
            rate: Ignored (browser controls rate).

        Returns:
            SynthesisResult with mode='browser' and text set.
        """
        return SynthesisResult(mode="browser", text=text)

    async def voice_options(self) -> list[VoiceOption]:
        """Browser voices are client-side; return empty list.

        Returns:
            Empty list (voices are determined by the browser).
        """
        return []


# Engine registry
_ENGINE_CLASSES: dict[str, type[TTSEngine]] = {
    "edge-tts": EdgeTTSEngine,
    "edge_tts": EdgeTTSEngine,
    "openai": OpenAITTSEngine,
    "browser": BrowserTTSEngine,
}


def get_tts_engine(name: str | None = None) -> TTSEngine:
    """Factory: return a TTSEngine instance by name.

    Args:
        name: Engine name ('edge-tts', 'openai', 'browser').
              Defaults to settings.TTS_ENGINE.

    Returns:
        TTSEngine instance.

    Raises:
        ValueError: If engine name is not recognized.
    """
    if name is None:
        settings = get_settings()
        name = settings.TTS_ENGINE

    cls = _ENGINE_CLASSES.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown TTS engine: {name!r}. "
            f"Available: {', '.join(sorted(_ENGINE_CLASSES))}"
        )
    return cls()


# ---------------------------------------------------------------------------
# Backward-compatible top-level function used by reading router
# ---------------------------------------------------------------------------
async def synthesize_text(
    text: str,
    voice: str | None = None,
    rate: str | None = None,
    engine_name: str | None = None,
) -> SynthesisResult:
    """Synthesize text using the configured TTS engine.

    This is the main entry point used by the reading router. It delegates
    to the appropriate engine based on configuration.

    Args:
        text: The text to convert to speech.
        voice: TTS voice name (defaults to engine/settings default).
        rate: TTS rate string (defaults to engine/settings default).
        engine_name: Override engine name (defaults to settings.TTS_ENGINE).

    Returns:
        SynthesisResult (file path for audio engines, text for browser).
    """
    engine = get_tts_engine(engine_name)
    return await engine.synthesize_to_file(text, voice=voice, rate=rate)


async def synthesize_with_fallback(
    text: str,
    voice: str | None = None,
    rate: str | None = None,
    engine_name: str | None = None,
) -> SynthesisResult:
    """Synthesize with automatic fallback to browser engine on failure.

    Tries the requested engine first. If it raises an exception (e.g.,
    network error for edge-tts), falls back to the browser engine.

    Args:
        text: The text to convert to speech.
        voice: TTS voice name.
        rate: TTS rate string.
        engine_name: Override engine name (defaults to settings.TTS_ENGINE).

    Returns:
        SynthesisResult from primary engine, or browser fallback.
    """
    engine = get_tts_engine(engine_name)

    if engine.name == "browser":
        return await engine.synthesize_to_file(text, voice=voice, rate=rate)

    try:
        return await engine.synthesize_to_file(text, voice=voice, rate=rate)
    except Exception:
        logger.warning(
            "TTS engine %r failed, falling back to browser",
            engine.name,
            exc_info=True,
        )
        browser = BrowserTTSEngine()
        return await browser.synthesize_to_file(text, voice=voice, rate=rate)
