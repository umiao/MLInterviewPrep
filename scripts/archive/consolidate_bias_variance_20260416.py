"""Consolidate Bias-Variance as a canonical_hub (KG-P2-01).

Phase 2 first real consolidation. Target: framework_node 67 becomes the
CANONICAL authority on Bias-Variance; Google R1 drill doc 56 is rewritten as
a tactical drill that points at the canonical hub rather than re-deriving the
decomposition.

Actions:
  1. Expand framework_nodes.description for id=67 with a canonical_hub marker,
     complexity-axis diagnostic curves, explicit remedies matrix, interview
     pitfalls, Components (composed_of) list, and 后续 links. Target length
     in [8000, 12000] chars.
  2. Trim company_documents.content for id=56 to <= 5000 chars: drop the
     decomposition re-derivation, keep Google-specific tactical drill (4-quadrant
     diagnosis, bagging variance formula + RF insight, RF vs GBDT duality,
     learning curve 4 shapes, 2-minute oral self-check). Add canonical pointer
     blockquote at the top per docs/protocol/kg_markdown_conventions.md.
  3. Insert concept_links rows:
       - (company_document:56) --canonical--> (framework_node:67)
       - (framework_node:67)   --drill------> (company_document:56)
     Requires the drill-relation schema migration (run automatically).

Idempotent: each target carries a sentinel '<!-- KG_P2_01_BIAS_VARIANCE_20260416 -->'.
On re-run, targets with the sentinel print [UNCHANGED].
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- KG_P2_01_BIAS_VARIANCE_20260416 -->"

CANONICAL_NODE_ID = 67
DRILL_DOC_ID = 56
CANONICAL_PATH = "pillar2.supervised_learning.bias_variance_tradeoff"
CANONICAL_POINTER = (
    f"> **正典** [Bias-Variance Tradeoff ({CANONICAL_PATH})]"
    f"(/framework/{CANONICAL_NODE_ID})"
)

MIGRATION_SCRIPT = (
    Path(__file__).resolve().parent
    / "_migrate_concept_links_add_drill_20260416.py"
)


NODE_67_DESCRIPTION = f"""<!-- doc_kind: canonical_hub -->
<!-- canonical_topic: bias_variance -->
{SENTINEL}

# Bias-Variance Tradeoff（偏差-方差权衡）

> **前置** [Supervised Learning Setup](/framework/60)
> **前置** [Expectation & Variance (pillar7.probability_statistics.expectation_variance)](/framework/167)

## Overview

**Bias-Variance Tradeoff（偏差-方差权衡）** 是解释模型泛化能力的核心概念。它将预测误差分解为不可约噪声、偏差（欠拟合）和方差（过拟合）三个部分。这一框架指导着每一个模型选择和正则化决策，是MLE面试中最基础也最重要的理论之一。

理解偏差-方差权衡的关键在于：我们无法同时最小化偏差和方差，必须在两者之间找到最优平衡点。模型过于简单会导致高偏差（无法捕捉数据中的真实模式），模型过于复杂则导致高方差（对训练数据的微小变化过度敏感）。

## Core Concepts

### Error Decomposition（误差分解）

对于在数据集 $D$ 上训练的模型 $\\hat{{f}}$，在点 $x$ 处的期望预测误差可以精确分解为三项：

$$E_D[(y - \\hat{{f}}(x))^2] = \\text{{Bias}}[\\hat{{f}}(x)]^2 + \\text{{Var}}_D[\\hat{{f}}(x)] + \\sigma^2$$

其中各项含义如下：

**Bias（偏差）**：模型预测的期望值与真实值之间的差距

$$\\text{{Bias}}[\\hat{{f}}(x)] = E_D[\\hat{{f}}(x)] - f(x)$$

偏差度量的是模型的系统性误差，反映了模型假设与真实函数之间的差距。例如用线性模型拟合非线性数据，无论训练多少次，平均预测都会偏离真实值。

**Variance（方差）**：模型预测对训练数据变化的敏感度

