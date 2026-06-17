# /task-planning -- Enforced Task Planning Mode

Decompose work into well-specified tasks with hard enforcement against code execution.

## Usage

```
/task-planning                  # Start a planning session
/task-planning <scope>          # Plan tasks for a specific area
```

## Steps

### Step 0: Activate Plan Mode

Run immediately -- this enables the PreToolUse hook that blocks mutating tools:

```bash
python .claude/hooks/plan_mode.py activate
```

Confirm activation succeeded before proceeding. If it fails, stop and report.

### Step 1: Understand Scope

- Ask the user what area/feature needs planning (if not already specified)
- Read relevant source files to understand the current state
- Read TASKS.md to understand existing tasks and avoid duplication
- Read PROGRESS.md for recent context
- Ask clarifying questions if the scope is ambiguous

**Do NOT write any code or modify any files. Only read and discuss.**

### Step 2: Decompose into Tasks

For each task, write a full spec using this template:

```
## Summary
One-sentence description of what this task delivers.

## Context
Why this task exists. What user-facing or system problem it solves.
Reference related tasks if applicable.

## Grounding Assets
<asset-path-or-name> (ROLE/relation); ...   (see docs/workflow/grounding-assets.md)
# Roles: NORTHSTAR | CONTRACT | DEMO | DECISION-RECORD | REFERENCE
# Relations: binds (must conform, do not redefine) | requires | informs
# MANDATORY: a UX/port/match task MUST cite the locked golden/demo/mockup it
# reproduces as DEMO/binds -- that is the anti-drift lock (the executor conforms
# to the asset, never re-invents it). If the golden lives OUTSIDE this repo
# (a sibling project, an external URL), VENDOR a copy + a .sha256 manifest into
# the repo so it is a real repo-local DEMO/binds (existence-checked + diffable),
# NOT a weak REFERENCE. Every repo-resident path must resolve (plan_validate
# checks the first whitespace-delimited token); put any symbol/heading
# sub-locator AFTER a space, never `path:symbol`.

## Acceptance Criteria
- [ ] AC1: Specific, testable condition
- [ ] AC2: Include at least one full user journey AC
- [ ] AC3: For conditional behavior, specify BOTH branches (if X then Y, else Z)
- [ ] AC4: For UX tasks, include manual smoke test AC
- [ ] AC5: For a UX/port task, an AC that binds the cited DEMO ("matches <golden> with no drift")

## Technical Approach
- Implementation strategy (which files, what changes)
- Key design decisions and trade-offs
- Integration points with existing code

## Edge Cases
- What could go wrong
- Platform-specific concerns (Windows/Unix)
- Error handling requirements

## Complexity
S / M / L -- with brief justification

## Dependencies
- List task IDs this depends on, or "None"
```

### Step 3: Preview (for 5+ tasks)

If decomposition produces 5 or more tasks, present a summary table before writing:

```
| # | Title | Priority | Complexity | Dependencies |
|---|-------|----------|------------|--------------|
| 1 | ...   | P0       | M          | None         |
```

Ask the user to confirm or adjust before proceeding to Step 4.

### Step 4: Write to DB

Use `task_db.py` to create tasks. For multiple tasks, use batch mode:

```bash
python .claude/hooks/task_db.py batch --commands '[
  {"cmd": "add", "title": "...", "priority": "P0", "complexity": "M", "description": "..."},
  {"cmd": "add", "title": "...", "priority": "P1", "complexity": "S", "description": "..."}
]'
```

For single tasks:
```bash
python .claude/hooks/task_db.py add --title "..." --priority P0 --complexity M --description "..."
```

Set dependencies after creation:
```bash
python .claude/hooks/task_db.py depend T-P0-XX --on T-P0-YY
```

### Step 5: Validate

Run the plan validator to check completeness:

```bash
python .claude/hooks/plan_validate.py
```

Fix any failures (missing sections, missing regeneration) before proceeding.

### Step 6: Plan-time review (L1/L2) -- run by default

After L0 (Step 5) passes, invoke the **plan-review** skill against the tasks you
just wrote, so the user gets a refute-by-default per-task review (axis-1) plus a
human-friendly guidance brief (axis-2) **before the plan is finalized**:

```
Skill(skill="plan-review")        # reviews the freshly-written tasks
```

