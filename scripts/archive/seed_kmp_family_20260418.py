"""Seed: T-P1-508 -- Tag KMP family on 4 existing problems.

Part A of KG-CONTENT-01. Tags these problems with
`family = 'string_matching_kmp'` so they show up under the new
"String Matching (KMP family)" group on Quick Index.

Problems (already in DB, no inserts):
  id=303, LC  28, Find the Index of the First Occurrence in a String
  id=344, LC 214, Shortest Palindrome
  id=672, LC 686, Repeated String Match
  id=352, LC 796, Rotate String

Idempotent: WHERE family IS NULL guard avoids clobbering future
reassignments. Running the script twice produces no additional
UPDATEs on the second run.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

FAMILY_SLUG = "string_matching_kmp"
PROBLEM_IDS = (303, 344, 672, 352)


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    conn = sqlite3.connect(str(DB_PATH))
    try:
        placeholders = ",".join("?" * len(PROBLEM_IDS))
        before = conn.execute(
            f"SELECT id, leetcode_id, title, family FROM problems "
            f"WHERE id IN ({placeholders}) ORDER BY id",
            PROBLEM_IDS,
        ).fetchall()
        if len(before) != len(PROBLEM_IDS):
            missing = set(PROBLEM_IDS) - {r[0] for r in before}
            print(f"[FAIL] Missing problem ids: {sorted(missing)}")
            return 1
        print("[INFO] Before:")
        for r in before:
            print(f"  id={r[0]} lc={r[1]} family={r[3]!r} -- {r[2]}")
        cur = conn.execute(
            f"UPDATE problems SET family = ? "
            f"WHERE id IN ({placeholders}) AND family IS NULL",
            (FAMILY_SLUG, *PROBLEM_IDS),
        )
        changed = cur.rowcount
        conn.commit()
        after = conn.execute(
            f"SELECT id, leetcode_id, title, family FROM problems "
            f"WHERE id IN ({placeholders}) ORDER BY id",
            PROBLEM_IDS,
        ).fetchall()
        print(f"[DONE] Updated {changed} row(s) -> family={FAMILY_SLUG!r}")
        print("[INFO] After:")
        for r in after:
            print(f"  id={r[0]} lc={r[1]} family={r[3]!r}")
        # Verify every target now has the family slug.
        mismatches = [r for r in after if r[3] != FAMILY_SLUG]
        if mismatches:
            print(f"[FAIL] Post-update mismatches: {mismatches}")
            return 1
        print(f"[PASS] All {len(after)} target problems have family={FAMILY_SLUG!r}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
