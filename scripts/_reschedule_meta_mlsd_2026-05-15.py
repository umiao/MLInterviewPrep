"""Idempotent reschedule: Meta AI-Enabled ML System Design follow-up.

Reschedule history (all Discord-driven, all on 2026-05-13):
  - Originally seeded as 2026-05-14 10:00 AM PDT, title "Meta Follow-up Round
    - ML System Design" by scripts/_add_meta_mlsd_followup_2026-05-14.py
    (event id=66)
  - Moved to 2026-05-15 11:00 AM PDT, title realigned to include "AI-Enabled"
    per Discord msg 1504175057919017090
  - Moved to 2026-05-15 12:00 PM PDT per Discord msg 1504182639463235645
    (current canonical slot)

The current canonical slot is the NEW_* constants below. PRIOR_SLOTS lists
every historically-seeded slot in newest-first order so this script is
robust to:
  - Re-runs (no-op via SYNC at the canonical slot)
  - Fresh-DB rebuild after the original 2026-05-14 seed (UPDATEs in place)
  - Re-runs after partial application from any intermediate state

The script never inserts; it only UPDATEs an existing row (or SYNCs the
already-canonical row). The interview_events.id is preserved (=66) so any
downstream references remain stable.

  - Friday 2026-05-15, 12:00-12:45 PM PDT (GMT-07:00)
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

NEW_SCHEDULED_AT = "2026-05-15 12:00:00"
NEW_TITLE = "Meta Follow-up Round - AI-Enabled ML System Design"
NEW_DESCRIPTION = (
    "Meta follow-up interview (additional round after 2026-05-01 final).\n"
    "Friday 2026-05-15, 12:00-12:45 PM PDT (GMT-07:00).\n"
    "AI-Enabled ML System Design (follow-up to the 2026-05-01 round with "
    "Nailong Z., event id=45).\n"
    "Interviewer: TBD.\n"
    "Platform: Zoom.\n"
    "Note: rescheduled from 2026-05-14 10:00 AM PDT to 2026-05-15 11:00 AM PDT, "
    "then to 2026-05-15 12:00 PM PDT, per user requests (Discord 2026-05-13)."
)

# Historical slots in newest-first order. The script walks this list looking
# for a row to migrate to (NEW_SCHEDULED_AT, NEW_TITLE). Each entry is the
# (scheduled_at, title) the row had AT that point in its reschedule history.
PRIOR_SLOTS = [
    ("2026-05-15 11:00:00", "Meta Follow-up Round - AI-Enabled ML System Design"),
    ("2026-05-14 10:00:00", "Meta Follow-up Round - ML System Design"),
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Already-canonical case: SYNC fields, no row movement.
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

    # Walk historical slots newest-first, UPDATE the first match in place.
    for prior_scheduled_at, prior_title in PRIOR_SLOTS:
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (COMPANY_ID, prior_scheduled_at, prior_title),
        )
        existing = cur.fetchone()
        if existing is None:
            continue

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
                existing[0],
            ),
        )
        conn.commit()
        conn.close()
        print(
            f"[UPDATE] id={existing[0]}: {prior_title!r} @ {prior_scheduled_at} "
            f"-> {NEW_TITLE!r} @ {NEW_SCHEDULED_AT}"
        )
        return

    conn.close()
    raise SystemExit(
        "[FAIL] Could not find a Meta MLSD row at any known historical slot "
        f"(canonical={NEW_SCHEDULED_AT}, prior={PRIOR_SLOTS}). "
        "Inspect interview_events manually."
    )


if __name__ == "__main__":
    main()
