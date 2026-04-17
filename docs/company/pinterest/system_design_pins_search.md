# Pinterest ML System Design: Pins Search Engine

> Pinterest ML System Design Interview Prep
> Scope: End-to-end Pins search — query understanding, candidate generation, ranking, serving, metrics
> Format: 45-min onsite SD loop (clarify 5m, high-level 5m, CG 10m, ranking 15m, infra+metrics 10m)

---

## 0. Clarifying Questions (前 5 分钟必问)

面试官抛出 "Design Pinterest Pins Search" 时, 不要直接画图. 先澄清:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| Scale | DAU? QPS? Pins corpus size? | 决定 ANN index 规模与分片策略. Pinterest 实际约 500M MAU, 数十亿 Pins, peak ~100K QPS |
| Latency SLO | P99 end-to-end? | 决定 CG+ranking 的时间预算 (通常 P99 < 500ms 意味 CG < 150ms, ranking < 200ms) |
| Surface | Search results page only? or also related-pins, home feed? | 明确 scope. 本设计聚焦 keyword search |
| Query type | Text-only? Image (visual search / Lens)? Both? | Lens 用 image embedding query, 架构差异大 |
| Personalization | 个性化强度? Cold-start user 占比? | 决定 user tower 复杂度, 与是否需要 popularity prior |
| Freshness | 新 Pin 多快进索引? | 决定是否需要 online index + periodic rebuild |
| Business goal | CTR? Repin? Long-term retention? | 决定 ranking loss 与 online metric |
| Constraint | Safety (NSFW/violent) filtering, dedup, locale/language | 决定 policy layer + filter stages |

**假设 (本设计默认)**:
- Text query, 英文 + 多语言, 5B Pins corpus, 100K QPS peak, P99 500ms
- 个性化中等强度 (user history 存在), 需要 cold-start fallback
- 业务目标: Repin-rate (长期 engagement proxy) + CTR

---

## 1. High-Level Architecture

```
User Query
    |
    v
[Query Understanding] -- spell correct, tokenize, intent, query embedding
    |
    v
[Candidate Generation] -- multi-source retrieval, union ~5-10K candidates
    |   +-- Inverted Index (term match)
    |   +-- Two-Tower ANN (semantic)
    |   +-- Personalized (user history similar pins)
    |   +-- Trending / Popular (cold-start fallback)
    v
[Lightweight Ranker] -- GBDT, ~5K -> 500, pruning by basic features
    |
    v
[Heavy Ranker] -- DNN multi-task, 500 -> 50
    |
    v
[Re-ranking / Blending] -- diversity, freshness, policy filter, MMR
    |
    v
Final 25 Pins -> SRP
```

**服务分层** (4 stages) 是 Pinterest/Google/Meta 搜索系统的通用模式. 每一级都在 **精度 vs 成本** 之间权衡:
- CG: 高召回, 低精度, 便宜 (embedding lookup + inverted index)
- L1 ranker: 中精度, GBDT, 数百特征, < 10ms on 5K candidates
- L2 ranker: 高精度, DNN, 数千特征 + embedding, < 100ms on 500
- Re-rank: business rules + 多样性, < 20ms

---

## 2. Query Understanding

### 2.1 Normalization + Spell Correction
- Unicode normalize, lowercase, tokenize (language-aware: 中文 jieba, 日文 MeCab, 英文 BPE/wordpiece)
- Noisy channel spell correction: $P(c \mid q) \propto P(q \mid c) \cdot P(c)$, 以 query-log n-gram 作 prior
- Pinterest 特色: 视觉/时尚/DIY 词汇拼写变体多 ("charcuterie", "boho")

### 2.2 Query Segmentation + NER
- BiLSTM-CRF 或 fine-tuned BERT 标注 query 中的 entity: `{category, brand, attribute, color, occasion}`
- 例: "minimalist scandinavian living room" -> style=minimalist, theme=scandinavian, object=living_room

### 2.3 Intent Classification
- 分类: navigational (brand name), informational (inspiration browse), transactional (shoppable product)
- 影响后续 mix: informational -> 更多 idea pins; transactional -> 更多 product pins

### 2.4 Query Embedding
- **Text encoder** (query tower): fine-tuned SBERT / DistilBERT, 输出 256-dim vector
- 训练: (query, clicked_pin) positive pairs + in-batch negatives, InfoNCE loss
- 缓存: Redis, top-1M query 命中率 > 70%, 省掉 online BERT 推理成本

---

## 3. Candidate Generation (Retrieval)

