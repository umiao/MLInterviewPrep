"""Tests for database views and indexes."""
from datetime import date

from sqlalchemy import inspect, text

from src.backend.models.framework import StudyLog
from src.backend.models.problem import Attempt, Problem


def test_indexes_exist(db_engine):
    """Verify that the expected indexes are created on key columns."""
    insp = inspect(db_engine)

    def _has_index(table: str, column: str) -> bool:
        """Check if an index exists covering the given column."""
        indexes = insp.get_indexes(table)
        for idx in indexes:
            if column in idx["column_names"]:
                return True
        # Also check unique constraints (they create implicit indexes)
        return any(column in uc["column_names"] for uc in insp.get_unique_constraints(table))

    assert _has_index("problems", "pattern"), "problems.pattern index missing"
    assert _has_index("problems", "difficulty"), "problems.difficulty index missing"
    assert _has_index("problems", "next_review_at"), "problems.next_review_at index missing"
    assert _has_index("framework_nodes", "path"), "framework_nodes.path index missing"
    assert _has_index("study_logs", "date"), "study_logs.date index missing"
    assert _has_index("interview_questions", "company"), "interview_questions.company index missing"


def test_v_problem_stats_empty(db_session):
    """v_problem_stats returns empty when no problems exist."""
    rows = db_session.execute(text("SELECT * FROM v_problem_stats")).fetchall()
    assert rows == []


def test_v_problem_stats_with_data(db_session):
    """v_problem_stats aggregates attempt data per problem."""
    p = Problem(
        title="Two Sum",
        difficulty="easy",
        pattern="hash_map",
        tags="[]",
        company_tags="[]",
    )
    db_session.add(p)
    db_session.flush()

    a1 = Attempt(problem_id=p.id, duration_seconds=300, comfort_after=3)
    a2 = Attempt(problem_id=p.id, duration_seconds=600, comfort_after=5)
    db_session.add_all([a1, a2])
    db_session.commit()

    rows = db_session.execute(text("SELECT * FROM v_problem_stats")).fetchall()
    assert len(rows) == 1
    row = rows[0]._mapping
    assert row["problem_id"] == p.id
    assert row["title"] == "Two Sum"
    assert row["attempt_count"] == 2
    assert row["avg_duration_seconds"] == 450.0
    assert row["best_comfort"] == 5


def test_v_problem_stats_no_attempts(db_session):
    """v_problem_stats shows zero attempts for problems with no attempts."""
    p = Problem(title="Lonely Problem", tags="[]", company_tags="[]")
    db_session.add(p)
    db_session.commit()

    rows = db_session.execute(text("SELECT * FROM v_problem_stats")).fetchall()
    assert len(rows) == 1
    row = rows[0]._mapping
    assert row["attempt_count"] == 0
    assert row["avg_duration_seconds"] == 0
    assert row["best_comfort"] is None


def test_v_weekly_progress_empty(db_session):
    """v_weekly_progress returns empty when no study logs exist."""
    rows = db_session.execute(text("SELECT * FROM v_weekly_progress")).fetchall()
    assert rows == []


def test_v_weekly_progress_with_data(db_session, seed_framework):
    """v_weekly_progress aggregates study logs by week."""
    node = seed_framework[1]  # child node

    sl1 = StudyLog(
        framework_node_id=node.id,
        date=date(2026, 3, 9),
        duration_minutes=60,
        activity_type="reading",
    )
    sl2 = StudyLog(
        framework_node_id=node.id,
        date=date(2026, 3, 10),
        duration_minutes=90,
        activity_type="practice",
    )
    db_session.add_all([sl1, sl2])
    db_session.commit()

    rows = db_session.execute(text("SELECT * FROM v_weekly_progress")).fetchall()
    assert len(rows) == 1
    row = rows[0]._mapping
    assert row["total_study_minutes"] == 150
    assert row["total_study_hours"] == 2.5
    assert row["session_count"] == 2
    assert row["nodes_studied"] == 1


def test_v_weekly_progress_multiple_weeks(db_session, seed_framework):
    """v_weekly_progress groups by ISO year-week."""
    node = seed_framework[1]

    # Week 10 (Mon 2026-03-02 to Sun 2026-03-08)
    sl1 = StudyLog(
        framework_node_id=node.id,
        date=date(2026, 3, 2),
        duration_minutes=30,
    )
    # Week 11 (Mon 2026-03-09 to Sun 2026-03-15)
    sl2 = StudyLog(
        framework_node_id=node.id,
        date=date(2026, 3, 12),
        duration_minutes=45,
    )
    db_session.add_all([sl1, sl2])
    db_session.commit()

    rows = db_session.execute(text("SELECT * FROM v_weekly_progress ORDER BY year_week")).fetchall()
    assert len(rows) == 2
    assert rows[0]._mapping["total_study_minutes"] == 30
    assert rows[1]._mapping["total_study_minutes"] == 45
