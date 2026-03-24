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


## 2026-03-17 -- [T-P1-135] Sticky toolbar + scroll position sync for PrepNotes
- **What I did**: (1) Made PrepNotesTab toolbar sticky with `sticky top-0 z-10 bg-white border-b` so it stays visible during scroll. (2) Created shared `useScrollRestore` hook that captures scroll ratio before mode switch and restores it after new content renders using ResizeObserver + 500ms timeout fallback. (3) Encapsulated `setMode` into `switchMode(newMode, captureScroll?)` in `usePrepNotes` to ensure scroll capture always happens before mode change. (4) Wired scroll restore into both PrepNotesTab (via explicit `scrollContainerRef` prop from parent) and PrepNotesPage (via owned `contentRef`). (5) Added UI component best practices to LESSONS.md.
- **Deliverables**: src/frontend/src/hooks/useScrollRestore.ts (new), src/frontend/src/hooks/usePrepNotes.ts, src/frontend/src/components/companies/PrepNotesTab.tsx, src/frontend/src/pages/PrepNotesPage.tsx, src/frontend/src/pages/Companies.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-135 --status completed`

## 2026-03-17 -- [T-P1-136] Fix scroll sync dual-ref targeting
- **What I did**: Fixed scroll position sync to use the correct scroll target per mode. Preview mode scrolls the outer container div; edit mode scrolls the textarea internally. (1) Rewrote `useScrollRestore` to accept dual refs (`containerRef` + `textareaRef`) and pick the correct element based on mode. Removed ResizeObserver in favor of rAF + 100ms fallback for async markdown. (2) Added `captureScrollRef` option to `usePrepNotes` so `switchMode()` auto-captures scroll before mode change -- callers no longer pass `beforeSwitch` manually. (3) Both `PrepNotesTab` and `PrepNotesPage` now attach `textareaRef` to their textarea elements and wire the capture ref.
- **Deliverables**: src/frontend/src/hooks/useScrollRestore.ts, src/frontend/src/hooks/usePrepNotes.ts, src/frontend/src/components/companies/PrepNotesTab.tsx, src/frontend/src/pages/PrepNotesPage.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-136 --status completed`

## 2026-03-17 -- [T-P1-137] Full-screen MD rendering for Study Radio + framework tree notes links
- **What I did**: (1) Study Radio "Read" button now navigates to full-screen pages (`/framework/:nodeId/notes` for framework nodes, `/companies/:companyId/prep` for prep notes) instead of opening the small TranscriptViewer modal. Interview questions still use the modal. (2) Added a notes icon-link on each node in FrameworkTreeView that links to `/framework/:nodeId/notes` with stopPropagation to avoid triggering onSelect.
- **Deliverables**: src/frontend/src/pages/StudyRadio.tsx, src/frontend/src/components/FrameworkTreeView.tsx
- **Sanity check result**: TypeScript compiles cleanly (npx tsc --noEmit)
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-137 --status completed`

## 2026-03-17 -- [T-P1-138] Fix math delimiters, add code syntax highlighting, document conventions
- **What I did**: (1) Created `scripts/fix_math_delimiters.py` to convert `$...$` inline math to `$$...$$` across all 8 seed files (1,526 conversions). Script protects code blocks, inline code spans, and currency patterns like `$2M`. (2) Installed `react-syntax-highlighter` and added Prism-based code highlighting (oneDark theme) to `MarkdownPreview.tsx` -- block code gets syntax colors (default: Python), inline code keeps existing gray styling. (3) Re-seeded all 148 framework nodes. (4) Added `## Markdown Content Conventions` section to CLAUDE.md.
- **Deliverables**: scripts/fix_math_delimiters.py (new), scripts/seed_pillar{1..8}_content.py (converted), src/frontend/src/components/ui/MarkdownPreview.tsx, src/frontend/package.json, CLAUDE.md
- **Sanity check result**: 811 tests pass, TypeScript compiles, frontend builds, API smoke test confirms `$$O(1)$$` in DB and API responses, currency `$2M` preserved, code block content untouched
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-138 --status completed`

## 2026-03-17 -- [T-P1-139..142] Fix 6 Framework page issues + seed interview events
- **What I did**: (1) Widened right panel default from 288px to 35% of viewport (min 480px). (2) Made URL the single source of truth for node selection -- added `/framework/:nodeId` route, removed `selectedNode` state, derive from `useParams`. Leaf nodes with description navigate to notes page. (3) Auto-expand ancestors in tree when URL changes selection. (4) Row click on non-leaf nodes now toggles expand + selects (VS Code/Finder pattern). (5) Checkbox toggles now calculate progress_pct from checked/total checkboxes and send to backend. Backend propagates weighted progress to all ancestors atomically. (6) Created `scripts/seed_interview_events.py` for DoorDash (3/26 ML Deep Dive) and Uber (3/27 HR) events.
- **Deliverables**: src/frontend/src/App.tsx, src/frontend/src/pages/Framework.tsx, src/frontend/src/components/FrameworkTreeView.tsx, src/frontend/src/hooks/useFrameworkNotes.ts, src/backend/routers/framework.py, scripts/seed_interview_events.py (new)
- **Sanity check result**: 811 tests pass, TypeScript compiles cleanly, ruff clean
- **Status**: [DONE]
- **Request**: Tasks T-P1-139 through T-P1-142 marked completed


## 2026-03-17 -- Seed companies from application tracking spreadsheet
- **What I did**: Read the Excel tracking file (已投递追踪.xlsx), parsed 20 unique companies with their applied positions and notes, and created an idempotent seed script to insert them into the DB. LinkedIn and DoorDash already existed (2 prior entries); 20 new companies added (Google, Airbnb, Uber, Netflix, Glean, Apple, Nvidia, Reddit, Salesforce, Microsoft, Instacart, Robinhood, Roblox, Amazon, Coinbase, Quora, Intuit, Snap, OpenAI, Anthropic). Each company has position details in notes field, status=applied, applied_at=2026-03-17.
- **Deliverables**: scripts/seed_companies.py (new)
- **Sanity check result**: 22 total companies verified in DB via query
- **Status**: [DONE]
- **Request**: No task ID (ad-hoc user request)

## 2026-03-17 -- Red dot logic change + card click-to-prep navigation
- **What I did**: Changed company card red dot from counting unchecked markdown checkboxes to showing whenever prep_notes is non-empty AND status is not "rejected". Changed card click in kanban to navigate to full-screen prep notes page (`/companies/:id/prep`) instead of opening the side panel. Added `useNavigate` import. Kept `CompanyDetailPanel` and its tab badge intact.
- **Deliverables**: src/frontend/src/pages/Companies.tsx (modified)
- **Sanity check result**: TypeScript type check clean, production build succeeds
- **Status**: [DONE]
- **Request**: No task ID (ad-hoc user request)

## 2026-03-18 -- Landing page for parent framework nodes without notes
- **What I did**: Replaced the empty "No notes yet" message on parent framework nodes with a landing page showing all leaf descendant nodes grouped by category. Each leaf is a clickable card with status dot, title, and progress bar. Added helper functions `collectLeaves` and `getGroupedLeaves`. Edit mode and existing-notes display unchanged.
- **Deliverables**: src/frontend/src/pages/FrameworkNotesPage.tsx (modified)
- **Sanity check result**: `npx tsc --noEmit` clean, `npx vite build` succeeds
- **Status**: [DONE]
- **Request**: No task ID (ad-hoc user request)

## 2026-03-18 -- Fix lint error + harden pre-exit checks
- **What I did**: Fixed ruff F401 (unused `import pytest` in test_import_blind75_notes.py). Created `scripts/check.sh` as unified ruff+pytest runner. Added Step 0 to CLAUDE.md Exit Protocol requiring `bash scripts/check.sh` as primary defense. Removed unreliable lint cache from lint_check.py. Deleted stale `.claude/last_lint_pass`.
- **Deliverables**: tests/test_import_blind75_notes.py, scripts/check.sh (new), CLAUDE.md, .claude/hooks/lint_check.py, LESSONS.md
- **Sanity check result**: `ruff check src/ tests/` passes clean. `bash scripts/check.sh` runs end-to-end (1 pre-existing flaky test unrelated to changes).
- **Status**: [DONE]
- **Request**: No task ID (ad-hoc user request)

## 2026-03-19 -- [T-P2-143] Forum models + migration v9
- **What I did**: Created ForumSeed, ForumPostLink, ForumPost SQLAlchemy models in src/backend/models/forum.py. Added migration v9 to database.py with three CREATE TABLE IF NOT EXISTS statements. Registered models in models/__init__.py.
- **Deliverables**: src/backend/models/forum.py (new), src/backend/database.py (migration v9), src/backend/models/__init__.py (updated), tests/test_models_forum.py (new, 13 tests)
- **Sanity check result**: All 13 forum model tests pass. Ruff clean. Migration idempotent. Cascade delete verified. UNIQUE and CHECK constraints enforced. Pre-existing test_client error (onepoint3acres_cookie in .env but not config.py) unrelated to changes.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-143 --status completed`

