"""Idempotent seed: LC 1135 Connecting Cities With Minimum Cost.

Adds the problem row (if missing), wires its follow-up link to LC 815,
and attaches the user's Chinese solution notes (Kruskal + union-find + heap).

Run: python scripts/add_lc1135_mst_with_notes.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_ID = 1135
TITLE = "Connecting Cities With Minimum Cost"
URL = "https://leetcode.com/problems/connecting-cities-with-minimum-cost/"
DIFFICULTY = "medium"
PATTERN = "graph"
TAGS = ["Union Find", "Graph", "Minimum Spanning Tree", "Heap", "Kruskal"]
FAMILY = "mst"

DESCRIPTION = """There are `N` cities numbered from 1 to `N`.

You are given `connections`, where each `connections[i] = [city1, city2, cost]` represents the cost to connect `city1` and `city2` together. A connection is bidirectional.

Return the minimum cost so that for every pair of cities, there exists a path of connections that connects those two cities together. The cost is the sum of the connection costs used. If the task is impossible, return -1.

**Example 1:** N = 3, connections = [[1,2,5],[1,3,6],[2,3,1]] -> 6

**Example 2:** N = 4, connections = [[1,2,3],[3,4,4]] -> -1 (disconnected)

**Constraints:** 1 <= N <= 10000; 1 <= connections.length <= 10000; 0 <= cost <= 1e5.
"""

NOTES = """## 题目定位
**最小生成树 (MST) 模板题**。所有边带权，选出权和最小的一组边使所有节点连通；连不通返回 `-1`。
与 LC 1584 Min Cost to Connect All Points 完全同构（后者是二维点距离自动生成边）。

## 解法：Kruskal + Union-Find + Heap
**核心思路**：按边权从小到大扫，每条边用并查集判断两端是否已在同一连通块；不在就合并并累加 cost，已在就跳过（否则形成环）。当合并次数 = `n-1` 时 MST 成环，提前返回。

**复杂度**：$O(E \\log E)$（堆排序边） + $O(E \\cdot \\alpha(N))$（路径压缩 + 按秩合并的 UF 近似 $O(E)$）；空间 $O(N + E)$。

## 关键实现点
1. **堆 vs 排序**：两者都可以（$O(E \\log E)$ 等价）。用 heap 的好处是"提前终止"——合并够 n-1 次就不再 pop 剩余边。
2. **1-indexed → 0-indexed**：`connections` 给的是 `1..N`，UF 数组用 0-based 索引，所以 `_find(src-1)` 减一。
3. **按秩合并 (union by rank)**：`rank[p_a] > rank[p_b]` 时交换，保证矮树挂到高树下；两树等高时被合并后的根 rank++。这是把 find 的最坏深度从 $O(N)$ 压到 $O(\\log N)$ 的关键。
4. **路径压缩 (path compression)**：`_find` 里 `unionFindSet[a] = unionFindSet[unionFindSet[a]]` 是"路径减半"版本（每次跳两步），比全路径压缩略弱但无递归；与按秩合并合用可达摊还 $O(\\alpha(N))$。
5. **提前返回条件**：`target == 1`（剩一个连通块）= 合并了 n-1 次 = MST 完成。
6. **不连通判断**：heap 耗尽仍 `target > 1` → 返回 `-1`。

## 正确性 re-check
- `n == 1` 时直接返回 0（无需任何边）。
- Kruskal 正确性来自切割性质 (cut property)：在任何切割中，最小权跨切边一定在某棵 MST 里。按升序扫描每条不成环边即是对任意切割取最小跨边，贪心正确。

## Prim vs Kruskal 怎么选
| 维度 | Kruskal | Prim |
| --- | --- | --- |
| 数据结构 | UF + 排好序的边 | 堆 + visited 集 |
| 稠密图 (E ≈ V²) | 排序 $E\\log E$ 慢 | 堆 $O(E + V\\log V)$ 更优 |
| 稀疏图 (E ≈ V) | $O(E \\log E)$ 很快 | 同量级 |
| 实现代码行数 | 依赖 UF 模板，~20 行 | 一个堆即可，~15 行 |
| 面试偏好 | 边列表给定 → Kruskal | 邻接表/矩阵 → Prim |

**本题边列表直接给，Kruskal 天然合适。**

