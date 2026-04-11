# Human Input: Failure-Story Placeholders (EX-30 / EX-31 / EX-32)

## Why these slots exist

A behavioral-content audit on 2026-04-11 found that only 4 of 29 behavioral
examples (EX-05, EX-08, EX-19, EX-20) contain genuine failure-and-learning
content. All 15 failure-ask questions currently route into that same tiny pool,
so a two-failure-question interview round forces the same story to be reused.

To prevent that, three placeholder slots (EX-30, EX-31, EX-32) have been
reserved in the database. They are tagged `principle_tags=failure,learning,
needs_input`, display a distinct `[Needs Input]` badge in the UI, and render
every empty STAR field as `(missing -- pending user input)`. The titles are
prefixed with `[NEEDS-INPUT]` so they are easy to grep and easy for the user
to spot.

**No invented stories.** This file only contains prompts -- the user fills the
real content.

## Before you start

Pick three *distinct* failures from your real career -- one per theme. Do not
double up (e.g. two technical miscalls), and do not recycle EX-05/08/19/20.
If you catch yourself reaching for an existing example, you are about to
waste a slot.

Estimated effort: **20--30 minutes per slot** (60--90 min total), assuming you
already know roughly which stories you want to tell.

STAR word-count targets (used by the existing 4 real failure examples as a
reference):

- Situation: ~80-120 words
- Task: ~50-80 words
- Action: ~150-250 words (this is where depth lives)
- Result: ~80-150 words (include the lesson + what you now do differently)

## Slot specs

### EX-30 -- Technical miscall

Theme: wrong architecture, premature optimization, over-engineering, wrong
abstraction, or a technical bet that didn't pay off.

Routed questions (user answers via this slot):
OWN-1, OWN-8, ADP-5, ADP-18, EXE-2.

Prompts -- answer each in plain prose, then merge into STAR:

1. **What went wrong technically?**
   What was the technical decision? What signal(s) should have warned you?
   Why did the alternative not get chosen?
2. **What was the concrete damage?**
   Hours/weeks wasted, rework cost, downstream teams blocked, SLO breach,
   compute cost, data quality regression -- be specific with numbers.
3. **What did you do once you noticed?**
   Detection moment -> mitigation -> rollback or rebuild -> stakeholder
   comms -- chronological.
4. **What did you learn?**
   One *general* principle you now apply (not "I'll be more careful").
5. **What would you do differently next time?**
   A concrete checklist item or review step, not a sentiment.

STAR reminder: Situation = context + tech stack, Task = what you owned,
Action = YOUR decisions (use "I", not "we"), Result = metric + lesson.

### EX-31 -- Interpersonal failure

Theme: mishandled peer conflict, lost trust with a collaborator, botched
feedback (giving or receiving), damaged a cross-team relationship, or
mismanaged a disagreement.

Routed questions:
COL-1, COL-2, COM-5, ADP-19.

Prompts:

1. **What happened between you and the other person?**
   Who was involved, what was the triggering interaction, what was each
   party's position?
2. **What did you do that made it worse (or fail to do that would have
   helped)?**
   This is the hard part. Be honest -- an interpersonal failure story with
   no first-person fault is a story about someone else.
3. **How did you repair it (or fail to)?**
   Exact conversation, who initiated, what was said, what changed.
4. **What did you learn about yourself?**
   E.g. "I over-index on being right over being heard," "I avoid conflict
   until it compounds," etc.
5. **What would you do differently next time?**
   A concrete first-move you now make in similar situations.

STAR reminder: Situation = relationship + context, Task = your role in the
collaboration, Action = how you engaged (or didn't), Result = state of the
relationship now + durable lesson.

### EX-32 -- Execution / delivery miss

Theme: missed deadline with customer impact, shipped a regression, placed
the wrong project bet, mis-scoped a commitment, or dropped a ball on a
cross-team dependency.

Routed questions:
OWN-11, ADP-11, ADP-13, ADP-15, EXE-6, EXE-9.

Prompts:

1. **What was the commitment and who was counting on it?**
   Ship date, audience (internal/customer), dependency chain.
2. **Where did it go off the rails?**
   Scope creep, underestimated work, a hidden blocker, a wrong planning
   assumption -- diagnose the root cause, not the symptom.
3. **What did you do when you realized the miss was coming?**
   Early warning given? Re-scoping? Overtime? Cutting features?
4. **What was the actual impact?**
   Days slipped, features dropped, customer complaints, trust damage --
   with specifics.
5. **What did you change in how you plan / commit / escalate now?**
   A durable process change, not "I work harder now."

STAR reminder: Situation = project + stakes, Task = your accountability,
Action = decisions you made under delivery pressure, Result = outcome +
the concrete change you made to your working model.

## Filling the slots

When you are ready to fill a slot:

```bash
cd MLInterviewPrep
python .claude/hooks/task_db.py add ... # not needed -- direct DB edit
# Use: python scripts/_fill_failure_placeholder.py EX-30 path/to/draft.md
# (or edit via the frontend once the CRUD form lands)
```

(The `_fill_failure_placeholder.py` helper is NOT part of T-P0-351 -- this
task only seeds the slots + frontend fallback. A follow-up task can add the
fill helper if the user wants it.)

Remember to remove the `[NEEDS-INPUT] ` prefix from the title when you fill
a slot -- that is what tells the UI to drop the amber `Needs Input` badge.
