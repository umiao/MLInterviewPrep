"""Tests for the T-P0-911 reconcile sweep driver.

Scope of this suite (the driver, NOT the shared helper -- that is
covered byte-for-byte by ``tests/test_framework_progress_helper.py``):

* **AC2 (scope pinned, Review B verbatim)**: the sweep touches ONLY
  fully-checked leaves and is provably disjoint from the reverse
  (pct>0/0-checked, 115/171 shape), partial-stale (node 92 shape), and
  no-checklist-drift (node 69 shape) classes -- enforced by
  :func:`assert_scope_pinned` and surfaced by :func:`classify_excluded`.
* **AC5 (not hardcoded)**: the would-change set is discovered by
  signature over the whole table; no id is enumerated literally.
* **AC6 (idempotent)**: a second pass after a committed apply yields an
  empty diff.
* **Dry-run guarantee**: :func:`compute_reconcile_diff` mutates the
  session but the caller's rollback leaves the DB unchanged.
"""
import sys
from datetime import datetime
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# The driver imports `from lib...` and `from src...`; importing it here
# is the same path the CLI uses.
import importlib  # noqa: E402

sweep = importlib.import_module(
    "reconcile_fully_checked_nodes_20260519"
)

from src.backend.models.framework import FrameworkNode  # noqa: E402

_FULL = "## Key Takeaways\n- [x] a\n- [x] b\n"
_PARTIAL = "## Key Takeaways\n- [x] a\n- [ ] b\n"
_ZERO = "## Key Takeaways\n- [ ] a\n- [ ] b\n"
_NO_BOX = "## Prose only\nNo checklist here.\n"


def _leaf(db, *, path, description=None, status="not_started",
          progress_pct=0.0, importance=1.0, parent_id=None, depth=1,
          stamped=False):
    """Insert one node and return it (flushed, id available).

    ``stamped=True`` sets ``started_at``/``completed_at`` so a
    fully-checked ``mastered/100`` node is a genuine reconcile no-op
    (an unstamped one is still drift -- the helper backfills the
    timestamps, exactly the node-44 already-mastered-but-NULL case).
    """
    ts = datetime(2026, 5, 1) if stamped else None
    n = FrameworkNode(
        parent_id=parent_id, path=path, depth=depth, title=path,
        importance=importance, priority="P0", estimated_hours=5,
        status=status, progress_pct=progress_pct, description=description,
        started_at=ts, completed_at=ts,
    )
    db.add(n)
    db.flush()
    return n


# ---------------------------------------------------------------------------
# AC2 / AC5 -- scope pinned, signature-discovered
# ---------------------------------------------------------------------------

class TestScopePinned:
    def test_only_fully_checked_unreconciled_is_in_diff(self, db_session):
        """A full-but-not-mastered leaf is the ONLY would-change node;
        reverse / partial-stale / no-checklist / already-mastered are
        all left out -- discovered by signature, not by id."""
        full = _leaf(db_session, path="p.full", description=_FULL,
                     status="not_started", progress_pct=100.0)
        already = _leaf(db_session, path="p.done", description=_FULL,
                        status="mastered", progress_pct=100.0,
                        stamped=True)
        reverse = _leaf(db_session, path="p.rev", description=_ZERO,
                        status="review", progress_pct=100.0)
        partial = _leaf(db_session, path="p.part", description=_PARTIAL,
                        status="not_started", progress_pct=0.0)
        nobox = _leaf(db_session, path="p.nb", description=_NO_BOX,
                      status="review", progress_pct=100.0)

        diff = sweep.compute_reconcile_diff(db_session)
        db_session.rollback()

        assert diff.changed_leaf_ids == [full.id]
        assert reverse.id in diff.excluded["reverse"]
        assert partial.id in diff.excluded["partial_stale"]
        assert nobox.id in diff.excluded["no_checklist_drift"]
        # already-mastered is fully-checked but is a no-op -> not changed
        assert already.id not in diff.changed_leaf_ids
        changed = {d.node_id for d in diff.deltas if d.kind ==
                   "reconciled-leaf"}
        assert changed == {full.id}
        # the excluded classes never appear as a changed delta
        assert reverse.id not in {d.node_id for d in diff.deltas}
        assert partial.id not in {d.node_id for d in diff.deltas}
        assert nobox.id not in {d.node_id for d in diff.deltas}

    def test_reverse_and_partial_untouched_after_rollback(self, db_session):
        """Dry-run guarantee: reverse + partial rows are byte-identical
        after the rollback the dry-run caller performs."""
        reverse = _leaf(db_session, path="p.rev", description=_ZERO,
                        status="review", progress_pct=100.0)
        partial = _leaf(db_session, path="p.part", description=_PARTIAL,
                        status="not_started", progress_pct=0.0)
        db_session.commit()

        sweep.compute_reconcile_diff(db_session)
        db_session.rollback()

        db_session.refresh(reverse)
        db_session.refresh(partial)
        assert (reverse.status, reverse.progress_pct) == ("review", 100.0)
        assert (partial.status, partial.progress_pct) == ("not_started", 0.0)

    def test_assert_scope_pinned_raises_on_synthetic_breach(self,
                                                            db_session):
        """Defense-in-depth tripwire: if a NON-fully-checked id were ever
        reported as changed, the guard aborts before any commit."""
        partial = _leaf(db_session, path="p.part", description=_PARTIAL)
        before = sweep.snapshot_states(db_session)
        with pytest.raises(sweep.ScopeViolationError):
            sweep.assert_scope_pinned(before, [partial.id])

    def test_assert_scope_pinned_raises_on_reverse_id(self, db_session):
        reverse = _leaf(db_session, path="p.rev", description=_ZERO,
                         status="review", progress_pct=100.0)
        before = sweep.snapshot_states(db_session)
        with pytest.raises(sweep.ScopeViolationError):
            sweep.assert_scope_pinned(before, [reverse.id])

    def test_assert_scope_pinned_passes_for_legit_full_leaf(self,
                                                            db_session):
        full = _leaf(db_session, path="p.full", description=_FULL,
                     status="not_started", progress_pct=100.0)
        before = sweep.snapshot_states(db_session)
        # no raise
        sweep.assert_scope_pinned(before, [full.id])


