# Source 04 — Top-3 Comments Golden Answer (Meta MLSD, 45-min walkthrough)

**Provenance**: Verbatim from user-authored Discord message 1503871555216605214
(2026-05-12, channel #ml-interview-prep). Part 4 "Golden Answer (完整脚本)" + Part 5
"通用 Mock 节奏 Checklist" reproduced below in full. A second user message
(1503874418802163744) follows under "Reference appendix" with the user's own
Shallow Bias Tower / Shadow Feature Logging / Design Doc 强调话术 reference --
this is the source of the **Bias Tower 简版** fusion segment embedded into the
seeded `architecture` column AND the **Shadow Logging + Train-Serve Skew 简版**
fusion segment embedded into the seeded `production_constraints` column, both
anchored to fr-node `meta-prep/system-design-must-knows/popularity-bias-debiasing`
(framework_nodes.id=266) for 深入 navigation.

---

## Part 4: Top-3 Comments Golden Answer (完整脚本)

下面是 ideal narrative，按上面的三段式 + 缝合规则写。第一人称、可朗读、可背诵。

### Opening (60s)

"在我深入之前，先 60 秒锁三件事：
Scope: 我要设计一个系统，从一个 post 下的所有 comments 中选出 3 条 surface 给 viewer，
optimize for viewer's joint experience (engagement + community health)。Retrieval
被单个 post 的 comment pool 天然 bound，所以这是个 ranking + set-selection 问题，
不是 multi-stage retrieval。
3 个 unique twists vs generic ranking:

- Comment != item: 超短文本 + 作者是 user graph 节点 + social signal 是主信号
- Time-bias: 早发的 comment 抢曝光，需要 velocity-based feature 和 bandit explore
- Adversarial + community health: 进 guardrail，不进主优化目标

Time plan: 15 min 给 framing/metric/label/feature，25 min 给 model+serving+monitoring。"

### Section 1: Framing (4 min)

"L1 (user): Viewer 是主用户 -- 他们消费 comments 决定是否参与。Commenter 和 OP 是
secondary stakeholder，进 joint experience guardrail。
L2 (scale): 100M DAU, ~10% commenting rate, viral post peak 100x average,
p99 < 200ms。
L3 (twists with implications):

- Comment != item -> 需要 text + social fused representation，commenter 当 sub-entity
- Time-bias -> engagement velocity (rate not count) 当 feature，bandit explore 补晚评论
- Community health -> 独立 abuse model + toxicity hard filter pre-ranker

L4 (ML formulation): 2-stage point-wise ranking (cheap pre-rank -> deep rank) +
list-level reranking (MMR for diversity)。Retrieval trivial 不展开。
==> 下段缝合: 这 3 个 twist 每个都会 hook 到下一段的具体 metric 或 guardrail。"

### Section 2: Metrics (3 min)

"L1 North-star: weekly commenter return rate -- 一个数，不并列。捕捉「看到好的 top-3
-> 愿意参与 -> 长期回流」。
L2 Proxies (3, 每个一句 alignment):

- Comment-area dwell time -> top-3 有趣 -> 用户读得久 -> return ↑
- Reply rate triggered by top-3 -> top-3 引发对话 -> commenter return ↑
- Self-comment rate after top-3 -> top-3 激发参与 -> 新 commenter return ↑

List-level metric (top-3 是 set selection):

- Top-3 diversity score (sentiment / commenter / topic 3 轴)
- Set-level user satisfaction (post-view next-action distribution)

L3 Guardrails (指标 + 阈值 + enforce 机制):

- Toxicity rate < 0.5% -> hard filter pre-ranker
- Report rate per 1k impressions < X -> A/B halt criterion
- p99 latency < 200ms -> serving constraint
- Early-post exposure share -> fairness re-weight in loss
- Group exposure gini -> fairness audit

L4 Causal chain: reply rate ↑ -> 用户感受到 comment area 有对话价值 -> 用户回流参与
-> weekly commenter return ↑
==> 下段缝合: north-star 和 3 个 proxy 直接定义了 label 结构 -- 下面 label 段会逐一落地。"

### Section 3: Labels (4 min)

"Positive label 阶梯:

- L1 baseline (the dumbest version): binary engagement (like / reply within window)
- L2: weighted multi-signal (reply > like > view-completion)
- L3 (我选这层): engagement-to-impression ratio in rolling [T, T+1h] window
  - Trade-off: 比 raw count 复杂，但 partial-debias 了 position bias
- L4 (留 follow-up): multi-task labels with weighted heads

Negative label (这道题的核心难点 -- selection bias):

- Explicit: dislike / report (strong signal, 直接用)
- Exposed-not-engaged: 标准 negative
- Unexposed: treat as unknown + IPS-weighted + bandit-exploration backfill
  - Why not 'unexposed = negative': 引入巨量 false negative (好 comment 只是没曝光过)
  - Trade-off: 工程复杂，但理论正确

Imbalance ladder (stop at L2, 留 L3/L4 给 follow-up):

- L1: stratified sampling
- L2: class-weighted loss

Bias handling: popularity / position / freshness -> shallow bias tower，serving 时
mask 输出 (YouTube 2019 做法，比 mask input feature 更稳，因为 model 不能从其他
feature 重建 bias)。
Leakage guard: feature snapshot @ T, label observation @ [T, T+ΔT], no overlap。
==> 下段缝合: multi-task label (engagement / quality / safety) 定义了下面 architecture
需要的 head 数量。"

### Section 4: Features (3 min)

"4 象限模型，每象限 3 个 + 1 个 comment 独有:
User (viewer):

- Demographic + topic preference embedding
- Viewer 历史 comment engagement rate
- Viewer sentiment preference (likes positive / debate / sarcasm)

Item (comment + commenter sub-entity):

- Comment text embedding (computed once at creation)
- Early engagement velocity (rate-based, time-debiased) <- 对应 Section 1 time-bias twist
- Commenter identity (verified / OP / followed-by-viewer) <- 对应 comment != item twist
- Toxicity / sentiment score (bonus, 喂 quality head)

Context:

- Post topic + age
- Time of day + day of week
- Device + session intent

Interaction (viewer x this specific comment):

- Viewer x commenter follow relationship
- Semantic similarity (viewer's comment history vs this comment)
- Viewer's historical engagement with this commenter

Critical distinction: Interaction features 是 per-(user, item) pair, serving 时
每条 candidate 算一次。这是 ranking 比 single-tower retrieval 强大的根源。
==> 下段缝合: comment embedding 喂 L2 ranker 主路；interaction features 在 DCN 风格
cross layer 里和 user embedding 交叉。"

### Section 5.1: Architecture (6 min)

"Funnel:
Pre-filter (toxicity hard filter + dedup, in-storage)  -> 1000 candidates
L1 pre-rank (GBDT, cheap features, weighted target)    -> top 100-200
L2 deep rank (MMOE + shallow bias tower)               -> point-wise scores
Reranker (MMR with hard quota)                         -> top 3
L2 ranker 详细架构 (这是核心):

```
+--------------------------------------------+
| Main tower (Deep + Cross)                  |
|  +- Head 1: engagement                     |
|  +- Head 2: toxicity (also pre-filter)     |
|  +- Head 3: diversity-contrib              |
+--------------------------------------------+
| Shallow bias tower                         |
|  Input: position / popularity / recency    |
|  Output: additive at training              |
|           MASKED at inference  <- 关键     |
+--------------------------------------------+
```

Multi-task 起点: shared bottom + 多 head + 合成 label，升级到 MMOE 只有在 negative
transfer 出现时。Loss weight 由 biz context 锁 (comment 相对 like 的 lift 价值 +
risk budget)，不是 uncertainty weighting -- 因为 weight 本质是产品决策。
Reranker 选择 MMR 不 DPP:

- Why: n=3, list 太短，DPP 的 set-level optimization 没空间体现
- Method: MMR across 3 axes (commenter / sentiment / topic) + hard quota (no 2 same
  commenter, <=1 OP self-reply)
- Future upgrade: DPP with learned kernel when list 扩到 top-10+

==> 下段缝合: 3 head 对应 Section 2 的 3 proxy；shallow tower 实现 Section 3 承诺的 debias。"

### Section 5.2: Training (4 min)

"Loss formulation:

- Engagement head: weighted BCE per signal (或 regression for continuous like dwell time)
- Toxicity head: BCE with strong class weighting
- Diversity-contrib head: pairwise ranking loss
- Per-head monitoring metric: 即使合成 label 训练，每个原始 signal 也单独跑 monitor head
  (不参与 loss)，保持 diagnostic 能力

Negative sampling batch composition (具体比例):
1   positive (exposed + engaged)
: 3-5 exposed-not-engaged (IPS-weighted)
: 1-2 unexposed (from bandit exploration data)
: 0.5-1 hard negative (mined from 上一轮 model 高分但未 engage)
Train/eval split (双轴):

- 主轴 time-based: train [T-30d, T-1d], eval [T-1d, T]
  - Why: freshness-sensitive，random split 会 leak future popularity trend
- 次轴 user-level holdout: 每个时间窗 5% user holdout，测 user generalization
- Feature snapshot: 对齐 train/eval 时间，daily snapshot strategy

Multi-task conflict (engagement vs toxicity):

- 选择: hard constraint via pre-filter + soft penalty in engagement head
- Why not gradient surgery (PCGrad/GradVac): 复杂度不值得
- Why not reward shaping into single label: 保 eval diagnostic 能力

==> 下段缝合: feature snapshot 策略定义 serving 必须 fetch 什么、多新。"

### Section 5.3: Serving (6 min)

"Latency budget (p99 < 200ms):
Candidate retrieve + parallel feature prefetch:   60 ms
Storage-local pre-filter:                         10 ms
L2 ranker (DNN batch 100-200):                    80 ms
Rerank feature fetch + MMR:                       30 ms
Aggregation + serialize:                          20 ms
                                                ------
                                                 200 ms 
关键设计: feature prefetch 在 candidate retrieve 阶段就并行发 RPC，到 ranker 时
feature 已在内存。Reranker 只要 30ms 因为 n=3 时 MMR 几乎免费，主要开销是 sentiment
/ commenter group 的额外 feature fetch。
Tiered refresh strategy (不是一刀切):

| Cadence            | What                                                                    |
|--------------------|-------------------------------------------------------------------------|
| Streaming (1-5 min)| engagement velocity, recent counts, real-time toxicity flag             |
| Hourly batch       | aggregated like rate, cumulative stats                                  |
| Daily batch        | user profile, commenter reputation, topic preference                    |
| At creation        | comment text embedding (compute once, never recompute)                  |
| Daily              | ranker model retrain                                                    |
| Quarterly          | embedding model contrastive retraining                                  |

关键: engagement velocity 必须 streaming，否则 Section 1 承诺的 time-bias mitigation
跑不起来。
Serving-skew prevention (工业标准 2 件套):

- Shadow feature logging: serving 时把实际喂给 model 的 feature 值落盘，offline 训练
  用这份 log，不再重算 -> 唯一彻底防 skew 的方法
- Online-offline feature parity test: 同一个 (user, item) 在 online 和 offline pipeline
  各算一遍，diff > 阈值告警

Cache: hot post results 在 session 开始 cache, 5-min TTL + 新高互动 comment 触发 invalidation。
==> 下段缝合: shadow logging 也是下面 monitoring 段 online-offline metric gap 的 ground truth 来源。"

### Section 5.4: Monitoring + A/B (4 min)

"Model health monitoring (4 个 signal):

- Online-offline metric gap: eval AUC vs online CTR divergence > X% -> alert
  (label leak / distribution shift 早期信号)
- Prediction distribution shift: KL divergence of model output day-over-day
  -> 比 metric 退化更早的 leading indicator
- Feature drift: PSI on top features, hourly
- Engagement metric: 24h moving avg vs baseline

A/B 设计 for top-3 list-level:

- Randomization: user-level (同 user sessions 必须 consistent)
- Metrics:
  - Primary list-level: any-engagement rate in top-3 (不是单条 NDCG/MRR)
  - Secondary: dwell time / reply rate / self-comment rate
  - Guardrails: report rate / toxicity exposure / group fairness
- Ramp: 1% -> 5% -> 20% -> 50%, automatic halt 当任一 guardrail 越界
- North-star (weekly return) measurement: 4-week long-horizon holdout group,
  A/B ramp 决策接受 proxy-based

Abuse / gaming detection:

- 独立模型 (NSFW + relevance + high-risk)，不和 ranker share weights (避免 ranker
  学 abuse pattern 形成 collusion)
- Tiered action:
  - Confident -> hard filter (移出 candidate set)
  - Uncertain -> hard demote (保留在 pool 但不进 top-K)
- Adversarial drift: abuse model precision/recall daily 监控, weekly retrain

Loop closure: monitoring outputs -> (a) training data quality feedback,
(b) abuse model retraining schedule。"

### Closing (30s)

"30-sec recap: viewer-primary top-3 set selection, retrieval bounded (trivial),
2-stage ranking + MMR rerank with hard quota, multi-task MMOE with shallow bias
tower (masked at serve), time + user 双轴 split, tiered feature refresh with
shadow logging for skew defense, list-level A/B with long-horizon north-star
holdout, independent abuse model with tiered action."

---

## Part 5: 通用 Mock 节奏 Checklist (每次开题前过一遍)

### 5.1 开场 60s checklist

- 一句话 scope statement (input / output / objective / constraint)
- 2-3 个 unique twists，每个带 design implication
- Time plan (15 min 前段 + 25 min 后段)

### 5.2 每段进入时 checklist

- 先说 L1 (the dumbest version)，60 秒内
- 再爬阶梯，每层带 trade-off
- 段末做 4 件事: L1 锚定 / 阶梯展示 / trade-off 表态 / 下段缝合

### 5.3 段末 checkpoint 句式

```
To summarize this section:
 - The simplest version is ___
 - Going one level deeper would be ___ (trade-off: ___)
 - I'm choosing to stop at level ___ because ___
 - This connects to Section ___ where I'll use ___
```

### 5.4 Drift 自查 (每段结束扫一遍)

- 没有在当前段讲下一段的内容
- 没有 reverse-drift 回前面段补丁
- 没有用错位术语 (每个技术词原 paper 解决的是当前问题吗?)
- 没有 dodge 具体问题 (被问 X 答 Y)

### 5.5 List-level 题目特殊提醒 (top-K / carousel / multi-slot)

- 开场显式说 "this is a set-selection problem, not pure ranking"
- Metric 段包含 list-level 指标 (diversity / coverage / set satisfaction)
- Architecture 段显式区分 ranker / reranker
- A/B 段用 list-level metric (any-engagement) 而非 NDCG/MRR

---

## Reference appendix — 排序模型 Debias 与特征一致性 (verbatim 用户参考资料 msg 1503874418802163744)

**Fusion point**: Below 8 节内容 is the source for two short segments
embedded into the seeded system_designs row:
- (A) The **Bias Tower 简版** (3-sentence digest of 一/二/三 节) is appended to
  the end of the `architecture` column, with an anchor sentence pointing to
  fr-node `meta-prep/system-design-must-knows/popularity-bias-debiasing` (id=266)
  for the 深入 / 深版 walkthrough.
- (B) The **Shadow Logging + Train-Serve Skew 简版** (4-source digest of 五/六 节
  + 2-piece shadow-logging core) is appended to the end of the `production_constraints`
  column, with the same anchor sentence.
- (C) The **Design Doc 强调话术 4 句金句** (verbatim from 第八节) is appended to
  the end of the `cheat_sheet` column.

### 一、Shallow Bias Tower (YouTube 2019)

**架构**

- 双塔加性结构: `logit = main_tower(content, user, ctx) + bias_tower(bias_features)`
- 主塔深 (MMoE)，偏差塔浅 (1-2 层 / 线性)
- 偏差塔输入只放 bias 类特征: position、device、slot type、isAds 等

**为什么浅**

- 容量瓶颈 -> 只吸收加性偏置，吃不下 content 信号
- 防止 position 抢梯度，逼主塔学真实相关性

**核心归纳偏置**

- 加性可分: relevance + bias，提供可识别性
- 主塔输出天然独立于 position，干净的反事实表达

### 二、Mask-at-Inference

- 训练: bias tower 喂真实 position
- 推理: 屏蔽 bias 项
- 两种等价实现:
  - 把 bias term 整个置 0 (最干净)
  - position 设为固定参考值 (如 1)，bias term 变常数，不影响排序
- 配套训练技巧: 训练时对 position 做 feature dropout，让模型对缺失鲁棒

### 三、Bias Tower vs. 直接当 Feature

| 维度       | Bias Tower             | 拼进主塔                    |
|------------|------------------------|-----------------------------|
| 分解结构   | 加性可分               | content x position 纠缠     |
| 推理 mask  | 良定义                 | 分布外、表示被污染          |
| 梯度竞争   | 主塔学相关性           | position 抢信号             |
| 可识别性   | 强先验                 | 解不唯一                    |

理论等价的前提 (即用工程隐式重建 bias tower): position 随机分布 + dropout + 正则 +
大容量。做齐这些 = 手工搭 bias tower。

### 四、isAds 的判断标准

- 想要 反事实「若为 organic 的相关性」-> 当 bias 处理
- 想要 事实预测 P(click | 当前真实身份) -> 当 context feature

判断点: ads 与 organic 是否只是 logit 加性偏移 (-> bias) 还是有真 interaction (-> feature)。

### 五、Train/Serve Skew

**常见来源**

- 训练/服务代码路径不一致 (Python vs C++)
- Time travel: 训练特征泄漏未来
- 数据源 / 默认值 / null 处理漂移
- bias 特征训练用真实值、serving 用 mask，分布不匹配

后果: 离线指标好、线上掉点

### 六、Shadow Feature Logging

做法: serving 时把模型实际看到的 feature_vector 原样落盘，事后 join label 作为训练样本。

**保证**

- 训练/服务特征 100% 一致 (同一份代码算的)
- Point-in-time 正确，无未来泄漏
- bias 特征 (position / device) 忠实记录，bias tower 训练分布对齐

**工程要点**

- 采样要无偏，避免引入新 bias
- 异步队列 (Kafka / Pub-Sub)，不阻塞 serving
- 流式 label joiner (Flink / Beam) 按 request_id 关联行为
- 持续监控 logged 特征分布 vs serving 实时分布 -> 主动告警 skew

### 七、整体设计内在逻辑链

- 隐式反馈 -> 选择偏差 -> 需 debias
- 模型层: shallow bias tower 剥离 position bias
- 推理层: mask-at-inference 实现反事实预测
- 数据层: shadow logging 消除 train/serve skew，保证 1-3 真正生效

口诀: **架构纠偏 (bias tower) + 推理纠偏 (mask) + 数据纠偏 (shadow log)，三层缺一不可。**

### 八、Design Doc 强调话术

1. 「采用加性 shallow bias tower，结构性强制 relevance / bias 分解」
2. 「Mask-at-inference 提供干净的反事实排序信号」
3. 「Shadow feature logging 保证 bias 特征训练/服务分布一致，避免 debias 机制被 skew 破坏」
4. 「离线 AUC 可能持平甚至微跌，业务指标 (多样性 / 留存 / 新内容曝光) 为真实评估目标」
