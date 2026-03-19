"""Tests for PlaywrightCrawler CDP attach and cookie fallback methods."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.backend.scraper.crawler import PlaywrightCrawler


@pytest.fixture()
def crawler() -> PlaywrightCrawler:
    """Return a PlaywrightCrawler instance."""
    return PlaywrightCrawler()


# ---------------------------------------------------------------------------
# fetch_page_cdp
# ---------------------------------------------------------------------------

class TestFetchPageCdp:
    """Tests for the CDP-based fetch method."""

    @pytest.mark.asyncio()
    async def test_returns_html_on_success(self, crawler: PlaywrightCrawler) -> None:
        """CDP fetch returns page HTML on success."""
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html>CDP</html>"
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()

        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = MagicMock()
        mock_browser.contexts = [mock_context]
        mock_browser.close = MagicMock()

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.connect_over_cdp = AsyncMock(
            return_value=mock_browser
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            result = await crawler.fetch_page_cdp(
                "https://example.com", port=9222, delay=(0, 0)
            )

        assert result == "<html>CDP</html>"
        mock_pw_instance.chromium.connect_over_cdp.assert_awaited_once_with(
            "http://localhost:9222"
        )
        mock_page.close.assert_awaited_once()
        # Browser should NOT be fully closed -- only disconnected
        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio()
    async def test_returns_empty_on_connection_error(
        self, crawler: PlaywrightCrawler
    ) -> None:
        """CDP fetch returns empty string when connection fails."""
        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.connect_over_cdp = AsyncMock(
            side_effect=ConnectionError("refused")
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            result = await crawler.fetch_page_cdp(
                "https://example.com", delay=(0, 0)
            )

        assert result == ""

    @pytest.mark.asyncio()
    async def test_rate_limiting_applied(self, crawler: PlaywrightCrawler) -> None:
        """CDP fetch calls asyncio.sleep with a value in the delay range."""
        sleep_values: list[float] = []

        async def capture_sleep(val: float) -> None:
            sleep_values.append(val)

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.connect_over_cdp = AsyncMock(
            side_effect=ConnectionError("test")
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", side_effect=capture_sleep
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            await crawler.fetch_page_cdp(
                "https://example.com", delay=(2, 5)
            )

        assert len(sleep_values) == 1
        assert 2 <= sleep_values[0] <= 5

    @pytest.mark.asyncio()
    async def test_custom_port(self, crawler: PlaywrightCrawler) -> None:
        """CDP fetch uses the specified port."""
        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.connect_over_cdp = AsyncMock(
            side_effect=ConnectionError("test")
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            await crawler.fetch_page_cdp(
                "https://example.com", port=9333, delay=(0, 0)
            )

        mock_pw_instance.chromium.connect_over_cdp.assert_awaited_once_with(
            "http://localhost:9333"
        )


# ---------------------------------------------------------------------------
# fetch_page_with_cookie
# ---------------------------------------------------------------------------

class TestFetchPageWithCookie:
    """Tests for the cookie-based fetch method."""

    @pytest.mark.asyncio()
    async def test_returns_html_on_success(self, crawler: PlaywrightCrawler) -> None:
        """Cookie fetch returns page HTML on success."""
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html>Cookie</html>"
        mock_page.goto = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.add_cookies = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            result = await crawler.fetch_page_with_cookie(
                "https://example.com/page",
                cookie_str="session=abc123; token=xyz",
                delay=(0, 0),
            )

        assert result == "<html>Cookie</html>"
        mock_pw_instance.chromium.launch.assert_awaited_once_with(headless=True)
        mock_browser.close.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_cookies_parsed_correctly(self, crawler: PlaywrightCrawler) -> None:
        """Cookie string is parsed into correct cookie dicts."""
        captured_cookies: list[list[dict]] = []  # type: ignore[type-arg]

        mock_page = AsyncMock()
        mock_page.content.return_value = "<html></html>"

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        async def capture_add_cookies(cookies: list[dict]) -> None:  # type: ignore[type-arg]
            captured_cookies.append(cookies)

        mock_context.add_cookies = AsyncMock(side_effect=capture_add_cookies)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            await crawler.fetch_page_with_cookie(
                "https://www.1point3acres.com/bbs/thread-123.html",
                cookie_str="sid=abc; token=def; flag=1",
                delay=(0, 0),
            )

        assert len(captured_cookies) == 1
        cookies = captured_cookies[0]
        assert len(cookies) == 3
        assert cookies[0] == {
            "name": "sid",
            "value": "abc",
            "domain": "www.1point3acres.com",
            "path": "/",
        }
        assert cookies[1]["name"] == "token"
        assert cookies[1]["value"] == "def"
        assert cookies[2]["name"] == "flag"

    @pytest.mark.asyncio()
    async def test_returns_empty_on_error(self, crawler: PlaywrightCrawler) -> None:
        """Cookie fetch returns empty string on error."""
        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(
            side_effect=RuntimeError("launch failed")
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            result = await crawler.fetch_page_with_cookie(
                "https://example.com",
                cookie_str="a=b",
                delay=(0, 0),
            )

        assert result == ""

    @pytest.mark.asyncio()
    async def test_empty_cookie_string(self, crawler: PlaywrightCrawler) -> None:
        """Cookie fetch works with empty cookie string (no cookies added)."""
        mock_page = AsyncMock()
        mock_page.content.return_value = "<html>NoCookies</html>"

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.add_cookies = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", new_callable=AsyncMock
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            result = await crawler.fetch_page_with_cookie(
                "https://example.com",
                cookie_str="",
                delay=(0, 0),
            )

        assert result == "<html>NoCookies</html>"
        mock_context.add_cookies.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_rate_limiting_applied(self, crawler: PlaywrightCrawler) -> None:
        """Cookie fetch calls asyncio.sleep within the delay range."""
        sleep_values: list[float] = []

        async def capture_sleep(val: float) -> None:
            sleep_values.append(val)

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium.launch = AsyncMock(
            side_effect=RuntimeError("test")
        )
        mock_pw_instance.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_instance.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.backend.scraper.crawler.asyncio.sleep", side_effect=capture_sleep
        ), patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_instance,
        ):
            await crawler.fetch_page_with_cookie(
                "https://example.com",
                cookie_str="a=b",
                delay=(3, 7),
            )

        assert len(sleep_values) == 1
        assert 3 <= sleep_values[0] <= 7


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

class TestConfigSettings:
    """Tests for new config settings."""

    def test_onepoint3acres_cookie_default(self) -> None:
        """ONEPOINT3ACRES_COOKIE defaults to empty string."""
        from src.backend.config import Settings

        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
            ANTHROPIC_API_KEY="",
            DATABASE_URL="sqlite:///test.db",
        )
        assert settings.ONEPOINT3ACRES_COOKIE == ""

    def test_chrome_debug_port_default(self) -> None:
        """CHROME_DEBUG_PORT defaults to 9222."""
        from src.backend.config import Settings

        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
            ANTHROPIC_API_KEY="",
            DATABASE_URL="sqlite:///test.db",
        )
        assert settings.CHROME_DEBUG_PORT == 9222
