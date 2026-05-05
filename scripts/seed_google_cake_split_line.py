"""Seed Google custom problem: 蛋糕水平分割线 (sweep line + 离散化 + 线段树).

Custom Google interview-prep problem driven by user's Discord drop on 2026-05-05.
Per memory `feedback_pinterest_two_tier_notes`, the canonical home for the
per-problem note is `problems.notes` (rendered by the ProblemDrawer when an
index entry like `db://<id>` is opened); the R2 Coding Index doc 92 just
holds the navigation entry, not the content itself.

Idempotency:
  - Matched by `title` (canonical key for custom problems per CLAUDE.md
    `Idempotent seed pattern per row type`).
  - First clean run: 1 INSERT. Re-run with no content drift: 0 writes.

Invariant 3: this is the sole sanctioned write path for this row.

After running this, re-run `scripts/seed_google_r2_coding_index_20260502.py`
to refresh doc 92 (it now references this problem by title under a new
"Sweep Line / 离散化 / 线段树" section).

Run: python scripts/seed_google_cake_split_line.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "蛋糕水平分割线"
SOURCE_LABEL = "Google R2 Custom Note 2026-05"
COMPANY_TAGS = ["Google"]


# --------------------------------------------------------------------------
# Description (rendered as the problem-statement card in ProblemDrawer)
# --------------------------------------------------------------------------

DESCRIPTION = r"""无限大平面上摆放 $N$ 个轴对齐的正方形蛋糕，每块以左上角 $(x, y)$ 与边长 $\text{side}$ 给出（$y$ 轴朝上，所以左上角是该蛋糕 $y$ 坐标的最大值）。

要求一条水平线 $y = L$，使其上方与下方的蛋糕总面积相等。允许切过蛋糕，输出浮点解，多解任意一个即可。

「面积」语义有两种，本题按两种分别讨论：

- **独立面积**：总面积 $= \sum \text{side}^2$，重叠区域被多次累加。
- **几何并集**：重叠区域只算一次，求的是真正的几何并集面积。

题面里"切过蛋糕"的说法暗示蛋糕是有独立实体的，倾向独立语义；本题解两种都给出，并把几何并集语义中的 $O(n \log n)$ 线段树进阶解法重点讲透。

来源: Google 面经 / 2026-05 prep。
"""


# --------------------------------------------------------------------------
# Notes (full multi-method walkthrough; rendered as the deep-dive)
# --------------------------------------------------------------------------

NOTES = r"""## 蛋糕水平分割线

### 题意

无限大平面上 $N$ 个轴对齐正方形蛋糕，每块由左上角 $(x, y)$ 和边长 $\text{side}$ 给出。求一条水平线 $y = L$，让其上下方蛋糕总面积相等；允许切过蛋糕，多解任一即可。

「面积」的两种语义直接决定算法：

- **独立面积**：每块蛋糕单独算自己的面积，重叠区域被重复累加。
- **几何并集**：重叠区域只算一次。

下面三种方法层层递进：方法 A 是不分语义都能用的暴力二分；方法 B 用扫描线把二分省成一遍线性插值；方法 C 处理几何并集语义，并在朴素 $O(n^2)$ 之上用「离散化 + 线段树」做到 $O(n \log n)$ —— 这部分是本题的进阶重点。

---

### 方法 A：二分 $L$（baseline，独立语义最容易讲）

#### 思路

定义 $A(L) = $ 水平线 $y = L$ 以上的蛋糕面积。$L$ 越往下，$A(L)$ 越大，$A$ 关于 $L$ 单调，可以二分。

二分区间：从最顶部蛋糕的上边界到最底部蛋糕的下边界。每次取 $L$ 的中点，逐块判断每个蛋糕：

- 完全在线上：贡献 $\text{side}^2$
- 完全在线下：贡献 $0$
- 被切：贡献 $\text{side} \times (\text{top}_y - L)$

把所有贡献加起来得到 $A(L)$，与 $\text{target} = \frac{1}{2}\sum \text{side}^2$ 比较，调整二分边界。

#### 代码

