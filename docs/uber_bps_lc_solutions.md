# Uber BPS -- LC Problem Solutions

> All solutions include: approach explanation, clean Python code, time/space complexity,
> edge cases, and ALL follow-ups/variants reported in 1p3a interviews.
>
> Task: T-P0-242

---

## LC 230: Kth Smallest Element in a BST

**Pattern**: Tree / Inorder Traversal

### (a) Iterative Inorder

```python
def kthSmallest(root, k):
    """Iterative inorder traversal -- stop at kth element."""
    stack = []
    node = root
    count = 0
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.right
```
**Time**: O(H + k) where H = tree height. **Space**: O(H) for stack.

### (b) Recursive Inorder

```python
def kthSmallest(root, k):
    """Recursive inorder with early termination."""
    result = [None]
    count = [0]

    def inorder(node):
        if not node or result[0] is not None:
            return
        inorder(node.left)
        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return
        inorder(node.right)

    inorder(root)
    return result[0]
```
**Time**: O(H + k). **Space**: O(H) recursion stack.

### (c) VARIANT: Kth Largest

Reverse inorder (right -> root -> left):

```python
def kthLargest(root, k):
    """Reverse inorder: visit right subtree first."""
    stack = []
    node = root
    count = 0
    while stack or node:
        while node:
            stack.append(node)
            node = node.right  # go right first
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.left  # then left
```

### (d) FOLLOW-UP: O(1) Space -- Morris Traversal

```python
def kthSmallest_morris(root, k):
    """Morris inorder traversal -- O(1) space, O(n) time."""
    node = root
    count = 0
    while node:
        if not node.left:
            count += 1
            if count == k:
                return node.val
            node = node.right
        else:
            # Find inorder predecessor
            pred = node.left
            while pred.right and pred.right != node:
                pred = pred.right
            if not pred.right:
                # Thread: link predecessor to current
                pred.right = node
                node = node.left
            else:
                # Unthread: predecessor already linked
                pred.right = None
                count += 1
                if count == k:
                    return node.val
                node = node.right
```
**Time**: O(n). **Space**: O(1) -- temporarily modifies tree then restores.

### (e) FOLLOW-UP: Augmented BST (left_count/right_count)

If we can modify the tree structure, add `left_count` to each node:

```python
def kthSmallest_augmented(root, k):
    """O(H) lookup with augmented BST storing subtree sizes."""
    node = root
    while node:
        left_count = node.left_count if hasattr(node, 'left_count') else 0
        if k == left_count + 1:
            return node.val
        elif k <= left_count:
            node = node.left
        else:
            k -= left_count + 1
            node = node.right
```
**Time**: O(H). **Space**: O(1). Requires O(n) preprocessing to compute subtree sizes.

### (f) FOLLOW-UP: Flatten the Tree

Convert BST to sorted array via inorder, then index directly:

```python
def kthSmallest_flatten(root, k):
    """Flatten BST to sorted list, then O(1) index lookup."""
    vals = []
    def inorder(node):
        if node:
            inorder(node.left)
            vals.append(node.val)
            inorder(node.right)
    inorder(root)
    return vals[k - 1]
```
**Time**: O(n) preprocessing, O(1) per query. **Space**: O(n).

---

## LC 547: Number of Provinces

**Pattern**: Union Find / DFS

### Union Find

```python
def findCircleNum(isConnected):
    """Union Find with path compression and union by rank."""
    n = len(isConnected)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1

    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                union(i, j)

    return len(set(find(i) for i in range(n)))
```
**Time**: O(n^2 * alpha(n)). **Space**: O(n).

### DFS Alternative

```python
def findCircleNum_dfs(isConnected):
    n = len(isConnected)
    visited = [False] * n
    provinces = 0

    def dfs(city):
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

---

## LC 337: House Robber III

**Pattern**: Tree DP

```python
def rob(root):
    """Tree DP: each node returns (rob_this, skip_this)."""
    def dfs(node):
        if not node:
            return (0, 0)
        left = dfs(node.left)
        right = dfs(node.right)
        # Rob this node: can't rob children
        rob_this = node.val + left[1] + right[1]
        # Skip this node: take max of each child
        skip_this = max(left) + max(right)
        return (rob_this, skip_this)

    return max(dfs(root))
```
**Time**: O(n). **Space**: O(H) recursion stack.

---

## LC 1020: Number of Enclaves

**Pattern**: BFS from Border

```python
from collections import deque

