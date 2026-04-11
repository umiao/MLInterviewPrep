"""Translate and expand Pillar 3 ML System Design nodes (89-107) to Chinese."""
import os
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "mle_prep.db"
)

NODES = {}

# ============================================================
# NODE 89: Search & Retrieval Systems
# ============================================================
NODES[89] = r"""# Search & Retrieval Systems

## Overview

**Search & Retrieval（搜索与检索）** 系统是互联网产品中最核心的基础设施之一，驱动着从网页搜索到电商商品查找、从企业知识库到社交内容发现的各类应用场景。一个资深 **MLE (Machine Learning Engineer，机器学习工程师)** 必须能够设计端到端的搜索流水线，涵盖 **Query Understanding（查询理解）**、多阶段检索、相关性排序和实时索引等关键模块。该主题频繁出现在 Google、Meta、LinkedIn 和 Amazon 的面试中。

搜索系统的核心挑战在于：如何在数十亿文档中，以毫秒级延迟返回最相关的少量结果。现代搜索架构通过多阶段漏斗（Multi-Stage Funnel）逐步缩小候选集，从而在计算成本和结果质量之间取得平衡。

## Core Concepts

### Query Understanding Pipeline

**Query Understanding（查询理解）** 管道将用户原始输入转化为结构化的检索意图，是搜索系统中投资回报率最高的模块之一：

| 阶段 | 技术 | 示例 |
|------|------|------|
| **Tokenization（分词）** | WordPiece / **BPE (Byte Pair Encoding，字节对编码)** | "machine learning" -> ["machine", "learning"] |
| **Spell Correction（拼写纠错）** | 编辑距离 + **LM (Language Model，语言模型)** | "machin lerning" -> "machine learning" |
| **Query Expansion（查询扩展）** | 同义词注入、**PRF (Pseudo Relevance Feedback，伪相关反馈)** | "ML" -> "ML OR machine learning" |
| **Intent Classification（意图分类）** | BERT 分类器 | "buy iPhone 15" -> 商业购买意图 |
| **NER (Named Entity Recognition，命名实体识别)** | 序列标注模型 | "restaurants near Seattle" -> LOC: Seattle |

查询理解的每个阶段都会影响下游检索的召回率。例如，拼写纠错可以挽回 5-10% 的流量，查询扩展可以将长尾查询的召回率提升 15-20%。

### Multi-Stage Retrieval Architecture

现代搜索系统采用多阶段检索架构，每个阶段在计算复杂度和候选数量之间做权衡：

$$
\text{Candidates} \xrightarrow{\text{L0: Boolean}} \xrightarrow{\text{L1: ANN}} \xrightarrow{\text{L2: Cross-Encoder}} \text{Top-K Results}
$$

- **L0 -- Inverted Index（倒排索引）**：基于 **BM25** 的稀疏检索，时间复杂度为 $O(\text{postings})$。倒排索引将每个词映射到包含该词的文档列表，支持高效的精确匹配。
- **L1 -- Dense Retrieval（稠密检索）**：**Bi-Encoder（双编码器）** 将查询和文档分别编码为向量，通过 **ANN (Approximate Nearest Neighbor，近似最近邻)** 搜索（如 **HNSW (Hierarchical Navigable Small World，层级可导航小世界图)** / ScaNN）返回 top-1000。延迟预算：10-50ms。
- **L2 -- Re-ranking（重排序）**：**Cross-Encoder（交叉编码器）** 对查询-文档对进行联合编码评分，捕获细粒度的语义交互。延迟：5-20ms（处理 top-100）。

### BM25 Scoring

**BM25** 是经典的稀疏检索评分函数，至今仍是强基线：

$$
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}
$$

其中 $f(t,d)$ 是词频，$k_1 \approx 1.2$ 控制词频饱和度，$b \approx 0.75$ 控制文档长度归一化。**IDF (Inverse Document Frequency，逆文档频率)** 衡量词的稀有程度，稀有词获得更高权重。BM25 的优势在于无需训练数据、对精确匹配效果极好，但无法捕获语义相似性。

### Relevance Metrics

搜索质量的离线评估使用排序指标：

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i + 1)}
$$

**NDCG (Normalized Discounted Cumulative Gain，归一化折损累积增益)** 衡量排序质量，考虑了结果位置的折损效应——排在前面的结果权重更大。$r_i$ 是第 $i$ 个结果的相关性等级（通常 0-4）。在线指标（如点击率、停留时间、搜索成功率）在实际决策中比离线 NDCG 更重要。

### Learning to Rank

**LTR (Learning to Rank，排序学习)** 将排序问题建模为机器学习任务：

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
        tf + k1 * (1 - b + b * doc_len / avg_dl)
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
"""

# ============================================================
# NODE 90: Recommendation Systems
# ============================================================
NODES[90] = r"""# Recommendation Systems

## Overview

**Recommendation Systems（推荐系统）** 是 ML 系统设计面试中最常见的考题。推荐系统驱动着信息流、商品推荐、内容发现和匹配等核心产品功能。一个资深 MLE 必须能够设计端到端的推荐管道，涵盖 **Candidate Generation（候选生成）**、排序、重排序以及具备实时个性化能力的服务架构。

推荐系统的核心目标是：在海量物品库中，为每个用户找到最相关、最有价值的少量内容。这需要在用户兴趣建模、物品理解、实时上下文和业务目标之间进行多维度的平衡。

## Core Concepts

### System Architecture

推荐系统采用经典的多阶段漏斗架构，每个阶段逐步缩小候选集并增加模型复杂度：

```
用户请求
    |
    v
[Candidate Generation（候选生成）] -- 数千个物品, <50ms
    |
    v
[Ranking Model（排序模型）] -- 对 top-1000 评分, <100ms
    |
    v
[Re-ranking / Business Rules（重排序/业务规则）] -- 多样性、新鲜度、广告混排
    |
    v
[Served Results（最终结果）] -- top 10-50 个物品
```

### Candidate Generation Strategies

**候选生成** 是推荐系统的第一阶段，优化目标是 **Recall（召回率）**——确保好的物品不被遗漏：

| 策略 | 方法 | 优势 | 劣势 |
|------|------|------|------|
| **Collaborative Filtering（协同过滤）** | 用户-物品矩阵分解 | 捕获用户偏好模式 | 冷启动问题 |
| **Content-based（基于内容）** | 物品特征相似度 | 物品无冷启动 | 信息茧房效应 |
| **Two-tower（双塔模型）** | 独立的用户/物品编码器 | 可扩展的 ANN 服务 | 表达能力受限 |
| **Graph-based（基于图）** | 交互图上的 **GNN (Graph Neural Network，图神经网络)** | 信号丰富 | 基础设施复杂 |

多源候选融合是工业级推荐系统的标准做法：从协同过滤、内容相似、热门趋势、用户历史等多个来源获取候选，合并后送入排序阶段。

### Matrix Factorization

**Matrix Factorization（矩阵分解）** 是协同过滤的经典方法，将用户-物品交互矩阵分解为低维向量：

$$
\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \mathbf{q}_i
$$

其中 $\mu$ 是全局偏置，$b_u$ 和 $b_i$ 分别是用户和物品偏置，$\mathbf{p}_u$ 和 $\mathbf{q}_i$ 是用户和物品的隐向量。

带正则化的损失函数：

$$
\mathcal{L} = \sum_{(u,i) \in \mathcal{K}} (r_{ui} - \hat{r}_{ui})^2 + \lambda(\|\mathbf{p}_u\|^2 + \|\mathbf{q}_i\|^2 + b_u^2 + b_i^2)
$$

正则化项 $\lambda$ 防止过拟合，在稀疏数据场景下尤为重要。

### Deep Ranking Models

现代排序模型使用特征丰富的深度网络，融合多种信号：
- **用户特征**：人口统计、历史行为、上下文（时间、设备）
- **物品特征**：内容属性、流行度、新鲜度、预训练 Embedding
- **交叉特征**：用户-物品交互历史、共现统计

主流架构演进：**Wide & Deep** -> **DCN-v2 (Deep & Cross Network v2，深度交叉网络v2)** -> **DIN (Deep Interest Network，深度兴趣网络)** -> **DLRM (Deep Learning Recommendation Model，深度学习推荐模型)**。DIN 的核心创新是引入注意力机制，对用户历史行为序列中与当前候选物品相关的行为赋予更高权重。

### Ranking Loss Functions

**Pointwise（逐点）** 损失——将每个样本独立评分：
$$
\mathcal{L} = -\sum [y_i \log \hat{y}_i + (1 - y_i) \log(1 - \hat{y}_i)]
$$

**Pairwise（逐对）** 损失——**BPR (Bayesian Personalized Ranking，贝叶斯个性化排序)**：
$$
\mathcal{L} = -\sum_{(u,i,j)} \log \sigma(\hat{r}_{ui} - \hat{r}_{uj})
$$

其中 $(u,i,j)$ 表示用户 $u$ 对物品 $i$（正样本）的偏好高于物品 $j$（负样本）。BPR 直接优化排序关系，比 Pointwise 方法更适合排序任务。

## Implementation

```python
import numpy as np

class TwoTowerModel:
    # 简化的双塔候选生成模型

    def __init__(self, user_dim: int, item_dim: int, emb_dim: int) -> None:
        self.user_proj = np.random.randn(user_dim, emb_dim) * 0.01
        self.item_proj = np.random.randn(item_dim, emb_dim) * 0.01

    def user_embedding(self, user_feat: np.ndarray) -> np.ndarray:
        emb = user_feat @ self.user_proj
        return emb / (np.linalg.norm(emb) + 1e-8)

    def item_embedding(self, item_feat: np.ndarray) -> np.ndarray:
        emb = item_feat @ self.item_proj
        return emb / (np.linalg.norm(emb) + 1e-8)

    def score(self, user_feat: np.ndarray, item_feat: np.ndarray) -> float:
        u_emb = self.user_embedding(user_feat)
        i_emb = self.item_embedding(item_feat)
        return float(u_emb @ i_emb)
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 多阶段漏斗 | 任何推荐系统 | 候选生成（召回） -> 排序（精度） -> 重排序（业务目标） |
| 双塔 + ANN | 大规模物品库 | 预计算物品 Embedding，通过 HNSW 服务 |
| Feature Store | 实时特征 | 分离离线（批处理）和在线（流式）特征管道 |
| 探索-利用 | 冷启动/新颖性 | **Thompson Sampling（汤普森采样）** 或 epsilon-greedy 在重排序中使用 |
| 基于会话 | 短会话、未登录 | GRU/Transformer 对会话内点击序列建模 |

### Common Interview Questions
- [ ] 设计一个新闻信息流排序系统（Meta）
- [ ] 设计电商商品推荐系统（Amazon）
- [ ] 如何处理冷启动用户和物品？
- [ ] 如何平衡相关性、多样性和新鲜度？
- [ ] 设计一个推送通知系统——决定推送什么内容、何时推送

## Comparisons

| 维度 | 协同过滤 | 双塔模型 | Cross-Encoder 排序 |
|------|---------|---------|-------------------|
| 服务延迟 | 预计算 | ANN 查找 ~10ms | 逐对评分 ~50ms |
| 特征丰富度 | 仅用户-物品交互 | 中等 | 丰富的交叉特征 |
| 冷启动 | 差 | 较好（内容特征） | 最好 |
| 规模 | 百万级 | 十亿级（ANN） | 仅 Top-K |

## Key Takeaways
- [ ] 始终设计为多阶段漏斗，每个阶段有明确的延迟预算
- [ ] 双塔模型是大规模候选生成的主流方案
- [ ] 特征工程（尤其是实时特征）通常比模型架构更重要
- [ ] 离线指标（AUC、NDCG）必须通过在线 A/B 测试验证
- [ ] 多样性和探索对长期用户参与至关重要
"""

# ============================================================
# NODE 91: Ads & Click Prediction
# ============================================================
NODES[91] = r"""# Ads & Click Prediction

## Overview

**Ads & Click Prediction（广告与点击预测）** 系统是收入导向型 ML 系统的典型代表。广告系统融合了 **CTR (Click-Through Rate，点击率)** 预测、出价优化、拍卖机制和预算调控等多个技术模块。该主题是 Meta、Google、Amazon 等拥有广告业务公司的面试必考题。理解广告系统需要同时掌握经济学原理和 ML 技术。

广告系统的核心挑战在于：如何在用户体验、广告主 **ROI (Return on Investment，投资回报率)** 和平台收入之间取得三方平衡，同时满足毫秒级延迟和数十万 QPS 的性能要求。

## Core Concepts

### Ads Serving Pipeline

广告服务的完整流水线涵盖从请求到反馈的闭环：

```
广告请求 -> 候选筛选 -> CTR 预测 -> 出价计算
    -> 竞价排名 -> 广告展示 -> 点击/转化追踪 -> 模型更新
```

每个环节的延迟预算通常总计不超过 100ms，其中 CTR 模型推理约占 5-20ms。

### Click-Through Rate Prediction

CTR 模型预测用户在给定上下文下点击广告的概率 $P(\text{click} | \text{user, ad, context})$：

$$
\text{eCPM} = \text{CTR} \times \text{bid} \times 1000
$$

**eCPM (effective Cost Per Mille，有效千次展示成本)** 是广告排序的核心指标。拥有最高 eCPM 的广告赢得竞价（简化模型）。这个公式同时考虑了广告的相关性（CTR 反映用户兴趣）和商业价值（bid 反映广告主的出价意愿）。

### Feature Categories

广告 CTR 模型的特征可以分为四大类，每类的更新频率不同：

| 类别 | 示例 | 更新频率 |
|------|------|---------|
| 用户特征 | 人口统计、兴趣标签、行为历史 | 小时/天级 |
| 广告特征 | 创意素材、落地页、类目 | 广告变更时 |
| 上下文特征 | 时间、设备、页面内容 | 实时 |
| 交叉特征 | 用户-广告亲和度、历史 CTR | 实时 |

实时特征（如用户近期点击行为、当前会话上下文）往往是 CTR 提升的最大来源。

### Model Architecture Evolution

CTR 模型经历了五代演进，每一代引入了新的特征交互方式：

| 代际 | 模型 | 核心创新 |
|------|------|---------|
| 第1代 | **Logistic Regression（逻辑回归）** | 稀疏特征，可解释性强 |
| 第2代 | **GBDT + LR** | 非线性特征交叉 |
| 第3代 | **Wide & Deep** | 记忆性 + 泛化性的统一 |
| 第4代 | **DCN-v2 / DLRM** | 显式交叉网络，大规模 Embedding 表 |
| 第5代 | **DIN / DIEN (Deep Interest Evolution Network，深度兴趣演化网络)** | 对用户行为序列的注意力机制 |

### Auction Mechanisms

**Second-price auction（第二价格拍卖）**（经典 GSP 模型）：
$$
\text{payment} = \frac{\text{eCPM}_{\text{2nd}}}{\text{CTR}_{\text{winner}}}
$$

广告主实际支付的 **CPC (Cost Per Click，每次点击成本)** 等于第二高 eCPM 除以自己的 CTR。这种机制鼓励广告主如实出价。

**VCG (Vickrey-Clarke-Groves) Auction（VCG 拍卖）**：如实出价是占优策略。胜出者支付的费用等于其存在对其他参与者造成的外部性成本。VCG 拍卖保证了 **Incentive Compatibility（激励相容性）**，但实现复杂度较高。

近年来，许多广告平台转向 **First-price auction（第一价格拍卖）**，因为它更简单且收入更可预测，但需要广告主进行出价 shading（降低出价以避免多付）。

### Calibration

CTR 模型必须良好校准，才能正确定价：

$$
\text{Calibration} = \frac{\text{Predicted avg CTR}}{\text{Observed avg CTR}}
$$

校准比 $1.0$ 表示预测偏高，低于 $1.0$ 表示预测偏低。一个 AUC 很高但校准不良的模型会导致广告定价错误——高估 CTR 会导致广告主过度支付，低估 CTR 会导致平台收入损失。常用校准方法包括 **Platt Scaling（普拉特缩放）** 和 **Isotonic Regression（保序回归）**。

### Budget Pacing

**Budget Pacing（预算调控）** 确保广告主的预算在投放周期内均匀消耗，避免过早花完：

$$
\text{pacing\_multiplier} = \frac{\text{remaining\_budget}}{\text{ideal\_remaining\_budget}}
$$

当实际消耗超过计划时，降低出价系数来减缓投放速度；当消耗不足时，提高出价系数加速投放。

## Implementation

```python
import numpy as np

def compute_ecpm(ctr: np.ndarray, bid: np.ndarray) -> np.ndarray:
    # 计算有效千次展示成本用于广告排序
    return ctr * bid * 1000.0

def second_price_payment(
    winner_ctr: float, second_ecpm: float,
) -> float:
    # 第二价格拍卖中的每次点击成本计算
    if winner_ctr <= 0:
        return 0.0
    return second_ecpm / (winner_ctr * 1000.0)

def budget_pacing(
    remaining_budget: float, remaining_time_frac: float,
    spent_so_far: float, total_budget: float,
) -> float:
    # 预算调控乘数——平滑预算消耗
    ideal_spend = total_budget * (1.0 - remaining_time_frac)
    if ideal_spend <= 0:
        return 1.0
    return max(0.1, min(2.0, remaining_budget / ideal_spend))
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 多目标优化 | CTR + CVR + 质量 | 组合 $P(\text{click}) \times P(\text{convert}|\text{click}) \times \text{bid} \times \text{quality}$ |
| 延迟反馈 | 转化归因 | 转化事件延迟数小时/天到达；需要重要性加权 |
| 位置偏差 | 列表中的广告 | 高位置无论相关性如何都获得更多点击 |
| 探索-利用 | 新广告/创意 | 对冷启动广告使用 Thompson Sampling |
| 预算调控 | 广告活动优化 | 平滑消耗避免预算过早耗尽 |

### Common Interview Questions
- [ ] 为社交媒体广告平台设计 CTR 预测系统
- [ ] 如何处理模型训练中的延迟转化？
- [ ] 解释位置偏差及其去偏方法
- [ ] 如何设计广告活动的预算调控？
- [ ] 比较第一价格与第二价格拍卖

## Comparisons

| 维度 | 逻辑回归 | 深度 CTR (DCN-v2) | 序列模型 (DIN) |
|------|---------|-------------------|---------------|
| 训练速度 | 快 | 中等 | 慢 |
| 特征交互 | 手工交叉 | 自动学习 | 注意力机制 |
| 推理延迟 | <1ms | ~5ms | ~10ms |
| 冷启动 | 好（稀疏特征） | 中等 | 差（需要历史） |
| 可解释性 | 高 | 低 | 低 |

## Key Takeaways
- [ ] eCPM = CTR x Bid 是广告排序的基本公式
- [ ] 校准与区分度（AUC）同等重要
- [ ] 位置偏差校正对无偏训练至关重要
- [ ] 实时特征（近期点击、会话上下文）贡献最大增益
- [ ] 预算调控和拍卖设计与 ML 模型同等重要
"""

