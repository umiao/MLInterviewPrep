# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

#### T-P0-405: [Pinterest/SD] ML SD: Design Pins Search Engine
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD (most frequently asked 2025-11). End-to-end: (1) candidate generation (two-tower embedding, ANN/HNSW, multi-source text/image/history), (2) ranking (pairwise vs pointwise, feature eng: text/image/graph/user-context, loss functions, offline metrics NDCG/MAP/AUC), (3) online metrics (CTR, repin-rate, session engagement), (4) infra (Faiss/ScaNN, feature stores, training pipeline), (5) cold-start + freshness. Chinese markdown docs/pinterest/system_design_pins_search.md.

#### T-P0-406: [Pinterest/SD] ML SD: Notification Recommendation
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. (1) notification triggering (when to notify), (2) content candidate generation, (3) ranking, (4) delivery constraints (frequency cap, quiet hours, channel push/email/in-app), (5) offline metrics (open-rate AUC, long-term retention), (6) engagement-vs-annoyance tradeoffs. Chinese markdown docs/pinterest/system_design_notification_reco.md.

#### T-P0-407: [Pinterest/SD] ML SD: Pin Ranking Recommendation
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. Pin ranking for home/topic feed. (1) two-stage retrieval+rerank, (2) features (pin/user/context/graph), (3) model family (MMOE/wide-and-deep/transformer), (4) multi-objective (engagement+diversity+long-term), (5) serving constraints, (6) metric ladder. Chinese markdown docs/pinterest/system_design_pin_ranking.md.

#### T-P0-410: [Pinterest/SD] SD: Catalog bulk update (500M records, S3+async)
- **Priority**: P0
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. Update internal downstream systems from large catalog (~500M). (1) ingestion (bulk via S3 consume; single sync/quick-async), (2) partitioning (range, hash, consistent-hash), (3) retry for failed partitions (at-least-once + idempotency, DLQ, checkpoint), (4) fan-out (Kafka, backpressure, flow control), (5) monitoring (lag, error-rate, RPO/RTO), (6) tradeoffs: sync-vs-async, exactly-once-vs-at-least-once. Chinese markdown docs/pinterest/system_design_catalog_bulk_update.md.

### P1 -- Should Have (agentic intelligence)

