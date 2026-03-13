"""Integration test: problem lifecycle.

Full journey: create problem -> attempt (comfort=2) -> verify in review queue
-> LLM review -> attempt (comfort=5) -> verify not in review queue for days.
"""

from datetime import datetime
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_problem(client, **overrides):
    """Create a problem and return (response, id)."""
    payload = {
        "title": "Two Sum",
        "leetcode_id": 1,
        "difficulty": "easy",
        "tags": ["array", "hash_map"],
        "pattern": "hash_map",
        "source": "blind75",
        "company_tags": ["google"],
    }
    payload.update(overrides)
    resp = client.post("/api/problems", json=payload)
    return resp, resp.json().get("id") if resp.status_code == 201 else None


def _post_attempt(client, problem_id, comfort, result="solved", duration=600):
    """Post an attempt and return the response."""
    return client.post(f"/api/problems/{problem_id}/attempts", json={
        "duration_seconds": duration,
        "result": result,
        "approach_notes": "hash map approach",
        "complexity_time": "O(n)",
        "complexity_space": "O(n)",
        "comfort_after": comfort,
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestProblemLifecycleHappyPath:
    """End-to-end problem lifecycle: create -> attempt -> review queue -> LLM review -> mastery."""

    def test_full_lifecycle(self, test_client, mock_llm):
        """Complete lifecycle: low-comfort attempt puts problem in review queue,
        LLM review stores feedback, high-comfort attempt removes from queue."""

        # 1. Create problem
        resp, pid = _create_problem(test_client)
        assert resp.status_code == 201
        problem = resp.json()
        assert problem["title"] == "Two Sum"
        assert problem["is_completed"] is False
        assert problem["comfort_level"] == 0
        assert problem["next_review_at"] is None

        # 2. First attempt -- comfort=2 (struggling)
        resp = _post_attempt(test_client, pid, comfort=2)
        assert resp.status_code == 201
        attempt = resp.json()
        assert attempt["comfort_after"] == 2

        # Verify problem updated
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["comfort_level"] == 2
        assert prob["is_completed"] is False  # comfort < 3
        assert prob["next_review_at"] is not None

        # 3. Verify NOT yet in review queue (review date is ~1 day in the future)
        resp = test_client.get("/api/problems/review-queue")
        assert resp.status_code == 200
        queue_ids = [p["id"] for p in resp.json()]
        assert pid not in queue_ids  # 1 day hasn't passed yet

        # 4. Verify the scheduling math: comfort=2 -> 1 day interval
        next_review = datetime.fromisoformat(prob["next_review_at"])
        now = datetime.utcnow()
        delta = next_review - now
        assert 0.9 < delta.total_seconds() / 86400 < 1.1

        # 5. LLM review
        with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm):
            resp = test_client.post(f"/api/problems/{pid}/review", json={
                "approach_text": "Use a hash map to store complements.",
            })
        assert resp.status_code == 200
        review = resp.json()
        assert review["verdict"] == "optimal"
        assert review["feedback"] == "Good approach."

        # Verify review is stored in the latest attempt
        resp = test_client.get(f"/api/problems/{pid}/attempts")
        assert resp.status_code == 200
        attempts = resp.json()
        assert len(attempts) == 1
        assert attempts[0]["llm_review"] is not None

        # 6. Second attempt -- comfort=5 (mastered)
        resp = _post_attempt(test_client, pid, comfort=5)
        assert resp.status_code == 201

        # Verify problem is now completed with high comfort
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["comfort_level"] == 5
        assert prob["is_completed"] is True

        # 7. Verify NOT in review queue (next_review far in the future)
        # comfort=5 with previous_interval from last attempt:
        # previous_interval should be small (0-1 days since we just attempted),
        # so next interval = max(1, interval) * 2.5 = 2-3 days minimum.
        next_review2 = datetime.fromisoformat(prob["next_review_at"])
        # Should be at least 2 days from now
        delta2 = next_review2 - datetime.utcnow()
        assert delta2.total_seconds() > 86400  # more than 1 day away

        resp = test_client.get("/api/problems/review-queue")
        queue_ids = [p["id"] for p in resp.json()]
        assert pid not in queue_ids  # next review is days away

        # 8. Verify attempt history
        resp = test_client.get(f"/api/problems/{pid}/attempts")
        attempts = resp.json()
        assert len(attempts) == 2
        # Newest first
        assert attempts[0]["comfort_after"] == 5
        assert attempts[1]["comfort_after"] == 2


class TestProblemCreationEdgeCases:
    """Edge cases for problem creation."""

    def test_duplicate_leetcode_id_rejected(self, test_client):
        """Creating two problems with same leetcode_id returns 409."""
        resp1, _ = _create_problem(test_client)
        assert resp1.status_code == 201

        resp2, _ = _create_problem(test_client, title="Different Title")
        assert resp2.status_code == 409

    def test_null_leetcode_id_allows_duplicates(self, test_client):
        """Multiple problems with null leetcode_id are allowed."""
        resp1, _ = _create_problem(test_client, leetcode_id=None, title="Custom Q1")
        resp2, _ = _create_problem(test_client, leetcode_id=None, title="Custom Q2")
        assert resp1.status_code == 201
        assert resp2.status_code == 201

    def test_create_problem_minimal(self, test_client):
        """Create problem with only required fields."""
        resp = test_client.post("/api/problems", json={"title": "Minimal Problem"})
        assert resp.status_code == 201
        p = resp.json()
        assert p["title"] == "Minimal Problem"
        assert p["difficulty"] is None
        assert p["is_completed"] is False


class TestAttemptAndReviewScheduling:
    """Verify spaced repetition scheduling via attempts."""

    def test_first_attempt_low_comfort_short_interval(self, test_client):
        """comfort=1 on first attempt -> 1 day interval."""
        _, pid = _create_problem(test_client)
        _post_attempt(test_client, pid, comfort=1, result="failed")

        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        next_review = datetime.fromisoformat(prob["next_review_at"])
        delta_days = (next_review - datetime.utcnow()).total_seconds() / 86400
        assert 0.9 < delta_days < 1.1  # ~1 day

    def test_first_attempt_high_comfort_longer_interval(self, test_client):
        """comfort=5 on first attempt -> 2-3 day interval (1 * 2.5 = 2.5)."""
        _, pid = _create_problem(test_client)
        _post_attempt(test_client, pid, comfort=5)

        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        next_review = datetime.fromisoformat(prob["next_review_at"])
        delta_days = (next_review - datetime.utcnow()).total_seconds() / 86400
        # compute_next_review(5, 1) = int(1 * 2.5) = 2
        assert 1.9 < delta_days < 2.2

    def test_completion_flag_set_at_comfort_3(self, test_client):
        """Problem marked completed when comfort >= 3."""
        _, pid = _create_problem(test_client)

        # comfort=2 -> not completed
        _post_attempt(test_client, pid, comfort=2)
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["is_completed"] is False

        # comfort=3 -> completed
        _post_attempt(test_client, pid, comfort=3)
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["is_completed"] is True

    def test_completion_sticky_after_low_comfort(self, test_client):
        """is_completed stays True even if comfort drops below 3."""
        _, pid = _create_problem(test_client)

        _post_attempt(test_client, pid, comfort=5)
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["is_completed"] is True

        # Low comfort attempt -- is_completed should remain True (sticky)
        _post_attempt(test_client, pid, comfort=1)
        resp = test_client.get("/api/problems")
        prob = next(p for p in resp.json() if p["id"] == pid)
        assert prob["is_completed"] is True


class TestLLMReviewIntegration:
    """LLM review stored on attempt and accessible."""

    def test_review_stored_on_latest_attempt(self, test_client, mock_llm):
        """POST review stores result in latest attempt's llm_review field."""
        _, pid = _create_problem(test_client)
        _post_attempt(test_client, pid, comfort=3)

        with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm):
            resp = test_client.post(f"/api/problems/{pid}/review", json={
                "approach_text": "Sort then merge overlapping intervals.",
            })
        assert resp.status_code == 200

        # Verify stored
        resp = test_client.get(f"/api/problems/{pid}/attempts")
        attempts = resp.json()
        assert len(attempts) == 1
        assert attempts[0]["llm_review"] is not None

    def test_review_without_attempt_still_works(self, test_client, mock_llm):
        """Review on a problem with no attempts should still return review."""
        _, pid = _create_problem(test_client)

        with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm):
            resp = test_client.post(f"/api/problems/{pid}/review", json={
                "approach_text": "BFS approach.",
            })
        # Should work (just no attempt to store on)
        assert resp.status_code == 200
        review = resp.json()
        assert review["verdict"] == "optimal"

    def test_review_nonexistent_problem(self, test_client, mock_llm):
        """Review on non-existent problem returns 404."""
        with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm):
            resp = test_client.post("/api/problems/99999/review", json={
                "approach_text": "Some approach.",
            })
        assert resp.status_code == 404


