"""Idempotent: write LC 384 notes (Shuffle an Array) + seed Uber tag.

LC 384 是 Fisher-Yates 洗牌算法的入门题。本脚本同时把 user 在 Discord 里的
两条洞察也写进 notes：
  (1) Fisher-Yates 与 reservoir sampling 共享同一个望远镜式概率分解；
  (2) sort-based shuffle (`sorted((random(), x) for x ...)`) 是合法的
      替代方案，在分布式 / SQL 场景下反而是首选。

Run: python scripts/_update_lc384_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 384
PATTERN = "fisher_yates_shuffle"
FAMILY = "randomized_algorithms"
UBER_COMPANY_ID = 5
SENTINEL = "<!-- LC384_NOTES_V1 -->"

NOTES = """<!-- LC384_NOTES_V1 -->
## 题目定位
LC 384 Shuffle an Array —— **均匀随机洗牌 (Fisher-Yates / Knuth Shuffle)**
的标准模板题。设计一个类，支持 `reset()` 返回原始数组、`shuffle()` 返回一个
**每种排列出现概率严格相等**（$1/n!$）的随机排列。

**关键洞察**：每种排列等概率 $\\Leftrightarrow$ 每个元素出现在每个位置的概率
都是 $1/n$（对称性）。Fisher-Yates 用一行 swap 配合"把已确定位的元素从采样
区间剔除"的递归结构，做到这一点。

## 思路
### Fisher-Yates 倒序版（最常见）
从最后一位往前，每次从 `[0, i]` 里选一个下标 $j$，把 `arr[j]` 和 `arr[i]`
交换。位置 $i$ 一旦写好就**冻结**。

### Fisher-Yates 正序版（user 在讨论里写的版本，更易解释概率）
从第 0 位往后，第 $i$ 步从 `[i, n-1]` 里选一个 $j$，与位置 $i$ 交换。
位置 $i$ 一旦写好就**冻结**。

两个版本完全等价（数学上互为逆映射），区别只在采样区间方向。

## 核心代码
```python
import random

class Solution:
    def __init__(self, nums: list[int]):
        self.original = nums[:]   # 深拷贝, reset 用
        self.arr = nums[:]

    def reset(self) -> list[int]:
        self.arr = self.original[:]
        return self.arr

    def shuffle(self) -> list[int]:
        # Fisher-Yates 正序版: i 从 0 到 n-1, 每步从 [i, n-1] 抽
        n = len(self.arr)
        for i in range(n):
            j = random.randint(i, n - 1)        # 含两端
            self.arr[i], self.arr[j] = self.arr[j], self.arr[i]
        return self.arr
```

### 走查（n = 3, arr = [A, B, C]，一条具体路径）
| 步 i | 采样区间 | 抽到 j | 操作 | 数组 |
| --- | --- | --- | --- | --- |
| 0 | [0, 2] | 2 | swap arr[0], arr[2] | [C, B, A] |
| 1 | [1, 2] | 1 | swap arr[1], arr[1]（no-op）| [C, B, A] |
| 2 | [2, 2] | 2 | swap arr[2], arr[2]（no-op）| [C, B, A] |

每步采样区间长度 = $3, 2, 1$ → 共 $3 \\times 2 \\times 1 = 3! = 6$ 条等可能路径，
每种排列恰好对应一条路径，故概率 $1/6$ 均匀。✓

## 概率正确性证明（**user 第 1 条洞察的展开**）
**目标**：证明任意元素 $x$ 落在任意位置 $k$ 的概率都是 $1/n$。

考虑正序版本，$x$ 落在位置 $k$ 当且仅当：
- 第 0 步没被抽到，
- 第 1 步没被抽到，
- ...
- 第 $k-1$ 步没被抽到，
- 第 $k$ 步被抽到。

每一步的"没被抽到"概率是 (剩余区间长度 - 1) / 剩余区间长度：

$$
P(x \\text{ 落在 } k) = \\underbrace{\\frac{n-1}{n}}_{\\text{step 0 漏}} \\cdot \\underbrace{\\frac{n-2}{n-1}}_{\\text{step 1 漏}} \\cdots \\underbrace{\\frac{n-k}{n-k+1}}_{\\text{step } k-1 \\text{ 漏}} \\cdot \\underbrace{\\frac{1}{n-k}}_{\\text{step } k \\text{ 命中}}
$$

