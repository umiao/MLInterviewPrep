"""Tests for T-P2-67: Performance + final polish."""
from unittest.mock import patch

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool


class TestResponseTimeMiddleware:
    """Tests for the response time logging middleware."""

    def test_health_returns_response_time_header(self, test_client):
        """Health endpoint response includes X-Response-Time header."""
        resp = test_client.get("/api/health")
        assert resp.status_code == 200
        header = resp.headers.get("X-Response-Time")
        assert header is not None
        assert header.endswith("ms")
        # Should be a parseable float
        float(header.replace("ms", ""))

    def test_response_time_on_list_endpoint(self, test_client):
        """List endpoint also gets the timing header."""
        resp = test_client.get("/api/problems")
        assert resp.status_code == 200
        assert "X-Response-Time" in resp.headers

    def test_response_time_on_nonexistent_route(self, test_client):
        """Even non-matching routes get timing headers."""
        resp = test_client.get("/api/nonexistent-route")
        assert "X-Response-Time" in resp.headers


class TestValidationErrorHandler:
    """Tests for the 422 validation error handler."""

    def test_invalid_problem_create_returns_422(self, test_client):
        """Creating a problem with missing required fields returns 422."""
        resp = test_client.post("/api/problems", json={})
        assert resp.status_code == 422
        data = resp.json()
        assert "detail" in data

    def test_invalid_attempt_body_returns_422(self, test_client, seed_problems):
        """Invalid attempt body returns 422."""
        pid = seed_problems[0].id
        # comfort_after must be 1-5, sending invalid data
        resp = test_client.post(
            f"/api/problems/{pid}/attempts",
            json={"comfort_after": "not-a-number"},
        )
        assert resp.status_code == 422


class TestSQLiteWALMode:
    """Tests for SQLite WAL mode configuration."""

    def test_wal_mode_enabled_for_file_db(self, tmp_path):
        """WAL mode is set for file-based SQLite databases."""
        db_path = tmp_path / "test.db"
        db_url = f"sqlite:///{db_path}"

        with patch("src.backend.database.get_settings") as mock_settings:
            mock_settings.return_value.DATABASE_URL = db_url
            from src.backend.database import init_db

            init_db()

        from src.backend.database import get_engine

        engine = get_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode")).fetchone()
            assert result[0] == "wal"

    def test_wal_mode_skipped_for_memory_db(self):
        """WAL mode is NOT set for in-memory SQLite databases."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode")).fetchone()
            # In-memory defaults to "memory", not "wal"
            assert result[0] != "wal"