# ============================================================
# NODE 92: Marketplace & Logistics
# ============================================================
NODES[92] = r"""# Marketplace & Logistics

## Overview

**Marketplace & Logistics（交易市场与物流）** ML 系统处理供需匹配、动态定价、**ETA (Estimated Time of Arrival，预计到达时间)** 预测和物流优化等核心问题。这类系统常见于 Uber、DoorDash、Airbnb 等双边平台。系统需要在实时约束下平衡多方利益相关者（买方、卖方、平台）的目标。

交易市场系统的独特挑战在于：供需双方的行为相互影响，定价决策会改变供给和需求的分布，形成复杂的动态博弈。这要求 ML 工程师不仅理解模型技术，还要理解市场机制设计。

## Core Concepts

### Two-Sided Marketplace Architecture

双边市场平台的核心 ML 系统架构：

```
[需求侧]              [平台 ML 系统]            [供给侧]
  买家/乘客  <-->  匹配与定价引擎  <-->  卖家/司机
  搜索/浏览        ETA 预测              库存/可用性
  个性化推荐        欺诈检测              质量评分
```

### Dynamic Pricing (Surge)

**Dynamic Pricing（动态定价）**（或 **Surge Pricing，加价/潮汐定价**）实时平衡供需：

$$
\text{surge\_multiplier} = f\left(\frac{\text{demand\_rate}}{\text{supply\_rate}}\right)
$$

常用的对数线性定价模型：
$$
\log(\text{price}) = \beta_0 + \beta_1 \log\left(\frac{D}{S}\right) + \beta_2 \cdot \text{features}
$$

其中 $D/S$ 是供需比，$\beta_1$ 控制价格对供需失衡的敏感度。使用对数变换确保价格始终为正且变化率与倍数成正比。动态定价的目标是通过价格信号引导供给向需求热点区域转移，同时在需求过剩时抑制部分低价值需求。

### ETA Prediction

**ETA** 预测是用户体验和运营效率的关键指标，由多个组件模型组成：

$$
\text{ETA} = \text{routing\_time} + \text{pickup\_time} + \text{preparation\_time}
$$

每个组件使用独立的 ML 模型：
- **Routing（路径规划）**：图搜索最短路径 + 交通状况 ML 模型。使用历史 GPS 轨迹数据训练实时交通预测。
- **Preparation（准备时间）**：基于商家/门店历史完成时间的回归模型。需要考虑订单复杂度、当前积压量等因素。
- **Pickup（取件时间）**：骑手到商家的行程时间 + 等待时间。涉及地理编码和实时位置数据。

ETA 准确度直接影响用户转化率和信任度——高估导致用户流失，低估导致差评。

### Matching / Dispatch Optimization

**Dispatch Optimization（派单优化）** 是组合优化问题——将订单分配给骑手/司机：

$$
\min \sum_{i,j} c_{ij} x_{ij} \quad \text{s.t.} \quad \sum_j x_{ij} = 1 \; \forall i, \quad x_{ij} \in \{0,1\}
$$

其中 $c_{ij}$ 是将订单 $i$ 分配给骑手 $j$ 的成本（包括距离、ETA、公平性因子等）。

贪心分配的时间复杂度为 $O(n \cdot m)$，但全局最优需要使用 **Hungarian Algorithm（匈牙利算法）**，复杂度为 $O(n^3)$。工业实践中常采用 **Batch Matching（批量匹配）**：积累一个时间窗口内的请求，进行全局优化分配，比贪心方法提升 10-20% 的匹配效率。

### Key Metrics

| 指标 | 定义 | 目标 |
|------|------|------|
| 转化率 | 订单数 / 访问数 | 最大化 |
| ETA 准确度 | 预测与实际的 **MAE (Mean Absolute Error，平均绝对误差)** | 最小化 |
| 供给利用率 | 有效服务时间 / 在线时间 | 平衡（过高影响服务质量） |
| 缺陷率 | 取消 + 退货比率 | 最小化 |
| **Take Rate（抽成率）** | 平台收入 / **GMV (Gross Merchandise Volume，商品交易总额)** | 业务目标 |

### Geospatial Features

地理空间特征是市场平台 ML 的关键信号。常用的地理索引系统：

- **H3**：Uber 开源的六边形网格系统，支持多分辨率（res 0-15）。六边形相比矩形网格有更均匀的邻居距离。
- **S2**：Google 的球面几何库，将地球表面映射为层级化的单元格。
- **GeoHash**：将经纬度编码为字符串，前缀越长精度越高。

在每个网格单元内聚合供需信息，生成区域级特征用于定价和调度决策。

## Implementation

```python
import numpy as np

def surge_multiplier(
    demand_rate: float, supply_rate: float,
    min_surge: float = 1.0, max_surge: float = 3.0,
) -> float:
    # 计算动态定价乘数
    if supply_rate <= 0:
        return max_surge
    ratio = demand_rate / supply_rate
    surge = min_surge + (max_surge - min_surge) * max(0, ratio - 1)
    return min(max_surge, max(min_surge, surge))

def greedy_dispatch(
    order_locs: np.ndarray,
    driver_locs: np.ndarray,
) -> list[tuple[int, int]]:
    # 贪心最近司机派单
    assignments = []
    available = set(range(len(driver_locs)))
    for oi in range(len(order_locs)):
        best_d, best_dist = -1, float("inf")
        for di in available:
            dist = float(np.linalg.norm(order_locs[oi] - driver_locs[di]))
            if dist < best_dist:
                best_d, best_dist = di, dist
        if best_d >= 0:
            assignments.append((oi, best_d))
            available.discard(best_d)
    return assignments
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 批量匹配 | 打车、配送 | 积累时间窗口内的请求，全局优化分配 |
| 地理空间索引 | 基于位置的匹配 | H3/S2 六边形网格用于供需聚合 |
| 多目标定价 | 收入 vs 增长 | 约束优化：最大化收入同时满足最低转化率 |
| 因果推断 | 定价影响评估 | **Switchback Experiment（交替实验）**——基于时间的随机化 |
| 仿真 | 策略测试 | 在部署定价变更前进行基于智能体的仿真 |

### Common Interview Questions
- [ ] 设计一个外卖配送派单系统（DoorDash/Uber Eats）
- [ ] 如何为打车平台构建动态定价？
- [ ] 设计一个带实时更新的 ETA 预测系统
- [ ] 如何处理交易市场中的供需失衡？
- [ ] 设计 Airbnb 房源的搜索排序系统

## Comparisons

| 维度 | 贪心派单 | 批量优化 | 基于 RL 的方法 |
|------|---------|---------|-------------|
| 延迟 | <100ms | 1-5s 批次 | <100ms（推理） |
| 最优性 | 局部最优 | 近全局最优 | 学习到的策略 |
| 复杂度 | $O(n \cdot m)$ | $O(n^3)$ 匈牙利算法 | 训练成本 |
| 公平性 | 差 | 可配置 | 通过奖励函数塑造 |

## Key Takeaways
- [ ] 双边市场需要平衡买方/卖方/平台三方目标
- [ ] 动态定价需要因果评估（不仅是 A/B 测试——需要 Switchback 实验）
- [ ] ETA 准确度直接影响转化率和用户信任
- [ ] 批量匹配优于贪心派单，但增加了延迟
- [ ] 地理空间特征（H3 网格、出行时间）是关键信号
"""

# ============================================================
# NODE 93: NLP & LLM Systems
# ============================================================
NODES[93] = r"""# NLP & LLM Systems

## Overview

**NLP & LLM Systems（自然语言处理与大语言模型系统）** 设计涵盖围绕语言模型构建生产系统的各个方面：聊天机器人、内容生成、实体提取和 **RAG (Retrieval-Augmented Generation，检索增强生成)** 应用。该主题在面试中的重要性近年来急剧上升。资深 MLE 必须设计在质量、延迟、成本和安全性之间取得平衡的系统。

LLM 系统的核心挑战包括：**Hallucination（幻觉）** 控制、推理成本优化、输出质量评估，以及随着模型能力快速迭代保持系统可适配性。

## Core Concepts

### LLM Application Architecture

生产级 LLM 应用的标准架构包含多个保障层：

```
用户查询 -> [Guard Rails（防护栏）] -> [Router / Intent（路由/意图）]
    -> [Retrieval (RAG)] -> [Prompt Construction（提示构建）]
    -> [LLM Inference（LLM 推理）] -> [Output Validation（输出验证）]
    -> [Response Caching（响应缓存）] -> 用户响应
```

每一层都有明确的职责和延迟预算。Guard Rails 在输入端阻止有害内容和 **Prompt Injection（提示注入）** 攻击，Output Validation 在输出端检测幻觉、**PII (Personally Identifiable Information，个人身份信息)** 泄露和有害内容。

### RAG System Design

**RAG** 是知识密集型 LLM 应用的默认架构模式，通过检索外部知识来减少幻觉：

$$
P(\text{answer} | q) = \sum_{d \in \text{TopK}} P(\text{answer} | q, d) \cdot P(d | q)
$$

该公式表示最终答案的概率是各检索文档下条件概率的加权和，权重由文档与查询的相关性决定。

| 组件 | 选项 | 延迟预算 |
|------|------|---------|
| **Embedding（向量化）** | OpenAI, E5, BGE | 10-30ms |
| **Vector DB（向量数据库）** | Pinecone, Weaviate, pgvector | 10-50ms |
| **Re-ranker（重排序器）** | Cross-encoder, Cohere | 50-100ms |
| **LLM** | GPT-4, Claude, Llama | 500-5000ms |

RAG 系统的关键设计决策：
- **Chunking Strategy（分块策略）**：固定长度 vs 语义分段 vs 递归分割。块大小影响检索精度和上下文窗口利用率。
- **Embedding Model（向量化模型）**：通用 vs 领域微调。领域微调通常提升 10-20% 的检索质量。
- **Top-K Selection**：检索文档数量的权衡——更多文档增加召回但也增加噪声和成本。

### Prompt Engineering Patterns

**Prompt Engineering（提示工程）** 是 LLM 系统中成本最低、效果最直接的优化手段：

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| **Few-shot（少样本）** | 分类、实体提取 | 在提示中提供 3-5 个标注示例 |
| **Chain-of-thought（思维链）** | 推理任务 | "Let's think step by step..." |
| **Self-consistency（自一致性）** | 提高准确率 | 采样 N 个响应，多数投票 |
| **ReAct** | 工具调用代理 | Reason -> Act -> Observe 循环 |

### Cost Optimization

LLM 推理成本计算：

$$
\text{Cost per query} = \frac{\text{input\_tokens} \times p_{\text{in}} + \text{output\_tokens} \times p_{\text{out}}}{1000}
$$

关键优化策略：
- **Semantic Caching（语义缓存）**：使用 Embedding 相似度匹配相似查询，避免重复推理
- **Prompt Compression（提示压缩）**：去除冗余上下文，减少输入 Token 数
- **Model Routing（模型路由）**：简单查询用小模型，复杂查询用大模型——类似 **Cascade（级联）** 架构
- **Continuous Batching（连续批处理）**：动态组批提高 GPU 利用率

### Evaluation Framework

LLM 系统的评估是最大挑战——传统 ML 指标无法完全衡量生成质量：

| 评估维度 | 指标 | 方法 |
|---------|------|------|
| 相关性 | 回答正确性 | **LLM-as-Judge（LLM 做评判）**、人工评估 |
| 忠实度 | 基于上下文的事实性 | **NLI (Natural Language Inference，自然语言推理)** 模型或引用检查 |
| 延迟 | **TTFT (Time To First Token，首 Token 延迟)** | P50/P95 监控 |
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
| 流式传输 | 聊天应用 | **SSE (Server-Sent Events，服务器发送事件)** 逐 Token 传输，改善感知延迟 |
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
"""

