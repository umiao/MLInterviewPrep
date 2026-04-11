#!/usr/bin/env python3
"""Expand node translation files to meet 5500+ character minimum."""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TRANS_DIR = os.path.join(os.path.dirname(__file__), 'node_translations')

# Additional content to append before "## Interview Tips" for each node
expansions = {}

expansions[149] = r"""
### Emergent Abilities
**Emergent Abilities（涌现能力）** 是大规模语言模型中最令人兴奋的现象之一。当模型规模超过某个阈值时，突然表现出在小规模模型中完全不存在的能力：

- **Arithmetic（算术）**：在约 13B 参数时开始能够进行简单算术运算
- **Multi-step Reasoning（多步推理）**：在约 100B 参数时出现链式推理能力
- **Code Generation（代码生成）**：在约 60B 参数时开始生成正确的代码

涌现能力的存在是缩放定律的非线性延伸，也是持续增大模型规模的核心动力。但需要注意的是，也有研究者认为"涌现"可能只是评估指标选择的副产品——在连续指标上，性能提升实际上是渐进的。

### Tokenization
**BPE (Byte Pair Encoding，字节对编码)** 分词器是 GPT 系列的标准选择：

1. 从字节级别开始，统计最频繁的相邻字节对
2. 合并最频繁的对形成新的子词单元
3. 重复直到达到目标词表大小

GPT-2 使用约 50K 词表，GPT-4 使用约 100K 词表。更大的词表意味着：
- 更高的文本压缩率（相同文本用更少 token 表示）
- 更好的多语言支持
- 但嵌入层参数量增加

### GPT vs BERT Paradigm Comparison

| 维度 | GPT（自回归） | BERT（双向） |
|------|-------------|-------------|
| 训练目标 | 下一词预测 | 遮蔽语言建模 |
| 注意力 | 因果（单向） | 双向 |
| 生成能力 | 自然支持 | 不自然 |
| 理解能力 | 较弱（单向） | 较强（双向） |
| 主要用途 | 文本生成/对话 | 文本分类/NER |
| 缩放表现 | 优秀 | 一般 |

随着 GPT-3 的成功，自回归范式已经成为主流。BERT 类模型仍在特定任务（如检索、分类）中有优势。
"""

expansions[150] = r"""
### LLaMA Training Strategy
LLaMA 的训练策略体现了"开源追赶闭源"的方法论：

- **更多数据**：LLaMA-1 使用 1.4T tokens（超过 Chinchilla 最优），LLaMA-2 使用 2T tokens
- **公开数据**：仅使用公开可获取的数据，确保可复现性
- **数据混合**：精心调配不同数据源的比例（如 Common Crawl 67%, C4 15%, GitHub 4.5%, Wikipedia 4.5%, Books 4.5%, ArXiv 2.5%, Stack Exchange 2%）

### Mixtral MoE Architecture
**Mixtral**（Mistral 推出的 MoE 模型）将 **MoE (Mixture of Experts，混合专家)** 架构引入开源模型：

- 每层有 8 个专家，每次推理选择 2 个
- 总参数 46.7B，活跃参数 12.9B
- 使用 **Top-k Router（top-k路由器）** 选择专家：

$$G(x) = \text{TopK}(\text{softmax}(xW_g), k=2)$$

每个 token 被路由到得分最高的 2 个专家，输出为加权和。MoE 的关键挑战包括：
- **Load Balancing（负载均衡）**：确保专家被均匀使用
- **Expert Specialization（专家特化）**：让不同专家学习不同的知识

### Context Length Extension
上下文长度扩展是开源模型持续进化的方向：

- **Position Interpolation（位置插值）**：线性缩放 RoPE 频率，$\theta' = \theta \cdot \frac{L_{\text{train}}}{L_{\text{target}}}$
- **NTK-aware Scaling**：调整 RoPE 的基础频率 $\theta_{\text{base}}$
- **YaRN**：分段调整不同频率的缩放比例
- **Continual Pre-training（持续预训练）**：在更长序列上继续训练

### Tokenizer Design
LLaMA-3 将词表大小从 32K 扩展到 128K，这一变化带来的影响：
- 单个英文字符更可能被编码为完整 token（减少 token 数量，提高效率）
- 中文、日文、韩文等语言的支持显著改善
- 代码的 token 化更高效
- 嵌入层参数量增加但整体影响有限
"""

