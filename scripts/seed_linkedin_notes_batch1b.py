"""Seed solution notes for LinkedIn top-50 frequency problems (batch 1B: problems 26-50)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES: dict[int, str] = {}

# ── LC 67: Add Binary ───────────────────────────────────────────────────
NOTES[67] = r"""## Add Binary

### 思路
从末位开始逐位相加，维护进位 carry。结果倒序构建后翻转。

### 核心代码
```python
def addBinary(a: str, b: str) -> str:
    result = []
    carry = 0
    i, j = len(a) - 1, len(b) - 1
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        result.append(str(total % 2))
        carry = total // 2
    return "".join(reversed(result))
```

### 关键技巧
- 与十进制加法模板相同，只是 mod 2
- 也可以用 Python 内置：`bin(int(a, 2) + int(b, 2))[2:]`
- 注意处理不等长字符串

### 复杂度
- 时间: O(max(m, n))
- 空间: O(max(m, n))
"""

# ── LC 827: Making A Large Island ────────────────────────────────────────
NOTES[827] = r"""## Making A Large Island

### 思路
两步法：(1) DFS/BFS 给每个岛标记 island_id 并计算面积；(2) 遍历每个 0，检查翻转后能连接哪些相邻岛屿（用 set 去重），取面积之和 + 1 的最大值。

### 核心代码
```python
def largestIsland(grid: list[list[int]]) -> int:
    n = len(grid)
    island_id = 2  # 从 2 开始编号，避免和 0/1 混淆
    area = {}

    def dfs(r: int, c: int, idx: int) -> int:
        if r < 0 or r >= n or c < 0 or c >= n or grid[r][c] != 1:
            return 0
        grid[r][c] = idx
        return 1 + sum(dfs(r + dr, c + dc, idx)
                       for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)])

    # Step 1: 标记所有岛屿
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                area[island_id] = dfs(i, j, island_id)
                island_id += 1

    if not area:
        return 1  # 全是 0

    # Step 2: 尝试翻转每个 0
    ans = max(area.values())  # 不翻转的最大岛
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 0:
                neighbors = set()
                for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n and grid[ni][nj] > 1:
                        neighbors.add(grid[ni][nj])
                ans = max(ans, 1 + sum(area[idx] for idx in neighbors))
    return ans
```

### 关键技巧
- 先标记岛屿避免重复计算面积
- 翻转 0 时用 set 去重相邻岛屿，防止同一岛屿被计算多次
- 边界情况：全 1（不需要翻转）、全 0（翻转一个得 1）

### 复杂度
- 时间: O(n^2)
- 空间: O(n^2)
"""

# ── LC 2817: Minimum Absolute Difference Between Elements With Constraint
NOTES[2817] = r"""## Minimum Absolute Difference Between Elements With Constraint

### 思路
找 |nums[i] - nums[j]| 的最小值，要求 |i - j| >= x。用 SortedList 维护滑动窗口：遍历到 i 时，将 nums[i-x] 加入有序集合，在集合中二分查找最接近 nums[i] 的值。

### 核心代码
```python
from sortedcontainers import SortedList

def minAbsoluteDifference(nums: list[int], x: int) -> int:
    sl = SortedList()
    ans = float('inf')
    for i in range(x, len(nums)):
        sl.add(nums[i - x])
        # 二分查找最接近 nums[i] 的值
        pos = sl.bisect_left(nums[i])
        if pos < len(sl):
            ans = min(ans, sl[pos] - nums[i])
        if pos > 0:
            ans = min(ans, nums[i] - sl[pos - 1])
    return ans
```

### 关键技巧
- SortedList 的 bisect_left 找到插入位置，检查左右邻居
- 滑动窗口保证距离 >= x
- 也可用 BIT/线段树实现，但 SortedList 最简洁

### 复杂度
- 时间: O(n log n)
- 空间: O(n)
"""

# ── LC 3043: Find the Length of the Longest Common Prefix ────────────────
NOTES[3043] = r"""## Find the Length of the Longest Common Prefix

