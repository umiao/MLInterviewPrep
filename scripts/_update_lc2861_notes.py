"""Idempotent: write LC 2861 notes (Maximum Number of Alloys) —
binary-search-on-answer canonical pattern.

User's solving insight (worth preserving in notes):
当二分搜索写成 "成功就 beg = mid + 1"，循环终止时 beg/end 指向**第一个失败**
的 alloy 数量；要么用 ans 跟踪，要么最后返回 beg - 1，几乎不可能直接返回 mid。

Run: python scripts/_update_lc2861_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 2861
PATTERN = "binary_search"
FAMILY = "binary_search_on_answer"
SENTINEL = "<!-- LC2861_NOTES_V1 -->"

NOTES = """<!-- LC2861_NOTES_V1 -->
## 题目定位
LC 2861 Maximum Number of Alloys —— **二分答案 (binary search on answer)**
家族的标准模板题。给 $k$ 台机器、$n$ 种金属、初始库存 stock、单价 cost、
预算 budget，机器 $i$ 造 1 单位 alloy 需要 `composition[i][j]` 单位金属
$j$；**所有 alloy 必须用同一台机器造**。求最多能造几个 alloy。

**关键洞察**：可造数量 $x$ 满足 **单调性**——若 $x$ 个能造出来，则任意
$x' < x$ 也能造（少买金属即可）；反之 $x$ 不行则 $x+1$ 也不行。
"can produce $x$ alloys" 是关于 $x$ 的**布尔单调谓词** → 二分答案。

## 思路
1. **定义谓词** `check(val)`：是否**存在某台机器** $i$ 能在预算内造 val 个
   alloy。对每台机器算 `requiredBudget = Σ_j max(0, comp[i][j]*val - stock[j]) * cost[j]`，
   只要任一机器的 requiredBudget ≤ budget 就返回 True。
2. **二分上下界**：
   - 下界 `beg = 0`（一个都不造永远 OK）
   - 上界 `end = budget + max(stock) + 1`（粗放但安全：即使每个 alloy
     只需 1 单位某金属，库存 + 用预算全买这种金属也只能造这么多）
3. **二分模板**（**find largest valid**）：
   - `check(mid)` True：可行域更大，`ans = max(ans, mid); beg = mid + 1`
   - `check(mid)` False：缩右，`end = mid`

## 核心代码
```python
class Solution:
    def maxNumberOfAlloys(
        self, n: int, k: int, budget: int,
        composition: list[list[int]], stock: list[int], cost: list[int],
    ) -> int:
        beg, end = 0, budget + max(stock) + 1

        def check(val: int) -> bool:
            for i in range(k):
                required_budget = 0
                for j in range(n):
                    required = composition[i][j] * val
                    if required > stock[j]:
                        required_budget += (required - stock[j]) * cost[j]
                if required_budget <= budget:
                    return True
            return False

        ans = 0
        while beg < end:
            mid = beg + (end - beg) // 2
            if check(mid):
                ans = max(ans, mid)
                beg = mid + 1
            else:
                end = mid
        return ans
```

### 走查（LC 官方 Example 2：n=3, k=2, budget=15, comp=[[1,1,1],[1,1,10]], stock=[0,0,100], cost=[1,2,3]）
- 机器 1：每个 alloy 要 (1,1,10) 金属。stock 已有 (0,0,100)，造 $x$ 个需买
  $(x, x, \\max(0, 10x-100))$ 单位 → 成本 $x \\cdot 1 + x \\cdot 2 + \\max(0, 10x-100) \\cdot 3$
  = $3x + \\max(0, 30x-300)$。
- $x=10$：成本 $30 + 0 = 30 > 15$ ✗
- $x=5$：成本 $15 + 0 = 15 ≤ 15$ ✓
- 二分收敛到 5。预期答案 5。✓

## 关键技巧 / 易错点（**user 自己踩到的坑写在最前**）

### [PITFALL] 二分模板"成功就 +1, 终止后 beg 指向第一个失败值"
> user 的原话："如果我们在满足的时候总是 `beg = mid + 1`，最后得到的结果
> 几乎总是需要 `-1` 的，因为我们找到的是**第一个满足不了 / 做不出来的** alloy 数量"

这是 **find largest valid** 二分模板的标准陷阱。三种等价正确写法：

| 写法 | 终止时 | 返回 |
| --- | --- | --- |
| **A. 显式跟踪 ans**（user 用的） | `beg == end`，指向第一个 fail | `ans` |
| **B. 不跟踪，循环后修正** | `beg == end`，指向第一个 fail | `beg - 1` |
| **C. lower_bound 风格反转谓词** | 把 `check'(x) = not check(x)` 当做"找第一个 True" | `beg - 1` |

写法 A 最稳，**不必心算"我现在要 -1 还是不要"**——`ans` 永远是**已知可行**
的最大值。代价仅是一行赋值。**`ans = max(ans, mid)` 中的 `max` 其实可写
`ans = mid`**，因为 `check` 单调性保证后续被接受的 mid 严格更大；保留
`max` 只是 defensive。