### 3.1 多源召回 (Multi-source Retrieval)

单一召回源总有盲区, Pinterest 生产系统用 **union of sources** 保召回:

| Source | Method | 解决的问题 |
|--------|--------|----------|
| **Token / Inverted Index** | Elasticsearch / Lucene, BM25 on title+description+board-name | 精确关键词匹配, 长尾 rare query |
| **Semantic ANN** | Two-tower + HNSW, query emb -> top-K pin emb | 语义相似 ("home office setup" vs "desk ideas") |
| **Personalized** | User history pins -> similar pins (item-item) | 冷启动 query 下的个性化 |
| **Trending / Popular** | 按类目/地域 top pins | Cold-start user, 流行词 |
| **Board-based** | User followed boards -> pins in those boards | 长期兴趣 |

Union 后约 5-10K candidates 进入 L1 ranker.

### 3.2 Two-Tower 模型 (Core of Semantic CG)

```
Query                          Pin
  |                             |
[text tokens]            [title, desc, image, board_name, category]
  |                             |
[Query Tower]              [Pin Tower]
  |                             |
q_emb (256-d)             p_emb (256-d)
         \                /
          \              /
         cosine / dot product
                |
             score
```

**Query Tower**: BERT-small / DistilBERT, mean-pool last layer -> 256d + L2 norm
**Pin Tower**:
- Text: title + description + board_name -> DistilBERT
- Image: pretrained ViT / CLIP-ViT-B/32 image encoder -> 512d -> project to 256d
- Categorical: category id embedding
- **Fusion**: concat + MLP -> 256d + L2 norm

**Loss**: InfoNCE (sampled softmax) with in-batch negatives + **hard negatives** (BM25 top-K but no-click)

$$ L = -\log \frac{\exp(q \cdot p^+ / \tau)}{\exp(q \cdot p^+/\tau) + \sum_{p^-} \exp(q \cdot p^-/\tau)} $$

$\tau$ temperature 通常 0.05-0.1.

**Training data**:
- Positive: (query, pin) where `action in {click, repin, close-up > 10s}`
- Hard negatives: BM25 high-score no-action pins (hard) + random (easy, in-batch)
- Scale: ~1B pairs, 1 epoch, Adam lr=1e-4, batch 4096

### 3.3 ANN Index (HNSW)

- **Why HNSW**: 比 IVF 召回更高 (recall@100 ~99% vs ~95%), 查询延迟 < 10ms on 1B vectors
- **Sharding**: by geo + category, each shard 50M-100M vectors
- **Rebuild**: nightly full rebuild + online incremental add (append-only delta index, merged每 4h)
- **Quantization**: PQ (product quantization) 压缩到 32 bytes/vec, 5B pins * 32B = 160GB, 可全装内存

### 3.4 Freshness: Online Index
- 新 pin 上传 -> Kafka -> 实时特征抽取 -> 写入 "fresh index" (小, 最近 24h pin)
- 查询时同时查 main index + fresh index, 合并召回
- 昨日后 fresh pin 会在 nightly rebuild 被 merge 进 main

---

## 4. Ranking

### 4.1 L1 Lightweight Ranker (GBDT)

**输入**: 5K candidates, **输出**: top 500
**模型**: LightGBM / XGBoost, 数百棵树
**特征** (~100):
- Query features: length, intent, embedding norm
- Pin features: age, repin count (log), CTR_7d, quality score
- Query-Pin: BM25 score, cosine(q_emb, p_emb), text overlap, category match
- User-Pin: user historical engagement on pin's category/board

**训练**: pairwise LambdaRank on (query, pin_pos, pin_neg) with label = engagement weight

**延迟**: ~5-10ms on 5K candidates (tree inference is cheap)

### 4.2 L2 Heavy Ranker (Multi-task DNN)

**输入**: 500 candidates, **输出**: top 50
**架构**: MMoE (Multi-gate Mixture of Experts) 多任务

```
            shared bottom: [q_emb, p_emb, user_emb, engagement_emb, context]
                 |
        [Expert1] [Expert2] [Expert3] [Expert4]
             \    /  \    /
         [Gate_CTR]  [Gate_Repin]  [Gate_CloseUp]  [Gate_Hide]
              |           |             |             |
           y_ctr       y_repin       y_closeup     y_hide
```

**多任务**:
- $y_{ctr}$: 用户会 click 吗 (pointwise BCE)
- $y_{repin}$: 会 save / repin 吗 (强信号)
- $y_{closeup}$: 会长按/停留 > 5s 吗
- $y_{hide}$: 会主动 hide 吗 (负面)