$$\\text{{Var}}_D[\\hat{{f}}(x)] = E_D[(\\hat{{f}}(x) - E_D[\\hat{{f}}(x)])^2]$$

方差度量的是在不同训练集上得到的模型之间的波动。高方差意味着模型过度拟合了训练数据中的噪声。

**Irreducible Error（不可约误差）**：$\\sigma^2$，也称为 **Bayes Error（贝叶斯误差）**，这是数据本身的噪声，任何模型都无法消除。

### Derivation（推导过程）

完整的推导过程帮助深入理解各项的来源：

$$E_D[(y - \\hat{{f}})^2] = E_D[(f + \\epsilon - \\hat{{f}})^2]$$

$$= E_D[(f - \\hat{{f}})^2] + 2E_D[(f - \\hat{{f}})\\epsilon] + E_D[\\epsilon^2]$$

由于 $\\epsilon$ 与 $\\hat{{f}}$ 独立且 $E[\\epsilon] = 0$，中间项为零：

$$= E_D[(f - \\hat{{f}})^2] + \\sigma^2$$

对第一项加减 $E_D[\\hat{{f}}]$：

$$E_D[(f - \\hat{{f}})^2] = (f - E_D[\\hat{{f}}])^2 + E_D[(\\hat{{f}} - E_D[\\hat{{f}}])^2]$$

$$= \\text{{Bias}}^2 + \\text{{Variance}}$$

### Model Complexity Spectrum（模型复杂度谱）

| 复杂度 | 偏差 | 方差 | 示例模型 | 典型表现 |
|--------|------|------|---------|---------|
| 低 | 高 | 低 | **Linear Regression（线性回归）**, **Naive Bayes（朴素贝叶斯）** | 训练误差和测试误差都较高但接近 |
| 中 | 中 | 中 | 小型神经网络、浅层树集成 | 训练/测试误差的较好平衡 |
| 高 | 低 | 高 | 深层决策树、$k=1$ 的 **KNN（K-Nearest Neighbors，K近邻）**、未剪枝神经网络 | 训练误差极低但测试误差高 |

### Diagnostic Curves: Error vs. Model Complexity（错误率-复杂度诊断曲线）

与上一节按训练集大小绘制学习曲线不同，下面这张 **"复杂度-误差"** 曲线是面试中更常被要求徒手画出的图。横轴是模型容量（如多项式阶数、树深度、隐藏单元数、$1/\\lambda$），纵轴是误差。随着容量从低到高：

- 训练误差单调下降到 0（过参数化时可完美记忆训练集）
- 验证误差呈 **U 形**：先下降（偏差消退）后上升（方差爆发）
- 两曲线之间的 **gap** 就是方差；两曲线的 **共同 floor** 就是（偏差² + 噪声）

```
误差
 |              验证/测试误差
 |  ╲                        ╱
 |   ╲                      ╱
 |    ╲___________________╱          <-- U 形最低点 = 最优复杂度
 |           ╲___          ╱
 |               ╲_______╱
 |                     ╱
 |              训练误差（单调下降到 0）
 +--------------------------------------> 模型复杂度
   低偏差不足区          最优          高方差区
```

读图 SOP：
1. 先看两条线在右端的 **gap** —— gap 大 = 高方差问题；gap 小而两条线都高 = 高偏差问题。
2. 定位验证误差的 **U 底部** —— 这是最佳复杂度点；左边欠拟合，右边过拟合。
3. 若右端看到 **Double Descent（双重下降）** 的二次下降（见下文），说明已进入插值区间，需要额外论证（SGD 隐式正则化、flat minima 等）。

### Regularization as Bias-Variance Control（正则化作为偏差-方差控制）

正则化通过增加偏差来减少方差：

$$\\mathcal{{L}}_{{\\text{{reg}}}} = \\mathcal{{L}}_{{\\text{{data}}}} + \\lambda \\cdot R(w)$$

