# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-462: [QIdx-A1] Backfill family on 11 ungrouped LC_PROBLEMS
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: BACKFILL family on 11 LC problems whose cards currently render in the label-less flat grid at the bottom of QuickIndex LC tab (frontend file: src/frontend/src/pages/QuickIndex.tsx, LC_PROBLEMS list minus STATEFUL_DS_DESIGN set).

EXACT 11 problems + proposed family values (final decision -- use these):
  LC 215 Kth Largest Element in an Array          -> heap_topk
  LC 373 Find K Pairs with Smallest Sums          -> heap_topk
  LC 127 Word Ladder                              -> graph_bfs
  LC 269 Alien Dictionary                         -> graph_topo_sort
  LC 200 Number of Islands                        -> graph_grid_traversal
  LC 235 Lowest Common Ancestor of a BST          -> tree_lca
  LC 212 Word Search II                           -> trie_multiword
  LC 15 3Sum                                      -> two_pointers_target
  LC 2503 Max Points From Grid Queries            -> offline_queries_dsu
  LC 2791 Palindrome Paths in Tree                -> tree_dp_rerooting
  LC 2858 Min Edge Reversals                      -> tree_dp_rerooting

IMPLEMENTATION:
- Create scripts/backfill_quickindex_families_20260416.py (idempotent).
- Mapping MUST be a dict at top of file (LC_ID -> family).
- For each (lc_id, family): UPDATE problems SET family=? WHERE leetcode_id=? AND (family IS NULL OR family='').
- Print per-row action: [SET] lc=215 family=heap_topk  OR  [SKIP] lc=215 family already set to heap_topk.
- Re-run must produce all [SKIP] lines (idempotent test).

ACCEPTANCE CRITERIA:
1. After first run, query SELECT COUNT(*) FROM problems WHERE leetcode_id IN (215,373,127,269,200,235,212,15,2503,2791,2858) AND family IS NOT NULL  -> returns 11.
2. Second run prints 11 [SKIP] lines, 0 [SET].
3. No other problems modified (verify via pre/post row count of problems with non-null family; delta == 11 if starting from current NULL state).
4. Commit message format: [T-P1-462] Backfill family on 11 QuickIndex LC problems

CONFIDENCE GATE: all 11 LC IDs verified in DB (done in investigation); family values chosen to match existing conventions (existing non-null families: stateful_ds_design, sparse_representation, mst, bfs_state_space). New values introduced here are semantic and will be reused by T-P1-463 for frontend grouping.

DO NOT TOUCH: Stateful DS problems (LC 146/460/432 etc) -- already have family='stateful_ds_design'. Do not touch the STATEFUL_DS_DESIGN constant in frontend (that is T-P1-463 scope).

#### T-P1-463: [QIdx-A2] QuickIndex.tsx: dynamic family-based grouping
- **Priority**: P1
- **Complexity**: M
- **Depends on**: T-P1-462
- **Description**: REFACTOR src/frontend/src/pages/QuickIndex.tsx to render LC problems grouped by family, eliminating the current label-less flat grid.

USER-APPROVED APPROACH (a): keep hardcoded LC_PROBLEMS array as the source of visible problems, but add a FAMILY_GROUPS mapping and render one collapsible <details> section per family (matching existing Stateful Data Structure Design pattern). NO backend API change.

EXACT EDITS TO src/frontend/src/pages/QuickIndex.tsx:

1. Extend LC_PROBLEMS entries to include a 'family' field (4th property). Use values from T-P1-462 mapping:
   - LC 146/716/432 -> 'stateful_ds_design'  (already implicitly via STATEFUL_DS_DESIGN)
   - LC 215/373     -> 'heap_topk'
   - LC 127         -> 'graph_bfs'
   - LC 269         -> 'graph_topo_sort'
   - LC 200         -> 'graph_grid_traversal'
   - LC 235         -> 'tree_lca'
   - LC 212         -> 'trie_multiword'
   - LC 15          -> 'two_pointers_target'
   - LC 2503        -> 'offline_queries_dsu'
   - LC 2791/2858   -> 'tree_dp_rerooting'

2. Add FAMILY_LABELS constant mapping family slug to display name:
   stateful_ds_design     -> 'Stateful Data Structure Design'
   heap_topk              -> 'Heap / Top-K'
   graph_bfs              -> 'Graph BFS (Word Ladder family)'
   graph_topo_sort        -> 'Graph Topological Sort'
   graph_grid_traversal   -> 'Graph / Grid Traversal'
   tree_lca               -> 'Tree: LCA'
   trie_multiword         -> 'Trie: Multi-word Search'
   two_pointers_target    -> 'Two-Pointers Target Sum'
   offline_queries_dsu    -> 'Offline Queries + DSU'
   tree_dp_rerooting      -> 'Tree DP / Rerooting'

