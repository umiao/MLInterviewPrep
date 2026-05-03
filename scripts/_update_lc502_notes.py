"""Idempotent: seed LC 502 IPO notes.

LC 502 是 "sort + max-heap 贪心" 家族的 canonical 题目 ——
项目选择问题, 每轮挑当前资金可承担的最大利润项目.

Run: python scripts/_update_lc502_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 502
PATTERN = "sort_heap_greedy"
FAMILY = "heap_greedy"
SENTINEL = "<!-- LC502_NOTES_V1 -->"

NOTES = """<!-- LC502_NOTES_V1 -->
## 题目定位
LC 502 IPO —— **"sort + max-heap" 贪心**家族的 canonical 题目。给定初始
资本 $w$、最多做 $k$ 个项目，每个项目有启动门槛 `capital[i]` 和完成利润
`profits[i]`。每轮**只能挑选 `capital[i] <= w` 的项目**，做完后 $w \\mathrel{+}=
\\text{profit}$。求 $k$ 轮后最大化 $w$。

**关键洞察**：每轮做完项目后 $w$ **单调不减**（题目保证 $\\text{profits}[i]
\\ge 0$），所以"曾经可承担"的项目永远还可承担——可承担集合**只增不减**。
所以维护一个 max-heap，每轮把新解锁的项目 push 进来、pop 出当前最大
profit 即可。

## 思路
1. **按 capital 升序排序**所有项目。
2. **指针 `unblockedPtr`** 从前往后扫，把所有 `capital[i] <= w` 的 profit
   推进 max-heap。
3. **每轮**：pop 堆顶（当前最大可承担 profit），$w \\mathrel{+}= \\text{profit}$，
   $k \\mathrel{-}= 1$，再前进指针把新解锁的项目入堆。
4. **终止**：$k == 0$，或者堆空 + 指针到底（剩下的全做不起）。

**为什么贪心正确**：exchange argument。若某最优解某一步没取当前最大可行 profit
$p^*$ 而取了 $p < p^*$，把这一步换成 $p^*$、把后面取到 $p^*$ 的那一步换回 $p$
（因为 $p^*$ 解锁后的状态是 $p$ 的超集），总和不变或增加。所以"每轮取当前最大
可行 profit"是最优策略。

## 核心代码（推荐）
```python
import heapq
from typing import List

class Solution:
    def findMaximizedCapital(
        self, k: int, w: int, profits: List[int], capital: List[int]
    ) -> int:
        n = len(profits)
        # 按 capital 升序；tie-break 无所谓（所有同 capital 的最终都会进堆）
        projects = sorted(zip(capital, profits))   # (capital, profit)
        heap: list[int] = []                       # max-heap on profit (存 -profit)
        ptr = 0

        for _ in range(k):
            # 解锁所有当前可承担的项目
            while ptr < n and projects[ptr][0] <= w:
                heapq.heappush(heap, -projects[ptr][1])
                ptr += 1
            if not heap:
                break                              # 没有可做的项目, 提前结束
            w += -heapq.heappop(heap)              # 取最大 profit
        return w
```

## 关键技巧
- **sort + lazy push**：与其每轮 $O(n)$ 扫描所有项目找可承担的，不如**一次排序
  $O(n \\log n)$ + 单调指针**——每个项目只入堆一次，总入堆操作 $O(n \\log n)$。
- **Python 模拟 max-heap**：`heapq` 只有 min-heap，存 `-profit` 即可。
- **monotonicity 是关键**：$w$ 单调不减保证了"已解锁的项目永远还可做"。如果
  $\\text{profits}[i]$ 允许负值，这个性质破坏，需要改成更复杂的 DP。
- **tie-break 无所谓**：相同 capital 的项目最终都会被同一轮 push 进堆，谁先
  谁后不影响结果。用户写的 `key=lambda x: (x[1], -x[0])` 多此一举但无害。
- **for k 比 while k > 0 更对仗**：固定轮数循环更明确，配 `if not heap: break`
  处理"项目不够 k 轮"的情况。

## 易错点
1. **每轮 $O(n)$ 扫描所有项目找最大** → $O(nk)$，$n, k = 10^5$ 时 TLE。必须
   用 sort + heap。
