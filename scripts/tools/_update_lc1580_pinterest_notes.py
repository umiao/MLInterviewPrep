# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: insert LC 1580 (Put Boxes Into Warehouse II) with Pinterest tag + Chinese notes.

T-P1-395 deliverable. Idempotent: creates problem row if missing, tags Pinterest, writes notes.
Harder variant of LC 1564: boxes may enter from EITHER end of the warehouse.
"""
import json
import sqlite3
from datetime import UTC, datetime

DB_PATH = "data/mle_prep.db"

NOTES = r"""## LC 1580 - Put Boxes Into Warehouse II (双向入口 + 排序贪心)

> Pinterest must-do list (2025-11 cutoff). See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目回顾

与 [LC 1564](./) 同设定，但**箱子可从左入口或右入口进入**仓库。每个房间最多放一个，箱子能放进房间 j 当且仅当存在**某一侧入口**的路径，使路径上所有房间的高度都 >= 该箱子高度。

约束：`1 <= boxes.length, warehouse.length <= 1e5`，高度 `1..1e9`。

### 关键洞察：双向前缀 min 的"上包络"

对房间 j，从左进入受 `leftMin[j] = min(warehouse[0..j])` 限制；从右进入受 `rightMin[j] = min(warehouse[j..n-1])` 限制。

> **箱子可选更宽松的一侧**，所以房间 j 的**有效限高** `eff[j] = max(leftMin[j], rightMin[j])`。

直观图像：沿 x 轴画 `leftMin`（从左向右单调不增）和 `rightMin`（从左向右单调不减，在两端取到全局 min）。二者**在中间交汇**，`eff` 取二者**较高者**形成一个"**V 字的上包络**"——中间某一段较矮（两侧进入都受中段拖累），两端较高。

**关键性质**：`eff` **不再单调**（不像 1564 的单调不增），因此 1564 的"从最矮房间开始扫描"写法失效；必须**排序 eff** 后与箱子配对。

### 贪心策略：双排序 + 双指针

1. 计算 `eff[j] = max(leftMin[j], rightMin[j])`，得长度 n 的数组。
2. 将 `eff` 与 `boxes` 都**升序排序**。
3. 双指针从小到大配对：若 `boxes[bi] <= eff[wi]`，放入（`bi++, wi++, ans++`）；否则当前房间 `wi` 太矮连最小未放箱都装不下 -> **跳过房间** (`wi++`)。

```python
def maxBoxesInWarehouse(boxes: list[int], warehouse: list[int]) -> int:
    n = len(warehouse)
    left_min = [0] * n
    right_min = [0] * n
    left_min[0] = warehouse[0]
    for j in range(1, n):
        left_min[j] = min(left_min[j - 1], warehouse[j])
    right_min[n - 1] = warehouse[n - 1]
    for j in range(n - 2, -1, -1):
        right_min[j] = min(right_min[j + 1], warehouse[j])
    eff = [max(left_min[j], right_min[j]) for j in range(n)]

    eff.sort()
    boxes.sort()
    ans, bi, m = 0, 0, len(boxes)
    for wi in range(n):
        if bi < m and boxes[bi] <= eff[wi]:
            ans += 1
            bi += 1
        # else: room too short for the smallest remaining box -> skip room
    return ans
```

**时间 O(n log n + m log m)，空间 O(n)**。

### 为什么不能跳过箱子、只能跳过房间（同 1564 的陷阱）

若 `eff[wi] < boxes[bi]`（最矮未用房间装不下最小未放箱），说明**没有任何未放箱**能放进此房间（其他箱 >= `boxes[bi]` > `eff[wi]`）-> 果断舍弃此房间。反之，若跳过箱子，我们就错失了"最小箱可能匹配更高房间"的机会，浪费机会。

### 交换论证（正确性证明）

将 `eff` 与 boxes 升序排序后，考虑一个**反证**：若算法放了 k 个箱子而 OPT 放了 k+1 个，对比二者的"已用房间集合" A (算法) vs B (OPT) 在升序 eff 上的位置：

- OPT 用了 k+1 个房间，每个房间分配了一个**能放入**的箱子。把 OPT 的分配按 `eff` 升序重排，再按箱子升序重排后，最小箱必放入最矮能容纳它的房间（不失一般性，排序配对是最优的）。
- 算法正是这么做的，故算法放的数量必 >= OPT 的"最优排序配对数量" = k+1，矛盾。

### 示例追踪

`boxes = [1, 2, 2, 3, 4], warehouse = [3, 4, 1, 2]`
- leftMin  = [3, 3, 1, 1]
- rightMin = [1, 1, 1, 2]
- eff      = [max(3,1), max(3,1), max(1,1), max(1,2)] = [3, 3, 1, 2]
- sort(eff) -> [1, 2, 3, 3]；sort(boxes) -> [1, 2, 2, 3, 4]
- wi=0 eff=1: 1<=1 放, ans=1, bi=1
- wi=1 eff=2: 2<=2 放, ans=2, bi=2
- wi=2 eff=3: 2<=3 放, ans=3, bi=3
- wi=3 eff=3: 3<=3 放, ans=4, bi=4
- 剩余箱 [4] 无房间 -> **Total = 4** [OK]

