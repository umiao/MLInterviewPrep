# Uber BPS -- Timed Mock Interview Problem Sets（限时模拟面试题组）

> 3组限时模拟题，模拟 **BPS (Behavioral + Problem Solving，行为+问题解决)** 面试中45分钟的编程部分。
> 每组：1道 medium（20分钟）+ 1道 medium-hard（20分钟）+ follow-up（5分钟）。
>
> **使用方法**：设定计时器。打开 HackerRank 或空白编辑器。时间结束前不要查看答案。
> 每组完成后，在 `uber_bps_lc_solutions.md` 和 `uber_bps_custom_solutions.md` 中复习解法。
>
> Task: T-P2-248

---

## Set 1: Tree Traversal + Union Find

**考察模式**：**BST (Binary Search Tree，二叉搜索树)** 中序遍历、**UF (Union Find，并查集)** 事件处理

**目标时间**：共45分钟

---

### Problem 1A: Kth Smallest in BST (Medium, 20 min)

**来源**：[LC 230](lc://230) 变体

给定一棵 BST 的根节点和整数 `k`，返回第 k 小的元素。

```
Input: root = [5, 3, 6, 2, 4, null, null, 1], k = 3
Output: 3
```

**要求**：
1. 使用迭代中序遍历实现（不使用递归）。
2. 说明时间和空间复杂度。

**Follow-up A**（面试官提示，+3分钟）：
> "现在找第 k **大**的元素。"

期望：反向中序遍历（right -> node -> left）。复杂度相同。

**Follow-up B**（面试官提示，+2分钟）：
> "如果这棵 BST 频繁修改（插入/删除），且 `kthSmallest` 被频繁调用，如何优化？"

期望：为每个节点增加 `left_count`（左子树大小）。O(H) 查找，无需完整遍历。需讨论权衡：每次插入/删除需要 O(H) 维护计数。

**评分标准**：
- [ ] 干净的迭代中序遍历：2分
- [ ] 在第 k 个元素处正确提前终止：1分
- [ ] 复杂度分析（O(H+k) 时间，O(H) 空间）：1分
- [ ] Follow-up A（反向中序遍历）：1分
- [ ] Follow-up B（增强型 BST）：1分

---

### Problem 1B: Rider Connection Log（骑手连接日志）(Medium-Hard, 20 min)

**来源**：Custom #3

给定带时间戳的骑手交互日志，找到所有骑手最早全部连通（直接或传递）的时间。

```
Input:
  n_riders = 4
  logs = [
    (1, "Alice", "Bob"),       # timestamp 1: Alice shared ride with Bob
    (2, "Charlie", "Dave"),    # timestamp 2: Charlie shared ride with Dave
    (5, "Bob", "Charlie"),     # timestamp 5: Bob shared ride with Charlie
  ]
Output: 5  # At timestamp 5, all 4 riders are in one connected component
```

**要求**：
1. 实现带路径压缩和按秩合并的 Union Find。
2. 按时间顺序处理日志。当 `components == 1` 时返回最早时间戳，若永远不完全连通则返回 `None`。
3. 说明时间和空间复杂度。

**Follow-up**（面试官提示，+5分钟）：
> "现在日志还可以包含'屏蔽'事件：`(7, 'blocked', 'Alice', 'Bob')`。如何处理断开连接？"

期望方案：Union Find 不支持删除操作。改用邻接表 + **BFS (Breadth-First Search，广度优先搜索)** / **DFS (Depth-First Search，深度优先搜索)** 连通性检查。讨论权衡：UF 每次查询 O(alpha(N))，但不支持删除；BFS 重建每次事件 O(V+E)，但支持删除。提到离线逆序处理作为替代方案（如果所有事件已知）。

**评分标准**：
- [ ] 正确的 UnionFind 类（带压缩的 find、按秩合并的 union）：2分
- [ ] 正确的连通分量计数和提前返回：1分
- [ ] 处理骑手名字到 ID 的映射：1分
- [ ] 复杂度分析（O(E * alpha(N)) 时间，O(N) 空间）：1分
- [ ] Follow-up：BFS 重建方案及权衡讨论：2分

---

### Set 1 Debrief Checklist（复盘清单）

完成 Set 1 后回顾：
- [ ] 编码前是否解释了思路？
- [ ] 是否编写并运行了测试用例？
- [ ] 是否对每种方案说明了复杂度？
- [ ] 是否处理了边界情况（空树、k=1、单个骑手）？
- [ ] 总时间：______ / 45分钟

---

## Set 2: Multi-source BFS + Prefix Sum Binary Search

**考察模式**：网格 BFS、**前缀和 (Prefix Sum)** + **BS (Binary Search，二分查找)**

**目标时间**：共45分钟

---

### Problem 2A: Rotting Oranges（腐烂的橘子）(Medium, 20 min)

**来源**：[LC 994](lc://994)

有一个 `m x n` 的网格，每个格子是：
- `0` = 空格
- `1` = 新鲜橘子
- `2` = 腐烂橘子

每分钟，与腐烂橘子相邻（4个方向）的新鲜橘子会变腐烂。返回所有新鲜橘子都腐烂的最少分钟数，如果不可能则返回 `-1`。

```
Input: grid = [[2,1,1],[1,1,0],[0,1,1]]
Output: 4
```

**要求**：
1. 使用多源 BFS（先将所有腐烂橘子入队）。
2. 追踪新鲜橘子计数；BFS 完成后若 fresh > 0 则返回 -1。
3. 说明时间和空间复杂度。

**Follow-up A**（面试官提示，+3分钟）：
> "如果腐烂橘子也能对角线传播（8个方向）呢？"

期望：在方向数组中添加4个对角方向。BFS 逻辑不变。时间仍为 O(mn)。

**Follow-up B**（面试官提示，+2分钟）：
> "如果某些格子是墙（值为3）会阻挡传播呢？"

期望：在 BFS 邻居检查中跳过值为3的格子。复杂度不变。说明：墙可能造成不可达的新鲜橘子，因此 -1 的情况更常见。

**评分标准**：
- [ ] 正确的多源 BFS 初始化：2分
- [ ] 正确的分钟计数（逐层 BFS）：1分
- [ ] 处理 fresh == 0 的边界情况（返回0）：1分
- [ ] 不可达时返回 -1：1分
- [ ] 复杂度分析（O(mn) 时间和空间）：1分

---

### Problem 2B: Purchase Optimization（采购优化）(Medium-Hard, 20 min)

**来源**：Custom #1

给定一个商品 `prices` 列表（可能未排序）和一系列查询 `(start_pos, budget)`，对每个查询找出从索引 `start_pos` 开始、在给定预算内最多能买多少件商品。商品必须按最便宜的顺序购买。

```
Input:
  prices = [10, 5, 20, 15, 3]
  queries = [(0, 25), (2, 40), (0, 100)]
Output: [3, 2, 5]
  # Query 1: sorted = [3,5,10,15,20], from pos 0 with budget 25: buy 3+5+10=18, can't add 15 -> 3 items
  # Query 2: from pos 2 with budget 40: buy 10+15=25, can't add 20 -> wait, pos 2 in sorted -> 10,15,20 -> 10+15=25 <= 40, +20=45 > 40 -> 2 items
  # Query 3: from pos 0, budget 100: buy all 5 items (3+5+10+15+20=53 <= 100) -> 5
```

**要求**：
1. 先对价格排序。
2. 构建前缀和数组。
3. 对每个查询，二分查找最大可购买数量。
4. 说明时间和空间复杂度。

**Follow-up**（面试官提示，+5分钟）：
> "如果每件商品有'类别'，且每个类别最多买2件呢？"

期望讨论：前缀和 + 二分查找不再适用，因为约束是按类别而非全局的。需要贪心方法：遍历排序后的价格，维护类别计数，跳过超过类别限制的商品。每次查询时间变为 O(n) 而非 O(log n)。或者，预计算每种类别限制约束下的"过滤前缀和"。

**评分标准**：
- [ ] 正确的排序 + 前缀和构建：1分
- [ ] 正确的二分查找（bisect_right on prefix sum）：2分
- [ ] 处理边界情况（pos 越界、budget 为0）：1分
- [ ] 复杂度分析（O(n log n + q log n) 时间，O(n) 空间）：1分
- [ ] Follow-up：识别 BS 失效，提出贪心替代方案：2分

---

### Set 2 Debrief Checklist（复盘清单）

完成 Set 2 后回顾：
- [ ] 编码前是否确认了约束条件（网格大小、价格范围）？
- [ ] 是否主动用边界情况测试（全部腐烂、无新鲜、空网格）？
- [ ] 前缀和索引是否正确处理（off-by-one）？
- [ ] 选择方案前是否讨论了多种方案？
- [ ] 总时间：______ / 45分钟

---

## Set 3: Graph Components + OOD

**考察模式**：**UF (Union Find，并查集)** / DFS 连通性、**OOD (Object-Oriented Design，面向对象设计)** Strategy 模式

**目标时间**：共45分钟

---

### Problem 3A: Number of Provinces（省份数量）(Medium, 20 min)

**来源**：[LC 547](lc://547)

有 `n` 个城市。`isConnected[i][j] = 1` 表示城市 `i` 和城市 `j` 直接相连。省份是一组直接或间接相连的城市。返回省份数量。

```
Input: isConnected = [[1,1,0],[1,1,0],[0,0,1]]
Output: 2
```

**要求**：
1. 使用 Union Find 或 DFS 实现（选择一种，准备好讨论另一种）。
2. 说明时间和空间复杂度。
3. 用示例输入演示你的解法。

**Follow-up A**（面试官提示，+3分钟）：
> "给定一系列新建的城市间道路，如何高效追踪每条道路建成后的省份数？"

期望：Union Find 非常适合在线连通性问题。初始 n 个分量，每次合并减少1（若未已连通）。每条道路 O(alpha(n))。DFS 每次需要完整重新遍历——效率差很多。

**Follow-up B**（面试官提示，+2分钟）：
> "如果某些道路是单向的（有向），你的方案还有效吗？"

期望：不行。Union Find 假设无向边。对于有向图，需要用 **Tarjan** 或 **Kosaraju** 算法求**SCC (Strongly Connected Components，强连通分量)**。需提到弱连通分量和强连通分量的区别。

**评分标准**：
- [ ] 正确的 UF 或 DFS 实现：2分
- [ ] 正确的省份计数：1分
- [ ] 复杂度分析（O(n^2 * alpha(n)) UF 或 O(n^2) DFS）：1分
- [ ] Follow-up A：在线 UF 优于 DFS：1分
- [ ] Follow-up B：有向图意识（SCC）：1分

---

### Problem 3B: Cart & Pricing Engine（购物车定价引擎）(Medium-Hard, 20 min)

**来源**：Custom #6

设计一个 Uber Eats 购物车系统，需要以下功能：
1. **菜单项**：含基础价格和可选附加项（如"Extra cheese +$1.50"）
2. **高峰加价**：高峰时段的乘数（如1.3倍）
3. **会员折扣**：如 Uber One 享9折
4. **优惠码**：固定金额或百分比折扣
5. **收据生成**：显示逐项明细

**要求**：
1. 设计类结构。画出/描述类之间的关系。
2. 实现核心类：`MenuItem`、`CartItem`、`Cart`，以及至少两条定价规则。
3. 定价规则应以可配置顺序应用（**Strategy Pattern，策略模式**）。
4. 展示一个生成收据的使用示例。

```
Example usage:
  cart = Cart()
  burger = MenuItem("Burger", 12.00, add_ons=[AddOn("Extra cheese", 1.50)])
  cart.add_item(burger, quantity=2)
  cart.add_pricing_rule(SurgePricingRule(1.3))
  cart.add_pricing_rule(MembershipDiscountRule(10))
  print(cart.receipt())

Expected receipt:
  === Receipt ===
  Burger (+ Extra cheese) x2    $27.00
  Subtotal:                     $27.00
  Surge pricing (1.3x):        $35.10
  Uber One discount (-10%):    $31.59
  Total:                        $31.59
```

**Follow-up**（面试官提示，+5分钟）：
> "如何添加一条最大折扣上限为$15的规则？它应该放在定价管道的哪个位置？"

期望：创建 `MaxDiscountCapRule`，比较当前金额与 `(subtotal - max_discount)`，取较大值。应在所有折扣之后**最后**应用。讨论：规则顺序很重要——上限必须是后处理步骤，不能和折扣交错。

**评分标准**：
- [ ] 干净的类设计（MenuItem, CartItem, Cart）：2分
- [ ] 定价规则的 Strategy Pattern（ABC + 具体实现）：2分
- [ ] 正确的带定价明细的收据：1分
- [ ] 可扩展性讨论（添加新规则无需修改 Cart）：1分
- [ ] Follow-up：最大折扣上限及顺序合理性：1分

---

### Set 3 Debrief Checklist（复盘清单）

完成 Set 3 后回顾：
- [ ] Problem 3A 是否讨论了 UF 与 DFS 的权衡？
- [ ] Problem 3B 是否画了类图或描述了类关系？
- [ ] 是否解释了为什么用 Strategy Pattern 而非 if/else 链？
- [ ] 是否用给定示例测试了 OOD 代码？
- [ ] 总时间：______ / 45分钟

---

## Overall Practice Schedule（整体练习计划）

| 日期 | 题组 | 完成后重点复习内容 |
|------|------|--------------------|
| Day 1 | Set 1 | BST 遍历变体、Union Find 模板 |
| Day 2 | Set 2 | BFS 模式、前缀和 + 二分查找 |
| Day 3 | Set 3 | 图连通性、OOD / Strategy Pattern |
| Day 4 | 最弱题组 | 重做得分最低的那组 |

### Scoring Guide（评分指南）

| 分数 | 水平 | 行动 |
|------|------|------|
| 10-12 / 12 每组 | 优秀 | BPS 准备就绪。专注提速。 |
| 7-9 / 12 每组 | 良好 | 复习 follow-up 模式。练习口头表达权衡分析。 |
| 4-6 / 12 每组 | 需提高 | 在 `uber_bps_pattern_cheatsheet.md` 中重新学习该模式，从头重做。 |
| < 4 / 12 每组 | 存在差距 | 用3-5道类似 **LC (LeetCode)** 题目练习该模式后再重试。 |

### Time Management Tips（时间管理技巧）

- **0-2分钟**：明确问题。复述约束条件。询问边界情况。
- **2-5分钟**：讨论2种方案。选择一种。说明复杂度。
- **5-18分钟**：编码。边写边说。在线处理边界情况。
- **18-20分钟**：用给定示例 + 1个边界情况测试。修复 bug。
- **Follow-ups**：大声思考。先说关键洞察，不用写完整代码。

> **黄金法则**：如果实现过程中卡住超过3分钟，退后一步重新审视方案。一个错误算法写得再完美也得0分。一个正确算法有小 bug 仍然得分不错。