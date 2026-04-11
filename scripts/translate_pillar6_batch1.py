"""Translate and expand Pillar 6 nodes 141-148 to Chinese."""
import sqlite3

DB = "data/mle_prep.db"

NODES = {}

NODES[141] = r"""# Self-Attention Mechanism

## Overview
**Self-Attention（自注意力机制）** 是 **Transformer（变换器）** 架构的核心构建模块。它允许序列中的每个 **Token（词元）** 关注所有其他词元，通过 **Query-Key（查询-键）** 相似度计算 **Value（值）** 向量的加权组合。对于任何从事 **LLM (Large Language Model，大语言模型)** 工作的 MLE 来说，深入理解自注意力是必不可少的。

## Core Concepts

### Scaled Dot-Product Attention
给定输入嵌入 $$X \in \mathbb{R}^{n \times d}$$，我们将其投影为查询、键和值：

$$
Q = XW^Q, \quad K = XW^K, \quad V = XW^V
$$

其中 $$W^Q, W^K \in \mathbb{R}^{d \times d_k}$$，$$W^V \in \mathbb{R}^{d \times d_v}$$。这里 $d$ 是模型的隐藏维度，$d_k$ 和 $d_v$ 分别是查询/键和值的投影维度。

注意力输出为：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

这个公式的直觉是：$QK^T$ 计算每对词元之间的相似度分数，**Softmax（软最大化函数）** 将分数归一化为概率分布，然后用这些概率对值向量进行加权求和。

### Why Scale by $$\sqrt{d_k}$$?
如果不进行缩放，当 $d_k$ 较大时，点积 $q \cdot k$ 的方差与 $d_k$ 成正比。这会将 softmax 推入饱和区域，导致梯度消失。除以 $$\sqrt{d_k}$$ 可以将方差保持在 $$O(1)$$。

**数学推导**：假设 $$q_i, k_i \sim \mathcal{N}(0, 1)$$ 独立同分布，则：

$$
\text{Var}(q \cdot k) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = d_k
$$

因为每个 $q_i k_i$ 的方差为 $\text{Var}(q_i)\text{Var}(k_i) = 1$，$d_k$ 个独立项求和后方差为 $d_k$。缩放后 $\text{Var}\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = 1$，softmax 的输入保持在合理范围，梯度流动更稳定。

**实际影响**：在 GPT-3 中 $d_k = 128$，不缩放时点积标准差约为 11.3，softmax 输出接近 one-hot 分布，梯度几乎为零。缩放后标准差为 1，softmax 输出更平滑，学习更高效。

### Attention as Soft Dictionary Lookup
自注意力可以被理解为一个可微分的字典查找操作：
- **Keys（键）**：定义每个位置"宣告"的内容——"我包含什么信息"
- **Queries（查询）**：定义每个位置"寻找"的内容——"我需要什么信息"
- **Values（值）**：定义要检索的具体信息——"我能提供什么"
- Softmax 权重是"软匹配"分数——不像硬字典只返回一个结果，而是返回所有值的加权组合

这个视角有助于理解 **Cross-Attention（交叉注意力）**：在 encoder-decoder 架构中，decoder 的查询在 encoder 的键值对中"查找"相关信息。

### Causal (Masked) Attention
对于 **Autoregressive（自回归）** 生成，必须屏蔽未来词元：

$$
\text{CausalAttention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + M\right)V
$$

其中 $$M_{ij} = -\infty$$ 当 $$j > i$$（上三角部分），确保词元 $i$ 只能关注位置 $$\leq i$$ 的词元。在实际实现中，$-\infty$ 通常用一个很大的负数（如 $-10^9$ 或 float('-inf')）代替。

**因果掩码的重要性**：
- 保证训练时的 **Teacher Forcing（教师强制）** 与推理时的自回归生成保持一致
- 使得整个序列可以并行计算（不像 RNN 需要逐步展开），每个位置只"看到"它前面的上下文
- 训练时一次前向传播就能计算所有位置的损失

### Complexity Analysis
- 时间复杂度：$$O(n^2 d)$$，其中 $n$ 是序列长度，$d$ 是维度
- 内存复杂度：$$O(n^2)$$，用于存储注意力矩阵
- 这个二次缩放是处理长序列的主要瓶颈

**具体数字**：对于序列长度 $n = 4096$，$d = 4096$（类似 LLaMA-7B），注意力矩阵有 $4096^2 \approx 16.7M$ 个元素。以 FP16 存储需要约 33MB。对于 $n = 128K$（Claude/GPT-4 级别），注意力矩阵需要约 32GB——这就是为什么需要 **Flash Attention（闪存注意力）** 等技术。

### Attention Patterns and Interpretability
研究发现，训练后的注意力头会形成可解释的模式：
- **位置头**：关注固定相对位置（如前一个词元）
- **语法头**：关注语法相关的词元（如动词关注其主语）
- **稀有词头**：在出现低频词时激活
- 这些发现催生了 **Mechanistic Interpretability（机制可解释性）** 领域

## Implementation

```python
import numpy as np

def self_attention(X, W_q, W_k, W_v):
    # Scaled dot-product self-attention.
    Q = X @ W_q  # (n, d_k)
    K = X @ W_k  # (n, d_k)
    V = X @ W_v  # (n, d_v)
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)  # (n, n)
    weights = np.exp(scores - scores.max(axis=-1, keepdims=True))
    weights /= weights.sum(axis=-1, keepdims=True)
    return weights @ V  # (n, d_v)

def causal_mask(n):
    # Upper-triangular mask for autoregressive attention.
    mask = np.full((n, n), -1e9)
    mask = np.triu(mask, k=1)
    return mask
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 注意力瓶颈分析 | "Transformer 为什么不能处理长序列？" | $$O(n^2)$$ 注意力矩阵；催生 Flash Attention、稀疏注意力 |
| 注意力即软检索 | "自注意力的直觉是什么？" | 键宣告、查询搜索、值传递信息 |
| 因果掩码 | "GPT 如何防止看到未来？" | softmax 之前应用上三角 $$-\infty$$ 掩码 |
| 缩放因子推导 | "为什么除以 $$\sqrt{d_k}$$？" | 防止大方差点积导致 softmax 饱和 |
| 注意力与卷积/循环对比 | "自注意力相比 RNN/CNN 的优劣？" | 全局感受野 vs 二次复杂度的权衡 |

### Common Interview Questions
- [ ] 为什么自注意力在没有位置编码时具有 **Permutation Equivariance（置换等变性）**？——因为注意力只依赖词元间的相似度，与顺序无关
- [ ] 自注意力的计算和内存复杂度是多少？——时间 $$O(n^2 d)$$，内存 $$O(n^2 + nd)$$
- [ ] 因果掩码如何实现自回归生成？——上三角 $-\infty$ 使未来位置的注意力权重为零
- [ ] 比较自注意力与卷积和循环网络在序列建模上的差异——路径长度、并行性、归纳偏置
- [ ] 为什么自注意力需要单独注入位置信息？——操作本身对输入顺序不敏感

## Comparisons

| Aspect | Self-Attention | RNN | CNN (1D) |
|--------|---------------|-----|----------|
| 序列建模 | 全局，$$O(1)$$ 路径长度 | 顺序，$$O(n)$$ 路径 | 局部，$$O(n/k)$$ 路径 |
| 并行化 | 完全并行 | 顺序执行 | 完全并行 |
| 每层复杂度 | $$O(n^2 d)$$ | $$O(n d^2)$$ | $$O(k n d^2)$$ |
| 长距离依赖 | 原生支持 | 梯度消失问题 | 需要深层堆叠 |
| 归纳偏置 | 无（完全数据驱动） | 时序性、马尔可夫性 | 局部性、平移不变性 |

## Key Takeaways

- [ ] 自注意力通过 $$QK^T$$ 相似度计算词元间的成对交互
- [ ] 除以 $$\sqrt{d_k}$$ 防止 softmax 梯度消失——方差从 $d_k$ 归一化到 $1$
- [ ] 因果掩码强制执行自回归属性（不能看到未来）
- [ ] $$O(n^2)$$ 复杂度催生高效注意力变体（Flash Attention、稀疏注意力、线性注意力）
- [ ] 注意力具有置换等变性——位置编码是不可或缺的
- [ ] 注意力头会自发形成可解释的模式——这是 **Mechanistic Interpretability（机制可解释性）** 研究的基础
"""