```python
def find_balancing_line_binary(cakes, eps=1e-9):
    '''独立面积语义; 二分到精度 eps.'''
    target = sum(c.side ** 2 for c in cakes) / 2

    lo = min(c.top_y - c.side for c in cakes)
    hi = max(c.top_y for c in cakes)

    def area_above(L):
        s = 0.0
        for c in cakes:
            top, bot = c.top_y, c.top_y - c.side
            if bot >= L:                  # 完全在线上
                s += c.side ** 2
            elif top > L:                 # 被切
                s += c.side * (top - L)
            # else 完全在线下，跳过
        return s

    while hi - lo > eps:
        mid = (lo + hi) / 2
        if area_above(mid) > target:
            lo = mid                      # 上方面积太多 -> 线再往下
        else:
            hi = mid
    return (lo + hi) / 2
```

#### 复杂度

时间 $O(n \log \frac{K}{\varepsilon})$，$K$ 是 $y$ 范围；空间 $O(1)$。

---

### 方法 B：扫描线 + 线性插值（独立语义，一遍扫描）

#### 关键观察

把每个蛋糕的上、下边界 $y$ 坐标作为「事件点」排序。在任意两个相邻事件点之间，被扫描线穿过的蛋糕集合恒定，所以 $A(L)$ 是 $L$ 的**分段线性函数**。每段斜率 $= |dA/dL| = $ 当前段「切片宽度」：

| 语义 | 段内切片宽度 |
|---|---|
| 独立面积 | 所有穿过扫描线的蛋糕**边长之和** |
| 几何并集 | 所有穿过扫描线的蛋糕在 $x$ 轴**投影的并集长度** |

既然每段都是线性的，就不必二分了。一遍扫描累加，跨过 $\text{target}$ 时直接在段内线性反解 $L$。

#### 代码（独立语义版）

维护一个标量 `width_through_line` —— 当前被扫描线穿过的所有蛋糕的边长之和 —— 它就是 $A(L)$ 在该段的斜率。

```python
from dataclasses import dataclass

@dataclass
class Cake:
    '''y 轴朝上; (x, top_y) 是蛋糕左上角.'''
    x: float
    top_y: float
    side: float

    @property
    def bottom_y(self) -> float:
        return self.top_y - self.side


def find_balancing_line_independent(cakes: list[Cake]) -> float:
    '''独立面积语义 (重叠重复累加), 返回水平线 y = L.'''
    target_area_above = sum(c.side ** 2 for c in cakes) / 2

    # 事件: (y, 边长增量); 顶 +side / 底 -side
    events: list[tuple[float, float]] = []
    for c in cakes:
        events.append((c.top_y,    +c.side))
        events.append((c.bottom_y, -c.side))
    events.sort(key=lambda ev: -ev[0])              # 自上而下

    width_through_line = 0.0
    area_above         = 0.0
    scan_y             = events[0][0]

    i = 0
    while i < len(events):
        # 先把当前 y 层的所有事件一次性应用完
        current_y = events[i][0]
        while i < len(events) and events[i][0] == current_y:
            width_through_line += events[i][1]
            i += 1
        scan_y = current_y

        if i == len(events):
            break

        next_y         = events[i][0]
        segment_height = scan_y - next_y

        if width_through_line > 0:
            area_after = area_above + width_through_line * segment_height
            if area_after >= target_area_above:
                # 段内线性反解
                remaining = target_area_above - area_above
                return scan_y - remaining / width_through_line

        area_above += width_through_line * segment_height

    return scan_y    # 浮点兜底
```

#### 复杂度

时间 $O(n \log n)$，瓶颈是事件排序；空间 $O(n)$。

---

### 方法 C：扫描线 + 几何并集（朴素 $O(n^2)$）

几何并集语义下，「active 集合」不再是一个标量，而是当前被扫描线穿过的蛋糕集合。段内斜率 $= $ 这些蛋糕在 $x$ 轴上投影区间的**并集长度**。

#### 朴素实现：每段重排所有 active 蛋糕求并集

