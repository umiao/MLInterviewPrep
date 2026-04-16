"""Consolidate Regularization as the second canonical_hub (KG-P2-02).

Phase 2 second canonical hub. Target: framework_node 195 becomes the
CANONICAL authority on L1/L2 regularization, absorbing the unique L1/L2
proofs from legacy 合集 doc 21 and promoting Google R1 drill doc 55 to a
tactical drill that defers to the canonical hub.

Actions:
  1. Expand framework_nodes.description for id=195 with a canonical_hub
     marker, L1/L2 geometric picture + KKT primal-dual + soft-thresholding
     + Ridge-bias & James-Stein + Bayesian MAP priors (Gaussian/Laplace) +
     Elastic Net + AdamW vs L2 subtlety + Interview Pitfalls + Components
     list. Target length in [10000, 14000] chars.
  2. Trim company_documents.content for id=55 to <= 5500 chars: drop the
     re-derivations of L1 subgradient geometry, L2 closed-form, and
     Elastic Net (now canonical on node 195). Keep drill-specific treatments
     of Dropout, Early Stopping, Data-Aug/VRM, the 7-method panorama table,
     and the oral self-check. Add a canonical-pointer blockquote at the top
     per docs/protocol/kg_markdown_conventions.md.
  3. Insert concept_links rows:
       - (company_document:55) --canonical---->     (framework_node:195)
       - (framework_node:195)  --drill------->      (company_document:55)
       - (framework_node:195)  --absorbed_from-->   (company_document:21)
     Requires the absorbed_from-relation schema migration (runs first).

Idempotent: each target carries a sentinel
    '<!-- KG_P2_02_REGULARIZATION_20260416 -->'.
On re-run, targets with the sentinel print [UNCHANGED].
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- KG_P2_02_REGULARIZATION_20260416 -->"

CANONICAL_NODE_ID = 195
DRILL_DOC_ID = 55
ABSORBED_DOC_ID = 21
CANONICAL_PATH = "pillar2.regularization.regularization_canonical_hub"
CANONICAL_POINTER = (
    f"> **正典** [Regularization ({CANONICAL_PATH})]"
    f"(/framework/{CANONICAL_NODE_ID})"
)

MIGRATION_SCRIPT = (
    Path(__file__).resolve().parent
    / "_migrate_concept_links_add_absorbed_from_20260416.py"
)


NODE_195_DESCRIPTION = f"""<!-- doc_kind: canonical_hub -->
<!-- canonical_topic: regularization -->
{SENTINEL}

# Regularization 正典枢纽：L1/L2 几何、KKT 对偶、与 Bayesian MAP

> **前置** [Bias-Variance Tradeoff (pillar2.supervised_learning.bias_variance_tradeoff)](/framework/67)
> **前置** [Expectation & Variance (pillar7.probability_statistics.expectation_variance)](/framework/167)
> **前置** [Supervised Learning Setup](/framework/60)

## Overview

**Regularization（正则化）** 是通过对参数施加先验 / 约束来**压缩假设空间**的一组技术。在有限样本下，高容量模型的 variance 爆炸；正则化以**可控的 bias 增加**换取 variance 大幅下降，从而降低总期望 **MSE**（见 [Bias-Variance](/framework/67)）。

本节点是 L1/L2 正则的**正典**：它统一 penalty / constraint 两种写法、用 **KKT** 给出严格的 primal-dual 对应、给出 Ridge 与 Lasso 的闭式 / 软阈值解、从 **MAP** 角度解释高斯/拉普拉斯先验，并区分 Adam 下 weight decay 与 L2 penalty 的微妙差异（AdamW 修正）。dropout / early stopping / data augmentation 等非 L1/L2 正则技术属于 drill 范围，详见 [Google R1 Regularization Drill](/companies/google/documents/55)。

## 1. Penalty vs Constraint Form（两种等价写法）

L1 / L2 正则有两种等价写法——**penalty form** 与 **constraint form**。澄清这一点能避免将“几何切点图”误读为“优化过程图”。

Penalty form（无约束，含惩罚项）：

$$(\\mathrm{{P1}}):\\quad \\min_{{w}}\\; \\mathrm{{MSE}}(w) + \\lambda\\,\\|w\\|$$

Constraint form（有界约束域）：

