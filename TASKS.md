# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 55 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
- [x] **2026-03-15** -- T-P0-69: Fix CI: add python-multipart dependency
- [x] **2026-03-13** -- T-P2-67: Performance + final polish. Response time logging middleware, SQLite WAL mode, 422 error handler, README setup instructions, ruff/mypy clean pass. D
- [x] **2026-03-13** -- T-P2-60: AI Study Plan display. Card on Framework page showing GET /api/framework/suggest results. Regenerate button. LLM toggle for natural language pl
- [x] **2026-03-13** -- T-P2-48: DB views + indexes. Create views v_problem_stats, v_weekly_progress. Add indexes on: problems.pattern, problems.difficulty, problems.next_re
- [x] **2026-03-13** -- T-P2-34: LLM-enhanced study recommendations. Add ?use_llm=true to suggest endpoint. Send urgency list to LLM for natural language plan. Return {structured, plan_text
- [x] **2026-03-13** -- T-P1-66: Integration test -- framework + study planning. Load seed framework -> log study -> verify progress -> create company + weights -> get suggestions -> verify urgency ord
- [x] **2026-03-13** -- T-P1-65: Integration test -- scraper pipeline. Create seed URL -> paste text -> verify questions extracted and stored -> analyze question -> verify analysis stored. De
- [x] **2026-03-13** -- T-P1-64: Integration test -- problem lifecycle. Create problem -> attempt (comfort=2) -> verify in review queue -> LLM review -> attempt (comfort=5) -> verify not in re
- [x] **2026-03-13** -- T-P1-62: Frontend Dockerfile + docker-compose.yml. Node 20 build + nginx serve. Compose: backend + frontend services, shared network. Depends: T-P1-61, T-P1-49.
- [x] **2026-03-13** -- T-P1-61: Backend Dockerfile. Python 3.11-slim, pip install requirements, EXPOSE 8000, CMD uvicorn. Volume mount for data/. Depends: T-P0-7.
- [x] **2026-03-13** -- T-P1-59: Paste experience form. Modal on Questions page: large textarea, optional company/role fields. Shows extracted questions for review before confi
- [x] **2026-03-13** -- T-P1-58: Interview questions browse page. Filterable table: company, role, type, reviewed, text search. Expandable rows. Analyze button (calls LLM). Mark reviewed
- [x] **2026-03-13** -- T-P1-57: Company management (kanban). Kanban columns by status. Company cards with name, group tag, deadline. Add company form. Click -> focus topics panel. D
