"""One-off: add the 6 behavioral-review tasks approved on 2026-04-11.

Runs `task_db.py batch` with all 6 tasks + 2 inter-task depends in a single
atomic transaction. Uses $LAST to chain the last added id into the next
task's depends-on where needed.

Task numbering strategy: real category slugs and real example_id format (EX-NN
sequential) were queried from the DB first, then interpolated into the specs.
See PROGRESS.md entry 2026-04-11 for the upstream research summary.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_DB = ROOT / ".claude" / "hooks" / "task_db.py"


T1_DESC = """\
# Behavioral: seed 3 failure-story placeholders EX-30/31/32

## Context
Audit on 2026-04-11 found only 4 of 29 behavioral_examples (EX-05, EX-08, EX-19, EX-20)
contain genuine failure-learning content. All 15 failure-ask questions route to this
tiny pool, so a two-failure-question interview round forces story reuse. Placeholders
reserve three slots; real content is filled later by the user (no invented stories).

## Placeholder slots
- EX-30 Technical miscall (wrong architecture / premature optimization / over-engineering)
- EX-31 Interpersonal failure (mishandled peer conflict / lost trust / botched feedback)
- EX-32 Execution / delivery miss (missed deadline w/ customer impact / shipped regression / wrong project bet)

## Scenario matrix
| Condition | Expected |
|---|---|
| Placeholder title visible in example drawer | Rendered with distinct "needs-input" warning badge, NOT hidden |
| STAR fields empty | Frontend renders "(missing -- pending user input)" fallback, NOT crash or raw empty strings |
| User later fills the slot | Same row updated in place; `[NEEDS-INPUT]` prefix removed from title |
| Placeholder linked to non-failure-ask Q | Must NOT happen -- only the 15 failure-ask Qs get the links |
| Re-running the seed script | Idempotent: existing EX-30/31/32 not duplicated |

## Acceptance criteria
- [ ] behavioral_examples has 3 new rows with example_id in (EX-30, EX-31, EX-32)
- [ ] Titles start with `[NEEDS-INPUT] Failure story:` + theme label
- [ ] situation=task=action=result="" on all 3 placeholders
- [ ] risk_statement non-empty, format: "Audit 2026-04-11 found 4/29 examples contain genuine failure content. Placeholder reserves a slot for <theme> failure story."
- [ ] principle_tags = "failure,learning,needs_input"
- [ ] All 15 failure-ask question_ids linked to >=1 placeholder via question_example_links.relevance_note='[PLACEHOLDER] pending user-authored failure story'. The 15 question_ids are: OWN-1, OWN-8, OWN-11, COL-1, COL-2, COM-5, ADP-5, ADP-11, ADP-13, ADP-15, ADP-18, ADP-19, EXE-2, EXE-6, EXE-9
- [ ] docs/human_input/EX-30-32_failure_placeholders.md created with per-slot prompts: "What went wrong?" / "What did you do?" / "What did you learn?" / "What would you do differently?" + estimated word count + STAR reminder
- [ ] TASKS.md projection shows `[NEEDS-INPUT: 3 failure stories]` marker on this task row
- [ ] Consumer audit: ExampleDrawerContent.tsx handles empty STAR fields with "(missing -- pending)" fallback, not broken layout
- [ ] scripts/_seed_failure_placeholders.py is idempotent (re-runnable without duplicates)

## Manual smoke test
1. `scripts/dev.py` -> wait for "Application startup complete"
2. Open BehavioralQuestions page
3. Navigate to ADP-15 ("biggest lesson from a failed project")
4. Linked examples list shows EX-30/31/32 placeholders with warning badge visibly distinct from real examples
5. Click a placeholder -> drawer opens, STAR sections render "(missing -- pending user input)" fallback, no crash
6. Verify via API: `curl /api/behavioral/examples/EX-30` returns row with empty STAR fields and non-empty risk_statement
"""


T2_DESC = """\
# Behavioral: secondary links for single-link Qs in communication/collaboration/leadership

## Context
Audit 2026-04-11: 54% of questions (62/115) have only 1 link in question_example_links.
The three smallest-avg categories are communication (5 Qs), collaboration (9 Qs),
leadership (11 Qs) -- each averaging ~1.2 links per question. A single-linked question
leaves no rotation option if that example was just used on a prior question.

## Scenario matrix
| Condition | Expected |
|---|---|
| Q in {communication, collaboration, leadership} AND link_count == 1 | Add 1 secondary link |
| Q in {communication, collaboration, leadership} AND link_count >= 2 | Skip (already covered) |
| Q in other categories AND link_count == 1 | Out of scope (deferred to future task) |
| Existing links | Never modified or deleted (additive only) |
| Re-running verification | Produces 0 single-link rows in target categories |