$$(\\mathrm{{P2}}):\\quad \\min_{{w}}\\; \\mathrm{{MSE}}(w)\\quad \\text{{s.t.}}\\quad \\|w\\| \\le t$$

**静态几何对象（并非迭代轨迹）**：在 $w$ 空间：

- **椭圆等高线**：$\\mathrm{{MSE}}(w)$ 的 level set，是一族**同心椭圆**，中心为无约束 MSE 最小点 $\\hat w$（即 **OLS** 解）。
- **约束区域**：L1 下是以原点为中心的**菱形（$\\ell_1$ ball）**；L2 下是**圆 / 球（$\\ell_2$ ball）**。
- **最优解 $w^*$**：从椭圆中心 $\\hat w$ 出发不断**放大等高线**，**首次触碰约束区域**的那个点就是 $w^*$。这是**位置关系**，与优化算法、初始点、步长都无关——这张图描述的是**最优解在哪里**，不是**解是怎么走到的**。

**为什么 L1 偏顶点（稀疏性几何直觉）**：菱形的**顶点凸出**（锥形尖角），椭圆从大多数方向逼近时会**先碰到顶点**；而顶点恰好落在**坐标轴上**，对应某个分量 $w_i = 0$——这就是 L1 产生**稀疏解**的几何原因。维度升高时，$\\ell_1$ 单位球的顶点数以 $O(2^p)$ 增长，稀疏性倾向**更强**。

**为什么 L2 不稀疏**：圆 / 球表面**处处光滑**，椭圆与圆的切点可以出现在圆周上**任意位置**，几乎不会精确落在坐标轴——因此 L2 只把参数**整体压小**，却**不压到零**。

**常见误读纠正**：这张“椭圆 + 菱形/圆”图**不是**梯度下降的轨迹图，也不反映 $\\lambda$ 或初始点的影响；它仅描述**最优解位置**。penalty form 里调大 $\\lambda$ $\\Leftrightarrow$ constraint form 里缩小 $t$（约束区收紧），两者通过下一节的 **KKT** 一一对应。

## 2. Primal-Dual Equivalence via KKT

上一节给了**几何直觉**，本节给**严格推导**：penalty form (P1) 与 constraint form (P2) 通过 **Lagrangian** 和 **KKT 条件**一一对应。以 L1 为例（L2 推导同构，只把 $\\|w\\|_1$ 换成 $\\|w\\|_2^2$）。

**方向 1：(P2) ⇒ (P1)**。写 (P2) 的 Lagrangian，其中 $\\lambda \\ge 0$ 为对偶变量：

$$\\mathcal{{L}}(w,\\lambda) = \\mathrm{{MSE}}(w) + \\lambda\\bigl(\\|w\\| - t\\bigr)$$

对偶函数（对 w 内层求极小）：

$$g(\\lambda) = \\min_{{w}}\\;\\mathcal{{L}}(w,\\lambda) = \\underbrace{{\\min_{{w}}\\bigl[\\mathrm{{MSE}}(w) + \\lambda\\|w\\|\\bigr]}}_{{\\text{{正是 (P1)}}}} \\;-\\;\\lambda t$$

中括号内的子问题**恰好就是 (P1)**；因此在固定 $\\lambda$ 下，两问题有**相同的内层最优 w**。由 **Slater 条件**（只要 $t > 0$，取 $w = 0$ 严格满足 $\\|w\\| < t$），强对偶成立，**KKT** 条件既必要又充分：

$$\\begin{{aligned}} &\\text{{Stationarity:}}\\quad 0 \\in \\partial_w \\mathrm{{MSE}}(w^*) + \\lambda^*\\,\\partial\\|w^*\\|\\\\ &\\text{{Primal feasibility:}}\\quad \\|w^*\\| \\le t\\\\ &\\text{{Dual feasibility:}}\\quad \\lambda^* \\ge 0\\\\ &\\text{{Complementary slackness:}}\\quad \\lambda^*\\bigl(\\|w^*\\| - t\\bigr) = 0 \\end{{aligned}}$$

