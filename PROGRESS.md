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
> 113 session entries archived as of 2026-04-08.

## 2026-04-05 -- [T-P1-267] Story Map page implementation
- **What I did**: Implemented Story Map (故事脉络) page as a new tab in BehavioralQuestions. Created bq_story_arcs.json with 6 project arcs, full Chinese narratives (前因后果), principle mappings per story, improvement suggestions per arc, and cross-arc connections. Added GET /api/behavioral/story-arcs endpoint that enriches static arc data with live DB metadata (title, link_count, tags). Built StoryMapView.tsx with: timeline visualization per arc, expandable story cards with principle badges, collapsible Chinese narrative sections, improvement notes, cross-arc connections panel, and principle legend.
- **Deliverables**: docs/bq_story_arcs.json, src/backend/routers/behavioral.py (story-arcs endpoint), src/frontend/src/components/behavioral/StoryMapView.tsx, BehavioralQuestions.tsx (story-map tab)
- **Sanity check result**: TypeScript clean, 1033 tests pass, all 29 examples verified present in DB and mapped to arcs.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-267 --status completed`

## 2026-04-05 -- Story Map markdown rendering fix
- **What I did**: Fixed narrative rendering in StoryMapView -- replaced plain paragraph text with MarkdownPreview component so **bold** markers render correctly.
- **Deliverables**: StoryMapView.tsx (MarkdownPreview for narrative_zh)
- **Sanity check result**: TypeScript clean.
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc fix)

## 2026-04-07 -- Lyra mental health + Uber onsite prep events
- **What I did**: Created Lyra as a new company (id=25, mental health provider, not a job target). Added 3 events: (1) Apr 8 9:00AM Lyra follow-up with therapist Jacqueline, (2) Apr 13 1:00PM Lyra MD video session with Mary Miller for FMLA, (3) Apr 16 12:00PM Uber onsite prep meeting with recruiter. Both Lyra events include intake form reminders in description.
- **Deliverables**: mle_prep.db (1 new company + 3 new events)
- **Sanity check result**: DB verified with 5 upcoming events in correct chronological order.
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc Discord request)

## 2026-04-07 -- [T-P0-268] Uber VO prep page
- **What I did**: Created comprehensive Uber Virtual Onsite prep content. (1) Updated Uber company status to "onsite" with 4-round interview_stages JSON. (2) Created "Uber VO 完整准备指南" document (doc id=37) with 8 sections: VO概览, 通用面试技巧, Round 1-4 detailed prep, 重要链接汇总, 总体Checklist. All in Chinese with English terms preserved. Includes checklists for each round, BQ story recommendations mapped to Uber's 3 behavioral dimensions, system design framework (STEP 1-2-3-4), and resource links. (3) Appended VO Prep Checklist to main prep_notes.
- **Deliverables**: mle_prep.db (Uber status/stages update, doc 37, prep_notes update). Uber now has 10 documents total.
- **Sanity check result**: 1033 tests pass, DB verified with 10 Uber documents and onsite status.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-268 --status completed`

## 2026-04-07 -- Pinterest and Poshmark event additions
- **What I did**: Added two new companies and interview events via Discord requests. (1) Created Pinterest (id=29) with Phone Call with David on Apr 8 1:30PM (hr_call). (2) Created Poshmark (id=30) with Intro Call on Apr 9 11:00AM (hr_call). Dashboard now shows 7 upcoming events.
- **Deliverables**: mle_prep.db (2 new companies + 2 new events)
- **Sanity check result**: DB verified, both events confirmed in upcoming timeline.
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc Discord requests)

## 2026-04-07 -- Fix timeline event timezone display bug (two-pass fix)
- **What I did**: (Pass 1 - wrong) Initially added UTC Z-suffix serializer, which broke all correctly-stored Pacific Time events. (Pass 2 - correct) Identified the real bug: only the frontend form's `new Date(val).toISOString()` was converting to UTC on submit; all other events were stored as naive Pacific Time and displayed correctly. Fix: (1) Replaced UTCDatetime with `NaivePacific` Pydantic BeforeValidator that strips TZ and converts TZ-aware inputs to America/Los_Angeles before storage. (2) Frontend form now sends naive datetime-local value directly instead of `.toISOString()`. (3) Fixed 2 Lyra events in DB (id=11: 16:00->09:00, id=12: 20:00->13:00). Added lesson to LESSONS.md.
- **Deliverables**: `src/backend/schemas/timeline.py` (NaivePacific validator), `src/frontend/src/components/timeline/EventFormModal.tsx` (removed .toISOString()), `data/mle_prep.db` (2 rows fixed), `LESSONS.md` (timezone lesson)
- **Sanity check result**: 1033 tests pass, TypeScript clean, manual verification confirms: naive input preserved as-is, UTC input converted to Pacific, response has no Z suffix. DB events 11/12 now show correct Pacific times.
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc Discord request)

## 2026-04-07 -- Plan StoryMap UI improvements (T-P1-269, T-P1-270)
- **What I did**: Task planning mode. Created 2 tasks for Story Map behavioral section: (1) T-P1-269 -- fix expanded card losing background color (approved direction: always white bg + colored border for contrast). (2) T-P1-270 -- add hover link on card title to navigate to full STAR example (using existing handleExampleClick mechanism, splitting click targets). Launched autonomous_run.sh for execution.
- **Deliverables**: T-P1-269 and T-P1-270 created in task_db with detailed ACs and implementation plans
- **Sanity check result**: Tasks verified in TASKS.md, autonomous_run.sh launched (2 sessions)
- **Status**: [DONE] (planning complete, execution delegated to autonomous_run.sh)
- **Request**: No status change needed (tasks managed by autonomous executor)

