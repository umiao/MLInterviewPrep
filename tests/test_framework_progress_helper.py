"""Test matrix for scripts/lib/framework_progress.py (T-P0-910).

Hard precondition for the T-P0-911 sweep: all green here gates that task --
no DB-wide reconcile sweep runs before this suite passes.

Covers (AC3): fully-checked / partially-checked / reverse (pct>0, 0 checked --
the 115/171 shape) / empty (no checkbox) / boundary (1/1, 0/1, NULL
description) + ancestor-propagation parity vs a HAND-computed weighted
average (independent oracle, not the production helper) + idempotency (AC4) +
both promote-only branches and the reverse no-zero guarantee (AC5).
"""
import sys
from pathlib import Path

import pytest

# scripts/ is not an importable package name in this workspace (a sibling
# project owns `scripts`); the repo convention is to put THIS project's
# scripts/ dir on sys.path and import `from lib.<mod>` (see
# scripts/sweep_stuck_leases.py, .claude/hooks/task_store.py).
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.framework_progress import (  # noqa: E402
    checkbox_progress_pct,
    count_checkboxes,
    reconcile_all_fully_checked,
    reconcile_node_from_checkboxes,
)

from src.backend.models.framework import FrameworkNode  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FULL_2 = "## Key Takeaways\n- [x] First idea\n- [x] Second idea\n"
_HALF_2 = "## Key Takeaways\n- [x] First idea\n- [ ] Second idea\n"
_ZERO_2 = "## Key Takeaways\n- [ ] First idea\n- [ ] Second idea\n"
_ONE_OF_1 = "- [x] only box\n"
_ZERO_OF_1 = "- [ ] only box\n"
_NO_BOX = "## Prose only\nThis node has no checklist at all.\n"


def _leaf(db, *, path, description=None, status="not_started",
          progress_pct=0.0, importance=1.0, parent_id=None, depth=1):
    """Insert one leaf node and return it (flushed, id available)."""
    n = FrameworkNode(
        parent_id=parent_id, path=path, depth=depth, title=path,
        importance=importance, priority="P0", estimated_hours=5,
        status=status, progress_pct=progress_pct, description=description,
    )
    db.add(n)
    db.flush()
    return n


# ---------------------------------------------------------------------------
# count_checkboxes / checkbox_progress_pct  (byte-faithful to the frontend)
# ---------------------------------------------------------------------------

class TestCheckboxParsing:
    def test_counts_checked_unchecked(self):
        assert count_checkboxes(_HALF_2) == (1, 2)
        assert count_checkboxes(_FULL_2) == (2, 2)
        assert count_checkboxes(_ZERO_2) == (0, 2)

    def test_null_and_empty_description(self):
        assert count_checkboxes(None) == (0, 0)
        assert count_checkboxes("") == (0, 0)
        assert count_checkboxes(_NO_BOX) == (0, 0)

    def test_asterisk_and_capital_x_and_indent(self):
        md = "  * [X] indented asterisk\n*  [ ] loose spacing\n"
        assert count_checkboxes(md) == (1, 2)

    def test_js_math_round_parity(self):
        """progress_pct must match the frontend Math.round (half-up), NOT
        Python banker's rounding (which would give 62 -> 6.2 for 1/16)."""
        assert checkbox_progress_pct(2, 2) == 100.0
        assert checkbox_progress_pct(1, 2) == 50.0
        assert checkbox_progress_pct(3, 4) == 75.0
        assert checkbox_progress_pct(1, 3) == 33.3
        assert checkbox_progress_pct(2, 3) == 66.7
        assert checkbox_progress_pct(1, 8) == 12.5
        assert checkbox_progress_pct(1, 16) == 6.3   # banker's would be 6.2
        assert checkbox_progress_pct(0, 5) == 0.0
        assert checkbox_progress_pct(0, 0) is None


# ---------------------------------------------------------------------------
# AC5 -- fully checked
# ---------------------------------------------------------------------------

