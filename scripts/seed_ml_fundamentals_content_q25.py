"""Seed: T-P0-545 -- ML Fundamentals Y-depth Q#25 MLE vs MAP.

[T-MLF-06c] Upgrades Question 25 (Maximum Likelihood Estimation vs
Maximum A Posteriori) from the X-depth placeholder to the locked
Y-depth template (the same template applied to #22 in T-P0-544)
into framework_nodes.description for the leaf at path
'ml-fundamentals/llm_stats/mle-vs-map'.

Y-depth = deep expansion. Per the 5-section template:

  1. 问题设定       -- Frequentist vs Bayesian framing; MLE / MAP /
                       full Bayesian as point-estimator hierarchy;
                       notation table.
  2. 推导           -- Gaussian MLE (mu, sigma^2) with L2 equivalence;
                       Bernoulli MLE vs MAP with Beta prior;
                       Laplace prior -> L1 equivalence via KKT
                       stationarity; full MAP decomposition
                       log p(theta|D) = log p(D|theta) + log p(theta)
                       + const; prior-as-regularizer equivalence.
  3. 物理意义       -- Why prior sharpness (sigma or b) controls the
                       regularization strength lambda; Gaussian prior
                       = isotropic shrinkage toward 0; Laplace prior
                       = sparsity via non-smooth point at 0;
                       asymptotic behavior n -> infinity.
  4. 常见追问预判   -- 6 items (conjugate priors / Beta-Bernoulli
                       posterior; n -> infinity asymptotic and data
                       swamping the prior; when to prefer MAP over
                       MLE; credible intervals vs confidence
                       intervals; Jeffreys prior and MLE-invariance;
                       Empirical Bayes as halfway house).
  5. 参考           -- 4+ refs (Bishop 2006 PRML Ch. 3-4; Murphy 2012
                       MLaPP Ch. 5-7; Gelman et al. BDA3;
                       Tibshirani 1996 Lasso; Hoerl & Kennard 1970
                       Ridge).

Acronyms first-occurrence expanded in bold **English** (acronym, 中文)
per data/ml_fundamentals_inventory.yaml: MLE, MAP, KKT. Additional
first-occurrence acronyms inline: iid, MSE, MAE, MCMC, VI.

Idempotency:
  - Expected description is a single raw-string constant.
  - Second run yields updated=0 skipped=1 conflict=0.
  - SHA-256 of (path, description) captured pre/post for audit.
  - If the existing description is neither the placeholder
    'TODO[MLF-mle-vs-map]' nor the new content, script aborts
    with [CONFLICT] before any write.

Acceptance:
  - framework_nodes row at path
    'ml-fundamentals/llm_stats/mle-vs-map' updated.
  - Description contains KaTeX math ($ or $$) and section headers (## ).
  - Re-run is no-op (updated=0).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

TARGET_PATH = "ml-fundamentals/llm_stats/mle-vs-map"
PLACEHOLDER = "TODO[MLF-mle-vs-map]"


DESC_MLE_VS_MAP = r"""# MLE vs MAP：频率派与贝叶斯派的点估计

## 1. 问题设定

参数估计要回答的问题是："给定观测数据 $D = \{x_1, \ldots, x_n\}$ 和参数化概率模型 $p(x \mid \theta)$，如何从数据反推参数 $\theta$？"。**Maximum Likelihood Estimation** (MLE, 极大似然估计) 和 **Maximum A Posteriori** (MAP, 最大后验估计) 是机器学习里两种最主流的点估计框架，对应**频率派**（frequentist）和**贝叶斯派**（Bayesian）对"参数"本质的两种不同哲学。

