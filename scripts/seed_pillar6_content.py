"""Seed Pillar 6 (Deep Learning & LLMs) framework node descriptions.

Usage:
    python scripts/seed_pillar6_content.py

Populates the `description` field for all 24 Pillar 6 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== TRANSFORMER DEEP UNDERSTANDING =====

CONTENT["pillar6.transformer.self_attention"] = r"""# Self-Attention Mechanism

## Overview
Self-attention is the core building block of the Transformer architecture. It allows each token to attend to every other token in the sequence, computing a weighted combination of value vectors based on query-key similarity. Understanding self-attention deeply is essential for any MLE working with LLMs.

## Core Concepts

### Scaled Dot-Product Attention
Given input embeddings $X \in \mathbb{R}^{n \times d}$, we project into queries, keys, and values:

$$
Q = XW^Q, \quad K = XW^K, \quad V = XW^V
$$

where $W^Q, W^K \in \mathbb{R}^{d \times d_k}$ and $W^V \in \mathbb{R}^{d \times d_v}$.

The attention output is:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

### Why Scale by $\sqrt{d_k}$?
Without scaling, for large $d_k$, the dot products $q \cdot k$ have variance proportional to $d_k$. This pushes softmax into saturated regions where gradients vanish. Scaling by $\sqrt{d_k}$ keeps variance at $O(1)$.

If $q_i, k_i \sim \mathcal{N}(0, 1)$ i.i.d., then:

$$
\text{Var}(q \cdot k) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = d_k
$$

### Attention as Soft Dictionary Lookup
Self-attention can be interpreted as a differentiable dictionary:
- **Keys** define what each position "advertises"
- **Queries** define what each position "looks for"
- **Values** define what information to retrieve
- Softmax weights are the "soft match" scores

### Causal (Masked) Attention
For autoregressive generation, future tokens must be masked:

$$
\text{CausalAttention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + M\right)V
$$

where $M_{ij} = -\infty$ for $j > i$ (upper triangle), ensuring token $i$ can only attend to positions $\leq i$.

### Complexity Analysis
- Time: $O(n^2 d)$ for sequence length $n$ and dimension $d$
- Memory: $O(n^2)$ for the attention matrix
- This quadratic scaling is the primary bottleneck for long sequences

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
| Explain attention bottleneck | "Why can't Transformers handle long sequences?" | $O(n^2)$ attention matrix; motivates Flash Attention, sparse attention |
| Attention = soft retrieval | "Intuition for self-attention?" | Keys advertise, queries search, values deliver information |
| Causal masking | "How does GPT prevent seeing future?" | Upper-triangular $-\infty$ mask before softmax |
| Scaling justification | "Why divide by $\sqrt{d_k}$?" | Prevents softmax saturation from large-variance dot products |

### Common Interview Questions
- [ ] Why is self-attention permutation-equivariant without positional encoding?
- [ ] What is the computational and memory complexity of self-attention?
- [ ] How does causal masking enable autoregressive generation?
- [ ] Compare self-attention to convolution and recurrence for sequence modeling.
- [ ] Why does self-attention need positional information injected separately?

## Comparisons

| Aspect | Self-Attention | RNN | CNN (1D) |
|--------|---------------|-----|----------|
| Sequence modeling | Global, $O(1)$ path length | Sequential, $O(n)$ path | Local, $O(n/k)$ path |
| Parallelization | Fully parallel | Sequential | Fully parallel |
| Complexity per layer | $O(n^2 d)$ | $O(n d^2)$ | $O(k n d^2)$ |
| Long-range deps | Native | Vanishing gradients | Needs deep stacking |

## Key Takeaways

- [ ] Self-attention computes pairwise token interactions via $QK^T$ similarity
- [ ] Scaling by $\sqrt{d_k}$ prevents gradient vanishing in softmax
- [ ] Causal mask enforces autoregressive property (no future peeking)
- [ ] $O(n^2)$ complexity motivates efficient attention variants (Flash, sparse, linear)
- [ ] Attention is permutation-equivariant -- position encoding is essential
"""

CONTENT["pillar6.transformer.multi_head_attention"] = r"""# Multi-Head Attention

## Overview
Multi-head attention (MHA) runs multiple attention operations in parallel with different learned projections, allowing the model to attend to information from different representation subspaces. It is the standard attention mechanism in all modern Transformers.

## Core Concepts

### Multi-Head Formulation
Given $h$ heads, each head $i$ computes attention independently:

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)
$$

where $W_i^Q, W_i^K \in \mathbb{R}^{d \times d_k}$, $W_i^V \in \mathbb{R}^{d \times d_v}$, with $d_k = d_v = d/h$.

The outputs are concatenated and projected:

$$
\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)W^O
$$

where $W^O \in \mathbb{R}^{d \times d}$.

### Why Multiple Heads?
- A single attention head can only compute one attention pattern per position
- Multiple heads allow attending to different aspects: syntactic, semantic, positional
- Heads specialize: some attend locally, some globally, some to specific relations
- Empirically, multiple smaller heads outperform one large head of the same total dimension

### Parameter Count
For a model with dimension $d$ and $h$ heads:
- Per head: $3 \times d \times (d/h)$ for Q, K, V projections
- All heads: $3d^2$ (same as a single large head)
- Output projection: $d^2$
- Total MHA: $4d^2$ parameters

### Head Pruning and Redundancy
Research shows many heads can be pruned with minimal quality loss. Michel et al. (2019) found that in some layers, a single head suffices. This motivates:
- Structured pruning of attention heads
- Multi-Query Attention (MQA) and Grouped-Query Attention (GQA)

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
| Head specialization | "Why multiple heads?" | Different heads learn different attention patterns (local, global, syntactic) |
| Param equivalence | "Are MHA params more than single head?" | Same $3d^2$ for Q/K/V; heads split the dimension |
| Head pruning | "How to make attention faster?" | Many heads are redundant; pruning maintains quality |
| MHA vs MQA | "Inference optimization" | MQA shares K/V across heads, reducing KV cache by $h\times$ |

### Common Interview Questions
- [ ] Why does MHA use $d_k = d/h$ instead of full $d$ per head?
- [ ] How does the total parameter count of MHA compare to single-head attention?
- [ ] What do different attention heads learn to attend to?
- [ ] How does MHA relate to ensemble methods?
- [ ] Explain the output projection $W^O$ -- why is it needed?

## Comparisons

| Aspect | Multi-Head (MHA) | Multi-Query (MQA) | Grouped-Query (GQA) |
|--------|-----------------|-------------------|---------------------|
| K/V per head | Separate | Shared across all | Shared within groups |
| KV cache size | $2 \times n \times h \times d_k$ | $2 \times n \times d_k$ | $2 \times n \times g \times d_k$ |
| Quality | Baseline | Slight degradation | Near-MHA quality |
| Inference speed | Baseline | Fastest | Good balance |

## Key Takeaways

- [ ] MHA splits $d$ into $h$ heads, each computing attention in $d/h$ dimensions
- [ ] Total parameter count is $4d^2$ (same cost as one big head + output projection)
- [ ] Heads specialize in different attention patterns, improving representation
- [ ] Many heads can be pruned -- motivates MQA/GQA for efficient inference
- [ ] Output projection $W^O$ mixes information across heads
"""

CONTENT["pillar6.transformer.position_encoding"] = r"""# Position Encoding (Sinusoidal, RoPE, ALiBi)

## Overview
Self-attention is permutation-equivariant -- it has no inherent notion of token position. Position encodings inject sequential information so the model can distinguish token order. Modern approaches include sinusoidal (original Transformer), learned absolute, Rotary Position Embeddings (RoPE), and Attention with Linear Biases (ALiBi).

## Core Concepts

### Sinusoidal Position Encoding (Vaswani et al., 2017)
Deterministic encoding added to input embeddings:

$$
PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d}}\right), \quad PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d}}\right)
$$

Key properties:
- Each dimension has a different frequency, forming a unique "fingerprint" per position
- Relative positions can be represented as linear transformations: $PE_{pos+k}$ is a linear function of $PE_{pos}$
- Generalizes to unseen sequence lengths (extrapolation)

### Learned Absolute Position Embeddings
A lookup table $E_{pos} \in \mathbb{R}^{L \times d}$ added to token embeddings. Used in BERT, GPT-2.
- Pros: more expressive than sinusoidal
- Cons: fixed max length $L$; no extrapolation

### Rotary Position Embeddings (RoPE)
Used in LLaMA, Mistral, and most modern LLMs. Encodes position by rotating query/key vectors:

$$
f(x, m) = \begin{pmatrix} x_1 \\ x_2 \end{pmatrix} \otimes \begin{pmatrix} \cos m\theta \\ \cos m\theta \end{pmatrix} + \begin{pmatrix} -x_2 \\ x_1 \end{pmatrix} \otimes \begin{pmatrix} \sin m\theta \\ \sin m\theta \end{pmatrix}
$$

where $m$ is position and $\theta_i = 10000^{-2i/d}$.

The key property: $\langle f(q, m), f(k, n) \rangle$ depends only on $q$, $k$, and the relative position $m - n$:

$$
\text{Re}[\langle f(q, m), f(k, n) \rangle] = g(q, k, m-n)
$$

### ALiBi (Attention with Linear Biases)
Adds a position-dependent bias directly to attention scores instead of modifying embeddings:

$$
\text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + m \cdot [-(i-j)]_{i,j}\right)
$$

where $m$ is a head-specific slope (geometric sequence, e.g., $2^{-8/h}, 2^{-16/h}, \ldots$).

- No extra parameters or computation in embeddings
- Strong length extrapolation without fine-tuning
- Each head has a different slope: some attend locally, others globally

### NTK-Aware Scaling for RoPE
To extend context length beyond training, scale the frequency base:

$$
\theta_i' = \theta_i \cdot \alpha^{-2i/d}, \quad \alpha = \frac{L'}{L}
$$

This preserves local position resolution while stretching long-range capacity.

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
| Absolute vs relative | "Compare position encoding methods" | Absolute: simple but no extrapolation. Relative: generalizes better |
| RoPE rotation | "How does RoPE work?" | Rotation in 2D subspaces; dot product depends on relative position |
| ALiBi simplicity | "Simplest way to add position info?" | Linear bias on attention scores; no embedding modification |
| Context extension | "How to extend context beyond training?" | NTK-aware RoPE scaling or YaRN; ALiBi extrapolates natively |

### Common Interview Questions
- [ ] Why does the original Transformer need position encoding?
- [ ] How does RoPE achieve relative position encoding through rotation?
- [ ] Compare RoPE, ALiBi, and sinusoidal for length extrapolation.
- [ ] Why do different RoPE dimensions encode different frequency scales?
- [ ] How would you extend a 4K-context model to 32K?

## Comparisons

| Aspect | Sinusoidal | Learned | RoPE | ALiBi |
|--------|-----------|---------|------|-------|
| Type | Absolute | Absolute | Relative | Relative |
| Parameters | 0 | $L \times d$ | 0 | 0 (fixed slopes) |
| Extrapolation | Limited | None | With scaling | Native |
| Used in | Original Transformer | BERT, GPT-2 | LLaMA, Mistral | BLOOM, MPT |

## Key Takeaways

- [ ] Position encoding is necessary because self-attention is permutation-equivariant
- [ ] RoPE: rotates Q/K so dot product depends on relative position; standard in modern LLMs
- [ ] ALiBi: bias on attention scores; simplest approach, best extrapolation
- [ ] NTK-aware scaling extends RoPE context without fine-tuning
- [ ] Learned absolute PE is limited by max training length
"""

CONTENT["pillar6.transformer.layer_normalization"] = r"""# Layer Normalization

## Overview
Layer normalization (LayerNorm) stabilizes training in deep Transformers by normalizing activations within each sample. Its placement (pre-norm vs post-norm) and variant (RMSNorm) significantly affect training dynamics and model quality.

## Core Concepts

### Layer Normalization
Normalizes across the feature dimension for each token independently:

$$
\text{LayerNorm}(x) = \gamma \odot \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} + \beta
$$

where $\mu = \frac{1}{d}\sum_{i=1}^{d} x_i$, $\sigma^2 = \frac{1}{d}\sum_{i=1}^{d}(x_i - \mu)^2$, and $\gamma, \beta \in \mathbb{R}^d$ are learned.

### Pre-Norm vs Post-Norm

**Post-Norm** (original Transformer):
$$
x_{l+1} = \text{LayerNorm}(x_l + \text{SubLayer}(x_l))
$$

**Pre-Norm** (GPT-2, LLaMA):
$$
x_{l+1} = x_l + \text{SubLayer}(\text{LayerNorm}(x_l))
$$

Key differences:
- Pre-norm: gradient flows through residual stream unimpeded; trains more stably without warmup
- Post-norm: better final quality at convergence but requires careful learning rate warmup
- Pre-norm is standard in modern LLMs due to training stability at scale

### RMSNorm (Root Mean Square Normalization)
Simplification of LayerNorm that removes the mean-centering step:

$$
\text{RMSNorm}(x) = \gamma \odot \frac{x}{\text{RMS}(x) + \epsilon}, \quad \text{RMS}(x) = \sqrt{\frac{1}{d}\sum_{i=1}^{d} x_i^2}
$$

- Used in LLaMA, Mistral, Gemma
- 10-15% faster than full LayerNorm (no mean computation)
- Empirically equivalent quality to LayerNorm

### Why Not BatchNorm?
Batch normalization normalizes across the batch dimension -- problematic for:
- Variable-length sequences (padding affects statistics)
- Autoregressive generation (batch size = 1 at inference)
- Distributed training with small per-device batches

## Implementation