**方向 2：(P1) ⇒ (P2)**。给定某个 $\\lambda \\ge 0$，令 $w^*(\\lambda)$ 为 (P1) 最优解；取 $t = \\|w^*(\\lambda)\\|$。反证：若存在某 $\\tilde w$ 使 $\\mathrm{{MSE}}(\\tilde w) < \\mathrm{{MSE}}(w^*)$ 且 $\\|\\tilde w\\| \\le t$，则 $\\mathrm{{MSE}}(\\tilde w) + \\lambda\\|\\tilde w\\| < \\mathrm{{MSE}}(w^*) + \\lambda\\|w^*\\|$，与 $w^*$ 是 (P1) 最优矛盾。故 $w^*$ 也是 (P2) 对该 $t$ 的最优解。

**互补松弛的两种几何情形**：

- **情形 (i)**：$\\lambda^* = 0$。约束不起作用，$w^* = \\hat w$ 已经在约束区内——等价于 penalty form 里 $\\lambda$ 过小、正则失效。
- **情形 (ii)**：$\\|w^*\\| = t$。最优解**贴边界**；L1 下典型就是顶点，L2 下是圆周上某点。这就是几何图里“首次触碰”场景的严格对应。

**一句话总结**：$\\lambda$（penalty 强度）与 $t$（约束半径）通过 **KKT** **一一对应**；几何图呈现的是 KKT 最优性条件的**可视化**，而非优化过程。L2 推导结构完全相同，只需把次梯度 $\\partial\\|w\\|_1$ 换为光滑梯度 $\\nabla\\|w\\|_2^2 = 2w$。

## 3. Closed-Form Ridge vs Soft-Thresholding Lasso

Ridge 闭式解（正规方程加正则项）：

$$\\hat\\beta_{{\\text{{ridge}}}} = (X^\\top X + \\lambda I)^{{-1}} X^\\top y$$

加上 $\\lambda I$ 之后，即便 $X^\\top X$ 奇异（多重共线，multicollinearity）也可解——这正是 L2 缓解**共线性**的代数原因。特征值较小的方向被 $\\lambda$ 抬升，使得估计不再发散。用 SVD 写，若 $X = U D V^\\top$，则 Ridge 的逐奇异值收缩因子为：

$$\\hat w_j^{{\\text{{ridge}}}} = \\frac{{d_j^2}}{{d_j^2 + \\lambda}}\\,\\hat w_j^{{\\text{{OLS}}}}$$

**小奇异值（不稳定方向）被收缩得最多**，大奇异值几乎不变——这是"自适应的尺度化"。

正交设计下 Lasso 有逐坐标闭式解（**soft-thresholding** operator）：

$$\\hat\\beta_j^{{\\text{{lasso}}}} = \\operatorname{{sign}}\\!\\left(\\hat\\beta_j^{{\\text{{OLS}}}}\\right)\\cdot\\max\\!\\left(|\\hat\\beta_j^{{\\text{{OLS}}}}| - \\lambda,\\;0\\right)$$

当 $|\\hat\\beta_j^{{\\text{{OLS}}}}| \\le \\lambda$，坐标被"削平"为 0——这就是 **L1 做特征选择（feature selection）**的算法实现。Ridge 对应的逐坐标操作是 $\\hat\\beta_j = \\hat\\beta_j^{{\\text{{OLS}}}} / (1 + \\lambda)$，**按比例缩小**，永不为 0。

## 4. Biased Estimators & James-Stein（正则引入的偏差）

OLS 是**无偏**的：$E[\\hat\\beta_{{\\text{{OLS}}}}] = \\beta_{{\\text{{true}}}}$。但 Ridge 不是：

$$E[\\hat\\beta_{{\\text{{Ridge}}}}] = (X^\\top X + \\lambda I)^{{-1}}X^\\top X \\cdot \\beta_{{\\text{{true}}}} \\neq \\beta_{{\\text{{true}}}}$$

Ridge estimator **系统性地把系数向零收缩**，因此是 biased 的。Lasso 同理，额外把一部分系数精确压到 0（硬性的稀疏 bias）。

**为什么值得引入 bias？** 由 MSE 分解 $\\mathrm{{MSE}} = \\mathrm{{Bias}}^2 + \\mathrm{{Variance}}$，OLS 在 $p$ 较大、$n$ 较小时 variance 爆炸；Ridge / Lasso 付出少量 bias 换取方差大幅下降，**总 MSE 下降**——这就是正则化存在的根本原因。

**James-Stein 现象**：当维度 $p \\ge 3$ 时，任意 biased shrinkage estimator 的 MSE **严格小于** OLS（Stein 1956, James-Stein 1961）。这是一个反直觉的数学结论：**在三维及以上，对无偏估计做一点点收缩一定会让总 MSE 变好**。这为 Ridge / Lasso 提供了频率学派的正当性基础。

