"""Seed Google R2 Coding link to LC 778 'Swim in Rising Water'.

User-requested indexing only (Discord 2026-05-07 msg 1501810532360130685,
"同理 把778 LC也给加到google的那个index上面去"). LC 778 row already exists
(problems.id=116, leetcode_id=778, hard, company_tags=[LinkedIn,Uber,Adobe])
with a solid existing 题解 (Dijkstra minimax + alt binary-search/UF +
LC 1631/1102 follow-ups). User did NOT request a notes rewrite -- this
seed leaves notes untouched and only does metadata + index work.

Changes:

  1. Merge Google into `problems.company_tags` (preserves existing
     LinkedIn/Uber/Adobe surface).
  2. Set `family='graph'` (was NULL) and upgrade `pattern` from generic
     `'graph'` to `'dijkstra-minimax'` (more informative; consistent with
     specific patterns used by sibling rows in doc 92, e.g.
     `'rollback-dsu'`, `'circular-allocation-heap'`).
  3. Notes left untouched (the existing 1505-char writeup is canonical).

The R2 Coding Index doc 92 is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this
commit to add a NEW `### Graph / Dijkstra` section (between
`### Graph / 连通分量` and `### Tree / Graph Validation`) -- the existing
`### Graph / 连通分量` section is connectivity-flavored (BFS/DSU), not
shortest-path; LC 778 belongs to a different algorithm family. The new
section is forward-compatible: LC 1631 'Path With Minimum Effort' and
LC 1102 'Path With Maximum Minimum Value' (already in user's notes as
follow-ups) can land there later.

Idempotent. leetcode_id=778 is the canonical key. First run on the
existing row: 1 UPDATE (3 fields). Re-run on identical state: 0 writes.

Run: python scripts/seed_google_r2_lc778_swim_rising_water_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 778
SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS_TO_ADD = ["Google"]

PATTERN = "dijkstra-minimax"
FAMILY = "graph"


def _select_existing(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, pattern, family, source, company_tags "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
    ).fetchone()
    if row is None:
        return None
    keys = ["id", "pattern", "family", "source", "company_tags"]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _merge_company_tags(current_json: str | None, add_list: list[str]) -> str:
    """Append each tag in add_list to JSON-encoded list if not present."""
    cur = json.loads(current_json) if current_json else []
    for t in add_list:
        if t not in cur:
            cur.append(t)
    return json.dumps(cur, ensure_ascii=False)


def upsert(conn: sqlite3.Connection) -> tuple[int, str]:
    """UPDATE LC 778 metadata. Notes are NOT touched. Return (id, action)."""
    existing = _select_existing(conn, LEETCODE_ID)
    if existing is None:
        raise SystemExit(
            f"[FAIL] problems.leetcode_id={LEETCODE_ID} missing -- "
            "the bulk LC seed must run first"
        )
    pid, current = existing

    target = {
        "pattern": PATTERN,
        "family": FAMILY,
        "source": SOURCE_LABEL,
        "company_tags": _merge_company_tags(
            current.get("company_tags"), COMPANY_TAGS_TO_ADD
        ),
    }
    drift = {f: target[f] for f in target if current.get(f) != target[f]}
    if not drift:
        return pid, "UNCHANGED"

    set_clauses = ", ".join(f"{f} = ?" for f in drift)
    values = list(drift.values()) + [pid]
    conn.execute(
        f"UPDATE problems SET {set_clauses} WHERE id = ?",
        values,
    )
    return pid, "UPDATED"


def main() -> int:
    """Update LC 778 metadata + Google linkage. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc778_swim_rising")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert(conn)
        print(f"[{action}] problem id={pid} leetcode_id={LEETCODE_ID}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
