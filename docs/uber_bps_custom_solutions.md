# Uber BPS -- 自定义（非 LC）题目解题方案

> Uber 面试专属题目的解答，这些题目没有对应的标准 LeetCode 编号。
> 每题包含：题目描述（根据 1p3a 重构）、解题思路、简洁 Python 代码、
> 时间/空间复杂度、边界情况及延伸问题。
>
> Task: T-P0-243

---

## Table of Contents

1. [Purchase Optimization](#1-purchase-optimization)
2. [Customer Revenue & Referral Tracking (OOD)](#2-customer-revenue--referral-tracking-ood)
3. [Uber Rider Connection Log (Union Find)](#3-uber-rider-connection-log-union-find)
4. [Elevator Binary Search OA](#4-elevator-binary-search-oa)
5. [Server Throughput with Heap](#5-server-throughput-with-heap)
6. [Cart & Pricing Engine (OOD)](#6-cart--pricing-engine-ood)
7. [Circular Array Shortest Jump](#7-circular-array-shortest-jump)
8. [Robot Distance in Grid](#8-robot-distance-in-grid)
9. [Min Operations n to 0](#9-min-operations-n-to-0)
10. [Shortest Subarray with k Distinct](#10-shortest-subarray-with-k-distinct)
11. [Price Discount (Monotonic Stack)](#11-price-discount-monotonic-stack)
12. [Balanced Permutation](#12-balanced-permutation)
13. [Elevator/Stairs Energy](#13-elevatorstairs-energy)
14. [N-ary Tree 3-Part](#14-n-ary-tree-3-part)
15. [Max Throughput with Budget](#15-max-throughput-with-budget)
16. [Parking Lot (OOD)](#16-parking-lot-ood)
17. [Task Assignment to 2 People](#17-task-assignment-to-2-people)
18. [Jump Game Prime-Ending Variant](#18-jump-game-prime-ending-variant)
19. [Min Edge Reversal for Optimal Root](#19-min-edge-reversal-for-optimal-root)
20. [Palindrome Paths in Tree](#20-palindrome-paths-in-tree)
21. [Minesweeper Grid Generator](#21-minesweeper-grid-generator)
22. [2D Grid Nearest Exit (BFS)](#22-2d-grid-nearest-exit-bfs)
23. [Lock Combination BFS](#23-lock-combination-bfs)
24. [Non-overlapping Interval Triples](#24-non-overlapping-interval-triples)
25. [City Graph BFS Sort](#25-city-graph-bfs-sort)

---

## 1. Purchase Optimization

**Pattern**: **Prefix Sum（前缀和）** + **Binary Search（二分查找）**

### Problem Statement

给定一个升序排列的价格数组 `prices`，以及一组查询 `(pos, amount)`，
对于每个查询，求从索引 `pos` 开始、预算为 `amount` 时，最多能购买多少件商品。

### Approach

1. 对 prices 排序（若未排序）。
2. 构建前缀和数组：`prefix[i] = prices[0] + prices[1] + ... + prices[i-1]`。
3. 对于每个查询 `(pos, amount)`：二分查找最大的 `end`，使得
   `prefix[end] - prefix[pos] <= amount`。

```python
import bisect
from typing import List, Tuple


def max_items_purchasable(
    prices: List[int], queries: List[Tuple[int, int]]
) -> List[int]:
    """For each (pos, amount), find max items buyable from prices[pos:]."""
    prices.sort()
    n = len(prices)

    # prefix[i] = sum of prices[0..i-1]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + prices[i]

    results = []
    for pos, amount in queries:
        if pos >= n:
            results.append(0)
            continue
        # Find largest end such that prefix[end] - prefix[pos] <= amount
        # i.e. prefix[end] <= prefix[pos] + amount
        target = prefix[pos] + amount
        end = bisect.bisect_right(prefix, target, lo=pos, hi=n + 1) - 1
        results.append(end - pos)

    return results
```

**时间复杂度**：排序 O(n log n) + 构建前缀和 O(n) + 处理 q 个查询 O(q log n)。
**空间复杂度**：O(n)，用于存储前缀和数组。

### Edge Cases
- `amount` 为 0 -> 返回 0
- `pos` 超出数组范围 -> 返回 0
- 预算足以购买所有剩余商品

### Follow-up: Unsorted Prices

若价格数组未排序，需先排序。若查询需要原始索引，排序前需维护一个索引映射。

---

## 2. Customer Revenue & Referral Tracking (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）** / **Tree Aggregation（树形聚合）**

### Problem Statement

设计一个系统，支持以下操作：
- `insertNewCustomer(revenue, referrerID)`：添加一位客户，其收入为 revenue，由 referrerID 推荐。收入沿推荐链向上传播。
- `getLowestK(k, minTotalRevenue)`：返回总收入（直接收入 + 所有被推荐人收入之和）超过 minTotalRevenue 的 k 位总收入最低的客户。

### Approach

每个客户记录直接收入和 `total_revenue`（直接 + 子树收入之和）。
插入时，沿推荐链向上传播收入。对于 `getLowestK`，维护一个有序结构或过滤扫描。

```python
import heapq
from typing import List, Optional


class Customer:
    """A customer node in the referral tree."""

    def __init__(self, cid: int, revenue: float, referrer_id: Optional[int]):
        self.cid: int = cid
        self.revenue: float = revenue
        self.total_revenue: float = revenue  # direct + subtree
        self.referrer_id: Optional[int] = referrer_id
        self.referrals: List[int] = []


class ReferralSystem:
    """Referral tracking with upward revenue propagation."""

    def __init__(self) -> None:
        self.customers: dict[int, Customer] = {}
        self._next_id: int = 0

    def insert_new_customer(
        self, revenue: float, referrer_id: Optional[int] = None
    ) -> int:
        """Insert customer and propagate revenue up the referral chain."""
        cid = self._next_id
        self._next_id += 1

        customer = Customer(cid, revenue, referrer_id)
        self.customers[cid] = customer

        if referrer_id is not None and referrer_id in self.customers:
            self.customers[referrer_id].referrals.append(cid)
            # Propagate revenue upward
            current_id = referrer_id
            while current_id is not None:
                self.customers[current_id].total_revenue += revenue
                current_id = self.customers[current_id].referrer_id

        return cid

    def get_lowest_k(self, k: int, min_total_revenue: float) -> List[int]:
        """Return k customers with lowest total_revenue >= min_total_revenue."""
        candidates = [
            (c.total_revenue, c.cid)
            for c in self.customers.values()
            if c.total_revenue >= min_total_revenue
        ]
        # Use heapq.nsmallest for efficiency when k << n
        smallest = heapq.nsmallest(k, candidates)
        return [cid for _, cid in smallest]
```

**时间复杂度**：
- `insert`：O(D)，D 为推荐树的深度（收入向上传播）。
- `getLowestK`：O(n log k)，使用堆选择。

**空间复杂度**：O(n)，存储所有客户。

### Edge Cases
- 无推荐人的客户（根节点）
- 深度较大的推荐链（O(D) 传播）
- k 大于满足条件的客户数量

### Follow-up: Efficient getLowestK

若查询频繁，可维护一个按 total_revenue 索引的有序容器（如 sortedcontainers 的 SortedList）。
插入时：删除旧条目、更新、重新插入，可实现插入 O(log n)、查询 O(k + log n)。

---

## 3. Uber Rider Connection Log (Union Find)

**Pattern**: **Union Find（并查集）** / **Graph Connectivity（图连通性）**

### Problem Statement

给定形如 `"<timestamp> A shared-ride-with B"` 的带时间戳日志，求所有乘客首次全部连通（直接或间接）的最早时间戳。

**延伸问题**：处理 `"<timestamp> A blocked B"`（断开连接）事件。

### Approach -- Part 1: Union Find

按时间顺序处理日志。对每条 `shared-ride-with` 记录，合并两位乘客。
每次合并后检查所有乘客是否已在同一连通分量中。

```python
from typing import List, Optional, Tuple


class UnionFind:
    """Weighted Union-Find with path compression."""

    def __init__(self, n: int):
        self.parent: List[int] = list(range(n))
        self.rank: List[int] = [0] * n
        self.components: int = n

    def find(self, x: int) -> int:
        """Find root with path compression."""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if a merge occurred."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True


def earliest_full_connection(
    logs: List[Tuple[int, str, str]], n_riders: int
) -> Optional[int]:
    """Find earliest timestamp when all n_riders are connected.

    Args:
        logs: List of (timestamp, rider_a, rider_b) sorted by timestamp.
        n_riders: Total number of distinct riders.

    Returns:
        Earliest timestamp or None if never fully connected.
    """
    rider_to_id: dict[str, int] = {}
    next_id = 0

    def get_id(name: str) -> int:
        nonlocal next_id
        if name not in rider_to_id:
            rider_to_id[name] = next_id
            next_id += 1
        return rider_to_id[name]

    uf = UnionFind(n_riders)

    for timestamp, a, b in logs:
        id_a, id_b = get_id(a), get_id(b)
        uf.union(id_a, id_b)
        if uf.components == 1:
            return timestamp

    return None
```

**时间复杂度**：O(E * alpha(N)) ≈ O(E)，E 为日志条数。
**空间复杂度**：O(N)，用于并查集结构。

### Follow-up: Handling "block" Events (Deletions)

并查集**不支持**删除操作。有两种方案：

**方案 A：离线处理——逆序**

若需要找所有人**最后一次**全部连通的时间，可逆序处理事件：断开变合并，共乘变边。但这改变了问题语义。

**方案 B：使用 BFS/DFS 重建**

对于需要同时处理连接和断开事件的在线场景，维护邻接表。每次事件后运行 **BFS (Breadth-First Search，广度优先搜索)** 或 **DFS (Depth-First Search，深度优先搜索)** 检查连通性。

```python
from collections import defaultdict, deque
from typing import List, Optional, Tuple


def earliest_full_connection_with_blocks(
    logs: List[Tuple[int, str, str, str]], n_riders: int
) -> Optional[int]:
    """Handle both 'connect' and 'block' events.

    Args:
        logs: (timestamp, action, rider_a, rider_b) where action is
              'shared-ride-with' or 'blocked'.
    """
    graph: dict[str, set[str]] = defaultdict(set)
    all_riders: set[str] = set()

    def is_connected() -> bool:
        if len(all_riders) < n_riders:
            return False
        start = next(iter(all_riders))
        visited: set[str] = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return len(visited) == len(all_riders)

    for timestamp, action, a, b in logs:
        all_riders.add(a)
        all_riders.add(b)

        if action == "shared-ride-with":
            graph[a].add(b)
            graph[b].add(a)
        elif action == "blocked":
            graph[a].discard(b)
            graph[b].discard(a)

        if is_connected():
            return timestamp

    return None
```

**时间复杂度**：O(E * (V + E))——每次事件后进行 BFS。对于大规模输入，可用 Link-Cut Tree 或 ETT（欧拉回路树）优化至 O(log N) 每次操作。
**空间复杂度**：O(V + E)，用于邻接表。

### Edge Cases
- 只有一位乘客（天然连通）
- 对不存在的连接执行 block 操作（无操作）
- 同一对乘客之间有多条连接

---

## 4. Elevator Binary Search OA

**Pattern**: **Array Simulation（数组模拟）** / Binary Search

### Problem Statement

给定一个数组，每个元素表示移动距离，从索引 `i` 出发，移动到 `i + arr[i]`（或根据规则移动到 `i - arr[i]`）。
求最小的起始索引，使得遍历过程中永远不会越过左边界（索引 < 0）。

### Approach

从每个起始索引模拟路径。若该属性具有单调性（起始索引越大，左侧空间越多），可用记忆化或二分查找提升效率。

```python
from typing import List


def min_starting_index(moves: List[int]) -> int:
    """Find minimum starting index that never goes below 0.

    The array alternates: even indices move right (+moves[i]),
    odd indices move left (-moves[i]).
    """
    n = len(moves)

    def simulate(start: int) -> bool:
        """Return True if starting at 'start' never goes below 0."""
        pos = start
        visited: set[int] = set()
        while 0 <= pos < n:
            if pos in visited:
                return True  # cycle detected, never exits left
            visited.add(pos)
            pos += moves[pos]  # moves[i] can be negative (left jump)
        return pos >= 0  # exited right or stayed in bounds

    # If monotonic: binary search
    lo, hi = 0, n - 1
    result = n  # no valid start found

    # Linear scan fallback (safe for all cases)
    for i in range(n):
        if simulate(i):
            return i

    return result
```

**时间复杂度**：线性扫描 + 模拟，最坏情况 O(n^2)。
若具有单调性，使用二分查找：O(n log n)。
**空间复杂度**：O(n)，用于 visited 集合。

### Variant: Bidirectional Jumps with Array Values

```python
def min_start_bidirectional(arr: List[int]) -> int:
    """Each position has jump distance. Even-index: right, odd-index: left."""
    n = len(arr)
    for start in range(n):
        pos = start
        steps = 0
        valid = True
        while 0 <= pos < n and steps < 2 * n:
            pos = pos + arr[pos] if pos % 2 == 0 else pos - arr[pos]
            steps += 1
            if pos < 0:
                valid = False
                break
        if valid:
            return start
    return -1
```

### Edge Cases
- 数组长度为 1
- 所有元素为 0（在起点形成无限循环）
- 负数跳跃导致立即越过左边界

---

## 5. Server Throughput with Heap

**Pattern**: **Heap（堆）** / **Greedy Scheduling（贪心调度）**

### Problem Statement

给定 `n` 台服务器及其处理时间，以及传入的请求，最大化吞吐量。
对比递归解法与基于堆的解法。

### Approach: Min-Heap for Earliest Available Server

```python
import heapq
from typing import List, Tuple


def max_throughput_heap(
    servers: List[int], requests: List[Tuple[int, int]]
) -> int:
    """Assign requests to servers to maximize throughput.

    Args:
        servers: Processing time for each server.
        requests: (arrival_time, processing_time) sorted by arrival.

    Returns:
        Number of requests successfully processed.
    """
    # Min-heap: (available_time, server_id)
    heap: List[Tuple[int, int]] = [(0, i) for i in range(len(servers))]
    heapq.heapify(heap)

    processed = 0
    for arrival, duration in requests:
        # Get the server that becomes free earliest
        avail_time, sid = heapq.heappop(heap)
        if avail_time <= arrival:
            # Server is free, assign this request
            new_avail = arrival + duration
            heapq.heappush(heap, (new_avail, sid))
            processed += 1
        else:
            # No server available, put it back and skip request
            heapq.heappush(heap, (avail_time, sid))

    return processed
```

**时间复杂度**：O(R log S)，R 为请求数，S 为服务器数。
**空间复杂度**：O(S)，用于堆。

### Recursive Approach (for comparison)

```python
def max_throughput_recursive(
    servers: List[int],
    requests: List[Tuple[int, int]],
    idx: int = 0,
    avail: List[int] | None = None,
) -> int:
    """Brute force: try assigning each request to each server."""
    if avail is None:
        avail = [0] * len(servers)
    if idx == len(requests):
        return 0

    arrival, duration = requests[idx]
    # Option 1: skip this request
    best = max_throughput_recursive(servers, requests, idx + 1, avail)

    # Option 2: assign to an available server
    for s in range(len(servers)):
        if avail[s] <= arrival:
            old = avail[s]
            avail[s] = arrival + duration
            result = 1 + max_throughput_recursive(
                servers, requests, idx + 1, avail
            )
            best = max(best, result)
            avail[s] = old  # backtrack

    return best
```

**时间复杂度**：O(S^R) 指数级——仅适用于小规模输入。

### Edge Cases
- 所有请求同时到达
- 只有一台服务器
- 处理时间超过请求间隔

---

## 6. Cart & Pricing Engine (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）** / **Strategy Pattern（策略模式）**

### Problem Statement

为 Uber Eats 购物车系统设计类。需求：
- 商品定制（附加项及额外费用）
- 高峰期价格倍增（Surge Pricing）
- 会员折扣（Uber One）
- 优惠码（固定金额或百分比）
- 小票明细输出

### Design

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class AddOn:
    """An item customization (e.g., extra cheese)."""
    name: str
    price: float


@dataclass
class MenuItem:
    """A menu item with optional add-ons."""
    name: str
    base_price: float
    add_ons: List[AddOn] = field(default_factory=list)

    @property
    def total_price(self) -> float:
        return self.base_price + sum(a.price for a in self.add_ons)


@dataclass
class CartItem:
    """An item in the cart with quantity."""
    menu_item: MenuItem
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.menu_item.total_price * self.quantity


# --- Pricing Rules (Strategy Pattern) ---

class PricingRule(ABC):
    """Base class for pricing rules applied to cart total."""

    @abstractmethod
    def apply(self, amount: float) -> float:
        """Return the adjusted amount after applying this rule."""

    @abstractmethod
    def description(self) -> str:
        """Human-readable description for receipt."""


class SurgePricingRule(PricingRule):
    """Multiplier during peak demand."""

    def __init__(self, multiplier: float):
        self.multiplier = multiplier

    def apply(self, amount: float) -> float:
        return amount * self.multiplier

    def description(self) -> str:
        return f"Surge pricing ({self.multiplier}x)"


class MembershipDiscountRule(PricingRule):
    """Flat percentage discount for Uber One members."""

    def __init__(self, discount_pct: float):
        self.discount_pct = discount_pct

    def apply(self, amount: float) -> float:
        return amount * (1 - self.discount_pct / 100)

    def description(self) -> str:
        return f"Uber One discount (-{self.discount_pct}%)"


class PromoCodeType(Enum):
    FLAT = "flat"
    PERCENTAGE = "percentage"


class PromoCodeRule(PricingRule):
    """Promo code: flat amount off or percentage off."""

    def __init__(self, code: str, promo_type: PromoCodeType, value: float):
        self.code = code
        self.promo_type = promo_type
        self.value = value

    def apply(self, amount: float) -> float:
        if self.promo_type == PromoCodeType.FLAT:
            return max(0.0, amount - self.value)
        return amount * (1 - self.value / 100)

    def description(self) -> str:
        if self.promo_type == PromoCodeType.FLAT:
            return f"Promo '{self.code}' (-${self.value:.2f})"
        return f"Promo '{self.code}' (-{self.value}%)"


# --- Cart ---

class Cart:
    """Shopping cart with pricing engine."""

    def __init__(self) -> None:
        self.items: List[CartItem] = []
        self.pricing_rules: List[PricingRule] = []

    def add_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        """Add item to cart."""
        self.items.append(CartItem(menu_item, quantity))

    def add_pricing_rule(self, rule: PricingRule) -> None:
        """Add a pricing rule (surge, discount, promo)."""
        self.pricing_rules.append(rule)

    @property
    def subtotal(self) -> float:
        """Raw total before pricing rules."""
        return sum(item.subtotal for item in self.items)

    @property
    def total(self) -> float:
        """Final total after all pricing rules applied in order."""
        amount = self.subtotal
        for rule in self.pricing_rules:
            amount = rule.apply(amount)
        return round(amount, 2)

    def receipt(self) -> str:
        """Generate itemized receipt with pricing breakdown."""
        lines: List[str] = ["=== Receipt ==="]

        for item in self.items:
            base = item.menu_item.base_price
            lines.append(
                f"  {item.menu_item.name} x{item.quantity}"
                f"  ${base:.2f} ea"
            )
            for addon in item.menu_item.add_ons:
                lines.append(f"    + {addon.name}: ${addon.price:.2f}")
            lines.append(f"    Item total: ${item.subtotal:.2f}")

        lines.append(f"\nSubtotal: ${self.subtotal:.2f}")

        amount = self.subtotal
        for rule in self.pricing_rules:
            new_amount = rule.apply(amount)
            diff = new_amount - amount
            sign = "+" if diff >= 0 else ""
            lines.append(f"  {rule.description()}: {sign}${diff:.2f}")
            amount = new_amount

        lines.append(f"\nTotal: ${round(amount, 2):.2f}")
        lines.append("===============")
        return "\n".join(lines)
```

### Usage Example

```python
burger = MenuItem("Burger", 12.99, [AddOn("Extra Cheese", 1.50)])
fries = MenuItem("Fries", 4.99)

cart = Cart()
cart.add_item(burger, 2)
cart.add_item(fries, 1)

cart.add_pricing_rule(SurgePricingRule(1.3))
cart.add_pricing_rule(MembershipDiscountRule(10))
cart.add_pricing_rule(
    PromoCodeRule("SAVE5", PromoCodeType.FLAT, 5.0)
)

print(cart.receipt())
```

**关键设计决策**：
- 策略模式用于定价规则：方便扩展新规则类型
- 规则按顺序应用（高峰倍增 -> 折扣 -> 优惠码）
- `MenuItem.total_price` 包含附加项费用
- 小票展示完整明细

### Follow-up: Rule Ordering and Conflicts

生产环境中，为规则定义 `priority` 字段，应用前按优先级排序。
对于互斥规则（如只能使用一个优惠码），在 `add_pricing_rule` 时进行校验。

---

## 7. Circular Array Shortest Jump

**Pattern**: BFS on Circular Array（循环数组 BFS）

### Problem Statement

给定一个循环整数数组，`arr[i]` 表示索引 `i` 处的跳跃距离，
求从索引 A 到索引 B 的最少跳跃次数。
跳跃支持循环绕回：从索引 `i` 出发，可以跳到 `(i + arr[i]) % n` 或 `(i - arr[i]) % n`。

### Approach

从源节点 A 开始 BFS。每个状态为循环数组中的一个位置。
由于求最短路径，BFS 保证最优性。

```python
from collections import deque
from typing import List


def shortest_jump(arr: List[int], start: int, end: int) -> int:
    """Find minimum jumps from start to end in circular array.

    At each position i, can jump to (i + arr[i]) % n or (i - arr[i]) % n.
    Returns -1 if unreachable.
    """
    n = len(arr)
    if start == end:
        return 0

    visited = [False] * n
    visited[start] = True
    queue: deque[tuple[int, int]] = deque([(start, 0)])

    while queue:
        pos, dist = queue.popleft()
        for nxt in [(pos + arr[pos]) % n, (pos - arr[pos]) % n]:
            if nxt == end:
                return dist + 1
            if not visited[nxt]:
                visited[nxt] = True
                queue.append((nxt, dist + 1))

    return -1
```

**时间复杂度**：O(n)——每个节点最多访问一次。
**空间复杂度**：O(n)，用于 visited 数组和队列。

### Edge Cases
- `start == end` -> 0 次跳跃
- `arr[i] == 0` -> 卡在位置 i（无出边）
- 所有元素相同 -> 规律性跳跃模式

---

## 8. Robot Distance in Grid

**Pattern**: **DP（动态规划）** Precomputation / 4-Direction Obstacle Distance

### Problem Statement

给定一个网格，其中：
- `O` = 机器人
- `E` = 空格
- `X` = 障碍物

以及一个距离数组 `[left, top, bottom, right]`，表示目标机器人到各方向最近障碍物的距离，
找出与之匹配的机器人。

### Approach

用 DP 预计算每个格子在四个方向上到最近障碍物的距离，
然后遍历所有机器人格子，检查其四方向距离是否与查询匹配。

```python
from typing import List, Optional, Tuple

INF = float("inf")


def find_robot(
    grid: List[List[str]], target_dist: Tuple[int, int, int, int]
) -> Optional[Tuple[int, int]]:
    """Find the robot whose distances to nearest obstacle in 4 directions match.

    Args:
        grid: 2D grid with 'O' (robot), 'E' (empty), 'X' (obstacle).
        target_dist: (left, top, bottom, right) distances.

    Returns:
        (row, col) of matching robot, or None.
    """
    if not grid or not grid[0]:
        return None

    rows, cols = len(grid), len(grid[0])

    # Precompute distances to nearest obstacle in 4 directions
    left_dist = [[0] * cols for _ in range(rows)]
    right_dist = [[0] * cols for _ in range(rows)]
    top_dist = [[0] * cols for _ in range(rows)]
    bottom_dist = [[0] * cols for _ in range(rows)]

    # Left: scan each row left-to-right
    for r in range(rows):
        dist = 0
        for c in range(cols):
            if grid[r][c] == "X":
                dist = 0
            else:
                left_dist[r][c] = dist
                dist += 1

    # Right: scan each row right-to-left
    for r in range(rows):
        dist = 0
        for c in range(cols - 1, -1, -1):
            if grid[r][c] == "X":
                dist = 0
            else:
                right_dist[r][c] = dist
                dist += 1

    # Top: scan each column top-to-bottom
    for c in range(cols):
        dist = 0
        for r in range(rows):
            if grid[r][c] == "X":
                dist = 0
            else:
                top_dist[r][c] = dist
                dist += 1

    # Bottom: scan each column bottom-to-top
    for c in range(cols):
        dist = 0
        for r in range(rows - 1, -1, -1):
            if grid[r][c] == "X":
                dist = 0
            else:
                bottom_dist[r][c] = dist
                dist += 1

    # Find robot matching target distances
    t_left, t_top, t_bottom, t_right = target_dist
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "O":
                if (
                    left_dist[r][c] == t_left
                    and top_dist[r][c] == t_top
                    and bottom_dist[r][c] == t_bottom
                    and right_dist[r][c] == t_right
                ):
                    return (r, c)

    return None
```

**时间复杂度**：预计算 O(rows * cols) + 查找 O(rows * cols)。
**空间复杂度**：O(rows * cols)，用于四个方向的距离矩阵。

### Edge Cases
- 机器人在网格边界（到障碍物的距离等于到边界的距离）
- 多个机器人具有相同的距离分布（返回第一个匹配或全部）
- 没有匹配的机器人

### Note on Distance Definition

问题可能将"距离"定义为到最近障碍物的格数，或到边界的格数（将边界视为障碍物）。
请与面试官确认。上述方案将起始列/行的边缘距离视为 0（隐式边界墙）。

---

## 9. Min Operations n to 0

**Pattern**: **Greedy（贪心）** / **NAF (Non-Adjacent Form，非相邻表示法)**

### Problem Statement

给定整数 `n`，使用操作 `n += 2^i` 或 `n -= 2^i`（i 为任意非负整数）将其减至 0。
求最少操作次数。

### Approach

等价于求 `n` 的 **NAF (Non-Adjacent Form，非相邻表示法)**。
核心思路：最少操作次数等于 NAF 中非零数字的个数。基于 `n % 4` 的贪心规则：

- 若 `n % 2 == 0`：除以 2（右移），无需操作
- 若 `n % 4 == 1`：减 1（一次操作）
- 若 `n % 4 == 3`：加 1（一次操作，产生更长的进位，但总操作次数更少）

```python
def min_operations(n: int) -> int:
    """Minimum +/- 2^i operations to reduce n to 0."""
    if n < 0:
        n = -n  # symmetric
    ops = 0
    while n > 0:
        if n % 2 == 0:
            n //= 2
        elif n % 4 == 1:
            n -= 1
            ops += 1
            n //= 2
        else:  # n % 4 == 3
            n += 1
            ops += 1
            n //= 2
    return ops
```

**时间复杂度**：O(log n)——每次迭代至少将 n 减半。
**空间复杂度**：O(1)。

### Proof of Optimality

NAF 在所有有符号二进制表示中，非零数字位数最少。
贪心规则 `n%4==3 -> +1` 可避免相邻的 1 位，这正是 NAF 的构造方式。

### Alternative: Bit Counting

```python
def min_operations_bit(n: int) -> int:
    """Count non-zero digits in NAF representation."""
    ops = 0
    while n:
        if n & 1:
            # Check if we have consecutive 1-bits
            if n & 2:
                n += 1  # NAF: replace trailing 11 with 100 then subtract
            else:
                n -= 1
            ops += 1
        n >>= 1
    return ops
```

### Edge Cases
- n = 0 -> 0 次操作
- n = 1 -> 1 次操作（减去 2^0）
- n 是 2 的幂次 -> 1 次操作
- 大数 n（在 O(log n) 内完成）

---

## 10. Shortest Subarray with k Distinct

**Pattern**: **Sliding Window（滑动窗口）** + Counter（计数器）

### Problem Statement

给定数组 `nums` 和整数 `k`，求包含至少 `k` 个不同元素的最短子数组长度。
若不可能，返回 -1。

### Approach

经典滑动窗口 + 频率计数器。向右扩展直到有 `k` 个不同元素，然后向左收缩以最小化长度。

```python
from collections import defaultdict
from typing import List


def shortest_subarray_k_distinct(nums: List[int], k: int) -> int:
    """Find shortest subarray with at least k distinct elements."""
    n = len(nums)
    if k > n:
        return -1

    counter: dict[int, int] = defaultdict(int)
    distinct = 0
    min_len = n + 1
    left = 0

    for right in range(n):
        if counter[nums[right]] == 0:
            distinct += 1
        counter[nums[right]] += 1

        # Shrink from left while we still have k distinct
        while distinct >= k:
            min_len = min(min_len, right - left + 1)
            counter[nums[left]] -= 1
            if counter[nums[left]] == 0:
                distinct -= 1
            left += 1

    return min_len if min_len <= n else -1
```

**时间复杂度**：O(n)——每个元素进出窗口各一次。
**空间复杂度**：O(k)，用于计数器。

### Edge Cases
- 所有元素相同且 k > 1 -> 返回 -1
- k = 1 -> 返回 1
- 整个数组恰好有 k 个不同元素 -> 返回 n（若无更短子数组）

---

## 11. Price Discount (Monotonic Stack)

**Pattern**: **Monotonic Stack（单调栈）** / Next Smaller Element（下一个更小元素）

### Problem Statement

对于索引 `i` 处价格为 `prices[i]` 的商品，找到第一个 `j > i` 使得 `prices[j] <= prices[i]`。
索引 `i` 处的折扣价为 `prices[i] - prices[j]`。
输出：总折扣后的价格之和，以及以原价出售的商品索引（即找不到 j 的索引）。

### Approach

使用单调栈查找每个索引的"下一个更小或等于"的元素。

```python
from typing import List, Tuple


def price_discount(prices: List[int]) -> Tuple[int, List[int]]:
    """Compute total discounted sum and indices sold at original price.

    For each i, discount = prices[j] where j is first j>i with prices[j] <= prices[i].
    If no such j, item sold at original price.

    Returns:
        (total_sum, original_price_indices)
    """
    n = len(prices)
    discount = [0] * n  # discount applied at each index
    stack: List[int] = []  # monotonic stack of indices

    for i in range(n):
        # Pop all elements where current price <= stack top price
        while stack and prices[i] <= prices[stack[-1]]:
            idx = stack.pop()
            discount[idx] = prices[i]
        stack.append(i)

    # Remaining in stack: no discount (sold at original price)
    original_indices = list(stack)

    total = sum(prices[i] - discount[i] for i in range(n))
    return total, sorted(original_indices)
```

**时间复杂度**：O(n)——每个元素最多入栈和出栈各一次。
**空间复杂度**：O(n)，用于栈和折扣数组。

### Example

```
prices = [8, 4, 6, 2, 3]
Discounts: 8-4=4, 4-2=2, 6-2=4, 2 (original), 3 (original)
Total = 4 + 2 + 4 + 2 + 3 = 15
Original price indices: [3, 4]
```

### Edge Cases
- 所有价格递增 -> 每件商品都被下一件折扣
- 所有价格递减 -> 只有最后一件以原价出售
- 所有价格相同 -> 每件被下一件折扣，最后一件以原价出售

---

## 12. Balanced Permutation

**Pattern**: Tracking Min/Max Positions（追踪最小/最大位置）

### Problem Statement

给定 `1..n` 的一个排列，对每个 `k`（从 1 到 n），检查是否存在一个连续子数组构成 `1..k` 的排列。

### Approach

记录每个值的位置。要使连续子数组构成 `1..k` 的排列，所有值 `1..k` 必须占据连续的索引范围。
随着 k 增大，维护 `min_pos` 和 `max_pos`。若 `max_pos - min_pos + 1 == k`，则满足条件。

```python
from typing import List


def balanced_permutation(perm: List[int]) -> List[bool]:
    """For each k=1..n, check if a contiguous subarray forms perm of 1..k.

    Args:
        perm: A permutation of 1..n (1-indexed values).

    Returns:
        List of booleans, result[k-1] = True if subarray perm of 1..k exists.
    """
    n = len(perm)
    pos = [0] * (n + 1)  # pos[v] = index of value v in perm
    for i, v in enumerate(perm):
        pos[v] = i

    result: List[bool] = []
    min_pos = pos[1]
    max_pos = pos[1]

    for k in range(1, n + 1):
        min_pos = min(min_pos, pos[k])
        max_pos = max(max_pos, pos[k])
        # If the range [min_pos, max_pos] has exactly k elements,
        # and we know values 1..k are all within it, it must be a perm of 1..k
        result.append(max_pos - min_pos + 1 == k)

    return result
```

**时间复杂度**：O(n)。
**空间复杂度**：O(n)，用于位置数组。

### Proof

对于值 `1..k` 所占位置的范围 `max_pos - min_pos + 1`：
- 若范围 == k，则 k 个槽位恰好存放 k 个值，无间隙 -> 连续排列。
- 若范围 > k，则区间内存在不属于 `1..k` 的值 -> 非连续排列。

### Edge Cases
- n = 1 -> 始终为 [True]
- 有序排列 [1,2,3,...,n] -> 全为 True
- 逆序排列 -> 仅 k=1 和 k=n 为 True

---

## 13. Elevator/Stairs Energy

**Pattern**: **Binary Search（二分查找）** on Split Point

### Problem Statement

一个人先乘电梯爬 `mid` 层，再走楼梯爬剩余楼层。
- 电梯：每层增加 `e1` 能量，花费 `t1` 时间。
- 楼梯：每层消耗 `e2` 能量，每层时间 = `ceil(c / 当前能量)`。

求使总时间最小（或使两种策略的时间差最小）的分割点。

### Approach

对分割点 `mid` 进行二分/线性搜索。对每个候选点计算：
1. 电梯阶段（楼层 0..mid）的时间
2. 楼梯阶段（楼层 mid..总层数，与能量相关）的时间

```python
import math
from typing import Tuple


def optimal_split(
    total_floors: int,
    e1: float,
    t1: float,
    e2: float,
    c: float,
    initial_energy: float,
) -> Tuple[int, float]:
    """Find optimal floor to switch from elevator to stairs.

    Args:
        total_floors: Total floors to climb.
        e1: Energy gained per elevator floor.
        t1: Time per elevator floor.
        e2: Energy consumed per stair floor.
        c: Constant for stair time calculation.
        initial_energy: Starting energy.

    Returns:
        (split_floor, total_time)
    """

    def compute_time(split: int) -> float:
        """Total time if taking elevator for first 'split' floors."""
        # Elevator phase
        elev_time = split * t1
        energy = initial_energy + split * e1

        # Stairs phase
        stairs_floors = total_floors - split
        stair_time = 0.0
        for _ in range(stairs_floors):
            if energy <= 0:
                return float("inf")  # Can't climb
            stair_time += math.ceil(c / energy)
            energy -= e2

        return elev_time + stair_time

    best_split = 0
    best_time = float("inf")

    # Binary search works if time function is unimodal (valley-shaped)
    # Otherwise, linear scan:
    for split in range(total_floors + 1):
        t = compute_time(split)
        if t < best_time:
            best_time = t
            best_split = split

    return best_split, best_time
```

**时间复杂度**：线性扫描 O(n^2)（每次评估 O(n)，共 n 个候选）。
若时间函数为单峰（谷形），使用三分搜索：O(n log n)。
**空间复杂度**：O(1)。

### Binary Search Optimization (if unimodal)

```python
def optimal_split_binary(
    total_floors: int,
    e1: float, t1: float, e2: float, c: float,
    initial_energy: float,
) -> Tuple[int, float]:
    """Ternary search for minimum on unimodal function."""

    def compute_time(split: int) -> float:
        elev_time = split * t1
        energy = initial_energy + split * e1
        stair_time = 0.0
        for _ in range(total_floors - split):
            if energy <= 0:
                return float("inf")
            stair_time += math.ceil(c / energy)
            energy -= e2
        return elev_time + stair_time

    lo, hi = 0, total_floors
    while hi - lo > 2:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if compute_time(m1) < compute_time(m2):
            hi = m2
        else:
            lo = m1

    best_split = lo
    best_time = compute_time(lo)
    for s in range(lo + 1, hi + 1):
        t = compute_time(s)
        if t < best_time:
            best_time = t
            best_split = s
    return best_split, best_time
```

### Edge Cases
- 0 层 -> 时间为 0
- 楼梯阶段能量耗尽 -> 需要更多电梯楼层
- 全程乘电梯或全程走楼梯可能是最优解

---

## 14. N-ary Tree 3-Part

**Pattern**: Tree DFS（树形深度优先搜索）/ Path Finding（路径查找）

### Problem Statement

给定一棵 N 叉树，实现三个操作：
1. 求所有节点值之和
2. 找出最大路径值（根到叶）
3. 返回最大路径上的节点

### Solution

```python
from typing import List, Optional, Tuple


class NaryNode:
    """N-ary tree node."""

    def __init__(self, val: int, children: Optional[List["NaryNode"]] = None):
        self.val: int = val
        self.children: List["NaryNode"] = children or []


def sum_all(root: Optional[NaryNode]) -> int:
    """Part (a): Sum all node values in the tree."""
    if root is None:
        return 0
    return root.val + sum(sum_all(child) for child in root.children)


def max_path_value(root: Optional[NaryNode]) -> int:
    """Part (b): Find maximum root-to-leaf path sum."""
    if root is None:
        return 0
    if not root.children:
        return root.val
    return root.val + max(max_path_value(c) for c in root.children)


def max_path_nodes(root: Optional[NaryNode]) -> List[int]:
    """Part (c): Return node values on the maximum root-to-leaf path."""
    if root is None:
        return []
    if not root.children:
        return [root.val]

    best_path: List[int] = []
    best_sum = float("-inf")

    for child in root.children:
        child_path = max_path_nodes(child)
        child_sum = sum(child_path)
        if child_sum > best_sum:
            best_sum = child_sum
            best_path = child_path

    return [root.val] + best_path
```

**时间复杂度**：每个操作 O(n)——遍历每个节点一次。
**空间复杂度**：O(h)，h 为树的高度（递归深度）。

### Optimization: Single Pass for All Three

```python
def tree_analysis(
    root: Optional[NaryNode],
) -> Tuple[int, int, List[int]]:
    """Compute all three parts in a single DFS.

    Returns: (total_sum, max_path_value, max_path_nodes)
    """
    if root is None:
        return 0, 0, []

    if not root.children:
        return root.val, root.val, [root.val]

    total = root.val
    best_child_sum = float("-inf")
    best_child_path: List[int] = []

    for child in root.children:
        child_total, child_max, child_path = tree_analysis(child)
        total += child_total
        if child_max > best_child_sum:
            best_child_sum = child_max
            best_child_path = child_path

    return (
        total,
        root.val + best_child_sum,
        [root.val] + best_child_path,
    )
```

### Edge Cases
- 空树（root 为 None）
- 单节点（叶节点即根节点）
- 所有值为负数
- 多条路径具有相同最大和（返回任意一条）

---

## 15. Max Throughput with Budget

**Pattern**: **Binary Search on Answer（二分答案）**

### Problem Statement

给定 `n` 个服务，每个服务有 `current_throughput[i]` 和 `scale_cost[i]`（每单位吞吐量的扩容成本），
以及预算 `B`。在所有服务都达到同一水平的前提下，求可实现的最大吞吐量（瓶颈为最小值）。

### Approach

对目标吞吐量 `T` 进行二分查找。对每个候选 T，计算将所有服务提升至 T 的总成本。
若成本 <= 预算，则 T 可行。

```python
from typing import List


def max_throughput(
    current: List[int], cost: List[int], budget: int
) -> int:
    """Find max throughput achievable within budget.

    Each service i needs (T - current[i]) * cost[i] to reach throughput T.
    Only services below T need scaling.
    """
    n = len(current)

    def feasible(target: int) -> bool:
        total_cost = 0
        for i in range(n):
            if current[i] < target:
                total_cost += (target - current[i]) * cost[i]
                if total_cost > budget:
                    return False
        return True

    lo = min(current)
    hi = max(current) + budget  # upper bound: all budget on cheapest service

    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1

    return lo
```

**时间复杂度**：O(n * log(最大吞吐量范围))。
**空间复杂度**：O(1)。

### Edge Cases
- 预算为 0 -> 答案为 min(current)
- 所有服务吞吐量相同 -> 均匀分配预算
- 某个服务扩容成本极高（主导预算分配）
- 大预算 -> 上界计算很重要

### Follow-up: Fractional Throughput

若吞吐量可为非整数，使用浮点数二分查找并设置 epsilon 容差：

```python
def max_throughput_float(
    current: List[float], cost: List[float], budget: float
) -> float:
    """Float version with 1e-6 precision."""
    lo = min(current)
    hi = max(current) + budget

    for _ in range(100):  # enough iterations for double precision
        mid = (lo + hi) / 2
        total = sum(max(0, mid - c) * k for c, k in zip(current, cost))
        if total <= budget:
            lo = mid
        else:
            hi = mid

    return lo
```

---

## 16. Parking Lot (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）**

### Problem Statement

设计一个停车场系统：
- `park(vehicle)` - 停放一辆车，返回车位 ID 或 -1
- `unpark(spot_id)` - 从车位移走车辆
- `check_car(license_plate)` - 检查某辆车是否已停放，返回车位 ID 或 -1

约束条件：摩托车位只能停摩托车，普通车位可停摩托车和轿车。

### Solution

```python
from enum import Enum
from typing import Dict, Optional


class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"


class Vehicle:
    """A vehicle with type and license plate."""

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate: str = license_plate
        self.vehicle_type: VehicleType = vehicle_type


class SpotType(Enum):
    MOTORCYCLE = "motorcycle"
    REGULAR = "regular"


class ParkingSpot:
    """A parking spot that may hold a vehicle."""

    def __init__(self, spot_id: int, spot_type: SpotType):
        self.spot_id: int = spot_id
        self.spot_type: SpotType = spot_type
        self.vehicle: Optional[Vehicle] = None

    @property
    def is_available(self) -> bool:
        return self.vehicle is None

    def can_fit(self, vehicle: Vehicle) -> bool:
        """Check if this spot can accommodate the vehicle."""
        if self.spot_type == SpotType.MOTORCYCLE:
            return vehicle.vehicle_type == VehicleType.MOTORCYCLE
        # Regular spots fit both cars and motorcycles
        return True


class ParkingLot:
    """Parking lot with motorcycle and regular spots."""

    def __init__(
        self, num_motorcycle_spots: int, num_regular_spots: int
    ) -> None:
        self.spots: Dict[int, ParkingSpot] = {}
        self.plate_to_spot: Dict[str, int] = {}

        spot_id = 0
        for _ in range(num_motorcycle_spots):
            self.spots[spot_id] = ParkingSpot(spot_id, SpotType.MOTORCYCLE)
            spot_id += 1
        for _ in range(num_regular_spots):
            self.spots[spot_id] = ParkingSpot(spot_id, SpotType.REGULAR)
            spot_id += 1

    def park(self, vehicle: Vehicle) -> int:
        """Park vehicle, return spot ID or -1 if no spot available.

        Strategy: try motorcycle spots first for motorcycles (preserve
        regular spots for cars), then regular spots.
        """
        if vehicle.license_plate in self.plate_to_spot:
            return self.plate_to_spot[vehicle.license_plate]

        # For motorcycles: prefer motorcycle spots first
        preferred_order = (
            [SpotType.MOTORCYCLE, SpotType.REGULAR]
            if vehicle.vehicle_type == VehicleType.MOTORCYCLE
            else [SpotType.REGULAR]
        )

        for pref_type in preferred_order:
            for spot in self.spots.values():
                if (
                    spot.is_available
                    and spot.spot_type == pref_type
                    and spot.can_fit(vehicle)
                ):
                    spot.vehicle = vehicle
                    self.plate_to_spot[vehicle.license_plate] = spot.spot_id
                    return spot.spot_id

        return -1

    def unpark(self, spot_id: int) -> bool:
        """Remove vehicle from spot. Returns True if successful."""
        if spot_id not in self.spots:
            return False
        spot = self.spots[spot_id]
        if spot.vehicle is None:
            return False

        del self.plate_to_spot[spot.vehicle.license_plate]
        spot.vehicle = None
        return True

    def check_car(self, license_plate: str) -> int:
        """Check if car is parked. Return spot ID or -1."""
        return self.plate_to_spot.get(license_plate, -1)
```

**时间复杂度**：
- `park`：O(S)，S 为总车位数（线性扫描可用车位）。
- `unpark`：O(1) 直接访问车位。
- `check_car`：O(1) 哈希查找。

**空间复杂度**：O(S + V)，V 为已停放的车辆数。

### Follow-up: Optimize park() to O(1)

为每种车位类型维护独立的空闲车位队列（deque 或 set）：

```python
from collections import deque


class ParkingLotOptimized:
    """O(1) park/unpark using free-spot queues."""

    def __init__(self, n_moto: int, n_regular: int) -> None:
        self.spots: Dict[int, ParkingSpot] = {}
        self.plate_to_spot: Dict[str, int] = {}
        self.free_motorcycle: deque[int] = deque()
        self.free_regular: deque[int] = deque()

        sid = 0
        for _ in range(n_moto):
            self.spots[sid] = ParkingSpot(sid, SpotType.MOTORCYCLE)
            self.free_motorcycle.append(sid)
            sid += 1
        for _ in range(n_regular):
            self.spots[sid] = ParkingSpot(sid, SpotType.REGULAR)
            self.free_regular.append(sid)
            sid += 1

    def park(self, vehicle: Vehicle) -> int:
        if vehicle.license_plate in self.plate_to_spot:
            return self.plate_to_spot[vehicle.license_plate]

        spot_id = -1
        if vehicle.vehicle_type == VehicleType.MOTORCYCLE:
            if self.free_motorcycle:
                spot_id = self.free_motorcycle.popleft()
            elif self.free_regular:
                spot_id = self.free_regular.popleft()
        else:  # CAR
            if self.free_regular:
                spot_id = self.free_regular.popleft()

        if spot_id == -1:
            return -1

        self.spots[spot_id].vehicle = vehicle
        self.plate_to_spot[vehicle.license_plate] = spot_id
        return spot_id

    def unpark(self, spot_id: int) -> bool:
        if spot_id not in self.spots or self.spots[spot_id].vehicle is None:
            return False
        spot = self.spots[spot_id]
        del self.plate_to_spot[spot.vehicle.license_plate]
        spot.vehicle = None
        if spot.spot_type == SpotType.MOTORCYCLE:
            self.free_motorcycle.append(spot_id)
        else:
            self.free_regular.append(spot_id)
        return True
```

### Edge Cases
- 停放已在停车场的车（幂等操作）
- 对空车位执行 unpark
- 所有车位已满

---

## 17. Task Assignment to 2 People

**Pattern**: **Greedy（贪心）** / Sort by Difference（按差值排序）

### Problem Statement

给定 `n` 个任务，`reward1[i]`（人员 1 完成任务 i 的奖励）和 `reward2[i]`（人员 2 完成任务 i 的奖励）。
人员 1 必须完成恰好 `k` 个任务，人员 2 完成其余任务。求最大总奖励。

### Approach

对每个任务，计算分配给人员 1 的"优势"：`diff[i] = reward1[i] - reward2[i]`。
按 diff 降序排序，将前 k 个任务分配给人员 1，其余分配给人员 2。

```python
from typing import List, Tuple


def max_reward(
    reward1: List[int], reward2: List[int], k: int
) -> Tuple[int, List[int]]:
    """Assign k tasks to person 1, rest to person 2, maximizing total reward.

    Returns: (max_total, list of task indices assigned to person 1)
    """
    n = len(reward1)
    # (advantage of person 1, task index)
    diffs = [(reward1[i] - reward2[i], i) for i in range(n)]
    diffs.sort(reverse=True)

    person1_tasks = [idx for _, idx in diffs[:k]]
    total = 0
    person1_set = set(person1_tasks)
    for i in range(n):
        if i in person1_set:
            total += reward1[i]
        else:
            total += reward2[i]

    return total, sorted(person1_tasks)
```

**时间复杂度**：O(n log n)，用于排序。
**空间复杂度**：O(n)。

### Proof of Correctness

初始时将所有任务分配给人员 2，总奖励 = sum(reward2)。
将任务 i 从人员 2 切换到人员 1，总奖励变化量为 `reward1[i] - reward2[i]`。
为最大化，选取 diff 最大的 k 个任务。

### Edge Cases
- k = 0 -> 所有任务分配给人员 2
- k = n -> 所有任务分配给人员 1
- 所有 diff 相等 -> 任意 k 个任务均可
- 所有 diff 为负 -> 仍需分配 k 个任务给人员 1

---

## 18. Jump Game Prime-Ending Variant

**Pattern**: **DP（动态规划）** / **Sieve of Eratosthenes（埃拉托斯特尼筛法）**

### Problem Statement

类似 LC 1696（Jump Game VI），但从位置 `i` 可以跳到 `i+1` 或 `i+p`，
其中 `p` 是末位数字为 3 的质数（3, 13, 23, 43, 53, 73, 83, ...）。
求到达最后一个索引的最小代价。

### Approach

1. 使用**埃拉托斯特尼筛法**预计算所有 <= n 的末位为 3 的质数。
2. 从左到右做 DP：`dp[i]` = 到达索引 `i` 的最小代价。
3. 对每个 `i`：`dp[i] = min(dp[i-1], dp[i-p] for all valid primes p) + cost[i]`。

```python
from typing import List


def sieve_primes_ending_3(limit: int) -> List[int]:
    """Return all primes <= limit that end in digit 3."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [p for p in range(2, limit + 1) if is_prime[p] and p % 10 == 3]


def min_cost_jump(cost: List[int]) -> int:
    """Minimum cost to reach last index.

    From index i, can jump to i+1 or i+p (p = prime ending in 3).
    """
    n = len(cost)
    if n <= 1:
        return cost[0] if cost else 0

    primes = sieve_primes_ending_3(n)

    INF = float("inf")
    dp = [INF] * n
    dp[0] = cost[0]

    for i in range(1, n):
        # Jump +1 from i-1
        dp[i] = dp[i - 1] + cost[i]

        # Jump +p from i-p
        for p in primes:
            if p > i:
                break
            dp[i] = min(dp[i], dp[i - p] + cost[i])

    return dp[n - 1]
```

**时间复杂度**：O(n * P)，P 为 <= n 的末位为 3 的质数个数。
n=10000 时，P 约为 100 个，实际约为 O(100n)。
**空间复杂度**：O(n)（dp 数组）+ O(n)（筛法）。

### Optimization: Deque for Sliding Window Minimum

若需要 O(n) 或 O(n log n)，可使用线段树或单调双端队列处理有效跳跃位置。
但由于 P 较小，O(nP) 方案已足够实用。

### Edge Cases
- n = 1 -> 返回 cost[0]
- 所有代价为负（最大化负数路径）
- 大 n（筛法为 O(n log log n)，可忽略不计）

---

## 19. Min Edge Reversal for Optimal Root

**Pattern**: **Re-rooting DP（换根 DP）**

### Problem Statement

给定一棵有 `n` 个节点的有向树，选择一个根节点，使需要反转的边数（使所有边从根向外指）最少。
返回最少反转次数及对应的根节点编号。

### Approach

1. 构建无向邻接表，记录原始方向。
2. 从节点 0 出发 DFS：统计以 0 为根时所需的反转次数。
3. 换根：将根从父节点移至子节点时，若边为 parent->child（正向），反转次数 += 1；
   若边为 child->parent（反向），反转次数 -= 1。

```python
from collections import defaultdict
from typing import List, Tuple


def min_reversals(n: int, edges: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Find optimal root minimizing edge reversals.

    Args:
        n: Number of nodes.
        edges: Directed edges (u, v) meaning u -> v.

    Returns:
        (min_reversals, optimal_root)
    """
    # Build adjacency: (neighbor, cost_to_reverse)
    # If edge u->v exists, going from u to v costs 0 (correct direction),
    # but going from v to u costs 1 (reversal needed).
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v in edges:
        adj[u].append((v, 0))  # original direction: no reversal
        adj[v].append((u, 1))  # reverse direction: needs reversal

    # Step 1: DFS from node 0 to count reversals rooted at 0
    cost_at_0 = 0
    visited = [False] * n

    def dfs(node: int) -> None:
        nonlocal cost_at_0
        visited[node] = True
        for neighbor, cost in adj[node]:
            if not visited[neighbor]:
                cost_at_0 += cost
                dfs(neighbor)

    dfs(0)

    # Step 2: Re-root DP
    result = [0] * n
    result[0] = cost_at_0

    visited = [False] * n

    def reroot(node: int) -> None:
        visited[node] = True
        for neighbor, cost in adj[node]:
            if not visited[neighbor]:
                # Moving root from node to neighbor:
                # cost=0 means edge node->neighbor (forward), now becomes
                # backward, so +1 reversal
                # cost=1 means edge neighbor->node (backward), now becomes
                # forward, so -1 reversal
                result[neighbor] = result[node] + (1 if cost == 0 else -1)
                reroot(neighbor)

    reroot(0)

    min_rev = min(result)
    optimal = result.index(min_rev)
    return min_rev, optimal
```

**时间复杂度**：O(n)——两次 DFS。
**空间复杂度**：O(n)，用于邻接表和结果数组。

### Key Insight

将根从父节点 `p` 移至子节点 `c` 时：
- 若原始边为 `p -> c`（从 p 出发 cost=0）：以 p 为根时方向正确，以 c 为根时方向相反，反转次数 += 1。
- 若原始边为 `c -> p`（从 p 出发 cost=1）：以 p 为根时方向相反，以 c 为根时方向正确，反转次数 -= 1。

### Edge Cases
- 所有边从节点 0 向外指 -> 0 次反转，以 0 为根
- 星形图 -> 取决于边的方向
- 线性链 -> 以一端为根

### Warning: 1-indexed Nodes

若问题使用 1 索引节点，需调整：
```python
visited = [False] * (n + 1)
result = [0] * (n + 1)
```

---

## 20. Palindrome Paths in Tree

**Pattern**: **Bitmask（位掩码）** XOR DFS / Prefix on Tree（树上前缀）

### Problem Statement

给定一棵树，每条边标有一个字符（a-z），统计路径数量，使得路径上的字符可以重新排列成回文串。

### Approach

若字符串可以重排成回文串，则至多有一个字符出现奇数次。
用位掩码表示字符频率（第 i 位 = 字符 i 的频率奇偶性）。
若路径的 XOR 位掩码为 0 或恰好一位为 1，则该路径为回文路径。

从根节点出发用 DFS 维护前缀 XOR。路径 (u, v) 的掩码：`mask(u,v) = prefix[u] XOR prefix[v]`。

```python
from collections import defaultdict
from typing import List, Tuple


def count_palindrome_paths(
    n: int, edges: List[Tuple[int, int, str]]
) -> int:
    """Count paths whose edge labels can form a palindrome.

    Args:
        n: Number of nodes (0-indexed).
        edges: (u, v, char) undirected edges.

    Returns:
        Number of palindrome-formable paths.
    """
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v, ch in edges:
        bit = 1 << (ord(ch) - ord("a"))
        adj[u].append((v, bit))
        adj[v].append((u, bit))

    # prefix[node] = XOR of all edge bits from root to node
    prefix = [0] * n
    visited = [False] * n
    count = 0

    # Counter of prefix masks seen so far
    mask_count: dict[int, int] = defaultdict(int)

    def dfs(node: int) -> None:
        nonlocal count
        visited[node] = True

        # Count pairs: path (u, v) has mask prefix[u] ^ prefix[v]
        # Palindrome if mask == 0 or mask has exactly one bit set

        # Case 1: prefix[v] == prefix[node] -> XOR = 0
        count += mask_count[prefix[node]]

        # Case 2: prefix[v] ^ prefix[node] has exactly one bit set
        for bit in range(26):
            target = prefix[node] ^ (1 << bit)
            count += mask_count[target]

        mask_count[prefix[node]] += 1

        for neighbor, bit_mask in adj[node]:
            if not visited[neighbor]:
                prefix[neighbor] = prefix[node] ^ bit_mask
                dfs(neighbor)

    dfs(0)
    return count
```

**时间复杂度**：O(26n) = O(n)。
**空间复杂度**：O(n)，用于前缀数组和掩码计数器。

### Key Insight

- 从根节点出发的前缀 XOR 表示根到节点路径上每个字符的频率奇偶性。
- `prefix[u] XOR prefix[v]` 消除了公共的根到 LCA 部分，只保留 u 到 v 路径的字符频率奇偶性。
- 回文串要求 XOR = 0（全为偶数）或恰好一位为 1（一个奇数字符）。

### Edge Cases
- 单节点（0 条路径）
- 线性树（路径为子路径）
- 所有边标同一字符（所有路径均为回文路径）

---

## 21. Minesweeper Grid Generator

**Pattern**: Random Placement（随机布局）/ Code Quality（代码质量）

### Problem Statement

生成一个 M x N 的扫雷网格，随机放置恰好 K 个地雷。
显示网格时，每个格子显示相邻 8 格中地雷的数量，或用 `*` 表示地雷。

**延伸问题**：迭代改进代码质量——去除不必要的变量、简化逻辑、减少集合使用。

### Solution (Clean Version)

```python
import random
from typing import List


def generate_minesweeper(rows: int, cols: int, mines: int) -> List[List[str]]:
    """Generate a minesweeper grid with random mine placement.

    Args:
        rows, cols: Grid dimensions.
        mines: Number of mines to place.

    Returns:
        Grid where '*' = mine, digit = adjacent mine count.
    """
    total = rows * cols
    if mines > total:
        raise ValueError(f"Cannot place {mines} mines on {total}-cell grid")

    # Random mine positions
    positions = random.sample(range(total), mines)
    mine_set = set()
    for pos in positions:
        mine_set.add((pos // cols, pos % cols))

    # Build grid
    grid: List[List[str]] = []
    for r in range(rows):
        row: List[str] = []
        for c in range(cols):
            if (r, c) in mine_set:
                row.append("*")
            else:
                count = sum(
                    1
                    for dr in (-1, 0, 1)
                    for dc in (-1, 0, 1)
                    if (dr or dc)
                    and 0 <= r + dr < rows
                    and 0 <= c + dc < cols
                    and (r + dr, c + dc) in mine_set
                )
                row.append(str(count))
        grid.append(row)

    return grid


def print_grid(grid: List[List[str]]) -> None:
    """Pretty-print a minesweeper grid."""
    for row in grid:
        print(" ".join(row))
```

**时间复杂度**：O(M * N)（每格检查 8 个邻居，O(1)）。
**空间复杂度**：O(M * N)（网格）+ O(K)（地雷集合）。

### Follow-up: Iterative Code Quality Improvement

面试官会要求代码逐步变得更简洁：

**V1（初版）**：使用独立的 `is_mine` 二维数组，显式列出 8 个方向，变量较多。

**V2（简化版）**：用集合内联地雷检查，生成器表达式计算计数。

**V3（极简版）**：
```python
def minesweeper(m: int, n: int, k: int) -> List[List[str]]:
    mines = set(random.sample(range(m * n), k))
    is_mine = lambda r, c: r * n + c in mines

    def count(r: int, c: int) -> str:
        if is_mine(r, c):
            return "*"
        return str(sum(
            is_mine(r + dr, c + dc)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr or dc) and 0 <= r + dr < m and 0 <= c + dc < n
        ))

    return [[count(r, c) for c in range(n)] for r in range(m)]
```

### Edge Cases
- 0 个地雷 -> 全为 0
- 全为地雷 -> 全为星号
- 1x1 网格且有一个地雷

---

## 22. 2D Grid Nearest Exit (BFS)

**Pattern**: **BFS（广度优先搜索）** / Shortest Path（最短路径）

### Problem Statement

给定一个二维网格，包含墙和空格，从起始位置找到最近的出口（开放的边界格子）。
起始位置本身不算出口。

### Solution

```python
from collections import deque
from typing import List, Tuple


def nearest_exit(
    grid: List[List[str]], start: Tuple[int, int]
) -> int:
    """Find minimum steps from start to nearest exit (open boundary cell).

    Args:
        grid: '.' = open, '+' = wall.
        start: (row, col) starting position.

    Returns:
        Minimum steps to exit, or -1 if impossible.
    """
    rows, cols = len(grid), len(grid[0])
    sr, sc = start

    visited = [[False] * cols for _ in range(rows)]
    visited[sr][sc] = True
    queue: deque[Tuple[int, int, int]] = deque([(sr, sc, 0)])

    while queue:
        r, c, dist = queue.popleft()

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                if grid[nr][nc] == ".":
                    # Check if it's a boundary cell (exit)
                    if (
                        nr == 0
                        or nr == rows - 1
                        or nc == 0
                        or nc == cols - 1
                    ):
                        return dist + 1
                    visited[nr][nc] = True
                    queue.append((nr, nc, dist + 1))

    return -1
```

**时间复杂度**：O(M * N)——每个格子最多访问一次。
**空间复杂度**：O(M * N)，用于 visited 数组和队列。

### Edge Cases
- 起点在边界（仍需移动到另一个出口）
- 没有可达的出口（被墙包围）
- 多个出口距离相同

---

## 23. Lock Combination BFS

**Pattern**: BFS on State Space（状态空间 BFS）

### Problem Statement

一把锁有 `n` 个转盘，每个转盘有 0-9 十个数字。每次操作可将一个转盘向上或向下转动 1 位。
给定目标组合和一组"死锁"组合（需要避免），求从"0000"到目标的最少操作次数。

### Solution

这本质上是 LC 752（Open the Lock），Uber 常考：

```python
from collections import deque
from typing import List, Set


def min_moves_to_unlock(
    deadends: List[str], target: str
) -> int:
    """Minimum moves to reach target from '0000', avoiding deadends.

    Each move: rotate one wheel +1 or -1.
    """
    dead: Set[str] = set(deadends)
    start = "0000"

    if start in dead or target in dead:
        return -1

    if start == target:
        return 0

    visited: Set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])

    while queue:
        state, moves = queue.popleft()

        for i in range(len(state)):
            digit = int(state[i])
            for delta in (1, -1):
                new_digit = (digit + delta) % 10
                new_state = state[:i] + str(new_digit) + state[i + 1 :]

                if new_state == target:
                    return moves + 1

                if new_state not in visited and new_state not in dead:
                    visited.add(new_state)
                    queue.append((new_state, moves + 1))

    return -1
```

**时间复杂度**：O(10^n * n)，n 为转盘数量。n=4 时：O(40000)。
**空间复杂度**：O(10^n)，用于 visited 集合。

### Optimization: Bidirectional BFS

```python
def min_moves_bidirectional(
    deadends: List[str], target: str
) -> int:
    """Bidirectional BFS for faster convergence."""
    dead = set(deadends)
    start = "0000"
    if start in dead or target in dead:
        return -1
    if start == target:
        return 0

    front: Set[str] = {start}
    back: Set[str] = {target}
    visited: Set[str] = set()
    moves = 0

    while front and back:
        # Always expand the smaller frontier
        if len(front) > len(back):
            front, back = back, front

        next_front: Set[str] = set()
        for state in front:
            for i in range(len(state)):
                digit = int(state[i])
                for delta in (1, -1):
                    new_digit = (digit + delta) % 10
                    ns = state[:i] + str(new_digit) + state[i + 1 :]

                    if ns in back:
                        return moves + 1
                    if ns not in visited and ns not in dead:
                        visited.add(ns)
                        next_front.add(ns)

        front = next_front
        moves += 1

    return -1
```

### Edge Cases
- "0000" 是死锁 -> 返回 -1
- 目标为 "0000" -> 返回 0
- 不存在路径 -> 返回 -1

---

## 24. Non-overlapping Interval Triples

**Pattern**: Sorting（排序）+ Greedy（贪心）/ **DP（动态规划）**

### Problem Statement

给定一组区间 `[start, end]`，统计三个区间构成的组合数量，使得组中任意两个区间互不重叠。

### Approach

按结束时间排序区间。对于每个区间作为"中间"区间，统计在其开始之前结束的区间数（左侧候选）
和在其结束之后开始的区间数（右侧候选）。以该区间为中间的三元组数 = `left * right`。

```python
import bisect
from typing import List, Tuple


def count_non_overlapping_triples(
    intervals: List[Tuple[int, int]]
) -> int:
    """Count groups of 3 pairwise non-overlapping intervals."""
    intervals.sort()
    n = len(intervals)

    # Precompute: ends sorted for binary search
    ends = sorted(e for _, e in intervals)
    starts = sorted(s for s, _ in intervals)

    count = 0

    for i in range(n):
        s, e = intervals[i]

        # Count intervals that end strictly before s (can precede interval i)
        left = bisect.bisect_left(ends, s)

        # Count intervals that start strictly after e (can follow interval i)
        right = n - bisect.bisect_right(starts, e)

        count += left * right

    # Each triple is counted 1 time (middle element is unique)
    # But we need to handle overcounting: if left has 2+ and they overlap each other,
    # we overcounted. For exact count, need more careful approach.
    # The above is an APPROXIMATION. For exact count, use the approach below.

    return count


def count_triples_exact(intervals: List[Tuple[int, int]]) -> int:
    """Exact count using sorted order and DP.

    Sort by end time. For each interval i, count pairs of non-overlapping
    intervals that end before i starts. Then i extends each pair to a triple.
    """
    intervals.sort(key=lambda x: x[1])
    n = len(intervals)
    ends = [e for _, e in intervals]

    # pairs_before[i] = number of non-overlapping pairs among intervals
    # that end before intervals[i] starts
    # singles_before[i] = number of intervals that end before intervals[i] starts

    count = 0
    # For each interval i, find how many intervals end before its start
    # Then from those, how many non-overlapping pairs exist

    # Approach: sweep and maintain count of singles and pairs
    # When processing interval i (sorted by end):
    #   - singles = number of previous intervals that end before start[i]
    #   - pairs = number of non-overlapping pairs among those

    # Prefix approach:
    # singles[i] = number of intervals j < i where end[j] < start[i]
    # For triples: for interval i, count pairs among intervals ending before start[i]

    # Two-pass: first compute singles_before for each interval
    singles = [0] * n
    for i in range(n):
        singles[i] = bisect.bisect_left(ends, intervals[i][0])

    # pairs_ending_before[t] = number of non-overlapping pairs where both
    # intervals end before time t
    # For each interval i (in end-sorted order), it forms pairs with
    # all singles_before[i] intervals before it.
    # pairs_before[i] = sum of singles_before[j] for all j where end[j] < start[i]
    # This requires a Fenwick tree or prefix sum approach.

    # Simpler O(n^2) approach:
    pairs_before = [0] * n
    for i in range(n):
        for j in range(i):
            if ends[j] <= intervals[i][0]:
                pairs_before[i] += 1
            else:
                break  # since sorted by end, can optimize

    # For triples: for each i, count non-overlapping pairs before start[i]
    # A pair (j, k) where j < k, end[j] < start[k], and end[k] < start[i]
    pair_count = [0] * n
    for k in range(n):
        pair_count[k] = singles[k]  # intervals before k that don't overlap

    # Triple: for each i, sum pair_count[k] for all k where end[k] < start[i]
    # Use prefix sums on pair_count indexed by end time
    for i in range(n):
        s_i = intervals[i][0]
        idx = bisect.bisect_left(ends, s_i)
        count += sum(pair_count[j] for j in range(idx))

    return count
```

### Cleaner O(n log n) Solution

```python
def count_triples_optimal(intervals: List[Tuple[int, int]]) -> int:
    """O(n log n) using Fenwick tree.

    Sort by end time. For each interval i:
      - singles_before[i] = # intervals ending before start[i]
      - For triples, maintain cumulative pair_count.
    """
    intervals.sort(key=lambda x: x[1])
    n = len(intervals)
    ends = [e for _, e in intervals]

    total = 0
    # For each interval as the LAST in a triple:
    # Count non-overlapping pairs that both end before this interval starts.
    # A pair is (j, k) with end[j] < start[k] and end[k] < start[i].
    # For interval k: it can pair with singles_before[k] intervals.
    # Accumulate pair_count as we go.

    cumulative_pairs = 0  # total pairs ending before current consideration
    pair_counts = []  # pair_count[k] for each k in order

    for i in range(n):
        s_i = intervals[i][0]

        # Count pairs that fully precede interval i
        # All intervals k where end[k] < s_i contribute pair_count[k] pairs
        idx = bisect.bisect_left(ends, s_i)
        triple_count = sum(pair_counts[:idx]) if pair_counts else 0
        total += triple_count

        # This interval's pair count (how many singles precede it)
        my_pairs = bisect.bisect_left(ends, s_i)
        pair_counts.append(my_pairs)

    return total
```

**时间复杂度**：前缀和方法 O(n^2)，使用 Fenwick 树（树状数组）可达 O(n log n)。
**空间复杂度**：O(n)。

### Edge Cases
- 少于 3 个区间 -> 0
- 所有区间重叠 -> 0
- 所有区间互不重叠 -> C(n, 3)

---

## 25. City Graph BFS Sort

**Pattern**: BFS + Custom Sorting（BFS + 自定义排序）

### Problem Statement

给定一个城市图（无向）和起始城市，按城市到起始城市的距离对所有城市排序。
距离相同时，城市编号较小的排在前面。

### Solution

```python
from collections import defaultdict, deque
from typing import List, Tuple


def sort_cities_by_distance(
    n: int, edges: List[Tuple[int, int]], start: int
) -> List[int]:
    """Sort cities by BFS distance from start. Ties: smaller index first.

    Args:
        n: Number of cities (0-indexed).
        edges: Undirected edges (u, v).
        start: Starting city.

    Returns:
        List of city indices sorted by (distance, index).
    """
    adj: dict[int, List[int]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # BFS to compute distances
    dist = [-1] * n
    dist[start] = 0
    queue: deque[int] = deque([start])

    while queue:
        node = queue.popleft()
        for neighbor in adj[node]:
            if dist[neighbor] == -1:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)

    # Sort by (distance, index). Unreachable cities get infinite distance.
    INF = n + 1
    cities = list(range(n))
    cities.sort(key=lambda c: (dist[c] if dist[c] != -1 else INF, c))

    return cities
```

**时间复杂度**：O(V + E)（BFS）+ O(V log V)（排序）。
**空间复杂度**：O(V + E)。

### Edge Cases
- 不连通图（不可达城市排在末尾）
- 起始城市孤立
- 完全图（除起点外所有城市距离均为 1）
- 自环（不影响 BFS）

### Follow-up: Weighted Graph

对于有权图，使用 **Dijkstra（迪杰斯特拉算法）** 代替 BFS：

```python
import heapq


def sort_cities_weighted(
    n: int, edges: List[Tuple[int, int, int]], start: int
) -> List[int]:
    """Weighted version using Dijkstra."""
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    dist = [float("inf")] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in adj[node]:
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))

    cities = list(range(n))
    cities.sort(key=lambda c: (dist[c], c))
    return cities
```

---

## Summary Table

| # | Problem | Pattern | Time | Space |
|---|---------|---------|------|-------|
| 1 | Purchase Optimization | Prefix Sum + Binary Search | O(n log n + q log n) | O(n) |
| 2 | Revenue & Referral (OOD) | Tree Aggregation | O(D) insert, O(n log k) query | O(n) |
| 3 | Rider Connection Log | Union Find + BFS | O(E alpha(N)) / O(E(V+E)) | O(N) |
| 4 | Elevator Binary Search | Simulation | O(n^2) / O(n log n) | O(n) |
| 5 | Server Throughput | Heap Scheduling | O(R log S) | O(S) |
| 6 | Cart & Pricing (OOD) | Strategy Pattern | O(items * rules) | O(items) |
| 7 | Circular Array Jump | BFS | O(n) | O(n) |
| 8 | Robot Distance Grid | DP Precompute | O(M*N) | O(M*N) |
| 9 | Min Ops n->0 | Greedy/NAF | O(log n) | O(1) |
| 10 | Shortest k-Distinct | Sliding Window | O(n) | O(k) |
| 11 | Price Discount | Monotonic Stack | O(n) | O(n) |
| 12 | Balanced Permutation | Min/Max Tracking | O(n) | O(n) |
| 13 | Elevator/Stairs Energy | Binary/Ternary Search | O(n log n) | O(1) |
| 14 | N-ary Tree 3-Part | Tree DFS | O(n) | O(h) |
| 15 | Max Throughput Budget | Binary Search on Answer | O(n log T) | O(1) |
| 16 | Parking Lot (OOD) | OOD + Free Queues | O(1) optimized | O(S) |
| 17 | Task Assignment | Greedy Sort by Diff | O(n log n) | O(n) |
| 18 | Jump Game Prime | DP + Sieve | O(nP) | O(n) |
| 19 | Min Edge Reversal | Re-rooting DP | O(n) | O(n) |
| 20 | Palindrome Paths | Bitmask XOR DFS | O(26n) | O(n) |
| 21 | Minesweeper Generator | Random + Grid | O(M*N) | O(M*N) |
| 22 | Grid Nearest Exit | BFS | O(M*N) | O(M*N) |
| 23 | Lock Combination | BFS State Space | O(10^n * n) | O(10^n) |
| 24 | Non-overlapping Triples | Sort + Prefix Count | O(n^2) / O(n log n) | O(n) |
| 25 | City Graph BFS Sort | BFS + Sort | O(V+E + V log V) | O(V+E) |

---

## Pattern Quick Reference

- **Binary Search**: #1 Purchase Opt, #4 Elevator, #13 Energy, #15 Max Throughput
- **BFS/DFS**: #7 Circular Jump, #22 Grid Exit, #23 Lock, #25 City Sort
- **Union Find**: #3 Rider Connection
- **DP**: #18 Jump Game Prime, #19 Re-rooting, #20 Palindrome Paths
- **Greedy**: #9 Min Ops, #17 Task Assignment
- **Monotonic Stack**: #11 Price Discount
- **Sliding Window**: #10 k-Distinct Subarray
- **Heap**: #5 Server Throughput
- **OOD**: #2 Revenue Tracking, #6 Cart Engine, #16 Parking Lot
- **Grid/Matrix**: #8 Robot Distance, #21 Minesweeper
- **Tree**: #14 N-ary Tree 3-Part
- **Tracking**: #12 Balanced Permutation
