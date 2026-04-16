<!-- KG_M_01_DIFFUSION_20260416 -->

# Diffusion Models — Canonical Deep Dive

> **正典节点** [Diffusion Models (pillar6.diffusion_models)](/framework/200)

> 本文是 KG-M-01 迁移自 Adobe Doc 19 的 paper 风格深推导，**与正典节点共生**。结构对应：节点给出 12-section 概览与 interview pitfalls；本文给出从 DDPM 到 IP-Adapter 的完整章节式深推导。Sections 11 (Positional Embedding) 与 12 (KV-Cache) 为 Doc 19 误归类的 transformer / LLM-inference 内容，已分别由 [Position Encoding](/framework/143) 与 [KV Cache](/framework/156) 节点承载，故此处剔除。

---

# Diffusion Models 深度指南 (Adobe Prep Day 1)

## Prerequisites

- 基础概率论: 高斯分布、条件概率、贝叶斯定理
- 神经网络基础: 前向/反向传播、损失函数、梯度下降
- VAE 概念: 编码器-解码器架构、潜在空间 (latent space)
- 卷积神经网络: 卷积操作、特征图、UNet 跳跃连接

## Key Terms

- **DDPM** (Denoising Diffusion Probabilistic Models): 通过逐步去噪来生成数据的概率模型
- **VAE** (Variational Autoencoder): 变分自编码器，将高维数据压缩到低维潜在空间
- **UNet** (U-shaped Network): 编码器-解码器对称结构，带跳跃连接的卷积网络
- **CFG** (Classifier-Free Guidance): 无分类器引导，推理时放大条件方向的采样策略
- **CLIP** (Contrastive Language-Image Pre-training): 对比学习预训练的图文对齐模型
- **DDIM** (Denoising Diffusion Implicit Models): 确定性采样方法，可跳步加速推理
- **SDE** (Stochastic Differential Equation): 随机微分方程，统一描述扩散过程的连续时间框架
- **ODE** (Ordinary Differential Equation): 常微分方程，DDIM 对应的确定性轨迹
- **ControlNet** (ControlNet): 通过零卷积渐进式注入空间控制信号的网络结构
- **IP-Adapter** (Image Prompt Adapter): 通过额外 cross-attention 层注入图像风格参考
- **Score Function** (Score Function): 数据分布的对数梯度，指向密度增大方向

## 1. 数学符号与基础概念

在深入 Diffusion 模型之前，先明确几个核心数学符号的含义。

### $\mathcal{N}$ -- 高斯分布 (Gaussian Distribution)

$\mathcal{N}(x;\, \mu,\, \sigma^2)$ 表示变量 $x$ 服从均值为 $\mu$、方差为 $\sigma^2$ 的正态分布。

当我们写 $q(x_t \mid x_0) = \mathcal{N}(x_t;\, \sqrt{\bar{\alpha}_t}\, x_0,\; (1 - \bar{\alpha}_t)\, \mathbf{I})$ 时：

- $x_t$ 是随机变量（第 $t$ 步的噪声图像）

- 均值 = $\sqrt{\bar{\alpha}_t}\, x_0$（原始图像被缩放）

- 协方差矩阵 = $(1 - \bar{\alpha}_t)\, \mathbf{I}$（各维度独立同方差噪声）

### $\mathbf{I}$ -- 单位矩阵 (Identity Matrix)

图像是高维数据（如 64x64x4 = 16,384 维）。$\mathbf{I}$ 是对应维度的单位矩阵，意味着：

- **每个维度（每个像素/通道）的噪声是独立的**

- **每个维度的噪声方差相同**

即我们往每个像素上加同等大小的、互不相关的高斯噪声。

## 2. 前向过程: 逐步加噪与方差守恒

**DDPM** 的前向过程将干净图像 $x_0$ 逐步加噪，经过 $T$ 步变成纯高斯噪声。

### 单步加噪

每一步在前一步结果上加少量高斯噪声，$\beta_t \in (0, 1)$ 控制噪声强度：

单步加噪公式: 将前一步图像缩放 (信号衰减) 并加入方差为 beta_t 的噪声

$$q(x_t \mid x_{t-1}) = \mathcal{N}(x_t;\, \sqrt{1 - \beta_t}\, x_{t-1},\; \beta_t \mathbf{I})$$

### 重参数化技巧: 一步跳到任意 $t$

定义累积量：$\alpha_t = 1 - \beta_t$，$\bar{\alpha}_t = \prod_{s=1}^{t} \alpha_s$（累积信号保留率）。

利用高斯分布的叠加性质，可以从 $x_0$ 直接采样 $x_t$，无需逐步迭代：

一步采样公式: 信号部分 (根号alpha_bar * x_0) + 噪声部分 (根号(1-alpha_bar) * epsilon)

$$x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})$$

**关键洞察:** 当 $t \to T$ 时，$\bar{\alpha}_T \to 0$，所以 $x_T \approx \epsilon$（纯噪声）。

### 方差守恒: 为什么系数带根号？

前向过程的核心约束是**总方差保持不变**（假设 $\text{Var}(x_0) = 1$）：

方差守恒验证: 信号方差 + 噪声方差 = 1，总能量不变

$$\text{Var}(x_t) = (\sqrt{\bar{\alpha}_t})^2 \cdot 1 + (\sqrt{1-\bar{\alpha}_t})^2 \cdot 1 = \bar{\alpha}_t + (1-\bar{\alpha}_t) = 1$$

**标准差 vs 方差的区别** -- 这是常见混淆点：

| 层面 | 信号部分 | 噪声部分 |
|------|---------|---------|
| **采样公式**（操作数值，用标准差） | $\sqrt{\bar{\alpha}_t} \cdot x_0$ | $\sqrt{1-\bar{\alpha}_t} \cdot \epsilon$ |
| **分布表达**（描述统计量，用方差） | 均值 = $\sqrt{\bar{\alpha}_t}\, x_0$ | 方差 = $(1-\bar{\alpha}_t)\,\mathbf{I}$ |

**直觉总结:** 前向过程的本质是**在保持总方差守恒的前提下，逐步把信号能量转移成噪声能量**。

## 3. 噪声调度 $\beta_t$ 的本质

### $\beta_t$ 是预设的，不是学习的

在原始 **DDPM** 中，$\beta_t$ 从 $\beta_1 = 10^{-4}$ 到 $\beta_T = 0.02$ 线性插值，$T = 1000$ 步。这些数值是经验性选择的，**训练前完全固定，训练和推理用同一套**。

### 推理时 $\beta_t$ 不会动态调整

图像逐步变清晰，不是因为 $\beta_t$ 在变小，而是因为：

- 早期（$t$ 大）：图像几乎全是噪声，网络做**粗略轮廓恢复**

- 后期（$t$ 小）：图像已比较清晰，网络做**细节精修**

- 每步减去的噪声量自然递减，因为剩余噪声越来越少

### 所有变量都是 $t$ 的确定函数

| 变量 | 含义 | 由 $t$ 决定？ |
|------|------|-------------|
| $\beta_t$ | 单步噪声强度 | 由 schedule 查表 |
| $\alpha_t = 1-\beta_t$ | 单步信号保留率 | 是 |
| $\bar{\alpha}_t = \prod \alpha_s$ | 累积信号保留率 | 是 |
| $\sigma_t^2$ | 反向过程方差 | 通常设为 $\beta_t$ 或 $\tilde{\beta}_t$ |

**$t$ 是唯一的时钟，所有调度参数都是 $t$ 的确定函数，训练前就全部算好存成查找表。** 网络唯一要学的是 $\epsilon_\theta(x_t, t)$ -- 给定噪声图和时钟，预测噪声。

### Cosine vs Linear Schedule

- **Linear**: $\beta_t$ 从 $10^{-4}$ 线性增到 $0.02$。问题：后期 $\bar{\alpha}_t$ 骤降，信息突然消失

- **Cosine**: 先设计 $\bar{\alpha}_t$ 的形状（余弦曲线），再反推 $\beta_t$。信息销毁更均匀

