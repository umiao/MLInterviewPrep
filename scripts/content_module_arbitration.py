"""Populate module-arbitration system design with all 8 markdown sections.

Content sourced from docs/PLAN_system_design_showcase.md section 6.1.
Idempotent: overwrites existing content for the module-arbitration slug.

Chinese translation with English technical terms preserved (bold + first-use
explanation). Formulas and code blocks kept as-is.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "module-arbitration"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

eBay 的**搜索结果页 (SRP, Search Results Page)** 传统上采用**固定模块布局**：
自然搜索结果占据预设位置，广告和促销模块被硬编码地插入特定槽位。这种架构在
小规模下运行良好，但随着业务增长暴露出三个递进式问题：

### 问题 (The Problem)

1. **模块缺乏价值信号。** 没有机制评估哪个模块每次曝光创造最大价值。一个
   促销 banner 可能占据黄金位置，却比被挤到屏幕下方的自然结果产生更少的
   用户互动。

2. **静态分配忽略上下文。** 最优页面组合取决于查询意图、用户群体、设备类型
   和时间段。固定布局对品牌查询 "Nike Air Max" 和长尾查询 "vintage brass
   lamp shade" 一视同仁——但理想的广告、推荐和自然结果配比大相径庭。

3. **新模块的扩展瓶颈。** 每种新模块类型（视觉相似度、跨类目推荐、品牌
   赞助广告）都需要产品团队谈判一个固定页面槽位。这造成组织摩擦并拖慢
   实验节奏。

### 核心洞察 (The Insight)

将 SRP 构建为一个**内容市场 (Content Marketplace)**，模块基于预测价值竞争
页面空间。每种模块类型提交一个"出价"（预测的用户互动价值），由集中式仲裁
系统在满足用户体验约束的前提下分配页面位置以最大化总页面价值。

### 业务影响 (Business Impact)

- 实现跨模块类型的**数据驱动空间分配**
- 提供**透明的"价格发现"机制**——每个团队可以看到自己模块的价值与替代方案的对比
- 从 12 种模块类型扩展到 200+ 种，无需手动协商槽位
- 页面级 **GMV (Gross Merchandise Value，成交总额)** 提升约 4%
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

系统分为**离线预计算层**（构建价值估计）和**在线两阶段查询执行**管道（执行
实时仲裁）。

### 离线 / 预计算层 (Offline / Pre-computing Layer)

| 组件 | 职责 |
|------|------|
| **Module Registration (模块注册)** | 元数据存储：模块类型、位置约束、A/B 变体注册、内容提供方端点 |
| **Module Performance & Features (模块表现与特征)** | 从 Kafka 用户互动流汇总的历史 CTR (Click-Through Rate，点击率)、CVR (Conversion Rate，转化率)、每模块收入 |
| **Contextual Value Predictor (上下文价值预测器)** | **梯度提升模型** (XGBoost/LightGBM) 根据查询上下文预测每个模块的价值 |
| **Global Thompson Sampling (全局汤普森采样)** | 对新模块或低流量模块进行探索/利用权衡；维护每模块的 **Beta 后验分布** |
| **Feature Engineering & Model Training (特征工程与模型训练)** | 基于 6 个月互动数据的每日批量训练；特征包括查询意图、用户分群、设备、时间段 |
| **Module Register Table (模块注册表)** | 存储所有已注册模块（约 200 个）及其预计算的基础分数；每 6 小时刷新 |

### 在线两阶段查询执行 (Online Two-Stage Query Execution)

**Stage 1: River & Module Content (河流与模块内容)** (Adaptive **HMAC (Hierarchical Module Allocation & Composition，层级模块分配与组合)** + top-N 选择)

- 查询上下文 + 用户特征从注册表中选择**符合条件的模块**（从约 200 个中选出
  15-30 个候选）
- 对每个候选模块并行获取内容：
  - In-Cassini 模块：本地检索
  - 外部提供方：通过 SaaS/IIS 流获取，**50ms 超时**
- Stage 1 延迟预算：**<20ms**（选择 + 内容获取启动）

**Stage 2: Module Arbitration (模块仲裁 - 核心)**

这是中央决策引擎，包含四个子组件：

1. **Module Placement Optimizer (模块位置优化器)** -- 决定每个位置区域
   （顶部、中间、底部、侧边栏）的可用槽位数量和位置
2. **Module Filter (模块过滤器)** -- 应用质量阈值（最低预测 CTR、内容质量
   分数）以防止最差 UX 情况
3. **River Composition & Value Maximizer (河流组合与价值最大化器)** -- 求解
   带约束优化问题（**LP (Linear Programming，线性规划)** 松弛 + 取整）以
   最大化总页面价值
4. **Page Composer (页面组合器)** -- 将模块与自然结果交错的最终布局，遵守
   视觉约束（不相邻广告、多样性规则）

Stage 2 延迟预算：完整仲裁管道 **<10ms**。

### 反馈回路 (Feedback Loop)

用户互动事件（点击、曝光、加购）通过 **Kafka** 流回离线层，为模型重训练和
**Thompson Sampling (汤普森采样)** 后验更新形成闭环。

### Kafka 流管道详解 (Kafka Stream Pipeline Detail)

反馈回路是整个系统的**数据基础设施骨干**。原始用户互动事件流经多阶段流处理
管道：

**Event Schema (事件模式)**（简化版）：

```
{
  "event_type": "impression" | "click" | "add_to_cart" | "purchase",
  "timestamp_ms": 1717430400000,
  "query_id": "uuid",
  "user_id": "hashed",
  "module_id": "sponsored_brand_42",
  "module_type": "sponsored_brand_ad",
  "position_zone": "top" | "middle" | "bottom" | "sidebar",
  "position_index": 3,
  "page_id": "uuid",           // groups all modules on one SRP render
  "session_id": "uuid",
  "device_type": "mobile" | "desktop",
  "query_intent": "brand" | "category" | "longtail",
  "revenue_cents": 0,          // non-zero only for purchase events
  "dwell_time_ms": null        // populated on click events via beacon
}
```

**Stream Processing Topology (流处理拓扑)**：

```
Raw Kafka Topic (按 query_id 分区)
  |
  v
Stage 1: Deduplication & Sessionization (Kafka Streams)
  - Idempotent producer + transactional consumer 保证 exactly-once
  - Session windows (30 分钟间隔) 将事件分组为用户会话
  |
  v
Stage 2: Attribution Join (Kafka Streams / Flink)
  - 将曝光与同一会话内的下游点击/购买进行 join
  - 计算每模块归因：该点击是否归属于模块 X？
  |
  v
Stage 3: Aggregation (Spark Structured Streaming, 5 分钟微批次)
  - 每模块 CTR、CVR、收入聚合（小时 + 天粒度）
  - 并行输出到两个目标：
    |
    +-- Redis: Thompson Sampling 后验更新（每小时）
    |   Key: "ts:{module_id}" -> {alpha, beta, last_updated}
    |
    +-- HDFS / Feature Store: 模型训练特征（每日批量）
        按日期分区，约 2TB/天 压缩 Parquet
```

**Exactly-once 保证**：Kafka producer 使用 `enable.idempotence=true`
配合事务写入。Consumer 运行在 `read_committed` 隔离级别。归因 join 是
确定性的（相同输入 -> 相同输出），故障后重放产生相同结果。

**Backpressure (背压) 处理**：Consumer group 基于 **KEDA** 的 lag 指标
自动扩缩容。如果 lag 超过 15 分钟，系统回退到最近一次成功聚合的结果——
Thompson Sampling 后验略有陈旧，但 LP 求解器仍使用最新缓存的分数。lag 达到
30 分钟时触发告警，需人工干预。
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 请求路径（在线） (Request Path - Online)

```
User Query (用户查询)
  |
  v
Query Context Extraction (查询上下文提取)
  (查询意图分类, 用户画像查找, 设备/地理特征)
  |
  v
Stage 1: Candidate Module Selection (候选模块选择)
  - 从注册表中筛选符合条件的模块 (15-30 from ~200)
  - 并行从提供方获取内容 (50ms timeout)
  |
  v
Stage 2: Module Arbitration (模块仲裁)
  |-- Placement Optimization: 每个位置区域分配多少槽位？
  |-- Quality Filtering: 最低 CTR/质量阈值门控
  |-- Value Maximization: LP 松弛 + 贪心取整
  |-- Page Composition: 交错模块的最终布局
  |
  v
Rendered SRP (发送到客户端)
  |
  v
User Interactions (点击, 曝光, 滚动, 加购)
  |
  v
Kafka Event Stream
```

### 反馈路径（离线） (Feedback Path - Offline)

```
Kafka Event Stream (按 query_id 分区, 约 5 亿曝光/天)
  |
  v
Stage 1: Dedup & Sessionization (Kafka Streams, exactly-once)
  |
  v
Stage 2: Attribution Join (曝光 <-> 点击/购买 在同一会话内)
  |
  v
Stage 3: Aggregation (Spark Structured Streaming, 5 分钟微批次)
  |
  v
+-- Redis: TS Posterior Update (每小时)
|     Key: "ts:{module_id}" -> {alpha, beta, last_updated}
|     滑动窗口衰减在读取时应用
|
+-- HDFS Feature Store (6 个月滚动窗口, 约 2TB/天 Parquet)
|     |
|     v
|     XGBoost/LightGBM Model Training (每日批量)
|       -> 更新 Contextual Value Predictor
|
+-- Module Register Table Refresh (每 6 小时)
      -> 预计算基础分数 = 最新模型的 E[V_m] + TS 先验
```

**为什么 TS 每小时更新但模型每天训练？** Thompson Sampling 后验是简单的
**充分统计量 (sufficient statistics)**（alpha, beta 计数），更新代价极低——
每小时刷新可以捕捉日内变化（闪购、趋势查询）。而 XGBoost 模型基于 6 个月
的特征（100+ 维度）训练，需要完整的 Spark 作业（约 45 分钟）。更频繁的
模型重训练仅带来 <0.3% 的 CTR 提升（通过离线回放测量），不足以证明
计算成本的合理性。

### 关键数据存储 (Key Data Stores)

| 存储 | 技术 | 规模 | 刷新频率 |
|------|------|------|----------|
| Module Register Table (模块注册表) | In-memory cache (Cassini) | 约 200 条 | 每 6 小时 |
| Feature Store (特征存储) | HDFS + Spark | 6 个月互动数据 | 流式摄入 |
| Thompson Sampling State | Redis | 每模块 Beta 后验 | 每小时 |
| Engagement Log (互动日志) | Kafka + HDFS | 约 5 亿曝光/天 | 实时 |
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 每模块期望价值 (Expected Value per Module)

将模块 $m$ 放置在查询 $q$ 对用户 $u$ 的预测价值：

$$E[V_m] = P(\text{click} \mid m, q, u) \cdot \text{Revenue}(m) + \alpha \cdot P(\text{engagement} \mid m)$$

其中：
- $P(\text{click} \mid m, q, u)$ 是 XGBoost 输出的上下文 CTR 预测
- $\text{Revenue}(m)$ 是模块 $m$ 每次点击的预期收入
- $\alpha$ 是平衡收入与互动的可调权重
- $P(\text{engagement} \mid m)$ 捕捉非点击互动（滚动、停留时间）

### Thompson Sampling 模块探索 (Thompson Sampling for Module Exploration)

#### 为什么选择 Beta-Bernoulli？(Why Beta-Bernoulli?)

每次模块曝光是一个 **Bernoulli 试验 (伯努利试验)**：用户要么点击（成功,
$y=1$）要么不点击（$y=0$）。**Beta 分布**是 Bernoulli 似然函数的
**共轭先验 (conjugate prior)**，这意味着后验更新是解析可求的——无需
**MCMC (Markov Chain Monte Carlo，马尔可夫链蒙特卡洛)** 或变分推断：

$$\text{Prior: } \theta_m \sim \text{Beta}(\alpha_m, \beta_m)$$

$$\text{Likelihood: } y \mid \theta_m \sim \text{Bernoulli}(\theta_m)$$

$$\text{Posterior: } \theta_m \mid y \sim \text{Beta}(\alpha_m + s_m, \beta_m + f_m)$$

其中：
- $s_m$ = 滑动窗口内的"成功"次数（点击）
- $f_m$ = 滑动窗口内的"失败"次数（曝光但未点击）
- $\alpha_m, \beta_m$ = 先验参数

这种共轭性意味着每次后验更新是 $O(1)$——只需递增两个计数器——使得在
50K QPS 下可行。

#### 滑动窗口变体 (Sliding-Window Variant)

标准 TS 假设平稳奖励，但模块 CTR 会随季节性、库存变化和促销活动而变化。
我们使用指数衰减：

$$s_m^{(t)} = \sum_{d=0}^{6} \gamma^d \cdot s_m^{(t-d)}, \quad \gamma = 0.95$$

**有效样本量 (effective sample size)** 为 $\frac{1}{1-\gamma} \approx 20$
天的等效观测，这意味着后验会"忘记"旧表现，在 3-5 天内适应制度变化。

#### 冷启动先验迁移 (Cold-Start Prior Transfer)

对于零观测的**新模块**，我们使用模块类型相似性来预热 Beta 先验：

1. 基于元数据特征（类目、广告 vs 自然、内容格式、目标位置区域）计算
   **模块类型嵌入 (module type embedding)**
2. 在嵌入空间中通过余弦相似度找到 $k=5$ 个最近的现有模块
3. 将先验设为它们后验的加权平均：

$$\alpha_m^{(0)} = \sum_{j \in \text{NN}(m)} w_j \cdot \alpha_j, \quad \beta_m^{(0)} = \sum_{j \in \text{NN}(m)} w_j \cdot \beta_j$$

其中 $w_j \propto \text{sim}(m, j)$ 且 $\sum w_j = 1$。

这避免了在纯随机探索上浪费曝光。例如：新的 "sponsored brand ad" 模块从
现有广告类模块继承先验（典型值 $\alpha^{(0)} \approx 8$,
$\beta^{(0)} \approx 200$，意味着约 3.8% CTR 先验），而非从无信息的
$\text{Beta}(1,1)$ 开始。

#### 分数融合：TS + 上下文价值预测器 (Score Fusion: TS + Contextual Value Predictor)

上下文价值预测器 (XGBoost) 输出一个**利用分数 (exploitation score)**
$\hat{V}_m^{\text{exploit}}$。Thompson Sampling 提供一个**探索加成
(exploration bonus)**。融合方式为：

$$V_m^{\text{final}} = (1 - \epsilon) \cdot \hat{V}_m^{\text{exploit}} + \epsilon \cdot \theta_m \cdot \text{Revenue}(m)$$

其中：
- $\theta_m$ 是从 $\text{Beta}(\alpha_m, \beta_m)$ 中的一次采样——采样的
  随机性驱动探索
- $\epsilon$ 是探索权重，从 0.3（新模块）退火到 0.05（曝光 >10K 的成熟模块）

对于成熟模块，XGBoost 分数占主导。对于新/低流量模块，TS 采样引入的方差
自然地探索后验不确定性高（Beta 分布宽）的欠观测模块。

#### 大规模批量 Thompson Sampling (Batched Thompson Sampling at Scale)

在 50K QPS 下，逐查询采样是浪费的，因为后验在连续查询间几乎不变。替代方案：

- **批次周期 (Batch period)**：每 100ms（约 5K 个查询），从当前后验对每个
  模块抽取一次样本 $\theta_m$
- **缓存 (Cache)**：将采样分数存储在内存查找表中（与 LP 求解器共址，
  <1ms 读取延迟）
- **陈旧度 (Staleness)**：最大 100ms 陈旧，相对于小时级后验更新周期可忽略
- **多样性 (Diversity)**：不同 pod 独立采样，因此跨集群仍有逐查询的探索方差

### 页面价值最大化（整数 LP） (Page Value Maximization - Integer LP)

$$\max \sum_{m \in M} \sum_{p \in P} x_{m,p} \cdot V(m, p)$$

约束条件：

$$\sum_{p \in P} x_{m,p} \leq 1 \quad \forall m \in M \quad \text{(每个模块最多放置一次)}$$

$$\sum_{m \in M} x_{m,p} \leq 1 \quad \forall p \in P \quad \text{(每个位置最多容纳一个模块)}$$

$$x_{m,p} \in \{0, 1\}$$

附加约束：
- **多样性 (Diversity)**：同类型模块不超过 $k$ 个
- **相邻性 (Adjacency)**：连续位置不可出现两个广告模块
- **最低自然结果 (Minimum organic)**：前 $n$ 个位置至少包含 $r$ 个自然结果

**实际实现：** 使用 LP 松弛（允许分数 $x_{m,p} \in [0, 1]$），通过
**最小费用最大流 (MCMF, Min-Cost Max-Flow)** 建模求解。分配问题自然映射为
二部图（一侧模块，另一侧位置），MCMF 求解器在 $O(n \cdot m)$ 时间内完成
（$n$ 个模块和 $m$ 个位置——在 30 x 48 规模的 10ms 预算内完全可行）。
确定性贪心取整在满足硬约束（多样性、相邻性、最低自然结果数）的前提下解决
分数分配。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

| 指标 | 值 | 上下文 |
|------|-----|--------|
| **QPS** | 峰值约 50K 查询/秒（美国市场） | 每个查询触发完整的两阶段仲裁 |
| **每查询候选模块** | 15-30 个（从约 200 个注册模块中筛选） | Stage 1 根据查询上下文激进裁剪 |
| **Stage 1 延迟预算** | <20ms（模块选择 + 内容获取启动） | 内容获取异步执行，50ms 超时 |
| **Stage 2 延迟预算** | <10ms（仲裁：LP + 页面组合） | LP 操作 15-30 个候选，约 48 个页面槽位 |
| **端到端延迟 (P99)** | <150ms 总 SRP 渲染（仲裁约占 30ms） | 主要受外部提供方内容获取延迟影响 |
| **模块注册表规模** | 约 200 个注册模块，每市场约 50 个活跃 | 每 6 小时以离线分数刷新 |
| **离线模型重训练** | 每日批量；Thompson Sampling 后验每小时更新 | 特征存储包含 6 个月互动数据 |
| **数据量** | 约 5 亿曝光/天，约 2000 万点击/天回流 | Kafka 摄入, Spark 处理, HDFS 存储 |

### 延迟分解 (P50) (Latency Breakdown)

```
查询解析 + 上下文提取:              5ms
Stage 1 模块选择:                  12ms
Stage 1 内容获取 (异步):          ~45ms (50ms timeout)
Stage 2 仲裁:
  - 位置优化:                       2ms
  - 质量过滤:                       1ms
  - LP 求解 + 取整:                 5ms
  - 页面组合:                       2ms
Stage 2 合计:                      10ms
响应序列化:                         3ms
---
合计 (不含内容获取):              ~30ms
合计 (含内容获取):        ~75ms P50, ~150ms P99
```

### 扩展性考量 (Scaling Considerations)

- 模块注册表可完全装入内存（约 200 条，<1MB）
- LP 求解器操作的问题规模小（30 模块 x 48 位置），使精确 LP 松弛在延迟
  预算内可行
- Thompson Sampling 状态（Beta 后验）存储在 Redis 中，保证跨 pod 一致性；
  读取延迟 <1ms
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| 探索策略 | UCB (Upper Confidence Bound，上置信界) | Thompson Sampling | **Thompson Sampling** -- 在非平稳奖励下经验表现更好；UCB 对季节性模块表现变化过于保守 |
| 优化范围 | 逐槽位贪心分配 | 整页 LP 优化 | **整页 LP** -- 贪心忽略跨模块交互（如相邻广告的广告疲劳）；LP 以约 2 倍延迟代价捕捉页面级价值 |
| 冷启动模块 | 随机探索 | 基于模块类型相似性先验的上下文 bandits | **上下文 bandits** -- 使用模块类型相似性预热 Beta 先验；纯随机在低质量位置浪费过多曝光 |
| 质量门控 | 硬阈值（低于 X 则阻止） | 目标函数中的软惩罚 | **混合方案** -- 硬门控阻止最差 UX（屏蔽真正低质量模块）；软惩罚为边界模块保留探索机会 |
| 打分位置 | 全部离线（预计算） | 全部在线（实时） | **混合方案** -- 离线预计算基础价值和模块特征（低成本）；在线调整实时上下文如查询意图和用户会话（昂贵但必要） |

### 详细分析：Thompson Sampling vs. UCB

**为什么 TS 在此场景胜出：**

- 模块表现是**非平稳的**（季节趋势、促销活动、库存变化）。带滑动窗口的 TS
  自然适应，因为从后验采样自动基于不确定性平衡探索。
- UCB1 的置信上界 $\sqrt{\frac{2 \ln n}{n_m}}$ 单调递减，意味着即使环境
  发生变化它最终也会停止探索。
- **实证结果：** 滑动窗口 TS 在 Q4 2024（高季节性）期间比固定窗口 TS 的
  累积模块 CTR 高 12%，比 UCB1 高 8%。

### 详细分析：贪心 vs. LP

**为什么整页 LP 值得延迟代价：**

- 贪心分配独立处理每个槽位，忽略**跨模块效应**：广告疲劳（相邻广告降低双方
  点击率）、内容多样性（展示 3 个相似推荐模块浪费页面空间）。
- LP 建模通过约束（相邻规则、类型多样性限制）捕捉这些效应，优化**联合**
  页面价值。
- LP 松弛 + 取整方案将延迟保持在约 5ms（精确 ILP 不可行），同时在 98.7%
  的查询上与精确最优解的差距不超过 2.5%。

### 迭代与评估：我们如何调优系统 (Iteration & Evaluation)

系统设计的一个关键部分是**如何验证和迭代**方案。这往往是中级和 Staff+ 级别
系统设计回答的分水岭。

#### 评估方法论 (Evaluation Methodology)

我们使用**三层评估**策略：

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **离线回放** | 对日志数据进行反事实评估 | 小时级 | 模型/算法变更的快速迭代 |
| **交错测试** | Team-Draft Interleaving (TDI) | 天级 | 以高统计功效比较两个排序策略 |
| **A/B 测试** | 流量分割 (5% treatment) | 1-2 周 | 全量上线前的最终验证 |

**反事实评估 (Counterfactual evaluation)** 使用**逆倾向得分 (IPS, Inverse
Propensity Scoring)**：

$$\hat{V}(\pi_{\text{new}}) = \frac{1}{N} \sum_{i=1}^{N} \frac{\pi_{\text{new}}(a_i \mid x_i)}{\pi_{\text{old}}(a_i \mid x_i)} \cdot r_i$$

其中 $\pi_{\text{old}}$ 是日志策略，$\pi_{\text{new}}$ 是候选策略，$a_i$
是动作（模块放置），$r_i$ 是观测到的奖励。我们使用 **Doubly Robust (DR，
双重稳健)** 估计器在倾向比 $\frac{\pi_{\text{new}}}{\pi_{\text{old}}}$
较大时降低方差。

#### 关键超参数调优 (Key Hyperparameter Tuning)

| 参数 | 方法 | 结果 |
|------|------|------|
| $\alpha$（收入 vs 互动权重） | 离线回放 grid search + A/B 验证 | 最优 $\alpha = 0.35$（偏收入）；$\alpha > 0.5$ 损害长期留存 |
| $\epsilon$ 退火计划（探索权重） | 离线遗憾的贝叶斯优化 | 起始 0.3，在每模块 10K 曝光后退火至 0.05 |
| 多样性限制 $k$（同类型模块上限） | 产品驱动约束 (UX 评审) + A/B 测试 | 广告 $k=3$，推荐 $k=2$；由 UX 团队设定，A/B 验证 |
| 前 $n$ 位中最低自然结果 $r$ | A/B 测试（测量跳出率） | 前 6 位中至少 $r=4$ 个自然结果；低于此值跳出率飙升 15% |
| $\gamma$（TS 衰减因子） | 离线 A/B 比较 $\gamma \in [0.9, 0.99]$ | $\gamma=0.95$ 最佳平衡：0.9 太敏感（噪声大），0.99 适应太慢 |

#### 典型失败模式与修复 (Typical Failure Modes & Fixes)

1. **马太效应反馈回路 (Rich-get-richer feedback loop)**：高 CTR 模块获得更多
   曝光，强化其后验，饿死新模块。**修复**：$\epsilon$ 退火计划确保新模块
   无论竞争模块分数如何都获得最低探索预算。

2. **位置偏差的 CTR 估计 (Position bias in CTR estimation)**：放在顶部位置
   的模块仅因可见性获得更高 CTR，而非内在质量。模型学会过度排名历史上被
   放在高位的模块。**修复**：训练**位置去偏 CTR 模型 (position-debiased CTR
   model)**，参考 Joachims et al. 的方法——训练时包含位置作为特征，但推理时
   设为参考位置。

3. **紧约束下 LP 求解退化 (LP solver degeneration under tight constraints)**：
   当多个硬约束同时激活时（如节日页面的强制促销 banner + 多样性限制 + 最低
   自然结果），LP 可行域收缩，取整产生低质量解。**修复**：约束优先级排序——
   如果 LP 不可行，先放松软约束（多样性限制），再考虑硬约束（最低自然结果）。
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = r"""## 对抗性答辩问答 (Adversarial Defense Q&A)