class TestClassifyExcluded:
    def test_buckets_each_class_correctly(self, db_session):
        rev = _leaf(db_session, path="c.rev", description=_ZERO,
                    status="review", progress_pct=100.0)
        part = _leaf(db_session, path="c.part", description=_PARTIAL)
        nb = _leaf(db_session, path="c.nb", description=_NO_BOX,
                   status="review", progress_pct=100.0)
        # a clean fully-checked leaf must NOT land in any excluded bucket
        full = _leaf(db_session, path="c.full", description=_FULL,
                     status="not_started", progress_pct=100.0)

        ex = sweep.classify_excluded(sweep.snapshot_states(db_session))
        assert rev.id in ex["reverse"]
        assert part.id in ex["partial_stale"]
        assert nb.id in ex["no_checklist_drift"]
        all_excluded = (set(ex["reverse"]) | set(ex["partial_stale"])
                        | set(ex["no_checklist_drift"]))
        assert full.id not in all_excluded


# ---------------------------------------------------------------------------
# AC6 -- idempotency + propagation visible in the diff
# ---------------------------------------------------------------------------

class TestIdempotencyAndPropagation:
    def test_second_pass_after_apply_is_empty(self, db_session):
        """Apply once (commit), then a fresh dry-run pass finds nothing
        -- the helper is idempotent so the diff is empty (AC6)."""
        _leaf(db_session, path="i.full", description=_FULL,
              status="not_started", progress_pct=100.0)
        db_session.commit()

        first = sweep.compute_reconcile_diff(db_session)
        assert len(first.changed_leaf_ids) == 1
        db_session.commit()  # simulate --apply

        second = sweep.compute_reconcile_diff(db_session)
        db_session.rollback()
        assert second.changed_leaf_ids == []
        assert second.deltas == []

    def test_propagated_ancestor_tagged_distinctly(self, db_session):
        """Reconciling a leaf rolls its parent up; the parent shows in
        the diff tagged 'propagated-ancestor', NOT 'reconciled-leaf'."""
        root = _leaf(db_session, path="r", depth=0, importance=1.0,
                     description=None)
        child = _leaf(db_session, path="r.c", parent_id=root.id,
                      description=_FULL, status="not_started",
                      progress_pct=100.0)

        diff = sweep.compute_reconcile_diff(db_session)
        db_session.rollback()

        kinds = {d.node_id: d.kind for d in diff.deltas}
        assert kinds[child.id] == "reconciled-leaf"
        assert kinds[root.id] == "propagated-ancestor"
        assert diff.changed_leaf_ids == [child.id]


# ---------------------------------------------------------------------------
# Report renderer -- shape only (content correctness covered above)
# ---------------------------------------------------------------------------

class TestReportRenderer:
    def test_report_lists_changed_and_excluded(self, db_session):
        full = _leaf(db_session, path="p.full", description=_FULL,
                     status="not_started", progress_pct=100.0)
        _leaf(db_session, path="p.rev", description=_ZERO,
              status="review", progress_pct=100.0)

        diff = sweep.compute_reconcile_diff(db_session)
        db_session.rollback()
        md = sweep.render_report(diff, "dry-run", datetime(2026, 5, 19))

        assert "T-P0-911" in md
        assert "ZERO DB writes" in md
        assert f"{full.id}" in md
        assert "OUT OF SCOPE" in md
        assert "T-P0-915" in md  # apply is the separate gated task

    def test_empty_diff_renders_idempotent_note(self, db_session):
        _leaf(db_session, path="p.done", description=_FULL,
              status="mastered", progress_pct=100.0, stamped=True)
        diff = sweep.compute_reconcile_diff(db_session)
        db_session.rollback()
        md = sweep.render_report(diff, "dry-run", datetime(2026, 5, 19))
        assert "idempotent re-run" in md
