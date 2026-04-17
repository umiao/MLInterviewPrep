# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-484: [KG-VIZ-R01] Migrate /kg from Cytoscape to React Flow + ELK.js (LR mind-map)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: COMPLETE REWRITE of /kg visualization. Remove Cytoscape.js, adopt React Flow + ELK.js for a left-to-right mind-map layout.

READ-ONLY POLICY: The KG page is a VIEWER only. No user drag-n-drop, no rearranging, no editing. All structural changes happen through Claude (task_db / seed scripts). React Flow's interactiveElements, nodesDraggable, nodesConnectable, edgesUpdatable all set to FALSE. Only pan/zoom + click-to-view allowed.

CURRENT STATE (files to replace):
- src/frontend/src/pages/KnowledgeGraph.tsx (Cytoscape imperative init, ~100 lines)
- src/frontend/src/pages/kgGraph.helpers.ts (Cytoscape ElementDefinition builder)
- Backend src/backend/routers/kg.py stays unchanged (GET /api/kg/graph returns nodes+edges)

DEPENDENCY CHANGES:
- REMOVE: cytoscape, cytoscape-dagre, @types/cytoscape
- ADD: @xyflow/react (React Flow v12+), elkjs (ELK WASM layout engine)
- Optional: @xyflow/react already includes Minimap, Controls, Background components

LAYOUT:
- ELK layered algorithm with direction='RIGHT' (left-to-right)
- Root nodes (8 pillars, depth=0) on the leftmost column
- Category nodes (depth=1) as second column
- Leaf nodes (depth=2+) as third+ column
- Edge routing: ELK handles orthogonal edge routing to minimize crossings
- rankSep ~150px (horizontal gap between columns), nodeSep ~40px (vertical gap)
- After layout, call reactFlowInstance.fitView({ padding: 0.1 }) for auto-fit on load

NODE HIERARCHY (from verified DB query):
- 8 pillar roots: Coding & Algorithms / ML Fundamentals & Theory / ML System Design / Applied ML & Domain-Specific / ML Infrastructure & MLOps / Deep Learning & LLM Specialization / Math & Statistics Foundations / Behavioral & Leadership
- ~40 category nodes (depth=1)
- ~150 leaf nodes (depth=2+)
- Parent-child edges from framework_nodes.parent_id field

PILLAR GROUPING:
- Each pillar is a React Flow GROUP NODE (type='group') with styled background
- Children of each pillar rendered INSIDE the group (parent field set in React Flow node data)
- Group node has colored left border (4px), light-tinted background, rounded corners
- Group header shows: pillar icon/emoji-free label + "(N nodes)" count
- DEFAULT STATE: collapsed (only pillar group node visible as a pill/card)
- Expand on click: shows category → leaf tree inside the group

CUSTOM NODE COMPONENTS (React TSX with Tailwind):
- PillarNode: group header with title + node count + expand/collapse toggle + progress bar
- CategoryNode: medium card with title + child count
- LeafNode: compact card with title + content_length indicator (thin bar) + click handler
- All nodes: rounded-lg, shadow-sm, border, font-medium text-sm (14px), max-w-[200px]
- Selected node: ring-2 ring-blue-500