面试速写：`ridge_regression(X, y, lam)` 的实现就是 `np.linalg.solve(X.T @ X + lam * I, X.T @ y)`；Lasso 的坐标下降就是逐坐标做 `sign(rho) * max(|rho| - lam/n, 0)`。两行代码里分别嵌了"闭式解"与"软阈值"两个核心意象。

## 5. Bayesian / MAP View（先验视角）

正则化等价于对参数加一个**先验**并做 **MAP** 估计：

$$\\hat\\theta_{{\\text{{MAP}}}} = \\arg\\max_\\theta\\; \\underbrace{{P(D \\mid \\theta)}}_{{\\text{{似然}}}}\\cdot \\underbrace{{P(\\theta)}}_{{\\text{{先验}}}}$$

对 log 后可写为 $\\arg\\min_\\theta\\,\\bigl[-\\log P(D\\mid\\theta) - \\log P(\\theta)\\bigr]$。将 $-\\log P(\\theta)$ 当作 penalty，**不同先验对应不同正则**：

- **L2 = Gaussian prior**：$P(\\theta) = \\mathcal{{N}}(0, \\tau^2 I)$，$-\\log P(\\theta) = \\frac{{1}}{{2\\tau^2}}\\|\\theta\\|_2^2 + \\text{{const}}$。对应 Ridge 的二次 penalty，$\\lambda = 1/(2\\tau^2)$。高斯在 0 处**光滑**、没有尖峰——先验并不特别偏好"严格等于 0"。

- **L1 = Laplace prior**：$P(\\theta_j) = \\frac{{1}}{{2b}}\\exp(-|\\theta_j|/b)$，$-\\log P(\\theta) = \\frac{{1}}{{b}}\\|\\theta\\|_1 + \\text{{const}}$。对应 Lasso 的一次 penalty，$\\lambda = 1/b$。拉普拉斯在 0 处**有尖峰**（峰值密度高于相同方差的高斯），**先验本身就偏好稀疏解**——这是 L1 稀疏性的**概率版解释**，与"菱形顶点"的几何解释完全等价。

**一句话总结**：正则 penalty 的形状 = 负对数先验的形状。想要什么样的稀疏性，就用什么样的先验。

## 6. Elastic Net：Bridging L1 and L2

Elastic Net 同时包含两种惩罚：

$$\\min_{{\\beta}}\\;\\frac{{1}}{{2n}}\\|y - X\\beta\\|_2^2 + \\lambda\\!\\left[\\alpha\\|\\beta\\|_1 + \\tfrac{{1-\\alpha}}{{2}}\\|\\beta\\|_2^2\\right]$$

$\\alpha=1$ 退化为 Lasso，$\\alpha=0$ 退化为 Ridge。其约束区域是**菱形与圆的凸组合**——仍保留坐标轴上的"轻微尖角"得到稀疏性，同时圆弧部分让**高度相关特征被一起保留**。Lasso 面对一组高度相关特征（correlated features）时常**任选一个**；Elastic Net 倾向**同时保留**它们，在基因组学、点击预测等 $p \\gg n$ 且特征成组的场景下更稳。

## 7. Weight Decay ≠ L2 in Adam（AdamW 修正）

在 SGD 下，**L2 penalty 与 weight decay 完全等价**：

$$w_{{t+1}} = w_t - \\eta\\,(\\nabla J + \\lambda w_t) = (1 - \\eta\\lambda)\\,w_t - \\eta\\,\\nabla J$$

即"在梯度里加 $\\lambda w_t$"等于"把参数直接乘以 $1-\\eta\\lambda$"。但在 **Adam** 下两者不再等价：L2 penalty 把 $\\lambda w$ 加进**原始梯度**里，之后被 Adam 的自适应二阶矩 $\\sqrt{{v_t}}$ **除掉**；于是历史梯度大的参数（$v_t$ 大）得到的**实际正则强度变小**——正则不再均匀。

**AdamW**（Loshchilov & Hutter 2019）把 decay 挪出自适应步之外：

$$w_{{t+1}}^{{\\text{{AdamW}}}} = (1 - \\eta\\lambda)\\,w_t - \\eta\\,\\frac{{m_t}}{{\\sqrt{{v_t}} + \\epsilon}}$$

