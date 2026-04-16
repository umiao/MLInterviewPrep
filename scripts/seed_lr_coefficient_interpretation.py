"""Seed: Logistic regression coefficient interpretation into framework_node id=64.

Covers T-P0-446 AC:
 Expand framework_node id=64 (Linear Models) description from 145 bytes
 to >=3000 bytes. No new doc -- node description is the only deliverable.
 Pyramid base -- no fancy expansion, no duplication of doc 52 (Google DNN gist).

Scope:
 (a) continuous one-unit change -> odds multiplier exp(beta)
 (b) categorical one-hot, k levels, reference baseline -> exp(beta_k)
 (c) boolean flip -> exp(beta)
 (d) 3-example decision script for the typical Google / LinkedIn screen
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 64


NODE_DESCRIPTION = """# Linear Models（线性模型）

## Scope

本节覆盖线性回归（Normal Equation + GD + 6 条假设）与逻辑回归（sigmoid + BCE + 矩阵形式梯度）。机械推导请看 Doc 27/28/29 的 T2+T3 章节；本节聚焦 **interpretation 层**——尤其是 Google / LinkedIn 屏前题高频问的"系数 0.7 意味着什么？"。

## Linear Regression（一行复习）

$\\hat{y} = X\\beta$，闭式解 $\\hat{\\beta} = (X^{\\top}X)^{-1} X^{\\top} y$。系数 $\\beta_j$ 读作"控制其他特征时，$x_j$ 每增加 1 单位，$\\hat{y}$ 的平均变化"。这是直觉的起点，但逻辑回归的解读与此**不同**——下面展开。

## Logistic Regression Coefficient Interpretation

### 为什么系数不是"概率"的变化量

逻辑回归的 link function 是 logit：

$$\\log \\frac{p}{1-p} = \\beta_0 + \\beta_1 x_1 + \\cdots + \\beta_k x_k$$

左边是 **log-odds（对数几率）**，不是概率。所以 $\\beta_j$ 每增加 1 单位带来的是 log-odds 的加法改变；翻成 odds 就是**乘法**改变 $\\exp(\\beta_j)$。这是面试第一条必答：**"系数 exp 一下就是 odds ratio。"**

### (a) 连续变量（continuous feature）

$x_j$ 增加 1 个单位（其他特征不变），新旧 odds 之比：

$$\\frac{\\text{odds}_{\\text{new}}}{\\text{odds}_{\\text{old}}} = \\exp(\\beta_j)$$

- $\\beta_j = 0.7 \\Rightarrow \\exp(0.7) \\approx 2.01$：每增加 1 单位，positive 的 odds 翻一倍。
- $\\beta_j = -0.3 \\Rightarrow \\exp(-0.3) \\approx 0.74$：每增加 1 单位，odds 降到原来的 74%。
- 单位很重要：若 $x_j$ 是"年龄（岁）"，$\\beta_j$ 是"每多一岁"；若换成"年龄（十岁）"，数值会除以 10。**面试时务必问单位**。

### (b) 类别变量（one-hot with reference level）

一个 k 类的类别特征（颜色：red / blue / green），会编码成 k−1 个虚拟变量（reference level = green）。$\\beta_{\\text{red}}$ 是"red vs green"的 log-odds 差：

$$\\frac{\\text{odds}(x = \\text{red})}{\\text{odds}(x = \\text{green})} = \\exp(\\beta_{\\text{red}})$$

- **每个非参照类都是与参照类的成对比较，不是与整体的比较。**
- 换参照类（drop_first 选哪一列）会改变所有 $\\beta_k$ 的数值但不会改变两两比较的 odds ratio；报告时要明写 reference level。
- $\\beta_{\\text{red}} = 1.1, \\beta_{\\text{blue}} = 0.4$，reference=green：red vs green = $\\exp(1.1) \\approx 3.0$；blue vs green = $\\exp(0.4) \\approx 1.49$；red vs blue = $\\exp(1.1 - 0.4) \\approx 2.01$。

### (c) 布尔变量（boolean / 0-1 dummy）

等价于 k = 2 的类别 with reference=False：

$$\\frac{\\text{odds}(x = 1)}{\\text{odds}(x = 0)} = \\exp(\\beta)$$

- $\\beta = 0.7$：打开该特征（False → True）把 odds 乘 2.01——"该用户是 Premium 会员"使转化的 odds 翻倍。
- 对"概率"的影响是 **非线性** 的：当基线概率 $p_0 = 0.5$ 时，odds 翻倍后 $p_1 \\approx 0.67$（+17pp）；$p_0 = 0.1$ 时 $p_1 \\approx 0.18$（+8pp）；$p_0 = 0.9$ 时 $p_1 \\approx 0.95$（+5pp）。**不要说"概率翻倍"——说的是 odds 翻倍**。

## 3-Example Decision Script（屏前题演练）

