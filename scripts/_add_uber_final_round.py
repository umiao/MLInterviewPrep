"""Add Uber final round interview events to the interview_events table.

Idempotent: re-running only inserts events not already present (keyed by
company_id + scheduled_at + title).

Source: user confirmation 2026-04-10 (Discord).
Timezone convention: naive Pacific time (per
feedback_check_data_before_fix.md — MLInterviewPrep stores naive PT).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

UBER_COMPANY_ID = 5
UBER_COMPANY_NAME = "Uber"
DURATION_MINUTES = 60
LOCATION = "Zoom"
STATUS = "upcoming"

# All datetimes are naive Pacific time. PDT = GMT-07:00.
EVENTS = [
    {
        "event_type": "technical",
        "title": "Uber Final Round - Coding 2 (Depth in Specialization) | Bo Cui",
        "description": (
            "Uber final round virtual onsite - Interview 1 of 4.\n"
            "10:00-11:00 AM PDT (GMT-07:00).\n"
            "Software Engineering - Depth in Specialization (Coding 2).\n"
            "Interviewer: Bo Cui.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-27 10:00:00",
    },
    {
        "event_type": "system_design",
        "title": "Uber Final Round - Design & Architecture (New Problem) | Ke Chen",
        "description": (
            "Uber final round virtual onsite - Interview 2 of 4.\n"
            "1:30-2:30 PM PDT (GMT-07:00).\n"
            "Design & Architecture - New Problem interview.\n"
            "Interviewer: Ke Chen.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-27 13:30:00",
    },
    {
        "event_type": "behavioral",
        "title": "Uber Final Round - Collaboration & Leadership | Yifan Ma",
        "description": (
            "Uber final round virtual onsite - Interview 3 of 4.\n"
            "3:30-4:30 PM PDT (GMT-07:00).\n"
            "Collaboration & Leadership interview (behavioral).\n"
            "Interviewer: Yifan Ma.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-27 15:30:00",
    },
    {
        "event_type": "technical",
        "title": "Uber Final Round - Coding 1 (Algorithms & Data Structures) | Ali Shameli",
        "description": (
            "Uber final round virtual onsite - Interview 4 of 4.\n"
            "11:00 AM-12:00 PM PDT (GMT-07:00).\n"
            "Software Engineering - Algorithms & Data Structures (Coding 1).\n"
            "Interviewer: Ali Shameli.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-29 11:00:00",
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for ev in EVENTS:
        cur.execute(
            """
            SELECT id FROM interview_events
            WHERE company_id = ? AND scheduled_at = ? AND title = ?
            """,
            (UBER_COMPANY_ID, ev["scheduled_at"], ev["title"]),
        )
        existing = cur.fetchone()
        if existing is not None:
            print(f"[SKIP] id={existing[0]} already present: {ev['title']}")
            skipped += 1
            continue

        cur.execute(
            """
            INSERT INTO interview_events (
                company_id, company_name, event_type, title, description,
                scheduled_at, duration_minutes, location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                UBER_COMPANY_ID,
                UBER_COMPANY_NAME,
                ev["event_type"],
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                DURATION_MINUTES,
                LOCATION,
                STATUS,
            ),
        )
        new_id = cur.lastrowid
        print(f"[INSERT] id={new_id}: {ev['title']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, skipped={skipped}")


if __name__ == "__main__":
    main()
