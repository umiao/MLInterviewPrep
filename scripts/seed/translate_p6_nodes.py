#!/usr/bin/env python3
# PINNED_BY: T-P1-876  (open fix ticket for L1973 syntax error; do NOT auto-retire until fixed or ticket closed)
"""Translate nodes 149-164 to Chinese with deep expansion."""

import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = r"C:\Users\Shenghui Xu\Desktop\Gen_AI_Proj\MLInterviewPrep\data\mle_prep.db"

translations = {}

# ============================================================
# Node 149: GPT Family
# ============================================================
translations[149] = r"""# GPT Family

## Overview
**GPT (Generative Pre-trained Transformer，生成式预训练变换器)** 系列开创了 **Decoder-only（纯解码器）** 自回归语言模型的范式。从 GPT-1 到 GPT-4，该系列不断验证了一个核心发现：通过扩展模型规模、数据量和计算资源，可以涌现出 **In-context Learning（上下文学习）**、**Chain-of-Thought Reasoning（链式思维推理）** 和 **Instruction Following（指令跟随）** 等能力。

GPT 系列的发展历程不仅是大语言模型技术的缩影，更深刻地改变了自然语言处理的研究范式——从"预训练+微调"转向"预训练+提示"，再到"预训练+对齐"。理解 GPT 系列的演进脉络，对于准备 MLE 面试中的 LLM 相关问题至关重要。

## Core Concepts

### Autoregressive Language Modeling
所有 GPT 模型都基于 **Autoregressive（自回归）** 的 **Next-token Prediction（下一词预测）** 范式进行训练。模型将文本视为 token 序列，每个 token 的生成仅依赖于之前的所有 token：

$$P(x) = \prod_{t=1}^{n} P(x_t | x_{<t}; \theta)$$

对应的训练目标是最小化负对数似然：

$$\mathcal{L} = -\sum_{t=1}^{n} \log P(x_t | x_{<t}; \theta)$$

其中 $\theta$ 为模型参数，$x_{<t}$ 表示位置 $t$ 之前的所有 token。这一目标函数的优雅之处在于：通过简单的下一词预测任务，模型被迫学习语言的语法结构、语义关系、世界知识和推理能力。

自回归建模使用 **Causal Masking（因果遮蔽）** 确保每个位置只能关注之前的位置，防止信息泄漏。这与 BERT 等双向模型的 MLM 目标不同，自回归模型天然适合文本生成任务。

### GPT Model Evolution

| Model | Year | Params | Context | Key Innovation |
|-------|------|--------|---------|----------------|
| GPT-1 | 2018 | 117M | 512 | 预训练+微调范式 |
| GPT-2 | 2019 | 1.5B | 1024 | 零样本任务迁移 |
| GPT-3 | 2020 | 175B | 2048 | 上下文学习/少样本提示 |
| GPT-4 | 2023 | ~1.8T (MoE) | 128K | 多模态/RLHF/指令跟随 |

**GPT-1** 确立了"无监督预训练+有监督微调"的两阶段范式，使用 12 层 Transformer 解码器。**GPT-2** 将规模提升一个数量级，发现模型可以在不微调的情况下直接通过提示完成任务（零样本迁移）。**GPT-3** 实现了质的飞跃——175B 参数使模型涌现出 **In-context Learning（上下文学习）** 能力，仅通过几个示例就能完成新任务。**GPT-4** 采用 **MoE (Mixture of Experts，混合专家)** 架构，支持多模态输入，并通过 **RLHF (Reinforcement Learning from Human Feedback，基于人类反馈的强化学习)** 实现了更好的对齐。

### In-Context Learning (ICL)
**ICL（上下文学习）** 是 GPT-3 中发现的涌现能力。模型可以通过提示中提供的示例来完成任务，无需任何梯度更新：

$$P(y|x, \text{examples}) \approx P(y | \text{demo}_1, \ldots, \text{demo}_k, x)$$

其中 $\text{demo}_i = (x_i, y_i)$ 是输入-输出示例对。ICL 有三种模式：

- **Zero-shot（零样本）**：仅提供任务描述，不给示例
- **Few-shot（少样本）**：提供 $k$ 个输入-输出示例
- **Chain-of-Thought（链式思维）**：示例中包含推理过程

ICL 的机制仍有争议。一种理论认为预训练隐式地学习了一个"学习算法"，在推理时通过注意力机制实现梯度下降的近似。另一种观点认为 ICL 本质上是 **Task Location（任务定位）**——模型在预训练分布中找到与当前上下文最匹配的任务。

### Scaling Laws
**Scaling Laws（缩放定律）**（Kaplan et al., 2020）揭示了模型性能与计算资源之间的幂律关系：

$$L(N) \approx \left(\frac{N_c}{N}\right)^{\alpha_N}, \quad L(D) \approx \left(\frac{D_c}{D}\right)^{\alpha_D}$$

其中 $L$ 是损失，$N$ 是参数量，$D$ 是数据量，$N_c, D_c, \alpha_N, \alpha_D$ 是拟合常数。关键发现包括：

- 损失随参数量和数据量平滑地呈幂律下降
- 更大的模型具有更高的 **Sample Efficiency（样本效率）**
- 在固定计算预算下，存在最优的参数量和数据量分配

**Chinchilla Scaling（Chinchilla缩放定律）**（Hoffmann et al., 2022）修正了早期的发现，证明对于固定计算预算 $C$，应当均衡分配给模型大小和数据量：

$$N_{\text{opt}} \propto C^{0.5}, \quad D_{\text{opt}} \propto C^{0.5}$$

这意味着 GPT-3（175B 参数，300B tokens）实际上是"欠训练"的——以同等计算量训练的 Chinchilla（70B 参数，1.4T tokens）达到了相同甚至更好的性能。这一发现深刻影响了后续 LLM 的训练策略，LLaMA 等模型都采用了更多数据量的方案。

### GPT Architecture Details
GPT-2/3 的关键架构设计：

- **Pre-norm（前置归一化）**：在注意力和 FFN 之前进行 LayerNorm，提升训练稳定性
- **Learned Absolute Position Embeddings（学习的绝对位置编码）**：将位置信息作为可学习参数
- **Dense Attention（密集注意力）**：所有头、全序列参与注意力计算
- **BPE Tokenizer（字节对编码分词器）**：约 50K 词表
- 无编码器、无交叉注意力——纯解码器结构

GPT-4 可能使用了 **MoE** 架构，每次推理仅激活部分专家，在保持计算效率的同时拥有更大的总参数量。

## Implementation

```python
# 使用 GPT 风格模型进行文本生成
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# In-context Learning 示例
prompt = '''Classify the sentiment:
Text: "Great movie!" -> Positive
Text: "Terrible service" -> Negative
Text: "The food was amazing" ->'''
inputs = tokenizer(prompt, return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=5)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

```python
# 计算自回归模型的困惑度 (Perplexity)
import torch
import torch.nn.functional as F

def compute_perplexity(model, tokenizer, text):
    """计算给定文本的困惑度"""
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
    # 困惑度 = exp(平均交叉熵损失)
    perplexity = torch.exp(outputs.loss)
    return perplexity.item()
```

## Interview Tips
- 能够清晰描述 GPT-1 到 GPT-4 的演进逻辑和关键创新
- 理解自回归建模与双向建模（BERT）的本质区别和适用场景
- 掌握缩放定律和 Chinchilla 定律的核心结论
- 能够解释 ICL 的工作机制及其与传统微调的对比
- 了解 MoE 架构如何在效率和容量之间取得平衡
"""

# ============================================================
# Node 150: LLaMA / Mistral
# ============================================================
translations[150] = r"""# LLaMA / Mistral Open-Source LLMs

## Overview
**LLaMA (Large Language Model Meta AI)** 和 **Mistral** 代表了开源权重大语言模型的最前沿。它们融合了多项架构改进——**RoPE (Rotary Position Embedding，旋转位置编码)**、**GQA (Grouped-Query Attention，分组查询注意力)**、**SwiGLU（SwiGLU激活函数）** 和 **RMSNorm（均方根归一化）**——使得开源模型在许多任务上达到了与闭源模型可比拟的性能。

这些模型的开源推动了整个 LLM 生态系统的发展，使得研究者和企业可以在本地部署、微调和改进大语言模型，而不必依赖 API 服务。理解它们的架构设计选择，对于面试中的模型架构讨论至关重要。

## Core Concepts

### RoPE (Rotary Position Embedding)
**RoPE（旋转位置编码）** 是 LLaMA 和 Mistral 共同采用的位置编码方案，通过对查询和键向量施加旋转矩阵来编码位置信息：

$$f(x_m, m) = x_m e^{im\theta}$$

对于每一对维度 $(2i, 2i+1)$，旋转角度为：

$$\theta_i = 10000^{-2i/d}$$

其中 $d$ 是注意力头的维度，$m$ 是 token 位置。RoPE 的核心优势在于：

- **相对位置编码**：两个位置之间的注意力仅取决于相对距离 $m - n$
- **外推能力**：通过调整基础频率（如 **NTK-aware Scaling** 或 **YaRN**），可以将训练上下文长度扩展到更长序列
- **计算高效**：仅需要简单的旋转操作，不引入额外参数

### GQA (Grouped-Query Attention)
**GQA（分组查询注意力）** 是介于 **MHA (Multi-Head Attention，多头注意力)** 和 **MQA (Multi-Query Attention，多查询注意力)** 之间的折中方案：

| 方案 | Key/Value 头数 | 内存效率 | 质量 |
|------|----------------|----------|------|
| MHA | $n_h$ | 低 | 最优 |
| GQA | $n_h / g$ | 中等 | 接近MHA |
| MQA | 1 | 最高 | 略有下降 |

LLaMA-2 70B 使用 $n_h = 64$ 个查询头和 $8$ 个 KV 头（$g = 8$），将 KV cache 内存减少了 8 倍，同时保持了接近 MHA 的性能。GQA 的关键在于多个查询头共享同一组键值头，大幅降低推理时的显存占用。

### SwiGLU Activation
**SwiGLU** 是 GLU 变体中表现最佳的激活函数，替代了传统的 ReLU/GELU：

$$\text{SwiGLU}(x) = \text{Swish}(xW_1) \otimes (xW_2)$$

其中 $\text{Swish}(x) = x \cdot \sigma(\beta x)$，$\otimes$ 表示逐元素乘法。SwiGLU 引入了门控机制，使得网络可以动态地选择哪些信息通过 FFN 层。虽然增加了一个权重矩阵（从两个变为三个），但通常通过减小隐层维度来保持总参数量不变（$d_{ff} = \frac{2}{3} \times 4d$）。

### RMSNorm
**RMSNorm (Root Mean Square Normalization，均方根归一化)** 简化了 LayerNorm，去除了均值中心化步骤：

$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d}\sum_{i=1}^{d} x_i^2 + \epsilon}} \cdot \gamma$$

相比 LayerNorm，RMSNorm 减少了计算量（省去均值计算），同时在实践中不损失性能。LLaMA 在每个 Transformer 层的注意力和 FFN 之前使用 **Pre-RMSNorm**。

### Sliding Window Attention (Mistral)
**Sliding Window Attention（滑动窗口注意力）** 是 Mistral 的核心创新，每个 token 仅关注窗口大小 $W$ 内的 token：

$$\text{Attention}(x_i) = \text{softmax}\left(\frac{Q_i K_{[i-W:i]}^T}{\sqrt{d_k}}\right) V_{[i-W:i]}$$

通过层级堆叠，第 $l$ 层可以间接关注到 $l \times W$ 距离外的 token，形成 **Effective Receptive Field（有效感受野）**。Mistral 7B 使用 $W = 4096$，在32层堆叠下理论感受野达到 131K token。这在保持线性内存增长的同时实现了对长上下文的处理。

### Architecture Comparison

| Feature | LLaMA-2 | Mistral 7B | LLaMA-3 |
|---------|---------|------------|---------|
| 位置编码 | RoPE | RoPE | RoPE (扩展频率) |
| 注意力 | GQA | GQA + 滑动窗口 | GQA |
| 激活函数 | SwiGLU | SwiGLU | SwiGLU |
| 归一化 | RMSNorm | RMSNorm | RMSNorm |
| 上下文长度 | 4K | 8K (滑动窗口32K) | 8K→128K |
| 词表大小 | 32K | 32K | 128K |
| 训练数据量 | 2T tokens | 未公开 | 15T+ tokens |

LLaMA-3 进一步扩展了词表到 128K（更好的多语言支持）和训练数据到 15T+ tokens（遵循 Chinchilla 定律的数据为王策略）。

## Implementation

```python
# 加载和使用 LLaMA/Mistral 模型
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载 Mistral 7B
model_name = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# RoPE 位置编码的核心实现
def apply_rotary_emb(xq, xk, freqs_cis):
    """对 query 和 key 施加旋转位置编码"""
    xq_complex = torch.view_as_complex(xq.reshape(*xq.shape[:-1], -1, 2))
    xk_complex = torch.view_as_complex(xk.reshape(*xk.shape[:-1], -1, 2))
    xq_out = torch.view_as_real(xq_complex * freqs_cis).flatten(-2)
    xk_out = torch.view_as_real(xk_complex * freqs_cis).flatten(-2)
    return xq_out, xk_out

def precompute_freqs_cis(dim, max_seq_len, theta=10000.0):
    """预计算旋转频率"""
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(max_seq_len)
    freqs = torch.outer(t, freqs)
    return torch.polar(torch.ones_like(freqs), freqs)
```

## Interview Tips
- 能够对比 RoPE 与绝对位置编码、相对位置编码的优缺点
- 理解 GQA 如何在推理效率和模型质量之间取得平衡
- 能够解释滑动窗口注意力如何通过层级堆叠获得长距离依赖
- 掌握 LLaMA 和 Mistral 的架构差异及设计动机
- 了解开源模型生态系统的发展趋势和对行业的影响
"""