3. Keep STATEFUL_DS_DESIGN constant as-is (stays as 11-item curated group). Render Stateful DS group FIRST (same position as today).

4. Below Stateful DS group: group the remaining 11 LC_PROBLEMS by family. Render each family as <details open> with count badge, grid-cols-2/md:3/lg:4 identical to existing pattern. Render order: follow FAMILY_LABELS insertion order (heap_topk first, tree_dp_rerooting last). No 'Other / Ungrouped' section -- every problem must belong to a family after T-P1-462.

5. Remove the current lines 211-228 'flat ungrouped grid' -- replaced by family-grouped rendering.

ACCEPTANCE CRITERIA:
1. Visit http://localhost:5173/quick-index?section=lc -> every LC card sits under a named <details> group. No unlabeled grid.
2. LRU, LFU, AllOne still appear under 'Stateful Data Structure Design' group (no regression).
3. Each group has a count badge showing correct count.
4. npm run build passes with 0 TS errors.
5. frontend vitest passes (existing 39+ tests).
6. Click behavior unchanged: card -> ProblemDrawer opens with LC id.
7. Manual smoke: visit page, count groups present (should be 8: Stateful DS + 7 new family groups since tree_dp_rerooting combines 2 items).
8. Commit message: [T-P1-463] QuickIndex: family-based grouping replaces flat ungrouped grid

DEPENDS ON: T-P1-462 must complete first (DB family values must be set before frontend groups by family; though frontend relies on hardcoded local mapping, the DB backfill is the contract/source of truth).

NON-GOALS: Do NOT fetch from backend. Do NOT touch ML tab, BQ tab, or knowledge-tree tabs. Do NOT change ProblemDrawer behavior. Do NOT add pagination.

#### T-P1-464: [QIdx-B1] LC 895 Maximum Frequency Stack: Chinese solution notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Write Chinese solution notes for LC 895 Maximum Frequency Stack and mark completed.

CURRENT STATE (verified via DB query):
- problems.leetcode_id=895, title='Maximum Frequency Stack'
- family='stateful_ds_design', is_completed=0, LENGTH(notes)=0

PROBLEM RECAP: FreqStack supports push(val), pop() which removes and returns the most frequent element; ties broken by most recent. All O(1) expected.

SOLUTION TO COVER (canonical):
- Data structures: dict[val]->freq; dict[freq]->stack (list); int max_freq.
- push(val): freq[val]++; if freq[val]>max_freq: max_freq=freq[val]; groups[freq[val]].append(val). O(1).
- pop(): v = groups[max_freq].pop(); freq[v]--; if not groups[max_freq]: max_freq--. Return v. O(1).
- Key insight: group-by-frequency + recency-within-group (stack LIFO). No deletion from earlier-frequency groups needed -- val stays in ALL lower-frequency groups too (this is the clever part).

IMPLEMENTATION:
- Script: scripts/_update_lc895_notes.py (follow pattern of scripts/_update_lc1570_notes.py)
- Use StudyNoteBuilder from scripts/study_note_builder.py (required per CLAUDE.md; use FormulaBlock for any display math; $...$ inline is OK per feedback memory).
- Chinese prose (per memory feedback_lc_notes_chinese); code blocks English Python; algorithm names/complexity in English.
- Idempotent via sentinel in script: SELECT notes -- if notes already includes sentinel '<!-- LC895_NOTES -->' skip.

NOTES SHOULD COVER (in Chinese):
1. 题目定位 (1 段): stateful_ds_design 家族, 考点 = 频次分组 + 组内栈序
2. 核心洞察: 同一 val 在所有 ≤ freq 的 groups 里都有副本. 为什么 pop 时 freq-- 后不需要在低层清理 -- 因为低层副本本来就在, 代表低频时期的那个它.
3. 完整 Python 代码 (defaultdict(int) + defaultdict(list) + max_freq)
4. 走一个示例: push(5), push(7), push(5), push(7), push(4), pop(), pop(), pop(), pop() -> 5,7,5,4
5. 复杂度 O(1) amortized; 空间 O(总 push 次数)
6. 易错点: 用 heap (freq, neg_seq, val) 也能做但 O(log n); 面试官想要 O(1), 不要这么答.
7. Follow-up 追问指针 -> LC 716 Max Stack (同家族, 另一种 stateful 栈变体) + LC 1429 First Unique Number (类似 eviction 思路)
8. 45 秒 pitch

