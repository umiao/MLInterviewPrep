"""Add a personal tax reminder event: call California FTB on 2026-04-13.

Full-day reminder to notify California Franchise Tax Board that the user's
2025 tax filing documents are correct - the employer issued a corrected W-2
that reports reduced withholding to the government, and the corrected W-2 is
ready to file.

Idempotent: re-running only inserts if not already present (keyed by title +
scheduled_at).

Timezone: naive Pacific time (per MLInterviewPrep convention).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

COMPANY_ID = None  # No row in companies table; personal, not a job
COMPANY_NAME = "California FTB"  # NOT NULL column
EVENT_TYPE = "other"
TITLE = "Call California FTB re: corrected W-2 and tax filing (full day)"
DESCRIPTION = (
    "Full-day personal task for 2026-04-13 (Monday).\n"
    "\n"
    "Call the California Franchise Tax Board to notify them that the 2025\n"
    "tax filing documents are correct:\n"
    "  - Employer issued a CORRECTED W-2 (the earlier one was wrong).\n"
    "  - Corrected W-2 reports reduced withholding to the government.\n"
    "  - Corrected W-2 is now ready to file.\n"
    "\n"
    "Bring to the call:\n"
    "  - Corrected W-2 (original + amount breakdown)\n"
    "  - Prior W-2 for comparison if asked\n"
    "  - Any FTB reference/case number from previous correspondence\n"
    "\n"
    "Reminder sourced from user request 2026-04-10 (Discord)."
)
SCHEDULED_AT = "2026-04-13 17:00:00"  # naive Pacific; scheduled late (5pm) so
                                      # the event stays in "upcoming" view all
                                      # day instead of flipping to past at 9am.
                                      # "Full day" intent encoded via
                                      # description + duration_minutes=None.
DURATION_MINUTES = None  # None = full day / open-ended
LOCATION = "Phone"
STATUS = "upcoming"


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id FROM interview_events
        WHERE title = ? AND scheduled_at = ?
        """,
        (TITLE, SCHEDULED_AT),
    )
    existing = cur.fetchone()
    if existing is not None:
        print(f"[SKIP] id={existing[0]} already present: {TITLE}")
        conn.close()
        return

    cur.execute(
        """
        INSERT INTO interview_events (
            company_id, company_name, event_type, title, description,
            scheduled_at, duration_minutes, location, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            COMPANY_ID,
            COMPANY_NAME,
            EVENT_TYPE,
            TITLE,
            DESCRIPTION,
            SCHEDULED_AT,
            DURATION_MINUTES,
            LOCATION,
            STATUS,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    print(f"[INSERT] id={new_id}: {TITLE}")


if __name__ == "__main__":
    main()
