# Pinterest ML System Design: Notification Recommendation

> Pinterest ML System Design Interview Prep
> Scope: End-to-end notification reco — triggering, content candidate generation, ranking, delivery constraints, metrics
> Format: 45-min onsite SD loop (clarify 5m, high-level 5m, triggering+CG 10m, ranking 15m, delivery+metrics 10m)

---

## 0. Clarifying Questions (前 5 分钟必问)

面试官抛出 "Design Pinterest Notification Recommendation" 时, 不要直接画图. 先澄清:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| Scale | DAU/MAU? 每日发送 notification 总量? 用户平均接收频次? | 决定 pipeline 规模与 frequency-cap 策略. Pinterest 约 500M MAU, 日发送可达数十亿 |
| Channel | Push (iOS/Android), Email, In-app inbox, SMS? | 不同 channel 成本/SLA/metric 不同 (push 秒级, email 分钟级) |
| Notification type | Engagement (new pin from followed board), Transactional (shopping order), Marketing, Re-engagement (dormant user)? | 决定 触发源 与 ranking 目标 |
| Latency | 必须实时? (event-triggered 秒级) 或批量? (daily digest) | 决定 streaming vs batch 架构 |
| Business goal | Short-term open-rate? Long-term retention? Sessions? | 避免只优化 CTR 导致 spam |
| Constraint | Quiet hours, per-user cap, channel cap, unsubscribe, locale timezone | 决定 delivery layer 硬约束 |
| Cold start | 新用户/dormant 用户怎么办? | 决定 fallback 策略 |
| 负向信号 | Disable-notification rate, uninstall 是否可观测? | 决定是否纳入 loss 以抑制 annoyance |

**假设 (本设计默认)**:
- 500M MAU, 日发送 ~3B push notifications (peak), P99 触发-投递 < 30s
- 4 大类: Engagement / Re-engagement / Transactional / Marketing
- 业务目标: 长期 weekly active user (WAU) + session count, 约束 unsubscribe-rate < 基线
- 3 个核心 channel: mobile push, email, in-app inbox

---

## 1. High-Level Architecture

```
[Event Stream]  [Batch Candidate Builder]      [User Profile Store]
 (new pin,        (dormant user,                 (preferences,
  new follow,      trending topic,                tz, device,
  order, ...)      weekly digest)                 history)
       |                  |                            |
       v                  v                            |
  [Triggering Layer] -- decide WHEN to consider user --+
       |
       v
  [Content Candidate Generation] -- what pins/boards/topics to show
       |
       v
  [Ranking] -- 2-stage: L1 lightweight + L2 multi-task DNN
       |
       v
  [Delivery Constraint Layer]
   - frequency cap (daily/weekly)
   - quiet hours (user tz)
   - channel selection (push > email fallback)
   - dedup against recent sent
   - policy/unsubscribe filter
       |
       v
  [Channel Senders] -- APNs / FCM / SendGrid / inbox DB
       |
       v
  [Feedback Loop] -- impressions, opens, clicks, disables, uninstalls
```

时间分配建议: Triggering 10%, CG 20%, Ranking 35%, Delivery 20%, Metrics+Infra 15%.

---

## 2. Triggering Layer (when to notify)

**核心问题**: 对每个 (user, candidate_event), 决定是否"值得打扰".

### 2.1 两类触发源

| 类型 | 例子 | 架构 |
|------|------|------|
| **Event-driven** (reactive) | 被关注者发新 Pin, 关注的 board 更新, 订单状态, 有人评论你的 Pin | Kafka -> Flink streaming job, fan-out 到订阅用户 |
| **Scheduled** (proactive) | 每周 digest, trending topic 推荐, dormant 用户唤回 | Airflow 每日 batch, 用 user embedding 对候选打分 |

### 2.2 Send/Don't-Send Model (pCTR gate)

即使有触发源, 也不一定发. 在进入 ranking 前, 先用一个 **轻量二分类模型** 做 send/skip 决策:

