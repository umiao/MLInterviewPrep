# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

#### T-P0-518: T-MLSD-PILOT-92-S2: Pilot rewrite §2 of id=92 under new rules + human-review gate
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-514
- **Description**: ## Context
Blocking gate between T-P0-514 (Writing Discipline rules published) and T-P0-515/516 (full V2 rewrites). Reviewer insight 2026-04-18: "514's GOOD/BAD examples ARE the prompt corpus for 515/516 — if 514 is weak, V2 copies the weakness 20x." This pilot validates the rules on ONE section before committing to full rewrites.

## CRITICAL — this task does NOT mark itself completed

The autonomous session executing this task MUST leave `status=in_progress` after producing the pilot artifact. DO NOT run `task_db.py update T-P0-518 --status completed` from the session. The human reviews the pilot doc in Discord and flips status to `completed` manually after approval — that's what unblocks T-P0-515 and T-P0-516.

If the session marks itself completed automatically, the runner will incorrectly unblock the downstream V2 rewrites before human approval. To prevent this, write the pilot artifact + PROGRESS.md entry + session_state.json update, then STOP without the status update — this is a deviation from the normal exit protocol for one task only.

## Scope — rewrite ONLY §2 of id=92 Marketplace

Use all Writing Discipline rules from id=18 Appendix A.1 (produced by T-P0-514). Target ONLY the existing §2 "Capacity Estimation" section of id=92 (current V1 content from commit 589dad8). Do NOT touch other sections, do NOT update the DB.

### Steps
1. Load current id=92 description (V1, 9727 chars from commit 589dad8)
2. Extract §2 Capacity Estimation block (content between `## 2.` heading and `## 3.` heading)
3. Rewrite §2 ONLY, applying all 4 Writing Discipline rules (Section Contract, Acronym per-section, Triage 4-element, Specificity discipline) AND the patch-style ban
4. Use the callout convention locked in T-P0-514 (`> **GOOD**:` / `> **BAD**:` / `> **NOTE**:`) if illustrating anything
5. Run `scripts/audit_mlsd_prose_quality.py --node-id 92 --section 2 --report-only` on the NEW §2 content
6. Run `scripts/llm_judge_mlsd.py --v1-text <extracted V1 §2> --v2-text <new §2>` — all three dimensions must show strict improvement
7. Write `docs/mlsd_pilot_92_s2_20260418.md` with:
   - V1 §2 original (verbatim)
   - New §2 rewrite (verbatim)
   - Regex audit report (all 4 gates for the new §2)
   - LLM-judge scores with rationale notes
   - Any observations from the writer about rule ambiguity or edge cases
8. Commit `docs/mlsd_pilot_92_s2_20260418.md` + PROGRESS.md entry
9. Leave task status as `in_progress` — human completes it after Discord approval

## Deliverables
- `docs/mlsd_pilot_92_s2_20260418.md` — side-by-side + audit + LLM-judge
- No DB mutations on framework_nodes (that's 515's job, after approval)
- Task stays `in_progress`, waiting for human explicit unblock

## Acceptance Criteria
- [ ] `docs/mlsd_pilot_92_s2_20260418.md` exists with all 5 content requirements
- [ ] New §2 passes regex gates 7/8/9/11 (per section)
- [ ] New §2 scores strictly higher than V1 §2 on ALL three LLM-judge dimensions (pass verdict from llm_judge_mlsd.py)
- [ ] Pilot doc committed; PROGRESS.md entry appended; `.claude/session_state.json` notes last_task=T-P0-518 + all_done=false (518 still in_progress)
- [ ] **Task status is `in_progress`, NOT `completed`** — waiting for human review
- [ ] If pilot FAILS any gate or LLM-judge doesn't improve: status=`blocked` with diagnostic; task specs iteration on T-P0-514 rules before retry

#### T-P2-517: KG-UX-18: Drawer rendering polish (GFM, rehype-raw, blockquote + callout styling)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Context
Drawer-layer rendering polish, parallel to content V2 tasks. Independent of 514/515/516/518 — can run first, in parallel, or last. User flagged "排版不够精细，可读性不是很强，缺缩进着色" in the MLSD gold review (2026-04-18).