**设计哲学:** Cosine schedule 是"先定义行为再推参数"的典范。

## 4. 为什么需要显式建模时间步 $t$

### 只告诉网络 $\beta_t$ 不够

$\beta_t$ 只描述**单步噪声增量**，但网络需要知道的是**累积到现在，这张图被噪了多少** -- 这由 $\bar{\alpha}_t$ 描述，而 $\bar{\alpha}_t$ 是 $t$ 的函数。

### 直觉

- **$t = 990$**: 图像几乎是纯噪声，网络需要大胆地预测大幅度噪声

- **$t = 10$**: 图像只有轻微噪声，网络需要精细地预测微弱噪声

如果不告诉网络 $t$，它无法知道当前图片的噪声程度。同一张模糊的图，可能是 $t=500$ 的猫，也可能是 $t=200$ 的雾。网络需要 $t$ 来**校准预测尺度**。

### Sinusoidal Embedding: 整数 $t$ -> 高维向量

直接把标量 $t=500$ 丢给网络效果不好（数值尺度问题）。用和 Transformer 位置编码相同的方法：

Sinusoidal 时间编码: 低频分量区分大阶段 (t=10 vs t=990), 高频分量区分相邻步 (t=500 vs t=501)

$$\text{emb}(t)_{2i} = \sin\!\left(\frac{t}{10000^{2i/d}}\right), \quad \text{emb}(t)_{2i+1} = \cos\!\left(\frac{t}{10000^{2i/d}}\right)$$

再接一个可学习 MLP 变换: $t_{\text{emb}} = \text{MLP}(\text{sinusoidal}(t))$（典型: 256维 -> Linear -> SiLU -> Linear -> 256维）

### Scale + Shift 注入: 在每个 ResBlock 中调制特征

```
ResNet Block 前向过程:
1. h = Conv(x)                      # 正常卷积
2. h = GroupNorm(h)                  # 归一化
3. scale, shift = Linear(t_emb)      # 时间向量 -> 两组参数
4. h = scale * h + shift             # 用时间信息调制特征
5. h = activation(h)
6. h = Conv(h)                       # 再一次卷积
```

**直觉:** 这在告诉每一层 -- "现在是第500步，噪声程度是这样的，请相应调整你的特征处理方式。"

这也是为什么**一个 **UNet** 能处理所有 $T$ 个时间步** -- 它不是 $T$ 个不同的网络，而是一个网络通过时间条件化来适应不同的去噪难度。

## 5. 反向过程: 从噪声生成图像

### 核心思想

训练一个神经网络 $\epsilon_\theta(x_t, t)$ 来预测加在 $x_t$ 上的噪声 $\epsilon$。

### 训练目标 (简化 MSE Loss)

训练损失: 预测噪声与真实噪声的均方误差。极简但高效。

$$\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\!\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]$$

**为什么预测噪声 $\epsilon$ 而非直接预测 $x_0$?**

- $\epsilon$-prediction 的方差更小、训练更稳定

- 等价于估计 **Score Function** $\nabla_x \log p_t(x)$（见后文 **SDE** 统一框架）

### 采样算法 (DDPM)

从纯噪声 $x_T \sim \mathcal{N}(0, \mathbf{I})$ 开始，逐步去噪：


```python
# DDPM 采样伪代码
x = x_T  # 从纯噪声开始
for t in range(T, 0, -1):
    predicted_noise = UNet(x, t)
    x = denoise_step(x, predicted_noise, t)  # 用 beta_t 系数还原
    if t > 1:
        x += sigma_t * z  # z ~ N(0, I), 加少量随机噪声
return x  # x_0, 最终生成的干净图片
```



## 6. Latent Diffusion / Stable Diffusion Pipeline

### 核心创新: 在潜在空间做扩散

直接在像素空间（512x512x3 = 786,432维）做扩散计算量巨大。**Stable Diffusion** 的核心思路: 先用 **VAE** 将图像压缩到低维潜在空间，在那里做扩散。

### 完整推理 Pipeline

<div style="background:#f8f9fa; padding:16px; border-radius:8px; margin:16px 0; font-family:monospace; text-align:center;"><div style="display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap;"><span style="background:#4a90d9; padding:6px 12px; border-radius:4px; color:white;">Text Prompt</span><span style="color:#666;">-></span><span style="background:#6b4c9a; padding:6px 12px; border-radius:4px; color:white;">**CLIP** Text Encoder</span><span style="color:#666;">-></span><span style="background:#d4a843; padding:6px 12px; border-radius:4px; color:white;">Cross-Attention</span><span style="color:#666;">-></span><span style="background:#c0392b; padding:6px 12px; border-radius:4px; color:white;">UNet (iterative denoise)</span><span style="color:#666;">-></span><span style="background:#27ae60; padding:6px 12px; border-radius:4px; color:white;">**VAE** Decoder</span><span style="color:#666;">-></span><span style="background:#2c3e50; padding:6px 12px; border-radius:4px; color:white;">Pixel Image</span></div></div>

### 关键数字

| 指标 | 数值 |
|------|------|
| 像素分辨率 | 512x512 (v1.5), 1024x1024 (SDXL) |
| Latent 维度 | 64x64x4 |
| VAE 空间降采样 | 8x |
| 压缩比 | ~48x (786,432 -> 16,384) |

### Cross-Attention: 文本如何控制图像

在 UNet 的每个 attention 层中：

- **Query** 来自 noisy latent（图像问："我这个位置应该生成什么？"）

- **Key/Value** 来自 CLIP text embedding（文本答："这里应该是猫的耳朵"）

每个图像位置可以自由关注任意文本 token，实现灵活的语义对齐。

## 7. Classifier-Free Guidance (**CFG**)

**CFG** 是一种**推理策略**（不改网络结构），通过放大条件方向来增强生成质量。

### 训练: 随机丢弃条件

训练时以一定概率（如 10%）用空条件 $\varnothing$ 替代文本条件，让同一个网络同时学会 conditional 和 unconditional 生成。

### 推理公式

CFG 公式: unconditional 预测 + w 倍的 (conditional - unconditional) 方向

$$\hat{\epsilon} = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))$$

- $w$ 是 **guidance scale**:

  - $w = 1$: 标准 conditional generation

  - $w = 7.5$（典型值）: 增强文本一致性，图像更"听话"但多样性下降

  - $w$ 过大: 出现 artifacts（过饱和、不自然）

  - $w < 1$: 更自由，多样性增加但可能偏离 prompt

- **代价**: 每步需要两次前向传播（一次 conditional，一次 unconditional），推理成本 2x

## 8. 条件注入方式全景

不同类型的条件需要不同的注入机制。这是面试中展示系统性理解的好机会。

| 条件类型 | 注入方式 | 原因 |
|---------|---------|------|
| **文本描述** | Cross-Attention (Q=图像, K/V=文本) | 语义级别，非空间对齐。图像每个位置自由关注任意词 |
| **边缘/深度/姿态图** | **ControlNet** (特征逐层相加) | 空间对齐，像素级对应。左上角边缘 -> 左上角内容 |
| **遮罩/参考图 (inpainting)** | Channel concatenation (通道拼接) | 直接空间输入，输入通道从 4 -> 9 |
| **风格参考图** | **IP-Adapter** (额外 cross-attn 层) | 全局风格，不需空间对齐，与文本 cross-attn 并行 |
| **放大文本效果** | **CFG** (推理策略) | 不改结构，只改采样 |

### 为什么空间对齐的条件不用 Cross-Attention?

Cross-Attention 的优势在于**灵活的、非对齐的关联** -- "cat" 可以影响图像任何位置。但对于边缘图这种**像素级一一对应**的条件，逐层特征相加比 attention 更直接、更精确。

## 9. **ControlNet** 的 Zero Convolution 设计哲学

### 架构

```
控制信号 (边缘图)
      |
UNet Encoder 副本 -> 特征 f
      | (zero conv: 1x1卷积, 初始权重=0)
原始 UNet <- 正常接收 z_t, t, text
      |
h_new = h + 0*f = h    <- 训练初始，完全不受影响
```

