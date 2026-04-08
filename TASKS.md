# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-282: System design depth: distributed-task-queue add Defense Q&A
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_distributed_task_queue.py. (2) NEVER overwrite Chinese with English. (3) Read DB content FIRST, preserve ALL existing Chinese. (4) Seed script = source of truth. (5) Formulas: \mid not |.

Add Defense Q&A to distributed-task-queue. Current: 22.9K chars, rich content, 0 Q&A.

REFERENCE: Read scripts/content_module_arbitration.py DEFENSE section for format.

STEPS: 1. Read DB (slug=distributed-task-queue), dump all 8 sections. 2. Find or create scripts/content_distributed_task_queue.py, preserve ALL existing Chinese. 3. Add 5 Defense Q&A (Chinese): Exactly-once delivery, Poison pill, Priority inversion, Worker starvation, Distributed lock trade-off. 4. Seed and verify all other sections unchanged.

AC: 5 Q&A acknowledge-mitigate-data format, Chinese with English terms, ALL existing content preserved, Seed script = source of truth, No bare | in math

#### T-P1-283: System design depth: database-comparison supplement
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_database_comparison.py. (2) NEVER overwrite Chinese with English. (3) Read DB first, preserve existing Chinese. (4) Seed script = source of truth. (5) Formulas: \mid not |.

Supplement database-comparison. Current: 21.1K chars, 6 Q&A, missing iteration/evaluation and failure modes.

REFERENCE: Read scripts/content_module_arbitration.py for depth standard.

STEPS: 1. Read DB (slug=database-comparison), dump all 8. 2. Find or create scripts/content_database_comparison.py, preserve Chinese. 3. Expand (Chinese): Migration strategy (dual-write, shadow, cutover), 3 failure modes (split brain, corruption, hot partition), Capacity planning, Iteration approach. 4. Seed and verify.

AC: Migration strategy, 3 failure modes, Capacity planning, Seed script = Chinese source of truth, ALL existing preserved, No bare | in math, Total >= 24K

#### T-P1-284: System design depth: pbe-pipeline expansion
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_pbe_pipeline.py. (2) NEVER overwrite Chinese with English. (3) Read DB first, preserve existing Chinese. (4) Seed script = source of truth. (5) Formulas: \mid not |.

Expand pbe-pipeline. Current: 12.5K chars, 6 display math, 4 Q&A, missing iteration/evaluation, data quality monitoring, failure modes.

REFERENCE: Read scripts/content_module_arbitration.py for depth standard.

STEPS: 1. Read DB (slug=pbe-pipeline), dump all 8. 2. Find or create scripts/content_pbe_pipeline.py, preserve Chinese. 3. Expand (Chinese): Data quality monitoring (anomaly detection, schema drift, freshness SLAs), Schema evolution strategy, Iteration & Evaluation, 2-3 failure modes, 2 more Defense Q&A. 4. Seed and verify.

AC: Data quality monitoring, Schema evolution, Iteration subsection, 2+ failure modes, 6+ total Q&A, Seed = Chinese source of truth, ALL existing preserved, No bare |, Total >= 16K

### P2 -- Nice to Have

#### T-P2-285: System design depth: vibe-code-engineering restructure
- **Priority**: P2
- **Complexity**: L
- **Depends on**: None
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_vibe_code_engineering.py. (2) NEVER overwrite Chinese with English. (3) Read DB first. (4) Seed script = source of truth. (5) Formulas: \mid not |.

Restructure vibe-code-engineering to sys design depth. Current: 6.2K chars, 0 formulas, 0 Q&A -- weakest module.

REFERENCE: Read scripts/content_module_arbitration.py for depth standard.

STEPS: 1. Read DB (slug=vibe-code-engineering-patterns), dump all 8. 2. Create scripts/content_vibe_code_engineering.py. 3. Restructure as Engineering Tooling System Design (Chinese): Overview as sys design problem, Architecture component diagram, Formulas (precision/recall, throughput), Production Constraints with real numbers, 3+ Trade-off decisions, 4+ Defense Q&A, Verbal Outline 3-min and 10-min. 4. Seed and verify.

AC: All 8 sections restructured, 3+ display math, 4+ Q&A, Trade-off table 3+ decisions, Seed = Chinese source of truth, No bare |, Total >= 14K

