# DoorDash ML Domain Prep: LLM+RecSys Frontiers + Cross-Vertical Transfer

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: LLM-Powered Recommendation, Generative RecSys, Frontier Methods, Cross-Vertical Transfer Learning

---

## 1. LLM + RecSys: Integration Paradigms

### 1.1 Four Modes of LLM in Recommendation

LLM 在推荐系统中的角色可归纳为四种范式, 从浅层到深层:

| Mode | Description | Latency Impact | DoorDash Example |
|------|-------------|---------------|------------------|
| **Feature Extractor** | LLM 生成 embedding / 文本特征, 喂给传统 ranking model | Offline, 无在线延迟 | 菜品描述 embedding via Sentence-BERT |
| **Scoring / Reranker** | LLM 直接给 candidate 打分或 rerank | 高 (LLM inference) | GPT-based rerank top-50 restaurants |
| **Agent / Conversational** | LLM 作为对话式推荐 agent, 理解复杂意图 | 极高 (multi-turn) | "I want something spicy under $15 near me" |
| **Generator** | LLM 直接生成推荐 item ID 或内容 | 高 | 生成个性化菜单描述 / 推荐理由 |

### 1.2 LLM as Feature Extractor (最实用)

**核心思路**: 用 LLM 的语义理解能力增强特征工程, 不改变在线架构.

**DoorDash 具体应用**:

1. **菜品/商家描述 Embedding**:
   - 用 Sentence-BERT / E5 / BGE 对菜品描述生成 dense embedding
   - 替代传统 TF-IDF, 捕捉语义相似性 ("spicy ramen" ~ "hot noodle soup")
   - Offline batch 计算, 存入 feature store

2. **Cross-Vertical Feature Generation**:
   - LLM 为杂货商品生成"口味标签" (savory / sweet / spicy / umami)
   - 用餐厅用户偏好预测杂货购买意图: "喜欢泰餐的用户可能买 sriracha 酱"
   - 这是 **跨品类特征迁移** 的核心

3. **Review Summarization**:
   - 将数百条评论压缩为结构化特征: {taste: 4.2, speed: 3.8, portion: 4.5}
   - 作为 ranking model 的额外输入

```
Pipeline:
  [Raw Text] -> [LLM Encoder] -> [Dense Embedding / Structured Tags]
       |                                      |
       v                                      v
  Offline Batch Job                   Feature Store (Redis/DynamoDB)
                                              |
                                              v
                                    Online Ranking Model (DCN/MTL)
```

**优点**: 不增加在线延迟, 利用 LLM 语义能力, 渐进式替换旧特征.
**缺点**: Embedding 更新频率受限于 batch pipeline (通常 daily), 无法捕捉实时信号.

### 1.3 LLM as Scoring / Reranker

**核心思路**: 利用 LLM 的 zero-shot / few-shot 能力在 reranking 阶段提升排序质量.

**方法**:

1. **Pointwise Scoring**: 给 LLM 一个 prompt + user profile + item info, 输出 relevance score
   ```
   Given user preferences: {likes spicy food, orders Thai often, budget $15-25}
   Rate this restaurant (1-10): {Thai Basil, 4.3 stars, $$ price range, 25min delivery}
   ```

2. **Listwise Reranking**: 给 LLM 一组 candidates, 要求排序
   ```
   Rank these 10 restaurants for this user, most relevant first: [...]
   ```

3. **Pairwise Comparison**: 两两比较, 更稳定但 O(n^2) 复杂度

**实际挑战**:
- **Latency**: LLM inference ~100ms+, 对 reranking 20-50 items 可能可接受
- **Cost**: 每次请求调用 LLM, API cost 显著
- **Calibration**: LLM scores 不一定 well-calibrated, 需要后处理
- **Positional Bias**: LLM 对 prompt 中 item 顺序敏感, 需要 debiasing

**DoorDash 适用场景**: 高价值用户的首页 reranking, ROI 可以覆盖 LLM cost.

### 1.4 LLM as Conversational Agent

**核心思路**: 用户通过自然语言描述需求, LLM 理解意图并推荐.

