# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

#### T-P1-181: Fetch missing problem descriptions (5 problems)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: 5 problems (id=151-155) missing description. Fetch via POST /api/problems/fetch-all-descriptions. LeetCode GraphQL first, neetcode fallback, manual for premium. ADOPTED REVIEW: Add idempotency protection -- skip problems that already have description unless force=True param is passed. Acceptance: all 155 problems have non-null description; re-running fetch does NOT overwrite existing descriptions.

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-182: Remove Review column from Problems table
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Review column (next_review_at badge) adds no value currently: 0/155 problems have next_review_at set, no dedicated review queue page exists, Dashboard link to review filter is broken. Remove ReviewBadge from both All Problems and Blind75 table views. Keep the backend spaced_repetition logic and review-queue endpoint for future use. Acceptance: Review column gone from Problems page, no regression in other features.

#### T-P1-183: Framework progress: sync progress_pct with checklist state
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Framework progress sync: auto-propagate status + progress upward when children change.

ADOPTED REVIEW CHANGES (6 items):
1. Status machine: priority-driven -- mastered > review > in_progress > not_started. [mastered,review] mix = in_progress (not review). else fallback = in_progress.
2. Child add/remove/reparent MUST trigger parent re-propagation (blind spot in original plan).
3. Timestamps only-set-never-clear: completed_at and started_at are irreversible once set. Do NOT clear completed_at when leaving mastered.
4. Cycle detection: log critical + stop propagation silently. Do NOT raise exception to user (would break normal operations like study log).
5. Study log auto in_progress: keep original design (no threshold). Simple and direct.
6. Additional tests: child deletion propagation + status rollback scenarios.

Backend: refactor _propagate_progress -> _propagate_upward with _derive_status helper. Fix triggers in update_framework_node and create_study_log. Frontend: disable status dropdown for parent nodes, show auto from children indicator. One-time migration script for existing stale data.

### P2 -- Nice to Have

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 158 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-22** -- T-P2-157: Wire enriched extraction into service layer + import. ## Summary
- [x] **2026-03-22** -- T-P2-156: Add full_page_text column to ForumPost + migration. ## Summary
- [x] **2026-03-22** -- T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor. ## Summary
- [x] **2026-03-22** -- T-P2-112: SSE chunked audio streaming (if latency requires it). Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with
- [x] **2026-03-22** -- T-P1-177: LeetCode: Add solution notes for 4 problems (K-Similar Strings, Longest Continuous Subarray, Russian Doll, Merge K Lists). ## Goal
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
- [x] **2026-03-22** -- T-P0-180: Fix ruff lint errors (4x UP017 datetime.UTC). 4 auto-fixable UP017 errors in system_design.py. Run ruff check --fix. Acceptance: ruff check src/backend/ passes clean.
- [x] **2026-03-22** -- T-P0-179: Fix /api/problems 500 error (NULL priority). 2 problems had NULL priority causing Pydantic validation failure. Fixed schema, response builder, and added migration.
- [x] **2026-03-22** -- T-P0-178: Ad-hoc: commit all uncommitted changes from previous sessions. ## Problem
