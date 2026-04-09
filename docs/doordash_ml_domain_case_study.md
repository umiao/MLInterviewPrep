# DoorDash ML Domain Prep: Case Study Mock Answers + SCOPE Templates

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: Interview-Ready Case Studies, SCOPE Framework, eBay Experience Mapping, Clarifying Questions

---

## 0. SCOPE Framework Reference

每个 Case Study 遵循 **SCOPE** 结构, 确保回答完整且有条理:

| Letter | Step | Key Questions | Time Budget |
|--------|------|---------------|-------------|
| **S** | Scenario & Clarification | 业务场景是什么? 用户是谁? 核心指标? | 2-3 min |
| **C** | Components & Architecture | 系统分几个模块? 数据流如何? | 3-4 min |
| **O** | Optimization & Modeling | 用什么模型? 目标函数? 特征? | 5-7 min |
| **P** | Performance & Evaluation | 离线/在线指标? A/B test 设计? | 3-4 min |
| **E** | Extension & Edge Cases | 冷启动? 扩展到新品类? 公平性? | 2-3 min |

**答题节奏**: 先花 2 min 用 S 阶段 clarify + 对齐, 然后按 C->O->P->E 展开. 每个阶段结束时 check-in: "Does this direction make sense? Should I go deeper on any part?"

---

## 1. Case Study: Restaurant Recommender (Homepage Feed)

### S -- Scenario & Clarification

**问题**: Design a restaurant recommendation system for DoorDash's homepage feed.

**Clarifying Questions**:
- Homepage feed 是给 logged-in 用户还是也包含 guest? (假设: logged-in, 有历史数据)
- 优化目标: 点击率 (CTR) vs 转化率 (CVR) vs GMV? (假设: 多目标, CTR + CVR + GMV 加权)
- 地理范围: 固定配送地址还是 GPS 实时? (假设: 用户已设定配送地址)
- Feed 长度和形式: infinite scroll 还是固定 N 个? (假设: paginated, 每页 20-30 restaurants)

**核心指标**:
- **Primary**: Order Conversion Rate (下单转化率)
- **Secondary**: CTR, GMV per session, user retention (7-day return rate)
- **Guardrail**: Restaurant coverage (避免只推头部商家), delivery satisfaction (配送体验)

### C -- Components & Architecture

```
User Request (address, time, context)
    |
    v
[Candidate Retrieval]  -- 地理过滤 + 多路召回
    |  ~500-1000 restaurants
    |-- Geo filter: 配送范围内, 当前营业中
    |-- Two-Tower: user embedding x store embedding (ANN)
    |-- Collaborative Filtering: 历史行为相似用户的偏好
    |-- Popularity: 区域热门 (时间衰减)
    |-- Personal history: 用户近期常点商家
    v
[Pre-Ranking]  -- 轻量模型粗排
    |  ~200 restaurants
    v
[Ranking]  -- 重模型精排 (DCN-v2 + MTL)
    |  ~50 restaurants
    v
[Re-Ranking]  -- 多样性 + 业务规则 + 广告混排
    |  ~20-30 restaurants (一页)
    v
Homepage Feed
```

**数据流**:
- **Feature Store**: Redis (在线特征) + DynamoDB (离线特征)
- **Model Serving**: TensorFlow Serving / Triton, GPU inference for ranking
- **Logging**: 曝光/点击/下单事件 -> Kafka -> 训练数据 pipeline

### O -- Optimization & Modeling

**Ranking Model: DCN-v2 + Multi-Task Learning**

特征组:

| Category | Features |
|----------|----------|
| User | 历史订单频率, 平均客单价, 偏好菜系 embedding, 活跃时段, DashPass 状态 |
| Store | 评分, 价格档次, 菜系 embedding, 历史订单量, 平均出餐时间 |
| Context | 当前时间 (午餐/晚餐), 天气, 星期几, 是否节假日 |
| Cross | 用户-商家历史交互次数, 用户到商家距离, 用户对该菜系的偏好强度 |
| Real-time | 商家当前等待时间, ETA 预估, 动态配送费 |

**多任务目标** (MMoE architecture):
- Task 1: $P(\text{click})$ -- 点击率预估
- Task 2: $P(\text{order} \mid \text{click})$ -- 点击后转化率
- Task 3: $E[\text{GMV} \mid \text{order}]$ -- 订单金额预估

**融合公式**:
$$\text{score} = w_1 \cdot P(\text{click}) \cdot w_2 \cdot P(\text{order} \mid \text{click}) \cdot w_3 \cdot E[\text{GMV}] + \lambda \cdot \text{diversity\_bonus}$$

权重 $w_1, w_2, w_3$ 通过 Pareto 优化或 scalarization 调节, $\lambda$ 控制多样性.

