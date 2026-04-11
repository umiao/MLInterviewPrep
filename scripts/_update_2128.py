"""Idempotent upsert for LeetCode 2128 "Remove All Ones With Row and Column Flips".

Inserts the problem row if missing (LC 2128 is Premium and not previously seeded),
then updates notes / description / metadata to the latest Chinese solution writeup.
Safe to re-run; will only write when content differs.
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

LEETCODE_ID = 2128
TITLE = "Remove All Ones With Row and Column Flips"
URL = "https://leetcode.com/problems/remove-all-ones-with-row-and-column-flips/"
DIFFICULTY = "medium"
PATTERN = "Math"
CATEGORY = "algorithm"
TAGS = ["Math", "Bit Manipulation", "Matrix", "XOR", "Greedy"]
# LC 2128 is primarily a Google problem per user confirmation (2026-04-10).
# Also fits the LinkedIn premium cluster convention used by nearby grid/XOR
# problems (1829, 1878, 1931, 2282, 2328, 2429, 2503, 2577, 2812, ...).
COMPANY_TAGS = ["LinkedIn", "Uber", "Adobe", "Google"]

DESCRIPTION = """You are given an m x n binary matrix grid.

In one operation, you can choose any row or column and flip each value in that
row or column (i.e., changing all 0's to 1's, and all 1's to 0's).

Return true if it is possible to remove all 1's from grid using any number of
operations or false otherwise.

Example 1:
    Input: grid = [[0,1,0],[1,0,1],[0,1,0]]
    Output: true
    Explanation: One possible way to remove all 1's from grid is to flip the
    middle row and flip the middle column.

Example 2:
    Input: grid = [[1,1,0],[0,0,0],[0,0,0]]
    Output: false
    Explanation: It is impossible to remove all 1's from grid.

Example 3:
    Input: grid = [[0]]
    Output: true
    Explanation: There are no 1's in grid.

Constraints:
    - m == grid.length
    - n == grid[i].length
    - 1 <= m, n <= 300
    - grid[i][j] is either 0 or 1.
"""

NOTES = r"""## Remove All Ones With Row and Column Flips

### 思路
经典的"行翻转 + 列翻转"可达性问题。翻转操作满足交换律和自反性（翻两次等于没翻），所以每一行 / 每一列只有"翻" 或"不翻" 两种最终状态。设：

- r_i ∈ {0, 1}：第 i 行是否被翻转（奇偶次）
- c_j ∈ {0, 1}：第 j 列是否被翻转（奇偶次）

要让所有格子变成 0，需要对每个 (i, j) 都有：

$$grid[i][j] \oplus r_i \oplus c_j = 0 \iff grid[i][j] = r_i \oplus c_j$$

把 i = 0 固定下来观察：对每一列 j 都有 grid[0][j] = r_0 ⊕ c_j，所以 c_j = grid[0][j] ⊕ r_0 完全由第一行决定（r_0 只是一个全局偏移）。把这个关系代回任意第 i 行：

$$grid[i][j] = r_i \oplus c_j = r_i \oplus r_0 \oplus grid[0][j]$$

令 d = r_i ⊕ r_0 ∈ {0, 1}，则对同一行 i，要么 d = 0、即 grid[i] 整行等于 grid[0]；要么 d = 1、即 grid[i] 整行等于 grid[0] 按位取反。

**核心结论**：能把矩阵全部消成 0 ⟺ 每一行要么等于第一行，要么是第一行的按位取反。

### 关键技巧
- 把"行翻转 + 列翻转"的操作抽象到 GF(2) 上：每一步操作都是 XOR，顺序无关，只看奇偶。
- 行列变量解耦：先固定 r_0 = 0 把 c_j 解出来，再代回任意行 i，就把 m·n 个方程压缩成"每行与第一行的关系"这一条判据。
- 判定时不需要真正去模拟翻转，只需对比每一行和 grid[0] / grid[0] 取反即可，O(mn) 走完。

### 核心代码
```python
from typing import List


class Solution:
    def removeOnes(self, grid: List[List[int]]) -> bool:
        # 核心结论（GF(2) 推导）：
        # 能把矩阵全部消成 0  ⟺  每一行要么等于第一行，要么是第一行的按位取反。
        #
        # 证明思路：设 r_i, c_j ∈ {0,1} 表示第 i 行 / 第 j 列是否被翻转（奇偶）。
        # 要求 grid[i][j] XOR r_i XOR c_j = 0，即 grid[i][j] = r_i XOR c_j。
        # 固定 i=0 后，c_j 由第一行决定；代回任意行 i 得到
        #     grid[i] = grid[0]        (当 r_i = r_0)
        #  或 grid[i] = grid[0] 取反    (当 r_i ≠ r_0)

        first = grid[0]
        flipped = [1 - x for x in first]
        return all(row == first or row == flipped for row in grid)
```

### 注意点
- 只需要看"每一行和第一行的关系"，不需要去判断"第一行和其他某行的关系"——因为一旦每一行都满足 "等于第一行或其取反"，就可以构造合法的 r_i / c_j 把整张矩阵消成 0。
- 第一行本身自动满足条件（row == first），不用特殊处理。
- 该条件是**充要**的：必要性来自上面的代数推导；充分性可以直接构造翻转序列——先按第一行中的 1 对应的列去翻列，把第一行清零；再把"和第一行相反"的那些行各翻一次行，也会被清零。
- 题目保证 grid[i][j] ∈ {0, 1}，所以用 `1 - x` 或 `x ^ 1` 取反都是合法写法。

