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

> 119 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-17** -- T-P2-133: Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs. Generate prep docs for Pillars 1, 5, 8 leaf topics. Coding: DS cheat sheets, algorithm paradigms, MLE-specific patterns.
- [x] **2026-03-17** -- T-P2-132: Applied ML pillar (Pillar 4) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 4 leaf topics. Covers: recommender systems, search & IR, NLP & LLM applicatio
- [x] **2026-03-17** -- T-P1-134: Fix MarkdownPreview checkbox mismatch caused by remarkMath dollar-sign corruption
- [x] **2026-03-17** -- T-P1-131: Math & Statistics pillar (Pillar 7) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 7 leaf topics. Covers: probability distributions, Bayesian inference, hypothe
- [x] **2026-03-17** -- T-P1-130: ML System Design pillar (Pillar 3) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 3 leaf topics. Covers: design framework methodology, classic problems (rec sy
- [x] **2026-03-17** -- T-P1-129: Deep Learning & LLM pillar (Pillar 6) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 6 leaf topics following content template. Covers: Transformer architecture, a
- [x] **2026-03-17** -- T-P1-128: PrevNextNav arrow component + integrate in PrepNotesPage and ProblemDetailPage. Reusable PrevNextNav component with left/right chevrons + tooltip. PrepNotesPage: navigate companies alphabetically. Pro
- [x] **2026-03-17** -- T-P1-127: Content template + ML Fundamentals pillar (Pillar 2) prep docs for all 25 leaf topics. Create docs/framework_content_template.md with standard structure (Overview, Core Concepts with LaTeX, Implementation, I
- [x] **2026-03-17** -- T-P1-126: Framework full-screen notes page: backend GET endpoint + useFrameworkNotes hook + FrameworkNotesPage + route + Open Full Page link. End-to-end: (1) GET /framework/nodes/{id} endpoint returning single node. (2) useFrameworkNotes hook mirroring usePrepNo
- [x] **2026-03-17** -- T-P1-125: Fix checkbox persistence and scroll white space bugs on PrepNotesPage
- [x] **2026-03-16** -- T-P2-123: Framework: resizable right panel and scrollable tabs in NodeDetailPanel. Problem: Right panel fixed at 288px (w-72), tabs overflow when names are long.
- [x] **2026-03-16** -- T-P2-111: Listening session analytics on Dashboard and StudyRadio. Track listening sessions via ReadingSession model. POST /api/reading/sessions (create/close), GET /api/reading/stats (to
- [x] **2026-03-16** -- T-P2-110: LLM-generated TTS summaries for long content. Use LLM service to create spoken-word-optimized summaries. Cache in tts_summaries table. Prompt: Rewrite for TTS narrati
- [x] **2026-03-16** -- T-P2-109: Interview-aware content ordering in reading queue. Enhance get_reading_queue(): query interview_events for upcoming interviews, boost urgency for soonest interview company
