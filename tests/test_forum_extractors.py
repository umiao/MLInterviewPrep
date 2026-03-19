"""Tests for forum HTML extractors (1point3acres)."""

from pathlib import Path

import pytest

from src.backend.scraper.forum_extractors import (
    derive_page_url,
    extract_max_page,
    extract_post_content,
    extract_post_links,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def index_html() -> str:
    """Load forum index HTML fixture."""
    return (FIXTURES_DIR / "forum_index.html").read_text(encoding="utf-8")


@pytest.fixture()
def post_html() -> str:
    """Load forum post HTML fixture."""
    return (FIXTURES_DIR / "forum_post.html").read_text(encoding="utf-8")


# --- extract_post_links tests ---


class TestExtractPostLinks:
    """Tests for extract_post_links."""

    def test_returns_correct_count(self, index_html: str) -> None:
        """Should extract all 5 post links from the fixture."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        assert len(links) == 5

    def test_urls_are_absolute(self, index_html: str) -> None:
        """All returned URLs must be absolute, not relative."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        for link in links:
            assert link["url"].startswith("https://"), f"URL not absolute: {link['url']}"

    def test_link_dict_keys(self, index_html: str) -> None:
        """Each link dict must have url, title, and order keys."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        for link in links:
            assert "url" in link
            assert "title" in link
            assert "order" in link

    def test_order_is_sequential(self, index_html: str) -> None:
        """Order values should be sequential starting from 0."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        for idx, link in enumerate(links):
            assert link["order"] == idx

    def test_titles_not_empty(self, index_html: str) -> None:
        """All extracted titles should be non-empty strings."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        for link in links:
            assert link["title"], f"Empty title for {link['url']}"

    def test_first_link_url(self, index_html: str) -> None:
        """First link should resolve to the correct absolute URL."""
        links = extract_post_links(index_html, "https://www.1point3acres.com/bbs/")
        assert links[0]["url"] == "https://www.1point3acres.com/bbs/thread-1169245-1-1.html"

    def test_empty_html_returns_empty(self) -> None:
        """Empty input should return empty list."""
        assert extract_post_links("", "https://example.com") == []

    def test_no_hotlist_returns_empty(self) -> None:
        """HTML without ul.hotlist or thread links should return empty list."""
        html = "<html><body><div>No posts here</div></body></html>"
        assert extract_post_links(html, "https://example.com") == []

    def test_table_layout(self) -> None:
        """Should extract links from table layout (th > a[href*=thread-])."""
        html = (FIXTURES_DIR / "forum_index_table.html").read_text(
            encoding="utf-8"
        )
        links = extract_post_links(
            html, "https://www.1point3acres.com/bbs/"
        )
        assert len(links) == 3
        assert links[0]["url"].endswith("thread-1169229-1-1.html")
        assert links[0]["title"] == "MLE phone screen"
        assert links[2]["order"] == 2


# --- extract_post_content tests ---


class TestExtractPostContent:
    """Tests for extract_post_content."""

    def test_returns_correct_title(self, post_html: str) -> None:
        """Should extract the post title from h2."""
        result = extract_post_content(post_html)
        assert "Thinking of leaving LinkedIn for Meta" in result["title"]

    def test_returns_body_text(self, post_html: str) -> None:
        """Body should contain the actual post content."""
        result = extract_post_content(post_html)
        assert "I worked at Meta for 3 years" in result["body"]

    def test_jammer_stripped(self, post_html: str) -> None:
        """Jammer font.jammer noise text must not appear in body."""
        result = extract_post_content(post_html)
        assert "jammer" not in result["body"].lower()
        assert ".--" not in result["body"]
        assert "Waral" not in result["body"]
        assert "1point 3acres bbs" not in result["body"]

    def test_external_post_id(self, post_html: str) -> None:
        """Should extract the numeric post ID from pid attribute."""
        result = extract_post_content(post_html)
        assert result["external_post_id"] == "20871855"

    def test_author_extracted(self, post_html: str) -> None:
        """Should extract the author name."""
        result = extract_post_content(post_html)
        assert result["author"]  # Non-empty

    def test_date_extracted(self, post_html: str) -> None:
        """Should extract the published date from meta tag."""
        result = extract_post_content(post_html)
        assert "2026-3-6" in result["date"]

    def test_extracts_only_op_body(self, post_html: str) -> None:
        """Should extract only the first (OP) post, not replies."""
        result = extract_post_content(post_html)
        assert "Both companies have good and bad teams" not in result["body"]

    def test_empty_html_returns_empty_dict(self) -> None:
        """Empty input should return empty dict."""
        assert extract_post_content("") == {}

    def test_body_has_no_extra_noise(self, post_html: str) -> None:
        """Body should read cleanly without anti-scraping artifacts."""
        result = extract_post_content(post_html)
        # Should contain actual content
        assert "bureaucratic" in result["body"]
        assert "LinkedIn workload" in result["body"]
        # Should not contain noise patterns
        assert ". .noise" not in result["body"]


# --- derive_page_url tests ---


class TestDerivePageUrl:
    """Tests for derive_page_url."""

    def test_basic(self) -> None:
        """Replace page 1 with page 5."""
        url = "https://www.1point3acres.com/bbs/tag-415-1.html"
        assert derive_page_url(url, 5) == "https://www.1point3acres.com/bbs/tag-415-5.html"

    def test_page_1(self) -> None:
        """Replace page 5 back to page 1."""
        url = "https://www.1point3acres.com/bbs/tag-415-5.html"
        assert derive_page_url(url, 1) == "https://www.1point3acres.com/bbs/tag-415-1.html"

    def test_invalid_url(self) -> None:
        """Non-matching URL should raise ValueError."""
        with pytest.raises(ValueError, match="does not match"):
            derive_page_url("https://example.com/not-a-tag-page", 1)

    def test_high_page(self) -> None:
        """Page 255 should work correctly."""
        url = "https://www.1point3acres.com/bbs/tag-415-1.html"
        result = derive_page_url(url, 255)
        assert result == "https://www.1point3acres.com/bbs/tag-415-255.html"


# --- extract_max_page tests ---


@pytest.fixture()
def index_with_pagination_html() -> str:
    """Load forum index HTML fixture with pagination."""
    return (FIXTURES_DIR / "forum_index_with_pagination.html").read_text(encoding="utf-8")


class TestExtractMaxPage:
    """Tests for extract_max_page."""

    def test_with_pagination(self, index_with_pagination_html: str) -> None:
        """Should extract max page from a.last href."""
        assert extract_max_page(index_with_pagination_html) == 255

    def test_no_pagination(self, index_html: str) -> None:
        """HTML without div.pg should return 1."""
        assert extract_max_page(index_html) == 1

    def test_empty_html(self) -> None:
        """Empty string should return 1."""
        assert extract_max_page("") == 1