```python
import numpy as np

def layer_norm(x, gamma, beta, eps=1e-5):
    # Standard LayerNorm.
    mu = x.mean(axis=-1, keepdims=True)
    var = x.var(axis=-1, keepdims=True)
    return gamma * (x - mu) / np.sqrt(var + eps) + beta

def rms_norm(x, gamma, eps=1e-5):
    # RMSNorm (no mean centering).
    rms = np.sqrt((x ** 2).mean(axis=-1, keepdims=True) + eps)
    return gamma * x / rms
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Pre vs post norm | "Training stability" | Pre-norm allows clean gradient flow; standard in modern LLMs |
| RMSNorm choice | "Why RMSNorm over LayerNorm?" | Faster (no mean), same quality; used in LLaMA/Mistral |
| LayerNorm vs BatchNorm | "Why not BatchNorm in Transformers?" | Variable lengths, small batches, autoregressive generation |
| Gradient flow analysis | "Why do deep Transformers train?" | Residual + pre-norm keeps gradient magnitude stable across layers |

### Common Interview Questions
- [ ] What is the difference between LayerNorm and BatchNorm?
- [ ] Why is pre-norm preferred for training large language models?
- [ ] How does RMSNorm differ from LayerNorm and why is it used?
- [ ] Explain how pre-norm affects gradient flow in deep networks.
- [ ] Where exactly is LayerNorm placed in GPT-style models?

## Comparisons

| Aspect | LayerNorm | RMSNorm | BatchNorm |
|--------|----------|---------|-----------|
| Normalization axis | Feature (per token) | Feature (per token) | Batch (across samples) |
| Parameters | $2d$ ($\gamma, \beta$) | $d$ ($\gamma$ only) | $2d$ + running stats |
| Mean centering | Yes | No | Yes |
| Inference behavior | Same as training | Same as training | Uses running statistics |
| Used in | GPT-2, BERT | LLaMA, Mistral | CNNs, ResNets |

## Key Takeaways

- [ ] LayerNorm normalizes per-token across features; essential for Transformer stability
- [ ] Pre-norm (LN before sublayer) is standard in modern LLMs for stable training
- [ ] RMSNorm drops mean centering for speed; empirically equivalent to LayerNorm
- [ ] BatchNorm is unsuitable for Transformers due to variable lengths and small batches
- [ ] Learned scale ($\gamma$) and shift ($\beta$) restore representational capacity
"""

CONTENT["pillar6.transformer.feed_forward"] = r"""# Feed-Forward Networks (SwiGLU)

## Overview
The feed-forward network (FFN) in each Transformer block is a position-wise MLP that transforms each token independently. Modern LLMs use gated variants like SwiGLU that outperform the original ReLU FFN. The FFN contains the majority of model parameters.

## Core Concepts

### Standard FFN (ReLU)
The original Transformer uses a two-layer MLP with ReLU:

$$
\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2
$$

where $W_1 \in \mathbb{R}^{d \times d_{ff}}$, $W_2 \in \mathbb{R}^{d_{ff} \times d}$, typically $d_{ff} = 4d$.

### Gated Linear Units (GLU)
Dauphin et al. proposed gating the linear transform:

$$
\text{GLU}(x) = (xW_1) \odot \sigma(xW_{\text{gate}})
$$

where $\sigma$ is sigmoid and $\odot$ is element-wise multiplication.

### SwiGLU (Used in LLaMA, PaLM)
Replaces ReLU with Swish-gated variant:

$$
\text{SwiGLU}(x) = (\text{Swish}(xW_{\text{gate}})) \odot (xW_1)
$$

$$
\text{Swish}(x) = x \cdot \sigma(\beta x), \quad \text{typically } \beta = 1 \text{ (SiLU)}
$$

Full FFN with SwiGLU:

$$
\text{FFN}(x) = (\text{SiLU}(xW_{\text{gate}}) \odot xW_1)W_2
$$

Note: SwiGLU has 3 weight matrices ($W_1, W_{\text{gate}}, W_2$) vs 2 for standard FFN. To keep param count similar, $d_{ff}$ is reduced (e.g., $d_{ff} = \frac{8d}{3}$ rounded to multiple of 256).

### FFN as Key-Value Memory
Geva et al. (2021) showed FFN layers act as key-value memories:
- $W_1$ rows are "keys" (patterns to match)
- $W_2$ columns are "values" (information to retrieve)
- ReLU/SwiGLU acts as sparse gating, activating relevant memories

### Parameter Distribution
For a standard Transformer block with dim $d$:
- Attention: $4d^2$ (Q, K, V, O projections)
- FFN (standard): $2 \times d \times 4d = 8d^2$
- FFN (SwiGLU, $d_{ff} = 8d/3$): $3 \times d \times 8d/3 = 8d^2$
- FFN accounts for ~67% of each block's parameters

## Implementation

```python
import numpy as np

def relu_ffn(x, W1, b1, W2, b2):
    # Standard Transformer FFN.
    return np.maximum(0, x @ W1 + b1) @ W2 + b2

def swiglu_ffn(x, W_gate, W1, W2):
    # SwiGLU FFN (LLaMA-style, no bias).
    gate = x @ W_gate
    silu_gate = gate * (1 / (1 + np.exp(-gate)))  # SiLU
    return (silu_gate * (x @ W1)) @ W2
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SwiGLU advantage | "Why not plain ReLU FFN?" | Gating allows selective information flow; empirically better |
| FFN as memory | "What do FFN layers store?" | Key-value memory interpretation; factual knowledge storage |
| Param count | "Where are most Transformer params?" | FFN has ~2/3 of block parameters |
| $d_{ff}$ sizing | "Why $8d/3$ in LLaMA?" | Keeps total params same as $4d$ ReLU FFN despite 3 matrices |

### Common Interview Questions
- [ ] Why does SwiGLU outperform ReLU in FFN layers?
- [ ] What fraction of Transformer parameters are in the FFN?
- [ ] How does the FFN-as-memory interpretation relate to model editing?
- [ ] Why is there no bias in LLaMA's FFN layers?
- [ ] Compare GeLU, SwiGLU, and ReLU for Transformer FFNs.

## Comparisons

| Aspect | ReLU FFN | GeLU FFN | SwiGLU FFN |
|--------|---------|---------|------------|
| Activation | $\max(0, x)$ | $x\Phi(x)$ | $x\sigma(x) \odot \text{linear}$ |
| Weight matrices | 2 | 2 | 3 |
| $d_{ff}$ for same params | $4d$ | $4d$ | $8d/3$ |
| Quality | Baseline | Better | Best |
| Used in | Original Transformer | GPT-2, BERT | LLaMA, PaLM, Mistral |

## Key Takeaways

- [ ] FFN is a position-wise MLP applied independently per token
- [ ] SwiGLU (gated SiLU) is the standard in modern LLMs; empirically superior to ReLU
- [ ] FFN has ~67% of block parameters and acts as a key-value memory
- [ ] $d_{ff}$ is adjusted (typically $8d/3$) in SwiGLU to match ReLU param count
- [ ] No biases in modern LLMs (LLaMA, Mistral) for simplicity and efficiency
"""

CONTENT["pillar6.transformer.attention_variants"] = r"""# Attention Variants (MQA, GQA, Flash Attention)

## Overview
Standard multi-head attention (MHA) has quadratic memory/compute cost and large KV cache requirements. Modern variants address both: Multi-Query Attention (MQA) and Grouped-Query Attention (GQA) reduce KV cache, while Flash Attention reduces memory via tiling. Understanding these is critical for LLM system design.

## Core Concepts

### Multi-Query Attention (MQA)
Shazeer (2019): all heads share a single set of K and V projections.

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW^K, VW^V)
$$

- KV cache reduced by $h\times$ (e.g., $32\times$ for LLaMA-7B)
- Slight quality degradation vs MHA
- Used in PaLM, Falcon

### Grouped-Query Attention (GQA)
Ainslie et al. (2023): intermediate between MHA and MQA. Heads are divided into $g$ groups; each group shares K/V.

$$
\text{head}_i = \text{Attention}(QW_i^Q, KW_{\lfloor i \cdot g/h \rfloor}^K, VW_{\lfloor i \cdot g/h \rfloor}^V)
$$

- $g = h$: equivalent to MHA
- $g = 1$: equivalent to MQA
- Typical: $g = 8$ with $h = 32$ (LLaMA 2 70B, Mistral)
- Near-MHA quality with significant KV cache savings

### Flash Attention (Dao et al., 2022)
IO-aware exact attention algorithm that avoids materializing the full $n \times n$ attention matrix:

**Key idea**: Tile the Q, K, V matrices into blocks that fit in SRAM (fast on-chip memory), compute partial softmax in tiles, accumulate results.

**Online softmax trick**:

$$
m_{\text{new}} = \max(m_{\text{old}}, \max(S_{\text{block}}))
$$

$$
\ell_{\text{new}} = e^{m_{\text{old}} - m_{\text{new}}} \cdot \ell_{\text{old}} + \sum e^{S_{\text{block}} - m_{\text{new}}}
$$

Performance:
- Memory: $O(n)$ instead of $O(n^2)$ (no materialized attention matrix)
- Speed: 2-4x faster due to reduced HBM reads/writes
- Exact (not approximate) -- numerically identical to standard attention
- Flash Attention 2: further 2x speedup via better parallelism and work partitioning

### Sliding Window Attention
Used in Mistral: each token attends only to a local window of size $W$:

$$
A_{ij} = \begin{cases} \frac{q_i \cdot k_j}{\sqrt{d_k}} & \text{if } |i - j| \leq W \\ -\infty & \text{otherwise} \end{cases}
$$

- Reduces complexity to $O(nW)$
- With $L$ layers and window $W$, effective receptive field is $L \times W$
- Combined with GQA in Mistral 7B

### Multi-Latent Attention (MLA)
Used in DeepSeek-V2: compresses KV into a low-rank latent space:

$$
c_t = W^{DKV} h_t, \quad K = W^{UK} c_t, \quad V = W^{UV} c_t
$$

- Caches only the compressed $c_t$ (much smaller than full K/V)
- Maintains quality via joint compression of K and V

## Implementation

```python
import numpy as np

def grouped_query_attention(Q, K, V, n_heads, n_kv_groups):
    # GQA: Q has n_heads, K/V have n_kv_groups.
    heads_per_group = n_heads // n_kv_groups
    outputs = []
    for g in range(n_kv_groups):
        k_g, v_g = K[g], V[g]
        for h in range(heads_per_group):
            q_h = Q[g * heads_per_group + h]
            d_k = q_h.shape[-1]
            scores = q_h @ k_g.T / np.sqrt(d_k)
            w = np.exp(scores - scores.max(-1, keepdims=True))
            w /= w.sum(-1, keepdims=True)
            outputs.append(w @ v_g)
    return np.concatenate(outputs, axis=-1)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| KV cache sizing | "How to reduce inference memory?" | MQA/GQA reduce KV cache by $h/g$ factor |
| Flash Attention | "How to handle long sequences?" | IO-aware tiling; $O(n)$ memory, exact computation |
| GQA trade-off | "Balance quality vs efficiency" | $g$ groups: knob between MHA quality and MQA speed |
| Sliding window | "Local attention approaches" | $O(nW)$ per layer; $L \times W$ effective receptive field |

### Common Interview Questions
- [ ] How does GQA interpolate between MHA and MQA?
- [ ] Why is Flash Attention faster despite doing the same FLOPs?
- [ ] What is the KV cache memory for a 70B model with GQA ($g=8$)?
- [ ] How does sliding window attention achieve long-range dependency with local windows?
- [ ] Compare the memory vs quality trade-offs of MQA, GQA, and MLA.

## Comparisons

| Aspect | MHA | MQA | GQA | Flash Attention |
|--------|-----|-----|-----|----------------|
| KV heads | $h$ | 1 | $g$ ($1 < g < h$) | N/A (orthogonal) |
| KV cache | $2nhd_k$ | $2nd_k$ | $2ngd_k$ | No change |
| Quality | Best | Slight drop | Near MHA | Identical to MHA |
| Training change | Baseline | Need retraining | Uptraining works | Drop-in replacement |
| Inference speed | Baseline | Fastest | Fast | 2-4x faster |

## Key Takeaways

- [ ] MQA shares K/V across all heads; GQA shares within groups -- both reduce KV cache
- [ ] Flash Attention: IO-aware tiling gives $O(n)$ memory and 2-4x speedup, exact results
- [ ] GQA with $g=8$ is the sweet spot for modern LLMs (LLaMA 2 70B, Mistral)
- [ ] Sliding window attention: $O(nW)$ complexity, $L \times W$ effective receptive field
- [ ] These optimizations are orthogonal and combinable: GQA + Flash + sliding window
"""

CONTENT["pillar6.transformer.architecture_variants"] = r"""# Architecture Variants (Encoder/Decoder)

## Overview
Transformers come in three main architectures: encoder-only (BERT), decoder-only (GPT), and encoder-decoder (T5). The choice impacts pre-training objectives, task suitability, and inference patterns. Modern LLMs have converged on decoder-only, but understanding all variants is important for MLE interviews.

## Core Concepts

### Encoder-Only (BERT-style)
- **Attention**: Bidirectional -- each token attends to all tokens
- **Pre-training**: Masked Language Modeling (MLM) -- predict masked tokens from context
- **Architecture**: Stack of Transformer blocks with bidirectional attention

$$
P(x_{\text{mask}} | x_{\backslash \text{mask}}) = \text{softmax}(hW_e^T)
$$

- Best for: classification, NER, semantic similarity, retrieval
- Examples: BERT, RoBERTa, DeBERTa, ELECTRA

### Decoder-Only (GPT-style)
- **Attention**: Causal (unidirectional) -- each token only attends to previous tokens
- **Pre-training**: Next-token prediction (autoregressive language modeling)

$$
P(x_1, \ldots, x_n) = \prod_{t=1}^{n} P(x_t | x_{<t})
$$

- **KV cache**: During generation, reuse computed keys/values for previous tokens
- Best for: text generation, in-context learning, instruction following
- Examples: GPT-2/3/4, LLaMA, Mistral, Claude

### Encoder-Decoder (T5-style)
- **Encoder**: Bidirectional attention over input
- **Decoder**: Causal attention over output + cross-attention to encoder
- **Pre-training**: Span corruption -- mask spans, predict them

**Cross-attention** in decoder layers:

$$
\text{CrossAttention}(Q_{\text{dec}}, K_{\text{enc}}, V_{\text{enc}})
$$

- Best for: translation, summarization, structured generation
- Examples: T5, BART, Flan-T5, mBART

### Why Decoder-Only Dominates
1. **Simpler architecture**: one model for all tasks via prompting
2. **Scaling efficiency**: more parameters in a unified model vs split encoder/decoder
3. **In-context learning**: emergent with scale; encoder-only cannot generate
4. **KV cache**: efficient autoregressive generation
5. **Training efficiency**: every token is a training signal (vs only masked tokens in BERT)

### Prefix LM
Hybrid approach: bidirectional attention over a prefix, causal over the rest.

$$
\text{Attention mask} = \begin{cases} \text{bidirectional} & i \leq p \text{ (prefix)} \\ \text{causal} & i > p \text{ (generation)} \end{cases}
$$

Used in PaLM, U-PaLM. Combines encoder-like understanding with decoder-like generation.

## Implementation

```python
import numpy as np

def create_attention_mask(seq_len, mask_type="causal"):
    # Create attention mask for different architectures.
    if mask_type == "bidirectional":  # Encoder (BERT)
        return np.zeros((seq_len, seq_len))
    elif mask_type == "causal":  # Decoder (GPT)
        mask = np.full((seq_len, seq_len), -1e9)
        return np.triu(mask, k=1)
    elif mask_type == "prefix":  # Prefix LM
        prefix_len = seq_len // 2
        mask = np.full((seq_len, seq_len), -1e9)
        mask = np.triu(mask, k=1)
        mask[:prefix_len, :prefix_len] = 0  # bidirectional prefix
        return mask
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Architecture selection | "Which Transformer for this task?" | Encoder: understanding. Decoder: generation. Enc-Dec: seq2seq |
| Why decoder-only | "Why do all LLMs use decoder-only?" | Scaling efficiency, ICL emergence, simpler serving |
| MLM vs CLM training | "Compare BERT and GPT training" | MLM: 15% of tokens. CLM: 100% of tokens as training signal |
| Cross-attention | "How does encoder-decoder work?" | Decoder attends to encoder hidden states via cross-attention |

