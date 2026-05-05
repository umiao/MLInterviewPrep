# Pinterest ML System Design: Pin Ranking for Home/Topic Feed

> Pinterest ML System Design Interview Prep
> Scope: End-to-end pin ranking for home feed + topic feed — retrieval, ranking, multi-objective optimization, serving, metrics
> Format: 45-min onsite SD loop (clarify 5m, high-level 5m, retrieval 8m, ranking 15m, serving+metrics 10m, follow-ups 2m)

---

## 0. Clarifying Questions (前 5 分钟必问)

面试官抛出 "Design Pinterest Pin Ranking" 时, 不要直接画架构图. 先澄清 scope:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| Surface | Home feed? Topic feed? Related pins? Search? | 不同 surface 目标不同: home 偏 exploration, related 偏 relevance |
| Scale | DAU/MAU? QPS? Pin corpus 大小? | Pinterest 约 500M MAU, peak ~100K QPS, corpus 数十 B pins |
| 业务目标 | Session length? Repin rate? Long-term retention? | 决定 label 设计与 multi-objective 权重 |
| Latency | Home feed 端到端 SLA? | 典型 P99 < 400ms, 留给 ranking ~150ms |
| 反馈信号 | 正向 (repin/click/closeup/longclick), 负向 (hide/report/not-interested)? | 决定 head 设计 |
| Freshness | 是否需要考虑新 pin cold start? 内容时效? | 决定 retrieval 是否需要 real-time index |
| Diversity | 单次 feed 是否需 topic/creator diversity? | 决定是否加 re-ranking 层 |
| Constraint | Ads 插入? Shopping pin 配额? Policy filter? | 决定 business-rule 层位置 |

**假设 (本设计默认)**:
- Surface: home feed (logged-in), 单次请求返回 25 pins (无限滚动后续分页)
- 500M MAU, peak 80K QPS ranking, pin corpus ~5B active pins
- 主目标: long-term weekly repin + session length; 约束 hide-rate < baseline
- P99 端到端 400ms, ranking budget 150ms, candidate generation 100ms

---

## 1. High-Level Architecture

```
[User request: /v3/home_feed]
        |
        v
  [Request Context Builder]  -- user_id, device, locale, time, session state
        |
        v
  [Candidate Generation / Retrieval]  -- 多路并行, 输出 ~2k candidates
   - PinSage embedding ANN (user -> pin)
   - Board-follow / recent-engagement based
   - Trending / topic-affinity
   - Creator-follow fresh pins
        |
        v
  [L1 Light Ranker] -- GBDT or 2-tower dot-product, 2k -> 600
        |
        v
  [L2 Heavy Ranker] -- MMOE multi-task DNN, 600 -> scored
        |
        v
  [Blending + Business Rules]
   - multi-objective utility score
   - diversity (MMR over topic/creator)
   - ads/shopping insertion
   - policy/safety filter, dedup vs recent
        |
        v
  [Final 25 pins] -- response, async log to Kafka for training
```

Side infra:
- **Feature store**: online (Redis/RocksDB) + offline (S3+Hive), consistency via dual-write.
- **Embedding service**: PinSage/GraphSAGE embeddings refreshed daily.
- **Training pipeline**: Spark feature join -> TFRecord -> TF/PyTorch distributed training.
- **Online serving**: TF-Serving / Triton with GPU for L2, CPU for L1.

---

## 2. Retrieval / Candidate Generation

### 2.1 多路召回 (分而治之)

| 路径 | 原理 | 规模 | 更新频率 |
|------|------|-----|--------|
| **PinSage ANN** | user embedding (avg recent pin emb) -> HNSW/ScaNN top-500 | 500 | daily refresh emb, index hourly |
| **Board/Topic follow** | user 关注的 board/topic -> 最新 pins | 400 | streaming |
| **Recent engagement co-pin** | item-item CF: "repinned X -> also repinned" | 300 | daily |
| **Trending** | per-topic trending pins (24h repin velocity) | 200 | 5min 更新 |
| **Creator fresh** | user follow 的 creator 的 <24h pins | 200 | streaming |
| **Reranking recovery** | dedup 后补齐 long-tail exploration | 400 | on demand |

