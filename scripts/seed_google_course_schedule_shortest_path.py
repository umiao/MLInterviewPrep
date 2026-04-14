"""Seed Google coding prep: LC 207/210 Course Schedule + damage-node follow-up,
and a new custom Shortest Path (A->B) problem with all-pairs follow-up.

Task: T-P1-205.
- Append Chinese solution notes to problems 45 (LC 207) and 113 (LC 210) with
  Google damage-node follow-up (Dijkstra on DAG with node weights).
- Add Google company tag + 'Google 2026-04-17 prep' source badge.
- Insert new custom non-LC problem 'Shortest Path A->B (undirected, unweighted)'
  with Dijkstra/BFS baseline and all-pairs variants (Floyd-Warshall vs V x Dijkstra).
Idempotent: re-running does not duplicate tags or append notes twice.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"


def merge_json_tag(existing: str | None, tag: str) -> str:
    tags = json.loads(existing) if existing else []
    if tag not in tags:
        tags.append(tag)
    return json.dumps(tags, ensure_ascii=False)


def merge_source(existing: str | None, new: str) -> str:
    if not existing:
        return new
    parts = [s.strip() for s in existing.split(",") if s.strip()]
    if new not in parts:
        parts.append(new)
    return ", ".join(parts)


def append_notes(existing: str | None, addendum: str, marker: str) -> str:
    if existing and marker in existing:
        return existing
    if not existing:
        return addendum
    return existing.rstrip() + "\n\n---\n\n" + addendum


LC207_ADDENDUM = """## [Google 2026-04-17] Follow-up: 最小化受损节点数

### 问题变体
给定课程依赖图（DAG 保证），以及一个"受损节点"集合 $D \\subseteq V$。
求一个合法拓扑顺序 / 一条从源到终点的可行修课路径，使得经过的
"受损节点"数量最少。

### 关键转化：DAG 上带点权的最短路
- 每个节点点权 $w(u) = 1$ 若 $u \\in D$，否则 $0$。
- 路径代价 = $\\sum_{u \\in \\text{path}} w(u)$。
- 在 DAG 上求最小化受损节点数 = **拓扑序 + DP** 或 **Dijkstra**。

### 解法 A：拓扑序 + DP（推荐，$O(V+E)$）
```python
# dist[u] = 从任意 0-入度源到 u 的最少受损数
from collections import deque

def min_damage(n, prereq, damaged):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for c, p in prereq:
        adj[p].append(c); indeg[c] += 1
    INF = float('inf')
    dist = [INF] * n
    q = deque()
    for u in range(n):
        if indeg[u] == 0:
            dist[u] = 1 if u in damaged else 0
            q.append(u)
    while q:
        u = q.popleft()
        for v in adj[u]:
            cand = dist[u] + (1 if v in damaged else 0)
            if cand < dist[v]:
                dist[v] = cand
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return dist
```

### 解法 B：Dijkstra（更通用，$O((V+E)\\log V)$）
DAG 保证松弛是单向的，堆的 $\\log V$ 因子可省；但若边权非 0/1，或
图实际上不是严格 DAG（偶有回边），Dijkstra 更稳健。

### 为什么不能用 BFS？
- 普通 BFS 假设边权都相等；这里是"**点权**"不是边权，且 0/1 混合。
- 可以用 **0-1 BFS（双端队列）**：遇到 $w(v)=0$ 的邻居 `appendleft`，
  否则 `append`，时间 $O(V+E)$，等价于 Dijkstra on 0/1 weights.

### 面试口径
1. 澄清："受损"是节点属性还是边属性？是否允许绕过受损节点？路径起终点？
2. 先给 DAG 拓扑 DP 的 $O(V+E)$ 方案。
3. 若面试官追问"若图有环/边权不是 0-1"，升级到 Dijkstra。
4. 若追问"能否避免 heap"，给出 0-1 BFS。

### 关于 heap 的坑（原注释延伸）
原注释提醒：基础拓扑排序不能换 heap（优先队列会破坏"就绪即处理"的
语义，造成错误松弛）。但这里的 **damage-min DP** 已经用 `dist` 数组
单独存代价，用普通队列处理拓扑顺序 + DP 松弛是安全的。如果改用堆来按
`dist` 取最小（即 Dijkstra），需保证松弛时只用已确定最小 `dist` 的
节点——DAG 拓扑序天然满足这个条件。
"""

LC210_ADDENDUM = """## [Google 2026-04-17] Follow-up: 受损节点最少的合法拓扑序

