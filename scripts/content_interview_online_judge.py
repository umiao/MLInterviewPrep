"""Populate interview-online-judge system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design an Online Judge
(LeetCode) -- code sandbox execution (Docker/gVisor), queue-based submission
pipeline, test case runner, judge verdicts, anti-cheat (MOSS plagiarism),
multi-language runtime support, and scaling to millions of submissions.
Idempotent: creates record if missing, overwrites existing.

Chinese translation with English technical terms preserved (bold + first-use
explanation). Formulas and code blocks kept as-is.
"""
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "interview-online-judge"
TITLE = "Design an Online Judge (LeetCode)"
DISPLAY_ORDER = 115

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**在线判题系统 (Online Judge, OJ)**，类似 LeetCode / Codeforces /
HackerRank。用户可以在浏览器中编写代码、提交解答，系统在安全沙箱中编译并
执行用户代码，对比预期输出给出判定结果 (Accepted, Wrong Answer,
Time Limit Exceeded 等)，同时支持竞赛排行榜和题目管理。

核心挑战在于：(1) 在多租户环境下安全执行不可信代码，(2) 保证判题结果的正确性
和一致性，(3) 在高并发竞赛场景下 (数千人同时提交) 保持低延迟判题，
(4) 支持多编程语言运行时的隔离与资源限制。

### 功能性需求 (Functional Requirements)

1. **题目管理 (Problem Management)**: 管理员创建/编辑题目，包含题目描述、
   输入输出格式、示例、隐藏测试用例、时间/空间限制
2. **代码提交与判题 (Code Submission & Judging)**: 用户提交代码后，系统
   编译、执行、对比输出，返回判定结果 (AC/WA/TLE/MLE/RE/CE)
3. **多语言支持 (Multi-Language)**: 至少支持 C++, Java, Python, Go, JavaScript
   等主流语言，每种语言有独立的编译器版本和资源限制
4. **实时反馈 (Real-Time Feedback)**: 用户提交后可实时看到判题进度
   (编译中 -> 运行测试用例 1/10 -> 运行测试用例 2/10 -> ...)
5. **竞赛模式 (Contest Mode)**: 支持限时竞赛，实时排行榜
   (按 **ACM-ICPC** 规则或 **Rating** 规则排名)
6. **代码运行 (Code Playground)**: 用户可以在提交前运行代码测试自定义输入
7. **提交历史 (Submission History)**: 查看历史提交记录、通过率统计

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.9% -- 竞赛期间要求更高 (99.95%)，
  判题队列可容忍短暂延迟但不能丢失提交
- **延迟 (Latency)**: 普通提交判题延迟 P99 < 30s (含编译+运行所有测试用例);
  竞赛高峰 P99 < 60s; 代码运行 (Playground) P99 < 10s
- **一致性 (Consistency)**: 判题结果必须强一致 -- 同一份代码对同一题目的
  多次提交必须得到相同判定; 排行榜可最终一致 (3-5s 延迟可接受)
- **可扩展性 (Scalability)**: 支持 500 万注册用户，每日 100 万次提交，
  竞赛高峰 5000 并发提交/分钟
- **安全性 (Security)**: 用户代码在完全隔离的沙箱中运行，无法访问网络、
  文件系统 (除指定 I/O)、其他进程; 防止 fork bomb、OOM、无限循环

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 是否需要支持 Special Judge (自定义评判器)?**
   -- WHY: 某些题目 (如浮点数输出、多解题) 需要自定义比较逻辑而非精确匹配，
   这影响判题引擎的可扩展性设计

2. **Q: 竞赛规模有多大? 是否需要支持万人同时在线竞赛?**
   -- WHY: 万人竞赛意味着每秒数百次提交突发，需要弹性伸缩的判题集群;
   百人竞赛用固定集群即可

3. **Q: 是否需要支持交互式题目 (Interactive Problem)?**
   -- WHY: 交互式题目需要用户程序和评判程序通过 stdin/stdout 实时通信，
   判题架构从"运行-比较"变成"运行-交互-判定"，复杂度显著增加

4. **Q: 测试用例数据量有多大? 是否有大数据量测试用例 (>100MB)?**
   -- WHY: 大测试用例影响存储策略 (文件系统 vs 对象存储) 和判题 Worker
   的 I/O 设计 (流式读取 vs 全量加载)

5. **Q: 是否需要抄袭检测 (Plagiarism Detection)?**
   -- WHY: 竞赛场景下抄袭检测 (如 **MOSS (Measure of Software Similarity)**)
   是关键功能，需要额外的代码相似度分析管道

6. **Q: 用户代码的运行环境是否需要支持 GPU (如机器学习题目)?**
   -- WHY: GPU 支持需要 NVIDIA Container Runtime，资源调度和成本管理
   与 CPU-only 场景完全不同

7. **Q: 是否需要支持用户自定义测试用例 (Custom Test)?**
   -- WHY: 自定义测试只需要执行用户代码，不需要比较预期输出，
   可以使用更轻量的判题管道

### 范围界定 (Out of Scope)

- 在线代码编辑器 (Monaco Editor) 的具体实现 -- 假设使用成熟组件
- 题目推荐算法 (基于用户能力推荐练习题)
- 社区讨论区和题解系统
- 付费订阅和商业化系统
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Architecture)

### 组件总览 (Component Overview)

系统分为四大子系统：**用户交互层 (User Interaction Layer)**、
**提交处理层 (Submission Processing Layer)**、
**判题执行层 (Judge Execution Layer)**、
**数据与分析层 (Data & Analytics Layer)**。

