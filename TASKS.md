# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-13: Spaced repetition service (SM-2 variant)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: src/backend/services/spaced_repetition.py. compute_next_review + update_review_schedule. Pure functions. comfort<=2->1d, 3->max(2,prev), 4->2x, 5->2.5x. Clamp min=1. Depends: T-P0-4.

#### T-P0-14: Wire SM-2 into attempt creation
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Modify POST attempts: call update_review_schedule BEFORE updating last_attempted_at. Set next_review_at. Depends: T-P0-12, T-P0-13.

#### T-P0-15: GET /api/problems/review-queue
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Return problems where next_review_at <= now, ordered ASC (most overdue first). Null excluded. Depends: T-P0-14.

#### T-P0-16: LLM service (Anthropic API wrapper)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/services/llm_service.py. LLMService.chat(). Sync client. Never raises - returns {error:...}. JSON parse failure returns {error, raw}. Depends: T-P0-2.

#### T-P0-17: POST /api/problems/{id}/review (LLM quick review)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Accept {approach_text}. REVIEW_SYSTEM_PROMPT from design doc. Call LLM response_format=json. Store in latest attempt llm_review. Return verdict/feedback/hint/complexity/pattern/follow_up. Depends: T-P0-16, T-P0-11.

#### T-P0-18: POST /api/qa/chat (multi-turn QA)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/routers/qa.py. session_id=null creates new, session_id=N continues. Messages as JSON with ISO timestamps. Return {session_id, reply, messages}. Depends: T-P0-16.

#### T-P0-20: GET /api/problems/stats
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Return total, completed, avg_comfort, by_difficulty, by_pattern, weak_patterns (avg<3), total_attempts, avg_duration_seconds. Empty DB returns zeros. Depends: T-P0-12.

#### T-P0-21: Blind75 seed JSON
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/seed_data/blind75.json. 75 entries with leetcode_id, title, url, difficulty, tags, pattern, source=blind75. 18 pattern categories. All unique leetcode_ids. Depends: T-P0-4.

#### T-P0-22: NeetCode150 seed JSON
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/seed_data/neetcode150.json. 150 entries. Overlap with B75 -> source=blind75+neetcode150. NeetCode-only -> source=neetcode150. No duplicate leetcode_ids within file. Depends: T-P0-21.

#### T-P0-23: Framework tree seed JSON
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: src/backend/seed_data/framework_tree.json. Flat array from mle_interview_framework.md. 8 pillars, 150-200 nodes. path dot-separated lowercase_snake_case. parent_path must resolve. Star ratings -> importance. Depends: T-P0-6.

#### T-P0-24: Seed data loader + POST /api/import/seed
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/services/seed_loader.py. load_seed_problems (skip if leetcode_id exists), load_seed_framework (skip if path exists, insert depth-order). POST /api/import/seed loads all 3. Auto-load on startup if empty. Idempotent. Depends: T-P0-21, T-P0-22, T-P0-23, T-P0-9.

#### T-P0-25: Pydantic schemas for framework + company
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/schemas/framework.py + company.py. FrameworkNodeUpdate, StudyLogCreate (duration ge=1), FrameworkNodeResponse (recursive children), CompanyCreate (name min_length=1), CompanyUpdate, CompanyResponse, TopicWeightCreate. Depends: T-P0-6.

#### T-P0-26: GET /api/framework/tree
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Build nested tree from flat DB rows in O(n). max_depth param (0=pillars only, None=full). Return list[FrameworkNodeResponse]. Depends: T-P0-25, T-P0-7.

#### T-P0-27: PUT /api/framework/nodes/{id}
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Partial update. Status transitions: ->in_progress sets started_at if null; ->mastered sets completed_at+progress=100; mastered->other clears completed_at. Depends: T-P0-26.

#### T-P0-28: POST /api/framework/nodes/{id}/log (study log)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Create StudyLog. Update node last_studied_at. Auto-progress: min(95, total_hours/estimated_hours*100). Cap at 95 (mastered explicit). No auto if estimated_hours null. Depends: T-P0-27.

#### T-P0-29: GET /api/framework/stats
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: total_nodes, by_status, overall_progress_pct (weighted by importance), study_hours_this_week, study_hours_by_pillar, weakest_nodes (importance>=0.5, confidence<=2, not mastered), total_study_logs. Depends: T-P0-28.

#### T-P0-30: Companies CRUD
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: GET/POST/PUT /api/companies. List with status/group_tag filter. Duplicate name -> 409. Partial update. Depends: T-P0-25.

#### T-P0-35: Pydantic schemas for scraper module
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: src/backend/schemas/scraper.py. SeedURLCreate (url, source_site Literal), PasteRequest (text min_length=10), ScraperRunRequest, InterviewQuestionResponse. Depends: T-P0-5.

#### T-P0-36: Seed URL management (GET/POST)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: src/backend/routers/scraper.py. GET /api/scraper/seeds with source_site/is_active filters. POST: validate URL, duplicate -> 409. Depends: T-P0-35, T-P0-7.

