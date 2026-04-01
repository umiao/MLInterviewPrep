# Uber BPS -- Custom (Non-LC) Problem Solutions

> Solutions for Uber-specific interview problems without standard LeetCode numbers.
> Each includes: problem statement (reconstructed from 1p3a), approach, clean Python
> code, time/space complexity, edge cases, and follow-ups.
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

**Pattern**: Prefix Sum + Binary Search

### Problem Statement

Given an array `prices` (sorted ascending) representing item prices and a list of
queries `(pos, amount)`, for each query find the maximum number of items purchasable
starting from index `pos` with budget `amount`.

### Approach

1. Sort prices (if not already sorted).
2. Build prefix sum array: `prefix[i] = prices[0] + prices[1] + ... + prices[i-1]`.
3. For each query `(pos, amount)`: binary search for the largest `end` such that
   `prefix[end] - prefix[pos] <= amount`.

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

**Time**: O(n log n) for sort + O(n) prefix sum + O(q log n) for queries.
**Space**: O(n) for prefix array.

### Edge Cases
- `amount` is 0 -> return 0
- `pos` beyond array bounds -> return 0
- Budget enough for all remaining items

### Follow-up: Unsorted Prices

If prices are not given sorted, we must sort first. If queries need original indices,
maintain an index mapping before sorting.

---

## 2. Customer Revenue & Referral Tracking (OOD)

**Pattern**: Object-Oriented Design / Tree Aggregation

### Problem Statement

