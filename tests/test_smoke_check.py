"""Tests for scripts/smoke_check.py."""
import importlib.util
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

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
