"""Seed Google R2 Coding problem: 文件与指令的级联故障 (Doc & Query Collapse).

User-provided content (Discord 2026-05-05). Bipartite-graph cascade
problem: Doc nodes + Query nodes, "contains" edges; an initial set of
broken queries triggers cascading damage (any Doc holding a bad Query
goes bad; any Query inside a bad Doc goes bad). Find all Docs that
end up bad.

Core insight: cascade is symmetric -> "Doc bad ⟺ in same connected
component as some initial bad Query". So this reduces to multi-source
reachability on the bipartite graph. Two clean solutions: BFS (preferred
for one-shot query) and Union-Find (preferred when relations are
incremental or queries are repeated against multiple bad-sets).

Per `feedback_pinterest_two_tier_notes`, the per-problem note lives in
`problems.notes` (rendered by ProblemDrawer via `db://<id>`). The R2
Coding Index doc 92 is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this
commit to add the new entry under a `### Graph / 连通分量` section.

Idempotent. Title is canonical key. Per Invariant 3 (CLAUDE.md), this
seed is the sole sanctioned write path for this row.

Run: python scripts/seed_google_r2_doc_query_collapse_20260505.py
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

TITLE = "文件与指令的级联故障"

DESCRIPTION = """\
系统中有两类对象：**文件 (Document)** 和**查询指令 (Query)**，文件包含若干指令，一个指令也可以出现在多个文件中。

- 给定一组初始损坏的指令
- 文件包含任意一个坏指令 → 文件损坏
- 文件损坏 → 它包含的所有指令都损坏
- 损坏会持续级联传播

求最终所有损坏的文件列表。

来源: Google R2 Coding 2026-05 用户 Discord 2026-05-05 提供。
"""

NOTES = """\
## 文件与指令的级联故障 (Doc & Query Collapse)

### 核心洞察

把 Doc 和 Query 都看作节点，"包含"关系看作无向边，整个系统就是一个**二部图**。损坏的传播沿边进行且方向对称：

> **一个 Doc 最终损坏 ⟺ 它与某个初始坏 Query 处于同一个连通分量。**

看穿这一层后，问题就是标准的"从一组源点出发的可达性"问题，用 BFS / DFS 即可。并查集也能做，但本题没必要。

### 解法 1: BFS (一次性求解首选)

维护两个 visited 集合（坏 Doc、坏 Query），交替推进：坏 Query 触发 Doc 损坏，坏 Doc 触发其内部 Query 损坏。

```python
from collections import defaultdict, deque

def find_broken_docs(docs: dict[str, list[str]],
                    broken_queries: list[str]) -> list[str]:
    # 反向索引：query -> 包含它的所有 doc
    q2d = defaultdict(list)
    for d, qs in docs.items():
        for q in qs:
            q2d[q].append(d)

    bad_q = set(broken_queries)
    bad_d: set[str] = set()
    queue = deque(broken_queries)

    while queue:
        q = queue.popleft()
        for d in q2d.get(q, ()):
            if d in bad_d:
                continue
            bad_d.add(d)
            # 此 doc 中所有未标记的 query 全部入队
            for nq in docs[d]:
                if nq not in bad_q:
                    bad_q.add(nq)
                    queue.append(nq)

    return list(bad_d)
```

### 复杂度

设 $N$ 为 Doc + Query 节点总数，$M$ 为所有包含关系的总数（即 `sum(len(qs) for qs in docs.values())`）。

- 时间：$O(N + M)$，每个节点和每条边各被访问一次
- 空间：$O(N + M)$，反向索引 + 两个 visited 集合

### 易错点

1. 初始坏 Query 可能压根不在任何 Doc 中，反向索引查不到要兜底（代码里用 `q2d.get(q, ())`）
2. visited 必须用 `set`，否则稠密关系下会退化到 $O(N \\cdot M)$
3. 同一 Query 在同一 Doc 重复出现要靠 visited 去重，不需额外预处理

### 解法 2: 并查集 (Union-Find)

把每个 Doc 与它包含的每个 Query union 起来，最后所有"含初始坏点的连通分量"中的 Doc 即为答案：

```python
def find_broken_docs_uf(docs, broken_queries):
    parent: dict = {}
    def find(x):
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(a, b):
        parent[find(a)] = find(b)

    for d, qs in docs.items():
        for q in qs:
            union(d, q)

    bad_roots = {find(q) for q in broken_queries if q in parent}
    return [d for d in docs if find(d) in bad_roots]
```

代码对称简洁，复杂度 $O((N+M) \\cdot \\alpha(N))$。**适合的场景**：

- 关系动态加入（在线场景）
- 需要用多组不同的初始坏点反复查询
- 需要查询"两个对象是否同属一个故障域"

一次性求解则首选 BFS，语义更直接。

### 相关模型

这个"双向级联 → 连通分量"的套路在很多题里反复出现：

- 病毒 / 谣言在社交网络中的传播
- 化学反应中的连锁反应物
- 编译依赖中的失效传播
- 等价类合并 / 朋友圈问题 (LC 547 Number of Provinces)

### 一句话总结

**只要传播是对称的，就转化为图的连通分量问题**: BFS 用于一次性求解（语义直接、代码短），Union-Find 用于动态加边或多组查询（结构通用、复杂度同阶）。
"""


PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "medium",
    "tags": ["graph", "bfs", "union-find", "bipartite", "connected-components"],
    "pattern": "bfs",
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
    """Insert-or-update the Doc & Query Collapse problem. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # CJK TITLE -> avoid cp1252 stdout crash
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_doc_query_collapse")
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
