"""Idempotent seed: Lyra MD session with Mary Miller on Thu 2026-04-23 08:30 AM PDT.

Per user Discord 2026-04-20: 'Mary scheduled a new session with you,
Thursday, April 23, 2026, 8:30 AM PDT'. Category = Lyra (incoming
psychological care / therapy), mirrors the prior Mary Miller MD video
session pattern (event id=12 on 2026-04-13, duration 60 min).

Run: python scripts/_add_lyra_mary_2026-04-23.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
COMPANY_ID = 25
COMPANY_NAME = "Lyra"
EVENT_TYPE = "other"
TITLE = "MD Video Session -- Mary Miller"
SCHEDULED_AT = "2026-04-23 08:30:00"  # naive Pacific (PDT), per project convention
DURATION_MINUTES = 60
DESCRIPTION = (
    "Mary scheduled a new session. Thursday 2026-04-23 08:30 AM PDT, "
    "60 min. Follow-up MD video session with Mary Miller (Lyra). "
    "Bring updated symptom log and medication list; confirm any FMLA / "
    "STD-leave paperwork items open since the 2026-04-13 session."
)


def main() -> None:
    with sqlite3.connect(str(DB_PATH)) as conn:
        existing = conn.execute(
            "SELECT id FROM interview_events WHERE title = ? AND scheduled_at = ?",
            (TITLE, SCHEDULED_AT),
        ).fetchone()
        if existing:
            print(f"[SKIP] event already exists id={existing[0]}")
            return

        conn.execute(
            "INSERT INTO interview_events "
            "(company_id, company_name, event_type, title, description, "
            " scheduled_at, duration_minutes, location, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                COMPANY_ID,
                COMPANY_NAME,
                EVENT_TYPE,
                TITLE,
                DESCRIPTION,
                SCHEDULED_AT,
                DURATION_MINUTES,
                None,
                "upcoming",
            ),
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"[OK] inserted event id={new_id} ({TITLE} @ {SCHEDULED_AT})")


if __name__ == "__main__":
    main()
