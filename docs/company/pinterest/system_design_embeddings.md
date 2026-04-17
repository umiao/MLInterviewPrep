# Pinterest ML System Design: User & Item (Pin) Embeddings

> Pinterest SD 2025-11 onsite 题目: "Design user & pin embeddings that power candidate generation, ranking features, and similar-pins"
> Scope: objective → encoder 结构 → 训练 pipeline → 服务/ANN → 下游消费
> Format: 45-min SD loop (clarify 5m, objective+label 8m, encoder 10m, training 8m, serving 8m, downstream+followup 6m)

---

## 0. Clarifying Questions (前 5 分钟必问)

"Design Pinterest embeddings" 非常开放, 必须先对齐:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| 消费场景 | 用于 candidate gen (ANN)? ranking 特征? similar-pins 展示? 全要? | 不同消费对 dim / freshness / calibration 要求不同 |
| 实体 | 只 user + pin, 还是 board / advertiser / query? | 多实体联合训练 vs 单塔分别训练 |
| 目标 | 单一 objective (repin) 还是 multi-task (click, repin, long-click, hide)? | 决定 loss 结构, label 噪声处理 |
| 语义 vs 行为 | 要 "兴趣语义" 还是 "协同过滤"? | 语义重: GraphSAGE/文本塔; 协同重: two-tower + in-batch negatives |
| 冷启动 | 新 pin (<100 impression) 与 新用户如何处理? | 决定是否必须 content-based (图像+文本) 塔 |
| Freshness SLA | user embedding 分钟级 / 小时级 / 天级? | 分钟级 ⇒ streaming 推理; 天级 ⇒ batch 足够 |
| Scale | 活跃 pin / user 数? | 5B pins × 500M MAU ⇒ ANN index + shard 必须 |
| Latency | 在线取 embedding P99? | candidate gen 阶段 <20ms, ranking 特征 <5ms |

**本设计假设**:
- 同时服务 (a) candidate gen (ANN, top-k retrieval) (b) ranking 特征 (dot product / elementwise) (c) similar-pins module
- Multi-task: 主 label = **long-repin** (repin 后 7 天未删), 辅 label = click, closeup, long-click
- 新 pin 必须 day-1 可用 ⇒ content tower 必需 (image + text)
- user embedding **15-min 刷新** (近期 session 行为入特征); pin embedding **T+1 daily batch** + 新 pin 实时 inference
- Target dim = **256** (平衡 ANN 检索速度与表达力); 下游 ranking 可再投影到 64
- 5B active pins, 500M MAU, peak 200K QPS user embedding fetch

---

## 1. High-Level Architecture

```
                      ┌───────────────── Offline Training ──────────────────┐
                      │                                                      │
  engagement log ─┬─► label builder (long-repin + aux) ─► training sampler   │
  pin content ────┤                                           │              │
  pin graph ──────┤                                           ▼              │
  user profile ───┘                                    ┌────────────┐        │
                                                       │ Two-tower  │        │
                                                       │ + GraphSAGE│        │
                                                       │   trainer  │        │
                                                       └─────┬──────┘        │
                                                             │ checkpoints   │
                      ┌──────────────────────────────────────┼───────────────┘
                      ▼                                      ▼
            ┌──────────────────┐                   ┌─────────────────┐
            │ Pin Inference    │ (daily batch +    │ User Inference  │ (15-min micro-batch)
            │  Spark + GPU)    │  new-pin stream)  │  Flink + GPU    │
            └────────┬─────────┘                   └────────┬────────┘
                     │                                      │
                     ▼                                      ▼
            ┌──────────────────┐                   ┌─────────────────┐
            │ Pin Embedding KV │ ◄── ANN build ─►  │ User Embedding  │
            │ (RocksDB shard)  │   (ScaNN/HNSW)    │  KV (Redis)     │
            └────────┬─────────┘                   └────────┬────────┘
                     │                                      │
                     └──────────┬───────────────────────────┘
                                ▼
                    ┌───────────────────────────┐
                    │ Downstream consumers:     │
                    │ • Candidate gen (ANN)     │
                    │ • Ranking feature extract │
                    │ • Similar-pins module     │
                    │ • Ad targeting lookalike  │
                    └───────────────────────────┘
```

关键拆分:
- **Pin tower** = content-heavy (image + text + taxonomy + graph), 天级刷新足够 (pin 本身属性变化慢)
- **User tower** = sequence-heavy (近 N 次 engagement), 必须近实时 (兴趣漂移快)
- 两塔在 **shared embedding space** (same dim, same loss) ⇒ 可以直接做 dot-product 检索

