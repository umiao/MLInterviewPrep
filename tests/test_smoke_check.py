"""Tests for scripts/smoke_check.py."""
import importlib.util
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import MagicMock, patch

import pytest

# Import smoke_check from scripts/ (not a package)
_script_path = Path(__file__).resolve().parent.parent / "scripts" / "smoke_check.py"
_spec = importlib.util.spec_from_file_location("smoke_check", _script_path)
smoke_check = importlib.util.module_from_spec(_spec)
sys.modules["smoke_check"] = smoke_check
_spec.loader.exec_module(smoke_check)

SmokeReport = smoke_check.SmokeReport
check_server_alive = smoke_check.check_server_alive
run_api_checks = smoke_check.run_api_checks
_page_slug = smoke_check._page_slug
_cleanup_old_screenshots = smoke_check._cleanup_old_screenshots
_save_screenshot = smoke_check._save_screenshot


class TestSmokeReport:
    """Tests for SmokeReport aggregation."""

    def test_empty_report_passes(self) -> None:
        report = SmokeReport()
        assert report.all_passed is True
        assert report.failed == []

    def test_all_pass(self) -> None:
        report = SmokeReport()
        report.add("check1", True, "ok")
        report.add("check2", True, "ok")
        assert report.all_passed is True
        assert len(report.failed) == 0

    def test_one_failure(self) -> None:
        report = SmokeReport()
        report.add("check1", True, "ok")
        report.add("check2", False, "bad")
        assert report.all_passed is False
        assert len(report.failed) == 1
        assert report.failed[0].name == "check2"

    def test_summary_format(self) -> None:
        report = SmokeReport()
        report.add("API /foo", True)
        report.add("API /bar", False, "got 0, need >= 1")
        s = report.summary()
        assert "1/2" in s
        assert "[FAIL]" in s
        assert "/bar" in s


class TestCheckServerAlive:
    """Tests for server liveness check."""

    def test_unreachable_server(self) -> None:
        assert check_server_alive("http://localhost:19999", "test") is False


class _MockAPIHandler(BaseHTTPRequestHandler):
    """Mock API handler for testing."""

    def do_GET(self) -> None:
        if self.path == "/api/baking/recipes":
            data = [{"id": i, "name": f"recipe_{i}"} for i in range(12)]
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.write = self.wfile.write
            self.wfile.write(body)
        elif self.path == "/api/problems":
            data = [{"id": 1, "title": "Two Sum"}]
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/system-design/topics":
            data = [{"slug": "rate-limiter"}]
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass  # Suppress request logging


@pytest.fixture()
def mock_api_server():
    """Start a mock API server on a random port."""
    server = HTTPServer(("127.0.0.1", 0), _MockAPIHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield port
    server.shutdown()


class TestRunAPIChecks:
    """Tests for API endpoint verification."""

    def test_api_checks_pass_with_mock(self, mock_api_server: int) -> None:
        report = SmokeReport()
        with patch.object(smoke_check, "BACKEND_URL", f"http://127.0.0.1:{mock_api_server}"):
            run_api_checks(report)
        assert report.all_passed is True
        assert len(report.results) == 3

    def test_api_checks_fail_on_unreachable(self) -> None:
        report = SmokeReport()
        with patch.object(smoke_check, "BACKEND_URL", "http://127.0.0.1:19999"):
            run_api_checks(report)
        assert report.all_passed is False
        assert len(report.failed) == 3


class TestPageSlug:
    """Tests for _page_slug helper."""

    def test_root_path(self) -> None:
        assert _page_slug("/") == "home"

    def test_simple_path(self) -> None:
        assert _page_slug("/baking") == "baking"

    def test_nested_path(self) -> None:
        assert _page_slug("/system-design") == "system-design"


class TestCleanupOldScreenshots:
    """Tests for screenshot cleanup logic."""

    def test_keeps_max_screenshots(self, tmp_path: Path) -> None:
        # Create 12 files with staggered mtimes
        for i in range(12):
            f = tmp_path / f"home_2026010{i:02d}_120000.png"
            f.write_bytes(b"fake")
        _cleanup_old_screenshots("home", tmp_path)
        remaining = list(tmp_path.glob("home_*.png"))
        assert len(remaining) == 10

    def test_no_cleanup_when_under_limit(self, tmp_path: Path) -> None:
        for i in range(5):
            f = tmp_path / f"baking_2026010{i}_120000.png"
            f.write_bytes(b"fake")
        _cleanup_old_screenshots("baking", tmp_path)
        remaining = list(tmp_path.glob("baking_*.png"))
        assert len(remaining) == 5

    def test_only_cleans_matching_slug(self, tmp_path: Path) -> None:
        for i in range(12):
            f = tmp_path / f"home_2026010{i:02d}_120000.png"
            f.write_bytes(b"fake")
        other = tmp_path / "baking_20260101_120000.png"
        other.write_bytes(b"fake")
        _cleanup_old_screenshots("home", tmp_path)
        assert other.exists()


class TestSaveScreenshot:
    """Tests for _save_screenshot."""

    def test_saves_png_file(self, tmp_path: Path) -> None:
        mock_page = MagicMock()
        mock_page.screenshot = MagicMock()
        result = _save_screenshot(mock_page, "/baking", tmp_path)
        assert result is not None
        assert "baking_" in result
        assert result.endswith(".png")
        mock_page.screenshot.assert_called_once()

    def test_creates_archive_dir(self, tmp_path: Path) -> None:
        subdir = tmp_path / "nested" / "archive"
        mock_page = MagicMock()
        _save_screenshot(mock_page, "/", subdir)
        assert subdir.exists()

    def test_returns_none_on_error(self, tmp_path: Path) -> None:
        mock_page = MagicMock()
        mock_page.screenshot.side_effect = RuntimeError("browser crashed")
        result = _save_screenshot(mock_page, "/", tmp_path)
        assert result is None
