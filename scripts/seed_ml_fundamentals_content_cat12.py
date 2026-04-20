"""Seed: T-P0-539 -- ML Fundamentals T1 content fill, Cat 1-2 (7 leaves).

Replaces the placeholder TODO[MLF-<slug>] descriptions inserted by
seed_ml_fundamentals_skeleton.py (T-P0-538) with cleaned, KaTeX-rendered
markdown for the seven highest-frequency Tier-1 questions:

  classical_ml (5):
    - bias-variance-tradeoff           (#1)
    - l1-vs-l2-regularization          (#2)  (with OLS / ellipse deep-dive)
    - logistic-regression-loss         (#3)
    - gbdt-vs-rf-xgboost               (#4)
    - cross-entropy-kl-divergence      (#14, source-numbered #14, lives here)

  eval_data (2):
    - class-imbalance-handling         (#5)
    - auc-vs-pr-curve                  (#6)

T1 = verbatim cleanup. The source attachment renders every formula three
times (LaTeX + glyph dump + glyph dump). This script collapses each triplet
to a single KaTeX block in $...$ / $$...$$ form, expands first-occurrence
acronyms per data/ml_fundamentals_inventory.yaml's acronyms_to_expand list
(format: **English full term** (acronym, 中文译名)), and preserves every
derivation and "追问预判" section.

Idempotency:
  - Each leaf has a stable expected description; second run yields
    updated=0 skipped=7 conflict=0.
  - SHA-256 of the 7 description blobs captured pre/post for audit.
  - If a leaf's existing description is neither the placeholder nor the
    new content (i.e. a human-edited intermediate state), the script
    aborts with [CONFLICT] before any write.

Acceptance:
  - 7 framework_nodes.description rows updated (path LIKE
    'ml-fundamentals/<cat>/<slug>')
  - Each description has KaTeX math ($ or $$ delimiters)
  - Each description has section headers (## ...)
  - Re-run is no-op (updated=0)
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"


# ---------------------------------------------------------------------------
# Cleaned descriptions. Raw strings to keep LaTeX backslashes literal.
# ---------------------------------------------------------------------------

DESC_BIAS_VARIANCE = r"""# Bias-Variance Tradeoff

## 1. 设定（关键！先说清楚"期望"是对谁取的）

真实数据生成过程：

$$y = f(x) + \epsilon, \quad E[\epsilon] = 0, \ \text{Var}(\epsilon) = \sigma^2$$

我们从分布中采样一个 **Independent and Identically Distributed** (IID, 独立同分布) 训练集 $D$，学出一个预测器 $\hat{f}_D$。对一个固定的测试点 $x$，期望误差取在两个随机源上：训练集 $D$ 和测试噪声 $\epsilon$。

记 $\bar{f}(x) = E_D[\hat{f}_D(x)]$，即"无数次重采训练集、取预测平均"。

## 2. 推导（加减 $\bar{f}$ 这一招是核心）

$$E_{D,\epsilon}\big[(y - \hat{f}_D(x))^2\big] = E_{D,\epsilon}\big[(f(x) + \epsilon - \hat{f}_D(x))^2\big]$$

加减 $\bar{f}(x)$ 做恒等变形：

$$= E_{D,\epsilon}\big[\big((f - \bar{f}) + (\bar{f} - \hat{f}_D) + \epsilon\big)^2\big]$$

展开后三个交叉项都为 0（因为 $E_D[\bar{f} - \hat{f}_D] = 0$，$E[\epsilon] = 0$ 且 $\epsilon \perp D$），只剩三个平方项：

$$\boxed{\ E[(y - \hat{f})^2] = \underbrace{(f(x) - \bar{f}(x))^2}_{\text{Bias}^2} + \underbrace{E_D[(\hat{f}_D(x) - \bar{f}(x))^2]}_{\text{Variance}} + \underbrace{\sigma^2}_{\text{Irreducible}}\ }$$

这条分解式在 **Mean Squared Error** (MSE, 均方误差) 损失下成立。

## 3. 三项的物理意义

- **Bias²**：模型族表达能力不够 → 平均预测偏离真值（欠拟合）。
- **Variance**：同一族模型对训练集扰动敏感 → 不同 $D$ 学出来的 $\hat{f}$ 抖得厉害（过拟合）。
- $\sigma^2$：数据本身的随机性，任何模型都消不掉的下界。

## 4. "Tradeoff" 要加限定词

经典 U 型曲线说的是：在固定数据量下、沿模型容量这一个轴移动时，bias↓ 往往伴随 variance↑。但这不是定理：

- 加更多训练数据可以单纯降 variance，bias 不动。
- 正则化、ensembling（bagging 降 variance、boosting 降 bias）可以"作弊"。
- **Double descent**：过参数化区域 variance 反而再次下降，打破 U 型。

所以更准确的说法是："在经典欠参数化区域，沿容量轴存在 bias-variance 权衡"，而不是"降 bias 必然升 variance"。
"""


DESC_L1_L2 = r"""# L1 vs L2 Regularization