## Acceptance criteria
- [ ] Every question with `category_id IN ('communication','collaboration','leadership')` and link_count==1 now has link_count>=2
- [ ] Each newly-created link has non-empty relevance_note (>=30 chars) explaining the semantic fit
- [ ] No existing link row modified or deleted
- [ ] scripts/verify_behavioral_links.py written; exits 0 and prints "0 remaining single-link rows in target categories"
- [ ] Total new links added matches the expected count (compute before starting: SELECT questions with link_count==1 in target cats)
- [ ] Each new link's example is semantically defensible (not just a random pad)

## Manual smoke test
1. `scripts/dev.py` -> dev server up
2. Open BehavioralQuestions -> filter to Communication & Influence
3. Open each of the 5 questions' example drawers
4. Each shows >=2 examples, each with a non-empty relevance_note
5. Repeat for Teamwork & Cross-Functional Collaboration (9 Qs) and Leadership & People Development (11 Qs)
6. Run verification script and confirm it reports 0 remaining single-link rows in target categories
"""


T3_DESC = """\
# Behavioral: 15-theme vocabulary, tag tables, keyword backfill

## Context
Audit 2026-04-11 proposed 15 themes cross-cutting the existing 9 category taxonomy.
Themes are: technical_problem_solving, collaboration_teamwork, leadership_direction,
process_systems, failure_setback, prioritization_tradeoffs, ownership_accountability,
data_analysis, conflict_disagreement, deadline_pressure, mentoring_coaching,
scope_creep_ambiguous, code_quality_tech_debt, ambiguity_uncertainty,
oncall_prod_incident (intentionally empty -- future human-input target).

## Scenario matrix
| Condition | Expected |
|---|---|
| Question text matches >=1 theme keyword rule | Insert row(s) in question_theme_tags |
| Question text matches 0 keyword rules | Log as unclassified; script emits a "needs-human-review" list |
| Example STAR+principle_tags matches >=1 rule | Insert row(s) in example_theme_tags |
| Example matches 0 rules | Log as unclassified |
| Re-run seed script on already-tagged DB | Idempotent: no duplicate rows, existing tags preserved |
| Theme with 0 matches (oncall_prod_incident) | Row still in behavioral_themes table; API returns count=0 |
| API called with unknown theme slug | 400 Bad Request |
| API called with valid slugs in AND mode | Returns intersection |
| API called with valid slugs in OR mode | Returns union |

## Acceptance criteria
- [ ] New tables: behavioral_themes(id, slug UNIQUE, label, description, display_order); question_theme_tags(question_id FK, theme_id FK, composite PK); example_theme_tags(example_id FK, theme_id FK, composite PK). ON DELETE CASCADE from behavioral_questions and behavioral_examples.
- [ ] Schema migration follows whatever mechanism src/backend/models/ already uses (investigate first; do NOT invent a new one)
- [ ] SQLAlchemy models in src/backend/models/behavioral_theme.py; pydantic schemas in src/backend/schemas/behavioral_theme.py
- [ ] behavioral_themes seeded with exactly 15 rows; slug snake_case, label Title Case, display_order matches frequency rank from audit
- [ ] question_theme_tags: >=110 of 115 questions tagged (<=5% unclassified)
- [ ] example_theme_tags: 29 of 29 examples tagged with >=1 theme
- [ ] Backend: GET /api/behavioral/themes returns list of {slug, label, question_count, example_count}
- [ ] Backend: GET /api/behavioral/questions?theme=slug1,slug2&theme_mode=or|and filters correctly; unknown slug -> 400
- [ ] scripts/seed_behavioral_themes.py is idempotent (re-runnable)
- [ ] tests/test_behavioral_themes.py covers: seed, filter by single theme, filter by multi-theme OR, filter by multi-theme AND, re-run idempotency, cascade delete

## Manual smoke test (cross-boundary: verify via API consumer, not raw SELECT per CLAUDE.md)
1. `scripts/dev.py` -> backend up
2. `curl /api/behavioral/themes` -> 15 themes with counts. failure_setback count ~10, oncall_prod_incident count 0
3. `curl /api/behavioral/questions?theme=failure_setback` -> exactly the ~10 questions tagged with that theme
4. `curl /api/behavioral/questions?theme=failure_setback,leadership_direction&theme_mode=and` -> intersection (smaller set)
5. `curl /api/behavioral/questions?theme=failure_setback,leadership_direction&theme_mode=or` -> union (larger set)
6. `curl /api/behavioral/questions?theme=not_a_theme` -> 400
7. Re-run `python scripts/seed_behavioral_themes.py` -> reports no changes (idempotent)
"""


T4_DESC = """\
# Behavioral: theme pills + frequency-sorted filter sidebar on BehavioralQuestions page

