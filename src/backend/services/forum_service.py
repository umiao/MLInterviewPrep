"""Forum scraping service layer -- two-phase scrape + import to prep notes."""

import asyncio
import logging
import random
from datetime import datetime
from re import match as re_match

from sqlalchemy.orm import Session

from src.backend.config import get_settings
from src.backend.models.company import Company, CompanyDocument
from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed
from src.backend.scraper.crawler import PlaywrightCrawler
from src.backend.scraper.extractors import compute_content_hash
from src.backend.scraper.forum_extractors import (
    derive_page_url,
    extract_max_page,
    extract_post_content,
    extract_post_links,
)
from src.backend.scraper.site_configs import get_config

logger = logging.getLogger(__name__)

# Posts shorter than this are likely login walls or empty pages
MIN_POST_CONTENT_LENGTH = 50


def _extract_external_id(url: str) -> str | None:
    """Extract external post ID from a forum URL.

    Looks for /thread-NNNNN pattern in 1point3acres URLs.

    Args:
        url: Absolute URL of the post.

    Returns:
        The numeric ID string, or None if not found.
    """
    m = re_match(r".*?/thread-(\d+)", url)
    return m.group(1) if m else None


def _is_cdp_available(port: int = 9222) -> bool:
    """Quick TCP probe to check if Chrome debug port is listening.

    Args:
        port: Chrome debug port to check.

    Returns:
        True if port accepts connections, False otherwise.
    """
    import socket

    try:
        with socket.create_connection(("localhost", port), timeout=0.5):
            return True
    except (ConnectionRefusedError, OSError):
        return False


async def _fetch_html(
    crawler: PlaywrightCrawler, url: str, port: int = 9222
) -> str:
    """Fetch HTML via CDP (if available) or cookie method.

    Probes the CDP port first with a fast TCP check (~0.5s) to avoid
    the expensive Playwright startup when no Chrome debug instance is running.

    Args:
        crawler: PlaywrightCrawler instance.
        url: URL to fetch.
        port: Chrome debug port for CDP.

    Returns:
        HTML string (may be empty on failure).
    """
    if _is_cdp_available(port):
        html = await crawler.fetch_page_cdp(url, port=port)
        if html:
            return html
        logger.info("CDP connected but fetch failed for %s, trying cookie", url)

    settings = get_settings()
    cookie = settings.ONEPOINT3ACRES_COOKIE
    if cookie:
        html = await crawler.fetch_page_with_cookie(url, cookie)
        return html

    logger.warning("No CDP and no cookie configured, cannot fetch %s", url)
    return ""


def _upsert_links_from_html(
    db: Session,
    seed_id: int,
    html: str,
    base_url: str,
    order_offset: int = 0,
) -> tuple[list[ForumPostLink], int]:
    """Extract post links from HTML and upsert into the database.

    Idempotent -- existing links get title updates, new links are inserted.

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed.
        html: Raw HTML of the index page.
        base_url: Base URL for resolving relative hrefs.
        order_offset: Shifts fetch_order for pages beyond 1.

    Returns:
        Tuple of (all_links, new_count) where new_count is genuinely new links.
    """
    raw_links = extract_post_links(html, base_url)
    result: list[ForumPostLink] = []
    new_count = 0

    for item in raw_links:
        url = item["url"]
        title = item["title"]
        order = item["order"] + order_offset
        ext_id = _extract_external_id(url)

        # Check for existing link by URL (unique constraint)
        existing = db.query(ForumPostLink).filter(ForumPostLink.url == url).first()
        if existing:
            # Update title if changed
            if title and existing.title != title:
                existing.title = title
            result.append(existing)
            continue

        # Check external_post_id conflict
        if ext_id:
            conflict = (
                db.query(ForumPostLink)
                .filter(ForumPostLink.external_post_id == ext_id)
                .first()
            )
            if conflict:
                if conflict.forum_seed_id == seed_id:
                    # Same seed, different URL: treat as duplicate
                    result.append(conflict)
                else:
                    logger.info(
                        "external_post_id %s already exists from seed %d, skipping",
                        ext_id,
                        conflict.forum_seed_id,
                    )
                continue

        link = ForumPostLink(
            forum_seed_id=seed_id,
            url=url,
            external_post_id=ext_id,
            title=title,
            fetch_order=order,
        )
        db.add(link)
        result.append(link)
        new_count += 1

    db.flush()
    return result, new_count