### Common Interview Questions
- [ ] Why has the field converged on decoder-only for large models?
- [ ] When would you still choose an encoder-only or encoder-decoder model?
- [ ] What is the computational difference between MLM and CLM pre-training?
- [ ] How does cross-attention differ from self-attention?
- [ ] Explain the prefix LM approach and its advantages.

## Comparisons

| Aspect | Encoder-Only | Decoder-Only | Encoder-Decoder |
|--------|-------------|-------------|-----------------|
| Attention | Bidirectional | Causal | Bi (enc) + Causal (dec) + Cross |
| Pre-training | MLM | Next-token | Span corruption |
| Token efficiency | ~15% (masked only) | 100% | ~15% (corrupted spans) |
| Generation | Not native | Native | Native |
| Examples | BERT, RoBERTa | GPT, LLaMA | T5, BART |
| Best for | Classification, retrieval | Generation, ICL | Translation, summarization |

## Key Takeaways

- [ ] Three architectures: encoder-only (bidirectional), decoder-only (causal), encoder-decoder (both)
- [ ] Decoder-only dominates LLMs: simpler, scales better, ICL emerges with scale
- [ ] Encoder-only still best for retrieval/embeddings (sentence-transformers)
- [ ] CLM trains on 100% of tokens vs MLM's ~15%, making decoder-only more data-efficient
- [ ] Cross-attention in encoder-decoder allows decoder to "read" the encoded input
"""

# ===== PRE-TRAINED LANGUAGE MODELS =====

CONTENT["pillar6.pretrained_lm.bert_family"] = r"""# BERT Family

## Overview
BERT (Bidirectional Encoder Representations from Transformers) revolutionized NLP by introducing bidirectional pre-training via masked language modeling. The BERT family -- including RoBERTa, DeBERTa, ELECTRA, and DistilBERT -- remains the workhorse for classification, NER, retrieval, and embedding tasks in production.

## Core Concepts

### BERT Pre-training Objectives

**Masked Language Modeling (MLM)**:
- Randomly mask 15% of tokens: 80% [MASK], 10% random, 10% unchanged
- Predict original token from bidirectional context

$$
\mathcal{L}_{\text{MLM}} = -\sum_{i \in \text{masked}} \log P(x_i | x_{\backslash i})
$$

**Next Sentence Prediction (NSP)**:
- Binary classification: is sentence B the actual next sentence?
- Later shown to be unhelpful (RoBERTa removes it)

### BERT Architecture Details
- BERT-base: $L=12, d=768, h=12$, 110M params
- BERT-large: $L=24, d=1024, h=16$, 340M params
- WordPiece tokenizer with 30K vocab
- Learned absolute position embeddings (max 512 tokens)
- Input: [CLS] + tokens_A + [SEP] + tokens_B + [SEP]

### RoBERTa (Robustly Optimized BERT)
Key improvements over BERT:
- Remove NSP objective (train on single sentences)
- Larger batches (8K), more data (160GB), longer training
- Dynamic masking (new mask each epoch vs static)
- BPE tokenizer (50K vocab)
- Result: significant gains across all tasks

### DeBERTa (Decoupled Attention)
- Disentangled attention: separate content and position embeddings in attention

$$
A_{ij} = \{H_i^c, H_j^c\} + \{H_i^c, P_{j|i}\} + \{P_{i|j}, H_j^c\}
$$

- Enhanced mask decoder: absolute position in final layer only
- State-of-the-art on SuperGLUE; DeBERTa-v3 uses ELECTRA-style training

### ELECTRA
Replaced Token Detection (RTD) instead of MLM:
1. Small generator produces replacements for masked tokens
2. Discriminator classifies each token as original or replaced

$$
\mathcal{L}_{\text{RTD}} = -\sum_{i=1}^{n} \left[y_i \log D(x_i) + (1-y_i)\log(1-D(x_i))\right]
$$

- Trains on ALL tokens (not just 15% masked) -- more sample efficient
- Small ELECTRA matches BERT-large quality

### DistilBERT (Knowledge Distillation)
- 6 layers (half of BERT-base), 66M params
- Trained with soft-label distillation from BERT-base
- 97% of BERT performance at 60% size and 2x speed

## Implementation

```python
# Fine-tuning BERT for classification (HuggingFace)
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained(
    "microsoft/deberta-v3-base", num_labels=2
)
tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-base")

# For sentence embeddings (retrieval)
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(["query text", "document text"])
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| BERT vs GPT | "When to use encoder vs decoder?" | BERT for understanding tasks; GPT for generation |
| Model selection | "Which BERT variant?" | DeBERTa-v3 for quality; DistilBERT for latency; ELECTRA for efficiency |
| MLM design choices | "Why 80/10/10 masking?" | [MASK] never seen at fine-tune time; mixing reduces mismatch |
| ELECTRA efficiency | "Most sample-efficient pre-training?" | Trains discriminator on ALL tokens, not just masked 15% |

### Common Interview Questions
- [ ] What problem does BERT's [MASK] token mismatch cause at fine-tuning?
- [ ] Why did RoBERTa remove Next Sentence Prediction?
- [ ] How does ELECTRA achieve better sample efficiency than MLM?
- [ ] When would you use BERT-family vs decoder-only models in production?
- [ ] Compare DeBERTa's disentangled attention to standard attention.

## Comparisons

| Aspect | BERT | RoBERTa | DeBERTa | ELECTRA | DistilBERT |
|--------|------|---------|---------|---------|------------|
| Objective | MLM + NSP | MLM only | MLM | RTD | Distillation |
| Token efficiency | 15% | 15% | 15% | 100% | N/A |
| Size (base) | 110M | 125M | 184M | 110M | 66M |
| Relative PE | No | No | Yes (disentangled) | No | No |
| Best for | General | General (better) | Quality | Efficiency | Speed |

## Key Takeaways

- [ ] BERT = bidirectional encoder with MLM; foundation for NLU tasks
- [ ] RoBERTa: remove NSP, more data, dynamic masking -- strictly better BERT
- [ ] DeBERTa: disentangled attention for position; current SoTA encoder
- [ ] ELECTRA: discriminator on all tokens; most sample-efficient pre-training
- [ ] BERT-family is still best for embeddings, classification, NER in production
"""

CONTENT["pillar6.pretrained_lm.gpt_family"] = r"""# GPT Family

## Overview
The GPT (Generative Pre-trained Transformer) family pioneered decoder-only autoregressive language models. From GPT-1 to GPT-4, the series demonstrated that scaling model size, data, and compute yields emergent capabilities like in-context learning, chain-of-thought reasoning, and instruction following.

## Core Concepts

### Autoregressive Language Modeling
All GPT models are trained with next-token prediction:

$$
\mathcal{L} = -\sum_{t=1}^{n} \log P(x_t | x_{<t}; \theta)
$$

Each token is predicted conditioned on all previous tokens via causal (masked) self-attention.

### GPT Model Evolution

| Model | Year | Params | Context | Key Innovation |
|-------|------|--------|---------|----------------|
| GPT-1 | 2018 | 117M | 512 | Pre-train + fine-tune paradigm |
| GPT-2 | 2019 | 1.5B | 1024 | Zero-shot task transfer via prompting |
| GPT-3 | 2020 | 175B | 2048 | In-context learning, few-shot prompting |
| GPT-4 | 2023 | ~1.8T (MoE) | 128K | Multimodal, RLHF, instruction following |

### In-Context Learning (ICL)
Emergent ability at scale: GPT-3+ can perform tasks by conditioning on examples in the prompt:

$$
P(y|x, \text{examples}) \approx P(y | \text{demo}_1, \ldots, \text{demo}_k, x)
$$

- Zero-shot: task description only
- Few-shot: $k$ input-output examples in context
- No gradient updates -- pure inference-time adaptation

### Scaling Laws (Kaplan et al., 2020)
Performance follows power laws with compute $C$, data $D$, and parameters $N$:

$$
L(N) \approx \left(\frac{N_c}{N}\right)^{\alpha_N}, \quad L(D) \approx \left(\frac{D_c}{D}\right)^{\alpha_D}
$$

Key findings:
- Loss scales smoothly as a power law with model size and data
- Larger models are more sample-efficient
- Optimal allocation: scale $N$ and $D$ together (Chinchilla: $D \approx 20N$)

### Chinchilla Scaling (Hoffmann et al., 2022)
Revised scaling: for fixed compute budget, balance model size and data:

$$
N_{\text{opt}} \propto C^{0.5}, \quad D_{\text{opt}} \propto C^{0.5}
$$

GPT-3 (175B, 300B tokens) was undertrained; Chinchilla (70B, 1.4T tokens) matches it.

### GPT Architecture Details (GPT-2/3)
- Pre-norm (LayerNorm before attention and FFN)
- Learned absolute position embeddings
- No encoder, no cross-attention
- Dense attention (all heads, full sequence)
- Tokenizer: BPE with ~50K vocab

## Implementation

```python
# Using GPT-style models for generation
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# In-context learning example
prompt = '''Classify the sentiment:
Text: "Great movie!" -> Positive
Text: "Terrible service" -> Negative
Text: "The food was amazing" ->'''
inputs = tokenizer(prompt, return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=5)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Scaling laws | "How to allocate compute budget?" | Chinchilla: $D \approx 20N$ tokens for compute-optimal training |
| ICL mechanism | "How does few-shot work?" | Implicit Bayesian inference over pre-training distribution |
| GPT vs BERT | "When to use which?" | GPT: generation, reasoning. BERT: classification, retrieval |
| Emergent abilities | "What changes with scale?" | ICL, CoT reasoning, instruction following appear at ~100B+ |

### Common Interview Questions
- [ ] What are scaling laws and why do they matter for LLM development?
- [ ] How does in-context learning work mechanically in a Transformer?
- [ ] Why was GPT-3 considered compute-suboptimal by Chinchilla standards?
- [ ] What is the difference between zero-shot, few-shot, and fine-tuned performance?
- [ ] How does GPT-4's MoE architecture differ from dense GPT-3?

## Comparisons

| Aspect | GPT-2 | GPT-3 | LLaMA 2 | GPT-4 |
|--------|-------|-------|---------|-------|
| Parameters | 1.5B | 175B | 7-70B | ~1.8T (MoE) |
| Training tokens | 40B | 300B | 2T | ~13T |
| Context length | 1024 | 2048 | 4096 | 128K |
| Open weights | Yes | No | Yes | No |
| Architecture | Dense | Dense | Dense | MoE |

## Key Takeaways

- [ ] GPT family: decoder-only autoregressive LMs trained on next-token prediction
- [ ] Scaling laws: loss follows power laws with $N$, $D$, $C$; Chinchilla ratio $D \approx 20N$
- [ ] In-context learning: emergent at scale; no gradient updates, pure conditioning
- [ ] GPT-4 is likely MoE (~1.8T total, ~220B active per token)
- [ ] Open alternatives (LLaMA, Mistral) match GPT-3.5 quality with fewer parameters
"""

CONTENT["pillar6.pretrained_lm.llama_mistral"] = r"""# LLaMA / Mistral Open-Source LLMs

## Overview
LLaMA (Meta) and Mistral represent the state-of-the-art in open-weight LLMs. They incorporate architectural improvements (RoPE, GQA, SwiGLU, RMSNorm) that make them more efficient than GPT-3 while achieving comparable or better quality. Understanding their design choices is essential for any MLE building LLM-based systems.

## Core Concepts

### LLaMA Architecture (Meta, 2023)
Key design choices vs original Transformer:
- **RMSNorm** instead of LayerNorm (faster, no mean centering)
- **SwiGLU activation** instead of ReLU in FFN ($d_{ff} = 8d/3$)
- **RoPE** instead of learned position embeddings
- **Pre-norm** (normalize before attention/FFN)
- **No bias** in linear layers
- **GQA** (LLaMA 2 70B): 8 KV heads for 64 query heads

### LLaMA Model Sizes

| Model | Layers | $d$ | Heads | KV Heads | Params | Training Tokens |
|-------|--------|-----|-------|----------|--------|----------------|
| LLaMA 2 7B | 32 | 4096 | 32 | 32 (MHA) | 7B | 2T |
| LLaMA 2 13B | 40 | 5120 | 40 | 40 (MHA) | 13B | 2T |
| LLaMA 2 70B | 80 | 8192 | 64 | 8 (GQA) | 70B | 2T |
| LLaMA 3 8B | 32 | 4096 | 32 | 8 (GQA) | 8B | 15T |
| LLaMA 3 70B | 80 | 8192 | 64 | 8 (GQA) | 70B | 15T |

### Mistral Architecture
Mistral 7B innovations:
- **Sliding Window Attention**: window size $W = 4096$; effective context $L \times W$
- **GQA**: 8 KV heads for 32 query heads
- **Rolling buffer KV cache**: fixed cache size $W$, older entries overwritten
- **Pre-fill and chunking**: process prompt in chunks for memory efficiency

Mixtral 8x7B (MoE):
- 8 expert FFNs per layer, top-2 routing
- Total params: 46.7B; active params per token: ~13B
- Router: $G(x) = \text{TopK}(\text{softmax}(xW_g), k=2)$

### Tokenization
- LLaMA: SentencePiece BPE, 32K vocab
- LLaMA 3: tiktoken-based, 128K vocab (better multilingual, code)
- Mistral: SentencePiece BPE, 32K vocab

### Training Details
- Optimizer: AdamW ($\beta_1=0.9, \beta_2=0.95$)
- Cosine learning rate schedule with warmup
- Weight decay: 0.1
- Context length: 4096 (LLaMA 2), extended to 8K-128K with RoPE scaling
- BF16 mixed precision training
- Data: CommonCrawl, Wikipedia, Books, Code, ArXiv, StackExchange

### LLaMA 2 Chat (Instruction Tuning)
Pipeline:
1. Pre-training on 2T tokens
2. Supervised Fine-Tuning (SFT) on instruction data
3. RLHF with reward model and PPO
4. Ghost Attention (GAtt) for multi-turn system prompt adherence

## Implementation

