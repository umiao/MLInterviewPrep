"""Comprehensive tests for SM-2 spaced repetition algorithm."""
from datetime import datetime, timedelta

import pytest

from src.backend.services.spaced_repetition import (
    compute_next_review,
    update_review_schedule,
)

# ── compute_next_review: comfort <= 2 always returns 1 day ──────────────


def test_comfort_1_returns_1_day() -> None:
    """Comfort 1 always returns 1 day regardless of previous interval."""
    assert compute_next_review(1, 5) == 1


def test_comfort_2_returns_1_day() -> None:
    """Comfort 2 always returns 1 day regardless of previous interval."""
    assert compute_next_review(2, 10) == 1


def test_comfort_1_large_interval_still_1() -> None:
    """Comfort 1 with large previous interval still returns 1."""
    assert compute_next_review(1, 100) == 1


def test_comfort_2_small_interval_returns_1() -> None:
    """Comfort 2 with interval=1 returns 1."""
    assert compute_next_review(2, 1) == 1


def test_comfort_1_zero_interval_returns_1() -> None:
    """Comfort 1 with zero interval (clamped to 1) returns 1."""
    assert compute_next_review(1, 0) == 1


def test_comfort_2_zero_interval_returns_1() -> None:
    """Comfort 2 with zero interval returns 1."""
    assert compute_next_review(2, 0) == 1


# ── compute_next_review: comfort 3 -> max(2, prev) ──────────────────────


def test_comfort_3_keeps_interval_when_above_2() -> None:
    """Comfort 3 returns previous interval when >= 2."""
    assert compute_next_review(3, 3) == 3


def test_comfort_3_minimum_is_2() -> None:
    """Comfort 3 has a floor of 2 days."""
    assert compute_next_review(3, 1) == 2


def test_comfort_3_zero_interval_clamped() -> None:
    """Comfort 3 with 0 interval: clamped to 1, then max(2, 1) = 2."""
    assert compute_next_review(3, 0) == 2


def test_comfort_3_large_interval() -> None:
    """Comfort 3 preserves large intervals."""
    assert compute_next_review(3, 30) == 30


def test_comfort_3_interval_exactly_2() -> None:
    """Comfort 3 with interval=2 returns 2."""
    assert compute_next_review(3, 2) == 2


# ── compute_next_review: comfort 4 -> 2x ────────────────────────────────


def test_comfort_4_doubles() -> None:
    """Comfort 4 doubles the interval."""
    assert compute_next_review(4, 4) == 8


def test_comfort_4_doubles_small() -> None:
    """Comfort 4 doubles small interval."""
    assert compute_next_review(4, 3) == 6


def test_comfort_4_doubles_one() -> None:
    """Comfort 4 with interval=1 returns 2."""
    assert compute_next_review(4, 1) == 2


def test_comfort_4_zero_interval_clamped_then_doubled() -> None:
    """Comfort 4: 0 clamped to 1, then 1*2 = 2."""
    assert compute_next_review(4, 0) == 2


def test_comfort_4_large_interval() -> None:
    """Comfort 4 doubles large interval."""
    assert compute_next_review(4, 15) == 30


# ── compute_next_review: comfort 5 -> 2.5x ──────────────────────────────


def test_comfort_5_multiplies_2_5() -> None:
    """Comfort 5 multiplies interval by 2.5."""
    assert compute_next_review(5, 4) == 10


def test_comfort_5_interval_1() -> None:
    """Comfort 5 with interval=1 returns 2 (int(1*2.5))."""
    assert compute_next_review(5, 1) == 2


def test_comfort_5_interval_2() -> None:
    """Comfort 5 with interval=2 returns 5."""
    assert compute_next_review(5, 2) == 5


def test_comfort_5_zero_interval_clamped() -> None:
    """Comfort 5: 0 clamped to 1, then int(1*2.5) = 2."""
    assert compute_next_review(5, 0) == 2


def test_comfort_5_large_interval() -> None:
    """Comfort 5 with large interval."""
    assert compute_next_review(5, 20) == 50


def test_comfort_5_truncation() -> None:
    """Comfort 5 truncates fractional result (int, not round)."""
    # 3 * 2.5 = 7.5 -> int(7.5) = 7
    assert compute_next_review(5, 3) == 7


# ── compute_next_review: clamping ────────────────────────────────────────