NODES[142] = r"""# Multi-Head Attention

## Overview
**Multi-Head Attention (MHA，多头注意力)** 并行运行多个注意力操作，每个使用不同的学习投影，使模型能够同时关注来自不同 **Representation Subspace（表示子空间）** 的信息。它是所有现代 Transformer 中的标准注意力机制。

## Core Concepts

### Multi-Head Formulation
给定 $h$ 个头，每个头 $i$ 独立计算注意力：

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)
$$

其中 $$W_i^Q, W_i^K \in \mathbb{R}^{d \times d_k}$$，$$W_i^V \in \mathbb{R}^{d \times d_v}$$，且 $$d_k = d_v = d/h$$。

所有头的输出拼接后再通过线性投影：

$$
\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O
$$

其中 $$W^O \in \mathbb{R}^{d \times d}$$。

**直觉理解**：每个头在一个低维子空间（$d/h$ 维）中计算注意力。不同的头可以学习关注不同类型的关系——有的关注局部语法，有的关注长距离语义依赖，有的关注位置信息。最后通过 $W^O$ 将所有子空间的信息融合回原始维度。

### Why Multiple Heads?
- 单个注意力头每个位置只能计算一种注意力模式
- 多个头允许同时关注不同方面：**Syntactic（句法）** 关系、**Semantic（语义）** 关系、位置关系
- 头会自然地 **Specialize（特化）**：某些关注局部、某些关注全局、某些关注特定关系
- 经验上，多个较小的头比同等总维度的一个大头表现更好

**Voita et al. (2019)** 的研究发现 Transformer 的头可以分类为：
1. **Positional heads（位置头）**：关注相邻位置
2. **Syntactic heads（句法头）**：关注语法依赖（如主谓关系）
3. **Rare token heads（稀有词元头）**：关注出现频率低的词

### Parameter Count
对于维度为 $d$、$h$ 个头的模型：
- 每个头：$$3 \times d \times (d/h)$$ 个参数用于 Q、K、V 投影
- 所有头合计：$$3d^2$$（与单个大头完全相同！）
- 输出投影：$$d^2$$
- MHA 总参数：$$4d^2$$

**具体例子**：LLaMA-7B 中 $d = 4096$，$h = 32$，每层 MHA 参数量为 $4 \times 4096^2 = 67.1M$。整个模型 32 层的 MHA 参数共约 2.15B，占总参数量的一半以上。

### Head Dimension Trade-offs
头维度 $d_k = d/h$ 的选择涉及重要权衡：
- **头数过多**（$d_k$ 过小）：每个头的表达能力有限，注意力模式过于简单
- **头数过少**（$d_k$ 过大）：无法同时捕捉多种关系模式
- 典型设置：$d_k = 64$ 或 $d_k = 128$（GPT-3 用 $d=12288$, $h=96$, $d_k=128$）
- 理论分析表明 $d_k$ 至少需要 $O(\log n)$ 才能区分序列中的不同位置

### Head Pruning and Redundancy
研究表明许多头可以被剪枝而质量下降很小。**Michel et al. (2019)** 发现在某些层中，一个头就足够了。这催生了：
- **Structured Pruning（结构化剪枝）**：移除整个注意力头
- **Multi-Query Attention (MQA，多查询注意力)**：所有头共享 K/V
- **Grouped-Query Attention (GQA，分组查询注意力)**：组内共享 K/V

## Implementation

```python
import numpy as np

class MultiHeadAttention:
    def __init__(self, d_model, n_heads):
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        # Initialize projection matrices
        self.W_q = np.random.randn(d_model, d_model) * 0.02
        self.W_k = np.random.randn(d_model, d_model) * 0.02
        self.W_v = np.random.randn(d_model, d_model) * 0.02
        self.W_o = np.random.randn(d_model, d_model) * 0.02

    def forward(self, X):
        n, d = X.shape
        Q = (X @ self.W_q).reshape(n, self.n_heads, self.d_k)
        K = (X @ self.W_k).reshape(n, self.n_heads, self.d_k)
        V = (X @ self.W_v).reshape(n, self.n_heads, self.d_k)
        # Per-head attention: (n_heads, n, n)
        scores = np.einsum('nhd,mhd->hnm', Q, K) / np.sqrt(self.d_k)
        weights = np.exp(scores - scores.max(-1, keepdims=True))
        weights /= weights.sum(-1, keepdims=True)
        # Weighted values: (n_heads, n, d_k) -> (n, d)
        out = np.einsum('hnm,mhd->nhd', weights, V)
        out = out.reshape(n, -1)  # concat heads
        return out @ self.W_o
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 头特化分析 | "为什么需要多个头？" | 不同头学习不同注意力模式（局部、全局、句法） |
| 参数等价性 | "MHA 参数比单头多吗？" | Q/K/V 同样是 $$3d^2$$；头只是分割了维度 |
| 头剪枝 | "如何加速注意力？" | 许多头是冗余的；剪枝后质量保持 |
| MHA vs MQA/GQA | "推理优化" | MQA 共享 K/V，KV 缓存减少 $$h$$ 倍 |
| 输出投影的作用 | "$$W^O$$ 为什么必要？" | 融合各头子空间信息，恢复到原始维度 |

### Common Interview Questions
- [ ] 为什么 MHA 使用 $$d_k = d/h$$ 而不是每个头用完整的 $d$？——保持总计算量不变，同时获得多样性
- [ ] MHA 的总参数量与单头注意力相比如何？——完全相同（$$4d^2$$），只是组织方式不同
- [ ] 不同的注意力头分别学习关注什么？——位置、句法、语义等不同模式
- [ ] MHA 与 **Ensemble Methods（集成方法）** 有什么关系？——类似于特征空间中的集成，但共享输入
- [ ] 解释输出投影 $$W^O$$——为什么需要它？——将各头的拼接输出映射回模型维度，实现信息融合

## Comparisons

| Aspect | Multi-Head (MHA) | Multi-Query (MQA) | Grouped-Query (GQA) |
|--------|-----------------|-------------------|---------------------|
| K/V 每头 | 独立 | 所有头共享 | 组内共享 |
| KV 缓存大小 | $$2 \times n \times h \times d_k$$ | $$2 \times n \times d_k$$ | $$2 \times n \times g \times d_k$$ |
| 质量 | 基线 | 轻微下降 | 接近 MHA 质量 |
| 推理速度 | 基线 | 最快 | 良好平衡 |
| 代表模型 | 原始 Transformer, BERT | PaLM, Falcon | LLaMA-2, Mistral |

## Key Takeaways

- [ ] MHA 将 $d$ 分成 $h$ 个头，每个头在 $d/h$ 维空间中计算注意力
- [ ] 总参数量为 $$4d^2$$（与一个大头加输出投影的开销相同）
- [ ] 各头 **Specialize（特化）** 为不同注意力模式，提升表示能力
- [ ] 许多头可以被剪枝——催生 MQA/GQA 用于高效推理
- [ ] 输出投影 $$W^O$$ 在各头之间混合信息
- [ ] 头维度 $d_k$ 的选择需要平衡表达能力和多样性
"""

