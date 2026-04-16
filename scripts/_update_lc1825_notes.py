"""Idempotent: mark LC 1825 complete and attach Chinese solution notes.

LC 1825 Finding MK Average -- "滑动窗口 + 三桶 SortedList + 增量和" 的
canonical 题; 属于 stateful_ds_design 家族, 是 LC 480 (sliding median)
的三桶推广版本.

Run: python scripts/_update_lc1825_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 1825
PATTERN = "sliding window + sorted list"
SENTINEL = "<!-- LC1825_NOTES -->"

NOTES = """<!-- LC1825_NOTES -->
## 题目定位
**stateful_ds_design 家族** -- MK Average 是"滑动窗口 + 分桶维护顺序统计量"的
进阶题, 可以视作 LC 480 Sliding Window Median 的**三桶推广**: 前者维护
两堆中位数, 这题维护三桶"去掉最小 k 个和最大 k 个后的中段平均"。

- `MKAverage(m, k)`: 初始化, 关心最近 $m$ 个元素, 去掉最小 $k$ 个和最大 $k$ 个。
- `addElement(num)`: 把 `num` 加入流。
- `calculateMKAverage()`: 若流长度 $< m$ 返回 `-1`; 否则返回最近 $m$ 个元素中,
  剔除最小 $k$ 与最大 $k$ 后, 剩余 $m-2k$ 个元素的**向下取整平均**。

**数据规模**: `m` 可达 $10^5$, `addElement` 调用最多 $10^5$ 次, `calculate`
最多 $10^5$ 次 -- 每次 `calculate` 重算 $O(m \\log m)$ 排序显然 TLE, 必须**增量维护**。

## 核心洞察（必背）
把最近 $m$ 个元素拆成三个**有序桶** + 一个**增量和**:
- `low`: 最小的 $k$ 个 (SortedList, 大小恒为 $k$, 除非窗口未满)
- `mid`: 中间的 $m-2k$ 个 (SortedList, 参与平均)
- `high`: 最大的 $k$ 个 (SortedList, 大小恒为 $k$)
- `sum_mid`: `mid` 的和, 增量维护; `calculate` 直接 `sum_mid // (m-2k)` 是 $O(1)$。
- `window`: `deque` 按插入顺序保存最近 $m$ 个元素, 用于**精确驱逐**最旧那一个。

**不变式** (稳态, 即窗口已满): `|low| == k`, `|high| == k`, `|mid| == m-2k`,
桶内值全序 $\\max(\\text{low}) \\le \\min(\\text{mid}) \\le \\max(\\text{mid}) \\le \\min(\\text{high})$。

`addElement` 的做法是: **先按当前阈值把新数放入正确桶, 再驱逐队首旧值
(若窗口超长), 最后 rebalance 到三桶大小满足不变式**。rebalance 不管之前做了
几次插删, 只要照着"缺的往里补, 多的往外推"的公式跑几条 `while`, 就能
把状态收敛回不变式 -- 不需要手工枚举 6 种 case。

## Python 代码（面试可直接默写）
```python
from sortedcontainers import SortedList
from collections import deque

class MKAverage:
    def __init__(self, m: int, k: int):
        self.m, self.k = m, k
        self.mid_size = m - 2 * k
        self.window = deque()
        self.low = SortedList()
        self.mid = SortedList()
        self.high = SortedList()
        self.sum_mid = 0

    def addElement(self, num: int) -> None:
        self._insert(num)
        self.window.append(num)
        if len(self.window) > self.m:
            self._erase(self.window.popleft())
        self._rebalance()

    def calculateMKAverage(self) -> int:
        if len(self.window) < self.m:
            return -1
        return self.sum_mid // self.mid_size

    # -- 内部: 按当前阈值落桶 --
    def _insert(self, x: int) -> None:
        if self.low and x <= self.low[-1]:
            self.low.add(x)
        elif self.high and x >= self.high[0]:
            self.high.add(x)
        else:
            self.mid.add(x)
            self.sum_mid += x

    def _erase(self, x: int) -> None:
        if self.low and x <= self.low[-1]:
            self.low.remove(x)
        elif self.high and x >= self.high[0]:
            self.high.remove(x)
        else:
            self.mid.remove(x)
            self.sum_mid -= x

    # -- 内部: 把 sizes 收敛回不变式 --
    def _rebalance(self) -> None:
        # low 过满 -> 推最大项进 mid
        while len(self.low) > self.k:
            v = self.low.pop(-1); self.mid.add(v); self.sum_mid += v
        # high 过满 -> 推最小项进 mid
        while len(self.high) > self.k:
            v = self.high.pop(0); self.mid.add(v); self.sum_mid += v
        # low 过少 -> 从 mid 拉最小项补
        while len(self.low) < self.k and self.mid:
            v = self.mid.pop(0); self.sum_mid -= v; self.low.add(v)
        # high 过少 -> 从 mid 拉最大项补
        while len(self.high) < self.k and self.mid:
            v = self.mid.pop(-1); self.sum_mid -= v; self.high.add(v)
```

