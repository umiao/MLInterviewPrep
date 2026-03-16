# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-101: Content Pipeline: queue ranking, preprocessing v2, chunking
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-100
- **Description**: Expand services/content_pipeline.py: (1) get_reading_queue(db, company_ids, days_until_interview, limit=20) - reuse compute_urgency() from study_planner.py, rank FrameworkNodes, interleave prep_notes + interview_questions for target companies. (2) preprocess_for_tts v2: add bullets->sentences, expand e.g./i.e., add [PAUSE] at headings (defer LaTeX/tables). (3) chunk_text(text, max_chars=500) - split at sentence boundaries. (4) get_content_text for all 3 content types. (5) compute_content_hash for cache invalidation. AC: Queue sorted by urgency with all 3 types, preprocessing tests per rule, chunking never breaks mid-sentence, hash changes on text change

#### T-P0-102: Reading REST endpoints: queue, progress, content, async synthesize
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-100, T-P0-101
- **Description**: Expand routers/reading.py + new schemas/reading.py: GET /api/reading/queue (ranked with progress), GET /api/reading/progress, PUT /api/reading/progress/{type}/{id} (update last_chunk_index + char_offset), GET /api/reading/content/{type}/{id} (preprocessed text + chunks), DELETE /api/reading/progress (reset). Refactor POST /api/reading/synthesize to use AudioCache (cache-aware + content_hash invalidation). Async mode for long content (>2000 chars): return 202 + job_id, poll GET /api/reading/jobs/{id}. AC: Queue sorted, progress persists both fields, cache hit/miss correct, long content returns 202, tests for each endpoint

### P1 -- Should Have (agentic intelligence)

#### T-P1-103: TTS Engine abstraction: EdgeTTS + OpenAI + Browser engines
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-99
- **Description**: Refactor services/tts_engine.py: ABC TTSEngine with synthesize_to_file + voice_options. EdgeTTSEngine (refactor from MVP), OpenAITTSEngine (httpx async, OPENAI_API_KEY), BrowserTTSEngine (returns text JSON, frontend speaks). Factory get_tts_engine(name). Add OPENAI_API_KEY to Settings. Browser engine returns {mode: browser, text: ...} instead of audio URL. AC: EdgeTTS produces MP3, OpenAI mocked + API call verified, Browser returns text, factory correct per config, fallback test: edge-tts network error -> returns browser mode

#### T-P1-104: Frontend Audio Player + Radio Mode (core playback)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-102, T-P1-103
- **Description**: New files: types/reading.ts, hooks/useAudioPlayer.ts, contexts/AudioPlayerContext.tsx. Hook manages <audio> element: play(item) calls POST /synthesize -> set src -> play, pause/resume via audio API, skip to next queue item, onended auto-advance (radio mode = autoAdvance + queue from /reading/queue), speed via playbackRate, progress tracking via ontimeupdate (save to backend every 30s). Wrap app in AudioPlayerContext in App.tsx. AC: play/pause/resume/skip work, auto-advance through queue, speed 0.75x-2.0x works, progress saved, state persists across navigation

#### T-P1-105: Browser Web Speech API fallback + prefetch next item
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-104
- **Description**: Enhance useAudioPlayer: (1) Browser fallback: if synthesize returns {mode: browser}, use SpeechSynthesis API seamlessly (same play/pause/skip interface). (2) Prefetch: while current item plays, POST /synthesize for next queue item so MP3 is cached and ready. AC: edge-tts failure -> browser fallback without user action, engine switch to browser uses SpeechSynthesis, next item starts instantly (prefetch hit), no prefetch if only 1 item remaining

#### T-P1-106: Persistent Audio Player Bar (Spotify-style bottom bar)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-104
- **Description**: New AudioPlayerBar.tsx: fixed-bottom bar with [Title+badge] [<<] [Play/Pause] [>>] [Progress bar] [Time] [Speed 0.75-2x] [Engine selector] [Queue slide-out] [Close]. Mount in Layout.tsx, visible only when player active. Keyboard: Space=play/pause (with focus guard for inputs), N=next. AC: All controls work, progress bar real-time via ontimeupdate, responsive on small screens, keyboard shortcuts work

