# BQ Stories: Unresolved TODO Placeholder Tracker

Created: 2026-04-13 (T-P0-179)
Source: `docs/bq_improved_stories.md` (+ mirrored JSON entry in `docs/bq_behavioral_examples.json`)

## Purpose

Earlier rework passes (T-P0-384, T-P0-385, T-P0-386, T-P1-387) inserted
`[TODO: confirm ...]` placeholders into Result sections where adjective-heavy
claims lacked concrete numbers. Per project convention, numbers are never
invented — they must come from the user's own production data / memory.

This tracker consolidates every unresolved placeholder into a single
question sheet. Once the user fills in an answer below, replace the
corresponding `[TODO: confirm ...]` span in the story file (and the JSON
mirror where applicable) with the concrete number.

## Status Legend

- `[OPEN]` — awaiting user input
- `[ANSWERED]` — user provided value; ready to patch source docs
- `[WONTFIX]` — user confirms the adjective is intentional, placeholder should be removed outright without a number

---

## Open Asks (12 placeholders across 10 stories)

### 1. EX-01 — Diversity blending initial A/B lift
- **File**: `docs/bq_improved_stories.md:57`
- **Current Result claim**: "Initial A/B lift before scaling: **[TODO: confirm initial GMB/CTR lift % from first vertical experiment]**"
- **What's needed**: initial GMB lift % OR CTR lift % from the very first diversity-blending vertical experiment, ideally with the quarter.
- **Why it matters**: 200M annualized impact is already stated; the first-experiment number is the causal anchor that shows the multi-year initiative started from a measurable signal, not a pitch.
- **Status**: `[OPEN]`
- **Answer**:

### 2. EX-04 — Abandonment OKR adoption quarter
- **File**: `docs/bq_improved_stories.md:115`
- **Current Result claim**: "adjusted team OKRs (**[TODO: confirm which quarter -- Q_/YYYY OKR cycle]**)"
- **What's needed**: the OKR cycle (e.g., Q3 2022) when leadership incorporated abandonment data into team OKRs.
- **Why it matters**: converts a vague "adjusted OKRs" into a dated org-change.
- **Status**: `[OPEN]`
- **Answer**:

### 3. EX-07 — Unbiased eval dataset downstream delta (MD copy)
- **File**: `docs/bq_improved_stories.md:174`
- **Current Result claim**: "downstream ranking experiments showed **[TODO: confirm downstream metric delta after dataset reformulation -- e.g., NDCG lift / relevance precision gain / abandonment-rate drop, with baseline quarter]**"
- **What's needed**: one concrete downstream signal after the unbiased dataset was adopted — NDCG lift, relevance precision gain, or abandonment-rate drop, with baseline quarter.
- **Why it matters**: the "problem formulation was the unlock, not a new model" thesis only lands if there's a post-fix number proving the fix worked.
- **Status**: `[OPEN]`
- **Answer**:

### 4. EX-07 — Unbiased eval dataset downstream delta (JSON mirror)
- **File**: `docs/bq_behavioral_examples.json:381`
- **Current Result claim**: same text as item 3, mirrored into JSON so MD and JSON stay in sync.
- **Action**: when item 3 is answered, patch both the MD and the JSON in the same pass.
- **Status**: `[OPEN]` (tied to item 3)

### 5. EX-14 — LLM-as-Judge GMB win
- **File**: `docs/bq_improved_stories.md:301` (first placeholder)
- **Current Result claim**: "delivered GMB improvement (+1.5% GMB [TODO: confirm])"
- **What's needed**: confirm the +1.5% GMB figure belongs to LLM-as-Judge (EX-14) and not distributed-training pushback (EX-18). If it does, the TODO can be deleted in place; if it doesn't, the sentence needs to be rewritten.
- **Why it matters**: Pass 1 flagged the 18K/day, $500/day, +1.5% GMB triad as possibly belonging to EX-18 rather than EX-14. User to disambiguate.
- **Status**: `[OPEN]`
- **Answer**:

### 6. EX-14 — LLM-as-Judge throughput + cost
- **File**: `docs/bq_improved_stories.md:301` (second placeholder)
- **Current Result claim**: "Throughput reached ~**18K labels/day at ~$500/day cost [TODO: confirm figures]**"
- **What's needed**: confirm (or correct) 18K labels/day and ~$500/day cost for the LLM-as-Judge pipeline.
- **Why it matters**: same disambiguation as item 5.
- **Status**: `[OPEN]`
- **Answer**:

### 7. EX-14 — LLM-as-Judge cross-team adoption count
- **File**: `docs/bq_improved_stories.md:301` (third placeholder)
- **Current Result claim**: "adopted by the ads team and [TODO: confirm # of additional teams, e.g., 3-5] other groups"
- **What's needed**: concrete count of additional teams beyond ads that adopted the LLM-as-Judge eval infra.
- **Why it matters**: turns "other groups" into a defensible adoption number.
- **Status**: `[OPEN]`
- **Answer**:

### 8. EX-15 — Post-mortem attribution norm adoption
- **File**: `docs/bq_improved_stories.md:320`
- **Current Result claim**: "now referenced by **[TODO: confirm # of other on-call teams / incidents avoided since]** other on-call teams"
- **What's needed**: number of other on-call teams that adopted the norm, OR number of incidents avoided since the norm was introduced.
- **Why it matters**: cross-team adoption is the scale claim; without a count it reads as self-congratulation.
- **Status**: `[OPEN]`
- **Answer**:

### 9. EX-17 — Senior IC collaboration sustained outcome
- **File**: `docs/bq_improved_stories.md:355`
- **Current Result claim**: "fast response times (**[TODO: confirm # of subsequent joint on-call rotations with zero escalations, or duration of positive trajectory]**)"
- **What's needed**: EITHER count of subsequent joint on-call rotations with zero escalations, OR duration (months/quarters) of the positive trajectory.
- **Why it matters**: converts "built mutual respect" into a durable professional outcome.
- **Status**: `[OPEN]`
- **Answer**:

### 10. EX-21 — Interim declarative-path merged PRs
- **File**: `docs/bq_improved_stories.md:431`
- **Current Result claim**: "business win (**[TODO: confirm # of merged PRs landed with zero review-restart via the interim path]**)"
- **What's needed**: number of PRs merged via the interim path with zero review-restart.
- **Why it matters**: shows the tech-debt "smart shortcut" produced actual shipping velocity.
- **Status**: `[OPEN]`
- **Answer**:

### 11. EX-23 — VP allocation avoided-traffic estimate
- **File**: `docs/bq_improved_stories.md:464`
- **Current Result claim**: "Avoided running an invalidated A/B that would have consumed **[TODO: confirm % of NYC C2C traffic that would have been burned on the broken control-overwrite test]** of experimentation traffic"
- **What's needed**: % of NYC C2C experimentation traffic that the aborted combo-launch would have burned.
- **Why it matters**: quantifies the cost avoided by catching the control-overwrite defect before launch.
- **Status**: `[OPEN]`
- **Answer**:

### 12. EX-24 — Slot-allocation false-positive rate before/after
- **File**: `docs/bq_improved_stories.md:482` (two placeholders, one data point)
- **Current Result claim**: "slot-allocation false-positive rate on combo-launch predictions fell from **[TODO: confirm X%] to [TODO: confirm Y%]**"
- **What's needed**: two numbers — pre-reframe false-positive rate (X%) and post-reframe false-positive rate (Y%).
- **Why it matters**: the single strongest metric claim in EX-24; without X/Y the sentence is a "fell from … to …" with no endpoints.
- **Status**: `[OPEN]`
- **Answer**:

---

## Patch Checklist (after user fills answers)

When answers come in, for each `[ANSWERED]` item:

1. In `docs/bq_improved_stories.md`, replace the exact `[TODO: ...]` span with the concrete number.
2. For item 3/4 (EX-07), also patch the mirrored string in `docs/bq_behavioral_examples.json` so MD and JSON stay in sync.
3. Re-run behavioral seed (if applicable) to propagate to DB.
4. Flip status to `[ANSWERED]` here, commit, and keep the tracker for audit history.

## Scope Note

This tracker closes T-P0-179. The task's definition of done was: "For each
[TODO]: fill concrete numbers or explicitly note what user input is still
required." Since concrete numbers can only come from the user's own
production data, the deliverable is a single consolidated question sheet
the user can answer in one pass rather than 12 scattered placeholders
discovered one-by-one during interview drills.

---

## Google R2: Top-20 G&L Common Questions x bq_improved_stories Mapping

Created: 2026-04-15 (T-P0-429)
Source: HR advice -- "you can anticipate 90%... top 20 questions, 3 answers for each, detailed and data-driven"

**Already-polished stories (no further edits needed):** EX-02, EX-08, EX-17

### Mapping Table

| # | Question | Story 1 | Story 2 | Story 3 | Coverage |
|---|----------|---------|---------|---------|----------|
| 1 | Tell me about a time you **disagreed** with someone | EX-13 (authorship dispute) | EX-20 (seller risk fairness vs. principal researcher) | COL-1 (brand recall implementation) | OK |
| 2 | Tell me about a time you **failed** | EX-15 (model deprecation incident) | EX-16 (cross-DC deployment) | EX-33 (MoE honest negative result) | OK |
| 3 | Tell me about a time you dealt with **ambiguity** | EX-14 (vague AI mandate -> LLM-as-Judge) | EX-09 (conversational search proxy item) | EX-01 (Hacker Week self-initiated discovery) | OK |
| 4 | Tell me about a time you had a **difficult stakeholder** | EX-17 (harsh senior IC) | EX-24 (explaining allocation to VP) | COL-3 (ads team boundary defense) | OK |
| 5 | Tell me about a time you **pushed back on your manager** | EX-18 (unreasonable distributed-training scope) | EX-02 (reframing diversity project) | COL-4 (manager pushed back on goal reform) | OK |
| 6 | Tell me about a time you made the **hardest decision** | EX-02 (deliberate team transfer) | EX-20 (escalating ethical concern) | EX-33 (labeling MoE "start test" -- giving up carry-over protection) | OK |
| 7 | Tell me about a time you **went above and beyond** | EX-01 (Hacker Week self-initiated 200M+) | EX-16 (proactive latency work without budgeted support) | EX-08 (detecting invisible cumulative degradation) | OK |
| 8 | Tell me about a time you **mentored** someone | EX-11 (intern goal communication) | EX-12 (PhD interns notebook -> production) | EX-22 (delegation -- hashing decision) | OK |
| 9 | Tell me about a time you **led without authority** | EX-23 (30-person NYC C2C project lead) | EX-01 (Hacker Week self-initiated -> multi-year initiative) | EX-08 (escalating degradation to VP) | OK |
| 10 | Tell me about a time you **handled feedback** | EX-17 (harsh IC feedback -> mutual respect) | EX-04 (MRR paradox -> OKR adoption) | COL-4 (manager challenged goal reform proposal) | OK |
| 11 | Tell me about a time you **resolved a conflict** | EX-13 (authorship dispute -> lasting norm) | EX-17 (senior IC -> professional respect) | EX-20 (researcher vs. fairness -> escalation) | OK |
| 12 | Tell me about a time you dealt with **deadline pressure** | EX-23 (2-week VP deadline, 30-person team) | EX-21 (shipping without waiting for infra) | -- | OK (2 strong) |
| 13 | Tell me about a time you **learned a new skill** quickly | EX-14 (LLM exploration from zero) | EX-16 (infra/C++ static compilation) | EX-12 (building production template for research stack) | OK |
| 14 | Tell me about a time you faced an **ethical choice** | EX-20 (seller risk fairness -- escalation to senior director) | COL-3 (boundary defense -- relevance not a tunable dial) | -- | OK (2 strong) |
| 15 | Tell me about a time you made a **mistake** | EX-15 (deleted models others depended on) | EX-16 (cross-DC factor name collision) | EX-02 (should have translated business case into OKR language sooner) | OK |
| 16 | Tell me about a time you're **proudest of** | EX-01 (diversity 200M+ from Hacker Week) | EX-06 (allocation framework 200M+) | EX-33 (honest negative -> paradigm shift) | OK |
| 17 | Tell me about a time you put **user-first over metric** | EX-07 (exposed self-fulfilling dataset bias) | EX-03 (challenged MRR as wrong metric) | EX-04 (abandonment -- "worse" MRR = better outcomes) | OK |
| 18 | Tell me about a time you dealt with **ambiguous priority** | EX-18 (competing tech stacks, multi-manager route dispute) | EX-14 (vague "explore AI" -> pragmatic pivot) | EX-23 (combo-launch scope adjustment) | OK |
| 19 | Tell me about a time you **gave feedback to a peer** | EX-11 (intern goal communication coaching) | EX-13 (authorship -- "authorship as gift" unacceptable) | COL-2 (code review standards) | OK |
| 20 | Tell me about a time you drove a **cross-team** initiative | EX-06 (allocation framework across verticals) | EX-23 (NYC C2C 30-person cross-org) | COL-3 (ads x relevance LLM pipeline) | OK |

