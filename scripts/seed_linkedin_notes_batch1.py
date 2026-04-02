"""Seed solution notes for LinkedIn top-50 frequency problems (batch 1: problems 1-25)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES: dict[int, str] = {}

# ── LC 2667: Create Hello World Function ──────────────────────────────────
NOTES[2667] = r"""## Create Hello World Function

### 思路
JavaScript 闭包基础题。返回一个无论传入什么参数都返回 "Hello World" 的函数。

### 核心代码
```python
# Python 等价实现
def createHelloWorld():
    def hello(*args):
        return "Hello World"
    return hello
```

### 关键技巧
- 考察闭包(closure)概念：函数作为返回值
- Python 中用 `*args` 接受任意参数
- 这是 LeetCode 30 Days of JavaScript 系列的入门题

### 复杂度
- 时间: O(1)
- 空间: O(1)
"""

# ── LC 696: Count Binary Substrings ──────────────────────────────────────
NOTES[696] = r"""## Count Binary Substrings

### 思路
统计连续相同字符的分组长度，相邻两组取较小值即为它们之间可构成的合法子串数。例如 "00111" 分组为 [2, 3]，贡献 min(2,3)=2 个合法子串("01","0011")。

### 核心代码
```python
def countBinarySubstrings(s: str) -> int:
    groups = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            groups.append(count)
            count = 1
    groups.append(count)
    return sum(min(groups[i], groups[i + 1]) for i in range(len(groups) - 1))
```

### 优化：O(1) 空间
```python
def countBinarySubstrings(s: str) -> int:
    ans, prev, cur = 0, 0, 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            cur += 1
        else:
            ans += min(prev, cur)
            prev, cur = cur, 1
    return ans + min(prev, cur)
```

### 关键技巧
- 分组计数法：只需记录当前组和前一组长度
- 不需要枚举所有子串

### 复杂度
- 时间: O(n)
- 空间: O(1)（优化版）
"""

# ── LC 7: Reverse Integer ────────────────────────────────────────────────
NOTES[7] = r"""## Reverse Integer

### 思路
逐位取出末位数字构建反转结果。注意 32 位有符号整数溢出检查：反转后超出 [-2^31, 2^31-1] 返回 0。

### 核心代码
```python
def reverse(x: int) -> int:
    sign = -1 if x < 0 else 1
    x = abs(x)
    result = 0
    while x:
        result = result * 10 + x % 10
        x //= 10
    result *= sign
    return result if -2**31 <= result <= 2**31 - 1 else 0
```

### 关键技巧
- Python 无整数溢出，但题目要求模拟 32 位限制
- 负数先取绝对值处理，最后恢复符号
- 也可以用字符串反转：`int(str(abs(x))[::-1]) * sign`

### 复杂度
- 时间: O(log x) - 数字位数
- 空间: O(1)
"""

# ── LC 13: Roman to Integer ──────────────────────────────────────────────
NOTES[13] = r"""## Roman to Integer

### 思路
从左到右遍历，如果当前字符代表的值小于下一个字符的值，则减去当前值（如 IV=4, IX=9）；否则加上当前值。

### 核心代码
```python
def romanToInt(s: str) -> int:
    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
             'C': 100, 'D': 500, 'M': 1000}
    result = 0
    for i in range(len(s)):
        if i + 1 < len(s) and roman[s[i]] < roman[s[i + 1]]:
            result -= roman[s[i]]
        else:
            result += roman[s[i]]
    return result
```

