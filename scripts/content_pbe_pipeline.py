"""Populate the pbe-pipeline system design module with all 8 content sections.

Usage:
    python scripts/content_pbe_pipeline.py

Finds the SystemDesign record with slug="pbe-pipeline" and fills in:
  overview, architecture, dataflow, formulas,
  production_constraints, tradeoffs, defense, verbal_outline

Chinese source of truth.  English technical terms preserved in bold
with first-use explanation.  Formulas and code blocks kept as-is.
Idempotent -- overwrites existing content on each run.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "pbe-pipeline"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------

OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

ML 排序模型的质量取决于训练数据。在 eBay，搜索排序引擎（**Cassini**）每日处理数十亿次曝光（impression），但历史上的训练信号依赖于**点击（click）**——这在根本上是有缺陷的标注来源。

### 为什么点击数据不够

- **稀疏性（sparsity）**：点击率仅为 2--5%。95% 以上的曝光在点击日志中**完全没有信号**。
- **位置偏差（position bias）**：用户不成比例地关注靠前位置。排在第 1 位的商品被点击，不是因为它最好，而是因为它最先被看到。
- **信任偏差（trust bias）**：用户倾向于信任排序结果，即使靠后的结果更相关，也会点击排在最前面的。
- **点击 != 满意度**：用户点击后立即返回是一个*负面*信号，但原始点击日志将其与停留 5 分钟的点击等同对待。

### PBE 方法

**PBE (Product-Based Experience)** 日志系统用更丰富的行为信号替代以点击为中心的标注：

| 信号 | 捕获内容 | 重要性 |
|--------|-----------------|----------------|
| **Viewport 曝光** | 商品是否真正在用户屏幕上可见 | 消除了未被查看商品的位置偏差 |
| **停留时长（dwell time）** | 用户在该商品上花费的时间 | 区分真正兴趣与偶然点击 |
| **交互深度（engagement depth）** | 滚动深度、图片放大、加入购物车 | 超越二元点击/未点击的多层次相关性 |

### 挑战

该管线必须满足**低延迟**（不影响搜索响应时间）、**高吞吐**（每日约 5 亿次曝光）以及**可归因性**（每个训练标注都可追溯至生成它的具体排序模型，从而支持反事实评估）。
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## 架构深入剖析 (Architecture Deep Dive)

**PBE (Product-Based Experience)** 管线跨越三个层级：在线服务、双流数据接入和离线处理。每个层级针对不同的延迟/吞吐权衡而设计。

### 在线搜索服务

```
[User Query]
    |
    v
[Search Front End] -- injects trackable IDs into HTML (data-track-id)
    |
    v
[Cassini Ranking Engine] -- produces ranked results with model attribution metadata
    |
    v
[PBE Carousel] -- enhanced product cards with viewport tracking (IntersectionObserver)
    |
    v
[Browser] -- fires viewport/dwell/engagement events to Sojourner
```

- **Search Front End**：每个渲染的商品都会获得一个唯一的 `data-track-id` 属性，编码 `(query_id, item_id, position, model_version)`。这是归因（attribution）的基础——没有它，我们就无法将训练标注追溯至对该商品进行排序的模型。
- **Cassini Ranking Engine**：为每个结果附加模型归因元数据（哪个模型评分、使用了哪些特征、原始分数）。
- **PBE Carousel**：增强版商品展示区，通过 `IntersectionObserver` API 进行视口追踪。当商品进入和离开视口时触发事件。

### 双流数据接入 (Dual-Stream Data Ingestion)

两个并行的数据流向离线处理层供给数据：

**Stream 1 -- 行为事件 (Sojourner/UBI)**：
- 原始用户事件（曝光、视口进入/离开、点击、停留、加入购物车）
- **Sojourner** 进行会话拼接（session stitching）和 ID 解析
- **Spark Join** 以 5 分钟微批次解析匿名事件至用户会话

**Stream 2 -- 商品特征 (Kafka Feature Broker)**：
- 商品元数据：价格、状况、卖家评分、图片质量、物流速度
- **Kafka Streams** 用于低延迟特征更新
- **Spark Streaming** 物化按日期分区的特征表

### 离线处理与归因

- **Analytics Engine**：计算每次曝光的标注——曝光布尔值、停留时长、交互深度、转化标记。
- **Formal Attribution**：应用位置偏差修正（**IPW, Inverse Propensity Weighting**）和多触点模块归因折扣。这是该管线的核心学术贡献。
- **Training Data Materialization**：将归因标注与特征合并为 ML/GPU 友好的格式（Parquet），按 `date + model_version` 分区。

### Schema 演进策略 (Schema Evolution Strategy)

PBE 事件 schema 随业务需求演进（新信号类型、新归因字段）。在每日处理数十亿事件的管线中，schema 变更必须**零停机**完成：

| 演进类型 | 策略 | 示例 |
|----------|------|------|
| **新增可选字段** | Avro schema 向前兼容（添加带默认值的字段） | 新增 `scroll_velocity_px_s` 字段，默认 `null` |
| **字段类型变更** | 双写过渡期（旧字段 + 新字段并存 2 周） | `dwell_time_ms` (int) -> `dwell_time_s` (float) |
| **字段废弃** | 标记 `@deprecated`，90 天后移除；下游 Spark job 先迁移 | 废弃 `click_type` 枚举 |

**Schema Registry**（Confluent Schema Registry）强制兼容性检查：
- Producer 注册新 schema 前，Registry 验证与前一版本的**向后兼容性**
- Consumer 使用 schema ID 解码，新旧 schema 可共存
- 不兼容变更（如移除必填字段）被 Registry 拒绝，需走 schema migration PR 审批流程

### ML 闭环

```
Training Data -> Model Training (LambdaMART / neural ranker)
    -> A/B Testing -> Deploy Ranking Policy -> New PBE Logs (closed loop)
```

每个模型都在其前任生成的数据上训练，形成反馈循环（feedback loop）。归因层必须小心管理这个循环，以避免反馈放大效应（feedback amplification）。
"""