## 1. 公式与目标函数

$$L_{\text{L1}}(w) = \mathcal{L}(w) + \lambda \|w\|_1 = \mathcal{L}(w) + \lambda \sum_i |w_i|$$

$$L_{\text{L2}}(w) = \mathcal{L}(w) + \lambda \|w\|_2^2 = \mathcal{L}(w) + \lambda \sum_i w_i^2$$

两者都可以写成等价的 constrained 形式（Lagrange duality）：在 $\|w\|_1 \le t$ 或 $\|w\|_2^2 \le t$ 下最小化 $\mathcal{L}(w)$。

## 2. 次梯度视角（为什么 L1 能"踩到 0"）

对单个维度 $w_i$ 求偏导，平衡条件是 $\partial \mathcal{L}/\partial w_i + \lambda \cdot \partial |w_i|/\partial w_i = 0$。

- **L2**：罚项导数是 $2\lambda w_i$，当 $w_i \to 0$ 时罚项的"推力"也 $\to 0$。只要数据给一点点梯度，$w_i$ 就会被"推开"一小步，永远不会恰好停在 0。结果是 shrinkage。
- **L1**：罚项在 $w_i \ne 0$ 时导数恒为 $\pm \lambda$（力度不衰减）；在 $w_i = 0$ 点不可导，次梯度是整个区间 $[-\lambda, +\lambda]$。**Karush-Kuhn-Tucker** (KKT, 一阶最优性条件) 稳定条件是：

$$w_i = 0 \text{ 稳定} \iff \left|\frac{\partial \mathcal{L}}{\partial w_i}\right|_{w_i = 0} \le \lambda$$

也就是只要数据梯度比罚项小，次梯度区间就能"吸收"它，$w_i = 0$ 是真正的最优点。这正是 soft-thresholding：

$$\hat{w}_i = \text{sign}(z_i) \cdot \max(|z_i| - \lambda, 0)$$

## 3. 几何视角

把问题看成 constrained form：loss 的等高线是椭圆，约束域是 $\|w\|_1 \le t$（菱形）或 $\|w\|_2^2 \le t$（圆）。最优解在椭圆第一次触碰约束域的地方。

- 菱形有尖角、尖角恰好在坐标轴上。从任意方向扩张的椭圆，首次接触菱形时大概率撞在角上 → 某个 $w_i = 0$。
- 圆是光滑的，触碰点几乎不会恰好落在轴上 → 所有 $w_i$ 都被压小但非零。

高维时 L1 的尖点更"尖"：$\ell_1$-ball 在 $d$ 维有 $2^d$ 个 vertex（每个 vertex 都有 $d - 1$ 个坐标为 0），sparse solution 的"靶心"非常大。

## 4. 其他对比点

| 维度 | L1 (Lasso) | L2 (Ridge) |
|-----|-----------|-----------|
| 解 | 稀疏 | 稠密、shrink |
| Correlated features | 随机挑一个，不稳定 | 均摊 |
| 闭式解 | 无（coordinate descent / ISTA / LARS） | 有 $(X^\top X + \lambda I)^{-1} X^\top y$ |
| Bayesian 先验 | Laplace | Gaussian |

Bayesian 先验视角对应 **Maximum a Posteriori** (MAP, 最大后验) 估计：把正则化项看成对 $w$ 的对数先验，与无正则化的 **Maximum Likelihood Estimation** (MLE, 最大似然估计) 之差就是这个先验项。Laplace 先验下 MAP = L1，Gaussian 先验下 MAP = L2。

## 5. 可能追问：Elastic Net

$$\lambda_1 \|w\|_1 + \lambda_2 \|w\|_2^2$$

L1 带来稀疏性，L2 让 correlated features 一起被选进来或一起退出（grouping effect）、解更稳定。

## 深挖：OLS 与椭圆等高线

### 1. 什么是 OLS？

OLS = Ordinary Least Squares（普通最小二乘）。就是没有任何正则化时，线性回归的"裸"优化问题：

$$\hat{w}_{\text{OLS}} = \arg\min_w \|y - Xw\|_2^2 = \arg\min_w \sum_{n=1}^{N}(y_n - x_n^\top w)^2$$

对 $w$ 求导 = 0，得到闭式解（normal equation）：

$$\hat{w}_{\text{OLS}} = (X^\top X)^{-1} X^\top y$$

加上 L1 / L2 正则化，相当于"从这个 OLS 最优点出发，被约束域往原点拽回来"。

### 2. 为什么等高线是椭圆？

把 loss 展开（记 $A = X^\top X$，$b = X^\top y$）：

$$\mathcal{L}(w) = \|y - Xw\|^2 = w^\top A w - 2 b^\top w + \|y\|^2$$

这是一个关于 $w$ 的二次型 (quadratic form)。在 $\hat{w}_{\text{OLS}}$ 附近做一次恒等变形（配方）：

