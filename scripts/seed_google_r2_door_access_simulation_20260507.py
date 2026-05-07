"""Seed Google R2 Coding problem: 门禁通行模拟 (Door Access Simulation).

User-provided content (Discord 2026-05-07 msg 1501776064647663656,
message.txt attachment). Custom problem (no LC id): N people arrive at a
door at given (timestamp, state in {enter, exit}); door processes one
person/sec; when multiple arrive in the same second, priority is decided
by what happened in the **previous second** (entering -> enter side wins,
exiting -> exit side wins, idle/start -> exit wins). Within a side, lower
original index wins.

Solution flavor: two deques (enter_q, exit_q) + a `prev` state variable
({-1 idle, 0 exit, 1 enter}) + sorted arrivals. Main loop has 4 steps:
admit arrivals, fast-forward time when both queues empty (CRITICAL:
reset prev to idle), pick a queue by prev, pop and advance clock.

USER EMPHASIS (per Discord message body): "注重和注意这里的沟通澄清"
-- the 写代码前应该问清楚的问题 section is the centerpiece of the
write-up. Preserved verbatim under a top-level heading so it can't be
missed. The interview signal here is "ask before coding," not just the
two-queue trick.

Per CLAUDE.md `Idempotent seed pattern per row type`: title is canonical
key for custom problems. Per Invariant 3, this seed is the sole
sanctioned write path.

The R2 Coding Index (doc 92) is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this
commit to add the new entry under a new `### Queue / Simulation` section.

Run: python scripts/seed_google_r2_door_access_simulation_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

TITLE = "门禁通行模拟"

DESCRIPTION = """\
给定一个数组 `events`, 长度为 `n`:

- 索引 `i` 代表第 `i` 个人
- `events[i] = (timestamp, state)`, `state in {"enter", "exit"}`

门每秒只能放一个人通过。当多人同一秒到达门口时, 按以下规则决定本秒谁通过:

1. 如果**前一秒**有人进门 → 进门方向优先
2. 如果**前一秒**有人出门 → 出门方向优先
3. 如果**前一秒**没人通过 (包括最开始) → 出门方向优先
4. 在同一方向内, 原数组索引小的人先通过

返回数组 `res`, `res[i]` 表示第 `i` 个人**实际通过门**的时刻。

来源: Google R2 Coding 2026-05 用户 Discord 2026-05-07 提供。
"""

NOTES = """\
## 门禁通行模拟 · 题解

### 题目描述

给定数组 `events` 长度 `n`, `events[i] = (timestamp, state)`, `state in {"enter", "exit"}`。门每秒过一人, 同秒多人冲突时按规则决定:

1. 前一秒有人**进门** -> 进门方向优先
2. 前一秒有人**出门** -> 出门方向优先
3. 前一秒**没人通过** (含最开始) -> 出门方向优先
4. 同方向内, **原数组索引小**的人先通过

返回 `res`, `res[i]` = 第 `i` 个人实际通过门的时刻。

---

## 写代码前应该问清楚的问题 (重点!)

> **面试时这道题口述给出, 先问问题再动手, 比写完被反问稳得多**。考官给口述题往往就是在等你问 -- 上来就写代码反而可能踩进他没说清的边界。

1. **吞吐量**: 一秒只能放一个人通过吗? 还是 $k$ 个? 这直接决定主循环结构。
2. **"前一秒"是什么意思**: 上一秒, 还是"上一次有人通过的那一刻"? 这两种在中间有空秒时结果不同。
   - 例: $t=2$ 有人进, $t=3, t=4$ 空, $t=5$ 来了同时冲突 -- 按"上一秒"算是 idle (出门优先), 按"上一次"算是 enter (进门优先)。
3. **timestamp 可以重复吗**: 从规则看显然可以, 但确认一下。
4. **输入是否保证按 timestamp 升序**: 如果保证就不用 sort, 否则需要防御性排序。
5. **state 字段类型**: 字符串还是 enum? 影响判等写法。
6. **数据规模**: $n$ 多大? `timestamp` 跨度多大? 如果 timestamp 跨度极大但 $n$ 小, 逐秒推进会 TLE, 必须用跳跃式。