- Label: 用户在收到 notification 后 24h 内 open=1, 否则 0. 同时训练辅助 head 预测 "会不会 disable"
- Features: user 历史 open-rate, 近 7 天 notification 数, last active time, device online signal, 候选 relevance prior
- Threshold 动态调整: 若用户近 7 天累积发送已接近 cap, 抬高阈值 (budget-aware)

> **Why a dedicated gate before ranking**: ranking 对所有进入队列的候选强行排序会产生过量低质通知. 在 Pinterest 规模下 (日 3B 级), 先用 send-gate 过滤 30-50% 低 pCTR 用户能显著降低成本 + annoyance.

### 2.3 Budget & Pacing
- 全局 budget: 日发送上限 / email 成本 / APNs throttle
- 个人 budget: 每用户 daily/weekly cap (e.g. push ≤ 3/day, ≤ 10/week)
- 使用 **Lagrangian dual** 或简单的 utility/cost ratio 排序, 在 budget 约束内挑最高 utility 的触发

---

## 3. Content Candidate Generation

每次触发后, 需要决定 notification payload — 具体展示哪个 Pin / board / topic / creator.

### 3.1 多源 candidate (per trigger type)

| Trigger | Candidate source |
|---------|-----------------|
| Engagement (followed activity) | 被关注者最新 Pin (近 24h), filter NSFW/dup |
| Re-engagement (dormant) | user long-term interest embedding -> ANN Top-K pins, boosted by trending |
| Weekly digest | user history 最近点击 board 的 related pins + fresh trending in user 语义 cluster |
| Transactional | 固定 payload (order update), 不过 ranker |

### 3.2 Two-tower retrieval for re-engagement
- User tower: long-term interest (7/30 天 repin embedding avg) + demographic
- Item tower: pin embedding (PinSage / Graph-based) + freshness
- Loss: InfoNCE with in-batch negatives + hard negatives (同 interest cluster 但历史 skip)
- Index: HNSW, refresh daily for dormant users; online for active users not needed (reuse home feed CG)
- Size: retrieve top 500 candidates per user, downstream ranker 精排

### 3.3 Multi-item notification (digest)
- Email 可打包 5-10 个 pin. 使用 **submodular selection** (coverage + diversity) 在 ranking 后做 second pass, 避免同一 creator 重复

---

## 4. Ranking

### 4.1 Stage 1: lightweight L1 filter
- 输入: top 500 candidates
- 模型: GBDT (LightGBM), ~30 features (user-pin cosine, creator match, pin age, pin popularity prior, user freshness tolerance)
- 输出: top 50 进入 L2

### 4.2 Stage 2: Multi-task DNN
**Heads** (all sigmoid):
- **pOpen**: 收到后是否会打开
- **pClick**: 打开后是否点击内容
- **pRepin**: 点击后是否 repin (长期 engagement proxy)
- **pDisable**: 是否会关闭 notification (负向, 严厉惩罚)
- **pUnsub**: 是否 unsubscribe

**Architecture**: MMoE (Multi-gate Mixture of Experts), 4-6 experts, 每个 head 一个 gate. 避免 open 与 disable 冲突导致跷跷板.

**Features** (~600):
- User: 历史 CTR, open-by-hour 分布 (时段偏好), notification tolerance (近期 disable rate), embedding, tz, device, locale
- Item: pin embedding, creator embedding, topic, freshness, popularity, safety score
- Context: hour-of-day in user tz, day-of-week, time since last notification, time since last app open
- Cross: user-pin cosine, user-creator affinity, user-topic history, 上次同 topic notification 间隔

**Final utility score**:
```
utility = w_open * pOpen
       + w_click * pClick
       + w_repin * pRepin * repin_value
       - w_disable * pDisable * disable_cost
       - w_unsub * pUnsub * unsub_cost
```
`disable_cost` / `unsub_cost` 取自 LTV (unsub 用户长期收入损失). 权重由 calibration + offline A/B 调.

**Loss**: 每 head BCE, 总 loss 加权和. 负采样: pOpen 用 impression-level (发送过的为正/负), pDisable 用 user-level (过去 30 天是否 disable 过).

