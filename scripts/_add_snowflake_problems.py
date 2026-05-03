"""Archive 2 Snowflake interview problems (2026-04-15 dump).

Problems (custom, not direct LC):
1. Nearest Bathroom to Each Desk -- multi-source BFS on a grid (LC 542 variant)
2. Max Tree Height After Deleting Nodes (+ follow-up: min deletions for height <= k)

Both tagged with Snowflake. Creates Snowflake company row if missing.
Idempotent: re-run updates notes in-place.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

COMPANY_NAME = "Snowflake"
COMPANY_TAGS = json.dumps(["Snowflake"])

PROBLEMS = [
    {
        "title": "Nearest Bathroom to Each Desk (grid)",
        "difficulty": "medium",
        "pattern": "Multi-source BFS on grid (single queue, all sources at dist=0)",
        "category": "algorithm",
        "tags": json.dumps(["BFS", "Grid", "Multi-source"]),
        "priority": 2,  # P1
        "description": """\
[Snowflake coding 2026-04-15, Round 1]
给定一个二维网格，`B` 代表 Bathroom（浴室），`D` 代表 Desk（办公桌），其余为可通行空格。
对每个 `D`，求它到最近 `B` 的最短步数（4 邻域，边权 1）。

**输入**：字符网格 `grid: list[list[str]]`，含 `'B'` / `'D'` / `'.'`（可通行）/ 可能的 `'#'`（墙，视题目变体）。
**输出**：对每个 D 的位置返回其到最近 B 的距离；不可达可返回 `-1` 或 `inf`。

**典型规模**：`R, C ≤ 10^3` 量级，`B` 和 `D` 可多。
""",
        "notes": """\
## 解法：多源 BFS（single queue）

**核心观察**：要对每个 D 求到**最近** B 的距离，天然适合"反向思考"——从所有 B 同时出发做一次 BFS，每个格子第一次被访问时的距离就是它到最近 B 的距离。

**为什么不开多个独立 queue**：如果每个 B 单独跑 BFS，复杂度 `O(B · R · C)`；多源 BFS 只跑一次 `O(R · C)`，省一个 `B` 的因子。

### 关键技巧

把**所有** B 一开始就 push 进同一个 queue，距离设为 0。BFS 逐层扩散时等价于所有 B 的波前同步推进，谁的波先到某格，谁就是那格的"最近"。

```python
from collections import deque

def nearest_bathroom(grid):
    R, C = len(grid), len(grid[0])
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    # 所有 B 作为多源起点
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "B":
                dist[r][c] = 0
                q.append((r, c))
    # 单队列 BFS
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and dist[nr][nc] == -1 and grid[nr][nc] != "#":
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    # 收集每个 D 的答案
    ans = {}
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "D":
                ans[(r, c)] = dist[r][c]   # -1 表示不可达
    return ans
```

### 复杂度
- 时间 `O(R · C)`：每个格子最多入队一次（首次被访问时设距离）。
- 空间 `O(R · C)`：距离矩阵 + 队列最坏填满一层。

### 与 LC 542 (01 Matrix) 的关系
LC 542 是"对每个 1 求到最近 0 的距离"，本题是"对每个 D 求到最近 B 的距离"——完全同构，把 `'0' → 'B'`、`'1' → 'D'` 即可。面试时先提"这是 LC 542 的变体"可以快速建立共识。

### 为什么不从 D 出发？
也能做，但每个 D 独立跑 BFS 是 `O(D · R · C)`。当 D 和 B 数量接近时没有优势；而"从稀疏的一侧出发、多源同时扩散"几乎总是更快，且代码更简洁（只跑一次 BFS）。

