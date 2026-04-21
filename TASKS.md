# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-575: [BQ-DEPTH-04] Rewrite EX-01 (Search Diversity/Intent Collapse) via story_rewrite_protocol
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-574
- **Description**: EX-01 has 16 question links -- the biggest stale surface. It IS golden-flagged but pre-dates the NRG-v2 / risk_statement / structured-protocol era.

Follow docs/workflow/story_rewrite_protocol.md (all 7 steps):
1. Red-flag scan BEFORE drafting: surface any defensive openers / cliche lessons / etc. in current EX-01
2. Draft + show on Discord, wait for explicit user approval ('可以执行' or equivalent)
3. Two idempotent seed scripts: _rewrite_ex01_*.py (STAR + risk_statement + NRG-v2) and _propagate_ex01_*.py (title/cn_elevator_pitch/principle_tags/16 relevance_notes)
4. Pre-draft audit: list the 16 current question framings; post-apply audit: 5 propagation surfaces (derived fields, join tables, API JSON, canonical seeds, frontend pre-renders)
5. Single propagation script + inline edits to scripts/seed_master_pitches.py and docs/bq_story_arcs.json (arc-1 narrative)
6. Verify: idempotent re-run, DB read-back, simulate /behavioral/story-arcs merge
7. Update NRG, principle_tags, role_zh meta-layers

AC:
- User approves rewritten draft on Discord before any DB write
- Both scripts re-run with [SKIP]
- All 16 relevance_notes refreshed to match new STAR
- canonical seed scripts updated inline (no silent re-run drift)
- DB backup with suffix _pre_ex01_rewrite

#### T-P0-576: [BQ-DEPTH-05] Rewrite EX-02 (Manager Resistance -> Team Transfer) via story_rewrite_protocol
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-574
- **Description**: EX-02 is a high-link story still on pre-rewrite relevance_notes (2026-03-24 batch).

Same protocol as BQ-DEPTH-04 (7 steps, 2 scripts, idempotent, DB backup).

Pre-draft red-flag scan should check: does EX-02 currently tell the persuasion story or the influence-without-authority story? User to call the frame during draft review.

AC:
- User approves draft before DB write
- Both scripts re-run [SKIP]
- All linked relevance_notes refreshed
- Canonical seeds updated inline
- DB backup with suffix _pre_ex02_rewrite

#### T-P0-577: [BQ-DEPTH-06] Rewrite EX-14 (LLM Exploration / Vague AI Mandate) via story_rewrite_protocol
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-574
- **Description**: EX-14 is a high-link, pre-rewrite story (2026-03-24 relevance_notes).

Same 7-step protocol as BQ-DEPTH-04.

Pre-draft red-flag scan: EX-14 currently frames as 'persuaded manager to pivot from flashy agentic to pragmatic LLM-as-Judge'. Check if this can be sharpened to structural-reframe pattern matching EX-15 golden voice (spoken-English rhythm, sentence fragments OK, no AI explainer mode).

AC:
- User approves draft before DB write
- Scripts re-run [SKIP]
- All linked relevance_notes refreshed
- Canonical seeds updated inline
- DB backup with suffix _pre_ex14_rewrite

#### T-P0-578: [BQ-DEPTH-07] Rewrite EX-33 (MoE -> Allocation Paradigm Shift) via story_rewrite_protocol
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-574
- **Description**: EX-33 is a high-link, pre-rewrite story (links from 2026-03-24 batch).

Same 7-step protocol as BQ-DEPTH-04.

Note: EX-33 already has sibling EX-33B (MoE Over-Iteration humility lesson). Pre-draft audit must check that rewriting EX-33 does not leave EX-33B stranded -- verify EX-33B can stand alone or needs parallel update.

AC:
- User approves draft before DB write
- Scripts re-run [SKIP]
- All linked relevance_notes refreshed
- EX-33B coherence check documented in commit message
- Canonical seeds updated inline
- DB backup with suffix _pre_ex33_rewrite

### P1 -- Should Have (agentic intelligence)

#### T-P1-579: [BQ-DEPTH-08] Phase B: Schema uplift -- add is_primary on links, probe_notes JSON on questions (NO angle_label)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-575, T-P0-576, T-P0-577, T-P0-578
- **Description**: Schema migration after all 4 high-link rewrites land.

Per user direction: NO angle_label DB field. Angle lives in probe_notes prose as writing discipline. Revisit in 6 months if cluster emerges.