# ============================================================
# Node 151: Pre-training
# ============================================================
translations[151] = r"""# Pre-training

## Overview
**Pre-training（预训练）** 是大语言模型学习语言表示的基础阶段，模型从海量无标注语料中学习语法、语义、世界知识和推理能力。预训练的质量直接决定了模型的能力上限，后续的微调和对齐只能在预训练建立的能力基础上进行调整和增强。

在高级 MLE 面试中，预训练相关问题涵盖数据处理流水线、训练稳定性、缩放定律和计算优化等方面。理解预训练的原理和工程实践，是成为 LLM 领域高级工程师的核心能力。

## Core Concepts

### Data Pipeline
预训练数据流水线是一个复杂的多阶段系统：

**数据收集** → **去重** → **质量过滤** → **有害内容过滤** → **分词** → **打包**

每个阶段都至关重要：

- **Web Crawling（网页爬取）**：使用 Common Crawl 等数据源，包含数万亿 token 的原始数据
- **Deduplication（去重）**：使用 **MinHash（最小哈希）** 和 **SimHash（相似哈希）** 进行模糊去重，文档级和段落级去重可减少 30-50% 的数据量，且能提升模型质量
- **Quality Filtering（质量过滤）**：基于启发式规则（长度、语言检测、标点比例）和分类器（如使用 Wikipedia 作为正例训练质量分类器）
- **Tokenization（分词）**：**BPE (Byte Pair Encoding，字节对编码)** 或 **SentencePiece** 将文本转换为 token 序列

### Curriculum Learning
**Curriculum Learning（课程学习）** 策略按照数据质量或难度逐步安排训练数据：

- **早期阶段**：使用大量通用网页数据建立基础语言能力
- **中期阶段**：逐步增加高质量数据（书籍、论文、代码）的比例
- **后期阶段**：使用精选的高质量数据进行 **Annealing（退火）**，同时降低学习率

这一策略的直觉是：先让模型学会"说话"，再让它学会"说好话"。实践证明，在训练末期加入高质量数据对最终性能有显著提升。

### Chinchilla Scaling Laws
**Chinchilla Scaling Laws（Chinchilla缩放定律）**（Hoffmann et al., 2022）是预训练资源分配的核心指导原则。对于给定的计算预算 $C$（以 FLOP 计）：

$$N_{\text{opt}} \propto C^{0.5}, \quad D_{\text{opt}} \propto C^{0.5}$$

即最优参数量和最优数据量都与计算预算的平方根成正比。具体的近似关系为：

$$D_{\text{opt}} \approx 20 \times N_{\text{opt}}$$

这意味着一个 7B 参数的模型理论上需要约 140B token 的训练数据才能达到最优。然而实际实践中（如 LLaMA），通常会使用远超 Chinchilla 最优值的数据量（如 2T tokens），因为推理成本通常远高于训练成本——使用更多数据训练较小的模型，可以在部署时节省大量推理成本。

### Training Stability
大规模预训练面临多种稳定性挑战：

- **Loss Spikes（损失尖峰）**：训练过程中损失突然上升，通常由数据中的噪声或数值不稳定引起。常见处理方式是跳过导致尖峰的数据批次或从较早的 checkpoint 恢复
- **Learning Rate Schedule（学习率调度）**：通常使用线性 warmup + cosine decay：

$$\eta(t) = \begin{cases} \eta_{\max} \cdot \frac{t}{T_{\text{warmup}}} & t \leq T_{\text{warmup}} \\ \eta_{\min} + \frac{\eta_{\max} - \eta_{\min}}{2}\left(1 + \cos\frac{\pi(t - T_{\text{warmup}})}{T_{\text{total}} - T_{\text{warmup}}}\right) & t > T_{\text{warmup}} \end{cases}$$

warmup 阶段通常占总训练步数的 0.1-1%。

- **Gradient Clipping（梯度裁剪）**：将梯度范数限制在阈值以内（通常 1.0），防止梯度爆炸
- **Mixed Precision（混合精度）**：使用 **BF16 (Brain Floating Point 16，脑浮点16位)** 进行前向和反向传播，FP32 用于主权重和梯度累积，兼顾速度和数值稳定性

### Distributed Training
大规模预训练通常需要数百到数千个 GPU，涉及多种并行策略：

- **Data Parallelism（数据并行）**：每个 GPU 持有完整模型副本，处理不同的数据批次
- **Tensor Parallelism（张量并行）**：将单个层的权重矩阵切分到多个 GPU
- **Pipeline Parallelism（流水线并行）**：将不同层分配到不同 GPU，使用微批次流水线化
- **FSDP (Fully Sharded Data Parallelism，完全分片数据并行)**：ZeRO 优化器的实现，将参数、梯度和优化器状态分片到所有 GPU

对于 70B+ 模型，通常需要组合使用多种并行策略（如 TP 在节点内 + PP 在节点间 + FSDP 覆盖全局）。

### Training Compute Estimation
训练一个 Transformer 模型所需的 FLOP 近似为：

$$C \approx 6 \times N \times D$$

其中 $N$ 是参数量，$D$ 是训练 token 数。因子 6 来自于每个 token 的前向传播（约 $2N$ FLOP）和反向传播（约 $4N$ FLOP）。

## Implementation

```python
# 预训练数据处理流水线示例
from datasets import load_dataset
from transformers import AutoTokenizer
import hashlib

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")

def dedup_by_minhash(documents, num_hashes=128, threshold=0.8):
    """基于 MinHash 的模糊去重"""
    from datasketch import MinHash, MinHashLSH
    lsh = MinHashLSH(threshold=threshold, num_perm=num_hashes)
    unique_docs = []
    for i, doc in enumerate(documents):
        m = MinHash(num_perm=num_hashes)
        for word in doc.split():
            m.update(word.encode('utf-8'))
        if not lsh.query(m):
            lsh.insert(str(i), m)
            unique_docs.append(doc)
    return unique_docs

# 学习率调度
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

def get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps):
    """带 warmup 的余弦退火学习率调度"""
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
```

## Interview Tips
- 能够详细描述预训练数据流水线的各个阶段及其重要性
- 理解 Chinchilla 定律及其对模型设计的实际影响
- 掌握训练稳定性问题的诊断和处理方法
- 能够解释不同并行策略的适用场景和权衡
- 了解训练计算量估算公式及其在资源规划中的应用
"""

# ============================================================
# Node 152: SFT
# ============================================================
translations[152] = r"""# Supervised Fine-Tuning (SFT)

## Overview
**SFT (Supervised Fine-Tuning，有监督微调)** 将预训练基座模型转化为能够跟随指令的对话助手。通过在精心策划的（指令，响应）数据对上进行训练，SFT 教会模型理解用户意图并生成有帮助、安全且格式正确的回答。

SFT 是 LLM 对齐流水线的第一步（SFT → RLHF/DPO），其质量直接影响后续对齐阶段的效果。在面试中，SFT 相关问题常涉及数据策略、训练技巧和过拟合防护。

## Core Concepts

### Instruction Tuning
**Instruction Tuning（指令微调）** 是 SFT 的核心范式。训练数据格式为：

```
[System Prompt] + [User Instruction] + [Model Response]
```

关键设计决策包括：

- **Loss Masking（损失遮蔽）**：仅在模型响应部分计算损失，而非用户指令部分。这确保模型学习"如何回答"而非"如何重复问题"
- **Chat Template（对话模板）**：使用特殊 token 标记对话角色和轮次，如 `<|im_start|>user\n...<|im_end|>\n<|im_start|>assistant\n...`
- **Multi-turn（多轮对话）**：训练数据应包含多轮对话，使模型学会维持上下文

### Data Quality > Quantity
SFT 的核心洞见是 **数据质量远比数量重要**：

- **LIMA 论文**（Zhou et al., 2023）证明仅用 1000 条高质量数据就能训练出接近 GPT-4 水平的对话模型
- **Alpaca 方法**：使用 GPT-4 生成 52K 条指令数据，成本低但质量参差不齐
- **Vicuna 方法**：使用 ShareGPT 上的用户-GPT 对话数据（70K 条），质量较高因为经过了真实用户的筛选

数据质量的关键维度：

| 维度 | 说明 | 影响 |
|------|------|------|
| 正确性 | 答案是否事实正确 | 最关键 |
| 信息量 | 回答是否详尽有深度 | 高 |
| 格式多样性 | 是否覆盖多种输出格式 | 中 |
| 任务多样性 | 是否覆盖广泛的任务类型 | 高 |
| 难度分布 | 是否包含有挑战性的问题 | 中 |

### Overfitting Prevention
SFT 数据量通常较小（数千到数万条），极易过拟合。防护策略包括：

- **Early Stopping（早停）**：通过验证集损失监控，在过拟合前停止训练。通常 SFT 只需要 1-3 个 epoch
- **Low Learning Rate（低学习率）**：SFT 学习率通常比预训练低一个数量级，如 $2 \times 10^{-5}$
- **Weight Decay（权重衰减）**：通常设为 0.01-0.1，防止权重过大
- **Dropout（随机失活）**：部分工作表明在 SFT 阶段重新开启 dropout 可以缓解过拟合
- **Data Augmentation（数据增强）**：通过改写指令、变换格式等方式扩充数据

### SFT 训练目标
SFT 的训练目标与预训练相同——最小化负对数似然，但仅在响应 token 上计算：

$$\mathcal{L}_{\text{SFT}} = -\sum_{t \in \text{response}} \log P(x_t | x_{<t}; \theta)$$

其中响应 token 的范围由特殊 token 标记确定。这一选择性损失计算的直觉是：模型应该学会根据指令生成高质量的回答，而不是学会预测指令本身。

### NEFTune
**NEFTune (Noisy Embedding Fine-Tuning，噪声嵌入微调)** 是一种简单有效的正则化技术，在训练时向输入嵌入中添加均匀噪声：

$$\tilde{e} = e + \frac{\alpha}{\sqrt{Ld}} \cdot U(-1, 1)$$

其中 $L$ 是序列长度，$d$ 是嵌入维度，$\alpha$ 是噪声强度（通常设为 5-15）。NEFTune 在多个基准测试上显著提升了 SFT 模型的性能，可能是因为它帮助模型避免了对训练数据表面模式的过度记忆。

### Packing vs Padding
为了高效利用 GPU 计算，训练数据需要进行批处理。两种主要策略：

- **Padding（填充）**：将短序列填充到最大长度。简单但浪费计算
- **Packing（打包）**：将多个短样本拼接成一个长序列，使用特殊分隔 token。需要使用注意力掩码确保不同样本之间不会相互关注

## Implementation

```python
# SFT 训练的完整示例
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 格式化指令数据
def format_instruction(sample):
    return f"""### Instruction:
{sample['instruction']}

### Response:
{sample['response']}"""

# 训练配置
training_args = TrainingArguments(
    output_dir="./sft-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-5,
    warmup_ratio=0.03,
    weight_decay=0.01,
    bf16=True,
    logging_steps=10,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    formatting_func=format_instruction,
    max_seq_length=2048,
    args=training_args,
    neftune_noise_alpha=5,  # NEFTune 正则化
)
trainer.train()
```

## Interview Tips
- 理解为什么 SFT 中数据质量比数量更重要，能够引用 LIMA 等论文
- 掌握 Loss Masking 的原理和实现
- 能够列举并解释常用的过拟合防护策略
- 了解 Packing vs Padding 的权衡和实现细节
- 能够描述 SFT 在 LLM 对齐流水线中的角色
"""

