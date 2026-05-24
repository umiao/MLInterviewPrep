"""Migration: add is_golden + golden_at to three content tables.

AC (T-P1-552 / T-GOLD-01):
  - framework_nodes.is_golden BOOLEAN NOT NULL DEFAULT 0
  - framework_nodes.golden_at DATETIME NULL
  - behavioral_examples.is_golden BOOLEAN NOT NULL DEFAULT 0
  - behavioral_examples.golden_at DATETIME NULL
  - company_documents.is_golden BOOLEAN NOT NULL DEFAULT 0
  - company_documents.golden_at DATETIME NULL

Idempotent: each ALTER is guarded by a PRAGMA table_info check, so re-running
on an already-migrated DB is a no-op.

Usage:
    python scripts/migrate_add_golden_marker_20260420.py [db_path]
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TABLES = ("framework_nodes", "behavioral_examples", "company_documents")


def _cols(cur: sqlite3.Cursor, table: str) -> set[str]:
    return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}


def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    added = 0
    skipped = 0
    for table in TABLES:
        cols = _cols(cur, table)
        if "is_golden" not in cols:
            cur.execute(
                f"ALTER TABLE {table} "
                "ADD COLUMN is_golden BOOLEAN NOT NULL DEFAULT 0"
            )
            print(f"[DONE] Added {table}.is_golden")
            added += 1
        else:
            print(f"[SKIP] {table}.is_golden already exists")
            skipped += 1
        if "golden_at" not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN golden_at DATETIME")
            print(f"[DONE] Added {table}.golden_at")
            added += 1
        else:
            print(f"[SKIP] {table}.golden_at already exists")
            skipped += 1

    conn.commit()

    print("\n[VERIFY] post-migration schema:")
    for table in TABLES:
        cols = _cols(cur, table)
        has_flag = "is_golden" in cols
        has_ts = "golden_at" in cols
        # Count golden rows as a sanity probe (should all be 0 on first run).
        cnt = cur.execute(
            f"SELECT COUNT(*) FROM {table} WHERE is_golden=1"
        ).fetchone()[0]
        print(
            f"  {table:<22}  is_golden={has_flag}  golden_at={has_ts}  "
            f"golden_rows={cnt}"
        )

    print(f"\n[SUMMARY] added={added}  skipped={skipped}")
    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)
    print(f"Migrating database: {db_path}")
    migrate(db_path)
