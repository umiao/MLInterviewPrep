"""Regression tests for BQ-TAX Phase 2 schema migration (T-P1-598).

Covers:
  (a) existing rows survive (data preserved across migration)
  (b) new tables created exactly once (idempotent CREATE)
  (c) ALTER COLUMN idempotent (re-run is a no-op)

The migration script lives at ``scripts/migrate_bq_taxonomy_20260421.py``.
These tests exercise it against a fresh SQLite file containing only the
legacy ``behavioral_examples`` table -- simulating the production DB state
before the migration lands.
"""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

_script_path = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "migrate_bq_taxonomy_20260421.py"
)
_spec = importlib.util.spec_from_file_location(
    "migrate_bq_taxonomy_20260421", _script_path
)
_migrate_mod = importlib.util.module_from_spec(_spec)
sys.modules["migrate_bq_taxonomy_20260421"] = _migrate_mod
_spec.loader.exec_module(_migrate_mod)
migrate = _migrate_mod.migrate


def _init_legacy_db(db_path: Path) -> None:
    """Create a minimal pre-Phase-2 schema with one behavioral_examples row."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Minimal legacy schema: behavioral_themes + behavioral_questions +
    # behavioral_examples as they existed before Phase 2. We intentionally
    # omit is_signature/signature_at to exercise the ADD COLUMN path.
    cur.executescript(
        """
        CREATE TABLE behavioral_themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug VARCHAR NOT NULL UNIQUE,
            label VARCHAR NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE behavioral_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id VARCHAR NOT NULL UNIQUE,
            text TEXT NOT NULL,
            category_id VARCHAR NOT NULL,
            category_name VARCHAR NOT NULL
        );
        CREATE TABLE behavioral_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            example_id VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL,
            situation TEXT,
            action TEXT,
            is_golden BOOLEAN NOT NULL DEFAULT 0
        );
        INSERT INTO behavioral_themes(slug, label, display_order)
            VALUES ('failure_setback', 'Failure & Setback', 1);
        INSERT INTO behavioral_questions(question_id, text, category_id, category_name)
            VALUES ('Q-L-1', 'describe failure', 'adaptability', 'Adaptability');
        INSERT INTO behavioral_examples(example_id, title, situation, action)
            VALUES ('EX-LEGACY-1', 'Legacy story',
                    'situation body', 'action body');
        """
    )
    conn.commit()
    conn.close()


def _cols(db_path: Path, table: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    finally:
        conn.close()


def _tables(db_path: Path) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        return {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()


@pytest.fixture()
def legacy_db(tmp_path: Path) -> Path:
    """A fresh SQLite file pre-populated with the pre-Phase-2 schema."""
    db = tmp_path / "mle_prep_legacy.db"
    _init_legacy_db(db)
    return db


def test_migration_creates_new_tables_and_columns(legacy_db: Path) -> None:
    """First run: tables created, columns added, legacy row survives."""
    counters = migrate(str(legacy_db), backup=False)
    assert counters["tables_created"] == 3
    assert counters["tables_skipped"] == 0
    assert counters["cols_added"] == 2
    assert counters["cols_skipped"] == 0

    tables = _tables(legacy_db)
    assert {"behavioral_facets", "question_facet_tags", "example_facet_tags"} <= tables

    ex_cols = _cols(legacy_db, "behavioral_examples")
    assert "is_signature" in ex_cols
    assert "signature_at" in ex_cols

    conn = sqlite3.connect(legacy_db)
    try:
        row = conn.execute(
            "SELECT example_id, title, situation, action, is_signature "
            "FROM behavioral_examples WHERE example_id = ?",
            ("EX-LEGACY-1",),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "EX-LEGACY-1"
    assert row[1] == "Legacy story"
    assert row[2] == "situation body"
    assert row[3] == "action body"
    assert row[4] == 0


def test_migration_idempotent_on_second_run(legacy_db: Path) -> None:
    """Second run: every step reports [SKIP]; counters flip to skipped side."""
    migrate(str(legacy_db), backup=False)
    counters = migrate(str(legacy_db), backup=False)
    assert counters["tables_created"] == 0
    assert counters["tables_skipped"] == 3
    assert counters["cols_added"] == 0
    assert counters["cols_skipped"] == 2


def test_migration_preserves_related_tables(legacy_db: Path) -> None:
    """Migration must not touch behavioral_themes or behavioral_questions rows."""
    migrate(str(legacy_db), backup=False)
    conn = sqlite3.connect(legacy_db)
    try:
        theme_cnt = conn.execute(
            "SELECT COUNT(*) FROM behavioral_themes"
        ).fetchone()[0]
        q_cnt = conn.execute(
            "SELECT COUNT(*) FROM behavioral_questions"
        ).fetchone()[0]
    finally:
        conn.close()
    assert theme_cnt == 1
    assert q_cnt == 1


def test_migration_can_insert_facet_and_tag_rows(legacy_db: Path) -> None:
    """After migration, the new tables accept inserts with expected FK wiring."""
    migrate(str(legacy_db), backup=False)
    conn = sqlite3.connect(legacy_db)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        theme_id = conn.execute(
            "SELECT id FROM behavioral_themes WHERE slug = 'failure_setback'"
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO behavioral_facets(slug, label, parent_theme_id, display_order) "
            "VALUES (?, ?, ?, ?)",
            ("staff_signal_ambiguity", "Ambiguity Tolerance", theme_id, 1),
        )
        facet_id = conn.execute(
            "SELECT id FROM behavioral_facets WHERE slug = 'staff_signal_ambiguity'"
        ).fetchone()[0]

        ex_id = conn.execute(
            "SELECT id FROM behavioral_examples WHERE example_id = 'EX-LEGACY-1'"
        ).fetchone()[0]
        q_id = conn.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = 'Q-L-1'"
        ).fetchone()[0]

        conn.execute(
            "INSERT INTO example_facet_tags(example_id, facet_id) VALUES (?, ?)",
            (ex_id, facet_id),
        )
        conn.execute(
            "INSERT INTO question_facet_tags(question_id, facet_id) VALUES (?, ?)",
            (q_id, facet_id),
        )
        conn.commit()

        ex_tag_cnt = conn.execute(
            "SELECT COUNT(*) FROM example_facet_tags"
        ).fetchone()[0]
        q_tag_cnt = conn.execute(
            "SELECT COUNT(*) FROM question_facet_tags"
        ).fetchone()[0]
    finally:
        conn.close()
    assert ex_tag_cnt == 1
    assert q_tag_cnt == 1


def test_migration_backup_is_created_when_requested(
    legacy_db: Path,
) -> None:
    """With backup=True, a timestamped *.bak.*_pre_bq_taxonomy file appears."""
    migrate(str(legacy_db), backup=True)
    siblings = list(legacy_db.parent.iterdir())
    assert any(
        s.name.startswith(f"{legacy_db.name}.bak.")
        and s.name.endswith("_pre_bq_taxonomy")
        for s in siblings
    ), [s.name for s in siblings]