## 易错点 (面试)
- 忘记 1-index 转 0-index → IndexError 或并错组。
- 路径压缩写成递归 → 深图可能爆 Python 递归栈（`sys.setrecursionlimit` 可救，但循环版本更稳）。
- 忘记判断"已同组跳过" → 形成环、cost 虚高。
- 忘记 `target == 1` 提前返回（功能上不影响结果，但面试官会追问"如果 E 远大于 N-1 怎么加速"）。

## Follow-up: LC 815 Bus Routes
LC 815 也是**最短连通**思路，但权重单位变成"换乘次数 (跳 bus 的次数)"，每条"边"是"同一条 bus 内任意两站之间"。
- **相同处**：都在问最小代价的连通方案。
- **关键差异**：LC 815 代价是 unweighted BFS 的层数，不是 MST；构图时把每条 bus 看成一个超级节点，或用 `stop -> routes[]` 邻接，BFS 层数就是答案。
- **思路迁移**：LC 1135 练熟 "UF + 按权取边"，LC 815 练 "层序 BFS + 访问过的 bus 不再进队"。两题都体现"把原问题抽象成图问题"是第一步；之后算法选型按权重类型分叉（有权 → Dijkstra/MST；无权 → BFS）。

## 一句话 pitch (面试)
> 这是标准 Kruskal MST：边按权进堆，UF 去环，合并 n-1 次就返回。提前终止条件是 target 降到 1，不连通返回 -1。与 Prim 相比稀疏图更简单、代码量小；Pinterest/Google 这类考察 union-find 的岗位是高频题。
"""


def _ensure_family_column(conn: sqlite3.Connection) -> None:
    """Ensure `family` column exists; it's added by an earlier migration."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(problems)")}
    if "family" not in cols:
        conn.execute("ALTER TABLE problems ADD COLUMN family TEXT")


def _link_follow_up(conn: sqlite3.Connection, parent_lc: int, follow_lc: int) -> None:
    """Record LC 815 as a follow-up of LC 1135 in problem_family_links if present."""
    # Only link if the table exists (feature flag: it may not be seeded yet)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if "problem_family_links" not in tables:
        return
    parent_row = conn.execute(
        "SELECT id FROM problems WHERE leetcode_id = ?", (parent_lc,)
    ).fetchone()
    follow_row = conn.execute(
        "SELECT id FROM problems WHERE leetcode_id = ?", (follow_lc,)
    ).fetchone()
    if not parent_row or not follow_row:
        return
    existing = conn.execute(
        "SELECT 1 FROM problem_family_links "
        "WHERE parent_id = ? AND child_id = ?",
        (parent_row[0], follow_row[0]),
    ).fetchone()
    if existing:
        return
    conn.execute(
        "INSERT INTO problem_family_links (parent_id, child_id, relation) "
        "VALUES (?, ?, ?)",
        (parent_row[0], follow_row[0], "follow_up"),
    )


def main() -> None:
    """Upsert LC 1135 with description + notes; link LC 815 as follow-up."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        _ensure_family_column(conn)

        row = conn.execute(
            "SELECT id, notes, description FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO problems "
                "(leetcode_id, title, url, difficulty, tags, pattern, "
                " source, priority, is_completed, description, "
                " description_source, notes, family) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    LC_ID,
                    TITLE,
                    URL,
                    DIFFICULTY,
                    json.dumps(TAGS, ensure_ascii=False),
                    PATTERN,
                    "user-added",
                    1,
                    1,
                    DESCRIPTION,
                    "leetcode.ca",
                    NOTES,
                    FAMILY,
                ),
            )
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            print(f"[ADDED] LC 1135 id={new_id}")
        else:
            pid, existing_notes, existing_desc = row
            fields: dict[str, str | int] = {}
            if not existing_notes:
                fields["notes"] = NOTES
            if not existing_desc:
                fields["description"] = DESCRIPTION
                fields["description_source"] = "leetcode.ca"
            fields["is_completed"] = 1
            fields["family"] = FAMILY
            sets = ", ".join(f"{k} = ?" for k in fields)
            conn.execute(
                f"UPDATE problems SET {sets} WHERE id = ?",
                (*fields.values(), pid),
            )
            print(f"[UPDATED] LC 1135 id={pid} fields={list(fields)}")

        _link_follow_up(conn, parent_lc=LC_ID, follow_lc=815)
        conn.commit()


if __name__ == "__main__":
    main()
