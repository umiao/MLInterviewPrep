# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-381: [BQ-rework] EX-16 PhD Interns Notebook-to-Production: add onboarding metric
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Flags A+C. Use user-provided facts (2026-04-13 Discord): 6 interns in my org adopted a similar notebook-to-production checklist/template; outcome was reported back to the HR + University team as input to improve the academic->industry transition program. Lead Result with "6 interns across the org adopted the checklist; outcome cited by HR + University team for onboarding program iteration". Convert "we/team" in Action to "I built the template / I ran the first review pass / I briefed HR on the outcome". Edit both JSON + markdown.

#### T-P0-382: [BQ-rework] EX-19 Model Deprecation Incident: own the gap personally
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Flags C+D. Use user-provided facts (2026-04-13 Discord): This was NOT a user-facing prod-model impact -- but it took 2 full days of my dedicated effort to fix, and the real test was cross-team trust, collaboration, and reasonable attribution of who did what. Reframe the story: own the attribution/trust dimension explicitly ("I should have checked downstream consumer Slack channels before deprecating; I spent 2 focused days resolving, and more importantly re-established trust and a post-mortem attribution norm across the affected teams"). Quantify: 2-day fix turnaround; zero user-facing impact; cross-team trust restored. Edit JSON + markdown.

#### T-P0-383: [BQ-rework] EX-20 Cross-DC Deployment Incident: quantify blast radius
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Flags A+C. Use user-provided facts (2026-04-13 Discord): Cross-DC deployment was delayed ~6 hours, blocking TWO launches (name them if known, else "two dependent launches"); I felt significant pressure and was called in TWICE to present RCA reports to Head of Engineering. Add additional achievements in Result: e.g. systematic cleanup of other implicit-coupling instances discovered during RCA, science-team factor/model migration to declarative artifactory. Lead with: "6-hour deployment delay blocking 2 launches; presented RCA to Head of Engineering x2; drove follow-up cleanup of N additional implicit-coupling sites". Replace "quickly stabilized" with concrete blast radius + MTTR + RCA-to-fix deliverable. Sharpen personal contribution vs backend team. Edit JSON + markdown.

#### T-P0-384: [BQ-rework] EX-22 Pushback on Scope: add delivery-impact metric
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Flags A+C+D. Target: JSON EX-18 (audit called it EX-22) "Pushing Back on Unreasonable Scope". User-provided facts (2026-04-13 Discord):
(Q1 burnout duration) Sustained 1 month, intermittently 10h/day;
(Q2 eng-time post-descope) freed time shipped new contextualized embedding + larger model work; avoided pulling the team in an opposite-direction speculative tech investment;
(Q3 self-reflection) this was my first quarter after rotating into the ranking team - still learning team/stack/business context; wanted to overstretch myself to prove I could deliver.
Rewrite to lead with these specifics. Replace "leadership accepted" passive framing with active "I delivered pros/cons analysis that let leaders converge". Close with the self-reflection line. Edit docs/bq_behavioral_examples.json (EX-18) + docs/bq_improved_stories.md (STORY 18) + behavioral_examples DB row (example_id=EX-18).

#### T-P0-385: [BQ-rework] EX-28 Explaining Allocation to VP: estimate avoided cost
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Flags A+C. Target: JSON EX-24 (audit called it EX-28) "Explaining Allocation Problem to VP". User-provided facts (2026-04-13 Discord):
(Q4 avoided cost) combo-launch would have burned at least 2-3 weeks on debugging + reverse-test collection for an outcome already known;
(Q5 follow-through) allocation framing became broadly adopted because of its near-real-time deployment capability + authenticity + long-term business value + fit with C2C strategy; team-wide mental model shift;
(Q6 tangible deliverable) I brought a concrete analysis I had been iterating on: the top-10 and top-30 slot distribution, framed as "you can bias toward any ONE of the priorities you want but not all simultaneously -- slots are a finite resource".
Rewrite Result to lead with the avoided-cost estimate and the top-10/top-30 analysis as the active deliverable. Replace "VP accepted" with "VP adopted the slot-as-finite-resource framing; allocation became team mental model for ranking strategy". Edit JSON (EX-24) + markdown (STORY 24) + DB row (example_id=EX-24).

