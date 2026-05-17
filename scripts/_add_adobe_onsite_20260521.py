"""Add Adobe final-round in-person onsite panel (4 rounds, 2026-05-21) to interview_events.

Source: Discord ad-hoc request 2026-05-17 (xushenghui) -- Adobe final onsite itinerary.
  4 back-to-back 45-min in-person rounds at "CR SJ AT10/Fitzroy VC (10)", all PDT:
    - 12:00-12:45  Binjie Lai
    - 13:00-13:45  Shawn (Xiang) Wu
    - 14:00-14:45  Hsin-Ya Lou
    - 15:00-15:45  Tian Zhou
  Panel rubric (5 focus areas, mapping interviewer->area NOT provided by source):
    1. Modeling & Statistics (End-to-End ML Lifecycle)
    2. Hands-On LLM Experience
    3. Communication & Presentation
    4. Ownership
    5. Manager Round (direct manager; ambition / interest / long-term plans)

Routing: interview itinerary -> interview_events (NEVER company_documents.content),
per MLInterviewPrep CLAUDE.md "Surface Identification" routing rules + invariant3_guard.

Idempotent UPSERT keyed on (company_id, scheduled_at, title), matching the pattern
in _add_uber_team_match_20260515.py. Also flips companies.status phone_screen->onsite
for Adobe (final onsite stage; consistent with onsite-stage peers Google/Meta/Uber/
Pinterest). Re-running yields a deterministic state. Timezone: naive Pacific wall-clock
per project convention (memory feedback_check_data_before_fix).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

ADOBE_COMPANY_ID = 23
ADOBE_COMPANY_NAME = "Adobe"
LOCATION = "CR SJ AT10/Fitzroy VC (10) -- in person, San Jose"

# Shared panel rubric appended to every round so each event row is self-contained.
PANEL_RUBRIC = (
    "Panel focus areas (interviewer->area mapping not provided; one round is the "
    "Manager Round):\n"
    "  1. Modeling & Statistics -- end-to-end ML lifecycle: training, validation, "
    "deployment, monitoring in production; moving models from local dev into "
    "stable, scalable pipelines with real-world impact.\n"
    "  2. Hands-On LLM Experience -- deep hands-on building AI-driven apps with "
    "LLMs; staying current as LLM tooling/techniques/best-practices evolve.\n"
    "  3. Communication & Presentation -- translate complex technical concepts and "
    "model outputs into clear, actionable insights for non-technical stakeholders.\n"
    "  4. Ownership -- own outcomes end-to-end; rapidly self-direct ramp on new "
    "tech, libraries, and problem domains to meet business needs.\n"
    "  5. Manager Round -- conversation with direct manager on ambition, interest, "
    "and long-term plans."
)

EVENTS = [
    {
        "title": "Adobe Final Round (Onsite Panel) -- R1 Binjie Lai",
        "scheduled_at": "2026-05-21 12:00:00",
        "window": "12:00-12:45 PM PDT (GMT-07:00)",
    },
    {
        "title": "Adobe Final Round (Onsite Panel) -- R2 Shawn (Xiang) Wu",
        "scheduled_at": "2026-05-21 13:00:00",
        "window": "1:00-1:45 PM PDT (GMT-07:00)",
    },
    {
        "title": "Adobe Final Round (Onsite Panel) -- R3 Hsin-Ya Lou",
        "scheduled_at": "2026-05-21 14:00:00",
        "window": "2:00-2:45 PM PDT (GMT-07:00)",
    },
    {
        "title": "Adobe Final Round (Onsite Panel) -- R4 Tian Zhou",
        "scheduled_at": "2026-05-21 15:00:00",
        "window": "3:00-3:45 PM PDT (GMT-07:00)",
    },
]

EVENT_TYPE = "technical"
DURATION_MINUTES = 45
STATUS = "upcoming"


def _build_description(interviewer: str, window: str) -> str:
    """Compose a self-contained description for one onsite panel round."""
    return (
        f"Adobe Senior MLE final-round IN-PERSON onsite panel.\n"
        f"Thursday 2026-05-21, {window}, 45 min.\n"
        f"Interviewer: {interviewer}.\n"
        f"Location: {LOCATION}.\n"
        f"Format: 4 back-to-back 45-min rounds (12:00 / 13:00 / 14:00 / 15:00 PDT) "
        f"with ~15 min gaps; same room all day.\n\n"
        f"{PANEL_RUBRIC}"
    )


def main() -> None:
    """UPSERT the 4 onsite panel events + flip Adobe pipeline status to onsite."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()

        for ev in EVENTS:
            interviewer = ev["title"].split(" -- ", 1)[1].split(" ", 1)[1]
            description = _build_description(interviewer, ev["window"])
            cur.execute(
                "SELECT id FROM interview_events "
                "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
                (ADOBE_COMPANY_ID, ev["scheduled_at"], ev["title"]),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE interview_events SET "
                    "event_type = ?, description = ?, duration_minutes = ?, "
                    "location = ?, status = ?, company_name = ? "
                    "WHERE id = ?",
                    (
                        EVENT_TYPE,
                        description,
                        DURATION_MINUTES,
                        LOCATION,
                        STATUS,
                        ADOBE_COMPANY_NAME,
                        row[0],
                    ),
                )
                print(f"[SYNC]   id={row[0]}: {ev['title']} @ {ev['scheduled_at']}")
            else:
                cur.execute(
                    "INSERT INTO interview_events ("
                    "company_id, company_name, event_type, title, description, "
                    "scheduled_at, duration_minutes, location, status"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        ADOBE_COMPANY_ID,
                        ADOBE_COMPANY_NAME,
                        EVENT_TYPE,
                        ev["title"],
                        description,
                        ev["scheduled_at"],
                        DURATION_MINUTES,
                        LOCATION,
                        STATUS,
                    ),
                )
                print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")

        # Pipeline status: Adobe is now in the final onsite stage. Idempotent flip
        # phone_screen -> onsite (no-op if already onsite). Valid per company.py
        # CHECK ('applied','phone_screen','onsite','offer','rejected').
        cur.execute("SELECT status FROM companies WHERE id = ?", (ADOBE_COMPANY_ID,))
        cur_status = cur.fetchone()
        if cur_status and cur_status[0] != "onsite":
            cur.execute(
                "UPDATE companies SET status = 'onsite' WHERE id = ?",
                (ADOBE_COMPANY_ID,),
            )
            print(f"[STATUS] Adobe {cur_status[0]} -> onsite")
        else:
            print("[STATUS] Adobe already onsite (no-op)")

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
