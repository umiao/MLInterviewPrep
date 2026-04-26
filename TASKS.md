# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-581: [BQ-DEPTH-10] Primary-story batch: mark is_primary=1 for top 40 high-probability questions
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-579
- **Description**: From the Phase A matrix (BQ-DEPTH-01), propose the top 40 high-probability BQ questions (based on company overlap + asked-frequency intuition). For each, pick the ONE primary story.

Dependency on BQ-DEPTH-09 is through user-approved calibration style + schema, but this task can run in parallel with C2 bulk if user approves the 40 assignments upfront.

Deliverables:
- docs/bq_primary_story_assignments_20260421.md -- 40 rows with (question_id, primary_example_id, rationale)
- scripts/seed_bq_primary_flags_20260421.py -- idempotent, DB-backup-guarded
- Invariant: each question has exactly one is_primary=1 link (trigger or pre-check)

AC:
- User reviews 40 assignments on Discord BEFORE DB write
- Script re-runs with [SKIP]
- SELECT question_id, COUNT(*) FROM question_example_links WHERE is_primary=1 GROUP BY question_id HAVING COUNT(*) > 1 returns empty
- 40 questions have is_primary=1 set; other questions left at is_primary=0 until later batch

#### T-P1-582: [BQ-DEPTH-11] Bulk probe_notes for remaining ~36 high-probability questions
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-580, T-P1-581
- **Description**: After calibration samples (BQ-DEPTH-09) approved + primary flags set (BQ-DEPTH-10), write probe_notes for the remaining 36 questions in the top 40.

Split into 3-4 sub-batches of ~10 each, each a separate autonomous session per feedback_always_auto_run. Between batches, user spot-check one probe_notes entry to catch style drift early.

Content rules (locked by BQ-DEPTH-09 calibration):
- 中文叙述 + 英文术语
- All 4 schema fields required (core_signal, what_good_looks_like, what_L5_adds, common_failure_modes)
- Reference the is_primary story in what_good_looks_like
- No angle_label -- angle lives in prose

Deliverables:
- scripts/seed_bq_probe_notes_batch{1-4}_20260421.py -- each idempotent + DB-backup-guarded
- After each batch: spot-check doc attached to Discord for user review

AC:
- All 40 top questions have probe_notes set
- Each batch script re-runs with [SKIP]
- No schema field empty; all 4 structured fields populated for every question
- User spot-check passed between batches

#### T-P1-583: [BQ-DEPTH-12] Frontend Phase D: primary-story prominent card + probe_notes expandable panel
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-581
- **Description**: src/frontend/src/pages/BehavioralQuestions.tsx redesign.

Journey-first AC (from CLAUDE.md planning rules): user opens /behavioral -> clicks expand on a top-40 question -> sees ONE gold-bordered primary story card (big, with full relevance_note + STAR Situation preview + 'use this angle' hint) -> sees 'Also applies' collapsed panel with 2-3 backup stories -> clicks 'What this question probes' -> sees 4-section probe_notes panel (core_signal / what_good_looks_like / what_L5_adds / common_failure_modes).

Scenario matrix:
- Question has is_primary link + probe_notes -> full new treatment
- Question has is_primary link + no probe_notes -> primary card only, probe panel hidden
- Question has no is_primary link (non-top-40) -> current flat list fallback (no visual regression)
- Question has 0 links -> current 'no example' red badge

Manual smoke test AC:
- Launch vite dev (localhost:5173/behavioral); pick OWN-1 (will have probe_notes after Phase C); verify primary card is gold-bordered and renders at top; verify probe_notes panel expands and shows 4 sections with markdown; verify 'Also applies' toggles

Also update frontend type src/frontend/src/types/behavioral.ts to include probe_notes + is_primary.

AC:
- TypeScript compiles
- vitest suite passes
- Manual smoke test path completes without console errors
- No regression on questions without probe_notes / without is_primary

#### T-P1-600: [BQ-TAX-03] Phase 2: Retag existing 34 examples + 115 questions against new taxonomy
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Retag all existing behavioral_examples + behavioral_questions against the new themes + facets from BQ-TAX-02.