**望远镜式抵消**：每个分子约去下一项的分母，最终只剩 $\\frac{1}{n}$。✓

> **user 在讨论里抓到的连接**：这正是 **reservoir sampling** 的同款套路——
> 第 $i$ 个元素以 $1/i$ 的概率上位，前面已经在位的以 $(i-1)/i$ 的概率留任，
> 乘起来对所有位置都一样。**Fisher-Yates 和 reservoir sampling 是同一个
> 数学结构在不同问题上的体现**：前者是"对每个位置选元素"，后者是"对每个
> 流入元素选是否替换"，但底层都是"递增/递减的概率让最终分布抹平"。

## 替代方案：Sort-based Shuffle（**user 第 2 条洞察的展开**）
> user 问："既然要生成这么多个 random number，为什么我们不直接按照 random num
> 给这些下标重排序算了？"

**答**：完全可行，工程上确实有人用。

```python
def shuffle(self) -> list[int]:
    return [x for _, x in sorted((random.random(), x) for x in self.arr)]
```

**正确性**：连续随机数撞 key 的概率为 0，每种排列出现概率严格 $1/n!$。

### Fisher-Yates vs Sort-based 取舍
| 维度 | Fisher-Yates | Sort-based |
| --- | --- | --- |
| 时间 | $O(n)$ | $O(n \\log n)$ |
| 空间 | $O(1)$（原地） | $O(n)$（存 key + 排序缓冲） |
| 随机数消耗 | $n$ 次小整数 | $n$ 次 64-bit 浮点（防撞） |
| 顺序依赖 | 严格顺序，无法并行 | 排序天然好分片 |
| 工程语境 | 单机内存 / LeetCode | Spark `ORDER BY RANDOM()`, SQL, MapReduce |

**为什么 Fisher-Yates 在面试里被推崇**：单机场景下严格更优，且能考察"采样
区间 `[i, n-1]` 还是 `[0, n-1]`"这个细节坑（见易错点 1）。

**为什么 Sort-based 仍然有用**：
- **分布式 shuffle**：Spark / Hive / Presto 没有 in-place swap 这种语义，
  但有 `ORDER BY RANDOM()`，这就是 sort-based shuffle 的产业级版本。
- **代码极短**：一行写完，工程上图方便时常见。
- **GPU / 向量化**：批量算 random key + 并行排序，远比串行 Fisher-Yates 友好。

> 一句话总结：sort-based 不是"歪门邪道"，是一个真实存在、有自己适用场景的
> 替代算法。LC 384 期待 Fisher-Yates **是因为它在单机内存场景下严格更优**，
> 不是因为 sort-based 错。

## 关键技巧 / 易错点

### [PITFALL] 1. 采样区间是 `[i, n-1]`，不是 `[0, n-1]`
最经典的 Fisher-Yates 错误版本：
```python
for i in range(n):
    j = random.randint(0, n - 1)   # 错: 区间没缩
    arr[i], arr[j] = arr[j], arr[i]
```
**这个版本是有偏的！** 共有 $n^n$ 条采样路径但只有 $n!$ 种排列，
$n^n$ **不被 $n!$ 整除**（除了 $n=1$）→ 必然有些排列概率高、有些低。
$n=3$ 时算一下：$3^3=27$ 条路径，$3!=6$ 种排列，$27/6=4.5$ 不是整数，
理论上不可能均匀。

**正确版**必须是 `randint(i, n-1)`（正序）或 `randint(0, i)`（倒序）。
**采样区间长度必须等于 `n!`** 才能保证均匀。

### 其它易错点
2. **`reset()` 必须返回原数组的拷贝而非别名**：`self.arr = self.original`（赋引用）
   会让下次 `shuffle()` 把 `self.original` 也搅了；必须 `self.original[:]`
   或 `list(self.original)` 或 `copy.copy()`。
3. **`__init__` 里没拷贝 `nums`**：题目交进来的 `nums` 后续可能被外部改动；
   `self.original = nums` 直接持引用就被打穿了。
4. **`random.randint(i, n-1)` 含两端**：Python 的 `randint` 是闭区间；
   如果误写成 `random.randrange(i, n-1)`（左闭右开），最后一位永远抽不到，
   产生偏差。
