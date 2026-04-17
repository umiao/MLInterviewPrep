# DoorDash ML Domain Prep: RecSys Architecture + Retrieval Deep Dive

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: Recommendation System Architecture & Retrieval Methods

---

## 1. Multi-Stage RecSys Pipeline

### 1.1 Pipeline Overview

现代推荐系统采用多级漏斗架构, 逐层缩小候选集同时提升排序精度:

```
全量物品池 (millions)
    |
    v
[Retrieval / Candidate Generation]  -- 毫秒级, 轻量模型
    |  ~1000 candidates
    v
[Pre-Ranking / Light Ranking]       -- 毫秒级, 中等复杂度
    |  ~200 candidates
    v
[Ranking / Scoring]                 -- 十毫秒级, 重模型 (DCN/DeepFM/MTL)
    |  ~50 candidates
    v
[Re-Ranking / Post-Processing]      -- 业务规则 + 多样性 + 公平性
    |  ~20 items
    v
展示给用户
```

### 1.2 各阶段 Latency/Precision Tradeoffs

| Stage | Candidate Scale | Latency Budget | Model Complexity | Key Metric |
|-------|----------------|----------------|------------------|------------|
| Retrieval | Millions -> ~1K | < 10ms | 低 (inner product / ANN) | Recall@K |
| Pre-Ranking | ~1K -> ~200 | < 5ms | 中 (distilled model) | 近似 NDCG |
| Ranking | ~200 -> ~50 | < 50ms | 高 (full feature cross) | NDCG / AUC |
| Re-Ranking | ~50 -> ~20 | < 10ms | 规则 + 轻量优化 | 多样性 / GMV |

**核心权衡**: Retrieval 阶段追求 **高召回率** (不能漏掉好结果), 允许精度较低; Ranking 阶段追求 **高精度** (排好序), 但只能处理少量候选. Pre-Ranking 是二者的桥梁, 用蒸馏模型在可接受延迟内粗排.

### 1.3 DoorDash Pipeline 特殊性

DoorDash 是 **三边市场** (消费者 - 商家 - 骑手), pipeline 需要额外考虑:
- **地理稀疏性**: 用户只能看到配送范围内的商家, 天然缩小候选池
- **实时性**: 商家营业状态, 预计配送时间 (ETA), 菜品售罄状态都实时变化
- **多品类 (Cross-Vertical)**: 餐厅 / 杂货 / 便利店 / 酒类, 不同品类的 retrieval 策略不同
- **供给约束**: 骑手产能限制, 需要在 retrieval 阶段就考虑 supply-demand balance

---

## 2. Two-Tower Model Deep Dive

### 2.1 Architecture

Two-Tower (双塔模型) 是工业界 retrieval 的标准范式:

```
User Tower                    Item Tower
    |                             |
[User Features]            [Item Features]
    |                             |
  MLP layers                 MLP layers
    |                             |
  user_emb (d-dim)         item_emb (d-dim)
    \                           /
     \                         /
      --- dot product / cosine ---
              |
           score = u . v
```

**核心思想**: User 和 Item 分别编码为低维向量, 用内积衡量匹配度. 两塔独立编码意味着:
- Item embeddings 可以离线预计算并建立 ANN 索引
- 在线只需计算 user embedding, 然后用 ANN 检索最近邻
- 推理延迟极低 (< 10ms for millions of items)

**User Tower 常见输入**:
- User ID embedding
- 历史行为序列 (点击/购买/收藏) -> 通过 pooling 或 attention 聚合
- 上下文特征: 时间, 地理位置, 设备类型
- 用户画像: 年龄段, 偏好标签

**Item Tower 常见输入**:
- Item ID embedding
- 类目/品牌/价格等属性
- Item 文本描述 (通过预训练 encoder 提取)
- Item 图片特征 (可选)

### 2.2 Training: Loss Functions

#### (a) Contrastive Loss (对比学习损失)

对于正样本对 $$(u, v^+)$$ 和负样本 $$(u, v^-)$$:

$$L = -\log \frac{\exp(u \cdot v^+ / \tau)}{\exp(u \cdot v^+ / \tau) + \sum_{j} \exp(u \cdot v_j^- / \tau)}$$

其中 $$\tau$$ 是温度参数. 这本质上是 softmax cross-entropy over similarity scores.

#### (b) Triplet Loss

$$L = \max(0, \; d(u, v^+) - d(u, v^-) + \text{margin})$$

