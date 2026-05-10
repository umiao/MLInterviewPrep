"""Schema invariant: framework_nodes path-separator convention (T-P0-609 / KG-FIX-01).

The 8 original pillars use '.' separators (e.g. 'pillar2.feature_engineering').
The ml-fundamentals subtree uses '/' separators
(e.g. 'ml-fundamentals/classical_ml/bias-variance-tradeoff'). Both are
permanent top-level taxonomies of the KG dual-view design ratified by
T-P2-614 (see docs/design/kg_dual_view_decision_20260425.md). Walking
parent_id back to depth=0 in src/backend/routers/kg.py::_pillar_of() handles
both conventions transparently.

Per Section 2 of that decision, any future 3rd top-level taxonomy with a
slash separator (or any non-dot separator) must be ratified by an explicit
design doc and added to RATIFIED_SLASH_ROOTS below in the same change set
that extends frontend PILLAR_STYLES + PILLAR_ORDER. This file is the
single source of truth for that registry.

This test enforces that every framework_node whose path contains '/' has a
depth=0 ancestor in RATIFIED_SLASH_ROOTS. Unratified slash roots would
otherwise slip in silently and recreate the original 'Other' bucket bug
(KG-FIX-01..05).

Skips if runtime DB data/mle_prep.db is not present.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

# Permanent registry of ratified slash-separated top-level taxonomies.
# T-P2-614 (KG-DESIGN-DUAL-VIEW) ratified ml-fundamentals as a permanent root
# alongside the dot-separated pillar1..pillar8. T-P1-800 (KG-INT B2b) ratified
# meta-prep as the cross-company synthesis root per Section 2 Criterion A
# of docs/design/kg_dual_view_decision_20260425.md (decision doc:
# docs/design/kg_meta_prep_root_decision_20260510.md). To add a new entry,
# follow Section 2 (distinct cognitive mode + non-overlapping leaf set OR
# explicit alternate-projection) AND extend frontend PILLAR_STYLES +
# PILLAR_ORDER in the same change set.
RATIFIED_SLASH_ROOTS: set[str] = {"ml-fundamentals", "meta-prep"}

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


def test_slash_paths_have_ratified_root() -> None:
    """Every slash-path node must trace back to a RATIFIED_SLASH_ROOTS entry.

    Unratified slash-path roots would slip in silently and recreate the
    original 'Other' bucket bug fixed by KG-FIX-01..05. To add a new
    slash-path root: follow Section 2 of
    docs/design/kg_dual_view_decision_20260425.md (file a design doc + extend
    RATIFIED_SLASH_ROOTS + extend frontend PILLAR_STYLES + PILLAR_ORDER, all
    in the same change set).
    """
    with sqlite3.connect(str(DB_PATH)) as conn:
        slash_rows = conn.execute(
            "SELECT id, path FROM framework_nodes WHERE path LIKE '%/%'"
        ).fetchall()
        offenders: list[tuple[int, str, str | None]] = []
        for node_id, path in slash_rows:
            root_path = _root_path_of(conn, node_id)
            if root_path not in RATIFIED_SLASH_ROOTS:
                offenders.append((node_id, path, root_path))

    assert not offenders, (
        f"slash-path nodes outside RATIFIED_SLASH_ROOTS "
        f"{sorted(RATIFIED_SLASH_ROOTS)}: {offenders}. Either ratify the new "
        "root via the Section 2 process in "
        "docs/design/kg_dual_view_decision_20260425.md (extend the registry "
        "+ PILLAR_STYLES + PILLAR_ORDER), or migrate paths to the "
        "dot-separator convention."
    )


def test_dual_view_decision_doc_exists() -> None:
    """The dual-view ratification doc must remain in place.

    docs/design/kg_dual_view_decision_20260425.md is the canonical reference
    for the permanent dual-root design and the Section 2 process for adding
    further slash-separated roots. Removing it would orphan
    RATIFIED_SLASH_ROOTS and the _pillar_of() docstring that point to it.
    """
    decision_doc = REPO_ROOT / "docs" / "design" / "kg_dual_view_decision_20260425.md"
    assert decision_doc.exists(), (
        f"missing {decision_doc.relative_to(REPO_ROOT)}: this doc is "
        "referenced by RATIFIED_SLASH_ROOTS and src/backend/routers/kg.py "
        "::_pillar_of(). Restore it or update both references."
    )
