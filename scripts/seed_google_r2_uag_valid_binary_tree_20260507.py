"""Seed Google R2 Coding problem: 判断 Undirected Acyclic Graph 是否为 Valid Binary Tree.

User-provided content (Discord 2026-05-07 msg 1501766944410439730).
Main: given an undirected ACYCLIC graph, decide whether it is a valid binary
tree (and output a root). Follow-up: nodes are colored black/white -- decide
whether some root choice produces BFS layers in which every depth is
mono-colored.

Core insight (main): under the acyclic precondition, valid binary tree iff
edges == N-1 (equivalent to connected, since an N-node forest with k
components has N-k edges) AND max_degree <= 3 (non-root: 1 parent + <=2
children; root: <=2 children). Any degree-<=2 vertex is a legal root; pick
a leaf for simplicity.

Core insight (follow-up): siblings (and all cousins at the same depth) must
share color. Brute force tries each degree-<=2 root with a BFS that aborts
on a mixed-color layer -> O(N^2). Optimization sketches: rerooting DP
maintaining per-depth color sets incrementally; or "forbidden region" per
mismatched color pair via path-midpoint analysis (only mismatched pairs at
even distance constrain root placement).

Per `feedback_pinterest_two_tier_notes`, the per-problem note lives in
`problems.notes` (rendered by ProblemDrawer via `db://<id>`). The R2 Coding
Index doc 92 is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this commit
to add the new entry under a new `### Tree / Graph Validation` section.

Idempotent. Title is canonical key. Per Invariant 3 (CLAUDE.md), this seed
is the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_uag_valid_binary_tree_20260507.py
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

TITLE = "Undirected Acyclic Graph 是否为 Valid Binary Tree"

DESCRIPTION = """\
**主问题**: 给定一个**无向无环**图 (Undirected Acyclic Graph, UAG), 判断它是不是一棵 valid binary tree。是的话, 同时输出一个合法的 root。

**Follow-up**: 每个节点带 black/white 颜色, 判断是否存在某种 root 选择, 使得从该 root 出发 BFS 后, 同一层 (depth) 的所有节点颜色一致。

来源: Google R2 Coding 2026-05 用户 Discord 2026-05-07 提供。
"""

NOTES = """\
## 判断 Undirected Acyclic Graph 是否为 Valid Binary Tree

### 主问题

#### 判定条件

输入已保证无环 (acyclic)。在此前提下, 是 valid binary tree 当且仅当:

1. **边数 = $N - 1$** (等价地: 图连通)
2. **每个点 degree $\\le 3$**

> **关键等价**: 无环 + 边数 = $N-1$ ⇔ 无环 + 连通 ⇔ 是树
> 因为 $N$ 个点 $k$ 个连通块的森林必有 $N-k$ 条边。

degree $\\le 3$ 的依据: 非根点 = 1 parent + $\\le 2$ children; root = $\\le 2$ children。

#### Root 选择

任意 **degree $\\le 2$** 的点都可以做 root。最简单: 挑一个叶子 (degree = 1)。

- $N \\ge 2$ 的树必有叶子, 所以合法 root 一定存在
- $N = 1$ 单点自身即 root
- 面试时可主动澄清: "任意合法 root, 还是特定的 (如 tree center)?"

#### 算法

```
1. 若 edge_count != N - 1   -> false
2. 若 max_degree > 3         -> false
3. 找任一 degree <= 2 的点作为 root
4. (可选) 从 root BFS 验证连通性 + 无环 (acyclic 已保证, 主要校验连通)
```

```python
from collections import defaultdict, deque

def is_valid_binary_tree(n: int, edges: list[tuple[int, int]]):
    \"\"\"Return (ok, root_or_None). Assumes the input graph is acyclic.\"\"\"
    if n == 0:
        return False, None
    if n == 1:
        return len(edges) == 0, 0  # 单点

    if len(edges) != n - 1:
        return False, None

    deg = [0] * n
    adj = defaultdict(list)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        adj[u].append(v)
        adj[v].append(u)

    if max(deg) > 3:
        return False, None

    # 任选一个 degree <= 2 的点; N>=2 树必有叶子, 一定存在
    root = next(i for i, d in enumerate(deg) if d <= 2)

    # 可选: BFS 验证连通 (输入保证无环 + 边数=N-1 时必然连通, 防御性校验)
    seen = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(seen) != n:
        return False, None

    return True, root
```