# ============================================================
# NODE 94: Computer Vision Systems
# ============================================================
NODES[94] = r"""# Computer Vision Systems

## Overview

**Computer Vision Systems（计算机视觉系统）** 设计涵盖构建生产级的图像分类、目标检测、语义分割和视觉搜索管道。常见于自动驾驶公司、Meta、Google、Amazon（视觉搜索）等。资深 MLE 必须设计能够处理高吞吐量图像处理且满足严格延迟要求的系统。

视觉系统的独特挑战在于：输入数据维度极高（一张 1080p 图像约 600 万像素），模型计算密集度远超文本模型，且对实时性要求严格（自动驾驶需要 30fps 以上的推理速度）。

## Core Concepts

### CV Pipeline Architecture

生产级视觉系统的标准管道：

```
图像输入 -> [Pre-processing（预处理）] -> [Feature Extraction / Backbone（特征提取/骨干网络）]
    -> [Task Head（任务头）] -> [Post-processing（后处理）] -> [Serving（服务）]
```

预处理包括图像解码、缩放、归一化和数据增强。**Backbone（骨干网络）** 负责提取通用视觉特征，任务头针对具体任务（分类、检测等）进行预测。

### Model Architecture Choices

不同视觉任务对应的主流架构：

| 任务 | 架构 | 输出 |
|------|------|------|
| 分类 | ResNet, **EfficientNet**, **ViT (Vision Transformer，视觉变换器)** | 类别概率 |
| 检测 | **YOLO (You Only Look Once)**, DETR, Faster R-CNN | 边界框 + 类别 |
| 分割 | Mask R-CNN, **SAM (Segment Anything Model，通用分割模型)** | 像素级掩码 |
| 视觉搜索 | CNN/ViT 骨干网络 + Embedding | 特征向量用于 ANN |

### Object Detection Metrics

目标检测使用 **AP (Average Precision，平均精度)** 作为核心指标：

$$
\text{AP} = \int_0^1 p(r) \, dr
$$

其中 $p(r)$ 是在召回率 $r$ 处的精度。**mAP (mean Average Precision，平均精度均值)** 对所有类别的 AP 取平均。

**IoU (Intersection over Union，交并比)**：

$$
\text{IoU} = \frac{|B_{\text{pred}} \cap B_{\text{gt}}|}{|B_{\text{pred}} \cup B_{\text{gt}}|}
$$

当 $\text{IoU} \geq 0.5$ 时判定检测正确（AP@0.5），或在多个阈值上取平均（AP@[.5:.95]）。COCO 数据集标准使用 AP@[.5:.95] 作为主要评估指标。

### Non-Maximum Suppression (NMS)

**NMS (Non-Maximum Suppression，非极大值抑制)** 是目标检测后处理的关键步骤，用于去除重复检测框：

```
1. 按置信度分数降序排列所有检测框
2. 取最高分检测框加入输出
3. 移除与已选框 IoU > 阈值（通常 0.5）的所有检测框
4. 重复直到没有剩余检测框
```

NMS 的变体包括 **Soft-NMS（软非极大值抑制）**——不直接删除重叠框而是降低其分数，在密集场景下效果更好。

### Serving Considerations

生产环境中的模型服务优化：

| 关注点 | 解决方案 |
|--------|---------|
| 延迟 | **TensorRT**, **ONNX Runtime**, 量化 (INT8) |
| 吞吐量 | 批量推理, GPU 共享 (**MPS, Multi-Process Service**) |
| 图像尺寸 | 缩放/裁剪管道, 大图像分块处理 |
| 模型大小 | **Knowledge Distillation（知识蒸馏）**, 剪枝, **MobileNet** |

量化可将模型大小和推理延迟减少 2-4 倍，精度损失通常在 1% 以内。**TensorRT** 通过算子融合、内核自动调优等技术进一步加速推理。

### Data Augmentation

数据增强是视觉模型训练中提升泛化能力的关键技术：

| 增强方法 | 描述 | 常用场景 |
|---------|------|---------|
| 随机裁剪/翻转 | 基础几何变换 | 所有任务 |
| **Mixup** | 线性混合两张图像及其标签 | 分类 |
| **CutMix** | 将一张图的区域替换到另一张 | 分类 |
| **Mosaic** | 拼接 4 张图像 | 检测（YOLO） |
| 色彩抖动 | 随机调整亮度/对比度/饱和度 | 所有任务 |

## Implementation

```python
import numpy as np

def nms(
    boxes: np.ndarray,    # (N, 4) [x1, y1, x2, y2]
    scores: np.ndarray,   # (N,)
    iou_threshold: float = 0.5,
) -> list[int]:
    # 非极大值抑制
    order = scores.argsort()[::-1]
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(int(i))
        if len(order) == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_r = (boxes[rest, 2] - boxes[rest, 0]) * (boxes[rest, 3] - boxes[rest, 1])
        iou = inter / (area_i + area_r - inter + 1e-8)
        order = rest[iou <= iou_threshold]
    return keep
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 两阶段检测 | 高精度需求 | 区域提议 + 分类（Faster R-CNN） |
| 单阶段检测 | 实时推理 | YOLO/SSD 用速度换精度 |
| 视觉搜索管道 | 电商、相似图片 | 骨干网络 Embedding + ANN 索引 |
| 边缘部署 | 移动端/IoT | MobileNet + 量化 + TensorRT |
| **Active Learning（主动学习）** | 有限标注 | 不确定性采样优先标注最有价值的样本 |

### Common Interview Questions
- [ ] 设计基于图像的商品搜索系统（Google Lens）
- [ ] 如何构建自动驾驶的实时目标检测系统？
- [ ] 设计图像/视频内容审核系统
- [ ] 如何处理检测任务中的类别不平衡？
- [ ] 设计制造业的视觉质量检测系统

## Comparisons

| 维度 | CNN (ResNet) | ViT | YOLO v8 |
|------|-------------|-----|---------|
| 归纳偏置 | 平移等变性 | 全局注意力 | 无锚框检测 |
| 数据效率 | 好（小数据集） | 需要大量数据 | 预训练后好 |
| 推理速度 | 快 | 中等 | 非常快 |
| 最适用于 | 分类 | 大规模分类 | 实时检测 |

## Key Takeaways
- [ ] 根据延迟 vs 精度的权衡选择架构
- [ ] NMS 和后处理设计显著影响检测质量
- [ ] 模型优化（量化、蒸馏）对生产服务至关重要
- [ ] 视觉搜索 = 骨干网络 Embedding + ANN 索引（与文本搜索相同模式）
- [ ] 数据质量和标注策略通常比模型架构更重要
"""

# ============================================================
# NODE 95: Fraud & Trust Safety
# ============================================================
NODES[95] = r"""# Fraud & Trust Safety

## Overview

**Fraud & Trust Safety（欺诈检测与信任安全）** 系统保护平台免受各类滥用：支付欺诈、虚假账户、垃圾信息、诈骗和违规行为。这些系统面临极端的 **Class Imbalance（类别不平衡）**、对抗性攻击者和严格的延迟要求。常见于金融科技公司（Stripe、PayPal）、交易平台（Amazon、eBay）和社交平台（Meta、Twitter）。

欺诈检测的独特挑战在于：攻击者会主动适应和规避检测系统，形成持续的攻防博弈。此外，标签延迟（拒付可能在 30-90 天后才确认）和极低的欺诈率（通常 0.1-1%）使得模型训练和评估尤为困难。

## Core Concepts

### Fraud Detection Pipeline

欺诈检测的完整流水线是一个从实时决策到反馈闭环的系统：

```
事件（交易/操作）
    |
    v
[Real-time Rules Engine（实时规则引擎）] -- 硬性拦截（速率限制、黑名单）
    |
    v
[ML Risk Scoring（ML 风险评分）] -- 在 <50ms 内计算 P(fraud)
    |
    v
[Decision Engine（决策引擎）] -- 通过 / 人工审核 / 拦截
    |
    v
[Human Review Queue（人工审核队列）] -- 处理临界案例
    |
    v
[Feedback Loop（反馈闭环）] -- 标签回流用于模型重训练
```

规则引擎和 ML 模型的组合是工业标准：规则引擎处理已知模式（速度快、可解释），ML 模型处理新型攻击（自适应、泛化能力强）。

### Feature Engineering for Fraud

**特征工程** 是欺诈检测中最关键的环节，好的特征往往比模型选择更重要：

| 特征类型 | 示例 | 计算方式 |
|---------|------|---------|
| **Velocity（速率特征）** | 过去 1h/24h/7d 的交易次数 | 滑动窗口计数器 |
| **Graph（图特征）** | 设备共享、IP 聚类 | 连通分量分析 |
| **Behavioral（行为特征）** | 打字速度、浏览模式 | 会话分析 |
| **Historical（历史特征）** | 过往拒付记录、账户年龄 | 查找表 |
| **Network（网络特征）** | 共享支付方式、地址 | 图特征 |

图特征是最强大的欺诈信号——欺诈团伙通常共享设备指纹、IP 地址或支付方式。**Device Fingerprinting（设备指纹）** 通过收集浏览器特征、屏幕分辨率、字体列表等信息唯一标识设备。

### Class Imbalance Handling

欺诈率通常为 0.1-1%。直接使用标准分类方法会导致模型倾向于全部预测为非欺诈。处理策略：

$$
\mathcal{L}_{\text{weighted}} = -\sum [w_+ \cdot y \log \hat{y} + w_- \cdot (1-y) \log(1-\hat{y})]
$$

其中 $w_+$ 和 $w_-$ 分别是正类和负类的权重，通过增大正类权重来弥补数量劣势。

| 策略 | 适用场景 |
|------|---------|
| 类别权重 ($w_+ = 100$) | 始终是好的基线方法 |
| **SMOTE (Synthetic Minority Over-sampling Technique，合成少数类过采样)** / 过采样 | 表格数据、小数据集 |
| **Focal Loss（聚焦损失）**: $\alpha(1-p_t)^\gamma \text{CE}$ | 深度模型、困难样本挖掘。$\gamma$ 越大越聚焦于困难样本 |
| **Anomaly Detection（异常检测）** | 无监督方法，检测新型欺诈 |
| **Isolation Forest（隔离森林）** 集成 | 与监督模型互补 |

### Evaluation Metrics

标准准确率在极度不平衡时无意义（99.9% 准确率可能只是全部预测为非欺诈）。应使用：

$$
\text{Precision@k} = \frac{\text{top-k 预测中的真实欺诈数}}{k}
$$

关键指标：**PR-AUC (Precision-Recall AUC，精度-召回率曲线下面积)**、操作点处的 **F1 Score**、给定 **TPR (True Positive Rate，真正率)** 下的 **FPR (False Positive Rate，假正率)**、以及业务指标（挽回的损失金额 / 误拦截造成的损失）。

### Adversarial Considerations

欺诈者会持续适应检测系统，关键防御策略：
- **Feature velocity（特征速率监控）**：检测特征分布漂移，识别攻击模式变化
- **Model versioning（模型版本管理）**：A/B 测试新模型与当前模型
- **Ensemble diversity（集成多样性）**：多种模型类型（树模型、神经网络、图模型）抵抗同一攻击向量
- **Delayed labels（延迟标签）**：拒付延迟 30-90 天到达，需要半监督学习处理近期无标签数据

## Implementation

```python
import numpy as np
from collections import defaultdict

class VelocityCounter:
    # 滑动窗口事件计数器用于欺诈特征

    def __init__(self, window_seconds: int = 3600) -> None:
        self.window = window_seconds
        self.events: dict[str, list[float]] = defaultdict(list)

    def add_event(self, key: str, timestamp: float) -> None:
        self.events[key].append(timestamp)

    def count(self, key: str, current_time: float) -> int:
        cutoff = current_time - self.window
        times = self.events.get(key, [])
        valid = [t for t in times if t > cutoff]
        self.events[key] = valid
        return len(valid)

def fraud_risk_score(
    features: np.ndarray, model, rules_blocked: bool,
) -> tuple[float, str]:
    # 规则 + ML 混合风险评分
    if rules_blocked:
        return 1.0, "BLOCK"
    score = float(model.predict_proba(features.reshape(1, -1))[0, 1])
    if score > 0.9:
        return score, "BLOCK"
    if score > 0.5:
        return score, "REVIEW"
    return score, "APPROVE"
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 规则 + ML 混合 | 任何欺诈系统 | 规则捕获已知模式；ML 捕获新型模式 |
| 基于图的检测 | 账户网络 | 欺诈团伙共享设备/IP/支付方式 |
| 流式特征 | 实时决策 | Flink/Kafka 实现速率计数器 |
| **HITL (Human-in-the-Loop，人机协同)** | 高价值决策 | ML 做分流，人工决定临界案例 |
| 反馈延迟 | 标签延迟 | 用已确认标签训练，用半监督方法处理近期数据 |

### Common Interview Questions
- [ ] 设计实时支付欺诈检测系统
- [ ] 如何处理拒付的 30-90 天标签延迟？
- [ ] 设计社交平台的虚假账户检测系统
- [ ] 标签噪声下如何评估欺诈模型？
- [ ] 如何检测协调虚假行为（欺诈团伙）？

## Comparisons

| 维度 | 规则引擎 | 监督 ML | **GNN (Graph Neural Network，图神经网络)** |
|------|---------|---------|-----|
| 延迟 | <1ms | 5-20ms | 50-200ms |
| 适应性 | 手动更新 | 重训练 | 重训练 |
| 新型欺诈 | 差 | 中等 | 好（结构性特征） |
| 可解释性 | 高 | 中等（SHAP） | 低 |
| 冷启动 | 立即可用 | 需要标签 | 需要图结构 |

## Key Takeaways
- [ ] 始终组合规则（快速、可解释）和 ML（自适应、泛化能力强）
- [ ] 类别不平衡要求谨慎选择评估指标（用 PR-AUC，不是准确率）
- [ ] 图特征（设备/IP/支付方式共享）是最强大的欺诈信号
- [ ] 为对抗性适应设计系统——欺诈者会持续探测和演化
- [ ] 反馈闭环和标签质量是最大的长期挑战
"""

# ============================================================
# NODE 96: ML Infrastructure Design
# ============================================================
NODES[96] = r"""# ML Infrastructure Design

## Overview

**ML Infrastructure Design（ML 基础设施设计）** 涵盖支撑 ML 全生命周期的系统：训练管道、模型服务、**Feature Store（特征存储）**、实验追踪和监控。该主题考察设计可靠、可扩展平台的能力，使团队能够快速迭代。这是所有大型科技公司甚至越来越多初创公司的面试考点。

ML 基础设施的核心理念是：好的平台应该让 ML 工程师专注于模型和特征的创新，而不是被部署、监控和数据管道等操作性工作所困扰。迭代速度（从想法到线上实验的时间）是衡量 ML 平台质量的最重要指标。

## Core Concepts

### ML Platform Architecture

ML 平台由三层组成，覆盖数据到服务的完整链路：

```
[Data Layer（数据层）]         [Training Layer（训练层）]      [Serving Layer（服务层）]
 Feature Store                Training Pipeline               Model Server
 Data Warehouse               Experiment Tracker              A/B Testing
 Streaming (Kafka)            Model Registry                  Feature Serving
 Label Management             Hyperparameter Tuning           Monitoring/Alerts
```

### Training Pipeline Design

训练管道的各组件及其职责：

| 组件 | 工具示例 | 用途 |
|------|---------|------|
| **Orchestration（编排）** | Airflow, Kubeflow, Metaflow | **DAG (Directed Acyclic Graph，有向无环图)** 调度、重试机制 |
| **Data Processing（数据处理）** | Spark, Ray, Dask | 分布式特征计算 |
| **Training（训练）** | PyTorch + **DDP (Distributed Data Parallel，分布式数据并行)** / **FSDP (Fully Sharded Data Parallel，全分片数据并行)**, DeepSpeed | 分布式训练 |
| **Experiment Tracking（实验追踪）** | MLflow, W&B, Neptune | 指标记录、产物管理、可复现性 |
| **Model Registry（模型注册表）** | MLflow, Vertex AI | 版本控制、升级门控 |

分布式训练的关键模式：
- **DDP**：每个 GPU 持有完整模型副本，梯度全局同步。适用于模型可以放入单个 GPU 的场景。
- **FSDP**：模型参数在 GPU 间分片，按需全收集。支持训练超大模型（数十亿参数）。
- **Pipeline Parallelism（管道并行）**：模型按层分割到不同 GPU，形成流水线。减少气泡（空闲时间）是关键挑战。

### Model Serving Patterns

模型服务的四种主要模式，各有适用场景：

| 模式 | 延迟 | 吞吐量 | 适用场景 |
|------|------|--------|---------|
| **Online (sync，在线同步)** | <50ms | 中等 | 实时预测 |
| **Batch（批处理）** | 小时级 | 非常高 | 每日推荐预计算 |
| **Streaming（流式）** | ~秒级 | 高 | 近实时评分 |
| **Edge（边缘）** | <10ms | 单设备 | 移动端、IoT |

### Feature Store Architecture

特征新鲜度直接影响模型质量：

$$
\text{Feature freshness} = t_{\text{serving}} - t_{\text{event}}
$$

| 模式 | 新鲜度 | 存储 | 示例 |
|------|--------|------|------|
| Batch | 小时-天 | 数据仓库 | 用户历史聚合 |
| Streaming | 秒-分钟 | Redis/DynamoDB | 最近点击 |
| On-demand | 实时 | 请求时计算 | 当前位置 |

### Model Monitoring

模型上线后的持续监控是防止静默性能退化的关键：

| 监控内容 | 指标 | 告警阈值 |
|---------|------|---------|
| 预测分布漂移 | **KL Divergence（KL 散度）**, **PSI (Population Stability Index，群体稳定性指数)** | PSI > 0.2 |
| 特征分布漂移 | **KS Test (Kolmogorov-Smirnov Test，KS 检验)** | p < 0.01 |
| 延迟 | P50, P95, P99 | P95 > SLA |
| 错误率 | 5xx / 总请求 | > 0.1% |
| 业务指标 | CTR, 转化率 | > 2 sigma 下降 |

**PSI** 用于检测预测分布是否显著偏离训练时的分布：

$$
\text{PSI} = \sum_{i=1}^{n} (p_i - q_i) \ln\left(\frac{p_i}{q_i}\right)
$$

其中 $p_i$ 是当前分布在第 $i$ 个桶中的比例，$q_i$ 是参考分布的比例。PSI < 0.1 表示稳定，0.1-0.2 需要关注，> 0.2 需要立即调查。

### Safe Model Deployment

安全的模型部署策略：

- **Shadow Deployment（影子部署）**：新模型与旧模型同时运行，比较输出但不影响线上结果。用于验证新模型的预测一致性。
- **Canary Release（金丝雀发布）**：逐步扩大流量 1% -> 5% -> 25% -> 100%，每步验证关键指标。
- **Circuit Breaker（熔断器）**：当主模型异常时自动回退到简单模型（如基于规则的备用模型）。

## Implementation

```python
from dataclasses import dataclass, field

@dataclass
class ModelVersion:
    name: str
    version: int
    artifact_path: str
    metrics: dict[str, float] = field(default_factory=dict)
    stage: str = "staging"

class SimpleModelRegistry:
    def __init__(self) -> None:
        self.models: dict[str, list[ModelVersion]] = {}

    def register(self, model: ModelVersion) -> None:
        if model.name not in self.models:
            self.models[model.name] = []
        self.models[model.name].append(model)

    def promote(self, name: str, version: int) -> None:
        for mv in self.models.get(name, []):
            if mv.stage == "production":
                mv.stage = "archived"
            if mv.version == version:
                mv.stage = "production"

    def get_production(self, name: str) -> ModelVersion | None:
        for mv in reversed(self.models.get(name, [])):
            if mv.stage == "production":
                return mv
        return None
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| Feature Store | 任何生产 ML 系统 | 解耦特征工程与模型训练/服务 |
| Shadow Deployment | 安全上线 | 新模型与旧模型并行运行，比较输出 |
| Canary Release | 渐进上线 | 路由 1% -> 5% -> 25% -> 100% 流量 |
| Circuit Breaker | 容错 | 主模型异常时回退到简单模型 |
| **Training-Serving Skew（训练-服务偏差）** | 调试精度下降 | 相同的特征代码必须在训练和服务路径中运行 |

### Common Interview Questions
- [ ] 为大规模推荐系统设计 Feature Store
- [ ] 如何设置模型监控和告警？
- [ ] 设计处理 100K QPS 的模型服务系统
- [ ] 如何防止训练-服务偏差？
- [ ] 设计 ML 模型 A/B 测试的实验平台

## Comparisons

| 维度 | 批处理服务 | 在线服务 | 流式服务 |
|------|----------|---------|---------|
| 延迟 | 小时级 | <50ms | 秒级 |
| 计算资源 | 离线集群 | GPU 集群 | 流处理器 |
| 新鲜度 | 陈旧 | 实时 | 近实时 |
| 成本 | 低（可用竞价实例） | 高（常驻服务） | 中等 |
| 复杂度 | 简单 | 高（SLA、回退策略） | 中等 |

## Key Takeaways
- [ ] Feature Store 解决训练-服务偏差问题——ML 中最常见的静默错误
- [ ] 模型监控（漂移检测）与模型训练同等重要
- [ ] 影子/金丝雀部署是安全模型上线的必备手段
- [ ] 为故障设计：熔断器、回退模型、优雅降级
- [ ] ML 平台应优化迭代速度，而不仅是模型性能
"""