```python
# Loading and running LLaMA/Mistral
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "mistralai/Mistral-7B-Instruct-v0.2"
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Mistral chat template
messages = [{"role": "user", "content": "Explain attention."}]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")
output = model.generate(inputs, max_new_tokens=256)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Architecture comparison | "Compare LLaMA to GPT-3" | RoPE + GQA + SwiGLU + RMSNorm = more efficient |
| Open vs closed | "Build with open or closed models?" | Open: controllable, fine-tunable, no API dependency |
| MoE trade-offs | "Mixtral vs dense model?" | More params per FLOP, but routing complexity and load balancing |
| Context extension | "How to get 128K context?" | RoPE NTK scaling + continued pre-training on long sequences |

### Common Interview Questions
- [ ] What architectural improvements does LLaMA have over GPT-3?
- [ ] Why does LLaMA 2 70B use GQA but 7B/13B use MHA?
- [ ] How does Mistral's sliding window attention work?
- [ ] What is the Mixtral MoE routing mechanism?
- [ ] How would you extend LLaMA 2's 4K context to 32K?

## Comparisons

| Aspect | LLaMA 2 7B | Mistral 7B | Mixtral 8x7B | LLaMA 3 8B |
|--------|-----------|-----------|-------------|-----------|
| Attention | MHA | GQA + sliding window | GQA + sliding window | GQA |
| Position | RoPE | RoPE | RoPE | RoPE |
| FFN | SwiGLU | SwiGLU | MoE (8 experts, top-2) | SwiGLU |
| Norm | RMSNorm | RMSNorm | RMSNorm | RMSNorm |
| Vocab | 32K | 32K | 32K | 128K |
| Training data | 2T tokens | Unknown | Unknown | 15T tokens |

## Key Takeaways

- [ ] LLaMA/Mistral are the open-weight standard: RoPE + GQA + SwiGLU + RMSNorm
- [ ] GQA is used in larger models (70B) to reduce KV cache; smaller models may use full MHA
- [ ] Mistral adds sliding window attention for efficient long-context handling
- [ ] Mixtral 8x7B: MoE with top-2 routing; 46.7B total, ~13B active per token
- [ ] LLaMA 3 trained on 15T tokens with 128K vocab -- data scale matters enormously
"""

# ===== LLM TRAINING & ALIGNMENT =====

CONTENT["pillar6.llm_training_alignment.pretraining"] = r"""# Pre-training

## Overview
Pre-training is the foundational phase where LLMs learn language representations from massive unlabeled corpora. It determines model capabilities, and the compute budget (often $10^{23}$-$10^{25}$ FLOPs) dominates total cost. Understanding pre-training choices -- data, objectives, optimization, and infrastructure -- is critical for senior MLE roles.

## Core Concepts

### Pre-training Objectives

**Causal Language Modeling (CLM)**: Standard for decoder-only models.

$$
\mathcal{L}_{\text{CLM}} = -\sum_{t=1}^{n} \log P(x_t | x_{<t}; \theta)
$$

**Masked Language Modeling (MLM)**: Used for encoder models (BERT).

$$
\mathcal{L}_{\text{MLM}} = -\sum_{i \in \mathcal{M}} \log P(x_i | x_{\backslash \mathcal{M}}; \theta)
$$

**Span Corruption**: T5-style; replace random spans with sentinel tokens.

**Fill-in-the-Middle (FIM)**: Used in code models (Codex, StarCoder):
Split document into prefix, middle, suffix; train on PSM or SPM orderings.

### Training Compute Estimation
For a Transformer with $N$ parameters, processing $D$ tokens:

$$
C \approx 6ND \text{ FLOPs (forward + backward)}
$$

For LLaMA 2 70B on 2T tokens: $C \approx 6 \times 70 \times 10^9 \times 2 \times 10^{12} = 8.4 \times 10^{23}$ FLOPs.

### Data Pipeline
1. **Collection**: CommonCrawl, Wikipedia, Books, Code, ArXiv
2. **Deduplication**: MinHash + LSH for near-duplicate removal (reduces memorization)
3. **Filtering**: Perplexity filtering (remove low-quality), toxicity filtering
4. **Mixing**: Carefully tuned domain proportions (e.g., 67% web, 4.5% code, 4.5% Wikipedia)
5. **Tokenization**: BPE (GPT), SentencePiece (LLaMA), tiktoken (LLaMA 3)

### Data Quality vs Quantity
- Chinchilla: train for longer on more data, not just bigger models
- Data quality filtering yields 2-3x effective data multiplier
- Repeat high-quality data (up to 4 epochs) is better than adding low-quality data
- Textbook-quality data (Phi models) enables surprisingly strong small models

### Optimization

**Optimizer**: AdamW with $\beta_1 = 0.9, \beta_2 = 0.95, \epsilon = 10^{-8}$

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2
$$

$$
\theta_t = \theta_{t-1} - \eta \left(\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} + \lambda \theta_{t-1}\right)
$$

**Learning rate schedule**: Linear warmup (2K steps) + cosine decay to $\eta_{\min} = 0.1 \eta_{\max}$.

**Weight decay**: 0.1 (decoupled from Adam update).

### Distributed Training
- **Data Parallelism (DP)**: replicate model across GPUs, split batches
- **Tensor Parallelism (TP)**: split individual layers across GPUs
- **Pipeline Parallelism (PP)**: split layers across GPU groups
- **FSDP / ZeRO**: shard optimizer states, gradients, and parameters
- **3D Parallelism**: combine TP + PP + DP for largest models

## Implementation

```python
# Compute-optimal model sizing (Chinchilla)
def chinchilla_optimal(compute_budget_flops):
    # Given compute C, find optimal N and D.
    # C = 6 * N * D, with N ~ D^1.0
    N = (compute_budget_flops / 6) ** 0.5  # params
    D = (compute_budget_flops / 6) ** 0.5  # tokens
    return int(N), int(D)

# Example: 10^22 FLOPs -> ~1.3B params, ~1.3T tokens
# (adjusted by Chinchilla ratio: D ~= 20 * N)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Compute budget allocation | "How to size a model?" | Chinchilla: $D \approx 20N$; balance params and data |
| Data quality | "What matters most in pre-training?" | Quality > quantity; dedup and filtering are critical |
| Training infrastructure | "How do you train a 70B model?" | 3D parallelism: TP within node, PP across nodes, DP for batch |
| Loss spikes | "What goes wrong during pre-training?" | Learning rate too high, data corruption, numerical instability |

### Common Interview Questions
- [ ] How do you estimate the compute required to pre-train a model?
- [ ] What is the Chinchilla-optimal ratio of parameters to data?
- [ ] Why is data deduplication important for pre-training?
- [ ] Describe the 3D parallelism strategy for training large models.
- [ ] How do you handle loss spikes during pre-training?

## Comparisons

| Aspect | CLM (GPT) | MLM (BERT) | Span Corruption (T5) |
|--------|----------|-----------|---------------------|
| Token utilization | 100% | ~15% | ~15% of spans |
| Bidirectional | No | Yes | Encoder: yes |
| Generation | Native | Not native | Native (decoder) |
| Use case | LLMs | Encoders | Seq2seq |

## Key Takeaways

- [ ] Pre-training cost: $C \approx 6ND$ FLOPs; dominates total training budget
- [ ] Chinchilla scaling: $D \approx 20N$ for compute-optimal training
- [ ] Data quality (dedup, filtering) matters more than raw quantity
- [ ] 3D parallelism (TP + PP + DP/FSDP) enables training at scale
- [ ] Cosine LR schedule with warmup is the standard; weight decay = 0.1
"""

CONTENT["pillar6.llm_training_alignment.sft"] = r"""# Supervised Fine-Tuning (SFT)

## Overview
Supervised Fine-Tuning transforms a pre-trained base model into an instruction-following assistant by training on curated (instruction, response) pairs. SFT is the bridge between raw language modeling capability and usable AI assistants. Quality of SFT data matters far more than quantity.

## Core Concepts

### SFT Objective
Same as CLM, but only compute loss on the response tokens:

$$
\mathcal{L}_{\text{SFT}} = -\sum_{t \in \text{response}} \log P(x_t | x_{<t}; \theta)
$$

Instruction/prompt tokens are included for context but masked from the loss.

### Data Format
```
<|system|>You are a helpful assistant.<|end|>
<|user|>Explain gradient descent.<|end|>
<|assistant|>Gradient descent is an optimization algorithm...
```

Chat templates vary by model (Alpaca, Vicuna, ChatML, Mistral).

### Data Quality Principles
- **LIMA**: 1K high-quality examples can match 52K Alpaca examples
- **Quality signals**: Clear instructions, accurate responses, diverse tasks
- **Decontamination**: Remove benchmark examples from training data
- **Human vs synthetic**: Human-written > GPT-4 generated > GPT-3.5 generated
- **Diversity**: Cover reasoning, coding, math, creative writing, safety refusals

### SFT Hyperparameters (Typical)
- Learning rate: $1 \times 10^{-5}$ to $5 \times 10^{-5}$ (10-100x smaller than pre-training)
- Epochs: 2-5 (small datasets), 1-2 (large datasets)
- Batch size: 32-128 (effective, with gradient accumulation)
- Warmup: 3-10% of steps
- Sequence packing: concatenate short examples to fill context window

### Catastrophic Forgetting
Over-training on SFT data degrades pre-trained capabilities:
- Mitigations: low LR, few epochs, mix in pre-training data (5-10%)
- Monitor perplexity on a held-out general corpus
- LoRA/QLoRA reduces forgetting by constraining weight updates

### Instruction Tuning at Scale
- Open-source datasets: OpenAssistant, Dolly, FLAN, ShareGPT
- Self-instruct: use the model itself to generate training data
- Evol-Instruct (WizardLM): iteratively evolve instructions for complexity
- Rejection sampling: generate multiple responses, filter by quality

## Implementation

```python
# SFT with HuggingFace TRL
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,  # formatted instruction-response pairs
    max_seq_length=2048,
    args=TrainingArguments(
        learning_rate=2e-5,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        warmup_ratio=0.03,
        bf16=True,
    ),
)
trainer.train()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Quality vs quantity | "How much SFT data?" | 1K high-quality > 50K low-quality (LIMA finding) |
| Catastrophic forgetting | "Risks of fine-tuning?" | Low LR, few epochs, mix pre-training data |
| Loss masking | "How does SFT loss work?" | Only compute loss on response tokens, not instruction |
| Data curation | "How to build SFT data?" | Human annotation + self-instruct + rejection sampling |

### Common Interview Questions
- [ ] Why mask instruction tokens from the loss during SFT?
- [ ] How does SFT data quality affect model performance?
- [ ] What is catastrophic forgetting and how do you mitigate it?
- [ ] Compare full fine-tuning vs LoRA for SFT.
- [ ] How would you build an SFT dataset for a domain-specific assistant?

## Comparisons

| Aspect | Full SFT | LoRA SFT | QLoRA SFT |
|--------|---------|---------|-----------|
| Parameters trained | All | 0.1-1% | 0.1-1% |
| Memory (7B model) | ~56 GB | ~16 GB | ~8 GB |
| Quality | Best | Near full | Near LoRA |
| Forgetting risk | Higher | Lower | Lower |
| Training speed | Slowest | 2-3x faster | 3-4x faster |

## Key Takeaways

- [ ] SFT: train on (instruction, response) pairs with loss only on response tokens
- [ ] Data quality >> quantity; 1K curated examples can match 50K noisy ones
- [ ] Low learning rate ($10^{-5}$) and few epochs prevent catastrophic forgetting
- [ ] Sequence packing maximizes GPU utilization for short examples
- [ ] LoRA/QLoRA are practical alternatives when GPU memory is limited
"""

CONTENT["pillar6.llm_training_alignment.rlhf"] = r"""# RLHF (Reinforcement Learning from Human Feedback)

## Overview
RLHF aligns LLM outputs with human preferences beyond what SFT alone achieves. It trains a reward model from human comparisons, then optimizes the LLM via reinforcement learning (PPO or DPO). RLHF is responsible for the "helpful, harmless, honest" behavior of ChatGPT, Claude, and similar assistants.

## Core Concepts

### RLHF Pipeline
1. **Pre-training**: Base language model on large corpus
2. **SFT**: Fine-tune on instruction-response pairs
3. **Reward Model (RM)**: Train on human preference data
4. **RL Optimization**: Use RM signal to optimize LLM via PPO

### Reward Model Training
Given human preference pairs $(y_w \succ y_l | x)$ (chosen over rejected):

$$
\mathcal{L}_{\text{RM}} = -\log \sigma(r_\theta(x, y_w) - r_\theta(x, y_l))
$$

This is the Bradley-Terry model: the probability that $y_w$ is preferred is:

$$
P(y_w \succ y_l) = \sigma(r(x, y_w) - r(x, y_l))
$$

### PPO (Proximal Policy Optimization)
Optimize the policy $\pi_\theta$ to maximize reward while staying close to the SFT model $\pi_{\text{ref}}$:

$$
\max_\theta \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(y|x)} \left[r_\phi(x, y) - \beta \text{KL}(\pi_\theta \| \pi_{\text{ref}})\right]
$$

The KL penalty prevents reward hacking (optimizing the reward model's weaknesses).

PPO clipped objective:

$$
L^{\text{CLIP}} = \mathbb{E}\left[\min\left(\frac{\pi_\theta}{\pi_{\text{old}}} A_t, \text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, 1-\epsilon, 1+\epsilon\right) A_t\right)\right]
$$

### DPO (Direct Preference Optimization)
Rafailov et al., 2023: bypass reward model and PPO entirely. Directly optimize preferences:

$$
\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)
$$

Key insight: the optimal policy under the RLHF objective has a closed-form relationship with the reward:

$$
r^*(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + C(x)
$$

### Reward Hacking
When the policy overoptimizes the reward model:
- Generates outputs that score high on RM but are low quality
- Common failure: verbose, sycophantic, or repetitive responses
- Mitigations: KL penalty, reward model ensembles, iterative RLHF

### Constitutional AI (CAI)
Anthropic's approach: use AI feedback instead of human feedback:
1. Generate response, then critique using constitutional principles
2. Revise based on critique
3. Train reward model on (original, revised) preference pairs
- Reduces reliance on human annotators
- Scales safety alignment

## Implementation

```python
# DPO training with TRL
from trl import DPOTrainer

# Dataset: {"prompt": str, "chosen": str, "rejected": str}
trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,  # frozen SFT model
    train_dataset=preference_data,
    beta=0.1,  # KL penalty strength
    args=TrainingArguments(
        learning_rate=5e-7,
        num_train_epochs=1,
        per_device_train_batch_size=4,
        bf16=True,
    ),
)
trainer.train()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| RLHF pipeline | "How is ChatGPT trained?" | Pre-train -> SFT -> RM -> PPO (or DPO) |
| DPO vs PPO | "Simpler alternative to PPO?" | DPO: no RM, no RL; direct preference optimization |
| Reward hacking | "What can go wrong with RLHF?" | Policy exploits RM weaknesses; KL penalty is key |
| KL penalty | "Why constrain to reference?" | Prevents mode collapse and reward hacking |

### Common Interview Questions
- [ ] Walk through the full RLHF training pipeline.
- [ ] What is reward hacking and how do you prevent it?
- [ ] How does DPO eliminate the need for a separate reward model?
- [ ] Why is a KL penalty needed when optimizing against the reward model?
- [ ] Compare PPO and DPO in terms of stability, compute, and quality.

## Comparisons

| Aspect | PPO (RLHF) | DPO | RLAIF / CAI |
|--------|-----------|-----|-------------|
| Reward model | Required | No | AI-generated |
| RL training | Yes (PPO) | No | Yes or DPO |
| Stability | Tricky to tune | More stable | Depends |
| Compute | High (4 models) | Low (2 models) | Medium |
| Human data | Preference pairs | Preference pairs | Minimal |
| Quality | Gold standard | Competitive | Good for safety |

## Key Takeaways