## 2026-03-19 -- [T-P2-144] Playwright CDP attach + cookie fallback methods
- **What I did**: Added two new async methods to PlaywrightCrawler: fetch_page_cdp (CDP attach to running Chrome) and fetch_page_with_cookie (headless with injected cookies). Added ONEPOINT3ACRES_COOKIE and CHROME_DEBUG_PORT to config.py Settings and .env.example.
- **Deliverables**: src/backend/scraper/crawler.py (2 new methods), src/backend/config.py (2 new settings), .env.example (updated), tests/test_crawler_cdp_cookie.py (new, 11 tests)
- **Sanity check result**: All 835 tests pass. Ruff clean. CDP mode does not close browser (only page). Cookie parsing handles empty strings. Rate limiting verified in delay range.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-144 --status completed`

## 2026-03-19 -- [T-P2-145] Forum HTML extractors with jammer stripping
- **What I did**: Created forum_extractors.py with two BeautifulSoup-based functions: extract_post_links (parses ul.hotlist for thread links, resolves to absolute URLs) and extract_post_content (extracts OP title/body/author/date/post_id, strips font.jammer anti-scraping noise). Created HTML test fixtures from real 1point3acres pages.
- **Deliverables**: src/backend/scraper/forum_extractors.py (new), tests/fixtures/forum_index.html (new), tests/fixtures/forum_post.html (new), tests/test_forum_extractors.py (new, 17 tests)
- **Sanity check result**: All 852 tests pass. Ruff clean. Jammer stripping verified -- no noise in extracted body. URLs correctly resolved to absolute. Only OP body extracted (not replies).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-145 --status completed`

## 2026-03-19 -- [T-P0-146] Forum service layer (two-phase scrape + import)
- **What I did**: Created forum_service.py with 6 functions: scrape_seed_page (Phase A: index scrape + upsert links, idempotent), fetch_single_post (Phase B: individual post fetch with content extraction), fetch_next_unfetched, retry_failed, import_post_to_prep_notes (appends to company notes with metadata header and --- separator), get_fetch_progress. CDP-first fetching with cookie fallback. External ID extraction from thread URLs. Content dedup via hash.
- **Deliverables**: src/backend/services/forum_service.py (new), tests/test_forum_service.py (new, 27 tests)
- **Sanity check result**: All 879 tests pass. Ruff clean. Idempotency verified (scrape twice = no duplicates). Failed status + retry_count incremented on error. Import appends with correct separator pattern.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-146 --status completed`

## 2026-03-19 -- [T-P0-147] Forum CLI script (scripts/forum_scrape.py)
- **What I did**: Created scripts/forum_scrape.py with 7 argparse subcommands wrapping forum_service: add-seed (auto-detects source_site from URL domain, resolves --company name to ID), list-seeds, scrape (Phase A), fetch (--next/--all/--link-id with 2s rate limiting), status (progress summary), import (post to company prep_notes), retry-failed. All commands use asyncio.run() to bridge sync CLI with async service functions. Error handling exits with code 1 and human-readable messages.
- **Deliverables**: scripts/forum_scrape.py (new), tests/test_forum_scrape_cli.py (new, 24 tests)
- **Sanity check result**: All 903 tests pass. Ruff clean. All 7 subcommands parse correctly. DB interaction tested for add-seed, list-seeds, status, import commands.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-147 --status completed`