# ============================================================
# NODE 97: Generative AI Systems
# ============================================================
NODES[97] = r"""# Generative AI Systems

## Overview

**Generative AI Systems（生成式 AI 系统）** 设计涵盖围绕图像生成、文生图、代码生成和多模态系统构建生产应用。这是 ML 系统设计面试中最新的类别。核心关注领域包括提示管理、安全对齐、成本控制和质量评估。

生成式 AI 系统的独特挑战在于：输出的开放性使得质量评估极其困难，安全风险（有害内容生成、版权侵权）需要多层防护，且推理成本远高于传统 ML 模型。

## Core Concepts

### GenAI Application Architecture

生成式 AI 应用的标准架构包含安全过滤和质量控制的多个层次：

```
用户输入 -> [Safety Filter（安全过滤）] -> [Prompt Template（提示模板）]
    -> [Model Selection（模型选择）] -> [Generation（生成）]
    -> [Quality Filter（质量过滤）] -> [Output Post-processing（输出后处理）]
    -> [Caching Layer（缓存层）] -> 用户输出
```

### Model Selection Strategy

模型选择需要在多个维度之间权衡：

| 因素 | 考量 |
|------|------|
| 质量 | 更大的模型产生更好的输出 |
| 延迟 | 更小的模型更快；量化有助于加速 |
| 成本 | Token 价格在不同模型大小间相差 100 倍 |
| 可控性 | 微调模型更好地遵循指令 |
| 安全性 | **RLHF (Reinforcement Learning from Human Feedback，基于人类反馈的强化学习)** 对齐的模型更安全，但可能过度拒绝合理请求 |

### Diffusion Models (Image Generation)

**Diffusion Models（扩散模型）** 是当前图像生成的主流架构（Stable Diffusion, DALL-E, Midjourney）。

前向过程逐步加噪：
$$
q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t I)
$$

其中 $\beta_t$ 是第 $t$ 步的噪声调度参数，控制每步添加的噪声量。经过 $T$ 步后（通常 $T = 1000$），原始图像被完全转化为高斯噪声。

反向过程学习去噪：
$$
p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \sigma_t^2 I)
$$

训练目标（简化）——预测添加的噪声：
$$
\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]
$$

其中 $\epsilon$ 是实际添加的噪声，$\epsilon_\theta(x_t, t)$ 是模型预测的噪声。模型在训练时学习在任意噪声水平下还原图像。

关键优化技术：
- **Latent Diffusion（潜空间扩散）**：在低维潜空间而非像素空间进行扩散，大幅减少计算量（Stable Diffusion 的核心思想）
- **Classifier-Free Guidance（无分类器引导）**：通过调节引导强度 $w$ 控制生成与文本条件的一致程度
- **DDIM (Denoising Diffusion Implicit Models)** 采样：减少推理步数（1000步 -> 20-50步），加速生成

### Serving Optimization

推理优化技术及其效果：

| 技术 | 加速比 | 质量影响 |
|------|--------|---------|
| **KV Cache（键值缓存）** | 2-3x | 无 |
| **Speculative Decoding（推测解码）** | 2-3x | 无。用小模型草拟多个 Token，大模型验证 |
| **Quantization（量化）** (INT8/INT4) | 2-4x | 轻微。INT8 几乎无损，INT4 需要校准 |
| **Distillation（蒸馏）** | 5-10x | 中等 |
| **Prompt Caching（提示缓存）** | 可变 | 无 |
| **Continuous Batching（连续批处理）** | 2-8x 吞吐量 | 无。动态插入新请求而非等待整批完成 |

### Safety & Alignment

安全与对齐的多层防护体系：

| 层级 | 方法 | 目的 |
|------|------|------|
| 输入过滤 | 分类器 | 阻止有害提示 |
| 系统提示 | 指令 | 引导模型行为 |
| **RLHF / DPO (Direct Preference Optimization，直接偏好优化)** | 训练阶段 | 与人类偏好对齐 |
| 输出过滤 | 分类器 + 规则 | 捕获有害输出 |
| **Watermarking（水印）** | 频谱嵌入 | 检测 AI 生成内容 |

**DPO** 是 RLHF 的简化替代方案，直接从偏好数据优化策略而无需训练奖励模型，显著简化了对齐训练流程。

## Implementation

```python
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9

def model_router(
    query: str, complexity_score: float,
    configs: dict[str, GenerationConfig],
) -> GenerationConfig:
    # 根据查询复杂度路由到适当的模型
    if complexity_score < 0.3:
        return configs["small"]
    if complexity_score < 0.7:
        return configs["medium"]
    return configs["large"]

def semantic_cache_key(
    query: str, embedder,
    cache: dict[str, str], threshold: float = 0.95,
) -> str | None:
    # 语义缓存：检查是否有相似的历史查询
    q_emb = embedder.encode(query)
    for cached_query, cached_response in cache.items():
        c_emb = embedder.encode(cached_query)
        sim = float(q_emb @ c_emb / (
            (q_emb @ q_emb) ** 0.5 * (c_emb @ c_emb) ** 0.5 + 1e-8
        ))
        if sim > threshold:
            return cached_response
    return None
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 模型级联 | 成本优化 | 先用小模型，仅在需要时升级到大模型 |
| 语义缓存 | 重复查询 | 用 Embedding 相似度匹配缓存 |
| 人类反馈闭环 | 质量改进 | 收集点赞/点踩 -> 微调数据 |
| 水印 | 内容来源追踪 | 在生成内容中嵌入可检测的信号 |
| 防护栏管道 | 安全保障 | 多层输入/输出过滤 |

### Common Interview Questions
- [ ] 设计文生图生成平台（DALL-E/Midjourney）
- [ ] 如何构建代码生成助手？
- [ ] 设计带质量和安全控制的内容生成系统
- [ ] 如何为大规模 LLM 应用优化成本？
- [ ] 设计带实时协作功能的 AI 写作助手

## Comparisons

| 维度 | API（GPT-4） | 自托管（Llama） | 微调 |
|------|-------------|---------------|------|
| 初始成本 | 零 | GPU 基础设施 | 训练 + 基础设施 |
| 每查询成本 | 高 | 低（摊销） | 低 |
| 定制化 | 仅限提示 | 完全控制 | 深度控制 |
| 延迟 | 可变（共享资源） | 可预测 | 可预测 |
| 数据隐私 | 数据离开组织 | 本地部署 | 本地部署 |

## Key Takeaways
- [ ] 模型路由和缓存是成本削减的两大杠杆
- [ ] 多层安全防护（输入过滤 + 系统提示 + 输出过滤）是必须的
- [ ] 评估是最大挑战——投资于自动化 + 人工评估
- [ ] 延迟优化：KV 缓存、连续批处理、推测解码
- [ ] 设计支持模型可替换——最佳模型每几个月更新一次
"""

# ============================================================
# NODE 98: Two-Tower Model
# ============================================================
NODES[98] = r"""# Two-Tower Model

## Overview

**Two-Tower Model（双塔模型）**（也称为 **Dual Encoder，双编码器**）是大规模检索系统的核心架构。它将查询和物品独立编码到共享的 **Embedding Space（嵌入空间）** 中，通过 **ANN (Approximate Nearest Neighbor，近似最近邻)** 实现亚线性检索。该架构广泛应用于 Google、Meta、YouTube、LinkedIn 的搜索和推荐候选生成阶段。

双塔模型的核心价值在于：将检索问题转化为向量空间中的最近邻搜索，使得物品编码可以离线预计算、ANN 索引可以高效查询，从而在数十亿物品库上实现毫秒级候选生成。

## Core Concepts

### Architecture

双塔架构的核心是两个独立的编码器，将不同输入映射到同一向量空间：

```
[User Features（用户特征）]    [Item Features（物品特征）]
      |                              |
  [User Tower（用户塔）]        [Item Tower（物品塔）]
  (MLP/Transformer)              (MLP/Transformer)
      |                              |
  user_emb (d维)                item_emb (d维)
      \                            /
       \                          /
        cosine_similarity(u, v)
              |
         相关性分数
```

双塔模型的核心评分公式：

$$
score(u, i) = f(u)^T g(i)
$$

其中 $f(u)$ 是用户塔的输出向量，$g(i)$ 是物品塔的输出向量。由于两个塔独立计算，物品向量可以离线预计算并存入 ANN 索引，在线仅需计算用户向量并进行 ANN 查询。

### Training Objective

使用 **In-batch Negatives（批内负采样）** 的 **Contrastive Loss（对比损失）**：

$$
\mathcal{L} = -\frac{1}{B} \sum_{i=1}^{B} \log \frac{\exp(\text{sim}(u_i, v_i) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(u_i, v_j) / \tau)}
$$

其中 $\tau$ 是 **Temperature（温度）** 参数，$B$ 是批大小。这个损失函数本质上是在做 $B$ 类分类——对于每个用户 $u_i$，正确的物品 $v_i$ 应该与之最相似，而批内其他物品 $v_j$（$j \neq i$）作为负样本。

温度 $\tau$ 的作用：$\tau$ 越低，相似度分布越尖锐，模型越倾向于学习更难区分的样本对。通常 $\tau \in [0.05, 0.1]$。

### Key Design Decisions

| 设计决策 | 选项 | 权衡 |
|---------|------|------|
| 相似度函数 | Cosine（余弦）, Dot Product（点积） | Cosine 归一化了幅值；点积允许流行度信号 |
| 负采样策略 | 批内负采样, **Hard Negatives（困难负样本）** | 困难负样本提升质量但需要精心挖掘 |
| 温度 $\tau$ | 0.05 - 0.1 | 越低 = 分布越尖锐 = 训练越困难 |
| Embedding 维度 | 64 - 256 | 越高 = 表达能力越强但 ANN 越慢 |
| 共享层 | 无 / 部分共享 / 完全共享 | 共享底层减少参数但限制了不对称性 |

### Hard Negative Mining

**Hard Negative Mining（困难负样本挖掘）** 是提升双塔模型质量的关键技术：

- **随机负采样**：从全部物品中随机采样。简单但负样本通常太容易区分。
- **批内负采样**：使用同一批次中其他正样本的物品作为负样本。免费获得负样本，但可能偏向热门物品。
- **半困难负样本**：从当前模型的 Top-K 检索结果中挖掘（排除正样本）。提供信息量最大的训练信号。
- **交叉批次负采样**：将多个 GPU/机器的嵌入广播，扩大有效批大小和负样本数量。

### Serving Pattern

双塔模型的服务模式是其最大的架构优势：

1. **离线阶段**：预计算所有物品的 Embedding 向量，构建 ANN 索引（HNSW, ScaNN）
2. **在线阶段**：根据用户实时特征计算用户 Embedding，查询 ANN 索引
3. **延迟分解**：用户塔推理 ~5ms + ANN 查询 ~10ms = 总计 ~15ms

### Limitations

- 无法建模细粒度的查询-物品交互（没有 **Cross-Attention，交叉注意力**）
- 用户和物品的表示相互独立——丢失了特征交叉信息
- 相比 **Cross-Encoder（交叉编码器）** 存在质量上限（但在规模上快 1000 倍）

## Implementation

```python
import numpy as np

class TwoTower:
    def __init__(self, user_dim: int, item_dim: int, emb_dim: int) -> None:
        self.w_user = np.random.randn(user_dim, emb_dim) * 0.01
        self.w_item = np.random.randn(item_dim, emb_dim) * 0.01

    def encode_user(self, feat: np.ndarray) -> np.ndarray:
        e = feat @ self.w_user
        return e / (np.linalg.norm(e, axis=-1, keepdims=True) + 1e-8)

    def encode_item(self, feat: np.ndarray) -> np.ndarray:
        e = feat @ self.w_item
        return e / (np.linalg.norm(e, axis=-1, keepdims=True) + 1e-8)

    def contrastive_loss(
        self, u: np.ndarray, v: np.ndarray, tau: float = 0.07,
    ) -> float:
        # 批内对比损失
        sims = (u @ v.T) / tau
        labels = np.arange(len(u))
        log_softmax = sims - np.log(np.exp(sims).sum(axis=1, keepdims=True))
        return float(-log_softmax[labels, labels].mean())
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 批内负采样 | 大批量训练 | 从批内其他样本免费获取负样本 |
| 困难负样本挖掘 | 提升精度 | 从 ANN 近邻或上一版模型的错误中挖掘 |
| 多任务塔 | 多检索任务 | 共享骨干网络 + 任务特定头部 |
| 定期重建索引 | 物品库变化 | 每天/每小时重建 ANN 索引 |
| 特征刷新 | 实时个性化 | 使用流式特征更新用户 Embedding |

### Common Interview Questions
- [ ] 双塔模型与 Cross-Encoder 在检索中有何不同？
- [ ] 为什么使用批内负采样而非显式负采样？
- [ ] 如何处理没有交互历史的冷启动物品？
- [ ] 如何决定 Embedding 维度和 ANN 算法？
- [ ] 如何向用户塔添加实时特征？

## Comparisons

| 维度 | 双塔模型 | Cross-Encoder | 矩阵分解 |
|------|---------|--------------|---------|
| 推理 | $O(1)$ 每对 + ANN | $O(n)$ 每查询 | 预计算 |
| 表达能力 | 中等 | 高 | 低 |
| 特征支持 | 丰富特征 | 丰富特征 | 仅 ID（基础） |
| 规模 | 数十亿物品 | 仅 Top-K | 百万级 |

## Key Takeaways
- [ ] 双塔模型通过预计算 Embedding + ANN 实现十亿级检索
- [ ] 批内负采样简单有效但可能偏向热门物品
- [ ] 温度参数和困难负样本挖掘是最关键的调优超参数
- [ ] 服务模式（离线物品索引 + 在线用户编码）是通用的
- [ ] 存在质量上限——始终配合重排序阶段使用
"""

