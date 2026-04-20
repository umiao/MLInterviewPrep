"""Seed: T-P0-542 -- ML Fundamentals T2 content fill, Cat 5 (6 leaves).

Replaces the placeholder TODO[MLF-<slug>] descriptions inserted by
seed_ml_fundamentals_skeleton.py (T-P0-538) with cleaned, KaTeX-rendered
markdown for the six Tier-2 questions under attention_transformer:

  attention_transformer (6):
    - self-attention-complexity-optimization   (#15)
    - scaled-dot-product-attention             (#16)
    - mha-mqa-gqa                              (#17)  [REBUILT comparison table]
    - positional-encoding                      (#18)
    - kv-cache                                 (#19)  [verified LLaMA-2-7B formula]
    - pre-norm-vs-post-norm                    (#20)

T2 = moderate reformat. The source attachment renders every formula three
times (LaTeX + glyph dump + glyph dump). This script collapses each triplet
to a single KaTeX block in $...$ / $$...$$ form, expands first-occurrence
acronyms per data/ml_fundamentals_inventory.yaml's acronyms_to_expand list
(format: **English full term** (acronym, 中文译名)), rebuilds the MHA/MQA/GQA
table that was collapsed in the source, and verifies the KV-cache memory
formula via the LLaMA-2-7B worked example (2 GB at 4K context, fp16).

Idempotency:
  - Each leaf has a stable expected description; second run yields
    updated=0 skipped=6 conflict=0.
  - SHA-256 of the 6 description blobs captured pre/post for audit.
  - If a leaf's existing description is neither the placeholder nor the
    new content (i.e. a human-edited intermediate state), the script
    aborts with [CONFLICT] before any write.

Acceptance:
  - 6 framework_nodes.description rows updated (path LIKE
    'ml-fundamentals/attention_transformer/<slug>')
  - Each description has KaTeX math ($ or $$ delimiters)
  - Each description has section headers (## ...)
  - Re-run is no-op (updated=0)
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"


# ---------------------------------------------------------------------------
# Cleaned descriptions. Raw strings to keep LaTeX backslashes literal.
# ---------------------------------------------------------------------------

DESC_SELF_ATTN_COMPLEXITY = r"""# Self-Attention 复杂度与优化

## 1. 问题设定

输入 $X \in \mathbb{R}^{n \times d}$，$n$ 是序列长度，$d$ 是 hidden dim。标准 self-attention 定义：

$$Q, K, V = X W_Q,\, X W_K,\, X W_V \in \mathbb{R}^{n \times d}$$

$$\text{Attn}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d}}\right) V$$

问题：这个公式在序列长度 $n$ 上的**计算**复杂度和**显存**复杂度各是多少？如何降？

第一次出现的缩写：**Floating-Point Operation** (FLOP, 浮点运算次数)、**High-Bandwidth Memory** (HBM, 高带宽显存)、**Static Random Access Memory** (SRAM, 片上静态随机存储)、**Graphics Processing Unit** (GPU, 图形处理器)、**FlashAttention** (FA, IO 感知的精确注意力)、**Exponential Linear Unit** (ELU, 指数线性单元)。

## 2. 复杂度推导：$O(n^2 d)$

三个步骤按顺序分析：

**(a) 投影 $Q, K, V$**：三次 $(n, d) \times (d, d)$ 的矩阵乘，每次 $O(n d^2)$，线性于 $n$。

**(b) 计算 attention score $Q K^\top$**：$(n, d) \times (d, n) \to (n, n)$，$\text{cost} = n \times n \times d = O(n^2 d)$。物理含义：每个 token 要和其他所有 token 做一次 $d$ 维点积，共 $n \times n$ 对，这是 $n^2$ 的根源（不是等差数列求和）。

**(c) attention weights $\times V$**：$(n, n) \times (n, d) \to (n, d)$，同样 $O(n^2 d)$。

主导项：

$$\boxed{\text{time} = O(n^2 d), \qquad \text{memory} = O(n^2)}$$

显存瓶颈比计算更严重。$n = 32\text{k}$ 时 attention matrix $\approx 1\text{ GB/head}$；长上下文下这是训练和推理的第一个墙。

## 3. 物理意义

$n^2$ 来自"每对 token 都要互相看一次"这个完全连接的二部图结构。只要 attention 的本质是 pairwise interaction，$n^2$ 对数量就消不掉——除非放弃精确、放弃 pairwise，或者换结构。显存是 $O(n^2)$ 而不是 $O(n^2 d)$，因为 attention matrix 中每个元素是一个标量 logit；但它要存下来才能做 row-wise softmax，这就是 FlashAttention 要绕开的点。

## 4. 降复杂度 / 降显存的四类方案

思路分两大类：**精确但更高效**（FlashAttention）和 **近似但更快**（稀疏、线性、核方法）。

### (a) FlashAttention —— 不降复杂度，降 IO

核心洞察：GPU 瓶颈是 HBM $\leftrightarrow$ SRAM 的数据搬运，不是 FLOPs。传统 attention 把 $n \times n$ 的中间矩阵写回 HBM，再读回来做 softmax，搬运量巨大。

FlashAttention 的做法：

- **Tiling**：把 $Q, K, V$ 切成 block，每个 block 在 SRAM 里完整算完一段 attention 再写回 HBM。
- **Online softmax**：softmax 需要全局 max / sum，但可以用增量公式边扫边更新，不用存整个 $n \times n$。
- **反向传播 recompute**：不存 attention matrix，反向时重算。

