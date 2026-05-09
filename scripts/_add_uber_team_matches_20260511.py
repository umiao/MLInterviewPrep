"""Add two Uber MLE II team-match calls on Mon 2026-05-11 to interview_events.

Source: Discord ad-hoc request 2026-05-09 (msg 1502520543478284500):
  - [Team Match Call] Dongtao / Shenghui -- MLE II (UberEats Feed)
    Mon May 11, 2026 12:00 - 12:30 PM PDT
  - [Team Match Call] Gil / Shenghui -- MLE II (Rider ML)
    Mon May 11, 2026 3:00 - 3:30 PM PDT

Idempotent UPSERT keyed on (company_id, scheduled_at, title), matching the
pattern in _add_uber_team_match_20260508.py. Re-running yields a deterministic
two rows (one per event). Timezone: naive Pacific time per project convention
(memory feedback_check_data_before_fix).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

UBER_COMPANY_ID = 5
UBER_COMPANY_NAME = "Uber"

EVENTS = [
    {
        "event_type": "other",
        "title": "Uber Team Match -- UberEats Feed | Dongtao",
        "description": (
            "Uber team-match conversation for the MLE II opportunity with the "
            "UberEats Feed team.\n"
            "Monday 2026-05-11, 12:00-12:30 PM PDT (GMT-07:00).\n"
            "Counterpart: Dongtao (UberEats Feed team).\n"
            "Format: 30-minute discovery / mutual-fit chat post-VO."
        ),
        "scheduled_at": "2026-05-11 12:00:00",
        "duration_minutes": 30,
        "location": "Zoom",
        "status": "upcoming",
    },
    {
        "event_type": "other",
        "title": "Uber Team Match -- Rider ML | Gil",
        "description": (
            "Uber team-match conversation for the MLE II opportunity with the "
            "Rider ML team.\n"
            "Monday 2026-05-11, 3:00-3:30 PM PDT (GMT-07:00).\n"
            "Counterpart: Gil (Rider ML team).\n"
            "Format: 30-minute discovery / mutual-fit chat post-VO."
        ),
        "scheduled_at": "2026-05-11 15:00:00",
        "duration_minutes": 30,
        "location": "Zoom",
        "status": "upcoming",
    },
]


def upsert(cur: sqlite3.Cursor, event: dict) -> None:
    """UPSERT one event keyed on (company_id, scheduled_at, title)."""
    cur.execute(
        "SELECT id FROM interview_events "
        "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
        (UBER_COMPANY_ID, event["scheduled_at"], event["title"]),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE interview_events SET "
            "event_type = ?, description = ?, duration_minutes = ?, "
            "location = ?, status = ?, company_name = ? "
            "WHERE id = ?",
            (
                event["event_type"],
                event["description"],
                event["duration_minutes"],
                event["location"],
                event["status"],
                UBER_COMPANY_NAME,
                row[0],
            ),
        )
        print(f"[SYNC]   id={row[0]}: {event['title']} @ {event['scheduled_at']}")
    else:
        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                UBER_COMPANY_ID,
                UBER_COMPANY_NAME,
                event["event_type"],
                event["title"],
                event["description"],
                event["scheduled_at"],
                event["duration_minutes"],
                event["location"],
                event["status"],
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {event['title']} @ {event['scheduled_at']}")


def main() -> None:
    """UPSERT both team-match events."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        for event in EVENTS:
            upsert(cur, event)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
