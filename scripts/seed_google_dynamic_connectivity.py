"""Seed Google coding prep for T-P1-209: Dynamic Connectivity via Segment Tree + Rollback DSU.

User-flagged problem 11: fully-dynamic connectivity with unions AND edge
deletions. Standard path-compressed DSU handles only monotone unions, so
once edges can vanish we need a different tool. The canonical offline
technique is a segment tree over time + rollback (undo-stack) DSU.

Cross-references the Uber custom problem id=1033 "Uber Rider Connection
Log", whose follow-up asked exactly this (blocked-rider events).

Chinese prose; algorithm names, code, complexity in English per
feedback_lc_notes_chinese.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"

TITLE = "Fully Dynamic Connectivity (Segment Tree over Time + Rollback DSU)"

DESCRIPTION = """Google coding interview (custom, non-LC; problem 11 from user flag list).

Setting: a graph on `n` nodes receives a chronological event stream:
- `ADD u v` at time `t`: edge `(u,v)` appears.
- `REMOVE u v` at time `t`: a previously added edge `(u,v)` disappears.
- `QUERY u v` at time `t`: are `u` and `v` connected *right now*?

Offline version (all events known up front) is the classic target: answer every
QUERY correctly with total time `O((N + Q) log Q * alpha(N))`.

Why the obvious DSU doesn't work: path-compressed / union-by-rank DSU supports
only monotone unions. Once REMOVE is introduced, there is no cheap "undo" on a
compressed tree (the compression destroys history). Rebuilding DSU per query is
`O(Q * (N + E))` and blows up.

Related:
- Uber custom problem id=1033 "Uber Rider Connection Log" -- union-only version;
  the follow-up "blocked rider" extension is this problem.
- LC 1970 / 1101 style offline connectivity questions use variants of the same
  trick (segment tree over time, or sort queries by threshold).
- LC 947 / 684 / 685 use vanilla DSU without deletion.

Follow-ups to expect:
(A) Online (must answer each query before seeing the next): need Link-Cut Trees
    or Euler-Tour Trees, `O(log N)` per op -- far outside a 45-min bar.
(B) Report the number of connected components at each time -- same structure,
    maintain a `components` counter in the rollback DSU.
(C) Edge weights / MST over a time window -- "offline dynamic MST", same
    segment-tree-over-time scaffold with a different inner structure.
(D) Space budget: can we avoid storing each edge in `O(log Q)` segment-tree
    nodes? Use small-to-large or link-cut if memory is the bottleneck.
"""

NOTES = """## Fully Dynamic Connectivity (Google 2026-04-17, problem 11)

### 问题本质与难点

- **Union-only**（如 LC 684 / Uber problem 1033 主线）：path-compressed DSU，
  均摊 $O(\\alpha(N))$ 即可。
- **加上删除**：DSU 的 path compression 把历史结构烧进了树形；一旦 union
  发生过，想"撤销"成本不可控。常见错误：试图在 compressed DSU 上倒着
  `parent[x] = x` —— 这会破坏其它节点的路径，不是合法撤销。

核心观察：**每条边存在的时间是一个区间** $[t_\\text{add}, t_\\text{remove})$。
把所有边按时间区间塞进一棵**时间线段树**；对每个查询时间点 $t$，沿根到叶
路径收集覆盖 $t$ 的所有边，就恰好是那一刻图的边集。

### 主解法：Segment Tree over Time + Rollback DSU

**数据结构**：
1. `seg[node]`: 一个 list[tuple[int,int]]，node 覆盖的时间区间上"全程存在"
   的边。边被 lazy 推到它完全覆盖的 seg 节点（不下推到叶）。
2. `DSU with rollback`: union-by-rank (或 union-by-size)，**禁用 path
   compression**；每次 `union` 往 `history` 栈压一条 "who was changed"，
   `rollback()` 弹出并复原。

**算法骨架**：DFS 时间线段树 —— 进入节点 apply 所有 seg-edges (union)，
递归两个孩子；离开节点时 rollback 到进入前的 history 长度。叶节点对应
某个具体时间 $t$，在叶处回答此时刻的所有 query。

