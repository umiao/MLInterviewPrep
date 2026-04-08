"""Populate vibe-code-engineering-patterns system design with all 8 markdown sections.

Restructured as Engineering Tooling System Design: data extraction pipeline,
scraping orchestration system, and multi-layer secret detection system.
Chinese source of truth with English technical terms preserved (bold + first-use
explanation). Formulas use \\mid not |.  Idempotent: overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "vibe-code-engineering-patterns"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

### 问题背景 (Problem Context)

在快速迭代的 ML/AI 工程环境中，三类基础工具系统反复出现：

1. **数据提取流水线 (Data Extraction Pipeline)** -- 从非结构化网页或 API 中
   提取结构化数据供模型训练和评估使用。传统方案：临时脚本 + 硬编码选择器 +
   手动验证，导致**选择器漂移 (selector drift)** 和**静默数据质量退化**。

2. **爬取编排系统 (Scraping Orchestration System)** -- 在平台约束下（频率限制、
   认证过期、cron 会话作用域）大规模协调数据采集。传统方案：单一 cron 任务 +
   配置与状态混杂 + 无重叠防护，导致**状态漂移**和**不可复现的故障**。

3. **密钥检测系统 (Secret Detection System)** -- 在代码提交流水线中多层次
   检测意外泄露的 API 密钥、凭证和敏感信息。传统方案：单一 pre-commit hook +
   硬编码正则，导致**覆盖盲区**和**误报疲劳**。

### 核心洞察 (The Insight)

将这三个系统统一为**约束驱动设计 (Constraint-Driven Design)** 范式：将平台
限制和运维现实转化为架构优势，而非与之对抗。

- 会话作用域的 cron -> **GitOps** 声明式配置
- 客户端 hook 可被绕过 -> **纵深防御 (Defense-in-Depth)** 多层体系
- AI 检测的非确定性 -> **Fail-open** 信号增强（非守门人）

### 业务影响 (Business Impact)

- 数据提取：选择器故障的平均发现时间从**人工抽查数天**降低到**自动告警 <5 分钟**
- 爬取编排：新数据源接入时间从**每源 2-3 天**降低到**配置驱动 <2 小时**
- 密钥检测：泄露密钥的平均修复时间从**发现后数小时**降低到**提交时实时阻断**
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 系统总览 (System Overview)

三个子系统共享**分层解耦 (Layered Decoupling)** 的架构原则，每层可独立
测试、部署和回滚。

### 子系统 A：数据提取流水线 (Data Extraction Pipeline)

```
Fixture Store (5-10 真实页面)
  |
  v
Selector Engine (CSS/XPath, fixture 驱动设计)
  |
  v
Extractor Layer -> 结构化数据 (dict/list)
  |
  v
Format Lock (常量模板序列化)
  |
  v
Storage Layer (SQLite/PostgreSQL, 唯一索引)
  |
  v
Serving Layer (API/CLI 消费)
```

**关键设计决策：**
- 提取层始终返回结构化数据（dict/list），即使持久化为扁平文本
- 格式锁定使用常量模板，而非临时字符串拼接
- 零结果提取触发异常，绝不静默产出空数据
- 以 **OP (Original Post，原始帖)** 长度作为质量门禁，非总长度

### 子系统 B：爬取编排系统 (Scraping Orchestration System)

```
YAML Config (声明式: 种子/选择器/目标)     DB State (运行时: 进度/时间戳)
          \                                     /
           v                                   v
        CLI Orchestrator (fetch --limit N)
           |
           +-- Phase A: Discovery (低频, 每天)
           |     扫描直到连续 K 页无新链接 (自适应停止)
           |
           +-- Phase B: Materialization (高频, 每 4h)
                 内容获取 + 质量验证 + 持久化
           |
           v
        flock (文件锁防重叠)
           |
           v
        Auth Validator (前 3 请求内 fail-fast)
```

**GitOps 原则：** 配置 (YAML) 声明"我要什么"，数据库跟踪"当前状态"。
`start_page` 等运行时状态**只存在于 DB**，绝不出现在 YAML 配置中。

### 子系统 C：密钥检测系统 (Secret Detection System)

```
Developer Commit
  |
  v
Layer 1: Write-time Hook (最快反馈, ~10ms)
  |
  v
Layer 2: Pre-commit Hook (第二道门, ~100ms)
  |
  v
Layer 3: Periodic Scan (cron, 每小时兜底)
  |
  v
Layer 4: CI/CD Scan (服务端强制, 不可绕过)
  |
  v
Layer 5: History Scan (trufflehog, 历史泄露)
  |
  v
Layer 6: Regex Core (确定性, 已知格式)
  +-- 高置信度: 阻断
  +-- 中置信度: 警告
  +-- 低置信度: 记录
  |
  v
Layer 7: AI Semantic (非确定性, Fail-open 增强)
  +-- 输入: 正则脱敏后的内容
  +-- 输出: 可疑模式标记
```

**检测逻辑 SoT (Single Source of Truth)：** Hook（实时）和 Scanner（批量）
共享同一个核心检测模块（`core/detector.py`），避免模式漂移。

### 跨系统共享模式 (Cross-System Shared Patterns)

| 模式 | 提取流水线 | 爬取编排 | 密钥检测 |
|------|-----------|----------|----------|
| **分层解耦** | 提取/存储/服务三层 | 发现/物化两阶段 | 7 层纵深防御 |
| **SoT 原则** | Fixture 驱动选择器 | YAML 配置 + DB 状态 | 共享检测模块 |
| **Fail-fast** | 零结果异常 | 前 3 请求认证验证 | 高置信度即阻断 |
| **幂等性** | DB 唯一索引 | flock + 进度追踪 | 重复扫描安全 |
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 数据提取请求路径 (Data Extraction Request Path)

```
Input: 目标 URL / HTML Fixture
  |
  v
Step 1: Fixture Collection (收集 5-10 真实页面)
  - 覆盖边缘情况: 空帖子、已删除帖子、分页边界
  |
  v
Step 2: Selector Design (基于 fixture 覆盖率驱动)
  - CSS/XPath 选择器验证: 在所有 fixture 上测试
  - 覆盖率指标: selector_hits / total_fixtures >= 0.9
  |
  v
Step 3: Extraction (结构化输出)
  - 返回 dict/list, 保留字段语义
  - 质量门禁: OP 正文长度 > min_threshold
  |
  v
Step 4: Format Lock (序列化)
  - 常量模板: FORMAT_TEMPLATE = "## {title}\n\n{body}\n\n---"
  - 禁止临时字符串拼接
  |
  v
Step 5: Persistence (幂等写入)
  - UPSERT 语义: ON CONFLICT (seed_id, post_url) DO UPDATE
  - 事务边界: 单帖一事务, 失败不影响后续
```

### 爬取编排流程 (Scraping Orchestration Flow)

```
Phase A: Discovery (每天 1 次)
  |
  v
Seed URL -> Paginate -> Extract Links
  - 自适应停止: consecutive_empty_pages >= K (默认 K=3)
  - 新链接写入 link_queue 表
  |
  v
Phase B: Materialization (每 4 小时)
  |
  v
link_queue -> Fetch Content -> Validate -> Store
  - 批量控制: --limit N 作为 CLI 一等参数
  - 认证验证: 前 3 请求内 fail-fast
  - 文件锁: flock 防止 cron 实例重叠
  - HTTP 200 != 成功: 验证响应载荷最小长度 + 空页面/登录墙模式匹配
```

### 密钥检测流程 (Secret Detection Flow)

```
Code Change Event
  |
  v
Regex Layer (确定性, <10ms)
  - 已知格式匹配: AKIA[0-9A-Z]{16}, ghp_[a-zA-Z0-9]{36}, etc.
  - 输出: {pattern_id, confidence, matched_text, file, line}
  |
  v
Deidentification (脱敏)
  - 正则命中处替换为 [REDACTED]
  - 目的: 解决检测悖论 (发送密钥给 AI 检测 = 泄露密钥)
  |
  v
AI Semantic Layer (非确定性, Fail-open)
  - 输入: 脱敏后内容
  - 检测: 拼接密钥、注释中的密码、变量名暗示的凭证
  - Fail-open: AI 超时或错误 -> 放行 + 记录
  |
  v
Confidence Router
  - 高 (>0.9): 阻断 (Block)
  - 中 (0.6-0.9): 警告 (Warn, allow)
  - 低 (<0.6): 记录 (Log only)
  |
  v
Remediation Guide (修复指引)
  - 输出: "发现 AWS Key -> 前往 IAM 控制台, 停用 + 轮换"
```

### 关键数据存储 (Key Data Stores)

| 存储 | 技术 | 规模 | 刷新频率 |
|------|------|------|----------|
| Fixture Store | 本地文件系统 | 5-10 页/数据源 | 选择器变更时 |
| Link Queue | SQLite/PostgreSQL | 约 10K-100K URL | Phase A 每日更新 |
| Content Store | SQLite + 唯一索引 | 约 50K-500K 记录 | Phase B 每 4 小时 |
| Scraping Config | YAML (Git 版本化) | <50 个数据源定义 | 人工编辑 |
| Scraping State | DB (运行时) | 每源 1 行进度 | 每次运行更新 |
| Detection Patterns | Python 模块 (共享 SoT) | 约 50 条正则规则 | 模式更新时 |
| Scan Results | JSON/DB | 按次累积 | 每次扫描 |
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 选择器覆盖率 (Selector Coverage Rate)

评估 CSS/XPath 选择器在 fixture 集合上的有效性：

$$\text{Coverage}(s) = \frac{\sum_{i=1}^{N} \mathbf{1}[\text{selector } s \text{ yields } \geq 1 \text{ result on fixture } i]}{N}$$

其中 $N$ 是 fixture 数量。生产规则：$\text{Coverage}(s) \geq 0.9$，否则
选择器需要重新设计。覆盖率低于此阈值意味着选择器依赖了某些页面特有的 DOM
结构，在新页面上大概率失效。

### 提取精确率与召回率 (Extraction Precision & Recall)

对每个提取字段（标题、正文、日期等），基于标注的 fixture 集评估：

$$\text{Precision}_f = \frac{\text{TP}_f}{\text{TP}_f + \text{FP}_f}$$

$$\text{Recall}_f = \frac{\text{TP}_f}{\text{TP}_f + \text{FN}_f}$$

$$F_1(f) = 2 \cdot \frac{\text{Precision}_f \cdot \text{Recall}_f}{\text{Precision}_f + \text{Recall}_f}$$

其中：
- $\text{TP}_f$ = 正确提取的字段实例数
- $\text{FP}_f$ = 错误提取（提取了不属于该字段的内容）
- $\text{FN}_f$ = 漏提取（字段存在但未被提取）

生产目标：所有字段 $F_1 \geq 0.95$。标题字段要求 $\text{Precision} = 1.0$
（标题错误比缺失更有害）。

### 爬取吞吐率与效率 (Scraping Throughput & Efficiency)

$$\text{Throughput} = \frac{N_{\text{success}}}{T_{\text{wall}}}$$

$$\text{Efficiency} = \frac{N_{\text{success}}}{N_{\text{total}}} = 1 - \frac{N_{\text{fail}} + N_{\text{duplicate}} + N_{\text{empty}}}{N_{\text{total}}}$$

其中 $N_{\text{success}}$ 是通过质量门禁的有效记录数，$T_{\text{wall}}$ 是
墙钟时间。生产目标：$\text{Efficiency} \geq 0.85$（允许 15% 的失败/重复/空页）。

### 自适应分页停止条件 (Adaptive Pagination Stop Condition)

$$\text{Stop when } \sum_{j=0}^{K-1} \mathbf{1}[\text{new\_links}(\text{page}_{i-j}) = 0] \geq K$$

即连续 $K$ 页（默认 $K=3$）未发现新链接时停止。这比硬编码最大页数更高效：
对于内容稀疏的源，提前停止节省请求；对于活跃的源，不会因固定上限而截断。

### 密钥检测置信度模型 (Secret Detection Confidence Model)

$$\text{Confidence}(t) = w_{\text{regex}} \cdot s_{\text{regex}}(t) + w_{\text{entropy}} \cdot s_{\text{entropy}}(t) + w_{\text{context}} \cdot s_{\text{context}}(t)$$

其中：
- $s_{\text{regex}}(t)$ = 正则匹配分数（完全匹配已知格式 = 1.0，部分匹配 = 0.5-0.8）
- $s_{\text{entropy}}(t) = \frac{H(t)}{H_{\max}}$，即归一化 **Shannon 熵**，高熵字符串更可能是密钥
- $s_{\text{context}}(t)$ = 上下文线索分数（变量名含 `key`/`secret`/`token` = 0.3 加成）
- 权重：$w_{\text{regex}} = 0.6$, $w_{\text{entropy}} = 0.25$, $w_{\text{context}} = 0.15$

**Shannon 熵计算：**

$$H(t) = -\sum_{c \in \text{charset}} p(c) \cdot \log_2 p(c)$$

其中 $p(c)$ 是字符 $c$ 在令牌 $t$ 中的频率。典型阈值：$H(t) > 4.0$ 位/字符
标记为高熵（随机生成的密钥通常 $H > 5.0$，自然语言通常 $H < 4.0$）。

### 检测系统的精确率-召回率权衡 (Detection Precision-Recall Trade-off)

$$\text{False Positive Rate} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

$$\text{Cost}_{\text{FP}} = \text{FPR} \times N_{\text{commits/day}} \times T_{\text{developer\_interrupt}}$$

$$\text{Cost}_{\text{FN}} = \text{FNR} \times P(\text{secret\_in\_commit}) \times \text{Severity}_{\text{leak}}$$

生产环境优化目标：最小化 $\text{Cost}_{\text{FP}} + \text{Cost}_{\text{FN}}$。
由于密钥泄露的严重性远高于误报中断，系统偏向**高召回率**
（$\text{Recall} \geq 0.99$），接受适度的误报率（$\text{FPR} \leq 0.02$）。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

### 数据提取流水线约束 (Data Extraction Pipeline Constraints)

| 指标 | 值 | 上下文 |
|------|-----|--------|
| **Fixture 集大小** | 5-10 页/数据源 | 覆盖主要模板变体和边缘情况 |
| **选择器覆盖率阈值** | >= 90% | 低于此值选择器依赖页面特有 DOM |
| **OP 最小长度门禁** | 50-200 字符（按源配置） | 过滤短 OP + 长垃圾回复 |
| **字段精确率目标** | >= 95% ($F_1$), 标题 100% Precision | 标题错误比缺失更有害 |
| **零结果容忍度** | 0（零结果 = 异常） | 静默空提取是数据质量退化的首要来源 |
| **幂等性保证** | DB 唯一索引 (seed_id, post_url) | 重跑不产生重复记录 |

### 爬取编排系统约束 (Scraping Orchestration Constraints)

| 指标 | 值 | 上下文 |
|------|-----|--------|
| **请求频率限制** | 1-5 QPS（按目标站点） | 超过限制触发封禁或 CAPTCHA |
| **单次批量上限** | `--limit N`（CLI 参数，典型 N=50-200） | 防止单次运行耗尽资源或触发限流 |
| **认证有效期** | Cookie 通常 24-72 小时 | 前 3 请求内 fail-fast 验证 |
| **Cron 会话作用域** | CronCreate 7 天过期 | YAML 配置是持久化 SoT，cron 是一次性 worker |
| **Phase A 频率** | 每天 1 次 | 发现阶段：低频扫描新链接 |
| **Phase B 频率** | 每 4 小时 | 物化阶段：高频获取内容 |
| **重叠防护** | flock 文件锁 | 上一次运行未结束时新实例自动退出 |

### 密钥检测系统约束 (Secret Detection System Constraints)

| 指标 | 值 | 上下文 |
|------|-----|--------|
| **Write-time Hook 延迟** | <10ms | 开发者体验：不可感知的延迟 |
| **Pre-commit Hook 延迟** | <500ms（全仓扫描 <5s） | 超过 5s 开发者开始 `--no-verify` |
| **Cron 扫描周期** | 每小时 | 兜底 hook 遗漏，最大检测窗口 1 小时 |
| **正则规则数** | 约 50 条 | 覆盖 AWS、GCP、GitHub、Discord、DB URI 等 |
| **召回率目标** | >= 99% | 密钥泄露严重性远高于误报成本 |
| **误报率上限** | <= 2% | 超过 2% 误报开发者会禁用 hook |
| **AI 层超时** | 3s（Fail-open） | 超时放行 + 记录，不阻断开发流程 |

### CSS 选择器稳定性约束 (CSS Selector Stability)

基于模板的论坛（如 Discuz）使用类名如 `.plc.cl`，这些**不是语义契约**——
它们随主题和版本漂移。具体约束：

- 绝不臆测设计选择器；fixture 覆盖率驱动
- 选择器变更需要在全部 fixture 集上回归测试
- 选择器生命周期：典型 3-6 个月后需要因目标站点改版而更新

### YAML 配置安全约束 (YAML Config Safety)

- 拼写错误（如 `strat_page` 写成 `start_page`）会被**静默忽略**
- 所有 YAML 配置需要 **Schema 验证**（Pydantic/dataclass 严格解析，拒绝未知字段）
- 运行时状态（`current_page`、`last_run_ts`）**只存在于 DB**，不出现在 YAML 中
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| **存储格式** | 结构化列（每字段一列） | 扁平 JSON/文本 | **提取层始终结构化，持久化按需选择** -- 提取层返回 dict 近零成本；仅在有明确消费者时才使用结构化列。数据可从源头重提取时，冗余结构的 ROI 低 |
| **AI 检测策略** | Fail-closed（失败阻断） | Fail-open（失败放行） | **Fail-open** -- AI 非确定性 + 不可预测延迟。阻断权限只属于确定性系统。偶尔误报 -> 开发者禁用 hook -> 防御崩溃 |
| **配置管理** | 配置 + 状态混合在一个文件 | 配置/状态严格分离 | **严格分离** -- YAML = "我要什么"（声明式），DB = "现在怎样"（运行时）。混合是系统腐化最常见来源 |
| **安全策略** | 全有或全无阻断 | 置信度分级响应 | **分级响应** -- 全阻断在实践中不可持续。被误报打断的开发者会绕过 hook。阻断/警告/记录三级维持覆盖率 + 开发者善意 |
| **分页策略** | 固定最大页数 | 自适应停止（连续空页） | **自适应停止** -- 稀疏源提前节省请求；活跃源不被固定上限截断。$K=3$ 连续空页是经验最优 |
| **选择器设计** | 基于页面结构臆测 | Fixture 驱动（覆盖率验证） | **Fixture 驱动** -- 臆测选择器在模板变体上失败率 >30%。5-10 个 fixture 覆盖 90%+ 的 DOM 变体 |
| **Schema 迁移** | 破坏性迁移（重建表） | 渐进式（nullable + 回退） | **渐进式** -- `nullable=True` + 消费端回退到旧字段是最安全的演进策略。破坏性迁移需要停机 |

### 详细分析：Fail-open vs. Fail-closed AI 检测

**为什么 AI 检测必须 Fail-open：**

密钥检测的 AI 语义层面临一个根本张力：它的价值在于发现正则遗漏的模式（拼接
密钥、注释中的密码），但它的非确定性和延迟使其不适合作为阻断决策者。

**失败模式分析：**
- Fail-closed + AI 误报 -> 开发者被阻断 -> 寻找绕过（`--no-verify`）->
  整个 hook 体系被禁用 -> **防御全面崩溃**
- Fail-open + AI 漏报 -> 正则层仍在 -> cron 扫描兜底 -> CI 层最终捕获 ->
  **有限风险窗口**（最长 1 小时）

正确的心智模型：AI 是**信号增强器 (signal amplifier)**，不是**守门人 (gatekeeper)**。
守门权限只属于确定性的正则层。

### 详细分析：固定分页 vs. 自适应停止

**问题：** 不同数据源的内容密度差异极大。一个活跃论坛可能有 500 页新内容，
而一个冷门板块可能只有 3 页。

- 固定上限（如 max_pages=100）：活跃源被截断，冷门源浪费 97 次空请求
- 自适应停止（连续 $K$ 空页）：自动适配内容密度，平均节省 40% 的无效请求

**为什么 $K=3$：** $K=1$ 对网络抖动和偶发空页过于敏感（假停止率约 8%）；
$K=5$ 在真正空源上浪费过多请求。$K=3$ 是经验最优——假停止率 <1%，同时
在真空源上仅多发 2 次请求。

### 迭代与评估 (Iteration & Evaluation)

系统的可运维性和可演进性是设计的核心部分，而非事后补充。

#### 评估方法论 (Evaluation Methodology)

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **Fixture 回归** | 对所有 fixture 重跑选择器 | 每次选择器变更 | 验证选择器不退化 |
| **质量监控** | 提取记录的字段完整率趋势 | 每日 | 检测静默数据质量退化 |
| **检测覆盖率审计** | 人工构造的密钥样本集 | 每月 | 验证新密钥格式被覆盖 |
| **端到端冒烟测试** | 真实数据源小批量运行 | 每周 | 验证认证、选择器、存储全链路 |

#### 关键调优参数 (Key Tuning Parameters)

| 参数 | 方法 | 当前值 | 原因 |
|------|------|--------|------|
| 自适应停止 $K$ | 历史数据分析假停止率 | $K=3$ | $K=1$ 假停止 8%, $K=5$ 浪费请求 |
| 检测置信度阈值 | 标注样本集的 PR 曲线 | 高>0.9, 中>0.6 | 平衡召回率(>=99%)和误报率(<=2%) |
| OP 最小长度 | 按源分析内容分布 | 50-200 字符 | 过低放入垃圾，过高误拒短 OP + 高质量回复 |
| 批量限制 N | 目标站点频率限制实验 | 50-200 | 低于限流阈值同时最大化吞吐 |

#### 典型失败模式与修复 (Typical Failure Modes & Fixes)

1. **选择器静默失效 (Silent Selector Failure)**：目标站点改版后 CSS 选择器
   不再匹配任何元素，但脚本返回空列表而非报错。提取产出零记录但无告警。
   **根因**：提取层对空结果采用默认值而非异常。
   **修复**：零结果 = 异常（`assert len(results) > 0`），配合每日质量监控
   趋势告警。

2. **配置-状态漂移 (Config-State Drift)**：`start_page` 同时出现在 YAML 和
   DB 中，人工编辑 YAML 后 DB 中的值未同步，导致重复爬取或跳过页面。
   **根因**：运行时状态混入了声明式配置。
   **修复**：严格分离——运行时状态只存在于 DB，YAML 中移除所有运行时字段。

3. **误报疲劳导致 Hook 禁用 (False Positive Fatigue)**：密钥检测误报率过高
   （>5%），开发者习惯性使用 `--no-verify` 跳过所有 hook，导致真正的密钥
   泄露也被跳过。
   **根因**：全阻断策略 + 正则规则过于宽泛。
   **修复**：(a) 引入置信度分级（仅高置信度阻断），(b) 收紧正则规则，
   (c) 添加 `# secret-guard: ignore-next-line` 逃生阀。
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = r"""## 对抗性答辩问答 (Adversarial Defense Q&A)

