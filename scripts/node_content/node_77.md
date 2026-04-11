# Training Tricks（训练技巧）

## Overview

实用训练技巧是理论和可工作模型之间的桥梁。这些技术是MLE面试的必备知识——它们表明你不仅会推导公式，还能真正训练模型。掌握权重初始化、归一化方法、混合精度训练和梯度技巧是区分初级和高级工程师的关键。

## Core Concepts

### Weight Initialization（权重初始化）

正确的初始化确保信号在前向传播和反向传播中保持合理的数值范围，避免梯度消失或爆炸。

**Xavier / Glorot Initialization（Xavier/Glorot初始化）**——适用于 **Sigmoid** 和 **Tanh（双曲正切）** 激活函数：

$$W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}} + n_{\text{out}}}\right) \quad \text{or} \quad W \sim U\left[-\sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}, \sqrt{\frac{6}{n_{\text{in}}+n_{\text{out}}}}\right]$$

**推导思想**：要求每层输出的方差等于输入的方差。对于线性层 $y = Wx$，$\text{Var}(y) = n_{\text{in}} \cdot \text{Var}(W) \cdot \text{Var}(x)$。令 $\text{Var}(y) = \text{Var}(x)$ 得 $\text{Var}(W) = 1/n_{\text{in}}$。考虑反向传播需 $\text{Var}(W) = 1/n_{\text{out}}$，折中取 $\text{Var}(W) = 2/(n_{\text{in}} + n_{\text{out}})$。

**He / Kaiming Initialization（He/Kaiming初始化）**——适用于 **ReLU（Rectified Linear Unit，修正线性单元）** 及其变体：

$$W \sim \mathcal{N}\left(0, \frac{2}{n_{\text{in}}}\right)$$

**为什么ReLU需要不同的初始化？** ReLU将约一半的输出置零（期望上有一半神经元被激活），因此方差被减半。He初始化通过将方差乘以2来补偿这个因子。

**其他初始化方法**：
- **Orthogonal Initialization（正交初始化）**：$W$ 是正交矩阵，保持激活值的范数。适用于RNN
- **LSUV（Layer-Sequential Unit-Variance，逐层单位方差）**：数据驱动的初始化，逐层调整使输出方差为1
- **Fixup**：允许在没有BatchNorm的情况下训练深度残差网络

### Batch Normalization（批归一化）

对每个mini-batch的激活值进行归一化：

$$\hat{x}_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat{x}_i + \beta$$

其中 $\mu_B = \frac{1}{m}\sum x_i$，$\sigma_B^2 = \frac{1}{m}\sum(x_i - \mu_B)^2$ 是batch统计量。$\gamma$ 和 $\beta$ 是可学习的缩放和偏移参数。

**推理时**：使用训练过程中的 **Running Mean/Variance（运行均值/方差）**（指数移动平均），而非当前batch的统计量。

**BN（Batch Normalization，批归一化）的好处**：
1. **加速收敛**：归一化使损失景观更平滑
2. **允许更大学习率**：减少了对初始化的敏感性
3. **轻微正则化**：batch统计量引入噪声（小batch噪声更大）
4. **减少内部协变量偏移**（**Internal Covariate Shift，内部协变量偏移**）——每层输入分布更稳定

**BN的局限性**：
- 依赖batch size：batch太小时统计量不稳定
- 不适用于变长序列（RNN/Transformer）
- 训练和推理行为不同（需要 `model.eval()`）

### Layer Normalization（层归一化）

跨特征（而非跨batch）归一化：

$$\hat{x}_i = \frac{x_i - \mu_i}{\sqrt{\sigma_i^2 + \epsilon}}, \quad \mu_i = \frac{1}{d}\sum_{j=1}^{d}x_{ij}$$

**LN（Layer Normalization，层归一化）** 在 **Transformer** 中使用，因为：
1. 不依赖batch统计量，batch size=1也可以
2. 适用于变长序列
3. 训练和推理行为一致

**其他归一化方法**：
- **Instance Normalization（实例归一化）**：对每个样本的每个通道独立归一化。用于风格迁移
- **Group Normalization（组归一化）**：将通道分组后组内归一化。batch size小时替代BN
- **RMS Normalization（均方根归一化）**：$\hat{x} = x / \text{RMS}(x)$，省略均值中心化。LLaMA等模型使用

### Gradient Clipping（梯度裁剪）

**按范数裁剪**（推荐）：

$$g \leftarrow g \cdot \min\left(1, \frac{\theta}{\|g\|}\right)$$

保持梯度方向不变，只缩放大小。

**按值裁剪**：$g_j \leftarrow \text{clip}(g_j, -\theta, \theta)$

可能改变梯度方向。

RNN和Transformer训练的必备技巧。典型最大范数：1.0。

### Mixed Precision Training（混合精度训练）

使用 **FP16（半精度浮点数）** 做前向/反向传播，**FP32（单精度浮点数）** 保存权重更新：

1. **Forward pass**：FP16计算，速度2-3x
2. **Loss Scaling（损失缩放）**：将损失乘以缩放因子防止FP16 **Underflow（下溢）**——FP16能表示的最小正数约 $6 \times 10^{-8}$，小梯度可能变为零
3. **Backward pass**：FP16计算梯度
4. **Unscale（反缩放）** 梯度，用FP32更新 **Master Weights（主权重）**

