# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-147: Forum CLI script (scripts/forum_scrape.py)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-146
- **Description**: Create scripts/forum_scrape.py as the primary CLI interface wrapping the forum service layer.

**Subcommands (via argparse):**
- `add-seed <url> [--company <name>] [--label <text>]` -- Create ForumSeed. Auto-detect source_site from URL domain. If --company provided, look up Company by name and set company_id.
- `list-seeds` -- Print all ForumSeeds with id, url, label, company, last_scraped_at.
- `scrape <seed_id>` -- Phase A: call scrape_seed_page(), print discovered link count.
- `fetch <seed_id> [--next | --all | --link-id <id>]` -- Phase B: --next fetches next pending, --all fetches all pending sequentially with delay, --link-id fetches specific link.
- `status <seed_id>` -- Print fetch progress: total/pending/fetched/failed counts.
- `import <post_id> --company <name>` -- Import raw_text to company prep_notes.
- `retry-failed <seed_id>` -- Call retry_failed(), print results.

**Implementation:**
- Use asyncio.run() to bridge sync argparse with async service functions.
- Initialize DB via init_db(), get session via SessionLocal().
- Instantiate PlaywrightCrawler() for scrape/fetch commands.
- Print results in human-readable format (not JSON).

**Error handling:** Catch exceptions, print user-friendly error messages, exit with code 1 on failure.

**AC:**
1. All 7 subcommands parse correctly and call the right service function
2. add-seed auto-detects source_site=1point3acres from URL
3. add-seed with --company resolves company name to company_id
4. scrape prints discovered link count
5. fetch --all processes all pending links with rate limiting
6. status prints progress summary
7. import appends to prep_notes successfully
8. retry-failed resets and re-fetches failed links
9. Smoke test: manual run with real seed URL (requires Chrome with CDP or cookie)

#### T-P0-148: Forum API routes + Pydantic schemas
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-146
- **Description**: Create src/backend/routers/forum.py and src/backend/schemas/forum.py for the forum scraping REST API.

**Schemas (src/backend/schemas/forum.py):**
- ForumSeedCreate: url (str, min_length=1), source_site (Literal["1point3acres"]), label (str|None), company_id (int|None)
- ForumSeedResponse: id, url, source_site, label, company_id, is_active, last_scraped_at, created_at. model_config = ConfigDict(from_attributes=True)
- ForumPostLinkResponse: id, forum_seed_id, url, external_post_id, title, discovered_at, status, retry_count, last_error, fetch_order. from_attributes=True
- ForumPostResponse: id, forum_post_link_id, raw_text, content_hash, author, published_at, fetched_at, company_id. from_attributes=True
- ForumProgressResponse: total (int), pending (int), fetched (int), failed (int), last_fetched_url (str|None)
- ForumImportRequest: company_id (int)

**Endpoints (src/backend/routers/forum.py):**
| Method | Path | Purpose |
|--------|------|---------|
| GET | /forum/seeds | List seeds (optional query params: company_id, source_site) |
| POST | /forum/seeds | Add seed (body: ForumSeedCreate) |
| DELETE | /forum/seeds/{id} | Remove seed + cascade |
| POST | /forum/seeds/{id}/scrape | Phase A: collect links (returns list of ForumPostLinkResponse) |
| GET | /forum/seeds/{id}/links | List post links with status (returns list of ForumPostLinkResponse) |
| POST | /forum/links/{id}/fetch | Phase B: fetch single post (returns ForumPostResponse) |
| POST | /forum/seeds/{id}/fetch-next | Fetch next unfetched (returns ForumPostResponse or 204) |
| GET | /forum/posts/{id} | Get raw post content (returns ForumPostResponse) |
| POST | /forum/posts/{id}/import | Import to prep notes (body: ForumImportRequest, returns company) |
| GET | /forum/seeds/{id}/progress | Fetch progress (returns ForumProgressResponse) |

**Router registration:** Add to main.py: `from src.backend.routers.forum import router as forum_router` and `app.include_router(forum_router, prefix="/api")`

**DB session:** Use `db: Session = Depends(get_db)` pattern matching existing routers.

**Async endpoints:** scrape and fetch endpoints must be async (they call async service functions). Use run_in_executor or make the endpoint async and await the service.

**AC:**
1. All 10 endpoints return correct HTTP status codes
2. POST /forum/seeds creates seed and returns ForumSeedResponse
3. POST /forum/seeds/{id}/scrape returns list of discovered links
4. POST /forum/links/{id}/fetch returns fetched post content
5. GET /forum/seeds/{id}/progress returns accurate counts
6. POST /forum/posts/{id}/import appends to prep notes and returns updated company
7. DELETE cascade works (seed + links + posts removed)
8. Router registered in main.py under /api prefix
9. Tests: tests/test_router_forum.py with TestClient + in-memory DB