# ============================================================
# Node 153: RLHF
# ============================================================
translations[153] = r"""# RLHF (Reinforcement Learning from Human Feedback)

## Overview
**RLHF (Reinforcement Learning from Human Feedback，基于人类反馈的强化学习)** 通过人类偏好信号将 LLM 的输出与人类价值观对齐。它超越了 SFT 的能力边界——SFT 教会模型"如何回答"，而 RLHF 教会模型"如何回答得更好"。RLHF 是 ChatGPT 成功的关键技术之一。

近年来，**DPO (Direct Preference Optimization，直接偏好优化)** 作为 RLHF 的简化替代方案获得了广泛关注。理解 RLHF 和 DPO 的原理及权衡，是 LLM 面试的高频考点。

## Core Concepts

### RLHF Pipeline
RLHF 的标准流水线包含三个阶段：

**阶段 1：SFT** → 在指令数据上微调基座模型，获得初始策略 $\pi_{\text{SFT}}$

**阶段 2：Reward Model Training（奖励模型训练）** → 使用人类偏好数据训练奖励模型 $R_\phi$

**阶段 3：RL Optimization（强化学习优化）** → 使用 PPO 优化策略模型，最大化奖励

### Reward Model Training
奖励模型学习人类的偏好。训练数据的格式为：给定一个提示 $x$，人类标注员对多个回答进行排序（通常是成对比较 $y_w \succ y_l$，即 $y_w$ 优于 $y_l$）。

奖励模型的训练目标基于 **Bradley-Terry Model（Bradley-Terry模型）**：

$$\mathcal{L}_{\text{RM}} = -\mathbb{E}_{(x, y_w, y_l)} \left[\log \sigma(R_\phi(x, y_w) - R_\phi(x, y_l))\right]$$

其中 $\sigma$ 是 sigmoid 函数。这个损失函数鼓励奖励模型给 preferred（被偏好的）回答更高的分数。

奖励模型的关键设计考虑：
- 通常使用与策略模型相同大小或更小的模型
- 需要高质量的人类标注数据（通常需要数万条偏好对）
- **Inter-annotator Agreement（标注者一致性）** 对奖励模型质量至关重要

### PPO Optimization
**PPO (Proximal Policy Optimization，近端策略优化)** 是 RLHF 中最常用的 RL 算法。优化目标为：

$$\max_{\pi_\theta} \mathbb{E}_{x \sim D, y \sim \pi_\theta(y|x)} \left[R_\phi(x, y) - \beta \cdot \text{KL}[\pi_\theta(y|x) \| \pi_{\text{ref}}(y|x)]\right]$$

其中：
- $R_\phi(x, y)$ 是奖励模型给出的分数
- $\beta \cdot \text{KL}[\cdot]$ 是 **KL Penalty（KL 惩罚项）**，防止策略偏离 SFT 模型太远
- $\pi_{\text{ref}}$ 通常是 SFT 模型的冻结副本

PPO 的 clipped objective：

$$L^{\text{CLIP}} = \mathbb{E}\left[\min\left(\frac{\pi_\theta}{\pi_{\text{old}}} A_t, \text{clip}\left(\frac{\pi_\theta}{\pi_{\text{old}}}, 1-\epsilon, 1+\epsilon\right) A_t\right)\right]$$

其中 $A_t$ 是优势函数估计，$\epsilon$ 是裁剪范围（通常 0.2）。PPO 通过裁剪来限制每次更新的幅度，提高训练稳定性。

### RLHF 的挑战
RLHF 的工程复杂度很高：
- 需要同时维护 4 个模型：策略模型、参考模型、奖励模型、价值模型
- **Reward Hacking（奖励攻击）**：策略模型可能找到"欺骗"奖励模型的方式，获得高奖励但人类评价差
- 超参数敏感：$\beta$（KL 系数）的选择至关重要，太大则更新不足，太小则分布偏移严重
- 训练不稳定：RL 训练本身就比监督学习更不稳定

### DPO (Direct Preference Optimization)
**DPO（直接偏好优化）**（Rafailov et al., 2023）绕过了显式的奖励模型和 RL 优化，直接从偏好数据中优化策略模型：

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(x, y_w, y_l)} \left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)\right]$$

DPO 的核心洞见是：存在一个从最优策略到奖励函数的闭式映射。因此可以将 RL 问题转化为等价的监督学习问题。

### RLHF vs DPO Comparison

| 维度 | RLHF (PPO) | DPO |
|------|-----------|-----|
| 复杂度 | 高（4 个模型） | 低（2 个模型） |
| 稳定性 | 较低 | 较高 |
| 内存需求 | 高 | 较低 |
| 在线学习 | 支持 | 不支持（离线） |
| 奖励模型 | 需要显式训练 | 隐式学习 |
| 大规模表现 | 通常更好 | 可能有分布偏移 |
| 工程难度 | 高 | 低 |

DPO 的主要局限是它是 **Offline（离线）** 方法——使用固定的偏好数据，无法像 PPO 那样在训练过程中探索新的回答并获取反馈。一些改进方案如 **Online DPO** 和 **IPO (Identity Preference Optimization)** 试图解决这些问题。

### Beyond RLHF: 其他对齐方法
- **RLAIF (RL from AI Feedback，基于AI反馈的强化学习)**：用 AI 代替人类提供偏好标注
- **Constitutional AI (CAI，宪法AI)**：模型自我改进，根据一组原则评价和修正自己的回答
- **KTO (Kahneman-Tversky Optimization)**：不需要成对比较数据，只需标记回答为"好"或"差"
- **ORPO (Odds Ratio Preference Optimization)**：将 SFT 和偏好对齐合并为单阶段训练

## Implementation

```python
# DPO 训练示例
from trl import DPOTrainer, DPOConfig

# 偏好数据格式
# {"prompt": "...", "chosen": "...", "rejected": "..."}

dpo_config = DPOConfig(
    beta=0.1,                    # KL 惩罚系数
    learning_rate=5e-7,          # 较低的学习率
    per_device_train_batch_size=4,
    num_train_epochs=1,
    bf16=True,
    loss_type="sigmoid",         # 标准 DPO 损失
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,         # 冻结的 SFT 模型
    train_dataset=preference_data,
    tokenizer=tokenizer,
    args=dpo_config,
)
trainer.train()
```

## Interview Tips
- 能够完整描述 RLHF 三阶段流水线
- 理解 DPO 损失函数的推导直觉及其与 RLHF 的等价关系
- 掌握 Reward Hacking 问题及 KL 惩罚的作用
- 能够比较 RLHF 和 DPO 的优缺点及适用场景
- 了解 RLAIF、Constitutional AI 等替代方案
"""

# ============================================================
# Node 154: LoRA/QLoRA
# ============================================================
translations[154] = r"""# Parameter-Efficient Fine-Tuning (LoRA, QLoRA)

## Overview
**PEFT (Parameter-Efficient Fine-Tuning，参数高效微调)** 通过仅更新少量参数来适配大语言模型，避免了全参数微调的巨大成本。**LoRA (Low-Rank Adaptation，低秩适配)** 是最流行的 PEFT 方法，而 **QLoRA (Quantized LoRA，量化低秩适配)** 进一步结合量化技术，使得在消费级 GPU 上微调大模型成为可能。

在面试中，PEFT 方法的原理、设计选择和实际应用是高频考点。理解 LoRA 的数学基础和工程实践，对于 LLM 微调任务至关重要。

## Core Concepts

### LoRA Core Idea
LoRA 的核心假设是：微调过程中的权重更新矩阵 $\Delta W$ 具有低秩结构。因此可以将 $\Delta W$ 分解为两个小矩阵的乘积：

$$W' = W + \Delta W = W + BA$$

其中：
- $W \in \mathbb{R}^{d \times k}$ 是冻结的原始权重
- $B \in \mathbb{R}^{d \times r}$ 是下投影矩阵（初始化为零）
- $A \in \mathbb{R}^{r \times k}$ 是上投影矩阵（随机初始化）
- $r \ll \min(d, k)$ 是 **Rank（秩）**，通常 $r \in \{4, 8, 16, 32, 64\}$

参数量从 $d \times k$ 降低到 $r \times (d + k)$。例如，对于 $d = k = 4096, r = 16$，参数量从 16.7M 降低到 131K（减少 99.2%）。

训练时使用缩放因子 $\alpha$：

$$h = Wx + \frac{\alpha}{r} BAx$$

$\frac{\alpha}{r}$ 用于控制低秩更新的幅度。通常 $\alpha$ 设为 $r$ 的两倍（如 $r = 16, \alpha = 32$），这样缩放因子为 2。

### Rank Selection
秩 $r$ 的选择对性能和效率有重要影响：

| Rank $r$ | 训练参数占比 | 性能 | 适用场景 |
|----------|-------------|------|----------|
| 4 | ~0.1% | 基础 | 简单分类任务 |
| 8-16 | ~0.2-0.5% | 良好 | 大多数场景 |
| 32-64 | ~1-2% | 接近全量 | 复杂生成任务 |
| 128+ | ~3-5% | ≈全量 | 追求最优性能 |

经验法则：
- 先用 $r = 16$ 作为基线
- 如果性能不足，增加 $r$ 或扩展 LoRA 到更多模块
- **Target Modules（目标模块）**：通常对 $W_Q, W_K, W_V, W_O$（注意力权重）应用 LoRA，有时也包括 FFN 权重

### QLoRA
**QLoRA（量化低秩适配）**（Dettmers et al., 2023）通过三项关键创新使得在单张 48GB GPU 上微调 65B 模型成为可能：

**4-bit NormalFloat (NF4)**：一种信息理论最优的量化数据类型，假设权重服从正态分布。NF4 将权重量化为 4 位，相比标准 INT4 量化在精度上有显著提升。

**Double Quantization（双重量化）**：对量化参数本身也进行量化，进一步节省内存。第一次量化将 FP32 权重→NF4，第二次量化将量化的缩放因子从 FP32→FP8。

**Paged Optimizers（分页优化器）**：利用 CUDA 统一内存在 CPU 和 GPU 之间分页，处理内存峰值。

QLoRA 的内存节省：

$$\text{Memory}_{\text{QLoRA}} \approx \frac{N}{2} \text{ bytes} + \text{LoRA params} \times 2 \text{ bytes}$$

其中 $N$ 是总参数量。一个 70B 模型需要约 35GB（4-bit）+ LoRA 开销，可以在单张 80GB GPU 上运行。

### Adapter Merging
LoRA 训练完成后，可以将适配器权重合并回原始模型：

$$W_{\text{merged}} = W + \frac{\alpha}{r} BA$$

合并后的模型在推理时没有任何额外开销。还可以维护多个 LoRA 适配器用于不同任务，在推理时动态加载。

多适配器管理策略：
- **LoRA Serving（LoRA服务）**：一个基础模型 + 多个 LoRA 适配器，根据请求动态切换
- **Adapter Composition（适配器组合）**：将多个 LoRA 的权重线性组合
- **Task Arithmetic（任务算术）**：通过加减 LoRA 权重实现任务能力的组合和消除

### Other PEFT Methods
除 LoRA 外的其他参数高效方法：

- **Prefix Tuning（前缀微调）**：在每层注意力的键值前添加可学习的前缀向量
- **Prompt Tuning（提示微调）**：仅在输入嵌入前添加可学习的软提示
- **IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations)**：通过可学习的缩放向量调节注意力和 FFN 的激活值，参数量比 LoRA 更少
- **DoRA (Weight-Decomposed Low-Rank Adaptation)**：将权重分解为方向和大小，分别用 LoRA 和可学习标量调节

## Implementation

```python
# LoRA 微调示例
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.bfloat16,
)

# LoRA 配置
lora_config = LoraConfig(
    r=16,                          # 秩
    lora_alpha=32,                 # 缩放因子
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# 输出: trainable params: 39.98M || all params: 6.78B || trainable%: 0.59%

# QLoRA 配置
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",      # NF4 量化类型
    bnb_4bit_use_double_quant=True,  # 双重量化
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model_4bit = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)
model_4bit = get_peft_model(model_4bit, lora_config)
```

## Interview Tips
- 能够推导 LoRA 的参数量节省比例
- 理解秩 $r$ 和缩放因子 $\alpha$ 的选择策略
- 掌握 QLoRA 的三项创新（NF4、双重量化、分页优化器）
- 能够比较 LoRA 与其他 PEFT 方法的优缺点
- 了解多适配器管理和推理时的动态加载策略
"""

