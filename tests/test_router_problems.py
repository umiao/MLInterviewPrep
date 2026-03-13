"""Tests for problems API routes."""


# ---------------------------------------------------------------------------
# Helper to seed multiple problems for filter/sort/pagination tests
# ---------------------------------------------------------------------------

def _seed_diverse_problems(client):
    """Create a diverse set of problems for filter tests. Returns list of created dicts."""
    problems = [
        {
            "title": "Two Sum", "difficulty": "easy", "pattern": "hash_map",
            "category": "algorithm", "source": "blind75",
            "tags": ["array", "hash-table"], "company_tags": ["google", "meta"],
            "leetcode_id": 1,
        },
        {
            "title": "3Sum", "difficulty": "medium", "pattern": "two_pointers",
            "category": "algorithm", "source": "blind75+neetcode150",
            "tags": ["array"], "company_tags": ["google"],
            "leetcode_id": 15,
        },
        {
            "title": "Merge Intervals", "difficulty": "medium", "pattern": "interval",
            "category": "algorithm", "source": "neetcode150",
            "tags": ["sorting"], "company_tags": ["meta"],
            "leetcode_id": 56,
        },
        {
            "title": "Binary Tree Max Path", "difficulty": "hard", "pattern": "tree",
            "category": "algorithm", "source": "blind75",
            "tags": ["tree", "dfs"], "company_tags": ["amazon"],
            "leetcode_id": 124,
        },
        {
            "title": "ML Feature Pipeline", "difficulty": "medium", "pattern": "pipeline",
            "category": "ml_coding", "source": "custom",
            "tags": ["ml"], "company_tags": ["meta", "google"],
        },
        {
            "title": "Sys Design Chat", "difficulty": "hard", "pattern": "system",
            "category": "system_design", "source": "custom",
            "tags": ["design"], "company_tags": ["amazon"],
        },
    ]
    results = []
    for p in problems:
        resp = client.post("/api/problems", json=p)
        assert resp.status_code == 201
        results.append(resp.json())
    return results


# ===========================================================================
# Health check
# ===========================================================================

def test_health_check(test_client):
    """GET /api/health returns 200."""
    resp = test_client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ===========================================================================
# GET /api/problems -- empty DB
# ===========================================================================

def test_list_problems_empty(test_client):
    """Empty DB returns empty list with X-Total-Count 0."""
    resp = test_client.get("/api/problems")
    assert resp.status_code == 200
    assert resp.json() == []
    assert resp.headers["X-Total-Count"] == "0"


# ===========================================================================
# GET /api/problems -- filters
# ===========================================================================

def test_filter_by_difficulty(test_client):
    """Filter by difficulty returns only matching problems."""
    _seed_diverse_problems(test_client)

    resp = test_client.get("/api/problems?difficulty=easy")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert all(p["difficulty"] == "easy" for p in data)


def test_filter_by_difficulty_medium(test_client):
    """Filter by medium returns 3 medium problems."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=medium")
    assert len(resp.json()) == 3


def test_filter_by_difficulty_hard(test_client):
    """Filter by hard returns 2 hard problems."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=hard")
    assert len(resp.json()) == 2


def test_filter_by_pattern(test_client):
    """Filter by pattern returns exact match."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?pattern=hash_map")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["pattern"] == "hash_map"


def test_filter_by_pattern_no_match(test_client):
    """Filter by non-existent pattern returns empty."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?pattern=nonexistent")
    assert resp.json() == []
    assert resp.headers["X-Total-Count"] == "0"


def test_filter_by_source_contains(test_client):
    """Source filter uses contains -- 'blind75' matches 'blind75' and 'blind75+neetcode150'."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?source=blind75")
    data = resp.json()
    assert len(data) == 3
    for p in data:
        assert "blind75" in p["source"]


def test_filter_by_source_neetcode(test_client):
    """Source neetcode150 matches 2 problems."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?source=neetcode150")
    data = resp.json()
    assert len(data) == 2
    for p in data:
        assert "neetcode150" in p["source"]


def test_filter_by_company_json_contains(test_client):
    """Company filter matches within JSON array text."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?company=google")
    data = resp.json()
    assert len(data) == 3
    for p in data:
        assert "google" in p["company_tags"]


def test_filter_by_company_amazon(test_client):
    """Company amazon matches 2 problems."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?company=amazon")
    data = resp.json()
    assert len(data) == 2
    for p in data:
        assert "amazon" in p["company_tags"]


def test_filter_by_company_no_match(test_client):
    """Company filter with non-existent company returns empty."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?company=netflix")
    assert resp.json() == []


def test_filter_by_is_completed_false(test_client):
    """Filter is_completed=false returns all (none completed by default)."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?is_completed=false")
    assert len(resp.json()) == 6


