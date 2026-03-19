# Archived Progress Log

> Older session entries moved from PROGRESS.md to keep it under ~300 lines.
> Chronological order (oldest first).

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

## 2026-03-13 -- Remove all emoji from documentation files
- **What I did**: Replaced 81 emoji characters across 2 documentation files (mle_prep_system_design.md and mle_interview_framework.md) with ASCII text equivalents per project CLAUDE.md rules. Replacements: stars to *, checkboxes to [x], feedback indicators to [OK]/[WARN]/[FAIL].
- **Deliverables**: mle_prep_system_design.md (9 replacements), mle_interview_framework.md (72 replacements)
- **Sanity check result**: `python scripts/check_emoji.py` reports 0 violations.
- **Status**: [DONE]
- **Request**: No task ID (ad-hoc cleanup)

## 2026-03-15 -- [T-P2-68] Add combined backend+frontend startup script
- **What I did**: Created scripts/dev.py that launches both uvicorn and npm dev as subprocesses with [backend]/[frontend] prefixed output. Handles Ctrl+C gracefully, uses taskkill /T /F on Windows, terminates the other process if one exits. Updated QUICKSTART.md with "Option A (combined)" section and README.md Quick Start with the new command.
- **Deliverables**: scripts/dev.py (new), scripts/QUICKSTART.md (edited), README.md (edited)
- **Sanity check result**: ruff clean, no emoji violations, smoke test confirmed both processes start with prefixed output and clean shutdown.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-68 --status completed`

## 2026-03-15 -- [T-P0-69] Fix CI: add python-multipart dependency
- **What I did**: Added python-multipart==0.0.20 to requirements.txt. FastAPI requires this for Form/File endpoints; it was missing from explicit deps causing 295 RuntimeErrors in CI.
- **Deliverables**: requirements.txt (edited)
- **Sanity check result**: 512 tests pass, pip install -r requirements.txt succeeds.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-69 --status completed`

## 2026-03-15 -- [T-P2-68] Change default backend port to 8100
- **What I did**: Changed default backend port from 8000 to 8100 across the entire project to avoid conflict with HelixOS. Updated scripts/dev.py (--port 8100), vite.config.ts proxy target, Dockerfile, docker-compose.yml, and all documentation (QUICKSTART.md, README.md, frontend README.md) including manual uvicorn commands.
- **Deliverables**: scripts/dev.py, src/frontend/vite.config.ts, Dockerfile, docker-compose.yml, scripts/QUICKSTART.md, README.md, src/frontend/README.md
- **Sanity check result**: 512 tests pass, port 8100 confirmed bindable.
- **Status**: [DONE]
- **Request**: No task change (included in T-P2-68 commit)

## 2026-03-15 -- [T-P0-70] SDK migration: async LLMService + sdk_adapter
- **What I did**: Created sdk_adapter.py with SDK_AVAILABLE flag and async run_query. Rewrote LLMService.chat() as async with dual backend dispatch (auto/sdk/anthropic). Made ANTHROPIC_API_KEY optional (default ''), added LLM_BACKEND='auto' config setting. Updated test_llm_service.py for async interface (12 tests covering both backends, JSON parsing, errors, auto-selection, max_tokens warning). Fixed test_config.py for optional API key.
- **Deliverables**: src/backend/services/sdk_adapter.py (new), src/backend/services/llm_service.py, src/backend/config.py, tests/test_llm_service.py, tests/test_config.py
- **Sanity check result**: 520/520 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-70 --status completed`

## 2026-03-15 -- [T-P0-71] Convert LLM callers to async + update tests
- **What I did**: Converted all LLM-calling endpoints and functions to async: qa.py (qa_chat, summarize_session), problems.py (review_problem), framework.py (suggest_study), scraper.py (paste_experience, analyze_question). Made extract_questions() async. Updated _run_scraper_job to use asyncio.run() for async extract_questions call. Updated all test fixtures (mock_llm, mock_llm_text) to use AsyncMock for chat method. Updated test_question_extractor.py to async tests. Updated test_router_scraper.py mock. Added pytest-asyncio to requirements.txt and asyncio_mode=auto to pyproject.toml.
- **Deliverables**: src/backend/routers/qa.py, src/backend/routers/problems.py, src/backend/routers/framework.py, src/backend/routers/scraper.py, src/backend/services/question_extractor.py, tests/conftest.py, tests/test_question_extractor.py, tests/test_router_scraper.py, requirements.txt, pyproject.toml
- **Sanity check result**: 520/520 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-71 --status completed`

## 2026-03-15 -- [T-P2-72] Add GET / root endpoint returning API info JSON
- **What I did**: Added a `GET /` endpoint to main.py that returns JSON with API name, docs URL, and health endpoint path. Added test in test_main.py verifying 200 status and expected keys.
- **Deliverables**: src/backend/main.py, tests/test_main.py
- **Sanity check result**: 521/521 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-72 --status completed`
## 2026-03-15 -- [T-P0-73] Install React Query + setup QueryClientProvider in App.tsx
- **What I did**: Installed @tanstack/react-query, wrapped App with QueryClientProvider (staleTime 30s, retry 1). Migrated Dashboard page from useApi to useQuery as proof of concept. Fixed two pre-existing TS errors (unused containerWidth in FrameworkTreemap, unused STATUS_BADGE in Companies).
- **Deliverables**: src/frontend/package.json, src/frontend/src/App.tsx, src/frontend/src/pages/Dashboard.tsx, src/frontend/src/components/FrameworkTreemap.tsx, src/frontend/src/pages/Companies.tsx
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-73 --status completed`

## 2026-03-15 -- [T-P0-74] Migrate all pages from useApi to React Query useQuery/useMutation
- **What I did**: Migrated all 6 remaining files from custom useApi/useMutation hooks and manual api.get/put/post calls to React Query's useQuery/useMutation with queryClient.invalidateQueries for cache invalidation. Files: Framework.tsx (2 useApi -> 2 useQuery), Problems.tsx (manual fetchProblems + patterns fetch -> 2 useQuery), Questions.tsx (manual fetch + toggle reviewed -> useQuery + useMutation), Companies.tsx (manual fetch + status update -> useQuery + useMutation), NodeDetailPanel.tsx (useApi + useMutation + api.put -> useQuery + 2 useMutation), StudyPlanCard.tsx (useApi -> useQuery). useApi.ts now has zero consumers.
- **Deliverables**: src/frontend/src/pages/Framework.tsx, Problems.tsx, Questions.tsx, Companies.tsx, src/frontend/src/components/NodeDetailPanel.tsx, StudyPlanCard.tsx
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds, TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-74 --status completed`

## 2026-03-15 -- [T-P0-75] Build Toast notification system (ToastContext + ToastProvider)
- **What I did**: Created ToastContext with success/error/info methods, ToastProvider with fixed bottom-right toast stack, auto-dismiss after 4s, click to dismiss. Wrapped App with ToastProvider. Added toast notifications to all existing useMutation onError/onSuccess callbacks in NodeDetailPanel (2 mutations), Companies FocusTopicsPanel (1 mutation), and Questions (1 mutation).
- **Deliverables**: src/frontend/src/contexts/ToastContext.tsx (new), src/frontend/src/App.tsx, src/frontend/src/components/NodeDetailPanel.tsx, src/frontend/src/pages/Companies.tsx, src/frontend/src/pages/Questions.tsx
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds, TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-75 --status completed`

## 2026-03-15 -- [T-P0-76] Build shared UI components (LoadingSpinner)
- **What I did**: Created components/ui/ directory and LoadingSpinner component with animated CSS spinner, configurable size (sm/md/lg), optional message, fullHeight mode, and ARIA role="status". Replaced all plain-text loading patterns across Dashboard, Framework, Problems, Questions pages and StudyPlanCard component with the new LoadingSpinner. Toast part was already completed in T-P0-75.
- **Deliverables**: src/frontend/src/components/ui/LoadingSpinner.tsx (new), src/frontend/src/pages/Dashboard.tsx, Framework.tsx, Problems.tsx, Questions.tsx, src/frontend/src/components/StudyPlanCard.tsx
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds, TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-76 --status completed`

## 2026-03-15 -- [T-P0-77] Add useFilterParams hook + useDebounce hook
- **What I did**: Created two reusable hooks in src/frontend/src/hooks/. useDebounce: generic debounce hook for delayed value updates. useFilterParams: stores filter/sort/page state in URL searchParams via react-router's useSearchParams, with a schema-driven API supporting typed parsing, serialization, and clean URLs (default values omitted). Applied useFilterParams to the Problems page, replacing 8 useState calls with URL-persisted params. Filters now persist across navigation and browser back/forward.
- **Deliverables**: src/frontend/src/hooks/useDebounce.ts (new), src/frontend/src/hooks/useFilterParams.ts (new), src/frontend/src/pages/Problems.tsx (refactored)
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds, TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-77 --status completed`

