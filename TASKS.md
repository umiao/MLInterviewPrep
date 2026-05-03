# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-709: [MLI-GOLDEN-2P-KNN] KNN (1106) second pass: shape-per-line + e2e block
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-706, T-P0-707
- **Description**: **Goal**: Apply second-pass rules to problem 1106 (KNN) per `docs/methodology/ml_impl_note_rewrite_spec.md` (post-706). Anchored to the K-Means golden updated in T-P0-707.

**Edits**:

1. **Shape-per-line rewrite** for every numpy block in the note. Specifically:
   - Distance computation section: split `data - x` (broadcast), squared, sum, sqrt onto separate lines with shape comments.
   - Top-K selection: `np.argpartition(dists, K)[:K]` gets a shape line; the resulting indices' shape `(K,)` annotated.
   - Voting: counts/weights array assembly and final argmax each get their own line.
   - The 3 split predict sections from first pass benefit MOST from this rule -- each section already has prose-before-code, now also has shape-per-line within code.

2. **`## End-to-end test` block** at the very end (after all body sections):

```python
## End-to-end test

```python
import numpy as np
np.random.seed(0)
N_train, N_test, D, K = 100, 20, 4, 5
X_train = np.random.rand(N_train, D)
y_train = np.random.randint(0, 3, N_train)
X_test = np.random.rand(N_test, D)
knn = KNN(k=K).fit(X_train, y_train)
preds = knn.predict(X_test)
assert preds.shape == (N_test,)
print(f"Predicted classes: {np.unique(preds)}")
```
```