- **频率派 / MLE**：$\theta$ 是一个固定但未知的常数，数据是随机的。推断的目标是找到使得观测数据最可能发生的那个 $\theta$：$\hat{\theta}_{\text{MLE}} = \arg\max_\theta p(D \mid \theta)$。不对 $\theta$ 放任何先验分布——数据不够多时，MLE 就大大方方过拟合。
- **贝叶斯派 / MAP**：$\theta$ 本身是随机变量，带一个**先验** $p(\theta)$ 表示"在看数据之前，我相信 $\theta$ 大概是什么样子"。结合数据后，贝叶斯定理给出**后验** $p(\theta \mid D) \propto p(D \mid \theta)\,p(\theta)$。MAP 取后验的 argmax：$\hat{\theta}_{\text{MAP}} = \arg\max_\theta p(\theta \mid D)$。先验项就是**正则化**。
- **完全贝叶斯** (full Bayesian)：不取点估计，保留整个后验 $p(\theta \mid D)$，预测时做积分 $p(y \mid x, D) = \int p(y \mid x, \theta)\,p(\theta \mid D)\,\mathrm{d}\theta$。代价是计算量大（常需 **Markov Chain Monte Carlo** (MCMC, 马尔可夫链蒙特卡洛) 或 **Variational Inference** (VI, 变分推断)），所以实际工程里 MAP 是"贝叶斯派的点估计近似"。

为什么这三者是同一梯度上的三档？MAP 可以看作 "**MLE + 先验作为正则项**"，完全贝叶斯可以看作 "**MAP 之上再加上对后验的积分**"。这给出一个自然的 trade-off：信息 vs 计算量。

| 方法 | 参数观 | 输出 | 正则化 | 过拟合风险 | 计算成本 |
|------|--------|------|--------|------------|----------|
| MLE | 频率派（常数） | 点估计 $\hat{\theta}$ | 无 | 高 | 低 |
| MAP | 贝叶斯派（随机） | 点估计 $\hat{\theta}$ | 先验 $p(\theta)$ | 中 | 低 |
| Full Bayesian | 贝叶斯派 | 后验分布 $p(\theta \mid D)$ | 先验 | 最低 | 高 (MCMC/VI) |

本节记号约定：数据 $D = \{x_i\}_{i=1}^{n}$，训练样本 **independent and identically distributed** (iid, 独立同分布)；对数似然 $\ell(\theta) = \log p(D \mid \theta) = \sum_i \log p(x_i \mid \theta)$；后验未归一化对数 $\log p(\theta \mid D) = \ell(\theta) + \log p(\theta) + \text{const}$。

## 2. 推导

### 2.1 高斯 MLE：$\hat\mu$ 和 $\hat\sigma^2$

设 $x_1, \ldots, x_n \stackrel{\text{iid}}{\sim} \mathcal{N}(\mu, \sigma^2)$。对数似然为

$$\ell(\mu, \sigma^2) = -\frac{n}{2}\log(2\pi) - \frac{n}{2}\log\sigma^2 - \frac{1}{2\sigma^2}\sum_{i=1}^{n}(x_i - \mu)^2$$

对 $\mu$ 求偏导令其为零：$\partial_\mu \ell = \frac{1}{\sigma^2}\sum_i (x_i - \mu) = 0 \Rightarrow \hat\mu_{\text{MLE}} = \bar x = \frac{1}{n}\sum_i x_i$。

对 $\sigma^2$ 求偏导令其为零：

$$\partial_{\sigma^2} \ell = -\frac{n}{2\sigma^2} + \frac{1}{2\sigma^4}\sum_{i=1}^{n}(x_i - \mu)^2 = 0 \;\Rightarrow\; \hat\sigma^2_{\text{MLE}} = \frac{1}{n}\sum_{i=1}^{n}(x_i - \hat\mu)^2$$

**注意**：$\hat\sigma^2_{\text{MLE}}$ **有偏**：$\mathbb{E}[\hat\sigma^2_{\text{MLE}}] = \frac{n-1}{n}\sigma^2$。因为用的是估计值 $\hat\mu$ 而非真值 $\mu$，残差向量 $(x_i - \hat\mu)$ 被投影到 $n-1$ 维子空间，丢了一个自由度。无偏估计要除以 $n-1$（Bessel 修正）。这个有偏/无偏的分歧恰好显示了 MLE 的一个经典缺陷——**MLE 只是渐近无偏**（$n \to \infty$ 时 $\hat\sigma^2_{\text{MLE}} \to \sigma^2$），有限样本下会系统性低估。

### 2.2 MSE 损失 = 高斯似然下的 MLE

线性回归 $y = f_\theta(x) + \epsilon$，假设 $\epsilon \sim \mathcal{N}(0, \sigma^2)$。观测对数似然

$$\log p(y \mid x, \theta) = -\frac{1}{2\sigma^2}(y - f_\theta(x))^2 + \text{const}$$

