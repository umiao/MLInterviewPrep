# Pinterest ML System Design: Ad CTR Prediction

> Pinterest SD 2025-11 onsite 题目: "Design CTR prediction for Pinterest ads"
> Scope: 从 impression/click 日志 → 特征 → 模型 → 校准 → 在线 serving → 监控, 端到端
> Format: 45-min SD loop (clarify 5m, data+label 8m, feature 8m, model 10m, calib+serving 8m, metrics+followup 6m)

---

## 0. Clarifying Questions (前 5 分钟必问)

"Design Pinterest Ad CTR" 之前先对齐 scope, 避免跑偏:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| Ad 形态 | Promoted pin? Shopping ad? Video ad? Carousel? | 不同形态的 creative feature 与 label 定义不同 |
| Surface | Home feed / search / related pins / shopping tab? | 不同 surface 分布差异大, 需要 surface-aware 特征或分模型 |
| 目标 | pCTR used for ranking? pricing via **optimized Cost Per Mille** (oCPM, 优化千次曝光出价)? budget pacing? | 决定是否必须 calibrated (pricing 必须, pure ranking 可不必) |
| Click 定义 | repin 算 click? closeup? outbound click (到广告主落地页)? | 决定 label source 与 attribution 窗口 |
| Scale | 每日 impression? QPS peak? 广告主数? | 500M MAU × 10 ad impr/session × 2 session/day ≈ 10B impr/day; peak ~150K QPS pCTR |
| Latency | Ranking SLA? | 典型 ad scoring P99 < 80ms (在 organic ranker 之后, 时间预算紧) |
| Fairness / policy | 新广告主 cold start? 预算 pacing? | 决定是否需 explore 机制 (ε-greedy / Thompson) |

**本设计假设**:
- Promoted pin (静态图/视频) 在 home feed + search surface, oCPM 计费 ⇒ pCTR **必须校准**
- Click = outbound click (点击广告到落地页), 归因窗口 24h post-click / 1h post-view
- 10B impr/day, peak 150K QPS scoring, P99 < 60ms ad ranker budget
- 冷启动: 新广告 < 1000 impressions 进入 explore 桶

---

## 1. High-Level Architecture

```
[User request /v3/home_feed] ──► organic ranker ──► slot allocator
                                                       │
                                              (1 in N slots 是 ad)
                                                       ▼
                                              [Ad Candidate Generation]
                                                       │  (targeting + budget filter: ~2k ads)
                                                       ▼
                                              [Ad L1 Light Ranker]  (GBDT, 2k→200)
                                                       │
                                                       ▼
                                              [Ad L2 Heavy Ranker]  (DeepFM / AutoInt, pCTR head)
                                                       │
                                                       ▼
                                              [Calibration layer]  (isotonic per surface)
                                                       │
                                                       ▼
                                              [eCPM = bid × pCTR × pCVR] + pacing multiplier
                                                       │
                                                       ▼
                                              [Auction (GSP / VCG)] → winner inserted into slot
                                                       │
                                   ┌────────────────────┼────────────────────┐
                                   ▼                    ▼                    ▼
                              [Impression log]    [Click log]          [Conversion log]
                                   │                    │                    │
                                   └──── Kafka ──► Spark joiner (attribution window) ──► Training data
```

Side infra:
- **Feature store**: Online = Redis + RocksDB shard (user features TTL 1h, ad features TTL 10m); Offline = Iceberg on S3
- **Embedding service**: user/pin/advertiser embeddings refreshed daily (Flink streaming for near-real-time user emb)
- **Training**: TF/PyTorch distributed on GPU, daily incremental + weekly full retrain
- **Serving**: Triton GPU for L2, CPU for L1 + calibration

---

## 2. Data Pipeline & Label Construction

### 2.1 事件流 (source of truth)
- **Impression event**: 广告真正曝光 (viewability ≥ 50% pixel × 1s) 才打点, 避免统计噪声
- **Click event**: outbound click (带 ad_request_id 回传到 server)
- **Conversion event**: 广告主 pixel 或 Pinterest tag 回传 (add-to-cart / purchase), 延迟可达数天

