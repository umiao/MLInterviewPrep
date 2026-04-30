# Pinterest VO Misdirected-Write Root Cause Memo

**Task**: T-P0-661 -- WHY did Claude default to `company_documents.content` instead of `interview_events` when the user said "update Pinterest onsite schedule"?
**Authored**: 2026-04-30 by autonomous T-P0-661 inner session
**Status**: AWAITING USER REVIEW -- do not auto-advance

---

## TL;DR

The bug was NOT a name collision (no lexical "which dashboard?" ambiguity exists in the codebase). It was a **mention-density + recency-priming** bias: when the user request was ambiguous about *which surface* to write to, Claude routed to the surface that was most discoverable in shared context (CLAUDE.md + docs + scripts/) and most recently edited (the prior turn was a prose-edit on `company_documents.id=84`). The "fix" is structural -- inject a `widget -> source-table` mapping into CLAUDE.md so the priors are inverted, AND extend the lint hook (T-P0-660) to flag prose-writes that LOOK like schedule data. Both, not either.

---

## (i) Session priming path -- literal turn-by-turn surface chain

Reconstructed from `git log --oneline` + `PROGRESS.md` lines 355--470 (transcripts not retained on disk):

| Turn | Task | Surface edited | Pattern |
|---|---|---|---|
| T-1 | T-P0-628 (2026-04-25) | `company_documents.id=84` audit | prose-on-doc |
| T-2 | T-P0-629 (2026-04-26) | `company_documents.id=84` content (Uber ML Coding golden, 411cf8c) | prose-on-doc |
| T-3 | T-P0-630 (2026-04-27) | `company_documents.id=85` content (Uber ML SD golden, 0b3d4ea) | prose-on-doc |
| T-4 | T-P0-632 (2026-04-28) | `company_documents.id=37` content (Uber VO multi-charter index, 6f38ff4) | prose-on-doc |
| T-5 | T-P1-635 (2026-04-28) | `company_documents` Uber companions (8cf02bb) | prose-on-doc |
| T-6 | T-P1-650 (2026-04-29 23:35) | `company_documents.id=84` content + `problems` row 1097 (Uber n-gram) | prose-on-doc + new prob row |
| **T-7** | **T-P0-651 (2026-04-30 01:55)** | **`company_documents.id=83` content + `companies.id=29.interview_stages`** | **MISDIRECTED -- Dashboard reads `interview_events` not these** |

**Mechanical fact**: 6 of the last 6 "update X for company Y" tasks landed on `company_documents.content`. T-7 inherited the template literally. The model never reached for `interview_events` because there was no recent precedent in working memory and no mapping prior in CLAUDE.md.

**Compounding miss**: T-P1-650 ALSO violated Invariant-3 by writing through `scripts/migrations/add_uber_prob_nextword.py` (raw SQL). T-P0-651 then used `scripts/migrations/update_pinterest_onsite_itinerary.py` -- same pattern. The migration-script anti-pattern was primed in the same chain.

---

## (ii) Discoverability comparison -- raw mention counts

Pure `rg -c` counts. "Mention density" = raw count / file-line count where applicable.

| Surface | CLAUDE.md (264L) | ../CLAUDE.md (162L) | shared/claude_md_shared.md (205L) | src/ | scripts/ | docs/ | tests/ | **TOTAL** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `company_documents` | 1 | 0 | 0 | 17 (3 files) | 393 (107 files) | 45 (13 files) | 15 (5 files) | **471** |
| `interview_events` | 0 | 0 | 0 | 10 (4 files) | 61 (22 files) | 1 (1 file) | 17 (1 file) | **89** |
| **Ratio (cd : ie)** | -- | -- | -- | 1.7x | **6.4x** | **45x** | 0.9x | **5.3x** |

