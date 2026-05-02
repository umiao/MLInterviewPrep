"""Seed: T-P0-690 [MLI-D3] -- Geometric Median (Weber problem) ml_coding.

Adds a new ``problems`` row that mirrors the section structure of
problems.id=1064 (K-Means), id=1102 (Linear Regression), id=1106 (KNN), and
id=1107 (Logistic Regression):

- title='Geometric Median (Weber 问题, L2 距离和最小)'
- category='ml_coding', difficulty='medium'
- source='ml-coding-handwritten-2026-05-02'
- notes contain: opening inclusion-criterion rationale / 题目描述 (with
  explicit L1 vs L2 contrast pointing to db://262 Best Meeting Point) /
  核心代码 (Weiszfeld iteration in numpy with Vardi-Zhang 1999 degeneracy
  correction) / 关键要点 / 面试追问 (mini-batch SGD scaling, 1D = median,
  k=1 K-Means relationship, robustness vs centroid) / 复杂度.

Plus an UPSERT of problems.id=262 (Best Meeting Point) appending a
single-line cross-link 'L2 版本见 [Geometric Median](db://<new_id>)' under
its own sentinel so the second run is a 0-write no-op.

Style anchors (per task spec):
1. T-P0-283 / T-P0-688 (Linear Regression handwritten numpy) -- minimal-
   runnable numpy.
2. problems.id=1064 K-Means -- canonical SECTION baseline.
3. problems.id=1107 Logistic Regression seed (T-P0-689) -- direct UPSERT
   template (canonical key = title + source).

Technical content (per task spec, precise):
- Weiszfeld iteration:
      x^{(t+1)} = (sum_i x_i / d_i^{(t)}) / (sum_i 1 / d_i^{(t)})
  where d_i^{(t)} = ||x^{(t)} - x_i||_2.
- Degeneracy fix per Vardi & Zhang 1999 ('A modified Weiszfeld algorithm
  for the Fermat-Weber location problem', Mathematical Programming 90(3),
  pp. 559-566). When the iterate lands on a sample point a_j (so d_j = 0),
  the standard update has a 1/0 denominator. The fix splits the sum: let
      T(x) = (sum_{i != j} a_i / d_i) / (sum_{i != j} 1 / d_i)
      R(x) = || sum_{i != j} (x - a_i) / d_i ||_2
  and let eta_j be the number of samples equal to a_j. Then:
      - if R(x) <= eta_j: a_j IS the geometric median (theorem 2.1).
      - else: x_{t+1} = max(0, 1 - eta_j / R) * T(x)
                          + min(1, eta_j / R) * a_j.
- 1D case degenerates to per-axis median (the L1 minimizer); contrast with
  L1 in 2D (db://262 Best Meeting Point) which also uses per-axis median.
  L2 in 2D does NOT decouple per-axis -- this is the key pedagogical point.
- Follow-ups: large-N -> mini-batch SGD on the convex objective;
  k=1 K-Means relationship (k=1 + L2-squared = mean, k=1 + L2 = geometric
  median); outlier robustness (geometric median has 50% breakdown point
  vs centroid's 0%).

Idempotency:
- Sentinel <!-- GEOMETRIC_MEDIAN_20260502 --> at the top of new notes body.
- Sentinel <!-- GEOMETRIC_MEDIAN_CROSSLINK_20260502 --> on the appended
  cross-link block in problems.id=262.
- Canonical key for new row UPSERT: (title, source).
- Canonical key for 262 cross-link UPSERT: presence of the cross-link
  sentinel inside problems.id=262 notes.
- Second run with no upstream change = 0 writes (verified manually).
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Geometric Median (Weber 问题, L2 距离和最小)"
SOURCE = "ml-coding-handwritten-2026-05-02"
DIFFICULTY = "medium"
PATTERN = "ML Implementation"
CATEGORY = "ml_coding"
TAGS = '["ml-fundamentals", "geometric-median", "weiszfeld", "robust-statistics", "implementation"]'
COMPANY_TAGS = '["Meta", "Uber", "DoorDash", "Pinterest"]'
PRIORITY = 1

SENTINEL = "<!-- GEOMETRIC_MEDIAN_20260502 -->"
CROSSLINK_SENTINEL = "<!-- GEOMETRIC_MEDIAN_CROSSLINK_20260502 -->"
BEST_MEETING_POINT_ID = 262

DESCRIPTION = (
    "**Geometric Median (Weber 问题)**: 给定 N 个二维点 "
    "$\\{x_1, \\dots, x_N\\}$, 找点 $x^*$ 使 $\\sum_i \\|x^* - x_i\\|_2$ "
    "最小 (L2 距离和). 这是 Fermat-Weber location problem 的经典形式, "
    "也是 L1 距离 (Manhattan, db://262 Best Meeting Point) 在 L2 度量下的"
    "对应版本. 关键区别: L1 距离按维度可分解 -> 每轴取中位数即可; "
    "L2 距离**不可分解**, 没有闭式解, 必须迭代求解.\n\n"
    "经典算法: **Weiszfeld 迭代** (1937) -- 把目标函数的一阶最优条件 "
    "$\\nabla f(x) = \\sum_i (x - x_i)/\\|x - x_i\\| = 0$ 改写成不动点形式 "
    "$x = (\\sum_i x_i / d_i) / (\\sum_i 1 / d_i)$. 退化情形 (迭代点恰好"
    "落在样本点上, 分母为零) 由 Vardi & Zhang 1999 给出标准修正 "
    "(Mathematical Programming 90(3), pp. 559-566).\n\n"
    "归类理由: 几何中位数严格属于 robust statistics / numerical "
    "optimization, 但 ml_coding 收录的标准是更宽的: 我们包含 (a) ML 算法"
    "实现 (KMeans/KNN/LR/LogReg) 或 (b) 与 ML/统计有直接联系的数值优化"
    "问题. 几何中位数符合 (b): Weiszfeld 是凸 L2 距离和目标的 IRLS / "
    "梯度下降变体, M-estimator / 鲁棒均值在 robust regression 与 robust "
    "clustering 初始化里直接用到; k=1 K-Means 用 L2^2 cost 给出 centroid, "
    "本题给的是 k=1 + L2 (非平方) 时的多维 'median' -- 一个干净的桥梁."
)

NOTES = SENTINEL + r"""

