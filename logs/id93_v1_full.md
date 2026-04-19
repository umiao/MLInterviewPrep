# NLP & LLM Systems

## Overview

**Natural Language Processing & Large Language Model Systems** (NLP & LLM, 自然语言处理与大语言模型系统) 设计涵盖围绕语言模型构建生产系统的各个方面：聊天机器人、内容生成、实体提取和 **Retrieval-Augmented Generation** (RAG, 检索增强生成) 应用。该主题在面试中的重要性近年来急剧上升。资深 **Machine Learning Engineer** (MLE, 机器学习工程师) 必须设计在质量、延迟、成本和安全性之间取得平衡的系统。

LLM 系统的核心挑战包括：**Hallucination** (幻觉) 控制、推理成本优化、输出质量评估，以及随着模型能力快速迭代保持系统可适配性。

## Core Concepts

### LLM Application Architecture

生产级 LLM 应用的标准架构包含多个保障层：

```
用户查询 -> [Guard Rails（防护栏）] -> [Router / Intent（路由/意图）]
    -> [Retrieval (RAG)] -> [Prompt Construction（提示构建）]
    -> [LLM Inference（LLM 推理）] -> [Output Validation（输出验证）]
    -> [Response Caching（响应缓存）] -> 用户响应
```

每一层都有明确的职责和延迟预算。**Guard Rails** (防护栏) 在输入端阻止有害内容和 **Prompt Injection** (提示注入) 攻击，**Output Validation** (输出验证) 在输出端检测幻觉、**Personally Identifiable Information** (PII, 个人身份信息) 泄露和有害内容。

### RAG System Design

RAG 是知识密集型 LLM 应用的默认架构模式，通过检索外部知识来减少幻觉：

$$
P(\text{answer} | q) = \sum_{d \in \text{TopK}} P(\text{answer} | q, d) \cdot P(d | q)
$$

该公式表示最终答案的概率是各检索文档下条件概率的加权和，权重由文档与查询的相关性决定。

| Component | Option | Latency Budget |
|-----------|--------|-----------------|
| **Embedding** (向量化) | OpenAI, E5, BGE | 10-30ms |
| **Vector Database** (向量数据库) | Pinecone, Weaviate, pgvector | 10-50ms |
| **Re-ranker** (重排序器) | Cross-encoder, Cohere | 50-100ms |
| **LLM** | GPT-4, Claude, Llama | 500-5000ms |

RAG 系统的关键设计决策：
- **Chunking Strategy** (分块策略)：固定长度 vs 语义分段 vs 递归分割。块大小影响检索精度和上下文窗口利用率。
- **Embedding Model** (向量化模型)：通用 vs 领域微调。领域微调通常提升 10-20% 的检索质量。
- **Top-K Selection** (Top-K选择)：检索文档数量的权衡——更多文档增加召回但也增加噪声和成本。

### Prompt Engineering Patterns

**Prompt Engineering** (提示工程) 是 LLM 系统中成本最低、效果最直接的优化手段：

| Pattern | 适用场景 | 示例 |
|---------|---------|------|
| **Few-shot Learning** (少样本学习) | 分类、实体提取 | 在提示中提供 3-5 个标注示例 |
| **Chain-of-Thought** (思维链) | 推理任务 | "Let's think step by step..." |
| **Self-consistency** (自一致性) | 提高准确率 | 采样 N 个响应，多数投票 |
| **ReAct** (推理+行动) | 工具调用代理 | Reason -> Act -> Observe 循环 |

### Cost Optimization

LLM 推理成本计算：

$$
\text{Cost per query} = \frac{\text{input\_tokens} \times p_{\text{in}} + \text{output\_tokens} \times p_{\text{out}}}{1000}
$$

关键优化策略：
- **Semantic Caching** (语义缓存)：使用 Embedding 相似度匹配相似查询，避免重复推理
- **Prompt Compression** (提示压缩)：去除冗余上下文，减少输入 Token 数
- **Model Routing** (模型路由)：简单查询用小模型，复杂查询用大模型——类似 **Cascade** (级联) 架构
- **Continuous Batching** (连续批处理)：动态组批提高 GPU 利用率

### Evaluation Framework

LLM 系统的评估是最大挑战——传统 ML 指标无法完全衡量生成质量：

| 评估维度 | 指标 | 方法 |
|---------|------|------|
| 相关性 | 回答正确性 | **LLM-as-Judge** (LLM做评判)、人工评估 |
| 忠实度 | 基于上下文的事实性 | **Natural Language Inference** (NLI, 自然语言推理) 模型或引用检查 |
| 延迟 | **Time To First Token** (TTFT, 首Token延迟) | P50/P95 监控 |
| 安全性 | 有害内容、PII 泄露 | 分类器防护栏 |
| 成本 | 每查询费用 | Token 计数 |

