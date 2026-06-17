"""Populate ml-system-design-patterns system design with all 8 markdown sections.

Expands from cheat-sheet level (~8.5K chars) to interview depth (>=14K chars).
Adds: math formulations (NDCG, MAP, CTR lift CI, feature store freshness),
concrete production examples, 4+ Defense Q&A, failure modes per pattern,
iteration methodology.

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

SLUG = "ml-system-design-patterns"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = r"""## ML 系统设计面试模式 (ML System Design Interview Patterns)

本模块整合了两类来源的面试准备模式：

1. **系统设计面试框架 (System Design Interview Framework)** —— 六段式回答模板、三层防御式 Q&A 结构、多项目元叙事框架、生产约束词汇表（**QPS (Queries Per Second)**/**延迟 (Latency)**/成本）、以及技术决策速查表（**Thompson Sampling** vs **UCB (Upper Confidence Bound)**、逐条排序 vs 页面级分配、**IPW (Inverse Propensity Weighting，逆倾向加权)** 位置偏差校正）
2. **框架工程模式 (Framework Engineering Patterns)** —— 状态机设计（优先级驱动的状态推导）、带环检测的向上传播、时间戳不可变性、防御性编程原则

贯穿主题：**结构化准备优于死记硬背**。面试奖励的是在压力下导航决策空间的能力，而非背诵架构图的能力。本模块中的每个模式都可以在 45 分钟系统设计面试中直接使用。

### 为什么需要系统化的面试模式 (Why Systematic Interview Patterns)

大多数候选人准备系统设计的方式是"多读案例"——但单纯积累案例无法覆盖面试官的所有变体。系统化模式的优势在于：

- **可迁移性**：六段式模板和三层防御框架适用于任何系统设计题目
- **可量化**：每个模式都有可验证的信号（如延迟预算、A/B 指标）
- **可递归**：面试中遇到新题目时，可以用模式快速推导出合理架构

### 业务影响量化 (Quantifying Business Impact)

在面试中展示业务影响是区分中级和高级候选人的关键信号：

| 常见指标 | 典型数值范围 | 面试中如何引用 |
|----------|-------------|---------------|
| **CTR (Click-Through Rate，点击率)** 提升 | 2-8% 相对提升 | "页面级 CTR 从 3.2% 提升到 3.45%，+7.8% 相对" |
| **NDCG (Normalized Discounted Cumulative Gain)** | 0.65-0.85 | "排序模型 NDCG@10 从 0.72 提升到 0.78" |
| **延迟 (Latency) P99** | 50ms-200ms | "推理延迟 P99 从 180ms 降到 95ms" |
| **GMV (Gross Merchandise Value，成交总额)** | 1-5% 提升 | "页面级 GMV +4%，年化收入影响约 $12M" |
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 面试回答架构：六段式模板 (Interview Answer Architecture: The 6-Section Template)

六段式模板本身就是一个面试回答框架：

```
Overview       -> Why this system exists (motivation + business value)
Architecture   -> How it works (components + responsibilities)
Dataflow       -> How data flows (end-to-end pipeline)
Formulas       -> Core algorithms (whiteboard-derivable)
Tradeoffs      -> Why this choice over alternatives (decision ability)
Defense        -> How to respond under challenge (high-pressure Q&A)
```

**核心洞察**：准备系统设计不是"背架构图" —— 而是内化每个决策点的选项空间和选择理由。

### 每段的展开策略 (Expansion Strategy per Section)

| 段落 | 时间分配 | 关键信号 | 常见失误 |
|------|---------|---------|---------|
| Overview | 1-2 分钟 | 业务动机先于技术方案 | 直接跳进架构而不解释 "why" |
| Architecture | 3-5 分钟 | 组件职责清晰、边界明确 | 画了 10 个组件但每个只说一句话 |
| Dataflow | 2-3 分钟 | 端到端数据路径、延迟标注 | 只画了正常路径，缺少错误/重试路径 |
| Formulas | 2-3 分钟 | 白板可推导、符号定义清楚 | 写了公式但说不出每个变量的含义 |
| Tradeoffs | 3-5 分钟 | 比较至少两个方案、给出选择理由 | "我选了 X 因为它好" 而没有定量对比 |
| Defense | 5-10 分钟 | L1/L2/L3 层次化回答 | 只准备了 "why X" 而没有准备 "why not Y" 和 "when X breaks" |