decay 项 $(1-\\eta\\lambda) w_t$ **直接作用于参数**，不经过 $v_t$ 的缩放，因此所有参数获得**均匀的正则强度**。这也解释了为什么 transformer 训练默认使用 AdamW 而不是 Adam+L2。面试一句话：**"Adam 的自适应步会吞掉 L2 梯度，所以 transformer 用 AdamW 把 weight decay 解耦出去。"**

## 8. Interview Q&A

**Q: 为什么 L1 会产生稀疏解，而 L2 不会？**

给三条互相印证的解释。**几何**：OLS 等高线为椭圆，L1 约束区是菱形，**尖角在坐标轴上**，椭圆与菱形相切大概率落在顶点，对应部分 $\\beta_i = 0$。**代数**：L1 在 0 处的次梯度为区间 $[-1, 1]$，数据梯度只要落入 $[-\\lambda, \\lambda]$ 即被 **KKT** 允许取 $\\beta_i=0$，形成**软阈值**；L2 的梯度在 0 处连续且为 0，没有这种吸附机制。**Bayesian**：L1 = Laplace prior，密度在 0 有尖峰，先验偏好稀疏；L2 = Gaussian prior，0 处光滑，不偏好稀疏。

**Q: 为什么多重共线性（multicollinearity）下 L2 比 L1 更稳？**

共线特征让 $X^\\top X$ 病态（接近奇异），OLS 估计方差爆炸。L2 把矩阵改为 $X^\\top X + \\lambda I$，**小特征值被抬升**，条件数下降，估计方差有界。L1 虽然也能缩小方差，但它会在一组高度相关的特征中**任选一个保留、其它置零**，选择哪一个对数据小扰动敏感；而 L2 会把权重**均匀分摊**给整组特征，预测更稳定。若既要稀疏又要稳，用 **Elastic Net**（$\\alpha \\approx 0.5$）可兼得。

**Q: 什么场景下 L1 / L2 都不够？**

(1) 真模型**非线性**，稀疏线性先验不匹配——换 GBDT 或 DNN + dropout；(2) 特征具有**群组结构**（grouped features，例如 one-hot 的一整个类别变量），标量 L1 会破坏组内一致性，用 **Group Lasso**；(3) 参数有**时序或空间光滑性**，用 **Fused Lasso** / total-variation 惩罚；(4) 样本严重不平衡时，正则化会抑制少数类信号——同时调 class weight 或用 focal loss；(5) 大部分特征是**噪声**且相互相关，Lasso 会误选——可改用 **SCAD / MCP** 等非凸正则降低 bias。

## Interview Pitfalls（常见误区）

- **"L1 = Lasso, L2 = Ridge 只是名字不同"** —— 不对。几何、代数、Bayesian 三层含义都不同；L1 产生稀疏，L2 产生稠密收缩。
- **"加了正则化就一定会变好"** —— 不对。高 bias 场景下正则反而加重欠拟合。正则化**换偏差、降方差**，只在方差占主导时收益为正。
- **"Adam + L2 = AdamW"** —— 错。Adam 下 L2 不等于 weight decay（见第 7 节），两者只有在 SGD 下才完全等价。
- **"正则图里 $\\lambda$ 增大意味着沿梯度方向往菱形里挪"** —— 误读。几何图是**静态最优解位置图**，与 $\\lambda$ 的对应关系是"penalty 的 $\\lambda$ $\\Leftrightarrow$ constraint 的 $t$"；$\\lambda\\uparrow$ 对应 $t\\downarrow$（约束区收紧），不是梯度轨迹。
- **"L1 比 L2 总是更好——能做特征选择"** —— 看场景。相关特征组里 L1 不稳定；$p\\gg n$ 稀疏真模型时 L1 更优；一般"所有特征都重要"时 L2 更优。
- **"Ridge 闭式解里 $\\lambda$ 改为 $\\lambda I$ 是因为方便"** —— 错。$\\lambda I$ 在**所有方向等向抬升特征值**；若希望各向不同的正则强度，需要用 $\\text{{diag}}(\\lambda_1, \\dots)$ 替换 $\\lambda I$（tikhonov generalized form）。
- **"正则化只对 linear model 有意义"** —— 不对。L2 = weight decay 是 DNN 的基石；L1 在稀疏自编码器、结构化稀疏、LASSO-style 特征选择里都是主力。
- **"Ridge / Lasso 是 unbiased estimator"** —— 错，均为 biased（见第 4 节）。James-Stein 告诉我们：在 $p\\ge 3$ 时，biased 反而是**数学上必然更优**的选择。

