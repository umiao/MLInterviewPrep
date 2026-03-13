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

## 2026-03-01 -- Task Deduplication Defense-in-Depth
- **What I did**: Implemented 3-layer dedup defense: clarified docs (CLAUDE.md, exit-protocol.md), added read-time filtering in session_context.py, created task_dedup_check.py stop hook, and registered it in settings.json. Added 10 tests.
- **Deliverables**: Modified CLAUDE.md, docs/workflow/exit-protocol.md, .claude/hooks/session_context.py, .claude/settings.json. New files: .claude/hooks/task_dedup_check.py, tests/test_task_dedup.py.
- **Sanity check result**: ruff clean, 11/11 pytest pass, hook exits 0 on clean TASKS.md, hook exits 2 and prints diagnostic on duplicate task IDs.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-02 -- Git Pre-Commit Hook for Ruff Version Consistency
- **What I did**: Pinned ruff==0.1.14 in requirements.txt, fixed CI lint job to use requirements.txt, created a POSIX pre-commit hook (version guard + ruff lint + emoji scan), created check_emoji_files.py for targeted file scanning, created setup-hooks.sh installer, and updated docs (QUICKSTART, README, CLAUDE.md, LESSONS).
- **Deliverables**: Modified requirements.txt, .github/workflows/ci.yml, scripts/QUICKSTART.md, README.md, CLAUDE.md, LESSONS.md. New files: scripts/check_emoji_files.py, scripts/git-hooks/pre-commit, scripts/setup-hooks.sh.
- **Sanity check result**: ruff clean, emoji scan clean, 11/11 pytest pass, setup-hooks.sh installs successfully, version extraction tested.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-12 -- Emoji Guard False Positives + TASKS.md Sync + Stop Hook Resilience
- **What I did**: Removed BMP ranges (U+2600-U+26FF, U+2700-U+27BF) from emoji regex in lint_check.py and check_emoji_files.py to eliminate 81 false positives on symbols like BLACK STAR. Added code-vs-doc distinction in stop hook so doc file emoji warns but doesn't block. Added TASKS.md auto-staging in task_db.py, pre-commit consistency check, .claude/tasks.db to .gitignore, and fresh-clone DB-missing warning in session_context.py. Extracted _get_completed_task_ids as public function and created missing task_dedup_check.py module to fix pre-existing test import errors.
- **Deliverables**: Modified .claude/hooks/lint_check.py, scripts/check_emoji_files.py, .claude/hooks/task_db.py, scripts/git-hooks/pre-commit, .claude/hooks/session_context.py, .gitignore. New files: tests/test_emoji_regex.py, .claude/hooks/task_dedup_check.py.
- **Sanity check result**: ruff clean, stop hook exits 0 (doc emoji warned not blocked), 80/80 tests pass (20 pre-existing router failures excluded), 7 emoji regex regression tests pass.
- **Status**: [DONE]
- **Request**: No change

## 2026-03-12 -- [T-P0-1] Pin all dependencies to exact versions
- **What I did**: Pinned all dependencies in requirements.txt to exact versions (fastapi==0.109.0, uvicorn==0.41.0, sqlalchemy==2.0.25, anthropic==0.84.0, pydantic-settings==2.13.1, httpx==0.27.2, beautifulsoup4==4.12.2, playwright==1.58.0, ruff==0.15.4, pytest==7.4.4). Updated pyproject.toml optional-deps (dev: pytest, httpx, ruff; scraper: playwright, beautifulsoup4) with exact pins.
- **Deliverables**: Modified requirements.txt, pyproject.toml
- **Sanity check result**: pip install succeeds, all imports work, ruff clean, 17/17 tests pass
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-1 --status completed`

## 2026-03-12 -- [T-P0-2] Config module with pydantic-settings
- **What I did**: Verified existing config.py (Settings class with DATABASE_URL, ANTHROPIC_API_KEY, LLM_MODEL, CORS_ORIGINS, DEBUG, env_file_encoding=utf-8). Added CORS_ORIGINS to .env.example. Expanded tests from 2 to 5: added defaults validation, get_settings() test, CORS_ORIGINS from env test.
- **Deliverables**: Modified .env.example, tests/test_config.py
- **Sanity check result**: 5/5 config tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-2 --status completed`

