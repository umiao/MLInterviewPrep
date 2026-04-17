# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-484: [KG-VIZ-R01] React Flow + ELK.js LR mind-map + incremental layout + URL state
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: FULL REWRITE of /kg. Remove Cytoscape.js, adopt React Flow + ELK.js for LR mind-map.

## Core Architecture Decisions (user-reviewed)
- READ-ONLY viewer: nodesDraggable=false, nodesConnectable=false, edgesUpdatable=false
- ELK layered direction='RIGHT' (LR mind-map)
- INCREMENTAL LAYOUT: first load = full ELK pass, cache all node positions. Expand/collapse = local sub-tree layout only (parent coords locked). Use ELK `interactiveLayout: true` or compute sub-graph independently relative to parent. This preserves spatial memory.
- DEFAULT SEMI-EXPANDED: pillar + category (depth 0+1) visible on load, leaves (depth 2+) collapsed. ~40-80 nodes on first screen showing skeleton.
- Desktop-first. No mobile layout. Existing FrameworkTreeView serves as a11y / mobile fallback (already exists, keep it).

## Dependencies
REMOVE: cytoscape, cytoscape-dagre, @types/cytoscape
ADD: @xyflow/react (v12+), elkjs

## Layout Details
- 8 pillar roots (depth=0) in leftmost column
- ~40 category nodes (depth=1) in second column (visible by default)
- ~150 leaf nodes (depth=2+) collapsed behind category pills
- Click category -> expand to show its leaf children (local layout, parent stays put)
- rankSep ~150px, nodeSep ~40px
- fitView({ padding: 0.1 }) on initial load
- Edge routing: ELK orthogonal routing minimizes crossings

## Pillar Grouping
- Each pillar is a React Flow GROUP NODE with styled background container
- Children render INSIDE the group (parent field in React Flow node data)
- Group has colored left-border (4px) + light tint background + rounded corners
- Human-readable names from DB: Coding & Algorithms / ML Fundamentals & Theory / ML System Design / Applied ML & Domain-Specific / ML Infrastructure & MLOps / Deep Learning & LLM / Math & Statistics / Behavioral & Leadership

## Custom Node Components (Tailwind)
- PillarNode: group header, title + node count + expand/collapse chevron
- CategoryNode: medium card, title + child count, click to expand leaves
- LeafNode: compact card, title + click to open drawer
- All: rounded-lg, shadow-sm, font-medium text-sm (14px), max-w-[200px]
- Selected: ring-2 ring-blue-500

## Edge Styling
- 'parent' edges: solid #cbd5e1 (slate-300), 1.5px, smooth step path, no arrow
- 'canonical' edges: solid #16a34a (green-600), 2px, animated dash, small arrow
- 'see_also' / 'drill' / others: DEFAULT opacity 0.3, no legend toggle. On hover of a node, highlight all connected edges to full opacity.
- Cross-pillar edges visible only when BOTH endpoint pillars/categories are expanded

## Search Interaction (must be well-defined)
Search box (top-right): on typing:
1. Auto-expand any collapsed pillar/category containing matches
2. Zoom + pan to center on first match
3. Highlight matching nodes (ring-2 ring-yellow-400)
4. Non-matching nodes: opacity 0.2 (not hidden)
5. Clear search: restore original expand state + fitView
6. Debounce 300ms on keystroke

## URL State / Deep Linking (from day 1)
- URL params: `?node={id}&expanded={pillar1,pillar2.supervised_learning,...}`
- On load: parse URL, expand specified paths, select + zoom to node if specified
- On node click / expand: update URL via replaceState (no history spam)
- Enables sharing "look at this concept" links

## Performance Targets
- First render (201 nodes, semi-expanded): <1s
- Pan/zoom: 60fps
- Expand/collapse: <200ms (local layout only)
- Ceiling: 500 nodes still usable (progressive loading deferred to P1 if needed)

## Files
- src/frontend/src/pages/KnowledgeGraph.tsx — full rewrite
- src/frontend/src/pages/kgGraph.helpers.ts — rewrite for React Flow format
- src/frontend/src/components/kg/PillarNode.tsx
- src/frontend/src/components/kg/CategoryNode.tsx
- src/frontend/src/components/kg/LeafNode.tsx
- src/frontend/src/components/kg/useKgLayout.ts — ELK layout hook with caching + incremental
- src/frontend/src/components/kg/kgStyles.ts — palette + config
- src/frontend/src/components/kg/useKgUrlState.ts — URL sync hook
- package.json — dep changes

