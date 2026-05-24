"""One-shot helper: add the 5 P0 + 1 P2 KG-FIX/MIGRATE tasks via task_db.py batch.

Throwaway scaffold (prefixed `_` per project convention). After running once,
TASKS.md is regenerated and this script can be deleted.

Run:
    /c/Anaconda/python.exe scripts/_kg_fix_taskplan_20260425.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASK_DB = REPO_ROOT / ".claude" / "hooks" / "task_db.py"


def _add(
    title: str,
    priority: str,
    complexity: str,
    description: str,
) -> dict:
    return {
        "cmd": "add",
        "title": title,
        "priority": priority,
        "complexity": complexity,
        "description": description,
    }


# ---------------------------------------------------------------------------
# Task descriptions (finalised after 2 review rounds on Discord 2026-04-25)
# ---------------------------------------------------------------------------

DESC_FIX_01 = """\
[KG-FIX-01] Backend: rewrite `_pillar_of()` in src/backend/routers/kg.py to walk
parent_id back to the depth=0 ancestor and return that ancestor's path string,
instead of `path.split(".",1)[0]`.

WHY: framework_nodes.path has two incompatible separator conventions. The 8
original pillars use dot (`pillar2.feature_engineering`); the 36-row
ml-fundamentals subtree uses slash (`ml-fundamentals/classical_ml/...`). The
current split-by-dot logic returns the entire slash-path as the pillar key,
which (a) falls into "Other" via PILLAR_STYLES fallback and (b) gives every
ml-fundamentals node a unique pillar value, exploding the swimlane layout
into 36 individual L1 lanes. Walking parent_id is taxonomy-agnostic and
correct under arbitrary path conventions.

