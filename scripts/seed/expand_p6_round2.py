#!/usr/bin/env python3
# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Second round of expansion for nodes still under 5500 chars."""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TRANS_DIR = os.path.join(os.path.dirname(__file__), 'node_translations')

# Target: at least 5500 chars
TARGET = 5500

expansions2 = {}

expansions2[149] = r"""
### Attention Pattern Analysis
GPT 系列中注意力模式的分析揭示了模型的工作机制：

- **Induction Heads（归纳头）**：在 GPT-2 中发现的特殊注意力头，专门负责检测和延续序列模式。它们是 ICL 能力的关键组成部分
- **Previous Token Heads（前一token头）**：总是关注前一个 token 的注意力头，用于基础的序列建模
- **Positional Heads（位置头）**：关注特定相对位置的注意力头

这些分析对理解和改进 LLM 有重要价值，也是 **Mechanistic Interpretability（机制可解释性）** 研究的基础。

### GPT-4 Technical Speculation
虽然 OpenAI 没有公开 GPT-4 的完整架构细节，但根据泄露信息和分析：

- 可能使用 8x220B 的 MoE 架构（8 个专家，每个约 220B 参数）
- 总参数约 1.8T，活跃参数约 220B
- 使用 128K 上下文窗口
- 训练成本估计超过 1 亿美元
- 支持视觉输入（GPT-4V）
"""

expansions2[150] = r"""
### Open Source Model Ecosystem
开源 LLM 生态系统的快速发展改变了 AI 行业格局：

**主要开源模型系列**：
- **LLaMA 系列**（Meta）：LLaMA-1/2/3，从 7B 到 405B
- **Mistral 系列**（Mistral AI）：Mistral 7B, Mixtral 8x7B/8x22B
- **Qwen 系列**（阿里巴巴）：Qwen 1.5/2，强调多语言能力
- **DeepSeek 系列**（DeepSeek）：DeepSeek V2/V3，MoE 架构创新
- **Gemma 系列**（Google）：轻量级开源模型

**开源 vs 闭源的权衡**：

| 维度 | 开源模型 | 闭源API |
|------|---------|---------|
| 成本 | 推理硬件成本 | API调用费用 |
| 定制性 | 完全可控 | 有限 |
| 数据隐私 | 数据不出本地 | 需传输到第三方 |
| 最新性能 | 通常落后 | 通常领先 |
| 部署复杂度 | 高 | 低 |

### Fine-tuning Ecosystem
开源模型带来了丰富的微调生态：

- **Axolotl**：支持多种微调策略的统一框架
- **LLaMA-Factory**：中文社区主导的微调工具
- **Unsloth**：通过自定义内核实现 2x 训练加速
- **TRL (Transformer Reinforcement Learning)**：HuggingFace 的 RLHF/DPO 训练库
"""

expansions2[151] = r"""
### Multi-Epoch Training Debate
关于预训练数据是否应该重复使用存在争议：

- **传统观点**：每个 token 只应训练一次（单 epoch），重复会导致过拟合
- **新发现**：对于高质量数据，4-5 个 epoch 仍可以持续降低损失
- **Scaling Laws for Repeating Data**（Muennighoff et al., 2023）：数据重复的边际收益随重复次数递减，$\text{Loss} \propto R^{-0.12}$，其中 $R$ 是重复次数
- **实践建议**：低质量数据严格单 epoch，高质量数据可以适度重复

### Data Contamination in Pre-training
预训练数据中的测试数据污染是一个严重问题：

- 网页数据可能包含基准测试的题目和答案
- 需要在数据处理阶段进行去污染
- 方法：n-gram 匹配、模糊匹配、perplexity-based 检测
- 一些模型（如 Phi 系列）被质疑训练数据中包含了基准测试数据

### Pre-training Loss Landscape
大规模预训练的损失曲线特征：

- **快速下降阶段**（前 5-10%）：模型学习基本语法和常见模式
- **稳定下降阶段**（10-80%）：模型学习更复杂的知识和能力
- **平台/微调阶段**（80-100%）：收益递减，学习率退火配合高质量数据
- **Grokking（顿悟）**：在某些情况下，模型可能在训练后期突然在特定能力上取得突破
"""