def numEnclaves(grid):
    """BFS from all border land cells, then count remaining land."""
    m, n = len(grid), len(grid[0])
    q = deque()

    # Enqueue all border land cells
    for i in range(m):
        for j in range(n):
            if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j] == 1:
                q.append((i, j))
                grid[i][j] = 0  # mark visited

    # BFS to mark all reachable from border
    while q:
        x, y = q.popleft()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                grid[nx][ny] = 0
                q.append((nx, ny))

    # Count remaining land cells (enclaves)
    return sum(grid[i][j] for i in range(m) for j in range(n))
```
**Time**: O(m*n). **Space**: O(m*n) worst case for queue.

---

## LC 994: Rotting Oranges

**Pattern**: Multi-source BFS

```python
from collections import deque

def orangesRotting(grid):
    """Multi-source BFS from all initially rotten oranges."""
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while q:
        minutes += 1
        for _ in range(len(q)):
            x, y = q.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    q.append((nx, ny))
        if fresh == 0:
            return minutes

    return -1  # some fresh oranges unreachable
```
**Time**: O(m*n). **Space**: O(m*n).

---

## LC 23: Merge K Sorted Lists

**Pattern**: Heap

### Min-Heap Approach

```python
import heapq

def mergeKLists(lists):
    """Merge k sorted lists using a min-heap."""
    dummy = ListNode(0)
    curr = dummy
    heap = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst.val, i, lst))

    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```
**Time**: O(N log k) where N = total nodes, k = number of lists. **Space**: O(k).

### Divide and Conquer

```python
def mergeKLists_dc(lists):
    """Merge k lists by repeatedly merging pairs."""
    if not lists:
        return None

    def merge2(l1, l2):
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
            merged.append(merge2(l1, l2))
        lists = merged
    return lists[0]
```
**Time**: O(N log k). **Space**: O(1) extra (modifies in-place) + O(log k) recursion.

---

## LC 815: Bus Routes

**Pattern**: BFS on Route Graph

```python
from collections import defaultdict, deque

def numBusesToDestination(routes, source, target):
    """BFS on route graph: nodes are routes, edges connect shared stops."""
    if source == target:
        return 0

    # Map stop -> list of route indices
    stop_to_routes = defaultdict(set)
    for i, route in enumerate(routes):
        for stop in route:
            stop_to_routes[stop].add(i)

    # BFS: start from all routes containing source
    visited_routes = set()
    visited_stops = {source}
    q = deque()

    for route_idx in stop_to_routes[source]:
        visited_routes.add(route_idx)
        q.append((route_idx, 1))

    while q:
        route_idx, buses = q.popleft()
        for stop in routes[route_idx]:
            if stop == target:
                return buses
            if stop in visited_stops:
                continue
            visited_stops.add(stop)
            for next_route in stop_to_routes[stop]:
                if next_route not in visited_routes:
                    visited_routes.add(next_route)
                    q.append((next_route, buses + 1))

    return -1
```
**Time**: O(sum of route lengths). **Space**: O(sum of route lengths).

---

## LC 981: Time Based Key-Value Store

**Pattern**: Binary Search on Timestamps

```python
import bisect

class TimeMap:
    def __init__(self):
        self.store = {}  # key -> [(timestamp, value), ...]

    def set(self, key, value, timestamp):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        if key not in self.store:
            return ""
        entries = self.store[key]
        # Binary search for largest timestamp <= given timestamp
        idx = bisect.bisect_right(entries, (timestamp, chr(127))) - 1
        if idx < 0:
            return ""
        return entries[idx][1]
