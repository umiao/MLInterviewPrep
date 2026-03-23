"""Tests for framework progress/status propagation.

Covers: _derive_status, _propagate_upward, timestamps only-set-never-clear,
child deletion propagation, status rollback, cycle detection, and
study log auto-start + propagation.
"""

from datetime import date

import pytest

from src.backend.models.framework import FrameworkNode
from src.backend.routers.framework import _derive_status

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_tree(db, *, children_count=2, grandchildren_count=0):
    """Create a parent with N children (and optional grandchildren).

    Returns (parent, [children], [[grandchildren_per_child]]).
    """
    parent = FrameworkNode(
        path="pillar", depth=0, title="Root",
        importance=1.0, priority="P0", estimated_hours=40,
    )
    db.add(parent)
    db.flush()

    children = []
    all_grandchildren = []
    for i in range(children_count):
        child = FrameworkNode(
            parent_id=parent.id, path=f"pillar.c{i}", depth=1,
            title=f"Child-{i}", importance=1.0, priority="P0",
            estimated_hours=10,
        )
        db.add(child)
        db.flush()
        children.append(child)

        gc_list = []
        for j in range(grandchildren_count):
            gc = FrameworkNode(
                parent_id=child.id, path=f"pillar.c{i}.gc{j}", depth=2,
                title=f"GC-{i}-{j}", importance=1.0, priority="P0",
                estimated_hours=5,
            )
            db.add(gc)
            db.flush()
            gc_list.append(gc)
        all_grandchildren.append(gc_list)

    db.commit()
    for n in [parent] + children:
        db.refresh(n)
    for gc_list in all_grandchildren:
        for gc in gc_list:
            db.refresh(gc)
    return parent, children, all_grandchildren


