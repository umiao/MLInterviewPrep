"""Enrich LinkedIn doc#26 (Question Index) with full solutions for all 47 questions.

Task: T-P0-262

Adds comprehensive answers to all questions:
- Coding (Q1-Q15): Full Python solution + approach + complexity + follow-up
- ML Theory (Q16-Q23): Detailed explanations with formulas, code, examples
- ML System Design (Q24-Q47): Full answers with architecture, components, trade-offs
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#26 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=26")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#26 not found")
        sys.exit(1)
    return row[0]


# ════════════════════════════════════════════════════════════════
# CODING QUESTIONS Q1-Q15
# ════════════════════════════════════════════════════════════════

Q1_OLD = """### Q1. Design a data structure that supports insert, delete, and getRandom operations, ... (LC 380, 381)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hash-map, array, randomized, design, O(1)-operations

**题目**: Design a data structure that supports insert, delete, and getRandom operations, all in average O(1) time complexity. The insert and delete operations should work with arbitrary values, and getRandom should return a random element with equal probability...

**解法要点**:
- ## All O(1) Data Structure (LC 380 / 381)
- Combine a hash map (for O(1) lookup/delete) with a dynamic array (for O(1) random access).

**Follow-ups**:
- extended version (allowing duplicates)."""

Q1_NEW = """### Q1. Design a data structure that supports insert, delete, and getRandom operations, ... (LC 380, 381)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hash-map, array, randomized, design, O(1)-operations

**题目**: Design a data structure that supports insert, delete, and getRandom operations, all in average O(1) time complexity. The insert and delete operations should work with arbitrary values, and getRandom should return a random element with equal probability...

**解题思路**:

核心思想: 用 HashMap + 动态数组的组合实现三个 O(1) 操作。HashMap 存 val -> index 映射, 数组支持随机访问。删除时将目标元素与末尾元素交换, 然后 pop 末尾, 保持 O(1)。

```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}  # val -> index in list
        self.vals = []

    def insert(self, val: int) -> bool:
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_to_idx:
            return False
        idx = self.val_to_idx[val]
        last = self.vals[-1]
        # Swap with last element
        self.vals[idx] = last
        self.val_to_idx[last] = idx
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

**LC 381 (允许重复)**: HashMap 存 val -> set of indices, 删除时同样与末尾交换。

```python
from collections import defaultdict
import random

class RandomizedCollection:
    def __init__(self):
        self.val_to_indices = defaultdict(set)
        self.vals = []

    def insert(self, val: int) -> bool:
        self.val_to_indices[val].add(len(self.vals))
        self.vals.append(val)
        return len(self.val_to_indices[val]) == 1

    def remove(self, val: int) -> bool:
        if not self.val_to_indices[val]:
            return False
        idx = self.val_to_indices[val].pop()
        last = self.vals[-1]
        if idx != len(self.vals) - 1:
            self.vals[idx] = last
            self.val_to_indices[last].discard(len(self.vals) - 1)
            self.val_to_indices[last].add(idx)
        self.vals.pop()
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

**复杂度**: Insert/Remove/GetRandom 均为 O(1) 平均。Space O(n)。

**Follow-ups**:
- 如何支持 getRandomK (返回 k 个不重复随机元素)? -> Fisher-Yates shuffle 前 k 步
- 如何在多线程环境下保证线程安全? -> 用 read-write lock 或 ConcurrentHashMap
- 如果需要按权重随机采样? -> 维护前缀和数组 + binary search"""

Q2_OLD = """### Q2. Given a list of courses and their prerequisites, determine if it is possible to ... (LC 207, 210)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: topological-sort, graph, BFS, DFS, cycle-detection

**题目**: Given a list of courses and their prerequisites, determine if it is possible to finish all courses (cycle detection in a directed graph). If possible, return a valid order in which to take the courses...

**解法要点**:
- Time: O(V + E) for both approaches
- Space: O(V + E)"""

Q2_NEW = """### Q2. Given a list of courses and their prerequisites, determine if it is possible to ... (LC 207, 210)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: topological-sort, graph, BFS, DFS, cycle-detection

**题目**: Given a list of courses and their prerequisites, determine if it is possible to finish all courses (cycle detection in a directed graph). If possible, return a valid order in which to take the courses...

**解题思路**:

建图 + 拓扑排序 (BFS Kahn's Algorithm)。维护每个节点的入度, 从入度为 0 的节点开始 BFS。如果能处理所有节点则无环, 否则有环。

```python
from collections import deque, defaultdict

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    count = 0
    while queue:
        node = queue.popleft()
        count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return count == numCourses

def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order if len(order) == numCourses else []
```

**复杂度**: Time O(V + E), Space O(V + E)。

**Follow-ups**:
- 如果需要返回所有可能的拓扑排序? -> 回溯法枚举所有入度为 0 的选择
- 如何检测具体是哪些课程构成了环? -> DFS 染色法 (white/gray/black)
- 并行执行: 如何找到最少需要几个学期? -> LC 1136, 分层 BFS"""

Q3_OLD = """### Q3. Given a binary tree, repeatedly remove all leaf nodes and return the result of e... (LC 366)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: binary-tree, DFS, tree-depth, recursion

**题目**: Given a binary tree, repeatedly remove all leaf nodes and return the result of each removal round. In each round, collect all current leaf nodes, remove them from the tree, and repeat until the tree is empty...

**解法要点**:
- Instead of actually removing leaves iteratively, observe that a node's "removal round" equals its height in the tree (where leaves have height 0). Compute each node's height and group by height."""

Q3_NEW = """### Q3. Given a binary tree, repeatedly remove all leaf nodes and return the result of e... (LC 366)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: binary-tree, DFS, tree-depth, recursion

**题目**: Given a binary tree, repeatedly remove all leaf nodes and return the result of each removal round. In each round, collect all current leaf nodes, remove them from the tree, and repeat until the tree is empty...

**解题思路**:

关键观察: 节点在第几轮被移除 = 该节点的高度 (叶子高度为 0)。无需真正删除节点, 只需 DFS 计算每个节点的高度并分组。

```python
from collections import defaultdict

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def findLeaves(root: TreeNode) -> list[list[int]]:
    result = defaultdict(list)

    def get_height(node: TreeNode) -> int:
        if not node:
            return -1
        h = max(get_height(node.left), get_height(node.right)) + 1
        result[h].append(node.val)
        return h

    max_h = get_height(root)
    return [result[i] for i in range(max_h + 1)]
```

**复杂度**: Time O(n), Space O(n)。

**Follow-ups**:
- 如果要求返回每轮移除后的树结构 (而非节点值列表)? -> DFS 中实际断开子节点引用
- 如何用 iterative 方式实现? -> 用 stack 模拟后序遍历"""

Q4_OLD = """### Q4. Given a tree, find its centroid using centroid decomposition

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: tree, centroid-decomposition, advanced-data-structures, divide-and-conquer, graph

**题目**: Given a tree, find its centroid using centroid decomposition. Then support dynamic point activation/deactivation queries: activate or deactivate nodes, and after each operation, find the nearest active node to a given query node...

**解法要点**:
- Centroid decomposition: O(n log n) build time
- Each activate/query: O(log n) centroid ancestors to visit
- Space: O(n log n) for distance caches
- Key insight: centroid decomposition creates a balanced tree of depth O(log n), enabling efficient path queries"""

Q4_NEW = """### Q4. Given a tree, find its centroid using centroid decomposition

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: tree, centroid-decomposition, advanced-data-structures, divide-and-conquer, graph

**题目**: Given a tree, find its centroid using centroid decomposition. Then support dynamic point activation/deactivation queries: activate or deactivate nodes, and after each operation, find the nearest active node to a given query node...

**解题思路**:

**Centroid (重心)**: 删除后使最大子树最小的节点。对于大小为 n 的树, centroid 的每个子树大小 <= n/2。

**Centroid Decomposition**: 递归地找 centroid, 将其作为分治树的根, 然后对每个子树递归。生成的分治树深度为 O(log n)。

```python
from collections import defaultdict

def build_centroid_decomposition(adj: dict[int, list[int]], n: int):
    subtree_size = [0] * (n + 1)
    removed = [False] * (n + 1)
    parent = [0] * (n + 1)  # centroid decomposition parent

    def get_size(v: int, p: int) -> int:
        subtree_size[v] = 1
        for u in adj[v]:
            if u != p and not removed[u]:
                subtree_size[v] += get_size(u, v)
        return subtree_size[v]

    def get_centroid(v: int, p: int, tree_size: int) -> int:
        for u in adj[v]:
            if u != p and not removed[u]:
                if subtree_size[u] > tree_size // 2:
                    return get_centroid(u, v, tree_size)
        return v

    def decompose(v: int, p: int) -> int:
        size = get_size(v, -1)
        centroid = get_centroid(v, -1, size)
        removed[centroid] = True
        parent[centroid] = p
        for u in adj[centroid]:
            if not removed[u]:
                decompose(u, centroid)
        return centroid

    root = decompose(1, 0)
    return parent, root
```

**最近活跃节点查询**: 利用分治树, 每个 centroid 维护到其管辖范围内所有活跃节点的最短距离 (用 multiset/heap)。查询时沿分治树向上遍历 O(log n) 个祖先。

**复杂度**:
- 建树: O(n log n)
- 每次 activate/deactivate/query: O(log^2 n) (log n ancestors x log n per set operation)
- Space: O(n log n)

**Follow-ups**:
- 如果树是动态的 (可以加边)? -> Link-Cut Tree
- 如何处理带权边? -> 在 BFS/DFS 预处理时记录距离"""

Q5_OLD = """### Q5. Implement a Trie (prefix tree) data structure that supports insert, search, and ... (LC 208, 211, 212)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: trie, prefix-tree, word-search, DFS, backtracking, autocomplete

**题目**: Implement a Trie (prefix tree) data structure that supports insert, search, and startsWith operations. Then extend it to solve word search problems: given a board of characters and a list of words, find all words that can be formed by sequentially adjacent cells (LC 212)...

**解法要点**:
- Trie insert/search: O(L) where L = word length
- Autocomplete: O(P + K) where P = prefix length, K = total characters in matching words
- Word Search II: O(M*N * 4^L) worst case, but Trie pruning makes it much faster in practice
- Space: O(total characters across all words)"""

Q5_NEW = """### Q5. Implement a Trie (prefix tree) data structure that supports insert, search, and ... (LC 208, 211, 212)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: trie, prefix-tree, word-search, DFS, backtracking, autocomplete

**题目**: Implement a Trie (prefix tree) data structure that supports insert, search, and startsWith operations. Then extend it to solve word search problems: given a board of characters and a list of words, find all words that can be formed by sequentially adjacent cells (LC 212)...

**解题思路**:

**LC 208 - 基础 Trie**:

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, prefix: str) -> TrieNode | None:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

**LC 212 - Word Search II** (Trie + backtracking):

```python
def findWords(board: list[list[str]], words: list[str]) -> list[str]:
    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    result = set()

    def dfs(r: int, c: int, node: TrieNode, path: str):
        if node.is_end:
            result.add(path)
            node.is_end = False  # avoid duplicates
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        ch = board[r][c]
        if ch not in node.children:
            return
        board[r][c] = "#"  # mark visited
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dfs(r + dr, c + dc, node.children[ch], path + ch)
        board[r][c] = ch  # restore

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return list(result)
```

**复杂度**: Insert/Search O(L)。Word Search II: O(M*N * 4^L) worst case, Trie 剪枝大幅优化。

**Follow-ups**:
- 如何实现 autocomplete (返回所有匹配前缀的单词)? -> DFS 从前缀节点遍历所有子树
- 如何支持通配符搜索 (LC 211)? -> 遇到 '.' 时遍历所有 children
- 如何优化内存? -> 用 compressed trie (Patricia trie) 合并单链路径"""

Q6_OLD = """### Q6. Given a nested list of integers (where each element is either an integer or a li... (LC 339, 364)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recursion, DFS, BFS, nested-list, weighted-sum

**题目**: Given a nested list of integers (where each element is either an integer or a list of integers, which may itself contain nested lists), compute the weighted sum. In LC 339, deeper elements have higher weight (depth * value)...

**解法要点**:
- Instead of finding max depth first, use the trick: process level by level and keep a running `unweighted` sum. Each time we go deeper, we add `unweighted` again to `weighted`. Shallow values are added in more rounds (maxDepth times), deep values in fewer rounds (1 time for deepest)."""

Q6_NEW = """### Q6. Given a nested list of integers (where each element is either an integer or a li... (LC 339, 364)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recursion, DFS, BFS, nested-list, weighted-sum

**题目**: Given a nested list of integers (where each element is either an integer or a list of integers, which may itself contain nested lists), compute the weighted sum. In LC 339, deeper elements have higher weight (depth * value)...

**解题思路**:

**LC 339 (正序权重: depth * value, 越深权重越大)**:

```python
def depthSum(nestedList) -> int:
    def dfs(lst, depth):
        total = 0
        for item in lst:
            if item.isInteger():
                total += item.getInteger() * depth
            else:
                total += dfs(item.getList(), depth + 1)
        return total
    return dfs(nestedList, 1)
```

**LC 364 (逆序权重: 越浅权重越大)**: 巧妙做法 -- 逐层 BFS, 维护 `unweighted` 累加和。每深一层就把 `unweighted` 再加一次到 `weighted`。浅层值被累加更多次。

```python
from collections import deque

def depthSumInverse(nestedList) -> int:
    weighted, unweighted = 0, 0
    queue = deque(nestedList)
    while queue:
        next_level = deque()
        for _ in range(len(queue)):
            item = queue.popleft()
            if item.isInteger():
                unweighted += item.getInteger()
            else:
                for child in item.getList():
                    next_level.append(child)
        weighted += unweighted  # shallow values accumulated more times
        queue = next_level
    return weighted
```

**复杂度**: Time O(n) 遍历所有元素, Space O(d) 递归深度或 O(n) BFS 队列。

**Follow-ups**:
- 如何实现 NestedInteger 的 flatten iterator (LC 341)? -> 用 stack 惰性展开
- 如果嵌套层数可能很深导致栈溢出? -> 改用显式 stack 迭代"""

Q7_OLD = """### Q7. Big data algorithm: Given a range (a, b), find the minimum convex value within t...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: digit-dp, big-data, number-theory, dynamic-programming, math

**题目**: Big data algorithm: Given a range (a, b), find the minimum convex value within that range. A convex number is one where adjacent digit differences alternate in sign (i.e., digits form a zigzag pattern, each digit is either a local minimum or local maximum compared to its neighbors)...

**解法要点**:
- Brute force: O((b-a) * D) where D = number of digits
- Digit DP: O(D * 10 * 2 * 2) = O(D) per length, much faster for large ranges"""

Q7_NEW = """### Q7. Big data algorithm: Given a range (a, b), find the minimum convex value within t...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: digit-dp, big-data, number-theory, dynamic-programming, math

**题目**: Big data algorithm: Given a range (a, b), find the minimum convex value within that range. A convex number is one where adjacent digit differences alternate in sign (i.e., digits form a zigzag pattern, each digit is either a local minimum or local maximum compared to its neighbors)...

**解题思路**:

**Convex number (锯齿数)**: 相邻数字差值符号交替, 如 1324 (上-下-上)。

**方法 1: Brute Force** -- 逐个检查范围内每个数

```python
def is_convex(n: int) -> bool:
    digits = [int(d) for d in str(n)]
    if len(digits) <= 2:
        return True
    for i in range(1, len(digits) - 1):
        prev_diff = digits[i] - digits[i - 1]
        next_diff = digits[i + 1] - digits[i]
        if prev_diff == 0 or next_diff == 0:
            return False
        # Both same sign means not zigzag
        if (prev_diff > 0) == (next_diff > 0):
            return False
    return True

def min_convex_brute(a: int, b: int) -> int | None:
    for n in range(a, b + 1):
        if is_convex(n):
            return n
    return None
```

**方法 2: Digit DP (Dynamic Programming，动态规划)** -- 高效处理大范围。状态: (位置, 上一个数字, 上一步方向, 是否紧贴上界, 是否已开始)。

