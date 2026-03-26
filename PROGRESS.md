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


## 2026-03-23 05:00 -- Backlog cleanup: clear remaining P2 tasks
- **What I did**: Verified LC 339 (730 chars notes) and LC 364 (1367 chars notes) both in DB with is_completed=True. Closed 4 remaining P2 backlog tasks (T-P2-112, T-P2-155, T-P2-156, T-P2-157) per user request. TASKS.md regenerated. Task queue now empty.
- **Deliverables**: TASKS.md (regenerated, all tasks completed)
- **Sanity check result**: 0 active tasks remaining. All 19 tasks in completed status.
- **Status**: [DONE]

## 2026-03-23 05:30 -- Fix /api/problems 500 error (NULL priority)
- **What I did**: Investigated backend crash when frontend loads /problems page. Root cause: 2 problem records (id=152, id=153) had NULL priority field, but ProblemResponse Pydantic schema required non-optional int. FastAPI response_model validation failed with 500. Fixed schema to accept None, added fallback default in _problem_to_response, added migration 12 to fix existing NULL data, and patched DB directly.
- **Deliverables**: `src/backend/schemas/problem.py` (priority now int|None), `src/backend/routers/problems.py` (None->2 fallback), `src/backend/database.py` (migration 12)
- **Sanity check result**: All /api/problems endpoints return 200 with limit=20,50,200. Previously failed at limit>=3 due to bad record at sort position 3.
- **Status**: [DONE]

## 2026-03-23 06:15 -- [T-P0-180] Fix ruff lint errors (UP017 datetime.UTC)
- **What I did**: Ran `ruff check --fix` on `src/backend/models/system_design.py` and `src/backend/routers/system_design.py` to replace `timezone.utc` with `datetime.UTC` (UP017 rule). Total 8 auto-fixed errors across both files.
- **Deliverables**: `src/backend/models/system_design.py`, `src/backend/routers/system_design.py`
- **Sanity check result**: `ruff check src/backend/` passes clean. 923/924 tests pass (1 pre-existing failure in test_timeline unrelated to this change).
- **Status**: [DONE]

## 2026-03-22 -- [T-P1-182] Remove Review column from Problems table
- **What I did**: Removed the broken "Due Reviews" dashboard card (linked to non-existent `/problems?review=due` filter). Removed `due_reviews` from `DashboardToday` type. Adjusted dashboard grid from 3 to 2 columns. The ReviewBadge component and Review table column were already absent from the codebase. Backend spaced_repetition logic preserved.
- **Deliverables**: `src/frontend/src/pages/Dashboard.tsx`, `src/frontend/src/types/dashboard.ts`, `src/frontend/src/pages/Problems.tsx`
- **Sanity check result**: TypeScript compiles clean (`tsc --noEmit`). 288/289 tests pass (1 pre-existing failure). Ruff: 1 pre-existing error (unrelated).
- **Status**: [DONE]

## 2026-03-23 06:20 -- [T-P1-181] Fetch missing problem descriptions
- **What I did**: Fetched descriptions for 5 problems missing them (id=151-155). 3 fetched from LeetCode GraphQL (151-153), 2 premium problems (LC 339, 364) fetched from user-provided URLs (algo.monster, hellointerview). Added idempotency protection (force param) to single-problem fetch-description endpoint. All 155/155 problems now have descriptions.
- **Deliverables**: `src/backend/routers/problems.py` (force param), DB updated
- **Sanity check result**: 0 problems with NULL/empty description.
- **Status**: [DONE]