合并后 dedup -> ~2k candidates.

### 2.2 PinSage 嵌入 (重点讲)

- **图结构**: pin-board 二部图, 边=pin 被 save 到 board.
- **采样**: 2-hop random walk with importance sampling, 每个 pin 采 50 邻居.
- **聚合**: GraphSAGE-style, 多层 mean/max-pool + MLP, 输出 256-d emb.
- **训练 loss**: max-margin triplet (positive=co-engaged pins, negative=in-batch + hard negatives from 同 topic).
- **服务**: emb 落 offline table, user emb = 最近 20 个 engaged pin emb 的 weighted avg (时间衰减).
- **索引**: ScaNN / HNSW, ef=200, recall@500 > 0.95 vs brute force.

### 2.3 召回层评估
- Offline: Recall@K (K=500, 1000) 针对 held-out engaged pins.
- Overlap 分析: 各路径重合度, 保证互补性.
- A/B 新召回源时, 单独开 flag 测 downstream repin lift.

---

## 3. Features

分 4 大类. 面试官常追问 "how do you version features", 重点讲 feature store.

### 3.1 Pin features (候选物)
- **Content emb**: visual (CNN/ViT from image) 512-d, text (BERT on title+desc) 768-d, graph (PinSage) 256-d.
- **Categorical**: topic id, language, domain (url host), is_video, aspect_ratio bucket.
- **Engagement histogram**: 1d/7d/30d repin/click/hide count + rate (统计全局).
- **Freshness**: age_in_hours bucket.
- **Creator quality score**: historical engagement-weighted Bayesian smoothing.

### 3.2 User features (请求者)
- **Long-term profile**: top 20 topics (weighted), language, country, gender-age predicted.
- **Short-term**: last 50 engaged pins emb (sequence), last searched queries (BERT emb).
- **Demographic**: device, OS, app-version (serving 兼容).
- **History counters**: repins/week, session/day 等 raw counts (让模型自己学 saturation).

### 3.3 Context features (请求时刻)
- Time-of-day (cyclic sin/cos), day-of-week, local_hour.
- Surface (home/topic), session depth (第几次翻页).
- Recent-impression set (用于避免 dedup).
- Network type (wifi/4g) — 影响 image quality 决策, 但也可当 feature.

### 3.4 Cross features (user x pin)
- Cosine(user_emb, pin_emb) across 3 emb spaces.
- User-topic x pin-topic match score.
- User has followed pin.creator? Has saved pin.board?
- Historical co-engagement between user 的 top-topic 与 pin.topic.

**Feature store 要点 (面试官喜欢问)**:
- Online 取 user+context in <10ms via Redis; pin features 预先 batch fetch (request 1 次 KV get 2k keys).
- Point-in-time correctness: 训练时用 request-time snapshot, 避免 label leakage (pin age 要用请求时的, 不是训练时的).
- Feature drift 监控: PSI / KS test 每日跑, alert 超阈值.

---

## 4. Model Family

### 4.1 L1 Light Ranker (2k -> 600)

选型: 两塔 DNN (dot product) 或 GBDT.
- **两塔**: user tower (user+context features) emb, pin tower (pin features) emb. 在线仅算 user tower (pin 预计算), 然后 dot-product. 延迟 <20ms for 2k pins.
- 训练 label: coarse engagement (click OR repin OR closeup).
- 为什么不用 L2 直接打 2k: L2 特征多, 过 cross feature 成本 ~5x, latency budget 吃不下.

### 4.2 L2 Heavy Ranker (600 -> scored)

选型: **Multi-gate Mixture of Experts** (MMOE, 多门混合专家) + shared-bottom cross layers.
- **Bottom**: embedding lookup + DCN-v2 cross (显式 feature interaction) + 3 层 MLP.
- **Experts**: 8 个 expert, each 2 层 MLP.
- **Task gates**: 每个 task 有独立 softmax gate 选 expert 组合.
- **Heads (multi-task)**:
  - pRepin (binary, BCE)
  - pClick / pCloseup (binary)
  - pLongClick (dwell > 10s, binary)
  - pHide / pNotInterested (binary, 负向)
  - pVideoCompletion (regression, 视频 pin only, masked loss)
  - LongTermValue head (next-7-day session count, regression, counterfactual-labeled)
