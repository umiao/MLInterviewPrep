"""Seed 2 Google R2 Coding interview problems on bipartite matching + König.

User's Discord drop on 2026-05-05: 2 new R2 prep problems sharing the same
algorithmic backbone (bipartite matching + Hungarian algorithm + König
theorem). Both are reductions of "minimum row/column cover" and
"max non-attacking rooks (with blocking)" -- the latter is the segment-
decomposition refinement of the former.

  1. 屋顶补漏（最小行列覆盖）   row/column-board coverage of a 0/1 grid
  2. 棋盘放最多车（带阻挡型障碍）   max rooks with blocking obstacles

Two artefacts:
  * problems table: 2 rows. Per `feedback_pinterest_two_tier_notes`, the
    canonical home of the per-problem note is `problems.notes` -- the
    ProblemDrawer renders this when the user opens a `db://<id>` link.
  * doc 92 `[Google] R2 Coding Index` -- updated by re-running
    `seed_google_r2_coding_index_20260502.py` (which now references the 2
    new problems by title under a new "Bipartite Matching / König" section).

Idempotency:
  * Matched by `title` (canonical key for custom problems per CLAUDE.md
    `Idempotent seed pattern per row type`). If a row exists, UPDATE only
    when any field differs; otherwise UNCHANGED.
  * First clean run: 2 INSERTs. Second run on same content: 0 writes.

Invariant 3: this is the sole sanctioned write path for these 2 rows.

Run: python scripts/seed_google_r2_bipartite_matching.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

SOURCE_LABEL = "Google R2 Custom Note 2026-05"
COMPANY_TAGS = ["Google"]


# --------------------------------------------------------------------------
# Problem 1 -- 屋顶补漏（最小行列覆盖）
# --------------------------------------------------------------------------

ROOF_TITLE = "屋顶补漏（最小行列覆盖）"

ROOF_DESCRIPTION = r"""给定 $m \times n$ 的 0/1 矩阵 `grid`，$1$ 表示屋顶上的一个漏洞。允许两种木板：

- **整行木板** $1 \times n$：盖住第 $i$ 行的所有格子
- **整列木板** $1 \times m$：盖住第 $j$ 列的所有格子

求最少用多少块木板，使得每个 $1$ 至少被一块木板覆盖。

来源: Google R2 Coding 2026-05 prep（二分图匹配模板题）。
"""

ROOF_NOTES = r"""## 屋顶补漏（最小行列覆盖）

### 思路

每个洞 $(i, j)$ 必须由「第 $i$ 行」或「第 $j$ 列」之一覆盖。把行/列当成图的顶点：

| 题目     | 图论                |
|---------|---------------------|
| 行 $i$   | 左部点 $L_i$         |
| 列 $j$   | 右部点 $R_j$         |
| `grid[i][j] == 1` | 边 $(L_i, R_j)$ |
| 选一行/列盖住一个洞 | 选一个端点覆盖该边 |
| **最少木板数**     | **最小点覆盖**       |

这是一个二分图的最小点覆盖问题。**König 定理**：二分图中最小点覆盖 $=$ 最大匹配。所以答案 $=$ 这张二分图的最大匹配数。

求最大匹配的标准做法是匈牙利算法（**Hungarian algorithm**, Kuhn 1955）：反复找增广路，每找到一条匹配数 $+1$。

- **增广路**：起点和终点都未匹配的交替路（边在 unmatched / matched 间交替）。沿路翻转所有边的状态后，匹配数恰好 $+1$。
- 实现上从每个左部点 $u$ 出发跑 DFS：
    - 邻居 $v$ 未访问且空 $\to$ 直接配对
    - 邻居 $v$ 被某个 $u'$ 占了 $\to$ 递归让 $u'$ 去找新搭档；$u'$ 成功则 $u$ 接管 $v$
- `visited` 数组防止 DFS 在一次调用内死循环；**每个新的 $u$ 启动时必须重置** —— 之前的剪枝结论在新起点的图状态下不成立。

### 代码

```python
def min_boards(grid: list[list[int]]) -> int:
    '''Minimum row/column boards to cover all 1-cells in the grid.'''
    m, n = len(grid), len(grid[0])
    # adj[u] = list of column indices v with grid[u][v] == 1
    adj = [[j for j in range(n) if grid[i][j] == 1] for i in range(m)]
    match_col = [-1] * n  # match_col[v] = row currently paired with col v

    def dfs(u: int, visited: list[bool]) -> bool:
        for v in adj[u]:
            if visited[v]:
                continue
            visited[v] = True
            if match_col[v] == -1 or dfs(match_col[v], visited):
                match_col[v] = u
                return True
        return False

    matched = 0
    for u in range(m):
        if dfs(u, [False] * n):  # fresh visited per left-vertex
            matched += 1
    return matched
```

### 复杂度

