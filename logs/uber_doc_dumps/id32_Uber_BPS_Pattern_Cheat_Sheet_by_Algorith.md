# Uber BPS -- 算法模式速查表

> 按算法模式组织的快速参考。每个部分：何时识别该模式、模板方法、所有使用该模式的 Uber BPS 题目以及复杂度。
>
> 来源：`uber_bps_lc_solutions.md`（19道 **LC (LeetCode)** 题）、`uber_bps_custom_solutions.md`（25道自定义题）
>
> Task: T-P1-247

---

## Table of Contents

1. [BFS / Multi-source BFS](#1-bfs--multi-source-bfs)
2. [DFS / Backtracking](#2-dfs--backtracking)
3. [Tree DP / Tree Traversal](#3-tree-dp--tree-traversal)
4. [Union Find (Disjoint Set)](#4-union-find-disjoint-set)
5. [Binary Search](#5-binary-search)
6. [Dynamic Programming](#6-dynamic-programming)
7. [Greedy](#7-greedy)
8. [Heap (Priority Queue)](#8-heap-priority-queue)
9. [Sliding Window](#9-sliding-window)
10. [Monotonic Stack](#10-monotonic-stack)
11. [Two Pointers](#11-two-pointers)
12. [Object-Oriented Design (OOD)](#12-object-oriented-design-ood)
13. [Grid / Matrix](#13-grid--matrix)
14. [Bitmask Techniques](#14-bitmask-techniques)
15. [Complexity Summary Table](#15-complexity-summary-table)
16. [Pattern Recognition Decision Tree](#16-pattern-recognition-decision-tree)

---

## 1. BFS / Multi-source BFS

### When to recognize（何时识别）

- "最短路径"——无权图或网格
- "最少步数/移动次数"到达目标
- 从多个源头同时扩散/感染
- 逐层探索（距离为 k 的所有节点）
- "最近出口"或"到边界的最短距离"

### Template（模板）

```python
from collections import deque

def bfs(graph, start, target):
    q = deque([(start, 0)])
    visited = {start}
    while q:
        node, dist = q.popleft()
        if node == target:
            return dist
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append((neighbor, dist + 1))
    return -1
```

**多源 BFS (Multi-source BFS)**：在开始之前将所有源节点以距离0入队。

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 994](lc://994) Rotting Oranges | 多源 BFS | 所有腐烂橘子同时开始 | O(mn) | O(mn) |
| [LC 1020](lc://1020) Number of Enclaves | 边界 BFS | 从边界 flood-fill，计数剩余 | O(mn) | O(mn) |
| [LC 1197](lc://1197) Min Knight Moves | 带剪枝的 BFS | 对称性：仅在第一象限工作 | O(xy) | O(xy) |
| [LC 815](lc://815) Bus Routes | 路线图上的 BFS | 节点 = 路线，边 = 共享站点 | O(sum routes) | O(sum routes) |
| [LC 2503](lc://2503) Max Grid Points | BFS + 排序查询 | 按升序处理查询，扩展前沿 | O(mn log mn) | O(mn) |
| Custom #7 Circular Jump | 环形数组 BFS | 取模运算处理环绕 | O(n) | O(n) |
| Custom #22 Grid Nearest Exit | 标准网格 BFS | 从所有出口多源 BFS，找最小值 | O(mn) | O(mn) |
| Custom #23 Lock Combination | 状态空间 BFS | 状态 = 数字组合，10^n 空间 | O(10^n * n) | O(10^n) |
| Custom #25 City Graph BFS Sort | BFS + Dijkstra | 最短路径后按距离排序 | O(V+E + V log V) | O(V+E) |

### Tips（技巧）

- 网格 BFS：4方向 `[(0,1),(0,-1),(1,0),(-1,0)]`，内联检查边界。
- 多源：先将所有源入队，再 BFS -- 得到正确的最小距离。
- 如果图有权重，BFS 不适用 -- 使用 **Dijkstra**（基于堆的 BFS）。

---

## 2. DFS / Backtracking

### When to recognize（何时识别）

- "生成所有组合/排列"
- "是否存在路径"（存在性，非最短）
- "在网格中搜索单词"
- "所有满足约束的有效配置"
- 电话号码字母组合、子集生成

### Template (Backtracking)（回溯模板）

```python
def backtrack(state, choices, result):
    if is_complete(state):
        result.append(state.copy())
        return
    for choice in choices:
        if is_valid(choice, state):
            state.add(choice)
            backtrack(state, choices, result)
            state.remove(choice)  # undo
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 79](lc://79) Word Search | 网格 **DFS (Depth-First Search，深度优先搜索)** + 回溯 | 用 '#' 原地标记已访问，恢复 | O(mn * 3^L) | O(L) |
| [LC 79](lc://79) variant: 8-dir straight | 线性扫描，无回溯 | 每个起点一个方向——简单得多 | O(mn * 8 * L) | O(1) |
| [LC 17](lc://17) Letter Combos | 回溯 | 数字映射到字符，枚举 | O(4^n * n) | O(n) |

### Tips（技巧）

- 标记-恢复：原地修改网格（`board[i][j] = '#'`），DFS 后恢复。
- 提前终止：剪枝无法得到有效结果的分支。
- 对于"计数"问题，返回整数而非收集所有解。

---

## 3. Tree DP / Tree Traversal

### When to recognize（何时识别）

- "树路径上可达的最大/最小值"
- "树形排列的房屋抢劫"（取/跳决策）
- "树中最长连续序列"
- "BST 中第 k 小/大"
- "垂直/层序遍历"
- 每个节点基于子节点的子答案贡献最终答案

### Template (Tree DP)（树形 DP 模板）

```python
def tree_dp(root):
    best = [0]

    def dfs(node):
        if not node:
            return (0, 0)  # (option_a, option_b)
        left = dfs(node.left)
        right = dfs(node.right)
        take = node.val + left[1] + right[1]   # take this node
        skip = max(left) + max(right)           # skip this node
        best[0] = max(best[0], take, skip)
        return (take, skip)

    dfs(root)
    return best[0]
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 230](lc://230) Kth Smallest BST | 中序遍历 | 迭代中序，在第 k 个停止 | O(H+k) | O(H) |
| [LC 230](lc://230) variant: Kth Largest | 反向中序 | Right -> root -> left | O(H+k) | O(H) |
| [LC 230](lc://230) follow-up: Morris | O(1) 空间遍历 | 线索化前驱节点 | O(n) | O(1) |
| [LC 230](lc://230) follow-up: Augmented | 存储子树大小 | 通过 left_count 实现 O(H) 查找 | O(H) | O(1) |
| [LC 337](lc://337) House Robber III | 树形 **DP (Dynamic Programming，动态规划)** (取/跳) | 每个节点返回 (rob, skip) 对 | O(n) | O(H) |
| [LC 549](lc://549) Longest Consecutive II | 树形 DP (递增/递减) | 同时追踪递增和递减长度 | O(n) | O(H) |
| [LC 987](lc://987) Vertical Traversal | **BFS (Breadth-First Search，广度优先搜索)** + 列追踪 | 按 (col, row, val) 排序 | O(n log n) | O(n) |
| Custom #14 N-ary Tree 3-Part | DFS 子树操作 | N叉树上的序列化、LCA、子树求和 | O(n) | O(H) |

### Tips（技巧）

- **BST (Binary Search Tree，二叉搜索树)** 性质：中序 = 有序。用此性质解第 k 小元素。
- 树形 DP 签名：`dfs(node) -> tuple`。元组捕获所有需要的状态。
- "经过节点的路径" = 左贡献 + 右贡献 + 节点值。
- Morris 遍历：O(1) 空间但修改/恢复树——面试中需提及。

---

## 4. Union Find (Disjoint Set)（并查集）

### When to recognize（何时识别）

- "连通分量数"
- "节点是否在同一组？"
- "随时间合并组"（在线连通性）
- "离线处理按权重/限制排序的查询"
- "省份/朋友圈/岛屿计数"

### Template（模板）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 547](lc://547) Number of Provinces | 基础 UF 或 DFS | 计数不同的根 | O(n^2 alpha(n)) | O(n) |
| [LC 1697](lc://1697) Edge Length Limited | 离线查询 + **UF (Union Find，并查集)** | 按权重排序边和查询 | O((E+Q) log) | O(n+Q) |
| [LC 1697](lc://1697) variant: weight >= k | 反向排序 | 按降序处理边权重 | O((E+Q) log) | O(n+Q) |
| Custom #3 Rider Connection | UF + BFS 重建 | UF 处理连接，BFS 处理屏蔽事件 | O(E alpha(N)) | O(N) |

### Tips（技巧）

- **离线查询技巧**：将边和查询一起排序，同步遍历。
- 路径压缩 + 按秩合并 = 每次操作近 O(1)（摊销）。
- 对于"撤销"操作（屏蔽/断开），UF 不支持撤销——使用 BFS 重建或离线逆序处理。
- 计数分量：`len(set(find(i) for i in range(n)))`。

---

## 5. Binary Search（二分查找）

### When to recognize（何时识别）

- "某值的最小/最大"且可行性具有单调性
- "在有序数组中搜索"或"有序 + 旋转"
- "前缀和 + 区间查询"
- "二分答案"（参数化搜索）
- "找阈值/边界"

### Template (Binary Search on Answer)（二分答案模板）

```python
def binary_search_on_answer(lo, hi, is_feasible):
    while lo < hi:
        mid = (lo + hi) // 2
        if is_feasible(mid):
            hi = mid      # try smaller (minimize)
        else:
            lo = mid + 1  # need larger
    return lo
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 981](lc://981) TimeMap | 时间戳上的 **BS (Binary Search，二分查找)** | 在有序时间戳列表上 bisect_right | O(log n) get | O(n) |
| [LC 977](lc://977) Squares Sorted (related) | 有序输入 | 双指针比 BS 更好 | O(n) | O(n) |
| Custom #1 Purchase Optimization | 前缀和 + BS | 在前缀和上二分查找预算 | O(n log n + q log n) | O(n) |
| Custom #4 Elevator BS | 模拟 + BS | 二分查找最优楼层 | O(n log n) | O(n) |
| Custom #13 Elevator/Stairs Energy | 三分/二分查找 | 单峰函数——三分查找 | O(n log n) | O(1) |
| Custom #15 Max Throughput Budget | 二分答案 | "能否在预算 B 下达到吞吐量 T？" | O(n log T) | O(1) |

### Tips（技巧）

- **前缀和 + 二分查找**：用于"预算内最大数量"的经典组合。
- **二分答案**：定义 `is_feasible(x)` 并二分查找 min/max x。
- **三分查找**：用于单峰函数（一个峰/谷）。
- 始终验证：`lo` 还是 `hi` 给出答案？Off-by-one 是 BS 的头号 bug。

---

## 6. Dynamic Programming（动态规划）

### When to recognize（何时识别）

- "每步有选择的最大/最小得分"
- "到达目标的方式数"
- "能否到达终点？"（可变跳跃）
- 重叠子问题 + 最优子结构
- 树上"换根"（计算每个根的答案）

### Template (Re-rooting DP)（换根 DP 模板）

```python
def rerooting_dp(n, adj):
    dp = [0] * n
    # Step 1: DFS from node 0 to compute dp[0]
    def dfs(node, parent):
        cost = 0
        for neighbor, edge_cost in adj[node]:
            if neighbor != parent:
                cost += edge_cost + dfs(neighbor, node)
        return cost
    dp[0] = dfs(0, -1)

    # Step 2: Propagate to all nodes
    def reroot(node, parent):
        for neighbor, edge_cost in adj[node]:
            if neighbor != parent:
                dp[neighbor] = dp[node] + delta(edge_cost)
                reroot(neighbor, node)
    reroot(0, -1)
    return dp
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 1696](lc://1696) Jump Game VI | DP + 单调双端队列 | 滑动窗口最大值实现 O(n) DP 转移 | O(n) | O(k) |
| [LC 1696](lc://1696) variant: prime jumps | DP + 筛法 | 预计算以3结尾的素数作为跳跃大小 | O(n*P) | O(n) |
| [LC 2858](lc://2858) Min Edge Reversals | 换根 DP | 计算根0，每条边 +1/-1 传播 | O(n) | O(n) |
| Custom #8 Robot Distance Grid | DP 预计算 | 通过网格 DP 预计算距离 | O(mn) | O(mn) |
| Custom #18 Jump Game Prime | DP + 筛法 | 跳 +1 或 +以3结尾的素数 | O(n*P) | O(n) |
| Custom #19 Min Edge Reversal | 换根 DP | 同 [LC 2858](lc://2858) | O(n) | O(n) |
| Custom #24 Non-overlapping Triples | 排序 + DP/前缀 | 排序区间，前缀计数实现不重叠 | O(n^2) | O(n) |

### Tips（技巧）

- **换根 DP**：两遍（根0的 DFS，然后传播）。关键：用 O(1) 转移从 dp[parent] 表达 dp[child]。
- **单调双端队列 DP**：当转移为 `dp[i] = max(dp[j] for j in window) + cost` 时使用双端队列。
- **DP + 筛法**：预计算素数一次，用作跳跃表。
- 注意边反转问题中的1-indexed 输入。

---

## 7. Greedy（贪心）

### When to recognize（何时识别）

- "最少操作次数"且有明确的局部最优选择
- "分配任务以最小化总成本"
- 排序 + 贪心选择给出最优解
- 每个选择独立（无未来后悔）

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #9 Min Ops n->0 | 贪心/NAF | 使用最大负斐波那契数幂 / 特殊移动 | O(log n) | O(1) |
| Custom #17 Task Assignment | 按差值排序 | 按 cost_A - cost_B 排序，最优分配 | O(n log n) | O(n) |

### Tips（技巧）

- **交换论证**：通过证明任何交换都会使结果变差来证明贪心最优。
- **按 X - Y 排序**：用于双选择分配的经典方法（如 A 和 B 的成本差）。
- 如果贪心不明显有效，那它可能就不行——改试 DP。

---

## 8. Heap (Priority Queue，优先队列)

### When to recognize（何时识别）

- "K 个最大/最小元素"
- "合并 K 个有序流"
- "调度作业以最大化吞吐量"
- "按优先级处理项目"
- 流数据中需要运行中的 top-k 或 min/max

### Template（模板）

```python
import heapq

# Min-heap (default in Python)
heapq.heappush(heap, item)
heapq.heappop(heap)           # smallest item

# Max-heap: negate values
heapq.heappush(heap, -item)
-heapq.heappop(heap)          # largest item
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 23](lc://23) Merge K Sorted Lists | k 个头节点的最小堆 | 弹出最小值，推入其下一个 | O(N log k) | O(k) |
| [LC 23](lc://23) variant: divide & conquer | 两两合并 | 反复合并对 | O(N log k) | O(1) |
| Custom #5 Server Throughput | 调度堆 | 将请求分配给最早空闲的服务器 | O(R log S) | O(S) |

### Tips（技巧）

- Python `heapq` 只有最小堆。最大堆用取负值或元组 `(-priority, item)`。
- "合并 K 个有序"任何东西：大小为 K 的堆，弹出-推入模式。
- 调度：堆存储 (end_time, server_id)，弹出最早空闲的。

---

## 9. Sliding Window（滑动窗口）

### When to recognize（何时识别）

- "具有性质 X 的最短/最长子数组"
- "最多 K 个不同元素"
- "和在范围内"
- 连续子数组/子串约束
- 问题中出现"窗口"关键词

### Template（模板）

```python
def sliding_window(arr, k):
    counts = {}
    left = 0
    best = float('inf')
    for right in range(len(arr)):
        # Expand: add arr[right]
        counts[arr[right]] = counts.get(arr[right], 0) + 1
        # Shrink while constraint violated
        while len(counts) > k:  # example constraint
            counts[arr[left]] -= 1
            if counts[arr[left]] == 0:
                del counts[arr[left]]
            left += 1
        best = min(best, right - left + 1)
    return best
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #10 Shortest k-Distinct | 达到 k 个不同时收缩 | 追踪字符计数，收缩找最小长度 | O(n) | O(k) |
| [LC 1696](lc://1696) (双端队列方面) | 滑动窗口最大值 | 单调双端队列维护窗口内最大值 | O(n) | O(k) |

### Tips（技巧）

- **双指针不变式**：维护窗口 [left, right]，其中性质成立。
- 扩展 right，收缩 left。在每个有效窗口时更新答案。
- "恰好 K 个不同"用 `atMost(K) - atMost(K-1)` 技巧。

---

## 10. Monotonic Stack（单调栈）

### When to recognize（何时识别）

- "下一个更大/更小元素"
- "价格折扣：最近的未来更低价格"
- "股票跨度"问题
- "直方图中最大矩形"系列
- 按顺序处理元素，维护递增/递减性质

### Template（模板）

```python
def next_smaller(prices):
    n = len(prices)
    result = [0] * n
    stack = []  # indices, maintaining increasing values
    for i in range(n):
        while stack and prices[stack[-1]] >= prices[i]:
            idx = stack.pop()
            result[idx] = prices[i]  # prices[i] is next smaller
        stack.append(i)
    return result
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #11 Price Discount | 下一个更小元素 | 为每个价格找最近的未来折扣 | O(n) | O(n) |

### Tips（技巧）

- 栈存储索引（不是值）——可以计算距离和访问值。
- **递增栈**：找下一个更小。**递减栈**：找下一个更大。
- 从左到右处理找"下一个"元素，从右到左处理找"前一个"元素。

---

## 11. Two Pointers（双指针）

### When to recognize（何时识别）

- 有序数组操作（合并、去重）
- "有序数组的平方"
- "盛最多水的容器" / "接雨水"
- 从两端向内比较

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 977](lc://977) Squares of Sorted Array | 从两端双指针 | 最大绝对值在边缘 | O(n) | O(n) |

### Tips（技巧）

- 当数组有序且需要对变换产生有序输出时，考虑从两端双指针。
- 从末尾填充结果数组（先放最大值），避免移位。

---

## 12. Object-Oriented Design (OOD，面向对象设计)

### When to recognize（何时识别）

- "设计一个系统"（停车场、购物车、收入追踪器）
- "实现一个具有这些操作的类"
- 面试官询问可扩展性、**SOLID** 原则
- 多种实体类型交互

### Design Checklist（设计清单）

1. **明确需求**：哪些操作？什么规模？
2. **识别实体**：问题中的名词 = 类
3. **定义接口**：每个类暴露哪些方法？
4. **选择模式**：可互换算法用 **Strategy Pattern（策略模式）**，事件用 **Observer Pattern（观察者模式）**
5. **优化**：识别最重要的 O(1) 操作

### Uber BPS Problems

| 题目 | 设计模式 | 关键思路 | 优化操作 |
|------|----------|----------|----------|
| Custom #2 Revenue & Referral | 树形聚合 | 推荐树 + 收入汇总 | O(D) 插入 |
| Custom #6 Cart & Pricing Engine | Strategy Pattern | 加价/会员/优惠作为可插拔规则 | O(items * rules) |
| Custom #16 Parking Lot | **OOD (Object-Oriented Design，面向对象设计)** + 空闲队列 | 按大小的最小堆或队列实现 O(1) 停车 | O(1) 停车/取车 |

### Tips（技巧）

- **从简单开始**：先写基础类，面试官问"如果需要添加 X 呢？"时再加模式。
- **Strategy Pattern**：当定价/评分规则变化时使用。每个规则是实现公共接口的类。
- **O(1) 优化**：停车场用按车辆大小的空闲车位队列。
- 始终讨论权衡："Strategy 更可扩展但增加了间接层。"

---

## 13. Grid / Matrix（网格/矩阵）

### When to recognize（何时识别）

- 2D 棋盘/地图问题
- "放置地雷"、"计数邻居"
- 机器人移动、距离计算
- 洪水填充、连通区域

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #8 Robot Distance | 网格 DP | 从源点预计算所有距离 | O(mn) | O(mn) |
| Custom #21 Minesweeper | 随机放置 + 计数 | 随机放置地雷，计算邻居计数 | O(mn) | O(mn) |

### Tips（技巧）

- 4方向：`[(0,1),(0,-1),(1,0),(-1,0)]`。8方向：加对角线。
- 边界检查：`0 <= nx < m and 0 <= ny < n`。
- 原地标记（`grid[i][j] = -1`）节省空间但修改输入——面试中需提及。

---

## 14. Bitmask Techniques（位掩码技术）

### When to recognize（何时识别）

- "回文可构成"（偶/奇字符计数）
- 按字符/元素的布尔标志进行状态追踪
- XOR 用于切换/取消操作
- 小字母表（26个字母可放入32位整数）

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 2791](lc://2791) Palindrome Paths | XOR 前缀位掩码 | 路径 u->v 回文当且仅当 XOR 最多1位为1 | O(26n) | O(n) |
| Custom #20 Palindrome Paths | 相同技术 | 路径上字符奇偶性的位掩码 | O(26n) | O(n) |

### Tips（技巧）

- **XOR 前缀**：`prefix[v] = prefix[parent] ^ (1 << char)`。路径 u-v = `prefix[u] ^ prefix[v]`。
- **最多1位为1**：检查 `x == 0` 或 `x & (x-1) == 0`。
- **26位掩码**：每个字母一位，追踪奇偶性。XOR 切换奇偶性。

---

## 15. Complexity Summary Table（复杂度汇总表）

### LC Problems

| LC # | 题目 | 模式 | 时间 | 空间 |
|------|------|------|------|------|
| 17 | Letter Combinations | 回溯 | O(4^n * n) | O(n) |
| 23 | Merge K Sorted Lists | 堆 | O(N log k) | O(k) |
| 79 | Word Search | DFS 回溯 | O(mn * 3^L) | O(L) |
| 230 | Kth Smallest BST | 中序遍历 | O(H + k) | O(H) |
| 337 | House Robber III | 树形 DP | O(n) | O(H) |
| 547 | Number of Provinces | Union Find / DFS | O(n^2 alpha) | O(n) |
| 549 | Longest Consecutive II | 树形 DP | O(n) | O(H) |
| 815 | Bus Routes | 路线 BFS | O(sum routes) | O(sum routes) |
| 977 | Squares Sorted Array | 双指针 | O(n) | O(n) |
| 981 | Time Based KV Store | 二分查找 | O(log n) get | O(n) |
| 987 | Vertical Traversal | BFS + 排序 | O(n log n) | O(n) |
| 994 | Rotting Oranges | 多源 BFS | O(mn) | O(mn) |
| 1020 | Number of Enclaves | 边界 BFS | O(mn) | O(mn) |
| 1197 | Min Knight Moves | BFS | O(xy) | O(xy) |
| 1696 | Jump Game VI | DP + 单调双端队列 | O(n) | O(k) |
| 1697 | Edge Length Limited | UF + 离线查询 | O((E+Q) log) | O(n+Q) |
| 2503 | Max Grid Points | BFS + 排序查询 | O(mn log mn) | O(mn) |
| 2791 | Palindrome Paths Tree | 位掩码 XOR DFS | O(26n) | O(n) |
| 2858 | Min Edge Reversals | 换根 DP | O(n) | O(n) |

### Custom Problems

| # | 题目 | 模式 | 时间 | 空间 |
|---|------|------|------|------|
| 1 | Purchase Optimization | 前缀和 + BS | O(n log n + q log n) | O(n) |
| 2 | Revenue & Referral | OOD / 树 | O(D) 插入 | O(n) |
| 3 | Rider Connection | Union Find + BFS | O(E alpha(N)) | O(N) |
| 4 | Elevator BS | 二分查找 | O(n log n) | O(n) |
| 5 | Server Throughput | 堆调度 | O(R log S) | O(S) |
| 6 | Cart & Pricing | OOD Strategy | O(items * rules) | O(items) |
| 7 | Circular Jump | BFS | O(n) | O(n) |
| 8 | Robot Distance | 网格 DP | O(mn) | O(mn) |
| 9 | Min Ops n->0 | 贪心 | O(log n) | O(1) |
| 10 | k-Distinct Subarray | 滑动窗口 | O(n) | O(k) |
| 11 | Price Discount | 单调栈 | O(n) | O(n) |
| 12 | Balanced Permutation | Min/Max 追踪 | O(n) | O(n) |
| 13 | Elevator/Stairs Energy | 三分查找 | O(n log n) | O(1) |
| 14 | N-ary Tree 3-Part | 树 DFS | O(n) | O(H) |
| 15 | Max Throughput Budget | 二分答案 | O(n log T) | O(1) |
| 16 | Parking Lot | OOD | O(1) 停车 | O(S) |
| 17 | Task Assignment | 贪心排序 | O(n log n) | O(n) |
| 18 | Jump Game Prime | DP + 筛法 | O(n*P) | O(n) |
| 19 | Min Edge Reversal | 换根 DP | O(n) | O(n) |
| 20 | Palindrome Paths | 位掩码 XOR DFS | O(26n) | O(n) |
| 21 | Minesweeper | 网格随机 | O(mn) | O(mn) |
| 22 | Grid Nearest Exit | BFS | O(mn) | O(mn) |
| 23 | Lock Combination | BFS 状态空间 | O(10^n * n) | O(10^n) |
| 24 | Non-overlapping Triples | 排序 + 前缀 | O(n^2) | O(n) |
| 25 | City Graph Sort | BFS + Dijkstra | O(V+E + V log V) | O(V+E) |

---

## 16. Pattern Recognition Decision Tree（模式识别决策树）

使用此流程图从问题关键词识别正确模式：

```
是设计问题吗？（类、实体、操作）
  是 -> OOD (#2, #6, #16)

是在树上吗？
  是 -> 是 BST 的第 k 小/搜索？
           是 -> 中序遍历 ([LC 230](lc://230))
         是"取或跳"节点决策？
           是 -> 树形 DP ([LC 337](lc://337), [LC 549](lc://549))
         是"所有根的最优解"？
           是 -> 换根 DP ([LC 2858](lc://2858), #19)
         是"回文路径"？
           是 -> 位掩码 XOR ([LC 2791](lc://2791), #20)
         其他 -> 树 DFS (#14)

是在图上吗？
  是 -> 无权"最短路径"？
           是 -> BFS ([LC 994](lc://994), [LC 1197](lc://1197), #22, #23)
         "连通分量"或"同一组"？
           是 -> Union Find ([LC 547](lc://547), [LC 1697](lc://1697), #3)
         "公交线路数/换乘"？
           是 -> 路线图 BFS ([LC 815](lc://815))

是在网格上吗？
  是 -> "最短距离 / 最近"？
           是 -> BFS ([LC 1020](lc://1020), #22)
         "查找单词 / 路径是否存在"？
           是 -> DFS 回溯 ([LC 79](lc://79))
         "预计算距离"？
           是 -> 网格 DP (#8)
         "生成棋盘"？
           是 -> 随机 + 计数 (#21)

是数组问题吗？
  是 -> "有序 + 搜索/查询"？
           是 -> 二分查找 ([LC 981](lc://981), #1, #4, #15)
         "具有 K 个不同元素的子数组 / 和约束"？
           是 -> 滑动窗口 (#10)
         "下一个更大/更小元素"？
           是 -> 单调栈 (#11)
         "跳跃的最大得分"？
           是 -> DP ([LC 1696](lc://1696), #18)
         "有序 + 变换"？
           是 -> 双指针 ([LC 977](lc://977))
         "分配以最小化成本"？
           是 -> 贪心排序 (#17)
         "合并 K 个有序"？
           是 -> 堆 ([LC 23](lc://23))
         "调度请求"？
           是 -> 堆 (#5)

是"生成所有组合"？
  是 -> 回溯 ([LC 17](lc://17))

是"有可行性检查的最小化/最大化"？
  是 -> 二分答案 (#13, #15)
```

### Quick Pattern Signals（快速模式信号）

| 问题中的信号 | 模式 | 示例 |
|-------------|------|------|
| "最短路径"、"最少步数" | BFS | [LC 994](lc://994), [LC 1197](lc://1197) |
| "连通分量"、"同一组" | Union Find | [LC 547](lc://547), [LC 1697](lc://1697) |
| "BST 中第 k 小/大" | 中序遍历 | [LC 230](lc://230) |
| "树上取或跳" | 树形 DP | [LC 337](lc://337) |
| "所有根最优" | 换根 DP | [LC 2858](lc://2858) |
| "回文路径 + 树" | 位掩码 XOR | [LC 2791](lc://2791) |
| "有序 + 预算/区间查询" | 前缀和 + BS | Custom #1 |
| "能否达到 X？"（单调性） | 二分答案 | Custom #15 |
| "下一个更小/更大" | 单调栈 | Custom #11 |
| "子数组中 K 个不同" | 滑动窗口 | Custom #10 |
| "合并 K 个有序流" | 堆 | [LC 23](lc://23) |
| "分配任务，最小化成本" | 按差值贪心排序 | Custom #17 |
| "设计停车/购物车/追踪器" | OOD | Custom #2, #6, #16 |
| "生成所有组合" | 回溯 | [LC 17](lc://17) |
| "网格中搜索单词" | DFS + 回溯 | [LC 79](lc://79) |