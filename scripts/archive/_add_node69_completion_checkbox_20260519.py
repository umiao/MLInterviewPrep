"""Idempotent fix for the node-69 no-checklist drift (T-P1-919).

Source: Discord user decision 2026-05-19 (msg 1506361186168606802) for the
T-P0-914 *no-checklist* drift bucket. SCOPE = node 69 ONLY
(``pillar2.supervised_learning.regularization`` "Regularization"):
``status='review'``/``progress_pct=100`` with **0/0 checkboxes** -- there
was no checklist to derive the 100 from. Explicitly NOT 115/171 (reverse,
that is T-P1-918) and NOT 92 (partial-stale).

Mechanism (user-directed): add >=1 GFM checkbox to the node description,
then re-derive status from checkbox state + propagate upward via the
tested T-P0-910 helper ``reconcile_node_from_checkboxes`` (REUSED, never
reimplemented). The box is added **checked**: the user framed it as
"确认已经学习完成", and the node was already ``review``/100 with
``completed_at`` set (human-endorsed done), so a checked box derives to
``mastered``/100 -- resolving the no-checklist drift while preserving the
"this is done" semantic. (An unchecked box would wrongly regress it to
``not_started``/0.)

Invariant 3: this git-tracked idempotent seed is the source of truth for
the description delta; the DB is a regenerable projection.

Idempotent: the SENTINEL substring is the canonical key. Re-running adds
nothing (section already present) and ``reconcile_node_from_checkboxes``
returns False when status/pct already match -> a clean no-op.

Run: python scripts/_add_node69_completion_checkbox_20260519.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib.framework_progress import (  # noqa: E402
    count_checkboxes,
    reconcile_node_from_checkboxes,
)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402

# Windows console is cp1252; the node description is Chinese. Force UTF-8
# stdout so the summary print never raises UnicodeEncodeError.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NODE_ID = 69
EXPECTED_PATH = "pillar2.supervised_learning.regularization"

# Canonical idempotency key -- the core checkbox text. If this substring is
# already in the description, the section was seeded; do not append again.
SENTINEL = "确认已系统学习并掌握本节点内容"

CONFIRM_SECTION = (
    "\n\n## 完成确认\n\n"
    "- [x] 确认已系统学习并掌握本节点内容"
    "（L1/L2 正则化、梯度行为、Elastic Net、"
    "Dropout / Early Stopping、AdamW Weight Decay 等核心要点）\n"
)

# Defensive scope guard: these MUST stay byte-unchanged (user excluded them).
OUT_OF_SCOPE = (115, 171, 92)


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        node = db.get(FrameworkNode, NODE_ID)
        if node is None:
            raise SystemExit(f"[FAIL] node {NODE_ID} not found")
        if node.path != EXPECTED_PATH:
            raise SystemExit(
                f"[FAIL] node {NODE_ID} path = {node.path!r}, "
                f"expected {EXPECTED_PATH!r} -- aborting (wrong node)"
            )

        oos_before = {
            nid: db.get(FrameworkNode, nid) for nid in OUT_OF_SCOPE
        }
        oos_snap = {
            nid: (n.status, n.progress_pct)
            for nid, n in oos_before.items()
            if n is not None
        }

        before = (node.status, node.progress_pct, count_checkboxes(node.description))
        already = SENTINEL in (node.description or "")

        if not already:
            node.description = (node.description or "").rstrip() + CONFIRM_SECTION
            db.flush()
            print(f"[ADD]  node {NODE_ID}: appended '## 完成确认' (1 checked box)")
        else:
            print(f"[SKIP] node {NODE_ID}: confirmation section already present")

        changed = reconcile_node_from_checkboxes(db, NODE_ID)
        db.commit()

        db.refresh(node)
        after = (node.status, node.progress_pct, count_checkboxes(node.description))
        print(f"[INFO] before: status={before[0]} pct={before[1]} boxes={before[2]}")
        print(f"[INFO] after : status={after[0]} pct={after[1]} boxes={after[2]} "
              f"(reconcile changed={changed})")

        # --- self-check (hard-fail; exit 2) ---
        chk, tot = after[2]
        if (tot, chk) != (1, 1):
            raise SystemExit(f"[FAIL] expected 1/1 boxes, got {chk}/{tot}")
        if after[0] != "mastered" or after[1] != 100.0:
            raise SystemExit(
                f"[FAIL] expected mastered/100.0, got {after[0]}/{after[1]}"
            )
        for nid, snap in oos_snap.items():
            n = db.get(FrameworkNode, nid)
            if (n.status, n.progress_pct) != snap:
                raise SystemExit(
                    f"[FAIL] OUT-OF-SCOPE node {nid} mutated: "
                    f"{snap} -> {(n.status, n.progress_pct)}"
                )
        print(f"[OK]   node {NODE_ID} = mastered/100.0 (1/1 checked); "
              f"out-of-scope {OUT_OF_SCOPE} byte-unchanged. Idempotent.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
