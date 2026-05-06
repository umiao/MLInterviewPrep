"""Seed Google R2 Coding link to LC 1882 'Process Tasks Using Servers'.

User-provided solution (Discord 2026-05-05). LC 1882 row already exists
(problems.id=539) from the bulk LC import, but with notes=NULL and no
family/pattern/source/tags/Google company-tag. This seed:

  1. Fills `problems.notes` with the full Chinese 题解 (two-heap event
     simulation; available-heap keyed (weight, idx); busy-heap keyed
     (free_time, weight, idx); fast-forward via popping busy when no
     server available -- avoids per-tick ticking).
  2. Sets family='heap', pattern='two-heap-simulation', tags including
     heap/simulation/priority-queue, source='Google R2 2026-05',
     is_completed=1.
  3. Merges 'Google' into company_tags WITHOUT clobbering existing
     ["LinkedIn", "Uber", "Adobe"] -- preserves cross-company surface.

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://539`. The R2 Coding
Index doc 92 is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in the same
commit to add a `### Heap / Simulation` section referencing this row.

Idempotent. leetcode_id=1882 is the canonical key. First run on a row
with notes=NULL and no Google tag: 1 UPDATE. Re-run on identical state:
0 writes (no drift). Per Invariant 3 (CLAUDE.md), this seed is the sole
sanctioned write path for these field updates.

Run: python scripts/seed_google_r2_lc1882_process_tasks_servers_20260505.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 1882
SOURCE_LABEL = "Google R2 2026-05"
GOOGLE_TAG = "Google"

NOTES = """\
## 1882. Process Tasks Using Servers

### 思路

事件驱动的模拟。两只堆维护服务器的两个状态：

- **availableHeap**：当前空闲的服务器。键为 `(weight, idx)`，按 weight 优先、idx 次之取最小，直接对应题目"choose the server with smallest weight (then smallest index)"。
- **busyHeap**：正在执行任务的服务器。键为 `(free_time, weight, idx)`，按最早释放时间排序；释放时序需要它，重新入 available 时还要保留 weight/idx。

任务 $i$ 在时刻 $i$ 入队（题目保证按时间到达）。处理任务 $i$ 的标准流程：

1. **释放完工**：把所有 `free_time <= i` 的 busy 服务器弹回 available（一个 while 循环，均摊 $O(\\log n)$）
2. **正常分配**：available 非空 → 直接弹最优 (weight, idx)
3. **快进时间**：available 为空 → 弹 busy 顶部，把 `taskTime` 推进到该 server 的 `free_time`，然后用它接这个任务

第 3 步的关键正确性：busy 顶部就是"会最先空出来的那台"，并且因为堆键以 free_time 排序、weight/idx 是次级，**多个同时空出的服务器中权重最小的会浮在堆顶**——所以直接弹一个就拿到了"该时刻最优可用"的服务器，不必把这一时刻所有空出的服务器全释放再选。

> **不是逐时刻 ticking**：直接跳到下一关键事件时刻（任务到达或服务器空闲），整体只有 $O(n + m)$ 次堆操作。

### 代码

```python
import heapq
from typing import List

class Solution:
    def assignTasks(self, servers: List[int], tasks: List[int]) -> List[int]:
        busyHeap: list[tuple[int, int, int]] = []          # (free_time, weight, idx)
        availableHeap: list[tuple[int, int]] = []          # (weight, idx)

        nServer = len(servers)
        for i in range(nServer):
            heapq.heappush(availableHeap, (servers[i], i))

        ans: list[int] = []
        for i in range(len(tasks)):
            taskTime, requiredTime = i, tasks[i]

            # 1) Release any servers whose free_time has come.
            while busyHeap and busyHeap[0][0] <= taskTime:
                _, _weight, _idx = heapq.heappop(busyHeap)
                heapq.heappush(availableHeap, (_weight, _idx))

            # 2) Pick a server: prefer available, else fast-forward to next free.
            if not availableHeap:
                taskTime, _weight, _idx = heapq.heappop(busyHeap)
            else:
                _weight, _idx = heapq.heappop(availableHeap)

            # 3) Schedule it back to busy with new free_time.
            heapq.heappush(busyHeap, (taskTime + requiredTime, _weight, _idx))
            ans.append(_idx)

        return ans
```

### 复杂度

设 $n = |\\text{servers}|$, $m = |\\text{tasks}|$。

- 时间 $O((n + m) \\log n)$：每个服务器最多在 busy/available 之间来回 $O(m / n)$ 次，每次堆操作 $\\log n$；任务总数 $m$ 决定主循环次数
- 空间 $O(n)$：两个堆合计 $n$ 个元素

### 易错点

1. **available 空时不要忙等**：忙等会退化到 $O(\\max(\\text{tasks}))$ 时刻，TLE。直接 `heappop(busyHeap)` 拿最早释放的并把 `taskTime` 跳过去
2. **busyHeap 三元组顺序很关键**：`(free_time, weight, idx)`，free_time 必须在最前；如果错写成 `(weight, free_time, idx)` 释放顺序就乱了
3. **同时空出多台服务器不需要全部释放再选**：busy 顶部的 (free_time, weight, idx) 已经处理了 tie-breaking；弹一个就是该时刻最优
4. **release 的循环条件用 `<= taskTime`**：边界等号要包含——`free_time == taskTime` 表示这台已经空了，可以接下一个

### 一句话总结

两只堆 (available 按 (weight, idx)、busy 按 (free_time, weight, idx)) 跑事件驱动模拟；available 空了就快进到下一释放时刻，避免按 tick 推进。
"""

PATTERN = "two-heap-simulation"
FAMILY = "heap"
TAGS = ["heap", "simulation", "priority-queue"]


def _select_existing(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, tags, pattern, family, source, company_tags, is_completed, notes "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
    ).fetchone()
    if row is None:
        return None
    keys = ["id", "tags", "pattern", "family", "source", "company_tags",
            "is_completed", "notes"]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _merge_company_tags(current_json: str | None, add: str) -> str:
    """Append `add` to JSON-encoded list if not present. Preserve order."""
    cur = json.loads(current_json) if current_json else []
    if add not in cur:
        cur.append(add)
    return json.dumps(cur, ensure_ascii=False)


def upsert(conn: sqlite3.Connection) -> tuple[int, str]:
    """UPDATE problems row 539 (LC 1882). Return (id, action)."""
    existing = _select_existing(conn, LEETCODE_ID)
    if existing is None:
        raise SystemExit(
            f"[FAIL] problems.leetcode_id={LEETCODE_ID} missing -- "
            "the bulk LC seed must run first"
        )
    pid, current = existing

    target = {
        "tags": json.dumps(TAGS, ensure_ascii=False),
        "pattern": PATTERN,
        "family": FAMILY,
        "source": SOURCE_LABEL,
        "company_tags": _merge_company_tags(current.get("company_tags"), GOOGLE_TAG),
        "is_completed": 1,
        "notes": NOTES,
    }
    drift = {f: target[f] for f in target if current.get(f) != target[f]}
    if not drift:
        return pid, "UNCHANGED"

    set_clauses = ", ".join(f"{f} = ?" for f in drift)
    values = list(drift.values()) + [pid]
    conn.execute(
        f"UPDATE problems SET {set_clauses} WHERE id = ?",
        values,
    )
    return pid, "UPDATED"


def main() -> int:
    """Update LC 1882 row with notes + Google linkage. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc1882_google")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert(conn)
        print(f"[{action}] problem id={pid} leetcode_id={LEETCODE_ID}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
