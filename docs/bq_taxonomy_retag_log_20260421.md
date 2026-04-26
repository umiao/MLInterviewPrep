# BQ-TAX Phase 2 retag log (T-P1-600 / BQ-TAX-03)

**Date**: 2026-04-26
**Driver**: `scripts/seed_bq_taxonomy_retag_20260421.py`
**Purpose**: Per-row rationale for the new theme/facet assignments and the
legacy `scope_creep_ambiguous` -> `scope_creep_pm_ambiguity` migration.
This doc is the source of truth; the seed script is its executable form.
If a tag is added or removed, **update this doc first**, then update the
script's `*_NEW_*_TAGS` dicts.

---

## Tagging philosophy

The new themes/facets seeded by BQ-TAX-02 must be applied **conservatively**.
Reviewers explicitly rejected "tag every plausibly related row" — facets in
particular are not a dumping ground (see
`src/backend/models/behavioral_facet.py` module docstring).

Each new theme/facet has a strict admit rule:

| Slug | Admit rule (must be the central narrative axis) |
|------|---------------------------------------------------|
| `customer_user_focus` | Decision hinged on user/customer impact rather than internal metrics or team convenience. Pure UX-adjacency (e.g. latency tuning) is **not** sufficient. |
| `ethical_integrity_backbone` | Real ethical / values-based stake OR explicit disagree-not-just-commit backbone with personal/political cost. Distinct from `conflict_disagreement` (which is about navigating tension). |
| `fast_learning` | Time-to-productivity / ramp-up speed in a new domain/stack/role is the central signal. |
| `scrappy_innovation` | Disproportionate impact with small resources / unorthodox approach (bias-for-action, invent-and-simplify adjacent). |
| `strategic_scope` | Scope of impact crosses multiple orgs, shapes multi-quarter strategy, or influences C-level / VP decisions. |

---

## Part 1 — Mechanical migration (`scope_creep_ambiguous` -> facet)

The legacy `scope_creep_ambiguous` theme conflated "scenario sub-type"
(scope creep / PM ambiguity) with the broader theme `ambiguity_uncertainty`
(see BQ-TAX-02 reviewer note). Phase 3 demotes it to a sub-facet under
`ambiguity_uncertainty` and drops the legacy theme.

**Migration rule**: every example/question currently tagged with
`scope_creep_ambiguous` -> add `scope_creep_pm_ambiguity` facet, drop the
theme tag. No judgment involved; this is mechanical.

| Examples migrated (7 rows) | Questions migrated (7 rows) |
|----------------------------|-------------------------------|
| EX-02, BLOG-04, EX-14, EX-18, EX-23, EX-24, EX-30 | ADP-2, ADP-3, ADP-4, ADP-7, ADP-8, ADP-9, EXE-8 |

After migration: `behavioral_themes` row count goes 17 -> 16, all
`example_theme_tags` / `question_theme_tags` rows referencing
`scope_creep_ambiguous` are deleted, equivalent facet tags inserted.

---

## Part 2 — New theme tagging

### `customer_user_focus`

| Example | Why it qualifies |
|---------|------------------|
| EX-04 | MRR Paradox: chose user behavior (purchase rate) over a team-internal metric (MRR). Decision axis = user signal. |
| EX-07 | Relevance Dataset Bias: discovered the eval was excluding genuine user intent (only converted results). User truth vs. internal pipeline truth. |
| EX-09 | Conversational Search privacy: proxy-item design preserves the UX while removing raw-query leakage. |
| EX-09B | Privacy-cut variant of EX-09. Same admit rule applies. |
| EX-20 | Seller Risk Modeling Fairness: new sellers were users of the marketplace; the choice was made on their behalf despite team friction. |
| EX-23 | NYC C2C Policy Launch: end-user policy was the deliverable, not an internal optimization. |
| EX-24 | C2C Policy Launch (VP communication-cut): same user-facing policy. |
| EX-34 | BBE Risk Policy: seller-level vs listing-level was a fairness choice for new/small sellers. |

