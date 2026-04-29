# Uber BPS -- LC Problem Solutions

> 所有题解均包含：解题思路、简洁 Python 代码、时间/空间复杂度、边界情况，以及 1point3acres 面经中报告的所有追问变体。
>
> Task: T-P0-242

---

## [LC 230](lc://230): Kth Smallest Element in a BST

> **题目描述** [medium]: Given the root of a binary search tree, and an integer k, return the kth smallest value (1-indexed) of all the values of the nodes in the tree.
 
Example 1:


Input: root = [3,1,4,null,2], k = 1
Output: 1

Example 2:


Input: root = [5,3,6,2,4,null,null,1], k = 3
Output: 3

 
Constraints:

The number of nodes in the tree is n.
1 &lt;= k &lt;= n &lt;= 104
0 &lt;= Node.val &lt;= 104

 
Follow up: If
 
Example 1:

Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1-&gt;4-&gt;5,
  1-&gt;3-&gt;4,
  2-&gt;6
]
merging them into one sorted linked list:
1-&gt;1-&gt;2-&gt;3-&gt;4-&gt;4


**Pattern**: Tree / Inorder Traversal（树 / 中序遍历）

### (a) Iterative Inorder

**中序遍历 (Inorder Traversal)** 在 **BST (Binary Search Tree，二叉搜索树)** 中会按升序访问所有节点，因此第 k 个访问到的节点即为第 k 小元素。迭代版本使用显式栈模拟递归。

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
**Time**: O(H + k)，其中 H 为树高。**Space**: O(H)，栈空间。

### (b) Recursive Inorder

递归版本使用列表作为可变闭包变量传递计数和结果，并在找到第 k 个元素后提前终止。

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
**Time**: O(H + k)。**Space**: O(H) 递归栈空间。

### (c) VARIANT: Kth Largest

第 k 大变体使用反向中序遍历（右 -> 根 -> 左），将右子树优先访问：

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

**Morris 遍历 (Morris Traversal)** 通过临时修改树的指针来实现 O(1) 空间的中序遍历，遍历结束后完整恢复树的结构。

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
**Time**: O(n)。**Space**: O(1)——临时修改树后恢复原结构。

### (e) FOLLOW-UP: Augmented BST (left_count/right_count)

若可修改树结构，为每个节点添加 `left_count`（左子树节点数），可实现 O(H) 的查询：

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
**Time**: O(H)。**Space**: O(1)。需要 O(n) 的预处理来计算子树大小。

### (f) FOLLOW-UP: Flatten the Tree

将 BST 通过中序遍历展开为有序数组，再直接按下标查询：

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
**Time**: O(n) 预处理，O(1) 单次查询。**Space**: O(n)。

---

## [LC 547](lc://547): Number of Provinces

> **题目描述** [medium]: There are N students in a class. Some of them are friends, while some are not. Their
friendship is transitive in nature. For example, if A is a direct friend of B, and B
is a direct friend of C, then A is an indirect friend of C. And we defined a
friend circle is a group of students who are direct or indirect friends.

Given a N*N matrix M representing the friend relationship between students in
t


**Pattern**: Union Find / DFS（并查集 / 深度优先搜索）

### Union Find

**并查集 (Union Find，UF)** 使用路径压缩与按秩合并优化，将连通分量合并操作接近 O(1) 均摊时间。

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
**Time**: O(n^2 * alpha(n))，其中 alpha 为反阿克曼函数（实际近似常数）。**Space**: O(n)。

### DFS Alternative

**DFS (Depth-First Search，深度优先搜索)** 替代方案：标记已访问节点，每次从未访问节点出发遍历即为一个新省份。

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

## [LC 337](lc://337): House Robber III

> **题目描述** [medium]: The thief has found himself a new place for his thievery again. There is only one entrance to
this area, called the "root." Besides the root, each house has one and only one
parent house. After a tour, the smart thief realized that "all houses in this place
forms a binary tree". It will automatically contact the police if two directly-linked
houses were broken into on the same night.

Determine th


**Pattern**: Tree DP（树上动态规划）