### 2.2 Join / Attribution
```
impression(request_id, user, ad, ts, context)  ─┐
                                                 ├─► Spark outer join on (request_id, ad_id)
click(request_id, ad_id, ts)                   ─┘      window: [impr_ts, impr_ts + 1h]
                                                 │
                                                 ▼
                                       labeled example: y ∈ {0,1}
```

**关键陷阱**:
- **Positive delay**: click 可能比 impression 晚几十秒到几分钟到达 ⇒ 不能用 impression 流实时生成负样本. 做法: **等 1h window close 后** 再固化 label (Criteo delayed feedback 论文的做法).
- **Feedback loop**: 模型推荐的广告才会被曝光 → 训练集 biased. 补偿: 在 serving 层对随机 (1%) 曝光记录做 explore 桶, 用于 unbiased eval + importance-weighted retraining.

### 2.3 采样
- Positive rate 典型 ~1-2%, 严重 imbalance. **负采样 1:5 或 1:10**, 训练时对 positive 加权 (或 focal loss); inference 时校准补偿 prior shift.
- 负采样公式: 原始 p₀ = clicks / impressions, 采样后 p' = clicks / (clicks + α·non_clicks). 校准: p̂ = p' / (p' + (1 − p') / α).

---

## 3. Feature Engineering

### 3.1 四大特征族
| 类别 | 示例 | 存储层 |
|------|------|--------|
| **User** | age_bucket, locale, device, historical CTR, last-7d category affinity vec, PinnerSage emb (64d) | Redis user-key |
| **Ad / Creative** | advertiser_id, campaign_id, pin_emb (PinSage 64d), creative text emb, image CLIP emb, past CTR (smoothed) | RocksDB ad-key |
| **Context** | time-of-day, day-of-week, surface, slot_position, device, connection_type | Request-time |
| **Cross** | user×ad category match, user×advertiser prior clicks, query×ad (search surface) | 在线拼接 |

### 3.2 特征工程关键点
- **Smoothing 低频 ID**: 新广告 CTR = (clicks + α·prior) / (impr + α), α ≈ 100, prior = 同 category 平均 CTR. 避免 1/1 = 100% 的假信号.
- **Hash trick**: advertiser_id 百万级 → hash 到 2M buckets, 减少 embedding table 大小.
- **Count features 用 log 变换**: log(1 + ad_past_impr), 避免长尾支配梯度.
- **Position bias**: slot_position 作为特征喂进 shallow tower, serving 时固定为 "position=1" (或积分期望). 避免 model 学到 "位置高 → CTR 高" 的伪因果 (见 YouTube 2019 论文).

### 3.3 特征一致性 (train/serve skew)
- **同一个 feature fetcher**: 训练和 serving 共享同一段 feature extraction code (protobuf schema + 共享 feature lib), 避免 pandas vs C++ 实现差异.
- **Point-in-time correctness**: 训练时 join 必须用 impression 时刻的 user state, 而不是当前 state. 做法: feature store 写 log-structured, 按 ts 回查.

---

## 4. Model

### 4.1 L1 light ranker (2k → 200)
- **Gradient Boosted Decision Trees** (GBDT, 梯度提升决策树) — 实现用 **LightGBM** (Microsoft 2017 高效梯度提升库) — 或 2-tower dot product. ~100 特征, P99 < 5ms.
- 目标: recall 高, 不要 drop 真正好的 ads; 对 pCTR 绝对值精度要求低.

### 4.2 L2 heavy ranker — DeepFM / AutoInt
选择对比:
| 模型 | 优势 | 劣势 |
|------|------|------|
| **Wide & Deep** (Google 2016 推荐架构, 宽-深双路并联) | 简单, wide 部分可解释 | cross 特征需手工 |
| **DeepFM** | **Factorization Machines** (FM, 因子分解机) 自动学 2nd-order cross + DNN 学高阶 | 2nd-order 之外的交叉效率一般 |
| **Automatic Feature Interaction Learning** (AutoInt, 自动特征交互) | multi-head self-attention on features, 自动学高阶交叉 | 训练慢, 解释性差 |
| **Deep & Cross Network v2** (DCN-v2, 深度与交叉网络 v2) | 显式 cross layer + DNN, Google 线上验证 | 参数量大 |

