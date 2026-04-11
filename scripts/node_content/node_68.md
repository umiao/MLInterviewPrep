# Loss Functions（损失函数）

## Overview

**Loss Functions（损失函数）** 量化了模型预测与真实目标之间的差异。选择正确的损失函数至关重要——它定义了模型优化的目标。面试中常考的问题包括：为什么使用特定的损失函数、它们的梯度特性，以及对异常值的鲁棒性。

每种损失函数背后都隐含着一个概率分布假设：**MSE（Mean Squared Error，均方误差）** 假设高斯噪声，**MAE（Mean Absolute Error，平均绝对误差）** 假设拉普拉斯噪声，**Cross-Entropy（交叉熵）** 来源于最大似然估计。理解这种联系有助于根据数据特性选择合适的损失函数。

## Core Concepts

### Regression Losses（回归损失）

#### MSE / L2 Loss（均方误差）

$$\mathcal{L}_{\text{MSE}} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2$$

**梯度**：$\frac{\partial \mathcal{L}}{\partial \hat{y}_i} = -\frac{2}{n}(y_i - \hat{y}_i)$

梯度大小与误差成正比，误差越大梯度越大。这意味着MSE对 **Outliers（异常值）** 非常敏感——一个异常点的平方误差可以主导整个损失。

**概率解释**：最小化MSE等价于在高斯噪声假设下的 **MLE（Maximum Likelihood Estimation，最大似然估计）**：$p(y|x) = \mathcal{N}(\hat{y}, \sigma^2)$

**优点**：处处可微，梯度平滑，收敛稳定
**缺点**：对异常值敏感，可能导致模型被少数极端样本主导

#### MAE / L1 Loss（平均绝对误差）

$$\mathcal{L}_{\text{MAE}} = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$$

**梯度**：$\frac{\partial \mathcal{L}}{\partial \hat{y}_i} = -\frac{1}{n}\text{sgn}(y_i - \hat{y}_i)$

梯度大小恒为常数（$\pm 1/n$），不受误差大小影响。对异常值鲁棒，但在零点处不可微。

**概率解释**：最小化MAE等价于在拉普拉斯噪声假设下的MLE：$p(y|x) = \text{Laplace}(\hat{y}, b)$

**优点**：对异常值鲁棒，预测的是条件中位数
**缺点**：零点不可微（实际中用 **Subgradient，次梯度** 处理），梯度不平滑可能导致收敛不稳定

#### Huber Loss（Huber损失）

综合了MSE和MAE的优点——小误差时二次惩罚，大误差时线性惩罚：

$$L_\delta(r) = \begin{cases} \frac{1}{2}r^2 & \text{if } |r| \leq \delta \\ \delta(|r| - \frac{1}{2}\delta) & \text{otherwise} \end{cases}$$

**梯度**：

$$\frac{\partial L_\delta}{\partial r} = \begin{cases} r & \text{if } |r| \leq \delta \\ \delta \cdot \text{sgn}(r) & \text{otherwise} \end{cases}$$

参数 $\delta$ 控制MSE和MAE之间的过渡点：$\delta \to 0$ 趋近MAE，$\delta \to \infty$ 趋近MSE。处处可微且对异常值鲁棒。

#### Log-Cosh Loss

$$\mathcal{L} = \frac{1}{n}\sum_{i=1}^{n}\log(\cosh(y_i - \hat{y}_i))$$

类似Huber Loss但处处二阶可微。小误差时近似 $\frac{r^2}{2}$，大误差时近似 $|r| - \log 2$。适用于需要二阶导数的优化方法（如Newton方法）。

#### Quantile Loss（分位数损失）

$$L_\tau(r) = \begin{cases} \tau \cdot r & \text{if } r \geq 0 \\ (\tau - 1) \cdot r & \text{if } r < 0 \end{cases}$$

当 $\tau = 0.5$ 时等价于MAE。不同的 $\tau$ 值可以估计条件分布的不同分位数，用于构建 **Prediction Intervals（预测区间）**。LightGBM和XGBoost都支持分位数回归。

### Classification Losses（分类损失）

#### Binary Cross-Entropy / Log Loss（二元交叉熵）

$$\mathcal{L}_{\text{BCE}} = -\frac{1}{n}\sum_{i}[y_i\log(\hat{p}_i) + (1-y_i)\log(1-\hat{p}_i)]$$

**梯度**（对logit $z$ 求导，其中 $\hat{p} = \sigma(z)$）：

$$\frac{\partial \mathcal{L}}{\partial z_i} = \hat{p}_i - y_i$$

梯度简洁优美：预测概率与真实标签之差。这也是为什么 **Logistic Regression（逻辑回归）** 使用交叉熵而非MSE的原因——MSE对sigmoid输出求导会产生 $\hat{p}(1-\hat{p})$ 因子，在 $\hat{p}$ 接近0或1时梯度消失。

**信息论解释**：交叉熵 $H(p, q) = -\sum p\log q$ 度量了用分布 $q$ 编码来自分布 $p$ 的数据所需的额外比特数。最小化交叉熵等价于最小化 **KL Divergence（KL散度，Kullback-Leibler Divergence）**。

