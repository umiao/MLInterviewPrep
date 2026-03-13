"""Playwright-based web crawler."""
import asyncio
import logging
import random

from src.backend.scraper.site_configs import SiteConfig

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


class PlaywrightCrawler:
    """Headless browser crawler with rate limiting and UA rotation."""

    async def fetch_page(self, url: str, site_config: SiteConfig) -> str:
        """Fetch page HTML with rate limiting and UA rotation.

        Args:
            url: URL to fetch.
            site_config: Site configuration with rate limits.

        Returns:
            Page HTML content, or empty string on error.
        """
        delay = random.uniform(*site_config.rate_limit_seconds)
        await asyncio.sleep(delay)

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page(
                        user_agent=random.choice(USER_AGENTS)
                    )
                    await page.goto(
                        url, wait_until="domcontentloaded", timeout=30000
                    )
                    html = await page.content()
                    return html
                finally:
                    await browser.close()
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", url, e)
            return ""
