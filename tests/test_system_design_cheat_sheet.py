"""Tests for the cheat_sheet field on system_designs (T-P1-641)."""
import pytest

from src.backend.models.system_design import SystemDesign


@pytest.fixture()
def seed_system_designs(db_session):
    """Insert two system_design rows: one with cheat_sheet, one without."""
    rows = [
        SystemDesign(
            slug="news-feed-ranking",
            title="News Feed Ranking",
            subtitle="Personalized ranker",
            display_order=1,
            cheat_sheet="# Cheat Sheet\n- two-tower retrieval\n- DLRM ranker",
        ),
        SystemDesign(
            slug="ads-ctr",
            title="Ads CTR Prediction",
            subtitle=None,
            display_order=2,
            cheat_sheet=None,
        ),
    ]
    for r in rows:
        db_session.add(r)
    db_session.commit()
    for r in rows:
        db_session.refresh(r)
    return rows


def test_get_slug_includes_cheat_sheet(test_client, seed_system_designs):
    """GET /api/system-designs/<slug> exposes cheat_sheet (populated case)."""
    resp = test_client.get("/api/system-designs/news-feed-ranking")
    assert resp.status_code == 200
    body = resp.json()
    assert "cheat_sheet" in body
    assert body["cheat_sheet"].startswith("# Cheat Sheet")


def test_get_slug_cheat_sheet_null_when_empty(test_client, seed_system_designs):
    """GET /api/system-designs/<slug> returns cheat_sheet=null when unset."""
    resp = test_client.get("/api/system-designs/ads-ctr")
    assert resp.status_code == 200
    body = resp.json()
    assert body["cheat_sheet"] is None


def test_put_updates_cheat_sheet(test_client, seed_system_designs):
    """PUT /api/system-designs/<slug> can write cheat_sheet."""
    new_md = "# Updated\n- key idea\n- formula"
    resp = test_client.put(
        "/api/system-designs/ads-ctr",
        json={"cheat_sheet": new_md},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["cheat_sheet"] == new_md

    # Round-trip via GET
    follow = test_client.get("/api/system-designs/ads-ctr")
    assert follow.status_code == 200
    assert follow.json()["cheat_sheet"] == new_md


def test_cheat_sheets_aggregation_endpoint(test_client, seed_system_designs):
    """GET /api/system-designs/cheat-sheets returns all rows in display_order, with cheat_sheet."""
    resp = test_client.get("/api/system-designs/cheat-sheets")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 2
    assert rows[0]["slug"] == "news-feed-ranking"
    assert rows[0]["cheat_sheet"].startswith("# Cheat Sheet")
    assert rows[1]["slug"] == "ads-ctr"
    assert rows[1]["cheat_sheet"] is None
    # No leakage of large body fields into the lean aggregation response
    for row in rows:
        assert "overview" not in row
        assert "architecture" not in row


def test_list_endpoint_stays_lean(test_client, seed_system_designs):
    """GET /api/system-designs (list) does NOT include cheat_sheet (kept summary-only)."""
    resp = test_client.get("/api/system-designs")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 2
    for row in rows:
        assert "cheat_sheet" not in row
        assert "overview" not in row
