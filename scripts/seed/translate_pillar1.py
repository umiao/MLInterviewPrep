# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Translate Pillar 1 (Coding & Algorithms) nodes 44-63 to Chinese."""
import re
import sqlite3

DB_PATH = "MLInterviewPrep/data/mle_prep.db"

# Node 45 is empty - write new content
NODE_45_CONTENT = r"""# HashMap / HashSet

## Overview
**HashMap（哈希映射）** 和 **HashSet（哈希集合）** 是面试中最高频的数据结构之一，提供平均 $$O(1)$$ 的查找、插入和删除操作。哈希表是解决"快速查找"类问题的核心工具，广泛应用于去重、计数、分组、缓存等场景。对于 MLE 面试，哈希表不仅是算法题的基石，也是实际工程中特征索引、embedding 查找、数据去重的底层实现。

## Core Concepts

### Hash Function Design
**Hash Function（哈希函数）** 将任意大小的键映射到固定范围的整数索引：

$$
h(key) = \text{hash}(key) \mod m
$$

其中 $m$ 是哈希表的桶数量。一个好的哈希函数需要满足以下性质：
- **确定性**：相同的键总是产生相同的哈希值
- **均匀分布**：键应尽可能均匀地分布在所有桶中，减少冲突
- **高效计算**：哈希函数的计算必须是 $$O(1)$$

Python 中内置对象的 `__hash__()` 方法实现了高质量的哈希函数。对于自定义对象，需要同时实现 `__hash__()` 和 `__eq__()` 以确保哈希表正确工作。

**常见哈希函数设计**：
- **整数**：直接取模或乘法哈希 $$h(k) = \lfloor m \cdot (k \cdot A \mod 1) \rfloor$$，其中 $A$ 是一个无理数常量（如黄金比例的倒数）
- **字符串**：多项式滚动哈希 $$h(s) = \sum_{i=0}^{n-1} s[i] \cdot p^i \mod m$$，其中 $p$ 是一个质数基数

### Collision Resolution
当两个不同的键映射到同一个桶时，发生 **Collision（哈希冲突）**。主要有两种解决策略：

#### Chaining（链地址法）
每个桶维护一个链表（或其他动态数据结构），所有映射到同一桶的元素存储在该链表中。

**优点**：
- 实现简单，删除操作方便
- 负载因子可以大于 1
- 对哈希函数的质量不太敏感

**缺点**：
- 链表节点需要额外内存
- 缓存不友好（链表节点分散在内存中）

**最坏情况**：所有元素映射到同一桶，退化为 $$O(n)$$ 查找。Java 8 的 HashMap 在链表长度超过 8 时将链表转为红黑树，保证最坏 $$O(\log n)$$。

#### Open Addressing（开放地址法）
所有元素直接存储在哈希表数组中。冲突时按照探测序列寻找下一个空位：

- **Linear Probing（线性探测）**：$$h(k, i) = (h(k) + i) \mod m$$。简单但容易产生 **Primary Clustering（一次聚集）**
- **Quadratic Probing（二次探测）**：$$h(k, i) = (h(k) + c_1 i + c_2 i^2) \mod m$$。减少一次聚集但可能产生二次聚集
- **Double Hashing（双重哈希）**：$$h(k, i) = (h_1(k) + i \cdot h_2(k)) \mod m$$。冲突分布最均匀

**优点**：
- 缓存友好（数据连续存储）
- 不需要额外的指针空间

**缺点**：
- 负载因子不能超过 1
- 删除操作复杂（需要标记为"已删除"而非直接清空）

Python 的 `dict` 内部使用开放地址法（紧凑字典实现），结合了伪随机探测序列。

### Load Factor
**Load Factor（负载因子）** 定义为：

$$
\alpha = \frac{n}{m}
$$

其中 $n$ 是存储的元素数量，$m$ 是桶的数量。

- 当 $\alpha$ 增大时，冲突概率增加，性能下降
- 当 $\alpha$ 超过阈值时（通常 0.75），触发 **Rehashing（重新哈希）**：创建一个更大的哈希表（通常 2 倍），重新插入所有元素
- Rehashing 的代价是 $$O(n)$$，但由于触发频率低，**Amortized（均摊）** 插入仍然是 $$O(1)$$

### Amortized O(1) Analysis
**Amortized Analysis（均摊分析）** 证明哈希表操作的平均时间复杂度为 $$O(1)$$：

- 假设每次 rehashing 将容量翻倍
- 从空表开始插入 $n$ 个元素，rehashing 发生在容量 1, 2, 4, 8, ..., $n$ 时
- 总 rehashing 代价：$$1 + 2 + 4 + \cdots + n = 2n - 1 = O(n)$$
- 每次插入的均摊代价：$$O(n) / n = O(1)$$

这与动态数组（Python `list`）的 `append` 操作的均摊分析原理相同。

## Implementation

```python
class HashMap:
    \"\"\"Simple hash map with chaining for collision resolution.\"\"\"

    def __init__(self, capacity: int = 16, load_factor: float = 0.75) -> None:
        self.capacity = capacity
        self.load_factor = load_factor
        self.size = 0
        self.buckets: list[list[tuple]] = [[] for _ in range(capacity)]

    def _hash(self, key) -> int:
        return hash(key) % self.capacity

    def put(self, key, value) -> None:
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, value)
                return
        self.buckets[idx].append((key, value))
        self.size += 1
        if self.size > self.capacity * self.load_factor:
            self._resize()

    def get(self, key, default=None):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return default

    def _resize(self) -> None:
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two Sum | 配对查找问题 | 遍历数组，用哈希表存储"需要的补数"，$$O(n)$$ 时间 |
| Group Anagram | 分组归类问题 | 将排序后的字符串作为键，原始字符串作为值分组 |
| LRU Cache | 缓存淘汰策略 | **HashMap + Doubly Linked List（双向链表）**，$$O(1)$$ 读写 |
| Frequency Count | 计数和统计问题 | `collections.Counter` 是面试中最常用的工具 |
| Prefix Sum + HashMap | 子数组求和问题 | 将前缀和存入哈希表，查找 `prefix_sum - target` |
| Two Pointers + HashSet | 去重和判重问题 | HashSet 提供 $$O(1)$$ 的存在性判断 |

### Two Sum Pattern
经典 Two Sum 问题展示了哈希表的核心思想 -- 用空间换时间：

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    # O(n) time, O(n) space using hash map.
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### Group Anagram Pattern
利用哈希表对具有相同特征的元素进行分组：

```python
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    # Group strings that are anagrams. O(n * k log k).
    groups: dict[str, list[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())
```

### LRU Cache Pattern
**LRU (Least Recently Used，最近最少使用)** 缓存结合了哈希表和双向链表：

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.cache: OrderedDict[int, int] = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

### Common Interview Questions
- [ ] Two Sum（哈希表经典入门题）
- [ ] Group Anagrams（分组归类）
- [ ] LRU Cache（OrderedDict 或手写双向链表 + 哈希表）
- [ ] Longest Consecutive Sequence（HashSet 查找连续序列）
- [ ] Subarray Sum Equals K（前缀和 + 哈希表）
- [ ] Contains Duplicate II（滑动窗口 + HashSet）
- [ ] Design HashMap（底层实现）

## Comparisons

| Aspect | HashMap (dict) | HashSet (set) | Sorted Dict (BST) | Array |
|--------|---------------|--------------|-------------------|-------|
| 查找 | $$O(1)$$ 平均 | $$O(1)$$ 平均 | $$O(\log n)$$ | $$O(n)$$ |
| 插入 | $$O(1)$$ 均摊 | $$O(1)$$ 均摊 | $$O(\log n)$$ | $$O(1)$$ 末尾 |
| 删除 | $$O(1)$$ 平均 | $$O(1)$$ 平均 | $$O(\log n)$$ | $$O(n)$$ |
| 有序遍历 | 否（Python 3.7+ 保持插入序） | 否 | 是 | 否（除非已排序） |
| 空间 | $$O(n)$$ | $$O(n)$$ | $$O(n)$$ | $$O(n)$$ |
| 最佳场景 | 键值映射、频率统计 | 去重、存在性检查 | 需要有序操作 | 索引访问 |

## Common Pitfalls
- **可变对象作为键**：Python 中 `list` 和 `dict` 不可哈希，不能作为字典键。使用 `tuple` 代替 `list`，使用 `frozenset` 代替 `set`
- **自定义对象哈希**：如果重写 `__eq__` 但不重写 `__hash__`，对象将变为不可哈希。两个方法必须一致：`a == b` 则 `hash(a) == hash(b)`
- **哈希冲突导致性能退化**：在极端情况下（如精心构造的输入），哈希表可退化为 $$O(n)$$。面试中通常不需要担心，但需要知道这个理论限制
- **遍历时修改字典**：在迭代字典时添加或删除键会引发 `RuntimeError`。先收集要修改的键，再进行修改
- **忽略负载因子**：手动实现哈希表时，忘记在负载因子过高时进行 rehashing 会导致性能严重下降

## Advanced Patterns
- **Consistent Hashing（一致性哈希）**：在分布式系统中用于均匀分配数据到多个节点。当节点增减时，只需重新分配 $$O(K/n)$$ 个键（$K$ 是总键数，$n$ 是节点数）。广泛应用于分布式缓存（如 Memcached、Redis Cluster）
- **Bloom Filter（布隆过滤器）**：一种概率数据结构，用于高效的"可能存在"检测。使用多个哈希函数映射到一个位数组，空间效率极高但有假阳性（无假阴性）。应用于网络爬虫 URL 去重、数据库查询优化
- **Cuckoo Hashing（布谷鸟哈希）**：使用两个哈希函数和两个表，保证最坏情况 $$O(1)$$ 查找。插入时如果两个位置都被占用，"踢出"现有元素并重新安置
- **Robin Hood Hashing**：开放地址法的变体，通过"劫富济贫"策略减少探测长度方差，使查找性能更稳定

## Key Takeaways
- [x] 哈希表提供平均 $$O(1)$$ 的查找、插入、删除 -- 是面试中使用最频繁的数据结构
- [ ] Two Sum 是哈希表的经典应用 -- 用空间换时间，将 $$O(n^2)$$ 暴力搜索优化为 $$O(n)$$
- [ ] LRU Cache = HashMap + Doubly Linked List，是面试最常考的复合数据结构设计题
- [ ] 理解 Chaining vs Open Addressing 的权衡：缓存友好性 vs 实现复杂度
- [ ] 对于 MLE：哈希表是特征索引、embedding 查找表、去重管道和分布式缓存的核心组件
"""

# Translations for all other nodes
TRANSLATIONS = {}

TRANSLATIONS[44] = r"""# Array / String

## Overview
**Array（数组）** 和 **String（字符串）** 是编程面试中最高频考察的数据结构。几乎每道题都直接或间接涉及它们。掌握原地操作、**Two-Pointer（双指针）** 技术和 **Sliding Window（滑动窗口）** 是高级 MLE 面试的必备技能，面试官期望候选人给出最优的时间/空间复杂度方案。

## Core Concepts

### Array Fundamentals
数组提供 $$O(1)$$ 的随机访问和 $$O(n)$$ 的插入/删除（最坏情况）。在 Python 中，`list` 是一个动态数组，`append` 操作的均摊时间复杂度为 $$O(1)$$。

**关键性质**：
- 连续内存布局使得遍历具有极好的缓存友好性
- 排序可以将许多问题从 $$O(n^2)$$ 优化到 $$O(n \log n)$$
- **Prefix Sum（前缀和）** 在 $$O(n)$$ 预处理后可实现 $$O(1)$$ 的区间求和查询：

$$
\text{prefix}[i] = \sum_{j=0}^{i} a[j], \quad \text{sum}(l, r) = \text{prefix}[r] - \text{prefix}[l-1]
$$

### String Specifics
Python 字符串是不可变的 -- 在循环中拼接字符串是 $$O(n^2)$$ 的操作。应使用 `"".join(parts)` 来实现 $$O(n)$$ 的字符串构建。关键操作：
- **Substring Search（子串搜索）**：**KMP (Knuth-Morris-Pratt)** 算法实现 $$O(n + m)$$ 的匹配；Python 的 `in` 运算符使用 Boyer-Moore 的变体
- **Character Frequency（字符频率）**：`collections.Counter` 实现 $$O(n)$$ 的频率统计
- **Encoding（编码）**：ASCII（128 个字符）vs Unicode -- 影响哈希表的大小设计

### Two-Pointer Technique
**Two-Pointer（双指针）** 将 $$O(n^2)$$ 的暴力搜索降为 $$O(n)$$，适用于排序数组或特定模式：

$$
\text{Invariant: } l < r \text{ and search space shrinks each step}
$$

**变体**：相向指针（排序数组的配对求和）、同向指针（快慢指针检测环）、读写指针（原地删除元素）。

### Sliding Window
**Sliding Window（滑动窗口）** 在连续子数组 $$[l, r]$$ 上维护一个窗口。有两种形式：
- **固定大小窗口**：两个指针同步移动
- **可变大小窗口**：扩展右边界 $$r$$，当约束被违反时收缩左边界 $$l$$

## Implementation

```python
def max_subarray_sum_k(arr: list[int], k: int) -> int:
    # Maximum sum of subarray of size k -- fixed sliding window.
    window_sum = sum(arr[:k])
    best = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        best = max(best, window_sum)
    return best

def length_of_longest_substring(s: str) -> int:
    # Longest substring without repeating chars -- variable window.
    seen: dict[str, int] = {}
    left = ans = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        ans = max(ans, right - left + 1)
    return ans
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 相向双指针 | 排序数组、配对/三元组求和 | 若未排序则先排序；跳过重复元素以获得唯一结果 |
| 可变滑动窗口 | 满足约束的最长/最短子数组 | 用哈希表或计数器跟踪约束；从左侧收缩 |
| 前缀和 | 区间求和查询、子数组和等于 k | 用哈希表存储前缀和，$$O(n)$$ 求解子数组和 = k |
| 原地操作 | 不使用额外空间删除/移动元素 | 读写指针模式；从末尾覆盖以处理移位 |
| 排序 + 扫描 | 合并区间、会议室问题 | 按起始时间排序；贪心合并或计算重叠 |

### Common Interview Questions
- [ ] Two Sum / Three Sum（最优复杂度解法）
- [ ] 无重复字符的最长子串
- [ ] 合并区间
- [ ] 除自身以外数组的乘积（不使用除法）
- [ ] 接雨水（双指针或栈方法）
- [ ] 最小覆盖子串

## Comparisons

| Aspect | Brute Force | Two Pointer | Sliding Window | Prefix Sum |
|--------|------------|-------------|----------------|------------|
| 时间 | $$O(n^2)$$ | $$O(n)$$ | $$O(n)$$ | $$O(n)$$ 预处理，$$O(1)$$ 查询 |
| 空间 | $$O(1)$$ | $$O(1)$$ | $$O(k)$$ 窗口状态 | $$O(n)$$ |
| 需要排序 | 否 | 通常是 | 否 | 否 |
| 最适合 | 小规模 $$n$$ | 配对问题 | 连续子数组 | 区间查询 |

## Common Pitfalls
- **滑动窗口的边界错误**：忘记在主循环之前初始化窗口，或者窗口大小计算错误
- **双指针未处理重复元素**：Three Sum 需要跳过重复值以避免结果中出现重复三元组
- **字符串不可变性**：在循环中使用 `+=` 拼接字符串是 $$O(n^2)$$ 的；应始终收集到列表中再 join
- **前缀和索引偏移**：前缀数组通常长度为 $$n+1$$，其中 `prefix[0] = 0`；索引偏移错误会导致区间和计算错误
- **迭代时修改数组**：使用单独的写指针或构建新数组

## Key Takeaways
- [x] 排序数组上的双指针将 $$O(n^2)$$ 降为 $$O(n)$$ -- 始终优先考虑排序
- [ ] 滑动窗口是连续子数组/子串问题的标准方法
- [ ] 前缀和将区间查询转化为 $$O(1)$$ 查找 -- 结合哈希表解决子数组和 = k
- [ ] 原地字符串/数组操作需要仔细的索引管理 -- 练习读写指针模式
- [ ] 对于 MLE：数组操作直接对应 NumPy/PyTorch 中的张量操作
"""

