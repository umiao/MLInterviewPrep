"""One-shot: insert LC 1564 (Put Boxes Into Warehouse I) with Pinterest tag + Chinese notes.

T-P1-394 deliverable. Idempotent: creates problem row if missing, tags Pinterest, writes notes.
"""
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 1564 - Put Boxes Into Warehouse I (前缀最小 + 贪心)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾
给定两个数组：
- `boxes[i]` - 第 i 个箱子的高度。
- `warehouse[j]` - 第 j 号房间的高度（只能**从左侧入口**进入，房间按 0..n-1 排列）。

每个房间**最多放一个箱子**；箱子 b 能放进房间 j 当且仅当 `b <= warehouse[k]` 对**所有 k <= j** 成立（因为必须穿过前面所有房间）。问最多能放几个箱子。

约束：`1 <= boxes.length, warehouse.length <= 1e5`，高度 `1..1e9`。

### 关键洞察：前缀最小 "有效高度"

因为箱子要从左走到第 j 号房间，途中被**最矮的房间**卡住，所以第 j 号房间的**有效限高**：

> `eff[j] = min(warehouse[0..j])`  （单调不增）

此预处理后，warehouse 可视为一条**单调不增**的"有效高度"走廊。

### 贪心策略：大箱配大房（从后往前塞）

- `eff` 单调不增，所以**最右边的房间最矮**、**最左边的房间最高**。
- 把 `boxes` **降序排列**。
- 指针 `i = n-1`（最右房间开始）。遍历降序的箱子：若 `box <= eff[i]`，放入并 `i--`；否则跳过（这个箱子太大，任何**剩余**房间也装不下，因为 eff[0..i] 都 >= eff[i]... 等等，这里要小心）。

**等价、更直观的等价写法**（推荐面试用）：

- 把 `eff` **反过来**看，从右向左就是**单调不减**。
- 双指针：`bi` 指向已升序排的 boxes 最小端，`wi` 指向 eff 最右端（最矮端）。
- 若 `boxes[bi] <= eff[wi]`：放进去（答案 +1），`bi++, wi--`；否则（此箱太大塞不进当前最矮）`wi--`（这个最矮房间永远装不下当前及更大箱，跳过）。

```python
def maxBoxesInWarehouse(boxes: list[int], warehouse: list[int]) -> int:
    n = len(warehouse)
    eff = [0] * n
    eff[0] = warehouse[0]
    for j in range(1, n):
        eff[j] = min(eff[j - 1], warehouse[j])  # 前缀最小

    boxes.sort()           # 升序
    ans, bi = 0, 0
    m = len(boxes)
    for wi in range(n - 1, -1, -1):        # 从最矮房间开始
        if bi < m and boxes[bi] <= eff[wi]:
            ans += 1
            bi += 1
    return ans
```

**时间 O(n + m log m)，空间 O(n)**（eff 数组；若允许原地改 warehouse 则 O(1) 额外空间）。

### 为什么贪心正确（交换论证）

假设最优解 OPT 放了 k 个箱子。考虑按房间编号从**右向左**依次遍历房间：

- 若最优解在当前最矮房间放了某箱 b，则 b 必然 <= eff(当前)。我们的算法此时会选"**当前最小的未放箱** b'"，`b' <= b <= eff(当前)`，可放；所以用 b' 替代 b 不会变差（b 仍可用于更高的房间）。
- 若最优解在当前房间**没放**箱子，我们算法也不放（当前最矮塞不下最小未放箱时跳过）——等价或更优。

归纳可知：算法放的数量 >= OPT。又 OPT 是最优，故相等。

### 示例追踪

`boxes = [4, 3, 4, 1], warehouse = [5, 3, 3, 4, 1]`
- eff = [5, 3, 3, 3, 1]（单调不增）
- boxes 排序 -> [1, 3, 4, 4]
- wi=4 (eff=1): 1 <= 1, 放，bi=1, ans=1
- wi=3 (eff=3): 3 <= 3, 放，bi=2, ans=2
- wi=2 (eff=3): 4 > 3, 跳过
- wi=1 (eff=3): 4 > 3, 跳过
- wi=0 (eff=5): 4 <= 5, 放，bi=3, ans=3
- **Total = 3** [OK]

`boxes = [1, 2, 2, 3, 4], warehouse = [3, 4, 1, 2]`
- eff = [3, 3, 1, 1]
- boxes 排序 -> [1, 2, 2, 3, 4]
- wi=3 (1): 1<=1 放，bi=1, ans=1
- wi=2 (1): 2>1 跳
- wi=1 (3): 2<=3 放，bi=2, ans=2
- wi=0 (3): 2<=3 放，bi=3, ans=3
- **Total = 3** [OK]

### 与 LC 1580 (Warehouse II) 的区别

