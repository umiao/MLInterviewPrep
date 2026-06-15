#!/usr/bin/env python3
"""L0 oracle unit tests for plan_validate.py (T-P0-386 AC8).

Run:
    python -m pytest .claude/hooks/test_plan_validate.py -q

The fixtures are inline task-description strings. Known-good plans must pass
with zero objective failures; each known-bad plan must trip exactly one defect
class. Plus regression tests for the --since timezone fix (AC6) and the
short-but-valid Dependencies non-false-trip (AC1).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import plan_validate as pv  # noqa: E402


# --------------------------------------------------------------------------
# Known-good fixtures (>=3) -- each well-formed via a different Verification
# form and a different Grounding shape.
# --------------------------------------------------------------------------

GOOD_PYTEST = """\
## Summary
Add a foo widget to the bar surface so users can baz.

## Context
The bar surface currently has no foo; users hand-craft baz which is friction.

## Acceptance Criteria
- [ ] AC1: when the user clicks foo, the widget renders and returns 200.
- [ ] AC2: if foo is disabled, the surface shows the empty state instead.

## Technical Approach
Add a FooWidget component and wire it into BarSurface via the existing slot.

## Edge Cases
Empty data -> render placeholder; very long label -> truncate.

## Complexity
S -- single component.

## Verification
pytest tests/test_foo_widget.py covering render + disabled branches.

## Dependencies
None.
"""

GOOD_MANUAL_SMOKE = """\
## Summary
Document the deploy runbook for the qux service.

## Context
The qux deploy steps live only in chat history; codify them into a doc.

## Acceptance Criteria
- [ ] AC1: the runbook lists every step from build to rollback.
- [ ] AC2 (user journey): an operator follows the doc and reaches a healthy deploy.

## Technical Approach
Write docs/runbooks/qux.md from the existing tribal-knowledge steps.

## Edge Cases
Partial rollout -> note the half-state recovery; secret rotation mid-deploy.

## Complexity
S -- a doc.

## Verification
Manual smoke: an operator runs the runbook end to end on staging and observes a healthy deploy.

## Dependencies
None.
"""

GOOD_NO_TEST = """\
## Summary
Rename the legacy `widget_v1` symbol to `widget` across the module.

## Context
The v1 suffix is vestigial; the rename reduces confusion.

## Acceptance Criteria
- [ ] AC1: when grep finds no `widget_v1`, the rename is complete.
- [ ] AC2: imports resolve and the module loads.

## Technical Approach
Mechanical rename + import fixups; no behavior change.

## Edge Cases
Shadowed local names; string references in docs.

## Complexity
S -- mechanical.

## Verification
no-test: pure mechanical rename verified by grep showing zero `widget_v1` hits + import smoke.

## Dependencies
None.
"""

GOOD_PLANS = {
    "GOOD_PYTEST": GOOD_PYTEST,
    "GOOD_MANUAL_SMOKE": GOOD_MANUAL_SMOKE,
    "GOOD_NO_TEST": GOOD_NO_TEST,
}


# --------------------------------------------------------------------------
# Known-bad fixtures (>=4) -- each trips exactly one defect class.
# Built by removing one thing from an otherwise well-formed plan.
# --------------------------------------------------------------------------

# Missing the "Edge Cases" section.
BAD_MISSING_SECTION = """\
## Summary
Add a foo widget so users can baz.

## Context
No foo today; users hand-craft baz.

## Acceptance Criteria
- [ ] AC1: when the user clicks foo, it returns 200.

## Technical Approach
Add FooWidget and wire it in.

## Complexity
S.

## Verification
pytest tests/test_foo.py.

## Dependencies
None.
"""

# Acceptance Criteria section present but with NO `- [ ]` items.
BAD_NO_AC = """\
## Summary
Add a foo widget so users can baz.

## Context
No foo today; users hand-craft baz.

## Acceptance Criteria
The widget should render and behave well when clicked, and degrade gracefully.

## Technical Approach
Add FooWidget and wire it in.

## Edge Cases
Empty data -> placeholder.

## Complexity
S.

## Verification
pytest tests/test_foo.py.

## Dependencies
None.
"""

# No Verification field anywhere (no pytest / no `## Verification` / no no-test:).
BAD_NO_VERIFICATION = """\
## Summary
Add a foo widget so users can baz.

## Context
No foo today; users hand-craft baz.

## Acceptance Criteria
- [ ] AC1: when the user clicks foo, it renders.

## Technical Approach
Add a FooWidget component and wire it into the surface.

## Edge Cases
Empty data -> placeholder.

## Complexity
S.

## Dependencies
None.
"""

# Grounding Assets names a repo path that does not exist.
BAD_BAD_GROUNDING = """\
## Summary
Add a foo widget so users can baz.

## Context
No foo today; users hand-craft baz.

## Grounding Assets
src/does/not/exist_xyzzy.py (CONTRACT/binds)

## Acceptance Criteria
- [ ] AC1: when the user clicks foo, it renders.

## Technical Approach
Add a FooWidget component.

## Edge Cases
Empty data -> placeholder.

## Complexity
S.

## Verification
pytest tests/test_foo.py.