**Loss Function**:
- CTR / CVR: Binary Cross-Entropy
- GMV: Huber Loss (对异常大订单 robust)
- MTL: $L = \alpha L_{CTR} + \beta L_{CVR} + \gamma L_{GMV}$, 权重通过 uncertainty weighting 自动学习

### P -- Performance & Evaluation

**离线指标**:
- AUC-ROC for CTR/CVR tasks (target: > 0.78)
- NDCG@20 for ranking quality
- Calibration plot: predicted probability vs actual conversion rate

**在线指标 (A/B Test)**:
- Primary: Order Conversion Rate (OCR), GMV per session
- Secondary: CTR, average session duration, 7-day retention
- Guardrail: Restaurant coverage (Gini coefficient), new restaurant exposure rate

**A/B Test 设计**:
- 分流单位: user_id (非 session, 避免同一用户看到不同推荐)
- 样本量计算: 基于历史 OCR variance, MDE=2%, power=0.8, alpha=0.05
- 持续时间: 至少 2 weeks (覆盖工作日+周末 pattern)
- **Novelty effect**: 先 burn-in 3 days, 再开始统计

### E -- Extension & Edge Cases

**冷启动**:
- New user: 基于地理位置 + 时间 + popularity 推荐; 利用 signup 时收集的偏好 (cuisine preference)
- New restaurant: boosted exploration (Thompson Sampling), 利用菜系/价格 embedding 做 warm-start

**多样性保障**:
- MMR (Maximal Marginal Relevance): $\text{MMR}(d) = \lambda \cdot \text{rel}(d) - (1-\lambda) \cdot \max_{d' \in S} \text{sim}(d, d')$
- Sliding window diversity: 每 5 个结果至少 3 种不同菜系
- 商家公平性: 小商家定期 boost, 防止 Matthew effect

**Cross-Vertical 扩展**:
- 同一框架扩展到 grocery / convenience store, 但特征不同 (basket size vs single item, replenishment cycle)
- Shared user embedding across verticals, vertical-specific ranking heads

---

## 2. Case Study: Spicy Ramen Search

### S -- Scenario & Clarification

**问题**: A user searches "spicy ramen" on DoorDash. Design the search ranking system.

**Clarifying Questions**:
- 搜索范围: 商家级别还是菜品级别? (假设: 先搜菜品, 再聚合到商家展示)
- 是否需要处理 zero-result? (假设: 是, 需要 fallback 策略)
- 排序目标: relevance only 还是 relevance + conversion? (假设: 二者兼顾)

**核心指标**:
- **Primary**: Search Conversion Rate (搜索后下单率)
- **Secondary**: MRR (Mean Reciprocal Rank), Zero-result rate, Abandonment rate

### C -- Components & Architecture

```
Query: "spicy ramen"
    |
    v
[Query Understanding]
    |-- Intent: Transactional (0.8)
    |-- NER: Attribute=spicy, Dish=ramen
    |-- Expansion: "spicy ramen OR tonkotsu OR miso ramen"
    |-- Embedding: dense query vector via fine-tuned BERT
    v
[Retrieval: Hybrid]
    |-- Lexical: Elasticsearch BM25 on menu items (dish name + description)
    |-- Semantic: query embedding x item embedding ANN (HNSW)
    |-- Filter: geo range, open now, in-stock
    |  ~200 candidate dishes
    v
[Ranking: Two-Pass]
    |-- Pass 1: Lightweight model (distilled BERT cross-encoder) -> top 50
    |-- Pass 2: Full ranking model (DCN-v2 + semantic features) -> top 20
    v
[Aggregation & Re-Ranking]
    |-- Group by store: top dish per store as representative
    |-- Re-rank stores: relevance x store quality x ETA
    |-- Diversity: 不同商家类型交错 (ramen shop / Japanese / Asian fusion)
    v
Search Results Page (top 15-20 stores)
```

### O -- Optimization & Modeling

**Hybrid Retrieval Score**:
$$\text{retrieval\_score} = \alpha \cdot \text{BM25}(q, d) + (1-\alpha) \cdot \cos(\mathbf{q}, \mathbf{d})$$

$\alpha$ 通过 A/B test 调优, 通常 $\alpha \in [0.3, 0.5]$ (语义权重略高).

**Ranking Features** (beyond retrieval score):
- **Relevance**: query-item semantic similarity, exact match indicator, NER entity match
- **Quality**: store rating, dish rating, order volume
- **Freshness**: 商家当前等待时间, ETA
- **Personalization**: user's spice preference score (from order history), cuisine affinity

**Loss**: LambdaMART or Listwise softmax cross-entropy, optimizing NDCG.

**Position Debiasing**: IPW (Inverse Propensity Weighting) on click data, 因为用户倾向于点击靠前结果.

### P -- Performance & Evaluation

