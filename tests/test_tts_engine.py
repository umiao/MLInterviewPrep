"""Tests for TTS engine utilities."""
from src.backend.services.tts_engine import compute_cache_key, get_cached_path


def test_cache_key_deterministic():
    """Same inputs produce same cache key."""
    k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
    k2 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
    assert k1 == k2
    assert len(k1) == 64  # SHA-256 hex


def test_cache_key_differs_on_text():
    """Different text produces different key."""
    k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
    k2 = compute_cache_key("world", "en-US-AriaNeural", "+0%")
    assert k1 != k2


def test_cache_key_differs_on_voice():
    """Different voice produces different key."""
    k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
    k2 = compute_cache_key("hello", "en-US-GuyNeural", "+0%")
    assert k1 != k2


def test_cache_key_differs_on_rate():
    """Different rate produces different key."""
    k1 = compute_cache_key("hello", "en-US-AriaNeural", "+0%")
    k2 = compute_cache_key("hello", "en-US-AriaNeural", "+20%")
    assert k1 != k2


def test_cached_path_format():
    """Cached path is in TTS_CACHE_DIR with .mp3 extension."""
    path = get_cached_path("abc123")
    assert path.name == "abc123.mp3"
    assert "tts_cache" in str(path)