NODES[143] = r"""# Position Encoding (Sinusoidal, RoPE, ALiBi)

## Overview
**Self-Attention（自注意力）** 具有 **Permutation Equivariance（置换等变性）**——它没有词元位置的内在概念。**Position Encoding（位置编码）** 注入顺序信息，使模型能够区分词元顺序。现代方法包括 **Sinusoidal（正弦余弦）** 编码（原始 Transformer）、**Learned Absolute（学习的绝对位置）** 编码、**RoPE (Rotary Position Embedding，旋转位置嵌入)**、以及 **ALiBi (Attention with Linear Biases，线性偏置注意力)**。

## Core Concepts

### Sinusoidal Position Encoding (Vaswani et al., 2017)
确定性编码，加到输入嵌入上：

$$
PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)
$$

**关键性质**：
- 每个维度有不同频率，为每个位置形成唯一的"指纹"
- 相对位置可以表示为线性变换：$$PE_{pos+k}$$ 是 $$PE_{pos}$$ 的线性函数
- 可以 **Extrapolate（外推）** 到训练时未见过的序列长度
- 低维变化频率高（捕捉局部位置），高维变化频率低（捕捉全局位置）

**频率设计的直觉**：将位置编码类比为二进制数——最低位每步翻转，次低位每两步翻转，以此类推。正弦编码用连续的三角函数实现了类似的多尺度位置表示。

### Learned Absolute Position Embeddings
查找表 $$E_{pos} \in \mathbb{R}^{L \times d}$$ 加到词元嵌入上。BERT、GPT-2 使用。
- 优点：比正弦编码更有表达力，可以学习任意位置模式
- 缺点：固定最大长度 $L$；无法外推；增加可训练参数

### Rotary Position Embeddings (RoPE)
用于 LLaMA、Mistral 以及大多数现代 LLM。通过旋转查询/键向量编码位置：

$$
f(x, m) = \begin{pmatrix} x_1 \\ x_2 \end{pmatrix} \otimes \begin{pmatrix} \cos m\theta \\ \cos m\theta \end{pmatrix} + \begin{pmatrix} -x_2 \\ x_1 \end{pmatrix} \otimes \begin{pmatrix} \sin m\theta \\ \sin m\theta \end{pmatrix}
$$

其中 $m$ 是位置，$$\theta_i = 10000^{-2i/d}$$。

**旋转矩阵推导**：对于每对维度 $(x_{2i}, x_{2i+1})$，RoPE 应用一个 2D 旋转：

$$
R_m = \begin{pmatrix} \cos m\theta_i & -\sin m\theta_i \\ \sin m\theta_i & \cos m\theta_i \end{pmatrix}
$$

完整的旋转矩阵是块对角的，每个 $2 \times 2$ 块对应一对维度。

**核心性质**：$$\langle f(q, m), f(k, n) \rangle$$ 只依赖 $q$、$k$ 和相对位置 $m - n$：

$$
\text{Re}[\langle f(q, m), f(k, n) \rangle] = g(q, k, m-n)
$$

这意味着 RoPE 自然地编码了相对位置信息，同时保持了绝对位置的感知——两全其美。

**RoPE 的优势**：
1. 相对位置信息自然嵌入点积中
2. 不增加额外参数
3. 通过 **NTK-Aware Scaling（NTK感知缩放）** 可以扩展上下文长度
4. 与 **Flash Attention（闪存注意力）** 兼容

### ALiBi (Attention with Linear Biases)
不修改嵌入，而是直接在注意力分数上添加位置依赖的偏置：

$$
\text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + m \cdot [-(i-j)]_{i,j}\right)
$$

其中 $m$ 是头特定的斜率（几何序列，如 $$2^{-8/h}, 2^{-16/h}, \ldots$$）。

**设计原理**：
- 无需额外参数或嵌入计算
- 强大的长度外推能力——无需微调即可处理更长序列
- 每个头有不同斜率：某些关注局部（大斜率，远距离惩罚大），某些关注全局（小斜率）
- 类似于给注意力分数加了一个"距离衰减"

**斜率选择**：$h$ 个头的斜率为 $$m_j = 2^{-8j/h}$$（$j = 1, \ldots, h$）。这保证了从高度局部到几乎全局的关注范围均匀覆盖。

### NTK-Aware Scaling for RoPE
为了将上下文长度扩展到训练范围之外，缩放频率基数：

$$
\theta_i' = \theta_i \cdot \alpha^{-2i/d}, \quad \alpha = \frac{L'}{L}
$$

其中 $L$ 是原始训练长度，$L'$ 是目标长度。这在保持局部位置分辨率的同时拉伸长距离容量。

**其他扩展方法**：
- **YaRN (Yet another RoPE extensioN)**：结合 NTK 缩放和温度调整
- **Position Interpolation（位置插值）**：将位置线性压缩到训练范围内
- **Dynamic NTK**：根据实际序列长度动态调整缩放因子

## Implementation

```python
import numpy as np

def sinusoidal_pe(max_len, d_model):
    # Sinusoidal position encoding.
    pe = np.zeros((max_len, d_model))
    pos = np.arange(max_len)[:, None]
    div = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(pos * div)
    pe[:, 1::2] = np.cos(pos * div)
    return pe

def apply_rope(x, pos):
    # Apply RoPE to a (seq_len, d) tensor.
    d = x.shape[-1]
    theta = 10000.0 ** (-np.arange(0, d, 2) / d)
    angles = pos[:, None] * theta  # (seq_len, d/2)
    cos_a, sin_a = np.cos(angles), np.sin(angles)
    x1, x2 = x[..., 0::2], x[..., 1::2]
    return np.stack([x1 * cos_a - x2 * sin_a,
                     x1 * sin_a + x2 * cos_a], axis=-1).reshape(x.shape)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 位置编码对比 | "RoPE vs ALiBi vs 正弦？" | 相对 vs 绝对、外推能力、参数效率 |
| RoPE 推导 | "解释旋转位置嵌入" | 2D 旋转使点积只依赖相对位置 |
| 上下文扩展 | "如何扩展 LLM 上下文长度？" | NTK 缩放、位置插值、YaRN |
| ALiBi 设计 | "ALiBi 为什么能外推？" | 线性偏置是归纳偏置，无需学习即可泛化 |

### Common Interview Questions
- [ ] 为什么 Transformer 需要位置编码？——自注意力对输入顺序不敏感
- [ ] 比较 RoPE 与正弦位置编码的优劣——RoPE 编码相对位置，正弦编码绝对位置
- [ ] RoPE 如何实现相对位置感知？——旋转使点积只依赖位置差
- [ ] 如何将 4K 上下文长度的模型扩展到 128K？——NTK 缩放/位置插值 + 持续预训练
- [ ] ALiBi 的斜率如何选择？每个头的行为有何不同？——几何序列，从局部到全局

## Comparisons

| Aspect | Sinusoidal | Learned | RoPE | ALiBi |
|--------|-----------|---------|------|-------|
| 类型 | 绝对、确定性 | 绝对、学习 | 相对、旋转 | 相对、偏置 |
| 额外参数 | 0 | $L \times d$ | 0 | 0 |
| 外推能力 | 中等 | 无 | 中等（需要缩放） | 强 |
| 主要用户 | 原始 Transformer | BERT, GPT-2 | LLaMA, Mistral | BLOOM, MPT |
| 与注意力的交互 | 加到嵌入 | 加到嵌入 | 旋转 Q/K | 偏置注意力分数 |

## Key Takeaways

- [ ] 自注意力是置换等变的——必须注入位置信息
- [ ] **RoPE（旋转位置嵌入）** 是当前主流选择：通过旋转使点积编码相对位置
- [ ] **ALiBi（线性偏置注意力）** 外推能力最强：在注意力分数上加线性距离惩罚
- [ ] 上下文长度扩展是活跃研究方向：NTK 缩放、YaRN、位置插值
- [ ] 位置编码的选择直接影响模型的 **Length Generalization（长度泛化）** 能力
"""