#### T-P0-37: Site configs module
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: src/backend/scraper/site_configs.py. SiteConfig dataclass (base_url, selectors, rate_limit_seconds). SITE_CONFIGS for blind, 1point3acres, leetcode_discuss. get_config() raises ValueError for unknown. No deps.

#### T-P0-38: HTML content extractor (BeautifulSoup)
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/scraper/extractors.py. extract_posts(html, source_site) -> [{title, body_text, url}]. compute_content_hash(text) -> MD5 hex. html.parser, .get_text(strip=True). Empty returns []. Depends: T-P0-37.

#### T-P0-39: LLM question extractor
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/services/question_extractor.py. EXTRACT_PROMPT from design doc. extract_questions(llm, text, source_context) -> [dict]. Validate required fields (question_text, question_type). Filter invalid. LLM error -> []. Depends: T-P0-16.

#### T-P0-40: POST /api/scraper/paste
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: Hash text, check for duplicate ScrapedPage. If new: create page, extract questions via LLM, store InterviewQuestions. Return {questions_count, questions, was_duplicate}. Depends: T-P0-39, T-P0-36.

#### T-P0-41: Playwright crawler
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/scraper/crawler.py. PlaywrightCrawler.fetch_page(url, site_config). Random delay before fetch. UA rotation (5 UAs). Headless, 30s timeout. Error -> empty string + log. Depends: T-P0-37.

#### T-P0-42: POST /api/scraper/run (orchestrator)
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: BackgroundTasks: for each seed URL, fetch->extract posts->dedup by hash->LLM extract->store. Return 202 + job_id. Track progress in _scraper_jobs dict. ScraperJobStatus dataclass. Depends: T-P0-41, T-P0-38, T-P0-39.

#### T-P0-43: GET /api/scraper/status
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: Return current + recent job statuses. Prune completed jobs older than 1 hour. Depends: T-P0-42.

#### T-P0-44: Interview questions endpoints
- **Priority**: P0
- **Complexity**: M
- **Depends on**: None
- **Description**: GET /api/questions: filters company/role/question_type/is_reviewed/year + text search LIKE. PUT /api/questions/{id}: update is_reviewed/notes/difficulty_estimate/mapped_framework_node_id. POST /api/questions/{id}/analyze: LLM analysis. Depends: T-P0-40.

### P1 -- Should Have (agentic intelligence)

#### T-P1-19: QA session summary + list
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: POST /api/qa/{id}/summarize: LLM summarizes, store in summary field. GET /api/qa/sessions: list without messages, filter by problem_id. Depends: T-P0-18.

#### T-P1-31: Company topic weights
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: POST /api/companies/{id}/weights: batch upsert [{framework_node_id, weight}]. GET /api/companies/{id}: include topic_weights with node titles. Depends: T-P0-30, T-P0-26.

#### T-P1-32: GET /api/companies/{id}/focus
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Return framework nodes weighted by company topic weights, sorted by weight DESC, filtered to progress_pct < 80. Depends: T-P1-31.

#### T-P1-33: Study planner service
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: src/backend/services/study_planner.py. compute_urgency(importance, progress, last_studied, days_until). suggest_study_plan(db, company_ids, hours, days). GET /api/framework/suggest. Exclude mastered. Time proportional to urgency. Depends: T-P0-16, T-P0-29, T-P1-32.

#### T-P1-45: GET /api/dashboard
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Aggregate all modules: problems (total/completed/due_for_review), framework (overall_progress, pillars), recent_activity (7d attempts/hours/questions), company_deadlines, scraper total. Empty DB -> zeros. Depends: T-P0-20, T-P0-29, T-P0-43.

#### T-P1-46: GET /api/export
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Export all data as single JSON: problems (with attempts), framework_nodes (with study_logs), companies (with weights), interview_questions. encoding=utf-8. Depends: T-P0-9, T-P0-26, T-P0-30.

#### T-P1-47: POST /api/import
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: JSON import with merge (skip existing by leetcode_id/path/name). CSV import for problems only. Return {inserted, skipped, errors}. Depends: T-P1-46.

#### T-P1-49: React + Vite + Tailwind scaffolding
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Init src/frontend/ with Vite React template. Tailwind, React Router v6. Proxy /api to localhost:8000 in vite.config.js. Base layout with sidebar (Dashboard, LeetCode, Framework, Questions, Companies). Depends: T-P0-7.

#### T-P1-50: API utility layer + hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: utils/api.js: fetch wrapper with base URL, error handling, JSON parse. hooks/useApi.js: {data, loading, error, refetch}. hooks/useTimer.js: start/pause/reset/elapsed. Depends: T-P1-49.

#### T-P1-51: Dashboard page
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Consumes GET /api/dashboard. Progress rings (Blind75/NeetCode), review queue badge, framework bar chart, weekly hours, company deadline cards. Depends: T-P1-50, T-P1-45.

#### T-P1-52: Problem list page with filters
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Filter sidebar (difficulty checkboxes, pattern dropdown, source toggle, company multi-select). Table/card view with comfort stars, pattern badge, review-due indicator. Pagination. Depends: T-P1-50, T-P0-9.