# ============================================================
# NODE 99: Multi-Stage Ranking
# ============================================================
NODES[99] = r"""# Multi-Stage Ranking

## Overview

**Multi-Stage Ranking（多阶段排序）** 是大规模 ML 预测服务的标准架构。每个阶段在缩小候选集的同时增加模型复杂度。该模式出现在每个主要科技公司的搜索、推荐、广告和信息流排序中。

多阶段排序的核心理念是"漏斗"——从海量候选中逐步筛选，每一步使用更复杂但也更耗时的模型。这种架构是必然选择：用最强大的模型评估数十亿候选项在计算上不可行。

## Core Concepts

### The Ranking Funnel

排序漏斗的各阶段及其典型配置：

$$
\text{Full Catalog} \xrightarrow{L0} \text{10K} \xrightarrow{L1} \text{1K} \xrightarrow{L2} \text{100} \xrightarrow{L3} \text{10-50}
$$

| 阶段 | 名称 | 模型 | 延迟 | 候选数 |
|------|------|------|------|--------|
| L0 | **Pre-filtering（预过滤）** | 规则、倒排索引 | <1ms | 10K |
| L1 | **Candidate Gen（候选生成）** | 双塔模型、ANN | 10-20ms | 1K |
| L2 | **Ranking（精排）** | 深度模型（DCN, DIN） | 20-50ms | 100 |
| L3 | **Re-ranking（重排序）** | 业务规则、多样性 | <10ms | 10-50 |

### Stage Design Principles

**L1 -- Candidate Generation（候选生成）**：优化 **Recall（召回率）**。在这一阶段遗漏的好物品将永远无法呈现给用户。使用多个检索来源来最大化召回：
- 协同过滤候选
- 基于内容的候选（Embedding 相似度）
- 热门/趋势物品
- 基于用户历史的个性化候选

**L2 -- Ranking（精排）**：优化 **Precision/NDCG**。特征丰富的模型对每个候选独立评分：

$$
\text{score}(u, i) = f_\theta(\text{user\_features}, \text{item\_features}, \text{cross\_features})
$$

精排模型通常使用数百个特征，包括用户画像、物品属性、上下文信息和交叉特征。模型架构选择（Wide & Deep、DCN-v2、DIN 等）取决于特征交互的复杂度和延迟预算。

**L3 -- Re-ranking（重排序）**：应用业务约束，这些约束纯粹的 ML 模型无法处理：
- **Diversity（多样性）**：使用 **MMR (Maximal Marginal Relevance，最大边际相关)** 或 **DPP (Determinantal Point Process，行列式点过程)**
- **Freshness Boost（新鲜度加权）**：提高新内容的曝光
- 广告插入位
- 作者/来源多样性

### Maximal Marginal Relevance (MMR)

**MMR** 在相关性和多样性之间取得平衡：

$$
\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[\lambda \cdot \text{Rel}(d_i) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j)\right]
$$

第一项 $\lambda \cdot \text{Rel}(d_i)$ 鼓励选择相关性高的文档，第二项 $(1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j)$ 惩罚与已选文档过于相似的候选。$\lambda$ 越大越倾向相关性，越小越倾向多样性。

### Latency Budget Management

总延迟预算（如 200ms）在各阶段间分配：

$$
t_{\text{total}} = t_{L0} + t_{L1} + t_{L2} + t_{L3} + t_{\text{network}} + t_{\text{feature\_fetch}}
$$

特征获取（从 Feature Store 读取）通常是延迟的最大来源，需要通过预加载热门特征、惰性加载冷门特征来优化。

### Score Calibration Across Sources

当 L1 阶段使用多个检索来源时，不同来源的分数不可直接比较。常用校准方法：
- **分数归一化**：将每个来源的分数映射到 [0, 1] 区间
- **学习融合权重**：用一个轻量模型学习各来源的最优权重
- **统一排序**：将所有候选送入同一个 L2 排序模型

## Implementation

```python
import numpy as np

def multi_stage_rank(
    user_features: np.ndarray,
    candidate_gen,
    ranker,
    item_features: dict,
    diversity_lambda: float = 0.3,
    top_k: int = 20,
) -> list[int]:
    # 多阶段排序管道
    # L1: 候选生成（召回优化）
    candidates = candidate_gen.retrieve(user_features, k=500)
    # L2: 精排（精度优化）
    scores = []
    for cid in candidates:
        feat = item_features.get(cid)
        if feat is not None:
            s = ranker.score(user_features, feat)
            scores.append((cid, s))
    scores.sort(key=lambda x: -x[1])
    ranked = scores[:100]
    # L3: MMR 重排序实现多样性
    selected: list[int] = []
    remaining = list(ranked)
    while len(selected) < top_k and remaining:
        best_idx, best_score = 0, -float("inf")
        for idx, (cid, rel) in enumerate(remaining):
            div_penalty = 0.0
            for sid in selected:
                sim = float(np.dot(item_features[cid], item_features[sid]))
                div_penalty = max(div_penalty, sim)
            mmr = (1 - diversity_lambda) * rel - diversity_lambda * div_penalty
            if mmr > best_score:
                best_idx, best_score = idx, mmr
        selected.append(remaining[best_idx][0])
        remaining.pop(best_idx)
    return selected
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 多源检索 | 扩大召回 | 合并来自 CF、内容、热门的候选 |
| 分数校准 | 跨来源排序 | 归一化不同 L1 来源的分数 |
| 特征缓存 | 延迟优化 | 预加载热门特征，惰性加载冷门特征 |
| 级联模型 | 渐进过滤 | 每个阶段使用前一阶段特征的超集 |
| 在线-离线一致性 | 调试 | 在预测时记录特征用于离线回放 |

### Common Interview Questions
- [ ] 为什么不用一个强大的模型替代多个阶段？
- [ ] 如何决定每个阶段的候选数量？
- [ ] 如何确保最终结果的多样性？
- [ ] 好的物品没有出现在结果中时如何调试？
- [ ] 如何管理各阶段的延迟预算？

## Comparisons

| 维度 | 单阶段 | 多阶段 | 端到端 (RL) |
|------|--------|--------|------------|
| 延迟 | 无法扫描所有物品 | 每阶段可控 | 分摊 |
| 质量 | 单物品最优 | 近最优 | 优化列表级指标 |
| 可调试性 | 简单 | 逐阶段分析 | 黑盒 |
| 工程复杂度 | 简单 | 中等 | 复杂 |

## Key Takeaways
- [ ] 多阶段排序在规模化时不是可选而是必须——无法用重模型评估数十亿物品
- [ ] L1 的召回率是整个系统的上限——在此投入重兵
- [ ] 重排序（L3）处理纯 ML 模型无法处理的业务需求
- [ ] 特征获取延迟通常占主导——用缓存和预计算优化
- [ ] 在每个阶段记录预测和特征，用于调试和离线分析
"""

# ============================================================
# NODE 100: Approximate Nearest Neighbor
# ============================================================
NODES[100] = r"""# Approximate Nearest Neighbor (ANN)

## Overview

**ANN (Approximate Nearest Neighbor，近似最近邻)** 算法实现了对大规模向量集合的亚线性相似性搜索。它们是搜索、推荐和 **RAG (Retrieval-Augmented Generation，检索增强生成)** 系统中基于 Embedding 检索的基础骨架。理解 ANN 在召回率、延迟和内存之间的权衡对任何检索系统设计至关重要。

## Core Concepts

### Why Approximate?

精确最近邻搜索的时间复杂度为 $O(n \cdot d)$，其中 $n$ 是向量数量，$d$ 是向量维度。对于 $n = 10^9$（十亿）和 $d = 256$，每次查询需要数秒。ANN 以微小的精度损失换取 100-1000 倍的加速。

### Algorithm Families

ANN 算法可以分为五大类，各有适用场景：

| 家族 | 算法 | 核心思想 |
|------|------|---------|
| **Tree-based（基于树）** | Annoy | 随机投影树，搜索多棵树取并集 |
| **Hash-based（基于哈希）** | **LSH (Locality-Sensitive Hashing，局部敏感哈希)** | 将相似向量哈希到同一桶中 |
| **Graph-based（基于图）** | **HNSW (Hierarchical Navigable Small World，层级可导航小世界图)** | 构建多层可导航图，贪心搜索 |
| **Quantization（基于量化）** | **IVF-PQ (Inverted File Index + Product Quantization，倒排文件索引 + 乘积量化)** | 聚类 + 乘积量化实现压缩 |
| **Learned（学习型）** | ScaNN | 基于各向异性损失的学习量化 |

### LSH (Locality-Sensitive Hashing)

**LSH** 的核心思想是：设计特殊的哈希函数，使得相似的向量以更高概率被映射到相同的哈希桶。对于余弦相似度，常用随机超平面哈希：

$$
h(v) = \text{sign}(r^T v)
$$

其中 $r$ 是随机向量。使用 $k$ 个哈希函数组合并重复 $L$ 轮，可以控制召回率和误报率之间的权衡。LSH 的理论保证使其在某些场景下仍有独特价值，但实践中通常被 HNSW 超越。

### HNSW (Hierarchical Navigable Small World)

**HNSW** 是目前最广泛使用的 ANN 算法，构建多层导航图：

- 第 0 层：所有向量，密集连接
- 第 $l$ 层：向量子集，约 $n \cdot e^{-l}$ 个节点
- 搜索过程：从最高层开始，贪心下降到最底层

关键参数：
- **M**：每个节点的最大连接数（控制图密度）。M 越大图越稠密，召回越高但内存和构建时间增加。
- **ef_construction**：构建时的搜索宽度（质量 vs 构建时间）
- **ef_search**：查询时的搜索宽度（召回率 vs 延迟）。这是最常调整的参数。

HNSW 的优势在于：查询延迟极低（~1ms@1M 向量），召回率高（>0.98），支持增量插入。

### IVF-PQ (Inverted File + Product Quantization)

**IVF-PQ** 是十亿级向量检索的核心方案，通过两个层次的压缩减少搜索空间和内存占用：

1. **IVF（倒排文件索引）**：使用 k-means 将向量聚类到 $k$ 个单元中。查询时仅搜索最近的 $n_{\text{probe}}$ 个单元。
2. **PQ（乘积量化）**：将 $d$ 维向量分成 $m$ 个子向量，每个子向量量化为 $b$ 位：

$$
\text{Memory per vector} = m \times b \text{ bits}
$$

例如 $d=256$, $m=32$, $b=8$ 时：每向量仅需 32 字节（而非 float32 的 1024 字节），压缩 32 倍。

近似距离通过查表计算：
$$
\hat{d}(x, y) = \sum_{j=1}^{m} d(x_j, c_{q(y_j)})
$$

其中 $c_{q(y_j)}$ 是第 $j$ 个子空间中 $y$ 对应的量化中心。

### Recall-Latency Tradeoff

ANN 系统的核心评估指标是召回-延迟权衡：

$$
\text{Recall@k} = \frac{|\text{ANN top-k} \cap \text{exact top-k}|}{k}
$$

典型目标：Recall@10 > 0.95 且延迟 < 10ms。调节 ef_search（HNSW）或 n_probe（IVF）可以在召回率和延迟之间平滑权衡。

## Implementation

```python
import numpy as np

class SimpleIVF:
    # 简化的 IVF 索引实现

    def __init__(self, n_clusters: int = 100) -> None:
        self.n_clusters = n_clusters
        self.centroids: np.ndarray | None = None
        self.buckets: dict[int, list[tuple[int, np.ndarray]]] = {}

    def build(self, vectors: np.ndarray) -> None:
        idx = np.random.choice(len(vectors), self.n_clusters, replace=False)
        self.centroids = vectors[idx].copy()
        for i, v in enumerate(vectors):
            dists = np.linalg.norm(self.centroids - v, axis=1)
            c = int(np.argmin(dists))
            self.buckets.setdefault(c, []).append((i, v))

    def search(
        self, query: np.ndarray, k: int = 10, n_probe: int = 5,
    ) -> list[tuple[int, float]]:
        assert self.centroids is not None
        c_dists = np.linalg.norm(self.centroids - query, axis=1)
        top_clusters = np.argsort(c_dists)[:n_probe]
        candidates = []
        for c in top_clusters:
            for idx, vec in self.buckets.get(int(c), []):
                dist = float(np.linalg.norm(query - vec))
                candidates.append((idx, dist))
        candidates.sort(key=lambda x: x[1])
        return candidates[:k]
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| HNSW | 低延迟、中等规模 | ~10M 向量以下召回/延迟权衡最优 |
| IVF-PQ | 十亿级、内存受限 | 压缩使十亿级内存检索成为可能 |
| 混合 (IVF-HNSW) | 大规模 + 低延迟 | IVF 用于分区，HNSW 在分区内搜索 |
| **GPU ANN (RAFT)** | 超高吞吐 | GPU 加速的批量查询 |
| **Filtered Search（过滤搜索）** | 元数据约束 | 预过滤或后过滤结合属性谓词 |

### Common Interview Questions
- [ ] 比较 HNSW 与 IVF-PQ——何时选择哪个？
- [ ] 如何处理实时索引更新（新物品）？
- [ ] 什么是召回-延迟权衡以及如何调优？
- [ ] 乘积量化如何减少内存？
- [ ] 如何在 ANN 搜索中添加元数据过滤？

## Comparisons

| 维度 | HNSW | IVF-PQ | ScaNN | Annoy |
|------|------|--------|-------|-------|
| Recall@10 | 0.98+ | 0.90-0.95 | 0.95+ | 0.90 |
| 延迟 (1M) | ~1ms | ~2ms | ~0.5ms | ~5ms |
| 每向量内存 | 完整 (4d 字节) | 压缩 (m 字节) | 压缩 | 完整 |
| 构建时间 | 慢 | 快 | 中等 | 快 |
| 更新支持 | 部分支持 | 需重建 | 需重建 | 需重建 |

## Key Takeaways
- [ ] HNSW 是大多数场景（<100M 向量）的默认选择
- [ ] IVF-PQ 使十亿级搜索在可接受的召回率下成为可能
- [ ] 调节 ef_search（HNSW）或 n_probe（IVF）控制召回-延迟权衡
- [ ] 乘积量化将内存减少 10-30 倍，召回率损失适中
- [ ] 实时更新是挑战——大多数系统使用定期重建索引
"""

# ============================================================
# NODE 101: Feature Store
# ============================================================
NODES[101] = r"""# Feature Store

## Overview

**Feature Store（特征存储）** 是管理、计算、存储和服务 ML 特征的集中化系统。它解决了 **Training-Serving Skew（训练-服务偏差）** 问题，促进特征复用，并提供一致的特征新鲜度保证。这是系统设计面试中测试的关键基础设施组件。

Feature Store 的核心价值在于：为 ML 特征提供"单一事实来源"，确保训练时使用的特征与线上服务时完全一致。没有 Feature Store 时，训练和服务使用不同的代码路径计算特征，是 ML 系统中最常见的静默错误来源。

## Core Concepts

### Why Feature Stores?

Feature Store 解决的五大核心问题：

| 问题 | 无 Feature Store | 有 Feature Store |
|------|-----------------|-----------------|
| 训练-服务偏差 | 不同代码路径 | 单一定义，双重物化 |
| 特征复用 | 团队间复制粘贴 | 共享特征目录 |
| 新鲜度 SLA | 临时性、不一致 | 声明式新鲜度保证 |
| **Point-in-time Correctness（时间点正确性）** | 标签泄露风险 | 内置时间旅行查询 |
| 特征发现 | 四处询问 | 可搜索的目录 + 元数据 |

### Architecture

Feature Store 的标准架构包含特征定义、转换引擎和双重存储：

```
[Feature Definitions（特征定义）(代码)]
        |
   [Transformation Engine（转换引擎）]
    /                  \
[Batch Pipeline]    [Stream Pipeline]
(Spark/Airflow)     (Flink/Kafka)
    \                  /
[Offline Store]    [Online Store]
(Data Warehouse)   (Redis/DynamoDB)
    |                  |
[Training]         [Serving]
```

**Dual Materialization（双重物化）** 是 Feature Store 的核心模式：同一份特征定义代码被物化到两个不同的存储中——离线存储用于训练（支持大批量读取），在线存储用于服务（支持低延迟点查）。

### Feature Freshness Tiers

特征按新鲜度需求分为三个层级：

| 层级 | 新鲜度 | 计算方式 | 存储 | 示例 |
|------|--------|---------|------|------|
| **Batch（批处理）** | 小时-天 | Spark 定时任务 | 数据仓库 | 30 天购买次数 |
| **Near-real-time（近实时）** | 分钟级 | Flink/Kafka | Redis | 会话点击计数 |
| **Real-time（实时）** | 毫秒级 | 请求时计算 | 计算生成 | 当前 GPS 位置 |

选择合适的新鲜度层级需要权衡计算成本、基础设施复杂度和模型质量收益。通常 80% 的特征是批处理特征，15% 是近实时特征，5% 是实时特征。

### Point-in-Time Correctness

训练数据中的特征必须反映 **预测时刻** 已知的信息，而非标签时刻的信息：

$$
\text{features}(t) = \{f_i(t) : f_i \text{ 在时刻 } t \text{ 可用}\}
$$

如果不遵守这一原则，就会产生 **Label Leakage（标签泄露）**——模型在训练时看到了未来的信息。例如：预测用户是否会在周五购买，但训练时使用了周五之后的浏览数据。Feature Store 通过维护特征的时间戳版本，自动实现时间旅行查询。

### Key Design Decisions

| 设计决策 | 选项 | 权衡 |
|---------|------|------|
| 在线存储 | Redis, DynamoDB, Bigtable | 延迟 vs 成本 vs 规模 |
| 离线存储 | S3/GCS + Parquet, 数据仓库 | 成本 vs 查询灵活性 |
| 转换引擎 | SQL, PySpark, Pandas | 表达能力 vs 性能 |
| 注册中心 | 中央特征目录 | 特征可发现性 |
| 监控 | 每特征漂移检测 | 运维开销 |

### Feature Monitoring

特征质量监控是 Feature Store 的关键能力：

- **Null Rate（空值率）** 监控：特征空值突增可能意味着数据管道故障
- **Distribution Drift（分布漂移）**：使用 PSI 或 KS 检验检测特征分布变化
- **Freshness Monitoring（新鲜度监控）**：特征最后更新时间是否超过 SLA
- **Cardinality Check（基数检查）**：类别特征的不同值数量是否异常

## Implementation

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class FeatureDefinition:
    name: str
    entity_key: str
    freshness: str
    dtype: str
    description: str = ""
    owner: str = ""
    tags: list[str] = field(default_factory=list)

class SimpleFeatureStore:
    def __init__(self) -> None:
        self.registry: dict[str, FeatureDefinition] = {}
        self.online: dict[str, dict[str, Any]] = {}

    def register(self, defn: FeatureDefinition) -> None:
        self.registry[defn.name] = defn

    def materialize(self, feature: str, entity_values: dict[str, Any]) -> None:
        if feature not in self.registry:
            raise KeyError(f"Unknown feature: {feature}")
        self.online.setdefault(feature, {}).update(entity_values)

    def get_online_features(
        self, features: list[str], entity_key: str, entity_id: str,
    ) -> dict[str, Any]:
        result = {}
        for f in features:
            store = self.online.get(f, {})
            result[f] = store.get(entity_id)
        return result
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 双重物化 | 训练+服务一致性 | 相同转换代码，不同存储后端 |
| 特征版本管理 | Schema 演进 | 版本化特征避免破坏下游消费者 |
| **Backfill Pipeline（回填管道）** | 历史特征用于训练 | 为过去的时间戳重新计算特征 |
| 特征监控 | 漂移检测 | 当特征分布偏移时告警 |
| **Entity Key Design（实体键设计）** | 多实体特征 | 复合键 (user_id, item_id) 用于交互特征 |

### Common Interview Questions
- [ ] Feature Store 如何防止训练-服务偏差？
- [ ] 设计支持批处理和实时特征的 Feature Store
- [ ] 如何处理训练数据的时间点正确性？
- [ ] 如何监控特征质量和新鲜度？
- [ ] 什么时候不需要使用 Feature Store？

## Comparisons

| 维度 | Feast | Tecton | Hopsworks | 自建 |
|------|-------|--------|-----------|------|
| 托管方式 | 自管理 | 托管服务 | 托管/自管 | 自建 |
| 实时能力 | 基础 | 高级 | 高级 | 灵活 |
| 转换 | 有限 | 完整管道 | 完整管道 | 自定义 |
| 成本 | 免费（开源） | 企业级 | 企业级 | 工程时间 |

## Key Takeaways
- [ ] Feature Store 解决训练-服务偏差——ML 中最常见的静默错误
- [ ] 时间点正确性防止训练数据中的标签泄露
- [ ] 按新鲜度层级（批处理/近实时/实时）设计特征
- [ ] 特征监控（漂移、空值率、延迟）至关重要
- [ ] 从简单开始（批处理特征 + Redis）按需增加复杂度
"""