## 2026-03-12 -- [T-P0-3] Database engine + session setup
- **What I did**: Verified existing database.py (Base, get_engine with URL override, SessionLocal, get_db generator, init_db with data dir creation, check_same_thread=False for SQLite). Expanded tests from 2 to 8: added get_engine override, check_same_thread, default URL, data dir creation, generator lifecycle, SessionLocal binding tests.
- **Deliverables**: Modified tests/test_database.py (2 -> 8 tests)
- **Sanity check result**: 8/8 database tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-3 --status completed`

## 2026-03-12 -- [T-P0-4] Module 1 SQLAlchemy models (Problem, Attempt, QASession)
- **What I did**: Verified existing models in src/backend/models/problem.py (Problem with nullable leetcode_id, difficulty/category/priority CheckConstraints, tags/company_tags JSON properties; Attempt with result CheckConstraint, llm_review Text; QASession with messages JSON). Expanded tests from 5 to 16: added nullable leetcode_id, defaults, tags_list setter, empty tags, invalid difficulty, all valid results, llm_review text, QA linked/unlinked to problem, messages_list setter, cascade delete.
- **Deliverables**: Modified tests/test_models_problem.py (5 -> 16 tests)
- **Sanity check result**: 16/16 model tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-4 --status completed`

## 2026-03-12 -- [T-P0-5] Module 2 SQLAlchemy models (SeedURL, ScrapedPage, InterviewQuestion)
- **What I did**: Verified existing models in src/backend/models/scraper.py (SeedURL with url UNIQUE, source_site CheckConstraint; ScrapedPage with UniqueConstraint(url,content_hash); InterviewQuestion with question_type CheckConstraint, mapped_framework_node_id FK, tags JSON property). Expanded tests from 5 to 19: added defaults, invalid source_site, all valid source_sites, relationship to scraped_pages, page creation defaults, same url/different hash OK, different url/same hash OK, cascade delete questions, question defaults, all valid types, tags_list property/setter, empty tags, linked to scraped page, nullable type.
- **Deliverables**: Modified tests/test_models_scraper.py (5 -> 19 tests)
- **Sanity check result**: 19/19 model tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-5 --status completed`

## 2026-03-12 -- [T-P0-6] Module 3 SQLAlchemy models (FrameworkNode, StudyLog, Company, CompanyTopicWeight)
- **What I did**: Verified existing models in src/backend/models/framework.py (FrameworkNode with self-referential parent/children, path UNIQUE, status/progress_pct/confidence_level CheckConstraints, relevant_companies JSON property) and src/backend/models/company.py (Company with name UNIQUE, status CheckConstraint, interview_stages JSON; CompanyTopicWeight with composite PK, weight CheckConstraint). Expanded tests from 5 to 28: added defaults, all valid statuses, invalid status, progress_pct range, confidence range, relevant_companies property, cascade delete children/study_logs/weights, study_log defaults/notes, company defaults/statuses/interview_stages, weight default/relationships.
- **Deliverables**: Modified tests/test_models_framework.py (5 -> 28 tests)
- **Sanity check result**: 28/28 model tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-6 --status completed`

## 2026-03-12 -- [T-P0-7] FastAPI app skeleton + health endpoint
- **What I did**: Verified existing main.py (FastAPI app with lifespan calling init_db, CORS middleware with configurable origins, GET /api/health returning {status:ok}, all routers under /api prefix). Wrote 9 tests covering health endpoint (200 status, JSON body, content-type), CORS middleware (allowed origin, credentials, methods), and app config (title, /api prefix on all routes, 404 for unknown routes).
- **Deliverables**: Created tests/test_main.py (9 tests)
- **Sanity check result**: 9/9 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-7 --status completed`

## 2026-03-12 -- [T-P0-8] Pydantic schemas for Problem CRUD
- **What I did**: Enhanced existing schemas with JSON-to-list validator on ProblemResponse (tags/company_tags stored as JSON text in SQLAlchemy but exposed as lists). Expanded test suite from 8 to 30 tests covering all schemas (ProblemCreate, ProblemUpdate, ProblemResponse, AttemptCreate, AttemptResponse) with boundary values, invalid inputs, from_attributes, and exclude_unset behavior.
- **Deliverables**: Modified src/backend/schemas/problem.py (added field_validator), rewrote tests/test_schemas_problem.py (30 tests)
- **Sanity check result**: 30/30 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-8 --status completed`