expansions[151] = r"""
### Data Mixture Optimization
预训练数据混合比例的优化是一个关键的工程决策：

| 数据源 | 典型比例 | 贡献 |
|--------|---------|------|
| Web Crawl | 60-70% | 广泛的语言能力 |
| Books | 5-10% | 长文本理解和叙述能力 |
| Academic Papers | 5-10% | 科学知识和推理 |
| Code | 5-15% | 编程和逻辑推理 |
| Wikipedia | 3-5% | 事实知识 |
| Conversation | 2-5% | 对话能力 |

关键发现：代码数据的比例对模型的推理能力有显著正面影响，即使是非编程任务。

### Training Infrastructure
大规模预训练的工程挑战：

- **Checkpoint Management（检查点管理）**：每 1-2 小时保存检查点，单个检查点可能数百GB
- **Failure Recovery（故障恢复）**：在数千 GPU 上训练时，硬件故障频繁。需要自动检测故障并从最近检查点恢复
- **Communication Optimization（通信优化）**：All-reduce、Ring-allreduce 等集体通信优化
- **Memory Optimization（内存优化）**：Activation Checkpointing（激活检查点）、Flash Attention

### Tokenizer Training
预训练还包括分词器的训练：

- **BPE 训练**：在预训练语料的子集上训练 BPE 分词器
- **Vocabulary Size（词表大小）** 的选择：更大的词表 -> 更少的 token -> 更快的训练，但嵌入层更大
- **Special Tokens（特殊token）**：预留 EOS、PAD、BOS 等特殊 token
- **Coverage（覆盖率）**：确保分词器能有效处理目标语言

### Pre-training Evaluation
训练过程中的评估策略：

- **Validation Loss（验证损失）**：在保留的验证集上监控损失
- **Downstream Probes（下游探测）**：定期在标准基准上评估
- **Scaling Prediction（缩放预测）**：根据小规模实验预测大模型的最终性能
- **Loss Plateaus（损失平台）**：识别训练是否进入平台期
"""

expansions[152] = r"""
### Chat Templates in Detail
不同模型使用不同的对话模板格式，这对 SFT 至关重要：

**ChatML（OpenAI格式）**：
```
<|im_start|>system
You are a helpful assistant.
<|im_end|>
<|im_start|>user
Hello!
<|im_end|>
<|im_start|>assistant
Hi there! How can I help?
<|im_end|>
```

**LLaMA-2 格式**：
```
[INST] <<SYS>>
System prompt here
<</SYS>>
User message [/INST] Assistant response
```

模板的正确性直接影响模型的对话质量。模板不匹配会导致模型行为异常。

### Data Curation Strategies
高质量 SFT 数据的策划方法：

- **Human-written（人工编写）**：质量最高但成本最大。适合核心能力的训练
- **Distillation（蒸馏）**：使用更强的模型（如GPT-4）生成回答，然后用于训练较小模型
- **Self-play（自对弈）**：让模型自己生成问题和回答，然后筛选高质量的
- **Rejection Sampling（拒绝采样）**：生成多个回答，选择最好的

### Training Hyperparameters
SFT 的关键超参数设置（基于最佳实践）：

| 超参数 | 典型值 | 说明 |
|--------|--------|------|
| 学习率 | $1 \times 10^{-5}$ 到 $5 \times 10^{-5}$ | 比预训练低一个数量级 |
| Epochs | 1-3 | 更多可能过拟合 |
| Batch Size | 64-128 | 根据GPU内存调整 |
| Max Seq Length | 2048-4096 | 覆盖大多数对话长度 |
| Warmup Ratio | 0.03-0.1 | 短warmup |
| Weight Decay | 0.01-0.1 | 防止过拟合 |

### SFT Quality Assurance
SFT 数据和模型的质量保证流程：

- **格式验证**：确保所有数据符合对话模板格式
- **内容审核**：过滤有害、错误或低质量的回答
- **多样性检查**：确保任务类型和难度的分布合理
- **人工评估**：随机抽样进行人工质量评估
- **A/B 测试**：对比不同数据集/配置训练的模型性能

### Catastrophic Forgetting
SFT 面临的一个重要风险是 **Catastrophic Forgetting（灾难性遗忘）**——模型在学习新的指令跟随能力时，可能会忘记预训练阶段学到的知识。缓解策略包括：

- 使用极低学习率
- 在 SFT 数据中混入少量预训练格式数据
- 使用 LoRA 等参数高效方法避免全量更新
"""