NODES[144] = r"""# Layer Normalization

## Overview
**Layer Normalization (LayerNorm，层归一化)** 是 Transformer 架构中的关键组件，对每个样本的特征维度进行归一化。与 **Batch Normalization (BatchNorm，批归一化)** 不同，LayerNorm 不依赖批量统计，因此在序列模型和小批量场景中更稳定。现代变体包括 **RMSNorm（均方根归一化）** 和 **Pre-LN / Post-LN** 架构选择。

## Core Concepts

### LayerNorm Formula
对于输入向量 $x \in \mathbb{R}^d$：

$$
\text{LN}(x) = \frac{x - \mu}{\sigma} \cdot \gamma + \beta
$$

其中：
- $$\mu = \frac{1}{d}\sum_{i=1}^d x_i$$（特征维度的均值）
- $$\sigma = \sqrt{\frac{1}{d}\sum_{i=1}^d (x_i - \mu)^2 + \epsilon}$$（特征维度的标准差，$\epsilon \approx 10^{-5}$ 防止除零）
- $\gamma, \beta \in \mathbb{R}^d$ 是可学习的缩放和偏移参数

**与 BatchNorm 的关键区别**：
- **BatchNorm** 在批量维度上归一化：$$\mu = \frac{1}{B}\sum_{b=1}^B x_b$$，依赖批量大小
- **LayerNorm** 在特征维度上归一化：$$\mu = \frac{1}{d}\sum_{i=1}^d x_i$$，每个样本独立
- LayerNorm 在推理时行为与训练时完全一致——不需要 **Running Statistics（运行统计量）**

### Pre-LN vs Post-LN

**Post-LN（原始 Transformer）**：
$$
x' = \text{LN}(x + \text{Sublayer}(x))
$$

**Pre-LN（GPT-2, LLaMA 等现代模型）**：
$$
x' = x + \text{Sublayer}(\text{LN}(x))
$$

**Pre-LN 的优势**（为什么现代模型几乎都用 Pre-LN）：
1. **训练稳定性**：梯度通过残差连接直接流动，不经过 LN，避免了梯度缩放问题
2. **无需 Warmup**：Post-LN 通常需要 **Learning Rate Warmup（学习率预热）** 才能稳定训练，Pre-LN 更鲁棒
3. **梯度流分析**：在 Pre-LN 中，残差路径是"高速公路"，梯度直达底层；Post-LN 中每一层的 LN 都可能改变梯度方向

**Post-LN 的优势**：
- 最终表示经过归一化，输出分布更稳定
- 某些研究（如 DeepNorm）表明 Post-LN 经过适当初始化后可以达到更好的最终性能

### RMSNorm (Root Mean Square Normalization)
**RMSNorm（均方根归一化）** 省略均值中心化，只做缩放：

$$
\text{RMSNorm}(x) = \frac{x}{\text{RMS}(x)} \cdot \gamma, \quad \text{RMS}(x) = \sqrt{\frac{1}{d}\sum_{i=1}^d x_i^2}
$$

**为什么 RMSNorm 越来越流行**（LLaMA, Mistral, Gemma 都使用）：
1. 计算效率更高——省去了均值计算和减法操作，减少约 10-15% 的归一化开销
2. 实践中效果与 LayerNorm 相当或更好
3. **理论解释**：Zhang & Sennrich (2019) 认为 LayerNorm 的成功主要来自缩放不变性，而非平移不变性（均值中心化的贡献较小）
4. 参数更少——没有偏移 $\beta$

### DeepNorm
为了在超深 Transformer（1000+ 层）中使用 Post-LN，DeepNorm 修改了残差连接：

$$
x' = \text{LN}(\alpha \cdot x + \text{Sublayer}(x))
$$

其中 $\alpha > 1$（如 $\alpha = (2N)^{1/4}$，$N$ 为层数）。这有效地放大了残差路径，防止深层网络的梯度消失。

### Normalization Placement in Practice

| 模型 | 归一化方法 | 位置 |
|------|----------|------|
| 原始 Transformer | LayerNorm | Post-LN |
| GPT-2/3 | LayerNorm | Pre-LN |
| LLaMA / LLaMA-2 | RMSNorm | Pre-LN |
| Mistral / Mixtral | RMSNorm | Pre-LN |
| PaLM | LayerNorm | Pre-LN（无偏置） |
| Gemma | RMSNorm | Pre-LN + Post-LN（双归一化） |

## Implementation

```python
import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    # Standard LayerNorm.
    mu = x.mean(axis=-1, keepdims=True)
    sigma = x.std(axis=-1, keepdims=True)
    return gamma * (x - mu) / (sigma + eps) + beta

def rms_norm(x, gamma, eps=1e-5):
    # RMSNorm -- no mean centering.
    rms = np.sqrt((x ** 2).mean(axis=-1, keepdims=True) + eps)
    return gamma * x / rms
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| LN vs BN 对比 | "为什么 Transformer 用 LayerNorm？" | LN 在特征维度归一化，不依赖批量大小 |
| Pre-LN vs Post-LN | "现代模型的归一化位置？" | Pre-LN 训练更稳定，梯度流更顺畅 |
| RMSNorm 动机 | "为什么 LLaMA 用 RMSNorm？" | 省去均值中心化，效率更高且效果相当 |
| 归一化与梯度流 | "归一化如何影响训练？" | 控制激活值范围，防止梯度爆炸/消失 |

### Common Interview Questions
- [ ] LayerNorm 和 BatchNorm 的区别是什么？——归一化维度不同（特征 vs 批量），推理行为不同
- [ ] 为什么现代 LLM 都使用 Pre-LN 而非 Post-LN？——训练稳定性更好，梯度通过残差直接流动
- [ ] RMSNorm 相比 LayerNorm 有什么优势？——计算效率更高，效果相当，省去均值中心化
- [ ] 在 Transformer 的哪些位置应用归一化？——MHA 之前/之后和 FFN 之前/之后
- [ ] 解释 DeepNorm 的原理——通过放大残差路径 ($\alpha > 1$) 实现超深网络训练

## Comparisons

| Aspect | LayerNorm | RMSNorm | BatchNorm | GroupNorm |
|--------|----------|---------|-----------|-----------|
| 归一化维度 | 特征 | 特征 | 批量 | 特征组 |
| 计算 | 均值+方差 | 仅均方根 | 均值+方差+运行统计 | 均值+方差 |
| 推理一致性 | 是 | 是 | 否（用运行统计） | 是 |
| 参数 | $\gamma, \beta$ | 仅 $\gamma$ | $\gamma, \beta$ + 运行统计 | $\gamma, \beta$ |
| 典型用途 | Transformer | 现代 LLM | CNN, MLP | CV 小批量场景 |

## Key Takeaways

- [ ] LayerNorm 在特征维度归一化：$$\text{LN}(x) = \frac{x-\mu}{\sigma}\cdot\gamma+\beta$$
- [ ] **Pre-LN** 是现代标准——训练更稳定，梯度通过残差连接直接流动
- [ ] **RMSNorm（均方根归一化）** 省去均值中心化，LLaMA/Mistral 等模型广泛采用
- [ ] 归一化位置（Pre/Post）对训练稳定性影响巨大
- [ ] DeepNorm 通过放大残差实现 Post-LN 的超深网络训练
"""

