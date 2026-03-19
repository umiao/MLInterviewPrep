# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-152: Forum service: refactor scrape_seed_page + add scrape_seed_pages
- **Priority**: P0
- **Complexity**: M
- **Depends on**: T-P0-151
- **Description**: Refactor src/backend/services/forum_service.py for multi-page scraping:

Step 1: Extract helper (refactoring safety: run existing TestScrapeSeedPage tests before and after)
- Extract _upsert_links_from_html(db, seed_id, html, base_url, order_offset=0) -> tuple[list[ForumPostLink], int]
  - Contains current extract+upsert logic from scrape_seed_page() lines 86-133
  - Returns (all_links, new_count) where new_count = genuinely new links inserted
  - order_offset shifts fetch_order for pages beyond 1. Caller passes running total of links seen so far (NOT hardcoded page*20)
- Simplify scrape_seed_page() to: fetch HTML via _fetch_html -> call _upsert_links_from_html -> update seed.last_scraped_at -> commit
  - Same function signature, same return type, same behavior

Step 2: Add new function
- scrape_seed_pages(db: Session, seed_id: int, crawler: PlaywrightCrawler, max_pages: int = 1, auto_detect: bool = True) -> dict
  - Load ForumSeed, validate exists
  - Fetch page 1 via _fetch_html(crawler, seed.url)
  - Call _upsert_links_from_html for page 1
  - If auto_detect: call extract_max_page(html) on page 1 HTML to get detected max
  - effective_max = min(max_pages, detected_max) if auto_detect else max_pages
  - Loop pages 2..effective_max:
    a. Rate limit: await asyncio.sleep(random.uniform(*get_config(seed.source_site).rate_limit_seconds) + random.uniform(0, 3))
    b. Derive URL: derive_page_url(seed.url, page)
    c. Fetch HTML via _fetch_html(crawler, url)
    d. If empty HTML: logger.warning('Page %d: empty response, skipping', page); continue (do NOT abort)
    e. Call _upsert_links_from_html(db, seed_id, html, seed.url, order_offset=cumulative_links)
    f. Structured logging: logger.info('Page %d/%d: %d links (%d new), cumulative %d', page, effective_max, page_total, page_new, running_total)
    g. Early stop: if page_new == 0, increment zero_new_streak; else reset to 0. If zero_new_streak >= 3 and page >= 5: break, set stopped_early=True
  - Update seed.last_scraped_at, db.commit()
  - Return: {'pages_scraped': int, 'total_links': int, 'new_links': int, 'max_page_detected': int, 'stopped_early': bool}

Imports needed: random, derive_page_url, extract_max_page from forum_extractors, get_config from site_configs

Tests (add to tests/test_forum_service.py):
- TestScrapeSeedPages class:
  - test_single_page: max_pages=1 returns correct stats
  - test_multi_page: mock crawler returns different HTML per URL (use side_effect), verify links from both pages, order_offset correct
  - test_auto_detect: mock page 1 with pagination HTML, verify effective_max is capped
  - test_early_stop: mock pages returning 0 new links after page 5, verify stopped_early=True
  - test_page_failure_continues: one page returns empty HTML, others succeed, verify scraping continues
- Must mock asyncio.sleep to avoid slow tests

AC:
- Existing TestScrapeSeedPage tests pass UNCHANGED (characterization test for refactoring safety)
- All new TestScrapeSeedPages tests pass
- _upsert_links_from_html is private but tested indirectly through both scrape_seed_page and scrape_seed_pages
- ruff clean

#### T-P0-153: Forum scrape CLI + API: pagination params
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-152
- **Description**: Wire pagination to CLI and API. Three files to modify:

1. src/backend/schemas/forum.py -- add response model:
   class ForumScrapeStatsResponse(BaseModel):
       pages_scraped: int
       total_links: int
       new_links: int
       max_page_detected: int = 1
       stopped_early: bool = False

2. src/backend/routers/forum.py -- update scrape endpoint:
   - Add max_pages: int = Query(1, ge=1) parameter to POST /seeds/{seed_id}/scrape
   - When max_pages > 1: call scrape_seed_pages(db, seed_id, crawler, max_pages=max_pages)
   - Return ForumScrapeStatsResponse
   - When max_pages == 1: keep existing behavior (call scrape_seed_page, return list)
   - Import scrape_seed_pages from forum_service, ForumScrapeStatsResponse from schemas