#### T-P1-53: Problem practice view + timer
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Modal/page: problem details, timer, markdown textarea, result dropdown, complexity inputs, comfort slider 1-5. Submit POSTs attempts. Depends: T-P1-52, T-P0-12.

#### T-P1-54: Quick Review chat panel
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Expandable panel: problem context, chat bubbles, input field. Color-coded verdicts. Toggle review mode (single-shot) vs QA mode (multi-turn). Depends: T-P1-52, T-P0-17, T-P0-18.

#### T-P1-55: Framework tree visualization
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Two views: (1) collapsible tree with progress bars; (2) treemap. Color: red=not_started, yellow=in_progress, blue=review, green=mastered. Size by importance. Depends: T-P1-50, T-P0-26.

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

#### T-P1-61: Backend Dockerfile
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Python 3.11-slim, pip install requirements, EXPOSE 8000, CMD uvicorn. Volume mount for data/. Depends: T-P0-7.

#### T-P1-62: Frontend Dockerfile + docker-compose.yml
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Node 20 build + nginx serve. Compose: backend + frontend services, shared network. Depends: T-P1-61, T-P1-49.

#### T-P1-63: Shared test fixtures (conftest.py)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: db_session (in-memory per test), test_client (FastAPI TestClient with DB override), mock_llm (canned JSON), seed_problems (5 problems), seed_framework (2-level tree). Depends: T-P0-3, T-P0-7.

#### T-P1-64: Integration test -- problem lifecycle
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Create problem -> attempt (comfort=2) -> verify in review queue -> LLM review -> attempt (comfort=5) -> verify not in review queue for days. Depends: T-P1-63, T-P0-14, T-P0-17.

#### T-P1-65: Integration test -- scraper pipeline
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Create seed URL -> paste text -> verify questions extracted and stored -> analyze question -> verify analysis stored. Depends: T-P1-63, T-P0-42.

#### T-P1-66: Integration test -- framework + study planning
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Load seed framework -> log study -> verify progress -> create company + weights -> get suggestions -> verify urgency ordering. Depends: T-P1-63, T-P1-33.

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

- [x] **2026-03-12** -- T-P0-9: GET /api/problems (list with filters). src/backend/routers/problems.py. Filters: difficulty, pattern, source, company (JSON contains), is_completed, category. 
- [x] **2026-03-12** -- T-P0-8: Pydantic schemas for Problem CRUD. src/backend/schemas/problem.py. ProblemCreate (title min_length=1, Literal difficulty/category), ProblemUpdate (all Opti
- [x] **2026-03-12** -- T-P0-7: FastAPI app skeleton + health endpoint. src/backend/main.py. Lifespan context manager calls init_db(). CORS middleware. GET /api/health -> {status:ok}. All rout
- [x] **2026-03-12** -- T-P0-6: Module 3 SQLAlchemy models (FrameworkNode, StudyLog, Company, CompanyTopicWeight). src/backend/models/framework.py + company.py. FrameworkNode: self-referential parent/children, path UNIQUE, status/progr
- [x] **2026-03-12** -- T-P0-5: Module 2 SQLAlchemy models (SeedURL, ScrapedPage, InterviewQuestion). src/backend/models/scraper.py. SeedURL: url UNIQUE, source_site CheckConstraint. ScrapedPage: UniqueConstraint(url,conte
- [x] **2026-03-12** -- T-P0-4: Module 1 SQLAlchemy models (Problem, Attempt, QASession). src/backend/models/problem.py. Match SQL schema from design doc. Problem: leetcode_id nullable, difficulty/category/prio
- [x] **2026-03-12** -- T-P0-3: Database engine + session setup. src/backend/database.py. Base, get_engine(url override), SessionLocal, get_db() generator, init_db(). check_same_thread=
- [x] **2026-03-12** -- T-P0-2: Config module with pydantic-settings. src/backend/config.py + .env.example. Settings class with DATABASE_URL, ANTHROPIC_API_KEY (required), LLM_MODEL, CORS_OR
- [x] **2026-03-12** -- T-P0-12: POST/GET /api/problems/{id}/attempts. POST: create attempt, update problem (last_attempted_at, comfort_level, is_completed sticky). GET: list newest first. AC
- [x] **2026-03-12** -- T-P0-11: PUT/DELETE /api/problems/{id}. PUT: partial update via model_dump(exclude_unset=True). DELETE: cascade, return 204. Both 404 if not found. AC: partial 
- [x] **2026-03-12** -- T-P0-10: POST /api/problems (create). Create problem. Duplicate leetcode_id -> 409. Null leetcode_id always OK. Convert tags/company_tags to JSON. Return 201.
- [x] **2026-03-12** -- T-P0-1: Update dependencies in requirements.txt and pyproject.toml. Add fastapi, uvicorn, sqlalchemy, anthropic, pydantic-settings, httpx, beautifulsoup4, playwright to requirements.txt (p
