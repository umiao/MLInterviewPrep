"""Idempotent: write LC 855 notes (Exam Room) — brute-force O(P) per seat()
on a sorted-list-of-occupied-positions, with the optimal heap-of-intervals
solution as labeled follow-up.

User explicitly noted "目前这里只讨论了暴力的解法" — keep brute force as the
primary solution; the O(log P) heap version is documented as a follow-up
that demonstrates the data-structure upgrade but is not required.

Run: python scripts/_update_lc855_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 855
PATTERN = "sorted_insertion_simulation"
FAMILY = "stateful_ds_design"
SENTINEL = "<!-- LC855_NOTES_V1 -->"

NOTES = """<!-- LC855_NOTES_V1 -->
## 题目定位
LC 855 Exam Room —— **设计题 / 区间最大化模拟**。$N$ 个连续座位
$0 \\dots N-1$，`seat()` 把一名学生放到**距离最近同学最远**的座位
（多解时取**编号最小**的），`leave(p)` 从位置 $p$ 移除一名学生。

**关键洞察**：用一个**已排序的占用位置列表** `students`，每次 `seat()`
扫描相邻对计算"中点距离"，再单独判左边 (0) 和右边 ($N-1$) 这两个端点。
单次操作 $O(P)$（$P$ = 当前学生数），简洁、好写、面试时一遍过。

## 思路（暴力 / 简洁版）
3 类候选位置：
1. **最左端 0**（如果没人在那里）：到最近学生的距离 = `students[0]`。
2. **每对相邻学生 (prev, s) 之间**：最优插入点是 `prev + (s-prev)//2`（中点
   靠左，因为题目要"小编号优先"），距离 = `(s-prev)//2`。
3. **最右端 N-1**（如果没人在那里）：距离 = `N-1 - students[-1]`。

从左到右扫，**用严格 `>` 更新最优**——这样自动保证"多解取最小编号"。

## 核心代码（user 提供，源自 LC 官方 editorial）
```python
import bisect

class ExamRoom:
    def __init__(self, N: int):
        self.N = N
        self.students = []

    def seat(self) -> int:
        if not self.students:
            student = 0
        else:
            # 左端候选：position 0, 到最近学生的距离 = students[0]
            dist, student = self.students[0], 0

            # 相邻对的中点候选
            for i, s in enumerate(self.students):
                if i:
                    prev = self.students[i - 1]
                    d = (s - prev) // 2          # 注意 Python 3 用 //
                    if d > dist:                 # 严格 > 保证 small-id 优先
                        dist, student = d, prev + d

            # 右端候选：position N-1
            d = self.N - 1 - self.students[-1]
            if d > dist:
                student = self.N - 1

        bisect.insort(self.students, student)    # 排序插入, O(P)
        return student

    def leave(self, p: int) -> None:
        self.students.remove(p)                  # 线性查找+移除, O(P)
```

### 走查（N = 10）
| 操作 | students 状态 | 返回 / 备注 |
| --- | --- | --- |
| `seat()` | `[]` → `[0]` | 0（空房间默认坐 0） |
| `seat()` | `[0]` → `[0, 9]` | 9（右端到 0 距离 9 > 任何中点） |
| `seat()` | `[0, 9]` → `[0, 4, 9]` | 4（中点 `(9-0)//2 = 4`，小编号优先） |
| `seat()` | `[0, 4, 9]` → `[0, 2, 4, 9]` | 2（左半段中点 `(4-0)//2 = 2`，胜过右半段中点 `(9-4)//2 = 2` 的 6 因 `>` 严格） |
| `leave(4)` | `[0, 2, 4, 9]` → `[0, 2, 9]` | — |
| `seat()` | `[0, 2, 9]` → `[0, 2, 5, 9]` | 5（`(9-2)//2 = 3` 在 5 处取得；左端 0 已占，左间距 `(2-0)//2 = 1` 不如它） |

## 关键技巧 / 易错点

### [PITFALL] 1. Python 3 必须用 `//`，不能 `/`
LC 官方 editorial 是 Python 2 写的，原文是 `(s - prev) / 2`。**Python 3 里
`/` 返回 float**，会污染 `student = prev + d` 让位置变成浮点；下一次
`bisect.insort` 虽然能比也能插，但会**让 `students` 列表里同时存在 int 和
float**，`leave(p)` 时 `students.remove(p)` 用 `==` 找元素——`4 == 4.0`
为 True 在 Python 里成立，但读 logs / 调试体验糟糕。**统一 `//` 最保险**。

### 其它易错点
2. **左端候选的初始 dist 不要写成 `dist = 0`**：那样任何相邻对的 `d > 0`
   都会覆盖左端，错过"左端永远是有效候选"的语义。`dist = students[0]` 是
   "坐在 0 时的实际最近距离"，本身就是合法的最优候选起点。
