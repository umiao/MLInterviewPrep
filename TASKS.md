# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-490: KG-UX-04: 0-children categories act as leaves; stub badge
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-489
- **Description**: 7 depth-1 categories (SQL Fundamentals, OOD SOLID, Diffusion Models, etc.) have 0 children. Expanding them does nothing - looks broken. Also ~34 content-empty leaves need visible stub marker.

Files: src/frontend/src/pages/KnowledgeGraph.tsx, CategoryNode.tsx, LeafNode.tsx
Changes:
- In handleActivate: if meta.kind==category AND childCount==0 -> treat as leaf (setSelectedId -> open drawer)
- CategoryNode: hide v/> chevron when childCount==0; show same completeness-arc indicator as leaf
- Add small "stub" pill (text "stub", gray bg) in header when contentLength < 2000
AC:
1. Click "SQL Fundamentals" (id=191) -> FrameworkNodeDrawer opens
2. Click "Data Structures" (childCount>0) -> still expands as category
3. Nodes with contentLength<2000 show "stub" badge
4. Build + vitest pass
5. Smoke test: all 7 zero-child cats behave as leaves

#### T-P1-491: KG-UX-05: Swimlane layout - per-pillar ELK vertically stacked
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P0-488, T-P0-489
- **Description**: Current layered layout stacks 8 pillars in leftmost column causing cross-pillar overlap and visual chaos. Refactor to swimlane: each pillar gets its own horizontal lane, laid out independently; lanes stack vertically.

Files: src/frontend/src/components/kg/useKgLayout.ts, kgStyles.ts, KnowledgeGraph.tsx
Changes:
- layoutAll rewrite: group visible nodes by pillar (via nodesById.get(id).pillar). For each pillar: run ELK layered RIGHT on just that subtree, capture bbox.
- Stack lanes: lane_i.y_offset = sum(lane_[0..i-1].height) + gap(60px). Apply offset to cached positions.
- Draw lane separators: in KnowledgeGraph.tsx add an SVG overlay layer (or React Flow custom node at lane boundary) rendering dashed 1px #e2e8f0 line between adjacent lanes.
- Sort pillars by their numeric key (pillar1..pillar8) for stable order
AC:
1. Expanding Pillar A does NOT move any node in Pillar B-H (verify via console logging cached positions)
2. 8 lanes visible top-to-bottom when all pillars have nodes
3. Dashed separator lines between lanes
4. Build + vitest pass
5. Smoke test: visually "one row per topic"; expand/collapse multiple pillars - other lanes stay put

### P2 -- Nice to Have

#### T-P2-492: KG-UX-06: Bezier edges, pillar-colored, spacing polish
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P1-491
- **Description**: Current edges are orthogonal smoothstep with flat gray. Upgrade to bezier curves colored by source pillar for mindmap aesthetic.

Files: src/frontend/src/pages/KnowledgeGraph.tsx, kgStyles.ts, kgGraph.helpers.ts
Changes:
- buildReactFlowEdges: for parent relation, type="default" (bezier). Keep canonical animated.
- edgeStyleFor: parent edges stroke = styleForPillar(sourcePillarOfEdge).border with 0.7 opacity; strokeWidth: 2. Need pillar lookup in edgeStyleFor (pass src metadata via edge.data.sourcePillar).
- LAYOUT_CONFIG: rankSep 150 -> 180; nodeSep 40 -> 20 (tighter vertical, wider horizontal)
- Confirm visual: connecting lines to pillar1 nodes are slate gray, pillar6 nodes are rose, etc.
AC:
1. Parent edges render as smooth bezier curves
2. Edge color matches source-pillar color
3. Node vertical density increased; horizontal rhythm wider
4. Build + vitest pass
5. Smoke test: visually pleasing - no overlapping edges, clear color coding per topic lane

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

> 446 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-17** -- T-P1-486: [KG-VIZ-R03] Interaction: tooltip, keyboard a11y, expand-all, hover edge highlight. Post-polish interaction refinements. Scoped per user review (cut edge legend toggle, pillar filter buttons, +/-/0 shortc
- [x] **2026-04-17** -- T-P0-489: KG-UX-03: Multi-line titles, wider nodes, bigger fonts. Titles up to 82 chars get truncated. Fix: line-clamp-2, wider boxes, larger fonts.
- [x] **2026-04-17** -- T-P0-488: KG-UX-02: Preserve focus on expand/collapse (setCenter). Clicking expand reshuffles layout and user loses focus on the clicked node. Fix: after layoutAll(), if a node was just a
- [x] **2026-04-17** -- T-P0-487: KG-UX-01: Restore pan-drag and add Controls panel. Canvas is unpannable after zoom. Fix: panOnDrag=true, panOnScroll=false, zoomOnScroll=true. Add <Controls> (zoom in/out/
- [x] **2026-04-17** -- T-P0-485: [KG-VIZ-R02] Visual encoding: palette + importance/completeness indicators + polish. Visual design pass after R01 migration. Adds information-dense encoding beyond just pillar color.
- [x] **2026-04-17** -- T-P0-484: [KG-VIZ-R01] React Flow + ELK.js LR mind-map + incremental layout + URL state. FULL REWRITE of /kg. Remove Cytoscape.js, adopt React Flow + ELK.js for LR mind-map.
- [x] **2026-04-16** -- T-P2-469: [QIdx-C1] Harden LC import scripts to set family. Harden LC import scripts so new rows no longer default to family=NULL silently.
- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P1-483: [KG-VIZ-01] /kg visualization POC: Cytoscape.js + dagre (user-picked). User-picked Cytoscape.js (over React Flow / D3-Force / Sigma / vis-network). POC scope below.
- [x] **2026-04-16** -- T-P1-482: [DOCS-03] Move intermediate / generated / audits / synced into docs/staging/. Per DOCS-01 convention, move 274 generated system design fragments + audits/ + synced/ + analysis/ into docs/staging/ wi
- [x] **2026-04-16** -- T-P1-481: [DOCS-02] Migrate top-level company prep files to docs/company/<slug>/. Per proposed convention (DOCS-01), move 34 top-level company prep files into docs/company/<slug>/ subdirs.
- [x] **2026-04-16** -- T-P1-475: [KG-G-01] Translate 11 Google R1 drill docs to Chinese (company_documents 55,56,60-65,67-69). Target 11 drill docs currently in English (or largely English with some Chinese tech terms). User wants Chinese-first pr