结果：复杂度仍是 $O(n^2 d)$，但**显存从 $O(n^2)$ 降到 $O(n)$**，wall-clock 快 $2$-$4 \times$。精确无近似损失，现在是所有主流 LLM 训练/推理的标配（FA-2、FA-3 是进一步优化）。

### (b) Sparse Attention —— 只算一部分位置

不是每对 token 都互相看，只看一个稀疏子集。

- **Sliding window**（Longformer / Mistral）：每个 token 只看附近 $w$ 个 token，$O(n w) \to O(n)$。
- **Global tokens**：`[CLS]` 等特殊 token 可以看所有位置，保持全局信息。
- **Dilated / strided**：跳跃式采样远处 token（类似 dilated convolution）。
- **BigBird**：sliding window + global + random，理论仍是 universal approximator。

代价：丢失一些长程信息，效果接近但不等于 full attention。

### (c) Linear Attention —— 改写成 $O(n)$

关键：softmax 把 $Q$ 和 $K$ "粘死"了——必须先算 $Q K^\top$ 才能 row-wise softmax。如果去掉 softmax，利用结合律：

$$(Q K^\top) V = Q (K^\top V)$$

$K^\top V$ 是 $(d, d)$ 矩阵，$Q \cdot (K^\top V)$ 是 $O(n d^2)$，**线性于 $n$**。

用 feature map $\phi$ 近似 softmax：

$$\text{softmax}(Q K^\top) \approx \phi(Q) \phi(K)^\top$$

- **Linear Transformer** (Katharopoulos 2020)：$\phi(x) = \text{ELU}(x) + 1$，保证输出全正。
- **Performer** (FAVOR+, Choromanski 2020)：random feature map，有 $\exp(q^\top k) = \mathbb{E}_\omega[\phi_\omega(q)^\top \phi_\omega(k)]$ 的无偏估计。
- **Linformer**：投影 $K, V$ 到低秩 $(k, d)$。
- **cosFormer, Nyströmformer**：不同 $\phi$ 或低秩近似。

代价：近似误差，长序列上累积；工程优化不如 FlashAttention 成熟。主要用在 full attention 跑不动的极长序列场景。

### (d) 架构替代 —— 跳出 attention

- **Mamba / SSM** (State Space Models)：状态空间模型替代 attention，天然 $O(n)$，长序列性能媲美 Transformer。
- **RWKV**：RNN 风格的 recurrence + Transformer 的 parallel 训练。
- **Mixture of Experts** (MoE, 专家混合)：不是降 attention 复杂度，而是通过稀疏激活扩大容量而不线性增加 FLOPs。

## 5. 四类方案对比表

| 方案 | 计算 | 显存 | 精确? | 典型使用 |
|------|------|------|-------|----------|
| Vanilla | $O(n^2 d)$ | $O(n^2)$ | 精确 | 教科书 |
| FlashAttention | $O(n^2 d)$ | $O(n)$ | 精确 | 现代 LLM 训练 / 推理标配 |
| Sliding window | $O(n w)$ | $O(n w)$ | 近似 | Mistral、Longformer |
| Linear attention | $O(n d^2)$ | $O(d^2)$ | 近似 | 极长序列 |
| Mamba / SSM | $O(n)$ | $O(n)$ | 非 attention | 长序列新方向 |

## 6. 常见追问

- **KV Cache**：推理时前面 token 的 $K, V$ 要重用，显存随序列线性增长，是长上下文推理的主要瓶颈。优化：GQA / MQA（多 query head 共享 K, V，显存砍数倍）、PagedAttention (vLLM，按 page 管理 KV 显存)。详见 [KV Cache](/ml-fundamentals?cat=attention_transformer&slug=kv-cache)。
- **为什么 $\sqrt{d}$ 归一化**：点积方差随 $d$ 线性增长，除以 $\sqrt{d}$ 把 softmax 输入拉回合理量级，避免饱和导致梯度消失。详见 [Scaled Dot-Product Attention](/ml-fundamentals?cat=attention_transformer&slug=scaled-dot-product-attention)。
- **Multi-head 不改变总复杂度**：$h$ 个 head 各自 $d/h$ 维，总成本 $h \cdot O(n^2 \cdot d/h) = O(n^2 d)$ 不变，但引入了表达的多样性（不同 head 关注不同 pattern）。
- **长上下文实际做法**（LLaMA 3、Claude、GPT-4 Turbo 百万级 context）：通常是 FlashAttention + RoPE 长度外推（NTK / YaRN）+ sliding window 混合，而不是单一技术。

## 7. Linear Attention 深挖：$\phi$ 的几何意义

### 为什么 softmax 是瓶颈

$n^2$ 瓶颈来自 softmax **把 $Q$ 和 $K$ 粘死了**——必须先算出完整的 $n \times n$ 矩阵 $Q K^\top$，才能 row-wise 取 softmax。矩阵乘法有结合律 $(Q K^\top) V = Q (K^\top V)$，但 softmax 挡在中间，先算哪个括号的自由度没了。

### 如果没有 softmax，$O(n)$ 是免费的

假装 attention 就是 $Q K^\top V$：

- 先 $Q K^\top$ 再 $V$：$O(n^2 d)$。
- 先 $K^\top V$ 再 $Q$：$(d \times n)(n \times d) = (d \times d)$ 只花 $O(n d^2)$，再 $(n \times d)(d \times d) = O(n d^2)$。**线性于 $n$**。

差别就在计算顺序。Linear Attention 的核心问题是：能不能把 softmax 拆开，让 $Q$ 和 $K$ 解耦？

### $\phi$ 的角色：一个 feature map