### 变体描述
给定 prerequisites（DAG）和受损节点集合 $D$，不只返回**一个**合法拓扑序，
而是返回一个 **经过受损节点最少** 的合法拓扑序。

### 关键洞察
所有合法拓扑序都必须包含全部 $V$ 个节点（拓扑排序本身是节点的排列），
所以"总受损数 = $|D|$"是常数 —— 问题退化。**正确的提法应改为：从源点
$s$ 到终点 $t$ 的路径中，经过受损节点最少**（参见 LC 207 的同题附录）。

### 另一种合理变体：字典序最小且优先选非受损节点
若面试官坚持"在合法拓扑序集合里选"，可以约定字典序 tie-break：
- 维护两个队列：非受损就绪队列 $Q_0$、受损就绪队列 $Q_1$。
- 每次优先从 $Q_0$ 弹出（若空，再从 $Q_1$ 弹）。
- 等价于带优先级的 Kahn 算法；复杂度仍 $O(V+E)$。

```python
from collections import deque

def order_avoid_damaged(n, prereq, damaged):
    adj = [[] for _ in range(n)]; indeg = [0]*n
    for c, p in prereq:
        adj[p].append(c); indeg[c] += 1
    q0, q1 = deque(), deque()
    for u in range(n):
        if indeg[u] == 0:
            (q1 if u in damaged else q0).append(u)
    order = []
    while q0 or q1:
        u = q0.popleft() if q0 else q1.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                (q1 if v in damaged else q0).append(v)
    return order if len(order) == n else []
```

### 与 LC 207 follow-up 的联系
- 207 follow-up = DAG 上带点权的最短路（问**数值**：最少多少个受损节点）。
- 210 follow-up（本附录）= 选择合法拓扑序时的 tie-break 策略（问**顺序**）。
面试时务必先澄清是哪一种，不要强行把两者套在一起。

### 复杂度
- Time: $O(V+E)$
- Space: $O(V+E)$
"""

NEW_PROBLEM_TITLE = "Shortest Path A->B (undirected, unweighted)"
NEW_PROBLEM_DESC = """Given an undirected graph $G=(V,E)$ and two vertices $A, B$,
find the shortest path from $A$ to $B$. Follow-ups:

1. Return the path, not just the length.
2. If edges have non-negative weights, use Dijkstra.
3. Extend to **all-pairs** shortest paths: compare Floyd-Warshall $O(V^3)$ with
   running Dijkstra from every source ($O(V \\cdot (V+E) \\log V)$).
4. Path reconstruction via predecessor matrix.

Interview context: Google 2026-04-17 coding, as a warmup + progressive-depth
probe (BFS -> Dijkstra -> all-pairs -> path reconstruction)."""

NEW_PROBLEM_NOTES = """## Shortest Path A->B (Google 2026-04-17)

### 基线：无权图用 BFS, $O(V+E)$
```python
from collections import deque

def shortest_path(graph, A, B):
    if A == B:
        return [A]
    parent = {A: None}
    q = deque([A])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in parent:
                parent[v] = u
                if v == B:
                    # reconstruct
                    path = [B]
                    while parent[path[-1]] is not None:
                        path.append(parent[path[-1]])
                    return path[::-1]
                q.append(v)
    return None  # unreachable
```

### Follow-up 1: 边带非负权 → Dijkstra, $O((V+E)\\log V)$
```python
import heapq

def dijkstra(graph, A, B):
    dist = {A: 0}
    parent = {A: None}
    pq = [(0, A)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == B:
            break
        if d > dist.get(u, float('inf')):
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
    # reconstruct from parent
    if B not in dist:
        return None, None
    path = []
    cur = B
    while cur is not None:
        path.append(cur); cur = parent[cur]
    return dist[B], path[::-1]
```

陷阱：
- 节点可能被多次入堆；出堆时用 `if d > dist[u]: continue` 丢弃过期项。
- 负权边 Dijkstra **不适用**，需 Bellman-Ford $O(VE)$ 或 SPFA。

### Follow-up 2: All-pairs 最短路

#### 方案 A: Floyd-Warshall $O(V^3)$, $O(V^2)$ 空间
```python
def floyd_warshall(n, edges):
    INF = float('inf')
    dist = [[INF]*n for _ in range(n)]
    nxt  = [[None]*n for _ in range(n)]
    for i in range(n): dist[i][i] = 0
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w; nxt[u][v] = v
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j]  = nxt[i][k]
    return dist, nxt

def reconstruct(nxt, u, v):
    if nxt[u][v] is None: return []
    path = [u]
    while u != v:
        u = nxt[u][v]; path.append(u)
    return path
```

