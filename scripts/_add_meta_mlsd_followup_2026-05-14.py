"""Idempotent seed: Meta ML System Design follow-up interview.

Per user Discord 2026-05-13 (msg 1503987892232650782): a follow-up ML System
Design round was scheduled for Thursday 2026-05-14, 10:00-10:45 AM PDT
(45 min). This is a follow-up to the 2026-05-01 Meta final virtual onsite
ML System Design round (Nailong Z., event id=45). The 10:00-10:45 AM slot was
freed by rescheduling the prior Lyra/Jacqueline therapy session to 2:00 PM
PDT the same day (see scripts/_add_lyra_jacqueline_2026-05-14.py).

  - Thursday 2026-05-14, 10:00-10:45 AM PDT (GMT-07:00)
  - ML System Design follow-up
  - Duration: 45 min
  - Interviewer: TBD
  - Platform: Zoom

Company: Meta (id=31). Timezone: naive Pacific (PDT), per project convention.

Run: python scripts/_add_meta_mlsd_followup_2026-05-14.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 31
COMPANY_NAME = "Meta"
EVENT_TYPE = "system_design"
DURATION_MINUTES = 45
STATUS = "upcoming"
LOCATION = "Zoom"

SESSIONS = [
    {
        "title": "Meta Follow-up Round - ML System Design",
        "scheduled_at": "2026-05-14 10:00:00",
        "description": (
            "Meta follow-up interview (additional round after 2026-05-01 final).\n"
            "Thursday 2026-05-14, 10:00-10:45 AM PDT (GMT-07:00).\n"
            "ML System Design.\n"
            "Interviewer: TBD.\n"
            "Platform: Zoom.\n"
            "Note: scheduled into the slot freed by rescheduling the Lyra/"
            "Jacqueline therapy session from 10:00 AM to 2:00 PM PDT."
        ),
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    inserted = 0
    synced = 0
    for ev in SESSIONS:
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (COMPANY_ID, ev["scheduled_at"], ev["title"]),
        )
        existing = cur.fetchone()
        if existing is not None:
            cur.execute(
                "UPDATE interview_events SET "
                "company_name = ?, event_type = ?, description = ?, "
                "duration_minutes = ?, location = ?, status = ? "
                "WHERE id = ?",
                (
                    COMPANY_NAME,
                    EVENT_TYPE,
                    ev["description"],
                    DURATION_MINUTES,
                    LOCATION,
                    STATUS,
                    existing[0],
                ),
            )
            print(f"[SYNC]   id={existing[0]}: {ev['title']} @ {ev['scheduled_at']}")
            synced += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                COMPANY_ID,
                COMPANY_NAME,
                EVENT_TYPE,
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                DURATION_MINUTES,
                LOCATION,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, synced={synced}")


if __name__ == "__main__":
    main()
