# LinkedIn 概率与统计面试准备笔记

> **来源**: 一亩三分地面经整理
> **公司**: LinkedIn
> **适用岗位**: MLE / Data Scientist / Applied Scientist
> **难度**: Phone Screen + Onsite ML Fundamentals

---

## 目录

1. [Weighted Probability Sampling / Multinomial Distribution](#1-weighted-probability-sampling--multinomial-distribution)
2. [N Random Variables的E[X_bar]和Var[X_bar]](#2-n-random-variables的exbar和varxbar)
3. [Simpson's Paradox (Email Campaign)](#3-simpsons-paradox-email-campaign)
4. [Queueing Theory: 单队列 vs 多队列](#4-queueing-theory-单队列-vs-多队列)
5. [Distributions: 身高分布与LinkedIn Connections分布](#5-distributions-身高分布与linkedin-connections分布)
6. [Class Imbalance处理](#6-class-imbalance处理)
7. [Sampling from Large Dataset与模型验证](#7-sampling-from-large-dataset与模型验证)
8. [Overfitting Prevention (Tree-based Models)](#8-overfitting-prevention-tree-based-models)
9. [L1/L2 Regularization与Bias](#9-l1l2-regularization与bias)
10. [Random Forest Theory](#10-random-forest-theory)
11. [MLE for Distribution Parameters (Normal, GMM, EM)](#11-mle-for-distribution-parameters-normal-gmm-em)
12. [Reservoir Sampling (Infinite Stream)](#12-reservoir-sampling-infinite-stream)
13. [Biased Coin to Uniform Random (0-6)](#13-biased-coin-to-uniform-random-0-6)
14. [Linear vs Logistic Regression数学等价性](#14-linear-vs-logistic-regression数学等价性)

---

## 1. Weighted Probability Sampling / Multinomial Distribution

### 题目描述

一个不公平的N面骰子，每面概率经过softmax归一化。请实现一个sampler，能够按照给定的概率分布进行采样。

### 最佳解答

**核心方法: Inverse CDF Sampling（逆累积分布函数采样）**

**Step 1**: 计算累积概率（cumulative sum）:

$$C_k = \sum_{i=1}^{k} p_i, \quad k = 1, 2, \ldots, N$$

其中 $C_0 = 0$, $C_N = 1$。

**Step 2**: 从均匀分布 $U \sim \text{Uniform}[0, 1)$ 采样一个随机数 $u$。

**Step 3**: 使用binary search找到最小的 $k$ 使得 $C_k > u$，该 $k$ 即为采样结果。

**时间复杂度**:
- 预处理（计算cumsum）: $O(N)$
- 每次采样: $O(\log N)$（binary search）

**空间复杂度**: $O(N)$

### Python代码

```python
import bisect
import random
from typing import List

class WeightedSampler:
    """Inverse CDF sampler for weighted probability distribution."""

    def __init__(self, probs: List[float]) -> None:
        """Initialize with probability vector (must sum to 1)."""
        self.cumsum = []
        running = 0.0
        for p in probs:
            running += p
            self.cumsum.append(running)
        self.cumsum[-1] = 1.0

    def sample(self) -> int:
        """Return sampled index in O(log N)."""
        u = random.random()
        return bisect.bisect_left(self.cumsum, u)


# 使用示例
probs = [0.1, 0.3, 0.2, 0.4]
sampler = WeightedSampler(probs)

from collections import Counter
counts = Counter(sampler.sample() for _ in range(100000))
for k in sorted(counts):
    print(f"Face {k}: {counts[k]/100000:.3f} (expected {probs[k]:.3f})")
```

**进阶方法: Alias Method**

如果需要 $O(1)$ 采样（牺牲 $O(N)$ 预处理时间），可以使用Alias Method:
- 预处理时间 $O(N)$，采样时间 $O(1)$
- 思想：将每个概率分成两部分，构建一个等概率的alias table

### 面试要点

- 首先明确softmax归一化保证 $\sum p_i = 1$
- Inverse CDF是最经典的方法，面试中优先提
- 注意浮点精度问题（cumsum最后一项强制设为1.0）
- 被追问优化时提Alias Method: $O(1)$ per sample
- 提及可以用 `numpy.random.choice` 验证实现的正确性

---

## 2. N Random Variables的E[X_bar]和Var[X_bar]

### 题目描述

给定N个random variables $X_1, X_2, \ldots, X_N$，每个均值为 $\mu$，方差为 $\sigma^2$。

1. 求 $\bar{X} = \frac{1}{N}\sum_{i=1}^N X_i$ 的期望和方差
2. 如果不是iid，存在pairwise correlation $\rho$，结果怎么变？
3. 这和Random Forest有什么联系？

### 最佳解答

**Case 1: iid（独立同分布）**

$$E[\bar{X}] = E\left[\frac{1}{N}\sum_{i=1}^N X_i\right] = \frac{1}{N}\sum_{i=1}^N E[X_i] = \frac{1}{N} \cdot N\mu = \mu$$

$$\text{Var}(\bar{X}) = \text{Var}\left(\frac{1}{N}\sum_{i=1}^N X_i\right) = \frac{1}{N^2}\sum_{i=1}^N \text{Var}(X_i) = \frac{1}{N^2} \cdot N\sigma^2 = \frac{\sigma^2}{N}$$

关键: 方差随 $N$ 线性减小。

**Case 2: 有correlation（pairwise correlation $\rho$）**

当 $\text{Cov}(X_i, X_j) = \rho\sigma^2$ 对所有 $i \neq j$:

$$\text{Var}(\bar{X}) = \frac{1}{N^2}\left[\sum_{i=1}^N \text{Var}(X_i) + \sum_{i \neq j}\text{Cov}(X_i, X_j)\right]$$

$$= \frac{1}{N^2}\left[N\sigma^2 + N(N-1)\rho\sigma^2\right]$$

$$= \frac{\sigma^2}{N}\left[1 + (N-1)\rho\right]$$

$$= \rho\sigma^2 + \frac{(1-\rho)\sigma^2}{N}$$

关键: 当 $N \to \infty$ 时，$\text{Var}(\bar{X}) \to \rho\sigma^2$，不再趋向0！Correlation限制了averaging的效果。

**Case 3: 与Random Forest的联系**

Random Forest = 多棵决策树取平均。每棵树是一个 $X_i$。

- 如果树之间完全独立（$\rho = 0$），ensemble的方差 = $\frac{\sigma^2}{N}$，无限加树可以把方差压到0
- 实际上树之间有correlation（因为训练数据有重叠），所以 $\rho > 0$
- RF通过两个机制降低 $\rho$:
  1. **Bagging**: 每棵树用bootstrap sample训练
  2. **Feature subsampling**: 每次split只考虑随机子集的特征（`max_features`参数）
- 最终方差: $\rho\sigma^2 + \frac{(1-\rho)\sigma^2}{N}$，第一项是irreducible的

### Python代码

```python
import numpy as np
from typing import Tuple

def xbar_stats_iid(mu: float, sigma2: float, n: int) -> Tuple[float, float]:
    """Return E[X_bar] and Var[X_bar] for iid case."""
    return mu, sigma2 / n

def xbar_stats_correlated(
    mu: float, sigma2: float, n: int, rho: float
) -> Tuple[float, float]:
    """Return E[X_bar] and Var[X_bar] with pairwise correlation rho."""
    var = (sigma2 / n) * (1 + (n - 1) * rho)
    return mu, var

# 数值验证
np.random.seed(42)
n, mu, sigma2, rho = 100, 5.0, 4.0, 0.3

cov_matrix = sigma2 * (rho * np.ones((n, n)) + (1 - rho) * np.eye(n))
samples = np.random.multivariate_normal([mu]*n, cov_matrix, size=10000)
xbars = samples.mean(axis=1)

print(f"Empirical E[X_bar]: {xbars.mean():.3f}, Theory: {mu:.3f}")
print(f"Empirical Var[X_bar]: {xbars.var():.3f}, "
      f"Theory: {xbar_stats_correlated(mu, sigma2, n, rho)[1]:.3f}")
```

### 面试要点

- 先写iid case，再推广到correlated case
- 核心公式推导要流畅，注意 $\frac{1}{N^2}$ 提出来
- **必须**主动联系Random Forest，这是面试官最想听到的
- 强调 $\rho$ 是RF的核心bottleneck，解释feature subsampling如何降低 $\rho$
- LinkedIn面经反复出现此题，是高频必考题

---

## 3. Simpson's Paradox (Email Campaign)

### 题目描述

LinkedIn marketing team想测试一个新的email campaign。在SF和NY两个城市分别做了实验。

- SF: 新邮件(B) conversion rate 高于旧邮件(A)
- NY: 新邮件(B) conversion rate 也高于旧邮件(A)
- 但combine两个城市的数据后: 旧邮件(A)总体conversion rate反而更高

为什么会这样？你会怎么判断哪个邮件更好？能否计算CI?

### 最佳解答

**这就是Simpson's Paradox（辛普森悖论）**

**核心原因**: 混杂变量（confounding variable）。两个城市的sample size分配不均。

**数值例子**:

| 城市 | 邮件版本 | 发送量 | 转化数 | 转化率 |
|------|---------|--------|--------|--------|
| SF | A | 100 | 10 | 10% |
| SF | B | 1000 | 150 | 15% |
| NY | A | 1000 | 300 | 30% |
| NY | B | 100 | 35 | 35% |
| **Total** | **A** | **1100** | **310** | **28.2%** |
| **Total** | **B** | **1100** | **185** | **16.8%** |

B在每个城市都赢了，但A总体赢了！原因: A在高转化率的NY city有更多样本，B在低转化率的SF有更多样本。

**正确做法**:

1. **识别confounding factors**: 城市、时区、发送时间、用户群体差异
2. **分层分析（Stratified Analysis）**: 在每个stratum内比较，不要直接合并
3. **Balanced Experiment Design**: 确保每个城市的A/B分配比例一致
4. **统计方法**:
   - Cochran-Mantel-Haenszel test: 控制confounding variable后的分层检验
   - Logistic regression加入城市作为控制变量
   - 加权平均（按城市总人口比例加权）

**关于CI（置信区间）**:
- 可以计算，但必须在每个stratum内分别计算
- 使用分层后的效应量估计，如Mantel-Haenszel odds ratio的CI
- 也可以用bootstrap方法

### Python代码

```python
import numpy as np
from typing import Dict

def simpsons_paradox_demo() -> None:
    """Demonstrate Simpson Paradox with email campaign data."""
    data = {
        "SF": {"A": (100, 10), "B": (1000, 150)},
        "NY": {"A": (1000, 300), "B": (100, 35)},
    }

    for city, versions in data.items():
        for v, (sent, conv) in versions.items():
            print(f"{city} - {v}: {conv/sent:.1%} ({conv}/{sent})")

    for v in ["A", "B"]:
        total_sent = sum(data[c][v][0] for c in data)
        total_conv = sum(data[c][v][1] for c in data)
        print(f"Total - {v}: {total_conv/total_sent:.1%} ({total_conv}/{total_sent})")

def stratified_test(strata: Dict[str, Dict[str, tuple]]) -> float:
    """Cochran-Mantel-Haenszel common odds ratio estimate."""
    numerator = 0.0
    denominator = 0.0
    for city, versions in strata.items():
        a_sent, a_conv = versions["A"]
        b_sent, b_conv = versions["B"]
        n = a_sent + b_sent
        numerator += (a_conv * (b_sent - b_conv)) / n
        denominator += ((a_sent - a_conv) * b_conv) / n
    return numerator / denominator

simpsons_paradox_demo()
```

### 面试要点

- 第一反应就说 "This is Simpson's Paradox"
- 强调confounding variable: 城市、时区、用户base rate不同
- 解决方案: balanced dataset + stratified analysis
- 被问CI时，回答在stratum内计算，推荐CMH test
- LinkedIn面经原题高频出现

---

## 4. Queueing Theory: 单队列 vs 多队列

### 题目描述

一个银行有5个柜员和1条队伍（single queue），另一个银行有5个柜员和5条队伍（multiple queues）。假设到达率和服务率相同，你会排哪边？为什么？

### 最佳解答

**结论: 单队列（1条队伍）更好。**

**直觉解释**:

- **单队列**: 你的等待时间取决于"最快可用的柜员"。任何一个柜员空闲，队伍最前面的人立即被服务。
- **多队列**: 你的等待时间取决于"你所选队伍的柜员速度"。如果你运气不好选了慢队伍，等待时间会远超平均。

**数学分析 (Erlang-C Model)**:

**均值**: 两种情况的**平均等待时间相同**（因为总到达率和总服务能力相同）。

$$E[W_{\text{single}}] = E[W_{\text{multi}}]$$

**方差**: 单队列的方差**更小**。

$$\text{Var}(W_{\text{single}}) < \text{Var}(W_{\text{multi}})$$

**单队列方差更小的原因**:

- 单队列系统是 M/M/c 模型（c=5个服务器，1个队列）
- 多队列系统相当于5个独立的 M/M/1 模型
- M/M/c 的性能严格优于 c 个独立 M/M/1:
  - **Statistical multiplexing**: 单队列利用了所有柜员的pooled capacity
  - 不会出现"一个柜员空闲而其他队伍排长队"的情况

**尾部风险**:
- 单队列: worst case相对可控，因为有5个柜员分摊负载
- 多队列: worst case可能极端（如果你选的柜员特别慢或者前面有复杂业务）

### 面试要点

- 先说结论：单队列更好
- 解释 "same mean, lower variance"
- 提到statistical multiplexing（资源池化）的概念
- 如果被问公式，写出M/M/c的基本设定即可
- 现实中银行、机场安检都在向单队列转变

---

## 5. Distributions: 身高分布与LinkedIn Connections分布

### 题目描述

**Part 1 (身高)**:
1. 画出美国男人身高的分布
2. 画出美国女人身高的分布
3. 把男人女人合并在一起，分布是怎样的？

**Part 2 (LinkedIn Connections)**:
1. 画出每个LinkedIn用户的connections数量的分布
2. 估计mean的值范围
3. 比较mean, median, mode的大小关系

### 最佳解答

**Part 1: 身高分布**

- **男性身高**: Normal distribution, $\mu \approx 175cm$, $\sigma \approx 7.5cm$
- **女性身高**: Normal distribution, $\mu \approx 163cm$, $\sigma \approx 6.5cm$
- **合并**: **Bimodal distribution**（双峰分布）

为什么是bimodal？
- 两个正态分布的均值差约为12cm（约 $2\sigma$）
- 当两个component的均值差 > 两倍标准差时，混合分布呈现双峰
- 如果两个component人数大致相等，两个峰高度接近

$$f(x) = \pi_m \cdot \mathcal{N}(x|\mu_m, \sigma_m^2) + \pi_f \cdot \mathcal{N}(x|\mu_f, \sigma_f^2)$$

其中 $\pi_m \approx \pi_f \approx 0.5$。

**Part 2: LinkedIn Connections分布**

- **分布形状**: 右偏分布（Right-skewed / Positive skew）
- 大部分用户connections数在几十到几百之间
- 少数"super connectors"有数千甚至上万connections
- 类似 **Log-normal** 或 **Power-law** 分布

**Mean的范围**: 大约 500-1000 connections
- LinkedIn官方数据显示平均约500+
- 但被重度用户（recruiters等）拉高

**Mean, Median, Mode的关系**:

对于右偏分布:

$$\text{Mode} < \text{Median} < \text{Mean}$$

**原因**: 右侧长尾把Mean向右拉，Median在中间位置受长尾影响小，Mode是最高频值在左侧。

### Python代码

```python
import numpy as np

def height_mixture_demo() -> None:
    """Generate mixture of male/female height distributions."""
    np.random.seed(42)
    n = 10000
    male = np.random.normal(175, 7.5, n // 2)
    female = np.random.normal(163, 6.5, n // 2)
    combined = np.concatenate([male, female])

    print(f"Male: mean={male.mean():.1f}, std={male.std():.1f}")
    print(f"Female: mean={female.mean():.1f}, std={female.std():.1f}")
    print(f"Combined: mean={combined.mean():.1f}, std={combined.std():.1f}")

def connections_stats() -> None:
    """Simulate right-skewed LinkedIn connections distribution."""
    np.random.seed(42)
    connections = np.random.lognormal(mean=5.5, sigma=1.2, size=100000).astype(int)
    connections = np.clip(connections, 0, 30000)

    mean_val = connections.mean()
    median_val = np.median(connections)
    from collections import Counter
    mode_val = Counter(connections).most_common(1)[0][0]

    print(f"Mean: {mean_val:.0f}")
    print(f"Median: {median_val:.0f}")
    print(f"Mode: {mode_val}")
    print(f"Verify: Mode({mode_val}) < Median({median_val:.0f}) < Mean({mean_val:.0f})")

height_mixture_demo()
connections_stats()
```

### 面试要点

- Part 1: 关键词 "bimodal distribution"，要能解释为什么合并后不是normal
- Part 2: 关键词 "right-skewed"，Mode < Median < Mean
- 准备好在白板上画出distribution的形状
- 被追问时可以讨论log-normal vs power-law的区别

---

## 6. Class Imbalance处理

### 题目描述

在ML项目中遇到class imbalance（类别不平衡），你会怎么处理？

### 最佳解答

**一、Data-level方法**:

1. **Undersample majority class（欠采样多数类）**
   - 适用：数据量大时
   - 风险：可能丢失有用信息
   - 方法：Random undersampling, Tomek links, NearMiss

2. **Oversample minority class（过采样少数类）**
   - 直接复制（risk of overfitting）
   - **SMOTE** (Synthetic Minority Over-sampling Technique): 在少数类样本之间插值生成新样本

$$x_{\text{new}} = x_i + \lambda \cdot (x_j - x_i), \quad \lambda \sim \text{Uniform}(0, 1)$$

3. **Data augmentation**: 对少数类做变换生成新数据

**二、Algorithm-level方法**:

1. **Class weights（类别权重）**: 在loss function中给少数类更高权重

$$L = -\sum_{i} w_{y_i} \cdot y_i \log(\hat{y}_i)$$

2. **Cost-sensitive learning**: 不同类型错误有不同代价
3. **Anomaly detection**: 当正类极少时，转化为异常检测问题

**三、Evaluation方法**:

不要用accuracy！使用:
- **Precision**: $\frac{TP}{TP + FP}$ -- 预测为正的有多少真的是正
- **Recall**: $\frac{TP}{TP + FN}$ -- 真正为正的有多少被找到
- **F1 Score**: $\frac{2 \cdot P \cdot R}{P + R}$
- **AUC-ROC**: 阈值无关的评估
- **PR Curve (Precision-Recall curve)**: 在极端imbalance下比ROC更informative

**四、Ensemble方法**:

- **BalancedBagging**: 每个base learner用balanced subsample训练
- **EasyEnsemble / BalanceCascade**

### 面试要点

- 分data-level、algorithm-level、evaluation三个层面回答
- SMOTE是高频考点，要能解释原理
- 强调不要用accuracy，用precision/recall/F1/AUC
- 提到anomaly detection作为extreme imbalance的替代方案

---

## 7. Sampling from Large Dataset与模型验证

### 题目描述

从一个超大数据集中采样来训练模型。如何验证从sample上训练的模型是好的？

### 最佳解答

**Step 1: 确保样本代表性**

1. **Stratified Sampling（分层采样）**: 对分类变量确保各类别比例一致
2. **Distribution Check**: 检查关键特征的分布
   - 直方图对比
   - KS test (Kolmogorov-Smirnov test): 检验两个分布是否相同
   - 比较mean, median, std

$$D = \sup_x |F_{\text{sample}}(x) - F_{\text{full}}(x)|$$

3. **Sample size**: 确保样本量足够大，power analysis可以帮助确定

**Step 2: 模型验证**

1. **Hold-out validation from full data**: 从完整数据中留出10%作为test set（在采样之前）
2. **Train on sample, evaluate on full holdout**: 确保模型泛化到全量数据
3. **Cross-validation on sample**: 在样本内做k-fold CV
4. **Bootstrap stability check**: 在多个bootstrap样本上训练，检查性能方差

$$\text{Var}(\hat{\theta}) \approx \frac{1}{B-1}\sum_{b=1}^{B}(\hat{\theta}_b - \bar{\hat{\theta}})^2$$

如果方差大，说明模型对采样敏感，需要更大样本。

**Step 3: 逐步扩大验证**

- 先在1%数据上训练，然后5%, 10%, 50%
- 画learning curve: 性能 vs 样本量
- 如果曲线plateaued，说明样本量足够

### 面试要点

- 核心: "sample representativeness" + "out-of-sample validation"
- KS test是验证分布一致性的标准工具
- 一定要提到hold-out set来自full data而非sample
- Bootstrap检查模型稳定性是加分项

---

## 8. Overfitting Prevention (Tree-based Models)

### 题目描述

使用tree-based model时，如何防止overfitting？

### 最佳解答

**一、单棵树的正则化**:

1. **限制树的深度 (max_depth)**: 减少树的复杂度
2. **最小叶节点样本数 (min_samples_leaf)**: 叶节点必须有足够样本
3. **最小分裂样本数 (min_samples_split)**: 节点样本数低于阈值不再分裂
4. **剪枝 (Pruning)**:
   - Pre-pruning: 提前停止生长
   - Post-pruning (Cost-complexity pruning): 先生长到full depth，再从底部剪枝

$$R_\alpha(T) = R(T) + \alpha |T|$$

其中 $R(T)$ 是训练误差，$|T|$ 是叶节点数，$\alpha$ 是正则化参数。

**二、Ensemble方法**:

1. **Random Forest**: Bagging + Feature subsampling降低variance
2. **Gradient Boosting (XGBoost/LightGBM)**:
   - Learning rate (shrinkage): 每棵树的贡献缩小
   - Subsampling: 每轮只用部分数据
   - L1/L2 regularization on leaf weights
   - **Early stopping**: 验证集性能不再提升时停止

**三、通用方法**:

1. **Cross-validation**: k-fold CV选择最优超参数
2. **Feature engineering**: 减少噪声特征
3. **增加数据量**: 更多数据自然减少overfitting

### 面试要点

- 至少提到3-4种方法，覆盖单树和ensemble两个层面
- 理解pre-pruning和post-pruning的区别
- Boosting + early stopping是最实用的组合
- 面试中可以结合具体参数名解释（sklearn的参数名）

---

## 9. L1/L2 Regularization与Bias

### 题目描述

为什么L1/L2 regularization不是unbiased estimator？

### 最佳解答

**核心结论: L1/L2 regularization引入bias，但降低variance，是经典的bias-variance tradeoff。**

**无正则化的OLS（Ordinary Least Squares）**:

$$\hat{\beta}_{\text{OLS}} = (X^TX)^{-1}X^Ty$$

OLS是unbiased: $E[\hat{\beta}_{\text{OLS}}] = \beta_{\text{true}}$

**L2 Regularization (Ridge)**:

$$\hat{\beta}_{\text{Ridge}} = (X^TX + \lambda I)^{-1}X^Ty$$

$$E[\hat{\beta}_{\text{Ridge}}] = (X^TX + \lambda I)^{-1}X^TX \cdot \beta_{\text{true}} \neq \beta_{\text{true}}$$

Ridge estimator **系统性地将系数向零收缩（shrink toward zero）**，所以是biased的。

**L1 Regularization (Lasso)**:

$$\hat{\beta}_{\text{Lasso}} = \arg\min_\beta \|y - X\beta\|_2^2 + \lambda\|\beta\|_1$$

Lasso不仅shrink，还进行feature selection（将某些系数精确压到0）。也是biased的。

**为什么要引入bias？**

$$\text{MSE} = \text{Bias}^2 + \text{Variance}$$

- OLS: 无bias，但可能有很高的variance（特别是feature多、数据少时）
- Ridge/Lasso: 引入少量bias，大幅降低variance
- 总MSE可能降低 -- 这是正则化的价值所在

**James-Stein现象**: 当维度 $p \geq 3$ 时，biased shrinkage estimator的MSE严格小于OLS。

### 面试要点

- 核心: 正则化通过向零收缩引入bias，换取更低的variance
- 能写出Ridge的闭式解并推导bias
- 提及bias-variance tradeoff
- L1的额外特性: sparsity / feature selection
- James-Stein estimator是高级加分项

---

## 10. Random Forest Theory

### 题目描述

1. 什么是Random Forest？主要参数有哪些？
2. 和Boosting有什么区别？
3. 如何防止overfitting？
4. 相对于其他模型有什么优劣势？

### 最佳解答

**一、Random Forest定义**

Random Forest = **Bagging** + **Random Feature Subsampling**

每棵树独立训练:
1. 从训练集中Bootstrap sampling（有放回抽样）得到子数据集
2. 每次split时，从全部 $p$ 个特征中随机选 $m$ 个特征（通常分类 $m=\sqrt{p}$，回归 $m=p/3$）
3. 在选定的 $m$ 个特征中找最优split
4. 预测时取所有树的平均（回归）或投票（分类）

**主要参数**:
- `n_estimators`: 树的数量
- `max_features`: 每次split考虑的特征数（控制 $\rho$）
- `max_depth`: 树的最大深度
- `min_samples_split` / `min_samples_leaf`: 节点分裂条件
- `bootstrap`: 是否使用bootstrap sampling

**二、Random Forest vs Boosting**

| 维度 | Random Forest | Boosting (XGBoost/LightGBM) |
|------|--------------|----------------------------|
| 训练方式 | 并行（independent trees） | 串行（sequential, 每棵树修正前一棵的残差） |
| 主要降低 | Variance | Bias（也降低variance） |
| Overfitting风险 | 低（增加树数不会overfit） | 高（树太多会overfit，需要early stopping） |
| 解释性 | Feature importance | Feature importance + SHAP |
| 计算效率 | 可并行化 | 必须串行 |

**三、防止Overfitting（RF特有）**

- 增加 `n_estimators`（更多树 = 更低variance，不会overfit）
- 减小 `max_features`（降低树间correlation $\rho$）
- 使用OOB (Out-of-Bag) error估计泛化误差
- 限制 `max_depth`

**四、优劣势**

| 优势 | 劣势 |
|------|------|
| 不容易overfit | 对高维稀疏数据不如Boosting |
| 可并行训练 | 内存消耗大（存储多棵完整树） |
| 天然给出feature importance | 预测速度慢于单棵树 |
| 对异常值和缺失值鲁棒 | 不擅长外推（extrapolation） |
| 不需要特征缩放 | 大数据集上不如Boosting精度高 |

### 面试要点

- 核心: Bagging + Feature subsampling
- 联系到第2题的variance公式: $\rho\sigma^2 + \frac{(1-\rho)\sigma^2}{N}$
- 明确RF降低variance，Boosting降低bias
- OOB error是RF的独特优势，不需要额外validation set

---

## 11. MLE for Distribution Parameters (Normal, GMM, EM)

### 题目描述

1. 给一堆数据点，怎么推算distribution的parameters？
2. 对于Normal distribution，推导MLE求 $\mu$ 和 $\sigma$
3. 对于Gaussian Mixture Model (GMM)，为什么不能直接用MLE？
4. 什么是EM algorithm？简述原理。

### 最佳解答

**一、Maximum Likelihood Estimation (MLE)**

给定数据 $x_1, x_2, \ldots, x_n$，假设来自分布 $f(x|\theta)$:

$$L(\theta) = \prod_{i=1}^n f(x_i|\theta)$$

取对数:

$$\ell(\theta) = \sum_{i=1}^n \log f(x_i|\theta)$$

求解: $\frac{\partial \ell}{\partial \theta} = 0$

**二、Normal Distribution的MLE**

$$f(x|\mu, \sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

Log-likelihood:

$$\ell(\mu, \sigma^2) = -\frac{n}{2}\log(2\pi) - \frac{n}{2}\log(\sigma^2) - \frac{1}{2\sigma^2}\sum_{i=1}^n(x_i - \mu)^2$$

对 $\mu$ 求导令为0:

$$\frac{\partial \ell}{\partial \mu} = \frac{1}{\sigma^2}\sum_{i=1}^n(x_i - \mu) = 0 \implies \hat{\mu}_{\text{MLE}} = \frac{1}{n}\sum_{i=1}^n x_i = \bar{x}$$

对 $\sigma^2$ 求导令为0:

$$\frac{\partial \ell}{\partial \sigma^2} = -\frac{n}{2\sigma^2} + \frac{1}{2\sigma^4}\sum_{i=1}^n(x_i - \mu)^2 = 0 \implies \hat{\sigma}^2_{\text{MLE}} = \frac{1}{n}\sum_{i=1}^n(x_i - \bar{x})^2$$

注意: MLE的 $\hat{\sigma}^2$ 除以 $n$ 而非 $n-1$，是biased estimator。无偏估计除以 $n-1$。

**三、为什么GMM不能直接用MLE？**

GMM的概率密度:

$$f(x) = \sum_{k=1}^K \pi_k \cdot \mathcal{N}(x|\mu_k, \sigma_k^2)$$

对数似然:

$$\ell = \sum_{i=1}^n \log\left(\sum_{k=1}^K \pi_k \cdot \mathcal{N}(x_i|\mu_k, \sigma_k^2)\right)$$

**问题**: $\log$ 里面有求和（log-sum），无法像单个Normal那样简化。对参数求导后得到的方程组**没有闭式解**（non-linear coupled equations）。

**四、EM Algorithm（期望最大化）**

EM是解决这类latent variable问题的迭代算法:

**E-Step (Expectation)**: 固定参数，计算每个数据点属于第 $k$ 个component的后验概率（responsibility）:

$$\gamma_{ik} = \frac{\pi_k \cdot \mathcal{N}(x_i|\mu_k, \sigma_k^2)}{\sum_{j=1}^K \pi_j \cdot \mathcal{N}(x_i|\mu_j, \sigma_j^2)}$$

**M-Step (Maximization)**: 固定responsibilities，更新参数:

$$\mu_k = \frac{\sum_i \gamma_{ik} x_i}{\sum_i \gamma_{ik}}, \quad \sigma_k^2 = \frac{\sum_i \gamma_{ik}(x_i - \mu_k)^2}{\sum_i \gamma_{ik}}, \quad \pi_k = \frac{\sum_i \gamma_{ik}}{n}$$

重复E-M步骤直到收敛（log-likelihood不再显著增加）。

**EM保证**: 每次迭代log-likelihood单调不减，但可能收敛到local maximum。

### Python代码

```python
import numpy as np
from typing import Tuple

def mle_normal(data: np.ndarray) -> Tuple[float, float]:
    """MLE for normal distribution parameters."""
    mu_hat = data.mean()
    sigma2_hat = ((data - mu_hat) ** 2).mean()
    return mu_hat, sigma2_hat

def em_gmm(
    data: np.ndarray, k: int = 2, max_iter: int = 100, tol: float = 1e-6
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """EM algorithm for Gaussian Mixture Model."""
    n = len(data)
    rng = np.random.default_rng(42)
    mu = rng.choice(data, k, replace=False)
    sigma2 = np.ones(k) * data.var()
    pi = np.ones(k) / k

    for iteration in range(max_iter):
        # E-step
        gamma = np.zeros((n, k))
        for j in range(k):
            gamma[:, j] = pi[j] * _normal_pdf(data, mu[j], sigma2[j])
        gamma /= gamma.sum(axis=1, keepdims=True)

        # M-step
        nk = gamma.sum(axis=0)
        mu_new = (gamma * data[:, None]).sum(axis=0) / nk
        sigma2_new = np.array([
            (gamma[:, j] * (data - mu_new[j])**2).sum() / nk[j]
            for j in range(k)
        ])
        pi_new = nk / n

        if np.max(np.abs(mu_new - mu)) < tol:
            break
        mu, sigma2, pi = mu_new, sigma2_new, pi_new

    return mu, sigma2, pi

def _normal_pdf(x: np.ndarray, mu: float, sigma2: float) -> np.ndarray:
    """Compute normal PDF."""
    return np.exp(-0.5 * (x - mu)**2 / sigma2) / np.sqrt(2 * np.pi * sigma2)
```

### 面试要点

- MLE推导要流畅，特别是对 $\mu$ 和 $\sigma^2$ 的求导
- 注意MLE的 $\hat{\sigma}^2$ 是biased的（除以n不是n-1）
- GMM不能直接MLE的原因: log里面有sum
- EM的两步要清楚: E-step算responsibility, M-step更新参数
- 强调EM收敛到local maximum，可以多次random initialization

---

## 12. Reservoir Sampling (Infinite Stream)

### 题目描述

在一个无限数据流中做随机采样。你需要从stream中均匀地采样k个元素，但你不知道总元素数量n。请用Python实现。

### 最佳解答

**Reservoir Sampling (Vitter's Algorithm R)**

**核心思想**: 维护一个大小为k的reservoir。对于第i个元素（$i > k$），以概率 $\frac{k}{i}$ 替换reservoir中的随机一个元素。

**数学证明**: 对于任意元素 $j$（$j \leq n$），在处理完所有n个元素后，该元素在reservoir中的概率:

$$P(\text{item } j \text{ in reservoir}) = \frac{k}{n}$$

**证明sketch**（对第 $j$ 个元素，$j \leq k$时显然在reservoir中；对$j > k$）:

- 元素 $j$ 被选入reservoir的概率: $\frac{k}{j}$
- 元素 $j$ 不被后续元素替换的概率:

$$\prod_{i=j+1}^{n}\left(1 - \frac{k}{i} \cdot \frac{1}{k}\right) = \prod_{i=j+1}^{n}\frac{i-1}{i} = \frac{j}{n}$$

- 总概率: $\frac{k}{j} \cdot \frac{j}{n} = \frac{k}{n}$

### Python代码

```python
import random
from typing import Iterator, List, TypeVar

T = TypeVar("T")

def reservoir_sampling(stream: Iterator[T], k: int) -> List[T]:
    """Sample k items uniformly from a stream of unknown length."""
    reservoir: List[T] = []

    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item

    return reservoir

# 验证均匀性
def verify_uniformity() -> None:
    """Verify each element has equal probability of being sampled."""
    from collections import Counter
    k = 5
    n = 100
    trials = 100000
    counts: Counter = Counter()

    for _ in range(trials):
        result = reservoir_sampling(iter(range(n)), k)
        counts.update(result)

    expected = k / n * trials
    values = list(counts.values())
    print(f"Expected count per element: {expected:.0f}")
    print(f"Actual range: [{min(values)}, {max(values)}]")
    print(f"Mean: {sum(values)/len(values):.0f}")

verify_uniformity()
```

### 面试要点

- 核心: 第i个元素以概率 $\frac{k}{i}$ 被选中
- 能快速写出代码（10行以内的核心逻辑）
- 能sketch概率证明
- Follow-up: 分布式reservoir sampling（多台机器各自维护reservoir，最后合并）

---

## 13. Biased Coin to Uniform Random (0-6)

### 题目描述

给一个不平衡的0-1随机函数（$P(1) = p$, $P(0) = 1-p$, $p \neq 0.5$），用它生成均匀分布的0-6随机数。

### 最佳解答

**分两步**:

**Step 1: Biased coin -> Fair coin (Von Neumann's trick)**

抛两次biased coin:
- (0, 1): 输出0，概率 = $p(1-p)$
- (1, 0): 输出1，概率 = $(1-p)p$
- (0, 0) 或 (1, 1): 丢弃，重来

由于 $P(0,1) = P(1,0) = p(1-p)$，输出0和1的概率相等 = 0.5。

**期望抛硬币次数**: 每次成功概率 = $2p(1-p)$，期望次数 = $\frac{2}{2p(1-p)} = \frac{1}{p(1-p)}$

**Step 2: Fair coin -> Uniform [0, 6]**

需要生成7个等概率结果。$7 < 2^3 = 8$，所以用3个fair coin bits:

- 生成3位二进制数，范围 [0, 7]
- 如果结果是0-6，接受
- 如果结果是7，重新生成

接受概率 = $\frac{7}{8}$，期望重试次数 = $\frac{8}{7} \approx 1.14$

### Python代码

```python
import random
from typing import Callable

def biased_coin(p: float = 0.7) -> int:
    """Simulate a biased coin with P(1) = p."""
    return 1 if random.random() < p else 0

def fair_from_biased(biased: Callable[[], int]) -> int:
    """Von Neumann trick: convert biased coin to fair coin."""
    while True:
        a, b = biased(), biased()
        if a == 0 and b == 1:
            return 0
        if a == 1 and b == 0:
            return 1

def uniform_0_to_6(biased: Callable[[], int]) -> int:
    """Generate uniform random integer in [0, 6] from biased coin."""
    while True:
        bits = [fair_from_biased(biased) for _ in range(3)]
        value = bits[0] * 4 + bits[1] * 2 + bits[2]
        if value <= 6:
            return value

# 验证
from collections import Counter
counts = Counter(uniform_0_to_6(biased_coin) for _ in range(70000))
for k in sorted(counts):
    print(f"{k}: {counts[k]/70000:.3f} (expected 0.143)")
```

### 面试要点

- 分两步走: biased -> fair -> uniform，不要试图一步到位
- Von Neumann's trick是核心，必须理解为什么(01)和(10)概率相等
- 解释rejection sampling的效率: 期望次数是有限的
- Follow-up: 如何优化？可以一次生成更多bits减少浪费

---

## 14. Linear vs Logistic Regression数学等价性

### 题目描述

Linear regression和logistic regression为何在数学上可以被看作"同一个模型"？

### 最佳解答

**核心思想: 两者都是Generalized Linear Model (GLM)的特例。**

**GLM框架**:

$$g(E[Y|X]) = X\beta$$

其中 $g(\cdot)$ 是link function。

**Linear Regression**:
- 假设: $Y \sim \text{Normal}(\mu, \sigma^2)$
- Link function: Identity, $g(\mu) = \mu$
- 即: $E[Y|X] = X\beta$

**Logistic Regression**:
- 假设: $Y \sim \text{Bernoulli}(p)$
- Link function: Logit, $g(p) = \log\frac{p}{1-p}$
- 即: $\log\frac{P(Y=1|X)}{P(Y=0|X)} = X\beta$

**数学等价性**:

两者的核心都是:
1. **Linear predictor**: $\eta = X\beta$（线性组合特征）
2. **通过link function映射到响应变量的期望**
3. **参数估计都通过最大化likelihood**

区别仅在于:
- 响应变量的分布假设（Normal vs Bernoulli）
- Link function（identity vs logit）
- 估计方法（OLS有闭式解 vs logistic需要迭代优化如Newton-Raphson）

**更深层的联系**:

如果把logistic regression写成:

$$P(Y=1|X) = \sigma(X\beta)$$

其中 $\sigma(z) = \frac{1}{1+e^{-z}}$ 是sigmoid函数。

而linear regression是:

$$E[Y|X] = f(X\beta) = X\beta$$

其中 $f$ 是identity function。

两者都是 "apply a function to a linear combination of features" 的形式。

### 面试要点

- 关键词: GLM (Generalized Linear Model)
- 能清楚说出两者的link function区别
- 强调共同点: linear predictor $X\beta$
- 如果被追问multiclass: Logistic Regression可以通过One-vs-Rest或Softmax扩展
- 这是LinkedIn面经中的surprise question，准备好不常见的角度

---

## 附录: 高频考点速查表

| 主题 | 关键公式/概念 | 出现频率 |
|------|-------------|---------|
| Weighted Sampling | Inverse CDF + Binary Search, $O(\log N)$ | High |
| E[X_bar], Var[X_bar] | $\frac{\sigma^2}{N}[1+(N-1)\rho]$ + RF联系 | Very High |
| Simpson's Paradox | Confounding variable, stratified analysis | High |
| Queueing Theory | Same mean, lower variance (single queue) | Medium |
| Distributions | Bimodal (height), Right-skewed (connections) | Medium |
| Class Imbalance | SMOTE, class weights, precision/recall | Medium |
| MLE + EM | Normal MLE推导, GMM需要EM | High |
| Reservoir Sampling | $P(k/i)$ replacement, Vitter's Algorithm R | Medium |
| Biased -> Fair Coin | Von Neumann's trick | Low-Medium |

---

*本文档整理自一亩三分地LinkedIn面经，覆盖了Phone Screen和Onsite ML Fundamentals轮次中出现的所有概率统计题目。建议结合白板练习公式推导和代码书写。*