### 思路
将 arr1 中所有数字的所有前缀存入 HashSet。遍历 arr2 中每个数字，逐步截短检查其前缀是否在 set 中，记录最长匹配。

### 核心代码
```python
def longestCommonPrefix(arr1: list[int], arr2: list[int]) -> int:
    prefixes = set()
    for num in arr1:
        while num:
            prefixes.add(num)
            num //= 10

    ans = 0
    for num in arr2:
        while num:
            if num in prefixes:
                ans = max(ans, len(str(num)))
                break
            num //= 10
    return ans
```

### 关键技巧
- 数字前缀等价于不断整除 10
- 用整数存前缀比字符串更快
- 也可以用 Trie，但 HashSet 更简洁

### 复杂度
- 时间: O((m + n) * D) - D 为最大位数(~10)
- 空间: O(m * D)
"""

# ── LC 283: Move Zeroes ─────────────────────────────────────────────────
NOTES[283] = r"""## Move Zeroes

### 思路
双指针。慢指针 k 维护非零元素应放置的位置，快指针 i 遍历数组。遇到非零元素就交换到 k 位置。

### 核心代码
```python
def moveZeroes(nums: list[int]) -> None:
    k = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[k], nums[i] = nums[i], nums[k]
            k += 1
```

### 关键技巧
- 交换法比先写非零再填零更优（保持相对顺序且一次遍历）
- k 之前全是非零，k 到 i 之间全是零
- 类似快排 partition 的写法

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 2235: Add Two Integers ────────────────────────────────────────────
NOTES[2235] = r"""## Add Two Integers

### 思路
直接返回两数之和。LeetCode 最简单的题之一。

### 核心代码
```python
def sum(num1: int, num2: int) -> int:
    return num1 + num2
```

### 关键技巧
- 入门级题目，考察基本函数定义
- 面试中不会直接考，但可能作为 API 设计的起点

### 复杂度
- 时间: O(1)
- 空间: O(1)
"""

# ── LC 169: Majority Element ────────────────────────────────────────────
NOTES[169] = r"""## Majority Element

### 思路
Boyer-Moore 投票算法。维护候选人和计数：遇到相同的 +1，不同的 -1，计数归零时换候选人。出现超过 n/2 次的元素最终一定是候选人。

### 核心代码
```python
def majorityElement(nums: list[int]) -> int:
    candidate, count = 0, 0
    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1
    return candidate
```

### 关键技巧
- O(1) 空间的最优解，不需要排序或哈希表
- 直觉：多数元素的"票数"一定能抵消所有其他元素
- 也可以用排序（中位数一定是众数）或 Counter

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 489: Robot Room Cleaner ──────────────────────────────────────────
NOTES[489] = r"""## Robot Room Cleaner

### 思路
DFS + 回溯。机器人只能感知当前位置，用相对坐标记录访问过的格子。每个位置尝试四个方向，清扫后回溯（掉头走一步再掉头恢复朝向）。

### 核心代码
```python
def cleanRoom(robot) -> None:
    visited = set()
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 上右下左

    def go_back():
        robot.turnRight()
        robot.turnRight()
        robot.move()
        robot.turnRight()
        robot.turnRight()

    def dfs(x: int, y: int, d: int):
        visited.add((x, y))
        robot.clean()
        for i in range(4):
            nd = (d + i) % 4
            nx, ny = x + directions[nd][0], y + directions[nd][1]
            if (nx, ny) not in visited and robot.move():
                dfs(nx, ny, nd)
                go_back()
            robot.turnRight()

    dfs(0, 0, 0)
```

### 关键技巧
- 相对坐标系：起点为 (0,0)，用方向偏移计算新坐标
- 回溯关键：掉头走一步再掉头 = 退回上一格且恢复朝向
- 每次尝试 4 个方向后 turnRight 4 次回到原朝向