## 2026-04-07 -- [T-P1-269, T-P1-270] StoryMap card UX improvements
- **What I did**: (1) T-P1-269: Changed ArcExampleCard to always use white background instead of switching to arc color on expand. Added border-2 + shadow-md on expand for visual depth. Cards now clearly contrast against the colored arc section background in both states. (2) T-P1-270: Added `onExampleClick` callback prop through StoryMapView -> ArcSection -> ArcExampleCard. Card title is now a clickable link (with hover underline + arrow icon) that navigates to the full STAR example in Examples view. Card body still expands/collapses on click. Added "View full example" link in expanded content area too. Wired up via existing `handleExampleClick` in BehavioralQuestions.tsx.
- **Deliverables**: `StoryMapView.tsx` (card styling + link navigation), `BehavioralQuestions.tsx` (pass onExampleClick prop)
- **Sanity check result**: TypeScript clean, 1033 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-269 --status completed` and `task_db.py update T-P1-270 --status completed`

## 2026-04-07 -- [T-P1-271] Plan slide-over drawer for behavioral example detail
- **What I did**: Task planning mode. Designed and planned slide-over drawer UX pattern for drill-down-and-return navigation in Behavioral page. Researched industry best practices (Material Design side sheets, Apple HIG inspector panels). Created T-P1-271 with detailed 4-step implementation plan. Incorporated user's review feedback: Portal (mandatory), stopPropagation (mandatory), scroll lock cleanup (mandatory), state=id with snapshot (compromise), pure CSS transitions (no framer-motion), skip focus trap and URL sync. Confirmed single task (no split needed).
- **Deliverables**: T-P1-271 created with full implementation spec, review-incorporated design decisions, and 15 acceptance criteria
- **Sanity check result**: Task spec reviewed and approved by user. TASKS.md regenerated.
- **Status**: [DONE] (planning complete, awaiting user approval to execute)
- **Request**: No status change (T-P1-271 remains active, pending execution approval)

## 2026-04-07 -- [T-P1-271] Slide-over drawer for behavioral example detail
- **What I did**: Implemented right-side slide-over drawer for drill-down-and-return navigation. (1) Created SlideOverPanel.tsx -- generic reusable component using createPortal, with Escape handler, scroll lock (saves/restores original overflow), stopPropagation, role="dialog" aria-modal="true". (2) Extracted BehavioralExample/LinkedQuestion types to types/behavioral.ts. (3) Created ExampleDrawerContent.tsx -- renders full STAR content with all sections (risk, analogy, tech_terms, evidence, linked_questions) without expand/collapse. (4) Rewired BehavioralQuestions.tsx -- handleExampleClick now opens drawer (setDrawerExampleId) instead of destructively switching viewMode/clearing filters. Removed old focusedExampleId state.
- **Deliverables**: SlideOverPanel.tsx (new), ExampleDrawerContent.tsx (new), types/behavioral.ts (new), BehavioralQuestions.tsx (modified)
- **Sanity check result**: TypeScript clean, 1033 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-271 --status completed`

## 2026-04-07 -- [T-P1-271] Fix TDZ runtime error in drawer wiring
- **What I did**: Fixed "Cannot access 'examples' before initialization" error. The `drawerExample` derivation (line 478) referenced the `examples` const declared later (line 514) -- a JavaScript temporal dead zone (TDZ) error. Moved `drawerExample` after the `useQuery` that declares `examples`.
- **Deliverables**: `BehavioralQuestions.tsx` (reordered variable declarations)
- **Sanity check result**: TypeScript clean, 1033 tests pass, user confirmed error resolved.
- **Status**: [DONE]
- **Request**: No task change (bugfix within T-P1-271)

## 2026-04-07 -- [T-P1-272] Plan system design Chinese translation
- **What I did**: Task planning mode. Investigated all 8 system design modules in DB: all have 8/8 sections filled, totaling ~193K characters of English technical content. Created T-P1-272 with detailed translation rules (narrative to Chinese, preserve terms/acronyms with expansion, keep code blocks/formulas). Proposed 4-batch execution strategy by content volume. Sent analysis with 3 decision questions to user for review.
- **Deliverables**: T-P1-272 created with translation rules, batch strategy, and scope analysis
- **Sanity check result**: DB content verified (8 modules, character counts confirmed), TASKS.md regenerated.
- **Status**: [DONE] (planning complete, awaiting user decisions on batch splitting and priority)
- **Request**: No status change (T-P1-272 remains active, pending user response)

## 2026-04-08 -- [T-P1-273~277] Translate all 8 system design modules to Chinese
- **What I did**: Translated all 8 system design modules (64 sections total, ~193K chars English) to Chinese via 5 batch task-executor agents. Batch 1: modules 7+8 (24K). Batch 2: modules 1+2 (36K). Batch 3: modules 3+4 (55K). Batch 4+5 in parallel: modules 5 (36K) and 6 (41K). Rules: narrative in Chinese, technical terms preserved in English bold with expansion, code blocks/formulas untouched, section headers bilingual, titles/subtitles English.
- **Deliverables**: data/mle_prep.db -- 64 section columns updated across 8 system_designs rows
- **Sanity check result**: All 64 sections verified to contain Chinese content. Titles/subtitles unchanged. ALL PASS.
- **Status**: [DONE]
- **Request**: T-P1-273~277 all marked completed via task_db.py

## 2026-04-08 -- Analyze module-arbitration content gaps for system design interview depth
- **What I did**: Read all 8 sections of module-arbitration (~11K chars). Analyzed interview-readiness across three dimensions: (1) Thompson Sampling -- formula present but missing step-by-step decision process, conjugate prior reasoning, batched TS at 50K QPS, cold start priors. (2) Kafka pipeline -- only an arrow in dataflow diagram, missing event schema, consumer group topology, attribution windows, partitioning. (3) Tuning iteration -- no monitoring/drift detection/A/B framework narrative. Identified two logic-chain breaks in interview flow: "why TS" lacks theoretical backing, "how system evolves" missing entirely. Proposed ~7.5K chars of additions across formulas, architecture, dataflow, tradeoffs, defense sections.
- **Deliverables**: Detailed expansion plan sent to user for review (3 themes, estimated sizes, placement locations)
- **Sanity check result**: N/A (planning/analysis only, no code changes)
- **Status**: [DONE] (awaiting user review before execution)
- **Request**: No task change (planning discussion)

### 2026-04-07 — [T-P1-163] Translate system design modules 7 and 8 to Chinese
- **What I did**: Translated all 8 section columns (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) for both `vibe-code-engineering-patterns` (module 7) and `ml-system-design-patterns` (module 8) from English to Chinese. Applied translation rules: bilingual section headers, technical terms kept in English with bold+Chinese explanation on first use, acronyms expanded per section, code blocks preserved as-is, table headers translated, math/formulas kept, proper nouns in English. Title and subtitle kept in English.
- **Deliverables**: 16 section columns updated in `data/mle_prep.db` table `system_designs`
- **Sanity check result**: Verified Chinese content present in all sections, title/subtitle remain English, code blocks untranslated.
- **Status**: [DONE]

### 2026-04-08 — Expand module-arbitration system design depth (Thompson Sampling, Kafka, Iteration)
- **What I did**: Expanded module-arbitration content across 5 sections to fill system design interview depth gaps. (1) **Formulas**: Added Beta-Bernoulli conjugate prior derivation, cold-start prior transfer algorithm (kNN module embedding), score fusion formula (TS + XGBoost with epsilon annealing), batched TS at scale (100ms batch period), LP solver specified as min-cost max-flow. (2) **Architecture**: Expanded HMAC acronym, added full Kafka stream pipeline (event schema with 10 fields, 3-stage processing topology, exactly-once semantics, backpressure handling). (3) **Data Flow**: Expanded feedback path with stream stages, added hourly-TS-vs-daily-model trade-off explanation. (4) **Trade-offs**: Added Iteration & Evaluation subsection (3-tier eval with IPS/DR formula, hyperparameter tuning table, 3 failure modes with fixes). (5) **Defense Q&A**: Added 2 new Q&As (position bias debiasing, feedback loop convergence prevention).
- **Deliverables**: `scripts/content_module_arbitration.py` (updated), `data/mle_prep.db` (8 sections re-seeded, ~11K -> ~32K chars total)
- **Sanity check result**: Seed script ran successfully, all 8 sections verified OK (>100 chars each). Thompson Sampling present in 6/8 sections, Kafka in 4/8, Iteration/Counterfactual in 2/8.
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc Discord request)

