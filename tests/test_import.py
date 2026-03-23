"""Tests for POST /api/import and POST /api/import/csv endpoints."""
import csv
import io
from datetime import date

from src.backend.models.company import Company
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.models.scraper import InterviewQuestion


class TestImportEmpty:
    """Import with empty or partial payloads."""

    def test_empty_payload(self, test_client):
        """Empty JSON body imports nothing."""
        resp = test_client.post("/api/import", json={})
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_empty_sections(self, test_client):
        """Empty lists in each section result in zero counts."""
        resp = test_client.post("/api/import", json={
            "problems": [],
            "framework_nodes": [],
            "companies": [],
            "interview_questions": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        for section in ("problems", "framework_nodes", "companies", "interview_questions"):
            assert data[section]["inserted"] == 0
            assert data[section]["skipped"] == 0


class TestImportProblems:
    """Import problems with merge (skip by leetcode_id or title)."""

    def test_insert_new_problem(self, test_client, db_session):
        """A new problem is inserted successfully."""
        payload = {
            "problems": [
                {
                    "leetcode_id": 1,
                    "title": "Two Sum",
                    "difficulty": "easy",
                    "tags": ["array", "hash_map"],
                    "pattern": "hash_map",
                    "category": "algorithm",
                    "source": "blind75",
                    "company_tags": ["google"],
                    "priority": 1,
                }
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.status_code == 200
        assert resp.json()["problems"]["inserted"] == 1
        assert resp.json()["problems"]["skipped"] == 0

        # Verify in DB
        p = db_session.query(Problem).filter(Problem.leetcode_id == 1).first()
        assert p is not None
        assert p.title == "Two Sum"
        assert p.tags_list == ["array", "hash_map"]

    def test_skip_duplicate_by_leetcode_id(self, test_client, db_session):
        """Problem with existing leetcode_id is skipped."""
        db_session.add(Problem(
            leetcode_id=42, title="Existing", difficulty="easy",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        resp = test_client.post("/api/import", json={
            "problems": [{"leetcode_id": 42, "title": "Different Title"}]
        })
        assert resp.json()["problems"]["skipped"] == 1
        assert resp.json()["problems"]["inserted"] == 0

    def test_skip_duplicate_by_title(self, test_client, db_session):
        """Problem with existing title (no leetcode_id) is skipped."""
        db_session.add(Problem(
            title="Merge Sort", difficulty="medium",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        resp = test_client.post("/api/import", json={
            "problems": [{"title": "Merge Sort", "difficulty": "hard"}]
        })
        assert resp.json()["problems"]["skipped"] == 1

    def test_import_with_attempts(self, test_client, db_session):
        """Problem import includes nested attempts."""
        payload = {
            "problems": [
                {
                    "title": "3Sum",
                    "difficulty": "medium",
                    "tags": [],
                    "company_tags": [],
                    "attempts": [
                        {
                            "duration_seconds": 1200,
                            "result": "solved",
                            "approach_notes": "Two pointers",
                            "complexity_time": "O(n^2)",
                            "complexity_space": "O(1)",
                            "comfort_after": 4,
                        },
                        {
                            "duration_seconds": 600,
                            "result": "solved",
                            "comfort_after": 5,
                        },
                    ],
                }
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.json()["problems"]["inserted"] == 1

        p = db_session.query(Problem).filter(Problem.title == "3Sum").first()
        assert p is not None
        assert len(p.attempts) == 2
        assert p.attempts[0].approach_notes == "Two pointers"

    def test_mixed_insert_and_skip(self, test_client, db_session):
        """Batch with both new and existing problems."""
        db_session.add(Problem(
            leetcode_id=1, title="Two Sum", difficulty="easy",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        resp = test_client.post("/api/import", json={
            "problems": [
                {"leetcode_id": 1, "title": "Two Sum"},
                {"leetcode_id": 15, "title": "3Sum", "difficulty": "medium"},
            ]
        })
        data = resp.json()["problems"]
        assert data["inserted"] == 1
        assert data["skipped"] == 1


class TestImportFrameworkNodes:
    """Import framework nodes with merge (skip by path)."""

    def test_insert_new_nodes(self, test_client, db_session):
        """New framework nodes are inserted with parent resolution."""
        payload = {
            "framework_nodes": [
                {
                    "path": "coding",
                    "depth": 0,
                    "title": "Coding",
                    "importance": 1.0,
                    "priority": "P0",
                    "estimated_hours": 40,
                },
                {
                    "path": "coding.dp",
                    "depth": 1,
                    "title": "Dynamic Programming",
                    "importance": 0.9,
                },
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        data = resp.json()["framework_nodes"]
        assert data["inserted"] == 2
        assert data["skipped"] == 0

        child = db_session.query(FrameworkNode).filter(
            FrameworkNode.path == "coding.dp"
        ).first()
        assert child is not None
        assert child.parent_id is not None
        parent = db_session.get(FrameworkNode, child.parent_id)
        assert parent.path == "coding"

    def test_skip_existing_path(self, test_client, db_session, seed_framework):
        """Node with existing path is skipped."""
        resp = test_client.post("/api/import", json={
            "framework_nodes": [
                {"path": "pillar1", "depth": 0, "title": "Coding & Algorithms"},
            ]
        })
        assert resp.json()["framework_nodes"]["skipped"] == 1

    def test_import_with_study_logs(self, test_client, db_session):
        """Framework node import includes nested study logs."""
        payload = {
            "framework_nodes": [
                {
                    "path": "ml",
                    "depth": 0,
                    "title": "Machine Learning",
                    "study_logs": [
                        {
                            "date": "2026-03-10",
                            "duration_minutes": 60,
                            "activity_type": "reading",
                            "notes": "Read chapter 1",
                        }
                    ],
                }
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.json()["framework_nodes"]["inserted"] == 1

        node = db_session.query(FrameworkNode).filter(
            FrameworkNode.path == "ml"
        ).first()
        assert len(node.study_logs) == 1
        assert node.study_logs[0].duration_minutes == 60


class TestImportCompanies:
    """Import companies with merge (skip by name)."""

    def test_insert_new_company(self, test_client, db_session):
        """New company is inserted."""
        payload = {
            "companies": [
                {
                    "name": "Google",
                    "group_tag": "FAANG",
                    "interview_stages": ["phone", "onsite"],
                    "status": "applied",
                    "applied_at": "2026-03-01",
                    "notes": "Via referral",
                }
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.json()["companies"]["inserted"] == 1

        c = db_session.query(Company).filter(Company.name == "Google").first()
        assert c is not None
        assert c.group_tag == "FAANG"
        assert c.applied_at == date(2026, 3, 1)

    def test_skip_existing_company(self, test_client, db_session):
        """Company with existing name is skipped."""
        db_session.add(Company(name="Meta", group_tag="FAANG"))
        db_session.commit()

        resp = test_client.post("/api/import", json={
            "companies": [{"name": "Meta", "group_tag": "Big Tech"}]
        })
        assert resp.json()["companies"]["skipped"] == 1

    def test_company_with_topic_weights(self, test_client, db_session, seed_framework):
        """Company import includes nested topic weights."""
        node_id = seed_framework[0].id
        payload = {
            "companies": [
                {
                    "name": "Apple",
                    "topic_weights": [
                        {"framework_node_id": node_id, "weight": 3.5},
                    ],
                }
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        assert resp.json()["companies"]["inserted"] == 1

        c = db_session.query(Company).filter(Company.name == "Apple").first()
        assert len(c.topic_weights) == 1
        assert c.topic_weights[0].weight == 3.5


class TestImportQuestions:
    """Import interview questions (no dedup, always insert)."""

    def test_insert_questions(self, test_client, db_session):
        """Questions are always inserted (no dedup)."""
        payload = {
            "interview_questions": [
                {
                    "company": "Google",
                    "role": "MLE",
                    "question_text": "Explain backprop",
                    "question_type": "ml_theory",
                    "tags": ["ml", "basics"],
                },
                {
                    "company": "Meta",
                    "question_text": "Design a feed ranking system",
                    "question_type": "ml_system_design",
                },
            ]
        }
        resp = test_client.post("/api/import", json=payload)
        data = resp.json()["interview_questions"]
        assert data["inserted"] == 2
        assert data["skipped"] == 0

        qs = db_session.query(InterviewQuestion).all()
        assert len(qs) == 2


class TestImportRoundTrip:
    """Export then re-import produces the same data (idempotent merge)."""

    def test_export_import_roundtrip(self, test_client, db_session, seed_framework):
        """Exported data can be re-imported; duplicates are skipped."""
        # Create some data
        p = Problem(
            leetcode_id=100, title="Test Problem", difficulty="easy",
            tags='["test"]', company_tags='["acme"]',
        )
        db_session.add(p)
        db_session.flush()

        c = Company(name="TestCo", group_tag="startup")
        db_session.add(c)
        db_session.commit()

        # Export
        export_resp = test_client.get("/api/export")
        assert export_resp.status_code == 200
        export_data = export_resp.json()

        # Re-import the same data -- everything should be skipped
        import_resp = test_client.post("/api/import", json=export_data)
        assert import_resp.status_code == 200
        result = import_resp.json()

        assert result["problems"]["skipped"] >= 1
        assert result["problems"]["inserted"] == 0
        assert result["framework_nodes"]["skipped"] >= 1
        assert result["framework_nodes"]["inserted"] == 0
        assert result["companies"]["skipped"] >= 1
        assert result["companies"]["inserted"] == 0


class TestImportCSV:
    """Import problems from CSV file."""

    def _make_csv(self, rows: list[dict]) -> bytes:
        """Build a CSV file in memory."""
        if not rows:
            return b""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return output.getvalue().encode("utf-8")

    def test_csv_import_basic(self, test_client, db_session):
        """CSV with basic problem fields imports correctly."""
        csv_bytes = self._make_csv([
            {
                "leetcode_id": "1",
                "title": "Two Sum",
                "url": "https://leetcode.com/problems/two-sum",
                "difficulty": "easy",
                "pattern": "hash_map",
                "category": "algorithm",
                "source": "blind75",
                "priority": "1",
                "tags": "array;hash_map",
                "company_tags": "google;meta",
            },
            {
                "leetcode_id": "15",
                "title": "3Sum",
                "url": "",
                "difficulty": "medium",
                "pattern": "two_pointers",
                "category": "algorithm",
                "source": "",
                "priority": "2",
                "tags": "array;sorting",
                "company_tags": "",
            },
        ])

        resp = test_client.post(
            "/api/import/csv",
            files={"file": ("problems.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["inserted"] == 2
        assert data["skipped"] == 0

        p1 = db_session.query(Problem).filter(Problem.leetcode_id == 1).first()
        assert p1.title == "Two Sum"
        assert p1.tags_list == ["array", "hash_map"]
        assert p1.company_tags_list == ["google", "meta"]

    def test_csv_skip_existing(self, test_client, db_session):
        """CSV import skips problems that already exist."""
        db_session.add(Problem(
            leetcode_id=1, title="Two Sum", difficulty="easy",
            tags="[]", company_tags="[]",
        ))
        db_session.commit()

        csv_bytes = self._make_csv([
            {"leetcode_id": "1", "title": "Two Sum", "difficulty": "easy",
             "tags": "", "company_tags": ""},
        ])
        resp = test_client.post(
            "/api/import/csv",
            files={"file": ("problems.csv", csv_bytes, "text/csv")},
        )
        assert resp.json()["skipped"] == 1
        assert resp.json()["inserted"] == 0

    def test_csv_empty_file(self, test_client):
        """CSV with only headers imports nothing."""
        csv_bytes = b"leetcode_id,title,difficulty,tags,company_tags\n"
        resp = test_client.post(
            "/api/import/csv",
            files={"file": ("empty.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 200
        assert resp.json()["inserted"] == 0

    def test_csv_no_leetcode_id(self, test_client, db_session):
        """CSV rows without leetcode_id still import by title."""
        csv_bytes = self._make_csv([
            {"leetcode_id": "", "title": "Custom Problem", "difficulty": "medium",
             "tags": "dp;greedy", "company_tags": ""},
        ])
        resp = test_client.post(
            "/api/import/csv",
            files={"file": ("problems.csv", csv_bytes, "text/csv")},
        )
        assert resp.json()["inserted"] == 1
        p = db_session.query(Problem).filter(Problem.title == "Custom Problem").first()
        assert p is not None
        assert p.tags_list == ["dp", "greedy"]