Retag steps:
1. For each of 34 examples: evaluate whether story advocates for user → tag customer_user_focus; evaluate ethical/integrity angle → tag ethical_integrity_backbone; evaluate fast_learning facet fit; evaluate scrappy_innovation facet fit; evaluate strategic_scope facet fit
2. For each of 115 questions: same evaluation against question stem
3. Migrate existing scope_creep_ambiguous theme tags to scope_creep_pm_ambiguity facet tags (under ambiguity_uncertainty) — same example/question rows, different tag table
4. After migration verification: DROP scope_creep_ambiguous theme (safe because all tags migrated to facet)

Tagging approach per story_rewrite_protocol Step 4 (audit propagation surface):
- Pre-draft audit: list which existing themes each example already has, check for overlap with new customer/ethical
- Apply tags via seed script
- Post-apply audit: verify count (expect 34 examples get 0-3 new tags each, 115 questions get 0-2)

Deliverables:
- scripts/seed_bq_taxonomy_retag_20260421.py (idempotent, DB-backup-guarded)
- docs/bq_taxonomy_retag_log_20260421.md — per-example + per-question tagging decisions with rationale (so revert recipe exists)

AC:
- Every example with user-advocacy angle tagged customer_user_focus
- Every example with push-back-at-cost angle tagged ethical_integrity_backbone
- 0 rows reference scope_creep_ambiguous theme post-migration
- scope_creep_ambiguous theme deleted from behavioral_themes (row count 17 → 16 after drop)
- Script re-runs [SKIP]
- Retag log shows rationale for each tag added (not a black box)

#### T-P1-601: [BQ-TAX-04] Phase 2: Frontend — new theme cards + facet pills + CLUSTER_FAMILIES update + is_signature visual
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-600
- **Description**: Frontend surface for the new taxonomy landed by BQ-TAX-01/02/03.

Scope:
1. /quick-index?section=bq — add 2 new theme cards (customer_user_focus, ethical_integrity_backbone). Update CLUSTER_FAMILIES in QuickIndex.tsx:
   - customer_user_focus → new cluster 'Customer & User' (standalone) OR fold into 'Data and Decisions' renamed to 'Data & Customer'
   - ethical_integrity_backbone → add to 'Conflict & Collaboration' cluster (renamed 'Conflict, Collaboration & Integrity')
   - Remove scope_creep_ambiguous from 'Decision under Ambiguity' cluster (it was deleted)
2. BehavioralQuestions.tsx ExampleCard + BehavioralThemePage ExampleCard — render facet pills (small, distinct color from theme pills). Example: a story tagged fast_learning + scrappy_innovation gets 2 small pills below the theme pills.
3. ThemeFilterSidebar.tsx — include new themes in the filter list; optionally add a separate 'Facets' filter group (can defer to later if scope creep)
4. is_signature visual — if is_signature=1, show a small 'Signature Story' badge (distinct from golden badge). Golden = quality mark; Signature = 'proudest achievement, use for open-ended impact Q's'
5. types/behavioral.ts — add facets: FacetTag[] and is_signature/signature_at to BehavioralExample interface

Deliverables:
- Updated QuickIndex.tsx / BehavioralQuestions.tsx / BehavioralThemePage.tsx / ThemeFilterSidebar.tsx / ExampleDrawerContent.tsx / types/behavioral.ts
- Backend response schemas updated in behavioral.py router to include facets + is_signature

AC:
- Manual smoke test: /quick-index?section=bq shows 2 new theme cards at correct cluster positions; ExampleCard shows facet pills when example has facet tags; ThemeFilterSidebar has new themes
- tsc + vitest + vite build pass
- No regression on existing theme/question/example rendering
- Backend tests confirm facets included in /behavioral/examples + /behavioral/themes responses

### P2 -- Nice to Have

#### T-P2-584: [BQ-DEPTH-13] Phase C1: probe_qa.md for remaining 4 golden (EX-01/15/16/17) matching EX-30 style
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P0-575
- **Description**: Extend the EX-30_probe_qa.md pattern to the other 4 golden stories. This is story-side depth (5 anticipated probes + delivery cues) that pairs with question-side probe_notes.

Decoupled from Phase D; independent sessions after EX-01 rewrite lands.

Output files (one per story):
- docs/behavioral_prep_notes/EX-01_probe_qa.md
- docs/behavioral_prep_notes/EX-15_probe_qa.md
- docs/behavioral_prep_notes/EX-16_probe_qa.md
- docs/behavioral_prep_notes/EX-17_probe_qa.md