要求正样本距离比负样本距离小至少一个 margin. 优点是简单直观, 缺点是只考虑一个负样本.

#### (c) Sampled Softmax Loss

$$L = -\log \frac{\exp(u \cdot v^+)}{\exp(u \cdot v^+) + \sum_{j=1}^{K} \exp(u \cdot v_j^-)}$$

Google 的 YouTube DNN 论文推广了这一做法: 从全量 item 中采样 K 个负样本计算 softmax, 避免对全量 item 计算的开销. 关键是采样分布的选择 (uniform vs popularity-based).

#### (d) Binary Cross-Entropy (BCE)

$$L = -[y \log \sigma(u \cdot v) + (1-y) \log(1 - \sigma(u \cdot v))]$$

将每个 (user, item) pair 独立地当作二分类问题. 简单但可能不如 contrastive loss 有效, 因为缺少 pair-wise comparison.

### 2.3 Negative Sampling Strategies

负样本的质量直接决定 Two-Tower 模型的效果. 常见策略:

#### (a) Random Negative Sampling
- 从全量 item 中均匀随机采样
- 优点: 简单, 计算高效
- 缺点: 太简单的负样本, 模型学不到有意义的区分

#### (b) Hard Negative Mining
- 选择与正样本相似但未被用户交互的 item
- 常见方法: 用当前模型检索 top-K 中未点击的 item 作为 hard negatives
- 优点: 提升模型区分能力
- 缺点: 可能引入 false negatives (用户没看到但其实会喜欢的 item)
- **实践 tip**: 不要全用 hard negatives, 与 random negatives 混合使用 (如 50:50)

#### (c) In-Batch Negatives
- 同一 batch 中其他样本的正样本 item 作为当前样本的负样本
- 优点: 零额外计算开销, 负样本数量 = batch_size - 1
- 缺点: 受 batch 组成偏差影响; 热门 item 出现频率高, 导致 popularity bias
- **修正方法**: Logit correction -- 减去 $$\log(p_j)$$ 其中 $$p_j$$ 是 item $$j$$ 的出现概率

#### (d) Mixed Negative Sampling (推荐实践)
- 混合使用 random + hard + in-batch negatives
- 典型比例: 50% in-batch, 30% random, 20% hard
- Hard negatives 从上一版本模型的 ANN 检索结果中挖掘 (避免 self-reinforcing bias)

### 2.4 ANN Serving (近似最近邻检索)

Two-Tower 模型的在线服务依赖 ANN 索引:

#### (a) FAISS (Facebook AI Similarity Search)
- 支持多种索引类型: Flat (精确), IVF (倒排), PQ (乘积量化), HNSW
- **IVF + PQ** 是大规模场景常用组合: 先用 IVF 粗聚类缩小搜索范围, 再用 PQ 压缩向量降低内存
- 优点: GPU 加速, 成熟稳定
- 适用: 静态索引, 批量更新

#### (b) HNSW (Hierarchical Navigable Small World)
- 基于图的 ANN 算法, 构建多层导航图
- 优点: 查询速度快, recall 高 (通常 >95% recall@100)
- 缺点: 内存占用大 (需要存储图结构), 构建时间长
- 适用: 对延迟要求极高, 数据集中等规模

#### (c) ScaNN (Scalable Nearest Neighbors, Google)
- 使用 anisotropic vector quantization, 优化了量化方向
- 核心: 传统量化同等对待所有方向的误差, ScaNN 认为平行于向量方向的误差对内积影响更大
- 优点: 在相同内存下 recall 更高
- 适用: Google 内部大规模部署

#### 选型对比

| Method | Build Time | Query Latency | Memory | Recall@100 | Dynamic Update |
|--------|-----------|---------------|--------|------------|----------------|
| FAISS-IVF-PQ | Medium | < 1ms | Low | ~90% | 需要重建 |
| HNSW | Slow | < 0.5ms | High | ~97% | 支持增量 |
| ScaNN | Medium | < 1ms | Medium | ~95% | 需要重建 |

**DoorDash 场景**: 商家数量相对有限 (城市级别), HNSW 的内存开销可接受, 且需要实时更新 (商家开关店), 因此 HNSW 是合理选择.

---

## 3. Beyond Two-Tower: Advanced Retrieval Methods

### 3.1 Multi-Interest Retrieval (MIND)

**问题**: 单一 user embedding 无法捕捉用户的多元兴趣. 一个用户可能同时喜欢日料, 火锅, 甜品.