**IMPORTANT — callout contract locked by T-P0-514**: The three callout forms this task must style are EXACTLY:
- `> **GOOD**: …`  → green left-border + light-green background tint
- `> **BAD**: …`   → red left-border + light-red background tint
- `> **NOTE**: …`  → blue left-border + light-blue background tint

No emoji variants, no `✅/❌`, no `**GOOD example**`. Exact literal match required. This is a contract — 514/515/516/518 content all use these three forms only.

## Audit first, then fix

Step 1 — audit `FrameworkNodeDrawer.tsx` and its `MarkdownPreview` to confirm current state of:
- `remark-gfm` (tables, task lists, strikethrough, autolinks)
- `rehype-raw` (raw HTML pass-through, needed for `<mark>` or `<span class>`)
- `remark-math` + `rehype-katex` (math — should be present already from existing formulas)
- Custom blockquote renderer (for callouts)
- Syntax highlighting (existing via `react-syntax-highlighter`)

Step 2 — fix gaps:
1. **Callout styling (PRIMARY DELIVERABLE)**: Implement a custom rehype/remark transform or react-markdown component override for blockquote. Detect `> **GOOD**:` / `> **BAD**:` / `> **NOTE**:` literal prefixes and apply corresponding CSS classes (`.callout-good`, `.callout-bad`, `.callout-note`). Other blockquotes render default. Test on id=18 drawer once T-P0-514's Appendix A.1 lands.
2. **GFM enable**: ensure tables with alignment (`| :---: |`) render correctly, horizontal scroll on narrow drawers
3. **Inline code contrast**: give `` `inline code` `` a distinct background tint + monospace
4. **Nested list indentation**: 3+ level nested bullets render with clear visual hierarchy
5. **Section spacing**: more breathing room between `## ` sections

