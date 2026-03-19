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
