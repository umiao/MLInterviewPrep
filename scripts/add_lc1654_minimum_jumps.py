"""Idempotent seed: LC 1654 Minimum Jumps to Reach Home.

Adds the problem row (if missing) with description + user's Chinese solution
notes (state-space BFS on the number line with a provable upper bound).

Run: python scripts/add_lc1654_minimum_jumps.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LC_ID = 1654
TITLE = "Minimum Jumps to Reach Home"
URL = "https://leetcode.com/problems/minimum-jumps-to-reach-home/"
DIFFICULTY = "medium"
PATTERN = "BFS"
TAGS = ["BFS", "Graph", "State Space", "Number Line"]
FAMILY = "bfs_state_space"

DESCRIPTION = """A bug starts at position 0 on the x-axis and wants to reach home at position `x`. The bug can jump exactly `a` positions forward or exactly `b` positions backward, with these constraints:

- It cannot jump backward twice in a row.
- It cannot land on any position in `forbidden`.
- It cannot land on a negative position.
- It may overshoot `x` during the process.

Given `forbidden`, `a`, `b`, `x`, return the minimum number of jumps to reach `x`, or `-1` if impossible.

**Example 1:** `forbidden = [14,4,18,1,15], a = 3, b = 15, x = 9` -> `3` (0 -> 3 -> 6 -> 9)

**Example 2:** `forbidden = [8,3,16,6,12,20], a = 15, b = 13, x = 11` -> `-1`

**Example 3:** `forbidden = [1,6,2,14,5,17,4], a = 16, b = 9, x = 7` -> `2` (0 -> 16 -> 7)

**Constraints:** `1 <= forbidden.length <= 1000`; `1 <= a, b, forbidden[i] <= 2000`; `0 <= x <= 2000`; `x` is not forbidden.
"""

NOTES = """## 题目定位
**状态空间 BFS（state-space BFS）在数轴上展开**。状态由 `(pos, last_dir)` 构成——因为"上一步是否是后跳"会影响当前能不能再后跳。经典的"BFS 层数 = 最少跳数"套路，关键难点在于**如何设置搜索上界**。

## 解法：BFS + 状态 `(pos, last)` + 安全上界
**核心思路**：把每个可达状态 `(pos, last ∈ {'f','b'})` 视作图中一个节点，`+a` 和（条件允许时）`-b` 是两条出边。BFS 保证第一次弹出 `x` 的层数就是最少跳数。

```python
class Solution:
    def minimumJumps(self, forbidden, a, b, x):
        forbidden = set(forbidden)
        if x == 0:
            return 0

        limit = max(max(forbidden, default=0), x) + a + b

        queue = deque([(0, 'f')])
        visited = {(0, 'f')}
        steps = 0

        while queue:
            steps += 1
            for _ in range(len(queue)):
                pos, last = queue.popleft()

                # forward jump
                nxt = pos + a
                if nxt == x:
                    return steps
                if nxt <= limit and nxt not in forbidden and (nxt, 'f') not in visited:
                    visited.add((nxt, 'f'))
                    queue.append((nxt, 'f'))

                # backward jump (previous step must not be 'b')
                if last != 'b':
                    nxt = pos - b
                    if nxt == x:
                        return steps
                    if nxt >= 0 and nxt not in forbidden and (nxt, 'b') not in visited:
                        visited.add((nxt, 'b'))
                        queue.append((nxt, 'b'))

        return -1
```

## 上界推导（面试最容易被追问的点）
设 `f = max(forbidden)`（空集时取 0）。**结论**：存在最优解使整条路径上所有位置都 `<= max(f, x) + a + b`。

**直觉论证（两段式）**：

1. **跨过 `f` 之后的段落退化**：当 `pos > f` 时，`[f+1, ∞)` 区间里没有禁点，forbidden 约束消失，问题退化为"在正半轴用 `+a` / `-b` 凑步数，且 `b` 不能连用"。在**无 forbidden 的直线上**，任何净位移 `Δ` 的最短实现方式都是"该前进就前进、该后退就后退"——多往远处跑一段再跑回来是纯浪费步数，没有禁点能强迫你绕远。
2. **所以**一条最优路径一旦跨过 `f + a`（进入安全区），再往前冲过 `f + a + b` 就没有任何收益，可以等价替换成在 `[f, f+a+b]` 内完成相同净位移。`x` 这一侧同理：若 `pos >= x` 想回到 `x`，继续往远冲也无意义。

