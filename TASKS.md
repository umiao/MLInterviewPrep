# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-687: [MLI-C] KNN + Weighted KNN ml_coding handwritten solution (new problem row)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Goal
Add a new ml_coding problem covering vanilla KNN classifier + weighted-KNN extension. Style mirrors K-Means(1064) AS-IS.

## Style anchor
- problems.id=1064 K-Means notes (current version) — section structure: 题目描述 / 核心代码 / 关键要点 / 面试追问 / 复杂度.

## Technical content (precise — per user review feedback)
- Vanilla KNN: argpartition top-K + majority vote.
- Weighted KNN — TWO weighting schemes side-by-side:
  - 1/d weighting: **MUST use 1/(d + epsilon)** with explicit small ε (e.g. 1e-9) to handle d=0 case (query point coincides with training point). Document why.
  - Gaussian kernel: w_i = exp(-d_i^2 / (2σ^2)) with σ tuning discussion.
- **Explicit BOTH classification AND regression coverage**:
  - Classification: weighted majority vote OR argmax over weighted class probabilities.
  - Regression: weighted average ŷ = Σw_i y_i / Σw_i.

## Acceptance criteria
1. New problems row via idempotent scripts/seed_knn_<date>.py. Canonical key: title='K-Nearest Neighbors (KNN + Weighted)'. Category='ml_coding'.
2. Notes contain TWO code blocks: (a) vanilla KNN; (b) weighted KNN with both 1/(d+ε) and Gaussian kernel, both classification and regression.
3. Discussion: tie-breaking, K selection (cross-val), curse of dimensionality, KD-tree/Ball-tree for sublinear query.
4. Idempotent: second run = 0 writes.
5. ruff check passes.
6. Manual smoke test: /problems/<new_id> renders; both code blocks highlight; KaTeX for Gaussian formula correct.
7. ALSO add new entry to QuickIndex.tsx ML_PROBLEMS in this same task.

## Dependencies (revised)
- Per user review: T-281 dep was overcautious — style anchor is K-Means(1064) AS-IS, not post-T-281. Dependency removed; parallelize with T-281.

## Files touched
- new: scripts/seed_knn_<date>.py
- new DB row in problems
- src/frontend/src/pages/QuickIndex.tsx (add ML_PROBLEMS entry)

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-282) — see PROGRESS.md.

#### T-P0-688: [MLI-D1] Linear Regression handwritten numpy in ml_coding (closed-form + GD)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Goal
FILL problems.id=1102 'Meta AI-Native Coding - Linear Regression (closed-form X^TX + Ridge/Lasso/SGD follow-ups)' with the actual solution notes. Confirmed during planning: row exists, category='ml_coding', notes IS NULL. The cheat-sheet at company_documents.id=90 indexes this problem via db://1102 but the destination is currently empty.

## Verified during planning
- problems.id=1102 row exists, category='ml_coding', notes IS NULL.
- company_documents.id=90 row 5 of cheat-sheet table prescribes EXACT style hints: '$w = (X^T X)^{-1} X^T y$, np.linalg.lstsq 不显式求逆', complexity '$O(n d^2 + d^3)$'.
- ALL Meta AI-Native sibling problems (1098-1101, 1103-1105) also have NULL notes — broader gap, OUT OF SCOPE for this task.

## Style anchor (TWO sources, both must be read first)
1. problems.id=1064 K-Means — for SECTION STRUCTURE (题目描述 / 核心代码 / 关键要点 / 面试追问 / 复杂度).
2. company_documents.id=90 cheat-sheet row for LR — for COLUMN HINTS (closed-form, Ridge/Lasso/SGD, lstsq prescription, complexity).