```
**Time**: set O(1), get O(log n). **Space**: O(n).

### Follow-ups

**1M+ requests/sec**: Shard by key hash across multiple machines. Each shard handles a subset of keys. Use consistent hashing for even distribution.

**Thread safety**: Use read-write locks per key. Multiple readers can access simultaneously, writers get exclusive access. Or use lock-free data structures (CAS-based append-only list).

**Amortized time complexity**: set is O(1) amortized (list append). get is O(log n) via binary search. If timestamps are always increasing (guaranteed by problem), the list is always sorted -- no extra sorting needed.

---

## LC 17: Letter Combinations of a Phone Number

**Pattern**: Backtracking

```python
def letterCombinations(digits):
    """Backtracking to generate all letter combinations."""
    if not digits:
        return []

    mapping = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = []

    def backtrack(idx, path):
        if idx == len(digits):
            result.append(''.join(path))
            return
        for char in mapping[digits[idx]]:
            path.append(char)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```
**Time**: O(4^n * n) where n = length of digits. **Space**: O(n) recursion depth.

### VARIANT: 10-digit Phone Number

Same algorithm, but output is much larger (up to 4^10 = ~1M combinations). May need iterative approach or generator for memory efficiency:

```python
def letterCombinations_iterative(digits):
    """Iterative BFS-style combination generation."""
    if not digits:
        return []
    mapping = {'2':'abc','3':'def','4':'ghi','5':'jkl',
               '6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    combos = ['']
    for digit in digits:
        combos = [prev + char for prev in combos for char in mapping[digit]]
    return combos
```

---

## LC 79: Word Search

**Pattern**: Backtracking / DFS

### Standard DFS

```python
def exist(board, word):
    """DFS backtracking on grid."""
    m, n = len(board), len(board[0])

    def dfs(i, j, k):
        if k == len(word):
            return True
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
            return False
        temp = board[i][j]
        board[i][j] = '#'  # mark visited
        for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
            if dfs(i+di, j+dj, k+1):
                return True
        board[i][j] = temp  # restore
        return False

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False
```
**Time**: O(m*n*3^L) where L = word length. **Space**: O(L).

### VARIANT: 8 Directions, Straight Line Only

```python
def exist_8dir_straight(board, word):
    """8 directions, must go in straight line (no turning).
    Much simpler -- O(R*C*8*L) enumeration, no backtracking."""
    m, n = len(board), len(board[0])
    L = len(word)
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    for i in range(m):
        for j in range(n):
            if board[i][j] != word[0]:
                continue
            for di, dj in directions:
                # Check if word fits in this direction
                ei, ej = i + di*(L-1), j + dj*(L-1)
                if ei < 0 or ei >= m or ej < 0 or ej >= n:
                    continue
                match = True
                for k in range(L):
                    if board[i+di*k][j+dj*k] != word[k]:
                        match = False
                        break
                if match:
                    return True
    return False
```
**Time**: O(R*C*8*L). **Space**: O(1).

---

## LC 977: Squares of a Sorted Array

**Pattern**: Two Pointers

```python
def sortedSquares(nums):
    """Two pointers from both ends -- largest absolute values at edges."""
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    pos = n - 1  # fill from the end

    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            result[pos] = nums[left] ** 2
            left += 1
        else:
            result[pos] = nums[right] ** 2
            right -= 1
        pos -= 1

    return result
```
**Time**: O(n). **Space**: O(n) for result.

---

## LC 987: Vertical Order Traversal of a Binary Tree

**Pattern**: BFS/DFS with Column Tracking

```python
from collections import defaultdict, deque

def verticalTraversal(root):
    """BFS with (row, col) tracking, sort by col -> row -> value."""
    if not root:
        return []

    col_map = defaultdict(list)
    q = deque([(root, 0, 0)])  # (node, row, col)

    while q:
        node, row, col = q.popleft()
        col_map[col].append((row, node.val))
        if node.left:
            q.append((node.left, row + 1, col - 1))
        if node.right:
            q.append((node.right, row + 1, col + 1))

    result = []
    for col in sorted(col_map):
        # Sort by row first, then by value
        col_map[col].sort()
        result.append([val for _, val in col_map[col]])

    return result
```
**Time**: O(n log n). **Space**: O(n).

---

## LC 1197: Minimum Knight Moves

**Pattern**: BFS

```python
from collections import deque

def minKnightMoves(x, y):
    """BFS from (0,0) to (|x|,|y|). Use symmetry to stay in quadrant I."""
    x, y = abs(x), abs(y)
    if x == 0 and y == 0:
        return 0

    visited = {(0, 0)}
    q = deque([(0, 0, 0)])
    moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

    while q:
        cx, cy, steps = q.popleft()
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) == (x, y):
                return steps + 1
            # Pruning: stay within reasonable bounds
            if (nx, ny) not in visited and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                visited.add((nx, ny))
                q.append((nx, ny, steps + 1))