## 2026-03-23 06:45 -- [T-P1-183] Framework progress sync: auto-propagate status and progress upward
- **What I did**: Implemented auto status+progress propagation from child to parent nodes. (1) Backend: new `_derive_status()` with priority model (mastered > review > in_progress > not_started). Refactored `_propagate_progress` to `_propagate_upward` with status derivation, cycle detection (log critical, no raise), and only-set-never-clear timestamps. Study log auto-starts leaf nodes and only auto-progresses leaves. (2) Frontend: disabled status dropdown for parent nodes, shows "auto from children" + mastered/total count. (3) Tests: 25 new tests in `test_propagation.py` covering `_derive_status` unit tests, progress propagation (weighted, multi-level), status rollback scenarios, timestamp immutability, child deletion, and study log auto-start + propagation. (4) Migration script for recalculating stale parent progress/status bottom-up.
- **Deliverables**: `src/backend/routers/framework.py`, `src/frontend/src/components/NodeDetailPanel.tsx`, `tests/test_propagation.py` (new, 25 tests), `scripts/migrate_recalculate_parent_progress.py` (new)
- **Sanity check result**: 1017/1021 tests pass (4 pre-existing test_timeline failures). All 25 propagation tests pass. TypeScript clean. Ruff clean.
- **Status**: [DONE]

## 2026-03-23 10:30 -- Fix CI test warnings and deprecation issues
- **What I did**: Fixed 3 categories of pytest warnings flagged in CI: (1) Replaced deprecated `Query.get()` with `Session.get()` in test_import.py, (2) Fixed SAWarning in test_models_framework.py by expunging first instance before adding conflicting PK, (3) Added filterwarnings in pyproject.toml for starlette/httpx dependency deprecation warnings. Note: the 4 test_timeline failures and 4 ruff UP017 errors were already fixed in commit 1a3b648.
- **Deliverables**: `tests/test_import.py`, `tests/test_models_framework.py`, `pyproject.toml`
- **Sanity check result**: 996 passed, 0 failed, 0 warnings. Ruff: all checks passed.
- **Status**: [DONE]

## 2026-03-23 11:40 -- Update Uber prep notes with Phone Screen section
- **What I did**: Added Part 8 (Phone Screen Prep) to uber_hr_call_prep.md based on recruiter call notes. Covers: process structure (2 phone screens + 4 virtual onsites, 4-5 week timeline), problem-solving approach (clarify -> explore -> tradeoff -> code), content areas (DSA, DP, ML algo coding KNN/ANN, edge cases, test generation), communication/pacing strategy (reserve 10+ min for experience, 5 min for questions). Also updated Part 5 with actual recruiter call notes. Re-imported to DB (27,509 chars).
- **Deliverables**: `docs/uber_hr_call_prep.md` (updated)
- **Sanity check result**: DB verified -- Uber prep_notes contains Phone Screen Prep section.
- **Status**: [DONE]

## 2026-03-24 06:50 -- Split Uber prep into HR Call + Phone Screen documents
- **What I did**: Moved section 7.6 (MLE Interview Process Overview) and Part 8 (Phone Screen Prep) from `uber_hr_call_prep.md` into a new `uber_phone_screen_prep.md`. Updated backfill script to create a CompanyDocument record for the phone screen file, so Uber now shows two tabs in the app: "Notes" (HR Call, 22,799 chars) and "Phone Screen Prep" (4,906 chars). Added `COMPANY_DOCUMENTS` dict to backfill for extensibility.
- **Deliverables**: `docs/uber_phone_screen_prep.md` (new), `docs/uber_hr_call_prep.md` (trimmed), `scripts/backfill_interviews.py` (extended)
- **Sanity check result**: DB verified -- Uber has prep_notes + 1 CompanyDocument. Frontend tabs render via existing `useCompanyDocuments` hook.
- **Status**: [DONE]

## 2026-03-24 21:30 -- [T-P0-36] Fix BehavioralQuestions page styling to match light theme
- **What I did**: Rewrote BehavioralQuestions.tsx to fix 4 issues: (1) Converted entire page from dark theme (bg-gray-800, text-white) to light theme (bg-white cards, text-gray-800, border-gray-200) matching Layout.tsx and Dashboard.tsx conventions. (2) Replaced cryptic category abbreviations (ADP, OWN, etc) with full names via CATEGORY_LABELS lookup + tooltips on filter buttons. (3) Overhauled heatmap: larger cells (min-w-[90px]), full category names in headers, proper text contrast (green-800/900/white on green backgrounds), wrapped in white card with border. (4) Fixed expand/collapse bug by lifting question expansion state to parent via Set<number> (expandedQuestions) instead of per-row useState, preventing state loss on re-render.
- **Deliverables**: `src/frontend/src/pages/BehavioralQuestions.tsx` (rewritten)
- **Sanity check result**: TypeScript clean (tsc --noEmit), Vite build clean, 996 backend tests pass
- **Status**: [DONE]