```
User: "I'm hosting a dinner party for 6 people, need something impressive
       but not too expensive. We have one vegetarian."
LLM Agent:
  1. Parse intent: group order, 6 people, budget-conscious, dietary constraint
  2. Retrieve candidates: filter vegetarian-friendly restaurants
  3. Rank by: group suitability, price/person, rating, variety
  4. Generate response: "Here are 3 options with vegetarian menus under $20/person..."
```

**DoorDash 战略价值**: 这是 search 的进化方向, 从 keyword search -> semantic search -> conversational commerce.

**技术栈**: RAG (Retrieval-Augmented Generation) + Tool Use (调用 search API, filter API)

---

## 2. DoorDash Cross-Vertical Feature Generation

### 2.1 三边市场跨品类挑战

DoorDash 的 cross-vertical (餐厅/杂货/便利店/酒类) 是面试重点:

| Challenge | Description | Solution Direction |
|-----------|-------------|-------------------|
| **Cold-Start Vertical** | 新品类 (如 pet supplies) 无行为数据 | 从已有品类迁移用户偏好 |
| **异构 Item Space** | 餐厅 menu vs 杂货 SKU, 特征空间不同 | 统一 embedding space |
| **行为信号差异** | 餐厅: 频率低单价高; 杂货: 频率高单价低 | 分离行为建模 + 共享用户表征 |
| **时间模式不同** | 餐厅: 午晚餐峰值; 杂货: 周末批量采购 | 多时间粒度建模 |

### 2.2 Hierarchical RAG for Cross-Vertical

**核心架构**: 分层检索增强生成, 打通多品类知识:

```
Layer 1: Global User Profile (shared across verticals)
  - Demographics, location, price sensitivity, dietary preferences
  |
  v
Layer 2: Vertical-Specific Retrievers
  - Restaurant Retriever: cuisine preference, order history
  - Grocery Retriever: brand preference, purchase frequency
  - Convenience Retriever: impulse buy patterns, time-of-day
  |
  v
Layer 3: Cross-Vertical Fusion
  - LLM synthesizes signals: "User orders Thai often -> retrieve Thai spices in grocery"
  - Hierarchical attention over multi-source candidates
  |
  v
Layer 4: Unified Ranking with Business Constraints
  - Multi-objective: relevance + margin + delivery capacity
```

### 2.3 Familiarity + Affordability + Novelty (FAN) Framework

DoorDash 推荐需要平衡三个维度:

- **Familiarity**: 用户熟悉的商家/菜品, 降低决策成本, 提升 conversion
- **Affordability**: 价格匹配用户预算, 避免推荐超出预期的选项
- **Novelty**: 新商家/菜品探索, 避免 filter bubble, 提升长期 engagement

**建模方式**:

1. **Familiarity Score**: 基于 repeat order rate, click history similarity
   $$F(u, i) = \alpha \cdot \text{RepeatRate}(u, i) + (1-\alpha) \cdot \text{CosineSim}(\mathbf{e}_u, \mathbf{e}_i)$$

2. **Affordability Score**: 基于用户历史 AOV (Average Order Value) 与商家价格分布
   $$A(u, i) = 1 - \frac{\max(0, \text{Price}(i) - \text{AOV}(u))}{\text{AOV}(u)}$$

3. **Novelty Score**: 基于 item 在用户历史中的出现频率的逆
   $$N(u, i) = 1 - \frac{\text{Freq}(u, i)}{\max_j \text{Freq}(u, j)}$$

**Multi-Objective Integration**:
- MTL 中增加 FAN 三个 auxiliary heads
- 或在 reranking 阶段用 Pareto-optimal selection

---

## 3. Semantic ID + Generative Recommendation

### 3.1 Semantic ID 概念

传统 RecSys 用 **atomic ID** (商家 ID = 12345), 缺乏语义信息. Semantic ID 用 **hierarchical token sequence** 表示 item:

```
Traditional:  Restaurant #12345
Semantic ID:  [Asian] -> [Thai] -> [Spicy] -> [$$] -> [4.5-star]
              Token:  t_1    t_2     t_3      t_4     t_5
```