## Components（复合概念组成）

本节点是 Regularization 的 canonical hub；下列节点 / drill 是它统摄的周边：

- [Bias-Variance Tradeoff (pillar2.supervised_learning.bias_variance_tradeoff)](/framework/67) -- 前置正典；本节点的"换偏差、降方差"由彼节点定义。
- [Google R1 Regularization Deep Dive Drill](/companies/google/documents/55) -- Google R1 面试的战术 drill（dropout / early stopping / data aug / AdamW 口述练习），不再重复 L1/L2 推导。
- [Expectation & Variance (pillar7.probability_statistics.expectation_variance)](/framework/167) -- 先验 / 后验推导所需的概率基础。

## Key Takeaways

- **两种写法等价**：penalty $\\lambda\\|w\\|$ 与 constraint $\\|w\\|\\le t$ 通过 **KKT** 一一对应；几何图呈现的是静态最优解位置，不是优化轨迹。
- **L1 稀疏性的三层解释**：菱形顶点（几何）、软阈值（代数）、Laplace 先验尖峰（Bayesian），三者完全等价。
- **Ridge 的代数价值**：$\\lambda I$ 抬升小奇异值，解决共线性；逐奇异值收缩因子 $d_j^2/(d_j^2+\\lambda)$。
- **Lasso 的软阈值**：$\\operatorname{{sign}}(\\hat\\beta_j)\\max(|\\hat\\beta_j|-\\lambda, 0)$ 实现特征选择。
- **Bias-Variance tradeoff 的正当性**：$p\\ge 3$ 时 James-Stein 定理保证 biased shrinkage 的 MSE 严格小于 OLS。
- **AdamW 的必要性**：Adam 的自适应步破坏了 L2 与 weight decay 的等价性；transformer 默认用 AdamW 解耦 decay。
- **Elastic Net = 几何凸组合**：保留 L1 顶角得到稀疏，保留 L2 圆弧让相关特征组一起保留。
- **Regularization ≠ 万能**：非线性、群组、时序、不均衡、非凸先验——都有专门对应的正则家族（GBDT / Group Lasso / Fused Lasso / focal loss / SCAD）。

> **后续** [Bias-Variance Tradeoff](/framework/67)
> **后续** [Model Selection & Cross-Validation](/framework/68)
"""

# Note: we strip trailing blanks to keep the DB column compact.
NODE_195_DESCRIPTION = NODE_195_DESCRIPTION.rstrip() + "\n"


DOC_55_CONTENT = f"""{SENTINEL}

# Regularization Deep Dive -- Google R1 Prep (Drill)

{CANONICAL_POINTER}

本 drill 服务 Google R1 面试的**口述练习**：L1 / L2 几何推导、KKT、soft-thresholding、Bayesian prior、AdamW 等核心内容已固化到 canonical hub。此处只保留 **drill-specific** 的战术要点——dropout、early stopping、data augmentation、以及 7 法全景表与 30 秒口述自测。

## Prerequisites

- Canonical hub: [Regularization](/framework/195)（务必先过一遍）
- 神经网络训练循环（forward / backward pass）
- 随机采样与蒙特卡洛的基本直觉

## 1. Dropout -- Bayesian Approximation & Ensemble View

训练阶段：每次前向把每个单元以概率 $p$ 置零。推理阶段：启用全部单元，activation 乘以 $(1-p)$；或训练时用 **inverted dropout** 直接除以 $(1-p)$，推理不变。

**集成视角（Srivastava 2014）**：$n$ 个单元 -> $2^n$ 个 thinned networks。平均预测近似等于一个指数级 ensemble 的平均。

**Bayesian 视角（Gal & Ghahramani 2016）**：推理时**保持 dropout 开启**，做 $T$ 次 forward，得到预测均值与不确定性。MC Dropout 的方差估计：