**Q: Thompson Sampling 假设平稳的奖励分布。模块表现明显是非平稳的（季节性、促销）。你如何为在此使用 TS 辩护？**

> **承认局限 (Limitation acknowledged)：** 你说得对——标准 TS 假设平稳的
> Beta 后验，而模块 CTR 在 Black Friday 或闪购期间可能变化 2-3 倍。
>
> **缓解措施 (Mitigation)：** 我们使用滑动窗口变体：Beta 后验在 7 天滚动
> 窗口上计算，而非全时间。旧观测以每天 $\gamma = 0.95$ 的折扣因子衰减。
> 这使后验"忘记"旧表现，在 3-5 天内适应制度变化。
>
> **数据 (Data)：** 在 A/B 测试中，滑动窗口 TS 在 Q4 2024（高季节性）期间
> 比固定窗口 TS 的累积模块 CTR 高 12%，比 UCB1 高 8%。收敛差距在新上线的
> 促销模块中最大。

---

**Q: 你的整页 LP 声称 <10ms，但整数 LP 是 NP-hard 的。真正的复杂度是多少？**

> **承认局限：** 精确 **ILP (Integer Linear Programming，整数线性规划)**
> 确实是 NP-hard 的。我们在生产环境中不求解精确 ILP。
>
> **缓解措施：** 我们使用 LP 松弛 + 确定性取整。LP 松弛（允许分数分配）通过
> 专用网络流求解器在 $O(n \cdot m)$ 时间内求解（$n$ 个模块和 $m$ 个位置）。
> 取整使用尊重硬约束的贪心过程。
>
> **数据：** 离线分析中，LP 松弛 + 取整方案在 98.7% 的查询上与精确 ILP
> 最优解的差距在 2.5% 以内。1.3% 的最差情况查询涉及 >20 个模块竞争 3-4 个
> 黄金槽位——即便在那里，差距也 <5%。30 模块 / 48 位置的 P99 求解时间为 7ms。

