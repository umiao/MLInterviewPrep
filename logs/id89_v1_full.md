# Search & Retrieval Systems

## Overview

**Search & Retrieval** (搜索与检索) 系统是互联网产品中最核心的基础设施之一，驱动着从网页搜索到电商商品查找、从企业知识库到社交内容发现的各类应用场景。一个资深 **MLE** (Machine Learning Engineer，机器学习工程师) 必须能够设计端到端的搜索流水线，涵盖 **Query Understanding** (查询理解)、多阶段检索、相关性排序和实时索引等关键模块。该主题频繁出现在 Google、Meta、LinkedIn 和 Amazon 的面试中。

搜索系统的核心挑战在于：如何在数十亿文档中，以毫秒级延迟返回最相关的少量结果。现代搜索架构通过 **Multi-Stage Funnel** (多阶段漏斗) 逐步缩小候选集，从而在计算成本和结果质量之间取得平衡。

## Core Concepts

### Query Understanding Pipeline

**Query Understanding** (查询理解) 管道将用户原始输入转化为结构化的检索意图，是搜索系统中投资回报率最高的模块之一：

| 阶段 | 技术 | 示例 |
|------|------|------|
| **Tokenization（分词）** | WordPiece / **BPE** (Byte Pair Encoding，字节对编码) | "machine learning" -> ["machine", "learning"] |
| **Spell Correction（拼写纠错）** | 编辑距离 + **LM** (Language Model，语言模型) | "machin lerning" -> "machine learning" |
| **Query Expansion（查询扩展）** | 同义词注入、**PRF** (Pseudo Relevance Feedback，伪相关反馈) | "ML" -> "ML OR machine learning" |
| **Intent Classification（意图分类）** | BERT 分类器 | "buy iPhone 15" -> 商业购买意图 |
| **NER** (Named Entity Recognition，命名实体识别) | 序列标注模型 | "restaurants near Seattle" -> LOC: Seattle |

查询理解的每个阶段都会影响下游检索的召回率。例如，拼写纠错可以挽回 5-10% 的流量，查询扩展可以将长尾查询的召回率提升 15-20%。

### Multi-Stage Retrieval Architecture

现代搜索系统采用多阶段检索架构，每个阶段在计算复杂度和候选数量之间做权衡：

$$
\text{Candidates} \xrightarrow{\text{L0: Boolean}} \xrightarrow{\text{L1: ANN}} \xrightarrow{\text{L2: Cross-Encoder}} \text{Top-K Results}
$$

- **L0 -- Inverted Index** (倒排索引)：基于 **BM25** 的稀疏检索，时间复杂度为 $O(\text{postings})$。倒排索引将每个词映射到包含该词的文档列表，支持高效的精确匹配。
- **L1 -- Dense Retrieval** (稠密检索)：**Bi-Encoder** (双编码器) 将查询和文档分别编码为向量，通过 **ANN** (Approximate Nearest Neighbor，近似最近邻) 搜索（如 **HNSW** (Hierarchical Navigable Small World，层级可导航小世界图) / ScaNN）返回 top-1000。延迟预算：10-50ms。
- **L2 -- Re-ranking** (重排序)：**Cross-Encoder** (交叉编码器) 对查询-文档对进行联合编码评分，捕获细粒度的语义交互。延迟：5-20ms（处理 top-100）。

### BM25 Scoring

**Best Matching 25** (BM25, BM25评分) 是经典的稀疏检索评分函数，至今仍是强基线：

$$
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}
$$

其中 $f(t,d)$ 是词频，$k_1 \approx 1.2$ 控制词频饱和度，$b \approx 0.75$ 控制文档长度归一化。**IDF** (Inverse Document Frequency，逆文档频率) 衡量词的稀有程度，稀有词获得更高权重。BM25 的优势在于无需训练数据、对精确匹配效果极好，但无法捕获语义相似性。

### Relevance Metrics

搜索质量的离线评估使用排序指标：

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i + 1)}
$$

**NDCG** (Normalized Discounted Cumulative Gain，归一化折损累积增益) 衡量排序质量，考虑了结果位置的折损效应——排在前面的结果权重更大。$r_i$ 是第 $i$ 个结果的相关性等级（通常 0-4）。在线指标（如点击率、停留时间、搜索成功率）在实际决策中比离线 NDCG 更重要。

### Learning to Rank

**LTR** (Learning to Rank，排序学习) 将排序问题建模为机器学习任务：

| 范式 | 损失函数 | 代表算法 |
|------|---------|---------|
| **Pointwise（逐点）** | 回归/分类损失 | 线性回归、GBDT |
| **Pairwise（逐对）** | 比较文档对的相对顺序 | **RankNet**、**LambdaRank** |
| **Listwise（列表级）** | 直接优化列表级指标 | **LambdaMART**、**ListNet** |

