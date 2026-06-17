"""Tests for the T-P3-916 partial pct-stale decision-report audit.

Scope: the read-only classifier ``classify_partial_stale`` and the HTML
renderer in ``scripts/audit_partial_pct_stale_20260617.py``. The reconcile
*logic* itself (pct = checked-ratio, promote-only status) is the shared
T-P0-910 helper, covered byte-for-byte by
``tests/test_framework_progress_helper.py``; this suite proves only that the
report selects the RIGHT class and computes the RIGHT deterministic target.

Class contract (T-P3-916):

* **IN** -- a *leaf* with ``0 < checked < total`` whose stored
  ``progress_pct`` disagrees with the checked-ratio (the node-92 shape:
  7/15 checked, pct=0). Recommendation: pct -> ratio, status promote-only.
* **OUT** -- partial leaf already in sync (pct == ratio); fully-checked leaf;
  reverse leaf (pct>0, 0 checked -- 115/171 shape); no-checklist leaf; any
  parent node (its pct is a rollup, not a checkbox fact).
"""
import importlib
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

audit = importlib.import_module("audit_partial_pct_stale_20260617")

from src.backend.models.framework import FrameworkNode  # noqa: E402

# 7/15 checked == the node-92 shape (ratio 46.7). Smaller fixtures below use
# 1/2 (ratio 50.0) and 1/4 (ratio 25.0) for clarity.
_PARTIAL_1_2 = "## K\n- [x] a\n- [ ] b\n"
_PARTIAL_1_4 = "## K\n- [x] a\n- [ ] b\n- [ ] c\n- [ ] d\n"
_FULL = "## K\n- [x] a\n- [x] b\n"
_ZERO = "## K\n- [ ] a\n- [ ] b\n"
_NO_BOX = "## Prose\nNo checklist here.\n"


def _leaf(db, *, path, description=None, status="not_started",
          progress_pct=0.0, parent_id=None, depth=1):
    """Insert one node and return it (flushed, id available)."""
    n = FrameworkNode(
        parent_id=parent_id, path=path, depth=depth, title=path,
        importance=1.0, priority="P0", estimated_hours=5,
        status=status, progress_pct=progress_pct, description=description,
    )
    db.add(n)
    db.flush()
    return n


class TestClassifyPartialStale:
    def test_node92_shape_is_selected_with_deterministic_target(
            self, db_session):
        """A partial leaf whose pct lags the ratio is flagged; target is
        the checked-ratio + promote-only in_progress."""
        n = _leaf(db_session, path="p3.design.marketplace",
                  description="## K\n" + "- [x] a\n" * 7 + "- [ ] b\n" * 8,
                  status="not_started", progress_pct=0.0)
        rows = audit.classify_partial_stale(db_session)

        assert [r.node_id for r in rows] == [n.id]
        r = rows[0]
        assert (r.checked, r.total) == (7, 15)
        assert r.stored_pct == 0.0
        assert r.ratio_pct == 46.7          # round(7/15*100, 1)
        assert r.target_status == "in_progress"   # promote-only

    def test_in_sync_partial_leaf_is_excluded(self, db_session):
        """pct already equal to the ratio is NOT stale -> omitted."""
        _leaf(db_session, path="p.synced", description=_PARTIAL_1_2,
              status="in_progress", progress_pct=50.0)
        assert audit.classify_partial_stale(db_session) == []

    def test_fully_checked_and_reverse_and_nobox_excluded(self, db_session):
        """The three sibling classes the report must NOT own."""
        _leaf(db_session, path="p.full", description=_FULL,
              status="not_started", progress_pct=0.0)        # fully-checked
        _leaf(db_session, path="p.rev", description=_ZERO,
              status="in_progress", progress_pct=40.0)       # reverse (115/171)
        _leaf(db_session, path="p.nb", description=_NO_BOX,
              status="mastered", progress_pct=100.0)         # no-checklist
        assert audit.classify_partial_stale(db_session) == []

    def test_promote_only_keeps_advanced_status(self, db_session):
        """A partial leaf already past not_started keeps its status; only
        the stale pct is corrected."""
        _leaf(db_session, path="p.adv", description=_PARTIAL_1_4,
              status="review", progress_pct=0.0)
        rows = audit.classify_partial_stale(db_session)
        assert len(rows) == 1
        assert rows[0].ratio_pct == 25.0
        assert rows[0].target_status == "review"   # unchanged, not demoted

    def test_parent_node_excluded_even_if_partial_shaped(self, db_session):
        """A node that is a parent carries a rolled-up pct; never flagged."""
        parent = _leaf(db_session, path="root", description=_PARTIAL_1_2,
                       status="not_started", progress_pct=0.0)
        _leaf(db_session, path="root.child", parent_id=parent.id,
              description=_NO_BOX, status="not_started", progress_pct=0.0)
        rows = audit.classify_partial_stale(db_session)
        assert parent.id not in [r.node_id for r in rows]


class TestRenderHtml:
    def test_renders_row_and_recommendation(self, db_session):
        n = _leaf(db_session, path="p.x", description=_PARTIAL_1_4,
                  status="not_started", progress_pct=0.0)
        rows = audit.classify_partial_stale(db_session)
        out = audit.render_html(rows, total_nodes=1,
                                generated_at=datetime(2026, 6, 17, 9, 0, 0))
        assert out.lstrip().startswith("<!doctype html>")
        assert "p.x" in out
        assert "25.0" in out                      # recommended pct
        assert "in_progress" in out               # promote-only target
        assert str(n.node_id if hasattr(n, "node_id") else n.id) in out

    def test_empty_set_renders_idempotent_note(self, db_session):
        out = audit.render_html([], total_nodes=0,
                                generated_at=datetime(2026, 6, 17, 9, 0, 0))
        assert "partial pct-stale" in out.lower()
        # No data rows -> the "no stale leaves" note is present.
        assert "无需任何动作" in out