$$\\mathrm{{Var}}[y^*] \\approx \\frac{{1}}{{T}}\\sum_{{t=1}}^{{T}} f_{{\\theta_t}}(x^*)^2 - \\left(\\frac{{1}}{{T}}\\sum_{{t=1}}^{{T}} f_{{\\theta_t}}(x^*)\\right)^2$$

**口述捷径**：“Dropout 是 $2^n$ 子网络的廉价集成；推理时不关它还能免费拿到不确定性。”

## 2. Early Stopping -- Implicit L2

从 $w=0$ 起，小学习率的 GD 在权重空间画一条轨迹；**停得早就等于限制 $\\|w\\|$ 的增长**。$T$ 步 × 学习率 $\\eta$ × 梯度上界 $G_{{\\max}}$：

$$\\|w_T\\| \\le \\eta \\cdot T \\cdot G_{{\\max}}$$

Bishop (1995) / Sjoberg & Ljung (1995) 证明：在二次损失下，early stopping 的第 $T$ 步等价于 L2 正则 $\\lambda_{{\\text{{eff}}}} \\propto 1/(\\eta T)$。

**口述捷径**：“Early stopping = 隐式 L2；步数少 = 范数小 = 正则强。免费但把优化和正则耦合在一起。”

## 3. Data Augmentation -- Vicinal Risk Minimization

ERM 最小化的是**训练点上的平均损失**；数据增广把每个点替换为一个**邻域（vicinity）**。形式化（Chapelle 等 2000）：

$$R_{{\\text{{VRM}}}} = \\frac{{1}}{{n}}\\sum_{{i=1}}^{{n}} \\mathbb{{E}}_{{x' \\sim \\nu(x_i)}}[\\ell(f(x'), y_i)]$$

vicinity 分布 $\\nu$ 编码领域先验：图像用 flip / crop，NLP 用 synonym replacement，Mixup 用插值。**正则化效果**：模型必须在邻域内都对，决策边界被平滑，variance 下降而 bias 不变（只要 augmentation 保标签）。

**口述捷径**：“Augmentation 就是在邻域上训练，不是在点上。数学上是 VRM——vicinity kernel 取代 ERM 里的 Dirac delta。”

## 4. AdamW in One Breath（canonical 已详述，此处仅口述）

> **正典** [Regularization §7 AdamW](/framework/195)

"Adam 的 $v_t$ 把 L2 梯度按历史自适应地缩小，所以正则强度不均匀；AdamW 把 decay 挪到 Adam 步之外，所有参数均匀 $(1-\\eta\\lambda)$。transformer 用 AdamW。"

## 5. 7-Method Regularization Panorama

