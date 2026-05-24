# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Expand Blind75 problem notes - batch 5 (14 problems).

Updates notes for LC 269, 271, 295, 297, 300, 322, 323, 338, 417, 424, 435, 572, 647, 1143
with structured sections: 思路, 关键技巧, 核心代码, 注意点, 复杂度.
"""

import sqlite3
import sys

DB_PATH = "data/mle_prep.db"

EXPANDED_NOTES: dict[int, str] = {
    269: """## Alien Dictionary

### 思路
拓扑排序。从相邻单词对中提取字符的先后顺序（有向边），然后做拓扑排序得到字典序。逐对比较相邻单词，找到第一个不同字符 c1, c2，建立 c1 -> c2 的边。

### 关键技巧
- 只有相邻单词的第一个不同字符能产生有效约束
- 如果短单词是长单词的前缀，但短单词排在后面，则字典序无效（返回 ""）
- 用 BFS（Kahn 算法）做拓扑排序，检测环
- 所有出现过的字符都要加入图（即使没有边约束）

### 核心代码
```python
from collections import deque, defaultdict

def alienOrder(words: list[str]) -> str:
    # Build graph with all characters
    graph = {ch: set() for word in words for ch in word}
    indegree = {ch: 0 for ch in graph}

    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))
        # Invalid: prefix comes after longer word
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    indegree[w2[j]] += 1
                break

    queue = deque(ch for ch in indegree if indegree[ch] == 0)
    result = []
    while queue:
        ch = queue.popleft()
        result.append(ch)
        for neighbor in graph[ch]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph):
        return ""  # Cycle detected
    return "".join(result)
```

### 注意点
- 前缀检查：["abc", "ab"] 是无效顺序，必须返回 ""
- 有环 = 无法确定顺序，返回 ""
- 拓扑排序结果不唯一，任意合法顺序都可以
- 只用相邻单词对提取约束，不用所有单词对

### 复杂度
- 时间: O(C) - C 是所有单词的总字符数
- 空间: O(U + E) - U 是唯一字符数，E 是边数""",

    271: """## Encode and Decode Strings

### 思路
编码时在每个字符串前加上长度和分隔符（如 "5#hello"），解码时读取长度，然后截取对应长度的字符串。这样任何字符（包括分隔符本身）都不会造成歧义。

### 关键技巧
- 长度前缀法：length + delimiter + string
- 分隔符选 '#' 或 ':' 都可以，因为长度已经确定了读取范围
- 不能用简单的分隔符（如 ","），因为字符串本身可能包含该字符
- Chunked transfer encoding 用的也是类似思路

### 核心代码
```python
class Codec:
    def encode(self, strs: list[str]) -> str:
        return "".join(f"{len(s)}#{s}" for s in strs)

    def decode(self, s: str) -> list[str]:
        result = []
        i = 0
        while i < len(s):
            j = s.index('#', i)
            length = int(s[i:j])
            result.append(s[j + 1: j + 1 + length])
            i = j + 1 + length
        return result
```

### 注意点
- 编码空字符串 "" -> "0#"
- 编码空列表 [] -> ""（encode 返回空字符串）
- 字符串可以包含任何字符，包括 '#' 和数字
- 长度前缀确保解码不依赖字符串内容

### 复杂度
- 时间: O(n) - n 是所有字符串的总长度
- 空间: O(n) - 编码/解码后的字符串""",

    295: """## Find Median from Data Stream

### 思路
用两个堆维护数据流的中位数。最大堆（max_heap）存较小的一半，最小堆（min_heap）存较大的一半。保持两个堆大小平衡（差不超过 1），中位数从堆顶取。

### 关键技巧
- Python 只有最小堆，用取负值模拟最大堆
- 始终保持 len(max_heap) == len(min_heap) 或 len(max_heap) == len(min_heap) + 1
- addNum：先加入 max_heap，再把 max_heap 堆顶移到 min_heap，然后平衡大小
- findMedian：奇数个取 max_heap 堆顶，偶数个取两堆顶平均

### 核心代码
```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []  # max heap (negated)
        self.hi = []  # min heap

    def addNum(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```

### 注意点
- 三步操作保证：(1) max_heap 的所有元素 <= min_heap 的所有元素；(2) 大小平衡
- 不能直接 push 到某个堆，必须经过另一个堆中转以保持有序性
- Follow-up: 如果数据范围有限，可以用桶/计数排序优化

### 复杂度
- 时间: addNum O(log n), findMedian O(1)
- 空间: O(n) - 存储所有元素""",

    297: """## Serialize and Deserialize Binary Tree

