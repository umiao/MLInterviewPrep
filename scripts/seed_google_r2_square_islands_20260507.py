"""Seed Google R2 custom problem: Number of Square Islands.

User-provided 题解 (Discord 2026-05-07 msg 1501824183984717895, attachment
~5KB). Custom Google R2 problem: count 4-connected 1-components in an
n*m grid that fill EXACTLY a k*k axis-aligned square (i.e. the component
itself is a solid square).

Two solutions preserved verbatim:

  1. BFS / DFS -- O(nm). For each maximal 4-connected component, track
     `size` and bounding box (rmin, rmax, cmin, cmax). It IS a square
     island iff (rmax - rmin == cmax - cmin) AND size == side*side.
     Maximality of the component is the moat-check guarantee.

  2. 2D prefix sum -- O(nm * min(n, m)). Enumerate (r1, c1, k); inner
     k*k must sum to k*k AND the four border strips (top/bottom/left/
     right, possibly out-of-bounds clipped) must sum to 0. Prune as
     soon as inner sum != k*k since strict superset can't fill either.

Custom problem -- no leetcode_id, canonical key = title='Number of
Square Islands'. family=matrix, pattern=flood-fill.
source='Google R2 2026-05', company_tags=[Google]. tags include
flood-fill, bfs, connected-components, prefix-sum, bounding-box.

Per `feedback_pinterest_two_tier_notes`: per-problem note in
`problems.notes`, ProblemDrawer renders via `db://<id>`. Doc 92
extended via `seed_google_r2_coding_index_20260502.py` to add a NEW
`### Matrix / Flood Fill` section between `### Matrix / Geometry` and
`### Prefix Sum / Hash`.

Idempotent. Title is the canonical key. First run on missing row:
1 INSERT. Re-run on identical state: 0 writes (UNCHANGED).

Run: python scripts/seed_google_r2_square_islands_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Number of Square Islands"
SOURCE_LABEL = "Google R2 2026-05"
COMPANY_TAGS = ["Google"]

NOTES = """\
## Number of Square Islands

### 题面

给定 `n*m` 二维网格 `grid`, 每格 `0` (水) / `1` (陆地)。一个 **island** 是上下左右四连通的极大 `1` 连通块。

如果一个 island 的所有陆地格子**恰好填满某个 k*k 正方形区域** (连通块本身就是实心正方形), 称为 **square island**。返回 square island 的数量。

**示例**

```
grid = [[1,1,0,1],
        [1,1,0,1],
        [0,0,0,0],
        [1,0,0,0]]
```

返回 `2`: 左上 2*2 是一个 square island, 右下角单个 `1` 是 1*1 的 square island, 右上的 2*1 竖条不是正方形所以不算。

---

### 解法一: BFS / DFS -- $O(nm)$ (推荐)

直接找出每个**极大**连通块, 验证是否实心正方形。每个连通块只需三个量:

- `size` -- 连通块格子数
- bounding box -- `(rmin, rmax, cmin, cmax)`

判定为 square island 当且仅当:

1. **bounding box 是正方形**: `rmax - rmin == cmax - cmin`
2. **连通块填满 bounding box**: `size == (rmax - rmin + 1)^2`

关键: 因为 BFS/DFS 找的是**极大**连通块, 天然保证不会有"和外面相连"的护城河遗漏 -- 不需要额外的 0-边界检查。

```python
from collections import deque
from typing import List

def countSquareIslands(grid: List[List[int]]) -> int:
    n, m = len(grid), len(grid[0])
    seen = [[False] * m for _ in range(n)]
    ans = 0

    def bfs(sr, sc):
        q = deque([(sr, sc)])
        seen[sr][sc] = True
        size = 0
        rmin = rmax = sr
        cmin = cmax = sc
        while q:
            r, c = q.popleft()
            size += 1
            rmin, rmax = min(rmin, r), max(rmax, r)
            cmin, cmax = min(cmin, c), max(cmax, c)
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < n and 0 <= nc < m
                        and not seen[nr][nc] and grid[nr][nc] == 1):
                    seen[nr][nc] = True
                    q.append((nr, nc))
        side = rmax - rmin + 1
        return (rmax - rmin == cmax - cmin) and size == side * side

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1 and not seen[i][j]:
                if bfs(i, j):
                    ans += 1
    return ans
```

- 时间 $O(nm)$ -- 每格至多入队一次。
- 空间 $O(nm)$ -- `seen` + 队列。

---

### 解法二: 二维前缀和 -- $O(nm \\cdot \\min(n, m))$

枚举每个候选正方形 `(r1, c1, k)`, 用前缀和判定。需要**同时**满足:

1. **内部全是 1**: `sum(r1, c1, r1+k-1, c1+k-1) == k^2`
2. **四周全是 0 (或越界)**: 护城河检查 -- 上一行 / 下一行 / 左一列 / 右一列 (clip 到合法范围) 全为 0

**只满足条件 1 不够** -- L 形 island 里可能嵌着一个全 1 的方形子矩形, 但 island 本身不是正方形, 那个子矩形会被错误计入。护城河保证候选正方形是**极大**的全 1 形状。