两条合起来 → `limit = max(f, x) + a + b` 足以覆盖最优解的所有位置。**这是把问题从"数轴无限"收缩成"有限状态图"的关键**。

## 为什么状态要带 `last_dir`
- 如果只用 `pos` 作为 visited key，会把"上一步前跳的 `pos`"和"上一步后跳的 `pos`"合并。两者对后续分支完全不同（后者下一步不能再后跳）。
- 带上 `last ∈ {'f','b'}` 后，状态数最多翻倍（`2 * limit`），仍是 $O(\\text{limit})$ 级。

## 复杂度
- 时间：$O(\\text{limit})$ = $O(\\max(f,x) + a + b)$。给定 `forbidden[i], a, b, x <= 2000` → 上界约 $6000$ 个 pos × 2 个 dir = $1.2 \\times 10^4$ 节点，BFS 常数很小。
- 空间：同量级 $O(\\text{limit})$（visited + queue）。

## 易错点（面试）
1. **上界漏 `a + b`**：只写 `max(f, x)` 会漏掉"先跳过去再跳回来"的合法迂回；`max(f, x) + b` 仍可能在极端数据上错。加 `a + b` 是最稳的工程余量。
2. **忘记 `x == 0` 短路**：初始状态就是终点，直接返回 0。
3. **把 `visited` 按 `pos` 去重**：会错判可达性（见上）。
4. **`last != 'b'` 写反**：是"上一步不是后跳才允许这次后跳"，搞反会允许连续两次 `-b`。
5. **后跳下界判断用 `> 0`**：必须是 `>= 0`（`pos = 0` 合法——本身就是起点方向）。
6. **边界落入 `forbidden` 的处理**：判 `nxt == x` 应放在 forbidden 检查之前，因为题目保证 `x` 不在 forbidden；但放前面能少一次 hash lookup。
7. **起点方向取 `'f'`**：起点的"上一步"没有，但用 `'f'` 做哨兵可以让第一次后跳不被禁（因为 `last != 'b'`）。

## 变体 / 迁移
- **不能连续前跳**（把 `'f'` 的限制也加上）→ 只需加一行判断，模板几乎不变。
- **多段禁区 / 二维迷宫**（如 LC 1293 Shortest Path with Obstacles）→ 同样是"状态 = (位置, 剩余资源) 的 BFS"；本题的"剩余资源"是"上一步方向"。
- **`a, b, x, forbidden` 范围更大**（例如 $10^6$）→ BFS 仍可，但要把 visited 换成 bitset；上界仍是 `max(f,x) + a + b`。

## 一句话 pitch（面试）
> 这是状态空间 BFS：节点 = `(pos, last_dir)`，边 = `+a` 或 `-b`（后跳不能连用）。难点是证明搜索上界 `max(f,x) + a + b`——超过这条线后 forbidden 消失、最优解不会绕远，所以可以在有限状态图里跑 BFS，第一次达到 `x` 的层数就是答案。复杂度 $O(\\max(f,x) + a + b)$。
"""


def main() -> None:
    """Upsert LC 1654 with description + notes; mark completed."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(problems)")}
        if "family" not in cols:
            conn.execute("ALTER TABLE problems ADD COLUMN family TEXT")

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
            print(f"[ADDED] LC {LC_ID} id={new_id}")
        else:
            pid, existing_notes, existing_desc = row
            fields: dict[str, str | int] = {"notes": NOTES, "is_completed": 1, "family": FAMILY}
            if not existing_desc:
                fields["description"] = DESCRIPTION
                fields["description_source"] = "leetcode.ca"
            sets = ", ".join(f"{k} = ?" for k in fields)
            conn.execute(
                f"UPDATE problems SET {sets} WHERE id = ?",
                (*fields.values(), pid),
            )
            print(f"[UPDATED] LC {LC_ID} id={pid} fields={list(fields)}")

        conn.commit()


if __name__ == "__main__":
    main()
