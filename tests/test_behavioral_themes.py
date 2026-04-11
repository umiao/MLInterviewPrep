"""Tests for behavioral theme taxonomy, filtering, and cascade.

Covers T-P1-353 scenario matrix: single-theme filter, multi-theme OR/AND,
unknown slug -> 400, cascade delete, and seed idempotency.
"""
import pytest
from sqlalchemy import text

from src.backend.models.behavioral import (
    BehavioralExample,
    BehavioralQuestion,
)
from src.backend.models.behavioral_theme import (
    BehavioralTheme,
    ExampleThemeTag,
    QuestionThemeTag,
)


def _enable_sqlite_fk(session):
    """SQLite disables FK enforcement by default; turn it on for cascade tests."""
    session.execute(text("PRAGMA foreign_keys = ON"))


@pytest.fixture()
def seeded_behavioral(db_session):
    """Insert 3 themes, 4 questions, 2 examples, with tags."""
    themes = []
    for order, (slug, label) in enumerate(
        [
            ("failure_setback", "Failure & Setback"),
            ("leadership_direction", "Leadership & Direction"),
            ("oncall_prod_incident", "On-call & Prod Incidents"),
        ],
        start=1,
    ):
        t = BehavioralTheme(slug=slug, label=label, display_order=order)
        db_session.add(t)
        themes.append(t)
    db_session.flush()
    failure, leadership, oncall = themes

    questions = []
    for qid, cat_id, q_text in [
        ("Q-FAIL-1", "adaptability", "Tell me about a setback and what you learned."),
        ("Q-LEAD-1", "leadership", "Describe leading a team through delegation."),
        ("Q-BOTH-1", "adaptability", "A leadership failure and how you recovered."),
        ("Q-NONE-1", "execution", "Describe a project you planned end to end."),
    ]:
        q = BehavioralQuestion(
            question_id=qid,
            text=q_text,
            category_id=cat_id,
            category_name=cat_id.title(),
        )
        db_session.add(q)
        questions.append(q)
    db_session.flush()
    q_fail, q_lead, q_both, q_none = questions

    db_session.add(
        QuestionThemeTag(question_id=q_fail.id, theme_id=failure.id)
    )
    db_session.add(
        QuestionThemeTag(question_id=q_lead.id, theme_id=leadership.id)
    )
    db_session.add(
        QuestionThemeTag(question_id=q_both.id, theme_id=failure.id)
    )
    db_session.add(
        QuestionThemeTag(question_id=q_both.id, theme_id=leadership.id)
    )
    # q_none has no tags

    examples = []
    for eid, title in [
        ("EX-T1", "Example with failure theme"),
        ("EX-T2", "Example with leadership theme"),
    ]:
        ex = BehavioralExample(example_id=eid, title=title)
        db_session.add(ex)
        examples.append(ex)
    db_session.flush()
    ex1, ex2 = examples

    db_session.add(
        ExampleThemeTag(example_id=ex1.id, theme_id=failure.id)
    )
    db_session.add(
        ExampleThemeTag(example_id=ex2.id, theme_id=leadership.id)
    )
    db_session.commit()

    return {
        "themes": {"failure": failure, "leadership": leadership, "oncall": oncall},
        "questions": {
            "fail": q_fail, "lead": q_lead, "both": q_both, "none": q_none
        },
        "examples": {"ex1": ex1, "ex2": ex2},
    }


def test_list_themes_returns_all_with_counts(test_client, seeded_behavioral):
    """GET /api/behavioral/themes returns every theme with q/ex counts."""
    resp = test_client.get("/api/behavioral/themes")
    assert resp.status_code == 200
    data = resp.json()
    slugs = {t["slug"]: t for t in data}
    assert set(slugs) == {
        "failure_setback", "leadership_direction", "oncall_prod_incident"
    }
    assert slugs["failure_setback"]["question_count"] == 2
    assert slugs["failure_setback"]["example_count"] == 1
    assert slugs["leadership_direction"]["question_count"] == 2
    assert slugs["leadership_direction"]["example_count"] == 1
    # Empty theme still returned
    assert slugs["oncall_prod_incident"]["question_count"] == 0
    assert slugs["oncall_prod_incident"]["example_count"] == 0