expansions2[152] = r"""
### Instruction Following Dimensions
SFT 需要教会模型的指令跟随维度：

- **Format Following（格式跟随）**：按要求输出 JSON、Markdown、列表等格式
- **Length Control（长度控制）**：按要求生成指定长度的内容
- **Style Adaptation（风格适配）**：正式/口语、技术/通俗等风格切换
- **Constraint Following（约束跟随）**：遵循"不要提及X"、"必须包含Y"等约束
- **Role Playing（角色扮演）**：按系统提示中定义的角色行事

### Self-Instruct Pipeline
**Self-Instruct（自指令）**（Wang et al., 2023）是一种低成本的 SFT 数据生成方法：

1. 从 175 个人工编写的种子任务开始
2. 使用 LLM 生成新的指令
3. 过滤与已有指令过于相似的指令
4. 使用 LLM 为新指令生成回答
5. 过滤低质量的指令-回答对

这种方法大大降低了 SFT 数据的获取成本，但生成数据的质量取决于种子任务的质量和多样性。

### Multi-task SFT
**Multi-task SFT（多任务SFT）** 在多种任务上同时训练：

- 混合不同类型的任务：问答、摘要、翻译、编程、数学、创意写作
- 每种任务的数据量需要平衡——过多某类任务会导致其他能力退化
- **Task Sampling（任务采样）**：通常对小任务过采样，大任务欠采样，平衡每步训练的任务分布
"""

expansions2[153] = r"""
### RLHF Training Pipeline Details
完整的 RLHF 训练流程的工程实现：

**数据准备**：
- 收集 prompt 集合（可以从 SFT 训练数据中复用）
- 为每个 prompt 生成多个回答（通常 4-8 个）
- 人类标注员对回答进行成对比较排序

**训练循环**（PPO 阶段）：
1. 从 prompt 集合中采样
2. 策略模型生成回答
3. 奖励模型打分
4. 计算 KL 惩罚：$\text{reward}' = R(x, y) - \beta \cdot \text{KL}$
5. 使用 PPO 更新策略模型
6. 定期更新参考模型（如每 N 步同步一次）

### RLHF vs DPO Performance Analysis
在实际应用中的性能对比：

- **小规模模型**（7B-13B）：DPO 通常与 RLHF 表现接近，且工程成本低得多
- **大规模模型**（70B+）：RLHF（PPO）在某些指标上优于 DPO，尤其是在需要在线探索的场景
- **领域特定**：对于有明确奖励信号的任务（如代码正确性），RLHF 优势更明显
- **迭代改进**：PPO 支持多轮迭代（生成->标注->训练），DPO 需要重新收集偏好数据

### Practical Tips for Alignment Training
对齐训练的实用建议：

- 从 DPO 开始，如果效果不足再考虑 PPO
- 数据质量 > 数据量 > 算法选择
- KL 系数 $\beta$ 的选择通过小规模实验确定（通常 0.05-0.2）
- 始终保留一个未对齐的基座模型作为对照
"""

expansions2[154] = r"""
### When to Use LoRA vs Full Fine-tuning
选择 LoRA 还是全量微调的决策指南：

**推荐使用 LoRA 的场景**：
- GPU 资源有限（单张或少量 GPU）
- 需要维护多个任务的适配器
- 微调数据量较小（< 100K 样本）
- 需要快速迭代和实验

**推荐全量微调的场景**：
- 充足的计算资源
- 目标任务与预训练分布差异很大
- 追求最优性能
- 只需要一个最终模型

### LoRA Initialization Strategies
初始化策略对 LoRA 性能有影响：

- **标准初始化**：$B = 0$（零初始化），$A \sim \mathcal{N}(0, \sigma^2)$（随机初始化）
- **PiSSA**：使用 SVD 分解原始权重的主成分初始化 LoRA 矩阵
- **OLoRA**：正交初始化，确保 A 和 B 的列/行正交

零初始化 B 矩阵确保训练开始时 LoRA 不改变原始模型行为，这是一个重要的设计选择。

### Memory Comparison
不同微调方法的显存对比（7B 模型，BF16）：

| 方法 | 模型权重 | 优化器 | 梯度 | 总计 |
|------|---------|--------|------|------|
| 全量微调 | 14 GB | 28 GB | 14 GB | ~56 GB |
| LoRA (r=16) | 14 GB | 0.16 GB | 0.08 GB | ~14.3 GB |
| QLoRA (4bit) | 3.5 GB | 0.16 GB | 0.08 GB | ~3.8 GB |
"""