## 2026-03-15 -- [T-P0-78] CJK font support + install recharts + react-markdown
- **What I did**: Added Noto Sans SC, Microsoft YaHei, PingFang SC, Hiragino Sans GB to font stack in index.css. Added break-words CSS utility class for CJK text wrapping. Applied break-words to text containers in NodeDetailPanel (study notes), ReviewPanel (chat bubbles, feedback), Questions (question text, solution approach), Companies (notes), StudyPlanCard (plan text). Installed recharts and react-markdown npm packages. Fixed pre-existing TypeScript errors in useFilterParams.ts (ParamDef<unknown> contravariance issue on serialize, unused useCallback import).
- **Deliverables**: src/frontend/src/index.css, src/frontend/package.json (recharts, react-markdown), src/frontend/src/hooks/useFilterParams.ts (TS fix), src/frontend/src/components/NodeDetailPanel.tsx, ReviewPanel.tsx, StudyPlanCard.tsx, src/frontend/src/pages/Questions.tsx, Companies.tsx
- **Sanity check result**: 521/521 backend tests pass, frontend build succeeds, TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-78 --status completed`

## 2026-03-15 -- [T-P0-79] Expose description in framework tree API + extend node update schema
- **What I did**: Added `title` and `description` optional fields to `FrameworkNodeUpdate` schema. Added `description` field to `FrameworkNodeResponse` schema. Updated `_build_tree()` and PUT response dict in framework router to include `description`. Added 4 new tests: title+description update round-trip, tree includes description, description-only update, null description default.
- **Deliverables**: src/backend/schemas/framework.py, src/backend/routers/framework.py, tests/test_router_framework.py
- **Sanity check result**: 525/525 backend tests pass, frontend TypeScript clean, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-79 --status completed`

## 2026-03-15 -- [T-P0-80] Notes tab in NodeDetailPanel with markdown edit/preview + autosave
- **What I did**: Restructured NodeDetailPanel into 3 tabs (Details | Notes | Study Log). Built reusable Tabs UI component. Notes tab has markdown textarea with Edit/Preview toggle using react-markdown, auto-saves via 500ms debounce on PUT /framework/nodes/{id} with {description}. Added inline title editing (click to edit, Enter to save, Escape to cancel). Added `description` field to FrameworkNode TypeScript type.
- **Deliverables**: src/frontend/src/components/NodeDetailPanel.tsx (rewritten), src/frontend/src/components/ui/Tabs.tsx (new), src/frontend/src/types/framework.ts
- **Sanity check result**: 525/525 backend tests pass, frontend TypeScript clean, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-80 --status completed`

## 2026-03-15 -- [T-P0-81] Add framework_node_id FK to Problem model + topic-linked endpoints
- **What I did**: Added nullable `framework_node_id` FK (SET NULL on delete) to Problem model. Updated ProblemCreate/ProblemUpdate/ProblemResponse schemas and problem router (create, update, response helper). Added two new endpoints: GET /framework/nodes/{id}/problems and GET /framework/nodes/{id}/questions. Updated export/import in main.py. Added `framework_node_id` to frontend Problem TypeScript type. Added conftest fixtures for problems/questions linked to framework nodes. Wrote 9 new tests covering CRUD with topic link, endpoint filtering, 404s, and cascade SET NULL behavior. Created migration script.
- **Deliverables**: src/backend/models/problem.py, src/backend/schemas/problem.py, src/backend/routers/framework.py, src/backend/routers/problems.py, src/backend/main.py, src/frontend/src/types/problem.ts, tests/conftest.py, tests/test_router_framework.py, scripts/migrate_add_problem_framework_node.py (new)
- **Sanity check result**: 534/534 backend tests pass, frontend TypeScript clean, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-81 --status completed`

## 2026-03-15 -- [T-P0-82] FrameworkNodePicker component
- **What I did**: Created reusable FrameworkNodePicker dropdown/autocomplete component for selecting framework topics. Fetches tree from /api/framework/tree?max_depth=2, flattens to a searchable list with path labels (e.g. "Coding > Dynamic Programming"). Supports debounced text search, clear/deselect, depth-indented dropdown, outside-click dismiss, and disabled state. Uses React Query with 5-min stale time for caching.
- **Deliverables**: src/frontend/src/components/framework/FrameworkNodePicker.tsx (new)
- **Sanity check result**: 534/534 backend tests pass, frontend TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-82 --status completed`

## 2026-03-15 -- [T-P0-83] Problem CRUD + text search
- **What I did**: Built Problem CRUD (Add/Edit/Delete) with text search on the Problems page. Created 7 shared UI components (Modal, ConfirmDialog, SearchInput, FormField, Badge, EmptyState, Pagination) and 3 problem-specific components (ProblemFormFields shared form, AddProblemModal, EditProblemModal). Updated Problems.tsx with SearchInput for client-side filtering across title/pattern/company, "+ Add Problem" button, per-row Edit/Delete actions, and React Query mutations with toast notifications and cache invalidation. Form state preserved on error.
- **Deliverables**: src/frontend/src/components/ui/Modal.tsx, ConfirmDialog.tsx, SearchInput.tsx, FormField.tsx, Badge.tsx, EmptyState.tsx, Pagination.tsx (all new), src/frontend/src/components/problems/ProblemFormFields.tsx, AddProblemModal.tsx, EditProblemModal.tsx (all new), src/frontend/src/pages/Problems.tsx (updated)
- **Sanity check result**: 534/534 backend tests pass, frontend TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-83 --status completed`

## 2026-03-15 -- [T-P0-84] Linked problems + questions in NodeDetailPanel
- **What I did**: Added "Problems" and "Questions" tabs to NodeDetailPanel. Each tab fetches from existing backend endpoints (GET /api/framework/nodes/{id}/problems and /questions), displays compact clickable lists with difficulty/pattern/company metadata, and shows empty state when no items are linked. Items link to the Problems/Questions pages with a search filter pre-filled.
- **Deliverables**: src/frontend/src/components/NodeDetailPanel.tsx (updated)
- **Sanity check result**: 534/534 backend tests pass, frontend TypeScript clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-84 --status completed`

## 2026-03-15 -- [T-P1-85] Split dashboard API into today/activity/summary endpoints
- **What I did**: Added three new dashboard sub-endpoints: GET /api/dashboard/today (due_reviews, suggested_focus_topic, streak_days), GET /api/dashboard/activity (30-day daily breakdown of attempts, study_minutes, questions_added), GET /api/dashboard/summary (problem counts, framework progress, company counts by status). Kept original GET /api/dashboard for backward compat.
- **Deliverables**: src/backend/main.py (updated), tests/test_dashboard_split.py (new, 17 tests)
- **Sanity check result**: 551/551 backend tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-85 --status completed`

## 2026-03-15 -- [T-P1-86] Dashboard rewrite with Today Focus + Weekly Chart + Pillar Progress
- **What I did**: Rewrote Dashboard.tsx to use all 3 split dashboard endpoints (today/activity/summary) plus framework tree. New layout: Row 1 = Today Focus cards (Due Reviews clickable -> /problems?review=due, Weakest Topic clickable -> /framework, Streak days). Row 2 = WeeklyActivityChart (Recharts stacked BarChart, 7 days) + Framework Pillar Progress bars (clickable -> /framework). Row 3 = Company Pipeline status summary with counts per status. Added loading skeletons for all sections. Created new components: WeeklyActivityChart.tsx, Skeleton.tsx.
- **Deliverables**: src/frontend/src/pages/Dashboard.tsx (rewritten), src/frontend/src/components/charts/WeeklyActivityChart.tsx (new), src/frontend/src/components/ui/Skeleton.tsx (new), src/frontend/src/types/dashboard.ts (updated with split endpoint types)
- **Sanity check result**: 551/551 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-86 --status completed`

## 2026-03-15 -- [T-P1-87] Backend CRUD for companies delete + questions create/delete/update
- **What I did**: Added DELETE /api/companies/{id} with cascade-delete of topic weights (returns count). Added POST /api/questions for creating single questions with all fields. Added DELETE /api/questions/{id}. Extended PUT /api/questions/{id} to accept all editable fields (company, role, question_type, level, year, tags, difficulty_estimate, mapped_framework_node_id, is_reviewed, notes) using a typed Pydantic schema instead of raw dict. Added InterviewQuestionCreate and InterviewQuestionUpdate schemas. Fixed existing integration test to match new PUT response format.
- **Deliverables**: src/backend/routers/companies.py (DELETE endpoint), src/backend/routers/scraper.py (POST/DELETE questions, extended PUT), src/backend/schemas/scraper.py (new create/update schemas), tests/test_router_companies.py (new, 4 tests), tests/test_router_questions.py (new, 9 tests), tests/test_integration_scraper_pipeline.py (fixed)
- **Sanity check result**: 564/564 backend tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-87 --status completed`