## 为什么 rebalance 不需要枚举 6 种 case
插入 + 驱逐最多动 **两个桶** (插入一次 + 删除一次), 每个桶大小最多偏离
不变式 $\\pm 1$。上面四条 `while` 的顺序 **"过满先出, 再从 mid 补过少"**
保证了:
1. `low`/`high` 过满的元素先被推进 `mid` -- 此时 `mid` 可能暂时过大, 但
   阈值已回到正确位置。
2. 随后 `low`/`high` 过少时, 再从 `mid` 两端拉元素 -- 拉的一定是
   "当前 mid 里最小/最大" 的那一批, 正是应当属于 `low`/`high` 的元素。

每次 `addElement` 里 `while` 循环累计只会跑 $O(1)$ 次 (最多 2 次), 因为
偏离量有界。所以 rebalance 是 $O(\\log m)$ 摊还。

## 走查示例
`MKAverage(3, 1)` (m=3, k=1, mid_size=1):
```
addElement(3): window=[3], low=[], mid=[3], high=[], sum_mid=3
  rebalance: low 过少但 mid 空不动, high 过少但 mid 空不动 -> 暂不合法
             (窗口未满, calculate 还返回 -1, 不用维持不变式)
addElement(1): window=[3,1], _insert(1)
  low 空 -> 进 mid, mid=[1,3], sum_mid=4; rebalance -> 仍不满, OK
addElement(10): window=[3,1,10], _insert(10)
  low 空 -> 进 mid, mid=[1,3,10], sum_mid=14
  rebalance: low<k (0<1), mid pop(0)=1, mid=[3,10], sum_mid=13, low=[1]
             high<k (0<1), mid pop(-1)=10, mid=[3], sum_mid=3, high=[10]
  稳态: low=[1], mid=[3], high=[10], sum_mid=3
calculate() -> 3 // 1 = 3  ✓
addElement(5): window=[3,1,10,5], _insert(5)
  low[-1]=1, 5>1; high[0]=10, 5<10 -> 进 mid, mid=[3,5], sum_mid=8
  窗口超 m=3, popleft=3, _erase(3): 在 mid, mid=[5], sum_mid=5
  rebalance: 三桶 sizes = [1,1,1] 已满足, 无动作
calculate() -> 5 // 1 = 5  ✓
```

## 复杂度
- `addElement`: $O(\\log m)$ -- `SortedList.add/remove` 是 $O(\\log m)$,
  `deque` 两端 $O(1)$, rebalance 常数次桶搬运。
- `calculateMKAverage`: $O(1)$ -- 只是 `sum_mid // mid_size`。
- 空间: $O(m)$ -- 三桶总和恒为 $\\min(\\text{stream\\_len}, m)$。

相比朴素 "每次 calculate 排序 $O(m \\log m)$", 增量维护省掉一个 $m$ 因子;
相比"维护单一 SortedList 然后 `islice(k, m-k)` 算和" ($O(m)$ per calculate),
三桶 + `sum_mid` 把 calculate 压到 $O(1)$, 这是此题能过时限的关键。

## 易错点
1. **驱逐时必须从正确桶精确删**。`_erase` 的判断要严格用**当前阈值**
   (`low[-1]` 和 `high[0]`), 不能盲目 `if x in low: low.remove(x)`
   因为重复值可能同时存在 `low` 和 `mid` 里。
2. **`sum_mid` 增减的时机要对齐桶操作**。每当一个值进入 `mid` 就 `+= v`,
   离开 `mid` (驱逐或被 rebalance 推出) 就 `-= v`。最简单的记忆:
   **"碰 mid 就动 sum"**。
