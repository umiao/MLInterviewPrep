"""Tests for GET /api/export endpoint."""
from datetime import date

from src.backend.models.company import Company, CompanyTopicWeight
from src.backend.models.framework import StudyLog
from src.backend.models.problem import Attempt, Problem
from src.backend.models.scraper import InterviewQuestion, ScrapedPage


class TestExportEmpty:
    """Export returns empty lists when the database is empty."""

    def test_empty_db_returns_empty_lists(self, test_client):
        """All export sections should be empty lists on a fresh database."""
        resp = test_client.get("/api/export")
        assert resp.status_code == 200
        data = resp.json()

        assert data["problems"] == []
        assert data["framework_nodes"] == []
        assert data["companies"] == []
        assert data["interview_questions"] == []


class TestExportProblems:
    """Export includes full problem data with attempts."""

    def test_problem_fields(self, test_client, db_session):
        """All problem fields are exported."""
        p = Problem(
            leetcode_id=1,
            title="Two Sum",
            url="https://leetcode.com/problems/two-sum",
            difficulty="easy",
            tags='["array","hash_map"]',
            pattern="hash_map",
            category="algorithm",
            source="blind75",
            company_tags='["google","meta"]',
            priority=1,
            is_completed=True,
            comfort_level=4,
        )
        db_session.add(p)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        assert len(data["problems"]) == 1
        prob = data["problems"][0]
        assert prob["leetcode_id"] == 1
        assert prob["title"] == "Two Sum"
        assert prob["url"] == "https://leetcode.com/problems/two-sum"
        assert prob["difficulty"] == "easy"
        assert prob["tags"] == ["array", "hash_map"]
        assert prob["pattern"] == "hash_map"
        assert prob["category"] == "algorithm"
        assert prob["source"] == "blind75"
        assert prob["company_tags"] == ["google", "meta"]
        assert prob["priority"] == 1
        assert prob["is_completed"] is True
        assert prob["comfort_level"] == 4
        assert prob["created_at"] is not None

    def test_problem_with_attempts(self, test_client, db_session):
        """Problem export includes nested attempts with all fields."""
        p = Problem(title="3Sum", difficulty="medium", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()

        a = Attempt(
            problem_id=p.id,
            duration_seconds=1200,
            result="solved",
            approach_notes="Used two pointers after sorting",
            complexity_time="O(n^2)",
            complexity_space="O(1)",
            comfort_after=4,
        )
        db_session.add(a)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        attempts = data["problems"][0]["attempts"]
        assert len(attempts) == 1
        att = attempts[0]
        assert att["duration_seconds"] == 1200
        assert att["result"] == "solved"
        assert att["approach_notes"] == "Used two pointers after sorting"
        assert att["complexity_time"] == "O(n^2)"
        assert att["complexity_space"] == "O(1)"
        assert att["comfort_after"] == 4
        assert att["started_at"] is not None

    def test_multiple_problems_multiple_attempts(self, test_client, db_session):
        """Multiple problems each with multiple attempts."""
        for i in range(3):
            p = Problem(
                title=f"Problem {i}",
                difficulty="easy",
                tags="[]",
                company_tags="[]",
            )
            db_session.add(p)
            db_session.flush()
            for j in range(2):
                db_session.add(Attempt(
                    problem_id=p.id,
                    result="solved" if j == 1 else "failed",
                    comfort_after=j + 1,
                ))
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        assert len(data["problems"]) == 3
        for prob in data["problems"]:
            assert len(prob["attempts"]) == 2


class TestExportFramework:
    """Export includes full framework node data with study logs."""

    def test_framework_node_fields(self, test_client, db_session, seed_framework):
        """All framework node fields are exported."""
        resp = test_client.get("/api/export")
        data = resp.json()

        assert len(data["framework_nodes"]) == 2
        root = next(n for n in data["framework_nodes"] if n["depth"] == 0)
        child = next(n for n in data["framework_nodes"] if n["depth"] == 1)

        assert root["path"] == "pillar1"
        assert root["title"] == "Coding & Algorithms"
        assert root["importance"] == 1.0
        assert root["priority"] == "P0"
        assert root["estimated_hours"] == 40
        assert root["status"] == "not_started"
        assert root["progress_pct"] == 0.0
        assert root["confidence_level"] == 0
        assert root["parent_id"] is None
        assert root["description"] is None
        assert root["relevant_companies"] == []

        assert child["parent_id"] == root["id"]
        assert child["path"] == "pillar1.dp"
        assert child["title"] == "Dynamic Programming"

    def test_framework_with_study_logs(self, test_client, db_session, seed_framework):
        """Framework nodes include nested study logs."""
        node = seed_framework[1]  # child node
        sl = StudyLog(
            framework_node_id=node.id,
            date=date(2026, 3, 10),
            duration_minutes=45,
            activity_type="practice",
            notes="DP practice session",
        )
        db_session.add(sl)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        child = next(n for n in data["framework_nodes"] if n["path"] == "pillar1.dp")
        assert len(child["study_logs"]) == 1
        log = child["study_logs"][0]
        assert log["date"] == "2026-03-10"
        assert log["duration_minutes"] == 45
        assert log["activity_type"] == "practice"
        assert log["notes"] == "DP practice session"
        assert log["created_at"] is not None


class TestExportCompanies:
    """Export includes full company data with topic weights."""

    def test_company_fields(self, test_client, db_session):
        """All company fields are exported."""
        c = Company(
            name="Google",
            group_tag="FAANG",
            interview_stages='["phone","onsite"]',
            status="applied",
            applied_at=date(2026, 3, 1),
            notes="Applied via referral",
        )
        db_session.add(c)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        assert len(data["companies"]) == 1
        comp = data["companies"][0]
        assert comp["name"] == "Google"
        assert comp["group_tag"] == "FAANG"
        assert comp["interview_stages"] == ["phone", "onsite"]
        assert comp["status"] == "applied"
        assert comp["applied_at"] == "2026-03-01"
        assert comp["notes"] == "Applied via referral"

    def test_company_with_topic_weights(self, test_client, db_session, seed_framework):
        """Companies include nested topic weights."""
        c = Company(name="Meta", group_tag="FAANG")
        db_session.add(c)
        db_session.flush()

        node = seed_framework[0]
        tw = CompanyTopicWeight(
            company_id=c.id,
            framework_node_id=node.id,
            weight=4.5,
        )
        db_session.add(tw)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        comp = data["companies"][0]
        assert len(comp["topic_weights"]) == 1
        assert comp["topic_weights"][0]["framework_node_id"] == node.id
        assert comp["topic_weights"][0]["weight"] == 4.5


class TestExportQuestions:
    """Export includes full interview question data."""

    def test_question_fields(self, test_client, db_session):
        """All interview question fields are exported."""
        page = ScrapedPage(url="https://example.com", content_hash="abc123")
        db_session.add(page)
        db_session.flush()

        q = InterviewQuestion(
            scraped_page_id=page.id,
            company="Google",
            role="MLE",
            level="L5",
            interview_round="onsite",
            year=2026,
            question_text="Design a recommendation system",
            question_type="ml_system_design",
            tags='["ml","system_design"]',
            is_reviewed=True,
            notes="Common question",
            difficulty_estimate="hard",
        )
        db_session.add(q)
        db_session.commit()

        resp = test_client.get("/api/export")
        data = resp.json()

        assert len(data["interview_questions"]) == 1
        iq = data["interview_questions"][0]
        assert iq["company"] == "Google"
        assert iq["role"] == "MLE"
        assert iq["level"] == "L5"
        assert iq["interview_round"] == "onsite"
        assert iq["year"] == 2026
        assert iq["question_text"] == "Design a recommendation system"
        assert iq["question_type"] == "ml_system_design"
        assert iq["tags"] == ["ml", "system_design"]
        assert iq["is_reviewed"] is True
        assert iq["notes"] == "Common question"
        assert iq["difficulty_estimate"] == "hard"
        assert iq["created_at"] is not None


class TestExportIntegrated:
    """Full integrated export with all data types populated."""

    def test_full_export(self, test_client, db_session, seed_framework):
        """Export contains data from all four sections simultaneously."""
        # Problem with attempt
        p = Problem(
            leetcode_id=42,
            title="Trapping Rain Water",
            difficulty="hard",
            pattern="two_pointers",
            tags='["stack","two_pointers"]',
            company_tags='["google"]',
        )
        db_session.add(p)
        db_session.flush()
        db_session.add(Attempt(
            problem_id=p.id, result="solved", comfort_after=3,
        ))

        # Study log on framework node
        db_session.add(StudyLog(
            framework_node_id=seed_framework[0].id,
            date=date(2026, 3, 12),
            duration_minutes=60,
            activity_type="reading",
        ))

        # Company with weight
        c = Company(name="Apple", group_tag="FAANG", status="applied")
        db_session.add(c)
        db_session.flush()
        db_session.add(CompanyTopicWeight(
            company_id=c.id,
            framework_node_id=seed_framework[0].id,
            weight=3.0,
        ))

        # Interview question
        page = ScrapedPage(url="https://test.com", content_hash="xyz")
        db_session.add(page)
        db_session.flush()
        db_session.add(InterviewQuestion(
            scraped_page_id=page.id,
            company="Apple",
            question_text="Explain gradient descent",
            question_type="ml_theory",
        ))

        db_session.commit()

        resp = test_client.get("/api/export")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["problems"]) == 1
        assert len(data["problems"][0]["attempts"]) == 1
        assert len(data["framework_nodes"]) == 2
        # Find the root node and check its study logs
        root = next(n for n in data["framework_nodes"] if n["depth"] == 0)
        assert len(root["study_logs"]) == 1
        assert len(data["companies"]) == 1
        assert len(data["companies"][0]["topic_weights"]) == 1
        assert len(data["interview_questions"]) == 1

    def test_export_excludes_llm_review(self, test_client, db_session):
        """LLM review JSON is excluded from attempt export (potentially large)."""
        p = Problem(title="Test", difficulty="easy", tags="[]", company_tags="[]")
        db_session.add(p)
        db_session.flush()
        db_session.add(Attempt(
            problem_id=p.id,
            result="solved",
            comfort_after=3,
            llm_review='{"verdict":"optimal","feedback":"Good"}',
        ))
        db_session.commit()

        resp = test_client.get("/api/export")
        att = resp.json()["problems"][0]["attempts"][0]
        # llm_review is intentionally excluded from export (large, regenerable)
        assert "llm_review" not in att