### 复杂度
- 时间：O(m·n)，每个元素最多被比较一次（`row == first` 的底层仍然是 O(n)）。
- 空间：基础解法 O(n)，用于存 `flipped` 这一份取反后的第一行。

### 空间优化：O(1) 额外空间
上面的版本为了写得紧凑，额外分配了 `flipped = [1 - x for x in first]`，空间是 O(n)。其实完全可以不显式构造这一行——观察到"第 i 行该不该翻"只取决于它和第一行在**任何一个固定列**上的关系，最自然的选择就是第 0 列：

- 若 `grid[i][0] == grid[0][0]`，那么这一行"应当等于第一行"，每个 j 都要求 `grid[i][j] == grid[0][j]`。
- 若 `grid[i][0] != grid[0][0]`，那么这一行"应当等于第一行取反"，每个 j 都要求 `grid[i][j] == grid[0][j] ^ 1`。

任何一列不符合立刻返回 False，否则扫完返回 True。整个过程只用了常数个标量变量，没有新分配数组。

```python
class Solution:
    def removeOnes(self, grid: List[List[int]]) -> bool:
        m, n = len(grid), len(grid[0])
        for i in range(1, m):
            same = (grid[i][0] == grid[0][0])
            for j in range(n):
                expected = grid[0][j] if same else grid[0][j] ^ 1
                if grid[i][j] != expected:
                    return False
        return True
```

**为什么这样是对的？**
- "第 i 行应当等于第一行还是等于第一行取反"这个 0/1 选择，由 r_i ⊕ r_0 唯一决定，而这个值可以从**任意一列**上读出来。选第 0 列只是因为它一定存在（n ≥ 1）。
- 一旦 `same` 定了，整行的期望值就确定了：要么逐位等于 `grid[0][j]`，要么逐位等于 `grid[0][j] ^ 1`。任何一个位置对不上就说明这一行既不等于第一行，也不是它的取反，直接判假。
- 如果 m == 1，外层循环空跑，直接返回 True——这也是对的，因为只有一行时，可以靠列翻转把所有 1 清掉（对每个为 1 的列翻一次即可）。
- 时间依旧是 O(m·n)（每个元素恰好被访问一次），而空间从 O(n) 降到 O(1)——只用了 `m`、`n`、`i`、`j`、`same`、`expected` 几个标量。

### 另一种思路：用集合去重
完全等价的写法：对每一行生成一个"规范化形态"——如果该行首元素和 grid[0][0] 相同就原样保留，否则整行取反。再把所有规范化后的行塞进一个集合，若集合大小 == 1 就说明它们全都等于 grid[0]，返回 True。

```python
class Solution:
    def removeOnes(self, grid: List[List[int]]) -> bool:
        seen = set()
        base = grid[0][0]
        for row in grid:
            if row[0] == base:
                seen.add(tuple(row))
            else:
                seen.add(tuple(1 - x for x in row))
            if len(seen) > 1:
                return False
        return True
```

这种写法的好处是"判等逻辑"被完全收拢到 `set` 里，读起来更像"所有行规范化后是否同一个模式"；代价是每行都要构造 tuple，空间重新回到 O(m·n)。面试里写 O(1) 空间的第二版最合适。
"""


def main() -> None:
    """Upsert LC 2128 with Chinese solution notes (idempotent)."""
    con = sqlite3.connect(str(DB_PATH))
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, notes, description FROM problems WHERE leetcode_id = ?",
            (LEETCODE_ID,),
        )
        row = cur.fetchone()

        tags_json = json.dumps(TAGS, ensure_ascii=False)
        company_tags_json = json.dumps(COMPANY_TAGS, ensure_ascii=False)

        if row is None:
            # Insert new row. LC 2128 is Premium and was not previously seeded.
            cur.execute(
                """
                INSERT INTO problems (
                    leetcode_id, title, url, difficulty, tags, pattern, category,
                    company_tags, priority, is_completed, comfort_level,
                    description, description_source, notes, last_attempted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    LEETCODE_ID,
                    TITLE,
                    URL,
                    DIFFICULTY,
                    tags_json,
                    PATTERN,
                    CATEGORY,
                    company_tags_json,
                    2,
                    1,
                    3,
                    DESCRIPTION,
                    "leetcode",
                    NOTES,
                ),
            )
            con.commit()
            new_id = cur.lastrowid
            print(f"[INSERT] problem id={new_id} (LC {LEETCODE_ID}) inserted")
            print(f"  notes length: {len(NOTES)}")
            print(f"  description length: {len(DESCRIPTION)}")
            return

        pid, existing_notes, existing_desc = row
        if existing_notes == NOTES and existing_desc == DESCRIPTION:
            print(f"[SKIP] problem id={pid} (LC {LEETCODE_ID}) already up to date")
            return

        cur.execute(
            """
            UPDATE problems SET
                title = ?,
                url = ?,
                difficulty = ?,
                tags = ?,
                pattern = ?,
                category = ?,
                company_tags = ?,
                is_completed = 1,
                comfort_level = 3,
                description = ?,
                description_source = 'leetcode',
                notes = ?,
                last_attempted_at = datetime('now')
            WHERE id = ?
            """,
            (
                TITLE,
                URL,
                DIFFICULTY,
                tags_json,
                PATTERN,
                CATEGORY,
                company_tags_json,
                DESCRIPTION,
                NOTES,
                pid,
            ),
        )
        con.commit()
        print(f"[UPDATE] problem id={pid} (LC {LEETCODE_ID}) updated")
        print(f"  notes length: {len(NOTES)}")
        print(f"  description length: {len(DESCRIPTION)}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
