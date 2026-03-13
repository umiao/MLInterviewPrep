"""Tests for GET /api/dashboard endpoint."""
from datetime import date, datetime, timedelta

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode, StudyLog
from src.backend.models.problem import Attempt, Problem
from src.backend.models.scraper import InterviewQuestion


class TestDashboardEmpty:
    """Dashboard returns zeros when the database is empty."""

    def test_empty_db_returns_zeros(self, test_client):
        """All dashboard stats should be zero/empty on a fresh database."""
        resp = test_client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()

        assert data["problems"] == {
            "total": 0,
            "completed": 0,
            "due_for_review": 0,
        }
        assert data["framework"]["overall_progress_pct"] == 0.0
        assert data["framework"]["pillars"] == []
        assert data["recent_activity"] == {
            "attempts_7d": 0,
            "study_hours_7d": 0.0,
            "questions_added_7d": 0,
        }
        assert data["company_deadlines"] == []
        assert data["scraper"] == {"total_questions": 0}


class TestDashboardProblems:
    """Dashboard problem stats aggregation."""

    def test_problem_counts(self, test_client, db_session):
        """Total, completed, and due_for_review are counted correctly."""
        now = datetime.utcnow()
        # 3 problems: 1 completed, 1 due for review, 1 neither
        db_session.add(Problem(
            title="P1", difficulty="easy", is_completed=True,
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="P2", difficulty="medium",
            next_review_at=now - timedelta(hours=1),
            tags="[]", company_tags="[]",
        ))
        db_session.add(Problem(
            title="P3", difficulty="hard",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        data = resp.json()

        assert data["problems"]["total"] == 3
        assert data["problems"]["completed"] == 1
        assert data["problems"]["due_for_review"] == 1

    def test_future_review_not_counted(self, test_client, db_session):
        """Problems with next_review_at in the future are NOT due."""
        db_session.add(Problem(
            title="Future", difficulty="easy",
            next_review_at=datetime.utcnow() + timedelta(days=3),
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        assert resp.json()["problems"]["due_for_review"] == 0


class TestDashboardFramework:
    """Dashboard framework progress aggregation."""

    def test_overall_progress_weighted(self, test_client, db_session):
        """Overall progress is weighted by importance."""
        # Node A: importance=2, progress=80 -> contributes 160
        # Node B: importance=3, progress=40 -> contributes 120
        # Expected: (160+120) / (2+3) = 56.0
        db_session.add(FrameworkNode(
            path="a", depth=0, title="A", importance=2.0, progress_pct=80.0,
        ))
        db_session.add(FrameworkNode(
            path="b", depth=0, title="B", importance=3.0, progress_pct=40.0,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        data = resp.json()

        assert data["framework"]["overall_progress_pct"] == 56.0

    def test_pillars_are_depth_zero(self, test_client, db_session):
        """Pillars section only includes depth=0 nodes."""
        root = FrameworkNode(
            path="root", depth=0, title="Root Pillar",
            importance=1.0, progress_pct=50.0,
        )
        db_session.add(root)
        db_session.flush()
        db_session.add(FrameworkNode(
            parent_id=root.id, path="root.child", depth=1,
            title="Child Node", importance=0.5, progress_pct=20.0,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        pillars = resp.json()["framework"]["pillars"]

        assert len(pillars) == 1
        assert pillars[0]["title"] == "Root Pillar"
        assert pillars[0]["progress"] == 50.0

    def test_zero_importance_excluded_from_overall(self, test_client, db_session):
        """Nodes with importance=0 don't affect overall_progress_pct."""
        db_session.add(FrameworkNode(
            path="a", depth=0, title="A", importance=1.0, progress_pct=60.0,
        ))
        db_session.add(FrameworkNode(
            path="b", depth=0, title="B", importance=0.0, progress_pct=100.0,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        # Only node A counts: 60*1 / 1 = 60.0
        assert resp.json()["framework"]["overall_progress_pct"] == 60.0


class TestDashboardRecentActivity:
    """Dashboard recent activity (7-day window)."""

    def test_attempts_7d(self, test_client, db_session):
        """Only attempts within the last 7 days are counted."""
        now = datetime.utcnow()
        p = Problem(title="P", difficulty="easy", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()

        # Recent attempt (within 7 days)
        db_session.add(Attempt(
            problem_id=p.id, started_at=now - timedelta(days=2),
            comfort_after=3,
        ))
        # Old attempt (>7 days ago)
        db_session.add(Attempt(
            problem_id=p.id, started_at=now - timedelta(days=10),
            comfort_after=2,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        assert resp.json()["recent_activity"]["attempts_7d"] == 1

    def test_study_hours_7d(self, test_client, db_session):
        """Study hours aggregated from study logs within 7 days."""
        now = datetime.utcnow()
        node = FrameworkNode(
            path="n", depth=0, title="N", importance=1.0,
        )
        db_session.add(node)
        db_session.flush()

        # 90 minutes recent
        db_session.add(StudyLog(
            framework_node_id=node.id, date=date.today(),
            duration_minutes=90,
        ))
        # 30 minutes recent
        db_session.add(StudyLog(
            framework_node_id=node.id,
            date=(now - timedelta(days=3)).date(),
            duration_minutes=30,
        ))
        # 60 minutes old (>7 days)
        db_session.add(StudyLog(
            framework_node_id=node.id,
            date=(now - timedelta(days=10)).date(),
            duration_minutes=60,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        # (90 + 30) / 60 = 2.0 hours
        assert resp.json()["recent_activity"]["study_hours_7d"] == 2.0

    def test_questions_added_7d(self, test_client, db_session):
        """Only interview questions created within 7 days counted."""
        now = datetime.utcnow()
        db_session.add(InterviewQuestion(
            question_text="Recent Q",
            created_at=now - timedelta(days=1),
        ))
        db_session.add(InterviewQuestion(
            question_text="Old Q",
            created_at=now - timedelta(days=14),
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        assert resp.json()["recent_activity"]["questions_added_7d"] == 1


class TestDashboardCompanyDeadlines:
    """Dashboard company deadlines section."""

    def test_companies_with_applied_at(self, test_client, db_session):
        """Only companies with applied_at set are shown."""
        db_session.add(Company(
            name="Google", status="applied",
            applied_at=date.today(),
        ))
        db_session.add(Company(
            name="NoDate", status="applied",
            applied_at=None,
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        deadlines = resp.json()["company_deadlines"]

        assert len(deadlines) == 1
        assert deadlines[0]["name"] == "Google"
        assert deadlines[0]["status"] == "applied"

    def test_multiple_companies(self, test_client, db_session):
        """Multiple companies with deadlines all appear."""
        for name in ("Meta", "Apple"):
            db_session.add(Company(
                name=name, status="phone_screen",
                applied_at=date.today(),
            ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        deadlines = resp.json()["company_deadlines"]

        assert len(deadlines) == 2
        names = {d["name"] for d in deadlines}
        assert names == {"Meta", "Apple"}


class TestDashboardScraper:
    """Dashboard scraper stats."""

    def test_total_questions(self, test_client, db_session):
        """Total questions count includes all interview questions."""
        for i in range(3):
            db_session.add(InterviewQuestion(
                question_text=f"Q{i}",
            ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        assert resp.json()["scraper"]["total_questions"] == 3


class TestDashboardIntegrated:
    """Full dashboard with data across all modules."""

    def test_full_dashboard(self, test_client, db_session):
        """Verify all sections populated correctly in one request."""
        now = datetime.utcnow()

        # Problems
        p = Problem(
            title="Two Sum", difficulty="easy", is_completed=True,
            next_review_at=now - timedelta(hours=1),
            tags="[]", company_tags="[]",
        )
        db_session.add(p)
        db_session.flush()

        db_session.add(Attempt(
            problem_id=p.id, started_at=now - timedelta(days=1),
            comfort_after=4,
        ))

        # Framework
        node = FrameworkNode(
            path="ml", depth=0, title="ML Fundamentals",
            importance=2.0, progress_pct=75.0,
        )
        db_session.add(node)
        db_session.flush()

        db_session.add(StudyLog(
            framework_node_id=node.id, date=date.today(),
            duration_minutes=120,
        ))

        # Company
        db_session.add(Company(
            name="Google", status="onsite",
            applied_at=date.today(),
        ))

        # Questions
        db_session.add(InterviewQuestion(
            question_text="Design a recommendation system",
            company="Google",
            created_at=now - timedelta(days=2),
        ))
        db_session.commit()

        resp = test_client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()

        assert data["problems"]["total"] == 1
        assert data["problems"]["completed"] == 1
        assert data["problems"]["due_for_review"] == 1
        assert data["framework"]["overall_progress_pct"] == 75.0
        assert len(data["framework"]["pillars"]) == 1
        assert data["recent_activity"]["attempts_7d"] == 1
        assert data["recent_activity"]["study_hours_7d"] == 2.0
        assert data["recent_activity"]["questions_added_7d"] == 1
        assert len(data["company_deadlines"]) == 1
        assert data["scraper"]["total_questions"] == 1