### 关键技巧
- 减法规则：小值在大值左边时减去（IV, IX, XL, XC, CD, CM）
- 从右往左遍历也可以，逻辑类似

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 3733: Minimum Time to Complete All Deliveries ─────────────────────
NOTES[3733] = r"""## Minimum Time to Complete All Deliveries

### 思路
树上 DFS 问题。给定以 0 为根的树，节点有配送需求。从根出发，每条边耗时 1，需要访问所有有需求的节点并返回根。关键观察：每条边最多走 2*(子树中有需求的节点数) 次，但最远路径只需走一次不返回可以省一个来回。

### 核心代码
```python
def minimumTime(n: int, edges: list[list[int]], deliveries: list[int]) -> int:
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    # DFS 计算每个子树的总配送次数和最远配送距离
    total_cost = 0

    def dfs(node: int, parent: int, depth: int) -> int:
        nonlocal total_cost
        max_depth = depth if deliveries[node] > 0 else 0
        sub_trips = deliveries[node]
        for nei in graph[node]:
            if nei == parent:
                continue
            child_max, child_trips = dfs(nei, node, depth + 1)
            max_depth = max(max_depth, child_max)
            sub_trips += child_trips
        if parent != -1 and sub_trips > 0:
            total_cost += 2 * sub_trips
        return max_depth, sub_trips

    max_d, _ = dfs(0, -1, 0)
    # 最远路径不需要返回，但题目要求回到原点
    return total_cost
```

### 关键技巧
- 树上配送问题的经典模型：每条边的遍历次数 = 2 * 子树需求量
- 如果不需要返回起点，可以减去最远路径的距离
- DFS 后序遍历统计子树信息

### 复杂度
- 时间: O(n)
- 空间: O(n) - 递归栈 + 邻接表
"""

# ── LC 3494: Find the Minimum Amount of Time to Brew Potions ─────────────
NOTES[3494] = r"""## Find the Minimum Amount of Time to Brew Potions

### 思路
二分答案。给定 n 个巫师和 m 个药水，每个巫师按顺序酿造每个药水需要 skill[i]*mana[j] 时间。巫师可以并行工作但每个药水必须按巫师顺序传递。二分总时间，检查是否可行。

### 核心代码
```python
def minTime(skill: list[int], mana: list[int]) -> int:
    n, m = len(skill), len(mana)

    def feasible(T: int) -> bool:
        # 检查在时间 T 内是否能完成所有药水
        # 每个药水 j 的开始时间需要满足：
        # 上一个药水在每个巫师处完成后才能开始
        start = [0] * m
        for j in range(1, m):
            for i in range(n):
                # 巫师 i 完成药水 j-1 后才能开始药水 j
                start[j] = max(start[j],
                    start[j-1] + skill[i] * mana[j-1])
            # 但我们只需要最后的约束
        # 检查最后一个药水能否在 T 内完成
        return start[-1] + sum(s * mana[-1] for s in skill) <= T

    lo, hi = 0, sum(skill) * sum(mana)
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

### 关键技巧
- 流水线调度问题：药水按顺序经过每个巫师
- 二分答案 + 贪心验证
- 关键约束：每个巫师同一时间只能处理一个药水

### 复杂度
- 时间: O(n*m*log(S)) - S 为答案上界
- 空间: O(m)
"""

# ── LC 22: Generate Parentheses ──────────────────────────────────────────
NOTES[22] = r"""## Generate Parentheses

### 思路
回溯法。维护当前已用的左括号数 open 和右括号数 close。只在 open < n 时添加左括号，close < open 时添加右括号，保证每一步都合法。

### 核心代码
```python
def generateParenthesis(n: int) -> list[str]:
    result = []
    def backtrack(path: list[str], open_count: int, close_count: int):
        if len(path) == 2 * n:
            result.append("".join(path))
            return
        if open_count < n:
            path.append("(")
            backtrack(path, open_count + 1, close_count)
            path.pop()
        if close_count < open_count:
            path.append(")")
            backtrack(path, open_count, close_count + 1)
            path.pop()
    backtrack([], 0, 0)
    return result
```

### 关键技巧
- 合法性保证：任何前缀中左括号数 >= 右括号数
- 结果数量为卡特兰数 C(2n,n)/(n+1)
- 也可用 BFS 或 DP 生成

### 复杂度
- 时间: O(4^n / sqrt(n)) - 卡特兰数
- 空间: O(n) - 递归深度
"""