expansions[153] = r"""
### Reward Model Architecture
奖励模型的典型实现：

- 基于预训练 LLM，将最后一层替换为单值输出头
- 输入：prompt + response 的拼接
- 输出：标量奖励值
- 训练数据：人类标注的偏好对 $(x, y_w, y_l)$

奖励模型的质量瓶颈：
- 标注者之间的一致性通常仅 60-70%
- 标注指南的设计直接影响模型行为
- 大规模标注的成本很高（每个偏好对 $0.5-$2）

### PPO Implementation Details
RLHF 中 PPO 的实际实现涉及多个技术细节：

- **GAE (Generalized Advantage Estimation，广义优势估计)**：使用 $\lambda$-return 估计优势函数
- **Value Function（价值函数）**：通常与策略模型共享底层参数
- **Mini-batch Training（小批量训练）**：每个 rollout 的数据可以训练多个 epoch
- **Gradient Accumulation（梯度累积）**：有效增大批量大小

$$A^{\text{GAE}}(\gamma, \lambda) = \sum_{t=0}^{T} (\gamma\lambda)^t \delta_t$$

其中 $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ 是 TD 误差。

### DPO Mathematical Derivation
DPO 损失函数的推导关键步骤：

1. 从 RLHF 的最优策略出发：$\pi^*(y|x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y|x) \exp\left(\frac{1}{\beta} R(x, y)\right)$
2. 求解奖励函数：$R(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$
3. 将其代入 Bradley-Terry 偏好模型
4. 得到仅依赖于策略和参考模型的损失函数

这种推导表明 DPO 本质上是在隐式地学习奖励函数，同时直接优化策略。

### Alignment Tax
**Alignment Tax（对齐税）** 指的是对齐训练对模型基础能力的潜在损害：

- RLHF 可能降低模型在某些基准测试上的表现（如数学推理）
- 对齐训练使模型倾向于生成更长、更详细的回答，但不一定更准确
- **Safety-Helpfulness Tradeoff（安全性-有用性权衡）**：过度对齐的模型可能拒绝合理的请求

实践中需要在对齐程度和基础能力之间取得平衡。
"""

expansions[154] = r"""
### LoRA Mathematical Analysis
LoRA 的工作原理可以从优化角度理解。微调实际上是在高维参数空间中寻找最优方向。研究表明，对于特定下游任务，这些更新方向通常集中在一个低维子空间中：

$$\Delta W \in \mathbb{R}^{d \times k}, \quad \text{rank}(\Delta W) \ll \min(d, k)$$

**Intrinsic Dimensionality（内在维度）** 的研究（Aghajanyan et al., 2021）发现，许多 NLP 任务的有效参数维度远小于模型的总参数数量，这为 LoRA 的低秩假设提供了理论支持。

### LoRA vs Full Fine-tuning

| 维度 | LoRA | 全量微调 |
|------|------|----------|
| 训练参数 | < 1% | 100% |
| GPU 内存 | 低 | 高 |
| 训练速度 | 较快 | 慢 |
| 性能上限 | 接近全量 | 最优 |
| 多任务支持 | 易于切换 | 需要多个副本 |
| 灾难性遗忘 | 风险低 | 风险高 |

### Advanced LoRA Techniques
LoRA 的改进变体：

- **LoRA+**：对 A 和 B 矩阵使用不同的学习率，通常 $\eta_B = \lambda \eta_A$，$\lambda \approx 16$
- **rsLoRA (Rank-Stabilized LoRA)**：使用 $\frac{\alpha}{\sqrt{r}}$ 代替 $\frac{\alpha}{r}$ 作为缩放因子
- **AdaLoRA**：自适应地分配不同层和模块的秩，重要的模块获得更高的秩
- **LoRA-FA (Frozen A)**：冻结随机初始化的 A 矩阵，只训练 B 矩阵
- **VeRA (Vector-based Random Matrix Adaptation)**：使用共享的随机矩阵 + 可学习的缩放向量

### Production LoRA Deployment
在生产环境中部署 LoRA 的策略：

- **S-LoRA**：通过共享基础模型和并行化 LoRA 计算，同时服务数千个 LoRA 适配器
- **LoRAX**：Predibase 的 LoRA 服务系统，支持动态加载
- **Punica**：支持批量推理时的异构 LoRA 适配器
"""