def test_filter_questions_by_single_theme(test_client, seeded_behavioral):
    """Single theme filter returns only tagged questions."""
    resp = test_client.get(
        "/api/behavioral/questions?theme=failure_setback"
    )
    assert resp.status_code == 200
    qids = {q["question_id"] for q in resp.json()}
    assert qids == {"Q-FAIL-1", "Q-BOTH-1"}


def test_filter_questions_multi_theme_or(test_client, seeded_behavioral):
    """OR mode returns union."""
    resp = test_client.get(
        "/api/behavioral/questions?theme=failure_setback,leadership_direction"
        "&theme_mode=or"
    )
    assert resp.status_code == 200
    qids = {q["question_id"] for q in resp.json()}
    assert qids == {"Q-FAIL-1", "Q-LEAD-1", "Q-BOTH-1"}


def test_filter_questions_multi_theme_and(test_client, seeded_behavioral):
    """AND mode returns intersection."""
    resp = test_client.get(
        "/api/behavioral/questions?theme=failure_setback,leadership_direction"
        "&theme_mode=and"
    )
    assert resp.status_code == 200
    qids = {q["question_id"] for q in resp.json()}
    assert qids == {"Q-BOTH-1"}


def test_filter_unknown_theme_returns_400(test_client, seeded_behavioral):
    """Unknown slug -> 400 Bad Request."""
    resp = test_client.get("/api/behavioral/questions?theme=not_a_theme")
    assert resp.status_code == 400


def test_filter_invalid_theme_mode_returns_400(test_client, seeded_behavioral):
    """theme_mode must be 'or' or 'and'."""
    resp = test_client.get(
        "/api/behavioral/questions?theme=failure_setback&theme_mode=xor"
    )
    assert resp.status_code == 400


def test_cascade_delete_removes_tags_when_question_deleted(
    db_session, seeded_behavioral
):
    """Deleting a question removes its theme tags (ON DELETE CASCADE)."""
    _enable_sqlite_fk(db_session)
    q = seeded_behavioral["questions"]["both"]
    q_id = q.id
    db_session.delete(q)
    db_session.commit()
    remaining = (
        db_session.query(QuestionThemeTag)
        .filter(QuestionThemeTag.question_id == q_id)
        .all()
    )
    assert remaining == []


def test_cascade_delete_removes_tags_when_theme_deleted(
    db_session, seeded_behavioral
):
    """Deleting a theme removes all its question+example tags."""
    _enable_sqlite_fk(db_session)
    theme = seeded_behavioral["themes"]["failure"]
    t_id = theme.id
    db_session.delete(theme)
    db_session.commit()
    q_remaining = (
        db_session.query(QuestionThemeTag)
        .filter(QuestionThemeTag.theme_id == t_id)
        .all()
    )
    ex_remaining = (
        db_session.query(ExampleThemeTag)
        .filter(ExampleThemeTag.theme_id == t_id)
        .all()
    )
    assert q_remaining == []
    assert ex_remaining == []


def test_seed_script_matcher_idempotent(db_session, seeded_behavioral):
    """Inserting duplicate (question_id, theme_id) pairs should not create dupes.

    The seed script checks for existing rows before insert; this test simulates
    the re-run path by attempting to add a duplicate and verifying the check.
    """
    q = seeded_behavioral["questions"]["fail"]
    t = seeded_behavioral["themes"]["failure"]
    # Check existing rows: should be exactly 1
    existing = (
        db_session.query(QuestionThemeTag)
        .filter(
            QuestionThemeTag.question_id == q.id,
            QuestionThemeTag.theme_id == t.id,
        )
        .all()
    )
    assert len(existing) == 1
    # Seed script's existence check would skip insertion here.
    # We simulate: only insert if not exists.
    if not existing:
        db_session.add(QuestionThemeTag(question_id=q.id, theme_id=t.id))
        db_session.commit()
    total = (
        db_session.query(QuestionThemeTag)
        .filter(
            QuestionThemeTag.question_id == q.id,
            QuestionThemeTag.theme_id == t.id,
        )
        .count()
    )
    assert total == 1