- [ ] RLHF: reward model trained on preferences, then PPO to optimize policy
- [ ] DPO: directly optimize preferences without RM or RL; simpler and competitive
- [ ] KL penalty prevents reward hacking (over-optimizing the reward model)
- [ ] $\beta$ controls exploration-exploitation: high $\beta$ = stay close to SFT model
- [ ] Constitutional AI uses AI-generated feedback for scalable alignment
"""

CONTENT["pillar6.llm_training_alignment.peft"] = r"""# Parameter-Efficient Fine-Tuning (LoRA, QLoRA)

## Overview
Parameter-Efficient Fine-Tuning (PEFT) methods adapt large models by updating only a small fraction of parameters, dramatically reducing memory and compute requirements. LoRA and QLoRA are the dominant approaches, enabling fine-tuning of 70B models on a single GPU.

## Core Concepts

### LoRA (Low-Rank Adaptation)
Hu et al., 2021: Instead of updating the full weight matrix $W \in \mathbb{R}^{d \times d}$, learn a low-rank decomposition:

$$
W' = W + \Delta W = W + BA
$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times d}$, and $r \ll d$ (typically $r = 8, 16, 64$).

Initialization: $A \sim \mathcal{N}(0, \sigma^2)$, $B = 0$ (so $\Delta W = 0$ at start).

Scaling factor: $\Delta W = \frac{\alpha}{r} BA$, where $\alpha$ is a hyperparameter.

### Why Low-Rank Works
Aghajanyan et al. (2020) showed that pre-trained models have low intrinsic dimensionality. Fine-tuning updates live in a low-dimensional subspace:

$$
\text{rank}(\Delta W) \ll \min(d_{\text{in}}, d_{\text{out}})
$$

Even $r = 4$ captures most of the fine-tuning signal for many tasks.

### Parameter Savings
For a Transformer with $L$ layers, applying LoRA to Q, K, V, O projections:
- Full FT: $L \times 4d^2$ trainable params
- LoRA ($r=16$): $L \times 4 \times 2 \times d \times r = 8Ldr$ trainable params
- For $d=4096, r=16$: reduction factor $= d/(2r) = 128\times$

### QLoRA (Quantized LoRA)
Dettmers et al., 2023: Combines 4-bit quantization with LoRA:
1. Quantize base model to 4-bit NormalFloat (NF4)
2. Add LoRA adapters in BF16/FP16
3. Backprop through quantized weights using double quantization

Memory savings:
- 7B model full FT: ~56 GB (FP16 weights + optimizer)
- 7B model QLoRA: ~6 GB (4-bit weights + FP16 LoRA + paged optimizer)

### NF4 (NormalFloat 4-bit)
Information-theoretically optimal 4-bit format for normally distributed weights:
- Quantization levels are evenly spaced in the normal distribution's quantile space
- Better than uniform INT4 for neural network weights

### Other PEFT Methods

**Adapters**: Small bottleneck modules inserted between layers:

$$
h \leftarrow h + f(hW_{\text{down}})W_{\text{up}}
$$

**Prefix Tuning**: Prepend learnable "virtual tokens" to K, V:

$$
K = [K_{\text{prefix}}; K_{\text{input}}], \quad V = [V_{\text{prefix}}; V_{\text{input}}]
$$

**IA3**: Scale activations with learned vectors (fewer params than LoRA).

### LoRA Best Practices
- Apply to all linear layers (Q, K, V, O, FFN up, FFN gate, FFN down)
- Rank $r$: 16-64 for instruction tuning; 8-16 for simple tasks
- Learning rate: 2-10x higher than full FT (e.g., $2 \times 10^{-4}$)
- $\alpha$: often set to $2r$ or $r$
- Multiple LoRA adapters can be merged or swapped at inference

## Implementation

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# QLoRA setup
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf", quantization_config=bnb_config
)
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # ~0.5% of total
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| LoRA rank selection | "How to choose $r$?" | Task complexity determines rank; 16-64 for instruction tuning |
| Full FT vs LoRA | "When to use each?" | LoRA: memory-constrained, multi-task. Full FT: maximum quality |
| QLoRA for 70B | "Fine-tune 70B on 1 GPU?" | 4-bit base + FP16 LoRA; ~48 GB for 70B |
| Adapter merging | "Serve multiple tasks?" | Merge LoRA into base weights; zero inference overhead |

### Common Interview Questions
- [ ] Why does low-rank adaptation work for fine-tuning?
- [ ] How does QLoRA reduce memory compared to full fine-tuning?
- [ ] What is the trade-off between LoRA rank $r$ and quality?
- [ ] How do you serve multiple LoRA adapters efficiently?
- [ ] Compare LoRA, adapters, and prefix tuning.

## Comparisons

| Aspect | Full FT | LoRA | QLoRA | Adapters | Prefix Tuning |
|--------|---------|------|-------|----------|---------------|
| Trainable params | 100% | 0.1-1% | 0.1-1% | 1-5% | 0.1% |
| Memory (7B) | 56 GB | 16 GB | 6 GB | 20 GB | 14 GB |
| Quality | Best | Near full | Near LoRA | Good | Lower |
| Inference overhead | None | Mergeable | Mergeable | Per-layer | Prefix tokens |
| Multi-task | Separate models | Swap adapters | Swap adapters | Swap modules | Swap prefixes |

## Key Takeaways

- [ ] LoRA: $\Delta W = BA$ with $r \ll d$; 0.1-1% of params, near-full quality
- [ ] QLoRA: 4-bit NF4 base + FP16 LoRA; fine-tune 70B on a single 48GB GPU
- [ ] Apply LoRA to all linear layers, not just attention projections
- [ ] LoRA adapters can be merged into base weights for zero inference overhead
- [ ] Higher rank $r$ = more capacity but more memory; 16-64 is typical sweet spot
"""

CONTENT["pillar6.llm_training_alignment.evaluation"] = r"""# LLM Evaluation & Benchmarks

## Overview
Evaluating LLMs requires a multi-dimensional approach: automated benchmarks for capabilities, human evaluation for quality, and safety evaluations for alignment. No single metric captures model quality -- understanding the evaluation landscape is essential for comparing models and identifying weaknesses.

## Core Concepts

### Perplexity
The standard intrinsic metric for language models:

$$
\text{PPL} = \exp\left(-\frac{1}{n}\sum_{t=1}^{n} \log P(x_t | x_{<t})\right)
$$

- Lower is better; measures how well the model predicts held-out text
- Not comparable across tokenizers (different vocab sizes)
- Necessary but not sufficient -- does not measure instruction following or reasoning

### Key Benchmarks

**Knowledge & Reasoning**:
- **MMLU** (57 subjects, 4-choice): broad knowledge evaluation
- **ARC** (science QA): reasoning over grade-school science
- **HellaSwag**: commonsense completion; saturating for large models
- **WinoGrande**: coreference resolution

**Math & Reasoning**:
- **GSM8K**: grade-school math word problems (8-shot CoT)
- **MATH**: competition-level math (harder)
- **HumanEval / MBPP**: code generation (pass@k)

**Long-Context**:
- **Needle-in-a-Haystack**: find a specific fact in long context
- **RULER**: multi-hop reasoning over long documents
- **InfiniteBench**: diverse tasks at 100K+ tokens

**Instruction Following**:
- **MT-Bench**: multi-turn conversation, GPT-4 judge (1-10 scale)
- **AlpacaEval**: pairwise comparison vs reference model
- **Chatbot Arena**: crowdsourced Elo ratings from blind human comparisons

### LLM-as-Judge
Use a strong LLM (GPT-4) to evaluate other models:
- Efficient and reproducible vs human evaluation
- Biases: verbosity bias, position bias, self-enhancement bias
- Mitigations: swap position, use rubrics, calibrate with human scores

### Contamination and Benchmark Saturation
- **Data contamination**: benchmark examples leaked into training data
- Detection: membership inference, canary strings, performance gap analysis
- **Saturation**: when models exceed human baseline (HellaSwag > 95%)
- Response: create harder benchmarks (GPQA, MuSR), use dynamic evaluations

### Safety Evaluation
- **TruthfulQA**: factual accuracy on questions designed to elicit false answers
- **BBQ**: bias in question answering across demographics
- **Red teaming**: adversarial prompt attacks to elicit unsafe behavior
- **Refusal rate**: balance between safety (refusing harmful) and helpfulness

### Evaluation Methodology
- **Few-shot prompting**: standard for benchmarks (0-shot, 5-shot, etc.)
- **Chain-of-Thought**: for reasoning tasks (GSM8K, MATH)
- **pass@k**: for code generation, probability of $\geq 1$ correct in $k$ samples

$$
\text{pass}@k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}
$$

where $n$ = total samples, $c$ = correct samples.

## Implementation

```python
# Evaluating with lm-eval-harness
# pip install lm-eval
# lm_eval --model hf --model_args pretrained=model_name \
#          --tasks mmlu,gsm8k,hellaswag --num_fewshot 5

# Custom MT-Bench style evaluation
def llm_judge_score(question, response, rubric):
    # Use GPT-4 as judge with position-debiased scoring.
    prompt = f'''Rate this response on a scale of 1-10.
Question: {question}
Response: {response}
Rubric: {rubric}
Score:'''
    # Call GPT-4 API, parse score
    return score
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Benchmark selection | "How to evaluate an LLM?" | Multi-dimensional: knowledge (MMLU), reasoning (GSM8K), safety (TruthfulQA) |
| Contamination | "Are benchmark scores trustworthy?" | Check for data leakage; dynamic benchmarks are more reliable |
| LLM-as-judge | "Scalable evaluation?" | GPT-4 judge correlates with human; watch for biases |
| Evaluation design | "Building an eval for your use case" | Task-specific held-out set + LLM judge + human spot-check |

### Common Interview Questions
- [ ] How would you evaluate an LLM for a production use case?
- [ ] What are the limitations of MMLU as an evaluation benchmark?
- [ ] How do you detect and handle data contamination?
- [ ] Compare human evaluation vs LLM-as-judge approaches.
- [ ] What is pass@k and how is it computed for code generation?

## Comparisons

| Aspect | Perplexity | MMLU | MT-Bench | Chatbot Arena |
|--------|-----------|------|----------|---------------|
| Type | Intrinsic | Knowledge | Instruction quality | Overall preference |
| Metric | PPL (lower=better) | Accuracy % | Score 1-10 | Elo rating |
| Evaluator | Automatic | Automatic | LLM judge | Human crowd |
| Contamination risk | Low | High | Medium | Low (dynamic) |
| Correlation with usefulness | Weak | Moderate | Strong | Strongest |

## Key Takeaways

- [ ] No single metric captures LLM quality; use a suite of benchmarks
- [ ] MMLU (knowledge), GSM8K (reasoning), HumanEval (code), MT-Bench (chat) cover key dimensions
- [ ] LLM-as-judge scales evaluation but has biases (verbosity, position)
- [ ] Data contamination is a major concern; dynamic/held-out evaluations are more reliable
- [ ] Chatbot Arena Elo ratings are the gold standard for overall model comparison
"""

# ===== LLM INFERENCE OPTIMIZATION =====

CONTENT["pillar6.llm_inference.kv_cache"] = r"""# KV Cache & PagedAttention

## Overview
KV cache is the key optimization for autoregressive LLM inference, avoiding recomputation of key-value pairs for previous tokens. PagedAttention (vLLM) addresses the memory fragmentation problem of naive KV cache management. Understanding KV cache sizing and management is essential for LLM serving.

## Core Concepts

### KV Cache Basics
During autoregressive generation, each new token needs attention over all previous tokens. Without caching, this requires $O(n^2)$ compute per sequence.

**With KV cache**: Store the K and V tensors for all previous tokens. For each new token, only compute its Q, then attend to cached K/V:

$$
\text{Attention}_t = \text{softmax}\left(\frac{q_t K_{1:t}^T}{\sqrt{d_k}}\right) V_{1:t}
$$

Per-token cost drops from $O(n \cdot d)$ to $O(d)$ for K/V computation (only need the new token's K, V).

### KV Cache Memory
For a model with $L$ layers, $h$ KV heads, head dim $d_k$, sequence length $n$:

$$
\text{KV cache} = 2 \times L \times h_{\text{kv}} \times d_k \times n \times \text{bytes per element}
$$

Example (LLaMA 2 70B, FP16):
- $L=80, h_{\text{kv}}=8, d_k=128, n=4096$
- KV cache = $2 \times 80 \times 8 \times 128 \times 4096 \times 2 = 1.34$ GB per sequence
- For batch size 32: 42.9 GB just for KV cache

### Pre-fill vs Decode Phases
**Pre-fill** (prompt processing):
- All prompt tokens processed in parallel (like training)
- Compute-bound: high arithmetic intensity
- KV cache populated for all prompt tokens

**Decode** (generation):
- One token at a time, sequentially
- Memory-bound: low arithmetic intensity (one Q vector attending to long K/V)
- KV cache grows by one entry per step

### PagedAttention (vLLM)
Kwon et al., 2023: Manages KV cache like OS virtual memory.

Problem: naive KV cache pre-allocates max sequence length per request, causing 60-80% memory waste due to fragmentation and over-allocation.

Solution:
- Divide KV cache into fixed-size **blocks** (pages, e.g., 16 tokens each)
- Maintain a **block table** mapping logical positions to physical blocks
- Allocate blocks on demand as sequence grows
- Share blocks across requests for common prefixes (copy-on-write)

Benefits:
- Near-zero memory waste
- 2-4x higher throughput via better batching
- Prefix caching: shared prompt KV blocks across requests

### KV Cache Compression
- **GQA/MQA**: reduce KV heads (architectural solution)
- **Quantized KV cache**: store K/V in INT8 or FP8 (2-4x reduction)
- **Sliding window**: discard KV entries outside window (Mistral)
- **Token eviction**: drop low-attention tokens (H2O, StreamingLLM)
- **Multi-Latent Attention**: compress KV into low-rank latent (DeepSeek-V2)

## Implementation

```python
class SimpleKVCache:
    # Minimal KV cache for illustration.
    def __init__(self, n_layers, n_heads, head_dim):
        self.cache = {}  # layer -> (K, V) tensors

    def update(self, layer, new_k, new_v):
        # Append new K/V to cache for this layer.
        if layer in self.cache:
            k, v = self.cache[layer]
            self.cache[layer] = (
                np.concatenate([k, new_k], axis=0),
                np.concatenate([v, new_v], axis=0),
            )
        else:
            self.cache[layer] = (new_k, new_v)
        return self.cache[layer]

def kv_cache_size_gb(n_layers, n_kv_heads, head_dim, seq_len,
                      batch_size, dtype_bytes=2):
    # Compute KV cache memory in GB.
    return (2 * n_layers * n_kv_heads * head_dim * seq_len
            * batch_size * dtype_bytes) / (1024 ** 3)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| KV cache sizing | "How much memory for inference?" | $2 L h_{\text{kv}} d_k n \times$ bytes; often dominates model weights |