---

**Q: 当外部内容提供方持续缓慢时会怎样？页面不会退化吗？**

> **承认局限：** 是的——慢提供方意味着其模块永远无法通过 50ms 超时，实质上
> 被从市场中移除。
>
> **缓解措施：** 三层防御：
>
> 1. **监控 (Monitoring)** -- 跟踪提供方延迟 P50/P99，在 P50 >40ms 时告警
> 2. **缓存 (Caching)** -- 对半静态内容的提供方（如品牌广告），缓存最近一次
>    成功响应，在 1 小时 TTL 内提供陈旧内容
> 3. **优雅退化 (Graceful degradation)** -- 页面始终使用已响应的模块渲染；
>    永不显示空白槽位。系统记录每次查询中被丢弃的模块供离线分析。
>
> **数据：** 2024 年提供方超时率约为 0.3% 的查询。加上缓存后，有效可用性为
> 99.85%。被丢弃模块的收入影响估计 <0.1% 总页面 GMV。

---

**Q: 顶部位置的模块仅因可见性获得更多点击。这种位置偏差不会污染你的 CTR 模型并形成反馈回路吗？**

> **承认局限：** 是的——**位置偏差 (position bias)** 是 **LTR (Learning-to-Rank，
> 学习排序)** 中有据可查的问题。放在位置 1 的模块仅因可见性比位置 8 获得
> 约 3 倍的 CTR。如果基于原始 CTR 训练，模型会学会延续当前排名而非发现每个
> 模块的真实内在质量。
>
> **缓解措施：** 我们训练一个**位置去偏 CTR 模型 (position-debiased CTR
> model)**，使用 Joachims et al. (2017) 的倾向框架：
>
> $$P(\text{click} \mid m, p) = P(\text{examine} \mid p) \cdot P(\text{click} \mid m, \text{examined})$$
>
> 训练时包含位置 $p$ 作为特征（使模型学习每个位置的检视概率），但在推理时
> 将 $p$ 设为**参考位置**（如位置 4，中位数）。这隔离了内在点击概率
> $P(\text{click} \mid m, \text{examined})$。
>
> **数据：** 应用位置去偏后，CTR 预测准确度提升 6%（通过留出数据集离线评估
> 测量），历史位置与预测分数的相关性从 0.72 降至 0.31。