$$\mathcal{L}(w) = (w - \hat{w}_{\text{OLS}})^\top A (w - \hat{w}_{\text{OLS}}) + \text{const}$$

所以等高线集合 $\{w : \mathcal{L}(w) = c\}$ 就是：

$$(w - \hat{w}_{\text{OLS}})^\top A (w - \hat{w}_{\text{OLS}}) = c'$$

这正是椭圆的定义式（$A$ 半正定 → 椭球 / 椭圆）。

几何含义（为什么是椭圆而不是圆）：

- 椭圆中心 = $\hat{w}_{\text{OLS}}$（loss 的最低点）。
- 椭圆轴方向 = $A = X^\top X$ 的特征向量。
- 椭圆轴长 $\propto 1 / \sqrt{\lambda_i}$（$\lambda_i$ 是 $A$ 的特征值）。

大特征值方向 → 椭圆窄（loss 对这个方向敏感，离开一点点 loss 就暴涨）；小特征值方向 → 椭圆胖（loss 平坦，走很远 loss 都不怎么变）。

### 3. 为什么这对正则化解读很重要

椭圆扁不扁 = feature 之间相关性强不强：

- features 互相正交（$X^\top X$ 接近对角）→ 椭圆接近圆 → L1 和 L2 的差别没那么明显。
- features 高度相关（$X^\top X$ 病态，有非常小的特征值）→ 椭圆又扁又长 → 沿"扁"方向走很远 loss 几乎不变，正则化可以在这个方向大刀阔斧地压。

这也正是 L1 在 correlated features 上"随便挑一个"的几何原因：椭圆长轴几乎平行于某条对角线，它和菱形的接触点对微小扰动非常敏感，稍微动一下就从一个角跳到另一个角。

所以 L2 解是"沿椭圆主轴 shrink"，L1 解是"撞到 $\ell_1$-ball 某个 vertex"，本质都是椭圆 vs 约束域的接触几何。
"""


DESC_LOGISTIC = r"""# Logistic Regression Loss

## 1. 模型假设

建模 $y \in \{0, 1\}$，假设：

$$P(y = 1 \mid x) = \sigma(w^\top x) = \frac{1}{1 + e^{-w^\top x}}, \quad P(y = 0 \mid x) = 1 - \sigma(w^\top x)$$

记 $p = \sigma(w^\top x)$，$z = w^\top x$（logit）。$\sigma$ 的由来：对 log-odds 做线性建模 $\log \frac{p}{1 - p} = w^\top x$，反解就是 sigmoid。

## 2. 从 MLE 推导 loss

单样本服从 Bernoulli：

$$P(y \mid x) = p^y (1 - p)^{1 - y}$$

取负对数似然 **Negative Log-Likelihood** (NLL, 负对数似然) 作为 loss——这等价于做 **Maximum Likelihood Estimation** (MLE, 最大似然估计)：

$$\ell(w) = -y \log p - (1 - y) \log(1 - p)$$

这就是 **Binary Cross-Entropy** (BCE, 二分类交叉熵)，也是 **Cross-Entropy** (CE, 交叉熵) 在二分类下的形式。在整个训练集上：

$$\mathcal{L}(w) = -\sum_{n=1}^{N} \Big[y_n \log \sigma(w^\top x_n) + (1 - y_n) \log(1 - \sigma(w^\top x_n))\Big]$$

## 3. 梯度（sigmoid + CE 的"漂亮消去"）

关键恒等式：$\sigma'(z) = \sigma(z)(1 - \sigma(z)) = p(1 - p)$。

对单样本求梯度：

$$\frac{\partial \ell}{\partial w} = \underbrace{\left(-\frac{y}{p} + \frac{1 - y}{1 - p}\right)}_{\partial \ell / \partial p} \cdot \underbrace{p(1 - p)}_{\partial p / \partial z} \cdot \underbrace{x}_{\partial z / \partial w}$$

前两项展开后恰好 $= (p - y)$，所以：

$$\boxed{\ \nabla_w \ell = (\hat{y} - y)\, x\ }$$

非常干净——和线性回归 MSE 的梯度长得一模一样，但这里 $\hat{y} = \sigma(w^\top x)$。这条梯度直接喂给 **Stochastic Gradient Descent** (SGD, 随机梯度下降) 或其变体即可优化。

## 4. 为什么不用 MSE

三个理由，从强到弱：

### (a) 凸性

- **CE + sigmoid**：Hessian 半正定（多元函数的二阶偏导矩阵；如 positive definite 则函数凸，不存在 local minima），$\mathcal{L}$ 关于 $w$ 凸，局部最优 = 全局最优。
- **MSE + sigmoid**：$\ell = \tfrac{1}{2}(\sigma(z) - y)^2$ 关于 $w$ 非凸，会有多个局部最优。

### (b) 梯度消失

MSE + sigmoid 的梯度：

