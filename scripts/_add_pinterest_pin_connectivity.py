"""Add Pinterest Pin Connectivity custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC, recurring).

Pinterest stores relationships between pins, boards, and users as a graph.
Given a stream of relationship edges and a sequence of connectivity queries
(``areConnected(a, b)``), determine whether two pins / boards / users are
reachable from each other through the relationship graph.

Canonical lean answer: Union-Find (Disjoint Set Union) with path compression
and union-by-rank -- near O(alpha(n)) amortized per op. Fallback BFS/DFS if
edge removals are in scope.

Task: T-P1-401
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Pin Connectivity on a Pinterest Relationship Graph"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["Graph", "Union-Find", "BFS", "DFS", "Connectivity", "Design"])
PATTERN = "Dynamic connectivity via Union-Find (path compression + union by rank)"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11] Pinterest's backend stores a heterogeneous graph of
pins, boards, and users. An edge connects two nodes when there is a direct
relationship, e.g.:
  - pin P is saved to board B          (pin-board edge)
  - user U follows board B             (user-board edge)
  - board B1 was cloned from board B2  (board-board edge)

Design a ConnectivityService with:
  - addEdge(a, b)           -- record a new relationship edge (undirected).
  - areConnected(a, b)      -- return True iff a and b lie in the same
                                connected component of the relationship graph.

Follow-ups discussed:
  (a) componentSize(x) and countComponents() in O(1) amortized.
  (b) Edge removals: what changes? (Union-Find alone no longer works.)
  (c) Shortest-hop distance between a and b (not just connectivity).
  (d) Scale: billions of edges streamed; sharded workers; eventual consistency.
"""

SOLUTION_TAG = "[Pinterest Pin-Connectivity Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11)

Given a stream of undirected edges over a heterogeneous pin/board/user graph,
answer online connectivity queries ``areConnected(a, b)``.

## Canonical Solution -- Union-Find / DSU (recommended)

**Data**:
  - ``parent: dict[node, node]`` -- parent pointer in the DSU forest.
  - ``rank:   dict[node, int]``  -- upper bound on tree height (for union-by-rank).
  - ``size:   dict[node, int]``  -- component size rooted at this node (for
                                   ``componentSize``).

**find(x)**: climb to root with **path compression** -- every node on the
climbing path is re-pointed directly to the root.

**union(a, b)**: link the shorter tree under the taller (union-by-rank).
Merge sizes into the new root.

**areConnected(a, b)**: ``find(a) == find(b)``.

```python
class ConnectivityService:
    def __init__(self) -> None:
        self.parent: dict = {}
        self.rank:   dict = {}
        self.size:   dict = {}
        self._components = 0

    def _ensure(self, x) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x]   = 0
            self.size[x]   = 1
            self._components += 1

    def find(self, x):
        self._ensure(x)
        # Iterative path compression.
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def add_edge(self, a, b) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # Union by rank.
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra]  += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self._components -= 1

    def are_connected(self, a, b) -> bool:
        return self.find(a) == self.find(b)

    def component_size(self, x) -> int:
        return self.size[self.find(x)]

    def count_components(self) -> int:
        return self._components
```

Complexity: ``add_edge``, ``are_connected`` amortized near O(alpha(N))
(inverse Ackermann -- effectively constant). Space O(N).

## Alternative -- BFS/DFS per query

Maintain ``adj: dict[node, set[node]]``. On ``areConnected(a, b)``, BFS from
``a`` until we reach ``b`` or exhaust the component.

Pros: trivially handles **edge removal** (just delete from adjacency sets).
Cons: every query is O(V+E) in the worst case. No good if queries dominate.

Good default only when (a) removals are in scope, or (b) you also need the
**path** between ``a`` and ``b``, not just connectivity. In all other cases,
DSU beats it.

## Follow-up (a) -- componentSize + countComponents

Already covered above: maintain ``size`` on the root and a running
``_components`` counter decremented on every successful union. Both queries
are O(1).

## Follow-up (b) -- Edge removals

DSU does **not** support removals efficiently -- you cannot "un-merge" two
components without a full rebuild. Options:

1. **Offline trick (Link-Cut Tree / Euler tour)**: if you can see the whole
   edge stream up front, process queries in reverse, turning deletions into
   insertions. Works only when the workload is offline / batched.
2. **Online dynamic connectivity (Holm/Lichtenberg/Thorup)**: supports insert
   + delete + query in ``O(log^2 N)`` amortized. Complex to implement --
   mention it exists, but do NOT write it on a whiteboard unless asked.
3. **Adjacency + BFS**: simplest fallback. Acceptable only if the graph /
   queries are small.

The "right" answer in the interview is: clarify whether deletions happen.
If yes, propose (1) for batch workloads or fall back to adjacency + BFS.

