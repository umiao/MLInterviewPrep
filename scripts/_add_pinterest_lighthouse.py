"""Add Pinterest Lighthouse 2D light-propagation custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC, recurring).
Canonical variant: ray-tracing on a 2D grid with lighthouses (beam sources),
mirrors ('/' and '\\') that reflect, splitters ('|' '-') that split a beam into
two perpendicular beams, and empty cells ('.') that let the beam pass through.
Count the set of illuminated cells (energized cells). Very close to AoC 2023
Day 16. The other plausible variants (Manhattan-radius coverage, cycle
detection) are summarized in the notes so an interviewer's exact phrasing can
be mapped onto this file.

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P1-398
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Lighthouse 2D Light Propagation (beam + mirrors + splitters)"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["Grid", "BFS", "Simulation", "Ray Tracing"])
PATTERN = "Grid BFS + State = (cell, direction)"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11] Light-propagation simulation on a 2D grid.
A lighthouse emits a beam in a given direction. The beam travels cell-by-cell
and interacts with grid contents:

  '.'  empty       - beam continues in same direction
  '/'  mirror      - (dr, dc) -> (-dc, -dr)    e.g. right -> up, down -> left
  '\\' mirror      - (dr, dc) -> ( dc,  dr)    e.g. right -> down, up -> left
  '|'  splitter    - if beam is horizontal, split into up + down; else pass
  '-'  splitter    - if beam is vertical, split into left + right; else pass

Count the number of distinct cells the beam(s) illuminate before exiting the
grid or revisiting a (cell, direction) state.

Extensions commonly asked:
  (a) Multiple lighthouses -- union illuminated sets.
  (b) Best placement: try each border cell as the beam origin, report the
      maximum illuminated count (O(N*M*(N+M)) brute force, O(N*M) with
      loop-aware memoization).
  (c) Cycle detection -- guaranteed by the (cell, direction) visited set.
"""

SOLUTION_TAG = "[Pinterest Lighthouse Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11)

Grid contents: `.` empty, `/` `\` mirrors, `|` `-` splitters. A lighthouse
emits a unit-speed beam from a given `(row, col, direction)`. Return the count
of distinct cells the beam illuminates.

## Key Insight: State = (cell, direction)

A beam at the same cell facing the same direction will always produce the same
future trace. So the visited set is keyed by `(r, c, dr, dc)`, NOT just
`(r, c)`. This is what guarantees termination (finite state space) and avoids
infinite loops in cyclic mirror configurations.

The illuminated count is `len({(r, c) for (r, c, _, _) in visited})`.

## Mirror Transforms (the one bit you must memorize)

For direction vector `(dr, dc)`:

| Cell | Transform | Intuition |
|------|-----------|-----------|
| `/`  | `(dr, dc) -> (-dc, -dr)` | right(0, 1)->up(-1,0); down(1,0)->left(0,-1) |
| `\`  | `(dr, dc) -> ( dc,  dr)` | right(0, 1)->down(1,0); up(-1,0)->left(0,-1) |

Splitters emit **two** new beams when hit perpendicularly; they act as `.`
when hit along their axis.

## Python Implementation

```python
from collections import deque

def energized(grid: list[str], start: tuple[int, int, int, int]) -> int:
    \"\"\"Return number of illuminated cells.

    start = (r0, c0, dr, dc). The start cell itself is illuminated.
    \"\"\"
    R, C = len(grid), len(grid[0])
    visited: set[tuple[int, int, int, int]] = set()
    q: deque[tuple[int, int, int, int]] = deque([start])

    while q:
        r, c, dr, dc = q.popleft()
        if not (0 <= r < R and 0 <= c < C):
            continue
        if (r, c, dr, dc) in visited:
            continue
        visited.add((r, c, dr, dc))
        ch = grid[r][c]

        if ch == '.':
            nxts = [(dr, dc)]
        elif ch == '/':
            nxts = [(-dc, -dr)]
        elif ch == '\\':
            nxts = [(dc, dr)]
        elif ch == '|':
            nxts = [(-1, 0), (1, 0)] if dr == 0 else [(dr, dc)]
        elif ch == '-':
            nxts = [(0, -1), (0, 1)] if dc == 0 else [(dr, dc)]
        else:
            nxts = []  # '#' wall or unknown -> absorbed

        for ndr, ndc in nxts:
            q.append((r + ndr, c + ndc, ndr, ndc))

    return len({(r, c) for (r, c, _, _) in visited})


def best_placement(grid: list[str]) -> int:
    \"\"\"Try every border origin; return max illuminated count.\"\"\"
    R, C = len(grid), len(grid[0])
    best = 0
    for r in range(R):
        best = max(best, energized(grid, (r, 0, 0, 1)))
        best = max(best, energized(grid, (r, C - 1, 0, -1)))
    for c in range(C):
        best = max(best, energized(grid, (0, c, 1, 0)))
        best = max(best, energized(grid, (R - 1, c, -1, 0)))
    return best