## Context
Frontend consumer of the theme backend (Task 3). Adds a secondary tag axis to question
rows + new filter sidebar cross-cutting the existing category filter. URL-persisted
state for shareable filter links.

## Scenario matrix
| Condition | Expected |
|---|---|
| No theme selected | Show all questions (category filter unchanged) |
| 1 theme selected | Show only questions tagged with that theme |
| >=2 themes + OR mode | Show questions matching ANY selected theme |
| >=2 themes + AND mode | Show questions matching ALL selected themes |
| Category filter AND theme filter both active | Intersection (AND between the two axes; user-controlled mode within themes) |
| Theme with 0 matches (oncall_prod_incident) | Sidebar entry still shown with "(0)" count; clicking filters to empty state with "no questions yet" placeholder |
| User clicks theme pill on a question row | That theme toggles in the sidebar (adds if absent, removes if present) |
| URL has themes+mode query params on page load | State restored from URL |
| Viewport < md | Sidebar collapses to bottom-sheet drawer |

## Acceptance criteria
- [ ] BehavioralQuestions.tsx renders theme pills under the existing category pill on each question row (max 5 visible, overflow "+N more" popover)
- [ ] New ThemeFilterSidebar.tsx component lists 15 themes sorted by question_count desc, shows count, supports multi-select
- [ ] AND/OR mode toggle in sidebar
- [ ] URL state: ?themes=slug1,slug2&theme_mode=or round-trips correctly on refresh/share
- [ ] Category filter + theme filter intersect (AND across axes)
- [ ] Clicking a theme pill on a row toggles that theme in the sidebar
- [ ] Mobile: sidebar becomes a bottom sheet below md breakpoint
- [ ] Validation: `npm run build` (tsc -b + vite build) passes -- not just `tsc --noEmit`
- [ ] Vitest tests: URL-param round trip, OR vs AND mode logic, click-to-toggle from row pill
- [ ] Consumer audit: list every component consuming behavioral_questions response; each has a fallback for empty/missing theme_tags array so old cached data doesn't crash

## Manual smoke test
1. `scripts/dev.py` -> dev server up
2. On 1920px monitor: navigate to BehavioralQuestions
3. Select "Failure & Setback" in sidebar -> list narrows to ~10 items
4. Toggle AND mode + also select "Leadership & Direction" -> list narrows further
5. Refresh page -> both themes still selected, list still filtered (URL-persisted)
6. Click a theme pill inside any question row -> that theme highlights/unhighlights in sidebar
7. Resize to <768px -> sidebar collapses to bottom sheet; toggle still works
8. Verify that clearing theme filter restores full list without touching category filter

## Dependencies
Depends on Task 3 (theme backend must exist for the sidebar to query /api/behavioral/themes).
"""


T5_DESC = """\
# Frontend: DrawerLayout single-source-of-truth responsive two-column refactor

## Context
SlideOverPanel.tsx:18 defaults to max-w-xl (576px). BehavioralQuestions.tsx:677 invokes
it without a width prop, so the behavioral-example drawer is stuck at 576px on all
monitors. On 1920px: ~30% viewport utilization; on 2560px: ~23%. User reports content
"compressed into a small strip on the right" on wide screens.

**Design constraint**: prose readability caps at ~75ch (~720px at 15px font). Naive
"stretch drawer wider" produces unreadable walls of text. Correct fix is a two-column
layout that spends extra pixels on metadata context, not on fatter prose.

**Scope expansion (user-confirmed 2026-04-11)**: apply uniformly to the drawer family.
Build a single DrawerLayout component as the source of truth; migrate SlideOverPanel's
behavioral-example drawer AND PrepNotesModal AND any other long-form drawer found via
grep audit. Future drawer styling changes then happen in exactly one place.

## Design spec

### Drawer container width breakpoints
- base: max-w-xl (576px)
- md: max-w-2xl (672px)
- lg: max-w-4xl (896px)
- xl: max-w-5xl (1024px)
- 2xl: max-w-6xl (1152px)