**本题解的实现假设**: **1 人/秒**, **"前一刻" = 上一秒** (有 gap 视为 idle)。

---

## 思路

两个队列做"候车厅":

- `enter_q`: 已到门口、想进门、还没过去的人
- `exit_q`: 已到门口、想出门、还没过去的人

再维护两个变量:

- `t`: 模拟时钟, 门当前处理到第几秒
- `prev`: 上一秒发生了什么 (`-1` idle / `0` exit / `1` enter)

主循环每轮做四步:

1. **入队**: 把所有 `arrival <= t` 的人塞进各自队列 (他们"到了")
2. **跳跃**: 两队列都空 -> 时钟直接跳到下一个事件的 timestamp, `prev` 重置为 `-1` (中间有空秒, 所以"前一秒"是 idle)
3. **选队**: 两队列都有人时按 `prev` 决定优先级, 否则走非空那边
4. **出队**: 弹一个人, 记录 `res[idx] = t`, `t += 1`

> **最关键的陷阱**: 第 2 步跳跃时**必须**把 `prev` 重置为 idle。如果不重置, 跳过的那段空秒后再发生冲突, 会错误地继承跳跃前的方向状态。

---

## 代码

```python
from collections import deque
from typing import List, Tuple

def process_door(events: List[Tuple[int, str]]) -> List[int]:
    \"\"\"
    events[i] = (timestamp, state),  state in {"enter", "exit"}
    返回 res, res[i] = 第 i 个人实际通过门的时刻。

    假设: 1 人/秒; "前一刻"指上一秒 (有 gap 视为 idle)。
    \"\"\"
    n = len(events)
    if n == 0:
        return []

    # 防御性排序: (timestamp, idx, state)
    # timestamp 天然是第一关键字, idx 天然是第二关键字
    # -> sort 默认行为直接满足"同 timestamp 按 idx 升序"
    arr = sorted((ts, idx, state) for idx, (ts, state) in enumerate(events))

    res = [0] * n
    enter_q, exit_q = deque(), deque()
    i, t, prev = 0, 0, -1   # prev: -1 idle, 0 exit, 1 enter

    while i < n or enter_q or exit_q:
        # 1. 把所有"已到门口"的人放进对应队列
        while i < n and arr[i][0] <= t:
            _, idx, state = arr[i]
            (enter_q if state == "enter" else exit_q).append(idx)
            i += 1

        # 2. 候车厅空 -> 时钟跳到下一个事件, prev 重置为 idle
        if not enter_q and not exit_q:
            t = arr[i][0]
            prev = -1
            continue

        # 3. 选队列: 两边都有人看 prev; 只有一边就走那边
        if enter_q and exit_q:
            q = enter_q if prev == 1 else exit_q
        else:
            q = enter_q or exit_q   # 利用 deque 非空为真

        # 4. 出队、记录时间、时钟前进
        idx = q.popleft()
        prev = 1 if q is enter_q else 0
        res[idx] = t
        t += 1

    return res
```

### 几个写法上的点

- `sorted((ts, idx, state) for ...)` 利用 Python 元组默认字典序比较, 省去了 `key=` 参数。
- `q = enter_q or exit_q` 利用 deque 非空为真的特性, 把"只有一边非空"的两个分支合并。
- `q is enter_q` 用**引用比较** (不是 `==`), 确认刚弹的是哪个队列对象。

---

## 走个例子

输入:

```python
events = [
    (0, "enter"),   # 人 0
    (0, "exit"),    # 人 1
    (1, "enter"),   # 人 2
    (5, "exit"),    # 人 3
]
```

排序后顺序不变 (已经按 (timestamp, idx) 有序)。模拟过程:

| 轮次 | i | t | prev (开始) | 入队后 enter_q / exit_q | 处理 | res 更新 | t 推进到 |
|----|---|---|-----------|----------------------|------|---------|------|
| 1  | 0 | 0 | -1 idle   | `[0]` / `[1]`        | idle -> 出门优先, 弹 1 | res[1]=0 | 1    |
| 2  | 2 | 1 | 0 exit    | `[0, 2]` / `[]`      | 只有进门, 弹 0 | res[0]=1 | 2    |
| 3  | 3 | 2 | 1 enter   | `[2]` / `[]`         | 只有进门, 弹 2 | res[2]=2 | 3    |
| 4  | 3 | 3 | 1 enter   | 都空 -> **跳到 t=5**, prev=-1 | continue | -- | 5 |
| 5  | 3 | 5 | -1 idle   | `[]` / `[3]`         | 只有出门, 弹 3 | res[3]=5 | 6    |

最终 `res = [1, 0, 2, 5]`。

注意第 4 轮: $t=3$ 和 $t=4$ 这两秒空着, 所以跳跃后 `prev` 必须重置成 idle。本例里第 5 轮没冲突所以看不出影响, 但如果 $t=5$ 同时还有一个 enter, 就会按"idle -> 出门优先"决定, 而不是继承 $t=2$ 的 enter 状态。

---

## 复杂度

- **时间**: $O(n \\log n)$, 瓶颈在排序。如果输入保证有序, 可以省掉 sort, 主循环 $O(n)$ (每个人入队一次出队一次, 时间跳跃 $O(1)$)。
- **空间**: $O(n)$, 结果数组 + 排序后的副本 + 两个队列。

模拟看起来"暴力", 但实际上是这道题的最优解 -- 每个人能不能通过门取决于他前面所有人的处理结果, 没法跳过。

---

## 容易翻车的点

1. **gap 后忘记重置 `prev`**: 跳跃时间后如果不把 `prev` 设回 idle, 下次冲突会用错误的优先级。
2. **入队用 `if` 而不是 `while`**: 同一个 timestamp 可能有多个人, 必须循环全部入队。
3. **跳跃后忘了 `continue`**: 跳完时间应该回到第 1 步重新入队, 不能直接进第 3 步 -- 否则刚跳到的那个时刻的人没机会入队就被跳过。
4. **主循环条件不全**: 必须是 `i < n or enter_q or exit_q`。只判 `i < n` 会漏处理队列里的尾巴。
5. **`prev` 初始值**: 第一次冲突时按规则 3 应该出门优先, 所以初始化为 `-1` (idle) 就对, 不需要特判第一秒。
6. **同 index 优先级**: 依赖排序的稳定性 + 元组的字典序, 不需要在循环里再做额外判断。如果用了不稳定的排序或者忘了把 idx 放进排序键, 这条规则会悄悄失效。

### 一句话总结

口述题先问 6 个澄清问题再动手 (尤其是 "前一秒"语义和吞吐量); 实现是**两 deque + prev 状态变量**的 4 步主循环 (admit / 时间跳跃-重置 prev / 按 prev 选队 / 出队记录); 最大坑是**跳跃后必须把 prev 设回 idle**, 否则方向继承错乱。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": [
        "queue", "deque", "simulation", "priority-rules",
        "time-jump", "interview-clarification",
    ],
    "pattern": "two-queue-simulation",
    "family": "queue",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "description": DESCRIPTION,
    "notes": NOTES,
}


def _select_existing(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, "
        "       description, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, "
            " description, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"],
                norm["description"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
    if not drift:
        return pid, "UNCHANGED"

    set_clauses = ", ".join(f"{f} = ?" for f in drift)
    values = list(drift.values())
    values.append(pid)
    conn.execute(
        f"UPDATE problems SET {set_clauses} WHERE id = ?",
        values,
    )
    return pid, "UPDATED"


def main() -> int:
    """Insert-or-update the door-access simulation problem. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_door_access_simulation")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