5. **倒序版起点错**：`for i in range(n - 1, 0, -1): j = randint(0, i)`，
   注意 `i` 从 `n-1` 走到 `1`（不是 `0`），最后一步 `i = 0` 是无操作可
   省略；写成 `range(n - 1, -1, -1)` 也对，多一次空 swap。
6. **以为"洗牌一次后再洗牌就坏了"**：错。Fisher-Yates 的均匀性对当前数组
   状态成立，**多次 shuffle 仍均匀**（每次都是从均匀分布到均匀分布）。

## 复杂度
- `__init__`: $O(n)$ 拷贝。
- `reset`: $O(n)$ 拷贝。
- `shuffle`: $O(n)$ 时间，$O(1)$ 额外空间（原地交换）。
- 调用 $n$ 次随机数生成器；若 RNG 调用本身 $O(1)$ 摊还，总开销 $O(n)$。

## 题目家族（randomized_algorithms / 抽样与洗牌）
- **LC 382** Linked List Random Node：reservoir sampling 模板题，与本题
  共享"望远镜式概率"证明结构。
- **LC 398** Random Pick Index：reservoir sampling 在多答案选 1 的应用。
- **LC 528** Random Pick with Weight：前缀和 + 二分，**离散加权抽样**——
  和本题的均匀抽样互补。
- **LC 470** Implement Rand10() Using Rand7()：拒绝采样 (rejection sampling)
  的入门题。Fisher-Yates 不是拒绝采样，但同属"用基础随机源构造目标分布"的家族。
- **LC 380 / 381** Insert Delete GetRandom O(1)：均匀抽样 + 哈希索引；
  本题的"shuffle 后等概率取一个"等价于 LC 380 的 `getRandom()`。
- **LC 519** Random Flip Matrix：Fisher-Yates 的"懒洗"变体，不预先生成全
  排列只在 query 时增量生成。

## Uber 视角
LC 384 在 Uber 这种**实时分发 + AB 实验**重度依赖随机性的公司是高频考点：
- **司机/订单分配的随机打散**：避免"地理上靠近的司机总是接相同的乘客"
  导致 driver-side 体验偏置——shuffle / 加权抽样是底层原语。
- **AB 实验的 traffic split**：用户 ID 哈希后均匀分桶，本质是"每个用户落
  在每个桶的概率等于桶权重"。
- **分布式 shuffle**：上面 sort-based 那一节直接对应 Spark / Presto 在
  Uber 数据栈里的常见用法 (`ORDER BY rand()` 在 Hive 是规范打散写法)。
- **面试展开方向**：从 LC 384 的"单机均匀洗牌"自然过渡到"如果数组在 10 台
  机器上分片你怎么洗"——答案就是 sort-based shuffle 路径。

**面试 30 秒 pitch**：
> "Fisher-Yates 正序版：第 i 步从 [i, n-1] 里抽一个 j 跟位 i 交换，位 i
> 冻结。每个元素落在每个位置的概率是望远镜积 (n-1)/n × (n-2)/(n-1) × ...
> × 1/(n-k) = 1/n。$O(n)$ 时间 $O(1)$ 空间。同款数学结构出现在 reservoir
> sampling。如果你想分布式做，用 sort-based shuffle: `sorted((rand(), x))`，
> $O(n \\log n)$ 但天然好分片，Spark 里的 `ORDER BY rand()` 就是这个。"
"""


def main() -> None:
    """Rewrite LC 384 notes + insert Uber tag; idempotent."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, fam, pat = row

        notes_changed = not (existing_notes and SENTINEL in existing_notes)
        if notes_changed:
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
            print(
                f"[UPDATED] LC {LC_ID} id={pid} "
                f"notes_len={len(NOTES)} fields={list(fields)}"
            )
        else:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} notes (sentinel present)")

        existing_tag = conn.execute(
            "SELECT id FROM problem_company_tags "
            "WHERE problem_id = ? AND company_id = ?",
            (pid, UBER_COMPANY_ID),
        ).fetchone()
        if existing_tag:
            print(f"[UNCHANGED] Uber tag exists row_id={existing_tag[0]}")
        else:
            cur = conn.execute(
                "INSERT INTO problem_company_tags "
                "(problem_id, company_id, relevance, source) "
                "VALUES (?, ?, 'likely', 'manual')",
                (pid, UBER_COMPANY_ID),
            )
            print(f"[INSERTED] Uber tag row_id={cur.lastrowid}")

        conn.commit()


if __name__ == "__main__":
    main()
