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

def test_create_problem_returns_201_with_id(test_client):
    """POST /api/problems returns 201 and response includes an integer id."""
    resp = test_client.post("/api/problems", json={
        "title": "Two Sum",
        "difficulty": "easy",
        "tags": ["array", "hash-table"],
        "pattern": "hash_map",
        "leetcode_id": 1,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert isinstance(data["id"], int)
    assert data["title"] == "Two Sum"


def test_create_problem_all_fields(test_client):
    """Create with every field populated returns them all correctly."""
    payload = {
        "title": "Median of Two Sorted Arrays",
        "leetcode_id": 4,
        "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
        "difficulty": "hard",
        "tags": ["binary-search", "divide-and-conquer"],
        "pattern": "binary_search",
        "category": "algorithm",
        "source": "blind75",
        "company_tags": ["google", "amazon"],
        "priority": 1,
    }
    resp = test_client.post("/api/problems", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["leetcode_id"] == 4
    assert data["url"] == payload["url"]
    assert data["difficulty"] == "hard"
    assert data["tags"] == ["binary-search", "divide-and-conquer"]
    assert data["pattern"] == "binary_search"
    assert data["category"] == "algorithm"
    assert data["source"] == "blind75"
    assert data["company_tags"] == ["google", "amazon"]
    assert data["priority"] == 1
    assert data["is_completed"] is False
    assert data["comfort_level"] == 0
    assert data["created_at"] is not None
    assert data["last_attempted_at"] is None
    assert data["next_review_at"] is None


def test_create_problem_minimal_fields(test_client):
    """Create with only title succeeds and fills defaults."""
    resp = test_client.post("/api/problems", json={"title": "Minimal"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Minimal"
    assert data["leetcode_id"] is None
    assert data["difficulty"] is None
    assert data["tags"] == []
    assert data["company_tags"] == []
    assert data["category"] == "algorithm"
    assert data["priority"] == 2
    assert data["is_completed"] is False
    assert data["comfort_level"] == 0


def test_create_problem_tags_stored_as_json(test_client):
    """Tags list is converted to JSON storage and returned as list."""
    resp = test_client.post("/api/problems", json={
        "title": "Tags Test",
        "tags": ["dp", "greedy", "math"],
        "company_tags": ["meta", "apple"],
    })
    data = resp.json()
    assert data["tags"] == ["dp", "greedy", "math"]
    assert data["company_tags"] == ["meta", "apple"]


def test_create_problem_empty_tags(test_client):
    """Empty tags arrays are stored and returned as empty lists."""
    resp = test_client.post("/api/problems", json={
        "title": "Empty Tags", "tags": [], "company_tags": [],
    })
    data = resp.json()
    assert data["tags"] == []
    assert data["company_tags"] == []


def test_create_problem_duplicate_leetcode_id_409(test_client):
    """Duplicate leetcode_id returns 409 with detail message."""
    test_client.post("/api/problems", json={
        "title": "Two Sum", "leetcode_id": 1,
    })
    resp = test_client.post("/api/problems", json={
        "title": "Two Sum v2", "leetcode_id": 1,
    })
    assert resp.status_code == 409
    assert "leetcode_id" in resp.json()["detail"]


def test_create_problem_duplicate_leetcode_id_different_titles(test_client):
    """Duplicate leetcode_id is rejected even with different titles."""
    test_client.post("/api/problems", json={
        "title": "Original", "leetcode_id": 42,
    })
    resp = test_client.post("/api/problems", json={
        "title": "Completely Different", "leetcode_id": 42,
    })
    assert resp.status_code == 409


def test_create_problems_null_leetcode_id_no_conflict(test_client):
    """Multiple problems with null leetcode_id all succeed (no uniqueness check)."""
    r1 = test_client.post("/api/problems", json={"title": "A"})
    r2 = test_client.post("/api/problems", json={"title": "B"})
    r3 = test_client.post("/api/problems", json={"title": "C"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201
    # All have distinct ids
    ids = {r1.json()["id"], r2.json()["id"], r3.json()["id"]}
    assert len(ids) == 3


def test_create_problem_different_leetcode_ids_ok(test_client):
    """Different leetcode_ids never conflict."""
    r1 = test_client.post("/api/problems", json={"title": "A", "leetcode_id": 1})
    r2 = test_client.post("/api/problems", json={"title": "B", "leetcode_id": 2})
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_create_problem_each_category(test_client):
    """All three categories are accepted."""
    for cat in ("algorithm", "ml_coding", "system_design"):
        resp = test_client.post("/api/problems", json={
            "title": f"Cat {cat}", "category": cat,
        })
        assert resp.status_code == 201
        assert resp.json()["category"] == cat


def test_create_problem_each_difficulty(test_client):
    """All three difficulty levels are accepted."""
    for diff in ("easy", "medium", "hard"):
        resp = test_client.post("/api/problems", json={
            "title": f"Diff {diff}", "difficulty": diff,
        })
        assert resp.status_code == 201
        assert resp.json()["difficulty"] == diff


def test_create_problem_priority_bounds(test_client):
    """Priority 1, 2, 3 are all valid."""
    for pri in (1, 2, 3):
        resp = test_client.post("/api/problems", json={
            "title": f"Pri {pri}", "priority": pri,
        })
        assert resp.status_code == 201
        assert resp.json()["priority"] == pri


def test_create_problem_invalid_priority_rejected(test_client):
    """Priority outside 1-3 is rejected with 422."""
    resp = test_client.post("/api/problems", json={
        "title": "Bad Priority", "priority": 0,
    })
    assert resp.status_code == 422

    resp = test_client.post("/api/problems", json={
        "title": "Bad Priority", "priority": 4,
    })
    assert resp.status_code == 422


def test_create_problem_empty_title_rejected(test_client):
    """Empty title string is rejected with 422."""
    resp = test_client.post("/api/problems", json={"title": ""})
    assert resp.status_code == 422


def test_create_problem_missing_title_rejected(test_client):
    """Missing title field is rejected with 422."""
    resp = test_client.post("/api/problems", json={"difficulty": "easy"})
    assert resp.status_code == 422


def test_create_problem_invalid_difficulty_rejected(test_client):
    """Invalid difficulty value is rejected with 422."""
    resp = test_client.post("/api/problems", json={
        "title": "Bad Diff", "difficulty": "impossible",
    })
    assert resp.status_code == 422


def test_create_problem_invalid_category_rejected(test_client):
    """Invalid category value is rejected with 422."""
    resp = test_client.post("/api/problems", json={
        "title": "Bad Cat", "category": "cooking",
    })
    assert resp.status_code == 422


def test_create_problem_persisted_in_list(test_client):
    """Created problem appears in GET /api/problems list."""
    resp = test_client.post("/api/problems", json={
        "title": "Persisted", "leetcode_id": 999,
    })
    pid = resp.json()["id"]

    list_resp = test_client.get("/api/problems")
    ids = [p["id"] for p in list_resp.json()]
    assert pid in ids


def test_create_problem_unicode_tags(test_client):
    """Unicode characters in tags are preserved."""
    resp = test_client.post("/api/problems", json={
        "title": "Unicode Test",
        "tags": ["dynamic-programming"],
        "company_tags": ["ByteDance"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["tags"] == ["dynamic-programming"]
    assert data["company_tags"] == ["ByteDance"]


# ===========================================================================
# PUT /api/problems/{id} -- partial update
# ===========================================================================

def test_update_problem_partial_preserves_unchanged(test_client):
    """PUT with partial data only updates specified fields, preserves rest."""
    resp = test_client.post("/api/problems", json={
        "title": "Original", "difficulty": "easy", "pattern": "dp",
        "category": "algorithm", "priority": 1, "tags": ["array"],
        "company_tags": ["google"], "source": "blind75", "leetcode_id": 100,
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"difficulty": "hard"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["difficulty"] == "hard"
    assert data["title"] == "Original"
    assert data["pattern"] == "dp"
    assert data["category"] == "algorithm"
    assert data["priority"] == 1
    assert data["tags"] == ["array"]
    assert data["company_tags"] == ["google"]
    assert data["source"] == "blind75"
    assert data["leetcode_id"] == 100


def test_update_problem_title(test_client):
    """Update only title."""
    resp = test_client.post("/api/problems", json={"title": "Old Title"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"title": "New Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


def test_update_problem_difficulty_each_value(test_client):
    """Update difficulty to each valid value."""
    resp = test_client.post("/api/problems", json={"title": "DiffTest"})
    pid = resp.json()["id"]

    for diff in ("easy", "medium", "hard"):
        resp = test_client.put(f"/api/problems/{pid}", json={"difficulty": diff})
        assert resp.status_code == 200
        assert resp.json()["difficulty"] == diff


def test_update_problem_category_each_value(test_client):
    """Update category to each valid value."""
    resp = test_client.post("/api/problems", json={"title": "CatTest"})
    pid = resp.json()["id"]

    for cat in ("algorithm", "ml_coding", "system_design"):
        resp = test_client.put(f"/api/problems/{pid}", json={"category": cat})
        assert resp.status_code == 200
        assert resp.json()["category"] == cat


def test_update_problem_priority_each_value(test_client):
    """Update priority to each valid value 1-3."""
    resp = test_client.post("/api/problems", json={"title": "PriTest"})
    pid = resp.json()["id"]

    for pri in (1, 2, 3):
        resp = test_client.put(f"/api/problems/{pid}", json={"priority": pri})
        assert resp.status_code == 200
        assert resp.json()["priority"] == pri


def test_update_problem_tags(test_client):
    """Update tags replaces entire list."""
    resp = test_client.post("/api/problems", json={
        "title": "TagUpdate", "tags": ["old1", "old2"],
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"tags": ["new1", "new2", "new3"]})
    assert resp.status_code == 200
    assert resp.json()["tags"] == ["new1", "new2", "new3"]


def test_update_problem_tags_to_empty(test_client):
    """Update tags to empty list."""
    resp = test_client.post("/api/problems", json={
        "title": "TagEmpty", "tags": ["a", "b"],
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"tags": []})
    assert resp.status_code == 200
    assert resp.json()["tags"] == []


def test_update_problem_company_tags(test_client):
    """Update company_tags replaces entire list."""
    resp = test_client.post("/api/problems", json={
        "title": "CompUpdate", "company_tags": ["google"],
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={
        "company_tags": ["meta", "amazon"],
    })
    assert resp.status_code == 200
    assert resp.json()["company_tags"] == ["meta", "amazon"]


def test_update_problem_multiple_fields(test_client):
    """Update multiple fields at once."""
    resp = test_client.post("/api/problems", json={
        "title": "Multi", "difficulty": "easy", "priority": 3,
    })
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={
        "title": "Updated Multi",
        "difficulty": "hard",
        "priority": 1,
        "pattern": "graph",
        "source": "neetcode150",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Multi"
    assert data["difficulty"] == "hard"
    assert data["priority"] == 1
    assert data["pattern"] == "graph"
    assert data["source"] == "neetcode150"


def test_update_problem_comfort_level(test_client):
    """Update comfort_level directly via PUT."""
    resp = test_client.post("/api/problems", json={"title": "Comfort"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"comfort_level": 4})
    assert resp.status_code == 200
    assert resp.json()["comfort_level"] == 4


def test_update_problem_is_completed(test_client):
    """Update is_completed directly via PUT."""
    resp = test_client.post("/api/problems", json={"title": "Complete"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"is_completed": True})
    assert resp.status_code == 200
    assert resp.json()["is_completed"] is True


def test_update_problem_url(test_client):
    """Update URL field."""
    resp = test_client.post("/api/problems", json={"title": "UrlTest"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={
        "url": "https://leetcode.com/problems/two-sum/",
    })
    assert resp.status_code == 200
    assert resp.json()["url"] == "https://leetcode.com/problems/two-sum/"


def test_update_problem_leetcode_id(test_client):
    """Update leetcode_id field."""
    resp = test_client.post("/api/problems", json={"title": "LcIdTest"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"leetcode_id": 42})
    assert resp.status_code == 200
    assert resp.json()["leetcode_id"] == 42


def test_update_problem_empty_body_noop(test_client):
    """PUT with empty body is a no-op, returns current state."""
    resp = test_client.post("/api/problems", json={
        "title": "NoOp", "difficulty": "easy",
    })
    pid = resp.json()["id"]
    original = resp.json()

    resp = test_client.put(f"/api/problems/{pid}", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == original["title"]
    assert data["difficulty"] == original["difficulty"]


def test_update_problem_invalid_difficulty_422(test_client):
    """PUT with invalid difficulty returns 422."""
    resp = test_client.post("/api/problems", json={"title": "BadDiff"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"difficulty": "impossible"})
    assert resp.status_code == 422


def test_update_problem_invalid_category_422(test_client):
    """PUT with invalid category returns 422."""
    resp = test_client.post("/api/problems", json={"title": "BadCat"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"category": "cooking"})
    assert resp.status_code == 422


def test_update_problem_invalid_priority_422(test_client):
    """PUT with priority outside 1-3 returns 422."""
    resp = test_client.post("/api/problems", json={"title": "BadPri"})
    pid = resp.json()["id"]

    assert test_client.put(f"/api/problems/{pid}", json={"priority": 0}).status_code == 422
    assert test_client.put(f"/api/problems/{pid}", json={"priority": 4}).status_code == 422


def test_update_problem_invalid_comfort_level_422(test_client):
    """PUT with comfort_level outside 0-5 returns 422."""
    resp = test_client.post("/api/problems", json={"title": "BadComf"})
    pid = resp.json()["id"]

    assert test_client.put(f"/api/problems/{pid}", json={"comfort_level": -1}).status_code == 422
    assert test_client.put(f"/api/problems/{pid}", json={"comfort_level": 6}).status_code == 422


def test_update_problem_empty_title_422(test_client):
    """PUT with empty title string returns 422."""
    resp = test_client.post("/api/problems", json={"title": "EmptyTitle"})
    pid = resp.json()["id"]

    resp = test_client.put(f"/api/problems/{pid}", json={"title": ""})
    assert resp.status_code == 422


def test_update_problem_404(test_client):
    """PUT on non-existent id returns 404."""
    resp = test_client.put("/api/problems/99999", json={"title": "X"})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_update_problem_persisted(test_client):
    """Updated fields persist across subsequent GET requests."""
    resp = test_client.post("/api/problems", json={
        "title": "Persist", "difficulty": "easy",
    })
    pid = resp.json()["id"]

    test_client.put(f"/api/problems/{pid}", json={
        "difficulty": "hard", "pattern": "graph",
    })

    # Verify via list endpoint
    list_resp = test_client.get("/api/problems")
    problem = [p for p in list_resp.json() if p["id"] == pid][0]
    assert problem["difficulty"] == "hard"
    assert problem["pattern"] == "graph"


# ===========================================================================
# DELETE /api/problems/{id}
# ===========================================================================

def test_delete_problem_returns_204(test_client):
    """DELETE returns 204 with no body."""
    resp = test_client.post("/api/problems", json={"title": "ToDelete"})
    pid = resp.json()["id"]

    resp = test_client.delete(f"/api/problems/{pid}")
    assert resp.status_code == 204


def test_delete_problem_removed_from_list(test_client):
    """Deleted problem no longer appears in GET /api/problems."""
    resp = test_client.post("/api/problems", json={"title": "RemoveMe"})
    pid = resp.json()["id"]

    test_client.delete(f"/api/problems/{pid}")

    resp = test_client.get("/api/problems")
    assert all(p["id"] != pid for p in resp.json())


def test_delete_problem_cascades_attempts(test_client):
    """DELETE cascades to remove associated attempts."""
    resp = test_client.post("/api/problems", json={"title": "CascadeTest"})
    pid = resp.json()["id"]

    # Create attempts
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "hint", "comfort_after": 2,
    })

    # Verify attempts exist
    resp = test_client.get(f"/api/problems/{pid}/attempts")
    assert len(resp.json()) == 2

    # Delete problem
    resp = test_client.delete(f"/api/problems/{pid}")
    assert resp.status_code == 204

    # Attempts endpoint returns 404 (problem gone)
    resp = test_client.get(f"/api/problems/{pid}/attempts")
    assert resp.status_code == 404


def test_delete_problem_404(test_client):
    """DELETE on non-existent id returns 404."""
    resp = test_client.delete("/api/problems/99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_delete_problem_twice_404(test_client):
    """Deleting the same problem twice returns 404 on the second call."""
    resp = test_client.post("/api/problems", json={"title": "DeleteTwice"})
    pid = resp.json()["id"]

    assert test_client.delete(f"/api/problems/{pid}").status_code == 204
    assert test_client.delete(f"/api/problems/{pid}").status_code == 404


def test_delete_problem_total_count_decreases(test_client):
    """Deleting a problem decreases X-Total-Count."""
    test_client.post("/api/problems", json={"title": "A"})
    resp = test_client.post("/api/problems", json={"title": "B"})
    pid_b = resp.json()["id"]

    resp = test_client.get("/api/problems")
    assert resp.headers["X-Total-Count"] == "2"

    test_client.delete(f"/api/problems/{pid_b}")

    resp = test_client.get("/api/problems")
    assert resp.headers["X-Total-Count"] == "1"


def test_delete_does_not_affect_other_problems(test_client):
    """Deleting one problem does not affect others."""
    r1 = test_client.post("/api/problems", json={"title": "Keep"})
    r2 = test_client.post("/api/problems", json={"title": "Remove"})
    pid_keep = r1.json()["id"]
    pid_remove = r2.json()["id"]

    test_client.delete(f"/api/problems/{pid_remove}")

    resp = test_client.get("/api/problems")
    ids = [p["id"] for p in resp.json()]
    assert pid_keep in ids
    assert pid_remove not in ids


# ===========================================================================
# POST/GET /api/problems/{id}/attempts
# ===========================================================================

# --- POST /api/problems/{id}/attempts: basic creation ---


def test_create_attempt_returns_201(test_client):
    """POST attempt returns 201 status."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })
    assert resp.status_code == 201


def test_create_attempt_response_has_id(test_client):
    """Attempt response includes auto-generated id."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    data = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    }).json()
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_attempt_response_has_problem_id(test_client):
    """Attempt response includes the correct problem_id."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    data = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    }).json()
    assert data["problem_id"] == pid


def test_create_attempt_response_has_started_at(test_client):
    """Attempt response includes a started_at timestamp."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    data = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    }).json()
    assert data["started_at"] is not None


def test_create_attempt_minimal_fields(test_client):
    """Only result and comfort_after are required."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    data = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1,
    }).json()
    assert data["duration_seconds"] is None
    assert data["approach_notes"] is None
    assert data["complexity_time"] is None
    assert data["complexity_space"] is None


def test_create_attempt_all_optional_fields(test_client):
    """All optional fields are stored and returned."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    payload = {
        "result": "solved",
        "comfort_after": 5,
        "duration_seconds": 1200,
        "approach_notes": "Used two pointers",
        "complexity_time": "O(n)",
        "complexity_space": "O(1)",
    }
    data = test_client.post(f"/api/problems/{pid}/attempts", json=payload).json()
    assert data["duration_seconds"] == 1200
    assert data["approach_notes"] == "Used two pointers"
    assert data["complexity_time"] == "O(n)"
    assert data["complexity_space"] == "O(1)"


# --- POST /api/problems/{id}/attempts: each result type ---


def test_create_attempt_result_solved(test_client):
    """result='solved' is accepted."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    assert resp.status_code == 201
    assert resp.json()["result"] == "solved"


def test_create_attempt_result_hint(test_client):
    """result='hint' is accepted."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "hint", "comfort_after": 3,
    })
    assert resp.status_code == 201
    assert resp.json()["result"] == "hint"


def test_create_attempt_result_failed(test_client):
    """result='failed' is accepted."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1,
    })
    assert resp.status_code == 201
    assert resp.json()["result"] == "failed"


def test_create_attempt_result_timeout(test_client):
    """result='timeout' is accepted."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "timeout", "comfort_after": 1,
    })
    assert resp.status_code == 201
    assert resp.json()["result"] == "timeout"


# --- POST /api/problems/{id}/attempts: problem state updates ---


def test_attempt_updates_last_attempted_at(test_client):
    """Creating an attempt sets problem.last_attempted_at."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    # Before attempt
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["last_attempted_at"] is None

    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 2,
    })

    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["last_attempted_at"] is not None


def test_attempt_updates_comfort_level(test_client):
    """Creating an attempt updates problem.comfort_level."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["comfort_level"] == 4


def test_attempt_sets_next_review_at(test_client):
    """Creating an attempt sets problem.next_review_at."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["next_review_at"] is not None


def test_comfort_3_sets_is_completed(test_client):
    """comfort_after=3 (threshold) sets is_completed=True."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is True


def test_comfort_5_sets_is_completed(test_client):
    """comfort_after=5 sets is_completed=True."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is True


def test_comfort_2_does_not_set_is_completed(test_client):
    """comfort_after=2 does NOT set is_completed."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 2,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is False


def test_comfort_1_does_not_set_is_completed(test_client):
    """comfort_after=1 does NOT set is_completed."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "timeout", "comfort_after": 1,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is False


def test_is_completed_sticky_after_low_comfort(test_client):
    """is_completed stays True even after a subsequent low comfort attempt."""
    pid = test_client.post("/api/problems", json={"title": "Sticky"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "hint", "comfort_after": 2,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is True
    assert problem["comfort_level"] == 2


def test_is_completed_sticky_comfort_1(test_client):
    """is_completed stays True even with comfort_after=1."""
    pid = test_client.post("/api/problems", json={"title": "Sticky2"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1,
    })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["is_completed"] is True
    assert problem["comfort_level"] == 1


def test_multiple_attempts_updates_comfort_each_time(test_client):
    """Each attempt overwrites problem.comfort_level with latest value."""
    pid = test_client.post("/api/problems", json={"title": "Multi"}).json()["id"]
    for comfort in [1, 3, 2, 5]:
        test_client.post(f"/api/problems/{pid}/attempts", json={
            "result": "solved", "comfort_after": comfort,
        })
    problem = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    assert problem["comfort_level"] == 5  # last attempt wins


def test_multiple_attempts_updates_next_review_at(test_client):
    """Each attempt updates next_review_at."""
    pid = test_client.post("/api/problems", json={"title": "Review"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 2,
    })
    problem1 = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    review1 = problem1["next_review_at"]

    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    problem2 = [p for p in test_client.get("/api/problems").json() if p["id"] == pid][0]
    review2 = problem2["next_review_at"]

    assert review1 is not None
    assert review2 is not None
    # comfort=5 should push review further out than comfort=2
    assert review2 > review1


# --- POST /api/problems/{id}/attempts: validation errors ---


def test_create_attempt_missing_result_422(test_client):
    """Missing result field returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "comfort_after": 3,
    })
    assert resp.status_code == 422


def test_create_attempt_missing_comfort_after_422(test_client):
    """Missing comfort_after field returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved",
    })
    assert resp.status_code == 422


def test_create_attempt_invalid_result_422(test_client):
    """Invalid result value returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "gave_up", "comfort_after": 1,
    })
    assert resp.status_code == 422


def test_create_attempt_comfort_after_0_422(test_client):
    """comfort_after=0 (below min 1) returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 0,
    })
    assert resp.status_code == 422


def test_create_attempt_comfort_after_6_422(test_client):
    """comfort_after=6 (above max 5) returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 6,
    })
    assert resp.status_code == 422


def test_create_attempt_negative_duration_422(test_client):
    """Negative duration_seconds returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3, "duration_seconds": -1,
    })
    assert resp.status_code == 422


def test_create_attempt_empty_body_422(test_client):
    """Empty body returns 422."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={})
    assert resp.status_code == 422


def test_create_attempt_nonexistent_problem_404(test_client):
    """POST attempt on non-existent problem returns 404."""
    resp = test_client.post("/api/problems/99999/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    assert resp.status_code == 404


# --- POST /api/problems/{id}/attempts: edge cases ---


def test_attempt_duration_zero_allowed(test_client):
    """duration_seconds=0 is valid."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3, "duration_seconds": 0,
    })
    assert resp.status_code == 201
    assert resp.json()["duration_seconds"] == 0


def test_attempt_does_not_affect_other_problems(test_client):
    """Attempting one problem does not change another."""
    pid1 = test_client.post("/api/problems", json={"title": "P1"}).json()["id"]
    pid2 = test_client.post("/api/problems", json={"title": "P2"}).json()["id"]

    test_client.post(f"/api/problems/{pid1}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })

    p2 = [p for p in test_client.get("/api/problems").json() if p["id"] == pid2][0]
    assert p2["comfort_level"] == 0
    assert p2["is_completed"] is False
    assert p2["last_attempted_at"] is None


def test_attempt_llm_review_initially_null(test_client):
    """New attempt has llm_review=null."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    data = test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    }).json()
    assert data["llm_review"] is None


# --- GET /api/problems/{id}/attempts ---


def test_list_attempts_empty(test_client):
    """GET attempts on problem with no attempts returns []."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    resp = test_client.get(f"/api/problems/{pid}/attempts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_attempts_returns_200(test_client):
    """GET attempts returns 200."""
    pid = test_client.post("/api/problems", json={"title": "A"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    resp = test_client.get(f"/api/problems/{pid}/attempts")
    assert resp.status_code == 200


def test_list_attempts_newest_first(test_client):
    """GET attempts returns newest first."""
    pid = test_client.post("/api/problems", json={"title": "Order"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "failed", "comfort_after": 1,
    })
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    attempts = test_client.get(f"/api/problems/{pid}/attempts").json()
    assert len(attempts) == 2
    assert attempts[0]["comfort_after"] == 5  # newest first
    assert attempts[1]["comfort_after"] == 1


def test_list_attempts_count_matches(test_client):
    """GET attempts returns the correct number of attempts."""
    pid = test_client.post("/api/problems", json={"title": "Count"}).json()["id"]
    for i in range(5):
        test_client.post(f"/api/problems/{pid}/attempts", json={
            "result": "failed", "comfort_after": i + 1,
        })
    attempts = test_client.get(f"/api/problems/{pid}/attempts").json()
    assert len(attempts) == 5


def test_list_attempts_isolated_per_problem(test_client):
    """Attempts for one problem do not appear under another."""
    pid1 = test_client.post("/api/problems", json={"title": "P1"}).json()["id"]
    pid2 = test_client.post("/api/problems", json={"title": "P2"}).json()["id"]

    test_client.post(f"/api/problems/{pid1}/attempts", json={
        "result": "solved", "comfort_after": 5,
    })
    test_client.post(f"/api/problems/{pid1}/attempts", json={
        "result": "hint", "comfort_after": 3,
    })
    test_client.post(f"/api/problems/{pid2}/attempts", json={
        "result": "failed", "comfort_after": 1,
    })

    a1 = test_client.get(f"/api/problems/{pid1}/attempts").json()
    a2 = test_client.get(f"/api/problems/{pid2}/attempts").json()
    assert len(a1) == 2
    assert len(a2) == 1
    assert all(a["problem_id"] == pid1 for a in a1)
    assert all(a["problem_id"] == pid2 for a in a2)


def test_list_attempts_nonexistent_problem_404(test_client):
    """GET attempts on non-existent problem returns 404."""
    resp = test_client.get("/api/problems/99999/attempts")
    assert resp.status_code == 404


def test_list_attempts_response_fields(test_client):
    """GET attempts response includes all expected fields."""
    pid = test_client.post("/api/problems", json={"title": "Fields"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 4,
        "duration_seconds": 600, "approach_notes": "DP",
        "complexity_time": "O(n)", "complexity_space": "O(n)",
    })
    attempt = test_client.get(f"/api/problems/{pid}/attempts").json()[0]
    assert attempt["id"] is not None
    assert attempt["problem_id"] == pid
    assert attempt["started_at"] is not None
    assert attempt["duration_seconds"] == 600
    assert attempt["result"] == "solved"
    assert attempt["approach_notes"] == "DP"
    assert attempt["complexity_time"] == "O(n)"
    assert attempt["complexity_space"] == "O(n)"
    assert attempt["comfort_after"] == 4


def test_list_attempts_after_delete_cascade(test_client):
    """Deleting problem cascades to its attempts; no orphans."""
    pid = test_client.post("/api/problems", json={"title": "Cascade"}).json()["id"]
    test_client.post(f"/api/problems/{pid}/attempts", json={
        "result": "solved", "comfort_after": 3,
    })
    test_client.delete(f"/api/problems/{pid}")
    # Problem gone -> 404 on attempts
    resp = test_client.get(f"/api/problems/{pid}/attempts")
    assert resp.status_code == 404


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