### 状态机架构：优先级驱动的状态推导 (State Machine Architecture: Priority-Driven Status Derivation)

当父节点状态必须从子节点推导时：

```
ALL mastered       -> mastered
ANY in_progress    -> in_progress
ANY review         -> review
ALL not_started    -> not_started
else               -> in_progress  (fallback)
```

**为什么不用组合式**：`[mastered, review]` 在语义上是模糊的。优先级模型消除了歧义。添加新状态只需 O(1) 插入优先级链，而非指数级的组合增长。

### 向上传播模式 (Upward Propagation Pattern)
- `progress_pct` = 子节点的重要性加权平均
- 每个父层在更新时调用 `_derive_status`
- visited 集合防止循环；检测到环时记录 critical 日志 + 停止传播（不向用户抛出异常）

### 触发器完备性清单 (Trigger Completeness Checklist)
所有改变父子关系的事件都必须触发传播：
- 状态变更 / 进度变更 / 学习日志创建 / **子节点新增/移除**
- 遗漏任何触发器 = 父节点永久停留在过期状态

### 失败模式 (Failure Modes)
1. **遗漏触发器**：新增了"子节点移除"操作但忘记触发向上传播 -> 父节点永久显示过期状态。**修复**：维护触发器清单，每新增操作时逐项检查。
2. **组合爆炸**：状态机采用组合式而非优先级链 -> 每新增一个状态，边界情况数量指数增长。**修复**：始终使用优先级链，仅在语义确实需要组合行为时例外。
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 元叙事与技术决策流 (Meta-Narrative & Technical Decision Flow)

### 元叙事：多项目框架构建 (Meta-Narrative: Framing Multiple Projects)

当展示 4 个以上项目时，面试官的第一个问题通常是"谈谈你的工作"。你需要一个 30 秒的统一框架，然后按需展开。

**示例叙事弧线**：
> "我的核心工作是将逐条排序演进为页面级分配"

没有这个框架，4 个项目听起来毫无关联。有了它，每个项目都成为一个连贯故事中的一章。

### 叙事构建流程 (Narrative Construction Pipeline)

```
Step 1: 列出所有项目的核心贡献 (List core contribution per project)
  |
  v
Step 2: 寻找共同主题 (Find common theme / evolution arc)
  - 时间线式：从 X 演进到 Y
  - 层级式：底层基础设施 -> 上层应用
  - 问题驱动式：同一类问题在不同场景的解法
  |
  v
Step 3: 构造 30 秒统一叙事 (Craft 30-second unified narrative)
  - 模板："我的核心工作是 [动词] [对象] 从 [A] 到 [B]"
  |
  v
Step 4: 为每个项目准备 2 分钟展开 (Prepare 2-min deep dive per project)
  - 触发条件：面试官说 "Tell me more about X"
  - 结构：问题 -> 方案 -> 结果 -> 教训
```

### 技术决策速查表 (Technical Decision Quick-Reference)

| 决策点 | 选择 | 核心理由 | 常见陷阱 |
|--------|------|----------|----------|
| **Thompson Sampling** vs **UCB (Upper Confidence Bound)** | TS | 在非平稳奖励分布下表现更好；UCB 过于保守 | 原始 TS 假设平稳 -> 需要滑动窗口后验 |
| **LLM (Large Language Model)** 直接 vs 代理模式 | 代理（LLM 生成工件 -> 引擎执行） | 幻觉、延迟、库存新鲜度 | 低估回退路径的重要性 |
| 仅点击 vs 可视区域曝光 | 可视区域 (Viewport) | 点击稀疏（2-5% **CTR (Click-Through Rate，点击率)**）+ 严重位置偏差 | IntersectionObserver 边界情况（后台标签页、快速滚动） |
| 逐条排序 vs 分配 | 分配 (Allocation) | 逐条评分忽略页面级组合效应 | **LP (Linear Programming，线性规划)** 求解器必须保持 <5ms，否则降级为贪心 |
| 硬约束 vs 软约束（多样性） | 混合 (Hybrid) | 硬约束作为合规底线，软约束用于体验调优 | 纯软约束可能完全被违反；纯硬约束过于僵硬 |
| **IPW (Inverse Propensity Weighting，逆倾向加权)** 位置去偏 vs 不处理 | IPW | 位置 1 的 CTR 是位置 10 的 5-10 倍 | IPW 权重需要随机化实验，不能靠猜测 |
| 策略更新频率 | 每日批处理 | 避免日内震荡；允许隔夜分析 | 实时看起来"高级"但风险远超收益 |
| **MUS (Multi-model Unified Score)** 分数归一化 vs 原始分 | 归一化 (Normalized) | 多模型分数不可直接比较 | 归一化假设近似正态分布 —— 必须验证 |