```python
def find_balancing_line_union(cakes: list[Cake]) -> float:
    def x_projections_crossing(y: float) -> list[tuple[float, float]]:
        return [(c.x, c.x + c.side) for c in cakes if c.bottom_y < y < c.top_y]

    def union_length(intervals: list[tuple[float, float]]) -> float:
        if not intervals:
            return 0.0
        intervals = sorted(intervals)
        total = 0.0
        L, R = intervals[0]
        for l, r in intervals[1:]:
            if l > R:
                total += R - L
                L, R = l, r
            else:
                R = max(R, r)
        total += R - L
        return total

    event_ys = sorted(
        {c.top_y for c in cakes} | {c.bottom_y for c in cakes},
        reverse=True,
    )

    # 第一遍：累加得到总并集面积
    total_area = 0.0
    for upper, lower in zip(event_ys, event_ys[1:]):
        sample_y    = (upper + lower) / 2
        slice_width = union_length(x_projections_crossing(sample_y))
        total_area += slice_width * (upper - lower)

    target = total_area / 2

    # 第二遍：找跨过 target 的那一段并反解
    area_above = 0.0
    for upper, lower in zip(event_ys, event_ys[1:]):
        sample_y    = (upper + lower) / 2
        slice_width = union_length(x_projections_crossing(sample_y))
        seg_height  = upper - lower

        if slice_width > 0:
            area_after = area_above + slice_width * seg_height
            if area_after >= target:
                remaining = target - area_above
                return upper - remaining / slice_width

        area_above += slice_width * seg_height

    return event_ys[-1]
```

复杂度 $O(n^2)$：每段重排 active 求并集。$n = 10^5$ 量级会爆。

要做到 $O(n \log n)$，必须**增量地维护**切片宽度 —— 这正是离散化 + 线段树要解决的子问题，下一节展开。

---

### 方法 D：扫描线 + 离散化 + 线段树（$O(n \log n)$ 进阶做法）

> **本题的核心进阶部分**。把方法 C 中朴素的 `union_length` 换成线段树查询；其它骨架完全不变。

#### D.1 抽象出来的子问题

我们需要一个数据结构，支持：

| 操作 | 含义 |
|---|---|
| `insert(l, r)` | 加入一段一维闭区间 $[l, r]$ |
| `remove(l, r)` | 移走一段（保证之前 `insert` 过完全相同的 $(l, r)$） |
| `total_length()` | 返回当前集合里所有区间的**并集**总长度 |

蛋糕的 $x$ 投影 $[x, x+\text{side}]$ 就是这里的区间；蛋糕的 `top_y` 触发 `insert`、`bottom_y` 触发 `remove`。

注意「成对调用」这个不变量 —— 它在 D.6 里会成为这棵线段树**不需要 lazy pushdown** 的根本原因。

#### D.2 为什么需要离散化

线段树天然处理整数下标。但 $x$ 坐标可以是任意浮点数，没法把每个浮点 $x$ 都做成一个叶子。

**离散化**：把所有出现过的 $x$ 端点（每个矩形贡献 $x$ 和 $x + \text{side}$ 两个）排序去重：

```
x_coords = [x_0, x_1, x_2, ..., x_{N-1}]   # 严格递增
```

切出 $N - 1$ 个**基本段**（"槽"）：第 $i$ 个基本段是 $[x_{coords}[i], x_{coords}[i+1]]$。

**关键观察**：任何一个矩形的 $x$ 投影 $[x, x+\text{side}]$ 必定**恰好**等于若干相邻基本段拼起来 —— 因为它的左右端点本身就在 `x_coords` 里。所以我们只需要在「基本段索引」（整数 $0$ 到 $N-2$）这个维度上建线段树。

把矩形 $[x_1, x_2]$ 的覆盖记到线段树上：

```
left_idx  = x_coords 中 x1 的位置
right_idx = x_coords 中 x2 的位置 - 1
update(left_idx, right_idx, +1)
```

`right_idx` 的 `-1` 是离散化最容易写错的地方：基本段 $i$ 对应 $[x_{coords}[i], x_{coords}[i+1]]$，所以覆盖到 $x_2 = x_{coords}[k]$ 时，最右边那个基本段是 $k - 1$。

##### 一个具体例子

`x_coords = [0, 2, 3, 4, 5, 6]` 切出 5 个基本段：

| 基本段索引 | 实际 $x$ 区间 | 长度 |
|---|---|---|
| 0 | $[0, 2]$ | 2 |
| 1 | $[2, 3]$ | 1 |
| 2 | $[3, 4]$ | 1 |
| 3 | $[4, 5]$ | 1 |
| 4 | $[5, 6]$ | 1 |

