"""Seed: T-P1-509 -- Insert LC 1392 "Longest Happy Prefix" into problems table.

Adds the purest teaching example of KMP's next-array semantics to the
`string_matching_kmp` family. The answer IS `kmp[n-1]`: compute the
next-array on the input string and return `s[n - kmp[n-1]:]`, no main
matching loop required.

Idempotent: INSERT OR IGNORE on `leetcode_id=1392`; if the row already
exists, a second-pass UPDATE ensures `family='string_matching_kmp'` only
when family is currently NULL (never clobbers a deliberate reassignment).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

LEETCODE_ID = 1392
TITLE = "Longest Happy Prefix"
URL = "https://leetcode.com/problems/longest-happy-prefix/"
DIFFICULTY = "hard"
FAMILY_SLUG = "string_matching_kmp"
SOURCE = "algorithm"


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1
    conn = sqlite3.connect(str(DB_PATH))
    try:
        existing = conn.execute(
            "SELECT id, leetcode_id, title, family, difficulty, url "
            "FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if existing:
            pid, lc, title, family, diff, url = existing
            print(f"[INFO] LC {lc} already in DB: id={pid} "
                  f"family={family!r} difficulty={diff!r}")
            if family is None:
                conn.execute(
                    "UPDATE problems SET family = ? "
                    "WHERE id = ? AND family IS NULL",
                    (FAMILY_SLUG, pid),
                )
                conn.commit()
                print(f"[DONE] Backfilled family={FAMILY_SLUG!r} on id={pid}")
            elif family != FAMILY_SLUG:
                print(f"[WARN] family mismatch: found {family!r}, "
                      f"expected {FAMILY_SLUG!r}. Not modified.")
            else:
                print(f"[SKIP] Row already has family={FAMILY_SLUG!r}")
            new_id = pid
        else:
            cur = conn.execute(
                "INSERT INTO problems "
                "(leetcode_id, title, url, difficulty, family, "
                " source, is_completed) "
                "VALUES (?, ?, ?, ?, ?, ?, 0)",
                (LEETCODE_ID, TITLE, URL, DIFFICULTY, FAMILY_SLUG, SOURCE),
            )
            conn.commit()
            new_id = cur.lastrowid
            print(f"[DONE] Inserted LC {LEETCODE_ID} as id={new_id} "
                  f"family={FAMILY_SLUG!r}")

        # Post-state verification.
        row = conn.execute(
            "SELECT id, leetcode_id, title, family, difficulty, url "
            "FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if not row:
            print("[FAIL] Row vanished after insert/update")
            return 1
        if row[3] != FAMILY_SLUG:
            print(f"[FAIL] Post-state family mismatch: {row[3]!r} "
                  f"!= {FAMILY_SLUG!r}")
            return 1
        print(f"[PASS] id={row[0]} lc={row[1]} family={row[3]!r} "
              f"difficulty={row[4]!r}")
        print(f"[INFO] Use dbId={row[0]} in QuickIndex.tsx LC_PROBLEMS entry")

        # Family group audit.
        group = conn.execute(
            "SELECT leetcode_id, title FROM problems "
            "WHERE family = ? ORDER BY leetcode_id",
            (FAMILY_SLUG,),
        ).fetchall()
        print(f"[INFO] {FAMILY_SLUG} group now has {len(group)} problems:")
        for lc, title in group:
            print(f"  LC {lc:>4} -- {title}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