Add:
1. question_example_links.is_primary BOOLEAN DEFAULT 0  (exactly one primary per question, enforced by trigger)
2. behavioral_questions.probe_notes JSON  (structured: {core_signal, what_good_looks_like, what_L5_adds, common_failure_modes})
3. behavioral_questions.probe_notes_updated_at DATETIME

Deliverables:
- scripts/migrate_bq_schema_20260421.py (idempotent: ALTER TABLE ... IF NOT EXISTS pattern via PRAGMA check)
- DB backup before migration
- SQLAlchemy model + Pydantic schema updates in src/backend/models/behavioral.py and schemas/behavioral.py
- Backend routes wired: GET /behavioral/questions returns probe_notes + link is_primary; PUT /behavioral/questions/{id} accepts probe_notes; POST /behavioral/links accepts is_primary
- Regression test in tests/: round-trip probe_notes JSON, enforce single-primary-per-question invariant

AC:
- Migration runs clean on current DB (no data loss)
- Migration script re-runs with [SKIP]
- Backend tests pass (existing + new)
- Frontend types file updated (src/frontend/src/types/behavioral.ts)
- No angle_label field added (verified via grep)

#### T-P1-580: [BQ-DEPTH-09] probe_notes PATTERN CALIBRATION: write 4 samples on fresh stories (EX-15/16/17/30 top-Q each)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-579
- **Description**: Per user direction: use the 4 already-rewritten (fresh) stories as free-lunch pattern calibration BEFORE doing bulk C2. This validates the probe_notes schema + style guide with 4 real samples so bulk work does not go sideways.

Pick each story's clearest primary question (propose during Phase A matrix, confirm in this task):
- EX-15 primary Q candidate: OWN-1 (take ownership of failure) -- picks up dashboard blind spot + absorbing rollback
- EX-16 primary Q candidate: PS-6 or ADP-5 (calculated risk / handled mistake)
- EX-17 primary Q candidate: ADP-19 or COM-5 (receiving difficult feedback / frame pivot)
- EX-30 primary Q candidate: OWN-1 or ADP-5 (ownership of failure / mistake recovery)

Language: 中文叙述 + 英文术语. Copy EX-30_probe_qa.md style for all 4. Do NOT write a style guide yet -- user wants to see 4 samples before codifying.

Structure for each probe_notes (stored in behavioral_questions.probe_notes JSON):
{
  'core_signal': '1-2 sentence 中文: 这题本质在问什么 L5 signal',
  'what_good_looks_like': '3-5 bullet 中文+英文术语: L4 bar 答出这些即过',
  'what_L5_adds': '2-3 bullet: L5 bar 在此基础上再多一层 (structural reframe / risk_statement / org-level lesson)',
  'common_failure_modes': '3-4 bullet: junior answer / redemption tail / scapegoating / 避开 reviewer 当场扣分的点'
}

Also mark the 4 links as is_primary=1 in question_example_links for these 4 Q-E pairs.

AC:
- scripts/seed_bq_probe_notes_calibration_20260421.py is idempotent + DB-backup-guarded
- 4 probe_notes persisted, each structurally complete (all 4 fields non-empty)
- 4 is_primary=1 flags set on the 4 chosen links
- User REVIEW GATE on Discord before any BQ-DEPTH-10 / BQ-DEPTH-11 work starts (attach the 4 probe_notes MD preview)
- Script re-runs with [SKIP]

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

#### T-P1-598: [BQ-TAX-01] Phase 2: Schema migration — add behavioral_facets tables + is_signature column
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-597
- **Description**: Phase 2 of taxonomy refactor. Blocked behind Phase 1 UX (T-P1-596/597) per reviewer-approved execution order: UX先稳, schema 再动, 避免 bug 归因成本非线性放大.

Schema changes (idempotent migration):
1. CREATE TABLE behavioral_facets (id INT PK, slug VARCHAR UNIQUE, label VARCHAR, parent_theme_id INT NULL FK->behavioral_themes, description TEXT, display_order INT, created_at DATETIME)
   - Facet usage rule (written in schema comment + docs): facets are ONLY for (a) staff/L6 signal tags, (b) cross-theme retrieval tags, (c) scenario sub-type when rename would mix abstraction layers. NOT a dumping ground.
