# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-531: T-GOOG-CN-52: Rewrite company_documents id=52 'Google DNN / Key Papers Gist' to Chinese-prose narration (9.5K chars, 0%→≥60% CN)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Context
Google R1 ML Basics interview 2026-04-21 11:15 AM PT. id=52 is a 9509-char one-page gist covering Google-family DNN recommender/search papers (YouTube DNN, Wide&Deep, DLRM, Two-Tower, etc). **0% Chinese prose** — pure English, violates content_style memory requiring CN narration + EN terms.

## Writing discipline
Follow `feedback_content_style_cn_en` memory:
- Prose narration in Chinese by default
- English technical terms preserved, first occurrence per section uses `**English** (acronym, 中文)` format, e.g. `**Wide & Deep** (W&D, 宽深模型)`
- Code / math / metric notation stay English
- Target ≥60% CJK/(CJK+EN-alpha) on prose lines (stripping code fences)

## Scope
Keep structure (Papers enumerated with What / Why-mattered / Architecture / Gotcha). Rewrite only the prose sentences. Do NOT change paper list, do NOT introduce new papers.

## Deliverables
- `scripts/seed_node_doc52_cn_20260419.py` idempotent UPSERT
- Length target: ~9500 chars → 10000-13000 chars (CN expansion acceptable)
- Title stays English (no title rewrite)

## Acceptance Criteria
- [ ] CN-prose ratio ≥60% via `scripts/_verify_cn_prose_ratio.py`
- [ ] All original papers present (YouTube DNN, Wide&Deep, DLRM, Two-Tower, YouTube retrieval v2, PinnerSage, etc — diff against V1)
- [ ] First-occurrence English-acronym-Chinese triplet format applied per section
- [ ] Frontend /companies/3/prep renders doc 52 without escape issues

#### T-P1-532: T-GOOG-CN-57: Rewrite company_documents id=57 'Staging 13 Flashcards' to Chinese-prose narration (12K chars, 0%→≥60% CN)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Context
Google R1 ML Basics 2026-04-21 11:15 AM PT. id=57 is a 12123-char StudyNoteBuilder-generated doc with 13 flashcards (2-min oral answers) covering ML staging fundamentals: loss/regularization/BN/LN/SGNS/GBDT/etc. **0% Chinese prose**.

## Writing discipline
Same as T-GOOG-CN-52 (see `feedback_content_style_cn_en` memory). Use StudyNoteBuilder with Chinese mode if available (see `feedback_math_formatting` memory — math `$$`/$ works).

## Scope
- Keep all 13 flashcard topics intact (GBDT, BN, LN, SGNS, Contrastive Loss, Skip-gram, etc)
- Each card: 2-min oral answer in Chinese prose, English terms preserved, math English
- Preserve Prerequisites + Key Terms sections but rewrite explanations in Chinese

## Deliverables
- `scripts/seed_node_doc57_cn_20260419.py` idempotent UPSERT (or regen via StudyNoteBuilder CN-mode if supported — check builder code first)
- Length target: 12K → 13000-16000 chars

## Acceptance Criteria
- [ ] CN-prose ratio ≥60%
- [ ] All 13 flashcards present (diff title list against V1)
- [ ] Key Terms section intact (English term + Chinese gloss)
- [ ] Frontend renders without math $ escape corruption

### P2 -- Nice to Have

#### T-P2-521: [DEBT] MLInterviewPrep: Customize CLAUDE.md.local with project overview and tech stack
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: CLAUDE.md.local still has template placeholder text (generated from claude-code-project-template). Specific gaps:

1. Project Overview section is empty (placeholder: Describe what your project does in 2-3 sentences)
2. Tech Stack lists only Python/pytest/ruff but project actually uses: FastAPI, SQLAlchemy, Uvicorn, Anthropic SDK, React+TypeScript (frontend), react-flow (KG viz), react-markdown+KaTeX (note rendering), Pydantic, edge-tts, python-docx
3. Third invariant has placeholder: Add your domain-specific invariants here

AC: CLAUDE.md.local Project Overview describes the ML interview prep platform in 2-3 sentences. Tech Stack lists all major dependencies. Third invariant is filled with a real domain rule (e.g., DB content must have a git-tracked seed source of truth). CLAUDE.md regenerated from .local after edits.

#### T-P2-533: T-GOOG-CN-DRILL-BATCH: Batch-upgrade 11 Google drill docs + id=72 Bridge to ≥50% CN prose (from 30-47%)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Context
Google R1 ML Basics 2026-04-21. 11 drill docs (id=55, 56, 60-69) + 1 bridge doc (id=72) currently 30-47% CN prose (mid-range violation). User asked whether to include id=72 — including.

Per-doc char counts: id=55 3206, id=56 3076, id=60 6161, id=61 7851, id=62 6875, id=63 8776, id=64 9740, id=65 12160, id=67 9124, id=68 9286, id=69 11098, id=72 7387. Total ~95K chars. id=69 already 55.6% (no rewrite needed), drop from batch → 11 docs, ~84K chars.

## Writing discipline
Same `feedback_content_style_cn_en`. Target ≥50% CN prose (lower than 531/532 because drills have heavier formula/code content).

## Scope
Light rewrite pass, not V2 rebuild:
- Prose paragraphs: CN-ify
- Formulas / code / pseudocode: English untouched
- Tables: header EN, cell prose CN
- Preserve all existing structure (headings, examples, talking points)

