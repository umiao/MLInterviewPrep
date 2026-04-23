"""Sync Uber final round interview events to the canonical post-reschedule set.

Idempotent: re-running deletes any "Uber Final Round -" rows that don't match
the canonical set below and inserts any missing rows. Safe to re-run.

Source:
  - Original schedule confirmed 2026-04-10 (Discord).
  - Reschedule confirmed 2026-04-22 (Discord msg 1496662923605446667):
    Coding 1 and Coding 2 interviewer roles swapped (Bo Cui is now Coding 1,
    Ali Shameli is now Coding 2); D&A moved from Apr 27 13:30 to Apr 29 14:00;
    Coding 2 (Ali) moved from Apr 29 to May 04 11:00; HackerRank links added.

Timezone: naive Pacific time (PDT = GMT-07:00), per project convention.
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
TITLE_PREFIX = "Uber Final Round -"

EVENTS = [
    {
        "event_type": "technical",
        "title": "Uber Final Round - Coding 1 (Algorithms & Data Structures) | Bo Cui",
        "description": (
            "Uber final round virtual onsite - Interview 1 of 4.\n"
            "Monday 2026-04-27, 10:00-11:00 AM PDT (GMT-07:00).\n"
            "Software Engineering - Algorithms & Data Structures (Coding 1).\n"
            "Interviewer: Bo Cui.\n"
            "HackerRank: https://hr.gs/1f5a617\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-27 10:00:00",
    },
    {
        "event_type": "behavioral",
        "title": "Uber Final Round - Collaboration & Leadership | Yifan Ma",
        "description": (
            "Uber final round virtual onsite - Interview 2 of 4.\n"
            "Monday 2026-04-27, 3:30-4:30 PM PDT (GMT-07:00).\n"
            "Collaboration & Leadership interview (behavioral).\n"
            "Interviewer: Yifan Ma.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-27 15:30:00",
    },
    {
        "event_type": "system_design",
        "title": "Uber Final Round - Design & Architecture (New Problem) | Ke Chen",
        "description": (
            "Uber final round virtual onsite - Interview 3 of 4.\n"
            "Wednesday 2026-04-29, 2:00-3:00 PM PDT (GMT-07:00).\n"
            "Design & Architecture - New Problem interview.\n"
            "Interviewer: Ke Chen.\n"
            "HackerRank: https://hr.gs/73b2465\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-04-29 14:00:00",
    },
    {
        "event_type": "technical",
        "title": "Uber Final Round - Coding 2 (Depth in Specialization) | Ali Shameli",
        "description": (
            "Uber final round virtual onsite - Interview 4 of 4.\n"
            "Monday 2026-05-04, 11:00 AM-12:00 PM PDT (GMT-07:00).\n"
            "Software Engineering - Depth in Specialization (Coding 2).\n"
            "Interviewer: Ali Shameli.\n"
            "HackerRank: https://hr.gs/d9de51d\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-05-04 11:00:00",
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    canonical_keys = {(ev["scheduled_at"], ev["title"]) for ev in EVENTS}

    cur.execute(
        "SELECT id, scheduled_at, title FROM interview_events "
        "WHERE company_id = ? AND title LIKE ?",
        (UBER_COMPANY_ID, f"{TITLE_PREFIX}%"),
    )
    existing_rows = cur.fetchall()
    existing_keys = set()
    deleted = 0
    for row_id, sched, title in existing_rows:
        if (sched, title) in canonical_keys:
            existing_keys.add((sched, title))
            continue
        cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
        print(f"[DELETE] id={row_id}: {title} @ {sched}")
        deleted += 1

    inserted = 0
    skipped = 0
    for ev in EVENTS:
        key = (ev["scheduled_at"], ev["title"])
        if key in existing_keys:
            cur.execute(
                "UPDATE interview_events SET description = ?, event_type = ?, "
                "duration_minutes = ?, location = ?, status = ? "
                "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
                (
                    ev["description"],
                    ev["event_type"],
                    DURATION_MINUTES,
                    LOCATION,
                    STATUS,
                    UBER_COMPANY_ID,
                    ev["scheduled_at"],
                    ev["title"],
                ),
            )
            print(f"[SYNC]   {ev['title']} @ {ev['scheduled_at']}")
            skipped += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, deleted={deleted}, synced={skipped}")


if __name__ == "__main__":
    main()
