"""Seed: T-P1-806 [KG-INT B3-4] -- meta-prep/lc-keyword-checklists children.

Distills shared LeetCode keyword / pattern checklists from the 10 P0+P1
companies' LC-related prep surfaces (`company_documents` of kind prep_note /
hub_doc / drill / card_index that index or annotate LC problems) into shared
`meta-prep/lc-keyword-checklists/<slug>` framework_nodes per the promotion
threshold locked in `docs/workflow/promotion_criteria.md` (>=3 of 11 P0+P1
companies AND de-companiable wording).

A grep-driven coverage scan was run across the LC-indexing docs of the 10
P0+P1 companies (LinkedIn id=26 [合集] 算法题解全索引; DoorDash ids=4/41/43/54
domain prep + master; Google ids=92/52/57/72 R2 Coding Index + DNN gist +
flashcards + MF-to-Two-Tower bridge; Uber ids=30/31/32/81/84 LC Solutions
Guide + Custom Problems + Pattern Cheat Sheet + LC Index View + Golden
Answers; Adobe id=16 sim Q + STAR-T; Pinterest ids=47/49/66 LC Must-Do +
Restaurant Intervals + Card Index; Meta ids=80/86/90 OA Prep Hub + Code-Pad
LLM Prompt + AI-Native Coding Inventory). 15 LC patterns / keyword families
cleared the >=3 P0+P1 threshold and were rewritten into de-companiable
checklist nodes. Each child node embeds:

  - Pattern definition + 1-2 sentence trigger phrase ("when do I reach for it")
  - 3-5 canonical LC problem citations with leetcode_id (used for retrieval
    by problem-pattern, NOT as company-specific recommendations)
  - Standard template / invariant / loop shape (the "how" once you've decided
    to use the pattern)
  - Cross-links via kg://N (framework_nodes.id) for adjacent KG nodes
  - Top failure modes / interview anti-patterns
  - relevant_companies CSV listing the >=3 P0+P1 sources

The parent stub `meta-prep/lc-keyword-checklists` (T-P1-800) had a
`TODO[KG-INT-B3-4]` marker. This seed updates the parent description to a
real summary on first run.

Scope decision (which patterns made the cut):
  Hard-promoted (>=3 P0+P1, distinct LC pattern signal): two-pointers,
  sliding-window, binary-search, bfs-dfs grid traversal, backtracking, DP
  (knapsack/LIS/edit-distance family), heap+top-K+quickselect, monotonic
  stack, prefix-sum, intervals-merge, trie, union-find, topological sort,
  linked-list (fast-slow + reverse), ML coding from scratch (kNN / k-means
  / linreg / logreg). Soft-rejected (passes word-frequency but not
  "meaningful instance" per promotion_criteria.md §"appears"):
  generic mentions of "graph" / "tree" / "matrix" without an associated LC
  problem citation -- those are taxonomy noise rather than coverage. Also
  rejected: dijkstra (n=2 sources), string-anagram (n=2 sources),
  monotonic-deque (n=1 source) -- below threshold; deferred to T-P1-821
  B4-promotion re-evaluation if more P0+P1 companies surface them.

Safety:
  1. SHA-256 of the `meta-prep/lc-keyword-checklists` subtree captured
     pre/post.
  2. Refuses to overwrite a child whose title/description/companies have
     drifted from this seed (someone hand-edited it).
  3. Idempotent: re-run yields inserted=0, updated=0, skipped=16
     (1 parent + 15 children).
  4. Parent description UPDATED only on first run (TODO marker present).
  5. Post-run invariant: exactly 16 rows match
     path = 'meta-prep/lc-keyword-checklists' OR
     path LIKE 'meta-prep/lc-keyword-checklists/%'.
  6. AC checks:
       - children count >= 4 (task spec)
       - each child has >=3 valid P0+P1 sources in relevant_companies
       - description contains at least one kg:// cross-link

Usage:
    python scripts/seed_meta_prep_lc_keyword_checklists.py
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "meta-prep/lc-keyword-checklists"
PARENT_TITLE = "LC Keyword Checklists"
PARENT_DESCRIPTION_NEW = (
    "跨公司 LeetCode pattern / keyword checklist (shared LC substrate, "
    "distilled from 10 P0+P1 companies' LC-indexing prep surfaces). "
    "子节点按 LC pattern family 拆分: array/string (two-pointers / "
    "sliding-window / prefix-sum / intervals), search (binary-search 含 "
    "binary-search-on-answer), graph/tree (bfs-dfs grid / backtracking / "
    "topological sort / union-find), aggregation (heap + top-K + "
    "quickselect / monotonic stack), structure (trie / linked-list "
    "fast-slow + reverse), 和 dp (knapsack / LIS / edit-distance), 加上 "
    "ML 岗特有的 ml-coding-from-scratch (kNN / k-means / linreg / logreg "
    "手写). 每个子节点带 trigger phrase (什么题面信号 -> 抓这个 pattern) + "
    "3-5 个 canonical LC 题号 (leetcode_id) + 标准 template / loop shape + "
    "kg://N cross-links (指向 pillar1.algorithm_paradigms / "
    "pillar1.data_structures 的具体节点). 这是 LC-prep round (R0/R1 "
    "coding) 的索引层 -- 看到题目先映射到 pattern 子节点, 再用对应 "
    "template 起手. 不是 LC 题库本身 (题库在 problems 表), 而是从 "
    "pattern 反向找题的 router."
)
PARENT_TODO_MARKER = "TODO[KG-INT-B3-4]"

P0P1_COMPANY_NAMES = {
    "LinkedIn", "DoorDash", "Google", "Uber", "Adobe",
    "TikTok", "Slack", "PARSPEC", "Pinterest", "Meta",
}

# Each tuple: (slug, title, description, [companies])
# Description should embed at least one kg://N cross-link.
CLUSTERS: list[tuple[str, str, str, list[str]]] = [
    (
        "two-pointers",
        "Two Pointers / 双指针",
        "数组/字符串题最常用 pattern, 两个 index 同向或对向移动, 用线性扫描 "
        "替代 O(n^2) brute force. 三种子模式: (1) **opposite-direction** "
        "(left=0, right=n-1, 收敛中间) -- 排序数组 two-sum / 容器盛水 / "
        "回文判定; (2) **same-direction-fast-slow** (slow 写位置, fast 扫描) -- "
        "remove duplicates / move zeros / partition array; (3) **two-pass-merge** "
        "(两个有序数组各一指针) -- merge sorted arrays / intersection. "
        "Trigger phrase: '排序数组找一对/三个数', 'in-place 修改数组', "
        "'从两端往中间走'. Canonical LC: 167 (Two Sum II), 15 (3Sum), "
        "26 (Remove Duplicates), 283 (Move Zeroes), 11 (Container With Most "
        "Water), 75 (Sort Colors / Dutch Flag). Template: while l < r: if "
        "cond(l, r): ... ; l += 1 (or r -= 1). "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://44 (pillar1.data_structures.array_string), "
        "kg://241 (parent lc-keyword-checklists). Anti-patterns: 没排序就用 "
        "对向双指针 (前提是 monotone); 用 nested loop 代替 (面试官等你想到 "
        "two-pointer 优化); l/r 边界条件搞反 (空数组 / n=1 没 guard).",
        ["Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "sliding-window",
        "Sliding Window / 滑动窗口",
        "数组/字符串子串 (subarray / substring) 题的标配 pattern, 双指针 "
        "[l, r] 维护一个 window, r 扩展, l 收缩, O(n) 完成 substring 性质 "
        "扫描. 两种子模式: (1) **fixed-size window** (r-l+1=k 固定) -- "
        "max sum of k consecutive / average of subarray; (2) **variable-size "
        "window** (条件触发 l 收缩) -- longest substring without repeating / "
        "min window substring. Trigger phrase: '连续子数组/子串', 'longest "
        "/ shortest / max / min subarray with property X', 'at most K of Y'. "
        "Canonical LC: 3 (Longest Substring Without Repeating), 76 (Min Window "
        "Substring), 209 (Min Size Subarray Sum), 239 (Sliding Window Maximum), "
        "438 (Find All Anagrams), 567 (Permutation in String). Template: l=0; "
        "for r in range(n): update_state(r); while not valid(): update_state(l); "
        "l += 1; ans = max(ans, r-l+1). Configurable: state 用 hashmap (字符 "
        "频率) / counter (匹配数) / running sum. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://44 (pillar1.data_structures.array_string), kg://241 (parent). "
        "Anti-patterns: 把 sliding-window 用在非连续 subarray (得用 DP 或 "
        "双指针其他变体); l 不收缩, 退化成 O(n^2); 忘记 update_state 双向 "
        "(扩张时 +1, 收缩时 -1) 导致 state 不对称.",
        ["DoorDash", "Google", "Uber"],
    ),
    (
        "binary-search-and-on-answer",
        "Binary Search + Binary Search on Answer / 二分查找 + 二分答案",
        "排序 / 单调函数上 O(log n) 查找的 pattern, 两层用法: (1) **direct "
        "binary search** -- 在有序数组找元素 / 找 lower_bound / 找 rotation "
        "point; (2) **binary search on answer (二分答案)** -- 在 [lo, hi] "
        "答案区间上二分, 用 feasibility check 函数判断 mid 是否可达. 第二种 "
        "是 senior signal 高频, e.g. 'min capacity to ship in D days', "
        "'split array largest sum'. Trigger phrase: '有序数组 / 找位置', "
        "'minimize the maximum / maximize the minimum', '答案在 [lo, hi] "
        "范围, 单调'. Canonical LC: 704 (Binary Search), 35 (Search Insert), "
        "33 (Search Rotated Sorted), 153 (Find Min in Rotated), 4 (Median Two "
        "Sorted Arrays), 875 (Koko Eating Bananas, BS on answer), 1011 (Capacity "
        "to Ship), 410 (Split Array Largest Sum). Template (BS on answer): "
        "lo, hi = min_ans, max_ans; while lo < hi: mid = (lo+hi)//2; if "
        "feasible(mid): hi = mid; else: lo = mid+1; return lo. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://52 (pillar1.algorithm_paradigms.binary_search), kg://241 (parent). "
        "Anti-patterns: lo/hi 边界写错 (off-by-one 是 BS 头号 bug, 写 invariant "
        "comment 'answer in [lo, hi]' or '[lo, hi)'); feasibility 函数 monotone "
        "性没验证就硬二分 (只有 feasible(x) -> feasible(x+1) 才能 BS); 没看到 "
        "'minimize max' 类题面就不想到 BS-on-answer.",
        ["Adobe", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "bfs-dfs-grid-traversal",
        "BFS / DFS Grid + Graph Traversal / 网格 + 图遍历",
        "图论题 baseline pattern, 决策点是 BFS vs DFS: (1) **BFS** 用 queue, "
        "层序扩展, 用于**最短路径 (无权图)** / level-order; (2) **DFS** 用 "
        "recursion 或 stack, 用于**全部路径 / 连通分量 / 拓扑序 / cycle "
        "detection**. Grid 题 (m x n 矩阵) 是最常见入口: 4-direction 邻接, "
        "用 visited set 或 in-place mark (e.g. grid[r][c]='#') 避免重复. "
        "Trigger phrase: '最短路径 (无权)', '连通分量个数', '岛屿数量', "
        "'最短桥梁', 'word ladder'. Canonical LC: 200 (Number of Islands, "
        "DFS or BFS), 994 (Rotting Oranges, multi-source BFS), 127 (Word "
        "Ladder, BFS), 695 (Max Area of Island), 417 (Pacific Atlantic), "
        "130 (Surrounded Regions), 542 (01 Matrix). Template (BFS): "
        "q=deque([start]); visited={start}; while q: node=q.popleft(); for "
        "nb in neighbors(node): if nb not in visited: visited.add(nb); "
        "q.append(nb). Multi-source BFS = 把所有 source 同时塞进 q 初始化. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://53 (pillar1.algorithm_paradigms.bfs_dfs), kg://241 (parent). "
        "Anti-patterns: 最短路径用 DFS (DFS 找到的不一定最短); 没 visited "
        "导致 cycle 死循环; 4-direction 写成 8-direction 没确认 (题面要 "
        "verify 邻接定义); BFS 用 list 而非 deque 拖到 O(n^2).",
        ["Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "backtracking-permutations-combinations",
        "Backtracking: Permutations / Combinations / Subsets",
        "穷举搜索 pattern, 用 recursion + state mutation + undo (回溯) 探索 "
        "所有解. 三种典型题: (1) **subsets** (2^n 子集) -- 每个元素 take/skip; "
        "(2) **permutations** (n! 排列) -- 每层选未用过的; (3) **combinations** "
        "(C(n,k)) -- 每层从 start 起选. 剪枝是 senior signal: 跳过重复 "
        "(sorted + skip if i > start and nums[i]==nums[i-1]), early termination "
        "(target - num < 0 -> break). Trigger phrase: 'all subsets / "
        "permutations / combinations', 'find all paths', 'N-Queens', "
        "'word search'. Canonical LC: 78 (Subsets), 90 (Subsets II), 46 "
        "(Permutations), 47 (Permutations II), 39 (Combination Sum), 40 "
        "(Combination Sum II), 79 (Word Search), 51 (N-Queens), 22 (Generate "
        "Parentheses). Template: def backtrack(path, choices): if done(path): "
        "result.append(path[:]); return; for c in choices: path.append(c); "
        "backtrack(path, next_choices(c)); path.pop(). "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://56 (pillar1.algorithm_paradigms.backtracking), kg://241 (parent). "
        "Anti-patterns: 忘记 path.pop() 导致 state 污染下层 recursion; "
        "result.append(path) 而非 path[:] (append 引用而非 copy, 最后全是 []); "
        "没剪枝跑 TLE (sorted + skip duplicate 必备); 用 list 模拟 visited "
        "导致 O(n^2) 查询 (用 set 或 bitmask).",
        ["LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "dynamic-programming-knapsack-lis-edit-distance",
        "Dynamic Programming: Knapsack / LIS / Edit Distance Family",
        "DP 是 LC pattern 中最大且最难诊断的 family. 5 大 canonical 子族: "
        "(1) **knapsack** (0/1 + unbounded) -- 选或不选, dp[i][w]; "
        "(2) **LIS** (longest increasing subsequence) -- O(n^2) DP 或 O(n log n) "
        "patience sort; (3) **edit distance / LCS** -- 二维网格 dp[i][j] "
        "比较两字符串; (4) **interval DP** -- dp[l][r] 区间合并 (matrix chain, "
        "burst balloons); (5) **bitmask DP** -- 状态压缩 (TSP, partition "
        "subsets). 抓 DP 的 4 步: 定义 state -> 写 transition -> 定 base case -> "
        "选填表方向 (top-down memo / bottom-up tabulation). Trigger phrase: "
        "'count number of ways', 'minimum cost / max profit', '能否 partition', "
        "'最长子序列 (非连续)'. Canonical LC: 322 (Coin Change, unbounded knapsack), "
        "416 (Partition Equal Subset Sum, 0/1), 300 (LIS), 1143 (LCS), 72 "
        "(Edit Distance), 312 (Burst Balloons, interval DP), 198 (House Robber), "
        "139 (Word Break), 887 (Egg Drop). Template: dp = [[base for _ in ..] "
        "for _ in ..]; for i in ...: for j in ...: dp[i][j] = transition(dp, i, j); "
        "return dp[-1][-1]. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://54 (pillar1.algorithm_paradigms.dynamic_programming), kg://241 (parent). "
        "Anti-patterns: 把 DP 当 backtracking 写 (没记忆化导致指数爆炸); "
        "state 定义不全 (LIS 只记 length 不记 ending element 错了); space "
        "优化没必要时硬搞 (先写 2D 再压成 1D); transition 写错方向 (knapsack "
        "0/1 的 weight loop 必须倒序).",
        ["Adobe", "Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "heap-topk-quickselect",
        "Heap + Top-K + Quickselect / 堆 + 前 K 大 + 快速选择",
        "Top-K / K-th element 类题的两种解: (1) **heap (min-heap of size K)** -- "
        "维护大小 K 的 min-heap, 全部 push 后 heap 顶就是第 K 大; O(n log K), "
        "适合 streaming (元素一边到一边处理); (2) **quickselect** -- partition "
        "递归到第 K 位置; 平均 O(n), 最坏 O(n^2) (用 random pivot 缓解); 适合 "
        "offline 全部已知. 3-axis streaming sketch (count-min / heavy-hitters / "
        "HyperLogLog) 是 streaming-K 的近似版, 看 kg://196 (pillar1.streaming_topk). "
        "Trigger phrase: 'k-th largest / smallest', 'top K frequent', 'k closest "
        "points', 'merge K sorted lists', 'streaming median'. Canonical LC: 215 "
        "(Kth Largest), 347 (Top K Frequent), 973 (K Closest Points), 23 (Merge "
        "K Sorted Lists, heap), 295 (Find Median from Data Stream, two heaps), "
        "703 (Kth Largest in Stream), 692 (Top K Frequent Words). Template "
        "(heap): import heapq; h = []; for x in arr: heapq.heappush(h, x); "
        "if len(h) > k: heapq.heappop(h); return h[0]. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://49 (pillar1.data_structures.heap_priority_queue), "
        "kg://196 (pillar1.streaming_topk), kg://241 (parent). "
        "Anti-patterns: 用 max-heap 找 top-K (heap 大小变成 n, O(n log n) -- "
        "min-heap of size K 才是 O(n log K)); quickselect 用 deterministic "
        "pivot 在 sorted input 上 TLE; Python heapq 默认 min-heap, 找 max 要 "
        "存 -x; streaming 题用 quickselect (无法 online).",
        ["Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "monotonic-stack",
        "Monotonic Stack / 单调栈",
        "栈里元素**严格单调 (递增 / 递减)** 的 stack, 用于 O(n) 求**下一个 "
        "更大/更小元素 (next greater / smaller)**, 是数组题里最高效的非 DP "
        "pattern 之一. 两种方向: (1) **从右往左扫** + **递减栈** -> 找右边 "
        "第一个比当前大的; (2) **从左往右扫** + **递增栈** -> pop 时 record "
        "区间. Trigger phrase: 'next greater / smaller element', 'largest "
        "rectangle in histogram', 'trapping rain water', 'daily temperatures'. "
        "Canonical LC: 496 (Next Greater Element I), 503 (Next Greater II, "
        "circular), 739 (Daily Temperatures), 84 (Largest Rectangle Histogram), "
        "85 (Maximal Rectangle), 42 (Trapping Rain Water), 901 (Online Stock "
        "Span). Template: stack = []; res = [-1]*n; for i in range(n): while "
        "stack and arr[stack[-1]] < arr[i]: j = stack.pop(); res[j] = i; "
        "stack.append(i); return res. (递减栈 -> 找右边 first greater 的 index.) "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://46 (pillar1.data_structures.stack_queue), kg://241 (parent). "
        "Anti-patterns: 单调栈方向选错 (找 next greater 用递增栈反了); "
        "存 value 而非 index (后续 record 区间宽度需要 index); 忘记栈非空 "
        "判定就 stack[-1] (IndexError); largest rectangle 题忘记最后 pad "
        "一个 sentinel (0 或 -inf) 让残留元素 flush.",
        ["Google", "Pinterest", "Uber"],
    ),
    (
        "prefix-sum-difference-array",
        "Prefix Sum + Difference Array / 前缀和 + 差分数组",
        "区间和 / 区间更新类题的 O(1) 查询 / O(1) 更新 pattern. 两个对偶 "
        "工具: (1) **prefix sum** P[i] = sum(arr[0..i-1]); 区间和 = "
        "P[r+1] - P[l]; 单次 O(1) 查询, 适合**多次区间求和 / 子数组和等于 K**. "
        "(2) **difference array** d[l] += v; d[r+1] -= v; 还原原数组用 prefix "
        "sum; 适合**多次区间加, 一次查询整体**. 进阶: 2D prefix sum (子矩阵和 "
        "O(1)) / hash map + prefix sum (subarray sum equals K). Trigger phrase: "
        "'sum of subarray (or 2D submatrix)', 'subarray sum equals k', "
        "'多次区间加 / 单次查询', 'count subarrays with property'. Canonical LC: "
        "303 (Range Sum Query 1D), 304 (Range Sum 2D), 560 (Subarray Sum "
        "Equals K), 974 (Subarray Sums Divisible by K), 1109 (Corporate "
        "Flight Bookings, difference array), 1248 (Count Number of Nice "
        "Subarrays). Template: P = [0]*(n+1); for i, v in enumerate(arr): "
        "P[i+1] = P[i] + v; range_sum(l, r) = P[r+1] - P[l]. Hash variant: "
        "count[0] = 1; cur = 0; for v in arr: cur += v; ans += count.get(cur-k, 0); "
        "count[cur] = count.get(cur, 0) + 1. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://44 (pillar1.data_structures.array_string), kg://241 (parent). "
        "Anti-patterns: prefix sum index 写成 P[i] 表示 sum[0..i] (不一致, "
        "推荐 sum[0..i-1] 让 range_sum(l,r) 公式干净); 差分数组忘记 r+1 边界 "
        "(d[r+1] -= v, 不是 d[r] -= v); subarray-sum-equals-K 用嵌套 loop "
        "代替 hash + prefix (TLE).",
        ["Google", "LinkedIn", "Uber"],
    ),
    (
        "intervals-merge-meeting-rooms",
        "Intervals: Merge / Insert / Meeting Rooms",
        "区间数组题 family, 抓住**先按 start 排序**这一招就解 80% 的题. "
        "5 个 canonical 子题: (1) **merge intervals** -- 排序后扫一遍, "
        "重叠合并; (2) **insert interval** -- 三段 (左独立 / 重叠合并 / "
        "右独立); (3) **meeting rooms II** (最少几间会议室) -- min-heap by "
        "end time, 或 sweep line (events sorted by time); (4) **non-overlapping "
        "intervals** -- 按 end 排序 + greedy 选最早 end; (5) **interval "
        "intersection** -- 双指针扫两个 intervals 数组. Trigger phrase: "
        "'merge / overlap intervals', 'minimum number of meeting rooms', "
        "'maximum number of non-overlapping events', '区间合并 / 区间求交'. "
        "Canonical LC: 56 (Merge Intervals), 57 (Insert Interval), 252 "
        "(Meeting Rooms I), 253 (Meeting Rooms II), 435 (Non-Overlapping "
        "Intervals), 986 (Interval List Intersections), 1288 (Remove Covered "
        "Intervals). Template (merge): intervals.sort(key=lambda x: x[0]); "
        "res = []; for s, e in intervals: if res and s <= res[-1][1]: "
        "res[-1][1] = max(res[-1][1], e); else: res.append([s, e]); return res. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://44 (pillar1.data_structures.array_string), kg://241 (parent). "
        "Anti-patterns: 没排序直接扫 (interval 题排序是前提); meeting rooms "
        "II 用 nested loop O(n^2) (heap 是 O(n log n)); 边界 inclusive vs "
        "exclusive 没确认 ([1,2] [2,3] 算重叠吗? 必须问 interviewer); insert "
        "题忘记加未访问尾部 interval.",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "trie-prefix-tree",
        "Trie / Prefix Tree / 字典树",
        "字符串前缀检索 pattern 的专用数据结构. Node 包含: children (dict "
        "char -> Node) + is_end (bool 标记是否完整 word). 三大用途: "
        "(1) **word dictionary** -- insert / search / startsWith; "
        "(2) **autocomplete** -- 找所有 with given prefix 的 word; "
        "(3) **word search II (board + words)** -- trie + DFS 一次扫完整张 "
        "board, 比逐个 word 单独 search 快 O(W) 倍. Trigger phrase: 'word "
        "dictionary', 'autocomplete / suggest', 'starts with', 'find words "
        "in board', 'replace words by root'. Canonical LC: 208 (Implement "
        "Trie), 211 (Add and Search Word, supports '.'), 212 (Word Search II), "
        "648 (Replace Words), 677 (Map Sum Pairs), 720 (Longest Word in "
        "Dictionary), 1268 (Search Suggestions System). Template: class "
        "Trie: def __init__(self): self.children = {}; self.is_end = False; "
        "def insert(self, w): node = self; for c in w: node = node.children."
        "setdefault(c, Trie()); node.is_end = True. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://50 (pillar1.data_structures.trie), kg://241 (parent). "
        "Anti-patterns: 用 nested dict 而非 class (能跑但难维护); is_end "
        "忘了 (search 'app' 在只插了 'apple' 的 trie 上误返 True); word "
        "search II 不用 trie 而是逐 word DFS (W*M*N*4^L 爆 TLE); 内存爆掉 "
        "没清理已用 word (找到一个 word 后从 trie 删掉防重复输出).",
        ["LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "union-find-dsu",
        "Union-Find / Disjoint Set Union / 并查集",
        "动态连通性 (dynamic connectivity) 数据结构, 用于 O(alpha(n)) ~ O(1) "
        "amortized 查询两个元素是否同一 component / 合并两个 component. 两个 "
        "标准优化: (1) **path compression** (find 时把链上所有节点直接指根); "
        "(2) **union by rank/size** (小树挂大树下). 4 大用途: (a) connected "
        "components count; (b) cycle detection in undirected graph; (c) MST "
        "(Kruskal); (d) offline query batching. Trigger phrase: '动态连通', "
        "'redundant connection', 'number of provinces / islands', 'accounts "
        "merge', 'min spanning tree (Kruskal)'. Canonical LC: 547 (Number "
        "of Provinces), 200 (Number of Islands, 也可 BFS), 684 (Redundant "
        "Connection), 721 (Accounts Merge), 1319 (Make Network Connected), "
        "305 (Number of Islands II, dynamic). Template: parent = list("
        "range(n)); rank = [0]*n; def find(x): while parent[x] != x: "
        "parent[x] = parent[parent[x]]; x = parent[x]; return x; def union("
        "a, b): ra, rb = find(a), find(b); if ra == rb: return False; if "
        "rank[ra] < rank[rb]: ra, rb = rb, ra; parent[rb] = ra; if rank[ra] "
        "== rank[rb]: rank[ra] += 1; return True. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://51 (pillar1.data_structures.union_find), kg://241 (parent). "
        "Anti-patterns: 没 path compression -> O(n) per find 退化; recursive "
        "find 在大 n 上 stack overflow (Python 用 iterative); union by rank "
        "和 union by size 混用; redundant-connection 题没意识到 'first edge "
        "that creates cycle' = first union returns False.",
        ["Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "topological-sort-course-schedule",
        "Topological Sort / 拓扑排序",
        "DAG (有向无环图) 的线性序排列 pattern, 保证所有边都从靠前节点指向 "
        "靠后. 两种实现: (1) **Kahn's algorithm (BFS)** -- 维护 in-degree, "
        "from in-degree=0 的节点开始扩展, 每次弹出后邻居 in-degree -1; "
        "(2) **DFS post-order reverse** -- DFS 后序入栈, 反转栈即拓扑序. "
        "BFS 版本更适合面试 (顺便检测 cycle: 若结果 size < n -> 有 cycle). "
        "Trigger phrase: 'course schedule (prerequisites)', 'task ordering', "
        "'alien dictionary', 'build order', 'find all topological orders'. "
        "Canonical LC: 207 (Course Schedule, 仅判定可行), 210 (Course Schedule "
        "II, 输出 order), 269 (Alien Dictionary), 310 (Min Height Trees, BFS "
        "from leaves), 444 (Sequence Reconstruction), 1136 (Parallel Courses). "
        "Template: indeg = [0]*n; graph = defaultdict(list); for u, v in edges: "
        "graph[u].append(v); indeg[v] += 1; q = deque(i for i in range(n) if "
        "indeg[i]==0); order = []; while q: u = q.popleft(); order.append(u); "
        "for v in graph[u]: indeg[v] -= 1; if indeg[v]==0: q.append(v); "
        "return order if len(order)==n else []. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://57 (pillar1.algorithm_paradigms.graph_algorithms), kg://241 (parent). "
        "Anti-patterns: 边的方向写反 (prerequisite a->b 表示 a 必须在 b 前, "
        "图里是 b -> a 还是 a -> b 必须 verify); 没 cycle check 直接 return "
        "order (course schedule 题里 cycle = 不可能完成); DFS 版本用了 visited "
        "但没区分 'in-progress' 和 'done' 三态, cycle 检测错; alien "
        "dictionary 没处理空 prefix matching (前缀长不算 lex 序冲突).",
        ["Adobe", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "linked-list-fast-slow-reverse",
        "Linked List: Fast/Slow Pointer + In-Place Reverse",
        "链表题三大核心 trick: (1) **fast/slow pointer** -- 快指针走 2 步 "
        "/ 慢指针走 1 步, 用于找中点 (slow 到 mid) / 检测环 (Floyd's "
        "tortoise and hare) / 找环入口 (相遇后 slow 从头, 快慢同步走再相遇); "
        "(2) **in-place reverse** -- 三指针 prev/cur/next 翻转方向, 不开新 "
        "list; (3) **dummy head** -- 简化 edge case (head 可能被删 / 替换). "
        "Trigger phrase: '反转链表', '检测链表环', '链表中点', '合并两个有序 "
        "链表', '删除倒数第 N 个节点'. Canonical LC: 206 (Reverse Linked "
        "List), 92 (Reverse Linked List II, 区间反转), 141 (Linked List Cycle), "
        "142 (Linked List Cycle II, 找入口), 876 (Middle of Linked List), "
        "21 (Merge Two Sorted Lists), 19 (Remove Nth From End), 234 (Palindrome "
        "Linked List). Template (reverse): prev=None; cur=head; while cur: "
        "nxt=cur.next; cur.next=prev; prev=cur; cur=nxt; return prev. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://47 (pillar1.data_structures.linked_list), kg://241 (parent). "
        "Anti-patterns: reverse 时忘记 nxt=cur.next 备份导致丢链; fast/slow "
        "没处理偶数长度 (mid 选靠左还是靠右? while fast and fast.next vs "
        "while fast.next and fast.next.next 决定); cycle 检测找入口忘了 "
        "Floyd 第二阶段 (相遇后 slow 必须从 head 重启).",
        ["Meta", "Pinterest", "Uber"],
    ),
    (
        "ml-coding-from-scratch",
        "ML Coding: kNN / k-Means / LinReg / LogReg from Scratch",
        "ML 岗特有的 coding round 题型 (区别于纯 LC), 要求**手写实现**经典 "
        "ML 算法, 无 sklearn / pytorch. 5 个最高频题: (1) **kNN classifier** "
        "-- pairwise distance + heap top-k + majority vote; (2) **k-means** -- "
        "随机初始化 + assign step + update centroid 直到收敛; (3) **linear "
        "regression** -- normal equation (X^T X)^-1 X^T y, 或 SGD; (4) "
        "**logistic regression** -- sigmoid + cross-entropy loss + gradient; "
        "(5) **PCA / SVD truncated** -- 协方差矩阵 + eigendecomposition (numpy "
        "底层). Trigger phrase: 'implement kNN / k-means / logistic regression "
        "from scratch', 'no sklearn please', 'using only numpy', 'write the "
        "training loop'. 关键 sub-skills: numpy broadcasting (避免 for-loop), "
        "numerical stability (logsumexp 防 overflow), gradient 推导 (能写在 "
        "纸上). Canonical 'LC for ML' (没有标准 leetcode_id, 通常题面自定义): "
        "(a) given (X, y), implement fit + predict for linear regression "
        "with L2 reg; (b) implement k-means with k-means++ init; (c) "
        "implement softmax regression with cross-entropy. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://11 (pillar1.mle_coding), "
        "kg://60 (pillar1.mle_coding.implement_ml_algorithms), kg://241 (parent). "
        "Anti-patterns: 用 for-loop 算 pairwise distance (numpy broadcasting "
        "X[:,None,:] - Y[None,:,:] 一行解决); k-means 没处理 empty cluster "
        "(若某 centroid 没 assigned point 会 NaN); logistic regression 直接 "
        "log(p) 没 log1pexp 数值不稳定; normal equation 在 X^T X 奇异时 crash "
        "(用 np.linalg.lstsq 或加 ridge regularization).",
        ["DoorDash", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """SHA-256 of all 'meta-prep/lc-keyword-checklists%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description, relevant_companies "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/lc-keyword-checklists/%' "
        "ORDER BY path",
        (PARENT_PATH,),
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def update_parent_description(
    conn: sqlite3.Connection, parent_id: int, current_desc: str | None
) -> str:
    """Update parent description if still TODO; otherwise SKIP."""
    if current_desc and PARENT_TODO_MARKER in current_desc:
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (PARENT_DESCRIPTION_NEW, parent_id),
        )
        return "UPDATED"
    if current_desc == PARENT_DESCRIPTION_NEW:
        return "SKIPPED"
    raise RuntimeError(
        f"[CONFLICT] parent description has been edited to something "
        f"other than the TODO marker or the seed's target text. "
        f"Refusing to overwrite. Current: {current_desc!r}"
    )