$$\nabla_w \ell_{\text{MSE}} = (\hat{y} - y) \cdot \sigma'(z) \cdot x = (\hat{y} - y) \cdot p(1 - p) \cdot x$$

当预测极度错误时（比如 $y = 1$ 但 $p \approx 0$，即 $z \ll 0$），$\sigma'(z) \to 0$ → 梯度 $\to 0$ → 错得越离谱学得越慢。CE 的 $\sigma'$ 被对数的导数消掉了，梯度 $= (\hat{y} - y)\, x$，错得越离谱 $|\hat{y} - y|$ 越接近 1，梯度饱满。

### (c) 概率解释 / 信息论解释

CE 是 MLE 在 Bernoulli 假设下的自然产物，也等价于最小化 $\text{KL}(p_{\text{data}} \| p_\theta)$。MSE 对应 Gaussian noise 假设，用在 $\{0, 1\}$ 二分类上属于模型误设（把离散 label 当连续量去拟合）。

## 5. 一个容易忽略的细节

"CE 比 MSE 好"只在输出层是 sigmoid / softmax 时成立——那个漂亮的梯度消去依赖于 sigmoid 和 log 的共轭关系。如果输出直接是 linear 层 + 回归任务，MSE 当然是对的选择。
"""


DESC_GBDT_RF_XGB = r"""# GBDT vs Random Forest + XGBoost Improvements

## 1. GBDT vs Random Forest：本质差别

两者都是 tree ensemble，但是集成方式完全不同：**Gradient Boosting Decision Tree** (GBDT, 梯度提升决策树) 走 boosting 路线，**Random Forest** (RF, 随机森林) 走 bagging 路线。

| 维度 | Random Forest | GBDT |
|-----|---------------|------|
| 集成范式 | Bagging（并行） | Boosting（串行） |
| 每棵树训练目标 | 独立训练，拟合原任务 | 拟合前序模型的残差 / 负梯度 |
| 单棵树形态 | 深、容量大（low bias, high var） | 浅、弱学习器（high bias, low var） |
| 主攻方向 | 降 variance | 降 bias |
| 预测方式 | 所有树投票 / 平均 | 所有树求和 $F_M(x) = \sum_m \eta \cdot h_m(x)$ |
| 过拟合特征 | 加更多树几乎不会过拟合 | 加更多树会过拟合 |
| 并行性 | 树间天然并行 | 串行（第 $m$ 棵依赖前 $m - 1$ 棵） |

RF 还有一个副产物 **Out-Of-Bag** (OOB, 袋外样本) 误差，可以做免费的泛化估计。

## 2. GBDT 的数学核心（Gradient Boosting）

把当前模型记作 $F_{m-1}(x)$，loss 是 $L(y, F(x))$。第 $m$ 棵树拟合的是负梯度（伪残差）：

$$r_{n,m} = -\left[\frac{\partial L(y_n, F(x_n))}{\partial F(x_n)}\right]_{F = F_{m-1}}$$

然后 $F_m(x) = F_{m-1}(x) + \eta \cdot h_m(x)$，$\eta$ 是 learning rate（shrinkage）。

- $L = \tfrac{1}{2}(y - F)^2$ 时 $r = y - F$，就是传统 residual fitting。
- $L$ 是 log-loss 时 $r = y - \sigma(F)$，可以做分类。

所以"fit bias"的准确说法：每一步都在沿 loss 的负梯度方向走一小步，用一棵树来近似这个方向。

## 3. **XGBoost** (XGBoost, 极致梯度提升) 相对传统 GBDT 的改进

### (a) 二阶 Taylor 展开

传统 GBDT 只用一阶梯度 $g_i$，XGBoost 同时用二阶 $h_i = \partial^2 L / \partial F^2$：

$$\mathcal{L}^{(m)} \approx \sum_i \left[g_i \cdot h_m(x_i) + \tfrac{1}{2} h_i \cdot h_m(x_i)^2\right] + \Omega(h_m)$$

好处：不用针对每种 loss 手动推导 residual，用二阶信息直接得到每个叶子的最优权重闭式解：

$$w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}$$

和最优 split 增益公式：

$$\text{Gain} = \tfrac{1}{2}\left[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda}\right] - \gamma$$

### (b) 结构正则化

$$\Omega(h) = \gamma T + \tfrac{1}{2}\lambda \|w\|_2^2$$

- $\gamma T$：惩罚叶子数（树复杂度）。
- $\lambda \|w\|^2$：惩罚叶子权重幅度。

传统 GBDT 只有预剪枝或深度限制，XGBoost 是把正则化直接写进目标函数。

### (c) Sparsity-aware split

对缺失值 / 稀疏特征，每个 split 学一个"默认方向"，缺失样本自动分到该方向。处理稀疏数据又快又好。

### (d) Approximate split (histogram)

不遍历所有候选点，而是按特征分位数分桶，只在桶边界找 split。大数据下加速巨大，也是 **LightGBM** (LightGBM, 轻量梯度提升机) 的核心思路。

