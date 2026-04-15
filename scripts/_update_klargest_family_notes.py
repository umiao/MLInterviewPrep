"""One-shot: add Chinese notes for K-largest family (LC 703 + 973 + 378) and mark completed.

T-P0-435 deliverable.
"""
import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES_703 = r"""## LC 703 - Kth Largest Element in a Stream (Min-Heap)

> Easy. 核心: 维护大小为 k 的最小堆, 堆顶即第 k 大.

### 题目回顾
设计一个类, 初始化时给定整数流的初始数据和 k, 每次调用 `add(val)` 返回当前流中第 k 大的元素.

### 核心思路
- 维护一个大小恰好为 k 的 **min-heap**.
- 堆顶 = 堆中最小值 = 整个数据中第 k 大的值.
- `add(val)` 时: push val, 若堆大小 > k 则 pop 最小值, 堆顶即答案.

**直觉**: 堆里存的是"前 k 大"的元素. 最小堆的堆顶是这 k 个里最小的 = 第 k 大.

### 代码

```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap: list[int] = []
        for n in nums:
            self.add(n)

    def add(self, val: int) -> int:
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
```

### 复杂度
| 操作 | 时间 | 空间 |
|------|------|------|
| `__init__` | O(n log k) | O(k) |
| `add` | O(log k) | O(1) |

### 为什么用 min-heap 不用 max-heap?
- min-heap 大小 k: 堆顶 = 第 k 大, O(log k) 维护.
- max-heap: 每次要 pop k-1 个才能拿到第 k 大, 太慢.
- Python `heapq` 原生只有 min-heap, 直接用.

### 变体: 如果要第 k 小?
- 用 **max-heap** 大小 k (Python 取负存入 min-heap).
- 堆顶 (取负后) = 第 k 小.

### 45 秒口播脚本
> "LC 703 用大小为 k 的 min-heap. 堆里存当前最大的 k 个元素, 堆顶就是第 k 大. add 时 push 进去, 超过 k 就 pop 掉最小的, 返回堆顶. 初始化 O(n log k), 每次 add O(log k), 空间 O(k). 这是 top-K 流式问题的基础模板."
"""

NOTES_973 = r"""## LC 973 - K Closest Points to Origin (Heap / Quickselect)

> Medium. 核心: top-K 问题双解 -- max-heap O(n log k) vs quickselect 平均 O(n).

### 题目回顾
给定平面上 n 个点 `points[i] = [xi, yi]`, 返回离原点最近的 k 个点 (任意顺序).

### 方法一: Max-Heap (大小 k)

**思路**: 维护大小为 k 的 max-heap (距离最大的在堆顶). 遍历每个点, push 进堆; 若堆大小 > k, pop 掉最远的. 最终堆中剩 k 个最近的.

```python
import heapq

def kClosest(points: list[list[int]], k: int) -> list[list[int]]:
    heap: list[tuple[int, list[int]]] = []
    for p in points:
        dist = p[0] ** 2 + p[1] ** 2
        heapq.heappush(heap, (-dist, p))  # 取负 -> min-heap 模拟 max-heap
        if len(heap) > k:
            heapq.heappop(heap)
    return [p for _, p in heap]
```

**复杂度**: 时间 O(n log k), 空间 O(k).

### 方法二: Quickselect (最优平均)

**思路**: 类似快排 partition, 选 pivot 把数组分成 "距离 <= pivot" 和 "距离 > pivot" 两半. 递归只进入包含第 k 个位置的那一半.

```python
import random

def kClosest(points: list[list[int]], k: int) -> list[list[int]]:
    def dist(p: list[int]) -> int:
        return p[0] ** 2 + p[1] ** 2

    def partition(lo: int, hi: int, pivot_idx: int) -> int:
        pivot_d = dist(points[pivot_idx])
        points[pivot_idx], points[hi] = points[hi], points[pivot_idx]
        store = lo
        for i in range(lo, hi):
            if dist(points[i]) < pivot_d:
                points[store], points[i] = points[i], points[store]
                store += 1
        points[store], points[hi] = points[hi], points[store]
        return store

    lo, hi = 0, len(points) - 1
    while lo < hi:
        pivot_idx = random.randint(lo, hi)
        pos = partition(lo, hi, pivot_idx)
        if pos == k:
            break
        elif pos < k:
            lo = pos + 1
        else:
            hi = pos - 1
    return points[:k]
```

**复杂度**: 时间平均 O(n), 最坏 O(n^2) (随机化 pivot 大概率避免). 空间 O(1) in-place.

### 方法对比

| 维度 | Max-Heap | Quickselect |
|------|----------|-------------|
| 时间 (平均) | O(n log k) | O(n) |
| 时间 (最坏) | O(n log k) | O(n^2) |
| 空间 | O(k) | O(1) in-place |
| 稳定性 | 确定性 | 随机化, 最坏可能慢 |
| 流式支持 | 可以 (逐个 add) | 不行 (需要全部数据) |
| 面试推荐 | 首选 (安全, 好写) | 追问"能否 O(n)"时给出 |

### 面试追问: 为什么不直接排序?
- 排序 O(n log n), heap 是 O(n log k), 当 k << n 时 heap 更优.
- Quickselect 平均 O(n) 更快, 但代码更长且有最坏情况.

### 45 秒口播脚本
> "973 是经典 top-K 问题. 首选 max-heap 大小 k: 遍历所有点, 堆顶是当前第 k 近的点, 超过 k 就 pop, O(n log k). 追问 O(n) 时用 quickselect: 随机 pivot partition, 只递归包含第 k 位置的那半边, 平均线性但最坏平方. 面试中 heap 解法更安全, quickselect 作为加分项."
"""