### 失败模式 (Failure Modes)
1. **叙事碎片化**：4 个项目各讲 2 分钟但缺少统一框架 -> 面试官记不住重点。**修复**：先讲 30 秒统一叙事，再按需展开。
2. **决策速查表僵化**：死记速查表结论而不理解推导过程 -> 面试官追问 "why not" 时答不出。**修复**：每个决策点都准备 L1/L2/L3 三层回答。
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 排序质量度量：NDCG (Ranking Quality: NDCG)

**NDCG (Normalized Discounted Cumulative Gain，归一化折损累计增益)** 是评估排序系统最常用的离线指标：

$$\text{DCG}@k = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i+1)}$$

$$\text{NDCG}@k = \frac{\text{DCG}@k}{\text{IDCG}@k}$$

其中 $r_i$ 是位置 $i$ 的相关性评分，$\text{IDCG}@k$ 是理想排序下的 DCG。

**面试要点**：NDCG 对顶部位置的排序错误惩罚最重（$\log_2$ 分母增长慢），这与用户行为一致——用户很少浏览第二页。

### 检索质量度量：MAP (Retrieval Quality: MAP)

**MAP (Mean Average Precision，平均精度均值)** 衡量检索系统的精确率-召回率权衡：

$$\text{AP} = \frac{1}{\text{rel}} \sum_{k=1}^{n} P(k) \cdot \mathbb{1}[\text{doc}_k \text{ is relevant}]$$

$$\text{MAP} = \frac{1}{\lvert Q \rvert} \sum_{q \in Q} \text{AP}(q)$$

其中 $P(k)$ 是前 $k$ 个文档的精确率，$\text{rel}$ 是相关文档总数。

### CTR 提升的置信区间 (Confidence Interval for CTR Lift)

A/B 测试中 CTR 提升的显著性检验：

$$\hat{\delta} = \hat{p}_T - \hat{p}_C$$

$$\text{SE}(\hat{\delta}) = \sqrt{\frac{\hat{p}_T(1-\hat{p}_T)}{n_T} + \frac{\hat{p}_C(1-\hat{p}_C)}{n_C}}$$

$$\text{CI}_{95\%} = \hat{\delta} \pm 1.96 \cdot \text{SE}(\hat{\delta})$$

其中 $\hat{p}_T$, $\hat{p}_C$ 分别是 treatment 和 control 的 CTR，$n_T$, $n_C$ 是样本量。

**生产数字**：典型电商搜索 CTR 约 3-5%，检测 2% 相对提升（即绝对 0.06-0.10%）需要每组约 100 万样本（$\alpha=0.05$, $\beta=0.2$）。这决定了 A/B 测试至少需要 1-2 周的流量积累。

### 特征存储新鲜度 SLA (Feature Store Freshness SLA)

特征存储的**新鲜度 (freshness)** 定义为特征值与真实世界状态之间的最大允许延迟：

$$\text{freshness}(f) = t_{\text{serve}} - t_{\text{event}}$$

$$\text{SLA: } P(\text{freshness}(f) \leq \tau) \geq 1 - \epsilon$$

其中 $\tau$ 是最大允许延迟，$\epsilon$ 是违规容忍度。

| 特征类别 | $\tau$ | $\epsilon$ | 典型实现 |
|----------|--------|-----------|---------|
| 用户画像 (User profile) | 24h | 1% | 每日批量 Spark |
| 实时计数 (Real-time counts) | 5min | 0.1% | Kafka + Flink |
| 物品元数据 (Item metadata) | 1h | 0.5% | CDC + Redis |

### 状态机公式与时间戳规则 (State Machine Formulas & Timestamp Rules)

#### 优先级驱动的状态推导 (Priority-Driven Status Derivation)
```
priority_chain = [mastered, in_progress, review, not_started]
derive_status(children):
  if ALL children.status == mastered: return mastered
  for status in [in_progress, review]:
    if ANY child.status == status: return status
  if ALL children.status == not_started: return not_started
  return in_progress  # fallback for mixed states
```