所以 $\arg\max_\theta \sum_i \log p(y_i \mid x_i, \theta) = \arg\min_\theta \sum_i (y_i - f_\theta(x_i))^2$——**Mean Squared Error** (MSE, 均方误差) 损失就是高斯噪声假设下的负对数似然。这是"为什么回归用 MSE" 的概率答案，而非"就是这样定义的"。类似地：

- **Mean Absolute Error** (MAE, 平均绝对误差) $\Leftrightarrow$ Laplace 噪声的 MLE；
- 交叉熵 $\Leftrightarrow$ Bernoulli / Categorical 似然的 MLE。

### 2.3 MAP 分解：对数后验 = 对数似然 + 对数先验

后验 $p(\theta \mid D) = \frac{p(D \mid \theta)\,p(\theta)}{p(D)}$。分母 $p(D)$ 是边缘似然（对 $\theta$ 积分），跟 $\theta$ 无关，在 argmax 里消掉。取对数：

$$\log p(\theta \mid D) \;=\; \underbrace{\log p(D \mid \theta)}_{\ell(\theta)} \;+\; \underbrace{\log p(\theta)}_{\text{正则项}} \;+\; \underbrace{\text{const}}_{-\log p(D)}$$

$$\boxed{\;\hat\theta_{\text{MAP}} \;=\; \arg\max_\theta \left[\, \ell(\theta) + \log p(\theta) \,\right]\;}$$

$\log p(\theta)$ 起到正则项的作用。**先验越"尖"**（方差越小），$\log p(\theta)$ 在偏离先验中心时下降得越快，对偏离的惩罚越重；**先验越"平"**（方差越大），惩罚越弱，MAP 越接近 MLE。先验趋于均匀时 MAP 退化为 MLE（下 §3.3 给出一般命题）。

### 2.4 高斯先验 $\Leftrightarrow$ L2 正则化（Ridge）

假设 $\theta \sim \mathcal{N}(0, \tau^2 I)$，即每个分量独立、以 0 为中心、方差 $\tau^2$。对数先验：

$$\log p(\theta) \;=\; -\frac{1}{2\tau^2}\,\|\theta\|_2^2 + \text{const}$$

把它加到 MLE 的对数似然上：

$$\hat\theta_{\text{MAP}} = \arg\max_\theta \left[\,\ell(\theta) - \frac{1}{2\tau^2}\,\|\theta\|_2^2\,\right] = \arg\min_\theta \left[\,-\ell(\theta) + \frac{\lambda}{2}\,\|\theta\|_2^2\,\right],\quad \lambda = \frac{1}{\tau^2}$$

**高斯先验的 MAP 等价于 L2 正则化（Ridge）**。这个映射严格成立：$\lambda$ 是先验精度（precision，方差的倒数），先验**越窄**（$\tau^2 \downarrow$） $\Leftrightarrow$ $\lambda$ **越大** $\Leftrightarrow$ 正则化**越强**。

### 2.5 Laplace 先验 $\Leftrightarrow$ L1 正则化（Lasso）+ 用 **Karush-Kuhn-Tucker** (KKT, 卡鲁什-库恩-塔克) 条件看稀疏性

假设 $\theta_j \stackrel{\text{iid}}{\sim} \text{Laplace}(0, b)$，密度 $p(\theta_j) = \frac{1}{2b}\exp(-|\theta_j|/b)$。对数先验：

$$\log p(\theta) \;=\; -\frac{1}{b}\,\|\theta\|_1 + \text{const}$$

MAP 目标：

$$\hat\theta_{\text{MAP}} = \arg\min_\theta \left[\,-\ell(\theta) + \lambda\,\|\theta\|_1\,\right],\quad \lambda = \frac{1}{b}$$

**Laplace 先验的 MAP 等价于 L1 正则化（Lasso）**。L1 产生稀疏解（许多分量恰为 0）的原理可以用 **KKT** 条件解释：以平方损失为例 $-\ell(\theta) = \frac{1}{2}\|y - X\theta\|_2^2$，$\partial_j |\theta_j| = \mathrm{sign}(\theta_j)$（$\theta_j \ne 0$）或 $[-1, 1]$（$\theta_j = 0$，次梯度）。KKT 稳定性（stationarity）要求对每个 $j$：

