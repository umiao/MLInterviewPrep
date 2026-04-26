"""Schema invariant: framework_nodes path-separator convention (T-P0-609 / KG-FIX-01).

The 8 original pillars use '.' separators (e.g. 'pillar2.feature_engineering').
The ml-fundamentals subtree was authored with '/' separators
(e.g. 'ml-fundamentals/classical_ml/bias-variance-tradeoff'). Walking
parent_id back to depth=0 makes the slash convention work for KG rendering,
but the convention itself remains an exception that must be tracked.

This test enforces that:
  1. Every framework_node whose path contains '/' has a depth=0 ancestor
     in WHITELIST. New slash-path roots require explicit whitelist additions.
  2. Once T-P2-614 (KG-DESIGN-DUAL-VIEW) is marked completed, the WHITELIST
     must be empty -- the design decision either consolidates the dual root
     (no slash paths remain) OR ratifies it permanently (whitelist is no
     longer the right enforcement vehicle and should be replaced).

Skips if runtime DB data/mle_prep.db is not present.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
TASK_DB_CLI = REPO_ROOT / ".claude" / "hooks" / "task_db.py"

# TTL: remove after T-P2-614 (KG-DESIGN-DUAL-VIEW) lands a decision.
WHITELIST: set[str] = {"ml-fundamentals"}

pytestmark = pytest.mark.skipif(
    not DB_PATH.exists(), reason="runtime DB data/mle_prep.db not present"
)


def _root_path_of(conn: sqlite3.Connection, node_id: int) -> str | None:
    """Walk parent_id from node_id to depth=0 and return that root's path."""
    cur_id: int | None = node_id
    seen: set[int] = set()
    while cur_id is not None:
        if cur_id in seen:
            return None
        seen.add(cur_id)
        row = conn.execute(
            "SELECT parent_id, path FROM framework_nodes WHERE id=?",
            (cur_id,),
        ).fetchone()
        if row is None:
            return None
        parent_id, path = row
        if parent_id is None:
            return path
        cur_id = parent_id
    return None


def test_slash_paths_have_whitelisted_root() -> None:
    """Every slash-path node must trace back to a WHITELIST root.

    A new top-level taxonomy that uses '/' separators would otherwise slip in
    silently and recreate the original 'Other' bucket bug. To add a new
    slash-path root: extend WHITELIST AND add corresponding entries to
    PILLAR_STYLES (KG-FIX-02) and PILLAR_ORDER (KG-FIX-03).
    """
    with sqlite3.connect(str(DB_PATH)) as conn:
        slash_rows = conn.execute(
            "SELECT id, path FROM framework_nodes WHERE path LIKE '%/%'"
        ).fetchall()
        offenders: list[tuple[int, str, str | None]] = []
        for node_id, path in slash_rows:
            root_path = _root_path_of(conn, node_id)
            if root_path not in WHITELIST:
                offenders.append((node_id, path, root_path))

    assert not offenders, (
        f"slash-path nodes outside WHITELIST {sorted(WHITELIST)}: "
        f"{offenders}. Add the new root to WHITELIST + PILLAR_STYLES + "
        "PILLAR_ORDER, or migrate paths to dot-separator convention."
    )


def test_whitelist_emptied_when_dual_view_decision_lands() -> None:
    """Force whitelist cleanup once T-P2-614 closes.

    When KG-DESIGN-DUAL-VIEW completes, either (a) the slash subtree was
    consolidated (slash paths no longer exist) or (b) the dual root was
    ratified (whitelist is the wrong enforcement vehicle and must be removed
    in favour of a permanent rule). Either way, the WHITELIST sentinel
    should not survive the decision.
    """
    if not TASK_DB_CLI.exists():
        pytest.skip(f"task_db CLI not found at {TASK_DB_CLI}")

    result = subprocess.run(
        [sys.executable, str(TASK_DB_CLI), "get", "T-P2-614"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(
            f"task_db get T-P2-614 failed (rc={result.returncode}): "
            f"{result.stderr.strip()}"
        )

    try:
        task = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.skip(f"task_db output is not JSON: {exc}")

    status = task.get("status")
    if status == "completed":
        assert not WHITELIST, (
            "T-P2-614 (KG-DESIGN-DUAL-VIEW) is completed but the slash-path "
            f"WHITELIST is still non-empty: {sorted(WHITELIST)}. "
            "Remove WHITELIST entries (and this test if appropriate) per the "
            "design decision documented for T-P2-614."
        )
