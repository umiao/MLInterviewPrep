<!-- UBER_LC_INDEX_V1 -->

# Uber LC 题库索引视图 (Index View)

> **47 道**带 Uber tag 且**已有题解**的 LeetCode 题目快速导航。
> 与 *Uber BPS LeetCode Solutions Guide* (深度精讲) 是兄弟关系——本文档是**宽度索引**, 那是**深度题解**, 索引中带 `lc://N` 的链接点击会以 SlideOverPanel 弹出该题完整笔记。
>
> **覆盖**: 47 题 (38 来自用户 curated 50-list 中已有题解的部分 + 9 来自 doc id=30 独占题), 按知识点 / pattern 分 10 组, 组内按 LeetCode id 升序。
> **`[NEW]`**: 标 `[NEW]` 的 6 道是 2026-04 期间新加入的, 在 `problem_company_tags` 关系表中也有显式 Uber 关联。
>
> **未列入索引** (无题解, 待补): LC 679, 719, 1101, 1475, 1931, 2092, 2389, 2561, 3419, 3629; LC 2954 (DB 缺录入)。

---

##  概览

| 维度 | 数量 |
| --- | --- |
| 总题数 | **47** |
| 分组数 | 10 |
| `[NEW]` 标记 | 6 |
| 来自 doc id=30 (深度精讲) | 19 (其中 19 道在本索引中) |

##  分组总览