async def scrape_seed_page(
    db: Session, seed_id: int, crawler: PlaywrightCrawler
) -> list[ForumPostLink]:
    """Phase A: Fetch index page for a seed and extract/upsert post links.

    Idempotent -- re-running discovers new posts without duplicating existing ones.
    Updates titles if they changed for existing links.

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed to scrape.
        crawler: PlaywrightCrawler for fetching pages.

    Returns:
        List of ForumPostLink objects (both new and updated).

    Raises:
        ValueError: If seed_id not found.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise ValueError(f"ForumSeed {seed_id} not found")

    html = await _fetch_html(crawler, seed.url)
    if not html:
        logger.warning("No HTML fetched for seed %d (%s)", seed_id, seed.url)
        return []

    result, _new_count = _upsert_links_from_html(db, seed_id, html, seed.url)

    seed.last_scraped_at = datetime.utcnow()
    db.commit()

    return result


async def scrape_seed_pages(
    db: Session,
    seed_id: int,
    crawler: PlaywrightCrawler,
    max_pages: int = 1,
    auto_detect: bool = True,
    start_page: int = 1,
) -> dict:
    """Multi-page scraping: fetch multiple index pages for a seed.

    Fetches pages starting from start_page, optionally detects max pages
    from pagination, then loops through subsequent pages with rate limiting
    and early stop (3 consecutive pages with 0 new links).

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed to scrape.
        crawler: PlaywrightCrawler for fetching pages.
        max_pages: Maximum number of pages to scrape.
        auto_detect: If True, cap max_pages by detected pagination max.
        start_page: Page number to start from (default 1). Use to resume
            from where a previous scrape left off.

    Returns:
        Dict with pages_scraped, total_links, new_links, max_page_detected,
        stopped_early, last_page.

    Raises:
        ValueError: If seed_id not found.
    """
    seed = db.query(ForumSeed).filter(ForumSeed.id == seed_id).first()
    if not seed:
        raise ValueError(f"ForumSeed {seed_id} not found")

    # First page (may be start_page, not necessarily page 1)
    first_url = derive_page_url(seed.url, start_page) if start_page > 1 else seed.url
    html = await _fetch_html(crawler, first_url)
    if not html:
        logger.warning("No HTML fetched for seed %d (%s)", seed_id, first_url)
        return {
            "pages_scraped": 0,
            "total_links": 0,
            "new_links": 0,
            "max_page_detected": 1,
            "stopped_early": False,
            "last_page": start_page,
        }

    first_links, first_new = _upsert_links_from_html(db, seed_id, html, seed.url)
    total_links = len(first_links)
    new_links = first_new
    pages_scraped = 1
    last_page = start_page

    # Commit first page immediately so progress is durable
    seed.last_scraped_at = datetime.utcnow()
    seed.last_scraped_page = start_page
    db.commit()

    # Detect max page from pagination (always fetch page 1 for this if needed)
    if auto_detect and start_page == 1:
        detected_max = extract_max_page(html)
    elif auto_detect:
        # Fetch page 1 just for pagination detection
        page1_html = await _fetch_html(crawler, seed.url)
        detected_max = extract_max_page(page1_html) if page1_html else max_pages
    else:
        detected_max = max_pages
    effective_max = min(max_pages, detected_max) if auto_detect else max_pages

    # Rate limit config
    config = get_config(seed.source_site)
    rate_low, rate_high = config.rate_limit_seconds

    stopped_early = False
    # Count first page toward the zero-new streak
    zero_new_streak = 1 if first_new == 0 else 0
    cumulative_links = len(first_links)

    # Early stop check for first page (all 3 consecutive zeros already seen)
    if zero_new_streak >= 3:
        stopped_early = True

    if not stopped_early:
        for page in range(start_page + 1, start_page + effective_max):
            # Rate limit
            delay = random.uniform(rate_low, rate_high)
            await asyncio.sleep(delay)

            # Derive URL and fetch
            page_url = derive_page_url(seed.url, page)
            page_html = await _fetch_html(crawler, page_url)
            if not page_html:
                logger.warning("Page %d: empty response, skipping", page)
                pages_scraped += 1
                last_page = page
                continue

            page_links, page_new = _upsert_links_from_html(
                db, seed_id, page_html, seed.url, order_offset=cumulative_links
            )
            page_total = len(page_links)
            cumulative_links += page_total
            total_links += page_total
            new_links += page_new
            pages_scraped += 1
            last_page = page

            # Commit per-page: crash-safe, progress is never lost
            seed.last_scraped_at = datetime.utcnow()
            seed.last_scraped_page = page
            db.commit()

            logger.info(
                "Page %d/%d: %d links (%d new), cumulative %d",
                page,
                start_page + effective_max - 1,
                page_total,
                page_new,
                cumulative_links,
            )

            # Early stop: 3 consecutive pages with 0 new links
            if page_new == 0:
                zero_new_streak += 1
            else:
                zero_new_streak = 0

            if zero_new_streak >= 3:
                stopped_early = True
                break

    return {
        "pages_scraped": pages_scraped,
        "total_links": total_links,
        "new_links": new_links,
        "max_page_detected": detected_max,
        "stopped_early": stopped_early,
        "last_page": last_page,
    }


async def fetch_single_post(
    db: Session, link_id: int, crawler: PlaywrightCrawler
) -> ForumPost | None:
    """Phase B: Fetch an individual post page for a ForumPostLink.

    Skips if already fetched. On success creates ForumPost with content hash.
    On failure sets status=failed and increments retry_count.

    Args:
        db: Database session.
        link_id: ID of the ForumPostLink to fetch.
        crawler: PlaywrightCrawler for fetching pages.

    Returns:
        ForumPost on success, None on skip or failure.

    Raises:
        ValueError: If link_id not found.
    """
    link = db.query(ForumPostLink).filter(ForumPostLink.id == link_id).first()
    if not link:
        raise ValueError(f"ForumPostLink {link_id} not found")

    if link.status == "fetched":
        logger.info("Link %d already fetched, skipping", link_id)
        return None

    html = await _fetch_html(crawler, link.url)
    if not html:
        link.status = "failed"
        link.retry_count = (link.retry_count or 0) + 1
        link.last_error = "Empty HTML response"
        db.commit()
        return None

    content = extract_post_content(html)
    if not content or not content.get("body"):
        link.status = "failed"
        link.retry_count = (link.retry_count or 0) + 1
        link.last_error = "Failed to extract post content"
        db.commit()
        return None

    raw_text = content["body"]

    # Content quality check: reject suspiciously short posts (login wall, empty)
    if len(raw_text.strip()) < MIN_POST_CONTENT_LENGTH:
        link.status = "failed"
        link.retry_count = (link.retry_count or 0) + 1
        link.last_error = (
            f"Content too short ({len(raw_text.strip())} chars) "
            f"-- possible login wall"
        )
        db.commit()
        return None

    content_hash = compute_content_hash(raw_text)

    # Content dedup warning
    existing_hash = (
        db.query(ForumPost).filter(ForumPost.content_hash == content_hash).first()
    )
    if existing_hash:
        logger.warning(
            "Duplicate content hash %s (existing post %d)", content_hash, existing_hash.id
        )

    post = ForumPost(
        forum_post_link_id=link_id,
        raw_text=raw_text,
        content_hash=content_hash,
        author=content.get("author", ""),
        published_at=content.get("date", ""),
        fetched_at=datetime.utcnow(),
    )
    db.add(post)

    link.status = "fetched"
    # Update external_post_id from content if we got one and link didn't have it
    if content.get("external_post_id") and not link.external_post_id:
        link.external_post_id = content["external_post_id"]

    db.commit()
    return post


async def fetch_next_unfetched(
    db: Session, seed_id: int, crawler: PlaywrightCrawler
) -> ForumPost | None:
    """Fetch the next pending post link for a seed.

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed.
        crawler: PlaywrightCrawler for fetching pages.

    Returns:
        ForumPost if one was fetched, None if all done.
    """
    link = (
        db.query(ForumPostLink)
        .filter(
            ForumPostLink.forum_seed_id == seed_id,
            ForumPostLink.status == "pending",
        )
        .order_by(ForumPostLink.fetch_order)
        .first()
    )
    if not link:
        return None

    return await fetch_single_post(db, link.id, crawler)


async def retry_failed(
    db: Session, seed_id: int, crawler: PlaywrightCrawler
) -> list[ForumPost]:
    """Reset failed links to pending and re-fetch them.

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed.
        crawler: PlaywrightCrawler for fetching pages.

    Returns:
        List of successfully fetched ForumPost objects.
    """
    failed_links = (
        db.query(ForumPostLink)
        .filter(
            ForumPostLink.forum_seed_id == seed_id,
            ForumPostLink.status == "failed",
        )
        .all()
    )

    for link in failed_links:
        link.status = "pending"
        link.retry_count = 0
        link.last_error = None

    db.commit()

    results: list[ForumPost] = []
    for link in failed_links:
        post = await fetch_single_post(db, link.id, crawler)
        if post:
            results.append(post)

    return results


def import_post_to_document(
    db: Session, post_id: int, company_id: int, doc_id: int | None = None
) -> CompanyDocument:
    """Append forum post content to a company document.

    If doc_id is provided, appends to that document. Otherwise creates or
    finds a document titled after the seed label for the post's seed.

    Args:
        db: Database session.
        post_id: ID of the ForumPost to import.
        company_id: ID of the target Company.
        doc_id: Optional target document ID. Auto-resolves if None.

    Returns:
        Updated CompanyDocument object.

    Raises:
        ValueError: If post, company, or document not found.
    """
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise ValueError(f"ForumPost {post_id} not found")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    # Resolve target document
    if doc_id:
        doc = (
            db.query(CompanyDocument)
            .filter(
                CompanyDocument.id == doc_id,
                CompanyDocument.company_id == company_id,
            )
            .first()
        )
        if not doc:
            raise ValueError(f"CompanyDocument {doc_id} not found")
    else:
        # Auto-resolve: use seed label or default title
        seed = post.post_link.forum_seed
        doc_title = seed.label or f"{seed.source_site} posts"
        doc = (
            db.query(CompanyDocument)
            .filter(
                CompanyDocument.company_id == company_id,
                CompanyDocument.title == doc_title,
            )
            .first()
        )
        if not doc:
            doc = CompanyDocument(
                company_id=company_id,
                title=doc_title,
                content="",
                source_type="forum_import",
            )
            db.add(doc)
            db.flush()

    # Build header with metadata
    link = post.post_link
    title = link.title or "Untitled"
    source_url = link.url
    fetched_at = post.fetched_at.isoformat() if post.fetched_at else "unknown"
    ext_id = link.external_post_id or "N/A"

    header = (
        f"## Forum Post: {title}\n"
        f"**Source**: {source_url}\n"
        f"**Fetched**: {fetched_at}\n"
        f"**Post ID**: {post.id} | **External ID**: {ext_id}\n"
    )
    content = header + "\n" + post.raw_text

    if not doc.content:
        doc.content = content
    else:
        doc.content = doc.content + "\n\n---\n\n" + content

    db.commit()
    db.refresh(doc)
    return doc


def get_fetch_progress(db: Session, seed_id: int) -> dict:
    """Get fetch progress statistics for a seed.

    Args:
        db: Database session.
        seed_id: ID of the ForumSeed.

    Returns:
        Dict with total, pending, fetched, failed counts and last_fetched_url.
    """
    links = (
        db.query(ForumPostLink)
        .filter(ForumPostLink.forum_seed_id == seed_id)
        .all()
    )

    total = len(links)
    pending = sum(1 for lk in links if lk.status == "pending")
    fetched = sum(1 for lk in links if lk.status == "fetched")
    failed = sum(1 for lk in links if lk.status == "failed")

    last_fetched_url = None
    fetched_links = [lk for lk in links if lk.status == "fetched"]
    if fetched_links:
        # Get the most recently discovered fetched link
        last_fetched_url = max(fetched_links, key=lambda lk: lk.id).url

    return {
        "total": total,
        "pending": pending,
        "fetched": fetched,
        "failed": failed,
        "last_fetched_url": last_fetched_url,
    }
