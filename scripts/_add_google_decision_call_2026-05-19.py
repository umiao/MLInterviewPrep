"""Idempotent seed: Google final decision call timeline event, 2026-05-19.

Per user (calendar invite, 2026-05-18):
  - Google final decision call
      * Tuesday 2026-05-19, 11:30-11:45 AM PT (15 min)
      * Timezone: North America Pacific Time -- America/Los_Angeles
      * Organizer: Emily Thomas
      * Attendee: xushenghui@gmail.com

This is the terminal outcome gate following the 2026-05-07 Google
IN-PERSON final round (Coding 1 @ 15:15 + Coding 2 @ 16:00, events 41/42).
Recruiter-driven outcome/next-steps call -> event_type='hr_call' (mirrors
the earlier Google "Recruiter Call", event id=10).

Timezone: naive Pacific time (PDT = GMT-07:00), per project convention.

Idempotent: (scheduled_at, title) is the canonical key. Re-running updates
company/type/description/duration/location/status fields in place. Safe to
re-run.

Run: python scripts/_add_google_decision_call_2026-05-19.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

EVENTS = [
    {
        "company_id": 3,
        "company_name": "Google",
        "event_type": "hr_call",
        "title": "Google Final Decision Call -- Emily Thomas",
        "description": (
            "Google SWE III (AI/ML) final decision call.\n"
            "Tuesday 2026-05-19, 11:30-11:45 AM PT (GMT-07:00), 15 min.\n"
            "Timezone: North America Pacific Time (America/Los_Angeles).\n"
            "Organizer: Emily Thomas (recruiter).\n"
            "Attendee: xushenghui@gmail.com.\n"
            "Terminal outcome gate following the 2026-05-07 IN-PERSON final "
            "round (Coding 1 @ 15:15 + Coding 2 @ 16:00, Google Building 43, "
            "Mountain View). Expect hiring decision / next-steps."
        ),
        "scheduled_at": "2026-05-19 11:30:00",
        "duration_minutes": 15,
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
