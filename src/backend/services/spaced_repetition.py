"""SM-2 spaced repetition algorithm for coding problems."""
from datetime import datetime, timedelta


def compute_next_review(comfort_level: int, previous_interval_days: int) -> int:
    """Return number of days until next review using SM-2 simplified.

    Args:
        comfort_level: Self-assessed comfort (1-5).
        previous_interval_days: Days since last review.

    Returns:
        Number of days until next review.
    """
    previous_interval_days = max(1, previous_interval_days)
    if comfort_level <= 2:
        return 1
    elif comfort_level == 3:
        return max(2, previous_interval_days)
    elif comfort_level == 4:
        return int(previous_interval_days * 2.0)
    else:  # comfort_level == 5
        return int(previous_interval_days * 2.5)


def update_review_schedule(
    last_attempted_at: datetime | None,
    now: datetime,
    comfort_after: int,
) -> datetime:
    """Compute next_review_at datetime based on attempt history.

    Args:
        last_attempted_at: When the problem was last attempted (None if first attempt).
        now: Current time.
        comfort_after: Comfort level after this attempt (1-5).

    Returns:
        Datetime for the next review.
    """
    previous_interval = 1 if last_attempted_at is None else max(1, (now - last_attempted_at).days)
    days = compute_next_review(comfort_after, previous_interval)
    return now + timedelta(days=days)
