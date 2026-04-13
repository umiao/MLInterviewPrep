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
> 170+ session entries archived as of 2026-04-11.

- **What I did**: Redesigned RecipeCard to be compact (reduced padding, smaller text, single-row name+badge layout, truncated names). Added category grouping in BakingStudio browse mode -- recipes are now grouped under section headers (Base/Cream/Decoration/Complete) with descriptive captions. Removed unused category pill from cards since category is now shown via section headers. Maintained per-cake-type color themes.
- **Deliverables**: RecipeCard.tsx (compact layout), BakingStudio.tsx (category grouping with CATEGORY_SECTIONS + groupByCategory)
- **Sanity check result**: TypeScript type check passes, Vite build succeeds
- **Status**: [DONE]
> 82 session entries archived as of 2026-04-12.

## 2026-04-11 16:18 -- [behavioral-cluster + planning] Applied 7 task revisions from external code review
- **What I did**: User shared an external code-review pass on the 8-task plan (review of plan + meta-review of the review). Walked through each item, verified backend reality where the reviewer was speculating, applied 7 actionable revisions to task descriptions, declined 3 per the meta-review reasoning, and refuted 1 (the "biggest landmine") with direct schema evidence. Specific revisions: (1) T-P1-358 add PRAGMA table_info assert at the top of the seed script to prevent silent SQLite no-op when seed runs before migration. (2) T-P1-359 add a methodology guard before the uvicorn restart: capture PID via lsof/netstat, verify process command, hash routers/behavioral.py on disk, then verify after restart that theme_tags appears AND md5 was unchanged — only then is the stale-uvicorn hypothesis proven, not "restart fixed it" by induction. (3) T-P1-361 add staleTime: Infinity + gcTime: 1h to the behavioral-themes useQuery so section toggling does not refetch. (4) T-P1-362 drop the drawer's second fetch entirely: change state from activeExampleId:string|null to activeExample:BehavioralExample|null and pass the already-loaded object from the list query to ExampleDrawerContent — pure render-from-props, no race condition possible. Verified by reading src/backend/schemas/behavioral.py line 105+ that BehavioralExampleResponse already includes situation/task/action/result/evidence_quotes/principle_tags/risk_statement/analogy/tech_terms/linked_questions, so this is a one-line frontend change with NO backend touch. Also added an i18n typography sub-step for CN/EN font-stack alignment on the elevator-pitch pills (single CSS class with 'Inter','Noto Sans CJK SC',system-ui,sans-serif fallback chain + explicit line-height + vertical-align baseline). (5) T-P2-363 replaced the toy 8-line useReturnPath hook with a real useScrollRestore implementation using sessionStorage keyed by useLocation().key (react-router v6+ history-entry-unique key), save on scroll event, restore on mount via requestAnimationFrame. (6) T-P2-364 changed marker substring 'NARRATION-RISK GUARD' / 'TEMPORAL POV' to HTML-comment sentinels '<!-- NRG-v1 -->' / '<!-- TPV-v1 -->' across all gates, templates, asserts, and AC text — substring matching had a real false-positive risk if future content contained the human-readable phrase. (7) T-P2-365 tightened audit pass criterion from "1+ class of (a)/(b)/(c)/(d)" to "BOTH (a)+(b) required (quantitative number in Result AND metric+direction in Action), (c)/(d) downgraded to STRONG SUPPORTING evidence". Declined 3 items per meta-review reasoning: QuickIndex subcomponent split (premature refactor, scope-creep), reordering 362 before 361 (mock-data reasoning was wrong, dependency graph already encodes correct order), code-level FORBIDDEN guard in T-P2-364 (sentinel marker is enough, double layer is overkill). Refuted 1 item: the reviewer's "biggest landmine" was that /themes endpoint counts are an implicit contract — investigated and found src/backend/schemas/behavioral_theme.py BehavioralThemeResponse already declares question_count: int and example_count: int as non-Optional, so Pydantic enforces presence and type at serialization time. The landmine does not exist.
- **Deliverables**: scripts/_apply_review_revisions.py (new, idempotent atomic substitution script across 7 tasks), 8 task descriptions in tasks.db updated with the 7 revisions (final lengths: 358=5486, 359=5186, 360=3189, 361=3637, 362=5261, 363=4401, 364=7072, 365=1315 — total +6228 chars from the v1 plan), TASKS.md regenerated. NO behavioral data DB changes. NO source code changes (the plan is just edited; the code changes happen when autonomous_run executes the tasks).
- **Sanity check result**: (1) Substitution script ran with 12 individual substitutions reported [ok] across 7 tasks (the T-P2-364 sentinel update needed 11 individual substitutions for the 11 places the marker substring appeared). (2) Verified BehavioralThemeResponse is type-locked: question_count and example_count are non-Optional ints, ConfigDict(from_attributes=True) — Pydantic enforces, no implicit contract risk exists. (3) Verified BehavioralExampleResponse already returns full STAR fields including all 9 narrative columns + linked_questions — confirmed via direct file read of src/backend/schemas/behavioral.py line 105+. This means T-P1-362 drawer-no-second-fetch revision is purely a frontend change with zero backend coupling. (4) TASKS.md regenerates cleanly via task_db.py project. (5) All 7 substitution markers present in updated descriptions per the script's explicit verification step.
- **Status**: [DONE] for the planning iteration. 8-task plan is finalized at v2 (post-review). All actionable code-review feedback is encoded into the task descriptions; none of it is left as ambient context an autonomous session would need to recall. Ready for autonomous_run.sh kickoff once user approves.
- **Request**: No task_db status update -- planning iteration complete, no executable tasks have been started yet.
## 2026-04-11 -- [T-P1-358] Behavioral: cn_elevator_pitch column + seed 7 master pitches
- **What I did**: Added migration version 17 (ADD_COLUMN_IF_MISSING behavioral_examples.cn_elevator_pitch), added the column to SQLAlchemy BehavioralExample model and to all three Pydantic schemas (Create/Update/Response), added cn_elevator_pitch?: string | null to the frontend TypeScript BehavioralExample interface, wrote idempotent seed script scripts/seed_master_pitches.py with the PRAGMA table_info preflight (per the code-review guard), and seeded the exact Chinese pitch strings for all 7 master stories (EX-15/16/17/30/33B/34/09B). Also fixed a real bug uncovered by the task: src/backend/routers/behavioral.py _build_example_response was hand-constructing the response dict and would have silently dropped the new field — added "cn_elevator_pitch": ex.cn_elevator_pitch. Migration assigned version 17 (not 16 as in the task spec) because version 16 was already taken by the existing behavioral_themes migration.
- **Deliverables**: src/backend/database.py (migration 17), src/backend/models/behavioral.py (+1 Column), src/backend/schemas/behavioral.py (+3 field adds across Create/Update/Response), src/backend/routers/behavioral.py (+1 dict key in _build_example_response), src/frontend/src/types/behavioral.ts (+1 optional field), scripts/seed_master_pitches.py (new, idempotent).
- **Sanity check result**: (1) Migration applied: schema_versions now contains rows 1..17. PRAGMA table_info(behavioral_examples) shows cn_elevator_pitch. (2) Seed script reports "Updated 7/7 master-story pitches" — all 7 target example_ids updated, none missing. (3) uvicorn restarted (killed PID 12656 then PID 23780, relaunched on 127.0.0.1:8100). (4) Curl /api/behavioral/examples/by-example-id/EX-34 via urllib returns cn_elevator_pitch key present and populated with the exact seeded 361-char Chinese string. Verified all 7 example_ids through the API consumer path (not just a direct SELECT), each returns the correct length (EX-09B=334, EX-15=145, EX-16=245, EX-17=197, EX-30=189, EX-33B=207, EX-34=361). (5) Frontend `npm run build` (which runs tsc -b && vite build) succeeds cleanly. (6) Full pytest suite: 1058 passed, 0 failures in 33.91s.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-358 --status completed`
## 2026-04-11 16:50 -- [orchestrator monitoring] Session 1 completed T-P1-358; orchestrator died after 1 task; restarted
- **What I did**: User asked for autonomous run progress check. Investigated state: T-P1-358 successfully completed and committed as a5bb24d during autonomous Session 1 (including catching a real bug: _build_example_response was hand-constructing the dict and would have silently dropped the new cn_elevator_pitch field — Session 1 agent proactively added the dict key in addition to the Pydantic schema change). Verified via git log (1 new commit), task_db (T-P1-358 status=completed, completed_at=2026-04-11), PROGRESS.md (Session 1 wrote its own detailed entry), session_state.json (last_task=T-P1-358, last_status=completed, all_done=false), and 1058/1058 pytest pass. However, the parent bash orchestrator process (PID 9100) died after Session 1 committed: lockfile was stale (PID 9100 recycled by Windows to svchost.exe), output buffer only contained "--- Session 1/8 ---" with no "Session ended. Continuing..." line, no bash.exe process with autonomous_run in its CommandLine. Confirmed by powershell Get-WmiObject Win32_Process filter. Root cause analysis: autonomous_run.sh logic is correct (all_done=false branch should loop to Session 2), and Session 1 claude -p exit code must have been 0 since T-P1-358 committed successfully — so the script reached the "Session ended. Continuing..." branch but never printed it, strongly suggesting the parent bash was killed externally rather than by its own logic. Most likely cause: the Claude Code harness's long-lived background subprocess management did not keep the orchestrator alive across main-session turn boundaries. Cleaned up stale .claude/autonomous.lock and restarted with `bash scripts/autonomous_run.sh 7` as background task bq5yj0ljr. Flagged to user that if the restarted background dies again after 1-2 commits, it's the harness background issue and they should run autonomous_run.sh from their own terminal for reliability.
- **Deliverables**: Removed stale .claude/autonomous.lock (PID 9100 was svchost, not the bash parent). Relaunched background autonomous_run.sh (id bq5yj0ljr, targeting 7 remaining P1/P2 tasks).
- **Sanity check result**: (1) git log confirms a5bb24d T-P1-358 commit with correct [T-P1-358] prefix. (2) task_db.py direct query: T-P1-358 status='completed', completed_at='2026-04-11'. (3) session_state.json: last_task=T-P1-358, all_done=false — orchestrator should NOT have stopped per its own logic. (4) Lockfile was stale: PID 9100 is now svchost.exe not bash. (5) Confirmed no bash.exe process currently has 'autonomous_run' in its CommandLine via powershell Get-WmiObject. (6) Background task bq5yj0ljr launched; output buffer will grow as sessions proceed.
- **Status**: [PARTIAL] — 1 of 8 tasks committed (T-P1-358). Restarted orchestrator monitoring remaining 7 (T-P1-359 through T-P2-365). If background dies again after minimal progress, hand off to user's own terminal for reliability.
- **Request**: No task_db update from this monitoring pass — T-P1-358 was already updated by the autonomous Session 1.
## 2026-04-11 -- [T-P1-359] Behavioral API: add theme filter to /examples + regression tests
- **What I did**: Primary investigation found the root cause noted in the spec (stale uvicorn cache) had already been resolved during the previous T-P1-358 session -- running uvicorn PID 145752 (`C:\Anaconda\python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8100`) was serving current code: GET /api/behavioral/questions already included theme_tags key and ?theme=failure_setback correctly returned 15 filtered rows. So the only remaining code change was step 4: add theme parameter to list_examples (which previously had no theme support at all). Added `theme` + `theme_mode` Query params to src/backend/routers/behavioral.py::list_examples, mirroring the list_questions pattern but joining through ExampleThemeTag instead of QuestionThemeTag. Reused the existing BehavioralTheme slug validation, 400 on unknown slug, 400 on invalid theme_mode, OR/AND set semantics. Added 5 regression tests to tests/test_behavioral_themes.py: single-theme filter on /examples, multi-theme OR, unknown-slug 400, invalid-mode 400, and a theme_tags-presence assertion on /questions to pin the T-P1-354 contract.
- **Deliverables**: src/backend/routers/behavioral.py (list_examples: +39 lines adding theme filter + join through ExampleThemeTag), tests/test_behavioral_themes.py (+5 new test functions).
- **Sanity check result**: (1) Captured pre-restart evidence: PID 145752, cmdline=uvicorn Anaconda, routers/behavioral.py md5=ce2bb5ae99a27d5b3c1ce2adaef03614 (the updated version). Killed PID 145752 via psutil and relaunched uvicorn on 127.0.0.1:8100 in background. Server came up on first ping. (2) Consumer verification through urllib: /api/behavioral/questions?theme=failure_setback returns 15 rows, each with theme_tags array (confirming T-P1-354 still holds after restart). /api/behavioral/examples?theme=failure_setback returns exactly 5 rows with ids={EX-15, EX-16, EX-17, EX-30, EX-33B} -- matches the task spec's expected master failure-cluster stories. /api/behavioral/examples (unfiltered) returns 34 rows, proving the filter actually reduces the set. /api/behavioral/examples?theme=bogus -> 400, ?theme=failure_setback&theme_mode=xor -> 400. (3) pytest tests/test_behavioral_themes.py: 14/14 pass (9 existing + 5 new). (4) Full pytest suite: 1063 passed in 33.80s (up from 1058 after adding the 5 regression tests, zero existing-test regressions).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-359 --status completed`
## 2026-04-11 18:50 -- [infra] Orchestrator SIGPIPE root cause + PowerShell runner + bash patch
- **What I did**: User pushed back on my "just run it from your terminal" recommendation and asked for real root-cause investigation plus a PowerShell-native alternative — they'd run autonomous_run.sh for hours in prior sessions without this issue. Forensically diagnosed the die-after-1-task pattern by cross-correlating output buffer mtimes with commit timestamps: second run (bq5yj0ljr) started 17:13:26, wrote "--- Session 1/7 ---" at 17:13:30 (4 seconds in), then the output buffer STOPPED updating. But the T-P1-359 commit landed at 17:28:44 — 15 minutes later. That 15-minute gap is only explainable if (a) Session 1's inner claude -p was still running normally and committed successfully, AND (b) the parent bash was still alive (otherwise wait on claude -p would not have returned). The parent must have died in the first statement AFTER claude -p returned, which is the "echo Session ended. Continuing..." line. Conclusion: Claude Code's run_in_background subprocess capture closes the child's stdout fd at some point (timeout? turn boundary? buffer threshold? unknown, not a priority to dig further), and bash's echo to the closed fd fires SIGPIPE, which set -euo pipefail promotes to script termination. Fix is trivially "trap '' PIPE" + redirect stdout to an owned file via tee. Applied two fixes: (1) patched scripts/autonomous_run.sh at the top with `trap '' PIPE; mkdir -p logs; exec > >(tee -a logs/autonomous.log) 2>&1` plus a comment block with the forensic timeline, and changed `python3` to `python` to dodge the Windows Store stub that is already blocklisted in this project's CLAUDE.md. (2) New scripts/autonomous_run.ps1 — PowerShell-native rewrite mirroring the bash version's lockfile / MaxSessions loop / all_done check / git-stash-on-failure / consecutive-failure counter logic, using Start-Process + Get-Process -Id for lockfile + ConvertFrom-Json for state + Tee-Object-to-file for logging. .NOTES docblock at the top documents the SIGPIPE forensic evidence so a future reader understands why the PowerShell version exists at all. Both files syntax-checked clean (bash -n and powershell.exe PSParser::Tokenize). User acknowledged handoff and is running the PowerShell version against the remaining 6 tasks (T-P1-360 through T-P2-365) from their own Windows PowerShell session.
- **Deliverables**: scripts/autonomous_run.ps1 (new, 165 lines, PowerShell-native), scripts/autonomous_run.sh (patched: SIGPIPE guard + tee log redirect + python3→python). Both uncommitted, left for user to commit with their own timing.
- **Sanity check result**: (1) bash -n scripts/autonomous_run.sh reports no syntax errors. (2) powershell.exe -NoProfile -Command "[System.Management.Automation.PSParser]::Tokenize(...)" reports no parse errors. (3) Forensic correlation confirmed: output buffer last-write timestamp (17:13:30) is 15m14s before T-P1-359 commit (17:28:44) — only consistent with stdout-closed-before-subprocess-returns hypothesis. (4) `which python3` on this git-bash resolves to AppData/Local/Microsoft/WindowsApps/python3 (Windows Store stub) — directly confirmed the python3 trap is live on this machine. (5) Did NOT restart autonomous_run from my end this time — user is now the babysitter, per their explicit request.
- **Status**: [DONE] for the investigation + fix. 2/8 tasks committed so far (T-P1-358, T-P1-359). Remaining 6 tasks handed to user for PowerShell-driven execution.
- **Request**: No task_db update — infra investigation, no task in the backlog corresponds to it. Not filing a new task for this either; the fix is in-place and documented in the script's own comment block.
## 2026-04-11 -- [T-P1-360] QuickIndex: add section toggle bar (LC / ML coding / BQ)
- **What I did**: Restructured QuickIndex.tsx to split the 16-item problems array into LC_PROBLEMS (14 items with lcId) and ML_PROBLEMS (2 items without lcId). Added a top toggle bar with three buttons (LeetCode / ML Coding / Behavioral) using useSearchParams for URL-persisted ?section=lc|ml|bq state. Each section renders conditionally: LC and ML show their respective problem grids, BQ shows a placeholder for T-P1-361. Default section is 'lc' when no param is present.
- **Deliverables**: src/frontend/src/pages/QuickIndex.tsx (rewritten: split arrays, toggle bar, conditional rendering, useSearchParams)
- **Sanity check result**: (1) npm run build (tsc -b + vite build) passes clean. (2) Dev server on localhost:5173 serves /quick-index with 200. (3) Full pytest suite: 1063 passed in 34.02s, zero regressions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-360 --status completed`
## 2026-04-11 -- [T-P1-361] QuickIndex BQ section: render theme cards grouped by cluster
- **What I did**: Replaced the BQ placeholder in QuickIndex.tsx with a full theme-card grid. Added a useQuery call to /api/behavioral/themes (enabled only when section==='bq', staleTime Infinity). Defined CLUSTER_FAMILIES inline with 7 semantic groups covering all 15 theme slugs. Each family renders a heading + grid of ThemeCard components showing label and "N questions / M examples" counts from the API. Cards link to /behavioral/theme/<slug>?from=quick-index. Themes with 0 questions and 0 examples are dimmed. Unknown themes (not in any family) fall into an "Other" group.
- **Deliverables**: src/frontend/src/pages/QuickIndex.tsx (rewritten BQ section: useQuery, CLUSTER_FAMILIES, ThemeCard component)
- **Sanity check result**: (1) npm run build (tsc -b + vite build) passes clean. (2) Dev server on localhost:5173 serves /quick-index?section=bq with 200. (3) API at localhost:8100/api/behavioral/themes returns all 15 themes with correct counts. (4) Full pytest suite: 1063 passed in 54.74s, zero regressions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-361 --status completed`
## 2026-04-11 -- [T-P1-362] BQ theme detail page: example cards with Chinese pitch + STAR drawer
- **What I did**: Created new page component BehavioralThemePage.tsx at route /behavioral/theme/:slug. Page fetches theme metadata, examples (filtered by theme slug), and questions from existing API endpoints. Renders example cards showing example_id badge, title, and cn_elevator_pitch split into summary + KEY FACTS pills. Clicking a card opens SlideOverPanel with full ExampleDrawerContent (STAR sections) using the already-loaded example object (no second fetch). Questions rendered as a bulleted list below. Added CSS for CN/EN pitch pill typography with explicit font-family and line-height to prevent baseline jitter. Back link returns to /quick-index?section=bq.
- **Deliverables**: src/frontend/src/pages/BehavioralThemePage.tsx (new), src/frontend/src/App.tsx (route added), src/frontend/src/index.css (bq-pitch-text/bq-pitch-pill styles)
- **Sanity check result**: (1) npm run build passes clean. (2) All 15 theme slugs return 200 from dev server. (3) failure_setback API returns 5 examples (EX-15/16/17/30/33B) all with cn_elevator_pitch. (4) Full pytest suite: 1063 passed, zero regressions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-362 --status completed`
## 2026-04-11 -- [T-P2-363] BQ navigation: end-to-end browse-path preservation across QuickIndex/theme/drawer
- **What I did**: Created useReturnPath hook (reads ?from= param, returns correct QuickIndex URL with section preserved) and useRouteScrollRestore hook (saves/restores window.scrollY via sessionStorage keyed by location.key). Wired both hooks into BehavioralThemePage; wired scroll restore into QuickIndex. Removed redundant inline back-link logic from BehavioralThemePage. Verified SlideOverPanel does not add history entries (uses local state only) and preserves scroll (body overflow:hidden does not reset scrollTop).
- **Deliverables**: src/frontend/src/hooks/useReturnPath.ts (new), src/frontend/src/hooks/useRouteScrollRestore.ts (new), src/frontend/src/pages/BehavioralThemePage.tsx (refactored), src/frontend/src/pages/QuickIndex.tsx (scroll restore added)
- **Sanity check result**: (1) npm run build passes clean. (2) All routes return 200 (quick-index?section=bq, theme pages with/without ?from). (3) Full pytest suite: 1063 passed, zero regressions. (4) Path verification: P1 drawer open/close preserves scroll (body overflow:hidden, no scrollTop reset). P2 Back link goes to /quick-index?section=bq. P3 Browser back works (Link push, not replace). P4 Deep link without ?from defaults to /quick-index?section=bq. P5 URL section param persists on refresh. P6 setParams pushes history entries preserving section on back.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-363 --status completed`
## 2026-04-11 -- [T-P2-364] Failure cluster structural polish: tags + narration guards
- **What I did**: Created idempotent script `scripts/_polish_failure_cluster_structural.py` that adds principle_tags and narration-risk guard paragraphs to EX-15/16/17/30 risk_statements. Each edit gated on sentinel strings (`<!-- NRG-v1 -->`, `<!-- TPV-v1 -->`) so re-running is safe. Tags added: failure+humility+process_improvement_from_incident (EX-15), failure+humility+cross_boundary_failure (EX-16), failure+humility (EX-17), failure verified (EX-30 already had it). No factual content, evidence_quotes, analogies, or STAR text was modified.
- **Deliverables**: `scripts/_polish_failure_cluster_structural.py` (new), `data/mle_prep.db` (4 rows updated)
- **Sanity check result**: (1) Script ran successfully, all patches applied. (2) Re-run confirmed idempotent (all skips, no duplicates). (3) DB verification: all 4 examples have 'failure' tag and NRG sentinel; EX-16 also has TPV sentinel. (4) API consumer verification: all 4 examples verified via localhost:8100/api/behavioral/examples/by-example-id/. (5) Full pytest suite: 1063 passed, zero regressions.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-364 --status completed`
## 2026-04-11 -- [T-P2-365] Behavioral audit: technical_problem_solving data-driven evidence
- **What I did**: Audited all 28 examples tagged with `technical_problem_solving` theme for explicit data-driven evidence. Checked each example's Action and Result sections against four criteria: (a) quantitative number in Result, (b) metric name + direction in Action, (c) A/B test reference, (d) data-derived hypothesis. Generated comprehensive audit report with PASS/NEEDS-NOTE/RECOMMEND-UNTAG verdicts.
- **Deliverables**: `docs/audits/tech_depth_data_driven_2026-04.md` (new audit report)
- **Sanity check result**: (1) All 28 examples accounted for (task estimated 27). (2) Summary counts: 8 PASS, 13 NEEDS-NOTE, 7 RECOMMEND-UNTAG. (3) Full pytest suite: 1063 passed, zero regressions. (4) No DB modifications (audit-only task).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-365 --status completed`
## 2026-04-12 -- BQ Quick Index UX audit and task planning
- **What I did**: Investigated two user-reported issues on the BQ Quick Index page: (1) Chinese/English inconsistency in example cards (27/34 missing cn_elevator_pitch), (2) lack of text formatting. User clarified scope: only need cn_elevator_pitch for all 27 missing examples, keep mixed CN+EN-term style, no STAR formatting changes. Created 2 tasks: T-P0-366 (batch 1, 14 examples BLOG-01~EX-09) and T-P0-367 (batch 2, 13 examples EX-10~EX-33, depends on 366). Sent full scoping to Discord for review.
- **Deliverables**: T-P0-366 and T-P0-367 created in task_db with full description/AC. TASKS.md regenerated.
- **Sanity check result**: (1) Verified 27 examples missing cn_elevator_pitch via DB query. (2) Confirmed PUT /behavioral/examples/{id} API supports cn_elevator_pitch updates. (3) Both tasks visible in task_db with correct dependency chain.
- **Status**: [PARTIAL] -- tasks created, awaiting user confirmation to launch autonomous_run.sh
- **Request**: No status update yet -- tasks are active, pending execution approval
## 2026-04-12 -- [T-P0-366] BQ Quick Index: generate cn_elevator_pitch batch 1
- **What I did**: Generated and PUT cn_elevator_pitch for 14 examples (BLOG-01, BLOG-01B, BLOG-02, BLOG-03, BLOG-04, EX-01 through EX-09). Each pitch follows the established format: Chinese summary with English technical terms + KEY FACTS section. Content distilled from each example's STAR fields. Used PUT /behavioral/examples/{db_id} API for all updates.
- **Deliverables**: scripts/_batch1_cn_pitches.py (update script), 14 examples now have cn_elevator_pitch in database.
- **Sanity check result**: (1) All 14 PUT requests returned matching cn_elevator_pitch. (2) Verification pass confirmed 14/14 have non-null pitch. (3) Total count: 21/34 examples now have cn_elevator_pitch (was 7, added 14). Remaining 13 are batch 2 (T-P0-367).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-366 --status completed`
## 2026-04-12 -- [T-P0-367] BQ Quick Index: generate cn_elevator_pitch batch 2
- **What I did**: Generated and PUT cn_elevator_pitch for remaining 13 examples (EX-10, EX-11, EX-12, EX-13, EX-14, EX-18, EX-19, EX-20, EX-21, EX-22, EX-23, EX-24, EX-33). Each pitch follows the established format: Chinese summary with English technical terms + KEY FACTS section. Content distilled from each example's STAR fields.
- **Deliverables**: scripts/_batch2_cn_pitches.py (update script), 13 examples now have cn_elevator_pitch in database.
- **Sanity check result**: (1) All 13 PUT requests returned matching cn_elevator_pitch. (2) Final verification: 34/34 examples now have cn_elevator_pitch. (3) Zero missing pitches remain.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-367 --status completed`
## 2026-04-12 -- Post-auto-run: verification + process cleanup
- **What I did**: (1) Verified autonomous_run.sh completed both T-P0-366 and T-P0-367 successfully (34/34 cn_elevator_pitch populated, 2 commits landed). (2) Cleaned up stale processes left by autonomous sessions: killed 1 orphaned claude process, 3 duplicate uvicorn backends (ports 8200, 8210, 8100), 3 old PowerShell sessions, and several stale bash shells from earlier sessions and Apr 10. Kept current session, frontend dev server (npm run dev), and original backend (uvicorn :8765).
- **Deliverables**: No code changes. Process cleanup only.
- **Sanity check result**: (1) 34/34 examples confirmed with cn_elevator_pitch via DB query. (2) git log shows commits a123658 (batch 1) and 8bbd236 (batch 2). (3) Process list reduced from ~25 to ~5 active processes.
- **Status**: [DONE]
- **Request**: No task_db update -- tasks already marked completed by autonomous sessions
## 2026-04-13 -- Autonomous session: no unblocked tasks
- **What I did**: Evaluated TASKS.md for highest-priority unblocked task. All 10 remaining tasks are blocked [SYNC] tasks requiring writes to helixos/ or claude-code-project-template/ directories, which cannot be done from an MLInterviewPrep session due to file permission constraints.
- **Deliverables**: None. Read-only evaluation only.
- **Sanity check result**: Confirmed all 10 tasks have BLOCKED status and [SYNC] tag. No P0/P1/P2 unblocked tasks exist.
- **Status**: [DONE] -- no actionable work available
- **Request**: No task_db update -- no task was worked on. session_state.json all_done=true remains correct.
## 2026-04-11 -- [behavioral] Deepen EX-15 and EX-16 with user-provided incident analysis framework
- **What I did**: User provided a detailed framework for the cross-DC static compilation incident (EX-16) and clarifying details (preprod not prod, force-merge rollback, Head of Engineering RCA, science team factor migration). Deepened both EX-15 and EX-16 in bq_behavioral_examples.json and bq_improved_stories.md with three key improvements: (1) Upgraded root cause framing from personal ("didn't ask the right person") to architectural ("deployment model assumes loose DC coupling, but static compilation creates implicit strong coupling -- an undocumented mismatch"). (2) Added concrete details: preprod containment, Head of Engineering RCA presentation, systematic follow-up cleanup of additional implicit coupling instances, science team factor/model migration to declarative artifactory. (3) Established cross-reference thread between EX-15 and EX-16 around shared core lesson: "the most dangerous dependencies are the undocumented implicit ones." Updated arc-5 improvement_notes in bq_story_arcs.json to reflect that EX-15/16 are no longer "thin." User chose blended A+B framing: acknowledge failure/setback but emphasize clear root cause judgment and proactive response.
- **Deliverables**: docs/bq_behavioral_examples.json (EX-15 and EX-16 STAR fields rewritten), docs/bq_improved_stories.md (Story 15 and Story 16 rewritten), docs/bq_story_arcs.json (arc-5 improvement_notes updated).
- **Sanity check result**: Both JSON files pass json.load() validation. All three files edited consistently with the same thematic changes.
- **Status**: [DONE]
- **Request**: No task_db update -- this is collaborative interactive work on behavioral prep content, not a backlog task.
## 2026-04-12 -- Add Pinterest must-do LC problem list (14 problems)
- **What I did**: Added 14 Pinterest must-do LeetCode problems to the DB. Tagged 11 existing problems with "Pinterest" company tag, created 2 new problems (LC 1110 Delete Nodes And Return Forest, LC 1723 Find Minimum Time to Finish All Jobs), 1 was already tagged. Added full problem table to docs/pinterest_recruiter_call_prep.md. Created idempotent seed script.
- **Deliverables**: scripts/seed_pinterest_lc_problems.py (new), docs/pinterest_recruiter_call_prep.md (updated with LC list table), data/mle_prep.db (14 problems tagged)
- **Sanity check result**: Verified all 14 problems present in DB with Pinterest tag via direct SQL query. 6/14 already completed, 8 remaining.
- **Status**: [DONE]
- **Request**: No task_db update -- ad-hoc user request, not a backlog task.
## 2026-04-12 -- LC 332 Reconstruct Itinerary: solution analysis and notes
- **What I did**: Analyzed user's LC 332 solution, identified it as Hierholzer's Algorithm for Eulerian Path. Wrote comprehensive problem notes covering: algorithm explanation, why post-order matters, code review (naming, build pattern, state management, dead code removal), complexity analysis, edge cases, and interview pattern recognition. Updated DB notes with Pinterest prep doc drawer link. Replied on Discord with full analysis in Chinese.
- **Deliverables**: data/mle_prep.db (LC 332 notes field updated, 2977 chars)
- **Sanity check result**: Verified notes saved in DB via SELECT query, confirmed content starts with correct header and link.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching via Discord, not a backlog task.
## 2026-04-12 -- LC 465 Optimal Account Balancing: bitmask DP notes + correctness proof
- **What I did**: Wrote comprehensive notes for LC 465 into DB. Covered: core reformulation (min transactions = n - max zero-sum partitions), polished bitmask DP code with review of user's code, naive DFS alternative, and detailed correctness proof addressing user's question about why "opposite signs only" and "j > i" are sufficient. Key lemma: Full-Transfer Optimality. Replied on Discord in Chinese with full analysis.
- **Deliverables**: data/mle_prep.db (LC 465 notes updated, 7565 chars), scripts/_update_465_notes.py (one-shot writer)
- **Sanity check result**: DB update confirmed via script output; Discord reply sent (2 parts).
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching via Discord, not a backlog task.
## 2026-04-12 -- LC 465 addendum: submask enumeration trick (O(3^n) vs O(4^n))
- **What I did**: Appended a section to LC 465 notes explaining why `sub = (sub-1) & mask` is O(3^n) via the `Σ C(n,k) 2^k = 3^n` identity, while `for sub in range(mask+1)` degrades to O(4^n). Covered why the naive version still produces correct answers (guards + XOR-not-containment argument + max-doesn't-inflate lemma), numerical comparison at n=12/16, and the intuition for `(sub-1) & mask` as "decrement in popcount-bit subspace." Replied on Discord summarizing the findings.
- **Deliverables**: data/mle_prep.db (LC 465 notes extended: 7565 -> 9898 chars)
- **Sanity check result**: Script output confirms notes extension; Discord reply sent.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching, not a backlog task.
## 2026-04-12 -- LC 282 Expression Add Operators: brute-force + `prev` trick notes
- **What I did**: Wrote comprehensive LC 282 notes into DB. Covered: (A) cleaned-up version of user's custom myEval brute-force (push/pop vs list-copy, no debug print, concise leading-zero check); (B) polished `prev` trick version with two optimizations over user's code -- `break` instead of `continue` on leading zeros (prunes entire longer-slice branch), and push/pop on shared `expr` list instead of O(n^2) string concatenation. Explained why eval is inappropriate (security optics, perf, interview expectation, env portability), worked example of the `prev` invariant, related-problem list.
- **Deliverables**: data/mle_prep.db (LC 282 notes: 8433 chars), scripts/_update_282_notes.py (one-shot writer)
- **Sanity check result**: Script confirms DB update; Discord reply sent.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching, not a backlog task.
## 2026-04-12 -- LC 2402 Meeting Rooms III: two-heap simulation notes
- **What I did**: Wrote LC 2402 notes into DB. User's solution was correct and near-canonical; focused on the two-heap pattern (free + busy), cosmetic cleanups (`count` naming, `list.index(max(...))` idiom), and the 4 subtle traps (`<=` vs `<`, tuple tiebreak, delay formula uses duration not end, don't re-sort). Added pattern recognition notes pointing to LC 253, 1882, 1834 as related.
- **Deliverables**: data/mle_prep.db (LC 2402 notes: 5257 chars), scripts/_update_2402_notes.py
- **Sanity check result**: DB write confirmed; Discord reply sent.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching.
## 2026-04-12 -- LC 1110 Delete Nodes And Return Forest: DFS + is_root flag notes
- **What I did**: Wrote LC 1110 notes. User's post-order solution was correct but clunky (4 sites of set lookup per node, special-case check for original root after traversal). Presented canonical `dfs(node, is_root)` pattern: carry ancestor-deleted state DOWN via parameter, signal unlinking UP via return value. Added general design principle "carry state down vs handle on way up" and cross-refs to LC 814, 669, 1325.
- **Deliverables**: data/mle_prep.db (LC 1110 notes: 5361 chars), scripts/_update_1110_notes.py
- **Sanity check result**: DB write confirmed; Discord reply sent.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching.
## 2026-04-12 -- Pinterest LC review+index company document
- **What I did**: User clarified they wanted a dedicated Pinterest-company review/index doc (accessible at /companies/29/prep), distinct from per-problem notes and the existing recruiter call prep doc. Created new company_documents entry (id=47, source_type=prep_doc) with: Quick Status table for all 14 problems, Pattern Clusters (Graph/Eulerian, Backtracking, DP Subsets, Heap Simulation, String Arithmetic), Core Patterns Cheat Sheet compressing 5 already-written algorithm templates, Common Traps cross-refs, and a Daily Review Template. Script is idempotent (update-by-title).
- **Deliverables**: data/mle_prep.db (company_documents id=47, 6239 chars), scripts/_create_pinterest_lc_index_doc.py
- **Sanity check result**: Verified via SQL SELECT that doc exists for company_id=29. Backend on :8000 not running so API consumer check skipped; frontend on :5173 up.
- **Status**: [DONE]
- **Request**: No task_db update -- ad-hoc user request.
## 2026-04-12 -- Clickable `lc://N` links + ProblemDrawer for company prep docs
- **What I did**: Implemented end-to-end feature: clicking an LC problem reference in a company prep doc opens a right-side drawer with the problem description + solution notes. Backend: added `GET /api/problems/by-lc/{lc_id}` route (registered BEFORE `/problems/{problem_id}` to avoid path shadowing). Frontend: (1) new `ProblemDrawer.tsx` component using existing `SlideOverPanel` primitive, with difficulty/pattern/completed badges and markdown-rendered description+notes; (2) extended `MarkdownPreview` with `onLcLinkClick?` prop and an `a` component override -- `href="lc://N"` renders as button invoking handler, everything else behaves as external anchor; (3) wired `lcDrawerId` state into `DocumentViewer` in `PrepNotesPage.tsx`. Updated Pinterest LC index doc (id=47) to use `lc://N` syntax throughout Quick Status table and Pattern Clusters.
- **Deliverables**: src/backend/routers/problems.py (new route), src/frontend/src/components/problems/ProblemDrawer.tsx (new), src/frontend/src/components/ui/MarkdownPreview.tsx (prop + a override), src/frontend/src/pages/PrepNotesPage.tsx (state + render), data/mle_prep.db (doc 47 content updated to 6647 chars), scripts/_create_pinterest_lc_index_doc.py (updated)
- **Sanity check result**: `npx tsc --noEmit` -> 0 errors. Route ordering confirmed via router.routes introspection (`/problems/by-lc/{lc_id}` before `/problems/{problem_id}`). DB query tested directly: LC 332 -> id=148 with 2977-char notes; LC 99999 -> None (404 path). No full browser E2E because backend not running.
- **Status**: [DONE] -- pending user's browser-side smoke test when backend is started.
- **Request**: No task_db update -- ad-hoc user feature request.
## 2026-04-12 -- Audit + batch plan: Chinese LC notes, missing descriptions, missing notes
- **What I did**: User requested (via Discord) that LC notes should be in Chinese by default (except technical terms) and that missing problem descriptions need to be fetched. Used task planning mode (not execution). (1) Audited all 14 Pinterest problems: found 5 pure-English notes, 3 mixed, 2 already Chinese, 4 with no notes; separately 3 problems missing descriptions. (2) Created 12 tasks via task_db.py batch: T-P1-368..372 (translate 5 EN notes to CN), T-P2-373 (polish 3 mixed notes), T-P1-374 (fetch 3 missing descriptions), T-P1-375..378 (write 4 new notes in Chinese: LC 410/43/642/1723), T-P2-379 (refresh Pinterest index doc after everything). Added dependencies T-P2-379 -> {368,374,377,378}. (3) Saved feedback_lc_notes_chinese.md memory: Chinese prose + English for code/algorithm-names/complexity notation, with explicit do/don't list.
- **Deliverables**: .claude/tasks.db (12 new tasks), TASKS.md (regenerated), ~/.claude/.../memory/feedback_lc_notes_chinese.md, MEMORY.md updated
- **Sanity check result**: task_db.py batch returned all 12 task IDs cleanly; depend commands succeeded; project regenerated TASKS.md.
- **Status**: [DONE] -- planning phase. Execution pending user direction (autonomous_run.sh vs manual selection).
- **Request**: No single-task update; 12 P1/P2 tasks now in backlog awaiting execution.
## 2026-04-12 -- Clarification: preserve inline English terms where natural
- **What I did**: User clarified that the Chinese-notes rule should not aggressively replace English terms -- when an English word reads naturally inline (greedy, partition, state, sliding window, etc.) and translating would be awkward, keep it English. Updated feedback_lc_notes_chinese.md memory accordingly. Told user to launch autonomous via their proven PowerShell path (autonomous_run.ps1) and listed the expected task execution order.
- **Deliverables**: ~/.claude/.../memory/feedback_lc_notes_chinese.md (clarification added)
- **Sanity check result**: Memory file updated; Discord instructions sent.
- **Status**: [DONE]
- **Request**: No task_db update.
## 2026-04-12 -- [T-P1-368] Translate LC 332 notes to Chinese
- **What I did**: Translated LC 332 (Reconstruct Itinerary / Hierholzer's Algorithm) solution notes from English to Chinese. Existing DB notes had a missing code block and stripped backticks in the review table; rewrote with a canonical Hierholzer Python solution and dropped the broken review table. Kept algorithm names, code, complexity notation, and technical terms (heap, post-order, DFS, dead-end, Eulerian Path, Hamiltonian Path) in English per feedback_lc_notes_chinese.md.
- **Deliverables**: scripts/_update_332_notes.py; data/mle_prep.db (problems.notes for leetcode_id=332, 2167 chars).
- **Sanity check result**: Script ran clean; verified stored length = 2167 via sqlite SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-368 --status completed
## 2026-04-12 -- [T-P1-369] Translate LC 465 notes to Chinese
- **What I did**: Translated LC 465 (Optimal Account Balancing) solution notes to Chinese following the same bilingual convention as LC 332: algorithm names, code, complexity notation, and technical terms (bitmask, submask, DP state, partition, swap argument) kept in English; prose in Chinese.
- **Deliverables**: scripts/_update_465_notes.py; data/mle_prep.db (problems.notes for leetcode_id=465, 5375 chars).
- **Sanity check result**: Script ran clean; verified stored length = 5375 via sqlite SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-369 --status completed
## 2026-04-12 -- [T-P1-370] Translate LC 282 notes to Chinese
- **What I did**: Translated LC 282 (Expression Add Operators) notes to Chinese following the same bilingual convention: code blocks, algorithm names, and technical terms (backtracking, prev trick, DFS, operand, operator, submask) stay in English; prose in Chinese. Covers Version A (brute-force + custom myEval), why-not-eval argument, Version B (prev trick, canonical solution), and worked example.
- **Deliverables**: scripts/_translate_282_notes.py; data/mle_prep.db (problems.notes for leetcode_id=282, 6418 chars).
- **Sanity check result**: Script ran clean; verified stored length = 6418 via sqlite SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-370 --status completed
## 2026-04-12 -- [T-P1-371] Translate LC 2402 notes to Chinese
- **What I did**: Translated LC 2402 (Meeting Rooms III) notes to Chinese following the bilingual convention: code blocks, heap/tuple/tiebreak/duration and algorithm terms stay in English; prose in Chinese. Covers two-heap simulation pattern, canonical solution, code review, subtle traps, complexity, pattern recognition.
- **Deliverables**: scripts/_translate_2402_notes.py; data/mle_prep.db (problems.notes for leetcode_id=2402, 3829 chars).
- **Sanity check result**: Script ran clean; verified stored length = 3829 via sqlite SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-371 --status completed
## 2026-04-12 -- [T-P1-372] Translate LC 1110 notes to Chinese
- **What I did**: Translated LC 1110 (Delete Nodes And Return Forest) notes to Chinese. Preserved code blocks and English algorithm terms (is_root, DFS, post-order, unlink, membership). Covers key insight, canonical solution, code review, carry-state-down-vs-post-order principle, traps, complexity, pattern recognition.
- **Deliverables**: scripts/_translate_1110_notes.py; data/mle_prep.db (problems.notes for leetcode_id=1110, 3289 chars).
- **Sanity check result**: Script ran clean; stored length = 3289.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-372 --status completed
## 2026-04-12 -- [T-P1-374] Fetch missing Pinterest LC descriptions
- **What I did**: Fetched descriptions for LC 1110, 1723 (via leetcode.ca) and LC 2402 (via leetcode.com GraphQL, since leetcode.ca only hosts IDs <= 1857). Stored into problems.description with description_source set accordingly.
- **Deliverables**: scripts/_fetch_missing_pinterest_desc.py; data/mle_prep.db (problems.description for leetcode_id in {1110, 1723, 2402}).
- **Sanity check result**: Lengths 604 / 918 / 2568 chars respectively; verified via sqlite SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-374 --status completed
## 2026-04-12 -- [orchestrator] Launched autonomous_run.ps1 for 12-task Pinterest CN batch
- **What I did**: Per user approval, launched `powershell -ExecutionPolicy Bypass -File scripts/autonomous_run.ps1 12` in background. Using PowerShell path per 2026-04-11 SIGPIPE lesson (bash autonomous_run.sh dies when parent harness closes stdout fd). At 25-min mark, 6/12 child sessions completed and self-committed (T-P1-368..372 translations + T-P1-374 descriptions); session 7 in flight. Scheduled a wakeup at 17:01 PT to verify completion of remaining 6 (LC 410/43/642/1723 new notes, LC 311/815/1244 polish, T-P2-379 dependent index refresh). Orchestrator sends progress update to Discord.
- **Deliverables**: logs/autonomous.log (live trace); 6 child-session commits (53bb0f2..770bac6 inclusive); 6 child-session PROGRESS.md entries above.
- **Sanity check result**: Log shows all session timestamps advancing every 3-4 min; sessions 1-6 exited 0; SIGPIPE fix effective (no silent death). Git log confirms commits landed. Child sessions update their own task_db status on exit.
- **Status**: [PARTIAL] -- orchestrator-launch work done; 6/12 child tasks complete in background, 6 remaining.
- **Request**: No direct task_db update from this session -- child sessions handle their own.
## 2026-04-12 17:15 -- [T-P1-375] Write LC 410 solution notes (Split Array Largest Sum)
- **What I did**: Wrote Chinese solution notes for LC 410 covering binary-search-on-answer (推荐) with O(n) greedy feasibility check, DP on (i,k) alternative, code review pitfalls (lower bound = max(nums), `while lo < hi` template), recognition triggers for binary-search-on-answer pattern, and related family LC 1011/1760/875/1482. Stored via scripts/_update_410_notes.py into problems.notes.
- **Deliverables**: scripts/_update_410_notes.py; data/mle_prep.db (problems.notes for leetcode_id=410).
- **Sanity check result**: Notes length 3677 chars; sqlite SELECT confirms stored content begins with correct header.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-375 --status completed
## 2026-04-12 17:45 -- [T-P1-376] Write LC 43 solution notes (Multiply Strings)
- **What I did**: Wrote Chinese solution notes for LC 43 covering digit-by-digit with position array (推荐) using `p1=i+j`, `p2=i+j+1` convention, shift-and-add alternative, code review pitfalls ("0" edge case, p1/p2 direction, leading-zero strip, `+=` for carry), recognition template, and related family LC 2/415/67/66/989. Stored via scripts/_update_43_notes.py into problems.notes.
- **Deliverables**: scripts/_update_43_notes.py; data/mle_prep.db (problems.notes for leetcode_id=43).
- **Sanity check result**: Notes length 3020 chars; sqlite SELECT confirms stored content begins with correct header.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-376 --status completed
## 2026-04-12 18:15 -- [T-P1-377] Write LC 642 solution notes (Design Search Autocomplete System)
- **What I did**: Wrote Chinese solution notes for LC 642 covering Trie + node-level `counts` dict (推荐), alternatives (Trie + leaf count DFS, HashMap linear scan), streaming `input(c)` with `cur`+`buf`+`dead` pointer maintenance, `'#'` reset semantics, Top-3 `(-hot, sentence)` sort rule, code review pitfalls (new-sentence hot=1, `+=` across shared nodes, space-in-sentence ordering, `__slots__` memory), recognition template, and related family LC 208/211/677/1268/212. Stored via scripts/_update_642_notes.py into problems.notes.
- **Deliverables**: scripts/_update_642_notes.py; data/mle_prep.db (problems.notes for leetcode_id=642).
- **Sanity check result**: Notes length 4711 chars; sqlite SELECT confirms stored content begins with correct header.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-377 --status completed
## 2026-04-12 18:45 -- [T-P1-378] Write LC 1723 solution notes (Find Minimum Time to Finish All Jobs)
- **What I did**: Wrote Chinese solution notes for LC 1723 covering three approaches -- binary-search-on-answer + backtracking feasibility with three key prunings (sort jobs desc, per-level `seen` set for worker symmetry, "empty-worker first-job fail => break"), bitmask DP `O(k*3^n)` with standard subset enumeration `sub = (sub-1) & mask`, and plain backtracking. Added code-review pitfalls, recognition template distinguishing LC 410 (ordered split) from LC 1723 (arbitrary assignment), and family links LC 698/473/2305/1986. Stored via scripts/_update_1723_notes.py.
- **Deliverables**: scripts/_update_1723_notes.py; data/mle_prep.db (problems.notes for leetcode_id=1723).
- **Sanity check result**: Notes length 5604 chars; sqlite update confirmed.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-378 --status completed
## 2026-04-12 19:05 -- [T-P1-379] Refresh Pinterest LC index doc
- **What I did**: Updated scripts/_create_pinterest_lc_index_doc.py to mark LC 410/43/642/1723 as "Written" in the Notes column and bumped progress line to "14/14 notes written" with Chinese-translation annotation. Re-ran script to refresh company_documents doc id=47.
- **Deliverables**: scripts/_create_pinterest_lc_index_doc.py; data/mle_prep.db (company_documents id=47).
- **Sanity check result**: Script reported [UPDATE] doc id=47 refreshed (6723 chars); verified progress line updated via SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P2-379 --status completed

## 2026-04-12 19:30 -- [T-P2-373] Polish CN notes for LC 311/815/1244
- **What I did**: Wrote scripts/_polish_cn_lc_311_815_1244.py that rewrites the three mixed-language LC notes to fully Chinese prose while keeping code blocks, complexity notation, and standard algorithm names (BFS, CSR, MapReduce, etc.) in English. Translated remaining English prose headings ("My Solution", "Follow-up") and minor phrases to Chinese.
- **Deliverables**: scripts/_polish_cn_lc_311_815_1244.py; data/mle_prep.db (problems id=277/217/199 notes).
- **Sanity check result**: Script reported [UPDATE] LC 311 1692 chars, LC 815 2681 chars, LC 1244 794 chars (rows=1 each). Prose outside code blocks is fully Chinese; remaining ASCII chars are tech terms/identifiers per task spec.
- **Status**: [DONE]
- **Request**: task_db.py update T-P2-373 --status completed

## 2026-04-12 -- [investigation] Session-state + LC 1244 expanded notes with lazy-heap discussion
- **What I did**: (1) Investigated user's concern about session_state update being "blocked" -- ran forensic check: session_state.json is at `{last_task: T-P2-379, all_done: false}` which is correct because T-P2-373 was still running. Reconstructed execution order from logs+git: T-P2-379 ran before T-P2-373 despite T-P2-373 being unblocked earlier, because the orchestrator picks by (priority, sort_order) and T-P2-379 had lower sort_order. No bug; just sort_order + dependency interaction. (2) Written comprehensive LC 1244 expanded notes (5577 chars, fully Chinese) addressing user's observation that real-time `heapq.nlargest` is preferred over lazy heap: walks Approach A (nlargest canonical), Approach B (user's lazy heap with detailed code review of 5 pitfalls including `scores[pid]=-1` magic sentinel risk, heap size unbounded, recovery-required-on-every-path), Approach C (SortedList), when lazy heap is legitimately preferable (streaming LC 703 territory, N>>1M, top-K with small K), and interview talking-points ladder. Ran after session 12 (T-P2-373 polish) completed to avoid overwrite race.
- **Deliverables**: scripts/_update_1244_notes.py (new); data/mle_prep.db (problems.notes for leetcode_id=1244: 794 -> 5577 chars after overwrite of polish version)
- **Sanity check result**: Script reported `[OK] LC 1244 notes updated (5577 chars)`; sqlite SELECT length confirms 5577 stored. Session 12 T-P2-373 had committed first (8105291), then my expanded-notes script ran on top -- verified via git log that T-P2-373 committed before my overwrite. Autonomous runner fully complete: 12/12 sessions, all committed, all child tasks marked completed in task_db.
- **Status**: [DONE]
- **Request**: No task_db update -- investigation/coaching work, not a tracked backlog task.

## 2026-04-13 -- LC 410 code-review appendix for user's curBox variant
- **What I did**: User submitted their LC 410 solution using a `curBox` remaining-capacity counter (non-canonical). Appended a Code Review section to the existing autonomous-written Chinese notes identifying 4 improvements (redundant `v > upperbound` check, non-canonical usedCnt logic, missing early termination on `segs > k`, redundant post-loop mid recalculation) plus a bonus corner-case note on all-zeros semantics. Kept the existing canonical binary-search + DP coverage intact.
- **Deliverables**: scripts/_append_410_code_review.py; data/mle_prep.db (problems.notes leetcode_id=410: 3677 -> 6554 chars)
- **Sanity check result**: Script reported extension 3677 -> 6554; Discord reply sent.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching on already-completed task.

## 2026-04-13 -- LC 43 appendix: three-perspective derivation for `i+j+1` index
- **What I did**: User worked out a good intuition for why `ansArr[i+j+1]` is the correct target index in LC 43 Multiply Strings and asked for a quicker on-the-fly derivation. Appended a "three viewpoints" section to LC 43 DB notes: (A) rigorous weight algebra (`10^(m-1-i) * 10^(n-1-j)` -> k = i+j+1), (B) bounded-length + two-anchor verification (i=m-1 j=n-1 -> k=m+n-1; i=0 j=0 -> k=1, user's own approach), (C) one-liner mnemonic with `99*99` sanity check. Also clarified that the two for-loops (accumulation vs carry propagation) are decoupled -- index derivation and carry logic should be discussed separately.
- **Deliverables**: scripts/_append_43_weight_derivation.py; data/mle_prep.db (problems.notes leetcode_id=43: 3020 -> 4912 chars)
- **Sanity check result**: Script reported extension 3020 -> 4912 chars; Discord reply sent with matching structure.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching on completed task.

## 2026-04-13 -- LC 410 enrichment: segs=1 correctness defense
- **What I did**: User asked to roll Discord discussions back into the DB notes. Added a new "深入点 #2" section to LC 410 capturing the `segs=1` vs `usedCnt=0` debate: core invariant (non-empty array -> >= 1 segment), corner-case table contrasting behavior on 4 inputs, "全零 AC 是运气不是正确" argument, and the variant-problem failure mode (minimize-seg-count tasks where usedCnt=0 algorithm breaks). Completed the sweep: audited all 14 Pinterest problems, confirmed every other discussion point is already captured in the corresponding problem's notes.
- **Deliverables**: scripts/_append_410_segs_defense.py; data/mle_prep.db (LC 410 notes: 6554 -> 8107 chars)
- **Sanity check result**: Script reported extension; 14-problem audit table shared on Discord showing final notes lengths.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive enrichment pass.

## 2026-04-13 -- LC 1723 audit: existing notes are optimal, user's code missing pruning #3
- **What I did**: User shared their LC 1723 solution and asked to verify coverage is optimal. Read full DB notes (5604 chars) -- already comprehensive with Approach A (binary search + backtracking + 3 prunings), Approach B (bitmask DP O(k*3^n)), Approach C (plain backtracking), 7 code-review points, pattern recognition with 5 related problems, interview talking template, LPT greedy discussion. Concluded: no DB changes needed. Separately flagged user's code gaps: (1) missing "empty-worker-first-job-fail => break" pruning (their seenCapacity subsumes it in most cases but is not identical); (2) `self.ans` instance variable pattern is awkward -- return-value DFS is cleaner.
- **Deliverables**: No DB write (existing notes already optimal); Discord reply with concrete diffs between user's code and canonical.
- **Sanity check result**: Verified notes cover all 3 approaches + all 3 prunings + full related-problem family. No gaps found.
- **Status**: [DONE]
- **Request**: No task_db update.

## 2026-04-13 -- LC 642 code review: Trie API cleanness + encapsulation
- **What I did**: User shared their LC 642 AutocompleteSystem implementation using Trie + incremental cursor + dead flag, asked for code-review focused on cleanness. Reviewed 6 improvement axes: (1) `match(word, startNode)` dual-mode API confusion -> split to single-mode `advance(ch)`, (2) `dead` flag leaking from Trie into AutocompleteSystem (encapsulation violation) + redundant outer check, (3) `defaultdict(TrieNode)` autovivification risk in query paths -> explicit `setdefault` + `get`, (4) double return signals (dead flag + []) -> pick one, (5) kept `heapq.nsmallest(3, ...)` (semantically clearer than `sorted[:3]`), (6) scale-up optimization: precompute top-3 at each node for O(3) query. Included full improved reference implementation with iterative DFS (no recursion stack overflow risk) and `cursor: Optional[TrieNode]` idiom.
- **Deliverables**: scripts/_append_642_code_review.py; data/mle_prep.db (LC 642 notes: 4711 -> 9711 chars)
- **Sanity check result**: Script reported extension 4711 -> 9711; Discord reply sent with numbered diff.
- **Status**: [DONE]
- **Request**: No task_db update -- interactive coaching.

## 2026-04-13 -- Fix drawer blank-content bug + mark all Pinterest problems Done
- **What I did**: User reported Pinterest prep page drawer links "work but open to blank". Diagnosed: react-markdown v10's default `urlTransform` sanitizes non-whitelisted URL schemes (http/https/mailto/tel) BEFORE the custom `a` component override runs, so `lc://N` href arrived as empty string. My override's regex didn't match, and the fallback `<a href="" target="_blank">` opened a blank new tab. Fixed by adding `urlTransform={(url) => url}` (identity) to MarkdownPreview's ReactMarkdown config -- safe because our custom `a` override already handles the security split (lc:// -> button, everything else -> external anchor with noopener). Separately: user reported all 14 problems are solved and want status updated. Marked all 14 Pinterest problems `is_completed=1` in DB and regenerated the index doc with Status="Done" across the board.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx (urlTransform added); scripts/_create_pinterest_lc_index_doc.py (status column all Done); data/mle_prep.db (14 problems is_completed=1; company_documents id=47 refreshed to 6687 chars)
- **Sanity check result**: `npx tsc --noEmit` -> 0 errors. Backend on :8000 confirmed NOT running (curl returns 000); user needs to start it for the drawer API fetch to succeed.
- **Status**: [DONE] -- pending user's browser smoke test after backend start.
- **Request**: No task_db update -- infrastructure fix + status reflecting completed work; no new tasks.

## 2026-04-13 -- Lesson-worthy: react-markdown v10 urlTransform strips custom schemes
- **What I learned**: Custom URL schemes (e.g., `lc://N` for drawer-opening links) are silently stripped by react-markdown v10's default `defaultUrlTransform`. The user-facing symptom was "clicks work but content is blank" because `<a href="">` opens a blank tab. Custom `a` component overrides receive the already-sanitized href, so they can't inspect or preserve the original.
- **Fix pattern**: Pass `urlTransform={(url) => url}` (identity) to ReactMarkdown when you want custom-scheme links to reach your component override. Pair this with a defensive `a` override that still routes unknown schemes safely (e.g., fall through to `rel="noopener noreferrer"` on real http(s), or simply render `children` as text for unsupported schemes).
- **Detection**: The only visible signal was "clicking a styled link opens a blank tab" -- no console errors, no network failures. Diagnostic hint: inspect the rendered DOM of the link -- if `href` is empty string, the sanitizer is the culprit.
- **Applies to**: Any project using react-markdown 8+ with custom drawer-on-click or app-internal-route schemes.

## 2026-04-13 -- BQ rubric audit: 34 stories scored against strong/weak signal framework
- **What I did**: User supplied a 5-strong + 4-weak signal rubric and asked to audit all BQ examples. Delegated full scan to Explore agent (read-only, nuanced judgment task) across DB `behavioral_examples` + `docs/bq_*.json` + `docs/bq_improved_stories.md`. Corpus is 34 stories (IDs 1-30, 33-36; 31-32 absent). Classified into Tier 1 rework (7 stories), Tier 2 minor polish (19), Tier 3 solid (8). Identified 3 systemic cross-corpus fixes: adjective-to-metric replacement (~15 stories), Action-section "we" to "I" shift (~11 stories), incident stories need post-fix verification metrics (EX-19, EX-20). Reported findings to user on Discord with two execution options: A) fine-grained per-story tasks (~11 total), B) coarse three sweep tasks addressing each systemic fix family + individual Tier-1 rewrites.
- **Deliverables**: No DB writes (pure audit phase); Discord reply with tiered tables + systemic fix analysis + execution plan options.
- **Sanity check result**: Audit covers all 34 DB entries; cross-referenced with bq_improved_stories.md; Tier-1/2/3 buckets sum to 34.
- **Status**: [DONE] audit phase -- awaiting user choice between plan A/B for execution.
- **Request**: No task_db update yet -- execution tasks will be added after user picks plan granularity.

## 2026-04-13 -- BQ rework plan A: 10 tasks created in task_db
- **What I did**: User chose Plan A (fine-grained). Batched 10 tasks via task_db.py: 7 P0 individual Tier-1 rewrites (T-P0-380..386 for EX-12/16/19/20/22/28/33) + 3 P1 Tier-2 sweeps (T-P1-387 metric-number replacement across ~12 stories, T-P1-388 "we"->"I" ownership sharpening in Action sections across ~6 stories, T-P1-389 catch-all polish for remaining Tier-2). Each task description includes specific target stories, concrete fixes per 2026-04-13 audit, and instruction to edit both docs/bq_behavioral_examples.json + docs/bq_improved_stories.md. Regenerated TASKS.md.
- **Deliverables**: .claude/tasks.db (10 new tasks), TASKS.md (regenerated)
- **Sanity check result**: task_db.py batch returned all 10 task IDs; project command confirmed regen.
- **Status**: [DONE] planning. Execution pending user's go-ahead on autonomous launch.
- **Request**: 10 P0/P1 tasks queued; await user direction on autonomous_run.ps1 launch.

## 2026-04-13 -- BQ rework tasks enriched with user-provided facts + TODO placeholder rule
- **What I did**: User reviewed the 10-task plan and supplied concrete facts for 4 stories via Discord: EX-12 (custom-deploy rate 80%->50% despite urgent request rise), EX-16 (6 org interns adopted; outcome fed to HR+University team), EX-19 (2-day fulltime fix, 0 prod impact, core is cross-team trust/attribution), EX-20 (~6h delay blocking 2 launches, 2x RCA to Head of Engineering + implicit-coupling cleanup + factor/model migration). Updated task descriptions T-P0-380/381/382/383 to embed these. For EX-22/28/33 (no facts given), updated descriptions to instruct autonomous sessions to use `[TODO: confirm number]` placeholders rather than fabricate. Also updated T-P1-387 metric sweep with the same placeholder rule (never invent numbers). Awaiting user launch confirmation.
- **Deliverables**: 7 task descriptions updated in .claude/tasks.db (T-P0-380..386 + T-P1-387)
- **Sanity check result**: Each task_db.py update returned ok:true; placeholder rule explicit in descriptions so autonomous sessions produce fillable slots instead of fabrications.
- **Status**: [DONE] enrichment phase. Awaiting user launch.
- **Request**: No further task_db change; ready for autonomous_run.ps1 10.

## 2026-04-13 -- Audit ID mismatch discovered + context-gathering for remaining 3 BQ rework tasks
- **What I did**: Pulled current content of EX-22/28/33 target stories to identify specific number slots needed. Discovered the 2026-04-13 audit used sequential numbering that doesn't match the JSON's EX-NN IDs: audit's "EX-22 Pushback on Scope" = JSON EX-18, audit's "EX-28 VP Allocation" = JSON EX-24. Also discovered audit's "EX-33 MoE -> Allocation Paradigm Shift" has NO corresponding story in either docs/bq_behavioral_examples.json or docs/bq_improved_stories.md -- may be a planned/unwritten story or an audit mis-label. Drafted 9 specific context questions (Q1-Q9) across the 3 stories and sent to user on Discord: burnout duration + eng-time use post-descope + brief self-reflection for EX-18; avoided cost estimate + follow-through for allocation framing + tangible VP-meeting deliverable for EX-24; existence check + file location + decision on skip/create for audit's missing EX-33.
- **Deliverables**: No file changes; Discord questions sent as 2 parts.
- **Sanity check result**: Confirmed via JSON scan that EX-18 = Pushback-on-Scope and EX-24 = VP-Allocation; confirmed via keyword grep that "MoE" and "paradigm shift" are absent from both BQ files.
- **Status**: [BLOCKED] on user answering Q1-Q9 before autonomous launch. Any answer subset is workable.
- **Request**: No task_db update; 3 task descriptions still carry `[TODO: confirm number]` placeholder rule as fallback.

## 2026-04-13 -- MoE story mystery solved + 3 Tier-1 tasks finalized + autonomous launched
- **What I did**: Used user's context answers (1 month 10h/day burnout, contextualized-embedding delivery, first-quarter-rotation reflection; 2-3 weeks avoided combo-launch waste, top-10/top-30 distribution analysis, allocation framing adoption; MoE story exists keyword hint). Discovered EX-33 MoE story lives in DB behavioral_examples table only, not the JSON file -- was populated via scripts/_populate_hash_and_moe_examples.py on 2026-04-11. Further discovered the audit's claim "EX-33 has no business metric" was wrong: the Result field already includes 200M annualized GMB from subsequent allocation policy, just buried. Updated T-P0-384/385/386 task descriptions with user facts + the lead-with-existing-200M-GMB guidance for EX-33. Launched autonomous_run.ps1 with 10 max sessions via background powershell subprocess (background task id: bbpyn2fin).
- **Deliverables**: 3 task_db descriptions finalized (T-P0-384/385/386); autonomous runner launched in background
- **Sanity check result**: Each task_db update returned ok:true; background task ID returned cleanly (output file in tasks/ dir). Runner using proven PowerShell path (2026-04-11 SIGPIPE fix effective).
- **Status**: [DONE] planning + launch. Execution in flight.
- **Request**: No direct task_db update from this session; child sessions will mark their own tasks completed.

## 2026-04-13 -- [T-P0-380] EX-12 Code Review Standards: add concrete metric
- **What I did**: Reworked COL-2 story in docs/bq_improved_stories.md with user-provided metric (80% -> 50% custom-deployment rate, even as urgent-request volume rose). Converted passive "we agreed / team aligned" framing into active "I proposed the shared checklist / I documented the tradeoff". Mirrored the same situation/task/action/result into the JSON BLOG-02 entry (which previously had only cross-refs and tags).
- **Deliverables**: docs/bq_improved_stories.md (COL-2 rewrite), docs/bq_behavioral_examples.json (BLOG-02 populated with full STAR).
- **Sanity check result**: JSON parses cleanly (python json.load). Metric leads the Result line. Action bullets start with "I".
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-380 --status completed`

## 2026-04-13 -- Orchestrator bailed early; fixed sticky all_done flag and relaunched
- **What I did**: First launch of autonomous_run.ps1 for BQ rework batch (10 tasks) only completed T-P0-380 (EX-12 Code Review, commit 5ae75cf with "80% -> 50% bypass rate" metric) before bailing with "all_done=true -- all tasks complete!" despite 9 active tasks remaining. Root caused: previous Pinterest batch left session_state.json all_done=true and child sessions don't auto-reset when new tasks enter backlog. Manually reset all_done=false; relaunched autonomous_run.ps1 10 (background task id: btnkr4dn8). Documented the sticky-flag pattern + detection tip + fix procedure in LESSONS.md.
- **Deliverables**: .claude/session_state.json (all_done=false, last_status=reset_for_new_batch); 1 completed task (T-P0-380 committed 5ae75cf); LESSONS.md appended
- **Sanity check result**: task_db still shows 9 active; session_state rewritten and verified; relaunch accepted (background task id confirmed).
- **Status**: [PARTIAL] -- 1/10 done, 9 in flight.
- **Request**: No direct task_db update from this session; in-flight child sessions handle their own.

## 2026-04-13 -- [T-P0-381] EX-12 PhD Interns Notebook-to-Production: add onboarding metric
- **What I did**: Reworked EX-12 (Story 12) in bq_improved_stories.md and bq_behavioral_examples.json per user-provided facts from 2026-04-13 Discord. Result now leads with "6 interns across my org adopted the checklist; outcome cited by HR + University partnership team for academic-to-industry onboarding program iteration". Converted passive "we/team" framing in Action to active first-person: "I built the checklist/template", "I ran the first review pass", "I briefed HR on the outcome". Added specific diffusion detail ("once the first two shipped, the rest self-adopted") to strengthen the ownership narrative.
- **Deliverables**: docs/bq_improved_stories.md (STORY 12 rewrite), docs/bq_behavioral_examples.json (EX-12 action + result).
- **Sanity check result**: JSON parses cleanly (json.load). Result line leads with the concrete "6 interns" metric. All Action bullets start with "I".
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-381 --status completed`

## 2026-04-13 -- [T-P0-382] EX-15/Story 15 Model Deprecation Incident: own the gap personally
- **What I did**: Reworked STORY 15 / EX-15 Model Deprecation Incident in bq_improved_stories.md and bq_behavioral_examples.json per user-provided facts from 2026-04-13 Discord. Replaced the vague "one week on redeployment" framing with concrete "2-day fix turnaround, zero user-facing production impact, cross-team trust fully restored" metric. Added explicit self-ownership of the gap ("I should have checked downstream consumer Slack channels before deprecating") instead of the prior defensive-then-constructive arc. Added the post-mortem attribution norm as an explicit deliverable of the incident response. (Task title labels this as "EX-19" but the Model Deprecation content lives at EX-15/STORY 15 in the current files.)
- **Deliverables**: docs/bq_improved_stories.md (STORY 15 Action + Result rewrite), docs/bq_behavioral_examples.json (EX-15 action + result).
- **Sanity check result**: JSON parses cleanly (json.load). Result leads with the "2-day / zero user-facing impact / cross-team trust restored" triple. Action opens with personal ownership ("I should have checked downstream consumer Slack channels").
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-382 --status completed`

## 2026-04-13 -- [T-P0-383] EX-16/STORY 16 Cross-DC Deployment Incident: quantify blast radius
- **What I did**: Reworked STORY 16 / EX-16 Cross-Datacenter Deployment Incident in bq_improved_stories.md and bq_behavioral_examples.json per 2026-04-13 Discord facts. Replaced "quickly stabilized / preprod delay" framing with concrete blast radius + MTTR: "6-hour deployment delay blocking 2 dependent launches; RCA presented to Head of Engineering twice; follow-up cleanup of additional implicit-coupling sites; science-team factor/model migration to declarative artifactory". Sharpened personal contribution vs backend team (I owned diagnosis/coordination/architectural fix; backend team handled rollback mechanics). Added the "called in twice" detail and the pressure framing. (Task title labels this as EX-20, but the Cross-DC content lives at EX-16/STORY 16 in the current files; the prior T-P0-382 had the same label/content offset.)
- **Deliverables**: docs/bq_improved_stories.md (STORY 16 Action + Result rewrite), docs/bq_behavioral_examples.json (EX-16 action + result).
- **Sanity check result**: JSON parses cleanly (json.load). Result leads with "6-hour deployment delay blocking 2 dependent launches; presented RCA to Head of Engineering twice; drove follow-up cleanup...". Action explicitly separates my scope from backend team's rollback mechanics.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-383 --status completed`

## 2026-04-13 -- [T-P0-384] EX-18 Pushback on Scope: add delivery-impact metric
- **What I did**: Reworked STORY 18 / EX-18 "Pushing Back on Unreasonable Scope" across docs/bq_improved_stories.md, docs/bq_behavioral_examples.json, and the behavioral_examples DB row (example_id=EX-18) per 2026-04-13 Discord facts. Replaced passive "leadership accepted" framing with active "I delivered a pros/cons + resource/timeline analysis that let leaders converge". Added concrete delivery-impact metric: freed capacity was redeployed to ship a new contextualized embedding feature and a larger ranking model (moved business metrics) rather than a speculative multi-stack infrastructure bet. Quantified burnout (~1 month intermittent 10h/day). Closed with first-quarter-after-rotation self-reflection line about over-indexing on proving I could deliver.
- **Deliverables**: docs/bq_improved_stories.md (STORY 18 Action + Result + new Self-reflection paragraph), docs/bq_behavioral_examples.json (EX-18 action + result), data/mle_prep.db (behavioral_examples.action + result for example_id=EX-18).
- **Sanity check result**: JSON parses cleanly (json.load). DB row updated (action 722 chars, result 844 chars). All three surfaces now say "delivered analysis that drove leaders to converge" (active voice) and name the freed-capacity downstream wins (contextualized embedding + larger model).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-384 --status completed`

## 2026-04-13 -- [T-P0-385] EX-24 Allocation-to-VP: add avoided-cost metric + top-10/30 deliverable
- **What I did**: Reworked STORY 24 / EX-24 "Explaining Allocation Problem to VP" across docs/bq_improved_stories.md, docs/bq_behavioral_examples.json, and data/mle_prep.db (behavioral_examples row, example_id=EX-24) per 2026-04-13 Discord facts (Q4/Q5/Q6). Added a concrete tangible deliverable in Action: top-10 and top-30 slot-distribution analysis framed as "bias toward ONE priority -- slots are a finite resource". Led the Result with the avoided-cost estimate (~2-3 weeks of debugging + reverse-test collection saved). Replaced passive "VP accepted" with "VP adopted the slot-as-finite-resource framing" + follow-through reasons (near-real-time deployment, authenticity, long-term business value, C2C-strategy fit).
- **Deliverables**: docs/bq_improved_stories.md (STORY 24 Action + Result), docs/bq_behavioral_examples.json (EX-24 action/result/evidence_quotes), data/mle_prep.db (behavioral_examples row for EX-24), scripts/_update_ex24_allocation_vp.py.
- **Sanity check result**: JSON parses; EX-24 row now has action=842 chars, result=621 chars. Verified "2-3 weeks", "top-10", and "finite resource" all present in the updated JSON record. Markdown story leads Result with avoided-cost figure.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-385 --status completed`

## 2026-04-13 -- [T-P0-386] EX-33 MoE Paradigm Shift: lead Result with 200M GMB downstream
- **What I did**: Reworked DB `behavioral_examples` row example_id=EX-33 (DB-only story, no JSON match) per T-P0-386. Result now leads with "200M+ in annualized GMB" as the downstream receipt of the paradigm reframe, while keeping the honest-negative-result framing (MoE deprecated, did not ship). Added concrete downstream initiatives list (authenticated listings, C2C new listings, diversity framework reuse) as adoption evidence. Sharpened Action (1) from "my manager and I labeled" -> "I labeled (my manager signed off, but the framing was mine to propose and own)" to remove "we" ambiguity and show ownership. Also added STORY 33 section to docs/bq_improved_stories.md before the COL-1..COL-4 block.
- **Deliverables**: data/mle_prep.db (EX-33 action + result rewritten), docs/bq_improved_stories.md (+STORY 33 section), scripts/_rework_ex33_moe_paradigm.py.
- **Sanity check result**: DB update touched exactly 1 row; action=2293 chars, result=988 chars. Verified "200M" appears at position 83 in Result (lead sentence). STORY 33 inserted before "## EXISTING ANSWERS" anchor (idempotent guard included).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-386 --status completed`

## 2026-04-13 -- Pinterest expansion planning: 24 tasks for new LC/custom/SD/BQ/integration
- **What I did**: User shared a 2025-11 Pinterest interview dump (LC problems, custom coding, system designs, BQ questions) with request to plan via task planning mode, expand explanations, and link LC <-> SD back to prep notes. Planned 24 tasks via task_db.py batch (not executed): 7 new LC problems (84/392/3229/1526/1564/1580 + restaurant-interval investigation), 8 Pinterest-specific custom coding (Escape Room, Lighthouse, Prefix-match, Grant Access, Pin Connectivity, round-from-scratch, round-by-precision, LC332 loop follow-up), 7 system designs (Pins Search/Notification/Pin Ranking/Ad CTR/Embeddings/Catalog bulk update/Chat bot), 1 BQ mapping, 1 integration. Added 11 dependencies on T-P2-413 integration task. Regenerated TASKS.md.
- **Deliverables**: scripts/_plan_pinterest_expansion_tasks.py (batch script); .claude/tasks.db (24 new tasks T-P1-390..T-P2-413 with deps); TASKS.md regenerated
- **Sanity check result**: Batch returned 24 ok:true ids; all 11 depend commands succeeded; project confirmed regen.
- **Status**: [DONE] planning. Awaiting user review + current BQ rework batch completion before launch.
- **Request**: No further task_db changes until user reviews; BQ rework (bg id btnkr4dn8) still in flight (session 6/10).

## 2026-04-13 -- [T-P0-397] Pinterest Escape Room custom problem seeded
- **What I did**: Added Pinterest 2025-11 "Escape Room Game State" non-LC problem to mle_prep.db (id=1068). Canonical design: per-room doubly-linked list + global pid->Node map, giving O(1) proceedToNextRoom, O(1)+O(k) getPeople, O(R+K) getTop. Notes include Python impl (Game/_DLL/_Node), complexity table, edge cases, 中文 解析 with follow-up extensions (per-person skip sequences, O(K) getTop via non-empty-rooms DLL), and self-test.
- **Deliverables**: scripts/_add_pinterest_escape_room.py (idempotent seed); data/mle_prep.db row id=1068 (desc=937 chars, notes=6607 chars, company_tags=["Pinterest"]).
- **Sanity check result**: Smoke test of the NOTES code path (Game([1,2,3],[10,20,30])) passed all assertions incl. getTop tiebreak by entry order and final-room no-op guard. DB verified via SELECT.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-397 --status completed`

## 2026-04-13 -- [T-P0-405] Pinterest SD: Pins Search Engine
- **What I did**: Authored end-to-end ML SD doc for Pinterest Pins Search at docs/pinterest/system_design_pins_search.md. Covers 12 sections: clarifying questions, 4-stage funnel diagram, query understanding (normalization/NER/intent/embedding cache), candidate generation (multi-source retrieval, two-tower + InfoNCE with hard negatives, HNSW/PQ, online fresh index), ranking (L1 GBDT LambdaRank + L2 MMoE multi-task DNN with CTR/Repin/CloseUp/Hide heads), re-ranking (MMR diversity, freshness boost, policy/ads blending), offline metrics (NDCG/MAP/Recall@K), online metrics + A/B (repin-rate north star), infra (feature store, training pipeline, serving stack, capacity math for 100K QPS / 5B pins), cold-start (pin/user/query), failure modes, 7 likely follow-ups, and 45-min timing template.
- **Deliverables**: docs/pinterest/system_design_pins_search.md (376 lines, 14.4KB, 13 H2 sections).
- **Sanity check result**: File written UTF-8, structural check passed (title present, 13 ## sections).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-405 --status completed`

## 2026-04-13 -- [T-P0-406] Pinterest SD: Notification Recommendation
- **What I did**: Authored end-to-end ML SD doc for Pinterest notification reco at docs/pinterest/system_design_notification_reco.md. 12 sections covering: clarifying (scale/channel/goal/constraints), high-level pipeline (event+batch triggering -> CG -> rank -> delivery), triggering layer (event-driven vs scheduled, send/skip pCTR gate, budget/pacing via Lagrangian), content CG (two-tower for re-engagement, submodular selection for digest), 2-stage ranking (L1 GBDT + L2 MMoE with pOpen/pClick/pRepin/pDisable/pUnsub heads, long-term value head for counterfactual session uplift), delivery constraint layer (freq cap, quiet hours, channel fallback, dedup, GDPR), offline metrics (AUC/ECE/counterfactual), online metrics + A/B with WAU north star and 1% holdout, infra+capacity (35K QPS ranking), cold start, failure modes, 7 follow-ups, 45-min timing, and an appendix contrasting push vs pull products.
- **Deliverables**: docs/pinterest/system_design_notification_reco.md (300 lines, 14.8KB, 14 H2 sections).
- **Sanity check result**: File written UTF-8, 14 ## sections, no emoji, structural check passed.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-406 --status completed`

## 2026-04-13 -- [T-P0-407] Pinterest SD: Pin Ranking for Home/Topic Feed
- **What I did**: Authored end-to-end ML SD doc for Pinterest home-feed pin ranking at docs/pinterest/system_design_pin_ranking.md. 14 sections: clarifying (surface/scale/latency/objective), high-level architecture (retrieval -> L1 -> L2 MMOE -> blending -> business rules), multi-source retrieval (PinSage ANN + board/topic follow + co-pin + trending + creator fresh), feature families (pin/user/context/cross) with feature-store consistency notes, model family contrasting MMOE+DCN-v2 vs W&D vs HSTU-style generative ranker, multi-objective optimization (Pareto weight tuning, Lagrangian constraint, MMR diversity, counterfactual LTV head), serving (400ms E2E budget breakdown, ~300 GPU capacity estimate, graceful degradation), metric ladder (offline AUC/NDCG/ECE/IPS uplift, online north-star WAU+session+repin with guardrails), cold start (new-user/new-pin/dormant), failure modes (filter bubble/clickbait/creator-matthew/position-bias), 7 follow-up hooks, 45-min timing cheat sheet, and two appendices (home vs related vs search; key numbers).
- **Deliverables**: docs/pinterest/system_design_pin_ranking.md (370 lines, 14 H2 sections).
- **Sanity check result**: File written UTF-8, 14 ## sections, zero emoji/symbol chars, structural check passed.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-407 --status completed`

## 2026-04-13 -- BQ rework batch 1 complete (11 tasks) + Pinterest expansion launched (23 remaining)
- **What I did**: First autonomous batch completed 11 tasks (orchestrator ran into Pinterest P0s after BQ P0s since same priority): T-P0-380..386 (all 7 BQ P0 rework) + T-P0-397 (Escape Room) + T-P0-405/406/407 (Pinterest SD Pins Search/Notification/Pin Ranking). Commits 5ae75cf through 7b7d3c2. session_state.json was correctly maintained this time (all_done=false, last_task=T-P0-407) so no reset needed. Launched second autonomous batch for remaining 23 tasks: 3 BQ P1 sweeps (387/388/389), 1 Pinterest P0 (410 Catalog bulk update), 19 Pinterest P1/P2 (390-413 minus those already done). Background id: bgjp3psy4. T-P2-413 integration task gated on 11 deps, will run last.
- **Deliverables**: 11 commits in batch 1; batch 2 running via background PowerShell; task_db reflects batch 1 completions
- **Sanity check result**: logs/autonomous.log shows batch 1 exited cleanly with "Finished after 10 session(s)" (one of the 10 sessions accepted 2 tasks since both were same priority and quickly completable); session_state.json updated correctly this time indicating the fixed state from earlier reset.
- **Status**: [PARTIAL] batch 2 in flight; will report when completed.
- **Request**: No direct task_db update; child sessions handle their own status transitions.

## 2026-04-13 -- [T-P0-410] Pinterest SD: Catalog bulk update (500M records, S3+async)
- **What I did**: Authored end-to-end infra SD doc for catalog bulk update at docs/pinterest/system_design_catalog_bulk_update.md. 14 H2 sections covering clarifying (scale/freq/sources/downstream/consistency), high-level arch (S3 raw -> coordinator -> Spark partition workers -> Kafka single-topic -> 7 consumer groups + DLQ), ingestion (why S3 over sync API / quick-async / Kafka-direct, manifest protocol with _SUCCESS/sha256), partitioning (range vs hash vs consistent-hash, hash-mod-500 with 1M rows/part aligned to 1GB S3 parts, why Kafka needs consistent-hash-by-catalog_id for FIFO), retry (partition-level with Airflow meta DB checkpoint, at-least-once + version-based idempotency, 3-class DLQ routing), fan-out (single topic with 200 partitions replication=3, backpressure at producer/broker/consumer layers, Avro schema registry BACKWARD compat), monitoring (4 metric categories with thresholds + RPO=1d/RTO=2h), 4 key tradeoffs (sync/async, exactly-once/at-least-once, partition strategy, single-vs-per-consumer topic), 8 failure modes with mitigations, capacity planning (~$3.8K/mo), 7 follow-ups (delta upsert / multi-region / GDPR / schema upgrade / point-in-time / big seller / slow consumer), 45-min timing cheat sheet, and two appendices (three API styles, key numbers).
- **Deliverables**: docs/pinterest/system_design_catalog_bulk_update.md (422 lines, 14 H2 sections)
- **Sanity check result**: File UTF-8, 14 H2 sections, zero emoji chars (checked 0x2600-0x27BF and 0x1F000-0x1FFFF ranges), structural check passed
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-410 --status completed`

## 2026-04-13 -- [T-P1-390] Pinterest LC 84 Largest Rectangle: Pinterest tag + expanded Chinese notes
- **What I did**: Tagged LC 84 with Pinterest company tag and overwrote problems.notes (id=85) with a full 4874-char Chinese study note covering (1) monotonic-stack O(n) canonical with sentinel + equivalent "append 0" variant, (2) divide-and-conquer O(n log n) avg / O(n^2) worst, (3) two-pass left/right precompute variant, (4) relation table to LC 85/42/11/496/907, (5) 单调栈 pattern-recognition checklist, (6) traps (strict vs non-strict pop, clear-stack step, empty array, recursion limit), and a 45s interview opener.
- **Deliverables**: scripts/_update_lc84_pinterest_notes.py (new, one-shot idempotent), data/mle_prep.db (LC 84 row: company_tags +Pinterest, notes replaced)
- **Sanity check result**: Script ran [OK], tags now ["LinkedIn","Uber","Adobe","Pinterest"], notes_len=4874; also verified canonical solution against 4 test cases including [2,1,5,6,2,3]=10, [5,5,5]=15, []=0.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-390 --status completed` (already applied)


## 2026-04-13 -- [T-P1-391] Pinterest LC 392 Is Subsequence: Pinterest tag + Chinese notes
- **What I did**: Tagged LC 392 with Pinterest and overwrote notes (id=417) with a 4392-char Chinese study note covering (1) double-pointer O(n+m) with greedy correctness argument, (2) follow-up multi-query: bisect on per-char index lists O(n log m), (3) next-DP table O(m*26) preprocessing + O(n) query, (4) method selection table by k/charset size, (5) cross-links to LC 1055/524/792/115/1143, (6) traps (off-by-one in bisect, empty-string edge cases, sentinel in next table).
- **Deliverables**: scripts/_update_lc392_pinterest_notes.py (new, one-shot idempotent), data/mle_prep.db (LC 392 row: +Pinterest tag, notes replaced)
- **Sanity check result**: Script ran [OK], tags now ["LinkedIn","Uber","Adobe","Pinterest"], notes_len=4392; verified all three solutions against 5 test cases (including empty s, empty t, full match).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-391 --status completed` (already applied)

## 2026-04-13 -- [T-P1-392] Pinterest LC 3229 Min Operations to Make Array Equal to Target: tag + Chinese notes
- **What I did**: Tagged LC 3229 with Pinterest and overwrote notes (id=157) with a 3641-char Chinese study note covering (1) the diff-scan greedy d[i]=target[i]-nums[i] single-pass formulation, (2) correctness via "LC1526(max(d,0)) + LC1526(max(-d,0))" decomposition, (3) two traced examples, (4) cross-links to LC 1526/370/798/1109/2772, (5) edge cases (prev=0 seed, cross-zero non-merging, monotonic descending), (6) 45-sec pitch.
- **Deliverables**: scripts/_update_lc3229_pinterest_notes.py (new, idempotent), data/mle_prep.db (LC 3229: +Pinterest tag, notes replaced 564 -> 3641 chars)
- **Sanity check result**: Script ran [OK]; tags=["Pinterest"], notes_len=3641; verified algorithm against 4 test cases (mixed-sign, all-zero, ascending, equal).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-392 --status completed`

## 2026-04-13 -- [T-P1-393] Pinterest LC 1526 Min Increments on Subarrays: tag + Chinese notes
- **What I did**: Tagged LC 1526 with Pinterest and wrote notes (id=236) with a 3349-char Chinese study note covering (1) the O(n) upper-edge counting formula `ans = target[0] + sum(max(0, t[i]-t[i-1]))`, (2) correctness via diff-array lower bound argument (each op contributes one +1 rise), (3) two traced examples, (4) cross-links to LC 3229/370/1109/798/2772/1564, (5) edge cases (single peak, plateau, monotonic, multi-peak), (6) 45-sec pitch positioning as the single-sided version of LC 3229.
- **Deliverables**: scripts/_update_lc1526_pinterest_notes.py (new, idempotent), data/mle_prep.db (LC 1526: +Pinterest tag, notes 0 -> 3349 chars)
- **Sanity check result**: Script ran [OK]; tags=[LinkedIn, Uber, Adobe, Pinterest], notes_len=3349; verified algorithm against 3 test cases ([1,2,3,2,1]=3, [3,1,1,2]=4, [3,1,5,4,2]=7).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-393 --status completed`

## 2026-04-13 -- [T-P1-394] Pinterest LC 1564 Put Boxes Into Warehouse I: insert + Chinese notes
- **What I did**: Inserted new problem row for LC 1564 (not previously in DB) with Pinterest tag and a 4275-char Chinese study note covering (1) prefix-min "effective height" reduction, (2) greedy with sorted boxes + reverse-sweep of rooms (skip room, not box, when minimum box cannot fit), (3) exchange-argument correctness proof, (4) two traced examples, (5) contrast table vs LC 1580 (single vs dual entrance), (6) cross-links to LC 11/42/881/1580/2064, (7) edge cases (m != n, duplicate heights, all-too-big), (8) 45-sec pitch.
- **Deliverables**: scripts/_update_lc1564_pinterest_notes.py (new, idempotent), data/mle_prep.db (LC 1564: newly inserted, notes_len=4275)
- **Sanity check result**: Script ran [NEW]; verified greedy against 4 test cases ([4,3,4,1]/[5,3,3,4,1]=3; [1,2,2,3,4]/[3,4,1,2]=3; [1,2,3]/[1,2,3,4]=1; [3,5,5,2]/[2,1,3,4,5]=1).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-394 --status completed` (already applied)

## 2026-04-13 -- [T-P1-395] Pinterest LC 1580 Put Boxes Into Warehouse II: insert + Chinese notes
- **What I did**: Inserted new problem row for LC 1580 (hard, harder variant of 1564 with dual entrance) tagged Pinterest, with a 4720-char Chinese study note covering (1) bidirectional prefix-min "upper envelope" eff[j] = max(leftMin[j], rightMin[j]) reduction, (2) why eff loses monotonicity vs 1564 and therefore requires sorting eff, (3) double-sort + two-pointer greedy (skip room, never box) with worked code, (4) exchange-argument correctness sketch, (5) two traced examples, (6) contrast table vs LC 1564, (7) cross-links LC 1564/42/11/881/1705, (8) edge cases (eff-as-max-not-min trap, n=1, all-too-big), (9) 45-sec pitch.
- **Deliverables**: scripts/_update_lc1580_pinterest_notes.py (new, idempotent), data/mle_prep.db (LC 1580: newly inserted, notes_len=4720)
- **Sanity check result**: Script ran [NEW]; verified greedy against 5 test cases ([1,2,2,3,4]/[3,4,1,2]=4; [3,5,5,2]/[2,1,3,4,5]=3; [1,2,3]/[1,2,3,4]=3; [4,5,6]/[1,1,1]=0; [9,5,5,2,3,1]/[1,2,3,4,5]=4).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-395 --status completed`

## 2026-04-13 -- [T-P1-387] BQ Tier-2 metric sweep: add [TODO: confirm] placeholders (no fabricated numbers)
- **What I did**: Did a bounded metric-sweep pass on `docs/bq_improved_stories.md` for the 9 target stories that actually exist (EX-01, EX-04, EX-14, EX-15, EX-17, EX-21, EX-23, EX-24 -- EX-18 deliberately left unchanged, see below). Added 10 inline `[TODO: confirm ...]` placeholders in Result sections, each naming a specific missing number (initial A/B lift %, OKR quarter, labels/day throughput, # adopting teams, quarterly ticket-backlog, joint on-call rotations, review-restart-free PRs, invalid-A/B traffic %, slot-allocation FP-rate delta). Added a sweep-header section at top of MD explaining what Pass 1 did and flagging two open questions for the user: (a) the "18K labels/day at $500, 1.5% GMB" numbers the task ascribed to EX-18 actually match EX-14 LLM-as-Judge context -- wrote them into EX-14 behind [TODO: confirm] rather than into EX-18; (b) EX-29/EX-35/EX-36 do not exist in the canonical files (IDs stop at EX-24 plus EX-33), so cannot sweep. JSON mirror (`bq_behavioral_examples.json`) intentionally NOT touched yet -- will sync after user disambiguates EX-18 assignment and EX-29/35/36 identity.
- **Deliverables**: docs/bq_improved_stories.md (10 [TODO: confirm] markers + sweep header with open questions)
- **Sanity check result**: `grep -c "TODO: confirm" docs/bq_improved_stories.md` -> 10 markers present. No numbers fabricated. EX-18 original Result preserved verbatim pending user confirmation.
- **Status**: [PARTIAL] -- Pass 1 complete for the 9 existing stories. Remaining work: (1) user confirms EX-18 vs EX-14 number assignment, (2) user clarifies EX-29/35/36 -> real story IDs, (3) sync confirmed numbers into `docs/bq_behavioral_examples.json`, (4) then remove [TODO: confirm] markers as each is answered.
- **Request**: `task_db.py update T-P1-387 --status completed` (already done); open a follow-up task once EX-18 / EX-29 / EX-35 / EX-36 identities are clarified to do Pass 2 (JSON sync + placeholder resolution).

## 2026-04-13 -- [T-P1-388] BQ Tier-2 ownership sharpening: "we" -> "I" in Action sections (EX-02/11/13)
- **What I did**: Swept Action and Result sections in EX-02, EX-11, EX-13 across both `docs/bq_improved_stories.md` and `docs/bq_behavioral_examples.json` to make ownership unambiguous. Every Action bullet now explicitly starts with "I" (or credits the correct actor, e.g. "My intern prepared... at my direction"). Added specific ownership phrasing from task spec: EX-02 result front-loads "I led the first experiment to a +1% GMB lift"; EX-11 calls out the compression/context split ("I led compression into a leader-readable format; the researcher side gave me context"); EX-13 names the flag/point/air-cover split ("I flagged... I took point on negotiations... my manager gave air cover"). "We" preserved only in Situation sections (team context). Added a sweep-header section to the MD documenting this pass.
- **Deliverables**: docs/bq_improved_stories.md (EX-02/11/13 Action rewrites + sweep header), docs/bq_behavioral_examples.json (EX-02 result, EX-11 action, EX-13 action+result)
- **Sanity check result**: `python -c "import json; json.load(open('docs/bq_behavioral_examples.json', encoding='utf-8'))"` -> JSON OK. No numbers fabricated.
- **Status**: [PARTIAL] -- EX-02/11/13 complete. EX-25, EX-26, EX-27 (mentioned in task spec) do not exist in canonical files (IDs stop at EX-24 + EX-33). Flagged in the MD sweep header for user to disambiguate (same disposition as T-P1-387 EX-29/35/36 open questions).
- **Request**: `task_db.py update T-P1-388 --status completed`; follow-up pass can apply the same ownership sharpening to EX-25/26/27 once user clarifies which canonical IDs those refer to.

## 2026-04-13 -- [T-P1-389] BQ Tier-2 catch-all polish: EX-07 downstream metric placeholder
- **What I did**: EX-07 (relevance dataset bias / self-fulfilling prophecy) Result previously ended on a process outcome with no downstream signal. Added a `[TODO: confirm downstream metric delta after dataset reformulation -- e.g., NDCG lift / relevance precision gain / abandonment-rate drop, with baseline quarter]` placeholder to both `docs/bq_improved_stories.md` and `docs/bq_behavioral_examples.json` so the two stay in sync. Added a T-P1-389 sweep header to the MD. Scanned the rest of the Tier-2 stories for gaps not already covered by T-P1-387 (metric sweep) or T-P1-388 (ownership sweep); no additional structural gaps found outside the already-tracked EX-29/35/36 and EX-25/26/27 open-ID questions.
- **Deliverables**: docs/bq_improved_stories.md (EX-07 Result + T-P1-389 sweep header), docs/bq_behavioral_examples.json (EX-07 result mirrored)
- **Sanity check result**: `python -c "import json; json.load(open('docs/bq_behavioral_examples.json', encoding='utf-8'))"` -> JSON OK. No numbers fabricated -- placeholder only.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-389 --status completed`

## 2026-04-13 -- [T-P1-398] Pinterest Lighthouse 2D light-propagation custom problem
- **What I did**: Picked the ray-tracing variant (beam + mirrors `/` `\` + splitters `|` `-`, akin to AoC 2023 Day 16) as the canonical interpretation of the 2025-11 dump entry. Wrote an idempotent seeder `scripts/_add_pinterest_lighthouse.py` that inserts a non-LC problem into `data/mle_prep.db` with Python implementation, complexity analysis, English + Chinese notes, mirror-transform formulas, a "variant map" so an interviewer's alternate phrasing (radius coverage / cycle detection / multi-lighthouse overlay) can be remapped onto the same file, and three verified smoke tests.
- **Deliverables**: scripts/_add_pinterest_lighthouse.py (new), scripts/_smoke_lighthouse.py (new, standalone BFS verifier), data/mle_prep.db (new row id=1071, title "Lighthouse 2D Light Propagation").
- **Sanity check result**: `python scripts/_smoke_lighthouse.py` -> OK all 3 smoke tests passed (straight beam, `/` reflection, `|` split). `python scripts/_add_pinterest_lighthouse.py` -> `[INSERT] id=1071`. Self-test in the notes was cross-validated against the live BFS before committing.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-398 --status completed`

## 2026-04-13 -- [T-P1-399] Pinterest Prefix-Match First-Word-Index custom problem
- **What I did**: Added a non-LC Pinterest-tag problem to `data/mle_prep.db` covering the 2025-11 prefix-first-index prompt. Notes carry two canonical solutions (Trie with `min_index` updated on every node of the insertion path + bisect_left on sorted input with an explicit startswith verification), English + Chinese explanations, complexity table, edge cases (empty prefix, bisect-lands-on-non-match trap), and follow-ups (all matches / streaming inserts / many queries).
- **Deliverables**: scripts/_add_pinterest_prefix_first_index.py (new, idempotent seeder), scripts/_smoke_prefix_first_index.py (new, standalone verifier), data/mle_prep.db (new row id=1072).
- **Sanity check result**: `python scripts/_smoke_prefix_first_index.py` -> OK all smoke tests passed (Trie/bisect parity on sorted input, unsorted-only Trie cases, empty-prefix, and the bisect-lands-on-'az'-for-prefix-'ap' trap). Seeder -> `[INSERT] id=1072`.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-399 --status completed`

## 2026-04-13 -- [T-P1-402] Pinterest round()-from-scratch custom problem
- **What I did**: Added a non-LC Pinterest-tag problem to `data/mle_prep.db` for the 2025-11 "implement round() on a decimal string without using float()" prompt. Notes contain the canonical 4-segment state-machine parser (whitespace/sign/int/dot/frac), half-up carry propagation, English + Chinese explanations, a why-not-float() section (overflow + `2.675` binary artefact), and an edge-case matrix including `'-.2'`, `'2.'`, `'9.5' -> 10`, `'99.5' -> 100`, explicit `+` sign, and `ValueError` cases (`''`, `'.'`, `'1.2.3'`, `'1e2'`).
- **Deliverables**: scripts/_add_pinterest_round_from_scratch.py (new, idempotent seeder), scripts/_smoke_round_from_scratch.py (new, standalone verifier), data/mle_prep.db (new row id=1073).
- **Sanity check result**: `python scripts/_smoke_round_from_scratch.py` -> OK 20 valid + 9 invalid cases passed (including 400-digit input that would overflow float()). Seeder -> `[INSERT] id=1073`; second run -> `[SKIP]` (idempotent).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-402 --status completed`
