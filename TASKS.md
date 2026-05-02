# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

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

#### T-P2-697: [KMEANS-GOLDEN-3] Extend GoldenToggleButton to support 'problem' item type (cache invalidation + endpoint mapping)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P2-695
- **Description**: WHY: GoldenToggleButton.tsx currently supports framework_node, behavioral_example, company_document (line 8 of the component). To let the ProblemDrawer show a golden toggle, we need the button to know how to call PUT /problems/{id} and which react-query keys to invalidate after a successful flip.

FILES TO TOUCH:
- src/frontend/src/components/ui/GoldenToggleButton.tsx
  * Add 'problem' to the ItemType union (line 8 area)
  * Add endpoint mapping: itemType === 'problem' -> `/problems/${itemId}` (line 31 area where behavioral mapping lives)
  * Add cache invalidation keys for problem (lines 54-60 area). Look at how QuickIndex.tsx and ProblemDrawer.tsx fetch problems via react-query to identify the keys — common candidates: ['problem', id], ['problems'], ['quick-index-ml'].

REFERENCE: The existing 'behavioral_example' branch is the closest analog — lift its logic for 'problem'.

ACCEPTANCE CRITERIA:
1. TypeScript compiles (no type errors) after adding 'problem' to the union
2. The button renders without runtime errors when given itemType='problem'
3. Clicking the toggle in dev (with backend running) successfully PUTs the flag and the UI re-fetches with the new state — test by mounting the button on a tiny test harness or by completing T4 and clicking through the drawer
4. No regressions on the existing 3 item types — open a behavioral example drawer and confirm toggle still works

OUT OF SCOPE: Wiring the button into ProblemDrawer (KMEANS-GOLDEN-4) — this task only extends the button's internal config.

#### T-P2-698: [KMEANS-GOLDEN-4] Wire golden badge + toggle + drawer accent into QuickIndex ML cards and ProblemDrawer
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P2-697
- **Description**: WHY: With schema (T1), endpoint (T2), and button extension (T3) in place, this task is the actual UX-visible change — the user opens /quick-index?section=ml, sees a golden badge on K-Means in the grid, and on opening the drawer can see/toggle golden status with the same orange accent treatment as Behavioral.

FILES TO TOUCH:

A) src/frontend/src/pages/QuickIndex.tsx (lines 71-77, 278-295 area)
   - The ML_PROBLEMS array hardcodes 5 items. We need each card to read is_golden from the problem record. Either:
     (a) Fetch the full problem record via react-query for each ML_PROBLEMS entry (preferred — keeps source of truth in DB), OR
     (b) Add is_golden to the ML_PROBLEMS hardcoded entries (rejected — drifts from DB).
   - Use react-query to fetch /problems/{dbId} for each ML_PROBLEMS entry, render the card with goldenCardClass(is_golden) wrapper (utility at src/frontend/src/utils/goldenStyle.ts) and inline <GoldenBadge golden={is_golden} /> in the card header. Mirror the BehavioralThemePage ExampleCard pattern (lines 156-212 of BehavioralThemePage.tsx).

B) src/frontend/src/components/problems/ProblemDrawer.tsx (lines 1-124)
   - In the drawer header (where the title is rendered), add <GoldenToggleButton itemType='problem' itemId={problem.id} isGolden={problem.is_golden} /> next to the title — exact placement should mirror BehavioralThemePage.tsx lines 139-145 visually.
   - Add an orange top-border accent on the SlideOverPanel when problem.is_golden — mirror BehavioralThemePage.tsx lines 147-149.

REFERENCE: BehavioralThemePage.tsx is the canonical golden-treatment page. Read lines 134-212 in full to understand the badge + toggle + accent pattern before implementing.

