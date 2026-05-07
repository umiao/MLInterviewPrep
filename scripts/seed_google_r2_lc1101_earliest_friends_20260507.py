"""Seed Google R2 Coding problem: LC 1101 Earliest Moment Everyone Become Friends + breakup follow-up.

User-provided framing (Discord 2026-05-07 msg 1501807001548623912):
"vanilla 用并查集即可, 但 follow-up 允许朋友 breakup -- 需要 rollback DSU
+ snapshot 记录每个人成为朋友之前的状态". LC 1101 row already exists
(id=264, leetcode_id=1101, medium, company_tags=[LinkedIn,Uber,Adobe])
with notes=NULL and no family/pattern -- this seed UPDATEs in place,
unioning Google into company_tags without clobbering the cross-company
surface, sets family='union-find' pattern='rollback-dsu', and writes a
tight Chinese 题解.

Vanilla solution:
  - Sort logs by timestamp ascending.
  - Initialize DSU with n components.
  - For each (t, a, b): union(a, b); if it actually merges two distinct
    components, decrement count. When count == 1, return t.
  - If never reaches 1, return -1.

Follow-up (allow breakups):
  - Path compression makes ops irreversible -- use union-by-rank ONLY.
  - Each union pushes snapshot {(rx, parent[rx]_old=rx, ry, rank[ry]_old)}
    onto history stack so undo restores prior parent/rank.
  - Breakup at time t pops the corresponding union from history and reverts.
  - Caveat: simple stack supports only LIFO undo. For arbitrary
    fully-dynamic connectivity (any past union may break at any future
    time), need offline divide-and-conquer over the timeline + rollback
    DSU, or Link-Cut Trees online. Note this clearly in the writeup so the
    interviewer sees the awareness.

Per `feedback_pinterest_two_tier_notes`: UPDATE problems.notes (drawer
renders via db://264). Doc 92 R2 Coding Index extended to add LC 1101
entry under existing `### Graph / 连通分量` section (alongside the
cascade-failure problem -- both connectivity problems, complementary
algorithm focus: BFS multi-source vs DSU).

Idempotent. leetcode_id=1101 is the canonical key. First run on the
existing notes=NULL row: 1 UPDATE. Re-run on identical state: 0 writes.

Run: python scripts/seed_google_r2_lc1101_earliest_friends_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 1101
TITLE = "The Earliest Moment When Everyone Become Friends"
URL = "https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/"
SOURCE_LABEL = "Google R2 2026-05"

# Union with existing tags (LinkedIn, Uber, Adobe set by earlier pass);
# the merge helper preserves order and just appends Google.
COMPANY_TAGS_TO_ADD = ["Google"]

NOTES = """\
## LC 1101. The Earliest Moment When Everyone Become Friends

### 题意速览

`n` 人编号 `0 ~ n-1`, 给一组 `logs[i] = (timestamp, a, b)` 表示 a 和 b 在 timestamp 时刻成为朋友。"朋友"关系是**等价类** (自反、对称、传递)。求**最早的 timestamp**, 使得**所有 n 个人成为同一个朋友圈**; 不存在则返回 `-1`。

### 标准解 (Vanilla DSU)

经典 union-find: 排序 + 顺序合并 + 组件计数。

- 按 `timestamp` 升序排序 logs。
- DSU 初始化 `n` 个独立组件 (`count = n`)。
- 遍历每条 log, `union(a, b)`: 若**真合并**了两个不同组件, `count -= 1`。
- 当 `count == 1` 时, 当前 `timestamp` 就是答案; 提前返回。
- 全跑完仍 `count > 1` 则返回 `-1`。

```python
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # 路径压缩
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                   # 同 root, 没合并
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True

class Solution:
    def earliestAcq(self, logs: list[list[int]], n: int) -> int:
        logs.sort(key=lambda x: x[0])
        dsu = DSU(n)
        count = n
        for t, a, b in logs:
            if dsu.union(a, b):
                count -= 1
                if count == 1:
                    return t
        return -1
```

**复杂度**: 时间 $O(m \\log m + (m + n) \\cdot \\alpha(n))$ ($m = |\\text{logs}|$, $\\alpha$ 反 Ackermann 近 O(1)), 空间 $O(n)$。

---

### Follow-up: 允许朋友 breakup -- Rollback DSU

> **新约束**: 在某个时刻 `t'`, 一对已经成为朋友的人 `(a, b)` 可以 breakup, 撤销那次 union 操作; 之后每个时刻都可能继续 union 或 breakup。问每次操作后所有 n 人是否 connected (或类似的连通性查询)。

#### 关键障碍

普通 DSU 用**路径压缩**之后, `find(x)` 直接把 `x` 接到 root; 撤销原始那次 union 时, 所有路径上被压缩的节点的 parent 已经丢失, **不可逆**。

#### 解决方案

**两条规则同时改动**:

1. **只用 union-by-rank, 禁用路径压缩**。`find(x)` 只走 parent 链回 root, 不修改任何 parent。
2. **每次 union 写一份 snapshot**, 压栈; breakup 时弹栈、按 snapshot 反向赋值。

每个 snapshot 只需记录这次 union 改动的两个标量:

```
snapshot = (rx, ry, old_rank_rx)
# 假设 union 把 ry 挂到 rx 下: parent[ry] = rx (原来 parent[ry] = ry); 若 rank 持平则 rank[rx] += 1
```

**撤销**: `parent[ry] = ry; rank[rx] = old_rank_rx`。

```python
class RollbackDSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.history: list[tuple[int, int, int]] = []      # (rx, ry, old_rank_rx)

    def find(self, x: int) -> int:
        while self.parent[x] != x:                          # 不做路径压缩
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        rx, ry = self.find(a), self.find(b)
        if rx == ry:
            self.history.append((-1, -1, -1))               # 占位, 让撤销栈对齐 op 流
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        old_rank_rx = self.rank[rx]
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.history.append((rx, ry, old_rank_rx))
        return True

    def rollback(self) -> None:
        rx, ry, old_rank_rx = self.history.pop()
        if rx == -1:
            return                                          # 占位 op, 无需撤销
        self.parent[ry] = ry
        self.rank[rx] = old_rank_rx
```

**复杂度**: 没了路径压缩, `find` 是 $O(\\log n)$ (union-by-rank 保证树高 ≤ $\\log n$); 每个 op (union/rollback) $O(\\log n)$。

#### 重要细节: 哪种 "breakup" 才能直接用栈?

栈式 rollback 隐含一个假设: **撤销顺序必须是 LIFO -- 最后的 union 最先被撤销**。

- 若 breakup 总是撤销"最近一次 union", 直接 `rollback()` 即可。
- **若 breakup 是任意 (timeline 中**任何**过去的 union 都可能在**未来**任何时刻被撤销)** -- 这就是经典的**全动态连通性**问题, 普通栈式 rollback 不够。常见两条路:
  - **离线**: 把 timeline 切成线段树式的区间, 每条边只在它存在的时间段内被加, 用 **divide-and-conquer + rollback DSU** 跑, 整体 $O((n + q) \\log^2 n)$。
  - **在线**: 用 **Link-Cut Trees** (Tarjan), 复杂度 $O(\\log n)$ per op 但代码量大。

**面试沟通建议**: 提到 "我假设 breakup 是 LIFO 顺序撤销最近的 union, 那就栈式 rollback DSU; 如果是任意顺序 breakup, 那是全动态连通性, 离线用 D&C + rollback DSU, 在线用 Link-Cut Trees。" 把假设说清楚比直接写代码值钱。

#### 一图理解 snapshot

```
Before union(a, b):                  After union (假设 rank[rx] > rank[ry]):
  rx                                   rx
  |    ry                              |\\
  ...   |                              ... ry
        ...                                |
                                           ...

push snapshot: (rx, ry, old_rank_rx=rank[rx])
rollback: parent[ry] = ry, rank[rx] = old_rank_rx -- 完全复原
```

---

### 易错点

- **路径压缩与 rollback 互斥**: 如果保留路径压缩, snapshot 必须额外记录所有被压缩节点的 parent, 复杂度爆炸; 工程上直接禁用路径压缩。
- **`union` 失败 (同 root) 也要压一个占位 snapshot**, 否则 op 流和 history 栈对不齐, breakup 时撤销错了对象。
- **Union-by-size vs union-by-rank**: 两者都行, 但 rank 写出来的 snapshot 字段更少 (`rank[rx]`, 一个标量), size 需要把两个 size 都恢复, 略繁琐。
- **`count` 计数器**也要同步 rollback: 真合并的 union 撤销时 `count += 1`; 占位 op (同 root) 撤销时 `count` 不变。LC 1101 follow-up 题如果还要追踪连通性查询, 这是常见漏点。
- **LIFO 假设**要明确告诉面试官: 普通栈式 rollback 不能处理任意时间点的 breakup; 必须是离线 D&C 或 LCT。

### 一句话总结

LC 1101 vanilla = 排序 + DSU + 组件计数, $O(m \\log m)$ 一遍扫到 `count==1`; **breakup follow-up = 禁用路径压缩 + 每次 union 压 snapshot 栈 (rx, ry, old_rank_rx) + rollback 时弹栈反向赋值**, 假设 LIFO 撤销顺序; 任意顺序 breakup 是全动态连通性, 离线 D&C 或 Link-Cut Trees。
"""

PATTERN = "rollback-dsu"
FAMILY = "union-find"
TAGS = ["union-find", "graph", "rollback", "dsu", "connectivity"]


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


def _merge_company_tags(current_json: str | None, add_list: list[str]) -> str:
    """Append each tag in add_list to JSON-encoded list if not present. Preserve order."""
    cur = json.loads(current_json) if current_json else []
    for t in add_list:
        if t not in cur:
            cur.append(t)
    return json.dumps(cur, ensure_ascii=False)


def upsert(conn: sqlite3.Connection) -> tuple[int, str]:
    """UPDATE problems row 264 (LC 1101). Return (id, action)."""
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
        "company_tags": _merge_company_tags(
            current.get("company_tags"), COMPANY_TAGS_TO_ADD
        ),
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
    """Update LC 1101 row with notes + Google linkage. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc1101_earliest_friends")
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