#### Multi-class Cross-Entropy（多类交叉熵）

$$\mathcal{L}_{\text{CE}} = -\frac{1}{n}\sum_{i=1}^{n}\sum_{c=1}^{C}y_{ic}\log(\hat{p}_{ic})$$

其中 $\hat{p}_{ic}$ 由 **Softmax（归一化指数函数）** 计算：$\hat{p}_{ic} = \frac{e^{z_{ic}}}{\sum_{j=1}^{C}e^{z_{ij}}}$

#### Focal Loss（焦点损失）

$$\mathcal{L}_{\text{focal}} = -\alpha_t(1 - p_t)^\gamma \log(p_t)$$

由 **Lin et al. (2017)** 在 **RetinaNet** 论文中提出，专门解决目标检测中的严重类别不平衡问题。

**核心思想**：通过 $(1-p_t)^\gamma$ 因子降低 **Easy Examples（简单样本）** 的损失权重，使模型聚焦于 **Hard Examples（困难样本）**。

$$\text{当 } p_t = 0.9, \gamma = 2: \quad (1-0.9)^2 = 0.01 \text{（损失降低100倍）}$$
$$\text{当 } p_t = 0.1, \gamma = 2: \quad (1-0.1)^2 = 0.81 \text{（损失几乎不变）}$$

参数设置：$\gamma = 2, \alpha = 0.25$ 是最常用的默认值。$\gamma = 0$ 时退化为标准交叉熵。

#### Hinge Loss（合页损失）

$$\mathcal{L}_{\text{hinge}} = \frac{1}{n}\sum_i \max(0, 1 - y_i \cdot f(x_i)), \quad y_i \in \{-1, +1\}$$

**梯度**：

$$\frac{\partial \mathcal{L}}{\partial f} = \begin{cases} 0 & \text{if } y_i \cdot f(x_i) \geq 1 \\ -y_i & \text{otherwise} \end{cases}$$

当分类正确且间隔足够大 ($yf(x) \geq 1$) 时梯度为零——这产生了 **SVM（Support Vector Machine，支持向量机）** 的稀疏性：只有支持向量（间隔边界上或内的样本）有非零梯度。

**Squared Hinge Loss（平方合页损失）**：$\max(0, 1-yf(x))^2$，处处可微，对严重违反间隔的样本惩罚更重。

### Information-Theoretic Losses（信息论损失）

#### KL Divergence（KL散度）

$$D_{KL}(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)}$$

度量分布 $Q$ 相对于分布 $P$ 的信息损失。注意KL散度不对称：$D_{KL}(P\|Q) \neq D_{KL}(Q\|P)$。

**应用场景**：
- **Knowledge Distillation（知识蒸馏）**：学生网络拟合教师网络的软标签
- **VAE（Variational Autoencoder，变分自编码器）**：正则化潜在分布趋近标准正态
- **Policy Gradient（策略梯度）**：PPO中限制策略更新幅度

$$\mathcal{L}_{\text{VAE}} = \text{Reconstruction Loss} + D_{KL}(q(z|x) \| p(z))$$

#### Jensen-Shannon Divergence（JS散度）

$$D_{JS}(P \| Q) = \frac{1}{2}D_{KL}(P \| M) + \frac{1}{2}D_{KL}(Q \| M), \quad M = \frac{P+Q}{2}$$

对称且有界（$0 \leq D_{JS} \leq \log 2$），是 **GAN（Generative Adversarial Network，生成对抗网络）** 原始目标函数的理论基础。

### Ranking Losses（排序损失）

#### Contrastive Loss（对比损失）

$$\mathcal{L} = (1-y)\frac{1}{2}d^2 + y\frac{1}{2}\max(0, m-d)^2$$

其中 $d = \|f(x_1) - f(x_2)\|$，$y=0$ 表示相似对，$y=1$ 表示不相似对，$m$ 是间隔。用于 **Siamese Networks（孪生网络）** 的度量学习。

#### Triplet Loss（三元组损失）

$$\mathcal{L} = \max(0, d(a, p) - d(a, n) + m)$$

其中 $a$ 是 **Anchor（锚点）**，$p$ 是 **Positive（正样本）**，$n$ 是 **Negative（负样本）**，$m$ 是间隔。目标是让锚点与正样本的距离小于与负样本的距离至少 $m$。

**Hard Negative Mining（困难负样本挖掘）** 对三元组损失至关重要：选择距离锚点最近的负样本可以显著加速收敛。

#### Pairwise BPR Loss（贝叶斯个性化排序损失）

$$\mathcal{L}_{\text{BPR}} = -\sum_{(i,j)} \log \sigma(f(x_i) - f(x_j))$$

其中物品 $i$ 优于物品 $j$。广泛用于推荐系统的隐式反馈场景。

#### Listwise Losses（列表级损失）