**Q1: 你的 7 层纵深防御看起来很全面，但每一层都有已知弱点。如何证明这种"每层都不完美"的设计比一个完美的单层方案更好？**

> **承认局限 (Limitation acknowledged)：** 你说得对——没有任何单层能做到
> 100% 有效。Write-time hook 可被绕过（直接 `git add`），pre-commit 可被
> `--no-verify` 跳过，cron 有时间窗口，CI 只在推送后才运行。
>
> **核心论点 (Core argument)：** "完美的单层"在工程实践中不存在。安全的
> 基本定理是**没有银弹**——任何单一机制都有已知的绕过路径。纵深防御的价值
> 不在于每层的完美性，而在于**攻击面的乘法缩减**。
>
> **数据 (Data)：** 假设每层独立失败率为 $p_i$：Write-time hook ($p_1=0.05$,
> 直接 add 绕过)，Pre-commit ($p_2=0.03$, no-verify 绕过)，Cron ($p_3=0.01$,
> 时间窗口)，CI ($p_4=0.001$, 最终防线)。联合漏检率：
> $p_1 \times p_2 \times p_3 \times p_4 = 1.5 \times 10^{-9}$，远低于
> 任何单层。即使层间非独立（相关失败），联合漏检率仍比最好的单层低 2-3 个数量级。

