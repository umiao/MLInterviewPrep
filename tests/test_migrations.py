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


class TestMigration4ReadingTables:
    """Test migration 4: create reading_progress, reading_sessions, audio_cache."""

    def test_tables_created(self, old_schema_db):
        """After migration, all three reading tables exist."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        table_names = set(insp.get_table_names())
        assert "reading_progress" in table_names
        assert "reading_sessions" in table_names
        assert "audio_cache" in table_names

    def test_reading_progress_columns(self, old_schema_db):
        """reading_progress table has expected columns."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("reading_progress")}
        expected = {
            "id", "content_type", "content_id", "last_chunk_index",
            "char_offset", "total_chars", "completed", "last_read_at",
        }
        assert expected <= columns

    def test_audio_cache_columns(self, old_schema_db):
        """audio_cache table has expected columns."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("audio_cache")}
        expected = {
            "id", "content_type", "content_id", "content_hash",
            "file_path", "engine", "voice", "created_at",
        }
        assert expected <= columns

    def test_schema_version_4_recorded(self, old_schema_db):
        """Migration version 4 is recorded in schema_versions."""
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        assert 4 in {row[0] for row in rows}

    def test_idempotent(self, old_schema_db):
        """Running migration 4 twice is safe."""
        _run_migrations(old_schema_db)
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        assert "reading_progress" in set(insp.get_table_names())

    def test_tables_missing_before_migration(self, old_schema_db):
        """Sanity check: reading tables do NOT exist before migration."""
        insp = inspect(old_schema_db)
        table_names = set(insp.get_table_names())
        assert "reading_progress" not in table_names
        assert "reading_sessions" not in table_names
        assert "audio_cache" not in table_names


class TestMigration6TranscriptsTable:
    """Test migration 6: create transcripts table."""

    def test_transcripts_table_created(self, old_schema_db):
        """After migration, transcripts table exists with all expected columns."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        table_names = set(insp.get_table_names())
        assert "transcripts" in table_names

    def test_transcripts_columns(self, old_schema_db):
        """transcripts table has all expected columns."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("transcripts")}
        expected = {
            "id", "content_type", "content_id", "source_hash",
            "transcript_text", "transcript_hash", "generation_method",
            "prompt_version", "is_latest", "created_at",
        }
        assert expected <= columns

    def test_schema_version_6_recorded(self, old_schema_db):
        """Migration version 6 is recorded in schema_versions."""
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        assert 6 in {row[0] for row in rows}

    def test_idempotent(self, old_schema_db):
        """Running migration 6 twice is safe."""
        _run_migrations(old_schema_db)
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        assert "transcripts" in set(insp.get_table_names())

    def test_table_missing_before_migration(self, old_schema_db):
        """Sanity check: transcripts table does NOT exist before migration."""
        insp = inspect(old_schema_db)
        table_names = set(insp.get_table_names())
        assert "transcripts" not in table_names


class TestMigration7ProblemDescriptionColumns:
    """Test migration 7: add description, neetcode_slug, description_source to problems."""

    def test_description_column_added(self, old_schema_db):
        """After migration, description column exists in problems."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "description" in columns

    def test_neetcode_slug_column_added(self, old_schema_db):
        """After migration, neetcode_slug column exists in problems."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "neetcode_slug" in columns

    def test_description_source_column_added(self, old_schema_db):
        """After migration, description_source column exists in problems."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "description_source" in columns

    def test_all_three_columns_added(self, old_schema_db):
        """After migration, all three new columns exist in problems."""
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        expected = {"description", "neetcode_slug", "description_source"}
        assert expected <= columns

    def test_schema_version_7_recorded(self, old_schema_db):
        """Migration version 7 is recorded in schema_versions."""
        _run_migrations(old_schema_db)
        with old_schema_db.connect() as conn:
            rows = conn.execute(
                text("SELECT version FROM schema_versions")
            ).fetchall()
        assert 7 in {row[0] for row in rows}

    def test_idempotent(self, old_schema_db):
        """Running migration 7 twice is safe."""
        _run_migrations(old_schema_db)
        _run_migrations(old_schema_db)
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "description" in columns

    def test_columns_missing_before_migration(self, old_schema_db):
        """Sanity check: new columns do NOT exist before migration."""
        insp = inspect(old_schema_db)
        columns = {col["name"] for col in insp.get_columns("problems")}
        assert "description" not in columns
        assert "neetcode_slug" not in columns
        assert "description_source" not in columns