矩形 $[0, 4]$ → 覆盖基本段 $[0, 2]$（长度 $2+1+1=4$ ✓）
矩形 $[2, 6]$ → 覆盖基本段 $[1, 4]$（长度 $1+1+1+1=4$ ✓）
矩形 $[3, 5]$ → 覆盖基本段 $[2, 3]$（长度 $1+1=2$ ✓）

#### D.3 线段树的存储约定

线段树**整棵树用一个普通数组存**（不用指针）。节点编号从 1 开始，三条铁则：

```
根节点编号           = 1
编号 v 的节点，左孩子 = 2 * v
编号 v 的节点，右孩子 = 2 * v + 1
```

代码里到处出现的 `2 * node_index` 和 `2 * node_index + 1` 不是什么神秘公式，就是「找左右孩子」的固定算术。

每个节点**负责一段连续的基本段索引**。续用 5 段例子，整棵树长这样：

```
                节点1  负责 [0, 4]   <- 根
               /                  \
          节点2 [0,2]           节点3 [3,4]
          /        \             /        \
     节点4[0,1] 节点5[2,2]  节点6[3,3] 节点7[4,4]
      /     \
节点8[0,0] 节点9[1,1]
```

要点：

1. 每个节点的「区间」`[node_left, node_right]` 指**基本段索引**范围，不是 $x$ 坐标本身。
2. 节点 $v$ 对应的实际 $x$ 区间是 $[x_{coords}[node\_left], x_{coords}[node\_right + 1]]$。`+1` 是因为基本段 $i$ 从 $x_{coords}[i]$ 延伸到 $x_{coords}[i+1]$。
3. 节点编号不连续：上图节点 5 是叶子没孩子，但 `2v / 2v+1` 编号下节点 10、11 在数组里仍是空槽。
4. **数组开 $4n$ 大小** —— $n$ 叶子的二叉树，最大节点编号严格小于 $4n$。

#### D.4 节点维护什么：`cover` 与 `length`

每个节点存两个值：

| 字段 | 含义 |
|---|---|
| `cover[v]` | 节点 $v$ 负责的整段被「完整覆盖」的次数。只有对该节点**完整命中**的 update 才会让 `cover[v] += delta`。 |
| `length[v]` | 节点 $v$ 负责的实际 $x$ 区间内被覆盖至少一次的总长度。 |

**最终我们只读 `length[1]`**（根的 length），它就是当前并集总长度。

`cover` 可以理解为停留在节点上的「懒标记」 —— 但和普通线段树不同，这棵树的 `cover` **不下传**给孩子。原因放在 D.6 解释。

#### D.5 完整实现

```python
class CoverageSegTree:
    '''
    维护一组一维闭区间, 支持成对的 +1 / -1 更新, 查询并集总长度.
    所有区间端点必须事先离散化好, 作为 x_coords 传入.

    使用模式:
        tree = CoverageSegTree(x_coords)
        tree.update(left_idx, right_idx, +1)   # 加入一个区间
        ...
        tree.update(left_idx, right_idx, -1)   # 严格配对地移走
        width = tree.total_length()            # 当前并集总长度
    '''

    def __init__(self, x_coords):
        self.x_coords = x_coords
        self.num_segments = len(x_coords) - 1
        # 4 * n 是堆式存储下安全的数组大小; max(.., 1) 避免 n=0 的退化
        array_size = 4 * max(self.num_segments, 1)
        self.cover  = [0]   * array_size
        self.length = [0.0] * array_size

    def update(self, query_left, query_right, delta):
        '''对基本段索引区间 [query_left, query_right] 整段 += delta.'''
        self._update(
            node_index=1,
            node_left=0,
            node_right=self.num_segments - 1,
            query_left=query_left,
            query_right=query_right,
            delta=delta,
        )

    def _update(self, node_index, node_left, node_right,
                query_left, query_right, delta):
        # 情况 A: 完全不相交 -> 跟我无关，直接 return
        if query_right < node_left or node_right < query_left:
            return

        # 情况 B: 查询完全包住当前节点 -> 在这层截停, cover += delta, 不下钻
        if query_left <= node_left and node_right <= query_right:
            self.cover[node_index] += delta
            # 注意: 这里不 return! pushup 还要更新 length

        # 情况 C: 部分相交 -> 分裂到两个孩子
        else:
            node_mid = (node_left + node_right) // 2
            self._update(
                2 * node_index,     node_left,    node_mid,
                query_left, query_right, delta,
            )
            self._update(
                2 * node_index + 1, node_mid + 1, node_right,
                query_left, query_right, delta,
            )

        # pushup: 重算 length[node_index]
        if self.cover[node_index] > 0:
            # 自己整段被钉死覆盖 -> 不管孩子, 直接取整段长度
            self.length[node_index] = (
                self.x_coords[node_right + 1] - self.x_coords[node_left]
            )
        elif node_left == node_right:
            # 叶子且自己 cover==0 -> 长度为 0
            self.length[node_index] = 0.0
        else:
            # 内部节点且自己 cover==0 -> 决定权交给两个孩子
            self.length[node_index] = (
                self.length[2 * node_index] + self.length[2 * node_index + 1]
            )

    def total_length(self):
        '''根节点的 length 就是当前所有区间的并集总长度.'''
        return self.length[1]
```

