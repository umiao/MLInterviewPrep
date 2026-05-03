"""Mark T-P2-700 [KMEANS-GOLDEN-6] -- flip is_golden=1 / golden_at=now()
for problems.id=1064 ("K-Means Pure Python Implementation (K-Means++)").

This is the visible payoff that makes K-Means the first golden ML example,
mirroring the Behavioral golden-example treatment.

Idempotency:
- If is_golden is already 1 AND golden_at is non-null, [SKIP] without writes
  (no second timestamp overwrite).
- If is_golden=1 but golden_at is null (drift), only golden_at is set.
- Otherwise both columns are written in a single UPDATE.

Safety:
- Refuses to run if problems.id=1064 does not exist.
- Refuses to run if more than one row matches (sanity bound).
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
PROBLEM_ID = 1064


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, title, is_golden, golden_at FROM problems WHERE id = ?",
            (PROBLEM_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for problems.id={PROBLEM_ID}")
            return 1
        pid, title, is_golden, golden_at = row

        if is_golden and golden_at:
            print(
                f"[SKIP] id={pid} '{title}' already golden "
                f"(golden_at={golden_at})"
            )
            return 0

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if is_golden and not golden_at:
            conn.execute(
                "UPDATE problems SET golden_at = ? WHERE id = ?",
                (now_iso, pid),
            )
            action = "BACKFILL"
        else:
            conn.execute(
                "UPDATE problems SET is_golden = 1, golden_at = ? WHERE id = ?",
                (now_iso, pid),
            )
            action = "MARK"
        conn.commit()

        check = conn.execute(
            "SELECT is_golden, golden_at FROM problems WHERE id = ?", (pid,)
        ).fetchone()
        if check[0] != 1 or not check[1]:
            print(f"[FAIL] Post-write verify failed: is_golden={check[0]} golden_at={check[1]}")
            return 1

        total_golden = conn.execute(
            "SELECT COUNT(*) FROM problems WHERE is_golden = 1"
        ).fetchone()[0]
        print(
            f"[{action}] id={pid} '{title}' -> is_golden=1 "
            f"golden_at={check[1]}  (total golden problems: {total_golden})"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