expansions[155] = r"""
### MMLU in Detail
MMLU 的 57 个科目细分：

**STEM（25个科目）**：
抽象代数、天文学、大学生物学、大学化学、大学计算机科学、大学数学、大学物理、计算机安全、概念物理、电气工程、初等数学、高中生物、高中化学、高中计算机科学、高中数学、高中物理、高中统计、机器学习、数学、营养学等

**人文社科（32个科目）**：
商业伦理、临床知识、大学医学、全球事实、人类老化、国际法、法理学、逻辑推理、管理学、营销学、医学遗传学、道德争议、道德场景、哲学、职业心理学、专业会计等

### Benchmark Saturation
**Benchmark Saturation（基准饱和）** 是评估领域的重要问题：

- MMLU 上 GPT-4 已达 86%，接近人类专家水平
- 需要更难的基准来区分前沿模型
- **MMLU-Pro**：增加了更多困难题目和选项
- **GPQA**：PhD 级别的科学问题
- **FrontierMath**：研究级数学问题

### LLM-as-Judge
**LLM-as-Judge（LLM作为评判者）** 方法日益流行：

- 使用 GPT-4 等强模型对生成结果进行评分
- 优势：可扩展、一致性好、成本低于人类评估
- 劣势：存在偏见（偏好更长的回答、偏好自身风格）、在特定领域可能不可靠

评判框架设计要点：
- **Position Bias Mitigation（位置偏见缓解）**：随机交换两个回答的顺序
- **Rubric Design（评分标准设计）**：提供详细的评分标准
- **Few-shot Examples（少样本示例）**：提供评分示例提高一致性
- **Chain-of-Thought Scoring（链式思维评分）**：要求模型先分析再给分

### Evaluation Pipeline Design
设计企业级 LLM 评估流水线的关键组件：

- **Automated Suite（自动化套件）**：标准基准的定期自动运行
- **Human Evaluation（人类评估）**：关键场景的人工评估
- **Safety Testing（安全测试）**：红队测试和对抗评估
- **Domain-specific Evals（领域评估）**：针对特定业务场景的评估
- **Regression Detection（回归检测）**：模型更新后的性能对比
- **Cost-Quality Tradeoff（成本-质量权衡）**：不同模型的性价比分析
"""

expansions[156] = r"""
### Multi-Head KV Cache vs GQA KV Cache
详细对比不同注意力变体的 KV cache 效率：

对于一个 $n_h = 64$ 头、$d_h = 128$ 维的模型：

| 注意力类型 | KV 头数 | 每层每token KV大小 (BF16) |
|-----------|--------|--------------------------|
| MHA | 64 | $2 \times 64 \times 128 \times 2 = 32$ KB |
| GQA (g=8) | 8 | $2 \times 8 \times 128 \times 2 = 4$ KB |
| MQA | 1 | $2 \times 1 \times 128 \times 2 = 0.5$ KB |

GQA 在保持接近 MHA 质量的同时，将 KV cache 减少了 8 倍。

### Flash Attention and KV Cache
**Flash Attention** 与 KV Cache 的协同优化：

- Flash Attention 减少了注意力计算的 HBM 访问量
- 在 decode 阶段，Flash Attention 的 **Flash Decoding** 变体专门优化了单 token 注意力计算
- 结合 PagedAttention，实现了非连续 KV cache 的高效注意力计算

### KV Cache Quantization
**KV Cache Quantization（KV缓存量化）** 通过降低缓存精度来减少内存占用：

| 精度 | 每元素字节 | 内存节省 | 质量影响 |
|------|-----------|---------|---------|
| FP16/BF16 | 2 | 基准 | 无 |
| FP8 | 1 | 2x | 极小 |
| INT8 | 1 | 2x | 小 |
| INT4 | 0.5 | 4x | 中等 |

研究表明 KV cache 对量化的敏感度低于模型权重，因此可以使用更激进的量化策略。

### Token Eviction Strategies
当 KV cache 内存受限时，需要选择性地丢弃部分 token：

- **H2O (Heavy Hitter Oracle)**：保留注意力分数最高的 token（"重要token"）和最近的 token
- **Scissorhands**：基于注意力模式的 token 剪枝
- **StreamingLLM**：仅保留初始 token（Attention Sink）和最近的滑动窗口

$$\text{Retained tokens} = \text{Sink tokens} \cup \text{Recent window tokens}$$
"""

