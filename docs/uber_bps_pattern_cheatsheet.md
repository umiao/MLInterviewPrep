# Uber BPS -- Problem Pattern Cheat Sheet by Algorithm

> Quick-reference organized by algorithm pattern. Each section: when to recognize
> the pattern, the template approach, all Uber BPS problems using it, and complexity.
>
> Sources: `uber_bps_lc_solutions.md` (19 LC problems), `uber_bps_custom_solutions.md` (25 custom problems)
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

### When to recognize

- "Shortest path" in unweighted graph or grid
- "Minimum steps/moves" to reach target
- Spreading/infection from multiple sources simultaneously
- Layer-by-layer exploration (all cells at distance k)
- "Nearest exit" or "minimum distance to boundary"

### Template

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

For **multi-source BFS**, enqueue all sources at distance 0 before starting.

### Uber BPS Problems

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 994 Rotting Oranges | Multi-source BFS | All rotten oranges start simultaneously | O(mn) | O(mn) |
| LC 1020 Number of Enclaves | BFS from border | Flood-fill from border, count remaining | O(mn) | O(mn) |
| LC 1197 Min Knight Moves | BFS with pruning | Symmetry: work in quadrant I only | O(xy) | O(xy) |
| LC 815 Bus Routes | BFS on route graph | Nodes = routes, edges = shared stops | O(sum routes) | O(sum routes) |
| LC 2503 Max Grid Points | BFS + sorted queries | Process queries ascending, expand frontier | O(mn log mn) | O(mn) |
| Custom #7 Circular Jump | BFS on circular array | Modular arithmetic for wrap-around | O(n) | O(n) |
| Custom #22 Grid Nearest Exit | Standard grid BFS | Multi-source from all exits, find min | O(mn) | O(mn) |
| Custom #23 Lock Combination | BFS on state space | States = digit combos, 10^n space | O(10^n * n) | O(10^n) |
| Custom #25 City Graph BFS Sort | BFS + Dijkstra | Shortest path then sort by distance | O(V+E + V log V) | O(V+E) |

### Tips

- Grid BFS: 4-directional `[(0,1),(0,-1),(1,0),(-1,0)]`, check bounds inline.
- Multi-source: enqueue ALL sources first, then BFS -- gives correct min distances.
- If graph has weights, BFS won't work -- use Dijkstra (heap-based BFS).

---

## 2. DFS / Backtracking

### When to recognize

- "Generate all combinations/permutations"
- "Find if path exists" (existence, not shortest)
- "Word search in grid"
- "All valid configurations" with constraints
- Phone number letter combos, subset generation

### Template (Backtracking)

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 79 Word Search | Grid DFS + backtrack | Mark visited in-place with '#', restore | O(mn * 3^L) | O(L) |
| LC 79 variant: 8-dir straight | Linear scan, no backtrack | One direction per start -- much simpler | O(mn * 8 * L) | O(1) |
| LC 17 Letter Combos | Backtracking | Map digit -> chars, enumerate | O(4^n * n) | O(n) |

### Tips

- Mark-and-restore: modify grid in-place (`board[i][j] = '#'`), restore after DFS.
- Early termination: prune branches where partial solution can't lead to valid result.
- For "count" problems, return int instead of collecting all solutions.

---

## 3. Tree DP / Tree Traversal

### When to recognize

- "Maximum/minimum value achievable on tree paths"
- "Rob houses arranged as tree" (take/skip decisions)
- "Longest consecutive sequence in tree"
- "Kth smallest/largest in BST"
- "Vertical/level order traversal"
- Each node contributes to answer based on children's sub-answers

