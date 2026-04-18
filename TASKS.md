# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-501: KG-UX-10: Empty-content nodes skip drawer (tri-state click) + hasContent util
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ## Problem
Clicking L1/L2 organizational nodes (e.g. id=1 Coding & Algorithms) opens an empty drawer because the current handleActivate() only checks node kind/childCount, not whether description has content. DB survey (2026-04-18): 8/8 L1 + 34/41 L2 have empty description; 0 borderline stub cases (<30 chars).

## Solution: tri-state click behavior (replaces current leaf-vs-category check)

| Node content | Children | Click behavior |
|---|---|---|
| has content | any | open drawer (current behavior) |
| no content | 0 | focus animation only (NEW — no drawer) |
| no content | >0, collapsed | expand (current behavior) |
| no content | >0, expanded | collapse (NEW explicit — currently no-op) |

## Deliverables
1. New util `src/frontend/src/components/framework/hasContent.ts` exporting `hasContent(node): boolean`. Implementation: `node.content_length > 0`. This is the ONLY source of truth for "has drawer content". Add small unit test.
2. Refactor `handleActivate()` in `src/frontend/src/pages/KnowledgeGraph.tsx` to use `hasContent()` and implement the tri-state matrix above.
3. Focus animation for no-content leaf case:
   - `rf.setCenter(cx, cy, { zoom: Math.max(rf.getZoom(), 1.0), duration: 200 })` — preserves user's current zoom if already >=1.0, only zooms IN never OUT
   - CSS pulse keyframe animation on target node (200-300ms ring expansion) applied via temporary class — zoom-independent feedback so even no-op setCenter gives visible confirmation
4. Hover affordance: empty-description nodes set title attribute to "无内容 · 点击聚焦" (so cursor tooltip appears). No visual style change.

## Acceptance Criteria
- [ ] Unit test: `hasContent({content_length: 0})` → false; `hasContent({content_length: 1})` → true
- [ ] Journey: click id=1 Coding & Algorithms (L1 empty) → no drawer, node pulses, viewport centers on it
- [ ] Journey: click an empty L2 category with children (collapsed) → expands, no drawer
- [ ] Journey: click same empty L2 category again (now expanded) → collapses, no drawer
- [ ] Journey: click any L3 leaf (e.g. id=42 STAR) → drawer opens with content as before
- [ ] Journey: hover over empty node → cursor tooltip shows "无内容 · 点击聚焦"
- [ ] `npm run build` 0 TS errors
- [ ] Manually verify in browser at http://localhost:5173/kg: all 4 journeys above

#### T-P1-502: KG-UX-14: Initial fitView maxZoom cap + URL deeplink direct-focus
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ## Problem
User reports: default zoom when entering /kg page is too small — hard to read nodes. Current: KnowledgeGraph.tsx:338 calls `rf.fitView({ padding: 0.1, duration: 300 })` which zooms out to fit the entire swimlane layout. With wide pillar-per-lane layout the nodes become tiny. Additionally, deep-linking via `?node=n42` does fitView first then setCenter, causing a visible zoom-out-then-zoom-in jitter.

## Solution

### Part A: Cap initial fitView zoom
Change KnowledgeGraph.tsx:338 from:
```
rf.fitView({ padding: 0.1, duration: 300 });
```
to:
```
rf.fitView({ padding: 0.15, maxZoom: 1.0, duration: 300 });
```
Rationale: `maxZoom: 1.0` prevents zoom-out to fit huge graphs; `padding: 0.15` gives slight breathing room. React Flow's `minZoom=0.2, maxZoom=2.0` bounds still apply.

### Part B: Deeplink direct-focus (skip fitView)
When `?node=<id>` is present in URL on mount, skip the initial fitView entirely and go straight to setCenter on that node at `zoom: 1.0`. Implementation: read URL state in the initialFitDone branch (L336-340) — if a target node is parseable from URL, setCenter to its position instead of fitView.

## Acceptance Criteria
- [ ] Journey: load /kg cold (no URL params) → nodes are readable (not shrunk to fit). Pillar node titles legible without manual zoom-in.
- [ ] Journey: load /kg?node=n42 → viewport centers directly on id=42 at zoom 1.0, no visible fitView zoom-out first
- [ ] Journey: load /kg?node=n42 with expanded ancestors in URL → expansion + focus both work, node visible on mount
- [ ] Journey: no regression — clicking a pillar header still expands + centers correctly
- [ ] `npm run build` 0 TS errors
- [ ] Manually verify in browser: both cold-load and deeplink cases

