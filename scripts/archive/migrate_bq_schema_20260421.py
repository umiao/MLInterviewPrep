"""Migration: BQ-DEPTH Phase B schema uplift (T-P1-579).

AC:
  - ALTER TABLE question_example_links ADD COLUMN is_primary BOOLEAN DEFAULT 0
    plus a partial UNIQUE index enforcing at most one primary per question.
  - ALTER TABLE behavioral_questions ADD COLUMN probe_notes TEXT (JSON blob:
    {core_signal, what_good_looks_like, what_L5_adds, common_failure_modes}).
  - ALTER TABLE behavioral_questions ADD COLUMN probe_notes_updated_at DATETIME.

Idempotent: every ALTER is guarded by a PRAGMA table_info check; the unique
index uses IF NOT EXISTS. Re-runs print [SKIP] and leave data untouched.

NO angle_label field. Per T-P1-579 spec, angle lives in probe_notes prose as
writing discipline. Revisit in 6 months if a cluster emerges.

DB-backup-guarded: before any write, the target DB is copied to
``<db>.bak.<timestamp>_pre_bq_depth`` (skipped for in-memory DBs or when
``--no-backup`` is passed).

Usage:
    python scripts/migrate_bq_schema_20260421.py [db_path] [--no-backup]
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LINK_NEW_COLUMNS = (
    ("is_primary", "BOOLEAN NOT NULL DEFAULT 0"),
)
QUESTION_NEW_COLUMNS = (
    ("probe_notes", "TEXT"),
    ("probe_notes_updated_at", "DATETIME"),
)

# Partial UNIQUE index: at most one primary per question. SQLite enforces it
# by only indexing rows where is_primary = 1 (duplicates on 0 are allowed).
DDL_UNIQUE_PRIMARY_PER_QUESTION = (
    "CREATE UNIQUE INDEX IF NOT EXISTS "
    "ux_qel_primary_per_question "
    "ON question_example_links(question_id) "
    "WHERE is_primary = 1"
)


def _table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    """Check if a table exists."""
    row = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _cols(cur: sqlite3.Cursor, table: str) -> set[str]:
    """Return column names for a table."""
    return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}


def _index_exists(cur: sqlite3.Cursor, name: str) -> bool:
    """Check if an index exists."""
    row = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped .bak before mutating."""
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_bq_depth")
    shutil.copy2(db_path, backup)
    return backup


def migrate(db_path: str, *, backup: bool = True) -> dict[str, int]:
    """Apply Phase B schema. Returns counters for verification.

    Args:
        db_path: Path to the SQLite database file.
        backup: If True and DB file exists, copy to a timestamped ``.bak``
            before any write.

    Returns:
        Dict with keys ``cols_added``, ``cols_skipped``, ``indexes_created``,
        ``indexes_skipped``.
    """
    path = Path(db_path)
    if backup and path.exists():
        bkp = _backup_db(path)
        if bkp is not None:
            print(f"[BACKUP] {bkp.name}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    counters = {
        "cols_added": 0,
        "cols_skipped": 0,
        "indexes_created": 0,
        "indexes_skipped": 0,
    }

    # --- question_example_links.is_primary -------------------------------
    if _table_exists(cur, "question_example_links"):
        existing = _cols(cur, "question_example_links")
        for col_name, col_decl in LINK_NEW_COLUMNS:
            if col_name in existing:
                print(f"[SKIP] question_example_links.{col_name} already exists")
                counters["cols_skipped"] += 1
            else:
                cur.execute(
                    f"ALTER TABLE question_example_links "
                    f"ADD COLUMN {col_name} {col_decl}"
                )
                print(f"[DONE] added question_example_links.{col_name}")
                counters["cols_added"] += 1
    else:
        print(
            "[WARN] question_example_links table missing -- "
            "skip is_primary. Run init_db first."
        )

    # --- partial UNIQUE: at most one primary per question ----------------
    if _table_exists(cur, "question_example_links"):
        if _index_exists(cur, "ux_qel_primary_per_question"):
            print("[SKIP] index ux_qel_primary_per_question already exists")
            counters["indexes_skipped"] += 1
        else:
            cur.execute(DDL_UNIQUE_PRIMARY_PER_QUESTION)
            print("[DONE] created index ux_qel_primary_per_question")
            counters["indexes_created"] += 1

    # --- behavioral_questions.probe_notes + probe_notes_updated_at -------
    if _table_exists(cur, "behavioral_questions"):
        existing = _cols(cur, "behavioral_questions")
        for col_name, col_decl in QUESTION_NEW_COLUMNS:
            if col_name in existing:
                print(f"[SKIP] behavioral_questions.{col_name} already exists")
                counters["cols_skipped"] += 1
            else:
                cur.execute(
                    f"ALTER TABLE behavioral_questions "
                    f"ADD COLUMN {col_name} {col_decl}"
                )
                print(f"[DONE] added behavioral_questions.{col_name}")
                counters["cols_added"] += 1
    else:
        print(
            "[WARN] behavioral_questions table missing -- "
            "skip probe_notes / probe_notes_updated_at. Run init_db first."
        )

    conn.commit()

    print("\n[VERIFY] post-migration state:")
    if _table_exists(cur, "question_example_links"):
        existing = _cols(cur, "question_example_links")
        for col_name, _ in LINK_NEW_COLUMNS:
            print(
                f"  question_example_links.{col_name:<12} "
                f"present={col_name in existing}"
            )
        print(
            f"  index ux_qel_primary_per_question      "
            f"present={_index_exists(cur, 'ux_qel_primary_per_question')}"
        )
    if _table_exists(cur, "behavioral_questions"):
        existing = _cols(cur, "behavioral_questions")
        for col_name, _ in QUESTION_NEW_COLUMNS:
            print(
                f"  behavioral_questions.{col_name:<24} "
                f"present={col_name in existing}"
            )

    # --- Guardrail: assert no angle_label field was added anywhere. ------
    bad = []
    if _table_exists(cur, "behavioral_questions") and (
        "angle_label" in _cols(cur, "behavioral_questions")
    ):
        bad.append("behavioral_questions.angle_label")
    if _table_exists(cur, "question_example_links") and (
        "angle_label" in _cols(cur, "question_example_links")
    ):
        bad.append("question_example_links.angle_label")
    if bad:
        raise RuntimeError(
            "angle_label column detected (should not exist per T-P1-579): "
            + ", ".join(bad)
        )
    print("  [GUARD] no angle_label column -- OK")

    print(
        f"\n[SUMMARY] cols_added={counters['cols_added']} "
        f"cols_skipped={counters['cols_skipped']} "
        f"indexes_created={counters['indexes_created']} "
        f"indexes_skipped={counters['indexes_skipped']}"
    )
    conn.close()
    return counters


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
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
