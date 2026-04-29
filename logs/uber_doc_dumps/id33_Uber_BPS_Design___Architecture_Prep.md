# Uber BPS -- Design & Architecture (D&A) Prep Guide

> **目的**：深度准备 Uber **BPS (Business Platform & Solutions，商业平台与解决方案)** 面试中 **D&A (Design & Architecture，系统设计与架构)** 环节。
> 面试官会要求你结合高层架构图，详细讲解一个复杂的历史项目。
> 评估维度：系统思维、权衡取舍的推理能力以及表达沟通能力。
>
> **时间预算**：整个 1 小时 BPS session 中约 8-10 分钟（参见 `uber_phone_screen_prep.md`）
>
> Task: T-P1-245

---

## Table of Contents

1. [D&A Format and Expectations](#1-da-format-and-expectations)
2. [Project Showcase: Ranking-as-Allocation](#2-project-showcase-ranking-as-allocation)
3. [Project Showcase: LLM Evaluation Pipeline](#3-project-showcase-llm-evaluation-pipeline)
4. [Trade-off Discussion Framework](#4-trade-off-discussion-framework)
5. [Uber System Design Patterns](#5-uber-system-design-patterns)
6. [Common D&A Follow-up Questions](#6-common-da-follow-up-questions)
7. [D&A Communication Tips](#7-da-communication-tips)
8. [Practice Checklist](#8-practice-checklist)

---

## 1. D&A Format and Expectations

### What happens in the D&A segment

面试官会问："请介绍一个你设计或参与设计的复杂系统。"之后你需要：
1. 在 HackerRank 共享编辑器或白板上画出高层架构图
2. 端到端地讲解系统的数据流
3. 解释关键设计决策与权衡取舍
4. 回答面试官深挖的追问

### What the interviewer evaluates

| Signal | What they look for |
|--------|-------------------|
| **System thinking** | 你能否将复杂系统拆解为清晰的子模块？ |
| **Trade-off reasoning** | 你是否能解释为什么选择 X 而非 Y，而不仅仅描述你做了什么？ |
| **Depth of understanding** | 被深挖时你能否继续拓展，还是只停留在表面？ |
| **Communication** | 架构图是否清晰？讲解结构是否逻辑有序？ |
| **Scope awareness** | 你是否了解自己负责模块的上下游依赖？ |

### How to structure your walkthrough (8-10 min)

| Phase | Time | What to do |
|-------|------|------------|
| Context | 1 min | 一句话：什么产品、什么问题、为什么重要 |
| Diagram | 2 min | 画出架构图，清晰标注每个模块 |
| Flow | 3 min | 端到端地讲解一个完整的请求/数据流 |
| Decisions | 2-3 min | 重点讲解 2-3 个关键权衡以及选择依据 |

---

## 2. Project Showcase: Ranking-as-Allocation

### Context (1 min)

"在我上一家公司，我负责电商平台的搜索排序系统，日均处理数百万次查询。核心挑战在于：传统的逐条排序（**Pointwise Ranking，逐条打分排序**）对每个商品独立打分，但业务目标——如曝光公平性、转化目标以及风控约束——需要在 session 层面进行协同。我设计了一套 **Ranking-as-Allocation（排序即资源分配）** 框架，将排序问题转化为带约束的资源分配问题。"

### Architecture Diagram

```
                    User Query
                        |
                        v
              +-------------------+
              |   Query Parser    |
              | (intent, filters) |
              +-------------------+
                        |
                        v
              +-------------------+
              |    Retrieval      |
              | (embedding + BM25)|
              | ~1000 candidates  |
              +-------------------+
                        |
                        v
              +-------------------+
              |  Pointwise Scorer |
              | (deep model, MoE) |
              | per-item P(click) |
              +-------------------+
                        |
                        v
        +-------------------------------+
        |   Session-Level Allocator     |
        | (multi-objective optimization)|
        |                               |
        |  Objectives:                  |
        |  - Maximize conversion        |
        |  - Exposure fairness floor    |
        |  - Risk/compliance cap        |
        |  - Diversity target           |
        |                               |
        |  Method: constrained          |
        |  optimization (LP/ILP)        |
        +-------------------------------+
                        |
                        v
              +-------------------+
              |   Re-ranker       |
              | (late-stage MoE)  |
              | final position    |
              +-------------------+
                        |
                        v
              +-------------------+
              |  A/B Experiment   |
              |  Framework        |
              | (diagnostic tools)|
              +-------------------+
                        |
                        v
                  Search Results
```

### End-to-End Flow

1. **Query parsing（查询解析）**：从用户查询中提取意图、品类过滤条件、价格区间
2. **Retrieval（召回）**：两阶段召回——基于 embedding 的语义召回（FAISS/ANN）约 500 条，**BM25 (Best Match 25，词频逆文档频率检索)** 词法召回约 500 条，合并去重后得到约 1000 个候选
3. **Pointwise scoring（逐条打分）**：深度模型对每个商品预测 P(click)、P(purchase)、P(return)。**MoE (Mixture of Experts，混合专家)** 架构：不同商品品类由不同专家塔负责处理
4. **Session-level allocation（会话级资源分配）**：这是核心创新。不再按分数排序，而是构建带约束的优化问题：
   - 决策变量：每个候选商品的位置分配
   - 优化目标：最大化预期转化率
   - 约束条件：每个卖家层级的最低曝光量、每页风险商品上限、品类多样性要求
5. **Re-ranking（精排）**：最后一道处理，应用业务规则（赞助位、编辑精选），确保分配结果对应合法的排序列表
6. **Experimentation（实验）**：**A/B (A/B Testing，对照实验)** 框架，支持指标拆解：当整体转化率变化时，可定位是哪个分配约束驱动了变化

### Key Trade-off Discussions

**Trade-off 1: Pointwise scoring vs. listwise/pairwise**

| Approach | Pros | Cons |
|----------|------|------|
| Pointwise (chosen) | 推断速度快，便于逐条 debug，与分配层职责清晰分离 | 忽略了商品之间的相互依赖 |
| Listwise (LambdaMART) | 直接优化排序指标（**NDCG，归一化折扣累积增益**） | 推断开销大，难以拆解诊断 |
| Pairwise (RankNet) | 捕捉相对顺序关系 | 商品对数量二次方级增长，梯度噪声大 |

"我们选择 Pointwise，因为分配层已经负责商品间的协同。如果把这个责任推给打分模型，会造成优化目标冲突，且出了问题很难判断是打分层还是分配层的问题。"

**Trade-off 2: MoE vs. single deep model**

"初期我们使用单一模型，但观察到品类特异性模式（电子产品和服装的点击/购买漏斗差异显著）。采用按品类路由的 MoE——每次推断只激活 8 个专家中的 2 个——在不增加线上延迟的前提下，转化率提升了 +2.3%。"

**Trade-off 3: Hard constraints vs. soft penalties in allocation**

"我们最初使用软惩罚（**Lagrangian Relaxation，拉格朗日松弛**），但发现流量峰值时曝光公平性会被违反。改为通过 **LP (Linear Programming，线性规划)** 求解器强制执行硬约束，保证了合规性，但增加了约 5ms 延迟。由于这是不可妥协的业务要求，我们接受了这个延迟代价。"

### Anticipated follow-ups

| Question | Answer sketch |
|----------|--------------|
| "How do you handle latency?" | 召回与打分并行化。LP 求解器仅在预过滤的 top-100 候选上运行。整体 P99 < 200ms。 |
| "What if constraints conflict?" | 按优先级处理：合规 > 公平性 > 多样性。如果无可行解，放宽优先级最低的约束并记录日志。 |
| "How do you evaluate offline?" | 分配层使用反事实估计（IPS 加权）；打分层使用标准 AUC/NDCG。 |
| "What would you do differently?" | 考虑用上下文 bandit（**Contextual Bandit，上下文老虎机**）替代静态 LP 公式，实现在线分配学习。 |

---

## 3. Project Showcase: LLM Evaluation Pipeline

### Context (1 min)

"我构建了一套基于 **LLM (Large Language Model，大语言模型)** 的评测流水线，用于替代人工评审进行搜索质量评估。该系统将评测成本降低了 94%，周转时间从 2 周缩短到 4 小时，使团队每季度能运行 3 倍数量的实验。目前该系统已在搜索和广告团队内全面推广使用。"

### Architecture Diagram

```
              Experiment Request
              (query set + config)
                      |
                      v
            +-------------------+
            |   Data Pipeline   |
            | sample queries    |
            | retrieve results  |
            | pair with labels  |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Prompt Builder   |
            | task-specific     |
            | templates + few-  |
            | shot examples     |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Calibration      |
            | Module            |
            | - temperature     |
            | - chain-of-thought|
            | - self-consistency|
            | - anchor examples |
            +-------------------+
                      |
                      v
            +-------------------+
            | Batch Inference   |
            | (async, rate-     |
            |  limited, retry)  |
            | ~10K judgments/hr  |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Agreement        |
            |  Analysis         |
            | - vs human judges |
            | - Cohen's kappa   |
            | - per-category    |
            |   breakdown       |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Dashboard        |
            | - experiment      |
            |   comparison      |
            | - confidence      |
            |   intervals       |
            | - failure cases   |
            +-------------------+
```

### End-to-End Flow

1. **Data pipeline（数据流水线）**：给定一个实验（如"新排序模型 v2"），按品类/意图分层采样 N 条查询，分别从对照组和实验组获取搜索结果
2. **Prompt construction（Prompt 构建）**：针对不同任务（相关性、时效性、意图匹配）使用特定模板。附上来自标注数据的 few-shot 示例。格式示例："给定查询 Q 和结果 R，请对相关性评分（1-5 分）。请逐步思考。"
3. **Calibration（校准）**：使用带有已知人工标注的锚定示例，确保分数分布对齐。针对每个任务调整 temperature。**Self-consistency（自一致性）**：每对样本采样 3 次判断，取多数票
4. **Batch inference（批量推断）**：异步 API 调用，带限速、指数退避和结果缓存。每小时约 10K 次判断，每次约 $0.02（vs. 人工评审约 $0.35）
5. **Agreement analysis（一致性分析）**：与预留的人工标注计算 **Cohen's kappa（科恩 kappa 系数）**。按品类拆解，识别 LLM 与人工评审的分歧点（通常在主观性查询和领域专业术语上）
6. **Dashboard（仪表盘）**：多实验对比视图，附置信区间。高分歧样本的 failure case 查看器，支持人工复核

### Key Trade-off Discussions

**Trade-off 1: LLM-as-judge vs. fine-tuned classifier**

| Approach | Pros | Cons |
|----------|------|------|
| LLM-as-judge (chosen) | 零样本泛化，无需重新训练即可处理新评测维度，通过 CoT 可解释 | 单次判断成本高、延迟大、对 prompt 敏感 |
| Fine-tuned classifier | 快速、廉价、结果确定 | 每个任务需要标注数据，泛化性差，不可解释 |

"我们选择 LLM-as-judge，因为团队每季度约新增 3 个评测维度（如'时效性'、'视觉匹配'）。每次都微调一个新分类器正是我们想消除的瓶颈。"

**Trade-off 2: Single judgment vs. self-consistency**

"单次判断成本降低 3 倍，但噪声率约 8%。Self-consistency（3 次采样取多数票）将噪声降至约 2%，并自带置信度信号。我们在初步筛选时用单次判断，最终实验决策时用 self-consistency。"

**Trade-off 3: Prompt engineering vs. fine-tuning the LLM**

"Prompt engineering 较脆弱——措辞细微变化可能导致分数漂移。但微调每个任务需要 5K+ 个金标签，且每次模型更新后都要重新训练。我们通过锚定校准（固定参考示例以归一化评分尺度）来缓解 prompt 脆弱性，而非选择微调。"

### Anticipated follow-ups

| Question | Answer sketch |
|----------|--------------|
| "How do you handle hallucination?" | CoT + 结构化输出（带推理过程的 JSON）。标记推理过程与评分矛盾的判断。 |
| "What about bias?" | 位置偏差（总倾向于支持先展示的结果）。缓解方案：随机化展示顺序，测试两种顺序。 |
| "How reliable is kappa?" | 整体 kappa 0.72（显著一致）。按品类：导航类查询 0.85，主观性查询 0.55。主观品类我们不信任 LLM 的判断。 |
| "Scale to 100K judgments?" | Batch API + 结果缓存。常见查询-结果对已预先缓存。边际成本递减。 |

---

## 4. Trade-off Discussion Framework

当面试官问"为什么选 X 而不是 Y？"时，使用以下结构：

### STAR-T Framework for Trade-offs

1. **State the options（陈述选项）**："我们考虑了 X 和 Y"
2. **Trade-offs（列举权衡）**："X 带来 [收益] 但代价是 [缺点]。Y 带来 [收益] 但代价是 [缺点]"
3. **Analysis（分析）**："基于我们的约束条件——[延迟预算 / 团队规模 / 数据可用性 / 业务需求]——X 更合适，因为……"
4. **Result（结果）**："部署 X 之后，我们观察到 [指标提升]"
5. **Reflection（反思，如被追问）**："事后来看，我也会考虑 Z，因为……"

### Common trade-off dimensions at Uber

| Dimension | Option A | Option B | When to pick A | When to pick B |
|-----------|----------|----------|----------------|----------------|
| **Consistency vs. Availability** | 强一致性（SQL，事务） | 最终一致性（NoSQL，事件驱动） | 金融数据、行程匹配 | 数据分析、用户偏好 |
| **Latency vs. Accuracy** | 近似结果（缓存、预计算） | 精确结果（实时计算） | **ETA (Estimated Time of Arrival，预计到达时间)** 估算、司机地图 | 定价、支付 |
| **Batch vs. Stream** | 批处理（Spark，每日） | 流处理（Kafka，Flink） | 训练数据、报表 | 欺诈检测、动态调价 |
| **Monolith vs. Microservice** | 单体服务 | 独立微服务 | 早期阶段、紧耦合场景 | 独立扩容、团队各自归属 |
| **Build vs. Buy** | 自研方案 | 第三方工具 | 核心差异化能力、特殊需求 | 通用功能、时间压力大 |
| **Online vs. Offline** | 实时推断 | 预计算查找 | 个性化、动态上下文 | 静态推荐、冷启动 |

---

## 5. Uber System Design Patterns

以下是 Uber 真实的系统设计模式，可能以 D&A 讨论话题或代码追问的形式出现。熟悉这些模式能体现你的业务领域意识。

### 5.1 Driver Maps (Real-time Geospatial)

**问题**：在乘客地图上实时展示附近可用司机。

```
Driver App                          Rider App
    |                                   |
    | GPS update (every 4s)             | Map viewport request
    v                                   v
+----------+                    +----------+
| Location |  -- Kafka -->      | Map Tile |
| Service  |                    | Service  |
| (ingest) |                    | (query)  |
+----------+                    +----------+
    |                                   ^
    v                                   |
+-----------------------------------+   |
|      Geospatial Index             |---+
| (Google S2 cells / H3 hexagons)  |
| - cell resolution ~100m          |
| - in-memory, sharded by region   |
+-----------------------------------+
```

**关键设计决策**：
- **S2/H3 cells vs. geohash（地理空间索引方案对比）**：S2 cells 在所有纬度面积均匀（geohash 在极点附近会变形）。H3 六边形具有均匀的邻接性（始终有 6 个邻居）。Uber 使用 H3。
- **Push vs. pull（推拉模式）**：司机主动推送位置更新；乘客拉取视口数据。混合方案：将更新推送到索引，渲染时拉取。
- **Staleness（数据新鲜度）**：30 秒内无更新则将司机标记为离线。权衡：超时阈值越激进 = 幽灵车越少，但可能在隧道中误标司机为下线。

**Follow-up questions**：
- "How do you handle millions of concurrent drivers?" -- 按 H3 resolution-3 cell（全球约 12K 个 cell）分片，每个分片可放入内存
- "How accurate is the map?" -- 4 秒 GPS 间隔 + 插值。满足"司机在附近"的 UX 需求，但不适合导航

### 5.2 Shopping Cart (UberEats)

**问题**：跨 session、多设备及并发修改场景下的购物车管理。

```
Mobile App / Web
       |
       v
+---------------+
|  Cart API     |
| (CRUD + rules)|
+---------------+
       |
       v
+---------------+     +---------------+
|  Cart Store   |---->| Menu Service  |
| (per-user     |     | (prices,      |
|  document)    |     |  availability)|
+---------------+     +---------------+
       |
       v
+---------------+     +---------------+
| Pricing       |---->| Promo Engine  |
| Calculator    |     | (coupons,     |
| (surge, fees) |     |  referrals)   |
+---------------+     +---------------+
       |
       v
+---------------+
|  Checkout     |
|  (order       |
|   creation)   |
+---------------+
```

**关键设计决策**：
- **Cart as document vs. normalized rows（文档型 vs. 行归一化存储）**：文档型（每用户一个 JSON blob）读写更简单，但跨用户查询困难。归一化方案更适合分析。Uber 在热路径上使用文档型，异步同步到分析数据库。
- **Optimistic vs. pessimistic locking（乐观锁 vs. 悲观锁）**：使用乐观锁（版本号字段，冲突时重试），因为购物车冲突很少见（同一用户，两台设备）。悲观锁会在常规场景增加不必要的延迟。
- **Price at add-time vs. checkout-time（加购时定价 vs. 结账时定价）**：结账时重新获取当前价格。若价格变化超过阈值则展示"价格已变动"提示。避免以过期价格下单。

**Follow-up questions**：
- "What if a menu item becomes unavailable?" -- 软删除该商品，通知用户，但不阻塞其他商品的结账流程
- "How do you handle surge pricing in cart?" -- 价格在确认结账前不锁定。购物车展示预估总价，附"价格可能变动"说明

### 5.3 Driver Queue / Dispatch

**问题**：在保证公平性与效率的前提下，将乘客与最近的可用司机进行匹配。

```
Ride Request                    Driver Pool
     |                               |
     v                               v
+-----------+               +-----------+
| Dispatch  |<-- match ---->| Supply    |
| Engine    |               | Index     |
| (matching |               | (H3 cell |
|  + assign)|               |  lookup)  |
+-----------+               +-----------+
     |
     v
+-----------+
| Fairness  |
| Layer     |
| - FIFO    |
| - earnings|
|   balance |
+-----------+
     |
     v
+-----------+
| Offer     |
| Manager   |
| (timeout, |
|  reassign)|
+-----------+
```

**关键设计决策**：
- **Nearest-first vs. FIFO queue（最近优先 vs. 先进先出队列）**：纯最近优先会使低需求区域的司机长时间接不到单。纯 FIFO 忽略乘客等待时间。混合方案：在公平性窗口内优先最近（等待超过 X 分钟的司机获得优先级加成）。
- **Single offer vs. broadcast（单一派单 vs. 广播派单）**：单一派单（一次只向一位司机发单，15 秒超时）vs. 广播（同时推送多位司机，先接受者得）。Uber 在 UberX 使用单一派单（乘客期望明确的司机），在 Pool 中使用广播。
- **ETA-based vs. distance-based matching（基于 ETA vs. 基于距离的匹配）**：ETA 考虑了交通状况、单行道、当前车速，更准确但计算更昂贵。预先计算相邻 cell 的 ETA 矩阵。

### 5.4 ETA Estimation

**问题**：预测司机到达上车点（或配送目的地）的时间。

```
Route Request (origin, destination)
              |
              v
     +------------------+
     | Graph Engine      |
     | (road network,    |
     |  Dijkstra/A*)     |
     +------------------+
              |
              v
     +------------------+
     | Segment Speed    |
     | Predictor        |
     | (ML model:       |
     |  historical +    |
     |  real-time GPS)  |
     +------------------+
              |
              v
     +------------------+
     | Calibration      |
     | (bias correction |
     |  by city/time)   |
     +------------------+
              |
              v
     +------------------+
     | Post-processing  |
     | (rounding, min   |
     |  floor, display) |
     +------------------+
```

**关键设计决策**：
- **Historical average vs. ML model（历史均值 vs. ML 模型）**：历史均值（同一路段、同一小时、同一星期几）是强基线。ML 额外引入：GPS 探针的实时路况、天气、活动事件。ML 的 **MAPE (Mean Absolute Percentage Error，平均绝对百分比误差)** 降低约 15%。
- **Pre-computation vs. on-demand（预计算 vs. 按需计算）**：每 5 分钟预计算一次 cell 到 cell 的 ETA。对精确起终点进行按需计算。两层架构：快速查找用于"附近"估计 + 精确路由用于确认匹配。
- **Optimistic vs. conservative（乐观估计 vs. 保守估计）**：乐观 ETA 提升转化率（乘客更愿意叫车），但迟到会引起不满。保守估计损失订单但建立信任。Uber 的校准策略是轻微高估（约 10%）。

### 5.5 Food Ordering Pipeline (UberEats)

**问题**：从浏览到配送的端到端订单流程。

```
User browses         User orders          Restaurant         Courier
     |                    |                   |                  |
     v                    v                   v                  v
+---------+       +-----------+       +-----------+      +-----------+
| Menu &  |       | Order     |       | Restaurant|      | Courier   |
| Search  |       | Service   |------>| Dashboard |      | Matching  |
| Service |       | (payment, |       | (accept/  |      | & Routing |
+---------+       |  validate)|       |  prepare) |      +-----------+
                  +-----------+       +-----------+             |
                        |                   |                   v
                        v                   v            +-----------+
                  +-----------+       +-----------+      | Delivery  |
                  | Payment   |       | Kitchen   |      | Tracking  |
                  | Service   |       | Display   |      | (real-time|
                  +-----------+       | System    |      |  updates) |
                                      +-----------+      +-----------+
```

**关键设计决策**：
- **Synchronous vs. async order flow（同步 vs. 异步订单流）**：支付是同步的（必须确认后再发送给餐厅）。餐厅接单是异步的（webhook/推送通知）。若餐厅 5 分钟内未接单，自动取消并退款。
- **Courier pre-dispatch vs. post-accept（预分配配送员 vs. 接单后分配）**：预分配（餐厅接单前就分配配送员）可减少约 5 分钟配送时间，但若餐厅拒单则浪费配送员时间。接单后分配更安全。Uber 对高接单率餐厅（>95% 接单率）使用预分配。
- **Estimated delivery time（预计配送时间）**：由 prep_time（基于餐厅的 ML 模型）+ pickup_wait + travel_time（ETA 引擎）组成。每个分量都有不确定性。展示区间而非点估计。

---

## 6. Common D&A Follow-up Questions

以下问题在 1p3a BPS 报告中频繁出现。请针对你自己的项目准备答案。

### General architecture questions

| Question | What they're testing | How to answer |
|----------|---------------------|---------------|
| "Why did you choose X over Y?" | 权衡取舍的推理能力 | 使用 STAR-T 框架（第 4 节）。永远不要说"这是标准方案"。 |
| "What would you do differently?" | 自我认知、成长意识 | 说出一个真实局限性和具体的替代方案。"如果有更多时间，我会……" |
| "How did you handle failure cases?" | 容错思维 | 描述具体的失败模式 + 缓解措施。重试、熔断、降级、告警。 |
| "How did you scale this?" | 系统知识 | 水平扩展（分片、副本）vs. 垂直扩展。瓶颈识别。 |
| "Walk me through a request lifecycle" | 端到端理解 | 从用户操作 -> 数据库写入 -> 响应返回，全程追踪。包括缓存、异步步骤。 |

### ML-specific D&A questions

| Question | What they're testing | How to answer |
|----------|---------------------|---------------|
| "How do you monitor model quality in production?" | MLOps 成熟度 | 线上指标（CTR、转化率）+ 离线评估（holdout 集）。漂移检测。告警阈值。 |
| "How do you handle data drift?" | 实际 ML 经验 | 特征分布监控、重训触发机制、新模型影子模式测试。 |
| "How do you do A/B testing for ML models?" | 实验设计 | 随机流量分割、护栏指标、统计显著性、分阶段放量计划。 |
| "How do you handle cold-start?" | 算法思维 | 新用户：基于热门度的 fallback。新商品：基于内容特征。探索/利用（Explore/Exploit）。 |
| "How do you serve models at low latency?" | 基础设施知识 | 模型优化（量化、蒸馏）、缓存、batching、异步预计算。 |

### Questions from 1p3a BPS reports

| Question | Context |
|----------|---------|
| "Draw the architecture on the whiteboard" | 面试官真的会要求你在 HackerRank 编辑器上画图 |
| "What was the most complex technical decision?" | 选一个有明确前后对比和可量化影响的决策 |
| "How did you convince your team of this approach?" | 沟通能力 + 数据驱动决策 |
| "What metrics did you use to evaluate success?" | 要有具体数字："将 X 提升了 Y%" |
| "How long did this take and what was the team?" | 范围意识：你的贡献 vs. 团队整体投入 |
| "What's the bottleneck in this system?" | 展示你思考扩容限制，而非只关注 happy path |

### Red flags to avoid

| Red flag | Why it's bad | Better approach |
|----------|-------------|-----------------|
| "It took two weeks" | 强调时间而非复杂度 | "挑战在于 X，需要解决 Y" |
| "I just followed the standard approach" | 没有体现批判性思维 | "我们评估了 A 和 B。因为 [约束条件] 选择了 A" |
| "I built the whole thing" | 听起来要么不诚实，要么项目规模太小 | "我负责 [具体模块]。团队负责了 [X、Y]" |
| Only describing happy path | 缺乏容错思维 | "主要的失败模式是 X。我们通过 Y 来应对" |
| Vague metrics | "它更快了" | "将 P99 延迟从 450ms 降至 180ms" |

---

## 7. D&A Communication Tips

### During the diagram

- **从全局出发**：先画出所有方块，再加箭头和标签
- **使用清晰的模块名称**："Retrieval Service"，而不是"Step 1"
- **标明数据流方向**：箭头附标签（"query"、"candidates"、"scores"）
- **标注你负责的模块**：用圆圈或高亮标出你 own 的部分
- **控制在 5-7 个方块**：超过这个数量，8 分钟内讲不完

### During the walkthrough

- **实时旁白流程**："用户查询从这里进来，经过解析，然后……"
- **在决策点暂停**："到这一步，我们面临选择：X 还是 Y。我们选了 X，因为……"
- **主动预判问题**："你可能会问为什么没有做 Z——原因是……"
- **使用具体数字**："这个系统处理约 **QPS (Queries Per Second，每秒查询量)** 10K，P99 < 200ms"
- **承认局限性**："有一点我会改进的是……"（体现成熟度）

### Handling unknown questions

如果被问到你没有负责过的模块：
- "我没有直接负责那个模块，但我的理解是 [简要说明]。我可以详细介绍 [你负责的模块]，它通过 [API/接口协议] 与那个模块交互。"

---

## 8. Practice Checklist

### Project 1: Ranking-as-Allocation

- [ ] 在 2 分钟内凭记忆画出架构图
- [ ] 在 3 分钟内讲完端到端流程
- [ ] 清晰解释 Pointwise vs. Listwise 的权衡
- [ ] 解释 MoE 架构以及为何有效
- [ ] 用具体示例解释分配约束
- [ ] 准备一个指标："将转化率提升了 X%"
- [ ] 准备好"如果重做你会怎么做"的回答

### Project 2: LLM Evaluation Pipeline

- [ ] 在 2 分钟内凭记忆画出架构图
- [ ] 在 3 分钟内讲完端到端流程
- [ ] 解释 LLM-as-judge vs. 微调分类器的权衡
- [ ] 解释校准方法论
- [ ] 准备好指标："94% 成本降低，90% 延迟降低，0.72 kappa"
- [ ] 准备好幻觉/偏差缓解方案的答案

### General D&A readiness

- [ ] 向不熟悉背景的人练习讲解每个项目（计时）
- [ ] 针对每个项目至少 3 个决策，准备好"为什么选 X 而非 Y"的回答
- [ ] 在纯文本编辑器（而非画图工具）上练习画架构图
- [ ] 复习 Uber 系统设计模式（第 5 节）以建立业务领域认知
- [ ] 准备好 2-3 个具体的失败模式及应对方案
- [ ] 为每个论断准备好具体指标数据

---

## Quick Reference: D&A in 60 Seconds

时间紧迫时，牢记这套结构：

```
1. CONTEXT  (10 sec) -- 什么产品、什么问题、为什么重要
2. DIAGRAM  (60 sec) -- 5-7 个方块，箭头附数据流标签
3. FLOW     (90 sec) -- 一个请求从头到尾的完整路径
4. DECISION (90 sec) -- "我们选择 X 而非 Y，因为 [约束条件]"
5. METRIC   (30 sec) -- "这将 Z 提升了 N%"
6. REFLECT  (30 sec) -- "如果重做，我还会考虑……"
```

核心内容约 5 分钟，余下 3-5 分钟用于追问 Q&A。