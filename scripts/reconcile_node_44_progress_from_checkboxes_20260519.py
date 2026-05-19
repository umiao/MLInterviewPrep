"""Reconcile n44 (Array/String) progress/status with its checkbox state.

Source: Discord 2026-05-19 -- "http://localhost:5173/framework/44/notes
依然在KG - Framework里没有正确的显示为completed".

Root cause (data drift, NOT a code bug): node 44's Key Takeaways were
all checked by scripts/update_node_44_link_questions_check_takeaways_
20260519.py, which writes framework_nodes.description DIRECTLY to the DB.
The progress->status mechanism only runs on the API PUT path
(useFrameworkNotes.handleCheckboxClick computes progress_pct from the
checked ratio -> PUT -> routers/framework.py derives status). A direct
description write bypasses it, so node 44 stayed
status='not_started', progress_pct=0.0 while showing 5/5 checked. The
KG-Framework view colours/labels by `status`, so it rendered "Not
Started" (red) instead of "Mastered" (green = completed).

Fix: do exactly what the backend PUT does for a progress_pct=100
checkbox-driven update (routers/framework.py L212-227), then call the
REAL _propagate_upward() so ancestors (9 Data Structures, 1 Coding &
Algorithms) are recomputed by the production weighted-average + status
derivation -- imported, never re-implemented (CLAUDE.md: no duplicate
utilities; guarantees the rollup matches prod exactly).

Scope: this script owns ONLY node 44's reconciliation. The DB-wide
audit also flagged nodes 111 and 114 with milder drift; those are left
for an explicit user decision (114='review' may be intentional).

Safety:
  1. Timestamped .bak of mle_prep.db before any write.
  2. Idempotent: if node 44 is already mastered/100/completed and the
     ancestor chain is no longer all not_started, a re-run is a clean
     [SKIP] -- no .bak, no write.
  3. Post-write verification: node 44 == mastered/100/completed_at set;
     ancestors no longer not_started.

Run: python scripts/reconcile_node_44_progress_from_checkboxes_20260519.py
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402
from src.backend.routers.framework import _propagate_upward  # noqa: E402

NODE_ID = 44
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"


def backup_db() -> Path:
    """Copy the live DB to a timestamped .bak beside it. Returns the path."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


def ancestor_chain(db, node_id: int) -> list[FrameworkNode]:
    """Return [parent, grandparent, ...] for node_id (excludes the node)."""
    chain: list[FrameworkNode] = []
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    seen: set[int] = set()
    pid = node.parent_id if node else None
    while pid is not None and pid not in seen:
        seen.add(pid)
        p = db.query(FrameworkNode).filter(FrameworkNode.id == pid).first()
        if not p:
            break
        chain.append(p)
        pid = p.parent_id
    return chain


def main() -> int:
    """Reconcile node 44 + propagate. Idempotent; verifies post-write."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    init_db()  # binds SessionLocal to settings.DATABASE_URL (data/mle_prep.db)
    db = SessionLocal()
    try:
        node = db.query(FrameworkNode).filter(
            FrameworkNode.id == NODE_ID
        ).first()
        if not node:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            return 1

        anc = ancestor_chain(db, NODE_ID)
        anc_all_not_started = all(a.status == "not_started" for a in anc)

        already_good = (
            node.status == "mastered"
            and (node.progress_pct or 0.0) == 100.0
            and node.completed_at is not None
            and not anc_all_not_started
        )
        if already_good:
            print(
                f"[SKIP] Node {NODE_ID} already mastered/100/completed and "
                f"ancestors propagated. status={node.status} "
                f"pct={node.progress_pct} completed_at={node.completed_at}"
            )
            return 0

        print(
            f"[INFO] Before: node {NODE_ID} status={node.status} "
            f"pct={node.progress_pct} started_at={node.started_at} "
            f"completed_at={node.completed_at}"
        )
        for a in anc:
            print(
                f"[INFO]   ancestor {a.id} {a.title!r} "
                f"status={a.status} pct={a.progress_pct}"
            )

        backup_db()

        # Replicate routers/framework.py L212-227 for a progress_pct=100
        # checkbox-driven PUT (status derived -> 'mastered' side effects).
        now = datetime.utcnow()
        node.progress_pct = 100.0
        node.status = "mastered"
        if node.started_at is None:
            node.started_at = now
        if node.completed_at is None:
            node.completed_at = now

        # Reuse the production rollup so ancestors match prod exactly.
        _propagate_upward(NODE_ID, db)
        db.commit()

        # Verify.
        db.refresh(node)
        ok = (
            node.status == "mastered"
            and (node.progress_pct or 0.0) == 100.0
            and node.completed_at is not None
        )
        if not ok:
            print(
                f"[FAIL] Post-write node {NODE_ID} not reconciled: "
                f"status={node.status} pct={node.progress_pct} "
                f"completed_at={node.completed_at}"
            )
            return 1
        for a in ancestor_chain(db, NODE_ID):
            db.refresh(a)
            print(
                f"[PASS]   ancestor {a.id} {a.title!r} -> "
                f"status={a.status} pct={a.progress_pct}"
            )
        print(
            f"[PASS] Node {NODE_ID} reconciled: status=mastered "
            f"pct=100.0 completed_at={node.completed_at}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