# ---------------------------------------------------------------------------
# S3: Data Flow
# ---------------------------------------------------------------------------

DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 端到端流程

```
User sees SRP (Search Results Page)
  |
  |-- Trackable IDs embedded in HTML via data-track-id attributes
  |
  +-- Stream 1: Behavioral Events
  |     User actions -> Sojourner (session stitch + ID resolution)
  |       -> Spark Join (5-min micro-batch, resolves anonymous -> session)
  |       -> Behavioral event tables (partitioned by date)
  |
  +-- Stream 2: Product Features
  |     Product updates -> Kafka Feature Broker
  |       -> Spark Streaming -> Feature tables (partitioned by date)
  |
  +-- Offline Attribution Pipeline (daily batch)
        |
        +-- Analytics Engine
        |     Joins Stream 1 + Stream 2
        |     Computes: exposure labels, dwell, engagement, conversion
        |
        +-- Formal Attribution
        |     Position bias correction (IPW weights)
        |     Module attribution discount (multi-touch credit)
        |
        +-- Data Quality Gate  <-- NEW
        |     Schema drift detection, anomaly detection, freshness SLAs
        |
        +-- Training Data Materialization
              Parquet files: features + attributed labels
              Partitioned by date + model_version
              ~2TB per daily snapshot, 30-day retention
                |
                v
        ML Training -> A/B Test -> Deploy -> New Logs (closed loop)
```

### 关键组件详情

#### Sojourner（会话拼接器）

Sojourner 是 eBay 的实时事件处理系统，功能如下：
1. 接收原始 **UBI (Unified Behavioral Interface)** 事件
2. 将匿名浏览会话解析为用户 ID（如可用）
3. 将页面级事件拼接为连贯的会话
4. 峰值输出约 200K 事件/秒的增强会话事件

#### Spark Join（微批次解析）

5 分钟微批次 Spark 作业：
1. 读取最近 5 分钟窗口的 Sojourner 输出
2. 将行为事件与 trackable ID 元数据进行关联
3. 解析 `(data-track-id) -> (query_id, item_id, position, model_version)`
4. 将解析后的事件写入行为事件存储

#### Analytics Engine（标注计算）

对已解析事件流中的每次曝光：

| 标注 | 计算方式 | 类型 |
|-------|------------|------|
| `exposed` | 视口停留时间 > 阈值 且 可见百分比 > 50% | Boolean |
| `dwell_seconds` | 视口进入与视口离开/页面退出之间的时间 | Float |
| `engaged` | 停留 > 2 秒 或 图片放大 或 加入购物车 | Boolean |
| `converted` | 曝光后 24 小时内购买 | Boolean |
| `satisfaction` | 停留时长、交互、转化的加权组合 | Float [0,1] |

#### Attribution Engine（归因引擎）

对原始标注应用两项修正：