| 维度 | LC 1564 (I) | LC 1580 (II) |
|------|-------------|--------------|
| 入口 | 只有**左侧** | **两侧**都可进 |
| 有效高度 | `eff[j] = min(warehouse[0..j])`，单调不增 | `eff[j] = min(左前缀min, 右后缀min)` 的**上包络** |
| 预处理 | 一次前缀 min | 双向扫描，每个房间取**左 min** 与**右 min** 的**较大者**（即从两边都能进入的最大高度） |
| 贪心主体 | 同 | 把 eff 排序后与 boxes 升序双指针即可（因为两侧皆可进入，eff 不一定单调） |

口诀：**I 题有方向性（前缀 min）；II 题无方向性（排序 eff）**。

### 相关题 / 套路迁移

| 题号 | 连接 |
|------|------|
| **LC 1580** Put Boxes II | 同族；双入口 |
| **LC 11** Container With Most Water | 双指针 + 短板决定容量 |
| **LC 42** Trapping Rain Water | 双向前缀 min/max 思路 |
| **LC 881** Boats to Save People | 双指针 + 升序贪心配对 |
| **LC 2064** Min Largest Items | 贪心 + 二分猜答案（另一种"装箱"风格） |

### 套路识别

1. "**从某个方向进入**的容器/通道，沿途被最小值卡住" -> 想到**前缀 min** 做"**有效高度**"预处理。
2. "**最多装多少个**，每个单元最多放一个物件，且物件有大小约束" -> **两侧排序 + 双指针/贪心**。
3. 面试套路模板：`eff[j] = min-accumulate; sort(items); two-pointer (from the tightest constraint)`。

### 陷阱与边界

1. **不要忘记前缀 min**：直接对 warehouse 排序会丢失"必须穿过左边"的约束。
2. **m != n**：箱子数和房间数可能不等；循环时要用 `bi < m` 守卫。
3. **空 warehouse / 空 boxes**：题目约束 `>=1`，但实现上注意 `eff[0] = warehouse[0]` 不要越界。
4. **重复高度**：`<=` 不是 `<`，相等可放。
5. **一个箱子塞不进任何房间**：直接跳过，`bi` 不动（等价：该箱子被丢弃，但其实我们从小箱优先，最小都塞不进的房间以上也塞不进，所以**跳过房间**而不是箱子）。**注意：正确的是跳过房间，而不是箱子！**——因为"最矮房间装不下最小箱"意味着这个房间永远装不下任何未放箱（都 >= 最小）。**绝不能跳过箱子**（更大的房间或许能装最小箱）。
6. **箱子太大的极端**：所有箱子都 > eff[0]，答案 = 0。
7. **箱子都很小**：`ans = min(m, n)`。

### 复杂度总结

| 步骤 | 时间 | 空间 |
|------|------|------|
| 前缀 min | O(n) | O(n) |
| 排序 boxes | O(m log m) | O(1) |
| 双指针 | O(n + m) | O(1) |
| **总计** | **O(n + m log m)** | **O(n)** |

### 45 秒口播脚本（面试开头）

> "因为箱子从左侧进入，第 j 号房间的**有效限高**就是 warehouse 从 0 到 j 的最小值——一次前缀 min 即可预处理，得到一条**单调不增**的'有效走廊'。然后贪心：把箱子升序排好，从最矮的房间开始扫描，若当前最小未放箱能塞就塞；塞不下就放弃这个房间（因为它装不下任何未放箱，未放箱都 >= 最小）。O(n + m log m)，空间 O(n)。与 LC 1580 的差别仅在于 II 允许两侧进入，此时 eff 不再单调，要做**双向**前缀 min 的'上包络'后再排序配对。"
"""


def main() -> None:
    """Insert LC 1564 if missing, tag Pinterest, update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 1564")
    row = c.fetchone()
    if row:
        pid, existing = row
        tags = json.loads(existing) if existing else []
        if "Pinterest" not in tags:
            tags.append("Pinterest")
        c.execute(
            "UPDATE problems SET company_tags = ?, notes = ? WHERE id = ?",
            (json.dumps(tags, ensure_ascii=False), NOTES, pid),
        )
        print(f"[UPDATE] LC 1564 (id={pid}) tags={tags} notes_len={len(NOTES)}")
    else:
        c.execute(
            """INSERT INTO problems
            (leetcode_id, title, url, difficulty, tags, pattern, category,
             source, company_tags, priority, is_completed, comfort_level,
             created_at, notes)
            VALUES (?, ?, ?, 'medium', ?, ?, 'algorithm', 'pinterest_prep',
                    ?, 2, 0, 0, ?, ?)""",
            (
                1564,
                "Put Boxes Into Warehouse I",
                "https://leetcode.com/problems/put-boxes-into-warehouse-i/",
                json.dumps(["Array", "Greedy", "Sorting"]),
                "Greedy",
                json.dumps(["Pinterest"]),
                datetime.now(timezone.utc).isoformat(),
                NOTES,
            ),
        )
        print(f"[NEW] LC 1564 inserted, notes_len={len(NOTES)}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