### 2026-04-08 -- Fix formula rendering + diagnose Chinese translation loss
- **What I did**: (1) Diagnosed and fixed formula rendering breakage in module-arbitration: root cause was bare `|` (pipe) inside `$`/`$$` math blocks conflicting with remark-gfm table parser, plus multi-line `$$` blocks and consecutive `$$` without blank lines. Fixed all `|` to `\mid`, collapsed multi-line `$$` to single lines, added blank lines between consecutive `$$` blocks, split compound `$\alpha, \beta$` into separate `$` wrappers. (2) Diagnosed Chinese translation overwrite: `content_module_arbitration.py` has hardcoded English content, running it overwrote the Chinese translations in DB. Chinese is unrecoverable (DB not in git, WAL empty). Other 7 modules confirmed safe. (3) Proposed 2 tasks (formula verification + Chinese re-translation) and 2 lessons to user for review.
- **Deliverables**: `scripts/content_module_arbitration.py` (formula fixes), `data/mle_prep.db` (re-seeded with fixed formulas)
- **Sanity check result**: Seed script ran OK, all 8 sections verified. No bare `|` in any math block (verified via script). Awaiting user page refresh to confirm rendering.
- **Status**: [PARTIAL] Formula fix done. Chinese re-translation pending user approval.
- **Request**: No task to update (awaiting user confirmation to create translation task)

### 2026-04-08 -- Module-arbitration Chinese translation + global system design audit
- **What I did**: (1) Rewrote `content_module_arbitration.py` as Chinese version (preserving English terms, formulas, code blocks) with all expanded content (TS deep dive, Kafka pipeline, Iteration & Evaluation). Seed script is now the Chinese source of truth. (2) Audited all 8 system design modules for depth: checked char counts, formula counts, Defense Q&A counts, presence of key depth dimensions (cold-start, iteration, failure modes, Kafka detail, position bias). (3) Proposed 8-task improvement plan (Tasks A-H) prioritized by interview relevance, sent to user for review. Plan includes methodology extracted from module-arbitration deep-dive process.
- **Deliverables**: `scripts/content_module_arbitration.py` (Chinese rewrite, 18.5K chars across 8 sections), `data/mle_prep.db` (re-seeded), detailed task plan sent via Discord
- **Sanity check result**: Seed script ran OK, all 8 sections verified (Chinese chars present, formulas with `\mid`, bilingual headers). Global audit covered all 8 modules with depth markers.
- **Status**: [DONE] Chinese translation complete. Task plan A-H awaiting user review before creating in task_db.
- **Request**: No task_db update yet (tasks not yet approved by user)

### 2026-04-08 -- Task planning for system design depth improvements + autonomous_run attempt
- **What I did**: (1) Created 8 tasks (T-P0-164 through T-P2-171) via task_db.py for expanding all system design modules to interview-ready depth. Each task includes CRITICAL SAFETY RULES (never overwrite Chinese, seed script = source of truth, \mid not |). (2) Launched autonomous_run.sh with 8 sessions for MLInterviewPrep. Session 1 started but did not complete any task -- likely exceeded context/turn limits for L-size translation tasks. (3) Notified user via Discord and awaiting decision on next steps (split tasks, manual execution, or retry).
- **Deliverables**: 8 tasks in tasks.db (T-P0-164 to T-P2-171), TASKS.md regenerated, autonomous_run.sh attempted
- **Sanity check result**: All 8 tasks verified in DB with safety rules. autonomous_run.sh exited after 1 session with 0 tasks completed, 0 new git commits.
- **Status**: [BLOCKED] Awaiting user decision on execution strategy for L-size tasks that exceed autonomous session limits.
- **Request**: No task status change (tasks remain active pending user direction)

### 2026-04-08 -- [T-P2-257] Remove unused check_stop_cache/write_stop_cache from hook_utils.py
- **What I did**: Removed three dead functions from hook_utils.py: _get_repo_fingerprint(), check_stop_cache(), write_stop_cache(). Also removed now-unused imports (hashlib, subprocess, contextlib, Path) and updated module docstring. These were leftovers from the deprecated stop-cache architecture (LESSONS.md [2026-03-18]).
- **Deliverables**: .claude/hooks/hook_utils.py (cleaned up)
- **Sanity check result**: All 19 hook files import successfully after changes. No remaining references to removed functions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-257 --status completed`

### 2026-04-08 -- [T-P2-278] Propagate SQLite naive-datetime timezone lesson to helixos
- **What I did**: Propagated the [2026-04-07] SQLite naive datetime lesson from MLInterviewPrep/LESSONS.md to helixos/LESSONS.md. Adapted wording to helixos context (FastAPI/Pydantic/SQLAlchemy instead of generic). Added [PROPAGATED] tag with source reference.
- **Deliverables**: helixos/LESSONS.md (appended entry)
- **Sanity check result**: Verified entry present in helixos/LESSONS.md with correct tags and helixos-specific wording.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-278 --status completed`

### 2026-04-08 -- Fix task DB location + re-create tasks in MLInterviewPrep
- **What I did**: (1) Diagnosed why autonomous_run.sh completed T-P2-278 (lesson propagation) instead of our system design tasks: tasks were in root tasks.db but autonomous_run.sh uses MLInterviewPrep's tasks.db. (2) Re-created all 8 system design depth tasks (T-P0-280 ~ T-P2-287) in MLInterviewPrep's task_db with full safety rules (never overwrite Chinese, seed script = source of truth, \mid not |). (3) Marked T-P2-279 (sync task) as completed. (4) Launched autonomous_run.sh (max_session=1) targeting T-P0-280 (llm-orchestration expansion).
- **Deliverables**: 8 tasks in MLInterviewPrep/.claude/tasks.db, TASKS.md regenerated, autonomous_run.sh running
- **Sanity check result**: All 8 tasks verified active in MLInterviewPrep task_db with safety rules in descriptions. autonomous_run.sh launched targeting correct sub-project.
- **Status**: [IN PROGRESS] autonomous_run.sh session 1 running for T-P0-280.
- **Request**: No further task_db updates needed (tasks are active, autonomous session will update on completion)