def upsert_child(
    conn: sqlite3.Connection,
    *,
    parent_id: int,
    slug: str,
    title: str,
    description: str,
    relevant_companies_csv: str,
) -> tuple[str, int]:
    """Insert child if absent; SKIP if present with matching content."""
    path = f"{PARENT_PATH}/{slug}"
    existing = conn.execute(
        "SELECT id, title, description, relevant_companies "
        "FROM framework_nodes WHERE path = ?",
        (path,),
    ).fetchone()
    if existing is not None:
        node_id, ex_title, ex_desc, ex_companies = existing
        if (ex_title == title and ex_desc == description
                and (ex_companies or "") == relevant_companies_csv):
            return "SKIPPED", node_id
        raise RuntimeError(
            f"[CONFLICT] path={path!r} exists but content has drifted from "
            f"seed. title_match={ex_title == title} "
            f"desc_match={ex_desc == description} "
            f"companies_match={(ex_companies or '') == relevant_companies_csv}. "
            f"Refusing to overwrite hand-edited content; resolve by either "
            f"reverting the edit or updating the seed."
        )
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct, relevant_companies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, 2, title, description,
         0.7, "P1", "not_started", 0.0, relevant_companies_csv),
    )
    return "INSERTED", cur.lastrowid


CROSS_LINK_RE = re.compile(r"(kg://\d+|sd://[a-z0-9-]+)")