## Acceptance Criteria
1. /kg renders LR mind-map (not flat line, not top-down)
2. Default: 8 pillars + ~40 categories visible (semi-expanded), leaves collapsed
3. Expand category -> leaves appear to right, parent stays in place (incremental layout)
4. Click leaf -> FrameworkNodeDrawer opens from right
5. Search auto-expands + zooms + highlights matches
6. URL reflects selected node + expanded state; reloading URL restores view
7. Edges: parent=gray solid, canonical=green animated, others=faded 0.3 opacity
8. Hover node -> connected edges highlight to full opacity
9. Read-only: no drag, no connect, no edit
10. fitView on load; first render <1s
11. npm run build 0 TS errors; vitest passes
12. Playwright screenshot saved to logs/ showing readable LR tree
13. Commit: [KG-VIZ-R01] React Flow + ELK.js LR mind-map with incremental layout + URL state

## Non-Goals
- No user editing / drag-n-drop / add-node UI (all changes through Claude)
- No force-directed layout (ELK layered only)
- No mobile-specific layout (desktop-first; FrameworkTreeView is mobile fallback)
- No Learning Path overlay (defer; reserve path_id field for future)
- No edge legend toggle / pillar filter buttons (cut per review)
- Do NOT remove FrameworkTreeView or FrameworkTreemap pages
- Do NOT touch backend /api/kg/graph

#### T-P0-485: [KG-VIZ-R02] Visual encoding: palette + importance/completeness indicators + polish
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-484
- **Description**: Visual design pass after R01 migration. Adds information-dense encoding beyond just pillar color.