#### 复杂度

- 时间: $O(N + E) = O(N)$ (因为 $E = N-1$)
- 空间: $O(N)$

---

### Follow-up: 每层同色

#### 思路 (暴力 $O(N^2)$)

1. 全局 check: max degree $\\le 3$, 否则 false (前置条件不满足直接拒)
2. 候选 root 集合 = 所有 degree $\\le 2$ 的点
3. 对每个候选做 BFS:
   - 按层收集颜色
   - 任一层出现混色 -> 该 root 不合法, 早退
   - 所有层单色 -> 找到答案

```python
def find_mono_layer_root(n, edges, color):
    deg = [0] * n
    adj = defaultdict(list)
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
        adj[u].append(v); adj[v].append(u)
    if max(deg) > 3:
        return None

    for root in range(n):
        if deg[root] > 2:
            continue
        # BFS, 按层校验颜色
        seen = {root}
        layer = [root]
        ok = True
        while layer and ok:
            c = color[layer[0]]
            nxt = []
            for u in layer:
                if color[u] != c:
                    ok = False
                    break
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        nxt.append(v)
            layer = nxt
        if ok and len(seen) == n:
            return root
    return None
```

**复杂度**: $O(N)$ per BFS $\\times O(N)$ candidates = **$O(N^2)$**, 空间 $O(N)$。

#### 关键观察

- 相邻点 depth 差 1, 必在不同层, 对颜色无约束
- **兄弟节点 (同 parent) 必须同色** -- depth 相同
- 更强: **所有同 depth 的点都必须同色** (包括堂兄弟)

#### 优化方向 (口头提一下即可, 不必现场实现)

**思路 A: 换根 DP (Rerooting)**

先以任意点为根 BFS, 拿到一份"每层颜色集合" base 状态。换根 (从 $u$ 切到邻居 $v$) 时, 子树的层结构相对位移 $\\pm 1$, 增量维护"每层颜色集合"。理论 $O(N)$, 实现繁琐, 状态合并细节多。

**思路 B: 异色对的禁止区域**

对每对**异色** $(u, v)$:
- 若 $\\text{dist}(u, v)$ 是奇数: 任意 root 下 $u, v$ 都不同层 -> 无约束
- 若 $\\text{dist}(u, v)$ 是偶数: 设 $m$ 为 $u\\text{-}v$ 路径中点 (节点)。当 root 落在"去掉 $m$ 后不含 $u$ 也不含 $v$ 的子树 $\\cup \\{m\\}$"时, $u, v$ 同层 -> 这片区域禁止

合法 root = 所有禁止区域的补集。异色对最坏 $O(N^2)$ 个, 朴素实现不省, 但面试官压你优化时是个不错的口子。

---

### 易错点 / Checklist

- [ ] 别忘了 root 的 degree 限制是 **$\\le 2$** (不是 $\\le 3$)
- [ ] 单独处理 $N = 1$ 的 corner case
- [ ] 强调 "无环 + $N-1$ 条边 ⇔ 连通", 避免冗余检查
- [ ] Follow-up 里候选 root 限定在 degree $\\le 2$, 否则浪费一倍时间
- [ ] BFS 检查同层颜色时一旦混色立刻 break
- [ ] 输入保证无环这一前提要复述确认 -- 否则需要先做无环检查 (BFS / DFS 找回边)

---

### 复杂度总结

| 问题 | 时间 | 空间 |
|------|------|------|
| 主问题 | $O(N)$ | $O(N)$ |
| Follow-up 暴力 | $O(N^2)$ | $O(N)$ |
| Follow-up 换根 DP | $O(N)$ | $O(N)$ |

### 一句话总结

主问题靠"acyclic + edges=$N-1$ + max_degree$\\le 3$"三件套秒杀; Follow-up 暴力 $O(N^2)$ 上手, 优化口子是**换根 DP** 或**按异色对划禁止区域**。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": [
        "graph", "tree", "bfs", "tree-validation",
        "degree-counting", "rerooting",
    ],
    "pattern": "tree-validation",
    "family": "graph",
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
    """Insert-or-update the UAG valid binary tree problem. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_uag_valid_binary_tree")
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