def assert_promotion_threshold() -> None:
    """Static AC: each cluster has >=3 P0+P1 sources, all valid names; >=4 children;
    each description embeds at least one kg:// or sd:// cross-link."""
    if len(CLUSTERS) < 4:
        raise AssertionError(
            f"[AC-FAIL] only {len(CLUSTERS)} clusters defined; AC requires >=4"
        )
    seen_slugs: set[str] = set()
    for slug, _title, description, companies in CLUSTERS:
        if slug in seen_slugs:
            raise AssertionError(f"[AC-FAIL] duplicate slug {slug!r}")
        seen_slugs.add(slug)
        if len(companies) < 3:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has only {len(companies)} sources; "
                f"promotion threshold is >=3"
            )
        if len(companies) != len(set(companies)):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has duplicate sources: {companies}"
            )
        invalid = set(companies) - P0P1_COMPANY_NAMES
        if invalid:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} references non-P0+P1 companies: "
                f"{sorted(invalid)}"
            )
        if not CROSS_LINK_RE.search(description):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} description has no kg:// or sd:// "
                f"cross-link"
            )


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Update parent description (if TODO) and seed N child clusters."""
    counts = {"INSERTED": 0, "UPDATED": 0, "SKIPPED": 0}

    parent = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path = ?",
        (PARENT_PATH,),
    ).fetchone()
    if parent is None:
        raise RuntimeError(
            f"[FAIL] parent {PARENT_PATH!r} does not exist; "
            f"run scripts/seed_meta_prep_pillar.py first (T-P1-800)."
        )
    parent_id, parent_desc = parent
    parent_action = update_parent_description(conn, parent_id, parent_desc)
    counts[parent_action] += 1
    print(f"[{parent_action}] parent id={parent_id} path={PARENT_PATH}")

    for slug, title, description, companies in CLUSTERS:
        relevant_companies_csv = ",".join(companies)
        action, child_id = upsert_child(
            conn,
            parent_id=parent_id,
            slug=slug,
            title=title,
            description=description,
            relevant_companies_csv=relevant_companies_csv,
        )
        counts[action] += 1
        n_links = len(CROSS_LINK_RE.findall(description))
        print(
            f"[{action}] child  id={child_id} "
            f"slug={slug} sources={len(companies)} cross_links={n_links}"
        )

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    assert_promotion_threshold()
    print(
        f"[AC-OK] all {len(CLUSTERS)} clusters have >=3 valid P0+P1 sources "
        f"and embed at least one kg:// or sd:// cross-link"
    )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes "
            "WHERE path = ? OR path LIKE 'meta-prep/lc-keyword-checklists/%'",
            (PARENT_PATH,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(
        f"[SUMMARY] inserted={counts['INSERTED']} "
        f"updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total_in_subtree={total}"
    )

    expected_total = 1 + len(CLUSTERS)
    if total != expected_total:
        print(f"[FAIL] Expected {expected_total} rows, got {total}")
        sys.exit(1)
    touched = counts["INSERTED"] + counts["UPDATED"] + counts["SKIPPED"]
    if touched != expected_total:
        print(f"[FAIL] Expected to touch {expected_total} nodes, touched {touched}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
