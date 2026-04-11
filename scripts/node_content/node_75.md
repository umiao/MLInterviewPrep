# Learning Rate Scheduling（学习率调度）

## Overview

**Learning Rate（学习率）** 是最重要的超参数。学习率过高会导致发散，过低则收敛缓慢或陷入局部最优。**Learning Rate Scheduling（学习率调度）** 策略在训练过程中系统地调整学习率，以实现更好的收敛和泛化性能。

现代深度学习的标准做法是 **Warmup（预热）** + **Cosine Decay（余弦衰减）**，这一组合在从视觉模型到大语言模型的各种任务中表现优异。学习率调度的本质是在训练的不同阶段平衡探索（大学习率）和精细化（小学习率）。

## Core Concepts

### Warmup（预热）

从小学习率开始，线性增加到目标值：

$$\eta_t = \eta_{\max} \cdot \frac{t}{T_{\text{warmup}}}$$

**为什么需要Warmup**：
1. 训练初期梯度大且方向不可靠，大学习率容易发散
2. **Adam（Adaptive Moment Estimation，自适应矩估计）** 的分母 $\sqrt{\hat{v}_t}$ 在初期估计不准（$v_0 = 0$），尽管有偏差校正，实际值仍可能偏小，导致更新过大
3. **Batch Normalization（批归一化）** 的统计量在初期不稳定
4. 大batch训练中，warmup尤其关键——避免初始阶段的剧烈震荡

典型warmup步数：总训练步数的5-10%，或几百到几千步。

### Step Decay（阶梯衰减）

每 $k$ 个epoch将学习率乘以衰减因子 $\gamma$：

$$\eta_t = \eta_0 \cdot \gamma^{\lfloor t/k \rfloor}$$

经典设置：每30个epoch衰减10倍（$\gamma = 0.1, k = 30$）。曾是ResNet等CNN训练的标准方法。

**优点**：简单直观，每次衰减后性能通常有明显跳升
**缺点**：不连续的学习率跳变可能导致训练不稳定；需要手动选择衰减时间点

### Cosine Annealing（余弦退火）

$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\frac{t\pi}{T}\right)$$

从 $\eta_{\max}$ 平滑衰减到 $\eta_{\min}$。衰减曲线形状像余弦函数的前半周期——初期衰减慢，中期加速，末期再次变慢。

**优点**：平滑衰减避免突变，训练末期学习率趋近零有助于收敛到更好的解
**应用**：视觉模型和 **LLM（Large Language Model，大语言模型）** 训练的现代标准

### Cosine Annealing with Warm Restarts / SGDR（带热重启的余弦退火）

$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\frac{T_{\text{cur}}}{T_i}\pi\right)$$

周期性重置学习率到最大值（热重启），帮助模型逃离局部最优。$T_i$ 是第 $i$ 个周期的长度。

**Multiplicative Restart（乘性重启）**：$T_{i+1} = T_i \cdot T_{\text{mult}}$，周期逐渐变长（如 $T_{\text{mult}} = 2$），前期快速探索，后期精细收敛。

**Snapshot Ensemble**：在每次热重启前保存模型快照，最终对所有快照做集成。用一次训练的成本获得集成模型的效果。

### One-Cycle Policy（单周期策略）

由 **Leslie Smith (2018)** 提出的 **Super-Convergence（超收敛）** 方法：

1. 从低学习率warmup到最大学习率（前30%训练步数）
2. 从最大学习率cosine衰减到很低的值（后70%）
3. 同时，动量从高到低再到高（与学习率反向）

$$\eta_t = \begin{cases} \eta_{\min} + (\eta_{\max} - \eta_{\min}) \cdot \frac{t}{T_1} & t \leq T_1 \\ \eta_{\max} - (\eta_{\max} - \eta_{\min}) \cdot \frac{t - T_1}{T - T_1} & t > T_1 \end{cases}$$

**优点**：通常能以更少的训练步数达到更好的性能。fastai框架的默认策略。

### Inverse Square Root Schedule（反平方根调度）

**Transformer（变换器）** 原始论文（Vaswani et al., 2017）使用的调度：

$$\eta_t = d_{\text{model}}^{-0.5} \cdot \min(t^{-0.5}, t \cdot T_{\text{warmup}}^{-1.5})$$

warmup阶段线性增长，之后按 $t^{-0.5}$ 衰减。注意学习率与模型维度 $d_{\text{model}}$ 相关。

### Polynomial Decay（多项式衰减）

$$\eta_t = (\eta_{\max} - \eta_{\min}) \cdot \left(1 - \frac{t}{T}\right)^p + \eta_{\min}$$

$p = 1$ 为线性衰减，$p = 2$ 为二次衰减。TensorFlow中常用。

### Learning Rate Finder（学习率搜索）

逐步增大学习率（从极小到极大），绘制损失vs学习率曲线。选择损失下降最快处（拐点前）的学习率，而非损失最小处。

**步骤**：
1. 将学习率从 $10^{-7}$ 指数增加到 $10^{0}$
2. 在每个学习率下训练一个mini-batch，记录损失
3. 选择损失急剧下降区域的学习率作为 $\eta_{\max}$

由 **Leslie Smith** 提出，**fast.ai** 库推广使用。

### Learning Rate and Batch Size Coupling（学习率与Batch Size的耦合）

