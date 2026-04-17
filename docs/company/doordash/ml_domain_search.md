# DoorDash ML Domain Prep: Search + Semantic Matching + Bias/Debiasing

> DoorDash ML Domain Knowledge Interview Prep
> Interviewer: Ajaykrishna Karthikeyan | Date: 2026-04-14
> Focus: Query Understanding, Semantic Matching, Search Evolution, Bias/Debiasing, Exploration, Diversity

---

## 1. Query Understanding

### 1.1 Intent Classification

用户搜索意图分类是 search pipeline 的第一步, 决定后续处理策略:

| Intent Type | Description | DoorDash Example |
|-------------|-------------|------------------|
| Navigational | 用户知道想要什么, 搜索特定商家/品牌 | "McDonald's", "Chipotle near me" |
| Informational | 探索性搜索, 浏览品类 | "healthy lunch", "cheap eats" |
| Transactional | 明确购买意图, 搜索具体商品 | "pepperoni pizza", "bubble tea" |

**模型选择**:
- **轻量级**: Logistic Regression / Gradient Boosted Trees on query features (query length, token overlap with known entities, historical CTR)
- **深度模型**: Fine-tuned BERT classifier, 输入 query + user context, 输出 intent probability distribution
- **Multi-label**: 一个 query 可能同时有多种意图 (e.g., "Starbucks coffee" = navigational + transactional)

### 1.2 Query Rewriting

将用户原始 query 转换为更有效的检索 query:

**Spell Correction**:
- Edit distance (Levenshtein) + language model scoring
- Noisy channel model: $P(correction \mid query) \propto P(query \mid correction) \cdot P(correction)$
- DoorDash 特殊: 菜品名拼写变体多 (e.g., "pho" vs "foh", "gyro" vs "gyros")

**Query Expansion**:
- 同义词扩展: "burger" -> "burger OR hamburger OR cheeseburger"
- 上下文扩展: 基于用户历史行为, "pizza" 对于常点素食的用户 -> "pizza OR vegetarian pizza"
- Embedding-based expansion: 找到 query embedding 最近邻的 terms

**Query Relaxation**:
- 当精确匹配结果不足时, 逐步放宽约束
- e.g., "organic vegan sushi near downtown" -> "vegan sushi near downtown" -> "sushi near downtown"

### 1.3 Named Entity Recognition (NER)

从 query 中提取结构化实体:

```
Query: "spicy chicken from Popeyes under $15"
    |
NER Output:
    Cuisine: chicken
    Attribute: spicy
    Store: Popeyes
    Price Constraint: < $15
```

**模型**: BiLSTM-CRF 或 fine-tuned BERT + CRF head
- B-I-O tagging scheme
- DoorDash 实体类型: Store, Cuisine, Dish, Attribute (spicy/healthy/cheap), Dietary (vegan/gluten-free)

### 1.4 Query Understanding Pipeline

```
User Query: "cheap spicy ramen"
    |
    v
[Spell Correction] -> "cheap spicy ramen" (no change)
    |
    v
[Intent Classification] -> Informational (0.7), Transactional (0.3)
    |
    v
[NER] -> Attribute: cheap, Attribute: spicy, Dish: ramen
    |
    v
[Query Expansion] -> "cheap spicy ramen OR tonkotsu OR miso ramen"
    |
    v
[Query Embedding] -> dense vector for semantic retrieval
    |
    v
Retrieval Stage (BM25 + ANN)
```

---

## 2. Semantic Matching Models

### 2.1 Evolution Overview

```
TF-IDF + BM25 (Term Matching)
    |
DSSM (2013, Microsoft) -- Dual Encoder
    |
ARC-I / ARC-II (2014) -- CNN-based
    |
DRMM / KNRM (2016-17) -- Kernel-based
    |
ColBERT (2020) -- Late Interaction
    |
Cross-Encoder BERT (Full Interaction)
```

### 2.2 BM25 (Baseline)