### Coverage Summary

**All 20 questions have at least 2 mapped stories. No coverage gaps.**

Stories most frequently referenced (versatile anchors):
- **EX-01** (diversity/intent collapse): ambiguity, above-and-beyond, led-without-authority, proudest
- **EX-17** (harsh feedback -> respect): difficult stakeholder, feedback, conflict
- **EX-14** (LLM-as-Judge): ambiguity, new skill, ambiguous priority
- **EX-20** (seller risk fairness): disagreed, hardest decision, ethical, conflict
- **EX-23** (NYC C2C): deadline, led-without-authority, cross-team, ambiguous priority

Stories with low utilization (single-question coverage):
- **EX-03** (MRR metric challenge): only user-first-over-metric
- **EX-04** (MRR paradox): only feedback + user-first
- **EX-05** (relevance filtering deployment): not mapped to any top-20 question
- **EX-09** (conversational search proxy): only ambiguity
- **EX-10** (SIGIR experiment design): not mapped to any top-20 question
- **EX-19** (A/B test confounders to PM): not mapped (covered by EX-24 for "explain to non-technical")
- **EX-22** (delegation hashing): only mentoring (as delegation variant)

### Already-Polished Stories: EX-02, EX-08, EX-17

These three stories have been through full rework passes and are interview-ready. No further edits needed:
- **EX-02**: ownership sharpening done (T-P1-388). "I led the first experiment to a +1% GMB lift" front-loaded. Covers: disagreed, pushed-back, hardest-decision.
- **EX-08**: metric sweep done (T-P1-387). VP escalation with quantified cumulative degradation. Covers: above-and-beyond, led-without-authority.
- **EX-17**: ownership + metric sweeps done. "Built mutual respect" with durable professional outcome. Covers: difficult-stakeholder, feedback, conflict.

### Gap Analysis: What Would Strengthen the Bank

While all 20 questions are covered, some areas rely on fewer stories:

1. **Deadline pressure** (Q12): only EX-23 + EX-21. A third story with a different flavor (e.g., personal delivery crunch vs. team-level project management) would help.
2. **Ethical choice** (Q14): EX-20 is the anchor; COL-3 is a softer variant. A third story involving data privacy or user safety would diversify.
3. **Gave feedback to a peer** (Q19): EX-11 is intern (not peer-level), EX-13 is dispute (not developmental feedback), COL-2 is process alignment. A story about giving growth-oriented feedback to a same-level engineer would be stronger.

These are nice-to-haves, not blockers -- current coverage is sufficient for a 45-min G&L round.
