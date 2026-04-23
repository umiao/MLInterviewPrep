"""Tests for BQ-DEPTH Phase B schema uplift (T-P1-579).

Covers:
  - probe_notes round-trip: PUT then GET returns the same JSON structure.
  - probe_notes_updated_at stamped on every edit.
  - is_primary surfaced in linked_questions on example responses.
  - Single-primary-per-question invariant: second primary link rejected
    with 409 at the application layer.
"""
import pytest

from src.backend.models.behavioral import (
    BehavioralExample,
    BehavioralQuestion,
)


@pytest.fixture()
def seed_question(db_session):
    """Insert a single behavioral question for probe_notes tests."""
    q = BehavioralQuestion(
        question_id="OWN-TEST-1",
        text="Tell me about a time you owned something end-to-end.",
        category_id="ownership",
        category_name="Ownership & Accountability",
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    return q


@pytest.fixture()
def seed_question_and_examples(db_session):
    """Insert one question + two examples so links tests have real IDs."""
    q = BehavioralQuestion(
        question_id="OWN-PRIM-1",
        text="When did you push past your scope?",
        category_id="ownership",
        category_name="Ownership & Accountability",
    )
    ex1 = BehavioralExample(
        example_id="EX-PRIM-A",
        title="Example A",
        situation="S",
        task="T",
        action="A",
        result="R",
    )
    ex2 = BehavioralExample(
        example_id="EX-PRIM-B",
        title="Example B",
        situation="S",
        task="T",
        action="A",
        result="R",
    )
    db_session.add_all([q, ex1, ex2])
    db_session.commit()
    db_session.refresh(q)
    db_session.refresh(ex1)
    db_session.refresh(ex2)
    return q, ex1, ex2


def test_probe_notes_round_trip(test_client, seed_question):
    """PUT probe_notes -> GET /questions returns the same structured payload."""
    payload = {
        "probe_notes": {
            "core_signal": "Owns ambiguous ambiguity",
            "what_good_looks_like": "Names the gap and closes it",
            "what_L5_adds": "Links to cross-team system impact",
            "common_failure_modes": "Stops at \"not my team\"",
        },
    }
    resp = test_client.put(
        f"/api/behavioral/questions/{seed_question.id}", json=payload
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["probe_notes"] == payload["probe_notes"]
    assert body["probe_notes_updated_at"] is not None

    # Round-trip via GET (list endpoint is the main consumer).
    list_resp = test_client.get("/api/behavioral/questions")
    assert list_resp.status_code == 200
    rows = list_resp.json()
    row = next(r for r in rows if r["id"] == seed_question.id)
    assert row["probe_notes"] == payload["probe_notes"]
    assert row["probe_notes_updated_at"] is not None


def test_probe_notes_absent_initially(test_client, seed_question):
    """New questions surface probe_notes=None on list/PUT responses."""
    list_resp = test_client.get("/api/behavioral/questions")
    row = next(r for r in list_resp.json() if r["id"] == seed_question.id)
    assert row["probe_notes"] is None
    assert row["probe_notes_updated_at"] is None


def test_single_primary_per_question_invariant(
    test_client, seed_question_and_examples
):
    """Second is_primary=true link for same question -> 409."""
    q, ex1, ex2 = seed_question_and_examples

    resp1 = test_client.post(
        "/api/behavioral/links",
        json={
            "question_id": q.id,
            "example_id": ex1.id,
            "relevance_note": "primary",
            "is_primary": True,
        },
    )
    assert resp1.status_code == 201, resp1.text
    assert resp1.json()["is_primary"] is True

    resp2 = test_client.post(
        "/api/behavioral/links",
        json={
            "question_id": q.id,
            "example_id": ex2.id,
            "relevance_note": "should be rejected",
            "is_primary": True,
        },
    )
    assert resp2.status_code == 409
    assert "primary" in resp2.json()["detail"].lower()


def test_secondary_links_allowed_alongside_primary(
    test_client, seed_question_and_examples
):
    """One primary + one non-primary link on the same question is fine."""
    q, ex1, ex2 = seed_question_and_examples

    r1 = test_client.post(
        "/api/behavioral/links",
        json={
            "question_id": q.id,
            "example_id": ex1.id,
            "is_primary": True,
        },
    )
    assert r1.status_code == 201

    r2 = test_client.post(
        "/api/behavioral/links",
        json={
            "question_id": q.id,
            "example_id": ex2.id,
            "is_primary": False,
        },
    )
    assert r2.status_code == 201
    assert r2.json()["is_primary"] is False


def test_linked_questions_surface_is_primary(
    test_client, seed_question_and_examples
):
    """GET /examples/by-example-id includes is_primary on each linked question."""
    q, ex1, _ = seed_question_and_examples

    test_client.post(
        "/api/behavioral/links",
        json={
            "question_id": q.id,
            "example_id": ex1.id,
            "is_primary": True,
        },
    )

    resp = test_client.get(f"/api/behavioral/examples/by-example-id/{ex1.example_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["linked_questions"]) == 1
    lq = body["linked_questions"][0]
    assert lq["id"] == q.id
    assert lq["is_primary"] is True


def test_no_angle_label_field_on_models():
    """Guard against accidental reintroduction of angle_label (T-P1-579 decision)."""
    from src.backend.models.behavioral import QuestionExampleLink

    attrs = {c.name for c in QuestionExampleLink.__table__.columns}
    assert "angle_label" not in attrs
    q_attrs = {c.name for c in BehavioralQuestion.__table__.columns}
    assert "angle_label" not in q_attrs