TRANSLATIONS[46] = r"""# Stack / Queue

## Overview
**Stack（栈，LIFO 后进先出）** 和 **Queue（队列，FIFO 先进先出）** 是管理顺序和处理序列的基础数据结构。栈驱动表达式求值、括号匹配和 **Monotonic Stack（单调栈）** 问题。队列支持 **BFS (Breadth-First Search，广度优先搜索)**、层序遍历和速率限制。**Deque（双端队列）** 结合了两者的特点，出现在滑动窗口最大值问题中。这些都是高频面试主题，具有明确定义的模式。

## Core Concepts

### Stack (LIFO)
后进先出。操作：`push`、`pop`、`peek` -- 均为 $$O(1)$$。Python 中使用 `list`（从末尾 append/pop）。

**Monotonic Stack（单调栈）**：维护元素的排序顺序。核心思想 -- 当新元素破坏单调性时，弹出并处理元素：

$$
\text{For each element, it is pushed once and popped at most once} \implies O(n) \text{ total}
$$

每个元素最多被压入和弹出各一次，因此总时间复杂度为 $$O(n)$$。

### Queue (FIFO)
先进先出。操作：`enqueue`、`dequeue` -- 使用链表或 deque 时为 $$O(1)$$。Python 中使用 `collections.deque`（绝对不要用 `list.pop(0)`，那是 $$O(n)$$ 的）。

### Deque (Double-Ended Queue)
**Deque（双端队列）** 支持两端 $$O(1)$$ 的添加/弹出操作。是滑动窗口最大值的关键数据结构。

### Monotonic Stack Pattern
单调栈维护一个递减（或递增）序列。用于"下一个更大元素"、"柱状图中最大矩形"和温度问题。

## Implementation

```python
from collections import deque

def next_greater_element(nums: list[int]) -> list[int]:
    # For each element, find next greater element. O(n).
    result = [-1] * len(nums)
    stack: list[int] = []  # indices, values are decreasing
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            result[stack.pop()] = num
        stack.append(i)
    return result

def sliding_window_max(nums: list[int], k: int) -> list[int]:
    # Maximum in each window of size k. O(n) using deque.
    dq: deque[int] = deque()  # indices, values are decreasing
    result = []
    for i, num in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 括号匹配 | 有效括号、表达式解析 | 遇到左括号压栈；遇到右括号弹出并匹配 |
| 单调递减栈 | 下一个更大元素、每日温度 | 当前元素 > 栈顶时弹出；栈中剩余元素没有更大元素 |
| 单调递增栈 | 柱状图中最大矩形 | 当前元素 < 栈顶时弹出；宽度 = 两个边界之间的距离 |
| Min Stack | $$O(1)$$ 获取最小值 | 存储（值，当前最小值）对，或使用辅助最小栈 |
| 两栈实现队列 | 实现队列 | 均摊 $$O(1)$$：压入 in-stack，懒惰转移到 out-stack |
| 滑动窗口最大值 | 固定窗口中的最大值 | 使用索引的 deque；维护递减值 |

### Common Interview Questions
- [ ] Valid Parentheses（栈）
- [ ] Daily Temperatures（单调栈）
- [ ] Largest Rectangle in Histogram（单调栈）
- [ ] Min Stack（$$O(1)$$ getMin）
- [ ] Sliding Window Maximum（双端队列）
- [ ] Implement Queue using Stacks
- [ ] Evaluate Reverse Polish Notation

## Comparisons

| Aspect | Stack (list) | Queue (deque) | Deque | Priority Queue (heapq) |
|--------|-------------|--------------|-------|----------------------|
| 顺序 | LIFO | FIFO | 两端 | 按优先级 |
| Push | $$O(1)$$ | $$O(1)$$ | $$O(1)$$ 两端 | $$O(\log n)$$ |
| Pop | $$O(1)$$ | $$O(1)$$ | $$O(1)$$ 两端 | $$O(\log n)$$ |
| 查看最小/最大 | $$O(n)$$ 或带辅助栈 $$O(1)$$ | $$O(n)$$ | $$O(1)$$ 首/尾 | $$O(1)$$ 最小 |
| 适用场景 | 解析、回溯 | BFS、调度 | 滑动窗口 | Dijkstra、top-k |

## Common Pitfalls
- **用 list 当队列**：`list.pop(0)` 是 $$O(n)$$ 的，因为需要移动所有元素；应始终使用 `collections.deque`
- **单调栈方向搞反**：求"下一个更大元素"用递减栈；求"下一个更小元素"用递增栈 -- 混淆方向是常见错误
- **忘记检查空栈**：调用 `stack[-1]` 或 `stack.pop()` 前必须先检查 `stack` 是否为空
- **最大矩形哨兵技巧**：在数组末尾追加 0 可以简化代码，强制将所有剩余元素弹出栈

## Advanced Patterns
- **计算器问题**：使用两个栈（操作数 + 运算符）或先转换为 **RPN (Reverse Polish Notation，逆波兰表达式)**。通过与栈顶比较运算符优先级来决定是否压栈
- **基于栈的树遍历**：迭代版的中序/前序/后序遍历都使用显式栈。**Morris Traversal** 通过临时修改树的指针实现 $$O(1)$$ 空间遍历
- **循环队列**：使用固定大小的数组和 `front`/`rear` 指针，通过模运算实现：`rear = (rear + 1) % capacity`

## Key Takeaways
- [ ] 单调栈在 $$O(n)$$ 内求解"下一个更大/更小元素" -- 每个元素最多压入和弹出各一次
- [ ] 在 Python 中队列始终使用 `deque` -- `list.pop(0)` 是 $$O(n)$$ 的
- [ ] 滑动窗口最大值配合 deque 是经典模式：维护索引的递减 deque
- [ ] Min Stack：将每个元素与当前最小值配对，实现 $$O(1)$$ getMin
- [ ] 对于 MLE：队列出现在基于图的模型的 BFS、数据加载管道和请求缓冲中
"""

TRANSLATIONS[47] = r"""# Linked List

## Overview
**Linked List（链表）** 考察指针操作技巧和原地算法设计能力。虽然在 ML 系统中很少直接使用（数组因缓存性能更优而占主导），但链表问题是面试中的常客，考察候选人对边界情况、指针重新赋值和循环检测的细致处理。**Fast/Slow Pointer（快慢指针）** 技术尤为重要。

## Core Concepts

### Singly vs Doubly Linked List
- **Singly Linked List（单链表）**：每个节点有 `val` 和 `next`。遍历 $$O(n)$$，头部插入 $$O(1)$$
- **Doubly Linked List（双链表）**：每个节点有 `val`、`next` 和 `prev`。给定节点引用即可 $$O(1)$$ 删除

### Sentinel (Dummy) Node
**Sentinel Node（哨兵节点）** 简化边界情况的处理（空链表、头节点删除）：
```
dummy -> 1 -> 2 -> 3 -> None
```
返回 `dummy.next` 作为实际头节点。这消除了对头节点操作的特殊处理代码。

### Fast/Slow Pointer (Floyd's Algorithm)
**Floyd's Algorithm（弗洛伊德算法）** 使用两个不同速度移动的指针：
- **环检测**：慢指针每次移动 1 步，快指针每次移动 2 步。当且仅当存在环时它们会相遇
- **找中间节点**：当快指针到达末尾时，慢指针正好在中间
- **找环入口**：相遇后，将一个指针移到头部；两指针各走 1 步，再次相遇处即为环入口

$$
\text{Meeting point: } d_{\text{head to cycle start}} = d_{\text{meeting point to cycle start}}
$$

头部到环入口的距离等于相遇点到环入口的距离。

## Implementation

```python
class ListNode:
    def __init__(self, val: int = 0, nxt: "ListNode | None" = None):
        self.val = val
        self.next = nxt

def reverse_list(head: ListNode | None) -> ListNode | None:
    # Reverse a linked list iteratively. O(n) time, O(1) space.
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

def has_cycle(head: ListNode | None) -> bool:
    # Floyd's cycle detection. O(n) time, O(1) space.
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

def merge_two_sorted(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    # Merge two sorted lists. O(n+m) time, O(1) space.
    dummy = curr = ListNode()
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next, l1 = l1, l1.next
        else:
            curr.next, l2 = l2, l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 哑节点 | 任何链表修改操作 | 消除头节点删除的边界情况 |
| 快慢指针 | 环检测、找中间节点 | $$O(1)$$ 空间，替代哈希集合方案 |
| 分组反转 | 每 k 个节点反转 | 跟踪分组边界；每次反转后重新连接 |
| 合并有序链表 | 合并 k 个有序链表 | 使用堆进行 k 路合并，$$O(n \log k)$$ |
| 带间隔的双指针 | 删除倒数第 n 个节点 | 先让第一个指针走 n 步，然后两指针同时移动 |

### Common Interview Questions
- [ ] 反转链表（迭代和递归）
- [ ] 检测环并找到环入口（Floyd 算法）
- [ ] 合并两个有序链表
- [ ] 删除倒数第 n 个节点（带间隔的双指针）
- [ ] LRU Cache（双链表 + 哈希表）
- [ ] K 个一组反转链表
- [ ] 复制带随机指针的链表

## Comparisons

| Aspect | Singly Linked | Doubly Linked | Array |
|--------|--------------|--------------|-------|
| 按索引访问 | $$O(n)$$ | $$O(n)$$ | $$O(1)$$ |
| 头部插入 | $$O(1)$$ | $$O(1)$$ | $$O(n)$$ |
| 给定节点删除 | $$O(n)$$（需要前驱） | $$O(1)$$ | $$O(n)$$ |
| 内存开销 | 每节点 1 个指针 | 每节点 2 个指针 | 无 |
| 缓存性能 | 差 | 差 | 优秀 |

## Common Pitfalls
- **丢失 next 指针**：反转时，必须在重新赋值 `curr.next` 之前保存 `next`
- **不使用哑节点**：没有哑节点时，头节点删除需要特殊处理；应始终使用 `dummy = ListNode(0); dummy.next = head`
- **环问题中的死循环**：如果忘记移动指针或错误中断，代码会无限运行
- **"删除倒数第 n 个"的偏移错误**：第一个指针需要先走 $$n+1$$ 步（或使用哑节点）以停在目标节点之前

## Advanced Patterns
- **链表排序**：归并排序是最优选择 -- 用快慢指针找中点，递归排序两半，合并。$$O(n \log n)$$ 时间，$$O(\log n)$$ 栈空间
- **多层链表扁平化**：使用 **DFS (Depth-First Search，深度优先搜索)**（栈）或递归；将 child 指针视为分支
- **Skip List（跳表）**：平衡 BST 的概率替代方案，期望搜索时间 $$O(\log n)$$。用于 Redis 有序集合和 LevelDB。多层链表加随机晋升
- **XOR 链表**：在单个指针字段中存储 `prev XOR next`，将内存减半。实际中很少使用，但考察对指针运算的理解

## Key Takeaways
- [ ] 始终使用哑/哨兵节点简化链表操作中的边界情况
- [ ] Floyd 快慢指针：环检测、找中点和找环入口均为 $$O(1)$$ 空间
- [ ] 编码前画图 -- 指针重新赋值的顺序至关重要
- [ ] 常见 bug：在重新赋值指针之前丢失对 `next` 的引用
- [ ] 对于 MLE：LRU Cache（双链表 + 哈希表）是链表最实用的应用
"""