NOTES_378 = r"""## LC 378 - Kth Smallest Element in a Sorted Matrix (二分搜索 on Value)

> Medium. 核心: 在值域上二分, 用矩阵有序性 O(m+n) 计数.

### 题目回顾
给定 n x n 矩阵, 每行每列均升序排列, 找第 k 小的元素.

### 核心思路: 值域二分

矩阵元素范围 [matrix[0][0], matrix[-1][-1]]. 对 mid 值:
- 数矩阵中 <= mid 的元素个数 `count`.
- `count < k` -> 答案在右半 (lo = mid + 1).
- `count >= k` -> 答案在左半 (hi = mid).

**计数技巧**: 从左下角 (row=n-1, col=0) 出发:
- `matrix[row][col] <= mid` -> 该列 row+1 个元素都 <= mid, col++.
- `matrix[row][col] > mid` -> row--.
- 每步 row-- 或 col++, 总步数 O(n+n) = O(n).

### 代码

```python
def kthSmallest(matrix: list[list[int]], k: int) -> int:
    n = len(matrix)

    def count_leq(mid: int) -> int:
        row, col, cnt = n - 1, 0, 0
        while row >= 0 and col < n:
            if matrix[row][col] <= mid:
                cnt += row + 1
                col += 1
            else:
                row -= 1
        return cnt

    lo, hi = matrix[0][0], matrix[n - 1][n - 1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_leq(mid) < k:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

### 为什么二分结果一定是矩阵中的元素?

二分收敛时 `lo == hi`. 假设 lo 不在矩阵中:
- 那 count_leq(lo) == count_leq(lo-1), 即 lo 和 lo-1 的计数相同.
- 但二分保证 count_leq(lo) >= k 且 count_leq(lo-1) < k.
- 矛盾. 所以 lo 一定在矩阵中.

### 复杂度

| 维度 | 值 |
|------|------|
| 时间 | O(n * log(max - min)), 二分 log(值域) 次, 每次计数 O(n) |
| 空间 | O(1) |

### 与 LC 410 (Split Array Largest Sum) 的联系

两题都是 **"值域二分 + 可行性判定"** 模式:
- LC 378: 二分答案值, 判定 count_leq(mid) vs k.
- LC 410: 二分最大子数组和, 判定能否分成 <= m 组.
- 共同点: 答案空间上二分, 每次 O(n) 验证.

### 其他解法 (了解)

| 解法 | 时间 | 空间 | 特点 |
|------|------|------|------|
| Min-heap (BFS) | O(k log n) | O(n) | 从 (0,0) 出发 BFS 扩展, k 小时快 |
| 值域二分 | O(n log(max-min)) | O(1) | k 任意大小都稳定 |
| 排序 | O(n^2 log n) | O(n^2) | 暴力, 不推荐 |

面试首选值域二分 (代码简洁, 复杂度最优). k 很小时 heap 也可以提.

### 45 秒口播脚本
> "LC 378 的关键: 值域二分. 在 matrix[0][0] 到 matrix[-1][-1] 之间二分 mid, 从左下角走阶梯数 <= mid 的元素个数, O(n) 一次. count < k 收左界, 否则收右界. 总时间 O(n log(max-min)), 空间 O(1). 和 LC 410 同属值域二分家族 -- 答案空间上二分, 每步 O(n) 验证."
"""

