"""One-shot: extend LC 215 notes with Hoare two-pointer quickselect variant + 3-way partition.

Triggered by 2026-05-07 ad-hoc Discord request (msg 1502026871603466390):
"quickselect 部分多实现一个 while 循环的, 效率更高, 直接跳过不需要考虑的双端指针对应的节点".

Approach: idempotent UPSERT of the full notes string keyed on leetcode_id=215.
Re-running yields a deterministic result. Existing Lomuto + Min Heap solutions
are preserved; a new "Hoare double-end pointer partition" section is inserted
between them, plus a brief 3-way (Dutch flag) follow-up.
"""
from __future__ import annotations

import sqlite3

DB_PATH = "data/mle_prep.db"

NOTES_215 = r"""# 215. Kth Largest Element in an Array 题解

## 题目概述

给定一个未排序的整数数组 `nums` 和一个整数 `k`, 返回数组中第 `k` 大的元素.

---

## 解法一: Quick Select (Lomuto Partition)

核心思想: 利用 **Quick Sort** 的 partition 过程, 每次只递归一半, 平均 O(n).

**关键点:**
- Partition 后, pivot 在其最终位置 `p`.
- 如果 `p == n - k`, 找到答案.
- 如果 `p < n - k`, 在右半部分继续.
- 如果 `p > n - k`, 在左半部分继续.

```python
import random

def findKthLargest(nums, k):
    def partition(left, right):
        # 随机选 pivot 避免最坏情况
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot, store = nums[right], left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]
        return store

    target = len(nums) - k
    left, right = 0, len(nums) - 1
    while left <= right:
        p = partition(left, right)
        if p == target:
            return nums[p]
        elif p < target:
            left = p + 1
        else:
            right = p - 1
```

---

## 解法一-优化: Quick Select (Hoare 双端指针 Partition)

**动机**: Lomuto 是单指针扫描, 每个 `< pivot` 的元素都触发一次 swap (即使本来就在左侧). Hoare 用 **双端指针 + 内层 while 跳过已就位元素**, 只 swap 错位对, 平均 swap 次数减半, cache 命中率更高. 对已部分有序的输入收益尤其明显.

**核心思想**:
- `i` 从左向右扫, **内层 while 跳过** 所有 `nums[i] < pivot` 的元素 (它们已经在正确侧, 不需要考虑).
- `j` 从右向左扫, **内层 while 跳过** 所有 `nums[j] > pivot` 的元素 (同理).
- 两端都"卡住"时, `nums[i] >= pivot` 且 `nums[j] <= pivot` 是一对错位元素, swap.
- 直到 `i >= j` 收敛, 返回分界点 `j`.

```python
import random

def findKthLargest(nums, k):
    target = len(nums) - k  # 第 k 大 = 排序后第 (n-k) 个 (0-indexed)

    def partition(lo, hi):
        # 随机化 pivot 值 (注意是值, 不是 index, 因为 i/j 会移动)
        pivot = nums[random.randint(lo, hi)]
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while nums[i] < pivot:   # 跳过左侧已就位的
                i += 1
            j -= 1
            while nums[j] > pivot:   # 跳过右侧已就位的
                j -= 1
            if i >= j:
                return j   # Hoare 返回分界点 j, 不是 pivot 最终位置
            nums[i], nums[j] = nums[j], nums[i]

    lo, hi = 0, len(nums) - 1
    while lo < hi:
        p = partition(lo, hi)
        if p < target:
            lo = p + 1
        else:
            hi = p   # 注意: hi = p, 不是 p - 1
    return nums[target]
```

**Lomuto vs Hoare 对比**:

| 维度 | Lomuto (单指针) | Hoare (双端指针) |
|------|----------------|-----------------|
| 实现 | 一个 for-loop | 三层 while (外层 + 两个内层 skip) |
| Swap 次数 | 多 (每个 `< pivot` 都 swap) | 少 (只 swap 错位对) |
| 已部分有序输入 | 可能退化 | 表现更好 |
| 返回值语义 | pivot 最终位置 | 分界点 j: `nums[lo..j] <= pivot`, `nums[j+1..hi] >= pivot` |
| 外层边界 | `while lo <= hi`, `hi = p - 1` | `while lo < hi`, `hi = p` |
| 命中检查 | `if p == target: return` | 不检查, 收敛后 `nums[target]` |

**两个常见坑**:
1. **不能用 `nums[lo]` 或 `nums[hi]` 做 pivot** -- 会死循环 (内层 while 跳不出来). 必须取中间或随机.
2. **外层用 `hi = p` 不是 `p - 1`** -- Hoare 返回的 j 不一定等于 pivot 位置, target 可能就在 j 上, 减 1 会丢解.

---

## 解法一-加强: 3-way Partition (Dutch National Flag)

**动机**: 当数组有大量重复值 (如 follow-up "数组里只有 0 和 1") 时, Hoare 仍会反复 swap 等于 pivot 的元素. 3-way 把元素分成 `< pivot` / `== pivot` / `> pivot` 三段, **等于段直接命中即可返回**, 递归只进入两端一段.

```python
import random

def findKthLargest(nums, k):
    target = len(nums) - k
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        pivot = nums[random.randint(lo, hi)]
        lt, gt, i = lo, hi, lo
        while i <= gt:
            if nums[i] < pivot:
                nums[lt], nums[i] = nums[i], nums[lt]
                lt += 1
                i += 1
            elif nums[i] > pivot:
                nums[gt], nums[i] = nums[i], nums[gt]
                gt -= 1
            else:
                i += 1
        # 此时: nums[lo..lt-1] < pivot, nums[lt..gt] == pivot, nums[gt+1..hi] > pivot
        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            return nums[target]   # 命中等于段
    return nums[lo]
```

**何时选 3-way**: 数组中 distinct 值远小于 n 时 (如全是 0/1, 或值域很小). 否则 Hoare 已经够用, 3-way 多一层分支判断反而稍慢.

---

## 解法二: Min Heap (简单稳定)

维护大小为 k 的 **最小堆**, 堆顶即为第 k 大.

```python
import heapq

def findKthLargest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]
```

---

## 复杂度对比

| 解法 | 时间 (平均) | 时间 (最坏) | 空间 | 备注 |
|------|------------|------------|------|------|
| Quick Select (Lomuto) | O(n) | O(n^2) | O(1) | 写法简单, swap 次数多 |
| Quick Select (Hoare) | O(n) | O(n^2) | O(1) | swap 减半, 部分有序输入更优 |
| Quick Select (3-way) | O(n) | O(n^2) | O(1) | 重复值多时近似 O(n) 稳定 |
| Min Heap | O(n log k) | O(n log k) | O(k) | 流式数据首选 |
| 排序 | O(n log n) | O(n log n) | O(1) | 暴力, 不推荐 |

## 面试注意事项

1. **Quick Select 必须随机化 pivot** -- 否则已排序数组退化为 O(n^2).
2. **Hoare 是"更优 partition"的标准答案** -- 面试官追问"还能更快吗 / swap 能不能少"时给出.
3. **Follow-up: 大量重复值** -> 3-way partition (Dutch flag), 等于段直接命中.
4. **Follow-up: 数据流?** -> Min Heap, Quick Select 需要全部数据.
5. **Follow-up: k 很小?** -> Heap O(n log k) 反而更优.
6. **Follow-up: 稳定的最坏 O(n)?** -> Median of Medians, 常数因子大, 提一句即可.
"""


def main() -> None:
    """Idempotent UPSERT of LC 215 notes (Lomuto + Hoare + 3-way + Min Heap)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM problems WHERE leetcode_id = ?", (215,))
        row = c.fetchone()
        if not row:
            print("[ERR] LC 215 not found in DB")
            return
        pid = row[0]
        c.execute(
            "UPDATE problems SET notes = ?, is_completed = 1 WHERE id = ?",
            (NOTES_215, pid),
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
    finally:
        conn.close()


if __name__ == "__main__":
    main()