| Pre-fill vs decode | "Why is first token slow?" | Pre-fill: compute-bound parallel. Decode: memory-bound sequential |
| PagedAttention | "How does vLLM improve throughput?" | Virtual memory for KV cache; eliminates fragmentation |
| Cache compression | "Reduce inference memory" | Quantize KV to INT8, use GQA, sliding window, or token eviction |

### Common Interview Questions
- [ ] Calculate the KV cache memory for LLaMA 2 70B with batch size 16.
- [ ] Why is the decode phase memory-bound?
- [ ] How does PagedAttention handle variable-length sequences?
- [ ] What are the trade-offs of quantizing the KV cache?
- [ ] How does prefix caching improve throughput for shared prompts?

## Comparisons

| Aspect | Naive KV Cache | PagedAttention | Sliding Window |
|--------|---------------|----------------|----------------|
| Memory waste | 60-80% | <4% | Fixed (window size) |
| Max sequences | Low | High (2-4x) | High |
| Prefix sharing | No | Yes (CoW) | No |
| Complexity | Simple | Moderate | Simple |
| Context limit | Max length | Max length | Window $\times$ layers |

## Key Takeaways

- [ ] KV cache: store K/V for past tokens to avoid $O(n^2)$ recomputation
- [ ] Memory formula: $2 L h_{\text{kv}} d_k n \times$ bytes per element per sequence
- [ ] PagedAttention: virtual memory for KV cache; near-zero waste, prefix sharing
- [ ] Pre-fill is compute-bound; decode is memory-bound -- different optimization strategies
- [ ] GQA reduces KV cache by $h/g$ factor; INT8 quantization gives another 2x
"""

CONTENT["pillar6.llm_inference.quantization"] = r"""# Quantization (GPTQ, AWQ, FP8)

## Overview
Quantization reduces model precision from FP16/BF16 to lower bit-widths (INT8, INT4, FP8), shrinking memory footprint and increasing throughput. For LLMs, post-training quantization (PTQ) is practical since retraining is prohibitively expensive. Understanding quantization trade-offs is critical for deploying LLMs efficiently.

## Core Concepts

### Quantization Basics
Map a continuous range $[x_{\min}, x_{\max}]$ to discrete levels:

**Symmetric quantization**:

$$
x_q = \text{round}\left(\frac{x}{s}\right), \quad s = \frac{\max(|x|)}{2^{b-1} - 1}
$$

**Asymmetric quantization**:

$$
x_q = \text{round}\left(\frac{x - z}{s}\right), \quad s = \frac{x_{\max} - x_{\min}}{2^b - 1}
$$

Dequantization: $\hat{x} = s \cdot x_q + z$

### Weight-Only Quantization
Quantize only weights; activations remain in FP16:
- Saves memory (weights dominate for large models)
- Compute done in FP16 after dequantizing on the fly
- Works well because weight distributions are more predictable

### GPTQ (Generalized Post-Training Quantization)
Frantar et al., 2023: Layer-wise quantization using Hessian information.

Minimize reconstruction error per layer:

$$
\min_{\hat{W}} \|WX - \hat{W}X\|_2^2
$$

Uses Optimal Brain Quantization (OBQ) with Cholesky decomposition for efficient per-column quantization. Quantizes columns sequentially, adjusting remaining columns to compensate for error.

- 4-bit with minimal quality loss (often < 1% on perplexity)
- Requires calibration data (~128 samples)
- Standard for weight-only INT4 quantization

### AWQ (Activation-Aware Weight Quantization)
Lin et al., 2023: Not all weight channels are equally important.

Key insight: weights multiplied by large activations matter more. Scale weights by activation magnitude before quantization:

$$
s_j = \left(\frac{\max(|X_j|)}{\max(|W_j|)}\right)^\alpha, \quad \hat{W}_j = \text{Quant}(W_j \cdot s_j) / s_j
$$

where $\alpha$ balances weight and activation error (typically $\alpha = 0.5$).

- Slightly better than GPTQ at same bit-width
- Hardware-friendly (no mixed-precision compute needed)

### FP8 (8-bit Floating Point)
Two formats: E4M3 (range) and E5M2 (precision):
- E4M3: 4 exponent, 3 mantissa bits -- wider range, used for weights
- E5M2: 5 exponent, 2 mantissa bits -- larger dynamic range, used for gradients
- Native hardware support on H100 GPUs
- ~2x throughput vs FP16 with minimal quality loss
- Can quantize both weights AND activations (unlike INT4)

### Quantization-Aware Training (QAT)
Simulate quantization during training:

$$
\hat{x} = \text{Quantize}(\text{Dequantize}(x)) \quad \text{(straight-through estimator for gradients)}
$$

- Better quality than PTQ but requires full training run
- BitNet: 1-bit weights from scratch (extreme case)

### Practical Considerations
- **Group quantization**: quantize in groups of 128 channels (reduces error)
- **Mixed precision**: keep sensitive layers (first/last, attention) at higher precision
- **Calibration data**: 128-1024 samples from training distribution
- **Quality vs size**: 4-bit typically loses 1-3% on benchmarks; 3-bit degrades significantly

## Implementation

```python
# GPTQ quantization with AutoGPTQ
from auto_gptq import AutoGPTQForCausalLM

# Quantize
model = AutoGPTQForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model.quantize(calibration_data, batch_size=4)
model.save_quantized("llama-2-7b-gptq-4bit")

# Load quantized model
model = AutoGPTQForCausalLM.from_quantized(
    "llama-2-7b-gptq-4bit", device_map="auto"
)
# 7B model: FP16 = 14 GB -> GPTQ 4-bit = 3.5 GB
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Quantization method selection | "How to shrink a 70B model?" | GPTQ/AWQ for INT4 weights; FP8 for weight+activation |
| Quality-size trade-off | "How much quality do you lose?" | 4-bit: 1-3% loss; 8-bit: <1% loss; 3-bit: significant |
| Calibration importance | "Why calibration data?" | Determines quantization parameters (scales, zeros) |
| Deployment sizing | "How much memory for inference?" | $N_{\text{params}} \times b / 8$ bytes for $b$-bit quantization |

### Common Interview Questions
- [ ] How does GPTQ minimize quantization error?
- [ ] Why does AWQ weight by activation magnitude?
- [ ] Compare INT4 (weight-only) vs FP8 (weight+activation) quantization.
- [ ] When would you use QAT vs PTQ?
- [ ] How does group size affect quantization quality?

## Comparisons

| Aspect | FP16 | FP8 | GPTQ (INT4) | AWQ (INT4) | GGUF (Q4_K_M) |
|--------|------|-----|-------------|-----------|----------------|
| Bits | 16 | 8 | 4 | 4 | ~4.8 effective |
| Memory (7B) | 14 GB | 7 GB | 3.5 GB | 3.5 GB | ~4.2 GB |
| Quality | Baseline | ~Baseline | 1-3% loss | 1-2% loss | 1-2% loss |
| Activation quant | N/A | Yes | No (FP16) | No (FP16) | No |
| Hardware | Any GPU | H100+ | Any GPU | Any GPU | CPU (llama.cpp) |

## Key Takeaways

- [ ] Weight-only INT4 (GPTQ/AWQ): 4x memory reduction, 1-3% quality loss
- [ ] AWQ: activation-aware scaling; slightly better than GPTQ at same bits
- [ ] FP8: 2x speedup on H100; quantizes both weights and activations
- [ ] Group quantization (g=128) improves quality over per-tensor quantization
- [ ] Calibration data (128-1024 samples) is needed for all PTQ methods
"""

CONTENT["pillar6.llm_inference.continuous_batching"] = r"""# Continuous Batching

## Overview
Continuous (or dynamic) batching is a serving optimization that maximizes GPU utilization by adding and removing requests from the batch as they complete, rather than waiting for the longest sequence. It is a fundamental technique in all modern LLM serving systems (vLLM, TGI, TensorRT-LLM).

## Core Concepts

### Static vs Continuous Batching

**Static batching**: All requests in a batch start and end together.
- Problem: GPU is idle while waiting for the longest sequence
- Throughput limited by the slowest request
- Short requests waste GPU time after they finish

**Continuous batching**: Requests can join/leave the batch at each decode step.
- When a request finishes (EOS or max length), a waiting request takes its slot
- GPU stays fully utilized throughout
- 2-10x throughput improvement over static batching

### Iteration-Level Scheduling
At each decode iteration:
1. Run one forward pass for all active sequences
2. Check which sequences are complete (EOS token or length limit)
3. Remove completed sequences from the batch
4. Add new requests from the queue to fill empty slots
5. Repeat

### Pre-fill/Decode Batching Strategies

**Interleaved**: Mix pre-fill and decode within the same batch.
- Pre-fill tokens are compute-heavy; decode tokens are memory-heavy
- Mixing balances compute and memory utilization

**Chunked pre-fill**: Break long prompts into chunks, process across iterations.
- Prevents long prompts from stalling decode for other requests
- vLLM default: chunk pre-fill to maintain decode latency SLA

**Disaggregated (Splitwise/DistServe)**: Separate pre-fill and decode to different GPUs.
- Optimized hardware for each phase
- Better SLA compliance at scale

### Key Metrics
- **Time to First Token (TTFT)**: latency from request to first generated token
- **Time per Output Token (TPOT)**: average time between subsequent tokens
- **Throughput**: total tokens generated per second across all requests
- **Request latency**: end-to-end time for a single request

Trade-offs:
- Larger batch size -> higher throughput but longer per-request TPOT
- Pre-fill priority -> lower TTFT but pauses decode for other requests
- The scheduler must balance these competing objectives

### Scheduling Policies
- **FCFS (First Come, First Served)**: simple, fair
- **Shortest Job First**: prioritize short sequences for lower avg latency
- **Priority-based**: different SLA tiers for different users
- **Preemption**: pause a running sequence to serve a higher-priority request
  - Requires saving/restoring KV cache state

## Implementation

```python
class ContinuousBatcher:
    # Simplified continuous batching scheduler.
    def __init__(self, max_batch_size):
        self.max_batch = max_batch_size
        self.active = []   # currently generating
        self.queue = []     # waiting requests

    def step(self, model):
        # One decode iteration.
        # Remove completed requests
        self.active = [r for r in self.active if not r.is_done()]

        # Fill empty slots from queue
        while len(self.active) < self.max_batch and self.queue:
            req = self.queue.pop(0)
            req.prefill(model)  # compute KV cache
            self.active.append(req)

        if not self.active:
            return

        # Batch decode: one token per active request
        tokens = model.decode_batch(self.active)
        for req, tok in zip(self.active, tokens):
            req.append_token(tok)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Static vs continuous | "How to improve serving throughput?" | Continuous: 2-10x throughput by filling slots as requests complete |
| TTFT vs throughput | "Latency vs throughput trade-off?" | Pre-fill competes with decode; chunked pre-fill helps |
| Scheduling strategy | "How to meet SLA?" | Priority queues, preemption, separate pre-fill/decode |
| Batch size selection | "Optimal batch size?" | Increase until memory-bound or TPOT exceeds SLA |

### Common Interview Questions
- [ ] How does continuous batching improve GPU utilization?
- [ ] What is the difference between TTFT and TPOT?
- [ ] How does chunked pre-fill help with latency consistency?
- [ ] When would you disaggregate pre-fill and decode?
- [ ] How do you handle request preemption in a continuous batch?

## Comparisons

| Aspect | Static Batching | Continuous Batching | Disaggregated |
|--------|----------------|--------------------|--------------|
| GPU utilization | Low (wait for longest) | High (slots reused) | Highest (specialized) |
| Throughput | Baseline | 2-10x | 3-15x |
| TTFT consistency | Variable | Better | Best |
| Implementation | Simple | Moderate | Complex |
| Used in | Naive HF generate | vLLM, TGI, TRT-LLM | Splitwise, DistServe |

## Key Takeaways

- [ ] Continuous batching: add/remove requests per iteration; 2-10x throughput
- [ ] TTFT (time to first token) and TPOT (time per output token) are key SLA metrics
- [ ] Chunked pre-fill prevents long prompts from stalling decode
- [ ] PagedAttention + continuous batching = foundation of modern LLM serving
- [ ] Disaggregated serving separates compute-bound pre-fill from memory-bound decode
"""

CONTENT["pillar6.llm_inference.serving_systems"] = r"""# Serving Systems (vLLM, TensorRT-LLM)

## Overview
LLM serving systems combine PagedAttention, continuous batching, quantization, and kernel optimizations into production-ready inference engines. vLLM, TensorRT-LLM, and TGI are the leading open-source options. Choosing and configuring the right serving stack is a core MLE skill.

## Core Concepts

### vLLM
Kwon et al., 2023: Production-grade LLM serving engine.

Key features:
- **PagedAttention**: virtual memory for KV cache
- **Continuous batching**: iteration-level scheduling
- **Prefix caching**: share KV cache for common prefixes
- **Speculative decoding**: draft model proposes, main model verifies
- **Tensor parallelism**: split model across GPUs
- **Quantized inference**: GPTQ, AWQ, FP8 support

Typical deployment:
```
vllm serve meta-llama/Llama-2-70b-chat-hf \
  --tensor-parallel-size 4 \
  --quantization awq \
  --max-model-len 4096
```

### TensorRT-LLM (NVIDIA)
Optimized for NVIDIA GPUs with custom CUDA kernels:

Key features:
- **In-flight batching**: continuous batching with pre-fill interleaving
- **FP8 quantization**: native H100 support
- **KV cache quantization**: INT8 KV cache
- **Multi-GPU**: tensor + pipeline parallelism
- **Custom attention kernels**: fused MHA, Flash Attention 2
- **Speculative decoding**: Medusa heads, draft model

Advantage: typically 10-30% faster than vLLM on NVIDIA hardware.
Disadvantage: more complex setup, NVIDIA-only.

### Text Generation Inference (TGI)
HuggingFace's serving solution:
- Flash Attention 2 integration
- Continuous batching with token streaming
- Watermark-based text detection
- Good for quick deployment with HuggingFace models

### Speculative Decoding
Use a small "draft" model to generate candidate tokens, then verify in parallel with the main model:

1. Draft model generates $k$ tokens autoregressively
2. Main model scores all $k$ tokens in one forward pass
3. Accept tokens where main model agrees; reject and resample from main model where it disagrees

$$
P(\text{accept token } t) = \min\left(1, \frac{p_{\text{target}}(t)}{p_{\text{draft}}(t)}\right)
$$

Speedup: 2-3x if draft model is well-aligned with target model. Mathematically guaranteed to produce same distribution as target model alone.

### Serving Architecture Patterns

**Single-model serving**: One model on one or more GPUs.
- Tensor parallelism for models > single GPU memory
- Simplest deployment

**Multi-LoRA serving**: Base model + multiple LoRA adapters.
- Share base model weights, swap LoRA per request
- Efficient multi-tenant serving

**Cascade/routing**: Route requests to different models by complexity.
- Simple queries -> small model (fast, cheap)
- Complex queries -> large model (quality)
- Router: classifier or LLM-based