TRANSLATIONS[48] = r"""# Tree / BST

## Overview
**Tree（树）** 是算法面试和 ML 系统中的基础数据结构（决策树、层次聚类、NLP 语法树）。**BST (Binary Search Tree，二叉搜索树)** 在平衡时提供 $$O(\log n)$$ 的操作。树的遍历、递归思维和 BST 性质是面试中的重点考察内容。高级候选人应能熟练使用递归和迭代两种方法。

## Core Concepts

### Tree Traversals
对于一棵二叉树，根节点为 $$r$$，左子树为 $$L$$，右子树为 $$R$$：

| Traversal | Order | Use Case |
|-----------|-------|----------|
| Inorder（中序） | $$L \to r \to R$$ | BST 得到排序序列 |
| Preorder（前序） | $$r \to L \to R$$ | 序列化树、复制树 |
| Postorder（后序） | $$L \to R \to r$$ | 删除树、表达式求值 |
| Level-order（层序） | 按深度 BFS | 逐层处理 |

### Binary Search Tree (BST) Property
对于每个节点 $$n$$：左子树中的所有值 $$< n.val <$$ 右子树中的所有值。

**平衡 BST 的操作**：搜索、插入、删除均为 $$O(\log n)$$。最坏情况（退化为链表）：$$O(n)$$。

### Tree Height and Balance
- **高度**：从根到叶子的最长路径。平衡树：$$h = O(\log n)$$
- **AVL 树**：每个节点满足 $$|h(L) - h(R)| \le 1$$
- **Red-Black Tree（红黑树）**：保证 $$h \le 2 \log_2(n+1)$$

### Lowest Common Ancestor (LCA)
对于节点 $$p$$ 和 $$q$$，**LCA（最近公共祖先）** 是同时作为两者祖先的最深节点：
- **BST 中**：比较值；若两者都小则向左；都大则向右；否则当前节点即为 LCA
- **普通二叉树中**：递归 -- 若当前节点是 $$p$$ 或 $$q$$ 则返回；检查两个子树

## Implementation

```python
class TreeNode:
    def __init__(self, val: int = 0, left: "TreeNode | None" = None,
                 right: "TreeNode | None" = None):
        self.val = val
        self.left = left
        self.right = right

def inorder_iterative(root: TreeNode | None) -> list[int]:
    # Inorder traversal without recursion. O(n) time, O(h) space.
    result, stack = [], []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right
    return result

def max_depth(root: TreeNode | None) -> int:
    # Maximum depth of binary tree. O(n).
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def is_valid_bst(root: TreeNode | None,
                 lo: float = float("-inf"),
                 hi: float = float("inf")) -> bool:
    # Validate BST using range propagation. O(n).
    if not root:
        return True
    if root.val <= lo or root.val >= hi:
        return False
    return (is_valid_bst(root.left, lo, root.val)
            and is_valid_bst(root.right, root.val, hi))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 递归 DFS | 大多数树问题 | 基本情况 = None/叶子；合并左右子树结果 |
| 迭代 + 栈 | 不使用递归的中序/前序 | 显式模拟调用栈 |
| 层序 BFS | 逐层操作 | 基于队列；每次外层循环处理一层 |
| BST 性质 | BST 中的搜索、验证、LCA | 中序遍历得到排序序列；通过值比较剪枝搜索空间 |
| 路径问题 | 根到叶子路径和、最大路径和 | 跟踪累计和/路径；在叶子节点回溯 |

### Common Interview Questions
- [ ] 二叉树的最大深度 / 直径
- [ ] 验证二叉搜索树
- [ ] 最近公共祖先（BST 和普通二叉树）
- [ ] 二叉树的层序遍历
- [ ] 二叉树的序列化与反序列化
- [ ] 从中序和前序遍历构造二叉树
- [ ] 二叉树的最大路径和

## Common Pitfalls
- **BST 验证错误**：仅与父节点比较是错误的。约束是左子树中的所有值都必须小于当前节点，而不仅仅是直接子节点。应递归传递最小/最大边界
- **混淆树的直径和深度**：直径是任意两个节点之间的最长路径（可能不经过根）。在每个节点计算 `max(left_depth + right_depth)`
- **遗忘基本情况**：`if not root: return ...` 必须是每个递归树函数的第一行
- **遍历时修改树**：如果问题要求修改树，考虑是否需要后序遍历以在处理父节点之前先处理子节点

## Advanced Patterns
- **Morris Traversal**：$$O(1)$$ 空间的中序遍历，通过临时连接树的线程实现。中序前驱的右指针指向当前节点。访问后恢复树结构
- **序列化**：前序遍历加空标记可唯一标识一棵树。BFS 层序也可以。对于 BST，仅前序遍历就足够（无需空标记），因为 BST 性质约束了结构
- **Segment Tree（线段树）**：用于区间查询（和、最小、最大）的平衡二叉树，$$O(\log n)$$ 的更新和查询。用于竞赛编程和数据库索引
- **Binary Indexed Tree（树状数组 / Fenwick 树）**：支持 $$O(\log n)$$ 的前缀和查询和单点更新。比线段树更节省空间，适合累计频率表

## Key Takeaways
- [ ] 掌握递归和迭代两种遍历方式 -- 面试官可能要求任一种
- [ ] BST 验证：向下传递最小/最大边界，而非仅与父节点比较
- [ ] 树问题天然适合递归：确定基本情况、递推关系和结果合并方式
- [ ] 层序遍历模式：`for _ in range(len(queue))` 每次处理一层
- [ ] 对于 MLE：决策树的分裂直接对应类 BST 结构；基于树的模型（XGBoost）是面试常考内容
"""

TRANSLATIONS[49] = r"""# Heap / Priority Queue

## Overview
**Heap（堆）** 提供 $$O(\log n)$$ 的插入和 $$O(1)$$ 的最小（或最大）元素访问，是 top-k 问题、流处理和图算法（Dijkstra、Prim）的核心。Python 的 `heapq` 是一个最小堆。理解堆操作、heapify 技巧以及何时使用堆而非排序对面试表现至关重要。

## Core Concepts

### Binary Heap Properties
**Binary Heap（二叉堆）** 是一棵以数组形式存储的完全二叉树，满足：
- **Min-Heap（最小堆）**：父节点 $$\le$$ 子节点。根 = 最小元素
- **Max-Heap（最大堆）**：父节点 $$\ge$$ 子节点。根 = 最大元素

对于 0 索引的节点 $$i$$：
$$
\text{parent}(i) = \lfloor (i-1)/2 \rfloor, \quad \text{left}(i) = 2i+1, \quad \text{right}(i) = 2i+2
$$

### Time Complexities

| Operation | Time |
|-----------|------|
| 插入 (push) | $$O(\log n)$$ |
| 取出最小/最大 (pop) | $$O(\log n)$$ |
| 查看最小/最大 (peek) | $$O(1)$$ |
| 建堆 (heapify) | $$O(n)$$ -- 不是 $$O(n \log n)$$ |
| 找第 k 大 | $$O(n + k \log n)$$（先建堆再弹出 k 次） |

### Heapify Analysis
从无序数组建堆的时间是 $$O(n)$$，而不是 $$O(n \log n)$$：

$$
\sum_{h=0}^{\lfloor \log n \rfloor} \frac{n}{2^{h+1}} \cdot O(h) = O(n)
$$

直觉上：大多数节点在底层，它们只需要很少的下沉操作。

### Python heapq Patterns
`heapq` 仅支持最小堆。实现最大堆时需要取反值。自定义排序使用元组：`(priority, tiebreaker, item)`。

## Implementation

```python
import heapq

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    # Find k most frequent elements. O(n + m log k) where m = unique.
    from collections import Counter
    freq = Counter(nums)
    # Min-heap of size k: smallest frequency gets evicted
    return heapq.nlargest(k, freq.keys(), key=freq.get)

def merge_k_sorted_lists(lists: list[list[int]]) -> list[int]:
    # Merge k sorted lists. O(n log k) where n = total elements.
    result: list[int] = []
    heap: list[tuple[int, int, int]] = []  # (value, list_idx, elem_idx)
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    while heap:
        val, li, ei = heapq.heappop(heap)
        result.append(val)
        if ei + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][ei + 1], li, ei + 1))
    return result

def find_median_stream():
    # Running median using two heaps.
    lo: list[int] = []  # max-heap (negated) for lower half
    hi: list[int] = []  # min-heap for upper half
    def add(num: int) -> float:
        heapq.heappush(lo, -num)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        if len(lo) > len(hi):
            return -lo[0]
        return (-lo[0] + hi[0]) / 2
    return add
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Top-k 元素 | 找 k 个最大/最小/最高频 | 大小为 k 的最小堆；淘汰最小的 |
| K 路合并 | 合并 k 个有序流 | 大小为 k 的堆；弹出后从对应流推入下一个 |
| 双堆（中位数） | 运行中位数、平衡分区 | 最大堆（下半部分）+ 最小堆（上半部分），每次插入后重新平衡 |
| 懒删除 | 带更新的 Dijkstra | 推入重复项；弹出时跳过过期条目 |
| 堆 + 哈希表 | 设计 Twitter、事件调度 | 堆管理顺序，哈希表管理元数据 |

### Common Interview Questions
- [ ] Top K Frequent Elements（前 K 个高频元素）
- [ ] Merge K Sorted Lists（合并 K 个有序链表）
- [ ] Find Median from Data Stream（数据流中的中位数，双堆）
- [ ] Kth Largest Element in a Stream（数据流中的第 K 大元素）
- [ ] Task Scheduler（任务调度器，贪心 + 堆）
- [ ] Reorganize String（重新排列字符串，最大堆贪心）

## Comparisons

| Aspect | Heap | Sorted Array | BST (balanced) |
|--------|------|-------------|----------------|
| 插入 | $$O(\log n)$$ | $$O(n)$$ | $$O(\log n)$$ |
| 找最小 | $$O(1)$$ | $$O(1)$$ | $$O(\log n)$$ |
| 删除最小 | $$O(\log n)$$ | $$O(1)$$ 均摊 | $$O(\log n)$$ |
| 找第 k 个 | $$O(k \log n)$$ | $$O(1)$$ | $$O(\log n)$$ |
| 最适合 | 流式 top-k | 静态有序数据 | 动态有序集合 |

## Common Pitfalls
- **忘记元组排序的打破平局规则**：向 heapq 推入 `(priority, item)` 时，item 必须可比较。使用 `(priority, tiebreaker_counter, item)` 来避免不可比较对象的比较错误
- **混淆 heapify 和逐个 push**：`heapq.heapify(list)` 是 $$O(n)$$；逐个推入 $$n$$ 个元素是 $$O(n \log n)$$。当已有所有元素时始终使用 heapify
- **双堆再平衡**：每次插入后确保 $$|\text{len(lo)} - \text{len(hi)}| \le 1$$。操作顺序（先推入一个堆再平衡）很重要
- **使用堆获取排序输出**：反复弹出得到排序顺序但会销毁堆。若需不修改地排序遍历，先复制

## Advanced Patterns
- **Indexed Priority Queue（索引优先队列）**：通过维护位置映射支持 $$O(\log n)$$ 的 decrease-key。对于带有适当 decrease-key 的 Dijkstra 很重要（虽然懒删除在面试中更简单）
- **用堆做区间调度**：按开始时间处理事件；堆跟踪活跃区间的结束时间。任意时刻堆的大小 = 并发区间数
- **外部排序**：当数据超出内存时，分成排序块然后用堆进行 k 路合并。这是 `sort` 命令处理大文件和分布式系统合并排序分区的工作原理

## Key Takeaways
- [ ] Heapify 是 $$O(n)$$ 而非 $$O(n \log n)$$ -- 当已有所有元素时使用 `heapq.heapify`
- [ ] Python 中实现最大堆：取反值 `heappush(h, -val)`，结果 = `-heappop(h)`
- [ ] 双堆求中位数：最大堆（下半部分）+ 最小堆（上半部分），每次插入后重新平衡
- [ ] 堆的 K 路合并是 $$O(n \log k)$$ -- 对于大 $$k$$ 远优于 $$O(nk)$$ 的朴素合并
- [ ] 对于 MLE：堆驱动序列模型中的 Beam Search、基于优先级的数据采样以及图神经网络中的 Dijkstra
"""

TRANSLATIONS[50] = r"""# Trie

## Overview
**Trie（字典树 / 前缀树）** 是一种树形数据结构，用于高效的字符串前缀操作。它提供 $$O(L)$$ 的搜索/插入（$$L$$ 为单词长度），与存储的单词数量无关。Trie 在自动补全系统、拼写检查器和 IP 路由中不可或缺 -- 这些都与 ML 驱动的搜索和 NLP 应用相关。Trie 也出现在涉及前缀匹配和单词搜索的面试题中。

## Core Concepts

### Trie Structure
每个节点表示一个字符。从根到某个节点的路径表示一个前缀。一个布尔标志标记单词结尾。

**空间复杂度**：$$O(\Sigma \cdot N \cdot L)$$，其中 $$\Sigma$$ = 字母表大小，$$N$$ = 单词数量，$$L$$ = 平均长度。实际中前缀共享会显著减少空间使用。

### Operations Complexity

| Operation | Time | Space |
|-----------|------|-------|
| 插入单词 | $$O(L)$$ | $$O(L)$$ 最坏情况新建节点 |
| 搜索单词 | $$O(L)$$ | $$O(1)$$ |
| 前缀搜索 | $$O(P)$$（前缀长度 $$P$$） | $$O(1)$$ |
| 自动补全（所有匹配前缀的单词） | $$O(P + K)$$（$$K$$ = 结果数） | 取决于结果 |

### Trie vs Hash Set for Strings
- **Trie 优势**：前缀查询、字典序遍历、无哈希冲突
- **Hash Set 优势**：实现更简单、精确查找更快（常数因子更小）、对无共享前缀的短字符串内存更少

### Compressed Trie (Radix Tree)
**Compressed Trie（压缩字典树 / 基数树）** 合并只有单个子节点的节点，减少空间。用于 Linux 内核路由表和某些数据库。

## Implementation

```python
class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False

class Trie:
    def __init__(self) -> None:
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

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, prefix: str) -> "TrieNode | None":
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 基本 Trie | 前缀匹配、自动补全 | 使用 dict 类型的 children 以支持灵活的字母表 |
| Trie + DFS | 网格中的单词搜索、单词拆分 | 结合 Trie 遍历和网格/字符串 DFS |
| Trie + 回溯 | Word Search II（在网格中找所有单词） | 从单词列表构建 Trie；从每个格子 DFS |
| 位运算 Trie | 最大异或对 | 存储二进制表示；贪心选择相反的位 |
| 带计数的 Trie | 前缀频率、IP 路由 | 在每个节点存储计数用于前缀统计 |

### Common Interview Questions
- [ ] Implement Trie（实现 Trie：insert、search、startsWith）
- [ ] Word Search II（Trie + 网格 DFS）
- [ ] Design Search Autocomplete System（设计搜索自动补全系统）
- [ ] Replace Words（使用 Trie 的前缀替换）
- [ ] Maximum XOR of Two Numbers（位运算 Trie）
- [ ] Word Break（可用 Trie + DP 求解）

## Comparisons

| Aspect | Trie | HashMap | Sorted Array + Binary Search |
|--------|------|---------|------------------------------|
| 精确查找 | $$O(L)$$ | $$O(L)$$ 平均 | $$O(L \log n)$$ |
| 前缀查询 | $$O(P)$$ | $$O(n \cdot L)$$ 扫描 | $$O(L \log n)$$ |
| 空间 | $$O(\Sigma \cdot N \cdot L)$$ | $$O(N \cdot L)$$ | $$O(N \cdot L)$$ |
| 有序遍历 | 是（字典序） | 否 | 是 |
| 最适合 | 前缀密集型工作负载 | 精确查找 | 静态字典 |

## Common Pitfalls
- **基于数组的 children 内存爆炸**：在每个节点使用 `[None] * 26` 会浪费稀疏 Trie 的内存。基于 dict 的 children 更实用
- **遗忘 `is_end` 标志**：没有它，在包含 "apple" 的 Trie 中搜索 "app" 会错误地返回 True
- **Trie 删除**：很少被问到但很棘手 -- 删除前必须检查节点是否有其他子节点。使用引用计数或懒删除

## Key Takeaways
- [ ] Trie 提供 $$O(L)$$ 的前缀查询 -- 哈希表无法匹配"以 X 开头的所有单词"这类查询
- [ ] 使用基于 dict 的 children（而非大小为 26 的数组）以获得灵活性和稀疏字母表的空间效率
- [ ] Word Search II 是经典的 Trie + 回溯问题 -- 从单词列表构建 Trie，在网格上 DFS
- [ ] 位运算 Trie 求最大异或是高级但重要的模式
- [ ] 对于 MLE：Trie 驱动分词器词汇查找（BPE）、自动补全排序和基于前缀的特征匹配
"""