| Question | Why it qualifies |
|----------|------------------|
| IMP-1 | "product feature ... how did it impact users" — explicitly user impact. |
| IMP-2 | "prioritized user experience in a technical decision" — explicit. |
| IMP-15 | "advocated for responsible practices in product design" — user-facing responsibility. |

### `ethical_integrity_backbone`

| Example | Why it qualifies |
|---------|------------------|
| EX-03 | Sale NDCG Proxy: rejected the entrenched proxy metric — disagree-not-just-commit on team-favored measurement. |
| EX-04 | Educated stakeholders against MRR alarm; backbone to push back when leaders were already worried. |
| EX-07 | Challenged self-fulfilling prophecy in eval — months of team consensus that the gap "wasn't real". |
| EX-08 | Module Proliferation -> escalation to VP. Bypassing peers requires backbone with cost. |
| EX-13 | Authorship Dispute: integrity-rooted, not just interpersonal conflict. |
| EX-14 | Killed the agentic-LLM mandate from leadership using ROI math — explicit "no" to top-down direction. |
| EX-15 | Reframed conflict into a governance pattern after pushing back on the deprecation incident. |
| EX-17 | Difficult feedback to a senior IC — backbone with relational cost. |
| EX-18 | Pushed back on unreasonable scope from director — explicit disagree. |
| EX-20 | Literal ethical dilemma (the example title). Escalation. |
| EX-33 | Honest negative result on MoE — backbone to deliver what stakeholders didn't want to hear. |
| EX-34 | "Disagreeing with a Principal Researcher" + `have_backbone_disagree_and_commit` principle tag in DB. |
| BLOG-04 | "Honest Metrics Over Cosmetic Delivery" — integrity-rooted goal-tracking reform. |

| Question | Why it qualifies |
|----------|------------------|
| COM-2 | "persuade others to change direction" — backbone-flavored persuasion. |
| IMP-11 | "ethical dilemma" — explicit. |
| IMP-12 | "responsible innovation" — values-based. |
| IMP-13 | "tough ethical decision" — explicit. |
| IMP-15 | "advocated for responsible practices" — values-based. |

---

## Part 3 — New facet tagging

### `fast_learning`

| Row | Why it qualifies |
|-----|------------------|
| EX-12 (example) | Helping PhD interns transition notebook -> production stack. Admit rule = ramp-up speed in new stack/role. |
| EX-12B (example) | Team-cut: 5% -> 40% utilization via template+profile abstraction. Time-to-productivity is the central signal. |
| EX-14 (example) | Sandbox -> ROI verdict in one week, no precedent in production stack. Time-to-productivity in unfamiliar domain. |
| ADP-1 (question) | "quickly learn a new technology or skill" — explicit. |

### `scrappy_innovation`

| Row | Why it qualifies |
|-----|------------------|
| EX-06 (example) | Allocation Framework as Reusable Platform Primitive — 200M+ via reuse, not invention. |
| EX-07 (example) | Built a debiased eval framework as the answer; unorthodox vs. "improve the model". |
| EX-09 (example) | Proxy Item Breakthrough — bypassed the LLM-tokenizer mismatch with proxy items. |
| EX-09B (example) | Privacy-cut. Same proxy-item invention. |
| EX-12B (example) | Template + profile abstraction as the lever. |
| EX-14 (example) | One-week ROI math as the disqualification tool. Disproportionate impact, tiny resource. |
| EX-21 (example) | Declarative Artifactory POC built unilaterally to unblock the team. |
| OWN-9 (question) | "move fast and innovate without all the information" — admit rule explicit. |
| PS-2 (question) | "solved a problem creatively" — admit rule explicit. |
| INN-2 (question) | "project or idea you started on your own" — implies bias-for-action. |
| INN-4 (question) | "implemented an innovative solution" — explicit. |
| INN-9 (question) | "developed a creative solution to a complex problem" — explicit. |

### `strategic_scope`

