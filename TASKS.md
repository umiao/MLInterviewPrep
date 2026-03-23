# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

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

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

### P2 -- Nice to Have

### P3 -- Stretch Goals

## Blocked

## Completed Tasks

> 175 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-22** -- T-P2-157: Wire enriched extraction into service layer + import. ## Summary
- [x] **2026-03-22** -- T-P2-156: Add full_page_text column to ForumPost + migration. ## Summary
- [x] **2026-03-22** -- T-P2-155: Extract all page-1 posts (OP + replies) in forum extractor. ## Summary
- [x] **2026-03-22** -- T-P2-112: SSE chunked audio streaming (if latency requires it). Only if full-MP3 generation latency becomes a UX problem for long content. SSE endpoint streaming base64 MP3 chunks with
- [x] **2026-03-22** -- T-P1-182: Remove Review column from Problems table. Review column (next_review_at badge) adds no value currently: 0/155 problems have next_review_at set, no dedicated revie
- [x] **2026-03-22** -- T-P1-181: Fetch missing problem descriptions (5 problems). 5 problems (id=151-155) missing description. Fetch via POST /api/problems/fetch-all-descriptions. LeetCode GraphQL first