每个 square island 对应唯一的 `(r1, c1, k)` (左上角 + 边长), 不会重复计数。**剪枝**: 一旦 k*k 不全是 1, 更大的也不可能 (单调), 直接 `break`。

```python
from typing import List

def countSquareIslands(grid: List[List[int]]) -> int:
    n, m = len(grid), len(grid[0])
    P = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            P[i+1][j+1] = P[i][j+1] + P[i+1][j] - P[i][j] + grid[i][j]

    def rect_sum(r1, c1, r2, c2):
        r1, c1 = max(r1, 0), max(c1, 0)
        r2, c2 = min(r2, n - 1), min(c2, m - 1)
        if r1 > r2 or c1 > c2:
            return 0
        return P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]

    ans = 0
    for r1 in range(n):
        for c1 in range(m):
            if grid[r1][c1] == 0:
                continue
            for k in range(1, min(n - r1, m - c1) + 1):
                r2, c2 = r1 + k - 1, c1 + k - 1
                if rect_sum(r1, c1, r2, c2) != k * k:
                    break  # 单调剪枝
                if (rect_sum(r1 - 1, c1, r1 - 1, c2) == 0
                        and rect_sum(r2 + 1, c1, r2 + 1, c2) == 0
                        and rect_sum(r1, c1 - 1, r2, c1 - 1) == 0
                        and rect_sum(r1, c2 + 1, r2, c2 + 1) == 0):
                    ans += 1
    return ans
```

- 时间 $O(nm \\cdot \\min(n, m))$ -- 每个 (r1, c1) 枚举到边长无法扩张就 break。
- 空间 $O(nm)$ -- 前缀和数组。

---

### 两种解法对比

| | 解法一 (BFS/DFS) | 解法二 (前缀和) |
|---|---|---|
| 时间 | $O(nm)$ | $O(nm \\cdot \\min(n,m))$ |
| 直观度 | 高, 按定义模拟 | 中, 需要想到护城河 |
| 易扩展性 | 子矩形查询不好做 | 支持子矩形查询 / 动态边长筛选等 follow-up |

**面试建议**: 先答解法一拿 baseline; 再主动提解法二作为子矩形查询扩展, 体现思维深度。

---

### 易错 / 边界

- **极大性是关键**。解法一靠 BFS 自然保证 (扩到不能扩); 解法二靠护城河四边显式检查 (`rect_sum == 0`) 保证。漏一边都会把"L 形里嵌的方块"误判为 square island。
- **护城河越界要 clip**, 不能直接当 0 -- 用 `rect_sum` 的 `max/min` clamp + `r1 > r2 or c1 > c2 -> 0` 兜底。把 `r1-1 < 0` 当作"那一行不存在所以全是 0", 越界视为 0 是正确的, 但实现时要保证不下标越界。
- **解法二剪枝单调性**: 内部全 1 是大小**单调**的 (大方块全 1 -> 子方块也全 1), 反过来一旦 k*k 内部不全 1, 更大的也不行 -> 直接 `break` 内层循环, 否则退化到 $O(n^2 m^2)$。
- **判定式**: bounding box 正方形 + size 等于 side^2, **两条都要**。只查正方形而漏 size 会把 L 形包住的"含洞 island"误判 (虽然题目里 1 不会有洞, 因为 island 是 4-连通的极大块, 但代码上同时验两条更稳)。
- **k = 1 的单陆地**也算 square island。BFS 解法天然覆盖; 前缀和解法 `k=1` case 护城河检查依然正确 (单点四邻居全 0)。

### 一句话总结

Square Island = (极大 4-连通块 1) AND (bounding box 是正方形) AND (size == side^2)。**首选 BFS + bounding box O(nm)**, baseline 干净直观; 进阶解法二**前缀和 + 护城河枚举**走 $O(nm \\cdot \\min(n,m))$, 适合扩展子矩形 follow-up。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": None,
    "title": TITLE,
    "url": None,
    "difficulty": "medium",
    "tags": [
        "matrix", "flood-fill", "bfs", "connected-components",
        "prefix-sum", "bounding-box",
    ],
    "pattern": "flood-fill",
    "family": "matrix",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_title(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "title", "url", "difficulty", "tags", "pattern",
        "family", "category", "source", "company_tags", "is_completed", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def _merge_company_tags(current_json: str | None, target_list: list[str]) -> str:
    """Union target into existing JSON-encoded company_tags list, preserving order."""
    cur = json.loads(current_json) if current_json else []
    for tag in target_list:
        if tag not in cur:
            cur.append(tag)
    return json.dumps(cur, ensure_ascii=False)


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title (custom problem). Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_title(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    merged_company_tags = _merge_company_tags(
        current.get("company_tags"), spec["company_tags"]
    )
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "is_completed", "notes",
    ]
    drift = {
        f: norm[f] for f in fields_to_check if current.get(f) != norm[f]
    }
    if current.get("company_tags") != merged_company_tags:
        drift["company_tags"] = merged_company_tags

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
    """Insert-or-update Number of Square Islands. Return 0 on success."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_square_islands")
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
