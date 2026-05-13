"""Idempotent seed: Lyra therapy session with Jacqueline Hurt-Coppola.

Reschedule history (Discord-driven, all on 2026-05-14):
  - Originally scheduled 10:00 AM PDT (Discord 2026-05-10 msg 1502929534046044240)
  - Moved to 2:00 PM PDT to free the 10:00 slot for a Meta MLSD follow-up
    (Discord 2026-05-13 msg 1503987671909929112)
  - Moved to 12:00 PM PDT, the canonical current slot
    (Discord 2026-05-13 msg 1504181155916943452). The 2026-05-13 Meta MLSD
    follow-up has since been rescheduled off 2026-05-14 entirely
    (see scripts/_reschedule_meta_mlsd_2026-05-15.py).

  - Thursday 2026-05-14, 12:00 PM PDT (current canonical slot)
  - Therapy, 60 min
  - Provider: Jacqueline Hurt-Coppola

Company: Lyra (id=25). Timezone: naive Pacific (PDT), per project convention.
Mirrors prior Jacqueline session pattern (id=17/37/38/60 etc., last seeded by
scripts/_add_lyra_jacqueline_2026-05-08.py).

Migration: deletes the prior 10:00 and 14:00 rows for this company+title so
re-runs are idempotent and the rescheduled slot is the single source of truth.

Run: python scripts/_add_lyra_jacqueline_2026-05-14.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 25
COMPANY_NAME = "Lyra"
EVENT_TYPE = "other"
DURATION_MINUTES = 60
STATUS = "upcoming"

# Slots that were superseded by the rescheduled SESSIONS below. Cleaned up at
# the start of every run so the rescheduled slot is the only Lyra/Jacqueline
# row on this date.
SUPERSEDED_SLOTS = [
    ("2026-05-14 10:00:00", "Lyra session with Jacqueline"),
    ("2026-05-14 14:00:00", "Lyra session with Jacqueline"),
]

SESSIONS = [
    {
        "title": "Lyra session with Jacqueline",
        "scheduled_at": "2026-05-14 12:00:00",
        "description": (
            "Jacqueline Hurt-Coppola session. "
            "Thursday 2026-05-14 12:00 PM PDT, 60 min. "
            "Therapy session (Lyra). "
            "Rescheduled 2026-05-13: first 10:00 AM -> 2:00 PM (to free the "
            "10:00 slot for a Meta MLSD follow-up), then 2:00 PM -> 12:00 PM "
            "per user request. The Meta MLSD follow-up has since moved off "
            "2026-05-14 (now Friday 2026-05-15 11:00 AM PDT)."
        ),
    },
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    deleted = 0
    for old_scheduled_at, old_title in SUPERSEDED_SLOTS:
        cur.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (COMPANY_ID, old_scheduled_at, old_title),
        )
        for (row_id,) in cur.fetchall():
            cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
            print(f"[DELETE] id={row_id}: {old_title} @ {old_scheduled_at} (superseded)")
            deleted += 1

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
                    None,
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
                None,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\nDone. inserted={inserted}, synced={synced}, deleted={deleted}")


if __name__ == "__main__":
    main()