##### Pushup 三分支按优先级

```python
if self.cover[node_index] > 0:
    self.length[node_index] = self.x_coords[node_right + 1] - self.x_coords[node_left]
elif node_left == node_right:
    self.length[node_index] = 0.0
else:
    self.length[node_index] = self.length[2*v] + self.length[2*v + 1]
```

1. **`cover > 0`**：本节点整段被某个 update **直接钉死**为「完全覆盖」，那不管孩子怎样，并集长度就是整段长度。这一支**优先于子节点** —— 即使孩子的 length 是 0，只要 `cover > 0` 就以整段为准。
2. **`cover == 0` 且是叶子**：基本段索引 $[i, i]$ 单独是个叶子，没孩子可问，自己 `cover` 又是 0，那就是 0 长度。
3. **`cover == 0` 且不是叶子**：决定权交给两个孩子，左右 length 加起来。

##### 用例子追踪两次 update

继续用 5 段那棵树。要插入矩形 $[0, 4]$（基本段索引 $[0, 2]$），调用 `update(0, 2, +1)`：

```
_update(v=1, [0,4], query=[0,2], +1)
  情况 C(部分相交), node_mid = 2
  ├─ _update(v=2, [0,2], query=[0,2], +1)
  │    情况 B(完全包含) -> cover[2] += 1 (= 1)
  │    pushup: cover[2]>0 -> length[2] = x_coords[3] - x_coords[0] = 4 - 0 = 4
  │
  └─ _update(v=3, [3,4], query=[0,2], +1)
       情况 A(不相交, query_right=2 < node_left=3) -> return

  pushup v=1: cover[1]==0, 非叶子
    -> length[1] = length[2] + length[3] = 4 + 0 = 4 ✓
```

`total_length()` 返回 `length[1] = 4`，正好是矩形 $[0, 4]$ 的宽度。

接着插入 $[2, 6]$（基本段索引 $[1, 4]$），调用 `update(1, 4, +1)`：

```
_update(v=1, [0,4], query=[1,4], +1)
  情况 C, node_mid = 2
  ├─ _update(v=2, [0,2], query=[1,4], +1)
  │    情况 C ([0,2] 与 [1,4] 重叠在 [1,2])
  │    node_mid = 1
  │    ├─ _update(v=4, [0,1], query=[1,4], +1)
  │    │    情况 C, node_mid = 0
  │    │    ├─ _update(v=8, [0,0], query=[1,4], +1) -> A, return
  │    │    └─ _update(v=9, [1,1], query=[1,4], +1)
  │    │         情况 B -> cover[9] += 1, length[9] = x_coords[2]-x_coords[1] = 1
  │    │    pushup v=4: cover[4]==0, 非叶子 -> length[4] = 0 + 1 = 1
  │    └─ _update(v=5, [2,2], query=[1,4], +1)
  │         情况 B -> cover[5] += 1, length[5] = x_coords[3]-x_coords[2] = 1
  │    pushup v=2: cover[2]==1 (前一次插入留下的!)
  │           -> length[2] = x_coords[3] - x_coords[0] = 4
  │           (子节点 length 加起来是 1+1=2, 但 cover[2]>0 优先取整段长度 4)
  │
  └─ _update(v=3, [3,4], query=[1,4], +1)
       情况 B -> cover[3] += 1, length[3] = x_coords[5]-x_coords[3] = 2

  pushup v=1: cover[1]==0 -> length[1] = length[2] + length[3] = 4 + 2 = 6 ✓
```