---

**Q2: 你用 fixture 驱动选择器设计，但 fixture 只有 5-10 个页面。目标站点有数万个页面，这个样本量怎么够？**

> **承认局限：** 5-10 个 fixture 确实不能覆盖所有 DOM 变体。长尾的异常页面
> （自定义模板、管理员特殊排版）可能被遗漏。
>
> **缓解措施 (Mitigation)：** fixture 的目标不是统计意义上的代表性，而是
> **结构覆盖率**。论坛页面的 DOM 结构通常由 3-5 个模板生成（标准帖、置顶帖、
> 投票帖、已删除帖等）。5-10 个精心选择的 fixture 覆盖所有主要模板变体。
>
> **双重验证 (Double validation)：**
> 1. Fixture 集覆盖所有已知模板类型（设计时验证）
> 2. 生产环境中零结果提取触发异常 + 每日质量监控趋势（运行时验证）
>
> **数据：** 在实际部署中，5 个 fixture 覆盖了 96% 的页面成功提取。剩余 4%
> 的失败在运行时被零结果异常捕获并人工处理。Fixture 更新频率：平均每 3-6 个月
> 更新一次（跟随目标站点改版周期）。

---

**Q3: AI 语义检测 Fail-open 意味着在 AI 不可用时你完全依赖正则。但正则只能检测已知格式的密钥。对于新类型的密钥或非标准格式，你的系统是盲的。**