### (e) 工程优化

- Column subsampling（学 RF 的）降方差 + 加速。
- Shrinkage / learning rate 已在传统 GBDT 里，但 XGBoost 把它作为默认。
- Cache-aware、block 存储、out-of-core 使其能处理内存装不下的数据。
- 并行化：虽然 boosting 本身串行，但单棵树内部找 split 是并行的（每个特征一个线程）。

## 4. 常见追问预判

- **Early stopping**：因为 boosting 会过拟合，通常用 validation set + early stopping 选迭代轮数。
- **LightGBM vs XGBoost**：LightGBM 用 leaf-wise growth（XGB 是 level-wise），GOSS 采样，叶子数比深度更关键，通常更快但更容易过拟合小数据。
- **CatBoost**：ordered boosting 解决 target leakage，对 categorical 原生支持。
- **为什么 GBDT 用浅树**：每棵只修一点点"偏差"，深树会 overshoot，反而让后续难以纠正。
"""


DESC_CLASS_IMBALANCE = r"""# Class Imbalance Handling

## 1. 先问三个问题（选方案的前提）

不平衡本身不是问题，关键看下游：

- **评估指标是什么？** Accuracy 会骗人，少数类关注的是 Precision / Recall / F1 / **Precision-Recall Curve** (PR, 精确率-召回率曲线) 的 PR-**Area Under Curve** (AUC, 曲线下面积) / Recall@K。
- **不平衡有多严重？** 1:10（mild）、1:100（severe）、1:10000（extreme）处理手段完全不同。
- **少数类是"真稀有"还是"采样偏差"？** 欺诈检测是真稀有；而标注偏差可能需要重新采数据而不是算法修补。

## 2. 四大类方法

### (a) Class weight（最便宜，首选起点）

在 loss 里给每个类一个权重：

$$L = -\sum_n w_{y_n} \log p_{y_n}, \quad w_c = \frac{N}{K \cdot N_c}$$

- 优点：零改动数据，一行代码（`class_weight='balanced'`）。
- 缺点：只是放大梯度，不创造新信息；类别极度不平衡时效果有限。
- 适用：mild 到 moderate（1:10 ~ 1:100），logistic regression / tree models / NN 都支持。

### (b) Resampling

**Oversampling 少数类**：

- 简单复制：容易过拟合到重复样本。
- **Synthetic Minority Over-sampling Technique** (SMOTE, 合成少数类过采样)：在 k 近邻之间线性插值生成合成样本。
- ADASYN：在 hard-to-learn 的区域生成更多。

**Undersampling 多数类**：

- 随机丢：丢掉信息。
- Tomek links / Edited NN：只丢边界附近"冗余"的多数类样本。
- EasyEnsemble / BalancedBagging：多次 undersample + ensemble，挽回丢失信息。

对比：

| 维度 | Over | Under |
|-----|------|-------|
| 训练集 | 变大 | 变小 |
| 风险 | 过拟合少数类 | 丢信息 |
| 适用 | 数据量不大 | 数据量充足 |

### (c) Focal Loss（Lin et al., 2017, RetinaNet）

$$FL(p_t) = -\alpha_t (1 - p_t)^\gamma \log(p_t)$$

- $\alpha_t$ 就是 class weight。
- $(1 - p_t)^\gamma$ 是 focusing term：当模型已经很确信（$p_t \to 1$），这个因子 $\to 0$，几乎不贡献梯度。
- 直觉：让 easy examples 闭嘴，让 hard examples 大声说话。
- 适用：目标检测（背景像素占 99%+）、极度不平衡、easy negatives 淹没 loss 的场景。$\gamma = 2$ 是常用默认。

### (d) 其他策略

- **Threshold moving**：模型不动，只调决策阈值。因为正常阈值 0.5 对应先验 0.5，不平衡时改成贴近 minority 先验，或按 F1 / PR 曲线选最优点。最被低估的手段。
- **One-class / anomaly detection**：1:10000+ 的极端情况，不要当分类问题做，用 Isolation Forest、One-Class SVM、Autoencoder 重构误差。
- **Ensemble**：BalancedRandomForest、EasyEnsemble 结合 bagging。
- **生成更多真实数据**：data augmentation（图像 / 文本）、主动学习标更多少数类样本——往往比算法 trick 更有效。

## 3. SMOTE 的坑（常见追问）

- **高维失效**：高维空间里近邻距离趋同，线性插值出来的点可能落在不属于任何类的流形之外（著名的 curse of dimensionality）。
- **在 boundary 附近插值 → 噪声**：少数类样本自己就在决策边界上，SMOTE 插出来的点更模糊边界。
- **对 categorical features 没定义**：需要 SMOTE-NC。
- **Leakage 隐患**：SMOTE 必须在 train / val split 之后对训练集做，否则验证集里会有"见过"的合成邻居。
- **改进**：Borderline-SMOTE（只在边界插值）、SMOTE-ENN（插完再用 ENN 清噪声）。