expansions2[155] = r"""
### Safety and Robustness Evaluation
LLM 安全性评估的关键维度：

- **TruthfulQA**：测试模型是否会生成常见的错误信息
- **BBQ (Bias Benchmark for QA)**：检测社会偏见
- **AdvBench**：对抗攻击下的安全性
- **Red Teaming（红队测试）**：系统性的对抗测试

**Jailbreak（越狱）** 评估：
- 测试模型是否能被诱导生成有害内容
- 常见攻击方式：角色扮演、编码混淆、多轮渐进式引导
- 评估指标：**Attack Success Rate (ASR，攻击成功率)**

### Evaluation at Scale
大规模评估的工程挑战：

- **Parallel Evaluation（并行评估）**：使用多 GPU 并行运行评估
- **Reproducibility（可复现性）**：固定随机种子、采样参数
- **Cost Management（成本管理）**：智能调度评估任务
- **Result Aggregation（结果汇总）**：跨多个基准的综合评分

**Open LLM Leaderboard**（HuggingFace）提供了标准化的评估流水线，任何人都可以提交模型进行评估。

### Custom Evaluation Design
为特定业务场景设计评估的步骤：

1. **定义评估维度**：与业务目标对齐（如准确性、时延、安全性）
2. **构建测试集**：覆盖核心用例和边缘情况
3. **设计评分标准**：明确的评分 rubric，减少主观性
4. **选择评估方法**：自动指标 + 人类评估 + LLM-as-Judge 组合
5. **建立基线**：使用现有最佳模型作为对照
6. **持续监控**：在线环境中的持续评估和异常检测
"""

expansions2[156] = r"""
### Practical KV Cache Sizing
实际部署中 KV cache 大小的规划：

对于 LLaMA-2 7B（32层，32头，head_dim=128，GQA 关闭）：

$$\text{KV per token} = 2 \times 32 \times 32 \times 128 \times 2 = 524,288 \text{ bytes} \approx 0.5 \text{ MB}$$

| 配置 | 内存需求 | 可并发请求数 (24GB GPU余量 10GB) |
|------|---------|-------------------------------|
| seq=2048 | 1 GB/req | 10 |
| seq=4096 | 2 GB/req | 5 |
| seq=8192 | 4 GB/req | 2 |

这个计算直接决定了服务系统的最大并发量和吞吐量。
"""

expansions2[157] = r"""
### Weight-Only vs Weight-Activation Quantization
两种主要的量化策略对比：

**Weight-Only Quantization（仅权重量化）**（W4A16/W8A16）：
- 仅量化模型权重，激活值保持高精度
- 优势：实现简单，质量损失小
- 适用：decode 阶段（内存密集，瓶颈是权重读取）
- 代表：GPTQ、AWQ

**Weight-Activation Quantization（权重-激活联合量化）**（W8A8）：
- 同时量化权重和激活值
- 优势：利用 INT8 矩阵乘法硬件加速（如 NVIDIA Tensor Cores）
- 挑战：激活值的异常值使量化困难
- 代表：SmoothQuant、FP8

### Calibration Data Selection
量化校准数据的选择对量化质量有重要影响：

- 校准数据应代表目标使用场景的分布
- 通常使用 128-512 个样本
- 过少的样本可能导致量化参数不准确
- 过多的样本增加量化时间但边际收益递减
"""

expansions2[159] = r"""
### Benchmarking LLM Serving
LLM 服务系统的基准测试方法：

- **ShareGPT Trace（ShareGPT 轨迹）**：使用真实的用户对话分布进行测试
- **Synthetic Workload（合成负载）**：控制输入/输出长度分布
- **Load Testing（负载测试）**：逐步增加请求率直到系统饱和

关键测试场景：
| 场景 | 输入长度 | 输出长度 | 关注指标 |
|------|---------|---------|---------|
| 短对话 | 100 | 50 | TPOT, QPS |
| 长输入摘要 | 4000 | 200 | TTFT |
| 代码生成 | 500 | 500 | 端到端延迟 |
| RAG | 2000 | 300 | P99 延迟 |

### Auto-scaling Strategies
LLM 服务的自动扩缩容策略：

- **基于 QPS**：请求率超过阈值时扩容
- **基于队列长度**：等待队列过长时扩容
- **基于 GPU 利用率**：GPU 利用率过高时扩容
- **预测性扩容**：基于历史流量模式预测负载变化

### Multi-Model Serving
同时服务多个模型的架构：

- **Model Router（模型路由器）**：根据请求类型将请求路由到不同模型
- **Cascade（级联）**：先用小模型处理简单请求，复杂请求转发到大模型
- **Shared Backbone（共享骨干）**：多个 LoRA 适配器共享一个基础模型
"""

