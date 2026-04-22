"""Migration: BQ-TAX Phase 2 schema uplift (T-P1-598).

AC:
  - CREATE TABLE behavioral_facets (id PK, slug UNIQUE, label, parent_theme_id
    NULL FK -> behavioral_themes, description, display_order, created_at)
  - CREATE TABLE example_facet_tags (example_id FK, facet_id FK, created_at,
    PK(example_id, facet_id))
  - CREATE TABLE question_facet_tags (question_id FK, facet_id FK, created_at,
    PK(question_id, facet_id))
  - ALTER TABLE behavioral_examples ADD COLUMN is_signature BOOLEAN DEFAULT 0
  - ALTER TABLE behavioral_examples ADD COLUMN signature_at DATETIME NULL

Idempotent: each CREATE TABLE uses IF NOT EXISTS; each ALTER is guarded by a
PRAGMA table_info check. Re-runs print [SKIP] and leave data untouched.

DB-backup-guarded: before any write, the target DB is copied to
``<db>.bak.<timestamp>_pre_bq_taxonomy`` (skipped for in-memory DBs or when
``--no-backup`` is passed).

Facet usage rule (enforced by reviewer, documented in the model file):
  Facets are ONLY for (a) staff/L6 signal tags, (b) cross-theme retrieval tags,
  (c) scenario sub-type when rename would mix abstraction layers. NOT a
  dumping ground.

Usage:
    python scripts/migrate_bq_taxonomy_20260421.py [db_path] [--no-backup]
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NEW_TABLES = ("behavioral_facets", "question_facet_tags", "example_facet_tags")
NEW_COLUMNS = (
    ("is_signature", "BOOLEAN NOT NULL DEFAULT 0"),
    ("signature_at", "DATETIME"),
)

DDL_BEHAVIORAL_FACETS = """
CREATE TABLE IF NOT EXISTS behavioral_facets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug VARCHAR NOT NULL UNIQUE,
    label VARCHAR NOT NULL,
    parent_theme_id INTEGER REFERENCES behavioral_themes(id) ON DELETE SET NULL,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

DDL_QUESTION_FACET_TAGS = """
CREATE TABLE IF NOT EXISTS question_facet_tags (
    question_id INTEGER NOT NULL REFERENCES behavioral_questions(id) ON DELETE CASCADE,
    facet_id INTEGER NOT NULL REFERENCES behavioral_facets(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id, facet_id)
)
"""

DDL_EXAMPLE_FACET_TAGS = """
CREATE TABLE IF NOT EXISTS example_facet_tags (
    example_id INTEGER NOT NULL REFERENCES behavioral_examples(id) ON DELETE CASCADE,
    facet_id INTEGER NOT NULL REFERENCES behavioral_facets(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (example_id, facet_id)
)
"""

DDL_INDEXES = (
    "CREATE INDEX IF NOT EXISTS ix_bf_parent_theme_id "
    "ON behavioral_facets(parent_theme_id)",
    "CREATE INDEX IF NOT EXISTS ix_qft_facet_id "
    "ON question_facet_tags(facet_id)",
    "CREATE INDEX IF NOT EXISTS ix_eft_facet_id "
    "ON example_facet_tags(facet_id)",
)


def _table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    row = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _cols(cur: sqlite3.Cursor, table: str) -> set[str]:
    return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped .bak before mutating."""
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_bq_taxonomy")
    shutil.copy2(db_path, backup)
    return backup


def migrate(db_path: str, *, backup: bool = True) -> dict[str, int]:
    """Apply Phase 2 schema. Returns counters for verification.

    Args:
        db_path: Path to the SQLite database file.
        backup: If True and DB file exists, copy to a timestamped ``.bak``
            before any write.

    Returns:
        Dict with keys ``tables_created``, ``tables_skipped``, ``cols_added``,
        ``cols_skipped``.
    """
    path = Path(db_path)
    if backup and path.exists():
        bkp = _backup_db(path)
        if bkp is not None:
            print(f"[BACKUP] {bkp.name}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    counters = {
        "tables_created": 0,
        "tables_skipped": 0,
        "cols_added": 0,
        "cols_skipped": 0,
    }

    for table, ddl in (
        ("behavioral_facets", DDL_BEHAVIORAL_FACETS),
        ("question_facet_tags", DDL_QUESTION_FACET_TAGS),
        ("example_facet_tags", DDL_EXAMPLE_FACET_TAGS),
    ):
        if _table_exists(cur, table):
            print(f"[SKIP] table {table} already exists")
            counters["tables_skipped"] += 1
        else:
            cur.execute(ddl)
            print(f"[DONE] created table {table}")
            counters["tables_created"] += 1

    for idx_sql in DDL_INDEXES:
        cur.execute(idx_sql)

    if _table_exists(cur, "behavioral_examples"):
        existing = _cols(cur, "behavioral_examples")
        for col_name, col_decl in NEW_COLUMNS:
            if col_name in existing:
                print(f"[SKIP] behavioral_examples.{col_name} already exists")
                counters["cols_skipped"] += 1
            else:
                cur.execute(
                    f"ALTER TABLE behavioral_examples "
                    f"ADD COLUMN {col_name} {col_decl}"
                )
                print(f"[DONE] added behavioral_examples.{col_name}")
                counters["cols_added"] += 1
    else:
        print(
            "[WARN] behavioral_examples table missing -- "
            "skip is_signature / signature_at. Run init_db or migration 13 first."
        )

    conn.commit()

    print("\n[VERIFY] post-migration state:")
    for table in NEW_TABLES:
        present = _table_exists(cur, table)
        if present:
            row_cnt = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table:<22} present=True rows={row_cnt}")
        else:
            print(f"  {table:<22} present=False")
    if _table_exists(cur, "behavioral_examples"):
        existing = _cols(cur, "behavioral_examples")
        for col_name, _ in NEW_COLUMNS:
            print(
                f"  behavioral_examples.{col_name:<12} "
                f"present={col_name in existing}"
            )

    print(
        f"\n[SUMMARY] tables_created={counters['tables_created']} "
        f"tables_skipped={counters['tables_skipped']} "
        f"cols_added={counters['cols_added']} "
        f"cols_skipped={counters['cols_skipped']}"
    )
    conn.close()
    return counters


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "db_path",
        nargs="?",
        default=str(DEFAULT_DB),
        help="Path to SQLite DB (default: data/mle_prep.db)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip pre-migration backup copy",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    print(f"Migrating database: {args.db_path}")
    migrate(args.db_path, backup=not args.no_backup)
