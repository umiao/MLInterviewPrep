# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-634: [UBER-VO-7] Manual smoke + verification: full multi-charter flow + content correctness pass
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-632, T-P2-633
- **Description**: ## Goal
End-to-end manual verification that ALSO tests learning outcome (verbal recall), not just wiring. Per critical review: 'For a personal prep tool, the ultimate AC is "I can talk about it", not "it renders."'

## Steps (run sequentially)
1. **Doc-level smoke** -- open id=37, scroll to '多 Charter 快速索引' section. Click each of the 5 charter links in turn. Verify each lands on correct target (T-P0-629 doc / T-P0-630 doc / id=33 / behavioral page / id=36).
2. **Anchor-scroll smoke** -- in T-P0-630 (ML SD doc), navigate via URL \`db://NEW_SD_DOC_ID#uber-eats-restaurant-rec\` and \`#budget-promo-recommendation\`. Verify scroll lands at the right H2.
3. **Strengthening verification (T-P1-631)** -- open id=33, search for each of the 10 strengthening keywords (training-serving skew / graceful degradation / two-tower / MMoE / DIN / H3 / position bias / off-policy eval / cluster A/B / three-time-scale). All present.
4. **Heading-stability verification (T-P1-631 invariant)** -- run \`grep -E '^#{1,3} ' id=33-content-before.md > before.txt; ... after.txt; diff before.txt after.txt\`. Diff is empty for HEADING text.
5. **Source-TXT cross-check** -- pick 3 random paragraphs from source TXT golden answers (lines 14-451 Uber Eats; lines 460-974 Budget Promo). Find them verbatim (or near-verbatim with Chinese narration polish) in T-P0-630.
6. **Banner redirect smoke (T-P2-633)** -- open id=81, see banner at top, click \`db://37\`, lands on id=37.

## VERBAL RECALL AC (per critical review's most important point)
For a personal prep tool, 'rendered correctly' is necessary but not sufficient. The real AC:
- [ ] **VR-1**: I can talk through Uber Eats Golden Answer's 6 stages (心态/节奏 -> 需求澄清 -> 规模估算 -> High-level 架构 -> Deep Dive -> 收尾) in **<= 25 minutes** without re-reading.
- [ ] **VR-2**: I can recite Budget Promo Cheatsheet's 7 must-cover items + 5 anti-patterns in **<= 8 minutes** without notes.
- [ ] **VR-3**: For each of the 4 ML Coding items, I can explain the optimal solution + complexity + 1 follow-up in **<= 8 minutes** each.
- [ ] **VR-4**: I can answer 'what's the difference between H3 and geohash in the Uber-Eats context, and why does Uber prefer H3?' in **<= 90 seconds**.
- [ ] **VR-5**: I can answer 'how do you avoid training-serving skew in production rec systems' citing the 3-layer defense (Snapshot + Feature Store + Monitoring) in **<= 2 minutes**.

If any verbal AC fails: file a follow-up task to deepen the corresponding section's content (NOT a wiring fix).

## Scenario matrix
- All wiring + content checks pass + verbal recall passes -> ship.
- Wiring fails -> reopen the relevant T-P0-629/630/631/632/633.
- Wiring passes but verbal recall fails -> file new content-deepening task; this task closes with PARTIAL.
- Source TXT content drift detected -> reopen T-P0-630 with diff.

## Acceptance criteria
- [ ] All 6 wiring steps pass with notes saved to \`logs/uber_vo_smoke_<timestamp>.md\`.
- [ ] Heading-stability diff is empty.
- [ ] All 5 verbal-recall ACs pass on a single sitting practice run.
- [ ] PROGRESS.md entry written with smoke + recall results.
- [ ] Final go/no-go: 'Uber VO prep is ready for May 4 Coding 2 + any future ML/SD round.'

## Dependencies
Upstream: T-P0-632 (MVP), T-P2-633 (banner). Implicitly all of T-P0-628/629/630/631 must be done.

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
- **Depends on**: T-P0-632
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

> 587 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-29** -- T-P2-633: [UBER-VO-6] Add deprecation/redirect banner to legacy id=81 'Uber LC 题库索引视图'. ## Goal
- [x] **2026-04-29** -- T-P1-635: [UBER-VO-2b] Seed audit-discovered NEW ML Coding items (companion to T-P0-629). ## Goal
- [x] **2026-04-29** -- T-P1-631: [UBER-VO-4] Strengthen existing search/recommendation content in id=33 + id=37 (delta-only). ## Priority bump (per critical review)
- [x] **2026-04-29** -- T-P0-632: [UBER-VO-5 MVP] Patch id=37 Round 3+4 with anchor links to new ML Coding/SD docs (deferring full FE page). ## MVP downscope (per critical review)
- [x] **2026-04-29** -- T-P0-630: [UBER-VO-3] Seed company_document: 'Uber ML System Design Golden Answers' (Staff-level). ## Goal
- [x] **2026-04-29** -- T-P0-629: [UBER-VO-2] Seed company_document: 'Uber ML Coding Golden Answer 集合' (Staff-level). ## Goal
- [x] **2026-04-28** -- T-P0-628: [UBER-VO-1] Audit + inventory: extract ML Coding & ML Sys Design content from all Uber sources. ## Goal
- [x] **2026-04-27** -- T-P2-624: [LC545] Seed Boundary of Binary Tree notes (4-state flag DFS + deque appendleft). Discord ad-hoc msg 1498358265019371650. User pasted one-pass DFS solution with ROOT/LEFT/RIGHT/INNER flag classification
- [x] **2026-04-27** -- T-P2-623: [LC855] Seed Exam Room notes (brute-force sorted-list + heap follow-up). Discord ad-hoc msg 1498356808602095685. User pasted LC official editorial brute-force code and asked for notes + explici
- [x] **2026-04-27** -- T-P2-622: [LC384] Seed Shuffle an Array notes (Fisher-Yates + sort-based shuffle distillation) + Uber tag. Discord ad-hoc msg 1498353628937715803. User added their own LC 384 attempt and asked to distill discussion: (1) Fisher-
- [x] **2026-04-27** -- T-P2-621: [LC2861] Seed Maximum Number of Alloys notes (binary-search-on-answer canonical). Discord ad-hoc request msg 1498348552362000474. Write LC 2861 (Maximum Number of Alloys) seed notes to data/mle_prep.db 
- [x] **2026-04-27** -- T-P2-620: [followup] LC 2571 notes rewrite (bit-greedy + NAF formula) + Uber tag. Discord followup. User wrote LC 2571 with the canonical bit-trick (skip zeros + n&3==3 carry / n&3==1 subtract) and aske