expansions2[160] = r"""
### Token-Level vs Character-Level Chunking
分块粒度的选择：

- **Character-level（字符级）**：简单但不考虑 token 边界
- **Token-level（token级）**：使用与嵌入模型相同的分词器，更精确
- **Word-level（词级）**：在词边界分割，避免断词

推荐使用 token 级分块，因为嵌入模型对 token 数量敏感。同样的字符数在不同语言中可能对应差异很大的 token 数（如中文每个字符通常是 1-2 个 token）。

### Chunking for Tables
表格数据的特殊处理：

- **Table Serialization（表格序列化）**：将表格转换为文本格式
  - Markdown 格式：`| col1 | col2 |`
  - CSV 格式：`col1, col2`
  - 自然语言描述：将行转换为自然语言句子
- **Table-Text Pairing（表文配对）**：将表格与其标题/描述配对
- **Row-Level Chunking（行级分块）**：对于大表格，按行分块并保留列标题
- **Table Understanding Models（表格理解模型）**：使用专用模型（如 Table-GPT）处理表格

### End-to-End Chunking Optimization
优化分块策略的系统方法：

1. 从递归字符分割开始（chunk_size=500, overlap=50）
2. 在目标查询集上评估检索质量
3. 尝试不同的 chunk_size（256, 512, 1024）
4. 评估语义分块是否带来显著提升
5. 如果文档有明确结构，尝试结构化分块
6. 最终方案通过 A/B 测试在生产环境验证
"""

expansions2[161] = r"""
### Cross-lingual Embeddings
**Cross-lingual Embeddings（跨语言嵌入）** 将不同语言的文本映射到同一语义空间：

- **Multilingual Pre-training（多语言预训练）**：在多种语言的数据上训练
- **Translation Pair Training（翻译对训练）**：使用平行语料（翻译对）进行对齐
- **Zero-shot Transfer（零样本迁移）**：在一种语言上训练，在其他语言上使用

代表模型：
- **multilingual-e5-large**：支持 100+ 种语言
- **paraphrase-multilingual-MiniLM-L12-v2**：轻量级多语言模型

### Embedding Compression
降低嵌入存储和检索成本的技术：

- **Product Quantization（乘积量化）**：将嵌入向量量化为紧凑表示
- **Binary Quantization（二值量化）**：将浮点嵌入转换为二值向量，大幅减少存储（32x 压缩）
- **Dimensionality Reduction（降维）**：PCA 或 Matryoshka 截断
- **Scalar Quantization（标量量化）**：将 FP32 转换为 INT8

$$\text{Binary} \approx \text{sign}(z), \quad \text{Hamming}(x, y) \propto \text{sim}(x, y)$$
"""

expansions2[162] = r"""
### Operational Considerations
向量数据库运维的关键考虑：

- **Index Rebuild（索引重建）**：当大量数据变更后可能需要重建索引
- **Monitoring（监控）**：监控查询延迟、召回率、内存使用
- **Sharding（分片）**：数据量超过单节点容量时进行分片
- **Replication（副本）**：通过副本实现高可用和读扩展

### Emerging Trends
向量数据库领域的新趋势：

- **Multi-vector Search（多向量搜索）**：支持 ColBERT 等保留多个向量的模型
- **Streaming Indexing（流式索引）**：实时索引新数据，无需重建
- **Hybrid Storage（混合存储）**：SSD + Memory 混合存储，支持更大规模
- **GPU-accelerated Search（GPU加速搜索）**：利用 GPU 加速向量搜索
"""

expansions2[163] = r"""
### Graph RAG
**Graph RAG（图RAG）** 将知识图谱与 RAG 结合：

- 从文档中抽取实体和关系构建知识图谱
- 检索时同时查询向量索引和图索引
- 通过图遍历发现多跳关系
- Microsoft 的 GraphRAG 通过社区检测和层次摘要提升全局问题的回答质量

### RAG Production Best Practices
生产环境中 RAG 系统的最佳实践：

- **Document Versioning（文档版本管理）**：跟踪文档更新，及时重新索引
- **Feedback Loop（反馈循环）**：收集用户反馈，持续优化检索和生成
- **Fallback Strategy（降级策略）**：检索失败时的降级方案（如直接用 LLM 回答）
- **Citation（引用）**：在回答中标注信息来源，便于用户验证
- **Guardrails（护栏）**：输出过滤，防止生成不当内容
"""

def main():
    for node_id in range(149, 165):
        filepath = os.path.join(TRANS_DIR, f'node_{node_id}.txt')
        if not os.path.exists(filepath):
            continue

        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        if len(content) >= TARGET:
            print(f"Node {node_id}: already at {len(content)} chars, skipping")
            continue

        expansion = expansions2.get(node_id, "")
        if not expansion.strip():
            print(f"Node {node_id}: no expansion defined (len={len(content)})")
            continue

        marker = "## Interview Tips"
        if marker in content:
            idx = content.index(marker)
            new_content = content[:idx] + expansion.strip() + "\n\n" + content[idx:]
        else:
            new_content = content + "\n" + expansion.strip()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Node {node_id}: expanded from {len(content)} to {len(new_content)} chars (need {TARGET})")


if __name__ == "__main__":
    main()
