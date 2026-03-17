"""Tests for Problem and Attempt Pydantic schemas."""
import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from src.backend.schemas.problem import (
    AttemptCreate,
    AttemptResponse,
    ProblemCreate,
    ProblemResponse,
    ProblemUpdate,
)

# --- ProblemCreate ---


def test_valid_problem_create():
    """Valid ProblemCreate succeeds with defaults."""
    p = ProblemCreate(title="Two Sum", difficulty="easy")
    assert p.title == "Two Sum"
    assert p.difficulty == "easy"
    assert p.tags == []
    assert p.company_tags == []
    assert p.priority == 2
    assert p.category == "algorithm"
    assert p.leetcode_id is None
    assert p.url is None
    assert p.pattern is None
    assert p.source is None


def test_problem_create_all_fields():
    """ProblemCreate with all fields populated."""
    p = ProblemCreate(
        leetcode_id=1,
        title="Two Sum",
        url="https://leetcode.com/problems/two-sum",
        difficulty="easy",
        tags=["array", "hash_table"],
        pattern="hash_map",
        category="algorithm",
        source="blind75",
        company_tags=["google", "meta"],
        priority=1,
    )
    assert p.leetcode_id == 1
    assert p.tags == ["array", "hash_table"]
    assert p.company_tags == ["google", "meta"]
    assert p.priority == 1


def test_problem_create_empty_title():
    """Empty title raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemCreate(title="")


def test_problem_create_whitespace_title():
    """Whitespace-only title with length >= 1 is accepted (min_length check)."""
    p = ProblemCreate(title=" ")
    assert p.title == " "


def test_problem_create_invalid_difficulty():
    """Invalid difficulty raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemCreate(title="Test", difficulty="impossible")


def test_problem_create_invalid_category():
    """Invalid category raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemCreate(title="Test", category="data_structures")


def test_problem_create_all_categories():
    """All valid category values are accepted."""
    for cat in ("algorithm", "ml_coding", "system_design"):
        p = ProblemCreate(title="Test", category=cat)
        assert p.category == cat


def test_problem_create_all_difficulties():
    """All valid difficulty values are accepted."""
    for diff in ("easy", "medium", "hard"):
        p = ProblemCreate(title="Test", difficulty=diff)
        assert p.difficulty == diff


def test_problem_create_null_difficulty_ok():
    """Null difficulty is accepted."""
    p = ProblemCreate(title="Test")
    assert p.difficulty is None


def test_problem_create_priority_out_of_range():
    """Priority outside 1-3 raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemCreate(title="Test", priority=0)
    with pytest.raises(ValidationError):
        ProblemCreate(title="Test", priority=4)


# --- ProblemUpdate ---


def test_problem_update_all_none():
    """ProblemUpdate with no fields set creates valid schema."""
    p = ProblemUpdate()
    assert p.model_dump(exclude_unset=True) == {}


def test_problem_update_partial():
    """ProblemUpdate with partial fields uses exclude_unset correctly."""
    p = ProblemUpdate(difficulty="hard", comfort_level=3)
    dumped = p.model_dump(exclude_unset=True)
    assert dumped == {"difficulty": "hard", "comfort_level": 3}
    assert "title" not in dumped


def test_problem_update_comfort_level_6():
    """comfort_level=6 raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemUpdate(comfort_level=6)


def test_problem_update_comfort_level_negative():
    """comfort_level=-1 raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemUpdate(comfort_level=-1)


def test_problem_update_comfort_level_valid():
    """comfort_level 0-5 all succeed."""
    for level in range(6):
        p = ProblemUpdate(comfort_level=level)
        assert p.comfort_level == level


def test_problem_update_invalid_difficulty():
    """Invalid difficulty in update raises ValidationError."""
    with pytest.raises(ValidationError):
        ProblemUpdate(difficulty="nightmare")


def test_problem_update_is_completed():
    """Boolean is_completed field works."""
    p = ProblemUpdate(is_completed=True)
    assert p.model_dump(exclude_unset=True) == {"is_completed": True}


# --- ProblemResponse ---


def test_problem_response_from_dict():
    """ProblemResponse from dict with from_attributes."""
    now = datetime.utcnow()
    data = {
        "id": 1,
        "title": "Two Sum",
        "tags": ["array"],
        "company_tags": ["google"],
        "created_at": now,
    }
    p = ProblemResponse.model_validate(data)
    assert p.id == 1
    assert p.tags == ["array"]
    assert p.created_at == now


