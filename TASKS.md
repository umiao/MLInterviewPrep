# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

#### T-P0-243: Uber BPS: Write solutions for custom non-LC interview problems
- **Priority**: P0
- **Complexity**: L
- **Depends on**: T-P0-241
- **Description**: Detailed solutions for Uber-specific interview problems without standard LC numbers. Each solution must include: problem statement (reconstructed from 1p3a), approach explanation, clean Python code, time/space complexity, edge cases, and ALL follow-ups.

Problems with follow-ups:
(1) Purchase Optimization: prefix sum + binary search. Given prices array and queries (pos, amount), find max items purchasable.
(2) Customer Revenue & Referral Tracking: OOD design. insertNewCustomer(revenue, referrerID), getLowestK(k, minTotalRevenue). Revenue propagates up referral tree. Must handle tree aggregation efficiently.
(3) Uber Rider Connection Log: Union Find. Parse timestamped logs 'A shared-ride-with B', find earliest time all riders connected. FOLLOW-UP: handle 'block' events (A blocked B) -- UF cannot handle deletions, must use BFS/DFS rebuild. Discuss both approaches.
(4) Elevator Binary Search OA: array-based jump, each position has move distance. Find minimum starting index that never goes out of left boundary.
(5) Server Throughput with Heap: OA problem, recursive vs heap solution comparison.
(6) Cart & Pricing Engine OOD: Design classes for Uber Eats cart. Requirements: item customization (add-ons), surge pricing multiplier, membership discounts (Uber One), promo codes (flat/percentage), receipt breakdown output. Strategy pattern for pricing rules.
(7) Circular Array Shortest Jump: given circular array with jump distances, find shortest path from index A to B. BFS approach.
(8) Robot Distance in Grid: given grid with robots(O), empty(E), obstacles(X), and distance array [left,top,bottom,right], find robot matching distances. DP to precompute distances from each cell to nearest obstacle in 4 directions.
(9) Min Operations n->0: greedy/NAF. Each op: n += or -= 2^i. Optimal: binary representation analysis, n%4==1 -> -1, n%4==3 -> +1.
(10) Shortest Subarray with k Distinct: sliding window + counter. Standard two-pointer.
(11) Price Discount: monotonic stack. For each i, find first j>i where prices[j]<=prices[i]. Output: total discounted sum + indices sold at original price.
(12) Balanced Permutation: given permutation of 1..n, check for each k if subarray forming permutation of 1..k exists. Track min/max position as k increases.
(13) Elevator/Stairs Energy: binary search on split point. First mid floors by elevator (gain energy e1, cost t1 each), remaining by stairs (consume e2, time=ceil(c/energy)). Minimize time difference.
(14) N-ary Tree 3-part: (a) sum all node values, (b) find max path value, (c) return nodes on max path. Must define Node class.
(15) Max Throughput with Budget: binary search on target throughput. Each service has current throughput and scale cost. All services must reach target (bottleneck = min). Check if total cost <= budget.
(16) Parking Lot OOD: park/unpark/checkcar. Motorcycle spots only for motorcycles, regular spots for both. Class design.
(17) Task Assignment to 2 People: n tasks, reward1[i]/reward2[i] per person, person 1 must do exactly k. Greedy: sort by diff(r1-r2), pick top k for person 1.
(18) Jump Game Prime-Ending Variant (like LC 1696): jump +1 or +prime ending in 3. DP, precompute primes.
(19) Min Edge Reversal to find optimal root (re-rooting DP): directed graph, choose root to minimize reversed edges. DFS from 0 + re-root formula.
(20) Palindrome Paths in Tree (LC 2791 variant): bitmask XOR prefix on tree paths, count palindrome-formable paths using DFS + counter map.
(21) Minesweeper Grid Generator: place N mines randomly on 2D grid. FOLLOW-UP: optimize code quality -- remove unnecessary set, reduce variables, simplify logic. Interviewer pushes for cleaner code iteratively.
(22) 2D Grid Nearest Exit: BFS from starting point to find nearest boundary cell. Standard multi-source BFS.
(23) Lock Combination BFS: find minimum steps to unlock. BFS on state space.
(24) Non-overlapping Interval Triples: count groups of 3 intervals with no pairwise overlap.
(25) City Graph BFS Sort: given city graph + start city, sort by distance (ties: smaller index first).

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-245: Uber BPS: Create D&A (Design and Architecture) prep document
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-244
- **Description**: Create docs/uber_bps_design_architecture.md: (1) Project showcase - Ranking-as-Allocation, LLM eval pipeline with high-level diagrams, (2) Trade-off discussions - why tech X over Y, (3) SD patterns from Uber BPS: Driver Maps, Shopping Cart, Driver Queue, ETA, Food Ordering, (4) Common D&A follow-ups from 1p3a.