```
[Browser / Mobile App]
       |
[CDN + API Gateway / Load Balancer]
       |
  +----+-----+----------+-----------+
  |          |           |           |
[Problem  [Submission  [Contest   [User
 Service]  Service]    Service]   Service]
  |          |           |           |
  v          v           v           v
[Problem DB] [Sub DB]  [Contest DB] [User DB]
(PostgreSQL) (PostgreSQL)(PostgreSQL)(PostgreSQL)
               |
          [Message Queue]
            (RabbitMQ / Kafka)
               |
      +--------+--------+
      |        |        |
  [Judge    [Judge   [Judge
   Worker1]  Worker2] Worker N]
      |        |        |
  [gVisor / Docker Sandbox]
               |
          [Test Case Storage]
           (S3 / MinIO)
               |
     +---------+---------+
     |                   |
[Result Callback]   [WebSocket Gateway]
  (-> Sub Service)    (Real-time updates)
               |
          [Redis Cache]
          (Leaderboard,
           Rate Limit,
           Session)
```

### 核心服务及职责 (Core Services)

#### 1. Problem Service (题目服务)

管理题目的完整生命周期：

- **题目 CRUD**: 创建、编辑、发布题目; 支持 Markdown 渲染和 LaTeX 公式
- **测试用例管理**: 上传/编辑测试用例 (input/output 文件对)，
  区分样例测试用例 (公开) 和隐藏测试用例 (评判用)
- **版本控制**: 题目修改需要版本管理，避免竞赛中途改题影响公平性
- **资源限制配置**: 每道题目的时间限制 (如 2s)、内存限制 (如 256MB)，
  按语言设置不同倍率 (Java 通常 2x, Python 通常 3-5x)

存储: **PostgreSQL** 存题目元数据 + **S3/MinIO** 存测试用例文件

#### 2. Submission Service (提交服务)

接收并管理用户代码提交：

- **提交接收**: 校验代码长度 (限制 64KB)、语言合法性，生成唯一提交 ID
- **去重检测**: 短时间内 (5s) 对同一题目的重复提交进行去重
- **入队**: 将提交消息发送到 **RabbitMQ** 判题队列
- **状态追踪**: 维护提交状态机
  (Pending -> Compiling -> Running -> Judging -> Accepted/Wrong Answer/...)
- **回调处理**: 接收 Judge Worker 的判题结果，更新数据库，
  通过 **WebSocket** 推送实时状态给用户

#### 3. Judge Worker (判题工作节点)

系统的计算核心，在安全沙箱中执行用户代码：

- **编译阶段 (Compilation)**: 在沙箱内编译用户代码，捕获编译错误 (CE)
- **执行阶段 (Execution)**: 逐个运行测试用例，注入 stdin，捕获 stdout/stderr
- **资源限制**: 通过 **cgroups v2** 限制 CPU 时间、内存、进程数、磁盘 I/O
- **沙箱隔离**: 使用 **gVisor (runsc)** 或 **Docker + seccomp** 提供系统调用级隔离
- **输出比较**: 将用户输出与期望输出逐行比较 (忽略行尾空白);
  Special Judge 模式下调用自定义评判程序

#### 4. Contest Service (竞赛服务)

管理竞赛生命周期和排行榜：

- **竞赛管理**: 创建竞赛、设置时间窗口、绑定题目集
- **排行榜计算**: 支持两种排名规则:
  - **ACM-ICPC**: 按通过题数排序，相同则按罚时排序
    (罚时 = 通过时间 + 错误提交数 x 20min)
  - **Rating/OI**: 按各题得分之和排序 (部分分)
- **实时更新**: 排行榜通过 **Redis Sorted Set** 维护，
  提交判题完成后增量更新，通过 **SSE (Server-Sent Events)** 推送前端
- **封榜 (Freeze)**: 竞赛最后 1 小时封榜，隐藏其他选手最新提交结果

#### 5. WebSocket Gateway (实时通信网关)

- 维护用户 WebSocket 连接 (竞赛期间可能数千并发连接)
- 接收 Submission Service 的判题状态更新，推送给对应用户
- 广播排行榜变更到所有竞赛参与者
- 使用 **Redis Pub/Sub** 在多个 Gateway 实例间同步消息

### 数据库选型 (Database Choices)

| 数据类型 | 存储方案 | 理由 |
|----------|----------|------|
| 题目元数据 | **PostgreSQL** | 结构化数据，需要事务保证，支持全文搜索 |
| 测试用例文件 | **S3 / MinIO** | 大文件存储，测试用例可达数百 MB |
| 提交记录 | **PostgreSQL** (分区表) | 按月分区，支持复杂查询 (按用户/题目/状态) |
| 排行榜 | **Redis Sorted Set** | 高频读写，内存级延迟 |
| 用户 Session | **Redis** | 高速缓存，TTL 自动过期 |
| 代码相似度索引 | **Elasticsearch** | 全文搜索 + 倒排索引支持 token 级相似度查询 |

### 通信模式 (Communication Patterns)