#### 时间戳不可变性规则 (Timestamp Immutability Rule)
```
started_at:    set once on first activity, NEVER cleared
completed_at:  set once on completion, NEVER cleared on rollback
```
**原因**：`completed_at` 记录的是"这个事件发生了"，而非"当前状态为已掌握"。回退时清除它会销毁历史记录。时间戳是事件日志，不是状态字段。

#### 进度聚合 (Progress Aggregation)

$$\text{parent.progress} = \frac{\sum_{c \in \text{children}} w_c \cdot \text{progress}_c}{\sum_{c \in \text{children}} w_c}$$

其中 $w_c$ 是子节点 $c$ 的重要性权重。重要性加权平均在异构子话题之间保持了相对重要性。

### 失败模式 (Failure Modes)
1. **NDCG 与业务指标脱节**：NDCG 提升但 CTR/GMV 未变 -> 相关性标签与用户行为不一致。**修复**：用点击数据校准相关性标签，或直接用 CTR 作为 NDCG 的增益函数。
2. **A/B 测试假阳性泛滥**：同时运行 20 个实验，5% 显著性水平下平均有 1 个假阳性。**修复**：使用 **Benjamini-Hochberg** 校正多重比较，或使用 **Sequential testing** 减少所需样本量。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产约束词汇表与模式 (Production Constraint Vocabulary & Patterns)

每个系统设计回答都必须能够引用具体数字：

| 约束维度 | 典型数值 | 面试中如何使用 |
|----------|---------|---------------|
| **QPS / 吞吐量** | 搜索: 10K-100K, 推荐: 1K-10K | "峰值 50K QPS，每查询触发完整仲裁" |
| **延迟预算 (P50 / P99)** | 推理: 20-100ms, 端到端: 100-300ms | "模型推理 P99 < 50ms，端到端 P99 < 200ms" |
| **数据规模** | 日增量: 1-10 亿事件, 特征存储: TB 级 | "约 5 亿曝光/天，特征存储 6 个月滚动窗口" |
| **候选集规模** | 粗排: 10K-100K, 精排: 100-1000 | "从 100K 候选中粗排到 500，精排到 50" |
| **成本（月度量级）** | 训练: $1K-10K, 推理: $10K-100K | "GPU 推理成本月均 $30K，占搜索总成本 15%" |
| **故障模式 & 回退** | 降级延迟 +50%, 回退到缓存 | "模型超时时回退到规则引擎 + 缓存排序" |

**关键信号**：能够流畅描述算法但说不出延迟数字 -> 面试官会判定"从未上线过"。

### 工程流程约束 (Engineering Process Constraints)

#### 幂等的种子/迁移脚本 (Idempotent Seed/Migration Scripts)
- `upsert by slug`，而非 `insert` —— 重跑必须安全
- 任何批量写入端点默认 `skip existing`，需显式 `force` 标志才覆盖
- 数据库级唯一索引强制幂等性，而非仅依赖代码级检查

#### 列表 API 卫生 (List API Hygiene)
- `GET /collection` 仅返回摘要字段，绝不返回完整内容
- 详细内容通过 `GET /collection/:id` 按需获取

#### 迁移顺序 (Migration Ordering)
- 后端 schema -> 迁移 -> 前端展示
- 防止部署期间 UI 短暂显示脏数据/缺失数据

#### 层级数据中的环检测 (Cycle Detection in Hierarchical Data)
- visited 集合防止无限传播循环
- 但环的存在本身就标志着数据损坏
- 检测到时记录 critical 日志；不要静默跳过

### 延迟预算分配模式 (Latency Budget Allocation Pattern)

在面试中展示延迟分解是高级候选人的标志性动作：

```
典型推荐系统端到端延迟分解 (P50):
  查询解析 + 用户画像查找:          5ms
  候选检索 (ANN):                  10ms
  粗排 (lightweight model):        15ms
  精排 (heavy model):              30ms
  业务规则 + 多样性过滤:            5ms
  响应序列化:                       3ms
  ---
  合计:                          ~68ms (budget: <100ms P50)
```

**面试技巧**：画完延迟分解后，主动指出瓶颈在哪里、优化空间在哪里。例如："精排占了 44% 的延迟，如果需要降低延迟，首先考虑模型蒸馏或量化。"

