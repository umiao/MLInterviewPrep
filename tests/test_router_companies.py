"""Tests for company API routes."""


def test_create_and_list_companies(test_client):
    """Create a company and verify it appears in the list."""
    resp = test_client.post("/api/companies", json={
        "name": "Google",
        "group_tag": "FAANG",
        "status": "applied",
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Google"

    resp = test_client.get("/api/companies")
    assert len(resp.json()) == 1


def test_delete_company(test_client):
    """Delete a company returns success."""
    resp = test_client.post("/api/companies", json={
        "name": "Meta",
        "status": "applied",
    })
    company_id = resp.json()["id"]

    resp = test_client.delete(f"/api/companies/{company_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted"] is True
    assert data["weights_removed"] == 0

    # Verify it's gone
    resp = test_client.get(f"/api/companies/{company_id}")
    assert resp.status_code == 404


def test_delete_company_cascades_weights(test_client, seed_framework):
    """Delete company cascades topic weights and returns count."""
    # Create company
    resp = test_client.post("/api/companies", json={
        "name": "Amazon",
        "status": "applied",
    })
    company_id = resp.json()["id"]

    # Add topic weights
    _root, child = seed_framework
    resp = test_client.post(f"/api/companies/{company_id}/weights", json=[
        {"framework_node_id": child.id, "weight": 3},
    ])
    assert resp.status_code == 200

    # Delete company
    resp = test_client.delete(f"/api/companies/{company_id}")
    assert resp.status_code == 200
    assert resp.json()["weights_removed"] == 1


def test_delete_company_not_found(test_client):
    """Delete non-existent company returns 404."""
    resp = test_client.delete("/api/companies/99999")
    assert resp.status_code == 404


def test_delete_topic_weight(test_client, seed_framework):
    """Delete a single topic weight from a company."""
    resp = test_client.post("/api/companies", json={
        "name": "Netflix",
        "status": "applied",
    })
    company_id = resp.json()["id"]

    _root, child = seed_framework
    test_client.post(f"/api/companies/{company_id}/weights", json=[
        {"framework_node_id": child.id, "weight": 2},
    ])

    # Delete the weight
    resp = test_client.delete(
        f"/api/companies/{company_id}/weights/{child.id}"
    )
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Verify weight is gone
    resp = test_client.get(f"/api/companies/{company_id}")
    assert len(resp.json()["topic_weights"]) == 0


def test_delete_topic_weight_not_found(test_client):
    """Delete non-existent topic weight returns 404."""
    resp = test_client.post("/api/companies", json={
        "name": "Apple",
        "status": "applied",
    })
    company_id = resp.json()["id"]

    resp = test_client.delete(f"/api/companies/{company_id}/weights/99999")
    assert resp.status_code == 404