class TestFullyChecked:
    def test_fully_checked_to_mastered_100(self, db_session):
        leaf = _leaf(db_session, path="p.full", description=_FULL_2)
        changed = reconcile_node_from_checkboxes(db_session, leaf.id)
        db_session.commit()
        db_session.refresh(leaf)
        assert changed is True
        assert leaf.status == "mastered"
        assert leaf.progress_pct == 100.0
        assert leaf.started_at is not None
        assert leaf.completed_at is not None

    def test_boundary_1_of_1_mastered(self, db_session):
        leaf = _leaf(db_session, path="p.one", description=_ONE_OF_1)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is True
        db_session.commit()
        db_session.refresh(leaf)
        assert (leaf.status, leaf.progress_pct) == ("mastered", 100.0)

    def test_review_node_promotes_to_mastered(self, db_session):
        """review -> mastered on a fully-checked leaf is a legit promotion
        (fully-checked is terminal), not a promote-only violation."""
        leaf = _leaf(db_session, path="p.rev", description=_FULL_2,
                     status="review", progress_pct=40.0)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is True
        db_session.commit()
        db_session.refresh(leaf)
        assert leaf.status == "mastered"
        assert leaf.progress_pct == 100.0


# ---------------------------------------------------------------------------
# AC5 -- partially checked (promote-only)
# ---------------------------------------------------------------------------

class TestPartiallyChecked:
    def test_partial_not_started_to_in_progress(self, db_session):
        leaf = _leaf(db_session, path="p.half", description=_HALF_2)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is True
        db_session.commit()
        db_session.refresh(leaf)
        assert leaf.status == "in_progress"
        assert leaf.progress_pct == 50.0
        assert leaf.started_at is not None
        assert leaf.completed_at is None

    def test_partial_promote_only_does_not_demote_mastered(self, db_session):
        """Already-mastered leaf: partial reconcile sets pct=ratio but the
        status is NOT demoted (byte-faithful promote-only)."""
        leaf = _leaf(db_session, path="p.hm", description=_HALF_2,
                     status="mastered", progress_pct=100.0)
        changed = reconcile_node_from_checkboxes(db_session, leaf.id)
        db_session.commit()
        db_session.refresh(leaf)
        assert changed is True
        assert leaf.status == "mastered"          # never demoted
        assert leaf.progress_pct == 50.0          # pct still re-derived

    def test_partial_already_in_progress_status_unchanged(self, db_session):
        leaf = _leaf(db_session, path="p.hi", description=_HALF_2,
                     status="in_progress", progress_pct=20.0)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is True
        db_session.commit()
        db_session.refresh(leaf)
        assert leaf.status == "in_progress"
        assert leaf.progress_pct == 50.0


# ---------------------------------------------------------------------------
# AC5 -- zero checked / REVERSE / empty / NULL  (no silent zeroing)
# ---------------------------------------------------------------------------

class TestZeroCheckedAndReverse:
    def test_zero_checked_fresh_node_noop(self, db_session):
        leaf = _leaf(db_session, path="p.zero", description=_ZERO_2)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is False
        assert leaf.status == "not_started"
        assert (leaf.progress_pct or 0.0) == 0.0

    def test_boundary_0_of_1_untouched(self, db_session):
        leaf = _leaf(db_session, path="p.zo", description=_ZERO_OF_1)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is False
        assert leaf.status == "not_started"

    def test_reverse_pct_gt_0_zero_checked_not_zeroed(self, db_session, caplog):
        """The 115/171 shape: pct>0, 0 boxes checked. The helper MUST NOT
        silently zero it -- it leaves the row untouched and flags a WARN."""
        leaf = _leaf(db_session, path="p.rev", description=_ZERO_2,
                     status="review", progress_pct=100.0)
        with caplog.at_level("WARNING"):
            changed = reconcile_node_from_checkboxes(db_session, leaf.id)
        assert changed is False
        db_session.refresh(leaf)
        assert leaf.status == "review"            # untouched
        assert leaf.progress_pct == 100.0         # NOT zeroed
        assert "REVERSE drift" in caplog.text

    def test_null_description_noop_never_crashes(self, db_session):
        leaf = _leaf(db_session, path="p.null", description=None)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is False

    def test_no_checkbox_prose_noop(self, db_session):
        leaf = _leaf(db_session, path="p.prose", description=_NO_BOX)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is False

    def test_missing_node_returns_false(self, db_session):
        assert reconcile_node_from_checkboxes(db_session, 999999) is False


# ---------------------------------------------------------------------------
# AC4 -- idempotency: second call returns False and writes nothing
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_second_call_is_noop_and_writes_nothing(self, db_session):
        leaf = _leaf(db_session, path="p.idem", description=_FULL_2)
        assert reconcile_node_from_checkboxes(db_session, leaf.id) is True
        db_session.commit()
        db_session.refresh(leaf)
        before = (leaf.status, leaf.progress_pct,
                  leaf.started_at, leaf.completed_at)

        second = reconcile_node_from_checkboxes(db_session, leaf.id)
        assert second is False
        # Nothing pending: no flush/UPDATE was issued.
        assert db_session.is_modified(leaf) is False
        assert not db_session.dirty
        db_session.refresh(leaf)
        assert (leaf.status, leaf.progress_pct,
                leaf.started_at, leaf.completed_at) == before