## 2026-03-24 23:59 -- [T-P1-43] Extract ML system design interview patterns into system design module
- **What I did**: Verified that seed_system_designs.py module 8 ('ml-system-design-patterns') comprehensively covers the 10.5KB source file (system Design经验总结归纳.txt). Content maps: state machine design (sections 一-三) -> architecture/formulas, L1-L2-L3 defense framework + technical decision table (sections 3/5) -> defense/dataflow, production constraints (section 4) -> production_constraints, engineering lessons (section 6) -> tradeoffs. Frontend patterns (section 2: auto-save hook, tab layout) correctly excluded as implementation details, not interview patterns. Ran seed (0 inserted, 8 updated). Deleted source file and now-empty parent directory.
- **Deliverables**: DB record with 8 populated sections (13,558 chars total: overview 935c, architecture 1704c, dataflow 1845c, formulas 1009c, production_constraints 1283c, tradeoffs 2007c, defense 2549c, verbal_outline 2226c)
- **Sanity check result**: Seed script ran successfully, DB query confirmed all 8 sections populated, source file and directory deleted
- **Status**: [DONE]

## 2026-03-24 -- [T-P0-48] Import delegation decision BQ story: hashing experiment platform
- **What I did**: Created EX-22 (delegation decision -- hashing algorithm for experiment platform) with full STAR content, 3 defense Q&As, and 5 cross-references (LDR-6, LDR-7, LDR-8, LDR-9, PS-5). Added to bq_behavioral_examples.json, saved raw story to docs/bq_story_L_delegation_hashing.md, ran seed script to import into database.
- **Deliverables**: `docs/bq_behavioral_examples.json` (EX-22 added, total 22 examples), `docs/bq_story_L_delegation_hashing.md` (raw story), DB updated (26 examples, 118 links)
- **Sanity check result**: Seed script confirmed: 1 example inserted, 5 links created. DB state: 115 questions, 26 examples, 118 links.
- **Status**: [DONE]

## 2026-03-25 16:20 -- [PLAN] LinkedIn Phone Screen Interview Questions Import
- **What I did**: Read 7 screenshots + text file from LinkedIn interview experiences (C:/Users/Shenghui Xu/Desktop/2026 跳槽准备/tmp_LinkedIn_面经/). Extracted ~50 questions across 5 categories (Coding ~15, ML System Design/Product ~25, ML Theory/Stats ~5, ML Coding ~3, Behavioral ~2). Created 4 tasks (T-P1-59 through T-P1-62) with full extracted question lists embedded in descriptions for autonomous execution context. Plan approved by user.
- **Deliverables**: Tasks T-P1-59 (coding), T-P1-60 (ml_system_design), T-P1-61 (ml_theory+coding+behavioral), T-P1-62 (bulk import) added to task_db
- **Sanity check result**: All 4 tasks created with dependencies (T-P1-62 depends on 59/60/61). TASKS.md regenerated.
- **Status**: [DONE] Planning complete, awaiting autonomous execution