ACCEPTANCE CRITERIA:
1. UPDATE problems SET notes=..., is_completed=1 WHERE leetcode_id=895.
2. LENGTH(notes) >= 2000.
3. Re-run prints [UNCHANGED] (sentinel present).
4. Contains Chinese prose (至少 500 汉字).
5. Commit: [T-P1-464] LC 895 Maximum Frequency Stack: Chinese solution notes

REFERENCE: scripts/_update_lc1570_notes.py (same pattern; 1500 chars Chinese notes, is_completed=1).

#### T-P1-465: [QIdx-B2] LC 1146 Snapshot Array: Chinese solution notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Write Chinese solution notes for LC 1146 Snapshot Array and mark completed.

CURRENT STATE (verified): leetcode_id=1146, family='stateful_ds_design', is_completed=0, LENGTH(notes)=0.

PROBLEM RECAP: SnapshotArray(length) inits all-zero array. set(index,val) sets. snap() increments snap_id and returns previous. get(index,snap_id) returns val at index at that snap.

SOLUTION TO COVER:
- Per-index list of (snap_id, val) tuples, append-on-set with coalesce if same snap_id.
- get: bisect_right(arr[index], (snap_id, inf)) - 1. O(log n) per get.
- snap: just bump global snap_id, O(1). This is the key insight -- no deep copy.
- set: append O(1) amortized. Special case: if last entry has same snap_id, overwrite in place.

IMPLEMENTATION:
- scripts/_update_lc1146_notes.py (pattern of _update_lc1570_notes.py)
- StudyNoteBuilder required; Chinese prose; sentinel '<!-- LC1146_NOTES -->'.
- Idempotent.

NOTES MUST COVER:
1. 题目定位: stateful_ds_design, 考点 = 版本化数据结构 + 二分查找
2. 核心洞察: snap() O(1) 靠的是 per-index 只记增量 (snap_id, val), 从不整体拷贝. 空间 O(K) where K = 总 set 调用次数, 独立于 length 和 snap 次数.
3. 完整 Python 代码 (defaultdict(list) + bisect)
4. bisect_right 为什么用 -1: 找 <= snap_id 的最大 snap_id. 画一个走查示例.
5. 复杂度: set O(1) amort; get O(log K_i); snap O(1). 空间 O(K).
6. 易错点: 不能在 snap 时整体拷贝 (爆内存); bisect 条件要 snap_id 严格 <=; 同 snap_id 里多次 set 要覆盖不要 append (否则 bisect 会返回旧值).
7. Follow-up: 并发 snap 怎么办 (copy-on-write / MVCC 思路) -> 指向数据库 MVCC 的桥接.
8. 45 秒 pitch.

AC:
1. UPDATE notes + is_completed=1 for lcid=1146
2. LENGTH(notes) >= 2000
3. Re-run [UNCHANGED]
4. Commit: [T-P1-465] LC 1146 Snapshot Array: Chinese solution notes

REFERENCE: scripts/_update_lc1570_notes.py

#### T-P1-466: [QIdx-B3] LC 1825 Finding MK Average: Chinese solution notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Write Chinese solution notes for LC 1825 Finding MK Average and mark completed.

CURRENT STATE: leetcode_id=1825, family='stateful_ds_design', is_completed=0, LENGTH(notes)=0.

PROBLEM RECAP: MKAverage(m,k); addElement(num); calculateMKAverage() returns average of last m elements after removing smallest k and largest k (mean of middle m-2k).

SOLUTION TO COVER:
- Three SortedList (low=k smallest, mid=m-2k middle, high=k largest) + sum_mid running total.
- addElement: append to deque; if deque len > m evict oldest from whichever bucket; insert new into correct bucket; rebalance.
- calculateMKAverage: return sum_mid // (m-2k). O(1).
- Alt: two heaps with lazy deletion.

IMPLEMENTATION:
- scripts/_update_lc1825_notes.py (pattern _update_lc1570_notes.py)
- StudyNoteBuilder + Chinese prose + sentinel '<!-- LC1825_NOTES -->' + idempotent.