- **Offline**: NDCG@10, MRR, Recall@20 (semantic retrieval coverage)
- **Online**: Search CVR, Zero-result rate, Click-through position distribution
- **Human eval**: 搜索相关性标注 (1-5 scale), 每周采样 500 queries

### E -- Extension & Edge Cases

- **Zero result**: "spicy ramen" 在附近无结果 -> 放宽到 "ramen" -> 放宽到 "Japanese noodles" -> 显示 "No exact match, showing similar"
- **Typo handling**: "spicy ramne" -> spell correction -> "spicy ramen"
- **Multilingual**: 用户搜 "辣拉面" -> 跨语言 embedding 映射到 "spicy ramen"

---

## 3. Case Study: Cold-Start Merchant Recommendation

### S -- Scenario & Clarification

**问题**: A new restaurant just joined DoorDash with zero order history. How do you recommend it to users?

**Clarifying Questions**:
- 新商家有哪些初始信息? (假设: 菜单, 菜系标签, 价格范围, 地理位置, 营业时间)
- 目标: 快速积累订单 (exploration) 还是 精准推荐 (exploitation)? (假设: balance both)
- 冷启动阶段持续多久? (假设: 前 100 单或 2 周, 以先到者为准)

**核心指标**:
- **Primary**: Time-to-first-N-orders (新商家达到 N 单的速度)
- **Secondary**: New merchant retention (30-day active rate), User satisfaction on new merchant orders

### C -- Components & Architecture

```
New Merchant Onboarding
    |
    v
[Content-Based Embedding]
    |-- Menu text -> Sentence-BERT embedding
    |-- Cuisine tags + price range -> categorical embedding
    |-- Location -> geo embedding (lat/lng bucketed)
    |-- Aggregate: concatenate + projection to shared embedding space
    v
[Warm-Start in Retrieval]
    |-- Find k nearest existing merchants in embedding space
    |-- Initialize new merchant's collaborative embedding as weighted avg of neighbors
    |-- Inject into ANN index
    v
[Exploration Strategy]
    |-- Thompson Sampling: maintain Beta(alpha, beta) on CTR prior
    |-- Exploration bonus: score += exploration_weight * uncertainty
    |-- Gradually decrease exploration_weight as data accumulates
    v
[Feedback Loop]
    |-- Each impression/click/order updates:
    |   - Collaborative embedding (online learning / periodic retrain)
    |   - Thompson Sampling posterior
    |   - Quality signals (rating, reorder rate)
    |-- Exit cold-start when: orders >= 100 OR days >= 14
```

### O -- Optimization & Modeling

**Content-Based Warm-Start**:

$$\mathbf{e}_{new} = \frac{\sum_{i=1}^{k} \text{sim}(\mathbf{c}_{new}, \mathbf{c}_i) \cdot \mathbf{e}_i}{\sum_{i=1}^{k} \text{sim}(\mathbf{c}_{new}, \mathbf{c}_i)}$$

- $\mathbf{c}_{new}$: new merchant's content features
- $\mathbf{c}_i$, $\mathbf{e}_i$: neighbor's content features and learned embedding
- $k = 10$, weighted by cosine similarity

**Thompson Sampling for Exploration**:
- Prior: $\text{Beta}(1, 1)$ (uniform)
- After each impression: if order, $\alpha += 1$; else $\beta += 1$
- Sample $\theta \sim \text{Beta}(\alpha, \beta)$, use as exploration bonus
- Natural balancing: uncertain merchants get more exploration, successful ones get more exploitation

**Exploration Budget**:
- Dedicate 5-10% of homepage slots to cold-start merchants
- Ensure geographic relevance (only show to users in delivery range)
- Cap exposure per merchant per day to avoid overwhelming a new restaurant

### P -- Performance & Evaluation

- **Offline**: Leave-one-out simulation -- 假设已有商家是 "new", 用前 N 单前的数据做 warm-start, 预测后续 engagement
- **Online**: Time-to-100-orders (冷启动加速), New merchant 30-day retention, User order satisfaction (rating >= 4)
- **A/B**: Control = no exploration bonus, Treatment = Thompson Sampling exploration

### E -- Extension & Edge Cases

- **Bad merchant filter**: 如果前 20 单 rating < 3.0, 降低 exploration, 触发 quality review
- **Category imbalance**: 某区域已有 50 家 pizza 店, 新 pizza 店 exploration 权重降低; 新品类 (e.g., Ethiopian) 权重提高
- **Seasonal merchants**: food truck / pop-up, 短期营业 -> 更激进的 exploration schedule

---

## 4. Case Study: Multi-Objective Homepage Optimization

### S -- Scenario & Clarification

**问题**: DoorDash homepage needs to balance multiple objectives: user satisfaction, merchant fairness, and platform revenue. Design the multi-objective optimization.