经典 term-matching 模型, 仍是现代搜索系统的重要 baseline:

$$\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{\mid d \mid}{\text{avgdl}})}$$

- $f(t, d)$: term frequency in document $d$
- $\text{IDF}(t)$: inverse document frequency
- $k_1 \approx 1.2$, $b \approx 0.75$: 调节参数
- **优点**: 无需训练, 可解释, 对精确匹配效果好
- **缺点**: vocabulary mismatch (同义词问题), 无语义理解

### 2.3 DSSM (Deep Structured Semantic Model)

**架构**: Dual-Tower / Bi-Encoder

```
Query                    Document
  |                         |
[Word Hashing]          [Word Hashing]
  |                         |
[FC + tanh]             [FC + tanh]
  |                         |
[FC + tanh]             [FC + tanh]
  |                         |
q_vec (128d)            d_vec (128d)
  \                       /
   \                     /
    cosine_similarity(q, d)
```

$$P(d \mid q) = \frac{\exp(\gamma \cdot \cos(q, d))}{\sum_{d' \in D} \exp(\gamma \cdot \cos(q, d'))}$$

- **Word Hashing**: character n-gram hashing 解决 OOV 问题
- **训练**: click-through data, positive = clicked doc, negative = random + hard negatives
- **优点**: query 和 document 独立编码, document embedding 可离线计算 + ANN 索引, 毫秒级检索
- **缺点**: 无 query-document token-level interaction, 语义匹配能力有限

**DoorDash 应用**: Store/item embedding 离线计算, 存入 FAISS/ScaNN 索引, 在线 query embedding 做 ANN 检索

### 2.4 ColBERT (Contextualized Late Interaction over BERT)

**核心创新**: Late Interaction -- query 和 document 各自独立编码, 但保留 token-level representation, 最后做 token-level interaction:

```
Query tokens: [q1, q2, ..., qn]    (each is a BERT output vector)
Doc tokens:   [d1, d2, ..., dm]    (each is a BERT output vector)

Score = sum_i max_j (qi . dj)      (MaxSim operation)
```

$$S(q, d) = \sum_{i=1}^{n} \max_{j=1}^{m} q_i^T d_j$$

**与 DSSM 对比**:
| Aspect | DSSM | ColBERT |
|--------|------|---------|
| Encoding | Single vector per query/doc | Token-level vectors |
| Interaction | Cosine of two vectors | MaxSim over all token pairs |
| Expressiveness | Low (bottleneck) | High (fine-grained matching) |
| Index Size | Small (one vector per doc) | Large (all token vectors) |
| Latency | Very fast | Fast (with precomputed doc embeddings) |

**优点**: 比 DSSM 更精确 (token-level matching), 比 cross-encoder 更快 (doc embeddings 可预计算)
**缺点**: 索引存储大 (每个 doc token 一个向量), 需要压缩技术 (e.g., quantization)

### 2.5 Cross-Encoder BERT

**架构**: 将 query 和 document 拼接后输入单个 BERT:

```
Input: [CLS] query tokens [SEP] document tokens [SEP]
    |
  BERT (full self-attention across q and d)
    |
[CLS] output -> FC -> relevance score
```

$$S(q, d) = W^T \cdot \text{BERT}_{[CLS]}([q; d]) + b$$

- **优点**: 最强的语义匹配能力, query-document full interaction via self-attention
- **缺点**: 不能预计算 document embedding (每个 q-d pair 都要过 BERT), 推理慢, 只能用在 reranking stage

**实际应用位置**: Retrieval (DSSM/BM25) -> Pre-Ranking (ColBERT) -> Ranking (Cross-Encoder or DCN/DeepFM)

### 2.6 Matching Model Selection for DoorDash