$$X_j^\top(y - X\theta) \in \lambda \cdot \partial |\theta_j|$$

$\theta_j = 0$ 时 $\partial |\theta_j| = [-1, 1]$，条件变成 $|X_j^\top(y - X\theta)| \le \lambda$——只要这个"校正相关性" 在 $\pm\lambda$ 区间内，$\theta_j = 0$ 就是稳定点。$\lambda$ 越大，越多特征满足这个不等式，越多系数被压到 0。这个非光滑拐角（non-smooth kink at zero）正是 L1 产生稀疏的几何来源；高斯先验在 0 处平滑（二阶可导），不会把分量"掐断"，只会把它缩小。

### 2.6 Bernoulli MLE vs MAP with Beta 先验：共轭对的闭式解

$n$ 次独立伯努利试验，$k$ 次成功。对数似然 $\ell(p) = k\log p + (n-k)\log(1-p)$。

**MLE**：$\partial_p \ell = k/p - (n-k)/(1-p) = 0 \Rightarrow \hat p_{\text{MLE}} = k/n$。

**MAP with** $p \sim \text{Beta}(a, b)$：$\log p(p) = (a-1)\log p + (b-1)\log(1-p) + \text{const}$。对数后验

$$\log p(p \mid D) \propto (k + a - 1)\log p + (n - k + b - 1)\log(1 - p)$$

求导令零：$\hat p_{\text{MAP}} = \dfrac{k + a - 1}{n + a + b - 2}$。几何解读：$a - 1$ 和 $b - 1$ 扮演"虚拟成功次数"和"虚拟失败次数"，先验把额外的 $a + b - 2$ 个**伪样本**（pseudo-counts）注入到似然里。

- $a = b = 1$（均匀先验 $\text{Beta}(1, 1)$）：$\hat p_{\text{MAP}} = k/n = \hat p_{\text{MLE}}$。
- $a = b = 2$（弱先验 $\text{Beta}(2, 2)$，中心在 $0.5$）：$\hat p = (k+1)/(n+2)$，著名的"Laplace 平滑"。
- $n \to \infty$：$\hat p_{\text{MAP}} \to k/n$——数据"淹没"先验（§3.3 正式讨论）。

这里 Beta 是 Bernoulli 的共轭先验——后验仍是 Beta：若先验 $\text{Beta}(a, b)$，后验为 $\text{Beta}(a + k, b + n - k)$。共轭性让 MAP、后验均值、可信区间都有闭式解，无需 MCMC。

## 3. 物理意义

### 3.1 先验方差 $\sigma$ 或 $b$ 控制 $\lambda$：先验"尖"$\Leftrightarrow$正则化"紧"

从 §2.4 和 §2.5 直接读出：

| 先验 | 方差参数 | 等价正则化 | $\lambda$ |
|------|----------|-------------|-----------|
| $\mathcal{N}(0, \tau^2)$ | $\tau^2$ | L2（$\|\theta\|_2^2$） | $\lambda = 1/\tau^2$ |
| $\text{Laplace}(0, b)$ | $2b^2$（尺度 $b$） | L1（$\|\theta\|_1$） | $\lambda = 1/b$ |

先验方差 $\tau^2$（或尺度 $b$）**越小**，先验概率密度在 0 处**越尖**，相对于"$\theta$ 离 0 很远" 的区域，概率比悬殊越大——这就是对偏离 0 的"信念强度"。强信念 $\Leftrightarrow$ 大 $\lambda$ $\Leftrightarrow$ 强正则化 $\Leftrightarrow$ 解被拉回 0 附近更多。

等价地：$\lambda$ 是**信息的单位换算率**——每一个单位的 $\|\theta\|$ 正则化项，相当于"$\lambda$ 个单位的先验信息"。$\lambda$ 越大，先验信息权重越高；$\lambda = 0$ 等价于没有先验信息（均匀先验），退化到 MLE。

### 3.2 高斯先验 = 各向同性缩水；Laplace 先验 = 非光滑拐点 = 稀疏