**融合分**:
$$ \text{score} = w_1 \cdot y_{ctr} + w_2 \cdot y_{repin} + w_3 \cdot y_{closeup} - w_4 \cdot y_{hide} $$

权重 $w_i$ 通过 **线上 A/B 多目标优化** 学得 (Pinterest 用 evolutionary search on business KPI).

**特征工程** (~1000-2000):
- Dense: q_emb (256), p_emb (256), user_emb (128), ctr/repin rates
- Sparse: user_id, pin_id, category_id, board_id -> embedding table
- Cross: user_history_pins avg emb . p_emb; user's top-category match p.category
- Context: device, locale, hour-of-day, session position
- Image: pretrained CLIP image embedding (256d, from Pin tower)

**Loss**: 加权 multi-task BCE
$$ L = \sum_k \alpha_k \cdot \text{BCE}(y_k, \hat{y}_k) $$

### 4.3 Pairwise vs Pointwise 选择

| | Pointwise (BCE) | Pairwise (LambdaRank) | Listwise (ListNet/ListMLE) |
|-|----------------|----------------------|---------------------------|
| L1 GBDT | rarely | **常用** | rare |
| L2 DNN | **常用** (多任务好加) | 可用, 训练慢 | 少用, 梯度复杂 |

Pinterest 实践: L1 LambdaRank (pairwise 对 ranking metric 更直接), L2 pointwise multi-task (多目标好组合).

---

## 5. Re-ranking / Blending

L2 top-50 仍需 policy + diversity 调整:

### 5.1 Diversity (MMR)
$$ \text{MMR}(p) = \lambda \cdot \text{rel}(p) - (1-\lambda) \cdot \max_{p' \in S} \text{sim}(p, p') $$
- 防止 top-10 全是同一 board / 同一 category
- $\lambda \approx 0.7$ 调出 relevance vs diversity 平衡

### 5.2 Freshness Boost
- 新 pin (< 7 days) 分数 * (1 + $\beta$ / (age_days + 1))
- 防止 ranker 过度依赖 CTR_historical 压制新内容

### 5.3 Policy Filters
- NSFW / violent classifier (预计算, per pin 存为 flag)
- Spam / low-quality pins (image hash dedup)
- Locale (EN market 过滤日文-only pins)

### 5.4 Business / Ads Blending
- Organic result 与 promoted pin 按位插入 (每 10 位插 1 个 ad), 各自 ranking 独立, 位置校准用 slot-lift model

---

## 6. Offline Evaluation

| Metric | Formula / 含义 | 使用 stage |
|--------|----------------|----------|
| **Recall@K** | CG 阶段, 用 ground-truth clicks 评估 top-K 召回率 | CG only |
| **NDCG@K** | $\sum \frac{2^{rel}-1}{\log_2(i+1)} / \text{IDCG}$, relevance label from human or engagement | Ranking |
| **MAP** | mean Average Precision across queries | Ranking |
| **MRR** | mean Reciprocal Rank of first relevant | 导航类 query |
| **AUC / PR-AUC** | 各二分类 head (CTR, Repin) | L2 multi-task per head |

**Golden set**: 10K queries, each with human-labeled relevance (0-3). 季度重标.

---

## 7. Online Metrics + A/B

**Primary (north star)**:
- Repin-rate per search session (Pinterest 长期 engagement 代理)
- Session depth (pins viewed per session)

**Secondary**:
- CTR@top-25
- Close-up rate, long-dwell rate
- Query reformulation rate (下降 = 搜得更准)
- Diversity: # unique categories in top-25

**Guardrail**:
- P99 latency
- Hide rate, report rate
- Search abandonment (进搜索后无 action 直接退出)

**A/B framework**: 2-week experiments, 1% ramp -> 10% -> 50%, 用 Pinterest 内部 Helix A/B 平台. sequential testing 防 peeking.

---

## 8. Infra + Training Pipeline

### 8.1 Feature Store
- **Offline**: Snowflake / BigQuery, daily batch for user/pin aggregates (CTR_7d, top_categories)
- **Online**: Redis / RocksDB, serving features with P99 < 5ms
- **Consistency**: training 用 offline store snapshot, serving 用 online store; 定期 skew check

