"""Restore canonical_hub HTML markers on framework_node 67 (Bias-Variance).

The CN-narration rewrite (commit 295ada1) regenerated node 67's description
from scratch in Chinese-narration style and dropped the leading HTML comment
block that consolidate_bias_variance_20260416.py originally seeded:

    <!-- doc_kind: canonical_hub -->
    <!-- canonical_topic: bias_variance -->
    <!-- KG_P2_01_BIAS_VARIANCE_20260416 -->

Without those markers, tests/test_bias_variance_canonical_hub.py fails on
test_node_67_has_canonical_hub_marker. Re-running the original consolidate
script would overwrite the new CN content back to the pre-CN English version,
which is not what we want. This script instead re-prepends the markers
in-place, preserving the CN body.

Idempotent: detects sentinel presence and skips if already repaired.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
NODE_ID = 67
MARKERS = (
    "<!-- doc_kind: canonical_hub -->\n"
    "<!-- canonical_topic: bias_variance -->\n"
    "<!-- KG_P2_01_BIAS_VARIANCE_20260416 -->\n"
)
SENTINEL = "<!-- KG_P2_01_BIAS_VARIANCE_20260416 -->"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not DB.exists():
        print(f"[SKIP] DB not present: {DB}")
        return 0
    conn = sqlite3.connect(str(DB))
    try:
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE id=?",
            (NODE_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] node {NODE_ID} not found")
            return 1
        desc: str = row[0]
        if SENTINEL in desc:
            print(f"[UNCHANGED] node {NODE_ID} already has sentinel")
            return 0
        new_desc = MARKERS + desc
        conn.execute(
            "UPDATE framework_nodes SET description=? WHERE id=?",
            (new_desc, NODE_ID),
        )
        conn.commit()
        print(
            f"[OK] node {NODE_ID} markers restored "
            f"(len {len(desc)} -> {len(new_desc)})"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
