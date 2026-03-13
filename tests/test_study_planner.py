"""Tests for study planner service."""
from datetime import datetime, timedelta

from src.backend.services.study_planner import compute_urgency


def test_urgency_higher_importance_higher_score():
    """Higher importance yields higher urgency."""
    u1 = compute_urgency(0.5, 50.0, None, 14)
    u2 = compute_urgency(1.0, 50.0, None, 14)
    assert u2 > u1


def test_urgency_lower_progress_higher_score():
    """Lower progress yields higher urgency."""
    u1 = compute_urgency(1.0, 80.0, None, 14)
    u2 = compute_urgency(1.0, 20.0, None, 14)
    assert u2 > u1


def test_urgency_closer_deadline_higher_score():
    """Closer deadline yields higher urgency."""
    u1 = compute_urgency(1.0, 50.0, None, 30)
    u2 = compute_urgency(1.0, 50.0, None, 5)
    assert u2 > u1


def test_urgency_recently_studied_lower():
    """Recently studied has lower urgency due to recency decay."""
    now = datetime.utcnow()
    recent = now - timedelta(days=1)
    old = now - timedelta(days=14)

    u_recent = compute_urgency(1.0, 50.0, recent, 14)
    u_old = compute_urgency(1.0, 50.0, old, 14)
    assert u_old > u_recent


def test_urgency_zero_progress():
    """Zero progress means full urgency from gap."""
    u = compute_urgency(1.0, 0.0, None, 14)
    assert u > 0


def test_urgency_full_progress():
    """Full progress means zero urgency."""
    u = compute_urgency(1.0, 100.0, None, 14)
    assert u == 0.0
