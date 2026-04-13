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
