"""Seed detailed LC solutions for all Uber-tagged problems into mle_prep.db.

Updates the `notes` field with comprehensive Python solutions including:
- Primary solution with explanation
- All variants and follow-ups from 1p3a interviews
- Time/space complexity analysis for each approach

Task: T-P0-242
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def build_solution_notes(lc_id: int, solution_md: str) -> str:
    """Wrap solution markdown with a header tag for identification."""
    return f"[Uber BPS Solution] LC {lc_id}\n\n{solution_md}"


# ── Solutions ──

SOLUTIONS: dict[int, str] = {}

# ────────────────────────────────────────────
# LC 230: Kth Smallest Element in a BST
# ────────────────────────────────────────────
SOLUTIONS[230] = r"""## Solutions for LC 230: Kth Smallest Element in a BST

### Approach 1: Iterative Inorder (Primary)

BST inorder traversal yields sorted order. Use a stack-based iterative
approach so we can stop as soon as we find the k-th element.

```python
def kthSmallest(root: TreeNode, k: int) -> int:
    stack = []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val
        curr = curr.right
```

- Time: O(H + k) where H = tree height
- Space: O(H) for stack

### Approach 2: Recursive Inorder

```python
def kthSmallest(root: TreeNode, k: int) -> int:
    self.count = 0
    self.result = 0

    def inorder(node: TreeNode) -> None:
        if not node or self.count >= k:
            return
        inorder(node.left)
        self.count += 1
        if self.count == k:
            self.result = node.val
            return
        inorder(node.right)

    inorder(root)
    return self.result
```

- Time: O(H + k)
- Space: O(H) recursion stack

### VARIANT: Kth Largest Element

Reverse the inorder traversal: visit right subtree first.

```python
def kthLargest(root: TreeNode, k: int) -> int:
    stack = []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.right  # go right first
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val
        curr = curr.left  # then left
```

- Time: O(H + k)
- Space: O(H)

### FOLLOW-UP: Morris Traversal (O(1) Space)

Thread the tree to avoid using a stack. Temporarily modify tree pointers
to create links back to parent, then restore.

```python
def kthSmallest_morris(root: TreeNode, k: int) -> int:
    curr = root
    while curr:
        if not curr.left:
            k -= 1
            if k == 0:
                return curr.val
            curr = curr.right
        else:
            # Find inorder predecessor
            pred = curr.left
            while pred.right and pred.right != curr:
                pred = pred.right
            if not pred.right:
                # Create thread
                pred.right = curr
                curr = curr.left
            else:
                # Remove thread, visit node
                pred.right = None
                k -= 1
                if k == 0:
                    return curr.val
                curr = curr.right
```

- Time: O(n) worst case (each edge traversed at most twice)
- Space: O(1) -- no stack, modifies and restores tree in-place

### FOLLOW-UP: Augmented BST (left_count per node)

Store `left_count` (size of left subtree) at each node. Enables O(H) lookup.

```python
class AugmentedNode:
    def __init__(self, val: int) -> None:
        self.val = val
        self.left = None
        self.right = None
        self.left_count = 0  # number of nodes in left subtree

def kthSmallest_augmented(root: AugmentedNode, k: int) -> int:
    curr = root
    while curr:
        if curr.left_count == k - 1:
            return curr.val
        elif curr.left_count >= k:
            curr = curr.left
        else:
            k -= curr.left_count + 1
            curr = curr.right
```

- Time: O(H) per query
- Space: O(1) per query (O(n) for maintaining counts)
- Update cost: O(H) per insert/delete (update counts along path)

### FOLLOW-UP: Flatten BST to Sorted Array

Convert BST to sorted array, then O(1) index lookup.

```python
def flatten_and_find(root: TreeNode, k: int) -> int:
    result = []

    def inorder(node: TreeNode) -> None:
        if node:
            inorder(node.left)
            result.append(node.val)
            inorder(node.right)

    inorder(root)
    return result[k - 1]
```

- Time: O(n) to flatten, O(1) per query
- Space: O(n) for the array
- Best when: many queries on a static tree

### Complexity Comparison

| Approach | Time (query) | Space | Best for |
|----------|-------------|-------|----------|
| Iterative inorder | O(H+k) | O(H) | Single query |
| Morris traversal | O(n) | O(1) | Memory-constrained |
| Augmented BST | O(H) | O(n) | Frequent queries + modifications |
| Flatten to array | O(1) query | O(n) | Many queries, static tree |
"""

# ────────────────────────────────────────────
# LC 547: Number of Provinces
# ────────────────────────────────────────────
SOLUTIONS[547] = r"""## Solutions for LC 547: Number of Provinces

### Approach 1: Union-Find

```python
def findCircleNum(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x: int, y: int) -> bool:
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    provinces = n
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                if union(i, j):
                    provinces -= 1
    return provinces
```

- Time: O(n^2 * alpha(n)) ~= O(n^2)
- Space: O(n)

### Approach 2: DFS

```python
def findCircleNum(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    visited = [False] * n
    provinces = 0

    def dfs(city: int) -> None:
        visited[city] = True
        for neighbor in range(n):
            if isConnected[city][neighbor] == 1 and not visited[neighbor]:
                dfs(neighbor)

    for i in range(n):
        if not visited[i]:
            dfs(i)
            provinces += 1
    return provinces
```

