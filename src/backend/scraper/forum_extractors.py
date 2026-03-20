"""HTML content extraction for 1point3acres forum pages."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.backend.scraper.extractors import compute_content_hash  # noqa: F401

# Matches 1point3acres tag index URLs like tag-415-1.html
_TAG_PAGE_RE = re.compile(r"(tag-\d+-)(\d+)(\.html)")


def derive_page_url(base_url: str, page: int) -> str:
    """Replace the page number in a 1point3acres tag index URL.

    Args:
        base_url: A URL matching the pattern tag-{id}-{page}.html.
        page: The target page number.

    Returns:
        URL with the page number replaced.

    Raises:
        ValueError: If base_url does not match the expected pattern.
    """
    match = _TAG_PAGE_RE.search(base_url)
    if not match:
        raise ValueError(
            f"URL does not match tag-N-N.html pattern: {base_url}"
        )
    return base_url[: match.start()] + match.group(1) + str(page) + match.group(3) + base_url[match.end():]


def extract_max_page(html: str) -> int:
    """Extract the maximum page number from a forum index page's pagination.

    Looks for the div.pg pagination container. Tries a.last href first,
    then falls back to the '/ NNN' span text.

    Args:
        html: Raw HTML of the index/tag page.

    Returns:
        Maximum page number, or 1 if no pagination found.
    """
    if not html:
        return 1

    soup = BeautifulSoup(html, "html.parser")
    pg_div = soup.select_one("div.pg")
    if not pg_div:
        return 1

    # Try a.last href
    last_link = pg_div.select_one("a.last")
    if last_link:
        href = last_link.get("href", "")
        match = _TAG_PAGE_RE.search(href)
        if match:
            return int(match.group(2))

    # Fallback: span with '/ NNN' text
    for span in pg_div.select("span"):
        title = span.get("title", "")
        text = title or span.get_text()
        page_match = re.search(r"/\s*(\d+)", text)
        if page_match:
            return int(page_match.group(1))

    return 1


def extract_post_links(html: str, base_url: str) -> list[dict]:
    """Extract post links from a forum tag/index page.

    Supports two 1point3acres page layouts:
    1. Table layout (div.bm_c): thread links in th cells within table rows.
    2. Hotlist layout (ul.hotlist): thread links in li > a elements.

    Args:
        html: Raw HTML of the index/tag page.
        base_url: Base URL for resolving relative hrefs to absolute URLs.

    Returns:
        List of dicts with keys: url (absolute), title (str), order (int).
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results: list[dict] = []

    # Strategy 1: Table layout (div.bm_c > table > tr > th > a[href*=thread-])
    thread_re = re.compile(r"thread-\d+")
    th_links = soup.select("th a[href]")
    thread_anchors = [a for a in th_links if thread_re.search(a.get("href", ""))]
    if thread_anchors:
        seen_hrefs: set[str] = set()
        idx = 0
        for anchor in thread_anchors:
            href = anchor.get("href", "")
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)
            title = anchor.get_text(strip=True)
            abs_url = urljoin(base_url, href)
            results.append({"url": abs_url, "title": title, "order": idx})
            idx += 1
        return results

    # Strategy 2: Hotlist layout (ul.hotlist li a)
    hotlist = soup.select("ul.hotlist li a")
    for idx, anchor in enumerate(hotlist):
        href = anchor.get("href", "")
        if not href:
            continue

        # Title is in the first div's text (excluding the span.by)
        title_div = anchor.select_one("div")
        if title_div:
            by_span = title_div.select_one("span.by")
            if by_span:
                by_span.decompose()
            title = title_div.get_text(strip=True)
        else:
            title = anchor.get_text(strip=True)

        abs_url = urljoin(base_url, href)
        results.append({"url": abs_url, "title": title, "order": idx})

    return results


def extract_post_content(html: str) -> dict:
    """Extract content from an individual forum post page.

    Parses the first (OP) post from a 1point3acres thread page.
    Strips font.jammer elements (anti-scraping noise) before extracting text.

    Supports two layouts found on 1point3acres:
    1. Modern layout: h1.ts title, [itemprop=articleBody] body, .authi author
    2. Legacy layout: div.postlist h2, div.message span body, div.display.pi id

    Args:
        html: Raw HTML of the post page.

    Returns:
        Dict with keys: title, body, external_post_id, author, date.
        Returns empty dict if parsing fails.
    """
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # Title: try h1.ts first (modern), then div.postlist h2 (legacy)
    title = ""
    h1 = soup.select_one("h1.ts")
    if h1:
        title = h1.get_text(strip=True)
    else:
        h2 = soup.select_one("div.postlist h2")
        if h2:
            title = h2.get_text(strip=True)

    # Strip common title prefixes like [面试经验]
    if title.startswith("[") and "]" in title:
        title = title[title.index("]") + 1 :].strip()

    # Body: first [itemprop=articleBody] (works in both layouts)
    body = ""
    body_el = soup.select_one("[itemprop=articleBody]")
    if not body_el:
        # Fallback: first td.t_f (Discuz table layout)
        body_el = soup.select_one("td.t_f")
    if body_el:
        for jammer in body_el.select("font.jammer"):
            jammer.decompose()
        body = body_el.get_text(separator="\n", strip=True)

    # External post ID: div.display.pi (legacy) or thread ID from URL in page
    external_post_id = ""
    display_div = soup.select_one("div.display.pi")
    if display_div:
        item_id = display_div.get("itemid", "")
        if item_id.startswith("pid"):
            external_post_id = item_id[3:]

    # Author: .authi text before nbsp (modern), or [itemprop=author] (legacy)
    # Pattern in .authi: "username\xa0timestamp|other_links"
    # The username is always before the first \xa0 (non-breaking space).
    author = ""
    authi = soup.select_one(".authi")
    if authi:
        raw = authi.get_text()
        # Split on non-breaking space -- username is before it
        parts = raw.split("\xa0", 1)
        author = parts[0].strip()
    else:
        author_el = soup.select_one("[itemprop=author]")
        if author_el:
            author = author_el.get_text(strip=True)

    # Date: meta[itemprop=datePublished] (legacy) or em#authorposton (modern)
    date = ""
    date_meta = soup.select_one("meta[itemprop=datePublished]")
    if date_meta:
        date = date_meta.get("content", "")
    else:
        em = soup.select_one("em[id^=authorposton]")
        if em:
            date = em.get_text(strip=True)

    return {
        "title": title,
        "body": body,
        "external_post_id": external_post_id,
        "author": author,
        "date": date,
    }