Each file mirrors EX-30_probe_qa.md structure:
- Header: linked story id + themes + preservation note
- 5 anticipated probes (the most dangerous / most common follow-ups) with 应答方向
- 口述 delivery section: pacing cues, pause markers, L5 tone discipline
- Language: 中英混合 per user's EX-30 precedent (不需要统一)

AC:
- All 4 .md files created; each >= 40 lines
- Each file's Q1 is the single most-dangerous probe (the one where junior answer would get eliminated)
- Linked from behavioral_examples.analogy or tech_terms field (or a new pointer) so /behavioral/examples drawer can deeplink
- User reviews each one on Discord before marking complete

#### T-P2-585: [BQ-DEPTH-14] Phase E: narrow probe-drift detector (principle_tags/risk/outcome/hash only)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-582
- **Description**: Per user direction: drift trigger must be NARROW. Monitoring arbitrary STAR field changes will produce noise the user learns to ignore.

Write scripts/detect_probe_drift.py that flags probe_notes needing refresh ONLY when one of these changes on a linked story since probe_notes_updated_at:
- behavioral_examples.principle_tags
- behavioral_examples.risk_statement
- behavioral_examples.result (the outcome)
- Narrative hash (SHA256 of situation+task+action+result) changed AND delta > threshold (e.g. >30% diff)

Output: docs/bq_probe_drift_report_<date>.md listing (question_id, linked_example_id, drift_reason, diff_preview).

Optional: cron-schedule via session_context.py reminder (not hook -- reminder only).

AC:
- Script reads-only; no DB writes
- Empty output when no drift (silent-on-no-work rule)
- False-positive rate: manually run after BQ-DEPTH-09 with no changes; expect 0 reports
- True-positive rate: manually mutate a test risk_statement; expect 1 report

#### T-P2-607: F-2: emoji scan check_emoji.py honor CLI args (scan_single_file extraction)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Follow-up to T-P1-606 (first emoji-scanner fix commit).

Make scripts/check_emoji.py honor sys.argv[1:]: if non-empty, scan only those paths (files or directories); otherwise preserve full-repo fallback so CI bare-invocation (.github/workflows/ci.yml) stays unchanged.

Per reviewer feedback on the emoji_scan_fix_plan_20260423.md: before shipping, produce a diff preview of the scan_single_file extraction (current scan_emoji couples walk + per-file logic at lines 42-49) and surface it for user review. LoC estimate (~25) may be optimistic if the extraction requires parameter renames or return-value changes.

Acceptance: (a) python scripts/check_emoji.py [path] scans only [path]; (b) python scripts/check_emoji.py with zero args behaves exactly as before; (c) new test covers both the single-file-dirty and single-file-clean branches.