```
Full Store/Item Pool (~100K in a city)
    |
[BM25 + DSSM Dual Tower]  -- Retrieval, < 10ms
    |  ~500 candidates
    v
[ColBERT-style Late Interaction]  -- Pre-Ranking (optional)
    |  ~100 candidates
    v
[Cross-Encoder / DCN-v2]  -- Ranking, < 50ms
    |  ~20 results
    v
[Re-Ranking: diversity + bias correction]
    |
    v
Final Results
```

---

## 3. DoorDash Search System Evolution

### 3.1 Phase 1: LR + Elasticsearch

早期搜索系统:
- **Retrieval**: Elasticsearch (BM25-based), 按 store name / menu item name 匹配
- **Ranking**: Logistic Regression on hand-crafted features
  - Query-store relevance (token overlap, edit distance)
  - Store popularity (order count, rating)
  - Distance, ETA, delivery fee
  - 用户历史 (是否点过该商家)

**局限**:
- 依赖精确文本匹配, "Italian food" 搜不到 "pasta" 或 "pizza"
- 手动特征工程瓶颈, 无法捕获复杂交互
- 冷启动: 新商家/新菜品没有足够特征

### 3.2 Phase 2: DNN-based Search

**Retrieval 升级**:
- Dual-tower embedding model (类 DSSM)
- Query encoder + Store/Item encoder -> ANN 索引 (FAISS/ScaNN)
- 同时保留 BM25 做 fallback (term matching 仍然重要)

**Ranking 升级**:
- LR -> Wide & Deep -> DCN-v2
- 引入 embedding features: query embedding, store embedding, user embedding
- Multi-task learning: CTR + CVR + ETA prediction (参见 ranking doc)

**Query Understanding 升级**:
- 增加 spell correction, query expansion
- NER 识别菜系/菜品/dietary attributes
- Intent classification 决定检索策略

### 3.3 Phase 3: Unified Search + Cross-Vertical

DoorDash 从纯餐厅扩展到杂货/便利店/酒类后:

- **Cross-vertical retrieval**: 一个 query 可能跨品类 ("ice cream" -> 餐厅甜点 + 杂货冰淇淋)
- **Vertical-aware ranking**: 不同品类的 relevance signal 不同 (餐厅看评分, 杂货看价格/品牌)
- **Blending**: 多品类结果如何混合展示 (interleaving, slot allocation)

---

## 4. Bias in Search and Recommendation

### 4.1 Position Bias

**定义**: 用户倾向于点击排名靠前的结果, 即使靠后的结果可能更相关.

$$P(\text{click} \mid q, d, k) = P(\text{examine} \mid k) \cdot P(\text{click} \mid \text{examine}, q, d)$$

其中 $k$ 是展示位置, $P(\text{examine} \mid k)$ 随 $k$ 增大而单调递减.

**结果**: 训练数据中高位置的 item 获得更多正反馈 -> 模型学到 "高位置 = 好结果" 的虚假相关 -> Rich-get-richer 循环.

**解决方法**:

#### 4.1.1 Inverse Propensity Weighting (IPW)

给每个样本加权, 抵消位置偏差:

$$\mathcal{L}_{IPW} = \sum_{(q,d,k)} \frac{1}{P(\text{examine} \mid k)} \cdot \ell(y_{q,d}, \hat{y}_{q,d})$$

- $P(\text{examine} \mid k)$: propensity score, 可通过 randomized experiments 或 EM 算法估计
- **优点**: 理论上无偏, 简单易实现
- **缺点**: 高方差 (低位置 propensity 小, 权重大), 需要 clipping

#### 4.1.2 Unbiased Learning to Rank (ULTR)

在模型中显式建模 position bias:

```
          Relevance Score
              |
         [Relevance Tower]     [Position Tower]
           /        \               |
      Query      Document       Position k
```

$$P(\text{click}) = \sigma(f_{rel}(q, d)) \cdot \sigma(f_{pos}(k))$$

- 训练时同时学习 relevance model 和 position model
- 推理时只用 relevance model (丢弃 position tower)
- **代表工作**: PAL (Position-Aware Learning), Google ULTR

#### 4.1.3 PAL (Position-Aware ListNet)