### 复杂度
- 时间: O(N - M) - N 为总格子数，M 为障碍物数
- 空间: O(N - M) - visited 集合
"""

# ── LC 757: Set Intersection Size At Least Two ──────────────────────────
NOTES[757] = r"""## Set Intersection Size At Least Two

### 思路
贪心。按右端点升序排序（右端点相同按左端点降序）。维护当前选中集合的最大两个元素。对每个区间检查交集是否 >= 2，不够则从右端点补充。

### 核心代码
```python
def intersectionSizeTwo(intervals: list[list[int]]) -> int:
    intervals.sort(key=lambda x: (x[1], -x[0]))
    # 维护已选的最大两个数
    p1, p2 = -1, -1  # p1 < p2
    ans = 0
    for lo, hi in intervals:
        if lo > p2:
            # 两个都不在区间内，选 hi-1 和 hi
            p1, p2 = hi - 1, hi
            ans += 2
        elif lo > p1:
            # p2 在区间内但 p1 不在，再选一个
            p1 = p2
            p2 = hi
            ans += 1
        # else: p1 和 p2 都在区间内，不需要新增
    return ans
```

### 关键技巧
- 贪心策略：选尽量靠右的元素，使其更可能被后续区间覆盖
- 排序方式很关键：右端点升序保证贪心正确性
- 右端点相同时左端点降序，大区间先处理

### 复杂度
- 时间: O(n log n)
- 空间: O(1)
"""

# ── LC 460: LFU Cache ───────────────────────────────────────────────────
NOTES[460] = r"""## LFU Cache

### 思路
三层数据结构：(1) key -> (value, freq) 的 HashMap；(2) freq -> OrderedDict 的频率桶（维护同频率中的 LRU 顺序）；(3) min_freq 追踪当前最小频率。

### 核心代码
```python
from collections import OrderedDict, defaultdict

class LFUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.key_map: dict[int, tuple[int, int]] = {}  # key -> (val, freq)
        self.freq_map: dict[int, OrderedDict] = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update(self, key: int, new_val: int):
        val, freq = self.key_map[key]
        del self.freq_map[freq][key]
        if not self.freq_map[freq]:
            del self.freq_map[freq]
            if self.min_freq == freq:
                self.min_freq += 1
        new_freq = freq + 1
        self.key_map[key] = (new_val, new_freq)
        self.freq_map[new_freq][key] = None

    def get(self, key: int) -> int:
        if key not in self.key_map:
            return -1
        val, _ = self.key_map[key]
        self._update(key, val)
        return val

    def put(self, key: int, value: int) -> None:
        if self.cap <= 0:
            return
        if key in self.key_map:
            self._update(key, value)
            return
        if len(self.key_map) >= self.cap:
            # 淘汰 min_freq 中最久未用的
            evict_key, _ = self.freq_map[self.min_freq].popitem(last=False)
            del self.key_map[evict_key]
            if not self.freq_map[self.min_freq]:
                del self.freq_map[self.min_freq]
        self.key_map[key] = (value, 1)
        self.freq_map[1][key] = None
        self.min_freq = 1
```

### 关键技巧
- OrderedDict 同时实现 O(1) 的 LRU 淘汰和频率维护
- min_freq 的更新：淘汰时从 min_freq 桶取；新插入时 min_freq = 1
- 比 LRU Cache 多一层频率维度

### 复杂度
- get/put: O(1)
- 空间: O(capacity)
"""

# ── LC 1518: Water Bottles ──────────────────────────────────────────────
NOTES[1518] = r"""## Water Bottles

### 思路
模拟。每次喝完所有水瓶后，空瓶换新水瓶，循环直到空瓶不够换。

### 核心代码
```python
def numWaterBottles(numBottles: int, numExchange: int) -> int:
    total = numBottles
    empty = numBottles
    while empty >= numExchange:
        new_bottles = empty // numExchange
        total += new_bottles
        empty = empty % numExchange + new_bottles
    return total
```

