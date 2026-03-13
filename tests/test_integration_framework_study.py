"""Integration test: framework + study planning.

Full journey: load seed framework -> log study sessions -> verify progress
-> create company + weights -> get study suggestions -> verify urgency ordering.
"""

from datetime import date
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_company(client, name="Google", **overrides):
    """Create a company and return (response, id)."""
    payload = {
        "name": name,
        "group_tag": "FAANG",
        "status": "applied",
        "interview_stages": [{"stage": "phone_screen"}, {"stage": "onsite"}],
        "notes": "Target company",
    }
    payload.update(overrides)
    resp = client.post("/api/companies", json=payload)
    return resp, resp.json().get("id") if resp.status_code == 201 else None


def _log_study(client, node_id, duration_minutes=60, activity_type="practice",
               study_date=None):
    """Log a study session for a framework node."""
    if study_date is None:
        study_date = date.today().isoformat()
    return client.post(f"/api/framework/nodes/{node_id}/log", json={
        "date": study_date,
        "duration_minutes": duration_minutes,
        "activity_type": activity_type,
        "notes": "Integration test study session",
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFrameworkTreeAndStudyLogs:
    """Seed framework -> log study -> verify progress auto-calculation."""

    def test_seed_framework_appears_in_tree(self, test_client, seed_framework):
        """Seed framework nodes are returned in the tree endpoint."""
        resp = test_client.get("/api/framework/tree")
        assert resp.status_code == 200
        tree = resp.json()
        assert len(tree) >= 1
        root = tree[0]
        assert root["title"] == "Coding & Algorithms"
        assert root["depth"] == 0
        # Child should be nested
        assert len(root["children"]) == 1
        assert root["children"][0]["title"] == "Dynamic Programming"

    def test_tree_max_depth_filter(self, test_client, seed_framework):
        """max_depth=0 returns only root nodes without children."""
        resp = test_client.get("/api/framework/tree?max_depth=0")
        assert resp.status_code == 200
        tree = resp.json()
        assert len(tree) == 1
        assert tree[0]["children"] == []

    def test_log_study_auto_progress(self, test_client, seed_framework):
        """Logging study time auto-updates progress_pct based on estimated_hours."""
        root, child = seed_framework
        # Child has estimated_hours=10. Log 3 hours -> 30% progress
        resp = _log_study(test_client, child.id, duration_minutes=180)
        assert resp.status_code == 201
        log_data = resp.json()
        assert log_data["duration_minutes"] == 180
        assert log_data["framework_node_id"] == child.id

        # Verify node progress updated
        tree_resp = test_client.get("/api/framework/tree")
        tree = tree_resp.json()
        dp_node = tree[0]["children"][0]
        assert dp_node["progress_pct"] == pytest.approx(30.0, abs=0.1)

    def test_multiple_study_logs_accumulate(self, test_client, seed_framework):
        """Multiple study sessions accumulate progress."""
        _root, child = seed_framework
        # Log 3 hours twice -> 6h / 10h = 60%
        _log_study(test_client, child.id, duration_minutes=180)
        _log_study(test_client, child.id, duration_minutes=180)

        tree_resp = test_client.get("/api/framework/tree")
        dp_node = tree_resp.json()[0]["children"][0]
        assert dp_node["progress_pct"] == pytest.approx(60.0, abs=0.1)

    def test_progress_caps_at_95(self, test_client, seed_framework):
        """Progress from study logs caps at 95%, not 100%."""
        _root, child = seed_framework
        # Log 20 hours for a 10h topic -> should cap at 95
        _log_study(test_client, child.id, duration_minutes=1200)

        tree_resp = test_client.get("/api/framework/tree")
        dp_node = tree_resp.json()[0]["children"][0]
        assert dp_node["progress_pct"] == 95.0

    def test_log_for_nonexistent_node_404(self, test_client):
        """Logging study for missing node returns 404."""
        resp = _log_study(test_client, 9999)
        assert resp.status_code == 404


class TestFrameworkNodeUpdate:
    """Update node status and verify side effects."""

    def test_update_status_to_in_progress(self, test_client, seed_framework):
        """Setting status to in_progress sets started_at."""
        _root, child = seed_framework
        resp = test_client.put(f"/api/framework/nodes/{child.id}", json={
            "status": "in_progress",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_update_status_to_mastered(self, test_client, seed_framework):
        """Setting status to mastered sets progress to 100."""
        _root, child = seed_framework
        resp = test_client.put(f"/api/framework/nodes/{child.id}", json={
            "status": "mastered",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "mastered"
        assert data["progress_pct"] == 100.0

    def test_update_confidence_level(self, test_client, seed_framework):
        """Update confidence_level on a node."""
        _root, child = seed_framework
        resp = test_client.put(f"/api/framework/nodes/{child.id}", json={
            "confidence_level": 4,
        })
        assert resp.status_code == 200
        assert resp.json()["confidence_level"] == 4

    def test_update_nonexistent_node_404(self, test_client):
        """Updating a missing node returns 404."""
        resp = test_client.put("/api/framework/nodes/9999", json={
            "status": "mastered",
        })
        assert resp.status_code == 404


class TestFrameworkStats:
    """Verify aggregate stats endpoint."""

    def test_stats_with_seed_data(self, test_client, seed_framework):
        """Stats endpoint returns correct counts for seed framework."""
        resp = test_client.get("/api/framework/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_nodes"] == 2
        assert stats["by_status"]["not_started"] == 2
        assert stats["overall_progress_pct"] == 0.0
        assert stats["total_study_logs"] == 0

    def test_stats_after_study(self, test_client, seed_framework):
        """Stats reflect study activity."""
        _root, child = seed_framework
        _log_study(test_client, child.id, duration_minutes=60)

        resp = test_client.get("/api/framework/stats")
        stats = resp.json()
        assert stats["total_study_logs"] == 1
        assert stats["overall_progress_pct"] > 0

    def test_weakest_nodes_returned(self, test_client, seed_framework):
        """Weakest nodes include high-importance low-confidence nodes."""
        resp = test_client.get("/api/framework/stats")
        stats = resp.json()
        # Both seed nodes have importance >= 0.5 and confidence 0
        assert len(stats["weakest_nodes"]) == 2


class TestCompanyAndWeights:
    """Create company -> set topic weights -> verify company focus."""

    def test_create_company_and_set_weights(self, test_client, seed_framework):
        """Full flow: create company, set topic weights, verify via GET."""
        root, child = seed_framework

        # Create company
        resp, company_id = _create_company(test_client, name="Google")
        assert resp.status_code == 201
        assert company_id is not None

        # Set topic weights
        weights_resp = test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": root.id, "weight": 3.0},
            {"framework_node_id": child.id, "weight": 5.0},
        ])
        assert weights_resp.status_code == 200
        assert weights_resp.json() == {"inserted": 2, "updated": 0}

        # Verify company detail includes weights
        detail = test_client.get(f"/api/companies/{company_id}").json()
        assert len(detail["topic_weights"]) == 2
        weight_map = {w["node_id"]: w["weight"] for w in detail["topic_weights"]}
        assert weight_map[root.id] == 3.0
        assert weight_map[child.id] == 5.0

    def test_upsert_weights_updates_existing(self, test_client, seed_framework):
        """Upserting weights with existing node updates instead of inserting."""
        _root, child = seed_framework
        _, company_id = _create_company(test_client, name="Meta")

        # Insert
        test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": child.id, "weight": 2.0},
        ])
        # Update
        resp = test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": child.id, "weight": 4.5},
        ])
        assert resp.json() == {"inserted": 0, "updated": 1}

        detail = test_client.get(f"/api/companies/{company_id}").json()
        assert detail["topic_weights"][0]["weight"] == 4.5

    def test_company_focus_filters_high_progress(self, test_client, seed_framework):
        """Focus endpoint excludes nodes with progress >= 80%."""
        root, child = seed_framework
        _, company_id = _create_company(test_client, name="Amazon")

        # Set weights for both nodes
        test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": root.id, "weight": 3.0},
            {"framework_node_id": child.id, "weight": 4.0},
        ])

        # Both at 0% progress -> both in focus
        focus = test_client.get(f"/api/companies/{company_id}/focus").json()
        assert len(focus) == 2
        # Ordered by weight DESC
        assert focus[0]["weight"] >= focus[1]["weight"]

        # Set child to mastered (100% progress)
        test_client.put(f"/api/framework/nodes/{child.id}", json={
            "status": "mastered",
        })

        # Now only root should be in focus
        focus2 = test_client.get(f"/api/companies/{company_id}/focus").json()
        assert len(focus2) == 1
        assert focus2[0]["node_id"] == root.id

    def test_duplicate_company_409(self, test_client):
        """Creating a company with same name returns 409."""
        _create_company(test_client, name="Apple")
        resp, _ = _create_company(test_client, name="Apple")
        assert resp.status_code == 409

    def test_weights_for_nonexistent_company_404(self, test_client):
        """Setting weights for missing company returns 404."""
        resp = test_client.post("/api/companies/9999/weights", json=[
            {"framework_node_id": 1, "weight": 1.0},
        ])
        assert resp.status_code == 404