---

**Q: 你的反馈回路（Kafka -> 模型 -> 排名 -> 曝光 -> Kafka）是一个封闭系统。你如何防止系统收敛到局部最优而永远发现不了更好的模块组合？**

> **承认局限：** 这是经典的纯利用陷阱 (exploitation-only trap)。没有主动
> 探索，系统会收敛到历史最优组合而永不测试替代方案。
>
> **缓解措施：** 三个机制打破闭环：
>
> 1. **Thompson Sampling** 配合滑动窗口衰减确保持续探索。即使成熟模块也有
>    非零后验方差，因此采样分数偶尔会超过高排名模块的利用分数。
> 2. **定期随机探索预算 (Periodic random exploration budget)**：2% 的流量
>    保留给均匀随机的模块排序（在硬 UX 约束内）。这为反事实评估提供无偏数据。
> 3. **反事实离线评估 (Counterfactual offline evaluation)**（IPS/DR 估计器）
>    让我们在探索预算数据上评估候选策略，无需实际部署。这实现了快速离线
>    迭代：每周离线测试约 20 个模型变体，只 A/B 测试前 2-3 个。
>
> **数据：** 2% 探索预算的代价约为 0.15% 页面 GMV，但提供了可靠离线评估所需
> 的无偏数据。没有它，IPS 估计的方差高 3 倍，使离线模型选择不可靠。