def test_problem_response_from_attributes():
    """ProblemResponse uses from_attributes to read model-like objects."""
    mock_obj = MagicMock()
    mock_obj.id = 1
    mock_obj.leetcode_id = 42
    mock_obj.title = "Test"
    mock_obj.url = None
    mock_obj.difficulty = "easy"
    mock_obj.tags = json.dumps(["array", "dp"])
    mock_obj.pattern = "sliding_window"
    mock_obj.category = "algorithm"
    mock_obj.source = "blind75"
    mock_obj.company_tags = json.dumps(["google"])
    mock_obj.priority = 1
    mock_obj.is_completed = True
    mock_obj.comfort_level = 4
    mock_obj.created_at = datetime(2026, 1, 1)
    mock_obj.last_attempted_at = None
    mock_obj.next_review_at = None
    mock_obj.description = None
    mock_obj.neetcode_slug = None
    mock_obj.description_source = None

    p = ProblemResponse.model_validate(mock_obj, from_attributes=True)
    assert p.id == 1
    assert p.tags == ["array", "dp"]
    assert p.company_tags == ["google"]


def test_problem_response_null_tags_become_empty_list():
    """Null tags/company_tags from DB become empty lists."""
    mock_obj = MagicMock()
    mock_obj.id = 1
    mock_obj.leetcode_id = None
    mock_obj.title = "Test"
    mock_obj.url = None
    mock_obj.difficulty = None
    mock_obj.tags = None
    mock_obj.pattern = None
    mock_obj.category = "algorithm"
    mock_obj.source = None
    mock_obj.company_tags = None
    mock_obj.priority = 2
    mock_obj.is_completed = False
    mock_obj.comfort_level = 0
    mock_obj.created_at = None
    mock_obj.last_attempted_at = None
    mock_obj.next_review_at = None
    mock_obj.description = None
    mock_obj.neetcode_slug = None
    mock_obj.description_source = None

    p = ProblemResponse.model_validate(mock_obj, from_attributes=True)
    assert p.tags == []
    assert p.company_tags == []


# --- AttemptCreate ---


def test_valid_attempt_create():
    """Valid AttemptCreate succeeds."""
    a = AttemptCreate(result="solved", comfort_after=4)
    assert a.result == "solved"
    assert a.comfort_after == 4
    assert a.duration_seconds is None


def test_attempt_create_all_fields():
    """AttemptCreate with all fields."""
    a = AttemptCreate(
        duration_seconds=1200,
        result="hint",
        approach_notes="Used two pointers",
        complexity_time="O(n)",
        complexity_space="O(1)",
        comfort_after=3,
    )
    assert a.duration_seconds == 1200
    assert a.approach_notes == "Used two pointers"


def test_attempt_invalid_result():
    """Invalid result raises ValidationError."""
    with pytest.raises(ValidationError):
        AttemptCreate(result="invalid", comfort_after=3)


def test_attempt_all_valid_results():
    """All valid result values are accepted."""
    for result in ("solved", "hint", "failed", "timeout"):
        a = AttemptCreate(result=result, comfort_after=3)
        assert a.result == result


def test_attempt_comfort_after_required():
    """comfort_after is required."""
    with pytest.raises(ValidationError):
        AttemptCreate(result="solved")


def test_attempt_comfort_out_of_range():
    """comfort_after outside 1-5 raises ValidationError."""
    with pytest.raises(ValidationError):
        AttemptCreate(result="solved", comfort_after=0)
    with pytest.raises(ValidationError):
        AttemptCreate(result="solved", comfort_after=6)


def test_attempt_comfort_boundary_values():
    """comfort_after boundary values 1 and 5 are valid."""
    a1 = AttemptCreate(result="solved", comfort_after=1)
    assert a1.comfort_after == 1
    a5 = AttemptCreate(result="solved", comfort_after=5)
    assert a5.comfort_after == 5


def test_attempt_negative_duration():
    """Negative duration raises ValidationError."""
    with pytest.raises(ValidationError):
        AttemptCreate(result="solved", comfort_after=3, duration_seconds=-1)


# --- AttemptResponse ---


def test_attempt_response_from_dict():
    """AttemptResponse from dict."""
    now = datetime.utcnow()
    data = {
        "id": 1,
        "problem_id": 42,
        "started_at": now,
        "result": "solved",
        "comfort_after": 5,
    }
    a = AttemptResponse.model_validate(data)
    assert a.id == 1
    assert a.problem_id == 42


def test_attempt_response_from_attributes():
    """AttemptResponse uses from_attributes."""
    mock_obj = MagicMock()
    mock_obj.id = 1
    mock_obj.problem_id = 10
    mock_obj.started_at = datetime(2026, 1, 1)
    mock_obj.duration_seconds = 600
    mock_obj.result = "solved"
    mock_obj.approach_notes = "DP approach"
    mock_obj.complexity_time = "O(n)"
    mock_obj.complexity_space = "O(n)"
    mock_obj.llm_review = '{"verdict": "correct"}'
    mock_obj.comfort_after = 4

    a = AttemptResponse.model_validate(mock_obj, from_attributes=True)
    assert a.id == 1
    assert a.llm_review == '{"verdict": "correct"}'
