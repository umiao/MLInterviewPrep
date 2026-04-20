"""Tests for behavioral PUT endpoint golden marker auto-refresh (T-P1-553)."""
import time
from datetime import datetime

import pytest

from src.backend.models.behavioral import BehavioralExample


@pytest.fixture()
def seed_example(db_session):
    """Insert a single behavioral example for golden-marker tests."""
    ex = BehavioralExample(
        example_id="EX-GOLD-01",
        title="Golden marker test example",
        situation="S",
        task="T",
        action="A",
        result="R",
    )
    db_session.add(ex)
    db_session.commit()
    db_session.refresh(ex)
    return ex


def _iso_to_dt(raw: str) -> datetime:
    """Parse an ISO-format timestamp string into datetime."""
    return datetime.fromisoformat(raw)


def test_behavioral_golden_false_to_true_sets_golden_at(test_client, seed_example):
    """AC (a): false->true sets golden_at to a recent time."""
    before = datetime.utcnow()
    resp = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    after = datetime.utcnow()
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_golden"] is True
    assert body["golden_at"] is not None
    stamped = _iso_to_dt(body["golden_at"])
    assert before <= stamped <= after


def test_behavioral_golden_true_to_true_does_not_overwrite(test_client, seed_example):
    """AC (b): re-PUT with is_golden=true but no flip does NOT refresh golden_at."""
    resp1 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    assert resp1.status_code == 200
    first_stamp = resp1.json()["golden_at"]

    time.sleep(0.01)
    resp2 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    assert resp2.status_code == 200
    assert resp2.json()["golden_at"] == first_stamp


def test_behavioral_golden_true_to_false_keeps_golden_at(test_client, seed_example):
    """AC (c): true->false keeps golden_at pinned."""
    resp1 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    assert resp1.status_code == 200
    first_stamp = resp1.json()["golden_at"]

    resp2 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": False}
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["is_golden"] is False
    assert body["golden_at"] == first_stamp


def test_behavioral_golden_remark_refreshes_golden_at(test_client, seed_example):
    """AC (d): false->true after an unmark refreshes golden_at to a later timestamp."""
    resp1 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    assert resp1.status_code == 200
    first_stamp = _iso_to_dt(resp1.json()["golden_at"])

    resp2 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": False}
    )
    assert resp2.status_code == 200

    time.sleep(0.01)
    resp3 = test_client.put(
        f"/api/behavioral/examples/{seed_example.id}", json={"is_golden": True}
    )
    assert resp3.status_code == 200
    new_stamp = _iso_to_dt(resp3.json()["golden_at"])
    assert new_stamp > first_stamp
