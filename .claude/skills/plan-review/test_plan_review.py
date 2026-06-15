#!/usr/bin/env python3
"""Oracle tests for the plan-review deterministic layer (T-P0-388 / T-P1-389).

Covers the two machine-owned, judgement-free modules:
- validate_findings.py: the AC-level JSON contract gate (T3 AC1) + the coupling
  invariants that encode the bearing wall (T3 AC5 subjective / AC6 harden-L0).
- render_brief.py: the deterministic guidance-brief renderer (T4 AC4/AC5/AC7 +
  the 'no action needed' edge case).

Run:
    pytest .claude/skills/plan-review/test_plan_review.py -q
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_brief  # noqa: E402
import validate_findings as vf  # noqa: E402


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _finding(**over) -> dict:
    """A valid objective-pass finding; override fields per test."""
    base = {
        "task": "T-P0-388",
        "ac": "AC1",
        "dimension": "objective",
        "verdict": "pass",
        "severity": "low",
        "confidence": "high",
        "evidence": "AC1 lists the full item schema",
        "suggested_fix": "",
        "route": "none",
    }
    base.update(over)
    return base


def _doc(findings, **over) -> dict:
    base = {"run_id": "pr-test", "round": 1, "findings": findings}
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# validate_findings -- happy paths
# --------------------------------------------------------------------------- #
def test_valid_pass_finding():
    assert vf.validate_findings(_doc([_finding()])) == []


def test_valid_objective_concern_routes_human():
    f = _finding(verdict="concern", severity="high", route="human",
                 suggested_fix="add a pytest reference")
    assert vf.validate_findings(_doc([f])) == []


def test_valid_subjective_defer():
    f = _finding(dimension="subjective", verdict="defer", route="human",
                 ac=None, suggested_fix="decide: build now vs defer to T6")
    assert vf.validate_findings(_doc([f])) == []


def test_valid_harden_l0():
    # harden-L0 is a ROUTE for an objective defect L0 missed (AC6), not a dimension.
    f = _finding(dimension="objective", verdict="concern", route="harden-L0",
                 severity="med", suggested_fix="L0 should reject missing Verification here")
    assert vf.validate_findings(_doc([f])) == []


def test_empty_findings_is_valid_shape():
    assert vf.validate_findings(_doc([])) == []


# --------------------------------------------------------------------------- #
# validate_findings -- the verdict enum (no 'fail')
# --------------------------------------------------------------------------- #
def test_fail_verdict_rejected():
    errs = vf.validate_findings(_doc([_finding(verdict="fail")]))
    assert any("verdict" in e and "fail" in e for e in errs)


# --------------------------------------------------------------------------- #
# validate_findings -- coupling invariants (AC5 subjective / AC6 harden-L0)
# --------------------------------------------------------------------------- #
def test_subjective_must_be_defer():
    # subjective + a terminal verdict = machine judging a subjective matter.
    f = _finding(dimension="subjective", verdict="concern", route="human",
                 severity="high", suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("subjective" in e and "defer" in e for e in errs)


def test_subjective_must_route_human():
    f = _finding(dimension="subjective", verdict="defer", route="none",
                 suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("route='human'" in e for e in errs)


def test_defer_reserved_for_subjective():
    f = _finding(dimension="objective", verdict="defer", route="human",
                 suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("reserved for dimension=subjective" in e for e in errs)


def test_harden_route_rejects_subjective_dimension():
    # subjective forces route=human anyway, but assert the harden-L0 coupling msg.
    f = _finding(dimension="subjective", verdict="concern", route="harden-L0",
                 severity="med", suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("route=harden-L0 requires dimension=objective" in e for e in errs)


def test_harden_route_requires_concern_verdict():
    f = _finding(dimension="objective", verdict="pass", route="harden-L0",
                 severity="med", suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("route=harden-L0 requires verdict=concern" in e for e in errs)


def test_objective_concern_may_route_harden_l0():
    f = _finding(dimension="objective", verdict="concern", route="harden-L0",
                 severity="med", suggested_fix="L0 should have caught this")
    assert vf.validate_findings(_doc([f])) == []


def test_pass_must_route_none():
    errs = vf.validate_findings(_doc([_finding(verdict="pass", route="human")]))
    assert any("verdict='pass' must have route='none'" in e for e in errs)


def test_concern_cannot_route_none():
    f = _finding(verdict="concern", severity="high", route="none",
                 suggested_fix="x")
    errs = vf.validate_findings(_doc([f]))
    assert any("must route to 'human' or 'harden-L0'" in e for e in errs)


def test_concern_requires_suggested_fix():
    f = _finding(verdict="concern", severity="high", route="human",
                 suggested_fix="   ")
    errs = vf.validate_findings(_doc([f]))
    assert any("requires a non-empty suggested_fix" in e for e in errs)


# --------------------------------------------------------------------------- #
# validate_findings -- field-level + top-level structure
# --------------------------------------------------------------------------- #
def test_bad_severity():
    errs = vf.validate_findings(_doc([_finding(severity="critical")]))
    assert any(".severity" in e for e in errs)


def test_bad_confidence():
    errs = vf.validate_findings(_doc([_finding(confidence="certain")]))
    assert any(".confidence" in e for e in errs)


def test_missing_key():
    f = _finding()
    del f["evidence"]
    errs = vf.validate_findings(_doc([f]))
    assert any("missing key" in e and "evidence" in e for e in errs)


def test_empty_evidence_rejected():
    errs = vf.validate_findings(_doc([_finding(evidence="  ")]))
    assert any(".evidence" in e for e in errs)


def test_ac_null_ok_but_empty_string_rejected():
    assert vf.validate_findings(_doc([_finding(ac=None)])) == []
    errs = vf.validate_findings(_doc([_finding(ac="")]))
    assert any(".ac" in e for e in errs)


def test_task_null_ok_for_global_finding():
    # a global/cross-task finding (T4's global pass) has task=null
    f = _finding(task=None, dimension="subjective", verdict="defer",
                 route="human", ac=None, suggested_fix="option A / option B")
    assert vf.validate_findings(_doc([f], round=2)) == []
    errs = vf.validate_findings(_doc([_finding(task="")]))
    assert any(".task" in e for e in errs)


def test_bad_run_id():
    errs = vf.validate_findings(_doc([_finding()], run_id=""))
    assert any("run_id" in e for e in errs)


def test_bad_round():
    errs = vf.validate_findings(_doc([_finding()], round=3))
    assert any("round" in e for e in errs)


def test_top_level_not_object():
    assert vf.validate_findings([1, 2, 3]) == ["top-level: not an object"]


# --------------------------------------------------------------------------- #
# render_brief -- structure + edge cases
# --------------------------------------------------------------------------- #
def test_brief_clean_plan_says_no_action():
    # All pass + one discarded hallucination -> explicit no-action, never empty.
    doc = _doc([
        _finding(),
        _finding(verdict="concern", severity="high", route="human",
                 suggested_fix="x", adjudication="discarded",
                 audit_note="evidence does not support it"),
    ], round=2)
    brief = render_brief.build_brief(doc)
    assert "无需你处理" in brief
    assert "no action needed" in brief
    assert brief.strip() != ""
    # discarded count surfaced, not silently dropped
    assert "弃掉 1" in brief or "弃掉 1 条" in brief


def test_brief_objective_concern_drilldown():
    f = _finding(ac="AC4", verdict="concern", severity="high", route="human",
                 suggested_fix="add injection-hardening delimiter")
    brief = render_brief.build_brief(_doc([f], round=2))
    assert "需修正项" in brief
    assert "`T-P0-388`" in brief
    assert "AC4" in brief
    assert "add injection-hardening delimiter" in brief


def test_brief_subjective_in_decision_section_no_verdict():
    f = _finding(dimension="subjective", verdict="defer", route="human",
                 ac="AC5", severity="med",
                 evidence="touches 'should this be built'",
                 suggested_fix="option A: ship now / option B: gate on T6")
    brief = render_brief.build_brief(_doc([f], round=2))
    assert "需你裁决" in brief
    assert "option A" in brief
    # subjective section must not present a terminal pass/concern token as a verdict
    assert "verdict=concern" not in brief


def test_brief_discarded_excluded_from_actionable():
    kept = _finding(verdict="concern", severity="high", route="human",
                    ac="AC1", suggested_fix="real fix")
    halluc = _finding(verdict="concern", severity="high", route="human",
                      ac="AC2", suggested_fix="bogus",
                      adjudication="discarded", audit_note="hallucination")
    brief = render_brief.build_brief(_doc([kept, halluc], round=2))
    assert "real fix" in brief
    assert "bogus" not in brief  # discarded never shown as actionable


def test_brief_harden_l0_not_in_human_actionable():
    h = _finding(dimension="objective", verdict="concern", route="harden-L0",
                 severity="med", ac="AC2", suggested_fix="L0 should catch this")
    # also one human concern so we are NOT in the no-action branch
    c = _finding(verdict="concern", severity="high", route="human",
                 ac="AC1", suggested_fix="fix me")
    brief = render_brief.build_brief(_doc([h, c], round=2))
    assert "L0 加固回流" in brief
    assert "不需你处理" in brief
    # harden item's fix text is NOT in a decision/correction list (only counted)
    assert "L0 should catch this" not in brief


def test_brief_added_global_finding_marked():
    f = _finding(verdict="concern", severity="high", route="human", ac=None,
                 evidence="goal X has no task covering it",
                 suggested_fix="add a task for X", adjudication="added",
                 audit_note="global coverage gap")
    brief = render_brief.build_brief(_doc([f], round=2))
    assert "全局补充" in brief
    assert "task 级" in brief  # ac=None renders as task-level


def test_brief_names_primary_metric():
    brief = render_brief.build_brief(_doc([_finding()], round=2))
    assert "信噪比" in brief and "主指标" in brief


def test_brief_only_pass_task_not_shown_as_actionable():
    # a task whose findings are all pass should not appear in 需修正 / 需裁决
    brief = render_brief.build_brief(_doc([_finding(task="T-PASS-1")], round=2))
    assert "T-PASS-1" not in brief
    assert "无需你处理" in brief


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
