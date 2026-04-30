# T-P0-655 Pinterest VO Phase 1 Verification -- Deliverable

**Reviewer-mandated order: SQL > API > Screenshot.**

## 1. SQL Block A -- `interview_events` for Pinterest (`company_id=29`)

```sql
SELECT id, scheduled_at, event_type, duration_minutes, status, title
  FROM interview_events
 WHERE company_id=29
 ORDER BY scheduled_at;
```

| id | scheduled_at        | event_type    | dur | status    | title                                                              |
|----|---------------------|---------------|-----|-----------|--------------------------------------------------------------------|
| 14 | 2026-04-08T13:30:00 | hr_call       | 30  | completed | Phone Call with David                                              |
| 19 | 2026-04-16T14:00:00 | phone_screen  | 60  | upcoming  | Technical Virtual Phone Interview                                  |
| 50 | 2026-05-05 15:00:00 | system_design | 60  | upcoming  | Pinterest VO Day 1 R1 -- ML Systems Design \| Yiyang Zhang         |
| 51 | 2026-05-05 16:00:00 | behavioral    | 45  | upcoming  | Pinterest VO Day 1 R2 -- HM/Competency \| Daniel Liu               |
| 52 | 2026-05-06 13:00:00 | technical     | 45  | upcoming  | Pinterest VO Day 2 R1 -- Data/Algos \| Jiankai Sun                 |
| 53 | 2026-05-06 14:00:00 | technical     | 45  | upcoming  | Pinterest VO Day 2 R2 -- Data/Algos \| Yijian Xiang                |
| 54 | 2026-05-06 15:00:00 | technical     | 60  | upcoming  | Pinterest VO Day 2 R3 -- ML Practitioner \| Zihao Zhang            |

**Result: 7 rows (2 historical + 5 new). PASS.**

## 2. SQL Block B -- doc 83 misdirected prose reverted

```sql
SELECT count(*)
  FROM company_documents
 WHERE id=83
   AND content LIKE '%CONFIRMED 2026-04-30%';
```

```
0
```

**Result: 0. PASS** (the misdirected `CONFIRMED 2026-04-30` prose edit is gone from doc 83).

## 3. SQL Block C -- `companies.interview_stages` for Pinterest

```sql
SELECT interview_stages FROM companies WHERE id=29;
```

```json
[
  {"name": "Recruiter Call", "status": "completed"},
  {"name": "Phone Screen (60min)", "status": "completed"},
  {"name": "Virtual Onsite (5 rounds: 5/5-5/6)", "status": "scheduled",
   "scheduled_at": "2026-05-05T15:00:00"}
]
```

**Diff context** -- the prior misdirected value (pre-T-P0-653) had inflated five separate per-round stage entries. The current state matches the user-approved revert per T-P0-653 (single `Virtual Onsite (5 rounds: 5/5-5/6)` umbrella stage). **PASS.**

## 4. API parity

```
curl -s http://localhost:8000/api/timeline/events | jq '[.[] | select(.company_id==29)] | length'
=> 7
```

Matches SQL Block A row count exactly. **PASS.**

## 5. Screenshot

`logs/pinterest_vo_dashboard_20260429T200857.png` (207 KB, full-page).

**Visible-text grep verification (Playwright `page.locator("body").inner_text()`):**

| Interviewer    | Visible on Dashboard? |
|----------------|-----------------------|
| Yiyang Zhang   | YES                   |
| Daniel Liu     | YES                   |
| Jiankai Sun    | YES                   |
| Yijian Xiang   | YES                   |
| Zihao Zhang    | YES                   |

**Result: all 5 interviewer names render in the InterviewTimeline component. PASS.**

### Side-finding (NOT a code bug -- dev-environment misconfiguration)

The first screenshot attempt (`logs/pinterest_vo_dashboard_20260429T200551.png`)
showed `"Failed to load interview timeline."` This was traced to a port mismatch:

- `src/frontend/vite.config.ts` proxies `/api` to `http://localhost:8100` (the
  canonical port per `scripts/dev.py` and commit `5ddf84c [T-P2-68]`).
- The currently-running backend (PID 29616) is bound to port `8000`.
- Result: `5173 -> 8100 -> 502 Bad Gateway`, surfaced in the UI as the timeline
  error banner.

Mitigation for the screenshot: started a second uvicorn instance on `8100` for
the duration of the smoke run, verified Dashboard rendered all 5 names, then
killed it. The user's existing `:8000` backend was not touched and remains up.

**Recommendation for the user:** restart the backend via
`python scripts/dev.py` (or `uvicorn src.backend.main:app --port 8100`) so the
frontend can reach the API. No code change needed.

## 6. Phase-2 entry-criteria checklist (please confirm)

- [ ] (a) Doc 83 partial-revert strategy correct? (narrative restored, the
      misdirected `CONFIRMED 2026-04-30` prose removed; itinerary lives only
      in `interview_events` rows 50-54 going forward.)
- [ ] (b) Root-cause investigation for T-P0-661 ("WHY did Claude default to
      `company_documents.content` instead of `interview_events`?") should
      proceed?
- [ ] (c) Green-light Phase 2 -- T-P0-660 migration lint hook (forbid
      INSERT/UPDATE/DELETE in `scripts/migrations/*` against `data/*.db`)?

**This task (T-P0-655) stays in `in_progress` until you reply with green-light
on (c).** Per AC4 of the task spec.