### Template (Tree DP)

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 230 Kth Smallest BST | Inorder traversal | Iterative inorder, stop at k | O(H+k) | O(H) |
| LC 230 variant: Kth Largest | Reverse inorder | Right -> root -> left | O(H+k) | O(H) |
| LC 230 follow-up: Morris | O(1) space traversal | Thread predecessor links | O(n) | O(1) |
| LC 230 follow-up: Augmented | Subtree size stored | O(H) lookup via left_count | O(H) | O(1) |
| LC 337 House Robber III | Tree DP (take/skip) | Each node returns (rob, skip) pair | O(n) | O(H) |
| LC 549 Longest Consecutive II | Tree DP (inc/dec) | Track increasing AND decreasing lengths | O(n) | O(H) |
| LC 987 Vertical Traversal | BFS + column tracking | Sort by (col, row, val) | O(n log n) | O(n) |
| Custom #14 N-ary Tree 3-Part | DFS subtree ops | Serialize, LCA, subtree sum on N-ary | O(n) | O(H) |

### Tips

- BST property: inorder = sorted. Use this for kth element problems.
- Tree DP signature: `dfs(node) -> tuple`. The tuple captures all states needed.
- "Path through node" = left contribution + right contribution + node value.
- Morris traversal: O(1) space but modifies/restores tree -- mention in interview.

---

## 4. Union Find (Disjoint Set)

### When to recognize

- "Number of connected components"
- "Are nodes in the same group?"
- "Merge groups over time" (online connectivity)
- "Process queries offline sorted by weight/limit"
- "Province/friend circle/island counting"

### Template

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 547 Number of Provinces | Basic UF or DFS | Count distinct roots | O(n^2 alpha(n)) | O(n) |
| LC 1697 Edge Length Limited | Offline queries + UF | Sort edges and queries by weight | O((E+Q) log) | O(n+Q) |
| LC 1697 variant: weight >= k | Reverse sort | Descending edge weights | O((E+Q) log) | O(n+Q) |
| Custom #3 Rider Connection | UF + BFS rebuild | UF for connect, BFS for block events | O(E alpha(N)) | O(N) |

### Tips

- **Offline query trick**: sort both edges and queries, sweep through together.
- Path compression + union by rank = nearly O(1) per operation (amortized).
- For "undo" operations (block/disconnect), UF doesn't support undo -- use BFS rebuild or offline reverse processing.
- Count components: `len(set(find(i) for i in range(n)))`.

---

## 5. Binary Search

### When to recognize

- "Minimum/maximum of some value" with monotonic feasibility
- "Search in sorted array" or "sorted + rotated"
- "Prefix sum + range query"
- "Binary search on the answer" (parametric search)
- "Find threshold/boundary"

### Template (Binary Search on Answer)

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 981 TimeMap | BS on timestamps | bisect_right on sorted timestamp list | O(log n) get | O(n) |
| LC 977 Squares Sorted (related) | Sorted input | Two pointers better than BS here | O(n) | O(n) |
| Custom #1 Purchase Optimization | Prefix sum + BS | Binary search on prefix sum for budget | O(n log n + q log n) | O(n) |
| Custom #4 Elevator BS | Simulation + BS | Binary search optimal floor | O(n log n) | O(n) |
| Custom #13 Elevator/Stairs Energy | Ternary/Binary search | Unimodal function -- ternary search | O(n log n) | O(1) |
| Custom #15 Max Throughput Budget | BS on answer | "Can we achieve throughput T with budget B?" | O(n log T) | O(1) |

### Tips

- **Prefix sum + binary search**: classic combo for "max items within budget."
- **Binary search on answer**: define `is_feasible(x)` and binary search for min/max x.
- **Ternary search**: for unimodal functions (one peak/valley).
- Always verify: does `lo` or `hi` give the answer? Off-by-one is the #1 BS bug.

---

## 6. Dynamic Programming

### When to recognize

- "Maximum/minimum score with choices at each step"
- "Number of ways to reach target"
- "Can I reach the end?" with variable jumps
- Overlapping subproblems + optimal substructure
- "Re-rooting" on trees (compute answer for every root)

