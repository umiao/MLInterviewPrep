"""Idempotent seed: timeline events for Thursday 2026-05-07.

Per user Discord 2026-04-23:
  - Google IN-PERSON final round at Building 43, Mountain View (msg 1496915165004828754)
      * 1st interview 3:15-4:00 PM PDT (45 min) -- CODING
      * 2nd interview 4:00-4:45 PM PDT (45 min) -- CODING
      * Address: 1600 Amphitheatre Pkwy, Mountain View, CA 94043
      * Arrive 15 min early with gov't-issued photo ID
      * Entrance: Building 43 public entrance closest to Charleston Park
      * Parking: Guest Parking in the surface lot (avoid carpool/expectant mother stalls)
  - Lyra MD Video Session with Mary Miller, Thursday 2026-05-07 7:30 AM PDT
    ("Mary scheduled a new session with you"; mirrors prior Mary Miller MD
    session pattern, event id=32 on 2026-04-23, duration 60 min.)

Timezone: naive Pacific time (PDT = GMT-07:00), per project convention.

Idempotent: (scheduled_at, title) is the canonical key. Re-running updates
description/type/duration/location/status fields in place for canonical rows,
deletes drift rows under `title LIKE 'Google Final Round (Onsite)%'` on the
2026-05-07 date (so earlier-title versions like "Interview 1/2" are swept
cleanly when titles evolve), and inserts missing rows. Safe to re-run.

Run: python scripts/_add_google_final_and_lyra_2026-05-07.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

GOOGLE_LOCATION = (
    "Google Building 43, 1600 Amphitheatre Pkwy, Mountain View, CA 94043"
)
GOOGLE_LOGISTICS = (
    "Arrive 15 min early. Bring government-issued photo ID "
    "(driver's license or passport). Public entrance: Building 43 entrance "
    "closest to Charleston Park. Parking: Guest Parking in the surface lot "
    "(avoid stalls labeled 'carpool' or 'expectant mother'); signage "
    "directs to Building 43 entrance."
)

EVENTS = [
    {
        "company_id": 25,
        "company_name": "Lyra",
        "event_type": "other",
        "title": "MD Video Session -- Mary Miller",
        "description": (
            "Mary scheduled a new session. Thursday 2026-05-07 07:30 AM PDT, "
            "60 min. Follow-up MD video session with Mary Miller (Lyra). "
            "Same-day as Google onsite final (coding 1 @ 15:15 + coding 2 @ 16:00 "
            "at Google Building 43, Mountain View). Wrap on time and budget "
            "~1h commute + 15-min early arrival buffer before 15:15 onsite."
        ),
        "scheduled_at": "2026-05-07 07:30:00",
        "duration_minutes": 60,
        "location": None,
        "status": "upcoming",
    },
    {
        "company_id": 3,
        "company_name": "Google",
        "event_type": "technical",
        "title": "Google Final Round (Onsite) -- Coding 1",
        "description": (
            "Google SWE III (AI/ML) IN-PERSON final round, Coding 1 of 2.\n"
            "Thursday 2026-05-07, 3:15-4:00 PM PDT (GMT-07:00), 45 min.\n"
            "Format: onsite coding at Google Building 43, Mountain View.\n"
            "Back-to-back with Coding 2 at 4:00 PM -- no buffer between slots.\n"
            f"Logistics: {GOOGLE_LOGISTICS}"
        ),
        "scheduled_at": "2026-05-07 15:15:00",
        "duration_minutes": 45,
        "location": GOOGLE_LOCATION,
        "status": "upcoming",
    },
    {
        "company_id": 3,
        "company_name": "Google",
        "event_type": "technical",
        "title": "Google Final Round (Onsite) -- Coding 2",
        "description": (
            "Google SWE III (AI/ML) IN-PERSON final round, Coding 2 of 2.\n"
            "Thursday 2026-05-07, 4:00-4:45 PM PDT (GMT-07:00), 45 min.\n"
            "Format: onsite coding at Google Building 43, Mountain View.\n"
            "Back-to-back with Coding 1 at 3:15 PM -- no buffer between slots.\n"
            f"Logistics: {GOOGLE_LOGISTICS}"
        ),
        "scheduled_at": "2026-05-07 16:00:00",
        "duration_minutes": 45,
        "location": GOOGLE_LOCATION,
        "status": "upcoming",
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    canonical_keys = {(ev["scheduled_at"], ev["title"]) for ev in EVENTS}

    cur.execute(
        "SELECT id, scheduled_at, title FROM interview_events "
        "WHERE scheduled_at LIKE '2026-05-07%' "
        "AND title LIKE 'Google Final Round (Onsite)%'"
    )
    existing_google_rows = cur.fetchall()
    deleted = 0
    for row_id, sched, title in existing_google_rows:
        if (sched, title) in canonical_keys:
            continue
        cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
        print(f"[DELETE] id={row_id}: {title} @ {sched}")
        deleted += 1

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

    print(f"\nDone. inserted={inserted}, deleted={deleted}, synced={synced}")


if __name__ == "__main__":
    main()
