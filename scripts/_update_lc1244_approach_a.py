"""Rewrite LC 1244 Approach A: show explicit size-K min-heap (with nlargest as
reference comment), instead of hiding the algorithm behind heapq.nlargest.

User feedback: in an interview, calling nlargest reads as a shortcut; writing
out the size-K min-heap replace-smallest pattern demonstrates the algorithm.
The nlargest one-liner stays as an inline comment.

Idempotent: scans current notes for the old Approach A code block and the
accompanying explanation paragraph; replaces both. Run twice and the second
run detects the new content already in place and reports a no-op.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 1244

OLD_BLOCK = """### Approach A: Hash + `nlargest` (canonical 写法)

```python
import heapq

class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        return sum(heapq.nlargest(K, self.scores.values()))

    def reset(self, playerId: int) -> None:
        self.scores[playerId] = 0
```

**为什么 nlargest 已经够快**：`heapq.nlargest(K, iterable)` 内部维护一个大小为 K 的 min-heap，扫一遍 iterable：O(N log K)。K 远小于 N 时接近 O(N)。N <= 1000 的 LC 约束下，单次 `top` 顶多 ~10K 次比较，完全不用纠结。

**优点**：没有 stale entry 问题，没有恢复步骤，`reset` 就一行。面试首选。

---"""

NEW_BLOCK = """### Approach A: Hash + 手写 size-K min-heap (canonical 写法)

```python
import heapq

class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        # 面试默认写法：手写 size-K min-heap，dynamic replace 最小的
        # 省事一行版本（若面试允许）：return sum(heapq.nlargest(K, self.scores.values()))
        heap = []  # min-heap, 堆顶是当前 top-K 里最小的
        for score in self.scores.values():
            if len(heap) < K:
                heapq.heappush(heap, score)
            elif score > heap[0]:
                heapq.heapreplace(heap, score)  # pop 当前最小 + push 新值，一步完成
        return sum(heap)

    def reset(self, playerId: int) -> None:
        self.scores[playerId] = 0
```

**为什么这个写法是面试首选（而不是直接调 nlargest）**：`heapq.nlargest(K, it)` 内部就是这段代码——维护一个大小为 K 的 min-heap，扫一遍 iterable，遇到比堆顶大的就 `heapreplace`。面试场景下**手写比调库更能证明你理解算法**；调库是"我知道有这个 API"，手写是"我知道 API 背后在干什么"。功能和复杂度完全等价：O(N log K) 时间、O(K) 空间，K 远小于 N 时接近 O(N)。

**关键技巧 `heapreplace`**：等价于 `heappop` 后 `heappush` 但只做一次下滤（sift-down），常数更小。这是 size-K 维护模板的标志性 API，面试写出 `heapreplace` 是加分点。

**优点**：没有 stale entry 问题，没有恢复步骤，`reset` 就一行。LC 约束下性能和 nlargest 完全一样，算法可见度更高。

---"""


def main() -> None:
    """Replace LC 1244 Approach A code block + explanation; idempotent."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = ?", (LC_ID,)
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, notes = row
        if NEW_BLOCK in notes:
            print(f"[NOOP] LC {LC_ID} id={pid} already has the new Approach A")
            return
        if OLD_BLOCK not in notes:
            raise SystemExit(
                f"[FAIL] LC {LC_ID} notes do not contain the expected old Approach A block; "
                "manual inspection needed"
            )
        new_notes = notes.replace(OLD_BLOCK, NEW_BLOCK)
        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?", (new_notes, pid)
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} Approach A rewritten "
            f"(notes_len {len(notes)} -> {len(new_notes)})"
        )


if __name__ == "__main__":
    main()