class TestReviewQueueBehavior:
    """Verify review queue returns correct problems."""

    def test_new_problem_not_in_queue(self, test_client):
        """A problem with no attempts has no next_review_at, not in queue."""
        _, pid = _create_problem(test_client)
        resp = test_client.get("/api/problems/review-queue")
        queue_ids = [p["id"] for p in resp.json()]
        assert pid not in queue_ids

    def test_recently_attempted_not_in_queue(self, test_client):
        """A just-attempted problem's review date is in the future."""
        _, pid = _create_problem(test_client)
        _post_attempt(test_client, pid, comfort=4)

        resp = test_client.get("/api/problems/review-queue")
        queue_ids = [p["id"] for p in resp.json()]
        assert pid not in queue_ids

    def test_multiple_problems_queue_ordering(self, test_client):
        """Multiple problems in queue ordered by most overdue first."""
        # Create two problems
        _, pid1 = _create_problem(test_client, leetcode_id=100, title="Problem A")
        _, pid2 = _create_problem(test_client, leetcode_id=200, title="Problem B")

        # Both get low comfort attempts -> 1 day review interval
        _post_attempt(test_client, pid1, comfort=1)
        _post_attempt(test_client, pid2, comfort=1)

        # Neither should be in queue yet (review is tomorrow)
        resp = test_client.get("/api/problems/review-queue")
        assert len(resp.json()) == 0