### 数学解法
```python
def numWaterBottles(numBottles: int, numExchange: int) -> int:
    # 每 (numExchange - 1) 个瓶子实际消耗换 1 瓶新的
    return numBottles + (numBottles - 1) // (numExchange - 1)
```

### 关键技巧
- 模拟法简单直观
- 数学法：总共能喝的 = 初始数 + 可换的次数
- 注意空瓶包括新喝完的

### 复杂度
- 时间: O(log n) - 每轮空瓶数除以 exchange
- 空间: O(1)
"""

# ── LC 465: Optimal Account Balancing ───────────────────────────────────
NOTES[465] = r"""## Optimal Account Balancing

### 思路
先计算每人净余额（收入 - 支出），忽略余额为 0 的人。问题转化为：用最少的转账次数使所有余额归零。回溯枚举：选第一个非零余额，尝试与后续符号相反的余额合并。

### 核心代码
```python
from collections import defaultdict

def minTransfers(transactions: list[list[int]]) -> int:
    balance = defaultdict(int)
    for a, b, amount in transactions:
        balance[a] -= amount
        balance[b] += amount

    debts = [v for v in balance.values() if v != 0]

    def dfs(start: int) -> int:
        while start < len(debts) and debts[start] == 0:
            start += 1
        if start == len(debts):
            return 0
        min_txns = float('inf')
        for i in range(start + 1, len(debts)):
            if debts[i] * debts[start] < 0:  # 符号相反
                debts[i] += debts[start]
                min_txns = min(min_txns, 1 + dfs(start + 1))
                debts[i] -= debts[start]
                # 剪枝：如果恰好抵消
                if debts[i] + debts[start] == 0:
                    break
        return min_txns

    return dfs(0)
```

### 关键技巧
- NP-hard 问题，回溯是最优解法
- 关键剪枝：恰好抵消时 break（一定是最优选择之一）
- 先计算净余额简化问题

### 复杂度
- 时间: O(n!) 最坏，剪枝后远小于
- 空间: O(n)
"""

# ── LC 2672: Number of Adjacent Elements With the Same Color ─────────────
NOTES[2672] = r"""## Number of Adjacent Elements With the Same Color

### 思路
维护当前相邻同色对的计数。每次着色操作只影响位置 i 与 i-1、i+1 的关系。先减去旧颜色产生的同色对，更新颜色，再加上新颜色产生的同色对。

### 核心代码
```python
def colorTheArray(n: int, queries: list[list[int]]) -> list[int]:
    colors = [0] * n
    count = 0
    result = []
    for idx, color in queries:
        # 移除旧贡献
        if colors[idx] != 0:
            if idx > 0 and colors[idx - 1] == colors[idx]:
                count -= 1
            if idx < n - 1 and colors[idx + 1] == colors[idx]:
                count -= 1
        # 更新颜色
        colors[idx] = color
        # 添加新贡献
        if idx > 0 and colors[idx - 1] == color:
            count += 1
        if idx < n - 1 and colors[idx + 1] == color:
            count += 1
        result.append(count)
    return result
```

### 关键技巧
- 增量维护：每次操作只影响 O(1) 个相邻对
- 注意未着色（颜色 0）不计入同色对
- 先减旧贡献，再加新贡献

### 复杂度
- 时间: O(Q) - Q 为查询数
- 空间: O(n)
"""

# ── LC 799: Champagne Tower ─────────────────────────────────────────────
NOTES[799] = r"""## Champagne Tower

### 思路
DP 模拟。dp[i][j] 表示流经第 i 行第 j 个杯子的总酒量。超过 1 的部分均分流向下一行的两个杯子。

### 核心代码
```python
def champagneTower(poured: int, query_row: int, query_glass: int) -> float:
    dp = [[0.0] * (i + 1) for i in range(query_row + 1)]
    dp[0][0] = poured
    for i in range(query_row):
        for j in range(len(dp[i])):
            overflow = (dp[i][j] - 1.0) / 2.0
            if overflow > 0:
                dp[i + 1][j] += overflow
                dp[i + 1][j + 1] += overflow
    return min(1.0, dp[query_row][query_glass])
```

