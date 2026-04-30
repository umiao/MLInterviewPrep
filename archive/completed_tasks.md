# Completed Tasks Archive

> 604 completed tasks archived as of latest archival.

- [x] **2026-03-12** -- T-P0-1: Update dependencies in requirements.txt and pyproject.toml. Add fastapi, uvicorn, sqlalchemy, anthropic, pydantic-settings, httpx, beautifulsoup4, playwright to requirements.txt (p
- [x] **2026-03-12** -- T-P0-10: POST /api/problems (create). Create problem. Duplicate leetcode_id -> 409. Null leetcode_id always OK. Convert tags/company_tags to JSON. Return 201.
- [x] **2026-03-12** -- T-P0-11: PUT/DELETE /api/problems/{id}. PUT: partial update via model_dump(exclude_unset=True). DELETE: cascade, return 204. Both 404 if not found. AC: partial 
- [x] **2026-03-12** -- T-P0-12: POST/GET /api/problems/{id}/attempts. POST: create attempt, update problem (last_attempted_at, comfort_level, is_completed sticky). GET: list newest first. AC
- [x] **2026-03-12** -- T-P0-13: Spaced repetition service (SM-2 variant). src/backend/services/spaced_repetition.py. compute_next_review + update_review_schedule. Pure functions. comfort<=2->1d,
- [x] **2026-03-12** -- T-P0-14: Wire SM-2 into attempt creation. Modify POST attempts: call update_review_schedule BEFORE updating last_attempted_at. Set next_review_at. Depends: T-P0-1
- [x] **2026-03-12** -- T-P0-15: GET /api/problems/review-queue. Return problems where next_review_at <= now, ordered ASC (most overdue first). Null excluded. Depends: T-P0-14.
- [x] **2026-03-12** -- T-P0-16: LLM service (Anthropic API wrapper). src/backend/services/llm_service.py. LLMService.chat(). Sync client. Never raises - returns {error:...}. JSON parse fail
- [x] **2026-03-12** -- T-P0-17: POST /api/problems/{id}/review (LLM quick review). Accept {approach_text}. REVIEW_SYSTEM_PROMPT from design doc. Call LLM response_format=json. Store in latest attempt llm
- [x] **2026-03-12** -- T-P0-18: POST /api/qa/chat (multi-turn QA). src/backend/routers/qa.py. session_id=null creates new, session_id=N continues. Messages as JSON with ISO timestamps. Re
- [x] **2026-03-12** -- T-P0-2: Config module with pydantic-settings. src/backend/config.py + .env.example. Settings class with DATABASE_URL, ANTHROPIC_API_KEY (required), LLM_MODEL, CORS_OR
- [x] **2026-03-12** -- T-P0-20: GET /api/problems/stats. Return total, completed, avg_comfort, by_difficulty, by_pattern, weak_patterns (avg<3), total_attempts, avg_duration_sec
- [x] **2026-03-12** -- T-P0-21: Blind75 seed JSON. src/backend/seed_data/blind75.json. 75 entries with leetcode_id, title, url, difficulty, tags, pattern, source=blind75. 
- [x] **2026-03-12** -- T-P0-22: NeetCode150 seed JSON. src/backend/seed_data/neetcode150.json. 150 entries. Overlap with B75 -> source=blind75+neetcode150. NeetCode-only -> so
- [x] **2026-03-12** -- T-P0-23: Framework tree seed JSON. src/backend/seed_data/framework_tree.json. Flat array from mle_interview_framework.md. 8 pillars, 150-200 nodes. path do
- [x] **2026-03-12** -- T-P0-24: Seed data loader + POST /api/import/seed. src/backend/services/seed_loader.py. load_seed_problems (skip if leetcode_id exists), load_seed_framework (skip if path 
- [x] **2026-03-12** -- T-P0-25: Pydantic schemas for framework + company. src/backend/schemas/framework.py + company.py. FrameworkNodeUpdate, StudyLogCreate (duration ge=1), FrameworkNodeRespons
- [x] **2026-03-12** -- T-P0-26: GET /api/framework/tree. Build nested tree from flat DB rows in O(n). max_depth param (0=pillars only, None=full). Return list[FrameworkNodeRespo
- [x] **2026-03-12** -- T-P0-27: PUT /api/framework/nodes/{id}. Partial update. Status transitions: ->in_progress sets started_at if null; ->mastered sets completed_at+progress=100; ma
- [x] **2026-03-12** -- T-P0-28: POST /api/framework/nodes/{id}/log (study log). Create StudyLog. Update node last_studied_at. Auto-progress: min(95, total_hours/estimated_hours*100). Cap at 95 (master
- [x] **2026-03-12** -- T-P0-29: GET /api/framework/stats. total_nodes, by_status, overall_progress_pct (weighted by importance), study_hours_this_week, study_hours_by_pillar, wea
- [x] **2026-03-12** -- T-P0-3: Database engine + session setup. src/backend/database.py. Base, get_engine(url override), SessionLocal, get_db() generator, init_db(). check_same_thread=
- [x] **2026-03-12** -- T-P0-30: Companies CRUD. GET/POST/PUT /api/companies. List with status/group_tag filter. Duplicate name -> 409. Partial update. Depends: T-P0-25.
- [x] **2026-03-12** -- T-P0-35: Pydantic schemas for scraper module. src/backend/schemas/scraper.py. SeedURLCreate (url, source_site Literal), PasteRequest (text min_length=10), ScraperRunR
- [x] **2026-03-12** -- T-P0-36: Seed URL management (GET/POST). src/backend/routers/scraper.py. GET /api/scraper/seeds with source_site/is_active filters. POST: validate URL, duplicate
- [x] **2026-03-12** -- T-P0-37: Site configs module. src/backend/scraper/site_configs.py. SiteConfig dataclass (base_url, selectors, rate_limit_seconds). SITE_CONFIGS for bl
- [x] **2026-03-12** -- T-P0-38: HTML content extractor (BeautifulSoup). src/backend/scraper/extractors.py. extract_posts(html, source_site) -> [{title, body_text, url}]. compute_content_hash(t
- [x] **2026-03-12** -- T-P0-39: LLM question extractor. src/backend/services/question_extractor.py. EXTRACT_PROMPT from design doc. extract_questions(llm, text, source_context)
- [x] **2026-03-12** -- T-P0-4: Module 1 SQLAlchemy models (Problem, Attempt, QASession). src/backend/models/problem.py. Match SQL schema from design doc. Problem: leetcode_id nullable, difficulty/category/prio
- [x] **2026-03-12** -- T-P0-40: POST /api/scraper/paste. Hash text, check for duplicate ScrapedPage. If new: create page, extract questions via LLM, store InterviewQuestions. Re
- [x] **2026-03-12** -- T-P0-41: Playwright crawler. src/backend/scraper/crawler.py. PlaywrightCrawler.fetch_page(url, site_config). Random delay before fetch. UA rotation (
- [x] **2026-03-12** -- T-P0-42: POST /api/scraper/run (orchestrator). BackgroundTasks: for each seed URL, fetch->extract posts->dedup by hash->LLM extract->store. Return 202 + job_id. Track 
- [x] **2026-03-12** -- T-P0-43: GET /api/scraper/status. Return current + recent job statuses. Prune completed jobs older than 1 hour. Depends: T-P0-42.
- [x] **2026-03-12** -- T-P0-44: Interview questions endpoints. GET /api/questions: filters company/role/question_type/is_reviewed/year + text search LIKE. PUT /api/questions/{id}: upd
- [x] **2026-03-12** -- T-P0-5: Module 2 SQLAlchemy models (SeedURL, ScrapedPage, InterviewQuestion). src/backend/models/scraper.py. SeedURL: url UNIQUE, source_site CheckConstraint. ScrapedPage: UniqueConstraint(url,conte
- [x] **2026-03-12** -- T-P0-6: Module 3 SQLAlchemy models (FrameworkNode, StudyLog, Company, CompanyTopicWeight). src/backend/models/framework.py + company.py. FrameworkNode: self-referential parent/children, path UNIQUE, status/progr
- [x] **2026-03-12** -- T-P0-7: FastAPI app skeleton + health endpoint. src/backend/main.py. Lifespan context manager calls init_db(). CORS middleware. GET /api/health -> {status:ok}. All rout
- [x] **2026-03-12** -- T-P0-8: Pydantic schemas for Problem CRUD. src/backend/schemas/problem.py. ProblemCreate (title min_length=1, Literal difficulty/category), ProblemUpdate (all Opti
- [x] **2026-03-12** -- T-P0-9: GET /api/problems (list with filters). src/backend/routers/problems.py. Filters: difficulty, pattern, source, company (JSON contains), is_completed, category. 
- [x] **2026-03-12** -- T-P1-19: QA session summary + list. POST /api/qa/{id}/summarize: LLM summarizes, store in summary field. GET /api/qa/sessions: list without messages, filter
- [x] **2026-03-12** -- T-P1-31: Company topic weights. POST /api/companies/{id}/weights: batch upsert [{framework_node_id, weight}]. GET /api/companies/{id}: include topic_wei
- [x] **2026-03-12** -- T-P1-32: GET /api/companies/{id}/focus. Return framework nodes weighted by company topic weights, sorted by weight DESC, filtered to progress_pct < 80. Depends:
- [x] **2026-03-12** -- T-P1-33: Study planner service. src/backend/services/study_planner.py. compute_urgency(importance, progress, last_studied, days_until). suggest_study_pl
- [x] **2026-03-12** -- T-P1-45: GET /api/dashboard. Aggregate all modules: problems (total/completed/due_for_review), framework (overall_progress, pillars), recent_activity
- [x] **2026-03-12** -- T-P1-46: GET /api/export. Export all data as single JSON: problems (with attempts), framework_nodes (with study_logs), companies (with weights), i
- [x] **2026-03-13** -- T-P1-47: POST /api/import. JSON import with merge (skip existing by leetcode_id/path/name). CSV import for problems only. Return {inserted, skipped
- [x] **2026-03-13** -- T-P1-49: React + Vite + Tailwind scaffolding. Init src/frontend/ with Vite React template. Tailwind, React Router v6. Proxy /api to localhost:8000 in vite.config.js. 
- [x] **2026-03-13** -- T-P1-50: API utility layer + hooks. utils/api.js: fetch wrapper with base URL, error handling, JSON parse. hooks/useApi.js: {data, loading, error, refetch}.
- [x] **2026-03-13** -- T-P1-51: Dashboard page. Consumes GET /api/dashboard. Progress rings (Blind75/NeetCode), review queue badge, framework bar chart, weekly hours, c
- [x] **2026-03-13** -- T-P1-52: Problem list page with filters. Filter sidebar (difficulty checkboxes, pattern dropdown, source toggle, company multi-select). Table/card view with comf
- [x] **2026-03-13** -- T-P1-53: Problem practice view + timer. Modal/page: problem details, timer, markdown textarea, result dropdown, complexity inputs, comfort slider 1-5. Submit PO
- [x] **2026-03-13** -- T-P1-54: Quick Review chat panel. Expandable panel: problem context, chat bubbles, input field. Color-coded verdicts. Toggle review mode (single-shot) vs 
- [x] **2026-03-13** -- T-P1-55: Framework tree visualization. Two views: (1) collapsible tree with progress bars; (2) treemap. Color: red=not_started, yellow=in_progress, blue=review
- [x] **2026-03-13** -- T-P1-56: Study log form + node detail. Node detail sidebar: title, description, status, progress, confidence, study history. Log form: date picker, duration, a
- [x] **2026-03-12** -- T-P1-63: Shared test fixtures (conftest.py). db_session (in-memory per test), test_client (FastAPI TestClient with DB override), mock_llm (canned JSON), seed_problem
- [x] **2026-03-15** -- T-P0-69: Fix CI: add python-multipart dependency
- [x] **2026-03-15** -- T-P0-70: SDK migration: async LLMService + sdk_adapter. Create src/backend/services/sdk_adapter.py (SDK_AVAILABLE flag, async run_query). Rewrite LLMService with async chat(), 
- [x] **2026-03-15** -- T-P0-71: Convert LLM callers to async + update tests. All endpoints calling llm.chat() become async def + await. extract_questions() becomes async. Update all test files for 
- [x] **2026-03-15** -- T-P0-73: [B1] Install React Query + setup QueryClientProvider in App.tsx. AC:
- @tanstack/react-query installed
- QueryClientProvider wraps App
- Default staleTime 30s configured
- One page (Das
- [x] **2026-03-13** -- T-P1-57: Company management (kanban). Kanban columns by status. Company cards with name, group tag, deadline. Add company form. Click -> focus topics panel. D
- [x] **2026-03-13** -- T-P1-58: Interview questions browse page. Filterable table: company, role, type, reviewed, text search. Expandable rows. Analyze button (calls LLM). Mark reviewed
- [x] **2026-03-13** -- T-P1-59: Paste experience form. Modal on Questions page: large textarea, optional company/role fields. Shows extracted questions for review before confi
- [x] **2026-03-13** -- T-P1-61: Backend Dockerfile. Python 3.11-slim, pip install requirements, EXPOSE 8000, CMD uvicorn. Volume mount for data/. Depends: T-P0-7.
- [x] **2026-03-13** -- T-P1-62: Frontend Dockerfile + docker-compose.yml. Node 20 build + nginx serve. Compose: backend + frontend services, shared network. Depends: T-P1-61, T-P1-49.
- [x] **2026-03-13** -- T-P1-64: Integration test -- problem lifecycle. Create problem -> attempt (comfort=2) -> verify in review queue -> LLM review -> attempt (comfort=5) -> verify not in re
- [x] **2026-03-13** -- T-P1-65: Integration test -- scraper pipeline. Create seed URL -> paste text -> verify questions extracted and stored -> analyze question -> verify analysis stored. De
- [x] **2026-03-13** -- T-P1-66: Integration test -- framework + study planning. Load seed framework -> log study -> verify progress -> create company + weights -> get suggestions -> verify urgency ord
- [x] **2026-03-13** -- T-P2-34: LLM-enhanced study recommendations. Add ?use_llm=true to suggest endpoint. Send urgency list to LLM for natural language plan. Return {structured, plan_text
- [x] **2026-03-13** -- T-P2-48: DB views + indexes. Create views v_problem_stats, v_weekly_progress. Add indexes on: problems.pattern, problems.difficulty, problems.next_re
- [x] **2026-03-13** -- T-P2-60: AI Study Plan display. Card on Framework page showing GET /api/framework/suggest results. Regenerate button. LLM toggle for natural language pl
- [x] **2026-03-13** -- T-P2-67: Performance + final polish. Response time logging middleware, SQLite WAL mode, 422 error handler, README setup instructions, ruff/mypy clean pass. D
- [x] **2026-03-15** -- T-P0-74: [B1] Migrate all pages from useApi to React Query useQuery/useMutation. AC:
- Problems, Framework, Questions, Companies pages all use useQuery for reads
- All existing useMutation calls migrat
- [x] **2026-03-15** -- T-P0-75: [B1] Build Toast notification system (ToastContext + ToastProvider). AC:
- ToastContext.tsx with success/error/info methods
- ToastProvider wrapping App
- Fixed-position toast stack (bottom
- [x] **2026-03-15** -- T-P0-76: [B1] Build shared UI components (Modal, ConfirmDialog, Badge, EmptyState, LoadingSpinner, SearchInput, Pagination). AC (REDUCED SCOPE -- build only what Batch 1 needs):
- Toast.tsx: toast notification component (used by mutation error r
- [x] **2026-03-15** -- T-P0-77: [B1] Add useFilterParams hook + useDebounce hook. AC:
- useFilterParams: stores filter/sort state in URL searchParams via useSearchParams
- Applied to Problems page filte
- [x] **2026-03-15** -- T-P0-78: [B1] CJK font support + install recharts + react-markdown. AC:
- Noto Sans SC, Microsoft YaHei added to font stack in index.css
- break-words class on text containers for CJK
- re
- [x] **2026-03-15** -- T-P0-79: [B2] Backend: expose description in framework tree API + extend node update schema. AC:
- PUT /api/framework/nodes/{id} accepts title and description fields
- GET /api/framework/tree includes description 
- [x] **2026-03-15** -- T-P0-80: [B2] Frontend: Notes tab in NodeDetailPanel with markdown edit/preview + autosave. AC:
- Tabs component added to NodeDetailPanel (Details | Notes | Study Log)
- Notes tab: textarea for markdown editing +
- [x] **2026-03-15** -- T-P0-81: [B3] Backend: Add framework_node_id FK to Problem model + topic-linked endpoints. AC:
- Problem model gets nullable framework_node_id FK to framework_nodes
- DB MIGRATION REQUIRED: ALTER TABLE problems 
- [x] **2026-03-15** -- T-P0-82: [B3] Frontend: FrameworkNodePicker component. AC:
- Dropdown/autocomplete component for selecting a framework topic
- Fetches flat list from /api/framework/tree?max_d
- [x] **2026-03-15** -- T-P0-83: [B3] Frontend: Problem CRUD (Add/Edit/Delete) + text search. AC:
- + Add Problem button -> AddProblemModal (title, leetcode_id, url, difficulty, tags, pattern, category, source, com
- [x] **2026-03-15** -- T-P0-84: [B3] Frontend: Topic detail shows linked problems + questions in NodeDetailPanel. AC:
- NodeDetailPanel gets Problems and Questions sub-sections (or sub-tabs)
- Problems: fetches GET /api/framework/node
- [x] **2026-03-15** -- T-P1-85: [B4] Backend: Split dashboard API into today/activity/summary endpoints. AC:
- GET /api/dashboard/today: due_reviews count, suggested_focus_topic (weakest), streak_days
- GET /api/dashboard/act
- [x] **2026-03-15** -- T-P1-86: [B4] Frontend: Dashboard rewrite with Today Focus + Weekly Chart + Pillar Progress. AC:
- Row 1: Today Focus cards (3-col): Due Reviews (clickable -> /problems?review=due), Weakest Topic (clickable -> /fr
- [x] **2026-03-15** -- T-P1-87: [B5] Backend: DELETE companies/{id}, POST/DELETE questions, extend PUT questions/{id}. AC:
- DELETE /api/companies/{id}: deletes company + cascades topic weights. Returns count of deleted weights.
- POST /ap
- [x] **2026-03-15** -- T-P1-88: [B5] Frontend: Companies edit/delete + topic weight editor. AC:
- Edit company in FocusTopicsPanel: name, group_tag, notes, applied_at all editable + Save
- Delete company button -
- [x] **2026-03-15** -- T-P1-89: [B5] Frontend: Questions add/edit/delete + bulk mark reviewed + framework mapping. AC:
- + Add Question button -> AddQuestionModal (question_text, company, role, type, level, year, tags)
- Inline edit me
- [x] **2026-03-16** -- T-P0-100: ReadingProgress + AudioCache models + Migration v4. New models in models/reading.py: ReadingProgress (content_type, content_id, last_chunk_index, char_offset, total_chars, 
- [x] **2026-03-16** -- T-P0-101: Content Pipeline: queue ranking, preprocessing v2, chunking. Expand services/content_pipeline.py: (1) get_reading_queue(db, company_ids, days_until_interview, limit=20) - reuse comp
- [x] **2026-03-16** -- T-P0-102: Reading REST endpoints: queue, progress, content, async synthesize. Expand routers/reading.py + new schemas/reading.py: GET /api/reading/queue (ranked with progress), GET /api/reading/prog
- [x] **2026-03-16** -- T-P0-99: TTS MVP: edge-tts -> MP3 -> <audio> playback for framework nodes. Minimal vertical slice: pick one framework node -> preprocess markdown (v1: strip #, **, *, _, links, skip code blocks) 
- [x] **2026-03-16** -- T-P1-103: TTS Engine abstraction: EdgeTTS + OpenAI + Browser engines. Refactor services/tts_engine.py: ABC TTSEngine with synthesize_to_file + voice_options. EdgeTTSEngine (refactor from MVP
- [x] **2026-03-16** -- T-P1-104: Frontend Audio Player + Radio Mode (core playback). New files: types/reading.ts, hooks/useAudioPlayer.ts, contexts/AudioPlayerContext.tsx. Hook manages <audio> element: pla
- [x] **2026-03-16** -- T-P1-105: Browser Web Speech API fallback + prefetch next item. Enhance useAudioPlayer: (1) Browser fallback: if synthesize returns {mode: browser}, use SpeechSynthesis API seamlessly 
- [x] **2026-03-16** -- T-P1-106: Persistent Audio Player Bar (Spotify-style bottom bar). New AudioPlayerBar.tsx: fixed-bottom bar with [Title+badge] [<<] [Play/Pause] [>>] [Progress bar] [Time] [Speed 0.75-2x]
- [x] **2026-03-16** -- T-P1-107: Study Radio page: queue management, now playing, history. New StudyRadio.tsx page at /radio. Sections: (1) Quick Start with company filter + engine select + Start Radio button (2
- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
- [x] **2026-03-15** -- T-P2-72: Add GET / root endpoint returning API info JSON
- [x] **2026-03-15** -- T-P2-90: [B6] Frontend: Kanban drag-and-drop for Companies page. AC:
- Install @hello-pangea/dnd
- Wrap Kanban columns as Droppable, cards as Draggable
- On drop: call PUT /companies/{i
- [x] **2026-03-15** -- T-P2-91: [B6] Frontend: Framework tree search + breadcrumb path. AC:
- TreeSearchBar: type to filter, matching nodes highlighted (yellow bg), non-matching ancestors auto-expanded, non-m
- [x] **2026-03-15** -- T-P2-92: [B6] Frontend: Settings page (import/export + scraper management). AC:
- New /settings route added to App.tsx
- Settings link in Sidebar
- Export section: Download JSON button (GET /api/e
- [x] **2026-03-15** -- T-P2-93: [B6] Frontend: QA session summarize button in ReviewPanel. AC:
- Summarize button appears for completed QA sessions in ReviewPanel
- Calls POST /api/qa/{id}/summarize
- Shows summ
- [x] **2026-03-15** -- T-P2-94: [B7] Frontend: Analytics deep-dive (radar chart, scatter plot, trend lines). AC:\n- Pattern comfort radar chart (Recharts RadarChart) on Problems page or Dashboard\n- Framework confidence vs import
- [x] **2026-03-16** -- T-P0-113: Fix Radio blank page, TTS preprocessing quality, LinkedIn content sync
- [x] **2026-03-16** -- T-P0-117: Integrate LinkedIn JD into Prep Notes
- [x] **2026-03-16** -- T-P0-118: Problems UX: full-page descriptions, markdown rendering, batch fetch, remove Edit/Del
- [x] **2026-03-16** -- T-P1-108: Listen buttons across app (Companies, Questions, Dashboard, Framework). Add Listen buttons to existing pages using AudioPlayerContext.play(): Companies page (Listen to prep notes per company),
- [x] **2026-03-16** -- T-P1-114: Unified Faithful Transcript System
- [x] **2026-03-16** -- T-P1-115: Decouple Reading from Synthesis (Text View)
- [x] **2026-03-16** -- T-P1-116: Local LeetCode Descriptions (Neetcode.io Fetch)
- [x] **2026-03-16** -- T-P1-119: Fix strikethrough + math formula rendering in MarkdownPreview. Problem: (1) ~~strikethrough~~ text not rendering with line-through -- Tailwind v4 prose resets <del> styling. (2) Math 
- [x] **2026-03-16** -- T-P1-120: Problems: add Difficulty as a sort option (frontend + backend). AC:
1. Sort dropdown includes Difficulty option
2. Backend sorts semantically: easy(1) < medium(2) < hard(3); null sorts
- [x] **2026-03-16** -- T-P1-121: Problems: notes indicator icon on All Problems tab. Problem: No visual signal on All Problems landing page to indicate which problems have notes.
AC:
1. Problems with notes
- [x] **2026-03-16** -- T-P1-122: Problem detail: collapsible My Notes section (default collapsed). Problem: My Notes section always expanded adds visual noise.
AC:
1. My Notes defaults to collapsed, showing only header 
- [x] **2026-03-16** -- T-P1-124: Fix strikethrough in prep-prose CSS + fix Blind75 docx import regex for full-width colons
- [x] **2026-03-16** -- T-P1-95: Add prep_notes to Company model + migration v3 + get_or_create_company service. ## Acceptance Criteria
1. Company model has `prep_notes` Column(Text, nullable=True)
2. Migration v3 adds column via ADD
- [x] **2026-03-16** -- T-P1-96: Auto-link company on timeline event creation via get_or_create_company. ## Acceptance Criteria
1. timeline router create_event() calls get_or_create_company(event.company_name, db) to resolve 
- [x] **2026-03-16** -- T-P1-97: PrepNotesTab with checkbox click-toggle + Companies page integration. ## Acceptance Criteria
1. New utils/markdown.ts: countUnchecked(md) and countChecked(md) using regex ^[-*]\s*\[ \] and ^
- [x] **2026-03-16** -- T-P1-98: Dashboard timeline prep notes modal + red dots on EventCard. ## Acceptance Criteria
1. InterviewTimeline: new onCompanyClick(companyName, companyId) prop
2. EventCard: company_name 
- [x] **2026-03-17** -- T-P1-125: Fix checkbox persistence and scroll white space bugs on PrepNotesPage
- [x] **2026-03-17** -- T-P1-126: Framework full-screen notes page: backend GET endpoint + useFrameworkNotes hook + FrameworkNotesPage + route + Open Full Page link. End-to-end: (1) GET /framework/nodes/{id} endpoint returning single node. (2) useFrameworkNotes hook mirroring usePrepNo
- [x] **2026-03-17** -- T-P1-127: Content template + ML Fundamentals pillar (Pillar 2) prep docs for all 25 leaf topics. Create docs/framework_content_template.md with standard structure (Overview, Core Concepts with LaTeX, Implementation, I
- [x] **2026-03-17** -- T-P1-128: PrevNextNav arrow component + integrate in PrepNotesPage and ProblemDetailPage. Reusable PrevNextNav component with left/right chevrons + tooltip. PrepNotesPage: navigate companies alphabetically. Pro
- [x] **2026-03-17** -- T-P1-129: Deep Learning & LLM pillar (Pillar 6) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 6 leaf topics following content template. Covers: Transformer architecture, a
- [x] **2026-03-17** -- T-P1-130: ML System Design pillar (Pillar 3) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 3 leaf topics. Covers: design framework methodology, classic problems (rec sy
- [x] **2026-03-17** -- T-P1-131: Math & Statistics pillar (Pillar 7) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 7 leaf topics. Covers: probability distributions, Bayesian inference, hypothe
- [x] **2026-03-17** -- T-P1-134: Fix MarkdownPreview checkbox mismatch caused by remarkMath dollar-sign corruption
- [x] **2026-03-17** -- T-P1-135: Sticky toolbar + scroll position sync for PrepNotes
- [x] **2026-03-17** -- T-P1-136: Fix scroll sync to use dual refs (container + textarea) for correct capture/restore targets
- [x] **2026-03-17** -- T-P1-137: Fix Prep Notes Display: full-screen MD rendering + framework tree notes links
- [x] **2026-03-17** -- T-P1-138: Fix math delimiters, add code syntax highlighting, document markdown conventions
- [x] **2026-03-17** -- T-P1-139: Framework: widen right panel to 35% default
- [x] **2026-03-16** -- T-P2-109: Interview-aware content ordering in reading queue. Enhance get_reading_queue(): query interview_events for upcoming interviews, boost urgency for soonest interview company
- [x] **2026-03-16** -- T-P2-110: LLM-generated TTS summaries for long content. Use LLM service to create spoken-word-optimized summaries. Cache in tts_summaries table. Prompt: Rewrite for TTS narrati
- [x] **2026-03-16** -- T-P2-111: Listening session analytics on Dashboard and StudyRadio. Track listening sessions via ReadingSession model. POST /api/reading/sessions (create/close), GET /api/reading/stats (to
- [x] **2026-03-16** -- T-P2-123: Framework: resizable right panel and scrollable tabs in NodeDetailPanel. Problem: Right panel fixed at 288px (w-72), tabs overflow when names are long.
AC:
1. Right panel resizable by dragging 
- [x] **2026-03-19** -- T-P0-146: Forum service layer (two-phase scrape + import to prep notes). Create src/backend/services/forum_service.py with business logic for the two-phase forum scraping workflow.

**Functions
- [x] **2026-03-19** -- T-P0-147: Forum CLI script (scripts/forum_scrape.py). Create scripts/forum_scrape.py as the primary CLI interface wrapping the forum service layer.

**Subcommands (via argpar
- [x] **2026-03-19** -- T-P0-148: Forum API routes + Pydantic schemas. Create src/backend/routers/forum.py and src/backend/schemas/forum.py for the forum scraping REST API.

**Schemas (src/ba
- [x] **2026-03-19** -- T-P0-149: Frontend ForumPostsTab component + integration into PrepNotesPage. Create ForumPostsTab React component and integrate it as a tab in the existing PrepNotesPage.

**New files:**
1. `src/fr
- [x] **2026-03-19** -- T-P0-151: Forum extractor: derive_page_url + extract_max_page pure functions. Add two pure functions to src/backend/scraper/forum_extractors.py:

1. derive_page_url(base_url: str, page: int) -> str

- [x] **2026-03-19** -- T-P0-152: Forum service: refactor scrape_seed_page + add scrape_seed_pages. Refactor src/backend/services/forum_service.py for multi-page scraping:

Step 1: Extract helper (refactoring safety: run
- [x] **2026-03-19** -- T-P0-153: Forum scrape CLI + API: pagination params. Wire pagination to CLI and API. Three files to modify:

1. src/backend/schemas/forum.py -- add response model:
   class 
- [x] **2026-03-19** -- T-P0-154: Live scrape: LinkedIn 1point3acres first 5 pages. Execute the live scraping pipeline. This is a manual execution task, not a code task.

Prerequisites: T-P0-151, T-P0-152
- [x] **2026-03-17** -- T-P1-140: Framework: URL-driven selection + tree auto-expand + row-click expand
- [x] **2026-03-17** -- T-P1-141: Framework: checkbox progress calc + parent propagation
- [x] **2026-03-17** -- T-P1-142: Seed DoorDash and Uber interview events
- [x] **2026-03-22** -- T-P1-158: Backend: Add SystemDesign model, API endpoints, and seed data. Create SystemDesign model with 8 section columns (overview, architecture, dataflow, formulas, production_constraints, tr
- [x] **2026-03-22** -- T-P1-159: Frontend: Add System Design sidebar link and route definitions. Add 'System Design' to Sidebar.tsx navItems (between Framework and Questions). Add routes: /system-design -> SystemDesig
- [x] **2026-03-22** -- T-P1-160: Frontend: Create SystemDesignPage (landing/list page). Landing page with unified narrative blockquote at top + 2x2 card grid. Each card: diagram thumbnail, title, subtitle. Cl
- [x] **2026-03-22** -- T-P1-161: Frontend: Create SystemDesignDetailPage (module detail template). Full-screen detail page with 8-tab navigation (Overview, Architecture, Data Flow, Formulas, Production Constraints, Trad
- [x] **2026-03-22** -- T-P1-162: Content: Module Arbitration - Content Marketplace for eBay SRP. All 8 sections for Module Arbitration. Includes production constraints (50K QPS, <10ms arbitration, 500M impressions/day
- [x] **2026-03-22** -- T-P1-163: Content: LLM Artifact Orchestration for Structured Search. All 8 sections for LLM Orchestration. Includes production constraints (7B model, P99 65ms, 99.95% availability). Defense
- [x] **2026-03-17** -- T-P2-132: Applied ML pillar (Pillar 4) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 4 leaf topics. Covers: recommender systems, search & IR, NLP & LLM applicatio
- [x] **2026-03-17** -- T-P2-133: Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs. Generate prep docs for Pillars 1, 5, 8 leaf topics. Coding: DS cheat sheets, algorithm paradigms, MLE-specific patterns.
- [x] **2026-03-19** -- T-P2-143: Forum models (ForumSeed, ForumPostLink, ForumPost) + migration v9. Create src/backend/models/forum.py with 3 SQLAlchemy models for the two-phase forum scraping workflow.

**Models:**
- Fo
- [x] **2026-03-19** -- T-P2-144: Playwright CDP attach + cookie fallback methods on PlaywrightCrawler. Extend existing src/backend/scraper/crawler.py PlaywrightCrawler class with two new async methods for fetching pages fro
- [x] **2026-03-19** -- T-P2-145: Forum HTML extractors with jammer stripping (1point3acres). Create src/backend/scraper/forum_extractors.py with BeautifulSoup-based extraction functions for 1point3acres forum page
- [x] **2026-03-22** -- T-P0-178: Ad-hoc: commit all uncommitted changes from previous sessions. ## Problem
Multiple sessions modified files without committing. Need a cleanup commit.

## Uncommitted Changes
Modified:
- [x] **2026-03-22** -- T-P0-179: Fix /api/problems 500 error (NULL priority). 2 problems had NULL priority causing Pydantic validation failure. Fixed schema, response builder, and added migration.
- [x] **2026-03-22** -- T-P0-180: Fix ruff lint errors (4x UP017 datetime.UTC). 4 auto-fixable UP017 errors in system_design.py. Run ruff check --fix. Acceptance: ruff check src/backend/ passes clean.
- [x] **2026-03-22** -- T-P1-164: Content: PBE Logging & Dataset Pipeline. All 8 sections for PBE Pipeline. Includes production constraints (500M impressions/day, 5-min micro-batch, 2TB daily). D
- [x] **2026-03-22** -- T-P1-165: Content: Ranking-as-Allocation / Diversity Allotment Policy Framework. All 8 sections for Ranking-as-Allocation (SIGNATURE PROJECT - deepest coverage). Includes production constraints (50K QP
- [x] **2026-03-22** -- T-P1-166: Fix dev.py startup race condition: wait for backend health before starting frontend. ## Problem
`scripts/dev.py` starts backend (uvicorn) and frontend (Vite) simultaneously.
Vite starts faster, browser imm
- [x] **2026-03-22** -- T-P1-167: Fix Docker nginx.conf proxy port mismatch (8000 -> 8100). ## Problem
`src/frontend/nginx.conf` has `proxy_pass http://backend:8000;` but backend runs on port 8100.
Docker deploym
- [x] **2026-03-22** -- T-P1-168: System Design: replace static screenshots with HTML-rendered diagrams. ## Problem
System design architecture diagrams are currently static JPG screenshots provided by user.
These should be re
- [x] **2026-03-22** -- T-P1-169: Diagram screenshots: crop whitespace and increase render size. ## Problem
1. HTML diagram PNGs have excessive white margins/borders
2. Diagrams render too small on the page

## Fix
1.
- [x] **2026-03-22** -- T-P1-170: Diagram click-to-fullscreen lightbox overlay. ## Problem
Diagrams on the system design page are small. User wants click-to-enlarge to fullscreen as a temporary overla
- [x] **2026-03-22** -- T-P1-171: System Design detail: single-page layout with bookmark nav + fix module-arbitration content. ## Problem
1. Tab-based layout splits content into separate views, losing context. User wants all sections on one scroll
- [x] **2026-03-22** -- T-P1-172: System Design Module 5: Database Systems Comparison (Cassandra focus). ## Goal
Add a new system design module covering database system comparison, centered on Cassandra and its competitors.


- [x] **2026-03-22** -- T-P1-173: System Design Module 6: Distributed Task Queue (failure modes, idempotency, exactly-once). ## Goal
Add a comprehensive system design module on distributed task queues, covering deep failure analysis, recovery me
- [x] **2026-03-22** -- T-P1-174: LeetCode: Blind75 tab missing sort-by controls + filter state not shared with All tab. ## Problem
1. Blind Grind75 tab does not display the sort-by dropdown that is already implemented and visible in the All
- [x] **2026-03-22** -- T-P1-175: LeetCode: Blind75 add 'All Problems' ungrouped view alongside grouped view. ## Problem
Blind Grind75 tab only shows problems grouped by pattern. User wants an "All Problems" flat list view as well
- [x] **2026-03-22** -- T-P1-176: LeetCode: Move Practice/Review actions from table to ProblemDetailPage. ## Problem
Practice and Review buttons are in the table Actions column. User cannot see the problem description/details 
- [x] **2026-03-22** -- T-P1-177: LeetCode: Add solution notes for 4 problems (K-Similar Strings, Longest Continuous Subarray, Russian Doll, Merge K Lists). ## Goal
Update 4 LeetCode problems with user-provided solution notes. Find or create these problems in the DB, then set 
- [x] **2026-03-22** -- T-P1-181: Fetch missing problem descriptions (5 problems). 5 problems (id=151-155) missing description. Fetch via POST /api/problems/fetch-all-descriptions. LeetCode GraphQL first
- [x] **2026-03-22** -- T-P1-182: Remove Review column from Problems table. Review column (next_review_at badge) adds no value currently: 0/155 problems have next_review_at set, no dedicated revie
- [x] **2026-03-22** -- T-P1-183: Framework progress: sync progress_pct with checklist state. Framework progress sync: auto-propagate status + progress upward when children change.

ADOPTED REVIEW CHANGES (6 items)
- [x] **2026-03-26** -- T-P1-190: Fix search: add backend search + match tags/pattern/notes. Add search param to GET /problems API. Server-side ILIKE across title, tags, pattern, company_tags, notes. Frontend: sen
- [x] **2026-03-26** -- T-P1-191: Fix All tab: increase page size or show all when searching. All tab uses PAGE_SIZE=20 (Problems.tsx:29). Increase to 50/100 or set limit=200 when search is active. 159 problems tot
- [x] **2026-03-26** -- T-P1-193: Batch expand Blind75 problem notes - batch 1 (14 problems). Expand notes for LC 1, 3, 11, 15, 19, 20, 21, 33, 39, 48, 49, 53, 54, 55. Each note needs: 思路, 关键技巧, 核心代码 (code block), 
- [x] **2026-03-26** -- T-P1-194: Batch expand Blind75 problem notes - batch 2 (14 problems). Expand notes for LC 56, 57, 62, 70, 73, 76, 79, 91, 98, 100, 102, 104, 105, 121. Each note needs: 思路, 关键技巧, 核心代码 (code b
- [x] **2026-03-26** -- T-P1-195: Batch expand Blind75 problem notes - batch 3 (14 problems). Expand notes for LC 124, 125, 128, 133, 139, 141, 143, 152, 153, 190, 191, 198, 200, 206. Each note needs: 思路, 关键技巧, 核心代
- [x] **2026-03-26** -- T-P1-196: Batch expand Blind75 problem notes - batch 4 (14 problems). Expand notes for LC 207, 208, 211, 213, 217, 226, 230, 235, 238, 242, 252, 253, 261, 268. Each note needs: 思路, 关键技巧, 核心代
- [x] **2026-03-26** -- T-P1-197: Batch expand Blind75 problem notes - batch 5 (14 problems). Expand notes for LC 269, 271, 295, 297, 300, 322, 323, 338, 417, 424, 435, 572, 647, 1143. Each note needs: 思路, 关键技巧, 核心
- [x] **2026-03-26** -- T-P1-198: Debug LinkedIn HR prep materials not showing in UI view. User reports LinkedIn HR call prep materials not visible in UI. Data EXISTS in DB: companies.prep_notes (448 chars), com
- [x] **2026-03-26** -- T-P1-199: Fix Interview Questions table column alignment. Columns misaligned and squeezed on Questions page. Root cause: Questions.tsx table uses default table-layout:auto. Fix: 
- [x] **2026-03-22** -- T-P2-112: SSE chunked audio streaming (if latency requires it). Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with
- [x] **2026-03-22** -- T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor. ## Summary
Modify extract_post_content() in forum_extractors.py to return all posts on page 1 (OP + all replies), not ju
- [x] **2026-03-22** -- T-P2-156: Add full_page_text column to ForumPost + migration. ## Summary
Add full_page_text Text column to ForumPost model and a schema migration.

## Context
Currently ForumPost.raw
- [x] **2026-03-22** -- T-P2-157: Wire enriched extraction into service layer + import. ## Summary
Update fetch_single_post to store full_page_text from extractor. Update import_post_to_document to prefer ful
- [x] **2026-03-27** -- T-P0-210: Adobe Prep Day1: Diffusion Models deep-dive note. Create comprehensive study note for Diffusion Models (Adobe's core tech). Content: (1) DDPM forward process with full ma
- [x] **2026-03-27** -- T-P0-211: Adobe Prep Day2: RLHF/DPO alignment + LLM distillation note. Create study note covering: (1) RLHF 3-step flow (SFT -> Reward Model -> PPO) with HTML flow diagram. (2) Bradley-Terry 
- [x] **2026-03-27** -- T-P0-212: Adobe Prep Day3: Distributed training (DP/TP/PP/FSDP) note. Create study note: (1) 4 parallelism strategies with HTML diagram showing how each splits model/data. (2) DP: full repli
- [x] **2026-03-27** -- T-P0-213: Adobe Prep Day4: RoPE + long context + video generation note. Create study note: (1) RoPE: rotation matrix formulation, theta_i formula, how q_m*k_n depends only on m-n. HTML diagram
- [x] **2026-03-27** -- T-P0-214: Adobe Prep Day5: Inference optimization + project narrative note. Create study note: (1) FlashAttention: tiled computation, SRAM vs HBM, IO complexity. (2) Quantization comparison table:
- [x] **2026-03-27** -- T-P0-215: Adobe Prep Day6: Mock interview questions + STAR-T project stories. Create study note: (1) STAR-T framework (Situation/Task/Approach/Result/Transfer) with template. (2) 3 project story out
- [x] **2026-03-27** -- T-P0-216: Adobe Prep Day7: Review checklist + concept map + error cards. Create final review note: (1) Master checklist across all 6 domains (Diffusion, RLHF/DPO, Distributed, Inference, RoPE, 
- [x] **2026-03-26** -- T-P1-200: Add Adobe phone screen event to interview timeline. Add Adobe phone screen. Company=Adobe, event_type=phone_screen, week of March 30-April 3 2026 (exact time TBD). Steps: I
- [x] **2026-03-26** -- T-P1-201: Parse staging LC file: extract problems for LinkedIn/Uber/Adobe. Parse 'LC to be added 题解.txt' (3613 lines, 1014 problems) from C:\Users\Shenghui Xu\Desktop\staging. All three companies
- [x] **2026-03-26** -- T-P1-202: Batch import parsed LC problems into DB with company tags. Import parsed problems into mle_prep.db. All 1014 tagged with LinkedIn+Uber+Adobe. (1) Existing problems (~159): merge c
- [x] **2026-03-26** -- T-P1-203: Verify imported problems: counts, tags, frequency order. Post-import verification. (1) Count problems per company tag matches 1014. (2) Spot-check first 10 and last 10 match ori
- [x] **2026-03-26** -- T-P1-204: Add real-time HH:MM:SS countdown to dashboard timeline events. Replace static countdown text (e.g. 'in 3 days') with a live ticking countdown in HH:MM:SS format. Only use hours:minute
- [x] **2026-03-26** -- T-P1-205: Add Company Frequency tab to Problems page (like Blind 75). Add a new tab 'Company Freq' (or similar) to the Problems page, at the same level as 'All Problems' and 'Blind Grind 75'
- [x] **2026-03-26** -- T-P2-188: [DEBT] MLInterviewPrep: Remove deprecated stop-cache from test_check.py. test_check.py imports and uses check_stop_cache/write_stop_cache from hook_utils.py (grep hits: hook_utils.py:129,157, t
- [x] **2026-03-26** -- T-P2-189: [DEBT] MLInterviewPrep: Add [project].dependencies to pyproject.toml. pyproject.toml has no [project].dependencies section. All main app deps (fastapi==0.109.0, sqlalchemy==2.0.25, anthropic
- [x] **2026-03-26** -- T-P2-192: Fix search persistence across tabs. Move renderSortBar() above Tabs component so search bar is shared. Search URL param already persists via useFilterParams
- [x] **2026-03-27** -- T-P0-227: Minimal StudyNoteBuilder + FormulaBlock typed constraint. Minimal viable Builder with one typed block (FormulaBlock). Design: (1) FormulaBlock dataclass: latex:str, explanation:s
- [x] **2026-03-27** -- T-P0-228: Enable rehype-raw in MarkdownPreview. Install rehype-raw and add to MarkdownPreview. (1) npm install rehype-raw. (2) MarkdownPreview.tsx: import rehypeRaw, ad
- [x] **2026-03-27** -- T-P0-229: Pilot: Rewrite Day 1 (Diffusion) end-to-end with Builder. END-TO-END PILOT to validate Builder API before scaling. Take Adobe Day 1 doc (company_documents id=5, Diffusion Models)
- [x] **2026-03-27** -- T-P0-230: Scale: Rewrite remaining 6 Adobe docs with validated Builder. After Day 1 pilot validates the Builder API, rewrite Days 2-7 (company_documents ids 6-11). For each doc: (1) Use StudyN
- [x] **2026-03-27** -- T-P0-232: Add Builder convention to CLAUDE.md + update memory. After pilot validates Builder, codify the convention. (1) CLAUDE.md Prohibited Actions: add 'Never write study note cont
- [x] **2026-03-27** -- T-P0-233: Day1 Expansion A: PE deep-dive + sinusoidal derivation + KV-Cache. Expand Day 1 note (doc id=18) with 3 new sections: (1) Positional Embedding deep-dive: absolute PE, sinusoidal PE deriva
- [x] **2026-03-27** -- T-P0-234: Day1 Expansion B: VAE details + ControlNet deep-dive + industry landscape. Expand Day 1 note with 3 more sections: (1) VAE deep-dive: encoder/decoder architecture, latent space regularization (KL
- [x] **2026-03-27** -- T-P0-235: Day1 Expansion C: Answer all checklist questions. After expansions A+B are done, answer ALL 10 existing checklist questions plus any new ones added by A+B. Format: keep t
- [x] **2026-03-27** -- T-P0-236: Rewrite Day 2 (RLHF/DPO/Distillation) to Chinese with user supplement. Replace current English Day 2 doc (company_documents id=12, 17852 chars) with comprehensive Chinese version. Source: C:\
- [x] **2026-03-27** -- T-P0-237: Rewrite Day 3 (Distributed Training) to Chinese with user supplement. Replace current English Day 3 doc (company_documents id=13, 19574 chars) with comprehensive Chinese version. Source: C:\
- [x] **2026-03-31** -- T-P0-241: Uber BPS: Seed 1p3a interview problems into DB with solutions. Parse all Uber interview problems from staging/uber题目整理.txt into the mle_prep.db problems table.

Step 1 - LeetCode prob
- [x] **2026-03-31** -- T-P0-242: Uber BPS: Create LC solutions for all Uber-tagged problems. Write Python solutions with detailed explanations for each LC problem from Uber BPS interviews. CRITICAL: Include all fo
- [x] **2026-03-31** -- T-P0-243: Uber BPS: Write solutions for custom non-LC interview problems. Detailed solutions for Uber-specific interview problems without standard LC numbers. Each solution must include: problem
- [x] **2026-03-27** -- T-P1-231: Fix PrepNotesPage tab overflow: document dropdown. Replace document tab buttons with dropdown select in PrepNotesPage.tsx. Design: Lines 156-175, replace documents?.map(Ta
- [x] **2026-03-28** -- T-P2-185: [SYNC] helixos CLAUDE.md: Add no-bare-python rule to Prohibited Actions. MLInterviewPrep CLAUDE.md Prohibited Actions has this rule (lines 62-66):

  Never use bare `python` in hook commands or
- [x] **2026-03-28** -- T-P2-209: [SYNC] Propagate template session_context db-missing warning to MLInterviewPrep. claude-code-project-template/.claude/hooks/session_context.py (lines 475-486) has a db_missing_warning feature: if .clau
- [x] **2026-03-31** -- T-P0-244: Uber BPS: Update phone screen prep doc with BPS format. Update docs/uber_phone_screen_prep.md to reflect BPS format from recruiter: 5min intro, 40-50min coding+D&A, 5min Q&A. A
- [x] **2026-03-31** -- T-P0-249: Import Uber BPS prep docs into company_documents for web UI access. Import all 7 Uber prep markdown docs (uber_bps_lc_solutions.md, uber_bps_custom_solutions.md, uber_bps_pattern_cheatshee
- [x] **2026-03-31** -- T-P0-250: Organize LinkedIn prep notes into company_documents with problem solutions. Ensure LinkedIn prep materials are properly organized in company_documents (company_id=1). Currently has docs 21-27. Che
- [x] **2026-03-31** -- T-P0-252: Condense ML Fundamentals From-Scratch guide: deduplicate code, modular design. The ML Fundamentals From-Scratch guide (Doc 27/28/29, 162K chars each; source files t1-t8, 199K total) has significant c
- [x] **2026-04-01** -- T-P0-253: Convert Uber BPS prep docs to Chinese with acronym expansion. Convert all Uber BPS prep documents to Chinese following the project's chinese_conversion_spec.md rules. Files to conver
- [x] **2026-04-01** -- T-P0-258: Fetch LC problem descriptions from leetcode.ca for all 891 missing problems. 891 of 1057 problems in mle_prep.db have no description. Create a script scripts/fetch_lc_descriptions.py that:

1. Quer
- [x] **2026-04-01** -- T-P0-262: LinkedIn: Enrich doc#26 (Question Index) with full solutions for all 47 questions. Doc#26 (LinkedIn Interview Questions Index, 30198c, 47 questions) currently has question descriptions but NO actual solu
- [x] **2026-04-01** -- T-P0-263: LinkedIn: Enrich doc#21 (Probability/Stats) with detailed solutions. Doc#21 (LinkedIn probability/statistics interview prep notes, 34594c). Review all probability and statistics questions a
- [x] **2026-04-01** -- T-P0-264: LinkedIn: Enrich doc#22 (System Design) with detailed solutions. Doc#22 (LinkedIn System Design, 32989c). Review all system design questions and ensure each has: architecture diagram de
- [x] **2026-04-01** -- T-P0-265: LinkedIn: Enrich doc#24 (ML Fundamentals + Coding) with detailed solutions. Doc#24 (LinkedIn ML Fundamentals + Coding, 33241c). Review all ML and coding questions and ensure each has: complete ans
- [x] **2026-04-01** -- T-P0-266: LinkedIn: Write solution notes for top-50 frequency problems (batch 1). Write comprehensive solution notes for the top 50 LinkedIn problems by frequency that currently lack notes.
- [x] **2026-04-07** -- T-P0-268: Uber VO prep page: 4-round onsite preparation with Chinese content. ## 目标
为Uber Virtual Onsite (VO) 创建专属面试准备页面。Uber VO包含4轮面试，每轮60分钟：
1. **Coding: Algorithms & Data Structures** -- 通用算法题，考察
- [x] **2026-03-31** -- T-P1-245: Uber BPS: Create D&A (Design and Architecture) prep document. Create docs/uber_bps_design_architecture.md: (1) Project showcase - Ranking-as-Allocation, LLM eval pipeline with high-l
- [x] **2026-03-31** -- T-P1-246: Uber BPS: KNN from-scratch + ML fundamentals review. Recruiter explicitly mentions KNN. Create: (1) KNN from scratch Python - distance metrics, k selection, weighted KNN, (2
- [x] **2026-03-31** -- T-P1-247: Uber BPS: Problem pattern cheat sheet by algorithm. Create docs/uber_bps_pattern_cheatsheet.md organizing problems by pattern: BFS/DFS (994,1020,1197,230,337,549,987,2791,5
- [x] **2026-04-01** -- T-P1-251: Add company-filtered Notes tab to Problems page for quick solution access. On the Problems page, when filtering by company (e.g. Uber or LinkedIn in Company Freq tab), users should be able to qui
- [x] **2026-04-04** -- T-P1-267: Story Map page: project arc narrative with Chinese dedup view. ## Goal
Add a new tab 'Story Map' to BehavioralQuestions page, appearing to the right of Coverage. The page organizes al
- [x] **2026-04-07** -- T-P1-269: StoryMap: fix expanded card losing arc background color. Bug: In StoryMapView.tsx ArcExampleCard, the card sits inside an ArcSection that already has colors.bg (e.g. bg-blue-50)
- [x] **2026-04-07** -- T-P1-270: StoryMap: add hover link on card title to navigate to full example. Problem: Story Map cards only show truncated text (situation.slice(0,300) + '...' on line 119). There is no way to navig
- [x] **2026-04-07** -- T-P1-271: Behavioral: Slide-over drawer for example detail (drill-down-and-return). Add a right-side slide-over drawer to the Behavioral page so users can view full STAR example content without leaving th
- [x] **2026-04-07** -- T-P1-272: System Design: Translate 8 modules to Chinese (preserve terms + acronym expansion). Parent planning task -- split into T-P1-273 through T-P1-277 for execution
- [x] **2026-04-02** -- T-P2-186: [SYNC] Propagate ruff version-drift lesson to helixos. MLInterviewPrep LESSONS.md has [2026-03-02] lesson about ruff version drift between local and CI (loose pin + separate i
- [x] **2026-04-02** -- T-P2-206: [SYNC] Propagate 2 universal lessons to helixos LESSONS.md. helixos/LESSONS.md is missing 2 universal lessons already in the template:
1. [2026-03-02] Ruff version drift between lo
- [x] **2026-03-31** -- T-P2-240: [DEBT] MLInterviewPrep: Add _temp*.json pattern to .gitignore. `_temp_docs.json` is untracked in MLInterviewPrep and not in .gitignore. These files appear to be temp artifacts from co
- [x] **2026-03-31** -- T-P2-248: Uber BPS: Create timed mock interview problem sets. 3 mock BPS sets simulating 45min coding. Each: 1 medium + 1 medium/hard with follow-ups. Set 1: LC 230 variant + Rider C
- [x] **2026-04-01** -- T-P2-256: [DEBT] MLInterviewPrep: Remove stale scripts/git-hooks/ path from CLAUDE.md. CLAUDE.md File Structure section references scripts/git-hooks/ as a directory but only scripts/pre-commit exists (no git
- [x] **2026-04-08** -- T-P0-280: System design depth: llm-orchestration expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_llm_orchestration.py. (2) NE
- [x] **2026-04-08** -- T-P0-281: System design depth: ranking-allocation supplement. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ranking_allocation.py. (2) N
- [x] **2026-04-08** -- T-P0-290: Restructure System Design landing page with sub-sections (eBay Projects + Interview Prep). The current System Design landing page (SystemDesignList.tsx) only shows eBay project modules. The user needs it restruc
- [x] **2026-04-08** -- T-P0-291: SD Interview Prep Batch 1: URL Shortener, Rate Limiter, Notification System. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-08** -- T-P0-292: SD Interview Prep Batch 2: Ride-sharing (Uber), Proximity Service (Yelp), Real-time Leaderboard. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-08** -- T-P0-293: SD Interview Prep Batch 3: News Feed/Instagram, Chat System, Facebook Live Comments. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-07** -- T-P1-273: System Design Translation Batch 1: modules 7+8 (24K chars). Translate modules vibe-code-engineering-patterns (10K) and ml-system-design-patterns (14K) to Chinese. DB: data/mle_prep
- [x] **2026-04-07** -- T-P1-274: System Design Translation Batch 2: modules 1+2 (36K chars). Translate modules module-arbitration (20K) and llm-orchestration (16K) to Chinese. DB: data/mle_prep.db table system_des
- [x] **2026-04-07** -- T-P1-275: System Design Translation Batch 3: modules 3+4 (55K chars). Translate modules pbe-pipeline (21K) and ranking-allocation (34K) to Chinese. DB: data/mle_prep.db table system_designs.
- [x] **2026-04-07** -- T-P1-276: System Design Translation Batch 4: module 5 (36K chars). Translate module database-comparison (36K) to Chinese. DB: data/mle_prep.db table system_designs slug=database-compariso
- [x] **2026-04-07** -- T-P1-277: System Design Translation Batch 5: module 6 (41K chars). Translate module distributed-task-queue (41K) to Chinese. DB: data/mle_prep.db table system_designs slug=distributed-tas
- [x] **2026-04-08** -- T-P1-282: System design depth: distributed-task-queue add Defense Q&A. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_distributed_task_queue.py. (
- [x] **2026-04-08** -- T-P1-283: System design depth: database-comparison supplement. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_database_comparison.py. (2) 
- [x] **2026-04-08** -- T-P1-284: System design depth: pbe-pipeline expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_pbe_pipeline.py. (2) NEVER o
- [x] **2026-04-08** -- T-P1-288: Create HTML diagrams + PNG screenshots for vibe-code-engineering and ml-system-design-patterns. Two system design modules (vibe-code-engineering-patterns, ml-system-design-patterns) have diagram_filename set in DB bu
- [x] **2026-04-08** -- T-P1-289: Replace top bookmark nav with persistent right-side TOC in SystemDesignDetail. SystemDesignDetail.tsx currently uses a sticky top bookmark nav bar for section navigation. After clicking a section, th
- [x] **2026-04-08** -- T-P1-294: SD Interview Prep Batch 4: Search Autocomplete, Top-K Heavy Hitters, Ad Click Aggregator. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-08** -- T-P1-295: SD Interview Prep Batch 5: YouTube/Netflix, Dropbox/Google Drive, Price Drop Tracker. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-08** -- T-P1-296: SD Interview Prep Batch 6: Leetcode Judge, Ticketmaster, Web Crawler, Auction System, Distributed Cache. CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserve
- [x] **2026-04-08** -- T-P1-297: SD Interview Prep: Update landing page with all 20 topics + category grouping. After all 6 content batches are done, update SystemDesignList.tsx to:

1. Replace hardcoded INTERVIEW_TOPICS with dynami
- [x] **2026-04-08** -- T-P2-257: [DEBT] MLInterviewPrep: Remove unused check_stop_cache/write_stop_cache from hook_utils.py. hook_utils.py defines check_stop_cache() and write_stop_cache() (lines 129-170) but no hook file imports or calls them. 
- [x] **2026-04-08** -- T-P0-298: SD Prep: Design a URL Shortener. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-299: SD Prep: Design a Rate Limiter. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-300: SD Prep: Design a Notification System. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-301: SD Prep: Design a Ride-sharing System (Uber). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-302: SD Prep: Design a Proximity Service (Yelp). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-303: SD Prep: Design a Real-time Game Leaderboard. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-304: SD Prep: Design a News Feed (Instagram). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-305: SD Prep: Design a Chat System (Messenger/WhatsApp). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-306: SD Prep: Design Facebook Live Comments. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-307: SD Prep: Design Search Autocomplete. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-308: SD Prep: Design Top-K Heavy Hitters. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-309: SD Prep: Design an Ad Click Aggregator. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-310: SD Prep: Design YouTube/Netflix Video Streaming. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-311: SD Prep: Design Dropbox/Google Drive. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-312: SD Prep: Design a Price Drop Tracker (CamelCamelCamel). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-313: SD Prep: Design an Online Judge (Leetcode). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-09** -- T-P0-325: DoorDash ML Domain prep: RecSys architecture + Retrieval deep dive. Create comprehensive prep doc covering: (1) Multi-Stage RecSys Pipeline (Retrieval->PreRanking->Ranking->ReRanking) with
- [x] **2026-04-09** -- T-P0-326: DoorDash ML Domain prep: Ranking models + Multi-Task Learning deep dive. Create comprehensive prep doc: (1) Wide&Deep/DeepFM/DCN/DCNv2/xDeepFM/AutoInt comparison. (2) MTL: Shared-Bottom, MMoE, 
- [x] **2026-04-09** -- T-P0-327: DoorDash ML Domain prep: Feature engineering + DL modules for RecSys. Create prep doc: (1) Four feature categories with DoorDash mapping. (2) Embedding: ID, hashing trick, sequence (Transfor
- [x] **2026-04-09** -- T-P0-328: DoorDash ML Domain prep: Search + semantic matching + bias/debiasing. Create prep doc: (1) Query Understanding: intent classification, query rewriting, NER, query expansion. (2) Semantic mat
- [x] **2026-04-09** -- T-P0-329: DoorDash ML Domain prep: ML fundamentals rapid review + quick-fire Q&A. Create prep doc for ML fundamentals interspersed during domain interview: (1) Optimization: SGD/Adam/AdaGrad, LR schedul
- [x] **2026-04-09** -- T-P0-335: Stop hook: replace tsc --noEmit with npm run build. In .claude/hooks/test_check.py, replace the TypeScript check (tsc --noEmit) with 'npm run build' (which runs tsc -b && v
- [x] **2026-04-08** -- T-P1-314: SD Prep: Design Ticketmaster / Hotel Reservation. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-315: SD Prep: Design a Web Crawler. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-316: SD Prep: Design an Auction System (eBay). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-317: SD Prep: Design a Distributed Cache. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P2-278: [SYNC] Propagate SQLite naive-datetime timezone lesson to helixos. Propagate MLInterviewPrep LESSONS.md entry [2026-04-07] to helixos/LESSONS.md.

Lesson summary: SQLite strips TZ info fr
- [x] **2026-04-08** -- T-P2-279: [SYNC] Propagate DB-only content recovery lesson to template. Propagate MLInterviewPrep LESSONS.md entry [2026-04-08] to claude-code-project-template/LESSONS.md.

Lesson summary: Con
- [x] **2026-04-08** -- T-P2-285: System design depth: vibe-code-engineering restructure. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_vibe_code_engineering.py. (2
- [x] **2026-04-08** -- T-P2-286: System design depth: ml-system-design-patterns expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ml_system_design_patterns.py
- [x] **2026-04-08** -- T-P2-287: System design formula audit: all modules. CRITICAL SAFETY RULES: (1) NEVER run any module seed script unless fixing that specific module. (2) NEVER overwrite Chin
- [x] **2026-04-08** -- T-P2-318: SD Prep: Update landing page with all topics + category grouping. After all 20 content tasks are done, update SystemDesignList.tsx Interview Prep tab:

1. Replace hardcoded INTERVIEW_TOP
- [x] **2026-04-09** -- T-P0-336: Smoke check: DOM assertions + API verification script. Create scripts/smoke_check.py: (1) Check dev server is running (localhost:5173 + localhost:8100). (2) Playwright opens e
- [x] **2026-04-09** -- T-P0-337: CLAUDE.md: add production-path validation rules. Add two hard rules to CLAUDE.md: (1) Side-effect verification must go through the consumer, not the producer. After DB s
- [x] **2026-04-09** -- T-P1-330: DoorDash ML Domain prep: LLM+RecSys frontiers + cross-vertical transfer. Create prep doc: (1) DoorDash LLM+RecSys: cross-vertical feature gen, Hierarchical RAG, Familiarity+Affordability+Novelt
- [x] **2026-04-09** -- T-P1-331: DoorDash ML Domain prep: Case study mock answers + SCOPE templates. Create prep doc with interview-ready answers: (1) 5 classic case studies with full SCOPE framework (restaurant recommend
- [x] **2026-04-09** -- T-P1-332: Baking Studio: compact RecipeCard UI + category grouping with captions. Redesign BakingStudio browse mode: (1) Compact RecipeCard -- reduce padding/size, make key info (name, name_zh) bold and
- [x] **2026-04-09** -- T-P1-333: Baking Studio: multi-size select (4+6 inch) with ingredient summing. Allow simultaneous selection of 4-inch and 6-inch in FilterBar/ScalingCalculator: (1) FilterBar size selector becomes to
- [x] **2026-04-09** -- T-P1-334: Baking Studio: add 3 new recipes (coconut jelly, sago, mango cream). Add 3 new preset recipes to baking_seed.py and seed into DB: (1) Coconut Milk Jelly (椰奶冻, cream_cake/cream, universal): 
- [x] **2026-04-09** -- T-P1-338: Smoke check: add screenshot archiving (no diff). Extend smoke_check.py to save a screenshot of each page to data/visual_archive/{page}_{timestamp}.png after DOM assertio
- [x] **2026-04-10** -- T-P1-339: Translate content_module_arbitration.py to Chinese + add conversion spec. Translate scripts/content_module_arbitration.py English content to Chinese preserving English tech terms (bold + first-u
- [x] **2026-04-10** -- T-P1-340: Behavioral: add story-arcs endpoint + arcs data. Add GET /behavioral/story-arcs endpoint loading docs/bq_story_arcs.json and enriching with live DB data. Add bq_story_ar
- [x] **2026-04-10** -- T-P1-341: Behavioral prep: refresh EX-01, COL-3, COL-4 stories. Rewrite EX-01 'Hacker Week' STAR story with richer content + principle tags. Rewrite COL-3/COL-4 answers with LLM-judgme
- [x] **2026-04-10** -- T-P1-342: Baking Studio: per-recipe seed guard fix and UI polish. Replace all-or-nothing baking_seed guard with per-recipe existence check. Compact RecipeCard layout with size badge + in
- [x] **2026-04-10** -- T-P1-344: Add Google and Pinterest recruiter call prep notes. Add docs/google_recruiter_call_prep.md and docs/pinterest_recruiter_call_prep.md with recruiter call preparation notes.
- [x] **2026-04-10** -- T-P1-350: Add California FTB tax call reminder to dashboard (2026-04-13). Insert a full-day interview_events row for Monday 2026-04-13: call California Franchise Tax Board to notify that the cor
- [x] **2026-04-10** -- T-P2-343: Problem model: tolerate legacy comma-separated tag strings. Add defensive try/except JSONDecodeError fallback in tags_list/company_tags_list/messages_list getters, fall back to com
- [x] **2026-04-10** -- T-P2-345: LC problem updates: _update_*.py scripts (1055, 1055v2, 2128, 815, Uber final round, SD tasks). Idempotent one-off update scripts per the _update_*.py convention: LC 1055 Pinterest tag + Chinese note, LC 1055 cleanup
- [x] **2026-04-11** -- T-P0-351: Behavioral: seed 3 failure-story placeholders EX-30/31/32 [NEEDS-INPUT: 3 failure stories]. # Behavioral: seed 3 failure-story placeholders EX-30/31/32

## Context
Audit on 2026-04-11 found only 4 of 29 behaviora
- [x] **2026-04-11** -- T-P1-352: Behavioral: add secondary example links for single-link Qs in communication/collaboration/leadership. # Behavioral: secondary links for single-link Qs in communication/collaboration/leadership

## Context
Audit 2026-04-11:
- [x] **2026-04-11** -- T-P1-353: Behavioral: seed 15-theme vocabulary, tag tables, and keyword backfill on Qs and examples. # Behavioral: 15-theme vocabulary, tag tables, keyword backfill

## Context
Audit 2026-04-11 proposed 15 themes cross-cu
- [x] **2026-04-11** -- T-P1-354: Behavioral: theme pills on question rows + frequency-sorted filter sidebar on BehavioralQuestions page. # Behavioral: theme pills + frequency-sorted filter sidebar on BehavioralQuestions page

## Context
Frontend consumer of
- [x] **2026-04-11** -- T-P1-355: Frontend: DrawerLayout single-source-of-truth responsive two-column refactor for drawer family. # Frontend: DrawerLayout single-source-of-truth responsive two-column refactor

## Context
SlideOverPanel.tsx:18 default
- [x] **2026-04-11** -- T-P1-357: Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation. # Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation paradigm shift

## Context
Source ma
- [x] **2026-04-11** -- T-P1-358: Behavioral: add cn_elevator_pitch column + seed 7 master story pitches. Add behavioral_examples.cn_elevator_pitch column + populate for the 7 polished master stories: EX-15, EX-16, EX-17, EX-3
- [x] **2026-04-11** -- T-P1-359: Behavioral API: fix /questions and /examples theme filter (returns all instead of filtered). Fix /api/behavioral/questions and /api/behavioral/examples theme filter.

ROOT CAUSE (already investigated):
The code in
- [x] **2026-04-11** -- T-P1-360: QuickIndex: add section toggle bar (LC / ML coding / BQ). Restructure src/frontend/src/pages/QuickIndex.tsx — add a top toggle bar so the user can show ONE of three sections at a
- [x] **2026-04-11** -- T-P1-361: QuickIndex BQ section: render theme cards grouped by cluster. Inside the BQ section of QuickIndex (placeholder added by T-P1-360), render the 15 behavioral_themes as cards grouped by
- [x] **2026-04-11** -- T-P1-362: BQ theme detail page: example cards with Chinese pitch + STAR drawer. New page at route /behavioral/theme/:slug for the BQ theme detail view. Add the route in src/frontend/src/App.tsx and cr
- [x] **2026-04-11** -- T-P2-321: [SYNC] helixos: Propagate 3 new lessons from MLInterviewPrep 2026-04-08. Three new MLInterviewPrep LESSONS.md entries not yet in helixos: (1) autonomous_run.sh uses sub-project task_db not root
- [x] **2026-04-10** -- T-P2-346: Seed LinkedIn/Google/Pinterest prep content. Add seed scripts for LinkedIn question index, LinkedIn problem notes insertion, Google prep content, Pinterest prep cont
- [x] **2026-04-10** -- T-P2-347: Pillar 3/6 translation and expansion scripts. Add translation + expansion scripts for the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130). Scripts generate/u
- [x] **2026-04-10** -- T-P3-348: Lint: apply ruff auto-fixes to seed/translate/fix scripts. Apply ruff auto-fixes to scripts: import reordering, removal of unused imports, f-string cleanup (no placeholders).
- [x] **2026-04-10** -- T-P3-349: Add node_content and node_translations artifacts from Chinese batch. Commit the per-node markdown artifacts generated during the pillar 3/6 Chinese conversion batch (T-P1-120..T-P1-130) for
- [x] **2026-04-11** -- T-P0-366: BQ Quick Index: generate cn_elevator_pitch batch 1 (BLOG-01 to EX-09, 14 examples). Generate high-quality Chinese elevator pitch summaries for 14 examples missing cn_elevator_pitch. Format: '{summary} | K
- [x] **2026-04-11** -- T-P0-367: BQ Quick Index: generate cn_elevator_pitch batch 2 (EX-10 to EX-33, 13 examples). Generate high-quality Chinese elevator pitch summaries for remaining 13 examples missing cn_elevator_pitch. Format: '{su
- [x] **2026-04-12** -- T-P1-368: [Pinterest/CN] Translate LC 332 notes to Chinese (Reconstruct Itinerary). Translate existing English notes (2977 chars) to Chinese. Keep code blocks, algorithm names (Hierholzer, Eulerian Path),
- [x] **2026-04-12** -- T-P1-369: [Pinterest/CN] Translate LC 465 notes to Chinese (Optimal Account Balancing). Translate existing English notes (9898 chars) to Chinese. Includes two approaches (Bitmask DP + naive DFS), Full-Transfe
- [x] **2026-04-12** -- T-P1-370: [Pinterest/CN] Translate LC 282 notes to Chinese (Expression Add Operators). Translate existing English notes (8433 chars) to Chinese. Covers Version A (brute-force + custom myEval), Version B (pre
- [x] **2026-04-12** -- T-P1-371: [Pinterest/CN] Translate LC 2402 notes to Chinese (Meeting Rooms III). Translate existing English notes (5257 chars) to Chinese. Two-heap simulation pattern. Keep code and complexity notation
- [x] **2026-04-12** -- T-P1-372: [Pinterest/CN] Translate LC 1110 notes to Chinese (Delete Nodes And Return Forest). Translate existing English notes (5361 chars) to Chinese. is_root flag + carry-state-down-vs-post-order principle. Keep 
- [x] **2026-04-12** -- T-P1-374: [Pinterest/desc] Fetch missing problem descriptions: LC 2402, 1110, 1723. Three Pinterest problems have empty description field. Use the existing fetch-description endpoint or leetcode.ca scrape
- [x] **2026-04-12** -- T-P1-375: [Pinterest/notes] Write LC 410 solution notes (Split Array Largest Sum). Pinterest must-do; no notes yet. Cover: binary-search-on-answer approach (monotonic feasibility check), DP on (i,k) alte
- [x] **2026-04-11** -- T-P2-322: [DEBT] MLInterviewPrep: Add problems.db to .gitignore. problems.db is untracked in MLInterviewPrep git repo and not in .gitignore. The .gitignore already covers interview_prep
- [x] **2026-04-11** -- T-P2-323: [DEBT] MLInterviewPrep: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: pytest, pytest-asyncio, beautifulsoup4, pyyaml, ruff, playwright. 
- [x] **2026-04-11** -- T-P2-324: [DEBT] helixos: Sync dev deps from requirements.txt to pyproject.toml. 6 packages in requirements.txt not in pyproject.toml: httpx, ruff, pytest-asyncio, mypy, pytest, pytest-timeout. Add as 
- [x] **2026-04-11** -- T-P2-356: Behavioral: semantic relevance spot-check script for 10 random Q-example links. # Behavioral: semantic relevance spot-check script for 10 random Q-example links

## Context
Audit 2026-04-11 confirmed 
- [x] **2026-04-11** -- T-P2-363: BQ navigation: end-to-end browse-path preservation across QuickIndex/theme/drawer. Audit and fix end-to-end navigation paths so user never loses browse context across QuickIndex(BQ) -> theme detail -> ex
- [x] **2026-04-11** -- T-P2-364: Behavioral failure cluster: structural polish (tags + narration guards) for EX-15/16/17/30. STRUCTURAL/MECHANICAL polish ONLY for the 4 remaining failure-cluster master stories. Brings them in line with the EX-33
- [x] **2026-04-11** -- T-P2-365: Behavioral audit: verify all technical_problem_solving examples have explicit data-driven evidence. Audit pass over the example_theme_tags rows for theme_id=technical_problem_solving (currently 27 examples). For each, re
- [x] **2026-04-12** -- T-P0-380: [BQ-rework] EX-12 Code Review Standards: add concrete metric. Flag C (vague metric). Use user-provided facts (2026-04-13 Discord): before the checklist/standards, ~80% of changes req
- [x] **2026-04-12** -- T-P0-381: [BQ-rework] EX-16 PhD Interns Notebook-to-Production: add onboarding metric. Flags A+C. Use user-provided facts (2026-04-13 Discord): 6 interns in my org adopted a similar notebook-to-production ch
- [x] **2026-04-12** -- T-P0-382: [BQ-rework] EX-19 Model Deprecation Incident: own the gap personally. Flags C+D. Use user-provided facts (2026-04-13 Discord): This was NOT a user-facing prod-model impact -- but it took 2 f
- [x] **2026-04-12** -- T-P0-383: [BQ-rework] EX-20 Cross-DC Deployment Incident: quantify blast radius. Flags A+C. Use user-provided facts (2026-04-13 Discord): Cross-DC deployment was delayed ~6 hours, blocking TWO launches
- [x] **2026-04-12** -- T-P0-384: [BQ-rework] EX-22 Pushback on Scope: add delivery-impact metric. Flags A+C+D. Target: JSON EX-18 (audit called it EX-22) "Pushing Back on Unreasonable Scope". User-provided facts (2026-
- [x] **2026-04-12** -- T-P0-385: [BQ-rework] EX-28 Explaining Allocation to VP: estimate avoided cost. Flags A+C. Target: JSON EX-24 (audit called it EX-28) "Explaining Allocation Problem to VP". User-provided facts (2026-0
- [x] **2026-04-12** -- T-P0-386: [BQ-rework] EX-33 MoE Paradigm Shift: close the arc with downstream win. Flags C+D. Target: DB `behavioral_examples` row example_id=EX-33 "MoE -> Allocation Paradigm Shift - Org-Level Reframe v
- [x] **2026-04-12** -- T-P0-397: [Pinterest/custom] Escape Room game-state (Game(rooms, people)). Pinterest coding 2025-11. Design data structure: proceedToNextRoom(pid), getTop(K), getPeople(roomId). Requirements: O(1
- [x] **2026-04-12** -- T-P0-405: [Pinterest/SD] ML SD: Design Pins Search Engine. Pinterest SD (most frequently asked 2025-11). End-to-end: (1) candidate generation (two-tower embedding, ANN/HNSW, multi
- [x] **2026-04-13** -- T-P0-406: [Pinterest/SD] ML SD: Notification Recommendation. Pinterest SD 2025-11. (1) notification triggering (when to notify), (2) content candidate generation, (3) ranking, (4) d
- [x] **2026-04-13** -- T-P0-407: [Pinterest/SD] ML SD: Pin Ranking Recommendation. Pinterest SD 2025-11. Pin ranking for home/topic feed. (1) two-stage retrieval+rerank, (2) features (pin/user/context/gr
- [x] **2026-04-12** -- T-P1-376: [Pinterest/notes] Write LC 43 solution notes (Multiply Strings). Pinterest must-do; no notes yet. Cover: digit-by-digit simulation with (i+j, i+j+1) index trick, carry propagation, lead
- [x] **2026-04-12** -- T-P1-377: [Pinterest/notes] Write LC 642 solution notes (Design Search Autocomplete System). Pinterest must-do; no notes yet. Cover: Trie + hot-words map at each node, top-k with heap, input streaming state machin
- [x] **2026-04-12** -- T-P1-378: [Pinterest/notes] Write LC 1723 solution notes (Find Minimum Time to Finish All Jobs). Pinterest must-do; no notes yet. Cover: binary search on answer + backtracking feasibility check, pruning (sort jobs des
- [x] **2026-04-12** -- T-P2-373: [Pinterest/CN] Polish mixed-language notes to full Chinese: LC 311, 815, 1244. Three existing notes are MIX (ratios 0.11-0.29). Rewrite the English prose sections to Chinese, keep code blocks and tec
- [x] **2026-04-12** -- T-P2-379: [Pinterest/index] Refresh Pinterest LC index doc after translations/fetches. After Chinese translations and missing descriptions are done, regenerate the Pinterest LC Must-Do: Review & Index compan
- [x] **2026-04-13** -- T-P0-410: [Pinterest/SD] SD: Catalog bulk update (500M records, S3+async). Pinterest SD 2025-11. Update internal downstream systems from large catalog (~500M). (1) ingestion (bulk via S3 consume;
- [x] **2026-04-13** -- T-P1-387: [BQ-sweep] Tier-2 metric補充: replace adjectives with numbers across ~12 stories. User guidance (2026-04-13 Discord): "Fill in similarly". For stories where user has not provided facts, use [TODO: confi
- [x] **2026-04-13** -- T-P1-388: [BQ-sweep] Tier-2 ownership sharpening: "we" -> "I" in Action sections. Sweep target stories: EX-2 (lead +1% GMB prominently), EX-11 (I led compression, researcher gave context), EX-13 (I flag
- [x] **2026-04-13** -- T-P1-389: [BQ-sweep] Tier-2 catch-all polish: remaining 1-weak-signal stories. Remaining Tier-2 stories not covered by metric or ownership sweeps. Primary: EX-7 (add downstream metric after unbiased 
- [x] **2026-04-13** -- T-P1-390: [Pinterest/LC] Add + notes: LC 84 Largest Rectangle in Histogram. New Pinterest problem (2025-11 cutoff). Add to problems DB with Pinterest tag; fetch description; write Chinese notes: m
- [x] **2026-04-13** -- T-P1-391: [Pinterest/LC] Add + notes: LC 392 Is Subsequence. New Pinterest problem. Two-pointer O(n+m). Follow-up: many queries -> precompute indexed char positions, binary search e
- [x] **2026-04-13** -- T-P1-392: [Pinterest/LC] Add + notes: LC 3229 Min Operations to Make Array Equal to Target. New Pinterest problem. Diff-scan greedy (same family as LC 1526). Chinese notes covering increment/decrement region hand
- [x] **2026-04-13** -- T-P1-393: [Pinterest/LC] Add + notes: LC 1526 Min Increments on Subarrays. New Pinterest problem. Diff-array + greedy sign-change pattern. Chinese notes explaining why counting positive deltas is
- [x] **2026-04-13** -- T-P1-394: [Pinterest/LC] Add + notes: LC 1564 Put Boxes Into Warehouse I. New Pinterest problem. Greedy: warehouse prefix-min + sort boxes desc. Chinese notes highlighting the prefix-min insight
- [x] **2026-04-13** -- T-P1-395: [Pinterest/LC] Add + notes: LC 1580 Put Boxes Into Warehouse II. New Pinterest problem (harder variant of 1564, enter from both ends). Chinese notes: two-pointer shortest-interior-heigh
- [x] **2026-04-13** -- T-P1-398: [Pinterest/custom] Lighthouse 2D matrix light propagation. Pinterest coding 2025-11. 2D matrix simulation of light propagation. Resolve exact variant from dump (light rays + mirro
- [x] **2026-04-13** -- T-P1-399: [Pinterest/custom] Prefix-match first-word-index. Pinterest coding 2025-11: given ['a','apple','appz','b'] and prefix ['ap'], return index of first word containing prefix
- [x] **2026-04-13** -- T-P1-400: [Pinterest/custom] Grant Access permission propagation. Pinterest coding 2025-11. Problem linked at hack2hire.com (URL in dump). Research and document: likely DAG/graph permiss
- [x] **2026-04-13** -- T-P1-401: [Pinterest/custom] Pin Connectivity. Pinterest coding 2025-11. Graph connectivity problem on pin/board/user graph. Research variant, write canonical (Union-F
- [x] **2026-04-13** -- T-P1-402: [Pinterest/custom] round() from scratch (string input). Pinterest coding 2025-11. Implement round() given string s without using float(). Edge cases: float overflow, '-.2', '2.
- [x] **2026-04-13** -- T-P1-403: [Pinterest/custom] Round string s by precision p. Pinterest coding 2025-11 follow-up. Round s by precision p. Examples: s='12567',p='100'->'12600'; s='1234.678',p='0.1'->
- [x] **2026-04-14** -- T-P0-414: Fix 4 failing CI checks (test/lint/emoji/migration). Migration _add_column_if_missing skipped; 3 ruff errors fixed; 17 emoji replaced with ASCII tags; 32 migration tests now
- [x] **2026-04-14** -- T-P0-429: [Google/R2] G&L top-20 common questions × bq_improved_stories 映射 audit (HR 建议). HR source: 'you can anticipate 90%... top 20 questions, 3 answers for each, detailed and data-driven'. AC: (1) 列出 top 20
- [x] **2026-04-14** -- T-P0-430: [Google R1] Regularization 全景合并深挖 note (company_id=3). Gap: staging 零散提了 L2/dropout/AdamW, 但用户明确点名要合并深挖. Deliverable: docs/google_regularization_deep_dive.md, ingest as compan
- [x] **2026-04-14** -- T-P0-431: [Google R1] Bias/Variance + 过拟合诊断 drill note (company_id=3). 用户点名必须操练到位. Deliverable: docs/google_bias_variance_drill.md, ingest company_documents (company_id=3). AC: (1) 默写 E_D[(y-
- [x] **2026-04-14** -- T-P0-432: [Google R1] Staging 13 题 2-min 口头答复本 (company_id=3). 把 staging/04_14_ML问题深入拷打.md 13 题压缩成问答卡. Deliverable: docs/google_staging_13_flashcards.md, ingest company_documents (com
- [x] **2026-04-14** -- T-P0-433: [Google R2] G&L top-20 common questions × 6 polished stories 映射 audit. HR 明建议: top 20 questions × 3 answers each. Deliverable: update docs/bq_todo_tracker.md + append section to company_docum
- [x] **2026-04-14** -- T-P0-434: [LC] 攻下 85 Maximal Rectangle + 写中文笔记. LC 85 未完成, 用户明确点名考核重点. AC: (1) solve 一次不 peek; (2) 核心解法 = 每行转 histogram, heights[j]+=1 若'1' else 0, 跑 LC 84 单调栈; (3) 时间 
- [x] **2026-04-14** -- T-P0-435: [LC] K-largest heap/quickselect 家族 drill: 703 + 973 + 378. 三题都未完成, 用户点名 K-largest/sketch 方向必须 drill. AC 三题各自: (A) LC 703 Kth Largest in Stream — min-heap size k 核心模板, add() O(log 
- [x] **2026-04-14** -- T-P0-436: [LC/Pinterest] Sketch/Streaming 理论 1-pager (company_id=29). 用户明确说 K-largest 要结合 sketch 做法. Deliverable: docs/pinterest_sketch_streaming_1pager.md, ingest company_documents (company
- [x] **2026-04-13** -- T-P1-404: [Pinterest/custom] LC 332 loop follow-up addendum. Pinterest coding 2025-11 follow-up to LC 332: what if tickets form a cycle? Explain Hierholzer already handles Eulerian 
- [x] **2026-04-13** -- T-P1-408: [Pinterest/SD] SD: Ad CTR prediction. Pinterest SD 2025-11. (1) data pipeline (impressions/clicks with attribution), (2) feature engineering (user/ad/context 
- [x] **2026-04-13** -- T-P1-409: [Pinterest/SD] SD: User & Item Embeddings. Pinterest SD 2025-11. (1) objective (self-supervised contrastive / supervised from engagement), (2) encoder (towers, use
- [x] **2026-04-13** -- T-P1-411: [Pinterest/SD] ML SD: Personalized Chat Bot Recommending Pins. Pinterest SD 2025-11. (1) conversation understanding (LLM multi-turn state), (2) intent classification (ask-pins vs chit
- [x] **2026-04-13** -- T-P1-412: [Pinterest/BQ] Map Pinterest BQ questions to existing stories. Pinterest BQ (2025-11): (1) project led end-to-end, (2) where requirement came from, (3) stepping ahead when not respons
- [x] **2026-04-13** -- T-P2-396: [Pinterest/LC] Investigate + notes: 寻找餐馆区间. Pinterest dump 2025-11 mentions this with no LC number. Research to identify the actual LC mapping (candidates: LC 1779 
- [x] **2026-04-13** -- T-P2-413: [Pinterest/integration] Enrich Pinterest index doc with new sections. Final integration after all new LC/custom/SD content lands. Refresh company_documents id=47 to include: (1) new LC secti
- [x] **2026-04-15** -- T-P0-415: [Google/R1] LambdaRank/LambdaMART 推导 + pointwise/pairwise/listwise 对比自测. Gap vs staging 13: staging 无 ranking loss 推导. Round1 必考. AC: (1) 默写 RankNet pairwise sigmoid loss; (2) LambdaRank 如何用 de
- [x] **2026-04-15** -- T-P0-416: [Google/R1] NDCG/MAP/MRR 定义 + position bias 拷打自测. Gap: staging 只讲 ROC/PR. AC: (1) 默写 DCG=Σ(2^rel-1)/log2(i+1), NDCG=DCG/IDCG; (2) 为什么 MAP 不适合 graded relevance; (3) positi
- [x] **2026-04-15** -- T-P0-417: [Google/R1] Calibration 三法 (Platt/Isotonic/Temperature) + GMB bidding 校准陷阱. Gap: staging 没提. Round1 recruiter 明列. AC: (1) Platt=logistic over logit; (2) Isotonic preserve ranking 粒度粗; (3) Temperat
- [x] **2026-04-15** -- T-P0-418: [Google/R1] IPS/counterfactual eval/去偏 NDCG (SIGIR paper talking points). Gap: staging 无. SIGIR paper 必问. AC: (1) IPS 重加权 1/P(shown); (2) examination hypothesis P(click)=P(exam)·P(rel); (3) SNIP
- [x] **2026-04-15** -- T-P0-419: [Google/R1] Two-tower retrieval 深挖 (超越 InfoNCE 基础). staging 11 覆盖 InfoNCE 但缺系统级. AC: (1) 为什么两塔 (query 塔不看 doc 侧 → offline index); (2) negative sampling 四种 + failure mode; (
- [x] **2026-04-15** -- T-P0-420: [Google/R1] Multi-objective ranking: DPP/MMR + Etsy diversity 故事机制. Etsy diversity 必被追问机制. AC: (1) MMR = λ·rel-(1-λ)·max_sim; (2) DPP 用 det(L_S) 同时 model rel(对角) + diversity(非对角); (3) inte
- [x] **2026-04-15** -- T-P0-424: [Slack-SFDC] HR call Wed 2026-04-15 14:00 EST = 11:00 PT. Slack (Salesforce) ML team recruiter call. 时间: 04/15 Wed 14:00 EST = 13:00 CST = 11:00 PT. 30-45 min 预期. 准备: (1) 自我介绍 90
- [x] **2026-04-16** -- T-P0-445: [ML-Fund] Cost-sensitive model selection: FP/FN decision rubric + Pinterest/Google examples. Gap: when two models have near-equal accuracy/AUC, how to choose. Steps: (1) quantify FP vs FN business cost; (2) pick o
- [x] **2026-04-16** -- T-P0-446: [ML-Fund] Logistic regression coefficient interpretation: odds ratio for categorical + boolean variables. Gap: typical Google/LinkedIn screen: 'LR coef 0.7 on one-hot vs reference -- what does it mean?'. Cover: (a) continuous 
- [x] **2026-04-16** -- T-P0-447: [ML-Fund] Bagging vs Boosting decision rubric + XGBoost/LightGBM mechanics. Gap: (1) when bagging (high variance, stable base learner) vs boosting (high bias, weak learner). (2) XGBoost core: 2nd-
- [x] **2026-04-16** -- T-P1-421: [Google/R1] A/B test 严谨性: sample size/SRM/CUPED/novelty. pillar7 有基础但缺 drill. AC: (1) n=(z+z)^2·2σ²/Δ²; (2) SRM 是 randomization 健康性不是结果; (3) CUPED 用 pre-period covariate 降 varia
- [x] **2026-04-15** -- T-P1-440: Pinterest card index: backend + data prep. # Pinterest Card Index: Backend + Data Prep (T-P1-224)

## Goal
Seed a `card_index` document for Pinterest (company_id=2
- [x] **2026-04-15** -- T-P1-441: Pinterest card index: frontend CardGrid component. # Pinterest Card Index: Frontend CardGrid Component (T-P1-225)

## Goal
Create `CompanyCardIndex.tsx` that fetches the c
- [x] **2026-04-15** -- T-P1-442: Pinterest card index: integrate tab=index into PrepNotesPage. # Pinterest Card Index: Integrate tab=index into PrepNotesPage (T-P1-226)

## Goal
Add a new `tab=index` to PrepNotesPag
- [x] **2026-04-15** -- T-P1-443: Problems tab: Custom badge + source-type filter switch. # Problems tab: Custom badge + source-type filter (T-ML-xxx)

## Goal
Make custom (non-LC) problems visually distinct in
- [x] **2026-04-15** -- T-P1-444: Problems tab: Custom-mode company-grouped view. # Problems tab: Custom-mode company-grouped view (T-ML-xxx)

## Goal
When the user switches to `source_type=custom`, ren
- [x] **2026-04-16** -- T-P0-448: [ML-Fund] Classical model pitches: KNN / Naive Bayes / K-Means / DBSCAN when-to-use. Gap: node 71 Clustering stub + no NB/KNN nodes. Pitch-format 1-pager: per model -> (what / assumption / when use / when 
- [x] **2026-04-16** -- T-P0-449: [DL-Fund] Activation functions unified: ReLU/LeakyReLU/Sigmoid/Tanh/Softmax when and why. Gap: no standalone activation-functions node. Single comparison table: {activation, range, derivative, vanishing-grad ri
- [x] **2026-04-16** -- T-P0-450: [DL-Fund] Optimizer family: SGD -> Momentum -> AdaGrad -> RMSProp -> Adam derivation chain. Gap: node 74 Gradient Descent Family is stub (141b). Existing study note source: data/t8_optimizers.md (port into DB). C
- [x] **2026-04-16** -- T-P0-451: [DL-Fund] DL training pitfalls 1-pager: Focal loss + BatchNorm/LayerNorm + vanishing/exploding gradients. Gap: three scattered pitfall topics consolidated. (1) Focal loss: alpha/gamma, class imbalance, when NOT to use (already
- [x] **2026-04-16** -- T-P0-452: [Meta-Cleanup] Sketch family unification: 3-axis view + terminology grounding across sketch docs. User-flagged: compact-DS content (CMS/HLL/SS/Bloom) duplicated across framework_nodes 196/197/103 + Pinterest doc 58, ea
- [x] **2026-04-16** -- T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold. AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs
- [x] **2026-04-16** -- T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打. AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 s
- [x] **2026-04-16** -- T-P1-453: [Pinterest-CV] CNN foundation 1-pager: conv mechanics + ResNet/VGG/EfficientNet + transfer learning + data aug. Gap: Pinterest is visual-content-first, but CV framework_nodes 122/123 are shallow (5733b+6231b). (1) Conv op: stride/pa
- [x] **2026-04-16** -- T-P1-454: [Pinterest-NLP] Word2Vec/GloVe history + ViT + cross-modal attention supplement. Gap: pre-transformer embedding history missing entirely; node 164 (Vision-Language Models) covers CLIP/LLaVA shallowly b
- [x] **2026-04-16** -- T-P1-455: [Pinterest-RecSys] Cold-start strategies: user + item + pin bootstrap. Gap: cold-start absent from pillar4.recommender_systems nodes (108/109/110 cover CF/content-based/deep but not cold-star
- [x] **2026-04-16** -- T-P1-456: [ML-RecSys] Matrix factorization: SGD vs ALS + bridge from CF to embedding models. Gap: node 108 (Collaborative Filtering) covers CF concept but not the MF mechanics bridging CF -> Two-Tower. (1) Bias-on
- [x] **2026-04-16** -- T-P1-457: [Phase 0.5b] Template v1.1 post-Sketch revision: drawer tab render order + Optimization granularity example. DEFERRED revision of Phase 0.5 content template after T-P0-241 Sketch sample ships real-world signal. Per independent re
- [x] **2026-04-16** -- T-P1-461: [adhoc] LC 815 follow-up: station-level shortest path section. Append follow-up to LC 815 notes: min-stops variant via station-level BFS / Dijkstra. Idempotent script with sentinel gu
- [x] **2026-04-16** -- T-P1-462: [QIdx-A1] Backfill family on 11 ungrouped LC_PROBLEMS. BACKFILL family on 11 LC problems whose cards currently render in the label-less flat grid at the bottom of QuickIndex L
- [x] **2026-04-16** -- T-P1-463: [QIdx-A2] QuickIndex.tsx: dynamic family-based grouping. REFACTOR src/frontend/src/pages/QuickIndex.tsx to render LC problems grouped by family, eliminating the current label-le
- [x] **2026-04-16** -- T-P2-437: [SYNC] Propagate 4 new MLInterviewPrep lessons to helixos LESSONS.md. 4 lessons from MLInterviewPrep (2026-04-10 to 2026-04-15) not yet in helixos LESSONS.md. All apply to helixos. (1) 2026-
- [x] **2026-04-16** -- T-P0-470: [KG-P1-01] Create concept_links table + migration. Create new table `concept_links` in data/mle_prep.db for structured cross-references between concepts (framework_nodes) 
- [x] **2026-04-16** -- T-P0-471: [KG-P1-02] Deploy doc_kind taxonomy: canonical_hub / composition / drill. Current `company_documents.doc_kind` CHECK accepts: prep_note, hub_doc, card_index. KG design calls for richer taxonomy:
- [x] **2026-04-16** -- T-P0-472: [KG-P1-03] Markdown '正典' (canonical) link convention + POC patch on 2 framework_nodes. Establish canonical cross-ref syntax so future docs link to framework_nodes uniformly, enabling future scraping into con
- [x] **2026-04-16** -- T-P0-473: [KG-P2-01] Consolidate Bias-Variance as canonical_hub (Google doc 56 + node). Phase 2 first real canonical hub. Target: unify the Bias-Variance treatment into ONE framework_node as canonical authori
- [x] **2026-04-16** -- T-P0-474: [KG-P2-02] Consolidate Regularization as second canonical_hub (extends node 195). Phase 2 second canonical hub. User-picked (over Optimizer / Class Imbalance / Eval Metrics). Target: unify Regularizatio
- [x] **2026-04-16** -- T-P0-476: [KG-M-00] Generate per-concept coverage checklist (human review format) for 合集 docs 19/21/22/27. FIRST step of 合集 migration. Per user instruction, we do NOT auto-deprecate. Produce a per-doc, per-concept checklist so 
- [x] **2026-04-16** -- T-P0-477: [KG-M-01] CRITICAL: Migrate Doc 19 Diffusion Models (sole source) to framework_node + standalone. Doc 19 'Adobe MLE Prep All-in-One' contains Diffusion Models content (DDPM, DDIM, CFG, CLIP, SDE/ODE) that prior audit f
- [x] **2026-04-16** -- T-P0-478: [KG-M-02] CRITICAL: Migrate Doc 19 RoPE + Long Context (sole source) to framework_node. Sibling of KG-M-01. Doc 19 RoPE + Long Context section is sole source.

SCOPE: Same pattern as KG-M-01 but for RoPE / lo
- [x] **2026-04-16** -- T-P0-480: [DOCS-01] Write docs/ filing convention proposal (no file moves yet). Prior audit: docs/ has 365 files, 6 content categories mixed together, 3 mess examples. Propose a 6-subdir convention be
- [x] **2026-04-16** -- T-P1-464: [QIdx-B1] LC 895 Maximum Frequency Stack: Chinese solution notes. Write Chinese solution notes for LC 895 Maximum Frequency Stack and mark completed.

CURRENT STATE (verified via DB quer
- [x] **2026-04-16** -- T-P1-465: [QIdx-B2] LC 1146 Snapshot Array: Chinese solution notes. Write Chinese solution notes for LC 1146 Snapshot Array and mark completed.

CURRENT STATE (verified): leetcode_id=1146,
- [x] **2026-04-16** -- T-P1-466: [QIdx-B3] LC 1825 Finding MK Average: Chinese solution notes. Write Chinese solution notes for LC 1825 Finding MK Average and mark completed.

CURRENT STATE: leetcode_id=1825, family
- [x] **2026-04-16** -- T-P1-467: [QIdx-B4] LC 1845 Seat Reservation Manager: Chinese solution notes. Write Chinese solution notes for LC 1845 Seat Reservation Manager and mark completed.

CURRENT STATE (verified): leetcod
- [x] **2026-04-16** -- T-P1-468: [QIdx-B5] LC 362 Design Hit Counter: expand notes. Expand thin notes for LC 362 Design Hit Counter to full solution + mark completed.

CURRENT STATE: leetcode_id=362, fami
- [x] **2026-04-16** -- T-P1-479: [KG-M-03] Delete Doc 29 Adobe ML Fundamentals (byte-identical duplicate of Doc 28). Prior audit confirmed doc 29 (Adobe) and doc 28 (Uber) both titled 'ML Fundamentals From-Scratch' are 151,774 chars each
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-17** -- T-P0-484: [KG-VIZ-R01] React Flow + ELK.js LR mind-map + incremental layout + URL state. FULL REWRITE of /kg. Remove Cytoscape.js, adopt React Flow + ELK.js for LR mind-map.

## Core Architecture Decisions (us
- [x] **2026-04-17** -- T-P0-485: [KG-VIZ-R02] Visual encoding: palette + importance/completeness indicators + polish. Visual design pass after R01 migration. Adds information-dense encoding beyond just pillar color.

## Pillar Color Palet
- [x] **2026-04-17** -- T-P0-487: KG-UX-01: Restore pan-drag and add Controls panel. Canvas is unpannable after zoom. Fix: panOnDrag=true, panOnScroll=false, zoomOnScroll=true. Add <Controls> (zoom in/out/
- [x] **2026-04-17** -- T-P0-488: KG-UX-02: Preserve focus on expand/collapse (setCenter). Clicking expand reshuffles layout and user loses focus on the clicked node. Fix: after layoutAll(), if a node was just a
- [x] **2026-04-17** -- T-P0-489: KG-UX-03: Multi-line titles, wider nodes, bigger fonts. Titles up to 82 chars get truncated. Fix: line-clamp-2, wider boxes, larger fonts.

Files: src/frontend/src/components/k
- [x] **2026-04-17** -- T-P0-495: KG-UX-07: Limit pan range (translateExtent) + zoom bounds. Pan range is unlimited; user can drag canvas into empty space far outside graph bbox. Fix: compute bbox from all cached 
- [x] **2026-04-17** -- T-P0-496: KG-UX-08: Left TreeNav panel (3-level, replaces pillar badges). Current top-header pillar badges all call expandAll() - functionally useless. Replace with a left-side collapsible TreeN
- [x] **2026-04-16** -- T-P1-475: [KG-G-01] Translate 11 Google R1 drill docs to Chinese (company_documents 55,56,60-65,67-69). Target 11 drill docs currently in English (or largely English with some Chinese tech terms). User wants Chinese-first pr
- [x] **2026-04-16** -- T-P1-481: [DOCS-02] Migrate top-level company prep files to docs/company/<slug>/. Per proposed convention (DOCS-01), move 34 top-level company prep files into docs/company/<slug>/ subdirs.

SCOPE (verif
- [x] **2026-04-16** -- T-P1-482: [DOCS-03] Move intermediate / generated / audits / synced into docs/staging/. Per DOCS-01 convention, move 274 generated system design fragments + audits/ + synced/ + analysis/ into docs/staging/ wi
- [x] **2026-04-16** -- T-P1-483: [KG-VIZ-01] /kg visualization POC: Cytoscape.js + dagre (user-picked). User-picked Cytoscape.js (over React Flow / D3-Force / Sigma / vis-network). POC scope below.

DEPENDENCIES TO ADD (src/
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-469: [QIdx-C1] Harden LC import scripts to set family. Harden LC import scripts so new rows no longer default to family=NULL silently.

BACKGROUND: Current pipeline adds LC pr
- [x] **2026-04-17** -- T-P0-497: KG-UX-09: TreeNav click -> expand ancestors + setCenter on canvas. Wire TreeNav (KG-UX-08) to the canvas. Clicking an entry in TreeNav should: (1) setExpanded to include all ancestors of 
- [x] **2026-04-18** -- T-P0-510: T-MLSD-FRAMEWORK-01: Populate id=18 'System Design Framework' with canonical L5 paradigm. ## Context
id=18 "System Design Framework" in framework_nodes has description=NULL. It's the L2 category under Pillar 3 
- [x] **2026-04-17** -- T-P1-486: [KG-VIZ-R03] Interaction: tooltip, keyboard a11y, expand-all, hover edge highlight. Post-polish interaction refinements. Scoped per user review (cut edge legend toggle, pillar filter buttons, +/-/0 shortc
- [x] **2026-04-17** -- T-P1-490: KG-UX-04: 0-children categories act as leaves; stub badge. 7 depth-1 categories (SQL Fundamentals, OOD SOLID, Diffusion Models, etc.) have 0 children. Expanding them does nothing 
- [x] **2026-04-17** -- T-P1-491: KG-UX-05: Swimlane layout - per-pillar ELK vertically stacked. Current layered layout stacks 8 pillars in leftmost column causing cross-pillar overlap and visual chaos. Refactor to sw
- [x] **2026-04-17** -- T-P1-498: KG-CN-01: Rewrite node descriptions to CN narration + full English terms. Rewrite framework_nodes.description to Chinese narration + English full-expansion terms. Pilot on 4 nodes validated qual
- [x] **2026-04-18** -- T-P1-499: [SYNC] Fix settings.json: replace bare python with /c/Anaconda/python.exe. All 8 hook commands in .claude/settings.json use bare python instead of /c/Anaconda/python.exe. This violates the CLAUDE
- [x] **2026-04-18** -- T-P1-501: KG-UX-10: Empty-content nodes skip drawer (tri-state click) + hasContent util. ## Problem
Clicking L1/L2 organizational nodes (e.g. id=1 Coding & Algorithms) opens an empty drawer because the current
- [x] **2026-04-18** -- T-P1-502: KG-UX-14: Initial fitView maxZoom cap + URL deeplink direct-focus. ## Problem
User reports: default zoom when entering /kg page is too small — hard to read nodes. Current: KnowledgeGraph.
- [x] **2026-04-18** -- T-P1-504: Fix rewrite_nodes_to_cn.py: preserve canonical_hub HTML comment markers. CN rewrite (commit 295ada1) stripped HTML comment markers (<!-- doc_kind: canonical_hub -->, sentinel blocks) from frame
- [x] **2026-04-18** -- T-P1-505: KG-UX-16: Cold-load defaults to first pillar at zoom 1.0 (not fitView all). ## Problem
KG-UX-14 added `fitView({ padding: 0.15, maxZoom: 1.0 })` on cold load. `maxZoom` only caps the computed fit-
- [x] **2026-04-18** -- T-P1-506: KG-UX-15: Category node expanded/collapsed visual distinction (saturation + chevron). ## Problem
After KG-UX-10/14 shipped, canvas category nodes have NO visual difference between expanded and collapsed sta
- [x] **2026-04-18** -- T-P1-507: KG-UX-17: TreeNav click must honor hasContent gate (extract activateNode helper). ## Problem
KG-UX-10 added the tri-state drawer gate to `handleActivate` (canvas click path) but `onTreeNavSelect` (left-
- [x] **2026-04-18** -- T-P1-508: KG-CONTENT-01: Add KMP family to Quick Index + expand KMP section in Array/String node (n44). ## Context
While reading /kg?node=n44&expanded=n9 (Array / String), the user noted KMP deserves elevation:
1. Surface KM
- [x] **2026-04-18** -- T-P1-509: KG-CONTENT-02: Add LC 1392 Longest Happy Prefix to KMP family (kmp[n-1] canonical application). ## Context
User identified LC 1392 "Longest Happy Prefix" as the purest teaching example of KMP's next-array semantics: 
- [x] **2026-04-17** -- T-P2-492: KG-UX-06: Bezier edges, pillar-colored, spacing polish. Current edges are orthogonal smoothstep with flat gray. Upgrade to bezier curves colored by source pillar for mindmap ae
- [x] **2026-04-18** -- T-P0-514: T-MLSD-FRAMEWORK-02: Append Writing Discipline rules to id=18 Appendix A (5 rules + examples + heuristic gates). ## Context
Current id=18 has Appendix A (11 sections + 6 mechanical gates). User review of id=92/id=198 V1 golds reveale
- [x] **2026-04-19** -- T-P0-515: T-MLSD-WORKED-92-V2: Rewrite id=92 Marketplace under Writing Discipline rules (prose-first, triage-complete). ## Context
Depends on T-P0-514 (Writing Discipline rules + 4 regex gates + LLM-judge) AND T-P0-518 (pilot rewrite of §2 
- [x] **2026-04-19** -- T-P0-516: T-MLSD-WORKED-198-V2: Rewrite id=198 Rec System under Writing Discipline rules. ## Context
Parallel counterpart to T-P0-515 — same execution model and gates, applied to id=198 Rec System. Depends on T
- [x] **2026-04-18** -- T-P0-518: T-MLSD-PILOT-92-S2: Pilot rewrite §2 of id=92 under new rules + human-review gate. ## Context — ITERATION 2
First iteration (commit 004e351, docs/mlsd_pilot_92_s2_20260418.md) passed regex gates + Gate 1
- [x] **2026-04-18** -- T-P0-519: T-MLSD-FRAMEWORK-03: Tighten Appendix A.1 — Rule 3 ≥3 alternatives + expanded Gate 9 regex + Rule 6 follow-up preemption + raised length targets. ## Context
T-P0-518 pilot (commit 004e351) passed all 4 regex gates + Gate 10 LLM-judge, but user review revealed the RU
- [x] **2026-04-18** -- T-P1-511: T-MLSD-AUDIT-01: Score 10 design problems against L5 framework, produce gap report. ## Context
Depends on T-P0-510 (L5 framework + Appendix A Unified Template are now canonical). After the framework is pu
- [x] **2026-04-18** -- T-P1-512: T-MLSD-WORKED-92: Upgrade Marketplace & Logistics (id=92) to L5-bar gold standard. ## Context
Depends on T-P0-510 (L5 framework + Appendix A Unified Template) + T-P1-511 (audit identifies this problem's 
- [x] **2026-04-18** -- T-P1-513: T-MLSD-WORKED-198: Upgrade Real-Time Rec System (id=198) with L5 skeleton. ## Context
Depends on T-P0-510 (framework + Appendix A template) + T-P1-511 (audit). id=198 "Real-Time Recommendation Sy
- [x] **2026-04-19** -- T-P1-520: T-LC-399-NOTES: Add LC 399 Evaluate Division double-solution notes + mark completed + link framework. ## Context
LC 399 Evaluate Division already exists in `problems` table (id=227, leetcode_id=399, title="Evaluate Divisio
- [x] **2026-04-19** -- T-P1-522: T-MLSD-WORKED-90-V2: Rewrite id=90 Recommendation Systems under A.1.v2. ## Context
Depends on T-P0-519 (A.1.v2 rules, completed). Apply Uniform Migration Recipe from `docs/mlsd_l5_audit_202604
- [x] **2026-04-19** -- T-P1-523: T-MLSD-WORKED-89-V2: Rewrite id=89 Search & Retrieval Systems under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe from `docs/mlsd_l5_audit_20260418.md` to id=89 Search & R
- [x] **2026-04-19** -- T-P1-524: T-MLSD-WORKED-91-V2: Rewrite id=91 Ads & Click Prediction under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=91 Ads & Click Prediction. V1 ~5296 chars with stan
- [x] **2026-04-19** -- T-P1-525: T-MLSD-WORKED-97-V2: Rewrite id=97 Generative AI Systems under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=97 Generative AI Systems. V1 ~5511 chars, standard 
- [x] **2026-04-19** -- T-P1-526: T-MLSD-WORKED-96-V2: Rewrite id=96 ML Infrastructure Design under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=96 ML Infrastructure Design. V1 ~5677 chars, standa
- [x] **2026-04-18** -- T-P2-500: [DEBT] CLAUDE.md: Remove duplicate Key Constraints section. CLAUDE.md has two ## Key Constraints sections (lines 15 and 34) with nearly identical content. The first is a template p
- [x] **2026-04-18** -- T-P2-503: KG-UX-12: Audit/migrate scattered content_length checks + LESSONS entry. ## Problem
Before this cleanup, 'does a node have drawer content?' could be answered multiple ways (content_length === 0
- [x] **2026-04-19** -- T-P0-537: [T-MLF-01] Parse attachment -> ml_fundamentals_inventory.yaml (27 Q, tier + interview_freq columns). Parse the 85KB 'ML high-freq' attachment at C:/Users/Shenghui Xu/.claude/channels/discord/inbox/1776657806963-1495635943
- [x] **2026-04-19** -- T-P0-538: [T-MLF-02] seed_ml_fundamentals_skeleton.py: root + 6 category + 27 leaf stubs. Create scripts/seed_ml_fundamentals_skeleton.py (idempotent, Python 3.11+, encoding=utf-8).

Inserts into framework_node
- [x] **2026-04-19** -- T-P0-539: [T-MLF-03] T1 content fill Cat 1-2 (7 Q: Classical ML & Losses + Eval/Data). Write description markdown for 7 leaves:
  Cat 1 (Classical ML & Losses): #1 Bias-Variance, #2 L1 vs L2 (+OLS), #3 Logis
- [x] **2026-04-19** -- T-P0-540: [T-MLF-03.5] [BARRIER] Template lock checkpoint: dev server review + canonical snippet. BARRIER TASK: runner MUST stop here pending user review. Steps:
  1. Start frontend dev server (cd src/frontend && npm r
- [x] **2026-04-19** -- T-P0-541: [T-MLF-04] T1 content fill Cat 3-4 (7 Q: Unsupervised + DL Training). Write description markdown for 7 leaves per the canonical template (from gamma_barrier):
  Cat 3 (Unsupervised): #8 K-me
- [x] **2026-04-19** -- T-P0-542: [T-MLF-05] T2 content fill Cat 5 (6 Q: Attention & Transformer). Write description markdown for 6 leaves:
  #15 Self-Attention Complexity (merge with its linear-attention deep-dive subs
- [x] **2026-04-19** -- T-P0-543: [T-MLF-06a] [BARRIER] T3 Y-depth #21 SFT/RLHF/DPO (calibration session). CALIBRATION BARRIER: runner MUST stop here pending user review.

Write a full Y-depth golden answer for Q#21 (SFT / RLHF
- [x] **2026-04-19** -- T-P0-547: [T-MLF-07] MLFundamentals.tsx page + ?cat=&slug= deep-link. Create src/frontend/src/pages/MLFundamentals.tsx modeled on QuickIndex.tsx:
  - Top tab bar: 6 categories (classical_ml,
- [x] **2026-04-19** -- T-P0-548: [T-MLF-08] Sidebar navItem + route wiring. Edit src/frontend/src/components/Sidebar.tsx:
  add { to: '/ml-fundamentals', label: 'ML 八股文' } between Quick Index and 
- [x] **2026-04-19** -- T-P1-527: T-MLSD-WORKED-93-V2: Rewrite id=93 NLP & LLM Systems under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=93 NLP & LLM Systems. V1 ~5371 chars, standard 8-he
- [x] **2026-04-19** -- T-P1-528: T-MLSD-WORKED-94-V2: Rewrite id=94 Computer Vision Systems under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=94 Computer Vision Systems. V1 ~5174 chars, standar
- [x] **2026-04-19** -- T-P1-529: T-MLSD-WORKED-95-V2: Rewrite id=95 Fraud & Trust Safety under A.1.v2. ## Context
Depends on T-P0-519. Apply Uniform Migration Recipe to id=95 Fraud & Trust Safety. V1 ~5040 chars, standard 8
- [x] **2026-04-19** -- T-P1-530: T-GOOG-DEDUPE: Dedupe Google prep docs id=38/51/53 schedule overlap + refresh dates to 4/20 mock + 4/21 R1 (NO archive, NO delete). ## Context
Google R1 **rescheduled** (not past). Events per interview_events:
- Mon 2026-04-20 10:00 AM PT — Google Cham
- [x] **2026-04-19** -- T-P1-531: T-GOOG-CN-52: Rewrite company_documents id=52 'Google DNN / Key Papers Gist' to Chinese-prose narration (9.5K chars, 0%→≥60% CN). ## Context
Google R1 ML Basics interview 2026-04-21 11:15 AM PT. id=52 is a 9509-char one-page gist covering Google-fami
- [x] **2026-04-19** -- T-P1-532: T-GOOG-CN-57: Rewrite company_documents id=57 'Staging 13 Flashcards' to Chinese-prose narration (12K chars, 0%→≥60% CN). ## Context
Google R1 ML Basics 2026-04-21 11:15 AM PT. id=57 is a 12123-char StudyNoteBuilder-generated doc with 13 flas
- [x] **2026-04-19** -- T-P1-534: T-GOOG-REORG-HUB: Rewrite id=53 Prep Hub to pure 3-tier navigation index (~3558→~700 chars). ## Context
Google /companies/3/prep has 17 docs flat-listed; id=38 + id=51 + id=53 all overlap as 'entry'. User confused
- [x] **2026-04-20** -- T-P0-544: [T-MLF-06b] T3 Y-depth #22 MoE routing + load balancing (template from zeta1). Apply the calibrated Y-depth template (from zeta1 review) to #22 MoE.

Four sections with: top-k routing math, load-bala
- [x] **2026-04-20** -- T-P0-545: [T-MLF-06c] T3 Y-depth #25 MLE vs MAP (upgraded from X to Y). Upgrade #25 from original X-depth (acronym-only) to full Y-depth.

Original covers ~60% already (Gaussian→L2 and Laplace
- [x] **2026-04-20** -- T-P0-546: [T-MLF-06d] T3 X-depth batch #23/#24/#26/#27 (Tokenization, Chinchilla, CLT/LLN, A/B test). X-depth: keep original structure, expand all acronyms on first use, fix formula context holes.

  #23 Tokenization — BPE
- [x] **2026-04-19** -- T-P1-535: T-GOOG-REORG-SLIM51: Slim id=51 by replacing Round 1 ML-dims + Round 2 G&L-attrs with db://38 refs (~6213→~4500 chars). ## Context
id=51 (Interview Prep Note) currently duplicates content from id=38 (Recruiter Call Prep):
- §Round 1 > '面试官期
- [x] **2026-04-20** -- T-P1-549: [T-MLF-09] KaTeX/drawer smoke test — all 27 drawers. Run npm run dev; manually open every one of the 27 question drawers; record rendering status in docs/ml_fundamentals_smo
- [x] **2026-04-20** -- T-P1-550: [T-MLF-10] Content QA pass — acronyms, formula context, term definitions. Walk each of 27 leaf descriptions and verify:
  (1) every acronym has first-occurrence full expansion in **English** (缩写
- [x] **2026-04-20** -- T-P1-552: [T-GOLD-01] Schema + migration: is_golden + golden_at on framework_nodes / behavioral_examples / company_documents + docs/golden_marker.md. Add curation columns to three tables (single Alembic migration or one-shot Python migration script under scripts/ -- fol
- [x] **2026-04-20** -- T-P1-553: [T-GOLD-02] Backend PUT endpoints accept is_golden; endpoint-layer golden_at auto-refresh on false->true. Extend three existing PUT endpoints (do NOT add new ones):
  - PUT /framework/nodes/{node_id}  (routers/framework.py)
  
- [x] **2026-04-20** -- T-P1-554: [T-GOLD-03] Frontend <GoldenToggleButton> shared component + orange color tokens. Create src/frontend/src/components/ui/GoldenToggleButton.tsx:
  Props: { itemType: 'framework_node' | 'behavioral_exampl
- [x] **2026-04-20** -- T-P1-555: [T-GOLD-04] goldenCardClass(isGolden) helper + golden [star] badge for card lists. Create src/frontend/src/utils/goldenStyle.ts exporting:
  goldenCardClass(isGolden: boolean): string  -- returns extra T
- [x] **2026-04-20** -- T-P1-556: [T-GOLD-05] Integrate GoldenToggleButton into FrameworkNodeDrawer (audit placement first). BEFORE coding: take a screenshot of the current FrameworkNodeDrawer header (src/frontend/src/components/framework/Framew
- [x] **2026-04-20** -- T-P1-557: [T-GOLD-06] Integrate into MLFundamentals.tsx cards + ?golden=1 URL filter. Edit src/frontend/src/pages/MLFundamentals.tsx:
  1. Fetch is_golden + golden_at per leaf -- the /framework/tree endpoin
- [x] **2026-04-20** -- T-P1-567: Add Slack Hiring Manager Round (Scott Clark) 2026-04-22. Add Salesforce/Slack SWE II ML hiring-manager round with Scott Clark on Wed 2026-04-22 09:00-09:45 AM PDT (category Slac
- [x] **2026-04-19** -- T-P2-517: KG-UX-18: Drawer rendering polish (GFM, rehype-raw, blockquote + callout styling). ## Context
Drawer-layer rendering polish, parallel to content V2 tasks. Independent of 514/515/516/518 — can run first, 
- [x] **2026-04-19** -- T-P2-521: [DEBT] MLInterviewPrep: Customize CLAUDE.md.local with project overview and tech stack. CLAUDE.md.local still has template placeholder text (generated from claude-code-project-template). Specific gaps:

1. Pr
- [x] **2026-04-19** -- T-P2-533: T-GOOG-CN-DRILL-BATCH: Batch-upgrade 11 Google drill docs + id=72 Bridge to ≥50% CN prose (from 30-47%). ## Context
Google R1 ML Basics 2026-04-21. 11 drill docs (id=55, 56, 60-69) + 1 bridge doc (id=72) currently 30-47% CN p
- [x] **2026-04-19** -- T-P2-536: T-GOOG-REORG-PREFIX: Add [R1/Bucket] prefix to 14 Tier-3 doc titles for visual grouping on /prep. ## Context
Flat list on /companies/3/prep doesn't visually group docs by topic. Add title prefix so alphabetical sort au
- [x] **2026-04-20** -- T-P2-551: [T-MLF-11] Google Prep Hub id=53 cross-link to /ml-fundamentals. Via scripts/seed_google_hub_mlf_crosslink.py (idempotent with sha256 guard):
  append to company_documents.content id=53
- [x] **2026-04-20** -- T-P2-558: [T-GOLD-07a] Discovery: scan Behavioral UI for drawer + toggle insertion points. Research-only task, NO code writes. Read:
  - src/frontend/src/pages/Behavioral*.tsx (all files matching this glob)
  - 
- [x] **2026-04-20** -- T-P2-559: [T-GOLD-07b] Behavioral UI integration: drawer toggle + card visuals + filter. Execute the plan from T-GOLD-07a. Expected work surface:
  - Add <GoldenToggleButton itemType='behavioral_example' /> to
- [x] **2026-04-20** -- T-P2-560: [T-GOLD-08] Company docs integration: drawer toggle + card visuals (no filter on index pages). Add <GoldenToggleButton itemType='company_document' /> to whatever view renders a company_document in full (prep note pa
- [x] **2026-04-20** -- T-P2-561: [T-GOLD-09] Golden Collection aggregator page (backend /golden endpoint + frontend page). Backend: add GET /golden router endpoint that unions rows from the 3 tables where is_golden=true, normalized into a unif
- [x] **2026-04-20** -- T-P2-563: Bias-Variance node 209 (ML Fundamentals leaf): append 5 interview follow-ups. Per user Discord 2026-04-20: correctly target the ml-fundamentals/classical_ml/bias-variance-tradeoff leaf (not pillar2 
- [x] **2026-04-20** -- T-P2-564: L1 vs L2 node 210: append MLE/MAP + Gaussian/Laplace prior view. Per user Discord 2026-04-20: augment ml-fundamentals/classical_ml/l1-vs-l2-regularization with a dedicated subsection af
- [x] **2026-04-20** -- T-P2-565: EM+GMM node 216: density-ratio note + BIC/AIC/held-out expansion + DPMM mechanics. Per user Discord 2026-04-20: three improvements to ml-fundamentals/unsupervised/em-and-gmm -- (A) clarify E-step respons
- [x] **2026-04-21** -- T-P0-572: [BQ-DEPTH-01] Phase A: Golden-story x Trait matrix doc + free-lunch call-out. Author docs/bq_golden_trait_matrix.md mapping 5 golden (EX-01/15/16/17/30) + 4-5 strong non-golden (EX-14/33/13/20/02) a
- [x] **2026-04-21** -- T-P0-573: [BQ-DEPTH-02] Link distribution audit on 266 question_example_links + prune candidates. Write scripts/audit_bq_link_distribution.py (read-only, no DB writes) and produce docs/bq_link_audit_20260421.md.

Per u
- [x] **2026-04-21** -- T-P0-574: [BQ-DEPTH-03] Apply link pruning per audit (gated by user approval of prune list). Apply link pruning per audit output from BQ-DEPTH-02.

AUTONOMOUS-SAFE MODE (no user gate): apply prune rules determinis
- [x] **2026-04-23** -- T-P0-604: [HOTFIX] ProblemResponse NULL category ResponseValidationError. Hotfix applied at 2026-04-21 18:55 after user Discord error report (msg 1496327736505925767).

Root cause: src/backend/s
- [x] **2026-04-23** -- T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Verified: helixos/.claude/settings.json all hook commands use /c/Anaconda/pytho
- [x] **2026-04-23** -- T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P1-184 (both target helixos bare-python -> /c/Anaconda/python.ex
- [x] **2026-04-23** -- T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P1-184/T-P1-238 (helixos bare-python fix + setup_python_env.sh).
- [x] **2026-04-23** -- T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical). SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P1-184/T-P1-238/T-P1-254 (helixos bare-python fix). Verified fix
- [x] **2026-04-21** -- T-P1-588: [KG-MLF-FS-00] Skeleton: new category feature_engineering_selection + 1 leaf + YAML + frontend wiring. Add a new /ml-fundamentals category 'feature_engineering_selection' positioned at CATEGORY_ORDER slot 3 (after classical
- [x] **2026-04-21** -- T-P1-595: [KG-MLF-FS-01] Content: leaf 28 — Comprehensive 千级特征筛选与建模 (single-page, all 7 sections + expansions). Author the single comprehensive content page for leaf id=28 (feature-selection-pipeline-1000features). Per user clarific
- [x] **2026-04-21** -- T-P1-596: [BQ-UX-01] Phase 1: Extract parsePitch util + render cn_elevator_pitch in ExampleDrawerContent. Shared-component prep task for BQ Examples tab drawer conversion. All 34 behavioral_examples already have cn_elevator_pi
- [x] **2026-04-21** -- T-P1-597: [BQ-UX-02] Phase 1: Refactor BehavioralQuestions Examples tab (CN pitch + drawer). The /behavioral Examples tab's ExampleCard (BehavioralQuestions.tsx:182-334) lags behind the rest of the UI: it uses inl
- [x] **2026-04-21** -- T-P1-598: [BQ-TAX-01] Phase 2: Schema migration — add behavioral_facets tables + is_signature column. Phase 2 of taxonomy refactor. Blocked behind Phase 1 UX (T-P1-596/597) per reviewer-approved execution order: UX先稳, sche
- [x] **2026-04-21** -- T-P1-599: [BQ-TAX-02] Phase 2: Seed 2 new themes + 3 facets + demote scope_creep_ambiguous. Seed the taxonomy delta into the new facets schema from BQ-TAX-01.

ADD themes (2):
- customer_user_focus / 'Customer & 
- [x] **2026-04-23** -- T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Helixos portion VERIFIED DONE: setup_python_env.sh present + absolute Python pa
- [x] **2026-04-20** -- T-P2-566: Add Lyra MD session with Mary Miller 2026-04-23. Add incoming Lyra MD video session with Mary Miller scheduled Thu 2026-04-23 08:30 AM PDT per user Discord 2026-04-20.
- [x] **2026-04-20** -- T-P2-568: Cross-Entropy/KL node 222: clarify KL is not Earth Mover's / Wasserstein. Per user Discord 2026-04-20: add minimal-diff clarification that KL 'distance' is information-theoretic (not geometric),
- [x] **2026-04-20** -- T-P2-569: Cross-Entropy/KL node 222: add formal Wasserstein primal + K-R dual definition. Per user Discord 2026-04-20 follow-up: add Kantorovich primal (inf over couplings) + Kantorovich-Rubinstein dual (sup ov
- [x] **2026-04-20** -- T-P2-570: MHA/MQA/GQA node 225: add dimension-flow clarifier + 3 interview misconceptions. Per user Discord 2026-04-20 (critical distillation of supplied notes): insert dimension-flow invariants (X n-by-d preser
- [x] **2026-04-20** -- T-P2-571: Fix MHA node 225: render residual formula + replace emoji with ASCII tags. Per user Discord 2026-04-20: fix residual formula which was in a code span (backticks) so \text{Attn}(x) rendered litera
- [x] **2026-04-23** -- T-P0-575: [BQ-DEPTH-04] Rewrite EX-01 (Search Diversity/Intent Collapse) via story_rewrite_protocol. EX-01 has 16 question links -- the biggest stale surface. It IS golden-flagged but pre-dates the NRG-v2 / risk_statement
- [x] **2026-04-23** -- T-P0-576: [BQ-DEPTH-05] Rewrite EX-02 (Manager Resistance -> Team Transfer) via story_rewrite_protocol. EX-02 is a high-link story still on pre-rewrite relevance_notes (2026-03-24 batch).

Same protocol as BQ-DEPTH-04 (7 ste
- [x] **2026-04-23** -- T-P0-577: [BQ-DEPTH-06] Rewrite EX-14 (LLM Exploration / Vague AI Mandate) via story_rewrite_protocol. EX-14 is a high-link, pre-rewrite story (2026-03-24 relevance_notes).

Same 7-step protocol as BQ-DEPTH-04.

Pre-draft r
- [x] **2026-04-23** -- T-P0-578: [BQ-DEPTH-07] Rewrite EX-33 (MoE -> Allocation Paradigm Shift) via story_rewrite_protocol. EX-33 is a high-link, pre-rewrite story (links from 2026-03-24 batch).

Same 7-step protocol as BQ-DEPTH-04.

Note: EX-3
- [x] **2026-04-24** -- T-P0-608: Fix emoji-CI: align check_emoji.py regex + Windows UTF-8 streams + code/doc split + meta test + cp1252 regression harness. Recapture of prior aborted session. Root cause found: check_emoji.py has wider regex (includes \u2600-\u26ff + \u2700-\u
- [x] **2026-04-25** -- T-P0-609: [KG-FIX-01] Backend: walk parent_id for pillar derivation. [KG-FIX-01] Backend: rewrite `_pillar_of()` in src/backend/routers/kg.py to walk
parent_id back to the depth=0 ancestor 
- [x] **2026-04-23** -- T-P1-579: [BQ-DEPTH-08] Phase B: Schema uplift -- add is_primary on links, probe_notes JSON on questions (NO angle_label). Schema migration after all 4 high-link rewrites land.

Per user direction: NO angle_label DB field. Angle lives in probe
- [x] **2026-04-24** -- T-P1-580: [BQ-DEPTH-09] probe_notes PATTERN CALIBRATION: write 4 samples on fresh stories (EX-15/16/17/30 top-Q each). Per user direction: use the 4 already-rewritten (fresh) stories as free-lunch pattern calibration BEFORE doing bulk C2. 
- [x] **2026-04-24** -- T-P1-602: [SD-YT-01] Expand system_designs id=21 (YouTube/Netflix Video Streaming) — traditional SD gaps. Expand system_designs row id=21 'Design YouTube/Netflix Video Streaming' (currently 21417 chars across overview/architec
- [x] **2026-04-24** -- T-P1-603: [SD-YT-02] Expand framework_nodes id=198 (Real-Time Recommendation) — YouTube-specific ML pipeline. Expand framework_nodes.description for id=198 'Real-Time Recommendation System Design' (currently 27996 chars, 19 header
- [x] **2026-04-23** -- T-P1-605: Seed LC 3900 (Longest Balanced Substring After One Swap, Google tag). User-driven: ad-hoc request to seed LC 3900 with Google company tag, preserving prefix-sum + bucket approach and adding 
- [x] **2026-04-23** -- T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Folded into T-P2-207's expanded scope, which now covers BOTH helixos AND templa
- [x] **2026-04-23** -- T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P2-207 (helixos test_check.py stop-cache removal). Work folded i
- [x] **2026-04-23** -- T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py. SUPERSEDED 2026-04-23 by T-P2-587 dedup. Duplicate of T-P2-207 (helixos test_check.py stop-cache removal). Work folded i
- [x] **2026-04-23** -- T-P2-586: [SYNC] Propagate 3 universal lessons from MLInterviewPrep (2026-04-17..04-19) to root LESSONS.md. Promote 3 new universal lessons from MLInterviewPrep LESSONS.md (2026-04-17..04-19) to Gen_AI_Proj root LESSONS.md. None
- [x] **2026-04-23** -- T-P2-587: [DEBT] helixos: Deduplicate 10 stale blocked SYNC tasks (bare-python, stop-cache, setup_python_env.sh). The helixos task DB has 10 blocked SYNC/DEBT tasks that are stale duplicates of each other, clogging the backlog.

Dupli
- [x] **2026-04-25** -- T-P0-610: [KG-FIX-02] Frontend: add ml-fundamentals to PILLAR_STYLES. [KG-FIX-02] Frontend: extend PILLAR_STYLES in
src/frontend/src/components/kg/kgStyles.ts with an `"ml-fundamentals"` ent
- [x] **2026-04-25** -- T-P0-611: [KG-FIX-03] Frontend: explicit PILLAR_ORDER map (step=10). [KG-FIX-03] Frontend: replace pillarSortKey() regex in
src/frontend/src/components/kg/useKgLayout.ts with an EXPLICIT
`P
- [x] **2026-04-25** -- T-P0-612: [KG-FIX-04] Schema invariant + convention doc + smoke protocol + LESSONS postmortem. [KG-FIX-04] Schema invariant + path convention doc + LESSONS postmortem +
seed-batch process change.

WHY: The slash-pat
- [x] **2026-04-25** -- T-P0-613: [KG-FIX-05] Manual smoke + screenshots + HARD MERGE GATE (no auto-merge to main). [KG-FIX-05] Manual smoke test + before/after screenshots + HARD MERGE GATE.

WHY: AC-as-software-test only. Auto-merge b
- [x] **2026-04-25** -- T-P0-617: [DEV-FIX-01] scripts/dev.py auto-evict stale backend on port 8100 conflict. WHY
`scripts/dev.py` is the daily dev launcher (uvicorn backend on 8100 + vite frontend on 5173). Recurring high-frictio
- [x] **2026-04-27** -- T-P0-626: Fix BQ ExampleCard layout: title squeezed to one-word-per-line by long principle pills. Bug: BehavioralQuestions.tsx examples view, EX-01 card title 'Search Diversity --- Intent Collapse via Item-vs-Page Diag
- [x] **2026-04-25** -- T-P1-600: [BQ-TAX-03] Phase 2: Retag existing 34 examples + 115 questions against new taxonomy. Retag all existing behavioral_examples + behavioral_questions against the new themes + facets from BQ-TAX-02.

Retag ste
- [x] **2026-04-25** -- T-P1-601: [BQ-TAX-04] Phase 2: Frontend — new theme cards + facet pills + CLUSTER_FAMILIES update + is_signature visual. Frontend surface for the new taxonomy landed by BQ-TAX-01/02/03.

Scope:
1. /quick-index?section=bq — add 2 new theme ca
- [x] **2026-04-25** -- T-P1-615: [PROB-SEARCH-01] Pure-numeric search exact-match on leetcode_id (currently '4' returns 50+ irrelevant). WHY
`/problems?search=4` returns 50+ irrelevant matches (4, 14, 24, 34, 40-49, 64, 74, 84, 140, 142, 304, 410, ...) beca
- [x] **2026-04-25** -- T-P1-616: [PROB-NOTES-04] Rewrite LC#4 (id=89) solution with cleaner sentinel-based partition + 4-fact mental model. WHY
User reviewed current LC#4 solution at http://localhost:5173/problems/89 (DB row id=89, leetcode_id=4) and found the
- [x] **2026-04-27** -- T-P1-625: [Uber-LC-Index] New company_document: Uber LC index view (drawer-linked, grouped, all 247 Uber-tagged-with-notes problems). ## Goal
Discord ad-hoc msgs 1498358551654174802 + 1498360938733109532 (task-planning mode). Create an index/list view of
- [x] **2026-04-25** -- T-P2-584: [BQ-DEPTH-13] Phase C1: probe_qa.md for remaining 4 golden (EX-01/15/16/17) matching EX-30 style. Extend the EX-30_probe_qa.md pattern to the other 4 golden stories. This is story-side depth (5 anticipated probes + del
- [x] **2026-04-25** -- T-P2-607: F-2: emoji scan check_emoji.py honor CLI args (scan_single_file extraction). Follow-up to T-P1-606 (first emoji-scanner fix commit).

Make scripts/check_emoji.py honor sys.argv[1:]: if non-empty, s
- [x] **2026-04-25** -- T-P2-614: [KG-DESIGN-DUAL-VIEW] Open Q: consolidate vs legitimize ml-fundamentals + pillar2 coexistence. [KG-DESIGN-DUAL-VIEW] Document the dual-view decision as PERMANENT.

USER-RATIFIED DECISION (Discord msg 149777377600654
- [x] **2026-04-27** -- T-P2-618: [followup] LC 864 notes seeded (bitmask BFS canonical + list-of-bool baseline). Discord followup. User wrote LC 864 list-of-bool BFS solution, requested DB notes + bitmask compression upgrade. Seeded 
- [x] **2026-04-27** -- T-P2-619: [followup] LC 502 IPO notes seeded (sort + max-heap greedy). Discord followup. User wrote LC 502 sort+max-heap solution and asked for DB notes. Seeded notes via scripts/_update_lc50
- [x] **2026-04-28** -- T-P0-628: [UBER-VO-1] Audit + inventory: extract ML Coding & ML Sys Design content from all Uber sources. ## Goal
Build a complete inventory of every ML Coding + ML System Design topic that should land in the Uber VO prep, sou
- [x] **2026-04-29** -- T-P0-629: [UBER-VO-2] Seed company_document: 'Uber ML Coding Golden Answer 集合' (Staff-level). ## Goal
Create one new Uber company_document covering the 4 KNOWN ML Coding items from the source TXT, at the same Staff
- [x] **2026-04-29** -- T-P0-630: [UBER-VO-3] Seed company_document: 'Uber ML System Design Golden Answers' (Staff-level). ## Goal
Create one new Uber company_document covering all ML System Design items at Staff-level depth, with the source T
- [x] **2026-04-29** -- T-P0-632: [UBER-VO-5 MVP] Patch id=37 Round 3+4 with anchor links to new ML Coding/SD docs (deferring full FE page). ## MVP downscope (per critical review)
Original plan was a bespoke \`pages/UberIndex.tsx\` with 5 tabs + URL state + dra
- [x] **2026-04-29** -- T-P0-634: [UBER-VO-7] Manual smoke + verification: full multi-charter flow + content correctness pass. ## Goal
End-to-end manual verification that ALSO tests learning outcome (verbal recall), not just wiring. Per critical r
- [x] **2026-04-29** -- T-P0-653: Pinterest VO: revert misdirected prep_doc 83 + companies.interview_stages edits. Phase 1 of revised plan. **PARTIAL revert + redirect** (NOT pure revert per reviewer feedback hole #2): doc 83 has indep
- [x] **2026-04-29** -- T-P0-654: Pinterest VO: add 5 onsite rounds to interview_events (Dashboard InterviewTimeline). Phase 1 of revised plan. Add 5 Pinterest VO rounds to interview_events via idempotent seed.

CHANGED FROM ORIGINAL PLAN 
- [x] **2026-04-29** -- T-P0-655: Pinterest VO: verify Dashboard rendering via headless screenshot + user confirmation. Phase 1 verification. **Per reviewer: SQL > screenshot** -- SQL proves DB state, screenshot only proves UI render. Both 
- [x] **2026-04-29** -- T-P0-662: Pinterest HR prep call (Daniel McCray, 2026-04-30 14:00 PDT) added to InterviewTimeline. User received email from Daniel McCray (Pinterest interview coordinator/recruiter) proposing to move prep call to 2026-0
- [x] **2026-04-29** -- T-P1-631: [UBER-VO-4] Strengthen existing search/recommendation content in id=33 + id=37 (delta-only). ## Priority bump (per critical review)
P1 -> **P0**. Reasoning: id=33 is the active reference doc for the Round-3 Design
- [x] **2026-04-29** -- T-P1-635: [UBER-VO-2b] Seed audit-discovered NEW ML Coding items (companion to T-P0-629). ## Goal
Companion task to T-P0-629. Once T-P0-628 audit produces its NEW inventory and T-P0-629 lands the 4 known items,
- [x] **2026-04-29** -- T-P1-639: [DEBT] MLInterviewPrep: pyproject.toml deps out of sync with requirements.txt (13 missing). Cross-project-sync 2026-04-29 audit: pyproject.toml [project].dependencies has only 2 packages but requirements.txt has 
- [x] **2026-04-27** -- T-P2-620: [followup] LC 2571 notes rewrite (bit-greedy + NAF formula) + Uber tag. Discord followup. User wrote LC 2571 with the canonical bit-trick (skip zeros + n&3==3 carry / n&3==1 subtract) and aske
- [x] **2026-04-27** -- T-P2-621: [LC2861] Seed Maximum Number of Alloys notes (binary-search-on-answer canonical). Discord ad-hoc request msg 1498348552362000474. Write LC 2861 (Maximum Number of Alloys) seed notes to data/mle_prep.db 
- [x] **2026-04-27** -- T-P2-622: [LC384] Seed Shuffle an Array notes (Fisher-Yates + sort-based shuffle distillation) + Uber tag. Discord ad-hoc msg 1498353628937715803. User added their own LC 384 attempt and asked to distill discussion: (1) Fisher-
- [x] **2026-04-27** -- T-P2-623: [LC855] Seed Exam Room notes (brute-force sorted-list + heap follow-up). Discord ad-hoc msg 1498356808602095685. User pasted LC official editorial brute-force code and asked for notes + explici
- [x] **2026-04-27** -- T-P2-624: [LC545] Seed Boundary of Binary Tree notes (4-state flag DFS + deque appendleft). Discord ad-hoc msg 1498358265019371650. User pasted one-pass DFS solution with ROOT/LEFT/RIGHT/INNER flag classification
