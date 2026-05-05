"""Idempotent seed: Lyra therapy Session 6 with Jacqueline Hurt-Coppola.

Per user Discord 2026-05-05 (msg 1501371531886858270):
  - Friday 2026-05-08, 10:00 AM PDT
  - Therapy, Session 6, 60 min
  - Provider: Jacqueline Hurt-Coppola

Company: Lyra (id=25). Timezone: naive Pacific (PDT), per project convention.
Mirrors the existing 'Lyra session with Jacqueline' style (event id=17 / Apr 28-30
prior sessions seeded via scripts/_add_lyra_jacqueline_apr2830.py).

Run: python scripts/_add_lyra_jacqueline_2026-05-08.py
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

SESSIONS = [
    {
        "title": "Lyra session with Jacqueline",
        "scheduled_at": "2026-05-08 10:00:00",
        "description": (
            "Jacqueline Hurt-Coppola scheduled a new session. "
            "Friday 2026-05-08 10:00 AM PDT, 60 min. "
            "Therapy session (Lyra), Session 6."
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