## 4. 实战 recipe

1. 先看指标：换成 PR-AUC / F1 / Recall@FPR，很多时候"不平衡问题"就不成问题。
2. threshold moving + class weight 两板斧先试，成本最低。
3. 不行再上 resampling（倾向 SMOTE + undersample 组合）。
4. NN 场景 focal loss + class weight 同时用。
5. 极端不平衡（1:10000+）考虑转化为 anomaly detection。
6. 任何合成数据都只在训练集上做，验证集 / 测试集保持真实分布。

## 5. 容易忽略的陷阱

- Resampling 改变了类先验，模型输出的概率标定 (calibration) 会失真，下游需要概率时要用 Platt scaling / isotonic regression 重新校准。
- Cross-validation 要用 stratified split，不然 fold 之间 minority 分布抖动很大。
- 在业务指标（如 recall@1% FPR）而不是 F1 上评估，更贴近真实部署。Recall@FPR 这类指标也是 **Receiver Operating Characteristic** (ROC, 接收者操作特征) 曲线上某个点的衍生量。
"""


DESC_AUC_PR = r"""# AUC vs PR Curve

## 1. 先理清 ROC 曲线本身

对每个阈值 $\tau$，把预测分数 $\ge \tau$ 的判为正类，算两个指标：

$$\text{TPR (Recall)} = \frac{TP}{TP + FN}, \quad \text{FPR} = \frac{FP}{FP + TN}$$

- **True Positive Rate** (TPR, 真正率)：又叫 Recall / 召回率。对应的 **True Negative Rate** (TNR, 真负率) $= TN / (TN + FP)$。
- **False Positive Rate** (FPR, 假正率) $= 1 - \text{TNR}$。

阈值从 $+\infty$ 扫到 $-\infty$，$(\text{FPR}, \text{TPR})$ 画出一条从 $(0, 0)$ 到 $(1, 1)$ 的曲线。这条曲线叫 **Receiver Operating Characteristic** (ROC, 接收者操作特征) 曲线。**Area Under Curve** (AUC, 曲线下面积) = ROC 下面积。

## 2. AUC 的物理意义（核心）

$$\text{AUC} = P(\hat{s}(x^+) > \hat{s}(x^-))$$

即：随机抽一个正样本和一个负样本，模型给正样本打的分比负样本高的概率。

这等价于 Mann-Whitney U 统计量（也叫 Wilcoxon rank-sum），也就是 AUC 是一个排序质量指标——它完全不看你的概率校准，只看正负样本的相对排序。

几个直接推论：

- AUC = 0.5：随机猜。
- AUC = 1.0：所有正样本分数都高于所有负样本。
- AUC = 0：完全反向（把符号翻转就是完美分类器）。
- AUC 对单调变换不敏感：$\sigma(z)$、$z$、$e^z$ 的 AUC 完全相同。

不适合 AUC 的信号：

- 你关心的是绝对概率（如风控要校准过的违约概率）而非排序。
- 你关心的是某个特定 operating point 的性能（AUC 是对全阈值的平均）。

## 3. 为什么不平衡时 PR 比 ROC 更合适

关键在分母里有没有 TN：

| 曲线 | 横轴 | 纵轴 |
|-----|------|------|
| ROC | $\text{FPR} = \frac{FP}{FP + TN}$ | $\text{TPR} = \frac{TP}{TP + FN}$ |
| **Precision-Recall Curve** (PR, 精确率-召回率曲线) | $\text{Recall} = \frac{TP}{TP + FN}$ | $\text{Precision} = \frac{TP}{TP + FP}$ |

注意 Precision 又叫 **Positive Predictive Value** (PPV, 阳性预测值)。

**ROC 的问题**：当负样本极多（如 1:10000），$TN$ 在分母里是天文数字，即使 $FP$ 增加很多，$\text{FPR} = \frac{FP}{FP + TN}$ 几乎不变。结果是：模型产生了海量误报，ROC 看起来还是贴着左上角，AUC 接近 1，给出虚假的乐观。

**PR 的敏感性**：Precision 的分母是 $TP + FP$，没有 TN。多一个 FP 就直接拉低 precision。所以 PR 曲线精准反映少数类的实际检出质量。

### 一个直观例子

10000 个样本，100 正、9900 负。模型把 top-200 打成正：其中 90 个真阳，110 个假阳。

- $\text{TPR} = 90 / 100 = 0.9$。
- $\text{FPR} = 110 / 9900 \approx 0.011$ ← 看起来很小。
- $\text{Precision} = 90 / 200 = 0.45$ ← 一半是误报。

ROC 给人"完美"错觉，PR 直接暴露 45% 精度。

## 4. 什么时候用哪个