# ── LC 1797: Design Authentication Manager ──────────────────────────────
NOTES[1797] = r"""## Design Authentication Manager

### 思路
用 HashMap 存储 tokenId -> 过期时间。generate 直接插入，renew 检查未过期才更新，countUnexpiredTokens 遍历计数。

### 核心代码
```python
class AuthenticationManager:
    def __init__(self, timeToLive: int):
        self.ttl = timeToLive
        self.tokens: dict[str, int] = {}  # tokenId -> expiry time

    def generate(self, tokenId: str, currentTime: int) -> None:
        self.tokens[tokenId] = currentTime + self.ttl

    def renew(self, tokenId: str, currentTime: int) -> None:
        if tokenId in self.tokens and self.tokens[tokenId] > currentTime:
            self.tokens[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime: int) -> int:
        return sum(1 for exp in self.tokens.values() if exp > currentTime)
```

### 关键技巧
- 过期判断：expiry > currentTime（严格大于）
- renew 只对未过期的 token 生效
- 可以用有序字典优化 countUnexpiredTokens，但 HashMap 已足够

### 复杂度
- generate/renew: O(1)
- countUnexpiredTokens: O(n)
- 空间: O(n)
"""

# ── LC 407: Trapping Rain Water II ───────────────────────────────────────
NOTES[407] = r"""## Trapping Rain Water II

### 思路
3D 接雨水。用最小堆 + BFS 从矩阵边界向内扩展。边界是"围墙"，每次取出最矮的围墙，向内部邻居扩展：如果邻居更矮则可以积水（水量 = 当前围墙高度 - 邻居高度），将邻居加入堆（高度取 max）。

### 核心代码
```python
import heapq

def trapRainWater(heightMap: list[list[int]]) -> int:
    if not heightMap or not heightMap[0]:
        return 0
    m, n = len(heightMap), len(heightMap[0])
    visited = [[False] * n for _ in range(m)]
    heap = []

    # 将边界加入最小堆
    for i in range(m):
        for j in range(n):
            if i == 0 or i == m - 1 or j == 0 or j == n - 1:
                heapq.heappush(heap, (heightMap[i][j], i, j))
                visited[i][j] = True

    water = 0
    while heap:
        h, x, y = heapq.heappop(heap)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and not visited[nx][ny]:
                visited[nx][ny] = True
                water += max(0, h - heightMap[nx][ny])
                heapq.heappush(heap, (max(h, heightMap[nx][ny]), nx, ny))
    return water
```

### 关键技巧
- 从外向内收缩，最小堆保证每次处理最矮的边界
- 木桶原理：水位由最短边界决定
- 是 1D Trapping Rain Water (LC 42) 的推广

### Follow-up
- 1D 版本用双指针 O(n)，2D 版本必须用堆

### 复杂度
- 时间: O(mn * log(mn))
- 空间: O(mn)
"""

# ── LC 412: Fizz Buzz ────────────────────────────────────────────────────
NOTES[412] = r"""## Fizz Buzz

### 思路
经典入门题。遍历 1 到 n，能被 15 整除输出 "FizzBuzz"，能被 3 整除输出 "Fizz"，能被 5 整除输出 "Buzz"，否则输出数字字符串。

### 核心代码
```python
def fizzBuzz(n: int) -> list[str]:
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
```

### 扩展写法（可扩展多规则）
```python
def fizzBuzz(n: int) -> list[str]:
    rules = [(3, "Fizz"), (5, "Buzz")]
    result = []
    for i in range(1, n + 1):
        s = "".join(word for div, word in rules if i % div == 0)
        result.append(s or str(i))
    return result
```

### 关键技巧
- 面试中常考扩展性：如何支持任意规则组合
- 先检查 15（或用字符串拼接避免硬编码 15）

### 复杂度
- 时间: O(n)
- 空间: O(n) - 输出数组
"""