### DrawerLayout internal layout (new component)
- Props: {left: ReactNode, right: ReactNode, variant?: 'two-column' | 'single-column', leftWidth?: string}
- Default variant: two-column on >=lg, single-column below
- Two-column: flex row, left pane sticky top-0 w-72 (288px), right pane flex-1 with inner `max-w-[680px]` prose cap
- Single-column: stacked, left content first, then right content
- Opt-out: pass variant='single-column' to force single layout (for short-form drawers where two-column looks silly)

### Left pane contents
- Behavioral example: question_id badge, category pill, theme pills, source_project, linked-question quick-jump list, prev/next example nav
- Prep notes: company name, applied_at, status, "view in companies" link

### Right pane contents
- Long-form STAR sections (situation/task/action/result) OR markdown prep notes
- Inner wrapper `<div className="max-w-[680px]">` enforces 75ch readability cap
- Remaining pixels in the right pane beyond 680px are intentional whitespace -- do NOT stretch prose to fill

## Scenario matrix
| Viewport | Drawer width | Layout | Prose cap |
|---|---|---|---|
| <md | max-w-xl | single column | fills container |
| md..lg | max-w-2xl | single column | fills container |
| lg..xl | max-w-4xl | two column | 680px |
| xl..2xl | max-w-5xl | two column | 680px |
| >=2xl | max-w-6xl | two column | 680px |
| Short content (e.g., 5-bullet prep notes) | Same breakpoint width | two column; right pane naturally short, no forced empty space | 680px |
| Drawer explicitly opts out via variant='single-column' | Same breakpoint width | single column, full width up to breakpoint cap | 680px |
| User resizes browser across breakpoint | Layout re-computes via CSS only (no JS resize hooks) | correct at new breakpoint | 680px |

## Acceptance criteria
- [ ] New `src/frontend/src/components/ui/DrawerLayout.tsx` with the API above
- [ ] DrawerLayout is the ONLY place that encodes the two-column drawer pattern (single source of truth -- no duplicate flex/grid logic in consumer components)
- [ ] SlideOverPanel.tsx accepts responsive width classes (not a single fixed max-w)
- [ ] ExampleDrawerContent.tsx refactored to `<DrawerLayout left={<ExampleMetaPane/>} right={<ExampleStarContent/>} />`
- [ ] PrepNotesModal.tsx refactored to use DrawerLayout
- [ ] Prose `max-w-[680px]` enforced on all long-form text columns inside the right pane
- [ ] Drawer family audit: grep all `SlideOverPanel` and `Modal` imports across `src/frontend/src/`; list every usage in the PR description with an "adopted / opted-out / N/A" decision column; every drawer with long-form content either adopts DrawerLayout or opts out with explicit justification
- [ ] `npm run build` passes (tsc -b + vite build)
- [ ] Existing Vitest tests pass; new tests for DrawerLayout cover two-column, single-column, sticky left pane, responsive collapse
- [ ] Consumer audit: no existing drawer consumer renders incorrectly after refactor (visual check on dev server)

## Manual smoke test (MUST run on dev server per CLAUDE.md -- not just tests)
1. `scripts/dev.py` -> wait for "Application startup complete"
2. On 1920px monitor: open BehavioralQuestions -> click any question -> example drawer opens in two-column layout; left pane sticky with meta; right pane shows STAR prose capped at readable width
3. Resize browser narrower past lg breakpoint -> drawer collapses to single-column stack without layout break
4. Open Dashboard -> click a company name on an event (e.g., Lyra) -> PrepNotesModal opens with the same responsive two-column behavior (left: company meta; right: markdown prep notes)
5. On 2560px (or DevTools responsive emulation): drawer uses max-w-6xl (1152px) but prose still caps at 680px; extra ~180px is intentional whitespace, NOT stretched text
6. Open a short-form drawer (or one explicitly opted out): renders single-column correctly
7. Grep check: after refactor, search for `flex.*w-72` or two-column patterns in drawer-adjacent files -- only DrawerLayout.tsx should contain the implementation

## Dependencies
None (can interleave with Task 4).
"""


T6_DESC = """\
# Behavioral: semantic relevance spot-check script for 10 random Q-example links

## Context
Audit 2026-04-11 confirmed valence matching is correct (failure Qs route to
failure-ish examples) but flagged quantity-over-precision risk: some links may
have low semantic specificity. Randomly sample 10 links and human-review each
for semantic fit (not just valence).

## Scenario matrix
| Condition | Expected |
|---|---|
| Script run in review mode | Prints 10 pairs + reviewer checklist template |
| Script run in apply mode on filled-in review file | DB reflects keep/drop/update-note decisions |
| Re-running review mode with same seed | Selects the same 10 pairs (reproducible) |
| Re-running review mode with different seed | Selects a different 10 (for follow-up audits) |