```

## Complexity

- Single-beam `energized`: each (cell, direction) enqueued at most once.
  There are `4 * R * C` states, so time and space are O(R*C).
- `best_placement` brute force: O((R + C) * R * C). For grid sizes in a
  45-minute coding round (R, C <= 200), this is well within limits.

## Edge Cases / Gotchas

1. The start cell *is* illuminated even if it's off-grid one step before --
   initialize by pushing `(r0, c0, dr, dc)` directly, not `(r0-dr, c0-dc, ...)`.
2. Splitters at the origin must split immediately (the code handles this
   because `ch == '|'` is checked before enqueuing neighbors).
3. A beam can revisit a *cell* from a different direction -- don't dedupe on
   `(r, c)` alone, or you'll undercount cells that splitters re-enter.
4. Walls / unknown characters: treat as absorbers (empty `nxts`).

## Chinese Notes (中文解析)

**核心套路**: 2D 网格光束模拟。BFS/DFS 状态必须是 `(r, c, dr, dc)` 四元组,
而不是普通的 `(r, c)`。否则遇到镜子循环 (比如两面 `/\\` 相对) 会死循环。

**镜面公式** (考前背诵):
- `/`: `(dr, dc) -> (-dc, -dr)`
- `\\`: `(dr, dc) -> (dc, dr)`
推导: `/` 是反对角, 交换并取反; `\\` 是主对角, 直接交换。

**分光器 `|` 和 `-`**:
- `|` 只对横向光束 (dr==0) 分成上下两束; 竖向光束直接穿过。
- `-` 相反: 竖向 (dc==0) 分成左右两束; 横向穿过。
这一点是最容易写反的地方。

**为什么状态空间有限?** 格子数 R*C, 方向 4 种, 总共 4*R*C 个状态, 每个至多入队一次。
所以时间空间都是 O(R*C)。

**陷阱**:
1. 起点本身要算照亮 (第一格先放入队列, 不要往回退一格再入队)。
2. 光束出格就停 (`not (0<=r<R and 0<=c<C)` 直接 continue)。
3. 同一个格子被多个方向经过要各算一次进 visited, 但统计亮格时再去重到 (r, c)。

**追问 (面试常见)**:
- Q: 最佳起点放哪里最亮? A: 枚举所有边界格 * 指向内部方向, 每次跑一次 BFS,
  复杂度 O((R+C)*R*C)。
- Q: 如果允许光束绕圈, 如何保证终止? A: 就是 `(r,c,dr,dc)` visited 集合的作用。
- Q: 只有镜子没有分光器时, 每个起点对应多少格? A: 等于其轨迹长度 (无分支, 无环
  保证每格至多一次)。

## Variant Map (从题目描述映射)

| 题目关键词 | 对应写法 |
|-----------|---------|
| "mirror reflection" / "ray tracing" | 本文主解 (energized) |
| "find a cycle in the beam path" | 用相同 visited 集合, 如果发现 `(r,c,dr,dc)` 重复访问并且尚未离开网格, 即存在环 |
| "lighthouse with radius R" / "Manhattan coverage" | 改 BFS 为 "从灯塔扩散 step <= R"; 每格访问一次, O(R^2) 或 O(R*C) |
| "which cells are lit by at least K lighthouses" | 对每个灯塔跑一遍, 计数图累加, 最后筛 >= K |

## Self-Test (smoke)

```python
# Straight beam, no mirrors.
g = [
    "....",
    "....",
    "....",
]
assert energized(g, (0, 0, 0, 1)) == 4  # row 0 only

# '/' mirror bends right-going beam upward.
g = [
    "..",
    "./",
]
# Trace: (1,0)R -> (1,1)/ reflects to U -> (0,1)U -> exit top.
# Cells lit: (1,0), (1,1), (0,1) = 3.
assert energized(g, (1, 0, 0, 1)) == 3

# Splitter '|' hit horizontally splits into up + down; beam does NOT
# also continue rightward. Common live-coding trap: assuming '|' both
# splits AND passes through.
g = [
    "...",
    ".|.",
    "...",
]
# Trace: (1,0)R -> (1,1)| splits into U and D
#   U branch: (0,1)U -> exit top
#   D branch: (2,1)D -> exit bottom
# Cells lit: (1,0), (1,1), (0,1), (2,1) = 4
assert energized(g, (1, 0, 0, 1)) == 4
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
    now = datetime.now(UTC).isoformat()

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


if __name__ == "__main__":
    upsert()
