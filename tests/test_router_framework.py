"""Tests for framework API routes."""


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
