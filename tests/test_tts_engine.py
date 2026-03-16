"""Tests for TTS engine abstraction: EdgeTTS, OpenAI, Browser, factory, fallback."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.backend.services.tts_engine import (
    BrowserTTSEngine,
    EdgeTTSEngine,
    OpenAITTSEngine,
    SynthesisResult,
    TTSEngine,
    VoiceOption,
    compute_cache_key,
    get_cached_path,
    get_tts_engine,
    synthesize_text,
    synthesize_with_fallback,
)


# ---------------------------------------------------------------------------
# Utility tests (kept from original)
# ---------------------------------------------------------------------------
class TestCacheUtils:
    """Tests for cache key computation and path generation."""

    def test_cache_key_deterministic(self) -> None:
        """Same inputs produce same cache key."""
        k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
        k2 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
        assert k1 == k2
        assert len(k1) == 64  # SHA-256 hex

    def test_cache_key_differs_on_text(self) -> None:
        """Different text produces different key."""
        k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
        k2 = compute_cache_key("world", "en-US-AriaNeural", "+0%")
        assert k1 != k2

    def test_cache_key_differs_on_voice(self) -> None:
        """Different voice produces different key."""
        k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
        k2 = compute_cache_key("hello", "en-US-GuyNeural", "+0%")
        assert k1 != k2

    def test_cache_key_differs_on_rate(self) -> None:
        """Different rate produces different key."""
        k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
        k2 = compute_cache_key("hello", "en-US-AriaNeural", "+20%")
        assert k1 != k2

    def test_cached_path_format(self) -> None:
        """Cached path is in TTS_CACHE_DIR with .mp3 extension."""
        path = get_cached_path("abc123")
        assert path.name == "abc123.mp3"
        assert "tts_cache" in str(path)


# ---------------------------------------------------------------------------
# Abstract base class tests
# ---------------------------------------------------------------------------
class TestTTSEngineABC:
    """Verify TTSEngine cannot be instantiated directly."""

    def test_cannot_instantiate(self) -> None:
        """TTSEngine is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            TTSEngine()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# EdgeTTSEngine tests
# ---------------------------------------------------------------------------
class TestEdgeTTSEngine:
    """Tests for EdgeTTSEngine."""

    def test_name(self) -> None:
        """Engine name is edge_tts."""
        engine = EdgeTTSEngine()
        assert engine.name == "edge_tts"

    @pytest.mark.asyncio
    async def test_synthesize_produces_mp3(self, tmp_path: Path) -> None:
        """EdgeTTS synthesize creates MP3 file and returns file result."""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with (
            patch("edge_tts.Communicate", return_value=mock_communicate),
            patch("src.backend.services.tts_engine.TTS_CACHE_DIR", tmp_path),
        ):

            # Simulate edge_tts saving a file
            async def fake_save(path: str) -> None:
                """Write fake MP3 data."""
                Path(path).write_bytes(b"fake-mp3-data")

            mock_communicate.save = AsyncMock(side_effect=fake_save)

            result = await engine.synthesize_to_file(
                "Hello world", voice="en-US-AriaNeural", rate="+0%"
            )

        assert result.mode == "file"
        assert result.file_path is not None
        assert result.file_path.exists()
        assert result.file_path.suffix == ".mp3"
        assert result.text is None

    @pytest.mark.asyncio
    async def test_synthesize_cache_hit(self, tmp_path: Path) -> None:
        """EdgeTTS returns cached file without calling edge_tts again."""
        engine = EdgeTTSEngine()

        # Pre-create a cached file
        cache_key = compute_cache_key("cached text", "en-US-AriaNeural", "+0%")
        cached_file = tmp_path / f"{cache_key}.mp3"
        cached_file.write_bytes(b"cached-mp3")

        with patch("src.backend.services.tts_engine.TTS_CACHE_DIR", tmp_path):
            result = await engine.synthesize_to_file(
                "cached text", voice="en-US-AriaNeural", rate="+0%"
            )

        assert result.mode == "file"
        assert result.file_path == cached_file

    @pytest.mark.asyncio
    async def test_voice_options(self) -> None:
        """EdgeTTS returns voice options from edge_tts.list_voices."""
        engine = EdgeTTSEngine()

        mock_voices = [
            {"ShortName": "en-US-AriaNeural", "FriendlyName": "Aria", "Locale": "en-US"},
            {"ShortName": "zh-CN-XiaoxiaoNeural", "FriendlyName": "Xiaoxiao", "Locale": "zh-CN"},
            {"ShortName": "en-GB-SoniaNeural", "FriendlyName": "Sonia", "Locale": "en-GB"},
        ]

        with patch("edge_tts.list_voices", new_callable=AsyncMock, return_value=mock_voices):
            voices = await engine.voice_options()

        # Only English voices
        assert len(voices) == 2
        assert all(isinstance(v, VoiceOption) for v in voices)
        assert voices[0].id == "en-US-AriaNeural"
        assert voices[1].id == "en-GB-SoniaNeural"


