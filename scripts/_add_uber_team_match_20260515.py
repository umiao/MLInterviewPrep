"""Add Uber MLE II team-match call with Memberships team on 2026-05-15 to interview_events.

Source: Discord ad-hoc request 2026-05-14 (msg 1504541588871970866):
  - [Team Match Call] Hersh / Shenghui -- MLE II (Memberships)
    Thu May 15, 2026 1:00 - 1:30 PM PDT

Idempotent UPSERT keyed on (company_id, scheduled_at, title), matching the
pattern in _add_uber_team_matches_20260511.py / _add_uber_team_match_20260508.py.
Re-running yields a deterministic single row. Timezone: naive Pacific time per
project convention (memory feedback_check_data_before_fix).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

UBER_COMPANY_ID = 5
UBER_COMPANY_NAME = "Uber"

EVENT = {
    "event_type": "other",
    "title": "Uber Team Match -- Memberships | Hersh",
    "description": (
        "Uber team-match conversation for the MLE II opportunity with the "
        "Memberships team.\n"
        "Thursday 2026-05-15, 1:00-1:30 PM PDT (GMT-07:00).\n"
        "Counterpart: Hersh (Memberships team).\n"
        "Format: 30-minute discovery / mutual-fit chat post-VO."
    ),
    "scheduled_at": "2026-05-15 13:00:00",
    "duration_minutes": 30,
    "location": "Zoom",
    "status": "upcoming",
}


def main() -> None:
    """UPSERT the team-match event keyed on (company_id, scheduled_at, title)."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (UBER_COMPANY_ID, EVENT["scheduled_at"], EVENT["title"]),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE interview_events SET "
                "event_type = ?, description = ?, duration_minutes = ?, "
                "location = ?, status = ?, company_name = ? "
                "WHERE id = ?",
                (
                    EVENT["event_type"],
                    EVENT["description"],
                    EVENT["duration_minutes"],
                    EVENT["location"],
                    EVENT["status"],
                    UBER_COMPANY_NAME,
                    row[0],
                ),
            )
            print(f"[SYNC]   id={row[0]}: {EVENT['title']} @ {EVENT['scheduled_at']}")
        else:
            cur.execute(
                "INSERT INTO interview_events ("
                "company_id, company_name, event_type, title, description, "
                "scheduled_at, duration_minutes, location, status"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    UBER_COMPANY_ID,
                    UBER_COMPANY_NAME,
                    EVENT["event_type"],
                    EVENT["title"],
                    EVENT["description"],
                    EVENT["scheduled_at"],
                    EVENT["duration_minutes"],
                    EVENT["location"],
                    EVENT["status"],
                ),
            )
            print(f"[INSERT] id={cur.lastrowid}: {EVENT['title']} @ {EVENT['scheduled_at']}")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