### 4.3 Long-term objective via value model
简单 CTR 优化会导致 spam. Pinterest 的做法是训一个 **long-term value model** 预测 "发送这条 notification 后用户未来 7 天 session 数增量" (counterfactual delta, trained from A/B log). 最终排序 blend short-term pOpen + long-term delta.

---

## 5. Delivery Constraint Layer (硬约束, 非模型)

ranking 给出候选排序后, 在投递前还要过一层硬规则:

| 约束 | 规则 |
|------|------|
| Frequency cap | per-user push ≤ 3/day, email ≤ 1/day, inbox 无限 |
| Quiet hours | 在用户 tz 22:00 - 08:00 不发送 push (transactional 例外) |
| Channel selection | 优先 push; 若 device token 失效 或 近 30 天 push open=0, 降级 email |
| Dedup | 近 7 天发过同 pin_id / 同 creator-news 不再发 |
| Safety | NSFW / violent / policy-violating pins 过滤 |
| Unsubscribe | 按 category 检查 (user 可以关某类 marketing 但留 engagement) |
| Regulation | GDPR/CCPA: EU 用户默认 opt-out marketing; 保留 audit log |

实现: 一个 rule engine, 顺序执行, 任一 fail 就 drop. Daily 发送量: trigger 5B -> send-gate 2B -> rank+deliver 1B -> 实际投递 ~800M.

---

## 6. Offline Metrics

| Metric | Purpose |
|--------|---------|
| **Open-rate AUC / PR-AUC** | pOpen head calibration |
| **Disable AUC** | 负向 head, 越高越能识别骚扰 |
| **NDCG@K** (per user per day) | 多候选排序 (digest 场景) |
| **Calibration error (ECE)** | pOpen 概率是否可直接用于 threshold/budget 分配 |
| **Counterfactual uplift** | long-term value model 预测 vs 观测 (IPS-weighted) |
| **Coverage** | 被打通知的 DAU 占比, 避免只打熟客 |

---

## 7. Online Metrics & A/B

**North-star** (primary): **WAU retention** 或 **weekly sessions per user** (7-28 天 window).
> 选 WAU 而不是 open-rate 是因为 open-rate 可以靠 spam 堆高; WAU 是业务真实价值.

**Secondary**:
- Notification open rate, CTR
- Repin rate from notification traffic
- Session depth after notification open

**Guardrails** (必须不 regression):
- Daily **unsubscribe rate**, **disable-notification rate**
- **Uninstall rate** (Android 可观测, iOS 受限)
- Complaint / spam report rate
- Email bounce / spam-folder rate

**A/B setup**:
- 随机分桶 (user-level, sticky), 至少 2 周观测 retention
- Holdout group: 完全不发 notification 的 1% 用户, 长期保留, 用于计算 notification 整体增量价值
- 分 channel 子实验 (push vs email vs 组合)

---

## 8. Infrastructure & Capacity

### 8.1 Feature Store
- **Online**: RocksDB + in-memory cache (user features 500ms SLA)
- **Offline**: Feature generation via Spark, daily + hourly partial refresh. 保证 train/serve skew ≤ 1%.
- Real-time features (last_app_open, recent_disable) via Flink -> online KV

### 8.2 Training pipeline
- Daily full retrain + hourly incremental on recent engagement
- Training data 按 impression-join (发送 + 24h 标签拼接). 注意 label delay (有些 open 可能在 3 天后发生, window 设 3-7 天)
- Model size: MMoE ~100M params, FP16 serving

### 8.3 Serving
- Triggering + send-gate: Flink streaming (event) + Airflow (batch)
- Ranking: TF serving cluster, batch inference 32 candidates/req, P99 < 50ms
- Delivery: rule engine + channel queue (APNs batch 100 tokens/req, email via SendGrid)

### 8.4 Capacity math (sanity check)
- 3B candidates/day -> send-gate keep ~30% -> 1B rank -> 800M deliver
- Ranking QPS peak: 1B / 86400 * 3 (peak factor) ≈ 35K QPS, 每 req 50 candidates => ~1.75M scores/s. 需要 ~100-200 GPU instances.
- Storage: user profile 500M users * 2KB ≈ 1TB; pin embedding 5B * 64 * 4B = 1.2TB on disk