2. CREATE TABLE example_facet_tags (example_id INT FK, facet_id INT FK, created_at DATETIME, PRIMARY KEY(example_id, facet_id))
3. CREATE TABLE question_facet_tags (question_id INT FK, facet_id INT FK, created_at DATETIME, PRIMARY KEY(question_id, facet_id))
4. ALTER TABLE behavioral_examples ADD COLUMN is_signature BOOLEAN DEFAULT 0
5. ALTER TABLE behavioral_examples ADD COLUMN signature_at DATETIME NULL

Deliverables:
- scripts/migrate_bq_taxonomy_20260421.py (idempotent via PRAGMA table_info / sqlite_master check, DB-backup-guarded)
- SQLAlchemy model updates in src/backend/models/behavioral.py
- Pydantic schema updates in src/backend/schemas/behavioral.py
- Regression test confirming (a) existing rows survive, (b) new tables created once, (c) ALTER COLUMN idempotent

AC:
- Migration runs clean; re-runs with [SKIP]
- pytest passes 
- Backend API still returns existing data unchanged
- No frontend changes yet (Phase 2 schema only)

#### T-P1-599: [BQ-TAX-02] Phase 2: Seed 2 new themes + 3 facets + demote scope_creep_ambiguous
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-597, T-P1-598
- **Description**: Seed the taxonomy delta into the new facets schema from BQ-TAX-01.

ADD themes (2):
- customer_user_focus / 'Customer & User Focus' — 为用户做对的事的叙事轴 (Amazon CO, Meta, Google)
- ethical_integrity_backbone / 'Ethical Integrity & Backbone' — integrity / disagree-not-just-commit / push back even at cost