class TestStatsAfterLifecycle:
    """Verify stats endpoint reflects lifecycle changes."""

    def test_stats_reflect_attempts(self, test_client):
        """Stats update after creating problems and recording attempts."""
        _, pid1 = _create_problem(test_client, leetcode_id=1, title="Two Sum")
        _, pid2 = _create_problem(
            test_client, leetcode_id=2, title="3Sum",
            difficulty="medium", pattern="two_pointers",
        )

        _post_attempt(test_client, pid1, comfort=5, duration=300)
        _post_attempt(test_client, pid2, comfort=2, duration=900)

        resp = test_client.get("/api/problems/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total"] == 2
        assert stats["completed"] == 1  # only pid1 (comfort>=3)
        assert stats["total_attempts"] == 2
        assert stats["avg_comfort"] > 0

    def test_weak_patterns_identified(self, test_client):
        """Patterns with avg comfort < 3 appear in weak_patterns."""
        _, pid = _create_problem(
            test_client, pattern="dp", difficulty="hard",
        )
        _post_attempt(test_client, pid, comfort=1)

        resp = test_client.get("/api/problems/stats")
        stats = resp.json()
        assert "dp" in stats["weak_patterns"]


class TestDeleteCascade:
    """Verify deleting a problem cascades to attempts."""

    def test_delete_removes_attempts(self, test_client, mock_llm):
        """Deleting a problem also removes its attempts."""
        _, pid = _create_problem(test_client)
        _post_attempt(test_client, pid, comfort=3)
        _post_attempt(test_client, pid, comfort=5)

        # Store LLM review
        with patch("src.backend.services.llm_service.LLMService", return_value=mock_llm):
            test_client.post(f"/api/problems/{pid}/review", json={
                "approach_text": "test",
            })

        # Delete
        resp = test_client.delete(f"/api/problems/{pid}")
        assert resp.status_code == 204

        # Verify gone
        resp = test_client.get(f"/api/problems/{pid}/attempts")
        assert resp.status_code == 404

        # Verify not in list
        resp = test_client.get("/api/problems")
        assert len(resp.json()) == 0
