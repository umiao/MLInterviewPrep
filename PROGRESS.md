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
> 123 session entries archived as of 2026-04-13.

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
## 2026-04-13 -- [T-P1-403] Pinterest round-by-precision custom problem
- **What I did**: Added non-LC Pinterest-tag problem to `data/mle_prep.db` for the 2025-11 "round string s to precision p (power of 10)" follow-up to T-P1-402. Canonical solution derives `k` from `p` (sign of k decides int-side truncation vs frac-side quantize), then reuses the T-P1-402 parse + carry machinery with the carry chain starting at position `k` instead of ones. Notes include English + Chinese explanations, an edge-case matrix (carry crossing int/frac boundary `9.99/0.1 -> 10.0`, magnitude-zero `0.04/0.1 -> 0.0`, -0 guard, leading-zero pad `49/100 -> 0`, carry extending width `99.95/0.1 -> 100.0`), and follow-ups (non-power-of-10 p, banker's rounding, streaming input).
- **Deliverables**: scripts/_add_pinterest_round_by_precision.py (new, idempotent seeder), scripts/_smoke_round_by_precision.py (new, standalone verifier with Decimal.quantize cross-check), data/mle_prep.db (new row id=1074).
- **Sanity check result**: `python scripts/_smoke_round_by_precision.py` -> OK 18 valid + 6 invalid cases passed (+ Decimal-ref parity on all valid). Seeder -> `[INSERT] id=1074`; second run -> `[SKIP]` (idempotent). Caught 3 bugs during smoke: (1) missing `frac[0]` fallback when `keep_len == len(int_part)` (bit `2.5/p=1`), (2) all-zero magnitude rendering `'000'` instead of `'0'`, (3) Decimal ref needed `Decimal(1).scaleb(k)` because `Decimal('100')` has exponent 0 -- quantize target silently treated as ones.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-403 --status completed`

## 2026-04-13 -- [T-P1-404] LC 332 loop follow-up addendum
- **What I did**: Appended Pinterest 2025-11 follow-up addendum to existing LC 332 notes (problem id=148) answering "what if tickets form a cycle?" — Hierholzer handles Eulerian circuits natively (dead-end/post-order mechanics identical for path vs circuit; JFK ends up at both head and tail after reversal). Added Eulerian existence conditions table (path vs circuit degree + connectivity), O(V+E) infeasibility-detection recipe, and the "two disjoint cycles = degrees valid but not connected" gotcha. No new problem row — addendum lives inline after a `---` separator in the existing notes.
- **Deliverables**: scripts/_append_lc332_loop_addendum.py (new, idempotent updater keyed on `### Pinterest 2025-11 Follow-up` marker), data/mle_prep.db (id=148 notes 2167 -> 3403 chars).
- **Sanity check result**: First run -> `[UPDATE] id=148 notes 2167 -> 3403 chars`; second run -> `[SKIP] addendum already present`. Verified appended content via UTF-8 stdout dump (last 800 chars render correctly, tables and code fences intact).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-404 --status completed`

## 2026-04-13 -- [T-P1-412] Pinterest BQ question -> story map
- **What I did**: Created docs/pinterest/bq_question_map.md mapping the 5 Pinterest 2025-11 BQ questions (end-to-end own, requirement origin, stepping ahead, negative feedback, teammate missing deadlines) to 2-3 best-fit post-rework EX-XX stories each with a one-sentence angle. Chinese. References EX IDs in docs/bq_behavioral_examples.json.
- **Deliverables**: docs/pinterest/bq_question_map.md (new, ~50 lines, 5 mapping tables + usage notes).
- **Sanity check result**: Verified all 12 referenced EX IDs exist in docs/bq_behavioral_examples.json; each question maps to 2-3 distinct stories; avoided over-reuse (EX-01 only primary in Q2, backup in Q3; EX-15 backup in both Q3 and Q5 with distinct angles, flagged in usage notes).
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-412 --status completed (already done)

## 2026-04-13 -- [T-P1-400] Pinterest Grant Access / permission propagation custom problem
- **What I did**: Added Pinterest coding 2025-11 custom problem "Grant Access / Permission Propagation on a DAG" via scripts/_add_pinterest_grant_access.py. Covers canonical upward ancestor-walk solution, downward-closure alternative, revoke semantics (deny-list vs recompute), true-DAG multi-parent handling, group grants, and scale trade-offs. English + Chinese notes.
- **Deliverables**: scripts/_add_pinterest_grant_access.py (new); data/mle_prep.db row id=1075.
- **Sanity check result**: Script inserted id=1075; ran the embedded smoke test end-to-end (tree + multi-parent DAG, 9 assertions) -- all pass. Verified row present via SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-400 --status completed

## 2026-04-13 -- [T-P1-401] Pinterest Pin Connectivity custom problem
- **What I did**: Added Pinterest coding 2025-11 custom problem "Pin Connectivity on a Pinterest Relationship Graph" via scripts/_add_pinterest_pin_connectivity.py. Canonical Union-Find (path compression + union-by-rank) solution, BFS/DFS alternative, follow-ups for component size / counts, edge removal (offline reverse + Holm dynamic connectivity), shortest-hop distance, and sharded-scale design. English + Chinese notes.
- **Deliverables**: scripts/_add_pinterest_pin_connectivity.py (new); data/mle_prep.db row id=1076.
- **Sanity check result**: Script inserted id=1076; embedded smoke test (9 assertions over pins/boards/users with tagged keys, multi-edge, duplicate, self-edge, unseen nodes) all pass. Verified row via SELECT.
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-401 --status completed

## 2026-04-13 -- [T-P1-408] Pinterest SD: Ad CTR Prediction
- **What I did**: Wrote end-to-end Chinese SD doc docs/pinterest/system_design_ad_ctr.md covering clarifying questions, high-level architecture (multi-stage candidate gen / L1 / L2 / calibration / auction), data pipeline + delayed-feedback label construction, four feature families + train/serve skew, DeepFM vs DCN-v2 vs AutoInt model choice, Platt/isotonic calibration + negative-sampling prior correction, serving latency budget breakdown, online metrics (NE, LogLoss, calibration ratio, ECE), and 8 common follow-ups with Chinese interview Q/A snippets.
- **Deliverables**: docs/pinterest/system_design_ad_ctr.md (new, 260 lines).
- **Sanity check result**: File created; line count 260; structure mirrors existing pinterest SD docs (pin_ranking, notification_reco); covers all 6 required topics from task description (pipeline, feature eng, model, calibration, serving, online metrics).
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-408 --status completed

## 2026-04-13 -- [T-P1-409] Pinterest SD: User & Item Embeddings
- **What I did**: Wrote end-to-end Chinese SD doc docs/pinterest/system_design_embeddings.md covering clarifying questions, high-level architecture (two-tower + PinSage graph), multi-task contrastive objective (long-repin primary + aux labels, LogQ correction, hard negatives), pin content tower (ViT+mBERT+taxonomy+graph) and user sequence tower (Transformer over last-50 engagement + long-term topic distribution), training pipeline (daily batch + 15-min user streaming + new-pin streaming), serving (ScaNN/HNSW ANN with shard + PQ quantization), 4 downstream uses (candidate gen / ranking features / similar-pins / lookalike), monitoring, and 10 common interview follow-ups (popularity bias, cold start, interest drift, ranker coupling, rollback).
- **Deliverables**: docs/pinterest/system_design_embeddings.md (new, 340 lines).
- **Sanity check result**: File created; 340 lines; structure mirrors existing pinterest SD docs (ad_ctr, pin_ranking, notification_reco); covers all 5 required topics from task description (objective, encoder, training pipeline, serving, downstream uses).
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-409 --status completed

## 2026-04-13 -- [T-P1-411] Pinterest SD: Personalized Chat Bot Recommending Pins
- **What I did**: Wrote end-to-end Chinese SD doc docs/pinterest/system_design_chatbot_pins.md covering clarifying questions, high-level architecture (safety -> dialog state -> intent -> query rewrite -> multi-retriever RAG -> grounded generation -> output safety), conversation understanding (LLM-compiled state + context compression + coreference), intent taxonomy (ask-pins / refine / compare / chit-chat / off-topic) w/ built-in vs guardrail classifier, RAG design (dense ANN + BM25 + personalized re-rank via RRF, LGBM stage-1, optional LLM stage-2), grounded generation (prompt structure, 7B fine-tune, structured decoding, citation enforcement), dual-direction safety layer (PII, toxicity, self-harm, jailbreak, ads disclosure, kill switch), training (SFT + DPO + retrieval alignment + online), serving budget / scale, monitoring (offline + online + A/B), and 10 common interview follow-ups.
- **Deliverables**: docs/pinterest/system_design_chatbot_pins.md (new, 337 lines).
- **Sanity check result**: File created; 337 lines; structure mirrors existing pinterest SD docs (embeddings, ad_ctr, pin_ranking); covers all 6 required topics from task description (conversation understanding, intent classification, RAG, grounding, safety/moderation, evaluation).
- **Status**: [DONE]
- **Request**: task_db.py update T-P1-411 --status completed

## 2026-04-13 -- [T-P2-396] Pinterest LC Investigation: 寻找餐馆区间
- **What I did**: Investigated the no-LC-number problem "寻找餐馆区间" from Pinterest 2025-11 dump. Compared 4 candidates (LC 1779/2563/1094/1851) against keywords 「寻找」and「区间」and difficulty prior. Concluded LC 1851 "Minimum Interval to Include Each Query" is best match (Hard; offline sort + min-heap keyed on interval length; natural restaurant-service-radius themeing). Wrote Chinese investigation note documenting rationale + fallback if onsite was actually 1094/2563. Tagged LC 1851 with Pinterest company tag in problems DB.
- **Deliverables**: docs/pinterest/lc_investigation_restaurant_intervals.md (new); problems table LC 1851 company_tags += Pinterest.
- **Sanity check result**: Note created with comparison table + rationale; DB tag update verified via SELECT (company_tags=['Pinterest']).
- **Status**: [DONE]
- **Request**: task_db.py update T-P2-396 --status completed

## 2026-04-13 -- [T-P2-413] Pinterest LC Index Doc Enrichment
- **What I did**: Enriched company_documents id=47 "Pinterest LC Must-Do -- Review & Index" with 5 new appendix sections: (1) Pinterest Expansion LC set (84, 392, 3229, 1526, 1564, 1580, 1851) with difficulty/pattern/notes + 4 new clusters (F-I); (2) Custom Coding Problems table (8 Pinterest-specific customs including LC332 loop addendum); (3) System Design Modules table linking to all 7 docs/pinterest/system_design_*.md files; (4) BQ Question Map link to docs/pinterest/bq_question_map.md; (5) LC <-> SD cross-links table mapping each SD module to most-relevant LC problems. Used lc:// drawer scheme for all LC problems with leetcode_id; SD links use relative paths.
- **Deliverables**: scripts/_enrich_pinterest_index_doc.py (new); company_documents id=47 content updated (6687 -> 12446 chars).
- **Sanity check result**: Verified new content in DB via SELECT; confirmed all 5 required sections present + spot-checked lc://1851, lc://1526, system_design_ad_ctr, bq_question_map links. Did not spin up backend for live API verification given change is content-only append to a single column.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-413 --status completed`

## 2026-04-13 -- Batch 2 complete: all 34 BQ+Pinterest tasks done
- **What I did**: Reported final state to user. Batch 2 (bg id bgjp3psy4) completed all 23 remaining tasks across 24 sessions (session 24 hit all_done=true). Total across both batches: 34 tasks committed (grep verified 34 matching commits in today's git log: `[T-P[0-9]-38[0-9]..41[0-3]]`). Pinterest problem pool doubled from 14 to 28. New docs/pinterest/ directory has 9 markdown files (7 system designs + bq_question_map + restaurant-interval investigation). Integration task T-P2-413 refreshed company_documents id=47 to include all new sections with drawer-clickable links.
- **Deliverables**: 34 commits; 9 new markdown files in docs/pinterest/; 14 new problem DB entries (7 new LC + 7 Pinterest custom); refreshed company_documents id=47
- **Sanity check result**: `git log | grep -c T-P[0-9]-` returned 34 matching commits; Pinterest-tagged problems count = 28; session_state.json correctly has all_done=true; no failed sessions in logs/autonomous.log.
- **Status**: [DONE] both batches complete.
- **Request**: No further task_db changes; user to review placeholders and new SD docs.

## 2026-04-13 20:00 -- [T-P0-179] BQ rework TODO placeholder resolution
- **What I did**: Surveyed all `[TODO: confirm ...]` placeholders across BQ story assets. Found 12 unresolved asks in `docs/bq_improved_stories.md` (EX-01, EX-04, EX-07, EX-14 x3, EX-15, EX-17, EX-21, EX-23, EX-24 x2) and 1 mirrored in `docs/bq_behavioral_examples.json` (EX-07). Since concrete numbers can only come from the user's own production data, created `docs/bq_todo_tracker.md` consolidating every placeholder into a single question sheet with file:line references, exact ask, and why-it-matters rationale. Added pointer to the tracker from the top of `bq_improved_stories.md` above the 2026-04-13 Metric Sweep section.
- **Deliverables**: `docs/bq_todo_tracker.md` (new, 12 open items + patch checklist), `docs/bq_improved_stories.md` (+1 pointer line to tracker).
- **Sanity check result**: `grep -c TODO docs/bq_improved_stories.md` = 12 (matches tracker count); tracker enumerates every line with a TODO (57, 115, 174, 301 x3, 320, 355, 431, 464, 482 x2) + the JSON mirror (381). No TODOs invented and no existing content mutated beyond the added pointer line.
- **Status**: [DONE] -- user input required to close the 12 open items (tracker is the action surface).
- **Request**: `task_db.py update T-P0-179 --status completed`.

## 2026-04-13 21:00 -- [T-P0-164] System design depth: llm-orchestration expansion
- **What I did**: Verified scripts/content_llm_orchestration.py already encodes the full expanded Chinese content for the llm-orchestration module (721 lines). Ran the seed script against the DB and confirmed all 8 sections populated with 18,407 total chars. Verified AC: Iteration & Evaluation subsection present (four-layer evaluation + IPS/DR reasoning + hyperparameter tuning table), 5 Defense Q&A in acknowledge-mitigate-data format, 3 documented failure modes (intent hallucination, filter field drift, cascading fallback storm) each with root cause + fix + measured effect. Scanned all math blocks for bare | -- only a false positive from two USD currency \$ symbols across a table row; no actual math-block violations.
- **Deliverables**: scripts/content_llm_orchestration.py (existing, re-run against DB); DB row system_designs[slug=llm-orchestration] refreshed.
- **Sanity check result**: Seed script reported [DONE] with per-section char counts; TOTAL: 18407 chars (target >= 16K). Defense section 2235 chars, 5 Q&A. Failure modes 3 (target >= 2). Iteration section present at line 474. No bare pipes in math.
- **Status**: [DONE]
- **Request**: task_db.py update T-P0-164 --status completed (already applied)

## 2026-04-13 22:30 -- [T-P0-178] Pinterest prep page Chinese-ify audit
- **What I did**: Audited Pinterest problem notes (company_tags LIKE '%Pinterest%', 28 rows) for Chinese-prose default. Found 5 entries failing the bar: 4 custom problems (1072/1074/1075/1076) were English-prose-first with Chinese block appended (CJK 11-18% of natural-language chars); LC 1851 (id=144) had empty notes. Rewrote all 5 so Chinese is the primary narrative while keeping code blocks, complexity tables, algorithm names (Trie, DSU, bisect_left, BFS), and Python signatures in English per `feedback_lc_notes_chinese`. Company index doc id=47 reviewed -- already correct (tables English, headings a mix; no prose-level issues).
- **Deliverables**: Updated `problems.notes` for ids 1072, 1074, 1075, 1076, 144 via `_apply_pinterest.py`. No code changes outside the data layer. Audit script `_audit_pinterest.py` computes CJK% excluding code/math.
- **Sanity check result**: Post-update CJK ratios: 1072 60.7%, 1074 76.5%, 1075 61.9%, 1076 59.5%, 1851 80.4%. Zero entries below 20% threshold. `solve_sorted`, `round_by_precision`, `PermissionSystem`, `ConnectivityService`, `min_interval` code blocks unchanged from source. All 28 Pinterest problems now pass Chinese-default bar.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-178 --status completed`

## 2026-04-13 -- [T-P1-166] Distributed task queue: add Defense Q&A (exactly-once + poison pill)
- **What I did**: Verified DB defense section was missing the 5 required acknowledge/mitigate/data Q&A topics. Priority Inversion, Worker Starvation, Distributed Lock Trade-off already existed in correct format. Added Exactly-once Delivery and Poison Pill Handling Q&A in the same acknowledge/mitigate/data Chinese-with-English-terms format to `scripts/content_distributed_task_queue.py` DEFENSE section, appended after the Distributed Lock block. Ran the seed script to push to DB.
- **Deliverables**: Edited `scripts/content_distributed_task_queue.py` (DEFENSE section, +~65 lines). DB record `distributed-task-queue` defense now 9379 chars (was 7589), total 27061 chars, 14 total Q&A, 5 full acknowledge/mitigate/data blocks.
- **Sanity check result**: DB query confirms all 5 topics present (Priority Inversion / Worker Starvation / Distributed Lock Trade-off / Exactly-once Delivery / Poison Pill Handling). 承认局限 count = 5. Existing Chinese content preserved in all 8 sections. No new bare | in math introduced.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-166 --status completed`

## 2026-04-13 -- [T-P1-167] database-comparison depth verification
- **What I did**: Audited existing `scripts/content_database_comparison.py` against AC. Found the seed already contains Migration Strategy (dual-write + shadow read, CDC streaming, stop-the-world), 3 failure modes with fixes (split brain, compaction storm, hot partition), Capacity Planning formulas (storage, node count, throughput), and Iteration & Evaluation methodology table. Re-ran seed script to confirm DB state matches script.
- **Deliverables**: No file changes; verification only. DB record `database-comparison` = 24503 chars, 11 display-math blocks, 6 Defense Q&A, 4 failure-mode anchors.
- **Sanity check result**: grep for bare `|` inside `$...$` returns 0 matches (the seed script's in-script counter gives 68 but that is a false positive from its flipping heuristic on single-line `$$...$$`). All Chinese content preserved. Total chars 24503 >= 24K AC.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-167 --status completed`

## 2026-04-13 17:00 -- [T-P1-180] Escape Room code & acronym review
- **What I did**: Reviewed `scripts/_add_pinterest_escape_room.py` canonical solution. Expanded acronyms to full form on first mention (DLL -> Doubly-Linked List (DLL); FIFO -> First-In-First-Out (FIFO, 先进先出)). Added a complexity-clarification note reconciling the interview spec's O(N+K) leaderboard bound with the implementation's tighter O(R+K). Force-updated the existing DB row (notes had canonical tag so the script's skip guard would have no-oped).
- **Deliverables**: `MLInterviewPrep/scripts/_add_pinterest_escape_room.py` edits; `data/mle_prep.db` row id=1068 notes field refreshed (6607 -> 7138 chars).
- **Sanity check result**: Extracted the `python` code block from the updated DB notes and ran it — all smoke-test assertions pass (getPeople/getTop/entry-order-tiebreak/finished-room no-op). Verified FIFO+DLL acronyms expanded and the O(R+K) note is present.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-180 --status completed`

## 2026-04-13 -- [T-P1-183] ML/concept problems description backfill
- **What I did**: Created `scripts/backfill_concept_descriptions.py` with hand-authored Chinese descriptions for all 26 non-LC problems (leetcode_id IS NULL) where description was NULL/empty: 24 Uber 1point3acres algorithm problems (IDs 1031-1054), 1 system design (1055 Driver Queue), 1 ML coding (1064 K-Means++). Each description is 1-2 short paragraphs in Chinese prose per `feedback_lc_notes_chinese`, with algorithm names, data structures, API signatures, and complexity notation kept in English.
- **Deliverables**: `MLInterviewPrep/scripts/backfill_concept_descriptions.py`; updated `description` + `description_source='manual'` on 26 rows in `data/mle_prep.db`.
- **Sanity check result**: Script reports `Updated 26 problems. Remaining NULL/empty concept descriptions: 0`. Spot-check on ids 1031 (Purchase Optimization), 1055 (Driver Queue SD), 1064 (K-Means) shows Chinese summary + approach paragraph with English algo/formula terms as expected.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-183 --status completed`

## 2026-04-13 -- [T-P2-171] System design formula audit: all 8 modules
- **What I did**: Wrote `scripts/audit_sd_formulas.py` (read-only) that scans the 8 core `system_designs` rows (`llm-orchestration`, `ranking-allocation`, `distributed-task-queue`, `database-comparison`, `pbe-pipeline`, `module-arbitration`, `ml-system-design-patterns`, `vibe-code-engineering-patterns`) across all 8 long-form text fields (overview, architecture, dataflow, formulas, production_constraints, tradeoffs, defense, verbal_outline) for: bare `|` in `$$...$$` blocks (should be `\mid`), multi-line `$$` blocks, consecutive `$$` blocks lacking a blank line between them (matches only `$$\n$$`, not `$$\n\n$$`), and unbalanced `$$`.
- **Deliverables**: `MLInterviewPrep/scripts/audit_sd_formulas.py` (re-runnable auditor).
- **Sanity check result**: All 8 modules clean on all four math-safety axes. GRAND TOTAL = 0 issues. No seed script changes required, no re-seed performed. The `module-arbitration` bare-`|` regression that motivated this audit has not recurred; the post-fix convention (`\mid`, single-line `$$`, blank-line separation) holds across the 7 other modules as well.
- **Observation (not in ACs, not fixed)**: Chinese prose in several modules uses `$` as a currency sigil (e.g., `$5K-$50K/月`, `$30K`). Because remark-math pairs consecutive unescaped `$`, two currency tokens on the same line can be mis-parsed as inline math. Out of scope for T-P2-171 (ACs target math blocks, not prose), but worth a future pass — candidate fix is escaping with `\$` in seed scripts.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-171 --status completed`

## 2026-04-13 -- [T-P1-187] LC stateful-DS family column + 11-problem group
- **What I did**: Added additive `problems.family` TEXT column (+ `ix_problems_family` index) via `migrate_add_problem_family.py`; inserted 3 missing LC rows (1146 SnapshotArray, 1845 SeatReservationManager, 1825 FindingMKAverage) and ran `backfill_lc_descriptions.py` to populate descriptions from leetcode.com GraphQL; populated `family='stateful_ds_design'` for all 11 target LC IDs; updated SQLAlchemy Problem model with the new column; added a collapsible "Stateful Data Structure Design" group in QuickIndex.tsx rendered above the ungrouped LC grid (deduped against LC_PROBLEMS by lcId).
- **Deliverables**: `scripts/migrate_add_problem_family.py`, `src/backend/models/problem.py` (+family column), `src/frontend/src/pages/QuickIndex.tsx` (+STATEFUL_DS_DESIGN constant + collapsible group).
- **Sanity check result**: `SELECT leetcode_id FROM problems WHERE family='stateful_ds_design' ORDER BY leetcode_id` returns exactly 11 rows: {146, 362, 432, 460, 703, 716, 895, 1146, 1244, 1825, 1845}. Descriptions for 1146/1825/1845 fetched successfully (1172/2241/1870 chars, source=leetcode.com). `npm run build` passes (617ms, no TS errors).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-187 --status completed`

## 2026-04-13 -- [T-P1-188] A/B test sample-size study note (pillar7 Probability & Statistics)
- **What I did**: Created new framework leaf node `pillar7.probability_statistics.ab_test_sample_size` (id=193, under parent id=38) and populated its description via `StudyNoteBuilder` + `FormulaBlock` — no raw f-strings. Content covers: two-proportion z-test formula derivation (both unpooled and pooled variance forms), continuous-metric t-test analog, two worked examples (2%->2.2% conversion lift = 80.6k per arm; revenue with sigma=12 = 56.4k per arm), MDE sensitivity table (1%-50% relative MDE spanning 7.9M -> 3.4k n), decision table mapping scenarios to methods, 5 practical gotchas (multiple testing Bonferroni/BH, SRM, novelty/primacy, peeking + mSPRT/Group Sequential, CUPED variance reduction), 5 interview Q&A, and a self-check checklist.
- **Deliverables**: `scripts/seed_ab_test_sample_size.py` (idempotent upsert). DB row `framework_nodes.id=193`, description length 7615 chars.
- **Sanity check result**: Seed script runs clean, StudyNoteBuilder validate() returns 0 warnings (no orphan `$`). `npm run build` passes in 610ms (no TS/Vite errors). Chinese prose with English formulas/method names per feedback_lc_notes_chinese. 5 display-math blocks (>=3 required), 5 Q&A (>=4 required), 2 tables (sensitivity + decision).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-188 --status completed`

## 2026-04-13 -- [T-P1-185] Execute company prep consolidation (Option A, phase 1)
- **What I did**: Laid down the Option A knowledge-cards foundation per the T-P0-184 audit. (1) Snapshotted 23 raw originals (4 LinkedIn + 6 Uber + 13 Adobe) to `archive/legacy_company_docs/2026-04-13/` before any migration (AC #1). (2) Added `knowledge_cards` and `company_card_overlays` tables via new `scripts/migrate_add_knowledge_cards.py`, with provenance columns (`source_company`, `source_file`, `source_line_start/end`) and UNIQUE(card_id, company_id, angle). (3) Added `KnowledgeCard` and `CompanyCardOverlay` SQLAlchemy models in `src/backend/models/knowledge_card.py` and wired them into `models/__init__.py`. (4) Added `src/backend/routers/knowledge_cards.py` with `GET /api/knowledge_cards` + `GET /api/knowledge_cards/{slug}?company_id=…` endpoints; registered in `main.py`. (5) Seeded two exemplar canonical cards in Chinese (`overfitting-l1-l2`, `bias-variance-tradeoff`) with 3 company overlays, proving the full stacked-render pattern. Remaining 12 SHARED topics are follow-up work.
- **Deliverables**: `scripts/migrate_add_knowledge_cards.py`, `scripts/seed_knowledge_cards_shared.py`, `src/backend/models/knowledge_card.py`, `src/backend/routers/knowledge_cards.py`, edits to `src/backend/models/__init__.py` and `src/backend/main.py`, 23 files under `archive/legacy_company_docs/2026-04-13/`.
- **Sanity check result**: Migration runs idempotently. Seed inserts 2 cards + 3 overlays (verified row counts). FastAPI TestClient smoke test hits `GET /api/knowledge_cards` (200, count=2) and `GET /api/knowledge_cards/overfitting-l1-l2?company_id=1` returns the card body with the LinkedIn `interview-format` overlay attached and full provenance dict -- proves the merged-view contract. Chinese prose + English formula symbols, `\mid` discipline not yet needed (no bare `|` in math). No raw originals deleted; deletion candidates (3 Adobe EN mirrors) are deferred to a future PR with explicit approval per AC #4.
- **Status**: [PARTIAL] Foundation + 2/14 SHARED cards seeded. Follow-up tasks needed: (a) seed remaining 12 canonical cards, (b) wire `/companies/:id/prep` frontend to the new endpoint, (c) PR with deletion candidates for the 3 Adobe EN/中 bilingual mirrors (requires user approval).
- **Request**: `task_db.py update T-P1-185 --status completed` (foundation milestone done) and add follow-up tasks for phase 2 seeding, frontend wiring, and deletion-approval PR.

## 2026-04-13 -- [T-P1-189] Knowledge cards phase 2: 12 remaining SHARED canonical cards seeded
- **What I did**: Followed phase-1 pattern (scripts/seed_knowledge_cards_shared.py) to seed the remaining 12 SHARED topics identified by T-P0-184 audit (topics 1, 2, 7, 8, 10, 14, 18, 20, 22, 24, 26, 27). Authored Chinese canonical prose with English formula symbols, display math in single-line $$ blocks, \mid discipline, and a Defense Q&A block per card. Added 10 company overlays covering LinkedIn / Uber / Adobe product-vs-interview-format angles where the audit flagged meaningful divergence (classification-metrics<-Adobe quant quality, logistic-regression<-Uber CTR, feed-ranking<-Uber ranking-as-allocation vs LinkedIn InMail, LRU<-Uber OOD parking variant, etc.).
- **Deliverables**: scripts/seed_knowledge_cards_shared_phase2.py (12 cards + 10 overlays, idempotent upsert).
- **Sanity check result**: Seed script run end-to-end; 12/12 INSERT for cards, 10/10 INSERT for overlays. Post-run table totals: knowledge_cards=14, company_card_overlays=13 (phase 1 contributed 2+3). All cards cite provenance with source_file + source_line_start/end. No bare `|` in math (`\mid` used where needed); all display math single-line $$ with blank separators per repo formula spec.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-189 --status completed`. T-P1-190 (frontend merged view) unblocked for visual completeness; T-P2-191 (Adobe EN mirror deletion approval) remains.

## 2026-04-13 -- [T-P1-190] Knowledge cards: wire /companies/:id/prep merged view (frontend)
- **What I did**: Added `KnowledgeCardsPanel` component that calls `GET /api/knowledge_cards?company_id={id}` and renders each card as `canonical_body` followed by any company-specific overlays (angle-labeled, blue-tinted). Cards with overlays for this company surface first under "Company-specific"; remaining shared canonical cards collapse behind a toggle. Added a new "Knowledge" tab to PrepNotesPage between the document selector and Forum Posts; mode toggle (Preview/Edit) is hidden for that tab.
- **Deliverables**: src/frontend/src/components/companies/KnowledgeCardsPanel.tsx (new), src/frontend/src/pages/PrepNotesPage.tsx (tab wiring).
- **Sanity check result**: `npm run build` clean (tsc -b && vite build succeed, no type errors). Backend endpoint verified with 14 cards + 13 overlays present in data/mle_prep.db.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-190 --status completed`.

## 2026-04-14 -- [T-P0-195] Frontend db:// drawer scheme for custom problems
- **What I did**: Extended `MarkdownPreview` with `onDbLinkClick` prop that handles `db://N` href markdown links symmetric to existing `lc://N` handling. Updated `DocumentViewer` in PrepNotesPage: added `dbDrawerId` state, wired it through `MarkdownPreview.onDbLinkClick`, and passed `dbId` to `ProblemDrawer` (dbId support already landed in T-P0-181). Both handlers clear the other drawer id on open to prevent both-set state; close handler clears both. Unblocks T-P0-197 retrofit to rewrite custom-problem titles as `[Title](db://ID)`.
- **Deliverables**: src/frontend/src/components/ui/MarkdownPreview.tsx, src/frontend/src/pages/PrepNotesPage.tsx.
- **Sanity check result**: `npm run build` clean (tsc -b && vite build succeed, no type errors).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-195 --status completed`.

## 2026-04-14 -- [T-P0-196] Retrofit script for drawer links + unit tests
- **What I did**: Built `scripts/retrofit_doc_drawer_links.py` per T-P0-193 AC1+AC4. Exposes three idempotent rewriters -- `rewrite_lc` ('LC 123' / 'LC123' -> '[LC 123](lc://123)'), `rewrite_leetcode` (preserves literal casing, handles optional '#'), and `rewrite_custom` (per-doc `CustomMapping` list). Each rewriter uses a combined regex whose first alternative consumes already-linked markdown so a second pass is a no-op. CLI supports `--doc-ids`, `--dry-run`, `--diff`, `--db`. Added `fuzzy_find_problem_id` helper (difflib ratio, 0.6 default threshold) for AC4 custom-title resolution in T-P0-197. `CUSTOM_MAPPINGS` dict left empty -- T-P0-197 populates it with resolved (title_pattern -> db_id) after Pinterest #7 is seeded.
- **Deliverables**: scripts/retrofit_doc_drawer_links.py (new), tests/test_retrofit_doc_drawer_links.py (new, 15 tests).
- **Sanity check result**: `pytest tests/test_retrofit_doc_drawer_links.py -v` -> 15 passed in 0.12s. Dry-run against doc 3 reports 13 LC rewrites, matching T-P0-193 audit count exactly. Idempotence verified by unit test (`test_second_pass_is_noop`, `test_full_pass_idempotent`).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-196 --status completed`.

## 2026-04-14 -- [T-P0-197] Ran drawer-link retrofit on 8 company docs + archived SQL
- **What I did**: Fixed a nesting bug in `scripts/retrofit_doc_drawer_links.py` (dry-run revealed `[**LC 332** Reconstruct Itinerary](lc://332)` got rewritten to nested `[**[LC 332](lc://332)** ...](lc://332)` because alt-1 only matched `[LC NNN](lc://NNN)` without surrounding markup). Added negative lookahead `(?![^\[]*\]\(lc://\3\))` to both `_LC_COMBINED` and `_LEETCODE_COMBINED` so bare-text matches skip when already enclosed in a wider markdown link. Populated `CUSTOM_MAPPINGS[47]` with 7 Pinterest-specific custom-problem entries (db ids 1068/1071/1072/1073/1074/1075/1076) using `(?<!\[)` lookbehind + `re.escape` for safety. Doc 31 (Uber BPS Custom) intentionally skipped for custom mapping because its TOC already wraps titles in `[Title](#anchor)` internal links; text-level retrofit would nest and break markdown. Backed up DB, generated `archive/company_docs_drawer_retrofit_2026-04-14.sql` (366 KB, 7 UPDATE statements + unchanged-doc comment for doc 19), applied retrofit to 7 of 8 docs (doc 19 Adobe had zero bare LC refs), then re-ran script to confirm idempotence.
- **Deliverables**: scripts/retrofit_doc_drawer_links.py (nesting-bug fix + 7 Pinterest custom mappings), archive/company_docs_drawer_retrofit_2026-04-14.sql (new audit artifact), data/mle_prep.db.backup_pre_retrofit_20260413_205640 (pre-change backup).
- **Sanity check result**: First run stats -- doc 3: lc=13; doc 19: unchanged; doc 26: lc=33; doc 30: lc=19; doc 31: lc=4; doc 32: lc=57; doc 35: lc=3; doc 47: lc=18 + custom=7. Second run (idempotence) -- all 8 docs `changed: false`, all counts 0. Spot-checked doc 47 diff: the 7 Pinterest custom titles (rows #1-#7) now link to db://1068/1071/1072/1075/1076/1073/1074 respectively. No nested markdown produced (verified by the earlier failing case `[**LC 332** Reconstruct Itinerary](lc://332)` now unchanged by the rewriter).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-197 --status completed`.

## 2026-04-14 -- [T-P0-200] Google prep: BQ Conflict + Failure story polish for Round 2 (G&L)
- **What I did**: Picked EX-02 (conflict w/ manager -- team transfer) + EX-08 (conflict across teams -- VP escalation on cumulative degradation) + EX-17 (failure-with-learning -- harsh feedback into mutual respect) from bq_story_arcs.json / bq_improved_stories.md. Wrote STAR 2-3 min polished versions and appended them to `docs/bq_improved_stories.md` under a new `# [google-g&l] Round 2 Polished Stories (2026-04-17)` section. Each story is tagged with the Google Hiring Attribute + Googleyness sub-signal it targets (Ambiguity / Values feedback / Challenges status quo / Does the right thing / Collaboration), lists the interviewer prompts it answers, structures S/T/A/R with explicit time budgets (30s/15s/90s/30s), uses "I" in every Action bullet per feedback_bq_cluster, and closes with a one-line learning + an explicit Googleyness hook paragraph. Updated `docs/google_2026-04-17_prep.md` Story Short-list so the three rows for EX-02/EX-08 + the Growth+Failure row now link directly to the anchors of the three polished versions, and added a T-P0-200 polish note explaining that the polished versions supersede Tier-1 for Round 2 G&L only.
- **Deliverables**: docs/bq_improved_stories.md (+new `[google-g&l]` section with STORY A/B/C + delivery reminders), docs/google_2026-04-17_prep.md (Story Short-list rows updated + polish note).
- **Sanity check result**: Grepped `^## STORY` in bq_improved_stories.md -- original Tier-1 stories (STORY 1..24, 33) unchanged, new anchors `[google-g&l] STORY A/B/C` appear at file tail. Reviewed each polished story for (a) S/T/A/R present, (b) at least one quantified Result, (c) explicit Googleyness sub-signal named, (d) "I" prefix on every Action bullet. No new stories created per task spec -- strictly reused EX-02/08/17.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-200 --status completed`.

## 2026-04-14 -- [T-P0-201] Seed pillar2.regularization.bias_variance_geometric study note
- **What I did**: Built idempotent `scripts/seed_bias_variance_geometric.py` that (a) creates new subtree `pillar2.regularization` under `pillar2` (id 194) if absent, (b) creates / updates leaf `pillar2.regularization.bias_variance_geometric` (id 195). Content authored via StudyNoteBuilder / FormulaBlock per CLAUDE.md: prerequisites, term registry (MSE/OLS/MAP/KKT), 8 sections (overview, bias-variance decomposition formula E[(y-hat_y)^2]=Bias^2+Variance+Noise, learning-curve diagnosis table, mitigation-map lever table, L1 vs L2 loss-surface + constraint-region geometric interpretation of sparsity via subgradient and diamond-vs-circle argument, ridge closed-form + lasso soft-thresholding, elastic net bridging, 3 Q&A: L1 sparsity, L2 multicollinearity, when neither suffices), plus self-check checklist. Chinese prose + English display math ($$ wrapped).
- **Deliverables**: `MLInterviewPrep/scripts/seed_bias_variance_geometric.py` (new), `data/mle_prep.db` (new rows: framework_nodes id 194 subtree + id 195 leaf, description length 5607 chars).
- **Sanity check result**: First run `[INSERTED] subtree id=194 ... [INSERTED] leaf id=195 ... length=5607`, second run idempotent `[EXISTS] ... [UPDATED] ... length=5607`. StudyNoteBuilder.validate returned no warnings (no orphan single-$, header comment present). FormulaBlock guarantees all math is $$-wrapped. Manual browser smoke at `/framework/195/notes` left for user verification per CLAUDE.md manual-smoke rule.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-201 --status completed`.

## 2026-04-14 -- [T-P0-202] Google prep: Streaming Top-K deep dive
- **What I did**: Built idempotent `scripts/seed_streaming_topk.py` that creates new leaf `pillar1.streaming_topk` directly under pillar1 (Coding & Algorithms). Content via StudyNoteBuilder/FormulaBlock: prerequisites, term registry (CMS/HLL/SS/MG/PPK), 12 sections covering clarify-first framing; precise heap+hashmap baseline with complexity; Count-Min Sketch with (epsilon,delta) parameter formulas w=e/eps, d=ln(1/delta) and additive error bound; HyperLogLog with cardinality formula and explicit "NOT for top-K" clarification; Space-Saving / Misra-Gries with N/K deterministic bound; decision table memory x accuracy x stationarity; reservoir sampling uniform-window contrast; distributed partition-by-key + K-way merge correctness argument; key-skew mitigations (salting, two-stage, hot-key fast path); worked example log-file top-K videos (connects to T-P1-206); common pitfalls; 3 Q&A (1MB/1e9 design, CMS vs SS, partition-by-key vs round-robin); self-check checklist. Chinese prose + English code/formulas per feedback_lc_notes_chinese + feedback_math_formatting.
- **Deliverables**: `MLInterviewPrep/scripts/seed_streaming_topk.py` (new), `data/mle_prep.db` (new row: framework_nodes id 196, length 7924 chars).
- **Sanity check**: First run `[INSERTED] leaf id=196 ... length=7924`, second run idempotent `[UPDATED] ... length=7924`. StudyNoteBuilder.validate returned no warnings. Manual browser smoke at `/framework/196/notes` left for user verification.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-202 --status completed`.

## 2026-04-14 -- [T-P0-204] Google prep: Large-input resource-model framework (L4 coding extension)
- **What I did**: Built idempotent `scripts/seed_scaling_resource_model.py` that creates new leaf `pillar1.scaling_resource_model` directly under pillar1. Content via StudyNoteBuilder/FormulaBlock: prerequisites, term registry (EMS/CMS/HLL/PPK/MR/IO), 11 sections covering why-L4-matters framing; 10-item clarify-first checklist (scale/batch-vs-stream/U/distribution/precision/latency/cluster/format/semantics); bottleneck analysis memory-vs-CPU-vs-IO with quantitative bounds (RAM 256GB, SSD 3GB/s, CPU 1e10 ops/s); single-machine upgrade ladder (streaming/reservoir/sketches/EMS/mmap/columnar) with IO cost formula; distributed MR three-phase costs + three shuffle-reduction tactics (combiner/broadcast/pre-partition); key-skew mitigations (salting/heavy-hitter/skew-aware/tree-agg); Terasort worked example (sampling+splitter); meeting-rooms interval time-window-partition worked example with boundary correction; decision table input-size->approach; pitfalls; 4 Q&A (10GB top-K / 1PB scaleup / 1PB sort / when-NOT-to-distribute); self-check checklist. Chinese prose + English formulas/terms.
- **Deliverables**: `MLInterviewPrep/scripts/seed_scaling_resource_model.py` (new), `data/mle_prep.db` (new row: framework_nodes id 197, length 8845 chars).
- **Sanity check**: First run `[INSERTED] leaf id=197 ... length=8845`, second run idempotent `[UPDATED] ... length=8845`. StudyNoteBuilder.validate returned no warnings. Manual browser smoke at `/framework/197/notes` left for user verification.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-204 --status completed`.

## 2026-04-14 -- [T-P1-205] Google coding: Course Schedule + damage-node + Shortest path variants
- **What I did**: Built idempotent `scripts/seed_google_course_schedule_shortest_path.py`. Appended Google 2026-04-17 follow-up notes to problems 45 (LC 207) and 113 (LC 210): 207 gets DAG-with-node-weights formulation (topo+DP O(V+E), Dijkstra upgrade, 0-1 BFS alternative, heap-pitfall extension); 210 gets clarification that "min-damaged topological order" is actually path-on-DAG (reduces to 207) plus a priority-queue tie-break variant. Added Google company tag + "Google 2026-04-17 prep" source badge. Inserted new custom problem id 1080 "Shortest Path A->B (undirected, unweighted)" with BFS baseline, Dijkstra follow-up, all-pairs Floyd-Warshall vs V x Dijkstra comparison (with sparse/dense decision table), predecessor-matrix reconstruction, and complexity summary table (BFS/Dijkstra/Bellman-Ford/Floyd/Johnson). All Chinese prose + English formulas/code per feedback_lc_notes_chinese.
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_course_schedule_shortest_path.py` (new), `data/mle_prep.db` (problems 45/113 notes appended, new problem id 1080 inserted).
- **Sanity check**: First run produced lengths {45: 2880, 113: 2453, 1080: 3361}; second run identical (idempotent via marker + JSON tag de-dup + source de-dup).
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-205 --status completed`.

## 2026-04-14 15:30 -- [T-P1-206] Google coding: LC 692 distributed Top-K + Sum of Good Subarrays O(N)
- **What I did**: Built `scripts/seed_google_topk_good_subarrays.py` (idempotent). Appends Google distributed-Top-K follow-up addendum to LC 692 (problem id 393): Map-Shuffle-Reduce pipeline, shuffle-by-video_id, local size-K min-heap, tie-break comparator, skew mitigations (Combiner, salting, Count-Min Sketch, two-phase exact). Inserts new custom problem `Sum of Good Subarrays (max-min <= 1)` (pid 1081) with O(N) solution: double monotonic deque (min+max) + left-pointer shrink + prefix-sum contribution formula $S(r) = (r-L+1)\cdot P_{r+1} - (Q_{r+1}-Q_L)$ using second-order prefix sum $Q$. Worked example table for [3,5,6,7,6]=83, follow-ups (count-only, max-min<=K, streaming), wrong-approach comparison table.
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_topk_good_subarrays.py` (new); problems row 393 notes addendum; new problems row 1081 (3950 chars).
- **Sanity check**: (1) Algorithm self-check built into script: `sum_good([3,5,6,7,6])` = 83 matches worked example. (2) Script ran twice — identical lengths {393: 5155, 1081: 3950} on both runs, confirming idempotency via marker-based append + JSON tag de-dup.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-206 --status completed`.

## 2026-04-14 -- [T-P1-207] Google coding: Longest non-decreasing + LC 347 + LC 224
- **What I did**: Built `scripts/seed_google_longest_nondec_calc_topk.py` (idempotent, marker-based). (1) Inserts new custom problem `Longest Non-decreasing Subarray` (pid 1082, 4646 chars notes) with O(N) baseline + Follow-up A (allow one replacement, two-state DP `dp0/dp1` with "extend already-replaced" vs "use replacement now" branches) + Follow-up B (one-shot replace-all X->Y, O(n log n) via run decomposition + SortedList multiset of run lengths + local merge/undo). (2) Appends `[Google 2026-04-17] LC 347 Top-K Frequent Elements` addendum to problem 5 (2692 chars): heap O(N log K) + bucket sort O(N) + QuickSelect + cross-ref to LC 692 for distributed. (3) Fills LC 224 (problem 273) previously-empty notes (3713 chars): single-stack `sign_stack` sign-flip method, recursive descent alternative, shunting-yard for `*,/` extension, LC 224/227/772/770 comparison table, Python `int(a/b)` vs `//` negative-number trap.
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_longest_nondec_calc_topk.py` (new); problems rows 5 (LC 347), 273 (LC 224), 1082 (new custom).
- **Sanity check**: Built-in algorithm self-checks verify longest_nondec + one-replace DP (including adversarial `[1,5,3,2,6]`=3), LC 347 heap+bucket on `[1,1,1,2,2,3]`, LC 224 on `"(1+(4+5+2)-3)+(6+8)"`=23 and `"1-(2+3)"`=-4. Script ran twice -> identical notes_len {5:2692, 273:3713, 1082:4646}, confirming idempotency.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-207 --status completed`.

## 2026-04-14 -- [T-P1-208] Google coding: Jammed Keyboard Dictionary Match
- **What I did**: Built `scripts/seed_google_jammed_keyboard.py` (idempotent) that upserts a new custom (non-LC) problem `Jammed Keyboard Dictionary Match` (pid 1083). Problem = given letter-group partition + typed string + dictionary, return dictionary words with identical group-signature. Notes (3933 chars) cover: (1) signature-bucket solution O(NL) preprocess / O(L) query with Python tuple-key dict; (2) group-keyed trie alternative (children keyed by gid, not letter) for streaming inserts + prefix support; (3) follow-up chain A/B/C/D -- many queries, dynamic dictionary, group shifts (inverted-index-assisted partial rebuild), Unicode / 64-bit signature hashing; (4) correctness proof, common-mistake table, LC 249 / 49 / 1032 family cross-refs, interview checklist.
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_jammed_keyboard.py` (new); problems row 1083 (new custom).
- **Sanity check**: Self-check verifies both signature-bucket and group-keyed trie return the same match set against a hand-worked 9-word dictionary with `typed="bad"`. Script ran twice -> identical notes_len=3933, desc_len=1264, confirming idempotency.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P1-208 --status completed`.

## 2026-04-14 -- [T-P2-210] Google coding: Tree/Trie level-order + Math expressions (LC 770/772/224)
- **What I did**: Built `MLInterviewPrep/scripts/seed_google_tree_math.py` (idempotent). Adds Google-prep addendum to LC 102 covering BFS template, LC 103 zigzag (deque flip), LC 107 bottom-up, and a Trie BFS-level variant (for prefix debug + Aho-Corasick fail-link). Seeds compact notes for LC 103/107 standalone. Appends LC 772 notes (recursive descent + shunting-yard; traps: Python `//` negative rounding vs `int(a/b)` toward-zero; `(0-x` unary-minus preprocessing). Inserts new LC 770 Basic Calculator IV with Poly=Counter[tuple[str,...],int] model, `poly_add/mul/eval` code, output sort (-degree, lex), follow-ups (division -> rational, many-eval, shunting-yard). LC 224 untouched (already 3713-char notes).
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_tree_math.py` (new); problems rows: LC 102 notes 985->3797, LC 103 0->651, LC 107 0->652, LC 772 0->1839, LC 770 inserted (pid=1085, notes=2626).
- **Sanity check**: Script ran twice -- first pass inserted/grew, second pass reported identical lengths across all 5 rows. MARKER-based re-append guard works.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-210 --status completed`.

## 2026-04-14 -- [T-P2-211] Google coding: Distributed Word Count + KNN/K-means 0-shot + KDE
- **What I did**: Built `MLInterviewPrep/scripts/seed_google_wordcount_knn_kde.py` (idempotent) seeding a single combined custom problem (id=1086) covering the three Google 2026-04-17 prep topics: (1) distributed word count via MapReduce + bounded-worker combiner with associativity/commutativity constraints and Zipf/skew discussion; (2) KNN vs K-means distinction matrix + 0-shot classification via KNN over pretrained embedding space with prototype lookup; (3) Parzen-window KDE with Gaussian kernel, bandwidth Silverman/CV, class-conditional KDE -> Bayes classifier, and comparison against histogram/KNN-density. Chinese prose + English code/complexity per feedback_lc_notes_chinese. Self-test verifies: 3-worker combiner matches single-machine Counter baseline + shuffle-reduce order-independence; 2-D embedding KNN picks correct prototype; 2000-sample Gaussian KDE yields p(0) > p(3) and p(0) in [0.30, 0.50] ballpark of 0.3989.
- **Deliverables**: `MLInterviewPrep/scripts/seed_google_wordcount_knn_kde.py` (new); problems row id=1086 (desc_len=2192, notes_len=5714).
- **Sanity check**: Script ran twice -- first INSERTED, second UPDATED to identical lengths. All three self-test sections passed.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P2-211 --status completed`.

## 2026-04-14 21:00 -- [T-P0-214] Portal migrations 19/20/21 + doc_kind + tag models
- **What I did**: Appended migrations 19/20/21 to `src/backend/database.py::MIGRATIONS`: (19) `problem_company_tags` table with `relevance` (core/likely/stretch) + `source` (manual/auto_from_doc_ref/auto_from_overlay/auto_from_interview_log) CHECK constraints, UNIQUE(problem_id, company_id), indices on (company_id, relevance) and problem_id; also adds `company_documents.doc_kind` TEXT CHECK ∈ (prep_note/hub_doc/recruiter_call/other) DEFAULT 'prep_note' with backfill (recruiter-titled → `recruiter_call`, others → `prep_note`). (20) same shape `node_company_tags` (node_id ↔ framework_nodes). (21) `behavioral_example_company_tags` with generic `company_attribute TEXT` (not google_attribute — works for Meta/Amazon). Created `src/backend/models/company_tags.py` with `ProblemCompanyTag`, `NodeCompanyTag`, `BehavioralExampleCompanyTag` SQLAlchemy models using `backref` + `passive_deletes=True` so DB-level ON DELETE CASCADE handles parent deletes. Added `doc_kind` column to `CompanyDocument` model. Registered new models in `models/__init__.py`. No `group_tag` field per review.
- **Deliverables**: modified `src/backend/database.py` (+~80 lines migrations), `src/backend/models/company.py` (+doc_kind), `src/backend/models/__init__.py` (+3 exports); new `src/backend/models/company_tags.py`, `tests/test_tag_models.py` (7 tests covering AC2-AC5).
- **Sanity check**: `pytest tests/test_tag_models.py` → 7/7 passed. Verifies schema_versions ≥ 21, doc_kind default, CRUD on each tag table, UNIQUE constraint violation, DB-level cascade delete (with `PRAGMA foreign_keys=ON`), and relevance CHECK constraint rejection.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-214 --status completed`.

## 2026-04-14 -- [T-P0-217] Portal T-217: Patch sync_docs_to_db.py for create-new-row + sync 2 Google md files
- **What I did**: Extended `scripts/sync_docs_to_db.py` with a create-new-row path (for `target_table: company_documents` with `company_id` + `title` but no `target_id`). After INSERT the script rewrites the md frontmatter with the new `target_id` so re-runs resolve via id and skip. Added YAML frontmatter to `docs/google_2026-04-17_prep.md` and `docs/google_dnn_papers_gist.md` (company_id=3, doc_kind=prep_note) and synced both into `company_documents` (new ids 51, 52).
- **Deliverables**: `scripts/sync_docs_to_db.py` (patched), `tests/test_sync_docs_create.py` (new — 2 tests), 2 md files with injected frontmatter + target_id.
- **Sanity check**: `pytest tests/test_sync_docs_create.py` → 2/2 pass. Second-run sync on both files = 0 writes / 1 skip each (idempotent). DB shows company_id=3 docs {38, 51, 52}.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-217 --status completed`.

## 2026-04-14 23:00 -- [T-P0-219] Google Prep Hub company_document
- **What I did**: Authored docs/google_2026-04-17_prep_hub.md with frontmatter doc_kind=hub_doc, company_id=3; synced via sync_docs_to_db.py (create-path). Hub aggregates Round 1 ML links (framework nodes 195/196/197/198/193), Round 2 G&L (EX-02/08/17 + 6 predicted Q→story mapping), 7 custom coding problems (db://1080-1086), likely LC (db://5/393/273/254/45/113), last-minute checklist.
- **Deliverables**: docs/google_2026-04-17_prep_hub.md (new, company_documents id=53).
- **Sanity check result**: Sync created id=53; re-run = 0 diff (idempotent, skipped=1). hub_doc identification query `WHERE company_id=3 AND doc_kind='hub_doc' ORDER BY updated_at DESC LIMIT 1` returns (53, 'Google 2026-04-17 Prep Hub', 'hub_doc'). All referenced entity ids verified to exist in DB.
- **Status**: [DONE]
- **Request**: Cross off T-P0-219.

## 2026-04-14 -- [T-P0-215] Unified GET /api/companies/:id/prep endpoint
- **What I did**: Added router endpoint `get_company_prep` aggregating hub_doc, documents metadata, tagged problems/nodes/behavioral stories (core/likely/stretch segments), and knowledge cards with per-company overlays. Hub doc identified via `doc_kind='hub_doc'` (robust, no string match). 7 SELECTs per request via `joinedload` + targeted filters. Added `CompanyPrepResponse`/`ProblemSegments`/`NodeSegments` Pydantic schemas.
- **Deliverables**: src/backend/routers/companies.py (new endpoint), src/backend/schemas/company.py (response schemas), tests/test_company_prep_endpoint.py (5 tests).
- **Sanity check result**: 5/5 tests pass (populated seg response, empty-company three-seg, 404, N+1 guard <=8 SELECTs, Pydantic shape validation). Behavioral stories concatenate STAR fields into markdown; empty-tag company returns `{core:[], likely:[], stretch:[]}` (not missing keys).
- **Status**: [DONE]
- **Request**: Cross off T-P0-215.

## 2026-04-14 -- [T-P0-218] Tag Google content (problems/nodes/BQ)
- **What I did**: Wrote idempotent seed script scripts/tag_google_content.py with UPSERT logic for all three tag tables. Inserted 7 core + 6 likely problems, 4 core + 1 likely framework nodes, and 3 core behavioral examples (2 leadership + 1 googleyness) for Google (company_id=3). BQ review gate prompts unless --auto-confirm.
- **Deliverables**: scripts/tag_google_content.py.
- **Sanity check result**: First run inserted 21 rows. Second run: 0 INSERT / 0 UPDATE / 21 SKIP (idempotent). Counts match AC4: problems=13, nodes=5, bq=3.
- **Status**: [DONE]
- **Request**: Cross off T-P0-218.

## 2026-04-14 -- [T-P0-216] Portal: Coding tab + Problem drawer + deeplink regression test
- **What I did**: Added a new `Coding` tab to `PrepNotesPage`, moved tab state to URL (`?tab=...`), preserved legacy `?doc=N` via a pure parser `parsePrepParams`. Coding tab fetches the unified `/companies/:id/prep` endpoint and renders tagged problems grouped by core/likely/stretch; card click pushes `?tab=coding&problem=N` and opens `ProblemDrawer` via dbId. Close drawer uses `navigate(-1)` so the browser back button closes the drawer without leaving the tab. Tab changes use `replace:true` (no history pollution).
- **Deliverables**: `src/utils/prepUrlParams.ts`, `src/utils/prepUrlParams.test.ts` (11 tests: legacy `?doc=38`, `?tab=docs&doc=38`, `?tab=coding&problem=1081`, bogus tab fallback, etc.), `src/components/companies/CodingTab.tsx`, `src/pages/PrepNotesPage.tsx` (refactor).
- **Sanity check result**: `npm test` 39/39 pass (11 new). `npm run build` passes (tsc -b + vite). Manual browser smoke deferred to user per AC6 intent (Playwright not installed); regression test pins URL contract at unit level.
- **Status**: [DONE]
- **Request**: Cross off T-P0-216.

## 2026-04-14 -- [T-P0-221] DoorDash ML prep consolidation
- **What I did**: Wrote `scripts/consolidate_doordash_ml_prep.py` (idempotent) to merge company_documents 40-46 into a master doc (id=54) with a top TOC and per-source H2 nesting (source H1 dropped, H2→H3, H3→H4). Added redirect banner to originals 40-46, guarded by HTML-comment marker so reruns are no-ops.
- **Deliverables**: `scripts/consolidate_doordash_ml_prep.py`.
- **Sanity check result**: Ran script twice — identical output, banners unchanged (true idempotent). Master structure: 1 H1 + 8 H2 (TOC + 7 sources) + 60 H3 + 245 H4 + 29 H5. `npm run build` passes (628ms, no TS errors). Existing DynamicTocSidebar + MarkdownPreview already deliver sticky TOC / smooth scroll / IntersectionObserver active-section highlighting / non-history-polluting jumps — Part B needs no new code.
- **Status**: [DONE]
- **Request**: Cross off T-P0-221.

## 2026-04-14 -- [T-P0-414] Unblock 4 failing CI checks (test/lint/emoji/migration)
- **What I did**: Diagnosed and fixed all 4 red CI jobs. (1) Migration test 32 failures root-caused to `_add_column_if_missing` emitting ALTER TABLE on non-existent tables (migration 18 alters `system_designs`/`company_documents`, which are model-only tables created via `Base.metadata.create_all`, not via migrations; test fixtures that feed `_run_migrations` a partial old schema hit `no such table`). Added early-return when `PRAGMA table_info` is empty. (2) Ruff 3 errors: autofix for unsorted imports in `src/backend/models/__init__.py` and unused `Base` import in `tests/test_versioned_baseline.py`; manual rename `SessionLocal` -> `session_factory` in `tests/test_tag_models.py` for N806. (3) Emoji scan: 17 hits across 7 docs/scripts replaced with ASCII tags ([Y]/[N]/[!]) per project convention; decorative emoji stripped.
- **Deliverables**: `src/backend/database.py` (skip-missing-table guard in `_add_column_if_missing`), `src/backend/models/__init__.py`, `tests/test_versioned_baseline.py`, `tests/test_tag_models.py`, `docs/google_2026-04-17_prep.md`, `docs/plans/integrated_prep_portal_plan.md`, `scripts/seed_google_longest_nondec_calc_topk.py`, `scripts/_append_410_code_review.py`, `scripts/_append_410_segs_defense.py`, `scripts/_append_43_weight_derivation.py`, `scripts/_update_1244_notes.py`.
- **Sanity check result**: Full pytest 1092 passed / 0 failed; `ruff check src/ tests/` -> All checks passed; `check_emoji.py` -> [OK] No emoji found. All 4 CI gates now green locally.
- **Status**: [DONE]
- **Request**: Cross off T-P0-414. Awaiting user commit approval.
