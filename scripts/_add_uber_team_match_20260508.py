"""Add Uber team-match call with Mobility Simulation & Planning to interview_events.

Source: Recruiter email from Jaclyn (forwarded via Discord 2026-05-08 msg
1502151271099007047): "Setting up time for the two of you to discuss the MLE II
opportunity with the Mobility Simulation and Planning team."

When: Friday 2026-05-08, 3:00-3:30 PM Pacific Time.
Counterpart: Junyao (Uber-side team lead / hiring manager from the Mobility
Simulation & Planning team). Shenghui (me) is the candidate.

Idempotent UPSERT keyed on (company_id, scheduled_at, title) per the pattern
in _add_uber_final_round.py. Re-running yields a deterministic single row.
Timezone: naive Pacific time per project convention (memory
feedback_check_data_before_fix).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

UBER_COMPANY_ID = 5
UBER_COMPANY_NAME = "Uber"

EVENT = {
    "event_type": "other",
    "title": "Uber Team Match -- Mobility Simulation & Planning | Junyao",
    "description": (
        "Uber team-match conversation for the MLE II opportunity with the "
        "Mobility Simulation & Planning team.\n"
        "Friday 2026-05-08, 3:00-3:30 PM PDT (GMT-07:00).\n"
        "Counterpart: Junyao (team lead, Mobility Simulation & Planning).\n"
        "Recruiter: Jaclyn (organizer; reach out to her if reschedule needed).\n"
        "Format: 30-minute discovery / mutual-fit chat post-VO.\n"
        "Zoom: https://uber.zoom.us/j/94529612780?pwd=6ZzJtUBkICwoXoglAfOCYuflxX1meN.1&jst=2"
    ),
    "scheduled_at": "2026-05-08 15:00:00",
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