**Clarifying Questions**:
- 有哪些具体的 conflicting objectives? (假设: User CVR, Merchant GMV fairness, Ad revenue)
- 是否有硬约束? (假设: 每个商家至少获得最低曝光率, 广告不超过 20% of slots)
- 是否需要动态调整权重? (假设: 是, 基于市场状态)

**核心指标**:
- **Primary**: Blended utility = f(User satisfaction, Merchant health, Revenue)
- **Guardrail**: No single objective degrades > 5% vs baseline

### C -- Components & Architecture

```
[Ranking Model Output]
    |  Per-item scores: P(click), P(order), E[GMV], E[ad_revenue]
    v
[Multi-Objective Fusion Layer]
    |-- Scalarization: weighted sum with learned/tuned weights
    |-- OR Pareto-optimal set -> select based on business policy
    v
[Constraint Enforcement]
    |-- Merchant fairness: min exposure guarantee per merchant tier
    |-- Ad budget: max 20% ad slots, clearly labeled
    |-- Diversity: cuisine diversity, price diversity
    v
[Slate Optimization]
    |-- Integer Linear Programming (ILP) for slot assignment
    |-- OR Greedy with constraints
    v
Final Homepage Slate
```

### O -- Optimization & Modeling

**Scalarization Approach**:

$$\text{slate\_score} = \sum_{i \in \text{slate}} \left[ w_{cvr} \cdot P_i(\text{order}) + w_{gmv} \cdot E_i[\text{GMV}] + w_{fair} \cdot \text{fairness\_bonus}_i + w_{ad} \cdot \text{ad\_rev}_i \right]$$

Subject to constraints:
- $\sum_{i} \mathbb{1}[\text{ad}_i] \leq 0.2 \cdot \lvert \text{slate} \rvert$ (ad cap)
- $\text{exposure}(m) \geq \text{min\_exposure}(m)$ for each merchant tier $m$
- $\text{cuisine\_diversity}(\text{slate}) \geq \tau$ (diversity threshold)

**Fairness Bonus**:
$$\text{fairness\_bonus}_i = \log\left(\frac{\text{expected\_exposure}_i}{\text{actual\_exposure}_i + \epsilon}\right)$$

Under-exposed merchants get positive bonus, over-exposed get negative -- drives towards proportional exposure.

**Dynamic Weight Adjustment**:
- Peak hours (午餐/晚餐): 提高 $w_{cvr}$, 降低 $w_{fair}$ (用户体验优先)
- Off-peak: 提高 $w_{fair}$, 增加 new merchant exploration (供给侧健康)
- Campaign periods: 提高 $w_{ad}$ (within guardrail constraints)

### P -- Performance & Evaluation

- **Pareto front visualization**: 画 User CVR vs Merchant Gini coefficient vs Revenue scatter plot
- **Online**: Multi-metric dashboard, 任何指标 degradation > 5% -> 自动 rollback
- **Long-term**: Merchant 90-day retention, platform GMV growth rate

### E -- Extension & Edge Cases

- **Supply crunch**: 骑手不足时, 降低长距离商家权重, 优先推近距离 (保证 ETA)
- **New vertical launch**: 杂货品类刚上线, 需要 boosted exposure 但不能压垮已有餐厅排名
- **Regulatory**: 某些城市对广告展示比例有法规要求

---

## 5. Case Study: Cross-Vertical Transfer (Restaurant -> Grocery)

### S -- Scenario & Clarification

**问题**: DoorDash is launching grocery delivery. How do you leverage existing restaurant recommendation to bootstrap the grocery vertical?

**Clarifying Questions**:
- Grocery 和 restaurant 用户重叠度多高? (假设: ~60% overlap)
- Grocery 有独立的 item catalog? (假设: 是, SKU-based, 与 restaurant menu 完全不同)
- 已有多少 grocery 订单数据? (假设: 冷启动阶段, < 10K orders)

**核心指标**:
- **Primary**: Grocery order adoption rate (首次 grocery 下单率)
- **Secondary**: Grocery basket size, Cross-vertical user LTV

### C -- Components & Architecture

```
[Existing Restaurant Data]
    |-- User preference embeddings (cuisine, price, frequency)
    |-- User behavior patterns (order timing, basket value)
    v
[Transfer Learning Bridge]
    |-- Shared user embedding: restaurant + grocery in same latent space
    |-- Feature mapping: cuisine preference -> grocery category affinity
    |   (Thai food lover -> sriracha, coconut milk, rice noodles)
    |-- LLM-based tag generation: "What grocery items would a Thai food fan buy?"
    v
[Grocery-Specific Components]
    |-- Item retrieval: grocery SKU embedding (product name + category + brand)
    |-- Basket recommendation: frequently-bought-together (association rules + GNN)
    |-- Replenishment prediction: time-series on purchase frequency per item
    v
[Unified Ranking]
    |-- Shared bottom layers (user embedding)
    |-- Vertical-specific heads: restaurant ranking vs grocery ranking
    |-- Cross-vertical signals: "users who order Thai also buy these groceries"
```

