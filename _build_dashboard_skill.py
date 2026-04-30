"""Build the SKILL.md content for the dashboard skill.

Idempotent. Run: python _build_dashboard_skill.py
"""
from pathlib import Path

CONTENT = '''---
name: dashboard
description: Route requests that mention "dashboard" / "left tab" / "first nav item" / "left nav" / "我们 app" / "左侧 tab" to the Surface Identification table in CLAUDE.md before any DB write. Re-derives target table from widget -> queryKey -> endpoint -> table chain. Pairs with the invariant3_guard lint hook (T-P0-660 + T-P0-660b) -- this skill addresses the prior, the lint addresses the failure mode if the prior is overridden.
triggers:
  - dashboard
  - "left tab"
  - "left nav"
  - "first nav item"
  - "left-nav-first"
  - "我们 app"
  - "我们app"
  - "左侧 tab"
  - "左侧tab"
---

# /dashboard -- Surface-Identification Routing Skill

This skill is **documentation, not enforcement**. The structural enforcement is the `invariant3_guard.py` lint hook (T-P0-660 + T-P0-660b extension). This skill exists to make the right-path the easy default for any session that gets a "dashboard / app / left-nav-first" request.

The skill design absorbs the recommendation from `logs/2026-04-30_pinterest_root_cause.md` line 93 ("option (c) BOTH (a) AND (b), not either alone") and lines 91-99 (the BOTH-not-either argument). The CLAUDE.md `Surface Identification` table addresses the **prior** (mention-density bias); the lint hook addresses the **failure mode** when the prior is overridden by recency priming. They are TWO INDEPENDENT LAYERS, not one. This skill MUST treat them that way -- never collapse into a single "check the map" instruction.

## When this skill triggers

Any user message that names a UI surface without naming a DB table:

- "Update Pinterest onsite schedule on my dashboard"
- "Add the Stripe HR call to the dashboard"
- "Refresh the cheat sheet card on the left tab"
- "我们 app 上把 Uber 的 onsite 时间改一下" / "左侧 tab 第一个" / "left nav first item"
- "Add an event to the prep board"

The trigger keywords listed in frontmatter are the regex anchors. Anything that mentions the user-facing surface (dashboard, app, tab, nav, page) without a backend table name should land here.

## Six-Step Protocol

### 1. Read the Surface Identification table FIRST

Open `MLInterviewPrep/CLAUDE.md` and locate `## Surface Identification`. The widget -> queryKey -> endpoint -> table mapping is the single source of truth. Do not re-derive from prior session memory. Do not pattern-match from the last edited file. Read the table.

### 2. Confirm the widget by reading its component file

The table names the source file (e.g. `timeline/InterviewTimeline.tsx`). Open it and verify:
- The `queryKey` matches the table queryKey column.
- The `queryFn` calls the table API endpoint.
- The endpoint router (`src/backend/routers/<router>.py`) reads from the named DB table.

This is a 3-link chain (component -> endpoint -> table). Walking it explicitly defeats the recency-priming failure mode -- you cannot accidentally route to `company_documents.content` if you have just read `timeline.py` returning `interview_events` rows.

### 3. Locate the matching idempotent seed

Per Invariant 3 (CLAUDE.md), every DB content row must have a git-tracked, idempotent Python seed script. Search by canonical key:

- `interview_events`: `scripts/_add_<company>_<date>.py` -- e.g. `_add_pinterest_hr_prep_2026-04-30.py`
- `company_documents`: `scripts/seed_<company>_<doc>.py` (sentinel-UPSERT)
- `problems`: `scripts/seed_<company>_lc_problems.py` or focused `_add_*.py`
- `framework_nodes`: `scripts/seed_node_<id>_*.py` or pillar batches
- `companies.prep_notes`: `scripts/seed_<company>_prep_notes.py`
- `companies.status` / `companies.cheat_sheet`: `scripts/seed_<company>_companies_row.py`

If no matching seed exists, plan a new one BEFORE writing. Never reach for `scripts/migrations/*.py` raw-SQL templates -- those are blocked by `invariant3_guard.py` and are an anti-pattern (see T-P0-651 postmortem).

### 4. Edit the SEED, not the DB

Write or extend the seed script. Run it. Verify the output prints `[INSERT]`, `[UPDATE]`, or `[UNCHANGED]` for each row -- a missing log line means the seed is not actually idempotent and needs review. Run it twice; second run must be `[UNCHANGED]` for already-applied rows.

### 5. Verify with SQL count assertion FIRST, then optionally screenshot

Before declaring done, assert from the SQLite DB directly that the row exists with the expected canonical key:

```bash
python -c "import sqlite3; c=sqlite3.connect('data/mle_prep.db'); print(c.execute('SELECT id, scheduled_at, interviewer_name FROM interview_events WHERE company_id=? AND scheduled_at LIKE ?', (29, '2026-05-05%')).fetchall())"
```

SQL counts are the cheapest, most decisive verification. A screenshot of the rendered widget is supplementary, not primary -- the widget might render from cache, or the row might land in the wrong column. Counts come first.

### 6. Send the deliverable; wait for user confirmation

When reporting to the user (Discord or terminal), lead with the SQL counts. Reference the exact seed script that was created/run. Do NOT mark the task done until the user confirms the widget shows the expected state in their browser.

## What this skill does NOT do

- It does NOT re-implement the routing table in skill-body. The table lives in `CLAUDE.md` as single source of truth; this skill references it. (Reviewer hole #4: do not maintain the same mapping in 3 places.)
- It does NOT encode behavioral-only conclusions. `logs/2026-04-30_pinterest_root_cause.md` line 99 explicitly rejects "always remember to check the map" as a class of fix: it has zero leverage when the context window is tight or when the model is primed by the prior turn. The structural fix is the table itself + the lint hook, not an exhortation. This skill body is a **protocol** (read THIS file, walk THIS chain, run THIS seed) -- not a reminder.
- It does NOT replace the `invariant3_guard.py` lint hook. The lint hook is the belt; this skill is the suspenders. Both are required. See `logs/2026-04-30_pinterest_root_cause.md` lines 91-99 ("BOTH (a) AND (b), not either alone") for why each layer alone is insufficient: without the table the lint only catches one surface; without the lint the table is documentation that future sessions can ignore.

## Self-test: dry-run on "add Stripe HR call to my dashboard"

Walking the 6-step protocol on the prompt: add Stripe HR call to my dashboard scheduled for 2026-05-12 14:00 with Recruiter Jane.

1. **Read CLAUDE.md `Surface Identification`**. The phrase "dashboard" + "scheduled for <ISO-8601>" + "<interviewer-name>" maps to the row `Dashboard.InterviewTimeline -> interview_events` (queryKey `["timeline","events"]`, endpoint `GET /timeline/events`).

2. **Confirm chain**: open `src/frontend/src/components/timeline/InterviewTimeline.tsx`, find `queryFn: () => api.get<InterviewEvent[]>("/timeline/events")` (line 81). Open `src/backend/routers/timeline.py`, find `@router.get("/timeline/events", response_model=list[InterviewEventResponse])` returning rows from `interview_events` model. Chain confirmed.

3. **Locate seed pattern**: `scripts/_add_<company>_<date>.py` is the convention. Existing examples: `_add_pinterest_hr_prep_2026-04-30.py`. New seed: `scripts/_add_stripe_hr_2026-05-12.py`.

4. **Edit the seed**: write `_add_stripe_hr_2026-05-12.py` that resolves `company_id` for Stripe, then UPSERTs an `interview_events` row keyed on `(company_id, scheduled_at='2026-05-12 14:00', interviewer_name='Recruiter Jane')`. Run it. Run it twice; second run prints `[UNCHANGED]`.

5. **Verify**: `SELECT id, scheduled_at, interviewer_name FROM interview_events WHERE company_id=<stripe_id> AND scheduled_at LIKE '2026-05-12%'` returns exactly one row matching the input.

6. **Deliverable**: report SQL count + seed file path to user. Wait for browser-side confirmation before marking task done.

What the protocol explicitly does NOT propose:
- Editing `company_documents.content` to mention the schedule in prose. (`invariant3_guard.py` would block such a write under the schedule-prose detector even if step 1 misrouted.)
- Writing a `scripts/migrations/add_stripe_event.py` raw-SQL script. (Blocked by `invariant3_guard.py` migration-SQL detector.)
- Adding a behavioral comment "remember to check the table next time". (Rejected at memo line 99.)

## Cross-references

- **Surface Identification table**: `MLInterviewPrep/CLAUDE.md` (single source of truth for widget -> table mapping; this skill references, never duplicates).
- **Lint hook (independent enforcement layer)**: `.claude/hooks/invariant3_guard.py` -- migration-SQL detector (T-P0-660) + schedule-prose detector (T-P0-660b / T-P0-663).
- **Root-cause memo**: `logs/2026-04-30_pinterest_root_cause.md` -- specifically lines 91-99 (the BOTH-not-either recommendation, "option (c)") and line 99 (rejection of behavioral-only fixes). Reviewers verifying this skill MUST confirm those line references resolve to the cited content.
- **Originating incident**: T-P0-651 (Pinterest VO misdirected write, 2026-04-30) -- see `PROGRESS.md` lines 355-470 for the turn-by-turn surface chain.
- **Postmortem task chain**: T-P0-660 (lint), T-P0-660b/T-P0-663 (lint extension), T-P0-661 (root cause), T-P1-656 (this skill).
'''


def main() -> None:
    """Write the SKILL.md content idempotently."""
    target = Path(__file__).parent / ".claude" / "skills" / "dashboard" / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == CONTENT:
        print(f"[UNCHANGED] {target}")
        return
    target.write_text(CONTENT, encoding="utf-8")
    print(f"[WROTE] {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
