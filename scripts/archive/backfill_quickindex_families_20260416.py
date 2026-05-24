"""Backfill family values on the 11 ungrouped QuickIndex LC problems.

Idempotent: re-running prints [SKIP] for rows already set and leaves them alone.
Only touches rows whose current family is NULL or empty string.

Target mapping is fixed in LC_FAMILY at the top of the file to match the
frontend FAMILY_LABELS groups introduced in T-P1-463.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_FAMILY: dict[int, str] = {
    215: "heap_topk",
    373: "heap_topk",
    127: "graph_bfs",
    269: "graph_topo_sort",
    200: "graph_grid_traversal",
    235: "tree_lca",
    212: "trie_multiword",
    15: "two_pointers_target",
    2503: "offline_queries_dsu",
    2791: "tree_dp_rerooting",
    2858: "tree_dp_rerooting",
}


def main() -> None:
    """Apply the family backfill once per run, printing a per-row action."""
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        pre_total = cur.execute(
            "SELECT COUNT(*) FROM problems "
            "WHERE family IS NOT NULL AND family != ''"
        ).fetchone()[0]

        set_count = 0
        skip_count = 0
        for lc_id, family in LC_FAMILY.items():
            row = cur.execute(
                "SELECT family FROM problems WHERE leetcode_id = ?",
                (lc_id,),
            ).fetchone()
            if row is None:
                print(f"[MISS] lc={lc_id} not found in problems table")
                continue
            current = row[0]
            if current is None or current == "":
                cur.execute(
                    "UPDATE problems SET family = ? "
                    "WHERE leetcode_id = ? AND (family IS NULL OR family = '')",
                    (family, lc_id),
                )
                print(f"[SET]  lc={lc_id} family={family}")
                set_count += 1
            elif current == family:
                print(f"[SKIP] lc={lc_id} family already set to {family}")
                skip_count += 1
            else:
                print(
                    f"[KEEP] lc={lc_id} has family={current!r} "
                    f"(would be {family}); leaving untouched"
                )
                skip_count += 1
        con.commit()

        post_total = cur.execute(
            "SELECT COUNT(*) FROM problems "
            "WHERE family IS NOT NULL AND family != ''"
        ).fetchone()[0]

    print("---")
    print(f"[DONE] set={set_count} skip={skip_count} "
          f"family_rows_pre={pre_total} family_rows_post={post_total} "
          f"delta={post_total - pre_total}")


if __name__ == "__main__":
    main()