$\phi: \mathbb{R}^d \to \mathbb{R}^{d'}$ 是一个把向量映射到另一个（通常更高维）空间的函数，目的是用下面这个近似代替 softmax：

$$\text{softmax}(q \cdot k) \;\approx\; \phi(q)^\top \phi(k)$$

一旦这个近似成立，attention 就变成：

$$\text{Attn}(Q, K, V) \approx \phi(Q)\, \phi(K)^\top V = \phi(Q)\,\big(\phi(K)^\top V\big)$$

右边括号 $\phi(K)^\top V$ 先算，是 $(d' \times n)(n \times d) = O(n d' d)$，然后 $\phi(Q) \cdot (\cdot)$ 又是 $O(n d' d)$。总 $O(n d' d)$，$n$ 线性。

$\phi$ 的几何意义：把 $q, k$ 映射到新空间，在新空间里 softmax 的效果近似用普通内积就能复现。

### 代价

$\phi$ 毕竟是 softmax 的**近似**：误差存在，长序列上会积累；实际效果通常比 full attention 稍差；工程实现和硬件优化没有 FlashAttention 那么成熟。常规长度下 FlashAttention + full attention 仍是更好的选择。
"""


DESC_SCALED_DOT_PRODUCT = r"""# Scaled Dot-Product Attention

## 1. 问题设定

attention score 的核心是 query 和 key 的点积：

$$s_{ij} = q_i \cdot k_j = \sum_{l=1}^{d} q_{i, l}\, k_{j, l}$$

然后 row-wise softmax 得到权重。问题：为什么 Transformer 在 softmax 之前要除以 $\sqrt{d}$？除 $d$、除 $d^2$ 不行吗？

第一次出现的缩写：**Query-Key product** (QK, 查询-键点积)、**Layer Normalization** (LN, 层归一化)、**Root Mean Square Layer Norm** (RMSNorm, 均方根层归一化)、**Maximal Update Parametrization** ($\mu$P, 最大更新参数化)。

## 2. 推导：为什么要除 $\sqrt{d}$

假设 $q, k$ 的每个分量独立、均值 $0$、方差 $1$（初始化或 LN 后大致成立）。那么点积是 $d$ 个独立零均值乘积的和：

$$\mathbb{E}[q \cdot k] = 0$$

$$\text{Var}(q \cdot k) = \sum_{l=1}^{d} \text{Var}(q_l k_l) = d$$

**点积方差随 $d$ 线性增长**，标准差为 $\sqrt{d}$。$d = 64$ 时典型量级 $\approx \pm 8$，$d = 512$ 时 $\approx \pm 22$。这个量级喂进 softmax 就出问题。

除以 $\sqrt{d_k}$ 之后：

$$\text{Var}\!\left(\frac{q \cdot k}{\sqrt{d_k}}\right) = \frac{d_k}{d_k} = 1$$

方差归 $1$，softmax 输入落在合理范围内，梯度饱满。最终公式：

$$\boxed{\text{Attn}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V}$$

这里 $d_k$ 是**每个 head 的 key 维度**，不是总 hidden dim。Multi-head 下 $d_k = d / h$，scale 要用 per-head 的维度。

## 3. 物理意义：不 scale 会怎样

softmax 对输入的相对差值敏感。输入差距 $\approx 20$ 时：

$$\frac{e^{20}}{e^{20} + e^{0}} \approx 1 - 2 \times 10^{-9}$$

softmax 几乎退化成 one-hot——所有权重集中到最大的那个 key，其他被压成 $0$。两个严重后果：

**(a) 梯度消失**：softmax 饱和区导数 $p(1 - p) \to 0$，反向传过来的梯度被压成 $0$，attention 参数学不动。

**(b) 表达力塌陷**：attention 本来是"软选择"，能混合多个位置信息；饱和后变成"硬选一个"，信息瓶颈严重，训练初期尤其糟糕。

$d$ 越大这个问题越严重——这也是为什么 scale 因子必须依赖 $d$。

## 4. 常见追问

### 为什么是 $\sqrt{d}$ 不是 $d$

标准差是 $\sqrt{d}$。除以标准差把**方差归 $1$**；除以方差会把信号压得太死（除完标准差只剩 $1/\sqrt{d}$），softmax 变太平均反而无法区分——既避免饱和，也要保留区分度。

### 其他 attention 类型的 scale

additive attention (Bahdanau) 用 $v^\top \tanh(W q + U k)$，没有 $d$ 相关的方差爆炸问题，不需要 scale。原始 Transformer 论文专门做过消融：$d$ 大时 dot-product + scale 比 additive 稍好且更快。

### $\mu$P 与 scaling-aware 训练

现代大模型训练里，初始化方差、attention scale、lr schedule 都会和 $d$ 关联，形成一套 hyperparameter 可迁移的方案（$\mu$P）。scaled dot-product 里的 $\sqrt{d}$ 是这套思想最早的雏形。

### QK-Norm

一些大模型（Gemma 等）在 $Q$ 和 $K$ 上再加一次 LN / RMSNorm，进一步稳住点积量级，比单纯 $\sqrt{d}$ scaling 更鲁棒，尤其在深层和 long-context 训练中。

### 低精度训练的影响

fp16 / bf16 训练时 softmax 输入再大会直接溢出。$\sqrt{d}$ scale 不仅防梯度消失，也防数值溢出——这是 bf16 训练下 scale 不可省的另一原因。

## 5. 参考

- 方差分析即 $\mu$P 的起点，详见 [Self-Attention 复杂度](/ml-fundamentals?cat=attention_transformer&slug=self-attention-complexity-optimization) 的正文 §4(d) 与追问。
- Transformer 原论文 *Attention Is All You Need* (Vaswani 2017) 的 §3.2.1 给出 $\sqrt{d}$ 的方差论证。
"""


DESC_MHA_MQA_GQA = r"""# MHA / MQA / GQA 多头注意力权衡

## 1. 问题设定

**Multi-Head Attention** (MHA, 多头注意力) 把 $d_{\text{model}}$ 拆成 $h$ 个子空间并行做 attention，每个 head 在不同表示子空间学不同 pattern（局部 / 全局、语法 / 语义等）：

$$\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\, W^O$$

$$\text{head}_i = \text{Attn}(Q W_i^Q,\, K W_i^K,\, V W_i^V)$$

每个 head 的维度 $d_{\text{head}} = d_{\text{model}} / h$。LLM 推理的瓶颈是每层每 token 都要读一遍 **Key-Value cache** (KV, 键值缓存)，于是出现了减少 KV head 数的变种：**Multi-Query Attention** (MQA, 多查询注意力)、**Grouped-Query Attention** (GQA, 分组查询注意力)。

问题：为什么 bottleneck 是 KV 而不是 Q？三种方案怎么取舍？

## 2. 推导：KV head 共享怎么省显存

### MHA

$h$ 个 head 各自拥有独立的 $W_i^Q, W_i^K, W_i^V$。KV cache 大小正比于 head 数：

$$\text{KV mem}_{\text{MHA}} \propto h \cdot d_{\text{head}}$$

### MQA（Shazeer 2019）

所有 $h$ 个 Q head 共享**同一组** $K, V$：

$$\text{head}_i = \text{Attn}(Q W_i^Q,\, K W^K,\, V W^V)$$

KV cache 显存直接除以 $h$：

$$\text{KV mem}_{\text{MQA}} = \frac{1}{h} \cdot \text{KV mem}_{\text{MHA}}$$

### GQA（Ainslie 2023）

把 $h$ 个 Q head 分成 $g$ 组（$1 < g < h$），每组共享一对 $K, V$：

$$\text{KV mem}_{\text{GQA}} = \frac{g}{h} \cdot \text{KV mem}_{\text{MHA}}$$

LLaMA-2-70B 取 $h = 64, g = 8$，KV cache 砍到 MHA 的 $1/8$；Mixtral 8x7B 同样 $g = 8$。

$$\boxed{\text{GQA 是 MHA 和 MQA 之间的插值：}\; g = h \Rightarrow \text{MHA}, \; g = 1 \Rightarrow \text{MQA}}$$

## 3. 物理意义：为什么省 KV 不是省 Q

Decoder 推理每生成一个 token：

- $Q$ 只算**当前**这一个 token 的一份（$1 \times h \times d_{\text{head}}$），算完丢弃。
- $K, V$ 要**缓存历史所有 token**的值以便反复重用（$N \times h \times d_{\text{head}}$，$N$ 是到目前为止的序列长度）。

于是 KV cache 随 $N$ 线性增长而 Q 不会。在长上下文下 KV cache 很快超过模型权重本身的显存，成为首要瓶颈；同时每步 decode 都要把整个 KV cache 从 HBM 读进来再算 attention，**memory-bandwidth** 成为瓶颈。**省 KV head 数 $\Leftrightarrow$ 省 cache 显存 $\Leftrightarrow$ 省每步读 HBM 的字节数 $\Leftrightarrow$ 提高 tokens/sec**。

## 4. 三者对比（重建自 T-MLF-05 inventory，源表在附件中被折叠）

| 方案 | $K, V$ head 数 | KV cache 显存 | 推理速度 | 质量 | 典型使用 |
|------|----------------|---------------|----------|------|----------|
| **MHA** | $h$ | $\times 1$ | 基准 | 最好（有冗余） | 原始 Transformer、BERT、GPT-2 |
| **MQA** | $1$ | $\times \frac{1}{h}$ | 最快 | 略降，训练不太稳 | PaLM、Falcon |
| **GQA** | $g$（$1 < g < h$） | $\times \frac{g}{h}$ | 接近 MQA | 接近 MHA | **主流**：LLaMA-2-70B、Mixtral、Qwen（典型 $g = 8$） |

## 5. 常见追问

### MQA 为什么"训练不太稳"

所有 Q head 共享 $K, V$ 相当于强行约束了 attention 的容量。训练初期如果 learning rate 没调好，KV 的表达力不够容易出现 loss spike；小规模从头训时 MQA 甚至比 MHA 差一个档位。GQA 保留了 $g$ 组独立 KV，缓冲了这个问题，所以更主流。

### 从 MHA checkpoint 转 GQA 如何 uptraining

Ainslie 2023 的做法：把 MHA 中每组 $h / g$ 个 KV 头**平均**成一组，得到 GQA 初始化；然后在少量数据上 continued pretraining（约 $5\%$ 的原训练量）即可恢复质量。LLaMA-2-70B 的 70B GQA 就是这么从 MHA 升上来的。

### 为什么 $g = 8$ 是 sweet spot

经验上：$g = 8$ 时质量接近 MHA（差距可忽略），显存 / bandwidth 已经砍到 MHA 的 $1/8$；再减小到 $g = 4, 2, 1$ 边际节省收益下降但质量下降加速。这是"看 head 冗余度"和"KV 成本"两条曲线的交点。

### Multi-head 本质是否有冗余

Voita 2019 实证：相当一部分 head 可以剪掉（贡献极小）。这为 GQA / MQA 的合理性提供了经验依据——把冗余的 head 挤出去，再共享 KV，既省显存又几乎不损失质量。

## 6. 参考

- 源触发：Shazeer 2019 (*Fast Transformer Decoding: One Write-Head is All You Need*, MQA) 和 Ainslie 2023 (*GQA: Training Generalized Multi-Query Transformer Models*, GQA)。
- 与 [KV Cache](/ml-fundamentals?cat=attention_transformer&slug=kv-cache) 的显存公式配合读：`KV mem = 2 × L × N × n_kv_head × d_head × bytes`，GQA 就是把 $n_{\text{kv\_head}}$ 从 $h$ 降到 $g$。
"""


DESC_POSITIONAL_ENCODING = r"""# Positional Encoding：Sinusoidal / Learned / RoPE / ALiBi

## 1. 问题设定

self-attention 对 token 顺序**天然不变**（permutation equivariant）：交换两个 token 的位置，attention 输出跟着交换，但每个位置看到的其他位置的信息不变。这显然不对——语言里顺序有意义。于是需要**Positional Encoding** (PE, 位置编码) 把位置信息注入进去。

四种主流方案：Sinusoidal / Learned / **Rotary Position Embedding** (RoPE, 旋转位置编码) / **Attention with Linear Biases** (ALiBi, 线性偏置注意力)。

其他第一次出现的缩写：**Neural Tangent Kernel-aware scaling** (NTK, 神经正切核尺度扩展)、**Yet another RoPE extensioN** (YaRN, RoPE 长度外推方法)。

## 2. 推导：四种方案的公式

### (a) Sinusoidal（原 Transformer，Vaswani 2017）

固定正弦余弦函数，加到 input embedding：

$$PE_{(pos, 2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right), \qquad PE_{(pos, 2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)$$

每个维度是不同频率的 sin/cos。理论可外推到未见过的长度，实际效果一般。

### (b) Learned

位置当作 vocab，训一个大小为 max_len 的 embedding 表。和 token embedding 同维度、同加法注入。训练稳定但**不能外推**到训练长度外（vocab 外 token 没有 embedding）。BERT、GPT-2 用此。

### (c) RoPE（Su 2021）

对 $Q, K$ 分别乘一个依赖位置 $m$ 的旋转矩阵 $R_m$。关键恒等式：

$$\boxed{\langle R_m q, R_n k \rangle = \langle q, R_{n - m}^\top R_m^\top R_m k \rangle = \langle q, R_{n - m} k \rangle}$$

（利用旋转矩阵 $R_m^\top R_m = I$ 和 $R_m^\top R_n = R_{n - m}$）。

内积只依赖**相对位置 $n - m$**，且不改变向量模长 $\|R_m q\| = \|q\|$。实现上就是对 $Q, K$ 的相邻两维做一个 2D 旋转：

$$\begin{pmatrix} q_{2i}' \\ q_{2i+1}' \end{pmatrix} = \begin{pmatrix} \cos m\theta_i & -\sin m\theta_i \\ \sin m\theta_i & \cos m\theta_i \end{pmatrix} \begin{pmatrix} q_{2i} \\ q_{2i+1} \end{pmatrix}$$

$\theta_i = 10000^{-2i/d}$，频率从高到低。

### (d) ALiBi（Press 2022）

**不改动 $Q, K$**，直接在 attention logits 上加一个线性距离偏置：

$$\text{logit}_{ij} \mathrel{+}= -m_h \cdot |i - j|$$

$m_h$ 是**每个 head 特定**的斜率（几何序列 $2^{-8/h}, 2^{-16/h}, \ldots$），不学参数。距离越远，权重越被压低。

## 3. 物理意义：为什么主流是 RoPE

四个优点让 RoPE 几乎垄断 2023+ 的 LLM：

- **相对位置自然出现在 QK 内积里**：不需要改 value，不污染语义信号；attention 算完就自带相对位置感。
- **乘法（旋转）而不是加法**：加法会把位置信号和 embedding 语义信号混在一起，乘法（正交旋转）保留语义模长，只旋转方向。
- **模长不变**：$\|R_m q\| = \|q\|$，训练数值稳定，不会随位置引入 scale 漂移。
- **可长度外推**：配合 NTK-aware scaling、YaRN 等后处理，可以把训练时 $4\text{k}$ 的 RoPE 延长到 $32\text{k}$ / $128\text{k}$ 推理，几乎不掉点。

ALiBi 外推能力更强（斜率固定、不依赖训练长度），但表达力稍差、不太适合某些双向任务，所以更多用于 MPT 那条技术线。

## 4. 常见追问

### RoPE 长度外推：NTK 与 YaRN

- **NTK-aware scaling**：把 base $10000$ 改成 $10000 \cdot s^{d/(d-2)}$（$s$ 是目标扩展比），让高频不变、低频稀疏拉长，避免硬截断。零训练即可扩 $2$-$4 \times$。
- **YaRN**：更精细的频率分桶 + attention scale 调整，扩到 $8$-$16 \times$ 而保持质量。
- **Code Llama / LLaMA-3** 用 NTK + 少量 continued pretraining 把 $4\text{k}$ → $16\text{k}$ → $128\text{k}$。

### ALiBi vs RoPE 谁外推好

ALiBi 外推几乎无损（斜率独立于长度），在 MPT-7B 上测试 $2\text{k}$ 训练外推到 $16\text{k}$ 质量仍稳。RoPE 裸外推会掉点（高频相位周期性错位），必须配 NTK / YaRN。但 RoPE 的绝对质量上限更高，所以主流选择还是 RoPE + 外推技术。

### 为什么 Sinusoidal 理论可外推但实际不行

Sinusoidal PE 加到 embedding 上，模型在训练时没见过 $pos = 5000$ 对应的 sin/cos pattern 会如何影响 attention；而 RoPE 是在 attention 内积里作用，数学上相对位置的表示更直接。实践中 Sinusoidal 外推效果通常和 Learned 差不多差。

### 为什么 RoPE 频率 base 是 $10000$

继承自原 Transformer 的 Sinusoidal PE，目的是**让不同维度覆盖从短程到长程的位置差异**：低频维度周期长、能区分远距离；高频维度周期短、精细区分相邻位置。base $= 10000$ 是经验值，LLaMA-3 为长上下文把 base 调大到 $500000$（等价于频率变低、可表达范围变长）。

## 5. 参考

- 源论文：Su 2021 (RoPE)、Press 2022 (ALiBi)、Bloc97 2023 (NTK-aware)、Peng 2023 (YaRN)。
- 与 [KV Cache](/ml-fundamentals?cat=attention_transformer&slug=kv-cache) 和 [MHA/MQA/GQA](/ml-fundamentals?cat=attention_transformer&slug=mha-mqa-gqa) 配合读：长上下文推理需要 RoPE（相对位置）+ GQA（省 KV 显存）+ FlashAttention（省 attention 显存）三件套。
"""


DESC_KV_CACHE = r"""# KV Cache：原理与显存

## 1. 问题设定

decoder-only LLM 推理时逐个 token 自回归生成。每生成一个 token $t$，都要做：

$$q_t \cdot K_{1:t}^\top, \qquad \text{softmax}(\cdot) \cdot V_{1:t}$$

关键观察：前面 token 的 $K, V$ 只依赖自己（不依赖 $q_t$），**可以缓存下来反复用**。这就是 **Key-Value cache** (KV, 键值缓存)。

问题：KV cache 省了多少计算？显存成本怎么算？LLaMA-2-7B 在 $4\text{k}$ context 下 KV cache 多大？

第一次出现的缩写：**High-Bandwidth Memory** (HBM, 高带宽显存)、**Multi-Head Attention** (MHA, 多头注意力)、**Multi-Query Attention** (MQA, 多查询注意力)、**Grouped-Query Attention** (GQA, 分组查询注意力)。

## 2. 推导：prefill vs decode 两阶段

### Prefill：一次性喂入 prompt

输入 prompt 长度 $N_{\text{prompt}}$，一次性算完所有位置的 $Q, K, V$ 和 attention。复杂度：

$$\text{Prefill cost} = O(N_{\text{prompt}}^2 \cdot d) \quad \text{(每层)}$$

这一步顺便把 $K_{1:N_{\text{prompt}}}$ 和 $V_{1:N_{\text{prompt}}}$ 写进 KV cache。

### Decode：每步只算当前 token

第 $t$ 步生成时：

- 只算**当前 token** 的 $q_t, k_t, v_t$（一份）。
- 把 $k_t, v_t$ 追加到 cache：$K_{1:t} = [K_{1:t-1}, k_t]$，$V_{1:t}$ 类似。
- attention：$\text{softmax}(q_t K_{1:t}^\top / \sqrt{d}) V_{1:t}$，是 $(1, d) \times (d, t) \times (t, d)$。

每步 cost：

$$\text{Decode step cost} = O(t \cdot d) \quad \text{(每层)}$$

没有 cache 的话每步要重算整个 prefix：$O(t^2 \cdot d)$，即每步重新 $O(t)$ 倍。KV cache 的加速倍数约为 $O(t)$——context 越长加速越明显。

### 瓶颈：从 FLOPs 变成 memory bandwidth

decode 阶段每步要从 HBM 把**整个 KV cache** 读进 SRAM 才能算 attention。计算量 $O(t d)$ 很小，但读的字节数正比于 $t \cdot n_{\text{kv\_head}} \cdot d_{\text{head}}$。现代 GPU（H100、A100）decode 阶段几乎总是 **memory-bandwidth bound**，不是 compute bound。

## 3. 物理意义：显存公式

每个 batch、每个序列的 KV cache 大小：

$$\boxed{\text{KV cache size} = 2 \times L \times N \times n_{\text{kv\_head}} \times d_{\text{head}} \times \text{bytes}}$$

各项含义：

- $2$：$K$ 和 $V$ 各存一份。
- $L$：层数。每层都要存 KV。
- $N$：当前序列长度（随 decode 线性增长）。
- $n_{\text{kv\_head}}$：MHA $= h$，GQA $= g$，MQA $= 1$。
- $d_{\text{head}}$：每个 head 的维度 $= d_{\text{model}} / h$。
- bytes：fp16/bf16 $= 2$，fp8 $= 1$，fp32 $= 4$。

### LLaMA-2-7B 在 4K context 下的 KV cache

$L = 32$、$h = 32$、$d_{\text{head}} = 128$、$N = 4096$、fp16（MHA，$n_{\text{kv\_head}} = h = 32$）：

$$\text{KV cache} = 2 \times 32 \times 4096 \times 32 \times 128 \times 2\text{ bytes}$$

$$= 2{,}147{,}483{,}648\text{ bytes} \approx 2.0\text{ GB}$$

这就是**一个序列一份**的 KV cache 大小。batch size = 32、context = 4K 的服务场景，KV cache 占 $64\text{ GB}$——比 7B 模型本身（$14\text{ GB}$ fp16 权重）还大 $4.5 \times$。这是长上下文 serving 的首要显存瓶颈，也是 GQA / MQA 被推广的根本原因。

## 4. 常见追问

### GQA / MQA 下的 KV cache 砍多少

LLaMA-2-70B 用 GQA $g = 8$（$h = 64$）：$n_{\text{kv\_head}}$ 从 $64$ 降到 $8$，KV cache 直接砍到 $1/8$。$128\text{k}$ context、fp16 下原本要 $\sim 80\text{ GB}$ 的 cache 降到 $\sim 10\text{ GB}$，同一张 H100 才放得下。

### PagedAttention（vLLM）

传统 KV cache 要连续显存，batch 内序列长度不一时严重浪费（按 max_len 预留）。vLLM 的 PagedAttention 借鉴 OS 虚拟内存：把 KV cache 切成固定 block（如 $16$ 个 token 一页），按需分配，不同请求按 page 拼接。实际利用率从 $\sim 40\%$ 提到 $\sim 96\%$。

### KV 量化：int8 / fp8 / int4

把 $K, V$ 量化可以再砍一半显存。int8 KV 几乎无损，fp8 / int4 在长 context 上会逐步掉点。主流做法：$K$ 比 $V$ 敏感（影响 softmax），所以 $K$ 用 fp8、$V$ 用 int4；或全部保持 fp16、靠 GQA 控显存。

### 为什么 prefill 不叫 KV cache "加速"

prefill 本来就是一次性算完，不需要从 cache 读——但它会**写入** cache，为 decode 阶段准备。prefill 的优化另外有 FlashAttention、chunked prefill 等。"KV cache 加速"特指 decode 阶段重用历史 KV，不再重算。

### Speculative decoding 与 KV cache

speculative decoding（小模型 draft、大模型 verify）需要大模型对 draft tokens 做一次并行的 attention，这一步也要用到大模型的 KV cache。draft model 的 KV cache 另算。

## 5. 参考

- 与 [MHA/MQA/GQA](/ml-fundamentals?cat=attention_transformer&slug=mha-mqa-gqa) 配合读：上面的 $n_{\text{kv\_head}}$ 就是那篇里讲的 $h, g, 1$。
- vLLM 的 [PagedAttention 论文](https://arxiv.org/abs/2309.06180) (Kwon 2023) 给出端到端吞吐对比。
- LLaMA-2 tech report 有 7B / 13B / 70B 的 attention 参数（$L, h, d_{\text{head}}$），用于自己核 KV cache 算式。
"""


DESC_PRE_POST_NORM = r"""# Pre-norm vs Post-norm

## 1. 问题设定

Transformer block 里 **Layer Normalization** (LN, 层归一化) 放哪？原始 Transformer (Vaswani 2017) 把 LN 放在残差相加**之后**（post-norm）；现代 LLM（LLaMA、GPT-3+、PaLM、Mistral）全部改成放**之前**（pre-norm），并且多数把 LN 换成 **Root Mean Square Layer Norm** (RMSNorm, 均方根层归一化)。为什么？

## 2. 推导：两种结构的残差路径

用 $x_l$ 表示第 $l$ 层输入，$F$ 表示 attention 或 FFN 子模块。

### Post-norm（原 Transformer）

$$x_{l+1} = \text{LN}\big(x_l + F(x_l)\big)$$

### Pre-norm

$$x_{l+1} = x_l + F\big(\text{LN}(x_l)\big)$$

关键差异在**残差路径上是否有 LN**：

- Post-norm 下 $x_l \to x_{l+1}$ 的残差通路被 LN 夹在外面，梯度要穿过 LN 的 Jacobian。
- Pre-norm 下残差通路是**完全恒等**的：$x_l \to x_{l+1}$ 的加法直接穿过，LN 只作用在子模块输入上。

这个差异决定了深层堆叠的稳定性。

## 3. 物理意义：为什么 pre-norm 稳定

### 梯度畅通

反向传播时，pre-norm 下 $\partial x_{l+1} / \partial x_l = I + \partial F / \partial x_l$（LN 只作用在 $F$ 分支上）。深层堆叠时梯度有一条**无衰减的恒等路径**直通浅层，和 ResNet 同理；深度增加也不会爆炸 / 消失。

Post-norm 下 $\partial x_{l+1} / \partial x_l = \partial \text{LN} / \partial(\cdot) \cdot (I + \partial F / \partial x_l)$，多了 LN 的 Jacobian 缩放。深层堆叠会让 residual stream 的 scale 逐层放大 / 缩小，梯度难控。

$$\boxed{\text{Pre-norm }\Rightarrow\text{ 恒等残差 }\Rightarrow\text{ 深层稳定，无需 warmup}}$$

### 不需要 learning rate warmup

原始 Transformer 需要仔细的 lr warmup（如 $4000$ 步 linear warmup 再 decay）来避免早期梯度爆炸。pre-norm 配上常规 AdamW + cosine decay 就能稳定训练，工程上大幅简化。LLaMA / GPT-3 / PaLM 全系列都受益于这一点。

### 代价：residual stream 的 norm 会放大

pre-norm 下每层把 $F(\text{LN}(x_l))$ 加到 $x_l$ 上，而 $F$ 的输出 norm 不被后续 LN 重置——所以 residual stream 的 $\|x_l\|$ 会随深度累积增大。解决：堆完所有 block 后加一个 **final LN**（LLaMA 就是这样做），把输出送到 `lm_head` 之前归一化。

### 被诟病的 "层贡献退化"

Liu 2020 等工作指出：深层 pre-norm 模型里，后面的层对输出的贡献变小（因为 $\|x_l\|$ 很大，而 $\|F(\text{LN}(x_l))\|$ 相对小），网络倾向于"浅层有效 + 深层微调"。但工程可靠性压倒一切，所以主流仍然选 pre-norm。

## 4. 常见追问

### 为什么要换成 RMSNorm

标准 LN 同时做 mean centering 和 variance scaling：

$$\text{LN}(x) = \frac{x - \mu}{\sigma} \cdot \gamma + \beta$$

RMSNorm 去掉 mean centering，只做 RMS 归一化：

$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d} \sum_i x_i^2 + \epsilon}} \cdot \gamma$$

省掉一个 mean 的 reduction + 减法 + $\beta$ 参数。实证上质量几乎无损，计算省 $\sim 10\%$，梯度也稍稳。LLaMA 系列标准配置。

### DeepNorm（Post-norm 改良）

微软 2022 年的 DeepNorm 证明 post-norm 加合适的残差缩放也能训到 $1000$ 层，思路是把 $x_l + F(x_l)$ 改成 $\alpha \cdot x_l + F(x_l)$ 并精细初始化。主要用在 BERT 那条线和超深 encoder。decoder-only LLM 主流还是 pre-norm + RMSNorm。

### Sandwich Norm / DoubleNorm

有些变种（Gemma 等）在 $F$ 前后各加一次 RMSNorm（pre + post 都有），用以进一步稳定超长上下文训练。是 pre-norm 的加强版，不是回到 post-norm。

### QK-Norm 不算 pre-norm / post-norm 之争

QK-Norm 是在 attention 内部对 $Q, K$ 各加一次 LN / RMSNorm，目的是稳住点积量级（见 [Scaled Dot-Product Attention](/ml-fundamentals?cat=attention_transformer&slug=scaled-dot-product-attention) 追问），和 block 级 pre/post-norm 独立。

### 训练不稳定时的调试信号

如果你选的是 pre-norm 但训练仍然爆炸：优先看 attention logits 量级（考虑 QK-Norm）、residual stream norm（考虑 final LN 或 sandwich norm）、lr 和 gradient clipping——而不是回去切 post-norm。

## 5. 参考

- Xiong 2020 (*On Layer Normalization in the Transformer Architecture*) 首次系统分析 pre-norm 为何不需要 warmup。
- Liu 2020 (*Understanding the Difficulty of Training Transformers*) 指出深层 pre-norm 的层贡献衰减。
- LLaMA 技术报告：pre-norm + RMSNorm + SwiGLU + RoPE 是 2023+ LLM 的默认栈。
"""


# Map each leaf path -> (placeholder, new_description)
LEAVES: dict[str, tuple[str, str]] = {
    "ml-fundamentals/attention_transformer/self-attention-complexity-optimization": (
        "TODO[MLF-self-attention-complexity-optimization]",
        DESC_SELF_ATTN_COMPLEXITY,
    ),
    "ml-fundamentals/attention_transformer/scaled-dot-product-attention": (
        "TODO[MLF-scaled-dot-product-attention]",
        DESC_SCALED_DOT_PRODUCT,
    ),
    "ml-fundamentals/attention_transformer/mha-mqa-gqa": (
        "TODO[MLF-mha-mqa-gqa]",
        DESC_MHA_MQA_GQA,
    ),
    "ml-fundamentals/attention_transformer/positional-encoding": (
        "TODO[MLF-positional-encoding]",
        DESC_POSITIONAL_ENCODING,
    ),
    "ml-fundamentals/attention_transformer/kv-cache": (
        "TODO[MLF-kv-cache]",
        DESC_KV_CACHE,
    ),
    "ml-fundamentals/attention_transformer/pre-norm-vs-post-norm": (
        "TODO[MLF-pre-norm-vs-post-norm]",
        DESC_PRE_POST_NORM,
    ),
}


def sha256_of_descriptions(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pairs of the 6 target leaves."""
    h = hashlib.sha256()
    for path in sorted(LEAVES.keys()):
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE path = ?", (path,)
        ).fetchone()
        h.update(path.encode("utf-8"))
        h.update(b"\x00")
        h.update((row[0] or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: each description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    # Pre-flight: validate every staged content meets AC before touching DB.
    for path, (_placeholder, content) in LEAVES.items():
        validate_content(path, content)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_descriptions(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = {"UPDATED": 0, "SKIPPED": 0}
        for path, (placeholder, new_content) in LEAVES.items():
            row = conn.execute(
                "SELECT id, description FROM framework_nodes WHERE path = ?",
                (path,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"[FAIL] missing node at path={path}")
            node_id, current = row
            if current == new_content:
                counts["SKIPPED"] += 1
                print(f"[SKIP]   id={node_id} path={path}")
                continue
            if current != placeholder:
                preview = (current or "")[:80].replace("\n", " ")
                raise RuntimeError(
                    f"[CONFLICT] path={path}: existing description neither "
                    f"placeholder nor expected new content. "
                    f"current[:80]={preview!r}"
                )
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (new_content, node_id),
            )
            counts["UPDATED"] += 1
            print(
                f"[UPDATE] id={node_id} path={path} "
                f"len={len(new_content)} (was {len(current)})"
            )

        conn.commit()
        post_hash = sha256_of_descriptions(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={counts['UPDATED'] + counts['SKIPPED']} (expected 6)"
    )
    if counts["UPDATED"] + counts["SKIPPED"] != 6:
        print("[FAIL] expected to touch exactly 6 leaves")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