# ============================================================
# Node 155: LLM Evaluation
# ============================================================
translations[155] = r"""# LLM Evaluation & Benchmarks

## Overview
**LLM Evaluation（大语言模型评估）** 是衡量模型能力和质量的系统方法。随着 LLM 能力的快速提升，评估方法也在不断演进——从简单的 **Perplexity（困惑度）** 到多维度基准测试，再到基于人类或 AI 的对抗评估。

在面试中，候选人需要理解主流基准测试的设计原理、局限性，以及如何设计合理的评估方案来衡量特定场景下的模型表现。

## Core Concepts

### Perplexity
**Perplexity（困惑度）** 是语言模型最基础的评估指标，衡量模型对测试集的预测不确定性：

$$\text{PPL} = \exp\left(-\frac{1}{N}\sum_{i=1}^{N} \log P(x_i | x_{<i})\right)$$

困惑度越低表示模型对文本的预测越准确。直觉上，PPL 为 $k$ 意味着模型在预测下一个 token 时平均面临 $k$ 个等概率的选择。

困惑度的局限性：
- 不同分词器的困惑度不可直接比较（token 定义不同）
- 低困惑度不等于生成质量好（模型可能只是擅长记忆训练分布）
- 无法评估指令跟随、安全性等高级能力

### MMLU
**MMLU (Massive Multitask Language Understanding，大规模多任务语言理解)** 覆盖 57 个学科领域的多选题测试，包括：

- **STEM**：数学、物理、计算机科学、工程
- **人文**：历史、哲学、法律
- **社会科学**：经济学、心理学、政治学
- **其他**：医学、会计、专业执照考试

评估方式通常为 5-shot，即在提示中提供 5 个示例后让模型回答。MMLU 的得分范围是 25%（随机猜测）到 100%。GPT-4 达到约 86%，而人类专家平均约 89%。

### HumanEval
**HumanEval** 是 OpenAI 提出的代码生成基准，包含 164 个编程题目。评估指标为 **pass@k**：

$$\text{pass@k} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$

其中 $n$ 是生成的代码样本总数，$c$ 是通过所有测试用例的样本数。pass@1 衡量一次生成即正确的概率，pass@10 允许模型生成 10 次取最好的。

扩展基准：**MBPP (Mostly Basic Programming Problems)**、**SWE-bench**（真实 GitHub issue 修复）。

### MT-Bench
**MT-Bench（多轮对话基准）** 使用 GPT-4 作为评判，评估模型在 8 个能力维度上的多轮对话质量：

- Writing（写作）、Roleplay（角色扮演）、Reasoning（推理）
- Math（数学）、Coding（编程）、Extraction（信息提取）
- STEM、Humanities（人文）

评分从 1 到 10，采用 **Pairwise Comparison（成对比较）** 或 **Single Rating（单项评分）** 模式。MT-Bench 的优势是评估了指令跟随和对话能力，更接近真实使用场景。

### Chatbot Arena (LMSYS)
**Chatbot Arena（聊天机器人竞技场）** 采用 **Elo Rating（Elo评分系统）** 进行匿名对战：

- 用户提交问题，两个匿名模型同时回答
- 用户投票选择更好的回答
- 基于投票结果更新 Elo 分数

这是目前最受信赖的 LLM 排名系统，因为它：
- 反映真实用户的偏好
- 匿名避免了品牌偏见
- 大量投票保证了统计可靠性

### Contamination Issues
**Data Contamination（数据污染）** 是 LLM 评估的核心挑战：

- 基准测试数据可能出现在预训练语料中，导致分数虚高
- 模型可能"见过"测试题目而非真正理解
- 检测方法：**n-gram overlap analysis**、**membership inference**、在发布前保密的测试集上评估

应对策略：
- 使用 **Dynamic Benchmarks（动态基准）**：定期更新测试题目
- **Private Test Sets（私密测试集）**：不公开测试数据
- **Canary Strings（金丝雀字符串）**：在测试集中嵌入唯一标记，检测是否被抓取

### Comprehensive Evaluation Framework
现代 LLM 评估通常需要多维度评估框架：

| 维度 | 指标 | 基准 |
|------|------|------|
| 知识 | 准确率 | MMLU, ARC |
| 推理 | 准确率 | GSM8K, BBH |
| 编码 | pass@k | HumanEval, MBPP |
| 对话 | 人类/AI评分 | MT-Bench, Arena |
| 安全 | 拒绝率/攻击成功率 | TruthfulQA, AdvBench |
| 长文本 | 准确率 | RULER, InfiniteBench |

## Implementation

```python
# 使用 lm-evaluation-harness 进行评估
# pip install lm-eval
import lm_eval

results = lm_eval.simple_evaluate(
    model="hf",
    model_args="pretrained=meta-llama/Llama-2-7b-hf",
    tasks=["mmlu", "hellaswag", "arc_challenge"],
    num_fewshot=5,
    batch_size=8,
)

# 自定义评估指标
def compute_pass_at_k(n, c, k):
    """计算 pass@k 指标"""
    from math import comb
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)
```

## Interview Tips
- 理解不同评估指标的适用场景和局限性
- 掌握数据污染问题的检测和应对方法
- 能够为特定应用场景设计合理的评估方案
- 了解 Chatbot Arena 的 Elo 评分机制
- 能够解释 pass@k 指标的含义和计算方法
"""

# ============================================================
# Node 156: KV Cache & PagedAttention
# ============================================================
translations[156] = r"""# KV Cache & PagedAttention

## Overview
**KV Cache (Key-Value Cache，键值缓存)** 是自回归推理的核心优化，通过缓存已计算的 Key 和 Value 向量避免重复计算。**PagedAttention（分页注意力）** 将操作系统的虚拟内存管理思想引入 KV cache 管理，解决了内存碎片化问题。

在 LLM 推理中，KV cache 通常占据 GPU 显存的主要部分。理解 KV cache 的内存计算和优化方法，是 LLM 服务系统设计面试的必考内容。

## Core Concepts

### KV Cache Mechanism
在自回归生成中，每次生成新 token 时都需要对所有之前的 token 计算注意力。如果不缓存，每步都要重新计算所有 token 的 Key 和 Value，导致 $O(n^2)$ 的冗余计算。

KV Cache 保存了每一层、每个注意力头的 Key 和 Value 张量。生成新 token 时，只需计算新 token 的 Q, K, V，然后将新的 K, V 追加到缓存中。

### KV Cache Memory Calculation
KV Cache 的内存占用公式：

$$\text{Memory}_{\text{KV}} = 2 \times n_{\text{layers}} \times d_{\text{model}} \times \text{seq\_len} \times \text{batch} \times \text{bytes\_per\_element}$$

因子 2 表示 Key 和 Value 各一份。以 LLaMA-2 70B 为例（$n_{\text{layers}} = 80$，$d_{\text{model}} = 8192$）：

| 序列长度 | Batch Size | BF16 KV Cache 大小 |
|----------|------------|-------------------|
| 2048 | 1 | 5.2 GB |
| 4096 | 1 | 10.5 GB |
| 4096 | 8 | 83.9 GB |
| 8192 | 16 | 335 GB |

可以看到，长序列和大批量下 KV cache 很快成为瓶颈。对于 GQA 模型，KV cache 按 KV 头数（而非查询头数）计算，因此使用 GQA 的 LLaMA-2 70B（8 个 KV 头 vs 64 个查询头）将 KV cache 减少了 8 倍。

### KV Cache Optimization Techniques
除 PagedAttention 外的优化方法：

- **Multi-Query Attention (MQA，多查询注意力)**：所有查询头共享一组 KV 头
- **Grouped-Query Attention (GQA，分组查询注意力)**：MQA 和 MHA 之间的折中
- **KV Cache Compression（KV缓存压缩）**：使用量化（FP16→INT8/INT4）压缩缓存值
- **Sliding Window（滑动窗口）**：只保留最近 $W$ 个 token 的 KV cache（Mistral）
- **Token Pruning（Token剪枝）**：根据注意力分数丢弃不重要的 token

### PagedAttention
**PagedAttention（分页注意力）**（vLLM, Kwon et al., 2023）借鉴操作系统的 **Virtual Memory（虚拟内存）** 和 **Paging（分页）** 机制：

传统的 KV cache 为每个请求预分配连续的最大长度内存，导致：
- **Internal Fragmentation（内部碎片）**：实际序列远短于最大长度，浪费已分配的空间
- **External Fragmentation（外部碎片）**：频繁的分配释放导致不连续的空闲空间

PagedAttention 的解决方案：
- 将 KV cache 分成固定大小的 **Block（块）**，每个 block 存储固定数量 token 的 KV 向量
- 使用 **Block Table（块表）** 映射逻辑位置到物理 block（类似页表）
- 按需分配：只在生成新 token 时分配新 block
- 非连续存储：物理 block 不需要连续，通过块表间接寻址

### Prefix Caching
**Prefix Caching（前缀缓存）** 利用多个请求共享相同前缀的特点：

- 系统提示（System Prompt）对所有请求相同
- 同一轮对话中的上下文前缀相同
- **Automatic Prefix Caching（自动前缀缓存）**：使用前缀的哈希值作为键，自动检测和复用共享前缀的 KV cache

这可以显著减少 **TTFT (Time To First Token，首token延迟)**，因为共享前缀部分不需要重新计算。

### Memory Efficiency Analysis
PagedAttention 将 KV cache 的内存利用率从约 20-40% 提升到接近 100%：

$$\text{Waste}_{\text{traditional}} = \text{max\_seq\_len} - \text{actual\_len} \quad \text{(per request)}$$
$$\text{Waste}_{\text{paged}} \leq \text{block\_size} - 1 \quad \text{(per request)}$$

例如，最大序列长度 2048，实际平均长度 512 时：
- 传统方式浪费 75% 内存
- PagedAttention 浪费 < 1%（block size = 16 时）

## Implementation

```python
# PagedAttention 核心数据结构
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class KVBlock:
    """KV cache 的物理块"""
    block_id: int
    tokens: List[int]        # 存储的 token IDs
    kv_data: torch.Tensor    # shape: [num_layers, 2, block_size, head_dim]
    ref_count: int = 0       # 引用计数（用于 copy-on-write）

class BlockAllocator:
    """块分配器 - 管理物理 KV cache 块"""
    def __init__(self, num_blocks, block_size):
        self.free_blocks = list(range(num_blocks))
        self.block_size = block_size

    def allocate(self) -> int:
        if not self.free_blocks:
            raise MemoryError("KV cache blocks exhausted")
        return self.free_blocks.pop()

    def free(self, block_id: int):
        self.free_blocks.append(block_id)

class BlockTable:
    """块表 - 逻辑到物理的映射"""
    def __init__(self):
        self.table: List[int] = []  # 逻辑 block index → 物理 block id

    def append_block(self, physical_block_id: int):
        self.table.append(physical_block_id)

    def get_physical_block(self, logical_idx: int) -> int:
        return self.table[logical_idx]
```

## Interview Tips
- 能够推导 KV cache 的内存占用公式并计算具体场景
- 理解 PagedAttention 与操作系统虚拟内存的类比
- 掌握内部碎片和外部碎片的概念及 PagedAttention 如何解决
- 了解 Prefix Caching 的工作原理及对 TTFT 的影响
- 能够比较不同 KV cache 优化方法的适用场景
"""