### P2 -- Nice to Have

#### T-P2-500: [DEBT] CLAUDE.md: Remove duplicate Key Constraints section
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: CLAUDE.md has two ## Key Constraints sections (lines 15 and 34) with nearly identical content. The first is a template placeholder with CUSTOMIZE comment; the second is the actual content block. The duplicate adds confusion and could cause readers to miss updates if only one is maintained.

Fix: Remove the first placeholder Key Constraints section (lines 15-18 with the CUSTOMIZE comment). Keep the second, complete Key Constraints section.

AC: CLAUDE.md has exactly one ## Key Constraints section.

#### T-P2-503: KG-UX-12: Audit/migrate scattered content_length checks + LESSONS entry
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-501
- **Description**: ## Problem
Before this cleanup, 'does a node have drawer content?' could be answered multiple ways (content_length === 0, description field non-empty, etc). Without a single chokepoint, future changes to the content-presence rule (e.g. adding is_stub field, lazy-loading) would require hunting all call sites.

## Depends on
T-P1-501 (KG-UX-10) — which introduces `hasContent(node)` util. This task migrates existing scattered checks to it.

## Deliverables
1. Audit all frontend TS/TSX files for direct `content_length` comparisons or description-presence checks:
   - `grep -rn 'content_length' src/frontend/src/` — expected hits in CompletenessArc.tsx (stub border logic), possibly others
   - `grep -rn '\.description' src/frontend/src/components/` — check any "is it empty?" style checks
2. Migrate each call site to import and use `hasContent()` from KG-UX-10's util. If a call site needs the inverse, use `!hasContent(node)` — do NOT invert by touching content_length directly.
3. Add LESSONS.md entry documenting the convention (under ML-prep project LESSONS.md):
   - Title: "`hasContent(node)` is the only sanctioned content-presence check"
   - Body: rule + why (future-proofing for is_stub / lazy-load), how to apply (always import util, never raw content_length === 0 in consumers)

## Acceptance Criteria
- [ ] `grep -rn 'content_length === 0' src/frontend/src/` returns 0 results outside `hasContent.ts`
- [ ] `grep -rn 'content_length > 0' src/frontend/src/` returns 0 results outside `hasContent.ts`
- [ ] All prior call sites import and use `hasContent()`
- [ ] LESSONS.md entry added with rule + why + how-to-apply
- [ ] `npm run build` 0 TS errors

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

> 462 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-18** -- T-P1-499: [SYNC] Fix settings.json: replace bare python with /c/Anaconda/python.exe. All 8 hook commands in .claude/settings.json use bare python instead of /c/Anaconda/python.exe. This violates the CLAUDE
- [x] **2026-04-17** -- T-P2-492: KG-UX-06: Bezier edges, pillar-colored, spacing polish. Current edges are orthogonal smoothstep with flat gray. Upgrade to bezier curves colored by source pillar for mindmap ae
- [x] **2026-04-17** -- T-P1-498: KG-CN-01: Rewrite node descriptions to CN narration + full English terms. Rewrite framework_nodes.description to Chinese narration + English full-expansion terms. Pilot on 4 nodes validated qual
- [x] **2026-04-17** -- T-P1-491: KG-UX-05: Swimlane layout - per-pillar ELK vertically stacked. Current layered layout stacks 8 pillars in leftmost column causing cross-pillar overlap and visual chaos. Refactor to sw
- [x] **2026-04-17** -- T-P1-490: KG-UX-04: 0-children categories act as leaves; stub badge. 7 depth-1 categories (SQL Fundamentals, OOD SOLID, Diffusion Models, etc.) have 0 children. Expanding them does nothing 
- [x] **2026-04-17** -- T-P1-486: [KG-VIZ-R03] Interaction: tooltip, keyboard a11y, expand-all, hover edge highlight. Post-polish interaction refinements. Scoped per user review (cut edge legend toggle, pillar filter buttons, +/-/0 shortc
- [x] **2026-04-17** -- T-P0-497: KG-UX-09: TreeNav click -> expand ancestors + setCenter on canvas. Wire TreeNav (KG-UX-08) to the canvas. Clicking an entry in TreeNav should: (1) setExpanded to include all ancestors of 