### 8.2 Training Pipeline
```
Kafka events -> S3 parquet (daily)
                    |
            [Labeler] join actions with serving logs (1h window)
                    |
            [Feature Builder] join feature store snapshots
                    |
            [Trainer] PyTorch DDP, 8x A100, 1 epoch/day
                    |
            [Evaluator] offline NDCG + holdout AUC
                    |
            [Shadow Deploy] score prod traffic without serving
                    |
            [A/B Ramp] 1% -> 10% -> 50%
```

### 8.3 Serving Stack
- **Query Gateway**: gRPC, handles auth, logging, sampling
- **CG Service**: calls ES + HNSW shards + user-history service, merges
- **Ranking Service**: loads LightGBM (L1) + TorchScript DNN (L2)
- **Feature Service**: Redis lookup, batch API for 500 pins
- **Cache**: query -> final results, TTL 5min for long-tail, 30s for trending

### 8.4 Capacity Math (back-of-envelope)
- 100K QPS * 500ms * 10 services = ~500K concurrent RPCs
- 5B pins * 32B (PQ) = 160GB ANN index, shard into 20 * 8GB on-machine
- Daily training data: 1B (query, pin, action) * 2KB = 2TB/day
- Feature store online: 5B pins * 2KB features = 10TB, sharded RocksDB

---

## 9. Cold-start + Freshness

### 9.1 New Pin (Cold Pin)
- 无 historical CTR, 依赖 **content features**: image emb + text emb
- 临时 popularity prior: pin's uploader's avg pin CTR, pin's board's avg CTR
- Exploration bonus: UCB / Thompson Sampling 给新 pin 展示机会

### 9.2 New User (Cold User)
- 无 history -> user tower 退化为 locale + device + onboarding interests
- Fallback: trending pins by geo + inferred demographic
- 快速学习: 首 session 的 action heavily upweight in user emb update (EMA with high α)

### 9.3 New Query (Tail Query)
- 无历史 -> 完全依赖 semantic ANN + BM25
- 不走 personalized source (user history 无此类 pin)

---

## 10. Failure Modes + Mitigations

| Failure | Symptom | Mitigation |
|---------|---------|----------|
| ANN index stale | Search misses new pins | Online fresh index + nightly rebuild |
| Feature skew | Online AUC drops vs offline | Daily skew monitor; retrain on latest |
| Popularity bias | Same pins dominate | MMR diversity + exposure-decay feature |
| Feedback loop | Top-K biases future training | Counterfactual IPS weighting in training labels |
| Query cache poisoning | Bad result cached 5min | Cache key includes user segment + policy hash |
| Hot-shard | Popular query overwhelms one ANN shard | Query-level replication + consistent hashing |

---

## 11. Likely Follow-up Probes

面试官大概率会在 45-min onsite 里追问:

1. **"How do you handle visual search (Lens)?"**
   -> query tower 换 image encoder (CLIP ViT), pin tower 不变, 共享 embedding 空间
2. **"How do you personalize?"**
   -> user tower: history pins emb mean + sequence model (GRU/Transformer over last 50 actions); concat with q_emb before pin scoring
3. **"How to reduce feedback loop / exposure bias?"**
   -> IPS (Inverse Propensity Scoring), randomized exploration budget (1-2%), counterfactual model
4. **"What if ranker starts giving stale results?"**
   -> freshness feature, exploration bonus, online learning with streaming updates for hot pins
5. **"How do you evaluate without clicks (new country launch)?"**
   -> Human eval golden set + proxy metrics (CTR_pred calibration) + cautious online ramp with guardrails
6. **"Cost vs quality tradeoff?"**
   -> L2 DNN is 70% of cost; use distillation (teacher = big DNN, student = small DNN) to cut 3x; dynamic depth based on query importance
7. **"Multi-lingual?"**
   -> Multilingual BERT / LaBSE for query tower; maintain per-locale fresh index; translate at query-time as fallback for low-resource languages

---

## 12. 45-min Timing 模板

| 时间 | 段 | 重点 |
|------|-----|------|
| 0-5 | Clarify | Scale, latency, surface, freshness, personalization |
| 5-10 | High-level diagram | 4-stage funnel, 标延迟预算 |
| 10-20 | Candidate Generation | Two-tower 细节, ANN, multi-source, training data + negatives |
| 20-35 | Ranking | L1/L2 分层, MMoE 多任务, 特征, loss, pairwise vs pointwise |
| 35-42 | Metrics + A/B | Offline (NDCG) + Online (repin-rate) + guardrails |
| 42-45 | Follow-ups | Cold-start, diversity, 抽签 deep-dive |

**不要一次讲完所有 detail**. 面试是交互式, 画完高层图后 pause: "Which component do you want me to zoom into?"