### 1x1 卷积是什么?

本质是**逐像素的线性变换** -- 不看邻居像素，只在**通道维度**上做线性组合。用 1x1 卷积是因为空间信息已由 ControlNet 副本的正常卷积处理好了。

### 为什么初始权重为 0?

**核心问题:** 原始 UNet 是花巨大算力预训练好的。如果一上来就用随机权重往里加东西，等于往精密系统注入随机噪声 -- **预训练能力会被立刻破坏**。

Zero conv 保证了:

1. **训练第 0 步**: ControlNet 完全透明，原始 UNet 照常工作

2. **训练逐步进行**: 权重从 0 **自然增长**，控制信号渐进式引入

3. **训练结束**: 权重长到合适大小，ControlNet 有效施加空间控制

### 权重增长是自动的，不是人为调度的

| | Scheduled LR | Zero Conv |
|---|---|---|
| 谁控制变化 | 人为预设的 schedule | 梯度下降自动学习 |
| 控制什么 | 所有参数的学习率 | 特定连接的权重值本身 |
| 需要调参 | 需要选 schedule 和超参 | 不需要，初始化为 0 即可 |
| 最终值 | LR 通常趋向 0 | 权重长到任务需要的大小 |

**设计哲学:** "不破坏已有能力，渐进式引入新能力" -- 与 LoRA 的零初始化、residual connection 一脉相承。

## 10. DDPM vs DDIM 深度解析：从原理到直觉

> DDPM 和 DDIM 用**同一个模型、同一套训练**，区别**仅在推理时的采样策略**：DDPM 把反向去噪建模为"从分布中采样"（随机过程），DDIM 把它建模为"沿确定性路径求解"（确定性映射）。

### 10.1 共同的训练过程（两者完全一致）

无论 **DDPM (Denoising Diffusion Probabilistic Models)** 还是 **DDIM (Denoising Diffusion Implicit Models)**，训练时做的事完全一样：

1. 取一张干净图片 $x_0$
2. 随机采样时间步 $t \in \{1, 2, \ldots, T\}$
3. 随机采样噪声 $\epsilon \sim \mathcal{N}(0, \mathbf{I})$
4. 用闭式公式生成含噪图片：

$$
x_t = \sqrt{\bar{\alpha}_t} \cdot x_0 + \sqrt{1 - \bar{\alpha}_t} \cdot \epsilon
$$

5. 让 UNet 预测噪声：$\epsilon_\theta(x_t, t)$
6. 损失函数：$L = \|\epsilon - \epsilon_\theta(x_t, t)\|^2$

**关键认知**：UNet 学的能力是"给定任意噪声程度的图片，告诉你噪声长什么样"。它不知道、也不关心你后面怎么采样。

### 10.2 核心概念：predicted mean 与 $x_0$ 估计

#### 从噪声预测到 $x_0$ 估计

UNet 输出的是预测噪声 $\epsilon_\theta$，但我们可以立即反推出对原始干净图片的估计：

$$
\hat{x}_0 = \frac{x_t - \sqrt{1 - \bar{\alpha}_t} \cdot \epsilon_\theta}{\sqrt{\bar{\alpha}_t}}
$$

#### 从 $x_0$ 估计到 predicted mean

**Predicted mean** $\mu_\theta$ 就是利用这个 $\hat{x}_0$ 估计，计算出"$x_{t-1}$ 最可能在哪"：

$$
\mu_\theta(x_t, t) = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{1 - \alpha_t}{\sqrt{1 - \bar{\alpha}_t}} \cdot \epsilon_\theta \right)
$$

**直觉**：从含噪图片中，按比例减掉 UNet 预测的噪声，得到"少一步噪声后的最佳估计位置"。

### 10.3 唯一的区别：推理时加不加随机噪声

| | DDPM | DDIM |
|---|---|---|
| 采样公式 | $x_{t-1} = \mu_\theta + \sigma_t \cdot z \quad (z \sim \mathcal{N}(0, \mathbf{I}))$ | $x_{t-1} = \mu_\theta$ |
| 数学本质 | 求解随机微分方程 (**SDE**, Stochastic Differential Equation) | 求解常微分方程 (**ODE**, Ordinary Differential Equation) |
| 每步行为 | 在 predicted mean 附近随机游走 | 精确落在 predicted mean 上 |
| 同一起点 | 每次生成不同图片 | 永远生成同一张图片 |

### 10.4 为什么 DDPM 要加随机噪声？

这不是人为的技巧，而是理论推导的结果。DDPM 的设计哲学是**忠实建模反向过程的概率分布**。数学上可以证明，正向加噪过程的真实反向后验：

$$
q(x_{t-1} \mid x_t, x_0) = \mathcal{N}(\tilde{\mu}_t, \tilde{\sigma}_t^2 \mathbf{I})
$$

这个后验**本身就是一个有方差的高斯分布**——从 $x_t$ 到 $x_{t-1}$ 存在多条合理路径。

随机性带来的优势：
- **理论纯洁性**：完整的变分推断框架，训练目标是 **ELBO (Evidence Lower Bound)** 的严格推导
- **生成多样性**：同一个起始噪声能生成不同图片
- **鲁棒性**：每步的随机扰动起到"纠错"作用，对 UNet 预测误差有一定容忍度

### 10.5 DDIM 凭什么可以去掉方差？

**核心洞察**：DDPM 的训练目标（噪声预测的 **MSE (Mean Squared Error)** 损失）**只依赖于边际分布** $q(x_t \mid x_0)$，不依赖于中间步骤的联合分布 $q(x_{t-1}, x_t \mid x_0)$。

这意味着：训练时模型学到的能力，跟反向过程是否随机无关。

DDIM 据此构造了一个**非马尔可夫**的反向过程：边际分布和 DDPM 完全一致，但反向过程的方差为零。等价的轨迹，确定性的路径。

### 10.6 为什么确定性就能跳步？

**DDPM 必须逐步走**：每步加了随机噪声 $\sigma_t \cdot z$，让 $x_{t-1}$ 偏离了"光滑轨迹"。跳大步时，随机偏移累积，导致 $x_0$ 估计越来越不稳定。

*类比：浓雾中下山，每步看指南针走一步，但风会随机吹偏你。步子太大 -> 累积偏移 -> 迷路。*

**DDIM 可以跳步**：没有随机偏移，轨迹是一条光滑的确定性曲线（ODE 的解）。DDIM 跳步的逻辑：

