"""Tests for site configs module."""
import pytest

from src.backend.scraper.site_configs import get_config


def test_get_config_blind():
    """get_config returns valid SiteConfig for blind."""
    config = get_config("blind")
    assert config.base_url == "https://www.teamblind.com"
    assert "post_list" in config.selectors


def test_get_config_all_sites():
    """All configured sites return valid config."""
    for site in ("blind", "1point3acres", "leetcode_discuss"):
        config = get_config(site)
        assert config.base_url
        assert config.rate_limit_seconds[0] < config.rate_limit_seconds[1]


def test_get_config_unknown():
    """Unknown site raises ValueError."""
    with pytest.raises(ValueError, match="Unknown site"):
        get_config("unknown_site")