This is the default closing review, not an optional afterthought. Surface the
brief to the user and let them adjudicate concerns -- the machine never decides
subjective items, it only routes them (see plan-review's load-bearing wall).

**Cost (state it up front, then proceed):** axis-1 spawns a *fresh subagent per
task* (~39K tokens/task; ~280-370K tokens for an 8-task plan -- T6 measured, scales
with N). For a trivial **1-2 task** plan you MAY skip this step; for anything
larger, run it. The T6 incremental cache means a *re-planning* pass only
re-reviews tasks whose spec changed, so the full cost is paid once per new task.

**Sub-project caveat:** in sub-projects, L3 routing (writing `human_review` back
to gate/park tasks) is **inert until T-P2-321** (task_db unification) -- but L0
(validation) / L1 (review) / L2 (guidance brief) still run and deliver value. At
workspace root, all of L0-L3 are live.

### Step 7: Deactivate and deliver the debrief

```bash
python .claude/hooks/plan_mode.py deactivate
```

Then present the **debrief** -- and get this right, it is the single thing the user
actually reads. A thin "3 tasks created" summary is the recurring failure
(2026-06-17 user correction: "context每次都不够，我每次都需要纠正"). The debrief MUST:

1. **Be the improvement-ABSORBED final state.** Present the plan AS IT NOW STANDS
   after the Step 6 review + Step 8 self-pass were folded in. Do NOT narrate
   "here was the draft, here is what review found, here is the fix" -- the user
   wants the corrected plan, not the diff history. (Mention a revision only when the
   *reason* changes a decision the user must know, e.g. "migration dropped because a
   payload_json key is the precedent".)
2. **Carry the FULL planning context + detail** the user needs to hold the plan
   without re-reading the DB: per task -- what it delivers, the key design decisions
   (and any that research revised), the grounding it binds, the dependency edges, the
   complexity. Enough that the user can reason about it standalone. Err toward
   completeness over brevity here; this is the one place thinness is the bug.
3. **Separate the OPEN DECISIONS for discussion.** A distinct, clearly-labelled
   section listing every `## Open Decisions (human-gated)` item across the plan --
   each with its evidence, the concrete options, and a default recommendation -- and
   explicitly INVITE the user to decide them. These are the items only they can
   resolve; do not bury them in prose or pretend a default.

Then **STOP**. Do not begin implementation.

## Anti-patterns (DO NOT do these)

- Writing or editing source code files
- Running tests or linters
- Creating implementation files "to test the approach"
- Modifying any file outside of task_db.py operations
- Starting implementation of any planned task
- Using Write/Edit tools on any file
- Running Bash commands that modify files (mkdir, touch, cp, mv, etc.)

## Step 8 (final gate): Quality self-pass -- the LAST thing before you stop

This is the closing gate. The **structural** checklist is necessary but NOT
sufficient; the **recurring-defect bar** under it is the real gate. Apply BOTH to
EVERY task, and FIX any task that fails here before you finalize -- do not ship a
spec that needs these caught downstream by /plan-review or (worse) by the user.

> Distilled 2026-06-17 from a plan-review pass that found **18 objective tightenings
> on 3 freshly-written specs** -- every bar item below is a defect the reviewer, or
> the user, had to catch. The structural checklist alone passed those specs; the bar
> is what they failed. Grow this list whenever /plan-review surfaces a *new* class.

### Structural (each task has):
- [ ] A clear Summary a new developer could understand; Context explaining WHY, not just WHAT.
- [ ] A Grounding Assets section; a UX/port/match task binds its locked golden/demo as DEMO/binds (vendored in-repo if external), every cited path resolving.
- [ ] At least one user-journey AC (User does X -> system does Y -> user sees Z).
- [ ] Technical Approach with specific file paths; an Edge Cases section; a correct Complexity rating; Dependencies matching the implementation order.

### The recurring-defect bar (the part that actually keeps failing):
- [ ] **Grounded, not invented.** You READ the real integration points (cite file:line) and reused the EXISTING precedent. NO new column/migration/component/endpoint where a sibling pattern already provides it (e.g. a `payload_json` key vs a new ORM column + migration). If you assumed an integration surface, you VERIFIED it exists and is singular (don't spec "the X prompt" when there are two surfaces, or one that has no LLM at all). Prefer grounding the surfaces with read-only research agents BEFORE decomposing.
- [ ] **Every AC has a DETERMINISTIC oracle.** Each AC compares to an exact thing a test can check: a hash / cache-key / exact substring / exact response field. NEVER assert LLM-generated output bytes ("byte-identical derive/output") or "visibly / properly / correctly X" without a concrete observable. A manual AC names the EXACT action AND the EXACT expected string.
- [ ] **Coupling + cache-key named.** A change touching a shared computation states WHICH exact hash/key/util and WHO owns a shared helper (one definition, no dup -- per "Never duplicate utility functions"). If you change an input to a content-addressed / idempotent computation, the spec STATES how its cache-key / run_id invalidates (the silent-stale traps: folding context into a body-only content_hash; a run_id keyed on prompt-version not the user message).
- [ ] **Both branches + the no-regression anchor.** Every conditional AC states its inverse (if X then Y, ELSE Z). Every new optional input has an AC asserting that its empty/default value leaves behavior BYTE-IDENTICAL to today.
- [ ] **Subjective surfaced, never silently resolved.** Privacy / security / irreversibility / scope / intent decisions get an explicit `## Open Decisions (human-gated)` section IN the task -- options stated, evidence given, the human decides. Do NOT bake a quiet default for one.
- [ ] **Verification maps EVERY AC.** Name the test file/case per AC; a journey AC needs a wiring/integration test, not just a unit test on a helper; each listed Edge Case has a matching AC or verification line.

If /plan-review (Step 6) still surfaces an item that is on this bar, your self-pass
missed it: tighten the spec, and add the missed class to the bar so it does not
recur. The goal is that /plan-review CONFIRMS the plan rather than DISCOVERS its defects.