```python
from __future__ import annotations

class RollbackDSU:
    __slots__ = ("parent", "rank", "components", "history")

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n
        # history frame: (root_x, old_rank_x, root_y, old_parent_y, comp_delta)
        self.history: list[tuple[int, int, int, int, int]] = []

    def find(self, x: int) -> int:  # NO path compression
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            # still push a no-op frame so rollback count matches union count
            self.history.append((ra, self.rank[ra], ra, self.parent[ra], 0))
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        # attach rb under ra
        old_rank_a = self.rank[ra]
        old_parent_b = self.parent[rb]
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        self.history.append((ra, old_rank_a, rb, old_parent_b, 1))

    def snapshot(self) -> int:
        return len(self.history)

    def rollback(self, target_len: int) -> None:
        while len(self.history) > target_len:
            ra, old_rank_a, rb, old_parent_b, comp_delta = self.history.pop()
            self.rank[ra] = old_rank_a
            self.parent[rb] = old_parent_b
            self.components += comp_delta
```

```python
class TimeSegTree:
    def __init__(self, n_time: int) -> None:
        self.n = n_time
        self.tree: list[list[tuple[int, int]]] = [[] for _ in range(4 * n_time)]

    def add(self, node: int, lo: int, hi: int, ql: int, qr: int,
            edge: tuple[int, int]) -> None:
        if qr < lo or hi < ql:
            return
        if ql <= lo and hi <= qr:
            self.tree[node].append(edge)
            return
        mid = (lo + hi) // 2
        self.add(2 * node, lo, mid, ql, qr, edge)
        self.add(2 * node + 1, mid + 1, hi, ql, qr, edge)

    def solve(self, node: int, lo: int, hi: int,
              dsu: RollbackDSU, queries: dict[int, list],
              answers: dict[int, bool]) -> None:
        snap = dsu.snapshot()
        for u, v in self.tree[node]:
            dsu.union(u, v)
        if lo == hi:
            for qid, (u, v) in queries.get(lo, []):
                answers[qid] = dsu.find(u) == dsu.find(v)
        else:
            mid = (lo + hi) // 2
            self.solve(2 * node, lo, mid, dsu, queries, answers)
            self.solve(2 * node + 1, mid + 1, hi, dsu, queries, answers)
        dsu.rollback(snap)
```

**Driver**：
```python
def fully_dynamic_connectivity(n: int, events: list[tuple]) -> list[bool]:
    # events[i] = ('ADD', u, v) | ('REMOVE', u, v) | ('QUERY', u, v)
    T = len(events)
    alive: dict[frozenset[int], int] = {}  # edge -> add-time
    seg = TimeSegTree(T)
    queries: dict[int, list] = {}
    answers: dict[int, bool] = {}
    qid = 0

    for t, ev in enumerate(events):
        kind = ev[0]
        if kind == "ADD":
            alive[frozenset((ev[1], ev[2]))] = t
        elif kind == "REMOVE":
            key = frozenset((ev[1], ev[2]))
            start = alive.pop(key)
            seg.add(1, 0, T - 1, start, t - 1, (ev[1], ev[2]))
        else:  # QUERY
            queries.setdefault(t, []).append((qid, (ev[1], ev[2])))
            answers[qid] = False
            qid += 1

    # edges that were never removed: active until T-1
    for key, start in alive.items():
        u, v = tuple(key)
        seg.add(1, 0, T - 1, start, T - 1, (u, v))

    dsu = RollbackDSU(n)
    seg.solve(1, 0, T - 1, dsu, queries, answers)
    return [answers[i] for i in range(qid)]
```

### 复杂度

设 $N$ = 节点数，$Q$ = 事件总数（adds + removes + queries）。
- 每条边的时间区间被线段树切成 $O(\\log Q)$ 段。
- 线段树 DFS 对每个 seg-node apply/rollback 一次，每条边被 apply $O(\\log Q)$
  次；DSU 无 path compression，`find` 是 $O(\\log N)$（union-by-rank 保证）。
- 总时间 $O((Q \\log Q) \\cdot \\log N)$。在常见竞赛分析里也写成
  $O((N + Q) \\log Q \\cdot \\alpha(N))$，严谨起见用 $\\log N$。
- 空间 $O(Q \\log Q)$（线段树存边副本）+ $O(N)$（DSU）。

### 正确性为什么成立

线段树的**区间覆盖不下推**保证：任何叶子 $t$ 到根的路径上 seg-node 的并集
恰好是 "所有在时刻 $t$ 活着的边"。DFS 时进入 node -> apply，离开 -> rollback，
是严格后进先出栈，rollback DSU（union-by-rank 无 compression）可以精确撤销
最后一次 union —— 互相匹配，invariant 成立。

### 错误解法对照