3. **同值重复**。`SortedList` 允许重复元素, 但 `remove(x)` 只删一个,
   这正是我们要的语义。注意不要改成 `set`。
4. **窗口未满 (`len(window) < m`) 时的行为**。规范里明确 `calculate` 返回 `-1`,
   但 `addElement` 仍要把元素正确放入桶中。我的实现里 rebalance 在窗口未满
   时会因为 `mid` 为空而短路, 整体状态可能暂时不满足不变式 --
   **这是允许的**, 因为不变式只在稳态 (窗口已满) 下才要求, 而 `calculate`
   直接返回 -1 不读桶。稳态达到后所有后续 `addElement` 都维持不变式。
5. **向下取整**。Python 的 `//` 对正数就是 floor, 而本题只涉及非负和
   (`sum_mid / mid_size`), 所以 `//` 直接可用; 若值域包含负数要小心
   `//` 的 floor 语义与 C 的截断语义差异。
6. **`m == 2k + 1`**? 测试用例保证 $m \\ge 2k + 1$, 即 `mid_size >= 1`,
   不会除以 0; 但如果在工程里推广到任意 `m,k`, 要加守卫。

## Follow-up 追问指针
- **两 heap + lazy deletion**: 用 `minHeap_low` 与 `maxHeap_high`, 中间用
  `SortedList` 或另一组 heap + 惰性计数维护。`addElement` 时把元素推入
  堆, 旧元素驱逐只打标记; `pop` 时循环弹出被标记的顶部。**常数更大**
  (heap 操作常数优于平衡树, 但 lazy 要维护哈希表统计过期数), 代码更长。
  面试可以作为"在没有 SortedList 时怎么办"的答案。
- **两 SortedList + prefix sum**? 不行 -- 要维护排序 + 和, `SortedList`
  不支持 $O(\\log n)$ 前缀和。**如果允许 $O(\\log^2 n)$**, 用 Fenwick /
  segment tree over value domain, 可同时支持"第 k 小" 和 "前缀和"。此时
  整个解法变成"值域 BIT + 按秩查前缀和", 常数大, 但**支持在线改 k**。
- **扩展到 `removeOldestN(n)` 或动态 m**: SortedList 桶方案很容易适配,
  只需要把 `window` 的 popleft 次数改成 n 次循环, rebalance 自动收敛;
  动态 m 需要改 `mid_size` 并连跑几次 rebalance, 依然是 $O(\\log m)$。
- **流式分位数 (quantile)**: 去掉最小 k 最大 k 的平均, 本质是 **truncated
  mean** (截尾均值), 是统计里常见的 robust estimator。把 k 推广成分位点
  $(\\alpha_1, \\alpha_2)$, 就是**流式截尾均值**; 工业实现 (Datadog DDSketch,
  T-Digest) 用的是近似分位, 精确版本就是本题思路, 只是桶数可以更多。
- **线段树 / BIT on value domain**: 如果值域有限 ($\\le 10^5$, 本题成立),
  开一棵权值线段树, 每个节点记 `(count, sum)`, 插删 $O(\\log V)$, 找
  "第 k 小的位置 + 前缀和" $O(\\log V)$, `calculate` = "前 m-k 个之和" -
  "前 k 个之和"。常数比 SortedList 更大但理论上一样 $O(\\log m)$, 且
  支持"动态改 k" 只需要两次 $O(\\log V)$ 查询。

## 一句话 pitch（面试 45 秒）
> 用三个 SortedList 分别保存最小 k、中间 m-2k、最大 k 这三桶, 再维护
> 中间桶的**增量和** `sum_mid`, 这样 `calculate` 是 $O(1)$ 直接整除;
> `addElement` 先按当前阈值落桶再驱逐队首旧值, 最后跑几条 `while` 把
> 三桶大小收敛回不变式 -- 不用手枚举 6 种 case, 因为每次最多偏离 ±1,
> rebalance 摊还只跑常数次搬运, 整体 $O(\\log m)$。空间 $O(m)$, 与调用
> 次数无关。这题的关键是认出"去掉两端、维护中段和"是 LC 480 中位数的
> 三桶推广, 再用增量和把 $O(m)$ 汇总压到 $O(1)$。
"""


def main() -> None:
    """Attach notes and mark LC 1825 as completed; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, _fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN

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