1. **位置偏差修正**，通过 **IPW (Inverse Propensity Weighting)** 实现
2. **模块归因折扣**，用于出现在多个模块中的商品

### 数据质量监控 (Data Quality Monitoring)

训练数据质量直接影响排序模型质量。我们在归因管线输出端设置**四层数据质量门控**：

#### 异常检测 (Anomaly Detection)

对每日训练数据批次的关键统计量进行监控：

| 监控指标 | 正常范围 | 告警阈值 | 根因示例 |
|----------|----------|----------|----------|
| 曝光量 | 4.5--5.5 亿/天 | <4 亿 或 >6 亿 | 前端埋点故障、流量异常 |
| 视口事件/曝光比 | 3.5--4.5 | <3.0 或 >5.0 | IntersectionObserver 回调异常 |
| 满意度分数均值 | 0.25--0.35 | 偏移 >2 sigma | 标注计算逻辑变更、AB 实验泄漏 |
| IPW 权重极值比 | $w_{\max} / w_{\min} < 50$ | >50 | 随机化实验样本不足 |
| 特征缺失率 | <1% | >3% | Kafka Feature Broker 故障 |

异常检测使用**滚动 Z-score**：对每个指标维护 30 天滚动均值和标准差，当日值超出 $\pm 3\sigma$ 时触发告警。

#### Schema Drift 检测

Spark 作业在写入 Parquet 前，对比当前批次 schema 与 Schema Registry 中的注册 schema：
- **列增减检测**：新增列自动标记 `@new`，缺失列触发阻断告警
- **类型漂移检测**：`dwell_seconds` 从 float 变为 int 等类型变更触发阻断
- **值域检测**：`satisfaction` 超出 [0, 1] 范围的行被隔离到 quarantine 表

#### 时效性 SLA (Freshness SLAs)

| 数据产物 | SLA | 违反后果 |
|----------|-----|----------|
| 行为事件表 | T+15 分钟 | 模型重训延迟；触发 oncall 页面 |
| 特征表 | T+30 分钟 | 训练使用陈旧特征；可容忍 1 小时 |
| 归因训练数据 | T+6 小时 | 当日模型重训取消，使用前一天数据 |
| IPW 权重表 | 月度更新 +2 天容忍 | 位置偏差修正略有陈旧；不阻断训练 |

SLA 违反通过 **Grafana** 仪表板实时监控，P0 违反（归因数据延迟 >8 小时）触发 oncall 升级。
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 视口曝光检测 (Viewport Exposure Detection)

当商品 $i$ 在用户视口中以足够的时长和面积可见时，被认为是**已曝光**的：

$$\text{exposed}(i) = \mathbb{1}\bigl[\text{viewport\_dur}(i) > \tau \;\land\; \text{visible\_pct}(i) > 0.5\bigr]$$

其中 $\tau$ 通常为 1 秒（可按实验配置）。`IntersectionObserver` API 报告的 `visible_pct` 是商品边界框与视口交集的比例。

### 位置偏差修正 (Position Bias Correction via IPW)

用户更频繁地查看靠前位置，在行为标注中产生**位置偏差（position bias）**。我们使用 **IPW (Inverse Propensity Weighting)** 进行修正：

$$w_k = \frac{1}{P(\text{examine} \mid \text{pos} = k)}$$

其中 $P(\text{examine} \mid \text{pos} = k)$ 通过**随机化实验（randomization experiments）**估计：对约 0.1% 的查询，我们随机打乱结果并按位置测量查看率。

去偏后的商品 $i$ 在位置 $k$ 的标注为：

$$\text{label}_{\text{debiased}}(i) = w_k \cdot \text{label}_{\text{raw}}(i)$$

处于低位置但仍被点击/交互的商品被**上调权重**（模型学到它们确实相关，而非仅受位置青睐）。

### 模块归因折扣 (Module Attribution Discount)

在现代搜索结果页中，同一商品可能出现在多个模块中（自然结果、赞助轮播、"相似商品"组件）。原始标注会对商品相关性进行**重复计数（double-count）**。多触点归因折扣按曝光比例分配功劳：

$$\text{label}_{\text{adj}}(i, m) = \text{label}_{\text{raw}}(i) \cdot \frac{\text{exposure}(i, m)}{\sum_{m'} \text{exposure}(i, m')}$$

其中 $m$ 是模块索引，$\text{exposure}(i, m)$ 是商品 $i$ 在模块 $m$ 中的视口停留时长。

