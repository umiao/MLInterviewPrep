"""Idempotent seed: Lyra therapy session with Jacqueline -- Session 9.

Source: dashboard reminder 2026-05-26 ("see you soon! Your next session with
Jacqueline is Tomorrow at 2:00 PM PDT (05-27) Wed").
  - Wednesday 2026-05-27, 2:00 PM PDT
  - Therapy with Jacqueline, Session 9
  - 50 min

Company: Lyra (id=25). Timezone: naive Pacific (PDT), per project convention.
This is a NEW distinct session row, mirroring the prior Jacqueline session
pattern (id=17/37/38/60/67/76), last seeded by
scripts/_add_lyra_jacqueline_2026-05-19.py.

Canonical key (matches the proven pattern in the prior Jacqueline seeds):
(company_id, scheduled_at, title). Re-runs UPSERT the single row so the
seed is the idempotent source of truth.

Run: python scripts/_add_lyra_jacqueline_2026-05-27.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 25
COMPANY_NAME = "Lyra"
EVENT_TYPE = "other"
DURATION_MINUTES = 50
STATUS = "upcoming"

SESSIONS = [
    {
        "title": "Lyra session with Jacqueline",
        "scheduled_at": "2026-05-27 14:00:00",
        "description": (
            "Jacqueline Hurt-Coppola session -- Session 9. "
            "Wednesday 2026-05-27 2:00 PM PDT, 50 min. "
            "Therapy session (Lyra)."
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

    print(f"\nDone. inserted={inserted}, synced={synced}")


if __name__ == "__main__":
    main()