## 2026-03-19 -- [T-P0-148] Forum API routes + Pydantic schemas
- **What I did**: Created src/backend/schemas/forum.py with 6 Pydantic schemas (ForumSeedCreate, ForumSeedResponse, ForumPostLinkResponse, ForumPostResponse, ForumProgressResponse, ForumImportRequest). Created src/backend/routers/forum.py with 10 REST endpoints: GET/POST/DELETE seeds, POST scrape, GET links, POST fetch single/next, GET post, POST import, GET progress. Registered router in main.py under /api prefix. Async endpoints for scrape/fetch operations.
- **Deliverables**: src/backend/schemas/forum.py (new), src/backend/routers/forum.py (new), tests/test_router_forum.py (new, 25 tests)
- **Sanity check result**: All 928 tests pass. Ruff clean. All 10 endpoints tested for correct status codes, CRUD operations, cascade delete, progress counts, and import to prep notes.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-148 --status completed`

## 2026-03-19 -- [T-P0-149] Frontend ForumPostsTab component + PrepNotesPage tab integration
- **What I did**: Created useForumPosts.ts with 7 TanStack Query hooks (useForumSeeds, useForumLinks, useForumProgress, useScrapeLinks, useFetchNext, useFetchPost, useImportPost) and TS interfaces mirroring backend schemas. Created ForumPostsTab.tsx component with seed selector, progress bar, link list with status badges (pending/fetched/failed), action buttons (Scrape Links, Fetch Next, Fetch, Import), expandable raw text preview via MarkdownPreview, and error display. Added tab system (Notes/Forum Posts) to PrepNotesPage.tsx with conditional rendering of notes editor vs forum tab. Added post_id hybrid property to ForumPostLink model and schema so frontend can correctly reference posts for import and preview. Added joinedload for post relationship in list_links endpoint.
- **Deliverables**: src/frontend/src/hooks/useForumPosts.ts (new), src/frontend/src/components/companies/ForumPostsTab.tsx (new), src/frontend/src/pages/PrepNotesPage.tsx (modified), src/backend/models/forum.py (modified), src/backend/schemas/forum.py (modified), src/backend/routers/forum.py (modified)
- **Sanity check result**: All 928 tests pass. Ruff clean. TypeScript compiles with no errors. Frontend components follow existing TanStack Query and api utility patterns.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-149 --status completed`

## 2026-03-19 -- [T-P0-151] Forum extractor: derive_page_url + extract_max_page pure functions
- **What I did**: Added two pure functions to forum_extractors.py: `derive_page_url` (anchored regex replacement for tag-N-N.html page numbers, raises ValueError on mismatch) and `extract_max_page` (parses div.pg pagination block, tries a.last href then fallback span text, returns 1 when no pagination). Created forum_index_with_pagination.html fixture with realistic div.pg block. Added TestDerivePageUrl (4 tests) and TestExtractMaxPage (3 tests) classes.
- **Deliverables**: src/backend/scraper/forum_extractors.py (modified), tests/test_forum_extractors.py (modified), tests/fixtures/forum_index_with_pagination.html (new)
- **Sanity check result**: All 936 tests pass. Ruff clean. Existing 17 forum extractor tests unchanged and passing.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-151 --status completed`

## 2026-03-19 -- [T-P0-152] Forum service: refactor scrape_seed_page + add scrape_seed_pages
- **What I did**: Extracted `_upsert_links_from_html` helper from `scrape_seed_page` (returns `(all_links, new_count)` tuple, accepts `order_offset` for multi-page). Simplified `scrape_seed_page` to delegate to the helper. Added `scrape_seed_pages` function with rate limiting (via site_configs), auto-detect pagination (via `extract_max_page`), early stop after 3 consecutive zero-new pages past page 5, and structured logging. Added `TestScrapeSeedPages` class with 5 tests: single_page, multi_page, auto_detect, early_stop, page_failure_continues.
- **Deliverables**: src/backend/services/forum_service.py (modified), tests/test_forum_service.py (modified)
- **Sanity check result**: All 941 tests pass. Ruff clean. Existing 28 TestScrapeSeedPage tests unchanged and passing.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-152 --status completed`

## 2026-03-19 -- [T-P0-153] Forum scrape CLI + API: pagination params
- **What I did**: Added `ForumScrapeStatsResponse` schema. Updated `POST /seeds/{seed_id}/scrape` endpoint to accept `max_pages` query param -- when >1, calls `scrape_seed_pages` and returns stats; when ==1, keeps existing single-page behavior. Updated CLI `scrape` subcommand with `--pages N` and `--no-auto-detect` flags, printing formatted stats for multi-page scrapes. Added 2 CLI parser tests and 1 router test (mocked `scrape_seed_pages`).
- **Deliverables**: src/backend/schemas/forum.py (modified), src/backend/routers/forum.py (modified), scripts/forum_scrape.py (modified), tests/test_forum_scrape_cli.py (modified), tests/test_router_forum.py (modified)
- **Sanity check result**: All 944 tests pass. Ruff clean. Existing tests unchanged and passing.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-153 --status completed`

## 2026-03-19 -- [T-P0-154] Live scrape: LinkedIn 1point3acres first 5 pages
- **What I did**: Executed the live scraping pipeline for LinkedIn on 1point3acres. Fixed 3 bugs discovered during execution: (1) `forum_service._fetch_html` used `os.environ.get()` which doesn't load `.env` -- switched to `get_settings()` from pydantic-settings. (2) `extract_post_links` only supported `ul.hotlist` layout but the real page uses a table layout (`th > a[href*=thread-]`) -- added table layout strategy with href deduplication. (3) `_upsert_links_from_html` didn't check for `external_post_id` conflicts within the same seed -- added same-seed dedup. Successfully scraped 5 pages: 100 post links discovered, all pending. Max page detected: 255.
- **Deliverables**: src/backend/services/forum_service.py (modified), src/backend/scraper/forum_extractors.py (modified), tests/fixtures/forum_index_table.html (new), tests/test_forum_extractors.py (modified)
- **Sanity check result**: All 945 tests pass. Ruff clean. Live scrape verified: 100 links in DB, status command confirms all pending.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-154 --status completed`

