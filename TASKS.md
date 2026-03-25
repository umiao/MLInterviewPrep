# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare `python` which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all `python \"$CLAUDE_PROJECT_DIR/...\"` with `/c/Anaconda/python.exe \"$CLAUDE_PROJECT_DIR/.../...\"` in ALL hook commands
3. Add SessionStart hook entry: {\"type\": \"command\", \"command\": \"bash \\\"$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh\\\"\", \"timeout\": 10}

Reference: MLInterviewPrep/.claude/settings.json (correct format) and MLInterviewPrep/.claude/hooks/setup_python_env.sh (source file to copy)

Verification: After fix, run `/c/Anaconda/python.exe .claude/hooks/plan_mode.py status` to confirm hooks work.

### P2 -- Nice to Have

#### T-P2-185: [SYNC] helixos CLAUDE.md: Add no-bare-python rule to Prohibited Actions
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep CLAUDE.md Prohibited Actions has this rule (lines 62-66):

  Never use bare `python` in hook commands or scripts. The Windows Store stub exits with code 49. Use `/c/Anaconda/python.exe` (absolute path) in settings.json hooks. The SessionStart hook setup_python_env.sh injects Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE.

helixos CLAUDE.md has the lesson in LESSONS.md (line 266) but not in Prohibited Actions. Add the rule to the Prohibited Actions section to prevent recurrence.

Should be done AFTER [SYNC] helixos: Fix broken hooks task.

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 175 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-22** -- T-P2-157: Wire enriched extraction into service layer + import. ## Summary
- [x] **2026-03-22** -- T-P2-156: Add full_page_text column to ForumPost + migration. ## Summary
- [x] **2026-03-22** -- T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor. ## Summary
- [x] **2026-03-22** -- T-P2-112: SSE chunked audio streaming (if latency requires it). Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with
- [x] **2026-03-22** -- T-P1-183: Framework progress: sync progress_pct with checklist state. Framework progress sync: auto-propagate status + progress upward when children change.
- [x] **2026-03-22** -- T-P1-182: Remove Review column from Problems table. Review column (next_review_at badge) adds no value currently: 0/155 problems have next_review_at set, no dedicated revie
- [x] **2026-03-22** -- T-P1-181: Fetch missing problem descriptions (5 problems). 5 problems (id=151-155) missing description. Fetch via POST /api/problems/fetch-all-descriptions. LeetCode GraphQL first
