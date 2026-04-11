# Human Input: Failure-Story Placeholders (historical — now resolved)

## Status: RESOLVED 2026-04-11

This file is kept for history. The three slots it reserved have all been handled:

- **EX-30** — populated with the Hash Capability Misdesign pure-failure story
  (source: `staging/充实素材_bq_story_bank_moe_allocation.md`, Version E).
  Title: `Hash Capability Misdesign - Expert Frame Blind Spot`.

- **EX-31** — **deleted** on 2026-04-11 after a coverage audit showed the
  placeholder was redundant. Every failure-ask question that had been linked
  to EX-31 (COL-1, COL-2, COM-5, ADP-19) already had at least one real
  interpersonal/feedback example linked (BLOG-01, BLOG-02, EX-13, EX-17),
  so dropping the empty slot did not reduce coverage.

- **EX-32** — **deleted** on 2026-04-11 for the same reason. The six
  originally-linked questions (OWN-11, ADP-11, ADP-13, ADP-15, EXE-6, EXE-9)
  all retained real-content examples (EX-01, EX-02, EX-05, EX-15, EX-18, EX-23,
  EX-30, BLOG-03, BLOG-04) after the placeholder was removed.

## Why the original audit over-reserved

The 2026-04-11 T-P0-351 audit counted "4 of 29 examples with genuine failure
content" (EX-05, EX-08, EX-19, EX-20) and reserved three placeholders to close
the gap. That count undercounted interpersonal-failure and execution-setback
examples already in the pool — specifically EX-02 (manager resistance),
EX-13 (authorship dispute), EX-17 (difficult feedback), EX-18 (pushback on
scope), EX-23 (tight-deadline recovery), BLOG-01 (researcher-engineer
reframe), BLOG-02 (code review standards). After populating EX-30 (Hash
Misdesign) and EX-33 (MoE -> Allocation paradigm), the coverage audit
re-ran against the full real pool and every failure-ask question routed to
at least one real example without needing the remaining placeholders.

## If you want to add more failure stories later

The source story bank (`staging/充实素材_bq_story_bank_moe_allocation.md`,
Section 8) lists three brainstorm directions for genuine new failure stories:

1. A feature/model improvement that looked good offline but lost on online A/B
   and got rolled back. Learning: an offline-online gap source.
2. A technical direction you advocated for, pushed the team onto, and later
   had to admit was the wrong direction. Learning: advocacy vs. evidence.
3. A cross-team collaboration failure driven by underestimating stakeholder
   complexity. Learning: stakeholder mapping.

If you mine one of these, create a fresh `EX-34` / `EX-35` row rather than
resurrecting the deleted `EX-31` / `EX-32` slots. The sequential-ID convention
stays clean that way.

## Coverage snapshot after resolution (2026-04-11)

All 15 failure-ask questions have at least one real-content example linked:

| Q | real examples linked |
|---|---|
| OWN-1  | EX-08, EX-15, EX-30 |
| OWN-8  | EX-05, EX-15, EX-30 |
| OWN-11 | EX-01, EX-02, EX-05, BLOG-03, BLOG-04 |
| COL-1  | BLOG-01, EX-13 |
| COL-2  | BLOG-02 |
| COM-5  | EX-17 |
| ADP-5  | EX-05, EX-15, EX-16, EX-30 |
| ADP-11 | EX-15 |
| ADP-13 | EX-08, EX-15 |
| ADP-15 | EX-05, EX-16, EX-30 |
| ADP-18 | EX-17, EX-30 |
| ADP-19 | EX-17 |
| EXE-2  | EX-09, EX-30 |
| EXE-6  | EX-18, EX-23 |
| EXE-9  | EX-23 |

Five of these (COL-2, COM-5, ADP-11, ADP-19, EXE-9) still have only a single
link after the placeholder removal. That is a minor rotation-risk follow-up
for a future task, not a blocker — every question still reaches real content
on the first click.