# ============================================================
# Node 157: Quantization
# ============================================================
translations[157] = r"""# Quantization (GPTQ, AWQ, FP8)

## Overview
**Quantization（量化）** 通过降低模型权重和激活值的数值精度来减少模型大小和推理计算量。对于大语言模型而言，量化使得原本需要多张高端 GPU 才能运行的模型可以在单张 GPU 甚至消费级硬件上部署。

主流的 LLM 量化方法包括 **GPTQ (GPT Quantization)**、**AWQ (Activation-Aware Weight Quantization，激活感知权重量化)**、**SmoothQuant（平滑量化）** 和 **FP8 训练**。理解这些方法的原理和权衡是 LLM 部署面试的核心内容。

## Core Concepts

### Quantization Basics
量化将高精度数值映射到低精度表示。**Uniform Quantization（均匀量化）** 的基本公式：

$$x_q = \text{round}\left(\frac{x}{s}\right) + z, \quad \hat{x} = s \cdot (x_q - z)$$

其中 $s$ 是缩放因子，$z$ 是零点。量化位数决定了可表示的值的数量：$n$ 位可以表示 $2^n$ 个不同的值。

| 精度 | 位数 | 每参数字节 | 70B模型大小 |
|------|------|-----------|------------|
| FP32 | 32 | 4 | 280 GB |
| FP16/BF16 | 16 | 2 | 140 GB |
| FP8 | 8 | 1 | 70 GB |
| INT4 | 4 | 0.5 | 35 GB |

### GPTQ
**GPTQ** 基于 **Optimal Brain Quantization (OBQ)** 框架，使用 Hessian 信息进行逐层量化。其核心目标是最小化量化引起的输出误差：

$$\min_{\hat{W}} \|WX - \hat{W}X\|^2$$

其中 $W$ 是原始权重，$\hat{W}$ 是量化后的权重，$X$ 是该层的校准数据输入。

GPTQ 的关键步骤：
1. 收集少量校准数据（通常 128 个样本）通过模型
2. 对每一层，使用 Hessian 矩阵 $H = 2XX^T$ 确定每列权重的量化顺序
3. 量化一列权重后，通过 **Cholesky 分解** 将量化误差分配给未量化的列
4. **Lazy Batch（惰性批处理）**：每次处理 128 列以提高效率

GPTQ 可以在几分钟到几小时内将模型量化到 4-bit 或 3-bit，质量损失很小。它是目前最广泛使用的 PTQ 方法之一。

### AWQ
**AWQ (Activation-Aware Weight Quantization，激活感知权重量化)** 的核心观察是：并非所有权重同等重要，少量"显著"权重对模型输出影响很大。

AWQ 通过分析激活值来识别重要权重通道：

$$s_j = \max_{i} |X_{:,j}|$$

激活值大的通道对应的权重更重要。AWQ 对这些重要通道进行缩放后再量化：

$$\hat{W}_j = \text{Quantize}(W_j \cdot s_j) / s_j$$

通过缩放，重要权重的有效量化精度更高。AWQ 的优势：
- 不需要反向传播或梯度信息
- 量化速度很快（几分钟）
- 在 4-bit 下通常比 GPTQ 略好

### SmoothQuant
**SmoothQuant（平滑量化）** 解决的是 **Weight-Activation Quantization（权重-激活联合量化）** 中的难题：激活值通常有 **Outlier（异常值）** 通道，这些通道的动态范围远大于其他通道，导致量化困难。

SmoothQuant 将量化难度从激活值转移到权重上：

$$Y = (X \cdot \text{diag}(s)^{-1}) \cdot (\text{diag}(s) \cdot W) = \hat{X} \cdot \hat{W}$$

缩放因子 $s$ 在激活值和权重之间分配量化难度：

$$s_j = \frac{\max |X_j|^\alpha}{\max |W_j|^{1-\alpha}}$$

其中 $\alpha \in [0, 1]$ 控制分配比例（通常 $\alpha = 0.5$）。这使得激活值和权重都可以使用 INT8 量化，实现 W8A8 的高效推理。

### FP8 Training
**FP8 (8-bit Floating Point，8位浮点)** 是新一代 GPU（H100/H200）原生支持的数据类型，分为两种格式：

- **E4M3**（4位指数+3位尾数）：范围 $\pm 240$，精度较高，适合前向传播
- **E5M2**（5位指数+2位尾数）：范围 $\pm 57344$，动态范围大，适合反向传播中的梯度

FP8 训练的关键是 **Per-tensor Dynamic Scaling（逐张量动态缩放）**：

$$x_{\text{fp8}} = \text{cast\_to\_fp8}\left(x \cdot \frac{\text{fp8\_max}}{\max|x|}\right)$$

FP8 的优势在于不需要 PTQ 流程——模型直接以 FP8 训练和推理，在 H100 上相比 BF16 可获得接近 2 倍的吞吐提升。

### Quantization Comparison

| 方法 | 类型 | 精度 | 速度 | 质量保持 | 硬件需求 |
|------|------|------|------|----------|----------|
| GPTQ | PTQ | W4 | 中等 | 好 | 通用 GPU |
| AWQ | PTQ | W4 | 快 | 较好 | 通用 GPU |
| SmoothQuant | PTQ | W8A8 | 快 | 很好 | 通用 GPU |
| FP8 | 训练/推理 | W8A8 | 最快 | 最好 | H100+ |
| GGUF/llama.cpp | PTQ | W2-W8 | 中等 | 可变 | CPU/GPU |

## Implementation

```python
# GPTQ 量化示例
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

quantize_config = BaseQuantizeConfig(
    bits=4,                    # 量化位数
    group_size=128,            # 分组大小（每组共享缩放因子）
    desc_act=True,             # 按激活值排序列
    damp_percent=0.01,         # Hessian 阻尼因子
)

# 加载模型并量化
model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantize_config=quantize_config,
)
model.quantize(calibration_data)  # 使用校准数据量化
model.save_quantized("llama2-7b-gptq-4bit")

# AWQ 量化
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
model.quantize(
    tokenizer,
    quant_config={"w_bit": 4, "q_group_size": 128, "version": "gemm"}
)
```

## Interview Tips
- 理解 GPTQ 和 AWQ 的核心区别（Hessian-based vs Activation-aware）
- 能够解释 SmoothQuant 如何解决激活值异常值问题
- 掌握不同量化方法在精度、速度和硬件兼容性上的权衡
- 了解 FP8 格式的两种变体及各自适用场景
- 能够计算不同量化精度下的模型内存占用
"""

# ============================================================
# Node 158: Continuous Batching
# ============================================================
translations[158] = r"""# Continuous Batching

## Overview
**Continuous Batching（连续批处理）** 是 LLM 推理服务系统的核心调度技术。与传统的 **Static Batching（静态批处理）** 不同——等所有请求完成后才开始新批次——连续批处理在 **Iteration Level（迭代级别）** 进行调度，允许已完成的请求立即释放资源，新请求随时加入。

这一技术显著提升了 LLM 推理的吞吐量（通常 2-5 倍），是 vLLM、TensorRT-LLM 等现代服务系统的基础。理解连续批处理的原理和实现挑战是 LLM 系统设计面试的重点。

## Core Concepts

### Static vs Continuous Batching
**Static Batching（静态批处理）** 的问题：

假设一个批次中有 4 个请求，生成长度分别为 10, 50, 20, 100 token。静态批处理必须等最长的请求（100 token）完成后才能处理新请求。前 3 个请求完成后继续占用 GPU 资源，浪费了大量计算。

**Continuous Batching（连续批处理）** 的解决方案：
- 每生成一个 token 后检查是否有请求完成
- 已完成的请求立即释放资源
- 等待队列中的新请求立即加入当前批次
- GPU 利用率始终保持在高水平

### Prefill vs Decode Phases
LLM 推理包含两个性质完全不同的阶段：

**Prefill（预填充）阶段**：
- 一次性处理输入 prompt 的所有 token
- **Compute-bound（计算密集型）**：大量矩阵乘法
- 计算量大但只执行一次
- 生成第一个输出 token

**Decode（解码）阶段**：
- 每步生成一个新 token
- **Memory-bound（内存密集型）**：主要瓶颈是 KV cache 的读取
- 每步只处理一个 token，计算量小但需要读取大量 KV cache
- 重复执行直到生成结束

这两个阶段的计算特性差异带来了调度挑战：

$$\text{Arithmetic Intensity}_{\text{prefill}} \gg \text{Arithmetic Intensity}_{\text{decode}}$$

将 prefill 和 decode 混在一个批次中会导致 decode 请求的延迟显著增加（prefill 的大量计算阻塞了 decode）。

### Iteration-Level Scheduling
**Iteration-level Scheduling（迭代级调度）** 是连续批处理的核心机制：

```
Iteration 1: [Req1-decode, Req2-decode, Req3-prefill]
Iteration 2: [Req1-decode, Req2-decode, Req3-decode, Req4-prefill]
Iteration 3: [Req1-EOS,    Req2-decode, Req3-decode, Req4-decode]
Iteration 4: [Req5-prefill, Req2-decode, Req3-decode, Req4-decode]
```

每次迭代后，调度器检查：
- 哪些请求已完成（生成了 EOS token 或达到最大长度）
- 是否有资源（GPU 内存、KV cache）容纳新请求
- 新请求的 prefill 是否会影响当前 decode 请求的延迟 SLA

### Preemption Strategies
当 GPU 内存不足以容纳所有活跃请求时，需要 **Preemption（抢占）** 策略：

- **Swapping（换出）**：将被抢占请求的 KV cache 从 GPU 转移到 CPU 内存，待有空间时换回
- **Recomputation（重计算）**：丢弃被抢占请求的 KV cache，后续重新计算。如果 prefill 成本低于 swap I/O 成本，这可能更高效
- **Priority-based（基于优先级）**：根据请求优先级、等待时间或已生成长度决定抢占顺序

### Chunked Prefill
**Chunked Prefill（分块预填充）** 将长 prompt 的 prefill 分成多个块执行：

- 避免单个长 prefill 阻塞所有 decode 请求
- 每个块大小可调（如 512 token），在 prefill 吞吐和 decode 延迟之间取得平衡
- 分块的 prefill 可以与其他请求的 decode 交替执行

### Disaggregated Prefill & Decode
**Disaggregated Serving（解耦服务）** 将 prefill 和 decode 分配到不同的硬件上：

- **Prefill 节点**：优化计算吞吐量，使用高算力 GPU
- **Decode 节点**：优化内存带宽，使用高内存带宽配置
- 通过高速网络传输 KV cache

这种架构避免了 prefill 和 decode 之间的资源竞争，两个阶段都能获得最优的硬件配置。

### Throughput Analysis
连续批处理的吞吐量优势可以通过数学分析说明：

$$\text{Throughput}_{\text{static}} = \frac{\text{batch\_size}}{\max_i(\text{gen\_len}_i) \times t_{\text{step}}}$$

$$\text{Throughput}_{\text{continuous}} = \frac{\text{batch\_size}}{\text{avg}(\text{gen\_len}_i) \times t_{\text{step}}}$$

当生成长度方差很大时（常见于对话场景），连续批处理的优势尤其明显。

## Implementation

```python
# 连续批处理调度器的简化实现
from collections import deque
from enum import Enum

class RequestState(Enum):
    WAITING = "waiting"
    PREFILL = "prefill"
    DECODE = "decode"
    FINISHED = "finished"

class Request:
    def __init__(self, prompt_tokens, max_gen_len):
        self.prompt_tokens = prompt_tokens
        self.generated_tokens = []
        self.max_gen_len = max_gen_len
        self.state = RequestState.WAITING

class ContinuousBatchScheduler:
    def __init__(self, max_batch_size, max_kv_blocks):
        self.max_batch_size = max_batch_size
        self.max_kv_blocks = max_kv_blocks
        self.running: list[Request] = []
        self.waiting: deque[Request] = deque()

    def schedule_iteration(self):
        """每次迭代的调度决策"""
        # 1. 移除已完成的请求
        self.running = [r for r in self.running if r.state != RequestState.FINISHED]

        # 2. 尝试加入等待队列中的请求
        while (self.waiting and
               len(self.running) < self.max_batch_size and
               self._has_kv_space()):
            new_req = self.waiting.popleft()
            new_req.state = RequestState.PREFILL
            self.running.append(new_req)

        return self.running
```

## Interview Tips
- 能够清晰对比静态批处理和连续批处理的效率差异
- 理解 prefill 和 decode 阶段的计算特性差异
- 掌握抢占策略的权衡（swap vs recompute）
- 能够解释 chunked prefill 如何平衡 TTFT 和 TPOT
- 了解 disaggregated serving 架构的动机和实现
"""