TRANSLATIONS[51] = r"""# Union-Find

## Overview
**Union-Find（并查集 / DSU，Disjoint Set Union）** 高效跟踪连通分量，通过 **Path Compression（路径压缩）** 和 **Union by Rank（按秩合并）** 支持近 $$O(1)$$ 的合并和查找操作。它是动态连通性问题、**Kruskal's MST（最小生成树）** 算法和无向图环检测的最优数据结构。对于 MLE，它出现在聚类、图像分割和实体消解问题中。

## Core Concepts

### Core Operations
- **Find(x)**：返回 $$x$$ 所在分量的根代表
- **Union(x, y)**：合并包含 $$x$$ 和 $$y$$ 的分量
- **Connected(x, y)**：检查 $$x$$ 和 $$y$$ 是否在同一分量中

### Optimizations
不做优化时，树可能退化为链表（$$O(n)$$ 的 find）。两个关键优化：

**Path Compression（路径压缩）**：在 Find 过程中，将路径上的每个节点直接指向根：
$$
\text{Find}(x): \text{parent}[x] = \text{Find}(\text{parent}[x])
$$

**Union by Rank（按秩合并）**：将较小的树挂在较大树的根下。

同时使用两种优化时，每次操作的均摊代价为 $$O(\alpha(n))$$，其中 $$\alpha$$ 是 **Inverse Ackermann Function（反阿克曼函数）** -- 实际上是常数（对任何实际 $$n$$，$$\alpha(n) \le 4$$）。

### When to Use Union-Find vs BFS/DFS
- **Union-Find**：动态连通性（边随时间添加）、计数分量、环检测
- **BFS/DFS**：路径查找、最短路径、遍历顺序很重要时

## Implementation

```python
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already connected
        # union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 连通分量计数 | 岛屿数量、朋友圈 | 初始化 $$n$$ 个分量；每次成功合并递减计数 |
| Kruskal MST | 最小生成树 | 按权重排序边；合并端点；已连通则跳过 |
| 环检测 | 无向图的环 | 若合并前 find(u) == find(v)，添加边 (u,v) 会形成环 |
| 动态连通性 | 边随时间添加 | Union-Find 处理在线边添加；BFS/DFS 需要重建 |
| 带权 Union-Find | 方程式、相对关系 | 在边上存储权重；路径压缩时调整 |

### Common Interview Questions
- [ ] Number of Connected Components（连通分量数，Union-Find 或 DFS）
- [ ] Redundant Connection（找到形成环的边）
- [ ] Accounts Merge（通过共同邮箱合并账户）
- [ ] Number of Islands（合并相邻陆地格子）
- [ ] Evaluate Division（带权 Union-Find 解方程链）
- [ ] Smallest String With Swaps（合并交换位置，分量内排序）

## Comparisons

| Aspect | Union-Find | BFS/DFS | Adjacency Matrix |
|--------|-----------|---------|-----------------|
| 动态添加边 | $$O(\alpha(n))$$ 每次 | $$O(V+E)$$ 重建 | $$O(1)$$ 添加，$$O(V)$$ 查询 |
| 连通查询 | $$O(\alpha(n))$$ | $$O(V+E)$$ | $$O(V)$$ |
| 路径查找 | 不支持 | 支持 | 支持 |
| 空间 | $$O(V)$$ | $$O(V+E)$$ | $$O(V^2)$$ |
| 最适合 | 仅连通性 | 遍历、路径 | 稠密图 |

## Common Pitfalls
- **忘记路径压缩**：没有路径压缩，find 在倾斜树上退化为 $$O(n)$$。递归版中始终加上 `parent[x] = find(parent[x])`，或使用迭代路径减半
- **不使用按秩/大小合并**：没有基于秩的合并，树可能变成链表。始终将较小的树挂在较大的树下
- **节点索引偏移错误**：确保节点索引与 parent 数组大小匹配。对于 1 索引的问题，分配大小为 $$n+1$$ 的 `parent`
- **不返回合并是否成功**：`union` 函数应返回 `True`（合并了不同分量）或 `False`（已连通）。这在环检测和计数中是必需的

## Key Takeaways
- [ ] 始终同时实现路径压缩和按秩合并 -- 两者一起给出 $$O(\alpha(n))$$ 均摊
- [ ] 跟踪分量计数：初始化为 $$n$$，每次成功合并递减
- [ ] Union-Find 无法查找节点之间的路径 -- 它只回答连通性查询
- [ ] 无向图环检测中，Union-Find 比带 visited 跟踪的 DFS 更简洁
- [ ] 对于 MLE：Union-Find 驱动实体消解（合并重复记录）、图的连通分量分析和层次聚类的链接
"""

TRANSLATIONS[52] = r"""# Binary Search

## Overview
**Binary Search（二分查找）** 在排序/单调数据上实现 $$O(\log n)$$ 的搜索。除了简单的数组查找，真正的面试威力来自 **Binary Search on Answer（二分答案）** -- 当可行性函数单调时，在解空间上搜索。这种技术将优化问题转化为判定问题，是高级 MLE 面试中因其优雅和广泛适用性而备受青睐的方法。

## Core Concepts

### Standard Binary Search
在排序数组中搜索目标值。三个关键决策：
1. **闭区间**：`lo, hi = 0, len(arr) - 1`，使用 `while lo <= hi`
2. **左闭右开**：`lo, hi = 0, len(arr)`，使用 `while lo < hi`
3. **中点**：`mid = lo + (hi - lo) // 2`（避免溢出）

### Boundary Finding (bisect)
查找值的插入位置：
- **bisect_left**：第一个满足 `arr[pos] >= target` 的位置（最左边界）
- **bisect_right**：第一个满足 `arr[pos] > target` 的位置（最右边界 + 1）

$$
\text{bisect\_left}(a, x) = \min\{i : a[i] \ge x\}
$$

### Binary Search on Answer
当优化一个值 $$v$$ 并且可以在多项式时间内检查"$$v$$ 是否可行？"，且可行性是单调的（所有 $$\ge v^*$$ 的值都可行，或所有 $$\le v^*$$ 的），则在答案空间上二分搜索：

$$
\text{If } f(v) \text{ is monotonic, search } [lo, hi] \text{ for the boundary where } f \text{ flips}
$$

如果 $$f(v)$$ 是单调的，在 $$[lo, hi]$$ 中搜索 $$f$$ 翻转的边界。

**典型例题**：D 天内运送包裹的最小运力、分割数组的最大值、Koko 吃香蕉。

## Implementation

```python
from bisect import bisect_left

def binary_search(arr: list[int], target: int) -> int:
    # Standard binary search. Returns index or -1.
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def min_capacity_to_ship(weights: list[int], days: int) -> int:
    # Binary search on answer: min ship capacity for D days.
    def can_ship(cap: int) -> bool:
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = 0
            cur += w
        return d <= days

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_ship(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 标准搜索 | 排序数组查找 | 在 Python 中使用 `bisect_left`/`bisect_right` 使代码更简洁 |
| 第一个/最后一个出现 | 排序数组中有重复 | bisect_left 找第一个，bisect_right - 1 找最后一个 |
| 二分答案 | 最小化最大值 / 最大化最小值 | 定义 `is_feasible(mid)`；在答案范围上搜索 |
| 旋转排序数组搜索 | 旋转排序数组 | 一半总是有序的；判断目标在哪一半 |
| 二维矩阵搜索 | 行有序或完全有序的矩阵 | 视为一维数组：`row = mid // cols, col = mid % cols` |

### Common Interview Questions
- [ ] Binary Search（标准 + 边界情况）
- [ ] Search in Rotated Sorted Array（旋转排序数组搜索）
- [ ] Find First and Last Position of Element（找元素的第一个和最后一个位置）
- [ ] Koko Eating Bananas（二分答案）
- [ ] Split Array Largest Sum（分割数组最大值，二分答案）
- [ ] Median of Two Sorted Arrays（$$O(\log \min(m,n))$$）

## Comparisons

| Aspect | Linear Search | Binary Search | Interpolation Search |
|--------|--------------|---------------|---------------------|
| 时间 | $$O(n)$$ | $$O(\log n)$$ | $$O(\log \log n)$$ 平均（均匀分布） |
| 前提条件 | 无 | 排序/单调 | 均匀分布 |
| 实现难度 | 简单 | 中等 | 复杂 |
| 边界错误风险 | 无 | 高 | 高 |

## Common Pitfalls
- **边界错误**：最常见的 bug。搜索边界（最左有效值）时使用 `lo < hi` 配合 `hi = mid`。精确查找时使用 `lo <= hi` 配合 `lo = mid + 1, hi = mid - 1`
- **死循环**：当 `lo + 1 == hi` 时如果 `lo = mid`，循环永远不会终止。使用 `mid = lo + (hi - lo + 1) // 2`（向上取整）当更新中有 `lo = mid` 时
- **单调性方向错误**：二分答案要求可行性函数是单调的。验证：如果 $$f(x)$$ 为 True，$$f(x+1)$$ 是否也为 True？如果不是，二分查找不适用
- **未处理空输入**：开始二分查找前检查 `len(arr) == 0`

## Key Takeaways
- [ ] 二分答案是最强大的变体："最小化最大值"或"最大化最小值"暗示此模式
- [ ] 使用 `lo < hi` 配合 `hi = mid`（而非 `mid - 1`）查找边界以避免边界错误
- [ ] Python 的 `bisect_left`/`bisect_right` 可以干净地处理边界查找 -- 优先使用它们
- [ ] 旋转数组：始终先确定哪一半是有序的
- [ ] 对于 MLE：二分查找出现在超参数调优（二分学习率）、阈值优化（ROC 曲线）和分位数计算中
"""