NOTES COVER (Chinese):
1. 题目定位: 滑动窗口 + 分桶维护第-k 大/小 (类比 LC 480 中位数, 但三桶版本).
2. 核心洞察: 三个 SortedList + sum_mid, 避免每次 O(m) 重算; 维护 |low|=|high|=k 不变式.
3. 完整 Python 代码 (sortedcontainers.SortedList + collections.deque).
4. rebalance 6 种情况简化成先恢复 sizes 再按阈值迁移.
5. 复杂度 add O(log m), calc O(1), 空间 O(m).
6. 易错: evict 时要从正确桶精确删除 (bisect 定位, 不要盲 remove).
7. Follow-up: 两 heap + lazy del.
8. 45 秒 pitch.

AC:
1. UPDATE notes + is_completed=1 for lcid=1825.
2. LENGTH(notes) >= 2000.
3. Re-run prints [UNCHANGED].
4. Commit: [T-P1-466] LC 1825 Finding MK Average: Chinese solution notes.

REFERENCE: scripts/_update_lc1570_notes.py

#### T-P1-467: [QIdx-B4] LC 1845 Seat Reservation Manager: Chinese solution notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Write Chinese solution notes for LC 1845 Seat Reservation Manager and mark completed.

CURRENT STATE (verified): leetcode_id=1845, family='stateful_ds_design', is_completed=0, LENGTH(notes)=0.

PROBLEM RECAP: SeatManager(n) has n unreserved seats (1..n). reserve() returns smallest-numbered unreserved seat. unreserve(seat_number) marks seat unreserved again. Both O(log n) expected.

SOLUTION TO COVER:
- Min-heap of available seat numbers. reserve = heappop. unreserve = heappush.
- Two init strategies:
  (a) Upfront: heapq with 1..n all pushed at __init__ (O(n) via heapify). Pro: simple; con: O(n) memory + init time even if few reserves.
  (b) Lazy: maintain next_seat int + heap of returned seats. reserve: if heap nonempty return heappop; else return next_seat++. unreserve: heappush. Pro: O(1) init.
- Interview answer: default (a) heapify (heapq.heapify([1..n]) is O(n) not O(n log n)), mention (b) as optimization.

IMPLEMENTATION:
- scripts/_update_lc1845_notes.py (pattern _update_lc1570_notes.py)
- StudyNoteBuilder + Chinese + sentinel '<!-- LC1845_NOTES -->' + idempotent.

NOTES COVER:
1. 题目定位: stateful_ds_design 里最简单的 heap 问题, 但是是很多真实调度系统的 canonical 模型
2. 核心洞察: 只要 '最小可用 id' 这个语义, min-heap 最直接
3. 完整 Python 代码 (class SeatManager with heapq.heapify in __init__)
4. 两种 init 策略对比表 (内存 / 初始化时间 / 大 n 下的行为)
5. heapify O(n) 为什么不是 O(n log n) -- 自底向上 sift-down 的几何级数求和 (给出简略推导)
6. 复杂度: reserve/unreserve 都是 O(log n). 空间 (a) O(n) (b) O(R) where R=已归还数量.
7. 易错点: 不要用 sorted list + pop(0) (O(n) 每次); 不要用 set + min(s) (min 是 O(n)).
8. Follow-up: 若要求 'largest unreserved' 用 max-heap (Python 用负号); 若 unreserve 无序, 要不要去重保护 (一般题目说保证不重复, 省略).
9. 45 秒 pitch.

AC:
1. UPDATE notes + is_completed=1 for lcid=1845
2. LENGTH(notes) >= 2000
3. Re-run [UNCHANGED]
4. Commit: [T-P1-467] LC 1845 Seat Reservation Manager: Chinese solution notes

REFERENCE: _update_lc1570_notes.py

#### T-P1-468: [QIdx-B5] LC 362 Design Hit Counter: expand notes
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: Expand thin notes for LC 362 Design Hit Counter to full solution + mark completed.

CURRENT STATE: leetcode_id=362, family='stateful_ds_design', is_completed=0, LENGTH(notes)=956 (too thin).

PROBLEM RECAP: HitCounter with hit(timestamp) and getHits(timestamp) returning hits in past 300 seconds (sliding 5-minute window).

SOLUTIONS TO COVER:
- Solution A: queue of timestamps. hit: append. getHits: popleft while front < timestamp - 300; return len(queue). O(1) amortized hit; O(k) getHits where k = expired entries.
- Solution B: circular buffer size 300, bucket[(ts % 300)] = (ts, count). hit: if bucket.ts == ts increment else reset (ts, 1). getHits: sum bucket.count for each of 300 buckets where ts > timestamp - 300. O(1) hit, O(300) = O(1) getHits.
- B vs A: B is O(1) per op but fixed 300 memory; A is O(calls in window) memory and O(k) getHits which can burst. Production systems use B.

