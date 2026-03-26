# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-196: Batch expand Blind75 problem notes - batch 4 (14 problems)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Expand notes for LC 207, 208, 211, 213, 217, 226, 230, 235, 238, 242, 252, 253, 261, 268. Each note needs: 思路, 关键技巧, 核心代码 (code block), 注意点, 复杂度.

#### T-P1-197: Batch expand Blind75 problem notes - batch 5 (14 problems)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Expand notes for LC 269, 271, 295, 297, 300, 322, 323, 338, 417, 424, 435, 572, 647, 1143. Each note needs: 思路, 关键技巧, 核心代码 (code block), 注意点, 复杂度.

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

#### T-P2-192: Fix search persistence across tabs
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-190
- **Description**: Move renderSortBar() above Tabs component so search bar is shared. Search URL param already persists via useFilterParams. Files: src/frontend/src/pages/Problems.tsx. Depends on T-P1-190 (backend search).

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

> 175 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-26** -- T-P2-189: [DEBT] MLInterviewPrep: Add [project].dependencies to pyproject.toml. pyproject.toml has no [project].dependencies section. All main app deps (fastapi==0.109.0, sqlalchemy==2.0.25, anthropic
- [x] **2026-03-26** -- T-P2-188: [DEBT] MLInterviewPrep: Remove deprecated stop-cache from test_check.py. test_check.py imports and uses check_stop_cache/write_stop_cache from hook_utils.py (grep hits: hook_utils.py:129,157, t
- [x] **2026-03-26** -- T-P1-195: Batch expand Blind75 problem notes - batch 3 (14 problems). Expand notes for LC 124, 125, 128, 133, 139, 141, 143, 152, 153, 190, 191, 198, 200, 206. Each note needs: 思路, 关键技巧, 核心代
- [x] **2026-03-26** -- T-P1-194: Batch expand Blind75 problem notes - batch 2 (14 problems). Expand notes for LC 56, 57, 62, 70, 73, 76, 79, 91, 98, 100, 102, 104, 105, 121. Each note needs: 思路, 关键技巧, 核心代码 (code b
- [x] **2026-03-26** -- T-P1-193: Batch expand Blind75 problem notes - batch 1 (14 problems). Expand notes for LC 1, 3, 11, 15, 19, 20, 21, 33, 39, 48, 49, 53, 54, 55. Each note needs: 思路, 关键技巧, 核心代码 (code block), 
- [x] **2026-03-26** -- T-P1-191: Fix All tab: increase page size or show all when searching. All tab uses PAGE_SIZE=20 (Problems.tsx:29). Increase to 50/100 or set limit=200 when search is active. 159 problems tot
- [x] **2026-03-26** -- T-P1-190: Fix search: add backend search + match tags/pattern/notes. Add search param to GET /problems API. Server-side ILIKE across title, tags, pattern, company_tags, notes. Frontend: sen
- [x] **2026-03-22** -- T-P2-157: Wire enriched extraction into service layer + import. ## Summary
- [x] **2026-03-22** -- T-P2-156: Add full_page_text column to ForumPost + migration. ## Summary
- [x] **2026-03-22** -- T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor. ## Summary
- [x] **2026-03-22** -- T-P2-112: SSE chunked audio streaming (if latency requires it). Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with
- [x] **2026-03-22** -- T-P1-183: Framework progress: sync progress_pct with checklist state. Framework progress sync: auto-propagate status + progress upward when children change.
- [x] **2026-03-22** -- T-P1-182: Remove Review column from Problems table. Review column (next_review_at badge) adds no value currently: 0/155 problems have next_review_at set, no dedicated revie
- [x] **2026-03-22** -- T-P1-181: Fetch missing problem descriptions (5 problems). 5 problems (id=151-155) missing description. Fetch via POST /api/problems/fetch-all-descriptions. LeetCode GraphQL first