- Time: O(n^2)
- Space: O(n) recursion stack

### Approach 3: BFS

```python
from collections import deque

def findCircleNum(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    visited = [False] * n
    provinces = 0

    for i in range(n):
        if not visited[i]:
            queue = deque([i])
            visited[i] = True
            while queue:
                city = queue.popleft()
                for j in range(n):
                    if isConnected[city][j] == 1 and not visited[j]:
                        visited[j] = True
                        queue.append(j)
            provinces += 1
    return provinces
```

- Time: O(n^2)
- Space: O(n)
"""

# ────────────────────────────────────────────
# LC 337: House Robber III
# ────────────────────────────────────────────
SOLUTIONS[337] = r"""## Solutions for LC 337: House Robber III

### Approach: Tree DP with Rob/Not-Rob States

At each node, track two values:
- `rob`: max money if we rob this node
- `not_rob`: max money if we skip this node

```python
def rob(root: TreeNode) -> int:
    def dfs(node: TreeNode) -> tuple[int, int]:
        # Return (rob_this, skip_this) for the subtree.
        if not node:
            return (0, 0)

        left_rob, left_skip = dfs(node.left)
        right_rob, right_skip = dfs(node.right)

        # Rob this node: cannot rob children
        rob_this = node.val + left_skip + right_skip
        # Skip this node: take best of rob/skip for each child
        skip_this = max(left_rob, left_skip) + max(right_rob, right_skip)

        return (rob_this, skip_this)

    return max(dfs(root))
```

- Time: O(n) -- visit each node once
- Space: O(H) -- recursion stack depth

### Key Insight

The greedy "rob every other level" does NOT work because the tree is not
necessarily balanced. The DP approach correctly handles irregular tree shapes
by propagating optimal choices bottom-up.

### Why not memoization on node?

A naive recursive approach with memoization also works but is less clean:

```python
def rob(root: TreeNode) -> int:
    memo = {}

    def helper(node: TreeNode) -> int:
        if not node:
            return 0
        if node in memo:
            return memo[node]
        # Rob this node
        val = node.val
        if node.left:
            val += helper(node.left.left) + helper(node.left.right)
        if node.right:
            val += helper(node.right.left) + helper(node.right.right)
        # Skip this node
        memo[node] = max(val, helper(node.left) + helper(node.right))
        return memo[node]

    return helper(root)
```

- Time: O(n)
- Space: O(n) for memo dict + O(H) for recursion
- The tuple approach is preferred: cleaner, less space.
"""

# ────────────────────────────────────────────
# LC 1020: Number of Enclaves
# ────────────────────────────────────────────
SOLUTIONS[1020] = r"""## Solutions for LC 1020: Number of Enclaves

### Approach: BFS/DFS from Border

Any land cell connected to the border is NOT an enclave. Strategy:
1. Mark all border-connected land cells
2. Count remaining unmarked land cells

```python
from collections import deque

def numEnclaves(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def bfs(r: int, c: int) -> None:
        queue = deque([(r, c)])
        grid[r][c] = 0  # mark as visited by setting to 0
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 0
                    queue.append((nx, ny))

    # BFS from all border land cells
    for i in range(m):
        for j in range(n):
            if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j] == 1:
                bfs(i, j)

    # Count remaining land cells (enclaves)
    return sum(grid[i][j] for i in range(m) for j in range(n))
```

- Time: O(m * n)
- Space: O(m * n) for BFS queue in worst case

### DFS Alternative

```python
def numEnclaves(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] == 0:
            return
        grid[r][c] = 0
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc)

    for i in range(m):
        for j in range(n):
            if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j] == 1:
                dfs(i, j)

    return sum(grid[i][j] for i in range(m) for j in range(n))
```

- Time: O(m * n)
- Space: O(m * n) recursion stack worst case
- Note: May hit Python recursion limit on large grids; BFS preferred.
"""

# ────────────────────────────────────────────
# LC 994: Rotting Oranges
# ────────────────────────────────────────────
SOLUTIONS[994] = r"""## Solutions for LC 994: Rotting Oranges

### Approach: Multi-Source BFS

All rotten oranges spread simultaneously -- classic multi-source BFS.

```python
from collections import deque

def orangesRotting(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    # Initialize: find all rotten oranges and count fresh
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                queue.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while queue:
        minutes += 1
        for _ in range(len(queue)):
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    queue.append((nx, ny))
        if fresh == 0:
            return minutes

    return -1  # some fresh oranges unreachable
```

- Time: O(m * n)
- Space: O(m * n) for queue

### Key Points for Interview
- Must handle edge case: no fresh oranges -> return 0
- Must handle edge case: fresh oranges unreachable -> return -1
- BFS level = one minute of spreading
- Do NOT use DFS (DFS does not model simultaneous spreading)
"""

# ────────────────────────────────────────────
# LC 23: Merge k Sorted Lists
# ────────────────────────────────────────────
SOLUTIONS[23] = r"""## Solutions for LC 23: Merge k Sorted Lists

### Approach 1: Min-Heap

```python
import heapq

def mergeKLists(lists: list[ListNode]) -> ListNode:
    dummy = ListNode(0)
    curr = dummy
    heap = []

    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    while heap:
        val, idx, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next
```

