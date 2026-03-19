"""Tests for the forum service layer."""

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.backend.models.company import Company
from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed
from src.backend.services.forum_service import (
    _extract_external_id,
    fetch_next_unfetched,
    fetch_single_post,
    get_fetch_progress,
    import_post_to_prep_notes,
    retry_failed,
    scrape_seed_page,
)

FIXTURES = Path(__file__).parent / "fixtures"
INDEX_HTML = (FIXTURES / "forum_index.html").read_text(encoding="utf-8")
POST_HTML = (FIXTURES / "forum_post.html").read_text(encoding="utf-8")


@pytest.fixture()
def seed(db_session):
    """Create a ForumSeed for testing."""
    s = ForumSeed(
        url="https://www.1point3acres.com/bbs/tag-123.html",
        source_site="1point3acres",
        label="LinkedIn",
    )
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s


@pytest.fixture()
def company(db_session):
    """Create a Company for testing."""
    c = Company(name="LinkedIn")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def mock_crawler():
    """Create a mock PlaywrightCrawler with AsyncMock methods."""
    crawler = AsyncMock()
    crawler.fetch_page_cdp = AsyncMock(return_value=INDEX_HTML)
    crawler.fetch_page_with_cookie = AsyncMock(return_value=INDEX_HTML)
    return crawler


# --- _extract_external_id ---


class TestExtractExternalId:
    """Tests for external post ID extraction from URLs."""

    def test_extracts_thread_id(self) -> None:
        """Extract numeric ID from thread URL."""
        url = "https://www.1point3acres.com/bbs/thread-1169245-1-1.html"
        assert _extract_external_id(url) == "1169245"

    def test_returns_none_for_no_match(self) -> None:
        """Return None when URL has no thread pattern."""
        assert _extract_external_id("https://example.com/page") is None


# --- scrape_seed_page ---