# ── LC 1209: Remove All Adjacent Duplicates in String II ─────────────────
NOTES[1209] = r"""## Remove All Adjacent Duplicates in String II

### 思路
用栈存储 (字符, 连续计数)。遍历字符串，如果栈顶字符与当前相同则计数+1，达到 k 时弹出；否则压入新元素。

### 核心代码
```python
def removeDuplicates(s: str, k: int) -> str:
    stack = []  # [(char, count)]
    for c in s:
        if stack and stack[-1][0] == c:
            stack[-1] = (c, stack[-1][1] + 1)
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append((c, 1))
    return "".join(c * cnt for c, cnt in stack)
```

### 关键技巧
- 栈中存 (字符, 计数) 对，避免反复压入弹出
- k=2 时退化为 LC 1047 (Remove All Adjacent Duplicates)
- 一次遍历即可，不需要反复扫描

### 复杂度
- 时间: O(n)
- 空间: O(n)
"""

# ── LC 2571: Minimum Operations to Reduce an Integer to 0 ───────────────
NOTES[2571] = r"""## Minimum Operations to Reduce an Integer to 0

### 思路
贪心 + 位运算。每次操作可以加或减一个 2 的幂。观察二进制表示：连续的 1 可以通过 +1 变成更高位的 1（消除多个 1），单独的 1 直接减去。统计连续 1 段：长度 1 的段减一次，长度 > 1 的段加一次（变成更高位）再处理。

### 核心代码
```python
def minOperations(n: int) -> int:
    ops = 0
    while n:
        # 找最低位的 1
        if n & 1:
            # 检查是否有连续的 1
            if n & 2:
                # 连续的 1，加 1 合并
                n += 1
            else:
                # 单独的 1，减去
                n -= 1
            ops += 1
        else:
            n >>= 1
    return ops
```

### 关键技巧
- 连续 1 用加法合并比逐个减更优
- 例如 7 (111) -> +1 变 8 (1000) -> -8 变 0，共 2 步
- 本质是找最少的 +/- 2^k 操作覆盖所有 bit

### 复杂度
- 时间: O(log n)
- 空间: O(1)
"""

# ── LC 51: N-Queens ──────────────────────────────────────────────────────
NOTES[51] = r"""## N-Queens

### 思路
回溯法逐行放置皇后。用三个集合记录已占用的列、主对角线(row-col)、副对角线(row+col)，剪枝加速。

### 核心代码
```python
def solveNQueens(n: int) -> list[list[str]]:
    result = []
    cols = set()
    diag1 = set()  # row - col
    diag2 = set()  # row + col

    def backtrack(row: int, queens: list[int]):
        if row == n:
            board = []
            for q in queens:
                board.append("." * q + "Q" + "." * (n - q - 1))
            result.append(board)
            return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)
            queens.append(col)
            backtrack(row + 1, queens)
            queens.pop()
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0, [])
    return result
```

### 关键技巧
- 逐行放置保证行不冲突
- 对角线用 row-col 和 row+col 唯一标识
- 用集合 O(1) 检查冲突

### 复杂度
- 时间: O(n!) - 实际远小于，剪枝效果好
- 空间: O(n) - 递归深度
"""

# ── LC 2141: Maximum Running Time of N Computers ────────────────────────
NOTES[2141] = r"""## Maximum Running Time of N Computers

### 思路
二分答案。二分最长运行时间 T，检查 n 台电脑是否都能运行 T 分钟。关键贪心：电池容量 >= T 的直接分配给一台电脑，剩余电池共享给剩余电脑（可以热替换）。

### 核心代码
```python
def maxRunTime(n: int, batteries: list[int]) -> int:
    lo, hi = 1, sum(batteries) // n

    while lo < hi:
        mid = (lo + hi + 1) // 2
        # 容量 >= mid 的电池各分配一台电脑
        # 剩余电池总量是否够剩余电脑运行 mid 分钟
        total = 0
        remaining_computers = n
        for b in sorted(batteries, reverse=True):
            if b >= mid:
                remaining_computers -= 1
            else:
                total += b
        if total >= remaining_computers * mid:
            lo = mid
        else:
            hi = mid - 1
    return lo
```

### 关键技巧
- 大电池（>= T）独占一台电脑，小电池共享
- 小电池可以在多台电脑间切换，所以只要总量够就行
- 上界为总电量 / 电脑数（均分）

### 复杂度
- 时间: O(n * log(S/n)) - S 为电池总量
- 空间: O(1)（原地排序）
"""

