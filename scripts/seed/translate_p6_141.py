# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Translate and expand node 141 Self-Attention."""
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB = "data/mle_prep.db"

CONTENT = r"""# Self-Attention Mechanism

## Overview
**Self-Attention（自注意力机制）** 是 **Transformer（变换器）** 架构的核心构建模块。它允许序列中的每个 **Token（词元）** 关注所有其他词元，通过 **Query-Key（查询-键）** 相似度计算 **Value（值）** 向量的加权组合。对于任何从事 **LLM (Large Language Model，大语言模型)** 工作的 MLE 来说，深入理解自注意力是必不可少的。自注意力机制的出现彻底改变了 **NLP (Natural Language Processing，自然语言处理)** 领域，取代了此前占主导地位的 **RNN (Recurrent Neural Network，循环神经网络)** 和 **LSTM (Long Short-Term Memory，长短时记忆网络)**。

## Core Concepts

### Scaled Dot-Product Attention
给定输入嵌入 $$X \in \mathbb{R}^{n \times d}$$，我们将其投影为查询、键和值三个矩阵：

$$
Q = XW^Q, \quad K = XW^K, \quad V = XW^V
$$

其中 $$W^Q, W^K \in \mathbb{R}^{d \times d_k}$$，$$W^V \in \mathbb{R}^{d \times d_v}$$。这里 $d$ 是模型的隐藏维度，$d_k$ 和 $d_v$ 分别是查询/键和值的投影维度。在标准设置中通常 $d_k = d_v = d/h$，其中 $h$ 是注意力头数。

注意力输出的完整公式为：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

这个公式的直觉理解：$QK^T$ 计算每对词元之间的相似度分数（$n \times n$ 矩阵），**Softmax（软最大化函数）** 将分数归一化为概率分布（每行和为1），然后用这些概率对值向量进行加权求和。最终每个词元获得一个融合了其他词元信息的新表示。

### Why Scale by $$\sqrt{d_k}$$?
如果不进行缩放，当 $d_k$ 较大时，点积 $q \cdot k$ 的方差与 $d_k$ 成正比。这会将 softmax 推入饱和区域，导致梯度消失，使模型几乎无法学习。除以 $$\sqrt{d_k}$$ 可以将方差保持在 $$O(1)$$。

**严格的数学推导**：假设 $$q_i, k_i \sim \mathcal{N}(0, 1)$$ 独立同分布，则点积 $q \cdot k = \sum_{i=1}^{d_k} q_i k_i$。因为每个 $q_i k_i$ 的期望为0，方差为 $\text{Var}(q_i)\text{Var}(k_i) + \text{Var}(q_i)[\mathbb{E}(k_i)]^2 + \text{Var}(k_i)[\mathbb{E}(q_i)]^2 = 1$，所以：

$$
\mathbb{E}[q \cdot k] = 0, \quad \text{Var}(q \cdot k) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = d_k
$$

缩放后 $\text{Var}\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = 1$，softmax 的输入保持在合理范围内，确保梯度流动稳定。

**实际影响示例**：在 GPT-3 中 $d_k = 128$，不缩放时点积的标准差约为 $\sqrt{128} \approx 11.3$。softmax 输入值相差 20+ 时输出接近 one-hot 分布（一个值接近1，其余接近0），梯度几乎为零，模型无法有效更新。缩放后标准差为 1，softmax 输出更平滑，每个位置都能获得有意义的梯度信号。

### Attention as Soft Dictionary Lookup
自注意力可以被理解为一个可微分的字典查找操作，这是理解其工作原理最直观的方式：
- **Keys（键）**：定义每个位置"宣告"的内容——"我包含什么信息"
- **Queries（查询）**：定义每个位置"寻找"的内容——"我需要什么信息"
- **Values（值）**：定义要检索的具体信息——"我能提供什么"
- Softmax 权重是"软匹配"分数——不像硬字典只返回一个结果，而是返回所有值的加权组合

这个视角有助于理解许多变体：**Cross-Attention（交叉注意力）** 中 decoder 的查询在 encoder 的键值对中"查找"信息；**KV Cache（键值缓存）** 就是缓存已计算的"字典条目"。

### Causal (Masked) Attention
对于 **Autoregressive（自回归）** 生成（如 GPT 系列），必须屏蔽未来词元以防止信息泄露：

$$
\text{CausalAttention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + M\right)V
$$

其中 $$M_{ij} = -\infty$$ 当 $$j > i$$（上三角部分），确保词元 $i$ 只能关注位置 $$\leq i$$ 的词元。在实际实现中，$-\infty$ 通常用一个很大的负数（如 $-10^9$ 或 `float('-inf')`）代替，经过 softmax 后这些位置的权重变为零。

**因果掩码的重要性**：
- 保证训练时的 **Teacher Forcing（教师强制）** 与推理时的自回归生成保持一致
- 使得整个序列可以并行计算（不像 RNN 需要逐步展开），每个位置只"看到"它前面的上下文
- 训练时一次前向传播就能计算所有位置的损失——这是 Transformer 训练效率的关键
- 没有因果掩码的话，模型训练时"偷看答案"会导致推理时性能灾难性下降

### Complexity Analysis
自注意力的复杂度分析是面试高频考点：
- **时间复杂度**：$$O(n^2 d)$$，其中 $n$ 是序列长度，$d$ 是维度。$QK^T$ 计算需要 $O(n^2 d_k)$，与 $V$ 相乘需要 $O(n^2 d_v)$
- **内存复杂度**：$$O(n^2 + nd)$$——注意力矩阵 $O(n^2)$ 加上输入/输出矩阵 $O(nd)$
- 这个二次缩放是处理长序列的主要瓶颈，也是所有高效注意力研究的动机

**具体数字的直觉**：对于序列长度 $n = 4096$，$d = 4096$（类似 LLaMA-7B），注意力矩阵有 $4096^2 \approx 16.7M$ 个元素。以 FP16 存储需要约 33MB。但对于 $n = 128K$（Claude/GPT-4 级别），注意力矩阵有 $128K^2 \approx 16.4B$ 个元素，需要约 32GB——显然无法放入单个 GPU 的显存。这就是为什么需要 **Flash Attention（闪存注意力）** 等技术来避免显式构建完整的注意力矩阵。

### Attention Patterns and Interpretability
**Mechanistic Interpretability（机制可解释性）** 研究发现，训练后的注意力头会形成可解释的模式：
- **位置头**：关注固定相对位置（如前一个词元），负责局部上下文
- **语法头**：关注语法相关的词元（如动词关注其主语，代词关注其指代对象）
- **稀有词头**：在出现低频词时激活，帮助处理罕见信息
- **全局头**：均匀关注所有位置，类似于全局信息聚合
- 这些发现是 **Anthropic** 和 **OpenAI** 等公司进行模型安全分析的基础工具之一

### Linear Attention and Efficient Alternatives
为了解决 $O(n^2)$ 瓶颈，研究者提出了多种高效替代方案：
- **Linear Attention（线性注意力）**：用核函数近似 softmax，复杂度降至 $O(nd^2)$
- **Sparse Attention（稀疏注意力）**：只计算部分词元对的注意力，如 Longformer 的滑动窗口
- **State Space Models (SSM，状态空间模型)**：如 Mamba，完全放弃注意力，用线性递推代替
- 但目前标准 softmax 注意力 + Flash Attention 仍然是性能最优的组合

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

def masked_self_attention(X, W_q, W_k, W_v):
    # Self-attention with causal mask for autoregressive models.
    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v
    d_k = Q.shape[-1]
    n = Q.shape[0]
    scores = Q @ K.T / np.sqrt(d_k) + causal_mask(n)
    weights = np.exp(scores - scores.max(axis=-1, keepdims=True))
    weights /= weights.sum(axis=-1, keepdims=True)
    return weights @ V
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| 注意力瓶颈分析 | "Transformer 为什么不能处理长序列？" | $$O(n^2)$$ 注意力矩阵；催生 Flash Attention、稀疏注意力 |
| 注意力即软检索 | "自注意力的直觉是什么？" | 键宣告、查询搜索、值传递信息——可微分的字典查找 |
| 因果掩码机制 | "GPT 如何防止看到未来？" | softmax 之前应用上三角 $$-\infty$$ 掩码，使未来位置权重为零 |
| 缩放因子数学推导 | "为什么除以 $$\sqrt{d_k}$$？" | 防止大方差点积导致 softmax 饱和，保持梯度流动 |
| 注意力与卷积/循环对比 | "自注意力相比 RNN/CNN 的优劣？" | 全局感受野 vs 二次复杂度的权衡；并行性 vs 序列性 |
| 注意力可解释性 | "注意力权重能解释模型行为吗？" | 部分可以（位置头、语法头），但需谨慎——注意力不等于归因 |

### Common Interview Questions
- [ ] 为什么自注意力在没有位置编码时具有 **Permutation Equivariance（置换等变性）**？——因为注意力只依赖词元间的相似度，$f(\pi(X)) = \pi(f(X))$
- [ ] 自注意力的计算和内存复杂度是多少？——时间 $$O(n^2 d)$$，内存 $$O(n^2 + nd)$$
- [ ] 因果掩码如何实现自回归生成？——上三角 $-\infty$ 使未来位置的 softmax 权重为零
- [ ] 比较自注意力与卷积和循环网络在序列建模上的差异——路径长度、并行性、归纳偏置
- [ ] 为什么自注意力需要单独注入位置信息？——操作本身对输入顺序不敏感，是置换等变的
- [ ] 如何让注意力处理超长序列（100K+ 词元）？——Flash Attention + 稀疏模式或滑动窗口

## Comparisons

| Aspect | Self-Attention | RNN | CNN (1D) | SSM (Mamba) |
|--------|---------------|-----|----------|-------------|
| 序列建模 | 全局，$$O(1)$$ 路径长度 | 顺序，$$O(n)$$ 路径 | 局部，$$O(n/k)$$ 路径 | 全局，线性递推 |
| 并行化 | 完全并行 | 顺序执行 | 完全并行 | 训练并行/推理线性 |
| 每层复杂度 | $$O(n^2 d)$$ | $$O(n d^2)$$ | $$O(k n d^2)$$ | $$O(nd)$$ |
| 长距离依赖 | 原生支持 | 梯度消失问题 | 需要深层堆叠 | 通过状态传递 |
| 归纳偏置 | 无（完全数据驱动） | 时序性、马尔可夫性 | 局部性、平移不变性 | 线性动态系统 |
| 推理效率 | 每步需重新计算或用 KV 缓存 | 每步 $O(d^2)$ | 不适用于自回归 | 每步 $O(d)$ |

## Key Takeaways

- [ ] 自注意力通过 $$QK^T$$ 相似度计算词元间的成对交互——核心公式必须能手写推导
- [ ] 除以 $$\sqrt{d_k}$$ 防止 softmax 梯度消失——方差从 $d_k$ 归一化到 $1$
- [ ] 因果掩码强制执行自回归属性（不能看到未来），使训练和推理保持一致
- [ ] $$O(n^2)$$ 复杂度催生高效注意力变体（Flash Attention、稀疏注意力、线性注意力）
- [ ] 注意力具有 **Permutation Equivariance（置换等变性）**——位置编码是不可或缺的
- [ ] 注意力头会自发形成可解释的模式——这是 **Mechanistic Interpretability（机制可解释性）** 研究的基础
- [ ] 自注意力可以理解为可微分的字典查找——键宣告、查询搜索、值传递
"""

conn = sqlite3.connect(DB)
cur = conn.cursor()
content = CONTENT.strip()
cur.execute("UPDATE framework_nodes SET description = ? WHERE id = ?", (content, 141))
conn.commit()
print(f"Node 141 updated, length: {len(content)}")
conn.close()
