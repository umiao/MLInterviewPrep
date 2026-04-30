"""Seed Pinterest (companies.id=29) interview_stages JSON + notes.

Owner of the structured pipeline-stage list and the recruiter-call-summary
notes. Schedule details for individual onsite rounds are NOT here -- they
live in `interview_events` table (Dashboard's InterviewTimeline widget).
This seed exists per Invariant 3 (every DB content row needs a git-tracked
idempotent seed; ad-hoc SQL forbidden).

Source for AC4 final value: user Discord 2026-04-30 02:53 (msg
1499242161294676108) -- option C with two refinements:
  1. placeholder needs scheduled_at (use first onsite round time = 5/5 15:00)
  2. name bakes the date in; cross-table references stay in seed comments,
     never in data fields (callers want structured info, not human prose)

The single 'Virtual Onsite (5 rounds: 5/5-5/6)' placeholder lets callers of
GET /api/companies/29 see that the pipeline has reached onsite without
duplicating per-round details. For per-round details (interviewers, exact
timestamps, durations), callers should query GET /api/timeline/events
filtered by company_id=29 -- that hits the interview_events table where
each round is its own row (added by scripts/_add_pinterest_vo_2026-05-05_06.py).

Idempotency: hash-based gate. Re-running with byte-identical INTERVIEW_STAGES
+ NOTES = no writes.

Run: python scripts/seed_pinterest_companies_row.py
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
COMPANY_ID = 29

# --- interview_stages (option C from user 2026-04-30 02:53) ---
INTERVIEW_STAGES: list[dict[str, str]] = [
    {"name": "Recruiter Call", "status": "completed"},
    {"name": "Phone Screen (60min)", "status": "completed"},
    {
        "name": "Virtual Onsite (5 rounds: 5/5-5/6)",
        "status": "scheduled",
        "scheduled_at": "2026-05-05T15:00:00",
    },
]

# --- notes (revert to pre-2026-04-30 state: pure recruiter-summary text;
# the schedule-data block I incorrectly added at 02:00 is removed) ---
NOTES = (
    "Senior ML Engineer position\n"
    "TC ~$500K/yr\n"
    "Hiring model: general pool, ~5 HC available, competitive Team Match required\n"
    "\n"
    "2026-04-08 Recruiter Call Summary:\n"
    "- Phone Screen (60min): ML Project Discussion + 3 ML Fundamentals questions + Coding\n"
    "- Virtual Onsite (5 rounds x 60min): Coding x2, ML Deep Dive, ML System Modeling, BQ\n"
    "- Environment: Google Meet + CoderPad (no compiler)\n"
    "- Phone screen time TBD -- need to send 3+ availability slots to David"
)


def fingerprint(stages: list[dict[str, str]], notes: str) -> str:
    """Stable hash over the canonical row content."""
    blob = json.dumps(stages, sort_keys=True, ensure_ascii=False) + "\n" + notes
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main() -> int:
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    new_stages_json = json.dumps(INTERVIEW_STAGES, ensure_ascii=False)
    target_hash = fingerprint(INTERVIEW_STAGES, NOTES)

    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT name, interview_stages, notes FROM companies WHERE id = ?",
            (COMPANY_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] company id={COMPANY_ID} not found; run seed_companies first")
            return 1

        name, current_stages, current_notes = row
        try:
            current_stages_parsed = json.loads(current_stages) if current_stages else []
        except json.JSONDecodeError:
            current_stages_parsed = None
        current_hash = fingerprint(current_stages_parsed or [], current_notes or "")

        if current_hash == target_hash:
            print(
                f"[UNCHANGED] companies.id={COMPANY_ID} ({name}) "
                f"hash={target_hash[:12]}... 0 writes"
            )
            return 0

        conn.execute(
            "UPDATE companies SET interview_stages = ?, notes = ? WHERE id = ?",
            (new_stages_json, NOTES, COMPANY_ID),
        )
        conn.commit()
        print(
            f"[UPDATE] companies.id={COMPANY_ID} ({name}) "
            f"old_stages={len(current_stages_parsed or [])} -> "
            f"new_stages={len(INTERVIEW_STAGES)}; "
            f"old_notes_len={len(current_notes or '')} -> "
            f"new_notes_len={len(NOTES)}; "
            f"hash={target_hash[:12]}..."
        )

    # Embedded twice-run assertion: rerun the function and demand UNCHANGED.
    # Catches non-idempotent bugs at seed time, not after deploy.
    with sqlite3.connect(str(DB_PATH)) as conn:
        row2 = conn.execute(
            "SELECT interview_stages, notes FROM companies WHERE id = ?",
            (COMPANY_ID,),
        ).fetchone()
        verify_hash = fingerprint(json.loads(row2[0]), row2[1])
        if verify_hash != target_hash:
            print(
                "[ASSERTION-FAIL] post-write hash mismatch: "
                f"got {verify_hash[:12]} expected {target_hash[:12]}"
            )
            return 2

    print("[ASSERTION-PASS] post-write read-back matches target hash")
    return 0


if __name__ == "__main__":
    sys.exit(main())