| 想法 | 为什么挂 |
|------|---------|
| 每个 query 从头 BFS/DFS | $O(Q \\cdot (N + E))$，$Q=10^5$ 就炸 |
| 在 compressed DSU 上撤销最后 union | path compression 改动了许多 parent 指针，单帧 history 存不下 |
| 删除时从 DSU 中"移除"一条边 | DSU 不存边，它存"已合并的连通分量"；无对应操作 |
| 用 link-cut tree 代替 rollback DSU | 能做，但在线 $O(\\log N)$，代码长 3x，45 分钟写不完 |
| 线段树下推 lazy 边到叶 | 边被复制到 $O(Q)$ 个叶节点，空间/时间 degrade 到 $O(Q^2)$ |
| 用 frozenset 作 alive key 但忘记 REMOVE 未配对的边 | 丢掉"始终活着"的边；结尾必须把未 REMOVE 的边 add 到 `[start, T-1]` |

### Follow-up 应答

**(A) 在线版本**
真正的在线 fully-dynamic connectivity 需要 Link-Cut Tree（Sleator-Tarjan）或
Euler Tour Tree；每 op $O(\\log N)$ 摊还。面试里表态"知道存在但 45 分钟实现
不现实"并简述 LCT 的 splay-on-preferred-path 思想即可。

**(B) 连通分量计数**
`RollbackDSU.components` 字段已经维护好；query 叶子直接读即可。rollback 也
要恢复 `components`（上面代码里 `comp_delta` 字段就是为此）。

**(C) 带权 / 动态 MST**
外层仍是时间线段树；DSU 换成 "Kruskal-style rollback DSU with weight bound" —
按权重排序在段内做，或者用 Holm-Lichtenberg 的 offline MST。

**(D) 空间优化**
如果 $Q \\log Q$ 的边副本内存吃紧：
1. 用小到大 merging + DSU-on-tree (DSU over DFS order)；
2. 或者把 seg-tree 存边换成存 edge-id，边表只存一份；
3. 或直接上 LCT，空间降到 $O(N + Q)$。

### 面试应答 checklist

1. **澄清**：在线还是离线？查询形式？`n`, `q` 的量级？边有重复吗？
2. **先说暴力**：每 query 从头 BFS，$O(Q(N+E))$，给出 WHY-too-slow。
3. **上主解法**：时间线段树 + rollback DSU，画一个 3-事件小例子手推。
4. **写 RollbackDSU**：强调 union-by-rank，**no path compression**。
5. **写 TimeSegTree.add**：强调区间覆盖不下推到叶。
6. **写 driver**：alive dict 映射 edge -> add-time，结尾补未 REMOVE 的边。
7. **复杂度**：$O(Q \\log Q \\log N)$ 时间，$O(Q \\log Q)$ 空间。
8. **Follow-up**：在线场景 -> LCT；组件计数 -> `components` 字段顺带维护。

### 与本题族的模板

- "**Offline x with deletions**" 往往可以化为 "时间轴线段树 + 带回滚的目标结构"。
  目标结构是 DSU（连通性）、可撤销 Treap（有序集合）、带 weight 的 DSU（MST）
  等。遇到 "查询 + 插入 + 删除" 的离线题，先问自己：删除发生的时间点已知吗？
  如果已知，segment-tree-over-time 这把万能钥匙可能就够了。