#### T-P1-246: Uber BPS: KNN from-scratch + ML fundamentals review
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-244
- **Description**: Recruiter explicitly mentions KNN. Create: (1) KNN from scratch Python - distance metrics, k selection, weighted KNN, (2) Classification vs regression, (3) Optimization - KD-tree, ball tree, LSH, (4) Interview Qs - curse of dimensionality, feature scaling, categorical, (5) ML fundamentals: bias-variance, overfitting, CV, metrics.

#### T-P1-247: Uber BPS: Problem pattern cheat sheet by algorithm
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P0-242, T-P0-243
- **Description**: Create docs/uber_bps_pattern_cheatsheet.md organizing problems by pattern: BFS/DFS (994,1020,1197,230,337,549,987,2791,547), Union Find (547,1697,rider,balls), Binary Search (977,purchase opt,elevator,throughput), DP (jump game,house robber,intervals), Monotonic Stack (price discount), Sliding Window (k-distinct), OOD (cart,parking,revenue), Greedy (min ops,task assign). Include complexity summary and pattern recognition tips.

### P2 -- Nice to Have

#### T-P2-186: [SYNC] Propagate ruff version-drift lesson to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep LESSONS.md has [2026-03-02] lesson about ruff version drift between local and CI (loose pin + separate install = silent drift). Tags: #ruff #ci #version-drift. Not yet in helixos LESSONS.md. Action: append the lesson to helixos/LESSONS.md with [PROPAGATED] tag.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-206: [SYNC] Propagate 2 universal lessons to helixos LESSONS.md
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/LESSONS.md is missing 2 universal lessons already in the template:
1. [2026-03-02] Ruff version drift between local and CI (#ruff #ci) -- loose ruff pin causes CI-only failures; fix: pin ruff==X.Y.Z in requirements.txt.
2. [2026-03-11] Task ID P = Phase anti-pattern went undetected (#task-naming #convention-drift) -- P should always mean priority, never phase/stage.

Action: Append both entries (verbatim from template LESSONS.md) to helixos/LESSONS.md. Source: claude-code-project-template/LESSONS.md.

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

#### T-P2-240: [DEBT] MLInterviewPrep: Add _temp*.json pattern to .gitignore
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: `_temp_docs.json` is untracked in MLInterviewPrep and not in .gitignore. These files appear to be temp artifacts from content seeding scripts (e.g., from T-P1-148 tree model content creation). Add `_temp*.json` (and possibly `_temp*.py`) patterns to MLInterviewPrep/.gitignore to prevent accidental commits of temp files.

#### T-P2-248: Uber BPS: Create timed mock interview problem sets
- **Priority**: P2
- **Complexity**: S
- **Depends on**: T-P0-242, T-P0-243, T-P1-247
- **Description**: 3 mock BPS sets simulating 45min coding. Each: 1 medium + 1 medium/hard with follow-ups. Set 1: LC 230 variant + Rider Connection UF. Set 2: LC 994 BFS + Purchase Optimization BS. Set 3: LC 547 graph + Cart Pricing OOD. Timing: 20min per problem, 5min follow-ups.

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

## Completed Tasks

> 207 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-03-31** -- T-P0-244: Uber BPS: Update phone screen prep doc with BPS format. Update docs/uber_phone_screen_prep.md to reflect BPS format from recruiter: 5min intro, 40-50min coding+D&A, 5min Q&A. A
- [x] **2026-03-31** -- T-P0-242: Uber BPS: Create LC solutions for all Uber-tagged problems. Write Python solutions with detailed explanations for each LC problem from Uber BPS interviews. CRITICAL: Include all fo
- [x] **2026-03-31** -- T-P0-241: Uber BPS: Seed 1p3a interview problems into DB with solutions. Parse all Uber interview problems from staging/uber题目整理.txt into the mle_prep.db problems table.
- [x] **2026-03-28** -- T-P2-209: [SYNC] Propagate template session_context db-missing warning to MLInterviewPrep. claude-code-project-template/.claude/hooks/session_context.py (lines 475-486) has a db_missing_warning feature: if .clau
- [x] **2026-03-28** -- T-P2-185: [SYNC] helixos CLAUDE.md: Add no-bare-python rule to Prohibited Actions. MLInterviewPrep CLAUDE.md Prohibited Actions has this rule (lines 62-66):
- [x] **2026-03-27** -- T-P1-231: Fix PrepNotesPage tab overflow: document dropdown. Replace document tab buttons with dropdown select in PrepNotesPage.tsx. Design: Lines 156-175, replace documents?.map(Ta
- [x] **2026-03-27** -- T-P0-237: Rewrite Day 3 (Distributed Training) to Chinese with user supplement. Replace current English Day 3 doc (company_documents id=13, 19574 chars) with comprehensive Chinese version. Source: C:\
- [x] **2026-03-27** -- T-P0-236: Rewrite Day 2 (RLHF/DPO/Distillation) to Chinese with user supplement. Replace current English Day 2 doc (company_documents id=12, 17852 chars) with comprehensive Chinese version. Source: C:\
- [x] **2026-03-27** -- T-P0-235: Day1 Expansion C: Answer all checklist questions. After expansions A+B are done, answer ALL 10 existing checklist questions plus any new ones added by A+B. Format: keep t
- [x] **2026-03-27** -- T-P0-234: Day1 Expansion B: VAE details + ControlNet deep-dive + industry landscape. Expand Day 1 note with 3 more sections: (1) VAE deep-dive: encoder/decoder architecture, latent space regularization (KL
- [x] **2026-03-27** -- T-P0-233: Day1 Expansion A: PE deep-dive + sinusoidal derivation + KV-Cache. Expand Day 1 note (doc id=18) with 3 new sections: (1) Positional Embedding deep-dive: absolute PE, sinusoidal PE deriva
- [x] **2026-03-27** -- T-P0-232: Add Builder convention to CLAUDE.md + update memory. After pilot validates Builder, codify the convention. (1) CLAUDE.md Prohibited Actions: add 'Never write study note cont
- [x] **2026-03-27** -- T-P0-230: Scale: Rewrite remaining 6 Adobe docs with validated Builder. After Day 1 pilot validates the Builder API, rewrite Days 2-7 (company_documents ids 6-11). For each doc: (1) Use StudyN
- [x] **2026-03-27** -- T-P0-229: Pilot: Rewrite Day 1 (Diffusion) end-to-end with Builder. END-TO-END PILOT to validate Builder API before scaling. Take Adobe Day 1 doc (company_documents id=5, Diffusion Models)
- [x] **2026-03-27** -- T-P0-228: Enable rehype-raw in MarkdownPreview. Install rehype-raw and add to MarkdownPreview. (1) npm install rehype-raw. (2) MarkdownPreview.tsx: import rehypeRaw, ad
- [x] **2026-03-27** -- T-P0-227: Minimal StudyNoteBuilder + FormulaBlock typed constraint. Minimal viable Builder with one typed block (FormulaBlock). Design: (1) FormulaBlock dataclass: latex:str, explanation:s