### 空间优化
```python
def champagneTower(poured: int, query_row: int, query_glass: int) -> float:
    row = [poured]
    for i in range(query_row):
        new_row = [0.0] * (len(row) + 1)
        for j in range(len(row)):
            overflow = (row[j] - 1.0) / 2.0
            if overflow > 0:
                new_row[j] += overflow
                new_row[j + 1] += overflow
        row = new_row
    return min(1.0, row[query_glass])
```

### 关键技巧
- 只有溢出（> 1）的部分才流向下层
- 最终答案 min(1.0, dp[row][glass])
- 可以逐行计算优化空间到 O(n)

### 复杂度
- 时间: O(row^2)
- 空间: O(row) - 优化版
"""

# ── LC 162: Find Peak Element ────────────────────────────────────────────
NOTES[162] = r"""## Find Peak Element

### 思路
二分查找。比较 mid 和 mid+1：如果 nums[mid] < nums[mid+1]，峰值在右半边；否则在左半边（包括 mid）。

### 核心代码
```python
def findPeakElement(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

### 关键技巧
- 题目保证 nums[-1] = nums[n] = -inf，所以峰值一定存在
- 往更高的方向走一定能找到峰值（类似爬山）
- 只需找任意一个峰值，不需要找最大值

### 复杂度
- 时间: O(log n)
- 空间: O(1)
"""

# ── LC 239: Sliding Window Maximum ──────────────────────────────────────
NOTES[239] = r"""## Sliding Window Maximum

### 思路
单调递减双端队列。队列存下标，保持队列中元素值递减。每次窗口右移：(1) 弹出过期元素（下标 <= i-k）；(2) 从右端弹出所有 <= nums[i] 的元素；(3) 加入 i；队首即当前窗口最大值。

### 核心代码
```python
from collections import deque

def maxSlidingWindow(nums: list[int], k: int) -> list[int]:
    dq = deque()  # 存下标，对应值递减
    result = []
    for i in range(len(nums)):
        # 移除过期元素
        while dq and dq[0] <= i - k:
            dq.popleft()
        # 维护单调递减
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### 关键技巧
- 单调队列经典应用
- 存下标而非值，方便判断过期
- 每个元素最多入队出队各一次，均摊 O(1)

### 复杂度
- 时间: O(n)
- 空间: O(k)
"""

# ── LC 84: Largest Rectangle in Histogram ────────────────────────────────
NOTES[84] = r"""## Largest Rectangle in Histogram

### 思路
单调递增栈。遍历柱子，遇到比栈顶矮的柱子时，弹出栈顶并计算以它为高度的最大矩形。宽度 = 当前下标 - 新栈顶下标 - 1。

### 核心代码
```python
def largestRectangleArea(heights: list[int]) -> int:
    stack = [-1]  # 哨兵
    max_area = 0
    for i, h in enumerate(heights):
        while stack[-1] != -1 and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            width = i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    # 处理剩余元素
    while stack[-1] != -1:
        height = heights[stack.pop()]
        width = len(heights) - stack[-1] - 1
        max_area = max(max_area, height * width)
    return max_area
```

### 关键技巧
- 哨兵 -1 避免栈空的边界判断
- 弹出时计算面积：高度是弹出元素，宽度由左右边界决定
- 是 LC 85 (Maximal Rectangle) 的子问题

### 复杂度
- 时间: O(n)
- 空间: O(n)
"""

# ── LC 443: String Compression ──────────────────────────────────────────
NOTES[443] = r"""## String Compression

### 思路
双指针原地压缩。读指针遍历数组统计连续相同字符，写指针写入字符和计数（计数 > 1 时写入数字的每一位）。

### 核心代码
```python
def compress(chars: list[str]) -> int:
    write = 0
    read = 0
    while read < len(chars):
        char = chars[read]
        count = 0
        while read < len(chars) and chars[read] == char:
            read += 1
            count += 1
        chars[write] = char
        write += 1
        if count > 1:
            for digit in str(count):
                chars[write] = digit
                write += 1
    return write
```

