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
