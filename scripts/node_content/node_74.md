# Gradient Descent Family（梯度下降家族）

## Overview

**Gradient Descent（梯度下降）** 及其变体是ML优化的基石。每个神经网络、逻辑回归和许多树方法都使用基于梯度的优化。面试中考察对收敛性质、动量机制和自适应方法的理解。

## Core Concepts

### Vanilla Gradient Descent（标准梯度下降）

基本更新规则：

$$w_{t+1} = w_t - \eta \nabla \mathcal{L}(w_t)$$

其中 $\eta$ 是 **Learning Rate（学习率）**，$\nabla \mathcal{L}$ 是损失函数关于参数的梯度。

**来源于一阶泰勒展开**：

$$\mathcal{L}(w + \Delta w) \approx \mathcal{L}(w) + \nabla \mathcal{L}(w)^T \Delta w$$

在约束 $\|\Delta w\| \leq \eta$ 下，使上式最小的方向是 $\Delta w = -\eta \frac{\nabla \mathcal{L}}{\|\nabla \mathcal{L}\|}$，即负梯度方向。

| 变体 | 批量大小 | 优点 | 缺点 |
|------|---------|------|------|
| **Batch GD（批量梯度下降）** | 全部数据 | 梯度稳定精确 | 慢，内存大，无法逃出局部最优 |
| **SGD（Stochastic GD，随机梯度下降）** | 1个样本 | 更新频繁，能逃出局部最优 | 梯度噪声大 |
| **Mini-batch GD（小批量梯度下降）** | $B$ 个样本 | 速度和稳定性的最佳折中 | 需要调 $B$ |

**Mini-batch的选择**：通常 $B \in \{32, 64, 128, 256\}$。更大的batch需要更大的学习率（**Linear Scaling Rule，线性缩放规则**：$\eta \propto B$）。batch过大可能收敛到尖锐极小值（泛化差）。

### Momentum（动量法）

$$v_t = \beta v_{t-1} + \nabla \mathcal{L}(w_t)$$

$$w_{t+1} = w_t - \eta v_t$$

动量在梯度方向一致时加速收敛，在梯度方向振荡时相互抵消。物理类比：小球在损失曲面上滚动，$v_t$ 是速度，$\beta$ 是摩擦系数。典型值 $\beta = 0.9$。

**为什么动量有效**：考虑一个细长的椭圆形损失曲面——沿长轴方向梯度小但一致，沿短轴方向梯度大但振荡。动量在长轴方向积累加速，在短轴方向抵消振荡。

**动量的另一种形式**（有时出现在文献中）：

$$v_t = \beta v_{t-1} + \eta \nabla \mathcal{L}(w_t), \quad w_{t+1} = w_t - v_t$$

两种形式数学等价（$\eta$ 的缩放位置不同）。

### Nesterov Accelerated Gradient (NAG，Nesterov加速梯度)

$$v_t = \beta v_{t-1} + \nabla \mathcal{L}(w_t - \eta \beta v_{t-1})$$

$$w_{t+1} = w_t - \eta v_t$$

关键区别：在"前看"位置 $w_t - \eta\beta v_{t-1}$ 计算梯度（而非当前位置）。直觉：先按动量走一步看看，然后在新位置计算梯度做修正。

**理论优势**：对凸函数，NAG的收敛率为 $O(1/T^2)$，优于SGD+Momentum的 $O(1/T)$。

### AdaGrad（自适应梯度）

为每个参数维护独立的学习率，基于历史梯度平方和：

$$G_{t,j} = \sum_{\tau=1}^{t} g_{\tau,j}^2$$

$$w_{t+1,j} = w_{t,j} - \frac{\eta}{\sqrt{G_{t,j} + \epsilon}} g_{t,j}$$

**直觉**：频繁更新的参数（大梯度累积）学习率自动变小；稀少更新的参数（小梯度累积）保持较大学习率。非常适合稀疏数据（如 **NLP（Natural Language Processing，自然语言处理）** 中的词向量）。

**问题**：$G_{t,j}$ 单调递增，学习率持续下降，训练后期可能过早停止学习。

### RMSProp（均方根传播）

用 **EMA（Exponential Moving Average，指数移动平均）** 替代梯度平方的累积和：

$$v_t = \gamma v_{t-1} + (1-\gamma)g_t^2$$

$$w_{t+1} = w_t - \frac{\eta}{\sqrt{v_t + \epsilon}}g_t$$

典型值 $\gamma = 0.9$。解决了AdaGrad学习率持续下降的问题——只关注近期梯度。

**Hinton的建议**（2012年Coursera课程）：$\gamma = 0.9, \eta = 0.001$。

### Adam（Adaptive Moment Estimation，自适应矩估计）

结合了Momentum（一阶矩）和RMSProp（二阶矩）：

**一阶矩（均值/动量）**：

$$m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$$

**二阶矩（方差）**：

$$v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$$

**Bias Correction（偏差校正）**：

$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t}$$

**参数更新**：

$$w_{t+1} = w_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon}\hat{m}_t$$

**默认超参数**：$\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}, \eta = 0.001$

**为什么需要偏差校正？** 初始时 $m_0 = v_0 = 0$，前几步的 $m_t, v_t$ 严重偏向零。校正因子 $1/(1-\beta^t)$ 随 $t$ 增大趋近1，消除初始偏差。当 $t=1$ 时，$m_1 = (1-\beta_1)g_1$，校正后 $\hat{m}_1 = g_1$，与真实梯度一致。

### AdamW（解耦权重衰减）

