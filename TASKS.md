# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-561: [T-GOLD-09] Golden Collection aggregator page (backend /golden endpoint + frontend page)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P2-560
- **Description**: Backend: add GET /golden router endpoint that unions rows from the 3 tables where is_golden=true, normalized into a uniform response:
  [{ id, item_type: 'framework_node'|'behavioral_example'|'company_document', title, preview (first 200 chars of content/description), golden_at, url_path (for deep-linking: e.g. '/ml-fundamentals?cat=...&slug=...' or '/behavioral?id=...' or '/companies/<id>/documents/<id>') }]
  Sort by golden_at DESC. Implement in src/backend/routers/golden.py; mount in main.py.

Frontend: create src/frontend/src/pages/GoldenCollection.tsx. Three tabs (framework_nodes / behavioral / company_docs) + 'All' tab at position 0 (matching MLFundamentals pattern). Each card is clickable and navigates to the url_path from the API. Empty state per tab: 'No items marked golden in this category yet.'

Sidebar: add { to: '/golden', label: 'Golden' } nav item near the top (above Framework or between Fundamentals and LeetCode).

AC: mark 3+ items across 3 different tables; /golden page shows all with correct per-tab filtering; clicking a card deep-links to the correct origin page; empty tabs display the friendly message.

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

> 510 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-20** -- T-P2-560: [T-GOLD-08] Company docs integration: drawer toggle + card visuals (no filter on index pages). Add <GoldenToggleButton itemType='company_document' /> to whatever view renders a company_document in full (prep note pa
- [x] **2026-04-20** -- T-P2-559: [T-GOLD-07b] Behavioral UI integration: drawer toggle + card visuals + filter. Execute the plan from T-GOLD-07a. Expected work surface:
- [x] **2026-04-20** -- T-P2-558: [T-GOLD-07a] Discovery: scan Behavioral UI for drawer + toggle insertion points. Research-only task, NO code writes. Read:
- [x] **2026-04-20** -- T-P2-551: [T-MLF-11] Google Prep Hub id=53 cross-link to /ml-fundamentals. Via scripts/seed_google_hub_mlf_crosslink.py (idempotent with sha256 guard):
- [x] **2026-04-20** -- T-P1-557: [T-GOLD-06] Integrate into MLFundamentals.tsx cards + ?golden=1 URL filter. Edit src/frontend/src/pages/MLFundamentals.tsx:
- [x] **2026-04-20** -- T-P1-556: [T-GOLD-05] Integrate GoldenToggleButton into FrameworkNodeDrawer (audit placement first). BEFORE coding: take a screenshot of the current FrameworkNodeDrawer header (src/frontend/src/components/framework/Framew
- [x] **2026-04-20** -- T-P1-555: [T-GOLD-04] goldenCardClass(isGolden) helper + golden [star] badge for card lists. Create src/frontend/src/utils/goldenStyle.ts exporting:
- [x] **2026-04-20** -- T-P1-554: [T-GOLD-03] Frontend <GoldenToggleButton> shared component + orange color tokens. Create src/frontend/src/components/ui/GoldenToggleButton.tsx:
- [x] **2026-04-20** -- T-P1-553: [T-GOLD-02] Backend PUT endpoints accept is_golden; endpoint-layer golden_at auto-refresh on false->true. Extend three existing PUT endpoints (do NOT add new ones):
- [x] **2026-04-20** -- T-P1-552: [T-GOLD-01] Schema + migration: is_golden + golden_at on framework_nodes / behavioral_examples / company_documents + docs/golden_marker.md. Add curation columns to three tables (single Alembic migration or one-shot Python migration script under scripts/ -- fol
- [x] **2026-04-20** -- T-P1-550: [T-MLF-10] Content QA pass — acronyms, formula context, term definitions. Walk each of 27 leaf descriptions and verify:
- [x] **2026-04-20** -- T-P1-549: [T-MLF-09] KaTeX/drawer smoke test — all 27 drawers. Run npm run dev; manually open every one of the 27 question drawers; record rendering status in docs/ml_fundamentals_smo
- [x] **2026-04-20** -- T-P0-546: [T-MLF-06d] T3 X-depth batch #23/#24/#26/#27 (Tokenization, Chinchilla, CLT/LLN, A/B test). X-depth: keep original structure, expand all acronyms on first use, fix formula context holes.
- [x] **2026-04-20** -- T-P0-545: [T-MLF-06c] T3 Y-depth #25 MLE vs MAP (upgraded from X to Y). Upgrade #25 from original X-depth (acronym-only) to full Y-depth.
- [x] **2026-04-20** -- T-P0-544: [T-MLF-06b] T3 Y-depth #22 MoE routing + load balancing (template from zeta1). Apply the calibrated Y-depth template (from zeta1 review) to #22 MoE.
- [x] **2026-04-19** -- T-P2-536: T-GOOG-REORG-PREFIX: Add [R1/Bucket] prefix to 14 Tier-3 doc titles for visual grouping on /prep. ## Context
- [x] **2026-04-19** -- T-P2-533: T-GOOG-CN-DRILL-BATCH: Batch-upgrade 11 Google drill docs + id=72 Bridge to ≥50% CN prose (from 30-47%). ## Context
- [x] **2026-04-19** -- T-P2-521: [DEBT] MLInterviewPrep: Customize CLAUDE.md.local with project overview and tech stack. CLAUDE.md.local still has template placeholder text (generated from claude-code-project-template). Specific gaps:
- [x] **2026-04-19** -- T-P2-517: KG-UX-18: Drawer rendering polish (GFM, rehype-raw, blockquote + callout styling). ## Context
- [x] **2026-04-19** -- T-P1-535: T-GOOG-REORG-SLIM51: Slim id=51 by replacing Round 1 ML-dims + Round 2 G&L-attrs with db://38 refs (~6213→~4500 chars). ## Context
