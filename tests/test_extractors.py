"""Tests for HTML extractors."""
from src.backend.scraper.extractors import compute_content_hash, extract_posts


def test_extract_posts_empty_html():
    """Empty HTML returns empty list."""
    assert extract_posts("", "blind") == []


def test_extract_posts_unknown_site():
    """Unknown site returns empty list."""
    assert extract_posts("<html></html>", "unknown") == []


def test_extract_posts_with_matching_selectors():
    """Posts extracted when HTML matches site selectors."""
    html = """
    <html><body>
    <div class="post-item">
        <h3 class="title"><a href="/post/1">Interview at Google</a></h3>
        <div class="body-text">They asked about system design.</div>
    </div>
    <div class="post-item">
        <h3 class="title"><a href="/post/2">Meta MLE</a></h3>
        <div class="body-text">ML coding round was tough.</div>
    </div>
    </body></html>
    """
    posts = extract_posts(html, "blind")
    assert len(posts) == 2
    assert posts[0]["title"] == "Interview at Google"
    assert "system design" in posts[0]["body_text"]


def test_content_hash_deterministic():
    """Same text produces same hash."""
    h1 = compute_content_hash("hello world")
    h2 = compute_content_hash("hello world")
    assert h1 == h2


def test_content_hash_different():
    """Different text produces different hash."""
    h1 = compute_content_hash("hello")
    h2 = compute_content_hash("world")
    assert h1 != h2