## Scope discipline
- Drawer-only changes
- No content mutations (that's 515/516/518)
- No changes to KG canvas, TreeNav, or any page outside the drawer component

## Deliverables
1. Audit findings as a brief note in the autonomous session's PROGRESS.md entry
2. Updates to `src/frontend/src/components/framework/FrameworkNodeDrawer.tsx` and its markdown renderer
3. If a new remark/rehype plugin is introduced, add it to `package.json` deps and TS types
4. Regression tests (snapshot or DOM-assertion) covering: callout rendering (3 types), table alignment, inline code, nested list

## Acceptance Criteria
- [ ] Audit findings documented (in session PROGRESS.md)
- [ ] `> **GOOD**: …` renders with green left-border + light-green background
- [ ] `> **BAD**: …` renders with red left-border + light-red background
- [ ] `> **NOTE**: …` renders with blue left-border + light-blue background
- [ ] Other blockquotes (no matching prefix) render default (fallback)
- [ ] Tables with `:---:` alignment render correctly; narrow drawers get horizontal scroll
- [ ] Inline code has distinct background + monospace (test on id=18 once it has Appendix A.1)
- [ ] Nested lists 3+ levels render with visible indentation tiers
- [ ] Regression: id=18, id=92, id=198 drawers all render cleanly — no broken formatting, math intact, code fences intact
- [ ] `npm run build` 0 TS errors
- [ ] `npm test` all green (may add new tests for callout rendering)
- [ ] Manual smoke: open all three drawers — visual polish noticeably improved

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-515: T-MLSD-WORKED-92-V2: Rewrite id=92 Marketplace under Writing Discipline rules (prose-first, triage-complete)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-514, T-P0-518
- **Description**: ## Context
Depends on T-P0-514 (Writing Discipline rules + 4 regex gates + LLM-judge) AND T-P0-518 (pilot rewrite of §2 approved by human). V1 of id=92 (commit 589dad8) passes all 6 original mechanical gates but fails the new prose gates. This V2 rewrites the same content under the new rules.

**CRITICAL — this task does NOT auto-start after 518 completes.** The pilot task 518 produces a side-by-side document for human review; user must approve in Discord before this task actually unblocks. Treat the Discord approval as the logical unblock even though the DB-level dependency is already satisfied.

## Execution mode — SECTION-BY-SECTION (not single-pass)

Reviewer insight: single-pass rewrite of a long doc will degrade to patch-style (V1 + filler sentences). To prevent this, execute section-by-section:

1. Load V1 content (9727 chars)
2. Split V1 into sections by `## ` headings
3. Use T-P0-518's pilot §2 as the paired-transfer reference (shows the BEFORE state of that one section AND the approved AFTER state). All other sections follow the same transformation pattern.
4. For each section §0 through §6 + sub-sections (4a, 4b, 4c, 4d), one at a time:
   a. Apply the 4 Writing Discipline rules (Section Contract, Acronym per-section, Triage 4-element, Specificity discipline)
   b. Run `scripts/audit_mlsd_prose_quality.py --node-id 92 --section N` (hypothetical on the new content) on the rewritten section — gates 7/8/9/11
   c. Run `scripts/llm_judge_mlsd.py` comparing that section's V1 vs new — gate 10, must strictly improve on all 3 dimensions
   d. If any gate FAILS: abort the task with diagnostic, do NOT continue to next section. Write failure state to `logs/worked_92_v2_fail.md`
5. Only after ALL sections pass both regex and LLM-judge gates, assemble the full V2 document
6. Run audits on the FULL document one more time (per-document gates 7/11 + LLM-judge on full doc)
7. Seed script runs with hash-short-circuit idempotency; DB backup + history row; UPDATE id=92

## Hard rules (preserve V1 intent)
- All existing ML content (surge pricing formula, ETA decomposition, Hungarian algorithm, H3/S2/GeoHash tradeoff, Pareto frontier, greedy code, VRP formulation, key metrics table) MUST REMAIN
- §4d "Deep Dive: Domain ML Content" structure from V1 preserved
- Callout convention from T-P0-514 (`> **GOOD**:` / `> **BAD**:` / `> **NOTE**:`) used whenever inserting examples
- Length target: 11000-14500 chars (grows from 9727 — +15-50% from prose + triage expansions)

## Deliverables
Idempotent seed script `scripts/seed_node_92_marketplace_v2_20260418.py`:
- DB backup + history row (capture V1)
- Section-by-section audit + LLM-judge loop
- Final full-document audit + LLM-judge pass required before UPDATE
- Hash-short-circuit idempotent

## Acceptance Criteria
- [ ] Upstream block verified: T-P0-518 completed AND human approval confirmed in Discord/PROGRESS.md before this task starts
- [ ] id=92 description: 11000-14500 chars
- [ ] ALL 10 Quality Gates pass per-section AND full-document (Gates 1-9, 10, 11 from id=18 Appendix A + A.1)
- [ ] Every §0-§6 has Section Contract structure (opening ≥ 60 chars prose + closing bridge)
- [ ] Every tech-choice has Rule 3 triage shape with 4 elements visible in prose (not just in tradeoff table)
- [ ] Every section's first-occurrence acronym is expanded per Rule 2
- [ ] Patch-style ban (Gate 11): every section has `prose_lines ≥ bullet_lines`
- [ ] Gate 10 LLM-judge: V2 strictly > V1 on readability / triage / density per-section AND full-doc
- [ ] All V1 ML content preserved (grep checkpoints: "surge_multiplier", "Hungarian", "VRP", "Pareto", "H3")
- [ ] history row captures 9727-char V1
- [ ] `npm run build` green
- [ ] Manual smoke: /kg?node=n92 reads as coherent narrative with working GOOD/BAD callouts (if T-P2-517 has landed)

#### T-P0-516: T-MLSD-WORKED-198-V2: Rewrite id=198 Rec System under Writing Discipline rules
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-514, T-P0-518
- **Description**: ## Context
Parallel counterpart to T-P0-515 — same execution model and gates, applied to id=198 Rec System. Depends on T-P0-514 (rules + tools) AND T-P0-518 (pilot approved). id=198 V1 (commit 8d8fd17, 19457 chars) is acronym-dense (every ML term is one) so Rule 2 (per-section first-occurrence expansion) will add more overhead than in id=92.

**Same critical caveat as 515**: does NOT auto-start after 518 completes. User approves pilot in Discord, then this task unblocks logically.

## Execution mode — SECTION-BY-SECTION

Identical to T-P0-515's mode. For each section §0, §1, §2, §2b, §3-§10 (existing ML sections), §11, §11a, §11b, §12, §12b:
1. Apply 4 Writing Discipline rules
2. Audit that section (gates 7/8/9/11)
3. LLM-judge that section (gate 10 — V2 > V1 strictly)
4. Abort on failure, log to `logs/worked_198_v2_fail.md`, do not advance

## Section-specific focus (same as previous spec)
1. §0 Time Budget — add prose explaining how to use it in a rec-system round
2. §1 Problem Framing — convert bullets to narrative with bridges
3. §2b Capacity Estimation — each number needs "drives X decision" woven in
4. §3-§10 existing ML content — light touch: add thesis opening + bridge closing, leave dense ML intact
5. §11a/11b Serving Architecture — prose intro before each table
6. §12b L5 Tradeoff Table — prose sentence above each row explaining why the choice matters
7. Tech-choices (ScaNN, HNSW, IVF-PQ, MoE, MMR, DPP, DCN-v2, DLRM, ESMM, MMoE, Faiss, Milvus, Pinecone, Kafka, Flink) — all get Rule 3 triage shape or move to "alternatives considered" footnote
8. Acronyms — per-section first-occurrence expansion (Rule 2)

## Deliverables
Idempotent seed script `scripts/seed_node_198_rec_v2_20260418.py` — same pattern as 515's seed: DB backup + history + section-by-section audit loop + final full-doc gates + UPDATE id=198.

## Length target
V1 = 19457 chars. V2 target = 23000-28000 chars (+20-45% from added prose + triage expansions; larger headroom than 92-V2 because 198 is acronym-denser)

## Acceptance Criteria
- [ ] Upstream block: T-P0-518 done + user approval in Discord
- [ ] id=198 description: 23000-28000 chars
- [ ] ALL 10 Quality Gates pass (per-section + full-document)
- [ ] All 18 sections (§0-§12 + subsections) have Section Contract structure
- [ ] Every tech-choice (ScaNN/HNSW/IVF-PQ/MoE/MMR/DPP/DCN-v2/DLRM/ESMM/MMoE/Faiss/Milvus/Pinecone/Kafka/Flink — that's 15 distinct products) has Rule 3 triage shape with 4 elements in prose
- [ ] Every section's first-occurrence acronym is expanded per Rule 2
- [ ] Gate 10 LLM-judge: V2 strictly > V1 per-section AND full-doc
- [ ] All V1 ML content preserved (grep checkpoints: "two-tower", "log-Q softmax", "HNSW", "ScaNN", "MMoE", "DCN-v2", "MMR", "DPP", "PSI", "CUPED", "delayed feedback", "ESMM" — all present)
- [ ] history row captures 19457-char V1
- [ ] `npm run build` green
- [ ] Manual smoke: /kg?node=n198 reads as coherent narrative

### P1 -- Should Have (agentic intelligence)

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

> 478 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-18** -- T-P2-503: KG-UX-12: Audit/migrate scattered content_length checks + LESSONS entry. ## Problem
- [x] **2026-04-18** -- T-P2-500: [DEBT] CLAUDE.md: Remove duplicate Key Constraints section. CLAUDE.md has two ## Key Constraints sections (lines 15 and 34) with nearly identical content. The first is a template p
- [x] **2026-04-18** -- T-P1-513: T-MLSD-WORKED-198: Upgrade Real-Time Rec System (id=198) with L5 skeleton. ## Context
- [x] **2026-04-18** -- T-P1-512: T-MLSD-WORKED-92: Upgrade Marketplace & Logistics (id=92) to L5-bar gold standard. ## Context
- [x] **2026-04-18** -- T-P1-511: T-MLSD-AUDIT-01: Score 10 design problems against L5 framework, produce gap report. ## Context
- [x] **2026-04-18** -- T-P0-514: T-MLSD-FRAMEWORK-02: Append Writing Discipline rules to id=18 Appendix A (5 rules + examples + heuristic gates). ## Context
