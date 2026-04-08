"""Populate llm-orchestration system design with all 8 expanded markdown sections.

Expands llm-orchestration to interview-ready depth: adds prompt engineering details,
distillation pipeline, iteration & evaluation, failure modes, and additional Defense Q&A.

Chinese translation with English technical terms preserved (bold + first-use
explanation). Formulas and code blocks kept as-is. Formulas use \\mid not |.

Idempotent: overwrites existing content for the llm-orchestration slug.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "llm-orchestration"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

传统搜索依赖**关键词匹配 + 学习排序**，这在处理复杂多意图查询时力不从心
（例如 "vintage leather jacket under $100 with free shipping from top-rated sellers"）。
**LLM (Large Language Model，大语言模型)** 能理解细腻的意图，但由于幻觉、延迟
和缺乏实时库存感知，无法大规模执行检索。

### 代理模式 (The Proxy Pattern)

我们的方案将 LLM 用作**制品生成器 (Artifact Generator)**，而非检索引擎：

1. LLM 分析查询并生成**结构化制品 (Structured Artifacts)**：意图标签、
   过滤约束和查询改写。
2. 现有的 **Cassini** 搜索引擎使用这些制品执行检索。

> **核心洞察**：LLM 的智能 + Cassini 的可靠性。LLM 从不直接接触库存——
> 它只是塑造 Cassini 遵循的指令。

### 为什么这很重要 (Why This Matters)

| 方案 | 意图理解 | 检索准确性 | 延迟 | 幻觉风险 |
|------|----------|------------|------|----------|
| 关键词搜索 | 低 | 高 | 低 | 无 |
| 端到端 LLM | 高 | 低 | 高 | 高 |
| **代理模式** | **高** | **高** | **中** | **无** |

代理模式兼取两者之长：LLM 的语义理解能力与 Cassini 久经考验的检索管道。

### 关键挑战 (Key Challenges)

即使在代理模式下，系统仍面临三类核心挑战：

1. **制品质量保障**：LLM 可能生成格式错误的 JSON、幻觉出不存在的过滤字段、
   或产生语义偏移的查询改写。需要多层验证机制。
2. **延迟-准确率权衡**：大模型（100B+）准确率高但延迟不可接受；小模型（7B）
   延迟达标但需要精心的蒸馏和微调来弥补能力差距。
3. **持续演进**：搜索意图分布随季节、促销和用户行为演变。系统必须具备在线
   监控、离线评估和自动化迭代能力。
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深入剖析 (Architecture Deep Dive)

### 在线推理栈 (Online Inference Stack)

在线路径通过多阶段管道处理每个查询：

```
Query -> SaaS Orchestrator -> Context Manager -> Generator LLM -> Artifact Set -> Cassini -> Response
```

**组件：**

- **SaaS Orchestrator（SaaS 编排器）**：将查询路由到处理管道，管理超时（LLM 80ms 预算），处理回退逻辑。
- **Context Manager（上下文管理器）**：聚合会话上下文——历史查询、点击记录、购物车内容和浏览历史——为 LLM 生成紧凑的 prompt。
- **Generator LLM（生成式 LLM）**：微调后的约 7B 参数模型，生成结构化制品。规模足够小，在 A10 GPU 上实现 P99 < 65ms 推理。
- **Agent Artifact Set（智能体制品集）**：LLM 的输出，包含：
  - **Intent/Affinity Digest（意图/亲和摘要）**：查询的语义分解
  - **Proxy（代理指令）**：过滤和约束规格
  - **SrpAgentGist（SRP 智能体摘要）**：供下游组件使用的结构化摘要

### Prompt 工程与制品生成 (Prompt Engineering & Artifact Generation)

Context Manager 构建的 prompt 采用**结构化模板 (Structured Template)** 设计，
分为四个段：

```
[SYSTEM] Role definition + output schema (JSON schema with required fields)
[CONTEXT] Session history: last 5 queries + click/cart signals
[QUERY] Current query text + detected locale + device type
[CONSTRAINTS] Max output tokens: 256; required fields: intent, filters, rewrite
```

**关键设计决策：**

1. **Schema-Constrained Decoding（模式约束解码）**：使用 **Outlines** 库在
   token 级别强制 JSON 语法。每个 token 采样时，无效 token 的 logit 被置为
   $-\infty$。这将格式错误率从 3.2% 降至 0.01%。

2. **Few-Shot Exemplars（少样本示例）**：prompt 中包含 3 个与当前查询类型
   （品牌/类目/长尾）匹配的示例。示例通过**查询类型分类器 (query-type
   classifier)** 动态选择，而非硬编码。

3. **Field Validation Gate（字段验证门控）**：LLM 输出经过后处理验证：
   - 过滤字段是否在 Cassini schema 的合法字段列表中
   - 价格范围是否合理（$0-$10,000）
   - 意图标签是否在预定义类目树的叶子节点中

验证失败时，制品被丢弃并回退到缓存或纯 Cassini。

### 代理模型蒸馏管道 (Proxy Model Distillation Pipeline)

生产 7B 模型通过教师-学生蒸馏从更大的教师模型获得能力：

```
Teacher (GPT-4 class, ~100B)
  |
  | Step 1: Generate labeled artifacts for 500K diverse queries
  |         (offline batch, ~$15K API cost per refresh)
  |
  v
Training Data: (query, context, teacher_artifact) triples
  |
  | Step 2: Fine-tune student (7B) on teacher outputs
  |         + human-labeled corrections for teacher errors
  |
  v
Student Model (7B, fine-tuned)
  |
  | Step 3: Distance calibration against teacher on held-out set
  |
  v
Production Model (deployed to A10 GPU cluster)
```

**蒸馏刷新周期**：每季度用新查询分布重新生成教师标签并微调学生模型。
月度中间更新使用 **LoRA (Low-Rank Adaptation)** 适配器微调，仅更新约 2%
的参数（约 140M），训练时间从 48 小时缩短到 6 小时。

### Cassini 执行引擎 (Cassini Execution Engine)

Cassini 通过四个排序阶段处理制品：

1. **L1 Ranking（L1 排序 - 流行度）**：使用倒排索引 + 流行度先验快速检索候选。从数百万缩减到约 1000 个候选。
2. **Intent-Affinity Gating（意图亲和门控）**：使用 LLM 生成的意图信号对候选进行软门控。降权（而非移除）不匹配的商品。
3. **L2 Ranking（L2 排序 - 神经网络）**：全神经排序模型对门控后的候选集打分。
4. **Attribution-Aware Diversity Scoring（归因感知多样性评分）**：**MMR (Maximal Marginal Relevance)** 风格的重排序，对未充分代表的卖家/品类给予来源溯源加分。

### 离线学习与演进循环 (Offline Learning & Evolution Loop)

```
Sojourner/Cassini logs
  -> Unified Feature Table (streaming aggregation)
  -> Learning Core:
       - Distance Calibration (4-hour cycle)
       - MLR Training (daily)
       - Proxy Execution feedback
  -> SDF Service deploys updated models
```

离线循环利用生产参与度数据持续改善 LLM 的制品质量和 Cassini 的排序模型。
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 在线路径（每查询） (Online Path - per query)

```
User Query
  |
  v
SaaS Orchestrator (timeout budget: 200ms total)
  |
  v
Context Manager (session history, cart, prior clicks)
  |  -> Structured prompt: [SYSTEM][CONTEXT][QUERY][CONSTRAINTS]
  |
  v
Generator LLM (~7B, P50: 35ms, P99: 65ms)
  |  -> Schema-constrained decoding (Outlines)
  |
  +---> Intent/Affinity Digest
  +---> Proxy (filter constraints)
  +---> SrpAgentGist (structured summary)
  |
  v
Field Validation Gate
  |  -> Check: fields in schema? price range valid? intent in taxonomy?
  |  -> FAIL -> fallback to cache / pure Cassini
  |
  v
Cassini Execution Engine
  |---> L1 Retrieval (popularity-based, ~1000 candidates)
  |---> Intent-Affinity Gating (soft gate, confidence threshold 0.7)
  |---> L2 Neural Ranking (full scoring)
  |---> Attribution-Aware Diversity (MMR + source bonus)
  |
  v
Structured JSON Response -> Structured Builder -> User
```

### 离线路径（持续运行） (Offline Path - continuous)

```
User Interactions (clicks, purchases, dwell time)
  |
  v
Sojourner + Cassini Logs (raw events)
  |
  v
Unified Feature Table (~2TB, 2-week sliding window)
  |  (streaming aggregation via Kafka + Spark)
  |
  v
Learning Core
  |---> Distance Calibration (every 4 hours)
  |---> MLR Training (daily, ~50M query-artifact-engagement triples)
  |---> Proxy Execution Feedback (artifact quality monitoring)
  |
  v
SDF Service (model deployment) -> Updated Generator LLM + Cassini models
```

### 蒸馏数据流 (Distillation Data Flow)

```
Query Sampling (stratified by intent type + traffic volume)
  |
  v
Teacher LLM (GPT-4 class, batch inference)
  |  -> 500K labeled (query, context, artifact) triples
  |
  v
Human Review (sample 5K for error correction)
  |
  v
Training Pipeline (PyTorch + DeepSpeed)
  |  -> Full fine-tune: quarterly (~48h on 8x A100)
  |  -> LoRA adapter: monthly (~6h on 4x A10)
  |
  v
Evaluation Gate
  |  -> Intent accuracy >= 91%?
  |  -> Format error rate <= 0.05%?
  |  -> Latency P99 <= 70ms?
  |  -> PASS -> deploy; FAIL -> rollback to previous checkpoint
  |
  v
Canary Deployment (5% traffic, 24h)
  |  -> Monitor: CTR delta, fallback rate, error rate
  |  -> AUTO-PROMOTE if metrics within bounds
  |  -> AUTO-ROLLBACK if CTR drops > 0.5% or error rate > 1%
```

### 回退链 (Fallback Chain)

当 LLM 路径不可用时，系统优雅降级：

1. **主路径**：LLM 生成制品，Cassini 执行检索
2. **Tier 2**：使用最近相似查询的缓存制品
3. **Tier 3**：纯 Cassini（无制品）——即 LLM 上线前的生产系统

> 当 LLM 错误率在 1 分钟窗口内超过 5% 时，熔断器触发 Tier 3。错误率下降后自动恢复。

### 制品质量监控 (Artifact Quality Monitoring)

实时监控维度：

| 指标 | 阈值 | 告警动作 |
|------|------|----------|
| **格式错误率** | > 0.05% | P1 告警，自动回退到缓存 |
| **字段验证失败率** | > 2% | P2 告警，检查 schema 漂移 |
| **意图分布漂移** | KL 散度 > 0.1 | P2 告警，触发蒸馏数据刷新 |
| **回退率** | > 5% | P1 告警，检查 GPU 集群健康 |
| **缓存命中率** | < 60%（Tier 2） | P3 告警，扩大缓存窗口 |
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 意图亲和门控 (Intent-Affinity Gating)

门控函数决定制品意图信号对候选评分的影响强度：

$$\text{gate}(d, a) = \sigma(W_g \cdot [e_d;\; e_a;\; e_d \odot e_a])$$

其中：
- $e_d$ = 文档嵌入
- $e_a$ = 制品（意图）嵌入
- $\odot$ = 逐元素乘积（交互项）
- $\sigma$ = sigmoid 激活函数
- $W_g$ = 可学习的门控权重

门控输出是 $[0, 1]$ 范围内的**软权重**，用于缩放文档的 L2 排序分数。门控值
0.7 意味着文档分数乘以 0.7——不是移除，而是降权。

### 距离校准 (Distance Calibration)

将代理模型的预测与完整 LLM 的输出进行校准：

$$\mathcal{L}_{\text{cal}} = \sum_{(q,d)} \text{sign}(y) \cdot \|f(q,d) - \hat{f}_{\text{proxy}}(q,d)\|^2$$

其中：
- $f(q,d)$ = 完整 LLM 对查询-文档对的制品分数
- $\hat{f}_{\text{proxy}}(q,d)$ = 代理模型的预测分数
- $\text{sign}(y)$ = 基于参与度标签 $y$ 的非对称惩罚

**平滑近似**：由于 $\text{sign}$ 在零点不可微，我们使用：

$$\text{sign}(y) \approx \tanh(\beta \cdot y), \quad \beta = 5$$

这保持了梯度流，同时维持非对称行为：对**过度过滤的惩罚大于不足过滤**
（漏掉相关结果比展示边界结果更严重）。

### 蒸馏损失函数 (Distillation Loss Function)

学生模型训练使用教师输出的 **KL 散度 (Kullback-Leibler Divergence)** 加上
标注数据的交叉熵损失：

$$\mathcal{L}_{\text{distill}} = (1-\alpha) \cdot \mathcal{L}_{\text{CE}}(y, p_s) + \alpha \cdot T^2 \cdot D_{\text{KL}}(p_t^{(T)} \| p_s^{(T)})$$

其中：
- $p_s$ = 学生模型的输出分布
- $p_t^{(T)}$ = 教师模型在温度 $T$ 下的软标签
- $\alpha = 0.7$（教师信号权重）
- $T = 4$（蒸馏温度，软化教师分布以传递更多"暗知识"）
- $\mathcal{L}_{\text{CE}}$ = 标准交叉熵损失

温度 $T=4$ 是通过在验证集上搜索 $T \in \{2, 4, 8, 16\}$ 确定的。$T=4$
在意图分类准确率和过滤字段召回率之间取得最佳平衡。

### 归因感知多样性 (Attribution-Aware Diversity)

**MMR (Maximal Marginal Relevance)** 风格的重排序目标，带归因加分：

$$\text{score}_{\text{div}}(d_i) = \lambda \cdot \text{rel}(d_i) - (1-\lambda) \cdot \max_{d_j \in S} \text{sim}(d_i, d_j) + \alpha \cdot \text{attr\_bonus}(d_i)$$

其中：
- $\text{rel}(d_i)$ = L2 排序的相关性分数
- $S$ = 已选文档集合
- $\text{sim}(d_i, d_j)$ = 内容相似度
- $\text{attr\_bonus}(d_i)$ = 未充分代表来源（卖家、品类）的加分
- $\lambda$ = 相关性-多样性权衡参数
- $\alpha$ = 归因加分权重

### MLR 训练目标 (MLR Training Objective)

文档集上的 Pairwise Listwise 损失：

$$\mathcal{L}_{\text{MLR}} = -\sum_{q} \sum_{(d^+, d^-)} \log \sigma\bigl(s(q, d^+) - s(q, d^-)\bigr)$$

其中 $d^+$ 在真实标签中排名高于 $d^-$，$s(q, d)$ 是模型的评分函数。

### 意图分布漂移检测 (Intent Distribution Drift Detection)

使用 KL 散度监控线上意图分布与训练分布之间的差异：

$$D_{\text{KL}}(P_{\text{prod}} \| P_{\text{train}}) = \sum_{i} P_{\text{prod}}(c_i) \cdot \log \frac{P_{\text{prod}}(c_i)}{P_{\text{train}}(c_i)}$$

其中 $c_i$ 是意图类目。当 $D_{\text{KL}} > 0.1$ 时触发蒸馏数据刷新。
我们每小时在最近 100K 查询上计算此指标，使用 Laplace 平滑避免零概率问题。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

| 指标 | 数值 | 上下文 |
|------|------|--------|
| **LLM 推理延迟** | P50: 35ms, P99: 65ms | 微调 7B 模型运行在专用 GPU 集群 (A10) 上 |
| **LLM 吞吐量** | 集群约 8K 推理/秒 | 4 个 A10 GPU Pod，batch size 16 |
| **回退率** | 约 2% 的查询回退到纯 Cassini | LLM 超时 (80ms) 或置信度低于阈值 |
| **制品质量** | 92% 意图准确率（vs GPT-4 级别的 96%） | 每月用 1 万条人工标注查询验证 |
| **格式错误率** | 0.01%（使用 Outlines 约束解码） | 无约束解码时为 3.2% |
| **端到端搜索延迟** | P50: 120ms, P99: 200ms（含 LLM）；P50: 80ms（不含 LLM） | LLM 为搜索路径增加约 40ms，但可测量地提升相关性 |
| **离线学习周期** | 特征聚合：近实时；模型重训练：每日 | 距离校准每 4 小时更新 |
| **蒸馏周期** | 全量微调：每季度；LoRA 适配：每月 | 教师标签生成：500K 查询约 $15K API 成本 |
| **训练数据规模** | 每训练周期约 5000 万查询-制品-参与度三元组 | 2 周滑动窗口聚合 |
| **存储** | Unified Feature Table：约 2TB（2 周滑动窗口） | 按日期 + 查询分段分区 |

### 延迟预算分解 (Latency Budget Breakdown)

```
Total search P99: 200ms
  |- SaaS Orchestrator:    5ms
  |- Context Manager:     10ms
  |- Generator LLM:       65ms (P99)
  |- Field Validation:     2ms
  |- L1 Retrieval:        30ms
  |- Intent-Affinity Gate: 15ms
  |- L2 Neural Ranking:   50ms
  |- Diversity Scoring:   15ms
  |- Serialization:       10ms
```

### GPU 资源分配 (GPU Resource Allocation)

- **集群**：4 个 A10 GPU Pod（每个 24GB VRAM）
- **模型**：7B 参数，INT8 量化（约 7GB VRAM）
- **Batch size**：每批 16 个查询
- **扩缩容**：水平 Pod 自动扩缩，目标 GPU 利用率 70%
- **成本**：约 $8K/月（vs 大模型方案 8x A100 约 $50K/月）

### 延迟-准确率权衡实测数据 (Latency-Accuracy Trade-off Data)

| 模型 | 参数量 | 意图准确率 | P99 延迟 | GPU 成本/月 | 是否满足预算？ |
|------|--------|------------|----------|-------------|----------------|
| GPT-4 (API) | ~100B+ | 96.1% | 800ms | ~$120K | 否 |
| Llama-70B (自部署) | 70B | 95.3% | 320ms | $50K | 否 |
| Llama-13B (量化) | 13B | 93.7% | 110ms | $16K | 勉强 |
| **自研微调 7B** | **7B** | **92.0%** | **65ms** | **$8K** | **是** |
| Llama-3B (量化) | 3B | 86.4% | 28ms | $4K | 是，但准确率不足 |

7B 是**帕累托最优 (Pareto optimal)** 选择：准确率每降低 1%（从 96% 到 92%）
换来 12x 的延迟改善和 15x 的成本降低。低于 7B（如 3B）准确率急剧下降，
无法通过蒸馏弥补。
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

| 决策 | 方案 A | 方案 B | 我们的选择及原因 |
|------|--------|--------|------------------|
| **LLM 模型大小** | 大模型 (~100B) | 小型微调模型 (~7B) | **小模型**——需要 P99 < 65ms；微调后达到 92% 意图准确率 |
| **制品执行方式** | LLM 直接返回结果 | LLM -> 制品 -> Cassini 执行 | **代理模式**——消除幻觉，利用现有检索基础设施 |
| **校准频率** | 每日批量 | 近实时流式 | **混合策略**——特征流式处理，校准 4 小时批量 |
| **多样性策略** | 后置 **MMR (Maximal Marginal Relevance)** | 排序中融入归因感知 | **归因感知**——考虑来源溯源，而非仅内容相似度 |
| **回退策略** | 无制品（纯 Cassini） | 缓存相似查询的制品 | **分层策略**——(1) LLM, (2) 缓存, (3) 纯 Cassini。零停机保障 |
| **解码约束** | 后处理正则修复 | Token 级 schema 约束 | **Token 级约束 (Outlines)**——格式错误率从 3.2% 降至 0.01% |
| **蒸馏频率** | 实时在线蒸馏 | 离线周期性蒸馏 | **离线周期性**——全量每季度 + LoRA 每月；在线蒸馏引入训练-推理耦合风险 |

### 深入分析：模型大小权衡 (Deep Dive: Model Size Trade-off)

在大型基础模型和小型微调模型之间的选择是最具决定性的架构决策：

| 因素 | 大模型 (~100B) | 小型微调 (~7B) |
|------|----------------|----------------|
| 意图准确率 | ~96%（GPT-4 级别） | ~92% |
| 推理延迟 (P99) | 300-500ms | 65ms |
| GPU 成本 | 8x A100（$50K/月） | 4x A10（$8K/月） |
| 是否满足搜索延迟预算？ | 否（总预算 200ms） | 是 |
| 微调灵活性 | 有限（仅 API） | 完全掌控 |

4% 的准确率差距约损失 0.3% 的参与度，但延迟节省和成本降低使小模型在我们的
场景下具有明显优势。

### 深入分析：软门控 vs. 硬门控 (Deep Dive: Soft vs. Hard Gating)

我们选择了**软门控**（降权约 30%）而非硬门控（移除不匹配项）：

- **硬门控风险**：如果 LLM 的意图判断错误（8% 的查询），硬门控会移除所有
  相关结果。用户看到空白或不相关的页面。
- **软门控行为**：错误的意图会降低相关商品的权重但不移除它们。L2 神经排序器
  仍可通过相关性信号将它们浮现出来。
- **A/B 测试结果**：软门控在 8% 的错误查询上展现中性参与度（无损害），而硬门控
  在错误查询上参与度下降 12%（显著损害）。

### 迭代与评估：系统如何持续改进 (Iteration & Evaluation)

系统设计的一个关键部分是**如何验证和迭代**方案。这是中级和 Staff+ 级别
系统设计回答的分水岭。

#### 评估方法论 (Evaluation Methodology)

我们使用**四层评估**策略：

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **离线制品评估** | 教师-学生制品对比 | 每次蒸馏后 | 验证学生模型质量 |
| **离线排序评估** | 反事实评估 (IPS/DR) | 每日 | 模型/算法变更的快速迭代 |
| **交错测试** | Team-Draft Interleaving (TDI) | 天级 | 以高统计功效比较两个排序策略 |
| **A/B 测试** | 流量分割 (5% treatment) | 1-2 周 | 全量上线前的最终验证 |

**制品质量评估维度：**

| 维度 | 指标 | 目标 |
|------|------|------|
| 意图准确率 | 与人工标注的一致性 | >= 91% |
| 过滤字段精确率 | 生成的字段均在合法 schema 中 | >= 99% |
| 过滤字段召回率 | 人工标注的字段都被生成 | >= 85% |
| 查询改写相关性 | BERTScore 与教师改写对比 | >= 0.92 |

**反事实评估**使用**逆倾向得分 (IPS, Inverse Propensity Scoring)**：

$$\hat{V}(\pi_{\text{new}}) = \frac{1}{N} \sum_{i=1}^{N} \frac{\pi_{\text{new}}(a_i \mid x_i)}{\pi_{\text{old}}(a_i \mid x_i)} \cdot r_i$$

我们使用 **DR (Doubly Robust，双重稳健)** 估计器在倾向比较大时降低方差。

#### 关键超参数调优 (Key Hyperparameter Tuning)

| 参数 | 方法 | 结果 |
|------|------|------|
| LLM 置信度阈值 | 离线 precision-recall 曲线 | 0.7 最佳（precision 95% @ recall 88%） |
| 软门控衰减强度 | A/B 测试 | 30% 降权最优；20% 对错误查询保护不足，50% 过度惩罚正确查询 |
| 蒸馏温度 $T$ | 验证集 grid search | $T=4$ 最优（$T=2$ 标签太硬，$T=8$ 太平滑丢失判别力） |
| LoRA rank $r$ | 验证集扫描 $r \in \{8, 16, 32, 64\}$ | $r=16$ 最优（$r=8$ 欠拟合，$r=32$ 无额外收益但训练慢 50%） |
| 缓存 TTL（Tier 2） | 离线分析缓存命中与制品陈旧度 | 4 小时——命中率 72%，陈旧导致的 CTR 降幅 < 0.1% |

#### 典型失败模式与修复 (Failure Modes & Fixes)

1. **意图幻觉 (Intent Hallucination)**：LLM 生成训练集中不存在的意图类目
   （如将 "leather jacket" 标记为 "automotive accessories"）。**根因**：
   蒸馏数据中长尾类目样本不足。**修复**：在蒸馏数据采样中对低频类目 3x 过采样；
   添加意图验证门控（检查类目树合法性）。**效果**：幻觉意图从 2.1% 降至 0.3%。

2. **过滤字段漂移 (Filter Field Drift)**：Cassini schema 新增字段后，
   LLM 仍使用旧字段名。**根因**：蒸馏数据与生产 schema 版本不同步。
   **修复**：prompt 中注入当前 schema 版本号和有效字段列表（非硬编码于模型权重）；
   字段验证门控捕获并记录漂移事件。**效果**：字段验证失败率从 1.8% 降至 0.2%。

3. **级联回退风暴 (Cascading Fallback Storm)**：GPU 节点故障导致回退率
   飙升，缓存层因突发流量溢出，大量查询落到纯 Cassini。**根因**：回退层之间
   没有流量整形。**修复**：在 Tier 2 缓存前增加**令牌桶速率限制 (token bucket
   rate limiter)**，限制回退流量为正常 LLM 吞吐量的 150%。超出部分直接路由到
   Tier 3（纯 Cassini），避免缓存过载。**效果**：GPU 故障期间端到端延迟
   P99 从 800ms 降至 220ms。
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = r"""## 对抗性答辩问答 (Adversarial Defense Q&A)