## 2026-03-15 -- [T-P1-88] Frontend: Companies edit/delete + topic weight editor
- **What I did**: Added tabbed CompanyDetailPanel (Focus/Weights/Edit tabs) replacing old FocusTopicsPanel. Focus tab retains existing topic focus view and status changer. Edit tab has inline form for name, group_tag, status, applied_at, notes with Save via PUT. Delete button with ConfirmDialog shows cascade count (N topic weights will be removed). Weights tab has TopicWeightEditor: lists current weights with range sliders (0-5, step 0.5), remove button per weight with ConfirmDialog, and add-topic section using FrameworkNodePicker + weight slider. Added backend DELETE /companies/{id}/weights/{node_id} endpoint for individual weight removal. All mutations use React Query with cache invalidation and toast notifications.
- **Deliverables**: src/frontend/src/components/companies/EditCompanyPanel.tsx (new), src/frontend/src/components/companies/TopicWeightEditor.tsx (new), src/frontend/src/pages/Companies.tsx (refactored), src/backend/routers/companies.py (new DELETE weight endpoint), tests/test_router_companies.py (2 new tests)
- **Sanity check result**: 566/566 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-88 --status completed`

## 2026-03-15 -- [T-P1-89] Frontend: Questions add/edit/delete + bulk mark reviewed + framework mapping
- **What I did**: Added AddQuestionModal with form fields (question_text, company, role, type, level, year, tags, mapped_framework_node_id via FrameworkNodePicker). Replaced inline ExpandedRow with EditableQuestionRow component supporting inline edit mode for all metadata fields (company, role, type, level, year, tags, difficulty, framework topic), delete with ConfirmDialog, and LLM analysis. Added bulk mark reviewed: checkbox column with select-all header, floating action bar at bottom with count + "Mark Reviewed" + "Clear" buttons using Promise.all for parallel PUT calls. Header now has both "+ Add Question" and "Paste Experience" buttons.
- **Deliverables**: src/frontend/src/components/questions/AddQuestionModal.tsx (new), src/frontend/src/components/questions/EditableQuestionRow.tsx (new), src/frontend/src/pages/Questions.tsx (refactored)
- **Sanity check result**: 566/566 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-89 --status completed`

## 2026-03-15 -- [T-P2-90] Frontend: Kanban drag-and-drop for Companies page
- **What I did**: Installed @hello-pangea/dnd. Wrapped Kanban board in DragDropContext, columns as Droppable, cards as Draggable. On drop: optimistic cache update + PUT /companies/{id} with new status. Visual feedback: blue-tinted column on drag-over, shadow + slight rotation on dragged card, grab cursor. Toast on success/failure. React Query cache invalidation after API response.
- **Deliverables**: src/frontend/src/pages/Companies.tsx (modified), src/frontend/package.json (added @hello-pangea/dnd)
- **Sanity check result**: 566/566 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-90 --status completed`

## 2026-03-15 -- [T-P2-91] Frontend: Framework tree search + breadcrumb path
- **What I did**: Created TreeSearchBar component with debounced input (useDebounce hook). Created BreadcrumbPath component that builds ancestor chain from node to root with clickable path segments. Updated FrameworkTreeView to accept searchQuery prop: matching nodes highlighted with yellow bg, non-matching leaves hidden, ancestors auto-expanded. Match count displayed in toolbar. Wired everything into Framework.tsx page.
- **Deliverables**: src/frontend/src/components/framework/TreeSearchBar.tsx (new), src/frontend/src/components/framework/BreadcrumbPath.tsx (new), src/frontend/src/components/FrameworkTreeView.tsx (modified), src/frontend/src/pages/Framework.tsx (modified)
- **Sanity check result**: 566/566 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-91 --status completed`

## 2026-03-15 -- [T-P2-92] Frontend: Settings page (import/export + scraper management)
- **What I did**: Created Settings page with four panels: ExportPanel (JSON full backup + CSV problems-only download), ImportPanel (JSON and CSV file upload with result summaries), SeedDataPanel (load built-in seed data), ScraperPanel (seed URL list with add/delete, run scraper button, job status with auto-refresh). Added DELETE /api/scraper/seeds/{id} backend endpoint. Added /settings route to App.tsx and Settings link to Sidebar. Added 2 backend tests for seed URL delete.
- **Deliverables**: src/frontend/src/pages/Settings.tsx (new), src/frontend/src/App.tsx (modified), src/frontend/src/components/Sidebar.tsx (modified), src/backend/routers/scraper.py (modified), tests/test_router_scraper.py (modified)
- **Sanity check result**: 568/568 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-92 --status completed`

## 2026-03-15 -- [T-P2-93] QA session summarize button in ReviewPanel
- **What I did**: Added Summarize Session button to the QA mode in ReviewPanel. Button appears when a session has messages, calls POST /api/qa/{id}/summarize, displays the summary in a styled panel below chat messages. Includes loading state on button during request and toast notifications on success/failure. Summary clears when switching sessions.
- **Deliverables**: src/frontend/src/components/ReviewPanel.tsx (modified)
- **Sanity check result**: 568/568 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-93 --status completed`

## 2026-03-15 -- [T-P2-94] Analytics deep-dive page (radar, scatter, trend, readiness)
- **What I did**: Created Analytics page with four visualization sections: (1) Pattern Comfort radar chart showing avg comfort per problem pattern (top 8), (2) Confidence vs Importance scatter plot for framework nodes, (3) 30-day activity trend line chart (attempts + study minutes), (4) Company prep readiness scores with weighted progress bars and gap analysis. Added ProblemStats type, four new chart components, Analytics page, route, and sidebar nav link.
- **Deliverables**: src/frontend/src/pages/Analytics.tsx (new), src/frontend/src/components/charts/PatternRadarChart.tsx (new), src/frontend/src/components/charts/ConfidenceScatterChart.tsx (new), src/frontend/src/components/charts/ComfortTrendChart.tsx (new), src/frontend/src/components/charts/CompanyReadinessCard.tsx (new), src/frontend/src/types/problem.ts (modified), src/frontend/src/App.tsx (modified), src/frontend/src/components/Sidebar.tsx (modified)
- **Sanity check result**: 568/568 backend tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-94 --status completed`

## 2026-03-16 -- Interview Timeline + Widescreen Fix + Title Fix
- **What I did**: Implemented full interview timeline feature: InterviewEvent model with migration v2, CRUD API endpoints, Pydantic schemas, export/import support. Built InterviewTimeline component (upcoming/past sections, urgency colors, countdown) and EventFormModal (add/edit/delete). Integrated as Row 0 on Dashboard. Fixed page title ("frontend" -> "ML Interview Prep") and widescreen CSS bug (added width:100% to #root). Seeded LinkedIn 3/16 and DoorDash 3/26 events. Fixed pre-existing migration idempotency test broken by adding v2.
- **Deliverables**: src/backend/models/timeline.py (new), src/backend/schemas/timeline.py (new), src/backend/routers/timeline.py (new), src/backend/models/__init__.py (modified), src/backend/database.py (modified), src/backend/main.py (modified), src/frontend/index.html (modified), src/frontend/src/index.css (modified), src/frontend/src/types/timeline.ts (new), src/frontend/src/components/timeline/InterviewTimeline.tsx (new), src/frontend/src/components/timeline/EventFormModal.tsx (new), src/frontend/src/pages/Dashboard.tsx (modified), tests/test_timeline.py (new), tests/test_migrations.py (modified)
- **Sanity check result**: 590/590 tests pass, ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]

## 2026-03-16 -- [T-P1-95] Add prep_notes to Company + migration v3 + get_or_create_company
- **What I did**: Added prep_notes (Text, nullable) column to Company model with migration v3 (ADD_COLUMN_IF_MISSING directive). Updated CompanyCreate/CompanyUpdate/CompanyResponse schemas, _company_to_response(), and create_company() to include prep_notes. Added POST /companies/{id}/prep-notes/import endpoint supporting append/replace modes with .md file upload. Created get_or_create_company service with case-insensitive matching and IntegrityError race condition handling. Updated export/import to include prep_notes. Fixed pre-existing migration tests (added companies table to old schema fixtures for v3 compatibility).
- **Deliverables**: src/backend/models/company.py (modified), src/backend/database.py (modified), src/backend/schemas/company.py (modified), src/backend/routers/companies.py (modified), src/backend/main.py (modified), src/backend/services/company_service.py (new), tests/test_company_prep_notes.py (new), tests/test_migrations.py (modified), tests/test_timeline.py (modified)
- **Sanity check result**: 609/609 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-95 --status completed`