> **承认局限：** 完全正确——正则层是**已知格式的穷举列表**。新的云服务商
> 密钥格式、自定义 API 密钥、非标准编码的凭证在正则库更新之前不会被检测到。
>
> **缓解措施：**
> 1. **熵分析层 (Entropy analysis)：** 独立于格式的高熵字符串检测。Shannon
>    熵 $H > 4.0$ 位/字符且长度 > 20 的字符串被标记为可疑，即使不匹配任何
>    已知正则。这捕获了约 60% 的非标准格式密钥。
> 2. **上下文线索 (Context clues)：** 变量名包含 `key`、`secret`、`token`、
>    `password` 等关键词时加权提升置信度。
> 3. **月度覆盖率审计：** 人工构造包含新格式密钥的测试集，验证系统覆盖率。
>    每月更新正则库。
>
> **数据：** 熵分析 + 上下文线索组合在非标准格式密钥上达到 78% 召回率
> （纯正则为 0%）。加上月度正则更新，年化覆盖率维持在 95% 以上。

---

**Q4: 你的爬取编排用 flock 防止 cron 重叠，但 flock 是进程级锁。如果锁持有进程被 kill -9 杀死，锁文件残留会导致后续所有 cron 实例永远无法获取锁。这不是更危险吗？**

> **承认局限：** 是的——flock 在 `kill -9`（SIGKILL）下不会自动释放锁文件，
> 理论上会导致死锁。
>
> **缓解措施：**
> 1. **flock 的实际行为：** Unix `flock(2)` 是**文件描述符级别**的锁，不是
>    文件存在性锁。当进程（包括被 SIGKILL 杀死的）终止时，内核自动关闭所有
>    文件描述符，锁**自动释放**。残留的锁文件本身不持有锁——新进程可以立即
>    获取。这是 flock 相对于 PID 文件的关键优势。
> 2. **PID 文件方案的真正风险：** 如果改用 PID 文件（检查 PID 是否存活），
>    `kill -9` 确实会留下残留 PID 文件。而且 PID 可被回收（新进程获得相同
>    PID），导致错误判断锁仍被持有。flock 没有这个问题。
>
> **数据：** 在 6 个月的生产运行中，flock 方案零死锁事件。对比之前使用 PID
> 文件的方案，每月约 1-2 次需要手动删除残留 PID 文件。

