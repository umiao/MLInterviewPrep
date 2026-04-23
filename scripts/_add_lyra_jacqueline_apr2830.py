"""Idempotent seed: two new Lyra sessions with Jacqueline.

Per user Discord 2026-04-22 (msg 1496662923605446667):
  - Tuesday 2026-04-28, 10:00 AM PDT
  - Thursday 2026-04-30, 10:00 AM PDT

Company: Lyra (id=25). Timezone: naive Pacific (PDT), per project convention.
Mirrors the existing 'Lyra session with Jacqueline' style (event id=17).

Run: python scripts/_add_lyra_jacqueline_apr2830.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 25
COMPANY_NAME = "Lyra"
EVENT_TYPE = "other"
DURATION_MINUTES = 60
STATUS = "upcoming"

SESSIONS = [
    {
        "title": "Lyra session with Jacqueline",
        "scheduled_at": "2026-04-28 10:00:00",
        "description": (
            "Jacqueline scheduled a new session. Tuesday 2026-04-28 "
            "10:00 AM PDT, 60 min. Therapy session (Lyra)."
        ),
    },
    {
        "title": "Lyra session with Jacqueline",
        "scheduled_at": "2026-04-30 10:00:00",
        "description": (
            "Jacqueline scheduled a new session. Thursday 2026-04-30 "
            "10:00 AM PDT, 60 min. Therapy session (Lyra)."
        ),
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    inserted = 0
    skipped = 0
    for ev in SESSIONS:
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (COMPANY_ID, ev["scheduled_at"], ev["title"]),
        )
        existing = cur.fetchone()
        if existing is not None:
            print(f"[SKIP] id={existing[0]} already present: {ev['title']} @ {ev['scheduled_at']}")
            skipped += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                COMPANY_ID,
                COMPANY_NAME,
                EVENT_TYPE,
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                DURATION_MINUTES,
                None,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, skipped={skipped}")


if __name__ == "__main__":
    main()