1. 在 $t=1000$，用 UNet 估计 $x_0$（很粗糙）
2. 用这个估计 + 目标时间步的噪声水平，直接算出 $x_{t'}$
3. 在 $t'=800$，重新估计 $x_0$（更准了）
4. 继续跳...

**每一步都是"重新估计 $x_0$，然后跳到目标时间步"**。

*类比：没有风，步子再大也能精确到达目标点。*

- DDPM: $t = 1000, 999, 998, \ldots$ (1000步)
- DDIM: $t = 1000, 800, 600, 400, 200, 0$ (5步)
- 实践中 **20-50 步**即可接近 DDPM 质量，速度提升 20-50x

### 10.7 DDIM 的额外能力: Latent 插值

确定性采样意味着**同一噪声输入永远生成同一张图**，latent 空间变得有意义:

$$
z_{\text{interp}} = (1-\lambda)\, z_A + \lambda\, z_B
$$

对两个 latent 做线性插值后采样，得到平滑过渡。DDPM 的随机采样无法做到。

> DDIM 还提供了一个参数 $\eta \in [0, 1]$，可以在两者之间连续插值：$\eta=0$ 是完全确定性的 DDIM，$\eta=1$ 退化回 DDPM。

### 10.8 最终框架对比

| 维度 | DDPM | DDIM |
|---|---|---|
| **对反向过程的理解** | 概率分布采样 | 确定性映射求解 |
| **数学框架** | SDE（随机微分方程） | ODE（常微分方程） |
| **训练** | 完全相同 | 完全相同 |
| **模型** | 同一个 UNet | 同一个 UNet |
| **每步采样** | $\mu_\theta + \sigma_t \cdot z$ | $\mu_\theta$ |
| **步数** | ~1000 步 | ~20-50 步 |
| **多样性** | 高（同一起点 -> 不同图片） | 无（同一起点 -> 同一张图片） |
| **可控性** | 较弱 | 强（确定性 -> 可插值潜空间） |
| **设计哲学** | 理论严谨：忠实建模后验分布 | 实用优先：等价轨迹，最大加速 |

### 10.9 SDE 统一框架 (面试概念级)

将扩散过程从离散推广到连续时间:

- **前向 SDE**: $dx = f(x,t)\,dt + g(t)\,dw$ (加噪)
- **反向 SDE**: $dx = [f(x,t) - g(t)^2 \nabla_x \log p_t(x)]\,dt + g(t)\,d\bar{w}$ (去噪)

其中 $\nabla_x \log p_t(x)$ 是 **Score Function（得分函数）** -- 指向数据密度增大的方向。

| 方法 | 在 SDE 框架中的角色 |
|------|-------------------|
| DDPM | 反向 SDE 的离散化，带随机项 |
| DDIM | 反向 SDE 对应的 **Probability Flow ODE** |
| Score Matching | 直接训练网络估计 Score Function |

预测噪声就等价于估计 Score Function，只差一个和 $\bar{\alpha}_t$ 相关的缩放系数：

$$
\nabla_x \log p_t(x) = -\frac{\epsilon_\theta(x_t, t)}{\sqrt{1 - \bar{\alpha}_t}}
$$

### 面试速记（30秒版本）

1. **训练**（同一个）：UNet 学预测噪声，跟采样策略无关
2. **$x_0$ 估计**：UNet 在任意时间步都能估计原图，多步迭代只是逐步精化
3. **分歧**：DDPM 加随机噪声（理论正确），DDIM 去掉噪声（不影响训练目标）
4. **跳步**：有噪声=随机游走必须小步，无噪声=光滑曲线可大步跳
5. **比喻**：同一张地图，DDPM 雨中小步走（随机、慢、每次不同），DDIM 晴天大步跨（确定、快、路径唯一）


## 13. 为什么预测噪声而不是预测 $x_0$: 深度分析

DDPM 的训练目标是预测加入的噪声 $\epsilon$，而非直接预测干净图像 $x_0$。这个选择有深刻的数学原因。

### 13.1 方差分析: $\epsilon$-prediction 的优势

三种等价的参数化方式:
- **$\epsilon$-prediction**: 网络预测添加的噪声 $\epsilon_\theta(x_t, t)$
- **$x_0$-prediction**: 网络直接预测干净图像 $\hat{x}_0(x_t, t)$
- **$v$-prediction**: 网络预测 $v = \sqrt{\bar{\alpha}_t}\,\epsilon - \sqrt{1-\bar{\alpha}_t}\,x_0$

**关键差异在于目标的方差**:

$\epsilon$-prediction 的目标方差恒定:

$$\text{Var}[\epsilon] = \mathbf{I} \quad \text{(constant across all } t\text{)}$$

$x_0$-prediction 的目标方差随 $t$ 变化，在 $t$ 接近 $T$ 时趋向无穷:

$$\text{Var}[x_0 \mid x_t] = \frac{1-\bar{\alpha}_t}{\bar{\alpha}_t} \mathbf{I} \quad \text{(varies with } t\text{, explodes as } \bar{\alpha}_t \to 0\text{)}$$

**直觉**: 当 $t$ 很大时 (图像几乎是纯噪声)，要从 $x_t$ 预测 $x_0$ 相当于从噪声中凭空重建原图 -- 目标方差极大，梯度不稳定。而预测噪声 $\epsilon$ 的目标始终是单位方差的标准高斯噪声，loss landscape 更平滑。

### 13.2 与 Score Matching 的等价性

Score function 定义为对数概率的梯度:

预测噪声等价于估计 score function，仅差一个缩放系数:

$$\nabla_{x_t} \log p_t(x_t) = -\frac{\epsilon}{\sqrt{1-\bar{\alpha}_t}} \approx -\frac{\epsilon_\theta(x_t, t)}{\sqrt{1-\bar{\alpha}_t}}$$

这意味着 DDPM 的 $\epsilon$-prediction 训练等价于 **denoising score matching** (Vincent 2011)。Score function 指向数据密度增加最快的方向 -- 从噪声走向数据。预测 $\epsilon$ 就是在估计这个方向。

**统一视角**: DDPM ($\epsilon$-prediction) = Score Matching (估计 score) = SDE 反向过程 (Langevin dynamics)，三者殊途同归。

### 13.3 $v$-prediction: 折中方案 (Salimans & Ho, 2022)

$v$-prediction 定义目标为:

$v$ 是噪声和信号的加权组合，权重随 $t$ 平滑变化:

$$v_t = \sqrt{\bar{\alpha}_t}\,\epsilon - \sqrt{1-\bar{\alpha}_t}\,x_0$$

**优势**:
- 在 $t \approx 0$ (几乎无噪声) 时，$v \approx -x_0$，网络预测信号
- 在 $t \approx T$ (纯噪声) 时，$v \approx \epsilon$，网络预测噪声
- 方差在所有 $t$ 上近似均匀，训练更稳定
- Stable Diffusion v2 和 SDXL 的部分训练使用 $v$-prediction

### 13.4 三种参数化的转换关系

给定 $x_t$, $t$, 和网络输出，三种参数化可以互相转换:

- 从 $\hat{\epsilon}$ 恢复: $\hat{x}_0 = (x_t - \sqrt{1-\bar{\alpha}_t}\,\hat{\epsilon}) / \sqrt{\bar{\alpha}_t}$
- 从 $\hat{x}_0$ 恢复: $\hat{\epsilon} = (x_t - \sqrt{\bar{\alpha}_t}\,\hat{x}_0) / \sqrt{1-\bar{\alpha}_t}$
- 从 $\hat{v}$ 恢复: $\hat{x}_0 = \sqrt{\bar{\alpha}_t}\,x_t - \sqrt{1-\bar{\alpha}_t}\,\hat{v}$

**三种参数化方式对比**

| 参数化 | 目标方差 | 训练稳定性 | SNR 加权 | 代表模型 |
| --- | --- | --- | --- | --- |
| $\epsilon$-prediction | 恒定 ($\mathbf{I}$) | 高 (均匀 loss) | 高 SNR 时段权重过大 | DDPM, SD v1.x |
| $x_0$-prediction | 随 $t$ 增大而爆炸 | 低 ($t$ 大时不稳定) | 低 SNR 时段权重过大 | DALL-E (部分) |
| $v$-prediction | 近似均匀 | 最高 | 近似均匀加权 | SD v2, SDXL, Imagen Video |

## 14. **VAE** 深度解析: Stable Diffusion 的潜在空间引擎

Stable Diffusion 在 **潜在空间** 而非像素空间做扩散，而将图像映射到潜在空间的正是 VAE (Variational Autoencoder)。理解 VAE 的数学原理对理解整个 pipeline 至关重要。

### 14.1 VAE 的 Encoder-Decoder 架构

**Encoder** $q_\phi(z|x)$: 将图像 $x \in \mathbb{R}^{H \times W \times 3}$ 映射到潜在分布的参数 $(\mu, \sigma^2)$，其中 $\mu, \log\sigma^2 \in \mathbb{R}^{h \times w \times c}$ (SD 中 $h = H/8, w = W/8, c = 4$)。

**Decoder** $p_\theta(x|z)$: 从潜在向量 $z$ 重建图像。

**关键区别 vs 普通 Autoencoder**: VAE 的 encoder 输出的不是确定性向量，而是一个**概率分布的参数**。每次采样得到不同的 $z$，迫使 decoder 在整个潜在区域都学会重建，而不是死记单个点。

### 14.2 KL 散度正则化

VAE 的 loss 由两部分组成:

VAE 的 ELBO (Evidence Lower Bound) loss:

$$\mathcal{L}_{\text{VAE}} = \underbrace{\mathbb{E}_{z \sim q_\phi(z|x)}\big[-\log p_\theta(x|z)\big]}_{\text{Reconstruction Loss}} + \underbrace{D_{\text{KL}}\big(q_\phi(z|x) \| \mathcal{N}(0, \mathbf{I})\big)}_{\text{KL Regularization}}$$

**Reconstruction Loss**: 衡量重建质量 (像素级 MSE 或感知 loss)。

**KL Divergence**: 强制 encoder 输出的分布接近标准正态 $\mathcal{N}(0, \mathbf{I})$。

**KL 的闭式解** (两个高斯之间):

对每个潜在维度 $j$ 独立计算，无需采样估计:

$$D_{\text{KL}} = -\frac{1}{2} \sum_{j=1}^{d} \left(1 + \log\sigma_j^2 - \mu_j^2 - \sigma_j^2\right)$$

**为什么正则化到 $\mathcal{N}(0, \mathbf{I})$?**
- 保证潜在空间是**连续的** (相近的 $z$ 解码为相似图像) 和**完整的** (任意采样的 $z$ 都能解码为合理图像)
- 没有 KL 正则化，encoder 会把不同类别映射到互相远离的孤立点，中间区域decoder 无法处理
- 这正是 VAE 可以做生成 (而普通 AE 不行) 的核心原因

### 14.3 重参数化技巧 (Reparameterization Trick)

**问题**: 从 $z \sim q_\phi(z|x) = \mathcal{N}(\mu, \sigma^2)$ 采样是不可微的操作，无法反向传播。

**解决方案**: 将随机性分离到外部噪声:

重参数化: 采样过程变为确定性变换 + 外部随机噪声:

$$z = \mu + \sigma \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})$$

