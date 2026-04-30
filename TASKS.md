# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-582: [BQ-DEPTH-11] Bulk probe_notes for remaining ~36 high-probability questions
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-581
- **Description**: After calibration samples (BQ-DEPTH-09) approved + primary flags set (BQ-DEPTH-10), write probe_notes for the remaining 36 questions in the top 40.

Split into 3-4 sub-batches of ~10 each, each a separate autonomous session per feedback_always_auto_run. Between batches, user spot-check one probe_notes entry to catch style drift early.

Content rules (locked by BQ-DEPTH-09 calibration):
- 中文叙述 + 英文术语
- All 4 schema fields required (core_signal, what_good_looks_like, what_L5_adds, common_failure_modes)
- Reference the is_primary story in what_good_looks_like
- No angle_label -- angle lives in prose

Deliverables:
- scripts/seed_bq_probe_notes_batch{1-4}_20260421.py -- each idempotent + DB-backup-guarded
- After each batch: spot-check doc attached to Discord for user review

AC:
- All 40 top questions have probe_notes set
- Each batch script re-runs with [SKIP]
- No schema field empty; all 4 structured fields populated for every question
- User spot-check passed between batches

#### T-P1-583: [BQ-DEPTH-12] Frontend Phase D: primary-story prominent card + probe_notes expandable panel
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-581
- **Description**: src/frontend/src/pages/BehavioralQuestions.tsx redesign.

Journey-first AC (from CLAUDE.md planning rules): user opens /behavioral -> clicks expand on a top-40 question -> sees ONE gold-bordered primary story card (big, with full relevance_note + STAR Situation preview + 'use this angle' hint) -> sees 'Also applies' collapsed panel with 2-3 backup stories -> clicks 'What this question probes' -> sees 4-section probe_notes panel (core_signal / what_good_looks_like / what_L5_adds / common_failure_modes).

Scenario matrix:
- Question has is_primary link + probe_notes -> full new treatment
- Question has is_primary link + no probe_notes -> primary card only, probe panel hidden
- Question has no is_primary link (non-top-40) -> current flat list fallback (no visual regression)
- Question has 0 links -> current 'no example' red badge

Manual smoke test AC:
- Launch vite dev (localhost:5173/behavioral); pick OWN-1 (will have probe_notes after Phase C); verify primary card is gold-bordered and renders at top; verify probe_notes panel expands and shows 4 sections with markdown; verify 'Also applies' toggles

Also update frontend type src/frontend/src/types/behavioral.ts to include probe_notes + is_primary.

AC:
- TypeScript compiles
- vitest suite passes
- Manual smoke test path completes without console errors
- No regression on questions without probe_notes / without is_primary

### P2 -- Nice to Have

#### T-P2-585: [BQ-DEPTH-14] Phase E: narrow probe-drift detector (principle_tags/risk/outcome/hash only)
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P1-582
- **Description**: Per user direction: drift trigger must be NARROW. Monitoring arbitrary STAR field changes will produce noise the user learns to ignore.

Write scripts/detect_probe_drift.py that flags probe_notes needing refresh ONLY when one of these changes on a linked story since probe_notes_updated_at:
- behavioral_examples.principle_tags
- behavioral_examples.risk_statement
- behavioral_examples.result (the outcome)
- Narrative hash (SHA256 of situation+task+action+result) changed AND delta > threshold (e.g. >30% diff)

Output: docs/bq_probe_drift_report_<date>.md listing (question_id, linked_example_id, drift_reason, diff_preview).

Optional: cron-schedule via session_context.py reminder (not hook -- reminder only).

AC:
- Script reads-only; no DB writes
- Empty output when no drift (silent-on-no-work rule)
- False-positive rate: manually run after BQ-DEPTH-09 with no changes; expect 0 reports
- True-positive rate: manually mutate a test risk_statement; expect 1 report

### P3 -- Stretch Goals

## Blocked

#### T-P0-651: Pinterest VO itinerary update (May 5-6 confirmed): doc 83 + companies row
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: [SUPERSEDED 2026-04-30 by T-P0-654 chain] Original update went to wrong surface (prep_doc prose + companies.interview_stages JSON) instead of the Dashboard's InterviewTimeline widget which reads interview_events table. The DB writes will be reverted; new rows will be added to interview_events via T-P0-654. See T-P0-654/655/656/657/658/659 chain.

#### T-P0-652: Promote DB edits to seed scripts (Invariant 3 durable fix)
- **Priority**: P0
- **Complexity**: S
- **Depends on**: None
- **Description**: [PARTIALLY-SUPERSEDED 2026-04-30] Pinterest portion folded into T-P0-653 (revert) + T-P0-654 (add to interview_events). Uber portion (doc 84 §5 + problem 1097 Invariant-3 promotion) carried forward as T-P0-657.

#### T-P0-661: Root-cause investigation: WHY did Claude default to company_documents.content instead of interview_events?
- **Priority**: P0
- **Complexity**: S
- **Depends on**: T-P0-660
- **Description**: **Per reviewer hole #1**: surface-fix (skill + lint) protects against this specific miss, but the deeper question is unanswered: what made Claude choose company_documents over interview_events when the user said 'update Pinterest onsite schedule'? If the root cause is a general bias toward 'edit prose / follow last-modified doc / search by company name first', the same class of bug recurs on different surfaces.

INVESTIGATION STEPS (must answer 4 questions):