- Training: 输入包含 position feature, 模型学会分离 position effect 和 true relevance
- Serving: 将 position feature 设为 0 或固定值, 只输出 relevance-based score
- 这是 DoorDash / Uber Eats 等实际系统中最常见的做法

### 4.2 Exposure Bias

**定义**: 模型只能从展示过的 items 中学习, 从未展示的 items 缺乏反馈数据.

**后果**: 形成 closed feedback loop -- 模型偏好已知 items, 新 items 永远没机会被展示.

**解决方法**:
- **Exploration**: 随机展示部分未曾暴露的 items (详见 Section 5)
- **Counterfactual evaluation**: 使用 IPS 估计未展示 items 的潜在效果
- **Data augmentation**: 利用 item features 为未展示 items 生成 pseudo-labels

### 4.3 Selection Bias

**定义**: 用户选择性地与 items 交互 -- 只有感兴趣的才会点击, 不感兴趣的被忽略而非负反馈.

**后果**: Missing-Not-At-Random (MNAR) -- 缺失数据不是随机的, 用 "未点击 = 不相关" 作为负样本会引入偏差.

**解决方法**:
- **Explicit negative sampling**: 区分 "展示但未点击" vs "未展示"
- **Impression-based training**: 只用 impressed items 作为训练集, 未 impressed 的不作为负样本
- **Doubly robust estimator**: 结合 IPS 和 direct method, 降低方差

$$\hat{R}_{DR} = \frac{1}{n} \sum_{i} \left[ \hat{r}(x_i) + \frac{o_i}{\hat{e}(x_i)} (r_i - \hat{r}(x_i)) \right]$$

其中 $\hat{r}(x_i)$ 是 imputed reward, $\hat{e}(x_i)$ 是 propensity, $o_i$ 是 observation indicator.

### 4.4 Popularity Bias

**定义**: 热门 items 获得更多曝光和交互, 模型过度推荐热门 items, 抑制长尾 items.

**DoorDash 场景**: McDonald's, Chipotle 等连锁店获得大量订单 -> 模型更推荐它们 -> 本地小店难以获得曝光.

**解决方法**:
- **Calibrated recommendation**: 确保推荐的 popularity 分布匹配用户实际偏好分布
- **IPS reweighting**: 按 item popularity 做逆加权
- **Causal debiasing**: 用因果推断分离 "真实偏好" 和 "从众效应"
  - $P(\text{click} \mid d) = P(\text{click} \mid d, \text{do}(\text{popularity} = \text{avg}))$
- **长尾提升策略**:
  - 新商家 boost factor
  - 多样性约束 (Section 6)
  - Explore/exploit balance (Section 5)

### 4.5 Bias Summary Table

| Bias Type | Source | Impact | Primary Fix |
|-----------|--------|--------|-------------|
| Position | UI layout, user browsing | Rich-get-richer | IPW, PAL, ULTR |
| Exposure | Closed feedback loop | New items starved | Exploration, counterfactual |
| Selection | User self-selection | MNAR in training data | Impression-based training, DR |
| Popularity | Power-law distribution | Long-tail suppression | Calibration, causal debiasing |

---

## 5. Exploration vs Exploitation

### 5.1 Problem Setting

**Exploitation**: 推荐模型预测最优的 items (maximize immediate reward)
**Exploration**: 推荐不确定的 items 以收集信息 (improve future predictions)

DoorDash 场景:
- 新商家上线, 没有订单数据 -> 如果不探索, 永远没有数据
- 用户偏好变化 (e.g., 开始健身, 从快餐转向沙拉) -> 需要探索新品类
- Menu 更新, 新菜品需要曝光

### 5.2 Multi-Armed Bandit (MAB)

每次选择一个 arm (item), 观察 reward (click/order), 目标是最大化累计 reward:

#### Epsilon-Greedy
$$a_t = \begin{cases} \arg\max_a \hat{Q}(a) & \text{with probability } 1-\epsilon \\ \text{random arm} & \text{with probability } \epsilon \end{cases}$$