**关键洞察**:
- $\epsilon$ 与模型参数无关，梯度可以通过 $\mu$ 和 $\sigma$ 正常传播
- 这将不可微的「采样」操作转化为可微的「线性变换」
- 训练时每次前向传播采样不同的 $\epsilon$，等价于对 ELBO 做 Monte Carlo 估计
- 推理时可以直接用 $z = \mu$ (取均值) 或采样多次取平均

### 14.4 $\beta$-VAE: 控制重建与正则化的平衡

原始 VAE 中 KL 项权重为 1，但实践中常需要调整:

$\beta$-VAE 引入超参数 $\beta$ 控制正则化强度:

$$\mathcal{L}_{\beta\text{-VAE}} = \text{Reconstruction Loss} + \beta \cdot D_{\text{KL}}$$

- $\beta > 1$: 更强的正则化，潜在空间更平滑可插值，但重建质量下降 (更模糊)
- $\beta < 1$: 更好的重建质量，但潜在空间可能不连续
- $\beta = 0$: 退化为普通 Autoencoder (没有生成能力)

**Stable Diffusion 的选择**: SD 使用较小的 KL 权重 (约 $10^{-6}$)，因为潜在空间的平滑性由扩散模型进一步保证，VAE 侧重高质量重建。

### 14.5 VAE vs **VQ-VAE**: 连续 vs 离散潜在空间

**VAE vs VQ-VAE 对比**

| 特征 | VAE | VQ-VAE |
| --- | --- | --- |
| 潜在表示 | 连续向量 $z \in \mathbb{R}^d$ | 离散 codebook index $z_q \in \{1,...,K\}$ |
| 正则化 | KL divergence to $\mathcal{N}(0,\mathbf{I})$ | Codebook commitment loss + EMA update |
| 采样方式 | 重参数化技巧 | Straight-through estimator |
| 潜在空间性质 | 连续、可插值 | 离散、组合式 |
| 典型应用 | Stable Diffusion (latent space) | DALL-E (image tokenizer), AudioLM |
| 优势 | 平滑的潜在空间，易于与扩散模型结合 | 避免 posterior collapse，高压缩率 |
| 劣势 | 可能产生模糊重建 (KL 过强时) | Codebook collapse，需要精心调参 |


## 15. **ControlNet** 架构与训练深度解析

第 9 节介绍了 ControlNet 的 Zero Convolution 设计哲学。本节深入架构细节、训练流程、多 ControlNet 组合，以及与其他条件注入方法的对比。

### 15.1 ControlNet 的完整架构

ControlNet 的核心思想: **冻结原始预训练 UNet，创建一个可训练的副本(trainable copy)，通过 zero convolution 连接。**

具体结构:
1. **Locked Copy**: 原始 SD UNet 的 encoder blocks，权重冻结不更新
2. **Trainable Copy**: UNet encoder blocks 的完整拷贝，参数可训练
3. **Zero Convolution**: 1x1 卷积层，权重和偏置初始化为 0
4. **连接方式**: Trainable copy 的输出经 zero conv 后 **加到** locked copy 对应层的输出上

**数据流**:
- 条件图 (如 Canny edge) 经过轻量 encoder 后输入 trainable copy
- Trainable copy 处理条件信息，输出经 zero conv (初始为 0)
- Zero conv 输出加到 frozen UNet 的 skip connections 和 middle block 上
- 训练初期 zero conv 输出为 0，等于没加条件 -> 不破坏预训练权重
- 随训练进行，zero conv 权重逐渐增大 -> 条件信号逐渐注入

### 15.2 训练流程

**Step 1**: 冻结原始 SD UNet 的所有参数

**Step 2**: 克隆 UNet encoder (约 50% 的参数) 作为 trainable copy

**Step 3**: 在每个连接点插入 zero convolution (1x1 conv, weight=0, bias=0)

**Step 4**: 训练数据为 (image, condition, prompt) 三元组

**训练 loss**: 与标准 SD 相同的 $\epsilon$-prediction MSE loss，只是输入额外包含条件图

**训练量**: 在单个条件类型 (如 Canny) 上，使用 8 张 A100 训练约 600 GPU-hours。远小于从头训练 SD (约 150,000 GPU-hours)，这是 ControlNet 设计的核心价值。

**为什么克隆 encoder 而不是从头训练?**
- 克隆保留了 SD 学到的图像理解能力
- 只需要学习如何将条件信息对齐到这些特征上
- 训练从「不改变任何输出」(zero conv) 开始，安全地渐进式学习

### 15.3 多 ControlNet 组合

可以同时使用多个 ControlNet (如 pose + depth + canny):

**组合方式**: 每个 ControlNet 独立处理自己的条件图，输出通过加权求和后加到 UNet:

$\text{output} = \text{UNet}(x_t) + \sum_i w_i \cdot \text{ControlNet}_i(x_t, c_i)$

其中 $w_i$ 是每个 ControlNet 的权重 (condition scale)。

**实践建议**:
- 权重总和建议在 1.0-1.5 之间，过大会产生伪影
- 互补条件效果好 (pose + depth)，冗余条件可能冲突 (两种 edge)
- 推理速度随 ControlNet 数量线性增加

### 15.4 T2I-Adapter vs ControlNet

**ControlNet vs T2I-Adapter 对比**

| 特征 | ControlNet | T2I-Adapter |
| --- | --- | --- |
| 参数量 | 约 361M (UNet encoder 的完整拷贝) | 约 77M (轻量级 adapter) |
| 训练策略 | 冻结原始 UNet + 训练完整 copy | 冻结原始 UNet + 训练小型 adapter |
| 连接方式 | 加到 skip connections + middle block | 加到 encoder 的中间特征 |
| Zero Conv | 使用 (渐进式注入) | 不使用 (直接加法) |
| 条件控制精度 | 高 (完整 encoder 容量) | 中等 (参数量有限) |
| 训练成本 | 约 600 GPU-hours (A100) | 约 100 GPU-hours |
| 多条件组合 | 加权求和 | 加权求和 (更轻量) |


## 15. ControlNet (续): **IP-Adapter** 架构

### 15.5 IP-Adapter: 图像作为 Prompt