**树形 DP (Tree DP，树上动态规划)** 的核心思路：每个节点返回两个状态的最优值——抢当前节点 vs 不抢当前节点，由此避免相邻节点被同时抢劫的非法情况。

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
**Time**: O(n)。**Space**: O(H) 递归栈空间。

---

## [LC 1020](lc://1020): Number of Enclaves

> **题目描述** [medium]: Given a 2D array `A`, each cell is 0 (representing sea) or 1 (representing land)

A move consists of walking from one land square 4-directionally to another land square, or
off the boundary of the grid.

Return the number of land squares in the grid for which we cannot walk off
the boundary of the grid in any number of moves.

Example 1:

Input: [[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]
Output: 3



**Pattern**: BFS from Border（从边界出发的广度优先搜索）

**BFS (Breadth-First Search，广度优先搜索)** 策略：先将所有与边界相连的陆地格子标记为已访问（即可逃脱），剩余的陆地格子即为"飞地"（enclave）。

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
**Time**: O(m*n)。**Space**: O(m*n) 队列最坏情况。

---

## [LC 994](lc://994): Rotting Oranges

> **题目描述** [medium]: You are given an m x n grid where each cell can have one of three values:

0 representing an empty cell,
1 representing a fresh orange, or
2 representing a rotten orange.

Every minute, any fresh orange that is 4-directionally adjacent to a rotten orange becomes rotten.
Return the minimum number of minutes that must elapse until no cell has a fresh orange. If this is impossible, return -1.
 
Examp


**Pattern**: Multi-source BFS（多源广度优先搜索）

多源 BFS 的关键：将所有初始腐烂橙子同时加入队列，模拟并行扩散过程。按轮次（分钟）扩展边界，每轮处理当前层所有节点。

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
**Time**: O(m*n)。**Space**: O(m*n)。

---

## [LC 23](lc://23): Merge K Sorted Lists

**Pattern**: Heap（堆）

### Min-Heap Approach

使用**最小堆 (Min-Heap，最小优先队列)** 维护 k 个链表的当前最小节点，每次弹出最小值后将其下一个节点压入堆中。

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
**Time**: O(N log k)，其中 N 为所有节点总数，k 为链表数量。**Space**: O(k)。

### Divide and Conquer

**分治法 (Divide and Conquer，分治)** 替代方案：每轮将链表两两配对合并，共 log k 轮，每轮合并总量为 O(N)。

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
**Time**: O(N log k)。**Space**: O(1) 额外空间（原地修改）+ O(log k) 递归栈。

---

## [LC 815](lc://815): Bus Routes

> **题目描述** [hard]: You are given an array routes where routes[i] is a bus route that the ith bus repeats forever. Return the least number of buses you must take to travel from source to target. Return -1 if it is not possible.

### **My Solution: BFS on Routes (有性能隐患)**

```python
class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0
        routeData = {i: set(route) for i, route in enumerate(routes)}
        queue = deque()
        visited = set()
        for i in routeData:
            if source in routeData[i]:
                queue.append(i)
                visited.add(i)
        if not queue:
            return -1
        ans = 1
        while queue:
            for _ in range(len(queue)):
                cur = queue.popleft()
                if target in routeData[cur]:
                    return ans
                for key in routeData:  # O(R) per route -- bottleneck!
                    if key not in visited and routeData[key] & routeData[cur]:
                        queue.append(key)
                        visited.add(key)
            ans += 1
        return -1
```
- **问题**: 内层遍历所有路线 O(R)，集合交集 O(S) -> 总 O(R^2 * S)，routes 多时 TLE

### **最优解: BFS on Stops + stop_to_routes 映射**

```python
from collections import deque, defaultdict

class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0
        stop_to_routes = defaultdict(set)
        for i, route in enumerate(routes):
            for stop in route:
                stop_to_routes[stop].add(i)

        visited_routes = set()
        visited_stops = set([source])
        queue = deque([source])
        buses = 0

        while queue:
            buses += 1
            for _ in range(len(queue)):
                stop = queue.popleft()
                for route_id in stop_to_routes[stop]:
                    if route_id in visited_routes:
                        continue
                    visited_routes.add(route_id)
                    for next_stop in routes[route_id]:
                        if next_stop == target:
                            return buses
                        if next_stop not in visited_stops:
                            visited_stops.add(next_stop)
                            queue.append(next_stop)
        return -1
```
- 时间: O(R * S)，空间: O(R * S)
- 关键: stop_to_routes 映射避免 O(R^2) 两两比较


## [LC 981](lc://981): Time Based Key-Value Store

> **题目描述** [medium]: Design a time-based key-value data structure that can store multiple values for the same key at different time stamps and retrieve the key&#39;s value at a certain timestamp.

Implement the TimeMap class:


	TimeMap() Initializes the object of the data structure.
	void set(String key, String value, int timestamp) Stores the key key with the value value at the given time timestamp.
...(truncated)


**Pattern**: Binary Search on Timestamps（在时间戳上的二分查找）

**二分查找 (Binary Search，BS)** 应用：每个 key 对应一个按时间戳有序排列的列表（由 set 操作保证单调递增），get 时用 `bisect_right` 找到最大的满足 `timestamp <= 给定值` 的条目。

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
**Time**: set O(1)，get O(log n)。**Space**: O(n)。

### Follow-ups

**每秒 100 万次以上请求**：按 key 哈希值分片到多台机器。每台机器负责一个 key 子集，使用**一致性哈希 (Consistent Hashing，一致哈希)** 实现均匀分布。

**线程安全**：对每个 key 使用读写锁（多读单写）。多个读操作可并发，写操作独占访问。或使用基于 CAS 的无锁追加列表。

**均摊时间复杂度**：set 的均摊时间为 O(1)（列表追加）。get 为 O(log n) 二分查找。题目保证时间戳单调递增，因此列表始终有序，无需额外排序。

---

## [LC 17](lc://17): Letter Combinations of a Phone Number

> **题目描述** [medium]: Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order.
A mapping of digits to letters (just like on the telephone buttons) is given below. Note that 1 does not map to any letters.

 
Example 1:

Input: digits = "23"
Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]