- Time: O(N log k) where N = total nodes, k = number of lists
- Space: O(k) for heap
- Note: `idx` as tiebreaker prevents comparing ListNode objects

### Approach 2: Divide and Conquer

```python
def mergeKLists(lists: list[ListNode]) -> ListNode:
    if not lists:
        return None

    def merge_two(l1: ListNode, l2: ListNode) -> ListNode:
        dummy = ListNode(0)
        curr = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next
            curr = curr.next
        curr.next = l1 or l2
        return dummy.next

    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(l1, l2))
        lists = merged

    return lists[0]
```

- Time: O(N log k)
- Space: O(1) extra (O(log k) for recursion if recursive)

### Comparison
| Approach | Time | Space | Notes |
|----------|------|-------|-------|
| Heap | O(N log k) | O(k) | Simple, works well in practice |
| Divide & Conquer | O(N log k) | O(1) | Better space, merge-sort style |
"""

# ────────────────────────────────────────────
# LC 815: Bus Routes
# ────────────────────────────────────────────
SOLUTIONS[815] = r"""## Solutions for LC 815: Bus Routes

### Approach: BFS on Route Graph

Key insight: BFS on stops is too slow (too many stops). Instead, build a
graph of routes and BFS on routes.

```python
from collections import defaultdict, deque

def numBusesToDestination(
    routes: list[list[int]], source: int, target: int
) -> int:
    if source == target:
        return 0

    # Map: stop -> list of route indices
    stop_to_routes = defaultdict(set)
    for i, route in enumerate(routes):
        for stop in route:
            stop_to_routes[stop].add(i)

    # BFS on routes
    visited_routes = set()
    visited_stops = {source}
    queue = deque([(source, 0)])  # (stop, buses_taken)

    while queue:
        stop, buses = queue.popleft()
        for route_idx in stop_to_routes[stop]:
            if route_idx in visited_routes:
                continue
            visited_routes.add(route_idx)
            for next_stop in routes[route_idx]:
                if next_stop == target:
                    return buses + 1
                if next_stop not in visited_stops:
                    visited_stops.add(next_stop)
                    queue.append((next_stop, buses + 1))

    return -1
```

- Time: O(sum of all route lengths) for building graph + BFS
- Space: O(sum of all route lengths) for stop_to_routes map

### Key Interview Points
- Convert the stop-level problem to a route-level BFS
- Each "level" in BFS = taking one more bus
- Mark visited routes (not just stops) to avoid revisiting
- Edge case: source == target -> 0 buses needed
"""

# ────────────────────────────────────────────
# LC 981: Time Based Key-Value Store
# ────────────────────────────────────────────
SOLUTIONS[981] = r"""## Solutions for LC 981: Time Based Key-Value Store

### Primary Solution: HashMap + Binary Search

```python
from collections import defaultdict
import bisect

class TimeMap:
    def __init__(self) -> None:
        self.store: dict[str, list[tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        entries = self.store[key]
        # bisect_right finds insertion point; we want the entry just before
        idx = bisect.bisect_right(entries, (timestamp, chr(127))) - 1
        if idx < 0:
            return ""
        return entries[idx][1]
```

- set: O(1) amortized (timestamps are strictly increasing per problem)
- get: O(log n) where n = number of entries for that key
- Space: O(total number of set calls)

### Alternative get using manual binary search

```python
def get(self, key: str, timestamp: int) -> str:
    if key not in self.store:
        return ""
    entries = self.store[key]
    lo, hi = 0, len(entries) - 1
    result = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        if entries[mid][0] <= timestamp:
            result = entries[mid][1]
            lo = mid + 1
        else:
            hi = mid - 1
    return result
```

### FOLLOW-UP: Handle 1M+ Requests/Second

Strategies for high-throughput:
1. **Sharding by key**: Distribute keys across multiple nodes using
   consistent hashing. Each shard handles a subset of keys independently.
2. **Read replicas**: Since `set` is append-only and timestamps are
   increasing, replicas can serve `get` with eventual consistency.
3. **In-memory with periodic snapshots**: Keep everything in RAM,
   periodically snapshot to disk for durability.
4. **Batch writes**: Buffer `set` calls and flush in batches to reduce
   write amplification.

### FOLLOW-UP: Thread Safety

```python
import threading
from collections import defaultdict
import bisect

class ThreadSafeTimeMap:
    def __init__(self) -> None:
        self.store: dict[str, list[tuple[int, str]]] = defaultdict(list)
        self.locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    def set(self, key: str, value: str, timestamp: int) -> None:
        with self.locks[key]:
            self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        with self.locks[key]:
            entries = self.store[key]
            idx = bisect.bisect_right(entries, (timestamp, chr(127))) - 1
            return entries[idx][1] if idx >= 0 else ""
```

- Per-key locking: readers and writers for the same key are serialized,
  but different keys can be accessed concurrently.
- For higher concurrency: use `threading.RLock` or a read-write lock
  (multiple readers, single writer per key).

### FOLLOW-UP: Amortized Time Complexity Analysis

- `set`: O(1) amortized. Since timestamps are strictly increasing, we only
  append. Python list append is O(1) amortized (doubling strategy).