# ── LC 3350: Adjacent Increasing Subarrays Detection II ──────────────────
NOTES[3350] = r"""## Adjacent Increasing Subarrays Detection II

### 思路
找最大的 k，使得数组中存在两个相邻的长度为 k 的严格递增子数组。先预处理每个位置结尾的最长递增子数组长度 inc[i]，然后枚举分界点。

### 核心代码
```python
def maxIncreasingSubarrays(nums: list[int]) -> int:
    n = len(nums)
    # inc[i] = 以 i 结尾的最长连续严格递增长度
    inc = [1] * n
    for i in range(1, n):
        if nums[i] > nums[i - 1]:
            inc[i] = inc[i - 1] + 1

    ans = 1
    for i in range(1, n):
        # 第一段结尾在 i-1，第二段结尾在某处
        # 第二段从 i 开始，长度为 inc[i]
        # 第一段结尾在 i-1，长度为 inc[i-1]
        # 两段相邻，k = min(inc[i-1], inc[i])
        # 但需要两段各自长度 >= k
        k = min(inc[i - 1], inc[i])
        ans = max(ans, k)
        # 也可以单段折半：一段长度 L 可以拆成两个 L//2
        ans = max(ans, inc[i] // 2)
    return ans
```

### 关键技巧
- 预处理连续递增长度数组
- 两个相邻递增段的 k 取两段长度的较小值
- 单段足够长时可以拆成两半（L//2）

### 复杂度
- 时间: O(n)
- 空间: O(n)
"""

# ── LC 875: Koko Eating Bananas ──────────────────────────────────────────
NOTES[875] = r"""## Koko Eating Bananas

### 思路
二分答案。二分吃香蕉速度 k（1 到 max(piles)），对每个 k 计算吃完所有堆需要的小时数，找最小的 k 使得总时间 <= h。

### 核心代码
```python
import math

def minEatingSpeed(piles: list[int], h: int) -> int:
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

### 关键技巧
- 经典二分答案模板：最小化满足条件的值
- ceil(p/k) 也可以写成 (p + k - 1) // k 避免浮点
- 每堆独立计算，向上取整（不满一小时也算一小时）

### 复杂度
- 时间: O(n * log(max(piles)))
- 空间: O(1)
"""

# ── LC 88: Merge Sorted Array ────────────────────────────────────────────
NOTES[88] = r"""## Merge Sorted Array

### 思路
从后往前合并，避免覆盖 nums1 中未处理的元素。三个指针：p1 指向 nums1 有效末尾，p2 指向 nums2 末尾，p 指向 nums1 总末尾。

### 核心代码
```python
def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
    p1, p2, p = m - 1, n - 1, m + n - 1
    while p2 >= 0:
        if p1 >= 0 and nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1
```

### 关键技巧
- 从后往前填充，不需要额外空间
- 只需检查 p2 >= 0，因为如果 p2 用完，nums1 剩余部分已在正确位置
- 原地操作，空间 O(1)

### 复杂度
- 时间: O(m + n)
- 空间: O(1)
"""

# ── LC 680: Valid Palindrome II ──────────────────────────────────────────
NOTES[680] = r"""## Valid Palindrome II

### 思路
双指针从两端向中间移动。遇到不匹配时，尝试删除左边或右边的字符，检查剩余部分是否为回文。

### 核心代码
```python
def validPalindrome(s: str) -> bool:
    def is_palindrome(lo: int, hi: int) -> bool:
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo += 1
            hi -= 1
        return True

    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return is_palindrome(lo + 1, hi) or is_palindrome(lo, hi - 1)
        lo += 1
        hi -= 1
    return True
```

### 关键技巧
- 最多删一个字符，所以只需在第一个不匹配处分叉
- 两个分支只需检查一次，总体仍是 O(n)
- 扩展：最多删 k 个 -> 用 DP (LC 516 变体)

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 2043: Simple Bank System ──────────────────────────────────────────
NOTES[2043] = r"""## Simple Bank System

### 思路
模拟题。维护账户余额数组，实现 transfer、deposit、withdraw 三个操作。关键是参数验证：账户号是否有效、余额是否充足。