ACCEPTANCE CRITERIA:
1. Open http://localhost:5173/quick-index?section=ml — K-Means card (after T6 marks it golden) shows the orange GoldenBadge and golden card styling; the other 4 ML items render normally without the badge
2. Click K-Means → drawer opens with orange top-border accent + GoldenToggleButton in header showing filled star
3. Toggle the star OFF in the drawer → after PUT completes, badge disappears from both the drawer header and the card behind it (cache invalidation works)
4. Toggle back ON → badge reappears on both surfaces
5. Open another ML item (e.g., Linear Regression 1102) → no golden treatment, but the toggle button is present and clicking it makes that item golden too (no item-type discrimination at UI level)
6. No regression: open any algorithm-category problem from another route → drawer behaves as before (the toggle+accent should still appear since they're now part of the drawer, but un-toggled by default — confirm no visual breakage)

OUT OF SCOPE: Backfilling content (KMEANS-GOLDEN-5). Marking K-Means specifically as golden (KMEANS-GOLDEN-6). Visual polish beyond mirroring Behavioral — if you notice density/typography issues in the drawer Markdown, do NOT fix them in this task; flag them as a follow-up task instead.

#### T-P2-699: [KMEANS-GOLDEN-5] Replace problems.id=1064 notes with condensed K-Means golden draft (sentinel-based idempotent UPSERT)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P2-695
- **Description**: WHY: User has produced a condensed K-Means / K-Means++ rewrite (~7KB, vs the existing ~9.8KB notes) optimized for density and review. The new draft is on disk at docs/drafts/kmeans_golden_v1.md. This task replaces problems.notes for id=1064 with that file's contents, using the same sentinel-based idempotent pattern as scripts/seed_kmeans_vanilla_init_20260502.py.

FILES TO TOUCH:
- Create scripts/seed_kmeans_golden_v1.py — model it on scripts/seed_kmeans_vanilla_init_20260502.py but with two differences:
  1. It REPLACES the notes column entirely (not append), since the new draft is a full rewrite
  2. Sentinel: <!-- KMEANS_GOLDEN_V1_20260502 --> as the first line of the new notes value, so the script is idempotent (re-running detects the sentinel and exits 0 without changes)
- Source content path (read at script runtime): docs/drafts/kmeans_golden_v1.md
- Run the script after creating it: `python scripts/seed_kmeans_golden_v1.py` from MLInterviewPrep root

ACCEPTANCE CRITERIA:
1. Script exits 0 on first run — notes column updated, length matches len(file_contents) + sentinel-comment-line overhead
2. Script exits 0 on second run with stdout 'already applied' (or similar) — DB row unchanged (verify with: SELECT length(notes) FROM problems WHERE id=1064;)
3. SELECT substr(notes, 1, 60) FROM problems WHERE id=1064; shows the sentinel as the first line
4. Open http://localhost:5173/quick-index?section=ml → K-Means → drawer renders the new content correctly: TL;DR blockquote, all code blocks formatted, the math $$D(x)^2$$ renders as inline math (not literal text), the comparison table renders as a table
5. No FOREIGN KEY or CHECK constraint violations
6. The seed script does not delete or rename the row, only updates the notes column

OUT OF SCOPE: Marking the row golden (KMEANS-GOLDEN-6). Schema changes (T1).

NOTE FOR THE WORKER: Read scripts/seed_kmeans_vanilla_init_20260502.py first as the canonical seed-script template. Use the same SQLAlchemy session pattern, same sentinel detection style, same logging format.

#### T-P2-700: [KMEANS-GOLDEN-6] Mark K-Means (problems.id=1064) as is_golden=1, set golden_at=now() — the visible payoff
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P2-699
- **Description**: WHY: After T1 adds the schema and T5 lands the new content, this task flips the bit. This is the smallest task in the chain but it's the user-visible deliverable: K-Means becomes the first golden ML example, mirroring the Behavioral golden-example treatment.

APPROACH:
- Create scripts/mark_kmeans_golden_20260502.py (small one-shot) OR call the PUT endpoint via curl in a verification script.
- Recommended: a small Python script under scripts/ that uses the same SQLAlchemy session pattern as other seed scripts. Sentinel: check is_golden first; if already True with a non-null golden_at, exit 0 idempotently.
- SQL equivalent: UPDATE problems SET is_golden=1, golden_at=datetime('now') WHERE id=1064 AND is_golden=0;

ACCEPTANCE CRITERIA:
1. SELECT is_golden, golden_at FROM problems WHERE id=1064; returns (1, '<some ISO timestamp>') — both populated
2. Re-running the script is a no-op (no second timestamp overwrite)
3. Open http://localhost:5173/quick-index?section=ml — K-Means card now shows the golden badge + golden card styling; the drawer header shows the orange accent + filled star toggle (this is the integrated end-to-end test of T1+T2+T3+T4+T5+T6 together)
4. No other rows in problems have been touched (run: SELECT COUNT(*) FROM problems WHERE is_golden=1; — must be exactly 1)

OUT OF SCOPE: Marking other problems as golden. Adjusting schema or UI.

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

> 636 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-02** -- T-P2-696: [KMEANS-GOLDEN-2] Add PUT /problems/{id} support for is_golden field (mirrors behavioral PUT pattern). WHY: GoldenToggleButton (frontend) calls PUT {endpoint} with body { is_golden: bool }. Behavioral examples have a workin
- [x] **2026-05-02** -- T-P2-695: [KMEANS-GOLDEN-1] Add is_golden + golden_at columns to problems table (Alembic migration + ORM model + Problem TS type + /problems API serialization). Schema parity with behavioral_examples / framework_nodes / company_documents — these three already have is_golden + gold
- [x] **2026-05-02** -- T-P2-694: [MLI-F-FOLLOWUP] Fix seed_geometric_median print() Unicode crash on Windows cp1252. ## Found during T-P0-693 batch verification (2026-05-02)
- [x] **2026-05-02** -- T-P2-683: [SD-CHEAT-BULK] Backfill cheat_sheet column for 31 remaining SDs (8 eBay + 20 interview + 3 old Pinterest). Followup to in-session 2026-05-01 fix. After T-2026-05-01 patches, 31 SDs still have empty cheat_sheet column. Each need
- [x] **2026-05-02** -- T-P2-666: [SYNC] Promote remaining harness gaps (has-unblocked + session_state.json carve-out) from MLInterviewPrep to template. Two universal harness improvements present in MLInterviewPrep but missing from claude-code-project-template:
- [x] **2026-05-02** -- T-P0-693: [MLI-F] Post-batch idempotency re-run + global URI audit + ML_PROBLEMS sanity check. ## Goal (per user review feedback: 'Idempotency 验证: design 上 idempotent + 实际跑过没 = 两件事')
- [x] **2026-05-02** -- T-P0-692: [MLI-E2] Google /companies/3/prep R2 Coding Index doc (links to extended problem 73 via db://). ## Goal
- [x] **2026-05-02** -- T-P0-691: [MLI-E1] Extend problems.id=73 (Rotate Image) with rectangular n×m generalization. ## Goal
- [x] **2026-05-02** -- T-P0-690: [MLI-D3] Geometric median (Weber problem): L2 distance-sum minimizer + Weiszfeld. ## Goal
- [x] **2026-05-02** -- T-P0-689: [MLI-D2] Logistic Regression handwritten numpy in ml_coding (BCE + GD). ## Goal
- [x] **2026-05-02** -- T-P0-688: [MLI-D1] Linear Regression handwritten numpy in ml_coding (closed-form + GD). ## Goal
- [x] **2026-05-02** -- T-P0-687: [MLI-C] KNN + Weighted KNN ml_coding handwritten solution (new problem row). ## Goal
- [x] **2026-05-02** -- T-P0-686: [MLI-B] K-Means(1064): add vanilla random-init helper for pedagogical contrast. ## Goal
- [x] **2026-05-02** -- T-P0-685: [MLI-A] Remove Lock Combination from quick-index?section=ml (BFS is not ML coding). ## Goal