- **Loss**: `L = Σ w_task * BCE_task - w_neg * BCE_hide - w_neg * BCE_nir + λ_aux * MSE_LTV`.
  - 负向 head 用减号 (最小化 P(hide)).
  - w_task 通过 Pareto 自动调 (见 §5).

### 4.3 替代方案与权衡

| 方案 | 优点 | 缺点 | 为什么不选 |
|------|------|------|----------|
| **Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联) | 简单, memorization 强 | 多任务差, cross feature 手工 | 已被 MMOE + DCN-v2 超过 |
| DIN/DIEN (attention over user seq) | 序列建模强 | 训练/serving 复杂 | 可作为 user tower 子模块, 不是顶层结构 |
| Transformer-based ranker (HSTU / GR) | SOTA, unified generation+rank | GPU 成本高, latency 压力 | 放 follow-up: 下一代方案, 本设计用 MMOE 作为 baseline |
| Pure GBDT | 训练快, 可解释 | 序列/emb 特征弱, 多任务差 | 仅作 L1 或 feature importance 工具 |

### 4.4 训练细节
- 样本: 每天 ~10B impression, 按用户 subsample (每 user 上限 200 samples/day) 防头部过拟合.
- 负采样: in-batch negatives for L1; L2 用真实 impression 中未 repin 作 negative (更接近 serving 分布).
- Position debiasing: shallow position-tower (position 只进 wide, 不进 deep), serving 时置 0.
- Optimizer: AdamW, lr schedule cosine, warmup 10k steps, distributed across 32 GPU (Horovod/DeepSpeed).
- 每日增量训练 (warm-start from 前一日 checkpoint), 每周 full retrain 防漂移.

---

## 5. Multi-Objective Optimization

单 objective (CTR) 会诱发低质内容. Pinterest 在意 long-term repin + session + 低 hide.

### 5.1 Blending utility
serving 时对每个 pin 计算:

```
utility = Σ w_i * pHead_i  -  Σ w_neg_j * pNegHead_j  +  γ * DiversityBonus
```

默认权重 (示例):
- w_repin = 1.0, w_click = 0.3, w_closeup = 0.4, w_longclick = 0.5, w_video_complete = 0.2
- w_hide = 2.0, w_nir = 1.5
- γ (diversity) = 0.1

### 5.2 权重学习 / tuning
- **Pareto front scan**: 离线对权重网格搜索, 画 (repin, hide) / (repin, session) trade-off 曲线, PM 选点.
- **Bayesian optimization online**: 每周一次多 arm A/B, 以 north-star metric (WAU * session_len) 为 reward 更新 w.
- **Constrained opt**: Lagrangian, 限制 hide-rate <= baseline+ε, 学 λ_hide.

### 5.3 Diversity / Long-term

- **MMR (Maximal Marginal Relevance)** 对 top 200 做 re-rank:
  `score' = (1-λ) * utility - λ * max sim(pin, chosen)`,
  sim 用 topic 匹配 + PinSage emb cos.
- **Creator 频次约束**: 单次 feed 同 creator <=2 个.
- **Exploration**: 10% slot 保留给 Thompson-sampling 选的 less-served content, 收集反馈训练.
- **Long-term head**: counterfactual uplift model (DML / doubly-robust) 估 "展示该 pin 对 next-7d session 的因果效应", 加入 utility.

---

## 6. Serving Constraints

### 6.1 Latency budget (端到端 400ms)
| 阶段 | budget |
|------|--------|
| Gateway + auth | 20ms |
| Context + user feature fetch | 20ms |
| Retrieval (并行 6 路, ANN + KV) | 80ms |
| L1 light ranker | 20ms |
| Pin feature batch fetch (600 pins) | 30ms |
| L2 heavy ranker (GPU batch) | 80ms |
| Blending + MMR + business rules | 15ms |
| Image meta fetch + response build | 40ms |
| Network overhead | ~95ms |

