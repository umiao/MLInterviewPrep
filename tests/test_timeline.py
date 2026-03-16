"""Tests for the interview timeline API and migration."""
import sqlite3

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from src.backend.database import _run_migrations

# ---- Fixtures ----

@pytest.fixture()
def event_payload():
    """Minimal valid event creation payload."""
    return {
        "company_name": "LinkedIn",
        "event_type": "hr_call",
        "title": "HR Phone Screen",
        "scheduled_at": "2026-03-16T10:30:00",
    }


# ---- CRUD Tests ----

class TestTimelineCRUD:
    """Test timeline event CRUD via the API."""

    def test_create_event(self, test_client, event_payload):
        """POST /timeline/events creates and returns event."""
        resp = test_client.post("/api/timeline/events", json=event_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["company_name"] == "LinkedIn"
        assert data["event_type"] == "hr_call"
        assert data["title"] == "HR Phone Screen"
        assert data["status"] == "upcoming"
        assert data["id"] > 0

    def test_list_events(self, test_client, event_payload):
        """GET /timeline/events returns events sorted by scheduled_at."""
        # Create two events
        early = {**event_payload, "scheduled_at": "2026-03-10T09:00:00"}
        late = {**event_payload, "title": "Tech Screen", "scheduled_at": "2026-03-20T14:00:00"}
        test_client.post("/api/timeline/events", json=late)
        test_client.post("/api/timeline/events", json=early)

        resp = test_client.get("/api/timeline/events")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        # Should be sorted ASC by scheduled_at
        assert data[0]["title"] == "HR Phone Screen"
        assert data[1]["title"] == "Tech Screen"

    def test_filter_by_status(self, test_client, event_payload):
        """GET /timeline/events?status=upcoming filters correctly."""
        test_client.post("/api/timeline/events", json=event_payload)
        cancelled = {**event_payload, "title": "Cancelled", "status": "cancelled"}
        test_client.post("/api/timeline/events", json=cancelled)

        resp = test_client.get("/api/timeline/events", params={"status": "upcoming"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "upcoming"

    def test_filter_by_company_id(self, test_client, event_payload):
        """GET /timeline/events?company_id=N filters correctly."""
        # Create event for LinkedIn (auto-creates company)
        resp1 = test_client.post("/api/timeline/events", json=event_payload)
        linkedin_cid = resp1.json()["company_id"]

        # Create event for a different company
        other_payload = {**event_payload, "company_name": "Google", "title": "Google Screen"}
        test_client.post("/api/timeline/events", json=other_payload)

        resp = test_client.get("/api/timeline/events", params={"company_id": linkedin_cid})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["company_id"] == linkedin_cid

    def test_update_event(self, test_client, event_payload):
        """PUT /timeline/events/{id} partial update works."""
        create_resp = test_client.post("/api/timeline/events", json=event_payload)
        event_id = create_resp.json()["id"]

        update_resp = test_client.put(
            f"/api/timeline/events/{event_id}",
            json={"status": "completed", "title": "Done Screen"},
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["status"] == "completed"
        assert data["title"] == "Done Screen"
        # Unchanged fields preserved
        assert data["company_name"] == "LinkedIn"

    def test_delete_event(self, test_client, event_payload):
        """DELETE /timeline/events/{id} removes the event."""
        create_resp = test_client.post("/api/timeline/events", json=event_payload)
        event_id = create_resp.json()["id"]

        del_resp = test_client.delete(f"/api/timeline/events/{event_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True

        # Verify gone
        list_resp = test_client.get("/api/timeline/events")
        assert len(list_resp.json()) == 0

    def test_update_nonexistent(self, test_client):
        """PUT /timeline/events/999 returns 404."""
        resp = test_client.put(
            "/api/timeline/events/999", json={"title": "X"}
        )
        assert resp.status_code == 404

    def test_delete_nonexistent(self, test_client):
        """DELETE /timeline/events/999 returns 404."""
        resp = test_client.delete("/api/timeline/events/999")
        assert resp.status_code == 404

    def test_limit_param(self, test_client, event_payload):
        """GET /timeline/events?limit=1 returns at most 1."""
        test_client.post("/api/timeline/events", json=event_payload)
        test_client.post(
            "/api/timeline/events",
            json={**event_payload, "title": "Second"},
        )

        resp = test_client.get("/api/timeline/events", params={"limit": 1})
        assert len(resp.json()) == 1


# ---- Auto-link Company Tests ----

class TestTimelineAutoLinkCompany:
    """Test auto-linking company on event create/update."""

    def test_create_event_auto_creates_company(self, test_client, event_payload):
        """Creating an event auto-creates the company and links company_id."""
        resp = test_client.post("/api/timeline/events", json=event_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["company_id"] is not None

        # Verify company was created
        companies = test_client.get("/api/companies").json()
        names = [c["name"] for c in companies]
        assert "LinkedIn" in names
        # company_id matches
        company = next(c for c in companies if c["name"] == "LinkedIn")
        assert data["company_id"] == company["id"]

    def test_create_event_existing_company_no_duplicate(self, test_client, event_payload):
        """Creating events with same company name reuses existing company."""
        # Create first event -> company auto-created
        resp1 = test_client.post("/api/timeline/events", json=event_payload)
        cid1 = resp1.json()["company_id"]

        # Create second event with same company
        payload2 = {**event_payload, "title": "Tech Screen"}
        resp2 = test_client.post("/api/timeline/events", json=payload2)
        cid2 = resp2.json()["company_id"]

        assert cid1 == cid2

        # Only one company exists
        companies = test_client.get("/api/companies").json()
        linkedin_companies = [c for c in companies if c["name"] == "LinkedIn"]
        assert len(linkedin_companies) == 1

    def test_create_event_case_insensitive_match(self, test_client, event_payload):
        """Company matching is case-insensitive (no duplicate for 'linkedin' vs 'LinkedIn')."""
        test_client.post("/api/timeline/events", json=event_payload)  # "LinkedIn"

        payload2 = {**event_payload, "company_name": "linkedin", "title": "2nd"}
        resp2 = test_client.post("/api/timeline/events", json=payload2)
        cid2 = resp2.json()["company_id"]

        companies = test_client.get("/api/companies").json()
        # Should only have one company (case-insensitive dedup)
        assert len(companies) == 1
        assert companies[0]["id"] == cid2

    def test_update_event_company_name_links_new_company(self, test_client, event_payload):
        """Updating company_name on event auto-creates and links the new company."""
        create_resp = test_client.post("/api/timeline/events", json=event_payload)
        event_id = create_resp.json()["id"]
        old_cid = create_resp.json()["company_id"]

        # Update company_name to a new one
        update_resp = test_client.put(
            f"/api/timeline/events/{event_id}",
            json={"company_name": "DoorDash"},
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["company_name"] == "DoorDash"
        assert data["company_id"] is not None
        assert data["company_id"] != old_cid

        # DoorDash company exists
        companies = test_client.get("/api/companies").json()
        names = [c["name"] for c in companies]
        assert "DoorDash" in names

    def test_update_event_without_company_name_keeps_existing(self, test_client, event_payload):
        """Updating other fields without company_name preserves existing company_id."""
        create_resp = test_client.post("/api/timeline/events", json=event_payload)
        event_id = create_resp.json()["id"]
        original_cid = create_resp.json()["company_id"]

        update_resp = test_client.put(
            f"/api/timeline/events/{event_id}",
            json={"title": "Updated Title"},
        )
        assert update_resp.json()["company_id"] == original_cid


# ---- Export/Import Tests ----

class TestTimelineExportImport:
    """Test export/import roundtrip for interview_events."""

    def test_export_includes_events(self, test_client, event_payload):
        """GET /api/export includes interview_events key."""
        test_client.post("/api/timeline/events", json=event_payload)

        resp = test_client.get("/api/export")
        data = resp.json()
        assert "interview_events" in data
        assert len(data["interview_events"]) == 1
        assert data["interview_events"][0]["company_name"] == "LinkedIn"

    def test_import_events(self, test_client):
        """POST /api/import with interview_events inserts them."""
        payload = {
            "interview_events": [
                {
                    "company_name": "DoorDash",
                    "event_type": "technical",
                    "title": "Tech Chat",
                    "scheduled_at": "2026-03-26T13:00:00",
                    "status": "upcoming",
                },
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.status_code == 200
        assert resp.json()["interview_events"]["inserted"] == 1

        # Verify via list endpoint
        list_resp = test_client.get("/api/timeline/events")
        assert len(list_resp.json()) == 1


# ---- Migration Tests ----

def _create_pre_v2_schema(db_path: str) -> None:
    """Create a DB with schema_versions tracking v1, but no interview_events table.

    Args:
        db_path: Path to the SQLite file.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE framework_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            path TEXT NOT NULL,
            depth INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL,
            importance REAL DEFAULT 1.0,
            priority TEXT DEFAULT 'P2',
            estimated_hours REAL DEFAULT 0,
            confidence REAL DEFAULT 0.0
        )
    """)
    conn.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            framework_node_id INTEGER REFERENCES framework_nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL UNIQUE,
            group_tag VARCHAR,
            interview_stages TEXT,
            status VARCHAR DEFAULT 'applied',
            applied_at DATE,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE schema_versions (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute(
        "INSERT INTO schema_versions (version, description) VALUES (1, 'v1 done')"
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def pre_v2_db(tmp_path):
    """Create a file DB with v1 applied but no interview_events table.

    Yields:
        SQLAlchemy engine for the temp DB.
    """
    db_path = str(tmp_path / "test_v2.db")
    _create_pre_v2_schema(db_path)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


class TestMigration2InterviewEvents:
    """Test migration 2: create interview_events table."""

    def test_table_created(self, pre_v2_db):
        """After migration, interview_events table exists."""
        _run_migrations(pre_v2_db)
        insp = inspect(pre_v2_db)
        assert "interview_events" in insp.get_table_names()

    def test_index_created(self, pre_v2_db):
        """After migration, scheduled_at index exists."""
        _run_migrations(pre_v2_db)
        insp = inspect(pre_v2_db)
        indexes = {idx["name"] for idx in insp.get_indexes("interview_events")}
        assert "ix_interview_events_scheduled_at" in indexes

    def test_version_recorded(self, pre_v2_db):
        """After migration, schema_versions has version 2."""
        _run_migrations(pre_v2_db)
        with pre_v2_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        versions = {row[0] for row in rows}
        assert 2 in versions
        assert 1 in versions  # v1 still there

    def test_idempotent(self, pre_v2_db):
        """Running migration twice is safe."""
        _run_migrations(pre_v2_db)
        _run_migrations(pre_v2_db)
        with pre_v2_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        assert len(rows) == 3  # v1 + v2 + v3

    def test_table_missing_before(self, pre_v2_db):
        """Sanity: interview_events does not exist before migration."""
        insp = inspect(pre_v2_db)
        assert "interview_events" not in insp.get_table_names()