### 45 秒口播
> "多源 BFS：把所有 B 一次性入队、距离设 0，然后跑一次标准 BFS。每个格子第一次被访问时的距离就是它到最近 B 的距离——因为 BFS 按层扩散，先到的一定最近。不要对每个 B 分别 BFS，那是 O(B·R·C)；多源只跑一次 O(R·C)。代码核心就是"起点是多个"这一行改动，其余和标准 BFS 一样。"
""",
    },
    {
        "title": "Max Tree Height After Deleting Nodes + k-height min deletions",
        "difficulty": "medium",
        "pattern": "Post-order DFS; greedy delete-near-root for k-height follow-up",
        "category": "algorithm",
        "tags": json.dumps(["Tree", "DFS", "Greedy"]),
        "priority": 2,
        "description": """\
[Snowflake coding 2026-04-15, Round 2]

**主题**：给定一棵 N 叉树和要删除的节点列表 `delete_set`。删除节点后，其子节点**直接接到祖父节点**（类似"吸收"被删节点）。求删除后树的**最大高度**（edge 数）。

**Follow-up**：反过来——给定一个 `k`，问**最少**删除多少个节点能让树的最大高度 `≤ k`？root 不能删。

**节点结构**（示意）：
```python
class Node:
    val: int
    children: list["Node"]
```

时间限制内只要求 O(N) 解法。
""",
        "notes": """\
## 主题解法：后序 DFS 一次遍历

**观察**：每棵子树对父亲贡献的"到叶子的边数"（= 子树深度）可以递归计算：
- 叶子：若被删 → 贡献 0（它消失，父亲直接连到空），若保留 → 贡献 1（自己到父亲那条边，但我们改成返回"到该节点子树最深叶子的边数"更顺；统一口径见下）
- 内部节点：`mx = max(dfs(c) for c in children)` 是所有子树贡献的最大值；若当前节点被删 → 返回 `mx`（当前节点消失，子节点直接接父亲，深度不变）；否则返回 `mx + 1`（当前节点到父亲那条边）。

```python
def tree_height_after_delete(root, delete_set):
    def dfs(node):
        if not node.children:
            return 0 if node in delete_set else 1
        mx = max(dfs(c) for c in node.children)
        return mx if node in delete_set else mx + 1
    # root 通常保留；题目约定 root 不删
    return max((dfs(c) for c in root.children), default=0)
```

### 为什么被删节点返回 `mx` 而不是 `mx + 1`
被删节点消失后，它的子节点直接连父亲。原本"子节点到当前节点 1 条边 + 当前节点到父亲 1 条边"= `mx + 1` 变成"子节点直接到父亲 1 条边" = `mx`。正好少 1。

### 复杂度
`O(N)` 时间，`O(H)` 递归栈空间。

---

## Follow-up：给定 `k`，最少删多少节点

**贪心直觉**：优先删靠近 root 的节点——删一个靠上的节点能同时把其整个子树的"深度贡献"砍掉 1，对多条路径生效；删叶子只对自己那条路径有帮助。

**算法**：后序 DFS，计算每个节点向上传的深度 `h`；若 `h > k`，就删掉当前节点并把 `h` 回退 1。

```python
def min_deletions_for_height_k(root, k):
    deletions = 0

    def dfs(node):
        nonlocal deletions
        if not node.children:
            return 1   # 叶子保留时向上贡献 1 条边
        mx = max(dfs(c) for c in node.children)
        h = mx + 1
        if h > k:
            deletions += 1
            return mx  # 删除当前节点，深度退回 mx
        return h

    # root 不能删；只对 root 的子节点做 DFS，root 本身的"到自己"不计
    for c in root.children:
        dfs(c)
    return deletions
```

### 正确性证明（归纳）
- **归纳假设**：处理完任何节点后它向上传的 `h` 都 `≤ k`。
  - 叶子：`h = 1 ≤ k`（假设 `k ≥ 1`；`k = 0` 需特判即 root 外全删）。
  - 内部节点：`mx ≤ k` 由归纳假设，若 `mx + 1 > k` 则删，退回 `mx ≤ k`；否则 `h = mx + 1 ≤ k`。
- 因此 root 所有子节点回传的 `h` 都 `≤ k`，整树高度 `≤ k`。