## 2026-03-25 -- [T-P1-59] Extract LinkedIn Coding questions with full solutions
- **What I did**: Extracted and expanded 15 coding questions from LinkedIn phone screen interviews into full Q&A format. Sources: 文本面经.txt (items 1-3, 5-6, 11, 13, 15, 17-20) and screenshots (S27 consecutive subsequences, S30 SQL article views, S32 SQL+Python video posts). Each includes complete English problem statement, detailed solution with code, complexity analysis, tags, and difficulty estimate. Breakdown: 8 algorithm/DS (O(1) DS, course schedule, find leaves, centroid decomposition, Trie, nested list sum, convex number, locker toggle), 3 advanced (BST common ancestor, function mapping sort, coins DP), 1 backtracking (phone number), 1 array (consecutive subsequences), 2 SQL/data (article types, video uploads). Deduped against ml_theory_and_coding.json (items 7, 10, 12, 16 already extracted there).
- **Deliverables**: MLInterviewPrep/data/linkedin_seed/coding.json (15 questions)
- **Sanity check result**: JSON validated against InterviewQuestionCreate schema. All 15 entries pass: company=LinkedIn, valid question_type=coding, non-empty tags, difficulty in {easy,medium,hard}, interview_round=phone_screen.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-59 --status completed`

## 2026-03-25 -- [T-P1-62] Bulk import LinkedIn seed data into DB
- **What I did**: Created `scripts/import_linkedin_seed.py` to bulk import all LinkedIn seed JSON files into the `interview_questions` table. The script reads coding.json (15), ml_theory_and_coding.json (8), and ml_system_design.json (24) = 47 total questions. It validates required fields (question_text, company=LinkedIn), handles duplicates via dedup on question_text, and serializes tags as JSON. Also updated LinkedIn company entry with prep_notes summarizing phone screen format and set status=phone_screen.
- **Deliverables**: MLInterviewPrep/scripts/import_linkedin_seed.py, updated data/mle_prep.db (47 LinkedIn questions + company prep_notes)
- **Sanity check result**: All 47 questions imported with correct company, question_type distribution (21 ml_system_design, 15 coding, 4 ml_theory, 3 general_system_design, 2 ml_coding, 2 behavioral), non-empty tags, valid difficulties, interview_round=phone_screen. Zero duplicates. Idempotency verified (re-run skips all 47).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-62 --status completed`

## 2026-03-26 -- [T-P1-65] Update behavioral_examples DB schema + import improved stories
- **What I did**: Phase 1: Added migration v14 to `database.py` adding 3 new columns (risk_statement, analogy, tech_terms) to behavioral_examples. Updated ORM model, Pydantic schemas (Create/Update/Response), and router response builder to support the new fields. Phase 2: Created `scripts/update_improved_bq.py` that parses `docs/bq_improved_stories.md` and updates all 28 examples with improved situation/action/result text plus new risk_statement (28/28), analogy (15/28), and tech_terms JSON dict (12/28). Script runs backup first, supports --dry-run (default) and --apply modes, uses single transaction. Updated frontend `BehavioralQuestions.tsx` ExampleCard to display risk statement, analogy, and tech terms sections.
- **Deliverables**: `src/backend/database.py` (migration v14), `src/backend/models/behavioral.py` (3 columns + tech_terms_dict property), `src/backend/schemas/behavioral.py` (3 fields in Create/Update/Response), `src/backend/routers/behavioral.py` (response builder + CRUD), `scripts/update_improved_bq.py` (new, ~300 lines), `src/frontend/src/pages/BehavioralQuestions.tsx` (3 new display sections)
- **Sanity check result**: 7/7 AC passed -- v14 migration applied (idempotent), 28/28 records updated in single transaction, backup runs before apply, --dry-run/--apply both work, JSON validated, frontend TypeScript check clean, 996 tests pass
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-65 --status completed`

## 2026-03-26 -- [T-P1-70] Fix MLInterviewPrep ruff lint errors
- **What I did**: Fixed all 9 ruff lint errors across 5 script files. Added `# noqa: E402` to 8 imports that must follow `sys.path.insert()` in scripts (content_llm_orchestration.py, content_module_arbitration.py, seed_behavioral.py, seed_system_designs.py). Removed unused `story_pattern` variable in update_improved_bq.py (F841).
- **Deliverables**: `scripts/content_llm_orchestration.py`, `scripts/content_module_arbitration.py`, `scripts/seed_behavioral.py`, `scripts/seed_system_designs.py`, `scripts/update_improved_bq.py`
- **Sanity check result**: `ruff check src/ tests/ scripts/` = 0 errors ("All checks passed!"), 996 tests pass
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-70 --status completed`

## 2026-03-26 -- [T-P1-81] Blog to Prep - DDIA Fundamentals (Ch1-9)
- **What I did**: Created MLInterviewPrep/docs/prep_ddia_fundamentals.md from 9 DDIA blog notes (Ch1-9, ~1159 lines total). Consolidated into one interview-ready reference covering three pillars (reliability/scalability/maintainability), data models (relational/document/graph), storage engines (LSM-tree vs B-tree with trade-offs table), OLTP vs OLAP (star schema, column storage, bitmap encoding), encoding formats (JSON/protobuf/Avro with compatibility rules), and communication patterns (REST/RPC/message passing/actor model).
- **Deliverables**: MLInterviewPrep/docs/prep_ddia_fundamentals.md (352 lines) with 6 sections: Overview, Core Concepts (14 subsections), Implementation (2 Python decision helpers), Interview Patterns table + 10 questions, Comparisons (4 tables: data model, storage engine, encoding format, communication pattern), 8 Key Takeaways. Framework node id=2 registered under system_design path with status=review.
- **Sanity check result**: 31/31 content checks pass. 14 subsections, 70 table rows, 18 checklist items.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-81 --status completed`