- **L2 (Ridge，岭回归)**：$R(w) = \\|w\\|_2^2$ —— 缩小所有系数，保留所有特征
- **L1 (Lasso，套索回归)**：$R(w) = \\|w\\|_1$ —— 将系数驱动为零，实现特征选择
- **Elastic Net（弹性网络）**：$R(w) = \\alpha\\|w\\|_1 + (1-\\alpha)\\|w\\|_2^2$ —— 两者折中

参数 $\\lambda$ 的作用：
- $\\lambda = 0$：无正则化，模型最大程度拟合数据（低偏差、高方差）
- $\\lambda \\to \\infty$：所有参数趋近于零，模型退化为常数（高偏差、低方差）
- 最优的 $\\lambda$ 在两者之间，通过交叉验证选择

### Ensemble Methods and Bias-Variance（集成方法与偏差-方差）

集成方法可以从偏差-方差的角度精确理解：

**Bagging（Bootstrap Aggregating，自助聚合）**——减少方差：
- 通过对多个独立模型的预测取平均来减少方差
- 对于 $B$ 个相关系数为 $\\rho$ 的模型：$\\text{{Var}}_{{avg}} = \\rho\\sigma^2 + \\frac{{1-\\rho}}{{B}}\\sigma^2$
- **Random Forest（随机森林）** 通过特征随机采样进一步降低 $\\rho$，从而更有效地减少方差
- 偏差几乎不变（每个基模型仍是完整的树）

**Boosting（提升法）**——减少偏差：
- 每一步都在拟合前一步的残差，逐步修正偏差
- **GBDT（Gradient Boosted Decision Trees，梯度提升决策树）** 用浅树作为弱学习器
- 过度boosting会增加方差（过拟合），需要通过学习率和早停来控制
- **XGBoost（eXtreme Gradient Boosting，极端梯度提升）** 通过正则化项同时控制方差

**Stacking（堆叠）**——减少偏差和方差：
- 用一个元学习器组合多个基学习器的预测
- 元学习器学习每个基学习器在不同区域的可靠性

### Double Descent（双重下降现象）

现代深度学习挑战了经典的U形偏差-方差曲线。在 **Interpolation Regime（插值区间）** ($d \\gg n$，参数远多于样本)，测试误差在插值阈值之后可以再次下降：

1. **Classical Regime（经典区间）**：增加参数使方差增加，测试误差呈U形
2. **Interpolation Threshold（插值阈值）**：模型刚好能完美拟合训练数据，测试误差达到峰值
3. **Over-parameterized Regime（过参数化区间）**：继续增加参数，**Implicit Regularization（隐式正则化）** 通过 **SGD（Stochastic Gradient Descent，随机梯度下降）** 的噪声和最小范数解特性减少有效复杂度

**双重下降的关键理解**：
- 它不仅在参数数量维度上出现，还在训练时间和数据量维度上出现
- **Epoch-wise Double Descent（训练轮次双重下降）**：训练足够长时间后，测试误差可能再次下降
- 现代的理解是：SGD在过参数化模型中倾向于找到 **Flat Minima（平坦极小值）**，这些解具有更好的泛化性能

### Bias-Variance for Different Models（不同模型的偏差-方差特性）

| 模型 | 偏差 | 方差 | 调控手段 |
|------|------|------|---------|
| 线性回归 | 高 | 低 | 增加多项式特征降偏差 |
| KNN ($k$小) | 低 | 高 | 增大 $k$ 降方差 |
| KNN ($k$大) | 高 | 低 | 减小 $k$ 降偏差 |
| 决策树（未剪枝） | 低 | 高 | 剪枝/限制深度降方差 |
| Random Forest | 低 | 中 | 增加树的数量进一步降方差 |
| GBDT | 中 | 中 | 调节学习率和迭代次数 |
| 深度神经网络 | 低 | 高 | Dropout/正则化/早停降方差 |

## Remedies Matrix（补救措施矩阵）

面试现场拿到"模型表现不好"的提问时，**先定位是偏差问题还是方差问题，再从下表按列选择措施**。这张表把所有常见补救措施按"降偏差 / 降方差 / 两者兼修"三类对齐。