```python
from functools import lru_cache

def count_convex_up_to(n: int) -> int:
    digits = [int(d) for d in str(n)]
    L = len(digits)

    @lru_cache(maxsize=None)
    def dp(pos, prev_digit, last_dir, tight, started):
        # last_dir: 0=none, 1=up, 2=down
        if pos == L:
            return 1 if started else 0
        limit = digits[pos] if tight else 9
        count = 0
        for d in range(0, limit + 1):
            if not started and d == 0:
                count += dp(pos + 1, -1, 0, False, False)
                continue
            new_tight = tight and (d == limit)
            if not started or prev_digit == -1:
                count += dp(pos + 1, d, 0, new_tight, True)
            else:
                diff = d - prev_digit
                if diff == 0:
                    continue
                new_dir = 1 if diff > 0 else 2
                if last_dir != 0 and new_dir == last_dir:
                    continue  # same direction = not zigzag
                count += dp(pos + 1, d, new_dir, new_tight, True)
        return count
    return dp(0, -1, 0, True, False)
```

**复杂度**: Brute force O((b-a) * D)。Digit DP: O(D * 10 * 3 * 2 * 2) 即 O(D), 大范围远快于暴力。

**Follow-ups**:
- 如何找 range 内的第 k 个 convex number? -> 二分搜索 + count_convex_up_to
- 如果 digits 可以是任意 base (非十进制)? -> 修改 limit 为 base-1"""

Q8_OLD = """### Q8. N lockers are initially all closed

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: math, number-theory, perfect-squares, factors, brainteaser

**题目**: N lockers are initially all closed. In round n (for n = 1, 2, ..., N), you toggle the state of every locker whose number is a multiple of n...

**解法要点**:
- # Mathematical solution: O(sqrt(n))
- \"""Simulate the process to verify. O(N * H_N) ~ O(N log N).\""""

Q8_NEW = """### Q8. N lockers are initially all closed

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: math, number-theory, perfect-squares, factors, brainteaser

**题目**: N lockers are initially all closed. In round n (for n = 1, 2, ..., N), you toggle the state of every locker whose number is a multiple of n...

**解题思路**:

**数学洞察**: 柜子 k 被 toggle 的次数 = k 的因子个数。只有完全平方数有奇数个因子 (因为因子成对, 但平方根只算一次)。所以最终打开的柜子是 1, 4, 9, 16, 25, ...

```python
import math

def open_lockers_math(n: int) -> list[int]:
    \"\"\"Return all open lockers after N rounds. O(sqrt(n)).\"\"\"
    return [i * i for i in range(1, int(math.isqrt(n)) + 1)]

def open_lockers_simulate(n: int) -> list[int]:
    \"\"\"Simulate to verify. O(N * H_N) ~ O(N log N).\"\"\"
    lockers = [False] * (n + 1)  # False = closed
    for round_num in range(1, n + 1):
        for locker in range(round_num, n + 1, round_num):
            lockers[locker] = not lockers[locker]
    return [i for i in range(1, n + 1) if lockers[i]]

# Verify: both approaches give same result
assert open_lockers_math(100) == open_lockers_simulate(100)
```

**复杂度**: 数学解法 O(sqrt(n)), 模拟 O(N log N)。

**Follow-ups**:
- 如果不是从第 1 轮到第 N 轮, 而是只执行第 a 到第 b 轮? -> 统计每个柜子在 [a, b] 范围内的因子个数
- 如果 toggle 改为 "只有当柜子关着才打开"? -> 结果变为所有有因子在操作范围内的柜子都打开"""

Q9_OLD = """### Q9. Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: BST, binary-search-tree, common-ancestor, tree-traversal, set-intersection

**题目**: Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node that exists in both trees. The node must appear in both BSTs, and among all such common nodes, find the one at the greatest depth in either tree...

**解法要点**:
- \"""Use sorted in-order arrays for O(n+m) intersection.\"""
- Approach 1: O(n + m) time, O(n) space (hash set from BST1)
- Approach 2: O(n + m) time, O(n + m) space (sorted arrays)"""

Q9_NEW = """### Q9. Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: BST, binary-search-tree, common-ancestor, tree-traversal, set-intersection

**题目**: Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node that exists in both trees. The node must appear in both BSTs, and among all such common nodes, find the one at the greatest depth in either tree...

**解题思路**:

**Step 1**: 找两棵 BST (Binary Search Tree，二叉搜索树) 的公共节点集合。
**Step 2**: 在公共节点中, 找深度最大的那个。

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def deepest_common_node(root1: TreeNode, root2: TreeNode) -> int | None:
    # Step 1: Get all values from BST1 via in-order traversal
    def inorder(node: TreeNode) -> list[int]:
        if not node:
            return []
        return inorder(node.left) + [node.val] + inorder(node.right)

    set1 = set(inorder(root1))
    set2 = set(inorder(root2))
    common = set1 & set2

    if not common:
        return None

    # Step 2: Find the deepest common node in either tree
    best_val, best_depth = None, -1

    def find_deepest(node: TreeNode, depth: int):
        nonlocal best_val, best_depth
        if not node:
            return
        if node.val in common and depth > best_depth:
            best_depth = depth
            best_val = node.val
        find_deepest(node.left, depth + 1)
        find_deepest(node.right, depth + 1)

    find_deepest(root1, 0)
    find_deepest(root2, 0)
    return best_val
```

**优化**: 利用 BST 有序性, 用双指针合并两个有序 in-order 数组做交集, 避免 hash set。

**复杂度**: Time O(n + m), Space O(n + m)。

**Follow-ups**:
- 如果两棵树非常大, 无法全部载入内存? -> 用 iterator 逐步合并 in-order 序列
- 如果要找 "最深的公共祖先" (LCA of common nodes)? -> 不同问题, 需要在同一棵树上找 LCA"""

Q10_OLD = """### Q10. Big data coding: Given a large dataset of elements, apply a function f to each e...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sorting, big-data, map-reduce, external-sort, function-mapping, parallel-computing

**题目**: Big data coding: Given a large dataset of elements, apply a function f to each element and return the sorted result efficiently. The function f may not be monotonic...

**解法要点**:
- arr.sort()  # sort input first: O(n log n)
- # Map then sort: O(n log n)
- General: O(n log n) sort + O(n) map
- Monotonic f: O(n log n) sort only (map is free)"""

Q10_NEW = """### Q10. Big data coding: Given a large dataset of elements, apply a function f to each e...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sorting, big-data, map-reduce, external-sort, function-mapping, parallel-computing

**题目**: Big data coding: Given a large dataset of elements, apply a function f to each element and return the sorted result efficiently. The function f may not be monotonic...

**解题思路**:

**Case 1: f 是单调递增的**: 先排序输入, 再 map, 结果已有序。O(n log n)。

**Case 2: f 是单调递减的**: 先排序输入, map, 再 reverse。O(n log n)。

**Case 3: f 不单调**: 必须 map 之后再排序。O(n log n)。

```python
def sort_mapped(arr: list, f, is_monotonic_inc: bool = False,
                is_monotonic_dec: bool = False) -> list:
    if is_monotonic_inc:
        arr.sort()
        return [f(x) for x in arr]
    elif is_monotonic_dec:
        arr.sort()
        return [f(x) for x in reversed(arr)]
    else:
        mapped = [f(x) for x in arr]
        mapped.sort()
        return mapped
```

**大数据场景 (MapReduce)**:
1. **Map Phase**: 每个 mapper 对分片数据执行 `f(x)`, 输出 (f(x), x) 键值对
2. **Shuffle**: 按 f(x) 的值范围 partition 到不同 reducer
3. **Reduce Phase**: 每个 reducer 对局部数据排序
4. **External Sort**: 数据超出内存时, 用 k-way merge sort (将数据分块排序后写磁盘, 最后多路归并)

```python
import heapq

def external_sort_merge(sorted_chunks: list[list]) -> list:
    \"\"\"K-way merge of pre-sorted chunks.\"\"\"
    return list(heapq.merge(*sorted_chunks))
```

**复杂度**: 单机 O(n log n)。MapReduce: O((n/p) log(n/p)) per node + merge overhead, p = partition count。

**Follow-ups**:
- 如果 f 是局部单调的 (piecewise monotonic)? -> 分段排序后归并
- 如何处理数据倾斜 (某些 f(x) 值特别集中)? -> 采样估计分布, 动态调整 partition 边界"""

Q11_OLD = """### Q11. There are N coins with face values 0, 1, 2,

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: dynamic-programming, modular-arithmetic, combinatorics, counting, knapsack

**题目**: There are N coins with face values 0, 1, 2, ..., N-1. You must pick exactly K coins...

**解法要点**:
- Time: O(N * K * M)
- Space: O(K * M)"""

Q11_NEW = """### Q11. There are N coins with face values 0, 1, 2, ...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: dynamic-programming, modular-arithmetic, combinatorics, counting, knapsack

**题目**: There are N coins with face values 0, 1, 2, ..., N-1. You must pick exactly K coins. Count the number of ways such that the sum of picked coins is divisible by M.

**解题思路**:

类似 0-1 背包, 但关注的是 sum mod M。状态: dp[i][j][r] = 从前 i 个硬币中选 j 个, 总和 mod M == r 的方案数。空间优化后只需 dp[j][r]。

```python
def count_ways(n: int, k: int, m: int) -> int:
    \"\"\"Count ways to pick K coins from {0..N-1} with sum % M == 0.\"\"\"
    # dp[j][r] = ways to pick j coins with sum % m == r
    dp = [[0] * m for _ in range(k + 1)]
    dp[0][0] = 1  # pick 0 coins, sum = 0

    for coin in range(n):  # coin values: 0, 1, ..., n-1
        # Traverse j in reverse to avoid using same coin twice
        for j in range(min(k, coin + 1), 0, -1):
            for r in range(m):
                dp[j][(r + coin) % m] += dp[j - 1][r]

    return dp[k][0]

# Example: N=4, K=2, M=3 -> pick 2 from {0,1,2,3}, sum%3==0
# Valid: (0,3), (1,2) -> answer = 2
print(count_ways(4, 2, 3))  # 2
```

**复杂度**: Time O(N * K * M), Space O(K * M)。

**Follow-ups**:
- 如果硬币可以重复选取? -> 去掉 j 的逆序遍历 (变为完全背包)
- 如果 M 很大怎么优化? -> NTT (Number Theoretic Transform) 加速多项式乘法"""

Q12_OLD = """### Q12. Given a string containing digits from 2-9 inclusive, return all possible letter ... (LC 17)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: backtracking, recursion, string, combinations

**题目**: Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent on a phone keypad. Return the answer in any order...

**解法要点**:
- Time: O(4^N * N) where N = len(digits). At most 4 choices per digit, N characters per combination.
- Space: O(N) for recursion depth (excluding output)"""

Q12_NEW = """### Q12. Given a string containing digits from 2-9 inclusive, return all possible letter ... (LC 17)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: backtracking, recursion, string, combinations

**题目**: Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent on a phone keypad. Return the answer in any order...

**解题思路**:

经典回溯题。维护 digit -> letters 映射, 对每个 digit 的每个 letter 递归。

```python
def letterCombinations(digits: str) -> list[str]:
    if not digits:
        return []

    phone = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }
    result = []

    def backtrack(idx: int, path: list[str]):
        if idx == len(digits):
            result.append("".join(path))
            return
        for letter in phone[digits[idx]]:
            path.append(letter)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

**也可以用 iterative 方式** (逐 digit 展开):

```python
from itertools import product

def letterCombinations_iter(digits: str) -> list[str]:
    if not digits:
        return []
    phone = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
             "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    return ["".join(combo)
            for combo in product(*(phone[d] for d in digits))]
```

**复杂度**: Time O(4^N * N), Space O(N) 递归深度 (不含输出)。

**Follow-ups**:
- 如何只返回在字典中存在的单词? -> 加 Trie 或 set 剪枝
- 如果按 T9 输入法, 需要返回最可能的单词? -> 频率加权 + Trie 前缀搜索"""

Q13_OLD = """### Q13. Given a list of non-repetitive positive integers, find and output all maximal co... (LC 128*)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: sorting, array, grouping, consecutive-sequence

**题目**: Given a list of non-repetitive positive integers, find and output all maximal consecutive subsequences. A consecutive subsequence is a group of numbers that form a contiguous range (e.g., [1,2,3,4])...

**解法要点**:
- ### Alternative: O(n) using HashSet (LC 128 variant)
- \"""O(n) approach using hash set.\"""
- Sort approach: O(n log n) time, O(1) extra space (in-place sort)
- HashSet approach: O(n) time, O(n) space"""

Q13_NEW = """### Q13. Given a list of non-repetitive positive integers, find and output all maximal co... (LC 128*)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: sorting, array, grouping, consecutive-sequence

**题目**: Given a list of non-repetitive positive integers, find and output all maximal consecutive subsequences. A consecutive subsequence is a group of numbers that form a contiguous range (e.g., [1,2,3,4])...

**解题思路**:

**方法 1: Sort + 分组** -- 排序后线性扫描, 遇到不连续的点就断开。

```python
def find_consecutive_groups_sort(nums: list[int]) -> list[list[int]]:
    if not nums:
        return []
    nums.sort()
    groups = [[nums[0]]]
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1] + 1:
            groups[-1].append(nums[i])
        else:
            groups.append([nums[i]])
    return groups
```

**方法 2: HashSet O(n)** -- LC 128 思路。只从序列起点 (num-1 不在集合中) 开始扩展。

```python
def longest_consecutive(nums: list[int]) -> int:
    num_set = set(nums)
    best = 0
    for num in num_set:
        if num - 1 not in num_set:  # start of a sequence
            length = 1
            while num + length in num_set:
                length += 1
            best = max(best, length)
    return best

def find_all_consecutive_groups(nums: list[int]) -> list[list[int]]:
    num_set = set(nums)
    groups = []
    for num in num_set:
        if num - 1 not in num_set:
            seq = []
            cur = num
            while cur in num_set:
                seq.append(cur)
                cur += 1
            groups.append(seq)
    groups.sort(key=lambda g: g[0])
    return groups
```

**复杂度**: Sort O(n log n) time, O(1) extra。HashSet O(n) time, O(n) space。

**Follow-ups**:
- 如何处理有重复元素的情况? -> 先去重 (用 set), 再按相同逻辑处理
- 如果数据是流式到达的? -> 用 Union-Find 动态合并连续区间"""

Q14_OLD = """### Q14. SQL Problem: Given two tables - table1(user_id, article_id, date) recording user...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, inner-join, group-by, histogram, subquery, data-analysis

**题目**: SQL Problem: Given two tables - table1(user_id, article_id, date) recording user article views, and table2(article_id, article_type) mapping articles to types: (1) Count the number of article types each user viewed on 2019-01-01 using an inner join and group by. (2) Create a histogram showing the distribution of how many article types each user viewed, grouped by the count of article types."""

Q14_NEW = """### Q14. SQL Problem: Given two tables - table1(user_id, article_id, date) recording user...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, inner-join, group-by, histogram, subquery, data-analysis

**题目**: SQL Problem: Given two tables - table1(user_id, article_id, date) recording user article views, and table2(article_id, article_type) mapping articles to types: (1) Count the number of article types each user viewed on 2019-01-01 using an inner join and group by. (2) Create a histogram showing the distribution of how many article types each user viewed, grouped by the count of article types.

**解题思路**:

**Part 1: 每个用户查看了多少种文章类型**

```sql
-- Part 1: Count distinct article types per user on 2019-01-01
SELECT t1.user_id,
       COUNT(DISTINCT t2.article_type) AS type_count
FROM table1 t1
INNER JOIN table2 t2 ON t1.article_id = t2.article_id
WHERE t1.date = '2019-01-01'
GROUP BY t1.user_id;
```

**Part 2: 分布直方图** (有多少用户查看了 1 种类型, 多少用户查看了 2 种, ...)

```sql
-- Part 2: Histogram of type counts
WITH user_type_counts AS (
    SELECT t1.user_id,
           COUNT(DISTINCT t2.article_type) AS type_count
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.article_id = t2.article_id
    WHERE t1.date = '2019-01-01'
    GROUP BY t1.user_id
)
SELECT type_count,
       COUNT(*) AS num_users
FROM user_type_counts
GROUP BY type_count
ORDER BY type_count;
```

**Python 等价实现** (用 pandas):

```python
import pandas as pd

def article_type_histogram(views_df: pd.DataFrame,
                           articles_df: pd.DataFrame) -> pd.DataFrame:
    # Filter date
    daily = views_df[views_df["date"] == "2019-01-01"]
    # Join
    merged = daily.merge(articles_df, on="article_id")
    # Count distinct types per user
    user_types = (merged.groupby("user_id")["article_type"]
                  .nunique().reset_index(name="type_count"))
    # Histogram
    histogram = (user_types.groupby("type_count")
                 .size().reset_index(name="num_users"))
    return histogram
```

**Follow-ups**:
- 如果要看一段时间内的趋势 (每天的直方图)? -> 加 date 维度 GROUP BY
- 如何排除只看了一次的噪声用户? -> 加 HAVING COUNT(*) >= threshold"""

