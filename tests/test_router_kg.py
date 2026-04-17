"""Tests for the /api/kg/graph endpoint (KG-VIZ-01 POC)."""
from __future__ import annotations

from sqlalchemy import text

from src.backend.models.framework import FrameworkNode


def _seed_node(db, **kwargs) -> FrameworkNode:
    """Insert a FrameworkNode for tests."""
    node = FrameworkNode(**kwargs)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def test_kg_graph_empty(test_client):
    """Empty DB returns empty nodes/edges arrays."""
    resp = test_client.get("/api/kg/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"nodes": [], "edges": []}


def test_kg_graph_emits_framework_nodes_with_pillar(test_client, db_session):
    """Each framework node is emitted with a pillar derived from path."""
    pillar = _seed_node(db_session, title="Coding", path="pillar1", depth=0)
    child = _seed_node(
        db_session,
        title="Two Sum",
        path="pillar1.two_sum",
        depth=1,
        parent_id=pillar.id,
        description="Hash map approach",
    )

    resp = test_client.get("/api/kg/graph")
    assert resp.status_code == 200
    data = resp.json()

    ids = {n["id"]: n for n in data["nodes"]}
    assert pillar.id in ids
    assert child.id in ids
    assert ids[pillar.id]["pillar"] == "pillar1"
    assert ids[child.id]["pillar"] == "pillar1"
    assert ids[child.id]["kind"] == "framework_node"
    assert ids[child.id]["content_length"] == len("Hash map approach")
    assert ids[pillar.id]["content_length"] == 0  # no description


def test_kg_graph_synthetic_parent_edges_when_concept_links_empty(
    test_client, db_session
):
    """When no concept_links exist, synthesize parent->child edges."""
    parent = _seed_node(db_session, title="Algorithms", path="pillar2", depth=0)
    a = _seed_node(
        db_session,
        title="DP",
        path="pillar2.dp",
        depth=1,
        parent_id=parent.id,
    )
    b = _seed_node(
        db_session,
        title="Greedy",
        path="pillar2.greedy",
        depth=1,
        parent_id=parent.id,
    )

    resp = test_client.get("/api/kg/graph")
    assert resp.status_code == 200
    edges = resp.json()["edges"]

    edge_pairs = {(e["src_id"], e["dst_id"]) for e in edges}
    assert (parent.id, a.id) in edge_pairs
    assert (parent.id, b.id) in edge_pairs
    for e in edges:
        assert e["relation"] == "parent"
        assert e["src_kind"] == "framework_node"
        assert e["dst_kind"] == "framework_node"


def test_kg_graph_uses_real_concept_links_when_present(
    test_client, db_session, db_engine
):
    """If concept_links table has framework_node->framework_node rows, use them."""
    src = _seed_node(db_session, title="Reg", path="pillar2.reg", depth=1)
    dst = _seed_node(db_session, title="L2", path="pillar2.l2", depth=2)

    with db_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS concept_links ("
                "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "  src_kind TEXT NOT NULL,"
                "  src_id INTEGER NOT NULL,"
                "  dst_kind TEXT NOT NULL,"
                "  dst_id INTEGER NOT NULL,"
                "  relation TEXT NOT NULL,"
                "  weight REAL DEFAULT 1.0,"
                "  note TEXT,"
                "  created_at TEXT DEFAULT (datetime('now'))"
                ")"
            )
        )
        conn.execute(
            text(
                "INSERT INTO concept_links "
                "(src_kind, src_id, dst_kind, dst_id, relation) "
                "VALUES ('framework_node', :s, 'framework_node', :d, 'see_also')"
            ),
            {"s": src.id, "d": dst.id},
        )

    resp = test_client.get("/api/kg/graph")
    assert resp.status_code == 200
    edges = resp.json()["edges"]

    relations = [e["relation"] for e in edges]
    assert "see_also" in relations
    assert all(e["relation"] != "parent" for e in edges), (
        "Synthetic parent edges should NOT be emitted when real edges exist"
    )


def test_kg_graph_pillar_filter(test_client, db_session):
    """?pillars=pillar1 limits nodes to that pillar."""
    _seed_node(db_session, title="Coding", path="pillar1", depth=0)
    _seed_node(db_session, title="Algos", path="pillar1.algos", depth=1)
    _seed_node(db_session, title="ML", path="pillar2", depth=0)

    resp = test_client.get("/api/kg/graph?pillars=pillar1")
    assert resp.status_code == 200
    pillars = {n["pillar"] for n in resp.json()["nodes"]}
    assert pillars == {"pillar1"}


def test_kg_graph_limit(test_client, db_session):
    """?limit caps the framework_node count."""
    for i in range(5):
        _seed_node(db_session, title=f"N{i}", path=f"pillar1.n{i}", depth=1)

    resp = test_client.get("/api/kg/graph?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()["nodes"]) <= 2
