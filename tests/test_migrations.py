"""Tests for database schema migrations.

Uses temporary file-based SQLite databases with old schemas (missing columns)
to verify that _run_migrations() correctly alters existing tables.
In-memory test databases hide this class of bug because create_all() always
starts fresh.
"""
import sqlite3

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from src.backend.database import _run_migrations


def _create_old_schema_db(db_path: str) -> None:
    """Create a SQLite DB with the problems table missing framework_node_id.

    Args:
        db_path: Path to the SQLite file.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE framework_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            path TEXT NOT NULL,
            depth INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL,
            importance REAL DEFAULT 1.0,
            priority TEXT DEFAULT 'P2',
            estimated_hours REAL DEFAULT 0,
            confidence REAL DEFAULT 0.0
        )
    """)
    conn.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leetcode_id INTEGER,
            title TEXT NOT NULL,
            url TEXT,
            difficulty TEXT,
            tags TEXT,
            pattern TEXT,
            category TEXT DEFAULT 'algorithm',
            source TEXT,
            company_tags TEXT,
            priority INTEGER DEFAULT 2,
            is_completed BOOLEAN DEFAULT 0,
            comfort_level INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            last_attempted_at TIMESTAMP,
            next_review_at TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL UNIQUE,
            group_tag VARCHAR,
            interview_stages TEXT,
            status VARCHAR DEFAULT 'applied',
            applied_at DATE,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


@pytest.fixture()
def old_schema_db(tmp_path):
    """Create a temporary file-based DB with the old schema (no framework_node_id).

    Yields:
        SQLAlchemy engine connected to the temp DB.
    """
    db_path = str(tmp_path / "test_migrate.db")
    _create_old_schema_db(db_path)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


class TestMigration1FrameworkNodeId:
    """Test migration 1: add framework_node_id to problems."""

    def test_column_added(self, old_schema_db):
        """After migration, framework_node_id column exists in problems."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "framework_node_id" in columns

    def test_index_created(self, old_schema_db):
        """After migration, ix_problems_framework_node_id index exists."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        indexes = {idx["name"] for idx in insp.get_indexes("problems")}
        assert "ix_problems_framework_node_id" in indexes

    def test_schema_versions_recorded(self, old_schema_db):
        """After migration, schema_versions table records version 1."""
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version, description FROM schema_versions")
            ).fetchall()
        versions = {row[0] for row in rows}
        assert 1 in versions

    def test_idempotent(self, old_schema_db):
        """Running migrations twice is a no-op the second time."""
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows_first = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows_second = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        assert len(rows_first) == len(rows_second)
        assert 1 in {r[0] for r in rows_second}

    def test_column_missing_before_migration(self, old_schema_db):
        """Sanity check: column does NOT exist before migration runs."""
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "framework_node_id" not in columns
