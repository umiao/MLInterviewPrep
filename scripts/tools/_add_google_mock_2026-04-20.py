# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Idempotent seed: Google Champion Program mock coding interview on 2026-04-20.

Confirmed by user via email reply on 2026-04-14. 60-minute mock coding slot
(Google Champion Program allows one mock coding max per candidate).
Run: python scripts/_add_google_mock_2026-04-20.py
"""
from __future__ import annotations

import sqlite3

DB_PATH = "data/mle_prep.db"
SCHEDULED_AT = "2026-04-20 10:00:00"
TITLE = "Google Champion Program -- Mock Coding Interview"


def main() -> None:
    """Insert the mock interview event if not already present."""
    with sqlite3.connect(DB_PATH) as conn:
        existing = conn.execute(
            "SELECT id FROM interview_events "
            "WHERE title = ? AND scheduled_at = ?",
            (TITLE, SCHEDULED_AT),
        ).fetchone()
        if existing:
            print(f"[SKIP] Event already exists id={existing[0]}")
            return

        conn.execute(
            "INSERT INTO interview_events "
            "(company_id, company_name, event_type, title, description, "
            " scheduled_at, duration_minutes, location, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                3,
                "Google",
                "technical",
                TITLE,
                "Confirmed via email on 2026-04-14. 60-min mock coding "
                "(Google Champion Program -- one mock coding max per candidate). "
                "Time: Mon 2026-04-20 10:00-11:00 PT (Los Angeles, GMT-07:00 PDT).",
                SCHEDULED_AT,
                60,
                "Virtual (Google Meet)",
                "upcoming",
            ),
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"[OK] Inserted event id={new_id}")


if __name__ == "__main__":
    main()