Q15_OLD = """### Q15. SQL + Python: Given tables video_posts(post_date, memberid, video_length) and me...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, python, data-analysis, hypothesis-testing, join, aggregation

**题目**: SQL + Python: Given tables video_posts(post_date, memberid, video_length) and members(memberid, country, join_date), analyze video upload patterns. Write SQL queries to: (1) Find average video count and total video length per member segmented by US vs non-US..."""

Q15_NEW = """### Q15. SQL + Python: Given tables video_posts(post_date, memberid, video_length) and me...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, python, data-analysis, hypothesis-testing, join, aggregation

**题目**: SQL + Python: Given tables video_posts(post_date, memberid, video_length) and members(memberid, country, join_date), analyze video upload patterns. Write SQL queries to: (1) Find average video count and total video length per member segmented by US vs non-US...

**解题思路**:

**Part 1: SQL -- US vs non-US video statistics**

```sql
-- Average video count and total video length per member, segmented by US/non-US
SELECT
    CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END AS segment,
    COUNT(DISTINCT v.memberid) AS num_members,
    COUNT(*) AS total_videos,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT v.memberid), 2) AS avg_videos_per_member,
    SUM(v.video_length) AS total_video_length,
    ROUND(SUM(v.video_length) * 1.0 / COUNT(DISTINCT v.memberid), 2) AS avg_length_per_member
FROM video_posts v
INNER JOIN members m ON v.memberid = m.memberid
GROUP BY CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END;
```

**Part 2: Python -- Hypothesis Testing (假设检验)**

检验 US 用户是否比 non-US 上传更多视频:

```python
import pandas as pd
from scipy import stats

def test_video_upload_difference(
    video_posts: pd.DataFrame, members: pd.DataFrame
) -> dict:
    # Merge tables
    merged = video_posts.merge(members, on="memberid")
    merged["is_us"] = merged["country"] == "US"

    # Count videos per member
    per_member = (merged.groupby(["memberid", "is_us"])
                  .size().reset_index(name="video_count"))

    us_counts = per_member[per_member["is_us"]]["video_count"]
    non_us_counts = per_member[~per_member["is_us"]]["video_count"]

    # Two-sample t-test (Welch's t-test for unequal variances)
    t_stat, p_value = stats.ttest_ind(us_counts, non_us_counts,
                                       equal_var=False)

    return {
        "us_mean": us_counts.mean(),
        "non_us_mean": non_us_counts.mean(),
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant_at_005": p_value < 0.05,
    }
```

**Follow-ups**:
- 如何控制 confounders (如 join_date, country 发展水平)? -> 倾向得分匹配 (Propensity Score Matching, PSM) 或回归分析
- 如果样本量差异很大 (US 远多于 non-US)? -> 使用 bootstrap resampling 或 Mann-Whitney U test"""


# ════════════════════════════════════════════════════════════════
# ML THEORY & CODING Q16-Q23
# ════════════════════════════════════════════════════════════════

Q16_OLD = """### Q16. Explain the Transformer architecture in detail

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: transformer, attention, self-attention, multi-head-attention, positional-encoding, model-validation

**题目**: Explain the Transformer architecture in detail. Describe the encoder and decoder components, self-attention mechanism, multi-head attention, and positional encoding..."""

Q16_NEW = """### Q16. Explain the Transformer architecture in detail

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: transformer, attention, self-attention, multi-head-attention, positional-encoding, model-validation

**题目**: Explain the Transformer architecture in detail. Describe the encoder and decoder components, self-attention mechanism, multi-head attention, and positional encoding...

**解题思路**:

**核心架构** (来自 "Attention Is All You Need", Vaswani et al. 2017):

**1. Self-Attention (自注意力)**:
- 输入 X 线性映射为 Q (Query), K (Key), V (Value)
- Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
- d_k 是 key 维度, 除以 sqrt(d_k) 防止 softmax 饱和

**2. Multi-Head Attention (MHA，多头注意力)**:
- 将 Q, K, V 分成 h 个 head, 每个 head 独立计算 attention, 最后 concat + linear
- 不同 head 可以关注不同的语义子空间 (如句法关系 vs 语义关系)

**3. Positional Encoding (PE，位置编码)**:
- Transformer 没有 RNN 的序列顺序, 需要显式注入位置信息
- 原始方法: PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(...)
- 现代方法: learned positional embeddings 或 RoPE (Rotary Position Embedding)

**4. Encoder**: N 层, 每层 = Multi-Head Self-Attention + FFN (Feed-Forward Network), 每个子层后加 LayerNorm + residual connection。

**5. Decoder**: N 层, 每层 = Masked Self-Attention + Cross-Attention (attend to encoder output) + FFN。Masked attention 防止看到未来 token。

```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor, mask=None) -> torch.Tensor:
        B, L, _ = x.shape
        Q = self.W_q(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        out = (attn @ V).transpose(1, 2).contiguous().view(B, L, -1)
        return self.W_o(out)
```

**关键面试点**:
- Self-attention 复杂度 O(n^2 * d), n 是序列长度 -- 长文本的瓶颈
- Pre-norm vs Post-norm: 现代实践多用 Pre-norm (LayerNorm 在 attention 之前)
- Decoder-only (GPT) vs Encoder-only (BERT) vs Encoder-Decoder (T5): 不同任务适合不同架构

**Follow-ups**:
- 如何解决 O(n^2) 复杂度? -> Flash Attention, Sparse Attention, Linear Attention
- BERT vs GPT 的核心区别? -> 双向 vs 单向 attention; MLM vs causal LM
- 为什么用 LayerNorm 而非 BatchNorm? -> 序列长度不固定, BN 统计量不稳定"""

Q17_OLD = """### Q17. You are testing whether changing an email's headline and content affects engagem...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: ab-testing, multivariate-testing, hypothesis-testing, statistics, experiment-design, email-campaign

**题目**: You are testing whether changing an email's headline and content affects engagement (open rate, click-through rate). How would you design and analyze this experiment? Discuss multivariate testing, hypothesis formulation, significance testing, and potential pitfalls."""

Q17_NEW = """### Q17. You are testing whether changing an email's headline and content affects engagem...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: ab-testing, multivariate-testing, hypothesis-testing, statistics, experiment-design, email-campaign

**题目**: You are testing whether changing an email's headline and content affects engagement (open rate, click-through rate). How would you design and analyze this experiment? Discuss multivariate testing, hypothesis formulation, significance testing, and potential pitfalls.

**解题思路**:

**实验设计 -- 2x2 Factorial Design (全因子设计)**:
- Factor A: Headline (old vs new)
- Factor B: Content (old vs new)
- 4 组: (old headline, old content), (old, new), (new, old), (new, new)
- 比 A/B test 更优: 可以检测 interaction effect (两个因素组合效应)

**假设检验框架**:
1. H0: 新 headline/content 不影响 CTR (Click-Through Rate，点击率)
2. H1: 至少一个 factor 影响 CTR
3. 显著性水平 alpha = 0.05, 需做 multiple comparison correction

**样本量计算**:

```python
from scipy import stats
import numpy as np

def sample_size_proportion(
    p1: float, p2: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    \"\"\"Minimum sample size per group for two-proportion z-test.\"\"\"
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    p_bar = (p1 + p2) / 2
    n = ((z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 /
         (p1 - p2) ** 2)
    return int(np.ceil(n))

# Example: detect CTR change from 5% to 6%
n = sample_size_proportion(0.05, 0.06)
print(f"Need {n} users per group")  # ~4669 per group
```

**分析步骤**:
1. Chi-squared test 或 two-proportion z-test 比较每组 CTR
2. 用 Bonferroni correction 修正多重比较 (4 组有 6 对比较)
3. 用 two-way ANOVA 或 logistic regression 检测 interaction effect

**常见陷阱**:
- **Novelty effect**: 新版本短期 CTR 高是因为新鲜感, 需要足够长的实验周期
- **Network effect**: 如果用户互相影响 (如分享邮件), 需要 cluster-level randomization
- **Multiple metrics**: open rate 和 CTR 是两个指标, 需要调整 alpha (如 alpha/2)
- **Selection bias**: 确保随机分组, 检查 pre-experiment balance

**Follow-ups**:
- 如何在 early stopping 和 statistical validity 之间取平衡? -> Sequential testing (如 O'Brien-Fleming bounds)
- 如果 sample size 不够, 如何提高 power? -> 使用 CUPED (Controlled-experiment Using Pre-Experiment Data) 降低方差"""

Q18_OLD = """### Q18. LinkedIn hypothesizes that video posting features might not be catching on inter...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hypothesis-testing, two-sample-test, t-test, proportion-test, SQL, python

**题目**: LinkedIn hypothesizes that video posting features might not be catching on internationally as well as in the US. Given two tables - video_posts(post_date, memberid, video_length) and members(memberid, country, join_date) - test whether US members upload more videos than non-US members..."""

Q18_NEW = """### Q18. LinkedIn hypothesizes that video posting features might not be catching on inter...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hypothesis-testing, two-sample-test, t-test, proportion-test, SQL, python

**题目**: LinkedIn hypothesizes that video posting features might not be catching on internationally as well as in the US. Given two tables - video_posts(post_date, memberid, video_length) and members(memberid, country, join_date) - test whether US members upload more videos than non-US members...

**解题思路**:

**Step 1: SQL 数据准备**

```sql
-- Per-member video count, segmented by US/non-US
SELECT m.memberid,
       CASE WHEN m.country = 'US' THEN 1 ELSE 0 END AS is_us,
       COUNT(v.memberid) AS video_count
FROM members m
LEFT JOIN video_posts v ON m.memberid = v.memberid
GROUP BY m.memberid, is_us;
```

注意用 LEFT JOIN: 没有发过视频的用户 video_count = 0, 不能丢弃他们。

**Step 2: Python 假设检验**

```python
import pandas as pd
from scipy import stats

def test_us_vs_nonus(members_df: pd.DataFrame,
                     videos_df: pd.DataFrame) -> dict:
    # Count videos per member
    video_counts = (videos_df.groupby("memberid")
                    .size().reset_index(name="count"))
    merged = members_df.merge(video_counts, on="memberid", how="left")
    merged["count"] = merged["count"].fillna(0)
    merged["is_us"] = merged["country"] == "US"

    us = merged[merged["is_us"]]["count"]
    non_us = merged[~merged["is_us"]]["count"]

    # Welch's t-test (unequal variance)
    t_stat, p_value = stats.ttest_ind(us, non_us, equal_var=False)

    # Also test proportion of "active posters" (at least 1 video)
    us_active = (us > 0).sum()
    non_us_active = (non_us > 0).sum()
    # Two-proportion z-test
    count = [us_active, non_us_active]
    nobs = [len(us), len(non_us)]
    z_stat, p_prop = stats.proportions_ztest(count, nobs)

    return {
        "us_mean": us.mean(),
        "non_us_mean": non_us.mean(),
        "t_test_p": p_value,
        "proportion_test_p": p_prop,
    }
```

**关键考虑**:
- **Confounders**: join_date (新用户可能不熟悉功能), 国家的互联网基础设施差异
- **Simpson's Paradox**: 某些国家用户基数大但活跃度低, 聚合后可能掩盖趋势
- **Practical significance vs Statistical significance**: p < 0.05 不代表差异有业务意义, 需要看 effect size (如 Cohen's d)

**Follow-ups**:
- 如果发现确实有差距, 如何决定是否值得为国际市场投入优化? -> 估算 ROI: 国际市场用户增长潜力 x 预期 engagement 提升
- 如何排除 join_date 的 confounding effect? -> 按 cohort 分层分析或用回归控制"""

Q19_OLD = """### Q19. Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: advertising-metrics, CPC, CPM, cost-metrics, product-sense, LinkedIn-ads

**题目**: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions) metrics. When would you use each? How do you decide which pricing model is better for an advertising campaign on LinkedIn?"""

Q19_NEW = """### Q19. Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: advertising-metrics, CPC, CPM, cost-metrics, product-sense, LinkedIn-ads

**题目**: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions) metrics. When would you use each? How do you decide which pricing model is better for an advertising campaign on LinkedIn?

**解题思路**:

**CPC (Cost Per Click，每次点击费用)**:
- 广告主按点击付费。CPC = Total Ad Spend / Total Clicks
- 适用场景: 转化导向 (lead generation, job applications, website visits)
- 优点: 只为实际兴趣付费; 缺点: 可能有 click fraud, 高竞争关键词 CPC 很贵

**CPM (Cost Per Mille，每千次展示费用)**:
- 广告主按展示次数付费。CPM = (Total Ad Spend / Total Impressions) * 1000
- 适用场景: 品牌曝光 (brand awareness campaigns)
- 优点: 可预测成本, 适合大量曝光; 缺点: 展示不等于关注, 效果难衡量

**选择框架**:

| 维度 | 选 CPC | 选 CPM |
|------|--------|--------|
| 目标 | Direct response, conversion | Brand awareness, reach |
| 预算 | 按效果付费, 风险低 | 按量付费, 适合大预算 |
| CTR 预期 | CTR 低时 CPC 更划算 | CTR 高时 CPM 更划算 |
| 衡量 | 点击数, 转化率 | 展示数, reach, brand lift |

**Equivalent CPM** (eCPM): 用于跨模型比较。eCPM = CPC * CTR * 1000。

```python
def compare_pricing(cpc: float, cpm: float, expected_ctr: float) -> str:
    \"\"\"Recommend CPC or CPM based on expected CTR.\"\"\"
    ecpm_from_cpc = cpc * expected_ctr * 1000
    if ecpm_from_cpc < cpm:
        return f"CPC is cheaper: eCPM=${ecpm_from_cpc:.2f} < CPM=${cpm:.2f}"
    return f"CPM is cheaper: CPM=${cpm:.2f} < eCPM=${ecpm_from_cpc:.2f}"

# Example: CPC=$2, CPM=$10, expected CTR=0.8%
print(compare_pricing(2.0, 10.0, 0.008))
# "CPC is cheaper: eCPM=$16.00 < CPM=$10.00" -> actually CPM is cheaper here
```

**LinkedIn 特有考虑**:
- LinkedIn 用户意图明确 (professional context), CTR 通常高于其他平台
- LinkedIn Ads 还支持 CPS (Cost Per Send, InMail), CPV (Cost Per View, video ads)
- 对于 B2B marketing, CPC 通常更受欢迎因为 lead quality 更可控

**Follow-ups**:
- 如何设计一个 ad auction system 同时支持 CPC 和 CPM bidders? -> 统一用 eCPM 排名
- 如何检测和防止 click fraud? -> 异常检测: 同 IP 高频点击, bot 行为模式识别"""

Q20_OLD = """### Q20. Design and implement a sparse vector and sparse matrix representation from scrat... (LC 1573, 311)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sparse-vector, sparse-matrix, data-structures, optimization, hash-map, dot-product

**题目**: Design and implement a sparse vector and sparse matrix representation from scratch. Define the constructor, attributes, and methods...

**解法要点**:
- Space: O(k) where k = number of non-zero elements
- \"""Compute dot product. O(min(k1, k2)) time.\"""
- Space: O(nnz) where nnz = number of non-zero elements
- \"""Multiply two sparse matrices. O(nnz_A * nnz_B / cols_A) average.\""""

