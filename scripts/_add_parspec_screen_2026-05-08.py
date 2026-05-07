"""Idempotent seed: PARSPEC phone screen with Sravanthi Rajanala on 2026-05-08.

Per user Discord 2026-05-06 (msg 1501604630851878983):
  Friday 2026-05-08, 1:00 PM - 1:45 PM PDT (America/Los_Angeles)
  Interviewer: Sravanthi Rajanala
  Location: https://meet.google.com/ysr-eozc-qxm

PARSPEC is a new company on the dashboard -- this seed creates the
companies row (status='phone_screen' since the screen is scheduled) and
the interview_events row in one transaction.

Timezone: naive Pacific per project convention (see CLAUDE.md +
memory feedback_check_data_before_fix.md).

Idempotent on (company_name, scheduled_at, title) for the event and
on companies.name for the company row -- re-runs SYNC, never duplicate.

Run: python scripts/_add_parspec_screen_2026-05-08.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_NAME = "PARSPEC"
COMPANY_GROUP_TAG = "startup"
COMPANY_STATUS = "phone_screen"
COMPANY_NOTES = (
    "PARSPEC: B2B / construction-spec startup (initial screen 2026-05-08).\n"
    "Recruiter / interviewer: Sravanthi Rajanala.\n"
    "More context TBD -- update this row after the screen."
)

EVENT_TYPE = "phone_screen"
EVENT_TITLE = "PARSPEC Phone Screen -- Sravanthi Rajanala"
SCHEDULED_AT = "2026-05-08 13:00:00"  # naive PDT
DURATION_MINUTES = 45
LOCATION = "https://meet.google.com/ysr-eozc-qxm"
STATUS = "upcoming"
DESCRIPTION = (
    "PARSPEC phone screen.\n"
    "Friday 2026-05-08, 1:00-1:45 PM PDT (America/Los_Angeles).\n"
    "Interviewer: Sravanthi Rajanala.\n"
    "Duration: 45 minutes.\n"
    "Platform: Google Meet (https://meet.google.com/ysr-eozc-qxm)."
)


def upsert_company(conn: sqlite3.Connection) -> int:
    """Create or fetch the PARSPEC company row. Returns companies.id."""
    row = conn.execute(
        "SELECT id, status, group_tag FROM companies WHERE name = ?",
        (COMPANY_NAME,),
    ).fetchone()
    if row:
        cid = row[0]
        # Sync only if status hasn't been advanced past phone_screen
        if row[1] in (None, "applied", "phone_screen"):
            conn.execute(
                "UPDATE companies SET status = ?, group_tag = COALESCE(group_tag, ?), "
                "notes = COALESCE(notes, ?) WHERE id = ?",
                (COMPANY_STATUS, COMPANY_GROUP_TAG, COMPANY_NOTES, cid),
            )
            print(f"[SYNC]   companies.id={cid} status -> {COMPANY_STATUS}")
        else:
            print(f"[SKIP]   companies.id={cid} status={row[1]} (preserved, not downgrading)")
        return cid

    cur = conn.execute(
        "INSERT INTO companies (name, group_tag, status, notes) VALUES (?, ?, ?, ?)",
        (COMPANY_NAME, COMPANY_GROUP_TAG, COMPANY_STATUS, COMPANY_NOTES),
    )
    cid = cur.lastrowid
    print(f"[INSERT] companies.id={cid} ({COMPANY_NAME}, status={COMPANY_STATUS})")
    return cid


def upsert_event(conn: sqlite3.Connection, company_id: int) -> None:
    """Create or sync the interview_events row."""
    row = conn.execute(
        "SELECT id FROM interview_events "
        "WHERE company_name = ? AND scheduled_at = ? AND title = ?",
        (COMPANY_NAME, SCHEDULED_AT, EVENT_TITLE),
    ).fetchone()
    if row:
        eid = row[0]
        conn.execute(
            "UPDATE interview_events SET "
            "company_id = ?, event_type = ?, description = ?, "
            "duration_minutes = ?, location = ?, status = ? "
            "WHERE id = ?",
            (company_id, EVENT_TYPE, DESCRIPTION, DURATION_MINUTES, LOCATION, STATUS, eid),
        )
        print(f"[SYNC]   interview_events.id={eid} {EVENT_TITLE} @ {SCHEDULED_AT}")
        return

    cur = conn.execute(
        "INSERT INTO interview_events ("
        "company_id, company_name, event_type, title, description, "
        "scheduled_at, duration_minutes, location, status"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            company_id, COMPANY_NAME, EVENT_TYPE, EVENT_TITLE, DESCRIPTION,
            SCHEDULED_AT, DURATION_MINUTES, LOCATION, STATUS,
        ),
    )
    print(f"[INSERT] interview_events.id={cur.lastrowid} {EVENT_TITLE} @ {SCHEDULED_AT}")


def main() -> None:
    with sqlite3.connect(str(DB_PATH)) as conn:
        cid = upsert_company(conn)
        upsert_event(conn, cid)

        # Verify
        row = conn.execute(
            "SELECT e.id, e.company_id, e.title, e.scheduled_at, e.duration_minutes, "
            "e.location, e.status, c.name, c.status "
            "FROM interview_events e LEFT JOIN companies c ON c.id = e.company_id "
            "WHERE e.company_name = ? AND e.scheduled_at = ?",
            (COMPANY_NAME, SCHEDULED_AT),
        ).fetchone()
        print(f"\n[VERIFY] {row}")


if __name__ == "__main__":
    main()
