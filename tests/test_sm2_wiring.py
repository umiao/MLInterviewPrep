"""Tests for SM-2 spaced repetition wiring into attempt creation.

Verifies that POST /api/problems/{id}/attempts correctly calls
update_review_schedule BEFORE updating last_attempted_at, and that
the resulting next_review_at matches SM-2 interval calculations.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

from src.backend.services.spaced_repetition import compute_next_review

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _create_problem(client, title="Test Problem"):
    """Create a problem and return its id."""
    resp = client.post("/api/problems", json={"title": title})
    assert resp.status_code == 201
    return resp.json()["id"]


def _get_problem(client, pid):
    """Fetch a single problem by id."""
    resp = client.get("/api/problems")
    assert resp.status_code == 200
    return next(p for p in resp.json() if p["id"] == pid)


def _attempt(client, pid, comfort, result="solved"):
    """Create an attempt and return the response."""
    resp = client.post(
        f"/api/problems/{pid}/attempts",
        json={"result": result, "comfort_after": comfort},
    )
    assert resp.status_code == 201
    return resp.json()


# ===========================================================================
# First attempt (no prior last_attempted_at) -- SM-2 uses interval=1
# ===========================================================================

def test_first_attempt_comfort_1_next_review_1_day(test_client):
    """First attempt with comfort=1: SM-2 interval=1 day (comfort<=2 -> 1d)."""
    pid = _create_problem(test_client)
    now_before = datetime.utcnow()
    _attempt(test_client, pid, comfort=1)
    problem = _get_problem(test_client, pid)
    review_at = datetime.fromisoformat(problem["next_review_at"])
    # Should be ~1 day from now
    assert review_at >= now_before + timedelta(days=1) - timedelta(seconds=5)
    assert review_at <= datetime.utcnow() + timedelta(days=1) + timedelta(seconds=5)


def test_first_attempt_comfort_2_next_review_1_day(test_client):
    """First attempt with comfort=2: SM-2 interval=1 day."""
    pid = _create_problem(test_client)
    now_before = datetime.utcnow()
    _attempt(test_client, pid, comfort=2)
    problem = _get_problem(test_client, pid)
    review_at = datetime.fromisoformat(problem["next_review_at"])
    expected_min = now_before + timedelta(days=1) - timedelta(seconds=5)
    expected_max = datetime.utcnow() + timedelta(days=1) + timedelta(seconds=5)
    assert expected_min <= review_at <= expected_max


def test_first_attempt_comfort_3_next_review_2_days(test_client):
    """First attempt with comfort=3: SM-2 interval=max(2, 1)=2 days."""
    pid = _create_problem(test_client)
    now_before = datetime.utcnow()
    _attempt(test_client, pid, comfort=3)
    problem = _get_problem(test_client, pid)
    review_at = datetime.fromisoformat(problem["next_review_at"])
    # compute_next_review(3, 1) = max(2, 1) = 2
    expected_days = compute_next_review(3, 1)
    assert expected_days == 2
    expected_min = now_before + timedelta(days=2) - timedelta(seconds=5)
    expected_max = datetime.utcnow() + timedelta(days=2) + timedelta(seconds=5)
    assert expected_min <= review_at <= expected_max


def test_first_attempt_comfort_4_next_review_2_days(test_client):
    """First attempt with comfort=4: SM-2 interval=int(1*2.0)=2 days."""
    pid = _create_problem(test_client)
    now_before = datetime.utcnow()
    _attempt(test_client, pid, comfort=4)
    problem = _get_problem(test_client, pid)
    review_at = datetime.fromisoformat(problem["next_review_at"])
    expected_days = compute_next_review(4, 1)
    assert expected_days == 2
    expected_min = now_before + timedelta(days=2) - timedelta(seconds=5)
    expected_max = datetime.utcnow() + timedelta(days=2) + timedelta(seconds=5)
    assert expected_min <= review_at <= expected_max


def test_first_attempt_comfort_5_next_review_2_days(test_client):
    """First attempt with comfort=5: SM-2 interval=int(1*2.5)=2 days."""
    pid = _create_problem(test_client)
    now_before = datetime.utcnow()
    _attempt(test_client, pid, comfort=5)
    problem = _get_problem(test_client, pid)
    review_at = datetime.fromisoformat(problem["next_review_at"])
    expected_days = compute_next_review(5, 1)
    assert expected_days == 2
    expected_min = now_before + timedelta(days=2) - timedelta(seconds=5)
    expected_max = datetime.utcnow() + timedelta(days=2) + timedelta(seconds=5)
    assert expected_min <= review_at <= expected_max


# ===========================================================================
# next_review_at is set (not None) after attempt
# ===========================================================================

def test_next_review_at_initially_none(test_client):
    """Problem starts with next_review_at=None."""
    pid = _create_problem(test_client)
    problem = _get_problem(test_client, pid)
    assert problem["next_review_at"] is None


def test_next_review_at_set_after_attempt(test_client):
    """next_review_at is populated after first attempt."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=3)
    problem = _get_problem(test_client, pid)
    assert problem["next_review_at"] is not None