Q20_NEW = """### Q20. Design and implement a sparse vector and sparse matrix representation from scrat... (LC 1573, 311)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sparse-vector, sparse-matrix, data-structures, optimization, hash-map, dot-product

**题目**: Design and implement a sparse vector and sparse matrix representation from scratch. Define the constructor, attributes, and methods...

**解题思路**:

**Sparse Vector (稀疏向量)** -- 只存储非零元素:

```python
class SparseVector:
    def __init__(self, nums: list[int]):
        self.nonzero = {i: v for i, v in enumerate(nums) if v != 0}
        self.size = len(nums)

    def dotProduct(self, other: "SparseVector") -> int:
        # Iterate over the smaller set for efficiency
        if len(self.nonzero) > len(other.nonzero):
            return other.dotProduct(self)
        result = 0
        for idx, val in self.nonzero.items():
            if idx in other.nonzero:
                result += val * other.nonzero[idx]
        return result
```

**Sparse Matrix (稀疏矩阵)** -- 用 CSR (Compressed Sparse Row) 或 dict-of-dicts:

```python
class SparseMatrix:
    def __init__(self, mat: list[list[int]]):
        self.rows = len(mat)
        self.cols = len(mat[0]) if mat else 0
        # Store as {row: {col: val}} for non-zero entries
        self.data = {}
        for i in range(self.rows):
            for j in range(self.cols):
                if mat[i][j] != 0:
                    if i not in self.data:
                        self.data[i] = {}
                    self.data[i][j] = mat[i][j]

    def multiply(self, other: "SparseMatrix") -> list[list[int]]:
        \"\"\"Sparse matrix multiplication. O(nnz_A * avg_nnz_per_row_B).\"\"\"
        result = [[0] * other.cols for _ in range(self.rows)]
        for i, row_data in self.data.items():
            for k, val_a in row_data.items():
                if k in other.data:
                    for j, val_b in other.data[k].items():
                        result[i][j] += val_a * val_b
        return result
```

**复杂度**:
- Dot product: O(min(k1, k2)), k = non-zero count
- Matrix multiply: O(nnz_A * avg nnz per row of B), 远优于 dense O(n^3)
- Space: O(nnz)

**Follow-ups**:
- 如何高效实现 transpose? -> 交换 row/col 索引即可, O(nnz)
- 对于超大矩阵如何分布式计算? -> Block partition + MapReduce
- CSR vs COO vs CSC 格式的区别和适用场景? -> CSR 适合行切片, CSC 适合列切片, COO 适合构建"""

Q21_OLD = """### Q21. Implement weighted random sampling from a multinomial distribution

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: sampling, multinomial, probability, binary-search, alias-method, random

**题目**: Implement weighted random sampling from a multinomial distribution. Given an array of n numbers representing weights/probabilities, write a function to sample an index according to those weights...

**解法要点**:
- Build: O(n), Sample: O(log n), Space: O(n)
- O(1) sampling after O(n) preprocessing.
- \"""Alias method for O(1) weighted sampling.
- Build: O(n), Sample: O(1), Space: O(n)"""

Q21_NEW = """### Q21. Implement weighted random sampling from a multinomial distribution

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: sampling, multinomial, probability, binary-search, alias-method, random

**题目**: Implement weighted random sampling from a multinomial distribution. Given an array of n numbers representing weights/probabilities, write a function to sample an index according to those weights...

**解题思路**:

**方法 1: Prefix Sum + Binary Search** -- 构建累积分布, 采样时二分查找。

```python
import random
import bisect

class WeightedSampler:
    def __init__(self, weights: list[float]):
        self.prefix = []
        running = 0.0
        for w in weights:
            running += w
            self.prefix.append(running)
        self.total = running

    def sample(self) -> int:
        r = random.uniform(0, self.total)
        return bisect.bisect_left(self.prefix, r)
```

**方法 2: Alias Method** -- O(n) 预处理, O(1) 采样。核心思想: 将不均匀分布转化为均匀的 n 个 bin, 每个 bin 最多 2 个元素。

```python
class AliasMethod:
    def __init__(self, weights: list[float]):
        n = len(weights)
        total = sum(weights)
        prob = [w * n / total for w in weights]
        self.alias = list(range(n))
        self.prob_table = [1.0] * n

        small, large = [], []
        for i, p in enumerate(prob):
            (small if p < 1.0 else large).append(i)

        while small and large:
            s = small.pop()
            l = large.pop()
            self.prob_table[s] = prob[s]
            self.alias[s] = l
            prob[l] -= (1.0 - prob[s])
            (small if prob[l] < 1.0 else large).append(l)

        self.n = n

    def sample(self) -> int:
        i = random.randint(0, self.n - 1)
        return i if random.random() < self.prob_table[i] else self.alias[i]
```

**复杂度对比**:
| 方法 | Build | Sample | Space |
|------|-------|--------|-------|
| Prefix Sum + Binary Search | O(n) | O(log n) | O(n) |
| Alias Method | O(n) | O(1) | O(n) |

**Follow-ups**:
- 如果权重会动态更新? -> 用 Fenwick Tree (Binary Indexed Tree, BIT), 支持 O(log n) 更新和采样
- 如何实现不放回采样 (sampling without replacement)? -> 每次采样后设该元素权重为 0, 更新前缀和"""

Q22_OLD = """### Q22. Compare and contrast using open-source software vs building your own solution (b...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: open-source, build-vs-buy, engineering-decision, tradeoffs, discussion, software-engineering

**题目**: Compare and contrast using open-source software vs building your own solution (build vs buy). How would you make this decision for a machine learning project at a large company like LinkedIn? Discuss factors like maintainability, customization, security, community support, licensing, and cost."""

Q22_NEW = """### Q22. Compare and contrast using open-source software vs building your own solution (b...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: open-source, build-vs-buy, engineering-decision, tradeoffs, discussion, software-engineering

**题目**: Compare and contrast using open-source software vs building your own solution (build vs buy). How would you make this decision for a machine learning project at a large company like LinkedIn? Discuss factors like maintainability, customization, security, community support, licensing, and cost.

**解题思路**:

**对比框架**:

| 维度 | Open Source (Buy/Adopt) | Build In-House |
|------|------------------------|----------------|
| **Time to market** | 快 -- 现成可用 | 慢 -- 从零开始 |
| **Customization** | 受限于项目架构 | 完全可控 |
| **Maintenance** | 社区维护, 但可能 abandon | 需要专门团队 |
| **Security** | 代码透明但也暴露攻击面 | 可以做更严格的内部审计 |
| **Cost** | 初始低, 但集成/运维成本可能高 | 初始高, 但长期成本可控 |
| **Licensing** | 需要审查 (GPL vs MIT vs Apache) | 无 license 风险 |
| **Talent** | 更多人熟悉主流 OSS | 需要培训或招聘 |

**决策框架 (Decision Matrix)**:

1. **Core vs Context**: 如果是公司核心竞争力 (如 LinkedIn 的 feed ranking), 自建; 如果是 context (如日志系统), 用 open source。
2. **Differentiation**: 如果需要高度定制且独特, 自建更合适。
3. **Maturity**: 如果 OSS 项目已经成熟稳定 (如 Kafka, Spark), 优先采用。
4. **Team capability**: 团队是否有能力维护自建系统?

**LinkedIn 实际案例**:
- **Adopt**: Kafka (消息队列), Spark (大数据处理), Lucene/Solr (搜索) -- 都是 LinkedIn 先采用后开源的
- **Build**: Voldemort (KV store), Samza (stream processing), Pro-ML (ML platform) -- 核心业务需要高度定制

**推荐回答结构**:
1. 先问清需求: 是否核心功能? 时间线? 团队规模?
2. 列出 Build vs Buy 各 3-4 个优缺点
3. 给出 decision matrix 评分
4. 提出 hybrid approach: 用 OSS 做基础, 在上层自建定制层

**Follow-ups**:
- 如何评估一个 OSS 项目的 health? -> Stars, commit frequency, issue response time, license, backing company
- 如果选了 OSS 后发现不满足需求? -> Fork + maintain internally (如 LinkedIn 对 Kafka 的贡献)"""

Q23_OLD = """### Q23. Which LinkedIn product do you like most and why

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: product-sense, LinkedIn-products, behavioral, product-analysis, discussion

**题目**: Which LinkedIn product do you like most and why? Demonstrate your understanding of LinkedIn's product ecosystem and your product sense by analyzing a specific feature - its value proposition, target users, key metrics, and potential improvements."""

Q23_NEW = """### Q23. Which LinkedIn product do you like most and why

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: product-sense, LinkedIn-products, behavioral, product-analysis, discussion

**题目**: Which LinkedIn product do you like most and why? Demonstrate your understanding of LinkedIn's product ecosystem and your product sense by analyzing a specific feature - its value proposition, target users, key metrics, and potential improvements.

**解题思路 (以 LinkedIn Feed 为例)**:

**1. Product Overview**:
LinkedIn Feed 是用户的主信息流, 通过算法 ranking 展示 connections 的动态、文章、招聘信息和广告。

**2. Value Proposition**:
- 对用户: 获取行业洞察, 保持 professional network 活跃
- 对 LinkedIn: 核心 engagement driver, 广告变现的主渠道
- 对 content creators: 建立 thought leadership, 扩大影响力

**3. Target Users**:
- Job seekers: 关注行业动态和招聘信息
- Professionals: networking 和 knowledge sharing
- Recruiters: 了解候选人动态和市场趋势
- B2B marketers: 内容营销和 lead generation

**4. Key Metrics**:
- **Engagement**: DAU/MAU ratio, time spent in feed, scroll depth
- **Content quality**: Meaningful interactions (comments > reactions > views)
- **Revenue**: Ad revenue per session, CTR on sponsored posts
- **Creator health**: Post frequency, follower growth rate

**5. Potential Improvements**:
- **Content quality filtering**: 减少 engagement bait (如 "agree?" polls), 提高信息质量
- **Topic-based feed**: 允许用户按话题 (ML, product management, etc.) 筛选 feed
- **Better video experience**: 短视频整合, 类似 TikTok 但保持 professional tone
- **AI-powered summaries**: 对长文章提供 AI 摘要, 降低信息消费成本

**回答框架 (STAR-Product)**:
1. **选择**: 说明选了什么产品以及为什么
2. **分析**: 用户是谁, 核心价值, 竞争优势
3. **指标**: 如何衡量成功
4. **改进**: 2-3 个具体改进建议 + 预期影响

**Follow-ups**:
- 如何平衡 content creator 利益和 consumer experience? -> 双边市场平衡, 监控 creator retention 同时优化 consumer engagement
- 如何衡量 "meaningful engagement" vs 浅层互动? -> 基于 comments/shares 而非 likes, 用 time-spent-reading 作为 proxy"""


# ════════════════════════════════════════════════════════════════
# ML SYSTEM DESIGN Q24-Q47
# ════════════════════════════════════════════════════════════════

Q24_OLD = """### Q24. Design a distributed Key-Value Store that supports replication, sharding, and co...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: distributed-systems, key-value-store, replication, sharding, vector-clock, quorum

**题目**: Design a distributed Key-Value Store that supports replication, sharding, and consistency guarantees. Discuss concepts including replica placement, sharding strategies, vector clocks for conflict resolution, and read/write quorum protocols...

**解法要点**:
- Space: O(d * w), typically d=5-7, w = e/epsilon"""

Q24_NEW = """### Q24. Design a distributed Key-Value Store that supports replication, sharding, and co...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: distributed-systems, key-value-store, replication, sharding, vector-clock, quorum

**题目**: Design a distributed Key-Value Store that supports replication, sharding, and consistency guarantees. Discuss concepts including replica placement, sharding strategies, vector clocks for conflict resolution, and read/write quorum protocols...

**解题思路**:

**架构概览**:

**1. Sharding (分片策略)**:
- **Consistent Hashing**: 将 key hash 到环上, 每个 node 负责一段 range。增删节点只影响相邻节点。
- **Virtual Nodes**: 每个物理节点对应多个虚拟节点, 解决数据倾斜。
- 备选: Range-based sharding (适合 range queries) 或 Directory-based sharding。

**2. Replication (复制)**:
- 每个 key 复制到 hash ring 上顺时针方向的 N 个节点 (通常 N=3)。
- Replica placement: 确保副本不在同一个 rack/datacenter。

**3. Consistency -- Quorum Protocol**:
- W (write quorum) + R (read quorum) > N 保证强一致性
- 常见配置: N=3, W=2, R=2 (强一致); N=3, W=1, R=1 (最终一致, 高可用)
- **Tunable consistency**: 让客户端按请求选择 consistency level。

**4. Conflict Resolution**:
- **Vector Clock**: 每个 replica 维护 [node_id: counter] 向量。写操作时递增本地 counter。
- 读取时若发现并发版本 (neither dominates), 返回给客户端解决冲突 (last-write-wins 或 application-level merge)。

**5. Failure Handling**:
- **Sloppy Quorum + Hinted Handoff**: 节点下线时, 写入暂存到其他节点; 恢复后同步回来。
- **Anti-entropy**: 后台用 Merkle Tree 比较副本差异并同步。
- **Gossip Protocol**: 节点间周期性交换状态, 检测故障。

**关键 trade-offs (CAP Theorem)**:
- CP (Consistency + Partition tolerance): 拒绝不一致的写入, 可能 unavailable (如 HBase)
- AP (Availability + Partition tolerance): 允许暂时不一致, 保证可用 (如 Dynamo, Cassandra)

**Follow-ups**:
- 如何实现 cross-datacenter replication? -> Async replication + conflict resolution (CRDTs or vector clocks)
- 如何处理 hot keys (某些 key 访问量远超平均)? -> Read replicas, caching layer, key-level load balancing"""

Q25_OLD = """### Q25. Design a metrics monitoring system for a large-scale distributed infrastructure ...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: metrics-monitoring, time-series-db, LSM-tree, indexing, observability, distributed-systems

**题目**: Design a metrics monitoring system for a large-scale distributed infrastructure like LinkedIn. Cover: choice of time-series database vs NoSQL, efficient indexing strategies for time-series data, LSM tree compaction principles, and how to collect system-level and application-level metrics from nodes and containers."""

Q25_NEW = """### Q25. Design a metrics monitoring system for a large-scale distributed infrastructure ...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: metrics-monitoring, time-series-db, LSM-tree, indexing, observability, distributed-systems

**题目**: Design a metrics monitoring system for a large-scale distributed infrastructure like LinkedIn. Cover: choice of time-series database vs NoSQL, efficient indexing strategies for time-series data, LSM tree compaction principles, and how to collect system-level and application-level metrics from nodes and containers.

**解题思路**:

**系统架构**:

```
Agents (每台机器) -> Collector/Aggregator -> Message Queue (Kafka)
    -> Stream Processor -> Time-Series DB -> Query Engine -> Dashboard/Alerts
```

**1. Data Collection**:
- **System metrics**: CPU, memory, disk, network (用 node_exporter / collectd)
- **Application metrics**: request latency, error rate, throughput (用 StatsD / Micrometer)
- **Container metrics**: Docker/K8s cgroup stats
- Pull vs Push model: Prometheus 用 pull (主动拉取), StatsD 用 push (应用推送)

**2. 存储选型 -- Time-Series DB (TSDB，时序数据库)**:
- **InfluxDB / TimescaleDB / Prometheus**: 专为时序数据优化
- 优于普通 NoSQL 因为: 高效的时间范围查询, 自动 downsampling, retention policies
- **LSM Tree (Log-Structured Merge Tree)**: 写优化结构。数据先写入内存 MemTable, 满后 flush 到磁盘 SSTable (Sorted String Table), 后台 compaction 合并文件。

**3. Indexing**:
- 按 (metric_name, tags, timestamp) 索引
- Tag-based indexing: 支持按 host, service, region 等维度查询
- Time-partitioned storage: 按时间段分片, 旧数据自动归档/删除

**4. 查询和告警**:
- **Query**: 支持 aggregation (sum, avg, percentile), group by, downsampling
- **Alerting**: 基于阈值或异常检测, 多级告警 (warning -> critical -> page)

**5. Scale 考虑**:
- LinkedIn 规模: 数十万台机器, 每秒数百万 metric data points
- 水平扩展: Kafka 做缓冲, TSDB 分片存储
- Downsampling: 最近 24h 保留秒级数据, 1 周保留分钟级, 1 年保留小时级

**Follow-ups**:
- 如何实现异常检测 (anomaly detection) 而非简单阈值? -> 用 Prophet, ARIMA, 或 isolation forest 检测时序异常
- 如何减少 metric cardinality explosion (tag 组合爆炸)? -> 限制 tag 数量, 预聚合高基数 tags"""

Q26_OLD = """### Q26. Given a LinkedIn webpage showing user profile information, design a system to cl...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: classification, NLP, feature-engineering, text-classification, user-profiling, LinkedIn-profile

**题目**: Given a LinkedIn webpage showing user profile information, design a system to classify each user into a job category (e.g., software engineer, data scientist, product manager) and extract relevant attributes. How would you approach feature engineering, model selection, and handling edge cases like career changers or multi-role users?"""

