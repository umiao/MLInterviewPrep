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

    async def fetch_page_cdp(
        self,
        url: str,
        port: int = 9222,
        delay: tuple[int, int] = (5, 15),
    ) -> str:
        """Fetch page by attaching to a running Chrome instance via CDP.

        Connects to Chrome DevTools Protocol on the given port, opens a new
        page in the existing browser context, navigates to the URL, and
        returns the HTML.  The browser itself is NOT closed -- only the page.

        Args:
            url: URL to fetch.
            port: Chrome debug port (default 9222).
            delay: Min/max seconds for rate-limiting sleep.

        Returns:
            Page HTML content, or empty string on error.
        """
        await asyncio.sleep(random.uniform(*delay))

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(
                    f"http://localhost:{port}"
                )
                try:
                    # Use the first (default) browser context
                    context = browser.contexts[0]
                    page = await context.new_page()
                    try:
                        await page.goto(
                            url, wait_until="domcontentloaded", timeout=30000
                        )
                        html = await page.content()
                        return html
                    finally:
                        await page.close()
                finally:
                    # Disconnect from CDP without closing the browser
                    browser.close()
        except Exception as e:
            logger.warning("CDP fetch failed for %s: %s", url, e)
            return ""

    async def fetch_page_with_cookie(
        self,
        url: str,
        cookie_str: str,
        delay: tuple[int, int] = (5, 15),
    ) -> str:
        """Fetch page using a headless browser with injected cookies.

        Launches a headless Chromium instance, parses the cookie string,
        adds cookies to the browser context, then navigates to the URL.

        Args:
            url: URL to fetch.
            cookie_str: Raw cookie header string (``key=val; key2=val2``).
            delay: Min/max seconds for rate-limiting sleep.

        Returns:
            Page HTML content, or empty string on error.
        """
        await asyncio.sleep(random.uniform(*delay))

        try:
            from urllib.parse import urlparse

            from playwright.async_api import async_playwright

            parsed = urlparse(url)
            domain = parsed.hostname or ""

            cookies = []
            for pair in cookie_str.split(";"):
                pair = pair.strip()
                if "=" not in pair:
                    continue
                name, value = pair.split("=", 1)
                cookies.append(
                    {
                        "name": name.strip(),
                        "value": value.strip(),
                        "domain": domain,
                        "path": "/",
                    }
                )

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    context = await browser.new_context(
                        user_agent=random.choice(USER_AGENTS)
                    )
                    if cookies:
                        await context.add_cookies(cookies)
                    page = await context.new_page()
                    await page.goto(
                        url, wait_until="domcontentloaded", timeout=30000
                    )
                    html = await page.content()
                    return html
                finally:
                    await browser.close()
        except Exception as e:
            logger.warning("Cookie fetch failed for %s: %s", url, e)
            return ""