class TestStudySuggestions:
    """Verify study plan generation and urgency ordering."""

    def test_suggest_returns_topics_ordered_by_urgency(
        self, test_client, seed_framework
    ):
        """Suggestions are ordered by urgency descending."""
        resp = test_client.get("/api/framework/suggest?hours=3&days=14")
        assert resp.status_code == 200
        data = resp.json()
        topics = data["structured"]
        assert len(topics) == 2  # both seed nodes (neither mastered)
        assert data["plan_text"] is None

        # Verify descending urgency
        for i in range(len(topics) - 1):
            assert topics[i]["urgency"] >= topics[i + 1]["urgency"]

        # Verify time allocation sums to ~180 minutes
        total_allocated = sum(t["allocated_minutes"] for t in topics)
        assert 170 <= total_allocated <= 190  # roughly 3 hours

    def test_mastered_nodes_excluded(self, test_client, seed_framework):
        """Mastered nodes are excluded from suggestions."""
        _root, child = seed_framework
        # Master the child
        test_client.put(f"/api/framework/nodes/{child.id}", json={
            "status": "mastered",
        })

        resp = test_client.get("/api/framework/suggest?hours=2&days=7")
        topics = resp.json()["structured"]
        node_ids = [t["node_id"] for t in topics]
        assert child.id not in node_ids

    def test_company_weights_boost_urgency(self, test_client, seed_framework):
        """Company topic weights amplify urgency for weighted nodes."""
        root, child = seed_framework

        # Get baseline urgency without company
        baseline = test_client.get("/api/framework/suggest?hours=3&days=14").json()
        baseline_urgency = {
            t["node_id"]: t["urgency"] for t in baseline["structured"]
        }

        # Create company with high weight on child
        _, company_id = _create_company(test_client, name="WeightTest")
        test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": child.id, "weight": 5.0},
        ])

        # Get suggestions with company
        boosted = test_client.get(
            f"/api/framework/suggest?hours=3&days=14&company_ids={company_id}"
        ).json()
        boosted_urgency = {
            t["node_id"]: t["urgency"] for t in boosted["structured"]
        }

        # Child urgency should be boosted by factor of 5
        assert boosted_urgency[child.id] > baseline_urgency[child.id]

    def test_study_reduces_urgency(self, test_client, seed_framework):
        """Studying a topic reduces its urgency (higher progress -> lower urgency)."""
        _root, child = seed_framework

        # Baseline urgency
        before = test_client.get("/api/framework/suggest?hours=3&days=14").json()
        before_urgency = {
            t["node_id"]: t["urgency"] for t in before["structured"]
        }

        # Study the child heavily
        _log_study(test_client, child.id, duration_minutes=300)

        # Urgency should decrease
        after = test_client.get("/api/framework/suggest?hours=3&days=14").json()
        after_urgency = {
            t["node_id"]: t["urgency"] for t in after["structured"]
        }

        assert after_urgency[child.id] < before_urgency[child.id]

    def test_shorter_deadline_increases_urgency(self, test_client, seed_framework):
        """Shorter deadline produces higher urgency scores."""
        far = test_client.get("/api/framework/suggest?hours=3&days=30").json()
        near = test_client.get("/api/framework/suggest?hours=3&days=3").json()

        far_max = max(t["urgency"] for t in far["structured"])
        near_max = max(t["urgency"] for t in near["structured"])
        assert near_max > far_max