# ============================================================
# Node 159: Serving Systems vLLM/TRT-LLM
# ============================================================
translations[159] = r"""# Serving Systems (vLLM, TensorRT-LLM)

## Overview
**LLM Serving Systems（大语言模型服务系统）** 是将 LLM 部署到生产环境的关键基础设施。**vLLM** 通过 **PagedAttention（分页注意力）** 革新了内存管理，**TensorRT-LLM** 利用 NVIDIA 的深度编译优化实现了极致的推理性能，而 **Speculative Decoding（推测解码）** 等技术则从算法层面加速了生成速度。

在面试中，候选人需要理解主流服务系统的架构设计、性能优化策略和部署权衡。

## Core Concepts

### vLLM Architecture
**vLLM**（Kwon et al., 2023）的核心创新是 PagedAttention，其整体架构：

- **Scheduler（调度器）**：实现连续批处理，管理请求生命周期
- **Block Manager（块管理器）**：管理 KV cache 的物理块分配
- **Worker（工作进程）**：执行模型推理，可跨多 GPU
- **API Server（API服务器）**：提供 OpenAI 兼容的 HTTP 接口

vLLM 的性能优势来源：
1. PagedAttention 消除内存碎片，提升有效批量
2. 连续批处理提升 GPU 利用率
3. 前缀缓存避免重复计算
4. Tensor Parallelism 支持大模型

### TensorRT-LLM
**TensorRT-LLM** 是 NVIDIA 的 LLM 推理引擎，结合了图编译优化和 LLM 特定的内核：

- **Graph Compilation（图编译）**：将模型计算图编译为高度优化的 CUDA 内核
- **Kernel Fusion（算子融合）**：将多个算子合并为单个 CUDA 内核，减少内存访问
- **Custom Attention Kernels（自定义注意力内核）**：针对不同注意力模式（MHA/GQA/MQA）优化的 CUDA 实现
- **In-flight Batching（在途批处理）**：TensorRT-LLM 对连续批处理的实现
- **Quantization Support（量化支持）**：原生支持 FP8、INT4（AWQ/GPTQ）量化

TensorRT-LLM 通常比 vLLM 有 20-50% 的推理速度优势，但灵活性较低，模型支持范围较窄。

### Speculative Decoding
**Speculative Decoding（推测解码）** 利用一个小型 **Draft Model（草稿模型）** 快速生成候选 token，然后由大型 **Target Model（目标模型）** 并行验证：

1. 草稿模型自回归生成 $\gamma$ 个候选 token（快速但不够准确）
2. 目标模型一次前向传播验证所有 $\gamma$ 个 token（并行验证）
3. 接受前 $k$ 个匹配的 token，拒绝后续不匹配的

接受率 $\gamma$ 的计算：

$$P(\text{accept } t_i) = \min\left(1, \frac{p_{\text{target}}(t_i)}{p_{\text{draft}}(t_i)}\right)$$

这确保了推测解码与纯目标模型解码生成 **完全相同的分布**——不会损失任何质量。

速度提升：
$$\text{Speedup} \approx \frac{\gamma + 1}{1 + \gamma \cdot c_{\text{draft}} / c_{\text{target}}}$$

当草稿模型比目标模型小很多且接受率高时，可以获得 2-3 倍加速。

### Speculative Decoding Variants
- **Self-speculative（自推测）**：使用目标模型的部分层作为草稿模型，无需额外模型
- **Medusa（美杜莎）**：在目标模型顶部添加多个预测头，同时预测多个未来 token
- **Eagle**：使用特征级别的推测，预测特征向量而非 token
- **Lookahead Decoding（前瞻解码）**：利用 Jacobi 迭代并行生成多个 token

### Disaggregated Serving
**Disaggregated Serving（解耦服务）** 将 prefill 和 decode 分离到不同的硬件池：

| 阶段 | 特性 | 最优硬件 |
|------|------|----------|
| Prefill | 计算密集 | 高FLOPS GPU (H100 SXM) |
| Decode | 内存密集 | 高带宽内存 (HBM3) |

通过 **RDMA（远程直接内存访问）** 或 **NVLink** 在节点间传输 KV cache。这种架构的优势是每个阶段都能获得最优的资源配置，缺点是增加了系统复杂度和网络延迟。

### Performance Metrics
LLM 服务系统的关键性能指标：

| 指标 | 定义 | 目标 |
|------|------|------|
| **TTFT** | 首 token 延迟 | < 500ms |
| **TPOT** | 每 token 生成延迟 | < 50ms |
| **Throughput** | 每秒生成 token 数 | 最大化 |
| **P99 Latency** | 99分位延迟 | SLA 合规 |
| **GPU Utilization** | GPU 利用率 | > 80% |

### System Selection Guide

| 场景 | 推荐系统 | 原因 |
|------|----------|------|
| 快速原型 | vLLM | 易用性好，模型支持广 |
| 最大吞吐 | TensorRT-LLM | 编译优化，性能最佳 |
| 边缘部署 | llama.cpp/Ollama | CPU 支持，资源占用小 |
| 多模型服务 | vLLM + LoRA | LoRA 动态加载支持 |
| 超长上下文 | vLLM | PagedAttention 内存效率 |

## Implementation

```python
# vLLM 服务端部署
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,         # 4-GPU 张量并行
    gpu_memory_utilization=0.9,     # 90% 显存利用率
    max_model_len=4096,             # 最大序列长度
    enable_prefix_caching=True,     # 前缀缓存
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
)

# 批量推理
outputs = llm.generate(prompts, sampling_params)

# 使用 vLLM 的 OpenAI 兼容 API
# python -m vllm.entrypoints.openai.api_server \
#     --model meta-llama/Llama-2-70b-chat-hf \
#     --tensor-parallel-size 4 \
#     --api-key token-abc123
```

## Interview Tips
- 能够比较 vLLM 和 TensorRT-LLM 的架构差异和适用场景
- 理解推测解码的数学保证（生成分布不变）
- 掌握 TTFT 和 TPOT 的定义及优化方向
- 能够描述 disaggregated serving 的动机和实现方案
- 了解如何根据具体需求选择合适的服务系统
"""

# ============================================================
# Node 160: Chunking Strategies
# ============================================================
translations[160] = r"""# Chunking Strategies

## Overview
**Chunking（分块）** 是 **RAG (Retrieval-Augmented Generation，检索增强生成)** 系统中的关键预处理步骤，负责将长文档分割成适合检索和生成的文本片段。分块策略直接影响检索质量和生成效果——过大的块可能包含过多无关信息，过小的块可能丢失上下文。

在面试中，候选人需要理解不同分块策略的原理、适用场景和权衡，以及如何根据具体需求设计最优的分块方案。

## Core Concepts

### Fixed-Size Chunking
**Fixed-Size Chunking（固定大小分块）** 是最简单的策略，按字符数或 token 数分割：

- **Chunk Size（块大小）**：通常 256-1024 token
- **Overlap（重叠）**：相邻块之间重叠 10-20% 的内容，避免在分割处丢失上下文

优点：实现简单、可预测、处理速度快
缺点：可能在句子或段落中间断开，破坏语义完整性

### Recursive Character Splitting
**Recursive Character Splitting（递归字符分割）** 是 LangChain 默认的分块方法，按照语义层次递归分割：

分割优先级：`\n\n`（段落）→ `\n`（行）→ `. `（句子）→ ` `（单词）→ `""`（字符）

算法：
1. 尝试用最高优先级的分隔符分割文本
2. 如果结果块大于目标大小，用下一级分隔符继续分割
3. 重复直到所有块都小于目标大小
4. 合并过小的相邻块

这种方法在保持语义完整性和块大小控制之间取得了很好的平衡。

### Semantic Chunking
**Semantic Chunking（语义分块）** 基于文本语义相似度进行分割：

1. 将文本分成基本单元（通常是句子）
2. 为每个单元计算 **Embedding（嵌入向量）**
3. 计算相邻单元之间的 **Cosine Similarity（余弦相似度）**
4. 在相似度低于阈值的位置进行分割（表示话题转换）

$$\text{similarity}(s_i, s_{i+1}) = \frac{e(s_i) \cdot e(s_{i+1})}{\|e(s_i)\| \cdot \|e(s_{i+1})\|}$$

当 $\text{similarity}(s_i, s_{i+1}) < \tau$ 时，在 $s_i$ 和 $s_{i+1}$ 之间断开。

优点：根据内容自适应分割，语义完整性最好
缺点：需要额外的嵌入计算，速度较慢

### Document-Specific Chunking
针对不同文档类型的专用分块策略：

- **Markdown/HTML**：按标题层级分割，保留文档结构
- **Code（代码）**：按函数、类或方法分割，使用 AST 解析
- **Table（表格）**：将表格作为整体保留，避免跨行或跨列分割
- **PDF**：使用版面分析工具识别段落、表格和图片区域

### Chunk Size vs Retrieval Quality Tradeoff
块大小的选择涉及多个维度的权衡：

| 块大小 | 检索精度 | 上下文完整性 | 嵌入质量 | 检索速度 |
|--------|----------|-------------|----------|----------|
| 小（128-256 token） | 高 | 低 | 好 | 快 |
| 中（256-512 token） | 中 | 中 | 中 | 中 |
| 大（512-1024 token） | 低 | 高 | 可能下降 | 慢 |

经验指导：
- **问答型 RAG**：较小的块（256-512 token），精确检索特定信息
- **摘要型 RAG**：较大的块（512-1024 token），保留更多上下文
- **代码 RAG**：按函数/类分割，大小自适应

### Advanced Chunking Techniques

**Parent-Child Chunking（父子分块）**：
- 创建两层索引：大块（父）和小块（子）
- 用小块进行精确检索，返回对应的大块保证上下文完整性
- 兼顾检索精度和上下文完整性

**Sentence Window（句子窗口）**：
- 以句子为单位建立索引
- 检索到目标句子后，返回周围的 $k$ 个句子作为上下文
- 提供精确的检索粒度和灵活的上下文范围

**Agentic Chunking（智能体分块）**：
- 使用 LLM 判断每个句子是否属于当前块或应开始新块
- 质量最好但成本最高
- 适用于高价值文档的离线处理

### Evaluation of Chunking
评估分块质量的方法：

- **Retrieval Hit Rate（检索命中率）**：正确答案是否被检索到
- **Context Relevancy（上下文相关性）**：检索到的块与问题的相关程度
- **Answer Quality（回答质量）**：最终生成答案的质量
- **A/B Testing（A/B测试）**：在实际场景中比较不同策略

## Implementation

```python
# 不同分块策略的实现
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 固定大小分块
fixed_splitter = TokenTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
)
chunks = fixed_splitter.split_text(document)

# 2. 递归字符分割
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)
chunks = recursive_splitter.split_text(document)

# 3. 语义分块
def semantic_chunking(text, model_name="all-MiniLM-L6-v2", threshold=0.5):
    """基于语义相似度的分块"""
    model = SentenceTransformer(model_name)
    sentences = text.split(". ")
    embeddings = model.encode(sentences)

    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        sim = np.dot(embeddings[i-1], embeddings[i]) / (
            np.linalg.norm(embeddings[i-1]) * np.linalg.norm(embeddings[i])
        )
        if sim < threshold:
            chunks.append(". ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])

    if current_chunk:
        chunks.append(". ".join(current_chunk))
    return chunks
```

## Interview Tips
- 能够比较不同分块策略的优缺点及适用场景
- 理解块大小与检索质量的权衡关系
- 掌握 parent-child chunking 和 sentence window 等高级技术
- 能够根据具体文档类型和应用场景推荐最优策略
- 了解如何评估和优化分块方案
"""

# ============================================================
# Node 161: Embedding Models
# ============================================================
translations[161] = r"""# Embedding Models

## Overview
**Embedding Models（嵌入模型）** 将文本转换为稠密向量表示，是 RAG 系统中检索的基础。现代嵌入模型基于 **Sentence Transformers（句子变换器）** 框架，通过 **Contrastive Learning（对比学习）** 训练，使语义相似的文本在向量空间中距离更近。

在面试中，候选人需要理解嵌入模型的训练方法、评估指标和实际部署中的优化技术。

## Core Concepts

### Sentence-Transformers Architecture
**Sentence-Transformers** 基于 BERT/RoBERTa 等预训练编码器，通过以下步骤获得句子嵌入：

1. 将句子通过 Transformer 编码器获得 token 级别的表示
2. 使用 **Pooling Strategy（池化策略）** 将 token 表示聚合为单一向量：
   - **[CLS] Pooling**：使用 [CLS] token 的表示
   - **Mean Pooling（均值池化）**：对所有 token 表示求平均（通常效果最好）
   - **Max Pooling（最大池化）**：对每个维度取最大值

### Contrastive Loss
嵌入模型的核心训练目标是 **Contrastive Loss（对比损失）**，也称为 **InfoNCE Loss**：

$$\mathcal{L} = -\log \frac{e^{\text{sim}(z_i, z_j) / \tau}}{\sum_{k=1}^{2N} \mathbb{1}_{[k \neq i]} e^{\text{sim}(z_i, z_k) / \tau}}$$

其中：
- $z_i, z_j$ 是正样本对（语义相似的文本对）的嵌入
- $\text{sim}(\cdot, \cdot)$ 是余弦相似度
- $\tau$ 是 **Temperature（温度系数）**，控制分布的尖锐程度
- $N$ 是批次中的正样本对数
- 分母包含所有非 $i$ 的样本作为 **In-batch Negatives（批内负样本）**

温度系数的作用：
- $\tau$ 较小时，模型更关注区分难负样本
- $\tau$ 较大时，梯度信号更均匀
- 通常 $\tau \in [0.01, 0.1]$

### Hard Negative Mining
**Hard Negative Mining（困难负样本挖掘）** 对嵌入质量至关重要。高质量的负样本是那些表面相似但语义不同的文本对：

- **In-batch Negatives（批内负样本）**：同一批次中的其他样本作为负样本
- **BM25 Negatives**：用 BM25 检索的高分但不正确的文档
- **Cross-encoder Reranking（交叉编码器重排序）**：用更强的模型识别困难负样本
- **Self-mining（自挖掘）**：用当前模型检索得到的假阳性

### Training Data Sources
嵌入模型的训练数据来源：

- **Natural Language Inference (NLI，自然语言推理)**：蕴含对作为正样本，矛盾对作为负样本
- **Paraphrase（释义）** 数据：同义表达作为正样本
- **Question-Answer（问答）** 数据：问题与答案作为正样本
- **Web Search（网页搜索）** 数据：查询与点击文档作为正样本
- **Synthetic Data（合成数据）**：使用 LLM 生成训练数据对

### Matryoshka Representation Learning (MRL)
**Matryoshka Representation Learning（套娃表示学习）**（Kusupati et al., 2022）训练出可以在不同维度截断使用的嵌入：

$$\mathcal{L}_{\text{MRL}} = \sum_{d \in \{32, 64, 128, 256, 768\}} \mathcal{L}_{\text{contrastive}}(z[:d])$$

训练时在多个维度上同时优化对比损失。使用时可以根据延迟和存储需求选择合适的维度：

| 维度 | 相对质量 | 存储节省 |
|------|----------|----------|
| 768 | 100% | 基准 |
| 256 | ~97% | 3x |
| 128 | ~95% | 6x |
| 64 | ~90% | 12x |

这使得一个模型可以适应从高质量检索到资源受限的移动端等不同场景。

### Late Interaction Models
**Late Interaction（晚期交互）** 模型（如 **ColBERT**）保留 token 级别的表示，提供更细粒度的匹配：

$$\text{Score}(q, d) = \sum_{i=1}^{|q|} \max_{j=1}^{|d|} q_i^T d_j$$

每个查询 token 找到最相似的文档 token，然后求和。与单向量模型相比，ColBERT 在保持检索速度的同时提供了更好的匹配质量。

### Bi-Encoder vs Cross-Encoder

| 特性 | Bi-Encoder（双编码器） | Cross-Encoder（交叉编码器） |
|------|----------------------|--------------------------|
| 编码方式 | 查询和文档独立编码 | 查询和文档拼接后联合编码 |
| 推理速度 | 快（可预计算文档嵌入） | 慢（每对都要重新编码） |
| 匹配质量 | 较好 | 最好 |
| 适用场景 | 初始检索（海量候选） | 重排序（少量候选） |

实际系统通常采用两阶段架构：Bi-Encoder 快速检索 Top-100 → Cross-Encoder 精排 Top-10。

### Evaluation Metrics
嵌入模型的评估指标：

- **NDCG@k (Normalized Discounted Cumulative Gain)**：考虑排序位置的检索质量
- **MRR (Mean Reciprocal Rank，平均倒数排名)**：第一个正确结果的排名倒数
- **Recall@k**：Top-k 结果中包含正确答案的比例
- **MTEB (Massive Text Embedding Benchmark)**：综合评估基准，覆盖检索、分类、聚类等任务

## Implementation

```python
# 使用 Sentence-Transformers 进行嵌入
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

# 加载预训练嵌入模型
model = SentenceTransformer("all-MiniLM-L6-v2")

# 编码文本
sentences = ["这是一个查询", "这是一个相关文档"]
embeddings = model.encode(sentences, normalize_embeddings=True)

# 计算余弦相似度
similarity = embeddings[0] @ embeddings[1]

# 微调嵌入模型
train_examples = [
    InputExample(texts=["查询文本", "正样本文档"], label=1.0),
    InputExample(texts=["查询文本", "负样本文档"], label=0.0),
]
train_dataloader = DataLoader(train_examples, batch_size=32, shuffle=True)
train_loss = losses.ContrastiveLoss(model)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
)
```

## Interview Tips
- 理解对比损失的原理及温度系数的作用
- 掌握困难负样本挖掘的方法和重要性
- 能够比较 Bi-Encoder 和 Cross-Encoder 的适用场景
- 了解 Matryoshka 表示学习如何实现维度自适应
- 掌握嵌入模型评估指标（NDCG、MRR、Recall）
"""