#### T-P0-386: [BQ-rework] EX-33 MoE Paradigm Shift: close the arc with downstream win
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Flags C+D. Target: DB `behavioral_examples` row example_id=EX-33 "MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Negative Result" (NOT in JSON file -- DB-only story populated via scripts/_populate_hash_and_moe_examples.py on 2026-04-11). User confirmed story exists (keyword "MoE - failure").
Key discovery during audit: the Result field ALREADY contains "200M annualized GMB from the subsequent allocation policy work" but buries it behind the org-rename narrative. Rework brief: (1) Lead Result with the 200M GMB number prominently (it is the business metric the audit claimed was missing); (2) Add adoption count if recoverable (how many Allocation-team shipped products post-rename?); (3) Keep the honest-negative-result framing (MoE deprecated) but let the follow-through win close the arc. Also polish Situation/Action if any "we" ambiguity. Edit DB row only (no JSON match needed). If a matching entry should also live in docs/bq_improved_stories.md, add a STORY 33 section.

### P1 -- Should Have (agentic intelligence)

#### T-P1-387: [BQ-sweep] Tier-2 metric補充: replace adjectives with numbers across ~12 stories
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: User guidance (2026-04-13 Discord): "Fill in similarly". For stories where user has not provided facts, use [TODO: confirm number] placeholder markers -- never invent metrics. Target stories and suggested fills: EX-1 (initial A/B lift before scaling), EX-4 (which Q OKRs updated), EX-14 (adoption count + Q), EX-15 (intern perf rating or ticket backlog), EX-17 (# subsequent papers applying the norm), EX-18 (sync DB to improved-story version: 18K labels/day at $500, 1.5% GMB -- these are known), EX-21 (# merged PRs with zero review-restart), EX-23 (traffic % avoided on invalid A/B), EX-24 (FP-rate delta), EX-29 (GMV delta or A/B result), EX-35 (new-seller FP rate X%->Y%), EX-36 (0 privacy incidents + retrieval recall@K unchanged). Replace "improved/streamlined/widely adopted" with either a concrete number (if known) or "[TODO: confirm]". Do NOT fabricate. Edit JSON + markdown for each.

#### T-P1-388: [BQ-sweep] Tier-2 ownership sharpening: "we" -> "I" in Action sections
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Sweep target stories: EX-2 (lead +1% GMB prominently), EX-11 (I led compression, researcher gave context), EX-13 (I flagged, I took point on negotiations; manager gave air cover), EX-25 (I independently researched and built), EX-26 (I defined acceptance criteria, validated final choice), EX-27 (I served as DRI / critical-path owner, not coordinator). Keep "we" only in Situation (context). Every Action bullet must start with "I". Edit JSON + markdown.

#### T-P1-389: [BQ-sweep] Tier-2 catch-all polish: remaining 1-weak-signal stories
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Remaining Tier-2 stories not covered by metric or ownership sweeps. Primary: EX-7 (add downstream metric after unbiased dataset adoption). Scan JSON/md for any other stories flagged in 2026-04-13 audit that dont fit metric or ownership sweeps. One-off fixes per story -- structural polish only. Edit JSON + markdown.

### P2 -- Nice to Have

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

#### T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos test_check.py still uses check_stop_cache/write_stop_cache which were deprecated per LESSONS.md 2026-03-18. Cache can produce false passes when files change between cache write and next session. MLInterviewPrep already removed this. Action: Remove cache imports and calls from test_check.py; clean up hook_utils.py if no other callers.

## Completed Tasks

> 350 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-12** -- T-P2-379: [Pinterest/index] Refresh Pinterest LC index doc after translations/fetches. After Chinese translations and missing descriptions are done, regenerate the Pinterest LC Must-Do: Review & Index compan
- [x] **2026-04-12** -- T-P2-373: [Pinterest/CN] Polish mixed-language notes to full Chinese: LC 311, 815, 1244. Three existing notes are MIX (ratios 0.11-0.29). Rewrite the English prose sections to Chinese, keep code blocks and tec
- [x] **2026-04-12** -- T-P1-378: [Pinterest/notes] Write LC 1723 solution notes (Find Minimum Time to Finish All Jobs). Pinterest must-do; no notes yet. Cover: binary search on answer + backtracking feasibility check, pruning (sort jobs des
- [x] **2026-04-12** -- T-P1-377: [Pinterest/notes] Write LC 642 solution notes (Design Search Autocomplete System). Pinterest must-do; no notes yet. Cover: Trie + hot-words map at each node, top-k with heap, input streaming state machin
- [x] **2026-04-12** -- T-P1-376: [Pinterest/notes] Write LC 43 solution notes (Multiply Strings). Pinterest must-do; no notes yet. Cover: digit-by-digit simulation with (i+j, i+j+1) index trick, carry propagation, lead
- [x] **2026-04-12** -- T-P0-380: [BQ-rework] EX-12 Code Review Standards: add concrete metric. Flag C (vague metric). Use user-provided facts (2026-04-13 Discord): before the checklist/standards, ~80% of changes req