| 类别 | 措施 | 机制 | 注意 |
|------|------|------|------|
| **降偏差** | 增加模型容量（更深网络、更高多项式阶、更大树深） | 扩大假设类 | 方差会上升，需要配合正则化或数据增强 |
| **降偏差** | 减少正则化（降低 $\\lambda$、减小 weight decay） | 放松系数约束 | 过拟合风险升高 |
| **降偏差** | 添加更有信息量的特征（特征工程） | 给模型新的信号 | 相关性要和目标强相关而非冗余 |
| **降偏差** | 切换更强的模型族（线性 → 树 → 神经网络） | 跳出当前 hypothesis class 限制 | 训练/推理成本上升 |
| **降方差** | 增加训练数据（含合成/增强） | 减小估计的抖动 | 对高偏差问题几乎无效 |
| **降方差** | 增强正则化（L1/L2、Dropout、early stopping、max_depth） | 注入偏差换取稳定性 | 过强会滑向欠拟合 |
| **降方差** | 集成：Bagging / Random Forest | 平均独立模型，方差 $\\rho\\sigma^2 + (1-\\rho)\\sigma^2/B$ | 只降方差，不降偏差 |
| **降方差** | 减小模型复杂度（剪枝、限制层数/单元数） | 缩小假设类 | 偏差会上升 |
| **两者兼修** | 交叉验证调超参 | 在 U 形曲线上精确定位最优复杂度 | 是面试首选答案 |
| **两者兼修** | Boosting + 学习率 + early stopping | 偏差由序列拟合残差消减，方差由学习率 + 早停压制 | XGBoost/LightGBM 的典型打法 |
| **两者兼修** | 迁移学习 / 预训练 | 用外部数据提供偏差先验，微调降剩余方差 | 需和目标任务分布兼容 |

## Implementation