### 思路
前序遍历序列化。将树转为字符串：节点值用逗号分隔，空节点用 "N" 表示。反序列化时按前序顺序递归重建。

### 关键技巧
- 前序遍历 + 空节点标记 可以唯一确定一棵二叉树
- 序列化：root,left_subtree,right_subtree，空节点输出 "N"
- 反序列化：维护一个迭代器/索引，每次取下一个值构建节点
- BFS 层序遍历也可以，但空节点较多时字符串更长

### 核心代码
```python
class Codec:
    def serialize(self, root: TreeNode) -> str:
        vals = []
        def dfs(node):
            if not node:
                vals.append("N")
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> TreeNode:
        vals = iter(data.split(","))
        def dfs():
            val = next(vals)
            if val == "N":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node
        return dfs()
```

### 注意点
- 分隔符和空节点标记要一致（序列化和反序列化配对）
- 用 iter + next 比用索引更优雅
- 负数和多位数需要正确处理（用逗号分隔，int() 转换）
- 空树序列化为 "N"

### 复杂度
- 时间: O(n) - 每个节点访问一次
- 空间: O(n) - 递归栈 + 字符串""",

    300: """## Longest Increasing Subsequence

### 思路
方法一：DP，dp[i] = 以 nums[i] 结尾的 LIS 长度，对每个 i 遍历 j < i 更新。方法二：贪心 + 二分，维护一个 tails 数组，tails[i] 是长度为 i+1 的递增子序列的最小末尾元素。

### 关键技巧
- DP: dp[i] = max(dp[j] + 1) for all j < i where nums[j] < nums[i]
- 贪心 + 二分：对每个 num，用二分找到 tails 中第一个 >= num 的位置替换；如果 num 比所有都大，追加
- tails 数组始终保持有序，但它本身不是 LIS（只是用来维护长度）
- bisect_left 找替换位置

### 核心代码
```python
import bisect

def lengthOfLIS(nums: list[int]) -> int:
    tails = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

### 注意点
- bisect_left 保证严格递增（相等时替换，不追加）
- tails 数组的长度就是 LIS 长度，但内容不一定是实际的 LIS
- DP 方法 O(n^2) 适合面试手写，贪心+二分 O(n log n) 更优
- 如果要输出实际 LIS 序列，需要额外记录前驱

### 复杂度
- 时间: O(n log n) - 贪心+二分；O(n^2) - DP
- 空间: O(n) - tails 数组或 dp 数组""",

    322: """## Coin Change

### 思路
完全背包 DP。dp[i] = 凑成金额 i 需要的最少硬币数。对每个金额从 1 到 amount，尝试每种硬币，取 dp[i - coin] + 1 的最小值。

### 关键技巧
- dp[0] = 0（金额 0 需要 0 枚硬币），其余初始化为 inf
- 转移：dp[i] = min(dp[i], dp[i - coin] + 1) for each coin <= i
- 完全背包：每种硬币可以无限使用
- 返回 dp[amount]，如果仍为 inf 则返回 -1

### 核心代码
```python
def coinChange(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

### 注意点
- amount = 0 时返回 0
- 无法凑成时返回 -1（dp[amount] 仍为 inf）
- 硬币面额可以是无序的
- 内外循环顺序无所谓（和完全背包不同于 0-1 背包的区别在于一维 dp 正序遍历）

### 复杂度
- 时间: O(amount * len(coins))
- 空间: O(amount) - dp 数组""",

    323: """## Number of Connected Components in an Undirected Graph

### 思路
Union-Find 或 BFS/DFS 计算连通分量数。初始化每个节点为一个分量，遍历所有边合并节点，最后统计独立集合数。

### 关键技巧
- Union-Find：初始 count = n，每次成功 union（两个不同集合）count -= 1
- DFS/BFS：遍历所有未访问节点，每次 DFS 找到一个完整连通分量
- Union-Find 带路径压缩 + 按秩合并最优

### 核心代码
```python
def countComponents(n: int, edges: list[list[int]]) -> int:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x: int, y: int) -> bool:
        px, py = find(x), find(y)
        if px == py:
            return False
        parent[px] = py
        return True

    count = n
    for u, v in edges:
        if union(u, v):
            count -= 1
    return count
```

### 注意点
- union 返回是否合并成功（已在同一集合返回 False）
- 路径压缩：parent[x] = parent[parent[x]]（隔代压缩，简单有效）
- n=0 返回 0，无边时返回 n
- 和 Graph Valid Tree 的区别：树还要求边数 == n-1 且无环

### 复杂度
- 时间: O(E * alpha(n)) - 接近 O(E)，alpha 是反阿克曼函数
- 空间: O(n) - parent 数组""",

    338: """## Counting Bits

### 思路
DP 利用位运算。dp[i] = dp[i >> 1] + (i & 1)。右移一位等于去掉最低位，再加上最低位是否为 1。

### 关键技巧
- i >> 1 的 1 的个数已经算过了（因为 i >> 1 < i）
- i & 1 判断最低位是否为 1
- 也可以用 dp[i] = dp[i & (i-1)] + 1（去掉最低位的 1）
- Brian Kernighan: i & (i-1) 去掉最低位的 1

### 核心代码
```python
def countBits(n: int) -> list[int]:
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

### 注意点
- dp[0] = 0（0 没有 1）
- 两种递推关系都可以：右移法和去最低 1 法
- 结果数组长度为 n+1（从 0 到 n）
- 一行写法：[bin(i).count('1') for i in range(n+1)]，但 O(n log n)

### 复杂度
- 时间: O(n) - 每个数 O(1)
- 空间: O(n) - 结果数组（题目要求返回）""",

    417: """## Pacific Atlantic Water Flow

### 思路
反向思维。从太平洋边界出发 DFS/BFS 标记能到达的所有格子，从大西洋边界出发同样标记。两个集合的交集就是答案。

### 关键技巧
- 正向思考（从每个格子出发判断能否到两个海洋）太慢
- 反向：从海洋边界逆流而上，水只能流向 >= 当前高度的邻居
- 太平洋：上边界 + 左边界；大西洋：下边界 + 右边界
- 用两个 visited 集合分别记录两个海洋能到达的格子

### 核心代码
```python
def pacificAtlantic(heights: list[list[int]]) -> list[list[int]]:
    if not heights:
        return []
    m, n = len(heights), len(heights[0])
    pacific = set()
    atlantic = set()

    def dfs(r: int, c: int, visited: set):
        visited.add((r, c))
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < m and 0 <= nc < n
                    and (nr, nc) not in visited
                    and heights[nr][nc] >= heights[r][c]):
                dfs(nr, nc, visited)

    for i in range(m):
        dfs(i, 0, pacific)
        dfs(i, n - 1, atlantic)
    for j in range(n):
        dfs(0, j, pacific)
        dfs(m - 1, j, atlantic)

    return list(pacific & atlantic)
