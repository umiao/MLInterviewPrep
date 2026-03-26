"""Expand Blind75 problem notes - batch 4 (14 problems).

Updates notes for LC 207, 208, 211, 213, 217, 226, 230, 235, 238, 242, 252, 253, 261, 268
with structured sections: 思路, 关键技巧, 核心代码, 注意点, 复杂度.
"""

import sqlite3
import sys

DB_PATH = "data/mle_prep.db"

EXPANDED_NOTES: dict[int, str] = {
    207: """## Course Schedule

### 思路
拓扑排序（BFS/Kahn 算法）。构建有向图和入度数组。将入度为 0 的节点入队，BFS 每次取出一个节点，将其邻居的入度减 1，新的入度为 0 的节点继续入队。如果处理的节点数等于总课程数，则无环。

### 关键技巧
- 入度为 0 = 没有前置课程，可以先修
- BFS 过程模拟修课顺序，每修一门课减少后续课的前置依赖
- 如果存在环，环中节点入度永远不会变为 0，无法全部处理
- DFS 判环也可以：三色标记法（白/灰/黑）

### 核心代码
```python
from collections import deque

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        indegree[course] += 1

    queue = deque(i for i in range(numCourses) if indegree[i] == 0)
    count = 0
    while queue:
        node = queue.popleft()
        count += 1
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    return count == numCourses
```

### 注意点
- prerequisites[i] = [a, b] 表示修 a 之前要先修 b（b -> a）
- 自环和多重边都算有环
- Course Schedule II (LC 210) 要返回拓扑排序结果，只需记录出队顺序

### 复杂度
- 时间: O(V + E) - V 是课程数，E 是依赖数
- 空间: O(V + E) - 图 + 入度数组 + 队列""",

    208: """## Implement Trie (Prefix Tree)

### 思路
每个节点包含一个 children 字典（字符 -> 子节点）和一个 is_end 标记。insert 沿路径创建节点，search 沿路径查找且最后节点 is_end 为 True，startsWith 沿路径查找即可。

### 关键技巧
- 用字典存子节点比定长数组更灵活（但面试中 26 长度数组也常用）
- is_end 标记区分前缀和完整单词：search("app") 在插入 "apple" 后应返回 False
- 三个操作共享 "沿路径走" 的逻辑

### 核心代码
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

    def _find(self, prefix: str) -> TrieNode:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

### 注意点
- search 和 startsWith 的区别仅在于是否检查 is_end
- 提取 _find 辅助方法减少重复代码
- 删除操作比较复杂，需要递归并清理空节点（但 Blind75 不考）

### 复杂度
- 时间: O(m) - m 是单词/前缀长度，insert/search/startsWith 都是
- 空间: O(总字符数) - 最坏情况无公共前缀""",

    211: """## Design Add and Search Words Data Structure

### 思路
基于 Trie 实现。addWord 和普通 Trie 插入一样。search 支持通配符 '.'，遇到 '.' 时需要遍历当前节点的所有子节点（回溯搜索）。

### 关键技巧
- '.' 匹配任意字符：对当前节点所有子节点递归搜索
- 非 '.' 字符：和普通 Trie search 一样走确定路径
- 用 DFS 递归处理通配符

### 核心代码
```python
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node['$'] = True

    def search(self, word: str) -> bool:
        def dfs(node: dict, i: int) -> bool:
            if i == len(word):
                return '$' in node
            if word[i] == '.':
                return any(dfs(node[ch], i + 1)
                           for ch in node if ch != '$')
            if word[i] not in node:
                return False
            return dfs(node[word[i]], i + 1)
        return dfs(self.root, 0)
```

### 注意点
- 用 '$' 或特殊键标记单词结尾，避免和字母键冲突
- 遍历子节点时跳过 '$' 标记
- 最坏情况（全是 '.'）：搜索时间退化为 O(26^m)
- 简洁写法用嵌套字典替代 TrieNode 类

### 复杂度
- 时间: addWord O(m); search 最坏 O(26^m)，通常远小于此
- 空间: O(总字符数)""",

    213: """## House Robber II

### 思路
环形排列：第一家和最后一家相邻，不能同时偷。拆分为两个子问题：(1) 偷 nums[0:n-1]（不偷最后一家）；(2) 偷 nums[1:n]（不偷第一家）。两个子问题都是线性 House Robber，取最大值。

### 关键技巧
- 分两次跑 House Robber I 的 DP
- 核心洞察：环形约束等价于"不能同时选首尾"，拆成两个不选首/不选尾的线性问题
- 只有一家时直接返回 nums[0]

### 核心代码
```python
def rob(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]

    def rob_linear(houses: list[int]) -> int:
        prev2, prev1 = 0, 0
        for h in houses:
            prev2, prev1 = prev1, max(prev1, prev2 + h)
        return prev1

    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```

### 注意点
- 特殊处理 n=1 的情况（两个子数组都为空）
- 切片 nums[:-1] 和 nums[1:] 各创建新列表，可以用索引优化空间
- 不需要显式处理 n=2 的情况，rob_linear 自然处理

### 复杂度
- 时间: O(n) - 两次线性扫描
- 空间: O(1) - 不算切片的话；切片是 O(n)""",

    217: """## Contains Duplicate

### 思路
用 HashSet 记录出现过的数字。遍历数组，如果当前数字已在 set 中，返回 True；否则加入 set。

### 关键技巧
- set 的查找和插入都是 O(1)
- 一行写法：return len(nums) != len(set(nums))
- 排序后检查相邻元素也可以，但 O(n log n)

### 核心代码
```python
def containsDuplicate(nums: list[int]) -> bool:
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

### 注意点
- 提前返回比先构建完整 set 更优（最好情况 O(1)）
- 空数组返回 False
- 一行写法简洁但必须遍历全部元素

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(n) - HashSet""",

    226: """## Invert Binary Tree

### 思路
递归交换每个节点的左右子树。先递归反转左右子树，然后交换当前节点的左右指针。

### 关键技巧
- 递归三行搞定：反转左、反转右、交换
- BFS 也可以：层序遍历时交换每个节点的左右子节点
- Python 可以用元组交换一行完成

### 核心代码
```python
def invertTree(root: TreeNode) -> TreeNode:
    if not root:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```

### 注意点
- 空节点返回 None（递归基）
- 先递归再交换（后序）或先交换再递归（前序）都可以
- 不要忘记返回 root
- 中序遍历交换会有问题（交换后左子树变成了原来的右子树）

### 复杂度
- 时间: O(n) - 每个节点访问一次
- 空间: O(h) - 递归栈，h 为树高""",

    230: """## Kth Smallest Element in a BST

### 思路
BST 的中序遍历是有序的。做中序遍历，计数到第 k 个就是答案。

### 关键技巧
- 中序遍历：左 -> 根 -> 右，自然产生升序序列
- 迭代版中序遍历用栈模拟，可以在找到第 k 个时提前停止
- 不需要遍历完整棵树

### 核心代码
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

### 注意点
- 迭代写法比递归更容易提前终止
- Follow-up: 频繁调用 + 频繁修改 -> 每个节点存左子树大小，O(h) 查找
- 递归写法需要用全局变量或引用传递 k 的计数

### 复杂度
- 时间: O(H + k) - H 为树高（走到最左），然后弹 k 次
- 空间: O(H) - 栈大小""",

    235: """## Lowest Common Ancestor of a Binary Search Tree

### 思路
利用 BST 性质。从根开始：如果 p 和 q 都小于当前节点，往左走；都大于当前节点，往右走；否则当前节点就是 LCA（一个在左一个在右，或其中一个就是当前节点）。

### 关键技巧
- BST 性质让 LCA 查找变成单路径搜索，不需要遍历整棵树
- 分裂点（p 和 q 分别在左右子树）就是 LCA
- 迭代写法更优，不需要递归栈

### 核心代码
```python
def lowestCommonAncestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    curr = root
    while curr:
        if p.val < curr.val and q.val < curr.val:
            curr = curr.left
        elif p.val > curr.val and q.val > curr.val:
            curr = curr.right
        else:
            return curr
```

### 注意点
- 题目保证 p 和 q 都存在于树中
- LCA 可以是 p 或 q 本身（p 是 q 的祖先的情况）
- 普通二叉树的 LCA (LC 236) 不能利用 BST 性质，需要后序遍历
- 不需要比较 p.val 和 q.val 的大小关系

### 复杂度
- 时间: O(h) - h 为树高，最坏 O(n)
- 空间: O(1) - 迭代写法""",

    238: """## Product of Array Except Self

### 思路
两次遍历。第一次从左到右计算前缀积（每个位置左边所有元素的乘积），第二次从右到左乘以后缀积（右边所有元素的乘积）。

### 关键技巧
- 不能用除法（题目要求）
- answer[i] = 左边所有元素之积 * 右边所有元素之积
- 用一个变量累积后缀积，直接乘到结果数组上，O(1) 额外空间

### 核心代码
```python
def productExceptSelf(nums: list[int]) -> list[int]:
    n = len(nums)
    answer = [1] * n
    # 前缀积
    prefix = 1
    for i in range(n):
        answer[i] = prefix
        prefix *= nums[i]
    # 后缀积
    suffix = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix
        suffix *= nums[i]
    return answer
```

### 注意点
- 第一遍 answer[i] 存的是 i 左边的乘积（不含 nums[i]）
- 第二遍乘以 i 右边的乘积
- 包含 0 的情况自然处理（乘积为 0 的位置）
- 题目要求 O(1) 额外空间（输出数组不算）

### 复杂度
- 时间: O(n) - 两次遍历
- 空间: O(1) - 除了输出数组""",

    242: """## Valid Anagram

### 思路
统计两个字符串中每个字符的出现次数，比较是否相同。

### 关键技巧
- 用 Counter 或长度 26 的数组统计频率
- 先检查长度是否相等，不等直接返回 False
- 排序后比较也可以，但 O(n log n)

### 核心代码
```python
from collections import Counter

def isAnagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)
```

### 注意点
- Counter 比较是 O(n) 的，整体 O(n)
- 数组写法：26 长度数组，s 中字符 +1，t 中字符 -1，最后检查全为 0
- Follow-up: 如果包含 Unicode 字符，用 HashMap 而非固定大小数组
- sorted(s) == sorted(t) 最简洁但 O(n log n)

### 复杂度
- 时间: O(n) - n 为字符串长度
- 空间: O(1) - 字母表大小固定为 26（或 O(k) 对 Unicode）""",

    252: """## Meeting Rooms

### 思路
判断是否有时间冲突。将所有会议按开始时间排序，检查相邻会议是否重叠（前一个的结束时间 > 后一个的开始时间）。

### 关键技巧
- 排序后只需检查相邻会议，不需要两两比较
- 重叠条件：intervals[i-1].end > intervals[i].start
- 可以参加所有会议 = 没有任何重叠

### 核心代码
```python
def canAttendMeetings(intervals: list[list[int]]) -> bool:
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i - 1][1] > intervals[i][0]:
            return False
    return True
```

### 注意点
- 空列表返回 True（没有会议，不冲突）
- [1,5] 和 [5,10] 不算重叠（end == start 可以背靠背）
- 这是 Meeting Rooms II 的基础

### 复杂度
- 时间: O(n log n) - 排序
- 空间: O(1) - 原地排序（或 O(n) 取决于排序算法）""",

    253: """## Meeting Rooms II

### 思路
需要多少间会议室 = 同一时刻最多有多少个会议重叠。方法一：扫描线，将开始和结束事件分别标记为 +1 和 -1，按时间排序后扫描。方法二：排序 + 最小堆，跟踪最早结束的会议室。

### 关键技巧
- 最小堆方法：堆顶是最早结束的会议。新会议开始时，如果开始时间 >= 堆顶结束时间，复用该会议室（pop）；否则需要新会议室。最后堆的大小就是答案。
- 扫描线方法：开始 +1，结束 -1，同一时间先处理结束（避免多算）

### 核心代码
```python
import heapq

def minMeetingRooms(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: x[0])
    heap = []  # 存各会议室的结束时间
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)
```

### 注意点
- heapreplace = heappop + heappush，但更高效
- 堆中存的是结束时间，不是整个区间
- heap[0] <= start（等于时可以复用，背靠背开会）
- 扫描线写法不需要堆，空间更优

### 复杂度
- 时间: O(n log n) - 排序 + 堆操作
- 空间: O(n) - 最坏情况所有会议重叠，堆大小为 n""",

    261: """## Graph Valid Tree

### 思路
树 = 连通 + 无环的无向图。条件：(1) 边数 == n-1；(2) 所有节点连通（从任意节点 BFS/DFS 能访问所有节点）。两个条件同时满足等价于合法树。

### 关键技巧
- 先检查边数：edges != n-1 直接返回 False（必要条件）
- 再检查连通性：BFS/DFS 从节点 0 出发，visited 集合大小 == n
- Union-Find 也可以：每次合并时检查是否已在同一集合（有环），最后检查连通分量数 == 1

### 核心代码
```python
from collections import deque

def validTree(n: int, edges: list[list[int]]) -> bool:
    if len(edges) != n - 1:
        return False
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    queue = deque([0])
    visited.add(0)
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited) == n
```

### 注意点
- n=0 或 n=1 的边界情况（0 个节点不是树，1 个节点 + 0 条边是树）
- 边数 == n-1 是必要条件但不充分（可能不连通），必须同时检查连通性
- Union-Find 方法不需要建图，边加入时直接合并

### 复杂度
- 时间: O(V + E) = O(n) 因为 E = n-1
- 空间: O(n) - 图 + visited""",

    268: """## Missing Number

### 思路
利用数学公式：0 到 n 的和减去数组的和就是缺失的数字。或者用异或：a ^ a = 0，将 0~n 和数组元素全部异或，剩下的就是缺失的数。

### 关键技巧
- 数学法：sum(0..n) - sum(nums) = missing
- 异或法：不怕整数溢出（虽然 Python 无此问题）
- 也可以用 HashSet 或排序，但不如以上两种优雅

### 核心代码
```python
def missingNumber(nums: list[int]) -> int:
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
```

### 注意点
- 数组长度为 n，包含 0 到 n 中 n 个不同数字，缺一个
- 数学法可能有整数溢出（其他语言），异或法没有
- 异或写法：result = n; for i, v in enumerate(nums): result ^= i ^ v
- 高斯求和公式：n*(n+1)/2

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1)""",
}


def main() -> None:
    """Update problem notes in the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    for leetcode_id, new_notes in EXPANDED_NOTES.items():
        # Get existing notes
        cur.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = ?",
            (leetcode_id,),
        )
        row = cur.fetchone()
        if not row:
            print(f"WARNING: LC {leetcode_id} not found in DB", file=sys.stderr)
            continue

        problem_id, old_notes = row

        # Merge: prepend old notes as "original notes" section, then expanded
        if old_notes and old_notes.strip():
            merged = f"**Original notes**: {old_notes.strip()}\n\n{new_notes.strip()}"
        else:
            merged = new_notes.strip()

        cur.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (merged, problem_id),
        )
        updated += 1
        print(f"Updated LC {leetcode_id} (id={problem_id})")

    conn.commit()
    conn.close()
    print(f"\nDone: {updated}/{len(EXPANDED_NOTES)} problems updated.")


if __name__ == "__main__":
    main()