- `get`: O(log n) always. Binary search on sorted list of n entries.
- Space: O(N) total where N = total number of set calls across all keys.
"""

# ────────────────────────────────────────────
# LC 17: Letter Combinations of a Phone Number
# ────────────────────────────────────────────
SOLUTIONS[17] = r"""## Solutions for LC 17: Letter Combinations of a Phone Number

### Approach: Backtracking

```python
def letterCombinations(digits: str) -> list[str]:
    if not digits:
        return []

    phone_map = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }
    result = []

    def backtrack(idx: int, path: list[str]) -> None:
        if idx == len(digits):
            result.append("".join(path))
            return
        for ch in phone_map[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

- Time: O(4^n * n) where n = len(digits), 4 = max letters per digit
- Space: O(n) recursion depth + O(4^n * n) for output

### Iterative BFS Approach

```python
def letterCombinations(digits: str) -> list[str]:
    if not digits:
        return []

    phone_map = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }
    result = [""]
    for digit in digits:
        new_result = []
        for combo in result:
            for ch in phone_map[digit]:
                new_result.append(combo + ch)
        result = new_result
    return result
```

- Same complexity, iterative style

### VARIANT: 10-Digit Phone Number

Same algorithm, just larger scale. For 10 digits:
- Worst case (all 7s/9s): 4^10 = 1,048,576 combinations
- Average case (mix): ~3^10 = 59,049 combinations
- The backtracking approach handles this fine. No algorithmic change needed,
  just be aware of output size.

```python
# Same code works for any length:
result = letterCombinations("2345678901")  # handles 10 digits
```

- Key interview point: The algorithm is the same regardless of input length.
  The output grows exponentially, but the algorithm itself is optimal since
  we must enumerate all combinations.
"""

# ────────────────────────────────────────────
# LC 79: Word Search
# ────────────────────────────────────────────
SOLUTIONS[79] = r"""## Solutions for LC 79: Word Search

### Standard Approach: DFS/Backtracking (4 directions)

```python
def exist(board: list[list[str]], word: str) -> bool:
    m, n = len(board), len(board[0])

    def dfs(r: int, c: int, idx: int) -> bool:
        if idx == len(word):
            return True
        if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != word[idx]:
            return False
        ch = board[r][c]
        board[r][c] = "#"  # mark visited
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if dfs(r + dr, c + dc, idx + 1):
                return True
        board[r][c] = ch  # restore
        return False

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False
```

- Time: O(m * n * 4^L) where L = len(word)
- Space: O(L) recursion depth

### VARIANT: 8 Directions, Straight Line Only (No Turning)

From 1p3a: Search in 8 directions (including diagonals), but must go in a
straight line (no turning). This SIMPLIFIES the problem -- no backtracking needed!

For each starting cell and each of 8 directions, check if the word matches
along that line.

```python
def exist_straight_line(board: list[list[str]], word: str) -> bool:
    m, n = len(board), len(board[0])
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  # horizontal, vertical
        (1, 1), (1, -1), (-1, 1), (-1, -1),  # diagonals
    ]

    def check_direction(r: int, c: int, dr: int, dc: int) -> bool:
        for k in range(len(word)):
            nr, nc = r + dr * k, c + dc * k
            if nr < 0 or nr >= m or nc < 0 or nc >= n:
                return False
            if board[nr][nc] != word[k]:
                return False
        return True

    for i in range(m):
        for j in range(n):
            if board[i][j] == word[0]:
                for dr, dc in directions:
                    if check_direction(i, j, dr, dc):
                        return True
    return False
```

- Time: O(R * C * 8 * L) -- much simpler than DFS/backtracking
- Space: O(1) -- no recursion needed
- Key insight: "straight line, no turning" removes the need for backtracking
  entirely. It becomes a simple enumeration problem.
"""

# ────────────────────────────────────────────
# LC 987: Vertical Order Traversal of a Binary Tree
# ────────────────────────────────────────────
SOLUTIONS[987] = r"""## Solutions for LC 987: Vertical Order Traversal

### Approach: BFS with Column + Row Tracking

```python
from collections import defaultdict, deque

def verticalTraversal(root: TreeNode) -> list[list[int]]:
    # (col, row, val) tuples
    nodes = []

    queue = deque([(root, 0, 0)])  # (node, col, row)
    while queue:
        node, col, row = queue.popleft()
        nodes.append((col, row, node.val))
        if node.left:
            queue.append((node.left, col - 1, row + 1))
        if node.right:
            queue.append((node.right, col + 1, row + 1))

    # Sort by col, then row, then value
    nodes.sort()

    # Group by column
    result = []
    prev_col = None
    for col, row, val in nodes:
        if col != prev_col:
            result.append([])
            prev_col = col
        result[-1].append(val)

    return result
```

- Time: O(n log n) for sorting
- Space: O(n)

### DFS Alternative

```python
def verticalTraversal(root: TreeNode) -> list[list[int]]:
    nodes = []

    def dfs(node: TreeNode, col: int, row: int) -> None:
        if not node:
            return
        nodes.append((col, row, node.val))
        dfs(node.left, col - 1, row + 1)
        dfs(node.right, col + 1, row + 1)

    dfs(root, 0, 0)
    nodes.sort()

    result = []
    prev_col = None
    for col, row, val in nodes:
        if col != prev_col:
            result.append([])
            prev_col = col
        result[-1].append(val)
    return result