expansions[157] = r"""
### GPTQ vs AWQ Deep Comparison

| 维度 | GPTQ | AWQ |
|------|------|-----|
| 理论基础 | Optimal Brain Quantization | 激活感知权重保护 |
| 校准数据需求 | 128 样本 | 128 样本 |
| 量化时间 (7B) | ~10 分钟 | ~5 分钟 |
| 3-bit 质量 | 较好 | 更好 |
| 4-bit 质量 | 好 | 略好 |
| 内核支持 | Marlin, ExLlama | GEMM, GEMV |
| 分组量化 | 支持 | 支持 |

### GGUF and llama.cpp Quantization
**GGUF（GPT-Generated Unified Format）** 是 llama.cpp 使用的模型格式，支持灵活的混合量化：

- **Q4_K_M**：4-bit 量化，k-means 聚类，中等质量
- **Q5_K_M**：5-bit 量化，质量更好
- **Q2_K**：极端 2-bit 量化，质量下降明显
- **IQ4_XS**：使用 importance matrix 的智能4-bit量化

GGUF 的优势是支持 CPU 推理，使得在没有 GPU 的设备上也能运行 LLM。

### Quantization-Aware Training (QAT)
**QAT (Quantization-Aware Training，量化感知训练)** 在训练过程中模拟量化效果：

$$\hat{W} = \text{FakeQuant}(W) = \text{Dequant}(\text{Quant}(W))$$

前向传播使用量化权重，反向传播使用 **Straight-Through Estimator (STE，直通估计器)** 绕过不可导的量化操作。QAT 通常比 PTQ 获得更好的量化精度，但需要额外的训练时间。

### Practical Quantization Guide
量化方法选择的决策流程：

1. 如果有 H100+ GPU -> 使用 FP8（原生支持，质量最好）
2. 如果需要 W4A16（仅量化权重）-> AWQ 或 GPTQ
3. 如果需要 W8A8（权重和激活都量化）-> SmoothQuant
4. 如果在 CPU/消费级 GPU 上运行 -> GGUF (llama.cpp)
5. 如果追求极致压缩 -> AQLM（2-bit）或 QuIP#

### Quantization Error Analysis
量化引入的误差可以分析为：

$$\text{Error} = \|WX - \hat{W}X\|_F$$

这个误差与以下因素相关：
- **Weight Distribution（权重分布）**：权重分布越集中，量化误差越小
- **Outliers（异常值）**：少量极端值会显著增大整体量化误差
- **Group Size（分组大小）**：更小的分组（如32 vs 128）允许更精细的缩放，减少误差
"""

expansions[158] = r"""
### Scheduling Algorithm Comparison

| 调度算法 | 吞吐量 | 延迟公平性 | 实现复杂度 |
|---------|--------|-----------|-----------|
| Static Batching | 低 | 差 | 简单 |
| Continuous Batching | 高 | 中等 | 中等 |
| Chunked Prefill | 高 | 好 | 较复杂 |
| Disaggregated | 最高 | 好 | 最复杂 |

### Token Budget Management
在实际部署中，需要管理每个请求的 token 预算：

- **Max Input Tokens（最大输入token）**：限制 prompt 长度
- **Max Output Tokens（最大输出token）**：限制生成长度
- **Total Token Budget（总token预算）**：KV cache 的最大容量决定了总 token 预算

$$\text{Max Concurrent Requests} = \frac{\text{Total KV Cache Memory}}{\text{Max Seq Len} \times \text{Per-token KV Size}}$$

### Queue Management
请求队列的管理策略：

- **Admission Control（准入控制）**：当系统负载过高时拒绝新请求
- **Request Prioritization（请求优先级）**：根据用户等级、请求类型设置优先级
- **Timeout Handling（超时处理）**：超时请求自动取消并释放资源
"""