```
**Time**: O(|x|*|y|) worst case. **Space**: O(|x|*|y|).

### VARIANT: Finite Board Size n

```python
def minKnightMoves_finite(n, x, y):
    """BFS on n x n board."""
    if x == 0 and y == 0:
        return 0
    visited = {(0, 0)}
    q = deque([(0, 0, 0)])
    moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    while q:
        cx, cy, steps = q.popleft()
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) == (x, y):
                return steps + 1
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny, steps + 1))
    return -1  # unreachable
```

---

## LC 1697: Checking Existence of Edge Length Limited Paths

**Pattern**: Offline Queries + Union Find

```python
def distanceLimitedPathsExist(n, edgeList, queries):
    """Sort edges and queries by weight/limit. Process offline with UF."""
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
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

    # Sort queries by limit, keep original index
    indexed_queries = sorted(enumerate(queries), key=lambda x: x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (a, b, limit) in indexed_queries:
        # Add all edges with weight < limit
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] < limit:
            u, v, w = edgeList[edge_idx]
            union(u, v)
            edge_idx += 1
        result[qi] = find(a) == find(b)

    return result
```
**Time**: O((E + Q) log(E + Q) + (E + Q) * alpha(n)). **Space**: O(n + Q).

### VARIANT: Edge Weight >= k

Change the condition: instead of `weight < limit`, use `weight >= limit`. Sort edges descending and queries descending:

```python
def pathsWithMinWeight(n, edgeList, queries):
    """All edges on path must have weight >= k."""
    parent = list(range(n))
    rank = [0] * n
    # ... same find/union ...

    edgeList.sort(key=lambda e: -e[2])  # descending by weight
    indexed_queries = sorted(enumerate(queries), key=lambda x: -x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (a, b, k) in indexed_queries:
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] >= k:
            u, v, w = edgeList[edge_idx]
            union(u, v)
            edge_idx += 1
        result[qi] = find(a) == find(b)

    return result
```

---

## LC 549: Binary Tree Longest Consecutive Sequence II

**Pattern**: Tree DP

```python
def longestConsecutive(root):
    """DFS tracking increasing and decreasing lengths per node."""
    max_len = [0]

    def dfs(node):
        """Returns (increasing_len, decreasing_len) through this node."""
        if not node:
            return (0, 0)

        inc = dec = 1  # at minimum, the node itself

        if node.left:
            li, ld = dfs(node.left)
            if node.left.val == node.val + 1:
                inc = max(inc, li + 1)
            if node.left.val == node.val - 1:
                dec = max(dec, ld + 1)

        if node.right:
            ri, rd = dfs(node.right)
            if node.right.val == node.val + 1:
                inc = max(inc, ri + 1)
            if node.right.val == node.val - 1:
                dec = max(dec, rd + 1)

        # Path through this node: inc + dec - 1 (don't double-count node)
        max_len[0] = max(max_len[0], inc + dec - 1)
        return (inc, dec)

    dfs(root)
    return max_len[0]
```
**Time**: O(n). **Space**: O(H).

---

## LC 2503: Maximum Number of Points From Grid Queries

**Pattern**: BFS + Sort Queries

```python
import heapq

def maxPoints(grid, queries):
    """Process queries in sorted order. BFS with min-heap for frontier."""
    m, n = len(grid), len(grid[0])

    # Sort queries with original indices
    sorted_q = sorted(enumerate(queries), key=lambda x: x[1])

    result = [0] * len(queries)
    visited = [[False] * n for _ in range(m)]
    heap = [(grid[0][0], 0, 0)]  # (value, row, col)
    visited[0][0] = True
    points = 0

    for qi, limit in sorted_q:
        # Expand BFS frontier: add all cells with value < limit
        while heap and heap[0][0] < limit:
            val, x, y = heapq.heappop(heap)
            points += 1
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and not visited[nx][ny]:
                    visited[nx][ny] = True
                    heapq.heappush(heap, (grid[nx][ny], nx, ny))
        result[qi] = points

    return result
```
**Time**: O(m*n*log(m*n) + Q*log(Q)). **Space**: O(m*n).

---

## LC 2858: Minimum Edge Reversals So Every Node Is Reachable

**Pattern**: Re-rooting DP

```python
from collections import defaultdict