### O -- Optimization & Modeling

**Cross-Vertical User Embedding (Hierarchical)**:

```
User Features (shared)
    |
[Shared Encoder]  -- 3 layers MLP
    |
user_shared_emb (128-dim)
   /              \
[Restaurant Head]  [Grocery Head]
   |                    |
user_restaurant_emb    user_grocery_emb
(64-dim)               (64-dim)
```

Training:
- Phase 1: Train shared + restaurant head on abundant restaurant data
- Phase 2: Freeze shared, train grocery head on limited grocery data
- Phase 3: Fine-tune all with joint loss: $L = L_{restaurant} + \lambda L_{grocery}$, $\lambda$ 从 0.1 gradually increase to 1.0

**LLM-Based Feature Bridge**:

Offline batch job using LLM to generate cross-category affinity:

```
Prompt: "Given a user who frequently orders: Thai cuisine, spicy food, 
         $15-25 range. Predict top 10 grocery categories they'd buy."
Output: ["Asian sauces", "Rice", "Noodles", "Coconut milk", 
         "Hot sauce", "Fresh herbs", "Tofu", ...]
```

这些 predicted affinities 作为 grocery ranking 的额外特征, 解决 grocery cold-start.

**FAN Framework (Familiarity + Affordability + Novelty)**:

$$\text{score} = w_F \cdot \text{Familiarity}(u, i) + w_A \cdot \text{Affordability}(u, i) + w_N \cdot \text{Novelty}(u, i)$$

- Familiarity: 基于 restaurant 行为推断 (常点泰餐 -> 泰国调料 high familiarity)
- Affordability: user's average order value vs grocery item price
- Novelty: 用户未接触过但相似用户喜欢的品类

### P -- Performance & Evaluation

- **Offline**: Grocery Recall@K for transferred embeddings vs cold-start baseline
- **Online**: Grocery adoption rate, Cross-purchase rate (restaurant + grocery in same week), Grocery retention
- **A/B**: Control = grocery cold-start (no transfer), Treatment = transferred embeddings + LLM features

### E -- Extension & Edge Cases

- **Negative transfer**: 某些用户餐厅偏好不预测 grocery 行为 (e.g., 经常点外卖但从不做饭) -> 检测并降低 transfer weight
- **Privacy**: 确保 cross-vertical data usage 符合 privacy policy, user opt-out 机制
- **Basket vs single item**: Grocery 是 basket-based (一次买多个), restaurant 是 single-store -> 需要 basket-level optimization

---

## 6. Deep Dive Follow-Up Q&A (7 Themes)

### Q1: How would you handle position bias in search ranking?

**Answer**:

Position bias 是搜索排序中最常见的偏差: 用户倾向于点击排名靠前的结果, 不论其真实相关性.

**Detection**:
- 随机化实验: 对一小部分流量随机打乱 top-10 结果, 观察点击分布
- 如果 position 强烈影响 CTR 但不影响 post-click conversion, 则 position bias 显著

**Debiasing 方法**:

1. **IPW (Inverse Propensity Weighting)**:
   $$L = \sum_{(q,d)} \frac{y_{q,d}}{P(\text{examine} \mid \text{pos})} \cdot \ell(f(q,d), y_{q,d})$$
   - $P(\text{examine} \mid \text{pos})$ 从随机化实验估计
   - 高位置的点击权重降低, 低位置的点击权重提高

2. **PAL (Position-Aware Learning)**:
   - 训练时加 position feature, 推理时设 position=0 或 average
   - 让模型学会分离 "position effect" 和 "true relevance"

3. **Doubly Robust Estimator**:
   - 结合 IPW 和 direct method, 更稳定的估计
   - 即使 propensity model 或 relevance model 有一个不准, 结果仍 consistent

**DoorDash 具体应用**: 在搜索 ranking 训练中使用 PAL, 因为实现简单且不需要额外随机化实验.

### Q2: How would you design the A/B testing framework for ranking changes?

**Answer**:

**分层实验架构**:
```
Traffic
  |
[Layer 1: User Segmentation]  -- 按 user_id hash 分流
  |
[Layer 2: Feature Flags]      -- 每层独立实验
  |-- Retrieval experiment
  |-- Ranking model experiment
  |-- Re-ranking experiment
```

**关键设计决策**:

1. **分流单位**: user_id (非 session/request), 确保同一用户体验一致
2. **Sample size**: 基于 historical metric variance + MDE (minimum detectable effect)
   - For CVR: 通常需要 ~100K users/arm, 运行 2 weeks