| 场景 | 首选 |
|-----|------|
| 类别大致平衡 | ROC-AUC |
| 不平衡 + 关心少数类的检出质量 | PR-AUC（也叫 Average Precision） |
| 欺诈 / 罕见病 / 异常检测 | PR |
| 两个模型的通用排序能力对比 | ROC |
| 有固定预算（如只能审查 1% 样本） | Precision@K / Recall@K |

## 5. 常见追问预判

**PR-AUC (Average Precision) 的物理意义**：

$$\text{AP} = \sum_n (R_n - R_{n-1}) P_n$$

即对 recall 的离散积分。直觉：按分数从高到低扫，每召回一个正样本时当前 precision 的加权平均。

**ROC 曲线在不平衡时为什么形状不变**：因为 ROC 的两个轴都是条件率（给定正类 / 给定负类），与先验 $P(y = 1)$ 解耦。而 PR 曲线随先验变化——同一模型在不平衡数据上 PR-AUC 会下降。

**Baseline**：

- ROC 的随机 baseline 恒为 0.5。
- PR 的随机 baseline 是正类比例（如 1% 正样本时随机模型 PR-AUC $\approx$ 0.01）。

**F1 vs PR-AUC**：F1 是 PR 曲线上某一个点（某个固定阈值）的调和平均；PR-AUC 是整条曲线的总结，阈值无关。
"""


DESC_CE_KL = r"""# Cross-Entropy and KL Divergence

## 1. 三个概念先理清

**Entropy (熵)**：单个分布 $P$ 自己的"不确定性"。

$$H(P) = -\sum_i P(i) \log P(i)$$

$P$ 越均匀 $H$ 越大，越集中 $H$ 越小。one-hot 分布 $H = 0$。

**Cross-Entropy** (CE, 交叉熵)：用分布 $Q$ 来编码真实分布 $P$ 的平均 code length。

$$H(P, Q) = -\sum_i P(i) \log Q(i)$$

$Q$ 越接近 $P$ 越小，$Q = P$ 时取最小值 $= H(P)$。

**Kullback-Leibler Divergence** (KL, KL 散度)：分布间的"非对称距离"。

$$D_{\text{KL}}(P \| Q) = \sum_i P(i) \log \frac{P(i)}{Q(i)}$$

$\ge 0$，当且仅当 $P = Q$ 时 $= 0$。非对称：$D_{\text{KL}}(P \| Q) \ne D_{\text{KL}}(Q \| P)$。

## 2. 核心关系

$$\boxed{\ H(P, Q) = H(P) + D_{\text{KL}}(P \| Q)\ }$$

一行推导：

$$H(P, Q) = -\sum P \log Q = -\sum P \log P + \sum P \log \frac{P}{Q} = H(P) + D_{\text{KL}}(P \| Q)$$

含义：交叉熵 = "P 本身的不确定性" + "用 Q 去近似 P 多付出的代价"。

## 3. 为什么分类任务用交叉熵

训练时 $P$ 是 ground-truth label（通常 one-hot），$Q$ 是模型输出的 softmax 分布。

- $P$ 固定 → $H(P)$ 是常数（one-hot 时直接 = 0）。
- 所以 $\min_\theta H(P, Q_\theta) \iff \min_\theta D_{\text{KL}}(P \| Q_\theta)$。

最小化交叉熵 = 最小化 KL 散度，只差一个与 $\theta$ 无关的常数。两者效果完全等价，但 CE 的形式更简单（不用算 $H(P)$ 那一项）、数值更稳定，所以用 CE。

进一步：CE 也恰好就是 Bernoulli / Categorical 分布下的 **Negative Log-Likelihood** (NLL, 负对数似然)，所以它同时是 **Maximum Likelihood Estimation** (MLE, 最大似然估计) 的自然产物。

## 4. 为什么不直接用 MSE

- MSE + softmax 是非凸的（前面 logistic 那题讲过的理由同样适用）。
- 对"错得很离谱"的样本，MSE 梯度会因为 softmax 饱和而消失；CE 梯度是 $(\hat{y} - y)$ 形式，错得越狠梯度越大，学习信号干净。
- CE 有信息论 / 概率论的自然动机，MSE 没有（把 categorical label 当连续量是 model misspecification）。

## 5. KL 的非对称性 — 两个方向有不同物理含义

$D_{\text{KL}}(P \| Q)$ 和 $D_{\text{KL}}(Q \| P)$ 不一样，各有用处：

**Forward KL**：$D_{\text{KL}}(P \| Q)$（$P$ 是真，$Q$ 是近似）

- 分类任务里用的就是这个方向。
- 性质 mean-seeking / mode-covering：$Q$ 必须在 $P$ 非零的地方都非零，否则 $\log(P / Q) \to \infty$。结果 $Q$ 倾向于"覆盖" $P$ 的所有 mode，哪怕都覆盖不太准。

**Reverse KL**：$D_{\text{KL}}(Q \| P)$

- VAE 的 ELBO 里出现的是这个。
- 性质 mode-seeking：$Q$ 只要在自己非零的地方 $P$ 也非零就行。结果 $Q$ 倾向于"锁定" $P$ 的某一个 mode，不去覆盖其他 mode。