## Geometric Median (Weber 问题, L2 距离和最小)

### 为什么这题归在 ml_coding (Inclusion Criterion)

Reviewer 曾指出: "geometric median 严格讲属于 robust statistics /
numerical optimization, 不是 ML coding". 这条意见对**单一定义下的 ML
coding** 是对的, 但本仓 ml_coding 收录的标准更宽 -- 满足以下任一即收:

- **(a)** ML 算法的从零实现 (KMeans / KNN / Linear Regression / Logistic
  Regression / Softmax 等).
- **(b)** 与 ML / 统计有直接联系的数值优化问题. 几何中位数属于 (b):
  - **Weiszfeld 算法本质是 IRLS** (Iteratively Reweighted Least Squares),
    与 Logistic Regression 的 Newton 求解器同族; 也是凸目标 $\sum \|x -
    x_i\|$ 上的一种梯度下降变体, 与 T-283/T-284 的 GD 训练循环同框架.
  - **几何中位数 = M-estimator / robust mean**: robust regression
    (Huber / Tukey) 与 robust clustering 初始化都直接用它代替均值, 因为
    它对离群点不敏感 (50% breakdown point, 见关键要点 5).
  - **k=1 K-Means 的 L2 多维'中位数'**: K-Means 用 L2^2 cost, 最优解是
    centroid (均值); 把 cost 换成 L2 (不平方), 最优解就是几何中位数 --
    一个干净的桥梁, 把"为什么 K-Means 不抗离群点"和"几何中位数"串到一起.
  - **Lock Combination 这类纯图搜索题**则同时不满足 (a) 和 (b),
    所以从 ml_coding 移除是符合该收录标准的; 几何中位数满足 (b),
    所以保留. 不同的 bar, 同一套原则.