**推荐**: DeepFM 或 DCN-v2 作为 baseline, AutoInt 作为 A/B 候选.

**结构**:
```
sparse features ─► embedding tables (each id → 16d)
                      │
                      ├─► FM second-order (pairwise dot) ─────┐
                      │                                        │
                      └─► concat → DNN [512, 256, 128] ──► ───┤
                                                               ▼
dense features (counts, age, bias) ────────────────────► concat → logit → σ → pCTR
                                                               │
position bias tower ──────────────────────────────────────────┘
```

- **Loss**: **Binary Cross-Entropy** (BCE, 二元交叉熵), 即 BCE(y, σ(logit)). 考虑 focal loss 缓解 class imbalance.
- **Multi-task**: 共享 bottom, 分别 head pCTR / **predicted Conversion Rate** (pCVR, 预估转化率) / pCloseup, 用 MMoE 或 PLE 动态路由. 好处: 更好 generalize, 对 sparse conversion 标签更 robust.

### 4.3 训练
- Daily incremental fine-tune (昨日数据), weekly full retrain (过去 30 天).
- Distributed: 8-GPU synchronous AllReduce; embedding table 太大 (数十 GB) 用 ParameterServer 或 DeepRec sparse storage.
- **Continual learning**: warm-start from yesterday's weights, 小 learning rate, 避免旧广告 embedding 被新数据冲掉.

---

## 5. Calibration

oCPM 计费要求 pCTR 是**概率** (期望频率), 不仅是 ranking score. 未校准模型的 logit 只保证序, 不保证值.

### 5.1 为什么会不校准
- Negative down-sampling → pCTR 整体偏高
- Focal loss / class weighting → 扭曲概率
- Covariate shift (serving 分布 ≠ 训练分布)

### 5.2 方法
| 方法 | 适用 | 公式 |
|------|------|------|
| **Platt scaling** | logit 平移缩放, 简单 | p̂ = σ(a·logit + b), (a,b) 在 holdout 上 MLE |
| **Isotonic regression** | 非参, 分段单调, 更灵活 | 按分桶中位数拟合单调函数 |
| **Beta calibration** | sigmoid 的 3-param 推广 | 对 logit 尾部更稳 |

**推荐**: isotonic per (surface × country), 每日重拟合. 对特殊人群 (冷启动用户) 单独 bucket.

### 5.3 校准指标
- **Expected Calibration Error (ECE)**: ECE = Σᵢ (|Bᵢ|/N) · |acc(Bᵢ) − conf(Bᵢ)|
- **Calibration ratio** Σ predicted / Σ actual, 目标 ≈ 1.0 ± 5%.
- **Reliability diagram**: 分 20 桶可视化 pCTR vs 实际 CTR.