ACCEPTANCE CRITERIA
AC1: All 36 ml-fundamentals/* rows return pillar="ml-fundamentals".
AC2: REGRESSION — every pillar1..pillar8 descendant still returns its original
     "pillarN" value. Parameterised pytest in tests/test_kg_router.py covering
     >=1 sample per pillar (>=8 cases total).
AC3: Invariant test in tests/test_framework_path_convention.py:
       WHITELIST = {"ml-fundamentals"}  # TTL: remove after T-P2-XX (KG-DESIGN-DUAL-VIEW)
     Test fails if any path matches '%/%' AND its depth=0 ancestor's path is
     not in WHITELIST. Additionally, test queries task_db (`task_db.py get
     T-P2-XX --json`) and FAILS if KG-DESIGN-DUAL-VIEW status==completed but
     WHITELIST is non-empty (forces whitelist cleanup once migration decision
     lands).
AC4: docstring on _pillar_of uses CONDITIONAL language:
     'NOTE: Required AS LONG AS the taxonomy permits multiple depth=0 roots
     with different path-separator conventions. The transitional vs permanent
     question is open and resolved by T-P2-XX (KG-DESIGN-DUAL-VIEW). DO NOT
     revert to path.split(".",1)[0] until that question is answered.'

COMPLEXITY: S
"""

DESC_FIX_02 = """\
[KG-FIX-02] Frontend: extend PILLAR_STYLES in
src/frontend/src/components/kg/kgStyles.ts with an `"ml-fundamentals"` entry
so the 36-row subtree no longer falls through to FALLBACK_STYLE / "Other".

ACCEPTANCE CRITERIA
AC1: New entry: `name: "ML 八股文 · Fundamentals"`, `border: "#0891b2"` (cyan-600),
     `bg: "#ecfeff"` (cyan-50). Adjust to a free hue if collision found.
AC2: Vitest snapshot/render test asserts FALLBACK_STYLE is NOT triggered for
     any of the 9 known pillar keys (pillar1..pillar8 + ml-fundamentals).
AC3: Existing styleForPillar() / colorForPillar() unit tests still pass.

COMPLEXITY: S
"""

DESC_FIX_03 = """\
[KG-FIX-03] Frontend: replace pillarSortKey() regex in
src/frontend/src/components/kg/useKgLayout.ts with an EXPLICIT
`PILLAR_ORDER: Record<string, number>` map. No fallback ordering by regex
match.

WHY: Current logic returns 9999 for non-matching pillars, which lets new
top-level taxonomies sort to "wherever" implicitly. Explicit map makes
swimlane order a first-class design decision.

ACCEPTANCE CRITERIA
AC1: PILLAR_ORDER uses step=10 numbering with documented insertion convention:
       pillar1: 10, pillar2: 20, "ml-fundamentals": 25, pillar3: 30,
       pillar4: 40, pillar5: 50, pillar6: 60, pillar7: 70, pillar8: 80
     Comment: "Insert new entries at adjacent decimals (e.g. 25, 35); reserve
     larger gaps if topology will expand."
AC2: ml-fundamentals swimlane is positioned visually between pillar2 and
     pillar3 on KG canvas (verified via KG-FIX-05 smoke).
AC3: Unit test in useKgLayout.test.ts asserting full sorted order matches
     [pillar1, pillar2, ml-fundamentals, pillar3, pillar4, pillar5, pillar6,
     pillar7, pillar8].

DEPENDS ON: KG-FIX-02 (the new pillar key must exist in PILLAR_STYLES first
so any KG render asserting style coverage doesn't trip).

COMPLEXITY: S
"""

DESC_FIX_04 = """\
[KG-FIX-04] Schema invariant + path convention doc + LESSONS postmortem +
seed-batch process change.

WHY: The slash-path bug entered through a seed-script series (the
ml-fundamentals batch) that was never run against KG page rendering before
merge. Convert this from a "should remember" lesson into machinery and
process that prevents the next occurrence.

ACCEPTANCE CRITERIA
AC1: tests/test_framework_path_convention.py (already created in KG-FIX-01
     AC3) lives in CI; verify it runs in `pytest -k "convention"`.
AC2: New file docs/protocol/kg_markdown_conventions.md (or extend existing)
     adds explicit rule: "framework_nodes.path uses '.' separator. Known
     historical exception: ml-fundamentals/* subtree, governed by T-P2-XX
     (KG-DESIGN-DUAL-VIEW). Any new top-level taxonomy MUST add a
     PILLAR_ORDER entry, a PILLAR_STYLES entry, and a whitelist entry in
     the convention test."
AC3: New file docs/workflow/seed_smoke_test_protocol.md — 5-step checklist
     for any framework_node seed batch (>=3 rows):
       1. Run seed against staging DB
       2. Full-table _pillar_of scan; assert all returned pillars in known set
       3. `vite dev` + open KG page; capture cold-start screenshot
       4. expand-all; capture screenshot; verify lane count matches expectation
       5. Diff before/after screenshots; no unexpected regressions
AC4: CLAUDE.md gets a new bullet under "Behavior Rules":
     '**New framework_node seed batches (>=3 rows) require running
     docs/workflow/seed_smoke_test_protocol.md before merge. Skipping the
     protocol is not optional.'
AC5: LESSONS.md postmortem entry with this content:
     - Date: 2026-04-25
     - Title: "Slash-path KG taxonomy mis-classification — silent merge"
     - Root cause: 35 ml-fundamentals seed inserts used '/' separator while
       _pillar_of() only split on '.'. Series merged because no AC required
       running KG page after seed.
     - Fix: KG-FIX-01..05 (parent_id-based pillar derivation, explicit pillar
       order map, schema invariant test, convention doc).
     - Prevention: seed_smoke_test_protocol.md + CLAUDE.md rule + invariant
       test gate.
     - Tags: #kg #taxonomy #seed-process #postmortem

COMPLEXITY: S
"""

DESC_FIX_05 = """\
[KG-FIX-05] Manual smoke test + before/after screenshots + HARD MERGE GATE.

WHY: AC-as-software-test only. Auto-merge by autonomous agent is forbidden
for this change because rendering bugs slip past unit tests
(see KG bug history — vitest passed while every node was bucketed as Other).

ACCEPTANCE CRITERIA
AC1: With FIX-01..04 deployed, cold-start KG page shows:
     - ml-fundamentals as a single cyan swimlane (not 36)
     - Tree expansion: 1 root -> 7 categories at depth=1 -> 28 leaves at
       depth=2, all rendered hierarchically under the cyan lane
     - "Other" / grey FALLBACK_STYLE appears nowhere
AC2: After clicking "Expand All", total swimlane count = 9
     (pillar1..pillar8 + ml-fundamentals). Not 36+.
AC3: Before/after screenshots saved to logs/kg_fix_smoke_20260425/
     (cold_before.png, cold_after.png, expandall_before.png,
     expandall_after.png).
AC4: [HARD GATE — autonomous agent MUST OBEY]
     - Autonomous session runs FIX-01..04 on feature branch `kg-fix-20260425`
       (NOT main). Each task gets its own commit.
     - After FIX-04 commit, session pushes the feature branch to origin
       (`git push -u origin kg-fix-20260425`) WITHOUT merging to main.
     - Session captures FIX-05 screenshots, posts them to Discord chat
       1484761064292749422 with text:
         "KG-FIX-01..05 done on branch kg-fix-20260425. Review screenshots.
          Reply: ✅ to merge to main, ❌ to abort, or describe needed changes."
     - Session EXITS without touching main. The fast-forward merge is
       performed by the user OR by the next session after user reaction is
       observed in Discord history.
     - Auto-merge to main is FORBIDDEN.

DEPENDS ON: KG-FIX-01, KG-FIX-02, KG-FIX-03, KG-FIX-04 (all four must be
done before smoke test can run).

COMPLEXITY: S
"""

DESC_DUAL_VIEW = """\
[KG-DESIGN-DUAL-VIEW] Open question: is ml-fundamentals/* + pillar2 coexistence
a bug to eliminate (consolidate to single root) OR a feature to legitimize
(permanent dual view)? Output: a design doc, not code.

WHY: Both KG bug-review rounds defaulted to "two structures = bug, migrate to
single root". Reviewer round 2 challenged that premise: ml-fundamentals
(interview-grind / leaf-dense / drill-oriented) and pillar2 (knowledge-system
/ structured / theory-deep) may serve different cognitive modes. Their
overlap could be intentional view separation, not redundancy. Resolving this
question changes whether KG-FIX-01's parent_id walk is transitional or
permanent infrastructure.

ACCEPTANCE CRITERIA
AC1: docs/design/kg_dual_view_decision_20260425.md created. Section 1 MUST
     answer the open Question 0 explicitly:
        "Are we eliminating duplication (single-root consolidation) or
         legitimizing it (permanent dual view)?"
     Pick (a) or (b) with stated rationale.
AC2: If (a) "consolidate":
     - Section 2 specifies migration strategy (keep eight_essays subnode vs
       flatten as pillar2 siblings vs change kindForDepth topology).
     - Section 3 enumerates name-collision pairs (e.g.
       pillar2.unsupervised_learning vs ml-fundamentals/unsupervised) and
       resolution (merge content, dedupe, drop one side).
     - Section 4 lists implementation tasks to be split out as P1 follow-ups.
AC3: If (b) "dual view":
     - Section 2 specifies path-convention rules for additional roots
       (under what circumstances may a 3rd top-level taxonomy be added?).
     - Section 3 confirms KG-FIX-01 implementation is permanent — request
     amendment of its docstring to drop "transitional" language.
     - Section 4 closes this task with no follow-up implementation work.
AC4: Decision is shared via Discord for explicit user ratification before
     any further migration / cleanup work begins.

DEPENDS ON: KG-FIX-05 (no point answering the dual-view question until the
acute "Other" symptom is resolved and the system is observable).

COMPLEXITY: L (deferred — this is a design question, not implementation)
"""


def main() -> int:
    commands = [
        _add(
            title="[KG-FIX-01] Backend: walk parent_id for pillar derivation",
            priority="P0",
            complexity="S",
            description=DESC_FIX_01,
        ),
        _add(
            title="[KG-FIX-02] Frontend: add ml-fundamentals to PILLAR_STYLES",
            priority="P0",
            complexity="S",
            description=DESC_FIX_02,
        ),
        _add(
            title="[KG-FIX-03] Frontend: explicit PILLAR_ORDER map (step=10)",
            priority="P0",
            complexity="S",
            description=DESC_FIX_03,
        ),
        _add(
            title="[KG-FIX-04] Schema invariant + convention doc + smoke protocol + LESSONS postmortem",
            priority="P0",
            complexity="S",
            description=DESC_FIX_04,
        ),
        _add(
            title="[KG-FIX-05] Manual smoke + screenshots + HARD MERGE GATE (no auto-merge to main)",
            priority="P0",
            complexity="S",
            description=DESC_FIX_05,
        ),
        _add(
            title="[KG-DESIGN-DUAL-VIEW] Open Q: consolidate vs legitimize ml-fundamentals + pillar2 coexistence",
            priority="P2",
            complexity="L",
            description=DESC_DUAL_VIEW,
        ),
    ]
    payload = json.dumps(commands, ensure_ascii=False)
    print(f"Submitting {len(commands)} tasks via task_db batch ...", flush=True)
    proc = subprocess.run(
        [sys.executable, str(TASK_DB), "batch", "--commands", payload],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
    )
    print("STDOUT:", proc.stdout)
    if proc.stderr:
        print("STDERR:", proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        return proc.returncode

    # Show the new task IDs
    print("\nReading back new tasks ...", flush=True)
    proc2 = subprocess.run(
        [sys.executable, str(TASK_DB), "list", "--status", "active"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
    )
    if proc2.returncode == 0:
        data = json.loads(proc2.stdout or "[]")
        kg_tasks = [t for t in data if "KG-FIX" in t["title"] or "KG-DESIGN" in t["title"]]
        for t in kg_tasks:
            print(f"  {t['id']:<10} P={t['priority']} C={t.get('complexity','-')} {t['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
