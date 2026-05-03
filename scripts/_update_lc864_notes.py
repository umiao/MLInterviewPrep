"""Idempotent: seed LC 864 Shortest Path to Get All Keys notes.

LC 864 是 "状态压缩 BFS / 收集物最短路" 家族的 canonical 题目 ——
钥匙集合作为状态额外维度, 把指数级搜索压回多项式 BFS.

Run: python scripts/_update_lc864_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 864
PATTERN = "bfs_state_compression"
FAMILY = "bfs_state_space"
SENTINEL = "<!-- LC864_NOTES_V1 -->"

NOTES = """<!-- LC864_NOTES_V1 -->
## 题目定位
LC 864 Shortest Path to Get All Keys —— **状态压缩 BFS (state-compression
BFS)** 家族的 canonical 题目。$m \\times n$ 网格含起点 `@`、墙 `#`、空地 `.`、
钥匙 `a`-`f` 与对应锁 `A`-`F`；钥匙必须先收集才能开对应锁，求收齐所有
钥匙的最短路径长度。

**关键洞察**：单纯位置 $(x, y)$ 不足以表征 BFS 状态——同一格子在持有不同
钥匙集合时算不同节点（因为可达性变了）。状态空间扩展为
$m \\cdot n \\cdot 2^k$，$k$ = 钥匙数（题目保证 $k \\le 6$，所以 $2^k \\le 64$）。

## 思路
1. **状态编码**：`state = (x, y, key_mask)`，`key_mask` 是 $k$ 位 int，第 $i$
   位为 1 表示已持有第 $i$ 把钥匙（`'a' + i`）。
2. **BFS 分层**：队列里放 `(x, y, key_mask)`，每层 `cost += 1`。`visited` 用
   `set` 存三元组 tuple——直接哈希，**不要** stringify。
3. **转移规则**：走到下一个 `(nx, ny)`：
   - 越界 / 墙 `#` → 跳过
   - 锁 `'A'-'F'` → 必须 `mask` 对应位为 1 才能进
   - 钥匙 `'a'-'f'` → 进入并 OR 上对应位（`new_mask = mask | (1 << bit)`）
   - 空地 `.` 或起点 `@` → 直接进，mask 不变
4. **终止**：一旦 `new_mask == (1 << total_keys) - 1` 就返回当前层 + 1。

**为什么 BFS**：要最短路径，每步代价相同 → BFS 是 Dijkstra 的退化形式。

## 核心代码（bitmask 版，推荐）
```python
from collections import deque

class Solution:
    def shortestPathAllKeys(self, grid: list[str]) -> int:
        m, n = len(grid), len(grid[0])
        sx = sy = 0
        total_keys = 0

        # 扫一遍：找起点 + 数钥匙
        for i in range(m):
            for j in range(n):
                c = grid[i][j]
                if c == '@':
                    sx, sy = i, j
                elif 'a' <= c <= 'f':
                    total_keys += 1

        target = (1 << total_keys) - 1   # 全收齐的目标 mask
        if target == 0:
            return 0                     # 无钥匙 → 起点即终点

        queue = deque([(sx, sy, 0)])     # (x, y, key_mask)
        visited = {(sx, sy, 0)}
        cost = 0

        while queue:
            for _ in range(len(queue)):
                x, y, mask = queue.popleft()
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < m and 0 <= ny < n):
                        continue
                    c = grid[nx][ny]
                    if c == '#':
                        continue
                    # 锁: 必须持有对应钥匙
                    if 'A' <= c <= 'F' and not (mask >> (ord(c) - ord('A')) & 1):
                        continue
                    # 钥匙: OR 上对应位
                    new_mask = mask
                    if 'a' <= c <= 'f':
                        new_mask |= 1 << (ord(c) - ord('a'))
                    if new_mask == target:
                        return cost + 1
                    state = (nx, ny, new_mask)
                    if state in visited:
                        continue
                    visited.add(state)
                    queue.append(state)
            cost += 1
        return -1
```

## 关键技巧
- **状态压缩 = 多维 BFS 的标配**：凡是"地图 + 收集物"题（钥匙、宝石、必经
  点），把"已收集集合"塞进 `mask` 是把指数级搜索压回多项式 BFS 的标准套路。
- **mask 用 int 而非 list-of-bool**：int 哈希 $O(1)$、`tuple` 直接进 set，
  省掉 `str(list)` 的 stringify 开销（实测能省一半以上时间）。
- **goal check 写在"踩进去"那一刻**：在 `new_mask == target` 的瞬间 `return
  cost + 1`，不要等下一层弹出再判——能省一整层无意义扩展。
- **`@` 不必特判**：起点也能正常走回去（虽然没收益），当成空地处理就行。
- **位运算 cheatsheet**：取第 $i$ 位 `(mask >> i) & 1`；置位 `mask | (1 << i)`；
  全收齐 `mask == (1 << k) - 1`。

## 易错点
1. **visited 用 `(x, y)` 而非 `(x, y, mask)`**——这是经典错误。同一格在不同
   钥匙状态下必须算不同节点；只用 `(x, y)` 会把"绕回去拿钥匙再回来"的合法
   路径误剪。
2. **锁的位偏移写反**：大写 `'A'` 对应钥匙 `'a'`，要查 `mask` 的第
   `ord(c) - ord('A')` 位。若错写成 `ord(c) - ord('a')`，结果是负数 → 永远
   过不去任何锁。
