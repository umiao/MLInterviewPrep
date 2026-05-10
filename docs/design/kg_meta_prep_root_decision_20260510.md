# KG `meta-prep` Root Decision (PERMANENT)

**Status**: RATIFIED
**Date ratified**: 2026-05-10
**Authoritative task**: T-P1-800 ([KG-INT B2b] Add 'meta-prep' pillar + 5 sub-node stubs)
**Parent epic**: KG-INT (T-P1-797..T-P2-836) -- per-company prose internalization
**Supersedes**: nothing (this is the 3rd top-level taxonomy after `pillar1..8` and `ml-fundamentals`).
**Authority**: `docs/design/kg_dual_view_decision_20260425.md` Section 2 Criterion A
(distinct cognitive mode + non-overlapping leaf set).

---

## Section 1 -- The Decision: TRIPLE VIEW LEGITIMIZED

The Knowledge Graph hosts **three top-level taxonomies as a permanent design**:

1. **`pillar1` .. `pillar8`** -- the *system* / knowledge-system view.
   Cognitive mode: structured, theory-deep, classical taxonomy.
2. **`ml-fundamentals`** -- the *interview-grind* view.
   Cognitive mode: leaf-dense, drill-oriented, fast-recall.
3. **`meta-prep`** (this decision) -- the *cross-company synthesis* view.
   Cognitive mode: de-companied shared substrate -- the patterns, vocabulary,
   templates, and checklists that recur across 3+ companies' prep docs and
   that the per-company prose is being archived into.

### Cognitive-mode positioning

`meta-prep` is **not** a third drill view and **not** a slice of pillarN. It is the
canonical home for cross-company shared substrate that emerges from the KG-INT
internalization protocol (`docs/workflow/company_internalization_protocol.md`).

When a behavioral pattern, a system-design vocabulary item, an LC keyword, an
onsite loop template, or a code-pad practice appears in 3+ companies' prep docs
with only cosmetic wording variation, it is **promoted** out of those per-company
docs into a `meta-prep/*` node. The per-company doc then references the meta-prep
node via `kg://N` (T-P1-799) and stores only the company-specific flavour as a
node tag (`node_company_tags.notes`).

Without a `meta-prep` root, that shared substrate would have to either:
- live duplicated under each `companies.prep_notes` field (the pre-2026-05 status
  quo -- 5-10x duplication with wording drift, the bug KG-INT exists to fix), OR