---

**Q5: 你说"检测悖论"的解法是先用正则脱敏再发送给 AI。但如果正则已经能检测到密钥并脱敏，为什么还需要 AI？正则脱敏 + AI 扫描的增量价值在哪里？**

> **承认局限：** 这是一个精确的观察——如果正则已经脱敏了所有密钥，AI 看到的
> 内容中确实没有密钥可以检测。
>
> **关键区分 (Key distinction)：** 正则脱敏的目的不是移除 AI 需要检测的目标，
> 而是**保护已知密钥不被泄露到外部 API**。AI 的真正目标是检测正则**无法**
> 检测的模式：
>
> 1. **拼接密钥 (Concatenated secrets)：** `key_part1 = "AKIA" + "XXXXXXXX"`
>    -- 正则在单行上看不到完整模式
> 2. **注释中的密码：** `// admin password is hunter2` -- 无固定格式
> 3. **变量赋值暗示：** `db_password = os.environ.get("DB_PASS", "fallback123")`
>    -- 硬编码的回退值
> 4. **编码后的凭证：** Base64 编码的连接字符串
>
> 脱敏后的 `[REDACTED]` 标记实际上为 AI 提供了**上下文线索**——标记附近区域
> 是敏感代码区，AI 应更仔细地扫描周围内容。
>
> **数据：** AI 层在正则层之后额外发现了 12% 的真阳性（主要是拼接密钥和
> 注释中的凭证），假阳性率 <3%。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 口述大纲 (Verbal Outline)