3. **Multiple testing correction**: Bonferroni 或 FDR (Benjamini-Hochberg) for multiple metrics
4. **Guardrail metrics**: 设定 pre-registered guardrails, 任何 guardrail degradation > threshold -> auto-halt
5. **Long-term effects**: 短期 A/B 可能忽略 novelty effect 和 learning effect -> 持续 holdout group (1-5% traffic)

**Novelty Effect 处理**:
- 前 3 天不统计 (burn-in period)
- 监控 day-over-day trend: 如果 treatment effect 逐日衰减, 可能是 novelty
- 长期 holdout: 保留 1% 用户永远在 control, 每月对比 treatment 长期效果

### Q3: How would you handle real-time feature freshness vs model performance?

**Answer**:

**三层特征时效性架构**:

| Layer | Update Frequency | Examples | Storage |
|-------|-----------------|----------|---------|
| Offline | Daily batch | User long-term preferences, store historical rating | Hive -> Feature Store |
| Near-line | Minutes (streaming) | Store current wait time, area order density, last 30 min clicks | Kafka -> Flink -> Redis |
| Online | Per-request | User current location, request time, device type | Request context |

**Staleness vs Performance Tradeoff**:
- 对 ETA/等待时间: freshness 极重要, 必须 near-line 更新 (1-5 min)
- 对 user preference: daily update 足够, 偏好变化缓慢
- 对 store rating: daily update, 但突发差评需 near-line override

**Feature Freshness Monitoring**:
- Dashboard tracking feature age distribution
- Alert if critical feature (e.g., store_open_status) staleness > threshold
- Fallback: if feature unavailable, use default value + flag for model

### Q4: How do you prevent feedback loops in recommendation?

**Answer**:

Feedback loop: 推荐 -> 用户点击 -> 训练数据强化 -> 更多推荐同类 -> 用户看到越来越窄的内容.

**Detection**:
- Entropy monitoring: 推荐结果的 cuisine/store entropy 随时间下降 -> loop 信号
- Coverage tracking: 被推荐的商家占总商家数的比例, 下降 = loop

**Mitigation**:

1. **Exploration injection**: Thompson Sampling 或 epsilon-greedy, 保证 5-10% 探索性推荐
2. **Counterfactual logging**: 记录模型预测但未展示的结果, 用于 offline 评估 diversity
3. **Negative feedback**: 不仅学习 click, 也学习 "展示但未点击" (implicit negative) 和 "点击但退出" (explicit negative)
4. **Diversity constraints**: Re-ranking 阶段强制多样性 (MMR, DPP)
5. **Periodic model reset**: 每季度用 broader data (包含 exploration traffic) 重训, 防止 model drift

### Q5: How would you evaluate model fairness across merchant types?

**Answer**:

**公平性维度**:
- **Size fairness**: 大型连锁 vs 小型独立商家
- **Cuisine fairness**: 不同菜系获得的曝光/转化是否公平
- **Geographic fairness**: 不同区域商家的曝光机会

**Metrics**:
- **Gini coefficient** on impression distribution: Gini = 0 完全公平, 1 完全不公平
- **Exposure-relevance ratio**: $\frac{\text{actual\_exposure}_m}{\text{expected\_exposure}_m}$ per merchant, expected 基于 relevance score
- **Per-group CVR**: small merchant CVR vs large merchant CVR, gap 不应过大

**Interventions**:
- Min exposure guarantee per merchant tier (enforced in re-ranking)
- Fairness bonus in ranking score (如 Case Study 4 所述)
- Regular fairness audit: monthly report on exposure distribution

### Q6: How would you handle a sudden surge in demand (e.g., Super Bowl)?

**Answer**:

**挑战**: 订单量暴增 -> 骑手不足 -> ETA 飙升 -> 用户体验下降 -> 商家出餐压力.

**ML System Adaptations**:

1. **Dynamic ranking weight adjustment**:
   - 提高 ETA/配送时间的权重, 优先推荐出餐快/距离近的商家
   - 降低 exploration 权重 (此时不适合推荐未验证商家)

2. **Supply-aware retrieval**:
   - 在 retrieval 阶段过滤当前订单积压过多的商家
   - 引入 "merchant capacity" 实时特征

3. **Demand prediction**:
   - Time-series model (Prophet / DeepAR) 预测区域级需求
   - Event calendar integration (Super Bowl, holidays, bad weather)
   - 提前 2-4 小时预警, 触发骑手 incentive / merchant preparation

4. **Graceful degradation**:
   - 如果系统负载过高, 降级到 simpler model (pre-computed rankings per area)
   - Cache popular recommendations, reduce personalization granularity

### Q7: How do you decide between online learning vs periodic batch retraining?

**Answer**:

| Criterion | Online Learning | Batch Retraining |
|-----------|----------------|------------------|
| Feature drift speed | 快 (小时/天级变化) | 慢 (周/月级变化) |
| Data volume | 流式, 单条/小 batch | 大规模, 全量/增量 |
| Model complexity | 轻量 (LR, FM, shallow NN) | 复杂 (DCN-v2, MTL) |
| Risk of instability | 高 (catastrophic forgetting, adversarial data) | 低 (全量验证) |
| Latency to adapt | 分钟级 | 小时/天级 |

**DoorDash 推荐实践** (hybrid approach):
- **Core ranking model**: Daily batch retrain on past 30 days data, validated on holdout set
- **Bias/calibration layer**: Online update (hourly), lightweight LR on top of ranking scores
- **Feature store**: Near-line streaming updates for real-time features
- **Emergency override**: 如遇商家关门/灾害等突发, 规则引擎实时覆盖

**Why not full online learning for ranking?**:
- DCN-v2 / MTL 模型太复杂, online update 不稳定
- 需要全量数据验证公平性和覆盖率约束
- 但轻量 calibration layer 可以在线调整, 兼顾时效性和稳定性

---

## 7. eBay Experience -> DoorDash Mapping

### 7.1 Ranking-as-Allocation -> Multi-Objective Homepage

| eBay | DoorDash | Transfer |
|------|----------|----------|
| Buyer-seller two-sided marketplace | Consumer-merchant-Dasher three-sided | 加入骑手供给约束, 但核心 allocation 框架相同 |
| Search ranking optimizes GMV + buyer satisfaction | Homepage ranking optimizes CVR + GMV + merchant fairness | 多目标融合方法直接迁移 (scalarization, Pareto) |
| Seller boost for new listings | New merchant exploration bonus | Thompson Sampling 机制相同, 只是 domain 不同 |
| Auction-based ad ranking (GSP/VCG) | Sponsored restaurant ads mixed in feed | Ad-organic blending 策略类似 |
| Item-level ranking | Store-level ranking (聚合 item scores) | 需要额外 aggregation layer |

**面试话术**: "At eBay, I worked on ranking-as-allocation where we balanced buyer relevance with seller fairness using multi-objective optimization. The same framework directly applies to DoorDash's homepage: replace buyer with consumer, seller with merchant, and add the Dasher supply constraint as a third dimension. The scalarization approach I used -- weighted combination with dynamic weight adjustment based on market conditions -- maps to DoorDash's peak-hour vs off-peak weight shifting."

### 7.2 Diversity Ranking -> Homepage Diversity

| eBay | DoorDash | Transfer |
|------|----------|----------|
| Category diversity (electronics, clothing, ...) | Cuisine diversity (pizza, Thai, sushi, ...) | MMR/DPP 算法直接复用 |
| Price diversity (budget to luxury) | Price tier diversity ($, $$, $$$) | 相同 |
| Brand diversity | Chain vs independent diversity | 类似, 但 DoorDash 有 fairness 要求 |
| Exploration-exploitation in search | Cold-start merchant exploration | Multi-armed bandit 方法迁移 |

**面试话术**: "I implemented diversity re-ranking at eBay using MMR to ensure users see varied categories and price points. For DoorDash, the same approach works for cuisine and restaurant type diversity. The additional challenge at DoorDash is the real-time nature -- restaurant availability changes by the minute, so the diversity constraints need to be computed on a dynamic candidate set, unlike eBay where inventory changes are slower."

### 7.3 LLM Evaluation -> DoorDash Evaluation Framework

| eBay | DoorDash | Transfer |
|------|----------|----------|
| Search relevance evaluation (query-item) | Search + recommendation evaluation | 评估框架可复用 |
| Human annotation pipeline (query-item relevance) | Annotate search relevance + rec quality | 标注 pipeline 经验直接迁移 |
| LLM-as-judge for annotation quality | LLM-as-judge for menu-query relevance | Prompt engineering 技巧相同 |
| Offline metrics: NDCG, MRR | Offline metrics: NDCG, MRR, Recall@K | 指标体系一致 |
| Online metrics: CTR, purchase rate, GMV | Online metrics: CTR, CVR, GMV per session | 度量框架对齐 |

**面试话术**: "At eBay, I built an LLM-based evaluation pipeline that used GPT-4 as a judge to assess search relevance at scale, replacing expensive human annotation for iteration speed while keeping humans for ground-truth calibration. This same approach would accelerate DoorDash's search evaluation -- instead of annotating query-restaurant relevance manually, we can use LLM judges with human oversight. The key lesson from eBay was that LLM judges need careful calibration: we found they over-rate popular items, so we added explicit debiasing in the evaluation prompt."

---

## 8. Clarifying Question Templates

通用模板, 适用于任何 ML design 问题:

### 8.1 Scope & Constraints