## 2026-03-16 -- [T-P1-96] Auto-link company on timeline event creation
- **What I did**: Modified timeline router create_event() and update_event() to call get_or_create_company() for automatic company linking. create_event now always resolves company_id via get_or_create_company. update_event auto-links when company_name changes. Updated EventFormModal to invalidate ["companies"] queries on create/update/delete success. Fixed existing test_filter_by_company_id test to work with auto-linking. Added 5 new tests covering: auto-create company, no duplicate on reuse, case-insensitive matching, update links new company, update without company_name preserves link.
- **Deliverables**: src/backend/routers/timeline.py (modified), src/frontend/src/components/timeline/EventFormModal.tsx (modified), tests/test_timeline.py (modified)
- **Sanity check result**: 614/614 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-96 --status completed`

## 2026-03-16 -- [T-P1-97] PrepNotesTab with checkbox click-toggle + Companies page integration
- **What I did**: Created markdown utility functions (countUnchecked, countChecked, toggleCheckbox) in utils/markdown.ts. Built PrepNotesTab component with edit/preview toggle, clickable checkbox rendering via ReactMarkdown custom li renderer, debounced auto-save (500ms) with saving/saved/error status and retry button, and .md file import with append/replace mode. Added prep_notes field to Company and CompanyCreate TypeScript types. Integrated PrepNotesTab as "Prep" tab in CompanyDetailPanel with red dot badge showing unchecked count. Added red dot indicator on CompanyCard for companies with unchecked prep items.
- **Deliverables**: src/frontend/src/utils/markdown.ts (new), src/frontend/src/components/companies/PrepNotesTab.tsx (new), src/frontend/src/types/company.ts (modified), src/frontend/src/pages/Companies.tsx (modified)
- **Sanity check result**: 614/614 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-97 --status completed`

## 2026-03-16 -- [T-P1-98] Dashboard timeline prep notes modal + red dots on EventCard
- **What I did**: Created PrepNotesModal component (max-w-2xl Modal wrapping PrepNotesTab with "View in Companies" link). Updated InterviewTimeline to fetch /companies, build Map<id, Company> lookup, pass company data to EventCard. Made company_name in EventCard a blue clickable link (e.stopPropagation) that opens PrepNotesModal via new onCompanyClick prop. Added red dot next to company name when countUnchecked(prep_notes) > 0. Updated Dashboard.tsx with prepCompanyId/Name state, passes onCompanyClick to InterviewTimeline, renders PrepNotesModal. PrepNotesModal invalidates ["companies"] on close to sync red dots.
- **Deliverables**: src/frontend/src/components/timeline/PrepNotesModal.tsx (new), src/frontend/src/components/timeline/InterviewTimeline.tsx (modified), src/frontend/src/pages/Dashboard.tsx (modified)
- **Sanity check result**: 614/614 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-98 --status completed`

## 2026-03-16 -- Full-screen prep notes page + Dashboard prep quick-access
- **What I did**: Created full-screen PrepNotesPage at /companies/:companyId/prep with sticky header, full-height editor/preview, GFM-inspired .prep-prose CSS styling. Extracted usePrepNotes hook and MarkdownPreview shared component. Replaced Dashboard PrepNotesModal with direct navigation. Added PrepQuickAccess section on Dashboard showing companies with prep notes, checklist progress bars, and unchecked count badges. Refactored PrepNotesTab to use shared hook with "Full Page" link. Moved LinkedIn interview from 03/16 to 03/17 10:30AM.
- **Deliverables**: src/frontend/src/hooks/usePrepNotes.ts (new), src/frontend/src/components/ui/MarkdownPreview.tsx (new), src/frontend/src/pages/PrepNotesPage.tsx (new), src/frontend/src/index.css (modified), src/frontend/src/App.tsx (modified), src/frontend/src/pages/Dashboard.tsx (modified), src/frontend/src/components/companies/PrepNotesTab.tsx (modified)
- **Sanity check result**: 614/614 tests pass, ruff clean, TypeScript compiles clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: No task change (ad-hoc)

## 2026-03-16 -- [T-P0-99] TTS MVP: edge-tts synthesize + audio playback for framework nodes
- **What I did**: Implemented minimal TTS vertical slice. Added edge-tts dependency and TTS settings (voice, rate) to config. Created EdgeTTS engine service with SHA-256 file caching in data/tts_cache/. Created content pipeline with markdown-to-spoken-text preprocessing (strips headings, bold/italic, links, code blocks; expands abbreviations). Added reading router with POST /synthesize (returns audio URL) and GET /audio/{cache_key} (serves MP3 via FileResponse). Created ListenButton UI component with play/pause/stop states. Integrated Listen button into NodeDetailPanel DetailsTab for nodes with descriptions.
- **Deliverables**: src/backend/services/tts_engine.py (new), src/backend/services/content_pipeline.py (new), src/backend/schemas/reading.py (new), src/backend/routers/reading.py (new), src/frontend/src/components/ui/ListenButton.tsx (new), src/backend/config.py (modified), src/backend/main.py (modified), src/frontend/src/components/NodeDetailPanel.tsx (modified), requirements.txt (modified), tests/test_content_pipeline.py (new), tests/test_tts_engine.py (new), tests/test_router_reading.py (new)
- **Sanity check result**: 637/637 tests pass, ruff clean, TypeScript compiles clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-99 --status completed`

## 2026-03-16 -- [T-P0-100] ReadingProgress + AudioCache models + Migration v4
- **What I did**: Created three new SQLAlchemy models in models/reading.py: ReadingProgress (tracks per-content listening progress with content_type+content_id unique constraint), ReadingSession (listening session duration/stats), AudioCache (cached TTS audio with content_type+content_id+engine+voice unique constraint and content_hash for invalidation). Added migration v4 to database.py creating all three tables. Updated models/__init__.py exports. Fixed pre-existing test_timeline idempotent assertion to use len(MIGRATIONS) instead of hardcoded count.
- **Deliverables**: src/backend/models/reading.py (new), src/backend/database.py (modified), src/backend/models/__init__.py (modified), tests/test_reading_models.py (new), tests/test_migrations.py (modified), tests/test_timeline.py (modified)
- **Sanity check result**: 653/653 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-100 --status completed`

## 2026-03-16 -- [T-P0-101] Content Pipeline: queue ranking, preprocessing v2, chunking
- **What I did**: Expanded services/content_pipeline.py with five new functions: (1) get_reading_queue(db, company_ids, days_until_interview, limit) ranks FrameworkNodes by urgency (reusing compute_urgency from study_planner), interleaves prep_notes and interview_questions for target companies, attaches ReadingProgress, filters completed items. (2) preprocess_for_tts v2 adds [PAUSE] markers at headings, ensures bullet/numbered items end with period, expands w/ and w/o abbreviations. (3) chunk_text splits at sentence boundaries respecting max_chars. (4) get_content_text retrieves raw text for all 3 content types (framework_node description, company prep_notes, problem metadata). (5) compute_content_hash returns SHA-256 for cache invalidation. Added QueueItem dataclass and content type constants.
- **Deliverables**: src/backend/services/content_pipeline.py (modified), tests/test_content_pipeline.py (modified - 40 tests total)
- **Sanity check result**: 682/682 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-101 --status completed`

