"""Sync Meta final onsite interview events to the canonical set.

Idempotent: re-running deletes any "Meta Final Round -" rows that don't match the
canonical set below and inserts/updates rows to match. Safe to re-run.

Source: schedule confirmed 2026-04-28 (Discord msg 1498758695708786689); Nikhil U.'s
AI-Native Coding round rescheduled 2026-05-01 (Discord msg 1499869369805701272) from
Friday 2026-05-01 1:00-2:00 PM PT to Tuesday 2026-05-05 10:00-11:00 AM PT:
  - Fri 2026-05-01 09:00-09:45 AM PT  AI-Enabled ML System Design / Nailong Z.   (45 min)
  - Fri 2026-05-01 11:00 AM-12:00 PM PT  AI-Native Coding / Sai Srujan E.        (60 min)
  - Tue 2026-05-05 10:00-11:00 AM PT  AI-Native Coding / Nikhil U.  [RESCHEDULED] (60 min)
  - Fri 2026-05-01 15:00-15:45 PM PT  AI-Native Behavioral / Yogeshkumar V.      (45 min)

Timezone: naive Pacific time (PDT = GMT-07:00 on both 2026-05-01 and 2026-05-05),
per project convention.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

META_COMPANY_ID = 31
META_COMPANY_NAME = "Meta"
LOCATION = "Zoom"
STATUS = "upcoming"
TITLE_PREFIX = "Meta Final Round -"

EVENTS = [
    {
        "event_type": "system_design",
        "title": "Meta Final Round - AI-Enabled ML System Design | Nailong Z.",
        "description": (
            "Meta final round virtual onsite - Interview 1 of 4.\n"
            "Friday 2026-05-01, 9:00-9:45 AM PDT (GMT-07:00).\n"
            "AI-Enabled ML System Design.\n"
            "Interviewer: Nailong Z.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-05-01 09:00:00",
        "duration_minutes": 45,
    },
    {
        "event_type": "technical",
        "title": "Meta Final Round - AI-Native Coding | Sai Srujan E.",
        "description": (
            "Meta final round virtual onsite - Interview 2 of 4.\n"
            "Friday 2026-05-01, 11:00 AM-12:00 PM PDT (GMT-07:00).\n"
            "AI-Native Coding.\n"
            "Interviewer: Sai Srujan E.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-05-01 11:00:00",
        "duration_minutes": 60,
    },
    {
        "event_type": "technical",
        "title": "Meta Final Round - AI-Native Coding | Nikhil U.",
        "description": (
            "Meta final round virtual onsite - Interview 3 of 4 (rescheduled).\n"
            "Tuesday 2026-05-05, 10:00-11:00 AM PDT (GMT-07:00).\n"
            "AI-Native Coding.\n"
            "Interviewer: Nikhil U.\n"
            "Platform: Zoom.\n"
            "Note: originally scheduled Fri 2026-05-01 1:00-2:00 PM PT;\n"
            "rescheduled 2026-05-01 to Tue 2026-05-05 10:00-11:00 AM PT."
        ),
        "scheduled_at": "2026-05-05 10:00:00",
        "duration_minutes": 60,
    },
    {
        "event_type": "behavioral",
        "title": "Meta Final Round - AI-Native Behavioral | Yogeshkumar V.",
        "description": (
            "Meta final round virtual onsite - Interview 4 of 4.\n"
            "Friday 2026-05-01, 3:00-3:45 PM PDT (GMT-07:00).\n"
            "AI-Native Behavioral.\n"
            "Interviewer: Yogeshkumar V.\n"
            "Platform: Zoom."
        ),
        "scheduled_at": "2026-05-01 15:00:00",
        "duration_minutes": 45,
    },
]


def main() -> None:
    """Sync Meta final-onsite rows to the canonical set."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    canonical_keys = {(ev["scheduled_at"], ev["title"]) for ev in EVENTS}

    cur.execute(
        "SELECT id, scheduled_at, title FROM interview_events "
        "WHERE company_id = ? AND title LIKE ?",
        (META_COMPANY_ID, f"{TITLE_PREFIX}%"),
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
    synced = 0
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
                    ev["duration_minutes"],
                    LOCATION,
                    STATUS,
                    META_COMPANY_ID,
                    ev["scheduled_at"],
                    ev["title"],
                ),
            )
            print(f"[SYNC]   {ev['title']} @ {ev['scheduled_at']}")
            synced += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                META_COMPANY_ID,
                META_COMPANY_NAME,
                ev["event_type"],
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                ev["duration_minutes"],
                LOCATION,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, deleted={deleted}, synced={synced}")


if __name__ == "__main__":
    main()