---

## 2. Objective & Label

### 2.1 为什么不用纯 self-supervised

Candidate: SimCLR-style 只用 pin↔pin 增强 ⇒ 得到的是 "视觉相似" 而非 "兴趣相似". Pinterest 用户的兴趣信号 (repin, board co-occurrence) 是金矿, 应当直接用上.

**结论**: 主体走 **supervised contrastive from engagement**, 辅以 self-supervised pin-pin augmentation 作为 warm-up / 正则.

### 2.2 Multi-task label

| Label | 权重 | 定义 | 噪声来源 |
|-------|------|------|----------|
| long-repin (主) | 1.0 | repin 且 7 天未删除 | 误点很少, 强信号 |
| click/closeup | 0.3 | 点大图 | 误点多, 噪声大 |
| long-click | 0.5 | closeup 停留 ≥ 10s | 较干净 |
| hide/not-interested | -0.5 (hard neg) | 显式负反馈 | 强信号 (主动表达) |

**Board co-occurrence** 作为第二主信号: 同一 user 在 7 天内 repin 到同一 board 的 pin pair ⇒ 强正对. 比单 impression 噪声低一个数量级.

### 2.3 Contrastive loss

两塔输出 $u \in \mathbb{R}^{256}$, $p \in \mathbb{R}^{256}$, L2-normalize 后:

$$\mathcal{L} = -\log \frac{\exp(u \cdot p^{+} / \tau)}{\exp(u \cdot p^{+}/\tau) + \sum_{p^{-}} \exp(u \cdot p^{-}/\tau)}$$

- $\tau = 0.07$ (典型值, 越小越 "锐化" top-k)
- **Negatives**: (1) in-batch negatives (B=8192, 免费 8k 负样本) + (2) 硬负 sample: 同 category 但用户没 repin 的 pin (避免 "热门偏置" — 全局热门 pin 混进 batch 会让模型学到 "popularity 就是相似")
- **LogQ correction** (Google YouTube two-tower 论文): 对 in-batch negatives 按采样概率 $q(p)$ 做 logit 修正 $s' = s - \log q(p)$, 否则热门 pin 永远被选为负样本 → 被压低 → popularity bias

### 2.4 为什么 multi-task 不是简单加权

主 label 长尾, 辅 label 丰富. 直接 $\sum w_i \mathcal{L}_i$ 会让辅 label 主导. 方案:
- **Shared-bottom + task-specific head**: bottom 出 256-dim shared embedding, 每个 task 有独立小 MLP head 算该 task 的相似度. 共享 embedding 即为下游使用的 embedding.
- 或 **PCGrad / GradNorm** 处理梯度冲突 (long-click 与 click 可能冲突: 误点 click 为正但 long-click 为负).

---

## 3. Encoder Architecture

### 3.1 Pin Tower (content-heavy)

```
 image ──► ViT-B/16 (frozen) ─► 768-d ─┐
 title+desc ─► mBERT (fine-tune last 2 layers) ─► 768-d ─┤
 taxonomy (category, board-topic) ─► embedding lookup ──┤──► concat ──► MLP [1024,512,256] ──► L2 norm ──► p
 engagement stats (CTR, repin rate, age) ─► standardize ─┤
 graph embedding (PinSage pretrained) ─► 256-d ─────────┘
```

- **ViT frozen**: 成本 (5B pins 全量算 ViT = $$$); 只在 fine-tune 阶段开尾部 2 层.
- **Text encoder**: mBERT (multilingual, Pinterest 用户 50% 非英语). Fine-tune 尾部.
- **PinSage 图特征**: 独立 GraphSAGE 预训练 (board co-occurrence graph), 输出固定 256-d 作为 **特征**, 不在 two-tower 里重新训练 graph (避免训练图 scale 爆炸). 这里 graph tower 是 "frozen feature provider".
- **输出**: 256-d, L2-normalized.

### 3.2 User Tower (sequence-heavy)

User 兴趣 = 近期行为序列. Transformer encoder over engagement sequence:

```
last N=50 engaged pins:
  ├─ pin_id embedding (shared lookup with pin tower output? NO — 分开, see below)
  ├─ action type (repin/click/close-up/long-click) embedding
  ├─ surface (home/search/rel-pins) embedding
  ├─ time gap (current_time - engage_time, bucketized) embedding
  └─ dwell time (bucketized) embedding
  ──► sum ──► Transformer (4-layer, 8-head) with causal mask ──► [CLS] pooling
                                                                      │
 user static profile (lang, country, age_bucket, signup_age) ─► emb ──┤──► concat ──► MLP ──► 256-d ──► L2 norm ──► u
 long-term interest vector (30-day repin distribution over 2k topics) ─┘
```