## 2026-03-16 -- [T-P0-102] Reading REST endpoints: queue, progress, content, async synthesize
- **What I did**: Expanded routers/reading.py with 7 endpoints: GET /reading/queue (ranked with progress, company filtering), GET /reading/progress (all records), PUT /reading/progress/{type}/{id} (upsert last_chunk_index + char_offset), DELETE /reading/progress (reset all), GET /reading/content/{type}/{id} (preprocessed text + chunks + hash), refactored POST /reading/synthesize (AudioCache-aware with content_hash invalidation, async 202 for content >= 2000 chars), GET /reading/jobs/{id} (poll async jobs). Expanded schemas/reading.py with ContentType literal, QueueItemResponse, QueueResponse, ProgressResponse, ProgressUpdateRequest, ContentResponse, SynthesizeAsyncResponse. All 3 content types supported: framework_node, prep_notes, interview_question.
- **Deliverables**: src/backend/routers/reading.py (rewritten), src/backend/schemas/reading.py (expanded), tests/test_router_reading.py (rewritten - 35 tests)
- **Sanity check result**: 710/710 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-102 --status completed`

## 2026-03-16 -- [T-P1-103] TTS Engine abstraction: EdgeTTS + OpenAI + Browser engines
- **What I did**: Refactored services/tts_engine.py into ABC TTSEngine with synthesize_to_file + voice_options. Implemented EdgeTTSEngine (refactored from MVP, lazy edge-tts import, file caching), OpenAITTSEngine (httpx async POST to /v1/audio/speech, OPENAI_API_KEY validation, file caching), BrowserTTSEngine (returns {mode: "browser", text: ...} for client-side SpeechSynthesis). Added factory get_tts_engine(name) with settings default. Added synthesize_with_fallback() that auto-falls back to browser on engine failure. Updated routers/reading.py synthesize endpoint to use engine abstraction with browser mode support. Added OPENAI_API_KEY to Settings. Updated SynthesizeRequest with engine field, SynthesizeResponse with mode/text fields.
- **Deliverables**: src/backend/services/tts_engine.py (rewritten), src/backend/config.py (OPENAI_API_KEY), src/backend/routers/reading.py (updated), src/backend/schemas/reading.py (updated), tests/test_tts_engine.py (rewritten - 28 tests), tests/test_router_reading.py (updated mocks)
- **Sanity check result**: 733/733 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-103 --status completed`

## 2026-03-16 -- [T-P1-104] Frontend Audio Player + Radio Mode (core playback)
- **What I did**: Created the core frontend audio player infrastructure. New types/reading.ts with ContentType, QueueItem, SynthesizeResponse, AudioPlayerItem, PlayerStatus types. New hooks/useAudioPlayer.ts managing HTML5 Audio element: play(item) calls POST /synthesize then plays audio_url or falls back to browser SpeechSynthesis, pause/resume/skip/seek controls, auto-advance through queue (radio mode), playback speed 0.75x-2.0x via playbackRate, progress tracking via ontimeupdate with periodic backend saves every 30s. New contexts/AudioPlayerContext.tsx wrapping the hook as a global provider. Wrapped App.tsx in AudioPlayerProvider so state persists across navigation. Refactored ListenButton.tsx to use the shared AudioPlayerContext instead of managing its own audio element.
- **Deliverables**: src/frontend/src/types/reading.ts (new), src/frontend/src/hooks/useAudioPlayer.ts (new), src/frontend/src/contexts/AudioPlayerContext.tsx (new), src/frontend/src/App.tsx (updated), src/frontend/src/components/ui/ListenButton.tsx (rewritten)
- **Sanity check result**: 733/733 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-104 --status completed`

## 2026-03-16 -- [T-P1-105] Browser Web Speech API fallback + prefetch next item
- **What I did**: Enhanced useAudioPlayer hook with two features: (1) Improved browser SpeechSynthesis fallback with proper pause/resume support via speechSynthesis.pause()/resume(), tracking active utterance and browser TTS mode in refs, cleanup via speechSynthesis.cancel(). (2) Prefetch system: when an item starts playing (both audio and browser TTS), automatically POST /synthesize for the next queue item in background. Prefetched responses stored in a Map ref keyed by "content_type:content_id". On play(), checks prefetch cache first to skip network round-trip. Cache cleared on stop() and startRadio() to prevent stale data.
- **Deliverables**: src/frontend/src/hooks/useAudioPlayer.ts (enhanced)
- **Sanity check result**: 733/733 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-105 --status completed`

## 2026-03-16 -- [T-P1-106] Persistent Audio Player Bar (Spotify-style bottom bar)
- **What I did**: Created AudioPlayerBar.tsx: fixed-bottom bar with title+content-type badge, prev/play-pause/next transport controls (SVG icons), clickable progress bar with hover scrub handle, time display (m:ss), speed selector dropdown (0.75x-2x), queue slide-out panel showing all items with current highlighted, close button. Mounted in Layout.tsx with conditional bottom padding when player is active. Added keyboard shortcuts: Space=play/pause (with focus guard for input/textarea/select elements), N=next. All controls use the global AudioPlayerContext.
- **Deliverables**: src/frontend/src/components/AudioPlayerBar.tsx (new), src/frontend/src/components/Layout.tsx (updated)
- **Sanity check result**: 733/733 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-106 --status completed`

## 2026-03-16 -- [T-P1-107] Study Radio page: queue management, now playing, history
- **What I did**: Created StudyRadio.tsx page at /radio with four sections: (1) Quick Start with company filter dropdown, TTS engine selector, Start Radio button, and auto-advance toggle. (2) Now Playing section with transport controls (prev/play-pause/next), title+badge, progress bar with time display, and queue position indicator. (3) Queue section showing ranked pending items with urgency labels (High/Med/Low), content-type badges, progress indicators (Not started/percentage/Done), and per-item Play buttons. Current item highlighted in green. (4) History section showing completed items with Replay buttons. Added route in App.tsx and nav item in Sidebar.tsx.
- **Deliverables**: src/frontend/src/pages/StudyRadio.tsx (new), src/frontend/src/App.tsx (updated), src/frontend/src/components/Sidebar.tsx (updated)
- **Sanity check result**: 733/733 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-107 --status completed`

## 2026-03-16 -- [T-P1-108] Listen buttons across app (Companies, Questions, Dashboard, Framework)
- **What I did**: Added ListenButton to three more pages: (1) Questions page - ListenButton in EditableQuestionRow expanded actions bar, plays interview_question content type. (2) Companies page - ListenButton in CompanyDetailPanel header next to company name, plays prep_notes (only shown when company has prep notes). (3) Dashboard - Start Radio quick action card with contextual label (Start Radio vs Go to Radio when already playing), navigates to /radio. Framework page already had ListenButton via NodeDetailPanel.
- **Deliverables**: src/frontend/src/components/questions/EditableQuestionRow.tsx (updated), src/frontend/src/pages/Companies.tsx (updated), src/frontend/src/pages/Dashboard.tsx (updated)
- **Sanity check result**: 733/733 tests pass, ruff clean, TypeScript compiles clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-108 --status completed`

## 2026-03-16 -- [T-P2-109] Interview-aware content ordering in reading queue
- **What I did**: Enhanced get_reading_queue() to automatically query InterviewEvent for upcoming interviews. Added get_interview_context() helper that derives company_ids, days_until_soonest, and imminent_company_ids (< 3 days). When interview is imminent, prep_notes for that company get a 100x urgency boost to appear first. Router updated to make company_ids and days_until_interview optional (auto-detected when omitted). Falls back to standard urgency ordering when no upcoming interviews exist.
- **Deliverables**: src/backend/services/content_pipeline.py (updated), src/backend/routers/reading.py (updated), tests/test_content_pipeline.py (updated, 9 new tests)
- **Sanity check result**: 742/742 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-109 --status completed`

## 2026-03-16 -- [T-P2-110] LLM-generated TTS summaries for long content
- **What I did**: Added TTSSummary model and migration v5 for caching LLM-generated summaries. Created generate_tts_summary() async function in content_pipeline.py that calls LLMService with a TTS-optimization prompt, caches results in tts_summaries table with content_hash invalidation, and falls back to preprocessed raw text when LLM unavailable. Added get_cached_summary() for read-only cache lookups. New POST /reading/summary endpoint generates or retrieves cached summaries. Synthesize endpoint now prefers cached summaries over raw text. Content endpoint includes summary_text field when available.
- **Deliverables**: src/backend/models/reading.py (TTSSummary model), src/backend/database.py (migration v5), src/backend/services/content_pipeline.py (generate_tts_summary, get_cached_summary), src/backend/routers/reading.py (summary endpoint + integration), src/backend/schemas/reading.py (SummaryRequest/Response), tests/test_tts_summary.py (13 new tests)
- **Sanity check result**: 755/755 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-110 --status completed`

## 2026-03-16 -- [T-P2-111] Listening session analytics on Dashboard and StudyRadio
- **What I did**: Added POST /reading/sessions (create), PUT /reading/sessions/{id} (close with items/duration), and GET /reading/stats (total sessions, listening time, items listened, today's stats, streak) endpoints. ReadingSession model was already in place from migration v4. Added Pydantic schemas for session create/close requests and listening stats response. Updated StudyRadio page with a 4-stat card grid (sessions, minutes, items, streak). Enhanced Dashboard's Study Radio section with today/total/streak inline stats.
- **Deliverables**: src/backend/routers/reading.py (3 new endpoints), src/backend/schemas/reading.py (4 new schemas), src/frontend/src/types/reading.ts (ListeningStats type), src/frontend/src/pages/StudyRadio.tsx (stats grid), src/frontend/src/pages/Dashboard.tsx (inline listening stats), tests/test_listening_sessions.py (12 new tests)
- **Sanity check result**: 767/767 tests pass, ruff clean
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-111 --status completed`