直观记忆：forward KL 让近似分布"摊开"，reverse KL 让它"聚焦"。

## 6. 对称替代：**Jensen-Shannon Divergence** (JS, JS 散度)

$$D_{\text{JS}}(P, Q) = \tfrac{1}{2} D_{\text{KL}}(P \| M) + \tfrac{1}{2} D_{\text{KL}}(Q \| M), \quad M = \tfrac{1}{2}(P + Q)$$

对称、有界 $\in [0, \log 2]$。原始 GAN 的 loss 就等价于最小化 JS。

## 7. 常见追问预判

**Label smoothing 的信息论解释**：把 one-hot $[0, 0, 1, 0]$ 换成 $[0.025, 0.025, 0.925, 0.025]$。此时 $H(P) \ne 0$，CE 和 KL 相差的常数变了，但最优化行为上等价于"不让 $Q$ 变得太尖锐"——鼓励模型 output 更平滑的概率分布，防止过拟合和过度自信。

**Distillation**：student 用 soft label（teacher 的 softmax 输出，通常 temperature > 1）做 training，本质是 $D_{\text{KL}}(\text{teacher} \| \text{student})$。此时 teacher 的分布不是 one-hot，$H(P)$ 不是 0 也不是常数（teacher 对每个样本的熵不同），所以 CE 和 KL 在这里严格区分，要用 KL。

**Focal loss** 是 CE 的加权变体，不改变 CE 的信息论基础。

**Wasserstein distance**：KL / JS 在两个分布几乎不重叠时会爆炸或饱和（GAN 训练不稳的根源）。Wasserstein 度量考虑"运输成本"，即使无重叠也给出有意义的梯度，WGAN 用的就是它。
"""


# Map each leaf path -> (placeholder, new_description)
LEAVES: dict[str, tuple[str, str]] = {
    "ml-fundamentals/classical_ml/bias-variance-tradeoff": (
        "TODO[MLF-bias-variance-tradeoff]",
        DESC_BIAS_VARIANCE,
    ),
    "ml-fundamentals/classical_ml/l1-vs-l2-regularization": (
        "TODO[MLF-l1-vs-l2-regularization]",
        DESC_L1_L2,
    ),
    "ml-fundamentals/classical_ml/logistic-regression-loss": (
        "TODO[MLF-logistic-regression-loss]",
        DESC_LOGISTIC,
    ),
    "ml-fundamentals/classical_ml/gbdt-vs-rf-xgboost": (
        "TODO[MLF-gbdt-vs-rf-xgboost]",
        DESC_GBDT_RF_XGB,
    ),
    "ml-fundamentals/classical_ml/cross-entropy-kl-divergence": (
        "TODO[MLF-cross-entropy-kl-divergence]",
        DESC_CE_KL,
    ),
    "ml-fundamentals/eval_data/class-imbalance-handling": (
        "TODO[MLF-class-imbalance-handling]",
        DESC_CLASS_IMBALANCE,
    ),
    "ml-fundamentals/eval_data/auc-vs-pr-curve": (
        "TODO[MLF-auc-vs-pr-curve]",
        DESC_AUC_PR,
    ),
}


def sha256_of_descriptions(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pairs of the 7 target leaves."""
    h = hashlib.sha256()
    for path in sorted(LEAVES.keys()):
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE path = ?", (path,)
        ).fetchone()
        h.update(path.encode("utf-8"))
        h.update(b"\x00")
        h.update((row[0] or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: each description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    # Pre-flight: validate every staged content meets AC before touching DB.
    for path, (_placeholder, content) in LEAVES.items():
        validate_content(path, content)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_descriptions(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = {"UPDATED": 0, "SKIPPED": 0}
        for path, (placeholder, new_content) in LEAVES.items():
            row = conn.execute(
                "SELECT id, description FROM framework_nodes WHERE path = ?",
                (path,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"[FAIL] missing node at path={path}")
            node_id, current = row
            if current == new_content:
                counts["SKIPPED"] += 1
                print(f"[SKIP]   id={node_id} path={path}")
                continue
            if current != placeholder:
                preview = (current or "")[:80].replace("\n", " ")
                raise RuntimeError(
                    f"[CONFLICT] path={path}: existing description neither "
                    f"placeholder nor expected new content. "
                    f"current[:80]={preview!r}"
                )
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (new_content, node_id),
            )
            counts["UPDATED"] += 1
            print(
                f"[UPDATE] id={node_id} path={path} "
                f"len={len(new_content)} (was {len(current)})"
            )

        conn.commit()
        post_hash = sha256_of_descriptions(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={counts['UPDATED'] + counts['SKIPPED']} (expected 7)"
    )
    if counts["UPDATED"] + counts["SKIPPED"] != 7:
        print("[FAIL] expected to touch exactly 7 leaves")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