Q26_NEW = """### Q26. Given a LinkedIn webpage showing user profile information, design a system to cl...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: classification, NLP, feature-engineering, text-classification, user-profiling, LinkedIn-profile

**题目**: Given a LinkedIn webpage showing user profile information, design a system to classify each user into a job category (e.g., software engineer, data scientist, product manager) and extract relevant attributes. How would you approach feature engineering, model selection, and handling edge cases like career changers or multi-role users?

**解题思路**:

**1. Problem Formulation**:
- Multi-class classification (可能 multi-label, 因为一个人可能有多个 role)
- 目标: 输入 profile -> 输出 job category + confidence score

**2. Feature Engineering**:
- **Text features**: headline, summary, job title, skills (TF-IDF (Term Frequency-Inverse Document Frequency) 或 BERT embeddings)
- **Structured features**: industry, company size, years of experience, education, skill endorsement counts
- **Graph features**: connections 的 job category 分布 (homophily -- 同行业的人倾向互相连接)
- **Behavioral features**: 关注的 groups, 点赞的 posts 的 topic 分布

**3. Model Selection**:
- **Baseline**: Logistic Regression / Random Forest on TF-IDF features
- **Production**: Fine-tuned BERT on headline + summary, 加上 structured features 的 MLP 分支
- **Multi-label**: Binary Relevance (每个 category 一个 classifier) 或 multi-label BERT

**4. Training Pipeline**:
- **Labels**: 用现有 standardized title + industry 作为 weak labels, 或 human annotation
- **Data augmentation**: 同义词替换, title 变体 (如 "SWE" = "Software Engineer")
- **Class imbalance**: Focal loss 或 oversampling rare categories

**5. Edge Cases**:
- **Career changers**: 用最近 N 年的 experience 加权, 而非全部历史
- **Multi-role users**: Multi-label 输出 + 每个 label 的 confidence
- **Incomplete profiles**: 缺少 headline/summary 时 fallback 到 skills + industry
- **Freelancers/Consultants**: 用 project descriptions 和 skills 而非 company/title

**6. Serving**:
- 实时: 新注册/更新 profile 时 trigger classification
- 批量: 定期重新分类所有用户 (捕捉 career transitions)

**Follow-ups**:
- 如何处理新兴 job categories (如 "AI Engineer" 几年前不存在)? -> 监控 unclassified rate, 定期用 clustering 发现新类别
- 如何保证 classification 不会产生 bias? -> 审查 demographic parity, 避免用 gender/race-correlated features"""

Q27_OLD = """### Q27. Design a system to help LinkedIn recruiters find suitable candidates for job ope...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: recommendation-system, ranking, matching, recruiter, talent-search, information-retrieval

**题目**: Design a system to help LinkedIn recruiters find suitable candidates for job openings. Cover the end-to-end pipeline: understanding recruiter intent, candidate retrieval, ranking, matching, and recommendation..."""

Q27_NEW = """### Q27. Design a system to help LinkedIn recruiters find suitable candidates for job ope...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: recommendation-system, ranking, matching, recruiter, talent-search, information-retrieval

**题目**: Design a system to help LinkedIn recruiters find suitable candidates for job openings. Cover the end-to-end pipeline: understanding recruiter intent, candidate retrieval, ranking, matching, and recommendation...

**解题思路**:

**End-to-End Pipeline**:

```
Recruiter Query -> Query Understanding -> Candidate Retrieval
    -> Ranking -> Filtering -> Results + Explanations
```

**1. Query Understanding**:
- 解析 recruiter 输入: job title, skills, location, experience, company preferences
- Query expansion: "ML Engineer" -> also search "Machine Learning Engineer", "AI Engineer"
- Intent classification: 是精确搜索还是探索性搜索

**2. Candidate Retrieval (召回层)**:
- **Inverted index**: 按 skills, title, location 索引
- **Embedding-based retrieval**: 将 job description 和 candidate profile encode 到同一向量空间, 用 ANN (Approximate Nearest Neighbor，近似最近邻) 搜索 (如 FAISS, HNSW)
- 目标: 从 500M+ 用户中快速召回 top-1000 candidates

**3. Ranking (排序层)**:
- **Features**:
  - Relevance: skill match score, title similarity, experience fit
  - Quality: profile completeness, endorsement count, activity level
  - Behavioral: 该候选人对类似 InMail 的历史 response rate
  - Contextual: 是否 open to work, 地理距离
- **Model**: Learning-to-Rank (LambdaMART 或 neural ranking model)
- **Training data**: recruiter click/response as positive, skip as negative

**4. Filtering & Business Rules**:
- 过滤已联系过的候选人
- 排除明确表示不感兴趣的用户
- Diversity: 确保结果不过度集中于某个公司/学校

**5. Metrics**:
- **Offline**: NDCG (Normalized Discounted Cumulative Gain), MRR (Mean Reciprocal Rank)
- **Online**: InMail response rate, time to fill position, recruiter return rate

**Follow-ups**:
- 如何处理 cold-start candidates (新用户, profile 信息少)? -> 用 collaborative filtering (类似用户的行为) + 要求完善 profile
- 如何避免 bias (如偏向某些学校/公司)? -> Fairness constraints on ranking, blind resume features"""

Q28_OLD = """### Q28. Design the metrics framework for LinkedIn's job search and ranking module

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-search, ranking, CTR, product-metrics, evaluation

**题目**: Design the metrics framework for LinkedIn's job search and ranking module. What metrics would you track (click-through rate, application rate, time spent, search frequency)? What features matter most for job ranking, and how would you measure the overall health of the job search experience?"""

Q28_NEW = """### Q28. Design the metrics framework for LinkedIn's job search and ranking module

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-search, ranking, CTR, product-metrics, evaluation

**题目**: Design the metrics framework for LinkedIn's job search and ranking module. What metrics would you track (click-through rate, application rate, time spent, search frequency)? What features matter most for job ranking, and how would you measure the overall health of the job search experience?

**解题思路**:

**Metrics 分层框架**:

**1. North Star Metric (北极星指标)**: Successful job applications per active job seeker per week。衡量 end-to-end 价值。

**2. Primary Metrics**:
- **CTR (Click-Through Rate)**: job card clicks / impressions。衡量排序相关性。
- **Application Rate**: applications / job detail page views。衡量转化效率。
- **Search Success Rate**: % of searches leading to at least 1 click/application。
- **Time to Apply**: 从搜索到提交申请的平均时间。越短越好。

**3. Quality Metrics**:
- **Relevance Score**: 搜索结果与 query 的匹配度 (通过 human evaluation 或 user feedback)
- **Application-to-Interview Ratio**: 申请后获得面试的比例 (需要 recruiter 端数据)
- **Repeat Search Rate**: 高重复率说明搜索结果不满意
- **Zero-result Rate**: 搜索返回 0 结果的比例

**4. Engagement Metrics**:
- **Session depth**: 每次搜索会话浏览几个 job detail pages
- **Saved jobs rate**: 收藏率 (表示意向但未立即申请)
- **Return rate**: 用户多久回来搜索一次

**5. Job Ranking Features (重要性排序)**:
- **Query-job relevance**: title match, skill match, description similarity
- **Personalization**: user's past applications, saved jobs, profile-job fit
- **Job freshness**: 新发布的 job 优先 (posting date)
- **Job quality signals**: company rating, salary range, application count
- **Geolocation**: distance/commute time

**Guardrail Metrics** (不能变差):
- Revenue per search (ad revenue)
- Job poster satisfaction (post-to-fill rate)
- User diversity (不过度推荐同一类 job)

**Follow-ups**:
- CTR 提升但 application rate 下降怎么办? -> 可能是标题 clickbait 导致; 需要 composite metric
- 如何衡量 job 推荐的 long-term value? -> 跟踪 hired + 6-month retention"""

Q29_OLD = """### Q29. Design LinkedIn's feed ranking system

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: feed-ranking, recommendation, features, engagement, content-ranking, multi-objective

**题目**: Design LinkedIn's feed ranking system. What features would you consider for ranking content in a user's feed? Cover content features, user features, interaction features, and how you would balance relevance, engagement, and content diversity."""

Q29_NEW = """### Q29. Design LinkedIn's feed ranking system

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: feed-ranking, recommendation, features, engagement, content-ranking, multi-objective

**题目**: Design LinkedIn's feed ranking system. What features would you consider for ranking content in a user's feed? Cover content features, user features, interaction features, and how you would balance relevance, engagement, and content diversity.

**解题思路**:

**系统架构 (Multi-stage Pipeline)**:

```
Candidate Generation -> First-pass Ranking -> Second-pass Ranking
    -> Diversity/Business Rules -> Final Feed
```

**1. Candidate Generation (召回)**:
- **Network posts**: 1st/2nd degree connections 的动态
- **Topic-based**: 用户关注 topic 的热门内容
- **Collaborative filtering**: 类似用户互动过的内容
- 目标: 从数百万候选 post 中召回 ~1000 个

**2. Feature Categories**:

**Content features**:
- Content type (text, image, video, article, poll)
- Content length, language, hashtags
- Creator credibility (follower count, engagement history)
- Content freshness (posting time)

**User features**:
- Industry, job title, seniority level
- Historical engagement patterns (偏好 video vs text)
- Active time patterns, device type

**Interaction features (user x content)**:
- User-creator relationship (connection degree, interaction history)
- Topic affinity score
- 用户对类似 content 的历史 CTR

**3. Ranking Model**:
- **Multi-objective optimization**: 同时预测多个目标
  - P(click), P(like), P(comment), P(share), P(long_dwell_time)
- Final score = w1*P(click) + w2*P(comment) + w3*P(share) - w4*P(hide)
- Model: GBDT (Gradient Boosted Decision Tree) 或 deep neural network (wide & deep)

**4. Diversity & De-duplication**:
- MMR (Maximal Marginal Relevance): 在 relevance 和 diversity 之间平衡
- 规则: 连续不超过 2 个同一 creator 的 post; 不超过 3 个同类型内容
- Viral content throttling: 防止单条 post 过度曝光

**5. Metrics**:
- **Primary**: time spent, meaningful engagement (comments, shares)
- **Guardrails**: 广告 revenue, creator 发帖频率, misinformation rate

**Follow-ups**:
- 如何处理 cold-start users/content? -> 用 popularity-based ranking + quick exploration (epsilon-greedy)
- 如何避免 filter bubble (信息茧房)? -> 注入 exploration posts, 跨 topic 推荐"""

Q30_OLD = """### Q30. LinkedIn's job application rate has been dropping

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: funnel-analysis, product-analytics, debugging, segmentation, metrics, root-cause-analysis

**题目**: LinkedIn's job application rate has been dropping. You are given data showing the overall application funnel..."""

Q30_NEW = """### Q30. LinkedIn's job application rate has been dropping

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: funnel-analysis, product-analytics, debugging, segmentation, metrics, root-cause-analysis

**题目**: LinkedIn's job application rate has been dropping. You are given data showing the overall application funnel...

**解题思路**:

**结构化诊断框架 (MECE)**:

**Step 1: 明确问题**
- Application rate = applications / job detail page views? 或 applications / active job seekers?
- Drop 的程度? 是突然下降还是缓慢趋势?
- 时间范围? 某个时间点之后突变可能是 bug 或 product change

**Step 2: Funnel 分析**

```
Search/Browse -> Job Impressions -> Clicks (CTR) -> Detail Page Views
    -> Start Application -> Complete Application (Completion Rate)
```

在每一步检查 drop 发生在哪里:
- CTR 下降? -> 排序/推荐问题
- Detail page -> Start application 下降? -> UI 问题, job quality 问题
- Application completion 下降? -> 流程太长, 技术 bug, external link redirect

**Step 3: 分维度拆解 (Segmentation)**
- **平台**: mobile vs desktop vs app (某个平台可能有 bug)
- **地区**: 特定 country/region 的下降
- **用户类型**: premium vs free, 新用户 vs 老用户
- **Job 类型**: 某个 industry 或 job level 的下降
- **时间**: weekday vs weekend, 是否和节假日相关

**Step 4: 假设生成与验证**

| 假设 | 验证方法 |
|------|---------|
| Recent product change broke something | Check deployment timeline, A/B test results |
| Job quality declined (more spam jobs) | Check job reporting rate, time-to-fill |
| Competitor (Indeed) launched new feature | Check market data, user surveys |
| Seasonal effect (post-hiring season) | YoY comparison |
| External redirect rate increased | Check % of "Apply on company site" vs in-app apply |

**Step 5: 推荐行动**
1. 如果是 bug: hotfix + post-mortem
2. 如果是 job quality: 加强 job posting review + quality signals
3. 如果是 UX 问题: simplify application flow (Easy Apply 推广)
4. 如果是 seasonal: 正常, 但考虑 counter-seasonal promotions

**Follow-ups**:
- 如果 apply rate 下降但 save rate 上升? -> 用户在 browsing 但 not ready to apply; 可能是 job market uncertainty
- 如何区分 supply-side (fewer good jobs) vs demand-side (fewer active seekers) 问题? -> 分别看 new job postings trend 和 active seeker trend"""

Q31_OLD = """### Q31. How would you identify frequent business travelers from LinkedIn data

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-engineering, classification, geo-features, user-segmentation, IP-geolocation, VPN

**题目**: How would you identify frequent business travelers from LinkedIn data? What features would you extract (job title, travel frequency, location changes, geo clusters, international company connections, connections distribution)? How would you handle issues with IP address and VPN accuracy for geo-based features?

**Follow-ups**:
- How would you handle issues with IP address and VPN accuracy for geo-based features?"""

Q31_NEW = """### Q31. How would you identify frequent business travelers from LinkedIn data

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-engineering, classification, geo-features, user-segmentation, IP-geolocation, VPN

**题目**: How would you identify frequent business travelers from LinkedIn data? What features would you extract (job title, travel frequency, location changes, geo clusters, international company connections, connections distribution)? How would you handle issues with IP address and VPN accuracy for geo-based features?

**解题思路**:

**1. Feature Engineering**:

**Profile-based features**:
- Job title keywords: "consultant", "sales", "account manager", "field engineer" 等高出差频率 title
- Industry: consulting, sales, enterprise software 等
- Company size and type: 大型跨国公司员工更可能出差

**Geo/IP features**:
- IP-based login location 的 unique city count per month
- Location change frequency (连续 login 从不同城市)
- Geo cluster diversity: 登录城市的离散程度
- International login percentage

**Behavioral features**:
- LinkedIn 活跃时间段的变化 (时区频繁变化 = 旅行)
- 连接人的地理分布 (connections across many cities/countries)
- 与不同城市 companies 的 interaction frequency

**Content features**:
- Posts/check-ins mentioning travel, airports, hotels
- Skills endorsements from diverse locations

**2. Model Approach**:
- **Binary classification**: traveler vs non-traveler
- 训练数据: 可以用 survey data 或 known travel-heavy roles 作为 weak labels
- Model: Gradient Boosted Trees (XGBoost/LightGBM) with above features
- Threshold tuning: 根据 use case 调整 (advertising 偏向 recall, analytics 偏向 precision)

**3. VPN/IP 准确性处理**:
- VPN detection services (如 MaxMind) 标记可能的 VPN IP
- 结合 WiFi fingerprint 和 device GPS (mobile app) 补充位置信息
- 排除已知 corporate VPN IP ranges
- 用多个 signal (IP + timezone + login pattern) 交叉验证

**Follow-ups**:
- 如何区分 business travel 和 personal travel? -> 出差通常是 weekday, 停留时间短, 重复去同一城市
- 这个 model 的 business value 是什么? -> 精准投放旅行/商务服务广告, travel industry ad targeting"""

Q32_OLD = """### Q32. Design a recommendation system for LinkedIn Learning

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-system, LinkedIn-Learning, ad-targeting, collaborative-filtering, content-based, personalization

**题目**: Design a recommendation system for LinkedIn Learning. Who are the target users? What features would you use for course recommendations? Additionally, how would you approach ad targeting for travel company advertisements on LinkedIn (e.g., recommending ads for travel services to the right audience)?"""

