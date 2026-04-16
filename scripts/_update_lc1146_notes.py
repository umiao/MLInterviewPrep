"""Idempotent: mark LC 1146 complete and attach Chinese solution notes.

LC 1146 Snapshot Array -- "版本化数组 + 二分查找" 的 canonical 题。
属于 stateful_ds_design 家族，思路与 LC 981 Time Based Key-Value Store
同谱系（按时间戳追加 + bisect 查历史值）。

Run: python scripts/_update_lc1146_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 1146
PATTERN = "hash map + binary search"
SENTINEL = "<!-- LC1146_NOTES -->"

NOTES = """<!-- LC1146_NOTES -->
## 题目定位
**stateful_ds_design 家族** -- SnapshotArray 是"版本化数据结构 + 二分查找"的 canonical 题。
- `SnapshotArray(length)`：初始化一个全 0 数组，长度固定。
- `set(index, val)`：把当前版本的 `array[index]` 置为 `val`。
- `snap()`：把当前状态打快照，`snap_id` 自增，返回**打照前**的 `snap_id`（即此次快照对应的 id）。
- `get(index, snap_id)`：返回第 `snap_id` 次快照时 `array[index]` 的值。

**考点**：如何让 `snap()` 做到 $O(1)$ -- 直觉 "整体拷贝一份" 会在 length=$5 \\times 10^4$、snap=$10^5$ 时炸空间 ($5 \\times 10^9$ 单元)。破题点是**只为被改动的 index 记增量**，snap 仅仅 `snap_id += 1`。

## 核心洞察（必背）
**per-index 只追加 `(snap_id, val)` 二元组**：每个位置维护一条按 `snap_id` 升序的变更流水。
- `snap()` 不触碰任何流水，只把全局 `snap_id` 加一，$O(1)$。
- `get(index, snap_id)`：在 `history[index]` 里 `bisect_right((snap_id, +inf))` 然后 -1，找到最大的 `sid <= snap_id` 那条记录。若 index 从未被 set 过，返回默认 0。
- `set(index, val)`：追加 `(cur_snap, val)`。**特判**：若列表末尾已是当前 `cur_snap`（同一 snap 内多次 set 同一 index），原地覆盖，否则 bisect 会返回更早的错值。

空间 $O(K)$，$K$ 是 `set` 调用总数 -- **与 length 和 snap 次数都无关**，这是本解的杀手锏。

## Python 代码（面试可直接默写）
```python
from bisect import bisect_right
from collections import defaultdict

class SnapshotArray:
    def __init__(self, length: int):
        # history[i] = list of (snap_id, val), strictly increasing snap_id
        self.history: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.cur = 0  # current snap_id

    def set(self, index: int, val: int) -> None:
        lst = self.history[index]
        if lst and lst[-1][0] == self.cur:
            lst[-1] = (self.cur, val)         # 同一 snap 内覆盖
        else:
            lst.append((self.cur, val))       # 追加 O(1) amort

    def snap(self) -> int:
        sid = self.cur
        self.cur += 1
        return sid                             # 返回刚完成的 snap_id

    def get(self, index: int, snap_id: int) -> int:
        lst = self.history.get(index)
        if not lst:
            return 0                           # 从未被 set，初始 0
        # 找 sid <= snap_id 的最大那条
        i = bisect_right(lst, (snap_id, float('inf'))) - 1
        return lst[i][1] if i >= 0 else 0
```

## 走查示例
`SnapshotArray(3)`，操作序列：
```
set(0, 5)   -> history[0]=[(0,5)], cur=0
snap()      -> 返回 0, cur=1
set(0, 6)   -> history[0]=[(0,5),(1,6)], cur=1
get(0, 0)   -> bisect_right([(0,5),(1,6)], (0,+inf)) = 1, 索引 0 -> 值 5  ✓
get(0, 1)   -> bisect_right(..., (1,+inf)) = 2, 索引 1 -> 值 6
snap()      -> 返回 1, cur=2
get(0, 2)   -> bisect_right(..., (2,+inf)) = 2, 索引 1 -> 值 6（快照 2 里没新写入，继承快照 1 的值）
```

注意 `get(0, 0)` 那一步：`bisect_right` 用 `(snap_id, +inf)` 作 key 是为了把所有 `sid == snap_id` 的记录都归到"左侧"，减一之后正好定位到**最后一次** `sid <= snap_id` 的写入 -- 这正是该快照对应的值。

## 复杂度
- `set`：$O(1)$ 摊还（dict 访问 + list append / 尾部覆盖）。
- `snap`：$O(1)$。**核心卖点**。
- `get`：$O(\\log K_i)$，$K_i$ 是 index $i$ 上的 set 次数；最坏 $O(\\log K)$。
- 空间：$O(K)$，$K$ = 全局 set 调用总数。与 `length` 和 snap 次数**解耦**。