**问：你们的 7B 模型只有 92% 的意图准确率。这意味着 8% 的查询会将错误制品输入 Cassini。这不是比不用 LLM 更差吗？**

> **承认局限：** 8% 的错误率是真实存在的。错误的意图过滤可能完全移除相关结果。
>
> **缓解措施：** Intent-Affinity Gating 是**软门控**，而非硬过滤。错误的意图不会移除结果——而是在 L2 评分中将不匹配的候选降权约 30%。排序仍然会考虑独立于制品的相关性信号。此外，我们有置信度阈值：如果 LLM 的意图置信度 < 0.7，则完全跳过门控，回退到纯 Cassini。
>
> **数据支撑：** 在 A/B 测试中，8% 的错误查询展现中性参与度（非负面），因为软门控保留了回退检索。92% 的正确查询 **CTR (Click-Through Rate)** 提升 6%，购买率提升 3%。净效果：整体参与度相比无 LLM 基线提升 5.2%。

---

**问：如何防止 LLM 成为搜索路径中的单点故障？**

> **承认局限：** 在关键搜索路径中添加任何组件都会创造新的故障模式。
>
> **缓解措施：** (1) 熔断器：如果 LLM 错误率在 1 分钟窗口内超过 5%，自动对所有查询绕过 LLM 直至恢复。(2) 异步预获取：对于输入中的查询，LLM 在用户输入第 3 个字符时即开始处理。(3) 回退方案（纯 Cassini）就是运行了多年的生产系统——它没有降级，只是未被增强。
>
> **数据支撑：** LLM 服务可用性：99.95%（2024 年度）。熔断器在 12 个月内触发 3 次，每次持续 < 5 分钟。熔断期间的用户影响：在参与度指标中不可检测。