NOTES_COMPARISON = r"""## K-largest 家族总结: Heap vs Quickselect vs Bucket Sort

### 三种方法对比

| 维度 | Heap (Min/Max) | Quickselect | Bucket Sort |
|------|---------------|-------------|-------------|
| 时间 (平均) | O(n log k) | O(n) | O(n + range) |
| 时间 (最坏) | O(n log k) | O(n^2) | O(n + range) |
| 空间 | O(k) | O(1) in-place | O(range) |
| 流式数据 | 可以 | 不行 | 看情况 |
| 适用场景 | 通用 top-K | 一次性全量 | 值域有限 (计数排序) |
| 确定性 | 确定性 | 随机化 | 确定性 |
| 代码复杂度 | 低 (heapq) | 中 (partition) | 低 (但需值域) |

### 选择决策树

1. **流式数据** (元素逐个到达, 如 LC 703) -> **Min-Heap 大小 k**.
2. **一次性全量, k << n, 需要精确 top-K** -> **Quickselect** (平均 O(n)).
3. **值域有限** (如频率 0-100) -> **Bucket sort** (O(n) 确定性).
4. **面试默认** -> **Heap**, 追问优化再给 quickselect.

### Heap 模板: top-K 最大用 min-heap, top-K 最小用 max-heap

这是最容易搞混的点:
- 找第 k **大**: min-heap 大小 k, 堆顶 = 第 k 大 (最小的那个留在顶, 太小的被淘汰).
- 找第 k **小**: max-heap 大小 k, 堆顶 = 第 k 小 (最大的那个留在顶, 太大的被淘汰).
- Python 只有 min-heap, 模拟 max-heap 取负.

### Quickselect 核心: Lomuto Partition

```python
# 经典 partition: 选 pivot, 小的放左, 大的放右
# 返回 pivot 最终位置
def partition(arr, lo, hi):
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    return i
```

递归只进入 pivot 位置与 k 的比较方向, 期望 T(n) = T(n/2) + O(n) = O(n).

### 面试串联: 为什么 Pinterest 实时 top-K 用 sketch 不用 heap?

当数据量到达数十亿 QPS 级别, 精确 heap 不可行:
- 单机 heap 大小 k 没问题, 但需要对每个 item 计数 -> 计数本身是瓶颈.
- Count-Min Sketch 估计频率 (overestimate-only) + min-heap 维护 top-K.
- 近似但 O(1) 每次更新, 空间 O(1/epsilon * log(1/delta)).
"""


def main() -> None:
    """Update LC 703, 973, 378 notes and mark as completed."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updates = [
        (703, NOTES_703 + "\n\n" + NOTES_COMPARISON),
        (973, NOTES_973),
        (378, NOTES_378),
    ]

    for lc_id, notes in updates:
        c.execute("SELECT id FROM problems WHERE leetcode_id = ?", (lc_id,))
        row = c.fetchone()
        if not row:
            print(f"[ERR] LC {lc_id} not found in DB")
            continue
        pid = row[0]
        c.execute(
            "UPDATE problems SET notes = ?, is_completed = 1 WHERE id = ?",
            (notes, pid),
        )
        c.execute(
            "SELECT id, leetcode_id, title, is_completed, length(notes) "
            "FROM problems WHERE id = ?",
            (pid,),
        )
        v = c.fetchone()
        print(
            f"[OK] LC {v[1]} '{v[2]}' (id={v[0]}) updated. "
            f"is_completed={v[3]}, notes_len={v[4]}"
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