### 位置去偏的 LambdaMART (Position-Debiased LambdaMART)

排序模型（LambdaMART）使用 IPW 加权的 pairwise loss 进行训练。对于文档对 $(i, j)$，其中 $i$ 被偏好：

$$\mathcal{L}_{\text{IPW}} = \sum_{(i,j)} w_{k_i} \cdot w_{k_j} \cdot \bigl\lvert\Delta \text{NDCG}(i,j)\bigr\rvert \cdot \log\bigl(1 + e^{-(s_i - s_j)}\bigr)$$

其中 $s_i, s_j$ 为模型分数，$k_i, k_j$ 为位置，$\Delta\text{NDCG}(i,j)$ 是在当前排序中交换 $i$ 和 $j$ 后的 NDCG 变化。

### 满意度评分 (Satisfaction Score -- Composite Label)

最终训练标注将多个信号组合为一个满意度评分：

$$\text{satisfaction}(i) = \alpha \cdot \text{dwell\_norm}(i) + \beta \cdot \text{engaged}(i) + \gamma \cdot \text{converted}(i)$$

其中 $\alpha + \beta + \gamma = 1$，权重通过离线评估调优（通常 $\alpha = 0.3$，$\beta = 0.3$，$\gamma = 0.4$）。

### 数据异常检测 Z-score (Data Anomaly Detection Z-score)

对每日训练数据批次的关键指标 $x_t$，使用 30 天滚动窗口计算异常分数：

$$z_t = \frac{x_t - \bar{x}_{30}}{\sigma_{30}}$$

其中 $\bar{x}_{30}$ 和 $\sigma_{30}$ 分别为最近 30 天的滚动均值和标准差。当 $\lvert z_t \rvert > 3$ 时触发告警，$\lvert z_t \rvert > 5$ 时**阻断当日训练批次**，回退至前一天数据。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

### 规模数据

| 指标 | 数值 | 背景 |
|--------|-------|---------|
| **曝光量** | 每日约 5 亿次曝光，约 20 亿视口事件 | 每个 SRP 渲染 48--100 个可追踪商品 |
| **点击量** | 每日约 2000 万次点击（约 2--5% CTR） | 稀疏信号——这就是视口数据至关重要的原因 |
| **Stream 1 吞吐量** | 峰值约 200K 事件/秒（Sojourner） | Spark Join 以 5 分钟微批次进行 ID 解析 |
| **Stream 2 吞吐量** | 约 50K 特征更新/秒（Kafka） | 商品特征：价格、状况、卖家评分、图片质量 |
| **Spark Join 延迟** | 端到端约 5 分钟（事件到解析会话） | 对离线训练可接受，非实时 |
| **归因处理** | 每日批量，500 节点 Spark 集群约 4 小时 | 处理前一天的完整会话数据 |
| **训练数据量** | 每日快照约 2TB（特征 + 标注） | 30 天保留期，按日期分区 |
| **模型重训周期** | 主排序器每日重训；实验模型每周重训 | 在 14 天归因数据窗口上进行完整重训 |
| **IPW 估计** | 每月通过位置随机化实验更新 | 约 0.1% 的查询参与随机化 |

### 延迟预算

**PBE (Product-Based Experience)** 日志埋点不能降低搜索延迟：

| 组件 | 延迟预算 | 方法 |
|-----------|---------------|----------|
| Trackable ID 注入 | <1ms | 服务端，在 HTML 渲染时添加 |
| IntersectionObserver 初始化 | 每页 <5ms | 异步、非阻塞，在页面绘制后运行 |
| 事件 beacon 发送 | 0ms（异步） | `navigator.sendBeacon()` -- 发射后不管 |
| Sojourner 接收 | N/A（异步） | 与搜索服务路径解耦 |

### 存储与保留