3. scripts/forum_scrape.py -- update scrape subcommand:
   - Add --pages N argument (type=int, default=1) to p_scrape parser
   - Add --no-auto-detect flag (action='store_true')
   - In cmd_scrape():
     - If args.pages > 1: call asyncio.run(scrape_seed_pages(db, seed_id, crawler, max_pages=args.pages, auto_detect=not args.no_auto_detect))
     - Print formatted stats: Pages scraped, Total links, New links, Max page detected, Stopped early
     - If args.pages == 1: keep existing behavior (call scrape_seed_page, print link list)
   - Import scrape_seed_pages from forum_service

Tests:
- tests/test_forum_scrape_cli.py: add test_scrape_parses_pages_flag and test_scrape_parses_no_auto_detect
- tests/test_router_forum.py: add test_scrape_with_max_pages (verify query param accepted, mock returns stats dict)

AC:
- python scripts/forum_scrape.py scrape --help shows --pages and --no-auto-detect options
- Existing tests in test_forum_scrape_cli.py and test_router_forum.py pass unchanged
- New tests pass
- ruff clean

#### T-P0-154: Live scrape: LinkedIn 1point3acres first 5 pages
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-153
- **Description**: Execute the live scraping pipeline. This is a manual execution task, not a code task.

Prerequisites: T-P0-151, T-P0-152, T-P0-153 all completed. Cookie ONEPOINT3ACRES_COOKIE is set in .env.

Steps:
1. Add seed:
   python scripts/forum_scrape.py add-seed "https://www.1point3acres.com/bbs/tag-415-1.html" --company LinkedIn --label "1point3acres interviews"
   - Verify: seed created with correct company_id and source_site=1point3acres

2. Scrape 5 pages:
   python scripts/forum_scrape.py scrape <seed_id> --pages 5
   - This will fetch 5 index pages with 20-45s + 0-3s jitter between pages
   - Expected: ~100 post links (20 per page)
   - Total time: ~2-3 minutes for 5 pages

3. Check status:
   python scripts/forum_scrape.py status <seed_id>
   - Verify: Total links ~100, all pending status

4. Report stats to user:
   - Pages scraped
   - Total links discovered
   - New links (should equal total on first run)
   - Max page detected (should be 255 for LinkedIn)
   - Whether early stop triggered (should be False for 5 pages)

AC:
- Seed created in DB with company_id=1 (LinkedIn)
- ~100 post links stored in forum_post_links table
- Stats output printed clearly
- No HTTP errors or rate limit blocks
- If any page fails, verify the scraper continued to next page (resilience)

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
- [x] **2026-03-19** -- T-P0-151: Forum extractor: derive_page_url + extract_max_page pure functions. Add two pure functions to src/backend/scraper/forum_extractors.py:
- [x] **2026-03-19** -- T-P0-149: Frontend ForumPostsTab component + integration into PrepNotesPage. Create ForumPostsTab React component and integrate it as a tab in the existing PrepNotesPage.
- [x] **2026-03-19** -- T-P0-148: Forum API routes + Pydantic schemas. Create src/backend/routers/forum.py and src/backend/schemas/forum.py for the forum scraping REST API.
- [x] **2026-03-19** -- T-P0-147: Forum CLI script (scripts/forum_scrape.py). Create scripts/forum_scrape.py as the primary CLI interface wrapping the forum service layer.
- [x] **2026-03-19** -- T-P0-146: Forum service layer (two-phase scrape + import to prep notes). Create src/backend/services/forum_service.py with business logic for the two-phase forum scraping workflow.
- [x] **2026-03-17** -- T-P2-133: Remaining pillars (Coding P1, Infra P5, Behavioral P8) prep docs. Generate prep docs for Pillars 1, 5, 8 leaf topics. Coding: DS cheat sheets, algorithm paradigms, MLE-specific patterns.
- [x] **2026-03-17** -- T-P2-132: Applied ML pillar (Pillar 4) prep docs for all leaf topics. Generate detailed prep docs for all Pillar 4 leaf topics. Covers: recommender systems, search & IR, NLP & LLM applicatio
- [x] **2026-03-17** -- T-P1-142: Seed DoorDash and Uber interview events
- [x] **2026-03-17** -- T-P1-141: Framework: checkbox progress calc + parent propagation
- [x] **2026-03-17** -- T-P1-140: Framework: URL-driven selection + tree auto-expand + row-click expand
