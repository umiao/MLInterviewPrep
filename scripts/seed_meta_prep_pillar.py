"""Seed: T-P1-800 [KG-INT B2b] -- meta-prep pillar + 5 sub-node stubs.

Creates a new depth-0 framework_nodes pillar `meta-prep` and 5 depth-1
children that hold cross-company shared substrate (KG-INT B3 fills the
content):

  root  depth=0  path='meta-prep'   title='Cross-Company Interview Meta-Knowledge'
    sub   depth=1  path='meta-prep/behavioral-clusters'
    sub   depth=1  path='meta-prep/lc-keyword-checklists'
    sub   depth=1  path='meta-prep/system-design-must-knows'
    sub   depth=1  path='meta-prep/onsite-loop-templates'
    sub   depth=1  path='meta-prep/code-pad-best-practices'

The descriptions on the 5 sub-nodes are one-line stubs flagged
`TODO[KG-INT-B3-*]` so the B3 follow-up tasks (T-P1-803..T-P1-807) can
locate and replace them. The root description is left NULL to match the
existing depth-0 pillar convention (only `pillar1` has an empty-string
description; pillar2-8 + ml-fundamentals are NULL).

Safety:
  1. SHA-256 of all 'meta-prep%' rows captured pre/post for audit.
  2. Refuses to run if any target path already exists with a DIFFERENT
     title (protects against accidental overwrite of human edits).
  3. Idempotent: a node whose path+title already match is SKIPPED, not
     UPDATED. Second run yields inserted=0, skipped=6.
  4. Post-run invariant: exactly 6 rows match path = 'meta-prep' OR
     path LIKE 'meta-prep/%'.

Usage:
    python scripts/seed_meta_prep_pillar.py
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

ROOT_PATH = "meta-prep"
ROOT_TITLE = "Cross-Company Interview Meta-Knowledge"

SUBNODES: list[tuple[str, str, str]] = [
    (
        "behavioral-clusters",
        "Behavioral Story Clusters",
        "TODO[KG-INT-B3-1]: shared behavioral story clusters "
        "(failure, conflict, leadership, ambiguity, scope) "
        "consolidated from per-company BQ docs.",
    ),
    (
        "lc-keyword-checklists",
        "LC Keyword Checklists",
        "TODO[KG-INT-B3-4]: cross-company LeetCode keyword checklists "
        "(pattern names + trigger phrases) consolidated from per-company "
        "LC notes.",
    ),
    (
        "system-design-must-knows",
        "System Design Must-Knows",
        "TODO[KG-INT-B3-2]: shared ML system design vocabulary "
        "(retrieval, ranking, calibration, drift, online/offline eval) "
        "consolidated from per-company SD docs.",
    ),
    (
        "onsite-loop-templates",
        "Onsite Loop Templates",
        "TODO[KG-INT-B3-5]: common onsite loop structures and round-type "
        "playbooks (coding, BQ, ML breadth, MLSD) consolidated from "
        "per-company onsite docs.",
    ),
    (
        "code-pad-best-practices",
        "AI-Native Code-Pad Best Practices",
        "TODO[KG-INT-B3-3]: AI-native pair-programming code-pad practices "
        "(dictation discipline, plain-text formula reading, env setup) "
        "consolidated from per-company code-pad notes.",
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """Return SHA-256 of all 'meta-prep' subtree rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/%' "
        "ORDER BY path",
        (ROOT_PATH,),
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def upsert_node(
    conn: sqlite3.Connection,
    *,
    path: str,
    depth: int,
    title: str,
    description: str | None,
    parent_id: int | None,
    importance: float,
) -> tuple[str, int]:
    """Insert if absent, skip if present with matching title, refuse on title conflict.

    Returns (action, node_id) where action is 'INSERTED' or 'SKIPPED'.
    """
    existing = conn.execute(
        "SELECT id, title FROM framework_nodes WHERE path = ?", (path,)
    ).fetchone()
    if existing is not None:
        node_id, existing_title = existing
        if existing_title != title:
            raise RuntimeError(
                f"[CONFLICT] path={path!r} exists with title={existing_title!r}, "
                f"refusing to overwrite with {title!r}"
            )
        return "SKIPPED", node_id
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, depth, title, description,
         importance, "P1", "not_started", 0.0),
    )
    return "INSERTED", cur.lastrowid


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Seed root + 5 sub-node stubs. Returns action counts."""
    counts = {"INSERTED": 0, "SKIPPED": 0}

    action, root_id = upsert_node(
        conn,
        path=ROOT_PATH,
        depth=0,
        title=ROOT_TITLE,
        description=None,
        parent_id=None,
        importance=0.9,
    )
    counts[action] += 1
    print(f"[{action}] root id={root_id} path={ROOT_PATH}")

    for slug, title, description in SUBNODES:
        path = f"{ROOT_PATH}/{slug}"
        action, sub_id = upsert_node(
            conn,
            path=path,
            depth=1,
            title=title,
            description=description,
            parent_id=root_id,
            importance=0.8,
        )
        counts[action] += 1
        print(f"[{action}] sub  id={sub_id} path={path}")

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes "
            "WHERE path = ? OR path LIKE 'meta-prep/%'",
            (ROOT_PATH,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(f"[SUMMARY] inserted={counts['INSERTED']} "
          f"skipped={counts['SKIPPED']} "
          f"total_in_subtree={total}")

    expected_total = 1 + len(SUBNODES)
    if total != expected_total:
        print(
            f"[FAIL] Expected {expected_total} rows under meta-prep, got {total}"
        )
        sys.exit(1)
    if counts["INSERTED"] + counts["SKIPPED"] != expected_total:
        print(
            f"[FAIL] Expected to touch {expected_total} nodes, "
            f"touched {counts['INSERTED'] + counts['SKIPPED']}"
        )
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