TRANSLATIONS[53] = r"""# BFS / DFS

## Overview
**BFS (Breadth-First Search，广度优先搜索)** 和 **DFS (Depth-First Search，深度优先搜索)** 是两种基础的图/树遍历策略。BFS 在无权图中找到最短路径，逐层处理节点。DFS 深度探索，驱动 **Topological Sort（拓扑排序）**、环检测和连通分量分析。每个图问题都可以归结为这两种遍历之一加上特定问题的处理。

## Core Concepts

### BFS (Breadth-First Search)
使用队列。在距离 $$d+1$$ 之前探索所有距离为 $$d$$ 的邻居。

**性质**：
- 保证在无权图中找到最短路径
- 时间：$$O(V + E)$$，空间：$$O(V)$$（用于队列）
- 树的层序遍历就是 BFS

### DFS (Depth-First Search)
使用栈（或递归）。尽可能深入探索然后回溯。

**性质**：
- 不保证最短路径
- 时间：$$O(V + E)$$，空间：$$O(V)$$（用于递归栈）
- 环检测的三种状态：未访问、处理中、已完成

### Multi-Source BFS
从多个源点同时开始 BFS。所有源点在距离 0 时入队。用于"距离最近的 X"问题（如 01 矩阵、腐烂的橘子）。

### Topological Sort (DFS-based)
对于 **DAG (Directed Acyclic Graph，有向无环图)**，产生一个线性排序，使得每条边 $$(u, v)$$ 中 $$u$$ 在 $$v$$ 之前：
- DFS 后序遍历，然后反转
- 或者：如果一个节点在处理中被重新访问，则检测到环

$$
\text{Topological order exists} \iff \text{graph is a DAG (no cycles)}
$$

拓扑序存在当且仅当图是 DAG（无环）。

## Implementation

```python
from collections import deque

def bfs_shortest_path(graph: dict[int, list[int]], start: int,
                      end: int) -> int:
    # Shortest path in unweighted graph. Returns distance or -1.
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for nei in graph[node]:
            if nei not in visited:
                visited.add(nei)
                queue.append((nei, dist + 1))
    return -1

def topological_sort(graph: dict[int, list[int]], n: int) -> list[int]:
    # Kahn's algorithm (BFS-based). Returns [] if cycle exists.
    in_degree = [0] * n
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order: list[int] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return order if len(order) == n else []
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| BFS 最短路径 | 无权图距离 | BFS 保证最少跳数；入队时加入 visited（非出队时） |
| 多源 BFS | 距离最近源点 | 一次性将所有源点入队；逐层处理 |
| DFS + 回溯 | 路径枚举、排列 | 进入时标记 visited，退出时取消标记 |
| 拓扑排序 | 任务调度、课程先修 | Kahn's（BFS + 入度）或 DFS 后序反转 |
| DFS 环检测 | 有向图的环 | 三色标记：白色（未访问）、灰色（处理中）、黑色（完成） |
| 网格 BFS/DFS | 岛屿、网格最短路径 | 四方向邻居；标记 visited 避免重复访问 |

### Common Interview Questions
- [ ] Number of Islands（岛屿数量，网格 DFS/BFS）
- [ ] Rotting Oranges（腐烂的橘子，多源 BFS）
- [ ] Course Schedule I/II（课程表，拓扑排序、环检测）
- [ ] Word Ladder（单词接龙，BFS 最短转换）
- [ ] Clone Graph（克隆图，BFS/DFS + 哈希表）
- [ ] Pacific Atlantic Water Flow（太平洋大西洋水流，从边界 DFS）

## Comparisons

| Aspect | BFS | DFS |
|--------|-----|-----|
| 数据结构 | 队列 | 栈 / 递归 |
| 最短路径（无权） | 是 | 否 |
| 空间（树） | $$O(w)$$ 宽度 | $$O(h)$$ 高度 |
| 空间（图） | $$O(V)$$ | $$O(V)$$ |
| 环检测（有向） | 通过入度（Kahn's） | 通过三色标记 |
| 最适合 | 最短路径、层序 | 拓扑排序、路径存在性、回溯 |

## Key Takeaways
- [ ] BFS = 无权图最短路径；DFS = 探索所有路径 / 拓扑排序
- [ ] BFS 中在入队时加入 visited，而非出队时 -- 避免重复处理
- [ ] 多源 BFS：将所有源点在距离 0 处入队以找"最近源点"距离
- [ ] 拓扑排序：Kahn's 算法（BFS 方式）在面试中通常比基于 DFS 的方式更简洁
- [ ] 对于 MLE：BFS/DFS 驱动图神经网络的消息传递、ML 管道中的依赖解析和知识图谱遍历
"""

TRANSLATIONS[54] = r"""# Dynamic Programming

## Overview
**Dynamic Programming（动态规划，DP）** 通过缓存子问题的结果来解决具有 **Overlapping Subproblems（重叠子问题）** 和 **Optimal Substructure（最优子结构）** 的问题。它可以说是编程面试中最重要的算法范式 -- 也是最难的之一。关键技能是识别状态、转移方程和基本情况。对于 MLE，DP 出现在序列对齐（NLP）、**Viterbi Decoding（维特比解码，HMM）** 和编辑距离计算中。

## Core Concepts

### DP Framework
每个 DP 问题有三个组成部分：
1. **状态**：什么信息定义了一个子问题？（如 `dp[i]` = 使用前 $$i$$ 个元素的最优答案）
2. **转移**：子问题的答案如何与更小的子问题关联？
3. **基本情况**：哪些子问题可以直接求解？

$$
dp[i] = f(dp[i-1], dp[i-2], \ldots) \quad \text{(recurrence relation)}
$$

即递推关系。

### Top-Down (Memoization) vs Bottom-Up (Tabulation)
- **自顶向下（记忆化）**：递归 + `@lru_cache`；更容易编写，但空间优化更难
- **自底向上（制表法）**：迭代，从基本情况填充表格；可以进行空间优化

### Common DP Categories

| Category | State | Example |
|----------|-------|---------|
| 一维（线性） | `dp[i]` | 爬楼梯、打家劫舍 |
| 二维（网格/序列） | `dp[i][j]` | 编辑距离、LCS、不同路径 |
| 背包 | `dp[i][w]` | 0/1 背包、零钱兑换、子集和 |
| 区间 | `dp[i][j]` = 子数组 $$[i, j]$$ 的答案 | 矩阵链乘、戳气球 |
| 状态压缩 | `dp[mask]` | TSP、分配问题 |
| 状态机 | `dp[i][state]` | 买卖股票含冷冻期 |

### Space Optimization
当 `dp[i]` 仅依赖 `dp[i-1]`（或固定数量的前几行）时，空间从 $$O(n^2)$$ 降到 $$O(n)$$ 或 $$O(1)$$，只需保留所需的行。

## Implementation

```python
from functools import lru_cache

def longest_common_subsequence(s1: str, s2: str) -> int:
    # LCS via bottom-up DP. O(mn) time, O(n) space.
    m, n = len(s1), len(s2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[n]

def coin_change(coins: list[int], amount: int) -> int:
    # Minimum coins to make amount. O(amount * len(coins)).
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != float("inf") else -1
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 一维 DP | 带局部选择的序列 | 通常可优化到 $$O(1)$$ 空间（Fibonacci 模式） |
| 二维网格 | 不同路径、最小路径和 | 逐行填充；仅需前一行时可优化为一维 |
| 0/1 背包 | 有容量限制的子集选择 | 一维空间优化时内层循环倒序 |
| 完全背包 | 零钱兑换、物品无限 | 内层循环正序（物品可重复使用） |
| LCS / 编辑距离 | 字符串比较 | 经典二维 DP；空间可优化到 $$O(\min(m,n))$$ |
| 状态机 | 含状态的股票交易 | 明确定义状态（持有、未持有、冷冻期） |

### Common Interview Questions
- [ ] Climbing Stairs / House Robber（一维 DP）
- [ ] Longest Common Subsequence（最长公共子序列）
- [ ] Edit Distance（编辑距离 / Levenshtein 距离）
- [ ] Coin Change（零钱兑换）
- [ ] 0/1 Knapsack / Partition Equal Subset Sum（0/1 背包 / 分割等和子集）
- [ ] Best Time to Buy and Sell Stock（含冷冻期/手续费）
- [ ] Longest Increasing Subsequence（最长递增子序列，$$O(n \log n)$$ 配合二分查找）
- [ ] Word Break（单词拆分）

## Common Pitfalls
- **状态定义错误**：如果写不出清晰的递推关系，说明状态定义有问题。增加维度（如"是否包含最后一个元素"作为状态）
- **未初始化基本情况**：`dp[0] = ...` 必须在循环之前设置。遗漏基本情况会导致无声的错误答案
- **空间优化方向搞反**：0/1 背包一维化时容量从高到低遍历；完全背包从低到高遍历。搞反会得到错误结果
- **混淆子序列和子数组**：子序列 = 不必连续（索引上的 DP）；子数组 = 连续的（滑动窗口或前缀和通常就够了）

## Key Takeaways
- [ ] 从精确定义状态开始 -- 模糊的状态定义导致错误的转移
- [ ] 自顶向下写起来更快；自底向上可以空间优化 -- 两种都要会
- [ ] 0/1 背包：一维化时容量倒序遍历；完全背包：正序遍历
- [ ] 编辑距离是经典的二维 DP，直接应用于 NLP（拼写纠正、序列对齐）
- [ ] 对于 MLE：DP 是 Viterbi 解码（HMM）、CTC Loss（语音识别）、Beam Search 剪枝和生物信息学序列比对的基础
"""

TRANSLATIONS[55] = r"""# Greedy

## Overview
**Greedy Algorithm（贪心算法）** 在每一步做出局部最优选择，期望达到全局最优。当问题具有 **Greedy Choice Property（贪心选择性质，局部最优选择可导致全局最优解）** 和 **Optimal Substructure（最优子结构）** 时，贪心算法有效。贪心比 DP 更快（当适用时），但证明正确性是难点。对于 MLE，贪心算法出现在特征选择、调度和压缩（Huffman 编码）中。

## Core Concepts

### When Greedy Works
贪心算法在以下条件成立时是正确的：
1. **贪心选择性质**：全局最优解可以通过做出局部最优选择来构造
2. **最优子结构**：最优解包含子问题的最优解

**证明技术**：
- **Exchange Argument（交换论证）**：证明将最优解中的任何元素替换为贪心选择不会使结果变差
- **Stays-ahead（领先法）**：证明贪心解在每一步至少与其他任何解一样好

### Greedy vs Dynamic Programming
贪心每步只做一个选择，不回头重新考虑。DP 探索所有选择并选择最优的。如果贪心方法存在，它总是比 DP 更高效。

$$
\text{Greedy} \subseteq \text{DP-solvable problems}
$$

贪心可解的问题是 DP 可解问题的子集。

### Common Greedy Strategies
- **排序后贪心选取**：区间、作业、任务
- **Priority Queue（优先队列 / 堆）**：始终处理最紧急/最有价值的下一个
- **双指针**：从两端贪心分配资源

## Implementation

```python
def min_meeting_rooms(intervals: list[list[int]]) -> int:
    # Minimum meeting rooms needed. O(n log n).
    import heapq
    intervals.sort(key=lambda x: x[0])
    heap: list[int] = []  # end times of active meetings
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)  # reuse room
        heapq.heappush(heap, end)
    return len(heap)

def max_non_overlapping_intervals(intervals: list[list[int]]) -> int:
    # Maximum non-overlapping intervals. O(n log n).
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count = 0
    prev_end = float("-inf")
    for start, end in intervals:
        if start >= prev_end:
            count += 1
            prev_end = end
    return count

def assign_cookies(children: list[int], cookies: list[int]) -> int:
    # Assign smallest sufficient cookie to each child. O(n log n).
    children.sort()
    cookies.sort()
    child = cookie = 0
    while child < len(children) and cookie < len(cookies):
        if cookies[cookie] >= children[child]:
            child += 1
        cookie += 1
    return child
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 按结束时间排序 | 区间调度（最大不重叠） | 最早结束时间 = 为后续区间留出最多空间 |
| 按开始时间排序 + 堆 | 最少资源（会议室） | 堆跟踪结束时间；如果最早结束 <= 开始则重用 |
| 按比率排序 | 分数背包、作业调度 | 价值/重量比最大化总价值 |
| Huffman 编码 | 最优前缀编码 | 合并两个最小频率；自底向上构建最优树 |
| Jump Game | 能否到达终点？/ 最少跳跃次数 | 贪心跟踪最远可达位置 |

### Common Interview Questions
- [ ] Non-overlapping Intervals（无重叠区间，按结束时间排序）
- [ ] Meeting Rooms II（最少会议室，基于堆）
- [ ] Task Scheduler（任务调度器，贪心 + 空闲槽位）
- [ ] Jump Game I and II（跳跃游戏）
- [ ] Gas Station（加油站，环形贪心）
- [ ] Candy Distribution（分糖果，两遍贪心）
- [ ] Reorganize String（重组字符串，贪心 + 最大堆）

## Comparisons

| Aspect | Greedy | Dynamic Programming | Brute Force |
|--------|--------|-------------------|-------------|
| 时间 | 通常 $$O(n \log n)$$ | $$O(n^2)$$ 或 $$O(nW)$$ | 指数级 |
| 正确性 | 需要证明 | 总是正确 | 总是正确 |
| 方法 | 每步一个选择 | 探索所有选择 | 所有组合 |
| 空间 | 通常 $$O(1)$$ | $$O(n)$$ 到 $$O(n^2)$$ | 不定 |
| 何时使用 | 贪心选择性质成立时 | 重叠子问题 | 小规模输入 |

## Key Takeaways
- [ ] 排序几乎总是贪心区间/调度问题的第一步
- [ ] "最大不重叠"按结束时间排序；"最少资源"按开始时间排序 + 堆
- [ ] 如果贪心方法看似可行，先用交换论证验证再编码
- [ ] 如果贪心在反例上失败，切换到 DP -- 许多问题看起来像贪心但实际不是
- [ ] 对于 MLE：贪心驱动前向特征选择、压缩中的 Huffman 编码和语言模型中的贪心解码
"""

