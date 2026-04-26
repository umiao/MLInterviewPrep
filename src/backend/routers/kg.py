"""Knowledge graph API: framework nodes + concept_links edges.

POC scope (KG-VIZ-01): emits framework_nodes as graph nodes and concept_links
rows as edges. Pillar grouping is derived by walking parent_id back to the
depth=0 ancestor and using that ancestor's path string. This is
taxonomy-agnostic and works regardless of path-separator convention.
If concept_links is empty, a small set of synthetic parent->child edges is
returned so the frontend POC has at least some non-tree wiring to render.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.framework import FrameworkNode

router = APIRouter()


def _pillar_of(
    node: FrameworkNode | None,
    nodes_by_id: dict[int, FrameworkNode],
) -> str | None:
    """Walk parent_id chain for taxonomy-agnostic pillar derivation.

    Required because the KG supports multiple top-level taxonomies
    (pillar1..pillar8 system view + ml-fundamentals interview-grind view).
    See docs/design/kg_dual_view_decision_20260425.md.

    Walks parent_id back to the depth=0 ancestor and returns that root's
    path string. Works for both the dot-separated original pillars
    (e.g. 'pillar2.feature_engineering' -> root 'pillar2') and the
    slash-separated ml-fundamentals subtree
    (e.g. 'ml-fundamentals/classical_ml/bias-variance-tradeoff' -> root
    'ml-fundamentals'), and for any future user-approved 3rd root that
    follows the criteria in Section 2 of the decision doc above.

    PERMANENT infrastructure (ratified 2026-04-26 by T-P2-614). Do NOT
    revert to path.split(".",1)[0] -- doing so silently breaks the
    ml-fundamentals view (slash-separated paths have no '.' to split on)
    and re-introduces the bug fixed by KG-FIX-01..05.

    Args:
        node: The framework node to derive a pillar for.
        nodes_by_id: Lookup dict id -> FrameworkNode covering the full
            ancestor chain.

    Returns:
        The depth=0 ancestor's path string, or None if node is None or the
        chain is broken (orphaned parent_id, cycle).
    """
    if node is None:
        return None
    cur: FrameworkNode = node
    seen: set[int] = set()
    while cur.parent_id is not None:
        if cur.id in seen:
            return None
        seen.add(cur.id)
        parent = nodes_by_id.get(cur.parent_id)
        if parent is None:
            return None
        cur = parent
    return cur.path


@router.get("/kg/graph")
def get_kg_graph(
    pillars: str | None = Query(
        default=None,
        description="Comma-separated pillar prefixes to include (e.g. 'pillar1,pillar3'). "
        "If omitted, all pillars are returned.",
    ),
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, Any]]]:
    """Return graph payload for the Cytoscape.js POC.

    Args:
        pillars: Optional comma-separated pillar filter.
        limit: Max number of framework_node rows to emit.
        db: Injected SQLAlchemy session.

    Returns:
        {"nodes": [...], "edges": [...]} where node has id/kind/pillar/path/
        title/content_length and edge has src_kind/src_id/dst_kind/dst_id/
        relation.
    """
    pillar_filter: set[str] | None = None
    if pillars:
        pillar_filter = {p.strip() for p in pillars.split(",") if p.strip()}

    # Load all nodes once so _pillar_of() can walk parent_id chains even when
    # the limit slices off the depth=0 ancestors.
    all_nodes = (
        db.query(FrameworkNode).order_by(FrameworkNode.depth, FrameworkNode.id).all()
    )
    nodes_by_id: dict[int, FrameworkNode] = {n.id: n for n in all_nodes}
    rows = all_nodes[:limit]

    try:
        rows_cl = db.execute(
            text(
                "SELECT src_kind, src_id, dst_kind, dst_id, relation "
                "FROM concept_links "
                "WHERE src_kind = 'framework_node' AND dst_kind = 'framework_node'"
            )
        ).fetchall()
    except OperationalError:
        rows_cl = []

    edge_count_by_id: dict[int, int] = {}
    for r in rows_cl:
        edge_count_by_id[r[1]] = edge_count_by_id.get(r[1], 0) + 1
        edge_count_by_id[r[3]] = edge_count_by_id.get(r[3], 0) + 1

    node_payload: list[dict[str, Any]] = []
    emitted_ids: set[int] = set()
    for n in rows:
        pillar = _pillar_of(n, nodes_by_id)
        if pillar_filter is not None and pillar not in pillar_filter:
            continue
        node_payload.append(
            {
                "id": n.id,
                "kind": "framework_node",
                "pillar": pillar,
                "path": n.path,
                "title": n.title,
                "depth": n.depth,
                "parent_id": n.parent_id,
                "content_length": len(n.description) if n.description else 0,
                "edge_count": edge_count_by_id.get(n.id, 0),
            }
        )
        emitted_ids.add(n.id)

    edge_payload: list[dict[str, Any]] = []
    for r in rows_cl:
        if r[1] in emitted_ids and r[3] in emitted_ids:
            edge_payload.append(
                {
                    "src_kind": r[0],
                    "src_id": r[1],
                    "dst_kind": r[2],
                    "dst_id": r[3],
                    "relation": r[4],
                }
            )

    if not edge_payload:
        for n in rows:
            if n.parent_id is None or n.id not in emitted_ids or n.parent_id not in emitted_ids:
                continue
            edge_payload.append(
                {
                    "src_kind": "framework_node",
                    "src_id": n.parent_id,
                    "dst_kind": "framework_node",
                    "dst_id": n.id,
                    "relation": "parent",
                }
            )

    return {"nodes": node_payload, "edges": edge_payload}