Adam中L2正则化和Weight Decay不等价（前面"正则化"章节已解释）。AdamW正确实现权重衰减：

$$w_{t+1} = (1 - \lambda)w_t - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon}\hat{m}_t$$

权重衰减直接应用于参数，不经过自适应缩放。这是 **Transformer** 训练的标准优化器。

### LAMB and LARS（大批量训练优化器）

**LARS（Layer-wise Adaptive Rate Scaling，层级自适应速率缩放）**：

$$\eta_l = \eta \cdot \frac{\|w_l\|}{\|\nabla \mathcal{L}(w_l)\| + \lambda\|w_l\|}$$

为每层计算独立的学习率，基于参数范数和梯度范数的比值。解决大batch训练中不同层梯度尺度差异大的问题。

**LAMB（Layer-wise Adaptive Moments optimizer for Batch training）**：

$$r_t = \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} + \lambda w_t$$

$$w_{t+1} = w_t - \eta \cdot \frac{\|w_t\|}{\|r_t\|} \cdot r_t$$

LAMB = Adam + 层级自适应缩放。用于大batch训练（如BERT预训练用batch size=65536）。

### Gradient Clipping（梯度裁剪）

防止 **Exploding Gradients（梯度爆炸）**：

**按范数裁剪**：

$$g \leftarrow g \cdot \min\left(1, \frac{\theta}{\|g\|}\right)$$

**按值裁剪**：$g_j \leftarrow \text{clip}(g_j, -\theta, \theta)$

按范数裁剪保持梯度方向不变（只缩放大小），是RNN和Transformer训练的标准做法。典型阈值 $\theta = 1.0$。

### Optimizer Comparison（优化器对比）

| 优化器 | 一阶矩 | 二阶矩 | 偏差校正 | 适用场景 |
|--------|--------|--------|---------|---------|
| SGD | 否 | 否 | N/A | 调参空间充足时泛化最好 |
| SGD+Momentum | 是 | 否 | N/A | 经典CNN训练 |
| AdaGrad | 否 | 是（累积） | 否 | 稀疏数据/NLP |
| RMSProp | 否 | 是（EMA） | 否 | RNN训练 |
| Adam | 是 | 是（EMA） | 是 | 快速收敛的通用选择 |
| AdamW | 是 | 是（EMA） | 是 | Transformer训练标准 |
| LAMB | 是 | 是（EMA） | 是 | 大batch预训练 |

### SGD vs Adam Debate（SGD vs Adam之争）

一个重要的面试话题：

**Adam的优势**：收敛快，对学习率不敏感，几乎无需调参
**SGD+Momentum的优势**：在充分调参后泛化性能可能更好

**现代共识**：
- 快速原型/NLP/Transformer → Adam/AdamW
- 计算机视觉竞赛/需要极致性能 → SGD+Momentum+精心调参
- 预训练大模型 → AdamW（甚至LAMB/LARS用于超大batch）
- SGD找到的平坦极小值（flat minima）泛化更好的假说有理论支持但不绝对

## Implementation

```python
import torch

# SGD with momentum
optimizer = torch.optim.SGD(
    model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4
)

# Adam
optimizer = torch.optim.Adam(
    model.parameters(), lr=1e-3, betas=(0.9, 0.999), eps=1e-8
)

# AdamW (standard for Transformers)
optimizer = torch.optim.AdamW(
    model.parameters(), lr=1e-3, weight_decay=0.01
)

# Gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# LAMB (using apex or timm)
# from apex.optimizers import FusedLAMB
# optimizer = FusedLAMB(model.parameters(), lr=1e-3, weight_decay=0.01)
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| SGD vs Adam | "选哪个优化器？" | Adam收敛快；SGD调参充分后泛化更好 |
| AdamW用于Transformer | 大模型训练 | 解耦权重衰减是关键 |
| Batch size效应 | "batch size如何影响训练？" | 大batch=少噪声，可能需要更大学习率 |
| 梯度裁剪 | 梯度爆炸 | 按范数裁剪保持方向 |
| 偏差校正 | Adam细节 | 初始步骤校正防止更新过小 |

### Common Interview Questions

- **逐步解释Adam？$m_t$和$v_t$代表什么？** $m_t$是梯度的EMA（一阶矩，方向），$v_t$是梯度平方的EMA（二阶矩，缩放）。偏差校正消除零初始化的偏差
- **AdamW为什么修复了Adam的权重衰减问题？** Adam中L2梯度被自适应缩放调整，导致不同参数受到不同程度正则化；AdamW解耦权重衰减不经过缩放
- **何时选SGD+Momentum而非Adam？** 有充足计算资源调参时，SGD在CV任务上可能泛化更好
- **什么导致梯度爆炸/消失，如何修复？** 深层网络中梯度连乘；修复：裁剪、残差连接、BatchNorm、正确初始化
- **从泰勒展开推导梯度下降更新？** 一阶展开取最小化方向，约束步长得到 $\Delta w = -\eta\nabla\mathcal{L}$

## Key Takeaways

- SGD+Momentum：调参充分时泛化最好，但需精心调节学习率
- Adam/AdamW：快速收敛，对学习率不敏感，是Transformer的标准选择
- Adam中的偏差校正防止早期更新过小
- 梯度裁剪（按范数）是RNN和大规模训练的必备技巧
- 线性缩放规则：batch size翻倍时，学习率也翻倍（有一定适用范围）
- LAMB/LARS：大batch预训练的专用优化器，通过层级自适应缩放解决梯度尺度问题
- 现代最佳实践：AdamW + warmup + cosine decay