高斯先验的**密度光滑**：$p(\theta) \propto \exp(-\|\theta\|^2 / 2\tau^2)$ 在任何 $\theta$ 处都二阶可微，在 0 处有一个光滑的峰而非尖角。几何上 MAP 等价于**各向同性缩水**（isotropic shrinkage）——把原本会落在 $\hat\theta_{\text{MLE}}$ 的解按 $\lambda / (\lambda + \text{Hessian})$ 的比例拉向 0，但极少把某一分量真正压成 0。Ridge 的解是连续的、稠密的。

Laplace 先验的密度在 0 处**非光滑**（一阶导不连续）：$p(\theta) \propto \exp(-\|\theta\|_1 / b)$，$\|\theta\|_1$ 在坐标轴上有尖角。这个几何"拐点"和损失函数的等高线切到坐标轴的角上——只要切到，那个分量就恰好为 0。正是 §2.5 的 KKT 条件说的：$|X_j^\top \text{residual}| \le \lambda$ 时 $\theta_j = 0$ 成立的可行域。Laplace 先验把"稀疏" 编码成了一个**几何事实**，不是启发式修剪的副产品。

这个几何直觉还解释了 L1 为什么适合特征选择：不仅"变小"而且"归零"的分量才真正被从模型中剔除。

### 3.3 $n \to \infty$：数据淹没先验

MAP 对数目标 = $\ell(\theta) + \log p(\theta)$。$\ell(\theta)$ 随 $n$ 线性增长（$\sum_{i=1}^{n} \log p(x_i \mid \theta)$ 有 $n$ 项），$\log p(\theta)$ 不依赖 $n$。所以当 $n \to \infty$：

$$\frac{1}{n}\,\log p(\theta \mid D) \;=\; \frac{1}{n}\,\ell(\theta) + \underbrace{\frac{1}{n}\log p(\theta)}_{\to\, 0} + \text{const}$$

先验项的相对权重 $\to 0$，MAP 收敛到 MLE（在正则条件下，也收敛到真值 $\theta^\star$，这是 **Bernstein-von Mises 定理** 的后果：贝叶斯后验在 $n \to \infty$ 时向 $\hat\theta_{\text{MLE}}$ 附近的高斯分布收缩）。

工程启示：(i) 大数据时代选 MLE 还是 MAP 差别很小——先验被"淹没"；(ii) 先验的价值在**小样本**或**重尾**场景——它防止模型把噪声当信号；(iii) $\lambda$ 的最优值通常随 $n$ 减小（越多数据，越少正则化），这是 cross-validation 选 $\lambda$ 的理论根据。

### 3.4 MAP 并非永远"更好"：模式 vs 均值的 mismatch

直觉上 MAP 加了先验所以比 MLE 鲁棒——大部分情况确实如此。但 MAP 有个概念陷阱：**MAP 取的是后验的众数（mode），不是均值**。后验如果偏斜或多峰，mode 可能远离 mean。例子：Bernoulli + Beta$(0.5, 0.5)$（Jeffreys 先验）在 $k = 0$ 的时候，后验是 $\text{Beta}(0.5, n + 0.5)$，模式在 $p = 0$（边界），而后验均值是 $0.5/(n + 1)$——两者差很大。更极端的情况下，MAP 对**坐标变换不保持不变**（MLE 因为 $\arg\max$ 和 $\log$ 单调性是不变的；MAP 因为先验密度随坐标变换带 Jacobian，mode 会漂移）。这是"为什么贝叶斯派更喜欢后验均值" 的一个理由。

## 4. 常见追问预判

### 4.1 什么是共轭先验？为什么工程上有用？

**共轭先验**（conjugate prior）：如果先验属于某个分布族 $\mathcal{F}$，观测数据后的后验也属于 $\mathcal{F}$，那么 $\mathcal{F}$ 就是给定似然模型的共轭先验族。经典三对：

- Bernoulli / Binomial likelihood + Beta prior $\to$ Beta posterior。
- Poisson likelihood + Gamma prior $\to$ Gamma posterior。
- Gaussian (均值已知，估方差) + Inverse-Gamma $\to$ Inverse-Gamma posterior；Gaussian (方差已知，估均值) + Gaussian prior $\to$ Gaussian posterior。