expansions[159] = r"""
### SGLang
**SGLang** 是另一个重要的 LLM 服务系统，专注于编程式的 LLM 交互：

- **RadixAttention**：基于基数树的 KV cache 管理，自动检测和复用共享前缀
- **Structured Generation（结构化生成）**：原生支持 JSON 模式、正则表达式约束
- **Multi-call Optimization（多调用优化）**：自动优化多次 LLM 调用的执行顺序

### Deployment Patterns
LLM 部署的常见架构模式：

**单模型单GPU**：最简单，适合 7B 以下模型
**单模型多GPU（张量并行）**：适合 13B-70B 模型
**多副本负载均衡**：水平扩展，提高吞吐量
**模型网关**：统一入口，路由到不同模型

### Latency Optimization Techniques
降低推理延迟的技术栈：

- **CUDA Graph（CUDA图）**：捕获和重放 GPU 操作序列，减少 CPU 开销
- **Custom CUDA Kernels（自定义CUDA内核）**：针对特定操作编写优化内核
- **Flash Attention**：减少 HBM 访问，提高注意力计算效率
- **Compiler Optimization（编译器优化）**：使用 torch.compile 或 TensorRT 优化计算图

### Model Parallelism Strategies for Serving
大模型推理的并行策略：

- **Tensor Parallelism（张量并行）**：在注意力和 FFN 层切分权重矩阵。通常在同一节点的 GPU 之间使用（需要高带宽通信）
- **Pipeline Parallelism（流水线并行）**：将不同层分配到不同 GPU。适合跨节点部署
- **Expert Parallelism（专家并行）**：MoE 模型中，将不同专家分配到不同 GPU

推理时的并行策略选择：
- 8-GPU 节点内：优先使用 TP（NVLink 带宽足够）
- 跨节点：使用 PP（减少通信量）
- MoE 模型：EP + TP 组合
"""

expansions[160] = r"""
### Chunk Overlap Strategy
**Overlap（重叠）** 的设计对于避免信息丢失至关重要：

- **Fixed Overlap（固定重叠）**：相邻块重叠固定数量的字符/token
- **Sentence Boundary Overlap（句子边界重叠）**：在句子边界处重叠，确保完整句子在至少一个块中
- **Overlap Size（重叠大小）** 的选择：
  - 太小：可能在关键位置丢失上下文
  - 太大：增加存储和计算成本，增加重复检索

通常 overlap 设为 chunk size 的 10-20%。

### Multi-Modal Chunking
针对包含多种内容类型的文档的分块策略：

- **文本+图片**：将图片的描述文本与图片关联，形成图文对块
- **文本+表格**：将表格转换为文本描述或保持结构化格式
- **文本+代码**：代码块保持完整，不在代码中间断开
- **跨模态引用**：保持跨模态引用的完整性（如"如图1所示"与图1在同一块中）

### Chunking Pipeline Optimization
生产环境中的分块流水线优化：

- **Parallel Processing（并行处理）**：多文档并行分块
- **Caching（缓存）**：缓存分块结果避免重复处理
- **Incremental Chunking（增量分块）**：文档更新时只重新分块变化部分
- **Quality Monitoring（质量监控）**：监控分块质量指标（如块内语义一致性、块间信息重叠度）

### Practical Recommendations
基于不同应用场景的分块建议：

| 应用场景 | 推荐策略 | 块大小 | 重叠 |
|---------|---------|--------|------|
| 通用问答 | 递归字符 | 500 | 50 |
| 法律文档 | 按章节分割 | 1000 | 100 |
| 代码文档 | 按函数/类 | 自适应 | 0 |
| 学术论文 | 按段落 + 语义 | 300-500 | 50 |
| 技术手册 | 按标题层级 | 500-800 | 80 |
"""