Example 2:

Input: digits


**Pattern**: Backtracking（回溯）

**回溯 (Backtracking)** 枚举所有可能的字母组合：对每个数字位，依次尝试对应的每个字母，递归到下一位，完成后撤销选择。

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
**Time**: O(4^n * n)，其中 n 为 digits 长度。**Space**: O(n) 递归深度。

### VARIANT: 10-digit Phone Number

算法不变，但输出规模大幅增加（最多 4^10 ≈ 100 万种组合）。可改用迭代方式或生成器以节省内存：

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

## [LC 79](lc://79): Word Search

> **题目描述** [medium]: Given an m x n grid of characters board and a string word, return true if word exists in the grid.
The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.
 
Example 1:


Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
Output:


**Pattern**: Backtracking / DFS（回溯 / 深度优先搜索）

### Standard DFS

在网格中搜索单词：对每个起始格子运行 DFS，标记已访问格子（防止重复使用），找到匹配后恢复原值（回溯）。

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
**Time**: O(m*n*3^L)，其中 L 为单词长度（每步有 3 个方向可选，因为不能回头）。**Space**: O(L)。

### VARIANT: 8 Directions, Straight Line Only

8 方向但必须走直线（不能转弯），无需回溯，直接枚举每个起点和方向即可：

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
**Time**: O(R*C*8*L)。**Space**: O(1)。

---

## [LC 977](lc://977): Squares of a Sorted Array

> **题目描述** [?]: Given an array of integers `A` sorted in non-decreasing order, return an
array of the squares of each number, also in sorted non-decreasing order.

Example 1:

Input: [-4,-1,0,3,10]
Output: [0,1,9,16,100]

Example 2:

Input: [-7,-3,2,3,11]
Output: [4,9,9,49,121]

Note:

- `1 <= A.length <= 10000`

- `-10000 <= A[i] <= 10000`

- `A` is sorted in non-decreasing order.


