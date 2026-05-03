"""Mark T-P0-705 [MLI-GOLDEN-PROMOTE] -- flip is_golden=1 / golden_at=now()
for the 4 ML problems whose notes were rewritten under T-P0-701..704:

    1102  Linear Regression (closed-form lstsq + GD)
    1106  K-Nearest Neighbors (uniform + distance-weighted)
    1107  Logistic Regression (Sigmoid + Stable BCE + GD)
    1108  Geometric Median (Weiszfeld + Vardi-Zhang variant)

Mirrors `scripts/mark_kmeans_golden_20260502.py` (T-P2-699) -- same
idempotency policy and safety bounds, batched for 4 ids in one transaction.

Idempotency:
- If is_golden is already 1 AND golden_at is non-null, [SKIP] (no overwrite).
- If is_golden=1 but golden_at is null (drift), only golden_at is set.
- Otherwise both columns are written.

Safety:
- Refuses to run if any of the 4 problems is missing.
- Single transaction; partial failure rolls back all 4.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
PROBLEM_IDS = (1102, 1106, 1107, 1108)


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        rows = conn.execute(
            f"SELECT id, title, is_golden, golden_at FROM problems "
            f"WHERE id IN ({','.join('?' * len(PROBLEM_IDS))}) "
            f"ORDER BY id",
            PROBLEM_IDS,
        ).fetchall()
        found_ids = {r[0] for r in rows}
        missing = set(PROBLEM_IDS) - found_ids
        if missing:
            print(f"[FAIL] Missing problems: {sorted(missing)}")
            return 1

        now_iso = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        actions: list[tuple[int, str, str]] = []

        for pid, title, is_golden, golden_at in rows:
            if is_golden and golden_at:
                actions.append((pid, title, "SKIP"))
                continue
            if is_golden and not golden_at:
                conn.execute(
                    "UPDATE problems SET golden_at = ? WHERE id = ?",
                    (now_iso, pid),
                )
                actions.append((pid, title, "BACKFILL"))
            else:
                conn.execute(
                    "UPDATE problems SET is_golden = 1, golden_at = ? "
                    "WHERE id = ?",
                    (now_iso, pid),
                )
                actions.append((pid, title, "MARK"))

        conn.commit()

        check = conn.execute(
            f"SELECT id, is_golden, golden_at FROM problems "
            f"WHERE id IN ({','.join('?' * len(PROBLEM_IDS))})",
            PROBLEM_IDS,
        ).fetchall()
        bad = [r for r in check if r[1] != 1 or not r[2]]
        if bad:
            print(f"[FAIL] Post-write verify failed for: {bad}")
            return 1

        for pid, title, action in actions:
            print(f"[{action}] id={pid} '{title}'")

        total_golden = conn.execute(
            "SELECT COUNT(*) FROM problems WHERE is_golden = 1"
        ).fetchone()[0]
        print(f"[OK] total golden problems: {total_golden}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