| 数据 | 格式 | 保留期 | 存储量 |
|------|--------|-----------|---------|
| 原始 UBI 事件 | Avro on HDFS | 90 天 | 约 50TB/天 |
| 已解析行为事件 | Parquet on HDFS | 60 天 | 约 10TB/天 |
| 特征表 | Parquet on HDFS | 30 天 | 约 5TB/天 |
| 归因训练数据 | Parquet on HDFS | 30 天 | 约 2TB/天 |
| IPW 权重表 | CSV（小文件） | 永久保留 | 约 10MB/月 |
| 数据质量报告 | JSON on HDFS | 180 天 | 约 50MB/天 |
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|----------|----------|----------|------------------|
| **曝光追踪** | 仅点击标注 | 基于视口的 **PBE (Product-Based Experience)** 标注 | **视口** -- 点击仅占 2--5% CTR。视口捕获了用户看到但未点击的 95% 以上商品，提供密集监督信号。 |
| **特征日志** | 同步（嵌入搜索响应中） | 异步（Kafka） | **异步** -- 同步日志为搜索延迟增加 20--50ms，违反了我们 <5ms 的埋点预算。Kafka 将特征采集与服务解耦。 |
| **归因模型** | 末次触点（last-touch，功劳归于最后一个被查看的模块） | 多触点（multi-touch，按曝光加权） | **多触点** -- 商品出现在 SRP 的多个模块（自然结果、轮播、广告）中。末次触点会过度归功于最后一个模块，而低估发现性模块的贡献。 |
| **位置偏差处理** | 不处理（信任原始标注） | 基于随机化实验的 **IPW (Inverse Propensity Weighting)** | **IPW** -- 不修正的话，模型学到的是复制位置偏差而非真实相关性。0.1% 的随机化成本相比 +1.8% 的 NDCG 提升微不足道。 |
| **数据时效性** | 纯每日批量 | 流式 + 批量混合 | **混合** -- 流式（Kafka + Spark Streaming）使特征可用时间比纯批量提前约 5 小时。会话级归因仍需每日批量（需要完整会话数据）。 |

### 详细权衡：仅点击 vs. 视口标注

```
Click-only:
  + Simple instrumentation (just log clicks)
  + Low data volume (~20M events/day vs 2B)
  + No IntersectionObserver complexity
  - 95% of impressions have no label (sparse)
  - Position bias undetectable (can't distinguish "not seen" from "seen but not clicked")
  - Model learns CTR, not relevance

Viewport (PBE):
  + Dense labels for every impression
  + Enables position bias correction (know what was seen)
  + Richer signal (dwell, engagement depth)
  - 100x more data volume to process
  - IntersectionObserver has mobile edge cases
  - More complex attribution pipeline
```

**结论**：100 倍的数据量增长换来的是标注质量的本质提升。稀疏标注是排序模型质量的首要瓶颈——视口数据消除了这个瓶颈。

### 详细权衡：每日批量 vs. 流式

混合方案将流式用于特征、批量用于归因：

| 方面 | 纯批量 | 纯流式 | 混合（我们的选择） |
|--------|-----------|---------------|---------------------|
| 特征时效性 | T+24h | T+5min | T+5min（流式） |
| 归因时效性 | T+24h | T+5min | T+24h（批量） |
| 复杂度 | 低 | 高 | 中 |
| 成本 | 低 | 高 | 中 |
| 会话完整性 | 完整会话 | 部分会话 | 归因使用完整会话 |

归因需要完整的会话数据（用户可能在看到商品 30 分钟后才点击）。流式归因会产生不完整、不准确的标注。混合方案在加速特征可用性的同时避免了这一问题。

### 迭代与评估 (Iteration & Evaluation)

#### 评估方法论 (Evaluation Methodology)

PBE 管线的迭代采用**四层评估**策略，从快速离线验证到全量上线逐步推进：

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **离线回放** | 用历史数据比较新旧标注方案产出的模型 NDCG | 小时级 | 标注算法变更的快速迭代 |
| **Shadow 评估** | 新管线与生产管线并行运行，对比输出差异 | 天级 | Schema 变更、数据质量规则变更的安全验证 |
| **Interleaving** | Team-Draft Interleaving (TDI) 比较两个排序模型 | 天级 | 新标注方案训练的模型 vs 旧标注方案训练的模型 |
| **A/B 测试** | 5% 流量分割，测量 NDCG、CTR、GMV | 1-2 周 | 全量上线前的最终验证 |

#### 关键监控指标 (Key Monitoring Metrics)

| 指标 | 目标 | 告警条件 |
|------|------|----------|
| NDCG@10 周趋势 | 稳定或上升 | 连续 3 天下降 >0.5% |
| 训练数据覆盖率 | >98% 曝光有标注 | <95% |
| IPW 权重方差 | $\text{Var}(w) < 100$ | >200（随机化样本不足） |
| 归因管线延迟 | <6 小时 | >8 小时 |
| 模型重训成功率 | >99% | <95%（连续 2 天失败） |

#### 超参数调优 (Hyperparameter Tuning)