IP-Adapter (Image Prompt Adapter) 允许用一张参考图像作为生成条件，与 ControlNet 的空间条件 (edge, pose) 不同，它提取的是**语义风格信息**。

**架构**:
1. **Image Encoder**: 使用 CLIP image encoder 提取参考图像的特征向量
2. **Projection Network**: 线性层将 CLIP 特征投影到与文本 embedding 相同的维度
3. **Decoupled Cross-Attention**: 关键创新 -- 不与文本 token 共享 cross-attention，而是新增一组独立的 K/V 投影层:

$\text{Attn}_{\text{text}} = \text{softmax}(QK_t^\top/\sqrt{d})V_t$

$\text{Attn}_{\text{image}} = \text{softmax}(QK_i^\top/\sqrt{d})V_i$

$\text{output} = \text{Attn}_{\text{text}} + \lambda \cdot \text{Attn}_{\text{image}}$

其中 $K_t, V_t$ 是文本分支的 K/V (冻结)，$K_i, V_i$ 是图像分支新增的 K/V (可训练)，$\lambda$ 控制图像条件的强度。

**为什么用 Decoupled Cross-Attention?**
- 如果图像特征和文本 token 拼接后共享 attention，两种模态会互相干扰
- 独立的 K/V 让图像信息有自己的「通道」，不影响文本理解能力
- 训练时只需训练图像分支的 K/V 投影 + projection network，非常高效

## 16. 图像生成产业格局与技术演进

面试中常被问到对行业的理解。以下是截至 2024 年底的主要玩家和技术趋势。

### 16.1 主要产品与公司

**主要图像生成产品对比 (2024)**

| 产品 | 公司 | 架构 | 特点 | 开源 |
| --- | --- | --- | --- | --- |
| Stable Diffusion 1.x/2.x | Stability AI | UNet + CLIP | 最广泛的开源基础模型，社区生态庞大 | 是 |
| SDXL | Stability AI | UNet (更大) + dual CLIP | 更高质量，双文本 encoder | 是 |
| Stable Diffusion 3 | Stability AI | MMDiT (Multimodal **DiT**) | Transformer 替代 UNet，Flow Matching | 是 |
| Midjourney | Midjourney Inc. | 未公开 | 美学风格最强，Discord 交互 | 否 |
| DALL-E 3 | OpenAI | 未公开 (推测 DiT) | ChatGPT 集成，prompt 理解力强 | 否 |
| Adobe Firefly | Adobe | 未公开 | 企业级，版权安全 (仅用授权数据训练) | 否 |
| Imagen 2/3 | Google DeepMind | Cascaded Diffusion / DiT | 极高文本渲染能力 | 否 |
| Flux | Black Forest Labs | DiT-based | SD 原作者团队新作，高质量开源 | 部分 |
| Fooocus | 社区 | 基于 SDXL | 简化 UI，类 Midjourney 体验 | 是 |


## 16. (续): 架构演进与应用

### 16.2 架构演进: UNet -> DiT

**UNet 时代** (2020-2023):
- DDPM, SD 1.x/2.x, SDXL 均使用 UNet 作为去噪网络
- UNet 的 skip connections 天然适合「先破坏再恢复」的扩散过程
- 但 UNet 的 attention 层只占部分层，scaling 受限

**DiT 时代** (2023-至今):
- Peebles & Xie (2023) 提出 Diffusion Transformer (DiT): 用纯 Transformer 替代 UNet
- 将带噪声的图像 patch 化 (类似 ViT)，用 Transformer blocks 处理
- 时间步 $t$ 和类别条件通过 AdaLN (Adaptive Layer Norm) 注入
- **优势**: 更好的 scaling law (参数量翻倍 -> 质量持续提升)，与 LLM 共享基础设施
- SD3 的 MMDiT、Flux、DALL-E 3 (推测) 都采用 DiT 架构

**面试关键点**: 被问到「扩散模型的最新趋势」时，UNet -> DiT 的演进是核心答案。类比: CNN (视觉) -> ViT (视觉)，UNet (扩散) -> DiT (扩散)。

### 16.3 核心应用领域

1. **Text-to-Image**: 最成熟的应用，所有主要模型都支持
2. **Inpainting**: 擦除并重绘图像区域，SD 有专门的 inpaint 模型 (额外 mask channel)
3. **Outpainting**: 向外扩展图像边界，需要模型理解全局构图
4. **Image-to-Image**: 以参考图为起点，加部分噪声后重新去噪，实现风格迁移/局部修改
5. **Style Transfer**: 通过 IP-Adapter / LoRA / DreamBooth 实现风格控制
6. **Video Generation**: 将扩散过程扩展到时序维度 (Stable Video Diffusion, Sora, Kling)

**视频生成的技术挑战**:
- 时序一致性: 帧间不能闪烁或物体突变
- 计算量: 16 帧 512x512 的 latent 比单张图大 16 倍
- 训练数据: 高质量视频-文本对比图像-文本对稀缺得多

### 16.4 面试常见问题

**Q: SD 和 Midjourney 的核心差异?**
A: SD 是开源模型 (架构/权重公开)，可以 fine-tune 和部署; Midjourney 是闭源服务，美学质量领先但不可定制。企业场景通常选 SD (可控、可部署) 或 Adobe Firefly (版权安全)。

**Q: 为什么大家都在转向 Transformer 架构?**
A: 三个原因: (1) Scaling law 更优 -- Transformer 参数翻倍质量持续提升，UNet 到一定大小后收益递减; (2) 基础设施复用 -- 与 LLM 共享 GPU kernel 和推理优化; (3) 多模态统一 -- Transformer 天然处理序列，图像 patch、文本 token、音频帧都可以统一为 token 序列。

### Self-Check Questions

- [ ] 画出 Stable Diffusion 的完整推理 pipeline (Text -> CLIP -> UNet -> VAE -> Image)

> **Answer**: Stable Diffusion 推理 pipeline 分为 4 个阶段: (1) 文本编码: 用户 prompt 经过 CLIP text encoder 得到 77x768 的 token embedding 序列; (2) 噪声初始化: 在 64x64x4 的 latent space 中采样随机高斯噪声 $z_T \sim \mathcal{N}(0, \mathbf{I})$; (3) 迭代去噪: UNet 以 $z_t$、时间步 $t$、文本 embedding 为输入，预测噪声 $\epsilon_\theta$，通过 DDPM/DDIM 采样公式逐步去噪 (通常 20-50 步)，每步做两次前向传播 (CFG: 有条件 + 无条件); (4) VAE 解码: 最终 latent $z_0$ 经 VAE decoder 上采样 8 倍得到 512x512x3 的 RGB 图像。关键数字: latent 压缩比 48x (512x512x3 -> 64x64x4)，CFG 典型 $w=7.5$。

- [ ] 写出 CFG 公式并解释 guidance scale w 的影响

> **Answer**: CFG 推理公式: $\hat{\epsilon} = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))$，其中 $\epsilon_\theta(x_t, c)$ 是有条件预测，$\epsilon_\theta(x_t, \varnothing)$ 是无条件预测，$w$ 是 guidance scale。当 $w=1$ 时退化为标准条件生成; $w>1$ 时放大条件方向 (生成更符合 prompt 但多样性下降); $w$ 过大会产生过饱和伪影。训练时以 10% 概率随机丢弃条件 (用空 prompt 替代)，让模型同时学会有条件和无条件生成。典型值: SD v1.x 使用 $w=7.5$，SDXL 使用 $w=5.0$-$7.0$。

- [ ] 解释为什么在 latent space 做 diffusion 而不是 pixel space

> **Answer**: 在 pixel space 直接做 diffusion 计算量巨大: 512x512x3 = 786,432 维空间上做 UNet 前向传播。Latent Diffusion 用预训练 VAE 将图像压缩到 64x64x4 = 16,384 维 (压缩比 48 倍)，在此低维空间做扩散过程。优势有三: (1) 计算量减少约 48 倍，使消费级 GPU 可用; (2) VAE 的潜在空间已去除感知冗余 (perceptual redundancy)，只保留语义信息，扩散模型可以专注于学习语义分布; (3) VAE 只需训练一次，扩散模型和条件模块可以独立迭代。缺点是 VAE 解码会引入少量重建损失 (面部细节模糊)，但总体收益远大于代价。