## 2026-03-12 -- [T-P0-9] GET /api/problems list with filters
- **What I did**: Wrote 30 new tests for the GET /api/problems endpoint covering all filter types (difficulty, pattern, source, company JSON contains, is_completed, category), AND-together behavior of multiple filters, X-Total-Count header with pagination, sorting by comfort_level/created_at asc/desc, and pagination edge cases (offset beyond total, last partial page). Also fixed conftest.py by adding StaticPool to the in-memory SQLite engine so test_client fixture works reliably.
- **Deliverables**: Rewrote tests/test_router_problems.py (43 tests total), modified tests/conftest.py (StaticPool fix)
- **Sanity check result**: 222/222 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-9 --status completed`

## 2026-03-12 -- [T-P0-10] POST /api/problems (create) comprehensive tests
- **What I did**: Expanded POST /api/problems test coverage from 3 to 20 tests. Covers: all-fields create, minimal-fields defaults, tags/company_tags JSON conversion, empty tags, duplicate leetcode_id 409, null leetcode_id no-conflict (3 problems), different leetcode_ids OK, each category/difficulty/priority value, invalid priority/title/difficulty/category 422, persistence in list, and unicode tags.
- **Deliverables**: Modified tests/test_router_problems.py (59 tests total)
- **Sanity check result**: 238/238 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-10 --status completed`

## 2026-03-12 -- [T-P0-11] PUT/DELETE /api/problems/{id} comprehensive tests
- **What I did**: Expanded PUT/DELETE test coverage from 3 tests to 29 tests. PUT tests cover: partial update preserving unchanged fields, update each field individually (title, difficulty, category, priority, tags, company_tags, comfort_level, is_completed, url, leetcode_id), update tags to empty, update multiple fields at once, empty body no-op, invalid values 422 (difficulty, category, priority, comfort_level, empty title), 404 on non-existent id, persistence verification. DELETE tests cover: 204 return, removed from list, cascade deletes attempts, 404 on non-existent, double-delete 404, total count decreases, does not affect other problems.
- **Deliverables**: Modified tests/test_router_problems.py (84 tests total)
- **Sanity check result**: 263/263 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-11 --status completed`

## 2026-03-12 -- [T-P0-12] POST/GET /api/problems/{id}/attempts comprehensive tests
- **What I did**: Expanded POST/GET attempts test coverage from 3 tests to 40 tests. POST tests cover: 201 status, response fields (id, problem_id, started_at), minimal fields, all optional fields, each result type (solved/hint/failed/timeout), problem state updates (last_attempted_at, comfort_level, next_review_at), is_completed threshold (comfort>=3), is_completed sticky (stays True on low comfort), multiple attempts updating comfort each time, next_review_at progression. Validation: missing result/comfort_after 422, invalid result 422, comfort_after out of range (0,6) 422, negative duration 422, empty body 422, nonexistent problem 404. Edge cases: duration=0 allowed, no cross-problem contamination, llm_review initially null. GET tests: empty list, 200 status, newest first ordering, count matches, isolated per problem, 404 nonexistent, response fields, cascade on delete.
- **Deliverables**: Modified tests/test_router_problems.py (121 tests total)
- **Sanity check result**: 300/300 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-12 --status completed`

## 2026-03-12 -- [T-P0-13] Spaced repetition service (SM-2 variant)
- **What I did**: Verified existing spaced_repetition.py implementation (compute_next_review + update_review_schedule) matches design doc spec. Expanded test coverage from 7 to 56 tests covering: all comfort levels (1-5) with various intervals, clamping behavior (zero/negative intervals), parametric combinations, first attempt (None last_attempted_at), subsequent attempts with various gaps, multi-review progression chains, comfort regression resets, gradual comfort growth, return type validation, monotonicity property (higher comfort -> longer interval), determinism.
- **Deliverables**: Modified tests/test_spaced_repetition.py (56 tests)
- **Sanity check result**: 349/349 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-13 --status completed`

## 2026-03-12 -- [T-P0-14] Wire SM-2 into attempt creation
- **What I did**: Verified SM-2 wiring already implemented in POST /api/problems/{id}/attempts (update_review_schedule called BEFORE last_attempted_at update, next_review_at set). Created 18 dedicated integration tests verifying: exact interval calculations for all comfort levels (1-5) on first attempt, next_review_at initially None then set, ordering correctness (SM-2 sees old last_attempted_at via mock spy), monotonicity (higher comfort -> further review), interval growth with repeated high comfort, low comfort reset, is_completed interaction, argument verification via patch spy.
- **Deliverables**: Created tests/test_sm2_wiring.py (18 tests)
- **Sanity check result**: 367/367 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-14 --status completed`

