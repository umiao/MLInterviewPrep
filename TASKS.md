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

#### T-P1-747: [PINT-CONCEPTS-H] Concept doc: fill Section 7 - Pinterest-Specific Systems
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-740
- **Description**: Fill the body of `## Pinterest-Specific Systems` in `docs/company/pinterest/system_design_concepts.md`.

Terms covered: Pinnability, Pixie random-walk, Homefeed blender, PinSage paper, ItemSage, Pinterest Lens

Format per term (4-piece template, in 中文 narration with English technical terms per memory `feedback_content_style_cn_en.md`):
  - **English Full Name** (ACRONYM, 中文翻译) — first occurrence
  - 直觉解释: 1-2 句话讲清楚它解决什么问题，关键 idea
  - Pinterest 实际应用: 引用对应的 system_design_*.md 中的具体场景 (1-2 句)
  - 何时选它 vs 替代方案: 一句对比 (e.g., MMOE vs PLE: PLE 解 task-conflict via shared-vs-task-specific expert split)

Use H3 anchors `### {LETTER}-1`, `### {LETTER}-2`, ... so future docs can link via `sd://pinterest-system-design-concepts#h-1`. Add KaTeX formulas where applicable (e.g., DCN-v2 cross layer: $x_{l+1} = x_0 \odot (W_l x_l + b_l) + x_l$).

After write, run `python scripts/seed_pinterest_sd.py` to upsert. Verify body length non-empty in DB.

AC1: section body in markdown file contains 1 H3 sub-section per term listed above.
AC2: each H3 follows the 4-piece template (Full Name expansion + 直觉 + Pinterest 应用 + vs alternative).
AC3: KaTeX-friendly formulas where math is involved (use `$...$` and `$$...$$`).
AC4: re-run seed → DB body updated; localhost:5173/system-design/pinterest-system-design-concepts renders the section without KaTeX errors.
AC5: no Pinterest-specific systems leaked into wrong section (those go in T-H section 7).

#### T-P1-748: [PINT-CONCEPTS-I] Inline acronym expansion: pinterest-ad-ctr
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_ad_ctr.md` (system_designs.id=29), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: DCN-v2, GBDT, CVR/pCVR, oCPM, FM, AutoInt, AUC, ECE, BCE, IPS, PSI, KS-test, Wide & Deep, LightGBM

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-ad-ctr returns updated content; frontend at /system-design/pinterest-ad-ctr renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-749: [PINT-CONCEPTS-J] Inline acronym expansion: pinterest-embeddings
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_embeddings.md` (system_designs.id=30), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: ANN, HNSW, ScaNN, ViT, mBERT, CLIP, PQ, IVF, Faiss, GraphSAGE, NDCG@K, GradNorm, PCGrad

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-embeddings returns updated content; frontend at /system-design/pinterest-embeddings renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-750: [PINT-CONCEPTS-K] Inline acronym expansion: pinterest-chatbot-pins
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_chatbot_pins.md` (system_designs.id=31), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: BiLSTM-CRF, NER, SBERT, DistilBERT, vLLM, DPO, RLHF, SFT, PPO, DML, CLIP, ViT-L/14

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-chatbot-pins returns updated content; frontend at /system-design/pinterest-chatbot-pins renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-751: [PINT-CONCEPTS-L] Inline acronym expansion: pinterest-pin-ranking
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_pin_ranking.md` (system_designs.id=32), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: MMOE, PLE, DLRM, DPP, LambdaRank, CUPED, IPS, position bias

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-pin-ranking returns updated content; frontend at /system-design/pinterest-pin-ranking renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-752: [PINT-CONCEPTS-M] Inline acronym expansion: pinterest-pins-search
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_pins_search.md` (system_designs.id=33), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: LTR, HNSW, IVF, ScaNN, Faiss, ListNet, ListMLE, mBERT, LaBSE, BM25, InfoNCE

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-pins-search returns updated content; frontend at /system-design/pinterest-pins-search renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-753: [PINT-CONCEPTS-N] Inline acronym expansion: pinterest-notification-reco
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_notification_reco.md` (system_designs.id=34), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: WAU/DAU/MAU, QPS, APNs, FCM, IPS, Submodular, Lagrangian dual

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-notification-reco returns updated content; frontend at /system-design/pinterest-notification-reco renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-754: [PINT-CONCEPTS-O] Inline acronym expansion: pinterest-catalog-bulk-update
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: In `docs/company/pinterest/system_design_catalog_bulk_update.md` (system_designs.id=35), locate the FIRST occurrence of each acronym below and expand to `**English Full Name** (ACRONYM, 中文)`. Subsequent occurrences keep the bare acronym. Per user direction (Discord 2026-05-05): only do full-name expansion in-line; deep explanations live in the concept doc, not here.

Acronyms to expand: NDJSON, 2PC, CDC, DLQ, RPO/RTO, SQS, MirrorMaker