## Technical content (precise — per user review feedback)
- **Code MUST NOT use np.linalg.inv**. Use np.linalg.lstsq(X, y, rcond=None) OR np.linalg.solve(X.T @ X, X.T @ y). Comment block must explain WHY: ill-conditioned X^T X amplifies error; lstsq uses SVD/QR internally and is numerically stable. The cheat sheet itself prescribes this — code must not contradict its own index.
- TWO code paths: closed-form (lstsq) and iterative (full-batch GD).
- Follow-ups: Ridge ((X^T X + λI)^{-1} X^T y, again via solve not inv), Lasso (no closed form — coordinate descent / proximal gradient ISTA), SGD variant.
- Complexity: O(nd^2 + d^3) closed-form; O(nd) per GD iteration.

## Acceptance criteria
1. Read problems.id=1064 and company_documents.id=90 in full BEFORE drafting (cite both in PROGRESS.md).
2. UPSERT problems.id=1102 notes via idempotent scripts/seed_linear_regression_<date>.py (sentinel <!-- META_AI_NATIVE_LR_<DATE> -->).
3. NO new problems row — fill the existing 1102.
4. Code section uses lstsq or solve, NEVER inv. Comment explains the numerical-stability reason.
5. Idempotent: second run = 0 writes.
6. ruff check passes.
7. Manual smoke test: /problems/1102 renders; KaTeX for X^T X / Ridge / SGD formulas correct; /companies/31/prep cheat-sheet drawer for LR now resolves to non-empty notes.
8. Add ML_PROBLEMS entry for 1102 in QuickIndex.tsx in this task.

## Dependencies (revised)
- Per user review: T-281 dep was overcautious — style anchor is K-Means(1064) AS-IS. Dependency removed; parallelize with T-281.

## Out of scope (do NOT absorb)
- Meta AI-Native problems 1098-1101, 1103-1105 also have NULL notes. Broader content gap. NOT included in this batch.

## Files touched
- new: scripts/seed_linear_regression_<date>.py
- DB: problems.id=1102 notes (UPSERT, fill from NULL)
- src/frontend/src/pages/QuickIndex.tsx (add ML_PROBLEMS entry)

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-283) — see PROGRESS.md.

#### T-P0-689: [MLI-D2] Logistic Regression handwritten numpy in ml_coding (BCE + GD)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-688
- **Description**: ## Goal
Add Logistic Regression as ml_coding handwritten solution: sigmoid + BCE + GD. Restrained minimal numpy, mirrors LR style established in T-P0-283.

## Style anchor
- T-P0-283 output (filled problems.id=1102) — match exactly.
- problems.id=1064 K-Means — section structure baseline.

## Technical content (precise — per user review feedback)
- Forward: z = X w; p = σ(z) = 1/(1+exp(-z)).
- Loss: BCE = -1/n · Σ [y log p + (1-y) log (1-p)].
- Gradient: ∇w = 1/n · X^T (σ(Xw) - y).
- **Stable BCE formula (give EXPLICIT form, not just 'log-sum-exp')**: per-sample stable BCE = max(z, 0) - z·y + log(1 + exp(-|z|)). Show this in code, not just words. Document why: avoids overflow when |z| large via the |z| trick.
- Multi-class softmax extension: p_k = exp(z_k) / Σ_j exp(z_j); cross-entropy gradient ∇W = 1/n · X^T (P - Y).
- Regularization: L1 (subgradient sign(w)), L2 (2λw added to gradient).

## Acceptance criteria
1. Idempotent scripts/seed_logistic_regression_<date>.py.
2. New problems row, category='ml_coding'. (Confirmed during planning: no Logistic Regression problem exists.)
3. Notes content: 题目描述 / 核心代码 (sigmoid, stable BCE FORMULA in code, ∇=X^T(σ(Xw)-y), full-batch GD; mention softmax extension) / 关键要点 (numerical stability — show the explicit |z| trick, NOT just 'use log-sum-exp'; class imbalance; L1/L2) / 面试追问 (Newton/IRLS, SGD, calibration, Platt scaling) / 复杂度.
4. framework_node_problems insert: link to existing node id=211 'Logistic Regression Loss'.
5. Idempotent: second run = 0 writes.
6. ruff check passes.
7. Manual smoke test: /problems/<id> renders; KaTeX for sigmoid/BCE/gradient/stable-form formulas correct.
8. Add ML_PROBLEMS entry in QuickIndex.tsx.