### 失败模式 (Failure Modes)
1. **无回退的模型服务**：模型超时或异常时整个请求失败 -> 用户看到空白页。**修复**：三层降级策略——(1) 模型缓存最近结果，(2) 规则引擎兜底，(3) 随机排序作为最后手段。
2. **特征存储过期未检测**：批处理 Spark 任务静默失败，特征停留在 48 小时前的状态 -> 模型用过期特征做预测。**修复**：新鲜度监控告警 + 特征时间戳校验，超过 SLA 时触发回退到默认值。
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 固定列 vs JSON 内容存储 (Fixed Columns vs JSON for Content Storage)
| 方案 | 优点 | 缺点 |
|------|------|------|
| 固定列（6 个 Text） | 直接查询、部分更新、类型安全 | 添加字段需要迁移 |
| JSON 列 | 灵活 schema、嵌套结构 | 解析复杂、部分更新需读-改-写 |

**决策规则**：如果段落数量/结构是固定的 -> 固定列。JSON 仅在结构在运行时真正变化时使用。不要为了假设的未来灵活性牺牲当前简洁性（**YAGNI, You Ain't Gonna Need It**）。

### 独立表 vs 复用已有树结构 (Independent Table vs Reusing Existing Tree Structure)
系统设计案例研究是自包含的 —— 它们不是层级知识节点。数据模型应反映领域语义，而非为了复用而强行塞进已有结构。

### 静态文件 vs DB Blob vs 对象存储（图片）(Static Files vs DB Blob vs Object Storage for Images)
- 少量图片（<10），无用户上传，无访问控制 -> 静态文件由 Vite 服务
- 迁移阈值：用户上传或频繁变更的图片

### 组合式 vs 优先级链状态机 (Combinatorial vs Priority-Chain State Machines)
- 组合式：每个新状态带来指数级边界情况
- 优先级链：线性复杂度、确定性、易于扩展
- 除非状态语义确实需要组合特定行为，否则使用优先级链

### 防御性代码策略对比 (Defensive Code Strategy Comparison)

| 策略 | 适用场景 | 风险 |
|------|---------|------|
| 静默跳过 | 几乎不适用 | 最危险的隐藏 bug 模式 |
| 崩溃（raise） | 开发环境 | 因基础设施错误阻塞用户 |
| **记录 critical + 继续** | 生产环境首选 | 需配合告警系统，否则日志被忽略 |

### 功能完备性：降级展示 vs 完全隐藏 (Feature Completeness: Show Degraded vs Hide Entirely)
- "降级展示"需要完整的数据流水线
- 如果数据流水线损坏，任何展示都是误导
- 完全隐藏功能好过展示虚假/过期数据

### 迭代与评估方法论 (Iteration & Evaluation Methodology)

系统设计面试中，展示如何**验证和迭代**方案是 Staff+ 级别的核心信号。

#### 三层评估策略 (3-Layer Evaluation Strategy)

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **离线评估** | 留出集 + NDCG/MAP/AUC | 小时级 | 模型/算法变更的快速筛选 |
| **交错测试** | Team-Draft Interleaving (TDI) | 天级 | 以高统计功效比较两个排序策略 |
| **A/B 测试** | 流量分割 (5% treatment) | 1-2 周 | 全量上线前的最终验证 |

#### 关键超参数调优模式 (Key Hyperparameter Tuning Patterns)

| 参数 | 调优方法 | 典型结果 |
|------|---------|---------|
| 模型复杂度（层数/宽度） | 离线 NDCG + 延迟预算约束 | 3 层 MLP 在延迟和精度间最优 |
| 探索权重 $\epsilon$ | 贝叶斯优化 + A/B 验证 | 起始 0.3，退火至 0.05 |
| 多样性约束强度 | UX 评审 + A/B 测试跳出率 | 同类型上限 k=3，过低则跳出率 +15% |
| 特征更新频率 | 离线 ablation + 成本分析 | 用户画像每日更新，实时计数每 5 分钟 |