Q1: **Mapping in CLAUDE.md** -- Is there a widget->table or feature->seed mapping table anywhere in CLAUDE.md (root or MLInterviewPrep)? Grep for it. If absent, the model has no priors -- it falls back to free-text search.
  - Action: read MLInterviewPrep/CLAUDE.md fully; grep for 'widget'/'interview_events'/'Dashboard' in shared/claude_md_shared.md and root CLAUDE.md
  - Finding (expected): mapping is missing or buried

Q2: **Conversation priming** -- Did earlier turns in this session prime the prose path? The first task this session was 'add a problem to doc 84 (Uber)' -- that whole interaction was prose-edits-on-company-doc. By the time the Pinterest request came in, the LAST 'update X for company Y' template I executed was prose-on-doc. Re-reading that, it would be natural to apply the same template to Pinterest.
  - Action: re-read the doc-84 turn; identify whether the assistant chose company_documents because the prior turn established that pattern
  - Finding (expected): YES, last-modified priming

Q3: **'Dashboard' in codebase ambiguity** -- How many things are called 'dashboard' or render dashboard-like content? Search src/ for files/components/routes named *Dashboard* or /dashboard.
  - Action: grep -rn 'Dashboard|/dashboard' src/ --include=*.tsx --include=*.ts
  - Finding (expected): only one /dashboard route + Dashboard.tsx + Sidebar entry; user's 'dashboard' is unambiguous in the codebase. So the bug is NOT lexical ambiguity, it's semantic priming + missing mapping.

Q4: **Default search behavior** -- What's the assistant's default when given 'update X for company Y'? Read recent PROGRESS.md entries -- how often does the assistant grep company_documents content first vs check interview_events / companies.status / framework_node? Quantify.
  - Action: tail logs of recent autonomous sessions; count first-grep targets
  - Finding (expected): heavily biased toward company_documents

DELIVERABLE:
- Short root-cause memo (1-2 pages) saved to logs/2026-04-30_pinterest_root_cause.md
- Concrete recommendation: should the fix be (a) add widget->table mapping to CLAUDE.md, (b) extend lint hook (T-P0-660) to ALSO scan company_documents.content writes that smell schedule-like, or (c) both
- Memo's recommendation feeds DIRECTLY into T-P1-656 (skill design) and CLAUDE.md update content

ACCEPTANCE CRITERIA:
- AC1: All 4 Q&As answered with concrete evidence from this conversation + grep output
- AC2: Memo at logs/2026-04-30_pinterest_root_cause.md exists, <=200 lines
- AC3: Concrete recommendation with rationale (a/b/c above), priority-ordered
- AC4: User reviews + green-lights the recommendation BEFORE T-P1-656 begins (skill design depends on root-cause finding)

[USER CONSTRAINTS 2026-04-30 green-light -- HARD GATES]
- AC5: HYPOTHESIS + EVIDENCE, NOT REFLECTION. Memo must NOT read like 'I should check the widget map next time'. Reject behavioral / advisory-only conclusions at draft stage. The memo's value is its explanatory power for future surface bugs of the same class, not a self-pep-talk.

- AC6: REQUIRED MEMO SECTIONS (each with explicit data, not prose):
    (i)   **Session priming path**: If the conversation transcript is still accessible (check .claude/transcripts/, or scan recent autonomous logs/ for the doc-84 -> Pinterest turn sequence), trace the literal turn-by-turn 'last edited surface' chain leading into the misdirected write. If transcript is gone, document that explicitly and reconstruct from PROGRESS.md + git log.
    (ii)  **Discoverability comparison**: Quantitative grep counts for 'company_documents' vs 'interview_events' across:
            - root + MLInterviewPrep CLAUDE.md (literal mention count)
            - README files (literal mention count)
            - src/ (import / model usage count)
            - scripts/ seed files (import count)
            - docs/ (mention count)
          Present as a table. If 'company_documents' wins by >2x in CLAUDE.md / docs / README, that itself is a falsifiable mechanism for the priming.
    (iii) **At least one falsifiable root-cause hypothesis** -- a statement of the form 'Claude defaults to surface S because property P holds, where P is measurable. If P were inverted, the bias would flip.' Example shape (NOT the answer): 'Claude routes to whichever table has the highest CLAUDE.md mention-density when the user request is ambiguous. Falsification: rewrite CLAUDE.md to invert mention densities and re-test on a held-out ambiguous prompt.'
    (iv)  **Generalization claim**: name at least 2 OTHER surface pairs in this codebase where the same root-cause mechanism would predict a similar mistake (e.g. framework_nodes vs companies.notes, problems.notes vs solution_notes). This forces the hypothesis to make predictions, not just retrofit one incident.

- AC7: DO NOT MARK COMPLETED. After the memo is written:
    - Append a PROGRESS.md entry with the memo verbatim (or first ~100 lines + 'see logs/2026-04-30_pinterest_root_cause.md for full text')
    - Set status to in_progress with a STATUS NOTE: 'AWAITING USER REVIEW -- memo at logs/2026-04-30_pinterest_root_cause.md, do not auto-advance'
    - The orchestrator should then see no unblocked task and stop with all_done=true. User reads memo, replies green-light or revisions.

DEPENDS ON: T-P0-660 (lint hook is the foundation; root cause may recommend extending it)
COMPLEXITY: M (read + grep + write memo + measure discoverability table; the memo itself stays <=200 lines but the evidence-gathering is substantial)