- [ ] 写出训练目标 (MSE loss) 并解释为什么预测噪声而不是直接预测 x_0

> **Answer**: 简化 MSE 训练目标: $\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\big[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\big]$，其中 $x_t = \sqrt{\bar{\alpha}_t}\,x_0 + \sqrt{1-\bar{\alpha}_t}\,\epsilon$。预测噪声 ($\epsilon$-prediction) 优于预测 $x_0$ 的核心原因是**目标方差恒定**: $\text{Var}[\epsilon] = \mathbf{I}$ 在所有 $t$ 上不变; 而 $\text{Var}[x_0|x_t] = \frac{1-\bar{\alpha}_t}{\bar{\alpha}_t}\mathbf{I}$，在 $t$ 接近 $T$ 时趋向无穷，导致梯度不稳定。此外，$\epsilon$-prediction 等价于 denoising score matching: $\nabla_{x_t}\log p_t(x_t) \approx -\epsilon_\theta/\sqrt{1-\bar{\alpha}_t}$，统一了 DDPM、Score matching 和 SDE 框架。

- [ ] 解释方差守恒: 为什么采样公式的系数带根号？标准差 vs 方差的区别

> **Answer**: 前向过程公式 $x_t = \sqrt{\bar{\alpha}_t}\,x_0 + \sqrt{1-\bar{\alpha}_t}\,\epsilon$ 中系数带根号是因为在**标准差层面**操作，不是方差层面。方差守恒推导: $\text{Var}[x_t] = (\sqrt{\bar{\alpha}_t})^2 \cdot \text{Var}[x_0] + (\sqrt{1-\bar{\alpha}_t})^2 \cdot \text{Var}[\epsilon] = \bar{\alpha}_t + (1-\bar{\alpha}_t) = 1$ (假设 $\text{Var}[x_0]=1$, $\text{Var}[\epsilon]=1$)。如果不带根号而直接用 $\bar{\alpha}_t$ 和 $1-\bar{\alpha}_t$ 作系数，则方差为 $\bar{\alpha}_t^2 + (1-\bar{\alpha}_t)^2 \neq 1$，破坏分布一致性。标准差 $\sigma = \sqrt{\text{Var}}$; 混淆两者会导致加噪过强或过弱。这也是为什么 noise schedule 定义在 $\beta_t$ (方差) 但加噪公式的系数是 $\sqrt{\cdot}$ (标准差)。

- [ ] 解释 beta_t 的角色: 它是训练的还是预设的？推理时会变吗？

> **Answer**: $\beta_t$ 是**预设的超参数**，不是可学习的参数。Linear schedule 设 $\beta_1=10^{-4}$, $\beta_T=0.02$，等差递增; Cosine schedule 先定义 $\bar{\alpha}_t$ 的形状再反推 $\beta_t$。训练时 $\beta_t$ 固定不变，由此确定 $\alpha_t = 1-\beta_t$, $\bar{\alpha}_t = \prod_{s=1}^{t}\alpha_s$ 等所有相关量。推理时 $\beta_t$ 同样固定 -- 采样公式 (DDPM/DDIM) 使用与训练相同的 schedule。所有与时间相关的量 ($\beta_t, \alpha_t, \bar{\alpha}_t, \sigma_t$) 都是 $t$ 的确定函数，可以预先计算为查找表。网络唯一学习的是去噪函数 $\epsilon_\theta(x_t, t)$ 本身。

- [ ] 解释为什么 UNet 需要知道时间步 t，以及 sinusoidal embedding 的注入机制

> **Answer**: 同一个 UNet 处理从 $t=1$ (几乎无噪声) 到 $t=T$ (纯噪声) 的所有时间步，但不同噪声水平需要完全不同的去噪策略。如果不告诉网络当前 $t$，它无法判断输入的噪声程度，也无法选择正确的去噪行为。仅通过 $\beta_t$ 是不够的 -- $\beta_t$ 只描述相邻步的变化，网络需要全局噪声水平信息。注入机制: 整数 $t$ 先通过 sinusoidal embedding 映射到高维向量 (与 Transformer 的位置编码相同的公式: $\sin(t/10000^{2i/d})$, $\cos(t/10000^{2i/d})$)，再经 2 层 MLP 变换，最终在每个 ResBlock 中通过 scale + shift (AdaGN) 调制特征: $h = \gamma(t) \cdot \text{GroupNorm}(x) + \beta(t)$。这让网络在每一层都能根据 $t$ 调整行为。

- [ ] 列出 5 种条件注入方式及其适用场景 (Cross-Attention, ControlNet, concat, **IP-Adapter**, CFG)

> **Answer**: 5 种条件注入方式: (1) **Cross-Attention**: 文本条件的标准方式，$Q$ 来自图像特征，$K/V$ 来自 CLIP 文本 embedding，适合全局语义控制 (prompt 描述); (2) **ControlNet**: 通过冻结 UNet + 可训练副本 + zero conv 注入空间条件 (Canny edge, pose, depth map)，精确控制空间结构; (3) **Concat (通道拼接)**: 将条件图与噪声 latent 在通道维拼接后输入 UNet，用于 inpainting (mask + masked image) 和 img2img; (4) **IP-Adapter**: 通过 decoupled cross-attention 注入 CLIP 图像特征 (独立的 $K_i/V_i$ 投影)，适合风格迁移和图像参考; (5) **CFG (Classifier-Free Guidance)**: 推理时技术而非架构修改，通过放大条件/无条件预测差值来增强 prompt 遵循度。空间对齐条件 (edge/pose) 用 ControlNet/concat 而非 cross-attention，因为 attention 的全局感受野会模糊空间细节。

- [ ] 解释 ControlNet 的 zero convolution 设计哲学

> **Answer**: ControlNet 的核心设计是: 冻结预训练 UNet，克隆其 encoder 作为可训练副本，通过 1x1 zero convolution (权重和偏置初始化为 0) 连接两者。Zero conv 的设计哲学是**安全的渐进式学习**: 训练初期 zero conv 输出恒为 0，等于没有加入任何条件信号，完全保留预训练 UNet 的生成能力; 随着训练进行，zero conv 权重从 0 自动增长，条件信号逐渐注入。权重增长速率由梯度自动决定，不需要人为的 warm-up 或调度策略。这保证了训练不会在初期因随机初始化的大梯度破坏预训练权重 -- 对比: 如果用 Xavier/Kaiming 初始化，初始输出就是随机噪声，直接叠加到 UNet 会灾难性遗忘。训练成本仅约 600 GPU-hours (A100)，远低于从头训练 SD 的 150,000 GPU-hours。

- [ ] 用一句话描述 DDPM/DDIM/Score matching 在 SDE 框架下的统一关系

> **Answer**: SDE 统一视角: **DDPM 对应前向 SDE 的离散化 (加噪)，Score matching 训练网络估计 score function $\nabla_{x_t}\log p_t(x_t)$，DDIM 是反向 ODE (probability flow ODE) 的数值解 (确定性采样)**。具体来说，$\epsilon$-prediction 与 score function 仅差一个缩放系数: $\nabla_{x_t}\log p_t(x_t) = -\epsilon/\sqrt{1-\bar{\alpha}_t}$。DDPM 的随机采样对应反向 SDE (含 Langevin noise)，DDIM 的确定性采样对应反向 ODE (无 noise)。三者殊途同归: DDPM 定义过程，Score matching 提供训练目标，SDE/ODE 提供灵活的采样器选择。

- [ ] 比较 4 种位置编码方法 (Learned Absolute, Sinusoidal, Shaw Relative, RoPE) 的优劣和代表模型

