# Progress Log

> Append-only session log. Each session adds an entry at the bottom.
> Never edit previous entries.

<!-- Entry format:

## YYYY-MM-DD HH:MM -- [T-XX-N] Brief Title
- **What I did**: 1-3 sentences on concrete actions taken
- **Deliverables**: List of files created/modified
- **Sanity check result**: What I verified and the outcome
- **Status**: [DONE] Done / [PARTIAL] Partial (what remains) / [BLOCKED] Blocked (why)
- **Request**: Cross off TASK-XXX / Move TASK-XXX to In Progress / No change

-->

> Older entries archived to [archive/progress_log.md](archive/progress_log.md).
> 71 session entries archived as of 2026-04-01.

## 2026-03-28 -- [T-P2-209] Verify db-missing warning already present in session_context.py
- **What I did**: Investigated T-P2-209 which asked to port db_missing_warning from template to MLInterviewPrep session_context.py. Found the feature already exists at lines 475-490 of MLInterviewPrep's session_context.py. The template actually does NOT have this block (grep confirmed 0 matches). Task description had the direction backwards. Marked as completed since the feature is already present.
- **Deliverables**: No code changes needed
- **Sanity check result**: Grep confirmed db_missing_warning exists in MLInterviewPrep (4 matches) and is absent from template (0 matches). All remaining tasks (T-P2-185/186/187/206/207/208) are SYNC tasks targeting helixos or template, blocked by cross-project file permissions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-209 --status completed`
## 2026-03-28 -- [T-P2-185] Add no-bare-python rule to helixos CLAUDE.md Prohibited Actions
- **What I did**: Added the "Never use bare python in hook commands or scripts" rule to both the shared template (blog_proj/shared/claude_md_shared.md) and re-synced helixos CLAUDE.md via sync.py. The rule warns about the Windows Store stub (exit 49) and directs to use /c/Anaconda/python.exe absolute path.
- **Deliverables**: blog_proj/shared/claude_md_shared.md (added rule), helixos/CLAUDE.md (re-synced)
- **Sanity check result**: Grep confirmed "bare.*python" appears at line 93 of helixos CLAUDE.md. Sync script ran successfully.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-185 --status completed`
## 2026-03-31 -- [T-P1-147] ML Fundamentals Doc T5: Naive Bayes from scratch
- **What I did**: Created comprehensive Naive Bayes from-scratch content (599 lines, 21.7K chars). Bayes' theorem foundation and derivation, conditional independence assumption ("Naive") with full justification (4 reasons why it works despite being wrong), parameter complexity comparison. Laplace Smoothing with Dirichlet prior interpretation and alpha analysis. Three variants: Gaussian NB (continuous features, var_smoothing), Multinomial NB (count features, text classification), Bernoulli NB (binary features, explicit absence modeling) with comparison table. Pure Python implementations of all 3 variants with log-space computation and log-sum-exp trick. sklearn verification for all 3 (Iris dataset + 20newsgroups text). Pros/cons analysis, NB vs LR (generative vs discriminative) comparison with Ng & Jordan reference, 5 interview Q&As, practical application guide.
- **Deliverables**: `MLInterviewPrep/data/t5_naive_bayes.md`
- **Sanity check result**: File is 599 lines, 21,709 bytes. Contains 7 Python code blocks (3 from-scratch + 3 sklearn + 1 log-sum-exp), 12 major sections, all required elements verified (Bayes theorem, Naive derivation, Laplace, Gaussian, Multinomial, Bernoulli, sklearn).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-147 --status completed`
## 2026-03-31 -- [T-P1-148] ML Fundamentals Doc T6: Tree models comprehensive
- **What I did**: Created comprehensive tree models from-scratch content (1143 lines, 41.5K chars). Decision Tree fundamentals with 3 impurity measures (Entropy, Gini, Classification Error) and full calculation example. ID3/C4.5/CART three-algorithm comparison with Information Gain, Gain Ratio, Gini derivations and complete "tennis" dataset worked example. Pruning: Pre-Pruning (5 sklearn params), Post-Pruning, CCP with cost-complexity objective derivation and sklearn code. Random Forest: core principle, Variance formula derivation showing Bagging reduces second term and Feature Subsampling reduces correlation (first term), OOB error. AdaBoost: complete algorithm derivation with epsilon/alpha/weight update formulas, exponential loss connection, Decision Stump implementation. GBDT: negative gradient (pseudo-residual) framework for arbitrary loss, Shrinkage analysis, 6 regularization methods. XGBoost/LightGBM/CatBoost comparison with second-order Taylor expansion. Pure Python implementations of Decision Tree, Random Forest, AdaBoost, GBDT with sklearn verification for all 4. 5 interview Q&As, application guide, comprehensive comparison table.
- **Deliverables**: `MLInterviewPrep/data/t6_tree_models.md`
- **Sanity check result**: File is 1143 lines, 41,485 bytes. Contains 9 Python code blocks (4 from-scratch implementations + 4 sklearn verifications + 1 CCP demo), 12 major sections. All required elements verified (ID3/C4.5/CART, Pruning, Random Forest, AdaBoost, GBDT, Shrinkage).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-148 --status completed`
## 2026-03-31 -- [T-P1-149] ML Fundamentals Doc T7: Weight Initialization from scratch
- **What I did**: Created comprehensive weight initialization from-scratch content (731 lines, 27.2K chars). Variance propagation analysis framework with full derivation. Failed initialization analysis: zero init (symmetry problem), too-large init (variance explosion), too-small init (signal vanishing) with demo code. Xavier/Glorot: forward constraint, backward constraint, harmonic compromise derivation, normal and uniform forms, Sigmoid/Tanh applicability analysis. He/Kaiming: ReLU half-interval truncation proof via half-Gaussian integral, factor-2 compensation, fan_in/fan_out modes, Leaky ReLU adjustment formula. Other methods: Orthogonal (QR decomposition, RNN use case), LSUV (data-driven), Fixup (BN-free ResNets). Pure Python implementations of Xavier normal/uniform, He normal/uniform/leaky, Orthogonal init, and variance propagation verification experiment. LoRA initialization strategy (from Doc 17): zero B + random A, why no symmetry breaking issue. PyTorch API verification: all init functions, MLP with hooks for variance tracking, Conv2d fan calculation. 5 interview Q&As, practical lookup table (10 scenarios), formula summary table.
- **Deliverables**: `MLInterviewPrep/data/t7_weight_initialization.md`
- **Sanity check result**: File is 731 lines, 27,150 bytes. Contains 7 Python code blocks (4 from-scratch implementations + 1 variance experiment + 1 PyTorch verification + 1 zero-init demo), 12 major sections. All required elements verified (zero init, Xavier derivation, He derivation, Leaky ReLU, Orthogonal, LoRA, PyTorch API).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-149 --status completed`
## 2026-03-31 -- [T-P0-244] Uber BPS: Update phone screen prep doc with BPS format
- **What I did**: Rewrote docs/uber_phone_screen_prep.md from the old 2-round phone screen format to the recruiter-confirmed BPS (Behavioral + Problem Solving) format. Updated structure: 5min intro, 40-50min coding+D&A, 5min Q&A. Added 9 sections: BPS format overview, time allocation strategy, problem-solving approach, problem categorization by pattern (BFS/DFS 11 problems, UF 3, BS 5, DP 4, monotonic stack, sliding window, OOD 3, greedy/math 3), D&A prep with 2 project walkthroughs and diagram elements, ML fundamentals review (KNN deep-dive + 10 core concepts), HackerRank tips (before/during/gotchas), content area priority summary, and comprehensive BPS checklist. Incorporated 1p3a interview reports for pattern analysis and tips.
- **Deliverables**: `docs/uber_phone_screen_prep.md` (309 lines, 15.5KB)
- **Sanity check result**: All 6 task requirements verified: (1) Updated BPS structure with recruiter timing, (2) D&A prep with project diagrams, (3) ML fundamentals + KNN section, (4) Problem categorization by 8 patterns with 30+ problems, (5) HackerRank tips section, (6) Time allocation table. Cross-reference from uber_hr_call_prep.md still works.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-244 --status completed`
## 2026-03-31 -- [T-P0-241] Uber BPS: Seed 1p3a interview problems into DB
- **What I did**: Created seed script to parse all Uber interview problems from staging/uber题目整理.txt into mle_prep.db. Step 1: Updated 18 existing LC problems (230, 547, 337, 1020, 977, 815, 981, 17, 23, 1197, 1697, 549, 987, 79, 994, 2503, 2858, 2791) with '1point3acres' source badge and [1p3a Uber] interview notes (variants, follow-ups, tips from 1p3a reports). Created LC 1696 (Jump Game VI) as new entry. Step 2: Created 25 custom non-LC problem entries with titles, descriptions, tags, patterns, and detailed notes preserving original Chinese context. Problems include: Purchase Optimization, Customer Revenue & Referral Tracking, Uber Rider Connection Log, Cart & Pricing Engine OOD, Parking Lot OOD, Driver Queue SD, and 19 more. Step 3: Updated Uber BPS interview event (#8) with problem pool reference (44 1p3a-sourced problems: 19 LC + 25 custom).
- **Deliverables**: `scripts/seed_uber_1p3a_problems.py`, `data/mle_prep.db` (updated)
- **Sanity check result**: 19/19 LC problems verified with Uber tag + 1p3a source + notes. 25 custom problems created. Interview event #8 updated with 44-problem reference. Script is idempotent (re-run skips existing entries).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-241 --status completed`
## 2026-03-31 -- [T-P0-241] Supplement: Add missing custom problems + cleanup duplicates
- **What I did**: Created additional seed script (seed_uber_bps_problems.py) that added 8 missing custom problems: Elevator Binary Search (OA), Server Throughput with Heap (OA), Cart & Pricing Engine (OOD), Min Operations n to 0 (NAF), Shortest Subarray with k Distinct Integers, N-ary Tree 3-Part Problem, Min Edge Reversal for Optimal Root (Re-rooting DP), Palindrome Paths in Tree (Bitmask XOR). Also updated interview event description. Cleaned up 6 near-duplicate entries caused by slight title differences between seed scripts. Re-verified all 19 LC problems have Uber tag + 1p3a source + interview notes.
- **Deliverables**: `scripts/seed_uber_bps_problems.py`, `data/mle_prep.db` (updated: 27 custom + 19 LC = 46 total Uber BPS problems)
- **Sanity check result**: 19/19 LC verified OK. 27 custom problems (no duplicates). Interview event updated. 6 duplicates cleaned.
- **Status**: [DONE]
- **Request**: No task status change (T-P0-241 already completed)
## 2026-03-31 -- [T-P0-242] Uber BPS: LC solutions for all 19 Uber-tagged problems
- **What I did**: Created comprehensive solutions document covering all 19 LC problems from Uber BPS interviews. Each solution includes: approach explanation, clean Python code, time/space complexity analysis. CRITICAL follow-ups and variants included: LC 230 (6 approaches: iterative, recursive, kth largest, Morris O(1) space, augmented BST, flatten), LC 981 (3 follow-ups: 1M+ req/sec sharding, thread safety, amortized complexity), LC 17 (10-digit phone number variant with iterative approach), LC 79 (8-direction straight line variant), LC 1197 (finite board variant), LC 1697 (reversed edge weight >= k variant), LC 2858 (re-rooting DP with 1-indexed warning), LC 2791 (bitmask XOR palindrome path counting), LC 1696 (jump +prime ending in 3 variant with sieve). Solutions organized by pattern: tree (230, 337, 549, 987, 2858, 2791), graph/BFS (994, 1020, 815, 1197, 2503), union-find (547, 1697), binary search (981, 977), backtracking (17, 79), heap (23), DP (1696). Session 2: Also seeded all 19 solutions into DB notes field via `scripts/seed_uber_lc_solutions.py` (idempotent).
- **Deliverables**: `docs/uber_bps_lc_solutions.md` (1017 lines), `scripts/seed_uber_lc_solutions.py`, `data/mle_prep.db` (19 problems updated with solution notes)
- **Sanity check result**: 19/19 LC problems verified with solutions in both doc and DB. Script is idempotent (re-run skips existing). 6 variants, 4+ follow-ups documented. All solutions include time/space complexity.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-242 --status completed`
## 2026-03-31 -- [T-P0-243] Uber BPS: Solutions for all 25 custom non-LC interview problems
- **What I did**: Created comprehensive solutions document covering all 25 custom (non-LeetCode) Uber BPS interview problems. Each solution includes: reconstructed problem statement, approach explanation, clean Python code, time/space complexity, edge cases, and follow-ups. Key problems with detailed follow-ups: (3) Rider Connection Log -- Union Find base + BFS rebuild for block events, (6) Cart & Pricing Engine OOD -- Strategy pattern with surge/membership/promo rules and receipt breakdown, (16) Parking Lot OOD -- O(1) optimized version with free-spot queues, (19) Re-rooting DP for edge reversal, (20) Palindrome paths with bitmask XOR. Problems organized by pattern: Binary Search (1,4,13,15), BFS/DFS (7,22,23,25), Union Find (3), DP (18,19,20), Greedy (9,17), Monotonic Stack (11), Sliding Window (10), Heap (5), OOD (2,6,16), Grid (8,21), Tree (14), Tracking (12). Summary table and pattern quick reference included.
- **Deliverables**: `docs/uber_bps_custom_solutions.md` (2615 lines, 25 problems)
- **Sanity check result**: 25/25 problems verified with solutions. All follow-ups from task spec covered. Summary table matches all problems. Pattern quick reference cross-references all 25.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-243 --status completed`
## 2026-03-31 -- [T-P1-247] Uber BPS: Problem pattern cheat sheet by algorithm
- **What I did**: Created comprehensive pattern cheat sheet organizing all 44 Uber BPS problems (19 LC + 25 custom) by algorithm pattern. 14 pattern sections each with: recognition signals, code template, problem table with key insights and complexity, and practical tips. Includes full complexity summary tables for both LC and custom problems, plus a decision-tree flowchart for pattern recognition during interviews.
- **Deliverables**: `docs/uber_bps_pattern_cheatsheet.md` (721 lines, 14 patterns, 44 problems)
- **Sanity check result**: All 19 LC problems and 25 custom problems present in summary tables. Every problem appears in at least one pattern section. Decision tree covers all major pattern signals.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-247 --status completed`
## 2026-03-31 -- [T-P0-243] Seed custom solutions into DB notes
- **What I did**: Created `scripts/seed_uber_custom_solutions.py` to parse `docs/uber_bps_custom_solutions.md` and seed detailed solutions into DB notes field for all 22 custom problems (3 LC variants correctly skipped). Script is idempotent via `[Uber BPS Custom Solution]` tag check. Also committed the solutions doc (2615 lines) and pattern cheat sheet from previous uncommitted sessions.
- **Deliverables**: `scripts/seed_uber_custom_solutions.py`, `data/mle_prep.db` (22 problems updated with 1700-6200 char solution notes each)
- **Sanity check result**: 22/22 custom problems seeded, 3 LC variants skipped. Re-run produces 0 updates (idempotent). All notes contain Python code blocks and complexity analysis.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-243 --status completed`
## 2026-03-31 -- [T-P1-245] Create D&A prep document for Uber BPS
- **What I did**: Committed `docs/uber_bps_design_architecture.md` (614 lines) created in a prior session. Document covers: 2 project showcases (Ranking-as-Allocation, LLM Eval Pipeline) with ASCII diagrams, end-to-end flows, and trade-off discussions; STAR-T trade-off framework; 5 Uber system design patterns (Driver Maps, Shopping Cart, Driver Queue, ETA, Food Ordering); common D&A follow-ups from 1p3a reports; communication tips; practice checklist.
- **Deliverables**: `docs/uber_bps_design_architecture.md`
- **Sanity check result**: All 4 task requirements met: (1) project showcases with diagrams, (2) trade-off discussions, (3) 5 Uber SD patterns, (4) 1p3a follow-ups. Document cross-references `uber_phone_screen_prep.md`.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-245 --status completed`
## 2026-03-31 -- [T-P1-246] KNN from-scratch + ML fundamentals review
- **What I did**: Created `docs/uber_bps_knn_ml_fundamentals.md` (679 lines) covering KNN implementation from scratch with full Python class (classification + regression, 4 distance metrics, weighted voting), k selection strategies, optimization data structures (KD-Tree, Ball Tree, LSH), 6 KNN interview questions with answers, and ML fundamentals review (bias-variance, overfitting/regularization, cross-validation, evaluation metrics, feature engineering). Includes quick-fire Q&A cheat sheet for the ~5min ML segment.
- **Deliverables**: `docs/uber_bps_knn_ml_fundamentals.md`
- **Sanity check result**: All 5 task requirements met: (1) KNN from scratch with distance metrics/k selection/weighted KNN, (2) classification vs regression, (3) KD-Tree/Ball Tree/LSH optimization, (4) interview Qs covering curse of dimensionality/feature scaling/categorical features, (5) ML fundamentals: bias-variance/overfitting/CV/metrics.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-246 --status completed`
## 2026-03-31 -- [T-P2-240] Add _temp*.json pattern to .gitignore
- **What I did**: Added `_temp*.json` and `_temp*.py` patterns to `.gitignore` to prevent accidental commits of temp artifacts from content seeding scripts.
- **Deliverables**: `.gitignore` (updated)
- **Sanity check result**: `_temp_docs.json` no longer appears in `git status` output after adding the pattern.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-240 --status completed`
## 2026-03-31 -- [T-P2-248] Create timed mock interview problem sets
- **What I did**: Created `docs/uber_bps_mock_sets.md` with 3 timed mock BPS interview sets (45min each). Set 1: LC 230 variant + Rider Connection UF. Set 2: LC 994 BFS + Purchase Optimization BS. Set 3: LC 547 graph + Cart Pricing OOD. Each set includes problem statements, follow-ups, scoring rubrics, debrief checklists, and a practice schedule.
- **Deliverables**: `docs/uber_bps_mock_sets.md` (new, 364 lines)
- **Sanity check result**: All 3 sets contain correct problem pairings per task spec. Each has 1 medium (20 min) + 1 medium-hard (20 min) + follow-ups (5 min). Problems reference solutions in existing docs.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-248 --status completed`
## 2026-03-31 -- [T-P0-249] Import Uber BPS prep docs into company_documents
- **What I did**: Imported 8 Uber prep documents into company_documents table (company_id=5). Updated existing doc#3 (Phone Screen Prep, 2499 chars) with full uber_phone_screen_prep.md content (15,479 chars). Inserted 7 new docs: LC Solutions, Custom Solutions, Pattern Cheat Sheet, Design & Architecture, KNN & ML Fundamentals, Mock Interview Sets, HR Call Prep. Updated Uber prep_notes with document index header referencing all 9 documents.
- **Deliverables**: `scripts/import_uber_bps_docs.py` (new), `data/mle_prep.db` (9 Uber docs, 398,963 total chars)
- **Sanity check result**: All 9 documents verified in DB with correct titles, source_type=prep_doc, and content lengths matching source files. Prep_notes updated from 22,889 to 23,788 chars with reference index.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-249 --status completed`
## 2026-03-31 -- [T-P0-250] Organize LinkedIn prep notes into company_documents
- **What I did**: Cleaned up 5 LinkedIn document titles (removed Chinese, made descriptive). Updated LinkedIn prep_notes (company_id=1) with document index header listing all 9 documents (matching Uber format). Added solution notes for 16 key LinkedIn problems that lacked them: LC 210, 380, 236, 314, 127, 176, 181, 366, 311, 362, 394, 1249, 528, 348, 227, 588. These cover the prep checklist problems and top-frequency Questions Index problems.
- **Deliverables**: `scripts/organize_linkedin_docs.py` (new), `data/mle_prep.db` (9 LinkedIn docs with clean titles, 125 problems now have notes)
- **Sanity check result**: All 9 documents verified with proper English titles. prep_notes updated from 1886 to 2736 chars with document index. All 16 key problems confirmed with notes. Total LinkedIn problems with notes increased from 109 to 125.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-250 --status completed`

## 2026-03-31 -- [T-P0-252] Condense ML Fundamentals From-Scratch guide
- **What I did**: Audited all 8 source files (t1-t8, 162K chars total) for code duplication. Identified 5 major duplication categories: mini-batch GD loops (t1/t2/t3), PyTorch training loops (t1/t2/t3), logistic regression L2 variant (t3), sklearn verification patterns (t5/t6), optimizer implementations (t8). Applied targeted condensation: removed duplicate logistic SGD from t1 (covered in t3), merged logistic_regression + logistic_regression_l2 into single function with lam parameter in t3, condensed 3 PyTorch implementations to config table referencing t1 canonical template, removed duplicate GLM section from t3 (identical to t2 Section 10), extracted optimizer template pattern in t8 with collapsible full implementations, consolidated sklearn verifications in t5/t6 to compact format.
- **Deliverables**: `scripts/condense_ml_fundamentals.py` (new condensation script), 6 modified source files (t1/t2/t3/t5/t6/t8), `data/mle_prep.db` (docs 27/28/29 updated with condensed merged content)
- **Sanity check result**: Source files reduced from 162,050 to 151,482 chars (6.5% reduction, 10.5K chars saved). All theory, derivations, and interview Q&A preserved. Key structural improvements: cross-topic references added, duplicate code eliminated, optimizer implementations shown as template + core update logic. DB docs 27/28/29 all updated to 151,774 chars (from 162,209).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-252 --status completed`

## 2026-04-01 -- [T-P0-253] Convert Uber BPS prep docs to Chinese with acronym expansion
- **What I did**: Translated all 7 Uber BPS prep documents to Chinese following chinese_conversion_spec.md rules. Applied consistent acronym expansion on first use (BFS, DFS, DP, UF, BST, OOD, KNN, etc. with full English name + Chinese explanation in bold). Kept all code blocks, section headings, and O() notation in English. Translated all prose, problem statements, follow-ups, tables, and checklists to Chinese. Updated both markdown files and corresponding company_documents DB entries (company_id=5).
- **Deliverables**: 7 translated markdown files (uber_bps_mock_sets.md, uber_phone_screen_prep.md, uber_bps_knn_ml_fundamentals.md, uber_bps_pattern_cheatsheet.md, uber_bps_lc_solutions.md, uber_bps_design_architecture.md, uber_bps_custom_solutions.md), 3 translation scripts (translate_uber_bps_mock_sets.py, translate_uber_phone_screen.py, update_uber_docs_db.py), `data/mle_prep.db` (docs 3/30-35 updated with Chinese content)
- **Sanity check result**: All 7 DB docs validated: Chinese characters present, no formulas inside code blocks. Total markdown size: 224KB (from 214KB original). DB doc sizes: Doc 3=9081, Doc 30=28186, Doc 31=67549, Doc 32=19447, Doc 33=20973, Doc 34=18114, Doc 35=7765 chars.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-253 --status completed`

## 2026-04-01 -- [T-P1-251] Add expandable inline notes to Company Freq tab
- **What I did**: Added expandable inline notes preview to the Company Freq tab on the Problems page. Clicking a problem's notes preview now expands a full-width row below showing the complete solution notes rendered with MarkdownPreview. Added "Expand All Notes" / "Collapse All Notes" toggle button. Added notes count indicator (X/Y with notes) in the progress header. Verified all Uber (44 problems, 42 with notes), LinkedIn, and Adobe problems display notes properly.
- **Deliverables**: `src/frontend/src/pages/Problems.tsx` (added MarkdownPreview import, expandedNotes state, toggleNotes callback, inline expanded note rows with React.Fragment, expand/collapse all button, notes count in header)
- **Sanity check result**: TypeScript type-check passes (tsc --noEmit). Vite build succeeds. No new warnings.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-251 --status completed`

## 2026-04-01 -- [T-P0-258] Fetch LC problem descriptions from leetcode.ca for all missing problems
- **What I did**: Created `scripts/fetch_lc_descriptions.py` that queries mle_prep.db for problems with missing descriptions, fetches from leetcode.ca/all/N.html, parses HTML with custom HTMLParser to extract clean description text, and stores in DB with `description_source='leetcode.ca'`. Supports resume, rate limiting, progress logging, and --dry-run mode. Successfully fetched 605 descriptions (LC IDs 6-1857). Remaining 281 missing: 256 have LC ID > 1857 (not on leetcode.ca), 25 are custom problems without LC IDs.
- **Deliverables**: `scripts/fetch_lc_descriptions.py` (new), `data/mle_prep.db` (613 total leetcode.ca descriptions, up from 3)
- **Sanity check result**: 776/1057 problems (73.4%) now have descriptions. All 610 fetchable problems (LC ID <= 1857) covered. 0 errors, 0 404s during fetch. Ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-258 --status completed`

## 2026-04-01 -- [T-P0-259] Write solution notes for LinkedIn top-50 frequency problems (batch 1)
- **What I did**: Created solution notes for all 50 LinkedIn problems by frequency that lacked notes (ranks 20-106). Each note includes Chinese approach explanation, clean Python code, key techniques, and time/space complexity. Notes range from 224c (trivial problems like Add Two Integers) to 1767c (complex problems like LFU Cache), averaging 774c. Covered diverse patterns: binary search, backtracking, monotonic stack, DP, greedy, data structure design, SQL, tree DFS, and more. Marked all 50 as is_completed=1.
- **Deliverables**: `scripts/seed_linkedin_notes_batch1.py` (25 problems), `scripts/seed_linkedin_notes_batch1b.py` (25 problems), `data/mle_prep.db` (50 new solution notes)
- **Sanity check result**: All 50/50 problems confirmed with notes in DB. Min 224c, max 1767c, avg 774c. All marked completed. Ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-259 --status completed`

## 2026-04-01 -- [T-P0-263] Enrich LinkedIn doc#21 (Probability/Stats) with detailed solutions
- **What I did**: Enriched doc#21 (LinkedIn Probability/Statistics prep notes, 14 questions) from 34594c to 52327c (+17733c). Added Python code to 7 sections that lacked it (Q4 Queueing Theory, Q6 Class Imbalance, Q7 Sampling, Q8 Overfitting, Q9 L1/L2 Regularization, Q10 Random Forest, Q14 Linear vs Logistic). Added "Follow-up" sections to all 13 non-Reservoir questions with 2-3 common interview follow-ups each. Expanded 9 acronyms on first use (CDF, iid, OLS, SMOTE, AUC-ROC, PR Curve, KS test, OOB, SHAP, GLM). Updated appendix quick-reference table with 3 new rows.
- **Deliverables**: `scripts/enrich_linkedin_doc21.py` (enrichment script), `data/mle_prep.db` (doc#21 updated)
- **Sanity check result**: 19 Python code blocks (was 12), 13 follow-up sections (was 0), all 9 acronym expansions verified present, no orphan dollar signs. Ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-263 --status completed`

## 2026-04-01 -- [T-P0-262] Enrich LinkedIn doc#26 (Question Index) with full solutions for all 47 questions
- **What I did**: Enriched doc#26 (LinkedIn Interview Questions Index, 47 questions across 3 categories) from 30198c to 85003c (+54805c). Added comprehensive solutions to all 47 questions: Coding Q1-Q15 (full Python code + approach + complexity), ML Theory Q16-Q23 (detailed explanations with formulas, code, practical examples), ML System Design Q24-Q47 (architecture, components, metrics, trade-offs). Chinese explanations with English technical terms and acronym expansion throughout (CDF, BFS, DFS, DAG, TSDB, BERT, NLP, ANN, LTR, NDCG, MRR, CPM, CPC, RICE, TAM/SAM/SOM, etc.).
- **Deliverables**: `scripts/enrich_linkedin_doc26_a.py` (Q1-Q15, +14273c), `scripts/enrich_linkedin_doc26_b.py` (Q16-Q23, +9700c), `scripts/enrich_linkedin_doc26_c.py` (Q24-Q35, +14675c), `scripts/enrich_linkedin_doc26_d.py` (Q36-Q47, +16157c), `data/mle_prep.db` (doc#26 updated)
- **Sanity check result**: All 47/47 questions confirmed with solutions. Doc grew from 30198c to 85003c. Ruff clean on all 4 scripts.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-262 --status completed`

## 2026-04-01 -- [T-P0-264] Enrich LinkedIn doc#22 (System Design) with detailed solutions
- **What I did**: Enriched doc#22 (LinkedIn System Design Interview Prep Notes, 11 questions) from 32989c to 59880c (+26891c). Added three new sections to all 11 system design questions: API Design (explicit endpoint definitions with request/response schemas), Scalability Analysis (capacity estimation, bottleneck analysis, scaling strategies), and Key Metrics (system metrics, business metrics, model metrics where applicable). Expanded all acronyms with Chinese explanations and English technical terms (QPS, CDN, LB, TSDB, TTL, SSE, TTFT, PII, CMS, LTR, NDCG, MRR, AUC, ONNX, RPC, SSD, SIMD, NRT, LSM, SSTable, FPR, RAG, NER, etc.).
- **Deliverables**: `scripts/enrich_linkedin_doc22_a.py` (Q1-Q4, +8809c), `scripts/enrich_linkedin_doc22_b.py` (Q5-Q8, +8814c), `scripts/enrich_linkedin_doc22_c.py` (Q9-Q11, +8221c), inline Q6 API section (+1047c), `data/mle_prep.db` (doc#22 updated)
- **Sanity check result**: All 11/11 questions confirmed with API Design + Scalability Analysis + Key Metrics sections. Doc grew from 32989c to 59880c. Ruff clean on all 3 scripts.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-264 --status completed`

## 2026-04-01 -- [T-P0-262] Enrich LinkedIn doc#26 (Question Index) with full solutions for all 47 questions
- **What I did**: Enriched doc#26 (LinkedIn Interview Questions Index, 47 questions) from ~30198c to 141024c (+110826c). Added comprehensive solutions to all 47 questions across 3 sections: Coding (Q1-Q15, Python solutions + complexity + approach), ML Theory (Q16-Q23, detailed explanations with formulas and code), ML System Design (Q24-Q47, architecture, components, trade-offs, metrics). Added follow-ups to all 47 questions. Expanded acronyms (TF-IDF, ANN, CF, TSDB, CPC, CPM, SMOTE, SHAP, GDPR, OKR, etc.). Chinese explanations with English technical terms throughout.
- **Deliverables**: `scripts/enrich_linkedin_doc26.py` (main enrichment, 47 questions), `scripts/enrich_doc26_add_followups.py` (follow-up supplement for 13 questions), `data/mle_prep.db` (doc#26 updated)
- **Sanity check result**: All 47/47 questions have solutions + follow-ups. 25 Python code blocks, 10 SQL code blocks, 0 orphan dollar signs. Ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-262 --status completed`

## 2026-04-01 -- [T-P0-265] Enrich LinkedIn doc#24 (ML Fundamentals + Coding) with detailed solutions
- **What I did**: Enriched doc#24 (LinkedIn ML Fundamentals + Coding, 12 topics) from 33241c to 49895c (+16654c). Added 12 Follow-up Q&A sections (one per topic) with detailed answers, Python code, and practical tables. Expanded 23 acronyms (ANN, BCE, GLM, MLE, GMM, EM, GBDT, SGD, BFS, DFS, NLL, OLS, SSE, OOB, SMOTE, MAE, BPR, CSR, LFU, MAP, SVM, RMSProp, LARS). Added code for: activation functions, softmax/CE, gradient clipping, dropout, Gini/entropy, MLE normal distribution, sparse binary search, LRU cache, cycle detection, critical service finder.
- **Deliverables**: `scripts/enrich_linkedin_doc24.py` (main enrichment), `scripts/enrich_linkedin_doc24_fix.py` (fix for 3 sections with upstream replacement conflicts), `data/mle_prep.db` (doc#24 updated)
- **Sanity check result**: 23/23 acronyms expanded, 0 orphan dollar lines, 38 code blocks (18 Python), 12 follow-up sections. Ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-265 --status completed`

## 2026-04-01 -- [T-P2-256] Verify CLAUDE.md scripts/git-hooks/ reference (no change needed)
- **What I did**: Investigated T-P2-256 which claimed CLAUDE.md references a nonexistent `scripts/git-hooks/` directory. Verified that `scripts/git-hooks/` exists and contains `pre-commit`, and `scripts/setup-hooks.sh` correctly installs from it. The CLAUDE.md File Structure section is already accurate.
- **Deliverables**: None (no changes needed)
- **Sanity check result**: `scripts/git-hooks/pre-commit` exists, `scripts/setup-hooks.sh` references `scripts/git-hooks/` correctly
- **Status**: [DONE] - task description was based on incorrect information
- **Request**: `task_db.py update T-P2-256 --status completed`

## 2026-04-01 -- [T-P2-257] Remove unused stop cache functions from hook_utils.py (BLOCKED)
- **What I did**: Confirmed `check_stop_cache` and `write_stop_cache` are dead code in `.claude/hooks/hook_utils.py` (only used in `shared/hooks/` template files, not active hooks). Attempted to remove them but edits to `.claude/hooks/hook_utils.py` are blocked by sensitive file permissions.
- **Deliverables**: None (blocked)
- **Status**: [BLOCKED] - sensitive file permissions prevent editing `.claude/hooks/hook_utils.py`
- **Request**: `task_db.py update T-P2-257 --status blocked`

## 2026-04-02 -- [T-P2-186, T-P2-206] Mark already-done sync tasks + triage remaining blocked tasks
- **What I did**: Verified T-P2-186 (ruff version-drift lesson) and T-P2-206 (2 universal lessons) are already present in helixos LESSONS.md (items 8 and 18). Marked both as completed. Attempted T-P2-208 (template test_check.py) and T-P2-207 (helixos test_check.py) but all `.claude/hooks/` files across projects are blocked by sensitive file permissions. Marked T-P2-187, T-P2-207, T-P2-208, T-P2-239, T-P2-255 as blocked.
- **Deliverables**: TASKS.md updated via task_db.py
- **Sanity check result**: helixos LESSONS.md items 8 (ruff pin) and 18 (task ID grammar) match the propagated lessons
- **Status**: [DONE] - no unblocked tasks remain
- **Request**: All active tasks marked completed or blocked

## 2026-04-03 -- [T-P1-156] Baking Studio: Backend API routes
- **What I did**: Created FastAPI router with all 10 endpoints (CRUD recipes, scale, inventory, ingredients) and Pydantic schemas. Registered router in main.py. Defined SIZE_RATIOS constant.
- **Deliverables**: `schemas/baking.py` (new), `routers/baking.py` (new), `main.py` (updated imports + router registration)
- **Sanity check result**: Import OK, 10 routes registered, server starts cleanly, GET /api/baking/recipes and /api/baking/inventory return 200
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-156 --status completed`