**生成方式**:
1. **RQ-VAE (Residual Quantized VAE)**: 将 item embedding 量化为离散 token 序列
2. **Hierarchical Clustering**: 对 item feature space 递归聚类, 每层分配一个 token
3. **LLM-based Tagging**: 用 LLM 对 item 描述生成层级标签

**优势**:
- 天然支持 **cold-start**: 新 item 只要有描述, 就能生成 Semantic ID
- 支持 **generative retrieval**: 模型生成 token sequence 而不是从 candidate pool 选
- **可解释性**: Semantic ID 的每个 token 有明确含义

### 3.2 Generative Recommendation

**核心思路**: 将推荐视为 **序列生成** 问题, 不再从 candidate pool 中 retrieve, 而是直接 **生成** item 表示.

**代表工作**:

| Method | Key Idea | Architecture |
|--------|----------|-------------|
| **TIGER** (Google, 2023) | Semantic ID + Transformer, autoregressively generate item tokens | Encoder-Decoder |
| **P5** (Salesforce) | 统一推荐任务为 text-to-text (rating, retrieval, explanation) | T5-based |
| **GPT4Rec** | GPT 生成 search query, 再用传统 search 检索 | GPT + BM25 |
| **RecFormer** | 将用户行为序列格式化为 text, 用 LM 建模 | Language Model |

**TIGER Pipeline**:
```
[User Behavior Sequence]
  -> Encoder (Transformer)
  -> Decoder: Autoregressively generate Semantic ID tokens
     t_1 -> t_2 -> t_3 -> ... -> t_K
  -> Map Semantic ID back to item
```

### 3.3 DoorDash Semantic ID 应用

**设计思考**: DoorDash 的 Semantic ID 可以编码:
- Level 1: Vertical (Restaurant / Grocery / Convenience)
- Level 2: Cuisine/Category (Thai / Chinese / Mexican / Beverages / Snacks)
- Level 3: Price Tier (`$` / `$$` / `$$$` / `$$$$`)
- Level 4: Quality Cluster (based on rating + repeat rate)
- Level 5: Fine-grained feature (delivery speed, portion size)

**好处**:
1. 新商家入驻时, 无需等 behavioral data, 直接从 metadata 生成 Semantic ID
2. Cross-vertical retrieval: 生成的 token 序列可以跨品类 (Thai restaurant -> Thai grocery)
3. 可解释推荐: "We recommend this because [Thai][Spicy][$$][High-Rating]"

---

## 4. Frontier Methods in RecSys

### 4.1 Diffusion Models for Recommendation

**核心思路**: 将推荐视为从 noise 中恢复用户偏好分布的过程.

**DiffRec / DreamRec**:
- Forward process: 给用户-物品交互矩阵加 noise
- Reverse process: 学习去噪, 恢复用户真实偏好

```
Forward:  User preference x_0 -> x_1 -> ... -> x_T (pure noise)
Reverse:  x_T -> x_{T-1} -> ... -> x_0 (recovered preference)
```

**优势**:
- 天然建模 **不确定性**: 输出是分布, 不是点估计
- 多样性: 每次 sampling 可以得到不同推荐列表
- 对 sparse data 更鲁棒: noise schedule 隐式做了 data augmentation

**劣势与挑战**:
- Inference 慢 (多步 denoising), 不适合在线 real-time
- 目前主要用于 **offline candidate generation** 或 **reranking diversity**

**DoorDash 潜在应用**: 用 diffusion model 生成多样化的首页 slate, 替代 deterministic MMR/DPP.

### 4.2 Multi-Modal Recommendation (CLIP-based)

**核心思路**: 利用视觉+文本多模态表征增强推荐.

**CLIP for RecSys**:
```
[Food Photo] -> CLIP Image Encoder -> visual embedding v_i
[Menu Text]  -> CLIP Text Encoder  -> text embedding  t_i
                                         |
                                         v
                              Fused embedding: f_i = MLP(concat(v_i, t_i))
                                         |
                                         v
                              Standard Ranking Pipeline (DCN/MTL)
```

**DoorDash 高价值场景**:

1. **Visual Search**: 用户拍照或上传图片 -> 推荐视觉相似的菜品
   - "I want something that looks like this" -> CLIP similarity search

2. **Menu Photo Quality Signal**: 有吸引力的菜品图片 -> 更高 CTR
   - 用 CLIP aesthetic score 作为 ranking feature