"""


def verify_examples() -> None:
    """Self-check on a hand-worked 4-node scenario.

    Timeline (node set = {0,1,2,3}):
      t=0: ADD 0-1
      t=1: QUERY 0-1        -> True
      t=2: ADD 1-2
      t=3: QUERY 0-2        -> True
      t=4: REMOVE 0-1
      t=5: QUERY 0-2        -> False  (chain broken at 0)
      t=6: ADD 2-3
      t=7: QUERY 1-3        -> True
      t=8: REMOVE 1-2
      t=9: QUERY 1-3        -> False
    """
    class RollbackDSU:
        def __init__(self, n: int) -> None:
            self.parent = list(range(n))
            self.rank = [0] * n
            self.components = n
            self.history: list = []

        def find(self, x: int) -> int:
            while self.parent[x] != x:
                x = self.parent[x]
            return x

        def union(self, a: int, b: int) -> None:
            ra, rb = self.find(a), self.find(b)
            if ra == rb:
                self.history.append(("noop",))
                return
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            old_rank_a = self.rank[ra]
            old_parent_b = self.parent[rb]
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
            self.components -= 1
            self.history.append(("merge", ra, old_rank_a, rb, old_parent_b))

        def snapshot(self) -> int:
            return len(self.history)

        def rollback(self, target: int) -> None:
            while len(self.history) > target:
                frame = self.history.pop()
                if frame[0] == "merge":
                    _, ra, old_rank_a, rb, old_parent_b = frame
                    self.rank[ra] = old_rank_a
                    self.parent[rb] = old_parent_b
                    self.components += 1

    class TimeSegTree:
        def __init__(self, n_time: int) -> None:
            self.n = n_time
            self.tree: list[list[tuple[int, int]]] = [[] for _ in range(4 * max(1, n_time))]

        def add(self, node: int, lo: int, hi: int, ql: int, qr: int,
                edge: tuple[int, int]) -> None:
            if qr < lo or hi < ql:
                return
            if ql <= lo and hi <= qr:
                self.tree[node].append(edge)
                return
            mid = (lo + hi) // 2
            self.add(2 * node, lo, mid, ql, qr, edge)
            self.add(2 * node + 1, mid + 1, hi, ql, qr, edge)

        def solve(self, node: int, lo: int, hi: int,
                  dsu: RollbackDSU, queries: dict, answers: dict) -> None:
            snap = dsu.snapshot()
            for u, v in self.tree[node]:
                dsu.union(u, v)
            if lo == hi:
                for qid, (u, v) in queries.get(lo, []):
                    answers[qid] = dsu.find(u) == dsu.find(v)
            else:
                mid = (lo + hi) // 2
                self.solve(2 * node, lo, mid, dsu, queries, answers)
                self.solve(2 * node + 1, mid + 1, hi, dsu, queries, answers)
            dsu.rollback(snap)

    events = [
        ("ADD", 0, 1),
        ("QUERY", 0, 1),
        ("ADD", 1, 2),
        ("QUERY", 0, 2),
        ("REMOVE", 0, 1),
        ("QUERY", 0, 2),
        ("ADD", 2, 3),
        ("QUERY", 1, 3),
        ("REMOVE", 1, 2),
        ("QUERY", 1, 3),
    ]
    T = len(events)
    alive: dict[frozenset, int] = {}
    seg = TimeSegTree(T)
    queries: dict[int, list] = {}
    answers: dict[int, bool] = {}
    qid = 0
    for t, ev in enumerate(events):
        kind = ev[0]
        if kind == "ADD":
            alive[frozenset((ev[1], ev[2]))] = t
        elif kind == "REMOVE":
            start = alive.pop(frozenset((ev[1], ev[2])))
            seg.add(1, 0, T - 1, start, t - 1, (ev[1], ev[2]))
        else:
            queries.setdefault(t, []).append((qid, (ev[1], ev[2])))
            qid += 1
    for key, start in alive.items():
        u, v = tuple(key)
        seg.add(1, 0, T - 1, start, T - 1, (u, v))

    dsu = RollbackDSU(4)
    seg.solve(1, 0, T - 1, dsu, queries, answers)
    got = [answers[i] for i in range(qid)]
    expected = [True, True, False, True, False]
    assert got == expected, (got, expected)

    # Brute-force cross-check: rebuild edge set at each query time
    def brute(events: list) -> list[bool]:
        edges: set[frozenset] = set()
        out: list[bool] = []
        for ev in events:
            kind = ev[0]
            if kind == "ADD":
                edges.add(frozenset((ev[1], ev[2])))
            elif kind == "REMOVE":
                edges.discard(frozenset((ev[1], ev[2])))
            else:
                u, v = ev[1], ev[2]
                adj: dict[int, set[int]] = {}
                for e in edges:
                    a, b = tuple(e)
                    adj.setdefault(a, set()).add(b)
                    adj.setdefault(b, set()).add(a)
                stack = [u]
                seen = {u}
                found = False
                while stack:
                    x = stack.pop()
                    if x == v:
                        found = True
                        break
                    for y in adj.get(x, ()):
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
                out.append(found)
        return out

    assert brute(events) == expected

    print("dynamic connectivity self-checks: all passed [OK]")


def upsert_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["union-find", "dsu", "segment-tree", "offline", "graph", "rollback"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google", "Uber"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (DESCRIPTION, NOTES, tags_json, "offline-segtree-rollback-dsu", "algorithm",
             company_json, SOURCE_BADGE, "hard", 1, pid),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, "
        "category, company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (TITLE, DESCRIPTION, NOTES, tags_json, "offline-segtree-rollback-dsu", "algorithm",
         company_json, SOURCE_BADGE, "hard", 1, now),
    )
    return cur.lastrowid


def main() -> None:
    verify_examples()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    pid = upsert_problem(cur)
    conn.commit()
    cur.execute(
        "SELECT id, title, length(description), length(notes) FROM problems WHERE id=?",
        (pid,),
    )
    r = cur.fetchone()
    print(f"problem id={r[0]} title={r[1]!r} desc_len={r[2]} notes_len={r[3]}")
    conn.close()


if __name__ == "__main__":
    main()
