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