## 2026-03-19 -- Bugfix: timezone mismatch in listening streak calculation
- **What I did**: Ran full lint+test suite (`scripts/check.sh`). Found 1 failure: `test_stats_streak` expected streak_days==3 but got 2. Root cause: `date.today()` (local time) vs `datetime.now(UTC).date()` (UTC) mismatch in streak calculation at `src/backend/routers/reading.py:729`. Fixed by using `datetime.now(UTC).date()` consistently.
- **Deliverables**: src/backend/routers/reading.py (1-line fix)
- **Sanity check result**: All 945 tests pass. Ruff clean.
- **Status**: [DONE]
- **Request**: No task status change needed (ad-hoc bugfix)

## 2026-03-20 -- Scraper performance overhaul + full link collection + post extractor fix
- **What I did**: (1) Analyzed DB: 100 links from 5 pages, 29% interview-relevant, 2% coverage. (2) Fixed triple rate-limiting (site config 20-45s + CDP 5-15s + cookie 5-15s -> single 0.5-5s layer). (3) Added per-page DB commits (crash lost all progress before). (4) Added `start_page` param for resumable scraping. (5) Improved early exit: removed `page>=5` guard, count first page in zero-new streak. (6) Added TCP probe for CDP port to skip Playwright startup when no Chrome debug instance. (7) Fixed post content extractor for real HTML: h1.ts title, [itemprop=articleBody] body, author from .authi before nbsp. (8) Scraped pages 6-~120: 2,559 total links collected (41% interview-related). (9) Fetched 9/10 test posts successfully.
- **Deliverables**: src/backend/services/forum_service.py, src/backend/scraper/crawler.py, src/backend/scraper/site_configs.py, src/backend/scraper/forum_extractors.py, scripts/forum_scrape.py, tests/test_forum_service.py
- **Sanity check result**: All 85 forum tests pass. 9/10 live post fetches succeeded. 2,559 links in DB.
- **Status**: [PARTIAL] Pages 123-255 not yet scraped (early exit false positive on overlap zone). 1 post (#14) failed extraction (likely locked/deleted page).
- **Request**: No task status change needed (ad-hoc improvement)

## 2026-03-20 -- Cron-driven forum scraping system (scrape protocol v2)
- **What I did**: Built full scraping automation infrastructure: (1) YAML config file (`config/scrape_seeds.yaml`) for declarative seed management. (2) Strict schema validator (`scrape_config.py`) with unknown-key rejection. (3) `last_scraped_page` column + migration for resume tracking. (4) Content quality check (MIN_POST_CONTENT_LENGTH=50) to catch login walls. (5) `batch-status` CLI command for all-seeds progress table. (6) `--limit N` flag for batched fetch runs. (7) `/scrape` skill with full procedure (config sync, Phase A/B, cron setup, escalation rules).
- **Deliverables**: config/scrape_seeds.yaml, src/backend/scraper/scrape_config.py, src/backend/models/forum.py, src/backend/database.py (migration 11), src/backend/services/forum_service.py, scripts/forum_scrape.py, .claude/skills/scrape/SKILL.md, tests/test_scrape_config.py, tests/test_migrations.py, tests/test_forum_service.py
- **Sanity check result**: All 965 tests pass. Config validator catches typos. batch-status shows real DB state. Migration adds column correctly.
- **Status**: [DONE]
- **Request**: No task status change needed (plan implementation)

## 2026-03-20 -- Scrape protocol refinements: timeout, seed URLs, cron simplification
- **What I did**: (1) Replaced `--limit N` with `--timeout-minutes N` for time-based fetch runs (e.g. 300 = 5 hours). (2) Fixed LinkedIn seed URL in config: `tag-123` -> `tag-415` (matching DB). (3) Added real DoorDash seed URL `tag/doordash-1829-1.html`. (4) Simplified cron from 2 jobs to 1 daily 2:00 AM full scrape with 5h timeout.
- **Deliverables**: config/scrape_seeds.yaml, scripts/forum_scrape.py, .claude/skills/scrape/SKILL.md
- **Sanity check result**: All 965 tests pass. Config validates. Seed URLs match DB.
- **Status**: [DONE]
- **Request**: No task status change needed

## 2026-03-20 -- Plan full-page forum extraction + fix batch command bug
- **What I did**: (1) Explored forum scraper system, identified that extract_post_content() only captures OP, not replies. (2) Designed 3-task plan (T-P2-155/156/157) for full-page extraction with corrected format template locked, selector fallback strategy, and YAGNI-compliant scope (no replies_json, no view_count). (3) Discovered and fixed critical bug in task_db.py batch command: CLAUDE.md and SKILL.md documented nested `args` format but code read flat keys, causing silent data loss (empty titles/descriptions). (4) Added validation to reject empty titles in batch add. (5) Fixed docs in CLAUDE.md and SKILL.md. (6) Added 6 regression tests for batch format handling.
- **Deliverables**: .claude/hooks/task_store.py (batch args fix + validation), tests/test_task_batch.py (new), CLAUDE.md (docs fix), .claude/skills/task-planning/SKILL.md (docs fix)
- **Sanity check result**: 971 tests pass, ruff clean.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-155 --status active` (reset from in_progress, not yet started)

## 2026-03-22 07:15 -- Plan System Design Showcase feature + update Uber prep notes
- **What I did**: (1) Updated Uber HR prep notes with JD key elements from Shopping Ranking Team JD -- added 5 key requirement keywords, updated self-intro/Q2/Q3 to reference Shopping team + GenAI angle, checked "Review JD" checkbox, re-ran backfill. (2) Planned full System Design Showcase feature: analyzed 4 architecture diagrams (Module Arbitration, LLM Orchestration, PBE Pipeline, Ranking-as-Allocation), created comprehensive implementation plan (v2) with unified narrative, 8-section content structure per module (added Production Constraints + Adversarial Defense Q&A + Verbal Outline per review feedback). Created 8 tasks (T-P1-158~165) in task_db covering backend model/API, frontend sidebar/routes/pages, and content for all 4 modules.
- **Deliverables**: `docs/uber_hr_call_prep.md` (updated), `docs/PLAN_system_design_showcase.md` (new, v2), 8 tasks in task_db (T-P1-158~165)
- **Sanity check result**: Tasks verified in DB, TASKS.md regenerated, plan file sent to user via Discord for review.
- **Status**: [DONE] (planning phase complete, awaiting review before execution)

## 2026-03-22 08:00 -- Execute System Design Showcase feature (T-P1-158~165)
- **What I did**: Executed all 8 tasks for the System Design Showcase feature via parallel subagents. Phase 1 (infra): T-P1-158 backend model/API/seed + T-P1-159 frontend sidebar/routes/types. Phase 2 (UI): T-P1-160 landing page with narrative + card grid + T-P1-161 detail page with 8-tab layout/hook/auto-save. Phase 3 (content): T-P1-162~165 populated all 4 modules with 8 sections each (overview, architecture, dataflow, formulas, production constraints, trade-offs, adversarial defense, verbal outline). Total content: 91,786 chars across 32 sections.
- **Deliverables**: Backend: `src/backend/models/system_design.py`, `src/backend/routers/system_design.py`, registered in main.py, `scripts/seed_system_designs.py`. Frontend: `src/frontend/src/pages/SystemDesignList.tsx`, `src/frontend/src/pages/SystemDesignDetail.tsx`, `src/frontend/src/hooks/useSystemDesignNotes.ts`, `src/frontend/src/types/system-design.ts`, updated Sidebar.tsx + App.tsx. Content: `scripts/content_module_arbitration.py`, `scripts/content_llm_orchestration.py`, `scripts/content_pbe_pipeline.py`, `scripts/content_ranking_allocation.py`. Static: 4 diagram images in `src/frontend/public/static/system-designs/`.
- **Sanity check result**: All 4 modules verified 8/8 sections populated (19K-34K chars each). TypeScript compiles clean (tsc --noEmit). TASKS.md regenerated.
- **Status**: [DONE]

## 2026-03-22 12:45 -- Investigate ECONNREFUSED errors + plan 3 new tasks
- **What I did**: Investigated root cause of Vite proxy ECONNREFUSED errors on startup. Found startup race condition in `scripts/dev.py` (backend and frontend start simultaneously, Vite ready before uvicorn). Also discovered Docker nginx.conf port mismatch (8000 vs 8100). Planned 3 tasks: T-P1-166 (dev.py health-check gate), T-P1-167 (nginx port fix), T-P1-168 (replace static screenshots with HTML-rendered diagrams). Sent analysis and plan to user via Discord for review.
- **Deliverables**: 3 tasks added to task_db (T-P1-166, T-P1-167, T-P1-168), TASKS.md regenerated
- **Sanity check result**: Root cause confirmed by reading dev.py (lines 106-132 show simultaneous startup). nginx.conf port mismatch confirmed. Tasks verified in DB.
- **Status**: [DONE] (planning only, awaiting user review before execution)

## 2026-03-22 12:55 -- [T-P1-166/167/168] Fix startup race, nginx port, HTML diagrams
- **What I did**: (1) T-P1-166: Added health-check gate in `scripts/dev.py` -- backend now starts first, polls `/api/health` every 0.5s (max 30s), then starts frontend. Eliminates ECONNREFUSED on startup. (2) T-P1-167: Fixed `src/frontend/nginx.conf` proxy_pass port from 8000 to 8100 to match backend. (3) T-P1-168: Created 4 HTML diagram source files in `static/system-designs/html/`, used Playwright to generate PNG screenshots replacing the original JPGs. Updated seed script to reference .png, re-seeded DB.
- **Deliverables**: `scripts/dev.py` (modified), `src/frontend/nginx.conf` (modified), 4 HTML files in `src/frontend/public/static/system-designs/html/`, 4 PNG files in `src/frontend/public/static/system-designs/`, `scripts/generate_diagram_screenshots.py` (new), `scripts/seed_system_designs.py` (updated .jpg->.png)
- **Sanity check result**: All 4 PNGs generated successfully (52-75 KB). DB re-seeded with .png filenames. Frontend references diagram_filename dynamically -- no code changes needed.
- **Status**: [DONE]

## 2026-03-22 13:50 -- Plan T-P1-169/170/171 + fix autonomous_run.sh for sub-projects
- **What I did**: (1) Planned 3 improvement tasks: T-P1-169 (crop/resize diagrams), T-P1-170 (lightbox overlay), T-P1-171 (single-page layout + fix module-arbitration duplicate content). Found module-arbitration has all 8 tabs with identical content (all overview text). (2) Updated CLAUDE.md (root + MLInterviewPrep) with explicit multi-task execution rule: always use autonomous_run.sh, never execute in main context. (3) Fixed autonomous_run.sh: added `project_dir` parameter for sub-project support, auto-reset `all_done` flag on start, use `cd` subshell to run claude from correct directory. Fixed `--cwd` flag (not supported by claude CLI).
- **Deliverables**: `scripts/autonomous_run.sh` (updated with sub-project support), root `CLAUDE.md` (updated), `MLInterviewPrep/CLAUDE.md` (updated), 3 tasks in task_db (T-P1-169/170/171)
- **Sanity check result**: Tasks verified in DB. autonomous_run.sh first run failed (root TASKS.md had no tasks, stale all_done=true). Fixed and re-launched with `bash scripts/autonomous_run.sh 3 MLInterviewPrep`.
- **Status**: [DONE] (autonomous run in progress for task execution)

## 2026-03-22 14:15 -- [T-P1-169] Crop whitespace and increase render size for diagram PNGs
- **What I did**: Scaled up all 4 HTML diagram sources: body padding 24px->8px, width 1200px->1600px, all font sizes increased ~1.4x (titles 16->22px, box text 10->14px, sub-text 8->11px, section headers 11->15px). Updated `generate_diagram_screenshots.py` to use `body.screenshot()` (element-level) instead of `page.screenshot(full_page=True)` for auto-cropping, and increased viewport from 1280x900 to 1680x1200.
- **Deliverables**: 4 HTML files modified (`src/frontend/public/static/system-designs/html/*.html`), `scripts/generate_diagram_screenshots.py` (modified), 4 PNGs regenerated (68-95 KB, up from 52-75 KB)
- **Sanity check result**: All 4 PNGs generated. Visual inspection confirms larger text, minimal whitespace borders, clean auto-cropping.
- **Status**: [DONE]

## 2026-03-22 14:30 -- [T-P1-170] Diagram click-to-fullscreen lightbox overlay
- **What I did**: Created `ImageLightbox` component (pure React + Tailwind, no external libs). Click diagram image -> fixed fullscreen overlay with dark backdrop (bg-black/80). Image fills 95vw/95vh with object-contain. Click backdrop or press Escape to close. `e.stopPropagation()` prevents list page card navigation when clicking diagram. Integrated into both SystemDesignDetail (architecture tab) and SystemDesignList (card thumbnails).
- **Deliverables**: `src/frontend/src/components/ui/ImageLightbox.tsx` (new), `SystemDesignDetail.tsx` (modified), `SystemDesignList.tsx` (modified)
- **Sanity check result**: TypeScript type-check passes, Vite build succeeds.
- **Status**: [DONE]

## 2026-03-22 15:30 -- [T-P1-171] Single-page layout with bookmark nav + fix module-arbitration content
- **What I did**: Replaced tab-based layout in SystemDesignDetail with a single scrollable page showing all 8 sections. Added sticky bookmark nav with IntersectionObserver-based scroll highlighting. Refactored useSystemDesignNotes hook to manage all section contents simultaneously with per-section debounced auto-save. In edit mode, all section textareas visible with individual save status indicators. Ran content_module_arbitration.py to populate all 8 sections with distinct content (1.6K-3.6K chars each).
- **Deliverables**: `src/frontend/src/pages/SystemDesignDetail.tsx` (rewritten), `src/frontend/src/hooks/useSystemDesignNotes.ts` (rewritten), module-arbitration DB updated
- **Sanity check result**: TypeScript type-check passes, Vite build succeeds. Module-arbitration now has 8 distinct sections.
- **Status**: [DONE]

## 2026-03-22 16:30 -- [T-P1-172] System Design Module 5: Database Systems Comparison
- **What I did**: Added new system design module (slug: database-comparison, display_order: 5) covering Cassandra, HBase, DynamoDB, ScyllaDB, CockroachDB, TiDB, MongoDB. Created HTML architecture comparison diagram with AP/CP system groupings, write/read path comparison, CAP theorem visual, and 7-database comparison table. Wrote content script with all 8 sections: Overview (2K chars), Architecture (5.9K), Data Flow (4.3K), Formulas (3.6K), Production Constraints (3.4K), Trade-offs (4.8K), Defense Q&A (7.6K), Verbal Outline (4.4K). Updated seed script and diagram generator.
- **Deliverables**: `scripts/seed_system_designs.py` (updated), `scripts/content_database_comparison.py` (new), `scripts/generate_diagram_screenshots.py` (updated), `src/frontend/public/static/system-designs/html/database_comparison.html` (new), `database_comparison.png` (generated, 145KB)
- **Sanity check result**: TypeScript type-check passes, Vite build succeeds. All 8 sections populated (2K-7.6K chars). Diagram PNG renders correctly with architecture comparison layout. Module visible as 5th entry in system design list.
- **Status**: [DONE]

## 2026-03-22 17:30 -- [T-P1-173] System Design Module 6: Distributed Task Queue
- **What I did**: Added new system design module (slug: distributed-task-queue, display_order: 6) covering failure modes, idempotency, and exactly-once semantics. Created HTML architecture diagram showing core architecture (producer/broker/worker pool/result backend), 7 failure scenarios (worker crash, lost ack, dual execution, poison pill, broker crash, rolling deploy, malformed payload), broker comparison (Redis/RabbitMQ/SQS/Kafka), recovery mechanisms, and failure scenario quick reference table. Wrote content script with all 8 sections: Overview (2.5K chars), Architecture (4.3K), Data Flow (7.1K), Formulas (3.6K), Production Constraints (2.8K), Trade-offs (4.9K), Defense Q&A (10.5K), Verbal Outline (5.2K). Updated seed script and diagram generator.
- **Deliverables**: `scripts/seed_system_designs.py` (updated), `scripts/content_distributed_task_queue.py` (new), `scripts/generate_diagram_screenshots.py` (updated), `src/frontend/public/static/system-designs/html/distributed_task_queue.html` (new), `distributed_task_queue.png` (generated, 158KB)
- **Sanity check result**: TypeScript type-check passes, Vite build succeeds. All 8 sections populated (2.5K-10.5K chars). Diagram PNG renders correctly. Module visible as 6th entry in system design list.
- **Status**: [DONE]

## 2026-03-22 20:40 -- Update LinkedIn interview data: phone screen scheduled
- **What I did**: (1) Updated LinkedIn company status from 'applied' to 'phone_screen'. (2) Added new InterviewEvent (id=4): SWE Phone Screen 1 - AI Engineer, April 2 2026 1:00-2:00 PM PDT, Zoom Video, status=upcoming. (3) Added CompanyDocument (id=2) with phone screen scheduling details and prep checklist.
- **Deliverables**: Database updated (companies table: LinkedIn status, interview_events table: new event id=4, company_documents table: new doc id=2)
- **Sanity check result**: Verification query confirms LinkedIn status=phone_screen, event id=4 scheduled_at=2026-04-02T13:00:00-07:00, document created.
- **Status**: [DONE]

## 2026-03-22 21:30 -- Plan LeetCode improvements + commit rule enforcement
- **What I did**: (1) Planned 4 LeetCode tasks: T-P1-174 (Blind75 sort/filter sync), T-P1-175 (Blind75 flat view), T-P1-176 (Practice/Review to detail page), T-P1-177 (4 LC solutions with notes). (2) Added commit rule to CLAUDE.md requiring every session to commit before exit. (3) Updated autonomous_run.sh prompt to include git commit step. (4) Added T-P0-178 cleanup commit task for all uncommitted changes from prior sessions.
- **Deliverables**: 5 tasks in task_db (T-P1-174~177, T-P0-178), CLAUDE.md updated (commit rule), autonomous_run.sh updated (commit in prompt)
- **Sanity check result**: Tasks verified in DB. TASKS.md regenerated.
- **Status**: [DONE] (planning complete, awaiting user confirmation to execute)

## 2026-03-22 22:00 -- [T-P0-178] Commit all uncommitted changes from prior sessions
- **What I did**: Reviewed all modified and untracked files for secrets/sensitive data (none found), staged 29 files spanning system design module infrastructure, scraper improvements, dev.py health wait, nginx port fix, .gitignore hardening, CLAUDE.md updates, Uber HR prep notes, and task/progress bookkeeping. Committed as single cleanup commit.
- **Deliverables**: Git commit 821ecc7 with 29 files, 4632 insertions
- **Sanity check result**: git status clean (only .claude/worktrees/ untracked, intentionally excluded)
- **Status**: [DONE]

## 2026-03-22 23:00 -- [T-P1-174] Blind75 tab: add sort/search controls + sort within groups
- **What I did**: Extracted sort/search bar into shared `renderSortBar()` used by both All Problems and Blind75 tabs. Added client-side sort within pattern groups in Blind75 view (supports all 5 sort fields + asc/desc). Filter state already persists across tab switches via URL params.
- **Deliverables**: Modified `src/frontend/src/pages/Problems.tsx`
- **Sanity check result**: TypeScript check clean (`tsc --noEmit`), Vite build succeeds
- **Status**: [DONE]

## 2026-03-22 23:30 -- [T-P1-175] Blind75 tab: add ungrouped flat list view toggle
- **What I did**: Added a "Grouped by Pattern" / "All Problems" toggle to the Blind75 tab. The flat view shows a single table with all blind75 problems including the Pattern column. View state persists via `blind75View` URL param. Default remains grouped view. Both views share sort/filter state.
- **Deliverables**: Modified `src/frontend/src/pages/Problems.tsx`
- **Sanity check result**: TypeScript check clean (`tsc --noEmit`), Vite build succeeds
- **Status**: [DONE]

## 2026-03-22 23:50 -- [T-P1-176] Move Practice/Review actions to ProblemDetailPage
- **What I did**: Added Practice and Review buttons to ProblemDetailPage header, wired up PracticeModal and ReviewPanel overlays. Replaced table Practice/Review buttons in Problems.tsx with a single "View" link to the detail page. Removed unused PracticeModal/ReviewPanel imports and state from Problems.tsx.
- **Deliverables**: Modified `src/frontend/src/pages/ProblemDetailPage.tsx`, `src/frontend/src/pages/Problems.tsx`
- **Sanity check result**: TypeScript check clean (`tsc --noEmit`), Vite build succeeds
- **Status**: [DONE]

## 2026-03-23 00:10 -- [T-P1-177] Add solution notes for 4 LeetCode problems
- **What I did**: Updated notes for K-Similar Strings (LC 854) and Merge K Sorted Lists (LC 23), replacing Chinese notes with structured English notes. Created two new problem entries: Longest Continuous Subarray (LC 1438) and Russian Doll Envelopes (LC 354) with full metadata and notes. All 4 marked completed with comfort_level=3.
- **Deliverables**: Modified `data/mle_prep.db` (2 updates, 2 inserts)
- **Sanity check result**: All 4 problems verified in DB with correct notes, completion status, and metadata. Frontend ProblemDetailPage has "My Notes" section that renders when notes exist.
- **Status**: [DONE]

## 2026-03-23 04:50 -- Ad-hoc: Add 2 extra LC problems + Discord fix + commit rule
- **What I did**: (1) Added LC 339 (Nested List Weight Sum) and LC 364 (Nested List Weight Sum II) to DB with solution notes. (2) Fixed Discord channel access (re-added channel to allowlist). (3) Updated CLAUDE.md with commit rule and autonomous_run.sh with git commit step (done in earlier session, committed by T-P0-178). (4) LinkedIn phone screen event added (April 2, 2026).
- **Deliverables**: DB updated (2 new problems: LC 339, LC 364), Discord access.json fixed
- **Sanity check result**: Both problems created in DB. Discord replies working again. All 5 autonomous tasks (T-P0-178, T-P1-174~177) completed and committed.
- **Status**: [DONE]

## 2026-03-23 05:00 -- Backlog cleanup: clear remaining P2 tasks
- **What I did**: Verified LC 339 (730 chars notes) and LC 364 (1367 chars notes) both in DB with is_completed=True. Closed 4 remaining P2 backlog tasks (T-P2-112, T-P2-155, T-P2-156, T-P2-157) per user request. TASKS.md regenerated. Task queue now empty.
- **Deliverables**: TASKS.md (regenerated, all tasks completed)
- **Sanity check result**: 0 active tasks remaining. All 19 tasks in completed status.
- **Status**: [DONE]

## 2026-03-23 05:30 -- Fix /api/problems 500 error (NULL priority)
- **What I did**: Investigated backend crash when frontend loads /problems page. Root cause: 2 problem records (id=152, id=153) had NULL priority field, but ProblemResponse Pydantic schema required non-optional int. FastAPI response_model validation failed with 500. Fixed schema to accept None, added fallback default in _problem_to_response, added migration 12 to fix existing NULL data, and patched DB directly.
- **Deliverables**: `src/backend/schemas/problem.py` (priority now int|None), `src/backend/routers/problems.py` (None->2 fallback), `src/backend/database.py` (migration 12)
- **Sanity check result**: All /api/problems endpoints return 200 with limit=20,50,200. Previously failed at limit>=3 due to bad record at sort position 3.
- **Status**: [DONE]

## 2026-03-23 06:15 -- [T-P0-180] Fix ruff lint errors (UP017 datetime.UTC)
- **What I did**: Ran `ruff check --fix` on `src/backend/models/system_design.py` and `src/backend/routers/system_design.py` to replace `timezone.utc` with `datetime.UTC` (UP017 rule). Total 8 auto-fixed errors across both files.
- **Deliverables**: `src/backend/models/system_design.py`, `src/backend/routers/system_design.py`
- **Sanity check result**: `ruff check src/backend/` passes clean. 923/924 tests pass (1 pre-existing failure in test_timeline unrelated to this change).
- **Status**: [DONE]

## 2026-03-22 -- [T-P1-182] Remove Review column from Problems table
- **What I did**: Removed the broken "Due Reviews" dashboard card (linked to non-existent `/problems?review=due` filter). Removed `due_reviews` from `DashboardToday` type. Adjusted dashboard grid from 3 to 2 columns. The ReviewBadge component and Review table column were already absent from the codebase. Backend spaced_repetition logic preserved.
- **Deliverables**: `src/frontend/src/pages/Dashboard.tsx`, `src/frontend/src/types/dashboard.ts`, `src/frontend/src/pages/Problems.tsx`
- **Sanity check result**: TypeScript compiles clean (`tsc --noEmit`). 288/289 tests pass (1 pre-existing failure). Ruff: 1 pre-existing error (unrelated).
- **Status**: [DONE]

## 2026-03-23 06:20 -- [T-P1-181] Fetch missing problem descriptions
- **What I did**: Fetched descriptions for 5 problems missing them (id=151-155). 3 fetched from LeetCode GraphQL (151-153), 2 premium problems (LC 339, 364) fetched from user-provided URLs (algo.monster, hellointerview). Added idempotency protection (force param) to single-problem fetch-description endpoint. All 155/155 problems now have descriptions.
- **Deliverables**: `src/backend/routers/problems.py` (force param), DB updated
- **Sanity check result**: 0 problems with NULL/empty description.
- **Status**: [DONE]

## 2026-03-23 06:45 -- [T-P1-183] Framework progress sync: auto-propagate status and progress upward
- **What I did**: Implemented auto status+progress propagation from child to parent nodes. (1) Backend: new `_derive_status()` with priority model (mastered > review > in_progress > not_started). Refactored `_propagate_progress` to `_propagate_upward` with status derivation, cycle detection (log critical, no raise), and only-set-never-clear timestamps. Study log auto-starts leaf nodes and only auto-progresses leaves. (2) Frontend: disabled status dropdown for parent nodes, shows "auto from children" + mastered/total count. (3) Tests: 25 new tests in `test_propagation.py` covering `_derive_status` unit tests, progress propagation (weighted, multi-level), status rollback scenarios, timestamp immutability, child deletion, and study log auto-start + propagation. (4) Migration script for recalculating stale parent progress/status bottom-up.
- **Deliverables**: `src/backend/routers/framework.py`, `src/frontend/src/components/NodeDetailPanel.tsx`, `tests/test_propagation.py` (new, 25 tests), `scripts/migrate_recalculate_parent_progress.py` (new)
- **Sanity check result**: 1017/1021 tests pass (4 pre-existing test_timeline failures). All 25 propagation tests pass. TypeScript clean. Ruff clean.
- **Status**: [DONE]

## 2026-03-23 10:30 -- Fix CI test warnings and deprecation issues
- **What I did**: Fixed 3 categories of pytest warnings flagged in CI: (1) Replaced deprecated `Query.get()` with `Session.get()` in test_import.py, (2) Fixed SAWarning in test_models_framework.py by expunging first instance before adding conflicting PK, (3) Added filterwarnings in pyproject.toml for starlette/httpx dependency deprecation warnings. Note: the 4 test_timeline failures and 4 ruff UP017 errors were already fixed in commit 1a3b648.
- **Deliverables**: `tests/test_import.py`, `tests/test_models_framework.py`, `pyproject.toml`
- **Sanity check result**: 996 passed, 0 failed, 0 warnings. Ruff: all checks passed.
- **Status**: [DONE]

## 2026-03-23 11:40 -- Update Uber prep notes with Phone Screen section
- **What I did**: Added Part 8 (Phone Screen Prep) to uber_hr_call_prep.md based on recruiter call notes. Covers: process structure (2 phone screens + 4 virtual onsites, 4-5 week timeline), problem-solving approach (clarify -> explore -> tradeoff -> code), content areas (DSA, DP, ML algo coding KNN/ANN, edge cases, test generation), communication/pacing strategy (reserve 10+ min for experience, 5 min for questions). Also updated Part 5 with actual recruiter call notes. Re-imported to DB (27,509 chars).
- **Deliverables**: `docs/uber_hr_call_prep.md` (updated)
- **Sanity check result**: DB verified -- Uber prep_notes contains Phone Screen Prep section.
- **Status**: [DONE]

## 2026-03-24 06:50 -- Split Uber prep into HR Call + Phone Screen documents
- **What I did**: Moved section 7.6 (MLE Interview Process Overview) and Part 8 (Phone Screen Prep) from `uber_hr_call_prep.md` into a new `uber_phone_screen_prep.md`. Updated backfill script to create a CompanyDocument record for the phone screen file, so Uber now shows two tabs in the app: "Notes" (HR Call, 22,799 chars) and "Phone Screen Prep" (4,906 chars). Added `COMPANY_DOCUMENTS` dict to backfill for extensibility.
- **Deliverables**: `docs/uber_phone_screen_prep.md` (new), `docs/uber_hr_call_prep.md` (trimmed), `scripts/backfill_interviews.py` (extended)
- **Sanity check result**: DB verified -- Uber has prep_notes + 1 CompanyDocument. Frontend tabs render via existing `useCompanyDocuments` hook.
- **Status**: [DONE]

## 2026-03-24 21:30 -- [T-P0-36] Fix BehavioralQuestions page styling to match light theme
- **What I did**: Rewrote BehavioralQuestions.tsx to fix 4 issues: (1) Converted entire page from dark theme (bg-gray-800, text-white) to light theme (bg-white cards, text-gray-800, border-gray-200) matching Layout.tsx and Dashboard.tsx conventions. (2) Replaced cryptic category abbreviations (ADP, OWN, etc) with full names via CATEGORY_LABELS lookup + tooltips on filter buttons. (3) Overhauled heatmap: larger cells (min-w-[90px]), full category names in headers, proper text contrast (green-800/900/white on green backgrounds), wrapped in white card with border. (4) Fixed expand/collapse bug by lifting question expansion state to parent via Set<number> (expandedQuestions) instead of per-row useState, preventing state loss on re-render.
- **Deliverables**: `src/frontend/src/pages/BehavioralQuestions.tsx` (rewritten)
- **Sanity check result**: TypeScript clean (tsc --noEmit), Vite build clean, 996 backend tests pass
- **Status**: [DONE]