### 最优性
`h` 自叶子向上**单调递增**（每层 +1，删除时才回退）。`h` 第一次超过 `k` 的位置就是"能删的最高节点"——删它一举把该路径的深度砍 1。从下往上删叶子只能解决单路径；从高处删能同时救所有过深的叶子。每次删除把 `h` 精确减 1，不多删。

### 走一遍示例
链 `root - A - B - C - D - E`，`k = 2`：
- `dfs(E) = 1`
- `dfs(D) = 2`（= `mx + 1` = `1 + 1`）
- `dfs(C) = 3 > 2` → 删 C，返回 `mx = 2`
- `dfs(B) = 3 > 2` → 删 B，返回 `mx = 2`
- `dfs(A) = 3 > 2` → 删 A，返回 `mx = 2`
- root 子节点 A 的最终贡献 2，整树高度 2 ✓
- 共删除 3 个（A/B/C），都靠近 root，最终 `root - D - E`。

### 复杂度
`O(N)` 时间。

### 面试细节
- `k = 0` 边界：根据题意 root 不删，所以 `k = 0` 等价于"只保留 root"，需要删 root 下所有子节点——可以在主函数里判断 `k = 0` 直接返回 root 的直接子孙计数，或让 `dfs` 在 `k = 0` 时把 `h = 1 > 0` 全删（需允许删除后 `h` 退回 0；注意叶子被删时不该"贡献 1"，要再写一种口径）。建议面试时主动澄清 `k` 的下界。
- "root 不能删"是关键约束；若允许删 root，贪心会在极端情况下选择删 root，结构退化。

### 45 秒口播
> "主题是后序 DFS：每个节点返回"到子树最深叶子的边数"；被删节点返回 mx，保留节点返回 mx+1。Follow-up 用同一个 DFS + 贪心：h = mx + 1 时若 h > k 就删掉当前节点、h 回退到 mx。正确性归纳：处理完任何节点 h ≤ k；最优性来自"bottom-up 时 h 单调增，第一次超 k 的位置是最靠近 root 的可删点，一删救多条路径"。O(N)。"
""",
    },
]


def upsert_company(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM companies WHERE name = ?", (COMPANY_NAME,)).fetchone()
    if row:
        print(f"[OK] Snowflake exists id={row[0]}")
        return row[0]
    cur = conn.execute(
        "INSERT INTO companies (name, status) VALUES (?, 'applied')",
        (COMPANY_NAME,),
    )
    conn.commit()
    new_id = cur.lastrowid
    print(f"[INSERT] Snowflake created id={new_id}")
    return new_id


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> int:
    now = datetime.now(UTC).isoformat()
    row = conn.execute(
        "SELECT id FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (spec["title"],),
    ).fetchone()
    if row:
        pid = row[0]
        conn.execute(
            "UPDATE problems SET description = ?, notes = ?, pattern = ?, "
            "difficulty = ?, tags = ?, category = ?, company_tags = ?, priority = ? "
            "WHERE id = ?",
            (
                spec["description"], spec["notes"], spec["pattern"],
                spec["difficulty"], spec["tags"], spec["category"],
                COMPANY_TAGS, spec["priority"], pid,
            ),
        )
        print(f"[UPDATE] id={pid} {spec['title'][:50]}")
        return pid
    cur = conn.execute("SELECT MAX(id) FROM problems")
    next_id = (cur.fetchone()[0] or 0) + 1
    conn.execute(
        """
        INSERT INTO problems (
            id, leetcode_id, title, url, difficulty, tags, pattern,
            category, source, company_tags, priority, is_completed,
            comfort_level, created_at, description, notes
        ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
        """,
        (
            next_id, spec["title"], spec["difficulty"], spec["tags"],
            spec["pattern"], spec["category"], "snowflake_interview,custom",
            COMPANY_TAGS, spec["priority"], now, spec["description"], spec["notes"],
        ),
    )
    print(f"[INSERT] id={next_id} {spec['title'][:50]}")
    return next_id


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        upsert_company(conn)
        for spec in PROBLEMS:
            upsert_problem(conn, spec)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