#### 方案 B: V 次 Dijkstra, $O(V \\cdot (V+E)\\log V)$
稀疏图 ($E = O(V)$) 首选 V × Dijkstra，总复杂度 $O(V^2 \\log V)$ ≪ $V^3$。
稠密图 ($E = \\Theta(V^2)$) Floyd 优（缓存友好、常数小、实现简单）。

| 场景 | 选择 | 原因 |
|------|------|------|
| 稀疏图 ($E \\ll V^2$) | V × Dijkstra | $V^2 \\log V$ vs $V^3$ |
| 稠密图 | Floyd-Warshall | 紧凑循环，缓存命中高 |
| 有负权、无负环 | Floyd 或 Bellman-Ford | Dijkstra 不支持负权 |
| 需要检测负环 | Bellman-Ford | Floyd: `dist[i][i] < 0` 也可 |
| 动态查询 (在线) | Johnson 算法 | $O(V E \\log V)$ 预处理，$O(\\log V)$ 查询 |

### Follow-up 3: Predecessor 矩阵重建
Floyd 的 `nxt[i][j]` 记录"从 i 走到 j 的**下一跳**"，递推重建路径。
也可以存 `pred[i][j]` = "j 的前驱"，则从 j 回溯到 i。两种都 $O(V^2)$ 空间。

### 复杂度总结
| 算法 | 时间 | 空间 | 负权 |
|------|------|------|------|
| BFS | $O(V+E)$ | $O(V)$ | 无权图 |
| Dijkstra | $O((V+E)\\log V)$ | $O(V)$ | 非负 |
| Bellman-Ford | $O(VE)$ | $O(V)$ | 允许，检测负环 |
| Floyd-Warshall | $O(V^3)$ | $O(V^2)$ | 允许，无负环 |
| Johnson | $O(V^2 \\log V + VE)$ | $O(V^2)$ | 允许 |

### 面试应答 checklist
1. 澄清：有向/无向？有权/无权？是否允许负权？需要路径还是仅长度？单源还是多源？
2. 从 BFS 开始给基线，逐步升级。
3. 主动提 path reconstruction（parent/nxt 数组）。
4. all-pairs 要会比较 Floyd vs V×Dijkstra 的场景选择。
5. 提一句 A* / 双向 BFS 作为启发式优化（大图场景）。
"""


def upsert_lc_addendum(cur: sqlite3.Cursor, problem_id: int, marker: str, addendum: str) -> None:
    cur.execute("SELECT notes, tags, company_tags, source FROM problems WHERE id=?", (problem_id,))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"problem id {problem_id} not found")
    notes, tags_json, company_json, source = row
    new_notes = append_notes(notes, addendum, marker)
    new_company = merge_json_tag(company_json, "Google")
    new_source = merge_source(source, SOURCE_BADGE)
    cur.execute(
        "UPDATE problems SET notes=?, company_tags=?, source=? WHERE id=?",
        (new_notes, new_company, new_source, problem_id),
    )


def upsert_new_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (NEW_PROBLEM_TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (
                NEW_PROBLEM_DESC,
                NEW_PROBLEM_NOTES,
                json.dumps(["graph", "shortest-path", "bfs", "dijkstra", "floyd-warshall"], ensure_ascii=False),
                "graph",
                "algorithm",
                json.dumps(["Google"], ensure_ascii=False),
                SOURCE_BADGE,
                "medium",
                1,
                pid,
            ),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, category, "
        "company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (
            NEW_PROBLEM_TITLE,
            NEW_PROBLEM_DESC,
            NEW_PROBLEM_NOTES,
            json.dumps(["graph", "shortest-path", "bfs", "dijkstra", "floyd-warshall"], ensure_ascii=False),
            "graph",
            "algorithm",
            json.dumps(["Google"], ensure_ascii=False),
            SOURCE_BADGE,
            "medium",
            1,
            now,
        ),
    )
    return cur.lastrowid


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    upsert_lc_addendum(cur, 45, "[Google 2026-04-17] Follow-up: 最小化受损节点数", LC207_ADDENDUM)
    upsert_lc_addendum(cur, 113, "[Google 2026-04-17] Follow-up: 受损节点最少的合法拓扑序", LC210_ADDENDUM)
    new_id = upsert_new_problem(cur)
    conn.commit()
    cur.execute("SELECT id, length(notes) FROM problems WHERE id IN (45, 113, ?)", (new_id,))
    for r in cur.fetchall():
        print(f"problem id={r[0]} notes_len={r[1]}")
    print(f"new/updated shortest-path problem id={new_id}")
    conn.close()


if __name__ == "__main__":
    main()