ADD facets (3):
- fast_learning / 'Fast Learning' / parent_theme_id=NULL (cross-theme tag per reviewer: learning is capability not scenario, independent retrieval axis)
- scrappy_innovation / 'Scrappy Innovation' / parent_theme_id NULL (cross-theme tag: solution style not scenario)
- strategic_scope / 'Strategic / Org-Level Scope' / parent_theme_id NULL (staff/L6 signal per reviewer: not a theme, don't split leadership_direction)

DEMOTE scope_creep_ambiguous → facet under ambiguity_uncertainty (do NOT rename ambiguity_uncertainty per reviewer: 场景 vs 能力 不能绑死一个 theme):
- Create facet 'scope_creep_pm_ambiguity' with parent_theme_id = ambiguity_uncertainty.id
- Do NOT delete the original theme yet — Phase 3 (after retag verified) can drop it

Deliverables:
- scripts/seed_bq_taxonomy_delta_20260421.py (idempotent, DB-backup-guarded)
- docs/bq_taxonomy_delta_20260421.md — documents the delta + facet usage rule

AC:
- 2 themes + 4 facets inserted (3 cross-theme + 1 scope_creep_pm_ambiguity under ambiguity)
- Idempotent re-run prints [SKIP]
- behavioral_themes row count: 15 → 17
- behavioral_facets row count: 0 → 4
- Existing example/question theme tags unchanged (Phase 2 schema+seed only; retag is BQ-TAX-03)

#### T-P1-600: [BQ-TAX-03] Phase 2: Retag existing 34 examples + 115 questions against new taxonomy
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-599
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

#### T-P2-586: [SYNC] Propagate 3 universal lessons from MLInterviewPrep (2026-04-17..04-19) to root LESSONS.md
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Promote 3 new universal lessons from MLInterviewPrep LESSONS.md (2026-04-17..04-19) to Gen_AI_Proj root LESSONS.md. None of these are in the root yet (root is current to 2026-04-13).

Lessons to add:
1. [2026-04-17] claude -p usage limits & 429 handling -- Tags: #claude-code #usage-limits #batch-scripts #429-retry. Batch scripts using claude -p hit daily subscription cap (rc=1, JSON result with api_error_status=429). Fix: detect 429 JSON pattern, fail fast with clear message; split batches across days.
2. [2026-04-18] Background runner visibility: nohup & vs Bash run_in_background -- Tags: #orchestration #autonomous #bash #monitor #visibility. nohup+& detaches child; Bash tool tracks launcher (exits fast), not runner. Fix: use run_in_background directly (no &) OR keep nohup+& with Monitor on tail -f log filtered for session boundaries.
3. [2026-04-19] Human-approval-gate language in task specs is sticky -- Tags: #autonomous #task-spec #approval-gate #workflow. Prose gate inside task description (does NOT auto-start) persists across autonomous sessions even after condition is cleared. Fix: use a separate blocking task OR make gate language self-cancelling (if T-XX status=completed, proceed).

Source: MLInterviewPrep LESSONS.md lines approx 2026-04-17 to 2026-04-19 section.

#### T-P2-587: [DEBT] helixos: Deduplicate 10 stale blocked SYNC tasks (bare-python, stop-cache, setup_python_env.sh)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: The helixos task DB has 10 blocked SYNC/DEBT tasks that are stale duplicates of each other, clogging the backlog.

Duplicates to consolidate or close:
- Bare python fix (4 duplicates): T-P1-184, T-P1-238, T-P1-254, T-P1-319 -- all address the same issue (bare python in helixos settings.json)
- stop-cache removal (3 duplicates): T-P2-207, T-P2-255, T-P2-320 -- all address deprecated stop-cache in helixos test_check.py
- setup_python_env.sh: T-P2-187 (overlaps with bare-python tasks)
- template stop-cache: T-P2-208
- session_context propagation: T-P2-239

Action: verify current helixos state (does bare python still exist? does test_check.py still have stop-cache?), close duplicates keeping only the newest or most complete, and consolidate survivors into 2 clean tasks max.

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

> 535 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-21** -- T-P1-597: [BQ-UX-02] Phase 1: Refactor BehavioralQuestions Examples tab (CN pitch + drawer). The /behavioral Examples tab's ExampleCard (BehavioralQuestions.tsx:182-334) lags behind the rest of the UI: it uses inl
- [x] **2026-04-21** -- T-P1-596: [BQ-UX-01] Phase 1: Extract parsePitch util + render cn_elevator_pitch in ExampleDrawerContent. Shared-component prep task for BQ Examples tab drawer conversion. All 34 behavioral_examples already have cn_elevator_pi
- [x] **2026-04-21** -- T-P1-595: [KG-MLF-FS-01] Content: leaf 28 — Comprehensive 千级特征筛选与建模 (single-page, all 7 sections + expansions). Author the single comprehensive content page for leaf id=28 (feature-selection-pipeline-1000features). Per user clarific
- [x] **2026-04-21** -- T-P1-588: [KG-MLF-FS-00] Skeleton: new category feature_engineering_selection + 1 leaf + YAML + frontend wiring. Add a new /ml-fundamentals category 'feature_engineering_selection' positioned at CATEGORY_ORDER slot 3 (after classical
- [x] **2026-04-21** -- T-P0-574: [BQ-DEPTH-03] Apply link pruning per audit (gated by user approval of prune list). Apply link pruning per audit output from BQ-DEPTH-02.
- [x] **2026-04-21** -- T-P0-573: [BQ-DEPTH-02] Link distribution audit on 266 question_example_links + prune candidates. Write scripts/audit_bq_link_distribution.py (read-only, no DB writes) and produce docs/bq_link_audit_20260421.md.
- [x] **2026-04-21** -- T-P0-572: [BQ-DEPTH-01] Phase A: Golden-story x Trait matrix doc + free-lunch call-out. Author docs/bq_golden_trait_matrix.md mapping 5 golden (EX-01/15/16/17/30) + 4-5 strong non-golden (EX-14/33/13/20/02) a
- [x] **2026-04-20** -- T-P2-571: Fix MHA node 225: render residual formula + replace emoji with ASCII tags. Per user Discord 2026-04-20: fix residual formula which was in a code span (backticks) so \text{Attn}(x) rendered litera
- [x] **2026-04-20** -- T-P2-570: MHA/MQA/GQA node 225: add dimension-flow clarifier + 3 interview misconceptions. Per user Discord 2026-04-20 (critical distillation of supplied notes): insert dimension-flow invariants (X n-by-d preser
- [x] **2026-04-20** -- T-P2-569: Cross-Entropy/KL node 222: add formal Wasserstein primal + K-R dual definition. Per user Discord 2026-04-20 follow-up: add Kantorovich primal (inf over couplings) + Kantorovich-Rubinstein dual (sup ov
- [x] **2026-04-20** -- T-P2-568: Cross-Entropy/KL node 222: clarify KL is not Earth Mover's / Wasserstein. Per user Discord 2026-04-20: add minimal-diff clarification that KL 'distance' is information-theoretic (not geometric),
- [x] **2026-04-20** -- T-P2-566: Add Lyra MD session with Mary Miller 2026-04-23. Add incoming Lyra MD video session with Mary Miller scheduled Thu 2026-04-23 08:30 AM PDT per user Discord 2026-04-20.
