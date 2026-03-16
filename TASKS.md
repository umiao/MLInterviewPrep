# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

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
- [x] **2026-03-16** -- T-P1-107: Study Radio page: queue management, now playing, history. New StudyRadio.tsx page at /radio. Sections: (1) Quick Start with company filter + engine select + Start Radio button (2
- [x] **2026-03-16** -- T-P1-106: Persistent Audio Player Bar (Spotify-style bottom bar). New AudioPlayerBar.tsx: fixed-bottom bar with [Title+badge] [<<] [Play/Pause] [>>] [Progress bar] [Time] [Speed 0.75-2x]
- [x] **2026-03-16** -- T-P1-105: Browser Web Speech API fallback + prefetch next item. Enhance useAudioPlayer: (1) Browser fallback: if synthesize returns {mode: browser}, use SpeechSynthesis API seamlessly 
- [x] **2026-03-16** -- T-P1-104: Frontend Audio Player + Radio Mode (core playback). New files: types/reading.ts, hooks/useAudioPlayer.ts, contexts/AudioPlayerContext.tsx. Hook manages <audio> element: pla
- [x] **2026-03-16** -- T-P1-103: TTS Engine abstraction: EdgeTTS + OpenAI + Browser engines. Refactor services/tts_engine.py: ABC TTSEngine with synthesize_to_file + voice_options. EdgeTTSEngine (refactor from MVP
- [x] **2026-03-16** -- T-P0-99: TTS MVP: edge-tts -> MP3 -> <audio> playback for framework nodes. Minimal vertical slice: pick one framework node -> preprocess markdown (v1: strip #, **, *, _, links, skip code blocks) 
- [x] **2026-03-16** -- T-P0-102: Reading REST endpoints: queue, progress, content, async synthesize. Expand routers/reading.py + new schemas/reading.py: GET /api/reading/queue (ranked with progress), GET /api/reading/prog
- [x] **2026-03-16** -- T-P0-101: Content Pipeline: queue ranking, preprocessing v2, chunking. Expand services/content_pipeline.py: (1) get_reading_queue(db, company_ids, days_until_interview, limit=20) - reuse comp
- [x] **2026-03-16** -- T-P0-100: ReadingProgress + AudioCache models + Migration v4. New models in models/reading.py: ReadingProgress (content_type, content_id, last_chunk_index, char_offset, total_chars, 
- [x] **2026-03-15** -- T-P2-94: [B7] Frontend: Analytics deep-dive (radar chart, scatter plot, trend lines). AC:\n- Pattern comfort radar chart (Recharts RadarChart) on Problems page or Dashboard\n- Framework confidence vs import
- [x] **2026-03-15** -- T-P2-93: [B6] Frontend: QA session summarize button in ReviewPanel. AC:
- [x] **2026-03-15** -- T-P2-92: [B6] Frontend: Settings page (import/export + scraper management). AC:
- [x] **2026-03-15** -- T-P2-91: [B6] Frontend: Framework tree search + breadcrumb path. AC:
- [x] **2026-03-15** -- T-P2-90: [B6] Frontend: Kanban drag-and-drop for Companies page. AC:
- [x] **2026-03-15** -- T-P2-72: Add GET / root endpoint returning API info JSON
- [x] **2026-03-15** -- T-P2-68: Add combined backend+frontend startup script (scripts/dev.py)