# ---------------------------------------------------------------------------
# AC3 -- ancestor propagation parity vs a HAND-computed weighted average
# ---------------------------------------------------------------------------

class TestAncestorPropagationParity:
    def test_equal_importance_parity(self, db_session):
        root = _leaf(db_session, path="r", depth=0, importance=1.0)
        a = _leaf(db_session, path="r.a", parent_id=root.id,
                  description=_FULL_2, importance=1.0)
        b = _leaf(db_session, path="r.b", parent_id=root.id,
                  description=_HALF_2, importance=1.0)

        reconcile_node_from_checkboxes(db_session, a.id)   # -> mastered/100
        reconcile_node_from_checkboxes(db_session, b.id)   # -> in_progress/50
        db_session.commit()
        db_session.refresh(root)

        # HAND oracle: weighted avg = (100*1 + 50*1) / (1+1) = 75.0
        # status: children {mastered, in_progress} -> in_progress
        assert root.progress_pct == pytest.approx(75.0, abs=0.05)
        assert root.status == "in_progress"

    def test_weighted_importance_parity(self, db_session):
        root = _leaf(db_session, path="w", depth=0, importance=1.0)
        # child c1 importance 3 fully checked (100), c2 importance 1 zero
        c1 = _leaf(db_session, path="w.c1", parent_id=root.id,
                   description=_FULL_2, importance=3.0)
        _leaf(db_session, path="w.c2", parent_id=root.id,
              description=_ZERO_2, importance=1.0)

        reconcile_node_from_checkboxes(db_session, c1.id)
        db_session.commit()
        db_session.refresh(root)

        # HAND oracle: (100*3 + 0*1) / (3+1) = 75.0
        assert root.progress_pct == pytest.approx(75.0, abs=0.05)
        # children {mastered, not_started} -> in_progress
        assert root.status == "in_progress"

    def test_grandparent_parity_two_levels(self, db_session):
        root = _leaf(db_session, path="g", depth=0, importance=1.0)
        mid = _leaf(db_session, path="g.m", parent_id=root.id, depth=1,
                    importance=1.0)
        gc1 = _leaf(db_session, path="g.m.1", parent_id=mid.id, depth=2,
                    description=_FULL_2, importance=1.0)
        gc2 = _leaf(db_session, path="g.m.2", parent_id=mid.id, depth=2,
                    description=_FULL_2, importance=1.0)

        reconcile_node_from_checkboxes(db_session, gc1.id)
        reconcile_node_from_checkboxes(db_session, gc2.id)
        db_session.commit()
        db_session.refresh(mid)
        db_session.refresh(root)

        # Both grandchildren mastered -> mid mastered/100 -> root mastered/100
        assert mid.progress_pct == pytest.approx(100.0, abs=0.05)
        assert mid.status == "mastered"
        assert root.progress_pct == pytest.approx(100.0, abs=0.05)
        assert root.status == "mastered"


# ---------------------------------------------------------------------------
# reconcile_all_fully_checked -- the T-P0-911 building block
# ---------------------------------------------------------------------------

class TestReconcileAllFullyChecked:
    def test_only_fully_checked_reconciled(self, db_session):
        full = _leaf(db_session, path="b.full", description=_FULL_2)
        half = _leaf(db_session, path="b.half", description=_HALF_2)
        rev = _leaf(db_session, path="b.rev", description=_ZERO_2,
                    status="review", progress_pct=100.0)
        nobox = _leaf(db_session, path="b.nb", description=_NO_BOX)

        changed = reconcile_all_fully_checked(db_session)
        db_session.commit()

        assert changed == [full.id]            # only the fully-checked one
        db_session.refresh(full)
        db_session.refresh(half)
        db_session.refresh(rev)
        db_session.refresh(nobox)
        assert full.status == "mastered"
        assert half.status == "not_started"    # partial: out of batch scope
        assert rev.status == "review"          # reverse class: never touched
        assert rev.progress_pct == 100.0
        assert nobox.status == "not_started"

    def test_batch_is_idempotent(self, db_session):
        _leaf(db_session, path="i.full", description=_FULL_2)
        first = reconcile_all_fully_checked(db_session)
        db_session.commit()
        assert len(first) == 1
        second = reconcile_all_fully_checked(db_session)
        assert second == []                    # nothing left to change