3. **右端 `>` 改成 `>=` 会破坏 small-id 优先**：题目明确要求多解取最小编号，
   右端用严格 `>` 才不会抢中点候选的编号位。
4. **`leave(p)` 用 `students.remove(p)` 是 $O(P)$**：先线性扫描找 p 再删除。
   如果 p 来自 `seat()` 的返回值，可以维护一个 `position → index` map 把
   leave 改成 $O(\\log P)$ 二分查找，但**LC 855 数据规模 $N, \\text{ops} \\le 10^4$
   暴力即可**。
5. **N=1 边界**：第一次 `seat()` 返回 0，第二次 `seat()` 不会被调用（题目
   保证不会让 seat() overflow）。代码无需特判。
6. **空房间 `seat()`**：`if not self.students: student = 0`——不要漏这个分支
   直接进 for 循环，`students[0]` 会 IndexError。
7. **`prev + d` 是 "中点靠左"，不是 "中点四舍五入"**：`//` 是地板除，正好
   实现 small-id 优先；用 `round()` 或 `(prev + s) // 2` 都行，但要保证向
   下取整。`prev + (s - prev) // 2` 与 `(prev + s) // 2` 在 prev、s 同奇偶
   性时一致；prev=0, s=3 时前者 `0 + 1 = 1`、后者 `3 // 2 = 1`——一致。

## 复杂度
- `seat()`: $O(P)$ 扫相邻对 + $O(P)$ `bisect.insort` 移动元素 = $O(P)$。
- `leave()`: $O(P)$ 线性查找 + $O(P)$ 移动元素 = $O(P)$。
- 空间：$O(P)$ 存当前学生列表。

## Follow-up: O(log P) 堆 + 区间懒删除
> 题目最优解是把"空闲区间"做成一个**最大堆**，按区间产生的"中点距离"排序；
> 同时维护两个 `dict` 把每个区间端点映射到它所属的区间对象，配合**懒删除**
> 处理 `leave(p)` 把两个邻接区间合并。

```python
import heapq

class ExamRoom:
    def __init__(self, N: int):
        self.N = N
        self.heap = []                    # max-heap (push -priority)
        self.left = {}                    # left endpoint -> Interval
        self.right = {}                   # right endpoint -> Interval
        self._add(Interval(-1, N))         # 哨兵区间, 端点 -1 和 N

    def _add(self, itv): ...   # 同时入堆 + 双 map
    def _del(self, itv): ...   # 双 map 删, 堆里留垃圾(懒删除)

    def seat(self) -> int:
        while self.heap and self.heap[0].invalid: heapq.heappop(self.heap)
        itv = heapq.heappop(self.heap)
        # ... 把 itv 拆成左右两个新区间 ...

    def leave(self, p: int) -> None:
        # 左区间右端 p, 右区间左端 p, 合并成一个新区间
        ...
```

**优点**：`seat()` $O(\\log P)$、`leave()` $O(\\log P)$。**代价**：代码量翻
3 倍，懒删除 + 双 map + 哨兵区间这些细节面试 30 分钟很难一次写对。**LC 855
的暴力解法在数据规模下完全够用**，面试时**先给暴力**再口头说"如果 N 很大、
ops 很多，可以升级到堆 + 区间双 map + 懒删除"是更稳的 narrative。

## 题目家族（stateful_ds_design / 维护排序集合的设计题）
- **LC 1845** Seat Reservation Manager：本题的简化版——只问"最小可用编号"。
  用最小堆即可，无需算"最近距离最远"。
- **LC 1146** Snapshot Array：另一个 stateful ds_design 家族成员，技巧不同
  （binary search on history）但同属"维护一个会被多次 query/update 的状态"的设计题型。
- **LC 729 / 731 / 732** My Calendar I/II/III：维护一组区间 + 答询有无冲突，
  与 LC 855 共享"区间操作 + 排序结构"的代码骨架。
- **LC 295** Find Median from Data Stream：双堆设计的入门题。
- **LC 480** Sliding Window Median：上面的 hard 版，对**懒删除**这个套路
  做了实战考察——刚好是 LC 855 follow-up 提到的同款技巧。

**面试 30 秒 pitch**：
> "维护一个有序的占用列表 students。`seat()` 时考虑 3 类候选：左端 0、
> 每对相邻学生的中点 `prev + (s-prev)//2`、右端 N-1，从左到右用严格 `>`
> 取最大距离即可自动保证小编号优先。`leave(p)` 直接 `list.remove`。
> 单次 $O(P)$。如果要求 $O(\\log P)$，把空闲区间做成最大堆 + 双端点
> 字典 + 懒删除。"
"""


def main() -> None:
    """Rewrite LC 855 notes; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} notes (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN
        if not fam:
            fields["family"] = FAMILY
        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} "
            f"notes_len={len(NOTES)} fields={list(fields)}"
        )


if __name__ == "__main__":
    main()