def _update_node(client, node_id, **fields):
    """PUT /framework/nodes/{id} with given fields."""
    resp = client.put(f"/api/framework/nodes/{node_id}", json=fields)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _log_study(client, node_id, duration_minutes=60):
    """POST study log."""
    resp = client.post(f"/api/framework/nodes/{node_id}/log", json={
        "date": date.today().isoformat(),
        "duration_minutes": duration_minutes,
        "activity_type": "Practice",
        "notes": "test",
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# _derive_status unit tests
# ---------------------------------------------------------------------------

class TestDeriveStatus:
    """Unit tests for _derive_status helper."""

    def test_all_mastered(self):
        assert _derive_status(["mastered", "mastered"]) == "mastered"

    def test_all_not_started(self):
        assert _derive_status(["not_started", "not_started"]) == "not_started"

    def test_mixed_mastered_not_started(self):
        assert _derive_status(["mastered", "not_started"]) == "in_progress"

    def test_mixed_mastered_review(self):
        """[mastered, review] mix = in_progress (not review)."""
        assert _derive_status(["mastered", "review"]) == "in_progress"

    def test_mixed_in_progress_not_started(self):
        assert _derive_status(["in_progress", "not_started"]) == "in_progress"

    def test_all_in_progress(self):
        assert _derive_status(["in_progress", "in_progress"]) == "in_progress"

    def test_all_review(self):
        assert _derive_status(["review", "review"]) == "in_progress"

    def test_single_mastered(self):
        assert _derive_status(["mastered"]) == "mastered"

    def test_single_not_started(self):
        assert _derive_status(["not_started"]) == "not_started"


# ---------------------------------------------------------------------------
# Progress propagation
# ---------------------------------------------------------------------------

class TestProgressPropagation:
    """Parent progress = importance-weighted avg of children."""

    def test_parent_progress_from_children(self, test_client, db_session):
        """Updating child progress propagates to parent."""
        parent, children, _ = _seed_tree(db_session)

        # Set child-0 to 60%
        _update_node(test_client, children[0].id, progress_pct=60.0)

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["progress_pct"] == pytest.approx(30.0, abs=0.1)

    def test_weighted_progress(self, test_client, db_session):
        """Progress weights by importance."""
        parent = FrameworkNode(
            path="p", depth=0, title="P", importance=1.0,
            priority="P0", estimated_hours=40,
        )
        db_session.add(parent)
        db_session.flush()

        c1 = FrameworkNode(
            parent_id=parent.id, path="p.c1", depth=1, title="C1",
            importance=3.0, priority="P0", estimated_hours=10,
        )
        c2 = FrameworkNode(
            parent_id=parent.id, path="p.c2", depth=1, title="C2",
            importance=1.0, priority="P0", estimated_hours=10,
        )
        db_session.add_all([c1, c2])
        db_session.commit()

        # c1 (importance=3) at 100%, c2 (importance=1) at 0%
        _update_node(test_client, c1.id, progress_pct=100.0)

        tree = test_client.get("/api/framework/tree").json()
        # weighted: (100*3 + 0*1) / (3+1) = 75%
        assert tree[0]["progress_pct"] == pytest.approx(75.0, abs=0.1)

    def test_grandchild_propagates_to_root(self, test_client, db_session):
        """Changes propagate up multiple levels."""
        parent, children, grandchildren = _seed_tree(
            db_session, children_count=1, grandchildren_count=2,
        )

        # Set grandchild-0 to mastered (100%)
        _update_node(test_client, grandchildren[0][0].id, status="mastered")

        tree = test_client.get("/api/framework/tree").json()
        child_node = tree[0]["children"][0]
        # Child has 2 GC: one at 100%, one at 0% -> 50%
        assert child_node["progress_pct"] == pytest.approx(50.0, abs=0.1)
        # Root has 1 child at 50% -> 50%
        assert tree[0]["progress_pct"] == pytest.approx(50.0, abs=0.1)


# ---------------------------------------------------------------------------
# Status propagation + rollback
# ---------------------------------------------------------------------------

class TestStatusPropagation:
    """Parent status derived from children via _derive_status."""

    def test_all_children_mastered_parents_mastered(self, test_client, db_session):
        """When all children become mastered, parent becomes mastered."""
        parent, children, _ = _seed_tree(db_session)

        _update_node(test_client, children[0].id, status="mastered")
        _update_node(test_client, children[1].id, status="mastered")

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["status"] == "mastered"
        assert tree[0]["progress_pct"] == pytest.approx(100.0, abs=0.1)

    def test_status_rollback_mastered_to_in_progress(self, test_client, db_session):
        """Parent reverts from mastered when a child goes back to in_progress."""
        parent, children, _ = _seed_tree(db_session)

        # Both mastered
        _update_node(test_client, children[0].id, status="mastered")
        _update_node(test_client, children[1].id, status="mastered")
        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["status"] == "mastered"

        # Roll back child-1
        _update_node(test_client, children[1].id, status="in_progress", progress_pct=50.0)

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["status"] == "in_progress"
        # Progress: (100*1 + 50*1) / 2 = 75%
        assert tree[0]["progress_pct"] == pytest.approx(75.0, abs=0.1)

    def test_one_child_in_progress_parent_in_progress(self, test_client, db_session):
        """Mixed children -> parent in_progress."""
        parent, children, _ = _seed_tree(db_session)
        _update_node(test_client, children[0].id, status="in_progress")

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["status"] == "in_progress"

    def test_all_not_started_parent_not_started(self, test_client, db_session):
        """All not_started children -> parent not_started."""
        parent, children, _ = _seed_tree(db_session)

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["status"] == "not_started"


# ---------------------------------------------------------------------------
# Timestamps only-set-never-clear
# ---------------------------------------------------------------------------

class TestTimestamps:
    """started_at and completed_at are irreversible once set."""

    def test_started_at_set_on_in_progress(self, test_client, db_session):
        """started_at is set when moving to in_progress."""
        parent, children, _ = _seed_tree(db_session)
        _update_node(test_client, children[0].id, status="in_progress")

        db_session.refresh(children[0])
        assert children[0].started_at is not None

    def test_completed_at_set_on_mastered(self, test_client, db_session):
        """completed_at is set when reaching mastered."""
        parent, children, _ = _seed_tree(db_session)
        _update_node(test_client, children[0].id, status="mastered")

        db_session.refresh(children[0])
        assert children[0].completed_at is not None

    def test_completed_at_not_cleared_on_rollback(self, test_client, db_session):
        """completed_at is NOT cleared when leaving mastered."""
        parent, children, _ = _seed_tree(db_session)
        _update_node(test_client, children[0].id, status="mastered")

        db_session.refresh(children[0])
        original_completed_at = children[0].completed_at
        assert original_completed_at is not None

        # Roll back to in_progress
        _update_node(test_client, children[0].id, status="in_progress", progress_pct=50.0)

        db_session.refresh(children[0])
        # completed_at should still be set (never cleared)
        assert children[0].completed_at == original_completed_at

    def test_parent_timestamps_propagate(self, test_client, db_session):
        """Parent gets started_at/completed_at via propagation."""
        parent, children, _ = _seed_tree(db_session)

        # Start one child -> parent started
        _update_node(test_client, children[0].id, status="in_progress")
        db_session.refresh(parent)
        assert parent.started_at is not None
        assert parent.completed_at is None

        # Master both -> parent completed
        _update_node(test_client, children[0].id, status="mastered")
        _update_node(test_client, children[1].id, status="mastered")
        db_session.refresh(parent)
        assert parent.completed_at is not None

    def test_parent_completed_at_not_cleared(self, test_client, db_session):
        """Parent completed_at not cleared when child rolls back."""
        parent, children, _ = _seed_tree(db_session)

        _update_node(test_client, children[0].id, status="mastered")
        _update_node(test_client, children[1].id, status="mastered")
        db_session.refresh(parent)
        completed = parent.completed_at
        assert completed is not None

        # Roll back a child
        _update_node(test_client, children[1].id, status="in_progress", progress_pct=50.0)
        db_session.refresh(parent)
        # Parent completed_at preserved
        assert parent.completed_at == completed


# ---------------------------------------------------------------------------
# Child deletion propagation
# ---------------------------------------------------------------------------

class TestChildDeletionPropagation:
    """Deleting a child should leave parent in consistent state
    when parent is next recalculated."""

    def test_delete_child_parent_recalculated(self, test_client, db_session):
        """After deleting a child, updating the remaining child triggers
        correct parent recalculation."""
        parent, children, _ = _seed_tree(db_session)

        # Set child-0 to mastered (100%)
        _update_node(test_client, children[0].id, status="mastered")
        # Set child-1 to 50%
        _update_node(test_client, children[1].id, progress_pct=50.0)

        # Parent should be at (100+50)/2 = 75%
        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["progress_pct"] == pytest.approx(75.0, abs=0.1)

        # Delete child-1
        db_session.delete(children[1])
        db_session.commit()

        # Now trigger recalculation by updating remaining child
        _update_node(test_client, children[0].id, status="mastered")

        tree = test_client.get("/api/framework/tree").json()
        # Only child-0 at 100% remains
        assert tree[0]["progress_pct"] == pytest.approx(100.0, abs=0.1)
        assert tree[0]["status"] == "mastered"


# ---------------------------------------------------------------------------
# Study log auto-start + propagation
# ---------------------------------------------------------------------------

class TestStudyLogPropagation:
    """Study log creation triggers auto-start and propagation."""

    def test_study_log_auto_starts_not_started_node(self, test_client, db_session):
        """Logging study on not_started node transitions to in_progress."""
        parent, children, _ = _seed_tree(db_session)
        assert children[0].status == "not_started"

        _log_study(test_client, children[0].id, duration_minutes=30)

        tree = test_client.get("/api/framework/tree").json()
        child_data = tree[0]["children"][0]
        assert child_data["status"] == "in_progress"

    def test_study_log_propagates_to_parent(self, test_client, db_session):
        """Study log on child updates parent status and progress."""
        parent, children, _ = _seed_tree(db_session)

        _log_study(test_client, children[0].id, duration_minutes=60)

        tree = test_client.get("/api/framework/tree").json()
        # Parent should now be in_progress (one child in_progress, one not_started)
        assert tree[0]["status"] == "in_progress"
        # Parent progress > 0
        assert tree[0]["progress_pct"] > 0

    def test_study_log_does_not_affect_already_in_progress(self, test_client, db_session):
        """Study log on in_progress node doesn't change status."""
        parent, children, _ = _seed_tree(db_session)
        _update_node(test_client, children[0].id, status="in_progress")

        _log_study(test_client, children[0].id, duration_minutes=30)

        tree = test_client.get("/api/framework/tree").json()
        assert tree[0]["children"][0]["status"] == "in_progress"