---

**问：带符号学习的距离校准——sign 函数不是几乎处处梯度为零吗？**

> **承认局限：** sign 函数确实在零点不可微。
>
> **缓解措施：** 我们使用平滑近似：$\text{sign}(y) \approx \tanh(\beta \cdot y)$，其中 $\beta = 5$。这保持了梯度流，同时维持非对称惩罚行为。关键洞察是我们希望对过度过滤的惩罚**大于**不足过滤（漏掉相关结果比展示边界结果更严重）。
>
> **数据支撑：** 使用平滑 sign，校准在约 3 个 epoch 内收敛。使用硬 sign 则会振荡。平滑变体达到 94% 的校准相关性，而对称 **MSE (Mean Squared Error)** 损失仅 87%。

---

**问：蒸馏模型每季度更新一次，但查询分布可能每周都在变化。3 个月的刷新周期是否太慢？**

> **承认局限：** 是的，纯季度蒸馏确实会导致模型在刷新周期末尾出现能力退化，
> 尤其是在新品类上线或重大促销期间。
>
> **缓解措施：** 我们采用**双频率更新策略**：(1) 全量蒸馏（500K 样本，完整
> 微调）每季度执行，覆盖查询分布的结构性变化。(2) **LoRA (Low-Rank Adaptation)**
> 适配器每月更新，仅微调约 2% 的参数（rank 16），训练 6 小时即可完成。
> LoRA 使用最近 30 天的查询采样，聚焦于高漂移的意图类目。(3) 意图分布漂移
> 监控（KL 散度阈值 0.1）可在需要时触发**紧急中间蒸馏**。
>
> **数据支撑：** 引入月度 LoRA 后，季度末意图准确率从 89.5% 提升至 91.3%
> （相比季度初的 92.0%，退化从 2.5% 缩小到 0.7%）。紧急蒸馏在 12 个月内
> 触发 2 次（Black Friday 和新品类大规模上线），每次在 48 小时内恢复准确率。