```

### 注意点
- 逆流条件：邻居高度 >= 当前高度（水可以从高处流下来）
- 从边界出发，所以 DFS 的"前进方向"是逆流的
- 结果是两个 visited 集合的交集
- BFS 也可以，把边界格子全部入队一起搜

### 复杂度
- 时间: O(m * n) - 每个格子最多访问两次
- 空间: O(m * n) - 两个 visited 集合""",

    424: """## Longest Repeating Character Replacement

### 思路
滑动窗口。维护窗口内出现次数最多的字符的频率 max_freq。窗口大小 - max_freq <= k 时窗口合法（最多替换 k 个字符使窗口内字符全相同）。不合法时收缩左边界。

### 关键技巧
- 窗口合法条件：window_size - max_freq <= k
- max_freq 只增不减（关键优化）：当 max_freq 没有增大时，窗口大小不会增大，答案不会更新
- 不需要在收缩时更新 max_freq（因为更小的 max_freq 不可能产生更大的窗口）

### 核心代码
```python
def characterReplacement(s: str, k: int) -> int:
    count = {}
    max_freq = 0
    left = 0
    result = 0
    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_freq = max(max_freq, count[s[right]])
        while (right - left + 1) - max_freq > k:
            count[s[left]] -= 1
            left += 1
        result = max(result, right - left + 1)
    return result
```

### 注意点
- max_freq 不需要在左指针移动后重新计算（只增不减的优化）
- 这个优化是正确的：我们只关心更大的窗口，更小的 max_freq 不会带来更大窗口
- while 可以换成 if（因为左指针每次最多移动 1 步），但 while 更安全
- 窗口内不关心具体是哪个字符最多，只关心最大频率

### 复杂度
- 时间: O(n) - 每个字符进出窗口各一次
- 空间: O(26) = O(1) - 字符频率数组""",

    435: """## Non-overlapping Intervals

### 思路
贪心。等价于：最多能保留多少个不重叠区间？按结束时间排序，贪心选结束最早的区间（为后面留更多空间），跳过与已选区间重叠的。需要移除的 = 总数 - 最多保留数。

### 关键技巧
- 按 end 排序（不是 start），贪心选结束最早的
- 等价于"活动选择问题"（经典贪心）
- 选了一个区间后，下一个区间的 start 必须 >= 当前 end
- 也可以反过来想：按 end 排序，遇到重叠就移除当前区间（end 更大的那个）

### 核心代码
```python
def eraseOverlapIntervals(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: x[1])
    count = 0
    prev_end = float('-inf')
    for start, end in intervals:
        if start >= prev_end:
            prev_end = end
        else:
            count += 1
    return count
