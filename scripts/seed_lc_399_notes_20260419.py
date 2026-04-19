"""Seed: T-P1-520 -- Add LC 399 Evaluate Division dual-solution notes.

Marks problems.id=227 (leetcode_id=399, "Evaluate Division") completed,
attaches Chinese-prose notes covering both Weighted Union-Find and BFS
solutions verbatim, sets family='union_find_weighted' and links to
framework_node_id=51 (Union-Find).

Backs up the DB to data/mle_prep.db.bak.YYYYMMDD_HHMMSS before mutating.
Idempotent: a SHA-256 hash of the notes payload is compared against the
existing row -- a second run prints [SKIP] when nothing changed.
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

LEETCODE_ID = 399
EXPECTED_DB_ID = 227
FAMILY_SLUG = "union_find_weighted"
FRAMEWORK_NODE_ID = 51  # Union-Find

NOTES = """## Evaluate Division (LC 399)

### 问题本质

给一组等式 `a / b = k`，再给一批查询 `x / y`，要求返回比值或 -1.0（变量未出现或不连通）。把每条等式视为图的一条**带权有向边**：`a -> b` 边权 `k`，反向 `b -> a` 边权 `1/k`。查询 `x / y` 等价于"x 到 y 的任意路径上边权累乘是多少"。该问题是"**带权并查集**"和"**图上路径累乘查询**"的双模板题，面试现场最稳的策略是先把图建出来 (`O(E)`)，再用 BFS/DFS 累乘 (`O(Q*(V+E))`)；时间够、追问性能时再改成 Weighted Union-Find，把每次查询摊到 `O(alpha(N))`。

### Solution 1 -- Weighted Union-Find (最优、面试加分)

每个节点 `x` 维护两个量：`parent[x]`（所在树的父节点）与 `weight[x]`（**x / parent[x] 的比值**）。`find(x)` 走到根 `root` 时，路径压缩同时把每条边权累乘到 `weight[x]`。union 把两棵树挂到一起时，根据 `a/b = k` 推出两根之间的比值。

```python
class Solution:
    def calcEquation(self, equations, values, queries):
        parent, weight, rank = {}, {}, {}
        def add(x):
            if x not in parent:
                parent[x] = x; weight[x] = 1.0; rank[x] = 0
        def find(x):
            if parent[x] != x:
                root = find(parent[x])
                weight[x] *= weight[parent[x]]   # 路径压缩时把边权累乘
                parent[x] = root
            return parent[x]
        def union(a, b, k):  # a/b = k
            add(a); add(b)
            rootA, rootB = find(a), find(b)
            if rootA == rootB: return
            if rank[rootA] < rank[rootB]:
                parent[rootA] = rootB
                weight[rootA] = k * weight[b] / weight[a]
            elif rank[rootA] > rank[rootB]:
                parent[rootB] = rootA
                weight[rootB] = weight[a] / (k * weight[b])
            else:
                parent[rootB] = rootA
                weight[rootB] = weight[a] / (k * weight[b])
                rank[rootA] += 1
        for (a, b), v in zip(equations, values):
            union(a, b, v)
        res = []
        for a, b in queries:
            if a not in parent or b not in parent or find(a) != find(b):
                res.append(-1.0)
            else:
                res.append(weight[a] / weight[b])
        return res
```

### Weight 公式推导（用户强调的难点）

**1. 路径压缩里的 `weight[x] *= weight[parent[x]]`**

设原始结构 `x -> p -> root`，边权语义 `weight[x] = x / p`、`weight[p] = p / root`。压缩后想直接挂 `x -> root`，新的 `weight[x]` 必须等于 `x / root`：

$$\\frac{x}{root} = \\frac{x}{p} \\cdot \\frac{p}{root} = \\text{weight}[x] \\cdot \\text{weight}[p]$$

注意实现细节：**必须先递归 `find(parent[x])`**（先把 `parent[x]` 连到 root 并把它的 weight 累乘好），然后再读 `weight[parent[x]]` —— reverse order。如果倒过来写（先动 `weight[x]` 再 recurse）就会读到旧的 `weight[parent[x]]`，少累一段。这是带权 UF 最容易写错的地方。

**2. union 时把 rootA 挂到 rootB 下**

已知 `a / rootA = weight[a]`、`b / rootB = weight[b]`、`a / b = k`。合并后让 `rootA -> rootB`，新边权 `weight[rootA]` 必须等于 `rootA / rootB`：

