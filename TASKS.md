# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

#### T-P2-112: SSE chunked audio streaming (if latency requires it)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with MediaSource API on frontend. Evaluate need after Phase 2. AC: SSE streams audio chunks, frontend plays without gaps, progress tracked per chunk

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 103 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-17** -- T-P1-125: Fix checkbox persistence and scroll white space bugs on PrepNotesPage
- [x] **2026-03-16** -- T-P2-123: Framework: resizable right panel and scrollable tabs in NodeDetailPanel. Problem: Right panel fixed at 288px (w-72), tabs overflow when names are long.
- [x] **2026-03-16** -- T-P2-111: Listening session analytics on Dashboard and StudyRadio. Track listening sessions via ReadingSession model. POST /api/reading/sessions (create/close), GET /api/reading/stats (to
- [x] **2026-03-16** -- T-P2-110: LLM-generated TTS summaries for long content. Use LLM service to create spoken-word-optimized summaries. Cache in tts_summaries table. Prompt: Rewrite for TTS narrati
- [x] **2026-03-16** -- T-P2-109: Interview-aware content ordering in reading queue. Enhance get_reading_queue(): query interview_events for upcoming interviews, boost urgency for soonest interview company
- [x] **2026-03-16** -- T-P1-98: Dashboard timeline prep notes modal + red dots on EventCard. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-97: PrepNotesTab with checkbox click-toggle + Companies page integration. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-96: Auto-link company on timeline event creation via get_or_create_company. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-95: Add prep_notes to Company model + migration v3 + get_or_create_company service. ## Acceptance Criteria
- [x] **2026-03-16** -- T-P1-124: Fix strikethrough in prep-prose CSS + fix Blind75 docx import regex for full-width colons
- [x] **2026-03-16** -- T-P1-122: Problem detail: collapsible My Notes section (default collapsed). Problem: My Notes section always expanded adds visual noise.
- [x] **2026-03-16** -- T-P1-121: Problems: notes indicator icon on All Problems tab. Problem: No visual signal on All Problems landing page to indicate which problems have notes.
- [x] **2026-03-16** -- T-P1-120: Problems: add Difficulty as a sort option (frontend + backend). AC:
- [x] **2026-03-16** -- T-P1-119: Fix strikethrough + math formula rendering in MarkdownPreview. Problem: (1) ~~strikethrough~~ text not rendering with line-through -- Tailwind v4 prose resets <del> styling. (2) Math 
- [x] **2026-03-16** -- T-P1-116: Local LeetCode Descriptions (Neetcode.io Fetch)
- [x] **2026-03-16** -- T-P1-115: Decouple Reading from Synthesis (Text View)
- [x] **2026-03-16** -- T-P1-114: Unified Faithful Transcript System
- [x] **2026-03-16** -- T-P1-108: Listen buttons across app (Companies, Questions, Dashboard, Framework). Add Listen buttons to existing pages using AudioPlayerContext.play(): Companies page (Listen to prep notes per company),
- [x] **2026-03-16** -- T-P0-118: Problems UX: full-page descriptions, markdown rendering, batch fetch, remove Edit/Del
- [x] **2026-03-16** -- T-P0-117: Integrate LinkedIn JD into Prep Notes
- [x] **2026-03-16** -- T-P0-113: Fix Radio blank page, TTS preprocessing quality, LinkedIn content sync
