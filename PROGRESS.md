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