## 2026-03-12 -- [T-P0-15] GET /api/problems/review-queue tests
- **What I did**: Verified the review-queue endpoint was already implemented (returns problems where next_review_at <= now, ordered ASC, null excluded). Created 17 comprehensive tests covering: empty DB, due/future/null filtering, ASC ordering (most overdue first), default limit (20), custom limit, limit validation (min/max), response field shape, edge cases (exactly-now, mix of states, completed-but-due), limit+ordering interaction, and integration with SM-2 attempt creation (low/high comfort).
- **Deliverables**: Created tests/test_review_queue.py (17 tests)
- **Sanity check result**: 384/384 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-15 --status completed`

## 2026-03-12 -- [T-P1-63] Shared test fixtures + bulk task status update
- **What I did**: Audited all P0 and early P1 tasks against existing codebase. Found that 24 tasks (T-P0-16 through T-P1-33) were already fully implemented from prior sessions but not marked completed. Marked all as completed. Added mock_llm and mock_llm_text fixtures to tests/conftest.py to complete the shared fixtures task (was missing only the LLM mock).
- **Deliverables**: Updated tests/conftest.py (added mock_llm, mock_llm_text fixtures), updated 24 task statuses to completed
- **Sanity check result**: 384/384 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-63 --status completed`

## 2026-03-12 -- [T-P1-45] Add comprehensive dashboard endpoint tests
- **What I did**: Wrote 13 tests for GET /api/dashboard covering empty DB (zeros), problem counts, framework weighted progress, pillars, recent activity (attempts/study hours/questions in 7d window), company deadlines, scraper totals, and a full integrated scenario. Endpoint implementation was already in place from prior sessions.
- **Deliverables**: tests/test_dashboard.py (13 tests across 7 test classes)
- **Sanity check result**: 397/397 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-45 --status completed`

## 2026-03-12 -- [T-P1-46] Enhance GET /api/export with full data
- **What I did**: Enhanced the existing GET /api/export endpoint to include all model fields and nested relationships: problems with full attempts (approach_notes, complexity, timestamps), framework_nodes with study_logs, companies with topic_weights and interview_stages, interview_questions with all fields (level, round, year, tags, difficulty_estimate). Added datetime serialization helpers. Wrote 11 comprehensive tests across 6 test classes.
- **Deliverables**: src/backend/main.py (enhanced export_data endpoint), tests/test_export.py (11 tests)
- **Sanity check result**: 408/408 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-46 --status completed`

## 2026-03-13 -- [T-P1-47] Add POST /api/import JSON and CSV endpoints
- **What I did**: Implemented POST /api/import for JSON data import with merge semantics (skip existing by leetcode_id/title for problems, path for framework nodes, name for companies; questions always insert). Implemented POST /api/import/csv for CSV problem import with semicolon-separated tags. Both return {inserted, skipped, errors} per section. Wrote 19 comprehensive tests across 8 test classes including round-trip export/import idempotency test.
- **Deliverables**: src/backend/main.py (import endpoints + helper functions), tests/test_import.py (19 tests)
- **Sanity check result**: 427/427 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-47 --status completed`

## 2026-03-13 -- [T-P1-64] Integration test -- problem lifecycle
- **What I did**: Wrote 17 integration tests across 7 test classes covering the full problem lifecycle: create problem, attempt with low comfort, verify review queue scheduling, LLM review storage, attempt with high comfort, verify mastery. Also covers edge cases (duplicate leetcode_id, null IDs, minimal creation), spaced repetition scheduling math, completion flag stickiness, stats aggregation, weak pattern detection, and delete cascade.
- **Deliverables**: tests/test_integration_problem_lifecycle.py (17 tests)
- **Sanity check result**: 444/444 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-64 --status completed`