### 6.2 Capacity
- Peak 80K QPS, L2 单请求 600 pins 前向 -> 48M pins/s 前向.
- 单 A10 GPU ~500K pins/s (batch=512, MMOE 10M params), 需约 100 GPU replicas + 2x HA + 1.5x headroom ≈ 300 GPU.
- Feature KV: 2k pin feature fetch per req, 每 pin ~2KB, 总流量 ~300Gbps peak, Redis cluster + local cache (LRU 100k pins, hit rate ~70%).

### 6.3 可靠性
- **分级降级**:
  - L2 超时 -> 用 L1 score 直接返回
  - Retrieval 单路 fail -> 其余路径 quorum
  - Feature store fail -> pin-level 默认 feature (全局均值)
- **Circuit breaker** on each downstream, p99 latency 超阈值自动 degrade.
- **Shadow traffic** 新模型先 1% dark launch 对比预测分布.

### 6.4 训练-serving 一致性
- 同一 feature transformation code (Python lib + C++ serving binding).
- 每日 consistency check: online log 抽 1% 和 offline 重算 feature, 不一致率 <0.1%.
- Schema registry (protobuf) 强制 feature 版本号.

---

## 7. Metric Ladder

### 7.1 Offline
- **Ranking quality**: AUC per head, NDCG@25 over repin label, GAUC (per-user AUC).
- **Calibration**: ECE (expected calibration error) per head (对 pRepin, hide-rate 阈值触发 business 决策, 必须 calibrate).
- **Uplift**: counterfactual NDCG via **Inverse Propensity Scoring** (IPS, 逆倾向加权) on logged exploration slots.
- **Fairness / coverage**: creator Gini coefficient, topic entropy.

### 7.2 Online A/B
| Layer | Metric | Guardrail |
|-------|--------|-----------|
| North-star | WAU, weekly session count, weekly repin | primary, 2-week test |
| Engagement | repin/impression, longclick rate, video completion | — |
| Negative | hide rate, report rate, notification-disable rate | must NOT regress |
| Diversity | unique topics/session, creator Gini | guardrail |
| Ecosystem | new-creator pin impression share | guardrail (防 rich-get-richer) |
| Infra | P99 latency, error rate, cost/request | guardrail |

Statistical design: 1% exposure, 14-day, **Controlled-experiment Using Pre-Experiment Data** (CUPED, 实验前数据方差缩减), Bonferroni 校正 multi-metric.

### 7.3 Long-term holdout
- 1% 永久 holdout (用户级), 追踪 6-month retention / paid conversion, 防 short-term proxy 过拟合.

---

## 8. Cold Start

### 8.1 新用户 (<5 engagement)
- Onboarding: 让用户选 5 个 interest -> seed topic vectors.
- Retrieval: 偏 trending + topic-popular, 少用 PinSage (无 history).
- Ranking: 用 "new-user sub-model" (少量 feature, 高 exploration), switch to 主模型 at 20 engagement.

### 8.2 新 Pin (<24h)
- Emb: image/text emb 立即可算 (CNN + BERT inference), graph emb 缺失 -> 用 board 邻居平均.
- Ranking: fresh-boost term 在 blending 加 β * exp(-age/τ), β 随 exploration budget 衰减.
- Feedback loop: 新 pin 前 1000 次 impression 强制分配到 exploration slot 收敛 CTR 估计.

### 8.3 Dormant 唤醒
- >30d 未活跃 -> 用 "reactivation pool" (用户历史 top-topic + 近期 trending 交集).

---

## 9. Failure Modes & Mitigations

| 风险 | 症状 | 缓解 |
|------|------|------|
| Filter bubble | 用户 topic entropy 单调下降 | diversity 约束 + exploration slot 硬配额 |
| Clickbait 过推 | click 高但 repin 低 longclick 短 | multi-head + w_hide + quality score feature |
| Creator 马太 | top 1% creator 占 50% impression | 在 MMR 加 creator penalty, monitor Gini |
| **Position bias** (位置偏差) 学偏 | 模型学成 "第一位总是高分" | shallow position-tower, serving 清零 |
| Feature drift | holiday / 事件导致特征分布跳变 | PSI daily alert, auto fall-back to older checkpoint |
| Label delay | repin 可能 hours 后才发生 | 7-day conversion window, 区分 immediate vs delayed head |
| Training-serving skew | offline AUC 涨 online 不涨 | feature parity check + online replay |