3. **Cross-Modal Retrieval**: 用文本 query 检索图片, 或反之
   - "colorful salad bowl" -> retrieve restaurants with matching food photos

4. **Cold-Start Mitigation**: 新商家无行为数据, 但有菜品图片 + 描述
   - CLIP embedding 提供 day-1 representation

**技术选型**:
- **OpenCLIP / SigLIP**: 开源, 可 fine-tune on food domain
- **Fine-tuning**: 在 DoorDash food image-text pairs 上 contrastive learning
- **Serving**: Offline batch compute embeddings, 存入 vector store (FAISS/Milvus)

### 4.3 Causal Inference for RecSys

**核心问题**: 观测数据中的 confounders 导致推荐模型学到 spurious correlations.

**经典案例**: 热门商家被推荐更多 -> 获得更多点击 -> 模型认为它们更好 -> 推荐更多 = **popularity bias feedback loop**.

**方法体系**:

| Method | Idea | Application |
|--------|------|-------------|
| **IPS (Inverse Propensity Scoring)** | 对过度曝光的 item 降权 | Unbiased ranking learning |
| **Doubly Robust** | IPS + 直接估计的组合, 更稳定 | Offline evaluation |
| **Causal Embedding** | 将 confounders 分离出 embedding | Debiased representation |
| **Backdoor/Frontdoor Adjustment** | 因果图上的 do-calculus | Treatment effect estimation |
| **Instrumental Variable** | 用外生变量打破 confounding | Price sensitivity estimation |

**DoorDash 具体应用**:

1. **Position Bias Correction**: 列表位置影响 CTR, 用 position 作为 instrument variable
   $$P(\text{click} \mid \text{item}, \text{position}) \neq P(\text{click} \mid \text{item})$$
   - 训练时加入 position feature, 预测时 counterfactual: 设 position = 1

2. **Promotion Effect Estimation**: 优惠券/折扣对 conversion 的 **真实因果效应**
   - Naive: 有优惠 -> conversion 更高 (但本身可能就是高意向用户)
   - Causal: 用 propensity score matching 或 RCT 估计 ATE

3. **Delivery Time Confounding**: 配送时间短 -> CTR 高, 但短 ETA 的往往是近距离热门商家
   - 需要 deconfound distance 和 popularity

### 4.4 RL for Slate Optimization

**核心问题**: 传统 ranking 是 item-level scoring, 但推荐 **列表 (slate)** 的价值不是 item 价值之和.

**为什么需要 RL**:
- **Item 间交互**: 同类商家放一起可能导致选择困难; 多样化 slate 更好
- **长期价值**: 推荐新商家短期 CTR 低, 但长期提升用户 retention
- **Sequential Decision**: 用户多次刷新/翻页, 每次推荐影响后续行为

**方法**:

1. **Contextual Bandits (简化版 RL)**:
   - State: user context + 已展示 items
   - Action: 选择下一个 item 放入 slate
   - Reward: click / order / GMV
   - 适合 exploration vs exploitation (新商家探索)

2. **Full RL (MDP formulation)**:
   - State: user session history
   - Action: 整个 slate (combinatorial action space)
   - Reward: session-level GMV + user return rate
   - 算法: REINFORCE, PPO, Off-policy (CQL, BCQ)

3. **SlateQ / Combinatorial RL**:
   - 专门处理 slate-level action 的 Q-learning
   - Decompose slate value 为 item-level Q-values + interaction terms

**DoorDash 适用场景**:
- 首页 slate optimization: 平衡 conversion + diversity + exploration
- 新商家 cold-start: RL agent 决定 exploration budget
- 长期 user LTV optimization: 不只优化当次订单, 而是 30-day retention

---

## 5. Prompt-Based Recommendation

### 5.1 Recommendation as Language Task

**核心思路**: 将推荐系统的各种任务统一为 prompt-based language generation.

**Unified Prompt Framework (P5-style)**:

```
Task 1 - Rating Prediction:
  "User {user_id} has rated {item_1}: 4, {item_2}: 5, {item_3}: 2.
   Predict the rating for {item_4}."
  -> Model output: "4"

Task 2 - Sequential Recommendation:
  "User ordered: Thai Basil -> Chipotle -> Panda Express.
   What will they order next?"
  -> Model output: "A Chinese or Asian fusion restaurant"

Task 3 - Explanation Generation:
  "Explain why {restaurant} is recommended for {user}."
  -> Model output: "Based on your frequent Thai orders and preference for
     spicy food under $20, Thai Basil matches your taste profile."
```

### 5.2 In-Context Learning for RecSys

**核心优势**: 无需训练, 通过 prompt 中的 examples 实现 few-shot recommendation.

**DoorDash 应用**:

1. **Cold-Start 用户**: 新用户无历史, 用 few-shot 从 demographic 推荐
   ```
   Similar users in downtown SF, age 25-30, ordered:
   - User A: Ramen, Boba, Poke Bowl
   - User B: Sushi, Thai, Bubble Tea
   - User C: Korean BBQ, Ramen, Milk Tea
   New user profile: downtown SF, age 28.
   Recommend top 3 cuisines.
   ```

2. **新品类 Launch**: 用现有品类的行为 pattern 作为 in-context examples
   ```
   In the Restaurant vertical, users who like Italian also like:
   Wine, Olive Oil, Pasta, Tiramisu.
   For the new Grocery vertical, recommend grocery items for Italian food lovers.
   ```

### 5.3 LLM vs Traditional RecSys: Trade-Off Analysis

| Dimension | Traditional (DCN/MTL) | LLM-based |
|-----------|----------------------|-----------|
| **Latency** | < 50ms | 100ms - 2s |
| **Cost per request** | ~$0.001 | ~$0.01 - $0.10 |
| **Cold-start** | Poor (needs behavioral data) | Good (zero/few-shot) |
| **Scalability** | Handles millions QPS | Limited by LLM throughput |
| **Explainability** | Low (black-box scores) | High (natural language) |
| **Personalization** | High (fine-grained features) | Medium (limited context window) |
| **Real-time signals** | Excellent (streaming features) | Poor (context window is static) |
| **Domain adaptation** | Requires retraining | Prompt engineering |

**Practical Guideline**: LLM 不会 **替代** 传统 RecSys, 而是 **增强** 特定环节:
- **Offline**: LLM as feature extractor (highest ROI)
- **Near-real-time**: LLM for reranking high-value users
- **User-facing**: LLM for explanation generation, conversational search
- **Cold-start**: LLM for zero-shot scoring

---

## 6. Interview Q&A: LLM + RecSys Frontiers

### Q1: DoorDash 如何用 LLM 增强跨品类推荐?

**Answer**:
跨品类推荐的核心挑战是 **异构 item space** + **sparse cross-vertical signals**. LLM 增强的切入点:

1. **Unified Semantic Space**: 用 LLM encoder 将所有品类的 item (restaurant menu, grocery SKU, convenience store product) 映射到同一 embedding space. 例如 "Pad Thai" (restaurant) 和 "Thai Kitchen Pad Thai Noodle Kit" (grocery) 在语义空间中接近.

2. **Cross-Vertical Feature Transfer**: LLM 从 restaurant 行为数据提取用户口味偏好 (spicy, Asian, budget), 作为 grocery retrieval 的 query expansion. 这解决了新品类 cold-start.

3. **Hierarchical RAG**: 每个品类有独立 retriever, LLM 作为 orchestrator 决定从哪个品类检索多少 candidates, 并做跨品类 fusion.

**关键权衡**: LLM inference cost vs. cross-vertical GMV uplift. 建议 A/B test: 对 multi-vertical 用户开启 LLM-enhanced 推荐, 对比 GMV per session.

### Q2: Semantic ID 相比传统 embedding-based retrieval 有什么优势?

**Answer**:
三个核心优势:

1. **Generative Retrieval**: 传统方法从 ANN index 中搜索 nearest neighbors (受限于 index 中的 items); Semantic ID 可以 **生成** 不在 index 中的 item 表示 -- 这对 cold-start item 至关重要.

2. **Hierarchical Semantics**: Atomic ID "12345" 无语义; Semantic ID [Asian][Thai][Spicy][$$] 每层 token 编码不同粒度的语义. Retrieval 模型可以在 coarse level (cuisine) 先做 beam search, 再细化到 fine level (specific restaurant).