## 2026-03-13 -- [T-P1-65] Integration test -- scraper pipeline
- **What I did**: Wrote 24 integration tests across 8 test classes covering the full scraper pipeline: seed URL CRUD + dedup + filters, paste text extraction with LLM mock, duplicate paste caching, question listing with company/type/search/reviewed filters, pagination, question update, LLM question analysis with storage verification, and scraper job status. Also fixed a pre-existing bug where InterviewQuestionResponse.tags failed validation because the DB stores tags as JSON strings.
- **Deliverables**: tests/test_integration_scraper_pipeline.py (24 tests), src/backend/schemas/scraper.py (tags JSON validator fix)
- **Sanity check result**: 468/468 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-65 --status completed`

## 2026-03-13 -- [T-P1-66] Integration test -- framework + study planning
- **What I did**: Wrote 30 integration tests across 8 test classes covering the full framework + study planning pipeline: seed framework tree + max_depth filter, study log auto-progress calculation + accumulation + 95% cap, node status updates with side effects (mastered sets 100%), framework stats aggregation, company CRUD + topic weight upsert, company focus endpoint with progress filtering, study suggestions with urgency ordering + mastered exclusion + company weight boost + study-reduces-urgency + deadline factor, LLM plan text generation, and a full end-to-end journey test.
- **Deliverables**: tests/test_integration_framework_study.py (30 tests)
- **Sanity check result**: 498/498 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-66 --status completed`

## 2026-03-13 -- [T-P1-61] Backend Dockerfile
- **What I did**: Created Dockerfile for the backend service using Python 3.11-slim base image. Installs requirements, copies src/, exposes port 8000, runs uvicorn. Added .dockerignore to exclude non-essential files (tests, .git, .env, data/, etc.). Data directory is created inside the container for SQLite volume mount.
- **Deliverables**: Dockerfile, .dockerignore
- **Sanity check result**: 498/498 tests pass, ruff clean on Python source. Docker not available in CI env for build test but Dockerfile structure verified manually.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-61 --status completed`

## 2026-03-13 -- [T-P1-49] React + Vite + Tailwind scaffolding
- **What I did**: Scaffolded the frontend app in src/frontend/ using Vite 8 + React 19 + TypeScript template. Installed Tailwind CSS v4 (PostCSS integration), React Router v6. Created base Layout with sidebar navigation (Dashboard, LeetCode, Framework, Questions, Companies) and placeholder pages. Configured Vite proxy for /api to localhost:8000.
- **Deliverables**: src/frontend/ (package.json, vite.config.ts, postcss.config.js, src/index.css, src/main.tsx, src/App.tsx, src/components/Sidebar.tsx, src/components/Layout.tsx, src/pages/{Dashboard,Problems,Framework,Questions,Companies}.tsx)
- **Sanity check result**: Frontend builds clean (tsc + vite build), ESLint clean, backend 498/498 tests pass, ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-49 --status completed`

## 2026-03-13 -- [T-P1-50] API utility layer + hooks
- **What I did**: Created the frontend API utility layer and React hooks. `utils/api.ts`: typed fetch wrapper with base URL (/api), JSON serialization, error handling via ApiRequestError class, query param builder, and methods for GET/POST/PUT/DELETE. `hooks/useApi.ts`: useApi hook (auto-fetch on mount with {data, loading, error, refetch}) and useMutation hook for POST/PUT/DELETE operations. `hooks/useTimer.ts`: stopwatch hook with start/pause/reset/elapsed for problem practice sessions.
- **Deliverables**: src/frontend/src/utils/api.ts, src/frontend/src/hooks/useApi.ts, src/frontend/src/hooks/useTimer.ts
- **Sanity check result**: ESLint clean, TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-50 --status completed`

## 2026-03-13 -- [T-P1-51] Dashboard page
- **What I did**: Built the Dashboard page consuming GET /api/dashboard. Created TypeScript types for the dashboard response. Implemented progress rings (completed/remaining problems), review queue badge (amber when >0, green when 0), framework pillar bar chart with overall progress percentage, weekly activity stat cards (attempts, study hours, questions added, total questions), and company deadline cards with color-coded status badges.
- **Deliverables**: src/frontend/src/types/dashboard.ts, src/frontend/src/pages/Dashboard.tsx
- **Sanity check result**: TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-51 --status completed`