# ============================================================
# NODE 102: Embedding Techniques
# ============================================================
NODES[102] = r"""# Embedding Techniques

## Overview

**Embedding Techniques（嵌入技术）** 将离散或高维输入转换为稠密的低维向量表示。它们是现代 ML 系统的基石——驱动搜索、推荐、NLP 和多模态应用。理解 Embedding 的训练、服务和质量评估对资深 MLE 面试至关重要。

Embedding 的核心思想是：将语义相似的实体映射到向量空间中相近的位置。这使得"相似性"可以通过简单的向量运算（如余弦相似度、点积）来高效计算。

## Core Concepts

### Embedding Types

不同输入类型对应的 Embedding 方法：

| 输入类型 | 方法 | 输出 |
|---------|------|------|
| 词/Token | **Word2Vec**, **GloVe**, **BPE (Byte Pair Encoding，字节对编码)** 子词 | Token Embedding |
| 句子/文档 | **BERT**, E5, BGE, **Sentence-BERT** | 文本 Embedding |
| 用户/物品 | 双塔模型、矩阵分解 | 实体 Embedding |
| 图像 | CNN/ViT 骨干网络 | 视觉 Embedding |
| 类别特征 | 学习的查找表 | 特征 Embedding |

### Word2Vec (Skip-gram)

**Word2Vec** 通过预测上下文词来学习词向量——中心词预测周围词：

$$
\mathcal{L} = -\sum_{(w, c) \in D} \log \sigma(v_c^T v_w) - \sum_{(w, c') \in D'} \log \sigma(-v_{c'}^T v_w)
$$

其中 $D$ 是正样本对（词及其上下文），$D'$ 是负采样对，$\sigma$ 是 Sigmoid 函数。Word2Vec 的关键洞察是：经常出现在相似上下文中的词会获得相似的向量表示。

Word2Vec 的经典特性——向量算术捕获语义关系：$\text{king} - \text{man} + \text{woman} \approx \text{queen}$。

### BERT Embeddings

**BERT (Bidirectional Encoder Representations from Transformers，双向变换器编码表示)** 生成上下文相关的词向量——同一个词在不同上下文中有不同的 Embedding。

获取句子 Embedding 的方法：
- **CLS Token**：取 [CLS] 位置的输出作为句子表示。简单但质量一般。
- **Mean Pooling（均值池化）**：对所有 Token 的输出取平均。通常优于 CLS。
- **Sentence-BERT**：使用孪生网络在 **NLI (Natural Language Inference，自然语言推理)** 数据上微调，专门优化句子表示。

### Contrastive Learning for Embeddings

**Contrastive Learning（对比学习）** 是当前 Embedding 训练的主流范式。**InfoNCE** 损失（用于 CLIP, SimCLR, E5 等）：

$$
\mathcal{L} = -\log \frac{\exp(\text{sim}(z_i, z_j^+) / \tau)}{\sum_{k=1}^{N} \exp(\text{sim}(z_i, z_k) / \tau)}
$$

其中 $z_i$ 和 $z_j^+$ 是正样本对的表示，分母包含所有正负样本。$\tau$ 是温度参数。对比学习的核心理念：拉近正样本对的距离，推远负样本对的距离。

**CLIP (Contrastive Language-Image Pre-training，对比语言-图像预训练)** 使用 InfoNCE 损失在图文配对数据上训练，将文本和图像映射到同一向量空间，实现跨模态检索。

### Embedding Quality Metrics

Embedding 质量的评估方法：

| 指标 | 衡量内容 | 计算方式 |
|------|---------|---------|
| 内在指标：类比 | 关系结构 | "king - man + woman = queen" |
| 内在指标：聚类 | 语义分组 | 类别数据上的 **Silhouette Score（轮廓系数）** |
| 外在指标：检索 | 下游效用 | 检索任务上的 Recall@K |
| **Alignment（对齐度）** | 跨模态一致性 | 匹配对的 Embedding 相似度 |
| **Uniformity（均匀度）** | 空间利用率 | $\log \mathbb{E}[e^{-2\|z_i - z_j\|^2}]$——越低表示分布越均匀 |

好的 Embedding 空间应该同时具有高对齐度（相似的实体接近）和高均匀度（向量均匀分布在超球面上，充分利用向量空间）。

### Embedding Dimension Selection

维度选择的经验规则：

$$
d \approx \min(600, \; 4 \times (\text{vocab size})^{0.25})
$$

实践中通常使用 64-512 维。更高维度增加表达能力但也增加内存和 ANN 延迟。选择维度时需要考虑：下游任务复杂度、向量存储成本、ANN 索引性能。

## Implementation

```python
import numpy as np

class EmbeddingTable:
    # 带 L2 归一化的 Embedding 查找表

    def __init__(self, vocab_size: int, dim: int) -> None:
        scale = np.sqrt(2.0 / (vocab_size + dim))
        self.weights = np.random.randn(vocab_size, dim) * scale

    def lookup(self, ids: list[int]) -> np.ndarray:
        embs = self.weights[ids]
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        return embs / (norms + 1e-8)

    def similarity(self, id_a: int, id_b: int) -> float:
        a = self.lookup([id_a])[0]
        b = self.lookup([id_b])[0]
        return float(np.dot(a, b))

def mean_pooling(
    token_embeddings: np.ndarray,
    attention_mask: np.ndarray,
) -> np.ndarray:
    # 对 Token Embedding 做均值池化（生成句子 Embedding）
    mask = attention_mask[:, :, None]
    summed = (token_embeddings * mask).sum(axis=1)
    counts = mask.sum(axis=1).clip(min=1e-8)
    return summed / counts
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 预训练 + 微调 | 大多数 NLP 任务 | 从 BERT/E5 开始，在领域数据上微调 |
| Embedding 压缩 | 内存优化 | PQ、标量量化或降维 |
| 多模态 Embedding | 跨模态搜索 | CLIP 风格训练对齐文本和图像空间 |
| Embedding 版本管理 | 生产更新 | 重训 Embedding 需要重建 ANN 索引 |
| 负样本挖掘 | 提升检索质量 | 从当前模型 Top-K 错误中挖掘困难负样本 |

### Common Interview Questions
- [ ] 如何在有限数据下为新领域训练 Embedding？
- [ ] 何时使用预训练 vs 任务特定的 Embedding？
- [ ] 如何处理模型更新时的 Embedding 漂移？
- [ ] 比较 Mean Pooling 与 CLS Token 的句子 Embedding
- [ ] 如何压缩 Embedding 以支持十亿级服务？

## Comparisons

| 维度 | Word2Vec | BERT (CLS) | Sentence-BERT | E5/BGE |
|------|---------|------------|---------------|--------|
| 粒度 | 词级 | Token/句子 | 句子 | 句子 |
| 上下文感知 | 否 | 是 | 是 | 是 |
| 训练数据 | 无标注文本 | 无标注文本 | NLI 标注对 | 多样化标注对 |
| 检索质量 | 低 | 中等 | 好 | 最好 |

## Key Takeaways
- [ ] Embedding 是离散数据与 ML 模型之间的通用接口
- [ ] 对比学习（InfoNCE）是当前主流的训练范式
- [ ] Embedding 质量直接决定检索系统质量
- [ ] 压缩（PQ、量化）使十亿级部署成为可能
- [ ] 始终在下游任务上评估 Embedding，而非仅用内在指标
"""

# ============================================================
# NODE 103: Real-time Feature Computation
# ============================================================
NODES[103] = r"""# Real-time Feature Computation

## Overview

**Real-time Feature Computation（实时特征计算）** 在事件发生后的毫秒到秒级时间内为 ML 预测提供最新的信号。这对 **Fraud Detection（欺诈检测）**（近期交易速率）、推荐系统（会话点击）和动态定价（当前供需）至关重要。设计低延迟、高吞吐量的特征管道是系统设计面试的关键技能。

实时特征的价值在于：许多 ML 预测的质量高度依赖于最新的用户行为和系统状态。例如，欺诈检测中"过去 5 分钟内的交易次数"比"过去 30 天的平均交易次数"更具预测价值。

## Core Concepts

### Feature Freshness Spectrum

特征新鲜度从批处理到实时形成一个连续谱：

```
[Batch（批处理）: 小时级]  ->  [Near-RT（近实时）: 分钟级]  ->  [Real-time（实时）: 毫秒级]
  Spark/Hive                    Flink/Kafka                    请求时计算
  数据仓库                       Redis/DynamoDB                 内存中
```

### Stream Processing Architecture

流处理系统的标准架构：

```
[Event Source（事件源）] -> [Kafka] -> [Stream Processor（流处理器）(Flink)]
    -> [Aggregation（聚合）] -> [Online Store（在线存储）(Redis)] -> [Feature Serving（特征服务）]
```

**Apache Kafka** 作为事件总线提供持久化、分区和重放能力。**Apache Flink** 作为流处理引擎提供精确一次语义和窗口聚合。Redis 作为在线存储提供亚毫秒级的读取延迟。

### Common Real-time Feature Patterns

实时特征的五种常见模式：

| 模式 | 示例 | 窗口类型 |
|------|------|---------|
| **Sliding Window Count（滑动窗口计数）** | 过去 1 小时的点击次数 | 时间窗口 |
| **Sliding Window Avg（滑动窗口平均）** | 过去 24 小时的平均消费 | 时间窗口 |
| **Session Aggregates（会话聚合）** | 本次会话浏览的物品 | 会话作用域 |
| **Last-N Events（最近 N 个事件）** | 最近 5 次搜索查询 | 计数窗口 |
| **Exponential Decay（指数衰减）** | 加权近期活动 | 连续衰减 |

### Windowed Aggregation

**Tumbling Window（滚动窗口）**（非重叠）：
$$
f(t) = \text{AGG}(\{e_i : t_{\text{start}} \leq e_i.t < t_{\text{end}}\})
$$

滚动窗口将时间轴切分为等长的不重叠区间，每个区间独立聚合。

**Sliding Window（滑动窗口）**（重叠）：
$$
f(t) = \text{AGG}(\{e_i : t - w \leq e_i.t < t\})
$$

滑动窗口在每个时间点维护一个固定长度的时间段，随时间滑动。实现上通常使用环形缓冲区或双端队列来高效管理窗口内的事件。

### Exponential Moving Average

**EMA (Exponential Moving Average，指数移动平均)** 是一种内存高效的替代方案，无需存储所有历史事件：

$$
\text{EMA}(t) = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EMA}(t-1)
$$

其中 $\alpha = 1 - e^{-\Delta t / \text{halflife}}$ 用于时间加权衰减。$\text{halflife}$ 是半衰期——经过一个半衰期后，旧信号的权重减半。EMA 仅需存储一个值和一个时间戳，空间复杂度 $O(1)$，而滑动窗口需要 $O(w)$ 空间存储窗口内所有事件。

### Challenges

实时特征计算面临的主要挑战及解决方案：

| 挑战 | 解决方案 |
|------|---------|
| **Late-arriving Events（迟到事件）** | **Watermark（水位线）** + 允许的迟到时间 |
| **Exactly-once Semantics（精确一次语义）** | Kafka 事务 + 幂等写入 |
| **High Cardinality Keys（高基数键）** | 近似数据结构：**HyperLogLog (HLL，超对数计数)** 用于唯一计数, **Count-Min Sketch (CMS，计数最小草图)** 用于频率估计 |
| 特征服务延迟 | 预计算后缓存在 Redis 中 |
| 训练数据回填 | 通过相同管道重放事件 |

**HyperLogLog** 用 $O(\log \log n)$ 空间估计唯一元素数量，误差约 2%。**Count-Min Sketch** 用固定空间估计元素频率，仅会高估不会低估。

## Implementation

```python
import time
from collections import defaultdict, deque

class SlidingWindowCounter:
    # O(1) 摊销的滑动窗口事件计数器

    def __init__(self, window_secs: int = 3600) -> None:
        self.window = window_secs
        self.queues: dict[str, deque[float]] = defaultdict(deque)

    def add(self, key: str, ts: float | None = None) -> None:
        ts = ts or time.monotonic()
        self.queues[key].append(ts)

    def count(self, key: str, now: float | None = None) -> int:
        now = now or time.monotonic()
        q = self.queues[key]
        cutoff = now - self.window
        while q and q[0] < cutoff:
            q.popleft()
        return len(q)

class ExponentialMovingAvg:
    # 时间加权指数移动平均

    def __init__(self, halflife_secs: float = 3600.0) -> None:
        self.halflife = halflife_secs
        self.state: dict[str, tuple[float, float]] = {}

    def update(self, key: str, value: float, ts: float) -> float:
        if key not in self.state:
            self.state[key] = (value, ts)
            return value
        prev_ema, prev_ts = self.state[key]
        import math
        dt = max(0.0, ts - prev_ts)
        alpha = 1.0 - math.exp(-dt / self.halflife)
        new_ema = alpha * value + (1 - alpha) * prev_ema
        self.state[key] = (new_ema, ts)
        return new_ema
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| **Lambda Architecture（Lambda 架构）** | 批处理 + 实时特征 | 批处理保证准确性，流处理保证新鲜度 |
| **Kappa Architecture（Kappa 架构）** | 纯流处理 | 将一切视为流来简化架构 |
| 特征日志 | 训练数据生成 | 在预测时记录特征用于离线回放 |
| 近似聚合 | 高基数键 | HyperLogLog 用于唯一计数，CMS 用于频率 |
| 双写一致性 | Feature Store 更新 | 从单一来源同时写入批处理和在线存储 |

### Common Interview Questions
- [ ] 如何确保批处理和实时特征之间的一致性？
- [ ] 为欺诈检测设计实时特征管道
- [ ] 如何处理流处理管道中的迟到事件？
- [ ] 何时使用近似数据结构（HLL、CMS）？
- [ ] 如何为历史训练数据回填实时特征？

## Comparisons

| 维度 | Batch (Spark) | Near-RT (Flink) | 请求时计算 |
|------|-------------|-----------------|-----------|
| 新鲜度 | 小时级 | 秒-分钟 | 毫秒级 |
| 吞吐量 | 非常高 | 高 | 受请求限制 |
| 复杂度 | 低 | 中等 | 高 |
| 成本 | 低（竞价实例） | 中（常驻服务） | 高（每请求计算） |
| 回填 | 容易 | 中等（需要重放） | 困难 |

## Key Takeaways
- [ ] 特征新鲜度直接影响时间敏感应用的模型质量
- [ ] 滑动窗口聚合是最常见的实时特征模式
- [ ] EMA 是滑动窗口的内存高效替代方案
- [ ] 迟到事件和精确一次语义是主要工程挑战
- [ ] 在预测时记录特征以实现一致的离线训练
"""