**Key inequalities**:
- In CLAUDE.md (the file Claude reads first): `company_documents` = 1 mention (Invariant-3 example), `interview_events` = 0 mentions. Pure absence.
- In `docs/`: `company_documents` = 45 vs `interview_events` = 1. **45x bias** in the surface most likely to be opened during research.
- In `scripts/`: 6.4x bias toward `company_documents`. Every recent prep seed (`seed_pinterest_*`, `seed_uber_*`, `seed_doordash_*`, `seed_meta_oa_*`) writes to `company_documents`. Only ~22 special-purpose `_add_*` and `seed_*_companies_row.py` files touch `interview_events`.
- The ONLY surface where `interview_events` wins is `tests/` (one focused file `test_timeline.py` with 17 mentions vs `company_documents` spread across 5 generic content tests). This is exactly the surface Claude does NOT search first when given a content-shaped request.

**Falsification implication**: if mention density really drives routing, T-P0-661's recommended fix must move at least the CLAUDE.md and docs/ ratios. Adding a widget mapping table that names `interview_events` 5+ times in CLAUDE.md and `docs/protocol/dashboard_surface_map.md` 20+ times would invert the priors at the surface Claude reads first.

---

## (iii) Falsifiable root-cause hypothesis

> **H1 (Recency-Weighted Mention-Density Routing)**: When a user request is ambiguous about which DB surface to write to, Claude routes to the surface S\* that maximizes `recency_weight(last_edit_of_S) * log(mention_count_in_priors(S))`, where priors = CLAUDE.md + last-N PROGRESS entries + docs/ + scripts/. The model does NOT walk the UI -> API -> table chain unless that chain is named in the priors.

**Why this fits the data**:
- mention_count_in_priors(`company_documents`) >> mention_count_in_priors(`interview_events`): 471 to 89 raw, with the imbalance worst in CLAUDE.md (1 to 0) and docs/ (45 to 1) which dominate the prior.
- recency_weight at T-7 was MAXIMAL for `company_documents.content` (T-1 through T-6 were all prose-on-doc).
- The user's word "dashboard" is NOT in either prior -- it has 8 file mentions in src/ but 0 in CLAUDE.md and 0 mentions of "dashboard widget reads X" anywhere. The model had no anchor to walk Dashboard.tsx -> InterviewTimeline -> /api/timeline/events -> interview_events table.

**Falsification test** (concrete, runnable):
1. Insert into CLAUDE.md a "Surface Identification" table with rows `Dashboard.InterviewTimeline -> interview_events`, `Dashboard.UpcomingTasks -> tasks`, `KG.NodeDetail -> framework_nodes`, `CompanyDrawer.Notes -> company_documents.content`. Bring `interview_events` mention count in CLAUDE.md from 0 to >=5.
2. On a fresh session with no prior context, give the prompt: *"Update Pinterest onsite schedule -- the user just confirmed dates for May 5-6."*
3. Observe first action. **Hypothesis predicts**: first grep is now for `interview_events`, first edit targets `_add_pinterest_*.py` (or equivalent seed_*.py), NOT `company_documents.content`.
4. **Falsification**: if the first grep STILL targets `company_documents` after the table is in CLAUDE.md, H1 is wrong (or the prior is being overridden by something else -- conversational priming alone, the user word "schedule" lacking surface anchoring, etc.).

H1 is preferred over alternatives:
- H0 (random / no bias): falsified -- 6/6 prior turns landed on the same surface.
- H2 ("Claude searches by company name first"): would predict random routing among `companies.*`, `company_documents`, `interview_events` (all keyed by company_id). Doesn't explain the 6/6 streak on `company_documents` specifically.
- H3 ("dashboard" is lexically ambiguous): falsified by Q3 -- only one `/dashboard` route, one `Dashboard.tsx`, no shadowed components.

---

## (iv) Generalization claim -- 2+ other surface pairs at risk

H1 predicts the same bug class on these pairs in this codebase:

1. **`framework_nodes.description` (KG node prose) vs `framework_nodes.problems[]` (canonical KG-LC link table)**. Request shape: *"add LeetCode X to KG node Y."* Mention density skew: `framework_nodes.description` is grep-rich in `seed_node_*.py` and protocol docs; the join table `framework_node_problems` is rarely named outside `models/framework.py`. H1 predicts Claude will append a prose mention of LC X into the description field instead of inserting the join row -- which renders the problem in the description text but NOT in the KG NodeDetail's "Related LC" panel.

