# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ALL hook commands in helixos settings.json use bare python instead of /c/Anaconda/python.exe. This causes exit code 49 on Windows Store stub. Also missing setup_python_env.sh in SessionStart. Actions: (1) Replace python with /c/Anaconda/python.exe in every hook command. (2) Add setup_python_env.sh as first SessionStart hook copied from MLInterviewPrep. Source: MLInterviewPrep settings.json, LESSONS.md 2026-03-20.

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

## Completed Tasks

> 286 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-09** -- T-P1-331: DoorDash ML Domain prep: Case study mock answers + SCOPE templates. Create prep doc with interview-ready answers: (1) 5 classic case studies with full SCOPE framework (restaurant recommend
- [x] **2026-04-09** -- T-P1-330: DoorDash ML Domain prep: LLM+RecSys frontiers + cross-vertical transfer. Create prep doc: (1) DoorDash LLM+RecSys: cross-vertical feature gen, Hierarchical RAG, Familiarity+Affordability+Novelt
- [x] **2026-04-09** -- T-P0-329: DoorDash ML Domain prep: ML fundamentals rapid review + quick-fire Q&A. Create prep doc for ML fundamentals interspersed during domain interview: (1) Optimization: SGD/Adam/AdaGrad, LR schedul
- [x] **2026-04-09** -- T-P0-328: DoorDash ML Domain prep: Search + semantic matching + bias/debiasing. Create prep doc: (1) Query Understanding: intent classification, query rewriting, NER, query expansion. (2) Semantic mat
- [x] **2026-04-09** -- T-P0-327: DoorDash ML Domain prep: Feature engineering + DL modules for RecSys. Create prep doc: (1) Four feature categories with DoorDash mapping. (2) Embedding: ID, hashing trick, sequence (Transfor
- [x] **2026-04-09** -- T-P0-326: DoorDash ML Domain prep: Ranking models + Multi-Task Learning deep dive. Create comprehensive prep doc: (1) Wide&Deep/DeepFM/DCN/DCNv2/xDeepFM/AutoInt comparison. (2) MTL: Shared-Bottom, MMoE, 
- [x] **2026-04-09** -- T-P0-325: DoorDash ML Domain prep: RecSys architecture + Retrieval deep dive. Create comprehensive prep doc covering: (1) Multi-Stage RecSys Pipeline (Retrieval->PreRanking->Ranking->ReRanking) with
- [x] **2026-04-08** -- T-P2-318: SD Prep: Update landing page with all topics + category grouping. After all 20 content tasks are done, update SystemDesignList.tsx Interview Prep tab:
- [x] **2026-04-08** -- T-P2-287: System design formula audit: all modules. CRITICAL SAFETY RULES: (1) NEVER run any module seed script unless fixing that specific module. (2) NEVER overwrite Chin
- [x] **2026-04-08** -- T-P2-286: System design depth: ml-system-design-patterns expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ml_system_design_patterns.py
- [x] **2026-04-08** -- T-P2-285: System design depth: vibe-code-engineering restructure. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_vibe_code_engineering.py. (2
- [x] **2026-04-08** -- T-P2-279: [SYNC] Propagate DB-only content recovery lesson to template. Propagate MLInterviewPrep LESSONS.md entry [2026-04-08] to claude-code-project-template/LESSONS.md.
- [x] **2026-04-08** -- T-P2-278: [SYNC] Propagate SQLite naive-datetime timezone lesson to helixos. Propagate MLInterviewPrep LESSONS.md entry [2026-04-07] to helixos/LESSONS.md.
- [x] **2026-04-08** -- T-P1-317: SD Prep: Design a Distributed Cache. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-316: SD Prep: Design an Auction System (eBay). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-315: SD Prep: Design a Web Crawler. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-314: SD Prep: Design Ticketmaster / Hotel Reservation. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