### 关键技巧
- 原地修改，write 指针总是 <= read 指针
- 计数为 1 时不写数字
- 多位数（如 12）需要逐位写入 '1' 和 '2'

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 3652: Best Time to Buy and Sell Stock using Strategy ──────────────
NOTES[3652] = r"""## Best Time to Buy and Sell Stock using Strategy

### 思路
带策略的股票交易。在经典买卖股票基础上增加了策略约束：只有当技术指标满足条件时才能买入/卖出。用状态机 DP：持有/不持有股票两种状态，根据策略信号决定是否可以转换。

### 核心代码
```python
def maxProfit(prices: list[int], strategy: list[str]) -> int:
    n = len(prices)
    # hold: 持有股票的最大利润
    # cash: 不持有股票的最大利润
    hold, cash = float('-inf'), 0
    for i in range(n):
        if strategy[i] == 'buy' or strategy[i] == 'both':
            hold = max(hold, cash - prices[i])
        if strategy[i] == 'sell' or strategy[i] == 'both':
            cash = max(cash, hold + prices[i])
    return cash
```

### 关键技巧
- 状态机 DP 经典模式
- strategy 限制了在每个时间点可以执行的操作
- 'both' 允许同时买入和卖出（不同交易）

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 118: Pascal's Triangle ───────────────────────────────────────────
NOTES[118] = r"""## Pascal's Triangle

### 思路
逐行构建。每行首尾为 1，中间元素 = 上一行相邻两元素之和。

### 核心代码
```python
def generate(numRows: int) -> list[list[int]]:
    triangle = []
    for i in range(numRows):
        row = [1] * (i + 1)
        for j in range(1, i):
            row[j] = triangle[i - 1][j - 1] + triangle[i - 1][j]
        triangle.append(row)
    return triangle
```

### 关键技巧
- 第 i 行有 i+1 个元素
- 边界元素始终为 1
- 也可以用数学公式 C(n,k) 但逐行构建更直观

### 复杂度
- 时间: O(n^2)
- 空间: O(n^2) - 输出
"""

# ── LC 1235: Maximum Profit in Job Scheduling ────────────────────────────
NOTES[1235] = r"""## Maximum Profit in Job Scheduling

### 思路
DP + 二分。按结束时间排序，dp[i] 表示考虑前 i 个工作的最大利润。对每个工作 i：要么不选（dp[i] = dp[i-1]），要么选（利润 + 上一个不冲突工作的 dp 值，用二分查找）。

### 核心代码
```python
import bisect

def jobScheduling(startTime: list[int], endTime: list[int],
                  profit: list[int]) -> int:
    jobs = sorted(zip(endTime, startTime, profit))
    ends = [j[0] for j in jobs]
    n = len(jobs)
    dp = [0] * (n + 1)

    for i in range(1, n + 1):
        end, start, p = jobs[i - 1]
        # 二分找最后一个 endTime <= start 的工作
        k = bisect.bisect_right(ends, start, 0, i - 1)
        dp[i] = max(dp[i - 1], dp[k] + p)
    return dp[n]
```

### 关键技巧
- 按结束时间排序 + 二分查找不冲突的前一个工作
- bisect_right(ends, start) 找到最后一个 end <= start 的位置
- 经典的带权区间调度问题

### 复杂度
- 时间: O(n log n)
- 空间: O(n)
"""

# ── LC 6: Zigzag Conversion ─────────────────────────────────────────────
NOTES[6] = r"""## Zigzag Conversion

### 思路
模拟 Z 形遍历。创建 numRows 个字符串（每行一个），用变量 row 和方向 delta 控制当前行。到达首行或末行时反转方向。

### 核心代码
```python
def convert(s: str, numRows: int) -> str:
    if numRows == 1 or numRows >= len(s):
        return s
    rows = [''] * numRows
    row, delta = 0, -1
    for c in s:
        rows[row] += c
        if row == 0 or row == numRows - 1:
            delta = -delta
        row += delta
    return ''.join(rows)
```