`boxes = [3, 5, 5, 2], warehouse = [2, 1, 3, 4, 5]`
- leftMin  = [2, 1, 1, 1, 1]
- rightMin = [1, 1, 3, 4, 5]
- eff      = [2, 1, 3, 4, 5]
- sort(eff) -> [1, 2, 3, 4, 5]；sort(boxes) -> [2, 3, 5, 5]
- wi=0 eff=1: 2>1 跳房间
- wi=1 eff=2: 2<=2 放, ans=1, bi=1
- wi=2 eff=3: 3<=3 放, ans=2, bi=2
- wi=3 eff=4: 5>4 跳房间
- wi=4 eff=5: 5<=5 放, ans=3, bi=3
- **Total = 3** [OK]

### 与 LC 1564 (Warehouse I) 的区别

| 维度 | LC 1564 (I) | LC 1580 (II) |
|------|-------------|--------------|
| 入口 | 只有**左侧** | **两侧**都可进 |
| eff 计算 | `leftMin[j]` 一次前缀 | `max(leftMin[j], rightMin[j])` 双向 |
| eff 形态 | **单调不增** | 一般**非单调**（V 形或更复杂） |
| 贪心写法 | 从最矮房间 (索引 n-1) 扫，可不排 eff | **必须排序 eff** 再双指针 |
| 额外成本 | O(n) eff | O(n log n) 排序 eff |

口诀：**I 题有方向性（前缀 min 即可）；II 题无方向性（双向 min 再排序）**。

### 套路识别

1. "**可从两端进入**的容器/通道" -> **左 min + 右 min 的较大者** 作为有效约束。
2. 只要 eff 不再单调，就**排序 eff** 后用"最小与最小配对"的升序双指针。
3. 箱子装不下最矮房间时：**跳过房间**，绝不跳过箱子。

### 相关题 / 套路迁移

| 题号 | 连接 |
|------|------|
| **LC 1564** Put Boxes I | 同族；单入口；eff 单调 |
| **LC 42** Trapping Rain Water | 双向前缀 min/max 套路 |
| **LC 11** Container With Most Water | 双指针 + 短板约束 |
| **LC 881** Boats to Save People | 排序 + 双指针配对 |
| **LC 1705** Max Eaten Apples | 贪心 + 堆（选更紧的约束优先） |

### 陷阱与边界

1. **eff 误写为 min**：`max(leftMin, rightMin)` 而**非 min**——箱子选**更宽松**的入口，故取二者较大。
2. **单调假设失效**：不能沿用 1564 "从最矮房间扫" 的写法；必须排序。
3. **m != n**：循环守卫 `bi < m`。
4. **边界 j=0 / j=n-1**：leftMin[0] = warehouse[0], rightMin[n-1] = warehouse[n-1]。
5. **全部箱子过大**：答案 = 0；所有房间都跳过。
6. **n = 1**：eff = warehouse[0]，与 1564 等价。
7. **重复高度**：`<=` 不是 `<`，相等可放。

### 复杂度总结

| 步骤 | 时间 | 空间 |
|------|------|------|
| 双向 min | O(n) | O(n) |
| 排序 eff | O(n log n) | O(1) |
| 排序 boxes | O(m log m) | O(1) |
| 双指针 | O(n + m) | O(1) |
| **总计** | **O(n log n + m log m)** | **O(n)** |

### 45 秒口播脚本（面试开头）

> "因为箱子可以从左或右侧进入，每个房间的有效限高 = max(从左进来的前缀 min, 从右进来的后缀 min)——箱子选**更宽松**的一侧。这使 eff 不再单调，所以和 1564 不同，不能再'从最矮房间扫'。把 eff 和 boxes 都升序排序，双指针从小到大配对：最小箱能塞进最矮能容的房间就放；若当前最矮房间连最小未放箱都装不下，就跳过**房间**（不能跳箱子，因为最小箱也许还能塞进更高的房间）。O((n+m) log (n+m)) 时间、O(n) 空间。"
"""


def main() -> None:
    """Insert LC 1580 if missing, tag Pinterest, update notes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, company_tags FROM problems WHERE leetcode_id = 1580")
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
        print(f"[UPDATE] LC 1580 (id={pid}) tags={tags} notes_len={len(NOTES)}")
    else:
        c.execute(
            """INSERT INTO problems
            (leetcode_id, title, url, difficulty, tags, pattern, category,
             source, company_tags, priority, is_completed, comfort_level,
             created_at, notes)
            VALUES (?, ?, ?, 'hard', ?, ?, 'algorithm', 'pinterest_prep',
                    ?, 2, 0, 0, ?, ?)""",
            (
                1580,
                "Put Boxes Into Warehouse II",
                "https://leetcode.com/problems/put-boxes-into-warehouse-ii/",
                json.dumps(["Array", "Greedy", "Sorting"]),
                "Greedy",
                json.dumps(["Pinterest"]),
                datetime.now(UTC).isoformat(),
                NOTES,
            ),
        )
        print(f"[NEW] LC 1580 inserted, notes_len={len(NOTES)}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