> **Answer**: (1) **Learned Absolute**: 每个位置学习 $d$-维向量加到 embedding，简单有效但长度固定为 $L_{\max}$，无法泛化到训练时未见的序列长度，代表模型 GPT-2/BERT; (2) **Sinusoidal**: 用 $\sin/\cos$ 不同频率手工设计，核心性质是相对位置可表示为旋转矩阵 $\text{PE}(\text{pos}+k) = M_k \cdot \text{PE}(\text{pos})$，理论上可外推但实际效果有限，代表原始 Transformer; (3) **Shaw Relative**: 在 attention score 中直接加入可学习的相对距离向量 $a_{ij}^K$，天然支持任意长度但实现复杂，代表 Transformer-XL; (4) **RoPE**: 将旋转矩阵直接应用到 Q/K 向量 (非 embedding)，利用 $R_m^\top R_n = R_{n-m}$ 使 attention score 只依赖相对位置，支持 NTK-aware 长度外推，代表 LLaMA/Qwen。面试趋势: 当前主流 LLM 几乎全部使用 RoPE。

- [ ] 推导 KV-Cache 的显存公式，并估算 LLaMA-2 7B 在 4096 上下文时的 cache 大小

> **Answer**: KV-Cache 公式: $\text{Memory} = 2 \times n_{\text{layers}} \times d_{\text{model}} \times \text{seq\_len} \times \text{dtype\_bytes}$。因子 2 是因为需要同时缓存 K 和 V 两个矩阵。每层每个 token 缓存一个 K 向量和一个 V 向量，维度均为 $d_{\text{model}}$。LLaMA-2 7B 估算: $n_{\text{layers}}=32$, $d_{\text{model}}=4096$, float16 (2 bytes), seq_len=4096: $2 \times 32 \times 4096 \times 4096 \times 2 = 2$ GB。若 seq_len=32K 则 cache 为 16 GB，超过模型参数本身 (14GB)! KV-Cache 与 seq_len 线性增长是长上下文推理的主要瓶颈。优化方法: GQA (LLaMA-2 70B 使用，cache 缩小 $1/4$-$1/8$)、Paged Attention (vLLM，消除显存碎片)、Sliding Window (Mistral，固定上限)。

- [ ] 解释 noise ($\epsilon$) prediction vs $x_0$ prediction vs $v$-prediction 的方差差异和适用场景

> **Answer**: 三种参数化的核心差异在目标方差: $\epsilon$-prediction 的目标 $\epsilon \sim \mathcal{N}(0,\mathbf{I})$，方差恒为 1; $x_0$-prediction 的目标方差 $\frac{1-\bar{\alpha}_t}{\bar{\alpha}_t}$，在 $t \to T$ 时趋向无穷，导致大 $t$ 时梯度爆炸; $v$-prediction ($v = \sqrt{\bar{\alpha}_t}\epsilon - \sqrt{1-\bar{\alpha}_t}x_0$) 在 $t \approx 0$ 时退化为预测信号，$t \approx T$ 时退化为预测噪声，方差全程近似均匀。实际使用: DDPM 和 SD v1.x 用 $\epsilon$-prediction; SD v2 和 SDXL 部分训练用 $v$-prediction; $x_0$-prediction 较少直接使用但可通过公式互转: $\hat{x}_0 = (x_t - \sqrt{1-\bar{\alpha}_t}\hat{\epsilon})/\sqrt{\bar{\alpha}_t}$。

- [ ] 解释 VAE 重参数化技巧 (reparameterization trick) 解决了什么问题，写出公式

> **Answer**: 问题: VAE 需要从 encoder 输出的分布 $q_\phi(z|x) = \mathcal{N}(\mu, \sigma^2)$ 中采样 $z$，但「采样」操作不可微分，梯度无法通过 $z$ 反向传播到 encoder 参数 $\phi$。重参数化技巧将随机性分离到与模型参数无关的外部噪声: $z = \mu + \sigma \odot \epsilon$, $\epsilon \sim \mathcal{N}(0, \mathbf{I})$。这样 $z$ 对 $\mu$ 和 $\sigma$ 都是可微的确定性函数 (加法和乘法)，梯度可以正常回传: $\partial z/\partial \mu = 1$, $\partial z/\partial \sigma = \epsilon$。训练时每次前向传播采样不同的 $\epsilon$，等价于对 ELBO loss 做单样本 Monte Carlo 估计。这个技巧是所有 VAE 变体 (包括 SD 的潜在空间 VAE) 能端到端训练的关键。

- [ ] 描述 ControlNet 的训练流程: 冻结了什么，训练了什么，为什么训练成本远低于从头训练 SD

> **Answer**: ControlNet 训练流程: (1) **冻结**原始 SD UNet 的全部参数 (locked copy); (2) **克隆** UNet 的 encoder blocks (约 50% 参数) 作为 trainable copy; (3) 在每个连接点插入 1x1 zero conv (weight=0, bias=0); (4) 用 (image, condition, prompt) 三元组训练，loss 与标准 SD 相同的 $\epsilon$-prediction MSE。训练成本低的原因: 克隆保留了 SD 学到的图像理解能力，训练只需学习「条件信息如何对齐到已有特征」; zero conv 保证初始输出为 0 (不破坏预训练)，避免灾难性遗忘; 实际训练量约 600 GPU-hours (8xA100)，仅为从头训练 SD (约 150,000 GPU-hours) 的 0.4%。多 ControlNet 可通过加权求和组合: $\text{output} = \text{UNet}(x_t) + \sum_i w_i \cdot \text{ControlNet}_i(x_t, c_i)$。

- [ ] 对比 SD/SDXL/SD3/Midjourney/Firefly 的架构差异和各自定位

> **Answer**: **SD 1.x/2.x**: UNet + CLIP text encoder，最广泛的开源基础模型，社区生态庞大，适合研究和 fine-tune; **SDXL**: 更大的 UNet + 双 CLIP encoder (OpenCLIP ViT-G + CLIP ViT-L)，质量提升但推理更慢; **SD3**: 用 MMDiT (Multimodal Diffusion Transformer) 替代 UNet，采用 Flow Matching 训练，代表 UNet -> DiT 的架构演进; **Midjourney**: 闭源服务，美学风格最强，Discord 交互，适合创意设计但不可定制部署; **Adobe Firefly**: 闭源企业级产品，核心卖点是**版权安全** -- 仅用 Adobe Stock 授权数据训练，适合商业场景。架构演进趋势: UNet -> DiT，因为 Transformer 有更好的 scaling law、与 LLM 共享基础设施、天然支持多模态统一。

## 面试快速参考

### 完整知识链

```
1. 前向过程: x_t = sqrt(a_bar_t) * x_0 + sqrt(1-a_bar_t) * eps  (方差守恒)
2. 反向过程: UNet 预测 eps, MSE loss 训练                          (极简目标)
3. Latent Diffusion: VAE 压缩 -> latent 空间扩散 -> VAE 解码       (48x 压缩)
4. 文本控制: CLIP 编码 -> Cross-Attention 注入 UNet                 (Q=图像, K/V=文本)
5. CFG: 两次前向传播, 放大文本方向                                  (w=7.5 典型值)
6. Noise Schedule: cosine 优于 linear                              (均匀信息销毁)
7. 时间注入: sinusoidal -> MLP -> scale+shift 每个 ResBlock         (一个UNet全时间步)
8. ControlNet: zero conv 渐进引入空间控制                          (不破坏预训练)
9. DDIM: 确定性采样, 20-50步, 支持插值                             (ODE 视角)
10. SDE 框架: 统一 DDPM/DDIM/Score matching                        (eps = -score)
```

### 设计哲学总结

1. **方差守恒**: 加噪保持总能量不变，系数带根号是因为在标准差层面操作

2. **预测噪声而非原图**: epsilon-prediction 方差更小、训练更稳定，等价于 score estimation

3. **先定义行为再推参数**: cosine schedule 先设计 alpha_bar_t 形状，再反推 beta_t

4. **不破坏已有能力**: zero conv / LoRA 零初始化，渐进式引入新能力

5. **一个网络适配所有步**: 通过 sinusoidal embedding + scale/shift 让单一 UNet 处理全部时间步


---

<a id="day-2"></a>