**Pattern**: Two Pointers（双指针）

**双指针 (Two Pointers)** 从数组两端向中间移动：绝对值最大的元素在两端，因此每次取两端绝对值较大者的平方，从结果数组末尾向前填充。

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
**Time**: O(n)。**Space**: O(n) 存储结果。

---

## [LC 987](lc://987): Vertical Order Traversal of a Binary Tree

> **题目描述** [hard]: Given a binary tree, return the vertical order traversal of its nodes values.

For each node at position `(X, Y)`, its left and right children respectively will
be at positions `(X-1, Y-1)` and `(X+1, Y-1)`.

Running a vertical line from `X = -infinity` to `X = +infinity`,
whenever the vertical line touches some nodes, we report the values of the nodes in order
from top to bottom (decreasing `Y` c


**Pattern**: BFS/DFS with Column Tracking（带列追踪的 BFS/DFS）

BFS 遍历时记录每个节点的 (行, 列) 坐标，按列分组后对每列内元素先按行、再按值排序。

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
**Time**: O(n log n)。**Space**: O(n)。

---

## [LC 1197](lc://1197): Minimum Knight Moves

> **题目描述** [medium]: In an infinite chess board with coordinates from `-infinity` to
`+infinity`, you have a knight at square `[0,
0]`.

A knight has 8 possible moves it can make, as illustrated below. Each move is two
squares in a cardinal direction, then one square in an orthogonal direction.

Return the minimum number of steps needed to move the knight to the square `[x,
y]`.  It is guaranteed the answer exists.

E


**Pattern**: BFS（广度优先搜索）

利用棋盘的对称性将目标映射到第一象限（取绝对值），减少搜索空间。BFS 保证找到的第一条到达目标的路径即为最短路径。

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
**Time**: O(|x|*|y|) 最坏情况。**Space**: O(|x|*|y|)。

### VARIANT: Finite Board Size n

棋盘大小有限（n x n），BFS 时需检查边界条件，无路可达时返回 -1：

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

## [LC 1697](lc://1697): Checking Existence of Edge Length Limited Paths

> **题目描述** [hard]: An undirected graph of `n` nodes is defined by `edgeList`,
where `edgeList[i] = [ui, vi, disi]` denotes
an edge between nodes `ui` and `vi` with
distance `disi`. Note that there may be multiple
edges between two nodes.

Given an array `queries`, where `queries[j] = [pj,
qj, limitj]`, your task is to determine for each `queries[j]`
whether there is a path between `pj` and
`qj` such that each edge o


**Pattern**: Offline Queries + Union Find（离线查询 + 并查集）

**离线查询 (Offline Queries)** 技巧：将所有边和查询按权重/限制排序后一起处理。对每个查询，只将权重严格小于限制的边加入并查集，再判断两端点是否连通。

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
**Time**: O((E + Q) log(E + Q) + (E + Q) * alpha(n))。**Space**: O(n + Q)。

### VARIANT: Edge Weight >= k

变体要求路径上所有边权重均不小于 k。将边和查询按权重降序排列，逐步加入满足条件的边：

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

## [LC 549](lc://549): Binary Tree Longest Consecutive Sequence II

> **题目描述** [medium]: Given a binary tree, you need to find the length of Longest Consecutive Path in Binary
Tree.

Especially, this path can be either increasing or decreasing. For example, [1,2,3,4] and
[4,3,2,1] are both considered valid, but the path [1,2,4,3] is not valid. On the other hand,
the path can be in the child-Parent-child order, where not necessarily be parent-child
order.

Example 1:

Input:
1
/ \
2   


**Pattern**: Tree DP（树上动态规划）

每个节点向上汇报两个值：以该节点为端点的最长递增序列长度和最长递减序列长度。过该节点的最长连续路径 = 递增长度 + 递减长度 - 1（节点本身不重复计数）。

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
**Time**: O(n)。**Space**: O(H)。

---

## [LC 2503](lc://2503): Maximum Number of Points From Grid Queries

> **题目描述** [hard]: Given an m x n integer matrix grid and an array queries. For each queries[i], start from the top left cell of the matrix and repeatedly visit cells of strictly less value. Return the maximum number of points achievable for each query.


**Pattern**: BFS + Sort Queries（BFS + 排序查询）

将查询按限制值排序，用**最小堆 (Min-Heap)** 维护 BFS 边界。对每个查询，将所有值严格小于限制的可达格子扩展进入已统计点数中，实现增量计算。

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
**Time**: O(m*n*log(m*n) + Q*log(Q))。**Space**: O(m*n)。

---

## [LC 2858](lc://2858): Minimum Edge Reversals So Every Node Is Reachable

> **题目描述** [hard]: Given a directed tree with n nodes rooted at node 0. Find the minimum number of edge reversals needed so that every node can reach node 0, for each possible root.


**Pattern**: Re-rooting DP（换根动态规划）

**换根 DP (Re-rooting DP)** 分两步：先以节点 0 为根做一次 DFS 得到 dp[0]，再通过第二次 DFS 将根从父节点"移动"到子节点，利用父节点的 dp 值 O(1) 推导子节点的 dp 值。

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
**Time**: O(n)。**Space**: O(n)。

**1point3acres 面经注意点**：需自行构建邻接表，注意输入可能是 1-indexed。根据题目要求，返回翻转次数最少的节点编号或整个 dp 数组。

---

## [LC 2791](lc://2791): Count Paths That Can Form a Palindrome in a Tree

> **题目描述** [hard]: Given a tree rooted at node 0 with n nodes. Each node has a character value. For each query node, count how many nodes v exist on the path from the query node to root such that the characters can be rearranged to form a palindrome.


**Pattern**: Bitmask XOR + DFS（位掩码异或 + 深度优先搜索）

**关键洞察**：路径 u->v 上的字符集等于从根到 u 的路径字符集 XOR 从根到 v 的路径字符集（公共前缀抵消）。路径可构成回文 = XOR 结果中最多有 1 个 bit 为 1（至多一个字符出现奇数次）。

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
**Time**: O(26n)。**Space**: O(n)。

**关键洞察**：路径 u->v 上的字符来自 root->u 的前缀异或 root->v 的前缀。可构成回文意味着至多 1 个字符出现奇数次，即 XOR 结果至多有 1 个 bit 为 1。

---

## [LC 1696](lc://1696): Jump Game VI

> **题目描述** [medium]: You are given a 0-indexed integer array `nums` and an
integer `k`.

You are initially standing at index `0`. In one move, you can jump at most
`k` steps forward without going outside the boundaries of the array. That
is, you can jump from index `i` to any index in the range `[i + 1,
min(n - 1, i + k)]` inclusive.

You want to reach the last index of the array (index `n - 1`). Your
score is the sum


**Pattern**: DP + Sliding Window Max (Deque)（动态规划 + 单调双端队列滑动窗口最大值）

**单调双端队列 (Monotonic Deque)** 维护大小为 k 的窗口内 dp 值的最大值：队列头部始终保存窗口内最大 dp 值的下标，新元素加入前从队尾弹出所有不大于它的元素。

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
**Time**: O(n)。**Space**: O(k)。

### VARIANT: Jump +1 or +Prime Ending in 3

变体：每步可跳 +1 或 +任意以 3 结尾的素数（3, 13, 23, ...）。先用筛法预计算所有满足条件的素数，再做 DP：

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
**Time**: O(n * P)，其中 P 为不超过 n 的以 3 结尾的素数个数。**Space**: O(n)。

---

## Edge Cases & General Tips

### Common Edge Cases to Check（常见边界情况检查）

- 空输入 / 单元素
- 所有元素相同
- 已有序 / 逆序排列
- 树只有左子树或只有右子树
- 图中存在不连通分量
- k = 0 或 k = n

### Complexity Analysis Checklist（复杂度分析清单）

对每个题解，务必说明：
1. 时间复杂度及主导操作的解释
2. 空间复杂度，区分辅助空间与输入空间
3. 若最好/最坏情况差异显著，分别说明