```

### Key Interview Points
- Sorting by (col, row, val) handles the "same position" tiebreaker rule
- This is different from LC 314 (Binary Tree Vertical Order Traversal) which
  does NOT sort by value at same position
"""

# ────────────────────────────────────────────
# LC 1197: Minimum Knight Moves
# ────────────────────────────────────────────
SOLUTIONS[1197] = r"""## Solutions for LC 1197: Minimum Knight Moves

### Approach 1: BFS (Standard)

```python
from collections import deque

def minKnightMoves(x: int, y: int) -> int:
    # Exploit symmetry: move to first quadrant
    x, y = abs(x), abs(y)

    visited = set()
    visited.add((0, 0))
    queue = deque([(0, 0, 0)])  # (cx, cy, moves)

    moves_list = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ]

    while queue:
        cx, cy, moves = queue.popleft()
        if cx == x and cy == y:
            return moves
        for dx, dy in moves_list:
            nx, ny = cx + dx, cy + dy
            # Pruning: stay within reasonable bounds
            if (nx, ny) not in visited and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                visited.add((nx, ny))
                queue.append((nx, ny, moves + 1))

    return -1
```

- Time: O(|x| * |y|) with pruning
- Space: O(|x| * |y|)

### Approach 2: Bidirectional BFS (Faster)

```python
from collections import deque

def minKnightMoves(x: int, y: int) -> int:
    x, y = abs(x), abs(y)
    if x == 0 and y == 0:
        return 0

    moves_list = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ]

    src_visited = {(0, 0): 0}
    dst_visited = {(x, y): 0}
    src_queue = deque([(0, 0)])
    dst_queue = deque([(x, y)])

    while True:
        # Expand from source
        next_src = deque()
        while src_queue:
            cx, cy = src_queue.popleft()
            for dx, dy in moves_list:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in dst_visited:
                    return src_visited[(cx, cy)] + 1 + dst_visited[(nx, ny)]
                if (nx, ny) not in src_visited and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                    src_visited[(nx, ny)] = src_visited[(cx, cy)] + 1
                    next_src.append((nx, ny))
        src_queue = next_src

        # Expand from destination
        next_dst = deque()
        while dst_queue:
            cx, cy = dst_queue.popleft()
            for dx, dy in moves_list:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in src_visited:
                    return dst_visited[(cx, cy)] + 1 + src_visited[(nx, ny)]
                if (nx, ny) not in dst_visited and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                    dst_visited[(nx, ny)] = dst_visited[(cx, cy)] + 1
                    next_dst.append((nx, ny))
        dst_queue = next_dst
```

### VARIANT: Board Size is n (Bounded)

When board is n x n instead of infinite:
- Simpler: just standard BFS with bounds [0, n-1]
- No need for symmetry tricks or pruning heuristics

```python
def minKnightMoves_bounded(n: int, sx: int, sy: int, tx: int, ty: int) -> int:
    visited = set()
    visited.add((sx, sy))
    queue = deque([(sx, sy, 0)])
    moves_list = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2),
    ]
    while queue:
        cx, cy, dist = queue.popleft()
        if cx == tx and cy == ty:
            return dist
        for dx, dy in moves_list:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, dist + 1))
    return -1  # unreachable
```

- Time: O(n^2)
- Space: O(n^2)
"""

# ────────────────────────────────────────────
# LC 1697: Checking Existence of Edge Length Limited Paths
# ────────────────────────────────────────────
SOLUTIONS[1697] = r"""## Solutions for LC 1697: Checking Existence of Edge Length Limited Paths

### Approach: Offline Queries + Sorted Edges + Union-Find

Sort both edges by weight and queries by limit. Process queries in order of
increasing limit, adding edges that satisfy the constraint.

```python
def distanceLimitedPathsExist(
    n: int,
    edgeList: list[list[int]],
    queries: list[list[int]],
) -> list[bool]:
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1

    # Sort edges by weight
    edgeList.sort(key=lambda e: e[2])

    # Sort queries by limit, keeping original index
    sorted_queries = sorted(enumerate(queries), key=lambda x: x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (u, v, limit) in sorted_queries:
        # Add all edges with weight < limit
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] < limit:
            union(edgeList[edge_idx][0], edgeList[edge_idx][1])
            edge_idx += 1
        # Check if u and v are connected
        result[qi] = find(u) == find(v)

    return result
```

- Time: O(E log E + Q log Q + (E + Q) * alpha(n))
- Space: O(n + Q)

### VARIANT: Edge Weight >= k (Reversed Condition)

Instead of "all edges < limit", we want "path where all edges >= k".

Strategy: Sort edges in DECREASING order, sort queries by k in DECREASING
order. Add edges with weight >= k before checking connectivity.

```python
def pathsWithMinWeight(
    n: int,
    edgeList: list[list[int]],
    queries: list[list[int]],
) -> list[bool]:
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1

    # Sort edges by weight DESCENDING
    edgeList.sort(key=lambda e: -e[2])

    # Sort queries by k DESCENDING
    sorted_queries = sorted(enumerate(queries), key=lambda x: -x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (u, v, k) in sorted_queries:
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] >= k:
            union(edgeList[edge_idx][0], edgeList[edge_idx][1])
            edge_idx += 1
        result[qi] = find(u) == find(v)

    return result