- **同步 REST**: 用户 -> API Gateway -> 各微服务 (题目查询、提交代码)
- **异步消息队列**: Submission Service -> RabbitMQ -> Judge Worker (判题任务)
- **WebSocket**: 判题实时进度推送、竞赛排行榜实时更新
- **Redis Pub/Sub**: 多 WebSocket Gateway 实例间的消息广播
"""

# ---------------------------------------------------------------------------
# S3: API Design & Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 核心 API 端点 (Core API Endpoints)

#### 提交代码 (Submit Code)

```
POST /api/v1/submissions
Authorization: Bearer <token>
Content-Type: application/json

{
  "problem_id": "two-sum",
  "language": "cpp",
  "source_code": "#include <vector>\n..."
}

Response 202 Accepted:
{
  "submission_id": "sub_abc123",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 查询提交状态 (Query Submission Status)

```
GET /api/v1/submissions/{submission_id}

Response 200:
{
  "submission_id": "sub_abc123",
  "status": "accepted",
  "language": "cpp",
  "runtime_ms": 12,
  "memory_kb": 7840,
  "test_cases_passed": 50,
  "test_cases_total": 50,
  "created_at": "2024-01-15T10:30:00Z",
  "judged_at": "2024-01-15T10:30:05Z"
}
```

#### 运行代码 (Run Code - Playground)

```
POST /api/v1/run
Authorization: Bearer <token>

{
  "problem_id": "two-sum",
  "language": "python3",
  "source_code": "class Solution: ...",
  "custom_input": "[2,7,11,15]\n9"
}

Response 200:
{
  "run_id": "run_xyz789",
  "status": "finished",
  "stdout": "[0, 1]\n",
  "stderr": "",
  "runtime_ms": 45,
  "memory_kb": 14200
}
```

#### 获取竞赛排行榜 (Get Contest Leaderboard)

```
GET /api/v1/contests/{contest_id}/leaderboard?page=1&page_size=50

Response 200:
{
  "contest_id": "weekly-380",
  "total_participants": 12345,
  "leaderboard": [
    {
      "rank": 1,
      "user": "tourist",
      "score": 4,
      "penalty_minutes": 85,
      "problems": [
        {"problem_id": "A", "accepted": true, "attempts": 1, "time_min": 5},
        {"problem_id": "B", "accepted": true, "attempts": 2, "time_min": 25}
      ]
    }
  ]
}
```

### 核心数据模型 (Core Data Models)

#### Problem (题目)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| slug | VARCHAR(100) | URL 友好标识 (如 "two-sum") |
| title | VARCHAR(255) | 题目名称 |
| description | TEXT | Markdown 格式题目描述 |
| difficulty | ENUM | easy / medium / hard |
| time_limit_ms | INT | 默认时间限制 (ms) |
| memory_limit_kb | INT | 默认内存限制 (KB) |
| language_multipliers | JSONB | 各语言时间/内存倍率 |
| is_special_judge | BOOLEAN | 是否使用自定义评判器 |
| created_at | TIMESTAMP | 创建时间 |

#### Submission (提交记录)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 外键 -> User |
| problem_id | UUID | 外键 -> Problem |
| language | VARCHAR(20) | 编程语言 |
| source_code | TEXT | 用户提交的代码 |
| status | ENUM | pending / compiling / running / accepted / wrong_answer / tle / mle / re / ce |
| runtime_ms | INT | 最大测试用例运行时间 |
| memory_kb | INT | 最大测试用例内存使用 |
| test_cases_passed | INT | 通过的测试用例数 |
| test_cases_total | INT | 总测试用例数 |
| judge_worker_id | VARCHAR(50) | 执行判题的 Worker ID |
| created_at | TIMESTAMP | 提交时间 |
| judged_at | TIMESTAMP | 判题完成时间 |

#### TestCase (测试用例)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| problem_id | UUID | 外键 -> Problem |
| input_url | VARCHAR(500) | S3 输入文件 URL |
| output_url | VARCHAR(500) | S3 期望输出文件 URL |
| is_sample | BOOLEAN | 是否为样例 (对用户可见) |
| order_index | INT | 排序 (简单用例在前) |

### 写路径: 用户提交代码 (Write Path)

```
1. [Browser] --POST /submissions--> [API Gateway]
2. [API Gateway] --auth check--> [User Service]
3. [API Gateway] --> [Submission Service]
   - 校验: 代码长度 <= 64KB, 语言合法, 频率限制 (5次/分钟)
   - 去重: Redis SETNX(user:problem:hash, 5s TTL)
   - 写入 PostgreSQL (status=pending)
   - 发送消息到 RabbitMQ judge_queue
     payload: {submission_id, problem_id, language, source_code}
4. [API Gateway] --202 Accepted--> [Browser]
5. [Browser] 建立 WebSocket 连接监听 submission_id 状态更新
```

### 读路径: 判题执行 (Read Path - Judge Execution)

```
1. [Judge Worker] 从 RabbitMQ 消费一条提交消息
2. [Judge Worker] 从 S3 下载测试用例 (LRU 缓存热门题目)
3. [Judge Worker] 创建 gVisor 沙箱容器:
   - 挂载: 用户代码(只读), 测试输入(只读), 输出目录(读写)
   - cgroups: CPU={time_limit}s, MEM={mem_limit}KB, PID=10, NET=none
4. [沙箱内] 编译用户代码 -> 如果失败返回 CE
5. 逐个测试用例执行:
   a. 将 input 文件重定向到 stdin
   b. 运行用户程序, 捕获 stdout + stderr
   c. 检查退出码 (非零 -> RE), 时间 (超限 -> TLE), 内存 (超限 -> MLE)
   d. 比较 stdout 与 expected output (逐行, trim trailing whitespace)
   e. 回调 Submission Service 更新进度 (running 3/10)
6. 所有测试用例通过 -> AC; 任一失败 -> 对应状态 (WA/TLE/MLE/RE)
7. [Judge Worker] POST /internal/judge-result -> [Submission Service]
8. [Submission Service] 更新 DB, 通过 WebSocket 推送最终结果
9. [Submission Service] 如果是竞赛提交, 发消息给 Contest Service 更新排行榜
```
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Capacity Estimation)

#### 用户规模与提交量 (User Scale & Submission Volume)

- 注册用户: 500 万
- **DAU (Daily Active Users)**: 50 万 (10% 日活率)
- 每用户日均提交: 2 次
- 日提交量: $50 \times 10^4 \times 2 = 10^6$ (100 万次/天)
- 平均提交 QPS: $\frac{10^6}{86400} \approx 12$ QPS
- **峰值 QPS** (竞赛高峰, 10x): $\approx 120$ QPS
- 竞赛突发: 5000 并发参赛者，每人每 2 分钟提交一次
  $\rightarrow \frac{5000}{120} \approx 42$ QPS (单场竞赛)

#### 存储估算 (Storage Estimation)

**提交记录存储:**
- 每条提交: 代码 (平均 2KB) + 元数据 (500B) $\approx$ 2.5KB
- 日增量: $10^6 \times 2.5\text{KB} = 2.5\text{GB/day}$
- 年增量: $2.5 \times 365 \approx 912\text{GB/year} \approx 1\text{TB/year}$

**测试用例存储:**
- 题目数量: 3000 道
- 每题平均测试用例: 50 个, 每个 input+output 平均 10KB
- 总量: $3000 \times 50 \times 10\text{KB} = 1.5\text{GB}$
- 大数据题 (约 5%): 每个测试用例可达 50MB
  $\rightarrow 150 \times 5 \times 50\text{MB} = 37.5\text{GB}$

**题目元数据:**
- 每题: 描述 10KB + 元数据 1KB $\approx$ 11KB
- 总量: $3000 \times 11\text{KB} \approx 33\text{MB}$ (可忽略)

#### 计算资源估算 (Compute Resource Estimation)

**Judge Worker 数量:**
- 峰值 120 提交/秒, 每次判题平均耗时 10s (编译 2s + 运行 50 个测试 x 160ms)
- 并发判题数: $120 \times 10 = 1200$
- 每个 Worker 同时处理 1 个提交 (安全隔离要求)
- 需要 Worker 数: $\lceil 1200 \rceil = 1200$ 个容器槽位
- 实际部署: 每台物理机 (8 核 32GB) 可运行 4 个并发 Worker
  $\rightarrow \lceil 1200 / 4 \rceil = 300$ 台机器 (峰值)
- 非竞赛日 (12 QPS): $12 \times 10 / 4 = 30$ 台机器
- **弹性伸缩策略**: 基础 30 台 + 竞赛前 Auto Scaling 到 300 台

#### 带宽估算 (Bandwidth Estimation)

- 每次提交: 请求 ~3KB, 响应 ~1KB
- 峰值带宽: $120 \times 4\text{KB} = 480\text{KB/s} \approx 4\text{Mbps}$ (可忽略)
- 测试用例下载 (内网): Judge Worker 从 S3 拉取，热门题缓存命中率 > 90%

#### 内存估算 (Memory - Cache)

- 热门题目测试用例缓存: 前 500 题 x 平均 500KB = 250MB (每 Worker)
- 排行榜 Redis: 竞赛 10K 参赛者 x 100B/条 = 1MB (可忽略)
- 用户 Session 缓存: 50 万 DAU x 200B = 100MB

### 核心算法 (Core Algorithms)

#### 1. 判题状态机 (Judge State Machine)

```
[Pending] --(Worker拾取)--> [Compiling]
[Compiling] --(编译失败)--> [Compile Error]
[Compiling] --(编译成功)--> [Running]
[Running] --(逐个测试用例)--> [Running (i/N)]
[Running] --(时间超限)--> [Time Limit Exceeded]
[Running] --(内存超限)--> [Memory Limit Exceeded]
[Running] --(运行时错误)--> [Runtime Error]
[Running] --(输出不匹配)--> [Wrong Answer]
[Running] --(全部通过)--> [Accepted]
```

#### 2. 沙箱资源限制 (Sandbox Resource Limits via cgroups v2)

每个 Judge Worker 为用户进程设置以下约束:

$$
\text{CPU Time Limit} = T_{\text{problem}} \times M_{\text{language}}
$$

其中 $T_{\text{problem}}$ 是题目设定的时间限制 (如 2s)，
$M_{\text{language}}$ 是语言倍率:

| 语言 | $M_{\text{language}}$ | 典型限制 (2s 题目) |
|------|----------------------|-------------------|
| C/C++ | 1.0 | 2s |
| Java | 2.0 | 4s |
| Python | 3.0-5.0 | 6-10s |
| Go | 1.5 | 3s |
| JavaScript (Node) | 2.0 | 4s |

内存限制类似:

$$
\text{Memory Limit} = M_{\text{problem}} \times K_{\text{language}}
$$

Java 额外加 $+64\text{MB}$ 作为 JVM 基础开销。

#### 3. ACM-ICPC 排名算法 (ACM-ICPC Ranking)

$$
\text{Penalty}(u) = \sum_{p \in \text{Solved}(u)} \left( t_p + 20 \times (a_p - 1) \right)
$$

其中 $t_p$ 是用户 $u$ 通过题目 $p$ 的时间 (分钟)，$a_p$ 是提交次数。

排序规则:
1. 通过题数降序
2. 相同题数时，罚时升序

#### 4. 代码相似度检测 -- MOSS 算法 (Winnowing)

**MOSS (Measure of Software Similarity)** 使用 **Winnowing** 指纹算法:

1. **Token 化**: 将代码转为 token 序列 (去除变量名、空白、注释)
2. **K-gram 哈希**: 对连续 $k$ 个 token 计算哈希值
3. **Winnowing 选择**: 在每个大小为 $w$ 的窗口中选择最小哈希作为指纹

$$
\text{Similarity}(A, B) = \frac{\mid F(A) \cap F(B) \mid}{\min(\mid F(A) \mid, \mid F(B) \mid)}
$$

其中 $F(A)$ 和 $F(B)$ 分别是代码 $A$ 和 $B$ 的指纹集合。
典型阈值: $\text{Similarity} > 0.7$ 标记为疑似抄袭。

参数选择: $k = 25$ (token gram 大小), $w = 4$ (窗口大小)，
平衡检测灵敏度与误报率。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性深入分析 (Scale & Reliability Deep Dive)

### 具体规模数据 (Concrete Scale Numbers)

| 维度 | 数值 |
|------|------|
| 注册用户 | 500 万 |
| DAU | 50 万 |
| 日提交量 | 100 万次 |
| 平均判题时间 | 10s |
| 题目数量 | 3000 道 |
| 测试用例总量 | ~40 GB |
| 提交存储 (年) | ~1 TB |
| 峰值并发 Judge Worker | 1200 |
| 竞赛峰值 QPS | 120 |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 风险 | 缓解方案 |
|------|------|----------|
| **RabbitMQ** | 队列宕机 -> 提交丢失 | 镜像队列 (Mirrored Queue) + 持久化; 备用 Dead Letter Queue |
| **PostgreSQL** | 主库宕机 -> 写入失败 | 主从复制 + 自动 Failover (Patroni); 提交表按月分区 |
| **S3 / MinIO** | 测试用例不可用 -> 判题失败 | S3 本身 11 个 9 持久性; MinIO 部署时使用纠删码 (Erasure Coding) |
| **Judge Worker** | 个别 Worker 崩溃 | 无状态设计，RabbitMQ 自动重投; 心跳检测 + 超时回收 |
| **Redis** | 缓存击穿 | Redis Sentinel 高可用; 排行榜数据同时持久化到 PostgreSQL |
| **WebSocket Gateway** | 实例宕机 -> 连接断开 | 多实例 + 客户端自动重连; Redis Pub/Sub 跨实例消息同步 |

### 多数据中心 / 跨地域部署 (Multi-Datacenter)

对于全球化 OJ (如 LeetCode 同时服务美国、中国、印度用户):

- **Active-Active 读, Active-Passive 写**: 题目数据和提交历史可在多区域读取
  (PostgreSQL 只读副本); 写操作路由到主区域
- **Judge Worker 区域部署**: 每个区域独立部署 Judge Worker 集群，
  避免跨区域传输用户代码和测试用例
- **测试用例 CDN**: S3 Cross-Region Replication，Judge Worker 从最近的
  S3 副本读取测试用例
- **竞赛全局一致性**: 竞赛期间排行榜通过单一主区域计算，
  其他区域通过 Redis 全局复制获取副本 (延迟 < 1s)
- **DNS 路由**: **GeoDNS** 将用户路由到最近的 API 入口;
  竞赛提交始终路由到 Judge Worker 所在区域

### 高并发处理 (High Concurrency Handling)

#### 1. 判题队列背压控制 (Backpressure)

竞赛开始瞬间可能出现数千提交的突发:

- **分优先级队列**: 竞赛提交 > 普通提交 > Playground 运行
  (RabbitMQ Priority Queue 或独立队列)
- **预热 (Pre-warming)**: 竞赛开始前 10 分钟自动扩容 Judge Worker
- **客户端限流**: 每用户 5 次提交/分钟 (Token Bucket); 竞赛模式放宽到 10 次/分钟
- **降级策略**: 极端负载下暂停 Playground 功能，优先保证正式提交

#### 2. 连接池与数据库优化

- **PgBouncer** 连接池: 限制最大 PostgreSQL 连接数 (500)
- 提交表按月分区: `submissions_2024_01`, `submissions_2024_02`, ...
- 查询优化: 覆盖索引 `(user_id, problem_id, created_at DESC)` 加速历史查询
- 批量写入: Judge Worker 的中间结果 (running 3/10) 不写 DB,
  仅通过 WebSocket 推送; 只有最终结果写 DB

#### 3. 速率限制 (Rate Limiting)

- **提交限流**: Token Bucket, 每用户 5 次/分钟 (Redis 实现)
- **Playground 限流**: 10 次/分钟 (资源更轻量)
- **API 全局限流**: 1000 req/s per IP (防止 DDoS)
- **竞赛注册限流**: 渐进式开放注册 (防止瞬间万人注册)

#### 4. 熔断器 (Circuit Breaker)

- Judge Worker 连续 5 次执行超时 -> 标记该 Worker 为 unhealthy,
  暂停分配新任务 30s
- 外部依赖 (S3 测试用例下载) 失败率 > 50% -> 触发熔断,
  使用本地缓存的测试用例
- 竞赛排行榜更新延迟 > 10s -> 降级为定时批量更新 (每 5s)

### 监控与告警 (Monitoring & Alerting)

关键指标:

| 指标 | 告警阈值 | 说明 |
|------|----------|------|
| 判题队列深度 | > 5000 | 提交积压，需要扩容 Worker |
| 判题 P99 延迟 | > 60s | 超出 SLA, 检查 Worker 健康状态 |
| Worker 利用率 | > 85% | 即将饱和，触发 Auto Scaling |
| 编译错误率 | > 30% | 可能是编译器版本问题 |
| WebSocket 连接数 | > 10K/实例 | 接近容量上限 |
| RabbitMQ 消息重投率 | > 5% | Worker 频繁崩溃 |
| 测试用例缓存命中率 | < 80% | 缓存大小不足或热点变化 |
"""

