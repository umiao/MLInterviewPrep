# Uber ML System Design Golden Answers (Staff-Level)

> **Source**: 2026-04 Uber VO 复盘整理 (Round 3 ML System Design 两道核心 Staff-level Golden Answers)
> **Scope**: 2 道核心 ML System Design 题 — Uber Eats 餐厅推荐系统 + Budget-Constrained Promo Recommendation System (uplift × constrained optimization).
> **Style**: 中文叙述 + 英文术语 (English term first, 中文 in parens for first occurrence). 行业黑话 (industry jargon) 用 **bold** 标出, 每个架构决策给出 trade-off 论证. ASCII 架构图用 code-fence, 数学公式用 `$$...$$`.
> **Anchors**: 每个 H2 都用 kebab-case stable HTML id, 供 T-P0-632 的 deep-link 使用 (`/docs/<doc-id>#<anchor>`).

---

## 目录 (Table of Contents)

1. [Uber Eats 餐厅推荐系统 (Restaurant Recommendation)](#uber-eats-restaurant-rec)
2. [Budget-Constrained Promo Recommendation (uplift × Lagrangian)](#budget-promo-recommendation)
3. [跨题通用 Senior 信号速查表 (Cross-cutting Senior Signals)](#cross-cutting-senior-signals)

---

<h2 id="uber-eats-restaurant-rec">1. Uber Eats 餐厅推荐系统 (Restaurant Recommendation)</h2>

> **题目 (Problem)**: 设计一个 Uber Eats 的餐厅推荐系统 (Restaurant Recommendation System).
> **目标 Level**: Staff (L6) 水准的回答.
> **答题节奏**: 这份 Golden Answer 按真实面试推进顺序展开 — 阶段 0 心态 → 阶段 1 需求澄清 → 阶段 2 规模估算 → 阶段 3 high-level 架构 → 阶段 4 deep dive → 阶段 5 senior 加分项 → 阶段 6 一页纸记忆卡.

### 1.0 阶段 0 · 心态与节奏 (30 秒内说完)

> "我先用 3-5 分钟把需求 (requirements) 和 scope 定下来, 然后做规模估算 (back-of-envelope), 再给一个 high-level 架构. 架构出来后我们挑 1-2 个组件做 deep dive. 如果中途你想调整方向, 随时打断我."

**为什么说这句**: 开场就主导节奏, 体现 senior 对面试结构的把控. **面试官最怕的是"看不到候选人的思路框架"** — 这句开场把整个 60 分钟的 outline 摊开放在桌上.

---

### 1.1 阶段 1 · 需求澄清 (Functional / Non-Functional / Out-of-Scope)

#### 1.1.1 用户场景与产品定义

> "我先确认产品形态: 这是 Uber Eats App **首页的『为你推荐』模块** (home feed personalized module), 用户打开 App 看到的个性化餐厅 feed. 我假设这是一个 ML-driven 的个性化模块, 区别于 rule-based 的『再来一单』(reorder)、『附近热门』(nearby popular) 这些非个性化模块 — 后者我们承认存在但不展开."

**澄清问题清单 (主动提假设, 而不是问开放题)**:

| 维度 | 我的假设 | 等待确认 |
|---|---|---|
| Feed 形态 | 主页 grid/carousel, ~30 个候选, 可 "show more" 进入完整推荐页 | 待确认 |
| 个性化粒度 | Per-user 个性化, 结合 location + time-of-day + history | 待确认 |
| 配送半径 | 城市核心 3-5mi, 郊区 ~10mi (**注意: 不是 20mi, 外卖半径很短**) | 待确认 |
| 实时性 | 首屏推荐预计算, **不要求 in-session 实时更新** (用户滑动时不重新 rank) | 待确认 |
| 广告 | sponsored items 不在本次 scope 的竞价机制内 | 待确认 |

#### 1.1.2 Non-Functional 需求

> "延迟方面: home feed 是首屏, **P99 服务端延迟 \< 200ms**, 加网络渲染用户感知 ~500ms. 这个 budget 比较紧, 所以我会倾向**尽量预计算** (pre-compute) — 后面架构里会体现."
>
> "可用性 99.95%+. **Graceful degradation** (优雅降级) 是必须的 — 任何一路 feature service 挂了, 系统要能 fallback 到默认值或 popularity-based 推荐, 不能整体不可用."

#### 1.1.3 Success Metrics (这块要主动讲, 体现产品 sense)

> "成功指标分两层:
>
> **Product metrics**:
> - **Module CTR (Click-Through Rate)**: feed 内餐厅点击率
> - **CVR (Conversion Rate)**: 从 feed 点击到下单的转化
> - **Module adoption rate**: 多少用户用 home feed 而不是直接走 search
> - **Abandonment rate**: 用了 feed 但没下单, 转头去 search 的比例 — 这是 home feed 失败的核心信号
>
> **Business metrics**:
> - **GMV (Gross Merchandise Value) per session**
> - **Search efficiency lift**: home feed 是否分担了 search 的负载 (和 search bar compete 的 framing)
> - 长期 retention / DAU"

#### 1.1.4 Out-of-Scope (明确划出去)

- In-session 实时 rerank
- Search bar 的 query understanding (NER / rewrite)
- Sponsored items 的广告竞价机制 (ad auction)
- Driver/courier 调度系统 (虽然 ETA 会用到它的输出)

---

### 1.2 阶段 2 · 规模估算 (Back-of-Envelope)

#### 1.2.1 流量

```
DAU              ~50M (全球)
平均请求/用户/天   ~1.2 (打开 App 频次)
平均 QPS          50M * 1.2 / 86400 ~= 700 QPS

峰值倍数          5-8x  <- 注意: 外卖是 traffic 最 peaky 的产品
                        lunch (11-13) + dinner (18-21) 双峰
                        时区跨度叠加 (美东 dinner ~= 美西 lunch 后)
峰值 QPS          ~5K-10K
```

**这里的关键洞察**: 外卖比一般电商 peakier, **capacity planning 要按 8x 峰值预留**, 缓存策略也要考虑 lunch/dinner 集中失效问题.

#### 1.2.2 读写比

```
每次 home feed 渲染 = 1 read + ~30 impression logs + 0-3 click logs + 0-1 order log
读写比 ~= 1:30+   <- 写远多于读
```

**关键洞察**: 不能按 read-heavy 系统设计, **logging pipeline 是核心组件**, 不是 nice-to-have.

#### 1.2.3 候选规模

```
单用户可达餐厅 (3-5mi 半径) ~300-1000 家
Candidate generation 输出   ~500-1000
Coarse ranking 输出         ~100-200
Fine ranking 输出           ~30-50
最终 feed 展示              ~30
```

#### 1.2.4 存储

| 类别 | 规模 | 备注 |
|---|---|---|
| 餐厅 metadata | ~1M 餐厅 * 几 KB ~= 几 GB | 在线 KV |
| 餐厅 embedding | 1M * 256d float32 ~= 1GB | ANN index |
| 用户 embedding | 200M users * 1KB ~= 200GB | 分热冷 |
| User-item interaction | TB 量级 | 热数据 Cassandra, 冷数据 HDFS |
| **训练数据日志** | **~TB / day** | **真正的存储大头** |
| 餐厅图片 | 不在推荐系统存储里, CDN 引用 URL | — |

**关键洞察**: **ML 系统的存储瓶颈是训练数据 pipeline, 不是 serving 数据.** 这是和普通 CRUD 系统的最大区别.

---

### 1.3 阶段 3 · High-Level 架构

```
+-----------------------------------------------------------------+
|                         CLIENT (App)                             |
+------------------------------+----------------------------------+
                               |
                    +----------v----------+
                    |  API Gateway / BFF  |
                    +----------+----------+
                               |
                    +----------v----------+
                    |   Feed Service      |  <- orchestrator
                    +----------+----------+
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
 +-------------+      +----------------+    +----------------+
 | Context     |      | Feature Store  |    | Restaurant     |
 | Assembly    |      | (Online KV)    |    | Availability   |
 | user/loc/   |      | user feat,     |    | (real-time)    |
 | time/device |      | item feat,     |    | open? ETA?     |
 +------+------+      | context feat   |    +--------+-------+
        |             +--------+-------+             |
        |                      |                     |
        +----------+-----------+---------------------+
                   |
        +----------v--------------+
        | Candidate Generation     |  -> ~500-1000 candidates
        | +---------+-----------+  |
        | |Geo (H3) |ANN(2-tower)| | <- multi-channel retrieval
        | |Inverted | Popular    | |
        | +---------+-----------+  |
        |  + Hard filter:          |
        |    "is open / accepting" |  <- dead-click 防护
        +----------+---------------+
                   |
        +----------v----------+
        |  Coarse Ranker      |  -> ~100-200
        |  (LR / GBDT /       |
        |   2-tower light)    |
        +----------+----------+
                   |
        +----------v----------+
        |  Fine Ranker        |  -> ~30-50
        |  (DIN / DeepFM /    |
        |   MMoE multi-task)  |
        |  特征已通过 snapshot|
        +----------+----------+
                   |
        +----------v----------+
        |  Re-ranker          |  -> ~30
        |  - Diversity (MMR / |
        |    DPP)             |
        |  - Business rules   |
        |  - Extreme ETA      |
        |    hard filter      |
        |  - Cold-start boost |
        +----------+----------+
                   |
                   v
              [Feed Response]
                   |
                   v
        +--------------------------------+
        |  Logging / Feature Snapshot    |  <- 关键: snapshot 在 serving 时
        +----------+---------------------+
                   |
        +----------v-------------+
        |  Streaming(Kafka/Flink)|
        |  - Near-line features  | -> 回写 Feature Store
        |  - Real-time signals   |
        +----------+-------------+
                   |
        +----------v-------------+
        |  Offline (Spark/HDFS)  |
        |  - Training data prep  |
        |  - Model training      |
        |  - Embedding refresh   | -> 推回 ANN index
        |  - ANN index rebuild   |
        +------------------------+
```

#### 1.3.1 三层时间尺度 (这是 senior 信号)

| 层 | 更新频率 | 例子 |
|---|---|---|
| **Offline (batch)** | 小时 / 天 | 餐厅 embedding、用户 long-term embedding、ANN index |
| **Near-line (streaming)** | 秒 / 分钟 | 用户最近点击、餐厅 ETA、busy 程度、surge |
| **Online (request-time)** | 毫秒 | Ranking inference、context feature、availability filter |

**外卖场景的特殊性**: 餐厅"是否还接单 / 当前 ETA"秒级变化, 所以 **near-line 这层不能省**. 这是和 Netflix / Amazon 推荐系统的核心区别 — 后者的物品供给是稳定的, Uber Eats 的物品 (餐厅) 供给 (是否接单) 是分钟级动态的.

---

### 1.4 阶段 4 · Deep Dive

#### 1.4.1 Candidate Generation 多路召回

**多路召回策略 (multi-channel retrieval)**:

| 召回路 | 算法 | 输出量 | 用途 |
|---|---|---|---|
| Geo | **H3** hexagon index (Uber 自家开源) | ~1000 | 距离硬约束 |
| Embedding ANN | **Two-tower model** + HNSW / IVF | ~500 | 个性化语义匹配 |
| Inverted index | 类目 / 标签倒排 | ~200 | 显式偏好 (爱吃日料) |
| Popularity | 地域 + 时段热门 | ~100 | 兜底 + 冷启动 |
| Recent interaction | 用户最近交互过的店 + 相似店 | ~100 | 短期兴趣 |

**为什么用 H3 而不是 geohash** (**Uber 面试必答**):

- **H3 是 Uber 自己开源的六边形地理索引系统** (hexagonal hierarchical geospatial indexing system).
- Hexagon 邻居距离均匀 (geohash 方形 grid 对角邻居距离 $\sqrt{2}$ 倍于边邻居).
- 没有 geohash 的边界突变问题 (物理相邻点的 prefix 可能完全不同).
- 多分辨率友好, level 7-9 适合外卖半径.

> 提到 H3 的话术: "考虑到这是 Uber 的题, 我会用 H3 — Uber 自己开源的 hexagonal grid system, 邻居距离均匀, 避免 geohash 的 boundary discontinuity 问题."

**Two-tower model** (**行业黑话 #1**: 双塔模型) — user / item 两个独立 encoder 共享 embedding 空间:

```
User Tower:  user features + history -> user embedding (256d)
Item Tower:  restaurant features     -> restaurant embedding (256d)
Loss:        in-batch sampled softmax / contrastive loss

Serving:
  - User tower 在线 inference (<10ms)
  - Item tower 离线 inference, 结果灌进 ANN index (HNSW)
  - Query: user emb 在 ANN 找 top-K
```

**多路 merge 策略**:

> "两个选项:
> 1. **Unified ranking**: 各路只输出 candidate id, 不带 score, 全交给 coarse ranker 重打分. 优点是无需 calibration.
> 2. **Quota allocation**: 每路给配额 (geo 40%, embedding 30%, popular 10% 等). 适合各路 score 难统一 calibrate 的情况.
>
> 我倾向 #1, 因为下游有 ranker, 让 ranker 学习总比手工调配额好. 但冷启动场景下 #2 更稳."

**Sharding vs IVF (常见混淆点)**:

- **Sharding**: 按城市 / region 切分索引. 纽约用户永远不查旧金山 — **地理天然分片**, sharding key 干净.
- **IVF (Inverted File Index) / HNSW (Hierarchical Navigable Small World)**: shard 内部的 ANN 加速算法. 两个**都要做**, 不是替代关系.

**冷启动 (cold-start)**:

- 新店: 用 metadata (菜系、价位、地段) 映射到已有店 embedding 做初始化 (**content-based bootstrap**).
- 探索预算: **Thompson sampling / UCB bandit**, 给新店一定 impression 预算积累数据.
- 业务策略: 可以给"新店扶持"硬扶持权重, re-ranking 阶段加成.

---

#### 1.4.2 Ranking Model + Feature Pipeline

**Fine Ranker 模型**:

> "我会选 **MMoE (Multi-gate Mixture-of-Experts)** 做多目标, bottom 用 DIN-style attention 处理用户行为序列."

**MMoE vs MoE 的区别 (常见追问点)**:

- **MoE (Mixture-of-Experts)**: 单目标, gate 学习路由到不同 expert.
- **MMoE (Multi-gate MoE)**: 多目标, **每个 task 有自己的 gate**, expert 在 task 间共享但 task-specific 加权方式不同 — 解决多任务相关性差时的 negative transfer 问题.

**特征分类 (每类举 3-5 个例子)**:

| 类别 | 例子 |
|---|---|
| User 静态 | 用户画像、历史下单频率、客单价 |
| User 动态 | 最近 30 天点击 / 下单序列、最近 1h 行为 (near-line) |
| Item 静态 | 餐厅评分、菜系、价位、地理位置、历史 CTR / CVR |
| Item 动态 | 当前 busy 程度、ETA、当日订单量、是否 surge |
| Context | 时段、星期几、天气、设备、location |
| Cross | user x cuisine 历史偏好、user x price-band 命中率 |

**多目标融合 (multi-objective fusion)**:

$$\text{final\_score} = w_1 \cdot P(\text{click}) + w_2 \cdot P(\text{order}) + w_3 \cdot \log(\text{GMV}) - w_4 \cdot P(\text{cancel})$$

权重由业务调优, **PM 和算法 co-own**.

**Explore intent 不放进主 ranker** — 放在 re-ranking 阶段做 diversity (MMR / DPP) 或 bandit exploration. 混进主 ranking objective 容易让模型发散.

---

#### 1.4.3 Training-Serving Skew — 最重要的工程问题

**这是面试官最想听的部分. Senior 答案**:

> "**Training-serving skew** (训练-服务特征分布不一致) 是推荐系统最常见的线上 bug, 必须用**系统设计** (system design) 而不是**纪律** (discipline) 来规避. 我的方案有三层:
>
> **1. Feature Snapshot at Serving Time** (服务时特征快照)
>
> 不要事后重算训练特征, 而是在 serving 时把模型实际看到的特征值原样 log 下来:
>
> ```
> serving:
>   features = fetch_features(user, context)
>   score = model.predict(features)
>   log(request_id, features, score)   <- snapshot
>
> training:
>   join(serving_log, label_log_by_request_id)
>   train on logged features (不重算)
> ```
>
> 这样 training 和 serving **物理上不可能 skew**. 代价是 logging 量大, 做列式压缩 + 采样.
>
> **2. Feature Store (Single Source of Truth)**
>
> Uber 内部叫 **Michelangelo Palette**. 统一管理 feature definition, offline 训练和 online serving **共享同一份 feature transformation 代码**. 新增 feature 走 feature store 流程, 禁止两边各写各的.
>
> **3. Feature Monitoring** (特征监控)
>
> 每天比对 online serving feature 分布 vs offline training feature 分布, KL divergence / PSI (Population Stability Index) 报警. **事前防御 + 事后监控两层**."

**Graceful Degradation (在线系统 robustness)**:

> "Online serving 必须设 timeout + fallback:
> - 每个 feature service 拉取设 50ms timeout, 超时用 default value 填充.
> - **'是否 fallback' 本身作为一个 feature** 喂给模型.
> - 训练时主动模拟 missing pattern (例如 dropout 部分特征), 让模型在 fallback 状态下也能合理预测.
> - 极端情况下整个 ranker 不可用, 降级到 popularity-based 兜底."

---

#### 1.4.4 Freshness / Availability — 外卖独有问题

**核心原则**:

> "**Hard filter 处理'用户根本下不了单', Soft feature 处理'体验程度差异'. Model 学连续信号, policy 兜极端 outlier, 两层防御.**"

| 信号 | 进入位置 | 处理 |
|---|---|---|
| 是否营业 / 是否接单 | **Candidate gen 阶段 hard filter** | 直接剔除 (避免 dead click) |
| ETA (30 vs 45 min) | **Ranking feature** | Model 学习 |
| Surge / Busy | **Ranking feature + Re-rank 调整** | Soft + 业务规则 |
| 极端 ETA (>2h) | **Re-rank hard filter / 降级** | Policy 兜底 |
| Driver supply 紧张 | **Ranking feature** | Model 感知 |

**为什么 dead click 是高优 bug**:
- 推荐了关门的店 -> 用户点进去发现下不了单 -> **abandonment 直接发生**.
- 这个用户这一单可能就流失到 DoorDash 了.
- 直接打击 success metrics 里的 abandonment rate 和 GMV.

**Lunch / Dinner Rush 的策略调整**:

- Supply 紧张时, re-ranker 降权 ETA > 阈值的店.
- 主动把 ETA 短的店上提 (哪怕 fine ranker score 略低), 保护用户体验.
- 预测 ETA 模型本身要 aware of region-level supply (这是和 dispatch 系统的接口).

---

### 1.5 阶段 5 · 收尾的 Senior 加分项

如果时间还有, 主动抛这几个话题让面试官感觉你"显然做过线上推荐系统":

#### 1.5.1 Position Bias (位置偏差)

> "训练数据里高位曝光的 item 天然 CTR 高, 不修正会让模型学到 position 而不是相关性. 两个解法:
> - **Position 作为 feature 训练时输入, serving 时统一置为 0** (Google paper 的做法, 也叫 'position-as-feature, position-zero-at-serve').
> - **IPS (Inverse Propensity Scoring)** 加权 — 给低位曝光样本更高权重, 从训练 loss 上 debias."

#### 1.5.2 Online Learning vs Batch Retraining

> "主流是 daily / hourly batch retrain. Online learning 风险高 (数据噪声直接进模型). 折中是 **embedding 在线更新 + ranker 离线训练**, 或者 **incremental fine-tune** 每小时一次."

#### 1.5.3 Counterfactual Evaluation (反事实评估)

> "上线前用 **off-policy evaluation (OPE)** (IPS / DR / Switch / SNIPS estimator) 估计新模型效果, 不能只看离线 AUC. AUC 高不代表线上 GMV 高 — 离线 metric 和业务 metric 解耦是行业老问题. **DR (Doubly Robust)** 是生产首选, outcome model 和 propensity model 任一正确即 unbiased."

#### 1.5.4 A/B Testing 框架 + Cluster-Randomized

> "上线靠 A/B test 看真实业务指标. Uber 内部叫 **XP (Experimentation Platform)**. 要注意:
> - **Interference (干扰效应)**: 推荐系统的 A/B 在同一城市内有 supply 干扰 (A 组抢了 B 组的 driver), 必要时做 **cluster-randomized trial** (按城市分组), 也叫 **switchback test**.
> - 看 long-term retention, 不只是当次 CTR."

---

### 1.6 阶段 6 · 一页纸记忆卡 (面试前 5 分钟扫一眼)

```
开场:    Functional / Non-Functional / Out-of-Scope / Metrics
规模:    DAU 50M, QPS peak 5-10K (8x), candidate 300, feed 30
         存储大头: training log ~TB/day
         读写比: 1:30+ (写多于读)

架构:    Client -> Gateway -> FeedService
         -> Context + FeatureStore + Availability
         -> Candidate Gen (H3 + Two-tower + Inverted + Popular)
            + Hard filter (open?)
         -> Coarse (GBDT/light 2-tower) -> 100
         -> Fine (MMoE + DIN, multi-task) -> 30
         -> Re-rank (MMR diversity + biz rules + extreme filter)
         -> Logging (Snapshot!) -> Streaming -> Offline -> 回灌

三层:    Offline (天) | Near-line (秒) | Online (ms)

关键:    H3 (Uber!)  Two-tower  MMoE
         Feature Snapshot  Michelangelo
         Graceful Degradation (timeout + fallback)
         Hard filter dead-click + Soft feature ETA
         Model + Policy 双层
         Position bias  Off-policy eval  Cluster A/B
```

#### 1.6.1 Senior 信号速查

| 维度 | 不及格答法 | Staff Golden 答法 |
|---|---|---|
| 行业黑话 | 概念都对, 没用标准词 | **H3 / two-tower / MMoE / Michelangelo / feature snapshot / graceful degradation / position bias** — 会就要说 |
| Training-serving skew | "靠 pipeline 纪律" | **Feature snapshot at serving + Feature store + Monitoring 三层防御**. 系统设计兜底, 不靠人 |
| Online robustness | 默认 feature 必须 ready | **Timeout + fallback + 模拟 missing pattern 训练 + popularity 兜底** |
| Model vs Policy | 倾向把复杂事情交给 policy | **Model 学连续信号, policy 兜极端**. 两层防御, 不是二选一 |
| 答题密度 | 频繁说"前面提过"、"common sense" | 即使重复也要完整说出 reasoning chain. 把面试官当同事, 不是考官 |

**最后一条建议**: 面试中讲到一个有名词的概念 (比如 "two-tower"), **先说名字, 再用一句话解释**. 这样既显示你知道行业术语, 又确保面试官即使不熟悉也能跟上. 例:

> "我会用 **two-tower model** — user 侧和 item 侧各一个 tower, 共享 embedding 空间, 用 in-batch sampled softmax 训练. serving 时 item tower 离线算好灌进 ANN index, user tower 在线 inference."

一句话里包含: 术语名 + 结构 + 训练方式 + serving 方式. 这是 staff level 的密度.

---

<h2 id="budget-promo-recommendation">2. Budget-Constrained Promo Recommendation (uplift x Lagrangian)</h2>

> **题目 (Problem)**: 给定固定 promo budget (例如 \$10M / 月), 设计一个 ML 系统决定给哪些用户发什么 promo, 目标是在 budget 约束下**最大化 incremental profit** (增量利润).
> **目标 Level**: Staff (L6) 水准的回答.
> **答题骨架**: TL;DR -> Problem framing -> Clarifying questions -> Requirements -> Metrics -> ML 层 (Uplift) -> 优化层 (Constrained allocation) -> 探索层 (Bandit) -> 系统架构 -> 评估策略 -> Common pitfalls -> Cheatsheet.

### 2.0 TL;DR (面试 30 秒版本)

> 这是一个 **uplift modeling x constrained optimization** 的复合问题.
>
> **ML 层**: 用 randomized experiment 数据训练 uplift model (T-learner / X-learner with XGBoost), 对每个 (user, promo) pair 预测 incremental profit $\tau(u, p)$.
>
> **优化层**: formulate 为 Multiple-Choice Knapsack (ILP), 用 **Lagrangian relaxation** (拉格朗日松弛) 在 N=10M scale 下并行求解 — 每个用户独立 argmax $\tau(u, p) - \lambda \cdot c(u, p)$, 外层对 shadow price $\lambda$ 做 binary search.
>
> **探索层**: 在 uplift 输出上加 **contextual bandit / Thompson sampling**, 处理 explore-exploit.
>
> **评估层**: offline 用 IPS / DR estimator 做 off-policy evaluation, online 用 long-running holdout (永远不发 promo 的 control group) 量 incremental profit.

---

### 2.1 Problem Framing

#### 2.1.1 业务目标

最大化 **incremental profit** (增量利润):

$$\text{Profit} = \text{take\_rate} \times \text{incremental\_GMV} - \text{promo\_cost}$$

**关键词是 "incremental"** — 只算 promo "带来的"额外 GMV, 不算用户本来就会下的单.

#### 2.1.2 The Incrementality Trap (核心陷阱)

很多候选人会跳进这个坑:

[WRONG] **错误做法**: 训练模型预测 $P(\text{redeem} \mid u, p)$ 或 $E[\text{GMV} \mid u, p, \text{sent}=1]$.

考虑两个用户:

| 用户 | 不发 promo | 发 \$5 off | 净影响 |
|---|---|---|---|
| A: 每周下单的活跃用户 | \$30 GMV | \$30 GMV, 用了 promo | **-\$5 (白送)** |
| B: dormant 用户 | \$0 | \$25 GMV, 用了 promo | **+\$25 GMV** |

只预测 "redemption" 或 "post-treatment GMV" 会**偏向用户 A** — 他 redemption 概率高、行为稳定. 但他根本不需要 promo, 这是 **cannibalization** (蚕食自有 GMV).

[RIGHT] **正确 framing**: 预测 **treatment effect / uplift** (因果效应):

$$\tau(u, p) = E[Y \mid \text{do}(T=p), X=u] - E[Y \mid \text{do}(T=0), X=u]$$

这里 $\text{do}(\cdot)$ 是 Pearl 的 do-operator, 强调**因果干预 (causal intervention)** 而非条件概率.

---

### 2.2 Clarifying Questions Framework

面试官会期望你**先问问题再设计**. 下面是该问的全部问题, 按优先级排序.

#### 2.2.1 Business / Objective (必问)

| 问题 | 为什么重要 |
|---|---|
| Winning metric 是什么? 是 redemption rate、incremental GMV、还是 incremental profit? | 决定 ML target |
| Profit 的定义? `take_rate * GMV - promo_cost`? 还是有 unit economics 模型? | 决定能不能直接转成 \$ 量纲 |
| 时间窗口? (短期 7d? 中期 4w? 长期 LTV?) | 决定 label 怎么取 |
| 关注哪些用户群? (new / dormant / active / churned) | 不同 segment 可能要分开建模 |
| 有 fairness / per-segment quota 约束吗? | 是否在优化层加 lower bound |

#### 2.2.2 Data / Constraints

| 问题 | 为什么重要 |
|---|---|
| Promo catalog 有多少种? (10? 100?) | 决定 K 维 |
| 每个用户多久 cooldown 一次? 同时只能持有一个 promo 吗? | individual constraint |
| 历史数据里有 randomized hold-out 吗? (有没有 control group 不发 promo) | **决定能不能做 causal inference** |
| Budget 是 daily / weekly / monthly? 需要 pacing 吗? | 决定要不要加 budget controller |
| Real-time 决策还是 batch? 延迟要求? | 影响系统架构 |

#### 2.2.3 Operational

| 问题 | 为什么重要 |
|---|---|
| Fraud / abuse 的处理在哪一层? ML 层还是 rule layer? | 决定 feature engineering |
| 模型部署频率? monthly retrain? daily? | 决定 pipeline |
| Cold-start 用户怎么办? (没有交互历史) | 需要 fallback strategy |

---

### 2.3 Requirements

#### 2.3.1 Functional

- 每天 / 每周对全体 eligible users 输出 promo 分配方案.
- 支持新 promo 上线后的快速 onboarding (不能等 6 个月数据).
- Real-time API: 用户打开 app 时返回个性化 promo (latency < 200ms).
- Audit trail: 每个分配决策可追溯.

#### 2.3.2 Non-functional

| 维度 | 要求 |
|---|---|
| Scale | N=10M 用户 x K=10 promo, 每日决策 |
| Latency | Batch: <2h; Online API: P99 < 200ms |
| Budget compliance | 月底实际花费 $\leq B$, 且 $\lvert \text{actual} - \text{target} \rvert / \text{target} < 5\%$ |
| Model freshness | Retrain $\geq$ weekly |
| Reliability | 99.9% uptime; graceful degradation to rule-based fallback |

---

### 2.4 Metrics

#### 2.4.1 Winning metric

**Incremental profit per dollar spent (iROI)**:

$$\text{iROI} = \frac{\sum \text{incremental\_profit}}{\sum \text{promo\_cost}}$$

#### 2.4.2 Guardrail metrics (不能动的)

- **Total GMV** (not incremental): 保证不掉.
- **User retention 30d / 90d**: 保证不伤害留存.
- **Fraud rate**: 保证不被薅羊毛.
- **Per-segment coverage**: 保证某些 segment 不被完全忽略.

#### 2.4.3 Counter-metrics (容易被忽略的)

- **Cannibalization rate**: 发出的 promo 中, 多少给了"反正会下单"的用户.
- **Promo redemption $\neq$ success**: redemption rate 高不等于 ROI 高.
- **LTV impact**: promo 习惯化是否伤害长期 organic 行为.

---

### 2.5 ML 层: Uplift Modeling

#### 2.5.1 数据要求 (最重要)

**Causal inference 的前提是有 unbiased treatment assignment 的数据**:

- 必须有 **randomized hold-out group** (A/B test): 随机选一部分用户不发 promo, 作为 ground-truth control.
- 或者用 **Inverse Propensity Weighting (IPTW)** 调整 observational data, 但需要 propensity model 准确.

如果没有 randomization, **不要做 uplift modeling** — 会被 selection bias 杀死.

#### 2.5.2 Meta-learner 框架

| Method | 思路 | 何时用 |
|---|---|---|
| **S-learner** | 单模型, treatment 作为 feature $f(X, T)$ | 简单、treatment 是连续值时合适 |
| **T-learner** | 训两个模型 $f_1(X)$ 和 $f_0(X)$, 预测时算差 | Treatment / control 数据都充足 |
| **X-learner** | T-learner + propensity 加权交叉修正 | Treatment imbalance 严重时 |
| **DR-learner** | Doubly robust, 结合 outcome model 和 propensity | 想要 robust to model misspec |
| **Causal Forest** | 直接优化 heterogeneous TE | 中等数据量、要 uncertainty |

**实际工业界第一版几乎都是: T-learner with XGBoost / LightGBM as base**.

#### 2.5.3 Multi-Treatment 扩展

我们有 K=10 种 promo, 不是 binary treatment. 两种处理:

1. **Multi-T-learner**: 每种 promo 训一个 outcome model + 一个 control model, K+1 个 model.
2. **S-learner with promo as feature**: 单模型, promo 类型作为 categorical feature.

后者数据效率更高, 前者更灵活.

#### 2.5.4 Features

- **User**: tenure, lifetime orders, avg order value, day-since-last-order, segment, geo, device.
- **Promo**: discount type, discount magnitude, expiry, redemption complexity.
- **Context**: day-of-week, time-of-day, weather, local events.
- **Interaction**: past redemption history, response to similar promos.
- **Cross**: user x promo embedding (learned, e.g. two-tower).

#### 2.5.5 Calibration

Predicted $\tau$ 必须 well-calibrated (不是只关心排序) — 因为下游优化层要用绝对值算 budget.

- 用 **isotonic regression** 或 **Platt scaling** 在 hold-out 上 calibrate.
- 监控 **calibration plot** (predicted vs actual lift in deciles).

---

### 2.6 优化层: Constrained Allocation

#### 2.6.1 ILP Formulation (Multiple-Choice Knapsack)

**决策变量**:

$$x_{i,j} \in \{0, 1\}, \quad i \in \text{users}, \; j \in \{0, 1, \ldots, K\}$$

$j=0$ 表示 "不发 promo".

**目标**:

$$\text{maximize} \quad \sum_i \sum_j \hat{\tau}_{i,j} \cdot x_{i,j}$$

**约束**:

$$
\begin{aligned}
& \sum_j x_{i,j} = 1 && \forall i \quad \text{(每用户恰好一个 assignment)} \\
& \sum_i \sum_j c_{i,j} \cdot x_{i,j} \leq B && \text{(全局 budget)} \\
& x_{i,j} \in \{0, 1\} && \text{(integrality)}
\end{aligned}
$$

这是 **Multiple-Choice Knapsack Problem (MCKP)**, NP-hard, 但有特殊结构.

#### 2.6.2 Lagrangian Relaxation (生产标配)

**关键 insight**: 把 budget 约束吸收进目标函数, 问题完全 decouple.

引入 Lagrange multiplier $\lambda \geq 0$:

$$
\begin{aligned}
L(x, \lambda) &= \sum_i \sum_j \hat{\tau}_{i,j} \cdot x_{i,j} - \lambda \cdot \left( \sum_i \sum_j c_{i,j} \cdot x_{i,j} - B \right) \\
              &= \sum_i \left[ \max_j (\hat{\tau}_{i,j} - \lambda \cdot c_{i,j}) \right] + \lambda B
\end{aligned}
$$

**结论**: 每个用户**独立**地挑能让 $\hat{\tau}_{i,j} - \lambda \cdot c_{i,j}$ 最大的 promo $j$.

**优势**:
- 10M 用户**完全并行**, 每个用户 $O(K) = O(10)$.
- 总复杂度 $O(N \cdot K)$ per iteration, $N=10^7, K=10 \to 10^8$ ops, 秒级完成.
- 外层只对**一个标量** $\lambda$ 做 binary search, 使总花费 $\approx B$.

**直觉**: $\lambda$ 是 budget 的 **shadow price** (影子价格) — 多花 \$1 budget 的边际 profit.

```python
import numpy as np

def lagrangian_solve(uplift, cost, B, tol=1e-3):
    """Binary-search shadow price lambda so total spend matches budget B.

    uplift, cost: (N, K) arrays. Returns (N,) array of chosen promo indices.
    """
    N = uplift.shape[0]
    lo, hi = 0.0, float((uplift / np.maximum(cost, 1e-9)).max())
    while hi - lo > tol:
        lam = (lo + hi) / 2
        # Each user picks argmax_j (uplift[i,j] - lam * cost[i,j]).
        score = uplift - lam * cost
        choice = score.argmax(axis=1)
        spent = cost[np.arange(N), choice].sum()
        if spent > B:
            lo = lam   # Too expensive -> raise penalty.
        else:
            hi = lam   # Slack remains -> lower penalty.
    return choice
```

#### 2.6.3 LP Relaxation 对比

把 $x_{i,j} \in \{0,1\}$ 放松为 $x_{i,j} \in [0,1]$, 变为 LP, 多项式时间可解.

**特殊性质**: MCKP 的 LP relaxation 最优解里**最多有一个 fractional variable** — 所以简单 round 损失极小.

**何时选 LP relaxation**: 当你需要**精确**最优解的近似时.
**何时选 Lagrangian**: 当你需要 **scale** 和 **online 部署**时 (生产首选).

#### 2.6.4 Greedy & Approximation

**Greedy by bang-per-buck**: 按 $\hat{\tau}_{i,j} / c_{i,j}$ 降序分配, 直到 budget 耗尽.

**Approximation guarantee**:

- **Pure greedy**: **没有常数近似比** (unbounded bad). 反例:

  | Item | Profit | Cost |
  |---|---|---|
  | A | 2 | 1 |
  | B | 100 | 100 |

  Budget=100, pure greedy 选 A 后 B 装不下, profit=2, OPT=100, 比例任意小.

- **Modified greedy**: $\max(\text{greedy\_solution}, \text{best\_single\_item})$ 是 **1/2-approximation**.
- **FPTAS (Fully Polynomial-Time Approximation Scheme)**: 可以做到 $(1 - \epsilon)$ approximation, 但实际不用 — Lagrangian 已经够好.

**何时 greedy 就够**: budget 不 binding 时 (钱够发给所有 positive-uplift user).

#### 2.6.5 Online Allocation

Batch 解法假设你**事先知道**所有用户. 但现实里 promo 触发是 real-time (用户打开 app、即将取消订单).

**生产做法**:
1. 离线用 historical data + Lagrangian 算出 $\lambda^*$.
2. Online serving 时, 每个用户独立计算 $\arg\max_j (\hat{\tau}_{i,j} - \lambda^* \cdot c_{i,j})$.
3. 监控实际花费, 必要时**动态调整** $\lambda$.

#### 2.6.6 Budget Pacing (PID Controller)

Budget $B$ 是月预算, 不是日预算. Greedy spending 第一周花光不行.

**PID controller 控制 $\lambda$**:

$$
\begin{aligned}
\text{error}(t) &= \text{expected\_spent}(t) - \text{actual\_spent}(t) \\
\lambda(t+1) &= \lambda(t) + K_p \cdot \text{error}(t) + K_i \cdot \int \text{error} + K_d \cdot \frac{d(\text{error})}{dt}
\end{aligned}
$$

- 花太快 -> error<0 -> 抬高 $\lambda$ -> 模型变挑剔.
- 花太慢 -> error>0 -> 降低 $\lambda$ -> 模型变激进.

实际 Uber / Lyft / DoorDash 都用类似机制.

---

### 2.7 探索: Bandit & Exploration

#### 2.7.1 [WRONG] Per-User Bandit (不主流)

每个用户维护一套 posterior 不可行:
- Cold start: 新用户没 prior.
- 参数爆炸: $N \times K$ 个 posterior.
- 大部分用户一辈子见过 1-2 次 promo, 更新不充分.

#### 2.7.2 [RIGHT] Contextual Bandit (主流)

**全局共享 policy**, 用户 features 作为 context:

- **LinUCB**: 线性 reward + UCB (Upper Confidence Bound) 探索.
- **Neural LinUCB**: 用 NN 做特征 encoder, 最后一层线性.
- **Thompson Sampling on uplift posterior**: 从 Bayesian uplift model 的 posterior 采样, 用采样值代替点估计去做 Lagrangian.

#### 2.7.3 与 Lagrangian 的关系

**正交且可组合**:
- Bandit 决定"探索哪些 (user, promo) 组合" — 给 uplift 加 exploration bonus.
- Lagrangian 决定"在 budget 下怎么分配" — 优化层.

$$\text{final\_score}_{i,j} = (\hat{\tau}_{i,j} + \text{exploration\_bonus}_{i,j}) - \lambda \cdot c_{i,j}$$

#### 2.7.4 何时引入 Bandit

- **Day 1**: 先用 $\epsilon$-greedy (比如 5% 流量随机探索) — 简单且有效.
- **Phase 2**: 模型成熟、新 promo 频繁上线时, 引入 Thompson Sampling.
- **Phase 3**: full RL (Reinforcement Learning) — 如果决策序列性强、有 long-term reward shaping 需求.

---

### 2.8 系统架构

```
+-------------------------------------------------------------+
|                      OFFLINE PIPELINE                         |
|                                                               |
|  +----------+   +----------+   +----------+   +----------+   |
|  | Raw logs | ->| Feature  | ->|  Uplift  | ->|  Model   |   |
|  | (events, |   |   Store  |   |   Model  |   | Registry |   |
|  |  promos) |   |          |   | Training |   |          |   |
|  +----------+   +----------+   +----------+   +----------+   |
|       |              |                                |       |
|       |         +----v-----+                   +------v---+  |
|       +-->------| Holdout  |                   | Lagrange |  |
|                 |   Eval   |                   |  Solver  |  |
|                 +----------+                   +----------+  |
+-------------------------------------------------------------+
                                                       | lambda*
                                                       v
+-------------------------------------------------------------+
|                      ONLINE PIPELINE                          |
|                                                               |
|   User opens app                                              |
|         |                                                     |
|         v                                                     |
|   +----------+   +----------+   +----------+                  |
|   | Feature  | ->|  Uplift  | ->| Argmax   | -> return promo  |
|   | Lookup   |   | Inference|   | + lambda |                  |
|   +----------+   +----------+   +----------+                  |
|                                       |                       |
|                                       v                       |
|                                 +----------+                  |
|                                 | Bandit   |                  |
|                                 | Explore  |                  |
|                                 +----------+                  |
|                                       |                       |
|                                       v                       |
|                                 +----------+                  |
|                                 | Budget   |                  |
|                                 | Pacer    |-- adjusts lambda |
|                                 +----------+                  |
+-------------------------------------------------------------+
                       |
                       v
                  Event log -> back to Raw logs (closing the loop)
```

---

### 2.9 评估策略

#### 2.9.1 Offline Evaluation / Backtesting

**问题**: log data 是 old policy 生成的, 怎么评估 new policy?

**Off-Policy Evaluation (OPE) 工具箱**:

##### 2.9.1.1 Inverse Propensity Scoring (IPS)

$$\hat{V}_{\text{IPS}}(\pi_{\text{new}}) = \frac{1}{N} \sum_i \frac{\pi_{\text{new}}(a_i \mid x_i)}{\pi_{\text{old}}(a_i \mid x_i)} \cdot r_i$$

- 优点: unbiased.
- 缺点: variance 高 (propensity 接近 0 时爆炸).

##### 2.9.1.2 Doubly Robust (DR) Estimator

$$\hat{V}_{\text{DR}} = \frac{1}{N} \sum_i \left[ \hat{q}(x_i, \pi_{\text{new}}(x_i)) + \frac{\pi_{\text{new}}}{\pi_{\text{old}}} \cdot (r_i - \hat{q}(x_i, a_i)) \right]$$

- $\hat{q}$ 是 outcome model 的预测.
- 即使 outcome model 或 propensity 有一个错, 估计仍 unbiased.
- **生产首选**.

##### 2.9.1.3 Counterfactual Replay

如果新 policy 在 logged action 上不变, 那条样本可以直接复用 — 简单但只能评估部分覆盖情况.

##### 2.9.1.4 Switch Estimator / SNIPS

- **Switch**: 当 importance weight 太大时切换到 model-based estimate, 控制 variance.
- **SNIPS (Self-Normalized IPS)**: 除以 importance weight 之和, 更稳定.

##### 2.9.1.5 Backtest 实战 checklist

- [DO] 用 holdout (randomized control) 数据做 ground truth anchor.
- [DO] 比较多个 estimator (IPS / DR / Switch), 看是否一致.
- [DO] Stratified eval: 按 user segment 分别看, 不要只看总体.
- [DO] 检查 propensity 分布, 识别 weak overlap region.
- [DON'T] 不要只看 "predicted profit" — 是 model 自己的输出, 循环论证.

#### 2.9.2 Online A/B Testing

##### 2.9.2.1 标准 A/B

- Treatment: new policy.
- Control: old policy.
- Metric: iROI, total profit, GMV, retention.

##### 2.9.2.2 Long-running Holdout (生产关键)

**永远**留一小部分流量 (1-5%) **完全不发 promo**. 这是:
- Ground truth 的 organic GMV baseline.
- Uplift model 的训练数据来源.
- Causal inference 的 anchor.

> **WARNING**: 没有 long-running holdout, 整个 uplift modeling 就是空中楼阁. 这是 **infra 投资** 不是 ML 决策.

##### 2.9.2.3 Switchback / Cluster-randomized 设计

如果 promo 有网络效应 (用户互相推荐), 单用户随机会有 spillover. 这时用:
- **City-level switchback**: 整个城市轮流 on / off.
- **Cluster-randomized**: 用户社交网络聚类后整簇分配.

---

### 2.10 Common Pitfalls 速查

| Pitfall | 表现 | 解法 |
|---|---|---|
| **Cannibalization** | 给本来就会下单的用户发 promo | 用 uplift 不是 $P(\text{redeem})$ |
| **Selection bias** | 历史数据里 promo 不是随机发的 | 必须有 randomized holdout |
| **Calibration drift** | Predicted profit 和实际差很多 | Isotonic regression + 监控 |
| **Budget pacing fail** | 月初花光 / 月末花不掉 | PID controller on $\lambda$ |
| **Cold start** | 新用户无 features | Fallback to segment-level policy |
| **Fraud** | 用户专门刷 promo | Rule layer + fraud model 在 ML 之前 |
| **Network effects** | 用户互相分享 promo code | Switchback / cluster A/B |
| **Long-term harm** | 用户被惯坏, organic 下降 | 90d retention guardrail |

---

### 2.11 面试 Cheatsheet

如果时间紧, 至少 cover 这 7 件事:

1. **Frame 成 incremental profit 最大化** (不是 redemption rate).
2. **指出 uplift / causal inference 是核心** (不是普通 supervised learning).
3. **写出 ILP formulation** (决策变量、目标、约束清楚).
4. **提到 Lagrangian decomposition 是 scale 解法** (强调 decouple 到独立 user).
5. **提 long-running holdout 和 OPE** (DR estimator 加分).
6. **提 budget pacing** (PID / shadow price 动态调整).
7. **Mention contextual bandit** (不是 per-user bandit).

**避免的 anti-patterns**:

- 一上来就谈 model (XGBoost / DNN) — 应该先 frame.
- 谈 model 时不谈 causal — 直接挂.
- 优化层只提 "用 LP 解" 不展开 — 体现不出对 scale 的理解.
- 不提 evaluation — senior 候选人必扣分.
- 把 "redemption rate" 当 winning metric — 暴露不懂业务.

---

### 2.12 附录 A: 术语表

| 术语 | 含义 |
|---|---|
| **Uplift / ITE / CATE** | Individual Treatment Effect / Conditional Avg Treatment Effect — $E[Y \mid \text{do}(T=1), X] - E[Y \mid \text{do}(T=0), X]$ |
| **iROI** | Incremental Return on Investment |
| **MCKP** | Multiple-Choice Knapsack Problem |
| **Shadow price** ($\lambda$) | Lagrangian multiplier, 对应 budget 约束的边际价值 |
| **IPS** | Inverse Propensity Scoring |
| **DR** | Doubly Robust estimator |
| **OPE** | Off-Policy Evaluation |
| **Cannibalization** | Promo 给了本来就会下单的用户 |
| **Long-running holdout** | 永久不发 promo 的小流量 control group |

### 2.13 附录 B: 进一步阅读

- Künzel et al., 2019 — *Metalearners for estimating heterogeneous treatment effects* (T / S / X / U-learner).
- Athey & Wager, 2019 — *Estimating Treatment Effects with Causal Forests*.
- Dudík et al., 2011 — *Doubly Robust Policy Evaluation and Learning*.
- Boyd & Vandenberghe — *Convex Optimization* (Lagrangian / dual decomposition 章节).
- Vazirani — *Approximation Algorithms* (knapsack 1/2 近似证明).
- Uber Engineering Blog — 实际生产案例 (按面试 prep 抄系统设计).

---

<h2 id="cross-cutting-senior-signals">3. 跨题通用 Senior 信号速查表 (Cross-cutting Senior Signals)</h2>

> 两道题共享的高层答题模板. 不论遇到 Uber Eats rec 还是 budget promo, 都要主动覆盖这些维度.

### 3.1 黑话词云 (Industry Jargon Cloud)

| 类别 | 必会词 | 一句话解释 |
|---|---|---|
| 检索 | **H3**, **two-tower**, **HNSW**, **IVF** | H3 是 Uber 开源 hexagon geo index; two-tower 是 user / item 双 encoder ANN; HNSW / IVF 是 ANN 加速结构 |
| 排序 | **MMoE**, **DIN**, **DeepFM**, **GBDT** | MMoE 多任务多 gate 共享 expert; DIN attention on user behavior seq |
| 因果 | **uplift**, **CATE**, **ITE**, **IPTW**, **propensity** | uplift = treatment effect; CATE / ITE 个体异质 TE; IPTW 用 propensity 加权 debias |
| 优化 | **MCKP**, **Lagrangian**, **shadow price**, **PID pacing** | MCKP 是 Multi-choice knapsack; Lagrangian decouple 到 user 级独立 argmax |
| 评估 | **IPS**, **DR**, **Switch**, **SNIPS**, **switchback** | DR 是 doubly robust 生产首选; switchback 解 spillover |
| 工程 | **Michelangelo**, **feature snapshot**, **graceful degradation** | Michelangelo 是 Uber 内部 ML platform; feature snapshot 防 train-serve skew |

### 3.2 Trade-off 框架 (Decision-by-decision)

每个架构决策都要主动给两端:

| 决策 | 选项 A (简单) | 选项 B (复杂) | 何时选哪个 |
|---|---|---|---|
| 召回 merge | Unified ranking (统一打分) | Quota allocation (配额) | 冷启动场景选 B, 否则 A |
| 排序模型 | GBDT | MMoE + DIN | 数据量 < 1B sample 用 A, 否则 B |
| Treatment 维度 | Binary T-learner | Multi-T-learner / S-learner | K $\leq$ 3 选 multi-T, K $\geq$ 5 选 S |
| 优化求解 | LP relaxation (精确) | Lagrangian (scale) | N $\leq$ 100K 选 LP, 生产选 Lagrangian |
| Bandit | $\epsilon$-greedy | Thompson Sampling | Day 1 选 A, 模型成熟选 B |
| Eval | A/B + holdout | Switchback / cluster | 单用户独立选 A, 有 spillover 选 B |

### 3.3 三层防御模式 (Triple-Layer Defense)

senior 候选人在每个维度都给"事前 + 运行时 + 事后"三层:

| 维度 | 事前 (build-time) | 运行时 (serve-time) | 事后 (monitor-time) |
|---|---|---|---|
| Train-serve skew | Feature store / Michelangelo | Feature snapshot 时 log | KL / PSI 监控 alarm |
| Robustness | 训练时模拟 missing pattern | Timeout + fallback default | Latency / error rate 监控 |
| Budget compliance | LP / Lagrangian 解 $\lambda^*$ | Online argmax 用 $\lambda^*$ | PID controller 动态调 $\lambda$ |
| Bias / fairness | Per-segment quota 约束 | Re-rank diversity (MMR / DPP) | Per-segment metric stratified eval |

### 3.4 Model + Policy 双层防御

> "Model 学连续信号, policy 兜极端 outlier" — 两道题都适用:

| 场景 | Model 学的 | Policy 兜的 |
|---|---|---|
| Uber Eats 排序 | ETA / busy / surge soft feature | 是否营业 hard filter, ETA > 2h hard filter |
| Promo 分配 | Uplift $\hat{\tau}(u, p)$ continuous | Fraud rule, per-segment lower bound, cool-down |

### 3.5 答题密度 / 节奏

每个 staff-level concept 用 "**name + 一句话结构 + 一句话 trade-off**" 三段式:

> "我会用 **MMoE** — 每个 task 有自己的 gate, expert 在 task 间共享但 task-specific 加权方式不同. 这避免了 multi-task 在 task 相关性差时的 negative transfer 问题. 代价是 expert 数量调参 + gate 训练不稳定, 实际部署 4-8 个 expert 就够了."

一段话覆盖: 名字 + 结构 + 解决的问题 + trade-off + 实战经验.

---

**End of document.**