NODES[145] = r"""# Feed-Forward Networks (SwiGLU)

## Overview
Transformer 中的 **FFN (Feed-Forward Network，前馈网络)** 是每个注意力层之后的逐位置全连接网络。它负责大部分的"计算"和"记忆存储"，参数量通常占模型总量的 2/3。现代 LLM 普遍使用 **SwiGLU（Swish 门控线性单元）** 替代原始的 ReLU FFN。

## Core Concepts

### Original Transformer FFN
原始 Transformer 使用两层全连接网络和 **ReLU (Rectified Linear Unit，修正线性单元)** 激活：

$$
\text{FFN}(x) = \text{ReLU}(xW_1 + b_1)W_2 + b_2
$$

其中 $$W_1 \in \mathbb{R}^{d \times d_{ff}}$$，$$W_2 \in \mathbb{R}^{d_{ff} \times d}$$，$d_{ff}$ 通常为 $4d$。

**参数量**：$$2 \times d \times d_{ff} = 8d^2$$（使用 $d_{ff} = 4d$）。这比 MHA 的 $4d^2$ 多一倍！

### GLU (Gated Linear Unit) Family
**GLU（门控线性单元）** 引入了门控机制：

$$
\text{GLU}(x) = (xW_1) \odot \sigma(xV)
$$

其中 $\odot$ 是逐元素乘法，$\sigma$ 是 **Sigmoid（S形函数）** 激活。$xW_1$ 提供内容，$\sigma(xV)$ 提供门控信号。

**变体**：
- **GEGLU**: $$\text{GEGLU}(x) = \text{GELU}(xW_1) \odot (xV)$$
- **SwiGLU**: $$\text{SwiGLU}(x) = \text{Swish}_\beta(xW_1) \odot (xV)$$
- **ReGLU**: $$\text{ReGLU}(x) = \text{ReLU}(xW_1) \odot (xV)$$

### SwiGLU Deep Dive
**SwiGLU（Swish 门控线性单元）** 是 LLaMA、PaLM、Mistral 等模型的标准选择：

$$
\text{SwiGLU}(x) = \text{Swish}(xW_1) \odot (xV)
$$

其中 **Swish** 激活函数为：

$$
\text{Swish}_\beta(x) = x \cdot \sigma(\beta x)
$$

通常 $\beta = 1$，即 $\text{Swish}(x) = x \cdot \sigma(x) = \frac{x}{1 + e^{-x}}$。

完整的 SwiGLU FFN 为：

$$
\text{FFN}_{SwiGLU}(x) = (\text{Swish}(xW_1) \odot (xV)) W_2
$$

**为什么 SwiGLU 优于 ReLU**：
1. **门控机制**：$xV$ 作为门控信号，模型可以学习选择性地激活或抑制特征
2. **平滑激活**：Swish 处处可微，不像 ReLU 在零点有不连续梯度
3. **信息流**：门控允许梯度通过两条路径流动（内容路径和门控路径）
4. **实验证据**：Shazeer (2020) 在多个基准上验证 GLU 变体全面优于 ReLU

### Parameter Expansion Ratio
SwiGLU 引入第三个权重矩阵 $V$，参数量增加：
- **ReLU FFN**: $$2 \times d \times d_{ff}$$
- **SwiGLU FFN**: $$3 \times d \times d_{ff}'$$

为了保持总参数量不变，$d_{ff}'$ 通常设为 $$\frac{2}{3} \times 4d = \frac{8d}{3}$$。

**实际设置**（考虑硬件对齐）：
| 模型 | $d$ | $d_{ff}$ | 比率 | 对齐 |
|------|-----|---------|------|------|
| LLaMA-7B | 4096 | 11008 | 2.69 | 128 的倍数 |
| LLaMA-13B | 5120 | 13824 | 2.70 | 128 的倍数 |
| LLaMA-70B | 8192 | 28672 | 3.50 | 256 的倍数 |
| Mistral-7B | 4096 | 14336 | 3.50 | 256 的倍数 |

硬件对齐（$d_{ff}$ 为 64/128/256 的倍数）对 GPU **Tensor Core（张量核心）** 效率至关重要。

### FFN as Key-Value Memory
**Geva et al. (2021)** 提出了一个重要观点：FFN 可以被理解为一个巨大的键值记忆：
- $W_1$ 的每一行是一个"键"（模式检测器）
- $W_2$ 的对应列是"值"（输出信息）
- 激活函数决定哪些键值对被激活

这解释了为什么更大的 FFN（更多参数）能存储更多知识。

### Sparse FFN and Mixture of Experts
**MoE (Mixture of Experts，混合专家)** 将 FFN 稀疏化：
- 保留多个并行的 FFN（"专家"），但每个词元只激活 Top-K 个
- **Mixtral 8x7B** 有 8 个专家，每次激活 2 个——总参数 47B 但活跃参数只有 13B
- 路由器 $$g(x) = \text{TopK}(\text{softmax}(xW_g), k)$$ 决定激活哪些专家

## Implementation

```python
import numpy as np

def swish(x):
    # Swish activation: x * sigmoid(x).
    return x * (1 / (1 + np.exp(-x)))

def swiglu_ffn(x, W1, V, W2):
    # SwiGLU FFN: Swish(xW1) * (xV) @ W2.
    return (swish(x @ W1) * (x @ V)) @ W2

def relu_ffn(x, W1, W2, b1, b2):
    # Original Transformer FFN with ReLU.
    return np.maximum(0, x @ W1 + b1) @ W2 + b2
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SwiGLU vs ReLU | "现代 LLM 用什么激活？" | SwiGLU 的门控机制和平滑梯度优于 ReLU |
| 参数量计算 | "FFN 参数占比多少？" | FFN 占模型参数的 2/3（8d^2 vs MHA 的 4d^2） |
| 扩展比调整 | "SwiGLU 的 d_ff 怎么设？" | $$\frac{8d}{3}$$ 保持参数量不变，再对齐到硬件友好值 |
| FFN 作为记忆 | "知识存储在哪？" | FFN 的 W1 行是键，W2 列是值——键值记忆 |
| MoE 稀疏化 | "如何在不增加计算的情况下增加参数？" | 多个专家 FFN + Top-K 路由 |

### Common Interview Questions
- [ ] SwiGLU 的公式是什么？它比 ReLU FFN 好在哪里？——门控机制、平滑梯度、两条梯度路径
- [ ] Transformer FFN 的参数量是多少？与注意力层相比呢？——FFN 为 $8d^2$（或 SwiGLU 的 $3d \cdot d_{ff}'$），MHA 为 $4d^2$
- [ ] 为什么 SwiGLU 的 $d_{ff}$ 要调整为 $\frac{8d}{3}$？——保持与标准 FFN 相同的参数量
- [ ] 解释 FFN 作为键值记忆的视角——W1 行=模式检测器（键），W2 列=输出信息（值）
- [ ] MoE 如何工作？有什么优势？——多个专家 + 路由器，扩大模型容量但保持计算量

## Comparisons

| Aspect | ReLU FFN | GELU FFN | SwiGLU FFN |
|--------|---------|---------|------------|
| 公式 | $$\text{ReLU}(xW_1)W_2$$ | $$\text{GELU}(xW_1)W_2$$ | $$\text{Swish}(xW_1) \odot (xV) W_2$$ |
| 参数 | $2d \cdot d_{ff}$ | $2d \cdot d_{ff}$ | $3d \cdot d_{ff}'$ |
| 门控 | 无 | 无 | 有（$xV$ 路径） |
| 平滑性 | 零点不可微 | 处处可微 | 处处可微 |
| 典型用户 | 原始 Transformer | BERT, GPT-2 | LLaMA, PaLM, Mistral |

## Key Takeaways

- [ ] **SwiGLU（Swish 门控线性单元）** 是现代 LLM 的标准 FFN：$$\text{SwiGLU}(x) = \text{Swish}(xW_1) \odot (xV)$$
- [ ] FFN 占 Transformer 参数量的 2/3——它是模型的主要"知识存储"
- [ ] SwiGLU 的 $d_{ff}$ 调整为 $$\frac{8d}{3}$$ 以保持参数量不变
- [ ] FFN 可以理解为键值记忆：$W_1$ 行是模式检测器，$W_2$ 列是存储的知识
- [ ] **MoE (Mixture of Experts，混合专家)** 通过稀疏化 FFN 在不增加计算的情况下扩大模型容量
"""

