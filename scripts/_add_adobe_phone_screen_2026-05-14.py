"""Idempotent seed: Adobe Phone Screen on 2026-05-14.

Per user Discord 2026-05-13 (msg 1504185501085864127):
  Thursday 2026-05-14, 2:00 PM PDT (America/Los_Angeles)
  Duration: 30 minutes
  Interviewer: TBD
  Platform: TBD

Adobe already exists in the `companies` table (id=23) -- this seed only
inserts the `interview_events` row.

Timezone: naive Pacific (PDT), per project convention.

Idempotent on (company_id, scheduled_at, title): re-runs SYNC, never
duplicate.

Run: python scripts/_add_adobe_phone_screen_2026-05-14.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 23
COMPANY_NAME = "Adobe"
EVENT_TYPE = "phone_screen"
EVENT_TITLE = "Adobe Phone Screen"
SCHEDULED_AT = "2026-05-14 14:00:00"  # naive PDT
DURATION_MINUTES = 30
LOCATION = None  # platform TBD
STATUS = "upcoming"
DESCRIPTION = (
    "Adobe phone screen.\n"
    "Thursday 2026-05-14, 2:00-2:30 PM PDT (America/Los_Angeles).\n"
    "Duration: 30 minutes.\n"
    "Interviewer: TBD.\n"
    "Platform: TBD."
)


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM interview_events "
        "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
        (COMPANY_ID, SCHEDULED_AT, EVENT_TITLE),
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
                DESCRIPTION,
                DURATION_MINUTES,
                LOCATION,
                STATUS,
                existing[0],
            ),
        )
        conn.commit()
        conn.close()
        print(f"[SYNC]   id={existing[0]}: {EVENT_TITLE} @ {SCHEDULED_AT}")
        return

    cur.execute(
        "INSERT INTO interview_events ("
        "company_id, company_name, event_type, title, description, "
        "scheduled_at, duration_minutes, location, status"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            COMPANY_ID,
            COMPANY_NAME,
            EVENT_TYPE,
            EVENT_TITLE,
            DESCRIPTION,
            SCHEDULED_AT,
            DURATION_MINUTES,
            LOCATION,
            STATUS,
        ),
    )
    conn.commit()
    print(f"[INSERT] id={cur.lastrowid}: {EVENT_TITLE} @ {SCHEDULED_AT}")
    conn.close()


if __name__ == "__main__":
    main()