### Template (Re-rooting DP)

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 1696 Jump Game VI | DP + monotonic deque | Sliding window max for O(n) DP transition | O(n) | O(k) |
| LC 1696 variant: prime jumps | DP + sieve | Precompute primes ending in 3 as jump sizes | O(n*P) | O(n) |
| LC 2858 Min Edge Reversals | Re-rooting DP | Compute root 0, propagate +1/-1 per edge | O(n) | O(n) |
| Custom #8 Robot Distance Grid | DP precompute | Precompute distances via DP on grid | O(mn) | O(mn) |
| Custom #18 Jump Game Prime | DP + sieve | Jump +1 or +prime-ending-3 | O(n*P) | O(n) |
| Custom #19 Min Edge Reversal | Re-rooting DP | Same as LC 2858 | O(n) | O(n) |
| Custom #24 Non-overlapping Triples | Sort + DP/prefix | Sort intervals, prefix count for non-overlap | O(n^2) | O(n) |

### Tips

- **Re-rooting DP**: two-pass (DFS for root 0, then propagate). Key: express dp[child] in terms of dp[parent] with O(1) transition.
- **Monotonic deque for DP**: when transition is `dp[i] = max(dp[j] for j in window) + cost`, use deque.
- **DP + sieve**: precompute primes once, use as jump table.
- Watch for 1-indexed inputs in edge reversal problems.

---

## 7. Greedy

### When to recognize

- "Minimum operations" with a clear locally-optimal choice
- "Assign tasks to minimize total cost"
- Sorting + greedy selection gives optimal
- Each choice is independent (no future regret)

### Uber BPS Problems

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| Custom #9 Min Ops n->0 | Greedy/NAF | Use largest power of negative Fibonacci / special moves | O(log n) | O(1) |
| Custom #17 Task Assignment | Sort by diff | Sort by cost_A - cost_B, split optimally | O(n log n) | O(n) |

### Tips

- **Exchange argument**: prove greedy is optimal by showing any swap worsens the result.
- **Sort by X - Y**: classic for 2-choice assignment (e.g., person A vs B cost difference).
- If greedy doesn't obviously work, it probably doesn't -- try DP instead.

---

## 8. Heap (Priority Queue)

### When to recognize

- "K largest/smallest elements"
- "Merge K sorted streams"
- "Schedule jobs to maximize throughput"
- "Process items by priority"
- Streaming data where you need running top-k or min/max

### Template

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 23 Merge K Sorted Lists | Min-heap of k heads | Pop min, push its next | O(N log k) | O(k) |
| LC 23 variant: divide & conquer | Pairwise merge | Merge pairs repeatedly | O(N log k) | O(1) |
| Custom #5 Server Throughput | Scheduling heap | Assign requests to earliest-free server | O(R log S) | O(S) |

### Tips

- Python `heapq` is min-heap only. For max-heap, negate values or use tuples `(-priority, item)`.
- For "merge K sorted" anything: heap of size K, pop-and-push pattern.
- For scheduling: heap of (end_time, server_id), pop earliest-free.

---

## 9. Sliding Window

### When to recognize

- "Shortest/longest subarray with property X"
- "At most K distinct elements"
- "Sum within range"
- Contiguous subarray/substring constraints
- "Window" keyword in problem

### Template

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| Custom #10 Shortest k-Distinct | Shrink when k distinct reached | Track char counts, shrink to find min length | O(n) | O(k) |
| LC 1696 (deque aspect) | Sliding window max | Monotonic deque maintains max in window | O(n) | O(k) |

### Tips

- **Two pointer invariant**: maintain window [left, right] where property holds.
- Expand right, shrink left. Update answer at each valid window.
- For "exactly K distinct", use `atMost(K) - atMost(K-1)` trick.

---

## 10. Monotonic Stack

### When to recognize

- "Next greater/smaller element"
- "Price discount: nearest future smaller price"
- "Stock span" problems
- "Largest rectangle in histogram" family
- Processing elements in order, maintaining increasing/decreasing property