## Follow-up (c) -- Shortest-hop distance

DSU only tells you "connected or not", never distance. For distance:
  - **Unweighted BFS** from ``a`` yields shortest hops. O(V+E) worst case.
  - For repeated queries on a static graph, precompute **BFS trees** per
    heavy node, or use **bidirectional BFS** (roughly sqrt of single-source).
  - True all-pairs distance on a billion-edge graph is infeasible;
    Pinterest-scale systems approximate via random walks / embeddings
    (e.g. PinSage) rather than exact BFS.

## Follow-up (d) -- Scale (sharded, streaming)

- **Partition the node space** by hash(node) across workers. Each worker
  owns a shard of the DSU.
- Cross-shard unions require a coordination message (two-phase: both shards
  ``find`` locally, then a leader merges). Use a **global component id**
  (e.g. a per-component UUID) so that ``find`` returns the same id regardless
  of which shard answers.
- **Eventual consistency**: edges may arrive out of order. Safe because
  unions are associative and commutative -- applying them in any order
  produces the same final partition.
- For **read-mostly** workloads, snapshot the partition into a flat
  ``node -> component_id`` map and push it to a KV cache; queries become O(1)
  cache lookups.

## Edge Cases

1. Self-edge ``add_edge(a, a)`` -- must be a no-op; DSU handles via
   ``ra == rb`` early return.
2. Query on an unseen node -- ``_ensure`` creates a singleton component;
   ``are_connected(x, x) == True`` by definition.
3. Duplicate edge ``add_edge(a, b)`` twice -- second call is a no-op (same root).
4. Heterogeneous node types (pin 123 vs board 123) -- use tagged keys
   (``("pin", 123)``) so hash collisions across types are impossible.
5. Empty graph -- ``count_components() == 0``; first ``find`` bumps to 1.

## Chinese Notes (中文解析)

**题意**: Pinterest 后端把 pin / board / user 存成一张异构图, 边表示直接关系
(比如一枚 pin 被存到某 board, 某 user 关注某 board)。实现:
  - ``addEdge(a, b)`` 新增一条无向边,
  - ``areConnected(a, b)`` 判断两点是否在同一连通分量。

**核心选型**: **并查集 (Union-Find / DSU)**。路径压缩 + 按秩合并后, 单次操作
均摊接近 O(alpha(N)), 几乎是 O(1)。这是"只有插入边 + 连通性查询"这类问题的
标准答案。

**为什么不用 BFS/DFS 每次查**:
- BFS/DFS 每次查询是 O(V+E), 查询量大时完全扛不住。
- 只有当问题明确**要求支持边删除**, 或**要求返回最短路径**, 才放弃 DSU 改
  邻接表 + BFS。

**实现要点**:
1. ``find`` 里必须做路径压缩, 否则退化成链表 O(N)。
2. ``union`` 按秩 (或按大小) 合并, 否则单路径压缩不足以保证复杂度。
3. 维护 ``size[root]`` 和全局 ``components`` 计数, 使 ``componentSize``
   和 ``countComponents`` 都是 O(1)。

**follow-up 常见问题**:
- **支持删边?** DSU 不擅长删除。方案: (1) 离线把删除反向成插入, (2) 上真正
  的 dynamic connectivity 数据结构 (``O(log^2 N)`` 摊还), (3) 退回邻接表
  + BFS。面试时先问删除是否在 scope 内。
- **最短跳数?** 走 BFS, DSU 不给距离信息。大规模时 Pinterest 用 random walk
  / 图嵌入 (如 PinSage) 做近似, 而不是精确 BFS。
- **十亿级边怎么分片?** 按 ``hash(node)`` 分 shard, 每个 worker 一个本地 DSU,
  跨 shard union 靠两阶段协调, 用全局 component id 保证查询一致。
- **异构节点**: 用 ``("pin", 123)`` 这样的 tagged key 避免 pin 和 board 的
  id 撞车。

**面试交付节奏**:
1. 画两三条边的样例, 说清楚"连通"这一本质;
2. 先问澄清: 会不会删边? 会不会问距离? 是否要 ``componentSize``?
3. 给 DSU 方案 + 写代码 + 说复杂度 (路径压缩 + 按秩);
4. 讨论 alternative (BFS) 的适用场景与边删除 follow-up;
5. 聊规模: 分片 DSU + 缓存到 KV;
6. 收尾: 和 PinSage / 随机游走 的工程替代方案 (在 Pinterest 上下文里加分)。

## Self-Test (smoke)

