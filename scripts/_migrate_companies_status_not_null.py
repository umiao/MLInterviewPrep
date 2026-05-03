"""One-shot migration: enforce NOT NULL + server default on companies.status.

Rationale: 2026-04-15 bug — a raw seed script inserted Slack without
setting status, producing `status=NULL`. Pydantic response schema requires
`status: str`, so GET /companies raised ResponseValidationError at index 28.
Backfill was immediate; this migration closes the recurrence window by
making the SQLite column itself reject NULLs.

SQLite has no `ALTER TABLE ... SET NOT NULL`, so we copy-then-swap:
  1. Verify no NULL rows remain (backfill must have run).
  2. Create companies_new with the desired constraints (+ relationships preserved).
  3. INSERT ... SELECT from old.
  4. Drop old, rename new.

Idempotent: re-running checks the existing table DDL for NOT NULL and exits
cleanly if migration already applied.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def migrate() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='companies'"
        ).fetchone()[0]
        if "status VARCHAR NOT NULL" in ddl or "status VARCHAR DEFAULT 'applied' NOT NULL" in ddl:
            print("[SKIP] companies.status already NOT NULL")
            return

        n_null = conn.execute(
            "SELECT COUNT(*) FROM companies WHERE status IS NULL"
        ).fetchone()[0]
        if n_null:
            raise SystemExit(
                f"[FAIL] {n_null} rows still have status=NULL; backfill first"
            )

        conn.execute("BEGIN")
        conn.execute(
            """
            CREATE TABLE companies_new (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR NOT NULL UNIQUE,
                group_tag VARCHAR,
                interview_stages TEXT,
                status VARCHAR NOT NULL DEFAULT 'applied'
                    CHECK (status IN ('applied','phone_screen','onsite','offer','rejected')),
                applied_at DATE,
                notes TEXT,
                prep_notes TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO companies_new (
                id, name, group_tag, interview_stages, status,
                applied_at, notes, prep_notes
            )
            SELECT id, name, group_tag, interview_stages, status,
                   applied_at, notes, prep_notes
            FROM companies
            """
        )
        conn.execute("DROP TABLE companies")
        conn.execute("ALTER TABLE companies_new RENAME TO companies")
        conn.execute("COMMIT")
        print("[DONE] companies.status is now NOT NULL DEFAULT 'applied'")

        row_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        print(f"[VERIFY] companies row count: {row_count}")

    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    migrate()