#### T-P1-581: [BQ-DEPTH-10] Primary-story batch: mark is_primary=1 for top 40 high-probability questions
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: From the Phase A matrix (BQ-DEPTH-01), propose the top 40 high-probability BQ questions (based on company overlap + asked-frequency intuition). For each, pick the ONE primary story.

Dependency on BQ-DEPTH-09 is through user-approved calibration style + schema, but this task can run in parallel with C2 bulk if user approves the 40 assignments upfront.

Deliverables:
- docs/bq_primary_story_assignments_20260421.md -- 40 rows with (question_id, primary_example_id, rationale)
- scripts/seed_bq_primary_flags_20260421.py -- idempotent, DB-backup-guarded
- Invariant: each question has exactly one is_primary=1 link (trigger or pre-check)

AC:
- User reviews 40 assignments on Discord BEFORE DB write
- Script re-runs with [SKIP]
- SELECT question_id, COUNT(*) FROM question_example_links WHERE is_primary=1 GROUP BY question_id HAVING COUNT(*) > 1 returns empty
- 40 questions have is_primary=1 set; other questions left at is_primary=0 until later batch

#### T-P1-606: Fix emoji-scan cp1252 crash + lock regex consistency (F-1 + F-3 + meta-test)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Commit 1 of the emoji-scanner fix plan. BLOCKED on user decision between options A/B/C for the 1 legit FE0F hit in PROGRESS.md:590 (discord msg 1497033478842351616, 2026-04-23).

INVESTIGATION COMPLETE, revised findings:
- Original plan assumed 3 regexes byte-identical (subagent survey claim). Verified empirically: FALSE. check_emoji.py retains stale BMP ranges \u2600-\u26ff + \u2700-\u27bf; check_emoji_files.py and lint_check.py had them removed 2026-04-11 per archive/progress_log.md:20 (to kill 81 BLACK STAR-style false positives).
- Current full-repo scan: 63 hits from stale check_emoji.py regex; 62 are BMP false positives that DISAPPEAR under the narrow (canonical) regex; 1 is a legit U+FE0F variation selector in PROGRESS.md:590 from a quoted historical discord message about a prior emoji incident.
- Root cause of user pain is this regex drift (RC-3), not the Windows encoding issue alone (RC-1 is latent).

