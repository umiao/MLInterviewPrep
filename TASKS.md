# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-185: [SYNC] helixos CLAUDE.md: Add no-bare-python rule to Prohibited Actions
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep CLAUDE.md Prohibited Actions has this rule (lines 62-66):

  Never use bare `python` in hook commands or scripts. The Windows Store stub exits with code 49. Use `/c/Anaconda/python.exe` (absolute path) in settings.json hooks. The SessionStart hook setup_python_env.sh injects Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE.

helixos CLAUDE.md has the lesson in LESSONS.md (line 266) but not in Prohibited Actions. Add the rule to the Prohibited Actions section to prevent recurrence.

Should be done AFTER [SYNC] helixos: Fix broken hooks task.

#### T-P2-186: [SYNC] Propagate ruff version-drift lesson to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep LESSONS.md has [2026-03-02] lesson about ruff version drift between local and CI (loose pin + separate install = silent drift). Tags: #ruff #ci #version-drift. Not yet in helixos LESSONS.md. Action: append the lesson to helixos/LESSONS.md with [PROPAGATED] tag.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

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

## Completed Tasks

> 191 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-26** -- T-P2-192: Fix search persistence across tabs. Move renderSortBar() above Tabs component so search bar is shared. Search URL param already persists via useFilterParams
- [x] **2026-03-26** -- T-P2-189: [DEBT] MLInterviewPrep: Add [project].dependencies to pyproject.toml. pyproject.toml has no [project].dependencies section. All main app deps (fastapi==0.109.0, sqlalchemy==2.0.25, anthropic
- [x] **2026-03-26** -- T-P2-188: [DEBT] MLInterviewPrep: Remove deprecated stop-cache from test_check.py. test_check.py imports and uses check_stop_cache/write_stop_cache from hook_utils.py (grep hits: hook_utils.py:129,157, t
- [x] **2026-03-26** -- T-P1-203: Verify imported problems: counts, tags, frequency order. Post-import verification. (1) Count problems per company tag matches 1014. (2) Spot-check first 10 and last 10 match ori
- [x] **2026-03-26** -- T-P1-202: Batch import parsed LC problems into DB with company tags. Import parsed problems into mle_prep.db. All 1014 tagged with LinkedIn+Uber+Adobe. (1) Existing problems (~159): merge c
- [x] **2026-03-26** -- T-P1-201: Parse staging LC file: extract problems for LinkedIn/Uber/Adobe. Parse 'LC to be added 题解.txt' (3613 lines, 1014 problems) from C:\Users\Shenghui Xu\Desktop\staging. All three companies
- [x] **2026-03-26** -- T-P1-200: Add Adobe phone screen event to interview timeline. Add Adobe phone screen. Company=Adobe, event_type=phone_screen, week of March 30-April 3 2026 (exact time TBD). Steps: I
