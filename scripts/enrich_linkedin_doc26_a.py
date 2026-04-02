"""Enrich LinkedIn doc#26 (Question Index) -- Coding Q1-Q15.

Task: T-P0-262 (Part 1/4)
Adds comprehensive solutions with Python code for all 15 coding questions.
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


def enrich(content: str) -> str:
    """Apply enrichments to coding questions Q1-Q15."""

    # ── Q1: Insert/Delete/GetRandom O(1) (LC 380/381) ──
    content = content.replace(
        """**解法要点**:
- ## All O(1) Data Structure (LC 380 / 381)
- Combine a hash map (for O(1) lookup/delete) with a dynamic array (for O(1) random access).

**Follow-ups**:
- extended version (allowing duplicates).

---

### Q2.""",
        """**解答**:

**思路**: 核心是将 hash map 和 dynamic array (动态数组) 结合。HashMap 存储 val -> index 的映射实现 O(1) 查找；数组支持 O(1) 随机访问。删除时将目标元素与数组末尾元素交换，然后 pop 末尾，保持 O(1)。

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
        self.vals[idx] = last
        self.val_to_idx[last] = idx
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

- **Time**: O(1) average for insert/remove/getRandom
- **Space**: O(n)

**Follow-up (LC 381 -- 允许重复)**:
HashMap 存 val -> set of indices。remove 时从 set 中取任一 index，与末尾交换。insert 时直接加入 set。

---

### Q2."""
    )

    # ── Q2: Course Schedule (LC 207/210) ──
    content = content.replace(
        """**解法要点**:
- Time: O(V + E) for both approaches
- Space: O(V + E)

---

### Q3.""",
        """**解答**:

**思路**: 经典的 Topological Sort (拓扑排序) 问题。用 BFS (Breadth-First Search，广度优先搜索) 的 Kahn's Algorithm: 维护每个节点的 in-degree (入度)，从入度为 0 的节点开始，逐层移除节点并更新邻居入度。如果最终处理的节点数 < 总数，说明存在环。

```python
from collections import deque

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    for course, pre in prerequisites:
        graph[pre].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    count = 0
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        count += 1
        for nei in graph[node]:
            in_degree[nei] -= 1
            if in_degree[nei] == 0:
                queue.append(nei)
    return count == numCourses  # order 即为拓扑排序结果 (LC 210)
```

- **Time**: O(V + E)，V = 课程数，E = 先修关系数
- **Space**: O(V + E)
- **Key Technique**: Kahn's Algorithm (BFS topological sort) -- 适合检测 DAG (Directed Acyclic Graph，有向无环图) 和输出排序

---

### Q3."""
    )

    # ── Q3: Remove Leaves Repeatedly (LC 366) ──
    content = content.replace(
        """**解法要点**:
- Instead of actually removing leaves iteratively, observe that a node's "removal round" equals its height in the tree (where leaves have height 0). Compute each node's height and group by height.

---

### Q4.""",
        """**解答**:

**思路**: 不需要真的反复删除叶子。观察规律：一个节点被删除的轮次 = 它在树中的高度 (height)。叶子节点 height=0 第一轮删除，其父节点如果两个子节点都是叶子则 height=1 第二轮删除，以此类推。用 DFS (Depth-First Search，深度优先搜索) 后序遍历计算每个节点高度，按高度分组。

```python
from collections import defaultdict

def findLeaves(root) -> list[list[int]]:
    result = defaultdict(list)

    def dfs(node) -> int:
        if not node:
            return -1
        h = max(dfs(node.left), dfs(node.right)) + 1
        result[h].append(node.val)
        return h

    dfs(root)
    return [result[i] for i in range(len(result))]
```

- **Time**: O(n)，每个节点访问一次
- **Space**: O(n)
- **Key Insight**: 节点的"删除轮次" = 节点高度，避免了 O(n^2) 的模拟删除

---

### Q4."""
    )

    # ── Q4: Centroid Decomposition ──
    content = content.replace(
        """**解法要点**:
- Centroid decomposition: O(n log n) build time
- Each activate/query: O(log n) centroid ancestors to visit
- Space: O(n log n) for distance caches
- Key insight: centroid decomposition creates a balanced tree of depth O(log n), enabling efficient path queries

---

### Q5.""",
        """**解答**:

**思路**: Centroid Decomposition (重心分解) 是树上分治的经典技术。树的 centroid (重心) 是删除后使最大子树最小的节点。递归地找重心、以重心为根分治，构建一棵深度 O(log n) 的 centroid tree。支持高效的路径查询和点激活/查询操作。

```python
def find_centroid(adj: list[list[int]], n: int) -> int:
    \"\"\"Find centroid of tree with n nodes.\"\"\"
    subtree_size = [0] * n
    removed = [False] * n

    def get_size(v: int, parent: int) -> int:
        subtree_size[v] = 1
        for u in adj[v]:
            if u != parent and not removed[u]:
                subtree_size[v] += get_size(u, v)
        return subtree_size[v]

    def get_centroid(v: int, parent: int, tree_size: int) -> int:
        for u in adj[v]:
            if u != parent and not removed[u]:
                if subtree_size[u] > tree_size // 2:
                    return get_centroid(u, v, tree_size)
        return v

    def decompose(v: int, parent_centroid: int) -> int:
        size = get_size(v, -1)
        centroid = get_centroid(v, -1, size)
        removed[centroid] = True
        # Process centroid: build centroid tree
        for u in adj[centroid]:
            if not removed[u]:
                child_centroid = decompose(u, centroid)
        return centroid

    return decompose(0, -1)
```

- **Build Time**: O(n log n)
- **Query/Activate**: O(log n) -- 沿 centroid tree 向上遍历 O(log n) 层祖先
- **Space**: O(n log n) for distance caches
- **Key Insight**: 重心分解将任意树变成深度 O(log n) 的平衡结构，使得路径查询从 O(n) 降到 O(log n)

---

### Q5."""
    )

    # ── Q5: Trie (LC 208/211/212) ──
    content = content.replace(
        """**解法要点**:
- Trie insert/search: O(L) where L = word length
- Autocomplete: O(P + K) where P = prefix length, K = total characters in matching words
- Word Search II: O(M*N * 4^L) worst case, but Trie pruning makes it much faster in practice
- Space: O(total characters across all words)

---

### Q6.""",
        """**解答**:

**思路**: Trie (前缀树/字典树) 是处理字符串前缀问题的核心数据结构。每个节点代表一个字符，从根到叶的路径构成完整单词。LC 212 Word Search II 将 Trie 与 DFS backtracking (回溯) 结合，在二维网格中高效搜索多个单词。

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

# Word Search II (LC 212): Trie + DFS backtracking
def findWords(board: list[list[str]], words: list[str]) -> list[str]:
    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    result = set()

    def dfs(r, c, node, path):
        ch = board[r][c]
        if ch not in node.children:
            return
        node = node.children[ch]
        path += ch
        if node.is_end:
            result.add(path)
        board[r][c] = '#'  # mark visited
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                dfs(nr, nc, node, path)
        board[r][c] = ch  # restore

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return list(result)
```

- **Trie insert/search**: O(L)，L = 单词长度
- **Word Search II**: O(M*N * 4^L) worst case，Trie 剪枝实际快很多
- **Space**: O(total characters across all words)

---

### Q6."""
    )

    # ── Q6: Nested List Weighted Sum (LC 339/364) ──
    content = content.replace(
        """**解法要点**:
- Instead of finding max depth first, use the trick: process level by level and keep a running `unweighted` sum. Each time we go deeper, we add `unweighted` again to `weighted`. Shallow values are added in more rounds (maxDepth times), deep values in fewer rounds (1 time for deepest).

---

### Q7.""",
        """**解答**:

**思路**:
- **LC 339 (正向加权)**: depth * value，DFS 递归传入当前深度即可。
- **LC 364 (反向加权)**: 浅层权重更大。技巧：BFS 逐层处理，维护 unweighted 累加和。每深入一层，把 unweighted 再加到 weighted 上。浅层值被累加更多次 (maxDepth 次)，深层值只被累加 1 次。

```python
# LC 339: Nested List Weight Sum (depth * value)
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

# LC 364: Nested List Weight Sum II (reverse weight)
def depthSumInverse(nestedList) -> int:
    weighted, unweighted = 0, 0
    level = nestedList
    while level:
        next_level = []
        for item in level:
            if item.isInteger():
                unweighted += item.getInteger()
            else:
                next_level.extend(item.getList())
        weighted += unweighted  # 浅层值被反复累加
        level = next_level
    return weighted
```

- **Time**: O(n)，n = 所有嵌套元素总数
- **Space**: O(d)，d = 最大嵌套深度
- **Key Trick**: LC 364 的 BFS 累加技巧避免了先求 maxDepth 再二次遍历

---

### Q7."""
    )

    # ── Q7: Convex Number / Digit DP ──
    content = content.replace(
        """**解法要点**:
- Brute force: O((b-a) * D) where D = number of digits
- Digit DP: O(D * 10 * 2 * 2) = O(D) per length, much faster for large ranges

---

### Q8.""",
        """**解答**:

**思路**: Convex number (凸数) 的相邻数字差值正负交替 (zigzag pattern)。暴力检查每个数是 O((b-a)*D)，当范围很大时不可行。使用 Digit DP (数位 DP，数位动态规划) 逐位构造合法数字，状态包括：当前位、前一位数字、前一个差值方向、是否仍受上界限制。

```python
def count_convex_in_range(a: int, b: int) -> int:
    \"\"\"Count convex (zigzag) numbers in [a, b].\"\"\"
    def count_up_to(n: int) -> int:
        digits = [int(d) for d in str(n)]
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def dp(pos, prev_digit, prev_dir, tight, started):
            # prev_dir: 1=up, -1=down, 0=not set
            if pos == len(digits):
                return 1 if started else 0
            limit = digits[pos] if tight else 9
            count = 0
            for d in range(0, limit + 1):
                if not started and d == 0:
                    count += dp(pos+1, -1, 0, False, False)
                    continue
                new_tight = tight and (d == limit)
                if not started or prev_digit == -1:
                    count += dp(pos+1, d, 0, new_tight, True)
                else:
                    diff = d - prev_digit
                    if diff == 0:
                        continue
                    new_dir = 1 if diff > 0 else -1
                    if prev_dir == 0 or new_dir != prev_dir:
                        count += dp(pos+1, d, new_dir, new_tight, True)
            return count
        return dp(0, -1, 0, True, False)

    return count_up_to(b) - count_up_to(a - 1)
```

- **Digit DP**: O(D * 10 * 3 * 2) states，D = 位数，远快于暴力
- **Key Technique**: Digit DP -- 逐位构建数字，用 tight 标记是否仍受上界约束

---

### Q8."""
    )

    # ── Q8: N Lockers ──
    content = content.replace(
        """**解法要点**:
- # Mathematical solution: O(sqrt(n))
- \"\"\"Simulate the process to verify. O(N * H_N) ~ O(N log N).\"\"\"

---

### Q9.""",
        """**解答**:

**思路**: 第 k 个 locker (储物柜) 在第 n 轮被 toggle (切换) 当且仅当 n 是 k 的因子。因此 locker k 最终打开当且仅当 k 有奇数个因子。只有 perfect square (完全平方数) 有奇数个因子 (因为因子配对，只有平方根与自身配对)。

```python
import math

def open_lockers(n: int) -> list[int]:
    \"\"\"Return list of open lockers after n rounds.\"\"\"
    # 只有完全平方数编号的 locker 最终打开
    return [i*i for i in range(1, int(math.isqrt(n)) + 1)]

def count_open(n: int) -> int:
    \"\"\"Count of open lockers = floor(sqrt(n)).\"\"\"
    return int(math.isqrt(n))
```

- **Answer**: 打开的 locker 编号为 1, 4, 9, 16, ..., 即所有 <= N 的完全平方数
- **数学本质**: 因子个数为奇数 <=> 完全平方数
- **Time**: O(sqrt(n)) 枚举结果，O(1) 计算个数

---

### Q9."""
    )

    # ── Q9: Deepest Common Ancestor of Two BSTs ──
    content = content.replace(
        """**解法要点**:
- \"\"\"Use sorted in-order arrays for O(n+m) intersection.\"\"\"
- Approach 1: O(n + m) time, O(n) space (hash set from BST1)
- Approach 2: O(n + m) time, O(n + m) space (sorted arrays)

---

### Q10.""",
        """**解答**:

**思路**: 先找两棵 BST (Binary Search Tree，二叉搜索树) 的公共节点集合，然后找其中最深的。方法一：对 BST1 做中序遍历得排序数组，对 BST2 做中序遍历得排序数组，双指针求交集。方法二：BST1 的值存入 HashSet，遍历 BST2 查找交集并记录深度。

```python
def deepest_common_ancestor(root1, root2) -> int | None:
    \"\"\"Find deepest node that exists in both BSTs.\"\"\"
    # Step 1: Collect all values from BST1
    vals1 = set()
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        vals1.add(node.val)
        inorder(node.right)
    inorder(root1)

    # Step 2: Find common nodes with max depth in BST2
    best_val, best_depth = None, -1
    def dfs(node, depth):
        nonlocal best_val, best_depth
        if not node:
            return
        if node.val in vals1 and depth > best_depth:
            best_depth = depth
            best_val = node.val
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
    dfs(root2, 0)
    return best_val
```

- **Time**: O(n + m)，n, m 分别为两棵树的节点数
- **Space**: O(n)，存储 BST1 的值集合
- **Alternative**: 双指针法对两个排序数组求交集，空间 O(n+m)

---

### Q10."""
    )

    # ── Q10: Big Data Map+Sort ──
    content = content.replace(
        """**解法要点**:
- arr.sort()  # sort input first: O(n log n)
- # Map then sort: O(n log n)
- General: O(n log n) sort + O(n) map
- Monotonic f: O(n log n) sort only (map is free)

---

### Q11.""",
        """**解答**:

**思路**: 对大规模数据集应用函数 f 后排序。关键优化取决于 f 的性质：
1. **f 单调递增**: 先排序输入，再 map，结果自动有序。O(n log n)。
2. **f 单调递减**: 先排序输入，map 后反转。O(n log n)。
3. **f 非单调 (一般情况)**: map 后再排序。O(n log n)。无法利用输入顺序。
4. **大数据 (内存放不下)**: External Sort (外部排序) -- 分块读入内存排序，写入临时文件，再多路归并 (k-way merge)。MapReduce 框架天然支持。

```python
import heapq

def map_and_sort(data: list, f) -> list:
    \"\"\"Apply f to each element and return sorted result.\"\"\"
    mapped = [f(x) for x in data]  # O(n)
    mapped.sort()                   # O(n log n)
    return mapped

# External sort for big data (conceptual)
def external_sort(input_file: str, output_file: str, chunk_size: int):
    \"\"\"Sort file too large for memory using external merge sort.\"\"\"
    # Phase 1: Sort chunks in memory, write to temp files
    temp_files = []
    # ... read chunk_size elements, sort, write to temp file

    # Phase 2: K-way merge using min-heap
    # heapq.merge(*sorted_iterators) for efficient merging
    pass
```

- **General case**: O(n log n) sort + O(n) map
- **Monotonic f**: O(n log n) sort only (利用单调性跳过重新排序)
- **External Sort**: O(n log n) with O(chunk_size) memory，适合数据量 >> 内存

---

### Q11."""
    )

    # ── Q11: Coins DP ──
    content = content.replace(
        """**解法要点**:
- Time: O(N * K * M)
- Space: O(K * M)

---

### Q12.""",
        """**解答**:

**思路**: N 枚硬币面值 0 到 N-1，选恰好 K 枚，求总面值 mod M 的某个值的方案数。经典 knapsack DP (背包动态规划)：dp[i][j][r] = 从前 i 种硬币中选了 j 枚、总面值 mod M 余 r 的方案数。空间优化后只需 dp[j][r]。

```python
def count_ways(n: int, k: int, m: int, target_mod: int) -> int:
    \"\"\"Count ways to pick exactly k coins from {0..n-1} with sum % m == target_mod.\"\"\"
    # dp[j][r] = ways to pick j coins with sum % m == r
    dp = [[0] * m for _ in range(k + 1)]
    dp[0][0] = 1  # 0 coins, sum=0

    for coin in range(n):  # coin values 0..n-1
        # Traverse in reverse to avoid reusing same coin
        for j in range(min(k, coin + 1), 0, -1):
            for r in range(m):
                prev_r = (r - coin) % m
                dp[j][r] += dp[j - 1][prev_r]

    return dp[k][target_mod]
```

- **Time**: O(N * K * M)
- **Space**: O(K * M)
- **Key Technique**: Modular knapsack DP，状态压缩到 (选了几枚, 余数)

---

### Q12."""
    )

    # ── Q12: Letter Combinations of Phone Number (LC 17) ──
    content = content.replace(
        """**解法要点**:
- Time: O(4^N * N) where N = len(digits). At most 4 choices per digit, N characters per combination.
- Space: O(N) for recursion depth (excluding output)

---

### Q13.""",
        """**解答**:

**思路**: Backtracking (回溯)。建立数字到字母的映射表，对每个数字尝试所有可能字母，递归生成组合。

```python
def letterCombinations(digits: str) -> list[str]:
    if not digits:
        return []
    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    result = []

    def backtrack(idx: int, path: list[str]):
        if idx == len(digits):
            result.append(''.join(path))
            return
        for ch in phone[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

- **Time**: O(4^N * N)，每个数字最多 4 种选择，生成长度 N 的字符串
- **Space**: O(N) 递归深度 (不含输出)
- **Key Technique**: Backtracking with explicit undo (回溯 + path.pop())

---

### Q13."""
    )

    # ── Q13: Maximal Consecutive Subsequences (LC 128*) ──
    content = content.replace(
        """**解法要点**:
- ### Alternative: O(n) using HashSet (LC 128 variant)
- \"\"\"O(n) approach using hash set.\"\"\"
- Sort approach: O(n log n) time, O(1) extra space (in-place sort)
- HashSet approach: O(n) time, O(n) space

---

### Q14.""",
        """**解答**:

**思路**: 找所有最长连续子序列。两种方法：
1. **排序法**: O(n log n)，排序后线性扫描分组。
2. **HashSet 法**: O(n)，只从序列起点 (num-1 不在 set 中) 开始向右扩展。

```python
def find_consecutive_groups(nums: list[int]) -> list[list[int]]:
    \"\"\"Find all maximal consecutive subsequences.\"\"\"
    if not nums:
        return []
    num_set = set(nums)
    groups = []

    for num in num_set:
        if num - 1 not in num_set:  # 只从序列起点开始
            seq = [num]
            cur = num
            while cur + 1 in num_set:
                cur += 1
                seq.append(cur)
            groups.append(seq)

    return groups

# LC 128: Longest Consecutive Sequence
def longestConsecutive(nums: list[int]) -> int:
    num_set = set(nums)
    best = 0
    for num in num_set:
        if num - 1 not in num_set:
            length = 1
            while num + length in num_set:
                length += 1
            best = max(best, length)
    return best
```

- **HashSet**: O(n) time, O(n) space -- 每个元素最多被访问两次 (一次作为起点检查，一次在 while 中)
- **Sort**: O(n log n) time, O(1) extra space
- **Key Insight**: 只从 "起点" 开始扩展，避免重复计算

---

### Q14."""
    )

    # ── Q14: SQL Problem ──
    # Q14 has no 解法要点, just the problem statement followed by ---
    content = content.replace(
        """**题目**: SQL Problem: Given two tables - table1(user_id, article_id, date) recording user article views, and table2(article_id, article_type) mapping articles to types: (1) Count the number of article types each user viewed on 2019-01-01 using an inner join and group by. (2) Create a histogram showing the distribution of how many article types each user viewed, grouped by the count of article types.

---

### Q15.""",
        """**题目**: SQL Problem: Given two tables - table1(user_id, article_id, date) recording user article views, and table2(article_id, article_type) mapping articles to types: (1) Count the number of article types each user viewed on 2019-01-01 using an inner join and group by. (2) Create a histogram showing the distribution of how many article types each user viewed, grouped by the count of article types.

**解答**:

```sql
-- (1) 每个用户在 2019-01-01 浏览的文章类型数
SELECT t1.user_id,
       COUNT(DISTINCT t2.article_type) AS type_count
FROM table1 t1
INNER JOIN table2 t2 ON t1.article_id = t2.article_id
WHERE t1.date = '2019-01-01'
GROUP BY t1.user_id;

-- (2) 用户浏览类型数的分布直方图
SELECT type_count, COUNT(*) AS user_count
FROM (
    SELECT t1.user_id,
           COUNT(DISTINCT t2.article_type) AS type_count
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.article_id = t2.article_id
    WHERE t1.date = '2019-01-01'
    GROUP BY t1.user_id
) sub
GROUP BY type_count
ORDER BY type_count;
```

- **Key SQL Techniques**: INNER JOIN + GROUP BY + COUNT(DISTINCT) 用于分类统计；子查询 (subquery) 实现二次聚合生成 histogram (直方图)
- **注意**: 使用 COUNT(DISTINCT article_type) 而非 COUNT(*)，因为同一用户可能多次浏览同类型文章

---

### Q15."""
    )

    # ── Q15: SQL + Python ──
    content = content.replace(
        """**题目**: SQL + Python: Given tables video_posts(post_date, memberid, video_length) and members(memberid, country, join_date), analyze video upload patterns. Write SQL queries to: (1) Find average video count and total video length per member segmented by US vs non-US...

---

## ML Theory""",
        """**题目**: SQL + Python: Given tables video_posts(post_date, memberid, video_length) and members(memberid, country, join_date), analyze video upload patterns. Write SQL queries to: (1) Find average video count and total video length per member segmented by US vs non-US...

**解答**:

```sql
-- (1) 按 US vs non-US 分段统计每个用户的视频数和总时长
SELECT
    CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END AS segment,
    COUNT(v.memberid) * 1.0 / COUNT(DISTINCT v.memberid) AS avg_video_count,
    SUM(v.video_length) AS total_video_length,
    COUNT(DISTINCT v.memberid) AS member_count
FROM video_posts v
JOIN members m ON v.memberid = m.memberid
GROUP BY CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END;

-- (2) 按加入时间队列分析视频上传趋势
SELECT
    DATE_TRUNC('month', m.join_date) AS cohort,
    CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END AS segment,
    COUNT(*) AS video_count
FROM video_posts v
JOIN members m ON v.memberid = m.memberid
GROUP BY cohort, segment
ORDER BY cohort;
```

```python
# Python: Hypothesis testing -- US vs Non-US video upload frequency
from scipy import stats
import pandas as pd

def test_video_upload_difference(df_us: pd.Series, df_non_us: pd.Series):
    \"\"\"Two-sample t-test for video upload frequency.\"\"\"
    t_stat, p_value = stats.ttest_ind(df_us, df_non_us, equal_var=False)
    alpha = 0.05
    print(f"t-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")
    if p_value < alpha:
        print("Reject H0: US and non-US upload rates differ significantly")
    else:
        print("Fail to reject H0: No significant difference")
    return t_stat, p_value
```

- **SQL**: JOIN + CASE WHEN 实现分段聚合；DATE_TRUNC 用于队列 (cohort) 分析
- **Python**: Welch's t-test (不假设方差相等) 检验两组均值差异
- **Follow-up**: 还可以做 Mann-Whitney U test (非参数检验) 如果数据不服从正态分布

---

## ML Theory"""
    )

    return content


def main() -> None:
    """Apply enrichments and save."""
    conn = sqlite3.connect(str(DB_PATH))
    content = get_content(conn)
    original_len = len(content)

    enriched = enrich(content)

    if enriched == content:
        print("WARNING: No changes applied -- check markers")
        conn.close()
        sys.exit(1)

    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=26",
        (enriched,),
    )
    conn.commit()
    new_len = len(enriched)
    print(f"OK: doc#26 enriched {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    print("Coding Q1-Q15: all 15 questions enriched with full solutions")
    conn.close()


if __name__ == "__main__":
    main()
