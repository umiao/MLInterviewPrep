# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

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

#### T-P2-257: [DEBT] MLInterviewPrep: Remove unused check_stop_cache/write_stop_cache from hook_utils.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: hook_utils.py defines check_stop_cache() and write_stop_cache() (lines 129-170) but no hook file imports or calls them. These are dead code left over from the old stop-cache caching architecture. LESSONS.md [2026-03-18] documents that lint caching was removed so every Stop hook runs fresh. Remove these two functions and their docstrings from hook_utils.py. Add regression test confirming no hook imports them.

## Completed Tasks

> 223 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-02** -- T-P2-206: [SYNC] Propagate 2 universal lessons to helixos LESSONS.md. helixos/LESSONS.md is missing 2 universal lessons already in the template:
- [x] **2026-04-02** -- T-P2-186: [SYNC] Propagate ruff version-drift lesson to helixos. MLInterviewPrep LESSONS.md has [2026-03-02] lesson about ruff version drift between local and CI (loose pin + separate i
- [x] **2026-04-01** -- T-P2-256: [DEBT] MLInterviewPrep: Remove stale scripts/git-hooks/ path from CLAUDE.md. CLAUDE.md File Structure section references scripts/git-hooks/ as a directory but only scripts/pre-commit exists (no git
- [x] **2026-04-01** -- T-P1-251: Add company-filtered Notes tab to Problems page for quick solution access. On the Problems page, when filtering by company (e.g. Uber or LinkedIn in Company Freq tab), users should be able to qui
- [x] **2026-04-01** -- T-P0-266: LinkedIn: Write solution notes for top-50 frequency problems (batch 1). Write comprehensive solution notes for the top 50 LinkedIn problems by frequency that currently lack notes.
- [x] **2026-04-01** -- T-P0-265: LinkedIn: Enrich doc#24 (ML Fundamentals + Coding) with detailed solutions. Doc#24 (LinkedIn ML Fundamentals + Coding, 33241c). Review all ML and coding questions and ensure each has: complete ans
- [x] **2026-04-01** -- T-P0-264: LinkedIn: Enrich doc#22 (System Design) with detailed solutions. Doc#22 (LinkedIn System Design, 32989c). Review all system design questions and ensure each has: architecture diagram de
- [x] **2026-04-01** -- T-P0-263: LinkedIn: Enrich doc#21 (Probability/Stats) with detailed solutions. Doc#21 (LinkedIn probability/statistics interview prep notes, 34594c). Review all probability and statistics questions a
- [x] **2026-04-01** -- T-P0-262: LinkedIn: Enrich doc#26 (Question Index) with full solutions for all 47 questions. Doc#26 (LinkedIn Interview Questions Index, 30198c, 47 questions) currently has question descriptions but NO actual solu
- [x] **2026-04-01** -- T-P0-258: Fetch LC problem descriptions from leetcode.ca for all 891 missing problems. 891 of 1057 problems in mle_prep.db have no description. Create a script scripts/fetch_lc_descriptions.py that:
- [x] **2026-04-01** -- T-P0-253: Convert Uber BPS prep docs to Chinese with acronym expansion. Convert all Uber BPS prep documents to Chinese following the project's chinese_conversion_spec.md rules. Files to conver
- [x] **2026-03-31** -- T-P2-248: Uber BPS: Create timed mock interview problem sets. 3 mock BPS sets simulating 45min coding. Each: 1 medium + 1 medium/hard with follow-ups. Set 1: LC 230 variant + Rider C
- [x] **2026-03-31** -- T-P2-240: [DEBT] MLInterviewPrep: Add _temp*.json pattern to .gitignore. `_temp_docs.json` is untracked in MLInterviewPrep and not in .gitignore. These files appear to be temp artifacts from co
- [x] **2026-03-31** -- T-P1-247: Uber BPS: Problem pattern cheat sheet by algorithm. Create docs/uber_bps_pattern_cheatsheet.md organizing problems by pattern: BFS/DFS (994,1020,1197,230,337,549,987,2791,5
- [x] **2026-03-31** -- T-P1-246: Uber BPS: KNN from-scratch + ML fundamentals review. Recruiter explicitly mentions KNN. Create: (1) KNN from scratch Python - distance metrics, k selection, weighted KNN, (2
- [x] **2026-03-31** -- T-P1-245: Uber BPS: Create D&A (Design and Architecture) prep document. Create docs/uber_bps_design_architecture.md: (1) Project showcase - Ranking-as-Allocation, LLM eval pipeline with high-l
- [x] **2026-03-31** -- T-P0-252: Condense ML Fundamentals From-Scratch guide: deduplicate code, modular design. The ML Fundamentals From-Scratch guide (Doc 27/28/29, 162K chars each; source files t1-t8, 199K total) has significant c
- [x] **2026-03-31** -- T-P0-250: Organize LinkedIn prep notes into company_documents with problem solutions. Ensure LinkedIn prep materials are properly organized in company_documents (company_id=1). Currently has docs 21-27. Che
- [x] **2026-03-31** -- T-P0-249: Import Uber BPS prep docs into company_documents for web UI access. Import all 7 Uber prep markdown docs (uber_bps_lc_solutions.md, uber_bps_custom_solutions.md, uber_bps_pattern_cheatshee
- [x] **2026-03-31** -- T-P0-244: Uber BPS: Update phone screen prep doc with BPS format. Update docs/uber_phone_screen_prep.md to reflect BPS format from recruiter: 5min intro, 40-50min coding+D&A, 5min Q&A. A