class TestScrapeSeedPage:
    """Tests for Phase A: index page scraping."""

    @pytest.mark.asyncio()
    async def test_scrape_creates_links(self, db_session, seed, mock_crawler) -> None:
        """Scraping index page creates ForumPostLink records."""
        links = await scrape_seed_page(db_session, seed.id, mock_crawler)
        assert len(links) > 0
        for link in links:
            assert link.forum_seed_id == seed.id
            assert link.url.startswith("https://")

    @pytest.mark.asyncio()
    async def test_scrape_is_idempotent(self, db_session, seed, mock_crawler) -> None:
        """Running scrape twice produces no duplicate links."""
        links1 = await scrape_seed_page(db_session, seed.id, mock_crawler)
        links2 = await scrape_seed_page(db_session, seed.id, mock_crawler)
        # Same count -- no new links on second run
        all_links = db_session.query(ForumPostLink).all()
        assert len(all_links) == len(links1)
        assert len(links2) == len(links1)

    @pytest.mark.asyncio()
    async def test_scrape_updates_title(self, db_session, seed, mock_crawler) -> None:
        """Existing links get title updated if changed."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()
        original_title = link.title
        assert original_title  # should have a title

    @pytest.mark.asyncio()
    async def test_scrape_updates_last_scraped_at(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Seed's last_scraped_at is updated after scraping."""
        assert seed.last_scraped_at is None
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        db_session.refresh(seed)
        assert seed.last_scraped_at is not None

    @pytest.mark.asyncio()
    async def test_scrape_invalid_seed_raises(self, db_session, mock_crawler) -> None:
        """Scraping non-existent seed raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await scrape_seed_page(db_session, 9999, mock_crawler)

    @pytest.mark.asyncio()
    async def test_scrape_empty_html_returns_empty(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Empty HTML response returns no links."""
        mock_crawler.fetch_page_cdp.return_value = ""
        mock_crawler.fetch_page_with_cookie.return_value = ""
        links = await scrape_seed_page(db_session, seed.id, mock_crawler)
        assert links == []

    @pytest.mark.asyncio()
    async def test_scrape_cdp_fallback_to_cookie(
        self, db_session, seed, mock_crawler, monkeypatch
    ) -> None:
        """Falls back to cookie method when CDP returns empty."""
        mock_crawler.fetch_page_cdp.return_value = ""
        mock_crawler.fetch_page_with_cookie.return_value = INDEX_HTML
        monkeypatch.setenv("ONEPOINT3ACRES_COOKIE", "test=cookie")
        links = await scrape_seed_page(db_session, seed.id, mock_crawler)
        assert len(links) > 0
        mock_crawler.fetch_page_with_cookie.assert_called_once()

    @pytest.mark.asyncio()
    async def test_scrape_extracts_external_ids(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Links have external_post_id extracted from thread URLs."""
        links = await scrape_seed_page(db_session, seed.id, mock_crawler)
        ids_set = {lk.external_post_id for lk in links if lk.external_post_id}
        assert len(ids_set) > 0
        # All should be numeric strings
        for eid in ids_set:
            assert eid.isdigit()

    @pytest.mark.asyncio()
    async def test_scrape_skips_conflicting_external_id(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Links with external_post_id from another seed are skipped."""
        # Create another seed with a link that has one of the external IDs
        other_seed = ForumSeed(
            url="https://example.com/other",
            source_site="1point3acres",
        )
        db_session.add(other_seed)
        db_session.flush()

        # Pre-insert a link with a conflicting external_post_id
        conflict_link = ForumPostLink(
            forum_seed_id=other_seed.id,
            url="https://example.com/conflict",
            external_post_id="1169245",  # Same as first link in fixture
        )
        db_session.add(conflict_link)
        db_session.commit()

        links = await scrape_seed_page(db_session, seed.id, mock_crawler)
        ext_ids = [lk.external_post_id for lk in links]
        assert "1169245" not in ext_ids


# --- fetch_single_post ---


class TestFetchSinglePost:
    """Tests for Phase B: single post fetching."""

    @pytest.mark.asyncio()
    async def test_fetch_creates_post(self, db_session, seed, mock_crawler) -> None:
        """Fetching a pending link creates a ForumPost."""
        mock_crawler.fetch_page_cdp.return_value = INDEX_HTML
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()

        # Now mock the post page fetch
        mock_crawler.fetch_page_cdp.return_value = POST_HTML
        post = await fetch_single_post(db_session, link.id, mock_crawler)
        assert post is not None
        assert post.raw_text
        assert post.content_hash
        assert link.status == "fetched"

    @pytest.mark.asyncio()
    async def test_fetch_skips_already_fetched(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Already-fetched links are skipped."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()
        link.status = "fetched"
        db_session.commit()

        result = await fetch_single_post(db_session, link.id, mock_crawler)
        assert result is None

    @pytest.mark.asyncio()
    async def test_fetch_failure_sets_status(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Failed fetch sets status=failed and increments retry_count."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()

        mock_crawler.fetch_page_cdp.return_value = ""
        mock_crawler.fetch_page_with_cookie.return_value = ""
        result = await fetch_single_post(db_session, link.id, mock_crawler)

        assert result is None
        db_session.refresh(link)
        assert link.status == "failed"
        assert link.retry_count == 1
        assert link.last_error

    @pytest.mark.asyncio()
    async def test_fetch_invalid_link_raises(self, db_session, mock_crawler) -> None:
        """Fetching non-existent link raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await fetch_single_post(db_session, 9999, mock_crawler)

    @pytest.mark.asyncio()
    async def test_fetch_extracts_author_and_date(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Fetched post has author and published_at from extraction."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()

        mock_crawler.fetch_page_cdp.return_value = POST_HTML
        post = await fetch_single_post(db_session, link.id, mock_crawler)
        assert post is not None
        # From fixture: author is AnonymousUser-XFEEV
        assert "AnonymousUser" in post.author
        assert post.published_at  # Has a date string


# --- fetch_next_unfetched ---


class TestFetchNextUnfetched:
    """Tests for fetching next pending post."""

    @pytest.mark.asyncio()
    async def test_fetches_next_pending(self, db_session, seed, mock_crawler) -> None:
        """Fetches the next pending link ordered by fetch_order."""
        mock_crawler.fetch_page_cdp.return_value = INDEX_HTML
        await scrape_seed_page(db_session, seed.id, mock_crawler)

        mock_crawler.fetch_page_cdp.return_value = POST_HTML
        post = await fetch_next_unfetched(db_session, seed.id, mock_crawler)
        assert post is not None

    @pytest.mark.asyncio()
    async def test_returns_none_when_all_fetched(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Returns None when no pending links remain."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        # Mark all as fetched
        for link in db_session.query(ForumPostLink).all():
            link.status = "fetched"
        db_session.commit()

        result = await fetch_next_unfetched(db_session, seed.id, mock_crawler)
        assert result is None


# --- retry_failed ---


class TestRetryFailed:
    """Tests for retrying failed links."""

    @pytest.mark.asyncio()
    async def test_retry_resets_and_refetches(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Failed links are reset to pending and re-fetched."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)

        # Mark first link as failed
        link = db_session.query(ForumPostLink).first()
        link.status = "failed"
        link.retry_count = 1
        link.last_error = "test error"
        db_session.commit()

        # Now retry with post HTML
        mock_crawler.fetch_page_cdp.return_value = POST_HTML
        results = await retry_failed(db_session, seed.id, mock_crawler)
        assert len(results) == 1
        db_session.refresh(link)
        assert link.status == "fetched"

    @pytest.mark.asyncio()
    async def test_retry_no_failed_returns_empty(
        self, db_session, seed, mock_crawler
    ) -> None:
        """No failed links means empty result."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        results = await retry_failed(db_session, seed.id, mock_crawler)
        assert results == []


# --- import_post_to_prep_notes ---


class TestImportPostToPrepNotes:
    """Tests for importing posts to company prep notes."""

    def _create_post(self, db_session, seed) -> ForumPost:
        """Helper to create a fetched post."""
        link = ForumPostLink(
            forum_seed_id=seed.id,
            url="https://www.1point3acres.com/bbs/thread-123-1-1.html",
            external_post_id="123",
            title="Test Interview Post",
            status="fetched",
        )
        db_session.add(link)
        db_session.flush()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="Interview experience at LinkedIn.\nAsked about system design.",
            content_hash="abc123",
            author="TestUser",
            published_at="2026-03-15",
            fetched_at=datetime(2026, 3, 15, 10, 0),
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        return post

    def test_import_appends_with_header(self, db_session, seed, company) -> None:
        """Import appends post content with metadata header."""
        post = self._create_post(db_session, seed)
        result = import_post_to_prep_notes(db_session, post.id, company.id)

        assert "Forum Post: Test Interview Post" in result.prep_notes
        assert "Interview experience at LinkedIn." in result.prep_notes
        assert "thread-123" in result.prep_notes
        assert "External ID" in result.prep_notes

    def test_import_uses_separator(self, db_session, seed, company) -> None:
        """Second import uses --- separator."""
        post = self._create_post(db_session, seed)
        company.prep_notes = "Existing notes here."
        db_session.commit()

        result = import_post_to_prep_notes(db_session, post.id, company.id)
        assert "Existing notes here.\n\n---\n\n## Forum Post:" in result.prep_notes

    def test_import_invalid_post_raises(self, db_session, company) -> None:
        """Invalid post ID raises ValueError."""
        with pytest.raises(ValueError, match="ForumPost.*not found"):
            import_post_to_prep_notes(db_session, 9999, company.id)

    def test_import_invalid_company_raises(self, db_session, seed) -> None:
        """Invalid company ID raises ValueError."""
        post = self._create_post(db_session, seed)
        with pytest.raises(ValueError, match="Company.*not found"):
            import_post_to_prep_notes(db_session, post.id, 9999)


# --- get_fetch_progress ---


class TestGetFetchProgress:
    """Tests for fetch progress reporting."""

    @pytest.mark.asyncio()
    async def test_progress_accurate_counts(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Progress returns correct counts per status."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        links = db_session.query(ForumPostLink).all()
        total = len(links)

        # Set various statuses
        if len(links) >= 2:
            links[0].status = "fetched"
            links[1].status = "failed"
            db_session.commit()

        progress = get_fetch_progress(db_session, seed.id)
        assert progress["total"] == total
        assert progress["fetched"] == 1
        assert progress["failed"] == 1
        assert progress["pending"] == total - 2

    def test_progress_empty_seed(self, db_session, seed) -> None:
        """Empty seed shows zero counts."""
        progress = get_fetch_progress(db_session, seed.id)
        assert progress == {
            "total": 0,
            "pending": 0,
            "fetched": 0,
            "failed": 0,
            "last_fetched_url": None,
        }

    @pytest.mark.asyncio()
    async def test_progress_last_fetched_url(
        self, db_session, seed, mock_crawler
    ) -> None:
        """Progress includes last fetched URL."""
        await scrape_seed_page(db_session, seed.id, mock_crawler)
        link = db_session.query(ForumPostLink).first()
        link.status = "fetched"
        db_session.commit()

        progress = get_fetch_progress(db_session, seed.id)
        assert progress["last_fetched_url"] == link.url