## Files touched
- new: scripts/seed_logistic_regression_<date>.py
- DB: new problems row + framework_node_problems(node_id=211, problem_id=<new>)
- src/frontend/src/pages/QuickIndex.tsx (add ML_PROBLEMS entry)

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-284) — see PROGRESS.md.

#### T-P0-690: [MLI-D3] Geometric median (Weber problem): L2 distance-sum minimizer + Weiszfeld
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-689
- **Description**: ## Goal
ml_coding application problem: given N points on plane, find point minimizing sum of L2 distances (Weber 问题 / geometric median). Primary: Weiszfeld iteration. Follow-ups: scaling, contrast with L1 version (db://262 Best Meeting Point).

## Categorization rationale (per user review)
- Reviewer flagged: 'geometric median 严格讲属于 robust statistics / numerical optimization, 不是 ML coding'.
- Resolution: ml_coding inclusion criterion is broader than 'pure ML algorithm'. We include problems that are EITHER (a) ML algorithm implementations (KMeans/KNN/LR/LogReg) OR (b) numerical-optimization problems with direct ML/statistics applications. Geometric median qualifies under (b):
  - Weiszfeld = gradient descent on convex L2-sum objective (same algorithmic family as T-283/T-284).
  - Geometric median = M-estimator / robust mean (used in robust regression, robust clustering init).
  - k=1 K-Means with L2 cost gives the centroid; geometric median is the L2 multivariate analog of median; clean pedagogical bridge.
- Lock Combination (T-280) fails BOTH (a) and (b) — pure graph search, no ML/optimization tie. Geometric median passes (b). Different bar, principled.
- Document this rule in the new notes' opening section.

## Style anchor
- T-P0-283 (Linear Regression) and T-P0-284 (Logistic Regression) — minimal-runnable numpy.
- problems.id=1064 K-Means — section structure.

## Technical content (precise — per user review feedback)
- Weiszfeld iteration: x^{(t+1)} = (Σ x_i / d_i^{(t)}) / (Σ 1 / d_i^{(t)}) where d_i^{(t)} = ||x^{(t)} - x_i||.
- **Degeneracy fix MUST cite Vardi & Zhang 1999** ('A modified Weiszfeld algorithm for the Fermat-Weber location problem', Mathematical Programming, 90(3):559-566). Their fix handles the case when iterate hits a sample point (denominator zero) by adding a correction term involving the subgradient of the objective at that sample point.
- 1D case degenerates to median (per-axis); contrast with L1 case (db://262 Best Meeting Point) which uses per-axis median in 2D too.
- Follow-ups: many points → mini-batch SGD on the convex objective; sublinear approximation; relationship to k=1 K-Means (which gives mean for L2² but median-like for L1); outlier robustness vs centroid.

## Acceptance criteria
1. New problems row via idempotent scripts/seed_geometric_median_<date>.py. Title: 'Geometric Median (Weber 问题, L2 距离和最小)'.
2. Notes content:
   - Opening: cite the inclusion-criterion rule (above) explaining why this is ml_coding despite being in robust statistics.
   - 题目描述 with explicit L1/L2 contrast pointing to db://262.
   - 核心代码: Weiszfeld iteration in numpy (~15 lines incl. Vardi-Zhang degeneracy correction). Cite Vardi-Zhang 1999 in comments.
   - 复杂度: O(N) per iter, sublinear iterations in practice.
   - 面试追问: scaling (mini-batch SGD), 1D = median, k=1 K-Means relationship, outlier robustness vs centroid.
3. Cross-link: append to problems.id=262 notes 'L2 版本见 [Geometric Median](db://<new_id>)' (with sentinel for the 262 UPSERT).
4. Idempotent: second run = 0 writes for both UPSERTs.
5. ruff check passes.
6. Manual smoke test: /problems/<new_id> + /problems/262 both render the cross-link drawer correctly.
7. Add ML_PROBLEMS entry in QuickIndex.tsx.

## Files touched
- new: scripts/seed_geometric_median_<date>.py
- DB: new problems row + problems.id=262 notes UPSERT
- src/frontend/src/pages/QuickIndex.tsx (add ML_PROBLEMS entry)

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-285) — see PROGRESS.md.

#### T-P0-691: [MLI-E1] Extend problems.id=73 (Rotate Image) with rectangular n×m generalization
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Goal
Extend problems.id=73 'Rotate Image' (LC 48, currently square-only) notes with the rectangular n×m generalization analysis the user provided in the original brief. PRESERVE the existing square-case content; APPEND the rectangular section.

## Style anchor
- problems.id=73 existing notes (read in full first) — match its current voice.
- problems.id=1064 K-Means — section structure baseline.

## Technical content (verified during planning)
- D₄ dihedral group decomposition: R₉₀ = H ∘ T = T ∘ V; R₁₈₀ = H ∘ V = V ∘ H; R₂₇₀ = V ∘ T = T ∘ H.
- **Tetrahedral group warning MOTIVATION** (per reviewer's question 'where does tetrahedral come from'): the warning is NOT abstract — the user themselves used '四面体群' in the original brief while actually meaning dihedral D₄. The notes' warning section explicitly frames it as 'a common terminology slip' and cites that 四面体群 = A₄ / S₄ (12 / 24 阶, alternating / symmetric group of the tetrahedron) which is unrelated to matrix rotation. Without this context the warning IS jarring; with the framing it makes pedagogical sense.
- **Cate & Twigg (1977), Algorithm 513 — VERIFIED REAL via web search**: Cate, E. G. & Twigg, D. W., 'Algorithm 513: Analysis of in-situ transposition', ACM Transactions on Mathematical Software 3(1):104-110, 1977. Cite precisely. Also reference: Brenner (1973) Algorithm 467 + Wikipedia 'In-place matrix transposition' for additional grounding. FFTW does include in-place transpose code based on this lineage.
- Special cases:
  - 180° (any shape): involution (i,j) ↔ (n-1-i, m-1-j), O(1) extra space single-pass swap.
  - Square 90°: H ∘ T decomposition — transpose (involution on upper-triangle) + horizontal flip (involution), each O(1) extra space.
  - Rectangular 90°: theoretical O(1) via Cate-Twigg cycle-leader enumeration using σ(k) = kn mod (N-1) multiplicative-group structure; FFTW-grade, '面试不写'.
- Complexity lower bound table:
  - 180° any shape: time Ω(nm), space O(1) achievable (involution).
  - Square 90°: time Ω(N²)=Ω(nm), space O(1) achievable (D₄ decomposition).
  - Rectangular 90°: time Ω(nm), space O(1) achievable (Cate-Twigg) but practically Θ(nm) auxiliary.
- '面试可达的最优' 收口语 (honest closing): square + 180° doable on whiteboard; rectangular 90° = O(nm) aux is interview answer; theoretical O(1) exists but not implemented.

## Acceptance criteria
1. UPSERT problems.id=73 notes via idempotent scripts/seed_rotate_image_rect_extension_<date>.py (sentinel <!-- ROTATE_IMAGE_RECT_<DATE> -->).
2. Existing square-case content PRESERVED (do not delete or rewrite — append the rectangular section).
3. Notes append:
   - 题目推广 (n×m 长方)
   - 核心挑战 (in-place 语义在长方下的微妙)
   - 解法层次: 主答案 (开 m×n 辅助 O(nm)) + 特殊情况 (180° / 方阵 90°) + 理论极限 (Cate-Twigg cite + FFTW + Brenner)
   - 群论 D₄ formulas + tetrahedral warning WITH motivating sentence ('一个常见的术语滑步: 四面体群 A_4/S_4 是正四面体的对称群, 12/24 阶, 与矩阵旋转无关')
   - 复杂度下界表
   - 面试可达的最优 收口
4. Idempotent: second run = 0 writes.
5. ruff check passes.
6. Manual smoke test: /problems/73 renders; KaTeX for ∘/H/T/V symbols correct; existing square content still intact.
7. Verify problems.id=73 leetcode_id=48 and existing content preserved (diff before/after).

## Files touched
- new: scripts/seed_rotate_image_rect_extension_<date>.py
- DB: problems.id=73 notes UPSERT (append-style)

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-286) — see PROGRESS.md.

#### T-P0-692: [MLI-E2] Google /companies/3/prep R2 Coding Index doc (links to extended problem 73 via db://)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-691
- **Description**: ## Goal
Build a new R2-coding-only indexing doc for Google (company_id=3). Seeded with the FIRST entry: matrix rotation (links via db://73 to the rectangular-extended notes from T-P0-286). All future index entries reuse ProblemDrawer (db:// scheme) per user requirement.

## Depends on T-P0-286
- The index links db://73 — the linked content must exist (square + rectangular) before smoke test passes. Hard dep on E1.

## Style anchor
- Existing Google company_documents (company_id=3) — check via SELECT DISTINCT doc_kind WHERE company_id=3 to pick the conventional doc_kind ('card_index' or 'prep_note').
- Memory reference_dblc_drawer_links: ALL index entries use db:// (problems) for ProblemDrawer reuse, NEVER cd:// for problems.

## Technical content
- New company_documents row: company_id=3, doc_kind chosen from existing convention, title='[Google] R2 Coding Index'.
- Content: short intro + entry list. First entry = matrix rotation (link via db://73). Document the criterion 'R2 coding only' (excludes R1 system design / behavioral).
- Hub wire-in: if Google has a top-level prep hub doc (check via SELECT id, title FROM company_documents WHERE company_id=3 AND doc_kind='hub_doc'), append a section pointing at the new R2 index via cd://<index_id>.

## Acceptance criteria
1. Read existing Google company_documents (kinds + titles) BEFORE picking doc_kind — cite the choice rationale in PROGRESS.md.
2. NEW company_documents row via idempotent scripts/seed_google_r2_coding_index_<date>.py (sentinel <!-- GOOGLE_R2_INDEX_<DATE> -->).
3. First entry uses db://73 (NEVER cd://73 — that would silently route to a non-existent company_document id=73 per memory feedback_dblc_drawer_links).
4. If Google hub doc exists: UPSERT-append a cd://<index_id> section in the hub.
5. Backend GET /companies/3/prep returns the new index in its response (verify by curl or browser).
6. Idempotent: second run = 0 writes for all UPSERTs.
7. Manual smoke test: http://localhost:5173/companies/3/prep — R2 coding section visible; click matrix-rotation entry → ProblemDrawer opens with full rectangular analysis (from T-P0-286) rendered correctly.
8. URI link audit: python scripts/audit_uri_consistency.py — clean, no broken db:// / cd:// / lc:// links.

## Files touched
- new: scripts/seed_google_r2_coding_index_<date>.py
- DB: new company_documents row + (conditionally) Google hub doc UPSERT

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-287) — see PROGRESS.md.

#### T-P0-693: [MLI-F] Post-batch idempotency re-run + global URI audit + ML_PROBLEMS sanity check
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-692, T-P0-685, T-P0-686, T-P0-687, T-P0-688, T-P0-690
- **Description**: ## Goal (per user review feedback: 'Idempotency 验证: design 上 idempotent + 实际跑过没 = 两件事')
After all 7 content tasks (T-P0-280 through T-P0-287) complete, run a global verification pass to catch any task that PASSED its individual idempotency check but BROKE on a global re-run.

## Acceptance criteria
1. Re-run every seed script touched in this batch in sequence:
   - scripts/seed_kmeans_vanilla_init_<date>.py (T-281)
   - scripts/seed_knn_<date>.py (T-282)
   - scripts/seed_linear_regression_<date>.py (T-283)
   - scripts/seed_logistic_regression_<date>.py (T-284)
   - scripts/seed_geometric_median_<date>.py (T-285)
   - scripts/seed_rotate_image_rect_extension_<date>.py (T-286)
   - scripts/seed_google_r2_coding_index_<date>.py (T-287)
2. Each must report 0 writes / [UNCHANGED]. Any non-zero is a bug — file a regression.
3. python scripts/audit_uri_consistency.py — must be clean.
4. Confirm QuickIndex.tsx ML_PROBLEMS array contains the expected final set:
   - K-Means(1064)
   - KNN(<new from T-282>)
   - Linear Regression(1102)
   - Logistic Regression(<new from T-284>)
   - Geometric Median(<new from T-285>)
   - NOT Lock Combination(1050) — removed in T-280
5. Manual smoke test sweep (~30-45 min budget): visit each new/modified problem URL + /quick-index?section=ml + /companies/3/prep — confirm rendering, no console errors, drawers open correctly.
6. Append a 'batch verification' entry to PROGRESS.md summarizing: 7 tasks completed, global re-run = clean, smoke tests passed.

## Files touched
- None (read-only verification + PROGRESS.md append)

## Why this exists
- Per-task idempotency check is local; doesn't catch order-dependent bugs (e.g., task B writes content that task C's sentinel doesn't recognize).
- Global re-run is the cheapest insurance against partial state corruption from the autonomous batch.

---
[migration 2026-05-02] Moved from root Gen_AI_Proj/.claude/tasks.db (was T-P0-288) — see PROGRESS.md.

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

> 620 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-05-02** -- T-P2-683: [SD-CHEAT-BULK] Backfill cheat_sheet column for 31 remaining SDs (8 eBay + 20 interview + 3 old Pinterest). Followup to in-session 2026-05-01 fix. After T-2026-05-01 patches, 31 SDs still have empty cheat_sheet column. Each need
- [x] **2026-05-02** -- T-P2-666: [SYNC] Promote remaining harness gaps (has-unblocked + session_state.json carve-out) from MLInterviewPrep to template. Two universal harness improvements present in MLInterviewPrep but missing from claude-code-project-template:
- [x] **2026-05-02** -- T-P0-686: [MLI-B] K-Means(1064): add vanilla random-init helper for pedagogical contrast. ## Goal
- [x] **2026-05-02** -- T-P0-685: [MLI-A] Remove Lock Combination from quick-index?section=ml (BFS is not ML coding). ## Goal
- [x] **2026-05-01** -- T-P2-665: [SYNC] Promote 3 new [UNIVERSAL] LESSONS.md entries (2026-04-30) from MLInterviewPrep to template. Three [UNIVERSAL]-tagged lessons from 2026-04-30 in MLInterviewPrep/LESSONS.md are not in claude-code-project-template/L
- [x] **2026-05-01** -- T-P1-682: [SD-TOC-UX] Fix SystemDesignDetail TOC disappearing at page bottom + CN/EN bilingual labels + mobile drawer. USER CONTEXT (2026-05-01, Discord review thread): right-side section TOC on /system-design/<slug> (a) is English-only an
- [x] **2026-05-01** -- T-P0-684: Reschedule Meta AI-Native Coding (Nikhil U.) to Tue 2026-05-05 10:00 PT. Update interview_events row for Nikhil U.'s AI-Native Coding round from Fri 2026-05-01 13:00 PT to Tue 2026-05-05 10:00 
- [x] **2026-04-30** -- T-P2-664: Widen .claude/skills/*/SKILL.md permission carve-out across 4 projects. Same class of harness permission gate that bit T-P1-256/258 earlier today bit T-P1-656 again when inner session tried to
- [x] **2026-04-30** -- T-P1-681: [Meta-Prep-E] Doc 88 §T3 Behavioral 5-Pack — formatting/style polish (paragraph breaks, bold kill-lines, CN-EN dedupe per feedback_content_style_cn_en.md). company_documents.id=88 has solid 5 stories but same formatting inconsistency as doc 87. Concrete edits: (1) split each 
- [x] **2026-04-30** -- T-P1-680: [Meta-Prep-D] Doc 87 §T2 Domain Breadth — formatting/style polish (paragraph breaks, bold/highlight, CN-EN dedupe per feedback_content_style_cn_en.md). company_documents.id=87 has solid content but inconsistent formatting vs golden style. Concrete edits: (1) audit each of
- [x] **2026-04-30** -- T-P1-676: [Drawer-Fix-T6] [FOLLOW-UP] Migrate other 4 affected hubs (Uber id=37/81 + Google id=51/53) from db://→cd://; re-run audit. FOLLOW-UP after Meta hub critical path lands. Migrate the remaining 4 hubs identified in 2026-04-30 audit (PROGRESS.md r
- [x] **2026-04-30** -- T-P0-679: [Meta-Prep-C] Doc 89 §T4-bp Prompt Best Practices — augment with canonical 1-sentence prompt (Version A/B), 30-sec spoken opener, missing pieces of §六 6-pack. Source review attachment §四/§五/§六: doc 89 already aligned philosophically but missing 3 concrete deliverables. Concrete 
- [x] **2026-04-30** -- T-P0-678: [Meta-Prep-B] Doc 86 §T1 Code-Pad Prompt — major rewrite per review (1-sentence Version A prompt, fix Step1 AI-clarify contradiction, replace opener, drop OrderedDict critique, add §六 6-pack). Source review attachment: rewrite company_documents.id=86. Concrete edits: (1) §1 30-sec opener: replace 'Cool. Before I
- [x] **2026-04-30** -- T-P0-677: [Meta-Prep-A] Hub doc 82 schedule cell-merge — fold 11:00/13:00 identical coding rows via <table> rowspan; verify cd://86 + cd://89 remain clickable in MarkdownPreview. Issue: hub schedule table at company_documents.id=82 has two coding rows (11:00 Sai Srujan, 13:00 Nikhil) with byte-iden
- [x] **2026-04-30** -- T-P0-675: [Drawer-Fix-T5] scripts/audit_uri_consistency.py + Meta hub seed migration db://→cd:// + backend integration test + dev-server smoke. Three deliverables in one task — they must land together for the Meta hub to work end-to-end.
- [x] **2026-04-30** -- T-P0-674: [Drawer-Fix-T4] PrepNotesPage discriminated-union DrawerTarget refactor + cd:// wiring + BehavioralQuestions same wiring + Vitest. Goal: Replace the multi-state drawer (lcDrawerId/dbDrawerId) with a single discriminated-union state that makes 'two dra
- [x] **2026-04-30** -- T-P0-673: [Drawer-Fix-T3] New CompanyDocDrawer component + 404 UI + error log + Vitest. Goal: New right-side drawer that resolves cd://N against the new /company-documents/{id} endpoint, with explicit 404/err
- [x] **2026-04-30** -- T-P0-672: [Drawer-Fix-T2] MarkdownPreview cd://N support + onCdLinkClick prop + Vitest. Goal: Add a third URI scheme cd:// (company-document) to MarkdownPreview, peer to existing lc:// and db://.
- [x] **2026-04-30** -- T-P0-671: [Drawer-Fix-T1] Backend GET /company-documents/{id} endpoint (id-only, no company_id required) + pytest 200/404 cases. Goal: Add a company-id-less endpoint so frontend drawers can resolve cd://N without knowing which company owns the doc.
- [x] **2026-04-30** -- T-P0-670: [Meta-AINative-T4] Hub restructure (drawer-link sub-docs) + 临场 Prompt Best-Practices doc. Goal: Two deliverables — (a) restructure existing Meta company_document id=82 ('[Meta] AI-Native Onsite Prep (2026-05-01
