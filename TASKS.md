# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-288: Create HTML diagrams + PNG screenshots for vibe-code-engineering and ml-system-design-patterns
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Two system design modules (vibe-code-engineering-patterns, ml-system-design-patterns) have diagram_filename set in DB but no actual PNG or HTML files on disk. The other 6 modules have both HTML sources in src/frontend/public/static/system-designs/html/ and PNG screenshots.

STEPS:
1. Read existing HTML diagrams for reference style (e.g., module_arbitration.html, distributed_task_queue.html). They use inline CSS, boxes, arrows, color-coded sections.
2. Read the architecture section of vibe-code-engineering-patterns and ml-system-design-patterns from DB to understand what to diagram.
3. Create src/frontend/public/static/system-designs/html/vibe_code_engineering.html -- architecture diagram for the engineering tooling system design (data extraction pipeline, secret detection, scraping components).
4. Create src/frontend/public/static/system-designs/html/ml_system_design_patterns.html -- architecture diagram for ML system design patterns (feature store, model serving, A/B testing, monitoring components).
5. Add both new filenames to DIAGRAMS list in scripts/generate_diagram_screenshots.py.
6. Run: python scripts/generate_diagram_screenshots.py to generate PNG screenshots.
7. Verify PNG files exist at the expected paths and are non-zero size.

AC:
- [ ] vibe_code_engineering.html created with architecture diagram
- [ ] ml_system_design_patterns.html created with architecture diagram
- [ ] generate_diagram_screenshots.py updated with both new entries
- [ ] PNG screenshots generated and exist on disk
- [ ] Diagrams render correctly in HTML (open in browser to verify)

#### T-P1-289: Replace top bookmark nav with persistent right-side TOC in SystemDesignDetail
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: SystemDesignDetail.tsx currently uses a sticky top bookmark nav bar for section navigation. After clicking a section, the nav stays at the top and the user loses context of where they are in the document. The user wants a persistent right-side TOC sidebar like PrepNotesPage uses.

REFERENCE IMPLEMENTATION: PrepNotesPage.tsx uses DynamicTocSidebar (src/frontend/src/components/ui/DynamicTocSidebar.tsx) which:
- Shows on the right side of the content
- Highlights the currently visible section via IntersectionObserver
- Is always visible (sticky) while scrolling
- Supports collapsible h1/h2 hierarchy

CURRENT: SystemDesignDetail.tsx (line 215-231) has a sticky top nav bar with horizontal buttons for each section. It uses IntersectionObserver (line 76-113) and scrollToSection callback.

STEPS:
1. Read DynamicTocSidebar.tsx and PrepNotesPage.tsx to understand the right-side TOC pattern.
2. Read SystemDesignDetail.tsx to understand current layout structure.
3. Modify SystemDesignDetail.tsx:
   a. Remove the sticky top bookmark nav (lines 215-231).
   b. Change the content area to a two-column flex layout: main content (left, flex-1) + TOC sidebar (right, fixed width ~200px).
   c. Either reuse DynamicTocSidebar or create a SystemDesignTocSidebar that uses the existing SECTIONS/SECTION_LABELS with the same sticky right-side pattern.
   d. The TOC should highlight the currently visible section and support click-to-scroll.
4. Verify: TypeScript compiles cleanly (npx tsc --noEmit).
5. Manual check: the TOC stays visible while scrolling through long sections.

AC:
- [ ] Top bookmark nav removed
- [ ] Right-side TOC sidebar added (persistent/sticky while scrolling)
- [ ] Current section highlighted in TOC
- [ ] Click TOC item scrolls to section
- [ ] TypeScript compiles cleanly
- [ ] Layout works on both desktop and mobile (TOC hidden on mobile or responsive)

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

## Completed Tasks

> 249 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-08** -- T-P2-287: System design formula audit: all modules. CRITICAL SAFETY RULES: (1) NEVER run any module seed script unless fixing that specific module. (2) NEVER overwrite Chin
- [x] **2026-04-08** -- T-P2-286: System design depth: ml-system-design-patterns expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ml_system_design_patterns.py
- [x] **2026-04-08** -- T-P2-285: System design depth: vibe-code-engineering restructure. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_vibe_code_engineering.py. (2
- [x] **2026-04-08** -- T-P2-279: [SYNC] Propagate DB-only content recovery lesson to template. Propagate MLInterviewPrep LESSONS.md entry [2026-04-08] to claude-code-project-template/LESSONS.md.
- [x] **2026-04-08** -- T-P2-278: [SYNC] Propagate SQLite naive-datetime timezone lesson to helixos. Propagate MLInterviewPrep LESSONS.md entry [2026-04-07] to helixos/LESSONS.md.
- [x] **2026-04-08** -- T-P2-257: [DEBT] MLInterviewPrep: Remove unused check_stop_cache/write_stop_cache from hook_utils.py. hook_utils.py defines check_stop_cache() and write_stop_cache() (lines 129-170) but no hook file imports or calls them. 
- [x] **2026-04-08** -- T-P1-284: System design depth: pbe-pipeline expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_pbe_pipeline.py. (2) NEVER o
- [x] **2026-04-08** -- T-P1-283: System design depth: database-comparison supplement. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_database_comparison.py. (2) 
- [x] **2026-04-08** -- T-P1-282: System design depth: distributed-task-queue add Defense Q&A. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_distributed_task_queue.py. (
- [x] **2026-04-08** -- T-P0-290: Restructure System Design landing page with sub-sections (eBay Projects + Interview Prep). The current System Design landing page (SystemDesignList.tsx) only shows eBay project modules. The user needs it restruc
- [x] **2026-04-08** -- T-P0-281: System design depth: ranking-allocation supplement. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ranking_allocation.py. (2) N
- [x] **2026-04-08** -- T-P0-280: System design depth: llm-orchestration expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_llm_orchestration.py. (2) NE
- [x] **2026-04-07** -- T-P1-277: System Design Translation Batch 5: module 6 (41K chars). Translate module distributed-task-queue (41K) to Chinese. DB: data/mle_prep.db table system_designs slug=distributed-tas
- [x] **2026-04-07** -- T-P1-276: System Design Translation Batch 4: module 5 (36K chars). Translate module database-comparison (36K) to Chinese. DB: data/mle_prep.db table system_designs slug=database-compariso
- [x] **2026-04-07** -- T-P1-275: System Design Translation Batch 3: modules 3+4 (55K chars). Translate modules pbe-pipeline (21K) and ranking-allocation (34K) to Chinese. DB: data/mle_prep.db table system_designs.
- [x] **2026-04-07** -- T-P1-274: System Design Translation Batch 2: modules 1+2 (36K chars). Translate modules module-arbitration (20K) and llm-orchestration (16K) to Chinese. DB: data/mle_prep.db table system_des
- [x] **2026-04-07** -- T-P1-273: System Design Translation Batch 1: modules 7+8 (24K chars). Translate modules vibe-code-engineering-patterns (10K) and ml-system-design-patterns (14K) to Chinese. DB: data/mle_prep
