"""Tests for Problem, Attempt, QASession models."""
import json

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.problem import Attempt, Problem, QASession


def test_create_problem_with_tags(db_session):
    """Problem JSON tags round-trip works."""
    p = Problem(title="Two Sum", tags=json.dumps(["dp", "array"], ensure_ascii=False))
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.tags_list == ["dp", "array"]
    assert p.id is not None


def test_problem_company_tags(db_session):
    """company_tags JSON property works."""
    p = Problem(title="Test", company_tags=json.dumps(["google"], ensure_ascii=False))
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.company_tags_list == ["google"]


def test_problem_nullable_leetcode_id(db_session):
    """Problem can be created with null leetcode_id."""
    p = Problem(title="Custom Problem")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.leetcode_id is None
    assert p.id is not None


def test_problem_defaults(db_session):
    """Problem defaults: category=algorithm, priority=2, comfort_level=0, is_completed=False."""
    p = Problem(title="Defaults Check")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.category == "algorithm"
    assert p.priority == 2
    assert p.comfort_level == 0
    assert p.is_completed is False
    assert p.created_at is not None


def test_problem_tags_list_setter(db_session):
    """tags_list setter serializes to JSON correctly."""
    p = Problem(title="Setter Test")
    p.tags_list = ["greedy", "sorting"]
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert json.loads(p.tags) == ["greedy", "sorting"]
    assert p.tags_list == ["greedy", "sorting"]


def test_problem_empty_tags_list(db_session):
    """Empty/null tags return empty list."""
    p = Problem(title="No Tags")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.tags_list == []
    assert p.company_tags_list == []


def test_problem_invalid_difficulty(db_session):
    """Problem with invalid difficulty raises IntegrityError."""
    p = Problem(title="Bad Diff", difficulty="extreme")
    db_session.add(p)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_attempt_linked_to_problem(db_session):
    """Attempt links to Problem correctly."""
    p = Problem(title="Test Problem")
    db_session.add(p)
    db_session.commit()

    a = Attempt(problem_id=p.id, result="solved", comfort_after=4)
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)

    assert a.problem_id == p.id
    assert a.problem.title == "Test Problem"


def test_attempt_invalid_result(db_session):
    """Attempt with invalid result raises IntegrityError."""
    p = Problem(title="Test")
    db_session.add(p)
    db_session.commit()

    a = Attempt(problem_id=p.id, result="invalid_value", comfort_after=3)
    db_session.add(a)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_attempt_all_valid_results(db_session):
    """All valid result values are accepted."""
    p = Problem(title="Multi Result")
    db_session.add(p)
    db_session.commit()

    for result in ("solved", "hint", "failed", "timeout"):
        a = Attempt(problem_id=p.id, result=result, comfort_after=3)
        db_session.add(a)
    db_session.commit()
    assert len(p.attempts) == 4


def test_attempt_llm_review_text(db_session):
    """Attempt llm_review stores JSON text."""
    p = Problem(title="LLM Test")
    db_session.add(p)
    db_session.commit()

    review = {"verdict": "optimal", "feedback": "Good approach"}
    a = Attempt(
        problem_id=p.id,
        result="solved",
        comfort_after=5,
        llm_review=json.dumps(review, ensure_ascii=False),
    )
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    assert json.loads(a.llm_review) == review


def test_qa_session_messages_json(db_session):
    """QASession messages JSON round-trip."""
    msgs = [{"role": "user", "content": "hello", "timestamp": "2024-01-01"}]
    s = QASession(messages=json.dumps(msgs, ensure_ascii=False), topic="test")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    assert s.messages_list == msgs


def test_qa_session_linked_to_problem(db_session):
    """QASession can optionally link to a problem."""
    p = Problem(title="QA Linked")
    db_session.add(p)
    db_session.commit()

    s = QASession(problem_id=p.id, messages='[]', topic="linked")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    assert s.problem.title == "QA Linked"
    assert len(p.qa_sessions) == 1


def test_qa_session_without_problem(db_session):
    """QASession works without a problem (problem_id nullable)."""
    s = QASession(messages='[{"role":"user","content":"hi"}]', topic="general")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    assert s.problem_id is None
    assert s.id is not None


def test_qa_session_messages_list_setter(db_session):
    """messages_list setter serializes correctly."""
    s = QASession(messages='[]', topic="setter")
    db_session.add(s)
    db_session.commit()

    new_msgs = [{"role": "assistant", "content": "hello"}]
    s.messages_list = new_msgs
    db_session.commit()
    db_session.refresh(s)
    assert s.messages_list == new_msgs


def test_problem_cascade_delete(db_session):
    """Deleting a problem cascades to attempts and qa_sessions."""
    p = Problem(title="Cascade Test")
    db_session.add(p)
    db_session.commit()

    a = Attempt(problem_id=p.id, result="solved", comfort_after=3)
    s = QASession(problem_id=p.id, messages='[]', topic="cascade")
    db_session.add_all([a, s])
    db_session.commit()

    db_session.delete(p)
    db_session.commit()

    assert db_session.query(Attempt).count() == 0
    assert db_session.query(QASession).filter_by(problem_id=p.id).count() == 0
