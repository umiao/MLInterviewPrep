"""Comprehensive tests for GET /api/problems/review-queue endpoint."""
from datetime import datetime, timedelta

from src.backend.models.problem import Problem


def _create_problem(db_session, title, next_review_at=None, **kwargs):
    """Helper to create a problem with optional next_review_at."""
    p = Problem(
        title=title,
        difficulty="medium",
        tags='["test"]',
        company_tags='[]',
        next_review_at=next_review_at,
        **kwargs,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


# ---------------------------------------------------------------------------
# Basic behavior
# ---------------------------------------------------------------------------

def test_review_queue_empty_db(test_client):
    """Empty DB returns empty list."""
    resp = test_client.get("/api/problems/review-queue")
    assert resp.status_code == 200
    assert resp.json() == []


def test_review_queue_returns_due_problems(test_client, db_session):
    """Problems with next_review_at in the past appear in the queue."""
    past = datetime.utcnow() - timedelta(hours=1)
    _create_problem(db_session, "Due Problem", next_review_at=past)

    resp = test_client.get("/api/problems/review-queue")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Due Problem"


def test_review_queue_excludes_null_next_review(test_client, db_session):
    """Problems with next_review_at=None are excluded."""
    _create_problem(db_session, "No Review Date", next_review_at=None)
    past = datetime.utcnow() - timedelta(hours=1)
    _create_problem(db_session, "Due", next_review_at=past)

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Due"


def test_review_queue_excludes_future_review(test_client, db_session):
    """Problems with next_review_at in the future are excluded."""
    future = datetime.utcnow() + timedelta(days=7)
    _create_problem(db_session, "Future Review", next_review_at=future)

    resp = test_client.get("/api/problems/review-queue")
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Ordering (most overdue first = ASC on next_review_at)
# ---------------------------------------------------------------------------

def test_review_queue_ordered_most_overdue_first(test_client, db_session):
    """Results are ordered ASC by next_review_at (most overdue first)."""
    now = datetime.utcnow()
    t1 = now - timedelta(hours=1)   # less overdue
    t2 = now - timedelta(days=3)    # most overdue
    t3 = now - timedelta(hours=12)  # middle

    _create_problem(db_session, "1h ago", next_review_at=t1)
    _create_problem(db_session, "3d ago", next_review_at=t2)
    _create_problem(db_session, "12h ago", next_review_at=t3)

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 3
    assert data[0]["title"] == "3d ago"
    assert data[1]["title"] == "12h ago"
    assert data[2]["title"] == "1h ago"


# ---------------------------------------------------------------------------
# Limit parameter
# ---------------------------------------------------------------------------

def test_review_queue_default_limit(test_client, db_session):
    """Default limit is 20."""
    now = datetime.utcnow()
    for i in range(25):
        _create_problem(
            db_session,
            f"Problem {i}",
            next_review_at=now - timedelta(hours=i + 1),
        )

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 20


def test_review_queue_custom_limit(test_client, db_session):
    """Custom limit parameter works."""
    now = datetime.utcnow()
    for i in range(10):
        _create_problem(
            db_session,
            f"Problem {i}",
            next_review_at=now - timedelta(hours=i + 1),
        )

    resp = test_client.get("/api/problems/review-queue?limit=3")
    data = resp.json()
    assert len(data) == 3


def test_review_queue_limit_validation_min(test_client):
    """Limit < 1 returns 422."""
    resp = test_client.get("/api/problems/review-queue?limit=0")
    assert resp.status_code == 422


def test_review_queue_limit_validation_max(test_client):
    """Limit > 100 returns 422."""
    resp = test_client.get("/api/problems/review-queue?limit=101")
    assert resp.status_code == 422


def test_review_queue_limit_100(test_client, db_session):
    """Limit=100 is accepted (max allowed)."""
    resp = test_client.get("/api/problems/review-queue?limit=100")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------

def test_review_queue_response_fields(test_client, db_session):
    """Each item in the queue has expected ProblemResponse fields."""
    past = datetime.utcnow() - timedelta(hours=1)
    _create_problem(
        db_session,
        "Field Check",
        next_review_at=past,
        leetcode_id=42,
        pattern="two_pointers",
        comfort_level=3,
    )

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert "id" in item
    assert item["title"] == "Field Check"
    assert item["leetcode_id"] == 42
    assert item["pattern"] == "two_pointers"
    assert item["comfort_level"] == 3
    assert item["next_review_at"] is not None
    assert "tags" in item
    assert "company_tags" in item


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_review_queue_exactly_now(test_client, db_session):
    """Problem with next_review_at = now should appear (<=, not <)."""
    # Use a time slightly in the past to avoid race conditions
    almost_now = datetime.utcnow() - timedelta(seconds=1)
    _create_problem(db_session, "Just Due", next_review_at=almost_now)

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Just Due"


def test_review_queue_mix_of_due_future_null(test_client, db_session):
    """Only due problems returned from a mix of due, future, and null."""
    now = datetime.utcnow()
    _create_problem(db_session, "Due 1", next_review_at=now - timedelta(hours=2))
    _create_problem(db_session, "Due 2", next_review_at=now - timedelta(hours=5))
    _create_problem(db_session, "Future", next_review_at=now + timedelta(days=3))
    _create_problem(db_session, "No Date", next_review_at=None)

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 2
    titles = [d["title"] for d in data]
    assert "Due 1" in titles
    assert "Due 2" in titles
    assert "Future" not in titles
    assert "No Date" not in titles


def test_review_queue_completed_problems_still_shown(test_client, db_session):
    """Completed problems that are due for review still appear in queue."""
    past = datetime.utcnow() - timedelta(hours=1)
    _create_problem(
        db_session,
        "Completed But Due",
        next_review_at=past,
        is_completed=True,
        comfort_level=4,
    )

    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["is_completed"] is True


def test_review_queue_limit_respects_ordering(test_client, db_session):
    """With limit, the most overdue problems are returned first."""
    now = datetime.utcnow()
    _create_problem(db_session, "Slightly Overdue", next_review_at=now - timedelta(hours=1))
    _create_problem(db_session, "Very Overdue", next_review_at=now - timedelta(days=10))
    _create_problem(db_session, "Medium Overdue", next_review_at=now - timedelta(days=2))

    resp = test_client.get("/api/problems/review-queue?limit=2")
    data = resp.json()
    assert len(data) == 2
    assert data[0]["title"] == "Very Overdue"
    assert data[1]["title"] == "Medium Overdue"


# ---------------------------------------------------------------------------
# Integration with attempt creation (SM-2 wiring)
# ---------------------------------------------------------------------------

def test_review_queue_after_attempt_low_comfort(test_client):
    """After attempt with low comfort, problem appears in review queue soon."""
    # Create problem
    resp = test_client.post("/api/problems", json={
        "title": "Review Test", "difficulty": "medium",
    })
    assert resp.status_code == 201
    pid = resp.json()["id"]

    # Create attempt with low comfort -> next_review_at = 1 day from now
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1, "duration_seconds": 60,
    })
    assert resp.status_code == 201

    # Not due yet (review is ~1 day away)
    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    due_ids = [d["id"] for d in data]
    assert pid not in due_ids

    # Check the problem has next_review_at set
    resp = test_client.get("/api/problems?limit=200")
    problem = [p for p in resp.json() if p["id"] == pid][0]
    assert problem["next_review_at"] is not None


def test_review_queue_after_attempt_high_comfort(test_client):
    """After attempt with high comfort, review is further in the future."""
    resp = test_client.post("/api/problems", json={
        "title": "Easy One", "difficulty": "easy",
    })
    pid = resp.json()["id"]

    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5, "duration_seconds": 120,
    })
    assert resp.status_code == 201

    # Should not be in review queue (review is many days away)
    resp = test_client.get("/api/problems/review-queue")
    data = resp.json()
    due_ids = [d["id"] for d in data]
    assert pid not in due_ids