## Pillar Color Palette (curated, Tailwind-derived)
  Coding & Algorithms          -> slate-600 (#475569) border + slate-50 bg
  ML Fundamentals & Theory     -> amber-600 (#d97706) border + amber-50 bg
  ML System Design             -> emerald-600 (#059669) border + emerald-50 bg
  Applied ML & Domain-Specific -> sky-600 (#0284c7) border + sky-50 bg
  ML Infrastructure & MLOps    -> violet-600 (#7c3aed) border + violet-50 bg
  Deep Learning & LLM          -> rose-600 (#e11d48) border + rose-50 bg
  Math & Statistics             -> teal-600 (#0d9488) border + teal-50 bg
  Behavioral & Leadership      -> orange-600 (#ea580c) border + orange-50 bg

## Visual Encoding Beyond Color (per user review)
Color is already bound to pillar. THREE additional encodings:

1. IMPORTANCE (node size):
   - Base size 1.0x (most nodes)
   - 1.2x for nodes with >5 concept_links edges (moderate connectivity)
   - 1.5x for nodes with >10 edges (hub nodes)
   - Subtle variation; must not break layered rhythm
   - Size computed from backend data (add edge_count to /api/kg/graph node payload)

2. COMPLETENESS (corner arc indicator):
   - iOS-style small circular arc in top-right corner of each leaf node
   - Arc fill = content_length / 10000 (capped at 100%)
   - Empty (0%): thin ring outline only
   - Partial: partial arc fill in pillar color
   - Full (>10000 chars): complete filled ring + subtle checkmark
   - Stub nodes (<2000 chars): dashed border on the whole node card (additional cue)

3. CONNECTIVITY (thicker border) — P1 DEFERRED:
   - Hub nodes (>10 edges) get 2px border instead of 1px
   - Defer to R03 to avoid overloading this task

## Node Component Specs
- PillarNode (semi-expanded): 240x48px, rounded-xl, left-4px colored border, white bg, shadow-md, title bold 15px + "(N)" count. Chevron for expand/collapse.
- CategoryNode: 200x40px, rounded-lg, border-l-2 colored, white bg, shadow-sm, 13px semi-bold. Child count badge.
- LeafNode: 180x36px (base, scales with importance), rounded-md, border-l-2, white bg, 12px. Corner arc indicator. Dashed border if stub.
- Selected: ring-2 ring-blue-500 ring-offset-2
- Hover: shadow-lg transition-shadow duration-150

## Edge Design
- Parent: stroke #cbd5e1, strokeWidth 1.5, smooth step, no arrow
- Cross-links: stroke by relation color, strokeWidth 1, default opacity 0.3, animated on hover

## Background + Minimap
- React Flow Background: dots variant, gap=20, color=#f1f5f9
- Canvas bg: white
- MiniMap: bottom-right, 150x100px, node colors match pillar

## Backend Change (small)
- Add `edge_count` field to /api/kg/graph node response: COUNT of concept_links rows where node is src or dst. Used for importance sizing.

## Acceptance Criteria
1. 8 pillar colors match spec (not generic rainbow)
2. Node size varies by importance (1.0x/1.2x/1.5x) — visually apparent but not jarring
3. Corner arc shows completeness on leaf nodes
4. Stub nodes (<2000 chars) have dashed border
5. Hover/selected states smooth
6. MiniMap with pillar colors
7. Background dots
8. Before/after Playwright screenshots saved to logs/
9. npm run build 0 TS errors
10. Commit: [KG-VIZ-R02] Visual encoding: palette + importance sizing + completeness arc

DEPENDS ON: T-P0-484 (React Flow migration)

### P1 -- Should Have (agentic intelligence)

#### T-P1-486: [KG-VIZ-R03] Interaction: tooltip, keyboard a11y, expand-all, hover edge highlight
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-485
- **Description**: Post-polish interaction refinements. Scoped per user review (cut edge legend toggle, pillar filter buttons, +/-/0 shortcuts).

## Features

1. HOVER TOOLTIP:
   - Floating div positioned above node on mouseenter
   - Content: Title (bold) / Pillar name (colored badge) / Content: "8,234 chars" or "Stub" / "Click to view"
   - Disappears on mouseleave
   - Z-index above edges

2. KEYBOARD NAVIGATION (a11y baseline):
   - Tab: cycle through visible nodes in tree order (left-to-right, top-to-bottom)
   - Enter on focused node: open FrameworkNodeDrawer
   - Escape: close drawer + deselect
   - Cut: +/-/0 zoom shortcuts (not a11y critical)

3. EXPAND / COLLAPSE ALL:
   - Button in page header: "Expand All" / "Collapse All"
   - Updates URL state accordingly
   - Re-runs incremental layout for newly visible subtrees

4. HOVER EDGE HIGHLIGHT:
   - On hover any node: all edges connected to that node go from opacity 0.3 -> 1.0
   - Connected neighbor nodes get subtle highlight (ring-1 ring-gray-300)
   - On mouseleave: revert

5. CONNECTIVITY BORDER (deferred from R02):
   - Nodes with >10 concept_links edges get 2px border (hub indicator)

## NOT in scope (per review)
- Edge legend toggle with checkboxes — CUT (replaced by hover highlight)
- Pillar filter buttons — CUT
- +/-/0 zoom shortcuts — CUT
- Learning Path overlay — DEFERRED (reserve path_id field only)
- Progressive loading — DEFERRED to future task if node count exceeds 500
- Mobile layout — desktop-first declared

## Acceptance Criteria
1. Tooltip shows on hover with correct content
2. Tab/Enter/Escape keyboard flow works
3. Expand/Collapse All button toggles all pillars
4. Edge hover highlight works (0.3 -> 1.0 on connected edges)
5. Hub nodes (>10 edges) have thicker border
6. npm run build 0 TS errors
7. Commit: [KG-VIZ-R03] Interactions: tooltip, keyboard a11y, expand-all, hover highlight

DEPENDS ON: T-P0-485

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

- [x] **2026-04-16** -- T-P2-469: [QIdx-C1] Harden LC import scripts to set family. Harden LC import scripts so new rows no longer default to family=NULL silently.
- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P1-483: [KG-VIZ-01] /kg visualization POC: Cytoscape.js + dagre (user-picked). User-picked Cytoscape.js (over React Flow / D3-Force / Sigma / vis-network). POC scope below.
- [x] **2026-04-16** -- T-P1-482: [DOCS-03] Move intermediate / generated / audits / synced into docs/staging/. Per DOCS-01 convention, move 274 generated system design fragments + audits/ + synced/ + analysis/ into docs/staging/ wi
- [x] **2026-04-16** -- T-P1-481: [DOCS-02] Migrate top-level company prep files to docs/company/<slug>/. Per proposed convention (DOCS-01), move 34 top-level company prep files into docs/company/<slug>/ subdirs.
- [x] **2026-04-16** -- T-P1-475: [KG-G-01] Translate 11 Google R1 drill docs to Chinese (company_documents 55,56,60-65,67-69). Target 11 drill docs currently in English (or largely English with some Chinese tech terms). User wants Chinese-first pr
