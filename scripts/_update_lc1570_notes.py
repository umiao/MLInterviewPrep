"""Idempotent: mark LC 1570 complete and attach Chinese solution notes.

LC 1570 is the 1-D follow-up to LC 311 Sparse Matrix Multiplication; the
existing LC 311 notes already reference 1570 in their 进阶追问 section,
so linking becomes bidirectional once these notes are in place.

Run: python scripts/_update_lc1570_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 1570
FAMILY = "sparse_representation"
PATTERN = "hash map"

NOTES = """## 题目定位
**LC 311 (二维稀疏矩阵乘) 的 1-D 版本**。给两个可能很长、但大部分为 0 的一维向量，求点积。
考点是"选什么稀疏表示"以及为什么通用的 dense 数组会在 nnz 很小时显著浪费 $O(n)$ 时空。

## 解法 A: Hash Map（我的提交思路）
**数据结构**：`defaultdict(int)`，只存非零位置 `index -> value`。
**点积**：遍历 `self` 的非零项，查 `other` 的 hashmap 是否有同 index；有就累乘累加。

**复杂度**：
- 预处理：$O(n)$ 扫描一次原数组。
- 点积：平均 $O(\\min(k_1, k_2))$，其中 $k$ 是 nnz 数；最坏 $O(k_1)$（hash 冲突退化到 $O(k_2)$ 查找，但 Python dict 几乎不会触发）。
- 空间：$O(k)$ 每个向量。

**优化点（面试易追问）**：点积时**主动选 nnz 更少的那一侧来遍历**，可保证 $O(\\min(k_1, k_2))$：
```python
if len(self.compactData) > len(vec.compactData):
    self, vec = vec, self
for key, val in self.compactData.items():
    if key in vec.compactData:
        ret += val * vec.compactData[key]
```

## 解法 B: 有序对列表 + 双指针
**数据结构**：`list[(index, value)]`，按 index 升序插入。
**点积**：两指针同向扫，index 相等则累乘前进两边，否则前进较小的一侧。

**复杂度**：预处理 $O(n)$（直接按原顺序 append，天然有序）；点积 $O(k_1 + k_2)$ 确定性，无 hash 开销。

**vs 方案 A 的权衡**：
| 维度 | Hash Map | 有序对 + 双指针 |
| --- | --- | --- |
| 插入顺序要求 | 无 | 必须升序（工业上数据常天然升序） |
| 点积常数因子 | hash 摊还 O(1)，有 overhead | cache-friendly，常数极小 |
| 最坏情况 | $O(k_1)$ 期望 | $O(k_1 + k_2)$ 确定 |
| 代码量 | 更短 | 稍长（双指针） |

**面试策略**：先给 hashmap 答案，被追问"在数据天然有序或追求稳定延迟时有没有更好做法"再给双指针版——体现"能按约束换方案"的判断力。

## 解法 C: 稠密数组
当向量**稠密度 > ~5-10%**，直接用原始 dense 数组 `sum(a * b for a, b in zip(nums1, nums2))` 反而最快：避开任何数据结构 overhead，SIMD / cache prefetch 都友好。判密标准在面试里可以说"sparse structure 的切换点是 nnz/n 在 5-10% 左右，具体看硬件和 n 的绝对值"。

## 易错点
1. **不要把 value=0 也塞进 map**：defaultdict 访问不存在键时会**创建 0 条目**，污染迭代集。我的实现里写成 `if val != 0: self.compactData[i] = val`，避免了这个坑。
2. **`__init__` 末尾的 `return`**：Python 可省，写了不报错；面试可以留也可以删，不影响得分。
3. **双向一致性**：`self.dotProduct(vec) == vec.dotProduct(self)` 必须恒成立——点积交换律。方案 A 因为只遍历 `self` 的 keys，结果不依赖于谁是 self（交集操作对称），所以自然满足。

## Follow-up: LC 311 Sparse Matrix Multiplication
LC 311 是这题的 **2-D 扩展**：把向量升级为矩阵，点积升级为矩阵乘法。
- **相同处**：稀疏表示原则不变——CSR（compressed sparse row）= 一行一个 hashmap 或有序对列表。
- **不同处**：matmul 需要 $A$ 的每行点积 $B$ 的每列；朴素 $O(m \\cdot p \\cdot n)$；稀疏版 $O(\\sum_i k_{A,i} \\cdot \\text{avg-nnz-per-column-of-}B)$。
- **思路迁移**：这题练的是"稀疏一维数据结构的选择"，LC 311 练的是"怎么把稀疏结构跨维度组合"。学完本题应能一句话说出：**nnz 小就存 index→value 的 map，两边都稀疏就取 keys 交集累乘**。

## 一句话 pitch (面试)
> 只存非零项的 hashmap，点积时遍历其中一侧并查另一侧。优化是主动遍历 nnz 更小的那边保证 $O(\\min(k_1, k_2))$。如果数据天然按 index 升序，可以换有序对 + 双指针拿更稳的延迟和更好的 cache 表现。
"""


def main() -> None:
    """Attach notes and mark LC 1570 as completed; idempotent."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, done, fam, pat = row

        fields: dict[str, str | int] = {"is_completed": 1}
        if not existing_notes:
            fields["notes"] = NOTES
        if not fam:
            fields["family"] = FAMILY
        if not pat:
            fields["pattern"] = PATTERN

        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(f"[UPDATED] LC {LC_ID} id={pid} fields={list(fields)}")


if __name__ == "__main__":
    main()