**MIND (Multi-Interest Network with Dynamic Routing)**:
- 用 Capsule Network 的 dynamic routing 将用户行为序列分成 K 个兴趣胶囊
- 每个胶囊输出一个 interest embedding
- 检索时, K 个 interest embeddings 分别做 ANN 检索, 合并结果
- 优点: 捕捉用户多元兴趣, 提升 recall
- 缺点: K 个检索增加延迟, 需要合并去重

**变体**:
- **ComiRec**: 用 self-attention 替代 capsule routing, 效果更稳定
- **SINE**: 稀疏兴趣网络, 只激活相关的兴趣胶囊

**DoorDash 应用**: 用户可能同时有 "快速午餐" 和 "周末聚餐" 两种需求, MIND 可以同时召回快餐店和高档餐厅.

### 3.2 Graph-Based Retrieval

利用 user-item 交互图和 item-item 共现图进行召回:

#### PinSage (Pinterest)
- 在 item-item 图上做 GraphSAGE, 学习 item embeddings
- 使用 random walk 采样邻居 (而非全邻居), 适合大规模图
- 优点: 捕捉高阶协同信号 (A 买了 X 和 Y, B 买了 X, 则推荐 Y 给 B)

#### LightGCN
- 简化 GCN: 去掉 feature transformation 和 non-linear activation
- 只保留邻居聚合 (neighborhood aggregation)
- 多层聚合后取加权和作为最终 embedding
- 优点: 参数少, 训练快, 效果不输复杂 GCN

#### DoorDash 图结构
- **User-Store 图**: 用户浏览/下单商家
- **Store-Item 图**: 商家提供的菜品
- **User-Cuisine 图**: 用户偏好的菜系
- **地理邻近图**: 地理上相近的商家天然形成 cluster

### 3.3 Generative Retrieval

传统 retrieval 是 "index + search", 新范式是 "直接生成 item ID":

#### DSI (Differentiable Search Index, Google 2022)
- 将所有 document IDs 编码到 Transformer 的参数中
- 输入 query, 直接 autoregressive 生成 document ID
- 训练: (query, docid) pairs 上做 seq2seq
- **Semantic ID**: 用层次聚类将 document 映射为语义 token 序列 (而非随机 ID), 使得语义相近的 document 有相似的 ID 前缀

#### GENRE (Generative ENtity REtrieval, Meta 2021)
- 用 BART 直接生成 entity name (非数字 ID)
- 用 constrained beam search 确保生成的 name 是合法的实体
- 适用于 entity linking 和 knowledge-intensive retrieval

#### TIGER (Google 2023)
- 基于 Semantic ID 的 generative recommendation
- 用 RQ-VAE (Residual Quantized VAE) 学习 item 的层次语义 ID
- Transformer 输入用户行为序列的 semantic IDs, 生成下一个推荐 item 的 semantic ID
- 优点: 不需要 ANN 索引, 天然支持新 item (只要有 content features 就能生成 semantic ID)

#### 局限性与现实应用
- Generative retrieval 目前主要在学术界, 工业大规模部署仍少
- 延迟: autoregressive 生成比 ANN lookup 慢
- 更新: 新 item 需要重新训练或至少 re-encode semantic ID
- **面试 tip**: 提到这些前沿方法展示知识广度, 但要说明 "Two-Tower + ANN 仍是工业主流"

---

## 4. Cold-Start Embedding

### 4.1 Cold-Start 问题分类

| Type | 描述 | 挑战 |
|------|------|------|
| New User | 新注册用户, 无历史行为 | User embedding 无行为信号 |
| New Item | 新商品/新商家, 无交互数据 | Item embedding 无协同信号 |
| New Market | 新城市/新区域 | 用户和商家都缺乏数据 |

### 4.2 Cold-Start 解决方案

#### (a) Content-Based Fallback
- 新 item: 用类目, 文本描述, 图片等 content features 构建 embedding (不依赖交互)
- 新 user: 用注册信息, 地理位置, 人口统计特征构建初始 embedding
- **Two-Tower 天然支持**: side features 可以为没有 ID embedding 的 item/user 提供 non-zero 表示

#### (b) Meta-Learning (学习如何快速学习)
- **MeLU (Meta-Learned User Preference Estimator)**: 用 MAML 框架, 几次交互后快速适应新用户
- 核心: 学习一个好的 embedding 初始化, 使得少量梯度步骤就能到达好的 user-specific embedding