- be wedged into `pillarN` (would corrupt the system view -- `pillarN` describes
  ML/MLE concepts hierarchically; "common onsite loop templates" and "behavioral
  story clusters" are not ML concepts), OR
- be wedged into `ml-fundamentals` (would corrupt the interview-grind view --
  `ml-fundamentals` leaves are flash-card ML 八股文 questions; "AI-native
  code-pad best practices" is not an ML 八股文 question).

A separate root with its own cognitive mode is the cleanest fit.

---

## Section 2 -- Criterion A Compliance Check

Per `kg_dual_view_decision_20260425.md` Section 2 Criterion A, a 3rd root MAY be
added when ALL three sub-criteria hold. Each is verified below:

### A.1 -- Distinct cognitive mode

`meta-prep` represents *cross-company de-companied synthesis*, distinct from:
- `pillarN` (system view: ML concepts in a hierarchical theory taxonomy)
- `ml-fundamentals` (interview-grind view: flash-card 八股文 ML questions)

The substrate under `meta-prep` is not ML knowledge per se -- it is interview-prep
infrastructure (behavioral story families, SD vocabulary glossaries, LC keyword
checklists, onsite loop templates, code-pad practices). It exists to be referenced
*from* per-company prep docs, not to be studied as ML topics.

This is a genuinely distinct cognitive mode and satisfies A.1.

### A.2 -- Non-overlapping leaf set

The 5 initial sub-nodes seeded by T-P1-800 are:

| Path                                       | Leaf-set source                                              |
|--------------------------------------------|--------------------------------------------------------------|
| `meta-prep/behavioral-clusters`            | T-P1-803 -- per-company BQ docs (`behavioral_examples` + `companies.prep_notes` BQ sections) |
| `meta-prep/lc-keyword-checklists`          | T-P1-806 -- per-company LC notes (`problems.notes` + `companies.prep_notes` LC sections)     |
| `meta-prep/system-design-must-knows`       | T-P1-804 -- per-company SD docs (`company_documents` + `system_designs`)                     |
| `meta-prep/onsite-loop-templates`          | T-P1-807 -- per-company onsite docs (`companies.prep_notes` onsite sections)                 |
| `meta-prep/code-pad-best-practices`        | T-P1-805 -- per-company code-pad notes                                                       |

None of these 5 leaves duplicate any existing `pillarN` or `ml-fundamentals` leaf:

- **Behavioral story clusters** is BQ infrastructure (cross-references
  `behavioral_examples`); pillarN has no BQ leaf set, ml-fundamentals has none.
- **LC keyword checklists** is a *checklist* (mnemonic prompts that map keywords
  to algorithmic patterns); the pattern leaves themselves live under
  `pillar1.data_structures.*` and `pillar1.algorithms.*` -- the checklist is a
  fast-prep meta-layer that points to those leaves, not a duplicate of them.
- **SD must-knows** is a *vocabulary glossary* (retrieval/ranking/calibration/
  drift terms in 1-line definitions); the SD curriculum leaves live under
  `pillar3.*` and are full design problems -- the glossary is a fast-prep
  meta-layer that points to those leaves, not a duplicate.
- **Onsite loop templates** are *interview-format playbooks* (5x45min vs 4x60min,
  round types per company); no `pillarN` or `ml-fundamentals` leaf covers
  interview-format choreography.
- **Code-pad best practices** are *AI-native pair-programming practices*
  (dictation discipline, plain-text formula reading); no existing leaf covers
  workflow practices for the AI-assisted code-pad surface.

A.2 satisfied.

### A.3 -- Path separator + frontend registration in same change set

- Separator: slash (`/`), matching the `ml-fundamentals` precedent.
- Frontend `PILLAR_STYLES` (`src/frontend/src/components/kg/kgStyles.ts`) extended
  with `meta-prep` in this same change set.
- Frontend `PILLAR_ORDER` (`src/frontend/src/components/kg/useKgLayout.ts`)
  extended with `meta-prep: 85` (positioned after `pillar8: 80`, since meta-prep
  is the cross-cutting synthesis layer that consumes from all pillars).
- `RATIFIED_SLASH_ROOTS` registry in
  `tests/test_framework_path_convention.py` extended.
- `kgStyles.test.ts` and `useKgLayout.test.ts` extended.

A.3 satisfied.

---

## Section 3 -- KG-FIX-01 `_pillar_of` Walk Continues To Work

The `_pillar_of()` function in `src/backend/routers/kg.py` walks `parent_id` to
the depth=0 ancestor and returns its path string. This is taxonomy-agnostic and
works for `meta-prep` paths exactly as it works for `pillarN.subtopic.leaf` and
`ml-fundamentals/cat/leaf`. **No backend code change** is needed for the new root.

This was verified empirically before this doc was committed:
`/api/kg/graph?limit=2000` returns the 6 meta-prep nodes with `pillar='meta-prep'`
on every node in the subtree.

---

## Section 4 -- Stubs Now, Content Later

T-P1-800 (this task) seeds the root + 5 sub-nodes as **stubs only**. The 5
sub-node descriptions are one-line `TODO[KG-INT-B3-*]` placeholders. Content is
filled by the B3 follow-up tasks:

- T-P1-803 fills `behavioral-clusters`
- T-P1-804 fills `system-design-must-knows`
- T-P1-805 fills `code-pad-best-practices`
- T-P1-806 fills `lc-keyword-checklists`
- T-P1-807 fills `onsite-loop-templates`

After B3 completes, T-P1-821 (`B4-promotion`) consolidates patterns flagged by
B4a per-company archive plans (T-P0-808..T-P0-814 + T-P1-815..T-P1-820) into
additional `meta-prep` updates.

---

## Section 5 -- Future-Only Ideas (P3, do NOT auto-promote)

The following are ideas tracked here so they are not lost. They are explicitly
**not** P1/P2 follow-ups and require a fresh user-triggered task spec to enter
the backlog:

- **Per-company tag overlay on meta-prep nodes**: when a user opens a
  meta-prep node from a company drawer (via `kg://N`), surface the
  `node_company_tags.notes` row (if any) as a "company flavour" panel so the
  shared substrate and the company-specific spin appear together.
- **Promotion candidate inbox**: a UI surface listing nodes that have been
  flagged for promotion to meta-prep (via §5 of B4a archive plans) but not yet
  consolidated by T-P1-821.
- **Reverse-link panel**: on a meta-prep node, list which `companies` reference
  it (via `node_company_tags`) for at-a-glance prevalence.

These are P3 *ideas only*. Do not file P1/P2 tasks for them.

---

## References

- Authority: `docs/design/kg_dual_view_decision_20260425.md` Section 2 Criterion A.
- Internalization protocol: `docs/workflow/company_internalization_protocol.md`.
- Promotion criteria: `docs/workflow/promotion_criteria.md`.
- Seed script: `scripts/seed_meta_prep_pillar.py`.
- Source of truth function: `src/backend/routers/kg.py` `_pillar_of()`.
- Frontend registries: `src/frontend/src/components/kg/kgStyles.ts`,
  `src/frontend/src/components/kg/useKgLayout.ts`.
- Test enforcement: `tests/test_framework_path_convention.py`
  `RATIFIED_SLASH_ROOTS`.