3. **goal check 的时机**：若 `total_keys == 0`，要么开头特判 `target == 0
   return 0`，要么把 check 放在"刚踩进新格子"那一刻。等 pop 后再 check 会
   漏掉"起点即答案"的边界。
4. **off-by-one on `cost`**：`cost` 是层数（边数），不是节点数。在"踩进新格
   子"瞬间返回 `cost + 1`（这一步本身是新边）；若改成层结束才检查，则返回
   `cost`。两种写法只差 1，**混着写就 WA**。
5. **list 当 visited key 必须 stringify**：`visited.add(str([x, y, [...]]))`
   每步多一次 $O(\\text{state len})$ 的字符串构造；bitmask 版用 tuple 直接
   哈希，省掉这层常数。
6. **共享 list 引用**：list-of-bool 版本里，给状态加新钥匙前必须
   `cur = list(status)` 复制；否则修改会污染队列里其他 state 的 status。

## 复杂度
- 时间：$O(m \\cdot n \\cdot 2^k \\cdot 4)$，每个状态最多入队一次，每次扩展
  4 个邻居。本题 $k \\le 6$，最坏约
  $30 \\cdot 30 \\cdot 64 \\cdot 4 \\approx 2.3 \\times 10^5$ 次操作。
- 空间：$O(m \\cdot n \\cdot 2^k)$，visited 集合 + 队列。

## Follow-up: list-of-bool 版本（baseline，不推荐）
直觉写法：把"持有哪几把钥匙"做成长度 6 的 bool 列表，state =
`[x, y, [b1, ..., b6]]`，visited 存 `str(state)`。功能等价、渐近同阶，但
常数显著更大。

```python
from collections import deque

class Solution:
    def shortestPathAllKeys(self, grid: list[str]) -> int:
        m, n = len(grid), len(grid[0])
        sx = sy = 0
        keyNum = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == '@':
                    sx, sy = i, j
                elif 'a' <= grid[i][j] <= 'f':
                    keyNum += 1
        if keyNum == 0:
            return 0

        start = [sx, sy, [False] * 6]
        queue = deque([start])
        visited = {str(start)}
        cost = 0

        while queue:
            for _ in range(len(queue)):
                x, y, status = queue.popleft()
                for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if not (0 <= nx < m and 0 <= ny < n) or grid[nx][ny] == '#':
                        continue
                    cell = grid[nx][ny]
                    cur = list(status)                       # 必须复制
                    if 'A' <= cell <= 'F':
                        if not cur[ord(cell) - ord('A')]:
                            continue
                    elif 'a' <= cell <= 'f':
                        cur[ord(cell) - ord('a')] = True
                    if sum(cur) == keyNum:
                        return cost + 1
                    key = str([nx, ny, cur])
                    if key in visited:
                        continue
                    visited.add(key)
                    queue.append([nx, ny, cur])
            cost += 1
        return -1
```

### 与 bitmask 版的常数差距
| 维度 | list-of-bool | bitmask |
| --- | --- | --- |
| 状态拷贝 | `list(status)` 是 $O(6)$ 复制 | `mask \\| (1 << bit)` 是 $O(1)$ |
| visited 哈希 | `str([x, y, [..]])` 全长字符串 | `(x, y, mask)` int tuple 直接哈希 |
| 终止判定 | `sum(cur) == keyNum` 是 $O(6)$ | `new_mask == target` 是 $O(1)$ |
| 内存 / state | list 对象头 + 6 bool + str repr | 单个 int |
| 实测时间 | baseline | **快 2-3 倍** |

**两版本渐近同阶 $O(m \\cdot n \\cdot 2^k)$**，但常数差距足以让 list 版在大
case 上 TLE。面试白板写出 list 版能拿基础分，**主动指出"可以用 bitmask
压缩状态"并改写**是加分项。

## 一句话 pitch (面试 30 秒)
> 状态空间不是 $(x, y)$ 而是 $(x, y, \\text{key\\_mask})$ —— 同一格在不同
> 钥匙状态算不同节点。BFS 一层层扩，遇锁查 mask 对应位、遇钥匙在 mask 上
> OR 一位、`mask == (1 << k) - 1` 即收齐返回。复杂度 $O(m \\cdot n \\cdot 2^k)$，
> $k \\le 6$。bitmask 比 list-of-bool 同阶但快 2-3 倍。

## 题目家族（状态压缩 BFS）
- **LC 1494 / LC 847 / LC 943**：状态 = "已访问节点集合" 的 bitmask，求最短
  Hamilton 路径 / 最短超字符串。
- **LC 1293** Shortest Path in Grid with Obstacles Elimination：额外维度是
  "已使用的消除次数"，思想同源——**任何"额外维度决定可达性"的最短路问题，
  把维度塞进 BFS 状态即可**。
- **LC 1654** Minimum Jumps to Reach Home：状态 = `(pos, last_dir)`，
  同 family `bfs_state_space`。
"""


def main() -> None:
    """Seed LC 864 notes; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN
        if not fam:
            fields["family"] = FAMILY

        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} "
            f"notes_len={len(NOTES)} fields={list(fields)}"
        )


if __name__ == "__main__":
    main()