#### 失败模式 (Failure Modes)
1. **离线-在线指标不一致**：NDCG 提升但 A/B 测试无显著差异 -> 离线评估集与线上分布漂移。**修复**：定期用最新线上数据刷新评估集，添加 **drift detection** 监控。
2. **A/B 测试的新奇效应 (Novelty effect)**：新功能上线初期 CTR 飙升，但一周后回归基线 -> 用户对新 UI 好奇而非真正偏好。**修复**：A/B 测试跑满 2 周以上，观察指标趋势而非只看第一周。
3. **多层 API 回退过度工程**：对于小规模数据缺口（如 5 条缺失描述），手动回填比维护多层爬取流水线更经济。回退层数与维护成本线性相关。
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = r"""## 防御模式：三层面试 Q&A 结构 (Defense Patterns: 3-Layer Interview Q&A Structure)

### L1-L2-L3 框架 (The L1-L2-L3 Framework)
```
L1 Clarification:  'Why X?'              -> Explain your choice
L2 Challenge:      'Why not Y?'           -> Compare alternatives
L3 Attack:         'X breaks when ___'    -> Acknowledge limits + show mitigation
```

**L3 是 Staff+ 信号。** 多数候选人只准备到 L1。从容应对 L3 的回答展示了对设计边界的深层理解。

### 防御具体决策 (Defending Specific Decisions)

**Thompson Sampling 选择**：
- L1："**TS (Thompson Sampling)** 在非平稳奖励分布下表现优于 **UCB (Upper Confidence Bound)**"
- L2："UCB 的置信上界在我们的场景下过于保守 —— 探索预算浪费在了明显次优的臂上"
- L3："原始 TS 假设平稳性。我们使用滑动窗口后验重置来应对分布漂移。权衡：窗口大小是一个需要按领域调优的超参数。"

**可视区域优先于仅点击 (Viewport over click-only)**：
- L1："点击稀疏（2-5% **CTR (Click-Through Rate，点击率)**）且位置偏差严重"
- L2："**IPW (Inverse Propensity Weighting，逆倾向加权)** 校正位置偏差但会放大稀疏点击的方差"
- L3："IntersectionObserver 有边界情况 —— 后台标签页、快速滚动。我们定义最小停留时间阈值并排除后台标签页事件。"

**分配优先于逐条排序 (Allocation over pointwise ranking)**：
- L1："逐条评分忽略页面级组合效应"
- L2："Listwise 方法成本高昂。通过 **LP (Linear Programming，线性规划)** 的分配同时捕获多样性和业务约束。"
- L3："LP 求解器必须保持在 5ms 以内。当候选集过大时，我们用逐条分数预筛选，然后在 top-K 上运行分配。这是有原则的降级，而非放弃分配。"

---

**Q1: 你用 NDCG 评估排序质量，但 NDCG 依赖人工标注的相关性标签。标注成本高且主观。如何保证评估可靠？**

> **承认局限**：你说得对——NDCG 的质量完全取决于标注质量。人工标注不仅昂贵（每个 query-doc 对约 $0.10-0.50），而且标注者之间的一致性（**inter-annotator agreement**）通常只有 Cohen's $\kappa \approx 0.4-0.6$。
>
> **缓解措施**：我们使用三层评估策略替代纯人工 NDCG：
>
> 1. **隐式反馈 NDCG**：用点击数据作为相关性代理（点击=1，曝光未点击=0），虽然有位置偏差但样本量大
> 2. **人工标注采样**：每周从线上流量中采样 500 个 query-doc 对进行三人标注，用于校准隐式反馈的偏差
> 3. **交错测试 (Interleaving)**：直接在线比较两个排序策略，无需标注
>
> **数据**：隐式反馈 NDCG 与三人标注 NDCG 的 Spearman 相关系数为 0.78。交错测试在 1 天内可检测到 NDCG 0.02 的差异，而 A/B 测试需要 7-10 天。

---

**Q2: 你的特征存储新鲜度 SLA 要求实时计数特征 5 分钟内更新。Flink 任务挂了怎么办？模型会用过期特征吗？**

> **承认局限**：是的——Flink 任务故障是实际会发生的。如果不处理，模型会静默使用过期特征，预测质量下降但无告警。
>
> **缓解措施**：三层防御：
>
> 1. **新鲜度水印 (Freshness watermark)**：每个特征值附带 `updated_at` 时间戳。服务时检查 `now() - updated_at > SLA`，超期则使用默认值而非过期值
> 2. **降级策略 (Graceful degradation)**：实时特征不可用时，回退到最近一次批处理版本（24 小时前），同时将此特征的重要性权重降低 50%
> 3. **告警 + 自动恢复**：Flink checkpoint 间隔 1 分钟，故障后从最近 checkpoint 恢复。如果 3 次重启仍失败，触发 PagerDuty 告警
>
> **数据**：过去 6 个月 Flink 任务可用性 99.95%。降级到批处理特征期间，CTR 预测准确度下降约 3%（可接受），但不会出现完全错误的预测。

---

**Q3: 你建议用优先级链状态机而非组合式。但如果业务要求某些状态组合有特殊行为怎么办？优先级链不就丢失了这些信息？**

> **承认局限**：优先级链确实会丢失组合信息——`[mastered, review]` 和 `[in_progress, review]` 在优先级链中都返回 `in_progress`，如果业务需要区分这两种组合，纯优先级链做不到。
>
> **缓解措施**：混合方案——优先级链作为**默认推导规则**，业务特殊行为通过**显式覆盖表 (override table)** 实现：
>
> ```
> override_rules = {
>   (mastered, review): "needs_review",  # 特殊：已掌握但有新评审
>   # 其他所有组合 -> 走默认优先级链
> }
> ```
>
> 覆盖表的规模是 O(特殊组合数)，而非 O(状态数^2)。只要特殊组合数远小于总组合数（实践中通常 <5%），复杂度就是可控的。
>
> **数据**：在我们的系统中，5 个状态的优先级链覆盖了 95% 的推导场景，只有 2 个特殊组合需要覆盖规则。

---

**Q4: 你推荐 A/B 测试跑 2 周以排除新奇效应。但业务等不了 2 周怎么办？如何加速实验？**

> **承认局限**：2 周是理想值，但在实际业务节奏下（尤其是促销前）确实太慢。
>
> **缓解措施**：三种加速策略：
>
> 1. **交错测试 (Interleaving)**：统计功效比 A/B 测试高 10-100 倍，1-2 天可出结果。适合排序策略比较，但无法测量绝对业务指标（如 GMV）
> 2. **Sequential testing**：使用 **CUSUM** 或 **mSPRT** 方法，在数据足够时提前停止实验，平均减少 30-40% 的等待时间
> 3. **分层触发 (Triggered analysis)**：只分析实际受影响的用户子群（例如只看搜索了特定类目的用户），有效样本量更大，收敛更快
>
> **数据**：交错测试 + 触发分析的组合，在实践中将实验周期从 14 天缩短到 3-5 天，覆盖了 80% 的实验场景。剩余 20% 的高风险实验（如定价策略变更）仍需完整 A/B 测试。

---

**Q5: 你的延迟预算分配假设各阶段是串行的。但如果引入并行化（如候选检索和用户画像查找并行），预算分配方式是否需要改变？**

> **承认局限**：串行假设确实过于简化。实际系统中，很多阶段可以并行执行，这改变了关键路径的计算方式。
>
> **缓解措施**：延迟预算应基于**关键路径 (critical path)** 而非各阶段之和：
>
> ```
> 串行模型:  总延迟 = 查询解析 + 检索 + 粗排 + 精排 + 过滤 + 序列化 = 68ms
> 并行模型:  总延迟 = max(查询解析 + 检索, 用户画像查找) + 粗排 + 精排 + 过滤 = 58ms
> ```
>
> 关键变化：(1) 关键路径上的阶段分配更多预算，(2) 非关键路径的阶段可以"借用"空闲时间但不能超过关键路径延迟，(3) 并行化引入了**尾延迟放大**——如果 3 个并行请求中任一个慢，整体就慢。
>
> **数据**：并行化将端到端 P50 从 68ms 降到 58ms（-15%），但 P99 只从 150ms 降到 140ms（-7%）——因为 P99 由最慢的并行分支决定。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 口述大纲：ML 系统设计面试模式 (Verbal Outline: ML System Design Interview Patterns)

### 3 分钟版本 (3-Minute Version)
本模块涵盖两个领域：面试专项模式和可迁移到任何系统设计讨论的工程设计模式。

**面试模式**：六段式模板结构化任何回答（概述、架构、数据流、公式、权衡、防御）。三层防御框架（澄清、挑战、何时失效）是关键区分因素 —— L3 回答是 Staff+ 信号。元叙事框架将多个项目串连为 30 秒的连贯故事。

**工程模式**：优先级驱动的状态机优于组合式方法。时间戳不可变性（事件日志，而非状态字段）。层级传播的触发器完备性。

**核心公式**：排序用 NDCG@k（顶部位置权重最高），A/B 测试用 CTR 提升置信区间（样本量决定实验周期），特征新鲜度 SLA（实时特征 5 分钟，批量特征 24 小时）。

**生产可信度**：始终准备好 **QPS (Queries Per Second)**、延迟 P50/P99、数据规模和成本数字。没有这些，面试官会认为你从未上线过。

### 10 分钟版本 (10-Minute Version)
展开每个领域：

**六段式模板**（2 分钟）：逐一讲解每个段落的目的。Overview = 为什么（动机），Architecture = 怎么做（组件），Dataflow = 数据流转，Formulas = 白板推导，Tradeoffs = 决策理由，Defense = 对抗性 Q&A。每段的时间分配和常见失误。

**三层防御**（3 分钟）：L1 = 解释选择。L2 = 与面试官将会提到的替代方案比较。L3 = 承认设计在哪里失效并展示缓解方案。以 **TS (Thompson Sampling)** vs **UCB (Upper Confidence Bound)** 演示：L1 非平稳优势，L2 UCB 浪费的探索预算，L3 滑动窗口后验的权衡。

**核心公式推导**（2 分钟）：
- NDCG: $\text{DCG}@k = \sum \frac{2^{r_i}-1}{\log_2(i+1)}$，归一化后 $\in [0,1]$
- CTR 提升检验: $\hat{\delta} \pm 1.96 \cdot \text{SE}$，典型样本量 100 万/组
- 特征新鲜度: $P(\text{freshness} \leq \tau) \geq 1 - \epsilon$，实时特征 $\tau=5\text{min}$

**技术决策**（2 分钟）：快速过决策表。可视区域优于点击（稀疏 + 偏差），分配优于逐条排序（组合效应），混合约束（硬底线 + 软调优），**IPW (Inverse Propensity Weighting，逆倾向加权)**（5-10 倍位置偏差），每日批处理策略（避免震荡）。

**状态机模式**（1 分钟）：优先级链消除组合爆炸。时间戳不可变性保留审计轨迹。传播触发器必须穷举 —— 遗漏"子节点移除"是经典 bug。

**生产约束 + 延迟预算**（1 分钟）：约束词汇表清单（QPS、延迟、规模、成本、故障模式）。延迟分解画出来，主动指出瓶颈和优化方向。幂等迁移。部署顺序（后端 -> 迁移 -> 前端）。

**迭代方法论**（1 分钟）：三层评估（离线/交错/A/B）。超参数调优模式。典型失败模式（离线-在线不一致、新奇效应、多重比较假阳性）。
"""