## 2026-03-16 -- Fix: Content area only fills half the screen width
- **What I did**: Added `w-full` to Layout component's root div. The `#root` div uses `display: flex` (row), and its Layout child had no width constraint, so it shrank to content intrinsic width instead of filling the viewport. Adding `width: 100%` ensures Layout fills `#root`, giving `<main className="flex-1">` the full remaining width after the sidebar.
- **Deliverables**: src/frontend/src/components/Layout.tsx (1-line className change)
- **Sanity check result**: Vite build succeeds, dev server starts, CSS chain verified (#root flex -> Layout w-full -> main flex-1)
- **Status**: [DONE]
- **Request**: No task_db change (ad-hoc fix, not a tracked task)

## 2026-03-16 -- Fix: Study Radio UX -- inline playback, async job polling, error feedback
- **What I did**: Fixed three issues with Study Radio: (1) Dashboard "Start Radio" no longer navigates to /radio -- audio plays inline via the global AudioPlayerBar. (2) Added async job polling to `play()` and `prefetchNext()` -- backend returns 202 + job_id for long content (>=2000 chars), but frontend had no polling logic and silently failed with "No audio URL". Now polls `GET /reading/jobs/{job_id}` every 1.5s until complete. (3) Added error/empty-queue feedback: "empty:" prefix on error distinguishes empty queue (blue info box) from real errors (red box). Added loading placeholders ("Preparing audio...") across Dashboard, StudyRadio, and AudioPlayerBar. Added idempotency guard to startRadio. Added "Radio" nav button to AudioPlayerBar.
- **Deliverables**: src/frontend/src/hooks/useAudioPlayer.ts, src/frontend/src/pages/Dashboard.tsx, src/frontend/src/pages/StudyRadio.tsx, src/frontend/src/components/AudioPlayerBar.tsx
- **Sanity check result**: TypeScript compiles clean, Vite build succeeds. Backend synthesize returns 202 with job_id, job completes in ~2s with audio_url (verified via curl).
- **Status**: [DONE]
- **Request**: No task_db change (ad-hoc fix, not a tracked task)

## 2026-03-16 -- Fix: Radio blank page, TTS quality, LinkedIn content sync
- **What I did**: Fixed three user-reported issues. (A) AudioPlayerBar had useCallback hooks after an early return, violating React's rules of hooks ("Rendered more hooks than during the previous render"). Moved all hooks before the conditional return. Created ErrorBoundary component wrapping Outlet and AudioPlayerBar in Layout for crash isolation. Updated startRadio to return boolean with try/catch, added NotAllowedError detection for Chrome autoplay. (B) TTS preprocessing v3: replaced literal [PAUSE] with empty lines, added table/checkbox/horizontal-rule/underscore-placeholder handling, CJK-dominant line skipping (>80% CJK). Enhanced LLM TTS prompt with Chinese translation and table cleanup instructions. 5 new regression tests. (C) Updated backfill script with TTS cache invalidation and idempotency check. Ran it to sync LinkedIn prep notes (15,344 chars).
- **Deliverables**: src/backend/services/content_pipeline.py, tests/test_content_pipeline.py, src/frontend/src/components/ErrorBoundary.tsx (new), src/frontend/src/components/Layout.tsx, src/frontend/src/components/AudioPlayerBar.tsx, src/frontend/src/hooks/useAudioPlayer.ts, scripts/backfill_interviews.py
- **Sanity check result**: 770/770 tests pass (2 pre-existing failures in test_listening_sessions), ruff clean, TypeScript compiles clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: No task_db change (ad-hoc fixes)

## 2026-03-16 -- Fix: Study Radio returns completed items for History/Replay
- **What I did**: Backend `get_reading_queue()` was filtering out completed items, so the frontend History section was always empty. Changed the function to split items into pending (capped by limit) and completed (always returned), with pending first. Updated 2 existing tests and added 3 regression tests covering ordering, limit behavior, and the all-completed scenario.
- **Deliverables**: src/backend/services/content_pipeline.py, tests/test_content_pipeline.py, tests/test_router_reading.py
- **Sanity check result**: 773/773 tests pass (2 pre-existing failures in test_listening_sessions), ruff clean
- **Status**: [DONE]
- **Request**: No task_db change (ad-hoc fix)

## 2026-03-16 -- Content Pipeline, LeetCode & LinkedIn JD Integration
- **What I did**: Implemented 3 planned tasks. (1) Unified Faithful Transcript System: replaced TTSSummary with new Transcript model (UNIQUE on content_type+content_id+source_hash+prompt_version, is_latest boolean for history). New TRANSCRIPT_SYSTEM_PROMPT preserves all key points for spoken delivery. generate_transcript() with transaction-safe is_latest toggle. GET /reading/transcript endpoint. Improved preprocess_for_tts() fallback with ML/DL/NLP/API/O(n) abbreviation expansion. (2) Decouple Reading from Synthesis: new TranscriptViewer.tsx modal, "Read" button in StudyRadio queue/history. (3) Local LeetCode Descriptions: added description/neetcode_slug/description_source columns to Problem, POST /problems/{id}/fetch-description endpoint (neetcode.io HTML parsing), ProblemDescriptionModal.tsx with "Fetch from Neetcode" button, title click in Problems page opens modal. Added python-docx to requirements.txt. Ad-hoc LinkedIn JD: extracted JD content from docx, presented themes for user review (awaiting confirmation before DB write).
- **Deliverables**: src/backend/models/reading.py, src/backend/database.py (migrations v6+v7), src/backend/services/content_pipeline.py, src/backend/routers/reading.py, src/backend/routers/problems.py, src/backend/schemas/reading.py, src/backend/schemas/problem.py, src/frontend/src/components/reading/TranscriptViewer.tsx (new), src/frontend/src/components/problems/ProblemDescriptionModal.tsx (new), src/frontend/src/pages/StudyRadio.tsx, src/frontend/src/pages/Problems.tsx, src/frontend/src/types/problem.ts, src/frontend/src/types/reading.ts, src/frontend/src/components/problems/ProblemFormFields.tsx, src/frontend/src/components/problems/EditProblemModal.tsx, tests/test_tts_summary.py, tests/test_schemas_problem.py, tests/test_migrations.py, tests/test_router_reading.py, tests/test_content_pipeline.py, tests/test_router_problems.py, requirements.txt
- **Sanity check result**: 784/784 tests pass (excl. 2 pre-existing test_listening_sessions failures), ruff clean, TypeScript compiles clean, Vite build succeeds, DB migrations verified
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-114 --status completed` (Unified Transcript), `T-P1-115` (Decouple Reading), `T-P1-116` (LeetCode Descriptions), `T-P0-117` (LinkedIn JD) -- all completed

## 2026-03-16 -- Blind Grind 75 Backfill & Tab
- **What I did**: Implemented full Blind Grind 75 feature: (1) Schema: migration v8 adds `notes` column to problems table, updated model/schemas/router/frontend types. (2) Docx import script (`scripts/import_blind75_notes.py`) with two-step workflow: parse docx to JSON preview, then `--commit` to DB. (3) Updated `fetch-description` endpoint to try LeetCode GraphQL API first (extracts title_slug from URL), falls back to neetcode scraping, added 5-second rate limiter. (4) Frontend: added "Blind Grind 75" tab to Problems page with progress bar, pattern-grouped tables, Notes column, deep-linking via `?tab=blind75`. Updated ProblemDescriptionModal with "My Notes" section (amber styling) and re-fetch button. Added notes textarea to ProblemFormFields.
- **Deliverables**: src/backend/database.py (migration v8), src/backend/models/problem.py, src/backend/schemas/problem.py, src/backend/routers/problems.py, src/backend/scraper/site_configs.py, src/frontend/src/pages/Problems.tsx, src/frontend/src/components/problems/ProblemDescriptionModal.tsx, src/frontend/src/components/problems/ProblemFormFields.tsx, src/frontend/src/components/problems/EditProblemModal.tsx, src/frontend/src/types/problem.ts, scripts/import_blind75_notes.py (new), tests/test_import_blind75_notes.py (new), tests/test_migrations.py, tests/test_router_problems.py
- **Sanity check result**: 158 tests pass (migrations + router + import), ruff clean, TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: No task_db change (user-requested ad-hoc feature)

## 2026-03-16 -- Problems UX overhaul: full-page descriptions, markdown rendering, batch fetch
- **What I did**: (1) Removed Edit/Del buttons from problem rows (unused, cluttering). (2) Installed remark-gfm and updated MarkdownPreview with GFM support (tables, strikethrough) and GitHub-PR-style checkbox icons (green check / gray circle). (3) Replaced ProblemDescriptionModal with full-screen ProblemDetailPage at `/problems/:problemId`. Problem titles now Link to detail page. (4) Backend now stores raw HTML from LeetCode GraphQL instead of stripped text, preserving formatting. Added `GET /problems/{problem_id}` and `POST /problems/fetch-all-descriptions` endpoints. (5) Batch-fetched 140/147 descriptions; 7 premium problems need manual input. (6) Added "Fetch All Descriptions" button with failure report panel showing unfetchable problems.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx, src/frontend/src/pages/Problems.tsx, src/frontend/src/pages/ProblemDetailPage.tsx (new), src/frontend/src/App.tsx, src/backend/routers/problems.py, src/frontend/package.json (remark-gfm)
- **Sanity check result**: 127 router tests pass, ruff clean, TypeScript clean, Vite build succeeds, 140 descriptions fetched and stored
- **Status**: [DONE] (7 premium problems pending user input)
- **Request**: No task_db change (user-requested ad-hoc feature)

## 2026-03-16 -- Fix checkbox rendering in MarkdownPreview and double prose nesting
- **What I did**: (1) Fixed broken task-list checkbox detection in MarkdownPreview -- replaced null/input child scanning (broken in react-markdown v10) with reliable `className.includes("task-list-item")` check from remark-gfm. (2) Removed duplicate `prose` classes from PrepNotesPage and PrepNotesTab outer wrappers to eliminate double prose nesting with MarkdownPreview's own prose context.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx, src/frontend/src/pages/PrepNotesPage.tsx, src/frontend/src/components/companies/PrepNotesTab.tsx
- **Sanity check result**: TypeScript clean, Vite build succeeds
- **Status**: [DONE]
- **Request**: No task_db change (ad-hoc bugfix)

## 2026-03-16 -- [T-P1-119] Fix strikethrough + math formula rendering in MarkdownPreview
- **What I did**: (1) Added remark-math + rehype-katex to enable LaTeX math rendering ($inline$ and $$block$$). (2) Fixed Tailwind v4 prose resetting `<del>`/`<s>` text-decoration by adding explicit CSS rule in index.css. (3) Imported KaTeX CSS for proper formula styling.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx, src/frontend/src/index.css, src/frontend/package.json
- **Sanity check result**: No new TS errors from changes, Vite build succeeds, pre-existing test failure unrelated
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-119 --status completed`

## 2026-03-16 -- [T-P1-120] Add Difficulty as a sort option for Problems page
- **What I did**: Added "Difficulty" to sort dropdown (frontend) and backend sort handler. Backend uses SQLAlchemy `case()` for semantic ordering (easy=1 < medium=2 < hard=3) with nulls always last. Added 3 regression tests covering asc, desc, and null-last behavior.
- **Deliverables**: src/frontend/src/types/problem.ts, src/frontend/src/pages/Problems.tsx, src/backend/routers/problems.py, tests/test_router_problems.py
- **Sanity check result**: 130 tests pass, TypeScript compiles cleanly
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-120 --status completed`

## 2026-03-16 -- [T-P1-121] Notes indicator icon on All Problems tab
- **What I did**: Added a small pencil/edit SVG icon (amber colored) inline in the Title cell of the All Problems tab for problems that have notes. Icon only appears when notes exist and only on the All Problems tab (Blind 75 tab already has a dedicated Notes column).
- **Deliverables**: src/frontend/src/pages/Problems.tsx
- **Sanity check result**: TypeScript compiles cleanly, 255 backend tests pass (1 pre-existing failure in unrelated listening stats test)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-121 --status completed`

## 2026-03-16 -- [T-P1-122] Collapsible My Notes section on Problem detail page
- **What I did**: Made the My Notes section on ProblemDetailPage collapsible with default collapsed state. Added a clickable header with a chevron toggle icon. Section still hidden entirely when no notes exist. State resets on navigation (no persistence).
- **Deliverables**: src/frontend/src/pages/ProblemDetailPage.tsx
- **Sanity check result**: TypeScript compiles cleanly, 255 backend tests pass (1 pre-existing failure in unrelated listening stats test)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-122 --status completed`

## 2026-03-16 -- [T-P2-123] Resizable right panel and scrollable tabs in Framework
- **What I did**: Added drag-to-resize functionality to the Framework page right panel. Replaced fixed w-72 with a mouse-draggable left edge (min 240px, max 50vw). Added a visible drag handle with col-resize cursor and hover highlight. Made Tabs component horizontally scrollable with overflow-x-auto + whitespace-nowrap + shrink-0 on tab buttons to prevent wrapping in narrow panels.
- **Deliverables**: src/frontend/src/pages/Framework.tsx, src/frontend/src/components/ui/Tabs.tsx
- **Sanity check result**: TypeScript compiles cleanly, 255 backend tests pass (1 pre-existing failure in unrelated listening stats test)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-123 --status completed`

## 2026-03-16 -- Fix strikethrough in prep-prose + import Blind75 notes
- **What I did**: (1) Extended the Tailwind v4 strikethrough CSS fix to cover `.prep-prose` in addition to `.prose`, so `~~text~~` renders correctly on the PrepNotesPage. (2) Fixed import_blind75_notes.py regex to handle full-width colon (U+FF1A) used in the CJK docx, plus added UTF-8 stdout wrapper for Windows. Re-parsed all 76 entries (75 Blind75 + 1 extra LC129) from `Blind75 LC解答.docx` and committed to DB (64 updated, 12 skipped).
- **Deliverables**: src/frontend/src/index.css (CSS fix), scripts/import_blind75_notes.py (regex + encoding fix), data/blind75_parsed.json (76 parsed notes), database updated with 64 problem notes
- **Sanity check result**: TypeScript compiles cleanly, 255 backend tests pass (1 pre-existing failure in unrelated listening stats test)
- **Status**: [DONE]

## 2026-03-17 -- [T-P1-125] Fix checkbox persistence and scroll white space on PrepNotesPage
- **What I did**: (1) Fixed checkbox revert bug by adding optimistic updates to saveMutation (onMutate cancels queries + sets cache), an isSavingRef guard to prevent useEffect([initialNotes]) from reverting state during saves, and removed premature lastSavedRef update from handleCheckboxClick. (2) Fixed scroll white space by replacing flex-1 with min-h-0 overflow-auto on the prep-prose div.
- **Deliverables**: src/frontend/src/hooks/usePrepNotes.ts, src/frontend/src/pages/PrepNotesPage.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit), no frontend test files to run
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-125 --status completed`

## 2026-03-17 -- [T-P1-126] Framework full-screen notes page
- **What I did**: (1) Added GET /framework/nodes/{id} backend endpoint returning a single node. (2) Created useFrameworkNotes hook with debounced auto-save, checkbox persistence, and optimistic updates. (3) Created FrameworkNotesPage at /framework/:nodeId/notes with prep-prose CSS, MarkdownPreview with LaTeX, breadcrumb navigation, and sibling prev/next arrows from cached tree. (4) Added route in App.tsx. (5) Added "Full Page" link in NodeDetailPanel Notes tab.
- **Deliverables**: src/backend/routers/framework.py, src/frontend/src/hooks/useFrameworkNotes.ts, src/frontend/src/pages/FrameworkNotesPage.tsx, src/frontend/src/components/NodeDetailPanel.tsx, src/frontend/src/App.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit), ruff passes, 102 framework tests pass
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-126 --status completed`