### Template

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

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| Custom #11 Price Discount | Next smaller element | For each price, find nearest future discount | O(n) | O(n) |

### Tips

- Stack holds indices (not values) -- lets you compute distances and access values.
- **Increasing stack**: finds next smaller. **Decreasing stack**: finds next greater.
- Process left-to-right for "next" element, right-to-left for "previous" element.

---

## 11. Two Pointers

### When to recognize

- Sorted array operations (merge, deduplicate)
- "Squares of sorted array"
- "Container with most water" / "trapping rain water"
- Comparing from both ends inward

### Uber BPS Problems

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 977 Squares of Sorted Array | Two pointers from ends | Largest absolute values at edges | O(n) | O(n) |

### Tips

- When array is sorted and you need to produce sorted output of a transformation, consider two-pointer from both ends.
- Fill result array from the end (largest first) to avoid shifting.

---

## 12. Object-Oriented Design (OOD)

### When to recognize

- "Design a system" (parking lot, shopping cart, revenue tracker)
- "Implement a class with these operations"
- Interviewer asks about extensibility, SOLID principles
- Multiple entity types interacting

### Design Checklist

1. **Clarify requirements**: what operations? what scale?
2. **Identify entities**: nouns in the problem = classes
3. **Define interfaces**: what methods does each class expose?
4. **Choose patterns**: Strategy for interchangeable algorithms, Observer for events
5. **Optimize**: identify the O(1) operation that matters most

### Uber BPS Problems

| Problem | Design Pattern | Key Insight | Optimized Op |
|---------|---------------|-------------|--------------|
| Custom #2 Revenue & Referral | Tree aggregation | Referral tree with revenue rollup | O(D) insert |
| Custom #6 Cart & Pricing Engine | Strategy pattern | Surge/membership/promo as pluggable rules | O(items * rules) |
| Custom #16 Parking Lot | OOD + free queues | Min-heap or queue per size for O(1) park | O(1) park/unpark |

### Tips

- **Start simple**: basic classes first, then add patterns when interviewer asks "what if we need to add X?"
- **Strategy pattern**: when pricing/scoring rules vary. Each rule is a class implementing a common interface.
- **O(1) optimization**: for parking lot, maintain a free-spot queue per vehicle size.
- Always discuss trade-offs: "Strategy is more extensible but adds indirection."

---

## 13. Grid / Matrix

### When to recognize

- 2D board/map problems
- "Place mines", "count neighbors"
- Robot movement, distance computation
- Flood-fill, connected regions

### Uber BPS Problems

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| Custom #8 Robot Distance | DP on grid | Precompute all distances from source | O(mn) | O(mn) |
| Custom #21 Minesweeper | Random placement + count | Place mines randomly, compute neighbor counts | O(mn) | O(mn) |

### Tips

- 4-directional: `[(0,1),(0,-1),(1,0),(-1,0)]`. 8-directional: add diagonals.
- Bounds check: `0 <= nx < m and 0 <= ny < n`.
- In-place marking (`grid[i][j] = -1`) saves space but modifies input -- mention this.

---

## 14. Bitmask Techniques

### When to recognize

- "Palindrome-formable" (even/odd character counts)
- State tracking with boolean flags per character/element
- XOR for toggle/cancel operations
- Small alphabet (26 letters fits in 32-bit int)

### Uber BPS Problems

| Problem | Variant | Key Insight | Time | Space |
|---------|---------|-------------|------|-------|
| LC 2791 Palindrome Paths | XOR prefix bitmask | Path u->v palindromic if XOR has <= 1 bit set | O(26n) | O(n) |
| Custom #20 Palindrome Paths | Same technique | Bitmask of char parity along path | O(26n) | O(n) |

### Tips

