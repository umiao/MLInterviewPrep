"""Sync Pinterest HR prep call (Daniel McCray, 2026-04-30 14:00 PDT) interview_events row.

Idempotent: re-running matches the canonical row by (company_id, scheduled_at,
interviewer_name) parsed from the trailing "| <Interviewer>" suffix in title.
Safe to re-run; second pass asserts 0/0/0.

Source: Daniel McCray email 2026-04-29 proposing prep call move to
2026-04-30 2:00 PM PDT. Coordinator/recruiter prep before Pinterest VO
(2026-05-05 / 2026-05-06).

Timezone: naive Pacific time (PDT = GMT-07:00 on 2026-04-30) per project
convention.

Modes:
  default: sync canonical row; embedded second pass asserts idempotency.
  --verify: read-only count + drift check; exits non-zero on mismatch.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
PINTEREST_COMPANY_NAME = "Pinterest"
LOCATION = "Zoom"
STATUS = "upcoming"
TITLE_PREFIX = "Pinterest HR Prep Call"

EVENT = {
    "event_type": "hr_call",
    "title": "Pinterest HR Prep Call | Daniel McCray",
    "description": (
        "Pinterest VO prep call (recruiter/coordinator).\n"
        "Thursday 2026-04-30, 2:00-2:30 PM PDT (GMT-07:00).\n"
        "Coordinator: Daniel McCray (rescheduled per email 2026-04-29).\n"
        "Platform: Zoom (placeholder; confirm with Daniel).\n"
        "Reference: company_documents id=83 (Pinterest VO prep doc)."
    ),
    "scheduled_at": "2026-04-30 14:00:00",
    "duration_minutes": 30,
}


def parse_interviewer(title: str) -> str:
    """Extract interviewer/coordinator name from the trailing '| <Name>' suffix."""
    if "|" not in title:
        raise ValueError(f"title missing '| <Interviewer>' suffix: {title!r}")
    return title.rsplit("|", 1)[1].strip()


def sync_pass(cur: sqlite3.Cursor) -> tuple[int, int, int]:
    """Sync the single canonical HR-prep-call row.

    Match strategy: rows whose title starts with TITLE_PREFIX and company_id
    matches Pinterest are candidates. Any candidate whose
    (scheduled_at, interviewer_name) does NOT match the canonical EVENT is
    deleted; otherwise fields are updated to canonical and counted.

    Returns (inserted, deleted, updated).
    """
    canonical_key = (EVENT["scheduled_at"], parse_interviewer(EVENT["title"]))

    cur.execute(
        "SELECT id, scheduled_at, title FROM interview_events "
        "WHERE company_id = ? AND title LIKE ?",
        (PINTEREST_COMPANY_ID, f"{TITLE_PREFIX}%"),
    )
    existing_rows = cur.fetchall()
    deleted = 0
    matched_existing = False
    for row_id, sched, title in existing_rows:
        try:
            interviewer = parse_interviewer(title)
        except ValueError:
            cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
            print(f"[DELETE] id={row_id}: {title} @ {sched} (unparseable)")
            deleted += 1
            continue
        if (sched, interviewer) == canonical_key:
            matched_existing = True
            continue
        cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
        print(f"[DELETE] id={row_id}: {title} @ {sched} (not canonical)")
        deleted += 1

    inserted = 0
    updated = 0
    if matched_existing:
        cur.execute(
            "SELECT title, description, event_type, duration_minutes, "
            "location, status FROM interview_events "
            "WHERE company_id = ? AND scheduled_at = ? AND title LIKE ?",
            (
                PINTEREST_COMPANY_ID,
                EVENT["scheduled_at"],
                f"%| {parse_interviewer(EVENT['title'])}",
            ),
        )
        current = cur.fetchone()
        target = (
            EVENT["title"],
            EVENT["description"],
            EVENT["event_type"],
            EVENT["duration_minutes"],
            LOCATION,
            STATUS,
        )
        if current == target:
            print(f"[UNCHANGED] {EVENT['title']} @ {EVENT['scheduled_at']}")
        else:
            cur.execute(
                "UPDATE interview_events SET title = ?, description = ?, "
                "event_type = ?, duration_minutes = ?, location = ?, status = ? "
                "WHERE company_id = ? AND scheduled_at = ? AND title LIKE ?",
                (
                    EVENT["title"],
                    EVENT["description"],
                    EVENT["event_type"],
                    EVENT["duration_minutes"],
                    LOCATION,
                    STATUS,
                    PINTEREST_COMPANY_ID,
                    EVENT["scheduled_at"],
                    f"%| {parse_interviewer(EVENT['title'])}",
                ),
            )
            print(f"[UPDATE] {EVENT['title']} @ {EVENT['scheduled_at']}")
            updated += 1
    else:
        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                PINTEREST_COMPANY_ID,
                PINTEREST_COMPANY_NAME,
                EVENT["event_type"],
                EVENT["title"],
                EVENT["description"],
                EVENT["scheduled_at"],
                EVENT["duration_minutes"],
                LOCATION,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {EVENT['title']} @ {EVENT['scheduled_at']}")
        inserted += 1

    return inserted, deleted, updated


def verify(cur: sqlite3.Cursor) -> int:
    """Read-only verification: canonical row present, no drift.

    Returns 0 on success, non-zero exit code on drift.
    """
    cur.execute(
        "SELECT scheduled_at, title, event_type, duration_minutes, status "
        "FROM interview_events WHERE company_id = ? AND title LIKE ? "
        "ORDER BY scheduled_at",
        (PINTEREST_COMPANY_ID, f"{TITLE_PREFIX}%"),
    )
    rows = cur.fetchall()
    if len(rows) != 1:
        print(f"[VERIFY-FAIL] expected 1 row, got {len(rows)}", file=sys.stderr)
        return 1
    sched, title, event_type, duration, status = rows[0]
    if (
        sched != EVENT["scheduled_at"]
        or title != EVENT["title"]
        or event_type != EVENT["event_type"]
        or duration != EVENT["duration_minutes"]
        or status != STATUS
    ):
        print(
            f"[VERIFY-FAIL] drift on {title} @ {sched}: "
            f"got event_type={event_type!r}, duration={duration!r}, "
            f"status={status!r}",
            file=sys.stderr,
        )
        return 1
    print("[VERIFY-OK] 1/1 row matches canonical, drift=0")
    print(f"[OK] {title} @ {sched}")
    return 0


def main() -> int:
    """Sync Pinterest HR-prep row; embedded second pass asserts idempotency."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Read-only verification mode (no writes).",
    )
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    if args.verify:
        rc = verify(cur)
        conn.close()
        return rc

    print("=== Pass 1: sync canonical row ===")
    inserted_1, deleted_1, updated_1 = sync_pass(cur)
    conn.commit()
    print(
        f"\nPass 1 done. inserted={inserted_1}, deleted={deleted_1}, "
        f"updated={updated_1}"
    )

    print("\n=== Pass 2: embedded idempotency assertion ===")
    inserted_2, deleted_2, updated_2 = sync_pass(cur)
    conn.commit()
    print(
        f"\nPass 2 done. inserted={inserted_2}, deleted={deleted_2}, "
        f"updated={updated_2}"
    )

    if inserted_2 != 0 or deleted_2 != 0 or updated_2 != 0:
        print(
            f"[ASSERT-FAIL] Pass 2 expected 0/0/0 but got "
            f"inserted={inserted_2}, deleted={deleted_2}, updated={updated_2}",
            file=sys.stderr,
        )
        conn.close()
        return 1

    print("[ASSERT-OK] Pass 2 reported 0 inserts, 0 deletes, 0 updates.")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