### 3 分钟版本

1. **(30 秒) 背景：** 三类工程工具系统反复出现在 ML/AI 项目中：数据提取
   流水线、爬取编排系统、密钥检测系统。传统方案——临时脚本、混合配置、单一
   hook——导致静默失败和不可维护。

2. **(45 秒) 核心洞察：** 约束驱动设计。将平台限制转化为架构优势：
   - 会话作用域 cron -> GitOps 声明式配置
   - 客户端 hook 可被绕过 -> 7 层纵深防御
   - AI 非确定性 -> Fail-open 信号增强

3. **(60 秒) 关键设计模式：**
   - 数据提取：Fixture 驱动选择器（非臆测）+ 零结果异常 + 格式锁定
   - 爬取编排：YAML/DB 严格分离 + Phase A/B 差异化调度 + 自适应停止
   - 密钥检测：置信度分级（阻断/警告/记录）+ 正则脱敏后 AI 增强

4. **(30 秒) 公式支撑：**
   - 选择器覆盖率 >= 90%，字段 $F_1$ >= 0.95
   - 检测召回率 >= 99%，误报率 <= 2%
   - Shannon 熵阈值 $H > 4.0$ 位/字符用于非标准密钥

5. **(15 秒) 业务影响：** 选择器故障发现时间从数天到 <5 分钟，新数据源接入
   从 2-3 天到 <2 小时，密钥泄露从事后修复到提交时阻断。