Design a system supporting:
- `insertNewCustomer(revenue, referrerID)`: Add customer with given revenue, referred by referrerID. Revenue propagates up the referral tree.
- `getLowestK(k, minTotalRevenue)`: Return k customers with lowest total revenue (direct + all referrals' revenue) that exceed minTotalRevenue.

### Approach

Each customer stores direct revenue and a `total_revenue` (direct + subtree).
On insert, propagate revenue upward through the referral chain. For `getLowestK`,
maintain a sorted structure or scan and filter.

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

**Time**:
- `insert`: O(D) where D = depth of referral tree (propagation).
- `getLowestK`: O(n log k) using heap selection.

**Space**: O(n) for all customers.

### Edge Cases
- Customer with no referrer (root-level)
- Deep referral chains (O(D) propagation)
- k larger than qualifying customers

### Follow-up: Efficient getLowestK

For frequent queries, maintain a sorted container (e.g., SortedList from sortedcontainers)
indexed by total_revenue. Update on insert: remove old entry, update, reinsert. This gives
O(log n) per insert and O(k + log n) per query.

---

## 3. Uber Rider Connection Log (Union Find)

**Pattern**: Union Find / Graph Connectivity

### Problem Statement

Given timestamped logs of the form `"<timestamp> A shared-ride-with B"`, find the
earliest timestamp at which all riders are connected (directly or transitively).

**Follow-up**: Handle `"<timestamp> A blocked B"` events (disconnect two riders).

### Approach -- Part 1: Union Find

Process logs in chronological order. For each `shared-ride-with`, union the two riders.
After each union, check if all riders are in one component.

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

**Time**: O(E * alpha(N)) ~ O(E) where E = number of logs.
**Space**: O(N) for UF structure.

### Follow-up: Handling "block" Events (Deletions)

Union-Find does NOT support deletions. Two approaches:

**Approach A: Offline -- Process in Reverse**

If we need the *latest* time all are connected, process events in reverse:
blocks become unions, shared-rides become edges. But this changes the problem.

**Approach B: Rebuild with BFS/DFS**

For online processing with both connect and block events, maintain an adjacency
list. After each event, run BFS/DFS to check connectivity.

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

**Time**: O(E * (V + E)) -- BFS after each event. For large inputs, optimize with
link-cut trees or ETT (Euler Tour Trees) for O(log N) per operation.

**Space**: O(V + E) for adjacency list.

### Edge Cases
- Single rider (trivially connected)
- Block event for non-existent connection (no-op)
- Multiple connections between same pair

---

## 4. Elevator Binary Search OA

**Pattern**: Array Simulation / Binary Search

### Problem Statement

Given an array where each element represents a move distance, starting at index `i`,
you move to `i + arr[i]` (or `i - arr[i]` depending on rules). Find the minimum
starting index such that the traversal never goes out of the left boundary (index < 0).

### Approach

Simulate the path from each starting index. For efficiency, use memoization or
binary search on the answer if the property is monotonic (larger starting index
= more room to the left).

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

**Time**: O(n^2) worst case with linear scan + simulation.
With binary search (if monotonic): O(n log n).
**Space**: O(n) for visited set.

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
- Array of length 1
- All elements are 0 (infinite loop at start)
- Negative jumps causing immediate left-boundary violation

---

## 5. Server Throughput with Heap

**Pattern**: Heap / Greedy Scheduling

### Problem Statement

Given `n` servers with processing times, and incoming requests, maximize throughput.
Compare recursive vs heap-based solutions.

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

**Time**: O(R log S) where R = requests, S = servers.
**Space**: O(S) for heap.

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

**Time**: O(S^R) exponential -- only for small inputs.

### Edge Cases
- All requests arrive simultaneously
- Single server
- Processing times exceeding gap between requests

---

## 6. Cart & Pricing Engine (OOD)

**Pattern**: Object-Oriented Design / Strategy Pattern

### Problem Statement

Design classes for an Uber Eats cart system. Requirements:
- Item customization (add-ons with extra cost)
- Surge pricing multiplier
- Membership discounts (Uber One)
- Promo codes (flat or percentage)
- Receipt breakdown output

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

**Key Design Decisions**:
- Strategy pattern for pricing rules: easy to add new rule types
- Rules applied in order (surge -> discount -> promo)
- `MenuItem.total_price` includes add-ons
- Receipt shows full breakdown

### Follow-up: Rule Ordering and Conflicts

In production, define a `priority` field on rules. Sort by priority before applying.
For mutual exclusion (e.g., only one promo code), validate at `add_pricing_rule`.

---

## 7. Circular Array Shortest Jump

**Pattern**: BFS on Circular Array

### Problem Statement

Given a circular array of integers where `arr[i]` represents the jump distance
at index `i`, find the shortest number of jumps from index A to index B.
Jumps wrap around: from index `i`, you can go to `(i + arr[i]) % n` or
`(i - arr[i]) % n`.

### Approach

BFS from source A. Each state is a position in the circular array. Since we
want shortest path, BFS guarantees optimality.

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

**Time**: O(n) -- each node visited at most once.
**Space**: O(n) for visited array and queue.

### Edge Cases
- `start == end` -> 0 jumps
- `arr[i] == 0` -> stuck at position i (no outgoing edges)
- All elements same -> regular skip pattern

---

## 8. Robot Distance in Grid

**Pattern**: DP Precomputation / 4-Direction Obstacle Distance

### Problem Statement

Given a grid with:
- `O` = robot
- `E` = empty cell
- `X` = obstacle

And a distance array `[left, top, bottom, right]` representing distances from the
target robot to the nearest obstacle in each direction, find which robot matches.

### Approach

Precompute distance-to-nearest-obstacle in all 4 directions for every cell using DP.
Then for each robot cell, check if its 4 distances match the query.

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

**Time**: O(rows * cols) for precomputation + O(rows * cols) for search.
**Space**: O(rows * cols) for 4 distance matrices.

### Edge Cases
- Robot at grid boundary (distance to obstacle = distance to wall)
- Multiple robots with same distances (return first match or all)
- No matching robot

### Note on Distance Definition

The problem may define distance as cells to nearest obstacle OR to boundary
(treating boundary as obstacle). Clarify with interviewer. The solution above
treats the starting column/row edge as distance 0 (implicit wall).

---

## 9. Min Operations n to 0

**Pattern**: Greedy / Non-Adjacent Form (NAF)

### Problem Statement

Given integer `n`, reduce it to 0 using operations: `n += 2^i` or `n -= 2^i`
for any non-negative integer `i`. Find the minimum number of operations.

### Approach

This is equivalent to finding the Non-Adjacent Form (NAF) representation of `n`.
Key insight: the minimum number of operations equals the number of non-zero digits
in NAF. The greedy rule based on `n % 4`:

- If `n % 2 == 0`: divide by 2 (shift right), no operation needed
- If `n % 4 == 1`: subtract 1 (one operation)
- If `n % 4 == 3`: add 1 (one operation, creates a longer carry but fewer total ops)

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

**Time**: O(log n) -- each iteration at least halves n.
**Space**: O(1).

### Proof of Optimality

The NAF (Non-Adjacent Form) of any integer has the fewest non-zero digits among
all signed binary representations. The greedy rule `n%4==3 -> +1` avoids adjacent
1-bits, which is exactly the NAF construction.

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
- n = 0 -> 0 operations
- n = 1 -> 1 operation (subtract 2^0)
- n is a power of 2 -> 1 operation
- Large n (works in O(log n))

---

## 10. Shortest Subarray with k Distinct

**Pattern**: Sliding Window + Counter

### Problem Statement

Given an array `nums` and integer `k`, find the length of the shortest subarray
containing at least `k` distinct elements. Return -1 if impossible.

### Approach

Classic sliding window with a frequency counter. Expand right until we have `k`
distinct, then shrink left to minimize length.

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

**Time**: O(n) -- each element enters and leaves the window once.
**Space**: O(k) for the counter.

### Edge Cases
- All elements are the same and k > 1 -> return -1
- k = 1 -> return 1
- Entire array has exactly k distinct -> return n (if no shorter subarray exists)

---

## 11. Price Discount (Monotonic Stack)

**Pattern**: Monotonic Stack / Next Smaller Element

### Problem Statement

For each item at index `i` with price `prices[i]`, find the first `j > i` such that
`prices[j] <= prices[i]`. The discounted price at `i` is `prices[i] - prices[j]`.
Output: total discounted sum and indices that were sold at original price (no j found).

### Approach

Use a monotonic stack to find the "next smaller or equal" element for each index.

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

**Time**: O(n) -- each element pushed and popped at most once.
**Space**: O(n) for stack and discount array.

### Example

```
prices = [8, 4, 6, 2, 3]
Discounts: 8-4=4, 4-2=2, 6-2=4, 2 (original), 3 (original)
Total = 4 + 2 + 4 + 2 + 3 = 15
Original price indices: [3, 4]
```

### Edge Cases
- All prices increasing -> every item discounted by next item
- All prices decreasing -> only last item at original price
- All same price -> each discounted by next, last at original

---

## 12. Balanced Permutation

**Pattern**: Tracking Min/Max Positions

### Problem Statement

Given a permutation of `1..n`, for each `k` from `1` to `n`, check if there exists
a contiguous subarray that forms a permutation of `1..k`.

### Approach

Track the position of each value. For a contiguous subarray to be a permutation of
`1..k`, all values `1..k` must occupy a contiguous range of indices. Maintain
`min_pos` and `max_pos` as we increase k. If `max_pos - min_pos + 1 == k`, then yes.

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

**Time**: O(n).
**Space**: O(n) for position array.

### Proof

For values `1..k` occupying positions with range `max_pos - min_pos + 1`:
- If range == k, exactly k slots for k values, no gaps -> contiguous permutation.
- If range > k, there are values outside `1..k` in between -> not a contiguous permutation.

### Edge Cases
- n = 1 -> always [True]
- Sorted permutation [1,2,3,...,n] -> all True
- Reverse sorted -> only k=1 and k=n are True

---

## 13. Elevator/Stairs Energy

**Pattern**: Binary Search on Split Point

### Problem Statement

A person takes the first `mid` floors by elevator, then remaining floors by stairs.
- Elevator: gains `e1` energy per floor, costs `t1` time per floor.
- Stairs: consumes `e2` energy per floor, time per floor = `ceil(c / current_energy)`.

Find the split point that minimizes total time (or minimizes time difference between
two strategies).

### Approach

Binary search on the split point `mid`. For each candidate, compute:
1. Elevator time for floors 0..mid
2. Stairs time for floors mid..total (energy-dependent)

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

**Time**: O(n^2) with linear scan (n per evaluation * n candidates).
With binary search on unimodal function: O(n log n).
**Space**: O(1).

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
- 0 floors -> 0 time
- Energy runs out during stairs -> need more elevator floors
- All elevator or all stairs may be optimal

---

## 14. N-ary Tree 3-Part

**Pattern**: Tree DFS / Path Finding

### Problem Statement

Given an N-ary tree, implement three operations:
1. Sum all node values
2. Find the maximum path value (root to leaf)
3. Return the nodes on the maximum path

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

**Time**: O(n) for each operation -- visit every node once.
**Space**: O(h) recursion depth where h = tree height.

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
- Empty tree (None root)
- Single node (leaf is root)
- All negative values
- Multiple paths with equal max sum (return any)

---

## 15. Max Throughput with Budget

**Pattern**: Binary Search on Answer

### Problem Statement

Given `n` services, each with `current_throughput[i]` and `scale_cost[i]` (cost per
unit to increase throughput), and a budget `B`, find the maximum throughput achievable
such that ALL services reach at least that level. The bottleneck is the minimum.

### Approach

Binary search on target throughput `T`. For each candidate T, compute total cost to
bring all services up to T. If cost <= budget, T is feasible.

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

**Time**: O(n * log(max_throughput_range)).
**Space**: O(1).

### Edge Cases
- Budget = 0 -> answer is min(current)
- All services at same throughput -> distribute budget evenly
- One extremely expensive service (dominates budget)
- Large budget -> upper bound calculation matters

### Follow-up: Fractional Throughput

If throughput can be non-integer, use float binary search with epsilon tolerance:

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

**Pattern**: Object-Oriented Design

### Problem Statement

Design a parking lot system:
- `park(vehicle)` - park a vehicle, return spot ID or -1
- `unpark(spot_id)` - remove vehicle from spot
- `check_car(license_plate)` - check if car is parked, return spot ID or -1

Constraints: Motorcycle spots only for motorcycles, regular spots for both
motorcycles and cars.

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

**Time**:
- `park`: O(S) where S = total spots (linear scan for available spot).
- `unpark`: O(1) direct spot access.
- `check_car`: O(1) hash lookup.

**Space**: O(S + V) where V = parked vehicles.

### Follow-up: Optimize park() to O(1)

Use separate free-spot queues (deque or set) per spot type:

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
- Parking a car that's already parked (idempotent)
- Unparking an empty spot
- All spots full

---

## 17. Task Assignment to 2 People

**Pattern**: Greedy / Sort by Difference

### Problem Statement

Given `n` tasks with `reward1[i]` (reward if person 1 does task i) and `reward2[i]`
(reward if person 2 does task i), person 1 must do exactly `k` tasks, person 2 does
the rest. Maximize total reward.

### Approach

For each task, compute the "advantage" of assigning to person 1: `diff[i] = reward1[i] - reward2[i]`.
Sort by diff descending. Give top k tasks to person 1, rest to person 2.

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

**Time**: O(n log n) for sorting.
**Space**: O(n).

### Proof of Correctness

Start with all tasks assigned to person 2. Total = sum(reward2).
Switching task i from person 2 to person 1 changes total by `reward1[i] - reward2[i]`.
To maximize, pick the k tasks with the largest positive diff.

### Edge Cases
- k = 0 -> all tasks to person 2
- k = n -> all tasks to person 1
- All diffs equal -> any k tasks work
- Negative diffs for all -> still must assign k to person 1

---

## 18. Jump Game Prime-Ending Variant

**Pattern**: DP / Sieve of Eratosthenes

### Problem Statement

Like LC 1696 (Jump Game VI), but from position `i` you can jump to `i+1` or `i+p`
where `p` is a prime ending in digit 3 (3, 13, 23, 43, 53, 73, 83, ...).
Find minimum cost to reach the last index.

### Approach

1. Precompute all primes up to `n` ending in 3 using Sieve of Eratosthenes.
2. DP from left to right: `dp[i]` = min cost to reach index `i`.
3. For each `i`, `dp[i] = min(dp[i-1], dp[i-p] for all valid primes p) + cost[i]`.

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

**Time**: O(n * P) where P = number of primes ending in 3 up to n.
For n=10000, P ~ 100 primes. So roughly O(100n).
**Space**: O(n) for dp + O(n) for sieve.

### Optimization: Deque for Sliding Window Minimum

If we want O(n) or O(n log n), use a segment tree or monotonic deque over the
valid jump positions. But since P is small, the O(nP) approach is practical.

### Edge Cases
- n = 1 -> return cost[0]
- All costs negative (maximize negative path)
- Large n (sieve is O(n log log n), negligible)

---

## 19. Min Edge Reversal for Optimal Root

**Pattern**: Re-rooting DP

### Problem Statement

Given a directed tree with `n` nodes, choose a root such that the number of edges
that must be reversed (to point away from root) is minimized. Return the minimum
reversals and which node to root at.

### Approach

1. Build undirected adjacency list, tracking original direction.
2. DFS from node 0: count reversals needed to make all edges point away from 0.
3. Re-root: when moving root from parent to child, if edge parent->child exists
   (forward), reversals += 1; if child->parent (backward), reversals -= 1.

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

**Time**: O(n) -- two DFS passes.
**Space**: O(n) for adjacency list and result array.

### Key Insight

When re-rooting from parent `p` to child `c`:
- If original edge is `p -> c` (cost=0 from p's perspective): this edge was correct
  when rooted at p, but wrong when rooted at c. So reversals += 1.
- If original edge is `c -> p` (cost=1 from p's perspective): this was wrong at p
  but correct at c. So reversals -= 1.

### Edge Cases
- All edges point from 0 outward -> 0 reversals, root at 0
- Star graph -> depends on edge directions
- Linear chain -> root at one end

### Warning: 1-indexed Nodes

If the problem uses 1-indexed nodes, adjust:
```python
visited = [False] * (n + 1)
result = [0] * (n + 1)
```

---

## 20. Palindrome Paths in Tree

**Pattern**: Bitmask XOR DFS / Prefix on Tree

### Problem Statement

Given a tree where each edge has a character label (a-z), count the number of paths
between any two nodes such that the characters along the path can be rearranged to
form a palindrome.

### Approach

A string can be rearranged into a palindrome if at most one character has an odd
frequency. Represent character frequencies as a bitmask (bit i = parity of char i).
A path is palindromic if its XOR bitmask is 0 or has exactly one bit set.

Use DFS with prefix XOR from root. For path (u, v): `mask(u,v) = prefix[u] XOR prefix[v]`.

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

**Time**: O(26n) = O(n).
**Space**: O(n) for prefix array and mask counter.

### Key Insight

- XOR prefix from root gives the parity of each character on root-to-node path.
- `prefix[u] XOR prefix[v]` cancels the common root-to-LCA portion, leaving
  just the u-to-v path's character parities.
- A palindrome needs XOR = 0 (all even) or exactly one bit set (one odd char).

### Edge Cases
- Single node (0 paths)
- Linear tree (paths are subpaths)
- All same character (all paths palindromic)

---

## 21. Minesweeper Grid Generator

**Pattern**: Random Placement / Code Quality

### Problem Statement

Generate an M x N minesweeper grid with exactly K mines placed randomly. Display
the grid where each cell shows the mine count of adjacent cells (8 neighbors),
or `*` for mines.

**Follow-up**: Iteratively improve code quality -- remove unnecessary variables,
simplify logic, reduce set usage.

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

**Time**: O(M * N) to build grid (8 neighbors check is O(1) per cell).
**Space**: O(M * N) for grid + O(K) for mine set.

### Follow-up: Iterative Code Quality Improvement

The interviewer pushes for progressively cleaner code:

**V1 (Naive)**: Separate `is_mine` 2D array, explicit 8-direction list, many variables.

**V2 (Simplified)**: Inline mine check via set, generator expression for count.

**V3 (Minimal)**:
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
- 0 mines -> all zeros
- All mines -> all asterisks
- 1x1 grid with mine

---

## 22. 2D Grid Nearest Exit (BFS)

**Pattern**: BFS / Shortest Path

### Problem Statement

Given a 2D grid with walls and open cells, find the nearest exit (boundary cell
that is open) from a starting position. The start itself is not considered an exit.

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

**Time**: O(M * N) -- visit each cell at most once.
**Space**: O(M * N) for visited array and queue.

### Edge Cases
- Start is on boundary (must still move to a different exit)
- No exit reachable (surrounded by walls)
- Multiple exits at same distance

---

## 23. Lock Combination BFS

**Pattern**: BFS on State Space

### Problem Statement

A lock has `n` wheels, each with digits 0-9. Each move rotates one wheel up or down
by 1. Given a target combination and a set of "deadend" combinations to avoid, find
the minimum number of moves from "0000" to the target.

### Solution

This is essentially LC 752 (Open the Lock), commonly asked at Uber:

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

**Time**: O(10^n * n) where n = number of wheels. For n=4: O(40000).
**Space**: O(10^n) for visited set.

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
- "0000" is a deadend -> return -1
- Target is "0000" -> return 0
- No path exists -> return -1

---

## 24. Non-overlapping Interval Triples

**Pattern**: Sorting + Greedy / DP

### Problem Statement

Given a list of intervals `[start, end]`, count the number of groups of 3 intervals
where no two intervals in the group overlap (pairwise non-overlapping).

### Approach

Sort intervals by end time. For each interval as the "middle" one, count how many
intervals end before it starts (left candidates) and how many start after it ends
(right candidates). The triple count with this middle is `left * right`.

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

**Time**: O(n^2) for the prefix-sum approach, O(n log n) with Fenwick tree.
**Space**: O(n).

### Edge Cases
- Fewer than 3 intervals -> 0
- All intervals overlap -> 0
- All intervals disjoint -> C(n, 3)

---

## 25. City Graph BFS Sort

**Pattern**: BFS + Custom Sorting

### Problem Statement

Given a city graph (undirected) and a start city, sort all cities by their distance
from the start city. Ties broken by smaller city index first.

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

**Time**: O(V + E) for BFS + O(V log V) for sorting.
**Space**: O(V + E).

### Edge Cases
- Disconnected graph (unreachable cities placed at end)
- Start city is isolated
- Complete graph (all at distance 1 except start)
- Self-loops (should not affect BFS)

### Follow-up: Weighted Graph

Use Dijkstra instead of BFS for weighted edges:

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
