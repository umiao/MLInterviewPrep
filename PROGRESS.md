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