IMPLEMENTATION:
- scripts/_update_lc362_notes.py (REPLACE existing thin notes, do not append; use sentinel '<!-- LC362_NOTES_V2 -->' to detect re-run).
- StudyNoteBuilder + Chinese + idempotent.

NOTES COVER (Chinese):
1. 题目定位: stateful_ds_design, 滑动时间窗计数 canonical 问题.
2. 两解法对比表 (内存 / 时间 / 爆发容忍 / 是否支持任意窗口大小).
3. 解法 A 代码 + 走查; 解法 B 代码 + 为什么 bucket=300 固定 (题目给定 window).
4. 复杂度分析 + 为什么 B 的 O(300) 算 O(1).
5. Follow-up:
   (a) 并发 hit 安全 -> bucket 上加 CAS 或 shard 按 ts 哈希;
   (b) 任意窗口大小 window_sec -> bucket 数 = window_sec, getHits 遍历全部桶;
   (c) 超高 QPS 下 bucket 溢出 -> 按秒的 count 用 atomic int64;
   (d) 分布式 -> Redis sliding-window-log (zset + remove-score-range).
6. 45 秒 pitch.

AC:
1. UPDATE notes (REPLACE, not append), is_completed=1, for lcid=362.
2. LENGTH(notes) >= 2500.
3. Re-run prints [UNCHANGED].
4. Commit: [T-P1-468] LC 362 Design Hit Counter: expand to full A/B comparison + follow-ups.

### P2 -- Nice to Have

#### T-P2-469: [QIdx-C1] Harden LC import scripts to set family
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: Harden LC import scripts so new rows no longer default to family=NULL silently.

BACKGROUND: Current pipeline adds LC problems via import_staging_lc.py and multiple seed_*lc*.py scripts. None set family; result is 1026 LC problems with family=NULL in DB. This task prevents the rot from growing.

IMPLEMENTATION: Pick a low-intrusion path:
- Locate all LC-insert call sites: grep -r -l "INSERT INTO problems" scripts/ and inspect each.
- Typical files (verify before editing): scripts/import_staging_lc.py, scripts/seed_pinterest_lc_problems.py, scripts/_seed_*.py that touch problems.
- At each INSERT: if family is not provided or is NULL/empty, log the row to logs/lc_family_quarantine.tsv (append-only tsv: timestamp\tlc_id\ttitle\tsource_script). Print WARN to stderr: [WARN] LC {id} inserted without family; logged to quarantine.
- DO NOT fail the insert -- non-blocking warn-and-log.
- Add a new helper module scripts/_lc_import_helpers.py with one function: warn_if_missing_family(lc_id, title, family, source_script). Each import script imports and calls this before/after the INSERT.

ACCEPTANCE CRITERIA:
1. scripts/_lc_import_helpers.py exists with warn_if_missing_family.
2. At least 2 existing import call sites patched to use it.
3. Demo: running any patched importer with a row that has no family produces a WARN line and appends a row to logs/lc_family_quarantine.tsv.
4. Rows WITH family do not produce warnings or quarantine entries.
5. Existing smoke tests (if any for these importers) still pass.
6. Commit: [T-P2-469] Harden LC import scripts: warn + quarantine rows missing family

NON-GOALS: No DB schema change. No retroactive fix for the 1026 existing NULL-family rows (covered separately if needed). No hard validation failure on insert (non-blocking warn only).

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