## 2026-04-08 -- [T-P0-280] Expand llm-orchestration system design to interview depth
- **What I did**: Expanded llm-orchestration from 9.8K to 18.4K chars. Added: (1) Prompt engineering details (structured template, schema-constrained decoding via Outlines, field validation gate). (2) Proxy model distillation pipeline (teacher-student, quarterly full + monthly LoRA). (3) Distillation data flow with evaluation gate and canary deployment. (4) Artifact quality monitoring table. (5) Distillation loss formula and intent drift detection (KL divergence). (6) Latency-accuracy trade-off table (3B/7B/13B/70B/100B comparison). (7) Iteration & Evaluation section (4-layer eval, hyperparameter tuning table). (8) 3 failure modes with root cause and fix. (9) 2 new Defense Q&A (distillation staleness, schema-constrained decoding limits). Updated verbal outlines.
- **Deliverables**: scripts/content_llm_orchestration.py (seed script, Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 18,407 total chars (target >=16K), 8 display math, 5 Q&A (target 4+), 3 failure modes (target 2+), iteration section present, no bare | in math, 5,182 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-280 --status completed`

### 2026-04-08 -- T-P0-280 completed + remaining 7 tasks launched
- **What I did**: (1) Verified T-P0-280 (llm-orchestration expansion) completed successfully by autonomous session: 9.8K -> 18.4K chars, 8 display math, 5 Defense Q&A, 3 failure modes, iteration section, no bare | in math. Committed as c7a1f46. (2) Launched autonomous_run.sh (max_session=7) for remaining 7 tasks (T-P0-281 through T-P2-287). Each session will pick one task, complete it, commit, and exit.
- **Deliverables**: T-P0-280 completed (scripts/content_llm_orchestration.py created, DB seeded), autonomous_run.sh running for 7 remaining tasks
- **Sanity check result**: T-P0-280 verified: 18.4K chars, Chinese content present, 5 Q&A, commit confirmed in git log. 7 tasks remain active in MLInterviewPrep task_db.
- **Status**: [IN PROGRESS] autonomous_run.sh executing remaining 7 tasks serially.
- **Request**: T-P0-280 already marked completed by autonomous session. No manual update needed.

### 2026-04-08 -- [T-P0-281] Expand ranking-allocation system design to interview depth
- **What I did**: Expanded ranking-allocation from 17.4K to 21.2K chars. Added: (1) Kafka feedback pipeline section with topic design, event schema, and end-to-end latency table. (2) Cold-start budget initialization formula with 3-phase evolution strategy (pure inheritance -> exploration -> convergence). (3) 3 failure modes with root cause and fix (budget oscillation, constraint conflict deadlock, cold-start segment drift). (4) Hyperparameter tuning table (7 params: lambda, eta, n0, beta, sigma_j, gamma, seller cap). Updated verbal outlines to reference new content. Converted seed script from English to Chinese source of truth.
- **Deliverables**: scripts/content_ranking_allocation.py (Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 21,196 total chars (target >=20K), 11 display math, 7 Q&A, 3 failure modes (target 2+), tuning table present, cold-start documented, Kafka detail added, no bare | in math, 7,428 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-281 --status completed`

### 2026-04-08 -- [T-P1-282] Add Defense Q&A to distributed-task-queue
- **What I did**: Added 3 new Defense Q&A to distributed-task-queue module: (1) Priority Inversion -- WFQ, age-based promotion, dedicated pools. (2) Worker Starvation -- autoscaling, long-task isolation, circuit breaker. (3) Distributed Lock Trade-off -- selective locking, lock extension, fencing tokens as alternative, fail-closed/fail-open degradation. Converted entire seed script from English to Chinese source of truth.
- **Deliverables**: scripts/content_distributed_task_queue.py (Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 25,269 total chars, 12 Defense Q&A (9 existing + 3 new), 9,041 Chinese characters, no bare | in math, all existing content preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-282 --status completed`

### 2026-04-08 -- [T-P1-283] Supplement database-comparison system design depth
- **What I did**: Expanded database-comparison from 21.1K to 24.5K chars. Added: (1) Migration strategy section with 3 approaches (dual-write + shadow read, CDC streaming, stop-the-world). (2) Iteration & Evaluation section with 4-level methodology (benchmark, shadow traffic, canary, A/B) and key monitoring metrics (p99 trend, write amplification, Gini coefficient, capacity, Raft election frequency). (3) 3 failure modes with root cause and fix (split brain, compaction storm write stall, hot partition cascade). (4) Capacity planning formulas (storage, node count, throughput estimation). Converted seed script from English to Chinese source of truth.
- **Deliverables**: scripts/content_database_comparison.py (Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 24,502 total chars (target >=24K), 11 display math, 6 Q&A, 3 failure modes, migration strategy present, iteration section present, no bare | in math, 7,463 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-283 --status completed`

### 2026-04-08 -- [T-P1-284] Expand pbe-pipeline system design to interview depth
- **What I did**: Expanded pbe-pipeline from 12.5K to 18.2K chars. Added: (1) Schema evolution strategy with Confluent Schema Registry and compatibility checks. (2) Data quality monitoring section with anomaly detection (rolling Z-score), schema drift detection, value range validation, freshness SLAs. (3) Iteration & Evaluation section with 4-layer methodology (offline replay, shadow evaluation, interleaving, A/B) and hyperparameter tuning table (5 params). (4) 3 failure modes with root cause and fix (viewport event storm, IPW weight explosion, feature-label temporal misalignment). (5) 2 new Defense Q&A (Z-score limitations in non-stationary e-commerce, schema evolution stress test). (6) Data anomaly Z-score formula. Converted seed script from English to Chinese source of truth.
- **Deliverables**: scripts/content_pbe_pipeline.py (Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 18,180 total chars (target >=16K), 7 display math, 6 Q&A (target 6+), 3 failure modes (target 2+), data quality monitoring present, schema evolution present, iteration section present, no bare | in math, 5,869 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-284 --status completed`

### 2026-04-08 -- [T-P2-285] Restructure vibe-code-engineering to system design depth
- **What I did**: Restructured vibe-code-engineering-patterns from 6.2K to 17.5K chars. Reframed from lesson summary into Engineering Tooling System Design covering three sub-systems: data extraction pipeline, scraping orchestration, and multi-layer secret detection. Added: (1) Architecture diagrams for all three sub-systems with cross-system pattern comparison table. (2) Detailed data flows for extraction, orchestration, and detection. (3) Formulas section with 12 display math blocks (selector coverage, precision/recall/F1, throughput/efficiency, adaptive pagination stop, confidence model, Shannon entropy, FPR/cost analysis). (4) Production constraints tables for all three sub-systems with concrete numbers. (5) 7 trade-off decisions in table + 2 detailed analyses (Fail-open vs Fail-closed, fixed vs adaptive pagination). (6) Iteration & evaluation section with methodology table and 3 failure modes. (7) 5 Defense Q&A (defense-in-depth justification, fixture sample size, AI fail-open blind spots, flock vs PID file, detection paradox value). (8) Verbal outlines 3-min and 10-min.
- **Deliverables**: scripts/content_vibe_code_engineering.py (new seed script, Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 17,459 total chars (target >=14K), 12 display math (target 3+), 5 Q&A (target 4+), 7 trade-off decisions (target 3+), 3 failure modes, no bare | in math, 5,568 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-285 --status completed`

### 2026-04-08 -- [T-P2-286] Expand ml-system-design-patterns to interview depth
- **What I did**: Expanded ml-system-design-patterns from 8.5K to 17.0K chars. Added: (1) Business impact quantification table in overview (CTR, NDCG, latency, GMV ranges). (2) Per-section expansion strategy table in architecture with time allocation and common mistakes. (3) Narrative construction pipeline in dataflow with step-by-step process and decision quick-reference table. (4) Math formulations: NDCG/DCG, MAP, CTR lift confidence interval, feature store freshness SLA, progress aggregation formula. (5) Production constraints table with typical numbers for QPS/latency/data scale/candidate set/cost/fallback. (6) Latency budget allocation pattern with example breakdown. (7) Iteration & evaluation methodology: 3-layer evaluation strategy, hyperparameter tuning patterns, 3 failure modes per section. (8) 5 Defense Q&A (NDCG label reliability, feature store freshness failure, priority-chain limitations, A/B test acceleration, latency budget parallelization). (9) Updated verbal outlines with formula summaries.
- **Deliverables**: scripts/content_ml_system_design_patterns.py (new seed script, Chinese source of truth), data/mle_prep.db updated
- **Sanity check result**: 17,017 total chars (target >=14K), 10 display math (target 5+), 8 Q&A (target 4+), failure modes in every section, no bare | in math, 5,768 Chinese characters preserved
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-286 --status completed`

### 2026-04-08 -- [T-P2-287] System design formula audit: all modules
- **What I did**: Audited all 8 system design modules for formula rendering safety. Found 3 real issues (consecutive $$ without blank lines): 1 in database-comparison/formulas, 2 in distributed-task-queue/formulas. Fixed in seed scripts and re-seeded only those 2 modules. No bare | in display math found. No multi-line $$ found. "Unbalanced $" flags were all false positives from currency symbols ($5K, $0.25) and code refs (`$lookup`). Created reusable audit script (scripts/audit_formulas.py). All 8 modules pass clean.
- **Deliverables**: scripts/content_database_comparison.py (1 blank line added), scripts/content_distributed_task_queue.py (2 blank lines added), scripts/audit_formulas.py (new audit tool), data/mle_prep.db updated
- **Sanity check result**: All 8 modules CLEAN. 0 bare | in display math, 0 multi-line $$, 0 consecutive $$ without blank lines. All Chinese preserved.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-287 --status completed`

### 2026-04-08 -- System design depth tasks all completed + 3 new UI/UX tasks planned
- **What I did**: (1) Verified all 8 system design depth tasks (T-P0-280 ~ T-P2-287) completed successfully via autonomous_run.sh (7 sessions, 7 commits). All modules now at interview-ready depth (14K-25K chars each, Chinese content, Defense Q&A, formulas audited). (2) Task planning mode: investigated 3 new issues per user request -- missing diagrams for 2 modules, poor section navigation UX, and need for System Design landing page restructure. Created 3 tasks: T-P1-288 (HTML diagrams + PNG screenshots for vibe-code-engineering and ml-system-design-patterns), T-P1-289 (replace top bookmark nav with right-side TOC sidebar referencing DynamicTocSidebar), T-P0-290 (restructure landing page with Interview Prep + eBay Projects tabs).
- **Deliverables**: 3 tasks in MLInterviewPrep tasks.db (T-P1-288, T-P1-289, T-P0-290), TASKS.md regenerated, task plan sent via Discord for review
- **Sanity check result**: All 3 tasks created with detailed self-contained descriptions and AC. Verified existing diagram/TOC patterns in codebase for reference.
- **Status**: [DONE] (task planning only -- awaiting user review before execution)
- **Request**: No task status changes needed (tasks are active, pending user approval)

### 2026-04-08 -- [T-P0-290] Restructure System Design landing page with sub-sections
- **What I did**: Restructured SystemDesignList.tsx into a tabbed layout with two sections: (1) Interview Prep (default tab) -- 8 placeholder cards for common SD interview questions (URL Shortener, Rate Limiter, News Feed, Chat System, Key-Value Store, Notification System, Web Crawler, Search Autocomplete) with difficulty badges, topic tags, descriptions, and "Coming Soon" labels. (2) eBay Projects -- existing 8 modules with narrative blockquote moved under this tab. Used useSearchParams for tab state persistence via URL (?tab=ebay), so tab is preserved on back navigation. Added useState + import for tab switching.
- **Deliverables**: src/frontend/src/pages/SystemDesignList.tsx (rewritten with tab layout)
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit). Interview Prep tab shows 8 topics. eBay Projects tab preserves existing module cards with narrative. Existing /system-design/:slug routes unchanged.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-290 --status completed`

### 2026-04-08 -- [T-P1-288] Create HTML diagrams + PNG screenshots for vibe-code-engineering and ml-system-design-patterns
- **What I did**: Created architecture diagrams for two system design modules that had diagram_filename set in DB but no actual files. (1) vibe_code_engineering.html -- three-column layout showing Data Extraction Pipeline, Scraping Orchestration System, and Secret Detection 7-Layer Defense, with shared cross-system patterns bar at bottom. (2) ml_system_design_patterns.html -- 6-section interview template with timing badges, priority-driven state machine architecture, and failure modes analysis. Updated generate_diagram_screenshots.py DIAGRAMS list. Generated PNG screenshots via Playwright.
- **Deliverables**: src/frontend/public/static/system-designs/html/vibe_code_engineering.html, src/frontend/public/static/system-designs/html/ml_system_design_patterns.html, src/frontend/public/static/system-designs/vibe_code_engineering.png (109KB), src/frontend/public/static/system-designs/ml_system_design_patterns.png (109KB), scripts/generate_diagram_screenshots.py updated
- **Sanity check result**: Both PNGs generated successfully with non-zero size. Visual verification confirms clear, well-structured diagrams matching existing style conventions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-288 --status completed`

## 2026-04-08 -- [T-P1-289] Replace top bookmark nav with persistent right-side TOC
- **What I did**: Replaced the sticky horizontal bookmark nav bar in SystemDesignDetail.tsx with a persistent right-side TOC sidebar. The TOC uses a two-column flex layout (main content left, TOC right), highlights the current section via the existing IntersectionObserver, supports click-to-scroll, and is hidden on small screens (lg: breakpoint). Reduced scroll-mt from 28 to 16 since the bookmark nav no longer occupies vertical space.
- **Deliverables**: src/frontend/src/pages/SystemDesignDetail.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-289 --status completed`

### 2026-04-08 -- Add Lyra Jacqueline session + verify 3 UI/UX tasks completed
- **What I did**: (1) Added Lyra therapist session with Jacqueline on Apr 17 10:00 AM (event id=17) to dashboard. (2) Verified all 3 UI/UX tasks (T-P0-290, T-P1-288, T-P1-289) completed by autonomous_run.sh: landing page restructured with Interview Prep + eBay Projects tabs, HTML diagrams + PNGs generated for 2 modules, right-side TOC sidebar replaced top nav.
- **Deliverables**: mle_prep.db (1 new event), 3 autonomous commits (1d95fc1, 7276ed9, + TOC commit)
- **Sanity check result**: Event verified in upcoming list (9 upcoming events total). All 3 tasks confirmed completed (0 active tasks remaining).
- **Status**: [DONE]
- **Request**: No task to update (ad-hoc Discord request)

### 2026-04-08 -- Task planning: 20 System Design Interview Prep topics in 7 tasks
- **What I did**: Task planning mode. Analyzed user's list of 20 high-frequency system design interview topics (URL Shortener, Ride-sharing/Uber, Chat System, etc.). Designed 8-section content structure adapted for interview prep (Clarification Questions, Capacity Estimation, 1h Interview Outline). Consolidated overlapping topics (Instagram+News Feed, Web Crawler+10K machines variant). Split into 6 content batch tasks (3-5 topics each) + 1 landing page update task. Created T-P0-291 through T-P1-297 in MLInterviewPrep task_db with detailed self-contained descriptions and safety rules. Also noted Discord MCP channel lost allowlist during session.
- **Deliverables**: 7 tasks in tasks.db (T-P0-291 ~ T-P1-297), TASKS.md regenerated, plan communicated to user for review
- **Sanity check result**: All 7 tasks verified active with descriptions. T-P1-297 depends on all 6 content batches.
- **Status**: [DONE] (task planning only -- awaiting user review before autonomous execution)
- **Request**: No task status changes needed (tasks active, pending user approval)

### 2026-04-08 -- [T-P0-298] SD Prep: Design a URL Shortener
- **What I did**: Created seed script `scripts/content_interview_url_shortener.py` with all 8 sections (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) in Chinese with English technical terms preserved. Created SystemDesign DB record with slug `interview-url-shortener`. Updated `SystemDesignList.tsx` to add optional `slug` field to InterviewTopic interface and make cards with slugs clickable (navigating to `/system-design/{slug}`).
- **Deliverables**: `scripts/content_interview_url_shortener.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 17,459 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-298 --status completed`

## 2026-04-08 -- [T-P0-299] SD Prep: Design a Rate Limiter
- **What I did**: Created seed script `scripts/content_interview_rate_limiter.py` with all 8 sections in Chinese with English technical terms preserved. Covers token bucket, sliding window counter, fixed window, sliding window log algorithms with code examples and comparison table. Includes Redis Lua script for atomic race-condition-free checking, multi-DC deployment strategies, and fail-open fault tolerance. Created SystemDesign DB record with slug `interview-rate-limiter`, display_order=101. Updated `SystemDesignList.tsx` to add slug link for Rate Limiter topic card.
- **Deliverables**: `scripts/content_interview_rate_limiter.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,369 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-299 --status completed`

## 2026-04-08 -- [T-P0-300] SD Prep: Design a Notification System
- **What I did**: Created seed script `scripts/content_interview_notification.py` with all 8 sections in Chinese with English technical terms preserved. Covers multi-channel delivery (Push/SMS/Email), priority queue with weighted fair queuing (P0:P1:P2 = 8:4:1), template engine, user preferences with quiet hours, exponential backoff retry with DLQ, per-user rate limiting, and notification aggregation. Includes capacity estimation (5B/day, 30K peak QPS), multi-DC active-active deployment, channel fallback (Push fail -> SMS), and three-layer deduplication (idempotency key + consumer offset + template window). Created SystemDesign DB record with slug `interview-notification-system`, display_order=102. Updated `SystemDesignList.tsx` to add slug link for Notification System topic card.
- **Deliverables**: `scripts/content_interview_notification.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 21,938 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-300 --status completed`

## 2026-04-08 -- [T-P0-301] SD Prep: Design a Ride-sharing System (Uber)
- **What I did**: Created seed script `scripts/content_interview_ride_sharing.py` with all 8 sections in Chinese with English technical terms preserved. Covers real-time driver matching (Greedy + Batch Matching with Hungarian Algorithm), Redis Geospatial for location indexing (33K QPS writes from 1M active drivers), dynamic surge pricing per Geohash cell, WebSocket-based real-time communication, trip state machine lifecycle, ETA estimation (Haversine + Routing API + ML), and GPS signal handling (Kalman Filter + Map Matching). Includes capacity estimation (15M daily trips, 333K location update QPS), multi-city sharding, and distributed lock for preventing double-matching. Created SystemDesign DB record with slug `interview-ride-sharing`, display_order=103. Added new topic card with slug in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_ride_sharing.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,246 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-301 --status completed`

## 2026-04-08 -- [T-P0-302] SD Prep: Design a Proximity Service (Yelp)
- **What I did**: Created seed script `scripts/content_interview_proximity_service.py` with all 8 sections in Chinese with English technical terms preserved. Covers Geohash spatial indexing (encode lat/lng to 1D string, B-Tree prefix queries), 9-cell neighbor search to handle boundary issues, Haversine distance for precise ranking, QuadTree vs Geohash comparison, multi-level caching (L1 Caffeine 30s + L2 Redis 5min + L3 MySQL replica) for 99:1 read-heavy workload, capacity estimation (200M businesses, 50M DAU, 5800 peak QPS), cache avalanche prevention (TTL jitter + mutex lock + warming), and density-adaptive multi-precision indexing. Created SystemDesign DB record with slug `interview-proximity-service`, display_order=104. Added new topic card with slug in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_proximity_service.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,752 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-302 --status completed`

## 2026-04-08 -- [T-P0-303] SD Prep: Design a Real-time Game Leaderboard
- **What I did**: Created seed script `scripts/content_interview_game_leaderboard.py` with all 8 sections in Chinese with English technical terms preserved. Covers Redis Sorted Set (Skip List + Hash Table internals, ZADD/ZINCRBY/ZREVRANK/ZREVRANGE O(log N) operations), Kafka-based peak shaving for 50K QPS burst during season settlement, composite score encoding for tie-breaking (timestamp in low bits), score range partitioning for 100M+ players, multi-dimension leaderboards (daily/weekly/season with TTL auto-expiry), MySQL async backup for disaster recovery (full rebuild < 15 min), Redis Pipeline batch updates, capacity estimation (50M players, 5M DAU, 4.4 GB Redis, $1600/mo total cost). Created SystemDesign DB record with slug `interview-game-leaderboard`, display_order=105. Added new topic card with slug in `SystemDesignList.tsx`. Archived PROGRESS.md (113 entries archived).
- **Deliverables**: `scripts/content_interview_game_leaderboard.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,481 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-303 --status completed`

## 2026-04-08 -- [T-P0-304] SD Prep: Design a News Feed (Instagram)
- **What I did**: Created seed script `scripts/content_interview_news_feed.py` with all 8 sections in Chinese with English technical terms preserved. Covers hybrid Fan-out strategy (Push for normal users, Pull for celebrities with 10K+ followers), ML ranking pipeline (EdgeRank + modern multi-objective DNN/GBDT), two-stage ranking (coarse 1000->200, fine 200->20), Redis Sorted Set feed cache, Kafka async fan-out, Snowflake ID generation, cursor-based pagination, celebrity optimization, multi-DC active-active with AP consistency, three-level graceful degradation (ML ranking -> chronological -> cached snapshot), capacity estimation (200M DAU, 115K QPS read, 3.6 TB Redis, 3.65 PB/yr media, ~206K USD/mo). Created SystemDesign DB record with slug `interview-news-feed`, display_order=106. Updated topic card with slug in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_news_feed.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,940 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-304 --status completed`

## 2026-04-08 -- [T-P0-305] SD Prep: Design a Chat System (Messenger/WhatsApp)
- **What I did**: Created seed script `scripts/content_interview_chat_system.py` with all 8 sections in Chinese with English technical terms preserved. Covers WebSocket connection management (50K connections/server, Redis connection registry with TTL=90s heartbeat), message routing (Chat Service -> Redis lookup -> gRPC push to target Gateway), at-least-once delivery + client dedup (4-layer guarantee: instant push -> retry with exponential backoff -> offline queue -> periodic sync), group chat write-time fan-out (up to 500 members), online presence via Redis TTL heartbeat + lazy aggregation (90%+ traffic saving), Cassandra message store (partition by conversation_id), Snowflake ID generation, multi-DC active-active with AP consistency, 4-level graceful degradation, E2E encryption discussion (Signal Protocol: X3DH + Double Ratchet), capacity estimation (500M DAU, 100B messages/day, 100M concurrent WebSocket connections, 2000 Gateway servers, 11.5 TB/day Cassandra, ~3M USD/mo). Created SystemDesign DB record with slug `interview-chat-system`, display_order=107. Updated topic card with slug in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_chat_system.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 24,586 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-305 --status completed`

## 2026-04-08 -- [T-P0-306] SD Prep: Design Facebook Live Comments
- **What I did**: Created seed script `scripts/content_interview_live_comments.py` with all 8 sections in Chinese with English technical terms preserved. Covers Fan-out Tree architecture (3-level: Root -> Regional Relays -> Edge Nodes -> Clients) for distributing comments to 10M concurrent viewers, SSE over WebSocket for lightweight single-direction push, comment sampling (Reservoir Sampling variant, ~30 comments/s per viewer from 100K/s input), two-level pre-moderation (keyword Bloom Filter <1ms + ML batch GPU inference ~10ms), reaction aggregation (Redis INCRBY + 500ms window push), 500ms comment batching (reduces network from 100K/s to 2 pushes/s per client), at-most-once delivery (unlike Chat System), Cassandra async persistence (stream_id + time_bucket partitioning), capacity estimation (100M concurrent, 500K comments/s, 5000 Edge Nodes, 200 GB/s outbound, ~470K USD/mo -- 85% cheaper than Chat System). Created SystemDesign DB record with slug `interview-live-comments`, display_order=108. Added topic card with slug in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_live_comments.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 23,909 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-306 --status completed`

## 2026-04-08 -- [T-P1-307] SD Prep: Design Search Autocomplete
- **What I did**: Created seed script `scripts/content_interview_search_autocomplete.py` with all 8 sections in Chinese with English technical terms preserved. Covers Compressed Trie (Radix Tree) with pre-computed top-K per node for O(p) prefix lookup in <1ms, multi-level caching (Browser 60s -> CDN 5min 40% hit -> App Cache 15min 30% hit -> Trie Node), data collection pipeline (Kafka -> 5min aggregation -> Frequency Store -> 15min Trie rebuild via S3 snapshots), trending detection (10s Z-Score window, fast injection 30-60s), ranking formula (frequency 0.5 + freshness decay 0.2 + trend 0.2 + personalization 0.1), Trie sharding (4 shards x 3 replicas = 84GB total for 50M queries), client-side personalization blending (preserves CDN cacheability), capacity estimation (1B DAU, ~800K peak QPS, 84GB Trie, 1.2TB/day logs, ~$32K/month). Created SystemDesign DB record with slug `interview-search-autocomplete`, display_order=109. Added slug to topic card in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_search_autocomplete.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,412 total chars. Chinese chars present in all sections. No bare `|` in math formulas (warnings are false positives from `$` in cost figures).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-307 --status completed`

## 2026-04-08 -- [T-P1-308] SD Prep: Design Top-K Heavy Hitters
- **What I did**: Created seed script `scripts/content_interview_top_k.py` with all 8 sections in Chinese with English technical terms preserved. Covers three-layer aggregation architecture (Local Counter 5s flush -> Kafka -> Flink partition by key -> Global Merger), Count-Min Sketch + Min-Heap combination (CMS 54KB for approximate counting, Min-Heap K=1000 for top-K tracking), Lambda Architecture (streaming 5s latency + hourly batch calibration via Kendall's tau), multi-time-window via CMS additivity (hierarchical time wheel 5s->1m->5m->1h->1d), Space-Saving algorithm comparison, Conservative Update optimization, multi-datacenter deployment with idempotent merge, graceful degradation (4 levels), capacity estimation (100M DAU, 5B daily events, 170K peak QPS, 25MB streaming memory, ~$5K/month). Created SystemDesign DB record with slug `interview-top-k-heavy-hitters`, display_order=110. Added slug to topic card in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_top_k.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,499 total chars. Chinese chars present in all sections. No bare `|` in math formulas (warnings are false positives from `$` in cost figures).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-308 --status completed`

## 2026-04-08 -- [T-P1-309] SD Prep: Design an Ad Click Aggregator
- **What I did**: Created seed script `scripts/content_interview_ad_click.py` with all 8 sections in Chinese with English technical terms preserved. Covers Lambda Architecture (real-time Flink path for analytics + batch Spark path for billing), exactly-once semantics (Kafka idempotent + Flink checkpoint + two-phase commit), two-level dedup (Bloom Filter 0.01% FPR + RocksDB exact Set), hybrid fraud detection (real-time rule engine + offline ML), watermark-based late event handling, ClickHouse OLAP for multi-dimensional queries, centralized aggregation with edge ingestion for multi-DC, graceful degradation (4 levels), capacity estimation (500M DAU, 10B daily impressions, 150M daily clicks, 350K peak QPS, 7GB Flink state, ~$50K/month). Created SystemDesign DB record with slug `interview-ad-click-aggregator`, display_order=111. Added slug to topic card in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_ad_click.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,177 total chars. Chinese chars present in all sections. No bare `|` in math formulas (warnings are false positives from `$` in cost figures).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-309 --status completed`

## 2026-04-08 -- [T-P1-310] SD Prep: Design YouTube/Netflix Video Streaming
- **What I did**: Created seed script `scripts/content_interview_video_streaming.py` with all 8 sections in Chinese with English technical terms preserved. Covers upload + transcoding pipeline (DAG parallel GPU transcode via Temporal, video segmentation by GOP boundary, FFmpeg + NVENC), ABR adaptive bitrate streaming (HLS/DASH, BBA and MPC algorithms), three-layer CDN caching (L1 Edge 200+ POP -> L2 Shield with Request Coalescing -> L3 Origin S3), multi-CDN failover (CloudFront primary + Akamai fallback, DNS 30s switch), viral video handling (proactive CDN warm-up, JIT transcoding), mixed transcoding strategy (eager for popular creators, JIT for long-tail, saves 60% storage), view count service (Redis real-time + Cassandra persistent + T+1 batch calibration), content deduplication (Chromaprint audio + pHash video fingerprinting). Capacity estimation: 1B DAU, 5B daily views, 174K peak playback QPS, 10M CDN segment QPS, 700 Gbps CDN outbound, 3000 GPU workers, ~$80M/month. Created SystemDesign DB record with slug `interview-video-streaming`, display_order=112. Added slug to topic card in `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_video_streaming.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 25,264 total chars. Chinese chars present in all sections. No bare `|` in math formulas (warnings are false positives from `$` in cost figures).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-310 --status completed`

## 2026-04-08 -- [T-P1-311] SD Prep: Design Dropbox/Google Drive
- **What I did**: Created seed script `scripts/content_interview_cloud_storage.py` with all 8 sections in Chinese with English technical terms preserved. Covers block-level chunking with CDC (Rabin Fingerprint, avg 4 MB chunks), delta sync (only upload changed chunks, 90%+ bandwidth savings), three-level dedup index (Bloom Filter 75 GB + Redis 200 GB + Cassandra), conflict detection via version number optimistic locking + conflict copy strategy (Dropbox model), WebSocket real-time sync notification with Long Polling fallback, tiered storage optimization (S3 Standard/IA/Glacier, 60% cost savings), version history with compaction (Time Machine-style gradual reduction, 87% storage savings), offline editing with local change queue + cursor-based reconciliation. Capacity estimation: 100M DAU, 500M users, 100B files, 35 PB storage (after dedup), 17K peak sync QPS, 52K chunk QPS, 856K metadata QPS, ~$1.5M/month. Created SystemDesign DB record with slug `interview-cloud-storage`, display_order=113. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_cloud_storage.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 26,794 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-311 --status completed`

## 2026-04-08 -- [T-P1-312] SD Prep: Design a Price Drop Tracker (CamelCamelCamel)
- **What I did**: Created seed script `scripts/content_interview_price_tracker.py` with all 8 sections in Chinese with English technical terms preserved. Covers scraping pipeline (proxy rotation with 10K+ IPs, anti-scraping countermeasures, golden tests for parser validation), TimescaleDB price history (hypertable with 7-day chunks, downsampling 90d raw + daily aggregates, continuous aggregates for OHLC), event-driven alert evaluation (Kafka price-update topic, rule engine with multiple conditions, 24h notification cooldown with breakthrough), Z-Score anomaly detection for suspicious price changes, dynamic scrape priority (weighted: watcher count x 0.5 + volatility x 0.3 + recency x 0.2). Capacity estimation: 10M users, 50M products, 300M scrapes/day, 10.4K peak QPS, 2 TB active storage, 200M active alerts, 5M notifications/day, ~2K USD/month proxy cost. Created SystemDesign DB record with slug `interview-price-drop-tracker`, display_order=114. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_price_tracker.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 25,122 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-312 --status completed`

## 2026-04-08 -- [T-P1-313] SD Prep: Design an Online Judge (LeetCode)
- **What I did**: Created seed script `scripts/content_interview_online_judge.py` with all 8 sections in Chinese with English technical terms preserved. Covers code sandbox execution (gVisor + cgroups v2 + seccomp multi-layer defense), queue-based submission pipeline (RabbitMQ with priority queues), test case runner with early termination, judge verdict state machine (Pending->Compiling->Running->AC/WA/TLE/MLE/RE/CE), MOSS plagiarism detection (Winnowing fingerprint algorithm), multi-language runtime with per-language time/memory multipliers, contest leaderboard (Redis Sorted Set with ACM-ICPC penalty calculation). Capacity estimation: 5M users, 500K DAU, 1M submissions/day, 120 peak QPS, 1TB/year submission storage, 1200 peak concurrent Judge Workers (elastic 30-300 machines). Created SystemDesign DB record with slug `interview-online-judge`, display_order=115. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_online_judge.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 23,717 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-313 --status completed`

## 2026-04-08 -- [T-P1-314] SD Prep: Design Ticketmaster / Hotel Reservation
- **What I did**: Created seed script `scripts/content_interview_ticket_reservation.py` with all 8 sections in Chinese with English technical terms preserved. Covers seat inventory with distributed locking (PostgreSQL `SELECT FOR UPDATE SKIP LOCKED`), payment hold TTL (Redis TTL + DB fallback scanner), virtual queue for flash sales (Redis Sorted Set, 5000 users/batch), overbooking probability model (hotel scenario with no-show rate), idempotent payment processing (triple-layer: client key + DB UNIQUE + gateway Idempotency-Key), waitlist notification, anti-scalper measures (Verified Fan + device fingerprint + purchase limits). Capacity estimation: 50M users, 2M DAU, 500K daily orders, 1M+ concurrent users during flash sale, 15K peak seat-selection QPS (after virtual queue), 511 GB/year storage. Created SystemDesign DB record with slug `interview-ticket-reservation`, display_order=116. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_ticket_reservation.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 20,374 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-314 --status completed`

## 2026-04-08 -- [T-P1-315] SD Prep: Design a Web Crawler
- **What I did**: Created seed script `scripts/content_interview_web_crawler.py` with all 8 sections in Chinese with English technical terms preserved. Covers URL Frontier dual-layer design (priority queue + per-host queue), distributed crawling with consistent hashing and virtual nodes, Bloom Filter deduplication (10B URLs in 11.2 GB memory at 1% FPR), SimHash content dedup (Hamming distance <= 3), robots.txt politeness enforcement with per-domain token bucket rate limiting, multi-datacenter geographic crawling strategy, spider trap detection, and fault tolerance (RocksDB persistent Frontier + Kafka replay). Capacity estimation: 15B pages/month, ~5,800 avg QPS (17,400 peak), 4.6 Gbps bandwidth (13.8 peak), 300 TB/month storage, 35-63 crawler nodes. Created SystemDesign DB record with slug `interview-web-crawler`, display_order=117. Added topic card slug to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_web_crawler.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 22,744 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-315 --status completed`

## 2026-04-08 -- [T-P1-316] SD Prep: Design an Auction System (eBay)
- **What I did**: Created seed script `scripts/content_interview_auction_system.py` with all 8 sections in Chinese with English technical terms preserved. Covers real-time bidding via WebSocket + Redis Pub/Sub, bid ordering with Snowflake monotonic timestamps, auction state machine (SCHEDULED->ACTIVE->ENDING->CLOSED->SETTLING->COMPLETED), proxy bidding engine, anti-sniping soft close mechanism (5-min window with max extension cap), hot auction isolation via Kafka serialization pipeline, payment escrow flow, Shill Bidding detection (rule engine + ML anomaly detection). Capacity estimation: 1.65K avg bid QPS (8.3K peak), 248K peak read QPS, 10.4 TB/year bid storage, 30 GB Redis, 20 WebSocket servers for 1M concurrent connections. Created SystemDesign DB record with slug `interview-auction-system`, display_order=118. Added topic card to `SystemDesignList.tsx`.
- **Deliverables**: `scripts/content_interview_auction_system.py` (new), `src/frontend/src/pages/SystemDesignList.tsx` (modified), DB record populated
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit, zero errors). All 8 sections in DB with 24,271 total chars. Chinese chars present in all sections. No bare `|` in math formulas.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-316 --status completed`