```python
import numpy as np
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

def plot_learning_curve(estimator, X, y, cv=5):
    \"\"\"绘制学习曲线，诊断偏差-方差问题\"\"\"
    train_sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, cv=cv,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring="neg_mean_squared_error"
    )
    train_mean = -train_scores.mean(axis=1)
    val_mean = -val_scores.mean(axis=1)

    plt.plot(train_sizes, train_mean, label="Training Error")
    plt.plot(train_sizes, val_mean, label="Validation Error")
    plt.xlabel("Training Set Size")
    plt.ylabel("MSE")
    plt.legend()
    plt.title("Learning Curve")

# 偏差-方差的蒙特卡洛估计
def estimate_bias_variance(model_class, X, y, n_bootstrap=200):
    predictions = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(X), len(X), replace=True)
        model = model_class()
        model.fit(X[idx], y[idx])
        predictions.append(model.predict(X))
    predictions = np.array(predictions)
    bias_sq = (predictions.mean(axis=0) - y) ** 2
    variance = predictions.var(axis=0)
    return bias_sq.mean(), variance.mean()
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| 诊断欠拟合/过拟合 | "模型表现差" | 训练误差高=欠拟合；训练-验证gap大=过拟合 |
| 集成方法动机 | "为什么用Random Forest？" | Bagging减方差；Boosting减偏差 |
| 正则化选择 | "Ridge vs. Lasso?" | Lasso做特征选择；Ridge在所有特征都重要时用 |
| 学习曲线分析 | "如何改进模型？" | 更多数据帮助高方差；增加模型容量帮助高偏差 |
| $k$ 的选择 | KNN面试 | $k=1$ 零训练误差但高方差；$k=n$ 高偏差 |

### Common Interview Questions

- **推导MSE的偏差-方差分解？** 关键步骤：加减 $E[\\hat{{f}}]$，利用噪声 $\\epsilon$ 的独立性消除交叉项
- **Bagging和Boosting如何分别处理偏差和方差？** Bagging通过平均多个高方差模型降低方差（但不降偏差）；Boosting逐步拟合残差降低偏差（但可能增加方差）
- **$k$-NN 中 $k=1$ 为何训练误差为零但方差高？** 训练时每个点的最近邻就是它自己，故零误差；但预测对训练集的微小变化极度敏感
- **解释双重下降现象？** 过参数化模型通过SGD的隐式正则化找到低范数解，泛化性能反而改善
- **Dropout如何在神经网络中起正则化作用？** 等价于训练 $2^n$ 个瘦网络的集成，预测时取平均（权重缩放），降低方差

## Interview Pitfalls（常见误区）

下面这些说法在面试中频繁出现，其中多数是 **错的或不完整的**。知道这些坑比知道标准答案更能显示深度。

- **"加数据总能改善模型"** —— 只对 **高方差** 有效。纯偏差问题加多少数据都救不了，必须先扩容模型或换模型族。
- **"正则化 = 降偏差"** —— 恰恰相反。正则化 **注入** 偏差以换取方差降低（$\\lambda \\uparrow$ ⇒ bias $\\uparrow$, variance $\\downarrow$）。
- **"Bagging 能降低偏差"** —— 不能。平均 $B$ 个独立估计量只压方差，期望不变；Random Forest 之所以强是因为降低了相关系数 $\\rho$，不是降了偏差。
- **"Boosting 不会过拟合"** —— 会。GBDT/XGBoost 增加轮数或深度后方差会爆。学习率、早停、max_depth、subsample 都是必备的方差控制。
- **"训练误差 = 0 说明模型好"** —— 红灯。训练误差等于 0 常伴随巨大的 train-val gap；要看验证误差和 U 形图的右端。
- **"Double Descent 意味着偏差-方差权衡被推翻"** —— 不准确。经典权衡仍在欠参数化区间成立；插值区间是 SGD 隐式正则化在平坦极小值处生效，是一种 **新的**、而非"推翻的"机制。
- **"偏差平方和方差单位不同，不能放同一个式子里"** —— 数学上它们同是 $\\text{{MSE}}$ 的分量（均方），单位一致（$y$ 的平方）。
- **"高偏差时早停能救"** —— 早停属于降方差工具；高偏差下早停只会让模型欠拟合得更彻底。

## Components（复合概念组成）

本节列出 Bias-Variance 作为 canonical hub 所统摄的相关节点与 drill 文档，便于跨 pillar 导航：

- [Bias-Variance & L1/L2 Geometric View (pillar2.regularization.bias_variance_geometric)](/framework/195) —— L1/L2 几何视角下的方差控制证明。
- [Expectation & Variance (pillar7.probability_statistics.expectation_variance)](/framework/167) —— 前置概率论基础，推导过程的数学地基。
- [Google Bias-Variance + Overfitting Diagnosis Drill](/companies/google/documents/{DRILL_DOC_ID}) —— Google R1 面试口述演练 drill，复习专用（不再重复推导，见上文 Derivation 节）。

## Key Takeaways

- 偏差 = 欠拟合，方差 = 过拟合；总误差 = 偏差² + 方差 + 不可约噪声
- 增加模型复杂度：偏差降低，方差增加（经典观点）
- 正则化注入偏差以控制方差——$\\lambda$ 是调节旋钮
- Bagging（Random Forest）减方差；Boosting（XGBoost）减偏差
- 现代深度学习：双重下降意味着在插值阈值之后，更多参数反而可以帮助泛化
- 学习曲线（训练集大小轴）与 U 形复杂度曲线（复杂度轴）合在一起才是完整的诊断工具箱
- 面试核心：能够根据训练/验证误差的模式判断是偏差还是方差问题，并用 Remedies Matrix 按类选对措施

> **后续** [Regularization (L1/L2/ElasticNet)](/framework/195)
> **后续** [Model Selection & Cross-Validation](/framework/68)
"""


def _rstrip_trailing_blanks(s: str) -> str:
    return s.rstrip() + "\n"


NODE_67_DESCRIPTION = _rstrip_trailing_blanks(NODE_67_DESCRIPTION)


DOC_56_CONTENT = f"""<!-- Generated by StudyNoteBuilder -->
<!-- doc_kind: drill -->
{SENTINEL}

# Bias-Variance + Overfitting Diagnosis Drill -- Google R1 Prep

{CANONICAL_POINTER}

Tactical oral-exam companion. Full derivation, regularization theory, and
double-descent treatment live on the canonical hub above; this file keeps only
the Google R1 drill surface: diagnosis cheat sheet, ensemble variance
formulas, learning-curve shapes, and oral shortcuts.

## 1. Diagnosis Label Cheat Sheet

The complexity-error relationship drives all diagnosis (derivation lives on the
canonical hub; the one-line consequence is what you recite):

> Model complexity up  =>  Bias down, Variance up.

**4-Quadrant Diagnosis Table**

| Symptom | Diagnosis | Fix |
| --- | --- | --- |
| High train error, high test error | Underfitting (high bias) | More features, more complex model, less regularization |
| Low train error, high test error | Overfitting (high variance) | More data, regularization, simpler model, dropout, early stopping |
| Low train error, low test error | Good fit | Ship it |
| High train error, low test error | Data leakage or evaluation bug | Audit pipeline, check for target leakage |

Oral shortcut: 'Underfit = both errors high = bias dominates. Overfit = gap
between train and test = variance dominates. Leakage = test better than train
= something is wrong.'

## 2. Bagging Variance Formula + RF Insight

Average of B models with pairwise correlation rho:

$$\\text{{Var}}_{{\\text{{bag}}}} = \\rho\\,\\sigma_{{\\text{{tree}}}}^2 + \\frac{{1-\\rho}}{{B}}\\,\\sigma_{{\\text{{tree}}}}^2 \\;\\xrightarrow{{B \\to \\infty}}\\; \\rho\\,\\sigma_{{\\text{{tree}}}}^2$$

Bagging hits a floor at $\\rho\\sigma^2$. Random Forest lowers $\\rho$ via random
feature subsets at each split (typically $m = \\sqrt{{p}}$ for classification,
$m = p/3$ for regression) -- lower $\\rho$ means lower floor.

Oral shortcut: 'Bagging floor = rho times sigma-squared. RF lowers rho via
random features. Lower rho = better ensemble.'

## 3. RF Deep Trees vs GBDT Shallow Trees (Dual Aesthetics)

RF and GBDT attack the bias-variance tradeoff from opposite ends:

|  | Random Forest | GBDT |
| --- | --- | --- |
| Base learner | Deep, unpruned trees (low bias, high variance) | Shallow trees / stumps (high bias, low variance) |
| Ensemble strategy | Parallel (bagging) -- reduces variance | Sequential (boosting) -- reduces bias |
| Overfitting risk | Rarely overfits by adding more trees | Can overfit if too many rounds or too deep |
| Key hyperparams | n_estimators, max_features | n_estimators, learning_rate, max_depth |
| Bias-variance lever | Random feature subsets lower rho (variance) | Each tree fits residual (bias reduction) |

RF: $f(x) = \\frac{{1}}{{B}}\\sum_{{b=1}}^{{B}} T_b(x)$ (average of deep trees)

GBDT: $f(x) = \\sum_{{m=1}}^{{M}} \\eta\\,h_m(x)$ (sum of shallow trees on residuals)

Oral shortcut: 'RF = deep trees averaged to kill variance. GBDT = shallow trees
stacked to kill bias. Opposite entry points, same destination.'

## 4. Learning Curve -- Four Diagnostic Shapes

Plot train error and validation error vs training set size. The shape diagnoses
the problem:

| Shape | Train | Val | Diagnosis | Action |
| --- | --- | --- | --- | --- |
| Large gap, both converging | Low | High but decreasing | High variance (overfit) | More data will help; or regularize |
| Small gap, both high | High | High, close to train | High bias (underfit) | More data will NOT help; need more capacity |
| Gap closes, both low | Low | Low, converging to train | Good fit | Optimal complexity; diminishing returns |
| Train near zero, val flat high | Near 0 | High, flat | Severe overfit / memorization | Regularize or simpler model, not more data |

Rules of thumb:
- Big train-val gap => variance problem. Add data or regularize.
- Both curves plateau high => bias problem. Add features or capacity.
- Train error = 0 => memorization red flag. Regularize.
- Convergence level approximates irreducible error under the current model class.

Oral shortcut: 'Big gap = variance, add data. Both high = bias, add capacity.
Train zero + val high = memorizing, regularize.'

## 5. 2-Minute Oral Self-Check

- [ ] Write $E_D[(y - \\hat{{f}})^2] = \\text{{Bias}}^2 + \\text{{Var}} + \\sigma^2$ from memory
- [ ] Name all three terms and what each means in one sentence
- [ ] Complexity up => bias down, variance up (say it)
- [ ] Underfit = both errors high; overfit = gap between train and test
- [ ] Bagging variance = $\\rho\\sigma^2 + (1-\\rho)\\sigma^2/B$, floor at $\\rho\\sigma^2$
- [ ] RF lowers rho by randomizing features; GBDT reduces bias sequentially
- [ ] RF = deep trees averaged; GBDT = shallow trees stacked
- [ ] Learning curve: big gap = variance; both high = bias; train=0 = memorizing
"""

DOC_56_CONTENT = _rstrip_trailing_blanks(DOC_56_CONTENT)


def _ensure_schema() -> None:
    """Run the drill-relation migration; fail loudly if it errors."""
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


def _patch_node_67(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE id=?",
        (CANONICAL_NODE_ID,),
    ).fetchone()
    if row is None:
        return "missing"
    if (row[0] or "") == NODE_67_DESCRIPTION:
        return "unchanged"
    conn.execute(
        "UPDATE framework_nodes SET description=? WHERE id=?",
        (NODE_67_DESCRIPTION, CANONICAL_NODE_ID),
    )
    return "patched"


def _patch_doc_56(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT content, doc_kind FROM company_documents WHERE id=?",
        (DRILL_DOC_ID,),
    ).fetchone()
    if row is None:
        return "missing"
    if (row[0] or "") == DOC_56_CONTENT and row[1] == "drill":
        return "unchanged"
    conn.execute(
        "UPDATE company_documents SET content=?, doc_kind='drill' WHERE id=?",
        (DOC_56_CONTENT, DRILL_DOC_ID),
    )
    return "patched"


def _insert_concept_links(conn: sqlite3.Connection) -> tuple[int, int]:
    """Insert the two concept_links rows idempotently. Returns (inserted, skipped)."""
    pairs = [
        ("company_document", DRILL_DOC_ID, "framework_node", CANONICAL_NODE_ID,
         "canonical", "Google R1 drill defers to canonical hub (KG-P2-01)"),
        ("framework_node", CANONICAL_NODE_ID, "company_document", DRILL_DOC_ID,
         "drill", "Google R1 prep drill companion (KG-P2-01)"),
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
        node_status = _patch_node_67(conn)
        doc_status = _patch_doc_56(conn)
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
        if not (8000 <= node_len <= 12000):
            problems.append(
                f"node 67 length {node_len} outside target [8000, 12000]"
            )
        if doc_len > 5000:
            problems.append(f"doc 56 length {doc_len} exceeds 5000 cap")

        if problems:
            conn.rollback()
        else:
            conn.commit()
    finally:
        conn.close()

    tag = {"patched": "[PATCHED]", "unchanged": "[UNCHANGED]",
           "missing": "[MISSING]"}
    print(f"{tag[node_status]} framework_node {CANONICAL_NODE_ID} "
          f"(Bias-Variance Tradeoff), length={node_len}")
    print(f"{tag[doc_status]} company_document {DRILL_DOC_ID} "
          f"(Google R1 drill), length={doc_len}")
    print(f"[LINKS] inserted={inserted} skipped={skipped}")

    if problems:
        print("[FAIL] invariants violated (transaction rolled back):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("[DONE] KG-P2-01 Bias-Variance canonical hub consolidation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