- 匈牙利：$O(V \cdot E)$，最坏 $O(m^2 n)$ —— 每个左部点跑一次 DFS，每次扫整张图。
- **Hopcroft-Karp** 优化（一次找一组互不相交的最短增广路）：$O(E \sqrt{V})$。$E = O(mn)$，$V = O(m + n)$，最坏 $O(mn \sqrt{m + n})$。
- 空间 $O(V + E)$。

### 识别套路

看到「用最少的整行/整列覆盖某种标记」立刻应当反应到：**网格 $\to$ 二分图 $\to$ König $\to$ 最大匹配**。

类似题型的关键词：

- 行/列上的「全覆盖」操作（整行/整列）
- 求最少的行 + 列总数
- 元素只能被同行或同列影响

LeetCode 上对应的几道：

- LC 1349. Maximum Students Taking Exam（座位互斥可建 bipartite，König 求最大独立集）
- LC 2123. Minimum Operations to Remove Adjacent Ones in Matrix（同样最小点覆盖）
- LC 2392. Build a Matrix With Conditions（虽是拓扑序，但同属「行列偏序」族）

### 易错点

1. **`visited` 必须在外层 for 内重置**，不在 `dfs` 内 —— 每次新 $u$ 启动时图的状态不同，之前的剪枝结论失效。
2. **递归深度** 在 $m, n$ 大时可能爆 Python 默认 1000 栈，必要时改迭代或 `sys.setrecursionlimit`。
3. **`match_col[v] = u` 必须在递归成功后才执行** —— 不是「先占了再说」，是「让位的递归回来确认能让位才占」。把这行写在 `if` 之前是经典 bug，会破坏不变量。
4. 如果题目要求**输出方案**（具体哪些行/列被覆盖），要额外做一次交替路 BFS 还原 König 构造（从未匹配的左部点出发走交替路，标记到的左部点取**未访问的**进结果集，标记到的右部点取**访问过的**）。
5. 不要混淆「**用任意长度的木板**」—— 那是另一类问题（区间覆盖），König 不适用，要用 sweep / DP。
"""


# --------------------------------------------------------------------------
# Problem 2 -- 棋盘放最多车（带阻挡型障碍）
# --------------------------------------------------------------------------

ROOK_TITLE = "棋盘放最多车（带阻挡型障碍）"

ROOK_DESCRIPTION = r"""$n \times m$ 棋盘，部分格子是障碍 `#`。在空格中放尽可能多的车（rook），使任意两车互不攻击。**车的攻击会被障碍阻挡**（射线碰到 `#` 就停，所以同一行被障碍切开的两段可以各放一车）。

求能放的最大车数。

来源: Google R2 Coding 2026-05 prep（屋顶补漏的段细化推广）。
"""

ROOK_NOTES = r"""## 棋盘放最多车（带阻挡型障碍）

### 思路

**无障碍**情形：「每行最多一车 + 每列最多一车」直接对应行 $\leftrightarrow$ 列的二分图匹配，答案是 $\min(n, m)$（对角线即解）。

**有阻挡型障碍**之后，一行被 `#` 切成若干**段**（**segment**, 极大连续空格区间），每段独立约束「至多一车」；列方向同理。把约束的最小单位从「整行 / 整列」细化到「水平段 $H$ / 垂直段 $V$」即可：

- 每个空格 $(i, j)$ **恰好属于一个水平段 $H[i][j]$ 和一个垂直段 $V[i][j]$**
- 在 $(i, j)$ 放车 $\Leftrightarrow$ 在二分图 $(H, V)$ 中选边 $H[i][j] - V[i][j]$
- 段两两不冲突 $\Leftrightarrow$ 这是一个匹配（每段最多匹配一次）

问题归约为**二分图最大匹配**，照样上匈牙利。

### 算法

1. **横扫每行**：给每个空格分配水平段编号 `H[i][j]`；遇 `#` 重置 flag，下一个空格起新段
2. **竖扫每列**：类似分配 `V[i][j]`
3. **建边**：每个空格连一条 $H[i][j] \to V[i][j]$
4. **跑匈牙利**（或 Hopcroft-Karp）

### 代码

```python
def max_rooks(grid: list[list[str]]) -> int:
    '''Max non-attacking rooks where '#' blocks attacks.'''
    n, m = len(grid), len(grid[0])
    H = [[0] * m for _ in range(n)]
    V = [[0] * m for _ in range(n)]

    # 1. horizontal segment id (1-indexed; 0 reserved for "no segment")
    h_id = 0
    for i in range(n):
        new_seg = True
        for j in range(m):
            if grid[i][j] == '#':
                new_seg = True
            else:
                if new_seg:
                    h_id += 1
                    new_seg = False
                H[i][j] = h_id

    # 2. vertical segment id
    v_id = 0
    for j in range(m):
        new_seg = True
        for i in range(n):
            if grid[i][j] == '#':
                new_seg = True
            else:
                if new_seg:
                    v_id += 1
                    new_seg = False
                V[i][j] = v_id

    # 3. build H -> V edges (one edge per empty cell, naturally no duplicates)
    adj: list[list[int]] = [[] for _ in range(h_id + 1)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] != '#':
                adj[H[i][j]].append(V[i][j])

    # 4. Hungarian
    match = [0] * (v_id + 1)  # 0 means unmatched (segment ids start at 1)

    def dfs(u: int, vis: list[bool]) -> bool:
        for v in adj[u]:
            if vis[v]:
                continue
            vis[v] = True
            if match[v] == 0 or dfs(match[v], vis):
                match[v] = u
                return True
        return False

    ans = 0
    for u in range(1, h_id + 1):
        vis = [False] * (v_id + 1)
        if dfs(u, vis):
            ans += 1
    return ans
```