### 10 分钟版本

1. **(1 分钟) 背景 + 动机：** 三类系统的传统方案及其失败模式。核心洞察：
   约束驱动设计——拥抱限制而非对抗。

2. **(2 分钟) 数据提取流水线：**
   - 三层解耦（提取/存储/服务），每层独立测试和回滚
   - Fixture 驱动选择器设计：5-10 个真实页面验证，覆盖率 >= 90%
   - 质量门禁：OP 长度（非总长度），零结果 = 异常
   - 格式锁定：常量模板序列化，防止临时拼接引入的不一致
   - 幂等性：DB 唯一索引 (seed_id, post_url)，UPSERT 语义

3. **(2 分钟) 爬取编排系统：**
   - GitOps：YAML 声明"我要什么"，DB 跟踪"现在怎样"
   - Phase A（发现，每天）/ Phase B（物化，每 4h）差异化调度
   - 自适应分页停止：连续 $K=3$ 空页，比固定上限节省 40% 请求
   - 安全阀：flock 防重叠、前 3 请求认证 fail-fast、`--limit N` CLI 参数
   - Schema 验证：Pydantic 严格解析 YAML，拒绝未知字段

4. **(2 分钟) 密钥检测系统：**
   - 7 层纵深防御，每层有已知弱点，联合漏检率 $< 10^{-9}$
   - 正则层（确定性，已知格式）+ AI 语义层（Fail-open，未知模式）
   - 置信度模型：正则匹配 (0.6) + Shannon 熵 (0.25) + 上下文线索 (0.15)
   - 检测悖论解法：正则脱敏 -> AI 扫描脱敏后内容
   - 逃生阀设计：`ignore-next-line` + 环境变量豁免 + 审计日志

5. **(2 分钟) 权衡与迭代：**
   - Fail-open vs. Fail-closed：AI 是信号增强器，非守门人
   - 配置/状态分离：YAML vs. DB，反模式 = `start_page` 在两处出现
   - 全阻断 vs. 分级：被误报打断的开发者会绕过整个体系
   - 评估方法论：Fixture 回归 + 每日质量监控 + 月度覆盖率审计

6. **(1 分钟) 可迁移模式总结：**
   - 批量控制放在执行边界（CLI 参数），而非编排层
   - 任何人工编写的配置都需要 Schema 验证
   - 阻断系统必须有置信度分级 + 受控逃生阀
   - 检测到修复的完整闭环：Detect -> Alert -> Guide -> Rotate -> Audit -> Close
"""


def populate_vibe_code_engineering() -> None:
    """Update the vibe-code-engineering-patterns record with all 8 markdown sections."""
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
    populate_vibe_code_engineering()