# ============================================================
# NODE 104: A/B Testing
# ============================================================
NODES[104] = r"""# A/B Testing

## Overview

**A/B Testing（A/B 测试）** 是在生产环境中评估 ML 模型变更的黄金标准。它提供了关于业务指标影响的因果证据。资深 MLE 必须理解实验设计、统计分析和常见陷阱。该主题在每个主要科技公司的面试中都会考察。

A/B 测试的核心价值在于：离线指标（AUC、NDCG）与在线业务指标之间的相关性常常不一致。只有 A/B 测试能提供模型变更对真实用户行为影响的因果证据。

## Core Concepts

### Experiment Design

A/B 实验的标准流程：

```
[流量] -> [Randomization Unit（随机化单元）] -> [Control（对照组 A）] -> [指标收集]
                                              -> [Treatment（实验组 B）] -> [指标收集]
                                                        |
                                                  [统计检验]
                                                        |
                                                  [发布 / 迭代]
```

随机化单元的选择至关重要——用户级随机化是最常见的选择，但在存在网络效应时需要考虑集群随机化。

### Hypothesis Testing Framework

**Null Hypothesis（零假设）**：$H_0: \mu_B - \mu_A = 0$（无效果）
**Alternative Hypothesis（备择假设）**：$H_1: \mu_B - \mu_A \neq 0$

**比例的 Z 检验**（例如 CTR）：

$$
Z = \frac{\hat{p}_B - \hat{p}_A}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_A} + \frac{1}{n_B}\right)}}
$$

其中 $\hat{p} = \frac{n_A \hat{p}_A + n_B \hat{p}_B}{n_A + n_B}$ 是 **Pooled Proportion（合并比例）**。当 $|Z|$ 超过临界值（例如双侧 $\alpha=0.05$ 时为 1.96），拒绝零假设。

### Sample Size Calculation

样本量计算是实验设计中最关键的步骤——过小的样本导致无法检测到真实效果，过大的样本浪费时间和流量：

$$
n = \frac{(z_{\alpha/2} + z_\beta)^2 \cdot 2\sigma^2}{\delta^2}
$$

其中：
- $\delta$ 是 **MDE (Minimum Detectable Effect，最小可检测效应)**——你希望能检测到的最小变化幅度
- $\sigma^2$ 是指标的方差
- $z_{\alpha/2}$ 对应显著性水平（$\alpha=0.05$ 时为 1.96）
- $z_\beta$ 对应检验功效（$1-\beta=0.8$ 时为 0.84）

例如：基线 CTR 为 2%，希望检测 5% 的相对提升（MDE = 0.1%），则 $\delta = 0.001$, $\sigma^2 = 0.02 \times 0.98 = 0.0196$，$n \approx 308,000$ 每组。

### Common Pitfalls

A/B 测试中的常见陷阱及解决方案：

| 陷阱 | 问题 | 解决方案 |
|------|------|---------|
| **Peeking（偷看）** | 反复检查结果导致假阳性率膨胀 | **Sequential Testing（序贯检验）**——使用始终有效的 p 值 |
| **Network Effects（网络效应）** | 实验单元之间相互干扰 | **Cluster Randomization（集群随机化）** |
| **Simpson's Paradox（辛普森悖论）** | 分段效果与总体效果矛盾 | 预分层 |
| **Novelty Effect（新鲜感效应）** | 短期参与度飙升 | 运行多周实验 |
| **Multiple Testing（多重检验）** | 族错误率膨胀 | **Bonferroni** 或 **FDR (False Discovery Rate，假发现率)** 校正 |

**Sequential Testing** 是现代实验平台的标准——允许在实验运行过程中持续检查结果，同时控制假阳性率。相比固定样本检验，可以在效果显著时提前停止实验，节省 20-30% 的实验时间。

### Variance Reduction Techniques

**CUPED (Controlled-experiment Using Pre-Experiment Data，使用实验前数据的控制实验)**：

$$
\hat{\mu}_{\text{CUPED}} = \bar{Y} - \theta(\bar{X} - \mathbb{E}[X])
$$

其中 $\theta = \text{Cov}(X, Y) / \text{Var}(X)$，$X$ 是实验前指标（如上周的 CTR）。CUPED 利用实验前的用户行为作为协变量，消除用户间的固有差异。

方差缩减效果：
$$
\text{Var}(\hat{\mu}_{\text{CUPED}}) = \text{Var}(Y)(1 - \rho_{XY}^2)
$$

当实验前后指标的相关性 $\rho_{XY}$ 较高时（通常 0.5-0.8），可以将所需样本量减少 30-50%。这意味着实验可以更快达到统计显著性，加速迭代速度。

### Metric Design

好的实验指标设计原则：
- **Primary Metric（主要指标）**：必须直接反映业务目标，且对变更足够敏感
- **Guardrail Metrics（护栏指标）**：确保实验不会损害关键体验（如页面加载时间、崩溃率）
- **Surrogate Metrics（代理指标）**：当主要指标需要较长时间才能观测到时（如长期留存），使用短期可观测的代理指标

## Implementation

```python
import numpy as np
from scipy import stats

def ab_test_proportions(
    conversions_a: int, total_a: int,
    conversions_b: int, total_b: int,
    alpha: float = 0.05,
) -> dict[str, float]:
    # 双比例 Z 检验
    p_a = conversions_a / total_a
    p_b = conversions_b / total_b
    p_pool = (conversions_a + conversions_b) / (total_a + total_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/total_a + 1/total_b))
    z_stat = (p_b - p_a) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    return {
        "p_a": p_a, "p_b": p_b,
        "lift": (p_b - p_a) / p_a if p_a > 0 else 0.0,
        "z_stat": z_stat, "p_value": p_value,
        "significant": p_value < alpha,
    }

def sample_size_proportions(
    baseline_rate: float, mde_relative: float,
    alpha: float = 0.05, power: float = 0.8,
) -> int:
    # 计算比例检验的每组所需样本量
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde_relative)
    delta = abs(p2 - p1)
    sigma_sq = p1 * (1 - p1) + p2 * (1 - p2)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = ((z_alpha + z_beta) ** 2 * sigma_sq) / (delta ** 2)
    return int(np.ceil(n))
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 序贯检验 | 尽早决策 | 始终有效的 p 值允许随时检查结果 |
| CUPED | 方差缩减 | 使用实验前数据减少 30-50% 的样本需求 |
| 集群随机化 | 社交/市场 | 用于存在网络效应的实验 |
| 分层分析 | 异质性检测 | 按用户群组分析效果差异 |
| **Interleaving（交错实验）** | 排序系统 | 在同一用户面前交错展示两个模型的结果 |

### Common Interview Questions
- [ ] 为什么不能在实验运行中反复检查显著性？
- [ ] 如何计算 A/B 测试的样本量？
- [ ] 解释 CUPED 及其如何加速实验
- [ ] 如何处理社交网络中的网络效应？
- [ ] 什么时候 A/B 测试不适用？

## Comparisons

| 维度 | 固定样本检验 | 序贯检验 | Bayesian A/B |
|------|------------|---------|-------------|
| 何时查看 | 仅在终点 | 随时 | 随时 |
| 停止规则 | 固定 N | 置信序列 | 后验概率 |
| 解释 | p 值 | 始终有效 p 值 | 后验分布 |
| 样本效率 | 基线 | 更好（可提前停止） | 相当 |

## Key Takeaways
- [ ] 样本量计算必须在实验开始前完成——事后计算是无意义的
- [ ] CUPED 是加速实验最实用的技术——利用实验前数据减少方差
- [ ] 偷看（反复检查结果）是最常见的错误——使用序贯检验
- [ ] 护栏指标防止实验损害关键用户体验
- [ ] 理解何时 A/B 测试不适用：小流量、长期效果、网络效应场景
"""

# ============================================================
# NODE 105: Exploration / Exploitation
# ============================================================
NODES[105] = r"""# Exploration / Exploitation

## Overview

**Exploration / Exploitation（探索与利用）** 权衡是 ML 系统中必须同时利用已知最优选项和发现潜在更优选项的基本问题。它出现在推荐系统（新内容发现）、广告系统（新创意测试）和任何存在反馈循环的系统中。

探索-利用困境的本质是：如果系统只利用当前已知的最佳选项，就会陷入局部最优，错过可能更好的新选项；如果过度探索，又会牺牲短期收益。最优策略需要在信息获取价值和即时回报之间取得动态平衡。

## Core Concepts

### The Multi-Armed Bandit Framework

**MAB (Multi-Armed Bandit，多臂老虎机)** 是探索-利用问题的经典抽象。在每一轮中：
1. 从 $K$ 个臂（选项）中选择一个
2. 获得该臂的随机奖励
3. 目标：最大化累积奖励（等价于最小化 **Regret，遗憾**）

$$
\text{Regret}(T) = T \cdot \mu^* - \sum_{t=1}^{T} \mu_{a_t}
$$

其中 $\mu^*$ 是最佳臂的期望奖励，$\mu_{a_t}$ 是第 $t$ 轮选择的臂的期望奖励。好的策略应该实现 $O(\sqrt{T})$ 或 $O(\log T)$ 的遗憾增长率。

### Epsilon-Greedy

**Epsilon-Greedy（$\epsilon$-贪心）** 是最简单的探索策略：

- 以概率 $1 - \epsilon$ 选择当前估计最佳的臂（利用）
- 以概率 $\epsilon$ 随机选择一个臂（探索）

$$
a_t = \begin{cases} \arg\max_a \hat{\mu}_a & \text{with probability } 1 - \epsilon \\ \text{random arm} & \text{with probability } \epsilon \end{cases}
$$

优点是简单易实现，缺点是对所有臂均匀探索而非优先探索不确定性高的臂。$\epsilon$ 的衰减策略（如 $\epsilon_t = \epsilon_0 / t$）可以在后期减少探索，但调参困难。

### UCB (Upper Confidence Bound)

**UCB (Upper Confidence Bound，置信上界)** 策略选择"乐观估计"最高的臂：

$$
a_t = \arg\max_a \left[\hat{\mu}_a + c \sqrt{\frac{\ln t}{n_a}}\right]
$$

其中 $\hat{\mu}_a$ 是臂 $a$ 的样本均值，$n_a$ 是臂 $a$ 被选择的次数，$c$ 是探索系数。

UCB 的核心思想是"面对不确定性保持乐观"——探索项 $c \sqrt{\frac{\ln t}{n_a}}$ 随着臂被探索的次数增加而减小。这意味着：被探索次数少的臂获得更大的探索奖励，自然地引导系统优先探索不确定性高的选项。

UCB 有理论保证的遗憾上界 $O(\sqrt{KT \ln T})$，其中 $K$ 是臂的数量。

### Thompson Sampling

**Thompson Sampling（汤普森采样）** 是一种贝叶斯方法，通过后验分布采样实现概率匹配：

1. 维护每个臂的奖励分布的后验
2. 从每个臂的后验中采样一个值
3. 选择采样值最高的臂
4. 观察奖励，更新后验

对于伯努利（点击/不点击）奖励：
$$
\theta_a \sim \text{Beta}(\alpha_a, \beta_a)
$$

其中 $\alpha_a$ 是成功次数 + 先验，$\beta_a$ 是失败次数 + 先验。每次选择后，根据观察到的结果更新 $\alpha$ 或 $\beta$。

Thompson Sampling 的优势：自然地平衡探索和利用（不确定性高的臂被采样到高值的概率更大）、在实践中通常优于 UCB、易于扩展到上下文 Bandit。

### Contextual Bandits

**Contextual Bandits（上下文 Bandit）** 扩展了 MAB——每轮决策时可以观察到上下文特征 $x_t$：

$$
a_t = \pi(x_t) = \arg\max_a f(x_t, a)
$$

这更接近实际应用场景。例如在推荐系统中：上下文是用户特征，臂是候选物品，奖励是是否点击。

常用算法：
- **LinUCB**：假设奖励与特征线性相关，$\hat{\mu}_a = x^T \theta_a + c \sqrt{x^T A_a^{-1} x}$
- **Neural Contextual Bandit**：用神经网络建模奖励函数，使用 Thompson Sampling 或 UCB 探索

### Application in ML Systems

探索-利用在实际 ML 系统中的应用：

| 应用场景 | 探索 | 利用 | 策略 |
|---------|------|------|------|
| 推荐新内容 | 展示新/冷启动内容 | 展示已验证的高质量内容 | Thompson Sampling 在重排序中 |
| 广告新创意 | 测试新广告创意 | 展示高 CTR 创意 | UCB 分配探索预算 |
| 搜索排序 | 尝试新排序模型 | 使用当前最优模型 | Interleaving + Bandit |
| 通知推送 | 测试新消息模板 | 使用已知最优模板 | Epsilon-Greedy |

## Implementation

```python
import numpy as np

class EpsilonGreedy:
    # Epsilon-Greedy 策略

    def __init__(self, n_arms: int, epsilon: float = 0.1) -> None:
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)

    def select_arm(self) -> int:
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_arms)
        return int(np.argmax(self.values))

    def update(self, arm: int, reward: float) -> None:
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n

class ThompsonSampling:
    # Beta-Bernoulli Thompson Sampling

    def __init__(self, n_arms: int) -> None:
        self.alpha = np.ones(n_arms)
        self.beta = np.ones(n_arms)

    def select_arm(self) -> int:
        samples = np.random.beta(self.alpha, self.beta)
        return int(np.argmax(samples))

    def update(self, arm: int, reward: float) -> None:
        if reward > 0:
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1

class UCB:
    # UCB1 策略

    def __init__(self, n_arms: int, c: float = 2.0) -> None:
        self.n_arms = n_arms
        self.c = c
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)
        self.t = 0

    def select_arm(self) -> int:
        self.t += 1
        if self.t <= self.n_arms:
            return self.t - 1  # 先各探索一次
        ucb_values = self.values + self.c * np.sqrt(
            np.log(self.t) / self.counts
        )
        return int(np.argmax(ucb_values))

    def update(self, arm: int, reward: float) -> None:
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| Thompson Sampling | 推荐中的冷启动 | 贝叶斯方法自然平衡探索和利用 |
| UCB | 广告创意测试 | "乐观面对不确定性"原则 |
| Epsilon-Greedy + 衰减 | 简单场景 | 随时间减少探索比例 |
| 上下文 Bandit | 个性化探索 | 根据用户特征定制探索策略 |
| Bandit + A/B | 混合评估 | Bandit 用于快速分配流量，A/B 用于严格评估 |

### Common Interview Questions
- [ ] 比较 Thompson Sampling 和 UCB——各自的优劣？
- [ ] 如何将 Bandit 方法应用到推荐系统的冷启动？
- [ ] 探索-利用与 A/B 测试有何关系？
- [ ] 上下文 Bandit 与标准 Bandit 有何不同？
- [ ] 如何在生产中评估 Bandit 策略的效果？

## Comparisons

| 维度 | Epsilon-Greedy | UCB | Thompson Sampling |
|------|---------------|-----|-------------------|
| 复杂度 | 最简单 | 中等 | 中等 |
| 理论保证 | 线性遗憾 | $O(\sqrt{KT \ln T})$ | $O(\sqrt{KT})$ |
| 实践表现 | 一般 | 好 | 最好 |
| 延迟奖励 | 容易处理 | 困难 | 自然处理 |
| 上下文扩展 | 简单 | LinUCB | Neural TS |

## Key Takeaways
- [ ] Thompson Sampling 在实践中通常是最佳选择——简单且表现优异
- [ ] UCB 提供理论保证的遗憾上界——在需要确定性保证时使用
- [ ] 探索预算应该随时间衰减——早期多探索，后期多利用
- [ ] 上下文 Bandit 将探索个性化——根据用户特征定制策略
- [ ] Bandit 方法可以与 A/B 测试互补——Bandit 用于快速筛选，A/B 用于严格验证
"""