---

**Q: 为什么不直接让产品团队手动设置模块优先级，而要构建这个市场？**

> **承认局限：** 手动优先级设置更简单，对少量模块类型（3-4 个）有效。
>
> **缓解措施：** eBay SRP 有约 200 种跨团队的注册模块类型，最优分配因查询
> 类型、用户群体和时间段而异。手动规则无法捕捉这种维度。市场方案还提供透明
> 的"价格发现"机制——每个团队可以看到自己模块价值与替代方案的对比，对齐激励。
>
> **数据：** 市场上线后，活跃模块类型在 6 个月内从 12 种增长到 45 种，因为
> 团队可以在不协商固定页面槽位的情况下上线新模块。页面级 GMV 提升约 4%。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 口述大纲 (Verbal Outline)

### 3 分钟版本

1. **(30 秒) 背景：** eBay SRP 采用固定模块布局，没有数据驱动的分配。新模块
   需要手动协商页面槽位，且无法评估哪个模块每次曝光创造最大价值。

2. **(45 秒) 核心洞察：** 将 SRP 视为内容市场——模块基于预测互动价值出价竞争
   页面空间，集中式仲裁系统分配位置以最大化总页面价值。

3. **(60 秒) 架构：** 两阶段系统。离线层使用 XGBoost 基于 6 个月互动数据
   预计算模块价值，配合 Thompson Sampling 进行探索。在线层每个查询执行两阶段：
   (1) 选择符合条件的模块并行获取内容，(2) 求解带约束 LP 分配页面位置并组合
   最终布局。

