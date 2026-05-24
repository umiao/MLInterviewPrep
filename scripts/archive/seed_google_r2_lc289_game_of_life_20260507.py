"""Seed Google R2 Coding problem: LC 289 Game of Life.

User-provided solution (Discord 2026-05-07 msg 1501771626813849741). Same
shape as LC 450: the problems row exists (id=452, leetcode_id=289) with
notes=NULL, family/pattern=NULL, and company_tags missing 'Google'. This
seed UPDATES the row in place: adds Google, sets family=matrix
pattern=simulation, writes a tight Chinese 题解 distilled from the user's
two-pass set-based solution plus the canonical in-place state-encoding
optimization and the infinite-board follow-up.

Canonical key per CLAUDE.md: leetcode_id (LC-numbered problems).

The R2 Coding Index (doc 92) is updated separately by re-running
`scripts/seed_google_r2_coding_index_20260502.py`, extended in this
commit to add the new entry under a new `### Matrix / Simulation` section.

Idempotent. Per Invariant 3 (CLAUDE.md), this seed is the sole sanctioned
write path for this row's drift fields.

Run: python scripts/seed_google_r2_lc289_game_of_life_20260507.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 289
TITLE = "Game of Life"
URL = "https://leetcode.com/problems/game-of-life/"
SOURCE_LABEL = "Google R2 2026-05"

# Union with existing tags; explicit list = idempotent canonical state.
COMPANY_TAGS = ["LinkedIn", "Uber", "Adobe", "Google"]

NOTES = """\
## LC 289. Game of Life

给一块 $m \\times n$ 0/1 矩阵 (1 = 活, 0 = 死), 按 Conway's Game of Life 规则同时更新一步, **原地修改**。

### 四条规则 (一定要先讲清)

设当前细胞活邻居数为 $L$ (8 邻域: 上下左右 + 4 对角):

| 当前状态 | $L$ 范围 | 下一步 | 直觉 |
|---------|---------|-------|------|
| 活 | $L < 2$ | 死 | 孤独 |
| 活 | $L \\in \\{2, 3\\}$ | 活 | 稳定 |
| 活 | $L > 3$ | 死 | 拥挤 |
| 死 | $L = 3$ | 活 | 繁殖 |

> **关键约束**: "同时" 更新 -- 必须先算完所有新状态再写入, 否则下游格子读到的是已经被修改的值, 结果错误。

### 思路 1: 双 set 暂存 (O(mn) 空间, 用户提供)

第一遍扫每格算 $L$, 把要变 0 / 变 1 的格子分别记入两个 `set`; 第二遍批量回填。简单直接, 不会污染读端。

```python
class Solution:
    def gameOfLife(self, board: list[list[int]]) -> None:
        m, n = len(board), len(board[0])
        DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        def live_neighbors(x, y):
            return sum(
                1 for dx, dy in DIRS
                if 0 <= (nx := x + dx) < m and 0 <= (ny := y + dy) < n
                and board[nx][ny] == 1
            )

        to_die, to_birth = set(), set()
        for i in range(m):
            for j in range(n):
                L = live_neighbors(i, j)
                if board[i][j] == 1 and (L < 2 or L > 3):
                    to_die.add((i, j))
                elif board[i][j] == 0 and L == 3:
                    to_birth.add((i, j))

        for i, j in to_die:    board[i][j] = 0
        for i, j in to_birth:  board[i][j] = 1
```

> **小优化** (vs 用户写法): `to_die` 只加"确实存活的"格子 -- 死格子标 0 是 no-op, 没必要进 set, 省掉一半冗余写。

**复杂度**: 时间 $O(mn)$, 空间 $O(mn)$ 最坏。

### 思路 2: 原地状态编码 (O(1) 额外空间, 面试加分项)

把 0/1 各扩成两态, 共 4 个状态码, 一个数同时编码 "**原状态 + 新状态**":

| 状态码 | 含义 | 原 | 新 |
|------|------|---|---|
| 0 | 死 -> 死 | 0 | 0 |
| 1 | 活 -> 活 | 1 | 1 |
| 2 | 活 -> 死 (dying) | 1 | 0 |
| 3 | 死 -> 活 (birth) | 0 | 1 |

读邻居时只判 "**原状态是不是活**" -- 活的原状态码是 $\\{1, 2\\}$, 用 `board[nx][ny] in (1, 2)` 或更简洁 `board[nx][ny] & 1` (1, 3 都活? 不! 3 是新生, 原是死) -- 注意位运算只对 (1,2)/(0,3) 不太对称, 直接 `in (1,2)` 最稳。