## 2026-03-13 -- [T-P1-52] Problem list page with filters
- **What I did**: Built the Problem list page with filter sidebar (difficulty radio, category dropdown, pattern dropdown populated from API, source text input, company text input, completed status dropdown), sortable table with comfort stars, pattern badges, review-due indicators, difficulty badges, company tags, and pagination. Extended api.ts with getWithTotal() to read X-Total-Count header. Created TypeScript types for Problem and ProblemFilters.
- **Deliverables**: src/frontend/src/types/problem.ts, src/frontend/src/pages/Problems.tsx, src/frontend/src/utils/api.ts (added getWithTotal)
- **Sanity check result**: TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-52 --status completed`

## 2026-03-13 -- [T-P1-53] Problem practice view + timer
- **What I did**: Built PracticeModal component with countdown timer (start/pause/reset), approach notes textarea, result dropdown (solved/hint/failed/timeout), time/space complexity inputs, comfort slider 1-5, and submit button that POSTs to /api/problems/{id}/attempts. Added Attempt/AttemptCreate types. Wired modal into Problems page via "Practice" button on each row; modal closes and refreshes list on successful submit.
- **Deliverables**: src/frontend/src/components/PracticeModal.tsx, src/frontend/src/types/problem.ts (added Attempt types), src/frontend/src/pages/Problems.tsx (added Practice button + modal)
- **Sanity check result**: TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-53 --status completed`

## 2026-03-13 -- [T-P1-54] Quick Review chat panel
- **What I did**: Built ReviewPanel slide-out component with two modes: (1) Review mode -- single-shot approach text submission to POST /api/problems/{id}/review with color-coded verdict badges (green=optimal, yellow=suboptimal, red=incorrect, blue=needs_clarification), feedback display, complexity, pattern, hint, and follow-up question; (2) QA mode -- multi-turn chat with POST /api/qa/chat, chat bubbles UI, session management (new/past sessions list), Enter-to-send. Added ReviewResult, QAChatMessage, QAChatResponse, QASessionSummary types. Wired into Problems page via purple "Review" button on each row.
- **Deliverables**: src/frontend/src/components/ReviewPanel.tsx, src/frontend/src/types/problem.ts (added review/QA types), src/frontend/src/pages/Problems.tsx (added Review button + panel)
- **Sanity check result**: TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-54 --status completed`

## 2026-03-13 -- [T-P1-55] Framework tree visualization
- **What I did**: Built the Framework page with two visualization modes: (1) Collapsible tree view with expand/collapse all, progress bars per node, confidence dots, status badges color-coded (red=not_started, yellow=in_progress, blue=review, green=mastered), indented by depth; (2) Treemap view with squarified layout, cells sized by importance, colored by status, adjustable detail depth (1-3). Added stats sidebar with overall progress stacked bar, status counts, weekly study hours, weakest nodes, hours by pillar. Node selection shows detail panel with status, progress, confidence, importance, priority, estimated hours, path. Created FrameworkNode/FrameworkStats TypeScript types.
- **Deliverables**: src/frontend/src/types/framework.ts, src/frontend/src/components/FrameworkTreeView.tsx, src/frontend/src/components/FrameworkTreemap.tsx, src/frontend/src/pages/Framework.tsx
- **Sanity check result**: TypeScript clean, Vite build succeeds, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-55 --status completed`

## 2026-03-13 -- [T-P1-56] Study log form + node detail panel
- **What I did**: Added GET /api/framework/nodes/{id}/logs endpoint returning study history (newest first, limit param). Created NodeDetailPanel component replacing the static NodeDetail sidebar: editable status dropdown and confidence slider with save button, study log form (date picker, duration, activity type, notes), study history timeline. Updated Framework page to use the new panel with refetch on updates. Added StudyLog TypeScript type. Widened sidebar to w-72 with scrollable overflow.
- **Deliverables**: src/backend/routers/framework.py (new endpoint), src/frontend/src/types/framework.ts (StudyLog type), src/frontend/src/components/NodeDetailPanel.tsx (new), src/frontend/src/pages/Framework.tsx (updated)
- **Sanity check result**: TypeScript clean, Vite build succeeds, ruff clean, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-56 --status completed`

## 2026-03-13 -- [T-P1-57] Company management kanban page
- **What I did**: Implemented the Companies page as a kanban board with 5 status columns (Applied, Phone Screen, Onsite, Offer, Rejected). Company cards show name, group tag badge, applied date, and notes snippet. Add Company modal with name, group tag, status, date, and notes fields. Click any card to open a Focus Topics side panel showing company details, status changer, and prioritized framework topics from GET /api/companies/{id}/focus. Created Company TypeScript types.
- **Deliverables**: src/frontend/src/types/company.ts (new), src/frontend/src/pages/Companies.tsx (rewritten)
- **Sanity check result**: TypeScript clean, Vite build succeeds, ruff clean, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-57 --status completed`