**设计决策**:
- **Pin id 是否与 pin tower 共享?** 不共享. Pin tower 输出 256-d 是 content embedding; user sequence 里的 pin 作为 "行为 token" 可以用独立更小的 id embedding (64-d) 训练. 原因: 用同一个 content embedding 作 input 会让序列模型学到 "复读" content embedding 的捷径, 失去 collaborative signal.
- **长期兴趣**: 30 天 topic 分布摘要 (2k taxonomy → soft distribution) 比把 30 天全序列塞 Transformer 便宜一个量级.
- **冷启动 user**: 序列为空时只靠 profile + 零填充序列 ⇒ 输出近似 "人口统计均值 embedding". 可接受 (一周内自然填充).

### 3.3 为什么要 GraphSAGE / PinSage 附加塔

纯 two-tower 对 **tail pin** 不友好 (行为稀疏). PinSage 用 pin-board bipartite graph 聚合邻居, 给冷/尾 pin 注入来自 "板子语义邻居" 的信号.

简化版 PinSage 一层:
$$h_v^{(k)} = \sigma\left(W^{(k)} \cdot \text{AGG}\left(\{h_u^{(k-1)}: u \in \mathcal{N}(v)\}\right) \oplus h_v^{(k-1)}\right)$$

- $\mathcal{N}(v)$ = random walk 采样的高访问频率邻居 (不是全邻居, 降成本).
- 聚合器: importance-weighted mean (按 random walk visit count).
- 2 层足够 (更深会过平滑).

---

## 4. Training Pipeline

### 4.1 数据量 & 采样

- 每日 engagement event: ~50B (impression/click/repin 混合)
- 下采样: 1% impression (作负样本池) + 100% repin/long-click (主正样本)
- 一个 epoch 训练样本 ~2B (user, pin+) pairs, in-batch neg B=8192 ⇒ 等效 16T 负样本比较

### 4.2 分布式 setup

- **Data parallel** (256 × A100) + **embedding parallel** for pin_id / user_id lookup tables (5B entries × 64d ≈ 1.2 TB, 必须分片 — 用 Meta torchrec 或 TF embedding parallel).
- 一个 epoch ~8 小时, 2 epoch 收敛.
- **Daily incremental fine-tune**: 用昨日 engagement 做 1-hour warm-start 训练, 每 7 天 full retrain.

### 4.3 Streaming vs batch

| 组件 | 选择 | 理由 |
|------|------|------|
| 主模型训练 | 每日 batch (daily fine-tune + weekly full) | 对比学习需要大 batch 做负采样, streaming 学不了 |
| User inference | Streaming (Flink 15-min micro-batch) | 用户兴趣漂移快, freshness 收益明显 |
| Pin inference | Batch (Spark 全量 daily) + streaming (新 pin 秒级) | 老 pin 属性不变, 新 pin 必须立即上线 |

### 4.4 Negative sampling: 关键陷阱

- **纯 in-batch negatives**: 简单但有 popularity bias. 解法: LogQ correction.
- **Hard negatives from ANN**: 取当前模型 top-100 近似召回中用户没 repin 的 pin 作为硬负. 大幅提升 top-k precision, 但加 5x 训练成本. 通常 stage-2 才加.
- **False negatives (看过但没反应的正样本)**: 用 hide/not-interested 作显式硬负是干净的; impression-not-click 作负噪声大 (用户可能单纯没看到).

### 4.5 Offline 评估

- **Retrieval @ k**: hold-out 当日用户 repin 的 pin, 看 query user embedding 从 5B 池子中能否 top-k 召回. Recall@100, Recall@500.
- **Cold pin Recall**: 专门评估 < 100 impression 的新 pin 能否被正确召回 (content tower 的价值).
- **NDCG on downstream ranker**: 把 embedding 接到现有 ranker 作特征, 看 NDCG@10 是否提升 (最终指标).
- **Embedding diversity**: 抽样看 intra-user top-k 的 category 分布, 避免 "全是同一个 topic".

---

## 5. Serving Architecture

### 5.1 Inference pipeline