TRANSLATIONS[56] = r"""# Backtracking

## Overview
**Backtracking（回溯法）** 通过递增地构建选择并放弃（"剪枝"）无法导致有效解的分支来系统地探索所有候选解。它是解决组合问题的首选方法：排列、组合、子集、N 皇后和约束满足。对于 MLE，回溯法是 Beam Search 变体、基于约束的特征选择和超参数网格搜索的基础。

## Core Concepts

### Backtracking Framework
每个回溯问题遵循以下模板：
1. **选择 (Choose)**：做一个决定（将元素添加到当前路径）
2. **探索 (Explore)**：带着已做的选择递归
3. **撤销 (Unchoose)**：撤销决定（回溯）

$$
\text{Prune: if current state violates constraints, return early (do not recurse)}
$$

剪枝：如果当前状态违反约束，提前返回（不再递归）。

### Time Complexity
回溯探索一棵决策树。没有剪枝时：
- $$n$$ 个元素的排列：$$O(n!)$$
- $$n$$ 个元素的子集：$$O(2^n)$$
- 从 $$n$$ 中选 $$k$$ 的组合：$$O(\binom{n}{k})$$

剪枝减少常数因子，但不改变最坏情况复杂度。

### Pruning Strategies
- **约束检查**：立即跳过违反约束的选择
- **排序 + 跳过重复**：排序输入，当 `i > start and nums[i] == nums[i-1]` 时跳过
- **界估计**：如果剩余元素无法改善当前最优解则剪枝（分支限界）

## Implementation

```python
def subsets(nums: list[int]) -> list[list[int]]:
    # Generate all subsets. O(2^n).
    result: list[list[int]] = []
    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result

def permutations(nums: list[int]) -> list[list[int]]:
    # Generate all permutations. O(n!).
    result: list[list[int]] = []
    def backtrack(path: list[int], used: set[int]) -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if i in used:
                continue
            used.add(i)
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used.discard(i)
    backtrack([], set())
    return result

def solve_n_queens(n: int) -> int:
    # Count N-Queens solutions. Prune by column and diagonals.
    count = 0
    cols: set[int] = set()
    diag1: set[int] = set()  # row - col
    diag2: set[int] = set()  # row + col
    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:
            count += 1
            return
        for col in range(n):
            if col in cols or row - col in diag1 or row + col in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            backtrack(row + 1)
            cols.discard(col); diag1.discard(row - col); diag2.discard(row + col)
    backtrack(0)
    return count
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 子集 | 生成所有子集 | 起始索引控制包含；选择包含或跳过每个元素 |
| 排列 | 所有排序方式 | 使用 `used` 集合或基于交换的方法 |
| 组合 | 从 $$n$$ 中选 $$k$$ | 类似子集但在路径长度 = $$k$$ 时停止 |
| 约束满足 | N 皇后、数独 | 用集合跟踪约束实现 $$O(1)$$ 有效性检查 |
| 单词搜索 / 路径 | 在网格中找单词 | DFS + 回溯 + visited 标记 |
| 回文分割 | 将字符串分割为回文串 | 选择每个有效的回文前缀，对剩余部分递归 |

### Common Interview Questions
- [ ] Subsets / Subsets II（子集/含重复元素的子集）
- [ ] Permutations / Permutations II（排列/含重复元素的排列）
- [ ] Combination Sum（组合总和，无限使用）/ Combination Sum II（每个只用一次）
- [ ] N-Queens（N 皇后）
- [ ] Word Search（网格路径查找）
- [ ] Palindrome Partitioning（回文分割）
- [ ] Generate Parentheses（括号生成）

## Comparisons

| Aspect | Backtracking | BFS/DFS | Dynamic Programming |
|--------|-------------|---------|-------------------|
| 目标 | 所有有效解 | 遍历/最短路径 | 最优值 |
| 剪枝 | 是（关键优势） | 有限 | 不适用（所有状态都计算） |
| 空间 | $$O(n)$$ 递归深度 | $$O(V)$$ | $$O(\text{state space})$$ |
| 何时使用 | 枚举组合 | 图遍历 | 有重叠子问题的优化 |

## Key Takeaways
- [ ] 掌握选择-探索-撤销模板 -- 几乎适用于所有组合问题
- [ ] 处理重复：排序数组，当 `i > start` 时跳过 `nums[i] == nums[i-1]`
- [ ] N 皇后：用集合跟踪列和两条对角线，实现 $$O(1)$$ 约束检查
- [ ] 回溯探索指数级空间 -- 剪枝是 TLE 和 AC 之间的关键差异
- [ ] 对于 MLE：回溯驱动 AutoML 中的约束搜索、NLP 中带剪枝的 Beam Search 和特征选择中的组合优化
"""

TRANSLATIONS[57] = r"""# Graph Algorithms

## Overview
**Graph（图）** 建模关系和网络 -- 从社交网络到 ML 计算图。除了 BFS/DFS（已在单独章节中介绍），关键图算法包括最短路径（Dijkstra、Bellman-Ford）、**MST (Minimum Spanning Tree，最小生成树)**（Kruskal、Prim）和强连通分量。对于 MLE，图是知识图谱、**GNN (Graph Neural Network，图神经网络)**、ML 管道中的依赖解析和网络分析的核心。

## Core Concepts

### Graph Representations

| Representation | Space | Edge Lookup | Best For |
|---------------|-------|------------|---------|
| **Adjacency List（邻接表）** | $$O(V + E)$$ | $$O(\text{degree})$$ | 稀疏图（大多数真实场景） |
| **Adjacency Matrix（邻接矩阵）** | $$O(V^2)$$ | $$O(1)$$ | 稠密图、矩阵运算 |
| **Edge List（边列表）** | $$O(E)$$ | $$O(E)$$ | Kruskal 算法、简单遍历 |

### Dijkstra's Algorithm
从源点到所有顶点的最短路径（非负权重的加权图）：

$$
\text{dist}[v] = \min_{(u,v) \in E}(\text{dist}[u] + w(u,v))
$$

时间：$$O((V + E) \log V)$$（使用最小堆）。不适用于负权重。

### Bellman-Ford Algorithm
处理负权重。对所有边松弛 $$V - 1$$ 次：

$$
\text{For each edge } (u, v, w): \quad \text{dist}[v] = \min(\text{dist}[v], \text{dist}[u] + w)
$$

时间：$$O(VE)$$。可检测负环（如果第 $$V-1$$ 次迭代后仍然能松弛则存在负环）。

### Minimum Spanning Tree
用最小总边权连接所有顶点：
- **Kruskal 算法**：按权重排序边，贪心添加（不形成环则添加，使用并查集）。$$O(E \log E)$$
- **Prim 算法**：从一个顶点开始生长树，始终添加连接到新顶点的最便宜的边（使用堆）。$$O((V+E) \log V)$$

## Implementation

```python
import heapq
from collections import defaultdict

def dijkstra(graph: dict[int, list[tuple[int, int]]],
             start: int) -> dict[int, int]:
    # Shortest paths from start. graph[u] = [(v, weight), ...].
    dist: dict[int, int] = {start: 0}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue  # stale entry (lazy deletion)
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

def kruskal_mst(n: int, edges: list[tuple[int, int, int]]) -> int:
    # MST weight using Kruskal's. edges = [(u, v, w), ...].
    edges.sort(key=lambda e: e[2])
    parent = list(range(n))
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total = count = 0
    for u, v, w in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            count += 1
            if count == n - 1:
                break
    return total
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Dijkstra | 最短路径、非负权重 | 懒删除：弹出距离 > 记录距离时跳过 |
| Bellman-Ford | 负权重、最多 k 站的最便宜航班 | 松弛所有边 $$V-1$$ 次；k 站变体需要复制 dist 数组 |
| Kruskal + Union-Find | MST、最小连接代价 | 排序边 + 并查集；在 $$V-1$$ 条边时停止 |
| 拓扑排序 + DP | DAG 中的最短/最长路径 | 按拓扑序处理；松弛边 |
| Floyd-Warshall | 全源最短路径 | $$O(V^3)$$；适用于小图 |
| 二部图检测 | 图着色、匹配 | BFS/DFS 加 2 色标记 |

### Common Interview Questions
- [ ] Network Delay Time（网络延迟时间，Dijkstra）
- [ ] Cheapest Flights Within K Stops（K 站内最便宜的航班，Bellman-Ford 变体）
- [ ] Minimum Spanning Tree（最小生成树，Kruskal 或 Prim）
- [ ] Course Schedule（课程表，拓扑排序 -- 见 BFS/DFS 章节）
- [ ] Is Graph Bipartite?（判断二部图）
- [ ] Minimum Cost to Connect All Points（连接所有点的最小费用）

## Comparisons

| Algorithm | Time | Negative Weights | Use Case |
|-----------|------|-----------------|----------|
| Dijkstra | $$O((V+E) \log V)$$ | 否 | 单源、非负权重 |
| Bellman-Ford | $$O(VE)$$ | 是 | 单源、负权重 |
| Floyd-Warshall | $$O(V^3)$$ | 是（无负环） | 全源 |
| Kruskal | $$O(E \log E)$$ | 不适用 | MST |
| Prim | $$O((V+E) \log V)$$ | 不适用 | MST（稠密图） |

## Key Takeaways
- [ ] 带懒删除的 Dijkstra（跳过过期堆条目）是面试中最简洁的实现
- [ ] Kruskal = 排序边 + 并查集；Prim = 从顶点开始 + 堆。两者都得到 MST
- [ ] Bellman-Ford："最多 K 站的最便宜"问题需要在每轮之间复制距离数组
- [ ] 始终明确：有向/无向、有权/无权、是否可能有负权重？
- [ ] 对于 MLE：图算法驱动 GNN 消息传递（类 BFS）、计算图优化（拓扑排序）和推荐系统中的网络流
"""

TRANSLATIONS[58] = r"""# Divide & Conquer

## Overview
**Divide and Conquer（分治法）** 将问题分成独立的子问题，递归求解每个子问题，然后合并结果。经典例子包括归并排序、快速排序和二分查找（已在单独章节中介绍）。面试中的关键是识别何时问题具有可以高效合并的独立子问题。对于 MLE，分治法出现在并行训练（数据并行）、MapReduce 和递归特征消除中。

## Core Concepts

### D&C Framework
1. **Divide（分）**：将问题分成更小的子问题
2. **Conquer（治）**：递归求解子问题（小输入直接求解）
3. **Combine（合）**：将子问题的解合并为最终答案

### Master Theorem
对于形如 $$T(n) = aT(n/b) + O(n^d)$$ 的递推关系：

$$
T(n) = \begin{cases}
O(n^d) & \text{if } d > \log_b a \\
O(n^d \log n) & \text{if } d = \log_b a \\
O(n^{\log_b a}) & \text{if } d < \log_b a
\end{cases}
$$

**Master Theorem（主定理）** 的应用示例：
- 归并排序：$$T(n) = 2T(n/2) + O(n) \Rightarrow O(n \log n)$$（情况 2：$$a=2, b=2, d=1$$）
- 二分查找：$$T(n) = T(n/2) + O(1) \Rightarrow O(\log n)$$（情况 1：$$a=1, b=2, d=0$$）
- Strassen 矩阵乘法：$$T(n) = 7T(n/2) + O(n^2) \Rightarrow O(n^{\log_2 7}) \approx O(n^{2.81})$$（情况 3）

### Merge Sort: The Canonical D&C Example
将数组分成两半，分别排序，然后 $$O(n)$$ 合并。始终 $$O(n \log n)$$，稳定排序，但需要 $$O(n)$$ 额外空间。

### Quick Select
在 $$O(n)$$ 期望时间内找到第 $$k$$ 小的元素，使用随机化分区：
- 围绕随机主元进行分区
- 仅对包含目标索引的那一半递归

$$
T(n) = T(n/2) + O(n) \Rightarrow O(n) \text{ expected}
$$

期望时间 $$O(n)$$。

## Implementation

```python
def merge_sort(arr: list[int]) -> list[int]:
    # Merge sort. O(n log n) time, O(n) space.
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)

def _merge(a: list[int], b: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result

def quick_select(nums: list[int], k: int) -> int:
    # Find k-th smallest (0-indexed). O(n) expected.
    import random
    if len(nums) == 1:
        return nums[0]
    pivot = random.choice(nums)
    lo = [x for x in nums if x < pivot]
    eq = [x for x in nums if x == pivot]
    hi = [x for x in nums if x > pivot]
    if k < len(lo):
        return quick_select(lo, k)
    elif k < len(lo) + len(eq):
        return pivot
    else:
        return quick_select(hi, k - len(lo) - len(eq))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 归并排序变体 | 逆序对计数、链表排序 | 合并步骤中的计数捕获跨分区的关系 |
| Quick Select | 第 K 大/小 | $$O(n)$$ 平均；随机化主元避免最坏情况 |
| 对半分割数组 | 最近点对、最大子数组 | 合并步骤是关键 -- 通常 $$O(n)$$ 或 $$O(n \log n)$$ |
| 递归矩阵运算 | 矩阵乘法 (Strassen) | 将 8 次乘法减少到 7 次，达到 $$O(n^{2.81})$$ |
| 树递归即分治 | 大多数树问题 | 左/右子树是独立的子问题 |

### Common Interview Questions
- [ ] Merge Sort（实现 + 稳定性分析）
- [ ] Kth Largest Element（Quick Select）
- [ ] Count of Smaller Numbers After Self（归并排序 + 逆序对计数）
- [ ] Maximum Subarray（分治法，与 Kadane 算法对比）
- [ ] Sort List（链表归并排序 -- $$O(1)$$ 额外空间）
- [ ] Median of Two Sorted Arrays（$$O(\log \min(m,n))$$ 分治）

## Comparisons

| Aspect | Merge Sort | Quick Sort | Quick Select |
|--------|-----------|------------|-------------|
| 时间（平均） | $$O(n \log n)$$ | $$O(n \log n)$$ | $$O(n)$$ |
| 时间（最坏） | $$O(n \log n)$$ | $$O(n^2)$$ | $$O(n^2)$$ |
| 空间 | $$O(n)$$ | $$O(\log n)$$ 栈 | $$O(n)$$ |
| 稳定 | 是 | 否（标准版） | 不适用 |
| 原地 | 否 | 是 | 视情况 |

## Key Takeaways
- [ ] 掌握主定理以快速分析分治递推的复杂度
- [ ] 归并排序是稳定 $$O(n \log n)$$ 排序的首选；合并步骤可复用于计数问题
- [ ] Quick Select 提供 $$O(n)$$ 期望的第 k 个元素 -- 始终随机化主元
- [ ] "合并"步骤通常是分治中最难的部分 -- 将分析重点放在那里
- [ ] 对于 MLE：分治法是数据并行训练（将 batch 分到多个 GPU，平均梯度）、分布式特征工程的 MapReduce 以及决策树递归分裂的基础
"""

