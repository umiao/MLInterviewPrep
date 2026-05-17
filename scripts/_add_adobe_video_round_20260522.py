"""Add the 5th Adobe final-round interview (video, 2026-05-22) to interview_events.

Source: Discord ad-hoc follow-up 2026-05-17 (xushenghui) -- a round missed from
the first itinerary drop:
  - Olivia Simpson | 05/22/2026 11:00-11:45 AM PDT | Microsoft Teams | Video Interview

This is a SEPARATE round from the 2026-05-21 in-person onsite panel
(see _add_adobe_onsite_20260521.py): different day, remote video via Teams,
NOT part of the 4 back-to-back in-person rounds. Kept in its own dated seed
per the granular scripts/_add_<company>_<date>.py convention.

Routing: interview itinerary -> interview_events (NEVER company_documents.content),
per MLInterviewPrep CLAUDE.md "Surface Identification" rules + invariant3_guard.

Idempotent UPSERT keyed on (company_id, scheduled_at, title), matching
_add_adobe_onsite_20260521.py / _add_uber_team_match_20260515.py. Re-running
yields a deterministic single row. Timezone: naive Pacific wall-clock per
project convention (memory feedback_check_data_before_fix). Adobe
companies.status is left as 'onsite' (already set by the 05-21 panel seed;
this remote round does not change the pipeline stage). Theme NOT assigned:
user confirmed Adobe rounds are team-random, no interviewer->theme mapping.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

ADOBE_COMPANY_ID = 23
ADOBE_COMPANY_NAME = "Adobe"

EVENT = {
    "event_type": "technical",
    "title": "Adobe Final Round (Video) -- Olivia Simpson",
    "description": (
        "Adobe Senior MLE final-round VIDEO interview (remote, Microsoft Teams).\n"
        "Friday 2026-05-22, 11:00-11:45 AM PDT (GMT-07:00), 45 min.\n"
        "Interviewer: Olivia Simpson.\n"
        "Platform: Microsoft Teams (meeting link provided by recruiter).\n"
        "Separate from the 2026-05-21 in-person onsite panel (4 back-to-back "
        "rounds in San Jose); this is the next-day remote round of the same "
        "final loop. Adobe panel covers 5 focus areas overall (Modeling & "
        "Statistics / Hands-on LLM / Communication / Ownership / Manager Round); "
        "interviewer->area mapping not provided (Adobe rounds are team-random)."
    ),
    "scheduled_at": "2026-05-22 11:00:00",
    "duration_minutes": 45,
    "location": "Microsoft Teams",
    "status": "upcoming",
}


def main() -> None:
    """UPSERT the 2026-05-22 video round keyed on (company_id, scheduled_at, title)."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (ADOBE_COMPANY_ID, EVENT["scheduled_at"], EVENT["title"]),
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
                    ADOBE_COMPANY_NAME,
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
                    ADOBE_COMPANY_ID,
                    ADOBE_COMPANY_NAME,
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