#### T-P1-387: [BQ-sweep] Tier-2 metric補充: replace adjectives with numbers across ~12 stories
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: User guidance (2026-04-13 Discord): "Fill in similarly". For stories where user has not provided facts, use [TODO: confirm number] placeholder markers -- never invent metrics. Target stories and suggested fills: EX-1 (initial A/B lift before scaling), EX-4 (which Q OKRs updated), EX-14 (adoption count + Q), EX-15 (intern perf rating or ticket backlog), EX-17 (# subsequent papers applying the norm), EX-18 (sync DB to improved-story version: 18K labels/day at $500, 1.5% GMB -- these are known), EX-21 (# merged PRs with zero review-restart), EX-23 (traffic % avoided on invalid A/B), EX-24 (FP-rate delta), EX-29 (GMV delta or A/B result), EX-35 (new-seller FP rate X%->Y%), EX-36 (0 privacy incidents + retrieval recall@K unchanged). Replace "improved/streamlined/widely adopted" with either a concrete number (if known) or "[TODO: confirm]". Do NOT fabricate. Edit JSON + markdown for each.

#### T-P1-388: [BQ-sweep] Tier-2 ownership sharpening: "we" -> "I" in Action sections
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Sweep target stories: EX-2 (lead +1% GMB prominently), EX-11 (I led compression, researcher gave context), EX-13 (I flagged, I took point on negotiations; manager gave air cover), EX-25 (I independently researched and built), EX-26 (I defined acceptance criteria, validated final choice), EX-27 (I served as DRI / critical-path owner, not coordinator). Keep "we" only in Situation (context). Every Action bullet must start with "I". Edit JSON + markdown.

#### T-P1-389: [BQ-sweep] Tier-2 catch-all polish: remaining 1-weak-signal stories
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Remaining Tier-2 stories not covered by metric or ownership sweeps. Primary: EX-7 (add downstream metric after unbiased dataset adoption). Scan JSON/md for any other stories flagged in 2026-04-13 audit that dont fit metric or ownership sweeps. One-off fixes per story -- structural polish only. Edit JSON + markdown.

#### T-P1-390: [Pinterest/LC] Add + notes: LC 84 Largest Rectangle in Histogram
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem (2025-11 cutoff). Add to problems DB with Pinterest tag; fetch description; write Chinese notes: monotonic-stack O(n) canonical + divide-and-conquer O(n log n) + related LC 85/42/11 + pattern recognition.

#### T-P1-391: [Pinterest/LC] Add + notes: LC 392 Is Subsequence
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem. Two-pointer O(n+m). Follow-up: many queries -> precompute indexed char positions, binary search each query. Chinese notes. Cross-link LC 1055 (greedy subsequence family).

#### T-P1-392: [Pinterest/LC] Add + notes: LC 3229 Min Operations to Make Array Equal to Target
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem. Diff-scan greedy (same family as LC 1526). Chinese notes covering increment/decrement region handling + sign-change counting. Cross-link LC 1526.

#### T-P1-393: [Pinterest/LC] Add + notes: LC 1526 Min Increments on Subarrays
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem. Diff-array + greedy sign-change pattern. Chinese notes explaining why counting positive deltas is optimal. Cross-link LC 3229.

#### T-P1-394: [Pinterest/LC] Add + notes: LC 1564 Put Boxes Into Warehouse I
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem. Greedy: warehouse prefix-min + sort boxes desc. Chinese notes highlighting the prefix-min insight.

#### T-P1-395: [Pinterest/LC] Add + notes: LC 1580 Put Boxes Into Warehouse II
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: New Pinterest problem (harder variant of 1564, enter from both ends). Chinese notes: two-pointer shortest-interior-height preprocessing. Contrast with 1564.

#### T-P1-398: [Pinterest/custom] Lighthouse 2D matrix light propagation
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Pinterest coding 2025-11. 2D matrix simulation of light propagation. Resolve exact variant from dump (light rays + mirrors? coverage? cycle?). Research variants; write solution + Chinese notes as non-LC entry.

#### T-P1-399: [Pinterest/custom] Prefix-match first-word-index
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest coding 2025-11: given ['a','apple','appz','b'] and prefix ['ap'], return index of first word containing prefix. Trie with earliest-word-index at each node (or sort+binary-search). Python + Chinese notes.

#### T-P1-400: [Pinterest/custom] Grant Access permission propagation
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Pinterest coding 2025-11. Problem linked at hack2hire.com (URL in dump). Research and document: likely DAG/graph permission propagation. Solution + Chinese notes as non-LC entry. Link in Pinterest index doc.

#### T-P1-401: [Pinterest/custom] Pin Connectivity
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: Pinterest coding 2025-11. Graph connectivity problem on pin/board/user graph. Research variant, write canonical (Union-Find or BFS/DFS) + Chinese notes. Non-LC entry.

#### T-P1-402: [Pinterest/custom] round() from scratch (string input)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest coding 2025-11. Implement round() given string s without using float(). Edge cases: float overflow, '-.2', '2.' (trailing dot). Parse digits+dot+sign manually; half-up rounding. Chinese notes with state machine.

#### T-P1-403: [Pinterest/custom] Round string s by precision p
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest coding 2025-11 follow-up. Round s by precision p. Examples: s='12567',p='100'->'12600'; s='1234.678',p='0.1'->'1234.7'. Parse both, determine decimal places from p, round accordingly. Chinese notes.

#### T-P1-404: [Pinterest/custom] LC 332 loop follow-up addendum
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest coding 2025-11 follow-up to LC 332: what if tickets form a cycle? Explain Hierholzer already handles Eulerian circuits naturally (returns to JFK). If question is detecting infeasible itinerary, discuss Eulerian existence conditions. Append as addendum to existing LC 332 notes (don't create new problem entry).

#### T-P1-408: [Pinterest/SD] SD: Ad CTR prediction
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. (1) data pipeline (impressions/clicks with attribution), (2) feature engineering (user/ad/context crosses), (3) model (DeepFM/wide-and-deep/AutoInt), (4) calibration (Platt/isotonic), (5) serving (model server, feature store, latency budget), (6) online metrics (NE, LogLoss, calibration error). Chinese markdown docs/pinterest/system_design_ad_ctr.md.

#### T-P1-409: [Pinterest/SD] SD: User & Item Embeddings
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. (1) objective (self-supervised contrastive / supervised from engagement), (2) encoder (towers, user sequence, graph-based GraphSAGE/PinSage), (3) training pipeline (streaming vs batch), (4) serving (ANN index, freshness, dimension), (5) downstream uses (candidate gen, ranking features, similar-pins). Chinese markdown docs/pinterest/system_design_embeddings.md.

#### T-P1-411: [Pinterest/SD] ML SD: Personalized Chat Bot Recommending Pins
- **Priority**: P1
- **Complexity**: L
- **Depends on**: None
- **Description**: Pinterest SD 2025-11. (1) conversation understanding (LLM multi-turn state), (2) intent classification (ask-pins vs chit-chat), (3) retrieval-augmented pin recommendation, (4) grounding (pins match intent), (5) safety/moderation, (6) evaluation (relevance + conversation quality). Chinese markdown docs/pinterest/system_design_chatbot_pins.md.

#### T-P1-412: [Pinterest/BQ] Map Pinterest BQ questions to existing stories
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest BQ (2025-11): (1) project led end-to-end, (2) where requirement came from, (3) stepping ahead when not responsible, (4) negative feedback received, (5) working with someone missing deadlines. Create docs/pinterest/bq_question_map.md mapping each Q to 2-3 best-fit EX-XX stories with 1-sentence angle each. Reference post-rework stories. Chinese.

### P2 -- Nice to Have

#### T-P2-396: [Pinterest/LC] Investigate + notes: 寻找餐馆区间
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Pinterest dump 2025-11 mentions this with no LC number. Research to identify the actual LC mapping (candidates: LC 1779 / 2563 / 1094 / 1851). If LC match found, add/update. If custom, create non-LC entry.

#### T-P2-413: [Pinterest/integration] Enrich Pinterest index doc with new sections
- **Priority**: P2
- **Complexity**: M
- **Depends on**: T-P1-390, T-P1-391, T-P1-392, T-P1-393, T-P1-394, T-P1-395, T-P0-397, T-P0-405, T-P0-406, T-P0-410, T-P1-412
- **Description**: Final integration after all new LC/custom/SD content lands. Refresh company_documents id=47 to include: (1) new LC section (84, 392, 3229, 1526, 1564, 1580, 餐馆区间), (2) Custom Coding section (Escape Room, Lighthouse, Prefix-match, Grant Access, Pin Connectivity, round(), Round-by-p, LC332 loop) with lc:// drawer links where applicable, (3) System Design section with links to docs/pinterest/system_design_*.md files, (4) BQ Question Map link, (5) cross-links LC problems <-> relevant SD modules (e.g. LC 1244 <-> Leaderboard SD family). Depends on all previous Pinterest expansion tasks being complete.

### P3 -- Stretch Goals

## Blocked

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare python which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all python with /c/Anaconda/python.exe in ALL hook commands
3. Add SessionStart hook entry for setup_python_env.sh

BLOCKED: Claude Code file permissions block writes to helixos .claude/hooks/ directory from MLInterviewPrep session. Must be done from a helixos session or manually.

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL: helixos settings.json uses bare python for ALL hook commands. On Windows, bare python resolves to the AppData Store stub (exit code 49), silently breaking all hooks. Fix: (1) Replace all bare python with /c/Anaconda/python.exe in settings.json. (2) Add setup_python_env.sh SessionStart hook (copy from MLInterviewPrep) to inject Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE. CLAUDE.md already documents this prohibition (added 2026-03-21 via propagation) but the fix was never applied. This is the same root cause as MLInterviewPrep lesson [2026-03-20] #bash-tool #path.

#### T-P1-319: [SYNC] helixos: Fix bare python in settings.json hooks (critical)
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: ALL hook commands in helixos settings.json use bare python instead of /c/Anaconda/python.exe. This causes exit code 49 on Windows Store stub. Also missing setup_python_env.sh in SessionStart. Actions: (1) Replace python with /c/Anaconda/python.exe in every hook command. (2) Add setup_python_env.sh as first SessionStart hook copied from MLInterviewPrep. Source: MLInterviewPrep settings.json, LESSONS.md 2026-03-20.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/hooks/test_check.py still imports and uses check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed the cache in T-P2-188 (commit abf6543), per the lesson that stop caches can produce false passes when files change between sessions.

Action: Update helixos/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove check_stop_cache/write_stop_cache import and usage. Run tests after to confirm hook still works.

Source: MLInterviewPrep/.claude/hooks/test_check.py (current, cache-free version).

#### T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/test_check.py still uses check_stop_cache/write_stop_cache from hook_utils. The lesson [2026-03-18] established that stop caches cause false PASS results when files change between sessions. MLInterviewPrep already fixed this.

Action: Update template/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove cache import and usage. The template is the reference baseline, so it should have the best-known version of all hooks.

Source: MLInterviewPrep/.claude/hooks/test_check.py.

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: test_check.py imports check_stop_cache and write_stop_cache from hook_utils and uses them to skip re-running tests in the same session. These deprecated caching functions were removed from the hook architecture (LESSONS.md lesson [2026-03-18]: removed lint cache so every Stop hook runs fresh). The caching logic means test failures can be silently skipped if tests passed earlier in the same session. Fix: Remove the cache check/write calls from test_check.py so tests always run fresh on Stop. Keep check_stop_cache/write_stop_cache in hook_utils.py only if other hooks still use them.

#### T-P2-320: [SYNC] helixos: Remove deprecated stop-cache from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos test_check.py still uses check_stop_cache/write_stop_cache which were deprecated per LESSONS.md 2026-03-18. Cache can produce false passes when files change between cache write and next session. MLInterviewPrep already removed this. Action: Remove cache imports and calls from test_check.py; clean up hook_utils.py if no other callers.

## Completed Tasks

> 350 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-12** -- T-P2-379: [Pinterest/index] Refresh Pinterest LC index doc after translations/fetches. After Chinese translations and missing descriptions are done, regenerate the Pinterest LC Must-Do: Review & Index compan
- [x] **2026-04-12** -- T-P2-373: [Pinterest/CN] Polish mixed-language notes to full Chinese: LC 311, 815, 1244. Three existing notes are MIX (ratios 0.11-0.29). Rewrite the English prose sections to Chinese, keep code blocks and tec
- [x] **2026-04-12** -- T-P1-378: [Pinterest/notes] Write LC 1723 solution notes (Find Minimum Time to Finish All Jobs). Pinterest must-do; no notes yet. Cover: binary search on answer + backtracking feasibility check, pruning (sort jobs des
- [x] **2026-04-12** -- T-P1-377: [Pinterest/notes] Write LC 642 solution notes (Design Search Autocomplete System). Pinterest must-do; no notes yet. Cover: Trie + hot-words map at each node, top-k with heap, input streaming state machin
- [x] **2026-04-12** -- T-P1-376: [Pinterest/notes] Write LC 43 solution notes (Multiply Strings). Pinterest must-do; no notes yet. Cover: digit-by-digit simulation with (i+j, i+j+1) index trick, carry propagation, lead
- [x] **2026-04-12** -- T-P0-397: [Pinterest/custom] Escape Room game-state (Game(rooms, people)). Pinterest coding 2025-11. Design data structure: proceedToNextRoom(pid), getTop(K), getPeople(roomId). Requirements: O(1
- [x] **2026-04-12** -- T-P0-386: [BQ-rework] EX-33 MoE Paradigm Shift: close the arc with downstream win. Flags C+D. Target: DB `behavioral_examples` row example_id=EX-33 "MoE -> Allocation Paradigm Shift - Org-Level Reframe v
- [x] **2026-04-12** -- T-P0-385: [BQ-rework] EX-28 Explaining Allocation to VP: estimate avoided cost. Flags A+C. Target: JSON EX-24 (audit called it EX-28) "Explaining Allocation Problem to VP". User-provided facts (2026-0
- [x] **2026-04-12** -- T-P0-384: [BQ-rework] EX-22 Pushback on Scope: add delivery-impact metric. Flags A+C+D. Target: JSON EX-18 (audit called it EX-22) "Pushing Back on Unreasonable Scope". User-provided facts (2026-
- [x] **2026-04-12** -- T-P0-383: [BQ-rework] EX-20 Cross-DC Deployment Incident: quantify blast radius. Flags A+C. Use user-provided facts (2026-04-13 Discord): Cross-DC deployment was delayed ~6 hours, blocking TWO launches
- [x] **2026-04-12** -- T-P0-382: [BQ-rework] EX-19 Model Deprecation Incident: own the gap personally. Flags C+D. Use user-provided facts (2026-04-13 Discord): This was NOT a user-facing prod-model impact -- but it took 2 f
- [x] **2026-04-12** -- T-P0-381: [BQ-rework] EX-16 PhD Interns Notebook-to-Production: add onboarding metric. Flags A+C. Use user-provided facts (2026-04-13 Discord): 6 interns in my org adopted a similar notebook-to-production ch
- [x] **2026-04-12** -- T-P0-380: [BQ-rework] EX-12 Code Review Standards: add concrete metric. Flag C (vague metric). Use user-provided facts (2026-04-13 Discord): before the checklist/standards, ~80% of changes req