**Workflow**:
1. Read updated spec `docs/methodology/ml_impl_note_rewrite_spec.md`.
2. Read updated K-Means golden (problem 1064) for shape-per-line reference.
3. Read current `problems.notes` for 1106 (post-first-pass; ~6500 chars from T-P0-705).
4. Edit notes content in `scripts/seed_knn_20260502.py`.
5. Run seed script (idempotent UPSERT).
6. **Run the e2e block** -- save to `/tmp/test_knn_e2e.py` and `python /tmp/test_..._e2e.py`. Must exit 0.
7. Length check: `len(notes)` <= 6500 (no regression vs first-pass; ideally a slight reduction since we're trimming non-shape comments while adding shape annotations).
8. Manual smoke on `/quick-index?section=ml`.

**Acceptance criteria (specific)**:
- Every shape-changing numpy op in the note has its own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- E2e block executes cleanly (exit 0).
- `len(notes)` <= 6500.
- TL;DR byte-identical to first-pass version.

**Two new structural rules to apply (added to spec by T-P0-706 first)**:

**Rule 1 -- Shape-per-line decomposition**:
- Every numpy operation that produces a shape-changing intermediate gets its OWN line with a `# (shape)` comment.
- No 3+ op chains in one expression. Specifically: avoid patterns like `np.array([... for c in centers]).T` -- split into list build, np.array, transpose, each on its own line with shape annotation.
- Inside a code block, prefer "one vector at a time" decomposition: `(d,) -> (n, d) broadcast -> (n,) -> list of K -> (k, n) -> .T -> (n, k) -> argmin -> (n,)` shown as 7 lines, not chained into 1.
- Goal: a reader whiteboarding from this code can trace shapes step-by-step without mental simulation.

**Rule 2 -- End-to-end runnable test block**:
- Every implementation note ends with a `## End-to-end test` section (visible, NOT collapsed) placed AFTER the complete implementation (after main loop / predict / etc.).
- Block must be <=10 lines, use `np.random.rand` (or `np.random.randn`) with named constants `N, D` (and `K` where applicable).
- Must instantiate the class, run `fit()` (and `predict()` if applicable) ONCE, assert output shape with `assert ... .shape == (...)`.
- Must complete in <1s with no external dependencies.
- **Run-and-confirm during the task**: the autonomous session MUST execute the e2e block and confirm it runs cleanly before declaring the task done. Capture stdout to verify no exceptions.

**Per-task common AC**:
- All numpy ops producing shape-changing intermediates have their own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- Trailing `## End-to-end test` block exists, runs cleanly (verified by execution, not just code inspection).
- `len(notes)` stays AT or BELOW the first-pass byte target (no regression -- shape-per-line adds lines but pruning fluff compensates).
- Manual smoke on `/quick-index?section=ml` -- code block renders, e2e test block visually distinct.
- TL;DR unchanged from first pass (per user direction).

#### T-P0-711: [MLI-GOLDEN-2P-GEOMED] Geometric Median (1108) second pass: shape-per-line + e2e block
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-706, T-P0-707, T-P0-704
- **Description**: **Goal**: Apply second-pass rules to problem 1108 (Geometric Median) per `docs/methodology/ml_impl_note_rewrite_spec.md` (post-706). Anchored to the K-Means golden updated in T-P0-707.

**Edits**:

1. **Shape-per-line rewrite** for every numpy block in the note. Specifically:
   - Weiszfeld iteration: `diffs = points - x_t  # (N, D)`, `dists = np.linalg.norm(diffs, axis=1)  # (N,)`, `weights = 1 / dists  # (N,)`, `x_next = (weights[:, None] * points).sum(axis=0) / weights.sum()  # (D,)` -- each on its own line.
   - Vardi-Zhang degenerate-handling branch: shape-per-line for the on-data-point detection + the modified update.
   - The variant comparison TABLE (from first pass) stays unchanged.
   - Title rename done in T-P0-704; second pass does NOT redo it.

2. **`## End-to-end test` block** at the very end (after all body sections):

```python
## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 50, 3
points = np.random.rand(N, D)
gm = GeometricMedian().fit(points)
assert gm.median_.shape == (D,)
print(f"Geometric median: {gm.median_}")
print(f"Mean for comparison: {points.mean(axis=0)}")
```
```

**Workflow**:
1. Read updated spec `docs/methodology/ml_impl_note_rewrite_spec.md`.
2. Read updated K-Means golden (problem 1064) for shape-per-line reference.
3. Read current `problems.notes` for 1108 (post-first-pass; ~6800 chars from T-P0-707).
4. Edit notes content in `scripts/seed_geometric_median_20260502.py`.
5. Run seed script (idempotent UPSERT).
6. **Run the e2e block** -- save to `/tmp/test_geometric_median_e2e.py` and `python /tmp/test_..._e2e.py`. Must exit 0.
7. Length check: `len(notes)` <= 6800 (no regression vs first-pass; ideally a slight reduction since we're trimming non-shape comments while adding shape annotations).
8. Manual smoke on `/quick-index?section=ml`.

**Acceptance criteria (specific)**:
- Every shape-changing numpy op in the note has its own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- E2e block executes cleanly (exit 0).
- `len(notes)` <= 6800.
- TL;DR byte-identical to first-pass version.

**Two new structural rules to apply (added to spec by T-P0-706 first)**:

**Rule 1 -- Shape-per-line decomposition**:
- Every numpy operation that produces a shape-changing intermediate gets its OWN line with a `# (shape)` comment.
- No 3+ op chains in one expression. Specifically: avoid patterns like `np.array([... for c in centers]).T` -- split into list build, np.array, transpose, each on its own line with shape annotation.
- Inside a code block, prefer "one vector at a time" decomposition: `(d,) -> (n, d) broadcast -> (n,) -> list of K -> (k, n) -> .T -> (n, k) -> argmin -> (n,)` shown as 7 lines, not chained into 1.
- Goal: a reader whiteboarding from this code can trace shapes step-by-step without mental simulation.

**Rule 2 -- End-to-end runnable test block**:
- Every implementation note ends with a `## End-to-end test` section (visible, NOT collapsed) placed AFTER the complete implementation (after main loop / predict / etc.).
- Block must be <=10 lines, use `np.random.rand` (or `np.random.randn`) with named constants `N, D` (and `K` where applicable).
- Must instantiate the class, run `fit()` (and `predict()` if applicable) ONCE, assert output shape with `assert ... .shape == (...)`.
- Must complete in <1s with no external dependencies.
- **Run-and-confirm during the task**: the autonomous session MUST execute the e2e block and confirm it runs cleanly before declaring the task done. Capture stdout to verify no exceptions.

**Per-task common AC**:
- All numpy ops producing shape-changing intermediates have their own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- Trailing `## End-to-end test` block exists, runs cleanly (verified by execution, not just code inspection).
- `len(notes)` stays AT or BELOW the first-pass byte target (no regression -- shape-per-line adds lines but pruning fluff compensates).
- Manual smoke on `/quick-index?section=ml` -- code block renders, e2e test block visually distinct.
- TL;DR unchanged from first pass (per user direction).

### P1 -- Should Have (agentic intelligence)

#### T-P1-582: [BQ-DEPTH-11] Bulk probe_notes for remaining ~36 high-probability questions
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-581
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

### P2 -- Nice to Have

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

### P3 -- Stretch Goals

## Blocked

#### T-P1-581: [BQ-DEPTH-10] Primary-story batch: mark is_primary=1 for top 40 high-probability questions
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
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

#### T-P1-627: Add display_label short field to principle_tags so pills show short labels (full phrase in tooltip)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Follow-up to T-P0-626. Pill UI primitive is for short labels; commit e52d568 (2026-04-23) put 33-char-avg phrases in principle_tags. T-P0-626 patches the layout to tolerate long phrases; this ticket fixes the data layer.

GATE (manual, intentional hack): status=blocked even though depends_on=None. Reason: programmatic schema has no 'not_before' field and creating a sentinel-task pattern is overhead for one ticket. Description-only soft gates are insufficient because the autonomous orchestrator's task picker reads only DB fields. Therefore status=blocked is the load-bearing gate. Re-open by manually flipping to active.

UNGATE WHEN: All Uber final-round interviews complete (last is May 4 Coding 2 with Ali Shameli). Manually run: `task_db.py update T-P1-627 --status active`. Re-launch autonomous_run.sh; the orchestrator will then pick this up.

Approach (when ungated):
- Add 'display_label' (~12 chars) to principle_tags source-of-truth seed
- Backend exposes both slug and display_label
- Frontend pills render display_label; tooltip shows full phrase
- Tags missing display_label fall back to label or auto-truncate

AC:
- All 8 EX-01 principle_tags have hand-crafted display_label
- Pills show short labels; tooltip on hover shows full phrase
- T-P0-626's _-to-space rendering becomes unnecessary once this ships

Scope: backend schema + router + frontend pill rendering + seed. M complexity.

#### T-P1-641: [CHEATSHEET-1] Schema + API: add cheat_sheet TEXT column to system_designs, expose in /system-designs/:slug
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Add nullable TEXT column 'cheat_sheet' to system_designs SQLAlchemy model + Alembic-style migration script (scripts/migrate_add_cheat_sheet.py). Update SystemDesign Pydantic schema (read + update) + frontend types/system-design.ts to include cheat_sheet field. Wire into useSystemDesignNotes if edit support is wanted (defer if too big -- read-only is fine for v1). AC: (1) ALTER TABLE migration is idempotent (IF NOT EXISTS / try-except); (2) GET /system-designs/<slug> response includes cheat_sheet (null when empty); (3) GET /system-designs (list endpoint) returns cheat_sheet too so the new tab can render without per-row fetch -- or keep list lean and have new tab call /system-designs/cheat-sheets aggregation endpoint, decide based on payload size; (4) backend tests added; (5) ruff/mypy clean. NO content authoring in this task -- column stays null.

#### T-P1-642: [CHEATSHEET-2] Frontend: add 'Cheat Sheet' tab to /system-design with one-pager card per row
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Add third tab 'Cheat Sheet' to SystemDesignList.tsx alongside 'Interview Prep' and 'eBay Projects'. New tab renders a vertically-stacked single-page list (NOT a grid) of all system_designs entries sorted by display_order. Each entry is a CheatSheetCard component:  (a) sticky-position H2 with title + small badge for category (eBay / Pinterest / Generic / Uber); (b) MarkdownPreview of the cheat_sheet field (so code-fence ascii arch + tables render correctly with KaTeX + GFM); (c) right-edge link 'Full design ->' to /system-design/<slug>; (d) graceful empty state when cheat_sheet is null ('No cheat sheet yet'). Add ?tab=cheatsheet URL synchronization (same pattern as existing tabs). Add a left-side sticky TOC sidebar within the cheat-sheet tab (desktop only) listing all cards by title for quick jump. AC includes a manual smoke test: open /system-design?tab=cheatsheet, verify 35+ cards render, KaTeX formulas render, no console errors, deep-link to ?tab=cheatsheet#<slug> scrolls to that card. Vitest snapshot for the new component.

#### T-P1-643: [CHEATSHEET-3] Add 2 Uber rows to system_designs from doc 85 (Restaurant Rec + Budget-Constrained Promo)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Currently Uber Eats Restaurant Recommendation and Budget-Constrained Promo Recommendation only live inside company_documents id=85 (markdown doc). Promote them to first-class system_designs rows so they appear on /system-design page and the new Cheat Sheet tab.  Steps: (1) Create scripts/seed_uber_system_designs.py (idempotent -- upsert by slug); (2) extract content from doc 85 sections 1.x and 2.x into the corresponding system_designs columns (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) -- DO NOT duplicate, KEEP doc 85 as the canonical narrative source and treat system_designs as the structured projection; (3) slugs: 'uber-eats-restaurant-rec' (display_order 200), 'uber-budget-promo-rec' (display_order 201); (4) populate cheat_sheet field directly from §1.6 and §2.11 (the existing one-pager sections) -- this is the ONLY content authoring in this task; (5) frontend: TOPIC_META in SystemDesignList.tsx may need a new 'Uber' category (or put under 'Specialized'). AC: backend GET /system-designs returns the 2 new rows; clicking renders the existing detail page UI with no errors; doc 85 is unchanged.

#### T-P1-644: [CHEATSHEET-4] Author cheat-sheets for 4 eBay projects (display_order 1-4)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: module-arbitration, llm-orchestration, pbe-pipeline, ranking-allocation. Source each cheat sheet from the existing system_designs.{overview,architecture,dataflow,formulas,production_constraints,tradeoffs,defense,verbal_outline} columns -- do NOT invent new content, distill from what is already there. Format MUST match doc 85 §1.6: (a) code-fence vertical pseudo-arch; (b) keywords block (bold industry jargon); (c) Senior signal table (不及格 vs Staff Golden); (d) mini jargon glossary. Length budget: ~2000 chars per cheat sheet. Write to cheat_sheet column via idempotent seed script scripts/seed_cheat_sheets_ebay_projects.py (upsert by slug, only update if content_hash differs). AC: 4 rows have non-null cheat_sheet; markdown lints; KaTeX renders if formulas used; vitest of CheatSheetCard with one of these 4 as fixture passes.

#### T-P1-645: [CHEATSHEET-5] Author cheat-sheets for 4 eBay reference docs (display_order 5-8)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: database-comparison, distributed-task-queue, vibe-code-engineering-patterns, ml-system-design-patterns. These are reference / pattern docs not single design problems, so the cheat sheet format adapts: (a) for database-comparison -- side-by-side decision matrix (workload -> recommended store) instead of vertical pseudo-arch; (b) for distributed-task-queue -- failure-mode table + idempotency strategy keywords; (c) for vibe-code -- pattern bullet-list with one-line trade-off each; (d) for ml-sd-patterns -- the cross-cutting senior signals from doc 85 §3 are a strong template, mirror that style. Same length budget (~2000 chars), same idempotent seed pattern (scripts/seed_cheat_sheets_ebay_refs.py). AC: 4 rows have non-null cheat_sheet; rendered cards visually distinct from project cards (badge color differs).

#### T-P1-646: [CHEATSHEET-6] Author cheat-sheets for 7 Pinterest ML problems
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Slugs: pinterest-ad-ctr, pinterest-embeddings, pinterest-chatbot-pins, pinterest-pin-ranking, pinterest-pins-search, pinterest-notification-reco, pinterest-catalog-bulk-update. Source from existing system_designs columns AND from any company_documents rows where company.slug='pinterest' and the doc maps to one of these 7 problems (cross-reference by title). Format MUST match doc 85 §1.6 -- vertical pseudo-arch + keywords + senior table + mini glossary. Pinterest-specific jargon to call out: PinSage, GraphSAGE, two-tower, Galaxy item embeddings, Pixie random walk, AutoML reranker -- expand each acronym in the glossary. Idempotent seed: scripts/seed_cheat_sheets_pinterest.py. Length budget per card ~2000 chars. AC: all 7 rows have non-null cheat_sheet; the vibe-code-style 'badge' on the card reads 'Pinterest'; manual smoke test on /system-design?tab=cheatsheet shows them grouped together visually.

#### T-P1-647: [CHEATSHEET-7] Author cheat-sheets for 10 generic SD problems (batch 1: Core Infra + Social/Real-time + Geo)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 1 slugs: interview-url-shortener, interview-rate-limiter, interview-distributed-cache, interview-notification-system, interview-news-feed, interview-chat-system, interview-live-comments, interview-game-leaderboard, interview-ride-sharing, interview-proximity-service. Format per doc 85 §1.6 (vertical pseudo-arch + keywords + senior table + mini glossary). Source from existing system_designs columns. Length ~1500 chars (these are interview-prep concise cards, slightly tighter than the eBay project cards). Idempotent seed: scripts/seed_cheat_sheets_generic_sd_batch1.py. AC: 10 rows have non-null cheat_sheet; ruff/mypy clean; vitest passes.

#### T-P1-648: [CHEATSHEET-8] Author cheat-sheets for 9 generic SD problems (batch 2: Search/Data + Storage/Media + Specialized)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 2 slugs: interview-search-autocomplete, interview-top-k-heavy-hitters, interview-ad-click-aggregator, interview-web-crawler, interview-video-streaming, interview-cloud-storage, interview-price-drop-tracker, interview-online-judge, interview-ticket-reservation, interview-auction-system. (10 slugs total -- batch 2 takes the remainder.) Same format as batch 1 (~1500 chars, doc 85 §1.6 style, idempotent seed scripts/seed_cheat_sheets_generic_sd_batch2.py). AC: every interview-* row in system_designs has non-null cheat_sheet after this task lands.

#### T-P1-649: [CHEATSHEET-9] Smoke test: load /system-design?tab=cheatsheet, verify all 37 cards render, no console errors
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-648
- **Description**: Final integration smoke test (manual + automated): (1) start dev server (npm run dev + uvicorn); (2) navigate to http://localhost:5173/system-design?tab=cheatsheet; (3) verify ALL rows in system_designs have a rendered card (count == row count); (4) zero console errors; (5) KaTeX formulas render where present; (6) deep-link with #<slug> hash scrolls correctly; (7) prev/next nav still works on detail pages; (8) Interview Prep + eBay Projects tabs still render unchanged (regression check). Append a screenshot or text-only confirmation to PROGRESS.md. Add a vitest E2E-ish test that mounts SystemDesignList and asserts all 3 tabs render their expected card count. AC: all 8 verification points pass; no regression in existing tabs.

#### T-P1-657: Invariant-3 promotion: doc 84 §5 N-gram LM + problem 1097 to seed scripts
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Phase 4. Promote earlier session's Uber doc 84 §5 + problem 1097 to seed scripts. **Per reviewer hole #3**: do NOT delete scripts/migrations/add_uber_prob_nextword.py. Better: keep file, replace body with a no-op + DEPRECATED header. Reasons: (a) git history preservation in working tree, not just log; (b) staging / rebuild environments that re-run migrations get a clear deprecation message rather than missing file errors; (c) future readers can grep for the original migration intent.

THREE STEPS:

1. Update scripts/seed_uber_ml_coding_golden.py:
   - Append §5 N-gram LM section to CONTENT (~600 lines from current DB doc 84 -- copy verbatim from `SELECT content FROM company_documents WHERE id=84`)
   - Bump validate_content() length range (currently caps at probably 35-40K, new content is ~49K) and add §5 markers ('## §5' or '## 5. 概率下一个词生成' or 'ngram-next-word')
   - Re-run, expect [UNCHANGED] (since DB content already matches the new CONTENT)

2. Create scripts/seed_uber_ml_coding_problems.py (or extend an existing matching seed):
   - Owns the from-scratch ML coding problems for Uber: problem 1064 (K-Means), problem 1097 (N-gram LM), and ideally also Geometric Median + Linear Regression + Logistic Regression (the 4 §-1 through §-4 problems in doc 84)
   - Idempotent UPSERT on title (or leetcode_id when present)
   - Each row gets the proper company_tags JSON ['Uber'] AND a problem_company_tags row (relevance='likely', source='manual')
   - Notes field includes [db://doc/84#<anchor>] cross-link to the matching section
   - Re-run, expect 5 [UNCHANGED] (since DB already has them via the migration)

3. Replace scripts/migrations/add_uber_prob_nextword.py with no-op + deprecation:
   - First line: `# DEPRECATED 2026-04-30: Logic moved to scripts/seed_uber_ml_coding_golden.py and scripts/seed_uber_ml_coding_problems.py per Invariant 3 (no migration scripts that write to DB).`
   - Body: `if __name__ == '__main__': sys.exit(0)`
   - Keep file in git so future tree references resolve, but it does nothing if executed
   - Same treatment for scripts/migrations/update_pinterest_onsite_itinerary.py (the other this-session migration)

ACCEPTANCE CRITERIA:
- AC1: scripts/seed_uber_ml_coding_golden.py CONTENT now includes §5; second run = [UNCHANGED]
- AC2: scripts/seed_uber_ml_coding_problems.py exists with 5 problems (1064 + 1097 + 3 others); second run = 5×[UNCHANGED]
- AC3: scripts/migrations/add_uber_prob_nextword.py and scripts/migrations/update_pinterest_onsite_itinerary.py both replaced with deprecation no-op; running each prints '[DEPRECATED] no-op' and exits 0
- AC4: T-P0-660 invariant3 lint hook does NOT trigger on the no-op deprecated files (since they no longer contain INSERT/UPDATE) — this proves the lint design works
- AC5: `git diff scripts/migrations/` shows clean rewrites; `git log --follow scripts/migrations/add_uber_prob_nextword.py` still shows full history

DEPENDS ON: T-P0-660 (lint hook should already exist — this task verifies the hook accepts the deprecated files)
COMPLEXITY: M

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

#### T-P2-636: [UBER-VO-5b POST-5/4] Bespoke pages/UberIndex.tsx with 5-tab charter switcher (deferred)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: None
- **Description**: ## Status: DEFERRED post-2026-05-04 per critical review
This is the original T-P0-632 scope (bespoke React page + URL state + drawer state + browser back/forward + accessibility + vitest). Moved out of the 5/4-readiness critical path. Pick up only if the T-P0-632 MVP (id=37 patch) proves insufficient during actual prep usage.

## Trigger to re-prioritize
- I find myself navigating id=37 -> Round 2 -> click link -> target doc -> back button -> click another link, repeatedly, and the friction matters.
- Or: a follow-up Uber recruiter loop schedules another VO requiring deeper navigation.

## Goal (preserved from original plan)
A bespoke \`pages/UberIndex.tsx\` route at \`/companies/uber/index\` mirroring \`pages/QuickIndex.tsx\` pattern: 5 tab pills (LC / ML Coding / ML SD / Behavioral / HR), per-tab card grid, click-to-drawer, URL state, browser back/forward, empty-state copy, ARIA accessibility, vitest coverage.

## Locked decisions inherited from MVP
- Drawer type: SlideOverPanel via existing \`db://N#anchor\` convention (with anchor support added if T-P0-632 surfaces it as missing).
- Behavioral API: \`/behavioral/themes?company=uber\`.
- Implementation Option A: bespoke page (NOT generalize QuickIndex).

## Acceptance criteria (from original T-P0-632)
- All 5 tabs render correct content with stable URL state.
- Card click opens SlideOverPanel with anchor-scroll.
- Browser back/forward preserves tab+drawer state.
- Empty state for charters lacking content.
- Accessibility: role=tab, ARIA-controls, keyboard arrow nav.
- Vitest tab-switch + drawer-open + empty-state.
- No emoji.

## Dependencies
Upstream: T-P0-632 (MVP must ship first; if MVP suffices, this task closes as 'skipped').

## Completed Tasks

> 652 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-03** -- T-P0-710: [MLI-GOLDEN-2P-LOGREG] Logistic Regression (1107) second pass: shape-per-line + e2e block. **Goal**: Apply second-pass rules to problem 1107 (Logistic Regression) per `docs/methodology/ml_impl_note_rewrite_spec.
- [x] **2026-05-02** -- T-P2-700: [KMEANS-GOLDEN-6] Mark K-Means (problems.id=1064) as is_golden=1, set golden_at=now() — the visible payoff. WHY: After T1 adds the schema and T5 lands the new content, this task flips the bit. This is the smallest task in the ch
- [x] **2026-05-02** -- T-P2-699: [KMEANS-GOLDEN-5] Replace problems.id=1064 notes with condensed K-Means golden draft (sentinel-based idempotent UPSERT). WHY: User has produced a condensed K-Means / K-Means++ rewrite (~7KB, vs the existing ~9.8KB notes) optimized for densit
- [x] **2026-05-02** -- T-P2-698: [KMEANS-GOLDEN-4] Wire golden badge + toggle + drawer accent into QuickIndex ML cards and ProblemDrawer. WHY: With schema (T1), endpoint (T2), and button extension (T3) in place, this task is the actual UX-visible change — th
- [x] **2026-05-02** -- T-P2-697: [KMEANS-GOLDEN-3] Extend GoldenToggleButton to support 'problem' item type (cache invalidation + endpoint mapping). WHY: GoldenToggleButton.tsx currently supports framework_node, behavioral_example, company_document (line 8 of the compo
- [x] **2026-05-02** -- T-P2-696: [KMEANS-GOLDEN-2] Add PUT /problems/{id} support for is_golden field (mirrors behavioral PUT pattern). WHY: GoldenToggleButton (frontend) calls PUT {endpoint} with body { is_golden: bool }. Behavioral examples have a workin
- [x] **2026-05-02** -- T-P0-712: [AR-11] MLI run_claude_with_timeout: work-done detection (HEAD diff + WIP exclusion + git fallback). Modify run_claude_with_timeout in MLInterviewPrep/scripts/autonomous_run.sh (around line 102-121). On timeout (rc=124/13
- [x] **2026-05-02** -- T-P0-708: [MLI-GOLDEN-2P-LR] Linear Regression (1102) second pass: shape-per-line + e2e block. **Goal**: Apply second-pass rules to problem 1102 (Linear Regression) per `docs/methodology/ml_impl_note_rewrite_spec.md
- [x] **2026-05-02** -- T-P0-707: [MLI-GOLDEN-2P-KMEANS] K-Means golden (1064) second pass: shape-per-line + e2e block + empty-cluster prose. **Goal**: Update K-Means golden (problem 1064) with the second-pass rules from `docs/methodology/ml_impl_note_rewrite_sp
- [x] **2026-05-02** -- T-P0-706: [MLI-GOLDEN-2P-SPEC] Update ml_impl_note_rewrite_spec.md: shape-per-line + e2e-test-block rules. **Goal**: Update `docs/methodology/ml_impl_note_rewrite_spec.md` to add the two new structural rules from the second-pas
- [x] **2026-05-02** -- T-P0-705: [MLI-GOLDEN-PROMOTE] Smoke test 4 rewrites on /quick-index?section=ml + mark all 4 is_golden=1. **Goal**: After T-P0-701..704 pass their own AC, do a workspace-wide visual smoke pass and promote all 4 problems to `is
- [x] **2026-05-02** -- T-P0-704: [MLI-GOLDEN-GEOMED] Geometric Median (1108) golden-style rewrite + drop '1999' from title (DB + QuickIndex.tsx). **Goal**: Rewrite problem 1108 (Geometric Median) notes to match K-Means golden style (docs/drafts/kmeans_golden_v1.md (