| 参数 | 调优方法 | 当前最优值 | 备注 |
|------|----------|-----------|------|
| $\tau$（曝光时长阈值） | 离线 NDCG grid search | 1.0 秒 | 0.5 秒过于宽松（噪声高），2.0 秒过于严格（丢失 30% 曝光） |
| $\alpha, \beta, \gamma$（满意度权重） | 离线回放 + A/B 验证 | 0.3, 0.3, 0.4 | $\gamma > 0.5$ 时模型过度偏向高价商品 |
| 随机化流量比例 | ROI 分析 | 0.1% | 0.05% 时 IPW 方差增大 3 倍；0.5% 时用户投诉增加 |
| 归因数据窗口 | 离线回放 | 14 天 | 7 天不足以捕捉月度购买模式；30 天计算成本翻倍 |
| 视口可见百分比阈值 | 眼动追踪实验 | 50% | 30% 时假阳性率升高 20% |

### 典型失败模式与修复 (Failure Modes & Fixes)

1. **视口事件风暴 (Viewport Event Storm)**
   - **根因**：前端部署引入了一个 bug，导致 IntersectionObserver 在每帧（60fps）都触发回调，而非仅在阈值交叉时触发。视口事件量从 20 亿/天暴涨至 500 亿/天。
   - **影响**：Sojourner 消费组 lag 飙升至 2 小时，Kafka 磁盘使用率达到 90%。
   - **修复**：(1) 紧急回滚前端部署。(2) 在 Sojourner 入口添加**逐查询事件数上限**（每次 SRP 最多 200 个视口事件），超出部分丢弃并计数。(3) 添加 Kafka 入口流量监控告警（事件率 >5 倍基线触发 P0 告警）。

2. **IPW 权重爆炸 (IPW Weight Explosion)**
   - **根因**：月度随机化实验中某个品类的样本量过小（<100 次查询），导致尾部位置（位置 40+）的 $P(\text{examine} \mid \text{pos}=k)$ 估计接近 0，IPW 权重 $w_k$ 趋于无穷。
   - **影响**：少量低位置商品获得极大权重，扭曲 LambdaMART 训练，NDCG 下降 1.2%。
   - **修复**：(1) 对 IPW 权重施加**截断 (clipping)**：$w_k = \min(w_k, w_{\text{cap}})$，其中 $w_{\text{cap}} = 50$（通过离线实验确定）。(2) 增加尾部位置的随机化样本量。(3) 使用**自归一化 IPW (Self-Normalized IPW, SNIPW)**：$w_k^{\text{SN}} = \frac{w_k}{\sum_{k'} w_{k'}}$，降低极端权重的影响。

3. **特征-标注时间错位 (Feature-Label Temporal Misalignment)**
   - **根因**：Stream 2（特征流）的 Spark Streaming 作业在一次集群升级后延迟了 3 小时。归因管线在特征表尚未更新时就开始了每日批次，导致训练数据中的特征是前一天的，而标注是当天的。
   - **影响**：模型在陈旧特征上训练，学到了错误的特征-标注关联。上线后 CTR 下降 0.8%，2 天后才被发现。
   - **修复**：(1) 归因管线启动前增加**特征时效性检查**：验证特征表的最新分区时间戳在 T-1 小时内。(2) 如果特征表陈旧，管线**等待并重试**最多 2 小时，超时后使用前一天完整数据并发出 P1 告警。(3) 在训练数据 Parquet 元数据中记录特征表时间戳，支持事后审计。
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## 对抗性答辩问答 (Adversarial Defense Q&A)

**Q: 基于 IntersectionObserver 的视口追踪在移动端浏览器上不太可靠。你们的实际准确率是多少？**

> **承认局限**：移动端视口追踪确实存在边界情况。iOS Safari 在惯性滚动期间会延迟 IntersectionObserver 回调，部分 Android WebView 在快速滑动手势时不触发事件。
>
> **应对措施**：我们使用 200ms 滚动停止轮询回退（scroll-end polling fallback）来补充 IntersectionObserver：当滚动停止时，强制检查所有可见商品。我们还将视口日志与服务端的"首屏（above-the-fold）"位置启发式规则进行交叉验证（位置 1--4 的商品假定 100% 可见）。
>
> **数据**：在一项眼动追踪验证研究（N=500 会话）中，我们的视口标注与实际眼睛注视数据的一致率为 85%。主要错误模式是快速滚动（在 <1 秒内滚过的商品被记为"未曝光"但有时确实被看到了）。这是一个保守型误差——它低估了曝光量，对训练数据而言比高估更安全。