**BF16（Brain Floating Point 16，脑浮点16位）**：与FP16相同的16位但分配更多位给指数（8位 vs FP16的5位），动态范围与FP32相同，减少了对损失缩放的需求。Google TPU和新一代GPU原生支持。

| 精度 | 位数 | 指数位 | 尾数位 | 动态范围 |
|------|------|--------|--------|---------|
| FP32 | 32 | 8 | 23 | $\sim 10^{-38}$ to $10^{38}$ |
| FP16 | 16 | 5 | 10 | $\sim 10^{-8}$ to $10^{4}$ |
| BF16 | 16 | 8 | 7 | $\sim 10^{-38}$ to $10^{38}$ |

### Label Smoothing（标签平滑）

将 **One-Hot（独热编码）** 标签替换为软标签：

$$y_{\text{smooth}} = (1-\epsilon) \cdot y_{\text{one-hot}} + \frac{\epsilon}{K}$$

例如 $K=10, \epsilon=0.1$：正确类的目标从1变为0.9，其他类从0变为0.01。

**效果**：
- 防止模型对预测过度自信（logits不会趋向无穷大）
- 提高泛化性能和校准性
- 等价于在交叉熵中添加KL散度正则项

### EMA and SWA（指数移动平均与随机权重平均）

**EMA（Exponential Moving Average，指数移动平均）**：

$$\theta_{\text{ema}} = \alpha \cdot \theta_{\text{ema}} + (1-\alpha) \cdot \theta_t$$

训练时维护一份参数的移动平均版本，用于评估。典型 $\alpha = 0.999$ 或 $0.9999$。

**SWA（Stochastic Weight Averaging，随机权重平均）**：

在训练后期，用周期性学习率的多个检查点做简单平均。理论上SWA找到更宽的极小值，泛化更好。

### Gradient Accumulation（梯度累积）

在GPU内存有限时模拟大batch：

```
accumulation_steps = 4  # 有效batch = 实际batch * 4
optimizer.zero_grad()
for i, batch in enumerate(dataloader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

注意：损失需要除以 `accumulation_steps`，BN统计量只基于实际batch size。

### Data Parallel Training（数据并行训练）

| 方法 | 描述 | 适用规模 |
|------|------|---------|
| **DP（DataParallel）** | 单机多GPU，复制模型到每块GPU | 2-8 GPU |
| **DDP（DistributedDataParallel）** | 多机多GPU，AllReduce同步梯度 | 8-数百GPU |
| **FSDP（Fully Sharded DP）** | 参数+梯度+优化器状态全分片 | 数百-数千GPU |
| **Pipeline Parallel** | 不同层放在不同GPU | 超大模型 |
| **Tensor Parallel** | 单层内分片 | 超大模型 |

## Implementation

```python
import torch
from torch.cuda.amp import autocast, GradScaler

# 混合精度训练完整流程
scaler = GradScaler()
for batch in dataloader:
    optimizer.zero_grad()
    with autocast():
        output = model(batch)
        loss = criterion(output, targets)
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    scaler.step(optimizer)
    scaler.update()

# EMA
class EMA:
    def __init__(self, model, decay=0.999):
        self.decay = decay
        self.shadow = {k: v.clone() for k, v in model.state_dict().items()}
    def update(self, model):
        for k, v in model.state_dict().items():
            self.shadow[k] = self.decay * self.shadow[k] + (1 - self.decay) * v
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| BN vs LN | 架构选择 | BN用于CNN（batch统计）；LN用于Transformer（序列统计） |
| 初始化策略 | "如何初始化？" | He用于ReLU；Xavier用于sigmoid/tanh；预训练权重优先 |
| 训练不稳定诊断 | "Loss变NaN" | 检查：LR过大、无梯度裁剪、初始化不当、数据问题 |
| 梯度累积 | GPU内存有限 | 累积 $k$ 步再更新，等效于 $k$ 倍batch |
| 混合精度 | 加速训练 | FP16前向/反向 + FP32更新 + 损失缩放 |

### Common Interview Questions

- **He初始化为什么比Xavier好（对ReLU）？** ReLU丢弃一半输出，方差减半。He初始化方差翻倍补偿：$\text{Var}(W) = 2/n_{\text{in}}$
- **解释BN：训练 vs 推理行为？** 训练用batch统计量+可学习参数；推理用运行均值/方差。`model.eval()` 切换模式
- **混合精度如何工作？为什么需要损失缩放？** FP16计算快但范围小，小梯度下溢为零。损失缩放放大梯度到FP16可表示范围
- **BN vs LN：何时用哪个？** BN适合固定长度的CNN输入；LN适合变长序列的Transformer
- **GPU内存不足怎么训练大模型？** 梯度累积、混合精度、梯度检查点（checkpoint）、模型并行

## Key Takeaways

- 权重初始化：匹配激活函数（He→ReLU，Xavier→tanh）
- BN按batch归一化；LN按样本归一化（适合Transformer）
- 梯度裁剪（按范数）：深层网络稳定训练的必备
- 混合精度：2-3x加速，大模型训练的标准实践
- 梯度累积：有效增大batch size而不增加内存
- Label Smoothing：防止过度自信，提高泛化和校准
- EMA：平滑模型参数，获得更稳定的评估结果
- BF16正在取代FP16成为新一代混合精度的标准