总并集 $= 6$（$[0, 6]$ 整段都被两个矩形并起来盖住），正确。

特别注意 pushup v=2 那一步 —— 这正是「`cover > 0` 时**忽略孩子**直接用整段长度」起作用的地方。如果错误地总是用 `length[左孩子] + length[右孩子]`，这里就会得到 2 而不是 4，最终答案会错。

#### D.6 为什么不需要 pushdown？

普通线段树（区间加 + 区间求和）的 lazy 标记是要 pushdown 的：因为查询点可能落在子树里，子树需要「知道」祖先上还压着多少懒标记。

这棵树**反直觉地不需要 pushdown**，原因有两层：

##### 第一层（不变量层面）

所有 update 都是**严格成对**出现的 —— 每次 $+1(l_i, h_i)$ 在未来必然伴随一次**对完全相同 $(l_i, h_i)$** 的 $-1$。所以 $+1$ 在哪个节点上「停下」（即被作为 `cover[v] += 1` 累上），未来的 $-1$ 也一定在那个**同一个节点**上停下并抵消。`cover` 标记从来不需要下放给孩子。

##### 第二层（语义层面）

我们**只读 `length[1]`**，不读子树的 `length`。`length[v]`（$v$ 不是根时）的语义其实是「**假装 $v$ 的祖先都没有 cover 时，$v$ 子树范围内的并集长度**」。这是个「局部」的、不完全对外正确的量；但它对根来说是完全正确的，因为根没有祖先。

把这两点合起来：因为不需要「下钻查询」，所以不需要把祖先的 `cover` 同步给子树；又因为 $\pm$ 成对，`cover` 数组本身就是一致的（不会出现「该消的消不掉」的情况）。

##### 副作用：不能 query 子区间

如果你想查询「某段 $x$ 范围内的并集长度」 —— 做不到，因为子节点的 `length` 不是局部正确的（没考虑祖先 `cover`）。如果需要这种查询，要么做 pushdown，要么递归查询时手动累加路径上所有祖先的 `cover`。但本题只需要根的 `length`，所以没问题。

#### D.7 在本题中接到主流程

```python
def find_balancing_line_union_segtree(cakes: list[Cake]) -> float:
    '''几何并集语义 + 线段树, O(n log n).'''
    # 1. 离散化 x
    x_coords = sorted(
        {c.x for c in cakes} | {c.x + c.side for c in cakes}
    )
    x_to_idx = {x: i for i, x in enumerate(x_coords)}

    # 2. y 事件: (y, delta, left_idx, right_idx)
    #    top_y -> +1 (蛋糕进入扫描区)
    #    bottom_y -> -1 (蛋糕离开扫描区)
    events = []
    for c in cakes:
        left_idx  = x_to_idx[c.x]
        right_idx = x_to_idx[c.x + c.side] - 1   # 注意 -1
        events.append((c.top_y,    +1, left_idx, right_idx))
        events.append((c.bottom_y, -1, left_idx, right_idx))
    events.sort(key=lambda e: -e[0])

    # 3 & 4. 双趟扫描
    def sweep(target=None):
        '''target=None 返回总面积; 否则在跨过 target 的那段反解 L.'''
        tree = CoverageSegTree(x_coords)
        area_above = 0.0
        prev_y = events[0][0]
        i, n = 0, len(events)

        while i < n:
            cur_y = events[i][0]

            # 段 [cur_y, prev_y] 的贡献
            if cur_y < prev_y:
                slice_width = tree.total_length()
                seg_height  = prev_y - cur_y

                if (target is not None
                        and slice_width > 0
                        and area_above + slice_width * seg_height >= target):
                    remaining = target - area_above
                    return prev_y - remaining / slice_width

                area_above += slice_width * seg_height
                prev_y = cur_y

            # 应用本层所有同 y 的事件 (一次性)
            while i < n and events[i][0] == cur_y:
                _, delta, left_idx, right_idx = events[i]
                tree.update(left_idx, right_idx, delta)
                i += 1

        return area_above   # target=None 时这就是总面积

    total_area = sweep(target=None)
    return sweep(target=total_area / 2)
```