## Dependencies
None.
"""


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(GOOD_PLANS))
def test_known_good_plans_pass(name):
    """All known-good plans produce zero objective failures."""
    failures, _warnings = pv.validate_description(name, GOOD_PLANS[name])
    assert failures == [], f"{name} unexpectedly failed: {failures}"


def test_bad_missing_section_trips_section_only():
    failures, _ = pv.validate_description("BAD_MISSING_SECTION", BAD_MISSING_SECTION)
    assert len(failures) == 1, failures
    assert "missing/empty section" in failures[0]
    assert "edge cases" in failures[0]


def test_bad_no_ac_trips_ac_only():
    failures, _ = pv.validate_description("BAD_NO_AC", BAD_NO_AC)
    assert len(failures) == 1, failures
    assert "no acceptance-criteria item" in failures[0]


def test_bad_no_verification_trips_verification_only():
    failures, _ = pv.validate_description("BAD_NO_VERIFICATION", BAD_NO_VERIFICATION)
    assert len(failures) == 1, failures
    assert "no Verification field" in failures[0]


def test_bad_grounding_trips_grounding_only():
    failures, _ = pv.validate_description("BAD_BAD_GROUNDING", BAD_BAD_GROUNDING)
    assert len(failures) == 1, failures
    assert "Grounding Assets path(s) do not exist" in failures[0]
    assert "exist_xyzzy.py" in failures[0]


# --- AC1: short-but-valid Dependencies must NOT false-trip --------------------

def test_short_dependencies_not_flagged():
    """`## Dependencies\\nNone.` is valid; the section check must not flag it."""
    missing = pv._check_spec_sections(GOOD_PYTEST)
    assert "dependencies" not in missing

    short_dep = GOOD_PYTEST.replace("## Dependencies\nNone.\n", "## Dependencies\nT-P0-1.\n")
    missing2 = pv._check_spec_sections(short_dep)
    assert "dependencies" not in missing2


# --- AC6: --since timezone round-trip fix -------------------------------------

def test_since_naive_is_treated_as_utc_unchanged():
    """A naive --since must NOT be shifted by the local UTC offset."""
    iso_since, _ts = pv._normalize_since("2026-06-13T00:00:00")
    assert iso_since == "2026-06-13T00:00:00"


def test_since_aware_normalized_to_naive_utc():
    """A tz-aware --since is converted to the matching naive-UTC wall clock."""
    iso_since, _ts = pv._normalize_since("2026-06-13T08:00:00+08:00")
    assert iso_since == "2026-06-13T00:00:00"


def test_naive_utc_created_at_compares_lexically():
    """Regression: a window boundary lexically precedes a later created_at."""
    iso_since, _ts = pv._normalize_since("2026-06-13T00:00:00")
    created_at = "2026-06-14T03:54:54"  # naive-UTC, as stored by task_store
    assert created_at >= iso_since


# --- Grounding path classification --------------------------------------------

def test_conceptual_and_memory_refs_are_exempt():
    assert pv._looks_like_repo_path("T3 findings JSON contract") is False
    assert pv._looks_like_repo_path("memory ops_autorun_and_taskdb") is False
    assert pv._looks_like_repo_path("https://example.com/x") is False
    assert pv._looks_like_repo_path(".claude/hooks/task_db.py") is True
    assert pv._looks_like_repo_path("TASK_PLAN_plan_review_pipeline.md") is True


# --- T-P0-387: topology checks (acyclic / cyclic / dangling / orphan) ---------

def test_topology_acyclic_passes():
    ids = {"T-A", "T-B", "T-C"}
    edges = [("T-A", "T-B"), ("T-B", "T-C")]
    failures, warnings = pv._check_topology(ids, edges, window_ids=set())
    assert failures == []


def test_topology_cycle_fails_with_path():
    ids = {"T-A", "T-B"}
    edges = [("T-A", "T-B"), ("T-B", "T-A")]
    failures, _ = pv._check_topology(ids, edges, window_ids=set())
    assert len(failures) == 1
    assert "dependency cycle" in failures[0]
    path = failures[0].split(":", 1)[1].strip()
    nodes = [n.strip() for n in path.split("->")]
    assert nodes[0] == nodes[-1]          # closed cycle
    assert set(nodes) == {"T-A", "T-B"}   # both members present


def test_topology_dangling_fails():
    ids = {"T-A"}
    edges = [("T-A", "T-Z")]  # T-Z does not exist
    failures, _ = pv._check_topology(ids, edges, window_ids=set())
    assert len(failures) == 1
    assert "dangling dependency edge" in failures[0]
    assert "T-A->T-Z" in failures[0]


def test_topology_orphan_warns_only_scoped_to_window():
    ids = {"T-A", "T-B", "T-C"}
    edges = [("T-A", "T-B")]           # T-C has no edges
    # T-C is in the window -> orphan WARN; out-of-window dep-less tasks ignored.
    failures, warnings = pv._check_topology(ids, edges, window_ids={"T-C"})
    assert failures == []
    assert len(warnings) == 1
    assert "T-C" in warnings[0]
    assert "orphan" in warnings[0]
    assert "standalone" in warnings[0]  # offers the confirm-standalone resolution


def test_topology_orphan_out_of_window_not_flagged():
    ids = {"T-A", "T-B", "T-C"}
    edges = [("T-A", "T-B")]
    # T-C dep-less but NOT in window -> no orphan warning.
    failures, warnings = pv._check_topology(ids, edges, window_ids={"T-A"})
    assert failures == []
    assert warnings == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
