"""Site-specific scraper configurations."""
from dataclasses import dataclass


@dataclass
class SiteConfig:
    """Configuration for scraping a specific site."""

    base_url: str
    selectors: dict[str, str]
    rate_limit_seconds: tuple[int, int]


SITE_CONFIGS: dict[str, SiteConfig] = {
    "blind": SiteConfig(
        base_url="https://www.teamblind.com",
        selectors={
            "post_list": "div.post-item",
            "post_title": "h3.title",
            "post_body": "div.body-text",
            "next_page": "a.next-page",
        },
        rate_limit_seconds=(15, 30),
    ),
    "1point3acres": SiteConfig(
        base_url="https://www.1point3acres.com",
        selectors={
            "post_list": "div.thread-item",
            "post_title": "a.thread-title",
            "post_body": "div.thread-content",
        },
        rate_limit_seconds=(20, 45),
    ),
    "leetcode_discuss": SiteConfig(
        base_url="https://leetcode.com/discuss",
        selectors={
            "post_list": "div.topic-item",
            "post_title": "a.title-link",
            "post_body": "div.discuss-markdown-container",
        },
        rate_limit_seconds=(10, 20),
    ),
}


def get_config(source_site: str) -> SiteConfig:
    """Get scraper config for a site.

    Args:
        source_site: Site identifier.

    Returns:
        SiteConfig for the site.

    Raises:
        ValueError: If site is unknown.
    """
    if source_site not in SITE_CONFIGS:
        raise ValueError(
            f"Unknown site: {source_site}. Valid: {list(SITE_CONFIGS.keys())}"
        )
    return SITE_CONFIGS[source_site]