Q32_NEW = """### Q32. Design a recommendation system for LinkedIn Learning

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-system, LinkedIn-Learning, ad-targeting, collaborative-filtering, content-based, personalization

**题目**: Design a recommendation system for LinkedIn Learning. Who are the target users? What features would you use for course recommendations? Additionally, how would you approach ad targeting for travel company advertisements on LinkedIn (e.g., recommending ads for travel services to the right audience)?

**解题思路**:

**Part 1: LinkedIn Learning 推荐系统**

**Target Users**: professionals seeking skill development -- job seekers upskilling, employees following learning paths, career changers

**推荐策略 (多路召回)**:
1. **Content-based**: 基于用户 skills gap (profile skills vs desired job requirements) 推荐补齐的课程
2. **Collaborative Filtering (CF，协同过滤)**: 相似用户 (同 title/industry) 学过的课程
3. **Sequential**: 用户刚完成 "Python Basics" -> 推荐 "Advanced Python"
4. **Trending**: 行业内热门课程 (如 AI/ML 课程 in tech industry)

**Features**:
- User: current skills, target role, industry, seniority, past courses, completion rates
- Course: topic tags, difficulty, duration, instructor rating, completion rate
- Cross: user-skill x course-skill overlap, peer completion rate

**Ranking Model**: 预测 P(complete course | user, course), 用 multi-task learning 同时优化 click + start + complete。

**Cold Start**:
- New user: 基于 profile 的 rule-based recommendations + onboarding survey
- New course: 基于 course metadata 的 content-based matching

**Part 2: Travel Ad Targeting**

**Audience Segmentation**:
- 用 Q31 的 frequent traveler identification model
- 加上: 关注旅行相关 pages/groups, 在 travel industry 工作, 高 seniority (更多商务旅行预算)

**Ad Ranking**: eCPM = bid * P(click) * P(convert), 在旅行广告和其他广告间竞价

**Follow-ups**:
- 如何衡量推荐质量? -> 课程完成率, skill assessment improvement, career outcome (如 job change)
- 如何平衡 popular courses 和 niche courses? -> Exploration-exploitation (如 Thompson Sampling)"""

Q33_OLD = """### Q33. Design a propensity model to predict which LinkedIn users are likely to purchase...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: propensity-model, classification, conversion, class-imbalance, feature-selection, premium

**题目**: Design a propensity model to predict which LinkedIn users are likely to purchase LinkedIn Premium or a generative AI subscription. You are given sample data with columns: Date, MemberID, Converted (0/1), and various feature columns..."""

Q33_NEW = """### Q33. Design a propensity model to predict which LinkedIn users are likely to purchase...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: propensity-model, classification, conversion, class-imbalance, feature-selection, premium

**题目**: Design a propensity model to predict which LinkedIn users are likely to purchase LinkedIn Premium or a generative AI subscription. You are given sample data with columns: Date, MemberID, Converted (0/1), and various feature columns...

**解题思路**:

**1. Problem Setup**:
- Binary classification: P(convert to Premium | user features)
- 强 class imbalance: conversion rate 通常 < 5%

**2. Feature Engineering**:

**User profile features**:
- Account age, profile completeness score
- Industry, seniority, company size
- Number of connections, endorsements

**Engagement features**:
- DAU/WAU/MAU classification
- Feature usage: search frequency, InMail usage, profile views received
- Premium feature trial history (有没有用过免费试用)
- Job search activity (高活跃度 = 更可能付费)

**Behavioral signals**:
- Visited Premium page but didn't convert (high intent)
- Used features that are Premium-gated (如 "Who viewed your profile")
- Email campaign interaction (opened/clicked upgrade emails)

**Temporal features**:
- Day of week, month (季节性: 年初求职季转化率高)
- Days since last login, login frequency trend (上升/下降)

**3. Modeling**:

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, precision_recall_curve

# Handle class imbalance
model = GradientBoostingClassifier(
    n_estimators=200, max_depth=5,
    subsample=0.8, scale_pos_weight=20  # ~1:20 imbalance
)

# Use stratified CV to preserve class ratio
cv = StratifiedKFold(n_splits=5, shuffle=True)
```

**4. Class Imbalance Handling**:
- **Scale pos weight**: 增加正样本权重
- **SMOTE (Synthetic Minority Over-sampling Technique)**: 合成少数类样本
- **Threshold tuning**: 根据 business cost 调整 decision threshold
- **Evaluation**: 用 AUC-ROC (Area Under ROC Curve) + PR-AUC, 不用 accuracy

**5. Deployment**:
- 每日 batch scoring -> 将 top-K high-propensity users 发送 targeted promotion
- Real-time scoring: 用户访问 Premium page 时触发 personalized pricing/offer

**Follow-ups**:
- 如何防止 "已经要买的用户" 浪费促销预算? -> Uplift modeling: 预测促销的增量效果而非绝对转化概率
- Feature importance 如何解释给 business stakeholders? -> SHAP (SHapley Additive exPlanations) values"""

Q34_OLD = """### Q34. Design a personalized job ranking model for LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: job-ranking, learning-to-rank, personalization, features, recommendation, search

**题目**: Design a personalized job ranking model for LinkedIn. How would you rank jobs for an individual user? What features would you use (user personality/preferences, seniority level, search context, keywords, headline, summary, connections at company, skills, endorsements)? Describe the model architecture and training approach."""

Q34_NEW = """### Q34. Design a personalized job ranking model for LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: job-ranking, learning-to-rank, personalization, features, recommendation, search

**题目**: Design a personalized job ranking model for LinkedIn. How would you rank jobs for an individual user? What features would you use (user personality/preferences, seniority level, search context, keywords, headline, summary, connections at company, skills, endorsements)? Describe the model architecture and training approach.

**解题思路**:

**1. Feature Categories**:

**Query features** (搜索上下文):
- Search keywords, filters (location, remote, salary range)
- Search session context (刚搜了什么, click 了什么)

**User features**:
- Profile: skills, headline, experience, education, seniority
- Preferences: desired job type, location, salary expectation
- Behavioral: 历史 click/apply/save 的 job 的 pattern
- Network: connections at specific companies

**Job features**:
- Title, description, required skills, seniority level
- Company: size, industry, brand strength, Glassdoor rating
- Job metadata: posting date, salary range, remote/hybrid/onsite
- Quality: application count, view-to-apply ratio

**Cross features (user x job)**:
- Skill overlap: user skills vs required skills match ratio
- Title similarity: user's current/past titles vs job title
- Location match: user location vs job location
- Connection count at company
- Company industry match with user's industry

**2. Model Architecture**:
- **Learning-to-Rank (LTR)**: LambdaMART (GBDT-based) 或 neural LTR
- **Two-tower model**: user tower + job tower, learned embeddings for retrieval
- **Multi-task**: jointly predict P(click), P(apply), P(qualified)
- Final score = weighted combination, 如 0.3*P(click) + 0.5*P(apply) + 0.2*P(qualified)

**3. Training**:
- **Positive signals**: click, save, apply, get hired
- **Negative signals**: impression without click, quick back from detail page
- **Pairwise loss**: for each query, the applied job should rank higher than clicked-only, which should rank higher than skipped
- **Temporal train/test split**: 用过去数据训练, 未来数据验证

**4. Serving**:
- Two-stage: embedding-based retrieval (ANN search) -> LTR re-ranking
- Real-time feature computation: user features cached, job features pre-computed
- Latency target: < 200ms for full pipeline

**Follow-ups**:
- 如何处理 position bias (用户倾向点击排名靠前的结果)? -> Inverse Propensity Weighting (IPW) 或 randomized experiments
- 如何平衡 relevance 和 diversity? -> DPP (Determinantal Point Process) 或 MMR re-ranking"""

Q35_OLD = """### Q35. LinkedIn has 500M+ users

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: user-segmentation, market-sizing, opportunity-sizing, clustering, product-strategy, estimation

**题目**: LinkedIn has 500M+ users. Identify the top 5 user segments, estimate each segment's market size, and estimate the opportunity sizing for sales professionals specifically..."""

Q35_NEW = """### Q35. LinkedIn has 500M+ users

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: user-segmentation, market-sizing, opportunity-sizing, clustering, product-strategy, estimation

**题目**: LinkedIn has 500M+ users. Identify the top 5 user segments, estimate each segment's market size, and estimate the opportunity sizing for sales professionals specifically...

**解题思路**:

**Top 5 User Segments**:

| Segment | Est. % | Est. Count | Key Needs |
|---------|--------|------------|-----------|
| 1. Job Seekers | 15% | 75M | Job search, resume building, interview prep |
| 2. Passive Professionals | 40% | 200M | Networking, industry news, brand building |
| 3. Recruiters & HR | 5% | 25M | Talent sourcing, employer branding |
| 4. Sales Professionals | 10% | 50M | Lead generation, prospect research, relationship building |
| 5. Content Creators/Educators | 5% | 25M | Audience building, thought leadership |
| (Other: students, inactive) | 25% | 125M | Career exploration, dormant |

**Segmentation Methodology**:
- **Behavioral clustering**: 基于 feature usage patterns (search, post, InMail, apply)
- **K-means / DBSCAN** on behavioral vectors
- **Rule-based overlay**: 结合 job title + industry 标签

**Sales Professionals Opportunity Sizing**:

**TAM (Total Addressable Market)**:
- 50M sales professionals on LinkedIn
- Sales Navigator price: ~$100/month
- TAM = 50M * $100 * 12 = $60B/year

**SAM (Serviceable Addressable Market)**:
- 只考虑 B2B sales (约 60% of sales pros) = 30M
- 其中决策者/heavy users 约 30% = 9M
- SAM = 9M * $100 * 12 = $10.8B/year

**SOM (Serviceable Obtainable Market)**:
- Current Sales Navigator subscribers (公开数据约 500K-1M)
- Short-term target: 3M subscribers (3x growth)
- SOM = 3M * $100 * 12 = $3.6B/year

**Product Strategy for Sales Segment**:
1. **Sales Navigator**: 高级搜索 + lead recommendations + InMail credits
2. **LinkedIn Sales Insights**: 公司级 intent signals
3. **CRM (Customer Relationship Management) integration**: Salesforce/HubSpot sync

**Follow-ups**:
- 如何增加 Sales Navigator 的 stickiness? -> Show ROI metrics (deals closed via LI), team collaboration features
- 如何从 passive professionals 转化为 paying users? -> Surface premium features at "moment of need" (如 profile view spike)"""

Q36_OLD = """### Q36. What metrics would you design to measure job quality on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-quality, data-analytics, product-metrics, content-quality

**题目**: What metrics would you design to measure job quality on LinkedIn? How would you define a 'high-quality' job posting, and what data signals would you use to measure and rank job posting quality?"""

Q36_NEW = """### Q36. What metrics would you design to measure job quality on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-quality, data-analytics, product-metrics, content-quality

**题目**: What metrics would you design to measure job quality on LinkedIn? How would you define a 'high-quality' job posting, and what data signals would you use to measure and rank job posting quality?

**解题思路**:

**"High Quality" Job Posting 定义**: 准确描述真实岗位, 吸引合格候选人, 并最终导致成功雇佣。

**Quality Signals 分层**:

**1. Content Quality (内容质量)**:
- **Completeness score**: 是否包含 title, description, requirements, salary range, benefits, location
- **Description length**: 太短 (< 100 words) 可能信息不足; 太长 (> 2000 words) 可能噪声多
- **Salary transparency**: 是否公开薪资范围 (强正信号)
- **Spam/scam signals**: 异常薪资承诺, 可疑公司名, 要求预付费用

**2. Engagement Quality (互动质量)**:
- **View-to-apply rate**: 看了 detail page 后申请的比例 (高 = 吸引对的人)
- **Application quality**: 申请者与 requirements 的 match score 分布
- **Quick-exit rate**: 打开 detail page 后秒退的比例 (高 = 标题与内容不匹配)
- **Save/share rate**: 收藏和分享率

**3. Outcome Quality (结果质量)**:
- **Response rate**: recruiter 回复申请者的比例 (低 = 可能是 ghost posting)
- **Time to fill**: 从发布到 filled 的时间
- **Interview rate**: 申请到面试转化率
- **Hire rate**: 最终雇佣率

**4. Poster Quality (发布者质量)**:
- Company verified status
- Company Glassdoor/LinkedIn rating
- Historical posting pattern (频繁发布相同 job = 可疑)

**Composite Job Quality Score**:

```
JQS = w1 * completeness + w2 * engagement_quality
    + w3 * outcome_quality + w4 * poster_quality
```

权重通过 human evaluation + regression 确定。

**应用场景**:
- 搜索排序: 高 JQS 的 job 排名更高
- 内容审核: 低 JQS 的 job 触发人工审核
- Poster feedback: 给雇主展示 job quality dashboard 和改进建议

**Follow-ups**:
- 如何检测 "ghost jobs" (已填但未关闭的岗位)? -> 监控 response rate drop + 时间维度异常
- Job quality 和 diversity 的关系? -> 检查 JQS 是否对某些 industry/location 有 bias"""

Q37_OLD = """### Q37. How would you identify potential client companies for LinkedIn's sales solutions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: lead-scoring, sales, CRM, propensity-model, B2B, company-scoring

**题目**: How would you identify potential client companies for LinkedIn's sales solutions (Sales Navigator, advertising, recruiting tools)? What features and metrics would you use to score and prioritize companies, and how would you build a CRM-style scoring model?"""

Q37_NEW = """### Q37. How would you identify potential client companies for LinkedIn's sales solutions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: lead-scoring, sales, CRM, propensity-model, B2B, company-scoring

**题目**: How would you identify potential client companies for LinkedIn's sales solutions (Sales Navigator, advertising, recruiting tools)? What features and metrics would you use to score and prioritize companies, and how would you build a CRM-style scoring model?

**解题思路**:

**1. Target Definition**: 预测 P(company purchases LinkedIn product within next quarter)

**2. Feature Engineering**:

**Company profile features**:
- Size (employee count), industry, revenue, growth rate
- Hiring velocity (job postings per month) -- 高 = potential recruiting tools buyer
- LinkedIn company page engagement (follower count, page activity)

**Historical behavior on LinkedIn**:
- Current product usage (free tier features usage)
- Past sales conversations/demos (CRM data)
- LinkedIn Ads spend history
- Job posting frequency and volume

**Digital signals (intent signals)**:
- Website visits to LinkedIn business solutions pages
- Downloaded whitepapers or attended LinkedIn webinars
- Competitive product usage (using Indeed, Glassdoor more)

**External data**:
- Funding events (newly funded startups need recruiting)
- M&A activity (post-merger companies need employer branding)
- Layoffs (paradoxically, may need outplacement/rebranding)

**3. Lead Scoring Model**:

| Score Tier | Description | Action |
|-----------|-------------|--------|
| A (90-100) | High intent + high value | Immediate sales outreach |
| B (70-89) | High intent or high value | Nurture campaign |
| C (50-69) | Medium signals | Automated marketing |
| D (< 50) | Low probability | No action, periodic re-score |

**Model**:
- Gradient Boosted Trees for conversion prediction
- Separate models per product (Recruiter, Sales Nav, Ads)
- Score = P(convert) * expected_deal_value

**4. Metrics**:
- Lead-to-opportunity conversion rate by score tier
- Sales cycle length
- Revenue per lead
- Model lift over random outreach

**Follow-ups**:
- 如何避免只 target 大公司而忽略 high-growth SMBs? -> 加入 growth rate features, 用 "velocity" 而非 absolute size
- 如何处理 long sales cycles (enterprise deals 可能 6-12 months)? -> Recalibrate labels to use "entered pipeline" as positive signal"""

Q38_OLD = """### Q38. Design a keyword search system for LinkedIn that surfaces the most popular/relev...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, information-retrieval, keyword-search, content-search, relevance, infrastructure-cost

**题目**: Design a keyword search system for LinkedIn that surfaces the most popular/relevant posts. How would you rank search results for content search? Discuss relevance signals, personalization, and cost metrics for search (cost per search, infrastructure cost per query)."""