## 易错点
1. **不要在 snap 里拷贝整个数组**。LC 测试用例 length $\\le 5 \\times 10^4$、snap $\\le 10^5$，整体拷贝 $5 \\times 10^9$ 单元直接 MLE/TLE。snap 必须 $O(1)$。
2. **同一 snap 内多次 `set(i, v)` 必须覆盖，不能 append**。否则 `history[i]` 里会出现两条同 `snap_id` 的记录，`bisect_right` 在 `(sid,+inf)` 下的行为是"跳过同 sid 的所有项"，-1 后落在最新的一条 -- 看起来好像对，但如果面试官要求"严格 per-snap 唯一"，重复记录是浪费；更关键的是如果换成 `bisect_left` 或其他查询模式就会读错旧值。保持 per-(index, snap_id) 唯一是健壮写法。
3. **`bisect_right` 比 `bisect_left` 好**。我们要的是"sid $\\le$ snap_id 的最大一条"，等价于"严格大于 snap_id 的第一条减一"。`bisect_right((snap_id, +inf))` 刚好把等于 snap_id 的也包含进来；写成 `bisect_left((snap_id,))` 然后 +1 再 -1 更烧脑。用 `(snap_id, +inf)` 作 sentinel 是 Python bisect 对 tuple 字典序的经典用法。
4. **snap 从未被 set 过的 index**：返回 0 是题目语义（初始全零），不是返回 None 或报错。defaultdict 访问会创建空 list，记得用 `history.get(index)` 或在 get 里显式判 `if not lst`。
5. **`snap()` 返回值是"刚完成的 snap_id"**。`self.cur` 先作为此次的 id 返回再自增，别写反。

## Follow-up 追问指针
- **LC 981 Time Based Key-Value Store**：同思路 -- 键值对按 timestamp 追加，`get(key, ts)` 用 bisect 找 $\\le ts$ 最大。SnapshotArray 相当于"以 index 为 key、cur_snap 为 ts"的特例。
- **并发 snap 怎么办？** 如果多个线程同时 `snap()` + `set()`，需要 MVCC 风格：每个事务用自己的 `cur_snap` 读，写时 CAS 插入新版本。本质上就是数据库的 **MVCC (Multi-Version Concurrency Control)** -- 每个版本是 `(txn_id, val)`，读事务看自己开始时的 snapshot，写事务只追加新版本。**本题是 MVCC 的单线程教学版**。
- **version cleanup / GC**：如果只需要保留最近 $N$ 个 snapshot（类似 Git shallow clone），需要给 history 加"最旧 snap_id"水位线，定期 popleft 过期记录 -- 此时 `history[i]` 要换 `deque` 并记录每个 index 的最新值以免 get 落空。
- **跨 index 的整体回滚 `rollback(snap_id)`**：如果要让 cur 回到旧 snap_id 并能继续写，需要把所有 `history[i]` 里 `sid > snap_id` 的尾部截掉。整体 O(changed indices)，不影响本解复杂度大框架，只是 API 设计题。
- **如果 set 极多而 get 极少**：append-only 列表其实已最优。反过来如果 get 极多、set 稀疏，可在每次 snap 后对 history[i] 做一次 compress（把连续相同值合并），get 端命中更浅。
- **能否换成 persistent segment tree？** 可以（每次 set 新建 $O(\\log n)$ 节点，snap 共享旧根），get 也是 $O(\\log n)$。优点是跨 index 范围查询（如"snap_id=7 时 index 区间 [3,9] 和"）支持到 $O(\\log n)$；缺点是常数大、实现复杂。本题只问点查，列表 + bisect 完胜。

## 一句话 pitch（面试 45 秒）
> 每个 index 维护一条按 snap_id 升序的 `(sid, val)` 变更流水，`snap()` 只把全局 snap_id +1 做到 $O(1)$（**不整体拷贝数组**），`get(i, sid)` 在 `history[i]` 上 `bisect_right((sid, +inf)) - 1` 找最大的 $\\le sid$ 一条。空间 $O(K)$，$K$ 是 set 总次数，与 length 和 snap 次数解耦。同一 snap 内多次 set 同 index 要原地覆盖而不是 append，否则历史流水冗余。这个结构等价于数据库 MVCC 的单线程教学版 -- 每个写操作是一个新版本，读永远定位到 $\\le$ 自己 snap 的最新版本。
"""


def main() -> None:
    """Attach notes and mark LC 1146 as completed; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, _fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN

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