### 复杂度

- 段数 $|H|, |V| = O(nm)$（最坏每个空格自成一段，例如棋盘上每隔一格一个 `#`）
- 边数 $|E| = O(nm)$（每个空格贡献恰好一条边）
- 匈牙利：$O(V \cdot E) = O((nm)^2)$
- Hopcroft-Karp：$O(E \sqrt{V}) = O(nm \sqrt{nm})$
- 空间 $O(nm)$

### 关键观察

- **每个空格对应唯一的 $(H, V)$，天然无重边**，建边无需去重。
- 无障碍 $n \times n$ 情形下水平段数 $= $ 垂直段数 $= n$，最大匹配 $= n$（对角线即一组解）—— 与经典结论自洽。
- **建模口诀**：看放一个东西后会让多大范围互斥 —— **互斥单位就是二分图的左右顶点**。屋顶补漏里互斥单位是「整行 / 整列」；本题被障碍切开后互斥单位下沉到「水平段 / 垂直段」；如果哪天题目里阻挡只挡一个方向（比如 `#` 只挡水平不挡垂直），那左右部就变得不对称，需要重新分析互斥单位。
- 与**屋顶补漏**对照：那题求的是最少行 + 列盖所有洞（最小点覆盖 = 最大匹配，König）；本题求的是最多空格放车（直接的最大匹配）。**同一张二分图，两种语义**。

### 易错点

1. 段编号从 $1$ 起（用 $0$ 当作「未分配」哨兵）—— 便于 `match[v] == 0` 判空。也可以从 $0$ 起，但要换 `match` 初值为 $-1$。
2. 横扫时 `new_seg` flag 要在每行开头重置；竖扫时在每列开头重置。漏一个会把上一行/列尾段错误地连到下一行/列首段。
3. 边的方向：标准实现里 DFS 从 $H$ 端发起，所以 `adj` 以 $H$ 为下标。反过来也行，但要保证 `match` 数组对应的是 DFS 的**对侧端点**。
4. 障碍如果是「**软**阻挡」（车能穿过 `#` 但不能停在 `#`），算法完全不同 —— 退化回行/列二分图，障碍无效。读题时务必看清。
5. 障碍单元自己**不参与建模**（不是顶点也不是边），别误把它编号为段。
"""


# --------------------------------------------------------------------------
# Per-row specs
# --------------------------------------------------------------------------

PROBLEMS_SPEC: list[dict] = [
    {
        "title": ROOF_TITLE,
        "leetcode_id": None,
        "url": None,
        "difficulty": "medium",
        "tags": [
            "graph",
            "bipartite-matching",
            "hungarian",
            "konig",
            "min-vertex-cover",
        ],
        "pattern": "bipartite-matching",
        "family": "bipartite-matching",
        "category": None,
        "source": SOURCE_LABEL,
        "company_tags": COMPANY_TAGS,
        "is_completed": 1,
        "description": ROOF_DESCRIPTION,
        "notes": ROOF_NOTES,
    },
    {
        "title": ROOK_TITLE,
        "leetcode_id": None,
        "url": None,
        "difficulty": "hard",
        "tags": [
            "graph",
            "bipartite-matching",
            "hungarian",
            "segment-decomposition",
        ],
        "pattern": "bipartite-matching",
        "family": "bipartite-matching",
        "category": None,
        "source": SOURCE_LABEL,
        "company_tags": COMPANY_TAGS,
        "is_completed": 1,
        "description": ROOK_DESCRIPTION,
        "notes": ROOK_NOTES,
    },
]


# --------------------------------------------------------------------------
# Upsert logic (matches seed_google_r2_three_problems_20260503.py)
# --------------------------------------------------------------------------


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
    """Insert-or-update the 2 bipartite-matching problems. Return 0 on success."""
    # Force stdout/stderr to UTF-8 -- titles contain CJK and Windows console
    # default cp1252 will crash before commit if we don't reconfigure.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_google_r2_bipartite")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        for spec in PROBLEMS_SPEC:
            pid, action = upsert_problem(conn, spec)
            print(f"[{action}] problems.id={pid} title={spec['title']!r}")
        conn.commit()

    print(
        "[OK] done -- next: re-run "
        "scripts/seed_google_r2_coding_index_20260502.py "
        "to refresh doc 92 index (now references these 2 problems under the "
        "new 'Bipartite Matching / König' section)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