TRANSLATIONS[59] = r"""# Matrix / Tensor Operations

## Overview
**Matrix（矩阵）** 和 **Tensor（张量）** 运算是机器学习的计算基础。每次前向传播、反向传播步骤和数据变换都涉及矩阵乘法、reshape 和逐元素操作。MLE 面试经常测试 NumPy/PyTorch 的熟练程度、**Broadcasting（广播）** 规则以及将循环向量化的能力。在底层理解这些操作对优化 ML 系统至关重要。

## Core Concepts

### Matrix Multiplication
对于矩阵 $$A \in \mathbb{R}^{m \times k}$$ 和 $$B \in \mathbb{R}^{k \times n}$$：

$$
C = AB, \quad C_{ij} = \sum_{l=1}^{k} A_{il} B_{lj}
$$

复杂度：$$O(mkn)$$。实际中，**BLAS (Basic Linear Algebra Subprograms)** 库（MKL、cuBLAS）通过缓存优化的分块实现接近峰值 FLOPS。

### Broadcasting Rules (NumPy/PyTorch)
在不同形状的数组上操作时，从末尾维度开始比较：
1. 维度兼容的条件是它们相等或其中一个为 1
2. 缺失的维度被视为大小 1（在前面补充）
3. 大小为 1 的维度被拉伸以匹配另一个

$$
(3, 4, 1) \odot (1, 4, 5) \to (3, 4, 5)
$$

### Key Tensor Operations

| Operation | NumPy | PyTorch | Notes |
|-----------|-------|---------|-------|
| 矩阵乘法 | `A @ B` 或 `np.matmul` | `torch.matmul` | 处理批量维度 |
| 逐元素 | `A * B` | `A * B` | 适用广播规则 |
| 转置 | `A.T` 或 `np.swapaxes` | `A.T` 或 `.permute` | `.T` 仅适用于二维 |
| Reshape | `A.reshape(m, n)` | `A.view(m, n)` | `view` 要求内存连续 |
| 规约 | `np.sum(A, axis=0)` | `A.sum(dim=0)` | keepdim 用于广播 |

### Einsum Notation
**Einsum（爱因斯坦求和约定）** 提供了一个简洁、通用的张量收缩接口：

```
np.einsum('ij,jk->ik', A, B)  # matrix multiply
np.einsum('bij,bjk->bik', A, B)  # batched matmul
np.einsum('ij->j', A)  # column sum
np.einsum('ii->', A)  # trace
```

## Implementation

```python
import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    # Numerically stable softmax along last axis.
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)

def batch_cosine_similarity(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # Cosine similarity between rows of A and B. O(n*d).
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return A_norm @ B_norm.T  # (n, m) similarity matrix

def attention_scores(Q: np.ndarray, K: np.ndarray,
                     V: np.ndarray) -> np.ndarray:
    # Scaled dot-product attention. Q,K,V shape: (seq, d_k).
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)  # (seq, seq)
    weights = softmax(scores)
    return weights @ V  # (seq, d_v)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 向量化距离 | 成对距离、相似度 | 使用广播：$$(A - B)^2$$ 配合形状操作 |
| 数值稳定性 | Softmax、log-sum-exp | 在 exp 之前减去最大值防止溢出 |
| 批量操作 | 处理多个样本 | 添加 batch 维度；使用 `einsum` 或批量矩阵乘法 |
| Reshape 以广播 | 特征-目标交互 | 调整形状对齐维度，然后逐元素乘 |
| 原地操作 | 内存效率 | 使用 `out=` 参数或原地运算符 |

### Common Interview Questions
- [ ] 实现 softmax（数值稳定版）
- [ ] 实现注意力机制（缩放点积注意力）
- [ ] 不使用循环计算成对欧氏距离
- [ ] 实现 Batch Normalization（前向传播）
- [ ] 使用广播将嵌套循环计算向量化
- [ ] 解释并使用 einsum 进行给定的张量收缩

## Comparisons

| Aspect | For 循环 | 向量化 (NumPy) | GPU (PyTorch) |
|--------|----------|-------------------|---------------|
| 速度（1M 元素） | 秒级 | 毫秒级 | 微秒级 |
| 内存控制 | 细粒度 | 中间副本 | GPU 内存限制 |
| 调试 | 容易 | 中等（形状错误） | 困难（异步） |
| 最适合 | 原型开发 | CPU 生产环境 | 训练/推理 |

## Key Takeaways
- [ ] 始终向量化：用 NumPy/PyTorch 操作替代 Python 循环可获得 100-1000 倍加速
- [ ] 广播规则：从末尾维度对齐；大小为 1 的维度拉伸以匹配
- [ ] 数值稳定性：softmax 前减去最大值，使用 log-sum-exp 替代 log(sum(exp))
- [ ] Einsum 是张量收缩的通用工具 -- 学习其表示法
- [ ] 面试准备：准备好仅使用 NumPy 从零实现 softmax、注意力、余弦相似度和 batch norm
"""

TRANSLATIONS[60] = r"""# Implement ML Algorithms from Scratch

## Overview
从零实现 ML 算法是 MLE 面试的核心技能，测试候选人对 API 调用之外的理解深度。面试官希望看到你理解数学原理、能将其转化为代码、处理边界情况并推理收敛性。常见目标：**Linear Regression（线性回归）**、**Logistic Regression（逻辑回归）**、**K-Means（K 均值聚类）**、**KNN (K-Nearest Neighbors，K 近邻)**、**Decision Tree（决策树）** 和 **Gradient Descent（梯度下降）**。重点是清晰、正确的实现，而非过度优化。

## Core Concepts

### Gradient Descent
**Gradient Descent（梯度下降）** 是大多数 ML 优化的基础。更新规则：

$$
\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)
$$

**变体**：
- **Batch GD（批量梯度下降）**：每次更新使用所有样本。稳定但对大数据集慢
- **SGD (Stochastic Gradient Descent，随机梯度下降)**：每次更新使用一个样本。有噪声但快
- **Mini-batch（小批量）**：折中方案。实践中的标准（batch size 32-256）

### K-Means Clustering
**K-Means（K 均值聚类）** 的迭代算法：
1. 初始化 $$k$$ 个质心（随机或 K-Means++）
2. 将每个点分配到最近的质心：$$c_i = \arg\min_j \|x_i - \mu_j\|^2$$
3. 更新质心：$$\mu_j = \frac{1}{|C_j|}\sum_{x \in C_j} x$$
4. 重复直到收敛

$$
\text{Objective: } J = \sum_{j=1}^{k} \sum_{x \in C_j} \|x - \mu_j\|^2
$$

目标函数为所有簇内距离的平方和。

### Decision Tree (CART)
对于每个节点，找到最佳分裂：

$$
\text{Best split} = \arg\min_{f, t} \left[ \frac{|L|}{|N|} G(L) + \frac{|R|}{|N|} G(R) \right]
$$

其中 $$G$$ 是 **Gini Impurity（基尼不纯度）** 或 **Entropy（熵）**，$$f$$ 是特征，$$t$$ 是阈值。

### K-Nearest Neighbors
分类：$$k$$ 个最近邻的多数投票。回归：平均值。
距离度量很重要：**Euclidean Distance（欧氏距离，$$L_2$$）**、**Manhattan Distance（曼哈顿距离，$$L_1$$）** 或 **Cosine Similarity（余弦相似度）**。

## Implementation

```python
import numpy as np

class KMeans:
    def __init__(self, k: int, max_iters: int = 100) -> None:
        self.k = k
        self.max_iters = max_iters

    def fit(self, X: np.ndarray) -> "KMeans":
        idx = np.random.choice(len(X), self.k, replace=False)
        self.centroids = X[idx]
        for _ in range(self.max_iters):
            dists = np.linalg.norm(
                X[:, None] - self.centroids[None, :], axis=2
            )  # (n, k)
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array([
                X[labels == j].mean(axis=0) if np.any(labels == j)
                else self.centroids[j]
                for j in range(self.k)
            ])
            if np.allclose(new_centroids, self.centroids):
                break
            self.centroids = new_centroids
        self.labels_ = labels
        return self

class LogisticRegressionScratch:
    def fit(self, X: np.ndarray, y: np.ndarray,
            lr: float = 0.01, epochs: int = 1000) -> "LogisticRegressionScratch":
        n, d = X.shape
        self.w = np.zeros(d)
        self.b = 0.0
        for _ in range(epochs):
            z = X @ self.w + self.b
            pred = 1 / (1 + np.exp(-z))
            self.w -= lr * (X.T @ (pred - y)) / n
            self.b -= lr * np.mean(pred - y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-(X @ self.w + self.b)))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 梯度下降循环 | 任何可微损失 | 解析计算梯度；在样本上向量化 |
| 距离矩阵 | KNN、K-Means | 广播：`X[:, None] - centroids[None, :]` 计算所有成对距离 |
| 递归分裂 | 决策树 | 在左/右子集上递归；跟踪深度用于停止 |
| 收敛检查 | 迭代算法 | 检查参数变化或损失变化 < epsilon |
| 数值稳定性 | Sigmoid、Softmax | 裁剪输入或使用对数空间计算 |

### Common Interview Questions
- [ ] 用梯度下降实现线性回归
- [ ] 从零实现逻辑回归
- [ ] 实现 K-Means 聚类
- [ ] 实现 KNN 分类器
- [ ] 实现简单决策树（基尼或熵分裂）
- [ ] 实现带动量的梯度下降

## Comparisons

| Algorithm | Training Time | Prediction Time | Handles Nonlinearity |
|-----------|-------------|----------------|---------------------|
| Linear Regression | $$O(nd)$$ 每轮 | $$O(d)$$ | 否 |
| Logistic Regression | $$O(nd)$$ 每轮 | $$O(d)$$ | 否（线性边界） |
| KNN | 无（懒惰学习） | $$O(nd)$$ | 是 |
| K-Means | $$O(nkd)$$ 每次迭代 | $$O(kd)$$ | 否（球形簇） |
| Decision Tree | $$O(n d \log n)$$ | $$O(\text{depth})$$ | 是 |

## Key Takeaways
- [ ] 对每个算法要知道损失函数及其梯度 -- 面试官会要求你推导
- [ ] 一切都要向量化：避免在样本上使用 Python for 循环；使用矩阵运算
- [ ] 处理边界情况：K-Means 中的空簇、逻辑回归中的完美分离、树中的单类叶节点
- [ ] K-Means++ 初始化在实践中很重要 -- 即使实现随机初始化也要提到它
- [ ] 对于 MLE 面试：准备好扩展基本实现（添加正则化、小批量、早停）
"""

TRANSLATIONS[61] = r"""# Data Processing Pipeline

## Overview
数据处理是 MLE 花费最多时间的环节。面试题测试你使用 pandas、SQL 或纯 Python 编写干净、高效数据转换的能力。关键技能包括处理缺失值、特征工程、连接操作和编写可扩展的管道。这些问题比算法题更实用，直接评估日常 MLE 的工作能力。

## Core Concepts

### Data Cleaning Patterns
- **Missing Values（缺失值）**：用 `isna()` 检测，通过填充（均值、中位数、众数、前向填充）或删除处理
- **Duplicates（重复值）**：`drop_duplicates(subset=[...], keep='first')`
- **Type Coercion（类型转换）**：确保数值列是数值类型、日期时间解析
- **Outlier Handling（异常值处理）**：裁剪到百分位数、z-score 过滤、**IQR (Interquartile Range，四分位距)** 方法

### Feature Engineering

| Technique | When to Use | Implementation |
|-----------|------------|----------------|
| **One-Hot Encoding（独热编码）** | 低基数分类 | `pd.get_dummies()` 或 `sklearn.OneHotEncoder` |
| **Target Encoding（目标编码）** | 高基数分类 | 每类别的目标均值（带平滑） |
| **Binning（分箱）** | 连续变量转分类 | `pd.cut()` 或 `pd.qcut()`（等频） |
| **Log Transform（对数变换）** | 右偏特征 | `np.log1p()`（处理零值） |
| **Interaction Features（交互特征）** | 特征组合 | `f1 * f2`，多项式特征 |
| **Time Features（时间特征）** | 日期时间列 | 提取 hour、day_of_week、is_weekend、time_since_event |

### Aggregation and Window Functions
GroupBy + 聚合是从交易数据进行特征工程的核心：

$$
\text{user\_avg\_spend} = \frac{1}{|T_u|} \sum_{t \in T_u} \text{amount}_t
$$

**Window Functions（窗口函数）**（rolling、expanding）用于时间序列特征。

### Efficient Processing
- **分块读取**：`pd.read_csv(..., chunksize=10000)` 处理大文件
- **向量化操作**：避免 `iterrows()`；使用向量化的 pandas/numpy
- **内存优化**：降低数据类型精度（`int64` -> `int32`），对字符串使用 category 类型

## Implementation

```python
import pandas as pd
import numpy as np

def build_user_features(transactions: pd.DataFrame) -> pd.DataFrame:
    # Aggregate transaction features per user.
    features = transactions.groupby("user_id").agg(
        total_spend=("amount", "sum"),
        avg_spend=("amount", "mean"),
        num_transactions=("amount", "count"),
        days_since_last=("date", lambda x: (pd.Timestamp.now() - x.max()).days),
        unique_merchants=("merchant_id", "nunique"),
    ).reset_index()
    return features

def handle_missing(df: pd.DataFrame,
                   numeric_strategy: str = "median") -> pd.DataFrame:
    # Impute missing values. Numeric: median/mean. Categorical: mode.
    df = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].isna().any():
            fill_val = df[col].median() if numeric_strategy == "median" else df[col].mean()
            df[col] = df[col].fillna(fill_val)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode()[0])
    return df

def create_time_features(df: pd.DataFrame,
                         date_col: str) -> pd.DataFrame:
    # Extract temporal features from a datetime column.
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    df["hour"] = dt.dt.hour
    df["day_of_week"] = dt.dt.dayofweek
    df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(int)
    df["month"] = dt.dt.month
    return df
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| GroupBy + agg | 用户/物品级特征 | 使用命名聚合使代码更清晰 |
| 窗口函数 | 滚动平均、累计和 | `df.rolling(7).mean()` 计算 7 天移动平均 |
| Merge/Join | 合并表 | 了解 left、inner、outer join；注意键重复 |
| Pivot / Melt | 数据重塑 | Pivot：长表变宽表；Melt：宽表变长表 |
| Apply + 向量化 | 自定义转换 | 优先使用向量化操作；`apply` 是最后手段 |

### Common Interview Questions
- [ ] 清洗混乱数据集（缺失值、重复、类型错误）
- [ ] 从交易日志构建聚合特征
- [ ] 为推荐系统实现特征工程管道
- [ ] 编写 SQL 计算用户留存指标
- [ ] 处理数据集中的类别不平衡（SMOTE、欠采样、类权重）
- [ ] 设计数据验证管道（schema 检查、分布漂移）

## Comparisons

| Aspect | Pandas | SQL | PySpark |
|--------|--------|-----|---------|
| 规模 | 单机（<10GB） | 取决于数据库 | 分布式（TB+） |
| 语法 | Python API | 声明式 | DataFrame API（类似 pandas） |
| 连接 | `merge()` | `JOIN` | `join()` 或 SQL |
| 窗口函数 | `rolling`、`expanding` | `OVER (PARTITION BY ... ORDER BY ...)` | 与 SQL 相同 |
| 最适合 | EDA、原型开发 | 生产查询 | 大规模 ETL |

## Key Takeaways
- [ ] 永远不要使用 `iterrows()` -- 用 pandas/numpy 向量化操作获得 100 倍以上的加速
- [ ] GroupBy + agg 是特征工程中最重要的 pandas 模式
- [ ] 始终显式处理缺失值 -- 记录你的填充策略
- [ ] 对偏斜特征做对数变换，建模前标准化
- [ ] 对于 MLE 面试：同时熟练掌握 pandas 和 SQL；预期在同一场面试中需要写两者
"""