EDGE STYLING:
- 'parent' edges: solid gray (#94a3b8), 1.5px, bezier, no arrow
- 'canonical' edges: solid green (#16a34a), 2px, animated dash, small arrow
- 'see_also' edges: dashed blue (#3b82f6), 1px
- 'drill' edges: dotted purple (#8b5cf6), 1px
- Cross-pillar edges only visible when BOTH endpoint pillars are expanded

INTERACTIONS:
- Click leaf/category node -> open FrameworkNodeDrawer (reuse existing, right side slide-over)
- Click pillar group -> toggle expand/collapse
- Pan: mouse drag on background
- Zoom: scroll wheel
- Auto-fit on load: fitView()
- Search box (top-right): filters nodes by title; non-matching nodes hidden (not just dimmed)

FILES TO CREATE/MODIFY:
- src/frontend/src/pages/KnowledgeGraph.tsx — full rewrite
- src/frontend/src/pages/kgGraph.helpers.ts — rewrite for React Flow node/edge format
- src/frontend/src/components/kg/PillarNode.tsx — custom pillar group component
- src/frontend/src/components/kg/ConceptNode.tsx — custom leaf/category component
- src/frontend/src/components/kg/kgStyles.ts — color palette + ELK config
- package.json — dep changes

ACCEPTANCE CRITERIA:
1. /kg renders 201 nodes in LEFT-TO-RIGHT tree layout (not top-down, not flat line)
2. 8 pillar groups visible with human-readable titles (from DB, NOT "pillar1")
3. Default: all pillars collapsed (8 pill cards in a column on left)
4. Click pillar -> expands to show category→leaf subtree flowing rightward
5. Click any leaf/category -> FrameworkNodeDrawer opens from right
6. concept_links edges rendered between nodes (canonical=green, see_also=blue)
7. Cross-pillar edges visible when both pillars expanded
8. Search filters by title
9. fitView on load — no manual zoom needed to see content
10. nodesDraggable=false, nodesConnectable=false (read-only)
11. npm run build 0 TS errors
12. frontend vitest passes (update/add KG tests)
13. Bundle delta: cytoscape removal ~-107KB, React Flow addition ~+40KB + ELK ~+200KB (net ~+130KB acceptable)
14. Playwright screenshot shows readable LR mind-map (take screenshot in test or commit message)
15. Commit: [KG-VIZ-R01] Migrate /kg to React Flow + ELK.js LR mind-map

NON-GOALS:
- No user editing / drag-n-drop / add-node UI
- No 3D visualization
- No force-directed layout (use ELK layered only)
- No company-lens filter (defer to R04)
- Do not touch backend /api/kg/graph endpoint
- Do not remove FrameworkTreeView or FrameworkTreemap pages

#### T-P0-485: [KG-VIZ-R02] Visual design system: pillar palette + node components + collapsed defaults
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-484
- **Description**: Polish the visual design of /kg after R01 migration lands. This task focuses on aesthetics, not functionality.

PILLAR COLOR PALETTE (curated, not generic rainbow):
Proposed mapping (Tailwind-derived, high contrast, colorblind-friendly pairs):

  Coding & Algorithms          -> slate-600 (#475569) border + slate-50 bg
  ML Fundamentals & Theory     -> amber-600 (#d97706) border + amber-50 bg
  ML System Design             -> emerald-600 (#059669) border + emerald-50 bg
  Applied ML & Domain-Specific -> sky-600 (#0284c7) border + sky-50 bg
  ML Infrastructure & MLOps    -> violet-600 (#7c3aed) border + violet-50 bg
  Deep Learning & LLM          -> rose-600 (#e11d48) border + rose-50 bg
  Math & Statistics             -> teal-600 (#0d9488) border + teal-50 bg
  Behavioral & Leadership      -> orange-600 (#ea580c) border + orange-50 bg

NODE DESIGN SPEC:
- PillarNode (collapsed): 240x48px, rounded-xl, left-4px colored border, white bg, shadow-md. Title bold 15px + "(N)" count right-aligned. Chevron-right icon for expand hint.
- PillarNode (expanded): same header + colored bg-{pillar}-50 container wrapping children
- CategoryNode: 200x40px, rounded-lg, border-l-2 colored, white bg, shadow-sm. Title 13px semi-bold. Count badge "(N leaves)".
- LeafNode: 180x36px, rounded-md, border-l-2 colored, white bg. Title 12px. Bottom thin progress bar (content_length / 10000 capped at 100%). If content_length < 2000: ghost/dashed border (stub indicator).
- Selected node: ring-2 ring-blue-500 ring-offset-2
- Hover: shadow-lg transition-shadow duration-150

EDGE DESIGN:
- Parent edges: stroke #cbd5e1 (slate-300), strokeWidth 1.5, no arrow, smooth step path
- Cross-link edges: stroke by relation color (green/blue/purple per R01), strokeWidth 1, animated=true (moving dash), markerEnd small arrow

TYPOGRAPHY:
- All node text: Inter or system-ui, antialiased
- No CJK in node labels (all pillar/category/leaf titles are English in DB)
- Search input: rounded-lg, border, px-3 py-2, placeholder "Search nodes..."

BACKGROUND:
- React Flow Background component: dots variant, gap=20, color=#f1f5f9 (slate-100)
- Canvas bg: white (#ffffff)

MINIMAP:
- React Flow MiniMap component, bottom-right corner, 150x100px
- Node colors match pillar colors

ACCEPTANCE CRITERIA:
1. Pillar colors match spec (not generic rainbow)
2. Collapsed pillar pills are visually distinct and readable
3. Stub nodes (content < 2000 chars) have visual indicator (dashed border or ghost style)
4. Hover/selected states smooth and visible
5. MiniMap renders in corner with correct pillar colors
6. Background dots visible
7. Screenshot comparison: before (flat line) vs after (LR tree with polish) — save both to logs/
8. Commit: [KG-VIZ-R02] Visual design: pillar palette, node polish, collapsed defaults

DEPENDS ON: KG-VIZ-R01 (React Flow migration must land first)

### P1 -- Should Have (agentic intelligence)

#### T-P1-486: [KG-VIZ-R03] Interaction refinements: tooltip, legend, keyboard nav, edge toggle
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-485
- **Description**: Post-polish interaction improvements for /kg.

FEATURES:
1. HOVER TOOLTIP: On node hover, show floating tooltip (absolute positioned div) with:
   - Title (bold)
   - Pillar name (colored badge)
   - Content length: "8,234 chars" or "Stub (empty)" if < 100
   - "Click to view details"
   - Tooltip disappears on mouse leave, positioned above node

2. EDGE TYPE LEGEND: Small legend panel (bottom-left, semi-transparent bg):
   - Line samples + labels for each edge type: Parent / Canonical / See Also / Drill / Absorbed From
   - Toggleable: click edge type to show/hide those edges

3. KEYBOARD NAVIGATION:
   - Tab: cycle through nodes in tree order
   - Enter on focused node: open drawer
   - Escape: close drawer, deselect node
   - +/-: zoom in/out
   - 0: fitView (reset zoom)

4. EXPAND/COLLAPSE ALL:
   - Button in header: "Expand All" / "Collapse All" toggle
   - Ctrl+E shortcut

5. PILLAR FILTER:
   - Row of pillar toggle buttons below search
   - Click to hide/show entire pillar (useful when focusing on one domain)
   - Active pillars have filled colored badge, inactive are grayed outline

ACCEPTANCE CRITERIA:
1. Hover tooltip shows on any node with correct info
2. Edge legend toggles work (hiding canonical edges hides green lines)
3. Tab + Enter keyboard flow works end-to-end
4. Expand/Collapse All button works
5. Pillar filter buttons correctly hide/show subtrees + re-layout
6. npm run build 0 TS errors
7. Commit: [KG-VIZ-R03] Interaction refinements: tooltip, legend, keyboard, pillar filter

DEPENDS ON: KG-VIZ-R02 (visual design must land first)
NON-GOALS: No user editing. No export (SVG/PNG). No undo/redo.

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
