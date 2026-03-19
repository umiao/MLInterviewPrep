# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

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
- [x] **2026-03-19** -- T-P0-148: Forum API routes + Pydantic schemas. Create src/backend/routers/forum.py and src/backend/schemas/forum.py for the forum scraping REST API.
- [x] **2026-03-19** -- T-P0-147: Forum CLI script (scripts/forum_scrape.py). Create scripts/forum_scrape.py as the primary CLI interface wrapping the forum service layer.
- [x] **2026-03-19** -- T-P0-146: Forum service layer (two-phase scrape + import to prep notes). Create src/backend/services/forum_service.py with business logic for the two-phase forum scraping workflow.
- [x] **2026-03-17** -- T-P2-133: Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs. Generate prep docs for Pillars 1, 5, 8 leaf topics. Coding: DS cheat sheets, algorithm paradigms, MLE-specific patterns.
- [x] **2026-03-17** -- T-P2-132: Applied ML pillar (Pillar 4) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 4 leaf topics. Covers: recommender systems, search & IR, NLP & LLM applicatio
- [x] **2026-03-17** -- T-P1-142: Seed DoorDash and Uber interview events
- [x] **2026-03-17** -- T-P1-141: Framework: checkbox progress calc + parent propagation
- [x] **2026-03-17** -- T-P1-140: Framework: URL-driven selection + tree auto-expand + row-click expand