**Pin side** (daily batch):
```
Spark job (daily 02:00) ─► load latest pin tower checkpoint
  ─► for each pin shard (10k batches × 500k pins):
        GPU inference ─► 256-d float16 vector
  ─► write to RocksDB sharded KV (pin_id → vec)
  ─► diff with yesterday ─► push delta to ANN index builder
```

**New pin streaming** (Kafka topic `pin_created`):
```
Flink consumer ─► TorchServe (pin tower container, 8 × A10)
  ─► 256-d vec ─► write KV + incremental add to ANN index
  ─► SLA: p99 < 30s from pin create to searchable
```

**User side** (15-min micro-batch):
```
Kafka topic `user_engagement` ─► Flink windowed aggregator
  ─► build (user_id, last-50-pin-sequence + profile) feature vec
  ─► TorchServe (user tower, 32 × A10) batched inference (B=256)
  ─► write to Redis cluster (user_id → vec, TTL=4h)
```

### 5.2 ANN index

- **Algorithm**: ScaNN (Google, quantization + tree-based) 或 HNSW.
- **Sharding**: 5B pins ÷ 50M per shard = 100 shards. Each shard 处理 ~2k QPS.
- **Build cadence**: 每日 rebuild full, hourly delta merge.
- **Memory**: 5B × 256 × 2 byte (fp16) = 2.5 TB; 量化到 int8 + PQ (product quantization) → ~500 GB, 可分 100 × 5 GB shard.
- **Query**: user vec → 100 shards parallel top-50 → merge top-200 ⇒ p99 ~15ms.

### 5.3 Freshness vs cost tradeoff

| 方案 | User latency 保证 | 成本 | 场景 |
|------|------------------|------|------|
| 分钟级 streaming | 15 min | 高 (32 GPU always-on) | 本设计 (重度用户效果显著) |
| 小时级 batch | 1 h | 中 | Passive user |
| Request-time on-the-fly | 当次 request | 极高 (每请求算 tower) | 不采用; 只在 "刚登录用户" fallback |

**Hybrid**: 老用户走 15-min cache, 新用户/长时间未活跃 fallback 到 request-time 计算 (用缓存 session 序列).

### 5.4 Dimension & Quantization

- 训练时 256-d float32.
- 存储: float16 (精度损失 < 0.1% Recall@100).
- ANN: int8 + PQ(m=32, k=256) 把 512 byte/vec 压到 32 byte/vec. 建议 top-500 之后再用 float16 精排.
- 下游 ranking 消费: 原生 256-d + MLP 投影到 64-d 作为 ranker 的 user/pin 特征 (减少 ranker 参数).

---

## 6. Downstream Uses

### 6.1 Candidate Generation
- User vec → ANN top-1000 pins → feed 给 L1 light ranker.
- 多路召回之一 (另一路 board-follow, topic, social).
- A/B 增益观察: Recall@1000 从 0.25 → 0.33.

### 6.2 Ranking Features
- 在 ranker input 加入: `user_emb`, `pin_emb`, `user_emb · pin_emb`, `elementwise_product`, `euclidean_dist`.
- Dot product 单特征即可带 ranker NDCG +2% (Pinterest paper).
- 必须防 leakage: ranker 训练用 embedding 必须来自 **训练集时间之前** 的 checkpoint (不能用当日 embedding 训当日 ranker).

### 6.3 Similar Pins Module
- "More like this" 按钮: 取 source pin 的 pin_emb → ANN top-20 同池检索.
- 要求过滤: 同 advertiser 不超过 2 个, 同 board 不超过 3 个 (diversity).

### 6.4 Ad Targeting (Lookalike)
- 广告主 seed 用户 → mean(user_emb) → ANN top-N 找 lookalike.
- 需要 **privacy 限制**: seed 人数 < 100 不允许 (避免重识别).

---

## 7. Monitoring & Evaluation

### 7.1 Offline (每日)
- Recall@100 / @500 on hold-out
- Cold pin recall (new pin < 100 impressions)
- Embedding drift: KL divergence between today's和 yesterday's topic-level mean embedding (> 0.1 触发告警, 说明模型漂移)

### 7.2 Online
- Candidate gen: Recall@1000 (有 ground-truth 的 held-out slice)
- Ranking feature: 下游 ranker offline NDCG
- A/B test primary: session-level repin rate, long-session rate
- Embedding staleness: p95 user embedding age (SLA < 20 min)

### 7.3 Popularity bias check
- 观察 top-k 召回中 pin 的 impression 分位数分布. 如果 top-k 90% 来自 top-10% 热门 pin ⇒ LogQ correction 失效, 需要重调 τ 或加硬负.

