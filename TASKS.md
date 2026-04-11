# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-355: Frontend: DrawerLayout single-source-of-truth responsive two-column refactor for drawer family
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: # Frontend: DrawerLayout single-source-of-truth responsive two-column refactor

## Context
SlideOverPanel.tsx:18 defaults to max-w-xl (576px). BehavioralQuestions.tsx:677 invokes
it without a width prop, so the behavioral-example drawer is stuck at 576px on all
monitors. On 1920px: ~30% viewport utilization; on 2560px: ~23%. User reports content
"compressed into a small strip on the right" on wide screens.

**Design constraint**: prose readability caps at ~75ch (~720px at 15px font). Naive
"stretch drawer wider" produces unreadable walls of text. Correct fix is a two-column
layout that spends extra pixels on metadata context, not on fatter prose.

**Scope expansion (user-confirmed 2026-04-11)**: apply uniformly to the drawer family.
Build a single DrawerLayout component as the source of truth; migrate SlideOverPanel's
behavioral-example drawer AND PrepNotesModal AND any other long-form drawer found via
grep audit. Future drawer styling changes then happen in exactly one place.

## Design spec

### Drawer container width breakpoints
- base: max-w-xl (576px)
- md: max-w-2xl (672px)
- lg: max-w-4xl (896px)
- xl: max-w-5xl (1024px)
- 2xl: max-w-6xl (1152px)

### DrawerLayout internal layout (new component)
- Props: {left: ReactNode, right: ReactNode, variant?: 'two-column' | 'single-column', leftWidth?: string}
- Default variant: two-column on >=lg, single-column below
- Two-column: flex row, left pane sticky top-0 w-72 (288px), right pane flex-1 with inner `max-w-[680px]` prose cap
- Single-column: stacked, left content first, then right content
- Opt-out: pass variant='single-column' to force single layout (for short-form drawers where two-column looks silly)

### Left pane contents
- Behavioral example: question_id badge, category pill, theme pills, source_project, linked-question quick-jump list, prev/next example nav
- Prep notes: company name, applied_at, status, "view in companies" link

### Right pane contents
- Long-form STAR sections (situation/task/action/result) OR markdown prep notes
- Inner wrapper `<div className="max-w-[680px]">` enforces 75ch readability cap
- Remaining pixels in the right pane beyond 680px are intentional whitespace -- do NOT stretch prose to fill

## Scenario matrix
| Viewport | Drawer width | Layout | Prose cap |
|---|---|---|---|
| <md | max-w-xl | single column | fills container |
| md..lg | max-w-2xl | single column | fills container |
| lg..xl | max-w-4xl | two column | 680px |
| xl..2xl | max-w-5xl | two column | 680px |
| >=2xl | max-w-6xl | two column | 680px |
| Short content (e.g., 5-bullet prep notes) | Same breakpoint width | two column; right pane naturally short, no forced empty space | 680px |
| Drawer explicitly opts out via variant='single-column' | Same breakpoint width | single column, full width up to breakpoint cap | 680px |
| User resizes browser across breakpoint | Layout re-computes via CSS only (no JS resize hooks) | correct at new breakpoint | 680px |

## Acceptance criteria
- [ ] New `src/frontend/src/components/ui/DrawerLayout.tsx` with the API above
- [ ] DrawerLayout is the ONLY place that encodes the two-column drawer pattern (single source of truth -- no duplicate flex/grid logic in consumer components)
- [ ] SlideOverPanel.tsx accepts responsive width classes (not a single fixed max-w)
- [ ] ExampleDrawerContent.tsx refactored to `<DrawerLayout left={<ExampleMetaPane/>} right={<ExampleStarContent/>} />`
- [ ] PrepNotesModal.tsx refactored to use DrawerLayout
- [ ] Prose `max-w-[680px]` enforced on all long-form text columns inside the right pane
- [ ] Drawer family audit: grep all `SlideOverPanel` and `Modal` imports across `src/frontend/src/`; list every usage in the PR description with an "adopted / opted-out / N/A" decision column; every drawer with long-form content either adopts DrawerLayout or opts out with explicit justification
- [ ] `npm run build` passes (tsc -b + vite build)
- [ ] Existing Vitest tests pass; new tests for DrawerLayout cover two-column, single-column, sticky left pane, responsive collapse
- [ ] Consumer audit: no existing drawer consumer renders incorrectly after refactor (visual check on dev server)