Rules:
- Only first occurrence per acronym. Use `Ctrl-F` to verify uniqueness.
- DO NOT add cross-doc deep-dive links (`sd://pinterest-system-design-concepts#...`) -- per user direction inline patches stay minimal.
- DO NOT add explanatory paragraphs. Just the bracketed expansion.
- If an acronym is already expanded inline (✓ in original audit), SKIP it.
- Format edge cases: 
  - `pCTR` → `**predicted Click-Through Rate** (pCTR, 预估点击率)`
  - `oCPM` → `**optimized Cost Per Mille** (oCPM, 优化千次曝光出价)`
  - `Wide & Deep` → `**Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联)` (no acronym)
- After edits, run `python scripts/seed_pinterest_sd.py` to upsert into DB.

AC1: each acronym in the list above appears in expanded form `**Full Name** (ACRONYM, 中文)` at its first occurrence in the file.
AC2: subsequent occurrences of the same acronym remain bare (no double-expansion).
AC3: no new prose paragraphs added (line count delta ≤ +50% of acronym count).
AC4: re-seed clean; GET /system-designs/pinterest-catalog-bulk-update returns updated content; frontend at /system-design/pinterest-catalog-bulk-update renders without markdown errors.
AC5: idempotent re-run of seed produces UPDATE not INSERT.

#### T-P1-772: [PINT-CONCEPTS-P] URI consistency audit + Pinterest tab smoke + close-out
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-740
- **Description**: Final QA pass after all section + inline tasks complete.

Steps:
1. Run `python scripts/audit_uri_consistency.py` (per memory `reference_dblc_drawer_links`). Confirm zero broken `sd://` / `cd://` / `lc://` links across all touched files.
2. Frontend smoke at /system-design?tab=pinterest:
   - 8 Pinterest cards visible, concept doc card included
   - Click concept doc → all 7 H2 sections render with 中文 + English mix
   - KaTeX renders in concept doc without errors
   - Click each of the 7 existing Pinterest topic docs → confirm acronym expansions visible at first occurrence
