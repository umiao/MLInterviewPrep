# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-216: Adobe Prep Day7: Review checklist + concept map + error cards
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Create final review note: (1) Master checklist across all 6 domains (Diffusion, RLHF/DPO, Distributed, Inference, RoPE, Video) with checkbox items from Days 1-6. (2) HTML concept map showing connections between all topics. (3) Error correction quick-reference table (7 common misunderstandings). (4) Daily time allocation table. All formulas use 440.

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

#### T-P2-206: [SYNC] Propagate 2 universal lessons to helixos LESSONS.md
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/LESSONS.md is missing 2 universal lessons already in the template:
1. [2026-03-02] Ruff version drift between local and CI (#ruff #ci) -- loose ruff pin causes CI-only failures; fix: pin ruff==X.Y.Z in requirements.txt.
2. [2026-03-11] Task ID P = Phase anti-pattern went undetected (#task-naming #convention-drift) -- P should always mean priority, never phase/stage.

Action: Append both entries (verbatim from template LESSONS.md) to helixos/LESSONS.md. Source: claude-code-project-template/LESSONS.md.

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

#### T-P2-209: [SYNC] Propagate template session_context db-missing warning to MLInterviewPrep
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/session_context.py (lines 475-486) has a db_missing_warning feature: if .claude/tasks.db is absent but TASKS.md has tasks, it warns the user to run task_db.py import. This is useful for fresh-clone scenarios.

MLInterviewPrep/.claude/hooks/session_context.py is missing this warning block.

Action: Port the db_missing_warning block from template to MLInterviewPrep session_context.py.

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

- [x] **2026-03-27** -- T-P0-215: Adobe Prep Day6: Mock interview questions + STAR-T project stories. Create study note: (1) STAR-T framework (Situation/Task/Approach/Result/Transfer) with template. (2) 3 project story out
- [x] **2026-03-27** -- T-P0-214: Adobe Prep Day5: Inference optimization + project narrative note. Create study note: (1) FlashAttention: tiled computation, SRAM vs HBM, IO complexity. (2) Quantization comparison table:
- [x] **2026-03-27** -- T-P0-213: Adobe Prep Day4: RoPE + long context + video generation note. Create study note: (1) RoPE: rotation matrix formulation, theta_i formula, how q_m*k_n depends only on m-n. HTML diagram
- [x] **2026-03-27** -- T-P0-212: Adobe Prep Day3: Distributed training (DP/TP/PP/FSDP) note. Create study note: (1) 4 parallelism strategies with HTML diagram showing how each splits model/data. (2) DP: full repli
- [x] **2026-03-27** -- T-P0-211: Adobe Prep Day2: RLHF/DPO alignment + LLM distillation note. Create study note covering: (1) RLHF 3-step flow (SFT -> Reward Model -> PPO) with HTML flow diagram. (2) Bradley-Terry 
- [x] **2026-03-27** -- T-P0-210: Adobe Prep Day1: Diffusion Models deep-dive note. Create comprehensive study note for Diffusion Models (Adobe's core tech). Content: (1) DDPM forward process with full ma
- [x] **2026-03-26** -- T-P2-192: Fix search persistence across tabs. Move renderSortBar() above Tabs component so search bar is shared. Search URL param already persists via useFilterParams
- [x] **2026-03-26** -- T-P2-189: [DEBT] MLInterviewPrep: Add [project].dependencies to pyproject.toml. pyproject.toml has no [project].dependencies section. All main app deps (fastapi==0.109.0, sqlalchemy==2.0.25, anthropic
- [x] **2026-03-26** -- T-P2-188: [DEBT] MLInterviewPrep: Remove deprecated stop-cache from test_check.py. test_check.py imports and uses check_stop_cache/write_stop_cache from hook_utils.py (grep hits: hook_utils.py:129,157, t
- [x] **2026-03-26** -- T-P1-205: Add Company Frequency tab to Problems page (like Blind 75). Add a new tab 'Company Freq' (or similar) to the Problems page, at the same level as 'All Problems' and 'Blind Grind 75'
- [x] **2026-03-26** -- T-P1-204: Add real-time HH:MM:SS countdown to dashboard timeline events. Replace static countdown text (e.g. 'in 3 days') with a live ticking countdown in HH:MM:SS format. Only use hours:minute
- [x] **2026-03-26** -- T-P1-203: Verify imported problems: counts, tags, frequency order. Post-import verification. (1) Count problems per company tag matches 1014. (2) Spot-check first 10 and last 10 match ori
- [x] **2026-03-26** -- T-P1-202: Batch import parsed LC problems into DB with company tags. Import parsed problems into mle_prep.db. All 1014 tagged with LinkedIn+Uber+Adobe. (1) Existing problems (~159): merge c
- [x] **2026-03-26** -- T-P1-201: Parse staging LC file: extract problems for LinkedIn/Uber/Adobe. Parse 'LC to be added 题解.txt' (3613 lines, 1014 problems) from C:\Users\Shenghui Xu\Desktop\staging. All three companies
- [x] **2026-03-26** -- T-P1-200: Add Adobe phone screen event to interview timeline. Add Adobe phone screen. Company=Adobe, event_type=phone_screen, week of March 30-April 3 2026 (exact time TBD). Steps: I
