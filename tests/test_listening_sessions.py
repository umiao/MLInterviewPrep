"""Tests for listening session analytics endpoints.

Covers: POST /reading/sessions (create), PUT /reading/sessions/{id} (close),
GET /reading/stats (aggregated listening statistics).
"""
from datetime import UTC, datetime, timedelta

from src.backend.models.reading import ReadingSession


# -----------------------------------------------------------------------
# POST /reading/sessions -- create a new session
# -----------------------------------------------------------------------
class TestCreateSession:
    """Tests for POST /reading/sessions endpoint."""

    def test_create_session_minimal(self, test_client):
        """Create a session with no engine specified."""
        resp = test_client.post("/api/reading/sessions", json={})
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["content_items_read"] == 0
        assert data["total_duration_seconds"] == 0.0
        assert data["tts_engine"] is None

    def test_create_session_with_engine(self, test_client):
        """Create a session with tts_engine specified."""
        resp = test_client.post("/api/reading/sessions", json={"tts_engine": "edge_tts"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["tts_engine"] == "edge_tts"
        assert data["started_at"] is not None
        assert data["ended_at"] is None

    def test_create_multiple_sessions(self, test_client):
        """Can create multiple sessions with unique IDs."""
        r1 = test_client.post("/api/reading/sessions", json={})
        r2 = test_client.post("/api/reading/sessions", json={})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]


# -----------------------------------------------------------------------
# PUT /reading/sessions/{session_id} -- close a session
# -----------------------------------------------------------------------
class TestCloseSession:
    """Tests for PUT /reading/sessions/{id} endpoint."""

    def test_close_session(self, test_client):
        """Close an existing session with items and duration."""
        # Create first
        create_resp = test_client.post("/api/reading/sessions", json={"tts_engine": "edge_tts"})
        session_id = create_resp.json()["id"]

        # Close
        resp = test_client.put(
            f"/api/reading/sessions/{session_id}",
            json={"session_id": session_id, "content_items_read": 5, "total_duration_seconds": 300.5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_items_read"] == 5
        assert data["total_duration_seconds"] == 300.5
        assert data["ended_at"] is not None

    def test_close_nonexistent_session(self, test_client):
        """Close a session that doesn't exist returns 404."""
        resp = test_client.put(
            "/api/reading/sessions/99999",
            json={"session_id": 99999, "content_items_read": 0, "total_duration_seconds": 0.0},
        )
        assert resp.status_code == 404

    def test_close_session_validation(self, test_client):
        """Negative values in close request return 422."""
        create_resp = test_client.post("/api/reading/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = test_client.put(
            f"/api/reading/sessions/{session_id}",
            json={"session_id": session_id, "content_items_read": -1, "total_duration_seconds": 0.0},
        )
        assert resp.status_code == 422


# -----------------------------------------------------------------------
# GET /reading/stats -- aggregated listening statistics
# -----------------------------------------------------------------------
class TestListeningStats:
    """Tests for GET /reading/stats endpoint."""

    def test_empty_stats(self, test_client):
        """No sessions returns all-zero stats."""
        resp = test_client.get("/api/reading/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 0
        assert data["total_listening_seconds"] == 0.0
        assert data["total_items_listened"] == 0
        assert data["sessions_today"] == 0
        assert data["listening_seconds_today"] == 0.0
        assert data["streak_days"] == 0

    def test_stats_with_sessions(self, test_client, db_session):
        """Stats reflect created and closed sessions."""
        # Create sessions directly in DB for precise control
        now = datetime.now(UTC)
        s1 = ReadingSession(
            started_at=now,
            ended_at=now + timedelta(minutes=10),
            content_items_read=3,
            total_duration_seconds=600.0,
            tts_engine="edge_tts",
        )
        s2 = ReadingSession(
            started_at=now - timedelta(hours=1),
            ended_at=now - timedelta(minutes=30),
            content_items_read=2,
            total_duration_seconds=1800.0,
        )
        db_session.add_all([s1, s2])
        db_session.commit()

        resp = test_client.get("/api/reading/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 2
        assert data["total_listening_seconds"] == 2400.0
        assert data["total_items_listened"] == 5

    def test_stats_today_filter(self, test_client, db_session):
        """sessions_today counts only today's sessions."""
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)

        today_session = ReadingSession(
            started_at=now,
            content_items_read=1,
            total_duration_seconds=120.0,
        )
        old_session = ReadingSession(
            started_at=yesterday,
            content_items_read=2,
            total_duration_seconds=300.0,
        )
        db_session.add_all([today_session, old_session])
        db_session.commit()

        resp = test_client.get("/api/reading/stats")
        data = resp.json()
        assert data["total_sessions"] == 2
        assert data["sessions_today"] == 1
        assert data["listening_seconds_today"] == 120.0

    def test_stats_streak(self, test_client, db_session):
        """Streak counts consecutive days with sessions."""
        now = datetime.now(UTC)
        # Sessions on today, yesterday, and day before
        for days_ago in range(3):
            s = ReadingSession(
                started_at=now - timedelta(days=days_ago),
                content_items_read=1,
                total_duration_seconds=60.0,
            )
            db_session.add(s)
        db_session.commit()

        resp = test_client.get("/api/reading/stats")
        data = resp.json()
        assert data["streak_days"] == 3

    def test_stats_broken_streak(self, test_client, db_session):
        """Streak breaks when a day is missed."""
        now = datetime.now(UTC)
        # Sessions today and 2 days ago (gap yesterday)
        for days_ago in [0, 2]:
            s = ReadingSession(
                started_at=now - timedelta(days=days_ago),
                content_items_read=1,
                total_duration_seconds=60.0,
            )
            db_session.add(s)
        db_session.commit()

        resp = test_client.get("/api/reading/stats")
        data = resp.json()
        assert data["streak_days"] == 1  # Only today counts


# -----------------------------------------------------------------------
# Integration: create -> close -> stats
# -----------------------------------------------------------------------
class TestSessionIntegration:
    """End-to-end flow for listening sessions."""

    def test_create_close_stats_flow(self, test_client):
        """Create session, close it, then verify stats reflect it."""
        # Create
        create_resp = test_client.post(
            "/api/reading/sessions", json={"tts_engine": "edge_tts"},
        )
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        # Close
        close_resp = test_client.put(
            f"/api/reading/sessions/{session_id}",
            json={"session_id": session_id, "content_items_read": 4, "total_duration_seconds": 500.0},
        )
        assert close_resp.status_code == 200

        # Stats
        stats_resp = test_client.get("/api/reading/stats")
        assert stats_resp.status_code == 200
        data = stats_resp.json()
        assert data["total_sessions"] >= 1
        assert data["total_items_listened"] >= 4
        assert data["total_listening_seconds"] >= 500.0