---

**问：Schema-Constrained Decoding 限制了 LLM 的表达空间。如果最优制品需要的字段不在预定义 schema 中怎么办？**

> **承认局限：** 约束解码确实将 LLM 的输出空间限制在预定义 schema 内。如果
> Cassini 需要新的过滤维度（如"环保认证"、"本地发货"），LLM 无法自发发现这些
> 需求——它只能在已有字段中操作。
>
> **缓解措施：** (1) Schema 演进是**产品驱动的流程**，而非 LLM 自主决策。
> 新字段由产品/搜索团队提议，经过 Cassini 索引支持验证后添加到 schema。
> LLM 的 prompt 中 schema 版本动态注入，无需重新训练模型即可支持新字段。
> (2) 我们保留一个**自由文本字段 `extra_signals`**，允许 LLM 输出非结构化
> 的补充信息。Cassini 目前忽略此字段，但它为离线分析提供了 LLM "想说但 schema
> 不允许"的信号——这些信号用于指导 schema 演进方向。
>
> **数据支撑：** 分析 `extra_signals` 字段帮助我们在 6 个月内识别并添加了 4
> 个新的高价值过滤字段（品牌认证、配送速度、买家保障等级、商品状态）。每个
> 新字段上线后贡献了 0.3-0.8% 的增量 CTR 提升。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 口述大纲 (Verbal Outline)