| Method | What It Constrains | Oral 10-Second Pitch |
| --- | --- | --- |
| L1 | 激活的特征数 | 菱形顶点在坐标轴 => 稀疏 |
| L2 / Ridge | 权重整体幅度 | 圆面光滑；闭式 $(X'X+\\lambda I)^{{-1}} X'y$ |
| Elastic Net | 相关特征组 | L2 绑定整组，L1 删除整组 |
| Dropout | 隐层共适应 | $2^n$ 子网集成；MC 拿不确定性 |
| Early Stopping | 原点出发的轨迹长度 | 隐式 L2；$\\lambda \\sim 1/(\\eta T)$；最便宜 |
| AdamW | 各参数统一幅度 | decoupled decay；Adam+L2 非 AdamW |
| Data Aug / VRM | 决策边界光滑度 | 在邻域上训练而非点上 |

## 6. 30-Second Oral Self-Check

- [ ] L1 稀疏的三层解释（几何 / 代数 / Bayesian）--- 指向 canonical §1/§5
- [ ] L2 闭式解 $(X^\\top X+\\lambda I)^{{-1}}X^\\top y$ 与逐奇异值收缩 --- canonical §3
- [ ] Ridge vs Lasso 的 bias 谁更大？两者都 biased，L1 还额外把系数压到 0
- [ ] Dropout = $2^n$ ensemble + MC Dropout uncertainty
- [ ] Early stopping 是隐式 L2，$\\lambda\\propto 1/(\\eta T)$
- [ ] AdamW 的一句话解释（$v_t$ 吞 L2；decay 解耦）
- [ ] Data aug = VRM，vicinity kernel 取代 Dirac delta
- [ ] James-Stein：$p\\ge 3$ 时收缩估计严格优于 OLS

**面试口吻收尾**："L1 / L2 的推导我画图+写 KKT+ Bayesian 三条线都能走；dropout 我用 ensemble 和 MC 两种解释；AdamW 我能说清 $v_t$ 吞 L2 这个技术细节。"
"""

DOC_55_CONTENT = DOC_55_CONTENT.rstrip() + "\n"


def _ensure_schema() -> None:
    """Run the absorbed_from-relation migration; fail loudly if it errors."""
    result = subprocess.run(
        [sys.executable, str(MIGRATION_SCRIPT)],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(
            f"Schema migration failed (code {result.returncode})"
        )


def _patch_node_195(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()
    if row is None:
        return "missing"
    if (row[0] or "") == NODE_195_DESCRIPTION:
        return "unchanged"
    conn.execute(
        "UPDATE framework_nodes SET description=? WHERE id=?",
        (NODE_195_DESCRIPTION, CANONICAL_NODE_ID),
    )
    return "patched"


def _patch_doc_55(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT content, doc_kind FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()
    if row is None:
        return "missing"
    if (row[0] or "") == DOC_55_CONTENT and row[1] == "drill":
        return "unchanged"
    conn.execute(
        "UPDATE company_documents SET content=?, doc_kind='drill' WHERE id=?",
        (DOC_55_CONTENT, DRILL_DOC_ID),
    )
    return "patched"


def _insert_concept_links(conn: sqlite3.Connection) -> tuple[int, int]:
    """Insert the three concept_links rows idempotently. Returns (inserted, skipped)."""
    pairs = [
        ("company_document", DRILL_DOC_ID, "framework_node", CANONICAL_NODE_ID,
         "canonical", "Google R1 drill defers to Regularization canonical hub (KG-P2-02)"),
        ("framework_node", CANONICAL_NODE_ID, "company_document", DRILL_DOC_ID,
         "drill", "Google R1 Regularization drill companion (KG-P2-02)"),
        ("framework_node", CANONICAL_NODE_ID, "company_document", ABSORBED_DOC_ID,
         "absorbed_from",
         "L1/L2 proofs absorbed from legacy 合集 doc 21 section 9 (KG-P2-02)"),
    ]
    inserted = skipped = 0
    for src_kind, src_id, dst_kind, dst_id, relation, note in pairs:
        cur = conn.execute(
            "INSERT OR IGNORE INTO concept_links "
            "(src_kind, src_id, dst_kind, dst_id, relation, weight, note) "
            "VALUES (?, ?, ?, ?, ?, 1.0, ?)",
            (src_kind, src_id, dst_kind, dst_id, relation, note),
        )
        if cur.rowcount:
            inserted += 1
        else:
            skipped += 1
    return inserted, skipped


def main() -> int:
    if not DB.exists():
        print(f"[ERROR] DB not found: {DB}")
        return 2

    _ensure_schema()

    conn = sqlite3.connect(str(DB))
    try:
        node_status = _patch_node_195(conn)
        doc_status = _patch_doc_55(conn)
        inserted, skipped = _insert_concept_links(conn)

        node_len = conn.execute(
            "SELECT length(description) FROM framework_nodes WHERE id=?",
            (CANONICAL_NODE_ID,),
        ).fetchone()[0]
        doc_len = conn.execute(
            "SELECT length(content) FROM company_documents WHERE id=?",
            (DRILL_DOC_ID,),
        ).fetchone()[0]

        problems = []
        if not (10000 <= node_len <= 14000):
            problems.append(
                f"node 195 length {node_len} outside target [10000, 14000]"
            )
        if doc_len > 5500:
            problems.append(f"doc 55 length {doc_len} exceeds 5500 cap")

        if problems:
            conn.rollback()
        else:
            conn.commit()
    finally:
        conn.close()

    tag = {"patched": "[PATCHED]", "unchanged": "[UNCHANGED]",
           "missing": "[MISSING]"}
    print(f"{tag[node_status]} framework_node {CANONICAL_NODE_ID} "
          f"(Regularization canonical hub), length={node_len}")
    print(f"{tag[doc_status]} company_document {DRILL_DOC_ID} "
          f"(Google R1 Regularization drill), length={doc_len}")
    print(f"[LINKS] inserted={inserted} skipped={skipped}")

    if problems:
        print("[FAIL] invariants violated (transaction rolled back):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("[DONE] KG-P2-02 Regularization canonical hub consolidation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
