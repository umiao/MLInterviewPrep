"""Idempotent seed: Slack Hiring Manager Round on Wed 2026-04-22 09:00-09:45 PDT.

Per user Discord 2026-04-20: Salesforce Virtual Interview for Software
Engineer II, Machine Learning -- hiring-manager round with Scott Clark
(Manager, Software Engineering). Category = Slack (per user, the role is
on the Slack ML team under Salesforce).

Run: python scripts/_add_slack_hm_2026-04-22.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
COMPANY_ID = 32  # Slack
COMPANY_NAME = "Slack"
EVENT_TYPE = "phone_screen"  # no dedicated HM bucket; phone_screen is closest pre-onsite round
TITLE = "Slack Hiring Manager Round -- SWE II, ML (Scott Clark)"
SCHEDULED_AT = "2026-04-22 09:00:00"  # naive Pacific (PDT), per project convention
DURATION_MINUTES = 45
LOCATION = "Virtual"
DESCRIPTION = (
    "Salesforce Virtual Interview - Software Engineer II, Machine Learning "
    "(Slack team). Hiring-manager round with Scott Clark, Manager, Software "
    "Engineering. Wed 2026-04-22 09:00-09:45 AM PDT, 45 min. Tentative per "
    "scheduling email. Prep focus: team/role fit questions, main project "
    "stories (Ranking-as-Allocation), comp anchor, 3 prepared questions for "
    "the hiring manager."
)


def main() -> None:
    with sqlite3.connect(str(DB_PATH)) as conn:
        existing = conn.execute(
            "SELECT id FROM interview_events WHERE title = ? AND scheduled_at = ?",
            (TITLE, SCHEDULED_AT),
        ).fetchone()
        if existing:
            print(f"[SKIP] event already exists id={existing[0]}")
            return

        conn.execute(
            "INSERT INTO interview_events "
            "(company_id, company_name, event_type, title, description, "
            " scheduled_at, duration_minutes, location, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                COMPANY_ID,
                COMPANY_NAME,
                EVENT_TYPE,
                TITLE,
                DESCRIPTION,
                SCHEDULED_AT,
                DURATION_MINUTES,
                LOCATION,
                "upcoming",
            ),
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"[OK] inserted event id={new_id} ({TITLE} @ {SCHEDULED_AT})")


if __name__ == "__main__":
    main()
