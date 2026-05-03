"""Add the Meta interview prep call with recruiter Elaine on 2026-04-28.

Idempotent: re-running deletes any "Meta Interview Prep Call -" rows that don't
match the canonical row below and inserts/updates the row to match. Safe to re-run.

Source: confirmed 2026-04-28 (Discord msg 1498777338991743048):
  - Elaine | Shenghui: Interview Prep
  - Tuesday 2026-04-28, 3:30-4:00 PM PDT (GMT-07:00)
  - Calendar invite to xushenghui@gmail.com.

Timezone: naive Pacific time, per project convention.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

META_COMPANY_ID = 31
META_COMPANY_NAME = "Meta"
LOCATION = "Zoom"
STATUS = "upcoming"
TITLE_PREFIX = "Meta Interview Prep Call -"

EVENTS = [
    {
        "event_type": "hr_call",
        "title": "Meta Interview Prep Call - Elaine",
        "description": (
            "Meta interview prep call with recruiter Elaine.\n"
            "Tuesday 2026-04-28, 3:30-4:00 PM PDT (GMT-07:00).\n"
            "Calendar event: 'Elaine | Shenghui: Interview Prep'.\n"
            "Invite to xushenghui@gmail.com.\n"
            "Pre-onsite logistics + final round briefing before Meta onsite (2026-05-01)."
        ),
        "scheduled_at": "2026-04-28 15:30:00",
        "duration_minutes": 30,
    },
]


def main() -> None:
    """Sync Meta prep-call rows to the canonical set."""
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
