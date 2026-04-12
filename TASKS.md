# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-373: [Pinterest/CN] Polish mixed-language notes to full Chinese: LC 311, 815, 1244
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Three existing notes are MIX (ratios 0.11-0.29). Rewrite the English prose sections to Chinese, keep code blocks and tech terms. Affects: LC 311 Sparse Matrix Multiplication (1714 chars), LC 815 Bus Routes (2766 chars), LC 1244 Design A Leaderboard (742 chars).

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

> 334 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-12** -- T-P2-379: [Pinterest/index] Refresh Pinterest LC index doc after translations/fetches. After Chinese translations and missing descriptions are done, regenerate the Pinterest LC Must-Do: Review & Index compan
- [x] **2026-04-12** -- T-P1-378: [Pinterest/notes] Write LC 1723 solution notes (Find Minimum Time to Finish All Jobs). Pinterest must-do; no notes yet. Cover: binary search on answer + backtracking feasibility check, pruning (sort jobs des
- [x] **2026-04-12** -- T-P1-377: [Pinterest/notes] Write LC 642 solution notes (Design Search Autocomplete System). Pinterest must-do; no notes yet. Cover: Trie + hot-words map at each node, top-k with heap, input streaming state machin
- [x] **2026-04-12** -- T-P1-376: [Pinterest/notes] Write LC 43 solution notes (Multiply Strings). Pinterest must-do; no notes yet. Cover: digit-by-digit simulation with (i+j, i+j+1) index trick, carry propagation, lead
- [x] **2026-04-12** -- T-P1-375: [Pinterest/notes] Write LC 410 solution notes (Split Array Largest Sum). Pinterest must-do; no notes yet. Cover: binary-search-on-answer approach (monotonic feasibility check), DP on (i,k) alte
- [x] **2026-04-12** -- T-P1-374: [Pinterest/desc] Fetch missing problem descriptions: LC 2402, 1110, 1723. Three Pinterest problems have empty description field. Use the existing fetch-description endpoint or leetcode.ca scrape
- [x] **2026-04-12** -- T-P1-372: [Pinterest/CN] Translate LC 1110 notes to Chinese (Delete Nodes And Return Forest). Translate existing English notes (5361 chars) to Chinese. is_root flag + carry-state-down-vs-post-order principle. Keep 
- [x] **2026-04-12** -- T-P1-371: [Pinterest/CN] Translate LC 2402 notes to Chinese (Meeting Rooms III). Translate existing English notes (5257 chars) to Chinese. Two-heap simulation pattern. Keep code and complexity notation
- [x] **2026-04-12** -- T-P1-370: [Pinterest/CN] Translate LC 282 notes to Chinese (Expression Add Operators). Translate existing English notes (8433 chars) to Chinese. Covers Version A (brute-force + custom myEval), Version B (pre
- [x] **2026-04-12** -- T-P1-369: [Pinterest/CN] Translate LC 465 notes to Chinese (Optimal Account Balancing). Translate existing English notes (9898 chars) to Chinese. Includes two approaches (Bitmask DP + naive DFS), Full-Transfe
- [x] **2026-04-12** -- T-P1-368: [Pinterest/CN] Translate LC 332 notes to Chinese (Reconstruct Itinerary). Translate existing English notes (2977 chars) to Chinese. Keep code blocks, algorithm names (Hierholzer, Eulerian Path),
- [x] **2026-04-11** -- T-P2-365: Behavioral audit: verify all technical_problem_solving examples have explicit data-driven evidence. Audit pass over the example_theme_tags rows for theme_id=technical_problem_solving (currently 27 examples). For each, re
- [x] **2026-04-11** -- T-P2-364: Behavioral failure cluster: structural polish (tags + narration guards) for EX-15/16/17/30. STRUCTURAL/MECHANICAL polish ONLY for the 4 remaining failure-cluster master stories. Brings them in line with the EX-33
- [x] **2026-04-11** -- T-P2-363: BQ navigation: end-to-end browse-path preservation across QuickIndex/theme/drawer. Audit and fix end-to-end navigation paths so user never loses browse context across QuickIndex(BQ) -> theme detail -> ex
- [x] **2026-04-11** -- T-P2-356: Behavioral: semantic relevance spot-check script for 10 random Q-example links. # Behavioral: semantic relevance spot-check script for 10 random Q-example links
- [x] **2026-04-11** -- T-P2-324: [DEBT] helixos: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: httpx, ruff, pytest-asyncio, mypy, pytest, pytest-timeout. Add as 
- [x] **2026-04-11** -- T-P2-323: [DEBT] MLInterviewPrep: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: pytest, pytest-asyncio, beautifulsoup4, pyyaml, ruff, playwright. 
- [x] **2026-04-11** -- T-P2-322: [DEBT] MLInterviewPrep: Add problems.db to .gitignore. problems.db is untracked in MLInterviewPrep git repo and not in .gitignore. The .gitignore already covers interview_prep
- [x] **2026-04-11** -- T-P0-367: BQ Quick Index: generate cn_elevator_pitch batch 2 (EX-10 to EX-33, 13 examples). Generate high-quality Chinese elevator pitch summaries for remaining 13 examples missing cn_elevator_pitch. Format: '{su
- [x] **2026-04-11** -- T-P0-366: BQ Quick Index: generate cn_elevator_pitch batch 1 (BLOG-01 to EX-09, 14 examples). Generate high-quality Chinese elevator pitch summaries for 14 examples missing cn_elevator_pitch. Format: '{summary} | K