## 2026-03-13 -- [T-P1-58] Interview questions browse page
- **What I did**: Built the Interview Questions browse page with a filterable table supporting company, role, type, reviewed status, and text search filters. Rows are expandable to show full question details, metadata, tags, and action buttons. Mark Reviewed toggle updates the backend via PUT /questions/{id}. Analyze button calls POST /questions/{id}/analyze for LLM analysis and displays structured results (solution approach, key concepts, difficulty, related patterns, suggested study). Created InterviewQuestion and QuestionAnalysis TypeScript types. Pagination with Previous/Next controls.
- **Deliverables**: src/frontend/src/types/question.ts (new), src/frontend/src/pages/Questions.tsx (rewritten)
- **Sanity check result**: TypeScript clean, Vite build succeeds, ruff clean, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-58 --status completed`

## 2026-03-13 -- [T-P1-59] Paste experience form
- **What I did**: Added a PasteExperienceModal to the Questions page. The modal has a large textarea for pasting interview experience text, optional company and role fields, and an "Extract Questions" button that calls POST /scraper/paste. After extraction, it shows a review list of extracted questions with type badges, company, and role. Duplicate detection warns the user. A "Done" button confirms and refreshes the question list. The modal is triggered by a "+ Paste Experience" button in the page header.
- **Deliverables**: src/frontend/src/pages/Questions.tsx (modified -- added PasteExperienceModal component, paste types, modal integration)
- **Sanity check result**: TypeScript clean, Vite build succeeds, ruff clean, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-59 --status completed`

## 2026-03-13 -- [T-P1-62] Frontend Dockerfile + docker-compose.yml
- **What I did**: Created a multi-stage frontend Dockerfile (Node 20 build + nginx serve) with nginx.conf that proxies /api/ to the backend service and serves the SPA with fallback routing. Created docker-compose.yml with backend and frontend services on a shared network, named volume for SQLite data, and a healthcheck on the backend before frontend starts.
- **Deliverables**: src/frontend/Dockerfile, src/frontend/nginx.conf, src/frontend/.dockerignore, docker-compose.yml
- **Sanity check result**: Vite build succeeds, YAML valid, ruff clean, backend 498/498 tests pass.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-62 --status completed`

## 2026-03-13 -- [T-P2-48] Add DB views and indexes
- **What I did**: Added indexes on problems.pattern, problems.difficulty, problems.next_review_at, study_logs.date, and interview_questions.company. Created two SQL views: v_problem_stats (per-problem attempt aggregates) and v_weekly_progress (weekly study log summaries). Updated conftest.py to create views in test DB.
- **Deliverables**: src/backend/database.py (views), src/backend/models/problem.py (indexes), src/backend/models/framework.py (index), src/backend/models/scraper.py (index), tests/conftest.py (view creation), tests/test_db_views_indexes.py (7 new tests)
- **Sanity check result**: 505 tests pass, ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-48 --status completed`

## 2026-03-13 -- [T-P2-67] Performance + final polish
- **What I did**: Added ResponseTimeMiddleware (logs method, path, status, duration; sets X-Response-Time header). Enabled SQLite WAL journal mode for file-based databases in init_db. Added Pydantic ValidationError exception handler returning structured 422 responses. Also marked T-P2-34 as completed (already implemented in prior sessions).
- **Deliverables**: src/backend/main.py (middleware, error handler), src/backend/database.py (WAL mode via _enable_wal), tests/test_performance_polish.py (7 new tests)
- **Sanity check result**: 512 tests pass, ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-67 --status completed`

## 2026-03-13 -- [T-P2-60] AI Study Plan display card
- **What I did**: Created StudyPlanCard component for the Framework page. The card calls GET /api/framework/suggest and displays ranked study topics with urgency bars, allocated time, and progress percentages. Includes a collapsible settings panel (hours, days, company selector, LLM toggle), Generate/Regenerate buttons, and a blue panel for LLM-generated natural language plan text. Added StudyTopic and StudyPlanResult TypeScript types.
- **Deliverables**: src/frontend/src/components/StudyPlanCard.tsx (new), src/frontend/src/types/framework.ts (added types), src/frontend/src/pages/Framework.tsx (integrated card)
- **Sanity check result**: TypeScript clean, 512 backend tests pass, ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-60 --status completed`