### 3 分钟版本 (3-Minute Version)

1. **(30s) 问题：** 复杂多意图查询无法仅靠关键词匹配来服务。用户输入自然语言
   查询并期望语义理解，但传统搜索引擎只做词法匹配。

2. **(45s) 核心洞察——代理模式：** LLM 生成结构化制品（意图标签、过滤约束、
   查询改写），现有 Cassini 引擎执行检索。LLM 从不直接接触库存——它只塑造指令。
   这完全消除了幻觉风险。Schema-constrained decoding 确保 JSON 格式正确率
   99.99%。

3. **(60s) 架构：** 在线路径：LLM -> 制品 -> 字段验证 -> Cassini L1 检索 ->
   意图亲和门控（软门控，非硬门控）-> L2 神经排序 -> 多样性评分。离线路径：
   参与度日志 -> 距离校准（4 小时周期）-> **MLR (Machine Learned Ranking)**
   训练（每日）-> 模型更新。蒸馏管道：教师 (100B) -> 学生 (7B) 每季度全量 +
   每月 LoRA 适配。

4. **(30s) 生产实况：** 7B 微调模型，A10 GPU 上 P99 65ms。置信度阈值 0.7 的
   软门控。5% 错误率触发熔断器。分层回退：LLM -> 缓存制品 -> 纯 Cassini。