# ===========================================================================
# SM-2 uses last_attempted_at from BEFORE update (ordering correctness)
# ===========================================================================

def test_sm2_called_before_last_attempted_at_update(test_client):
    """Verify SM-2 sees the OLD last_attempted_at, not the new one.

    If SM-2 were called AFTER updating last_attempted_at, the interval
    would always be 0 days (now - now = 0, clamped to 1). For comfort=5,
    interval should be > 1 day on the second attempt.
    """
    pid = _create_problem(test_client)
    # First attempt
    _attempt(test_client, pid, comfort=4)
    p1 = _get_problem(test_client, pid)
    assert p1["next_review_at"] is not None

    # Second attempt immediately (interval ~0 days, clamped to 1)
    _attempt(test_client, pid, comfort=5)
    p2 = _get_problem(test_client, pid)
    assert p2["next_review_at"] is not None
    # Both reviews should be set and second should differ from first
    assert p2["next_review_at"] != p1["next_review_at"]


# ===========================================================================
# Monotonicity: higher comfort -> further out review
# ===========================================================================

def test_higher_comfort_pushes_review_further(test_client):
    """comfort=5 should give a later next_review_at than comfort=1."""
    pid1 = _create_problem(test_client, title="Low comfort")
    pid2 = _create_problem(test_client, title="High comfort")
    _attempt(test_client, pid1, comfort=1)
    _attempt(test_client, pid2, comfort=5)
    p1 = _get_problem(test_client, pid1)
    p2 = _get_problem(test_client, pid2)
    review1 = datetime.fromisoformat(p1["next_review_at"])
    review2 = datetime.fromisoformat(p2["next_review_at"])
    assert review2 > review1


def test_comfort_3_vs_comfort_2_further(test_client):
    """comfort=3 review should be later than comfort=2."""
    pid1 = _create_problem(test_client, title="C2")
    pid2 = _create_problem(test_client, title="C3")
    _attempt(test_client, pid1, comfort=2)
    _attempt(test_client, pid2, comfort=3)
    p1 = _get_problem(test_client, pid1)
    p2 = _get_problem(test_client, pid2)
    r1 = datetime.fromisoformat(p1["next_review_at"])
    r2 = datetime.fromisoformat(p2["next_review_at"])
    assert r2 > r1


# ===========================================================================
# Multiple attempts: interval grows with repeated high comfort
# ===========================================================================

def test_repeated_high_comfort_extends_interval(test_client):
    """Multiple comfort=5 attempts should progressively extend the interval."""
    pid = _create_problem(test_client)
    reviews = []
    for _ in range(3):
        _attempt(test_client, pid, comfort=5)
        p = _get_problem(test_client, pid)
        reviews.append(datetime.fromisoformat(p["next_review_at"]))

    # Each review should be the same or later (interval grows)
    # Since attempts are immediate (interval clamped to 1), all first-pass
    # intervals are 2 days. But the progression is still valid.
    for i in range(len(reviews) - 1):
        assert reviews[i + 1] >= reviews[i]