## Manual smoke test (MUST run on dev server per CLAUDE.md -- not just tests)
1. `scripts/dev.py` -> wait for "Application startup complete"
2. On 1920px monitor: open BehavioralQuestions -> click any question -> example drawer opens in two-column layout; left pane sticky with meta; right pane shows STAR prose capped at readable width
3. Resize browser narrower past lg breakpoint -> drawer collapses to single-column stack without layout break
4. Open Dashboard -> click a company name on an event (e.g., Lyra) -> PrepNotesModal opens with the same responsive two-column behavior (left: company meta; right: markdown prep notes)
5. On 2560px (or DevTools responsive emulation): drawer uses max-w-6xl (1152px) but prose still caps at 680px; extra ~180px is intentional whitespace, NOT stretched text
6. Open a short-form drawer (or one explicitly opted out): renders single-column correctly
7. Grep check: after refactor, search for `flex.*w-72` or two-column patterns in drawer-adjacent files -- only DrawerLayout.tsx should contain the implementation

## Dependencies
None (can interleave with Task 4).

### P2 -- Nice to Have

#### T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos test_check.py still uses check_stop_cache/write_stop_cache which were deprecated per LESSONS.md 2026-03-18. Cache can produce false passes when files change between cache write and next session. MLInterviewPrep already removed this. Action: Remove cache imports and calls from test_check.py; clean up hook_utils.py if no other callers.

#### T-P2-321: [SYNC] helixos: Propagate 3 new lessons from MLInterviewPrep 2026-04-08
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Three new MLInterviewPrep LESSONS.md entries not yet in helixos: (1) autonomous_run.sh uses sub-project task_db not root - universal lesson for orchestration. (2) DB-only content must have recovery path - relevant to helixos SQLite data/. (3) Markdown math pipe conflicts with remark-gfm table parsing - helixos uses remark-gfm in MarkdownRenderer.tsx and ConversationView.tsx. Append all three with [PROPAGATED] tag to helixos/LESSONS.md.

#### T-P2-322: [DEBT] MLInterviewPrep: Add problems.db to .gitignore
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: problems.db is untracked in MLInterviewPrep git repo and not in .gitignore. The .gitignore already covers interview_prep.db and tasks.db but missed this one. Action: Add problems.db to MLInterviewPrep/.gitignore.

#### T-P2-323: [DEBT] MLInterviewPrep: Sync dev deps from requirements.txt to pyproject.toml
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: 6 packages in requirements.txt not in pyproject.toml: pytest, pytest-asyncio, beautifulsoup4, pyyaml, ruff, playwright. Add as optional-dependencies dev group in pyproject.toml to satisfy CLAUDE.md dependency sync rule.

#### T-P2-324: [DEBT] helixos: Sync dev deps from requirements.txt to pyproject.toml
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: 6 packages in requirements.txt not in pyproject.toml: httpx, ruff, pytest-asyncio, mypy, pytest, pytest-timeout. Add as optional-dependencies dev group in pyproject.toml to satisfy CLAUDE.md dependency sync rule.

#### T-P2-356: Behavioral: semantic relevance spot-check script for 10 random Q-example links
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-352
- **Description**: # Behavioral: semantic relevance spot-check script for 10 random Q-example links

## Context
Audit 2026-04-11 confirmed valence matching is correct (failure Qs route to
failure-ish examples) but flagged quantity-over-precision risk: some links may
have low semantic specificity. Randomly sample 10 links and human-review each
for semantic fit (not just valence).

## Scenario matrix
| Condition | Expected |
|---|---|
| Script run in review mode | Prints 10 pairs + reviewer checklist template |
| Script run in apply mode on filled-in review file | DB reflects keep/drop/update-note decisions |
| Re-running review mode with same seed | Selects the same 10 pairs (reproducible) |
| Re-running review mode with different seed | Selects a different 10 (for follow-up audits) |

## Acceptance criteria
- [ ] scripts/audit_qe_link_relevance.py uses random.Random(seed) with seed defaulting to 20260411 for reproducibility
- [ ] Review mode: for each of 10 random links, print question text, example title + 1-line situation + 1-line result, current relevance_note, and a markdown checklist line (keep / drop / update-note)
- [ ] Apply mode: read a filled-in markdown file and apply the decisions (DROP removes the link row, UPDATE overwrites relevance_note, KEEP no-op)
- [ ] Output report committed to docs/audits/qe_link_spotcheck_2026-04-11.md
- [ ] Script tolerates resumption (if reviewer only filled in 5 of 10, skip unfilled)

## Manual smoke test
1. Run `python scripts/audit_qe_link_relevance.py --mode review`
2. Fill decisions in docs/audits/qe_link_spotcheck_2026-04-11.md
3. Run `python scripts/audit_qe_link_relevance.py --mode apply --file docs/audits/qe_link_spotcheck_2026-04-11.md`
4. Verify via API consumer: `curl /api/behavioral/questions/<id>/examples` on a modified question shows updated relevance_notes (per CLAUDE.md rule "verify via consumer, not producer")

