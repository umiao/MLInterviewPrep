"""Migration: add problems.family column + index, seed stateful-DS-design family.

AC (T-P1-187):
  (1) additive column `family` + index ix_problems_family.
  (2) insert 3 missing LC rows (1146, 1845, 1825).
  (3) set family='stateful_ds_design' for the 11-problem target set.

Descriptions for the 3 new rows are left NULL; run
`python scripts/backfill_lc_descriptions.py` afterward to populate them.

Usage:
    python scripts/migrate_add_problem_family.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

FAMILY_VALUE = "stateful_ds_design"

# (leetcode_id, title, url) for the 3 missing rows.
MISSING_ROWS = [
    (
        1146,
        "Snapshot Array",
        "https://leetcode.com/problems/snapshot-array/",
    ),
    (
        1845,
        "Seat Reservation Manager",
        "https://leetcode.com/problems/seat-reservation-manager/",
    ),
    (
        1825,
        "Finding MK Average",
        "https://leetcode.com/problems/finding-mk-average/",
    ),
]

TARGET_LC_IDS = [146, 362, 432, 460, 703, 716, 895, 1146, 1244, 1825, 1845]


def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(problems)")
    cols = {r[1] for r in cur.fetchall()}
    if "family" not in cols:
        cur.execute("ALTER TABLE problems ADD COLUMN family TEXT")
        print("[DONE] Added problems.family column")
    else:
        print("[SKIP] problems.family already exists")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_problems_family ON problems(family)")

    inserted = 0
    for lc_id, title, url in MISSING_ROWS:
        existing = cur.execute(
            "SELECT id FROM problems WHERE leetcode_id=?", (lc_id,)
        ).fetchone()
        if existing:
            print(f"[SKIP] LC {lc_id} row already present (id={existing[0]})")
            continue
        cur.execute(
            """INSERT INTO problems
               (leetcode_id, title, url, category, difficulty, is_completed,
                comfort_level, priority)
               VALUES (?, ?, ?, 'algorithm', NULL, 0, 0, 2)""",
            (lc_id, title, url),
        )
        inserted += 1
        print(f"[INSERT] LC {lc_id} {title}")

    cur.executemany(
        "UPDATE problems SET family=? WHERE leetcode_id=?",
        [(FAMILY_VALUE, lc) for lc in TARGET_LC_IDS],
    )
    conn.commit()

    rows = cur.execute(
        "SELECT leetcode_id, title FROM problems "
        "WHERE family=? ORDER BY leetcode_id",
        (FAMILY_VALUE,),
    ).fetchall()
    print(f"\n[VERIFY] family='{FAMILY_VALUE}' rows ({len(rows)}):")
    for r in rows:
        print(f"  {r[0]:>5}  {r[1]}")
    print(f"[SUMMARY] inserted={inserted}, family_rows={len(rows)}")
    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)
    print(f"Migrating database: {db_path}")
    migrate(db_path)
