"""Sync Pinterest VO (2026-05-05 + 2026-05-06) interview_events to canonical set.

Idempotent: re-running deletes any "Pinterest VO Day" rows that don't match the
canonical set below and inserts/updates rows to match. Safe to re-run.

Canonical key per row: (company_id, scheduled_at, interviewer_name) where
interviewer_name is parsed from the trailing "| <Interviewer>" suffix in title.
This is more stable than title-as-key because round labels (e.g. "ML Systems
Design" vs "ML SD") may be edited later without breaking uniqueness.

Source: VO schedule confirmed 2026-04-29 (Pinterest VO May 5-6); interviewer
roster + CoderPad links updated 2026-05-04 from emails 5 + 6 (Day 1 R1
Yiyang Zhang -> Xiao Su; Day 2 R1 Jiankai Sun -> Eric Kim; Day 2 R2
Yijian Xiang -> Paulo Soares; CoderPad URLs added to all 5 rounds).
Timezone: naive Pacific time (PDT = GMT-07:00 on 2026-05-05 / 2026-05-06),
per project convention.

Modes:
  default: sync canonical set; embedded second pass asserts idempotency.
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
TITLE_PREFIX = "Pinterest VO Day"

EVENTS = [
    {
        "event_type": "system_design",
        "title": "Pinterest VO Day 1 R1 -- ML Systems Design | Xiao Su",
        "description": (
            "Pinterest virtual onsite - Day 1, Round 1.\n"
            "Tuesday 2026-05-05, 3:00-4:00 PM PDT (GMT-07:00).\n"
            "ML Systems Design.\n"
            "Interviewer: Xiao Su (Sr. Machine Learning Engineer).\n"
            "Platform: Zoom.\n"
            "CoderPad: https://app.coderpad.io/6M4XZEG9\n"
            "Reference: company_documents id=83 (Pinterest VO prep doc)."
        ),
        "scheduled_at": "2026-05-05 15:00:00",
        "duration_minutes": 60,
    },
    {
        "event_type": "behavioral",
        "title": "Pinterest VO Day 1 R2 -- HM/Competency | Daniel Liu",
        "description": (
            "Pinterest virtual onsite - Day 1, Round 2.\n"
            "Tuesday 2026-05-05, 4:00-4:45 PM PDT (GMT-07:00).\n"
            "Hiring Manager / Competency (behavioral).\n"
            "Interviewer: Daniel Liu (Manager II, Machine Learning Engineering).\n"
            "Platform: Zoom.\n"
            "CoderPad: https://app.coderpad.io/AQD3MMCC\n"
            "Reference: company_documents id=83 (Pinterest VO prep doc)."
        ),
        "scheduled_at": "2026-05-05 16:00:00",
        "duration_minutes": 45,
    },
    {
        "event_type": "technical",
        "title": "Pinterest VO Day 2 R1 -- Data/Algos | Eric Kim",
        "description": (
            "Pinterest virtual onsite - Day 2, Round 1.\n"
            "Wednesday 2026-05-06, 1:00-1:45 PM PDT (GMT-07:00).\n"
            "Data Structures & Algorithms (coding).\n"
            "Interviewer: Eric Kim (Staff Machine Learning Engineer).\n"
            "Platform: Zoom.\n"
            "CoderPad: https://app.coderpad.io/YNE499CY\n"
            "Note: 15-min break before Day 2 R2.\n"
            "Reference: company_documents id=83 (Pinterest VO prep doc)."
        ),
        "scheduled_at": "2026-05-06 13:00:00",
        "duration_minutes": 45,
    },
    {
        "event_type": "technical",
        "title": "Pinterest VO Day 2 R2 -- Data/Algos | Paulo Soares",
        "description": (
            "Pinterest virtual onsite - Day 2, Round 2.\n"
            "Wednesday 2026-05-06, 2:00-2:45 PM PDT (GMT-07:00).\n"
            "Data Structures & Algorithms (coding).\n"
            "Interviewer: Paulo Soares (he/him, Sr. Machine Learning Engineer).\n"
            "Platform: Zoom.\n"
            "CoderPad: https://app.coderpad.io/2RDZ3QD3\n"
            "Note: 15-min break before Day 2 R3.\n"
            "Reference: company_documents id=83 (Pinterest VO prep doc)."
        ),
        "scheduled_at": "2026-05-06 14:00:00",
        "duration_minutes": 45,
    },
    {
        "event_type": "technical",
        "title": "Pinterest VO Day 2 R3 -- ML Practitioner | Zihao Zhang",
        "description": (
            "Pinterest virtual onsite - Day 2, Round 3.\n"
            "Wednesday 2026-05-06, 3:00-4:00 PM PDT (GMT-07:00).\n"
            "ML Practitioner (applied ML coding/discussion).\n"
            "Interviewer: Zihao Zhang (he/him, Sr. Machine Learning Engineer).\n"
            "Platform: Zoom.\n"
            "CoderPad: https://app.coderpad.io/AWAF43ZX\n"
            "Reference: company_documents id=83 (Pinterest VO prep doc)."
        ),
        "scheduled_at": "2026-05-06 15:00:00",
        "duration_minutes": 60,
    },
]


def parse_interviewer(title: str) -> str:
    """Extract interviewer name from the trailing '| <Interviewer>' suffix."""
    if "|" not in title:
        raise ValueError(f"title missing '| <Interviewer>' suffix: {title!r}")
    return title.rsplit("|", 1)[1].strip()


def sync_pass(cur: sqlite3.Cursor) -> tuple[int, int, int]:
    """Run one sync pass against the canonical EVENTS list.

    Canonical key is (company_id, scheduled_at, interviewer_name). We match
    existing rows by (scheduled_at, interviewer_name) and update title +
    metadata; rows whose interviewer name does not appear in EVENTS are deleted.

    Returns (inserted, deleted, updated).
    """
    canonical_by_key = {
        (ev["scheduled_at"], parse_interviewer(ev["title"])): ev for ev in EVENTS
    }

    cur.execute(
        "SELECT id, scheduled_at, title FROM interview_events "
        "WHERE company_id = ? AND title LIKE ?",
        (PINTEREST_COMPANY_ID, f"{TITLE_PREFIX}%"),
    )
    existing_rows = cur.fetchall()
    existing_keys: set[tuple[str, str]] = set()
    deleted = 0
    for row_id, sched, title in existing_rows:
        try:
            interviewer = parse_interviewer(title)
        except ValueError:
            cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
            print(f"[DELETE] id={row_id}: {title} @ {sched} (unparseable)")
            deleted += 1
            continue
        key = (sched, interviewer)
        if key in canonical_by_key:
            existing_keys.add(key)
            continue
        cur.execute("DELETE FROM interview_events WHERE id = ?", (row_id,))
        print(f"[DELETE] id={row_id}: {title} @ {sched} (not in canonical)")
        deleted += 1

    inserted = 0
    updated = 0
    for ev in EVENTS:
        interviewer = parse_interviewer(ev["title"])
        key = (ev["scheduled_at"], interviewer)
        if key in existing_keys:
            cur.execute(
                "SELECT title, description, event_type, duration_minutes, "
                "location, status FROM interview_events "
                "WHERE company_id = ? AND scheduled_at = ? AND title LIKE ?",
                (
                    PINTEREST_COMPANY_ID,
                    ev["scheduled_at"],
                    f"%| {interviewer}",
                ),
            )
            current = cur.fetchone()
            target = (
                ev["title"],
                ev["description"],
                ev["event_type"],
                ev["duration_minutes"],
                LOCATION,
                STATUS,
            )
            if current == target:
                print(f"[UNCHANGED] {ev['title']} @ {ev['scheduled_at']}")
                continue
            cur.execute(
                "UPDATE interview_events SET title = ?, description = ?, "
                "event_type = ?, duration_minutes = ?, location = ?, status = ? "
                "WHERE company_id = ? AND scheduled_at = ? AND title LIKE ?",
                (
                    ev["title"],
                    ev["description"],
                    ev["event_type"],
                    ev["duration_minutes"],
                    LOCATION,
                    STATUS,
                    PINTEREST_COMPANY_ID,
                    ev["scheduled_at"],
                    f"%| {interviewer}",
                ),
            )
            print(f"[UPDATE] {ev['title']} @ {ev['scheduled_at']}")
            updated += 1
            continue

        cur.execute(
            "INSERT INTO interview_events ("
            "company_id, company_name, event_type, title, description, "
            "scheduled_at, duration_minutes, location, status"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                PINTEREST_COMPANY_ID,
                PINTEREST_COMPANY_NAME,
                ev["event_type"],
                ev["title"],
                ev["description"],
                ev["scheduled_at"],
                ev["duration_minutes"],
                LOCATION,
                STATUS,
            ),
        )
        print(f"[INSERT] id={cur.lastrowid}: {ev['title']} @ {ev['scheduled_at']}")
        inserted += 1

    return inserted, deleted, updated


def verify(cur: sqlite3.Cursor) -> int:
    """Read-only verification: 5 canonical rows present, no drift.

    Returns 0 on success, non-zero exit code on drift.
    """
    canonical_by_key = {
        (ev["scheduled_at"], parse_interviewer(ev["title"])): ev for ev in EVENTS
    }
    cur.execute(
        "SELECT scheduled_at, title, event_type, duration_minutes, status "
        "FROM interview_events WHERE company_id = ? AND title LIKE ? "
        "ORDER BY scheduled_at",
        (PINTEREST_COMPANY_ID, f"{TITLE_PREFIX}%"),
    )
    rows = cur.fetchall()
    if len(rows) != len(EVENTS):
        print(
            f"[VERIFY-FAIL] expected {len(EVENTS)} rows, got {len(rows)}",
            file=sys.stderr,
        )
        return 1

    drift = 0
    matched = 0
    for sched, title, event_type, duration, status in rows:
        try:
            interviewer = parse_interviewer(title)
        except ValueError:
            print(f"[VERIFY-FAIL] unparseable title: {title!r}", file=sys.stderr)
            drift += 1
            continue
        key = (sched, interviewer)
        ev = canonical_by_key.get(key)
        if ev is None:
            print(
                f"[VERIFY-FAIL] unexpected row: {title} @ {sched}",
                file=sys.stderr,
            )
            drift += 1
            continue
        if (
            title != ev["title"]
            or event_type != ev["event_type"]
            or duration != ev["duration_minutes"]
            or status != STATUS
        ):
            print(
                f"[VERIFY-FAIL] drift on {title} @ {sched}: "
                f"got event_type={event_type!r}, duration={duration!r}, "
                f"status={status!r}",
                file=sys.stderr,
            )
            drift += 1
            continue
        matched += 1
        print(f"[OK] {title} @ {sched}")

    if drift:
        print(f"[VERIFY-FAIL] drift={drift}", file=sys.stderr)
        return 1
    print(f"[VERIFY-OK] {matched}/{len(EVENTS)} rows match canonical, drift=0")
    return 0


def main() -> int:
    """Sync Pinterest VO rows; embedded second pass asserts idempotency."""
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

    print("=== Pass 1: sync canonical set ===")
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