4. **(30 秒) 核心算法：** 带滑动窗口后验的 Thompson Sampling 用于探索，加上
   LP 松弛配确定性取整用于整页优化——30 模块和 48 位置在 <10ms 内求解。

5. **(15 秒) 结果：** 页面级 GMV 提升约 4%。模块生态在 6 个月内从 12 种增长
   到 45 种活跃类型，无需手动槽位协商。

### 10 分钟版本

1. **(1 分钟) 背景 + 动机：** 固定布局的问题——无价值信号、忽略上下文的分配、
   新模块的扩展瓶颈。误配的业务影响：黄金位置浪费在低互动模块上，高价值
   模块被推到屏幕下方。

2. **(2 分钟) 架构讲解：**
   - 离线层：Module Registration（元数据、位置约束），Value Prediction
     （XGBoost/LightGBM 配上下文特征），Thompson Sampling（每模块 Beta
     后验，滑动窗口变体）
   - 在线层：Stage 1——候选选择（从约 200 中选 15-30 个），并行内容获取
     （50ms 超时）。Stage 2——位置优化、质量过滤、基于 LP 的价值最大化、
     页面组合。

3. **(2 分钟) 核心算法：**
   - 期望价值公式: $E[V_m] = P(\text{click} \mid m,q,u) \cdot \text{Revenue}(m) + \alpha \cdot P(\text{engagement} \mid m)$
   - Thompson Sampling: $\theta_m \sim \text{Beta}(\alpha_m + s_m, \beta_m + f_m)$，$\gamma=0.95$ 每日衰减
   - LP 建模: 最大化 $\sum x_{m,p} \cdot V(m,p)$ 受分配、多样性和相邻性约束
   - LP 松弛 + 贪心取整: $O(n \cdot m)$ 求解，98.7% 查询上与精确 ILP 差距在 2.5% 内