---

## 10. Follow-up Hooks (面试官可能深挖)

1. **"如何从 MMOE 迁到 transformer-based generative ranker (如 Meta HSTU)?"**
   答: 统一 retrieval+ranking, user history 当 token sequence, next-item prediction 作 pretrain, 再 multi-task fine-tune. 挑战: serving GPU 成本 5-10x, 需 prompt caching + KV-cache + speculative decoding. 用 distillation 回 MMOE 做学生模型落地.

2. **"cold start 用 LLM 做 text-only 理解值得吗?"**
   答: pin description/title 经 LLM embed 效果好于 BERT, 但 serving 贵. 方案: 离线 batch LLM -> 蒸馏到 in-house 小模型作 feature.

3. **"广告插入如何不破坏 organic 指标?"**
   答: ads 有独立 pAction model, 通过 second-price auction 转 ECPM; 插入位置由 joint optimizer 决定 (把 ads 加入同一 blending, organic 与 ads 公平竞争 slot, 但受 ad-load constraint).

4. **"离线-在线 gap 如何 debug?"**
   答: (a) feature parity (抽样对比), (b) label parity (offline 用 delayed label, online 用 immediate), (c) sample parity (training 有 subsample, 要逆权重), (d) serving skew (eg GPU fp16 vs training fp32).

5. **"如果 business 要求增加 shopping pin 占比, 怎么办?"**
   答: 不直接改 loss. 在 blending 加 shopping boost term w_shop 受 Lagrangian 约束于 "总 session 不跌 x%". 或 PM 模式: ads-style quota slot.

6. **"用户隐藏 pin 的 signal 应当作 hard filter 还是 soft loss?"**
   答: explicit hide creator -> hard filter 7d; hide single pin -> soft negative. not-interested 主题 -> 降该 topic weight in user profile 但不完全屏蔽.

7. **"多模态融合 CNN+BERT+PinSage 怎么做?"**
   答: 三路 emb concat -> gated fusion (learnable per-mode gate), 或 co-attention. 或 joint pretrain 用 CLIP-style contrastive. 实践: late fusion 稳 + 简单.

---

## 11. 45-Minute Timing Cheat Sheet

| 时间 | 内容 | 关键句 |
|------|------|------|
| 0-5m | Clarify + 假设 | "In scope: home feed ranking for logged-in users; out of scope: ads auction, safety classifier" |
| 5-10m | High-level arch 画图 | 画出 6 个 box: request / retrieval / L1 / L2 / blending / response |
| 10-18m | Retrieval + features | 重点: PinSage, multi-source, feature store 点对齐 |
| 18-33m | L2 model + multi-objective | 重点: MMOE + heads + negative head + MMR + Pareto |
| 33-40m | Serving budget + metric ladder | 画 latency 表 + capacity 估算 |
| 40-43m | Cold start + failure modes | 2-3 句扫一下, 证明想过 edge |
| 43-45m | Follow-up + questions | 留一个 hook 给面试官提问 |

---

## Appendix A: Home Feed vs Related Pins vs Search

三个 surface 共享基础架构但差异显著:

| 维度 | Home Feed | Related Pins | Search |
|------|-----------|--------------|--------|
| Intent | 探索, weak intent | 深挖当前 pin | 强 query intent |
| Retrieval | 多路 (user-centric) | pin-pin similarity (item-item) | query understanding -> inverted index + semantic |
| Ranking label | repin + session | closeup + next-click | click + query-satisfy |
| Diversity | 必须 | 次要 | query-scoped |
| Freshness | 中 | 中 | 高 (recency ranker) |

同一 MMOE backbone 可共享, per-surface fine-tune head 权重 + context features.

---

## Appendix B: 关键数字备忘

- 500M MAU, 100M+ DAU (约数)
- Pin corpus ~5B active (数十 B total)
- Home feed peak ~80K QPS
- Ranking P99 budget 150ms (in 400ms E2E)
- PinSage emb 256-d, image emb 512-d, text emb 768-d
- L2 MMOE ~10M params, 8 experts, 6 heads
- Training corpus ~10B daily impressions, 32-64 GPU distributed
- A/B duration 14 day, 1% traffic, CUPED variance reduction