2. **`problems.notes` (per-problem study text) vs `company_documents.content` sections referencing the problem**. Request shape: *"add a code sketch for LC X for company Y."* Both surfaces accept code blocks; both are queried by company tag. H1 predicts Claude will write to whichever was most-recently edited in session (recency-priming), and given the 6:1 mention density imbalance in scripts/ favoring `company_documents`, default routing will be the doc -- even when the problem already has a `problems.notes` field with a sketch and the user wanted that updated.

3. (Bonus) **`companies.cheat_sheet` (new column, T-P1-641, March 2026) vs `company_documents.content` cheat-sheet sections**. Mention density: cheat_sheet column = ~3 mentions in code; cheat-sheet prose sections in `company_documents.content` = dozens. H1 predicts that when the user says *"refresh the Pinterest cheat sheet,"* Claude will edit the prose section, not the new structured column -- recreating exactly the T-P0-651 class of bug, on a different table pair.

These predictions are testable on held-out ambiguous prompts.

---

## Concrete recommendation (priority-ordered)

**(c) BOTH (a) AND (b), not either alone.**

- **(a) Add `Widget -> Source Table` mapping to CLAUDE.md** -- highest leverage on the prior. Without this, every future "update X for Y" ambiguity re-rolls the same dice. Should live in MLInterviewPrep/CLAUDE.md (project-specific) under a new "## Surface Identification" section that names at minimum: Dashboard.InterviewTimeline, Dashboard.UpcomingTasks, Dashboard.ActivityChart, KG.NodeDetail, CompanyDrawer, PrepBoard. **This addresses the prior** -- inverts the mention density skew at the file Claude reads first.

- **(b) Extend T-P0-660 lint hook to flag prose-shaped schedule writes**: when a write to `company_documents.content` includes patterns matching ISO-8601 timestamps + interviewer-name prose ("R1 ML SD with X"), block with a redirect message to `interview_events`. This addresses the **failure mode** even if the prior fails -- belt-and-suspenders for the case where conversational priming overrides the CLAUDE.md table. **Without (a)**, lint hook only catches *this* surface mismatch; without (b), CLAUDE.md text is documentation that future sessions can ignore (the original reviewer critique of T-P1-656).

- **(c) DO NOT ALSO**: add a behavioral rule like "always check the widget map before editing." This is the kind of advisory-only conclusion AC5 explicitly rejects -- it has zero leverage when context-window is tight or the model is primed by the prior turn. Structural fixes (table in CLAUDE.md, lint hook) make the failure mode hard to repeat; behavioral rules make it slightly less likely.

These recommendations feed directly into:
- **T-P1-656** (skill design): skill's body should reference the CLAUDE.md "Surface Identification" table as single source of truth, not duplicate it.
- **T-P0-660 v2** (already shipped, may need extension): consider adding a "schedule-shaped prose detector" pass that flags ISO-8601 + interviewer-name pairs in `company_documents.content` writes.

---

## Audit trail

- Q1 finding: 0 widget->table mapping tables exist in CLAUDE.md, ../CLAUDE.md, or shared/claude_md_shared.md. `interview_events` count = 0 in all three. `company_documents` count = 1 (Invariant-3 example only).
- Q2 finding: 6/6 prior "update X for company Y" turns edited `company_documents.content`. The 7th (T-P0-651) inherited the template. Confirmed via `git log --oneline` + PROGRESS.md lines 355--420.
- Q3 finding: ZERO lexical ambiguity on "Dashboard" in the codebase. Single route, single component, single API namespace `/dashboard/*`. The bug was NOT word-sense.
- Q4 finding: aggregate `company_documents : interview_events` mention ratio = 5.3x; in CLAUDE.md+docs/ specifically (the strongest priors) = effectively infinite (1+45 vs 0+1).

End of memo.
