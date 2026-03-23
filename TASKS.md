# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-177: LeetCode: Add solution notes for 4 problems (K-Similar Strings, Longest Continuous Subarray, Russian Doll, Merge K Lists)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ## Goal
Update 4 LeetCode problems with user-provided solution notes. Find or create these problems in the DB, then set their `notes` field.

## Problems and Notes

### 1. K-Similar Strings (LC 854)
URL: https://leetcode.cn/problems/k-similar-strings/description/
Notes:
- BFS/DFS search approach: simulate every possible swap to match the first mismatched position
- Key optimizations/pruning:
  1. Skip already-matching positions (no need to swap matched chars)
  2. Only modify s1 to match s2 (don't sync both)
  3. Process one mismatched char at a time, break immediately after swap
  4. Track all generated strings (s1 variants) to prevent revisiting
- Pattern: BFS + pruning

### 2. Longest Continuous Subarray With Absolute Diff <= Limit (LC 1438)
URL: https://leetcode.cn/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/description/
Notes:
- Sliding window with two monotonic deques (one for max, one for min)
- Move right pointer, add new element to both deques (maintaining monotonicity)
- Check if abs(max - min) > limit; if so, shrink left pointer, pop from deques
- Since limit >= 0, we can always find a valid window (single element satisfies)
- Pattern: Sliding Window + Monotonic Deque

### 3. Russian Doll Envelopes (LC 354)
URL: https://leetcode.cn/problems/russian-doll-envelopes/description/
Notes:
- Sort envelopes: width ascending, height descending (same width can't nest)
- Reduce to Longest Increasing Subsequence (LIS) on height dimension
- Use binary search for O(n log n) LIS
- Pattern: Sort + LIS (Binary Search)

### 4. Merge K Sorted Lists (LC 23)
URL: https://leetcode.cn/problems/merge-k-sorted-lists/
Notes:
- Approach 1: Min-heap -- push all list heads into heap, pop min, push next
- Approach 2: Divide and conquer -- recursively merge pairs, log(k) rounds of pairwise merge sort
- Pattern: Heap / Divide and Conquer

## Implementation
1. For each problem, search DB by URL or title
2. If not found, create the problem entry with appropriate metadata (difficulty, tags, pattern)
3. Set the `notes` field with the solution notes in markdown format
4. Mark as completed (is_completed=True) with appropriate comfort level

## Acceptance Criteria
- [ ] All 4 problems exist in DB with correct metadata
- [ ] Each problem has solution notes populated
- [ ] Notes visible on ProblemDetailPage "My Notes" section
- [ ] Problems marked as completed

### P2 -- Nice to Have

#### T-P2-112: SSE chunked audio streaming (if latency requires it)
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with MediaSource API on frontend. Evaluate need after Phase 2. AC: SSE streams audio chunks, frontend plays without gaps, progress tracked per chunk

#### T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: ## Summary
Modify extract_post_content() in forum_extractors.py to return all posts on page 1 (OP + all replies), not just the OP.

## Context
Currently extract_post_content() uses select_one to grab only the first div.plc.cl block (the OP). Forum threads on 1point3acres have multiple reply blocks on page 1 that contain valuable interview discussion. User wants ALL page-1 content for later filtering.

## Acceptance Criteria
- [ ] extract_post_content() returns existing keys unchanged: title, body, author, date, external_post_id (all OP data)
- [ ] New key replies: list of dicts {author: str, date: str, body: str, post_id: str}, one per reply on page 1
- [ ] New key full_page_text: formatted concatenation with locked format:
  [OP] Author: {author} | Date: {date}\n{body}\n\n---\n\n[Reply 1] Author: ...\n{body}\n\n---\n...
- [ ] Jammer stripping (font.jammer removal) applied to ALL posts, not just OP
- [ ] Selector fallback: if 0 div.plc.cl blocks found, log warning and fall back to existing single-post extraction logic
- [ ] If post has 0 replies: replies=[], full_page_text == OP body with [OP] header
- [ ] Test fixture forum_post.html updated with 2+ replies having distinct authors/dates/bodies
- [ ] All existing tests in test_forum_extractors.py still pass (backward compat)
- [ ] New tests: reply count, reply content, full_page_text format, jammer in replies stripped, 0-reply case, selector fallback case
- [ ] Known limitation documented in code comment: MIN_POST_CONTENT_LENGTH check (in service layer) uses OP body only

## Technical Approach
- forum_extractors.py: use soup.select("div.plc.cl") to get ALL post blocks. First = OP (existing logic). Rest = replies.
- For each reply block: extract author from .authi, date from meta[itemprop=datePublished] or em, body from [itemprop=articleBody] or td.t_f, post_id from div.display.pi itemid
- Build full_page_text by concatenating with format template
- Update tests/fixtures/forum_post.html with realistic reply blocks
- Update tests/test_forum_extractors.py

## Edge Cases
- Pages with only OP (no replies) -> replies=[], full_page_text has only [OP] section
- Reply with missing author or date -> default to empty string
- Selector returns 0 blocks (HTML drift) -> log warning, fall back to current logic
- Reply body contains jammer text -> must be stripped

## Complexity
M - extractor logic change + fixture updates + new tests

#### T-P2-156: Add full_page_text column to ForumPost + migration
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: ## Summary
Add full_page_text Text column to ForumPost model and a schema migration.

## Context
Currently ForumPost.raw_text stores only OP body. Need a second column for the complete page 1 content (OP + replies). Keep raw_text as OP-only for backward compatibility.

## Acceptance Criteria
- [ ] ForumPost model has: full_page_text = Column(Text, nullable=True)
- [ ] New migration entry in MIGRATIONS list in database.py using ADD_COLUMN_IF_MISSING directive
- [ ] Migration adds column to existing forum_posts table without affecting existing data
- [ ] Existing rows get NULL for full_page_text (nullable)
- [ ] Migration test in tests/test_migrations.py: create old schema, run migration, verify column exists

## Technical Approach
- src/backend/models/forum.py: add Column(Text, nullable=True) after content_hash
- src/backend/database.py: add migration tuple to MIGRATIONS list, next version number, using ADD_COLUMN_IF_MISSING:forum_posts:full_page_text:ALTER TABLE forum_posts ADD COLUMN full_page_text TEXT
- tests/test_migrations.py: add test

## Edge Cases
- Column already exists (re-run) -> ADD_COLUMN_IF_MISSING handles idempotency
- Existing data -> NULL is fine, service layer falls back to raw_text

## Complexity
S - one column + one migration entry + one test

#### T-P2-157: Wire enriched extraction into service layer + import
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P2-155, T-P2-156
- **Description**: ## Summary
Update fetch_single_post to store full_page_text from extractor. Update import_post_to_document to prefer full_page_text.

## Context
After T-P2-155 (extractor returns full_page_text) and T-P2-156 (model has the column), this task connects them in the service layer.

## Acceptance Criteria
- [ ] fetch_single_post() in forum_service.py stores content.get("full_page_text", "") to ForumPost.full_page_text
- [ ] import_post_to_document() uses post.full_page_text if not None/empty, else falls back to post.raw_text
- [ ] Content quality check (MIN_POST_CONTENT_LENGTH) still uses raw_text (OP body only)
- [ ] Test: fetch a post -> ForumPost has both raw_text and full_page_text populated
- [ ] Test: import with full_page_text present -> document contains reply content
- [ ] Test: import with full_page_text=None (old data) -> falls back to raw_text gracefully

## Technical Approach
- forum_service.py fetch_single_post(): after creating ForumPost, set post.full_page_text = content.get("full_page_text", "")
- forum_service.py import_post_to_document(): change post.raw_text reference to (post.full_page_text or post.raw_text)
- Update existing tests or add new tests

## Edge Cases
- Old posts with full_page_text=None -> graceful fallback to raw_text
- Thread with only OP -> full_page_text contains just OP with header
- Empty full_page_text string -> treat as None, use raw_text

## Complexity
S - straightforward wiring, two functions to modify

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 158 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-22** -- T-P1-176: LeetCode: Move Practice/Review actions from table to ProblemDetailPage. ## Problem
- [x] **2026-03-22** -- T-P1-175: LeetCode: Blind75 add 'All Problems' ungrouped view alongside grouped view. ## Problem
- [x] **2026-03-22** -- T-P1-174: LeetCode: Blind75 tab missing sort-by controls + filter state not shared with All tab. ## Problem
- [x] **2026-03-22** -- T-P1-173: System Design Module 6: Distributed Task Queue (failure modes, idempotency, exactly-once). ## Goal
- [x] **2026-03-22** -- T-P1-172: System Design Module 5: Database Systems Comparison (Cassandra focus). ## Goal
- [x] **2026-03-22** -- T-P1-171: System Design detail: single-page layout with bookmark nav + fix module-arbitration content. ## Problem
- [x] **2026-03-22** -- T-P1-170: Diagram click-to-fullscreen lightbox overlay. ## Problem
- [x] **2026-03-22** -- T-P1-169: Diagram screenshots: crop whitespace and increase render size. ## Problem
- [x] **2026-03-22** -- T-P1-168: System Design: replace static screenshots with HTML-rendered diagrams. ## Problem
- [x] **2026-03-22** -- T-P1-167: Fix Docker nginx.conf proxy port mismatch (8000 -> 8100). ## Problem
- [x] **2026-03-22** -- T-P1-166: Fix dev.py startup race condition: wait for backend health before starting frontend. ## Problem
- [x] **2026-03-22** -- T-P1-165: Content: Ranking-as-Allocation / Diversity Allotment Policy Framework. All 8 sections for Ranking-as-Allocation (SIGNATURE PROJECT - deepest coverage). Includes production constraints (50K QP
- [x] **2026-03-22** -- T-P1-164: Content: PBE Logging & Dataset Pipeline. All 8 sections for PBE Pipeline. Includes production constraints (500M impressions/day, 5-min micro-batch, 2TB daily). D
- [x] **2026-03-22** -- T-P0-178: Ad-hoc: commit all uncommitted changes from previous sessions. ## Problem
