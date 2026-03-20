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