#### T-P1-107: Study Radio page: queue management, now playing, history
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-104, T-P0-102
- **Description**: New StudyRadio.tsx page at /radio. Sections: (1) Quick Start with company filter + engine select + Start Radio button (2) Queue: ranked list with urgency, type badge, progress per item, play button (3) Now Playing: current item highlight with scrolling text (4) History: recently completed items. Add route in App.tsx, nav item in Sidebar.tsx. AC: Queue sorted by urgency, items show progress (not started/partial/done), click item plays from last chunk, Start Radio auto-advances, current item highlighted

#### T-P1-108: Listen buttons across app (Companies, Questions, Dashboard, Framework)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-104
- **Description**: Add Listen buttons to existing pages using AudioPlayerContext.play(): Companies page (Listen to prep notes per company), Questions page (Listen on question rows), Dashboard (Start Radio quick action card), Framework tree (speaker icon per node). AC: Buttons on all content-bearing pages, click starts playback + shows player bar, consistent icon/behavior

### P2 -- Nice to Have

#### T-P2-109: Interview-aware content ordering in reading queue
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P0-101
- **Description**: Enhance get_reading_queue(): query interview_events for upcoming interviews, boost urgency for soonest interview company, interleave prep_notes first when interview < 3 days. AC: LinkedIn interview tomorrow -> LinkedIn prep notes first, company weights influence ordering, falls back to standard urgency without upcoming interviews

#### T-P2-110: LLM-generated TTS summaries for long content
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P0-101
- **Description**: Use LLM service to create spoken-word-optimized summaries. Cache in tts_summaries table. Prompt: Rewrite for TTS narration, conversational, expand abbreviations, no visual references. Fallback to preprocessed raw text when LLM unavailable. AC: Summary cached (not regenerated), used instead of raw when available, mocked LLM test

#### T-P2-111: Listening session analytics on Dashboard and StudyRadio
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P0-100, T-P1-107
- **Description**: Track listening sessions via ReadingSession model. POST /api/reading/sessions (create/close), GET /api/reading/stats (total time, items/day, streak). Show on Dashboard + StudyRadio page. AC: Sessions created/closed correctly, stats accurate, Dashboard shows listening time alongside study time

#### T-P2-112: SSE chunked audio streaming (if latency requires it)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P1-103
- **Description**: Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with MediaSource API on frontend. Evaluate need after Phase 2. AC: SSE streams audio chunks, frontend plays without gaps, progress tracked per chunk

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 87 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-16** -- T-P1-98: Dashboard timeline prep notes modal + red dots on EventCard. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-97: PrepNotesTab with checkbox click-toggle + Companies page integration. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-96: Auto-link company on timeline event creation via get_or_create_company. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-95: Add prep_notes to Company model + migration v3 + get_or_create_company service. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P0-99: TTS MVP: edge-tts -> MP3 -> <audio> playback for framework nodes. Minimal vertical slice: pick one framework node -> preprocess markdown (v1: strip #, **, *, _, links, skip code blocks) 
- [x] **2026-03-16** -- T-P0-100: ReadingProgress + AudioCache models + Migration v4. New models in models/reading.py: ReadingProgress (content_type, content_id, last_chunk_index, char_offset, total_chars, 
- [x] **2026-03-15** -- T-P2-94: [B7] Frontend: Analytics deep-dive (radar chart, scatter plot, trend lines). AC:\n- Pattern comfort radar chart (Recharts RadarChart) on Problems page or Dashboard\n- Framework confidence vs import
- [x] **2026-03-15** -- T-P2-93: [B6] Frontend: QA session summarize button in ReviewPanel. AC:
- [x] **2026-03-15** -- T-P2-92: [B6] Frontend: Settings page (import/export + scraper management). AC:
- [x] **2026-03-15** -- T-P2-91: [B6] Frontend: Framework tree search + breadcrumb path. AC:
- [x] **2026-03-15** -- T-P2-90: [B6] Frontend: Kanban drag-and-drop for Companies page. AC:
- [x] **2026-03-15** -- T-P2-72: Add GET / root endpoint returning API info JSON
- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