工程好处：(i) 后验更新**闭式**（参数加加减减就完了，不用 MCMC）；(ii) 可信区间 / 边缘似然有解析表达；(iii) Empirical Bayes（§4.6）可以直接用极大化边缘似然来估超参。坏处：共轭族往往表达能力有限，真实问题里"对 $\theta$ 的先验"不一定是 Beta/Gamma 形状。现代贝叶斯更倾向 HMC（Hamiltonian Monte Carlo）或 VI 跳出共轭家族。

### 4.2 什么时候应该用 MAP 而不是 MLE？

经验准则：

1. **样本小 / 维度高**：参数数远超样本数时 MLE 过拟合，MAP 的先验做正则化；高维回归经典场景。
2. **重尾 / 稀疏需求**：有理由相信"真实 $\theta$ 大部分分量接近 0" 时，用 Laplace/horseshoe 先验；Ridge 对重尾 / 稀疏信号欠拟合。
3. **领域先验可表述**：贝叶斯推理里，先验不必是"0-中心的高斯"，可以编码领域知识（比如药物剂量必须 $\ge 0$、某参数有历史估计范围）。
4. **需要不确定性**：虽然 MAP 只给点估计，但可以顺便做**Laplace 近似**——把后验局部用一个以 $\hat\theta_{\text{MAP}}$ 为均值、Hessian 倒数为协方差的高斯近似，无成本得到 approximate 置信带。

**不用** MAP 的场景：大数据（先验被淹没）、完全不知道先验形状时选 MLE 更简洁（不想编造先验）、需要坐标变换不变性（MLE 是不变的）。

### 4.3 信用区间 vs 置信区间：一个经典坑

- **Confidence interval**（置信区间，频率派）：$[L(D), U(D)]$ 是数据的函数，解释是"在反复抽样的设定下，95% 的区间会覆盖真值 $\theta^\star$"。单个区间**要么包含要么不包含**真值，概率谈的是**程序**不是 $\theta$。
- **Credible interval**（信用 / 可信区间，贝叶斯派）：一个对 $\theta$ 的后验区间，满足 $\mathbb{P}(\theta \in [L, U] \mid D) = 0.95$。直接谈 $\theta$ 的概率——这是贝叶斯派把 $\theta$ 视为随机变量的直接后果。

面试易错点：频率派**不能**说"这个 95% 置信区间里真值以 95% 概率落在这里"——真值是常数，不谈概率。贝叶斯派可以这样说——因为先验已经把 $\theta$ 变成了随机变量。两者数值上**经常接近**（Bernstein-von Mises），但解释框架完全不同。

### 4.4 Jeffreys 先验与 MLE 的坐标不变性

MLE 的一个优势是**不变性**：若 $\hat\theta_{\text{MLE}}$ 是 $\theta$ 的 MLE，则 $g(\hat\theta_{\text{MLE}})$ 是 $g(\theta)$ 的 MLE。这直接从 $\arg\max$ 的定义看出来。MAP 用"先验密度" 作为正则项时**不具备**这种不变性——坐标变换带来 Jacobian，mode 会漂移。

**Jeffreys 先验** $p(\theta) \propto \sqrt{\det I(\theta)}$（$I(\theta)$ 是 Fisher 信息矩阵）**是坐标不变的**：证明用 $I(\theta)$ 在变量替换下变换为 $|\partial\theta/\partial\phi|^2 I(\theta)$，开方后正好配上 Jacobian。Jeffreys 先验是一种"客观先验" 候选；但它经常是**不正常先验**（improper，积分无穷大），实用中要验证其后验仍是正常的。

### 4.5 MLE 估计量的大样本性质

大样本理论（$n \to \infty$）下 MLE 的三条性质（正则条件成立时）：

- **一致性**（consistency）：$\hat\theta_{\text{MLE}} \stackrel{P}{\to} \theta^\star$。
- **渐近正态性**：$\sqrt{n}(\hat\theta_{\text{MLE}} - \theta^\star) \stackrel{d}{\to} \mathcal{N}(0, I(\theta^\star)^{-1})$，$I(\theta)$ 是单样本 Fisher 信息。
- **渐近有效性**：任何**无偏** 估计量的方差下界是 Cramer-Rao $\frac{1}{n I(\theta)}$；MLE 渐近达到这个下界，所以是渐近**最优**的。

这三条是"为什么 MLE 是默认估计量" 的理论基础。注意是**渐近**——小样本下 MLE 可以很糟（高斯方差的有偏性、logistic 回归的完全分离都是例子）。

