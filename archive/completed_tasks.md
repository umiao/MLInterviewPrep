# Completed Tasks Archive

> 158 completed tasks archived as of latest archival.

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
