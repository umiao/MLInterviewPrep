# Story Rewrite Propagation Protocol

Distilled from the EX-15 rewrite cycle on 2026-04-20. Use this protocol whenever
rewriting a behavioral example, framework node, company document, or any other
content entity that lives in the DB AND has derived fields, join-table
references, API-consumed static files, or upstream seed sources.

The protocol exists because content rewrites have a much larger blast radius
than the primary fields suggest. The first EX-15 pass updated only
`situation/task/action/result/risk_statement` and was technically "done" -- but
the card title, KEY-FACTS pills, principle tags, 10 question relevance notes,
and a frontend-consumed JSON file were all still telling the old story. Users
opening the failure_setback theme page would have seen a coherent-looking page
made of inconsistent parts.

---

## The 7 Steps

### 1. Red-flag scan BEFORE drafting

Before writing anything, name the specific failure modes in the existing
version. Concrete examples from EX-15-v1:

- Defensive opener ("I followed proper process correctly") -- reads as
  deflecting ownership
- Manager backing for VP meetings -- reads as needing cover
- Scapegoating the victims ("informal stakeholders had undocumented tests")
- Cliché lesson ("learned to communicate cross-team better")

Naming the red flags upfront prevents the rewrite from re-introducing them in
new clothing. Without this step, the polish phase has no objective scoring
function.

### 2. Draft + show, don't push

Polish in chat (or in the user's preferred review surface), send for explicit
approval before any DB write. The gate is an unambiguous green light from the
user, not their silence. For EX-15 the gate was: "我觉得很好 可以去执行".

Anti-pattern: pushing to DB during the polish loop "since we'll iterate
anyway." Every push without explicit approval consumes user trust.

### 3. Apply atomically via idempotent seed script

Per CLAUDE.md invariant 3: every DB content row must have a git-tracked
idempotent seed script as its source of truth. Mandatory script properties:

- **DB backup before any write** -- timestamped, with a descriptive suffix
  (e.g., `mle_prep.db.bak.20260420_221854_pre_ex15_rewrite`)
- **Idempotency marker** -- check whether a stable invariant of the new
  version is already present (e.g., title equals NEW_TITLE, or situation
  starts with a fixed phrase). Re-run prints `[SKIP]`, not duplicates.
- **Single transaction** for the primary entity's changes
- **Verbose diff output** so the user can see exactly what changed

### 4. Audit the propagation surface

Apply the primary fields, then STOP and audit. Five places to always check:

1. **Derived fields on same row** -- summary, elevator pitch, key-facts pills,
   tags, title, role descriptions
2. **Join tables** -- e.g. `question_example_links.relevance_note`,
   `concept_links.note`, anything that describes the entity from the
   perspective of another row
3. **API-consumed static files** -- JSON or MD files that backend endpoints
   merge into responses (in MLInterviewPrep: `docs/bq_story_arcs.json`,
   `docs/company/*/...md` files exposed via `/companies/...`)
4. **Upstream seed sources** -- canonical `seed_*.py` scripts that will
   silently undo your work on next run if not updated inline
5. **Frontend pre-renders** -- hardcoded examples in test fixtures, sample
   data files, demo modes

Practical search: `grep -r "EX-XX" --include="*.py" --include="*.json"
--include="*.md" --include="*.tsx"`. Then for each hit, read the context to
classify it (live consumer / canonical seed / historical doc).

### 5. Single propagation script + inline edits to canonical seeds

Two complementary write surfaces:

- **One propagation seed script** for all DB-side changes that don't have an
  upstream canonical seed (the change becomes one atomic git artifact)
- **Inline edits to upstream canonical seeds** for fields that already have a
  source-of-truth seed (e.g., `seed_master_pitches.py` for cn_elevator_pitch).
  Without inline edits, re-running the canonical seed silently undoes the
  rewrite.

Anti-pattern: two seed scripts that touch the same field. The most-recently-run
one wins, which is non-obvious. Always prefer "edit the canonical source".

Static historical docs (named like `*_old.md`, `*_improved_stories.md`,
`*_history.json`) -- list as known-stale in the rewrite log, but skip
auto-update unless the user asks. They're working artifacts the user iterates
on; auto-edits there create merge friction.

### 6. Verify end-to-end

Three verification gates before declaring done:

- **Idempotency re-run** -- run every script you wrote a second time. Output
  must be `[SKIP]`, never duplicate writes.
- **Read-back from DB** -- not from the script's intent, but from what's
  actually persisted. `SELECT title, cn_elevator_pitch, principle_tags FROM
  ...` and confirm the values.
- **Simulate the live API merge** -- if a JSON file feeds an endpoint that
  enriches with DB data, simulate that merge in a small Python snippet to
  confirm the frontend-visible payload is internally consistent. Catches
  drift between the JSON's frozen-in-time view and the DB's live view.

If the backend is running and the frontend is touchable, also: hard-refresh
the affected page and visually inspect.

### 7. Update meta layers (the non-obvious step)

When a story's *shape* changes, meta-layer fields trained for the old shape
become actively misleading:

- **Narration risk guards** (`<!-- NRG-vN -->` blocks): the NRG-v1 on EX-15
  warned against "process improvement tail dilutes the failure" -- valid for
  the old story. After the structural-reframe rewrite, the actual narration
  risk became "jumping to the clever ownership-transfer framework before
  establishing the failure ack." Old guard would actively misdirect the
  storyteller. **Replace, don't preserve.**
- **Principle tags**: tags like `process_improvement_from_incident` or
  `innovation` were apt for the old framing. The new framing is
  `structural_reframe`, `shared_infrastructure_governance`,
  `credibility_first`. Drop stale, add fitting.
- **Role labels in story arcs** (`role_zh`, persona summaries): the persona
  changes too -- "消防员+制度建设者" became "结构性reframer".

Rule: for every meta-layer field that semantically *labels* the story, ask
"would I assign this label to the new story from scratch?" If no, rewrite it.

---

## Anti-patterns observed

- **Trust-based skip**: "the audit step is overhead, the user only changed
  STAR fields" -- false. EX-15 had 5 surfaces beyond STAR that all told the
  old story.
- **Touch-the-easy-stuff bias**: it's tempting to update only the obviously-
  visible fields and leave hidden ones (relevance_notes on join tables) for
  later. They never get updated.
- **Forgetting upstream seeds**: writing a propagation seed without also
  editing the canonical seed means the next time someone runs the canonical
  seed (e.g., during a fresh setup or after a `data/` wipe), the rewrite
  vanishes.

## When NOT to apply the full protocol

- Tiny edits (typo, single-word swap) -- the propagation surface is unlikely
  to reference a single word
- Throwaway scratch entities -- e.g., a draft framework node not yet linked
  anywhere
- User explicitly opts out -- "just edit the field, don't audit"
