"""Idempotent seed: Lyra MD video session #4 with Mary Miller, 2026-05-28.

Source: user-forwarded scheduling note 2026-05-19 -- "Mary scheduled a new
session with you. Thursday, May 28, 2026, 11:30 AM PDT."

4th in the recurring Lyra MD video session series with Mary Miller
(prior events: id=12 2026-04-13, id=32 2026-04-23, id=40 2026-05-07).
Mirrors that series exactly: event_type='other', 60-min default duration
(every prior session in the series is 60 min; duration not given by Mary
this time -> default to the series norm).

Company: Lyra (company_id=25). Timezone: naive Pacific (PDT = GMT-07:00),
per project convention (the DB stores wall-clock Pacific, no tz suffix).

Idempotent: (scheduled_at, title) is the canonical key. Re-running updates
company/type/description/duration/location/status in place. Safe to re-run.

Run: python scripts/_add_lyra_mary_2026-05-28.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

EVENTS = [
    {
        "company_id": 25,
        "company_name": "Lyra",
        "event_type": "other",
        "title": "MD Video Session -- Mary Miller",
        "description": (
            "Mary scheduled a new session. "
            "Thursday 2026-05-28 11:30 AM PDT, 60 min "
            "(duration not specified -- series default). "
            "4th MD video session with Mary Miller (Lyra); prior sessions "
            "2026-04-13, 2026-04-23, 2026-05-07. "
            "Timezone: North America Pacific Time (America/Los_Angeles)."
        ),
        "scheduled_at": "2026-05-28 11:30:00",
        "duration_minutes": 60,
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