# ============================================================
# NODE 106: Knowledge Distillation
# ============================================================
NODES[106] = r"""# Knowledge Distillation

## Overview

**Knowledge Distillation（知识蒸馏）** 将大型"教师"模型的知识转移到更小的"学生"模型中，使其能够在延迟和内存受限的条件下部署。这对于生产服务至关重要，因为模型大小直接影响推理成本和延迟。知识蒸馏广泛用于搜索排序、推荐系统和移动端部署。

知识蒸馏的核心洞察是：教师模型的"软标签"（如 [0.7, 0.2, 0.1]）比硬标签（如 [1, 0, 0]）包含更丰富的信息——它揭示了类别之间的相似性关系，这种"暗知识"（Dark Knowledge）可以被学生模型学习。

## Core Concepts

### Distillation Loss Function

知识蒸馏的核心损失函数结合了硬标签损失和软标签损失：

$$
L = \alpha L_{hard} + (1-\alpha) T^2 L_{soft}
$$

其中：
- $L_{hard}$ 是学生模型与真实标签之间的标准交叉熵损失
- $L_{soft}$ 是学生模型与教师模型软标签之间的 **KL Divergence（KL 散度）**
- $T$ 是 **Temperature（温度）** 参数——升高温度使概率分布更平滑，暴露类别间的相似性
- $\alpha$ 是硬标签和软标签损失的平衡系数
- $T^2$ 因子用于补偿温度缩放对梯度的影响

**温度的作用**：教师模型的 Softmax 输出通常很尖锐（如 [0.99, 0.005, 0.005]），难以传递类别间的关系。通过温度 $T > 1$：

$$
p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
$$

较高的温度（通常 $T \in [3, 20]$）使分布更加平滑，揭示出教师模型在各类别上的细微差异。例如 $T=5$ 可能将 [0.99, 0.005, 0.005] 变为 [0.6, 0.25, 0.15]，后者包含更多关于类别相似性的信息。

### Distillation Variants

知识蒸馏的不同变体适用于不同场景：

| 变体 | 方法 | 适用场景 |
|------|------|---------|
| **Response-based（基于响应）** | 匹配教师的输出概率 | 分类任务，最经典的方法 |
| **Feature-based（基于特征）** | 匹配中间层的特征表示 | 需要更深层次的知识转移 |
| **Relation-based（基于关系）** | 匹配样本之间的关系模式 | 嵌入学习、度量学习 |
| **Self-distillation（自蒸馏）** | 模型自身的早期层蒸馏到后期层 | 无需额外教师模型 |
| **Online Distillation（在线蒸馏）** | 教师和学生同时训练 | 没有预训练教师时 |

### Feature-based Distillation

**基于特征的蒸馏** 不仅匹配输出，还匹配中间层的表示：

$$
L_{feature} = \sum_{l \in \text{layers}} \| \phi(F_l^{teacher}) - \psi(F_l^{student}) \|^2
$$

其中 $\phi$ 和 $\psi$ 是可选的变换函数，用于对齐教师和学生的特征维度。FitNets 是该方向的代表性工作。

### Architecture Design for Student Models

学生模型的架构选择至关重要：

| 策略 | 描述 | 压缩比 |
|------|------|--------|
| 减少层数 | 保持宽度，减少深度 | 2-4x |
| 减少宽度 | 保持深度，减少隐藏维度 | 2-8x |
| 架构变换 | 用更高效的架构（如 MobileNet 替代 ResNet） | 5-20x |
| **Pruning + Distillation（剪枝+蒸馏）** | 先剪枝后蒸馏恢复精度 | 3-10x |

### Practical Considerations

工程实践中的关键考量：

- **教师模型质量**：教师越强，学生获益越大。使用集成模型（多个教师的平均输出）作为教师通常效果最好。
- **数据量**：蒸馏需要大量无标注数据来生成教师的软标签。可以使用训练数据 + 额外的未标注数据。
- **训练策略**：先用硬标签预训练学生，再用蒸馏损失微调，通常比直接蒸馏效果更好。
- **温度调优**：$T$ 通常在 3-20 之间，需要在验证集上调优。过高的温度会使信息过于模糊。

### Distillation in Production Systems

在工业界的典型应用链路：

```
[大规模教师模型] -- 离线评分 --> [软标签数据]
                                    |
                                    v
[学生模型训练] <-- 蒸馏损失 + 硬标签损失
    |
    v
[部署轻量学生模型] -- 在线推理，满足延迟 SLA
```

例如在搜索排序中：
- 教师：Cross-Encoder BERT-Large（高质量但推理慢，约 100ms/对）
- 学生：轻量 MLP 或 BERT-Tiny（推理快，约 5ms/对）
- 学生在相同延迟下取得接近教师 90-95% 的排序质量

## Implementation

```python
import numpy as np

def softmax_with_temperature(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    # 带温度的 Softmax
    scaled = logits / T
    exp_scaled = np.exp(scaled - scaled.max(axis=-1, keepdims=True))
    return exp_scaled / exp_scaled.sum(axis=-1, keepdims=True)

def distillation_loss(
    student_logits: np.ndarray,
    teacher_logits: np.ndarray,
    hard_labels: np.ndarray,
    temperature: float = 5.0,
    alpha: float = 0.3,
) -> float:
    # 计算知识蒸馏损失
    # 软标签损失 (KL 散度)
    teacher_soft = softmax_with_temperature(teacher_logits, temperature)
    student_soft = softmax_with_temperature(student_logits, temperature)
    kl_div = float((teacher_soft * np.log(
        teacher_soft / (student_soft + 1e-8) + 1e-8
    )).sum(axis=-1).mean())
    soft_loss = temperature ** 2 * kl_div

    # 硬标签损失 (交叉熵)
    student_prob = softmax_with_temperature(student_logits, 1.0)
    hard_loss = float(-np.log(
        student_prob[np.arange(len(hard_labels)), hard_labels.astype(int)] + 1e-8
    ).mean())

    return alpha * hard_loss + (1 - alpha) * soft_loss
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 排序蒸馏 | 搜索/推荐 | Cross-Encoder 教师 -> 轻量排序学生 |
| 多教师蒸馏 | 提高学生上限 | 多个教师的平均/加权输出作为软标签 |
| 渐进式蒸馏 | 极端压缩 | 教师 -> 中等模型 -> 小模型链式蒸馏 |
| 特定任务蒸馏 | NLP | 将通用 LLM 蒸馏为特定任务的小模型 |
| 蒸馏 + 量化 | 边缘部署 | 先蒸馏缩小模型，再量化加速推理 |

### Common Interview Questions
- [ ] 知识蒸馏中温度参数的作用是什么？
- [ ] 软标签比硬标签多提供了什么信息？
- [ ] 何时使用特征蒸馏而非响应蒸馏？
- [ ] 如何为生产搜索排序系统设计蒸馏管道？
- [ ] 蒸馏与模型剪枝/量化的关系和区别？

## Comparisons

| 维度 | 知识蒸馏 | 量化 | 剪枝 |
|------|---------|------|------|
| 压缩方式 | 训练小模型 | 降低数值精度 | 移除冗余参数 |
| 速度提升 | 2-10x | 2-4x | 2-5x |
| 精度保持 | 好（90-95%） | 好（INT8 近无损） | 中等 |
| 训练成本 | 需要重训练 | 低/无需训练 | 中等 |
| 可组合性 | 可与量化/剪枝组合 | 可组合 | 可组合 |

## Key Takeaways
- [ ] 蒸馏损失 $L = \alpha L_{hard} + (1-\alpha) T^2 L_{soft}$ 是核心公式
- [ ] 温度参数 $T$ 控制软标签的平滑程度——更高温度揭示更多类别间关系
- [ ] 软标签的"暗知识"是蒸馏价值的核心来源
- [ ] 蒸馏可以与量化、剪枝组合使用以达到更大的压缩比
- [ ] 在生产中，蒸馏是将重模型的质量"转移"到轻模型的最有效方法
"""

# ============================================================
# NODE 107: Multi-Task Learning
# ============================================================
NODES[107] = r"""# Multi-Task Learning

## Overview

**Multi-Task Learning (MTL，多任务学习)** 使用单个模型同时训练多个相关目标。它通过共享表示减少服务成本（一个模型替代多个）、通过隐式正则化提高泛化能力，并能学习更丰富的特征表示。MTL 广泛应用于排序系统（CTR + 转化率 + 观看时长）、NLP（多语言/多任务模型）和自动驾驶（检测 + 分割 + 深度估计）。

MTL 的核心价值在于：相关任务之间共享底层表示可以引入归纳偏置，帮助模型学习更泛化的特征。同时，单模型服务多任务大幅减少了在线推理的计算和维护成本。

## Core Concepts

### Parameter Sharing Architectures

MTL 架构的两大类——**Hard Parameter Sharing（硬参数共享）** 和 **Soft Parameter Sharing（软参数共享）**：

**Hard Parameter Sharing**——所有任务共享底层网络，顶部各有独立的任务头：

```
[Input Features]
      |
  [Shared Layers（共享层）] -- 所有任务共享的底层表示
      |
   /     |     \
[Head A] [Head B] [Head C]  -- 各任务独立的输出层
 CTR     CVR    Watch Time
```

优点：参数高效、实现简单、正则化效果强。缺点：如果任务差异大会导致 **Negative Transfer（负迁移）**——一个任务的梯度干扰另一个任务的学习。

**Soft Parameter Sharing**——每个任务有独立的网络，通过正则化鼓励参数相似：

$$
\mathcal{L}_{reg} = \sum_{i \neq j} \| W_i - W_j \|^2_F
$$

更灵活但参数量更大。

### Advanced MTL Architectures

工业界常用的高级 MTL 架构：

| 架构 | 核心思想 | 优势 |
|------|---------|------|
| **MMoE (Multi-gate Mixture-of-Experts，多门混合专家)** | 多个专家网络 + 每任务门控 | 自动学习每个任务应共享多少信息 |
| **PLE (Progressive Layered Extraction，渐进式分层提取)** | 任务特定专家 + 共享专家 + 渐进融合 | 缓解负迁移，每层逐步提取任务特定信息 |
| **Cross-Stitch Networks** | 学习任务间特征组合的线性权重 | 灵活的共享模式 |

**MMoE** 的数学表达：

$$
y_k = h_k\left(\sum_{i=1}^{n} g_k^{(i)}(x) \cdot f_i(x)\right)
$$

其中 $f_i(x)$ 是第 $i$ 个专家网络的输出，$g_k^{(i)}(x)$ 是任务 $k$ 对专家 $i$ 的门控权重，$h_k$ 是任务 $k$ 的任务头。门控网络是一个以输入 $x$ 为条件的 Softmax 层，自动为每个样本选择最相关的专家。

### Loss Balancing

多任务学习中的损失平衡是核心挑战——不同任务的损失量级和梯度方向可能差异巨大：

总损失：
$$
\mathcal{L}_{total} = \sum_{k=1}^{K} w_k \mathcal{L}_k
$$

损失权重 $w_k$ 的设置方法：

| 方法 | 描述 | 公式 |
|------|------|------|
| 手动调参 | 根据业务重要性设置 | $w_k$ 手动设定 |
| **Uncertainty Weighting（不确定性加权）** | 基于同方差不确定性自动调参 | $w_k = \frac{1}{2\sigma_k^2}$，$\sigma_k$ 可学习 |
| **GradNorm** | 归一化各任务梯度的范数 | 动态调整 $w_k$ 使梯度范数接近 |
| **Dynamic Weight Average (DWA，动态权重平均)** | 基于损失下降速率调整权重 | $w_k \propto \exp(r_k / T)$，$r_k$ 是损失变化率 |

**Uncertainty Weighting** 的损失函数：

$$
\mathcal{L} = \sum_{k=1}^{K} \frac{1}{2\sigma_k^2} \mathcal{L}_k + \log \sigma_k
$$

其中 $\sigma_k$ 是可学习的参数，表示任务 $k$ 的噪声水平。损失大的任务自动获得较低权重（因为 $1/(2\sigma_k^2)$ 与 $\sigma_k$ 成反比），避免某个困难任务主导整体梯度。

### Gradient Conflict

当不同任务的梯度方向冲突时（梯度余弦相似度为负），会产生 **Gradient Conflict（梯度冲突）**，导致训练不稳定：

$$
\cos(\nabla_\theta \mathcal{L}_i, \nabla_\theta \mathcal{L}_j) < 0
$$

解决方案：
- **PCGrad (Projecting Conflicting Gradients，投影冲突梯度)**：当梯度冲突时，将一个任务的梯度投影到另一个任务梯度的法平面上
- **CAGrad**：在冲突方向上寻找最优折中
- **分离优化器**：不同任务使用不同的学习率

### Task Relationship Modeling

任务之间的关系影响 MTL 的效果：

- **正相关任务**：CTR 和 CVR（点击的用户更可能转化）-> 共享表示有益
- **负相关任务**：短期参与度和长期留存可能冲突 -> 需要软共享或 MMoE
- **层级任务**：ESMM 模型将 CVR 分解为 $P(\text{convert}) = P(\text{click}) \times P(\text{convert}|\text{click})$

## Implementation

```python
import numpy as np

class MultiTaskModel:
    # 简化的硬参数共享 MTL 模型

    def __init__(self, input_dim: int, shared_dim: int, n_tasks: int) -> None:
        self.shared_w = np.random.randn(input_dim, shared_dim) * 0.01
        self.task_heads = [
            np.random.randn(shared_dim, 1) * 0.01 for _ in range(n_tasks)
        ]
        self.n_tasks = n_tasks

    def forward(self, x: np.ndarray) -> list[np.ndarray]:
        shared = np.maximum(0, x @ self.shared_w)  # ReLU
        return [shared @ head for head in self.task_heads]

class UncertaintyWeighting:
    # 基于同方差不确定性的自动损失加权

    def __init__(self, n_tasks: int) -> None:
        self.log_sigma = np.zeros(n_tasks)  # log(sigma)

    def weighted_loss(self, task_losses: list[float]) -> float:
        total = 0.0
        for i, loss in enumerate(task_losses):
            sigma_sq = np.exp(2 * self.log_sigma[i])
            total += loss / (2 * sigma_sq) + self.log_sigma[i]
        return total

class GradNormBalancer:
    # GradNorm 梯度归一化

    def __init__(self, n_tasks: int, alpha: float = 1.5) -> None:
        self.weights = np.ones(n_tasks)
        self.initial_losses: np.ndarray | None = None
        self.alpha = alpha

    def update_weights(
        self, task_losses: np.ndarray, grad_norms: np.ndarray,
    ) -> np.ndarray:
        if self.initial_losses is None:
            self.initial_losses = task_losses.copy()
        # 计算逆训练速率
        loss_ratios = task_losses / (self.initial_losses + 1e-8)
        mean_ratio = loss_ratios.mean()
        inv_train_rate = (loss_ratios / mean_ratio) ** self.alpha
        # 目标梯度范数
        mean_grad = (self.weights * grad_norms).mean()
        target_norms = mean_grad * inv_train_rate
        # 更新权重
        self.weights *= (target_norms / (grad_norms + 1e-8))
        self.weights /= self.weights.sum() / len(self.weights)
        return self.weights
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 硬参数共享 | 高度相关的任务 | 简单高效但可能有负迁移 |
| MMoE | 任务相关性未知 | 门控机制自动学习共享模式 |
| 不确定性加权 | 多任务损失平衡 | 自动调整权重，避免手动调参 |
| ESMM | 转化率预估 | 利用 $P(\text{cvr}) = P(\text{click}) \times P(\text{cvr}|\text{click})$ 分解 |
| 渐进式训练 | 防止负迁移 | 先训练主任务，再逐步加入辅助任务 |

### Common Interview Questions
- [ ] 硬参数共享与软参数共享的区别及适用场景？
- [ ] 什么是负迁移？如何检测和缓解？
- [ ] 如何平衡多任务学习中的损失权重？
- [ ] MMoE 是如何工作的？为什么比硬共享更好？
- [ ] 设计一个多目标排序系统（CTR + CVR + 观看时长）

## Comparisons

| 维度 | 独立模型 | 硬参数共享 | MMoE | PLE |
|------|---------|----------|------|-----|
| 服务成本 | K 个模型 | 1 个模型 | 1 个模型 | 1 个模型 |
| 负迁移风险 | 无 | 高 | 低 | 最低 |
| 参数量 | K x 单模型 | 共享 + K 个头 | 专家数 x 单专家 | 更大 |
| 实现复杂度 | 简单 | 简单 | 中等 | 高 |
| 推荐使用 | 任务不相关 | 任务高度相关 | 通用 | 任务关系复杂 |

## Key Takeaways
- [ ] MTL 通过共享表示减少服务成本并提高泛化能力
- [ ] 硬参数共享简单但可能产生负迁移——MMoE/PLE 更灵活
- [ ] 损失平衡至关重要——不确定性加权或 GradNorm 自动化此过程
- [ ] 梯度冲突是 MTL 训练不稳定的主要原因——PCGrad 等方法可以缓解
- [ ] 始终监控单任务性能——如果 MTL 使某任务退化，考虑调整共享结构
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    cur = conn.cursor()

    for node_id in sorted(NODES.keys()):
        desc = NODES[node_id]
        cur.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (desc, node_id),
        )
        print(f"Updated node {node_id}, new length = {len(desc)}")

    conn.commit()

    # Verify
    print("\n=== Verification ===")
    all_pass = True
    for node_id in sorted(NODES.keys()):
        cur.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (node_id,),
        )
        length = cur.fetchone()[0]
        # Check for Chinese characters
        cur.execute(
            "SELECT description FROM framework_nodes WHERE id = ?",
            (node_id,),
        )
        text = cur.fetchone()[0]
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
        status = "PASS" if length >= 5500 and has_chinese else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"Node {node_id}: length={length}, has_chinese={has_chinese}, {status}")

    conn.close()
    print(f"\nAll passed: {all_pass}")


if __name__ == "__main__":
    main()