def test_negative_interval_clamped_to_1() -> None:
    """Negative previous_interval_days is clamped to 1."""
    assert compute_next_review(4, -5) == 2  # max(1, -5) = 1, 1*2 = 2


def test_return_always_positive() -> None:
    """Return value is always >= 1 for any valid comfort level."""
    for comfort in range(1, 6):
        for interval in [-10, -1, 0, 1, 2, 5, 10, 100]:
            result = compute_next_review(comfort, interval)
            assert result >= 1, f"comfort={comfort}, interval={interval} -> {result}"


# ── compute_next_review: parametric coverage ─────────────────────────────


@pytest.mark.parametrize(
    "comfort,interval,expected",
    [
        (1, 1, 1),
        (1, 7, 1),
        (2, 1, 1),
        (2, 14, 1),
        (3, 1, 2),
        (3, 5, 5),
        (3, 10, 10),
        (4, 1, 2),
        (4, 7, 14),
        (4, 10, 20),
        (5, 1, 2),
        (5, 4, 10),
        (5, 10, 25),
    ],
    ids=[
        "c1_i1", "c1_i7", "c2_i1", "c2_i14",
        "c3_i1", "c3_i5", "c3_i10",
        "c4_i1", "c4_i7", "c4_i10",
        "c5_i1", "c5_i4", "c5_i10",
    ],
)
def test_parametric_combinations(comfort: int, interval: int, expected: int) -> None:
    """Parametric test covering multiple comfort/interval combinations."""
    assert compute_next_review(comfort, interval) == expected


# ── update_review_schedule: first attempt (last_attempted_at=None) ───────


def test_first_attempt_comfort_5() -> None:
    """First attempt with comfort 5 uses interval=1 -> 1*2.5 = 2 days."""
    now = datetime(2024, 1, 15, 12, 0, 0)
    result = update_review_schedule(None, now, 5)
    assert result == now + timedelta(days=2)


def test_first_attempt_comfort_1() -> None:
    """First attempt with comfort 1 returns next day."""
    now = datetime(2024, 6, 1, 10, 0)
    result = update_review_schedule(None, now, 1)
    assert result == now + timedelta(days=1)


def test_first_attempt_comfort_3() -> None:
    """First attempt with comfort 3: max(2, 1) = 2 days."""
    now = datetime(2024, 3, 10, 8, 0)
    result = update_review_schedule(None, now, 3)
    assert result == now + timedelta(days=2)


def test_first_attempt_comfort_4() -> None:
    """First attempt with comfort 4: 1*2 = 2 days."""
    now = datetime(2024, 3, 10, 8, 0)
    result = update_review_schedule(None, now, 4)
    assert result == now + timedelta(days=2)


def test_first_attempt_comfort_2() -> None:
    """First attempt with comfort 2 returns next day."""
    now = datetime(2024, 2, 20)
    result = update_review_schedule(None, now, 2)
    assert result == now + timedelta(days=1)


# ── update_review_schedule: subsequent attempts ─────────────────────────


def test_subsequent_attempt_2_days_gap() -> None:
    """Attempt after 2-day gap with comfort 5: int(2*2.5) = 5 days."""
    now = datetime(2024, 1, 17, 12, 0)
    last = datetime(2024, 1, 15, 12, 0)
    result = update_review_schedule(last, now, 5)
    assert result == now + timedelta(days=5)


def test_subsequent_attempt_same_day() -> None:
    """Same-day attempt: interval clamped to 1 day."""
    now = datetime(2024, 1, 15, 14, 0)
    last = datetime(2024, 1, 15, 10, 0)
    # (now - last).days == 0, clamped to 1
    result = update_review_schedule(last, now, 4)
    assert result == now + timedelta(days=2)  # 1*2 = 2


def test_subsequent_attempt_1_day_gap_comfort_3() -> None:
    """1-day gap with comfort 3: max(2, 1) = 2."""
    now = datetime(2024, 1, 16, 12, 0)
    last = datetime(2024, 1, 15, 12, 0)
    result = update_review_schedule(last, now, 3)
    assert result == now + timedelta(days=2)


def test_subsequent_attempt_7_day_gap_comfort_4() -> None:
    """7-day gap with comfort 4: 7*2 = 14 days."""
    now = datetime(2024, 1, 22, 12, 0)
    last = datetime(2024, 1, 15, 12, 0)
    result = update_review_schedule(last, now, 4)
    assert result == now + timedelta(days=14)