4. **(2 分钟) 生产约束：**
   - 50K QPS，<10ms 仲裁预算，<150ms 端到端 P99
   - LP 松弛使 NP-hard 的 ILP 可处理；网络流求解器 + 贪心取整
   - 提供方超时处理：监控、缓存（1 小时 TTL）、优雅退化
   - 数据规模：5 亿曝光/天，2000 万点击/天，6 个月特征存储

5. **(2 分钟) 权衡：**
   - Thompson Sampling vs. UCB：TS 在非平稳设置下经验胜出（Q4 高季节性
     期间 CTR 高 12%）
   - 贪心 vs. LP：LP 以 2 倍延迟代价捕捉跨模块交互（广告疲劳、多样性），
     但保持在预算内
   - 冷启动：基于模块类型先验的上下文 bandits vs. 随机探索

6. **(1 分钟) 结果 + 教训：**
   - GMV +4%，模块生态从 12 种增长到 45 种，透明的价值发现
   - 如果重新来过会怎样做：更早引入反事实评估，测量每个模块的真实增量价值
     （而非存在选择偏差的观测互动）
"""


def populate_module_arbitration() -> None:
    """Update the module-arbitration record with all 8 markdown sections."""
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
            print("Run scripts/seed_system_designs.py first to create the record.")
            sys.exit(1)

        record.overview = OVERVIEW
        record.architecture = ARCHITECTURE
        record.dataflow = DATAFLOW
        record.formulas = FORMULAS
        record.production_constraints = PRODUCTION_CONSTRAINTS
        record.tradeoffs = TRADEOFFS
        record.defense = DEFENSE
        record.verbal_outline = VERBAL_OUTLINE

        db.commit()
        print(f"[DONE] Updated all 8 sections for '{SLUG}'.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            ("overview", record.overview),
            ("architecture", record.architecture),
            ("dataflow", record.dataflow),
            ("formulas", record.formulas),
            ("production_constraints", record.production_constraints),
            ("tradeoffs", record.tradeoffs),
            ("defense", record.defense),
            ("verbal_outline", record.verbal_outline),
        ]
        for name, content in sections:
            length = len(content) if content else 0
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_module_arbitration()