- 简单但粗暴, 探索不够 targeted, $\epsilon$ 难以调节

#### UCB (Upper Confidence Bound)
$$a_t = \arg\max_a \left[ \hat{Q}(a) + c \sqrt{\frac{\ln t}{N(a)}} \right]$$

- **Optimism in the face of uncertainty**: 选择 upper bound 最高的 arm
- 被选次数少的 arm -> 不确定性高 -> UCB 更大 -> 更容易被探索
- 参数 $c$ 控制 exploration 强度

#### Thompson Sampling

$$a_t = \arg\max_a \theta_a, \quad \theta_a \sim \text{Beta}(\alpha_a, \beta_a)$$

- 为每个 arm 维护 reward 的 posterior distribution (Beta for binary rewards)
- 每轮从 posterior 采样, 选择采样值最大的 arm
- **优点**: 自然平衡 exploration/exploitation, 不确定的 arm 有更高概率被采样到高值
- **实践**: DoorDash/Uber Eats 对新商家常用 Thompson Sampling

### 5.3 Contextual Bandits

标准 MAB 不考虑 context (用户/时间/位置), contextual bandit 将 context 纳入决策:

$$a_t = \arg\max_a \hat{r}(x_t, a)$$

其中 $x_t$ 是上下文特征向量.

**LinUCB**:
$$a_t = \arg\max_a \left[ \theta_a^T x_t + \alpha \sqrt{x_t^T A_a^{-1} x_t} \right]$$

- 线性 reward model + confidence interval
- 每个 arm 维护 $A_a$ (precision matrix) 和 $b_a$ (reward accumulator)
- $\theta_a = A_a^{-1} b_a$

### 5.4 Neural Bandits

用 neural network 替代 LinUCB 的线性 reward model:

- **NeuralUCB**: $a_t = \arg\max_a [f_\theta(x_t, a) + \alpha \cdot \sigma(x_t, a)]$
  - $f_\theta$: neural network estimating reward
  - $\sigma$: uncertainty estimate (e.g., dropout-based, ensemble, gradient-based)
- **NeuralTS**: Thompson Sampling variant, 从 neural network 的 posterior 采样

**实际工程**:
- 训练一个 ensemble of models, 用 ensemble disagreement 作为 uncertainty
- 或用 MC Dropout 在推理时做多次 forward pass, 用方差估计 uncertainty
- DoorDash 可以对新商家用 neural bandit, 对老商家用 exploitation-only ranking

### 5.5 Exploration in DoorDash Search

```
User Query
    |
    v
[Ranking Model] -> top-K exploitation results
    |
    v
[Exploration Injection]
    |-- Reserve N slots (e.g., 2 out of 20) for exploration
    |-- Thompson Sampling: sample from new/uncertain stores
    |-- Position: mix into middle positions (not top, not bottom)
    |
    v
[Logging] -> record impression + outcome for exploration items
    |
    v
[Model Update] -> use logged exploration data to update store quality estimates
```

**关键设计决策**:
- 探索预算 (多少 slots 给探索): 太少则新商家永远冷启动, 太多则影响用户体验
- 探索位置: 放在顶部太冒险, 放在底部没人看, 通常混入中间位置
- 何时停止探索: 当 posterior variance 足够小时切换为 exploitation

---

## 6. Diversity and Fairness

### 6.1 Why Diversity Matters

即使 ranking model 完美预测 relevance, 展示 20 个最 relevant 的结果未必是最优的:
- **用户体验**: 全是 pizza 店 -> 用户选择疲劳, 缺少发现感
- **平台生态**: 只推荐头部商家 -> 长尾商家流失 -> 平台供给多样性下降
- **DoorDash 特殊**: 三边市场需要平衡消费者满意度和商家生态健康

### 6.2 MMR (Maximal Marginal Relevance)