| Template | Purpose |
|----------|---------|
| "What's the primary business metric we're optimizing?" | 明确目标, 避免盲目设计 |
| "Who are the users? Logged-in with history, or cold-start?" | 确定 personalization 深度 |
| "What's the latency budget for this component?" | 约束模型复杂度 |
| "What data do we have available? How much labeled data?" | 确定 supervised vs unsupervised 方向 |
| "Are there hard constraints (legal, fairness, privacy)?" | 确保合规性设计 |

### 8.2 System Design

| Template | Purpose |
|----------|---------|
| "What's the expected QPS? Do we need real-time or batch?" | 确定架构 (online serving vs batch pipeline) |
| "Is this a new system or improving an existing one?" | 确定是否需要考虑 backward compatibility |
| "What infrastructure is available? (GPU, feature store, etc.)" | 约束技术选型 |

### 8.3 Modeling

| Template | Purpose |
|----------|---------|
| "Is this a ranking, classification, or generation problem?" | 确定 model family |
| "What's the label definition? How is ground truth collected?" | 避免 label leakage/bias |
| "What's the training data volume? Any class imbalance?" | 确定 data augmentation / sampling 策略 |
| "How frequently does the model need to be retrained?" | 确定 training pipeline design |

### 8.4 Evaluation

| Template | Purpose |
|----------|---------|
| "What's the baseline we're comparing against?" | 确保有 meaningful comparison |
| "How do we run A/B tests? What's the traffic split capability?" | 确定实验能力 |
| "What are the guardrail metrics that must not degrade?" | 确保安全部署 |
| "How long should we run the experiment?" | 考虑 novelty effect, weekly patterns |

---

## 9. Sprint Checklist (Interview Day -3 to Day)

### Day -3: Review & Internalize
- [ ] Re-read all 6 domain prep docs (Retrieval, Ranking, Features, Search, Fundamentals, LLM Frontier)
- [ ] Practice SCOPE framework on 2 case studies from memory (no notes)
- [ ] Review eBay mapping section -- practice articulating experience transfer

### Day -2: Mock Practice
- [ ] Do 2 full mock case studies with timer (15 min each)
- [ ] Practice clarifying questions (2 min per case study)
- [ ] Record and review: check for filler words, technical precision, structure
- [ ] Review weak areas from mock (go back to specific prep doc sections)

### Day -1: Polish & Rest
- [ ] Quick scan of summary cheatsheet from each prep doc
- [ ] Practice 3-minute elevator pitch: "My eBay experience + how it maps to DoorDash"
- [ ] Prepare 2-3 questions to ask the interviewer about DoorDash's ML stack
- [ ] Good sleep, no cramming

### Day of Interview:
- [ ] 30 min before: scan SCOPE template + eBay mapping section
- [ ] Remember: Start with clarification, don't jump to solution
- [ ] Remember: Check-in with interviewer at each SCOPE transition
- [ ] Remember: Tie back to eBay experience naturally (don't force it)
- [ ] Remember: It's okay to say "Let me think about that" -- silence > wrong answer

---

## 10. Summary Cheatsheet

| Case Study | Key Architecture | Key Model | Key Metric | eBay Parallel |
|------------|-----------------|-----------|-----------|---------------|
| Restaurant Recommender | 4-stage pipeline (Retrieve->PreRank->Rank->ReRank) | DCN-v2 + MMoE (CTR+CVR+GMV) | Order CVR, GMV/session | Ranking-as-Allocation |
| Spicy Ramen Search | Hybrid retrieval (BM25 + semantic) -> 2-pass ranking | BERT cross-encoder + DCN-v2 | Search CVR, MRR | Search relevance |
| Cold-Start Merchant | Content-based warm-start + Thompson Sampling | Sentence-BERT embedding + Beta bandit | Time-to-100-orders | New listing boost |
| Multi-Objective Homepage | Scalarization + constraint enforcement | Pareto optimization + ILP | Blended utility (no > 5% degradation) | Multi-objective GMV |
| Cross-Vertical Transfer | Shared encoder + vertical-specific heads | Hierarchical embedding + LLM feature bridge | Grocery adoption rate | Cross-category rec |

| Follow-Up Theme | Key Technique | Remember |
|-----------------|---------------|----------|
| Position Bias | IPW / PAL / Doubly Robust | PAL simplest for DoorDash (no randomization needed) |
| A/B Testing | Layered experiments + guardrails | user_id split, 2-week min, burn-in 3 days |
| Feature Freshness | 3-layer (offline/near-line/online) | ETA must be near-line, preferences can be daily |
| Feedback Loops | Thompson Sampling + entropy monitoring | 5-10% exploration budget |
| Merchant Fairness | Gini coefficient + min exposure guarantee | Fairness bonus in ranking score |
| Surge Handling | Supply-aware retrieval + graceful degradation | Pre-compute fallback rankings |
| Online vs Batch | Hybrid: batch ranking + online calibration | DCN-v2 too complex for full online learning |
