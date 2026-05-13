# Meta-MLSD Overhaul -- Thin Audit Summary (2026-05-13)

**Schema source of truth**: `schemas/meta_mlsd_canonical.yaml` (rule IDs below cite that file).
This document is a thin map from downstream task -> schema rules. The schema YAML is the
machine-checkable contract; this file is the human-readable orienting note.

## Scope

5 documents in the overhaul:

| Ref       | Type           | Storage                              | Status    |
|-----------|----------------|--------------------------------------|-----------|
| cd96      | cd96-playbook  | `company_documents.content` (id=96)  | exists    |
| sd41      | sd-golden      | `system_designs.*` (slug=meta-reels-golden) | exists, needs prune |
| sd42      | sd-golden      | `system_designs.*` (slug=meta-top3-comments-golden) | exists, needs reseed |
| sd-weapon | sd-golden      | `system_designs.*` (slug=meta-weapon-ads-golden)    | NEW       |
| sd-friend | sd-golden      | `system_designs.*` (slug=meta-friend-rec-golden)    | NEW       |

## Downstream task -> schema rule map

### T-P0-866 (cd96 surgery)
- DELETE `§2.2`: rule `cd96_playbook.sections[§2].delete_subsections` (`R-FORBID-per-twist-4-section-template`).
- REWRITE `§1` timing table: rule `R-TIMING-row-4tag` -- 6 columns per row, all rows must populate `rhythm` + `trade`, twist/scale may be `-`.
- KEEP `§3..§9` (homepage methodology). `§4`, `§6`, `§8` exempt from 3-rule per their `apply_3rule: false` flags.
- DRAWER: rule `R-DRAWER-cd96` -- table must link all 4 sd-golden slugs (last 2 added by T-P0-871).
- Validator pass: schema rules under `cd96_playbook`.

### T-P0-867 (sd41 prune)
- DELETE drawer header: rule `R-DRAWER-no-sd-drawer` + `R-FORBID-drawer-header-literal`.
- REWRITE `overview`: delete `R-FORBID-rhythm-philosophy` subsection ("整体节奏哲学" prose), replace with 2-paragraph solution anchor.
- TRIM `defense`: rule `R-FORBID-why-this-is-strong` removes meta-commentary; keep Strong Moment verbatim only.
- CONSOLIDATE/DELETE `verbal_outline` + `cheat_sheet`: rules `R-XPAGE-cheatsheet-no-cd96-dup` + `R-XPAGE-verbal-no-cd96-dup`.
- Each section passes section-level 3-rule (`R-3RULE-decision`, `R-3RULE-tradeoff`, `R-3RULE-scale-sla`, `R-3RULE-twist-callback`). Pass = at-least-one-bullet, NOT per-bullet.
- DIFF-DELTA SELF-CHECK: rule `R-DIFFDELTA-70pct` -- if line-count reduction >70%, halt + human review (target ~40%, ~42KB -> ~25KB).

### T-P0-868 (sd42 reseed)
- Replace sd42 content from Discord attachment "Comments Ranking (rewritten)".
- Map to canonical `sd_golden.fields`: overview / architecture / dataflow / formulas / production_constraints / tradeoffs / defense.
- NO drawer header (`R-DRAWER-no-sd-drawer`).
- Section-level 3-rule pass.
- `tradeoffs` field: `bullet_pattern_regex` + `bullet_semantic_template` ("I pick A because X, costs Y, switches to B if Z"), 6-10 bullets.

### T-P0-869 (meta-weapon-ads-golden)
- INSERT new `system_designs` row, slug=`meta-weapon-ads-golden`.
- Family: T&S classification (NOT RecSys).
- Map Phase 1/2/3 -> overview / dataflow / defense + tradeoffs.
- Key anchors: cascade calibration shared scale, OCR+CLIP+seller-graph trio, three eval-set discipline (frozen/rolling/adversarial), disagreement-aware label, hard-neg shortcut counterfactual audit.
- No drawer header. Section-level 3-rule pass.

### T-P0-870 (meta-friend-rec-golden)
- INSERT new `system_designs` row, slug=`meta-friend-rec-golden`.
- Twist: bilateral matching P(send) x P(accept) threaded through framing / label / feature / model / serving / monitoring.
- Apply `R-90S-friend-rec-section5`: compress Section 5 (model ladder + 5 retrieval channels table + serving table) to narrative rhythm. After rewrite, run "if only 90 seconds, which 3 sentences?" -- the 3 must keep MMoE multi-head bilateral, cluster-randomized A/B, NRT bilateral signal.

### T-P0-871 (cd96 link-in)
- Update cd96 drawer header table: add 2 rows (`meta-weapon-ads-golden`, `meta-friend-rec-golden`) -- rule `R-DRAWER-cd96`.
- Section 1 timing skeleton may cite 4 worked examples instead of 1.
- Update `scripts/retrofit_meta_mlsd_96_drawer_header.py` canonical drawer block.
- DEP NOTE: depends on T-P0-866 (race risk -- both write cd96).

### T-P0-872 (validator: schema + cross-page + diff-delta)
Three-part lint, NOT a single grep pass:

- **(a) Per-page schema validation** -- `scripts/audit_meta_mlsd_3rule.py` consumes `schemas/meta_mlsd_canonical.yaml`, reports section-level 3-rule failures + forbidden_patterns hits on cd96 + sd41/42 + 2 new sds.
- **(b) Cross-page consistency** -- rules `R-XPAGE-section-naming`, `R-XPAGE-sd-link-resolves`, `R-XPAGE-twist-list-matches-cd96-drawer`, `R-XPAGE-cheatsheet-no-cd96-dup`.
- **(c) Diff-delta report** -- post-hoc summary of line-count reduction from T-P0-867's sd41 prune + T-P0-868's sd42 reseed; flag >70% (`R-DIFFDELTA-70pct`).

Exit codes: 0 = clean, 1 = findings, 2 = diff-delta breach. Report path: `logs/meta_mlsd_audit_{date}.json`.

## What the schema does NOT specify

- Exact prose phrasing (intentional -- each parallel agent writes its own).
- Word-count budgets at sub-section granularity (only field-level `target_chars`).
- Heading order WITHIN a sd-golden field (only field order and presence of required semantic tags).

## HITL gate (per T-P0-865 description)

Human reviewer should confirm schema **design** before unblocking T-866..T-870 in parallel:

1. Is the 3-rule SECTION-level (not bullet-level) interpretation correct?
2. Are the 4 forbidden_patterns the right ones to flag?
3. Does the `R-TIMING-row-4tag` 6-column row match the intended cd96 §1 format?
4. Is the `R-DIFFDELTA-70pct` threshold right (target ~40%, halt at >70%)?

Once HITL signs off (and unblocks T-866..T-870 + T-871 + T-872), the 5 fresh-context
parallel agents can each pick up their task with this YAML as shared ground truth.