### 其它易错点
1. **`end` 只用 `budget` 而不加 `max(stock)`**：边界情况下 stock[j] 已经
   够造很多 alloy（比如机器 0 只用金属 0 而 stock[0]=10^9），`end = budget`
   会人为压低答案。题目里 stock $\\le 10^9$、budget $\\le 10^8$，stock 主导。
2. **谓词写成 "对所有机器都满足"**：题目说造 alloy 必须**全用同一台机器**，
   所以是 `any` 不是 `all`。误写成 all 直接全错。
3. **谓词内部 `requiredAlloy > stock[j]` 写成 `>=`**：当 `comp[i][j]*val == stock[j]`
   时不需要花钱，写 `>=` 不会出错（差额为 0），但写 `<` 反向条件就会漏；
   想清楚 `max(0, ...)` 的语义最稳。
4. **谓词中累加溢出（C++/Java）**：$\\text{val} \\le 10^9$、$\\text{comp} \\le 100$、
   $\\text{cost} \\le 100$ → 单项可达 $10^{13}$，**必须 `long long`**。Python 无忧。
5. **`mid = (beg + end) // 2` 在 C++/Java 溢出**：`mid = beg + (end - beg) // 2`
   是肌肉记忆。Python 不会溢出但保留写法跨语言通用。
6. **谓词早返回的位置**：在**机器循环内**就 `return True`（user 写法），
   而不是先把所有机器算完取 min——前者 $O(kn)$ 最好情况就 $O(n)$ 退出，
   后者总是 $O(kn)$。

## 复杂度
- 二分轮数 $T = O(\\log(\\text{budget} + \\max(\\text{stock})))$ ≈ $O(\\log(2 \\cdot 10^9)) \\approx 31$。
- 每轮谓词 $O(k \\cdot n)$。
- 总：$O(k \\cdot n \\cdot \\log(\\text{budget} + \\max(\\text{stock})))$。
  约束下 $k, n \\le 100$ → $\\sim 100 \\cdot 100 \\cdot 31 = 3 \\cdot 10^5$ 操作，飞快。

## 题目家族（Binary Search on Answer / 二分答案）
所有这些题的套路都是 "找最大的 $x$ 使得 $f(x)$ 为真" 或 "找最小的 $x$ 使得
$f(x)$ 为真"，关键在**写出单调谓词**：

- **LC 875** Koko Eating Bananas：找最小吃速 $k$ 使得 $\\sum \\lceil \\text{piles}[i] / k \\rceil \\le H$。
  *与本题对偶*——这是 find smallest valid，本题是 find largest valid。
- **LC 1011** Capacity to Ship Packages Within D Days：找最小载重使得装船天数 ≤ D。
- **LC 410** Split Array Largest Sum：把数组分成 $m$ 段，最小化最大段和。
  谓词：`能否把数组分成 ≤ m 段, 每段和 ≤ x`。
- **LC 1283** Find the Smallest Divisor Given a Threshold：和 LC 875 几乎一样。
- **LC 2226** Maximum Candies Allocated to K Children：和 LC 2861 同款 find largest valid，
  谓词 `Σ floor(candies[i] / x) >= k`。
- **LC 1631** Path With Minimum Effort：二分答案 + BFS 验证，谓词复杂度更高。
- **LC 1482** Minimum Days to Make Bouquets：find smallest valid + 滑窗谓词。

**面试 30 秒 pitch**：
> "可造数量是单调的——能造 $x$ 个就一定能造 $x-1$ 个。把它转成 boolean 谓词
> '存在机器 $i$ 在预算内造 $x$ 个 alloy？'，对 $x$ 二分。谓词 $O(kn)$，
> 二分 $O(\\log V)$ 轮。模板用 'find largest valid'：成功 `beg = mid + 1`
> 同时跟踪 ans，避免最后还要心算 -1。"

## Follow-up
1. **如果改成必须用同**一台机器但**可以混合策略**（先造 a 个机器 0 的 alloy，
   再造 b 个机器 1 的）：单台机器假设破裂，要重新建模——可能退化成多维背包。
   *本题保证全部用同一台*，所以直接 any-machine 二分。
2. **如果允许买金属又允许卖金属**：仍可二分，但 requiredBudget 要算净额，
   注意符号。
3. **如果 cost 巨大、需要 hot path 的二分**：把 check 的内层 j 循环用 numpy
   向量化（`np.maximum(0, comp[i] * val - stock) @ cost`）——Python 解释器
   开销在 $k = n = 100$ 已经够低，但更大的 $kn$ 会受益。
"""


def main() -> None:
    """Rewrite LC 2861 notes; idempotent via sentinel."""
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
            print(f"[UNCHANGED] LC {LC_ID} id={pid} notes (sentinel present)")
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
