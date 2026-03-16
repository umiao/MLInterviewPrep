"""Tests for framework API routes."""
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.models.scraper import InterviewQuestion


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


# --- Node-linked problems endpoint ---


def test_get_node_problems(test_client, db_session):
    """GET /framework/nodes/{id}/problems returns linked problems."""
    node = _seed_node(db_session, title="DP", path="coding/dp")
    p1 = Problem(title="Climbing Stairs", difficulty="easy", framework_node_id=node.id)
    p2 = Problem(title="Coin Change", difficulty="medium", framework_node_id=node.id)
    p3 = Problem(title="Two Sum", difficulty="easy", framework_node_id=None)
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    resp = test_client.get(f"/api/framework/nodes/{node.id}/problems")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    titles = {p["title"] for p in data}
    assert titles == {"Climbing Stairs", "Coin Change"}


def test_get_node_problems_empty(test_client, db_session):
    """GET /framework/nodes/{id}/problems returns empty list when none linked."""
    node = _seed_node(db_session, title="Trees", path="coding/trees")
    resp = test_client.get(f"/api/framework/nodes/{node.id}/problems")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_node_problems_404(test_client):
    """GET /framework/nodes/{id}/problems returns 404 for missing node."""
    resp = test_client.get("/api/framework/nodes/99999/problems")
    assert resp.status_code == 404


# --- Node-linked questions endpoint ---


def test_get_node_questions(test_client, db_session):
    """GET /framework/nodes/{id}/questions returns linked interview questions."""
    node = _seed_node(db_session, title="DP", path="coding/dp")
    q1 = InterviewQuestion(
        question_text="Explain DP", company="Google",
        mapped_framework_node_id=node.id,
    )
    q2 = InterviewQuestion(
        question_text="Unlinked Q", company="Meta",
        mapped_framework_node_id=None,
    )
    db_session.add_all([q1, q2])
    db_session.commit()

    resp = test_client.get(f"/api/framework/nodes/{node.id}/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["question_text"] == "Explain DP"


def test_get_node_questions_404(test_client):
    """GET /framework/nodes/{id}/questions returns 404 for missing node."""
    resp = test_client.get("/api/framework/nodes/99999/questions")
    assert resp.status_code == 404


# --- Problem creation with framework_node_id ---


def test_create_problem_with_framework_node(test_client, db_session):
    """POST /problems with framework_node_id links the problem to a topic."""
    node = _seed_node(db_session, title="Graphs", path="coding/graphs")
    resp = test_client.post("/api/problems", json={
        "title": "Graph BFS",
        "difficulty": "medium",
        "framework_node_id": node.id,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["framework_node_id"] == node.id


def test_create_problem_without_framework_node(test_client):
    """POST /problems without framework_node_id creates an unlinked problem."""
    resp = test_client.post("/api/problems", json={
        "title": "Two Sum",
        "difficulty": "easy",
    })
    assert resp.status_code == 201
    assert resp.json()["framework_node_id"] is None


def test_update_problem_framework_node(test_client, db_session):
    """PUT /problems/{id} can set/change framework_node_id."""
    node = _seed_node(db_session, title="DP", path="coding/dp")
    # Create without link
    resp = test_client.post("/api/problems", json={"title": "Knapsack"})
    pid = resp.json()["id"]

    # Link to node
    resp = test_client.put(f"/api/problems/{pid}", json={"framework_node_id": node.id})
    assert resp.status_code == 200
    assert resp.json()["framework_node_id"] == node.id

    # Unlink
    resp = test_client.put(f"/api/problems/{pid}", json={"framework_node_id": None})
    assert resp.status_code == 200
    assert resp.json()["framework_node_id"] is None


# --- CASCADE behavior: SET NULL on node delete ---


def test_cascade_set_null_on_node_delete(db_session):
    """Deleting a framework node sets framework_node_id to NULL on linked problems."""
    node = _seed_node(db_session, title="DP", path="coding/dp")
    p = Problem(title="DP Problem", difficulty="easy", framework_node_id=node.id)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.framework_node_id == node.id

    db_session.delete(node)
    db_session.commit()
    db_session.refresh(p)
    assert p.framework_node_id is None