- **XOR prefix**: `prefix[v] = prefix[parent] ^ (1 << char)`. Path u-v = `prefix[u] ^ prefix[v]`.
- **At most 1 bit set**: check `x == 0` or `x & (x-1) == 0`.
- **26-bit mask**: one bit per letter, track parity. XOR toggles parity.

---

## 15. Complexity Summary Table

### LC Problems

| LC # | Problem | Pattern | Time | Space |
|------|---------|---------|------|-------|
| 17 | Letter Combinations | Backtracking | O(4^n * n) | O(n) |
| 23 | Merge K Sorted Lists | Heap | O(N log k) | O(k) |
| 79 | Word Search | DFS Backtracking | O(mn * 3^L) | O(L) |
| 230 | Kth Smallest BST | Inorder Traversal | O(H + k) | O(H) |
| 337 | House Robber III | Tree DP | O(n) | O(H) |
| 547 | Number of Provinces | Union Find / DFS | O(n^2 alpha) | O(n) |
| 549 | Longest Consecutive II | Tree DP | O(n) | O(H) |
| 815 | Bus Routes | BFS on Routes | O(sum routes) | O(sum routes) |
| 977 | Squares Sorted Array | Two Pointers | O(n) | O(n) |
| 981 | Time Based KV Store | Binary Search | O(log n) get | O(n) |
| 987 | Vertical Traversal | BFS + Sort | O(n log n) | O(n) |
| 994 | Rotting Oranges | Multi-source BFS | O(mn) | O(mn) |
| 1020 | Number of Enclaves | BFS from Border | O(mn) | O(mn) |
| 1197 | Min Knight Moves | BFS | O(xy) | O(xy) |
| 1696 | Jump Game VI | DP + Mono Deque | O(n) | O(k) |
| 1697 | Edge Length Limited | UF + Offline Queries | O((E+Q) log) | O(n+Q) |
| 2503 | Max Grid Points | BFS + Sorted Queries | O(mn log mn) | O(mn) |
| 2791 | Palindrome Paths Tree | Bitmask XOR DFS | O(26n) | O(n) |
| 2858 | Min Edge Reversals | Re-rooting DP | O(n) | O(n) |

### Custom Problems

| # | Problem | Pattern | Time | Space |
|---|---------|---------|------|-------|
| 1 | Purchase Optimization | Prefix Sum + BS | O(n log n + q log n) | O(n) |
| 2 | Revenue & Referral | OOD / Tree | O(D) insert | O(n) |
| 3 | Rider Connection | Union Find + BFS | O(E alpha(N)) | O(N) |
| 4 | Elevator BS | Binary Search | O(n log n) | O(n) |
| 5 | Server Throughput | Heap Scheduling | O(R log S) | O(S) |
| 6 | Cart & Pricing | OOD Strategy | O(items * rules) | O(items) |
| 7 | Circular Jump | BFS | O(n) | O(n) |
| 8 | Robot Distance | Grid DP | O(mn) | O(mn) |
| 9 | Min Ops n->0 | Greedy | O(log n) | O(1) |
| 10 | k-Distinct Subarray | Sliding Window | O(n) | O(k) |
| 11 | Price Discount | Monotonic Stack | O(n) | O(n) |
| 12 | Balanced Permutation | Min/Max Tracking | O(n) | O(n) |
| 13 | Elevator/Stairs Energy | Ternary Search | O(n log n) | O(1) |
| 14 | N-ary Tree 3-Part | Tree DFS | O(n) | O(H) |
| 15 | Max Throughput Budget | BS on Answer | O(n log T) | O(1) |
| 16 | Parking Lot | OOD | O(1) park | O(S) |
| 17 | Task Assignment | Greedy Sort | O(n log n) | O(n) |
| 18 | Jump Game Prime | DP + Sieve | O(n*P) | O(n) |
| 19 | Min Edge Reversal | Re-rooting DP | O(n) | O(n) |
| 20 | Palindrome Paths | Bitmask XOR DFS | O(26n) | O(n) |
| 21 | Minesweeper | Grid Random | O(mn) | O(mn) |
| 22 | Grid Nearest Exit | BFS | O(mn) | O(mn) |
| 23 | Lock Combination | BFS State Space | O(10^n * n) | O(10^n) |
| 24 | Non-overlapping Triples | Sort + Prefix | O(n^2) | O(n) |
| 25 | City Graph Sort | BFS + Dijkstra | O(V+E + V log V) | O(V+E) |

