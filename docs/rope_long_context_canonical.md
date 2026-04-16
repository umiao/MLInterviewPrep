<!-- KG_M_02_ROPE_LONGCTX_20260416 -->

# RoPE & Long Context Extension — Canonical Deep Dive

> **正典节点** [RoPE & Long Context Extension (pillar6.transformer.long_context_rope)](/framework/201)

> 本文是 KG-M-02 迁移自 Adobe Doc 19 Day 4 的 paper 风格深推导，**与正典节点共生**。结构对应：节点给出 10-section 概览与 interview pitfalls；本文保留 Doc 19 中 RoPE / PE / 长上下文扩展 四节的完整叙述。Section 5 视频生成、误解 3/4、Q3/Q4/Q5 与视频生成直接相关的内容已剔除——它们属于未来的视频生成枢纽节点（pillar6.video_generation，暂未创建）。

---

# RoPE + 长上下文扩展 + 视频生成 — 面试复习笔记

> Adobe 面试准备 Day 4 | 中文版 | 含数学推导、直觉解释、常见误解纠正

---

## 目录

1. [位置编码：为什么重要](#1-位置编码为什么重要)
2. [RoPE：旋转位置编码](#2-rope旋转位置编码)
3. [PE 方法对比](#3-pe-方法对比)
4. [长上下文扩展方法](#4-长上下文扩展方法)
5. [视频生成](#5-视频生成)
6. [常见误解纠正](#6-常见误解纠正)
7. [自测题与参考答案](#7-自测题与参考答案)
8. [快速参考卡片](#8-快速参考卡片)

---

## 术语表

| 缩写 | 全称 | 含义 |
|------|------|------|
| RoPE | Rotary Position Embedding | 通过旋转 Q/K 向量编码位置；点积只依赖相对距离 |
| PE | Positional Encoding | 向 Transformer 注入位置信息的机制 |
| PI | Position Interpolation | 线性压缩位置到训练范围内（插值而非外推） |
| NTK | Neural Tangent Kernel (scaling) | 修改 RoPE base frequency，保护高频、拉伸低频 |
| YaRN | Yet another RoPE extensioN | 分维度混合 PI 和 NTK + attention 温度缩放 |
| DiT | Diffusion Transformer | 用纯 Transformer 替代 U-Net 做扩散去噪 |
| 3D VAE | 3D Variational Autoencoder | 在空间和时间维度同时压缩视频到潜空间 |
| KV-cache | Key-Value Cache | 缓存先前 token 的 K/V 张量，加速自回归推理 |
| ALiBi | Attention with Linear Biases | 在 attention score 上加线性距离惩罚 |
| AdaLN | Adaptive Layer Normalization | LayerNorm 参数由外部信号（时间步/文本）控制 |

---

## 1. 位置编码：为什么重要

Transformer 本身是**排列不变的（permutation-invariant）**：没有位置信息时，attention 对任何 token 顺序产生相同输出。"狗咬人"和"人咬狗"无法区分。

**位置编码**就是打破这个对称性的机制。

### 好的位置编码需要满足四个条件

1. **唯一性**：每个位置有独一无二的编码
2. **有界性**：位置再大，编码值也不会爆炸
3. **相对距离感知**：attention 应依赖 $m - n$（相对距离），而非绝对位置 $m, n$
4. **外推能力**：训练时用 4K 长度，推理时能处理 32K+

后续所有方法的优劣评判都围绕这四点展开。

---

## 2. RoPE：旋转位置编码

### 2.1 核心直觉

传统方法（Sinusoidal、Learned）是**加法**：把位置向量加到 token embedding 上。

RoPE 换了思路：**不加，而是旋转**。把 Q 和 K 向量在 2D 平面上旋转一个与位置成正比的角度。

**时钟比喻**：位置 0 的指针指向 12 点，位置 1 转一小格，位置 2 转两小格……两根指针的夹角只取决于它们隔了几格，与各自指向哪里无关。这就是"相对位置"。

### 2.2 数学公式

#### 频率设计

embedding 维度为 $d$，分成 $d/2$ 对。第 $i$ 对的旋转频率：

$$\theta_i = \frac{1}{10000^{2i/d}}, \quad i = 0, 1, \ldots, d/2 - 1$$

- **小 $i$（前面的维度）**：$\theta_i$ 大，旋转快 → 捕捉**局部/短距离**模式
- **大 $i$（后面的维度）**：$\theta_i$ 小，旋转慢 → 捕捉**长距离**模式

> 多刻度尺子类比：有的刻度精细（毫米），有的粗糙（厘米），合在一起同时量近的和远的。

> 注意：这个频率公式和原始 Transformer 的 Sinusoidal PE 完全一样。区别在于注入方式——Sinusoidal 用加法，RoPE 用旋转。

#### 旋转矩阵

位置 $m$、第 $i$ 维度对的旋转：

$$\begin{pmatrix} \tilde{x}_{2i} \\ \tilde{x}_{2i+1} \end{pmatrix} = \begin{pmatrix} \cos(m\theta_i) & -\sin(m\theta_i) \\ \sin(m\theta_i) & \cos(m\theta_i) \end{pmatrix} \begin{pmatrix} x_{2i} \\ x_{2i+1} \end{pmatrix}$$

整体是分块对角矩阵：

$$R_m = \text{diag}\left(R^{(0)}_m, R^{(1)}_m, \ldots, R^{(d/2-1)}_m\right)$$

应用到 Q 和 K：

$$\tilde{q}_m = R_m \, q_m, \quad \tilde{k}_n = R_n \, k_n$$

### 2.3 为什么点积只依赖相对距离（核心证明）

**关键性质**：旋转矩阵满足 $R_m^T R_n = R_{n-m}$

**推导**（本质是三角和差公式）：

旋转矩阵的转置等于逆旋转：$R_m^T = R_{-m}$

两个旋转的复合 = 角度相加：$R_{-m} \cdot R_n = R_{n-m}$

验证：展开矩阵乘法，每个元素用 $\cos(A - B) = \cos A \cos B + \sin A \sin B$ 合并即得。

因此 attention score：

$$\tilde{q}_m^T \tilde{k}_n = q_m^T R_m^T R_n k_n = q_m^T R_{n-m} k_n$$

**绝对位置 $m, n$ 消失，只剩相对距离 $n - m$。证毕。**

### 2.4 高效实现

不需要构造稀疏矩阵，用 element-wise 运算：

$$\text{RoPE}(x_m) = x_m \odot \cos(m\theta) + \text{rotate\_{hal}f}(x_m) \odot \sin(m\theta)$$

其中 `rotate_half`：$(x_0, x_1, x_2, x_3, \ldots) \to (-x_1, x_0, -x_3, x_2, \ldots)$

本质就是 2D 旋转的分量形式：$a\cos\theta - b\sin\theta$ 和 $a\sin\theta + b\cos\theta$。

### 2.5 RoPE 只作用在 Q 和 K 上

关键点：RoPE 的作用范围非常窄。

$$x \xrightarrow{W_Q} q \xrightarrow{\text{RoPE}} \tilde{q} \xrightarrow{\text{dot product}} \text{attention score}$$

- **Value 不旋转**：RoPE 只影响"谁关注谁"，不影响"关注到之后传什么信息"
- **RoPE 之后没有 MLP**：点积按维度对应相乘，不做 cross-dimension mixing
- **$W_Q, W_K$ 是 learned 的**：模型可以学会把需要高频位置信号的信息路由到小 $i$ 维度，把需要低频信号的路由到大 $i$ 维度。**频率分配固定，语义路由可学。**

---

## 3. PE 方法对比

| 方法 | 类型 | 相对位置？ | 外推能力 | 代表模型 |
|------|------|-----------|---------|---------|
| Sinusoidal (2017) | 加法，固定 | 弱（dot product 含交叉项） | 差 | 原始 Transformer |
| Learned Absolute | 加法，可学 | 无 | 无（固定最大长度） | BERT, GPT-2 |
| ALiBi | Attention 偏置 | 是（线性惩罚） | 好 | BLOOM, MPT |
| **RoPE** | **乘法（旋转）** | **是（数学精确）** | **中等（需扩展方法）** | **LLaMA, Mistral, Qwen, Gemma** |

### RoPE vs Sinusoidal 的本质区别

- **Sinusoidal**：$h_m = x_m + PE_m$，点积 $h_m^T h_n$ 展开含 $x_m^T PE_n + PE_m^T x_n + PE_m^T PE_n$——相对信号与内容信号混杂
- **RoPE**：旋转操作使点积干净地只包含相对距离项，无交叉项

### RoPE 为什么成为主流（四大原因）

1. 相对位置是**数学性质**，非近似
2. **零额外参数**（不像 Learned PE）
3. **KV-cache 友好**（每个 token 独立旋转，不需重算历史 token）
4. **计算高效**（element-wise cos/sin 操作）

---

## 4. 长上下文扩展方法

### 4.0 问题根源

模型训练时最长见过 $L$ 个 token，每个维度 $i$ 见过的最大旋转角度为 $L \cdot \theta_i$。推理时若位置 $m > L$，旋转角度超出训练分布（out-of-distribution），attention 崩溃。

**核心矛盾：位置变大 → 角度超出训练分布 → 模型无法处理。**

### 4.1 Position Interpolation (PI) — "压缩所有位置"

**思路**：不外推，压回训练范围内做插值。

从 4K 扩展到 32K：所有位置乘以 $4096 / 32768 = 1/8$：

$$m' = m \cdot \frac{L_{\text{train}}}{L_{\text{target}}}$$

位置 32000 → 位置 4000，回到训练范围。

**优点**：极其简单，fine-tune ~1000 步即可。

**缺点**：对**所有频率维度做均匀压缩**。高频维度原本用来区分相邻 token，压缩后相邻位置角度差缩小 → **局部分辨率下降**。

> 尺子比喻：整把尺子等比缩小 8 倍——厘米级测量没问题，毫米精度丢了。

### 4.2 NTK-aware Scaling — "只拉伸低频"

**思路**：PI 的问题在于高频被误伤。NTK 修改 base frequency，让高频基本不变、只拉伸低频：

$$\theta_i' = \frac{1}{(b \cdot \alpha)^{2i/d}}, \quad \alpha = \frac{L_{\text{target}}}{L_{\text{train}}}$$

- 小 $i$（高频）：指数 $2i/d$ 小，$\alpha$ 影响被稀释，频率几乎不变
- 大 $i$（低频）：指数大，频率显著降低，容纳更远位置

> 尺子比喻：只把厘米刻度拉宽来量更长的东西，毫米刻度保持不变。

**优点**：保留高频局部模式，甚至 zero-shot 可用。

> **命名由来**：Neural Tangent Kernel 理论揭示了网络对不同频率特征学习速度不同。作者借此视角发现应**区别对待不同频率维度**，故名"NTK-aware"。

### 4.3 YaRN — "分维度精细处理 + 调温度"

**思路**：按频率分三组，各自最优处理：

| 频率组 | 维度 | 处理方式 |
|--------|------|----------|
| 高频（局部） | 小 $i$ | 不动，保持原样 |
| 中频 | 中间 $i$ | PI 和 NTK 的混合 |
| 低频（长距离） | 大 $i$ | 完全用 PI 插值 |

**Attention 温度缩放**：上下文变长后 attention 分布变平坦（信息熵增加），用温度因子 $\sqrt{t}$ 补偿：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d} \cdot \sqrt{t}}\right)V$$

**结果**：只需 ~400 步 fine-tune，质量最好。LLaMA 3.1（128K 上下文）使用 YaRN。

> **命名由来**："Yet another RoPE extensioN"——CS 领域常见的自嘲式命名，类似 YAML（Yet Another Markup Language）。

### 对比总结

| 方法 | 一句话 | Fine-tuning | 质量 |
|------|--------|-------------|------|
| PI | 等比压缩所有位置 | ~1K 步 | 好，但丢局部细节 |
| NTK | 改 base frequency，保高频拉低频 | ~1K 步（或 zero-shot） | 更好的局部保留 |
| **YaRN** | **分维度 PI/NTK + 温度缩放** | **~400 步** | **最佳** |

---

## 6. 常见误解纠正

### 误解 1："RoPE 是绝对位置编码"

**正确理解**：RoPE 的编码机制是绝对的（每个位置 $m$ 得到确定的旋转角度），但产生的 attention pattern 是**纯相对的**（$\tilde{q}_m^T \tilde{k}_n$ 只依赖 $n-m$）。准确说法："绝对编码，相对效果。"

### 误解 2："PI 和 NTK 做的是同一件事"

**正确理解**：PI 对所有频率维度均匀压缩（伤害高频局部分辨率）；NTK 修改 base frequency，只拉伸低频、保护高频。一句话区分：**PI 压缩位置，NTK 调整频率**。

### 误解 5："RoPE 天然支持任意长度"

**正确理解**：RoPE 在训练长度内很好，超出后旋转角度 out-of-distribution，attention 崩溃。需要 PI/NTK/YaRN 扩展。准确表述："RoPE **使长上下文成为可能**"，而非"RoPE **处理长上下文**"。

---

## 7. 自测题与参考答案

### Q1：RoPE 旋转公式 + 相对位置证明

**答**：位置 $m$、第 $i$ 维度对，旋转角度 $m \cdot \theta_i$（$\theta_i = 1/10000^{2i/d}$）：

$$\begin{pmatrix} \tilde{x}_{2i} \\ \tilde{x}_{2i+1} \end{pmatrix} = \begin{pmatrix} \cos(m\theta_i) & -\sin(m\theta_i) \\ \sin(m\theta_i) & \cos(m\theta_i) \end{pmatrix} \begin{pmatrix} x_{2i} \\ x_{2i+1} \end{pmatrix}$$

证明：$\tilde{q}_m^T \tilde{k}_n = q_m^T R_m^T R_n k_n = q_m^T R_{n-m} k_n$（因为 $R_m^T R_n = R_{n-m}$，即旋转矩阵复合 = 角度相加）。绝对位置消失，只剩 $n - m$。

### Q2：PI vs NTK 频率影响

**答**：PI 对所有频率均匀压缩（尺子整体缩小，毫米精度丢失）。NTK 只拉伸低频维度、保护高频维度（只拉宽厘米刻度，毫米刻度不动）。NTK 更好地保留局部模式，因为高频维度负责区分相邻 token。

## 8. 快速参考卡片

```
RoPE:       旋转 Q/K 在 2D 子空间。θ_i = 1/10000^(2i/d)。
            q_m · k_n 只依赖 (m-n)。零额外参数。
            高效：element-wise cos/sin。KV-cache 友好。
            只作用在 Q/K 上，不作用在 V 上。

vs 其他:    Sinusoidal = 加法，弱相对。Learned = 不能外推。
            ALiBi = attention 偏置，线性惩罚。RoPE = 乘法，精确相对。

长上下文:   PI: 位置乘以 L_train/L_target。简单但损失局部细节。
            NTK: 改 base freq。保护高频（局部）维度。
            YaRN: 分维度 PI/NTK + attention 温度。最佳质量，~400 步。

视频生成:   3D VAE 压缩 T×H×W → 潜空间（256 倍压缩）。
            Temporal attention: 跨帧一致性。
            DiT (Sora): 3D spacetime patches + Transformer。按 LLM 方式缩放。
            本质是 ViT 的推广 + AdaLN 条件注入。
            五大挑战: 时间一致性、运动、内存、长视频、数据。

Adobe:      Firefly Image → 插入 temporal 层 → Firefly Video。
            强调可控性 + 商业安全（授权数据）。
```

---

## 前置知识交叉引用

- **Day 1（扩散模型）**：视频去噪网络的迭代去噪过程与图像扩散相同，区别在于增加了 temporal attention
- **Day 3（分布式训练）**：视频模型参数量大（DiT 3B+），训练依赖分布式策略

---

*最后更新：Adobe 面试准备 Day 4*


---

<a id="day-5"></a>