| # | 分组 | 题数 | LC ids |
| --- | --- | --- | --- |
| 1 | [Tree / 树遍历 + Tree DP](#tree-树遍历-tree-dp) | 7 | 230, 337, 545, 549, 987, 2791, 2858 |
| 2 | [Graph / BFS / DFS / Grid](#graph-bfs-dfs-grid) | 9 | 200, 207, 210, 269, 815, 864, 994, 1020, 1197 |
| 3 | [Union-Find / 并查集](#union-find-并查集) | 5 | 305, 547, 827, 1697, 2503 |
| 4 | [Stateful DS Design / 设计题](#stateful-ds-design-设计题) | 6 | 146, 362, 380, 855, 1244, 2402 |
| 5 | [Heap / TopK / Greedy](#heap-topk-greedy) | 3 | 23, 502, 1696 |
| 6 | [Backtracking / Trie](#backtracking-trie) | 3 | 17, 79, 212 |
| 7 | [Sliding Window / Two Pointers](#sliding-window-two-pointers) | 3 | 121, 977, 1438 |
| 8 | [Binary Search / 二分（含答案二分）](#binary-search-二分含答案二分) | 4 | 162, 410, 981, 2861 |
| 9 | [DP / 区间 / 字符串](#dp-区间-字符串) | 2 | 5, 56 |
| 10 | [Bit / Greedy / Misc](#bit-greedy-misc) | 5 | 384, 427, 1428, 1429, 2571 |

---

## Tree / 树遍历 + Tree DP

- [LC 230. Kth Smallest Element in a BST](lc://230) `[medium]` — 在 BST 中找第 k 小; 中序遍历到第 k 个停, $O(h+k)$.  *pattern: `tree`*
- [LC 337. House Robber III](lc://337) `[medium]` — 树形 DP; 每节点返回 (rob, no_rob) 二元组取最优.  *pattern: `tree`*
- [LC 545. Boundary of Binary Tree](lc://545) `[medium]` — 二叉树边界; 一遍 DFS + 4 状态 flag (ROOT/LEFT/RIGHT/INNER), deque appendleft 收右边界.  *family: `tree_traversal` | pattern: `tree_boundary_dfs`*
- [LC 549. Binary Tree Longest Consecutive Sequence II](lc://549) `[medium]` — 树上最长连续路径 (双向); 后序返回 (inc, dec) 同时更新答案.  *pattern: `tree`*
- [LC 987. Vertical Order Traversal of a Binary Tree](lc://987) `[hard]` — 按列遍历; DFS 携带 (col, row) 后按 (col, row, val) 排序输出.  *pattern: `tree`*
- [LC 2791. Count Paths That Can Form a Palindrome in a Tree](lc://2791) `[medium]` — 树上回文路径计数; bitmask XOR + DFS, 同奇偶性子树两两组合.  *family: `tree_dp_rerooting` | pattern: `tree`*
- [LC 2858. Minimum Edge Reversals So Every Node Is Reachable](lc://2858) `[medium]` — Tree DP rerooting; 一次 DFS 算根, 二次 DFS 换根传播.  *family: `tree_dp_rerooting` | pattern: `tree`*

## Graph / BFS / DFS / Grid

- [LC 200. Number of Islands](lc://200) `[medium]` — 岛屿计数; DFS / BFS 染色, $O(mn)$.  *family: `graph_grid_traversal` | pattern: `graph`*
- [LC 207. Course Schedule](lc://207) `[medium]` — 拓扑排序判环; Kahn (BFS) 或 DFS 三色.  *pattern: `graph`*
- [LC 210. Course Schedule II](lc://210) `[medium]` — 拓扑排序输出顺序; Kahn 法直接得序列.  *pattern: `graph`*
- [LC 269. Alien Dictionary](lc://269) `[hard]` — 外星字典推字符顺序; 相邻单词比 → 建图 → 拓扑.  *family: `graph_topo_sort` | pattern: `graph`*
- [LC 815. Bus Routes](lc://815) `[hard]` — 公交换乘最少次数; **BFS on stops** (而非 routes), 用 stop_to_routes 映射加速.  *pattern: `graph`*
- [LC 864. Shortest Path to Get All Keys](lc://864) `[hard]` — 状态压缩 BFS; 状态 = (位置, 持有钥匙 bitmask).  *family: `bfs_state_space` | pattern: `bfs_state_compression`*
- [LC 994. Rotting Oranges](lc://994) `[medium]` — 多源 BFS; 所有 rotten 同时入队, 层数 = 时间.  *pattern: `graph`*
- [LC 1020. Number of Enclaves](lc://1020) `[medium]` — 飞地计数; 反向思路, 从边界 DFS 标记可达陆地后数剩余.  *pattern: `graph`*
- [LC 1197. Minimum Knight Moves](lc://1197) `[medium]` — 马最少步; BFS + 对称剪枝到第一象限.  *pattern: `graph`*

## Union-Find / 并查集

- [LC 305. Number of Islands II](lc://305) `[hard]` — 在线添陆地; UF 维护连通分量数, 新格 union 上下左右.
- [LC 547. Number of Provinces](lc://547) `[medium]` — 朋友圈数; UF 模板, 邻接矩阵遍历.  *pattern: `union-find`*
- [LC 827. Making A Large Island](lc://827) `[hard]` — 翻一格 0 后最大岛; UF 预标记每岛大小, 枚举 0 格累加邻岛 (用 set 去重). **[NEW]**
- [LC 1697. Checking Existence of Edge Length Limited Paths](lc://1697) `[hard]` — 离线查询 + 排序 + UF; 边按权重升序合并到 limit 阈值.  *pattern: `union-find`*
- [LC 2503. Maximum Number of Points From Grid Queries](lc://2503) `[hard]` — 离线查询 + UF + 多源 BFS; 按 query 阈值递增合并格子.  *family: `offline_queries_dsu` | pattern: `graph`*

## Stateful DS Design / 设计题

- [LC 146. LRU Cache](lc://146) `[medium]` — LRU Cache; HashMap + 双向链表, get/put 均 $O(1)$.  *family: `stateful_ds_design` | pattern: `linked_list`*
- [LC 362. Design Hit Counter](lc://362) `[medium]` — 5min 滑窗计数; 60 桶循环缓冲 或 deque 弹尾.  *family: `stateful_ds_design` | pattern: `circular-buffer`*
- [LC 380. Insert Delete GetRandom O(1)](lc://380) `[medium]` — Insert / Delete / GetRandom $O(1)$; 数组 + map, 删除时 swap-pop.
- [LC 855. Exam Room](lc://855) `[medium]` — 考场座位最大化最小距离; 排序列表 + 扫相邻对中点 + 端点.  *family: `stateful_ds_design` | pattern: `sorted_insertion_simulation`*
- [LC 1244. Design A Leaderboard](lc://1244) `[medium]` — 玩家分数榜; HashMap + 全排序或 BIT 加速 topK.  *family: `stateful_ds_design`*
- [LC 2402. Meeting Rooms III](lc://2402) `[hard]` — 双堆模拟 (空闲房 + 占用房); 按开始时间安排会议.

## Heap / TopK / Greedy

- [LC 23. Merge k Sorted Lists](lc://23) `[hard]` — k 路归并; 最小堆维护每路头, $O(N \log k)$.  *pattern: `heap`*
- [LC 502. IPO](lc://502) `[hard]` — IPO 双堆; 入门按 capital 排小顶, 满足资本者入大顶按 profit.  *family: `heap_greedy` | pattern: `sort_heap_greedy`*
- [LC 1696. Jump Game VI](lc://1696) `[medium]` — DP + 单调双端队列; $dp[i] = nums[i] + \max(dp[i-k..i-1])$.  *pattern: `Dynamic Programming`*

## Backtracking / Trie

- [LC 17. Letter Combinations of a Phone Number](lc://17) `[medium]` — 数字键盘字母组合; 经典回溯, 树深 = 数字位数.  *pattern: `backtracking`*
- [LC 79. Word Search](lc://79) `[medium]` — 网格找单词; DFS + 临时标记 + 回溯还原.  *pattern: `backtracking`*
- [LC 212. Word Search II](lc://212) `[hard]` — 网格找多词; Trie + DFS, 沿 trie 走避免重复探查每个单词.  *family: `trie_multiword` | pattern: `trie`*

## Sliding Window / Two Pointers

- [LC 121. Best Time to Buy and Sell Stock](lc://121) `[easy]` — 单次买卖; 维护历史最小 + 当前差最大, 一次扫描.  *pattern: `sliding_window`*
- [LC 977. Squares of a Sorted Array](lc://977) `[easy]` — 已排序数组平方; 双指针从两端比绝对值, 倒序填结果.  *pattern: `two-pointers`*
- [LC 1438. Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit](lc://1438) `[medium]` — 滑窗 + 单调双队列同时维护 max / min, 差超 limit 时左指针推进.  *pattern: `sliding_window`*

## Binary Search / 二分（含答案二分）

- [LC 162. Find Peak Element](lc://162) `[medium]` — 找任一峰值; 二分 nums[mid] vs nums[mid+1] 决定方向.
- [LC 410. Split Array Largest Sum](lc://410) `[hard]` — 分 m 段最小化最大段和; **二分答案** + 贪心可行性 check.
- [LC 981. Time Based Key-Value Store](lc://981) `[medium]` — 按时间戳查值; 每 key 一个 (ts, val) 列表, 二分查 ≤ ts 的最大.  *pattern: `binary-search`*
- [LC 2861. Maximum Number of Alloys](lc://2861) `[medium]` — **二分答案**; check(val) 遍 k 机器算 requiredBudget, 'find largest valid' 模板.  *family: `binary_search_on_answer` | pattern: `binary_search`*

## DP / 区间 / 字符串

- [LC 5. Longest Palindromic Substring](lc://5) `[medium]` — 最长回文子串; 中心扩展 $O(n^2)$ 或 Manacher $O(n)$.  *pattern: `dp`*
- [LC 56. Merge Intervals](lc://56) `[medium]` — 区间合并; 按起点排序后扫描合并重叠, 经典 interval 模板.  *pattern: `interval`*

## Bit / Greedy / Misc

- [LC 384. Shuffle an Array](lc://384) `[medium]` — Fisher-Yates 洗牌; 每步从 [i, n-1] 随机 swap, 与 reservoir sampling 同款望远镜概率. **[NEW]**  *family: `randomized_algorithms` | pattern: `fisher_yates_shuffle`*
- [LC 427. Construct Quad Tree](lc://427) `[medium]` — 四叉树构造; 递归四分, 全同则叶节点否则建内部节点. **[NEW]**
- [LC 1428. Leftmost Column with at Least a One](lc://1428) `[medium]` — 行排序矩阵找最左 1; 阶梯法 $O(m+n)$ 从右上往左下走. **[NEW]**
- [LC 1429. First Unique Number](lc://1429) `[medium]` — 流式找首个唯一; 哈希计数 + 双向链表维护当前唯一队列, $O(1)$ 摊还. **[NEW]**
- [LC 2571. Minimum Operations to Reduce an Integer to 0](lc://2571) `[medium]` — $\pm 2^k$ 最少操作; 位运算贪心, `n & 3 == 3` 加否则减, 进位链合并 1-run. **[NEW]**  *family: `bit_manipulation` | pattern: `bit_greedy`*

---

## 维护说明

本文档由 `scripts/seed_uber_lc_index.py` 生成，sentinel = `<!-- UBER_LC_INDEX_V1 -->`。
添加 / 删除题目: 编辑脚本里的 `GROUPS` 列表后重跑脚本; 幂等替换 `company_documents` 中本 sentinel 标记的整个内容。
