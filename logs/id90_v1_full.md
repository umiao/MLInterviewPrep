# Recommendation Systems

## Overview

**Recommendation Systems** (推荐系统) 是 ML 系统设计面试中最常见的考题。推荐系统驱动着信息流、商品推荐、内容发现和匹配等核心产品功能。一个资深 MLE 必须能够设计端到端的推荐管道，涵盖 **Candidate Generation** (候选生成)、排序、重排序以及具备实时个性化能力的服务架构。

推荐系统的核心目标是：在海量物品库中，为每个用户找到最相关、最有价值的少量内容。这需要在用户兴趣建模、物品理解、实时上下文和业务目标之间进行多维度的平衡。

## Core Concepts

### System Architecture

推荐系统采用经典的多阶段漏斗架构，每个阶段逐步缩小候选集并增加模型复杂度：

```
用户请求
    |
    v
[Candidate Generation] -- 数千个物品, <50ms
    |
    v
[Ranking Model] -- 对 top-1000 评分, <100ms
    |
    v
[Re-ranking / Business Rules] -- 多样性、新鲜度、广告混排
    |
    v
[Served Results] -- top 10-50 个物品
```

### Candidate Generation Strategies

**候选生成** 是推荐系统的第一阶段，优化目标是 **Recall** (召回率)——确保好的物品不被遗漏：

| 策略 | 方法 | 优势 | 劣势 |
|------|------|------|------|
| **Collaborative Filtering** (协同过滤) | 用户-物品矩阵分解 | 捕获用户偏好模式 | 冷启动问题 |
| **Content-based** (基于内容) | 物品特征相似度 | 物品无冷启动 | 信息茧房效应 |
| **Two-tower** (双塔模型) | 独立的用户/物品编码器 | 可扩展的 ANN 服务 | 表达能力受限 |
| **Graph-based** (基于图) | 交互图上的 **Graph Neural Network** (GNN, 图神经网络) | 信号丰富 | 基础设施复杂 |

多源候选融合是工业级推荐系统的标准做法：从协同过滤、内容相似、热门趋势、用户历史等多个来源获取候选，合并后送入排序阶段。

### Matrix Factorization

**Matrix Factorization** (矩阵分解) 是协同过滤的经典方法，将用户-物品交互矩阵分解为低维向量：

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

主流架构演进：**Wide & Deep** -> **Deep & Cross Network v2** (DCN-v2, 深度交叉网络v2) -> **Deep Interest Network** (DIN, 深度兴趣网络) -> **Deep Learning Recommendation Model** (DLRM, 深度学习推荐模型)。DIN 的核心创新是引入注意力机制，对用户历史行为序列中与当前候选物品相关的行为赋予更高权重。

### Ranking Loss Functions

**Pointwise** (逐点) 损失——将每个样本独立评分：
$$
\mathcal{L} = -\sum [y_i \log \hat{y}_i + (1 - y_i) \log(1 - \hat{y}_i)]
$$

**Pairwise** (逐对) 损失——**Bayesian Personalized Ranking** (BPR, 贝叶斯个性化排序)：
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
| 探索-利用 | 冷启动/新颖性 | **Thompson Sampling** (汤普森采样) 或 epsilon-greedy 在重排序中使用 |
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


## Advanced Topics

### Feedback Loop & Data Flywheel

**Data Flywheel** (数据飞轮) 是推荐系统持续改进的核心机制：用户行为数据训练模型 -> 更好的推荐吸引更多交互 -> 更多数据进一步提升模型。但需要警惕 **Filter Bubble** (过滤气泡) 效应：系统只推荐用户已知喜好的内容，导致信息茧房。解决方案包括引入多样性约束、探索机制（如 epsilon-greedy 或 Thompson Sampling）和内容新鲜度加分。

### Real-time Recommendation Architecture

现代推荐系统采用实时架构：用户行为通过 Kafka 流入实时特征计算管道（Flink/Spark Streaming），更新用户画像和近期行为序列。推理服务在毫秒级返回个性化推荐结果。这要求模型支持 **Incremental Update** (增量更新) 或 **Online Learning** (在线学习)，以捕获用户最新兴趣变化。实时推荐架构的关键组件包括实时特征存储（Redis/DynamoDB）、在线推理服务（TF Serving/Triton）和实时日志采集管道。

### Diversity & Exploration

推荐系统的多样性控制是工程与产品的核心课题：

| 策略 | 方法 | 目标 |
|------|------|------|
| **Maximal Marginal Relevance** (MMR, 最大边际相关性) | 贪心选择兼顾相关性和多样性的结果 | 避免结果同质化 |
| **Determinantal Point Process** (DPP, 行列式点过程) | 基于核矩阵的概率多样性采样 | 保证子集多样性 |
| **Slot-based Diversity** (插槽多样性) | 在结果列表中预留固定位置给不同品类 | 保证品类覆盖 |
| **Exploration** (探索) | Bandit 算法为新内容分配曝光 | 发现新兴趣 |

### Evaluation Beyond Accuracy

推荐系统的评估需要超越准确性指标，关注用户长期价值：**Serendipity** (惊喜度) 衡量推荐结果中用户意想不到但喜欢的比例；**Coverage** (覆盖率) 衡量被推荐过的物品占总物品的比例；**Fairness** (公平性) 确保不同创作者和供给方获得合理的曝光机会。长期指标如用户留存率、生态健康度比短期 CTR 更重要，但测量周期更长。