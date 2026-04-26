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

#### T-P1-616: [PROB-NOTES-04] Rewrite LC#4 (id=89) solution with cleaner sentinel-based partition + 4-fact mental model
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: WHY
User reviewed current LC#4 solution at http://localhost:5173/problems/89 (DB row id=89, leetcode_id=4) and found the boundary handling not ideal. Current code (in problems.notes for id=89) uses inclusive `while iMin <= iMax` + 4-way branched leftMax/rightMin computation (i==0 / j==0 / i==n1 / j==n2). User has a cleaner half-open + sentinel version they want propagated, while preserving the same overall approach (partition binary-search on shorter array) and the detailed Chinese commentary + mental-model section.

USER-PROVIDED REPLACEMENT (verbatim from Discord msg 1497814013814378546, 2026-04-26)
```python
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        n1, n2 = len(nums1), len(nums2)
        if n1 > n2:
            n1, n2 = n2, n1
            nums1, nums2 = nums2, nums1

        # once we determine the split point in nums1, nums2 is determined
        totalLen = n1 + n2
        # we want to find ideal split like:  nums1[:i] and nums2[:j]

        iBeg, iEnd = 0, n1 + 1  # it is legal to iterate to [:n1]

        while iBeg < iEnd:
            i = iBeg + (iEnd - iBeg) // 2
            j = (totalLen + 1) // 2 - i

            iLeftFirstElement = nums1[i - 1] if i >= 1 else float('-inf')
            iRightFirstElement = nums1[i] if i < n1 else float('inf')
            jLeftFirstElement = nums2[j - 1] if j >= 1 else float('-inf')
            jRightFirstElement = nums2[j] if j < n2 else float('inf')

            if iLeftFirstElement > jRightFirstElement:
                iEnd = i
            elif iRightFirstElement < jLeftFirstElement:
                iBeg = i + 1
            else:
                if totalLen % 2 == 1:
                    return max(iLeftFirstElement, jLeftFirstElement)
                else:
                    ret = max(iLeftFirstElement, jLeftFirstElement) + min(iRightFirstElement, jRightFirstElement)
                    ret = ret / 2
                    return ret

        return
```

USER-PROVIDED MENTAL MODEL (must be incorporated as the new core of the '思路' / '注意要点' section)
便于记忆的心智模型 — 记住这 4 件事就行,其他都是推导出来的:

1. 谁短二分谁 -- 保证 `i in [0, n1]`, `j` 是被动算出来的
2. `half = (total + 1) // 2` -- +1 让奇数情况下左半多 1 个,中位数就是 max(left)
3. 正确性条件: `left1 <= right2 AND left2 <= right1` (交叉比较)
4. 失败时的方向: 违反哪个条件就反向调整 `i`
   - `left1 > right2` -> nums1 给左边太多了 -> i 减小
   - `left2 > right1` -> nums1 给左边太少了 -> i 增大

CONTENT RULES (per memory: feedback_lc_notes_chinese.md + feedback_content_style_cn_en.md)
- Prose 中文; code blocks + algorithm names + complexity notation 英文.
- KaTeX math allowed (single-$ now works per memory feedback_math_formatting.md).
- Section structure preserved: '## Median of Two Sorted Arrays' / '### 思路' / '### 我的题解' / '### 注意要点' / '### 复杂度'.
- '### 思路' rewrite to lead with the 4-fact mental model (this is the user's NEW preferred framing).
- '### 注意要点' rewrite to focus on what is now ELEGANT about the new code (sentinel removes 4-way branching, half-open while removes off-by-one), not what was tricky in the OLD code.
- '### 复杂度' unchanged: O(log(min(m,n))) time, O(1) space.

DELIVERABLES
1. `scripts/seed_lc4_notes_rewrite_20260426.py` -- idempotent UPDATE of `problems.notes` WHERE id=89. Pattern: read current notes, compare against target, only UPDATE if different, log [SKIP] on second run. DB-backup-guarded with suffix `_pre_lc4_notes_rewrite`.
2. The seed script's target-content variable (`NEW_NOTES = '''...'''`) is the source of truth for the rewrite -- this is the canonical form per CLAUDE.md invariant 3. Do NOT also paste the markdown into a separate .md file (avoid two-source drift).

ACCEPTANCE CRITERIA
AC1: Script writes new notes to id=89 on first run; `[SKIP]` on second run (idempotent).
AC2: New notes preserve the 5 section headers (思路 / 我的题解 / 注意要点 / 复杂度).
AC3: Code block content matches the user-provided replacement byte-for-byte (after dedent + LF normalization).
AC4: 思路 section explicitly enumerates the 4 mental-model facts numbered 1-4.
AC5: `### 注意要点` section has at least 3 bullets explaining why the new sentinel-based code is cleaner than the prior 4-way-branch version (e.g. 'sentinel `+/- inf` 取代 4 个 `i==0 / j==0 / i==n1 / j==n2` 分支' / 'half-open `while iBeg < iEnd` 避免了 +/-1 off-by-one' / 'cross-check 条件直接对应失败方向').
AC6 (manual smoke per CLAUDE.md rule 5): With backend running, navigate to http://localhost:5173/problems/89; verify ProblemDetailPage renders updated notes with KaTeX math compiling, code block syntax-highlighted, all 5 section headers visible.
AC7 (regression): Full pytest stays green; `/problems/89` API `notes` length > 2500 chars (sanity floor).

DEPENDS ON: None.

COMPLEXITY: S (one row UPDATE + smoke test). Estimate ~80 lines for the seed script + the embedded NEW_NOTES heredoc.

### P2 -- Nice to Have

#### T-P2-584: [BQ-DEPTH-13] Phase C1: probe_qa.md for remaining 4 golden (EX-01/15/16/17) matching EX-30 style
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
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

> 571 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-25** -- T-P2-614: [KG-DESIGN-DUAL-VIEW] Open Q: consolidate vs legitimize ml-fundamentals + pillar2 coexistence. [KG-DESIGN-DUAL-VIEW] Document the dual-view decision as PERMANENT.
- [x] **2026-04-25** -- T-P2-607: F-2: emoji scan check_emoji.py honor CLI args (scan_single_file extraction). Follow-up to T-P1-606 (first emoji-scanner fix commit).
- [x] **2026-04-25** -- T-P1-615: [PROB-SEARCH-01] Pure-numeric search exact-match on leetcode_id (currently '4' returns 50+ irrelevant). WHY
- [x] **2026-04-25** -- T-P1-600: [BQ-TAX-03] Phase 2: Retag existing 34 examples + 115 questions against new taxonomy. Retag all existing behavioral_examples + behavioral_questions against the new themes + facets from BQ-TAX-02.
- [x] **2026-04-25** -- T-P0-613: [KG-FIX-05] Manual smoke + screenshots + HARD MERGE GATE (no auto-merge to main). [KG-FIX-05] Manual smoke test + before/after screenshots + HARD MERGE GATE.
- [x] **2026-04-25** -- T-P0-612: [KG-FIX-04] Schema invariant + convention doc + smoke protocol + LESSONS postmortem. [KG-FIX-04] Schema invariant + path convention doc + LESSONS postmortem +
- [x] **2026-04-25** -- T-P0-611: [KG-FIX-03] Frontend: explicit PILLAR_ORDER map (step=10). [KG-FIX-03] Frontend: replace pillarSortKey() regex in
- [x] **2026-04-25** -- T-P0-610: [KG-FIX-02] Frontend: add ml-fundamentals to PILLAR_STYLES. [KG-FIX-02] Frontend: extend PILLAR_STYLES in
