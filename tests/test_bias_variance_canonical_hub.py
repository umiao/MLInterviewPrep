"""Regression tests for KG-P2-01 Bias-Variance canonical hub consolidation.

Verifies: node 67 expanded with canonical_hub marker + required sections;
doc 56 trimmed to <=5000 chars with canonical pointer blockquote;
concept_links rows inserted both directions; 'drill' in relation vocabulary.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- KG_P2_01_BIAS_VARIANCE_20260416 -->"
CANONICAL_NODE_ID = 67
DRILL_DOC_ID = 56

pytestmark = pytest.mark.skipif(
    not DB_PATH.exists(), reason="runtime DB data/mle_prep.db not present"
)


@pytest.fixture()
def conn():
    c = sqlite3.connect(str(DB_PATH))
    try:
        yield c
    finally:
        c.close()


def test_drill_relation_in_vocabulary(conn: sqlite3.Connection) -> None:
    """Schema migration extended concept_links.relation CHECK to include 'drill'."""
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='concept_links'"
    ).fetchone()[0]
    assert "'drill'" in sql, (
        "'drill' not in concept_links relation CHECK -- run "
        "_migrate_concept_links_add_drill_20260416.py"
    )


def test_node_67_has_canonical_hub_marker(conn: sqlite3.Connection) -> None:
    desc = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()[0]
    assert "<!-- doc_kind: canonical_hub -->" in desc
    assert SENTINEL in desc


def test_node_67_length_in_range(conn: sqlite3.Connection) -> None:
    length = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()[0]
    assert 8000 <= length <= 12000, (
        f"node 67 length {length} outside canonical_hub range [8000, 12000]"
    )


def test_node_67_required_sections(conn: sqlite3.Connection) -> None:
    desc = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()[0]
    required = [
        "## Overview",
        "### Error Decomposition",
        "### Derivation",
        "### Diagnostic Curves: Error vs. Model Complexity",
        "## Remedies Matrix",
        "## Interview Pitfalls",
        "## Components",
        "## Key Takeaways",
    ]
    missing = [s for s in required if s not in desc]
    assert not missing, f"node 67 missing required sections: {missing}"


def test_node_67_has_prereq_and_followup_blockquotes(conn: sqlite3.Connection) -> None:
    desc = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()[0]
    pattern = re.compile(
        r"^\s*> \*\*(前置|后续)\*\* \[.*?\]\(/framework/\d+\)\s*$",
        re.MULTILINE,
    )
    matches = pattern.findall(desc)
    assert "前置" in matches, "canonical hub must declare at least one 前置"
    assert "后续" in matches, "canonical hub must declare at least one 后续"


def test_doc_56_length_capped(conn: sqlite3.Connection) -> None:
    length = conn.execute(
        "SELECT length(content) FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()[0]
    assert length <= 5000, f"drill doc 56 length {length} > 5000 cap"


def test_doc_56_has_canonical_pointer(conn: sqlite3.Connection) -> None:
    content = conn.execute(
        "SELECT content FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()[0]
    pattern = re.compile(
        r"^> \*\*\u6b63\u5178\*\* \[.*?\]\(/framework/67\)\s*$",
        re.MULTILINE,
    )
    assert pattern.search(content) is not None, (
        "doc 56 missing canonical 正典 blockquote pointing to /framework/67"
    )


def test_doc_56_derivation_removed(conn: sqlite3.Connection) -> None:
    """The re-derivation section is the thing we explicitly deleted -- its
    tell-tale markers must be gone from the drill."""
    content = conn.execute(
        "SELECT content FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()[0]
    forbidden = [
        "Bias-Variance Decomposition (Memorize This)",
        "Memorize This",
        "Oral shortcut: 'Expected test",
    ]
    leaked = [s for s in forbidden if s in content]
    assert not leaked, (
        f"drill doc 56 still contains canonical-only content: {leaked}"
    )


def test_doc_56_doc_kind_is_drill(conn: sqlite3.Connection) -> None:
    kind = conn.execute(
        "SELECT doc_kind FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()[0]
    assert kind == "drill"


def test_concept_links_forward_canonical_edge(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT src_kind, src_id, dst_kind, dst_id, relation "
        "FROM concept_links "
        "WHERE src_kind='company_document' AND src_id=? "
        "AND dst_kind='framework_node' AND dst_id=? AND relation='canonical'",
        (DRILL_DOC_ID, CANONICAL_NODE_ID),
    ).fetchone()
    assert row is not None, "forward canonical edge (doc 56 -> node 67) missing"


def test_concept_links_reverse_drill_edge(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT src_kind, src_id, dst_kind, dst_id, relation "
        "FROM concept_links "
        "WHERE src_kind='framework_node' AND src_id=? "
        "AND dst_kind='company_document' AND dst_id=? AND relation='drill'",
        (CANONICAL_NODE_ID, DRILL_DOC_ID),
    ).fetchone()
    assert row is not None, "reverse drill edge (node 67 -> doc 56) missing"