---

## 8. 常见 Follow-ups (面试官必追)

### Q1: 为什么用 two-tower 而不是单塔 (cross-attention)?
答: 单塔 (user-pin cross) 精度高但 serving 无法 ANN (必须每 pair 过一次模型). Pinterest 5B × 500M 规模下必须用 two-tower + ANN. Cross-attention 只能放在下游 ranker stage (1k 候选规模).

### Q2: 如何防止 popularity bias?
答: (1) LogQ correction 修 in-batch negative 的采样偏差. (2) 加 explicit hard negatives (同 category 未 repin). (3) 加 diversity-aware loss 项或 serving-side 粗粒度 cap. (4) 长期看要有 debias 数据 (随机小流量, uniform 采样) 校准.

### Q3: 冷启动 pin 怎么办?
答: Content tower (image + text + taxonomy) 保证 day-1 就有合理 embedding. 上线前跑一次 streaming inference. 首 24h 给 explore 流量 (小 budget cap, 收集行为). Graph tower (PinSage) 在 pin 获得第一个 board pin 后 incremental 更新.

### Q4: 用户兴趣漂移怎么捕获?
答: 双时间尺度: (a) 短期 = 近 50 次 engagement sequence, 15 分钟刷新. (b) 长期 = 30 天 topic 分布. Transformer 对近期 token 自然有位置偏好, 加时间 gap embedding 让模型显式学时间权重.

### Q5: Two-tower 训好后, 下游 ranker 什么时候也要改?
答: 理论上只要 embedding 换了 checkpoint, ranker 的 `user_emb · pin_emb` 特征分布就变. 做法: (a) ranker 做 embedding stop-gradient 拿到特征后冻住 embedding 版本. (b) embedding + ranker 联合发布: 新 embedding 落地 → retrain ranker → 同一 A/B 上线. (c) 防止 ranker 用过期 embedding: 特征中带 embedding_version id.

### Q6: 为什么不用 user-user collaborative filter?
答: MF-style user-user 对 cold user 完全无解; 新用户零行为 ⇒ 零 vector. Two-tower 有 user profile + 零序列 ⇒ 至少有 population-mean embedding. 且 MF 不能用 image/text content.

### Q7: PinSage 能否替代 two-tower?
答: PinSage 只输出 pin embedding, 没有 user embedding (它的 "user" 是 board, 或借 board-user 路径拼接, 绕). 作为 pin content 塔的附加信号合理, 但主 retrieval 还是 two-tower. 工业实践中 (Pinterest 2019 paper) 也是 PinSage 产 pin vec + 另一个 user tower.

### Q8: 如何降成本?
答: (1) Image tower frozen (ViT 不 fine-tune, 大头计算只做一次写 offline feature store). (2) Pin embedding 只 daily 刷新 + 新 pin streaming; 不必每分钟全量. (3) User tower 用蒸馏: 512-d teacher → 128-d student, 精度损失 1%, 成本降 4x. (4) ANN 用 PQ 压缩 + tiered cache (最热 1% 存 GPU-memory ANN, 其余 SSD).

### Q9: Multi-objective 怎么平衡 click vs repin?
答: Shared-bottom + task head, 共享 embedding 由 gradient 平均驱动. 可以 GradNorm / PCGrad 自动平衡. 或: 以 long-repin 为唯一 embedding-level loss (高质量干净), 其余 label 留给下游 ranker.

### Q10: 下线监测 embedding 质量坏掉怎么 rollback?
答: 每天 embedding 打 version tag + checksum. Online A/B 看 Recall@1000 与下游 NDCG 的实时曲线. 跌超过阈值 (如 −0.5%) 自动 halt promote; ANN 服务保留昨日 shard 可一键切回. 这就是为什么 **embedding 与 ANN index 分开版本化**: 切 embedding 不必 rebuild ranker.

---

## 9. 可选深入方向 (面试官问 "还有什么?")

- **Causal embedding**: impression-level propensity weighting, 消除 position bias.
- **Cross-surface embedding**: home / search / shopping 是否同一 embedding? 如果行为分布差异大, 考虑 surface-conditioned 头.
- **语言 / 地区公平性**: 低资源语言用户被同一 embedding 压制, 考虑 per-region fine-tune head.
- **Fresh content boost**: 新 pin 在 ANN 检索 score 加时间衰减 bonus.
- **隐私**: user embedding 本质是行为压缩, 需要 differential privacy 防重识别 (尤其 lookalike 场景).
