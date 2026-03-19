# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

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
- [x] **2026-03-19** -- T-P0-153: Forum scrape CLI + API: pagination params. Wire pagination to CLI and API. Three files to modify:
- [x] **2026-03-19** -- T-P0-152: Forum service: refactor scrape_seed_page + add scrape_seed_pages. Refactor src/backend/services/forum_service.py for multi-page scraping:
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