### 5.4 负采样后补偿
若训练用 1:α 负采样 (keep α fraction of negatives), 推理后再做 prior correction:
p̂ = p' / (p' + (1 − p') / α)
放在 calibration 之前或合并到 Platt 的 bias.

---

## 6. Serving

### 6.1 延迟预算 (P99 60ms)
| 组件 | 预算 |
|------|------|
| 广告 candidate gen (targeting + budget filter) | 10ms |
| Feature fetch (user + ad + context) | 15ms |
| L1 ranker | 5ms |
| L2 ranker (Triton GPU batch) | 20ms |
| Calibration + eCPM + auction | 5ms |
| 余量 / overhead | 5ms |

### 6.2 Feature store
- **User features**: Redis cluster, TTL 1h; 近实时信号 (最近点击 pin) 通过 Flink 直接写 Redis.
- **Ad features**: RocksDB (持久化, advertiser 百万级), 每 10min 从 offline ETL push 新 ad 条目.
- **Online-offline 一致性**: dual-write 到 Kafka, Spark 消费后固化; 所有 feature 读都打 metric (cache hit, staleness).

### 6.3 模型部署
- Triton / TF-Serving, 每次上线新模型前 **shadow traffic 1 天**, 比较 pCTR distribution + offline replay **Area Under ROC Curve** (AUC, ROC 曲线下面积).
- Canary 1% → 5% → 50% → 100%, 每阶段自动 guardrail 检查 (calibration ratio, ECE, CTR).
- **Embedding hot reload**: 新广告 embedding 每 10 min 增量 push, 不用重启服务.

---

## 7. Online Metrics & Monitoring

### 7.1 核心指标
| 指标 | 公式 | 用途 |
|------|------|------|
| **LogLoss (NLL)** | −1/N Σ [y·log p̂ + (1−y)·log(1−p̂)] | 整体模型质量 |
| **Normalized Entropy (NE)** | LogLoss / H(p̄), p̄ = 平均 CTR | 对 base rate 归一, Facebook 标准 |
| **AUC** | 排序能力 | 仅 ranking, 不反映 calibration |
| **Calibration ratio** | Σ p̂ / Σ y | oCPM 健康度 |
| **ECE** | 见 §5.3 | 分桶校准误差 |

### 7.2 业务指标 (A/B)
- Ad CTR, advertiser ROAS, Pinterest revenue per mille (RPM)
- Guardrail: organic session length, hide rate, negative feedback ratio — 广告模型改动**不能**显著伤害 organic engagement.

### 7.3 监控告警
- **Feature drift**: PSI (Population Stability Index) > 0.2 告警.
- **Prediction drift**: 每 5min 计算 serving pCTR 分布, 与昨日同时段比较, **Kolmogorov-Smirnov test** (KS-test, KS 检验) 阈值.
- **Calibration monitor**: hourly calibration ratio, 偏离 [0.9, 1.1] 报警 → 触发 isotonic 重拟合.

---

## 8. Follow-ups (面试官常追问)

1. **Cold start 新广告**: 前 1000 impressions 进 explore 桶 (Thompson sampling on Beta prior), 同时用 creative embedding (image + text) 做 warm-start.
2. **Delayed feedback** (长尾 click): 参考 Criteo 2014 delayed feedback model — 每个 example 带一个 delay distribution, 联合训练 click prob 与 delay prob.
3. **Position bias 校正**: training 用 position feature, serving 固定 position=1; 或用 **Inverse Propensity Scoring** (IPS, 逆倾向加权).
4. **Budget pacing**: pacing_multiplier 在 eCPM 之外, 由独立 PID 控制器根据剩余预算 + 剩余时间调整; 不混入模型.
5. **Exploration vs exploitation**: ε-greedy 或 UCB 给新 creative 机会; 记录 explore bucket 作为 unbiased holdout.
6. **Multi-objective** (CTR + CVR + long-term value): MMoE 多头, 加权求和 (权重由业务负责人定), 或用 Pareto 前沿作为候选集.
7. **隐私与合规**: 无 PII 进模型; IDFA / GDPR 下的 contextual-only fallback 模型; 训练数据脱敏 + k-anonymization.
8. **Train/serve skew 调试**: 在 serving 中采样 1% 请求记录完整 feature vector + score, offline replay 对比训练管道同一条 example 的 score, 差异 > 1e-6 则报警.

---

## 9. 常见面试对话 snippets (中文)

**Q: 为什么要校准? AUC 高不够吗?**
A: AUC 只看排序. oCPM 计费下 eCPM = bid × pCTR, 若 pCTR 整体偏高 2×, 广告主被多扣钱; 偏低则广告主少花预算, Pinterest 损失 revenue. 所以必须校准到真实概率.

**Q: DeepFM 比 Wide&Deep 好在哪?**
A: W&D 的 wide 部分需要人工设计 cross features (如 user_country × ad_category); DeepFM 用 FM 自动学所有 field 的二阶交叉 embedding, 省掉手工特征工程, 对长尾组合也能泛化.

**Q: 新广告 cold start 怎么办?**
A: 三层: (1) creative embedding 共享 (image/text emb 的 similar 广告历史 CTR 作先验); (2) hierarchical smoothing (advertiser / category / global prior); (3) explore bucket 给 1-5% 流量保证数据回流.

**Q: 如果发现线上 CTR 比预测低 20%?**
A: 排查顺序: (1) calibration ratio 是否漂移 → 重拟 isotonic; (2) feature 分布漂移 (PSI); (3) train/serve skew (feature fetch bug); (4) 用户行为真实下降 (check organic CTR 同步变化).