```

### Key Interview Points
- "Offline" means we can reorder queries -- crucial for efficiency
- Sorting both edges and queries makes the Union-Find incremental
- Union-Find with path compression + union by rank -> near O(1) per op
"""

# ────────────────────────────────────────────
# LC 2858: Minimum Edge Reversals So Every Node Is Reachable
# ────────────────────────────────────────────
SOLUTIONS[2858] = r"""## Solutions for LC 2858: Minimum Edge Reversals So Every Node Is Reachable

### Approach: Re-Rooting DP

Step 1: Root at node 0, DFS to count reversals needed.
Step 2: Re-root to each other node using the relationship:
  - Moving root from parent to child: if edge is parent->child (forward),
    we need one more reversal; if child->parent (backward), one fewer.

```python
from collections import defaultdict

def minEdgeReversals(n: int, edges: list[list[int]]) -> list[int]:
    # Build adjacency list with direction info
    # adj[u] = [(v, cost)] where cost=0 if edge u->v exists, cost=1 if reversed
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append((v, 0))  # original direction: no reversal needed
        adj[v].append((u, 1))  # reverse direction: 1 reversal needed

    # Step 1: DFS from root 0 to count total reversals
    result = [0] * n

    def dfs(node: int, parent: int) -> int:
        total = 0
        for neighbor, cost in adj[node]:
            if neighbor != parent:
                total += cost + dfs(neighbor, node)
        return total

    result[0] = dfs(0, -1)

    # Step 2: Re-root DFS
    def reroot(node: int, parent: int) -> None:
        for neighbor, cost in adj[node]:
            if neighbor != parent:
                # Moving root from node to neighbor:
                # If cost=0 (edge node->neighbor), reversing costs +1
                # If cost=1 (edge neighbor->node, was reversed), saves -1
                result[neighbor] = result[node] + (1 if cost == 0 else -1)
                reroot(neighbor, node)

    reroot(0, -1)
    return result
```

- Time: O(n) -- two DFS passes
- Space: O(n) for adjacency list + recursion

### Key Interview Points (from 1p3a)
- **Must self-construct edges**: The input may be edge list, not adjacency
  list. Build the graph yourself.
- **Watch for 1-indexed**: Some test cases use 1-indexed nodes. Clarify
  with interviewer. If 1-indexed, either subtract 1 or use n+1 sized arrays.
- The re-rooting technique is the core insight: compute answer for one root,
  then derive all others in O(1) per node.

### Understanding the Re-Rooting Transition

When we move the root from node `u` to its child `v`:
- If original edge is u->v (cost=0 from u's perspective):
  Now v is root, so we need v->u direction, meaning we must reverse u->v.
  That's +1 reversal compared to u's answer.
- If original edge is v->u (cost=1 from u's perspective, meaning we had
  to reverse it when u was root):
  Now v is root, v->u is the natural direction, so we save that reversal.
  That's -1 compared to u's answer.
"""

# ────────────────────────────────────────────
# LC 2791: Count Paths That Can Form a Palindrome in a Tree
# ────────────────────────────────────────────
SOLUTIONS[2791] = r"""## Solutions for LC 2791: Count Paths That Can Form a Palindrome in a Tree

### Approach: Bitmask XOR + DFS Prefix Counting

Key insight: A string can be rearranged into a palindrome iff at most one
character has odd frequency. We track character frequencies using a bitmask
(26 bits for a-z). XOR toggles bits: even count -> bit 0, odd count -> bit 1.

For a path from node u to node v (through LCA), the combined mask is
`mask[u] XOR mask[v]`. This path is palindrome-rearrangeable iff the XOR
result has at most 1 bit set.

```python
from collections import defaultdict

def countPalindromePaths(parent: list[int], s: str) -> int:
    n = len(parent)
    # Build tree
    children = defaultdict(list)
    for i in range(1, n):
        children[parent[i]].append(i)

    # mask_count[m] = number of nodes with prefix XOR mask = m
    mask_count = defaultdict(int)
    mask_count[0] = 1  # root has mask 0
    result = 0

    def dfs(node: int, mask: int) -> None:
        nonlocal result

        # Current node's mask
        if node > 0:  # root has no edge
            bit = 1 << (ord(s[node]) - ord("a"))
            mask ^= bit

        # Count paths ending at this node that form palindromes
        # Case 1: XOR of path = 0 (all even frequencies)
        result += mask_count[mask]

        # Case 2: XOR of path has exactly 1 bit set
        for i in range(26):
            result += mask_count[mask ^ (1 << i)]

        mask_count[mask] += 1

        for child in children[node]:
            dfs(child, mask)

    dfs(0, 0)
    return result
