# KG Dual-View Decision (PERMANENT)

**Status**: RATIFIED
**Date ratified**: 2026-04-26 (Discord msg 1497773776006545428, chat 1484761064292749422)
**Authoritative task**: T-P2-614 (KG-DESIGN-DUAL-VIEW)
**Supersedes**: any "transitional" / "temporary" framing of the multi-root taxonomy
that appeared in KG-FIX-01..05 commit messages, intermediate notes, or docstrings.

---

## Section 1 -- The Decision: DUAL VIEW LEGITIMIZED

The Knowledge Graph hosts **two top-level taxonomies as a permanent design**:

1. **`pillar1` .. `pillar8`** -- the *system* / knowledge-system view.
   - Cognitive mode: structured, theory-deep, classical taxonomy.
   - Authoring style: hierarchical decomposition of ML / MLE concepts grouped by
     pillar (e.g. `pillar2.feature_engineering`, `pillar3.deep_learning`).
   - Primary use case: building mental models, mapping concepts to a stable
     framework, long-form study.

2. **`ml-fundamentals`** -- the *interview-grind* view.
   - Cognitive mode: leaf-dense, drill-oriented, fast-recall.
   - Authoring style: flatter slash-separated subtree (e.g.
     `ml-fundamentals/classical_ml/bias-variance-tradeoff`).
   - Primary use case: timed mock interviews, daily flash-card style drills,
     fast jump-to-leaf during prep sessions.

### User ratification quote (Discord)

> Option (b) DUAL VIEW LEGITIMIZED.
>
> Rationale: ml-fundamentals (interview-grind / leaf-dense / drill-oriented) and
> pillar2 (knowledge-system / structured / theory-deep) serve different
> cognitive modes. Forcing consolidation back into pillar2 would reduce
> utilitarian interview-prep effectiveness. The KG-FIX-01 parent_id walk works
> correctly for both roots; no migration needed.

(Source: Discord chat 1484761064292749422, msg 1497773776006545428, 2026-04-26.)

### What this resolves

- The "consolidate ml-fundamentals back into pillar2 vs. keep both" question
  raised during KG-FIX-04 (LESSONS postmortem 2026-04-25) is **closed**.
- KG-FIX-01..05 commit messages and intermediate docstrings that hedge with
  "transitional" / "temporary" / "until the design question is answered" are
  superseded by this document. The mechanism is now **permanent infrastructure**.
- No data migration is needed. The two roots coexist as-is.

---

## Section 2 -- Path-Convention Rules for Additional Roots

**Default: 2 roots only.** Adding a 3rd top-level taxonomy is **forbidden**
unless the proposal meets one of the two criteria below, documented in a new
`docs/design/kg_*_decision_<date>.md` file and approved by the user.

### Criterion A -- Distinct cognitive mode AND non-overlapping leaf set

A 3rd root MAY be added when ALL of the following hold:

1. The proposed root represents a **cognitive mode that is genuinely distinct**
   from both `pillarN` (system view) and `ml-fundamentals` (interview-grind
   view). Examples of plausible distinct modes:
   - `interview-systems-design` -- end-to-end SD prep, scenario-shaped, where
     leaves are full design problems rather than concepts.
   - `behavioral-prep` -- if STAR stories ever became KG-shaped (currently they
     live in `behavioral_examples`, not `framework_nodes`, so this is
     hypothetical).
2. The leaf set is **non-overlapping** with both existing roots. Concepts that
   already exist under `pillarN` or `ml-fundamentals` MUST NOT be re-rooted; new
   leaves only.
3. A path-separator convention is declared up front (slash, dot, or other) and
   `kgStyles.ts` `PILLAR_STYLES` + `useKgLayout.ts` `PILLAR_ORDER` are extended
   in the same change set (per
   `docs/protocol/kg_markdown_conventions.md` Sec. 10 -- the FIX-04 invariant).

### Criterion B -- Strict view-of-same-leaves justification

A 3rd root MAY be added when it is an **explicit alternate projection** of an
existing leaf set, rather than introducing new leaves. In that case:

