"""Idempotent seed: Meta team-match joint call, 2026-05-19.

Source: recruiter message forwarded via Discord 2026-05-19
(msg 1506181574608293939). User confirmed scope = single one-time call
(the "every day / 每天" phrasing was a typo -- Discord msg 1506185264651960410,
"A 这是typo").

Recruiter context:
  - Headcount in Arash's team is moving to his peer manager Prateek Sharma.
  - Arash and Prateek report to the same Sr. Manager and work closely.
  - Joint call with Arash + Prateek to help understand Prateek's team.
  - Tomorrow at 1pm PT (Tuesday 2026-05-19, 13:00 PT). Calendar invite to
    follow. Duration not given by recruiter -> default 50 min (per the
    Discord clarification thread).

Recruiter-coordinated, non-technical pipeline conversation ->
event_type='hr_call' (mirrors Meta "Recruiter Call" event id=25 and the
Google decision-call precedent _add_google_decision_call_2026-05-19.py).

Company: Meta (company_id=31). Timezone: naive Pacific (PDT = GMT-07:00),
per project convention.

Idempotent: (scheduled_at, title) is the canonical key. Re-running updates
company/type/description/duration/location/status in place. Safe to re-run.

Run: python scripts/_add_meta_team_match_call_2026-05-19.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

EVENTS = [
    {
        "company_id": 31,
        "company_name": "Meta",
        "event_type": "hr_call",
        "title": "Meta Team Match Call -- Arash + Prateek Sharma",
        "description": (
            "Meta team-match joint call.\n"
            "Tuesday 2026-05-19, 1:00 PM PT (GMT-07:00), 50 min "
            "(duration not specified by recruiter -- default).\n"
            "Timezone: North America Pacific Time (America/Los_Angeles).\n"
            "Attendees: Arash + Prateek Sharma (peer hiring managers, same "
            "Sr. Manager).\n"
            "Context (recruiter update): the headcount in Arash's team is "
            "moving to his peer manager Prateek Sharma. Arash and Prateek "
            "report to the same Sr. Manager and work very closely. This "
            "joint call is to help better understand Prateek's team. "
            "Calendar invite to follow from the recruiter."
        ),
        "scheduled_at": "2026-05-19 13:00:00",
        "duration_minutes": 50,
        "location": None,
        "status": "upcoming",
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    inserted = 0
    synced = 0
    for ev in EVENTS:
        row = cur.execute(
            "SELECT id FROM interview_events WHERE scheduled_at = ? AND title = ?",
            (ev["scheduled_at"], ev["title"]),
        ).fetchone()

        if row:
            cur.execute(
                "UPDATE interview_events SET "
                "company_id = ?, company_name = ?, event_type = ?, "
                "description = ?, duration_minutes = ?, location = ?, status = ? "
                "WHERE id = ?",
                (
                    ev["company_id"],
                    ev["company_name"],
                    ev["event_type"],
                    ev["description"],
                    ev["duration_minutes"],
                    ev["location"],
                    ev["status"],
                    row[0],
                ),
            )
            print(f"[SYNC]   id={row[0]}: {ev['title']} @ {ev['scheduled_at']}")
            synced += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                ev["company_id"],
                ev["company_name"],
                ev["event_type"],
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                ev["duration_minutes"],
                ev["location"],
                ev["status"],
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, synced={synced}")


if __name__ == "__main__":
    main()