3. Confirm `python scripts/seed_pinterest_sd.py` is idempotent (8 UPDATEs, no INSERTs).
4. Append a PROGRESS.md close-out entry summarizing the 16-task batch.
5. Delete `scripts/_apply_pinterest_concepts_tasks.py` (this script's source; matches `_apply_*.py` post-run cleanup convention).

AC1: audit_uri_consistency.py exits 0 with no findings against any of the 8 Pinterest docs.
AC2: manual frontend smoke confirms 8 cards + KaTeX-clean concept doc + acronym expansions in topic docs.
AC3: PROGRESS.md has a close-out entry referencing T-A through T-P task IDs.
AC4: `_apply_pinterest_concepts_tasks.py` deleted; tree-clean except for the new concept_md and the 7 patched topic mds + the seed script edit.

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

#### T-P2-725: [MLI-CONTENT] LogReg golden: structural alignment with LR golden (numbered subsections + notation)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Optional structural / stylistic alignment of docs/drafts/logreg_golden_v1.md with
LR golden (scripts/seed_linear_regression_20260502.py). Pure cosmetics; no
correctness changes. Runs LAST in the chain (T-P0-724 -> T-P1-726 -> T-P2-725)
so renumbering accounts for the matrix广义 section that T-P1-726 adds.

Deltas:

7. Section 1 ("Bias augmentation"): T-P0-724 should already have removed
   the prose; this task ensures the heading itself is gone (or folded into
   Section 4 fit).

8. Reorganize top-level structure into LR-style numbered subsections:
   `### 1. 题面 / ### 2. 推导 / ### 3. Dimension argument /
    ### 4. 实现 / ### 5. End-to-end test / ### 6. 面试追问 /
    ### 7. 拓展 / ### 8. 矩阵广义 (multiclass bridge)`
   The 8 sections match LR golden's post-T-P1-726 structure.

   PRESERVE LogReg's existing TL;DR (5-line interview-ready distillation)
   as a pre-### block; do NOT delete it.

9. Notation: USER DECISION 2026-05-04 -- canonical = `w^\top x` (`^\top`).
   Backfill scripts/seed_linear_regression_20260502.py to use `^\top`.
   AC: grep `\^T[^o]` in both files = 0 matches; `\^\top` >= 5 matches.

Acceptance criteria:

- AC1: grep `^### [0-9]\.` in logreg_golden_v1.md returns 8 numbered sections.

- AC2: both LR seed script + LogReg draft use `^\top` exclusively.

- AC3: ProblemDrawer rendering of 1102 + 1107 still passes; curl
  `/api/problems/1102` and `/api/problems/1107` both return notes containing
  `### 8` substring.

- AC4: idempotent reseed -- both seed_linear_regression_20260502.py and
  seed_logreg_golden_v1.py UPDATE then SKIP on second run.

Depends on T-P1-726 (which itself depends on T-P0-724). Full chain:
P0-724 (LogReg bias refactor) -> P1-726 (matrix广义 in both files) ->
P2-725 (cosmetic + notation backfill).

Out of scope: TL;DR backfill onto LR golden; LR's 7+1=8 section structure
stays, only LogReg gets renumbered.

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

#### T-P2-716: [AR-17] Placeholder ticket: PostToolUse heartbeat as fallback if AR-12 porcelain signal proves insufficient
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: **Status**: PLACEHOLDER ONLY. Do NOT implement until trigger condition met.

**Trigger condition** (do not start work until this is observed):
- AR-12 (T-P1-713) has been live for >= 1 week with telemetry collected.
- `logs/wrapper-stats.jsonl` analysis shows AR-12 false-negative rate > 10% (i.e., wrapper false-killed sessions where Claude was working in stdout but had not yet touched working tree -- e.g., stuck in a long Read/Bash loop without an Edit).
- OR user reports a specific failure mode that AR-12's porcelain signal did not catch.

**Goal (when triggered)**: Implement a finer-grained progress signal via PostToolUse hook. Hook writes a heartbeat timestamp to `.claude/heartbeat` on every tool call. Wrapper polls heartbeat freshness; mtime within last N seconds = Claude is alive even if no commit / no working-tree change yet.

**Why deferred**: AR-12 + AR-16 cover the dominant failure modes (uncommitted edits + cold-start hang). Heartbeat adds complexity (hook coordination, file-system race, polling cadence) that may be unnecessary. Wait for data before adding.

**Implementation sketch (for future reference, not to be built now)**:
1. Add PostToolUse hook `.claude/hooks/heartbeat.py` that touches `.claude/heartbeat` on every invocation.
2. In wrapper, on timeout, also stat `.claude/heartbeat`; if mtime within last 60s, treat as InProgress like AR-12 porcelain branch.
3. New telemetry branch: `heartbeat_only` (HEAD unchanged + porcelain unchanged + heartbeat fresh).
4. Same kill switch pattern: `CLAUDE_P_DISABLE_HEARTBEAT_SIGNAL=1`.
5. Clean up stale heartbeat at session start.

**Acceptance criteria (when triggered)**:
1. Trigger condition documented and met (telemetry data referenced).
2. Hook coordinated across MLI + root .claude/hooks/.
3. Wrapper integration parallel to AR-12.
4. Telemetry branch added.
5. Kill switch verified.

**Depends on**: T-P1-713 (AR-12) -- need its telemetry to know if AR-17 is justified.

## Completed Tasks

> 687 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-05** -- T-P1-746: [PINT-CONCEPTS-G] Concept doc: fill Section 6 - Infrastructure & Business KPIs. Fill the body of `## Infrastructure & Business KPIs` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-745: [PINT-CONCEPTS-F] Concept doc: fill Section 5 - Debiasing & LLM Fine-Tuning. Fill the body of `## Debiasing & LLM Fine-Tuning` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-744: [PINT-CONCEPTS-E] Concept doc: fill Section 4 - Evaluation Metrics. Fill the body of `## Evaluation Metrics` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-743: [PINT-CONCEPTS-D] Concept doc: fill Section 3 - Learning-to-Rank Methods. Fill the body of `## Learning-to-Rank Methods` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-742: [PINT-CONCEPTS-C] Concept doc: fill Section 2 - Retrieval & Approximate Nearest Neighbor. Fill the body of `## Retrieval & Approximate Nearest Neighbor` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-741: [PINT-CONCEPTS-B] Concept doc: fill Section 1 - Multi-Task & Ranking Architectures. Fill the body of `## Multi-Task & Ranking Architectures` in `docs/company/pinterest/system_design_concepts.md`.
- [x] **2026-05-05** -- T-P1-740: [PINT-CONCEPTS-A] Create concept-doc skeleton + register seed + fix display_order alignment. Goal: bootstrap a new Pinterest-tab system-design doc that will house all core-concept deep-dives (no inline body yet, s
- [x] **2026-05-05** -- T-P1-739: [Google] Add 蛋糕水平分割线 (sweep line + 离散化 + 线段树 进阶精讲) to R2 Coding Index. User Discord drop 2026-05-05: add new Google custom problem with shallow-easy 'advanced segment tree' deep-dive. Created
- [x] **2026-05-04** -- T-P1-738: Card Game Sum-15 (db://1105 + cd://90 §8) major refactor: dedup/tablify/code-up/kill puffery. User-driven 2026-05-04: compress problems.id=1105 description from 12379→6151 chars; sync §8 card in cd://90; fix '12 对'
- [x] **2026-05-04** -- T-P1-730: Pinterest VO 2026-05-05/06 interviewer roster + CoderPad URL sync (emails 5+6). Update interview_events for Pinterest VO Day 1+2 (5 rounds) per latest schedule emails: Day 1 R1 interviewer Yiyang Zhan
- [x] **2026-05-04** -- T-P0-737: [META-ANC-9-fix] Escape pipe in doc=90 table row 7 (Find Words O-complexity). Discord ad-hoc request 2026-05-04: doc=90 (Meta AI-Native Coding Inventory hub, company_id=31) row 7 broken because $O(\