#### (c) Warm-Up Strategy
- 新用户: 展示 explore 性质的候选 (高多样性, 热门+冷门混合), 快速收集行为信号
- 新商家: 给予初始曝光 boost, 收集 impression + click 数据后再正常排序
- **Explore-Exploit tradeoff**: 新实体需要更多 exploration, 老实体偏 exploitation

#### (d) Cross-Domain Transfer
- 用户在其他品类 (如餐厅) 的行为可以 transfer 到新品类 (如杂货)
- DoorDash 优势: 同一平台多品类, 可以复用 user embedding

### 4.3 DoorDash Cold-Start 特殊挑战

- **新城市上线**: 商家和用户都是冷启动, 需要从其他城市 transfer 学到的模式
- **新商家入驻**: 用菜系类别, 价格区间, 地理位置等 content features 构建初始 embedding
- **季节性商家**: 某些商家不定期营业 (如冰淇淋车), 行为数据稀疏
- **Cross-Vertical Cold-Start**: 用户在餐厅品类活跃, 但在杂货品类是 "新用户"

---

## 5. DoorDash-Specific Retrieval Challenges

### 5.1 Three-Sided Marketplace Dynamics

DoorDash 不同于 Amazon/Netflix 的关键点在于三边市场:

```
消费者 (demand) <--> 商家 (supply) <--> 骑手 (delivery)
```

Retrieval 需要同时考虑:
- **消费者偏好**: 菜系, 价格, 评分
- **商家能力**: 当前是否营业, 出餐速度, 库存
- **骑手可用性**: 附近骑手数量, 预计取餐-配送时间

**实际影响**: 即使一个商家是用户的 "完美匹配", 如果 ETA 过长 (因为骑手不足), 不应该排在前面. 这在 retrieval 阶段可以通过 geo-aware filtering 初步处理, 在 ranking 阶段精确建模.

### 5.2 Geo-Sparsity

- 用户只能看到配送半径内的商家 (通常 5-10 miles)
- 不同区域的商家密度差异巨大 (downtown vs suburban)
- **影响 retrieval**: 候选池天然受限于地理范围, 有时候选本身就很少 (稀疏区域)
- **解决方案**:
  - 分区域建立 ANN 索引 (per-geohash 或 per-city)
  - 稀疏区域放宽地理过滤条件
  - 利用地理层次 (neighborhood -> city -> region) 做 fallback

### 5.3 Cross-Vertical Retrieval

DoorDash 同时提供餐厅, 杂货 (DashMart), 便利店, 酒类等:

- **挑战**: 不同品类的 item 特征空间不同 (一道菜 vs 一箱牛奶)
- **方法 1: Shared Embedding Space**: 将所有品类映射到同一向量空间, 但可能牺牲品类内精度
- **方法 2: Per-Vertical Tower**: 每个品类单独训练 Two-Tower, 最后合并结果
- **方法 3: Hierarchical Retrieval**: 先决定品类 (intent classification), 再在品类内检索
- **DoorDash 实践**: 结合 intent 理解 (用户当前想要什么品类) 和 cross-vertical signals (如用户同时加了餐和饮料)

### 5.4 Real-Time Constraints

食品外卖的实时性要求高于传统电商:
- **商家状态实时变化**: 营业/歇业, 接单暂停 (busy mode), 菜品售罄
- **ETA 动态更新**: 随骑手分布, 交通状况, 商家出餐速度变化
- **Flash Sales / Promotions**: DashPass 优惠, 限时折扣改变 item relevance
- **Retrieval 层的处理**: Pre-filter 掉不可用商家 (hard filter), 将 ETA 作为 embedding 的 context feature (soft signal)

---

## 6. Detailed Q&A

### Q1: Why use Two-Tower instead of a single tower for retrieval?

**A**: 核心原因是 **inference efficiency**. 单塔模型 (如 DSSM cross 模式) 需要对每个 (user, item) pair 做完整前向传播, 计算量是 O(N), N 是候选数 (millions). Two-Tower 将 user 和 item 独立编码, item embeddings 可以离线预计算并建 ANN 索引, 在线只需计算一次 user embedding + ANN 查询, 计算量是 O(1) + O(log N).

**Trade-off**: Two-Tower 不能建模 user-item 的交叉特征 (如 "用户 A 对品类 X 的偏好"), 因为两塔独立编码. 这是 retrieval 追求高召回的代价, 精细的交叉特征留给 ranking 阶段.

### Q2: How do you handle position bias in retrieval training data?