# ---------------------------------------------------------------------------
# OpenAITTSEngine tests
# ---------------------------------------------------------------------------
class TestOpenAITTSEngine:
    """Tests for OpenAITTSEngine."""

    def test_name(self) -> None:
        """Engine name is openai."""
        engine = OpenAITTSEngine()
        assert engine.name == "openai"

    @pytest.mark.asyncio
    async def test_synthesize_no_api_key_raises(self) -> None:
        """OpenAI engine raises RuntimeError without API key."""
        engine = OpenAITTSEngine()

        with (
            patch(
                "src.backend.services.tts_engine.get_settings",
                return_value=MagicMock(OPENAI_API_KEY=""),
            ),
            pytest.raises(RuntimeError, match="OPENAI_API_KEY not configured"),
        ):
            await engine.synthesize_to_file("test text")

    @pytest.mark.asyncio
    async def test_synthesize_api_call_verified(self, tmp_path: Path) -> None:
        """OpenAI engine makes correct API call and saves MP3."""
        engine = OpenAITTSEngine()

        mock_response = MagicMock()
        mock_response.content = b"openai-mp3-data"
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("src.backend.services.tts_engine.TTS_CACHE_DIR", tmp_path),
            patch(
                "src.backend.services.tts_engine.get_settings",
                return_value=MagicMock(OPENAI_API_KEY="sk-test-key"),
            ),
            patch(
                "httpx.AsyncClient",
                return_value=mock_client_instance,
            ),
        ):
            result = await engine.synthesize_to_file(
                "Hello from OpenAI", voice="nova", rate="1.0"
            )

        assert result.mode == "file"
        assert result.file_path is not None
        assert result.file_path.read_bytes() == b"openai-mp3-data"

        # Verify API call arguments
        call_args = mock_client_instance.post.call_args
        assert call_args[0][0] == "https://api.openai.com/v1/audio/speech"
        json_body = call_args[1]["json"]
        assert json_body["input"] == "Hello from OpenAI"
        assert json_body["voice"] == "nova"
        assert json_body["model"] == "tts-1"
        assert json_body["speed"] == 1.0

    @pytest.mark.asyncio
    async def test_voice_options(self) -> None:
        """OpenAI engine returns its fixed set of voices."""
        engine = OpenAITTSEngine()
        voices = await engine.voice_options()
        assert len(voices) == 6
        voice_ids = [v.id for v in voices]
        assert "alloy" in voice_ids
        assert "nova" in voice_ids
        assert "shimmer" in voice_ids


# ---------------------------------------------------------------------------
# BrowserTTSEngine tests
# ---------------------------------------------------------------------------
class TestBrowserTTSEngine:
    """Tests for BrowserTTSEngine."""

    def test_name(self) -> None:
        """Engine name is browser."""
        engine = BrowserTTSEngine()
        assert engine.name == "browser"

    @pytest.mark.asyncio
    async def test_synthesize_returns_text(self) -> None:
        """Browser engine returns text in browser mode, no file."""
        engine = BrowserTTSEngine()
        result = await engine.synthesize_to_file("Speak this in browser")

        assert result.mode == "browser"
        assert result.text == "Speak this in browser"
        assert result.file_path is None

    @pytest.mark.asyncio
    async def test_voice_options_empty(self) -> None:
        """Browser engine returns empty voice list (client-side)."""
        engine = BrowserTTSEngine()
        voices = await engine.voice_options()
        assert voices == []


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------
class TestGetTTSEngine:
    """Tests for the get_tts_engine factory."""

    def test_edge_tts(self) -> None:
        """Factory returns EdgeTTSEngine for 'edge-tts'."""
        engine = get_tts_engine("edge-tts")
        assert isinstance(engine, EdgeTTSEngine)

    def test_edge_tts_underscore(self) -> None:
        """Factory accepts 'edge_tts' (underscore variant)."""
        engine = get_tts_engine("edge_tts")
        assert isinstance(engine, EdgeTTSEngine)

    def test_openai(self) -> None:
        """Factory returns OpenAITTSEngine for 'openai'."""
        engine = get_tts_engine("openai")
        assert isinstance(engine, OpenAITTSEngine)

    def test_browser(self) -> None:
        """Factory returns BrowserTTSEngine for 'browser'."""
        engine = get_tts_engine("browser")
        assert isinstance(engine, BrowserTTSEngine)

    def test_unknown_raises(self) -> None:
        """Factory raises ValueError for unknown engine name."""
        with pytest.raises(ValueError, match="Unknown TTS engine"):
            get_tts_engine("nonexistent")

    def test_default_from_settings(self) -> None:
        """Factory uses settings.TTS_ENGINE when name is None."""
        with patch(
            "src.backend.services.tts_engine.get_settings",
            return_value=MagicMock(TTS_ENGINE="browser"),
        ):
            engine = get_tts_engine()
            assert isinstance(engine, BrowserTTSEngine)