```python
cs = ConnectivityService()

# pins/boards/users tagged to avoid id collisions across types.
pinA   = ("pin", "A")
pinB   = ("pin", "B")
board1 = ("board", 1)
board2 = ("board", 2)
userU  = ("user", "U")

# pinA and pinB both saved to board1 -> connected via board1.
cs.add_edge(pinA, board1)
cs.add_edge(pinB, board1)
assert cs.are_connected(pinA, pinB) is True
assert cs.component_size(pinA) == 3  # {pinA, pinB, board1}

# board2 is a separate component until we link it.
cs.add_edge(("pin", "C"), board2)
assert cs.are_connected(pinA, board2) is False
assert cs.count_components() == 2

# userU follows board1 -> joins the big component.
cs.add_edge(userU, board1)
assert cs.are_connected(userU, pinB) is True
assert cs.component_size(userU) == 4

# Clone edge: board2 cloned from board1 -> merges components.
cs.add_edge(board2, board1)
assert cs.are_connected(pinA, ("pin", "C")) is True
assert cs.count_components() == 1

# Duplicate add_edge is a no-op.
before = cs.count_components()
cs.add_edge(pinA, board1)
assert cs.count_components() == before

# Self-edge is a no-op.
cs.add_edge(pinA, pinA)
assert cs.are_connected(pinA, pinA) is True

# Unseen node -> singleton, not connected to anything else.
assert cs.are_connected(("pin", "Z"), pinA) is False
```
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, notes FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now(timezone.utc).isoformat()

    if row is None:
        cur.execute("SELECT MAX(id) FROM problems")
        next_id = (cur.fetchone()[0] or 0) + 1
        cur.execute(
            """
            INSERT INTO problems (
                id, leetcode_id, title, url, difficulty, tags, pattern,
                category, source, company_tags, priority, is_completed,
                comfort_level, created_at, description, notes
            ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """,
            (
                next_id,
                TITLE,
                DIFFICULTY,
                TAGS,
                PATTERN,
                CATEGORY,
                SOURCE,
                COMPANY_TAGS,
                PRIORITY,
                now,
                DESCRIPTION,
                NOTES,
            ),
        )
        print(f"[INSERT] id={next_id} title={TITLE!r}")
    else:
        pid, existing_notes = row
        if existing_notes and SOLUTION_TAG in existing_notes:
            print(f"[SKIP] id={pid} already has canonical solution")
        else:
            merged = (existing_notes + "\n\n---\n\n" + NOTES) if existing_notes else NOTES
            cur.execute(
                "UPDATE problems SET notes = ?, description = ? WHERE id = ?",
                (merged, DESCRIPTION, pid),
            )
            print(f"[UPDATE] id={pid} notes appended")

    conn.commit()
    conn.close()


def _smoke_test() -> None:
    """Execute the canonical solution + self-tests embedded in NOTES."""
    from collections import defaultdict  # noqa: F401  (kept for parity)

    class ConnectivityService:
        def __init__(self) -> None:
            self.parent: dict = {}
            self.rank:   dict = {}
            self.size:   dict = {}
            self._components = 0

        def _ensure(self, x) -> None:
            if x not in self.parent:
                self.parent[x] = x
                self.rank[x]   = 0
                self.size[x]   = 1
                self._components += 1

        def find(self, x):
            self._ensure(x)
            root = x
            while self.parent[root] != root:
                root = self.parent[root]
            while self.parent[x] != root:
                self.parent[x], x = root, self.parent[x]
            return root

        def add_edge(self, a, b) -> None:
            ra, rb = self.find(a), self.find(b)
            if ra == rb:
                return
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            self.parent[rb] = ra
            self.size[ra]  += self.size[rb]
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
            self._components -= 1

        def are_connected(self, a, b) -> bool:
            return self.find(a) == self.find(b)

        def component_size(self, x) -> int:
            return self.size[self.find(x)]

        def count_components(self) -> int:
            return self._components

    cs = ConnectivityService()
    pinA   = ("pin", "A")
    pinB   = ("pin", "B")
    board1 = ("board", 1)
    board2 = ("board", 2)
    userU  = ("user", "U")

    cs.add_edge(pinA, board1)
    cs.add_edge(pinB, board1)
    assert cs.are_connected(pinA, pinB) is True
    assert cs.component_size(pinA) == 3

    cs.add_edge(("pin", "C"), board2)
    assert cs.are_connected(pinA, board2) is False
    assert cs.count_components() == 2

    cs.add_edge(userU, board1)
    assert cs.are_connected(userU, pinB) is True
    assert cs.component_size(userU) == 4

    cs.add_edge(board2, board1)
    assert cs.are_connected(pinA, ("pin", "C")) is True
    assert cs.count_components() == 1

    before = cs.count_components()
    cs.add_edge(pinA, board1)
    assert cs.count_components() == before

    cs.add_edge(pinA, pinA)
    assert cs.are_connected(pinA, pinA) is True

    assert cs.are_connected(("pin", "Z"), pinA) is False
    print("[SMOKE] all 9 assertions passed")


if __name__ == "__main__":
    _smoke_test()
    upsert()