## 2026-03-26 -- [T-P1-83] Blog to Prep - DDIA Distributed Systems & Consensus (Ch16-17)
- **What I did**: Created MLInterviewPrep/docs/prep_ddia_distributed_consensus.md from 2 DDIA blog notes (Ch16-17, ~649 lines total). Consolidated unreliable networks, Phi Accrual failure detector, clock synchronization (NTP), process pauses, fencing tokens, linearizability vs serializability, CAP theorem, causal consistency, Lamport timestamps, total order broadcast, 2PC/3PC/XA, fault-tolerant consensus (Raft/Paxos/ZAB), epoch numbering, and ZooKeeper coordination.
- **Deliverables**: MLInterviewPrep/docs/prep_ddia_distributed_consensus.md (475 lines) with 6 sections. Framework node id=4 registered under system_design with status=review.
- **Sanity check result**: 30/30 content checks pass. 20 checklist items, 84 table rows, 3 code blocks.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-83 --status completed`

## 2026-03-26 -- [T-P1-84] Blog to Prep - DDIA Batch & Stream Processing (Ch18-19)
- **What I did**: Created MLInterviewPrep/docs/prep_ddia_batch_stream.md from 2 DDIA chapter notes (Ch18-19, ~438 lines total). Consolidated Unix philosophy and batch design, MapReduce execution model (mapper/reducer/shuffle), join patterns (reduce-side sort-merge, broadcast/partitioned/merge map-side joins), skew handling (hot keys), dataflow engines (Spark RDD lineage, Flink checkpoints, Tez), Pregel/BSP graph processing, event streams, message brokers (traditional vs log-based Kafka), CDC, event sourcing, CQRS, stream processing operators (CEP, analytics, materialized views), window types (tumbling/hopping/sliding/session), stream joins (stream-stream/stream-table/table-table), and exactly-once semantics (microbatching, checkpointing, idempotence).
- **Deliverables**: MLInterviewPrep/docs/prep_ddia_batch_stream.md (463 lines) with 6 sections: Overview, Core Concepts (27 subsections), Implementation (3 Python decision frameworks), Interview Patterns table + 12 questions, Comparisons (5 tables: batch vs stream, MR vs dataflow, broker architectures, join strategies, CDC vs event sourcing), 8 Key Takeaways. Framework node id=5 registered under system_design with status=review. Archived older PROGRESS.md entries (284 lines) to archive/progress_log.md.
- **Sanity check result**: 29/30 content checks pass (only "data lake" missing -- minor single-sentence mention in source, not a core concept). 27 subsections, 67 table rows, 3 code blocks, 20 checklist items.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-84 --status completed`

