"""Tests for question CRUD API routes."""


def test_create_question(test_client):
    """POST /api/questions creates a question and returns it."""
    resp = test_client.post("/api/questions", json={
        "question_text": "What is gradient descent?",
        "company": "Google",
        "role": "MLE",
        "question_type": "ml_theory",
        "level": "L4",
        "year": 2025,
        "tags": ["optimization", "basics"],
        "difficulty_estimate": "easy",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["question_text"] == "What is gradient descent?"
    assert data["company"] == "Google"
    assert data["tags"] == ["optimization", "basics"]
    assert data["difficulty_estimate"] == "easy"


def test_create_question_minimal(test_client):
    """POST /api/questions with only required field."""
    resp = test_client.post("/api/questions", json={
        "question_text": "Explain backprop",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["question_text"] == "Explain backprop"
    assert data["company"] is None


def test_create_question_empty_text_rejected(test_client):
    """POST /api/questions with empty text returns 422."""
    resp = test_client.post("/api/questions", json={
        "question_text": "",
    })
    assert resp.status_code == 422


def test_create_question_with_framework_node(test_client, seed_framework):
    """POST /api/questions with mapped_framework_node_id."""
    _root, child = seed_framework
    resp = test_client.post("/api/questions", json={
        "question_text": "DP question mapped to node",
        "mapped_framework_node_id": child.id,
    })
    assert resp.status_code == 201
    assert resp.json()["mapped_framework_node_id"] == child.id


def test_delete_question(test_client):
    """DELETE /api/questions/{id} removes the question."""
    resp = test_client.post("/api/questions", json={
        "question_text": "To be deleted",
    })
    qid = resp.json()["id"]

    resp = test_client.delete(f"/api/questions/{qid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Verify it's gone from listing
    resp = test_client.get("/api/questions")
    assert all(q["id"] != qid for q in resp.json())


def test_delete_question_not_found(test_client):
    """DELETE non-existent question returns 404."""
    resp = test_client.delete("/api/questions/99999")
    assert resp.status_code == 404


def test_update_question_all_fields(test_client, seed_framework):
    """PUT /api/questions/{id} updates all editable fields."""
    _root, child = seed_framework

    resp = test_client.post("/api/questions", json={
        "question_text": "Original question",
        "company": "OldCo",
    })
    qid = resp.json()["id"]

    resp = test_client.put(f"/api/questions/{qid}", json={
        "company": "NewCo",
        "role": "SDE",
        "question_type": "coding",
        "level": "L5",
        "year": 2026,
        "tags": ["array", "dp"],
        "difficulty_estimate": "hard",
        "mapped_framework_node_id": child.id,
        "is_reviewed": True,
        "notes": "Updated notes",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["company"] == "NewCo"
    assert data["role"] == "SDE"
    assert data["question_type"] == "coding"
    assert data["level"] == "L5"
    assert data["year"] == 2026
    assert data["tags"] == ["array", "dp"]
    assert data["difficulty_estimate"] == "hard"
    assert data["mapped_framework_node_id"] == child.id
    assert data["is_reviewed"] is True
    assert data["notes"] == "Updated notes"


def test_update_question_partial(test_client):
    """PUT /api/questions/{id} with partial data only updates sent fields."""
    resp = test_client.post("/api/questions", json={
        "question_text": "Partial update test",
        "company": "OrigCo",
        "role": "MLE",
    })
    qid = resp.json()["id"]

    resp = test_client.put(f"/api/questions/{qid}", json={
        "is_reviewed": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_reviewed"] is True
    # Original fields unchanged
    assert data["company"] == "OrigCo"
    assert data["role"] == "MLE"


def test_update_question_not_found(test_client):
    """PUT non-existent question returns 404."""
    resp = test_client.put("/api/questions/99999", json={
        "notes": "test",
    })
    assert resp.status_code == 404