**Linear Scaling Rule（线性缩放规则）**：当batch size翻倍时，学习率也翻倍。

$$\eta_{\text{new}} = \eta_{\text{base}} \cdot \frac{B_{\text{new}}}{B_{\text{base}}}$$

理论依据：大batch的梯度方差更小（$\text{Var} \propto 1/B$），可以承受更大的步长。

**适用范围**：在一定batch size范围内有效（通常到几千），超大batch（如32K+）后线性缩放不再成立，需要 **LARS/LAMB** 等层级自适应方法。

**Warmup的必要性随batch size增大而增加**：Goyal et al. (2017) 在ImageNet训练中证明，batch size=8192时需要5个epoch的warmup才能稳定训练。

### ReduceLROnPlateau（自适应衰减）

当验证指标不再改善时自动衰减学习率：

$$\text{if } \mathcal{L}_{\text{val}} \text{ 在 patience 个epoch内无改善} \Rightarrow \eta \leftarrow \eta \cdot \text{factor}$$

不需要预设衰减时间点，根据训练实际情况自适应调整。适用于不确定训练长度或数据特性的场景。

**常用参数**：`factor=0.1`（每次衰减10倍），`patience=10`（等待10个epoch），`min_lr=1e-7`（最低学习率下限）。

### Curriculum Learning Rate（课程学习率）

根据训练阶段使用不同的学习率策略：
- **预训练阶段**：较大学习率 + cosine衰减
- **微调阶段**：较小学习率（通常为预训练的1/10到1/100）
- **分层学习率**：底层（预训练）用较小LR，顶层（新增）用较大LR

这在 **Transfer Learning（迁移学习）** 中尤其重要——预训练的底层参数已经学到了通用特征，不需要大幅调整。

### Multi-Stage Training Schedule（多阶段训练调度）

现代大模型训练通常分为多个阶段，每个阶段使用不同的学习率：

| 阶段 | 学习率 | 数据 | 目的 |
|------|--------|------|------|
| 预训练 | 大（$\sim 10^{-3}$） | 大规模无标签 | 学习通用表示 |
| 微调 | 小（$\sim 10^{-5}$） | 任务特定有标签 | 适配下游任务 |
| 对齐/RLHF | 极小（$\sim 10^{-6}$） | 人类偏好 | 对齐人类意图 |

## Implementation

```python
import torch.optim as optim
import math

# Warmup + Cosine decay (最常用的现代方案)
def lr_lambda(step):
    if step < warmup_steps:
        return step / warmup_steps
    progress = (step - warmup_steps) / (total_steps - warmup_steps)
    return 0.5 * (1 + math.cos(math.pi * progress))
scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

# Cosine Annealing with Warm Restarts
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=10, T_mult=2, eta_min=1e-6
)

# One-Cycle Policy
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=1e-3,
    total_steps=num_epochs * steps_per_epoch,
    pct_start=0.3  # 30%用于warmup
)

# Step Decay
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

# ReduceLROnPlateau (自适应：验证损失不下降时衰减)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.1, patience=10
)
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| Warmup必要性 | Transformer/大batch | 防止初期大梯度和不稳定估计导致的发散 |
| Cosine vs Step衰减 | "用哪种调度？" | Cosine更平滑，避免突变；Step更简单但不连续 |
| LR-Batch Size耦合 | 扩大训练规模 | 线性缩放：$\eta \propto B$（有适用范围） |
| 周期性LR | 逃离局部最优 | 周期性LR增加有助于探索损失景观 |
| LR Finder | 快速确定范围 | 选择损失急剧下降处而非最低处 |

### Common Interview Questions

- **为什么Transformer训练需要Warmup？** Adam的二阶矩估计在初期不准确，大学习率会导致发散。warmup给自适应统计量时间稳定
- **Cosine退火 vs Step衰减，各自何时更好？** Cosine更平滑现代化，适合大多数场景；Step在需要手动控制衰减时间点时更灵活
- **如何使用学习率搜索器？** 指数增大LR，绘制loss曲线，选择损失下降最快处。注意用一次性探索，不影响正式训练
- **Batch size和学习率的关系？** 线性缩放规则 $\eta \propto B$；大batch需要warmup；超大batch用LARS/LAMB
- **解释One-Cycle策略及其工作原理？** 先升后降的LR + 反向变化的动量，fast.ai推广。能以更少步数达到更好性能（super-convergence）

## Key Takeaways

- Warmup + Cosine Decay是现代深度学习的默认方案
- 学习率搜索器：快速找到合适的学习率范围
- One-Cycle策略：快速收敛的有监督训练方案
- 反平方根调度：原始Transformer训练的标准方案
- Batch size翻倍时LR也翻倍（线性缩放规则，有适用范围）
- ReduceLROnPlateau：自适应方案，适合不确定训练长度的场景
- 面试中要能解释warmup的必要性和cosine衰减的优势
- 大模型训练通常分阶段，每阶段使用不同学习率量级
- 分层学习率在迁移学习微调中非常实用——底层小LR保留通用特征，顶层大LR学习任务特定特征
- ReduceLROnPlateau适合不确定最优训练长度的探索性实验
- Snapshot Ensemble利用周期性LR在一次训练中获得多个模型进行集成