##### 主流程几个要点

1. **事件方向**：自上而下扫描，遇到蛋糕的 `top_y` 是它进入扫描区（$+1$），`bottom_y` 是离开（$-1$）。
2. **同一 $y$ 上的多个事件要一次性应用完**，否则会在「半应用状态」下错读 `total_length()`。代码里那个内层 while 就是这件事。
3. **段贡献先算再应用事件**：先用旧的 `slice_width × seg_height` 累加上方面积，再应用 `cur_y` 处的事件。这保证「段 $[cur\_y, prev\_y]$ 内的 active 集合」是正确的（即 `cur_y` 处事件还没生效时的集合）。
4. **反解公式**：在跨过 target 的那段里，$\text{area\_above} + \text{slice\_width} \times (prev\_y - L) = \text{target}$，解得：

   $$L = prev\_y - \frac{\text{target} - \text{area\_above}}{\text{slice\_width}}$$

5. **双趟扫描**：第一趟 `target=None` 累加得到 `total_area`；第二趟 `target = total_area / 2` 触发反解。如果想省一倍常数，可以把第一趟的 `(prev_y, cur_y, slice_width)` 元组缓存下来，第二趟数组上线性查找即可，完全不动线段树。

---

### 边界与陷阱

1. **同 $y$ 多事件**：多块蛋糕的顶/底落在同一 $y$ 时，必须先把同层所有事件应用完再去看下一段，否则 active 状态在层间不一致。方法 B 里的内层 while、方法 D 主流程里的内层 while 都是为这个准备的。
2. **零斜率段**：某一段内没有任何蛋糕穿过（`width_through_line == 0` 或 `slice_width == 0`）时不能反解，跳过累加即可。常见于「上下两簇蛋糕中间隔了一段空白」。
3. **浮点误差兜底**：理论上 target 必然会被某段跨过，但浮点累加可能导致最后一段的 `area_after_segment` 略小于 target。函数末尾的 `return scan_y` / `return event_ys[-1]` 就是为这种边角兜底。
4. **语义差异验证**：造一组完全重叠的蛋糕（比如两块完全相同）喂进去，方法 B 和方法 C/D 答案应当不同 —— 方法 B 的 target 是单块面积，方法 C/D 的 target 是双块的几何并集。这是确认题目语义最简单的办法。
5. **浮点 $x$ 当 dict key**：`x_to_idx = {x: i for ...}` 在 $x$ 是 float 时虽然能跑，但存在两个理论上「应该相等」的 float 因计算路径不同而不相等的风险。如果输入保证从原始端点直接传入（不经过任何算术），是安全的；否则要么先 `round(x, 9)` 一下，要么改成 `sort + bisect_left`。
6. **递归深度**：Python 默认 `sys.setrecursionlimit(1000)`。基本段数 $\le 2n$，递归深度 $\approx \log_2(2n) + $ 常数，$n = 10^5$ 都没事。$n = 10^7$ 时建议改写成迭代 / zkw 线段树。
7. **$m = 0$ 的退化**：如果 cakes 列表为空，`x_coords` 也空，构造时 `4 * max(0, 1) = 4`，不会崩 —— 但你应该在主流程里直接 return 之前的兜底值。
8. **pushup 必须对所有被访问到的节点执行**：`_update` 里 pushup 写在递归之外、return 之前，正好覆盖了「整段命中（情况 B）」和「分裂下递归（情况 C）」两种情况。即使在情况 B（只改了 `cover`、没递归），`length` 也得根据新的 `cover` 重算 —— 别把 pushup 漏在 else 分支里。

---

### 复杂度对比

| 方法 | 语义 | 时间 | 空间 |
|---|---|---|---|
| A. 二分 $L$ | 独立 / 并集（替换 `area_above` 实现） | $O(n \log \frac{K}{\varepsilon})$ | $O(1)$ |
| B. 扫描线 + 线性插值 | 独立面积 | $O(n \log n)$ | $O(n)$ |
| C. 扫描线朴素 | 几何并集 | $O(n^2)$ | $O(n)$ |
| **D. 扫描线 + 离散化 + 线段树** | **几何并集** | **$O(n \log n)$** | **$O(n)$** |