TRANSLATIONS[62] = r"""# Sampling Algorithms

## Overview
**Sampling Algorithms（采样算法）** 对于处理大数据集、概率模型和 **Monte Carlo（蒙特卡洛）** 方法的 MLE 来说至关重要。面试题测试 **Reservoir Sampling（蓄水池采样，流处理）**、加权采样、**MCMC (Markov Chain Monte Carlo，马尔可夫链蒙特卡洛)** 基础以及从复杂分布生成样本的能力。这些技能直接应用于训练数据采样、A/B 测试分析和生成模型。

## Core Concepts

### Reservoir Sampling
从长度未知的流中均匀随机采样 $$k$$ 个元素：

对于第 $$i$$ 个元素（1-索引），以概率 $$k/i$$ 包含它。如果包含，替换蓄水池中的一个随机元素。

$$
P(\text{item } i \text{ in final sample}) = \frac{k}{n} \quad \forall i \in [1, n]
$$

每个元素最终被选中的概率相等。

**证明**：通过归纳法。元素 $$i$$ 被选中的概率为 $$k/i$$，在所有后续步骤中存活的概率为 $$\prod_{j=i+1}^{n} (1 - \frac{1}{j} \cdot \frac{k}{k}) = \frac{i}{n}$$。组合：$$\frac{k}{i} \cdot \frac{i}{n} = \frac{k}{n}$$。

### Weighted Random Sampling
从权重为 $$w_1, \ldots, w_n$$ 的离散分布中采样：
- **CDF Method（累积分布函数法）**：构建累积分布，对随机均匀数进行二分查找
- **Alias Method（别名法）**：$$O(n)$$ 预处理，$$O(1)$$ 每次采样

$$
P(\text{select } i) = \frac{w_i}{\sum_j w_j}
$$

### Rejection Sampling
**Rejection Sampling（拒绝采样）** 使用提议分布 $$q(x)$$ 从目标分布 $$p(x)$$ 采样，其中 $$Mq(x) \ge p(x)$$：
1. 从 $$q(x)$$ 采样 $$x$$
2. 以概率 $$\frac{p(x)}{Mq(x)}$$ 接受；否则拒绝并重复

效率：$$1/M$$ 的接受率。选择紧密的 $$M$$ 至关重要。

### Importance Sampling
**Importance Sampling（重要性采样）** 使用不同分布 $$q(x)$$ 的样本估计 $$E_{p}[f(x)]$$：

$$
E_{p}[f(x)] = E_{q}\left[\frac{p(x)}{q(x)} f(x)\right] \approx \frac{1}{n}\sum_{i=1}^{n} \frac{p(x_i)}{q(x_i)} f(x_i)
$$

应用于 **Off-policy RL（离策略强化学习）** 评估、罕见事件估计和粒子滤波器。

## Implementation

```python
import random
import bisect
import numpy as np

def reservoir_sample(stream, k: int) -> list:
    # Reservoir sampling: k items from stream of unknown length.
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir

def weighted_random_choice(values: list, weights: list[float]) -> object:
    # Weighted sampling using CDF + binary search. O(log n) per sample.
    cumulative = []
    total = 0.0
    for w in weights:
        total += w
        cumulative.append(total)
    r = random.uniform(0, total)
    return values[bisect.bisect_left(cumulative, r)]

def rejection_sample_circle(n: int) -> list[tuple[float, float]]:
    # Sample n points uniformly inside unit circle via rejection.
    points = []
    while len(points) < n:
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if x * x + y * y <= 1:
            points.append((x, y))
    return points
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 蓄水池采样 | 长度未知的流 | 以概率 $$k/i$$ 包含第 $$i$$ 个元素；替换随机槽位 |
| CDF + 二分查找 | 加权采样、少量样本 | 构建权重前缀和；`bisect_left` 实现 $$O(\log n)$$ |
| 别名法 | 加权采样、大量样本 | $$O(n)$$ 预处理，$$O(1)$$ 每次采样；适合重复采样 |
| 拒绝采样 | 复杂分布 | 以比率 $$p(x)/(Mq(x))$$ 接受/拒绝；效率 = $$1/M$$ |
| Fisher-Yates 洗牌 | 随机排列 | 将每个位置与随机的后续位置交换；$$O(n)$$ |

### Common Interview Questions
- [ ] 实现蓄水池采样并证明均匀性
- [ ] 加权分布中的随机数（CDF 方法）
- [ ] 均匀洗牌数组（Fisher-Yates）
- [ ] 从圆内均匀采样（拒绝采样）
- [ ] 带权重的随机选取（LC 528）
- [ ] 解释重要性采样及其失败场景（高方差）

## Comparisons

| Method | Preprocessing | Per-sample | Memory | Use Case |
|--------|--------------|-----------|--------|----------|
| CDF + bisect | $$O(n)$$ | $$O(\log n)$$ | $$O(n)$$ | 通用加权采样 |
| 别名法 | $$O(n)$$ | $$O(1)$$ | $$O(n)$$ | 固定分布的大量采样 |
| 拒绝采样 | 无 | $$O(1/\text{acceptance})$$ | $$O(1)$$ | 连续分布 |
| 蓄水池 | 无（流式） | $$O(1)$$ 每个元素 | $$O(k)$$ | 流处理 |
| MCMC | 预热期 | $$O(1)$$ | $$O(1)$$ | 高维分布 |

## Key Takeaways
- [ ] 蓄水池采样是流式均匀采样的首选 -- 需要掌握均匀性的证明
- [ ] 加权采样：CDF + 二分查找简单实用；别名法性能最优
- [ ] 拒绝采样：实现简单但如果提议分布与目标匹配差则效率低
- [ ] Fisher-Yates 洗牌：对每个 $$i$$ 将 `arr[i]` 与 `arr[randint(i, n-1)]` 交换 -- 产生均匀排列
- [ ] 对于 MLE：采样算法驱动 Mini-batch SGD（均匀）、Negative Sampling（Word2Vec）、Thompson Sampling（多臂老虎机）和 MCMC（贝叶斯推断）
"""

TRANSLATIONS[63] = r"""# Implement Neural Network Components

## Overview
从零实现神经网络组件展示了对深度学习框架底层工作原理的深刻理解。MLE 面试经常要求候选人仅使用 NumPy 实现常见层（线性层、softmax、batch norm、注意力）的前向和反向传播。这同时测试数学理解和编码能力 -- 这种组合是区分高级 MLE 的关键素质。

## Core Concepts

### Forward and Backward Pass
每一层实现：
- **Forward（前向传播）**：$$y = f(x; \theta)$$ -- 从输入计算输出
- **Backward（反向传播）**：给定 $$\frac{\partial L}{\partial y}$$，计算 $$\frac{\partial L}{\partial x}$$（用于链式法则）和 $$\frac{\partial L}{\partial \theta}$$（用于参数更新）

$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial x} \quad \text{(chain rule)}
$$

即链式法则。

### Linear Layer
前向：$$y = xW + b$$，其中 $$x \in \mathbb{R}^{n \times d_{in}}$$，$$W \in \mathbb{R}^{d_{in} \times d_{out}}$$

反向：
$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} W^T, \quad
\frac{\partial L}{\partial W} = x^T \frac{\partial L}{\partial y}, \quad
\frac{\partial L}{\partial b} = \sum_i \frac{\partial L}{\partial y_i}
$$

### Batch Normalization
**Batch Normalization（批归一化）** 归一化激活值：$$\hat{x} = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}$$，然后缩放和平移：$$y = \gamma \hat{x} + \beta$$

训练时：使用批统计量。推理时：使用运行平均值。

### Cross-Entropy Loss
对于 softmax 输出 $$\hat{y}$$ 和独热目标 $$y$$：

$$
L = -\sum_i y_i \log \hat{y}_i, \quad \frac{\partial L}{\partial z_i} = \hat{y}_i - y_i \quad \text{(combined softmax + CE gradient)}
$$

softmax 与交叉熵组合后的梯度简化为 $$\hat{y} - y$$。

### Attention Mechanism
**Scaled Dot-Product Attention（缩放点积注意力）**：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V
$$

## Implementation

```python
import numpy as np

class Linear:
    def __init__(self, d_in: int, d_out: int) -> None:
        self.W = np.random.randn(d_in, d_out) * np.sqrt(2.0 / d_in)
        self.b = np.zeros(d_out)

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.x = x  # cache for backward
        return x @ self.W + self.b

    def backward(self, grad_y: np.ndarray) -> np.ndarray:
        self.grad_W = self.x.T @ grad_y
        self.grad_b = grad_y.sum(axis=0)
        return grad_y @ self.W.T

def relu_forward(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def relu_backward(x: np.ndarray, grad_y: np.ndarray) -> np.ndarray:
    return grad_y * (x > 0)

def softmax_cross_entropy(logits: np.ndarray,
                          labels: np.ndarray) -> tuple[float, np.ndarray]:
    # Combined softmax + cross-entropy. labels: one-hot (n, C).
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    probs = exp_scores / exp_scores.sum(axis=1, keepdims=True)
    n = logits.shape[0]
    loss = -np.sum(labels * np.log(probs + 1e-12)) / n
    grad = (probs - labels) / n
    return loss, grad
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 前向 + 反向 | 任何层的实现 | 在前向传播中缓存输入，供反向传播使用 |
| 数值梯度检查 | 验证反向传播 | $$\frac{f(x+h) - f(x-h)}{2h}$$ 应与解析梯度匹配 |
| 组合 softmax + CE | 分类损失 | 梯度简化为 $$\hat{y} - y$$ |
| He 初始化 | ReLU 网络 | $$W \sim \mathcal{N}(0, 2/d_{in})$$ 防止梯度消失/爆炸 |
| Batch Norm 前向/反向 | 归一化激活 | 训练和推理模式需要跟踪运行均值/方差 |

### Common Interview Questions
- [ ] 实现线性层（前向 + 反向）
- [ ] 实现 softmax + 交叉熵损失（组合梯度）
- [ ] 实现 Batch Normalization（前向传播，训练 vs 推理）
- [ ] 实现 Dropout（训练 vs 推理行为）
- [ ] 实现缩放点积注意力
- [ ] 实现一个简单的两层 MLP 及训练循环
- [ ] 推导并实现卷积层的反向传播

## Comparisons

| Component | Forward Complexity | Backward Complexity | Key Pitfall |
|-----------|-------------------|-------------------|-------------|
| Linear | $$O(n \cdot d_{in} \cdot d_{out})$$ | 与前向相同 | 忘记缓存输入 |
| ReLU | $$O(n \cdot d)$$ | $$O(n \cdot d)$$ | $$x \le 0$$ 时梯度为 0（dying ReLU） |
| Softmax | $$O(n \cdot C)$$ | $$O(n \cdot C)$$ | 不减最大值会数值溢出 |
| Batch Norm | $$O(n \cdot d)$$ | $$O(n \cdot d)$$ | 训练和推理时行为不同 |
| Attention | $$O(n^2 \cdot d)$$ | $$O(n^2 \cdot d)$$ | 遗漏 $$\sqrt{d_k}$$ 缩放 |

## Key Takeaways
- [ ] 始终在前向传播中缓存输入/中间结果用于反向传播计算
- [ ] Softmax + 交叉熵的组合梯度是 $$\hat{y} - y$$ -- 比分开计算简单得多
- [ ] 数值梯度检查（$$\frac{f(x+h)-f(x-h)}{2h}$$）对于验证实现至关重要
- [ ] **He Initialization（He 初始化）**（$$\sqrt{2/d_{in}}$$）用于 ReLU，**Xavier Initialization（Xavier 初始化）**（$$\sqrt{1/d_{in}}$$）用于 tanh/sigmoid
- [ ] 对于 MLE 面试：能够从零实现任何标准层的前向和反向传播是高级候选人的强力区分点
"""


def main():
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "mle_prep.db")
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()

    # Update node 45 (new content)
    cur.execute("UPDATE framework_nodes SET description=? WHERE id=?",
                (NODE_45_CONTENT, 45))
    print(f"Node 45: WRITTEN new content ({len(NODE_45_CONTENT)} chars)")

    # Update all translated nodes
    for node_id, content in TRANSLATIONS.items():
        cur.execute("UPDATE framework_nodes SET description=? WHERE id=?",
                    (content, node_id))
        print(f"Node {node_id}: TRANSLATED ({len(content)} chars)")

    conn.commit()

    # Verification
    print("\n=== VERIFICATION ===")
    all_ok = True
    for node_id in range(44, 64):
        cur.execute("SELECT description FROM framework_nodes WHERE id=?", (node_id,))
        row = cur.fetchone()
        desc = row[0] if row else ""
        desc_len = len(desc)

        # Check Chinese chars
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', desc))

        # Check no formulas in code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', desc)
        formula_in_code = False
        for block in code_blocks:
            if '$$' in block:
                formula_in_code = True

        # Check minimum size
        min_size = 4000
        size_ok = desc_len >= min_size

        status = "OK" if (has_chinese and not formula_in_code and size_ok) else "FAIL"
        if status == "FAIL":
            all_ok = False
        issues = []
        if not has_chinese:
            issues.append("no Chinese")
        if formula_in_code:
            issues.append("formula in code block")
        if not size_ok:
            issues.append(f"too short ({desc_len} < {min_size})")

        issue_str = f" [{', '.join(issues)}]" if issues else ""
        print(f"Node {node_id}: {status} ({desc_len} chars){issue_str}")

    conn.close()
    print(f"\nOverall: {'ALL PASSED' if all_ok else 'SOME FAILED'}")


if __name__ == "__main__":
    main()