## Dependencies
Depends on Task 2 (after secondary links are added, the sampling pool reflects the final state of the corpus).

### P3 -- Stretch Goals

## Blocked

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare python which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all python with /c/Anaconda/python.exe in ALL hook commands
3. Add SessionStart hook entry for setup_python_env.sh

BLOCKED: Claude Code file permissions block writes to helixos .claude/hooks/ directory from MLInterviewPrep session. Must be done from a helixos session or manually.

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL: helixos settings.json uses bare python for ALL hook commands. On Windows, bare python resolves to the AppData Store stub (exit code 49), silently breaking all hooks. Fix: (1) Replace all bare python with /c/Anaconda/python.exe in settings.json. (2) Add setup_python_env.sh SessionStart hook (copy from MLInterviewPrep) to inject Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE. CLAUDE.md already documents this prohibition (added 2026-03-21 via propagation) but the fix was never applied. This is the same root cause as MLInterviewPrep lesson [2026-03-20] #bash-tool #path.

#### T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ALL hook commands in helixos settings.json use bare python instead of /c/Anaconda/python.exe. This causes exit code 49 on Windows Store stub. Also missing setup_python_env.sh in SessionStart. Actions: (1) Replace python with /c/Anaconda/python.exe in every hook command. (2) Add setup_python_env.sh as first SessionStart hook copied from MLInterviewPrep. Source: MLInterviewPrep settings.json, LESSONS.md 2026-03-20.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/hooks/test_check.py still imports and uses check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed the cache in T-P2-188 (commit abf6543), per the lesson that stop caches can produce false passes when files change between sessions.

Action: Update helixos/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove check_stop_cache/write_stop_cache import and usage. Run tests after to confirm hook still works.

Source: MLInterviewPrep/.claude/hooks/test_check.py (current, cache-free version).

#### T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/test_check.py still uses check_stop_cache/write_stop_cache from hook_utils. The lesson [2026-03-18] established that stop caches cause false PASS results when files change between sessions. MLInterviewPrep already fixed this.

Action: Update template/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove cache import and usage. The template is the reference baseline, so it should have the best-known version of all hooks.

Source: MLInterviewPrep/.claude/hooks/test_check.py.

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: test_check.py imports check_stop_cache and write_stop_cache from hook_utils and uses them to skip re-running tests in the same session. These deprecated caching functions were removed from the hook architecture (LESSONS.md lesson [2026-03-18]: removed lint cache so every Stop hook runs fresh). The caching logic means test failures can be silently skipped if tests passed earlier in the same session. Fix: Remove the cache check/write calls from test_check.py so tests always run fresh on Stop. Keep check_stop_cache/write_stop_cache in hook_utils.py only if other hooks still use them.

## Completed Tasks

> 318 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-11** -- T-P1-354: Behavioral: theme pills on question rows + frequency-sorted filter sidebar on BehavioralQuestions page. # Behavioral: theme pills + frequency-sorted filter sidebar on BehavioralQuestions page
- [x] **2026-04-11** -- T-P1-353: Behavioral: seed 15-theme vocabulary, tag tables, and keyword backfill on Qs and examples. # Behavioral: 15-theme vocabulary, tag tables, keyword backfill
- [x] **2026-04-11** -- T-P1-352: Behavioral: add secondary example links for single-link Qs in communication/collaboration/leadership. # Behavioral: secondary links for single-link Qs in communication/collaboration/leadership
- [x] **2026-04-11** -- T-P0-351: Behavioral: seed 3 failure-story placeholders EX-30/31/32 [NEEDS-INPUT: 3 failure stories]. # Behavioral: seed 3 failure-story placeholders EX-30/31/32
- [x] **2026-04-10** -- T-P3-349: Add node_content and node_translations artifacts from Chinese batch. Commit the per-node markdown artifacts generated during the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130) for
- [x] **2026-04-10** -- T-P3-348: Lint: apply ruff auto-fixes to seed/translate/fix scripts. Apply ruff auto-fixes to scripts: import reordering, removal of unused imports, f-string cleanup (no placeholders).
- [x] **2026-04-10** -- T-P2-347: Pillar 3/6 translation and expansion scripts. Add translation + expansion scripts for the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130). Scripts generate/u
- [x] **2026-04-10** -- T-P2-346: Seed LinkedIn/Google/Pinterest prep content. Add seed scripts for LinkedIn question index, LinkedIn problem notes insertion, Google prep content, Pinterest prep cont
