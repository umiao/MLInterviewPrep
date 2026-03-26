"""Expand Blind75 problem notes - batch 2 (14 problems).

Updates notes for LC 56, 57, 62, 70, 73, 76, 79, 91, 98, 100, 102, 104, 105, 121
with structured sections: 思路, 关键技巧, 核心代码, 注意点, 复杂度.
"""

import sqlite3
import sys

DB_PATH = "data/mle_prep.db"

EXPANDED_NOTES: dict[int, str] = {
    56: """## Merge Intervals

### 思路
按区间左端点排序，然后遍历。如果当前区间的左端点 <= 结果数组最后一个区间的右端点，说明有重叠，合并（取右端点的较大值）。否则直接加入结果。

### 关键技巧
- 只需要按左端点排序，不需要考虑右端点的排序
- 合并时只需要更新右端点：merged[-1][1] = max(merged[-1][1], interval[1])
- 排序后只需要和最后一个已合并区间比较

### 核心代码
```python
def merge(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

### 注意点
- 重叠条件是 start <= merged[-1][1]（等号表示端点相接也要合并）
- 空输入需要处理（但 LeetCode 保证至少一个区间）
- 不要忘记排序，这是前提条件

### 复杂度
- 时间: O(n log n) - 排序主导
- 空间: O(n) - 输出数组""",

    57: """## Insert Interval

### 思路
三段式处理：(1) 所有在新区间左侧且不重叠的区间直接加入结果；(2) 所有与新区间重叠的区间合并到新区间中；(3) 所有在新区间右侧的区间直接加入结果。

### 关键技巧
- 不重叠在左侧：interval[1] < newInterval[0]
- 不重叠在右侧：interval[0] > newInterval[1]
- 重叠时不断合并：更新 newInterval 的左右端点

### 核心代码
```python
def insert(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    result = []
    i = 0
    n = len(intervals)
    # 左侧不重叠
    while i < n and intervals[i][1] < newInterval[0]:
        result.append(intervals[i])
        i += 1
    # 合并重叠
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    result.append(newInterval)
    # 右侧不重叠
    while i < n:
        result.append(intervals[i])
        i += 1
    return result
```

### 注意点
- 输入已排序，不需要自己排序
- 空 intervals 数组时直接返回 [newInterval]
- newInterval 可能不和任何区间重叠（纯插入）

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(n) - 输出数组""",

    62: """## Unique Paths

### 思路
动态规划。dp[i][j] 表示从 (0,0) 到 (i,j) 的路径数。每个格子只能从上方或左方到达，所以 dp[i][j] = dp[i-1][j] + dp[i][j-1]。

### 关键技巧
- 第一行和第一列都只有一条路径（全部为1）
- 空间优化：只需要一行 dp 数组，从左到右更新
- 数学解法：结果为 C(m+n-2, m-1)，即组合数

### 核心代码
```python
def uniquePaths(m: int, n: int) -> int:
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]
```

### 注意点
- 空间优化后 dp[j] += dp[j-1]：dp[j] 是上方的值（还没更新），dp[j-1] 是左方的值（已更新）
- m 和 n 的含义：m 行 n 列，不要搞反
- 1x1 网格返回 1

### 复杂度
- 时间: O(m * n)
- 空间: O(n) - 一维 dp 数组""",

    70: """## Climbing Stairs

### 思路
动态规划，本质是斐波那契数列。到达第 n 阶的方案数 = 到达第 n-1 阶 + 到达第 n-2 阶（因为每次可以爬1或2阶）。

### 关键技巧
- 只需要维护最近两个状态，不需要完整 dp 数组
- f(1) = 1, f(2) = 2，从 f(3) 开始递推
- 和斐波那契的区别是初始值：f(0)=1, f(1)=1

### 核心代码
```python
def climbStairs(n: int) -> int:
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1
```

### 注意点
- n=1 返回 1，n=2 返回 2（两种：1+1 或 2）
- 用元组交换避免临时变量
- 矩阵快速幂可以做到 O(log n)，但面试一般不要求

### 复杂度
- 时间: O(n) - 线性递推
- 空间: O(1) - 只用两个变量""",

    73: """## Set Matrix Zeroes

### 思路
用矩阵的第一行和第一列作为标记数组。遍历矩阵，如果 matrix[i][j] == 0，则标记 matrix[i][0] = 0 和 matrix[0][j] = 0。然后根据标记置零。

### 关键技巧
- 第一行和第一列本身是否需要置零，用两个额外变量 row0 和 col0 记录
- 置零时要从内部开始（不要先处理第一行/列，否则标记信息被破坏）
- O(1) 空间的关键：复用矩阵自身作为存储

### 核心代码
```python
def setZeroes(matrix: list[list[int]]) -> None:
    m, n = len(matrix), len(matrix[0])
    row0 = any(matrix[0][j] == 0 for j in range(n))
    col0 = any(matrix[i][0] == 0 for i in range(m))
    # 标记
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    # 根据标记置零（内部）
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    # 处理第一行和第一列
    if row0:
        for j in range(n):
            matrix[0][j] = 0
    if col0:
        for i in range(m):
            matrix[i][0] = 0
```

### 注意点
- 必须先标记、再置零内部、最后处理第一行/列（顺序不能乱）
- 如果先处理第一行/列，会覆盖标记信息
- O(m+n) 解法用额外数组记录哪些行列需要置零，更简单但空间不是 O(1)

### 复杂度
- 时间: O(m * n) - 遍历两次
- 空间: O(1) - 只用两个额外变量""",

    76: """## Minimum Window Substring

### 思路
滑动窗口。维护一个窗口 [left, right]，用 Counter 记录 t 中各字符所需的数量。右指针扩展直到窗口包含 t 的所有字符，然后左指针收缩寻找最小窗口。

### 关键技巧
- need 字典记录 t 中每个字符的需求量，窗口内字符出现时 need[c] -= 1
- 用 formed 变量记录已满足的字符种类数，等于 required（t 中不同字符数）时窗口合法
- 收缩窗口时，如果某字符 need[c] 从 0 变为 1，formed -= 1

### 核心代码
```python
from collections import Counter

def minWindow(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    required = len(need)
    formed = 0
    left = 0
    ans = (float('inf'), 0, 0)  # (length, left, right)
    window = {}
    for right, char in enumerate(s):
        window[char] = window.get(char, 0) + 1
        if char in need and window[char] == need[char]:
            formed += 1
        while formed == required:
            if right - left + 1 < ans[0]:
                ans = (right - left + 1, left, right)
            lc = s[left]
            window[lc] -= 1
            if lc in need and window[lc] < need[lc]:
                formed -= 1
            left += 1
    return "" if ans[0] == float('inf') else s[ans[1]:ans[2] + 1]
```

### 注意点
- window[char] == need[char] 时才 formed += 1（不是 >=，避免重复计数）
- window[lc] < need[lc] 时 formed -= 1（刚好不满足时）
- t 中可能有重复字符，Counter 正确处理了这种情况

### 复杂度
- 时间: O(|S| + |T|) - 每个字符最多被访问两次（左右指针各一次）
- 空间: O(|S| + |T|) - 两个字典""",

    79: """## Word Search

### 思路
回溯法(DFS)。从每个格子出发，尝试匹配 word 的每个字符。匹配时向四个方向递归，用 visited 标记避免重复使用同一格子。

### 关键技巧
- 原地修改标记：将 board[i][j] 设为 '#'（或其他非字母字符）表示已访问，回溯时恢复
- 这样不需要额外的 visited 矩阵，空间更优
- 匹配到 word 最后一个字符时直接返回 True

### 核心代码
```python
def exist(board: list[list[str]], word: str) -> bool:
    m, n = len(board), len(board[0])

    def dfs(i: int, j: int, k: int) -> bool:
        if k == len(word):
            return True
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
            return False
        temp = board[i][j]
        board[i][j] = '#'  # mark visited
        found = (dfs(i+1, j, k+1) or dfs(i-1, j, k+1) or
                 dfs(i, j+1, k+1) or dfs(i, j-1, k+1))
        board[i][j] = temp  # restore
        return found

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False
```

### 注意点
- 回溯时必须恢复 board[i][j]，否则会影响后续搜索路径
- 短路求值：四个方向的 or 会在找到时提前返回
- 剪枝优化：如果 word 最后一个字符在 board 中出现次数少于第一个，可以反转 word

### 复杂度
- 时间: O(m * n * 3^L) - L 为 word 长度，每步最多3个方向（不能回头）
- 空间: O(L) - 递归深度""",

    91: """## Decode Ways

### 思路
动态规划。dp[i] 表示 s[0:i] 的解码方式数。对于每个位置，考虑单个字符解码（1-9有效）和两个字符解码（10-26有效）。

### 关键技巧
- 单字符有效：s[i] != '0'，则 dp[i] += dp[i-1]
- 双字符有效：10 <= int(s[i-1:i+1]) <= 26，则 dp[i] += dp[i-2]
- 空间优化：只需要前两个状态

### 核心代码
```python
def numDecodings(s: str) -> int:
    if not s or s[0] == '0':
        return 0
    prev2, prev1 = 1, 1  # dp[0], dp[1]
    for i in range(1, len(s)):
        curr = 0
        if s[i] != '0':
            curr += prev1
        two_digit = int(s[i-1:i+1])
        if 10 <= two_digit <= 26:
            curr += prev2
        prev2, prev1 = prev1, curr
    return prev1
```

### 注意点
- '0' 不能单独解码（没有对应字母），但 '10' 和 '20' 是有效的两位数
- 以 '0' 开头的字符串无法解码，返回 0
- dp[0] = 1 是边界条件（空字符串有一种解码方式：什么都不选）

### 复杂度
- 时间: O(n) - 一次遍历
- 空间: O(1) - 只用两个变量""",

    98: """## Validate Binary Search Tree

### 思路
中序遍历法：BST 的中序遍历结果必须严格递增。维护一个 prev 变量记录上一个访问的节点值，当前值必须大于 prev。

### 关键技巧
- 递归法：传入 (low, high) 范围，每个节点的值必须在 (low, high) 开区间内
- 中序遍历法：用一个变量 prev 记录前一个值，无需存储完整遍历结果
- 初始范围用 -inf 和 +inf

### 核心代码
```python
def isValidBST(root: TreeNode) -> bool:
    def validate(node, low=float('-inf'), high=float('inf')):
        if not node:
            return True
        if not (low < node.val < high):
            return False
        return (validate(node.left, low, node.val) and
                validate(node.right, node.val, high))
    return validate(root)
```

### 注意点
- BST 要求严格不等（< 而非 <=），相等的值不合法
- 不能只检查 node.left.val < node.val < node.right.val（只检查直接子节点不够）
- 需要全局约束：左子树所有节点 < root，右子树所有节点 > root

### 复杂度
- 时间: O(n) - 每个节点访问一次
- 空间: O(h) - 递归栈深度，h 为树高""",

    100: """## Same Tree

### 思路
递归比较两棵树。如果两个节点都为 None 返回 True，如果只有一个为 None 或值不同返回 False，否则递归比较左右子树。

### 关键技巧
- 先处理 None 的情况（两个都 None、只有一个 None）
- 递归结构清晰：根值相同 + 左子树相同 + 右子树相同
- 也可以用迭代法（BFS/DFS + 栈/队列）

### 核心代码
```python
def isSameTree(p: TreeNode, q: TreeNode) -> bool:
    if not p and not q:
        return True
    if not p or not q:
        return False
    return (p.val == q.val and
            isSameTree(p.left, q.left) and
            isSameTree(p.right, q.right))
```

### 注意点
- 短路求值：值不同就不需要比较子树了
- 两棵空树被认为是相同的
- 结构相同但值不同 -> False

### 复杂度
- 时间: O(n) - n 为较小树的节点数
- 空间: O(h) - 递归深度，最坏 O(n)（退化为链表）""",

    102: """## Binary Tree Level Order Traversal

### 思路
BFS（广度优先搜索）。用队列逐层遍历，每层开始时记录当前队列长度（该层的节点数），依次出队并将子节点入队。

### 关键技巧
- 每层开始时用 level_size = len(queue) 确定该层节点数
- 内层循环 level_size 次，保证每次处理完恰好一层
- 每层结果收集到一个 list 中

### 核心代码
```python
from collections import deque

def levelOrder(root: TreeNode) -> list[list[int]]:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

### 注意点
- 空树返回 []（不是 [[]]）
- 用 deque 保证 popleft() 是 O(1)
- 变体很多：zigzag（LC 103）、bottom-up（LC 107）、right side view（LC 199）

### 复杂度
- 时间: O(n) - 每个节点恰好处理一次
- 空间: O(w) - w 为最大层宽度（最坏 n/2）""",

    104: """## Maximum Depth of Binary Tree

### 思路
递归法。空节点深度为 0，非空节点深度 = 1 + max(左子树深度, 右子树深度)。

### 关键技巧
- 最简洁的树递归模板之一
- 也可以用 BFS 层数计数
- DFS 迭代法用栈存储 (node, depth) 对

### 核心代码
```python
def maxDepth(root: TreeNode) -> int:
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

### 注意点
- 空树深度为 0（不是 -1）
- LeetCode 定义深度为节点数（不是边数），所以单节点深度为 1
- 递归法简洁但有栈溢出风险（极深的树），实际面试中不需要担心

### 复杂度
- 时间: O(n) - 每个节点访问一次
- 空间: O(h) - 递归栈深度，最坏 O(n)""",

    105: """## Construct Binary Tree from Preorder and Inorder Traversal

### 思路
前序遍历第一个元素是根节点。在中序遍历中找到根节点的位置，左侧是左子树，右侧是右子树。递归构建。

### 关键技巧
- 用 hashmap 存储中序遍历中每个值的索引，O(1) 查找根节点位置
- 前序遍历中，根节点后面先是左子树的所有节点，再是右子树的所有节点
- 根据中序遍历中左子树的长度来划分前序遍历

### 核心代码
```python
def buildTree(preorder: list[int], inorder: list[int]) -> TreeNode:
    inorder_map = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = [0]  # 用列表包装以便在闭包中修改

    def build(in_left: int, in_right: int) -> TreeNode:
        if in_left > in_right:
            return None
        root_val = preorder[pre_idx[0]]
        pre_idx[0] += 1
        root = TreeNode(root_val)
        mid = inorder_map[root_val]
        root.left = build(in_left, mid - 1)   # 必须先构建左子树
        root.right = build(mid + 1, in_right)
        return root

    return build(0, len(inorder) - 1)
```

### 注意点
- 必须先递归构建左子树再构建右子树（和前序遍历顺序一致）
- 题目保证没有重复值（否则 hashmap 无法唯一定位）
- pre_idx 用列表或 nonlocal 来在递归中维护全局状态

### 复杂度
- 时间: O(n) - 每个节点处理一次
- 空间: O(n) - hashmap + 递归栈""",

    121: """## Best Time to Buy and Sell Stock

### 思路
一次遍历。维护到目前为止的最低买入价 min_price，每天计算以当前价格卖出的利润，更新最大利润。

### 关键技巧
- 关键是先更新 min_price，再计算利润（或反过来：先计算利润再更新 min_price，都可以）
- 等价于求数组中 max(prices[j] - prices[i])，其中 j > i
- Kadane 变体：将价格差分后求最大子数组和

### 核心代码
```python
def maxProfit(prices: list[int]) -> int:
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
```

### 注意点
- 只能买卖一次（买卖多次是 LC 122，用贪心）
- 如果价格一直下跌，最大利润为 0（不交易）
- 必须先买后卖，不能同一天买卖（虽然利润为0也合法）

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