$$\\frac{rootA}{rootB} = \\frac{rootA}{a} \\cdot \\frac{a}{b} \\cdot \\frac{b}{rootB} = \\frac{1}{\\text{weight}[a]} \\cdot k \\cdot \\text{weight}[b] = \\frac{k \\cdot \\text{weight}[b]}{\\text{weight}[a]}$$

反方向（rootB 挂到 rootA 下）就把分子分母倒一下，所以代码里 `weight[rootB] = weight[a] / (k * weight[b])`。Union-by-rank 决定挂哪边，结果一定是其中一个公式，不能写错方向。

**3. 查询 `weight[a] / weight[b]`**

调完 `find(a)` 与 `find(b)` 后，`weight[a] = a / root`、`weight[b] = b / root`，所以 `a / b = weight[a] / weight[b]`，前提是两者已经在同一棵树（`find(a) == find(b)`）。

### Solution 2 -- BFS on Weighted Graph (直观、易写)

把等式建成无向带权图，正向边权 `v`、反向边权 `1/v`。每个查询从起点出发 BFS，沿途累乘到目标节点。

```python
class Solution:
    def calcEquation(self, equations, values, queries):
        graph = defaultdict(dict)
        for (a, b), v in zip(equations, values):
            graph[a][b] = v
            graph[b][a] = 1.0 / v
        res = []
        for a, b in queries:
            if a not in graph or b not in graph:
                res.append(-1.0); continue
            if a == b:
                res.append(1.0); continue
            q = deque([(1.0, a)]); visited = {a}; found = False
            while q:
                product, src = q.popleft()
                for nxt in graph[src]:
                    if nxt in visited: continue
                    visited.add(nxt)
                    new_val = product * graph[src][nxt]
                    if nxt == b:
                        res.append(new_val); found = True; break
                    q.append((new_val, nxt))
                if found: break
            if not found: res.append(-1.0)
        return res
```

BFS 关键：建图时**反向边 `1/v` 也要加**；每个 query 用独立的 `visited`，product 沿边累乘；找到目标立即 break。换成 DFS 也行（递归回溯），逻辑等价。

### 复杂度对比

| 解法 | 预处理 | 单次查询 | 总时间 | 适用场景 |
|------|--------|----------|--------|----------|
| Weighted Union-Find | `O(E * alpha(N))` | `O(alpha(N))` | `O((E + Q) * alpha(N))` | 查询多、需要压到极致 |
| BFS on Graph | `O(E)` | `O(V + E)` | `O(E + Q * (V + E))` | 查询少（题目 N <= 20，Q <= 20），现场易写易讲 |

题目数据规模很小（变量数和等式数都 <= 20），BFS 完全够用且更易现场口述，面试可以"先写 BFS、追问性能再上 Weighted UF"。

### 常见陷阱

1. **未出现的变量**：`a` 或 `b` 不在 `parent`/`graph` 里直接返回 -1.0，**不要触发 KeyError**，也不要 lazy 加进去（题目要求未见过的变量当作"信息不足"）。
2. **a == b 且都存在**：返回 1.0。BFS 解法里如果不单独判 `a == b`，起点不会自我累乘，会漏判 —— 必须显式 short-circuit。
3. **除零**：题目保证 `values` 都非零，所以 `1.0 / v` 安全；自己造测试时要注意。
4. **Union-by-rank 不能写反**：把"矮树挂到高树"才能保持 `find` 最坏 `O(log N)`；写反会鼓包，find 退化。
5. **路径压缩的 reverse order**：先 `root = find(parent[x])` 再 `weight[x] *= weight[parent[x]]` 再 `parent[x] = root`。三句的顺序换一下结果就错。
6. **Weighted UF 用 union-by-size 也行**，但要把 `rank` 换成 `size` 字典并相应改条件，公式不变。

### 面试应答 checklist

1. **澄清**：变量类型（字符串）？查询数量级？是否允许 `a == a` 的查询？
2. **建模**：把"a / b = k"翻译成图的有向边或并查集的合并，边权是比值。
3. **先 BFS**：建无向图（反向边 `1/v` 一起加），逐 query BFS 累乘，时间 `O(Q*(V+E))`。
4. **追问性能 -> Weighted UF**：解释 `weight[x] = x / parent[x]` 的语义，推导路径压缩公式与 union 公式（关键是先 recurse 再更新 weight）。
5. **edge cases**：未出现变量返回 -1.0，`a == b` 直接返回 1.0。
6. **复杂度**：BFS `O(Q*(V+E))`，Weighted UF `O((E+Q)*alpha(N))`。