贪心选择: 每次选 relevance 最高且与已选结果最不相似的 item:

$$\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[ \lambda \cdot \text{Sim}(d_i, q) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]$$

- $R$: 候选集, $S$: 已选集
- $\lambda$: 控制 relevance vs diversity 的权衡
- **Sim**: cosine similarity in embedding space

**优点**: 简单直观, 可调 $\lambda$
**缺点**: 贪心不保证全局最优, $\lambda$ 需要 tuning

### 6.3 DPP (Determinantal Point Process)

概率模型, 天然鼓励选择多样化的子集:

$$P(S) \propto \det(L_S)$$

其中 $L_S$ 是 kernel matrix 的子矩阵, 元素 $L_{ij} = q_i \cdot \phi_i^T \phi_j \cdot q_j$:
- $q_i$: item $i$ 的 quality score (来自 ranking model)
- $\phi_i$: item $i$ 的 feature vector (用于衡量 diversity)
- $L_{ij}$ 大 -> $i, j$ 相似 -> $\det(L_S)$ 小 -> 同时选 $i, j$ 的概率低

**直觉**: 行列式惩罚相似 items 被同时选择, 自然产生 repulsion effect.

**工程实践**:
- 精确 DPP inference 是 $O(N^3)$, 可用 greedy MAP inference 近似
- 先用 ranking model 选 top-100, 再用 DPP re-rank 选 20 个多样化结果

### 6.4 Fairness Constraints

**商家公平性**:
- Proportional fairness: 曝光比例应与 relevance 比例成正比
- Min-exposure guarantee: 每个商家每天至少获得 X 次曝光
- Group fairness: 不同品类/价位/评分段的商家获得公平曝光

**形式化**: Constrained optimization:

$$\max \sum_i \text{relevance}(d_i) \quad \text{s.t.} \quad \text{exposure}(g) \geq \tau_g, \quad \forall g \in \text{groups}$$

**DoorDash 实践**:
- 新商家 boost: 前 N 周给予额外曝光预算
- 品类均衡: 搜索 "lunch" 不应全是 burger 店
- 距离公平: 不因距离远就完全排除 (ETA 已经作为 feature 考虑)

### 6.5 Diversity + Fairness in Re-Ranking

```
Ranking Model Output (top-50, sorted by predicted relevance)
    |
    v
[Diversity Re-Ranking]
    |-- MMR or DPP to ensure cuisine/price/store diversity
    |
    v
[Fairness Adjustment]
    |-- New merchant boost
    |-- Category balance constraints
    |-- Min-exposure enforcement
    |
    v
[Business Rules]
    |-- Sponsored results injection
    |-- DashPass partner prioritization
    |-- Seasonal/promotional boosts
    |
    v
Final Display (top-20)
```

---

## 7. Putting It All Together: DoorDash Search Architecture

```
                    User Query
                        |
                        v
             [Query Understanding]
             |-- Spell Correction
             |-- Intent Classification
             |-- NER (store/cuisine/dish/attr)
             |-- Query Expansion
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
    [BM25/ES]    [Dual-Tower ANN]  [Geo Filter]
    text match    semantic match    distance filter
         |              |              |
         +--------------+--------------+
                        |
                   [Union + Dedup]
                   ~500 candidates
                        |
                        v
              [Pre-Ranking (optional)]
              ColBERT-style or distilled model
                   ~100 candidates
                        |
                        v
                   [Ranking]
              DCN-v2 / DeepFM + MTL
              features: query, user, store, context, cross
              objectives: P(click), P(order), P(ETA < threshold)
                   ~50 candidates
                        |
                        v
                  [Re-Ranking]
              |-- Bias correction (PAL)
              |-- Diversity (MMR/DPP)
              |-- Fairness (new store boost)
              |-- Exploration (Thompson Sampling)
              |-- Business rules (ads, promos)
                        |
                        v
                  Final Results (~20)
                        |
                        v
                  [Logging Pipeline]
              impression, click, order, ETA -> feedback loop
```