---

## 9. Cold Start

| 场景 | 策略 |
|------|------|
| 新用户 (注册 < 7 天) | 用 onboarding interest + demographic; 初期 **降低发送频次**, 观察 tolerance. 只发高置信 engagement |
| Dormant (30+ 天不开 app) | Re-engagement campaign, 但 cap 到 1/week, 使用 long-term interest embedding + trending |
| 新 pin (< 1h) | freshness boost + creator popularity prior 代替 CTR |
| 新 creator | follower graph + topic prior |

---

## 10. Failure Modes & Mitigations

| 失败 | 影响 | 缓解 |
|------|------|------|
| Ranker 过拟合 short-term open -> spam | Disable rate 上升, 长期 retention 下降 | Long-term value head + disable penalty + holdout monitor |
| Feature skew (online/offline) | AUC 跌 | Feature store version lock + daily skew report |
| Channel outage (APNs 挂) | 降级 | Email/inbox fallback; 累积的高 utility 通知延迟发 (< 24h) |
| Timezone bug | 半夜打扰 | Quiet-hours 在 delivery layer 硬校验 + 单元测试覆盖极端 tz |
| Bot/abuse (fake creator 触发 notification) | Spam 用户 | Creator trust score gate, 低 trust 不进 engagement 触发 |
| Label delay | 训练数据偏差 | 固定 3-7 天 label window + incremental fine-tune |
| Lagrangian budget 漂移 | 某天超发 | 每小时更新 threshold, 限 max send/hour |

---

## 11. Likely Follow-ups (面试官追问)

1. **"How do you balance engagement vs annoyance?"** — Long-term value head + disable/unsub penalty + 1% holdout group 长期监控净增量.
2. **"A user just disabled notifications. What do you change?"** — 立即停所有 non-transactional; 30 天后通过 in-app prompt 询问是否恢复.
3. **"Why two-stage ranking (L1+L2)?"** — L1 GBDT 剔除 90% 低质候选成本低 (~1ms), L2 MMoE 精度高但重 (~30ms), 联合达到成本/精度最优.
4. **"How do you prevent filter bubble?"** — Diversity head + submodular selection + exploration bucket (epsilon-greedy).
5. **"How would you onboard a new notification type (e.g. shopping price drop)?"** — 新触发源 + 新 label head (shopping conversion) + 独立 holdout + gradual ramp.
6. **"What if the model says send, but user is offline?"** — Device online signal feature; 离线 push 会排队到上线, 若超过 24h TTL 则丢弃.
7. **"How do you attribute a session to a notification?"** — Click ID + 30-min attribution window; 对照 holdout 计算增量.

---

## 12. 45-Minute Timing Template

| 分钟 | 内容 |
|------|------|
| 0-5 | Clarify (scale / channel / goal / constraint) |
| 5-10 | High-level diagram + 画 triggering -> CG -> rank -> delivery |
| 10-20 | Triggering (event vs scheduled) + send-gate + CG (two-tower for re-engagement) |
| 20-35 | Ranking (MMoE heads, 尤其 disable/unsub, long-term value) |
| 35-42 | Delivery constraints, metrics (WAU + guardrails), A/B + holdout |
| 42-45 | Follow-up / trade-offs (engagement vs annoyance) |

---

## Appendix: Key Differentiators vs Feed Ranking

| 维度 | Feed Ranking | Notification |
|------|-------------|--------------|
| 发起方 | 用户主动打开 | 系统主动打扰 |
| 负向成本 | 低 (划走即可) | 高 (disable/uninstall, 几乎不可逆) |
| 候选规模 | 千万级/req | 几十级/trigger |
| Latency | < 500ms | 秒级~分钟级 |
| 核心指标 | Session engagement | Long-term retention (WAU) |
| 关键约束 | Diversity | Frequency cap + quiet hours + budget |

> 面试亮点: 点出 notification 是 **push product** (系统主动), 与 **pull product** (feed/search) 在负向成本与指标选择上根本不同, 这是最常被忽略但面试官最想听的观点.
