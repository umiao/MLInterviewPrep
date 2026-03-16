"""Tests for framework API routes."""
from src.backend.models.framework import FrameworkNode


def _seed_node(db, title="DP", path="coding/dp", depth=1, parent_id=None, description=None):
    """Helper to create a framework node."""
    node = FrameworkNode(
        title=title, path=path, depth=depth,
        parent_id=parent_id, description=description,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def test_framework_tree_empty(test_client):
    """Empty DB returns empty tree."""
    resp = test_client.get("/api/framework/tree")
    assert resp.status_code == 200
    assert resp.json() == []


def test_framework_stats_empty(test_client):
    """Stats on empty DB returns zeros."""
    resp = test_client.get("/api/framework/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_nodes"] == 0


def test_update_node_404(test_client):
    """Update non-existent node returns 404."""
    resp = test_client.put("/api/framework/nodes/99999", json={"status": "mastered"})
    assert resp.status_code == 404


def test_company_crud(test_client):
    """Company create/list/update cycle."""
    # Create
    resp = test_client.post("/api/companies", json={
        "name": "Google", "group_tag": "llm_first",
    })
    assert resp.status_code == 201
    cid = resp.json()["id"]

    # List
    resp = test_client.get("/api/companies")
    assert len(resp.json()) == 1

    # Duplicate
    resp = test_client.post("/api/companies", json={"name": "Google"})
    assert resp.status_code == 409

    # Update
    resp = test_client.put(f"/api/companies/{cid}", json={"status": "onsite"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "onsite"

    # Filter
    resp = test_client.get("/api/companies?status=onsite")
    assert len(resp.json()) == 1
    resp = test_client.get("/api/companies?status=applied")
    assert len(resp.json()) == 0


def test_company_404(test_client):
    """Update non-existent company returns 404."""
    resp = test_client.put("/api/companies/99999", json={"name": "X"})
    assert resp.status_code == 404


def test_update_node_title_and_description(test_client, db_session):
    """PUT /framework/nodes/{id} accepts title and description, round-trips correctly."""
    node = _seed_node(db_session, title="Sorting", path="coding/sorting", description=None)

    resp = test_client.put(f"/api/framework/nodes/{node.id}", json={
        "title": "Sorting Algorithms",
        "description": "Quicksort, mergesort, heapsort",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Sorting Algorithms"
    assert data["description"] == "Quicksort, mergesort, heapsort"

    # Verify via GET tree
    resp = test_client.get("/api/framework/tree")
    assert resp.status_code == 200
    tree = resp.json()
    matched = [n for n in tree if n["id"] == node.id]
    assert len(matched) == 1
    assert matched[0]["title"] == "Sorting Algorithms"
    assert matched[0]["description"] == "Quicksort, mergesort, heapsort"


def test_tree_includes_description(test_client, db_session):
    """GET /framework/tree response includes the description field."""
    _seed_node(db_session, title="ML Basics", path="ml/basics", description="Core ML concepts")

    resp = test_client.get("/api/framework/tree")
    assert resp.status_code == 200
    tree = resp.json()
    assert len(tree) == 1
    assert "description" in tree[0]
    assert tree[0]["description"] == "Core ML concepts"


def test_update_description_only(test_client, db_session):
    """PUT with only description field updates description without changing other fields."""
    node = _seed_node(db_session, title="Graphs", path="coding/graphs")

    resp = test_client.put(f"/api/framework/nodes/{node.id}", json={
        "description": "BFS, DFS, Dijkstra",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Graphs"  # unchanged
    assert data["description"] == "BFS, DFS, Dijkstra"


def test_tree_description_null_by_default(test_client, db_session):
    """Nodes without description return null in tree response."""
    _seed_node(db_session, title="Arrays", path="coding/arrays")

    resp = test_client.get("/api/framework/tree")
    tree = resp.json()
    assert tree[0]["description"] is None