### Optimization Checklist
1. **Quantization**: AWQ/GPTQ for weight-only INT4; FP8 on H100
2. **Batching**: continuous batching with PagedAttention
3. **Parallelism**: TP for latency, PP for throughput
4. **KV cache**: quantized (INT8), prefix caching
5. **Speculative decoding**: 2-3x speedup for latency-sensitive apps
6. **Kernel optimization**: Flash Attention 2, fused operations

## Implementation

```python
# vLLM OpenAI-compatible API
from openai import OpenAI

# Start vLLM server, then:
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="meta-llama/Llama-2-70b-chat-hf",
    messages=[{"role": "user", "content": "Explain KV cache."}],
    max_tokens=256,
    temperature=0.7,
)

# vLLM Python API
from vllm import LLM, SamplingParams
llm = LLM(model="meta-llama/Llama-2-7b-hf", quantization="awq")
outputs = llm.generate(["Explain attention"], SamplingParams(max_tokens=100))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| System selection | "Which serving framework?" | vLLM: general purpose. TRT-LLM: max NVIDIA perf. TGI: quick start |
| Speculative decoding | "Reduce latency?" | Draft model + parallel verify; 2-3x speedup, same distribution |
| Multi-LoRA serving | "Serve multiple fine-tuned models?" | One base model + swap LoRA per request; minimal overhead |
| Throughput vs latency | "Optimize for what?" | TP reduces latency; larger batch increases throughput |

### Common Interview Questions
- [ ] Compare vLLM and TensorRT-LLM for production deployment.
- [ ] How does speculative decoding maintain output distribution correctness?
- [ ] What is the serving architecture for a multi-tenant LLM platform?
- [ ] How do you choose between tensor and pipeline parallelism?
- [ ] Walk through the optimization stack for serving a 70B model.

## Comparisons

| Aspect | vLLM | TensorRT-LLM | TGI |
|--------|------|-------------|-----|
| PagedAttention | Yes | Yes (in-flight) | Partial |
| Quantization | GPTQ, AWQ, FP8 | FP8, INT4, INT8 | GPTQ, AWQ |
| Speculative | Yes | Yes (Medusa) | No |
| Hardware | NVIDIA, AMD | NVIDIA only | NVIDIA, AMD |
| Setup complexity | Low | High | Low |
| Throughput | High | Highest (NVIDIA) | Good |
| Multi-LoRA | Yes | Limited | Yes |

## Key Takeaways

- [ ] vLLM: PagedAttention + continuous batching; best general-purpose serving
- [ ] TensorRT-LLM: custom CUDA kernels; 10-30% faster on NVIDIA, complex setup
- [ ] Speculative decoding: draft + verify; 2-3x latency reduction, distribution-preserving
- [ ] Optimization stack: quantization + batching + parallelism + caching + kernels
- [ ] Multi-LoRA serving enables efficient multi-tenant deployment on shared hardware
"""

# ===== RAG DEEP DIVE =====

CONTENT["pillar6.rag_deep.chunking"] = r"""# Chunking Strategies

## Overview
Chunking is the process of splitting documents into smaller pieces for embedding and retrieval in RAG systems. The chunking strategy directly impacts retrieval quality -- too small and context is lost, too large and embeddings become diluted. Choosing the right strategy is a critical RAG design decision.

## Core Concepts

### Why Chunking Matters
- Embedding models have fixed context windows (512-8192 tokens)
- Smaller chunks = more precise retrieval but may lack context
- Larger chunks = more context but diluted embeddings and slower retrieval
- Chunk boundaries affect semantic coherence

### Fixed-Size Chunking
Split text into chunks of fixed token/character count with overlap:

$$
\text{chunk}_i = \text{text}[i \times s : i \times s + c]
$$

where $c$ = chunk size, $s$ = stride ($s = c - \text{overlap}$).

- Simplest approach; works well for uniform content
- Typical: 256-512 tokens with 50-100 token overlap
- Problem: may split mid-sentence or mid-paragraph

### Recursive Character Splitting
LangChain's default: try splitting by decreasing granularity:
1. Split by `\n\n` (paragraphs)
2. If chunk > max size, split by `\n` (lines)
3. If still too large, split by `. ` (sentences)
4. Last resort: split by character count

Preserves natural text boundaries better than fixed-size.

### Semantic Chunking
Group text by semantic similarity:
1. Split into sentences
2. Embed each sentence
3. Compute similarity between consecutive sentences
4. Split where similarity drops below threshold

$$
\text{split at } i \text{ if } \cos(e_i, e_{i+1}) < \tau
$$

- Adapts chunk boundaries to content structure
- More expensive (requires embedding each sentence)
- Better for heterogeneous documents

### Document-Structure-Aware Chunking
Use document structure (headers, sections, lists):
- Markdown: split by `## ` headers
- HTML: split by `<section>`, `<article>`, `<h2>` tags
- PDF: use layout analysis for section boundaries
- Code: split by function/class definitions

Preserves logical structure and context.

### Agentic / Late Chunking
Jina AI's approach: embed the full document first, then chunk the embeddings:
1. Pass full document through long-context embedding model
2. Mean-pool token embeddings within chunk boundaries

Each chunk embedding has full document context, avoiding the "lost context" problem.

### Parent-Child (Hierarchical) Chunking
- Index small chunks for precise retrieval
- Return the parent (larger) chunk for context
- Example: index by paragraph, return full section
- Balances retrieval precision with response context

### Chunk Size Selection
Rules of thumb:
- **Q&A / factoid retrieval**: 128-256 tokens (precise)
- **Summarization / reasoning**: 512-1024 tokens (context-rich)
- **Code**: function/class level (semantic boundaries)
- Always test empirically on your use case

## Implementation

```python
def fixed_size_chunks(text, chunk_size=500, overlap=100):
    # Fixed-size chunking with overlap.
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def semantic_chunks(sentences, embeddings, threshold=0.5):
    # Split where consecutive sentence similarity drops.
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = np.dot(embeddings[i-1], embeddings[i])
        if sim < threshold:
            chunks.append(" ".join(current))
            current = []
        current.append(sentences[i])
    chunks.append(" ".join(current))
    return chunks
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Chunk size selection | "How to choose chunk size?" | Smaller for precision, larger for context; test empirically |
| Semantic vs fixed | "Best chunking strategy?" | Semantic for heterogeneous docs; fixed for uniform content |
| Parent-child | "How to balance precision and context?" | Index small chunks, retrieve parent sections |
| Overlap importance | "Why overlap chunks?" | Prevents information loss at boundaries |

### Common Interview Questions
- [ ] How does chunk size affect retrieval quality?
- [ ] Compare fixed-size, recursive, and semantic chunking.
- [ ] How would you chunk a codebase for retrieval?
- [ ] What is the parent-child chunking strategy?
- [ ] How do you evaluate chunking quality?

## Comparisons

| Aspect | Fixed-Size | Recursive | Semantic | Structure-Aware |
|--------|-----------|-----------|----------|----------------|
| Complexity | Low | Low | Medium | Medium |
| Context preservation | Poor | Good | Best | Good |
| Document agnostic | Yes | Mostly | Yes | No |
| Compute cost | Minimal | Minimal | Embedding per sentence | Parsing required |
| Best for | Uniform text | General | Mixed content | Structured docs |

## Key Takeaways

- [ ] Chunk size directly impacts retrieval quality; test empirically for your use case
- [ ] Recursive splitting preserves natural boundaries (paragraphs > sentences > characters)
- [ ] Semantic chunking adapts to content but requires per-sentence embeddings
- [ ] Parent-child: index small chunks for precision, return parent for context
- [ ] Overlap (10-20%) prevents information loss at chunk boundaries
"""

CONTENT["pillar6.rag_deep.embedding_models"] = r"""# Embedding Models

## Overview
Embedding models map text to dense vectors for semantic retrieval in RAG systems. The choice of embedding model, training approach, and similarity metric directly impacts retrieval quality. Modern embedding models use contrastive learning on large-scale text pairs.

## Core Concepts

### Text Embedding Pipeline
1. Tokenize input text
2. Pass through encoder (BERT-family or custom)
3. Pool token embeddings into a single vector
4. Normalize to unit length (for cosine similarity)

$$
e = \text{normalize}\left(\text{pool}(f_\theta(\text{tokenize}(x)))\right)
$$

### Pooling Strategies
- **[CLS] token**: use the first token's embedding (BERT default)
- **Mean pooling**: average all token embeddings (most common, best results)
- **Last token**: use final token (for decoder models)

$$
e_{\text{mean}} = \frac{1}{n}\sum_{i=1}^{n} h_i
$$

### Training: Contrastive Learning
Train with InfoNCE loss on (query, positive, negative) triples:

$$
\mathcal{L} = -\log \frac{e^{\text{sim}(q, k^+)/\tau}}{\sum_{j} e^{\text{sim}(q, k_j)/\tau}}
$$

where $\tau$ is temperature, $k^+$ is the positive pair, and negatives are in-batch.

**Hard negative mining**: Sample negatives that are similar but not relevant (e.g., BM25 top-k that are not actual matches). Critical for quality.

### Matryoshka Representation Learning (MRL)
Train embeddings to be useful at multiple dimensions:

$$
\mathcal{L}_{\text{MRL}} = \sum_{d \in \{32, 64, 128, 256, 768\}} \mathcal{L}_{\text{contrast}}(e[:d])
$$

Enables trading dimension size for storage/speed without retraining.

### Bi-Encoder vs Cross-Encoder
**Bi-encoder**: embed query and document independently; fast retrieval via ANN.

$$
\text{score}(q, d) = \cos(f(q), f(d))
$$

**Cross-encoder**: jointly encode query and document; more accurate but $O(n)$.

$$
\text{score}(q, d) = \text{classifier}(\text{BERT}([q; d]))
$$

**Typical pipeline**: bi-encoder for retrieval (top-100) -> cross-encoder for reranking (top-10).

### Key Embedding Models

| Model | Dims | Max Tokens | Training Data | Performance |
|-------|------|-----------|---------------|-------------|
| all-MiniLM-L6-v2 | 384 | 256 | 1B pairs | Good baseline |
| BGE-large-en-v1.5 | 1024 | 512 | Large-scale | Strong |
| E5-mistral-7b | 4096 | 32K | Diverse | SoTA (large) |
| Cohere embed-v3 | 1024 | 512 | Proprietary | Strong API |
| OpenAI text-embedding-3 | 256-3072 | 8191 | Proprietary | Strong API, MRL |

### Similarity Metrics
- **Cosine similarity**: $\cos(a, b) = \frac{a \cdot b}{\|a\| \|b\|}$ -- standard for normalized embeddings
- **Dot product**: $a \cdot b$ -- same as cosine for unit vectors; faster
- **Euclidean distance**: $\|a - b\|_2$ -- equivalent ranking to cosine for unit vectors

## Implementation

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Embed documents and queries
docs = ["KV cache stores...", "Quantization reduces..."]
query = "How does KV cache work?"

doc_embeddings = model.encode(docs, normalize_embeddings=True)
query_embedding = model.encode([query], normalize_embeddings=True)

# Cosine similarity (dot product for normalized vectors)
scores = query_embedding @ doc_embeddings.T
top_idx = np.argmax(scores)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Model selection | "Which embedding model?" | BGE/E5 for open-source; OpenAI/Cohere for API; match dim to latency |
| Bi vs cross-encoder | "Improve retrieval accuracy?" | Bi-encoder retrieves, cross-encoder reranks; 2-stage pipeline |
| Hard negatives | "How to train better embeddings?" | Mine hard negatives from BM25; critical for quality |
| Dimension trade-off | "Reduce embedding storage?" | MRL models: truncate dims with graceful degradation |

### Common Interview Questions
- [ ] How does contrastive learning train embedding models?
- [ ] Compare bi-encoder and cross-encoder for retrieval.
- [ ] What is hard negative mining and why does it matter?
- [ ] How would you choose an embedding model for a RAG system?
- [ ] What are Matryoshka embeddings and when would you use them?

## Comparisons

| Aspect | BM25 (Sparse) | Bi-Encoder (Dense) | Cross-Encoder | ColBERT (Late) |
|--------|--------------|-------------------|---------------|----------------|
| Representation | Term frequency | Single vector | Joint encoding | Multi-vector |
| Speed (retrieval) | Very fast | Fast (ANN) | Slow ($O(n)$) | Medium |
| Semantic matching | No | Yes | Best | Yes |
| Index size | Inverted index | $n \times d$ floats | None (online) | $n \times l \times d$ |
| Use case | First stage | Retrieval | Reranking | Retrieval+quality |

## Key Takeaways

- [ ] Mean pooling + normalization is the standard embedding pipeline
- [ ] Contrastive learning with hard negatives is key to embedding quality
- [ ] Bi-encoder for fast retrieval; cross-encoder for accurate reranking
- [ ] MRL (Matryoshka) enables flexible dimension-quality trade-offs
- [ ] Match embedding model to your domain; fine-tune on domain data for best results
"""

CONTENT["pillar6.rag_deep.vector_database"] = r"""# Vector Databases

## Overview
Vector databases store and index high-dimensional embeddings for fast approximate nearest neighbor (ANN) search. They are the retrieval backbone of RAG systems. Understanding index types, trade-offs, and operational concerns is essential for building production retrieval systems.

## Core Concepts

### Exact vs Approximate Search
**Exact (brute-force)**: compute distance to every vector. $O(nd)$ per query.
- Guaranteed correct results
- Impractical for >1M vectors

**Approximate Nearest Neighbor (ANN)**: trade small recall loss for orders-of-magnitude speedup.
- Recall@k: fraction of true top-k returned by ANN
- Typical target: >95% recall with 100x+ speedup

### Index Types

**IVF (Inverted File Index)**:
- Cluster vectors into $C$ centroids via k-means
- At query time, search only the $n_{\text{probe}}$ nearest clusters
- Trade-off: more probes = higher recall, slower search

$$
\text{Recall} \uparrow \text{ with } n_{\text{probe}} \uparrow, \quad \text{Latency} \propto \frac{n_{\text{probe}}}{C} \times N
$$

**HNSW (Hierarchical Navigable Small World)**:
- Graph-based: each vector connected to nearest neighbors in a multi-layer graph
- Search: greedy traversal from top layer to bottom
- Best recall-speed trade-off for most workloads
- Higher memory (graph overhead: ~1.5x raw vectors)

**Product Quantization (PQ)**:
- Compress vectors by splitting into subvectors and quantizing each:

$$
x = [x_1, x_2, \ldots, x_M], \quad \tilde{x}_i = \text{nearest centroid in codebook}_i
$$

- 32-64x compression (e.g., 768-dim FP32 -> 48 bytes with PQ48)
- Can be combined with IVF: IVF-PQ

**Flat (no index)**: brute-force, exact. Good for <100K vectors.

### Popular Vector Databases

| Database | Type | Index | Key Feature |
|----------|------|-------|-------------|
| FAISS | Library | IVF, HNSW, PQ | Facebook; most flexible, in-process |
| Pinecone | Managed | Proprietary | Fully managed, serverless |
| Weaviate | Self-hosted/cloud | HNSW | Hybrid search, built-in ML |
| Qdrant | Self-hosted/cloud | HNSW | Rust-based, fast filtering |
| ChromaDB | Library | HNSW | Simple Python API, prototyping |
| pgvector | Extension | IVF, HNSW | PostgreSQL extension |

### Hybrid Search
Combine sparse (BM25) and dense (embedding) retrieval:

$$
\text{score} = \alpha \cdot \text{BM25}(q, d) + (1-\alpha) \cdot \cos(e_q, e_d)
$$

- Reciprocal Rank Fusion (RRF) is a popular combination method
- Sparse catches exact matches; dense catches semantic matches
- Typically $\alpha = 0.3$-$0.7$ (tune per use case)

### Filtering and Metadata
Production requirements beyond ANN:
- **Pre-filtering**: filter by metadata before ANN search (exact, fast if selective)
- **Post-filtering**: ANN first, then filter (risks returning too few results)
- **Hybrid filtering**: approximate pre-filter + ANN (Qdrant, Weaviate approach)

### Operational Concerns
- **Dimensionality**: higher dims = better quality but slower search and more storage
- **Index build time**: HNSW can take hours for >10M vectors
- **Update patterns**: HNSW supports incremental inserts; IVF needs periodic retraining
- **Memory**: HNSW keeps graph in memory; PQ enables disk-based search

## Implementation

```python
import faiss
import numpy as np