#### T-P0-149: Frontend ForumPostsTab component + integration into PrepNotesPage
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-148
- **Description**: Create ForumPostsTab React component and integrate it as a tab in the existing PrepNotesPage.

**New files:**
1. `src/frontend/src/components/companies/ForumPostsTab.tsx` -- Main tab component
2. `src/frontend/src/hooks/useForumPosts.ts` -- TanStack Query hooks for forum API

**useForumPosts.ts hooks:**
- useForumSeeds(companyId?: number) -- GET /api/forum/seeds?company_id=X
- useForumLinks(seedId: number) -- GET /api/forum/seeds/{id}/links
- useForumProgress(seedId: number) -- GET /api/forum/seeds/{id}/progress
- useFetchPost() -- mutation: POST /api/forum/links/{id}/fetch
- useFetchNext(seedId: number) -- mutation: POST /api/forum/seeds/{id}/fetch-next
- useImportPost() -- mutation: POST /api/forum/posts/{id}/import with {company_id}
- useScrapeLinks(seedId: number) -- mutation: POST /api/forum/seeds/{id}/scrape
Follow patterns from src/frontend/src/hooks/usePrepNotes.ts (TanStack useQuery/useMutation, queryClient.invalidateQueries).

**ForumPostsTab.tsx:**
- Props: { companyId: number }
- Shows list of ForumSeeds for this company
- For selected seed: shows progress bar (N fetched / M total), list of ForumPostLinks with status badges (pending=gray, fetched=green, failed=red)
- Buttons: "Scrape Links" (Phase A), "Fetch Next" (Phase B), "Fetch All", "Retry Failed"
- Each fetched post row has "Import" button that calls import endpoint with companyId
- Clicking a fetched post expands to show raw_text preview via MarkdownPreview component
- Loading/error states handled

**PrepNotesPage.tsx integration:**
- Add a tab system: "Notes" (existing editor) | "Forum Posts" (new ForumPostsTab)
- Use simple useState tab toggle at the top of the page
- ForumPostsTab rendered when tab is active, passing companyId
- Existing notes editor unchanged when "Notes" tab is active

**Reuse:**
- MarkdownPreview from src/frontend/src/components/ui/MarkdownPreview.tsx for rendering raw post text
- api utility from src/frontend/src/utils/api.ts
- TanStack React Query patterns from existing hooks

**AC:**
1. PrepNotesPage has "Notes" and "Forum Posts" tabs
2. Switching tabs preserves state (no re-fetch)
3. ForumPostsTab shows seeds for the current company
4. Progress bar shows fetched/total count
5. Post links display with correct status badges
6. "Scrape Links" button triggers Phase A and refreshes link list
7. "Fetch Next" button fetches one post and updates status
8. "Import" button appends post to prep notes and shows confirmation
9. Raw text preview works for fetched posts via MarkdownPreview
10. Error states shown for failed fetches with last_error message

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

> 136 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-19** -- T-P2-145: Forum HTML extractors with jammer stripping (1point3acres). Create src/backend/scraper/forum_extractors.py with BeautifulSoup-based extraction functions for 1point3acres forum page
- [x] **2026-03-19** -- T-P2-144: Playwright CDP attach + cookie fallback methods on PlaywrightCrawler. Extend existing src/backend/scraper/crawler.py PlaywrightCrawler class with two new async methods for fetching pages fro
- [x] **2026-03-19** -- T-P2-143: Forum models (ForumSeed, ForumPostLink, ForumPost) + migration v9. Create src/backend/models/forum.py with 3 SQLAlchemy models for the two-phase forum scraping workflow.
- [x] **2026-03-19** -- T-P0-146: Forum service layer (two-phase scrape + import to prep notes). Create src/backend/services/forum_service.py with business logic for the two-phase forum scraping workflow.
- [x] **2026-03-17** -- T-P2-133: Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs. Generate prep docs for Pillars 1, 5, 8 leaf topics. Coding: DS cheat sheets, algorithm paradigms, MLE-specific patterns.
- [x] **2026-03-17** -- T-P2-132: Applied ML pillar (Pillar 4) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 4 leaf topics. Covers: recommender systems, search & IR, NLP & LLM applicatio
- [x] **2026-03-17** -- T-P1-142: Seed DoorDash and Uber interview events
- [x] **2026-03-17** -- T-P1-141: Framework: checkbox progress calc + parent propagation
- [x] **2026-03-17** -- T-P1-140: Framework: URL-driven selection + tree auto-expand + row-click expand