5. **(15s) 结果：** 净参与度提升 5.2%（含 8% 错误查询）。99.95% 可用性。
   零停机回退到 LLM 上线前的系统。

### 10 分钟版本 (10-Minute Version)

1. **(1.5 min) 问题空间：** 为什么关键词搜索在复杂查询上失败。为什么 LLM 无法
   直接执行检索：幻觉（编造不存在的商品）、延迟（大模型 300ms+）、时效性
   （缺乏实时库存感知）。理解与执行之间的鸿沟。

2. **(2 min) 代理模式架构：** LLM 生成制品，Cassini 执行。制品类型：意图/亲和
   摘要、代理过滤器、SrpAgentGist。Prompt 工程：结构化模板、schema 约束解码
   （Outlines，格式错误 3.2% -> 0.01%）、字段验证门控。蒸馏管道：教师 (100B)
   -> 学生 (7B)，全量每季度 + LoRA 每月。软门控 vs. 硬过滤——为什么软门控对
   错误容忍至关重要。

3. **(2 min) 离线学习：** 距离校准：使用带符号学习将代理模型与完整 LLM 对齐。
   平滑 sign 近似以保持梯度流。MLR 训练：5000 万三元组上的 Pairwise Listwise
   损失。4 小时校准周期 vs. 每日模型重训练。意图分布漂移检测（KL 散度监控）。