> 414 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-16** -- T-P2-460: [Pinterest-SD] Responsible AI / Inclusive AI + model monitoring & retraining playbook. Gap: Pinterest brands on 'Inclusive AI' (skin-tone-fair visual search case study) but no prep doc covers it. Bundle with
- [x] **2026-04-16** -- T-P2-459: [Pinterest-SD] Multimodal unsafe content detection + query expansion recall boost. Gap: two known Pinterest SD interview prompts -- neither has a dedicated doc. (1) Unsafe content (image+text multimodal)
- [x] **2026-04-16** -- T-P2-458: [Pinterest-Gen] GAN / VAE / Diffusion contrast one-pager + Pinterest use cases. Gap: no generative-model contrast at pitch level. Pinterest angle (visual content): pin generation, style transfer for b
- [x] **2026-04-16** -- T-P2-439: [DEBT] MLInterviewPrep: requirements.txt has scraper deps in wrong section. beautifulsoup4==4.12.2 and playwright==1.58.0 are in [project.optional-dependencies].scraper in pyproject.toml but appea
- [x] **2026-04-16** -- T-P2-438: [DEBT] MLInterviewPrep: httpx duplicated in pyproject.toml main + dev groups. pyproject.toml lists httpx==0.27.2 in both [project].dependencies (main) and [project.optional-dependencies].dev. This i
- [x] **2026-04-16** -- T-P2-437: [SYNC] Propagate 4 new MLInterviewPrep lessons to helixos LESSONS.md. 4 lessons from MLInterviewPrep (2026-04-10 to 2026-04-15) not yet in helixos LESSONS.md. All apply to helixos. (1) 2026-
- [x] **2026-04-16** -- T-P1-461: [adhoc] LC 815 follow-up: station-level shortest path section. Append follow-up to LC 815 notes: min-stops variant via station-level BFS / Dijkstra. Idempotent script with sentinel gu
- [x] **2026-04-16** -- T-P1-457: [Phase 0.5b] Template v1.1 post-Sketch revision: drawer tab render order + Optimization granularity example. DEFERRED revision of Phase 0.5 content template after T-P0-241 Sketch sample ships real-world signal. Per independent re
- [x] **2026-04-16** -- T-P1-456: [ML-RecSys] Matrix factorization: SGD vs ALS + bridge from CF to embedding models. Gap: node 108 (Collaborative Filtering) covers CF concept but not the MF mechanics bridging CF -> Two-Tower. (1) Bias-on
- [x] **2026-04-16** -- T-P1-455: [Pinterest-RecSys] Cold-start strategies: user + item + pin bootstrap. Gap: cold-start absent from pillar4.recommender_systems nodes (108/109/110 cover CF/content-based/deep but not cold-star
- [x] **2026-04-16** -- T-P1-454: [Pinterest-NLP] Word2Vec/GloVe history + ViT + cross-modal attention supplement. Gap: pre-transformer embedding history missing entirely; node 164 (Vision-Language Models) covers CLIP/LLaVA shallowly b
- [x] **2026-04-16** -- T-P1-453: [Pinterest-CV] CNN foundation 1-pager: conv mechanics + ResNet/VGG/EfficientNet + transfer learning + data aug. Gap: Pinterest is visual-content-first, but CV framework_nodes 122/123 are shallow (5733b+6231b). (1) Conv op: stride/pa
- [x] **2026-04-16** -- T-P1-423: [Google/R1] Train-serve skew/leakage/时序 split 拷打. AC: (1) target encoding K-fold leakage + fold-out 修正; (2) 为什么 ranking 必须 time-based split; (3) feature store parity 三种 s
- [x] **2026-04-16** -- T-P1-422: [Google/R1] Feature drift 监控: PSI/KL/JS 区别 + alert threshold. AC: (1) PSI=Σ(a-e)·ln(a/e), 0.1 warn/0.25 critical; (2) KL 不对称无界, JS 对称 bounded; (3) 连续用 KS; (4) concept drift P(y|x) vs
- [x] **2026-04-16** -- T-P0-452: [Meta-Cleanup] Sketch family unification: 3-axis view + terminology grounding across sketch docs. User-flagged: compact-DS content (CMS/HLL/SS/Bloom) duplicated across framework_nodes 196/197/103 + Pinterest doc 58, ea
- [x] **2026-04-16** -- T-P0-451: [DL-Fund] DL training pitfalls 1-pager: Focal loss + BatchNorm/LayerNorm + vanishing/exploding gradients. Gap: three scattered pitfall topics consolidated. (1) Focal loss: alpha/gamma, class imbalance, when NOT to use (already
- [x] **2026-04-16** -- T-P0-450: [DL-Fund] Optimizer family: SGD -> Momentum -> AdaGrad -> RMSProp -> Adam derivation chain. Gap: node 74 Gradient Descent Family is stub (141b). Existing study note source: data/t8_optimizers.md (port into DB). C
- [x] **2026-04-16** -- T-P0-449: [DL-Fund] Activation functions unified: ReLU/LeakyReLU/Sigmoid/Tanh/Softmax when and why. Gap: no standalone activation-functions node. Single comparison table: {activation, range, derivative, vanishing-grad ri
- [x] **2026-04-16** -- T-P0-448: [ML-Fund] Classical model pitches: KNN / Naive Bayes / K-Means / DBSCAN when-to-use. Gap: node 71 Clustering stub + no NB/KNN nodes. Pitch-format 1-pager: per model -> (what / assumption / when use / when 