```

- Time: O(26 * n) = O(n)
- Space: O(n) for mask_count + recursion

### Detailed Explanation of Mask Logic

1. **Bitmask representation**: Each bit position (0-25) represents a letter
   (a-z). Bit is 1 if that letter appears an odd number of times on the
   path from root to this node.

2. **XOR property**: For path u->v through LCA:
   `path_mask = mask[u] XOR mask[v]`
   Because the root-to-LCA portion cancels out in XOR.

3. **Palindrome condition**: path_mask must have 0 or 1 bits set.
   - 0 bits: all characters have even frequency -> perfect palindrome
   - 1 bit: one character has odd frequency -> palindrome with center char

4. **Counting**: For each node with mask `m`:
   - All previous nodes with mask `m` give XOR = 0 (Case 1)
   - All previous nodes with mask `m ^ (1<<i)` give XOR with 1 bit (Case 2)

### Iterative Version (Avoids Stack Overflow)

```python
def countPalindromePaths(parent: list[int], s: str) -> int:
    n = len(parent)
    children = defaultdict(list)
    for i in range(1, n):
        children[parent[i]].append(i)

    mask_count = defaultdict(int)
    mask_count[0] = 1
    result = 0

    # Compute masks using BFS
    from collections import deque
    masks = [0] * n
    queue = deque([0])
    visited = [False] * n
    visited[0] = True

    while queue:
        node = queue.popleft()
        for child in children[node]:
            if not visited[child]:
                visited[child] = True
                masks[child] = masks[node] ^ (1 << (ord(s[child]) - ord("a")))
                queue.append(child)

    # Count palindrome paths
    mask_count = defaultdict(int)
    for mask in masks:
        # Count matches with previous masks
        result += mask_count[mask]  # XOR = 0
        for i in range(26):
            result += mask_count[mask ^ (1 << i)]  # XOR has 1 bit
        mask_count[mask] += 1

    return result
```

- Same complexity, avoids Python recursion limit issues.
"""

# ────────────────────────────────────────────
# LC 2503: Maximum Number of Points From Grid Queries
# ────────────────────────────────────────────
SOLUTIONS[2503] = r"""## Solutions for LC 2503: Maximum Number of Points From Grid Queries

### Approach: Sort Queries + BFS with Min-Heap

Process queries in increasing order. Use a min-heap to expand reachable
cells greedily.

```python
import heapq

def maxPoints(grid: list[list[int]], queries: list[int]) -> list[int]:
    m, n = len(grid), len(grid[0])
    result = [0] * len(queries)

    # Sort queries while keeping original indices
    sorted_q = sorted(enumerate(queries), key=lambda x: x[1])

    # Min-heap: (cell_value, row, col)
    heap = [(grid[0][0], 0, 0)]
    visited = [[False] * n for _ in range(m)]
    visited[0][0] = True
    count = 0

    for qi, q_val in sorted_q:
        # Expand all cells with value < q_val
        while heap and heap[0][0] < q_val:
            val, r, c = heapq.heappop(heap)
            count += 1
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not visited[nr][nc]:
                    visited[nr][nc] = True
                    heapq.heappush(heap, (grid[nr][nc], nr, nc))
        result[qi] = count

    return result
```

- Time: O(m*n*log(m*n) + Q*log(Q))
- Space: O(m*n)

### VARIANT: Terrain Grid with Limits Array

Start at (0,0), can traverse cells with value < limit[i]. Same approach:

```python
def terrainTraversal(
    grid: list[list[int]], limits: list[int]
) -> list[int]:
    # Identical algorithm -- start BFS from (0,0),
    # expand cells < limit using sorted queries + min-heap
    return maxPoints(grid, limits)  # same logic
```

### Key Points
- The "sort queries" trick converts Q independent BFS runs into a single
  incremental expansion -- much more efficient.
- Min-heap ensures we always expand the smallest-valued frontier cell first.
- This is sometimes called "offline BFS" or "persistent BFS".
"""

# ────────────────────────────────────────────
# LC 549: Binary Tree Longest Consecutive Sequence II
# ────────────────────────────────────────────
SOLUTIONS[549] = r"""## Solutions for LC 549: Binary Tree Longest Consecutive Sequence II

### Approach: Tree DP Tracking Increasing/Decreasing Lengths

At each node, track the longest increasing and decreasing paths going
downward. A path through a node can combine the increasing path from one
subtree with the decreasing path from the other.

```python
def longestConsecutive(root: TreeNode) -> int:
    result = 0

    def dfs(node: TreeNode) -> tuple[int, int]:
        # Return (longest_increasing_down, longest_decreasing_down).
        nonlocal result
        if not node:
            return (0, 0)

        inc = 1  # increasing length ending at this node
        dec = 1  # decreasing length ending at this node

        if node.left:
            l_inc, l_dec = dfs(node.left)
            if node.left.val == node.val + 1:
                inc = max(inc, l_inc + 1)
            if node.left.val == node.val - 1:
                dec = max(dec, l_dec + 1)

        if node.right:
            r_inc, r_dec = dfs(node.right)
            if node.right.val == node.val + 1:
                inc = max(inc, r_inc + 1)
            if node.right.val == node.val - 1:
                dec = max(dec, r_dec + 1)

        # Path through this node: increasing on one side + decreasing on other
        result = max(result, inc + dec - 1)

        return (inc, dec)

    dfs(root)
    return result