### 核心代码
```python
class Bank:
    def __init__(self, balance: list[int]):
        self.balance = balance
        self.n = len(balance)

    def _valid(self, account: int) -> bool:
        return 1 <= account <= self.n

    def transfer(self, account1: int, account2: int, money: int) -> bool:
        if not self._valid(account1) or not self._valid(account2):
            return False
        if self.balance[account1 - 1] < money:
            return False
        self.balance[account1 - 1] -= money
        self.balance[account2 - 1] += money
        return True

    def deposit(self, account: int, money: int) -> bool:
        if not self._valid(account):
            return False
        self.balance[account - 1] += money
        return True

    def withdraw(self, account: int, money: int) -> bool:
        if not self._valid(account):
            return False
        if self.balance[account - 1] < money:
            return False
        self.balance[account - 1] -= money
        return True
```

### 关键技巧
- 账户编号 1-indexed，数组 0-indexed
- 所有操作返回布尔值表示成功/失败
- 边界检查统一提取为 _valid 方法

### 复杂度
- 所有操作: O(1)
- 空间: O(n) - 余额数组
"""

# ── LC 31: Next Permutation ──────────────────────────────────────────────
NOTES[31] = r"""## Next Permutation

### 思路
三步算法：(1) 从右往左找第一个下降点 i（nums[i] < nums[i+1]）；(2) 从右往左找第一个大于 nums[i] 的数 j，交换 i 和 j；(3) 反转 i+1 到末尾。如果没有下降点说明已是最大排列，直接反转整个数组。

### 核心代码
```python
def nextPermutation(nums: list[int]) -> None:
    n = len(nums)
    # Step 1: 找第一个下降点
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1

    if i >= 0:
        # Step 2: 找第一个大于 nums[i] 的数
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]

    # Step 3: 反转 i+1 到末尾
    nums[i + 1:] = reversed(nums[i + 1:])
```

### 关键技巧
- 从右往左找下降点保证找到最小变化
- 交换后 i+1 之后仍然降序，反转变升序得到最小排列
- 原地操作，不需要额外空间

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 1200: Minimum Absolute Difference ─────────────────────────────────
NOTES[1200] = r"""## Minimum Absolute Difference

### 思路
排序后，最小绝对差只可能出现在相邻元素之间。一次遍历找到最小差值，再收集所有差值等于最小差的相邻对。

### 核心代码
```python
def minimumAbsDifference(arr: list[int]) -> list[list[int]]:
    arr.sort()
    min_diff = min(arr[i + 1] - arr[i] for i in range(len(arr) - 1))
    return [[arr[i], arr[i + 1]]
            for i in range(len(arr) - 1)
            if arr[i + 1] - arr[i] == min_diff]
```

### 关键技巧
- 排序后最小差一定在相邻元素间
- 可以一次遍历同时找最小差和收集结果（维护当前最小差）
- 结果自动按升序排列（因为数组已排序）

### 复杂度
- 时间: O(n log n) - 排序
- 空间: O(1) - 不算输出
"""

# ── LC 68: Text Justification ────────────────────────────────────────────
NOTES[68] = r"""## Text Justification

### 思路
贪心逐行填充。每行尽量多放单词（总长度 + 最少空格 <= maxWidth）。非最后一行左对齐分配空格：总空格均分到间隔中，多余空格从左到右分配。最后一行左对齐。

### 核心代码
```python
def fullJustify(words: list[str], maxWidth: int) -> list[str]:
    result = []
    i = 0
    while i < len(words):
        # 贪心确定当前行包含哪些单词
        j = i
        line_len = len(words[i])
        while j + 1 < len(words) and line_len + 1 + len(words[j + 1]) <= maxWidth:
            j += 1
            line_len += 1 + len(words[j])

        # 构建当前行
        num_words = j - i + 1
        total_spaces = maxWidth - sum(len(words[k]) for k in range(i, j + 1))

        if j == len(words) - 1 or num_words == 1:
            # 最后一行或只有一个单词：左对齐
            line = " ".join(words[i:j + 1])
            line += " " * (maxWidth - len(line))
        else:
            # 中间行：均匀分配空格
            gaps = num_words - 1
            space_per_gap = total_spaces // gaps
            extra = total_spaces % gaps
            line = ""
            for k in range(i, j + 1):
                line += words[k]
                if k < j:
                    line += " " * (space_per_gap + (1 if k - i < extra else 0))

        result.append(line)
        i = j + 1
    return result
```

### 关键技巧
- 三种情况：普通行（均匀空格）、单词独占一行（左对齐补空格）、最后一行（左对齐）
- 多余空格从左到右分配（extra 个间隔各多一个空格）
- 字符串拼接注意边界

### 复杂度
- 时间: O(n) - n 为所有字符总数
- 空间: O(n)
"""