class TestStudySuggestionsWithLLM:
    """Suggest endpoint with use_llm=true."""

    def test_suggest_with_llm(self, test_client, seed_framework, mock_llm_text):
        """use_llm=true returns plan_text from LLM."""
        with patch(
            "src.backend.services.llm_service.LLMService",
            return_value=mock_llm_text,
        ):
            resp = test_client.get(
                "/api/framework/suggest?hours=3&days=14&use_llm=true"
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan_text"] is not None
        assert len(data["plan_text"]) > 0
        assert len(data["structured"]) > 0


class TestEndToEndJourney:
    """Full integration journey combining all pieces."""

    def test_full_framework_study_journey(self, test_client, seed_framework):
        """Complete journey: seed -> study -> company -> suggestions -> verify."""
        root, child = seed_framework

        # 1. Verify initial state via stats
        stats = test_client.get("/api/framework/stats").json()
        assert stats["total_nodes"] == 2
        assert stats["overall_progress_pct"] == 0.0

        # 2. Update child to in_progress
        test_client.put(f"/api/framework/nodes/{child.id}", json={
            "status": "in_progress",
            "confidence_level": 1,
        })

        # 3. Log study session on child (3h / 10h estimated = 30%)
        log_resp = _log_study(test_client, child.id, duration_minutes=180)
        assert log_resp.status_code == 201

        # 4. Verify progress updated
        tree = test_client.get("/api/framework/tree").json()
        dp_node = tree[0]["children"][0]
        assert dp_node["status"] == "in_progress"
        assert dp_node["progress_pct"] == pytest.approx(30.0, abs=0.1)

        # 5. Create company with weights favoring DP
        _, company_id = _create_company(test_client, name="JourneyTestCo")
        test_client.post(f"/api/companies/{company_id}/weights", json=[
            {"framework_node_id": root.id, "weight": 1.0},
            {"framework_node_id": child.id, "weight": 4.0},
        ])

        # 6. Get focus topics for company
        focus = test_client.get(f"/api/companies/{company_id}/focus").json()
        assert len(focus) == 2
        # Both under 80% progress

        # 7. Get study suggestions with company weighting
        suggest = test_client.get(
            f"/api/framework/suggest?hours=5&days=7&company_ids={company_id}"
        ).json()
        topics = suggest["structured"]
        assert len(topics) == 2

        # Urgency order should be descending
        assert topics[0]["urgency"] >= topics[1]["urgency"]

        # Time allocated should sum to ~300 minutes (5 hours)
        total_min = sum(t["allocated_minutes"] for t in topics)
        assert 290 <= total_min <= 310

        # 8. Verify stats reflect the study
        final_stats = test_client.get("/api/framework/stats").json()
        assert final_stats["total_study_logs"] == 1
        assert final_stats["overall_progress_pct"] > 0
        assert final_stats["by_status"]["in_progress"] == 1


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_suggest_empty_framework(self, test_client):
        """Suggestions on empty framework returns empty list."""
        resp = test_client.get("/api/framework/suggest?hours=3&days=14")
        assert resp.status_code == 200
        assert resp.json()["structured"] == []

    def test_focus_empty_weights(self, test_client, seed_framework):
        """Focus with no weights returns empty list."""
        _, company_id = _create_company(test_client, name="NoWeights")
        focus = test_client.get(f"/api/companies/{company_id}/focus").json()
        assert focus == []

    def test_study_log_validation(self, test_client, seed_framework):
        """Study log with invalid duration is rejected."""
        _root, child = seed_framework
        resp = test_client.post(f"/api/framework/nodes/{child.id}/log", json={
            "date": date.today().isoformat(),
            "duration_minutes": 0,  # must be >= 1
        })
        assert resp.status_code == 422

    def test_company_update(self, test_client):
        """Company can be partially updated."""
        _, company_id = _create_company(test_client, name="UpdateTest")
        resp = test_client.put(f"/api/companies/{company_id}", json={
            "status": "onsite",
            "notes": "Updated notes",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "onsite"
        assert resp.json()["notes"] == "Updated notes"
        # name unchanged
        assert resp.json()["name"] == "UpdateTest"

    def test_company_list_filter_by_status(self, test_client):
        """List companies filtered by status."""
        _create_company(test_client, name="StatusA", status="applied")
        _create_company(test_client, name="StatusB", status="onsite")

        applied = test_client.get("/api/companies?status=applied").json()
        assert all(c["status"] == "applied" for c in applied)

        onsite = test_client.get("/api/companies?status=onsite").json()
        assert all(c["status"] == "onsite" for c in onsite)