# ---------------------------------------------------------------------------
# S6: Trade-offs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **沙箱技术** | Docker + seccomp | **gVisor (runsc)** | 选 gVisor: 提供系统调用级拦截，比 Docker 默认更强的隔离; Docker 的 seccomp 配置复杂且容易遗漏危险系统调用 |
| **消息队列** | Kafka | **RabbitMQ** | 选 RabbitMQ: 判题场景需要任务级别的 ACK/NACK 和优先级队列; Kafka 的日志语义在此场景下过度设计 |
| **判题粒度** | 按提交整体判 | **逐测试用例判** | 选逐个用例: 支持实时进度反馈和 early termination (首个 WA 即停); 但增加了 Worker 与 Submission Service 的通信次数 |
| **排行榜更新** | 每次提交同步更新 | **异步批量更新** | 选异步: 使用 Redis Sorted Set + 异步 Consumer; 排行榜延迟 2-3s 可接受, 避免竞赛高峰时排行榜更新成为瓶颈 |
| **测试用例存储** | 数据库 BLOB | **对象存储 (S3)** | 选 S3: 测试用例文件大小差异极大 (1KB-100MB), 对象存储更适合; DB 存大 BLOB 会严重影响备份和复制性能 |

### CAP 定理应用 (CAP Theorem Application)

