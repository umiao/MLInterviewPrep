"""Tests for the scrape config YAML validator."""

import textwrap
from pathlib import Path

import pytest

from src.backend.scraper.scrape_config import ScrapeConfig, load_config


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    """Create a temp dir for config files."""
    return tmp_path


def _write_yaml(config_dir: Path, content: str) -> str:
    """Write YAML content to a temp file and return the path string."""
    path = config_dir / "test_seeds.yaml"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(path)


class TestLoadConfig:
    """Tests for load_config validation."""

    def test_valid_config(self, config_dir: Path) -> None:
        """Valid YAML parses correctly."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: LinkedIn
                seeds:
                  - url: "https://example.com/tag-123.html"
                    label: "linkedin-1p3a"
            defaults:
              mode: full
        """)
        config = load_config(path)
        assert isinstance(config, ScrapeConfig)
        assert len(config.companies) == 1
        assert config.companies[0].name == "LinkedIn"
        assert len(config.companies[0].seeds) == 1
        assert config.companies[0].seeds[0].url == "https://example.com/tag-123.html"
        assert config.companies[0].seeds[0].label == "linkedin-1p3a"
        assert config.defaults.mode == "full"

    def test_default_mode(self, config_dir: Path) -> None:
        """Defaults section is optional, mode defaults to 'full'."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
        """)
        config = load_config(path)
        assert config.defaults.mode == "full"

    def test_links_only_mode(self, config_dir: Path) -> None:
        """Mode 'links-only' is valid."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
            defaults:
              mode: links-only
        """)
        config = load_config(path)
        assert config.defaults.mode == "links-only"

    def test_unknown_top_level_key(self, config_dir: Path) -> None:
        """Unknown top-level key raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
            strat_page: 5
        """)
        with pytest.raises(ValueError, match="Unknown key.*strat_page"):
            load_config(path)

    def test_unknown_seed_key(self, config_dir: Path) -> None:
        """Unknown key in seed entry raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
                    max_pages: 10
        """)
        with pytest.raises(ValueError, match="Unknown key.*max_pages"):
            load_config(path)

    def test_unknown_defaults_key(self, config_dir: Path) -> None:
        """Unknown key in defaults raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
            defaults:
              mode: full
              rate_limit: 5
        """)
        with pytest.raises(ValueError, match="Unknown key.*rate_limit"):
            load_config(path)

    def test_missing_url(self, config_dir: Path) -> None:
        """Missing url in seed raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - label: "test"
        """)
        with pytest.raises(ValueError, match="missing required field 'url'"):
            load_config(path)

    def test_missing_label(self, config_dir: Path) -> None:
        """Missing label in seed raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
        """)
        with pytest.raises(ValueError, match="missing required field 'label'"):
            load_config(path)

    def test_empty_companies(self, config_dir: Path) -> None:
        """Empty companies list raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies: []
        """)
        with pytest.raises(ValueError, match="must not be empty"):
            load_config(path)

    def test_invalid_mode(self, config_dir: Path) -> None:
        """Invalid mode value raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: TestCo
                seeds:
                  - url: "https://example.com/page"
                    label: "test"
            defaults:
              mode: turbo
        """)
        with pytest.raises(ValueError, match="Invalid mode 'turbo'"):
            load_config(path)

    def test_file_not_found(self) -> None:
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path.yaml")

    def test_missing_company_name(self, config_dir: Path) -> None:
        """Missing company name raises ValueError."""
        path = _write_yaml(config_dir, """\
            companies:
              - seeds:
                  - url: "https://example.com/page"
                    label: "test"
        """)
        with pytest.raises(ValueError, match="missing required field 'name'"):
            load_config(path)

    def test_multiple_companies(self, config_dir: Path) -> None:
        """Multiple companies parse correctly."""
        path = _write_yaml(config_dir, """\
            companies:
              - name: LinkedIn
                seeds:
                  - url: "https://example.com/linkedin"
                    label: "linkedin"
              - name: DoorDash
                seeds:
                  - url: "https://example.com/doordash"
                    label: "doordash"
        """)
        config = load_config(path)
        assert len(config.companies) == 2
        assert config.companies[1].name == "DoorDash"

    def test_real_config_file(self) -> None:
        """The actual config/scrape_seeds.yaml parses without error."""
        config = load_config("config/scrape_seeds.yaml")
        assert len(config.companies) >= 1
