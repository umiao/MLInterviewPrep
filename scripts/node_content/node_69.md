# Regularization（正则化）

## Overview

**Regularization（正则化）** 是一系列约束模型复杂度、防止过拟合的技术。过拟合是指模型记忆了训练数据中的噪声而非学习可泛化的模式。理解L1与L2正则化的区别、它们的梯度行为、以及何时使用哪种正则化，是MLE面试的基础考点。本专题连接了优化理论和实际模型调优。

## Core Concepts

### Overfitting: Causes and Solutions（过拟合：原因与对策）

过拟合发生在模型过于紧密地拟合训练分布，将噪声当作信号来捕捉时。

**六大主要原因**：
1. **训练数据不足** —— 样本量不够以学习真实分布
2. **分布不匹配** —— 训练数据相对于测试/生产数据违反了 **i.i.d.（independent and identically distributed，独立同分布）** 假设
3. **训练数据含噪声** —— 标签错误或无关特征
4. **训练迭代过多** —— 模型在学会信号后继续记忆噪声
5. **特征工程不当** —— 特征缺乏泛化能力
6. **信息泄漏** —— 过于复杂的模型将训练集当作查找表

**对策工具箱**：
- 特征选择（手动、基于模型如 **PCA（Principal Component Analysis，主成分分析）**/**SVD（Singular Value Decomposition，奇异值分解）**、或随机如Random Forest）
- 正则化（L1, L2, Elastic Net）
- **Dropout（随机失活）**（训练时随机置零激活值）
- **Early Stopping（早停法）**（验证损失上升时停止训练）
- 集成方法（Random Forest、Bagging以降低方差）
- 控制模型复杂度（树深度、参数数量）

### L1 Regularization — LASSO（L1正则化——套索回归）

在损失函数中添加参数绝对值之和：

$$J_{\text{L1}}(\theta) = J(\theta) + \lambda \sum_{j=1}^{p} |\theta_j|$$

**梯度行为**：

$$\frac{\partial L_1(\theta_j)}{\partial \theta_j} = \text{sgn}(\theta_j) = \begin{cases} +1 & \theta_j > 0 \\ -1 & \theta_j < 0 \end{cases}$$

梯度大小**恒定**（始终为1或-1，与 $\theta_j$ 的当前值无关）。这意味着每次更新都以固定步长将参数推向零，不论其当前大小。小参数会先到达零并被消除。

**关键性质**：
- 产生 **Sparse（稀疏）** 模型（部分权重恰好为零）
- 作为自动 **Feature Selection（特征选择）** 工具
- 在 $\theta_j = 0$ 处不可微，需使用 **Subgradient（次梯度）** 方法
- LASSO = **Least Absolute Shrinkage and Selection Operator（最小绝对值收缩和选择算子）**

**几何直觉**：L1正则化的约束区域是一个 **Diamond（菱形/超正方体）**。等高线与菱形的顶点（坐标轴上）接触的概率最大，顶点处某些坐标为零——这就是L1产生稀疏解的几何原因。

### L2 Regularization — Ridge（L2正则化——岭回归）

在损失函数中添加参数平方值之和：

$$J_{\text{L2}}(\theta) = J(\theta) + \lambda \sum_{j=1}^{p} \theta_j^2$$

**梯度行为**：

$$\frac{\partial L_2(\theta_j)}{\partial \theta_j} = 2\theta_j$$

梯度**与参数值成正比**。当 $\theta_j$ 接近零时，梯度趋于消失——参数收缩但永远不会恰好到达零。

**关键性质**：
- 所有权重向零收缩但**不会归零**
- 产生 **Dense（稠密）** 模型（所有特征保留，权重较小）
- 保证**唯一最优解**（严格凸罚项）
- 处处可微，计算更简单

**几何直觉**：L2正则化的约束区域是一个 **Sphere/Circle（球体/圆）**。等高线与圆的切点通常不在坐标轴上，因此参数不会恰好为零。

**与贝叶斯的联系**：L2正则化等价于对参数施加 **Gaussian Prior（高斯先验）** $\theta_j \sim \mathcal{N}(0, \frac{1}{2\lambda})$，L1等价于 **Laplace Prior（拉普拉斯先验）** $\theta_j \sim \text{Laplace}(0, \frac{1}{\lambda})$。拉普拉斯分布在零点有尖峰，鼓励稀疏。

### Elastic Net（弹性网络）

组合L1和L2惩罚，解决单独使用L1的局限性：

$$J_{\text{EN}}(\theta) = J(\theta) + \lambda_1 \sum |\theta_j| + \lambda_2 \sum \theta_j^2$$

在sklearn中通常写作：

$$J_{\text{EN}}(\theta) = J(\theta) + \lambda [\alpha \sum |\theta_j| + (1-\alpha) \sum \theta_j^2]$$

其中 $\alpha$ 是L1比例（`l1_ratio`），$\lambda$ 是总正则化强度（`alpha`）。

**为什么需要Elastic Net**：
- 当特征高度相关时，L1会**任意选择**其中一个特征（不稳定）
- Elastic Net 鼓励 **Grouping Effect（分组效应）**——相关特征要么同时被选中，要么同时被剔除
- L2部分确保解的唯一性（当 $\lambda_2 > 0$ 时严格凸）

### Weight Decay vs L2 Regularization in Adam（Adam中的权重衰减与L2正则化）

这是一个面试中极其重要的区别：

**L2正则化**：在损失函数中添加 $\frac{\lambda}{2}\|w\|^2$，梯度变为 $g_t + \lambda w_t$，然后传入优化器。

**Weight Decay（权重衰减）**：直接在参数更新时减去 $\lambda w_t$。

对于 **SGD（Stochastic Gradient Descent，随机梯度下降）**，两者数学等价：

$$w_{t+1} = w_t - \eta(g_t + \lambda w_t) = (1-\eta\lambda)w_t - \eta g_t$$

但对于 **Adam** 等自适应学习率优化器，两者**不等价**。L2正则化的梯度 $\lambda w_t$ 会被Adam的自适应缩放（$1/\sqrt{\hat{v}_t}$）调整，使得不同参数受到不同程度的正则化——这不是我们想要的。

**AdamW（Decoupled Weight Decay，解耦权重衰减）** 直接应用权重衰减，不经过自适应缩放：

$$w_{t+1} = (1-\lambda)w_t - \frac{\eta}{\sqrt{\hat{v}_t}+\epsilon}\hat{m}_t$$

这是 **Loshchilov & Hutter (2019)** 的重要发现，也是为什么现代Transformer训练都使用AdamW而非Adam+L2。

### Regularization Strength（正则化强度）

超参数 $\lambda$（或sklearn中等价的 $1/C$）控制偏差-方差权衡：

- **$\lambda$ 大**：强惩罚，更简单的模型，高偏差，低方差
- **$\lambda$ 小**：弱惩罚，更复杂的模型，低偏差，高方差
- **$\lambda = 0$**：无正则化，等价于普通最小二乘

### Dropout（随机失活）

训练时随机将一部分神经元的激活值置零：

$$\hat{a}_i = \begin{cases} \frac{a_i}{1-p} & \text{with probability } 1-p \\ 0 & \text{with probability } p \end{cases}$$

这里除以 $(1-p)$ 是 **Inverted Dropout（反向Dropout）** 的做法，确保测试时不需要额外缩放。

**Dropout的多种理解方式**：

1. **集成视角**：等价于训练 $2^n$ 个（$n$ 为神经元数）共享权重的瘦网络的集成，预测时取平均

2. **Bayesian Approximation（贝叶斯近似）** 视角：**Gal & Ghahramani (2016)** 证明Dropout训练等价于一种 **Variational Inference（变分推断）** 的近似。预测时使用多次Dropout的平均（**MC Dropout，蒙特卡洛Dropout**）可以估计预测不确定性

3. **正则化视角**：防止神经元之间的 **Co-adaptation（协同适应）**，迫使每个神经元学习更鲁棒的特征

**变体**：
- **Spatial Dropout**：在CNN中丢弃整个特征图通道
- **DropConnect**：丢弃权重连接而非激活值
- **DropBlock**：丢弃特征图的连续区域
- **Concrete Dropout**：自动学习最优dropout率

### Early Stopping（早停法）

监控验证损失，当它开始上升时停止训练：

$$\text{stop when } \mathcal{L}_{\text{val}}(t) > \mathcal{L}_{\text{val}}(t_{\text{best}}) + \delta \text{ for patience steps}$$

**隐式正则化**：限制了有效的优化步数，等价于限制了模型可以到达的参数空间区域。对于线性模型，可以证明早停等价于L2正则化。

**优势**：无需额外超参数调优（除了patience），计算成本最低的正则化方法。

### Data Augmentation as Regularization（数据增强作为正则化）

**Data Augmentation（数据增强）** 通过对训练数据施加变换来增加有效训练集大小：
- **图像**：翻转、旋转、裁剪、颜色抖动、**Mixup**、**CutMix**
- **文本**：同义词替换、回译、随机删除
- **表格**：**SMOTE（Synthetic Minority Over-sampling Technique，合成少数类过采样技术）**

**Mixup** 的正则化公式：

$$\tilde{x} = \lambda x_i + (1-\lambda) x_j, \quad \tilde{y} = \lambda y_i + (1-\lambda) y_j, \quad \lambda \sim \text{Beta}(\alpha, \alpha)$$

### Label Smoothing（标签平滑）

将硬标签 $(0, 1)$ 替换为软标签：

$$y_{\text{smooth}} = (1-\epsilon) \cdot y_{\text{one-hot}} + \frac{\epsilon}{K}$$

防止模型对预测过度自信，提高泛化性和校准性。常用 $\epsilon = 0.1$。

### Dimensionality Reduction as Regularization（降维作为正则化）

**PCA（Principal Component Analysis，主成分分析）**：找到协方差矩阵的特征向量，保留对应最大特征值的前 $k$ 个特征向量。在保留最大方差的同时降低特征空间维度，减少过拟合风险。

权衡：PCA通过降维减少过拟合，但牺牲了可解释性——主成分是原始特征的线性组合。

## Implementation

```python
from sklearn.linear_model import Lasso, Ridge, ElasticNet, LassoCV
from sklearn.model_selection import cross_val_score
import numpy as np

# L1 (LASSO) -- 通过稀疏性实现特征选择
lasso = Lasso(alpha=0.1)  # alpha = lambda
lasso.fit(X_train, y_train)
selected = np.where(lasso.coef_ != 0)[0]  # 非零特征

# L2 (Ridge) -- 收缩但不消除
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)

# Elastic Net -- 组合 L1 + L2
enet = ElasticNet(alpha=0.1, l1_ratio=0.5)  # l1_ratio: L1比例
enet.fit(X_train, y_train)

# 通过交叉验证调优 lambda
lasso_cv = LassoCV(cv=5, alphas=np.logspace(-4, 1, 50))
lasso_cv.fit(X_train, y_train)
best_alpha = lasso_cv.alpha_

# Dropout in PyTorch
import torch.nn as nn
model = nn.Sequential(
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(p=0.5),  # 训练时50%神经元被丢弃
    nn.Linear(128, 10)
)
# 测试时: model.eval() 自动禁用Dropout
```

## Comparisons

| 方面 | L1 (LASSO) | L2 (Ridge) | Elastic Net |
|------|-----------|-----------|-------------|
| 罚项 | $\sum \|\theta_j\|$ | $\sum \theta_j^2$ | $\lambda_1 \sum \|\theta_j\| + \lambda_2 \sum \theta_j^2$ |
| 梯度 | $\pm 1$（恒定） | $2\theta_j$（正比） | 两者组合 |
| 稀疏性 | 是（产生精确零） | 否（收缩但不归零） | 部分稀疏 |
| 特征选择 | 内建 | 否 | 内建 |
| 唯一性 | 可能有多个最优解 | 唯一最优解 | 唯一（$\lambda_2 > 0$时） |
| 相关特征 | 任意选择一个 | 在相关特征间分散权重 | 分组后选择 |
| 几何约束 | 菱形（顶点在坐标轴上） | 圆/球 | 介于两者之间 |
| 贝叶斯等价 | 拉普拉斯先验 | 高斯先验 | 组合先验 |
| sklearn类 | `Lasso(alpha=)` | `Ridge(alpha=)` | `ElasticNet(alpha=, l1_ratio=)` |

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| L1做特征选择 | 高维数据，多无关特征 | 恒定梯度将权重驱动到精确零 |
| L2处理多重共线性 | 相关特征，需稳定系数 | 在相关特征间分散权重 |
| Elastic Net | 相关特征+需要稀疏性 | 分组相关特征，然后选择组 |
| Early Stopping | 神经网络/迭代模型 | 最便宜的正则化——除patience外无超参数 |
| Dropout | 深度网络易协同适应 | 等价于 $2^n$ 个瘦网络的集成 |
| Weight Decay vs L2 | Adam优化器选择 | Adam中L2和Weight Decay不等价——用AdamW |

### Common Interview Questions

- **什么是过拟合，如何预防？** 六大原因对应不同解决方案
- **L1 vs L2：何时用哪个？** L1当怀疑很多特征无关（要稀疏）；L2当特征相关（要稳定）
- **为什么L1产生稀疏解？（梯度论证）** 恒定梯度 $\pm 1$ 以固定速率推向零，不受当前值影响
- **为什么L1产生稀疏解？（几何论证）** 菱形约束区域的顶点在坐标轴上，等高线更可能在顶点相切
- **正则化强度如何影响偏差-方差？** $\lambda$ 大→更简单模型→高偏差低方差
- **过度正则化会怎样？** 模型退化为常数预测，严重欠拟合
- **Dropout如何工作？为什么有效？** 随机置零激活值，等价于集成+防止协同适应；贝叶斯视角是变分推断
- **L1和L2的几何解释？** L1的菱形约束和L2的圆形约束——等高线与约束区域的切点位置不同
- **AdamW和Adam+L2的区别？** Adam中L2梯度被自适应缩放改变；AdamW解耦权重衰减，不受此影响

## Key Takeaways

- 过拟合有六大明确原因——根据原因匹配解决方案
- L1梯度恒定（$\pm 1$），将权重驱动到精确零（稀疏性）
- L2梯度正比于参数值（$2\theta_j$），权重收缩但永不为零
- $\lambda$ 控制偏差-方差权衡：更高 = 更简单模型 = 更多偏差
- L1用于怀疑很多特征无关时；L2用于特征相关时
- Elastic Net组合两者：适用于相关特征且仍需稀疏性的场景
- Dropout概念上是集成方法；Early Stopping是最廉价的正则化器
- 在Adam中使用Weight Decay（AdamW）而非L2正则化——两者在自适应优化器中不等价
- 数据增强和Label Smoothing也是有效的正则化手段