REVISED EXECUTION SCOPE when unblocked:
1. scripts/check_emoji.py: remove 2 BMP range lines to match check_emoji_files.py + lint_check.py.
2. scripts/check_emoji.py + scripts/check_emoji_files.py: F-1 UTF-8 stream reconfigure at main() entry (defense in depth for future U+1F6xx emoji).
3. tests/test_emoji_regex.py (or new tests/test_emoji_scanner.py): regex-equality meta-test + subprocess cp1252 env test (reviewer's revised F-3).
4. User-chosen handling of PROGRESS.md:590 FE0F (option A/B/C pending).

#### T-P1-627: Add display_label short field to principle_tags so pills show short labels (full phrase in tooltip)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Follow-up to T-P0-626. Pill UI primitive is for short labels; commit e52d568 (2026-04-23) put 33-char-avg phrases in principle_tags. T-P0-626 patches the layout to tolerate long phrases; this ticket fixes the data layer.

GATE (manual, intentional hack): status=blocked even though depends_on=None. Reason: programmatic schema has no 'not_before' field and creating a sentinel-task pattern is overhead for one ticket. Description-only soft gates are insufficient because the autonomous orchestrator's task picker reads only DB fields. Therefore status=blocked is the load-bearing gate. Re-open by manually flipping to active.

UNGATE WHEN: All Uber final-round interviews complete (last is May 4 Coding 2 with Ali Shameli). Manually run: `task_db.py update T-P1-627 --status active`. Re-launch autonomous_run.sh; the orchestrator will then pick this up.

Approach (when ungated):
- Add 'display_label' (~12 chars) to principle_tags source-of-truth seed
- Backend exposes both slug and display_label
- Frontend pills render display_label; tooltip shows full phrase
- Tags missing display_label fall back to label or auto-truncate

AC:
- All 8 EX-01 principle_tags have hand-crafted display_label
- Pills show short labels; tooltip on hover shows full phrase
- T-P0-626's _-to-space rendering becomes unnecessary once this ships

Scope: backend schema + router + frontend pill rendering + seed. M complexity.

#### T-P1-641: [CHEATSHEET-1] Schema + API: add cheat_sheet TEXT column to system_designs, expose in /system-designs/:slug
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Add nullable TEXT column 'cheat_sheet' to system_designs SQLAlchemy model + Alembic-style migration script (scripts/migrate_add_cheat_sheet.py). Update SystemDesign Pydantic schema (read + update) + frontend types/system-design.ts to include cheat_sheet field. Wire into useSystemDesignNotes if edit support is wanted (defer if too big -- read-only is fine for v1). AC: (1) ALTER TABLE migration is idempotent (IF NOT EXISTS / try-except); (2) GET /system-designs/<slug> response includes cheat_sheet (null when empty); (3) GET /system-designs (list endpoint) returns cheat_sheet too so the new tab can render without per-row fetch -- or keep list lean and have new tab call /system-designs/cheat-sheets aggregation endpoint, decide based on payload size; (4) backend tests added; (5) ruff/mypy clean. NO content authoring in this task -- column stays null.

#### T-P1-642: [CHEATSHEET-2] Frontend: add 'Cheat Sheet' tab to /system-design with one-pager card per row
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Add third tab 'Cheat Sheet' to SystemDesignList.tsx alongside 'Interview Prep' and 'eBay Projects'. New tab renders a vertically-stacked single-page list (NOT a grid) of all system_designs entries sorted by display_order. Each entry is a CheatSheetCard component:  (a) sticky-position H2 with title + small badge for category (eBay / Pinterest / Generic / Uber); (b) MarkdownPreview of the cheat_sheet field (so code-fence ascii arch + tables render correctly with KaTeX + GFM); (c) right-edge link 'Full design ->' to /system-design/<slug>; (d) graceful empty state when cheat_sheet is null ('No cheat sheet yet'). Add ?tab=cheatsheet URL synchronization (same pattern as existing tabs). Add a left-side sticky TOC sidebar within the cheat-sheet tab (desktop only) listing all cards by title for quick jump. AC includes a manual smoke test: open /system-design?tab=cheatsheet, verify 35+ cards render, KaTeX formulas render, no console errors, deep-link to ?tab=cheatsheet#<slug> scrolls to that card. Vitest snapshot for the new component.

#### T-P1-643: [CHEATSHEET-3] Add 2 Uber rows to system_designs from doc 85 (Restaurant Rec + Budget-Constrained Promo)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Currently Uber Eats Restaurant Recommendation and Budget-Constrained Promo Recommendation only live inside company_documents id=85 (markdown doc). Promote them to first-class system_designs rows so they appear on /system-design page and the new Cheat Sheet tab.  Steps: (1) Create scripts/seed_uber_system_designs.py (idempotent -- upsert by slug); (2) extract content from doc 85 sections 1.x and 2.x into the corresponding system_designs columns (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) -- DO NOT duplicate, KEEP doc 85 as the canonical narrative source and treat system_designs as the structured projection; (3) slugs: 'uber-eats-restaurant-rec' (display_order 200), 'uber-budget-promo-rec' (display_order 201); (4) populate cheat_sheet field directly from §1.6 and §2.11 (the existing one-pager sections) -- this is the ONLY content authoring in this task; (5) frontend: TOPIC_META in SystemDesignList.tsx may need a new 'Uber' category (or put under 'Specialized'). AC: backend GET /system-designs returns the 2 new rows; clicking renders the existing detail page UI with no errors; doc 85 is unchanged.

#### T-P1-644: [CHEATSHEET-4] Author cheat-sheets for 4 eBay projects (display_order 1-4)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: module-arbitration, llm-orchestration, pbe-pipeline, ranking-allocation. Source each cheat sheet from the existing system_designs.{overview,architecture,dataflow,formulas,production_constraints,tradeoffs,defense,verbal_outline} columns -- do NOT invent new content, distill from what is already there. Format MUST match doc 85 §1.6: (a) code-fence vertical pseudo-arch; (b) keywords block (bold industry jargon); (c) Senior signal table (不及格 vs Staff Golden); (d) mini jargon glossary. Length budget: ~2000 chars per cheat sheet. Write to cheat_sheet column via idempotent seed script scripts/seed_cheat_sheets_ebay_projects.py (upsert by slug, only update if content_hash differs). AC: 4 rows have non-null cheat_sheet; markdown lints; KaTeX renders if formulas used; vitest of CheatSheetCard with one of these 4 as fixture passes.

#### T-P1-645: [CHEATSHEET-5] Author cheat-sheets for 4 eBay reference docs (display_order 5-8)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-641
- **Description**: Slugs: database-comparison, distributed-task-queue, vibe-code-engineering-patterns, ml-system-design-patterns. These are reference / pattern docs not single design problems, so the cheat sheet format adapts: (a) for database-comparison -- side-by-side decision matrix (workload -> recommended store) instead of vertical pseudo-arch; (b) for distributed-task-queue -- failure-mode table + idempotency strategy keywords; (c) for vibe-code -- pattern bullet-list with one-line trade-off each; (d) for ml-sd-patterns -- the cross-cutting senior signals from doc 85 §3 are a strong template, mirror that style. Same length budget (~2000 chars), same idempotent seed pattern (scripts/seed_cheat_sheets_ebay_refs.py). AC: 4 rows have non-null cheat_sheet; rendered cards visually distinct from project cards (badge color differs).

#### T-P1-646: [CHEATSHEET-6] Author cheat-sheets for 7 Pinterest ML problems
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Slugs: pinterest-ad-ctr, pinterest-embeddings, pinterest-chatbot-pins, pinterest-pin-ranking, pinterest-pins-search, pinterest-notification-reco, pinterest-catalog-bulk-update. Source from existing system_designs columns AND from any company_documents rows where company.slug='pinterest' and the doc maps to one of these 7 problems (cross-reference by title). Format MUST match doc 85 §1.6 -- vertical pseudo-arch + keywords + senior table + mini glossary. Pinterest-specific jargon to call out: PinSage, GraphSAGE, two-tower, Galaxy item embeddings, Pixie random walk, AutoML reranker -- expand each acronym in the glossary. Idempotent seed: scripts/seed_cheat_sheets_pinterest.py. Length budget per card ~2000 chars. AC: all 7 rows have non-null cheat_sheet; the vibe-code-style 'badge' on the card reads 'Pinterest'; manual smoke test on /system-design?tab=cheatsheet shows them grouped together visually.

#### T-P1-647: [CHEATSHEET-7] Author cheat-sheets for 10 generic SD problems (batch 1: Core Infra + Social/Real-time + Geo)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 1 slugs: interview-url-shortener, interview-rate-limiter, interview-distributed-cache, interview-notification-system, interview-news-feed, interview-chat-system, interview-live-comments, interview-game-leaderboard, interview-ride-sharing, interview-proximity-service. Format per doc 85 §1.6 (vertical pseudo-arch + keywords + senior table + mini glossary). Source from existing system_designs columns. Length ~1500 chars (these are interview-prep concise cards, slightly tighter than the eBay project cards). Idempotent seed: scripts/seed_cheat_sheets_generic_sd_batch1.py. AC: 10 rows have non-null cheat_sheet; ruff/mypy clean; vitest passes.

#### T-P1-648: [CHEATSHEET-8] Author cheat-sheets for 9 generic SD problems (batch 2: Search/Data + Storage/Media + Specialized)
- **Priority**: P1
- **Complexity**: L
- **Depends on**: T-P1-641
- **Description**: Batch 2 slugs: interview-search-autocomplete, interview-top-k-heavy-hitters, interview-ad-click-aggregator, interview-web-crawler, interview-video-streaming, interview-cloud-storage, interview-price-drop-tracker, interview-online-judge, interview-ticket-reservation, interview-auction-system. (10 slugs total -- batch 2 takes the remainder.) Same format as batch 1 (~1500 chars, doc 85 §1.6 style, idempotent seed scripts/seed_cheat_sheets_generic_sd_batch2.py). AC: every interview-* row in system_designs has non-null cheat_sheet after this task lands.

#### T-P1-649: [CHEATSHEET-9] Smoke test: load /system-design?tab=cheatsheet, verify all 37 cards render, no console errors
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-648
- **Description**: Final integration smoke test (manual + automated): (1) start dev server (npm run dev + uvicorn); (2) navigate to http://localhost:5173/system-design?tab=cheatsheet; (3) verify ALL rows in system_designs have a rendered card (count == row count); (4) zero console errors; (5) KaTeX formulas render where present; (6) deep-link with #<slug> hash scrolls correctly; (7) prev/next nav still works on detail pages; (8) Interview Prep + eBay Projects tabs still render unchanged (regression check). Append a screenshot or text-only confirmation to PROGRESS.md. Add a vitest E2E-ish test that mounts SystemDesignList and asserts all 3 tabs render their expected card count. AC: all 8 verification points pass; no regression in existing tabs.

#### T-P1-656: Build /dashboard skill: route 'dashboard' keyword to InterviewTimeline + Dashboard widgets, never prep_doc prose
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-661
- **Description**: Phase 3. **Per reviewer**: skill is documentation, NOT enforcement (lint hook in T-P0-660 is the real guardrail). Skill's job: make the right path the easy default for any future Claude session that gets a 'dashboard / app / left-nav-first' request. **DEPENDS on T-P0-660 (lint exists) AND T-P0-661 (root cause + recommendation)** -- skill design absorbs the root-cause memo's recommendation.

REVISED DESIGN (per reviewer hole #4: 3 memory files -> 1 reference + CLAUDE.md):

The skill content lives in TWO places, both updated together:
1. **CLAUDE.md (canonical, loaded every session via SessionStart)**: add a widget->data-source mapping table. This is the source of truth.
2. **.claude/skills/dashboard.md (deepening / triggers)**: invoked when keywords match. References CLAUDE.md table; doesn't duplicate it. Skill body is the 6-step protocol.

CLAUDE.md addition (under 'Behavior Rules' or new 'Surface Identification' section):

  ### Surface Identification (MLInterviewPrep)

  Before editing DB content for a request that mentions a UI surface, map widget -> data source:

  | Widget (Dashboard.tsx) | Query key                | API endpoint            | DB table / column        |
  |------------------------|--------------------------|-------------------------|--------------------------|
  | InterviewTimeline      | ['timeline','events']    | GET /timeline/events    | interview_events         |
  | FocusTopic             | ['dashboard','today']    | GET /dashboard/today    | derived: framework_node + reading_progress |
  | CompanyPipeline        | ['companies']            | GET /companies          | companies.status         |
  | PrepQuickAccess        | ['companies']            | GET /companies          | companies.prep_notes (markdown checklist) |
  | WeeklyActivityChart    | ['dashboard','activity'] | GET /dashboard/activity | derived: problem_attempts + study_sessions |

  Schedule / itinerary / calendar / event = interview_events (NEVER company_documents.content).
  Pipeline status = companies.status. Daily focus = derived. Checklist = companies.prep_notes. Prose study notes (and ONLY those) = company_documents.

  Idempotent seed pattern per row type:
  - interview_events: scripts/_add_<company>_<date>.py, canonical key (company_id, scheduled_at, interviewer_name)
  - company_documents: scripts/seed_<company>_<doc>.py with sentinel-based UPSERT
  - problems: scripts/seed_<company>_lc_problems.py or similar; canonical key leetcode_id or title

Skill (.claude/skills/dashboard.md) body — 6-step protocol:
1. Read MLInterviewPrep/CLAUDE.md 'Surface Identification' table; map request to widget
2. Confirm match by reading the widget's component file (e.g. InterviewTimeline.tsx -> queryKey -> endpoint -> table)
3. Locate the matching idempotent seed (or, if absent, plan a new one)
4. Edit the SEED, not the DB. Run the seed. Verify [INSERT|UNCHANGED] output
5. Verify with SQL count assertion FIRST, then optionally screenshot
6. Send Discord deliverable: SQL counts > screenshot. Wait for user confirmation before marking task done.

ACCEPTANCE CRITERIA:
- AC1: CLAUDE.md (MLInterviewPrep/CLAUDE.md) has the new 'Surface Identification' section with the widget->table table
- AC2: .claude/skills/dashboard.md exists with the 6-step protocol referencing CLAUDE.md
- AC3: Skill triggers on regex matching 'dashboard' / '我们 app' / '左侧 tab' / 'left nav' / 'first nav item' (set in skill metadata or trigger field)
- AC4: Self-test: dry-run skill on 'add Stripe HR call to my dashboard' -> output proposes interview_events row + references _add_<company>_<date>.py pattern -- verified by reading skill output
- AC5: Section in CLAUDE.md cross-links to the lint hook (T-P0-660) so reader sees both the prescription AND the enforcement
- AC6: Skill design ABSORBS recommendation from T-P0-661 root-cause memo (e.g. if memo says 'last-modified doc priming bias', skill includes a note 'do NOT pattern-match from prior session's edit target — always re-derive from widget mapping')

DEPENDS ON: T-P0-660, T-P0-661
COMPLEXITY: M

#### T-P1-657: Invariant-3 promotion: doc 84 §5 N-gram LM + problem 1097 to seed scripts
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P0-660
- **Description**: Phase 4. Promote earlier session's Uber doc 84 §5 + problem 1097 to seed scripts. **Per reviewer hole #3**: do NOT delete scripts/migrations/add_uber_prob_nextword.py. Better: keep file, replace body with a no-op + DEPRECATED header. Reasons: (a) git history preservation in working tree, not just log; (b) staging / rebuild environments that re-run migrations get a clear deprecation message rather than missing file errors; (c) future readers can grep for the original migration intent.

THREE STEPS:

1. Update scripts/seed_uber_ml_coding_golden.py:
   - Append §5 N-gram LM section to CONTENT (~600 lines from current DB doc 84 -- copy verbatim from `SELECT content FROM company_documents WHERE id=84`)
   - Bump validate_content() length range (currently caps at probably 35-40K, new content is ~49K) and add §5 markers ('## §5' or '## 5. 概率下一个词生成' or 'ngram-next-word')
   - Re-run, expect [UNCHANGED] (since DB content already matches the new CONTENT)

2. Create scripts/seed_uber_ml_coding_problems.py (or extend an existing matching seed):
   - Owns the from-scratch ML coding problems for Uber: problem 1064 (K-Means), problem 1097 (N-gram LM), and ideally also Geometric Median + Linear Regression + Logistic Regression (the 4 §-1 through §-4 problems in doc 84)
   - Idempotent UPSERT on title (or leetcode_id when present)
   - Each row gets the proper company_tags JSON ['Uber'] AND a problem_company_tags row (relevance='likely', source='manual')
   - Notes field includes [db://doc/84#<anchor>] cross-link to the matching section
   - Re-run, expect 5 [UNCHANGED] (since DB already has them via the migration)

3. Replace scripts/migrations/add_uber_prob_nextword.py with no-op + deprecation:
   - First line: `# DEPRECATED 2026-04-30: Logic moved to scripts/seed_uber_ml_coding_golden.py and scripts/seed_uber_ml_coding_problems.py per Invariant 3 (no migration scripts that write to DB).`
   - Body: `if __name__ == '__main__': sys.exit(0)`
   - Keep file in git so future tree references resolve, but it does nothing if executed
   - Same treatment for scripts/migrations/update_pinterest_onsite_itinerary.py (the other this-session migration)

ACCEPTANCE CRITERIA:
- AC1: scripts/seed_uber_ml_coding_golden.py CONTENT now includes §5; second run = [UNCHANGED]
- AC2: scripts/seed_uber_ml_coding_problems.py exists with 5 problems (1064 + 1097 + 3 others); second run = 5×[UNCHANGED]
- AC3: scripts/migrations/add_uber_prob_nextword.py and scripts/migrations/update_pinterest_onsite_itinerary.py both replaced with deprecation no-op; running each prints '[DEPRECATED] no-op' and exits 0
- AC4: T-P0-660 invariant3 lint hook does NOT trigger on the no-op deprecated files (since they no longer contain INSERT/UPDATE) — this proves the lint design works
- AC5: `git diff scripts/migrations/` shows clean rewrites; `git log --follow scripts/migrations/add_uber_prob_nextword.py` still shows full history

DEPENDS ON: T-P0-660 (lint hook should already exist — this task verifies the hook accepts the deprecated files)
COMPLEXITY: M

#### T-P1-658: LESSONS.md: 'Dashboard means widget, not prose' + Invariant 3 enforcement
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Append a [UNIVERSAL] LESSONS.md entry capturing the 2026-04-30 mistake class so future sessions don't repeat it. Two distinct lessons:

LESSON A — Surface identification before prose edits:
- Title: '[2026-04-30] User says "dashboard" / "app 那边" / "left nav first item" -> they mean a UI widget on the named page, NOT prose in a prep doc'
- Context: User asked to update Pinterest VO schedule. I edited company_documents.id=83 (prep doc prose) and companies.interview_stages JSON. Both wrong surface. The Dashboard's InterviewTimeline widget reads the interview_events table; that was the surface user actually meant.
- What went wrong: I matched 'Pinterest onsite update' to the most prominent Pinterest text I could find (the prep doc) without first asking 'which UI surface renders this?' The prep doc is a study notebook; calendar/event data lives in interview_events.
- Fix: For any 'update X in our app / on dashboard / in <named UI element>' request, FIRST identify which frontend page + widget is being referenced (read src/frontend/src/pages/Dashboard.tsx and trace queryKey -> /api/<endpoint> -> <DB table>). THEN map to the appropriate idempotent seed. Schedule/itinerary/calendar => interview_events. Pipeline status => companies.status. Daily focus => derived from framework + reading. Checklist => companies.prep_notes. Prose study notes only => company_documents.
- Tags: #ux-target-identification #dashboard #widget-vs-prose #interview-events

LESSON B — Invariant 3 enforcement (already partly logged 2026-04-25; reinforce):
- Title: '[2026-04-30] Direct SQL UPDATE on data/mle_prep.db violates Invariant 3 — every DB row must originate from a git-tracked, idempotent Python seed in scripts/'
- Context: I twice this session wrote scripts/migrations/*.py that did sqlite3.execute('UPDATE ...') / INSERT directly. The DB is regenerable; the seed scripts are source of truth. Direct DB edits create timebombs (next seed run wipes them).
- What went wrong: scripts/migrations/ as a directory pattern feels familiar from server-side migrations, but in this project there are no migrations — there are only idempotent seeds. The migration scripts were correctly idempotent on their own canonical keys, but they bypassed the seed-based source of truth.
- Fix: For ANY DB content change, edit (or create) the matching seed in scripts/seed_*.py. The seed must be idempotent (re-runnable safely). Run it once to apply. Check git diff on the seed = the durable record of what changed. NEVER write to data/mle_prep.db from scripts/migrations/.
- Detection: any time you find yourself writing 'sqlite3.connect(...).execute("UPDATE"|"INSERT"|"DELETE")' outside scripts/seed_*.py — STOP. Ask: 'which seed owns this row?' Find/extend that seed.
- Tags: #invariant-3 #seed-not-migration #db-source-of-truth

ACCEPTANCE CRITERIA:
- AC1: LESSONS.md has both entries appended at bottom with date 2026-04-30 and tag-line format
- AC2: Lessons reference T-P0-651 (the misdirected work), T-P0-654 (the correct fix), T-P1-657 (the Invariant-3 promotion)
- AC3: cross-project-reviewer agent flagged-eligible (both lessons tagged [UNIVERSAL] for propagation to helixos/homestead/template per cross-project-sync 2026-04-29 pattern)

DEPENDS ON: nothing
COMPLEXITY: XS (~30 lines of LESSONS.md append)

#### T-P1-659: Save user feedback memory: dashboard semantics + Invariant 3 trigger words
- **Priority**: P1
- **Complexity**: S
- **Depends on**: T-P1-656
- **Description**: Phase 4. **Per reviewer hole #4**: 3 separate memory files is overengineering — 'next session finds it' is determined by surface path (CLAUDE.md / reference file), not file count. Merge to ONE reference file + ensure CLAUDE.md cross-links to it.

SINGLE MEMORY FILE: ~/.claude/projects/C--Users-Shenghui-Xu-Desktop-Gen-AI-Proj/memory/reference_dashboard_data_sources.md (type=reference)

Body:
- Lead: 'MLInterviewPrep Dashboard widget -> data source map (verified 2026-04-30 via T-P0-654/T-P0-661). Use this BEFORE editing any prose for a request mentioning a UI surface.'
- Body: the same widget->table mapping table that goes in CLAUDE.md (one-source-of-truth — memory file CITES CLAUDE.md path: `MLInterviewPrep/CLAUDE.md "Surface Identification"` rather than copying)
- Trigger phrases section: 'dashboard / app 那边 / 左侧 tab 第一 / left nav top / first nav item -- when these appear, route to /dashboard skill'
- Anti-pattern section: '2026-04-30 incident: edited company_documents.id=83 prose + companies.interview_stages JSON for an interview-schedule update. Both wrong surface. Right surface = interview_events table (5 rows for 5 onsite rounds).'
- Why-this-matters: 'Without this map, default behavior is to grep company name + content match -> hit company_documents (largest text surface) -> edit prose. That works for prose updates and FAILS for everything else (schedule, status, checklist, focus).'

MEMORY.md INDEX UPDATE:
- 1 new line: `- [reference_dashboard_data_sources.md](reference_dashboard_data_sources.md) — Dashboard widget->table map; route 'dashboard' keyword to /dashboard skill before editing`

DELETED FROM ORIGINAL PLAN (per reviewer 'overengineered'):
- ~~feedback_dashboard_means_widget.md~~ (folded into reference file)
- ~~feedback_invariant3_seed_only.md~~ (covered by lint hook + LESSONS.md, not a memory)
- ~~the 'why' / 'how to apply' duplication across 3 files~~ (consolidated)

ACCEPTANCE CRITERIA:
- AC1: Exactly ONE new memory file: reference_dashboard_data_sources.md (NOT 3)
- AC2: MEMORY.md has exactly 1 new line, ≤150 chars
- AC3: File body cites MLInterviewPrep/CLAUDE.md (the canonical source) -- doesn't duplicate the table
- AC4: A grep test: opening ~/.claude/.../memory/MEMORY.md and following the new index entry surfaces the widget mapping in <2 file reads (MEMORY.md -> reference file -> CLAUDE.md)

DEPENDS ON: T-P1-656 (CLAUDE.md table must exist BEFORE the memory file cites it)
COMPLEXITY: XS

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos + template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Remove deprecated stop-cache from BOTH helixos/.claude/hooks/test_check.py AND claude-code-project-template/.claude/hooks/test_check.py. Both still import and use check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed these (T-P2-188, commit abf6543) per the lesson that stop caches cause false PASS results when files change between sessions.

Verified state (2026-04-23): helixos/.claude/hooks/test_check.py lines 10, 21, 48 still import/call check_stop_cache/write_stop_cache. claude-code-project-template/.claude/hooks/test_check.py same three lines.

Action:
1. helixos/.claude/hooks/test_check.py: remove cache import and calls -- copy MLInterviewPrep version.
2. claude-code-project-template/.claude/hooks/test_check.py: same removal.
3. Clean up hook_utils.py in both repos only if no other callers remain.
4. Run tests after to confirm hook still works.

Consolidated from duplicates: T-P2-255, T-P2-320 (both helixos stop-cache), T-P2-208 (template stop-cache). All 3 marked completed-as-duplicate on 2026-04-23 per T-P2-587.

Blocked: must be executed from a helixos or template Claude Code session -- file permissions prevent writing to those repos' .claude/hooks/ from a MLInterviewPrep session.

Source: MLInterviewPrep/.claude/hooks/test_check.py (cache-free reference).

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-636: [UBER-VO-5b POST-5/4] Bespoke pages/UberIndex.tsx with 5-tab charter switcher (deferred)
- **Priority**: P2
- **Complexity**: L
- **Depends on**: None
- **Description**: ## Status: DEFERRED post-2026-05-04 per critical review
This is the original T-P0-632 scope (bespoke React page + URL state + drawer state + browser back/forward + accessibility + vitest). Moved out of the 5/4-readiness critical path. Pick up only if the T-P0-632 MVP (id=37 patch) proves insufficient during actual prep usage.

## Trigger to re-prioritize
- I find myself navigating id=37 -> Round 2 -> click link -> target doc -> back button -> click another link, repeatedly, and the friction matters.
- Or: a follow-up Uber recruiter loop schedules another VO requiring deeper navigation.

## Goal (preserved from original plan)
A bespoke \`pages/UberIndex.tsx\` route at \`/companies/uber/index\` mirroring \`pages/QuickIndex.tsx\` pattern: 5 tab pills (LC / ML Coding / ML SD / Behavioral / HR), per-tab card grid, click-to-drawer, URL state, browser back/forward, empty-state copy, ARIA accessibility, vitest coverage.

## Locked decisions inherited from MVP
- Drawer type: SlideOverPanel via existing \`db://N#anchor\` convention (with anchor support added if T-P0-632 surfaces it as missing).
- Behavioral API: \`/behavioral/themes?company=uber\`.
- Implementation Option A: bespoke page (NOT generalize QuickIndex).

## Acceptance criteria (from original T-P0-632)
- All 5 tabs render correct content with stable URL state.
- Card click opens SlideOverPanel with anchor-scroll.
- Browser back/forward preserves tab+drawer state.
- Empty state for charters lacking content.
- Accessibility: role=tab, ARIA-controls, keyboard arrow nav.
- Vitest tab-switch + drawer-open + empty-state.
- No emoji.

## Dependencies
Upstream: T-P0-632 (MVP must ship first; if MVP suffices, this task closes as 'skipped').

## Completed Tasks

> 604 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-29** -- T-P2-640: [SYNC] Promote Dependency source-of-truth CLAUDE.md rule to template + MLInterviewPrep. helixos/CLAUDE.md has a Key Constraints section codifying that pyproject.toml and requirements.txt must be kept in sync 
- [x] **2026-04-29** -- T-P2-638: [SYNC] Promote 3 [UNIVERSAL] LESSONS.md entries from MLInterviewPrep to template. MLInterviewPrep/LESSONS.md has 3 [UNIVERSAL]-tagged entries (task_db cwd-routing, autonomous all_done sticky-state, plus
- [x] **2026-04-29** -- T-P2-637: [SYNC] Promote MLInterviewPrep harness improvements to claude-code-project-template. Cross-project-sync 2026-04-29 found 4 universal harness improvements in MLInterviewPrep that template lacks:
- [x] **2026-04-29** -- T-P2-633: [UBER-VO-6] Add deprecation/redirect banner to legacy id=81 'Uber LC 题库索引视图'. ## Goal
- [x] **2026-04-29** -- T-P1-650: Doc 84 §5: Probabilistic Next-Word Generation (Uber, no-library n-gram LM). Add a 5th problem to Uber ML Coding Golden Answer 集合 (doc 84): Probabilistic next-word generation, no library, expand be
- [x] **2026-04-29** -- T-P0-660: Phase 2 — Migration lint hook: forbid INSERT/UPDATE/DELETE in scripts/migrations/* against data/*.db. **Per reviewer: 'Documentation != Constraint'** -- the dashboard skill (T-P1-656) is documentation that future sessions 