## Deliverables
- ONE seed script `scripts/seed_google_drills_cn_batch_20260419.py` handling all 12 docs (idempotent, per-doc hash-check skip)
- Run `scripts/_verify_cn_prose_ratio.py` on all 12 after seed; all must report ≥50%

## Acceptance Criteria
- [ ] All 12 drill docs pass ≥50% CN
- [ ] No drill-topic content lost (checklist: doc-by-doc heading diff pre/post)
- [ ] Seed script idempotent (second run → 0 updates)
- [ ] Frontend /companies/3/prep doc list still shows all 12 with same titles

#### T-P1-529: T-MLSD-WORKED-95-V2: Rewrite id=95 Fraud & Trust Safety under A.1.v2
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P0-519
- **Description**: ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=95 Fraud & Trust Safety. V1 ~5040 chars, standard 8-heading skeleton.

## Execution mode
SECTION-BY-SECTION per A.1.v2. Abort on failure.

## Domain-specific focus for id=95 (Fraud & Trust Safety)
- Capacity: transaction-heavy products (Stripe/Square/banking), 10-100K TPS transaction classification, p99 <50ms, extreme class imbalance (<0.1% positive)
- Service split: Feature Extraction / Rule Engine (deterministic) / ML Classifier (learned) / Decision Aggregator / Human Review Queue / Feedback Loop
- Tech choices (Rule 3 ≥3 alt + Rule 7): supervised (GBDT/XGBoost vs DNN vs graph-based like GraphSAGE); unsupervised (Isolation Forest vs autoencoder vs clustering); graph features (GNN vs hand-crafted vs subgraph matching); calibration under extreme imbalance; rule engine (Drools vs home-grown DSL vs learned rules); feedback loop (active learning vs auto-labeling vs human-in-loop)
- Key follow-ups: label delay (fraud ground truth takes days-weeks), concept drift (fraudsters adapt), explanability for human reviewers + regulators (SHAP/LIME/counterfactual), adversarial robustness, data sparsity for new user segments, privacy (GDPR) + fairness constraints

## Deliverables
`scripts/seed_node_95_fraud_v2_20260419.py` idempotent.

## Length target V1 ~5040 → V2 12000-17000 chars.

## Acceptance Criteria
Standard A.1.v2 gates.

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

> 478 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-19** -- T-P2-517: KG-UX-18: Drawer rendering polish (GFM, rehype-raw, blockquote + callout styling). ## Context
- [x] **2026-04-19** -- T-P1-530: T-GOOG-DEDUPE: Dedupe Google prep docs id=38/51/53 schedule overlap + refresh dates to 4/20 mock + 4/21 R1 (NO archive, NO delete). ## Context
- [x] **2026-04-19** -- T-P1-528: T-MLSD-WORKED-94-V2: Rewrite id=94 Computer Vision Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-527: T-MLSD-WORKED-93-V2: Rewrite id=93 NLP & LLM Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-526: T-MLSD-WORKED-96-V2: Rewrite id=96 ML Infrastructure Design under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-525: T-MLSD-WORKED-97-V2: Rewrite id=97 Generative AI Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-524: T-MLSD-WORKED-91-V2: Rewrite id=91 Ads & Click Prediction under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-523: T-MLSD-WORKED-89-V2: Rewrite id=89 Search & Retrieval Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-522: T-MLSD-WORKED-90-V2: Rewrite id=90 Recommendation Systems under A.1.v2. ## Context
- [x] **2026-04-19** -- T-P1-520: T-LC-399-NOTES: Add LC 399 Evaluate Division double-solution notes + mark completed + link framework. ## Context
- [x] **2026-04-19** -- T-P0-516: T-MLSD-WORKED-198-V2: Rewrite id=198 Rec System under Writing Discipline rules. ## Context
- [x] **2026-04-19** -- T-P0-515: T-MLSD-WORKED-92-V2: Rewrite id=92 Marketplace under Writing Discipline rules (prose-first, triage-complete). ## Context
- [x] **2026-04-18** -- T-P2-503: KG-UX-12: Audit/migrate scattered content_length checks + LESSONS entry. ## Problem
- [x] **2026-04-18** -- T-P2-500: [DEBT] CLAUDE.md: Remove duplicate Key Constraints section. CLAUDE.md has two ## Key Constraints sections (lines 15 and 34) with nearly identical content. The first is a template p
- [x] **2026-04-18** -- T-P1-513: T-MLSD-WORKED-198: Upgrade Real-Time Rec System (id=198) with L5 skeleton. ## Context
- [x] **2026-04-18** -- T-P1-512: T-MLSD-WORKED-92: Upgrade Marketplace & Logistics (id=92) to L5-bar gold standard. ## Context
- [x] **2026-04-18** -- T-P1-511: T-MLSD-AUDIT-01: Score 10 design problems against L5 framework, produce gap report. ## Context
- [x] **2026-04-18** -- T-P0-519: T-MLSD-FRAMEWORK-03: Tighten Appendix A.1 — Rule 3 ≥3 alternatives + expanded Gate 9 regex + Rule 6 follow-up preemption + raised length targets. ## Context
- [x] **2026-04-18** -- T-P0-518: T-MLSD-PILOT-92-S2: Pilot rewrite §2 of id=92 under new rules + human-review gate. ## Context — ITERATION 2
- [x] **2026-04-18** -- T-P0-514: T-MLSD-FRAMEWORK-02: Append Writing Discipline rules to id=18 Appendix A (5 rules + examples + heuristic gates). ## Context