#### T-P2-286: System design depth: ml-system-design-patterns expansion
- **Priority**: P2
- **Complexity**: L
- **Depends on**: None
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ml_system_design_patterns.py. (2) NEVER overwrite Chinese with English. (3) Read DB first. (4) Seed script = source of truth. (5) Formulas: \mid not |.

Expand ml-system-design-patterns. Current: 8.4K chars, 0 formulas, 0 Q&A -- cheat sheet level.

REFERENCE: Read scripts/content_module_arbitration.py for depth standard.

STEPS: 1. Read DB (slug=ml-system-design-patterns), dump all 8. 2. Create scripts/content_ml_system_design_patterns.py. 3. Expand each pattern (Chinese): Math formulations (NDCG, MAP, CTR lift CI, feature store freshness SLA), Concrete production examples, 4+ Defense Q&A, Failure modes per pattern, Iteration methodology. 4. Seed and verify.

AC: 5+ display math, 4+ Q&A, Failure modes per pattern, Concrete production numbers, Seed = Chinese source of truth, No bare |, Total >= 14K

#### T-P2-287: System design formula audit: all modules
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P0-280, T-P0-281, T-P1-282, T-P1-283, T-P1-284
- **Description**: CRITICAL SAFETY RULES: (1) NEVER run any module seed script unless fixing that specific module. (2) NEVER overwrite Chinese with English. (3) Formulas: \mid not |, single-line $$, blank lines between consecutive $$.

Audit all 8 system design modules for formula rendering safety.

STEPS: 1. For each of 8 modules, read content from DB. 2. Check every $ and $$ block for: bare | (should be \mid), multi-line $$ (single line), consecutive $$ without blank lines, unbalanced $. 3. If issues, fix ONLY in corresponding seed script (scripts/content_*.py). 4. Re-seed ONLY fixed modules. 5. Report findings.

AC: All 8 scanned, All bare | -> \mid, All multi-line $$ collapsed, All consecutive $$ have blank lines, Seed scripts updated for fixed modules only, ALL Chinese preserved

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

> 249 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-08** -- T-P2-279: [SYNC] Propagate DB-only content recovery lesson to template. Propagate MLInterviewPrep LESSONS.md entry [2026-04-08] to claude-code-project-template/LESSONS.md.
- [x] **2026-04-08** -- T-P2-278: [SYNC] Propagate SQLite naive-datetime timezone lesson to helixos. Propagate MLInterviewPrep LESSONS.md entry [2026-04-07] to helixos/LESSONS.md.
- [x] **2026-04-08** -- T-P2-257: [DEBT] MLInterviewPrep: Remove unused check_stop_cache/write_stop_cache from hook_utils.py. hook_utils.py defines check_stop_cache() and write_stop_cache() (lines 129-170) but no hook file imports or calls them. 
- [x] **2026-04-08** -- T-P0-281: System design depth: ranking-allocation supplement. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ranking_allocation.py. (2) N
- [x] **2026-04-08** -- T-P0-280: System design depth: llm-orchestration expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_llm_orchestration.py. (2) NE
- [x] **2026-04-07** -- T-P1-277: System Design Translation Batch 5: module 6 (41K chars). Translate module distributed-task-queue (41K) to Chinese. DB: data/mle_prep.db table system_designs slug=distributed-tas
- [x] **2026-04-07** -- T-P1-276: System Design Translation Batch 4: module 5 (36K chars). Translate module database-comparison (36K) to Chinese. DB: data/mle_prep.db table system_designs slug=database-compariso
- [x] **2026-04-07** -- T-P1-275: System Design Translation Batch 3: modules 3+4 (55K chars). Translate modules pbe-pipeline (21K) and ranking-allocation (34K) to Chinese. DB: data/mle_prep.db table system_designs.
- [x] **2026-04-07** -- T-P1-274: System Design Translation Batch 2: modules 1+2 (36K chars). Translate modules module-arbitration (20K) and llm-orchestration (16K) to Chinese. DB: data/mle_prep.db table system_des
- [x] **2026-04-07** -- T-P1-273: System Design Translation Batch 1: modules 7+8 (24K chars). Translate modules vibe-code-engineering-patterns (10K) and ml-system-design-patterns (14K) to Chinese. DB: data/mle_prep
