"""Tests for reading/TTS router endpoints.

Covers: queue, progress (CRUD + reset), content retrieval, synthesize
(sync + async + cache), job polling, and audio serving.
"""
from unittest.mock import AsyncMock, patch

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode
from src.backend.models.reading import AudioCache, ReadingProgress


def _seed_node(db, title="DP", path="coding/dp", description="Dynamic programming overview."):
    """Create a framework node with description."""
    node = FrameworkNode(
        title=title,
        path=path,
        depth=1,
        description=description,
        importance=0.8,
        status="not_started",
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def _seed_company(db, name="TestCo", prep_notes="Prep notes for TestCo."):
    """Create a company with prep notes."""
    company = Company(name=name, status="applied", prep_notes=prep_notes)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


# -----------------------------------------------------------------------
# GET /reading/queue
# -----------------------------------------------------------------------
class TestGetQueue:
    """Tests for GET /reading/queue endpoint."""

    def test_empty_queue(self, test_client):
        """Empty DB returns empty queue."""
        resp = test_client.get("/api/reading/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_queue_with_framework_node(self, test_client, db_session):
        """Queue includes framework nodes with descriptions."""
        _seed_node(db_session)
        resp = test_client.get("/api/reading/queue")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        item = data["items"][0]
        assert item["content_type"] == "framework_node"
        assert item["title"] == "DP"
        assert item["total_chars"] > 0

    def test_queue_with_company_ids(self, test_client, db_session):
        """Queue filters/boosts by company_ids."""
        company = _seed_company(db_session)
        resp = test_client.get(f"/api/reading/queue?company_ids={company.id}")
        assert resp.status_code == 200
        data = resp.json()
        # Should include prep_notes for the company
        types = [i["content_type"] for i in data["items"]]
        assert "prep_notes" in types

    def test_queue_invalid_company_ids(self, test_client):
        """Non-integer company_ids returns 400."""
        resp = test_client.get("/api/reading/queue?company_ids=abc")
        assert resp.status_code == 400
        assert "comma-separated integers" in resp.json()["detail"]

    def test_queue_limit(self, test_client, db_session):
        """Queue respects limit parameter."""
        for i in range(5):
            _seed_node(db_session, title=f"Node{i}", path=f"path/{i}", description=f"Desc {i}")
        resp = test_client.get("/api/reading/queue?limit=2")
        assert resp.status_code == 200
        assert resp.json()["total"] <= 2

    def test_queue_excludes_completed(self, test_client, db_session):
        """Queue excludes items marked as completed."""
        node = _seed_node(db_session)
        # Mark as completed
        progress = ReadingProgress(
            content_type="framework_node",
            content_id=node.id,
            completed=True,
        )
        db_session.add(progress)
        db_session.commit()

        resp = test_client.get("/api/reading/queue")
        assert resp.status_code == 200
        ids = [i["content_id"] for i in resp.json()["items"]
               if i["content_type"] == "framework_node"]
        assert node.id not in ids

    def test_queue_sorted_by_urgency(self, test_client, db_session):
        """Queue items are sorted by urgency descending."""
        low = FrameworkNode(title="Low", path="low", depth=1, description="Low urgency.", importance=0.1, status="not_started")
        high = FrameworkNode(title="High", path="high", depth=1, description="High urgency.", importance=1.0, status="not_started")
        db_session.add_all([low, high])
        db_session.commit()
        resp = test_client.get("/api/reading/queue")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if len(items) >= 2:
            assert items[0]["urgency"] >= items[1]["urgency"]


# -----------------------------------------------------------------------
# GET /reading/progress
# -----------------------------------------------------------------------
class TestGetProgress:
    """Tests for GET /reading/progress endpoint."""

    def test_no_progress(self, test_client):
        """No progress records returns empty list."""
        resp = test_client.get("/api/reading/progress")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_progress(self, test_client, db_session):
        """Returns all progress records."""
        rp = ReadingProgress(
            content_type="framework_node",
            content_id=1,
            last_chunk_index=3,
            char_offset=500,
            total_chars=1000,
        )
        db_session.add(rp)
        db_session.commit()

        resp = test_client.get("/api/reading/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["last_chunk_index"] == 3
        assert data[0]["char_offset"] == 500


# -----------------------------------------------------------------------
# PUT /reading/progress/{content_type}/{content_id}
# -----------------------------------------------------------------------
class TestUpdateProgress:
    """Tests for PUT /reading/progress/{type}/{id} endpoint."""

    def test_create_progress(self, test_client):
        """PUT creates new progress if none exists."""
        resp = test_client.put(
            "/api/reading/progress/framework_node/1",
            json={"last_chunk_index": 2, "char_offset": 300, "total_chars": 1000},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_type"] == "framework_node"
        assert data["content_id"] == 1
        assert data["last_chunk_index"] == 2
        assert data["char_offset"] == 300

    def test_update_existing_progress(self, test_client, db_session):
        """PUT updates existing progress record."""
        rp = ReadingProgress(
            content_type="framework_node", content_id=5,
            last_chunk_index=0, char_offset=0, total_chars=500,
        )
        db_session.add(rp)
        db_session.commit()

        resp = test_client.put(
            "/api/reading/progress/framework_node/5",
            json={"last_chunk_index": 4, "char_offset": 400, "total_chars": 500, "completed": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["last_chunk_index"] == 4
        assert data["char_offset"] == 400
        assert data["completed"] is True

    def test_update_progress_invalid_type(self, test_client):
        """PUT with invalid content_type returns 400."""
        resp = test_client.put(
            "/api/reading/progress/invalid_type/1",
            json={"last_chunk_index": 0, "char_offset": 0},
        )
        assert resp.status_code == 400
        assert "Invalid content type" in resp.json()["detail"]

    def test_update_progress_negative_chunk(self, test_client):
        """PUT with negative values returns 422 (Pydantic validation)."""
        resp = test_client.put(
            "/api/reading/progress/framework_node/1",
            json={"last_chunk_index": -1, "char_offset": 0},
        )
        assert resp.status_code == 422

    def test_update_progress_prep_notes(self, test_client):
        """PUT works for prep_notes content type."""
        resp = test_client.put(
            "/api/reading/progress/prep_notes/3",
            json={"last_chunk_index": 1, "char_offset": 100, "total_chars": 200},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "prep_notes"

    def test_update_progress_interview_question(self, test_client):
        """PUT works for interview_question content type."""
        resp = test_client.put(
            "/api/reading/progress/interview_question/7",
            json={"last_chunk_index": 0, "char_offset": 50},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "interview_question"


# -----------------------------------------------------------------------
# DELETE /reading/progress
# -----------------------------------------------------------------------
class TestResetProgress:
    """Tests for DELETE /reading/progress endpoint."""

    def test_reset_empty(self, test_client):
        """Reset with no records returns 204."""
        resp = test_client.delete("/api/reading/progress")
        assert resp.status_code == 204

    def test_reset_clears_all(self, test_client, db_session):
        """Reset deletes all progress records."""
        for i in range(3):
            db_session.add(ReadingProgress(
                content_type="framework_node", content_id=i,
            ))
        db_session.commit()

        resp = test_client.delete("/api/reading/progress")
        assert resp.status_code == 204

        # Verify cleared
        resp2 = test_client.get("/api/reading/progress")
        assert resp2.json() == []


# -----------------------------------------------------------------------
# GET /reading/content/{content_type}/{content_id}
# -----------------------------------------------------------------------
class TestGetContent:
    """Tests for GET /reading/content/{type}/{id} endpoint."""

    def test_framework_node_content(self, test_client, db_session):
        """Returns preprocessed text and chunks for framework node."""
        node = _seed_node(db_session, description="This is a detailed description. With multiple sentences.")
        resp = test_client.get(f"/api/reading/content/framework_node/{node.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_type"] == "framework_node"
        assert data["content_id"] == node.id
        assert len(data["raw_text"]) > 0
        assert len(data["preprocessed_text"]) > 0
        assert len(data["chunks"]) >= 1
        assert len(data["content_hash"]) == 64  # SHA-256 hex
        assert data["total_chars"] > 0

    def test_prep_notes_content(self, test_client, db_session):
        """Returns content for prep_notes."""
        company = _seed_company(db_session)
        resp = test_client.get(f"/api/reading/content/prep_notes/{company.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_type"] == "prep_notes"
        assert "Prep notes" in data["raw_text"]

    def test_content_not_found(self, test_client):
        """Returns 404 for nonexistent content."""
        resp = test_client.get("/api/reading/content/framework_node/99999")
        assert resp.status_code == 404

    def test_content_invalid_type(self, test_client):
        """Returns 400 for invalid content type."""
        resp = test_client.get("/api/reading/content/invalid_type/1")
        assert resp.status_code == 400
        assert "Invalid content type" in resp.json()["detail"]

    def test_content_empty_description_falls_back_to_title(self, test_client, db_session):
        """Node with empty description falls back to title via get_content_text."""
        node = FrameworkNode(title="Just Title", path="empty", depth=0, description="")
        db_session.add(node)
        db_session.commit()
        db_session.refresh(node)

        resp = test_client.get(f"/api/reading/content/framework_node/{node.id}")
        # get_content_text returns title as fallback, so this should succeed
        assert resp.status_code == 200
        assert "Just Title" in resp.json()["raw_text"]


# -----------------------------------------------------------------------
# POST /reading/synthesize (refactored with AudioCache)
# -----------------------------------------------------------------------
class TestSynthesize:
    """Tests for POST /reading/synthesize endpoint."""

    def test_synthesize_missing_node(self, test_client):
        """Synthesize for nonexistent node returns 404."""
        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": 99999,
        })
        assert resp.status_code == 404

    def test_synthesize_none_description(self, test_client, db_session):
        """Synthesize for node with None description (no fallback) returns 404-like or uses title."""
        node = FrameworkNode(title="", path="empty", depth=0, description=None)
        db_session.add(node)
        db_session.commit()
        db_session.refresh(node)

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        # get_content_text returns None for no description and empty title -> 400
        assert resp.status_code == 400

    def test_synthesize_unknown_content_type(self, test_client):
        """Unknown content type returns 422 (Pydantic Literal validation)."""
        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "unknown_type",
            "content_id": 1,
        })
        assert resp.status_code == 422

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_synthesize_success(self, mock_synth, test_client, db_session, tmp_path):
        """Successful synthesis returns audio URL."""
        node = _seed_node(db_session)

        fake_mp3 = tmp_path / "abc123.mp3"
        fake_mp3.write_bytes(b"\xff\xfb\x90\x00" * 100)
        mock_synth.return_value = fake_mp3

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "audio_url" in data
        assert data["audio_url"].startswith("/api/reading/audio/")
        assert data["content_length"] > 0
        assert isinstance(data["cache_hit"], bool)
        mock_synth.assert_called_once()

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_synthesize_creates_audio_cache_entry(self, mock_synth, test_client, db_session, tmp_path):
        """Synthesis creates an AudioCache DB entry."""
        node = _seed_node(db_session)

        fake_mp3 = tmp_path / "cache_entry.mp3"
        fake_mp3.write_bytes(b"\xff\xfb\x90\x00" * 50)
        mock_synth.return_value = fake_mp3

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        assert resp.status_code == 200

        # Verify AudioCache entry was created
        cache = db_session.query(AudioCache).filter_by(
            content_type="framework_node",
            content_id=node.id,
            engine="edge_tts",
        ).first()
        assert cache is not None
        assert len(cache.content_hash) == 64

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_synthesize_cache_invalidation_on_hash_change(
        self, mock_synth, test_client, db_session, tmp_path,
    ):
        """When content changes (hash differs), old cache entry is removed."""
        node = _seed_node(db_session, description="Original content.")

        # Seed an old AudioCache with a stale hash
        old_cache = AudioCache(
            content_type="framework_node",
            content_id=node.id,
            content_hash="stale_hash_that_will_not_match",
            file_path="old.mp3",
            engine="edge_tts",
            voice="en-US-AriaNeural",
        )
        db_session.add(old_cache)
        db_session.commit()

        fake_mp3 = tmp_path / "new_cache.mp3"
        fake_mp3.write_bytes(b"\xff\xfb\x90\x00" * 50)
        mock_synth.return_value = fake_mp3

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        assert resp.status_code == 200
        assert resp.json()["cache_hit"] is False

        # Old cache entry should be gone, new one created
        caches = db_session.query(AudioCache).filter_by(
            content_type="framework_node",
            content_id=node.id,
        ).all()
        assert len(caches) == 1
        assert caches[0].content_hash != "stale_hash_that_will_not_match"

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_synthesize_long_content_returns_202(
        self, mock_synth, test_client, db_session,
    ):
        """Content >= 2000 chars returns 202 with job_id for async synthesis."""
        long_desc = "A" * 2100  # Over ASYNC_THRESHOLD
        node = _seed_node(db_session, description=long_desc)

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["content_length"] >= 2000

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_synthesize_prep_notes(self, mock_synth, test_client, db_session, tmp_path):
        """Synthesis works for prep_notes content type."""
        company = _seed_company(db_session)

        fake_mp3 = tmp_path / "prep.mp3"
        fake_mp3.write_bytes(b"\xff\xfb\x90\x00" * 50)
        mock_synth.return_value = fake_mp3

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "prep_notes",
            "content_id": company.id,
        })
        assert resp.status_code == 200
        assert resp.json()["content_length"] > 0


# -----------------------------------------------------------------------
# GET /reading/jobs/{job_id}
# -----------------------------------------------------------------------
class TestJobPolling:
    """Tests for GET /reading/jobs/{job_id} endpoint."""

    def test_job_not_found(self, test_client):
        """Unknown job_id returns 404."""
        resp = test_client.get("/api/reading/jobs/nonexistent-uuid")
        assert resp.status_code == 404

    @patch("src.backend.routers.reading.synthesize_text", new_callable=AsyncMock)
    def test_job_created_on_async_synthesize(
        self, mock_synth, test_client, db_session,
    ):
        """Async synthesize creates a pollable job."""
        long_desc = "B" * 2200
        node = _seed_node(db_session, description=long_desc)

        resp = test_client.post("/api/reading/synthesize", json={
            "content_type": "framework_node",
            "content_id": node.id,
        })
        assert resp.status_code == 202
        job_id = resp.json()["job_id"]

        # Poll the job
        poll_resp = test_client.get(f"/api/reading/jobs/{job_id}")
        assert poll_resp.status_code == 200
        assert poll_resp.json()["job_id"] == job_id
        assert poll_resp.json()["status"] in ("pending", "completed", "failed")


# -----------------------------------------------------------------------
# GET /reading/audio/{cache_key}
# -----------------------------------------------------------------------
class TestGetAudio:
    """Tests for GET /reading/audio/{cache_key} endpoint."""

    def test_audio_not_found(self, test_client):
        """Audio endpoint returns 404 for missing file."""
        resp = test_client.get("/api/reading/audio/nonexistent_hash")
        assert resp.status_code == 404


# -----------------------------------------------------------------------
# Integration: full flow
# -----------------------------------------------------------------------
class TestIntegrationFlows:
    """End-to-end flow tests combining multiple endpoints."""

    def test_progress_persists_across_queue_calls(self, test_client, db_session):
        """Update progress, then verify queue reflects it."""
        node = _seed_node(db_session)

        # Update progress
        test_client.put(
            f"/api/reading/progress/framework_node/{node.id}",
            json={"last_chunk_index": 2, "char_offset": 200, "total_chars": 500},
        )

        # Queue should show progress
        resp = test_client.get("/api/reading/queue")
        items = resp.json()["items"]
        node_items = [i for i in items
                      if i["content_type"] == "framework_node" and i["content_id"] == node.id]
        if node_items:
            assert node_items[0]["last_chunk_index"] == 2
            assert node_items[0]["char_offset"] == 200

    def test_reset_then_queue_shows_zero_progress(self, test_client, db_session):
        """After reset, queue items show zero progress."""
        node = _seed_node(db_session)

        # Set progress
        test_client.put(
            f"/api/reading/progress/framework_node/{node.id}",
            json={"last_chunk_index": 5, "char_offset": 800, "total_chars": 1000},
        )
        # Reset
        test_client.delete("/api/reading/progress")

        # Queue items should have zero progress
        resp = test_client.get("/api/reading/queue")
        for item in resp.json()["items"]:
            assert item["last_chunk_index"] == 0
            assert item["char_offset"] == 0