1. The proposal MUST state the projection explicitly (e.g. "this root reorders
   pillar2's leaves by company-frequency for fast-prep scoping; same node ids,
   different parent_id wiring is forbidden -- the projection lives in a
   separate model, not framework_nodes").
2. Such a projection MUST NOT be implemented by mutating `parent_id` (which
   would corrupt the system view). Use a side table or a derived view instead.

### Forbidden patterns

- 3rd root that re-roots existing pillarN leaves into a new tree
  (would silently break the system view).
- 3rd root that mixes path separators within itself
  (e.g. `mixed-root/topic.subtopic`) -- pick one separator for the root and
  stick to it for all descendants.
- "Synonym roots" that duplicate concepts under multiple labels for SEO-style
  reasons -- the KG is a study tool, not a discoverability surface.

---

## Section 3 -- KG-FIX-01 `_pillar_of` Walk Is Permanent

The `_pillar_of()` function in `src/backend/routers/kg.py` (introduced by
T-P0-609 / KG-FIX-01) walks the `parent_id` chain to derive a node's depth=0
ancestor. **This is permanent infrastructure**, not a transitional shim.

### Why permanent

The dual-view design (Section 1) means the KG **always** contains nodes whose
ancestor chain ends at one of multiple roots with potentially different
path-separator conventions. The naive `path.split(".", 1)[0]` derivation that
predated KG-FIX-01 is **incorrect** for the slash-separated `ml-fundamentals`
subtree and for any future Section-2-approved 3rd root. The `parent_id` walk is
the only taxonomy-agnostic mechanism that works across all roots.

### Docstring update

The `_pillar_of` docstring in `src/backend/routers/kg.py` has been updated by
this task to drop the "transitional vs permanent question is open" hedging and
reference this decision document. See the function header in that file.

### Do NOT revert

Do not revert `_pillar_of` to `path.split(".", 1)[0]` (or any other
path-prefix-based derivation) under any circumstances. Doing so will:

- Break the `ml-fundamentals` view immediately (slash-separated paths have
  no `.` to split on, so the entire path becomes the "pillar" key, missing
  `PILLAR_STYLES` / `PILLAR_ORDER`, and the subtree falls back to grey).
- Silently break any future Section-2-approved 3rd root with a non-dot
  separator.
- Re-introduce the exact bug fixed by KG-FIX-01..05 (postmortem in
  `LESSONS.md` 2026-04-25).

---

## Section 4 -- No Follow-Up Implementation Work

This task closes the design question. **No further implementation work is
required**:

- Backend: `_pillar_of` is already correct (KG-FIX-01).
- Frontend `PILLAR_STYLES`: `ml-fundamentals` is registered (KG-FIX-02).
- Frontend `PILLAR_ORDER`: `ml-fundamentals` has an explicit step=10 slot
  (KG-FIX-03).
- Schema invariant + convention doc: documented (KG-FIX-04).
- Smoke test: passed (KG-FIX-05; artifacts in `logs/kg_fix_smoke_20260425/`).

### Nice-to-have UX ideas (P3, do NOT promote without user trigger)

The following are *future-only ideas* tracked here so they are not lost. They
are explicitly **not** P1/P2 follow-ups and require a fresh user-triggered task
spec to enter the backlog:

- **Root-toggle affordance**: a small UI control in the KG header that lets the
  user toggle between "system view" (pillar1..8) and "interview-grind view"
  (ml-fundamentals), filtering the rendered nodes accordingly. Currently the
  user navigates via the existing pillar filter -- adequate, but could be made
  more discoverable.
- **Root-distinct visual treatment**: subtle visual cue (e.g. a different lane
  background tint or a small badge on root nodes) to communicate at a glance
  which root a subtree belongs to. Today they are differentiated only by lane
  color via `PILLAR_STYLES`.
- **Cognitive-mode hint in tooltips**: tooltips on root nodes could explain the
  cognitive-mode positioning ("System view -- structured / theory-deep" vs
  "Interview-grind view -- leaf-dense / drill-oriented") to onboard new users.

These are P3 *ideas only*. Do not file P1/P2 tasks for them.

---

## References

- Task: T-P2-614 (KG-DESIGN-DUAL-VIEW).
- Predecessor epic: T-P0-609..T-P0-613 (KG-FIX-01..05).
- Postmortem: `LESSONS.md` 2026-04-25 entry.
- Convention rule: `docs/protocol/kg_markdown_conventions.md` Sec. 10.
- Smoke evidence: `logs/kg_fix_smoke_20260425/`.
- Source of truth function: `src/backend/routers/kg.py` `_pillar_of()`.