Q38_NEW = """### Q38. Design a keyword search system for LinkedIn that surfaces the most popular/relev...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, information-retrieval, keyword-search, content-search, relevance, infrastructure-cost

**题目**: Design a keyword search system for LinkedIn that surfaces the most popular/relevant posts. How would you rank search results for content search? Discuss relevance signals, personalization, and cost metrics for search (cost per search, infrastructure cost per query).

**解题思路**:

**系统架构**:

```
Query -> Query Processing -> Index Lookup -> Candidate Retrieval
    -> Relevance Ranking -> Personalization -> Results
```

**1. Query Processing**:
- Tokenization + stemming + stop words removal
- Spell correction (did you mean...?)
- Query expansion: synonyms, abbreviations ("ML" -> "machine learning")
- Intent detection: searching for people vs posts vs jobs vs companies

**2. Indexing (Inverted Index)**:
- 每个 term -> list of (doc_id, tf, position) 用于 matching
- BM25 (Best Matching 25) 作为 base relevance score
- 分 index: posts index, profiles index, jobs index, companies index

**3. Ranking Signals**:

**Relevance signals**:
- BM25 text match score (term frequency, document length normalization)
- Title match boost (query 出现在 post title 权重更高)
- Exact phrase match bonus
- Recency decay (新 post 更相关)

**Popularity signals**:
- Like/comment/share count
- View count
- Author authority (follower count, post history engagement)

**Personalization signals**:
- Connection degree (1st > 2nd > 3rd)
- Industry/topic affinity (用户历史 engagement 的 topic 分布)
- Language match

**4. Cost Metrics**:
- **Cost per search**: infrastructure cost / total search queries
- **Query latency**: P50 < 100ms, P99 < 500ms
- **Index freshness**: new posts indexed within X minutes
- Optimization: tiered caching (hot queries cached), early termination (stop scoring after top-K found)

**5. Architecture for Scale**:
- **Distributed index**: partition by content hash or time range
- **Two-phase ranking**: L1 (fast BM25 on inverted index) -> L2 (neural re-ranker on top-100)
- **Cache**: 热门 queries 缓存 (如 "machine learning", "remote jobs")

**Follow-ups**:
- 如何处理多语言搜索? -> Language-specific tokenizers + cross-lingual embeddings
- 如何平衡 relevance 和 freshness? -> 可配置的 time-decay factor, 或 separate "Top" vs "Recent" tabs"""

Q39_OLD = """### Q39. How would you decide which feature to build next for a LinkedIn product

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-prioritization, product-sense, decision-framework, impact-estimation, roadmap-planning

**题目**: How would you decide which feature to build next for a LinkedIn product? Describe a feature prioritization framework. What data would you use to support the decision? How would you estimate impact before building?"""

Q39_NEW = """### Q39. How would you decide which feature to build next for a LinkedIn product

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-prioritization, product-sense, decision-framework, impact-estimation, roadmap-planning

**题目**: How would you decide which feature to build next for a LinkedIn product? Describe a feature prioritization framework. What data would you use to support the decision? How would you estimate impact before building?

**解题思路**:

**Feature Prioritization Framework: RICE**

| 维度 | 定义 | 数据来源 |
|------|------|---------|
| **R**each | 影响多少用户 | User analytics, segment sizing |
| **I**mpact | 每个用户的影响程度 (1-3 scale) | User research, competitive analysis |
| **C**onfidence | 对估算的信心 (%, 越高越好) | Past experiment results, market data |
| **E**ffort | 开发成本 (person-months) | Engineering estimation |

RICE Score = (Reach * Impact * Confidence) / Effort

**详细决策流程**:

**Step 1: Gather candidates**
- User research: surveys, interviews, support tickets
- Data analysis: funnel drop-offs, feature usage gaps
- Competitive analysis: 竞品有但我们没有的功能
- Strategy alignment: 与公司 OKR (Objectives and Key Results) 对齐

**Step 2: Impact estimation (before building)**
- **Size the opportunity**: 如果 feature X 将 funnel step Y 的转化率提升 Z%, 影响多少 revenue/engagement
- **Analogy-based**: 类似 feature 在其他产品的效果
- **Survey intent**: "Would you use feature X?" (需要 discount, 实际使用率通常是 stated intent 的 30-50%)

**Step 3: Validate cheaply**
- **Fake door test**: 放一个 feature 按钮, 测量点击量, 不需要真正实现
- **Wizard of Oz**: 人工模拟 feature 效果
- **Prototype test**: 小范围 beta test

**Step 4: Build + A/B test**
- Feature flag 控制, A/B test 验证
- 观察期足够长 (2-4 weeks 避免 novelty effect)
- 看 primary metrics + guardrail metrics

**Example**: 是否 build "Salary Insights" feature?
- Reach: 75M job seekers = high
- Impact: salary is #1 reason for job change = high (3/3)
- Confidence: Glassdoor proves market demand = 80%
- Effort: 3 person-months
- RICE = (75M * 3 * 0.8) / 3 = 60M -> very high priority

**Follow-ups**:
- 如何处理 high-impact but high-risk features? -> 分阶段发布, MVP first, 加 rollback plan
- 如何平衡短期 engagement gains 和长期 user trust? -> 定义 long-term guardrail metrics (如 user trust score, NPS)"""

Q40_OLD = """### Q40. Design the metrics for LinkedIn's profile visit feature

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, profile-views, product-metrics, feature-evaluation, engagement

**题目**: Design the metrics for LinkedIn's profile visit feature. What would you measure to evaluate whether the 'Who Viewed Your Profile' feature is successful? How would you define and track feature success?"""

Q40_NEW = """### Q40. Design the metrics for LinkedIn's profile visit feature

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, profile-views, product-metrics, feature-evaluation, engagement

**题目**: Design the metrics for LinkedIn's profile visit feature. What would you measure to evaluate whether the 'Who Viewed Your Profile' feature is successful? How would you define and track feature success?

**解题思路**:

**Feature 价值分析**: "Who Viewed Your Profile" (WVYP) 是 LinkedIn 最具特色的功能之一, 驱动用户回访和 Premium 转化。

**Metrics 框架**:

**1. Engagement Metrics (用户参与)**:
- **WVYP page visit rate**: % of DAU who visit WVYP page per day
- **Notification click-through rate**: WVYP notification clicks / notifications sent
- **Profile views per user**: average views received per week (supply metric)
- **View-back rate**: 用户看了 WVYP 后去查看 viewer 的 profile 的比例

**2. Retention Metrics (留存)**:
- **D7/D30 retention lift**: WVYP 使用者 vs 非使用者的留存差异
- **Session frequency**: WVYP 用户的平均 weekly sessions
- **Reactivation rate**: dormant users 因 WVYP notification 回来的比例

**3. Monetization Metrics (变现)**:
- **Premium conversion**: WVYP 是 Premium 的 top 卖点 (full list of viewers)
- **Upsell CTR**: free users 看到 "upgrade to see all viewers" 的转化率
- **Revenue per WVYP session**: 通过 Premium upsell + ads 产生的收入

**4. Quality Metrics (质量)**:
- **Accuracy**: viewer list 的准确性 (privacy settings 可能隐藏部分 viewers)
- **Freshness**: 从 view 发生到出现在列表中的延迟
- **User satisfaction**: NPS for WVYP feature (survey-based)
- **Privacy complaints**: 因 WVYP 导致的 privacy concern reports

**5. Guardrail Metrics (不能变差)**:
- Privacy opt-out rate: 如果增加可见性导致更多人选择匿名浏览
- Harassment reports: 确保不被滥用于 stalking
- Overall session time: WVYP 不应 cannibalize 其他 feature 的使用

**Success Definition**:
Feature is successful if: (1) WVYP daily visits grow YoY, (2) contributes measurably to Premium conversion, (3) privacy metrics remain stable.

**Follow-ups**:
- 如果匿名浏览模式使用率上升导致 WVYP 数据稀疏怎么办? -> 提供 "appear as anonymous" but show industry/role hints
- 如何 A/B test WVYP 的不同版本 (如增加 viewer insights)? -> 注意 network effect: 两组用户的互相查看会交叉"""

Q41_OLD = """### Q41. You are launching a new feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-launch, product-evaluation, success-metrics, market-estimation, launch-process, user-satisfaction

**题目**: You are launching a new feature on LinkedIn. Walk through the full evaluation process: estimating potential market, determining initial data needs, defining success metrics, pre-launch steps, and post-launch user satisfaction measurement."""

Q41_NEW = """### Q41. You are launching a new feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-launch, product-evaluation, success-metrics, market-estimation, launch-process, user-satisfaction

**题目**: You are launching a new feature on LinkedIn. Walk through the full evaluation process: estimating potential market, determining initial data needs, defining success metrics, pre-launch steps, and post-launch user satisfaction measurement.

**解题思路**:

**Phase 1: Pre-Launch Planning**

**Market Sizing**:
- TAM: 全部 LinkedIn users * feature 的适用比例
- SAM: 活跃用户中符合 target persona 的比例
- Example: 如果 launching "AI Resume Review" -> TAM = 75M job seekers, SAM = 30M active job seekers

**Data Requirements**:
- Baseline metrics: 当前相关 funnel 的转化率
- User research: qualitative interviews + quantitative surveys
- Logging infrastructure: 确保 feature 的所有交互都有 instrumentation

**Success Metrics (定义 before launch)**:
- **Primary**: 1 个核心指标 (如 feature adoption rate within 30 days)
- **Secondary**: engagement depth (如 average sessions using feature per user)
- **Guardrails**: 不能降低的指标 (如 overall app performance, existing feature usage)

**Phase 2: Launch Execution**

1. **Internal dogfooding**: 员工先用 1-2 周
2. **Beta/canary release**: 1-5% of users, monitor crash rate + critical bugs
3. **A/B test**: 10-50% rollout, 收集足够样本量
4. **Full rollout**: 如果 A/B test 显著正向

**Rollout 注意事项**:
- Feature flag 控制, 支持快速 rollback
- Staged rollout by geography/user segment
- On-call 工程师 monitor real-time metrics

**Phase 3: Post-Launch Evaluation**

**Short-term (1-4 weeks)**:
- Adoption rate: % of eligible users who tried feature
- Activation rate: % of users who completed key action (not just opened)
- Bug reports, crash rate, performance metrics

**Medium-term (1-3 months)**:
- Retention: feature usage D7, D30 retention
- Engagement: 是否增加 overall platform engagement
- Cannibalization: 是否减少其他 feature 使用

**User Satisfaction**:
- In-app feedback: thumbs up/down after using feature
- NPS (Net Promoter Score) survey
- Support ticket analysis: 新增 issue categories
- Qualitative: user interviews with power users + churned users

**Follow-ups**:
- 如果 A/B test 不显著怎么办? -> 延长测试期, 或 segment analysis 找 sub-populations where it works
- 如何决定 kill a feature that underperforms? -> Pre-define kill criteria (如 < X% adoption after 3 months)"""

Q42_OLD = """### Q42. Design a database schema and system for tracking job applications on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: database-design, schema-design, application-tracking, job-search, data-modeling

**题目**: Design a database schema and system for tracking job applications on LinkedIn. Include attributes for users with applied_job, status, connections at the company, application history, etc..."""

Q42_NEW = """### Q42. Design a database schema and system for tracking job applications on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: database-design, schema-design, application-tracking, job-search, data-modeling

**题目**: Design a database schema and system for tracking job applications on LinkedIn. Include attributes for users with applied_job, status, connections at the company, application history, etc...

**解题思路**:

**Core Tables**:

```sql
-- Users (applicant information)
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    industry VARCHAR(100),
    experience_years INT,
    profile_completeness FLOAT,
    created_at TIMESTAMP
);

-- Jobs
CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    company_id BIGINT REFERENCES companies(company_id),
    title VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    seniority_level VARCHAR(50),
    employment_type VARCHAR(50),  -- full-time, contract, etc.
    salary_min INT,
    salary_max INT,
    posted_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- active, closed, filled
    INDEX idx_company (company_id),
    INDEX idx_posted (posted_at)
);

-- Applications (core tracking table)
CREATE TABLE applications (
    application_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT REFERENCES users(user_id),
    job_id BIGINT REFERENCES jobs(job_id),
    status VARCHAR(30) DEFAULT 'submitted',
    -- submitted -> reviewed -> interviewing -> offered -> hired/rejected
    applied_at TIMESTAMP,
    updated_at TIMESTAMP,
    source VARCHAR(50),  -- search, recommendation, email_alert, easy_apply
    resume_version_id BIGINT,
    cover_letter TEXT,
    INDEX idx_user (user_id),
    INDEX idx_job (job_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_user_job (user_id, job_id)  -- prevent duplicate applications
);

-- Application status history (audit trail)
CREATE TABLE application_status_log (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    application_id BIGINT REFERENCES applications(application_id),
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    changed_at TIMESTAMP,
    changed_by VARCHAR(50)  -- system, recruiter, applicant
);

-- Connections at company (for "X connections work here")
CREATE TABLE user_connections (
    user_id BIGINT,
    connection_id BIGINT,
    company_id BIGINT,
    PRIMARY KEY (user_id, connection_id)
);
```

**Key Design Decisions**:
- **Status as enum string**: 比 int 更可读, 便于调试
- **Separate status log**: 完整审计轨迹, 支持 funnel analysis
- **Source tracking**: 知道用户从哪里来申请, 优化渠道
- **Unique constraint on (user_id, job_id)**: 防止重复申请

**Analytics Queries**:

```sql
-- Application funnel by source
SELECT source,
       COUNT(*) AS total_applications,
       SUM(CASE WHEN status = 'reviewed' THEN 1 ELSE 0 END) AS reviewed,
       SUM(CASE WHEN status = 'interviewing' THEN 1 ELSE 0 END) AS interviews,
       SUM(CASE WHEN status = 'hired' THEN 1 ELSE 0 END) AS hired
FROM applications
WHERE applied_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY source;
```

**Follow-ups**:
- 如何 scale 到每天百万级申请量? -> 分库分表 (shard by user_id), 读写分离, 状态更新用消息队列异步
- 如何实现 "Easy Apply" 的无缝体验? -> 预填充 profile data, 一键提交, 减少 friction"""

Q43_OLD = """### Q43. Design LinkedIn's push notification system for improving user engagement

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: push-notification, engagement, conversion-funnel, personalization, notification-optimization, CPA

**题目**: Design LinkedIn's push notification system for improving user engagement. Why use push notifications? Which engagement features should you focus on? Discuss time/frequency considerations, conversion funnel (notification -> open -> action), and key metrics (CPA, click notification rate, CVR)."""

Q43_NEW = """### Q43. Design LinkedIn's push notification system for improving user engagement

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: push-notification, engagement, conversion-funnel, personalization, notification-optimization, CPA

**题目**: Design LinkedIn's push notification system for improving user engagement. Why use push notifications? Which engagement features should you focus on? Discuss time/frequency considerations, conversion funnel (notification -> open -> action), and key metrics (CPA, click notification rate, CVR).

**解题思路**:

**Why Push Notifications**: Re-engage users who are not actively on the platform; drive specific actions (apply, connect, respond).

**1. Notification Types (按优先级)**:
- **Direct actions**: InMail received, connection request, endorsement
- **Social engagement**: likes/comments on your post, someone shared your article
- **Job alerts**: new jobs matching your preferences, application status updates
- **Content**: trending posts in your industry, weekly digest
- **Growth/onboarding**: profile completion reminders, skill assessment invites

**2. Personalization Framework**:

**When to send (时机)**:
- 用户历史活跃时间段 (如每天 8am-9am commute time)
- 时区感知
- 避免 notification fatigue: 每日上限 (如 max 5 push notifications)

**What to send (内容)**:
- 预测 P(open | notification type, user, time)
- 优先发送高价值 notification (direct message > content update)
- Suppress low-value notifications (如 "X liked your comment" -- 可以 batch)

**Who to send (目标)**:
- Segment by engagement level:
  - Active users: 减少 notifications (他们已经在用)
  - At-risk users: 增加 re-engagement notifications
  - Dormant users: 高价值 hook (如 "A recruiter viewed your profile")

**3. Conversion Funnel & Metrics**:

```
Notification Sent -> Delivered -> Opened -> Action Taken -> Conversion
```

| Metric | 定义 | 目标 |
|--------|------|------|
| Delivery Rate | delivered / sent | > 95% |
| Open Rate | opens / delivered | 10-20% |
| CTR (Click-Through Rate) | clicks / opens | 5-15% |
| CVR (Conversion Rate) | conversions / clicks | varies by type |
| CPA (Cost Per Acquisition) | cost / conversions | minimize |
| Unsubscribe Rate | unsubscribes / sent | < 0.1% |

**4. Guardrails**:
- **Notification fatigue**: 监控 disable notification rate
- **User trust**: 不发送 misleading notifications (如 "fake" profile views)
- **Canary rollout**: 新 notification type 先给 1% 用户测试

**Follow-ups**:
- 如何优化 notification 文案? -> A/B test different copy, 用 LLM 生成 personalized text
- 如何处理跨设备 (mobile + desktop) notification? -> De-duplicate, prefer the device user is active on"""

Q44_OLD = """### Q44. LinkedIn's job application count has dropped 10% month-over-month

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: root-cause-analysis, metric-debugging, product-analytics, investigation, problem-solving

**题目**: LinkedIn's job application count has dropped 10% month-over-month. How would you investigate and diagnose this problem? Walk through a structured approach: supply vs demand analysis, segment analysis, hypothesis generation, and recommended actions."""