### 4.6 Empirical Bayes：$\lambda$ 的"自动调"

纯贝叶斯要求先验超参（如高斯先验的方差 $\tau^2$，即 $\lambda = 1/\tau^2$）预先给定。纯 MLE 不用先验。中间方案是 **Empirical Bayes**：用数据估 $\tau^2$，具体做法是极大化**边缘似然**（marginal likelihood / evidence）：

$$\hat\tau^2 = \arg\max_{\tau^2} \int p(D \mid \theta)\,p(\theta \mid \tau^2)\,\mathrm{d}\theta$$

内层积分对 $\theta$ 做出边缘化，相当于自动做了 Occam's razor——过复杂模型在边缘似然里会被惩罚。工程上有两种做法：(i) 闭式解（共轭族下常有）；(ii) **Expectation-Maximization**（EM）交替更新 $\theta$ 和 $\tau^2$。sklearn 的 `BayesianRidge` 就是这种实现；它不用交叉验证选 $\lambda$，而是从边缘似然里"学出来"。交叉验证是频率派答法，Empirical Bayes 是贝叶斯派答法——在大数据下两者经验结果接近。

## 5. 参考

- Bishop 2006, *Pattern Recognition and Machine Learning*, Chapters 3-4 —— 线性模型下 MLE / MAP / full Bayesian 的推导三段式；本节的高斯/Laplace 先验与正则化等价性严格跟随这本书的符号。
- Murphy 2012, *Machine Learning: A Probabilistic Perspective*, Chapters 5-7 —— MLE 大样本性质、MAP 的几何直觉、共轭先验的详细目录。
- Gelman, Carlin, Stern, Dunson, Vehtari, Rubin, *Bayesian Data Analysis* (BDA3) —— 贝叶斯推断的标准参考；可信区间 vs 置信区间、Jeffreys 先验、Empirical Bayes 都按这本书的语境讲。
- Tibshirani 1996, *Regression Shrinkage and Selection via the Lasso* —— L1 正则化的原始论文，和 Laplace-MAP 的对应一起构成 §2.5 的完整历史。
- Hoerl & Kennard 1970, *Ridge Regression: Biased Estimation for Nonorthogonal Problems* —— L2 / Ridge 的原始论文，高斯先验的贝叶斯解读在 Lindley & Smith 1972 *Bayes Estimates for the Linear Model* 中给出。
"""


def sha256_of_description(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pair of the target leaf."""
    h = hashlib.sha256()
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE path = ?", (TARGET_PATH,)
    ).fetchone()
    h.update(TARGET_PATH.encode("utf-8"))
    h.update(b"\x00")
    h.update((row[0] or "").encode("utf-8"))
    h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    """Update the single Q#25 leaf with the Y-depth golden answer (idempotent)."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    validate_content(TARGET_PATH, DESC_MLE_VS_MAP)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_description(conn)
        print(f"[PRE]  sha256={pre_hash}")

        row = conn.execute(
            "SELECT id, description FROM framework_nodes WHERE path = ?",
            (TARGET_PATH,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] missing node at path={TARGET_PATH}")
            return 1
        node_id, current = row

        if current == DESC_MLE_VS_MAP:
            print(f"[SKIP]   id={node_id} path={TARGET_PATH} (already up-to-date)")
            counts = {"UPDATED": 0, "SKIPPED": 1}
        elif current != PLACEHOLDER:
            preview = (current or "")[:80].replace("\n", " ")
            raise RuntimeError(
                f"[CONFLICT] path={TARGET_PATH}: existing description neither "
                f"placeholder nor expected new content. current[:80]={preview!r}"
            )
        else:
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (DESC_MLE_VS_MAP, node_id),
            )
            conn.commit()
            counts = {"UPDATED": 1, "SKIPPED": 0}
            print(
                f"[UPDATE] id={node_id} path={TARGET_PATH} "
                f"len={len(DESC_MLE_VS_MAP)} (was {len(current)})"
            )

        post_hash = sha256_of_description(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    total = counts["UPDATED"] + counts["SKIPPED"]
    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={total} (expected 1)"
    )
    if total != 1:
        print("[FAIL] expected to touch exactly 1 leaf")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