# ============================================================
# Node 162: Vector Databases
# ============================================================
translations[162] = r"""# Vector Databases

## Overview
**Vector Databases（向量数据库）** 是存储和检索高维向量的专用系统，是 RAG 和语义搜索应用的核心基础设施。它们通过 **ANN (Approximate Nearest Neighbor，近似最近邻)** 算法实现亚线性时间的相似度搜索，在数百万到数十亿向量的规模上提供毫秒级的查询响应。

在面试中，候选人需要理解主流索引算法的原理、不同向量数据库的架构差异，以及如何根据具体场景选择和优化。

## Core Concepts

### ANN Index Types
精确最近邻搜索的复杂度为 $O(n \cdot d)$（$n$ 是向量数，$d$ 是维度），在大规模场景下不可行。**ANN** 算法通过牺牲少量准确度来换取数量级的速度提升。

**IVF (Inverted File Index，倒排文件索引)**：
- 使用 K-means 将向量空间划分为 $n_{\text{list}}$ 个 **Voronoi Cell（泰森多边形）**
- 查询时只搜索距离最近的 $n_{\text{probe}}$ 个分区
- 速度提升：约 $n_{\text{list}} / n_{\text{probe}}$ 倍
- 适合中等规模数据集（百万级）

**PQ (Product Quantization，乘积量化)**：
- 将 $d$ 维向量分成 $m$ 个子向量
- 每个子向量独立聚类为 $k$ 个中心（通常 $k = 256$，用 8 bit 编码）
- 内存压缩比：$\frac{d \times 4}{m}$ 字节/向量

$$\text{距离近似} = \sum_{j=1}^{m} d(x^{(j)}, c_{q_j}^{(j)})$$

PQ 常与 IVF 组合使用（**IVF-PQ**），先粗筛再精排。

**HNSW (Hierarchical Navigable Small World，分层可导航小世界图)**：
- 构建多层图结构，高层稀疏（长距离跳跃），底层密集（精确搜索）
- 查询从最高层开始贪心搜索，逐层下降
- 建图参数：$M$（每个节点的连接数）、$ef_{\text{construction}}$（建图时的搜索宽度）
- 查询参数：$ef_{\text{search}}$（搜索时的候选集大小）

HNSW 通常提供最好的查询质量（Recall > 95%），但内存占用较大。

### Index Types Comparison

| 索引类型 | 查询延迟 | 内存 | 构建时间 | 召回率 | 适用规模 |
|---------|---------|------|---------|--------|---------|
| Flat (暴力) | O(n) | 低 | O(n) | 100% | < 100K |
| IVF | 中等 | 低 | 中等 | 85-95% | 100K-10M |
| IVF-PQ | 快 | 很低 | 中等 | 80-90% | 1M-1B |
| HNSW | 快 | 高 | 慢 | 95-99% | 100K-100M |
| ScaNN | 很快 | 中等 | 中等 | 90-98% | 1M-1B |

### FAISS
**FAISS (Facebook AI Similarity Search)** 是 Meta 开发的向量搜索库，支持多种索引类型：

核心特性：
- GPU 加速：支持 GPU 上的暴力搜索和 IVF
- 组合索引：如 `IVF4096,PQ64` 表示 4096 个分区 + 64 子向量 PQ
- 量化方法：PQ、SQ（标量量化）、OPQ（优化PQ）
- 适合嵌入式使用（作为库而非独立服务）

### Milvus
**Milvus** 是云原生的分布式向量数据库：

- **架构**：存储计算分离，多副本支持
- **索引**：支持 HNSW、IVF-FLAT、IVF-PQ、DiskANN
- **特性**：标量过滤、混合搜索（向量+关键词）、分区/分片
- **扩展性**：支持百亿级向量

### Pinecone
**Pinecone** 是全托管的向量数据库服务：

- **无服务器（Serverless）**：按使用量计费
- **Namespace（命名空间）**：逻辑隔离不同数据集
- **Metadata Filtering（元数据过滤）**：支持与向量搜索结合的属性过滤
- **适用场景**：快速上线、小中规模应用

### ANN Benchmark
**ANN Benchmark** 是标准化的向量搜索性能评测：

评测维度：
- **Recall vs QPS（查询/秒）** 曲线：在相同召回率下比较吞吐量
- **Build Time（构建时间）**：索引构建耗时
- **Memory Usage（内存占用）**：运行时内存需求

关键发现：
- HNSW 在高召回率（> 95%）下通常最快
- IVF-PQ 在内存受限场景下有优势
- **DiskANN** 在磁盘-内存混合架构下表现优异

### Vector Database Selection Guide

| 需求 | 推荐方案 |
|------|----------|
| 简单原型 | FAISS + Flat/HNSW |
| 中规模生产 | Milvus / Qdrant / Weaviate |
| 全托管服务 | Pinecone / Zilliz Cloud |
| 超大规模 | Milvus 分布式 / FAISS + DiskANN |
| 混合搜索 | Milvus / Weaviate |
| 极低延迟 | FAISS GPU / ScaNN |

### Hybrid Search
**Hybrid Search（混合搜索）** 结合稠密向量搜索和稀疏关键词搜索：

$$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{dense}} + (1 - \alpha) \cdot \text{Score}_{\text{sparse}}$$

稠密检索擅长语义匹配，稀疏检索擅长精确关键词匹配。混合搜索在多数实际场景下优于单一方法。$\alpha$ 通常需要根据具体场景调优。

## Implementation

```python
# FAISS 向量检索示例
import faiss
import numpy as np

dim = 768
n_vectors = 1_000_000

# 创建索引
# HNSW 索引（高召回率）
index_hnsw = faiss.IndexHNSWFlat(dim, 32)  # M=32
index_hnsw.hnsw.efConstruction = 200
index_hnsw.hnsw.efSearch = 64

# IVF-PQ 索引（内存高效）
quantizer = faiss.IndexFlatL2(dim)
index_ivfpq = faiss.IndexIVFPQ(quantizer, dim, 4096, 64, 8)
# 4096 个分区，64 个子量化器，每个 8 bit

# 训练和添加向量
vectors = np.random.randn(n_vectors, dim).astype('float32')
faiss.normalize_L2(vectors)  # L2 归一化用于余弦相似度

index_ivfpq.train(vectors[:100000])  # 用部分数据训练
index_ivfpq.add(vectors)
index_ivfpq.nprobe = 64  # 搜索 64 个分区

# 搜索
query = np.random.randn(1, dim).astype('float32')
faiss.normalize_L2(query)
distances, indices = index_ivfpq.search(query, k=10)
```

## Interview Tips
- 能够解释 IVF、PQ、HNSW 的工作原理
- 理解 Recall-QPS 权衡及如何调参优化
- 掌握不同向量数据库的架构差异和适用场景
- 了解混合搜索的原理和实际效果
- 能够根据数据规模和需求推荐合适的方案
"""