| Row | Why it qualifies |
|-----|------------------|
| EX-06 (example) | 200M+ business impact across multiple feature teams (org-level). |
| EX-08 (example) | VP escalation; outcome reshaped how prod degradation was triaged. |
| EX-12B (example) | Team-wide utilization swing; the abstraction landed across the team, not one project. |
| EX-13 (example) | "Establishing Norms" for authorship across the org. |
| EX-15 (example) | "Reframing Conflict into a Governance Pattern" — governance is org-level. |
| EX-20 (example) | Escalation to leadership about marketplace-wide fairness. |
| EX-21 (example) | Platform-level POC for the artifactory system. |
| EX-23 (example) | NYC C2C Policy Launch — multi-org policy decision. |
| EX-24 (example) | VP communication on the same C2C policy. |
| EX-30 (example) | Surfaced "Domain Depth Is Not Design Authority" as a design-governance lesson. |
| EX-33 (example) | Org-level paradigm shift (pairwise -> reranking) via honest negative result. |
| EX-34 (example) | BBE Risk Policy is a marketplace-wide policy, not a single feature. |
| LDR-3 (question) | "tough call as a leader" — staff/L6 decision-making. |
| INN-7 (question) | "thinking strategically" — admit rule explicit. |
| IMP-7 (question) | "future-proofing over short-term results" — multi-quarter horizon. |
| IMP-10 (question) | "focused on long-term impact" — explicit. |

---

## Counts (expected after run)

| Quantity | Before | After |
|----------|--------|-------|
| `behavioral_themes` rows | 17 | **16** (legacy `scope_creep_ambiguous` dropped) |
| `behavioral_facets` rows | 4 | 4 (no new facets, only tag rows) |
| `example_theme_tags` rows tagged `scope_creep_ambiguous` | 7 | **0** |
| `question_theme_tags` rows tagged `scope_creep_ambiguous` | 7 | **0** |
| `example_facet_tags` rows tagged `scope_creep_pm_ambiguity` | 0 | 7 |
| `question_facet_tags` rows tagged `scope_creep_pm_ambiguity` | 0 | 7 |
| `example_theme_tags` net delta from new themes | 0 | +27 (17 examples * mean ~1.6 tags) |
| `question_theme_tags` net delta from new themes | 0 | +8 |
| `example_facet_tags` net delta from new facets | 0 | +28 (17 examples * mean ~1.6 tags) |
| `question_facet_tags` net delta from new facets | 0 | +10 |

The script's AC gate enforces only the load-bearing invariants:
`themes_total == 16` and `legacy_theme_refs_remaining == 0`. The other
counts are reported but not gated (they serve as a sanity sketch — if they
drift wildly from these numbers, the per-row dicts in the script were
edited and this doc is now stale).

---

## Idempotency / re-run behavior

| First run | Second run |
|-----------|------------|
| Inserts ~50 new tag rows, deletes 14 legacy tag rows, drops 1 theme. | All inserts print nothing (skipped); migration block prints `[SKIP] legacy theme already dropped`; AC gates re-pass with `themes_total == 16`. |

If the legacy theme has been dropped but you want to re-derive what was
migrated, query: `SELECT example_id FROM example_facet_tags WHERE
facet_id = (SELECT id FROM behavioral_facets WHERE slug =
'scope_creep_pm_ambiguity');` — that's the post-migration record.

## Revert recipe (in case of regret)

1. Restore the `.bak.<ts>_pre_bq_taxonomy_retag` snapshot:
   `cp data/mle_prep.db.bak.<ts>_pre_bq_taxonomy_retag data/mle_prep.db`
2. The legacy theme + its 14 tag rows reappear; the 7+7 facet tag rows
   inserted by Part 1 disappear; the new theme/facet tag rows from
   Parts 2/3 disappear. State is exactly as before this script ran.
3. If only Parts 2/3 are regrettable but the migration is fine, you can
   leave the backup in place and just clear the new tag tables manually:
   `DELETE FROM example_theme_tags WHERE theme_id IN (SELECT id FROM
   behavioral_themes WHERE slug IN ('customer_user_focus',
   'ethical_integrity_backbone'));` and the equivalent for facets +
   questions.
