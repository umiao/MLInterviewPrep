"""HTML content extraction using BeautifulSoup."""
import hashlib

from bs4 import BeautifulSoup

from src.backend.scraper.site_configs import SITE_CONFIGS


def extract_posts(html: str, source_site: str) -> list[dict]:
    """Extract posts from HTML using site-specific selectors.

    Args:
        html: Raw HTML content.
        source_site: Site identifier for selector lookup.

    Returns:
        List of dicts with 'title', 'body_text', 'url' keys.
    """
    if not html or source_site not in SITE_CONFIGS:
        return []

    config = SITE_CONFIGS[source_site]
    soup = BeautifulSoup(html, "html.parser")
    posts = []

    post_elements = soup.select(config.selectors.get("post_list", ""))
    for el in post_elements:
        title_el = el.select_one(config.selectors.get("post_title", ""))
        body_el = el.select_one(config.selectors.get("post_body", ""))

        title = title_el.get_text(strip=True) if title_el else ""
        body_text = body_el.get_text(strip=True) if body_el else ""

        url = ""
        if title_el and title_el.name == "a":
            url = title_el.get("href", "")
        elif title_el:
            link = title_el.find("a")
            if link:
                url = link.get("href", "")

        if body_text:
            posts.append({
                "title": title,
                "body_text": body_text,
                "url": url,
            })

    return posts


def compute_content_hash(text: str) -> str:
    """Compute deterministic MD5 hash for content deduplication.

    Args:
        text: Text content to hash.

    Returns:
        Hex digest of MD5 hash.
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()
