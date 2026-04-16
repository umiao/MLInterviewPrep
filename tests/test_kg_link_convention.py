"""Tests for the KG markdown link convention (T-P0-472, KG-P1-03).

Verifies that the POC-patched framework_nodes carry at least one canonical
blockquote that matches the parser regex documented in
docs/protocol/kg_markdown_conventions.md. Skips if runtime DB missing.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_PATH = Path(__file__).resolve().parent.parent / "docs" / "protocol" / "kg_markdown_conventions.md"

# The canonical parser regex from the convention doc, section 4.
CANONICAL_TAG_REGEX = re.compile(
    r"^\s*> \*\*(正典|也见|前置|后续)\*\* \[(.*?)\]\(/framework/(\d+)\)\s*$",
    re.MULTILINE,
)

POC_NODE_IDS = (130, 133)
POC_TARGET_NODE_ID = 132  # LLM Serving -- the node both POC patches reference

pytestmark = pytest.mark.skipif(
    not DB_PATH.exists(), reason="runtime DB data/mle_prep.db not present"
)


@pytest.fixture()
def conn():
    c = sqlite3.connect(str(DB_PATH))
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def test_convention_doc_exists() -> None:
    """The convention doc is the spec -- without it the regex has no source."""
    assert DOC_PATH.exists(), f"missing convention doc: {DOC_PATH}"
    body = DOC_PATH.read_text(encoding="utf-8")
    for tag in ("正典", "也见", "前置", "后续"):
        assert tag in body, f"tag '{tag}' missing from convention doc"
    assert "/framework/" in body, "convention doc must show the /framework/{id} URL form"


@pytest.mark.parametrize("node_id", POC_NODE_IDS)
def test_poc_node_has_canonical_blockquote(
    conn: sqlite3.Connection, node_id: int
) -> None:
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (node_id,),
    ).fetchone()
    assert row is not None, f"framework_node {node_id} missing from DB"
    desc = row[0] or ""
    matches = list(CANONICAL_TAG_REGEX.finditer(desc))
    assert matches, (
        f"framework_node {node_id} has no canonical-syntax blockquote; "
        "run scripts/patch_kg_link_syntax_poc.py"
    )
    # At least one of the matches must point at the expected target node.
    targets = {int(m.group(3)) for m in matches}
    assert POC_TARGET_NODE_ID in targets, (
        f"framework_node {node_id} expected a canonical blockquote pointing to "
        f"/framework/{POC_TARGET_NODE_ID} (LLM Serving); found targets {targets}"
    )


def test_poc_nodes_carry_sentinel(conn: sqlite3.Connection) -> None:
    """The idempotency sentinel is what lets the patcher skip on re-run."""
    sentinel = "<!-- KG_LINK_POC_20260416 -->"
    for node_id in POC_NODE_IDS:
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE id=?",
            (node_id,),
        ).fetchone()
        assert row is not None, f"framework_node {node_id} missing"
        assert sentinel in (row[0] or ""), (
            f"framework_node {node_id} missing sentinel '{sentinel}'"
        )


def test_regex_rejects_inline_prose() -> None:
    """Negative control: inline '详见 LLM Serving 节点' must NOT match."""
    bad = "显著提升 GPU 利用率（详见 LLM Serving 节点）"
    assert not CANONICAL_TAG_REGEX.search(bad)


def test_regex_rejects_untagged_blockquote() -> None:
    """Blockquote without the bold tag word must NOT match."""
    bad = "> [LLM Serving](/framework/132)"
    assert not CANONICAL_TAG_REGEX.search(bad)


def test_regex_accepts_all_four_tags() -> None:
    """Positive control: each of the four tag families parses cleanly."""
    samples = [
        "> **正典** [Bias-Variance (pillar7.probability_statistics.bias_variance)](/framework/56)",
        "> **也见** [A/B Testing](/framework/104)",
        "> **前置** [Gradient Descent](/framework/18)",
        "> **后续** [Regularization](/framework/195)",
    ]
    for s in samples:
        m = CANONICAL_TAG_REGEX.search(s)
        assert m is not None, f"regex rejected valid sample: {s!r}"