NODES[146] = r"""# Attention Variants (MQA, GQA, Flash Attention)

## Overview
标准 **MHA (Multi-Head Attention，多头注意力)** 的 $$O(n^2)$$ 复杂度和高内存占用是推理和训练的主要瓶颈。本节深入探讨三大优化方向：**MQA (Multi-Query Attention，多查询注意力)** 和 **GQA (Grouped-Query Attention，分组查询注意力)** 减少 KV 缓存，**Flash Attention（闪存注意力）** 优化 IO 复杂度。

## Core Concepts

### Multi-Query Attention (MQA)
**MQA（多查询注意力）**（Shazeer, 2019）所有头共享同一组 K 和 V，只有 Q 是每头独立的：

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW^K, VW^V)
$$

**KV 缓存节省**：
- MHA：$$2 \times h \times d_k \times n$$
- MQA：$$2 \times d_k \times n$$
- 节省比率：$$h\times$$（如 32 头模型节省 32 倍）

**代价**：质量可能轻微下降，因为所有头被迫使用相同的键值表示。PaLM 和 Falcon 采用此方案。

### Grouped-Query Attention (GQA)
**GQA（分组查询注意力）**（Ainslie et al., 2023）是 MHA 和 MQA 的折中——将 $h$ 个查询头分成 $g$ 组，每组共享一套 K/V：

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_{g(i)}^K, VW_{g(i)}^V)
$$

其中 $g(i) = \lfloor i \cdot g / h \rfloor$ 是头 $i$ 所属的组。

**典型设置**：
| 模型 | 查询头 $h$ | KV 组 $g$ | KV 缓存比率 |
|------|-----------|----------|------------|
| LLaMA-2-70B | 64 | 8 | 1/8 |
| Mistral-7B | 32 | 8 | 1/4 |
| Gemma-7B | 16 | 1 (=MQA) | 1/16 |

GQA 的质量非常接近 MHA，同时大幅减少 KV 缓存——这是目前最受欢迎的选择。

### Flash Attention: The IO Complexity Revolution
**Flash Attention（闪存注意力）**（Dao et al., 2022）不改变注意力的数学公式，而是优化其 **IO Complexity（IO 复杂度）**——减少 GPU **HBM (High Bandwidth Memory，高带宽内存)** 与 **SRAM（静态随机存取存储器）** 之间的数据传输。

**GPU 内存层次**：
- **SRAM**（片上）：~20MB，带宽 ~19TB/s
- **HBM**（显存）：~40-80GB，带宽 ~2TB/s
- 比率：SRAM 快约 10 倍，但容量小 1000 倍以上

**标准注意力的 IO 问题**：
1. 计算 $S = QK^T$——需要将 $$n \times n$$ 矩阵写入 HBM
2. 计算 $P = \text{softmax}(S)$——从 HBM 读取 S，写回 P
3. 计算 $O = PV$——从 HBM 读取 P 和 V

总 HBM 访问：$$O(n^2)$$。对于长序列，这些 IO 操作（而非计算）成为瓶颈。

**Flash Attention 的 Tiling（分块）策略**：
1. 将 Q、K、V 分成小块（适合 SRAM 的大小）
2. 在 SRAM 中计算局部注意力
3. 使用 **Online Softmax（在线 Softmax）** 算法增量更新统计量（最大值和指数和），无需完整的 $n \times n$ 矩阵
4. 最终结果直接写回 HBM

**Online Softmax 的关键**：
$$
m_{new} = \max(m_{old}, m_{block}), \quad l_{new} = l_{old} \cdot e^{m_{old} - m_{new}} + l_{block} \cdot e^{m_{block} - m_{new}}
$$

其中 $m$ 是运行最大值，$l$ 是指数和。这允许逐块处理而不需要先计算全局最大值。

**IO 复杂度对比**：
- 标准注意力：$$O(n^2 d + n^2)$$ HBM 访问
- Flash Attention：$$O(n^2 d^2 / M)$$ HBM 访问（$M$ 是 SRAM 大小）

当 $M \gg d$ 时（通常成立），Flash Attention 的 IO 显著减少。

### Flash Attention 2 & 3
**Flash Attention 2** 的改进：
- 更好的并行化：在序列长度维度上分配工作
- 减少非矩阵乘法操作（占 GPU 时间大但 FLOPS 低的操作）
- 达到理论 FLOPS 的 50-73%（vs Flash Attention 1 的 25-40%）

**Flash Attention 3**（Hopper GPU）：
- 利用 H100 的异步执行和 FP8 **Tensor Core（张量核心）**
- 支持 **Pipelining（流水线）**：GEMM 和 softmax 重叠执行

### Memory Comparison

假设 batch=1, seq_len=4096, d=4096, h=32, d_k=128, FP16：

| 方案 | KV 缓存大小 | 注意力矩阵 | 总额外内存 |
|------|-----------|-----------|-----------|
| MHA | 32MB | 32MB | 64MB |
| MQA | 1MB | 32MB | 33MB |
| GQA (g=8) | 4MB | 32MB | 36MB |
| MHA + Flash Attention | 32MB | ~0 (SRAM) | 32MB |
| GQA + Flash Attention | 4MB | ~0 (SRAM) | 4MB |

## Implementation

```python
import numpy as np

def grouped_query_attention(Q, K, V, n_heads, n_kv_groups):
    # Grouped-Query Attention (GQA).
    n, d = Q.shape
    d_k = d // n_heads
    heads_per_group = n_heads // n_kv_groups
    Q = Q.reshape(n, n_heads, d_k)
    K = K.reshape(n, n_kv_groups, d_k)
    V = V.reshape(n, n_kv_groups, d_k)
    # Repeat K/V for each head in the group
    K = np.repeat(K, heads_per_group, axis=1)
    V = np.repeat(V, heads_per_group, axis=1)
    scores = np.einsum('nhd,mhd->hnm', Q, K) / np.sqrt(d_k)
    weights = np.exp(scores - scores.max(-1, keepdims=True))
    weights /= weights.sum(-1, keepdims=True)
    out = np.einsum('hnm,mhd->nhd', weights, V)
    return out.reshape(n, -1)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| KV 缓存分析 | "LLM 推理的内存瓶颈？" | KV 缓存随序列长度线性增长，MQA/GQA 减少 $h/g$ 倍 |
| Flash Attention 原理 | "如何加速注意力计算？" | 分块+在线 Softmax 减少 HBM IO |
| GQA 设计选择 | "MHA/MQA/GQA 如何选？" | GQA 是质量与效率的最佳平衡 |
| 内存层次分析 | "GPU 计算的瓶颈在哪？" | SRAM vs HBM 带宽差 10 倍——IO 是真正瓶颈 |

### Common Interview Questions
- [ ] MQA、GQA、MHA 的区别是什么？——K/V 共享粒度不同
- [ ] Flash Attention 为什么能加速？它改变了计算量吗？——不改变 FLOPS，减少 HBM IO
- [ ] 解释 Online Softmax——增量维护最大值和指数和
- [ ] GQA 中如何选择组数 $g$？——通常 $g = h/4$ 到 $h/8$
- [ ] Flash Attention 的分块大小如何选择？——取决于 SRAM 大小，确保 Q/K/V 块能放入

## Comparisons

| Aspect | MHA | MQA | GQA | Flash Attention |
|--------|-----|-----|-----|----------------|
| 优化目标 | 基线 | KV 缓存 | KV 缓存 | IO 复杂度 |
| FLOPS 变化 | 基线 | 减少 | 减少 | 不变 |
| 内存变化 | 基线 | KV 减 $h\times$ | KV 减 $h/g\times$ | 注意力矩阵 $\to$ O(1) |
| 质量影响 | 基线 | 轻微下降 | 接近基线 | 无（精确等价） |
| 可组合 | - | 与 Flash 组合 | 与 Flash 组合 | 与 GQA/MQA 组合 |

## Key Takeaways

- [ ] **GQA（分组查询注意力）** 是当前最佳实践——KV 缓存减少 $h/g$ 倍，质量接近 MHA
- [ ] **Flash Attention（闪存注意力）** 不改变计算量，通过分块和在线 Softmax 减少 IO
- [ ] GPU 内存层次（SRAM vs HBM）是理解 Flash Attention 的关键
- [ ] GQA + Flash Attention 的组合是现代 LLM 的标准配置
- [ ] Online Softmax 是 Flash Attention 的核心算法——增量维护统计量
"""