---

## 8. Interview Q&A

### Q1: DSSM vs ColBERT vs Cross-Encoder -- 什么时候用哪个?

**A**: 这三个模型代表 **efficiency vs effectiveness** 的 tradeoff:

| Model | Interaction | Precompute Doc? | Latency | Accuracy | Use Stage |
|-------|------------|-----------------|---------|----------|-----------|
| DSSM | Single-vector cosine | Yes | ~1ms (ANN) | Low | Retrieval |
| ColBERT | Token-level MaxSim | Yes (token vecs) | ~5-10ms | Medium | Pre-Ranking |
| Cross-Encoder | Full self-attention | No | ~50-100ms | High | Ranking/Reranking |

**DoorDash 选择**: Retrieval 用 DSSM + BM25, Ranking 用 DCN-v2 (比 Cross-Encoder 更高效因为用了 feature-based 而非 sequence-based), Re-Ranking 阶段如果候选少 (<50) 可以用 Cross-Encoder.

### Q2: 如何处理 DoorDash 搜索中的 position bias?

**A**: 推荐 PAL (Position-Aware Learning) 方法:
1. **Training**: 将 position 作为特征输入模型, 让模型学会分离 position effect 和 true relevance
2. **Serving**: 将 position feature 设为常数 (e.g., 0), 输出 pure relevance score
3. **验证**: 通过 randomized experiments -- 随机打乱部分位置, 比较 debiased model 和 biased model 的 NDCG

**补充措施**:
- IPW 作为训练 loss 的 sample weight
- 定期做 position randomization 实验收集 unbiased data
- 监控 position-wise CTR curve 是否符合预期

### Q3: 新商家冷启动怎么解决?

**A**: 多层次方法:
1. **Feature-based**: 用 content features (菜系, 价格, 评分, 位置) 而非纯 behavior features, 新商家也有这些
2. **Exploration**: Thompson Sampling 分配探索预算, 给新商家 2-4 周的曝光窗口
3. **Transfer learning**: 同品类/同区域的已有商家 embedding 做初始化
4. **Side information**: 利用 Yelp 评分, Google Maps 数据作为冷启动 prior
5. **DoorDash Storefront**: 给新商家提供 promotional period (首单优惠, 免配送费)

### Q4: 搜索中的 explore/exploit 如何平衡?

**A**: 实际系统中的分层策略:
1. **Reserve slots**: top-20 结果中 reserve 2-3 个 slots 给 exploration items
2. **Thompson Sampling**: 对 uncertain items (低 impression 数) 从 posterior sampling
3. **Decay schedule**: 随着 item data 积累, 逐渐减少探索 (posterior 收敛)
4. **Safety net**: 设置最低质量门槛, 差评多的不再探索
5. **Evaluation**: A/B test 不同 exploration budget, 监控 long-term metrics (user retention, new store growth)

### Q5: MMR vs DPP 怎么选?

**A**:
- **MMR**: 简单高效, 适合 latency 敏感的 online serving; 但 $\lambda$ 需要 tune, 贪心可能不是全局最优
- **DPP**: 概率模型, 理论更优美, 自然编码 quality + diversity; 但计算量大 ($O(N^3)$), 工程复杂
- **实际选择**: 大多数工业系统 (包括 DoorDash) 用 **MMR 或其变体**, 因为简单可控, latency 友好. DPP 更多见于学术研究和 offline re-ranking.

### Q6: Selection bias 和 position bias 有什么区别?

**A**:
- **Position bias**: 用户因 UI 位置 (高位) 而点击, 与 item 本身 relevance 无关. 是 **观察层面** 的偏差 (examination probability).
- **Selection bias**: 用户只与自己感兴趣的 items 交互, "未点击" 不等于 "不感兴趣". 是 **数据缺失层面** 的偏差 (MNAR).