```

### 注意点
- start == prev_end 不算重叠（[1,2] 和 [2,3] 可以共存）
- 按 end 排序是关键，按 start 排序贪心不正确
- count 计的是需要移除的数量
- 空输入返回 0

### 复杂度
- 时间: O(n log n) - 排序
- 空间: O(1) - 原地排序""",

    572: """## Subtree of Another Tree

### 思路
对 root 的每个节点，检查以该节点为根的子树是否和 subRoot 完全相同。递归两层：外层遍历 root 的每个节点，内层比较两棵树是否相同。

### 关键技巧
- isSameTree(s, t)：两棵树结构和值都相同
- isSubtree(root, subRoot)：root 为空返回 False；root 和 subRoot 相同，或 subRoot 是 root 左/右子树的子树
- 先检查 isSameTree 再递归子树

### 核心代码
```python
def isSubtree(root: TreeNode, subRoot: TreeNode) -> bool:
    if not root:
        return False
    if isSameTree(root, subRoot):
        return True
    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)

def isSameTree(s: TreeNode, t: TreeNode) -> bool:
    if not s and not t:
        return True
    if not s or not t:
        return False
    return (s.val == t.val
            and isSameTree(s.left, t.left)
            and isSameTree(s.right, t.right))
```

### 注意点
- subRoot 为空时：空树是任何树的子树（但 LeetCode 题目保证 subRoot 非空）
- 必须是完全匹配（子树的叶子也必须是叶子，不能有额外子节点）
- 暴力法足够面试，O(m*n)
- 优化：序列化 + KMP 或哈希比较，O(m+n)

### 复杂度
- 时间: O(m * n) - m 是 root 节点数，n 是 subRoot 节点数
- 空间: O(h) - h 是 root 的高度（递归栈）""",

    647: """## Palindromic Substrings

### 思路
中心扩展法。遍历每个可能的回文中心，向两边扩展计数。回文中心有 2n-1 个：n 个单字符中心（奇数长度回文）+ n-1 个双字符间隙（偶数长度回文）。

### 关键技巧
- 每个位置尝试两种扩展：以 i 为中心（奇数）和以 i,i+1 为中心（偶数）
- 扩展时 s[left] == s[right] 就是回文，count += 1
- 比 DP 更直观，空间 O(1)
- DP 方法：dp[i][j] = s[i:j+1] 是否是回文

### 核心代码
```python
def countSubstrings(s: str) -> int:
    count = 0
    n = len(s)

    def expand(left: int, right: int):
        nonlocal count
        while left >= 0 and right < n and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1

    for i in range(n):
        expand(i, i)      # odd length
        expand(i, i + 1)  # even length
    return count
```

### 注意点
- 单个字符也是回文，所以最少有 n 个回文子串
- 中心扩展比 DP 空间更优：O(1) vs O(n^2)
- Manacher 算法可以 O(n)，但面试中很少要求
- 和 LC 5 (Longest Palindromic Substring) 思路完全一样，只是统计方式不同

### 复杂度
- 时间: O(n^2) - 每个中心最多扩展 O(n)
- 空间: O(1) - 只用常数变量""",

    1143: """## Longest Common Subsequence

### 思路
经典二维 DP。dp[i][j] = text1[:i] 和 text2[:j] 的 LCS 长度。如果 text1[i-1] == text2[j-1]，则 dp[i][j] = dp[i-1][j-1] + 1；否则取 dp[i-1][j] 和 dp[i][j-1] 的最大值。

### 关键技巧
- 字符相等：当前字符属于 LCS，从左上角 +1
- 字符不等：要么跳过 text1[i-1]，要么跳过 text2[j-1]，取较大值
- dp 数组大小 (m+1) x (n+1)，第 0 行和第 0 列为 0（空字符串的 LCS 为 0）
- 可以空间优化到 O(min(m,n))，只用两行

### 核心代码
```python
def longestCommonSubsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

### 注意点
- 下标对应关系：dp[i][j] 对应 text1[i-1] 和 text2[j-1]
- 空字符串和任何字符串的 LCS 为 0（base case）
- 如果要输出实际 LCS 序列，需要回溯 dp 表
- 和编辑距离(LC 72)类似的 dp 框架

### 复杂度
- 时间: O(m * n)
- 空间: O(m * n)，可优化到 O(min(m, n))""",
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