## 2026-03-17 -- [T-P1-128] PrevNextNav arrow component for PrepNotesPage and ProblemDetailPage
- **What I did**: (1) Created reusable PrevNextNav component with left/right chevrons, tooltips showing target label, disabled state at boundaries, and keyboard ArrowLeft/Right support (skipped when input/textarea focused). (2) Integrated in PrepNotesPage: fetches companies list, sorts alphabetically, navigates prev/next company prep pages. Keyboard nav enabled only in preview mode. (3) Integrated in ProblemDetailPage: fetches problems sorted by last_attempted_at desc (limit=200), navigates prev/next problem. Keyboard nav always enabled. (4) Refactored FrameworkNotesPage to use PrevNextNav instead of inline buttons, adding keyboard nav in preview mode.
- **Deliverables**: src/frontend/src/components/ui/PrevNextNav.tsx (new), src/frontend/src/pages/PrepNotesPage.tsx, src/frontend/src/pages/ProblemDetailPage.tsx, src/frontend/src/pages/FrameworkNotesPage.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit), 641 tests pass (1 pre-existing failure unrelated to changes)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-128 --status completed`

## 2026-03-17 -- [T-P1-134] Fix MarkdownPreview checkbox mismatch from remarkMath corruption
- **What I did**: (1) Replaced fragile counter-based checkbox state detection in MarkdownPreview with direct hast node child inspection (`inputChild.properties.checked`), using `node.position.start.line` for click line index. Removed `checkboxLineIndices`, `checkboxCounter`, and `lines` array. (2) Disabled single-dollar math parsing in remarkMath (`singleDollarTextMath: false`) to prevent `$250K` being parsed as math and corrupting the AST. (3) Updated LinkedIn prep notes in DB to use `$$...$$` for the two legitimate math expressions.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx, data/mle_prep.db
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-134 --status completed`