---

**Q: 你们的 IPW (Inverse Propensity Weighting) 位置偏差修正需要随机化实验。随机重排结果是否会损害用户体验？**

> **承认局限**：是的，随机化会降低参与查询的短期用户体验。
>
> **应对措施**：我们仅对约 0.1% 的查询进行随机化（用户影响较小），且仅在"质量层级（quality tier）"内交换商品（相关性分数相近的商品之间交换）。我们绝不会将一个真正不相关的商品放在位置 1。随机化还限制在非敏感品类（不包括健康/安全类目）。
>
> **数据**：在 0.1% 随机化流量中，CTR 比排序流量下降约 15%。但由此推导的 IPW 权重为其余 99.9% 的流量提升了模型质量。净影响：排序模型 NDCG 提升 +1.8%，转化为全站 GMV 提升 +0.5%。随机化的投资回报率极高。

---

**Q: Stream 1 的 5 分钟微批次延迟意味着你们的"近实时"声称有误导性。5 分钟延迟如何影响模型质量？**

> **承认局限**：5 分钟不是实时的，我们不会将此数据用于在线特征。
>
> **应对措施**：5 分钟延迟仅影响离线特征聚合。训练管线本来就使用每日批量归因（需要完整会话数据）。流式层的价值在于使特征比纯批量提前 5 小时可用于*次日的*训练批次。这将反馈循环从约 30 小时缩短到约 25 小时。
>
> **数据**：将反馈循环从 30 小时减少到 25 小时，使模型对趋势变化（如新品上线）的响应速度提高了约 1 天，在趋势查询上可测量到 0.3% 的交互提升。

---

**Q: 多触点归因听起来很有道理，但增加了很多复杂度。你们是否衡量过它实际上比末次触点更好？**

> **承认局限**：多触点归因确实更难实现、调试和向利益相关者解释。
>
> **应对措施**：我们进行了为期 4 周的 A/B 测试：在其他条件相同的情况下，比较使用多触点标注和末次触点标注训练的模型。
>
> **数据**：多触点模型在自然结果上 NDCG 提升 +0.8%，在模块多样性查询（商品同时出现在自然结果和轮播中）上提升 +1.2%。对于单模块查询（商品仅出现在自然结果中），提升微乎其微（+0.1%）。因此多触点归因特别适用于日益常见的多模块 SRP 布局，验证了这项投入的价值。

---

**Q: 你们的数据质量监控使用简单的 Z-score 异常检测。这在非平稳的电商场景下够用吗？**

> **承认局限**：Z-score 假设近似正态分布和平稳性。在 Black Friday 等购物高峰期间，正常流量就会突增 3-5 倍，简单 Z-score 会产生大量误报。
>
> **应对措施**：我们使用**分层 Z-score**：(1) 按日期类型分层（工作日 vs 周末 vs 节日），每层独立维护滚动统计。(2) 对已知事件（大促、新市场上线）预先注入 **adjustment factor**，调高该时段的 baseline。(3) 对于季节性强的指标（如曝光量），额外使用**同比 (YoY) 对比**：当日值与去年同期对比，捕捉趋势偏移。
>
> **数据**：引入分层后，误报率从每周约 12 次降至约 2 次，同时保持对真实异常（管线故障）的召回率 >95%。

---

**Q: Schema 演进看起来很谨慎，但实际上你们多久做一次不兼容的 schema 变更？这个机制是否被真正考验过？**

> **承认局限**：大多数 schema 变更确实是简单的新增字段，兼容性检查很少被触发。
>
> **应对措施**：在过去 18 个月中，我们经历了 2 次重大不兼容变更：(1) `dwell_time_ms` (int32) -> `dwell_time_s` (float64)，因为毫秒精度在移动端不可靠。(2) 弃用 `click_type` 枚举并替换为 `engagement_signals` 数组，支持更灵活的信号类型。两次都使用了双写过渡期（2 周），下游消费者逐步迁移。Schema Registry 的兼容性检查在第一次变更时阻止了一个 PR，该 PR 试图直接删除旧字段而未添加新字段——这本会导致所有下游 Spark 作业失败。
>
> **数据**：双写过渡期的额外存储成本约 8%（两份字段并存 2 周），但避免了生产中断。在 18 个月内，PBE schema 从 v12 演进到 v23，零次因 schema 变更导致的管线故障。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## 口头大纲 (Verbal Outline)