- **判题结果**: 选择 **CP (Consistency + Partition Tolerance)** -- 判题结果
  必须准确无误, 宁可延迟也不能给出错误判定。当 Judge Worker 与主数据库
  网络分区时, Worker 会重试而非给出部分结果
- **排行榜**: 选择 **AP (Availability + Partition Tolerance)** -- 排行榜允许
  短暂不一致 (刚通过的提交可能 3-5s 后才反映在排行榜上), 但排行榜页面
  始终可用不会返回错误
- **题目内容**: 选择 **AP** -- 题目描述可以被缓存在 CDN, 即使数据库暂时
  不可用, 用户仍能浏览题目 (可能看到旧版本)

### 成本 vs 性能 (Cost vs Performance)

- **Judge Worker 成本**: 峰值 300 台机器 x $0.10/h = $30/h (竞赛日约 2 小时)
  vs 常态 30 台 x $0.10/h = $72/天
- **优化方案**: 使用 **Spot Instances** 作为竞赛扩容节点 (成本降低 70%),
  配合 **Warm Pool** 保证 2 分钟内扩容到位
- **替代方案**: 使用 **AWS Fargate / Kubernetes** 按需启动 Judge 容器,
  完全按使用量计费, 但冷启动延迟 (5-15s) 影响判题速度