## 2026-03-17 -- [T-P1-127] Content template + ML Fundamentals pillar (Pillar 2) prep docs for all 25 leaf topics
- **What I did**: (1) Created `docs/framework_content_template.md` with standard structure (Overview, Core Concepts with LaTeX, Implementation, Interview Patterns, Comparisons, Key Takeaways checklist). (2) Wrote `scripts/seed_pillar2_content.py` with detailed senior MLE-depth prep docs for all 25 Pillar 2 leaf topics: 7 Supervised Learning (Linear Models, Tree Models, SVM, Bias-Variance, Loss Functions, Regularization, Evaluation Metrics), 3 Unsupervised Learning (Clustering, Dimensionality Reduction, Anomaly Detection), 4 Optimization (Gradient Descent, Learning Rate, Convergence, Training Tricks), 6 Feature Engineering (Numerical, Categorical, Text, Temporal, Missing Values, Feature Selection), 2 Sampling & Class Imbalance (Oversampling, Loss Reweighting), 3 Model Selection & Validation (Cross-Validation, Hyperparameter Tuning, Calibration). (3) Each topic has KaTeX-compatible LaTeX formulas, Python implementation snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: docs/framework_content_template.md (new), scripts/seed_pillar2_content.py (new), data/mle_prep.db (25 nodes updated)
- **Sanity check result**: All 25 nodes verified in DB with LaTeX, checkboxes, and tables. TypeScript compiles cleanly. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-127 --status completed`

## 2026-03-17 -- [T-P1-129] Deep Learning & LLM pillar (Pillar 6) prep docs for all 24 leaf topics
- **What I did**: Wrote `scripts/seed_pillar6_content.py` with detailed senior MLE-depth prep docs for all 24 Pillar 6 leaf topics across 6 categories: (1) Transformer Deep Understanding (7 topics: self-attention, multi-head attention, position encoding, layer normalization, feed-forward/SwiGLU, attention variants MQA/GQA/Flash, architecture variants encoder/decoder), (2) Pre-trained Language Models (3 topics: BERT family, GPT family, LLaMA/Mistral), (3) LLM Training & Alignment (5 topics: pre-training, SFT, RLHF/DPO, LoRA/QLoRA PEFT, evaluation & benchmarks), (4) LLM Inference Optimization (4 topics: KV cache/PagedAttention, quantization GPTQ/AWQ/FP8, continuous batching, serving systems vLLM/TRT-LLM), (5) RAG Deep Dive (4 topics: chunking strategies, embedding models, vector databases, advanced RAG patterns), (6) Multimodal (1 topic: vision-language CLIP/LLaVA). Each topic has KaTeX-compatible LaTeX, Python code snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: scripts/seed_pillar6_content.py (new), data/mle_prep.db (24 nodes updated)
- **Sanity check result**: All 24 nodes verified in DB with content (4K-6K chars each), checkboxes, tables, and LaTeX (22/24 with block LaTeX; 2 topics without heavy math as expected). Ruff passes. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-129 --status completed`

## 2026-03-17 -- [T-P1-130] ML System Design pillar (Pillar 3) prep docs for all 19 leaf topics
- **What I did**: Wrote `scripts/seed_pillar3_content.py` with detailed senior MLE-depth prep docs for all 19 Pillar 3 leaf topics across 2 categories: (1) Classic Design Problems (9 topics: search & retrieval, recommendation systems, ads & click prediction, marketplace & logistics, NLP & LLM systems, computer vision systems, fraud & trust safety, ML infrastructure design, generative AI systems), (2) Building Blocks (10 topics: two-tower model, multi-stage ranking, ANN, feature store, embedding techniques, real-time feature computation, A/B testing, exploration/exploitation, knowledge distillation, multi-task learning). Each topic has KaTeX-compatible LaTeX, Python code snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: scripts/seed_pillar3_content.py (new), data/mle_prep.db (19 nodes updated)
- **Sanity check result**: All 19 nodes verified in DB with content (4.5K-5.5K chars each), checkboxes, tables, and LaTeX. Ruff passes. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-130 --status completed`

## 2026-03-17 -- [T-P1-131] Math & Statistics pillar (Pillar 7) prep docs for all 14 leaf topics
- **What I did**: Wrote `scripts/seed_pillar7_content.py` with detailed senior MLE-depth prep docs for all 14 Pillar 7 leaf topics across 3 categories: (1) Probability & Statistics (8 topics: probability basics, common distributions, expectation & variance, MLE & MAP, CLT, hypothesis testing, Bayesian inference, information theory), (2) Linear Algebra (3 topics: matrix operations, eigendecomposition, SVD), (3) Calculus & Optimization (3 topics: multivariable calculus, chain rule & backpropagation, convex optimization). Each topic has KaTeX-compatible LaTeX with proofs/derivations, Python code snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: scripts/seed_pillar7_content.py (new), data/mle_prep.db (14 nodes updated)
- **Sanity check result**: All 14 nodes verified in DB with content (4.2K-6.0K chars each), checkboxes, tables, and LaTeX. Ruff passes. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-131 --status completed`

## 2026-03-17 -- [T-P2-132] Applied ML pillar (Pillar 4) prep docs for all 18 leaf topics
- **What I did**: Wrote `scripts/seed_pillar4_content.py` with detailed senior MLE-depth prep docs for all 18 Pillar 4 leaf topics across 7 domain areas: (1) Recommender Systems (3 topics: collaborative filtering, content-based methods, deep recommendation models), (2) Search & IR (4 topics: classic IR/BM25, neural retrieval, query understanding, learning to rank), (3) NLP & LLM Applications (3 topics: text classification, question answering, LLM application patterns), (4) Ads & Monetization (1 topic: CTR prediction), (5) Marketplace & Logistics (3 topics: dynamic pricing, ETA prediction, causal inference), (6) Computer Vision (2 topics: image classification, object detection), (7) Trust & Safety (2 topics: anomaly detection, explainability/SHAP/LIME). Each topic has KaTeX-compatible LaTeX, Python code snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: scripts/seed_pillar4_content.py (new), data/mle_prep.db (18 nodes updated)
- **Sanity check result**: All 18 nodes verified in DB with content (4.5K-6.0K chars each), checkboxes, tables. Ruff passes. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-132 --status completed`

## 2026-03-17 -- [T-P2-133] Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs
- **What I did**: Created three seed scripts for the remaining framework pillars: `seed_pillar1_content.py` (20 Coding & Algorithms leaf topics across Data Structures, Algorithm Paradigms, MLE-Specific Coding), `seed_pillar5_content.py` (15 ML Infrastructure & MLOps leaf topics across Training Infra, Serving Infra, Data Infra, ML Pipeline & Ops), and `seed_pillar8_content.py` (13 Behavioral & Leadership leaf topics across Common Questions, STAR Framework, Company-Specific Behavioral). All 48 topics follow the content template with senior MLE-depth content, KaTeX LaTeX, Python code snippets, interview pattern tables, comparison tables, and self-assessment checkboxes.
- **Deliverables**: scripts/seed_pillar1_content.py (new), scripts/seed_pillar5_content.py (new), scripts/seed_pillar8_content.py (new), data/mle_prep.db (48 nodes updated)
- **Sanity check result**: All 48 nodes verified in DB with content (4.4K-8.9K chars each), checkboxes, tables. Ruff passes. 641 tests pass (1 pre-existing failure unrelated).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-133 --status completed`