**A**: Retrieval 的训练数据来自用户的隐式反馈 (点击, 下单), 这些反馈受到 position bias 影响 (靠前的 item 被点击概率更高, 不一定是因为更好).

处理方法:
1. **IPW (Inverse Propensity Weighting)**: 给低位置的点击更高权重, 高位置的点击降权
2. **Position as feature**: 训练时加入 position 作为特征, serving 时设为缺失值或默认值
3. **Unbiased sampling**: 定期做 random exposure 实验, 收集无偏数据用于校准
4. **对 retrieval 的特殊影响**: Retrieval 通常用 "有无交互" 作为正负样本, position bias 会导致被曝光但未交互的 item 被错误地当作 hard negatives

### Q3: How would you evaluate retrieval model performance?

**A**: 离线和在线两个维度:

**离线指标**:
- **Recall@K**: 在返回的 top-K 中, 真正 relevant items 的比例. K 通常取 50/100/500
- **Hit Rate@K**: 至少有一个 relevant item 出现在 top-K 中的 query 比例
- **MRR (Mean Reciprocal Rank)**: 第一个 relevant item 排名倒数的均值

**在线指标** (A/B test):
- **Downstream ranking quality**: Retrieval 改进是否提升了最终推荐的 NDCG/CTR/CVR
- **Coverage**: 被推荐到的 item/store 的比例 (防止 popularity collapse)
- **Diversity**: 推荐结果中不同类别的比例

**注意**: Recall@K 高不一定带来在线提升. 如果多召回的 candidate 被 ranking 阶段全部淘汰, 则 retrieval 改进无效. 需要和 ranking 团队协同优化.

### Q4: How do you decide the number of retrieval channels?

**A**: 实际工业系统通常使用 **多路召回 (multi-channel retrieval)**, 而非单一模型:

常见通道:
- **Two-Tower**: 个性化相关性
- **Item-CF**: 协同过滤 ("看过 X 的人也看了 Y")
- **Hot/Trending**: 热门 item (保证 coverage)
- **Geo-based**: 地理位置附近 (DoorDash 强需求)
- **Graph-based**: 图上的高阶协同信号

每个通道有独立的 recall quota (如 Two-Tower 200, Item-CF 100, Hot 50). 合并后去重, 输入 pre-ranking. 通道数量和配额需要通过 A/B test 调优.

### Q5: What are the key differences between retrieval for food delivery vs e-commerce?

**A**:

| Dimension | Food Delivery (DoorDash) | E-Commerce (Amazon) |
|-----------|------------------------|---------------------|
| Time sensitivity | 极高 (30-60min delivery) | 低 (1-2 day shipping) |
| Geo constraint | 严格 (配送半径) | 无 (全国配送) |
| Inventory | 动态 (每天变化, 实时售罄) | 相对稳定 |
| Repeat purchase | 高 (每周多次点外卖) | 低 (大多一次性购买) |
| Supply constraint | 三边 (骑手产能) | 单边 (仓库库存) |
| Decision context | Meal occasion (时间, 场景) | Need-based (搜索驱动) |

Retrieval 的关键差异:
- Food delivery 需要 **实时供给过滤** (e-commerce 不需要)
- Food delivery 的 **重复购买行为** 是强信号 (e-commerce 的 repeat purchase 对不同品类差异大)
- Food delivery 的 **地理约束** 天然缩小候选池, ANN 索引可以分地理区域

### Q6: How would you handle the exploration-exploitation tradeoff in retrieval?

**A**: 在 retrieval 阶段, exploration 意味着引入用户可能不熟悉但可能喜欢的新商家/新菜系:

策略:
1. **Epsilon-Greedy in Retrieval**: 以概率 epsilon 随机替换一些 Two-Tower 召回的结果为随机 item
2. **Dedicated Exploration Channel**: 多路召回中加一路专门的 exploration 通道
3. **Uncertainty-Aware Retrieval**: 对 embedding 的不确定性建模 (如 Bayesian Two-Tower), 选择高不确定性的 item (类似 UCB)
4. **Popularity Regularization**: 在 loss function 中加入 popularity penalty, 避免模型总是推荐热门 item

DoorDash 场景: 新入驻商家需要 exploration 来收集数据; 用户在新品类 (如从餐厅扩展到杂货) 需要 exploration 来学习偏好. 但过多 exploration 会损害短期用户体验.

### Q7: How would you design retrieval for a DoorDash-like homepage?

**A**: DoorDash 首页展示多种推荐模块 (轮播, 为你推荐, 品类入口, 附近热门等), 需要 multi-slot retrieval:

1. **Intent Prediction**: 预测用户当前意图 (快速午餐 / 周末聚餐 / 杂货购物)
2. **Per-Module Retrieval**:
   - "为你推荐": Two-Tower 个性化 + 多兴趣 (MIND)
   - "附近热门": Geo-filtered + trending score
   - "再次下单": 历史订单的时间衰减排序
   - "新店推荐": Cold-start exploration channel
3. **Cross-Module Dedup**: 同一商家不应出现在多个模块中
4. **Budget Allocation**: 每个模块分配候选数配额, 根据 A/B test 调优

### Q8: Explain how in-batch negatives can introduce popularity bias and how to fix it.

**A**: 在 in-batch negative sampling 中, 一个 batch 内其他样本的正样本 item 作为当前样本的负样本. 热门 item 出现在更多正样本中, 因此也更频繁地成为负样本.

**问题**: 模型学会 "惩罚" 热门 item (因为它们总是出现在负样本中), 导致热门 item 的 embedding 被 pushed away from all users.

**修正 (Logit Correction / Sampling Correction)**:

$$\text{corrected\_logit}(u, v_j) = u \cdot v_j - \log(p_j)$$

其中 $$p_j$$ 是 item $$j$$ 被采样为负样本的概率 (正比于其出现频率). 这相当于在 softmax 中除以每个负样本的先验概率, 消除 popularity 的影响.

这一技术在 Google 的 Two-Tower 论文 (2019) 和 YouTube recommendations 中广泛使用.

### Q9: What is the difference between ANN recall and model recall, and why does it matter?

**A**: 两种不同的 "recall":

- **Model Recall**: 在精确计算 (brute-force) 下, 模型检索的 top-K 中包含 relevant items 的比例. 这衡量的是 **模型质量**.
- **ANN Recall**: ANN 索引返回的 top-K 与 brute-force top-K 的重叠比例. 这衡量的是 **索引近似质量**.

**End-to-End Recall = Model Recall x ANN Recall**

在实践中:
- ANN Recall 通常 > 90% (可以通过调整索引参数提升)
- Model Recall 是瓶颈, 取决于模型设计和训练
- 优化时要分别 debug: 如果 end-to-end recall 差, 先检查 ANN recall (用 brute-force 作为 oracle), 再检查 model recall

### Q10: How would you incrementally update embeddings for Two-Tower models?

**A**: 大规模 Two-Tower 模型不能每次全量重训:

**Item Embedding 更新**:
- 新 item: 用 trained Item Tower 做 forward pass 得到 embedding, 增量插入 ANN 索引
- 索引更新: HNSW 支持增量插入; FAISS-IVF 需要定期重建 (如每小时)

**User Embedding 更新**:
- 在线计算: 每次请求时, 用最新行为序列通过 User Tower 实时计算 (因为只需一次 forward pass)
- 或定期批量更新: 每小时/每天更新全量用户的 embedding

**模型参数更新**:
- **Full retrain**: 每天/每周用最新数据全量训练 (最常见)
- **Incremental / Continual learning**: 在旧模型基础上用新数据 fine-tune (但有 catastrophic forgetting 风险)
- **实践**: 大多数公司采用 "daily full retrain + real-time feature update" 的混合策略

---

## 7. Key Papers & References

| Topic | Paper | Key Contribution |
|-------|-------|------------------|
| Two-Tower | Sampling-Bias-Corrected Neural Modeling (Google, 2019) | In-batch negatives + logit correction |
| YouTube DNN | Deep Neural Networks for YouTube Recommendations (2016) | Sampled softmax, candidate generation |
| MIND | Multi-Interest Network with Dynamic Routing (2019) | Multi-interest user representation |
| PinSage | Graph Convolutional Neural Networks for Web-Scale Recommender Systems (2018) | Scalable GNN for retrieval |
| LightGCN | LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation (2020) | Simplified GCN |
| DSI | Transformer Memory as a Differentiable Search Index (Google, 2022) | Generative retrieval paradigm |
| TIGER | Recommender Systems with Generative Retrieval (Google, 2023) | Semantic ID + generative rec |
| GENRE | Autoregressive Entity Retrieval (Meta, 2021) | Constrained decoding for entities |
| ScaNN | Accelerating Large-Scale Inference with Anisotropic Vector Quantization (2020) | Anisotropic quantization |
| FAISS | Billion-scale similarity search with GPUs (Meta, 2017) | ANN infrastructure |