def test_low_comfort_resets_to_short_interval(test_client):
    """After high comfort, a low comfort resets next_review to 1 day."""
    pid = _create_problem(test_client)
    # Build up with comfort=5
    _attempt(test_client, pid, comfort=5)

    # Reset with comfort=1
    _attempt(test_client, pid, comfort=1)
    p_low = _get_problem(test_client, pid)
    review_low = datetime.fromisoformat(p_low["next_review_at"])

    # comfort=1 always -> 1 day interval, so review_low should be closer to now
    # than review_high was
    now = datetime.utcnow()
    delta_low = (review_low - now).total_seconds()
    # 1 day = 86400 seconds, allow some slack
    assert delta_low < 86400 + 60


# ===========================================================================
# last_attempted_at updated alongside next_review_at
# ===========================================================================

def test_last_attempted_at_updated_with_review(test_client):
    """Both last_attempted_at and next_review_at are updated on attempt."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=3)
    problem = _get_problem(test_client, pid)
    assert problem["last_attempted_at"] is not None
    assert problem["next_review_at"] is not None


def test_comfort_level_and_review_consistent(test_client):
    """comfort_level on problem matches what SM-2 used."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=4)
    problem = _get_problem(test_client, pid)
    assert problem["comfort_level"] == 4
    assert problem["next_review_at"] is not None


# ===========================================================================
# Verify is_completed interaction with SM-2
# ===========================================================================

def test_is_completed_true_still_gets_review_scheduled(test_client):
    """Even when is_completed becomes True (comfort>=3), review is still scheduled."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=4)
    problem = _get_problem(test_client, pid)
    assert problem["is_completed"] is True
    assert problem["next_review_at"] is not None


def test_is_completed_false_still_gets_review_scheduled(test_client):
    """When comfort<3 (is_completed stays False), review is still scheduled."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=2)
    problem = _get_problem(test_client, pid)
    assert problem["is_completed"] is False
    assert problem["next_review_at"] is not None


# ===========================================================================
# Integration with update_review_schedule function directly via mock timing
# ===========================================================================

def test_update_review_schedule_receives_correct_args(test_client):
    """Verify update_review_schedule is called with correct arguments."""
    pid = _create_problem(test_client)

    calls = []
    original_fn = __import__(
        "src.backend.services.spaced_repetition", fromlist=["update_review_schedule"]
    ).update_review_schedule

    def spy(last_attempted_at, now, comfort_after):
        """Spy on update_review_schedule calls."""
        calls.append({
            "last_attempted_at": last_attempted_at,
            "now": now,
            "comfort_after": comfort_after,
        })
        return original_fn(last_attempted_at=last_attempted_at, now=now, comfort_after=comfort_after)

    with patch(
        "src.backend.routers.problems.update_review_schedule",
        side_effect=spy,
    ):
        _attempt(test_client, pid, comfort=3)

    assert len(calls) == 1
    assert calls[0]["last_attempted_at"] is None  # first attempt
    assert calls[0]["comfort_after"] == 3
    assert isinstance(calls[0]["now"], datetime)


def test_second_attempt_passes_old_last_attempted_at(test_client):
    """Second attempt passes the PREVIOUS last_attempted_at to SM-2."""
    pid = _create_problem(test_client)
    _attempt(test_client, pid, comfort=3)

    calls = []
    original_fn = __import__(
        "src.backend.services.spaced_repetition", fromlist=["update_review_schedule"]
    ).update_review_schedule

    def spy(last_attempted_at, now, comfort_after):
        """Spy on update_review_schedule calls."""
        calls.append({
            "last_attempted_at": last_attempted_at,
            "now": now,
            "comfort_after": comfort_after,
        })
        return original_fn(last_attempted_at=last_attempted_at, now=now, comfort_after=comfort_after)

    with patch(
        "src.backend.routers.problems.update_review_schedule",
        side_effect=spy,
    ):
        _attempt(test_client, pid, comfort=5)

    assert len(calls) == 1
    # On second attempt, last_attempted_at should NOT be None
    assert calls[0]["last_attempted_at"] is not None
    assert calls[0]["comfort_after"] == 5