### 10x / 100x 规模下的变化 (Scaling to 10x / 100x)

**10x (日提交 1000 万):**
- Judge Worker 峰值 3000 台 -> 需要 **Kubernetes** 编排 + 跨区域部署
- 提交存储 10TB/年 -> 冷热分离: 最近 3 个月热存 (SSD), 历史冷存 (HDD/S3)
- RabbitMQ -> 迁移到 **Kafka** (更好的吞吐量和分区扩展能力)

**100x (日提交 1 亿):**
- 单一 PostgreSQL 无法承载 -> 按 `problem_id` 分片 (Sharding)
- 全局唯一排行榜 -> 分区排行榜 (按 region/rating 段) + 异步合并
- 测试用例存储需要全球 CDN 分发，每个区域独立缓存层
- 安全沙箱可能需要 **microVM (Firecracker)** 替代 gVisor 以获得更好的启动性能
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果 Judge Worker 执行用户代码时自身被攻击了怎么办?

**承认局限性**: 沙箱安全是 OJ 最关键也是最难做到 100% 的部分。任何沙箱
都不能保证绝对安全，只能通过多层防御提高攻击成本。

**缓解措施**:

1. **多层沙箱**: gVisor (系统调用拦截) + cgroups (资源限制) + 网络命名空间
   (完全断网) + 只读文件系统 (除输出目录)
2. **一次性容器**: 每次判题使用全新容器, 执行完立即销毁。即使被攻破,
   攻击者也无法持久化
3. **Worker 隔离**: 每台 Judge 机器运行在独立 VPC 子网,
   无法访问内网其他服务 (数据库、消息队列等)
4. **系统调用白名单**: 只允许约 50 个安全的系统调用 (read, write, mmap, brk 等),
   阻止 fork, execve, socket, ptrace 等危险调用
5. **异常检测**: 监控 Judge Worker 的系统调用模式,
   偏离基线的行为 (如大量 mmap 调用) 触发告警并隔离该 Worker

### Q2: 竞赛高峰时如果判题队列积压严重怎么办?

**承认局限性**: 竞赛开始后 5 分钟是提交高峰, 可能出现队列深度短暂飙升。

**缓解措施**:

1. **预测性扩容**: 竞赛前 10 分钟根据注册人数预扩容 Worker
   (经验公式: Worker 数 = 注册人数 / 4)
2. **优先级队列**: 竞赛提交 > 练习提交 > Playground;
   极端情况下暂停 Playground 释放资源
3. **批量判题优化**: 多个用户提交同一题目时，测试用例只需从 S3 加载一次
   (共享本地缓存)
4. **Early Termination**: 遇到第一个 WA/TLE 即终止剩余测试用例，
   释放 Worker 给下一个提交 (LeetCode 实际也这样做)
5. **用户可见**: 队列深度 > 阈值时，在 UI 显示预计等待时间
   (如 "当前排队提交: 2300, 预计等待 45 秒")