2. **min-heap vs max-heap 弄反**：要的是最大 profit，存 `-profit` 才对。
3. **终止条件漏判堆空**：当所有还没解锁的项目都做不起时（`projects[ptr][0] > w`）
   且堆空时，无项目可做，必须 break；否则 `heappop` 空堆会抛异常。
4. **指针重置**：`ptr` 不要在循环内重置；它是单调的（已入堆的不重复入）。
5. **profits 含 0**：题目允许 profit=0，pop 出 0 是合法的（虽然没收益），
   不要写 `if profit > 0` 之类的过滤——这会把"必须做满 k 轮"的题改成"可以
   提前停"，所幸本题答案不变（做 0-profit 不会变差），但语义要清楚。
6. **整型溢出（其他语言）**：$w + \\sum \\text{profit}$ 在 Java/C++ 要用 `long`，
   Python 自动大整数无忧。

## 复杂度
- 时间：$O((n + k) \\log n)$。排序 $O(n \\log n)$；每个项目最多入堆/出堆各
  一次 $O(n \\log n)$；额外做 $k$ 次 pop $O(k \\log n)$。
- 空间：$O(n)$ 用于排序结果 + 堆。

## Follow-up: 双堆做法（教科书框架）
不排序而是用**两个堆**：min-heap on capital（候选池）+ max-heap on profit
（已解锁池）。每轮把 min-heap 里 capital ≤ w 的全 pop 到 max-heap，再 pop
max-heap 顶。

```python
import heapq
from typing import List

class Solution:
    def findMaximizedCapital(
        self, k: int, w: int, profits: List[int], capital: List[int]
    ) -> int:
        # min-heap on capital: (cap, profit)
        cap_heap = list(zip(capital, profits))
        heapq.heapify(cap_heap)
        prof_heap: list[int] = []                  # max-heap, 存 -profit

        for _ in range(k):
            while cap_heap and cap_heap[0][0] <= w:
                _, p = heapq.heappop(cap_heap)
                heapq.heappush(prof_heap, -p)
            if not prof_heap:
                break
            w += -heapq.heappop(prof_heap)
        return w
```

### 与 sort + heap 版的对比
| 维度 | sort + heap (推荐) | 双堆 |
| --- | --- | --- |
| 渐近复杂度 | $O((n+k) \\log n)$ | $O((n+k) \\log n)$ |
| 排序 vs heapify | sorted: $O(n \\log n)$ 严格 | heapify: $O(n)$ 但每次 pop $O(\\log n)$ |
| 实测常数 | 略快（cache-friendly 顺序访问） | 略慢（堆操作随机访问） |
| 概念清晰度 | 一个堆 + 一个指针 | 两个堆，**"候选池→已解锁池"语义更显式** |
| 面试白板 | 代码更短 | 更容易讲"为什么贪心" |

**两版同阶**，常数差距小到不重要。生产/竞赛偏向 sort+heap；面试白板若想突出
"分阶段维护两个 priority queue"的思想，双堆更自然。

## 题目家族（sort + heap greedy）
- **LC 1353** Max Events Attended：每天选一个还没结束的、结束最早的会议。
  sort by start + min-heap on end day。
- **LC 1834** Single-Threaded CPU：到时间的任务进 heap，弹最短任务/最小 idx。
  sort by enqueueTime + min-heap on (processingTime, idx)。
- **LC 630** Course Schedule III：贪心+替换，max-heap 维护已选课程时长，新课
  挤掉时长最大的。sort by deadline + max-heap on duration。
- **LC 253** Meeting Rooms II：sort by start + min-heap on end。同结构，目标
  是最少房间数。

**统一模板**：`sort by 时间/容量轴` + `heap 维护 "当前候选/已选" 集合` + 每轮
`pop 出最优`。LC 502 是这个家族里"目标 = 最大化总和"的最干净例子。

## 一句话 pitch (面试 30 秒)
> 贪心 + sort + max-heap：每轮取当前可承担项目里 profit 最大的。先按 capital
> 升序排序，单调指针把"解锁"项目 push 进 max-heap，每轮 pop 一次。正确性是
> exchange argument——profit 非负保证可承担集合单调扩张，所以"先取最大"不会
> 错过更优解。复杂度 $O((n+k) \\log n)$。
"""


def main() -> None:
    """Seed LC 502 notes; idempotent via sentinel."""
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
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
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
