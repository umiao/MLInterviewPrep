"""Idempotent reschedule: Meta AI-Enabled ML System Design follow-up.

Per user Discord 2026-05-13 (msg 1504175057919017090): the Meta follow-up
ML System Design round originally scheduled for Thursday 2026-05-14
10:00-10:45 AM PDT is rescheduled to Friday 2026-05-15 11:00-11:45 AM PDT.

The original event was seeded by scripts/_add_meta_mlsd_followup_2026-05-14.py
as event id=66 with title "Meta Follow-up Round - ML System Design". This
script:
  - finds that row (canonical key: company_id + old scheduled_at + title)
  - updates scheduled_at to 2026-05-15 11:00:00
  - aligns title with the parent round (id=45) wording: "AI-Enabled ML
    System Design"
  - rewrites the description to reflect the new slot

Idempotent: after the first run the row matches the new key, so subsequent
runs SYNC fields without inserting.

  - Friday 2026-05-15, 11:00-11:45 AM PDT (GMT-07:00)
  - AI-Enabled ML System Design follow-up
  - Duration: 45 min
  - Interviewer: TBD
  - Platform: Zoom

Company: Meta (id=31). Timezone: naive Pacific (PDT), per project convention.

Run: python scripts/_reschedule_meta_mlsd_2026-05-15.py
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

OLD_SCHEDULED_AT = "2026-05-14 10:00:00"
OLD_TITLE = "Meta Follow-up Round - ML System Design"

NEW_SCHEDULED_AT = "2026-05-15 11:00:00"
NEW_TITLE = "Meta Follow-up Round - AI-Enabled ML System Design"
NEW_DESCRIPTION = (
    "Meta follow-up interview (additional round after 2026-05-01 final).\n"
    "Friday 2026-05-15, 11:00-11:45 AM PDT (GMT-07:00).\n"
    "AI-Enabled ML System Design (follow-up to the 2026-05-01 round with "
    "Nailong Z., event id=45).\n"
    "Interviewer: TBD.\n"
    "Platform: Zoom.\n"
    "Note: rescheduled from 2026-05-14 10:00 AM PDT per user request "
    "(Discord 2026-05-13)."
)


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Already-rescheduled case: row at new key. SYNC fields, no insert.
    cur.execute(
        "SELECT id FROM interview_events "
        "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
        (COMPANY_ID, NEW_SCHEDULED_AT, NEW_TITLE),
    )
    existing_new = cur.fetchone()
    if existing_new is not None:
        cur.execute(
            "UPDATE interview_events SET "
            "company_name = ?, event_type = ?, description = ?, "
            "duration_minutes = ?, location = ?, status = ? "
            "WHERE id = ?",
            (
                COMPANY_NAME,
                EVENT_TYPE,
                NEW_DESCRIPTION,
                DURATION_MINUTES,
                LOCATION,
                STATUS,
                existing_new[0],
            ),
        )
        conn.commit()
        conn.close()
        print(f"[SYNC]   id={existing_new[0]}: already at {NEW_SCHEDULED_AT}, fields refreshed")
        return

    # First-run case: locate original row by old key, update in place.
    cur.execute(
        "SELECT id FROM interview_events "
        "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
        (COMPANY_ID, OLD_SCHEDULED_AT, OLD_TITLE),
    )
    existing_old = cur.fetchone()
    if existing_old is None:
        conn.close()
        raise SystemExit(
            f"[FAIL] Could not find Meta event at {OLD_SCHEDULED_AT!r} "
            f"with title {OLD_TITLE!r}. Inspect interview_events manually."
        )

    cur.execute(
        "UPDATE interview_events SET "
        "company_name = ?, event_type = ?, title = ?, description = ?, "
        "scheduled_at = ?, duration_minutes = ?, location = ?, status = ? "
        "WHERE id = ?",
        (
            COMPANY_NAME,
            EVENT_TYPE,
            NEW_TITLE,
            NEW_DESCRIPTION,
            NEW_SCHEDULED_AT,
            DURATION_MINUTES,
            LOCATION,
            STATUS,
            existing_old[0],
        ),
    )
    conn.commit()
    conn.close()
    print(
        f"[UPDATE] id={existing_old[0]}: {OLD_TITLE!r} @ {OLD_SCHEDULED_AT} "
        f"-> {NEW_TITLE!r} @ {NEW_SCHEDULED_AT}"
    )


if __name__ == "__main__":
    main()