### Q3: 如何保证同一份代码多次提交得到相同判定结果?

**承认局限性**: 完全确定性判题很难实现, 因为操作系统调度、CPU 缓存状态、
系统负载等因素都会影响运行时间。

**缓解措施**:

1. **时间限制宽松倍率**: 实际运行时间限制设为理论限制的 1.5-2x,
   留出波动余量 (如题目限制 2s, 实际判定用 3s)
2. **多次运行取最佳**: 对于接近时间限制的提交 (如限制 2s, 运行了 1.8s),
   自动重新判题 3 次, 取最短时间作为结果
3. **固定 CPU 频率**: Judge Worker 禁用 CPU 频率动态调节
   (**cpufreq governor** 设为 performance 模式)
4. **资源独占**: 每个 Judge Worker 同一时刻只运行一个用户程序,
   避免多用户代码争抢 CPU 缓存
5. **基准测试校准**: 每台 Worker 启动时运行标准基准程序,
   校准时间限制的修正系数 (慢机器给更多时间)

### Q4: 如何处理恶意代码 (fork bomb, 无限输出等)?

**缓解措施**:

1. **Fork bomb**: cgroups v2 限制 `pids.max = 10`,
   超出后新进程创建直接返回 EAGAIN
2. **无限输出**: 限制 stdout 写入量 (如 256MB),
   超出后关闭文件描述符, 进程收到 SIGPIPE 终止
3. **无限循环/死循环**: 墙钟时间 (wall clock) 限制 = CPU 时间限制 x 3,
   超出后发送 SIGKILL
4. **磁盘填满**: 沙箱 tmpfs 限制 (如 64MB), 写满后返回 ENOSPC
5. **网络访问**: 网络命名空间完全隔离, 无回环地址,
   所有 socket 系统调用被 seccomp 拒绝
6. **汇编内联 / 特权指令**: seccomp 阻止 ptrace, iopl, ioperm 等特权操作;
   gVisor 拦截所有非白名单系统调用

### Q5: 如何支持新增一种编程语言?

**设计扩展性**:

1. **语言配置注册**: 每种语言定义为一个 JSON 配置:
   ```json
   {
     "id": "rust",
     "name": "Rust 1.75",
     "compile_cmd": "rustc -O -o main main.rs",
     "run_cmd": "./main",
     "source_file": "main.rs",
     "time_multiplier": 1.2,
     "memory_extra_mb": 0,
     "docker_image": "judge-rust:1.75"
   }
   ```
2. **独立 Docker 镜像**: 每种语言有独立的运行时镜像, 新增语言只需构建新镜像
3. **热更新**: 新语言配置可以动态加载, 无需重启 Judge Worker
4. **测试矩阵**: 新增语言时, 使用标准测试套件 (Hello World, 大数据 I/O,
   递归深度, 内存分配) 验证沙箱兼容性和性能基线
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 完整 1 小时时间分配 (Full 1-Hour Breakdown)

#### 0-5 min: 需求澄清 (Requirements Clarification)

"我们要设计一个类似 LeetCode 的在线判题系统。让我先确认几个关键需求:

**功能性需求**:
- 用户提交代码 -> 系统在沙箱中编译运行 -> 对比测试用例给出判定
- 支持 5+ 编程语言 (C++, Java, Python, Go, JS)
- 竞赛模式 + 实时排行榜
- 代码 Playground (运行自定义输入)

**非功能性需求**:
- 500 万注册用户, 50 万 DAU, 日均 100 万次提交
- 判题 P99 < 30s, 竞赛峰值 < 60s
- 判题结果强一致, 排行榜最终一致
- 安全: 用户代码完全沙箱隔离

**需要确认**: 是否需要 Special Judge? 交互式题目? 抄袭检测?"

#### 5-15 min: 高层架构 (High-Level Architecture)

"系统的核心是一个**异步判题管道**:

1. **Submission Service** 接收代码, 写入 DB, 发消息到 **RabbitMQ**
2. **Judge Worker** 消费消息, 在 **gVisor** 沙箱中编译运行用户代码
3. 结果通过回调更新 DB, 通过 **WebSocket** 实时推送给用户

为什么选择异步而非同步?
- 判题耗时 5-30s, 同步会长时间占用 HTTP 连接
- 异步允许解耦提交速率和判题速率, 用队列吸收突发流量
- Judge Worker 可以独立弹性伸缩

数据库选择:
- **PostgreSQL**: 题目、提交记录 (ACID 保证)
- **S3/MinIO**: 测试用例文件 (大小不等, 最大 100MB)
- **Redis**: 排行榜 (Sorted Set), 限流, Session
- **RabbitMQ**: 判题任务队列 (优先级 + ACK/NACK)"

#### 15-40 min: 深入设计 (Deep Dive)

**深入方向 1: 沙箱安全 (10 min)**

"这是 OJ 最关键的组件。我们用多层防御:

- **gVisor**: 拦截系统调用, 在用户态模拟 Linux 内核
- **cgroups v2**: 限制 CPU 时间 / 内存 / 进程数 / 磁盘 I/O
- **seccomp**: 白名单 ~50 个安全系统调用
- **网络隔离**: 独立网络命名空间, 完全断网
- **一次性容器**: 每次判题新建, 执行完销毁

关键参数:
- CPU: 题目限制 x 语言倍率 (Python 3-5x)
- MEM: 题目限制 x 语言倍率 + JVM 额外开销
- PID: max 10 (防 fork bomb)
- 输出: max 256MB (防无限输出)"

**深入方向 2: 判题管道优化 (8 min)**

"从提交到出结果的完整流程:

1. 提交 -> 去重检测 (Redis SETNX, 5s 窗口) -> 入队 RabbitMQ
2. Worker 拉取任务 -> 下载测试用例 (LRU 缓存, 命中率 >90%)
3. 编译 (独立阶段, 失败快速返回 CE)
4. 逐用例执行: stdin 重定向 -> 运行 -> 捕获 stdout -> 逐行比较
5. Early termination: 首个失败即停止, 释放 Worker

竞赛高峰优化:
- 预测性扩容: 注册人数/4 = 预备 Worker 数
- 优先级队列: Contest > Practice > Playground
- 测试用例共享缓存: 热门题目 500 题 x 500KB = 250MB/Worker"

**深入方向 3: 排行榜系统 (7 min)**

"竞赛排行榜用 **Redis Sorted Set**:

- Score 编码: `-(solved_count * 10^8 + (total_time - penalty))`
  (负数确保 ZRANGEBYSCORE 返回正确顺序)
- 每次 AC 提交 -> 异步更新 Redis ZADD
- 前端通过 SSE 订阅排行榜变更, 每 2-3s 增量推送
- 封榜 (最后 1 小时): 停止向非当事人推送更新"

#### 40-50 min: 权衡讨论 (Trade-offs & Scaling)

"几个关键权衡:

1. **gVisor vs Docker seccomp**: gVisor 更安全但有 ~5-10% 性能开销,
   对于 OJ 场景安全性 > 性能
2. **RabbitMQ vs Kafka**: 判题需要任务级 ACK 和优先级, RabbitMQ 更合适;
   如果日提交 > 1000 万, 再考虑迁移 Kafka
3. **逐用例判 vs 整体判**: 逐用例支持实时进度和 early termination,
   但增加通信开销

10x 规模 (1000 万提交/天):
- Kubernetes 编排 Judge Worker, 跨区域部署
- 提交表分区 -> 分片
- RabbitMQ -> Kafka

100x 规模 (1 亿提交/天):
- Firecracker microVM 替代 gVisor (更快启动)
- 全球 CDN 分发测试用例
- 分区排行榜 + 异步合并"

#### 50-55 min: 收尾 (Wrap-up)

"如果有更多时间, 我还会改进:
1. **抄袭检测**: MOSS Winnowing 算法, 竞赛结束后批量分析
2. **动态难度**: 基于用户 Rating 推荐练习题
3. **分布式判题**: 跨区域 Worker 就近判题, 减少测试用例传输

监控方面: 判题队列深度、P99 延迟、Worker 利用率是三个最关键指标。"

#### 55-60 min: 向面试官提问

"关于这个系统, 我想了解:
- 贵团队实际使用什么沙箱技术?
- 多语言支持在实践中最大的痛点是什么?
- 竞赛场景下最常遇到的运维挑战是什么?"

---

### 3 分钟电梯演讲版 (3-Minute Elevator Pitch)

"在线判题系统的核心是一个**异步安全代码执行管道**。

用户提交代码后, Submission Service 做去重和限流, 然后通过 RabbitMQ 分发给
Judge Worker 集群。Worker 在 gVisor 沙箱中编译运行代码, 通过 cgroups 限制
CPU/内存/进程数, 逐个测试用例执行并比较输出。结果通过 WebSocket 实时
推送给用户。

竞赛模式下, 排行榜用 Redis Sorted Set 维护, 异步更新以避免成为瓶颈。
弹性伸缩: 常态 30 台 Worker, 竞赛前预扩容到 300 台 (Spot Instances 降低成本)。

关键设计选择: gVisor (安全 > 性能), RabbitMQ (任务级 ACK > Kafka 日志语义),
逐测试用例判题 (支持实时反馈 + early termination)。

最大挑战: 沙箱安全 (多层防御: gVisor + cgroups + seccomp + 网络隔离) 和
判题一致性 (固定 CPU 频率 + 资源独占 + 接近时限时多次运行取最佳)。"
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def populate_interview_online_judge() -> None:
    """Insert/update all 8 sections for the Online Judge system design."""
    init_db()
    db = SessionLocal()
    try:
        record = db.query(SystemDesign).filter_by(slug=SLUG).first()
        if record is None:
            record = SystemDesign(
                slug=SLUG,
                title=TITLE,
                display_order=DISPLAY_ORDER,
            )
            db.add(record)
            db.flush()
            print(f"[DONE] Created SystemDesign record: slug='{SLUG}', title='{TITLE}'")
        else:
            print(f"[INFO] Found existing record for slug='{SLUG}', updating...")

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
        total_chars = 0
        for name, content in sections:
            length = len(content) if content else 0
            total_chars += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")
        print(f"  Total: {total_chars} chars")

        # Check for Chinese characters
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        for name, content in sections:
            if content and chinese_pattern.search(content):
                print(f"  [OK] {name}: Chinese chars present")
            else:
                print(f"  [WARN] {name}: No Chinese chars found!")

        # Check for bare | in math
        bare_pipe = False
        for name, content in sections:
            if not content:
                continue
            in_math = False
            for i, ch in enumerate(content):
                if ch == "$" and (i == 0 or content[i - 1] != "\\"):
                    in_math = not in_math
                if in_math and ch == "|" and (i == 0 or content[i - 1] != "\\"):
                    before = content[max(0, i - 4):i]
                    if "\\mid" not in before and "\\vert" not in before:
                        bare_pipe = True
                        print(f"  [WARN] {name}: bare | found in math near position {i}")

        if not bare_pipe:
            print("  [OK] No bare | in math formulas")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_interview_online_judge()