# ── LC 1743: Restore the Array From Adjacent Pairs ──────────────────────
NOTES[1743] = r"""## Restore the Array From Adjacent Pairs

### 思路
构建邻接表，度为 1 的节点是数组端点。从任一端点开始 DFS/BFS 遍历即可还原数组。

### 核心代码
```python
from collections import defaultdict

def restoreArray(adjacentPairs: list[list[int]]) -> list[int]:
    graph = defaultdict(list)
    for u, v in adjacentPairs:
        graph[u].append(v)
        graph[v].append(u)

    # 找端点（度为 1 的节点）
    start = next(node for node, neighbors in graph.items() if len(neighbors) == 1)

    result = []
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        visited.add(node)
        result.append(node)
        for nei in graph[node]:
            if nei not in visited:
                stack.append(nei)
    return result
```

### 关键技巧
- 本质是链表/路径图的遍历
- 端点唯一确定（度为 1），遍历顺序唯一
- 用 visited 集合避免回头

### 复杂度
- 时间: O(n)
- 空间: O(n)
"""

# ── LC 1244: Design A Leaderboard ────────────────────────────────────────
NOTES[1244] = r"""## Design A Leaderboard

### 思路
HashMap 存储 playerId -> score。addScore 累加分数，top(K) 取前 K 大的分数之和，reset 删除玩家。

### 核心代码
```python
import heapq
from collections import defaultdict

class Leaderboard:
    def __init__(self):
        self.scores: dict[int, int] = defaultdict(int)

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] += score

    def top(self, K: int) -> int:
        return sum(heapq.nlargest(K, self.scores.values()))

    def reset(self, playerId: int) -> None:
        del self.scores[playerId]
```

### 关键技巧
- top(K) 用 heapq.nlargest 比完全排序更优：O(n log K) vs O(n log n)
- addScore 是累加不是覆盖
- 高频调用可用 SortedList 优化 top(K) 到 O(K)

### 复杂度
- addScore: O(1), top: O(n log K), reset: O(1)
- 空间: O(n)
"""

# ── LC 26: Remove Duplicates from Sorted Array ──────────────────────────
NOTES[26] = r"""## Remove Duplicates from Sorted Array

### 思路
双指针原地去重。慢指针 k 指向下一个要写入的位置，快指针 i 遍历数组。遇到新值就写入并移动 k。

### 核心代码
```python
def removeDuplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    k = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1]:
            nums[k] = nums[i]
            k += 1
    return k
```

### 关键技巧
- 数组已排序，重复元素一定相邻
- 返回去重后的长度 k，前 k 个元素是结果
- 扩展：允许最多 2 个重复 -> LC 80

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""


def main() -> None:
    """Insert notes into the database."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    updated = 0
    for lc_id, note in NOTES.items():
        note = note.strip()
        cur.execute(
            "UPDATE problems SET notes = ?, is_completed = 1 WHERE leetcode_id = ?",
            (note, lc_id),
        )
        if cur.rowcount:
            updated += 1
            print(f"  [OK] LC {lc_id} - notes updated ({len(note)}c)")
        else:
            print(f"  [MISS] LC {lc_id} - not found in DB")
    conn.commit()
    conn.close()
    print(f"\nBatch 1A: {updated}/{len(NOTES)} problems updated")


if __name__ == "__main__":
    main()
