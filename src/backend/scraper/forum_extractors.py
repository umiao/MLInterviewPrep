"""HTML content extraction for 1point3acres forum pages."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.backend.scraper.extractors import compute_content_hash  # noqa: F401


def extract_post_links(html: str, base_url: str) -> list[dict]:
    """Extract post links from a forum tag/index page.

    Parses the ul.hotlist structure used by 1point3acres to list threads.
    Each li contains an anchor with a relative href and a div with the title.

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

    hotlist = soup.select("ul.hotlist li a")
    for idx, anchor in enumerate(hotlist):
        href = anchor.get("href", "")
        if not href:
            continue

        # Title is in the first div's text (excluding the span.by)
        title_div = anchor.select_one("div")
        if title_div:
            # Get text excluding child span elements (which hold author info)
            by_span = title_div.select_one("span.by")
            if by_span:
                by_span.decompose()
            title = title_div.get_text(strip=True)
        else:
            title = anchor.get_text(strip=True)

        abs_url = urljoin(base_url, href)

        results.append({
            "url": abs_url,
            "title": title,
            "order": idx,
        })

    return results


def extract_post_content(html: str) -> dict:
    """Extract content from an individual forum post page.

    Parses the first (OP) post from a 1point3acres thread page.
    Strips font.jammer elements (anti-scraping noise) before extracting text.

    Args:
        html: Raw HTML of the post page.

    Returns:
        Dict with keys: title, body, external_post_id, author, date.
        Returns empty dict if parsing fails.
    """
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # Title from postlist h2
    title = ""
    h2 = soup.select_one("div.postlist h2")
    if h2:
        title = h2.get_text(strip=True)

    # First OP post body: first span[itemprop=articleBody]
    body = ""
    body_span = soup.select_one("div.message span[itemprop=articleBody]")
    if body_span:
        # Strip jammer elements before extracting text
        for jammer in body_span.select("font.jammer"):
            jammer.decompose()
        body = body_span.get_text(separator="\n", strip=True)

    # External post ID from div.display.pi itemid attr (pidNNNNN)
    external_post_id = ""
    display_div = soup.select_one("div.display.pi")
    if display_div:
        item_id = display_div.get("itemid", "")
        if item_id.startswith("pid"):
            external_post_id = item_id[3:]  # Strip "pid" prefix

    # Author from first itemprop=author element
    author = ""
    author_el = soup.select_one("[itemprop=author]")
    if author_el:
        author = author_el.get_text(strip=True)

    # Date from meta[itemprop=datePublished] content attr
    date = ""
    date_meta = soup.select_one("meta[itemprop=datePublished]")
    if date_meta:
        date = date_meta.get("content", "")

    return {
        "title": title,
        "body": body,
        "external_post_id": external_post_id,
        "author": author,
        "date": date,
    }