expansions[161] = r"""
### Embedding Model Training Pipeline
现代嵌入模型的训练通常分为多个阶段：

**阶段 1：Pre-training（预训练）**
- 在大规模文本对上进行对比学习预训练
- 使用弱监督信号（如标题-正文、问题-回答）

**阶段 2：Fine-tuning（微调）**
- 在高质量标注数据上微调
- 使用困难负样本提升区分能力

**阶段 3：Instruction Tuning（指令微调）**（如 E5-instruct, GTE）
- 使用自然语言指令描述检索任务
- 使不同检索任务使用不同的指令前缀
- 提升模型在多种检索场景下的泛化能力

### Embedding Dimension vs Quality
嵌入维度的选择涉及质量与效率的权衡：

$$\text{Storage} = N \times d \times 4 \text{ bytes (FP32)}$$

对于 100 万个文档：
- 384 维：~1.5 GB
- 768 维：~3 GB
- 1536 维：~6 GB

使用 Matryoshka 嵌入时可以动态调整维度，在不同场景下取得最优的质量-效率平衡。

### Domain Adaptation
将通用嵌入模型适配到特定领域：

- **继续训练**：在领域数据上继续对比学习
- **领域特定负样本**：使用领域内的困难负样本
- **数据增强**：使用 LLM 生成领域相关的训练数据对
- **评估**：在领域特定的测试集上评估，而非仅看通用基准
"""

expansions[162] = r"""
### HNSW Parameter Tuning Guide
HNSW 索引的关键参数调优：

**建图参数**：
- **M（连接数）**：每个节点的双向连接数。更大的 M 提高召回率但增加内存和构建时间。推荐 16-64
- **efConstruction（构建搜索宽度）**：建图时的候选集大小。更大值提高索引质量。推荐 200-500

**查询参数**：
- **efSearch（查询搜索宽度）**：搜索时的候选集大小。更大值提高召回率但增加延迟。推荐 32-256

$$\text{Memory per vector} \approx d \times 4 + M \times 2 \times (4 + 4) \text{ bytes}$$

### Filtering in Vector Search
向量搜索中的过滤（Filtered Search）是实际应用的常见需求：

- **Pre-filtering（前置过滤）**：先过滤再搜索。精确但可能导致候选集太小
- **Post-filtering（后置过滤）**：先搜索再过滤。可能返回不足 k 个结果
- **In-filter（内置过滤）**：在搜索过程中同时过滤。最优但实现复杂

不同向量数据库对过滤的支持程度不同：
- Milvus、Qdrant 支持高效的内置过滤
- FAISS 原生不支持过滤，需要外部实现

### Data Lifecycle Management
向量数据库的数据生命周期管理：

- **Upsert（插入/更新）**：当源文档更新时，需要更新对应的向量
- **Deletion（删除）**：支持按 ID 或按条件删除
- **Compaction（压缩）**：清理被删除的向量，回收空间
- **Backup/Restore（备份/恢复）**：定期备份索引和数据
- **Versioning（版本管理）**：管理嵌入模型更新导致的向量版本差异

### Cost Estimation
向量数据库的成本估算：

$$\text{Memory} = N \times (d \times 4 + \text{metadata\_size} + \text{index\_overhead})$$

对于 1000 万条 768 维向量（HNSW, M=16）：
- 向量存储：~30 GB
- HNSW 索引：~5 GB
- 元数据（假设100字节/条）：~1 GB
- 总计：约 36 GB
"""

expansions[163] = r"""
### Agentic RAG
**Agentic RAG（智能体RAG）** 使用 LLM 作为智能体来协调检索和生成过程：

- **Tool Use（工具使用）**：LLM 可以调用不同的检索工具（向量搜索、关键词搜索、SQL 查询、API 调用）
- **Planning（规划）**：LLM 制定检索计划，决定查询顺序和策略
- **Reflection（反思）**：检查已检索的信息是否足够，决定是否需要更多检索

这种方法最灵活但也最复杂，适合需要多种信息源的复杂问题。
"""

expansions[164] = ""  # Already meets 5500+


def main():
    for node_id in range(149, 165):
        filepath = os.path.join(TRANS_DIR, f'node_{node_id}.txt')
        if not os.path.exists(filepath):
            continue

        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        expansion = expansions.get(node_id, "")
        if not expansion.strip():
            print(f"Node {node_id}: no expansion needed (len={len(content)})")
            continue

        # Insert expansion before "## Interview Tips"
        marker = "## Interview Tips"
        if marker in content:
            idx = content.index(marker)
            new_content = content[:idx] + expansion.strip() + "\n\n" + content[idx:]
        else:
            new_content = content + "\n" + expansion.strip()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Node {node_id}: expanded from {len(content)} to {len(new_content)} chars")


if __name__ == "__main__":
    main()