def minEdgeReversals(n, edges):
    """Re-rooting DP: DFS from 0, then propagate to all nodes."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append((v, 0))  # original direction: cost 0
        graph[v].append((u, 1))  # reversed: cost 1

    dp = [0] * n

    # Step 1: DFS from node 0 to compute dp[0]
    def dfs(node, parent):
        cost = 0
        for neighbor, rev_cost in graph[node]:
            if neighbor != parent:
                cost += rev_cost + dfs(neighbor, node)
        return cost

    dp[0] = dfs(0, -1)

    # Step 2: Re-root to compute dp for all nodes
    def reroot(node, parent):
        for neighbor, rev_cost in graph[node]:
            if neighbor != parent:
                # Moving root from node to neighbor:
                # If edge node->neighbor was original (rev_cost=0): now need to reverse it (+1)
                # If edge was reversed (rev_cost=1): now it's in correct direction (-1)
                dp[neighbor] = dp[node] + (1 if rev_cost == 0 else -1)
                reroot(neighbor, node)

    reroot(0, -1)
    return dp
```
**Time**: O(n). **Space**: O(n).

**Note from 1p3a**: Must self-construct edges, watch for 1-indexed input. Return the node with minimum reversals or the full array depending on problem statement.

---

## LC 2791: Count Paths That Can Form a Palindrome in a Tree

**Pattern**: Bitmask XOR + DFS

```python
from collections import defaultdict

def countPalindromePaths(parent, s):
    """DFS with XOR bitmask prefix. Palindrome = at most 1 odd-count char."""
    n = len(parent)
    children = defaultdict(list)
    for i in range(1, n):
        children[parent[i]].append(i)

    # prefix[node] = XOR of character bitmasks from root to node
    prefix = [0] * n
    count = 0

    # Count pairs where prefix[u] XOR prefix[v] has at most 1 bit set
    freq = defaultdict(int)
    freq[0] = 1  # root's prefix is 0

    def dfs(node):
        nonlocal count
        for child in children[node]:
            bit = 1 << (ord(s[child]) - ord('a'))
            prefix[child] = prefix[node] ^ bit

            # Count paths ending at child:
            # Case 1: prefix[child] XOR prefix[ancestor] == 0 (all even)
            count += freq[prefix[child]]
            # Case 2: XOR has exactly 1 bit set
            for i in range(26):
                count += freq[prefix[child] ^ (1 << i)]

            freq[prefix[child]] += 1
            dfs(child)

    dfs(0)
    return count
```
**Time**: O(26n). **Space**: O(n).

**Key insight**: Path u->v has characters from root->u XOR root->v. Palindrome-formable means at most 1 character has odd count, i.e., XOR result has at most 1 bit set.

---

## LC 1696: Jump Game VI

**Pattern**: DP + Sliding Window Max (Deque)

```python
from collections import deque

def maxResult(nums, k):
    """DP with monotonic deque for sliding window maximum."""
    n = len(nums)
    dp = [0] * n
    dp[0] = nums[0]
    dq = deque([0])  # indices of dp values in decreasing order

    for i in range(1, n):
        # Remove elements outside window
        while dq and dq[0] < i - k:
            dq.popleft()

        dp[i] = nums[i] + dp[dq[0]]  # best reachable score

        # Maintain decreasing deque
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)

    return dp[-1]
```
**Time**: O(n). **Space**: O(k).

### VARIANT: Jump +1 or +Prime Ending in 3

```python
def jumpGamePrime(arr):
    """Jump +1 or +prime ending in 3 (3,13,23,...). Maximize score."""
    n = len(arr)

    # Precompute primes ending in 3 up to n
    def sieve_primes_ending_3(limit):
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [p for p in range(2, limit + 1) if is_prime[p] and p % 10 == 3]

    primes = sieve_primes_ending_3(n)
    jumps = [1] + primes  # can always jump +1, or +prime ending in 3

    dp = [float('-inf')] * n
    dp[0] = arr[0]

    for i in range(1, n):
        for jump in jumps:
            prev = i - jump
            if prev >= 0 and dp[prev] != float('-inf'):
                dp[i] = max(dp[i], dp[prev] + arr[i])

    return dp[-1] if dp[-1] != float('-inf') else -1
```
**Time**: O(n * P) where P = number of primes ending in 3 up to n. **Space**: O(n).

---

## Edge Cases & General Tips

### Common Edge Cases to Check
- Empty input / single element
- All elements the same
- Already sorted / reverse sorted
- Tree with only left or only right children
- Graph with disconnected components
- k = 0 or k = n

### Complexity Analysis Checklist
For every solution, state:
1. Time complexity with explanation of dominant operation
2. Space complexity distinguishing auxiliary from input space
3. Best/worst case if they differ significantly