NODES[147] = r"""# Architecture Variants (Encoder/Decoder)

## Overview
Transformer 有三大架构变体：**Encoder-Only（仅编码器）**、**Decoder-Only（仅解码器）** 和 **Encoder-Decoder（编码器-解码器）**。理解它们的设计哲学、适用场景和训练目标，对于选择模型架构和理解 LLM 演进至关重要。

## Core Concepts

### Encoder-Only Architecture
**典型代表**：BERT, RoBERTa, ALBERT, DeBERTa

**结构特点**：
- 双向注意力——每个词元可以关注序列中所有其他词元
- 无因果掩码
- 输出是每个词元的上下文表示

**训练目标**：
- **MLM (Masked Language Modeling，掩码语言模型)**：随机遮盖部分词元，预测被遮盖的词
- **NSP (Next Sentence Prediction，下一句预测)** 或 **SOP (Sentence Order Prediction，句子顺序预测)**

**适用场景**：理解任务——分类、**NER (Named Entity Recognition，命名实体识别)**、相似度计算、信息检索

**数学表示**：
$$
H = \text{Encoder}(X) = \text{TransformerBlock}^L(X + PE)
$$

每个位置的输出 $H_i$ 编码了整个序列的上下文信息。

### Decoder-Only Architecture
**典型代表**：GPT 系列、LLaMA、Mistral、Claude

**结构特点**：
- **Causal (Masked) Attention（因果注意力）**——每个词元只能关注之前的词元
- 自回归生成：逐词元预测下一个词

**训练目标**：
$$
\mathcal{L} = -\sum_{t=1}^{T} \log P(x_t | x_{<t})
$$

**适用场景**：生成任务——文本生成、代码生成、对话、推理

**为什么 Decoder-Only 成为主流**：
1. **统一框架**：任何 NLP 任务都可以转化为文本生成
2. **涌现能力**：规模化后出现 **In-Context Learning (ICL，上下文学习)**、**Chain-of-Thought (CoT，思维链)** 等能力
3. **训练效率**：每个位置都产生预测，100% 的词元参与损失计算（BERT 的 MLM 只有约 15%）
4. **简单性**：单一架构和目标函数，扩展路径清晰

### Encoder-Decoder Architecture
**典型代表**：T5, BART, mBART, Flan-T5

**结构特点**：
- 编码器处理输入（双向注意力）
- 解码器生成输出（因果注意力 + **Cross-Attention（交叉注意力）**）
- 交叉注意力连接编码器和解码器

**交叉注意力公式**：
$$
\text{CrossAttention}(Q_{dec}, K_{enc}, V_{enc}) = \text{softmax}\left(\frac{Q_{dec}K_{enc}^T}{\sqrt{d_k}}\right)V_{enc}
$$

解码器的查询在编码器的键值对中"查找"相关信息。

**训练目标**：
- **Span Corruption（片段损坏）**（T5）：随机遮盖连续片段，解码器生成被遮盖内容
- **Denoising（去噪）**（BART）：多种噪声（掩码、删除、打乱），解码器重建原文

**适用场景**：序列到序列任务——翻译、摘要、问答

### Architecture Comparison Deep Dive

**注意力模式对比**：
- Encoder-Only：完全双向，$$n \times n$$ 全注意力矩阵
- Decoder-Only：下三角矩阵（因果掩码）
- Encoder-Decoder：编码器全注意力 + 解码器因果注意力 + 交叉注意力

**计算效率对比**：
假设输入长度 $n$，输出长度 $m$：
- Encoder-Only：$$O(n^2)$$——无法生成
- Decoder-Only：$$O((n+m)^2)$$——输入和输出共享上下文窗口
- Encoder-Decoder：$$O(n^2 + m^2 + nm)$$——当 $m \ll n$ 时更高效

### Prefix LM: A Hybrid Approach
**Prefix LM（前缀语言模型）** 是 Decoder-Only 和 Encoder-Decoder 的折中：
- 输入前缀使用双向注意力（像编码器）
- 生成部分使用因果注意力（像解码器）
- 代表：U-PaLM、PaLM-2 的某些变体

**注意力掩码**：
$$
M_{ij} = \begin{cases} 0 & \text{if } j \leq \text{prefix\_len or } j \leq i \\ -\infty & \text{otherwise} \end{cases}
$$

## Implementation

```python
import numpy as np

def encoder_block(x, W_qkv, W_o, W1, W2, gamma1, beta1, gamma2, beta2):
    # Simplified encoder block: bidirectional attention + FFN.
    d = x.shape[-1]
    Q, K, V = x @ W_qkv[:, :d], x @ W_qkv[:, d:2*d], x @ W_qkv[:, 2*d:]
    scores = Q @ K.T / np.sqrt(d)
    attn = np.exp(scores - scores.max(-1, keepdims=True))
    attn /= attn.sum(-1, keepdims=True)
    x = x + (attn @ V) @ W_o  # residual
    x = layer_norm(x, gamma1, beta1)
    x = x + np.maximum(0, x @ W1) @ W2  # FFN + residual
    return layer_norm(x, gamma2, beta2)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 架构选择 | "什么任务用什么架构？" | 理解用 encoder-only，生成用 decoder-only，seq2seq 用 encoder-decoder |
| Decoder-Only 主导 | "为什么 GPT 架构胜出？" | 统一框架 + 训练效率 + 规模化涌现 |
| 交叉注意力 | "编码器和解码器如何交互？" | 解码器的 Q 查询编码器的 K/V |
| Prefix LM | "有折中方案吗？" | 输入双向 + 生成因果 |

### Common Interview Questions
- [ ] 比较三种架构的适用场景——理解 vs 生成 vs 序列到序列
- [ ] 为什么 Decoder-Only 成为 LLM 的主流选择？——统一性、效率、涌现能力
- [ ] Encoder-Decoder 中的交叉注意力如何工作？——解码器 Q 在编码器 K/V 中检索
- [ ] BERT 为什么不能直接用于文本生成？——双向注意力没有因果约束
- [ ] T5 的 Span Corruption 训练目标是什么？——遮盖连续片段，解码器重建

## Comparisons

| Aspect | Encoder-Only | Decoder-Only | Encoder-Decoder |
|--------|-------------|--------------|-----------------|
| 注意力 | 双向 | 因果（下三角） | 双向 + 因果 + 交叉 |
| 训练效率 | ~15%词元参与损失 | 100%词元 | 取决于任务 |
| 代表模型 | BERT, RoBERTa | GPT, LLaMA | T5, BART |
| 主要任务 | 分类、NER、检索 | 生成、对话、推理 | 翻译、摘要 |
| 规模化趋势 | 停滞 | 主流方向 | 仍有应用 |
| 上下文利用 | 全上下文 | 仅左上下文 | 输入全+输出左 |

## Key Takeaways

- [ ] **Decoder-Only（仅解码器）** 已成为 LLM 的主流架构——统一框架 + 规模化涌现
- [ ] **Encoder-Only（仅编码器）** 仍是理解任务（分类、检索、NER）的最佳选择
- [ ] **Encoder-Decoder（编码器-解码器）** 在序列到序列任务（翻译、摘要）中仍有优势
- [ ] 交叉注意力是 encoder-decoder 的核心：解码器查询在编码器表示中检索信息
- [ ] 训练效率是 Decoder-Only 胜出的重要因素：100% 词元参与损失 vs BERT 的 15%
- [ ] **Prefix LM（前缀语言模型）** 是两种架构的折中方案
"""