def test_filter_by_is_completed_true(test_client):
    """Filter is_completed=true returns empty when none completed."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?is_completed=true")
    assert resp.json() == []


def test_filter_by_is_completed_after_attempt(test_client):
    """is_completed filter works after marking a problem completed via attempt."""
    created = _seed_diverse_problems(test_client)
    pid = created[0]["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })

    resp = test_client.get("/api/problems?is_completed=true")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == pid


def test_filter_by_category(test_client):
    """Category filter returns only matching category."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?category=ml_coding")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "ml_coding"


def test_filter_by_category_system_design(test_client):
    """System design category returns 1 problem."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?category=system_design")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Sys Design Chat"


# ===========================================================================
# GET /api/problems -- multiple filters AND together
# ===========================================================================

def test_filters_and_together_difficulty_pattern(test_client):
    """Difficulty + pattern filters AND together."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=medium&pattern=two_pointers")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "3Sum"


def test_filters_and_together_difficulty_category(test_client):
    """Difficulty + category filters AND together."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=hard&category=system_design")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Sys Design Chat"


def test_filters_and_together_source_company(test_client):
    """Source + company filters AND together."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?source=blind75&company=meta")
    data = resp.json()
    # Two Sum (blind75, meta+google) matches
    assert len(data) == 1
    assert data[0]["title"] == "Two Sum"


def test_filters_and_together_all(test_client):
    """All filters combined returns very narrow result."""
    _seed_diverse_problems(test_client)
    resp = test_client.get(
        "/api/problems?difficulty=easy&pattern=hash_map&source=blind75"
        "&company=google&is_completed=false&category=algorithm"
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Two Sum"


def test_filters_and_together_no_match(test_client):
    """Conflicting filters return empty."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=easy&category=ml_coding")
    assert resp.json() == []


# ===========================================================================
# GET /api/problems -- X-Total-Count header
# ===========================================================================

def test_x_total_count_header(test_client):
    """X-Total-Count reflects total matching, not paginated count."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?limit=2")
    assert resp.headers["X-Total-Count"] == "6"
    assert len(resp.json()) == 2


def test_x_total_count_with_filter(test_client):
    """X-Total-Count reflects filtered total, not overall total."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?difficulty=medium&limit=1")
    assert resp.headers["X-Total-Count"] == "3"
    assert len(resp.json()) == 1


# ===========================================================================
# GET /api/problems -- sorting
# ===========================================================================

def test_sort_by_created_at_desc_default(test_client):
    """Default sort is created_at desc (newest first)."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems")
    data = resp.json()
    assert data[0]["title"] == "Sys Design Chat"  # last created


def test_sort_by_created_at_asc(test_client):
    """Sort created_at asc returns oldest first."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?sort_by=created_at&sort_order=asc")
    data = resp.json()
    assert data[0]["title"] == "Two Sum"  # first created


def test_sort_by_comfort_level(test_client):
    """Sort by comfort_level works."""
    created = _seed_diverse_problems(test_client)
    # Give different comfort levels via PUT
    test_client.put(f"/api/problems/{created[0]['id']}", json={"comfort_level": 5})
    test_client.put(f"/api/problems/{created[1]['id']}", json={"comfort_level": 2})

    resp = test_client.get("/api/problems?sort_by=comfort_level&sort_order=desc")
    data = resp.json()
    assert data[0]["comfort_level"] >= data[1]["comfort_level"]


def test_sort_by_comfort_level_asc(test_client):
    """Sort by comfort_level asc returns lowest first."""
    created = _seed_diverse_problems(test_client)
    test_client.put(f"/api/problems/{created[0]['id']}", json={"comfort_level": 5})

    resp = test_client.get("/api/problems?sort_by=comfort_level&sort_order=asc")
    data = resp.json()
    assert data[0]["comfort_level"] == 0  # default


# ===========================================================================
# GET /api/problems -- pagination
# ===========================================================================

def test_pagination_limit_offset(test_client):
    """Pagination with limit and offset returns correct slice."""
    _seed_diverse_problems(test_client)

    # Get all sorted by created_at asc for predictable order
    all_resp = test_client.get("/api/problems?sort_by=created_at&sort_order=asc")
    all_data = all_resp.json()

    # Get page 2 (offset=2, limit=2)
    resp = test_client.get(
        "/api/problems?sort_by=created_at&sort_order=asc&limit=2&offset=2"
    )
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == all_data[2]["id"]
    assert data[1]["id"] == all_data[3]["id"]


def test_pagination_offset_beyond_total(test_client):
    """Offset beyond total returns empty list."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?offset=100")
    assert resp.json() == []
    assert resp.headers["X-Total-Count"] == "6"