# Build HNSW index
dim = 768
index = faiss.IndexHNSWFlat(dim, 32)  # 32 neighbors per node
index.hnsw.efConstruction = 200  # quality during build
index.hnsw.efSearch = 64  # quality during search

# Add vectors
vectors = np.random.randn(100000, dim).astype("float32")
faiss.normalize_L2(vectors)
index.add(vectors)

# Search
query = np.random.randn(1, dim).astype("float32")
faiss.normalize_L2(query)
distances, indices = index.search(query, k=10)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Index selection | "Which ANN index?" | HNSW: best quality. IVF-PQ: memory-constrained. Flat: <100K |
| Hybrid search | "BM25 or embeddings?" | Both; hybrid captures exact AND semantic matches |
| Scaling strategy | "Billions of vectors?" | Shard across nodes; IVF-PQ for compression; tiered storage |
| Filtering strategy | "Search with metadata?" | Pre-filter if selective; hybrid filter for broad queries |

### Common Interview Questions
- [ ] Compare HNSW and IVF for ANN search.
- [ ] How does Product Quantization compress vectors?
- [ ] When would you use hybrid (sparse + dense) search?
- [ ] How do you handle filtering with ANN search?
- [ ] What are the trade-offs of different vector databases for production?

## Comparisons

| Aspect | HNSW | IVF | IVF-PQ | Flat |
|--------|------|-----|--------|------|
| Search quality | Best | Good | Good (with reranking) | Exact |
| Memory per vector | ~1.5x raw | ~1x raw | 0.03-0.1x raw | 1x raw |
| Build time | Slow | Medium | Medium | None |
| Incremental insert | Yes | Partial | Partial | Yes |
| Best scale | <50M | <100M | Billions | <100K |

## Key Takeaways

- [ ] HNSW: best recall-speed trade-off; standard for most RAG systems
- [ ] IVF-PQ: massive compression for billion-scale; sacrifice some quality
- [ ] Hybrid search (BM25 + dense): captures both exact and semantic matches
- [ ] Pre-filtering by metadata is critical for production RAG systems
- [ ] pgvector is practical for small-to-medium scale within existing PostgreSQL
"""

CONTENT["pillar6.rag_deep.advanced_rag"] = r"""# Advanced RAG Patterns

## Overview
Basic RAG (retrieve-then-generate) has well-known failure modes: irrelevant retrieval, missing context, hallucination over retrieved content. Advanced RAG patterns address these through query transformation, multi-step retrieval, reranking, and evaluation. These patterns are essential for building production-quality RAG systems.

## Core Concepts

### Query Transformation

**Query Rewriting**: Use an LLM to reformulate the user query for better retrieval.

$$
q' = \text{LLM}(\text{"Rewrite this query for retrieval: "} + q)
$$

**HyDE (Hypothetical Document Embeddings)**: Generate a hypothetical answer, embed it, and search for similar real documents.

$$
d_{\text{hyp}} = \text{LLM}(q), \quad \text{retrieve}(\text{embed}(d_{\text{hyp}}))
$$

Rationale: hypothetical documents are closer to real documents in embedding space than queries are.

**Multi-Query**: Generate multiple query variants, retrieve for each, merge results.

### Reranking
Two-stage pipeline: retrieve broadly (top-100 with bi-encoder), then rerank precisely:

1. **Cross-encoder reranking**: score each (query, document) pair jointly

$$
\text{score}(q, d) = \text{CrossEncoder}([q; \text{SEP}; d])
$$

2. **LLM reranking**: ask the LLM to rank documents by relevance
3. **Cohere Rerank / BGE-reranker**: specialized reranking models

Reranking typically improves recall@10 by 5-15%.

### Multi-Step Retrieval

**Iterative retrieval**: Use initial retrieved context to formulate follow-up queries:

```
Step 1: Retrieve with original query
Step 2: LLM reads context, generates follow-up query
Step 3: Retrieve with follow-up query
Step 4: Combine all retrieved context for final answer
```

**Self-RAG (Asai et al., 2023)**: LLM decides when to retrieve and critiques its own output:
- Generate + special tokens: [Retrieve], [IsRel], [IsSup], [IsUse]
- Model self-reflects on whether retrieval is needed and whether output is supported

### Contextual Compression
Reduce retrieved chunks to only the relevant portions:

$$
c_{\text{compressed}} = \text{LLM}(\text{"Extract the relevant parts for: "} + q + c)
$$

- Reduces noise in context window
- Enables fitting more chunks in the LLM context
- LLMLingua: token-level compression using perplexity

### RAG Fusion
Combine results from multiple retrieval strategies using Reciprocal Rank Fusion (RRF):

$$
\text{RRF}(d) = \sum_{r \in \text{rankings}} \frac{1}{k + \text{rank}_r(d)}
$$

where $k$ is typically 60. RRF is robust to score scale differences between retrievers.

### Structured / Graph RAG
- **Knowledge Graph RAG**: extract entities/relations, traverse graph for context
- **Graph RAG (Microsoft)**: build community summaries over document graph; query-focused summarization
- **SQL RAG**: convert natural language to SQL, query structured data

### RAG Evaluation

**Retrieval metrics**:
- **Recall@k**: fraction of relevant docs in top-k
- **MRR (Mean Reciprocal Rank)**: $\frac{1}{|Q|}\sum_{q} \frac{1}{\text{rank}_q}$
- **NDCG@k**: normalized discounted cumulative gain

**Generation metrics (RAGAS framework)**:
- **Faithfulness**: is the answer supported by retrieved context?
- **Answer relevancy**: does the answer address the question?
- **Context precision**: are retrieved documents relevant?
- **Context recall**: are all necessary documents retrieved?

## Implementation

```python
def hyde_retrieval(query, llm, retriever):
    # HyDE: generate hypothetical doc, then retrieve.
    hyp_doc = llm.generate(
        f"Write a passage that answers: {query}"
    )
    hyp_embedding = retriever.embed(hyp_doc)
    return retriever.search(hyp_embedding, k=10)

def rerank(query, docs, reranker):
    # Cross-encoder reranking.
    pairs = [(query, doc.text) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: -x[1])
    return [doc for doc, _ in ranked]

def rrf(rankings, k=60):
    # Reciprocal Rank Fusion.
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| HyDE | "Query-document mismatch" | Hypothetical answers bridge the query-document gap |
| Reranking | "Improve retrieval precision" | Cross-encoder reranking: 5-15% recall improvement |
| Multi-step retrieval | "Complex multi-hop questions" | Iterative: retrieve, reason, retrieve again |
| RAG evaluation | "How to measure RAG quality?" | RAGAS: faithfulness, relevancy, precision, recall |

### Common Interview Questions
- [ ] How does HyDE improve retrieval for RAG?
- [ ] Design a reranking pipeline for a production RAG system.
- [ ] When would you use multi-step vs single-step retrieval?
- [ ] How do you evaluate RAG system quality end-to-end?
- [ ] Compare RAG Fusion with simple retrieval.

## Comparisons

| Aspect | Naive RAG | + Reranking | + HyDE | + Multi-step | Self-RAG |
|--------|----------|-------------|--------|-------------|---------|
| Retrieval quality | Baseline | +5-15% | +10-20% | Best for multi-hop | Adaptive |
| Latency | Lowest | +cross-encoder | +LLM call | +multiple rounds | +reflection |
| Complexity | Simple | Low | Medium | High | High |
| Best for | Simple QA | Precision-critical | Short queries | Complex reasoning | Diverse tasks |

## Key Takeaways

- [ ] Query transformation (rewrite, HyDE, multi-query) bridges the query-document gap
- [ ] Cross-encoder reranking is the highest-ROI improvement for RAG precision
- [ ] Multi-step retrieval handles complex, multi-hop questions
- [ ] RAGAS framework: faithfulness, relevancy, context precision, context recall
- [ ] RRF combines multiple retrieval strategies robustly
"""

# ===== MULTIMODAL =====

CONTENT["pillar6.multimodal.vision_language"] = r"""# Vision-Language Models (CLIP, LLaVA)

## Overview
Vision-language models (VLMs) bridge the gap between visual and textual understanding. CLIP introduced contrastive vision-language pre-training; LLaVA and similar models extend LLMs with visual input for multimodal conversation. Understanding VLM architectures is increasingly important as LLMs become multimodal.

## Core Concepts

### CLIP (Contrastive Language-Image Pre-training)
Radford et al., 2021: Learn aligned image-text representations via contrastive learning.

**Architecture**: Dual encoder -- separate image encoder (ViT) and text encoder (Transformer).

**Training**: InfoNCE loss on (image, text) pairs:

$$
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N}\left[\log \frac{e^{\text{sim}(I_i, T_i)/\tau}}{\sum_j e^{\text{sim}(I_i, T_j)/\tau}} + \log \frac{e^{\text{sim}(T_i, I_i)/\tau}}{\sum_j e^{\text{sim}(T_i, I_j)/\tau}}\right]
$$

where $\text{sim}(I, T) = \frac{f(I) \cdot g(T)}{\|f(I)\| \|g(T)\|}$.

**Key properties**:
- Zero-shot classification: compare image embedding with text embeddings of class names
- Trained on 400M image-text pairs from the internet
- Strong transfer to downstream tasks without fine-tuning

### Vision Transformer (ViT)
Image encoder used in CLIP and VLMs:

1. Split image into $P \times P$ patches (typically $P = 14$ or $16$)
2. Linearly project each patch to embedding dimension
3. Add position embeddings + [CLS] token
4. Process through Transformer encoder

$$
z_0 = [\text{CLS}; x_1W_E; x_2W_E; \ldots; x_NW_E] + E_{\text{pos}}
$$

For 224x224 image with P=14: $N = (224/14)^2 = 256$ patches.

### LLaVA (Large Language and Vision Assistant)
Liu et al., 2023: Connect a vision encoder to an LLM for multimodal conversation.

**Architecture**:
1. **Vision encoder**: CLIP ViT-L/14 (frozen or fine-tuned)
2. **Projection**: MLP mapping vision tokens to LLM embedding space
3. **LLM**: LLaMA/Vicuna (fine-tuned)

$$
h_{\text{img}} = W_{\text{proj}} \cdot \text{ViT}(\text{image})
$$

Input to LLM: $[\text{system}; h_{\text{img}}; \text{user query}]$

**Training stages**:
1. Pre-training: align vision-language features (595K image-text pairs, freeze LLM)
2. Instruction tuning: fine-tune LLM on visual instruction data (158K examples)

### Other VLM Architectures

**Flamingo / OpenFlamingo**: Cross-attention between vision and language.
- Perceiver Resampler: compress variable-length image features to fixed tokens
- Gated cross-attention layers interleaved with LLM layers

**Qwen-VL / InternVL**: Native multimodal LLMs trained from scratch.

**GPT-4V / Claude Vision**: Proprietary multimodal models.

### Applications
- **Visual QA**: Answer questions about images
- **Image captioning**: Generate descriptions
- **Visual grounding**: Localize objects described in text
- **Document understanding**: Parse charts, tables, layouts
- **Zero-shot classification**: CLIP-style text-image matching

### CLIP Limitations
- Bag-of-words behavior: "a dog chasing a cat" $\approx$ "a cat chasing a dog"
- Poor at counting, spatial relations, fine-grained attributes
- Biases from web-scraped training data
- Fixed resolution (224x224 in original)

## Implementation

```python
# CLIP zero-shot classification
from transformers import CLIPProcessor, CLIPModel
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

image = load_image("cat.jpg")
texts = ["a photo of a cat", "a photo of a dog", "a photo of a bird"]
inputs = processor(text=texts, images=image, return_tensors="pt",
                   padding=True)

outputs = model(**inputs)
logits = outputs.logits_per_image  # (1, 3)
probs = logits.softmax(dim=-1)  # classification probabilities

# LLaVA-style inference
from transformers import LlavaForConditionalGeneration
model = LlavaForConditionalGeneration.from_pretrained("llava-hf/llava-1.5-7b-hf")
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| CLIP for retrieval | "Image search system" | Embed images and text in same space; cosine similarity |
| VLM architecture | "How does LLaVA work?" | ViT -> projection -> LLM; two-stage training |
| Zero-shot classification | "Classify without labels" | Compare image embedding with text class embeddings |
| Multimodal RAG | "RAG with images" | CLIP-embed images + text; retrieve both modalities |

### Common Interview Questions
- [ ] How does CLIP learn aligned image-text representations?
- [ ] Describe the LLaVA architecture and training pipeline.
- [ ] What are the limitations of CLIP's contrastive approach?
- [ ] How would you build a multimodal search system?
- [ ] Compare cross-attention (Flamingo) vs projection (LLaVA) for connecting vision to language.

## Comparisons

| Aspect | CLIP | LLaVA | Flamingo | GPT-4V |
|--------|------|-------|----------|--------|
| Architecture | Dual encoder | ViT + MLP + LLM | ViT + cross-attn + LLM | Unknown |
| Vision-language fusion | Late (dot product) | Early (concat tokens) | Cross-attention | Unknown |
| Generation | No | Yes | Yes | Yes |
| Training data | 400M pairs | 595K + 158K | Billions | Unknown |
| Open weights | Yes | Yes | Partially | No |
| Best for | Retrieval, zero-shot | Visual chat, VQA | Few-shot, in-context | General multimodal |

## Key Takeaways

- [ ] CLIP: contrastive dual encoder; aligns image and text in shared embedding space
- [ ] ViT: split image into patches, process as sequence with Transformer
- [ ] LLaVA: ViT + projection MLP + LLM; two-stage training (align, then instruct)
- [ ] Zero-shot classification: compare image embedding to text class embeddings
- [ ] VLMs enable multimodal RAG, visual QA, document understanding in production
"""

# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def main() -> None:
    # Populate Pillar 6 leaf nodes with content.
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
