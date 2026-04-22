# BQ Taxonomy Delta (2026-04-21)

Phase 2 of BQ-TAX refactor. Schema uplift landed in T-P1-598 (tables
`behavioral_facets` / `question_facet_tags` / `example_facet_tags` +
`behavioral_examples.is_signature` / `signature_at` columns). This delta
seeds the reviewer-approved first batch of themes + facets.

**Seed script (source of truth):**
`scripts/seed_bq_taxonomy_delta_20260421.py` (idempotent, DB-backup-guarded).

---

## 1. Themes added (2)

Appended after the legacy 15 themes. `display_order` continues the existing
sequence -- 16 and 17.

| slug | label | display_order | Why it exists |
|------|-------|---------------|---------------|
| `customer_user_focus` | Customer & User Focus | 16 | Previously had no dedicated theme -- stories fell under generic collaboration / problem-solving. Needed for Amazon Customer Obsession, Meta Move-Fast-For-Users, Google Focus-on-the-User retrieval. Primary signal: the decision hinged on user impact rather than internal metrics or team convenience. |
| `ethical_integrity_backbone` | Ethical Integrity & Backbone | 17 | Distinct from `conflict_disagreement` (which is about navigating interpersonal tension). This theme requires a real ethical or values-based stake -- integrity, push-back at personal/political cost, disagree-not-just-commit. Amazon Have Backbone + Google Do the Right Thing retrieval axis. |

### Theme ID assignments (post-seed)

| legacy id | slug |
|---:|------|
| 1  | technical_problem_solving |
| 2  | collaboration_teamwork |
| 3  | leadership_direction |
| 4  | process_systems |
| 5  | failure_setback |
| 6  | prioritization_tradeoffs |
| 7  | ownership_accountability |
| 8  | data_analysis |
| 9  | conflict_disagreement |
| 10 | deadline_pressure |
| 11 | mentoring_coaching |
| 12 | scope_creep_ambiguous *(deprecated -- see section 3)* |
| 13 | code_quality_tech_debt |
| 14 | ambiguity_uncertainty |
| 15 | oncall_prod_incident |
| **16** | **customer_user_focus** *(new)* |
| **17** | **ethical_integrity_backbone** *(new)* |

---

## 2. Facets added (4)

Facets are the new secondary-tag layer introduced by BQ-TAX-01. See
`src/backend/models/behavioral_facet.py` module docstring for the
authoritative usage rule -- reproduced below for convenience:

> **Facet usage rule:**
> Facets are ONLY for
>   (a) staff/L6 signal tags (e.g. `strategic_scope`, `principal_judgment`),
>   (b) cross-theme retrieval tags (e.g. `fast_learning`, `scrappy_innovation`
>       that span multiple primary themes and multiple categories),
>   (c) scenario sub-type when a rename of the parent theme would mix
>       abstraction layers (e.g. `scope_creep_pm_ambiguity` under
>       `ambiguity_uncertainty`).
>
> Facets are NOT a dumping ground for "things we felt like tagging".
> Reviewers should reject facet proposals that do not fit one of the three
> slots above.

| slug | label | parent | slot | Why it exists |
|------|-------|--------|------|---------------|
| `fast_learning` | Fast Learning | NULL (cross-theme) | (b) | Reviewer: **learning is a capability, not a scenario**. Ramp-up / time-to-productivity signal spans new-domain, new-stack, new-role, first-week-in-team stories -- cannot be stuffed into any single theme without forcing an artificial narrative. |
| `scrappy_innovation` | Scrappy Innovation | NULL (cross-theme) | (b) | Reviewer: **solution style, not scenario**. "Disproportionate impact with small resources" / "unorthodox approach" cuts across technical_problem_solving, process_systems, ownership_accountability. Bias-for-Action + Invent-and-Simplify adjacent. |
| `strategic_scope` | Strategic / Org-Level Scope | NULL (cross-theme) | (a) | Reviewer: **staff/L6 signal -- do NOT split `leadership_direction`**. A leadership story can be team-scope or org-scope; the theme captures the motion, the facet captures the level. Applied when scope crosses multiple orgs, shapes multi-quarter strategy, or influences C-level/VP decisions. |
| `scope_creep_pm_ambiguity` | Scope Creep / PM Ambiguity | `ambiguity_uncertainty` | (c) | See section 3 -- demotes legacy `scope_creep_ambiguous` theme. |

---

## 3. Legacy `scope_creep_ambiguous` theme -- demotion plan

The 12th legacy theme `scope_creep_ambiguous` is being demoted to a facet
under `ambiguity_uncertainty`. Reviewer rationale:

> 场景 vs 能力 不能绑死一个 theme。
> (Scenario vs. capability cannot be bundled into a single theme.)

`ambiguity_uncertainty` is the broad *capability* axis ("operating without
full information"). `scope_creep_pm_ambiguity` is a *scenario sub-type*
under that capability ("the specific PM/stakeholder flavour of ambiguity
where requirements shift mid-flight"). Keeping them as sibling themes
forces every ambiguity-flavoured story to pick one and mislabels the other.

### Phased demotion

1. **Phase 2 (this delta)**: Insert `scope_creep_pm_ambiguity` facet under
   `ambiguity_uncertainty`. **Do NOT delete the legacy theme row** -- it
   continues to hold its existing `question_theme_tags` / `example_theme_tags`
   joins so retrieval stays intact.
2. **Phase 2.5 / BQ-TAX-03**: Retag the 34 examples + 115 questions against
   the new taxonomy. Stories currently tagged `scope_creep_ambiguous` will
   receive:
   - Primary theme `ambiguity_uncertainty` (if not already present)
   - Facet `scope_creep_pm_ambiguity` (the new retrieval axis)
3. **Phase 3** (future -- NOT this task): Once retag is verified and no
   downstream surface still reads the legacy theme, drop the
   `scope_creep_ambiguous` theme row + cascading tag joins.

---

## 4. Acceptance criteria (for this seed)

| # | Criterion | Method |
|--:|-----------|--------|
| 1 | 2 themes + 4 facets inserted after first run | `SELECT COUNT(*) FROM behavioral_themes` returns 17; `SELECT COUNT(*) FROM behavioral_facets` returns 4 |
| 2 | Idempotent: second invocation prints `[SKIP]` for every row and inserts 0 | Re-run with `--no-backup`; report shows `themes_inserted=0`, `facets_inserted=0` |
| 3 | Existing `question_theme_tags` / `example_theme_tags` counts unchanged | Pre-seed vs post-seed COUNT(*) diff is 0 (Phase 2 is schema+seed only; retag is BQ-TAX-03) |
| 4 | `scope_creep_pm_ambiguity.parent_theme_id` resolves to `ambiguity_uncertainty.id` | JOIN `behavioral_facets` -> `behavioral_themes` on `parent_theme_id` returns slug `ambiguity_uncertainty` |
| 5 | DB-file backup written before first invocation (unless `--no-backup`) | `data/mle_prep.db.bak.<ts>_pre_bq_taxonomy_delta` exists |

---

## 5. Out of scope

- **No frontend changes.** CLUSTER_FAMILIES update + facet-pill rendering +
  is_signature visual are Phase 2 BQ-TAX-04 (T-P1-601).
- **No retag.** Existing tag joins are preserved as-is; retagging is
  BQ-TAX-03 (T-P1-600).
- **No drop of legacy `scope_creep_ambiguous` theme.** Deferred to Phase 3.
- **No new golden promotion.** `is_signature` column ships empty; the
  first signature flip is a separate content task.
