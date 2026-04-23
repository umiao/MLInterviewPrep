"""Idempotent seed: ByteDance video interview with 桑燕 on 2026-04-28 14:00 PDT.

Per user Discord 2026-04-22 (msg 1496692745719517214):
  Interviewer: 桑燕
  Duration: 60 minutes
  Date/Time: 2026-04-28 14:00 Pacific Time (GMT-07:00, PDT)

Stored under TikTok (company_id=24) since TikTok is ByteDance's product
(same legal parent); dashboard keeps ByteDance/TikTok prep consolidated.
Title preserves the "ByteDance" branding from the email for searchability.
If a later message reveals this is a separate ByteDance team (not
TikTok Commerce Ads Ranking), move to a new company row.

Timezone: naive Pacific per project convention.

Run: python scripts/_add_bytedance_interview_2026-04-28.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

COMPANY_ID = 24
COMPANY_NAME = "TikTok"
EVENT_TYPE = "technical"
TITLE = "ByteDance Video Interview -- 桑燕"
SCHEDULED_AT = "2026-04-28 14:00:00"  # naive PDT
DURATION_MINUTES = 60
LOCATION = "Video call"
STATUS = "upcoming"
DESCRIPTION = (
    "ByteDance video interview confirmation (email thread 2026-04-22).\n"
    "Tuesday 2026-04-28, 2:00-3:00 PM PDT (GMT-07:00).\n"
    "Interviewer: 桑燕 (Sang Yan).\n"
    "Duration: 60 minutes.\n"
    "Platform: video call (confirm via main email thread).\n"
    "Filed under TikTok company row (same parent -- ByteDance)."
)


def main() -> None:
    with sqlite3.connect(str(DB_PATH)) as conn:
        existing = conn.execute(
            "SELECT id FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title = ?",
            (COMPANY_ID, SCHEDULED_AT, TITLE),
        ).fetchone()
        if existing:
            print(f"[SKIP] event already exists id={existing[0]}")
            return

        conn.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"[OK] inserted event id={new_id} ({TITLE} @ {SCHEDULED_AT})")


if __name__ == "__main__":
    main()