def test_subsequent_attempt_low_comfort_resets() -> None:
    """Low comfort after long gap still returns 1 day."""
    now = datetime(2024, 2, 15, 12, 0)
    last = datetime(2024, 1, 15, 12, 0)  # 31 days ago
    result = update_review_schedule(last, now, 1)
    assert result == now + timedelta(days=1)


# ── update_review_schedule: multi-review progression ─────────────────────


def test_repeated_high_comfort_grows() -> None:
    """Repeated high comfort grows intervals exponentially."""
    now = datetime(2024, 1, 15)
    # First attempt: interval=1, comfort=5 -> 2 days
    r1 = update_review_schedule(None, now, 5)
    assert r1 == now + timedelta(days=2)

    # Second attempt 2 days later: interval=2, comfort=5 -> 5 days
    now2 = now + timedelta(days=2)
    r2 = update_review_schedule(now, now2, 5)
    assert r2 == now2 + timedelta(days=5)

    # Third attempt 5 days later: interval=5, comfort=5 -> 12 days
    now3 = now2 + timedelta(days=5)
    r3 = update_review_schedule(now2, now3, 5)
    assert r3 == now3 + timedelta(days=12)


def test_comfort_regression_resets_schedule() -> None:
    """If comfort drops, schedule resets to short interval."""
    now = datetime(2024, 1, 15)
    # First: comfort 5 -> 2 days
    r1 = update_review_schedule(None, now, 5)
    assert r1 == now + timedelta(days=2)

    # Second: comfort 1 (regression) -> 1 day
    now2 = now + timedelta(days=2)
    r2 = update_review_schedule(now, now2, 1)
    assert r2 == now2 + timedelta(days=1)


def test_gradual_comfort_growth() -> None:
    """Comfort improving from 3 to 4 to 5 over multiple reviews."""
    now = datetime(2024, 1, 1)

    # Attempt 1: comfort 3, interval 1 -> max(2,1) = 2
    r1 = update_review_schedule(None, now, 3)
    assert r1 == now + timedelta(days=2)

    # Attempt 2: comfort 4, interval 2 -> 2*2 = 4
    now2 = now + timedelta(days=2)
    r2 = update_review_schedule(now, now2, 4)
    assert r2 == now2 + timedelta(days=4)

    # Attempt 3: comfort 5, interval 4 -> int(4*2.5) = 10
    now3 = now2 + timedelta(days=4)
    r3 = update_review_schedule(now2, now3, 5)
    assert r3 == now3 + timedelta(days=10)


# ── update_review_schedule: return type ──────────────────────────────────


def test_return_type_is_datetime() -> None:
    """update_review_schedule returns a datetime object."""
    now = datetime(2024, 1, 15)
    result = update_review_schedule(None, now, 3)
    assert isinstance(result, datetime)


def test_result_always_after_now() -> None:
    """Next review is always strictly after 'now'."""
    now = datetime(2024, 6, 15, 12, 0)
    for comfort in range(1, 6):
        result = update_review_schedule(None, now, comfort)
        assert result > now, f"comfort={comfort} did not return future date"


def test_result_always_after_now_subsequent() -> None:
    """Next review is always after 'now' for subsequent attempts."""
    now = datetime(2024, 6, 15, 12, 0)
    last = datetime(2024, 6, 10, 12, 0)
    for comfort in range(1, 6):
        result = update_review_schedule(last, now, comfort)
        assert result > now, f"comfort={comfort} did not return future date"


# ── compute_next_review: pure function properties ────────────────────────


def test_higher_comfort_longer_or_equal_interval() -> None:
    """Higher comfort should give longer or equal intervals."""
    for interval in [1, 3, 5, 10]:
        prev = 0
        for comfort in range(1, 6):
            result = compute_next_review(comfort, interval)
            assert result >= prev, (
                f"comfort={comfort}, interval={interval}: "
                f"{result} < {prev} (lower comfort gave longer interval)"
            )
            prev = result


def test_deterministic() -> None:
    """Same inputs always produce same outputs (pure function)."""
    for _ in range(10):
        assert compute_next_review(3, 5) == 5
        assert compute_next_review(5, 4) == 10


def test_update_schedule_deterministic() -> None:
    """update_review_schedule is deterministic."""
    now = datetime(2024, 1, 15, 12, 0)
    last = datetime(2024, 1, 10, 12, 0)
    r1 = update_review_schedule(last, now, 4)
    r2 = update_review_schedule(last, now, 4)
    assert r1 == r2