### 题目描述

给定 $N$ 个二维 (推广到 $d$ 维) 点 $\{x_1, \dots, x_N\} \subset
\mathbb{R}^d$, 找一个点 $x^* \in \mathbb{R}^d$ 使

$$f(x) = \sum_{i=1}^{N} \|x - x_i\|_2$$

最小. 这就是 **Fermat-Weber location problem** / **geometric median**.

**与 L1 的对比 (这是本题的核心 insight)**:

| 距离 | 目标 $f(x)$ | 最优解 | 可分解? | 求法 |
|------|-------------|--------|---------|------|
| **L1 (Manhattan)** | $\sum \\|x - x_i\\|_1$ | 各轴**中位数** | 是 | $O(N \log N)$ 或 $O(N)$ select. 见 [Best Meeting Point (LC 296)](db://262). |
| **L2^2 (squared)** | $\sum \\|x - x_i\\|_2^2$ | **均值** (centroid) | 是 | $O(N)$, 求导 = 0 直接闭式. |
| **L2 (Euclidean)** | $\sum \\|x - x_i\\|_2$ | **几何中位数** (Weber 解) | **否** | 无闭式; **Weiszfeld 迭代** + Vardi-Zhang 1999 退化修正. |

L1 可分解是因为 $\|x - x_i\|_1 = \sum_k |x_k - x_{i,k}|$, 各坐标完全独立;
L2 写开是 $\sqrt{\sum_k (x_k - x_{i,k})^2}$, 平方根把各坐标耦合在一起,
不能逐轴最小化. 这一点是面试常被追问的"为什么 1D 中位数推广不到 2D L2".

**注意 1D 退化**: 当 $d = 1$ 时 L2 距离就是 L1 距离 ($\sqrt{(x - x_i)^2}
= |x - x_i|$), 所以 1D 几何中位数就是普通中位数. 这是 [LC 296](db://262)
1D 子问题的本来面貌.

### 核心代码

```python
import numpy as np


def geometric_median(
    points: np.ndarray,
    max_iter: int = 200,
    tol: float = 1e-7,
) -> np.ndarray:
    # Weiszfeld iteration with Vardi-Zhang 1999 degeneracy correction.
    #
    # References:
    #   - Weiszfeld, E. (1937). Sur le point pour lequel la somme des
    #     distances de n points donnes est minimum.
    #   - Vardi & Zhang (2000). The multivariate L1-median and associated
    #     data depth. PNAS 97(4), 1423-1426.   [accessible companion paper]
    #   - Vardi & Zhang (1999). A modified Weiszfeld algorithm for the
    #     Fermat-Weber location problem. Mathematical Programming 90(3),
    #     559-566.   [the algorithmic fix used here]
    #
    # Idea: rewrite the first-order condition
    #     grad f(x) = sum_i (x - x_i) / ||x - x_i|| = 0
    # as a fixed-point map
    #     x = (sum_i x_i / d_i) / (sum_i 1 / d_i),  d_i = ||x - x_i||.
    # This is the Weiszfeld update. It is also exactly the IRLS solution
    # for a least-squares problem with weights w_i = 1 / d_i, hence the
    # algorithm's quasi-Newton character.
    #
    # Degeneracy: if x lands on some sample a_j, d_j = 0 and the update
    # is undefined. Vardi-Zhang 1999, Theorem 2.1: split the sum into
    # the "non-singular" part T(x) and the singular indices, and replace
    # the update by a controlled convex combination -- with the option to
    # certify that a_j IS the geometric median when a subgradient bound
    # holds (no further iteration needed).

    points = np.asarray(points, dtype=float)
    n, d = points.shape

    # Initialization. The centroid is a strictly convex starting point
    # (the L2^2 minimizer); using a sample point or the median per-axis
    # are also common. Centroid converges fastest in the typical case
    # (no extreme outliers).
    x = points.mean(axis=0)

    for _ in range(max_iter):
        diffs = points - x                                      # (n, d)
        dists = np.linalg.norm(diffs, axis=1)                   # (n,)

        # Vardi-Zhang 1999 degeneracy guard: any sample within tol of x.
        singular_mask = dists < tol
        regular_mask = ~singular_mask

        if np.any(singular_mask):
            # eta_j = how many samples coincide with x (handles repeats).
            eta = int(singular_mask.sum())
            inv_d = 1.0 / dists[regular_mask]                   # (m,)
            weight_sum = inv_d.sum()
            # T(x) = standard Weiszfeld step over the regular subset.
            T = (points[regular_mask] * inv_d[:, None]).sum(axis=0) / weight_sum
            # R(x) = ||sum_{i in regular} (x - x_i) / d_i||_2
            #      = norm of subgradient at x excluding singular term(s).
            r_vec = ((x - points[regular_mask]) * inv_d[:, None]).sum(axis=0)
            R = float(np.linalg.norm(r_vec))

            if R <= eta:
                # Vardi-Zhang Theorem 2.1: x IS the geometric median.
                # (Subgradient inclusion 0 at x certifies optimality.)
                return x

            # Otherwise: gamma in (0, 1) controls how far to move toward T;
            # the closer R is to eta, the closer to staying at x.
            gamma = max(0.0, 1.0 - eta / R)
            x_new = gamma * T + (1.0 - gamma) * x
        else:
            # Standard Weiszfeld step (no degeneracy).
            inv_d = 1.0 / dists                                  # (n,)
            x_new = (points * inv_d[:, None]).sum(axis=0) / inv_d.sum()

        # Convergence: small step size at the fixed point.
        if np.linalg.norm(x_new - x) < tol:
            return x_new
        x = x_new

    return x
```

**为什么必须 cite Vardi-Zhang 1999**: 朴素 Weiszfeld 在 $x = a_j$ 处直接
除零会 NaN. 一个常见的"工程修补"是把 $d_i$ 加一个小 $\varepsilon$
($d_i \to d_i + \varepsilon$), 这能避免除零, 但**改变了 fixed point**
($\sum_i (x - x_i) / (d_i + \varepsilon) = 0$ 的解不再是真正的几何中位数,
而是一个有偏估计). Vardi-Zhang 给的修正没有这个偏差: 它要么直接证明
$a_j$ 就是最优解 (Theorem 2.1, 当 $R \le \eta_j$), 要么用一个**保形**的
凸组合更新. 面试给加 epsilon 的简化版没问题, 但应明确指出代价.

### 关键要点

**1. 凸性 + 一阶最优条件**

$f(x) = \sum_i \|x - x_i\|_2$ 是有限多个凸函数的和, 本身凸. 在样本点之外
处处可微, $\nabla f(x) = \sum_i (x - x_i) / \|x - x_i\|$. 令 $\nabla f =
0$ 给出 fixed-point 方程 $x = (\sum x_i / d_i) / (\sum 1 / d_i)$ -- 这就
是 Weiszfeld 的来源. 在样本点上目标不可微, 改用次梯度 (subgradient).

**2. Weiszfeld 收敛性**

- **下降性**: Kuhn 1973 证明如果 $x^{(t)} \ne$ 任何 $x_i$, 则 $f(x^{(t+1)})
  < f(x^{(t)})$, 且收敛到全局最优 (因为 $f$ 凸).
- **退化情形**: 不加修正时, 如果某次迭代恰好命中样本点, 算法卡死.
  Vardi-Zhang 1999 是教科书级修正, **必须知道这个引用**.
- **收敛速度**: 实战常 $10$-$50$ 次内 $\|x^{(t+1)} - x^{(t)}\| < 10^{-7}$;
  数学上是线性收敛 (一阶), 与 GD 同阶, 比 Newton 慢.

**3. Weiszfeld 是 IRLS**

Weiszfeld 等价于在加权最小二乘 $\min \sum w_i \|x - x_i\|_2^2$ 上解析解
$x = \sum w_i x_i / \sum w_i$, 其中权重 $w_i = 1 / d_i^{(t)}$ 每步根据上
一步距离重新计算 (IRLS = Iteratively Reweighted Least Squares). 这就是
为什么它在凸优化教材里和 Logistic Regression 的 Newton/IRLS 求解器并列.

**4. 1D 退化 = 普通中位数**

$d = 1$ 时 $\|x - x_i\|_2 = |x - x_i|$, 几何中位数 = 一维中位数. 一维
中位数 $O(N)$ select, 不需要迭代. 这恰好是 [Best Meeting Point](db://262)
按轴分解后的子问题; LC 296 在 2D Manhattan 下也能逐轴用同一招, 但
**2D 欧氏就不能** (见上表)).

**5. 鲁棒性: breakdown point**

- **均值 (centroid)**: breakdown point $= 0$. 任何**一个**样本点跑到无穷远,
  centroid 就跟着跑到无穷远.
- **几何中位数**: breakdown point $\approx 0.5$. 必须**超过半数**样本变成
  离群点才能让几何中位数失效. 这是它在 robust regression / robust
  clustering 里替代均值的根本原因.
- 这条性质让几何中位数在带恶意污染的 federated learning 里也很常见
  (e.g. **RFA = Robust Federated Aggregation** 把 client 上传的梯度做
  geometric median, 抵御少数 byzantine 客户端).

### 面试追问

- **Q1: $N$ 很大 (10^7+), Weiszfeld 单步 $O(N d)$ 仍嫌慢, 怎么办?**
  - **Mini-batch SGD on the convex objective**: 单步采一个小批量 $B$,
    在该批上做一次 Weiszfeld 步 (或 vanilla GD step on subgradient),
    单步代价 $O(|B| d)$. 因为目标凸, 步长适当 SGD 收敛到全局最优.
  - **Coreset / sublinear approximation**: Cohen et al. 2016 给了
    $\tilde{O}(N d / \varepsilon)$ 时间近似算法 (基于 stochastic smoothing
    + 梯度下降), 在 $\varepsilon \le 0.01$ 量级下比 Weiszfeld 快很多.
  - **Approximate via centroid + one Weiszfeld step**: 工业上点数极大
    且分布较均匀时, 直接用 centroid 当估计或一步 Weiszfeld 即可, 解析
    误差通常只有 1-5%, 满足下游 (e.g. 中心点选址) 的精度需求.

- **Q2: 这题和 k=1 K-Means 是什么关系?**
  - K-Means 用 **L2^2 距离和** 当 cost, 解析解是 **centroid (均值)**.
  - 把 cost 换成 **L2 距离和** (不平方), 解析解就是 **几何中位数**.
  - 即 "k=1 K-Means + L2^2 = 均值, k=1 K-Means + L2 = 几何中位数".
  - 推广到 $k > 1$: **k-medians** clustering 用 L1 cost (per-axis median),
    **k-medoids** (PAM 算法) 强制中心是样本点, 也用某种距离和最小化.
    这一族在 outlier-heavy 数据上比标准 K-Means 稳健.

- **Q3: 1D 时如果改用梯度下降, 需要多少步?**
  - 1D 梯度下降 on $f(x) = \sum |x - x_i|$, 梯度是 $\sum \mathrm{sign}(x -
    x_i)$, 即"右侧点数 - 左侧点数". 步长 $\eta = 1$ 时一步移动一个样本
    位置, 走到中位数需要 $O(N)$ 步, 比直接排序 $O(N \log N)$ 还慢.
    这说明**梯度下降不是万能的**: 凸但非光滑的目标上, 专用算法
    (排序找中位数 / Weiszfeld IRLS) 几乎总是更快.

- **Q4: 离群点对几何中位数 vs centroid 的影响, 给个量化对比?**
  - 想象 $N - 1$ 个点都在原点附近 (噪声 $\sigma = 1$), 1 个点在
    $(10^6, 10^6)$. centroid 被拖到约 $(10^6 / N, 10^6 / N)$, 离原点
    $\sqrt{2} \cdot 10^6 / N$ -- $N = 100$ 时已经是 $1.4 \times 10^4$,
    严重偏离真实中心. 几何中位数仍在原点附近, 因为少于半数样本是离群点.
  - 这种"被一个离群样本拉飞"的现象在 mean-based clustering / regression
    里很常见, 是 robust statistics 整个领域的出发点.

- **Q5: 收敛保证 -- Weiszfeld 一定收敛到全局最优吗?**
  - 是 (Kuhn 1973 + Vardi-Zhang 1999 一并保证). 凸目标 + 下降性 + 任何
    极限点都满足一阶最优条件 -> 全局最优. 但**收敛速度只是线性**, 不像
    Newton 是二次收敛. 真正想要快的话改成 Newton on smoothed objective
    $f_\varepsilon(x) = \sum \sqrt{\|x - x_i\|^2 + \varepsilon^2}$, 二次
    收敛但每步 $O(d^3)$ -- 与 LR 那边 IRLS 的取舍是同一回事.

### 复杂度

- **Weiszfeld 单步**: $O(N d)$ -- 计算 $N$ 个距离 + 加权求和.
- **总复杂度**: $O(T N d)$, $T$ 通常 $10$-$50$. 与排序找 1D 中位数的
  $O(N \log N)$ 比, 在 $d = 1$ 上是更慢的; 在 $d \ge 2$ 上没有更便宜的
  通用算法.
- **空间**: $O(N d)$ 存样本, $O(d)$ 存当前估计 $x$.
- **数值**: 加 epsilon 的"工程修补"会引入偏差; Vardi-Zhang 修正才是
  unbiased fixed-point.
"""


# ============================================================
# Cross-link block to append to problems.id=262 (Best Meeting Point)
# ============================================================
# Note: GEOMETRIC_MEDIAN_NEW_ID is filled in at runtime after the new
# row is INSERTed (or looked up). The sentinel guards idempotency: if it
# already appears in id=262 notes, the cross-link is a no-op.

CROSSLINK_TEMPLATE = (
    "\n\n" + CROSSLINK_SENTINEL + "\n"
    "### L2 版本 (Geometric Median / Weber 问题)\n\n"
    "本题 (LC 296) 用 L1 (Manhattan) 距离, 按轴分解 -> 各轴中位数.\n"
    "把距离改成 L2 (Euclidean) 不平方就成了 Fermat-Weber location problem,\n"
    "目标 $\\sum \\|x - x_i\\|_2$ **不可分解**, 无闭式解, 必须用\n"
    "**Weiszfeld 迭代** + Vardi-Zhang 1999 退化修正.\n\n"
    "完整笔记: [Geometric Median (Weber 问题, L2 距离和最小)](db://{new_id})\n"
)


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        # ---- Step 1: UPSERT the new Geometric Median row ----
        row = conn.execute(
            "SELECT id, description, notes "
            "FROM problems WHERE title = ? AND source = ?",
            (TITLE, SOURCE),
        ).fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if row is None:
            cur = conn.execute(
                "INSERT INTO problems "
                "(title, description, notes, difficulty, pattern, "
                "category, tags, source, company_tags, priority, "
                "is_completed, comfort_level, description_source, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "0, 0, 'manual', ?)",
                (
                    TITLE,
                    DESCRIPTION,
                    NOTES,
                    DIFFICULTY,
                    PATTERN,
                    CATEGORY,
                    TAGS,
                    SOURCE,
                    COMPANY_TAGS,
                    PRIORITY,
                    now,
                ),
            )
            new_id = int(cur.lastrowid or 0)
            conn.commit()
            print(
                f"[INSERT] '{TITLE}' id={new_id} "
                f"description={len(DESCRIPTION)} notes={len(NOTES)} chars"
            )
            inserted_new = True
        else:
            pid, old_desc, old_notes = row
            old_desc = old_desc or ""
            old_notes = old_notes or ""
            new_id = int(pid)
            if old_desc == DESCRIPTION and old_notes == NOTES:
                print(
                    f"[SKIP] id={pid} '{TITLE}' description+notes byte-equal "
                    f"(desc={len(old_desc)} notes={len(old_notes)})"
                )
                inserted_new = False
            else:
                conn.execute(
                    "UPDATE problems "
                    "SET description = ?, notes = ?, difficulty = ?, "
                    "    pattern = ?, category = ?, tags = ?, "
                    "    company_tags = ?, priority = ? "
                    "WHERE id = ?",
                    (
                        DESCRIPTION,
                        NOTES,
                        DIFFICULTY,
                        PATTERN,
                        CATEGORY,
                        TAGS,
                        COMPANY_TAGS,
                        PRIORITY,
                        pid,
                    ),
                )
                conn.commit()
                print(
                    f"[UPDATE] id={pid} '{TITLE}' "
                    f"desc {len(old_desc)} -> {len(DESCRIPTION)}, "
                    f"notes {len(old_notes)} -> {len(NOTES)} chars"
                )
                inserted_new = False

        # ---- Step 2: UPSERT cross-link block in problems.id=262 ----
        bmp_row = conn.execute(
            "SELECT id, notes FROM problems WHERE id = ?",
            (BEST_MEETING_POINT_ID,),
        ).fetchone()
        if bmp_row is None:
            print(
                f"[WARN] problems.id={BEST_MEETING_POINT_ID} "
                "(Best Meeting Point) not found -- skipping cross-link"
            )
            return 0

        bmp_id, bmp_notes = bmp_row
        bmp_notes = bmp_notes or ""
        crosslink = CROSSLINK_TEMPLATE.format(new_id=new_id)

        if CROSSLINK_SENTINEL in bmp_notes:
            # Already linked. If the linked id changed (shouldn't happen
            # in normal flow, but possible if the row was deleted +
            # re-inserted), rewrite the block; otherwise no-op.
            existing_idx = bmp_notes.find(CROSSLINK_SENTINEL)
            existing_block = bmp_notes[existing_idx - 2:]  # include "\n\n"
            if existing_block.rstrip() == crosslink.rstrip():
                print(
                    f"[SKIP] id={bmp_id} (Best Meeting Point) already has "
                    f"geometric-median cross-link (-> id={new_id})"
                )
            else:
                # Strip old block (everything from "\n\n<sentinel>" to end-of-notes)
                # and append fresh block.
                rebuilt = bmp_notes[: existing_idx - 2].rstrip() + crosslink
                conn.execute(
                    "UPDATE problems SET notes = ? WHERE id = ?",
                    (rebuilt, bmp_id),
                )
                conn.commit()
                print(
                    f"[UPDATE] id={bmp_id} (Best Meeting Point) "
                    f"cross-link rewritten -> id={new_id}, "
                    f"notes {len(bmp_notes)} -> {len(rebuilt)} chars"
                )
        else:
            rebuilt = bmp_notes.rstrip() + crosslink
            conn.execute(
                "UPDATE problems SET notes = ? WHERE id = ?",
                (rebuilt, bmp_id),
            )
            conn.commit()
            print(
                f"[APPEND] id={bmp_id} (Best Meeting Point) "
                f"+ geometric-median cross-link (-> id={new_id}), "
                f"notes {len(bmp_notes)} -> {len(rebuilt)} chars "
                f"(inserted_new_row={inserted_new})"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