**ListNet** 使用top-1概率分布的交叉熵，**LambdaRank** 直接优化 **NDCG（Normalized Discounted Cumulative Gain，归一化折损累计增益）** 的近似梯度。

### Loss Function Summary Table（损失函数总结表）

| 损失函数 | 任务 | 异常值鲁棒 | 可微 | 概率解释 | 梯度特性 |
|---------|------|-----------|------|---------|---------|
| MSE | 回归 | 否 | 是 | 高斯分布 | 与误差成正比 |
| MAE | 回归 | 是 | 否（零点） | 拉普拉斯分布 | 恒定大小 |
| Huber | 回归 | 是 | 是 | 近似 | 小误差正比，大误差恒定 |
| Log-Cosh | 回归 | 是 | 是（二阶也可微） | 近似 | 平滑过渡 |
| Cross-Entropy | 分类 | N/A | 是 | 伯努利/多项式 | $\hat{p} - y$ |
| Hinge | 分类 | N/A | 否（1处） | 否 | 间隔外为零 |
| Focal | 分类 | N/A | 是 | 否 | 降低简单样本权重 |
| KL散度 | 分布匹配 | N/A | 是 | 信息论 | 不对称 |

## Implementation

```python
import numpy as np
import torch
import torch.nn.functional as F

# Huber Loss
def huber_loss(y_true, y_pred, delta=1.0):
    r = y_true - y_pred
    return np.where(np.abs(r) <= delta,
                    0.5 * r**2,
                    delta * (np.abs(r) - 0.5 * delta))

# Focal Loss (PyTorch)
def focal_loss(logits, targets, gamma=2.0, alpha=0.25):
    probs = torch.sigmoid(logits)
    p_t = torch.where(targets == 1, probs, 1 - probs)
    alpha_t = torch.where(targets == 1, alpha, 1 - alpha)
    loss = -alpha_t * (1 - p_t)**gamma * torch.log(p_t + 1e-8)
    return loss.mean()

# Triplet Loss
def triplet_loss(anchor, positive, negative, margin=1.0):
    d_pos = F.pairwise_distance(anchor, positive)
    d_neg = F.pairwise_distance(anchor, negative)
    loss = F.relu(d_pos - d_neg + margin)
    return loss.mean()

# Label Smoothing Cross-Entropy
def label_smoothing_ce(logits, targets, n_classes, epsilon=0.1):
    log_probs = F.log_softmax(logits, dim=-1)
    targets_one_hot = F.one_hot(targets, n_classes).float()
    targets_smooth = (1 - epsilon) * targets_one_hot + epsilon / n_classes
    return -(targets_smooth * log_probs).sum(dim=-1).mean()
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| MSE vs. MAE | 异常值问题 | MSE对大误差二次惩罚；MAE线性惩罚 |
| 交叉熵 vs. MSE | "为什么分类不用MSE？" | MSE对sigmoid输出有梯度消失问题 |
| Focal Loss | 严重类别不平衡 | 降低已正确分类样本的损失贡献 |
| 自定义损失 | 业务优化 | 根据业务指标定义损失（如不对称成本） |
| 损失函数的概率解释 | 理论深度 | MSE=高斯，MAE=拉普拉斯，CE=MLE |
| 排序损失选择 | 推荐/搜索 | 点级(CE) vs 对级(BPR) vs 列表级(LambdaRank) |

### Common Interview Questions

- **为什么分类不用MSE？** sigmoid的MSE梯度含 $\hat{p}(1-\hat{p})$ 因子，$\hat{p}$ 接近0或1时梯度消失；交叉熵梯度 $\hat{p}-y$ 无此问题
- **推导BCE的梯度？** 对logit $z$ 求导：$\frac{\partial}{\partial z}[-y\log\sigma(z)-(1-y)\log(1-\sigma(z))] = \sigma(z)-y$
- **何时用Huber而非MSE？** 数据含异常值但仍需平滑梯度时（Huber处处可微，MAE不是）
- **Focal Loss如何解决类别不平衡？** $(1-p_t)^\gamma$ 因子使模型忽略已能正确分类的简单样本，聚焦于困难样本
- **设计一个FN成本是FP的10倍的损失函数？** 加权交叉熵：正类权重设为10，或等价地将阈值从0.5降低
- **KL散度为什么不对称？** $D_{KL}(P\|Q)$ 度量用 $Q$ 近似 $P$ 的信息损失；反向度量不同

## Key Takeaways

- 每种损失函数隐含概率假设：MSE = 高斯噪声，MAE = 拉普拉斯噪声
- 交叉熵是分类的标准选择——它提供正确的概率校准，梯度性质优良
- Huber损失：小误差二次，大误差线性——异常值存在且需要平滑梯度时使用
- Focal Loss：$\gamma$ 控制对简单样本的降权程度；目标检测任务的关键
- 面试中需要熟知MSE、交叉熵和Hinge Loss的梯度推导
- 排序场景中：点级损失最简单，对级和列表级损失更直接优化排序指标
- 自定义损失函数时：确保可微（或有良好的次梯度），注意数值稳定性（$\log$ 加 $\epsilon$）