**联合处理**: Click = Examination x Relevance x User Interest
- Position bias -> Examination 偏差 -> 用 PAL / IPW 校正
- Selection bias -> 负样本定义偏差 -> 用 impression-based training / DR 估计器

### Q7: DoorDash search 和 homepage recommendation 有什么区别?

**A**:

| Dimension | Search | Homepage Recommendation |
|-----------|--------|------------------------|
| User Intent | Explicit (query-driven) | Implicit (browsing/exploring) |
| Retrieval | Query-dependent (text + semantic) | User-dependent (collaborative filtering + content-based) |
| Key Challenge | Query understanding, relevance matching | Personalization, diversity, cold start |
| Bias Focus | Position bias, query bias | Exposure bias, popularity bias |
| Evaluation | NDCG, MAP, precision@k | CTR, CVR, user retention, GMV |

### Q8: 如何评估 debiasing 的效果?

**A**:
1. **Offline**: 用 unbiased test set (来自 randomized experiments) 评估 NDCG/AUC
2. **Counterfactual evaluation**: IPS-weighted offline metrics
3. **Online A/B test**: 比较 biased vs debiased model 的:
   - Short-term: CTR, CVR, order rate
   - Long-term: new store order growth, user retention, catalog coverage
4. **Fairness metrics**: Gini coefficient of store exposure, position-wise CTR calibration

### Q9: 什么是 Doubly Robust estimator? 为什么比 IPS 好?

**A**: DR 结合了 IPS 和 direct method (imputation model):

$$\hat{R}_{DR} = \frac{1}{n} \sum_{i} \left[ \hat{r}(x_i) + \frac{o_i}{\hat{e}(x_i)} (r_i - \hat{r}(x_i)) \right]$$

- 当 propensity model $\hat{e}$ 正确时, 无偏
- 当 imputation model $\hat{r}$ 正确时, 也无偏
- **只需其中一个正确就无偏** (doubly robust property)
- 比纯 IPS 方差更低 (imputation model 提供了 baseline, IPS 只修正残差)
- 实际中两个模型都不完美, 但 DR 比单独使用任一个都更鲁棒

### Q10: 如何设计 DoorDash search 的 A/B testing framework?

**A**:
1. **Randomization unit**: User-level (不是 query-level, 避免同用户看到不同结果)
2. **Metrics hierarchy**:
   - **Guardrail**: user retention, complaint rate, order cancel rate
   - **Primary**: search CVR (query -> order), revenue per search
   - **Secondary**: CTR, impression-to-click time, result diversity
3. **Statistical framework**: Sequential testing (不等固定期限, early stopping when significant)
4. **特殊考虑**:
   - Network effects: 一个用户下单影响另一个用户的 ETA (骑手被占用)
   - Novelty effect: 新排序模型前几天可能因为新鲜感 CTR 升高, 需要 burn-in period
   - Long-term effects: 探索对新商家的价值需要更长观察期 (weeks, not days)

---

## 9. Cross-Reference to Other Prep Docs

| Topic | See Document |
|-------|-------------|
| Retrieval (Two-Tower, ANN, Hard Negatives) | `doordash_ml_domain_retrieval.md` Section 2-3 |
| Ranking Models (DCN-v2, Wide&Deep, DeepFM) | `doordash_ml_domain_ranking.md` Section 1 |
| Multi-Task Learning (MMoE, PLE) | `doordash_ml_domain_ranking.md` Section 2 |
| Feature Engineering + Embeddings | `doordash_ml_domain_features_dl.md` Section 1-2 |
| Attention Mechanisms (DIN, DIEN, BST) | `doordash_ml_domain_features_dl.md` Section 3 |

---

*Prep doc created: 2026-04-09*
*Topics: Query Understanding, Semantic Matching (DSSM/ColBERT/Cross-Encoder), DoorDash Search Evolution, Bias (Position/Exposure/Selection/Popularity), Exploration (MAB/UCB/Thompson Sampling/Contextual Bandits), Diversity (MMR/DPP), Fairness*