## Acceptance criteria
- [ ] scripts/audit_qe_link_relevance.py uses random.Random(seed) with seed defaulting to 20260411 for reproducibility
- [ ] Review mode: for each of 10 random links, print question text, example title + 1-line situation + 1-line result, current relevance_note, and a markdown checklist line (keep / drop / update-note)
- [ ] Apply mode: read a filled-in markdown file and apply the decisions (DROP removes the link row, UPDATE overwrites relevance_note, KEEP no-op)
- [ ] Output report committed to docs/audits/qe_link_spotcheck_2026-04-11.md
- [ ] Script tolerates resumption (if reviewer only filled in 5 of 10, skip unfilled)

## Manual smoke test
1. Run `python scripts/audit_qe_link_relevance.py --mode review`
2. Fill decisions in docs/audits/qe_link_spotcheck_2026-04-11.md
3. Run `python scripts/audit_qe_link_relevance.py --mode apply --file docs/audits/qe_link_spotcheck_2026-04-11.md`
4. Verify via API consumer: `curl /api/behavioral/questions/<id>/examples` on a modified question shows updated relevance_notes (per CLAUDE.md rule "verify via consumer, not producer")

## Dependencies
Depends on Task 2 (after secondary links are added, the sampling pool reflects the final state of the corpus).
"""


COMMANDS = [
    {
        "cmd": "add",
        "title": "Behavioral: seed 3 failure-story placeholders EX-30/31/32 with [NEEDS-INPUT] markers",
        "priority": "P0",
        "complexity": "S",
        "description": T1_DESC,
    },
    {
        "cmd": "add",
        "title": "Behavioral: add secondary example links for single-link Qs in communication/collaboration/leadership",
        "priority": "P1",
        "complexity": "S",
        "description": T2_DESC,
    },
    {
        "cmd": "add",
        "title": "Behavioral: seed 15-theme vocabulary, tag tables, and keyword backfill on Qs and examples",
        "priority": "P1",
        "complexity": "M",
        "description": T3_DESC,
    },
    {
        "cmd": "add",
        "title": "Behavioral: theme pills on question rows + frequency-sorted filter sidebar on BehavioralQuestions page",
        "priority": "P1",
        "complexity": "M",
        "description": T4_DESC,
    },
    {
        "cmd": "add",
        "title": "Frontend: DrawerLayout single-source-of-truth responsive two-column refactor for drawer family",
        "priority": "P1",
        "complexity": "L",
        "description": T5_DESC,
    },
    {
        "cmd": "add",
        "title": "Behavioral: semantic relevance spot-check script for 10 random Q-example links",
        "priority": "P2",
        "complexity": "S",
        "description": T6_DESC,
    },
]


def main() -> None:
    # Step 1: batch-add all 6 tasks (no dependencies yet -- $LAST is only
    # resolved for `id`/`on` fields in batch, not `depends_on`).
    payload = json.dumps(COMMANDS, ensure_ascii=False)
    result = subprocess.run(
        [sys.executable, str(TASK_DB), "batch", "--commands", payload],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    result.check_returncode()

    parsed = json.loads(result.stdout)
    if not parsed.get("ok"):
        raise RuntimeError(f"Batch add failed: {parsed}")

    ids = [r["id"] for r in parsed["results"]]
    assert len(ids) == 6, f"expected 6 task ids, got {ids}"
    t1, t2, t3, t4, t5, t6 = ids
    print(f"Added: T1={t1} T2={t2} T3={t3} T4={t4} T5={t5} T6={t6}")

    # Step 2: add the two cross-task dependencies as a second batch call.
    dep_payload = json.dumps(
        [
            {"cmd": "depend", "id": t4, "on": t3},
            {"cmd": "depend", "id": t6, "on": t2},
        ]
    )
    dep_result = subprocess.run(
        [sys.executable, str(TASK_DB), "batch", "--commands", dep_payload],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print("DEP STDOUT:", dep_result.stdout)
    if dep_result.stderr:
        print("DEP STDERR:", dep_result.stderr)
    dep_result.check_returncode()

    dep_parsed = json.loads(dep_result.stdout)
    if not dep_parsed.get("ok"):
        raise RuntimeError(f"Dependency batch failed: {dep_parsed}")

    print(f"[OK] Dependencies: {t4} depends on {t3}, {t6} depends on {t2}")


if __name__ == "__main__":
    main()