# ---------------------------------------------------------------------------
# synthesize_text (backward compat wrapper) tests
# ---------------------------------------------------------------------------
class TestSynthesizeText:
    """Tests for synthesize_text top-level function."""

    @pytest.mark.asyncio
    async def test_delegates_to_engine(self) -> None:
        """synthesize_text delegates to the engine from factory."""
        mock_result = SynthesisResult(mode="browser", text="delegated")

        with patch(
            "src.backend.services.tts_engine.get_tts_engine"
        ) as mock_factory:
            mock_engine = AsyncMock()
            mock_engine.synthesize_to_file = AsyncMock(return_value=mock_result)
            mock_factory.return_value = mock_engine

            result = await synthesize_text("test", engine_name="browser")

        assert result.mode == "browser"
        assert result.text == "delegated"


# ---------------------------------------------------------------------------
# Fallback tests
# ---------------------------------------------------------------------------
class TestSynthesizeWithFallback:
    """Tests for synthesize_with_fallback."""

    @pytest.mark.asyncio
    async def test_success_no_fallback(self) -> None:
        """When primary engine succeeds, no fallback occurs."""
        mock_result = SynthesisResult(mode="file", file_path=Path("/tmp/test.mp3"))

        with patch(
            "src.backend.services.tts_engine.get_tts_engine"
        ) as mock_factory:
            mock_engine = AsyncMock()
            mock_engine.name = "edge_tts"
            mock_engine.synthesize_to_file = AsyncMock(return_value=mock_result)
            mock_factory.return_value = mock_engine

            result = await synthesize_with_fallback("test", engine_name="edge-tts")

        assert result.mode == "file"

    @pytest.mark.asyncio
    async def test_edge_tts_failure_falls_back_to_browser(self) -> None:
        """When edge-tts fails (network error), falls back to browser mode."""
        with patch(
            "src.backend.services.tts_engine.get_tts_engine"
        ) as mock_factory:
            mock_engine = AsyncMock()
            mock_engine.name = "edge_tts"
            mock_engine.synthesize_to_file = AsyncMock(
                side_effect=ConnectionError("Network unreachable")
            )
            mock_factory.return_value = mock_engine

            result = await synthesize_with_fallback(
                "fallback test text", engine_name="edge-tts"
            )

        assert result.mode == "browser"
        assert result.text == "fallback test text"

    @pytest.mark.asyncio
    async def test_browser_engine_no_double_fallback(self) -> None:
        """When browser is the primary engine, no fallback is attempted."""
        with patch(
            "src.backend.services.tts_engine.get_tts_engine"
        ) as mock_factory:
            mock_engine = BrowserTTSEngine()
            mock_factory.return_value = mock_engine

            result = await synthesize_with_fallback(
                "direct browser", engine_name="browser"
            )

        assert result.mode == "browser"
        assert result.text == "direct browser"

    @pytest.mark.asyncio
    async def test_openai_failure_falls_back_to_browser(self) -> None:
        """When OpenAI TTS fails, falls back to browser mode."""
        with patch(
            "src.backend.services.tts_engine.get_tts_engine"
        ) as mock_factory:
            mock_engine = AsyncMock()
            mock_engine.name = "openai"
            mock_engine.synthesize_to_file = AsyncMock(
                side_effect=RuntimeError("OPENAI_API_KEY not configured")
            )
            mock_factory.return_value = mock_engine

            result = await synthesize_with_fallback(
                "openai fallback test", engine_name="openai"
            )

        assert result.mode == "browser"
        assert result.text == "openai fallback test"