面试官掏出一张表：某模型的 summary 给出三个 $\\beta$。每个情景按下面的三问模板走：

**Template**：(1) 变量类型？→ (2) 单位/参照类是什么？→ (3) $\\exp(\\beta)$ 是 odds ratio，翻成业务语言。

### 例 1：continuous — 连续变量

> "age 的系数是 0.04，年龄以岁为单位。这说明什么？"
>
> 答：$\\exp(0.04) \\approx 1.041$。其他特征不变时，**每多一岁**，转化的 odds 增加 4.1%。若用户从 25 岁到 35 岁，累计 $\\exp(0.04 \\times 10) = \\exp(0.4) \\approx 1.49$，odds 提高约 49%。注意是**odds 不是概率**，且结论只在 age 的采样区间内有效（外推无意义）。

### 例 2：categorical — 类别变量（one-hot）

> "device_type 是 three-level one-hot：mobile / desktop / tablet，reference=desktop。$\\beta_{\\text{mobile}} = 0.7$, $\\beta_{\\text{tablet}} = -0.2$。怎么解读？"
>
> 答：$\\exp(0.7) \\approx 2.01$——mobile 用户相对 desktop，转化 odds 翻倍；$\\exp(-0.2) \\approx 0.82$——tablet 用户 odds 降到 desktop 的 82%；mobile vs tablet = $\\exp(0.7 - (-0.2)) = \\exp(0.9) \\approx 2.46$。要补充：**reference 是 desktop**、不报告 desktop 的系数（它是 0）。如果业务想对比 mobile vs tablet 而不是 mobile vs desktop，要么换 reference 重拟，要么手算差值（上面做的）。

### 例 3：boolean — 布尔变量

> "is_premium 是 0/1 dummy，$\\beta = 1.1$。"
>
> 答：$\\exp(1.1) \\approx 3.0$。**是 Premium 会员**相较于**非 Premium**，转化 odds 翻 3 倍。若基线概率 $p_0 = 0.2$（非 Premium 转化率 20%），则 Premium 用户 $p_1 = \\frac{0.25 \\times 3}{1 + 0.25 \\times 3} = \\frac{0.75}{1.75} \\approx 0.43$——43%，而不是 20% × 3 = 60%。**odds 的乘法 ≠ 概率的乘法**，这一步是屏前题的常见踩雷点。

## Sister Nodes & Handoff

- **Loss Functions (node 68)**：BCE 推导与 softmax-CE 推广；本节假定读者会 BCE。
- **Regularization (node 69)**：L1/L2 对 $\\beta$ 数值的影响——L2 会缩小系数，但不改变**比率**解释（$\\exp(\\beta)$ 的相对大小仍保留），L1 会把不重要系数压到 0。
- **Bias-Variance (node 67)**：特征工程对 $\\beta$ 稳定性的影响；多重共线会让个别 $\\beta$ 数值剧烈震荡。
- **Evaluation Metrics (node 70)**：系数只解释"模型内部"，最终部署要看 operating-point 指标。
- **Calibration drill (doc 62, Google R1)**：预测概率的可信度——即使 $\\beta$ 解读正确，未校准的 $\\hat{p}$ 仍不能直接当概率读。

## Pitfalls（面试高频坑）

1. 说"系数 0.7 意味着概率翻倍"——错。是 **odds** 翻倍，概率按 $p = \\sigma(\\text{logit})$ 非线性映射。
2. 忘了 reference level——one-hot 的 $\\beta$ 不是"某类的绝对效应"，而是"相对 reference 的差"。
3. 忘了单位——"age 系数 0.04"是**每岁**还是**每十岁**？不问就无法给业务翻译。
4. 多重共线下硬读单个 $\\beta$——variance 极大，可能系数符号都是错的；要么看 VIF，要么看两两的 marginal odds ratio。
5. 忽略特征缩放——对连续变量做 standardize 后，$\\beta$ 变成"每一个标准差变化的 odds ratio"，解读时要说明口径。
6. 把"统计显著"和"业务显著"混为一谈——大样本下 $\\exp(\\beta) = 1.02$ 也能 $p < 0.001$，但对业务基本没用。报告 $\\exp(\\beta)$ 必须带置信区间与基线 odds。
"""


def update_framework_node() -> int:
    """Update framework_node id=64 description. Returns byte length."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT id, title FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            sys.exit(1)
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (NODE_DESCRIPTION, NODE_ID),
        )
        conn.commit()
        size = conn.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[DONE] framework_node id={NODE_ID} description updated: {size} bytes")
        return size
    finally:
        conn.close()


def main() -> None:
    """Run the seed and sanity-check the byte target."""
    size = update_framework_node()
    if size < 3000:
        print(f"[FAIL] framework_node id={NODE_ID} description is {size} bytes, target >=3000")
        sys.exit(1)
    print(f"[OK] Acceptance check passed (node={size} bytes, target>=3000).")


if __name__ == "__main__":
    main()
