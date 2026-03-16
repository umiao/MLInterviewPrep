"""Tests for split dashboard endpoints: /today, /activity, /summary."""
from datetime import date, datetime, timedelta

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode, StudyLog
from src.backend.models.problem import Attempt, Problem
from src.backend.models.scraper import InterviewQuestion

# ── /api/dashboard/today ──────────────────────────────────────────────


class TestDashboardToday:
    """Tests for GET /api/dashboard/today."""

    def test_empty_db(self, test_client):
        """Empty DB returns zero due reviews, no focus topic, zero streak."""
        resp = test_client.get("/api/dashboard/today")
        assert resp.status_code == 200
        data = resp.json()
        assert data["due_reviews"] == 0
        assert data["suggested_focus_topic"] is None
        assert data["streak_days"] == 0

    def test_due_reviews_count(self, test_client, db_session):
        """Count problems whose next_review_at is in the past."""
        now = datetime.utcnow()
        db_session.add(Problem(
            title="Due", difficulty="easy",
            next_review_at=now - timedelta(hours=1),
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="Future", difficulty="easy",
            next_review_at=now + timedelta(days=3),
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="NoReview", difficulty="easy",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/today").json()
        assert data["due_reviews"] == 1

    def test_suggested_focus_topic(self, test_client, db_session):
        """Weakest non-mastered node with highest importance is suggested."""
        db_session.add(FrameworkNode(
            path="a", depth=0, title="Strong Topic",
            importance=2.0, progress_pct=90.0, status="in_progress",
        ))
        db_session.add(FrameworkNode(
            path="b", depth=0, title="Weak Topic",
            importance=3.0, progress_pct=10.0, status="not_started",
        ))
        db_session.add(FrameworkNode(
            path="c", depth=0, title="Mastered Topic",
            importance=5.0, progress_pct=100.0, status="mastered",
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/today").json()
        topic = data["suggested_focus_topic"]
        assert topic is not None
        assert topic["title"] == "Weak Topic"
        assert topic["progress_pct"] == 10.0

    def test_streak_days_with_attempts(self, test_client, db_session):
        """Streak counts consecutive days with attempts."""
        today = date.today()
        p = Problem(title="P", difficulty="easy", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()

        # Today and yesterday have attempts -> streak = 2
        db_session.add(Attempt(
            problem_id=p.id,
            started_at=datetime(today.year, today.month, today.day, 10, 0),
            comfort_after=3,
        ))
        db_session.add(Attempt(
            problem_id=p.id,
            started_at=datetime(today.year, today.month, today.day, 10, 0)
            - timedelta(days=1),
            comfort_after=3,
        ))
        # Gap: day before yesterday has no activity
        # 3 days ago has attempt but gap breaks streak
        db_session.add(Attempt(
            problem_id=p.id,
            started_at=datetime(today.year, today.month, today.day, 10, 0)
            - timedelta(days=3),
            comfort_after=3,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/today").json()
        assert data["streak_days"] == 2

    def test_streak_days_with_study_logs(self, test_client, db_session):
        """Study logs also count toward streak."""
        today = date.today()
        node = FrameworkNode(path="n", depth=0, title="N", importance=1.0)
        db_session.add(node)
        db_session.flush()

        db_session.add(StudyLog(
            framework_node_id=node.id, date=today, duration_minutes=30,
        ))
        db_session.add(StudyLog(
            framework_node_id=node.id,
            date=today - timedelta(days=1), duration_minutes=20,
        ))
        db_session.add(StudyLog(
            framework_node_id=node.id,
            date=today - timedelta(days=2), duration_minutes=15,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/today").json()
        assert data["streak_days"] == 3

    def test_streak_zero_when_no_activity_today(self, test_client, db_session):
        """If no activity today, streak is 0 even if yesterday had activity."""
        today = date.today()
        p = Problem(title="P", difficulty="easy", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()

        db_session.add(Attempt(
            problem_id=p.id,
            started_at=datetime(today.year, today.month, today.day, 10, 0)
            - timedelta(days=1),
            comfort_after=3,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/today").json()
        assert data["streak_days"] == 0


# ── /api/dashboard/activity ───────────────────────────────────────────


class TestDashboardActivity:
    """Tests for GET /api/dashboard/activity."""

    def test_empty_db_returns_30_days(self, test_client):
        """Empty DB returns 30 entries, all zeros."""
        resp = test_client.get("/api/dashboard/activity")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 30
        for entry in data:
            assert entry["attempts"] == 0
            assert entry["study_minutes"] == 0
            assert entry["questions_added"] == 0

    def test_activity_entries_have_correct_dates(self, test_client):
        """Entries span from 29 days ago to today."""
        data = test_client.get("/api/dashboard/activity").json()
        today = date.today()
        start = today - timedelta(days=29)
        assert data[0]["date"] == str(start)
        assert data[-1]["date"] == str(today)

    def test_attempts_counted_per_day(self, test_client, db_session):
        """Attempts are bucketed by date."""
        today = date.today()
        p = Problem(title="P", difficulty="easy", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()

        # 2 attempts today
        for _ in range(2):
            db_session.add(Attempt(
                problem_id=p.id,
                started_at=datetime(today.year, today.month, today.day, 14, 0),
                comfort_after=3,
            ))
        # 1 attempt yesterday
        yesterday = today - timedelta(days=1)
        db_session.add(Attempt(
            problem_id=p.id,
            started_at=datetime(yesterday.year, yesterday.month, yesterday.day, 10, 0),
            comfort_after=3,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/activity").json()
        today_entry = next(e for e in data if e["date"] == str(today))
        yesterday_entry = next(e for e in data if e["date"] == str(yesterday))
        assert today_entry["attempts"] == 2
        assert yesterday_entry["attempts"] == 1

    def test_study_minutes_summed_per_day(self, test_client, db_session):
        """Study minutes are summed per day."""
        today = date.today()
        node = FrameworkNode(path="n", depth=0, title="N", importance=1.0)
        db_session.add(node)
        db_session.flush()

        db_session.add(StudyLog(
            framework_node_id=node.id, date=today, duration_minutes=45,
        ))
        db_session.add(StudyLog(
            framework_node_id=node.id, date=today, duration_minutes=30,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/activity").json()
        today_entry = next(e for e in data if e["date"] == str(today))
        assert today_entry["study_minutes"] == 75

    def test_questions_counted_per_day(self, test_client, db_session):
        """Questions added counted per day."""
        today = date.today()
        db_session.add(InterviewQuestion(
            question_text="Q1",
            created_at=datetime(today.year, today.month, today.day, 12, 0),
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/activity").json()
        today_entry = next(e for e in data if e["date"] == str(today))
        assert today_entry["questions_added"] == 1

    def test_old_data_excluded(self, test_client, db_session):
        """Data older than 30 days is not included."""
        old_date = date.today() - timedelta(days=35)
        node = FrameworkNode(path="n", depth=0, title="N", importance=1.0)
        db_session.add(node)
        db_session.flush()

        db_session.add(StudyLog(
            framework_node_id=node.id, date=old_date, duration_minutes=60,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/activity").json()
        # All entries should have 0 study_minutes since old data excluded
        total_mins = sum(e["study_minutes"] for e in data)
        assert total_mins == 0


# ── /api/dashboard/summary ────────────────────────────────────────────


class TestDashboardSummary:
    """Tests for GET /api/dashboard/summary."""

    def test_empty_db(self, test_client):
        """Empty DB returns zeros."""
        resp = test_client.get("/api/dashboard/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["problems"] == {"total": 0, "completed": 0}
        assert data["framework_overall_progress_pct"] == 0.0
        assert data["company_counts_by_status"] == {}

    def test_problem_counts(self, test_client, db_session):
        """Total and completed problem counts."""
        db_session.add(Problem(
            title="P1", difficulty="easy", is_completed=True,
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="P2", difficulty="medium", is_completed=False,
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="P3", difficulty="hard", is_completed=True,
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/summary").json()
        assert data["problems"]["total"] == 3
        assert data["problems"]["completed"] == 2

    def test_framework_progress(self, test_client, db_session):
        """Overall progress is weighted by importance."""
        db_session.add(FrameworkNode(
            path="a", depth=0, title="A", importance=2.0, progress_pct=80.0,
        ))
        db_session.add(FrameworkNode(
            path="b", depth=0, title="B", importance=3.0, progress_pct=40.0,
        ))
        db_session.commit()

        data = test_client.get("/api/dashboard/summary").json()
        # (2*80 + 3*40) / (2+3) = 280/5 = 56.0
        assert data["framework_overall_progress_pct"] == 56.0

    def test_company_counts_by_status(self, test_client, db_session):
        """Companies grouped by status."""
        db_session.add(Company(name="G1", status="applied"))
        db_session.add(Company(name="G2", status="applied"))
        db_session.add(Company(name="M1", status="onsite"))
        db_session.add(Company(name="R1", status="rejected"))
        db_session.commit()

        data = test_client.get("/api/dashboard/summary").json()
        counts = data["company_counts_by_status"]
        assert counts["applied"] == 2
        assert counts["onsite"] == 1
        assert counts["rejected"] == 1


# ── Backward compat: /api/dashboard still works ───────────────────────


class TestDashboardBackwardCompat:
    """Existing /api/dashboard endpoint still works."""

    def test_original_endpoint_still_works(self, test_client):
        """GET /api/dashboard returns the original aggregated response."""
        resp = test_client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        # Original keys should still be present
        assert "problems" in data
        assert "framework" in data
        assert "recent_activity" in data
        assert "company_deadlines" in data
        assert "scraper" in data