## 2026-03-26 -- Blog to Prep: LambdaMART/XGBoost LTR + Fix ResponseValidationError
- **What I did**: (1) Created prep_learning_to_rank.md from LambdaMART_XGBoost_LTR blog post. Covers RankNet -> LambdaRank -> LambdaMART progression with full math, XGBoost rank:ndcg implementation, toy example (5-doc hand calculation), DoorDash phone screen scenario, 10 interview patterns, 12 questions. (2) Fixed ResponseValidationError bug: node id=192 had NULL values for progress_pct/confidence_level/importance/priority. Added Pydantic field_validators to coalesce None, added server_default to SQLAlchemy model, fixed _propagate_upward NULL arithmetic, patched existing DB row.
- **Deliverables**: MLInterviewPrep/docs/prep_learning_to_rank.md (300 lines), fixes in schemas/framework.py, models/framework.py, routers/framework.py
- **Sanity check result**: All 996 tests pass. 6 template sections present, 3 code blocks, 22 checklist items, 76 table rows. DB NULL row fixed.
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-88] Expand LTR prep doc with Q&A and detailed examples
- **What I did**: Expanded prep_learning_to_rank.md from 300 to 548 lines. Added 12 detailed interview Q&As (RankNet->LambdaMART progression, NDCG non-differentiability, delta NDCG role, XGBoost adaptation, position bias, multi-stage ranking, pair sampling, convergence behavior). Added gradient computation walkthrough (5 steps with full derivations), comprehensive XGBoost LTR parameter reference (6 ranking-specific + 8 tree parameters with LTR-tuned values), expanded toy example with step-by-step NDCG/DCG/lambda calculations from original blog post. Updated framework node 114 (Learning to Rank) to status=review, progress=80%.
- **Deliverables**: MLInterviewPrep/docs/prep_learning_to_rank.md (548 lines, 12 Q&A, 124 table rows)
- **Sanity check result**: 12 Q&A entries present, all 6 template sections intact, 548 lines total.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-88 --status completed`

## 2026-03-26 -- [T-P1-90] [T-P1-91] Sync LeetCode problem notes + fix DB issues
- **What I did**: (1) Added notes for 4 LeetCode problems (LC 3229, 17, 149, 2502) based on user's solutions, matching existing Chinese note style with solution approach, key techniques, edge cases, complexity. (2) Fixed DB issues: set URLs for 3 new problems, fetched LeetCode descriptions via GraphQL API, marked Delivery Heatmap (id=156) and LC 17 as completed, synced LTR prep doc content (33,525 chars) to framework node 114's description field.
- **Deliverables**: 4 problem notes in DB, 3 LeetCode descriptions fetched, 2 completion status fixes, LTR content synced to framework node
- **Sanity check result**: All 5 problems verified: descriptions present (413-2719 chars), notes present (564-2484 chars), is_completed=1. Framework tree Pydantic validation passes.
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-92] Fix description format: plain text -> HTML
- **What I did**: Scanned all 158 problems with descriptions. Found 3 (LC 3229, 149, 2502) stored as plain text instead of HTML. Re-fetched via LeetCode GraphQL as raw HTML. Updated feedback memory with correct convention: store `question.content` HTML as-is, never convert via `soup.get_text()`.
- **Deliverables**: 3 descriptions re-fetched as HTML, feedback memory updated
- **Sanity check result**: All 158 descriptions now contain HTML tags. Verified `<p>`, `<code>` present in re-fetched descriptions.
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-93] Add LC 981 Time Based Key-Value Store with notes
- **What I did**: Updated LC 981 (already in DB as id=88) with detailed notes: code simplification (removed redundant mid recalculation), bisect alternative using chr(127) upper bound trick, edge cases, related problems (LC 729, 352, 1146). Fetched HTML description (2609 chars). Marked completed, comfort=3.
- **Deliverables**: LC 981 notes (1648 chars) + HTML description in DB
- **Sanity check result**: is_completed=1, description_source=leetcode, desc=2609 chars, notes=1648 chars
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-98] Scan and plan: problem notes audit + frontend fixes
- **What I did**: Scanned all 159 problems. Found 70 with short notes (<200 chars, no code blocks), 73 with no notes. Identified 3 frontend bugs (search client-side only, All tab paginated at 20, search not shared across tabs). Created 4 tasks: T-P1-94 (backend search), T-P1-95 (All tab pagination), T-P2-96 (search persistence), T-P1-97 (batch expand 70 problem notes).
- **Deliverables**: 4 tasks in task_db, audit data
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-99] Enrich task plans with implementation specs
- **What I did**: Updated T-P1-94/95/96/97 with detailed implementation context: exact file paths, line numbers, code snippets, acceptance criteria. Set dependency T-P2-96 -> T-P1-94. Regenerated TASKS.md.
- **Deliverables**: 4 enriched task descriptions in task_db
- **Status**: [DONE]

## 2026-03-26 -- Ad-hoc: Add Uber phone screen to interview events
- **What I did**: Added Uber phone screen with Meng Tang (2026-04-01 11:00 AM PT, 60 min, HackerRank) to interview_events table. Fixed past events (LinkedIn app deadline, Uber HR call, DoorDash technical chat) status from 'upcoming' to 'completed'. Launched autonomous_run.sh for T-P1-94 + T-P1-95. Corrected date from Mar 27 to Apr 01.
- **Deliverables**: interview_events row id=5, 3 past events status fixed
- **Status**: [DONE]

## 2026-03-26 -- [T-P2-189] Add [project].dependencies to pyproject.toml
- **What I did**: Added `dependencies` list to `[project]` section in pyproject.toml with all 11 runtime deps from requirements.txt (fastapi, uvicorn, sqlalchemy, anthropic, pydantic, pydantic-settings, python-dotenv, python-multipart, httpx, python-docx, edge-tts). Also added missing pytest-asyncio and pyyaml to dev optional-dependencies. Validated TOML parsing and ran full test suite (996 passed).
- **Deliverables**: pyproject.toml updated with dependencies section
- **Sanity check result**: `tomllib.load()` passes, ruff clean, 996/996 tests pass
- **Status**: [DONE]

## 2026-03-26 -- [T-P2-188] Remove deprecated stop-cache from test_check.py
- **What I did**: Removed check_stop_cache/write_stop_cache imports and usage from `.claude/hooks/test_check.py`. Per LESSONS.md, the lint cache caused false passes; the same risk applies to test cache. Tests now run unconditionally on every Stop hook invocation. Also marked T-P1-184 as blocked (requires writes to helixos .claude/hooks/ which is outside permitted working directory).
- **Deliverables**: `.claude/hooks/test_check.py` updated (cache removed)
- **Sanity check result**: Hook runs correctly with valid input, ruff clean, 996/996 tests pass
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-190] Add backend search to GET /problems API
- **What I did**: Added `search` query param to `GET /api/problems` that does server-side ILIKE across title, tags, pattern, company_tags, and notes. Updated frontend to send search param to API and removed client-side filter. Added search to pagination-reset filter key. Added 12 new tests covering title/pattern/tags/company/notes search, case insensitivity, no-match, combined filters, and X-Total-Count.
- **Deliverables**: `src/backend/routers/problems.py` (search param + ILIKE filter), `src/frontend/src/pages/Problems.tsx` (server-side search), `tests/test_router_problems.py` (12 new tests)
- **Sanity check result**: Ruff clean, 1006/1006 tests pass (140 in test_router_problems.py)
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-191] Fix All tab: load all results when searching
- **What I did**: When search is active on the All tab, switched from PAGE_SIZE=20 to limit=200 so all matching results appear on one page. Added `loadAll` flag (true when searching or on Blind75 tab) to control limit/offset. Also updated totalPages calculation to use effective page size so pagination hides correctly when all results fit.
- **Deliverables**: `src/frontend/src/pages/Problems.tsx` (loadAll logic for limit/offset/pagination)
- **Sanity check result**: TypeScript compiles clean (tsc --noEmit passes)
- **Status**: [DONE]

## 2026-03-26 -- [T-P1-193] Batch expand Blind75 problem notes - batch 1
- **What I did**: Expanded notes for 14 Blind75 problems (LC 1, 3, 11, 15, 19, 20, 21, 33, 39, 48, 49, 53, 54, 55) with structured sections: 思路, 关键技巧, 核心代码 (Python code blocks), 注意点, 复杂度. Merged with existing notes (preserved as "Original notes" prefix). Written via sqlite3 update to data/mle_prep.db.
- **Deliverables**: `scripts/expand_notes_batch1.py` (expansion script), `data/mle_prep.db` (14 problems updated)
- **Sanity check result**: Verified DB reads back correctly with original notes preserved and all sections present
- **Status**: [DONE]
