#!/usr/bin/env python3
"""Oracle tests for plan-review L3 routing + provenance + T0 signal (T-P1-390).

Covers:
- route_and_record.plan_routing  (AC1 route human_review, AC4 if/else release)
- route_and_record.concern_event (AC2 provenance fields)
- route_and_record.summarize_events (T0 acceptance-rate + kill criterion; AC6)
- TaskStore.mark_for_review (AC1 set hr=1 WITHOUT park)
- the governance hardline (AC5): LLM cannot autonomously complete an hr=1 task.

Run:
    pytest .claude/skills/plan-review/test_route_and_record.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))

import route_and_record as rr  # noqa: E402
import task_store as ts_mod  # noqa: E402

# task_store.py / task_db.py are deliberately NOT propagated by the plan-review
# pattern (gated on the task_db unification, T-P2-321). In a sub-project whose
# task_store predates `mark_for_review`, the L3 routing (set_human_review) is
# inert and these store-dependent tests do not apply -- skip them rather than
# fail, so the propagated suite is green everywhere. The pure logic + events +
# T0-signal tests above always run.
_HAS_MARK_FOR_REVIEW = hasattr(ts_mod.TaskStore, "mark_for_review")
requires_mark_for_review = pytest.mark.skipif(
    not _HAS_MARK_FOR_REVIEW,
    reason="local task_store lacks mark_for_review (not yet propagated, T-P2-321)",
)


def _f(**over) -> dict:
    base = {
        "task": "T-A", "ac": "AC1", "dimension": "objective", "verdict": "concern",
        "severity": "high", "confidence": "high", "evidence": "AC1 ...",
        "suggested_fix": "fix", "route": "human", "adjudication": "kept",
    }
    base.update(over)
    return base


def _doc(findings, reviewed=("T-A", "T-B")) -> dict:
    return {"run_id": "r1", "round": 2, "tasks_reviewed": list(reviewed),
            "findings": findings}


# --------------------------------------------------------------------------- #
# plan_routing (AC1 / AC4)
# --------------------------------------------------------------------------- #
def test_route_human_task_gated():
    plan = rr.plan_routing(_doc([_f(task="T-A")]))
    assert plan["tasks_to_review"] == ["T-A"]


def test_clean_task_released():
    # T-B is reviewed but has no route=human finding -> released (AC4 else).
    plan = rr.plan_routing(_doc([_f(task="T-A")]))
    assert "T-B" in plan["tasks_released"]
    assert "T-A" not in plan["tasks_released"]


def test_pass_only_all_released():
    plan = rr.plan_routing(_doc([
        _f(task="T-A", verdict="pass", route="none"),
        _f(task="T-B", verdict="pass", route="none"),
    ]))
    assert plan["tasks_to_review"] == []
    assert sorted(plan["tasks_released"]) == ["T-A", "T-B"]


def test_discarded_concern_not_routed():
    plan = rr.plan_routing(_doc([_f(task="T-A", adjudication="discarded")]))
    assert plan["tasks_to_review"] == []
    assert "T-A" in plan["tasks_released"]


def test_harden_l0_not_routed_to_human():
    # route=harden-L0 feeds the L0 oracle, not human_review.
    plan = rr.plan_routing(_doc([_f(task="T-A", route="harden-L0")]))
    assert plan["tasks_to_review"] == []


def test_global_concern_in_concerns_but_not_gated():
    # a global (task=null) route=human concern is recorded but has no task to gate.
    plan = rr.plan_routing(_doc([_f(task=None, ac=None)]))
    assert plan["tasks_to_review"] == []
    assert len(plan["concerns"]) == 1


def test_added_global_finding_routed_as_concern():
    plan = rr.plan_routing(_doc([_f(task="T-A", adjudication="added")]))
    assert plan["tasks_to_review"] == ["T-A"]


# --------------------------------------------------------------------------- #
# concern_event (AC2 provenance)
# --------------------------------------------------------------------------- #
def test_concern_event_has_required_and_provenance():
    evt = rr.concern_event("r1", _f(), ts="2026-06-14T00:00:00",
                           disposition="pending", prompt_ver="p1",
                           model_ver="m1", artifact_hash="abc")
    for k in ("ts", "project_id", "task_id", "from_state", "to_state", "actor"):
        assert k in evt
    assert evt["kind"] == rr.CONCERN_KIND
    assert evt["artifact_hash"] == "abc"
    assert evt["prompt_ver"] == "p1" and evt["model_ver"] == "m1"
    assert evt["disposition"] == "pending"
    assert evt["ac_ref"] == "AC1"


def test_concern_event_global_uses_plan_task_id():
    evt = rr.concern_event("r1", _f(task=None, ac=None), ts="t",
                           disposition="pending", prompt_ver="p",
                           model_ver="m", artifact_hash=None)
    assert evt["task_id"] == "PLAN"


def test_content_hash_deterministic():
    assert rr.content_hash("abc") == rr.content_hash("abc")
    assert rr.content_hash("abc") != rr.content_hash("abd")


# --------------------------------------------------------------------------- #
# summarize_events (T0 signal + kill criterion, AC6)
# --------------------------------------------------------------------------- #
def _evt(run, task, ac, disp):
    return {"kind": rr.CONCERN_KIND, "run_id": run, "task_id": task,
            "ac_ref": ac, "disposition": disp}


def test_summary_insufficient_data():
    # fewer than S decided -> insufficient, never false-green.
    out = rr.summarize_events([_evt("r1", "T-A", "AC1", "accepted")])
    assert out["status"] == "insufficient_data"
    assert out["acceptance_rate"] is None


def test_summary_working_when_rate_high():
    evts = [_evt("r1", f"T-{i}", "AC1", "accepted") for i in range(10)]
    out = rr.summarize_events(evts)
    assert out["status"] == "working"
    assert out["acceptance_rate"] == 1.0


def test_summary_quarantine_when_rate_low():
    # 2 accepted, 8 dismissed -> 0.2 < tau(0.30) -> trip.
    evts = [_evt("r1", f"T-{i}", "AC1", "accepted") for i in range(2)]
    evts += [_evt("r1", f"T-{i}", "AC1", "dismissed") for i in range(2, 10)]
    out = rr.summarize_events(evts)
    assert out["decided"] == 10
    assert out["acceptance_rate"] == 0.2
    assert out["status"] == "quarantine_trip"


def test_summary_latest_disposition_wins():
    # pending then accepted for the same concern -> counts as accepted, once.
    evts = [_evt("r1", "T-A", "AC1", "pending"),
            _evt("r1", "T-A", "AC1", "accepted")]
    evts += [_evt("r1", f"T-{i}", "AC1", "accepted") for i in range(9)]
    out = rr.summarize_events(evts)
    assert out["decided"] == 10  # T-A counted once, not twice
    assert out["accepted"] == 10


def test_summary_pending_not_counted():
    out = rr.summarize_events([_evt("r1", f"T-{i}", "AC1", "pending") for i in range(20)])
    assert out["decided"] == 0
    assert out["status"] == "insufficient_data"


def test_summary_window_last_w_runs():
    # run r0 all dismissed (should fall out of W=3 window if 3 later runs exist).
    evts = [_evt("r0", f"X-{i}", "AC1", "dismissed") for i in range(10)]
    for r in ("r1", "r2", "r3"):
        evts += [_evt(r, f"{r}-{i}", "AC1", "accepted") for i in range(4)]
    out = rr.summarize_events(evts)
    assert out["runs_in_window"] == 3
    assert out["acceptance_rate"] == 1.0  # r0's dismissals excluded by window


# --------------------------------------------------------------------------- #
# TaskStore.mark_for_review (AC1) + governance hardline (AC5)
# --------------------------------------------------------------------------- #
def _store(tmp_path):
    store = ts_mod.TaskStore(str(tmp_path / "t.db"))
    # mimic the live schema: add the state + human_review columns the migrations
    # add. Schema-tolerant: a newer base schema (some sub-projects) may already
    # define these -- only ALTER the genuinely-missing ones (avoids the
    # "duplicate column" OperationalError).
    conn = store._get_conn()
    have = {c[1] for c in conn.execute("PRAGMA table_info(tasks)")}
    if "state" not in have:
        conn.execute("ALTER TABLE tasks ADD COLUMN state TEXT")
    if "human_review" not in have:
        conn.execute("ALTER TABLE tasks ADD COLUMN human_review INTEGER DEFAULT 0")
    return store


@requires_mark_for_review
def test_mark_for_review_sets_hr_without_park(tmp_path):
    store = _store(tmp_path)
    t = store.add("demo", task_id="T-X")
    res = store.mark_for_review("T-X")
    assert res["human_review"] == 1 and res["no_op"] is False
    # status/state untouched (NOT park): still active, not blocked.
    assert store.get("T-X").status == t.status == "active"


@requires_mark_for_review
def test_mark_for_review_idempotent(tmp_path):
    store = _store(tmp_path)
    store.add("demo", task_id="T-X")
    store.mark_for_review("T-X")
    res2 = store.mark_for_review("T-X")
    assert res2["no_op"] is True and res2["human_review"] == 1


@requires_mark_for_review
def test_mark_for_review_missing_task(tmp_path):
    store = _store(tmp_path)
    try:
        store.mark_for_review("T-NOPE")
        assert False, "expected ValueError"
    except ValueError:
        pass


@requires_mark_for_review
def test_hardline_llm_cannot_complete_hr1(tmp_path):
    # AC5: after mark-review, completing without a reviewer is hard-rejected.
    store = _store(tmp_path)
    store.add("demo", task_id="T-X")
    store.mark_for_review("T-X")
    try:
        store.complete_task("T-X", reviewer=None)
        assert False, "expected ValueError (hr=1 gate)"
    except ValueError as e:
        assert "human_review=1" in str(e)
    # update(status=completed) is also rejected for hr=1.
    try:
        store.update("T-X", status="completed")
        assert False, "expected ValueError (hr=1 gate on update)"
    except ValueError as e:
        assert "human_review=1" in str(e)


@requires_mark_for_review
def test_hardline_reviewer_can_complete(tmp_path):
    # the user's explicit complete --reviewer stays allowed (AC5).
    store = _store(tmp_path)
    store.add("demo", task_id="T-X")
    store.mark_for_review("T-X")
    res = store.complete_task("T-X", reviewer="xushenghui", project_root=tmp_path)
    assert res["state"] == "done" and res["status"] == "completed"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