# ============================================================
# Node 163: Advanced RAG
# ============================================================
translations[163] = r"""# Advanced RAG Patterns

## Overview
**Advanced RAG（高级检索增强生成）** 在基础 RAG 的基础上引入了多种技术来提升检索质量和生成准确性。从 **Query Rewriting（查询改写）** 到 **Self-RAG（自检索增强生成）**，从 **HyDE（假设文档嵌入）** 到 **Multi-hop Reasoning（多跳推理）**，这些方法系统性地解决了基础 RAG 的局限性。

在面试中，候选人需要展示对 RAG 系统全链路优化的深入理解，包括检索前优化、检索优化和检索后优化。

## Core Concepts

### RAG Pipeline Overview
高级 RAG 在基础 RAG（查询→检索→生成）的基础上增加了多个优化环节：

```
Query → [Pre-retrieval] → [Retrieval] → [Post-retrieval] → Generation
         查询改写           多路检索        重排序
         查询扩展           混合搜索        压缩/过滤
         HyDE              递归检索        上下文增强
```

### Query Rewriting
**Query Rewriting（查询改写）** 优化用户查询以提高检索效果：

- **LLM-based Rewriting（基于LLM的改写）**：使用 LLM 将口语化查询转换为更适合检索的形式
- **Multi-query（多查询）**：将一个查询扩展为多个不同角度的子查询，分别检索后合并结果
- **Step-back Prompting（后退提示）**：将具体问题抽象为更一般的问题，检索更全面的背景知识

示例：
- 原始查询："为什么我的代码运行这么慢？"
- 改写后："Python 代码性能优化 常见性能瓶颈 profiling 方法"

### HyDE (Hypothetical Document Embeddings)
**HyDE（假设文档嵌入）** 利用 LLM 生成一个"假设的回答"，然后用这个回答的嵌入去检索真实文档：

1. 用户提出问题 $q$
2. LLM 生成假设回答 $d_{\text{hypo}}$（可能不准确但包含关键术语）
3. 计算 $d_{\text{hypo}}$ 的嵌入向量
4. 用该嵌入检索真实文档
5. 用检索到的真实文档生成最终回答

$$e_{\text{query}} = \text{Embed}(\text{LLM}(q))$$

HyDE 的直觉是：假设回答与真实文档在语义空间中比原始查询更接近。

### Self-RAG
**Self-RAG（自检索增强生成）**（Asai et al., 2023）训练模型在生成过程中自主决定是否需要检索、检索内容是否相关、以及生成的回答是否忠实于检索结果：

模型生成特殊 token 来控制流程：
- **[Retrieve]**：是否需要检索（Yes/No）
- **[ISREL]**：检索到的文档是否与问题相关
- **[ISSUP]**：生成的回答是否有检索文档支撑
- **[ISUSE]**：回答是否有用

这使得模型可以根据查询的难度动态调整策略——简单问题直接回答，复杂问题触发检索。

### CRAG (Corrective RAG)
**CRAG（纠错检索增强生成）** 在检索后增加一个评估-纠正步骤：

1. 检索文档
2. 使用轻量级评估器判断文档相关性：
   - **Correct（正确）**：文档相关，直接使用
   - **Incorrect（不正确）**：文档不相关，触发网页搜索获取更多信息
   - **Ambiguous（模糊）**：部分相关，提取相关段落并补充检索
3. 使用纠正后的上下文生成回答

### Multi-hop Reasoning
**Multi-hop Reasoning（多跳推理）** 处理需要多次检索才能回答的复杂问题：

示例："获得图灵奖的人中，谁发明了最早的计算机编程语言？"
- 第一跳：检索图灵奖获得者列表
- 第二跳：检索各获奖者的贡献
- 第三跳：确认最早的编程语言

实现方法：
- **Iterative Retrieval（迭代检索）**：每次检索后更新查询，循环检索
- **Chain-of-Thought Retrieval（链式思维检索）**：让 LLM 分解问题，每步检索一部分信息
- **Graph-based Retrieval（基于图的检索）**：构建知识图谱，沿关系边进行多跳检索

### RAG Fusion
**RAG Fusion** 结合多个检索策略的结果：

1. 将原始查询改写为多个变体
2. 对每个变体独立检索
3. 使用 **Reciprocal Rank Fusion (RRF，倒数排名融合)** 合并结果：

$$\text{RRF}(d) = \sum_{i=1}^{n} \frac{1}{k + r_i(d)}$$

其中 $r_i(d)$ 是文档 $d$ 在第 $i$ 个检索列表中的排名，$k$ 是平滑常数（通常 60）。

### Reranking
**Reranking（重排序）** 使用更精确的模型对初始检索结果进行重新排序：

- **Cross-Encoder Reranking**：将查询和文档拼接后输入 BERT 类模型，获得更准确的相关性分数
- **LLM-based Reranking**：使用 LLM 对文档相关性进行打分或排序
- **Cohere Rerank API**：商用重排序服务

重排序通常在 Top-50 到 Top-100 的初始结果上运行，选出 Top-5 到 Top-10 的最相关文档。

### RAG Evaluation
RAG 系统的评估框架（如 **RAGAS**）涵盖多个维度：

| 指标 | 定义 | 衡量内容 |
|------|------|----------|
| **Faithfulness（忠实度）** | 回答是否基于检索到的上下文 | 减少幻觉 |
| **Answer Relevancy（回答相关性）** | 回答是否切题 | 回答质量 |
| **Context Precision（上下文精度）** | 检索到的上下文中相关内容的比例 | 检索精度 |
| **Context Recall（上下文召回）** | 需要的信息是否都被检索到 | 检索覆盖 |

$$\text{Faithfulness} = \frac{\text{由上下文支撑的声明数}}{\text{回答中总声明数}}$$

## Implementation

```python
# 高级 RAG 实现示例
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1. HyDE 实现
def hyde_retrieve(query, retriever, llm):
    """使用 HyDE 进行检索"""
    # 生成假设回答
    hyde_prompt = f"请回答以下问题（即使不确定也要尝试）：\n{query}"
    hypothetical_doc = llm.invoke(hyde_prompt).content
    # 用假设回答检索真实文档
    results = retriever.invoke(hypothetical_doc)
    return results

# 2. Multi-query 实现
def multi_query_retrieve(query, retriever, llm, n_queries=3):
    """生成多个查询变体并合并检索结果"""
    prompt = "将以下问题改写为" + str(n_queries) + "个不同角度的查询:\n    原始问题: " + query + "\n    请每行输出一个查询。"
    queries = llm.invoke(prompt).content.strip().split("\n")
    all_docs = set()
    for q in queries:
        docs = retriever.invoke(q)
        all_docs.update(doc.page_content for doc in docs)
    return list(all_docs)

# 3. RRF 融合
def reciprocal_rank_fusion(results_lists, k=60):
    """倒数排名融合"""
    scores = {}
    for results in results_lists:
        for rank, doc in enumerate(results):
            doc_id = doc.metadata.get("id", hash(doc.page_content))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs
```

## Interview Tips
- 能够完整描述 RAG 系统的全链路优化方案
- 理解 HyDE 和 Self-RAG 的核心思想及适用场景
- 掌握多跳推理的实现方法和挑战
- 能够解释 RAGAS 评估框架的各个指标
- 了解 RAG Fusion 和 RRF 的原理和实际效果
"""

# ============================================================
# Node 164: Vision-Language Models (CLIP, LLaVA)
# ============================================================
translations[164] = r"""# Vision-Language Models (CLIP, LLaVA)

## Overview
**Vision-Language Models (VLMs，视觉-语言模型)** 是连接视觉和语言的多模态模型。**CLIP (Contrastive Language-Image Pre-training，对比语言-图像预训练)** 通过对比学习将图像和文本映射到同一语义空间，而 **LLaVA (Large Language and Vision Assistant，大型语言与视觉助手)** 等模型将视觉编码器与 LLM 结合，实现了对图像的理解和对话。

在面试中，VLM 相关问题涵盖多模态对齐、架构设计和训练策略等方面。

## Core Concepts

### CLIP Architecture
**CLIP**（Radford et al., 2021）的核心思想是使用 **Contrastive Learning（对比学习）** 同时训练一个 **Image Encoder（图像编码器）** 和一个 **Text Encoder（文本编码器）**：

$$\mathcal{L}_{\text{CLIP}} = \mathcal{L}_{\text{InfoNCE}}(I, T) = -\frac{1}{N}\sum_{i=1}^{N}\left[\log\frac{e^{\text{sim}(f(I_i), g(T_i))/\tau}}{\sum_{j=1}^{N} e^{\text{sim}(f(I_i), g(T_j))/\tau}} + \log\frac{e^{\text{sim}(g(T_i), f(I_i))/\tau}}{\sum_{j=1}^{N} e^{\text{sim}(g(T_i), f(I_j))/\tau}}\right]$$

其中：
- $f(\cdot)$ 是图像编码器（ViT 或 ResNet）
- $g(\cdot)$ 是文本编码器（Transformer）
- $\text{sim}(\cdot, \cdot)$ 是余弦相似度
- $\tau$ 是可学习的温度参数
- $N$ 是批次大小（CLIP 使用 32K 的超大批次）

CLIP 的训练数据包含 4 亿个从互联网收集的（图像，文本描述）对。损失函数是对称的——既鼓励图像找到对应文本，也鼓励文本找到对应图像。

### CLIP Zero-shot Classification
CLIP 最革命性的能力是 **Zero-shot Image Classification（零样本图像分类）**：

1. 将类别名称转换为文本提示：`"a photo of a {class}"`
2. 分别编码图像和所有类别文本
3. 选择与图像最相似的文本对应的类别

$$\text{class} = \arg\max_c \text{sim}(f(I), g(\text{"a photo of a "} + c))$$

无需任何训练数据，CLIP 就能在 ImageNet 上达到 76.2% 的准确率（与有监督 ResNet-50 相当）。通过 **Prompt Engineering（提示工程）** 和 **Prompt Ensembling（提示集成）** 可以进一步提升性能。

### LLaVA Architecture
**LLaVA (Large Language and Vision Assistant，大型语言与视觉助手)**（Liu et al., 2023）的架构由三个组件组成：

$$\text{LLaVA} = \text{Visual Encoder} + \text{Projection} + \text{LLM}$$

1. **Visual Encoder（视觉编码器）**：使用预训练的 CLIP ViT-L/14 提取图像特征
2. **Projection Layer（投影层）**：将视觉特征映射到 LLM 的输入空间
   - LLaVA-1.0：简单的线性投影 $W \cdot v_{\text{image}}$
   - LLaVA-1.5：两层 MLP 投影（效果更好）
3. **LLM Backbone（LLM 骨干）**：接收视觉 token 和文本 token，生成回答

输入序列格式：`[visual tokens] [text instruction] [response]`

### LLaVA Training Pipeline
LLaVA 采用两阶段训练：

**阶段 1：Pretraining（预训练对齐）**：
- 冻结视觉编码器和 LLM，仅训练投影层
- 使用 558K 图像-文本对（CC-Filtered）
- 目标：学习视觉-语言对齐

**阶段 2：Visual Instruction Tuning（视觉指令微调）**：
- 冻结视觉编码器，训练投影层和 LLM
- 使用 665K 多模态指令数据（GPT-4 生成）
- 包含：详细描述、复杂推理、对话
- 目标：学习跟随多模态指令

### Flamingo
**Flamingo**（Alayrac et al., 2022, DeepMind）的关键创新是 **Gated Cross-Attention（门控交叉注意力）** 层：

- 在 LLM 的每几层之间插入交叉注意力层
- 查询来自文本 token，键和值来自视觉 token
- 使用 **Tanh Gating（tanh门控）** 控制视觉信息的注入强度（初始化为0，逐渐学习）
- 支持 **Interleaved Image-Text（交错图像-文本）** 输入

$$\text{Gated-XAttn}(x) = x + \tanh(\alpha) \cdot \text{CrossAttn}(x, v_{\text{image}})$$

其中 $\alpha$ 初始化为 0，使得训练初期 LLM 行为不变。

### Visual Grounding
**Visual Grounding（视觉定位）** 将语言描述与图像中的具体区域对应：

- **Referring Expression Comprehension（引用表达理解）**：给定描述，定位对应的图像区域
- **Object Detection（目标检测）**：结合语言条件进行目标检测（如 GLIP, Grounding DINO）
- **Bounding Box Prediction（边界框预测）**：输出格式如 `<box>x1, y1, x2, y2</box>`

### SigLIP and Improvements
**SigLIP (Sigmoid Loss for Language-Image Pre-training)** 改进了 CLIP 的损失函数：

$$\mathcal{L}_{\text{SigLIP}} = -\frac{1}{N}\sum_{i,j} \log \sigma(y_{ij} \cdot z_i^T z_j - b)$$

其中 $y_{ij} = 1$ 如果 $(i,j)$ 是正样本对，否则 $y_{ij} = -1$。

SigLIP 的优势：
- 不需要全局 softmax，支持更大批次
- 训练更稳定
- 在小批次下表现更好

### VLM Comparison

| 模型 | 视觉编码器 | LLM | 视觉-语言连接 | 训练数据 |
|------|-----------|-----|-------------|---------|
| LLaVA-1.5 | CLIP ViT-L | Vicuna-13B | MLP投影 | 1.2M |
| Qwen-VL | ViT-bigG | Qwen-7B | 交叉注意力 | 1.4B |
| InternVL | InternViT | InternLM | QLLaMA | 多阶段 |
| GPT-4V | 未知 | GPT-4 | 未知 | 未知 |
| Gemini | 原生多模态 | Gemini | 统一编码 | 未知 |

## Implementation

```python
# CLIP 零样本分类
import torch
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# 零样本分类
image = load_image("cat.jpg")
candidate_labels = ["a photo of a cat", "a photo of a dog", "a photo of a car"]

inputs = processor(text=candidate_labels, images=image, return_tensors="pt", padding=True)
outputs = model(**inputs)

# 计算图像-文本相似度
logits = outputs.logits_per_image  # shape: [1, 3]
probs = logits.softmax(dim=1)
print(f"分类结果: {candidate_labels[probs.argmax()]}, 置信度: {probs.max():.3f}")

# LLaVA 推理
from transformers import LlavaForConditionalGeneration, AutoProcessor

model = LlavaForConditionalGeneration.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

prompt = "<image>\n请详细描述这张图片中的内容。"
inputs = processor(prompt, image, return_tensors="pt").to("cuda")
output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0], skip_special_tokens=True))
```

## Interview Tips
- 理解 CLIP 对比学习的对称损失函数设计
- 能够描述 LLaVA 的两阶段训练策略及其设计动机
- 掌握不同 VLM 中视觉-语言连接方式的优缺点
- 了解零样本分类的原理和提示工程技巧
- 能够比较 CLIP、LLaVA 和 Flamingo 的架构差异
"""

# ============================================================
# Execute updates
# ============================================================
def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for node_id in range(149, 165):
        desc = translations[node_id].strip()
        cursor.execute("UPDATE framework_nodes SET description = ? WHERE id = ?", (desc, node_id))

        # Verify
        cursor.execute("SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,))
        length = cursor.fetchone()[0]

        # Check for Chinese
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in desc)

        # Check for $$ in code blocks
        in_code = False
        has_math_in_code = False
        for line in desc.split('\n'):
            if line.strip().startswith('```'):
                in_code = not in_code
            elif in_code and '$$' in line:
                has_math_in_code = True

        status = "OK" if (length >= 5500 and has_chinese and not has_math_in_code) else "WARN"
        print(f"Node {node_id}: len={length}, chinese={has_chinese}, math_in_code={has_math_in_code} -> {status}")

    conn.commit()
    conn.close()
    print("\nAll 16 nodes updated successfully.")

if __name__ == "__main__":
    main()