```python
class Solution:
    def gameOfLife(self, board: list[list[int]]) -> None:
        m, n = len(board), len(board[0])
        DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        for i in range(m):
            for j in range(n):
                L = sum(
                    1 for dx, dy in DIRS
                    if 0 <= (ni := i + dx) < m and 0 <= (nj := j + dy) < n
                    and board[ni][nj] in (1, 2)  # 原是活的
                )
                if board[i][j] == 1 and (L < 2 or L > 3):
                    board[i][j] = 2  # 标记 dying, 这一轮还能被读作 "原活"
                elif board[i][j] == 0 and L == 3:
                    board[i][j] = 3  # 标记 birth, 这一轮被读作 "原死"

        # 归一化: 2 -> 0, 3 -> 1, 即 % 2
        for i in range(m):
            for j in range(n):
                board[i][j] %= 2
```

**复杂度**: 时间 $O(mn)$, 空间 $O(1)$ 额外。

### Follow-up: 无限板 / 极稀疏

若 board 是无限大、活细胞稀疏, 用矩阵就浪费; 改用**集合表示**:

- `live: set[(int, int)]` 记录所有活格坐标
- 每轮: 对每个活格, 把它和它的 8 邻域都登记到一个 `defaultdict(int) cnt`, 累加它的 "存在感" -- 即每个活格给自己 + 8 邻居各贡献一次邻居计数
- 收尾: 遍历 `cnt`, 凡 $L = 3$ 或 ($L = 2$ 且原本就活) 的入下一代 `live`

```python
def step(live: set[tuple[int, int]]) -> set[tuple[int, int]]:
    from collections import defaultdict
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    cnt: dict[tuple[int, int], int] = defaultdict(int)
    for x, y in live:
        for dx, dy in DIRS:
            cnt[(x + dx, y + dy)] += 1
    return {p for p, L in cnt.items() if L == 3 or (L == 2 and p in live)}
```

时间 / 空间正比于"活细胞数 + 它们的邻域", 完全独立于板子大小。

### 易错点 / Checklist

- [ ] 必须**先全算后全写**, 否则同时性破坏 -- 用户的 set 法 / 状态编码 / 无限板都满足
- [ ] 8 邻域不是 4 邻域, 别漏对角线
- [ ] 边界: `0 <= nx < m and 0 <= ny < n` 的 `<` 别写成 `<=`
- [ ] $L == 3$ 既可以让活的存活, 也可以让死的复活 -- 死格的"复活"分支别忘
- [ ] 状态编码要先扫完整张图再做 `% 2` 归一化, 别在第一遍就归一
- [ ] 编码法判 "原是否活" 用 `in (1, 2)`, 不是 `== 1` (后者会漏掉本轮被标 dying 的格子)

### 复杂度总结

| 解法 | 时间 | 额外空间 |
|------|------|---------|
| 双 set 暂存 | $O(mn)$ | $O(mn)$ 最坏 |
| 原地状态编码 | $O(mn)$ | $O(1)$ |
| 无限板 sparse | $O(K)$, $K$ = 活细胞数 + 邻域 | $O(K)$ |

### 一句话总结

模拟同时性更新的核心是**读写分离**: 简单做法用两个 set / 一份 copy; 进阶做法用 0/1/2/3 四态在原地同时编码"原值+新值", 收尾 `% 2` 归一化; 稀疏无限板用 set + 邻居计数 dict, 完全脱离板子大小。
"""


PROBLEM_SPEC: dict = {
    "leetcode_id": LEETCODE_ID,
    "title": TITLE,
    "url": URL,
    "difficulty": "medium",
    "tags": ["matrix", "simulation", "in-place", "state-encoding", "cellular-automaton"],
    "pattern": "simulation",
    "family": "matrix",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "notes": NOTES,
}


def _select_existing_by_lc(
    conn: sqlite3.Connection, leetcode_id: int
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching leetcode_id, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, title, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, notes "
        "FROM problems WHERE leetcode_id = ?",
        (leetcode_id,),
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


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by leetcode_id. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing_by_lc(conn, spec["leetcode_id"])

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
    fields_to_check = [
        "title", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed", "notes",
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
    """Insert-or-update LC 289. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_lc289_game_of_life")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problem id={pid} leetcode_id={LEETCODE_ID} title={TITLE!r}")
        conn.commit()

    print("[OK] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