### 3 分钟版本

1. **(30s) 问题**：基于点击的训练数据是稀疏的（2--5% CTR）且存在位置偏差。95% 的曝光完全不产生训练信号。

2. **(45s) 方案**：基于视口的曝光追踪，使用 IntersectionObserver，加上双流接入——行为事件通过 Sojourner，商品特征通过 Kafka。

3. **(60s) 管线**：Trackable ID 在服务端注入每个搜索结果。IntersectionObserver 触发视口事件。Sojourner 拼接会话。Spark Join 以 5 分钟微批次解析 ID。归因引擎应用 **IPW (Inverse Propensity Weighting)** 位置偏差修正和多触点模块功劳分配。数据质量门控验证 schema 一致性和异常检测。输出：按日期和模型版本分区的 Parquet 训练数据。

4. **(30s) 生产规模**：每日 5 亿曝光，20 亿视口事件，5 分钟微批次解析，每日在 14 天归因数据窗口上重训模型。

5. **(15s) 影响**：IPW 去偏标注带来 +1.8% 的 NDCG 提升。eBay 的每个排序模型都在该管线的输出上进行训练。

### 10 分钟版本

1. **(1.5 min) 为什么点击不够**：稀疏性（2--5% CTR 意味着 95% 以上的曝光没有标注）、位置偏差（靠前结果不论质量都会被点击）、信任偏差，以及点击 != 满意度（跳回与深度交互被同等计数）。

2. **(2 min) 视口追踪设计**：IntersectionObserver API，阈值调优（$\tau$ = 1s，visible_pct > 50%），移动端边界情况（iOS 惯性滚动的 200ms 轮询回退方案），眼动追踪验证研究（85% 准确率，保守型误差模式）。

3. **(2 min) 双流架构**：Stream 1 -- 行为事件通过 Sojourner（200K 事件/秒）到 Spark Join（5 分钟微批次进行会话 + ID 解析）。Stream 2 -- 商品特征通过 Kafka Feature Broker（50K 更新/秒）到 Spark Streaming 特征表。为什么用两个流：行为事件需要会话上下文，特征可独立更新。Schema 演进通过 Confluent Schema Registry 管理，支持向前/向后兼容。

4. **(1.5 min) 归因深入**：**IPW (Inverse Propensity Weighting)** 位置偏差修正——通过 0.1% 随机化实验估计，每月刷新，限制在质量层级内随机化。多触点模块归因——按曝光加权的功劳分配。使用 IPW 加权 pairwise loss 训练位置去偏的 LambdaMART。

5. **(1.5 min) 数据质量与迭代**：四层数据质量门控——异常检测（滚动 Z-score）、schema drift 检测、值域验证、时效性 SLA。四层评估方法论——离线回放、Shadow 评估、Interleaving、A/B 测试。超参数调优表（$\tau$、满意度权重、随机化比例、数据窗口）。

6. **(1 min) 生产约束**：规模数据（5 亿曝光、2TB 每日快照、500 节点 Spark 集群、4 小时每日归因批处理）。延迟预算（<1ms trackable ID 注入、异步 beacon 发送、对搜索延迟零影响）。三个典型失败模式：视口事件风暴、IPW 权重爆炸、特征-标注时间错位。

7. **(0.5 min) 关键教训**：IPW 随机化的投资回报率极高（0.1% 流量成本换取 +1.8% NDCG）。多触点归因仅在多模块 SRP 布局下回报显著。数据质量门控是管线可靠性的基石——没有它，上游微小故障会悄无声息地污染训练数据。
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def populate_pbe_pipeline() -> None:
    """Find the pbe-pipeline SystemDesign record and populate all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            print(f"[FAIL] No SystemDesign record found with slug='{SLUG}'.")
            print("       Run scripts/seed_system_designs.py first.")
            sys.exit(1)

        record.overview = OVERVIEW.strip()
        record.architecture = ARCHITECTURE.strip()
        record.dataflow = DATAFLOW.strip()
        record.formulas = FORMULAS.strip()
        record.production_constraints = PRODUCTION_CONSTRAINTS.strip()
        record.tradeoffs = TRADEOFFS.strip()
        record.defense = DEFENSE.strip()
        record.verbal_outline = VERBAL_OUTLINE.strip()

        db.commit()
        print(f"[DONE] Updated pbe-pipeline (id={record.id}) with all 8 sections.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_pbe_pipeline()