def populate_ml_system_design_patterns() -> None:
    """Update the ml-system-design-patterns record with all 8 markdown sections."""
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
        total = 0
        for name, content in sections:
            length = len(content) if content else 0
            total += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")
        print(f"  TOTAL: {total} chars")

        # Count display math blocks
        all_content = "\n".join(c for _, c in sections if c)
        math_count = all_content.count("$$")
        print(f"  Display math ($$) pairs: {math_count // 2}")

        # Count Q&A
        qa_count = all_content.count("**Q")
        print(f"  Q&A count: {qa_count}")

        # Check for bare |
        lines = all_content.split("\n")
        bare_pipe_count = 0
        for _i, line in enumerate(lines):
            # Skip table rows and code blocks
            if line.strip().startswith("|") or line.strip().startswith("```"):
                continue
            if "$$" in line or line.strip().startswith("#"):
                continue
            # Check for bare | in math context (inside $ ... $)
            in_math = False
            for j, ch in enumerate(line):
                if ch == "$":
                    in_math = not in_math
                elif ch == "|" and in_math:
                    # Check if it's \mid
                    if j == 0 or line[j-1:j+1] != "\\|":
                        if "\\mid" not in line[max(0, j-4):j+1]:
                            bare_pipe_count += 1
        if bare_pipe_count == 0:
            print("  [OK] No bare | in math contexts")
        else:
            print(f"  [WARN] {bare_pipe_count} potential bare | in math contexts")

        # Count Chinese characters
        chinese_count = sum(1 for ch in all_content if '\u4e00' <= ch <= '\u9fff')
        print(f"  Chinese characters: {chinese_count}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_ml_system_design_patterns()