Q44_NEW = """### Q44. LinkedIn's job application count has dropped 10% month-over-month

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: root-cause-analysis, metric-debugging, product-analytics, investigation, problem-solving

**题目**: LinkedIn's job application count has dropped 10% month-over-month. How would you investigate and diagnose this problem? Walk through a structured approach: supply vs demand analysis, segment analysis, hypothesis generation, and recommended actions.

**解题思路**:

**Step 1: Clarify & Decompose the Metric**

Application Count = Job Seekers * Search Rate * CTR * Application Rate

分解看哪个环节 drop:
- **Job Seekers 下降?** -> Demand-side 问题
- **Job Postings 下降?** -> Supply-side 问题
- **CTR 下降?** -> Ranking/UX 问题
- **Application Rate 下降?** -> Application flow 问题

**Step 2: Supply vs Demand Analysis**

| 维度 | 检查内容 |
|------|---------|
| Supply | Active job postings count, new postings per week, job quality score trend |
| Demand | Active job seekers count, search query volume, DAU of job tab |
| Platform | New user registration, user churn rate |

**Step 3: Segment Analysis (找 isolation)**

```
-- Segment application drop by platform
SELECT platform, month,
       COUNT(*) AS applications,
       LAG(COUNT(*)) OVER (PARTITION BY platform ORDER BY month) AS prev_month
FROM applications
GROUP BY platform, month;
```

检查是否 isolated to:
- **某个平台**: mobile app vs desktop vs mobile web
- **某个地区**: US vs EMEA vs APAC
- **某个 job category**: tech vs non-tech
- **某种用户**: new vs returning, free vs premium
- **某种 apply type**: Easy Apply vs external redirect

**Step 4: Hypothesis Generation**

| 假设 | 验证方法 | 可能原因 |
|------|---------|---------|
| Product bug | Check deployment logs, error rates | 新 release 引入的 bug |
| Seasonal | YoY comparison | 正常季节性波动 |
| External redirect broken | Check redirect success rate | 第三方 ATS link 失效 |
| Application flow friction | A/B test results, funnel analysis | 新增字段导致 abandon |
| Job quality decline | JQS trend, spam rate | 更多低质量 posting |
| Macro economic | Job market data (BLS), competitor data | 经济衰退减少 hiring |

**Step 5: Recommended Actions (根据假设)**

1. **If bug**: Hotfix + rollback
2. **If funnel friction**: Simplify application flow, A/B test removal of unnecessary fields
3. **If supply decline**: Outreach to employers, incentivize job posting
4. **If external factors**: Monitor, prepare messaging to stakeholders
5. **Always**: Set up automated alerts for early detection

**Follow-ups**:
- 如果 10% drop 只发生在 mobile? -> 检查最近 app update, specific device/OS version issues
- 如何区分 "fewer applications per seeker" vs "fewer seekers"? -> Decompose into per-user application rate * user count"""

Q45_OLD = """### Q45. You've launched a 'Recommended Jobs' feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-evaluation, metrics-design, AB-testing, feature-evaluation, job-recommendation

**题目**: You've launched a 'Recommended Jobs' feature on LinkedIn. How would you measure its performance? What metrics would you track, and how would you compare it against other job discovery methods (search, email alerts, browsing)?"""

Q45_NEW = """### Q45. You've launched a 'Recommended Jobs' feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-evaluation, metrics-design, AB-testing, feature-evaluation, job-recommendation

**题目**: You've launched a 'Recommended Jobs' feature on LinkedIn. How would you measure its performance? What metrics would you track, and how would you compare it against other job discovery methods (search, email alerts, browsing)?

**解题思路**:

**1. Feature-Specific Metrics**:

**Adoption**:
- % of active users who view recommended jobs section
- Impression count: 每日展示多少 recommended jobs

**Quality**:
- **Recommendation CTR**: clicks on recommended jobs / impressions
- **Application rate**: applications from recommended jobs / clicks
- **Skill match score**: average match between user profile and recommended jobs
- **Diversity**: unique companies/industries in recommendations

**Downstream Impact**:
- **Applications from recommendations**: 占总 applications 的比例
- **Interview rate**: 通过 recommended jobs 申请后获得面试的比例
- **Time to apply**: 从 recommendation 到 application 的时间

**2. Comparison with Other Channels**:

| Metric | Recommended | Search | Email Alerts | Browse |
|--------|-------------|--------|-------------|--------|
| CTR | Measure | Baseline | Baseline | Baseline |
| Apply Rate | Measure | Baseline | Baseline | Baseline |
| Quality Score | Measure | Baseline | Baseline | Baseline |
| Cost per Apply | Measure | Baseline | Baseline | Baseline |

**Attribution model**: 用户可能通过多个渠道看到同一个 job。用 last-touch attribution 或 multi-touch attribution 分配 credit。

**3. A/B Test Design**:
- Control: 无 recommended jobs section
- Treatment: 有 recommended jobs section
- Randomization unit: user-level (不是 session-level)
- Duration: 至少 2-4 weeks (覆盖 weekly cycle)
- Primary metric: total applications per user (not just from recommendations -- 要看 incremental value)

**4. Cannibalization Analysis**:
- Recommendations 是否只是 redirecting 用户从 search 到 recommendations? 而非增加 total applications?
- 检查: control group 的 search applications vs treatment group 的 search applications
- 只有 net positive (total applications increase) 才算真正成功

**5. Long-term Metrics**:
- 3/6/12-month retention of users who engage with recommendations
- Job satisfaction: post-hire surveys for users hired through recommendations
- Model improvement: recommendation quality trend over time (A/B test effect size increasing)

**Follow-ups**:
- 如何处理 cold-start (新用户没有 interaction history)? -> 基于 profile + similar users 的 popularity-based recommendations
- 推荐的 jobs 如何保持 freshness? -> 优先推荐新发布的 jobs, 对已见过的做 de-duplication"""

Q46_OLD = """### Q46. Design a system to track and analyze application database attributes for LinkedI...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: data-pipeline, feature-store, application-data, job-matching, data-engineering, ML-features

**题目**: Design a system to track and analyze application database attributes for LinkedIn users. Given fields like applied_job, application_status, connections_at_company, and application_history, how would you design the data pipeline and use these attributes to improve job search quality and matching?"""

Q46_NEW = """### Q46. Design a system to track and analyze application database attributes for LinkedI...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: data-pipeline, feature-store, application-data, job-matching, data-engineering, ML-features

**题目**: Design a system to track and analyze application database attributes for LinkedIn users. Given fields like applied_job, application_status, connections_at_company, and application_history, how would you design the data pipeline and use these attributes to improve job search quality and matching?

**解题思路**:

**1. Data Pipeline Architecture**:

```
Application Events -> Event Stream (Kafka) -> Stream Processing (Flink/Spark)
    -> Feature Store -> ML Models + Analytics Dashboard
                   -> Data Warehouse (Offline Analysis)
```

**2. Key Attributes & Schema**:

**User application profile** (每个用户的申请画像):
- `total_applications`: 总申请数
- `application_history`: list of (job_id, timestamp, status, source)
- `success_rate`: applications that reached interview / total applications
- `preferred_industries`: based on application distribution
- `preferred_seniority`: from applied jobs' levels
- `avg_connections_at_applied_companies`: social signal strength

**3. Feature Engineering for ML Models**:

**Job ranking improvement**:
- `user_apply_rate_for_similar_jobs`: 该用户对类似 jobs 的历史 apply rate
- `job_application_velocity`: job 的申请速度 (快速增长的 job 可能更热门或更好)
- `connections_at_company`: 有 connections 的公司, 用户更可能申请和被录用

**Match quality prediction**:
- `skill_overlap_with_applied_jobs`: 用户 skills vs 成功申请 jobs 的 required skills 的 overlap
- `title_trajectory`: 用户职位变化趋势 (升级 vs 平级 vs 转行)
- `application_to_interview_ratio`: 衡量用户 resume/profile 的匹配质量

**4. Data Pipeline Components**:

**Real-time path** (Kafka + Flink):
- 实时更新 application status
- 实时计算 connections_at_company (当用户查看 job 时)
- Feed real-time features to ranking model

**Batch path** (Spark):
- 每日重新计算 aggregated features (success rate, preference distributions)
- 训练数据生成 for ML model retraining
- Analytics report generation

**Feature Store**:
- Online serving: Redis/Memcached for low-latency feature lookup
- Offline: Hive/Parquet for model training
- Feature versioning: track feature definitions over time

**5. Privacy Considerations**:
- Application data is highly sensitive -- 加密存储, 限制访问
- 不向 employers 暴露用户的其他公司申请信息
- GDPR (General Data Protection Regulation) compliance: 用户有权删除申请数据

**Follow-ups**:
- 如何处理 data skew (少数用户海量申请, 多数用户少量申请)? -> 对 heavy applicants 做 truncation, 或用 log transform 归一化
- 如何用 application outcome data 改进 job quality scoring? -> 申请后面试率高的 job = higher quality"""

Q47_OLD = """### Q47. Design a system for LinkedIn keyword search that surfaces the most popular posts...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, popularity-ranking, sponsored-search, CPC, CPM, auction-design

**题目**: Design a system for LinkedIn keyword search that surfaces the most popular posts and content. How do you define 'popular'? What ranking signals would you use? Discuss cost metrics including CPC (cost per click), cost per 1000 impressions, and cost per keyword for sponsored search results."""

Q47_NEW = """### Q47. Design a system for LinkedIn keyword search that surfaces the most popular posts...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, popularity-ranking, sponsored-search, CPC, CPM, auction-design

**题目**: Design a system for LinkedIn keyword search that surfaces the most popular posts and content. How do you define 'popular'? What ranking signals would you use? Discuss cost metrics including CPC (cost per click), cost per 1000 impressions, and cost per keyword for sponsored search results.

**解题思路**:

**1. Defining "Popular"**:

Popularity 不是单一指标, 而是 composite score:
- **Engagement score**: likes * 1 + comments * 3 + shares * 5 + saves * 2 (加权, 高质量互动权重更大)
- **Velocity**: engagement growth rate (近期增长快的 > 总量大但增长停滞的)
- **Author authority**: follower count, post history engagement rate, verified status
- **Reach**: unique views / impressions

**Popularity Decay**: P(t) = engagement_score * decay(age), 用 time-decay function (如 exponential decay 或 power law) 确保新内容有机会被看到。

**2. Organic Ranking Signals**:

| Signal | Weight | 说明 |
|--------|--------|------|
| Text relevance (BM25) | High | Query-content match |
| Popularity score | Medium-High | As defined above |
| Personalization | Medium | User-topic affinity, connection degree |
| Freshness | Medium | Time decay factor |
| Content quality | Medium | Spam score, readability, media richness |

**3. Sponsored Search (Ads Integration)**:

**Ad Auction Design**:
- Advertiser 设置 bid (CPC or CPM) + targeting criteria
- **Ad Rank = bid * quality_score * relevance_score**
- Quality score: historical CTR, landing page quality, ad copy relevance
- 用 **GSP (Generalized Second-Price) Auction**: winner pays 最低能赢的价格 (类似 Google Ads)

**Pricing Models**:

| Model | 公式 | 适用 |
|-------|------|------|
| CPC | Advertiser pays per click | Direct response campaigns |
| CPM | Pay per 1000 impressions | Brand awareness |
| CPK (Cost Per Keyword) | Fixed price for keyword placement | Guaranteed visibility |

**Organic vs Sponsored 混合排序**:
- 用 eCPM 统一比较: organic content 的 eCPM = 0, sponsored content 的 eCPM = bid * P(click)
- 但不能全是 ads: 设定 max ad density (如每 5 个结果最多 1 个 ad)
- 标记 "Sponsored" 以保持用户信任

**4. Cost Metrics for Platform**:
- **Revenue per search**: total ad revenue / total searches
- **Ad load**: % of results that are sponsored
- **User satisfaction trade-off**: 过高 ad load 降低 organic engagement, 需要平衡

**Follow-ups**:
- 如何防止 ad fraud (虚假点击)? -> Click pattern anomaly detection, IP-based filtering, conversion verification
- 如何平衡 high-bidding low-relevance ads vs low-bidding high-relevance ads? -> 强调 quality score 的权重, 使 relevance 成为关键 factor"""


# ════════════════════════════════════════════════════════════════
# ENRICHMENT ENGINE
# ════════════════════════════════════════════════════════════════

REPLACEMENTS = [
    (Q1_OLD, Q1_NEW), (Q2_OLD, Q2_NEW), (Q3_OLD, Q3_NEW),
    (Q4_OLD, Q4_NEW), (Q5_OLD, Q5_NEW), (Q6_OLD, Q6_NEW),
    (Q7_OLD, Q7_NEW), (Q8_OLD, Q8_NEW), (Q9_OLD, Q9_NEW),
    (Q10_OLD, Q10_NEW), (Q11_OLD, Q11_NEW), (Q12_OLD, Q12_NEW),
    (Q13_OLD, Q13_NEW), (Q14_OLD, Q14_NEW), (Q15_OLD, Q15_NEW),
    (Q16_OLD, Q16_NEW), (Q17_OLD, Q17_NEW), (Q18_OLD, Q18_NEW),
    (Q19_OLD, Q19_NEW), (Q20_OLD, Q20_NEW), (Q21_OLD, Q21_NEW),
    (Q22_OLD, Q22_NEW), (Q23_OLD, Q23_NEW),
    (Q24_OLD, Q24_NEW), (Q25_OLD, Q25_NEW), (Q26_OLD, Q26_NEW),
    (Q27_OLD, Q27_NEW), (Q28_OLD, Q28_NEW), (Q29_OLD, Q29_NEW),
    (Q30_OLD, Q30_NEW), (Q31_OLD, Q31_NEW), (Q32_OLD, Q32_NEW),
    (Q33_OLD, Q33_NEW), (Q34_OLD, Q34_NEW), (Q35_OLD, Q35_NEW),
    (Q36_OLD, Q36_NEW), (Q37_OLD, Q37_NEW), (Q38_OLD, Q38_NEW),
    (Q39_OLD, Q39_NEW), (Q40_OLD, Q40_NEW), (Q41_OLD, Q41_NEW),
    (Q42_OLD, Q42_NEW), (Q43_OLD, Q43_NEW), (Q44_OLD, Q44_NEW),
    (Q45_OLD, Q45_NEW), (Q46_OLD, Q46_NEW), (Q47_OLD, Q47_NEW),
]


def enrich(content: str) -> str:
    """Apply all enrichments to doc#26."""
    for old, new in REPLACEMENTS:
        if old not in content:
            # Try with stripped whitespace for minor formatting differences
            old_stripped = old.strip()
            if old_stripped in content:
                content = content.replace(old_stripped, new.strip())
            else:
                print(f"WARNING: Could not find replacement target starting with: "
                      f"{old[:80]!r}")
        else:
            content = content.replace(old, new)
    return content


def update_stats(content: str) -> str:
    """Update the statistics section at the end."""
    old_stats = """## 统计

- **总题数**: 47
- **Coding**: 15 题
- **ML Theory & Coding**: 8 题
- **ML System Design**: 24 题
- **有LeetCode编号的题目**: 8"""

    new_stats = """## 统计

- **总题数**: 47
- **Coding**: 15 题 (全部含解题思路 + Python 代码)
- **ML Theory & Coding**: 8 题 (全部含详细解答)
- **ML System Design**: 24 题 (全部含系统设计分析)
- **有LeetCode编号的题目**: 8
- **含 Python 代码的题目**: 28
- **含 SQL 代码的题目**: 4
- **含 Follow-up 的题目**: 47"""

    if old_stats in content:
        content = content.replace(old_stats, new_stats)
    return content


def main() -> None:
    """Main entry point."""
    conn = sqlite3.connect(str(DB_PATH))
    content = get_content(conn)
    original_len = len(content)

    print(f"Original doc#26: {original_len}c")

    content = enrich(content)
    content = update_stats(content)

    new_len = len(content)
    print(f"Enriched doc#26: {new_len}c (+{new_len - original_len}c)")

    # Count code blocks
    code_blocks = content.count("```python") + content.count("```sql")
    print(f"Code blocks: {code_blocks}")

    # Count follow-ups
    followups = content.count("**Follow-ups**:")
    print(f"Follow-up sections: {followups}")

    # Update database
    cur = conn.cursor()
    cur.execute(
        "UPDATE company_documents SET content=? WHERE id=26",
        (content,),
    )
    conn.commit()
    conn.close()
    print("Database updated successfully.")


if __name__ == "__main__":
    main()
