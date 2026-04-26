"""Tests for src.backend.routers.kg._pillar_of (T-P0-609 / KG-FIX-01).

The new implementation walks parent_id back to the depth=0 ancestor and
returns that ancestor's path string, rather than splitting the leaf node's
path on '.'. This is taxonomy-agnostic and correctly handles both the
dot-separated original pillars and the slash-separated ml-fundamentals
subtree.

These are pure unit tests against the in-memory db_session fixture; they
do not require the runtime data/mle_prep.db.
"""
from __future__ import annotations

import pytest

from src.backend.models.framework import FrameworkNode
from src.backend.routers.kg import _pillar_of


def _seed_root(db, path: str, title: str) -> FrameworkNode:
    """Insert a depth=0 root framework node."""
    n = FrameworkNode(path=path, depth=0, title=title)
    db.add(n)
    db.flush()
    return n


def _seed_child(
    db, parent: FrameworkNode, path: str, title: str, depth: int = 1
) -> FrameworkNode:
    """Insert a child framework node under parent."""
    n = FrameworkNode(parent_id=parent.id, path=path, depth=depth, title=title)
    db.add(n)
    db.flush()
    return n


# AC2 parameter set: every pillar1..pillar8 plus ml-fundamentals, with a
# representative descendant whose pillar derivation must return the root path.
PILLAR_REGRESSION_CASES = [
    ("pillar1", "pillar1.two_sum"),
    ("pillar2", "pillar2.feature_engineering"),
    ("pillar3", "pillar3.design_problems"),
    ("pillar4", "pillar4.recsys"),
    ("pillar5", "pillar5.serving"),
    ("pillar6", "pillar6.transformers"),
    ("pillar7", "pillar7.probability_statistics"),
    ("pillar8", "pillar8.behavioral"),
    ("ml-fundamentals", "ml-fundamentals/classical_ml"),
]


@pytest.mark.parametrize("root_path,child_path", PILLAR_REGRESSION_CASES)
def test_pillar_of_walks_parent_to_root(
    db_session, root_path: str, child_path: str
) -> None:
    """Each pillar's depth=1 descendant resolves to the root path.

    Covers AC2 (regression for the 8 original pillars) and the
    ml-fundamentals slash-path case in a single parameter list.
    """
    root = _seed_root(db_session, path=root_path, title=root_path)
    child = _seed_child(db_session, parent=root, path=child_path, title=child_path)
    nodes_by_id = {root.id: root, child.id: child}

    assert _pillar_of(child, nodes_by_id) == root_path
    # The root itself returns its own path.
    assert _pillar_of(root, nodes_by_id) == root_path


def test_pillar_of_ml_fundamentals_full_subtree(db_session) -> None:
    """AC1: every node under ml-fundamentals returns 'ml-fundamentals'.

    Reproduces the prod schema shape: depth=0 root with slash-separated
    descendants at depth=1 (categories) and depth=2 (leaves).
    """
    root = _seed_root(
        db_session, path="ml-fundamentals", title="ML Fundamentals"
    )
    cat = _seed_child(
        db_session,
        parent=root,
        path="ml-fundamentals/classical_ml",
        title="Classical ML",
        depth=1,
    )
    leaf = _seed_child(
        db_session,
        parent=cat,
        path="ml-fundamentals/classical_ml/bias-variance-tradeoff",
        title="Bias-Variance",
        depth=2,
    )
    nodes_by_id = {root.id: root, cat.id: cat, leaf.id: leaf}

    for n in (root, cat, leaf):
        assert _pillar_of(n, nodes_by_id) == "ml-fundamentals"


def test_pillar_of_does_not_split_on_dot_for_root(db_session) -> None:
    """A depth=0 node returns its own full path, not a split prefix.

    Guards against accidental regression to path.split('.', 1)[0] semantics.
    """
    root = _seed_root(db_session, path="pillar2", title="ML Fundamentals & Theory")
    nodes_by_id = {root.id: root}
    assert _pillar_of(root, nodes_by_id) == "pillar2"


def test_pillar_of_handles_none_node() -> None:
    """A None node returns None without raising."""
    assert _pillar_of(None, {}) is None


def test_pillar_of_orphan_parent_returns_none(db_session) -> None:
    """If parent_id points outside nodes_by_id, return None instead of crashing."""
    orphan = FrameworkNode(parent_id=99999, path="x.y", depth=1, title="orphan")
    db_session.add(orphan)
    db_session.flush()
    assert _pillar_of(orphan, {orphan.id: orphan}) is None


def test_pillar_of_cycle_returns_none(db_session) -> None:
    """Cycle protection: a parent_id loop must not infinite-loop."""
    a = _seed_root(db_session, path="cyclic", title="cyclic-root")
    b = _seed_child(db_session, parent=a, path="cyclic.b", title="b")
    # Force a cycle: make a.parent_id = b.id (only possible by direct mutation).
    a.parent_id = b.id
    db_session.flush()
    nodes_by_id = {a.id: a, b.id: b}
    assert _pillar_of(b, nodes_by_id) is None