```

- Time: O(n)
- Space: O(H) recursion depth

### Key Insight
- `inc + dec - 1` accounts for the node being counted once (it's the pivot
  of the path: increasing going one way, decreasing going the other).
- A path 3->4->5->4->3 has inc=3 (3,4,5) on one side and dec=3 (5,4,3) on
  the other side from node 5's perspective. But from node 4's perspective,
  considering both children, we might get inc=2 (4,5) + dec=2 (4,3) - 1 = 3.
- We update the global result at every node to capture the best path.
"""

# ────────────────────────────────────────────
# LC 977: Squares of a Sorted Array
# ────────────────────────────────────────────
SOLUTIONS[977] = r"""## Solutions for LC 977: Squares of a Sorted Array

### Approach: Two Pointers

The input is sorted. After squaring, the largest values are at the ends
(most negative or most positive). Use two pointers from both ends.

```python
def sortedSquares(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    pos = n - 1  # fill from the end

    while left <= right:
        l_sq = nums[left] ** 2
        r_sq = nums[right] ** 2
        if l_sq >= r_sq:
            result[pos] = l_sq
            left += 1
        else:
            result[pos] = r_sq
            right -= 1
        pos -= 1

    return result
```

- Time: O(n)
- Space: O(n) for output (O(1) extra if output doesn't count)

### Why Not Just Sort?

```python
def sortedSquares_naive(nums: list[int]) -> list[int]:
    return sorted(x * x for x in nums)
```

- Time: O(n log n) -- worse than two-pointer O(n)
- Works but suboptimal; interviewer expects the two-pointer approach.

### Key Interview Points
- The two-pointer insight: largest squares are at the extremes of sorted input
- Fill result array from the end (largest to smallest)
- Clean, simple code -- good warm-up problem
"""

# ────────────────────────────────────────────
# LC 1696: Jump Game VI
# ────────────────────────────────────────────
SOLUTIONS[1696] = r"""## Solutions for LC 1696: Jump Game VI

### Standard Approach: DP + Monotonic Deque

```python
from collections import deque

def maxResult(nums: list[int], k: int) -> int:
    n = len(nums)
    dp = [0] * n
    dp[0] = nums[0]
    dq = deque([0])  # indices, maintaining decreasing dp values

    for i in range(1, n):
        # Remove indices out of window
        while dq and dq[0] < i - k:
            dq.popleft()

        dp[i] = dp[dq[0]] + nums[i]

        # Maintain decreasing monotonic deque
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)

    return dp[n - 1]
```

- Time: O(n) -- each index enters/exits deque once
- Space: O(n) for dp array (can optimize to O(k))

### VARIANT: Jump +1 or +prime-ending-in-3 (3, 13, 23, ...)

From 1p3a: Instead of jumping 1..k, you can jump +1 or +p where p is a
prime ending in digit 3 (3, 13, 23, 43, 53, 73, 83, 103, ...).

```python
def maxResult_prime3(nums: list[int]) -> int:
    n = len(nums)

    # Precompute primes ending in 3 up to n using sieve
    def sieve_primes_ending_3(limit: int) -> list[int]:
        if limit < 2:
            return []
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, limit + 1, i):
                    is_prime[j] = False
        return [p for p in range(2, limit + 1) if is_prime[p] and p % 10 == 3]

    primes3 = sieve_primes_ending_3(n)

    # DP: dp[i] = max score reaching index i
    dp = [float("-inf")] * n
    dp[0] = nums[0]

    for i in range(n):
        if dp[i] == float("-inf"):
            continue
        # Jump +1
        if i + 1 < n:
            dp[i + 1] = max(dp[i + 1], dp[i] + nums[i + 1])
        # Jump +prime_ending_in_3
        for p in primes3:
            if i + p >= n:
                break
            dp[i + p] = max(dp[i + p], dp[i] + nums[i + p])

    return dp[n - 1]
```

- Time: O(n * |primes3|) where |primes3| = number of primes ending in 3 up to n
- Space: O(n)
- Note: For large n, the number of such primes is approximately n / (10 * ln(n))
  by the prime number theorem.

### Key Interview Points
- Standard Jump Game VI: monotonic deque is the key optimization over
  naive O(nk) DP
- The variant changes the jump set but keeps the DP structure. Without the
  sliding window property, we can't use a monotonic deque, so we iterate
  over allowed jumps at each position.
"""

# ────────────────────────────────────────────
# LC 337: already defined above
# LC 547: already defined above
# Add remaining problems
# ────────────────────────────────────────────

# ────────────────────────────────────────────
# Main update logic
# ────────────────────────────────────────────

def update_solutions() -> None:
    """Update notes field for each LC problem with solution content."""
    conn = get_connection()
    cursor = conn.cursor()

    updated = 0
    skipped = 0

    for lc_id, solution_md in SOLUTIONS.items():
        solution_tag = f"[Uber BPS Solution] LC {lc_id}"

        # Check current notes
        cursor.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = ?", (lc_id,)
        )
        row = cursor.fetchone()
        if not row:
            print(f"  [WARN] LC {lc_id} not found in DB, skipping")
            skipped += 1
            continue

        db_id = row["id"]
        current_notes = row["notes"] or ""

        if solution_tag in current_notes:
            print(f"  [SKIP] LC {lc_id} already has solution")
            skipped += 1
            continue

        # Append solution to existing notes
        full_solution = build_solution_notes(lc_id, solution_md.strip())
        if current_notes:
            new_notes = current_notes + "\n\n---\n\n" + full_solution
        else:
            new_notes = full_solution

        cursor.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (new_notes, db_id),
        )
        updated += 1
        print(f"  [OK] LC {lc_id} solution added (db_id={db_id})")

    conn.commit()
    conn.close()
    print(f"\nDone: {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    print("=== Seeding Uber BPS LC Solutions ===\n")
    update_solutions()