LambdaMART 至今仍是工业界最常用的 LTR 算法之一，它通过梯度提升树优化 NDCG 相关的 lambda 梯度。

## Implementation

```python
import numpy as np

def bm25_score(
    tf: float, df: int, doc_len: int,
    avg_dl: float, n_docs: int,
    k1: float = 1.2, b: float = 0.75,
) -> float:
    # BM25 单词项-文档评分
    idf = np.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
    tf_norm = (tf * (k1 + 1)) / (
        tf + k_1 * (1 - b + b * doc_len / avg_dl)
    )
    return float(idf * tf_norm)

def two_stage_retrieve(
    query_emb: np.ndarray,
    index,  # ANN 索引
    cross_encoder,
    query_text: str,
    doc_texts: list[str],
    top_k_ann: int = 100,
    top_k_final: int = 10,
) -> list[int]:
    # L1 ANN 检索 + L2 Cross-Encoder 重排序
    ids, _ = index.search(query_emb.reshape(1, -1), top_k_ann)
    candidates = ids[0].tolist()
    pairs = [(query_text, doc_texts[i]) for i in candidates]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [idx for idx, _ in ranked[:top_k_final]]
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 多阶段漏斗 | 任何搜索系统 | 每个阶段用更高的计算成本换取更高的精度 |
| 混合稀疏+稠密检索 | 网页/商品搜索 | BM25 处理精确匹配；稠密检索处理语义相似性 |
| 查询重写 | 模糊查询 | 基于 LLM 的重写可在不修改索引的情况下提升召回 |
| 实时索引 | 新鲜内容（新闻、社交） | 双索引架构：批量（每日）+ 实时（流式） |
| 排序学习 | 复杂相关性 | Pointwise、Pairwise（RankNet）、Listwise（LambdaMART） |

### Common Interview Questions
- [ ] 设计一个网页搜索引擎排序管道
- [ ] 如何大规模实现查询自动补全？
- [ ] 比较 BM25 与稠密检索——各自何时更优？
- [ ] 如何评估搜索质量（离线 vs 在线）？
- [ ] 为社交媒体信息流设计实时索引系统

## Comparisons

| 维度 | 稀疏检索 (BM25) | 稠密检索 (Bi-Encoder) | Cross-Encoder |
|------|----------------|---------------------|---------------|
| 延迟 | ~5ms | ~10-50ms (ANN) | ~100ms (top-100) |
| 精确匹配 | 优秀 | 较差 | 良好 |
| 语义匹配 | 较差 | 良好 | 优秀 |
| 索引大小 | 倒排索引 | 向量索引 | 无索引（逐对计算） |
| 训练数据 | 无需 | 需要正负样本对 | 需要带标签的样本对 |

## Key Takeaways
- [ ] 多阶段检索在延迟和质量之间取得平衡，是搜索系统的标准架构
- [ ] BM25 仍然是强基线——始终应包含稀疏信号
- [ ] 稠密检索实现语义匹配但需要 ANN 基础设施
- [ ] 在线指标（点击率、停留时间）比离线 NDCG 更具决策价值
- [ ] 查询理解通常是投资回报率最高的优化方向


## Advanced Topics

### Hybrid Retrieval Architecture

**Hybrid Retrieval** (混合检索) 是当前搜索系统的最佳实践，同时利用稀疏和稠密信号。通过 **RRF** (Reciprocal Rank Fusion，倒数排名融合) 合并两路结果：

$$\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

其中 $$r(d)$$ 为文档 $$d$$ 在排序 $$r$$ 中的排名，$$k$$ 为平滑常数（通常取 60）。混合检索通常比单独使用任一方法在 NDCG 上提升 5-15%。

### Query Rewriting with LLM

利用 **LLM** (Large Language Model，大语言模型) 进行查询改写是近年来的重要创新。LLM 可以理解用户的模糊意图并生成更适合检索的查询表达。这种方法不需要修改索引，是提升搜索质量的低成本高收益方案。同时，基于 LLM 的查询理解可以实现更复杂的意图解析，如多轮对话式搜索中的指代消解和上下文理解。

### Distributed Index Architecture

工业级搜索系统采用 **Sharding** (分片) + **Replication** (副本) 的分布式架构。索引按文档 ID 哈希或按主题进行分片，每个分片有多个副本保证高可用。查询执行采用 **Scatter-Gather** (分发-汇聚) 模式，将请求扇出到所有分片并行处理后合并结果。**Tiered Index** (分层索引) 策略将热门文档放入内存层，长尾文档放在磁盘层，优化整体资源利用率和查询尾部延迟。索引更新时使用 **Canary Query** (金丝雀查询) 机制进行质量回归检测，确保新索引不会导致搜索质量下降。