NODES[148] = r"""# BERT Family

## Overview
**BERT (Bidirectional Encoder Representations from Transformers，双向编码器表示)** 是 **Encoder-Only（仅编码器）** 架构的奠基性模型。通过 **MLM (Masked Language Modeling，掩码语言模型)** 和 **NSP (Next Sentence Prediction，下一句预测)** 预训练目标，BERT 学习了深度双向语言表示，革命性地改变了 NLP 的 **Fine-Tuning（微调）** 范式。

## Core Concepts

### Masked Language Modeling (MLM)
随机遮盖输入中 15% 的词元，预测被遮盖的词：

$$
\mathcal{L}_{MLM} = -\mathbb{E}\left[\sum_{i \in \mathcal{M}} \log P(x_i | x_{\backslash \mathcal{M}})\right]
$$

其中 $\mathcal{M}$ 是被遮盖位置的集合，$x_{\backslash \mathcal{M}}$ 是未被遮盖的词元。

**遮盖策略**（15% 的被选词元中）：
- 80% 替换为 `[MASK]` 标记
- 10% 替换为随机词元
- 10% 保持不变

**为什么不全部用 [MASK]**？这种混合策略解决了 **Train-Test Mismatch（训练-测试不匹配）** 问题——微调时输入中没有 `[MASK]`，如果模型只学会了处理 `[MASK]` 的位置，泛化能力会受限。

### Next Sentence Prediction (NSP)
给定两个句子 A 和 B，预测 B 是否是 A 的下一句：

$$
P(\text{IsNext} | [\text{CLS}], A, [\text{SEP}], B) = \sigma(W \cdot h_{[\text{CLS}]})
$$

**NSP 的争议**：
- RoBERTa (2019) 发现去掉 NSP 性能更好
- ALBERT 用 **SOP (Sentence Order Prediction，句子顺序预测)** 替代——预测两句是否交换了顺序
- 原因：NSP 太简单，模型主要通过主题匹配就能区分，学不到真正的语篇关系

### [CLS] Token Pooling
BERT 在序列开头添加特殊标记 `[CLS]`：
- 经过所有层的双向注意力后，`[CLS]` 的输出 $h_{[\text{CLS}]}$ 编码了整个序列的语义
- 用于分类任务的 **Sentence Representation（句子表示）**
- 替代方案：平均池化（所有词元的均值）或 [SEP] 表示

**为什么 [CLS] 能代表整句**：
通过 MLM 训练，`[CLS]` 需要关注所有位置才能预测遮盖词，因此自然地聚合了全局信息。

### Fine-Tuning Patterns
BERT 的微调范式为 NLP 建立了标准流程：

1. **Sequence Classification（序列分类）**：$h_{[\text{CLS}]} \to \text{Linear} \to \text{softmax}$
   - 情感分析、文本分类、自然语言推理

2. **Token Classification（词元分类）**：每个 $h_i \to \text{Linear} \to \text{softmax}$
   - **NER（命名实体识别）**、词性标注

3. **Question Answering（问答）**：预测答案在上下文中的起止位置
   - $P_{start}(i) = \text{softmax}(W_s \cdot h_i)$
   - $P_{end}(i) = \text{softmax}(W_e \cdot h_i)$

4. **Sentence Pair（句子对任务）**：$[\text{CLS}] + A + [\text{SEP}] + B \to h_{[\text{CLS}]}$
   - 语义相似度、自然语言推理、释义判断

### BERT Variants

| 模型 | 关键改进 | 参数量 |
|------|---------|--------|
| BERT-base | 原始，12 层 | 110M |
| BERT-large | 24 层 | 340M |
| RoBERTa | 去掉 NSP，更多数据，动态遮盖 | 355M |
| ALBERT | 参数共享 + 因式分解嵌入 | 12M-235M |
| DeBERTa | 解耦注意力（内容+位置分开计算） | 100M-1.5B |
| DistilBERT | 知识蒸馏压缩 | 66M |
| ELECTRA | 替换词元检测（非 MLM） | 14M-335M |

### ELECTRA: An Alternative Pre-training Approach
**ELECTRA（高效学习编码器）** 使用 **Replaced Token Detection（替换词元检测）** 代替 MLM：
- 生成器（小 MLM 模型）填充被遮盖位置
- 判别器（主模型）判断每个词元是原始的还是被替换的
- 所有词元都参与训练（不只是 15%），训练效率更高

$$
\mathcal{L}_{RTD} = -\sum_{t=1}^T \left[y_t \log D(x_t) + (1-y_t)\log(1-D(x_t))\right]
$$

### Modern Relevance of BERT
尽管 LLM 时代 decoder-only 模型占主导，BERT 家族仍然非常重要：
- **信息检索**：bi-encoder 架构（如 ColBERT、BGE）
- **嵌入模型**：句子嵌入用于 RAG
- **低延迟场景**：encoder 并行处理，推理比自回归模型快
- **资源受限**：小模型（110M）可以在 CPU 上运行

## Implementation

```python
import numpy as np

class BERTForClassification:
    def __init__(self, bert_dim, n_classes):
        self.classifier = np.random.randn(bert_dim, n_classes) * 0.02

    def forward(self, hidden_states):
        # Use [CLS] token output for classification.
        cls_output = hidden_states[0]  # first token
        logits = cls_output @ self.classifier
        return logits

def mlm_loss(logits, targets, mask_positions):
    # Compute MLM loss only at masked positions.
    masked_logits = logits[mask_positions]
    masked_targets = targets[mask_positions]
    # Softmax + cross-entropy
    probs = np.exp(masked_logits - masked_logits.max(-1, keepdims=True))
    probs /= probs.sum(-1, keepdims=True)
    loss = -np.log(probs[np.arange(len(masked_targets)), masked_targets])
    return loss.mean()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| MLM 设计动机 | "BERT 如何实现双向？" | 遮盖机制允许利用左右两侧上下文 |
| [CLS] 池化 | "如何获取句子表示？" | [CLS] 通过双向注意力聚合全局信息 |
| BERT vs GPT | "两种范式的区别？" | 双向理解 vs 单向生成；encoder vs decoder |
| 微调模式 | "BERT 如何适配下游任务？" | 加分类头 + 全参数微调 |
| NSP 争议 | "NSP 有用吗？" | RoBERTa 证明 NSP 无益，SOP 更好 |

### Common Interview Questions
- [ ] MLM 的遮盖比例为什么是 15%？80/10/10 策略的原因？——平衡上下文信息量和训练信号
- [ ] RoBERTa 相比 BERT 有哪些改进？——去掉 NSP、动态遮盖、更多数据、更长训练
- [ ] BERT 在现代 NLP 中还有什么用途？——嵌入模型、检索、低延迟分类
- [ ] 解释 DeBERTa 的解耦注意力——内容和位置分开计算注意力，更灵活
- [ ] ELECTRA 为什么比 BERT 训练效率高？——100% 词元参与训练 vs 15%

## Comparisons

| Aspect | BERT | RoBERTa | DeBERTa | ELECTRA |
|--------|------|---------|---------|---------|
| 预训练目标 | MLM + NSP | 仅 MLM | MLM | 替换词元检测 |
| 遮盖策略 | 静态 | 动态 | 动态 | N/A（判别式） |
| 位置编码 | 学习绝对 | 学习绝对 | 解耦（内容+位置） | 学习绝对 |
| 训练效率 | 基线 | 更多数据 | 基线 | 更高（100%词元） |
| GLUE 表现 | 基线 | 优于 BERT | 最佳 | 优于 BERT |

## Key Takeaways

- [ ] **MLM（掩码语言模型）** 通过遮盖+预测实现双向预训练，80/10/10 策略减轻训练-测试不匹配
- [ ] **[CLS] Pooling（池化）** 提供序列级表示——微调时加分类头即可适配各种任务
- [ ] **NSP（下一句预测）** 被证明无益——RoBERTa 去掉后性能更好
- [ ] BERT 家族在嵌入、检索、低延迟分类场景中仍然不可替代
- [ ] **ELECTRA** 的判别式预训练比 MLM 更高效——100% 词元参与训练
- [ ] **DeBERTa** 的解耦注意力是 encoder-only 架构的最新最强改进
"""

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    for nid, content in NODES.items():
        cur.execute("UPDATE framework_nodes SET description = ? WHERE id = ?", (content.strip(), nid))
        print(f"Updated node {nid}, length: {len(content.strip())}")
    conn.commit()
    conn.close()
    print("Batch 1 (141-148) complete.")

if __name__ == "__main__":
    main()
