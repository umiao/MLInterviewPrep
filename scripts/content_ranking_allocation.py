"""Populate Ranking-as-Allocation system design module with all 8 sections.

Usage:
    python scripts/content_ranking_allocation.py

This is the SIGNATURE PROJECT -- deepest coverage, most personal ownership voice.
Idempotent: overwrites existing content for the ranking-allocation slug.
Chinese is the source of truth.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

# ---------------------------------------------------------------------------
# Section 1: Overview & Motivation
# ---------------------------------------------------------------------------

OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

### 逐点排序的问题 (The Pointwise Ranking Problem)

传统的搜索排序对每个商品独立地针对查询进行评分，然后按分数排序。这种**逐点范式（pointwise paradigm）**忽略了一个关键现实：用户看到的是一*页*结果，而非单个商品。当每个商品被孤立评分时，结果页变得**同质化**——被相同的卖家、相同的类目、相同的价格区间主导。

### 同质化为何有害

| 利益相关方 | 同质化结果的影响 |
|-------------|------------------------------|
| **买家** | 探索空间缩小；冗余列表导致疲劳；更高的跳出率 |
| **长尾卖家** | 被主导相关性分数的头部卖家挤出 |
| **平台** | 会话继续率下降；购买多样性降低；市场健康风险 |

### 分配洞察 (The Allocation Insight)

搜索结果页有 $K$ 个槽位（eBay SRP 通常为 48 个）。排序本质上是一个**分配问题（allocation problem）**：将 $K$ 个稀缺槽位分配给竞争性目标——相关性、多样性、公平性和收入。

$$
\text{Ranking} \equiv \text{Allocating } K \text{ slots subject to constraints}
$$

这种重新定义解锁了运筹学的丰富工具集：约束优化、预算管理和闭环策略控制。

### 本项目的独特之处

1. **分配框架**应用于搜索排序（而非仅限于广告竞价）
2. **软约束 + 硬约束混合**实现灵活的多样性管理
3. **闭环策略管理**根据观测值与目标多样性指标每日自动调整多样性预算
4. **MUS (Model-Unified Scoring) 校准**支持多模型分数组合
5. **层次化分段预算**优雅处理稀疏数据

### 影响

- **+3.5%** 页面级购买率
- **+2.8%** 会话继续率
- 分配范式已在 eBay 的 3 个搜索垂直领域推广
"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## 架构深入剖析 (Architecture Deep Dive)

### 系统架构概览

系统有两个主要循环：处理实时查询流量的**在线服务管线**，以及根据观测结果调整多样性策略的**近线/离线闭环**。

### 在线服务管线

```
Query -> QN (Candidate Generation) -> Cassini ORC (Late-Stage Ranking) -> Page Composer -> SRP
```

#### Query Node (QN) -- 候选生成

QN 通过倒排索引查找加轻量级相关性过滤，为每个查询检索 50-200 个候选商品。关键的是，每个候选商品都被标记了**多样性队列标签（diversity cohort labels）**：

- **卖家队列（seller cohort）**：卖家层级（超级卖家、中等、长尾）
- **类目队列（category cohort）**：叶子类目 + 父类目
- **价格分桶（price bucket）**：离散化价格区间（低价 / 中档 / 高端）
- **状况队列（condition cohort）**：全新、翻新、二手

这些队列标签是预计算的，存储在商品索引中。

#### Cassini ORC -- 后期排序

**ORC (Orchestration/Ranking/Composition)** 层执行四个顺序步骤：

| 步骤 | 延迟 | 描述 |
|------|---------|-------------|
| **基础相关性评分** | ~5ms | 多模型集成（相关性、新鲜度、个性化） |
| **MUS 校准** | <1ms | 将跨模型分数归一化到统一尺度 |
| **策略分配重排** | <3ms | 带软约束 + 硬约束的贪心重排 |
| **硬性覆写** | <0.5ms | 法规、品牌安全和强制性多样性下限/上限 |

#### MUS 校准层 (MUS Calibration Layer)

多个排序模型在不同尺度上输出分数。**MUS (Model-Unified Scoring)** 将它们归一化到统一分布：

$$\hat{s}_i = \frac{s_i - \mu_m}{\sigma_m} \cdot \sigma_{\text{target}} + \mu_{\text{target}}$$

其中 $\mu_m, \sigma_m$ 是每个模型的统计量，每小时从近期流量样本中刷新。

#### 策略分配重排 (Policy Allocation Re-ranking)

核心重排器使用**带约束惩罚的贪心算法**：

1. 初始化：空结果集 $R$，完整候选集 $C$
2. 对位置 $k = 1, \ldots, K$：
   - 对每个候选 $i \in C$：计算调整后分数
     $s'_i = s_i - \lambda \cdot \text{violation\_penalty}(i, R)$
   - 选择 $i^* = \arg\max_{i \in C} s'_i$
   - 将 $i^*$ 加入 $R$，从 $C$ 中移除
   - 更新约束满足状态

**违约惩罚（violation penalty）**对会加剧约束违反的候选项递增（例如，当上限为 3 时添加同一卖家的第 4 件商品）。

#### 硬性覆写 (Hard Overrides)

作为后处理过滤器应用的不可协商约束：

- **法规**：特定地区的商品限制
- **品牌安全**：被拉黑的卖家或类目
- **强制下限**：特定多样性维度的最低表示要求

### 近线/离线闭环

```
User Interactions -> Profile Discovery -> DSBE Paradise Table
    -> Adjustment Engine -> Spark Job -> Updated Policy -> Serving Layer
```

#### Cassini Profile Discovery

分析用户交互以构建三种画像：

- **查询画像（query profiles）**：每种查询类型呈现什么多样性模式
- **落地画像（landing profiles）**：哪些多样性配置带来交互
- **口味画像（taste profiles）**：每用户的多样性偏好

#### DSBE Paradise Table

**DSBE (Diversity Segment Budget Engine)** 维护一张约 2000 个查询分段的观测值与目标多样性对比表：

| 分段 | 维度 | 目标 | 观测值 | 差距 |
|---------|-----------|--------|----------|-----|
| "shoes" x tier-1 | 卖家多样性 | 0.65 | 0.58 | -0.07 |
| "shoes" x tier-1 | 类目多样性 | 0.40 | 0.42 | +0.02 |
| "electronics" x tier-2 | 卖家多样性 | 0.70 | 0.71 | +0.01 |

#### 调整引擎 (Adjustment Engine)

比较观测值与目标多样性并调整预算：

$$b_j^{(t+1)} = b_j^{(t)} + \eta \cdot (b_j^{\text{target}} - \bar{d}_j^{(t)})$$

配合三道护栏：
1. **预算截断（budget clamping）**：$b_j \in [b_j^{\min}, b_j^{\max}]$
2. **保守学习率**：$\eta = 0.1$
3. **相关性护栏**：如果 NDCG 较基线下降 >2%，冻结预算

#### Spark 作业

每晚批处理作业（约 2 小时）：
1. 处理前一天的交互数据
2. 计算每个分段的更新多样性预算
3. 将新的策略参数分发至服务层
"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 在线路径（每查询，总计 <15ms）

```
1. Query arrives at Query Node (QN)
   |
   v
2. QN: Candidate generation (inverted index + lightweight relevance)
   - Retrieves 50-200 candidates
   - Tags each with diversity cohort labels (seller, category, price, condition)
   |
   v
3. Cassini ORC: Base Relevance Scoring
   - 3-model ensemble: base relevance, freshness, personalization
   - Each model produces raw score on its own scale
   |
   v
4. Cassini ORC: MUS Calibration
   - Normalize each model's scores: z-score transform to target distribution
   - Combine calibrated scores into unified relevance score
   |
   v
5. Cassini ORC: Policy Allocation Re-ranking
   - Load diversity budgets for this query's segment from policy cache
   - Greedy selection with constraint penalty:
     * Soft constraints: seller variety, category diversity, price spread
     * Hard constraints: regulatory, brand safety, mandatory floors
   - Output: ordered list of K=48 items satisfying constraints
   |
   v
6. Cassini ORC: Hard Overrides
   - Final pass: enforce non-negotiable constraints
   - Swap out any items violating regulatory or safety rules
   |
   v
7. Page Composer
   - Assemble final SRP layout
   - Inject non-organic modules (ads, promotions) into reserved slots
   - Render to user
```

### 离线反馈循环（每日批量）

```
1. User Interactions (clicks, purchases, session continuation)
   |
   v
2. Profile Discovery (Cassini pipeline)
   - Query profiles: diversity patterns per query type
   - Landing profiles: which configurations drive engagement
   - Taste profiles: per-user diversity preferences
   |
   v
3. DSBE Paradise Table
   - Aggregate observed diversity metrics per segment
   - Compare against target diversity budgets
   - Compute gap: observed - target per dimension per segment
   |
   v
4. Adjustment Engine
   - For each segment-dimension pair:
     * If gap < 0 (under-diverse): increase budget
     * If gap > 0 AND relevance stable: maintain budget
     * If relevance dropping (NDCG drop >2%): freeze budget, alert team
   - Apply hierarchical shrinkage for sparse segments
   |
   v
5. Spark Job (overnight, ~2 hours)
   - Materialize updated budgets
   - Distribute to serving layer policy cache
   - Next day's queries use updated constraints
```

### Kafka 反馈管线 (Kafka Feedback Pipeline)

用户交互通过 **Kafka** 消息系统流向离线闭环。具体数据流：

```
SRP Page -> Client SDK (click/purchase/dwell events)
   -> Kafka Topic: user-interactions (partitioned by query_id)
      -> Consumer Group 1: Profile Discovery (nearline, ~5min lag)
      -> Consumer Group 2: Diversity Metrics Aggregator (batch, hourly rollup)
      -> Consumer Group 3: NDCG Monitor (nearline, real-time guardrail)
```

#### Kafka Topic 设计

| Topic | 分区策略 | 保留期 | 消费者 |
|-------|----------|--------|--------|
| `user-interactions` | 按 `query_id` 哈希 | 7 天 | Profile Discovery, Metrics Aggregator |
| `diversity-metrics` | 按 `segment_id` 哈希 | 30 天 | Adjustment Engine, 监控仪表盘 |
| `policy-updates` | 按 `segment_id` 哈希 | 3 天 | 在线服务层 Policy Cache |

#### 交互事件 Schema

每条 Kafka 消息包含：
- `query_id`：查询标识（用于关联展示与点击）
- `item_id`：商品 ID
- `position`：展示位置（1-48）
- `event_type`：`impression` / `click` / `purchase` / `session_continue`
- `segment_id`：查询所属分段
- `diversity_cohorts`：该商品的多样性队列标签
- `timestamp`：事件时间戳

#### 端到端延迟

| 阶段 | 延迟 | 说明 |
|------|------|------|
| 客户端 -> Kafka | <1s | Client SDK 批量发送（每 500ms 或 10 事件） |
| Kafka -> Profile Discovery | ~5 min | 近线消费者，微批处理 |
| Kafka -> Metrics Aggregator | ~1 hour | 每小时滚动聚合 |
| Metrics -> DSBE Paradise Table | ~2 hours | 每晚 Spark 作业 |
| DSBE -> Policy Cache | <30 min | 策略分发至服务层 |

### 关键数据存储

| 存储 | 类型 | 内容 | 更新频率 |
|-------|------|----------|-----------------|
| **Item Index** | 倒排索引（Cassini） | 商品特征 + 多样性队列标签 | 实时（listing 更新） |
| **Policy Cache** | 内存键值存储 | 每分段-维度的多样性预算 | 每日（Spark 作业后） |
| **DSBE Paradise Table** | Hive/HDFS 表 | 每分段的观测 vs. 目标多样性 | 每日聚合 |
| **Model Statistics** | Redis | 每模型 $\mu_m, \sigma_m$（用于 MUS 校准） | 每小时从流量样本刷新 |
| **Profile Store** | 键值存储（Cassini） | 查询/落地/口味画像 | 近线更新（分钟级） |

### 约束类型

| 类型 | 示例 | 执行方式 | 灵活度 |
|------|----------|-------------|-------------|
| **硬约束** | 法规限制、品牌安全、强制多样性下限 | 后处理过滤器（商品被替换） | 零容忍——必须满足 |
| **软约束** | 卖家多样性、类目分布、价格区间多样性 | 重排期间的贪心惩罚 | 基于预算——如相关性代价过高，允许欠满足 |
"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 核心分配目标 (Core Allocation Objective)

排序问题被形式化为约束分配：

$$
\max_{x} \sum_{i=1}^{N} x_i \cdot s_i \quad \text{s.t.} \quad \sum_{i \in G_j} x_i \geq b_j \;\forall j, \quad \sum_i x_i = K
$$

其中：
- $x_i \in \{0, 1\}$：商品 $i$ 的选择指示变量
- $s_i$：校准后的相关性分数
- $G_j$：多样性维度 $j$ 的商品分组（如所有长尾卖家的商品）
- $b_j$：分组 $j$ 的最低预算（下限）
- $K = 48$：页面大小（槽位数量）

这是一个**整数线性规划（ILP）**——一般情况下是 NP-hard 的，但贪心近似效果良好，因为约束结构简单（基数约束 + 分组下限约束）。

### MUS 校准 (MUS Calibration)

**MUS (Model-Unified Scoring)** 将不同排序模型的分数归一化到统一的目标分布：

$$
\hat{s}_i = \frac{s_i - \mu_m}{\sigma_m} \cdot \sigma_{\text{target}} + \mu_{\text{target}}
$$

其中：
- $s_i$：模型 $m$ 的原始分数
- $\mu_m, \sigma_m$：模型 $m$ 分数的均值和标准差（从近期流量估计，每小时刷新）
- $\mu_{\text{target}} = 0, \sigma_{\text{target}} = 1$：目标分布参数（标准正态）

**为什么不直接用 z-score？** 目标参数允许控制组合分数的动态范围。实际中，$\sigma_{\text{target}}$ 按模型调优，以反映其离线 NDCG 贡献权重。

### 带约束惩罚的贪心重排 (Greedy Re-ranking with Constraint Penalty)

对每个位置 $k = 1, \ldots, K$：

$$
s'_i = s_i - \lambda \cdot \text{violation\_penalty}(i, R_k)
$$

其中：
- $R_k$：已放置在位置 $1, \ldots, k-1$ 的商品
- $\lambda$：惩罚权重（通过离线评估调优）

**违约惩罚函数**：

$$
\text{violation\_penalty}(i, R) = \sum_{j=1}^{J} w_j \cdot \max\left(0, \; c_j(R \cup \{i\}) - b_j^{\max}\right)
$$

其中 $c_j(R \cup \{i\})$ 是如果将商品 $i$ 添加到结果集中，分组 $j$ 中的商品计数，$b_j^{\max}$ 是上限约束。

**复杂度**：$O(K \cdot N)$，对于 $K=48$ 个槽位和 $N=200$ 个候选，约 9,600 次评分操作——轻松控制在 3ms 以内。

### 闭环预算调整 (Closed-Loop Budget Adjustment)

每日更新规则：

$$
b_j^{(t+1)} = \text{clamp}\left(b_j^{(t)} + \eta \cdot (b_j^{\text{target}} - \bar{d}_j^{(t)}), \; b_j^{\min}, \; b_j^{\max}\right)
$$

其中：
- $b_j^{(t)}$：维度 $j$ 的当前预算
- $b_j^{\text{target}}$：期望的多样性水平（由业务规则设定）
- $\bar{d}_j^{(t)}$：观测到的多样性指标（日均）
- $\eta = 0.1$：学习率（保守以防振荡）
- $b_j^{\min}, b_j^{\max}$：人工设定的护栏边界

**收敛性**：在 $\eta = 0.1$ 和截断边界下，新的预算目标在 3-7 天内稳定。当 $\bar{d}_j^{(t)}$ 对 $b_j^{(t)}$ 呈线性响应时（在操作范围内近似成立），系统单调收敛。

### 基于 Thompson Sampling 的预算探索

对于最优预算不确定的分段，进行探索：

$$
b_j^{\text{explore}} \sim \mathcal{N}(b_j^{(t)}, \sigma_j^2)
$$

其中 $\sigma_j^2$ 对新分段初始值较大，随着观测积累而缩小。这在探索潜在更优预算与利用已知良好设置之间取得平衡。

### 稀疏分段的层次化收缩 (Hierarchical Shrinkage for Sparse Segments)

对于每日查询量少的分段，预算估计噪声较大。我们应用**经验贝叶斯收缩（empirical Bayes shrinkage）**：

$$
\hat{b}_j^{\text{segment}} = \alpha_j \cdot b_j^{\text{segment}} + (1 - \alpha_j) \cdot b_j^{\text{parent}}
$$

其中：
- $\alpha_j = \frac{n_j}{n_j + n_0}$：收缩权重
- $n_j$：该分段的观测计数
- $n_0$：先验强度（调优到约 100 个日查询）
- $b_j^{\text{parent}}$：父分段的预算（如意图类目层级）

| 观测计数 | 收缩系数 $\alpha$ | 预算来源 |
|-------------------|-------------------|---------------|
| >500 日查询 | ~0.83 | 主要使用分段专有 |
| 100-500 查询 | 0.50-0.83 | 部分收缩 |
| <100 查询 | <0.50 | 主要继承自父分段 |

### 冷启动预算初始化 (Cold-Start Budget Initialization)

新分段（如新类目上线、新地区开放）没有历史交互数据，无法直接估计多样性预算。冷启动策略：

$$
b_j^{\text{cold}} = b_j^{\text{parent}} + \beta \cdot (b_j^{\text{global\_avg}} - b_j^{\text{parent}})
$$

其中：
- $b_j^{\text{parent}}$：父分段预算（层次化继承）
- $b_j^{\text{global\_avg}}$：全局维度 $j$ 的平均预算
- $\beta = 0.3$：全局先验混合权重（偏向父分段，但引入全局信息避免极端初始化）

**冷启动三阶段演进**：

| 阶段 | 条件 | 预算来源 | 探索强度 |
|------|------|----------|----------|
| **Phase 0: 纯继承** | 日查询 <10 | 100% 父分段预算 | 无探索（流量太少） |
| **Phase 1: 探索期** | 日查询 10-100 | 冷启动公式 + Thompson Sampling ($\sigma_j$ 较大) | 高探索（$\sigma_j = 0.15$） |
| **Phase 2: 收敛期** | 日查询 >100 | 层次化收缩（标准公式） | 标准探索（$\sigma_j$ 按观测缩小） |

**关键设计决策**：Phase 0 不做探索，因为日查询量 <10 时，任何预算调整的效果都无法可靠测量。强行探索只会引入噪声，不产生可操作的信号。
"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

### 吞吐量与延迟

| 指标 | 数值 | 背景 |
|--------|-------|---------|
| **QPS** | 峰值约 50K 查询/秒 | 与 Module Arbitration 共享 Cassini 服务路径的相同流量 |
| **每查询候选集** | QN 检索后 50-200 个商品 | 多样性重排在这个检索后集合上操作 |
| **页面大小** | $K = 48$ 个槽位 | 标准 eBay SRP 页面；分配恰好填满 $K$ 个槽位 |
| **重排延迟** | <3ms（带约束惩罚的贪心） | $O(K \cdot N)$，$K=48, N=200$ = 约 9,600 次操作 |
| **MUS 校准延迟** | <1ms（每查询的简单归一化） | 预计算 $\mu_m, \sigma_m$（每模型），每小时刷新 |
| **ORC 总延迟预算** | 端到端 <15ms | 包括基础评分（~5ms）、MUS（<1ms）、重排（<3ms）、覆写（<0.5ms）、开销 |

### 约束维度

| 维度 | 硬约束 | 软约束 |
|-----------|-----------------|-----------------|
| **卖家** | 每个卖家最多 3 件商品（反垃圾） | 卖家层级多样性目标（长尾卖家表示占比） |
| **类目** | 强制类目广度下限 | 每分段的类目多样性预算 |
| **价格** | 无 | 价格分桶分布目标 |
| **状况** | 特定地区（翻新品披露法规） | 状况组合多样性 |
| **品牌安全** | 拉黑卖家/类目移除 | 无（仅硬约束） |
| **法规** | 特定地区商品限制 | 无（仅硬约束） |

### 规模参数

| 参数 | 数值 | 备注 |
|-----------|-------|-------|
| **硬约束类型** | 8 个活跃类别 | 卖家上限、类目下限、状况多样性、品牌安全、法规等 |
| **软约束维度** | 4 个（卖家、类目、价格分桶、状况） | 每个维度在每个查询分段上有独立预算 |
| **查询分段** | 约 2,000 个分段（查询意图 x 用户层级） | 预算目标维护在 **DSBE (Diversity Segment Budget Engine)** Paradise Table 中 |
| **策略更新频率** | 每日批量（每晚 Spark 作业） | 约 2 小时处理前一天的数据并计算新预算 |
| **闭环收敛** | 新预算目标 3-7 天稳定 | 学习率 $\eta = 0.1$，截断到 $[b^{\min}, b^{\max}]$ 范围 |
| **模型统计刷新** | 每小时 | 每模型 $\mu_m, \sigma_m$（用于 MUS 校准） |

### 监控与告警

| 监控项 | 阈值 | 操作 |
|---------|-----------|--------|
| **分段多样性下降** | 低于目标 >10% 持续 2 小时以上 | 实时 Grafana 告警至值班人员 |
| **NDCG 护栏** | 较分段基线下降 >2% | 调整引擎冻结该分段预算 |
| **重排延迟 P99** | >5ms | 自动告警；回退到纯相关性排序 |
| **约束违反率** | >1% 的查询存在硬约束违反 | 即时页面告警；排查约束配置 |

### 故障模式与回退

| 故障 | 回退方案 | 恢复 |
|---------|----------|----------|
| Policy cache 不可用 | 使用默认多样性预算（保守，预配置） | 下一次 Spark 作业自动重建缓存 |
| MUS 统计过期（>4 小时） | 使用原始模型分数，不做校准 | 每小时刷新作业以指数退避重试 |
| 重排超时（>5ms） | 返回纯相关性排序结果，不做多样性重排 | 记录事件以排查延迟问题 |
| 调整引擎产生异常预算 | 截断到 $[b^{\min}, b^{\max}]$ 捕获极端值 | 超出范围告警触发人工审查 |

### 超参数调优表 (Hyperparameter Tuning Table)

| 超参数 | 搜索范围 | 最优值 | 调优方法 | 敏感度 |
|--------|----------|--------|----------|--------|
| $\lambda$（违约惩罚权重） | $[0.01, 1.0]$ | 0.15 | 离线 NDCG-diversity Pareto 扫描 | 高：<0.05 时多样性不足，>0.5 时相关性损失 >3% |
| $\eta$（预算学习率） | $[0.01, 0.5]$ | 0.1 | 离线模拟 + A/B 验证 | 中：0.05-0.2 范围内表现稳定 |
| $n_0$（收缩先验强度） | $[50, 500]$ | 100 | 交叉验证（留出分段） | 低：50-200 差异 <1% 购买率 |
| $\beta$（冷启动全局混合） | $[0.1, 0.5]$ | 0.3 | A/B 测试（新分段子集） | 低：影响仅限冷启动期 |
| $\sigma_j$（TS 探索初始方差） | $[0.05, 0.25]$ | 0.10 | 离线 regret 模拟 | 中：过大导致预算振荡 |
| $\gamma$（Spark 作业异常检测阈值） | $[2.0\sigma, 4.0\sigma]$ | $3.0\sigma$ | 历史数据回测 | 中：<2$\sigma$ 误报多，>4$\sigma$ 漏报 |
| 卖家上限（每页每卖家） | $[2, 5]$ | 3 | A/B 测试 + 买家调查 | 高：2 时头部卖家收入下降显著，5 时同质化回归 |
"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|----------|----------|----------|------------------|
| **排序范式** | 逐点（独立评分每个商品） | 分配（页面级约束优化） | **分配** -- 逐点忽略了组合效应；两个相同商品同时展示浪费槽位。分配框架直接建模我们关心的问题：页面级用户体验。 |
| **多样性执行** | 仅硬约束 | 软约束 + 硬约束混合 | **混合** -- 硬约束用于不可协商的要求（法规、品牌安全）；软约束用于偏好性多样性（卖家多样性）。纯硬约束过于死板；纯软约束则有关键违规风险。 |
| **约束范围** | 每查询预算 | 每查询分段预算（聚类） | **每分段** -- 单个查询的噪声太大，无法稳定估计预算。分段（约 2,000 个）聚合相似查询，在保持有意义粒度的同时实现可靠的多样性目标。 |
| **策略更新频率** | 每日批量 | 近实时流式 | **每日批量** -- 多样性策略变更需要谨慎评估副作用。实时更新有振荡风险且难以调试。每日节奏提供了稳定性，延迟可接受。 |
| **分数归一化** | 原始模型分数 | **MUS (Model-Unified Scoring)** 校准（z-score 转换到目标分布） | **MUS 校准** -- 多个模型在不可比的尺度上输出分数。原始分数组合无意义。MUS 支持原则性的集成，无需逐模型权重调优。 |

### 深入权衡讨论

#### 分配 vs. 逐点：组合问题

逐点排序优化 $\sum_{i=1}^{K} s_i$ —— 个体相关性分数之和。这等价于无约束的分配。问题在于：一页 48 个高度相关但完全相同的商品（同一卖家、同一类目、同一价格）最大化了逐点 NDCG，但提供了糟糕的用户体验。

分配框架添加约束，牺牲了部分逐点 NDCG（实测：-1.2%），但改善了与用户满意度实际相关的页面级指标（+3.5% 购买率，+2.8% 会话继续率）。

**关键洞察**：NDCG 是测量工具，不是目标。当测量指标偏离用户满意度时，应修正测量方式，而非系统。

#### 每日批量 vs. 实时策略更新

我们考虑过流式策略更新（根据上一个查询的结果，在每个查询后更新预算）。问题包括：

1. **振荡**：预算变更即时传播，但其效果需要数千个查询才能可靠测量。快速更新 + 缓慢反馈 = 振荡。
2. **调试**：当多样性指标下降时，每日批量有清晰的归因（昨天的策略变更）。实时模式则是一连串无法归因的微变更。
3. **爆炸半径**：每日批量的 bug 影响一天。实时 bug 会持续累积。

每日节奏意味着我们接受策略适应的 24 小时延迟。这是可接受的，因为多样性目标变化缓慢（由目录组成和季节性趋势驱动，而非逐分钟变化）。

#### 贪心 vs. 精确 ILP 求解器

分配目标是整数线性规划。我们可以精确求解（如使用 CPLEX 或 Gurobi）。我们选择贪心是因为：

| 因素 | 精确 ILP | 贪心 |
|--------|-----------|--------|
| **延迟** | 10-50ms（求解器开销） | <3ms |
| **最优性** | 可证明最优 | 95-98% 最优（经验测量） |
| **可解释性** | 黑盒求解器输出 | 逐步放置逻辑；易于调试 |
| **约束变更** | 需要重新建模 | 添加惩罚项 |

2-5% 的最优性差距是可接受的，因为延迟改善了 3-10 倍。对于服务 50K QPS 的在线系统，延迟更为关键。

### 典型失败模式与修复 (Typical Failure Modes & Fixes)

1. **预算振荡（Budget Oscillation）**：调整引擎对季节性变化反应过激，导致卖家多样性预算在连续几天间大幅摆动。**根因**：$\eta$ 设置过高（早期实验用 $\eta=0.3$），且未对季节性信号做平滑。**修复**：将 $\eta$ 降至 0.1，并在 Adjustment Engine 输入端添加 7 天 **EMA (Exponential Moving Average)** 平滑器。效果：预算日波动从 +/-15% 降至 +/-3%。

2. **约束冲突死锁（Constraint Conflict Deadlock）**：节日期间同时激活多个硬约束（促销 banner 强制展示 + 法规限制 + 卖家上限），导致贪心算法在前 20 个位置就耗尽合规候选。后续位置被迫填充低相关性商品，NDCG 暴跌。**根因**：硬约束之间无优先级排序。**修复**：实现**约束优先级堆栈（constraint priority stack）**——法规 > 品牌安全 > 促销强制 > 多样性下限。当多个硬约束冲突时，按优先级逐层放松低优先级约束，同时记录放松事件供离线审查。

3. **冷启动分段的预算漂移（Cold-Start Segment Budget Drift）**：新分段从父分段继承预算后，在 Phase 1 探索期内 Thompson Sampling 的高方差导致预算快速偏离合理范围，尤其在流量极低时。**根因**：$\sigma_j$ 初始值对低流量分段过大。**修复**：为 Phase 1 分段增加额外的 **micro-clamping**：$b_j \in [b_j^{\text{parent}} - 0.1, b_j^{\text{parent}} + 0.1]$。只允许在父预算附近小范围探索，直到流量达到 Phase 2 阈值后才放宽到标准范围。
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## 对抗性答辩问答 (Adversarial Defense Q&A)

**Q: 你们的分配框架听起来为边际收益增加了复杂度。你能量化多样性约束的相关性代价吗？**

> **承认局限**：多样性约束确实降低了纯相关性 NDCG。对最大化问题施加任何约束都会降低最优值——这是基本的数学事实，不是设计缺陷。
>
> **应对措施**：关键洞察是用户满意度与逐点相关性并非单调递增。一页 48 件来自同一卖家、都高度相关的商品是糟糕的体验。我们测量页面级交互（会话继续率、购买率），而非仅 NDCG。
>
> **数据**：启用多样性约束后，逐点 NDCG 下降 1.2%，但页面级购买率提升 3.5%，会话继续率提升 2.8%。用户更可能购买，也更可能回来。由 NDCG 衡量的多样性"代价"是测量失真——NDCG 奖励展示"最相关"的商品，但用户想要的是多样性，而非冗余。

---

**Q: 你们的闭环自动调整预算。如何防止它博弈指标或漂移到退化状态？**

> **承认局限**：闭环系统可能漂移、振荡或找到奖励黑客均衡。这是真实风险，不是理论风险——我在其他排序系统中见过奖励博弈。
>
> **应对措施**：三道护栏防止退化行为：
>
> 1. **预算截断**：每个预算都截断在 $[b^{\min}, b^{\max}]$ 范围内，由人工审查的业务规则设定。系统无法将卖家多样性设为 0% 或 100%。
> 2. **保守学习率**：$\eta = 0.1$ 意味着每日最大预算变化约为观测值与目标差距的 10%。大幅跳跃是不可能的。
> 3. **相关性护栏**：如果任何分段的 NDCG 较基线下降 >2%，调整引擎冻结该分段预算并通知团队。
>
> **数据**：在 14 个月的运行中，调整引擎冻结预算 7 次（占分段-天数的 0.5%）。5 次是季节性变化导致的误报（如节假日流量改变查询分布）；2 次是真正的约束配置错误，在影响用户之前被及时捕获。生产环境中未出现退化状态。

---

**Q: MUS (Model-Unified Scoring) 校准归一化了分数，但不同模型可能有根本不同的质量水平。归一化不是掩盖了质量差异吗？**

> **承认局限**：是的，归一化统一了尺度但不是不同模型的信息含量。一个训练不佳的模型校准后仍然贡献噪声。
>
> **应对措施**：MUS 校准在同一相关性层级内归一化，而非全局归一化。高质量模型的分数分布更紧凑、信息量更大——归一化后这一属性得以保留。校准后的分数与相关性标注之间仍具有更高的互信息。此外，我们按模型的离线 NDCG 贡献权重在最终分数组合中对模型加权，因此低质量模型被降权。
>
> **数据**：MUS 校准后，3 个排序模型（基础相关性、新鲜度、个性化）的集成比使用最佳单模型的原始分数高出 2.1% 的 NDCG。校准使有意义的分数组合成为可能，而使用不同尺度的原始分数是无法做到这一点的。

---

**Q: 2,000 个分段的每分段预算——你们如何处理数据稀疏的分段？**

> **承认局限**：长尾分段（稀有查询类型 + 小众用户层级）每天的观测很少，使得预算调整噪声很大。朴素的每分段估计会产生不可靠的预算。
>
> **应对措施**：**层次化收缩（hierarchical shrinkage，经验贝叶斯）**：每日查询量 <100 的分段继承其父分段的预算。收缩权重 $\alpha = n / (n + n_0)$ 随着观测计数增长，平滑地在分段专有估计和父分段估计之间插值。
>
> 这与 **James-Stein 估计**原理相同：跨相关组汇总信息可改善所有组的估计，尤其是稀疏组。
>
> **数据**：65% 的分段有 >500 个日查询（可靠的独立预算）。30% 有 100-500 个（部分收缩）。5% 有 <100 个（完全继承自父分段）。层次化方法将稀疏分段的预算方差降低了 60%，相比纯每分段估计。

---

**Q: 贪心算法是次优的——你们在损失相关性。为什么不用精确求解器？**

> **承认局限**：贪心是启发式方法。对于整数线性规划，它不保证最优解。
>
> **应对措施**：我们通过在抽样查询上离线运行精确 **ILP (Integer Linear Program)** 求解器（Gurobi）来经验性地测量最优性差距。贪心解达到最优相关性分数的 95-98%，而运行时间 <3ms，相比精确求解器的 10-50ms。
>
> 在 50K QPS 下，延迟差异比 2-5% 的最优性差距更重要。贪心方法还有一个关键的运维优势：它是透明且可调试的。当结果页看起来不对时，我们可以逐步追踪贪心放置过程。ILP 求解器是黑盒。
>
> **数据**：在 10,000 个查询样本上，贪心平均达到最优目标值的 96.3%。82% 的查询中，贪心产生了与精确求解器相同的 top-10。差异集中在约束竞争激烈的查询上（罕见边界情况）。

---

**Q: 这是你的代表性项目。你犯过的最大错误是什么，如果重来你会怎么做？**

> **诚实回答**：最大的错误是没有从第一天就投资**反事实评估（counterfactual evaluation）**。每次策略变更都需要 A/B 测试——通常需要 1-2 周的专用流量分配。如果有**IPS (Inverse Propensity Scoring)** 和 **DR (Doubly-Robust)** 估计器，我们可以在提交单个 A/B 测试之前离线评估 10+ 个策略变体。
>
> 我最终建立了离线评估基础设施，但那时我们已经花了大约 3 个月运行本可以并行化的顺序 A/B 测试。每个测试都消耗了本可服务于生产优化的流量。机会成本是显著的：我们可能将最终多样性配置延迟了 6-8 周。
>
> 根因是对初始策略设计的过度自信。我假设前几次 A/B 测试会快速收敛，所以离线评估感觉像是过度工程化。实际上，软约束、分段预算和学习率之间的交互创造了比我预期大得多的配置空间。系统性的离线探索本可以更快找到好的配置。
>
> **如果重来我会怎么做**：在第一个 sprint 就建立反事实评估框架，甚至在第一个策略约束之前。具体来说：
>
> 1. **从第一天就记录倾向分数（propensity scores）**（当前策略下每个商品在每个位置被展示的概率）
> 2. **实现 IPS 和 DR 估计器**用于离线策略评估
> 3. **使用离线评估将 A/B 测试空间**从数十个配置缩小到 2-3 个最有前景的
>
> **教训**：任何计划迭代策略的排序系统都需要从第一天就建立离线评估基础设施。A/B 测试用于验证，而非探索。这同样适用于打车匹配、定价或任何分配系统。

---

**Q: 你们如何确保多样性约束不会系统性地不利于某些卖家或造成不公平结果？**

> **承认局限**：多样性约束将槽位从主导卖家重新分配给代表不足的卖家。在纯相关性排序中排名靠前的卖家会失去槽位。这是刻意的权衡，但确实引发公平性问题。
>
> **应对措施**：这些约束旨在维护**市场健康**，而非个体卖家的结果。卖家上限（每页每卖家最多 3 件商品）防止搜索结果页被垄断。长尾卖家下限确保新卖家获得发现曝光。两者都由平台级指标驱动：
>
> - 买家满意度（多样性 = 更好的体验）
> - 市场流动性（更多活跃卖家 = 更健康的市场）
> - 长期收入（多元化的卖家基础降低平台风险）
>
> 我们向卖家公布约束策略，并提供面向卖家的仪表盘，展示他们的曝光份额及策略更新后的变化。
>
> **数据**：实施卖家多样性约束后，每天至少获得一次曝光的卖家数量增加了 18%。Top-10 卖家的曝光份额下降了 12%，但每次曝光的转化率提升了 8%（每个列表竞争减少 = 更高质量的流量）。卖家净满意度（通过季度调查衡量）保持中性——头部卖家理解了市场健康的论点。
"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## 口头大纲 (Verbal Outline)

### 3 分钟版本

**目标**：面向忙碌面试官或小组场景的电梯简报。

1. **(30s) 问题**：传统逐点排序独立评分每个商品，导致同质化的结果页——相同卖家、相同类目、相同价格区间。这损害了买家探索、长尾卖家和市场健康。

2. **(45s) 关键洞察**：将排序重新定义为资源分配。搜索页面有 $K=48$ 个槽位；排序就是将这些槽位分配给竞争性目标：相关性、多样性、公平性、收入。这解锁了约束优化工具。

3. **(60s) 架构**：两个循环。在线：**MUS (Model-Unified Scoring)** 校准归一化多模型分数，然后贪心重排在软约束（卖家多样性、类目多样性）和硬约束（法规、品牌安全）下填充槽位。离线：Kafka 管线收集用户交互事件，闭环策略调整比较每个查询分段的观测与目标多样性，以保守学习率和护栏每日更新预算。

4. **(30s) 生产规模**：50K QPS，<3ms 重排延迟，2,000 个查询分段通过层次化收缩处理稀疏数据，冷启动分段三阶段演进，每日策略更新 3-7 天收敛。

5. **(15s) 结果**：+3.5% 购买率，+2.8% 会话继续率。分配范式已在 eBay 的 3 个搜索垂直领域推广。

### 10 分钟版本

**目标**：面向招聘经理或系统设计轮的深度剖析。

1. **(1.5 min) 动机与问题陈述**
   - 逐点排序为何失败：组合问题的具体示例
   - 业务影响：同质化指标、买家疲劳数据、长尾卖家挤出
   - 分配洞察：$K$ 个槽位作为稀缺资源，约束作为策略杠杆

2. **(2 min) 分配建模**
   - 目标函数：在分组约束下最大化相关性
   - 硬约束 vs. 软约束分类及示例
   - MUS 校准：为什么多模型归一化是必要的，z-score 变换，每小时刷新节奏

3. **(2 min) 在线架构**
   - QN 检索时的多样性队列标记
   - Cassini ORC 管线：基础评分 -> MUS -> 贪心重排 -> 硬性覆写
   - 贪心算法细节：约束惩罚函数、复杂度分析、为什么不用精确 ILP

4. **(2 min) 闭环策略管理**
   - Kafka 反馈管线：事件 schema、topic 分区、端到端延迟
   - **DSBE (Diversity Segment Budget Engine)** Paradise Table：每分段的观测 vs. 目标
   - 调整引擎：更新规则、学习率、截断、相关性护栏
   - 收敛行为和生产稳定性数据
   - 稀疏分段的层次化收缩（经验贝叶斯）
   - 冷启动分段的三阶段演进策略

5. **(1.5 min) 生产约束与运维现实**
   - QPS、延迟预算、故障模式和回退方案
   - 监控：Grafana 仪表盘、告警阈值
   - 典型失败模式：预算振荡、约束冲突死锁、冷启动漂移及修复
   - 超参数调优表：$\lambda$、$\eta$、$n_0$ 等的搜索范围和最优值
   - 14 个月运行记录：7 次冻结，0 次退化状态

6. **(1 min) 回顾与教训**
   - 最大的错误：没有从第一天建立反事实评估
   - 3 个月的顺序 A/B 测试本可以并行化
   - 教训：A/B 测试用于验证，而非探索
   - 这如何适用于规模化分配系统（打车匹配、定价等）

### 面试过渡用语

连接作品集中的其他项目时：

- **来自 PBE Pipeline**："PBE 提供的无偏训练数据使得基础相关性分数足够可信，可以在此基础上构建分配框架。"
- **到 Module Arbitration**："一旦我们有了商品的分配框架，自然的延伸就是将相同的范式应用于模块——这就成为了 Module Arbitration 项目。"
- **到 LLM Orchestration**："分配基础设施也为 LLM 生成内容提供了服务框架——它们通过相同的约束系统竞争相同的页面槽位。"
"""


# ---------------------------------------------------------------------------
# Main: update the database record
# ---------------------------------------------------------------------------

def populate_ranking_allocation() -> None:
    """Find the ranking-allocation SystemDesign record and update all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == "ranking-allocation")
            .first()
        )

        if record is None:
            print("[FAIL] No SystemDesign record with slug='ranking-allocation' found.")
            print("       Run scripts/seed_system_designs.py first to create the record.")
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
        print("[DONE] Updated all 8 sections for ranking-allocation.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            "overview", "architecture", "dataflow", "formulas",
            "production_constraints", "tradeoffs", "defense", "verbal_outline",
        ]
        total = 0
        for section in sections:
            content = getattr(record, section)
            length = len(content) if content else 0
            total += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {section}: {length} chars {status}")
        print(f"  TOTAL: {total} chars")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_ranking_allocation()
