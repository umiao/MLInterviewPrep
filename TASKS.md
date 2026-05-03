# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-703: [MLI-GOLDEN-LOGREG] Logistic Regression (1107) golden-style rewrite + dedicated numerical-stability section
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: **Goal**: Rewrite problem 1107 (Logistic Regression) notes to match K-Means golden style (docs/drafts/kmeans_golden_v1.md (problem 1064)). Spec: `docs/methodology/ml_impl_note_rewrite_spec.md`. **Heaviest cut**: 15,964 -> ~11,200 (>=30%).

**Per-problem anchors (from spec section "Logistic Regression" -- this algorithm's soul is numerical stability)**:
- TL;DR MUST mention the stable BCE form: `np.logaddexp` or `log1p(exp(-|z|))`. This is the deviation-rule case 1 -- soul lives in non-typical place, declare it in TL;DR.
- DEDICATED section "Numerical stability" -- the RARE case where a math derivation IS allowed inline (per spec deviation rule). Show:
  - $\log(1 + e^z)$ overflows when $z$ is large positive
  - the equivalent stable form $\max(z, 0) + \log(1 + e^{-|z|})$
  - 1-2 lines of prose above explaining WHY each form has different overflow behavior
- All other followups stay in cheat sheet (1-3 bullets each):
  - why LR has no closed form (sigmoid -> likelihood non-quadratic, not $X^TX$ form)
  - softmax extension (multi-class generalization)
  - class imbalance (class weight / focal loss)
  - L1 vs L2 regularization geometric meaning (sparsity vs shrinkage)

**Style invariants from `docs/methodology/ml_impl_note_rewrite_spec.md` (AC fails if any violated)**

**Central axis -- "Why in prose, What in code"**:
- Algorithm motivation, geometric intuition, and contrast reasoning go in PROSE BEFORE each code block (1-2 sentences).
- Inside code blocks, the ONLY allowed comments are: shape annotations (`# (n, k)`), step/criterion anchors (`# Step 2`, `# Criterion 3: max iter`), edge cases (`# else: empty cluster fallback`), numerical hints (`# avoid log(0)`).
- Forbidden inside code: algorithm explanations, multi-line comment paragraphs, mixed-CN/EN long sentences, repetition of the prose above. If you see yourself writing inline math-explainer comments, lift them into 1-2 lines of prose ABOVE the code.

**Section granularity = "independently whiteboardable"**:
- `__init__` / class skeleton standalone (one section).
- Each helper standalone: init / E-step / M-step / objective / utility / fit / predict each get their own section.
- Multiple variants of the SAME concept (e.g., uniform vs weighted KNN; vanilla vs ++) live in the SAME section, separated by `**bold subtitle**` -- NOT split into separate sections.
- Main loop standalone, with `# Step N` or `# Criterion N` anchor comments threading the stopping conditions.
- `predict()` standalone even if 1-2 lines.
- Anti-pattern: helpers stuffed into one giant class block. That breaks "whiteboard a single section" usability.

**TL;DR (5-7 lines, blockquote with `>` on every line)**:
- Must enable a reader to recap the algorithm WITHOUT reading anything else.
- Required content: positioning (one line), core loop steps (numbered), edge / degenerate handling, complexity ($O(...)$).
- If the algorithm has a non-typical "soul" (e.g., LR's numerical stability), call it out in TL;DR.

**Variant comparison**:
- Always a TABLE, never prose paragraphs.
- <=5 columns, <=12 chars per cell, headers chosen from {选择方式, 失败模式, 实践默认值, 理论保证, 复杂度}.
- ONE sentence below the table answering "what's the essential difference / when to prefer which".

**Cheat sheet (面试追问)**:
- Format: `> **Q: question text**` followed by 1-3 bullets, each <=2 lines.
- If a Q would need a paragraph, EITHER promote to a body section OR delete -- it does not belong in cheat sheet.

**Typography**:
- All math (including inline complexity) wrapped in `$$...$$`. No bare `$...$`.
- Key terms first occurrence: `**bold**`.
- Algorithm names, library names, variable names: backticks.
- Section dividers: `---`.
- Lists use `-` (never `*`).
- No emoji anywhere.

**Aggressive deletion (do not hesitate)**:
- Paper citations, years, author names.
- "When else would you use X" pedagogical stretch paragraphs.
- "关键要点" / "key takeaways" recap blocks (always duplicate intro).
- Full mathematical proofs (keep only the result formula as a one-liner).
- Multi-line teaching comments inside code.
- Length floor: notes byte length must be at LEAST 30% shorter than baseline. If you fall short, you almost certainly haven't deleted enough -- find more.

**Deviation rule (the ONLY two legitimate exceptions)**:
1. Algorithm's soul lives in a non-typical place (e.g., LR's stable BCE deserves a dedicated section) -- must surface in TL;DR explicitly.
2. A specific followup is high-frequency for THIS algorithm and 1-2 lines aren't enough -- promote to a body section, do NOT stuff into cheat sheet.

**Doubt rule**: when uncertain whether to keep a passage, default to DELETE.


**Workflow**:
1. Audit `db://1107` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1107 (baseline 15,964 chars). Expect substantial cuts -- this is where the spec's "default to delete" rule earns the most.
3. Edit notes content in `scripts/seed_logistic_regression_20260502.py`.
4. Run the seed script.
5. Length check: `len(notes)` <= 11,200.
6. Manual smoke on `/quick-index?section=ml` -> Logistic Regression card. Confirm the stable-BCE math block renders cleanly in KaTeX.

**Acceptance criteria**:
- All style invariants above hold.
- TL;DR explicitly names the stable BCE form (`np.logaddexp` or `log1p(exp(-|z|))`).
- "Numerical stability" is its OWN top-level section (NOT buried in BCE inline comments). It is the ONLY section where math derivation appears.
- Followups (no closed form / softmax / imbalance / L1 vs L2) live in cheat sheet, 1-3 bullets each, never as body sections.
- `len(notes)` <= 11,200 (>=30% cut from 15,964).
- Manual smoke passes on `/quick-index?section=ml`.

#### T-P0-704: [MLI-GOLDEN-GEOMED] Geometric Median (1108) golden-style rewrite + drop '1999' from title (DB + QuickIndex.tsx)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: **Goal**: Rewrite problem 1108 (Geometric Median) notes to match K-Means golden style (docs/drafts/kmeans_golden_v1.md (problem 1064)). Spec: `docs/methodology/ml_impl_note_rewrite_spec.md`. Includes a title rename across two surfaces.

**Per-problem anchors (from spec section "Geometric Median")**:
- TITLE RENAME (drop "1999" per spec): two surfaces.
  - DB title: currently `Geometric Median (Weber 问题, L2 距离和最小)` -> rename to `Geometric Median (Weiszfeld + Vardi-Zhang variant)` via the seed script's `title=` field.
  - Frontend hardcoded label: `src/frontend/src/pages/QuickIndex.tsx` lines 74-80 currently shows "Geometric Median (Weiszfeld + Vardi-Zhang 1999)" -> change "1999" to "variant".
- Core formula (TL;DR or first section): Weiszfeld iteration $$x_{t+1} = \frac{\sum w_i x_i}{\sum w_i}, \quad w_i = \frac{1}{\|x_i - x_t\|}$$
- What Vardi-Zhang fixes: $w_i \to \infty$ degeneracy when iterate lands on a data point. Implementation: detect hit + switch update formula. Show this in code with a clear `# else: anchor-point fallback` style comment.
- Variant TABLE: vanilla Weiszfeld vs Vardi-Zhang with column headers chosen from {退化处理, 收敛性, 实现复杂度}.
- Followups (cheat sheet): vs mean / coordinate-wise median ($L_2$ robust center vs $L_1$ per-axis median); why no closed form (一阶条件含 $x$ 的 norm); convergence (convex + Lipschitz -> Weiszfeld a.e. convergence). Reference the existing `db://262` Best Meeting Point problem for the $L_1$ contrast (already cited in current seed).

**Style invariants from `docs/methodology/ml_impl_note_rewrite_spec.md` (AC fails if any violated)**

**Central axis -- "Why in prose, What in code"**:
- Algorithm motivation, geometric intuition, and contrast reasoning go in PROSE BEFORE each code block (1-2 sentences).
- Inside code blocks, the ONLY allowed comments are: shape annotations (`# (n, k)`), step/criterion anchors (`# Step 2`, `# Criterion 3: max iter`), edge cases (`# else: empty cluster fallback`), numerical hints (`# avoid log(0)`).
- Forbidden inside code: algorithm explanations, multi-line comment paragraphs, mixed-CN/EN long sentences, repetition of the prose above. If you see yourself writing inline math-explainer comments, lift them into 1-2 lines of prose ABOVE the code.

**Section granularity = "independently whiteboardable"**:
- `__init__` / class skeleton standalone (one section).
- Each helper standalone: init / E-step / M-step / objective / utility / fit / predict each get their own section.
- Multiple variants of the SAME concept (e.g., uniform vs weighted KNN; vanilla vs ++) live in the SAME section, separated by `**bold subtitle**` -- NOT split into separate sections.
- Main loop standalone, with `# Step N` or `# Criterion N` anchor comments threading the stopping conditions.
- `predict()` standalone even if 1-2 lines.
- Anti-pattern: helpers stuffed into one giant class block. That breaks "whiteboard a single section" usability.

**TL;DR (5-7 lines, blockquote with `>` on every line)**:
- Must enable a reader to recap the algorithm WITHOUT reading anything else.
- Required content: positioning (one line), core loop steps (numbered), edge / degenerate handling, complexity ($O(...)$).
- If the algorithm has a non-typical "soul" (e.g., LR's numerical stability), call it out in TL;DR.

**Variant comparison**:
- Always a TABLE, never prose paragraphs.
- <=5 columns, <=12 chars per cell, headers chosen from {选择方式, 失败模式, 实践默认值, 理论保证, 复杂度}.
- ONE sentence below the table answering "what's the essential difference / when to prefer which".

**Cheat sheet (面试追问)**:
- Format: `> **Q: question text**` followed by 1-3 bullets, each <=2 lines.
- If a Q would need a paragraph, EITHER promote to a body section OR delete -- it does not belong in cheat sheet.

**Typography**:
- All math (including inline complexity) wrapped in `$$...$$`. No bare `$...$`.
- Key terms first occurrence: `**bold**`.
- Algorithm names, library names, variable names: backticks.
- Section dividers: `---`.
- Lists use `-` (never `*`).
- No emoji anywhere.

**Aggressive deletion (do not hesitate)**:
- Paper citations, years, author names.
- "When else would you use X" pedagogical stretch paragraphs.
- "关键要点" / "key takeaways" recap blocks (always duplicate intro).
- Full mathematical proofs (keep only the result formula as a one-liner).
- Multi-line teaching comments inside code.
- Length floor: notes byte length must be at LEAST 30% shorter than baseline. If you fall short, you almost certainly haven't deleted enough -- find more.

**Deviation rule (the ONLY two legitimate exceptions)**:
1. Algorithm's soul lives in a non-typical place (e.g., LR's stable BCE deserves a dedicated section) -- must surface in TL;DR explicitly.
2. A specific followup is high-frequency for THIS algorithm and 1-2 lines aren't enough -- promote to a body section, do NOT stuff into cheat sheet.

**Doubt rule**: when uncertain whether to keep a passage, default to DELETE.


**Workflow**:
1. Audit `db://1108` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1108 (baseline 9,723 chars).
3. Edit BOTH the title field AND the notes content in `scripts/seed_geometric_median_20260502.py`.
4. Edit `src/frontend/src/pages/QuickIndex.tsx` to replace "1999" with "variant" in the hardcoded label (lines 74-80 area).
5. Run the seed script.
6. Length check: `len(notes)` <= 6,800 (>=30% reduction).
7. Manual smoke: `/quick-index?section=ml` shows label "Vardi-Zhang variant" (no "1999"); drawer title also says "variant"; renders cleanly.

**Acceptance criteria**:
- All style invariants above hold.
- Neither DB title NOR `QuickIndex.tsx` label contains "1999".
- Vanilla Weiszfeld vs Vardi-Zhang as a TABLE on {退化处理, 收敛性, 实现复杂度} with one-sentence summary.
- `len(notes)` <= 6,800.
- Manual smoke passes on `/quick-index?section=ml`.

#### T-P0-705: [MLI-GOLDEN-PROMOTE] Smoke test 4 rewrites on /quick-index?section=ml + mark all 4 is_golden=1
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-701, T-P0-702, T-P0-703, T-P0-704
- **Description**: **Goal**: After T-P0-701..704 pass their own AC, do a workspace-wide visual smoke pass and promote all 4 problems to `is_golden=1` with timestamp.

**Workflow**:
1. Visit `http://localhost:5173/quick-index?section=ml`. Click each of 1102, 1106, 1107, 1108. For each, verify on the RENDERED output (not just markdown source):
   - All KaTeX renders cleanly (no `ParseError` overlays).
   - All code blocks render with syntax highlighting.
   - Variant tables render as proper HTML tables (not raw markdown).
   - Followup cheat-sheet blockquotes render as styled quotes.
2. Cross-check the spec "验收清单" (9 items) against the RENDERED output for each of the 4 problems. The check is whether style invariants hold visually -- not just textually.
3. Hub-doc audit: re-read `scripts/content_meta_anc_inventory_hub.py` line 89 summary cell. If LR rewrite changed the closed-form discussion (e.g., dropped Ridge from main body), confirm the cell still represents what's actually in the note. Update + re-run the hub seed if drifted.
4. Write `scripts/mark_4_ml_problems_golden_20260503.py` modeled on `scripts/mark_kmeans_golden_20260502.py`. For each id in (1102, 1106, 1107, 1108), set `is_golden=1, golden_at=CURRENT_TIMESTAMP`. Idempotent (re-running is a no-op if already golden).
5. Run `python scripts/audit_uri_consistency.py` -- compare findings against pre-rewrite baseline. Zero new failures.

**Acceptance criteria**:
- All 4 problems show the golden badge on `/quick-index?section=ml`.
- Spec "验收清单" verified against RENDERED output for each of the 4 (not just source).
- Hub doc line 89 summary still accurate (or updated alongside, with the hub seed re-run).
- URI consistency audit: zero new failures vs pre-rewrite baseline.
- `mark_4_ml_problems_golden_20260503.py` is committed and idempotent.

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

> 636 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-02** -- T-P2-700: [KMEANS-GOLDEN-6] Mark K-Means (problems.id=1064) as is_golden=1, set golden_at=now() — the visible payoff. WHY: After T1 adds the schema and T5 lands the new content, this task flips the bit. This is the smallest task in the ch
- [x] **2026-05-02** -- T-P2-699: [KMEANS-GOLDEN-5] Replace problems.id=1064 notes with condensed K-Means golden draft (sentinel-based idempotent UPSERT). WHY: User has produced a condensed K-Means / K-Means++ rewrite (~7KB, vs the existing ~9.8KB notes) optimized for densit
- [x] **2026-05-02** -- T-P2-698: [KMEANS-GOLDEN-4] Wire golden badge + toggle + drawer accent into QuickIndex ML cards and ProblemDrawer. WHY: With schema (T1), endpoint (T2), and button extension (T3) in place, this task is the actual UX-visible change — th
- [x] **2026-05-02** -- T-P2-697: [KMEANS-GOLDEN-3] Extend GoldenToggleButton to support 'problem' item type (cache invalidation + endpoint mapping). WHY: GoldenToggleButton.tsx currently supports framework_node, behavioral_example, company_document (line 8 of the compo
- [x] **2026-05-02** -- T-P2-696: [KMEANS-GOLDEN-2] Add PUT /problems/{id} support for is_golden field (mirrors behavioral PUT pattern). WHY: GoldenToggleButton (frontend) calls PUT {endpoint} with body { is_golden: bool }. Behavioral examples have a workin
- [x] **2026-05-02** -- T-P2-695: [KMEANS-GOLDEN-1] Add is_golden + golden_at columns to problems table (Alembic migration + ORM model + Problem TS type + /problems API serialization). Schema parity with behavioral_examples / framework_nodes / company_documents — these three already have is_golden + gold
- [x] **2026-05-02** -- T-P2-694: [MLI-F-FOLLOWUP] Fix seed_geometric_median print() Unicode crash on Windows cp1252. ## Found during T-P0-693 batch verification (2026-05-02)
- [x] **2026-05-02** -- T-P2-683: [SD-CHEAT-BULK] Backfill cheat_sheet column for 31 remaining SDs (8 eBay + 20 interview + 3 old Pinterest). Followup to in-session 2026-05-01 fix. After T-2026-05-01 patches, 31 SDs still have empty cheat_sheet column. Each need
- [x] **2026-05-02** -- T-P2-666: [SYNC] Promote remaining harness gaps (has-unblocked + session_state.json carve-out) from MLInterviewPrep to template. Two universal harness improvements present in MLInterviewPrep but missing from claude-code-project-template:
- [x] **2026-05-02** -- T-P0-702: [MLI-GOLDEN-KNN] KNN (1106) golden-style rewrite per meta-prompt. **Goal**: Rewrite problem 1106 (KNN + Weighted) notes to match K-Means golden style (docs/drafts/kmeans_golden_v1.md (pr
- [x] **2026-05-02** -- T-P0-701: [MLI-GOLDEN-LR] Linear Regression (1102) golden-style rewrite per meta-prompt. **Goal**: Rewrite problem 1102 (Linear Regression) notes to match the K-Means golden style (docs/drafts/kmeans_golden_v1
- [x] **2026-05-02** -- T-P0-693: [MLI-F] Post-batch idempotency re-run + global URI audit + ML_PROBLEMS sanity check. ## Goal (per user review feedback: 'Idempotency 验证: design 上 idempotent + 实际跑过没 = 两件事')
- [x] **2026-05-02** -- T-P0-692: [MLI-E2] Google /companies/3/prep R2 Coding Index doc (links to extended problem 73 via db://). ## Goal
- [x] **2026-05-02** -- T-P0-691: [MLI-E1] Extend problems.id=73 (Rotate Image) with rectangular n×m generalization. ## Goal
- [x] **2026-05-02** -- T-P0-690: [MLI-D3] Geometric median (Weber problem): L2 distance-sum minimizer + Weiszfeld. ## Goal
- [x] **2026-05-02** -- T-P0-689: [MLI-D2] Logistic Regression handwritten numpy in ml_coding (BCE + GD). ## Goal
- [x] **2026-05-02** -- T-P0-688: [MLI-D1] Linear Regression handwritten numpy in ml_coding (closed-form + GD). ## Goal
- [x] **2026-05-02** -- T-P0-687: [MLI-C] KNN + Weighted KNN ml_coding handwritten solution (new problem row). ## Goal
- [x] **2026-05-02** -- T-P0-686: [MLI-B] K-Means(1064): add vanilla random-init helper for pedagogical contrast. ## Goal
- [x] **2026-05-02** -- T-P0-685: [MLI-A] Remove Lock Combination from quick-index?section=ml (BFS is not ML coding). ## Goal