def test_pagination_limit_1(test_client):
    """Limit=1 returns exactly 1 problem."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?limit=1")
    assert len(resp.json()) == 1


def test_pagination_last_page_partial(test_client):
    """Last page with fewer items than limit returns remaining items."""
    _seed_diverse_problems(test_client)
    resp = test_client.get("/api/problems?limit=4&offset=4")
    data = resp.json()
    assert len(data) == 2  # 6 total, offset 4 -> 2 remaining


# ===========================================================================
# POST /api/problems -- create
# ===========================================================================

def test_create_problem(test_client):
    """POST /api/problems creates and returns problem."""
    resp = test_client.post("/api/problems", json={
        "title": "Two Sum",
        "difficulty": "easy",
        "tags": ["array", "hash-table"],
        "pattern": "hash_map",
        "leetcode_id": 1,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["title"] == "Two Sum"
    assert data["tags"] == ["array", "hash-table"]


def test_create_problem_duplicate_leetcode_id(test_client):
    """Duplicate leetcode_id returns 409."""
    test_client.post("/api/problems", json={
        "title": "Two Sum", "leetcode_id": 1,
    })
    resp = test_client.post("/api/problems", json={
        "title": "Two Sum v2", "leetcode_id": 1,
    })
    assert resp.status_code == 409


def test_create_problems_null_leetcode_id(test_client):
    """Two problems with null leetcode_id both succeed."""
    r1 = test_client.post("/api/problems", json={"title": "A"})
    r2 = test_client.post("/api/problems", json={"title": "B"})
    assert r1.status_code == 201
    assert r2.status_code == 201


# ===========================================================================
# PUT/DELETE /api/problems
# ===========================================================================

def test_update_problem_partial(test_client):
    """PUT with partial data only updates specified fields."""
    resp = test_client.post("/api/problems", json={
        "title": "Original", "difficulty": "easy", "pattern": "dp",
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"difficulty": "hard"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["difficulty"] == "hard"
    assert data["title"] == "Original"  # unchanged
    assert data["pattern"] == "dp"  # unchanged


def test_delete_problem(test_client):
    """DELETE returns 204, subsequent GET returns 404."""
    resp = test_client.post("/api/problems", json={"title": "ToDelete"})
    pid = resp.json()["id"]

    resp = test_client.delete(f"/api/problems/{pid}")
    assert resp.status_code == 204

    resp = test_client.get("/api/problems")
    assert all(p["id"] != pid for p in resp.json())


def test_update_delete_404(test_client):
    """PUT/DELETE on non-existent id returns 404."""
    assert test_client.put("/api/problems/99999", json={"title": "X"}).status_code == 404
    assert test_client.delete("/api/problems/99999").status_code == 404


# ===========================================================================
# POST/GET /api/problems/{id}/attempts
# ===========================================================================

def test_create_attempt(test_client):
    """Creating an attempt updates problem state."""
    resp = test_client.post("/api/problems", json={"title": "Test"})
    pid = resp.json()["id"]

    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })
    assert resp.status_code == 201

    # Verify problem updated
    resp = test_client.get("/api/problems")
    problem = [p for p in resp.json() if p["id"] == pid][0]
    assert problem["comfort_level"] == 4
    assert problem["is_completed"] is True
    assert problem["next_review_at"] is not None


def test_attempt_is_completed_sticky(test_client):
    """is_completed stays True even on low comfort."""
    resp = test_client.post("/api/problems", json={"title": "Sticky"})
    pid = resp.json()["id"]

    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "hint", "comfort_after": 2,
    })

    resp = test_client.get("/api/problems")
    problem = [p for p in resp.json() if p["id"] == pid][0]
    assert problem["is_completed"] is True
    assert problem["comfort_level"] == 2


def test_list_attempts_order(test_client):
    """GET attempts returns newest first."""
    resp = test_client.post("/api/problems", json={"title": "Order"})
    pid = resp.json()["id"]

    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })

    resp = test_client.get(f"/api/problems/{pid}/attempts")
    attempts = resp.json()
    assert len(attempts) == 2
    assert attempts[0]["comfort_after"] == 5  # newest first


# ===========================================================================
# GET /api/problems/stats and /api/problems/review-queue
# ===========================================================================

def test_problem_stats_empty(test_client):
    """Stats on empty DB returns zeros."""
    resp = test_client.get("/api/problems/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["completed"] == 0


def test_review_queue_empty(test_client):
    """Review queue on empty DB returns []."""
    resp = test_client.get("/api/problems/review-queue")
    assert resp.status_code == 200
    assert resp.json() == []
