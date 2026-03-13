# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-56: Study log form + node detail
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Node detail sidebar: title, description, status, progress, confidence, study history. Log form: date picker, duration, activity type, notes. Depends: T-P1-55, T-P0-28.

#### T-P1-57: Company management (kanban)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Kanban columns by status. Company cards with name, group tag, deadline. Add company form. Click -> focus topics panel. Depends: T-P1-50, T-P0-30, T-P1-32.

#### T-P1-58: Interview questions browse page
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Filterable table: company, role, type, reviewed, text search. Expandable rows. Analyze button (calls LLM). Mark reviewed toggle. Depends: T-P1-50, T-P0-44.

#### T-P1-59: Paste experience form
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Modal on Questions page: large textarea, optional company/role fields. Shows extracted questions for review before confirm. Depends: T-P1-58, T-P0-40.

#### T-P1-62: Frontend Dockerfile + docker-compose.yml
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Node 20 build + nginx serve. Compose: backend + frontend services, shared network. Depends: T-P1-61, T-P1-49.

### P2 -- Nice to Have

#### T-P2-34: LLM-enhanced study recommendations
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Add ?use_llm=true to suggest endpoint. Send urgency list to LLM for natural language plan. Return {structured, plan_text}. Depends: T-P1-33.

#### T-P2-48: DB views + indexes
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Create views v_problem_stats, v_weekly_progress. Add indexes on: problems.pattern, problems.difficulty, problems.next_review_at, framework_nodes.path, study_logs.date, interview_questions.company. Depends: T-P0-3.

#### T-P2-60: AI Study Plan display
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Card on Framework page showing GET /api/framework/suggest results. Regenerate button. LLM toggle for natural language plan. Depends: T-P1-55, T-P1-33.

#### T-P2-67: Performance + final polish
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: Response time logging middleware, SQLite WAL mode, 422 error handler, README setup instructions, ruff/mypy clean pass. Depends: T-P1-64, T-P1-65, T-P1-66.

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 39 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-13** -- T-P1-66: Integration test -- framework + study planning. Load seed framework -> log study -> verify progress -> create company + weights -> get suggestions -> verify urgency ord
- [x] **2026-03-13** -- T-P1-65: Integration test -- scraper pipeline. Create seed URL -> paste text -> verify questions extracted and stored -> analyze question -> verify analysis stored. De
- [x] **2026-03-13** -- T-P1-64: Integration test -- problem lifecycle. Create problem -> attempt (comfort=2) -> verify in review queue -> LLM review -> attempt (comfort=5) -> verify not in re
- [x] **2026-03-13** -- T-P1-61: Backend Dockerfile. Python 3.11-slim, pip install requirements, EXPOSE 8000, CMD uvicorn. Volume mount for data/. Depends: T-P0-7.
- [x] **2026-03-13** -- T-P1-55: Framework tree visualization. Two views: (1) collapsible tree with progress bars; (2) treemap. Color: red=not_started, yellow=in_progress, blue=review
- [x] **2026-03-13** -- T-P1-54: Quick Review chat panel. Expandable panel: problem context, chat bubbles, input field. Color-coded verdicts. Toggle review mode (single-shot) vs 
- [x] **2026-03-13** -- T-P1-53: Problem practice view + timer. Modal/page: problem details, timer, markdown textarea, result dropdown, complexity inputs, comfort slider 1-5. Submit PO
- [x] **2026-03-13** -- T-P1-52: Problem list page with filters. Filter sidebar (difficulty checkboxes, pattern dropdown, source toggle, company multi-select). Table/card view with comf
- [x] **2026-03-13** -- T-P1-51: Dashboard page. Consumes GET /api/dashboard. Progress rings (Blind75/NeetCode), review queue badge, framework bar chart, weekly hours, c
- [x] **2026-03-13** -- T-P1-50: API utility layer + hooks. utils/api.js: fetch wrapper with base URL, error handling, JSON parse. hooks/useApi.js: {data, loading, error, refetch}.
- [x] **2026-03-13** -- T-P1-49: React + Vite + Tailwind scaffolding. Init src/frontend/ with Vite React template. Tailwind, React Router v6. Proxy /api to localhost:8000 in vite.config.js. 
- [x] **2026-03-13** -- T-P1-47: POST /api/import. JSON import with merge (skip existing by leetcode_id/path/name). CSV import for problems only. Return {inserted, skipped
- [x] **2026-03-12** -- T-P1-63: Shared test fixtures (conftest.py). db_session (in-memory per test), test_client (FastAPI TestClient with DB override), mock_llm (canned JSON), seed_problem
- [x] **2026-03-12** -- T-P1-46: GET /api/export. Export all data as single JSON: problems (with attempts), framework_nodes (with study_logs), companies (with weights), i
- [x] **2026-03-12** -- T-P1-45: GET /api/dashboard. Aggregate all modules: problems (total/completed/due_for_review), framework (overall_progress, pillars), recent_activity
- [x] **2026-03-12** -- T-P1-33: Study planner service. src/backend/services/study_planner.py. compute_urgency(importance, progress, last_studied, days_until). suggest_study_pl
- [x] **2026-03-12** -- T-P1-32: GET /api/companies/{id}/focus. Return framework nodes weighted by company topic weights, sorted by weight DESC, filtered to progress_pct < 80. Depends:
- [x] **2026-03-12** -- T-P1-31: Company topic weights. POST /api/companies/{id}/weights: batch upsert [{framework_node_id, weight}]. GET /api/companies/{id}: include topic_wei
- [x] **2026-03-12** -- T-P1-19: QA session summary + list. POST /api/qa/{id}/summarize: LLM summarizes, store in summary field. GET /api/qa/sessions: list without messages, filter