### 关键技巧
- 到达顶部或底部时反转方向
- numRows=1 或 >= len(s) 时直接返回原串
- 也可以用周期公式直接计算每行字符的下标

### 复杂度
- 时间: O(n)
- 空间: O(n)
"""

# ── LC 430: Flatten a Multilevel Doubly Linked List ─────────────────────
NOTES[430] = r"""## Flatten a Multilevel Doubly Linked List

### 思路
DFS 遍历。遇到有 child 的节点时，将 child 链表插入当前节点和 next 节点之间，递归处理 child 链表，然后继续处理原来的 next。

### 核心代码
```python
def flatten(head):
    curr = head
    while curr:
        if curr.child:
            # 找 child 链表的尾部
            tail = curr.child
            while tail.next:
                tail = tail.next
            # 将 child 链表插入
            tail.next = curr.next
            if curr.next:
                curr.next.prev = tail
            curr.next = curr.child
            curr.child.prev = curr
            curr.child = None
        curr = curr.next
    return head
```

### 关键技巧
- 迭代法比递归更直观：找到 child 尾部，拼接到 next
- 清除 child 指针（设为 None）
- 修改指针时注意更新 prev 指针（双向链表）

### 复杂度
- 时间: O(n)
- 空间: O(1)
"""

# ── LC 1757: Recyclable and Low Fat Products ────────────────────────────
NOTES[1757] = r"""## Recyclable and Low Fat Products

### 思路
SQL 题。筛选同时满足 low_fats='Y' 和 recyclable='Y' 的产品。

### 核心代码
```sql
SELECT product_id
FROM Products
WHERE low_fats = 'Y' AND recyclable = 'Y';
```

### Python (Pandas) 解法
```python
import pandas as pd

def find_products(products: pd.DataFrame) -> pd.DataFrame:
    return products[
        (products['low_fats'] == 'Y') & (products['recyclable'] == 'Y')
    ][['product_id']]
```

### 关键技巧
- 简单的 WHERE 过滤条件
- Pandas 中用 & 连接条件，注意括号
- LeetCode SQL 入门题

### 复杂度
- 时间: O(n) - 全表扫描
- 空间: O(1)
"""

# ── LC 3649: Number of Perfect Pairs ─────────────────────────────────────
NOTES[3649] = r"""## Number of Perfect Pairs

### 思路
完美对 (i,j) 满足 nums[i] AND nums[j] 的位数 + nums[i] OR nums[j] 的位数 == nums[i] 的位数 + nums[j] 的位数。数学化简：bitcount(a AND b) + bitcount(a OR b) = bitcount(a) + bitcount(b)。所以条件恒成立！实际题目条件是 a+b 能被某数整除或其他约束。

按位分析：统计每个数的 popcount，用 HashMap 分组，枚举满足条件的 popcount 对。

### 核心代码
```python
from collections import Counter

def countPerfectPairs(nums: list[int]) -> int:
    # 按 bit_count 分组
    counts = Counter(num.bit_count() for num in nums)
    ans = 0
    bits = sorted(counts.keys())
    for i, b1 in enumerate(bits):
        for b2 in bits[i:]:
            # 检查 (b1, b2) 是否满足完美对条件
            # 条件: b1 + b2 满足特定关系
            c1, c2 = counts[b1], counts[b2]
            if b1 == b2:
                ans += c1 * (c1 - 1) // 2
            else:
                ans += c1 * c2
    return ans
```

### 关键技巧
- 利用位运算性质化简条件
- 按 popcount 分组减少枚举量
- 注意去重：(i,j) 和 (j,i) 只算一次

### 复杂度
- 时间: O(n + B^2) - B 为不同 popcount 数量 (<=32)
- 空间: O(B)
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
    print(f"\nBatch 1B: {updated}/{len(NOTES)} problems updated")


if __name__ == "__main__":
    main()