---

## 16. Pattern Recognition Decision Tree

Use this flowchart to identify the right pattern from problem keywords:

```
Is it a DESIGN problem? (classes, entities, operations)
  YES -> OOD (#2, #6, #16)

Is it on a TREE?
  YES -> Is it BST with kth/search?
           YES -> Inorder traversal (LC 230)
         Is it "take or skip" at nodes?
           YES -> Tree DP (LC 337, LC 549)
         Is it "compute for ALL roots"?
           YES -> Re-rooting DP (LC 2858, #19)
         Is it "palindrome path"?
           YES -> Bitmask XOR (LC 2791, #20)
         Otherwise -> Tree DFS (#14)

Is it on a GRAPH?
  YES -> "Shortest path" unweighted?
           YES -> BFS (LC 994, LC 1197, #22, #23)
         "Connected components" or "same group"?
           YES -> Union Find (LC 547, LC 1697, #3)
         "Number of buses/transfers"?
           YES -> BFS on route graph (LC 815)

Is it on a GRID?
  YES -> "Shortest distance / nearest"?
           YES -> BFS (LC 1020, #22)
         "Find word / path exists"?
           YES -> DFS backtracking (LC 79)
         "Precompute distances"?
           YES -> Grid DP (#8)
         "Generate board"?
           YES -> Random + count (#21)

Is it an ARRAY problem?
  YES -> "Sorted + search/query"?
           YES -> Binary Search (LC 981, #1, #4, #15)
         "Subarray with K distinct / sum constraint"?
           YES -> Sliding Window (#10)
         "Next greater/smaller element"?
           YES -> Monotonic Stack (#11)
         "Maximum score with jumps"?
           YES -> DP (LC 1696, #18)
         "Sorted + transform"?
           YES -> Two Pointers (LC 977)
         "Assign to minimize cost"?
           YES -> Greedy sort (#17)
         "Merge K sorted"?
           YES -> Heap (LC 23)
         "Schedule requests"?
           YES -> Heap (#5)

Is it "generate all combinations"?
  YES -> Backtracking (LC 17)

Is it "minimize/maximize with feasibility check"?
  YES -> Binary Search on Answer (#13, #15)
```

### Quick Pattern Signals

| Signal in Problem | Pattern | Example |
|-------------------|---------|---------|
| "Shortest path", "minimum steps" | BFS | LC 994, LC 1197 |
| "Connected components", "same group" | Union Find | LC 547, LC 1697 |
| "Kth smallest/largest in BST" | Inorder traversal | LC 230 |
| "Rob/take or skip on tree" | Tree DP | LC 337 |
| "All roots optimal" | Re-rooting DP | LC 2858 |
| "Palindrome path + tree" | Bitmask XOR | LC 2791 |
| "Sorted + budget/range query" | Prefix sum + BS | Custom #1 |
| "Can we achieve X?" (monotonic) | BS on answer | Custom #15 |
| "Next smaller/greater" | Monotonic stack | Custom #11 |
| "K distinct in subarray" | Sliding window | Custom #10 |
| "Merge K sorted streams" | Heap | LC 23 |
| "Assign tasks, minimize cost" | Greedy sort by diff | Custom #17 |
| "Design parking/cart/tracker" | OOD | Custom #2, #6, #16 |
| "Generate all combos" | Backtracking | LC 17 |
| "Word in grid" | DFS + backtrack | LC 79 |