### 与本族其他题

- **LC 684 Redundant Connection**：朴素 Union-Find，无权。
- **LC 685 Redundant Connection II**：有向图，需要分情况讨论根。
- **LC 952 Largest Component Size by Common Factor**：Union-Find + 数论分解。
- **LC 1971 Find if Path Exists in Graph**：纯连通性，最简 Union-Find。
- **LC 990 Satisfiability of Equality Equations**：等式/不等式约束，Union-Find 验证。
- **本题特色**：在 Union-Find 上挂"边权"，把"连通性"扩展成"路径上的乘法"。这种"带权并查集"模板可推广到种类并查集、距离 mod k 等约束。
"""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    new_notes_hash = sha256(NOTES)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, leetcode_id, title, is_completed, family, "
            "framework_node_id, notes "
            "FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] No row for leetcode_id={LEETCODE_ID}")
            return 1

        pid, lc, title, is_completed, family, fwn_id, old_notes = row
        if pid != EXPECTED_DB_ID:
            print(f"[WARN] LC {lc} db id={pid} (expected {EXPECTED_DB_ID}); "
                  f"continuing with actual id")

        old_hash = sha256(old_notes) if old_notes else None
        already_complete = (
            is_completed == 1
            and family == FAMILY_SLUG
            and fwn_id == FRAMEWORK_NODE_ID
            and old_hash == new_notes_hash
        )
        if already_complete:
            print(f"[SKIP] LC {lc} (id={pid}) already in target state")
            print(f"[PASS] is_completed={is_completed} family={family!r} "
                  f"framework_node_id={fwn_id} notes_hash={new_notes_hash[:12]}")
            return 0

        print(f"[INFO] Pre: is_completed={is_completed} family={family!r} "
              f"framework_node_id={fwn_id} "
              f"notes_len={len(old_notes) if old_notes else 0}")
        print(f"[INFO] New: is_completed=1 family={FAMILY_SLUG!r} "
              f"framework_node_id={FRAMEWORK_NODE_ID} "
              f"notes_len={len(NOTES)} hash={new_notes_hash[:12]}")

        backup_db()

        conn.execute(
            "UPDATE problems SET is_completed = 1, family = ?, "
            "framework_node_id = ?, notes = ?, "
            "last_attempted_at = ? "
            "WHERE id = ?",
            (
                FAMILY_SLUG,
                FRAMEWORK_NODE_ID,
                NOTES,
                datetime.now().isoformat(timespec="seconds"),
                pid,
            ),
        )
        conn.commit()

        check = conn.execute(
            "SELECT is_completed, family, framework_node_id, notes "
            "FROM problems WHERE id = ?",
            (pid,),
        ).fetchone()
        post_hash = sha256(check[3])
        if (
            check[0] != 1
            or check[1] != FAMILY_SLUG
            or check[2] != FRAMEWORK_NODE_ID
            or post_hash != new_notes_hash
        ):
            print("[FAIL] Post-update mismatch:")
            print(f"  is_completed={check[0]} (want 1)")
            print(f"  family={check[1]!r} (want {FAMILY_SLUG!r})")
            print(f"  framework_node_id={check[2]} (want {FRAMEWORK_NODE_ID})")
            print(f"  notes_hash={post_hash[:12]} (want {new_notes_hash[:12]})")
            return 1

        print(f"[DONE] LC {lc} (id={pid}) updated")
        print(f"[PASS] is_completed=1 family={FAMILY_SLUG!r} "
              f"framework_node_id={FRAMEWORK_NODE_ID} "
              f"notes_len={len(check[3])} hash={post_hash[:12]}")

        family_group = conn.execute(
            "SELECT leetcode_id, title FROM problems "
            "WHERE family = ? ORDER BY leetcode_id",
            (FAMILY_SLUG,),
        ).fetchall()
        print(f"[INFO] family={FAMILY_SLUG!r} now has {len(family_group)} problem(s):")
        for lc_id, t in family_group:
            print(f"  LC {lc_id} -- {t}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
