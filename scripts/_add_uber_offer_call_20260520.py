"""Add Uber offer call with recruiter Jaclyn on 2026-05-20 to interview_events.

Source: calendar invite from Jaclyn (Uber recruiter):
  Wednesday May 20, 2026, 10:00 AM - 10:15 AM Pacific Time (Los Angeles).

This is the post-team-match offer conversation, following the final-round
loop (Apr 27 / Apr 29 / May 4) and four team-match conversations (May 8 -
May 15). Same recruiter as the original HR Talk (interview_events.id=3,
2026-03-23).

Idempotent UPSERT keyed on (company_id, scheduled_at, title), matching the
pattern in _add_uber_team_match_20260515.py / _add_uber_team_matches_20260511.py.
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
    "event_type": "hr_call",
    "title": "Uber Offer Call -- Jaclyn (Recruiter)",
    "description": (
        "Uber offer conversation with recruiter Jaclyn.\n"
        "Wednesday 2026-05-20, 10:00-10:15 AM PDT (GMT-07:00).\n"
        "Counterpart: Jaclyn (same recruiter as the 2026-03-23 HR Talk and "
        "the onsite-prep meeting).\n"
        "Format: 15-minute call, expected to deliver verbal offer terms "
        "following the final-round loop (Apr 27 / Apr 29 / May 4) and the "
        "four team-match conversations (May 8 - May 15)."
    ),
    "scheduled_at": "2026-05-20 10:00:00",
    "duration_minutes": 15,
    "location": "Phone / Zoom",
    "status": "upcoming",
}


def main() -> None:
    """UPSERT the offer-call event keyed on (company_id, scheduled_at, title)."""
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