对比朴素的 $O(n^2)$，方法 D 在 $n = 10^5$ 量级时实测会有 1000× 以上的差距 —— 这是 Google 级面试题与「会写朴素」的典型分水岭。

---

### 附录：数组大小为什么是 $4n$

$n$ 叶子的二叉树，最大节点编号 $< 4n$。严格推导：

- 树高 $h = \lceil \log_2 n \rceil$
- 完美二叉树到第 $h$ 层一共有 $2^{h+1} - 1$ 个节点
- 而 $2^{h+1} \le 2 \times 2^{\lceil \log_2 n \rceil} \le 2 \times 2n = 4n$

所以开 $4n$ 是约定俗成的「一定够」的安全值，不需要每次重新算。
"""


# --------------------------------------------------------------------------
# Per-row spec
# --------------------------------------------------------------------------

PROBLEM_SPEC: dict = {
    "title": TITLE,
    "leetcode_id": None,
    "url": None,
    "difficulty": "hard",
    "tags": [
        "geometry",
        "sweep-line",
        "segment-tree",
        "discretization",
        "binary-search",
    ],
    "pattern": "sweep-line + segment-tree",
    "family": "sweep-line",
    "category": None,
    "source": SOURCE_LABEL,
    "company_tags": COMPANY_TAGS,
    "is_completed": 1,
    "description": DESCRIPTION,
    "notes": NOTES,
}


# --------------------------------------------------------------------------
# Upsert logic (matches seed_google_r2_three_problems_20260503.py)
# --------------------------------------------------------------------------


def _select_existing(
    conn: sqlite3.Connection, title: str
) -> tuple[int, dict] | None:
    """Return (id, current_row) for the row matching title, else None."""
    row = conn.execute(
        "SELECT id, leetcode_id, url, difficulty, tags, pattern, family, "
        "       category, source, company_tags, is_completed, "
        "       description, notes "
        "FROM problems WHERE title = ?",
        (title,),
    ).fetchone()
    if row is None:
        return None
    keys = [
        "id", "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
    ]
    return int(row[0]), dict(zip(keys, row, strict=True))


def _normalize(spec: dict) -> dict:
    """Normalize spec into the comparable storage form (lists -> JSON strings)."""
    out = dict(spec)
    out["tags"] = json.dumps(spec["tags"], ensure_ascii=False)
    out["company_tags"] = json.dumps(spec["company_tags"], ensure_ascii=False)
    return out


def upsert_problem(conn: sqlite3.Connection, spec: dict) -> tuple[int, str]:
    """INSERT-or-UPDATE the problem row by title. Return (id, action)."""
    norm = _normalize(spec)
    existing = _select_existing(conn, spec["title"])

    if existing is None:
        cur = conn.execute(
            "INSERT INTO problems "
            "(leetcode_id, title, url, difficulty, tags, pattern, family, "
            " category, source, company_tags, is_completed, "
            " description, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "        CURRENT_TIMESTAMP)",
            (
                norm["leetcode_id"], spec["title"], norm["url"],
                norm["difficulty"], norm["tags"], norm["pattern"],
                norm["family"], norm["category"], norm["source"],
                norm["company_tags"], norm["is_completed"],
                norm["description"], norm["notes"],
            ),
        )
        return int(cur.lastrowid), "INSERTED"

    pid, current = existing
    fields_to_check = [
        "leetcode_id", "url", "difficulty", "tags", "pattern", "family",
        "category", "source", "company_tags", "is_completed",
        "description", "notes",
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
    """Insert-or-update the cake-split-line problem. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(f".db.bak.{ts}_pre_google_cake_split")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")

    with sqlite3.connect(str(DB_PATH)) as conn:
        pid, action = upsert_problem(conn, PROBLEM_SPEC)
        print(f"[{action}] problems.id={pid} title={PROBLEM_SPEC['title']!r}")
        conn.commit()

    print(
        "[OK] done -- next: re-run "
        "scripts/seed_google_r2_coding_index_20260502.py "
        "to refresh doc 92 index (now references this problem under the "
        "new 'Sweep Line / 离散化 / 线段树' section)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