3. **Transfer Learning**: Semantic ID 的 token vocabulary 在新 domain 中可复用 (Restaurant 的 [Spicy] token 和 Grocery 的 [Spicy] token 共享语义). 传统 ID embedding 完全 domain-specific, 无法迁移.

**挑战**: Semantic ID 需要高质量的 hierarchical taxonomy, 对 DoorDash 这样的多品类平台需要跨品类统一分类体系.

### Q3: Diffusion models for RecSys 什么时候值得投入?

**Answer**:
Diffusion RecSys 目前最适合两个场景:

1. **Diversity-Critical Slate Generation**: 当业务目标要求 **高多样性** slate (如首页 feed, 不能全是同类商家), diffusion 的 stochastic sampling 天然产生多样化结果, 优于 deterministic re-ranking + MMR.

2. **Sparse / Noisy Data**: 用户行为极稀疏 (新市场, 新品类), diffusion 的 noise schedule 起到 data augmentation 作用, 比 MF/DNN 更鲁棒.

**不适合的场景**: 需要 real-time, low-latency 的 online ranking (diffusion 推理需要多步 denoising, 延迟太高).

**DoorDash 判断**: 如果首页 diversity metrics (如 intra-list diversity, category coverage) 是 OKR, 值得 prototype. 否则 ROI 不高 -- 传统 DPP/MMR 已经足够.

### Q4: RL for slate optimization vs greedy item-level ranking 差多少?

**Answer**:
理论上 RL-based slate optimization 考虑 item 间交互 + 长期价值, 应该优于 greedy ranking. 实践中:

**Gains**: 学术论文报告 2-5% NDCG improvement, 工业界 (YouTube, Netflix) 报告 0.5-2% engagement lift.

**为什么 gain 不大**:
1. Greedy ranking + post-hoc diversity (MMR/DPP) 已经 capture 了大部分 item interaction
2. RL 的 credit assignment 困难: 用户 30 天后 return 是哪个 slate 的功劳?
3. Off-policy evaluation 不准: simulated environment 和真实用户差距大

**DoorDash 建议**:
- **Start with contextual bandits** (Thompson Sampling) for exploration: 新商家探索, 实现简单, gain 最直接
- **Avoid full RL** unless you have: (a) reliable offline simulator, (b) clear long-term metric, (c) engineering team to maintain RL infra
- **Quick win**: 用 RL 只做 exploration budget allocation (决定展示多少比例新商家), 不做全 slate optimization

### Q5: 如何评估 LLM-enhanced RecSys 的 ROI?

**Answer**:
LLM RecSys 的 ROI 评估需要分层:

**Layer 1 - Offline Metrics** (快速迭代):
- Feature quality: 用 LLM embedding 替换旧 embedding, 对比 AUC/NDCG lift
- Recommendation quality: 用 LLM reranker 对比 baseline, 测 NDCG@K

**Layer 2 - Online A/B Test** (真实 impact):
- Primary: CTR, Conversion Rate, GMV per session
- Secondary: diversity metrics, cold-start item coverage
- Cost: LLM API cost per request, incremental infra cost

**Layer 3 - Long-term** (3-6 month):
- User retention: LLM-enhanced group 的 30-day retention
- Cross-vertical adoption: LLM cross-vertical 推荐是否促进 grocery adoption
- Cold-start acceleration: 新商家从 0 单到 50 单的时间

**ROI Formula**:
$$\text{ROI} = \frac{\Delta \text{GMV} \times \text{Take Rate} - \text{LLM Infra Cost}}{\text{LLM Infra Cost}}$$

**Rule of Thumb**: 如果 LLM feature extraction 带来 0.5% GMV lift, 对 DoorDash 量级 (~$60B+ GOV) 约 $300M 增量, 远超 infra cost. 但 LLM reranking 的 cost-per-request 更高, ROI 取决于 target 用户群大小.

### Q6: 如何在 latency budget 内部署 LLM-enhanced retrieval?

**Answer**:
关键是 **分离 offline 和 online**:

1. **Offline (无延迟约束)**:
   - LLM 生成 item embeddings (daily batch)
   - LLM 生成 Semantic IDs (item catalog 更新时)
   - LLM 生成 cross-vertical features (daily)

2. **Nearline (秒级延迟)**:
   - LLM 生成用户 session summary (per session, cached)
   - LLM 更新用户 preference profile (event-triggered)

3. **Online (毫秒级)**:
   - 仅用 pre-computed embeddings, 走传统 ANN retrieval
   - Ranking 用 DCN/MTL + LLM features (feature store lookup)
   - LLM reranking 只用于 top-N (如 top-20), 用 speculative decoding 或 distilled small model

4. **Distillation**:
   - 用 LLM 的 reranking 结果作为 teacher signal
   - 蒸馏到 lightweight model (BERT-small / MLP) 部署在线
   - 保留 80%+ 的 LLM quality, latency 降到 < 10ms

```
Deployment Architecture:
  Offline:  LLM -> Feature Store (embeddings, Semantic IDs, tags)
  Online:   User Request -> ANN Retrieval (< 10ms)
                         -> DCN Ranking with LLM features (< 50ms)
                         -> Distilled Reranker (< 10ms)
                         -> Business Rules (< 5ms)
            Total: < 75ms
```

### Q7: eBay 经验如何映射到 DoorDash LLM+RecSys?

**Answer**:

| eBay Experience | DoorDash Mapping |
|----------------|-----------------|
| **Ranking-as-Allocation** (multi-objective auction ranking) | DoorDash Multi-Objective Ranking: conversion vs margin vs delivery capacity. eBay 的 auction allocation = DoorDash 的 merchant allocation under supply constraints |
| **Diversity Ranking** (category diversification in search results) | DoorDash Slate Diversity: 首页不能全是 pizza, 需要 cuisine diversity. 方法相同: DPP/MMR + business rules |
| **LLM Evaluation** (A/B testing LLM-powered features) | DoorDash LLM ROI Evaluation: 同样面临 "LLM 提升质量但增加 cost" 的 trade-off. eBay 的 evaluation framework 直接适用 |
| **Seller Cold-Start** (new seller with no sales history) | DoorDash Merchant Cold-Start: 新商家入驻, 无订单数据. eBay 用 listing content features -> DoorDash 用 menu content + LLM embedding |
| **Cross-Category Recommendation** (electronics buyer -> accessories) | DoorDash Cross-Vertical: restaurant lover -> grocery suggestions. eBay 的 category affinity graph -> DoorDash 的 vertical affinity model |

**Key Transfer**: eBay 大规模 marketplace 的 **allocation + diversity + cold-start** 三件套在 DoorDash 三边市场完全适用, 只是从 **goods marketplace** 变成 **local commerce marketplace**, 增加了地理和实时供给约束.

---

## 7. Summary Cheatsheet

| Topic | Key Takeaway | DoorDash Relevance |
|-------|-------------|-------------------|
| LLM as Feature Extractor | Offline batch, 无在线延迟, ROI 最高 | 菜品 embedding, cross-vertical features, review summarization |
| LLM as Reranker | High quality but high cost/latency | 高价值用户 reranking, personalized explanation |
| Conversational Rec | Search 的进化方向 | Complex intent understanding, group orders |
| Cross-Vertical Transfer | LLM 打通异构 item spaces | Restaurant -> Grocery 偏好迁移 |
| Semantic ID | Hierarchical token representation | Cold-start, generative retrieval, 可解释性 |
| Generative RecSys | TIGER/P5, 生成式推荐 | 替代传统 ANN retrieval, 统一多任务 |
| Diffusion RecSys | Stochastic diverse generation | 首页 slate diversity |
| Multi-Modal (CLIP) | Visual + text joint embedding | Food photo search, quality signal |
| Causal Inference | Debiased recommendation | Position bias, promotion effect, popularity loop |
| RL Slate Optimization | Long-term + item interaction | Exploration, 新商家 cold-start budget |
| Prompt-Based Rec | Unified text-to-text formulation | Cold-start, explanation, multi-task |
| LLM Deployment | Offline > Nearline > Distilled Online | 分层部署, latency budget 管理 |