4. **(1.5 min) 生产约束：** 7B 模型选择：65ms 下 92% 准确率 vs. 300ms 下 96%。
   延迟预算分解（总计 200ms，LLM 占 65ms）。GPU 集群规模：4 个 A10，8K 推理/秒，
   $8K/月。帕累托最优分析：3B/7B/13B/70B/100B 的延迟-准确率-成本权衡。
   回退策略与熔断器机制。

5. **(2 min) 权衡与失败模式：** 模型大小 vs. 准确率（4% 差距分析）。软 vs.
   硬门控（错误查询的 A/B 测试结果）。校准频率（流式特征 + 批量校准）。
   归因感知多样性 vs. 后置 MMR。失败模式：意图幻觉（长尾类目过采样修复）、
   过滤字段漂移（动态 schema 注入修复）、级联回退风暴（令牌桶限流修复）。

6. **(1 min) 迭代与结果：** 四层评估：制品质量 -> 离线排序 -> 交错测试 ->
   A/B。正确查询参与度 +5.2%，购买率 +3%。99.95% 可用性。如果重新做：先从
   更小的制品集开始（仅意图），再添加过滤器和改写。更早建立意图分布监控。
"""


def populate_llm_orchestration() -> None:
    """Update the llm-orchestration record with all 8 expanded markdown sections."""
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

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_llm_orchestration()