#### T-P2-614: [KG-DESIGN-DUAL-VIEW] Open Q: consolidate vs legitimize ml-fundamentals + pillar2 coexistence
- **Priority**: P2
- **Complexity**: L
- **Depends on**: T-P0-613
- **Description**: [KG-DESIGN-DUAL-VIEW] Open question: is ml-fundamentals/* + pillar2 coexistence
a bug to eliminate (consolidate to single root) OR a feature to legitimize
(permanent dual view)? Output: a design doc, not code.

WHY: Both KG bug-review rounds defaulted to "two structures = bug, migrate to
single root". Reviewer round 2 challenged that premise: ml-fundamentals
(interview-grind / leaf-dense / drill-oriented) and pillar2 (knowledge-system
/ structured / theory-deep) may serve different cognitive modes. Their
overlap could be intentional view separation, not redundancy. Resolving this
question changes whether KG-FIX-01's parent_id walk is transitional or
permanent infrastructure.

ACCEPTANCE CRITERIA
AC1: docs/design/kg_dual_view_decision_20260425.md created. Section 1 MUST
     answer the open Question 0 explicitly:
        "Are we eliminating duplication (single-root consolidation) or
         legitimizing it (permanent dual view)?"
     Pick (a) or (b) with stated rationale.
AC2: If (a) "consolidate":
     - Section 2 specifies migration strategy (keep eight_essays subnode vs
       flatten as pillar2 siblings vs change kindForDepth topology).
     - Section 3 enumerates name-collision pairs (e.g.
       pillar2.unsupervised_learning vs ml-fundamentals/unsupervised) and
       resolution (merge content, dedupe, drop one side).
     - Section 4 lists implementation tasks to be split out as P1 follow-ups.
AC3: If (b) "dual view":
     - Section 2 specifies path-convention rules for additional roots
       (under what circumstances may a 3rd top-level taxonomy be added?).
     - Section 3 confirms KG-FIX-01 implementation is permanent — request
     amendment of its docstring to drop "transitional" language.
     - Section 4 closes this task with no follow-up implementation work.
AC4: Decision is shared via Discord for explicit user ratification before
     any further migration / cleanup work begins.

DEPENDS ON: KG-FIX-05 (no point answering the dual-view question until the
acute "Other" symptom is resolved and the system is observable).

COMPLEXITY: L (deferred — this is a design question, not implementation)

### P3 -- Stretch Goals

## Blocked

#### T-P1-606: Fix emoji-scan cp1252 crash + lock regex consistency (F-1 + F-3 + meta-test)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Commit 1 of the emoji-scanner fix plan. BLOCKED on user decision between options A/B/C for the 1 legit FE0F hit in PROGRESS.md:590 (discord msg 1497033478842351616, 2026-04-23).

INVESTIGATION COMPLETE, revised findings:
- Original plan assumed 3 regexes byte-identical (subagent survey claim). Verified empirically: FALSE. check_emoji.py retains stale BMP ranges \u2600-\u26ff + \u2700-\u27bf; check_emoji_files.py and lint_check.py had them removed 2026-04-11 per archive/progress_log.md:20 (to kill 81 BLACK STAR-style false positives).
- Current full-repo scan: 63 hits from stale check_emoji.py regex; 62 are BMP false positives that DISAPPEAR under the narrow (canonical) regex; 1 is a legit U+FE0F variation selector in PROGRESS.md:590 from a quoted historical discord message about a prior emoji incident.
- Root cause of user pain is this regex drift (RC-3), not the Windows encoding issue alone (RC-1 is latent).

REVISED EXECUTION SCOPE when unblocked:
1. scripts/check_emoji.py: remove 2 BMP range lines to match check_emoji_files.py + lint_check.py.
2. scripts/check_emoji.py + scripts/check_emoji_files.py: F-1 UTF-8 stream reconfigure at main() entry (defense in depth for future U+1F6xx emoji).
3. tests/test_emoji_regex.py (or new tests/test_emoji_scanner.py): regex-equality meta-test + subprocess cp1252 env test (reviewer's revised F-3).
4. User-chosen handling of PROGRESS.md:590 FE0F (option A/B/C pending).

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos + template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Remove deprecated stop-cache from BOTH helixos/.claude/hooks/test_check.py AND claude-code-project-template/.claude/hooks/test_check.py. Both still import and use check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed these (T-P2-188, commit abf6543) per the lesson that stop caches cause false PASS results when files change between sessions.

Verified state (2026-04-23): helixos/.claude/hooks/test_check.py lines 10, 21, 48 still import/call check_stop_cache/write_stop_cache. claude-code-project-template/.claude/hooks/test_check.py same three lines.

Action:
1. helixos/.claude/hooks/test_check.py: remove cache import and calls -- copy MLInterviewPrep version.
2. claude-code-project-template/.claude/hooks/test_check.py: same removal.
3. Clean up hook_utils.py in both repos only if no other callers remain.
4. Run tests after to confirm hook still works.

Consolidated from duplicates: T-P2-255, T-P2-320 (both helixos stop-cache), T-P2-208 (template stop-cache). All 3 marked completed-as-duplicate on 2026-04-23 per T-P2-587.

Blocked: must be executed from a helixos or template Claude Code session -- file permissions prevent writing to those repos' .claude/hooks/ from a MLInterviewPrep session.

Source: MLInterviewPrep/.claude/hooks/test_check.py (cache-free reference).

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

## Completed Tasks

> 555 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-25** -- T-P0-613: [KG-FIX-05] Manual smoke + screenshots + HARD MERGE GATE (no auto-merge to main). [KG-FIX-05] Manual smoke test + before/after screenshots + HARD MERGE GATE.
- [x] **2026-04-25** -- T-P0-612: [KG-FIX-04] Schema invariant + convention doc + smoke protocol + LESSONS postmortem. [KG-FIX-04] Schema invariant + path convention doc + LESSONS postmortem +
- [x] **2026-04-25** -- T-P0-611: [KG-FIX-03] Frontend: explicit PILLAR_ORDER map (step=10). [KG-FIX-03] Frontend: replace pillarSortKey() regex in
- [x] **2026-04-25** -- T-P0-610: [KG-FIX-02] Frontend: add ml-fundamentals to PILLAR_STYLES. [KG-FIX-02] Frontend: extend PILLAR_STYLES in
- [x] **2026-04-25** -- T-P0-609: [KG-FIX-01] Backend: walk parent_id for pillar derivation. [KG-FIX-01] Backend: rewrite `_pillar_of()` in src/backend/routers/kg.py to walk
- [x] **2026-04-24** -- T-P1-603: [SD-YT-02] Expand framework_nodes id=198 (Real-Time Recommendation) — YouTube-specific ML pipeline. Expand framework_nodes.description for id=198 'Real-Time Recommendation System Design' (currently 27996 chars, 19 header
- [x] **2026-04-24** -- T-P1-602: [SD-YT-01] Expand system_designs id=21 (YouTube/Netflix Video Streaming) — traditional SD gaps. Expand system_designs row id=21 'Design YouTube/Netflix Video Streaming' (currently 21417 chars across overview/architec
- [x] **2026-04-24** -- T-P1-580: [BQ-DEPTH-09] probe_notes PATTERN CALIBRATION: write 4 samples on fresh stories (EX-15/16/17/30 top-Q each). Per user direction: use the 4 already-rewritten (fresh) stories as free-lunch pattern calibration BEFORE doing bulk C2. 
- [x] **2026-04-24** -- T-P0-608: Fix emoji-CI: align check_emoji.py regex + Windows UTF-8 streams + code/doc split + meta test + cp1252 regression harness. Recapture of prior aborted session. Root cause found: check_emoji.py has wider regex (includes \u2600-\u26ff + \u2700-\u
- [x] **2026-04-23** -- T-P2-587: [DEBT] helixos: Deduplicate 10 stale blocked SYNC tasks (bare-python, stop-cache, setup_python_env.sh). The helixos task DB has 10 blocked SYNC/DEBT tasks that are stale duplicates of each other, clogging the backlog.
- [x] **2026-04-23** -- T-P2-586: [SYNC] Propagate 3 universal lessons from MLInterviewPrep (2026-04-17..04-19) to root LESSONS.md. Promote 3 new universal lessons from MLInterviewPrep LESSONS.md (2026-04-17..04-19) to Gen_AI_Proj root LESSONS.md. None
- [x] **2026-04-23** -- T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P2-207 (helixos test_check.py stop-cache removal). Work folded i
- [x] **2026-04-23** -- T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P2-207 (helixos test_check.py stop-cache removal). Work folded i
- [x] **2026-04-23** -- T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Folded into T-P2-207's expanded scope, which now covers BOTH helixos AND templa
- [x] **2026-04-23** -- T-P1-605: Seed LC 3900 (Longest Balanced Substring After One Swap, Google tag). User-driven: ad-hoc request to seed LC 3900 with Google company tag, preserving prefix-sum + bucket approach and adding 
- [x] **2026-04-23** -- T-P1-579: [BQ-DEPTH-08] Phase B: Schema uplift -- add is_primary on links, probe_notes JSON on questions (NO angle_label). Schema migration after all 4 high-link rewrites land.
- [x] **2026-04-23** -- T-P0-578: [BQ-DEPTH-07] Rewrite EX-33 (MoE -> Allocation Paradigm Shift) via story_rewrite_protocol. EX-33 is a high-link, pre-rewrite story (links from 2026-03-24 batch).
- [x] **2026-04-23** -- T-P0-577: [BQ-DEPTH-06] Rewrite EX-14 (LLM Exploration / Vague AI Mandate) via story_rewrite_protocol. EX-14 is a high-link, pre-rewrite story (2026-03-24 relevance_notes).
- [x] **2026-04-23** -- T-P0-576: [BQ-DEPTH-05] Rewrite EX-02 (Manager Resistance -> Team Transfer) via story_rewrite_protocol. EX-02 is a high-link story still on pre-rewrite relevance_notes (2026-03-24 batch).
- [x] **2026-04-23** -- T-P0-575: [BQ-DEPTH-04] Rewrite EX-01 (Search Diversity/Intent Collapse) via story_rewrite_protocol. EX-01 has 16 question links -- the biggest stale surface. It IS golden-flagged but pre-dates the NRG-v2 / risk_statement