## Implementation

```python
from dataclasses import dataclass

@dataclass
class RAGResult:
    answer: str
    sources: list[str]
    latency_ms: float

def simple_rag_pipeline(
    query: str, embedder, vector_db, llm,
    top_k: int = 5,
) -> RAGResult:
    # 最小化 RAG 管道：向量化 -> 检索 -> 生成
    import time
    start = time.monotonic()
    q_emb = embedder.encode(query)
    docs = vector_db.search(q_emb, top_k=top_k)
    context = "\n\n".join(d.text for d in docs)
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer based on the context above:"
    )
    answer = llm.generate(prompt)
    elapsed = (time.monotonic() - start) * 1000
    return RAGResult(answer=answer, sources=[d.id for d in docs], latency_ms=elapsed)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| RAG | 知识密集型应用 | 检索减少幻觉；分块策略至关重要 |
| 模型路由 | 成本优化 | 简单查询用小模型，复杂查询用大模型 |
| 防护栏 | 安全关键应用 | 输入/输出分类器 + PII 检测 |
| 流式传输 | 聊天应用 | **Server-Sent Events** (SSE, 服务器发送事件) 逐 Token 传输，改善感知延迟 |
| 评估管道 | 任何 LLM 应用 | 自动评估（LLM-as-Judge）+ 人工标注 |

### Common Interview Questions
- [ ] 使用 LLM 设计客户支持聊天机器人
- [ ] 如何为企业文档构建 RAG 系统？
- [ ] 设计基于 LLM 的内容审核系统
- [ ] 如何大规模评估 LLM 输出质量？
- [ ] 设计 LLM 驱动的代码生成系统

## Comparisons

| 维度 | 微调模型 | RAG | Prompt Engineering |
|------|---------|-----|-------------------|
| 知识更新 | 需要重训练 | 更新索引即可 | 更新提示即可 |
| 成本 | 高（训练费用） | 中（基础设施） | 低 |
| 延迟 | 快（推理） | +检索开销 | 最小 |
| 幻觉 | 中等 | 低（有据可查） | 高 |
| 定制化 | 深度 | 中等 | 表面 |

## Key Takeaways
- [ ] RAG 是知识密集型 LLM 应用的默认模式
- [ ] 分块策略和检索质量通常比 LLM 选择更重要
- [ ] 始终设计防护栏（输入验证、输出过滤、PII 检测）
- [ ] 通过缓存和模型路由进行成本优化在规模化时至关重要
- [ ] 评估是最难的部分——投资于自动化 + 人工评估管道


## Advanced Topics

### LLM Fine-tuning Strategies

大模型的微调策略选择对系统效果和成本有重大影响：

| 策略 | 训练成本 | 效果 | 适用场景 |
|------|----------|------|----------|
| **Full Fine-tuning** (全量微调) | 极高 | 最好 | 有大量标注数据，需要深度定制 |
| **Low-Rank Adaptation** (LoRA, 低秩适应) | 低（仅训练 0.1% 参数） | 接近全量微调 | 资源受限，快速实验 |
| **Prefix Tuning** (前缀调优) | 低 | 中等 | 多任务共享基座模型 |
| **Reinforcement Learning from Human Feedback** (RLHF, 基于人类反馈的强化学习) | 高 | 对齐人类偏好 | 对话系统、安全对齐 |

### Evaluation of LLM Systems

LLM 系统的评估是一个开放性挑战，传统 NLP 指标（BLEU、ROUGE）无法充分衡量生成质量：

- **LLM-as-Judge** (LLM作为评判者)：使用强大的 LLM（如 GPT-4）评估其他模型的输出质量
- **Chatbot Arena / Elo Rating** (Elo评分)：通过人类盲评打分建立模型排名
- **Red Teaming** (红队测试)：系统性地尝试让模型产生有害输出，评估安全性边界
- **Domain-specific Benchmarks** (领域基准测试)：针对特定应用场景设计的评估集

### Hallucination Mitigation

**Hallucination** (幻觉) 是 LLM 系统的核心挑战。缓解策略包括：RAG 提供事实依据、**Self-consistency** (自洽性检查) 多次采样取一致答案、**Fact-Checking Pipeline** (事实核查管道) 对生成内容进行后验证、以及在 prompt 中明确要求模型在不确定时说"不知道"。工业系统通常将多种策略组合使用，并通过置信度分数决定是否需要人工审核。