"""Verify no question in communication/collaboration/leadership has only 1 link.

Exits 0 on success and prints a zero-remaining summary; exits 1 on failure.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
TARGET_CATEGORIES = ("communication", "collaboration", "leadership")


def main() -> int:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    rows = cur.execute(
        """
        SELECT q.question_id, q.category_id, COUNT(l.id) AS link_count
        FROM behavioral_questions q
        LEFT JOIN question_example_links l ON l.question_id = q.id
        WHERE q.category_id IN (?, ?, ?)
        GROUP BY q.id
        HAVING link_count = 1
        ORDER BY q.category_id, q.question_id
        """,
        TARGET_CATEGORIES,
    ).fetchall()

    offenders = [(r[0], r[1]) for r in rows]
    n_remaining = len(offenders)

    total_by_cat = dict(
        cur.execute(
            """
            SELECT q.category_id, COUNT(*)
            FROM behavioral_questions q
            WHERE q.category_id IN (?, ?, ?)
            GROUP BY q.category_id
            """,
            TARGET_CATEGORIES,
        ).fetchall()
    )

    con.close()

    print(
        f"[verify] total questions in target cats: "
        f"{sum(total_by_cat.values())} "
        f"(communication={total_by_cat.get('communication', 0)}, "
        f"collaboration={total_by_cat.get('collaboration', 0)}, "
        f"leadership={total_by_cat.get('leadership', 0)})"
    )

    if n_remaining:
        print(f"[verify] FAIL: {n_remaining} remaining single-link rows in target categories:")
        for qid, cat in offenders:
            print(f"  {qid} ({cat})")
        return 1

    print("[verify] 0 remaining single-link rows in target categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
