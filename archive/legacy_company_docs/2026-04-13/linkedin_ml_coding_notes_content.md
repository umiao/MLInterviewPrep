# LinkedIn ML Fundamentals + Coding 面试准备笔记 (一亩三分地面经整理)

---

## 目录

1. [ANN Deep Dive — 激活函数、Loss Function、Adam Optimizer](#1-ann-deep-dive)
2. [Logistic Regression 深入](#2-logistic-regression-深入)
3. [Gradient Descent — Batch GD vs SGD vs Mini-batch](#3-gradient-descent)
4. [Overfitting / Underfitting — L1 vs L2 正则化](#4-overfitting--underfitting)
5. [Decision Tree — Leaf Node 输出与 Overfitting 分析](#5-decision-tree)
6. [Random Forest 详解](#6-random-forest-详解)
7. [MLE 推导 — Normal Distribution 与 GMM/EM](#7-mle-推导)
8. [K-means 实现与停止条件 (重点!)](#8-k-means-实现与停止条件)
9. [Sparse Vector / Matrix Multiplication](#9-sparse-vector--matrix-multiplication)
10. [Stratified Sampling 实现](#10-stratified-sampling-实现)
11. [LRU Cache + 多线程 Follow-up (Coding with AI)](#11-lru-cache--多线程-follow-up)
12. [Service Dependency — 受影响服务查找 (Coding with AI)](#12-service-dependency--受影响服务查找)

---

## 1. ANN Deep Dive

### 题目描述

面试官从Neural Network的每一层开始逐个深入提问：各种激活函数 (ReLU, sigmoid, SwiGLU, SiLU) 的作用和区别，不同场景下应该用什么loss function，以及Adam optimizer的工作原理。

### 最佳解答

#### 1.1 激活函数对比

| 激活函数 | 公式 | 特点 | 适用场景 |
|---------|------|------|---------|
| **Sigmoid** | $$\sigma(x) = \frac{1}{1+e^{-x}}$$ | 输出 $(0,1)$，有梯度消失问题 | 二分类输出层 |
| **ReLU** | $$f(x) = \max(0, x)$$ | 计算快，缓解梯度消失，但有 dying ReLU 问题 | 隐藏层默认选择 |
| **SiLU (Swish)** | $$f(x) = x \cdot \sigma(x)$$ | 平滑、非单调，允许负值小幅通过 | 现代深度网络 (EfficientNet) |
| **SwiGLU** | $$f(x, W_1, W_2) = \text{SiLU}(xW_1) \odot (xW_2)$$ | GLU门控 + SiLU，两组权重 | LLM (LLaMA, PaLM) |

**关键区别**：
- **ReLU** 是最简单高效的，但负值区域梯度为0 (dying ReLU)
- **SiLU/Swish** 解决了dying ReLU，因为负值区域有小的非零梯度
- **SwiGLU** 在SiLU基础上加了门控机制 (Gated Linear Unit)，让模型自己学习哪些信息通过，性能优于单纯的SiLU，但参数量翻倍

#### 1.2 Loss Function 场景选择

| 场景 | Loss Function | 公式 |
|------|--------------|------|
| 二分类 | Binary Cross-Entropy (BCE) | $$L = -[y\log(\hat{y}) + (1-y)\log(1-\hat{y})]$$ |
| 多分类 | Categorical Cross-Entropy | $$L = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)$$ |
| 回归 | MSE (Mean Squared Error) | $$L = \frac{1}{n}\sum(y - \hat{y})^2$$ |
| 回归 (对outlier鲁棒) | Huber Loss | MSE when small, MAE when large |
| 排序/推荐 | Pairwise Hinge / BPR Loss | 比较正负样本对的相对顺序 |

#### 1.3 Adam Optimizer 原理

Adam = **Ada**ptive **M**oment Estimation，结合了 Momentum 和 RMSProp：

$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t \quad \text{(一阶矩：梯度的指数加权均值)}$$

$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \quad \text{(二阶矩：梯度平方的指数加权均值)}$$

$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t} \quad \text{(Bias correction，因为初始化为0)}$$

$$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$

**为什么要bias correction?** 因为 $m_0 = 0, v_0 = 0$，前几步的估计会偏向0，除以 $(1-\beta^t)$ 来纠正。

**默认超参**: $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$

### 面试要点

- Sigmoid 只在输出层用 (二分类)，隐藏层用ReLU或变体
- SwiGLU 是当前LLM标配，要能解释门控 (gate) 的直觉
- Adam 的核心优势：自适应学习率 + 动量，每个参数有自己的学习率
- 常见follow-up: Adam vs AdamW (weight decay vs L2 regularization 的区别)

---

## 2. Logistic Regression 深入

### 题目描述

1. 为什么Logistic Regression适合binary classification？为什么输出是概率？
2. 常用什么loss function，为什么？
3. Linear Regression 和 Logistic Regression 在数学上为什么是"同一个模型"？(GLM角度)

### 最佳解答

#### 2.1 为什么适合二分类 & 输出是概率

Logistic Regression 对 **log-odds (对数几率)** 做线性建模：

$$\log\frac{p}{1-p} = w^T x + b$$

等价于：

$$p = \sigma(w^T x + b) = \frac{1}{1+e^{-(w^T x + b)}}$$

**为什么输出是概率?**
- Sigmoid 函数将任意实数映射到 $(0,1)$
- 从概率论角度：假设 $P(Y=1|X) = p$，对 log-odds 做线性假设是自然的 (Bernoulli分布的canonical link function)
- 输出满足概率公理：$0 < p < 1$ 且 $P(Y=0) = 1 - P(Y=1)$

#### 2.2 BCE Loss 推导

假设 $y \in \{0,1\}$，似然函数为：

$$P(y|x) = \hat{y}^y (1-\hat{y})^{1-y}$$

对整个数据集取负对数似然 (NLL)：

$$L = -\frac{1}{N}\sum_{i=1}^{N}[y_i\log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)]$$

**为什么用BCE而不用MSE?**
- MSE + sigmoid 导致 loss surface 非凸，有很多局部极小值
- BCE + sigmoid 的 loss surface 是凸的，保证全局最优
- BCE 的梯度更大，收敛更快：$\frac{\partial L}{\partial w} = (\hat{y} - y)x$，不含 sigmoid 导数项

#### 2.3 与 Linear Regression 的关系 (GLM 角度)

**Generalized Linear Model (GLM)** 框架下，两者是同一模型族：

| | Linear Regression | Logistic Regression |
|---|---|---|
| 响应变量分布 | Normal (Gaussian) | Bernoulli |
| Link function | Identity: $\mu = w^Tx$ | Logit: $\log\frac{p}{1-p} = w^Tx$ |
| 输出 | 连续实数 | 概率 $\in (0,1)$ |

GLM 三要素：(1) 指数族分布，(2) 线性预测子 $\eta = w^Tx$，(3) link function 连接 $\eta$ 和分布均值。改变分布假设和link function，就从LR变成LogR。

### 面试要点

- 必须能解释 "为什么输出是概率" — 不只是 "sigmoid输出在0到1之间"，要说 log-odds 的线性假设
- BCE loss 是从 MLE 推导出来的，不是拍脑袋选的
- GLM 角度是高分答案，说明你理解统计学本质
- Follow-up: 多分类怎么办？→ Softmax + Categorical CE (Multinomial Logistic Regression)

---

## 3. Gradient Descent

### 题目描述

Batch GD vs SGD vs Mini-batch GD 有什么区别？Batch size 越大越好吗？从计算效率、收敛速度、gradient noise、泛化能力几个角度分析。

### 最佳解答

#### 3.1 三种变体对比

| | Batch GD | Mini-batch GD | SGD |
|---|---|---|---|
| 每次用多少数据 | 全部 $N$ 个 | $B$ 个 (如32, 64, 256) | 1个 |
| 梯度估计 | $$g = \frac{1}{N}\sum_{i=1}^N \nabla L_i$$ | $$g = \frac{1}{B}\sum_{i=1}^B \nabla L_i$$ | $$g = \nabla L_i$$ |
| 梯度噪声 | 无 (精确梯度) | 中等 | 很大 |
| 每步计算量 | 最大 | 中等 | 最小 |
| 收敛轨迹 | 平滑 | 适度震荡 | 剧烈震荡 |

#### 3.2 Batch Size 影响分析

**计算效率**: 大batch可以更好地利用GPU并行，throughput (samples/sec) 更高。但超过GPU memory上限后无法再增大。

**收敛速度 (steps)**: 大batch每步梯度更准，但 **不一定** 收敛到更好的解。实际上大batch通常需要更多epoch才能达到同样的loss。

**Gradient Noise**: 小batch引入的噪声反而是有益的！
- 噪声帮助跳出sharp minima (尖锐极小值)
- 大batch倾向于收敛到sharp minima → 泛化差

**泛化能力 (Generalization)**:
- **关键发现** (Keskar et al., 2017): 大batch倾向sharp minima，小batch倾向flat minima
- Flat minima 对参数扰动不敏感 → 在测试集上表现更稳定
- 经验法则：batch size 太大会伤害泛化

**Linear Scaling Rule**: 如果batch size乘以 $k$，学习率也要乘以 $k$ (但有上限，太大会不稳定)。

#### 3.3 实际建议

- 默认从 batch_size=32 或 64 开始
- 如果GPU利用率不高，适当增大
- 如果泛化gap大 (train好test差)，减小batch size
- Learning rate warmup 对大batch很重要

### 面试要点

- **不要简单说"大batch好"**，要从多个维度分析
- 必须提到 gradient noise 对泛化的正面作用 (flat vs sharp minima)
- Linear scaling rule 是加分项
- Follow-up: 有没有方法让大batch也能泛化好？→ LARS/LAMB optimizer, learning rate warmup

---

## 4. Overfitting / Underfitting

### 题目描述

1. 什么是overfitting和underfitting？怎么判断？
2. 缓解overfitting的方法有哪些？
3. L1 vs L2 正则化的区别、使用场景、为什么L1产生稀疏解？
4. L1/L2 为什么是 biased estimator？

### 最佳解答

#### 4.1 定义与判断

**Underfitting** (欠拟合): 模型太简单，train loss 和 val loss 都高。
**Overfitting** (过拟合): 模型太复杂，train loss 低但 val loss 高 (大gap)。

**判断方法**: 观察 training curve：
- Train loss 下降但 val loss 开始上升 → overfitting
- Train loss 和 val loss 都很高且接近 → underfitting
- 两者都低且接近 → good fit

#### 4.2 缓解 Overfitting 的方法

1. **更多数据** — 最有效但最贵
2. **数据增强** (Data Augmentation) — 图像翻转、裁剪、文本同义替换
3. **正则化** — L1, L2, Elastic Net
4. **Dropout** — 随机关闭神经元，迫使网络学习冗余表示
5. **Early Stopping** — 在val loss开始上升时停止训练
6. **减小模型复杂度** — 更少的层/参数
7. **Batch Normalization** — 有轻微正则化效果
8. **Ensemble** — Bagging (如Random Forest) 减少variance

#### 4.3 L1 vs L2 正则化

| | L1 (Lasso) | L2 (Ridge) |
|---|---|---|
| 惩罚项 | $$\lambda \sum |w_i|$$ | $$\lambda \sum w_i^2$$ |
| 梯度 | $\lambda \cdot \text{sign}(w)$ (常数大小) | $2\lambda w$ (与 $w$ 成正比) |
| 效果 | 产生 **稀疏解** (部分 $w=0$) | **均匀收缩** 所有 $w$ |
| 适用场景 | 特征选择 (高维数据) | 所有特征都重要时 |

**为什么L1产生稀疏解？(几何直觉)**

L1 约束区域是菱形 (diamond)，L2 约束区域是圆形 (circle)。等高线 (loss contour) 与约束区域的切点：
- **菱形的角** 在坐标轴上 → 切点大概率在轴上 → 某些 $w_i = 0$
- **圆形** 没有角 → 切点几乎不会恰好在轴上 → $w_i \neq 0$ 但接近0

**从梯度角度**: L1的梯度是常数 $\pm\lambda$，即使 $w$ 已经很小了，仍然以恒定速度把 $w$ 往0推。L2的梯度 $2\lambda w$ 随 $w$ 减小而减小，越接近0推力越小，所以只能接近0但不等于0。

#### 4.4 L1/L2 为什么是 Biased Estimator

无正则化的OLS (Ordinary Least Squares) 是无偏估计：$E[\hat{w}_{OLS}] = w_{true}$。

加入正则化后，解变成：

$$\hat{w}_{Ridge} = (X^TX + \lambda I)^{-1}X^Ty$$

这不等于 $(X^TX)^{-1}X^Ty$，所以 $E[\hat{w}_{Ridge}] \neq w_{true}$。

正则化本质上引入了 **bias-variance trade-off**：牺牲一些bias (偏差)，换取更小的variance → 整体MSE可能更低。

### 面试要点

- L1产生稀疏解必须从 **几何** 和 **梯度** 两个角度解释
- Biased estimator 的直觉：正则化 = 人为缩小权重 → 当然偏离真实值
- Elastic Net = L1 + L2 的结合，实践中常用
- Follow-up: Dropout 和 L2 的关系？→ Dropout 近似等价于 L2 正则化 (Wager et al.)

---

## 5. Decision Tree

### 题目描述

1. Decision Tree 的 leaf node 输出一定是 0 或 1 吗？
2. Model A: 每个 leaf node 只有 1 个 sample。Model B: 每个 leaf node 有多个 samples。哪个更容易 overfit？
3. 防止 Decision Tree overfitting 的方法。

### 最佳解答

#### 5.1 Leaf Node 输出

**不一定是 0 或 1！** 取决于树的类型：

- **分类树 (Classification Tree)**: leaf node 输出该节点中**多数类的标签** (如0或1)，但也可以输出**概率** (该节点中各类别的比例)。例如 leaf 中有 8 个正样本、2 个负样本 → 输出概率 0.8 或标签 1。
- **回归树 (Regression Tree)**: leaf node 输出该节点中所有样本的**均值** (连续值)。
- **Gradient Boosting** 中的树: leaf 输出的是 gradient residual，可以是任意实数。

`sklearn` 的 `predict_proba()` 就是返回 leaf node 中各类别的比例作为概率。

#### 5.2 Model A vs Model B Overfit 分析

**Model A (1 sample per leaf) 更容易 overfit！**

- 每个 leaf 只有 1 个样本 → 树完美记住了每个训练样本 → training accuracy = 100%
- 这就是典型的 overfitting：模型记忆了噪声而非学习规律
- 等价于"最近邻"，对新数据泛化能力差

**Model B (多 samples per leaf)** 相当于做了平滑/正则化，leaf 的输出是多个样本的"投票/平均"，噪声被平均掉了。

#### 5.3 防止 Decision Tree Overfit

1. **限制最大深度** (`max_depth`) — 最常用
2. **限制叶节点最少样本数** (`min_samples_leaf`) — 直接防止 Model A 情况
3. **限制分裂最少样本数** (`min_samples_split`)
4. **限制最大叶节点数** (`max_leaf_nodes`)
5. **剪枝 (Pruning)**:
   - Pre-pruning: 在生长过程中提前停止 (上面的限制就是)
   - Post-pruning: 先长完整棵树，再用验证集剪枝 (如 Cost Complexity Pruning / ccp_alpha)
6. **集成方法**: 用 Random Forest / Gradient Boosting 代替单棵树

### 面试要点

- Leaf node 输出不是"一定0或1"，要区分分类/回归/概率输出
- Model A vs B 的题目本质是考 "variance vs bias trade-off"
- 必须知道 pre-pruning vs post-pruning 的区别
- Follow-up: 为什么 Random Forest 不容易 overfit？→ Bagging + feature subsampling 降低 variance

---

## 6. Random Forest 详解

### 题目描述

Random Forest 的原理，bagging 和 feature subsampling 的作用，和 boosting 的区别，优劣势分析。

### 最佳解答

#### 6.1 核心原理

Random Forest = **Bagging** + **Feature Subsampling** + **Decision Trees**

1. **Bootstrap Sampling (Bagging)**: 从 $N$ 个训练样本中有放回采样 $N$ 个，构建 $T$ 棵树，每棵树的训练集不同
2. **Feature Subsampling**: 每次分裂时，只从随机选取的 $m$ 个特征中选最优分裂 ($m \approx \sqrt{d}$ 分类, $m \approx d/3$ 回归)
3. **聚合**: 分类用投票 (majority vote)，回归用平均

#### 6.2 为什么有效 (降低 Variance)

单棵深度 Decision Tree → 高 variance, 低 bias。

$$\text{Var}(\bar{X}) = \frac{\sigma^2}{T} \quad \text{(独立时)}$$

但树之间有相关性 $\rho$：

$$\text{Var} = \rho\sigma^2 + \frac{1-\rho}{T}\sigma^2$$

- **Bagging** 增大 $T$ → 减小第二项
- **Feature Subsampling** 降低 $\rho$ (树之间相关性) → 减小第一项

这就是为什么 Random Forest 比单纯 Bagging 效果更好。

#### 6.3 Random Forest vs Boosting (GBDT/XGBoost)

| | Random Forest | Boosting (GBDT) |
|---|---|---|
| 训练方式 | 并行，独立训练 | 串行，每棵树修正前面的错误 |
| 解决的问题 | 降低 variance | 降低 bias |
| 过拟合风险 | 低 (天然正则化) | 高 (需要调参控制) |
| 树的深度 | 通常很深 (fully grown) | 通常很浅 (weak learners) |
| 关键超参 | n_estimators, max_features | learning_rate, n_estimators, max_depth |

#### 6.4 优劣势

**优势**: 不容易overfit, 可并行, 能给出feature importance, 对缺失值鲁棒, 不需要特征缩放

**劣势**: 解释性不如单棵树, 内存消耗大, 对稀疏高维数据效果不如Boosting, 预测速度慢 (需遍历所有树)

### 面试要点

- 必须能推导出 variance 的公式，解释为什么 feature subsampling 比纯 bagging 好
- RF 不容易 overfit，但不是 "不会" overfit — 树太多时可能 overfit noise
- Follow-up: OOB (Out-of-Bag) error 是什么？→ 每棵树有约 36.8% 的样本没被选中，可用作验证集

---

## 7. MLE 推导

### 题目描述

1. 推导Normal Distribution的MLE estimator ($\mu$ 和 $\sigma^2$)
2. GMM为什么不能直接用MLE？EM algorithm原理

### 最佳解答

#### 7.1 Normal Distribution MLE

给定 i.i.d. 样本 $x_1, ..., x_n \sim N(\mu, \sigma^2)$：

**似然函数**:
$$L(\mu, \sigma^2) = \prod_{i=1}^n \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(-\frac{(x_i-\mu)^2}{2\sigma^2}\right)$$

**对数似然**:
$$\ell = -\frac{n}{2}\ln(2\pi) - \frac{n}{2}\ln(\sigma^2) - \frac{1}{2\sigma^2}\sum_{i=1}^n(x_i-\mu)^2$$

**求 $\mu$**: 令 $\frac{\partial \ell}{\partial \mu} = 0$：

$$\frac{\partial \ell}{\partial \mu} = \frac{1}{\sigma^2}\sum_{i=1}^n(x_i - \mu) = 0 \implies \hat{\mu}_{MLE} = \frac{1}{n}\sum_{i=1}^n x_i = \bar{x}$$

**求 $\sigma^2$**: 令 $\frac{\partial \ell}{\partial \sigma^2} = 0$：

$$\frac{\partial \ell}{\partial \sigma^2} = -\frac{n}{2\sigma^2} + \frac{1}{2(\sigma^2)^2}\sum_{i=1}^n(x_i-\mu)^2 = 0$$

$$\implies \hat{\sigma}^2_{MLE} = \frac{1}{n}\sum_{i=1}^n(x_i - \bar{x})^2$$

注意：MLE 的 $\hat{\sigma}^2$ 是**有偏估计** (除以 $n$ 而非 $n-1$)，因为 $\bar{x}$ 本身也是从数据估计的。

#### 7.2 GMM 不能直接 MLE 的原因

**Gaussian Mixture Model**: $p(x) = \sum_{k=1}^K \pi_k \mathcal{N}(x|\mu_k, \Sigma_k)$

对数似然：
$$\ell = \sum_{i=1}^n \ln\left(\sum_{k=1}^K \pi_k \mathcal{N}(x_i|\mu_k, \Sigma_k)\right)$$

**问题**: $\ln$ 里面有 $\sum$！这导致无法像单个高斯那样对 $\mu_k$ 求导得到 closed-form solution。对 $\mu_k$ 求导后发现每个样本的贡献依赖于所有component的参数 — 参数之间耦合了。

#### 7.3 EM Algorithm 原理

EM 通过引入隐变量 $z$ (每个点属于哪个component) 来解耦：

**E-step (Expectation)**: 固定参数，计算每个点属于第 $k$ 个component的后验概率：
$$\gamma_{ik} = \frac{\pi_k \mathcal{N}(x_i|\mu_k, \Sigma_k)}{\sum_{j=1}^K \pi_j \mathcal{N}(x_i|\mu_j, \Sigma_j)}$$

**M-step (Maximization)**: 固定 $\gamma$，更新参数 (此时变成了加权MLE，有closed-form)：
$$\mu_k = \frac{\sum_i \gamma_{ik} x_i}{\sum_i \gamma_{ik}}, \quad \pi_k = \frac{\sum_i \gamma_{ik}}{n}$$

**收敛保证**: 每次迭代 log-likelihood 单调不减。EM 收敛到局部最优 (不保证全局)。

### 面试要点

- MLE 推导必须流畅，尤其是对 $\sigma^2$ 求导的部分 (注意分母是 $(\sigma^2)^2$)
- GMM不能直接MLE的本质原因：log里面有sum，无法分离参数
- EM 的直觉：如果我们知道每个点属于哪个cluster (z)，MLE就简单了 → 所以先猜z，再做MLE，交替进行
- Follow-up: EM 和 K-means 的关系？→ K-means 是 EM 的特例 (hard assignment, 等方差)

---

## 8. K-means 实现与停止条件

> **重点题目！** 面试中因停止条件回答不完整而被 downlevel。

### 题目描述

实现 K-means 算法，并详细说明所有可能的停止条件 (stopping criteria)。

### 最佳解答

#### 8.1 停止条件 (Stopping Criteria) — 共4种

1. **Centroid 变化小于 epsilon**: $\max_k \|\mu_k^{(t)} - \mu_k^{(t-1)}\| < \epsilon$
2. **达到最大迭代次数**: $t \geq T_{max}$
3. **样本分配不再变化**: 所有点的cluster assignment 和上一轮完全一样
4. **SSE (Sum of Squared Errors) 变化小于 threshold**: $|SSE^{(t)} - SSE^{(t-1)}| < \delta$

实际中通常同时使用多个条件 (任一满足就停止)。

#### 8.2 完整 Python 实现

```python
import numpy as np
from typing import Optional, Tuple

class KMeans:
    def __init__(self, k: int, max_iters: int = 300,
                 tol: float = 1e-4, random_state: Optional[int] = None):
        """
        Args:
            k: 聚类数量
            max_iters: 最大迭代次数 (停止条件2)
            tol: centroid变化阈值 (停止条件1)
            random_state: 随机种子
        """
        self.k = k
        self.max_iters = max_iters
        self.tol = tol
        self.rng = np.random.RandomState(random_state)
        self.centroids = None
        self.labels = None
        self.inertia_ = None  # SSE

    def _init_centroids(self, X: np.ndarray) -> np.ndarray:
        """K-means++ initialization for better convergence."""
        n_samples = X.shape[0]
        centroids = [X[self.rng.randint(n_samples)]]

        for _ in range(1, self.k):
            # 计算每个点到最近centroid的距离
            dists = np.min([np.sum((X - c) ** 2, axis=1)
                           for c in centroids], axis=0)
            # 按距离的概率选下一个centroid
            probs = dists / dists.sum()
            idx = self.rng.choice(n_samples, p=probs)
            centroids.append(X[idx])

        return np.array(centroids)

    def _assign_clusters(self, X: np.ndarray) -> np.ndarray:
        """将每个点分配到最近的centroid。"""
        # shape: (n_samples, k)
        distances = np.array([np.sum((X - c) ** 2, axis=1)
                              for c in self.centroids]).T
        return np.argmin(distances, axis=1)

    def _update_centroids(self, X: np.ndarray,
                          labels: np.ndarray) -> np.ndarray:
        """重新计算每个cluster的centroid。"""
        new_centroids = np.zeros_like(self.centroids)
        for k in range(self.k):
            members = X[labels == k]
            if len(members) > 0:
                new_centroids[k] = members.mean(axis=0)
            else:
                # 空cluster: 随机重新初始化
                new_centroids[k] = X[self.rng.randint(X.shape[0])]
        return new_centroids

    def _compute_sse(self, X: np.ndarray,
                     labels: np.ndarray) -> float:
        """计算 Sum of Squared Errors (inertia)。"""
        sse = 0.0
        for k in range(self.k):
            members = X[labels == k]
            if len(members) > 0:
                sse += np.sum((members - self.centroids[k]) ** 2)
        return sse

    def fit(self, X: np.ndarray) -> 'KMeans':
        """
        训练K-means模型。

        停止条件 (任一满足即停止):
        1. centroid变化 < tol
        2. 达到max_iters
        3. assignment不变
        4. SSE变化 < tol (通过centroid变化间接保证)
        """
        self.centroids = self._init_centroids(X)
        prev_labels = None
        prev_sse = float('inf')

        for iteration in range(self.max_iters):  # 停止条件2
            # E-step: 分配
            self.labels = self._assign_clusters(X)

            # 停止条件3: assignment不变
            if prev_labels is not None and \
               np.array_equal(self.labels, prev_labels):
                print(f"Converged: assignments unchanged "
                      f"at iteration {iteration}")
                break

            # M-step: 更新centroids
            new_centroids = self._update_centroids(X, self.labels)

            # 停止条件1: centroid变化 < tol
            centroid_shift = np.max(
                np.sqrt(np.sum(
                    (new_centroids - self.centroids) ** 2, axis=1
                ))
            )
            self.centroids = new_centroids

            # 停止条件4: SSE变化
            current_sse = self._compute_sse(X, self.labels)
            sse_change = abs(prev_sse - current_sse)

            if centroid_shift < self.tol:
                print(f"Converged: centroid shift {centroid_shift:.6f} "
                      f"< tol {self.tol} at iteration {iteration}")
                break

            prev_labels = self.labels.copy()
            prev_sse = current_sse

        self.inertia_ = self._compute_sse(X, self.labels)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """对新数据预测cluster assignment。"""
        return self._assign_clusters(X)


# --- 使用示例 ---
if __name__ == "__main__":
    np.random.seed(42)
    X = np.vstack([
        np.random.randn(100, 2) + [2, 2],
        np.random.randn(100, 2) + [-2, -2],
        np.random.randn(100, 2) + [2, -2],
    ])

    km = KMeans(k=3, max_iters=100, tol=1e-4, random_state=42)
    km.fit(X)
    print(f"Final SSE: {km.inertia_:.2f}")
    print(f"Centroids:\n{km.centroids}")
```

#### 8.3 面试中容易遗漏的点

- **空cluster处理**: 如果某个cluster没有点，需要重新初始化 (随机选一个点，或选离当前centroid最远的点)
- **K-means++ 初始化**: 面试官可能会问为什么不用随机初始化 → 随机可能选到很近的点，导致收敛慢或找到差的局部最优
- **时间复杂度**: $O(n \cdot k \cdot d \cdot T)$，$n$=样本数, $k$=聚类数, $d$=维度, $T$=迭代次数
- **K-means 的局限**: 只能找凸形cluster, 对outlier敏感, 需要预设K

### 面试要点

- **停止条件是核心考点**，必须列出至少3种
- K-means++ 初始化要能写出来
- 空cluster处理不能忘
- Follow-up: 怎么选K？→ Elbow method (SSE vs K), Silhouette score
- Follow-up: K-means 和 EM/GMM 的关系？→ K-means 是 GMM + EM 的特例 (hard assignment, 各component等方差)

---

## 9. Sparse Vector / Matrix Multiplication

### 题目描述

设计一个 Sparse Vector 和 Sparse Matrix 的类，实现乘法操作。要求：
- 从零设计 class 和 constructor
- 时间复杂度不能是 $O(M \times N)$
- 内存要最优化
- 类似 LeetCode 1507 (Dot Product of Two Sparse Vectors) + 311 (Sparse Matrix Multiplication)

### 最佳解答

#### 9.1 Sparse Vector

```python
class SparseVector:
    """稀疏向量：只存储非零元素。

    存储方式: list of (index, value) pairs, sorted by index.
    空间: O(nnz) where nnz = number of non-zero elements.
    """
    def __init__(self, nums: list):
        # 只存非零元素
        self.pairs = [(i, v) for i, v in enumerate(nums) if v != 0]
        self.size = len(nums)

    @classmethod
    def from_dict(cls, data: dict, size: int):
        """从字典 {index: value} 构建。"""
        vec = cls.__new__(cls)
        vec.pairs = sorted(data.items())
        vec.size = size
        return vec

    def dot(self, other: 'SparseVector') -> float:
        """
        两个稀疏向量点积。

        用双指针法: O(nnz_a + nnz_b), 不是 O(M*N)!
        """
        result = 0.0
        i, j = 0, 0
        while i < len(self.pairs) and j < len(other.pairs):
            idx_a, val_a = self.pairs[i]
            idx_b, val_b = other.pairs[j]
            if idx_a == idx_b:
                result += val_a * val_b
                i += 1
                j += 1
            elif idx_a < idx_b:
                i += 1
            else:
                j += 1
        return result
```

#### 9.2 Sparse Matrix

```python
class SparseMatrix:
    """稀疏矩阵：CSR-like 格式存储。

    存储: dict of {row: [(col, value), ...]}
    空间: O(nnz)
    """
    def __init__(self, matrix: list[list]):
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if matrix else 0
        # row -> sorted list of (col, val)
        self.data = {}
        for r in range(self.rows):
            row_data = [(c, matrix[r][c])
                        for c in range(self.cols)
                        if matrix[r][c] != 0]
            if row_data:
                self.data[r] = row_data

    def multiply(self, other: 'SparseMatrix') -> 'SparseMatrix':
        """
        矩阵乘法: self (M x K) * other (K x N) = result (M x N)

        关键优化: 只遍历非零元素!
        时间: O(M * nnz_per_row_A * nnz_per_col_B)
        远好于 O(M * K * N)
        """
        # 先把 other 转成列索引格式, 方便按列访问
        other_by_col = {}
        for r, row_data in other.data.items():
            for c, v in row_data:
                if c not in other_by_col:
                    other_by_col[c] = []
                other_by_col[c].append((r, v))

        # 结果矩阵
        result = [[0.0] * other.cols for _ in range(self.rows)]

        for r_a, row_a in self.data.items():
            for k, val_a in row_a:
                # A[r_a][k] * B[k][c] for all c where B[k][c] != 0
                if k in other.data:
                    for c, val_b in other.data[k]:
                        result[r_a][c] += val_a * val_b

        return SparseMatrix(result)

    def to_dense(self) -> list[list]:
        """转回稠密矩阵。"""
        mat = [[0.0] * self.cols for _ in range(self.rows)]
        for r, row_data in self.data.items():
            for c, v in row_data:
                mat[r][c] = v
        return mat


# --- 使用示例 ---
if __name__ == "__main__":
    # Sparse Vector dot product
    v1 = SparseVector([1, 0, 0, 2, 3])
    v2 = SparseVector([0, 3, 0, 4, 0])
    print(f"Dot product: {v1.dot(v2)}")  # 1*0 + 0*3 + 0*0 + 2*4 + 3*0 = 8

    # Sparse Matrix multiplication
    A = SparseMatrix([[1, 0, 0], [-1, 0, 3]])
    B = SparseMatrix([[7, 0, 0], [0, 0, 0], [0, 0, 1]])
    C = A.multiply(B)
    print(f"Result: {C.to_dense()}")  # [[7,0,0],[-7,0,3]]
```

### 面试要点

- **双指针** 是 Sparse Vector dot product 的关键 — O(nnz_a + nnz_b)
- Matrix乘法要用 "A的行 x B的行" 的方式遍历，而不是传统的三重循环
- 面试官要求从0设计class，注意 constructor 要清晰
- Follow-up: 如果一个vector特别稀疏，另一个不那么稀疏？→ 用 binary search 查找匹配 index, O(nnz_small * log(nnz_large))
- Follow-up: 分布式场景怎么做？→ 按行分块到不同机器

---

## 10. Stratified Sampling 实现

### 题目描述

输入是存储在 JSON 里的 training samples，每个 class 对应各自的 labels。要求从这些 class 里做 uniform random sample (分层采样)，保持每个class采样相同数量。

### 最佳解答

```python
import json
import random
from collections import defaultdict
from typing import List, Dict, Any, Optional

def load_samples(json_path: str) -> List[Dict[str, Any]]:
    """从JSON文件加载训练样本。"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def stratified_sample(
    samples: List[Dict[str, Any]],
    label_key: str = 'label',
    n_per_class: Optional[int] = None,
    fraction: Optional[float] = None,
    random_state: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    分层采样: 从每个class中采样相同数量(或比例)的样本。

    Args:
        samples: 样本列表, 每个样本是dict, 包含label_key字段
        label_key: 标签字段名
        n_per_class: 每个class采多少个 (和fraction二选一)
        fraction: 每个class采样比例
        random_state: 随机种子

    Returns:
        采样后的样本列表
    """
    if random_state is not None:
        random.seed(random_state)

    # Step 1: 按class分组
    groups = defaultdict(list)
    for sample in samples:
        label = sample[label_key]
        groups[label].append(sample)

    result = []

    for label, group in groups.items():
        # Step 2: 确定每个class的采样数量
        if n_per_class is not None:
            n = min(n_per_class, len(group))
        elif fraction is not None:
            n = max(1, int(len(group) * fraction))
        else:
            # 默认: 取最小class的大小 (保证均匀)
            min_class_size = min(len(g) for g in groups.values())
            n = min_class_size

        # Step 3: 随机采样 (无放回)
        sampled = random.sample(group, n)
        result.extend(sampled)

    # 打乱顺序
    random.shuffle(result)
    return result


# --- 使用示例 ---
if __name__ == "__main__":
    # 模拟JSON数据
    data = [
        {"id": 1, "text": "good product", "label": "positive"},
        {"id": 2, "text": "terrible", "label": "negative"},
        {"id": 3, "text": "love it", "label": "positive"},
        {"id": 4, "text": "okay", "label": "neutral"},
        {"id": 5, "text": "amazing", "label": "positive"},
        {"id": 6, "text": "bad", "label": "negative"},
        {"id": 7, "text": "fine", "label": "neutral"},
        {"id": 8, "text": "worst ever", "label": "negative"},
        {"id": 9, "text": "great", "label": "positive"},
        {"id": 10, "text": "meh", "label": "neutral"},
    ]

    # 每个class采2个
    sampled = stratified_sample(data, n_per_class=2, random_state=42)
    print(f"Sampled {len(sampled)} items:")
    for s in sampled:
        print(f"  {s['label']}: {s['text']}")
```

### 面试要点

- 核心：先按label分组 → 每组等量采样 → 合并打乱
- 注意边界: 某个class样本不够时怎么办 (取min)
- `random.sample` 是无放回采样，`random.choices` 是有放回
- Follow-up: 如果class极度不平衡怎么办？→ oversampling (SMOTE), undersampling, class weights
- Follow-up: 怎么保证采样的reproducibility？→ random seed

---

## 11. LRU Cache + 多线程 Follow-up

### 题目描述

(Coding with AI 轮) 面试官先问 LRU 概念，然后要求编辑 LRU 代码，让 AI 生成代码并 generate test cases，最后做 dry run。Follow-up 问多线程场景。

### 最佳解答

#### 11.1 LRU Cache 概念

**LRU (Least Recently Used)**: 当缓存满时，淘汰最久未使用的元素。

核心操作 (都要 O(1)):
- `get(key)`: 获取值并标记为最近使用
- `put(key, value)`: 插入/更新值，满了则淘汰LRU

**数据结构**: HashMap + Doubly Linked List
- HashMap: key → node (O(1) 查找)
- Doubly Linked List: 维护使用顺序 (head = MRU, tail = LRU)

#### 11.2 完整实现

```python
class Node:
    """双向链表节点。"""
    __slots__ = ['key', 'val', 'prev', 'next']

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        # 哨兵节点 (dummy head/tail) 简化边界处理
        self.head = Node()  # MRU end
        self.tail = Node()  # LRU end
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """从链表中移除节点。O(1)"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node):
        """将节点添加到head后面 (标记为最近使用)。O(1)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # 移到最前面 (最近使用)
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int):
        if key in self.cache:
            # 更新已有节点
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # 淘汰LRU (tail的前一个)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            # 插入新节点
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)


# --- Dry Run Test Cases ---
if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)        # cache: {1=1}
    cache.put(2, 2)        # cache: {1=1, 2=2}
    print(cache.get(1))    # 1, cache: {2=2, 1=1} (1变成MRU)
    cache.put(3, 3)        # 淘汰key=2, cache: {1=1, 3=3}
    print(cache.get(2))    # -1 (已被淘汰)
    cache.put(4, 4)        # 淘汰key=1, cache: {3=3, 4=4}
    print(cache.get(1))    # -1
    print(cache.get(3))    # 3
    print(cache.get(4))    # 4
```

#### 11.3 多线程 Follow-up

**问题**: 多个线程同时访问 LRU Cache 会有什么问题？怎么解决？

**问题1 — Race Condition**: 两个线程同时 `put`，可能导致链表指针错乱或超出容量。

**解决方案**:

```python
import threading

class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        self._cache = LRUCache(capacity)
        self._lock = threading.Lock()  # 互斥锁

    def get(self, key: int) -> int:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: int, value: int):
        with self._lock:
            self._cache.put(key, value)
```

**进阶 — 读写锁 (更高并发)**:

```python
class RWLockLRUCache:
    """读写锁版本: 允许多个读者同时读，但写者独占。

    注意: LRU的get也修改了链表(移到前面)，所以get也需要写锁！
    因此对LRU来说，读写锁的优势不大。
    """
    def __init__(self, capacity: int):
        self._cache = LRUCache(capacity)
        self._lock = threading.RLock()

    def get(self, key: int) -> int:
        with self._lock:  # get也需要独占锁(修改链表)
            return self._cache.get(key)

    def put(self, key: int, value: int):
        with self._lock:
            self._cache.put(key, value)
```

**关键洞察**: LRU 的 `get` 操作不是只读的 — 它会修改链表顺序，所以不能用简单的读写锁优化。如果要真正高并发，可以考虑分段锁 (Segmented LRU) 或 lock-free 数据结构。

### 面试要点

- Dummy head/tail 是面试标配写法，不要用无哨兵版本 (边界处理太容易出错)
- Dry run 时要口头跟踪链表状态和 HashMap 状态
- 多线程 follow-up 的关键陷阱：get 不是只读操作！
- 面试中 Coding with AI 轮要注意：让 AI 生成代码后你要能 review 并发现 bug

---

## 12. Service Dependency — 受影响服务查找

### 题目描述

(Coding with AI 轮) 给定不同 service 之间的 dependency 关系 (JSON格式)，当某个 service 挂了，需要 print 出所有受影响的 service。需要考虑 parent directory 关联和链式传播。

### 最佳解答

#### 12.1 问题分析

- 输入: JSON 描述的依赖关系 + 一个挂掉的 service
- 输出: 所有直接或间接受影响的 service
- 本质: **图的遍历** (BFS/DFS) — 从挂掉的节点出发，沿反向依赖边传播

#### 12.2 完整实现

```python
import json
from collections import defaultdict, deque
from typing import List, Set, Dict

def load_dependencies(json_path: str) -> Dict:
    """加载service依赖关系JSON。"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_reverse_graph(
    dependencies: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    构建反向依赖图。

    原始: A depends on [B, C] 意味着 B挂了 → A受影响
    反向图: B -> [A], C -> [A]
    """
    reverse = defaultdict(list)
    for service, deps in dependencies.items():
        for dep in deps:
            reverse[dep].append(service)
    return reverse

def find_affected_services(
    dependencies: Dict[str, List[str]],
    failed_service: str
) -> Set[str]:
    """
    BFS找出所有受影响的service (包括链式传播)。

    时间: O(V + E), V=service数, E=依赖边数
    """
    reverse_graph = build_reverse_graph(dependencies)

    affected = set()
    queue = deque([failed_service])

    while queue:
        current = queue.popleft()
        for dependent in reverse_graph.get(current, []):
            if dependent not in affected:
                affected.add(dependent)
                queue.append(dependent)  # 链式传播

    return affected

def find_affected_with_parent_dir(
    dependencies: Dict[str, List[str]],
    failed_service: str
) -> Set[str]:
    """
    扩展版: 考虑parent directory关联。

    如果 service "platform/auth" 挂了,
    那么 "platform/auth/login" 也受影响 (子服务)。
    """
    reverse_graph = build_reverse_graph(dependencies)
    all_services = set(dependencies.keys())

    affected = set()
    queue = deque([failed_service])

    while queue:
        current = queue.popleft()

        # 1. 检查反向依赖
        for dependent in reverse_graph.get(current, []):
            if dependent not in affected:
                affected.add(dependent)
                queue.append(dependent)

        # 2. 检查子服务 (parent dir关联)
        for svc in all_services:
            if svc.startswith(current + "/") and \
               svc not in affected and svc != failed_service:
                affected.add(svc)
                queue.append(svc)

    return affected


# --- 使用示例 ---
if __name__ == "__main__":
    # 依赖关系: key depends on values
    deps = {
        "web-app": ["auth-service", "user-service"],
        "auth-service": ["database", "cache"],
        "user-service": ["database"],
        "payment-service": ["auth-service", "database"],
        "notification": ["user-service"],
        "database": [],
        "cache": [],
    }

    failed = "database"
    affected = find_affected_services(deps, failed)
    print(f"If '{failed}' goes down, affected services:")
    for svc in sorted(affected):
        print(f"  - {svc}")
    # Output:
    #   - auth-service
    #   - notification
    #   - payment-service
    #   - user-service
    #   - web-app
```

### 面试要点

- 本质是 **反向图 + BFS**，一定要先构建反向依赖图
- 链式传播是关键：A 依赖 B，B 依赖 C → C 挂了，A 也受影响
- Parent directory 关联是 follow-up，要注意用 `startswith(prefix + "/")` 而不是 `startswith(prefix)` (避免 "auth" 匹配 "auth-service")
- Coding with AI 轮：让 AI 读 JSON 文件 → 你指导 AI 写代码 → review → 手动 dry run
- 面试官注意的不是你写的有多快，而是你能否有效地和 AI 协作、发现 AI 的错误

---

## 附录: 高频 Follow-up 问题速查

| 主题 | Follow-up | 简答 |
|------|-----------|------|
| Adam | AdamW vs Adam? | AdamW 将 weight decay 从梯度更新中解耦, 效果更好 |
| LR | 多分类? | Softmax + Categorical CE (Multinomial LR) |
| GD | 大batch泛化差怎么办? | LARS/LAMB, LR warmup, gradient accumulation |
| L1/L2 | Elastic Net? | $\alpha L1 + (1-\alpha) L2$, 兼顾稀疏性和稳定性 |
| Decision Tree | 为什么RF不容易overfit? | Bagging降variance + feature subsampling降相关性 |
| K-means | 怎么选K? | Elbow method, Silhouette score, Gap statistic |
| K-means | 和GMM关系? | K-means = hard EM + 等方差GMM |
| Sparse | 分布式? | 按行分块, MapReduce |
| LRU | 高并发? | 分段锁 (Segmented LRU), 或用 concurrent hash map |
| Service Dep | 环怎么办? | visited set 防止无限循环 (代码已包含) |

---

*本文档基于一亩三分地 LinkedIn MLE 面经整理，涵盖 ML fundamentals (八股)、ML coding、coding with AI 三类题型。*
