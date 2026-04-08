"""Populate interview-rate-limiter system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Rate Limiter.
Idempotent: creates record if missing, overwrites existing content.

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

SLUG = "interview-rate-limiter"
TITLE = "Design a Rate Limiter"
DISPLAY_ORDER = 101

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**限流器 (Rate Limiter)**：在给定时间窗口内，限制客户端（用户/IP/API Key）
对服务的请求次数。当请求超过阈值时，多余的请求被拒绝并返回 **HTTP 429 (Too Many
Requests)**。限流器通常部署在 **API Gateway** 层，保护后端服务免受流量洪峰和滥用。

### 功能性需求 (Functional Requirements)

1. **请求计数 (Request Counting)**：按客户端标识（user ID / IP / API Key）准确统计请求数
2. **限流决策 (Rate Decision)**：根据预定义规则判断是否允许当前请求通过
3. **限流规则引擎 (Rule Engine)**：支持灵活配置限流规则（每分钟 N 次、每秒 M 次等）
4. **HTTP 响应头 (Response Headers)**：返回 `X-RateLimit-Limit`、`X-RateLimit-Remaining`、`X-RateLimit-Retry-After` 等标准头
5. **多维度限流 (Multi-dimension)**：支持按用户、API 端点、IP 等不同维度独立限流

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（限流器故障不应导致后端服务不可用）
- **延迟 (Latency)**：P99 < 1ms（限流检查在请求关键路径上，必须极快）
- **一致性 (Consistency)**：在分布式环境下允许轻微不精确（偶尔多放几个请求可接受），但不能严重超限
- **可扩展性 (Scalability)**：支撑百万级 QPS（作为所有 API 请求的入口层）
- **容错性 (Fault Tolerance)**：限流器不可用时，应该 **放行 (fail-open)** 而非 **拒绝 (fail-closed)**

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 限流器部署在客户端还是服务端？** -- WHY: 客户端限流容易被绕过（恶意用户可直接调 API），服务端 / API Gateway 限流是标准做法。确认部署位置决定整体架构。

2. **Q: 需要支持哪些限流维度？按用户、按 IP、按 API 端点、还是组合？** -- WHY: 不同维度对应不同的 key 设计（`user:123:endpoint:/api/orders` vs `ip:1.2.3.4`），影响存储结构和规则引擎复杂度。

3. **Q: 限流规则是硬编码还是动态可配置？** -- WHY: 如果需要运行时热更新规则（如促销期间临时提高某 API 限额），需要独立的规则存储 + 推送机制，增加架构复杂度。

4. **Q: 分布式环境下对精确度的要求是什么？允许偶尔超限 1-2% 吗？** -- WHY: 严格精确需要全局锁或强一致存储（性能差）；允许轻微不精确可以用本地计数器 + 定期同步（性能好得多）。

5. **Q: 限流器故障时应该放行还是拒绝？** -- WHY: **Fail-open** 意味着限流器故障时所有请求放行（可能导致后端过载）；**Fail-closed** 意味着拒绝所有请求（用户体验极差）。大多数生产系统选择 fail-open。

6. **Q: 是否需要支持不同用户层级的差异化限流（如免费用户 vs 付费用户）？** -- WHY: 差异化限流需要规则引擎支持用户属性查询，增加每次限流检查的延迟。

7. **Q: 被限流的请求需要排队等待还是直接拒绝？** -- WHY: 排队（如 **Leaky Bucket**）适合平滑流量；直接拒绝（如 **Token Bucket**）适合保护后端。场景不同选择不同。

### 范围外 (Out of Scope)

- DDoS 防护（由 CDN/WAF 层处理）
- 用户认证 / 鉴权系统（假设已有，限流器只读取身份信息）
- 计费 / 配额管理（限流器不负责计费，只做流量控制）
- 客户端限流 SDK（只设计服务端限流器）
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Client (Browser/App/API Consumer)
    |
    v
[Load Balancer]
    |
    v
[API Gateway + Rate Limiter Middleware]
    |                 |
    |  (check)        |  (read rules)
    v                 v
[Redis Cluster]   [Rule Config Store]
    |
    v  (allowed)
[Backend Services]
```

### 服务划分 (Service Breakdown)

| 组件 | 职责 | 特点 |
|------|------|------|
| **API Gateway** | 请求入口，调用限流中间件检查后转发请求 | 无状态，水平扩展 |
| **Rate Limiter Middleware** | 核心限流逻辑：提取 key、查询计数、做出 allow/deny 决策 | 嵌入 API Gateway 进程内 |
| **Redis Cluster** | 存储限流计数器（每个 client key 的当前请求数/令牌数） | 内存存储，亚毫秒延迟 |
| **Rule Config Store** | 存储限流规则（YAML/JSON），支持动态更新 | 可用文件、数据库或配置中心（如 etcd） |
| **Rule Sync Worker** | 定期从 Config Store 拉取最新规则，缓存到 Gateway 本地内存 | 后台线程，减少每次请求查规则的延迟 |

### 数据库选择 (Storage Choice)

**计数器存储: Redis (主选)**
- 理由：限流计数器需要**亚毫秒级读写** + **原子递增** + **自动过期 (TTL)**
- Redis 的 `INCR` + `EXPIRE` 组合天然适合限流场景
- **Redis Cluster** 模式支持百万级 QPS（多分片并行）
- 持久化关闭（限流数据丢失可接受，服务重启后计数器重置）

**规则存储: 文件 / 配置中心**
- 简单方案：YAML 文件存储在磁盘，Gateway 启动时加载
- 高级方案：**etcd** / **Consul** 作为配置中心，支持运行时热更新 + 变更通知

### 通信模式 (Communication Patterns)

- **限流检查**: Gateway 进程内同步调用（本地内存规则 + Redis 网络调用）
- **规则同步**: 定时轮询 Config Store（每 30 秒），或使用 etcd watch 实时推送
- **规则更新**: 管理员通过管理 API 写入 Config Store -> 各 Gateway 异步拉取

### 限流规则配置示例 (Rule Configuration Example)

```yaml
rules:
  - key: "user:{user_id}"
    endpoint: "/api/orders"
    limit: 100
    window: "1m"       # 每分钟 100 次
    algorithm: "sliding_window_log"

  - key: "user:{user_id}"
    endpoint: "/api/search"
    limit: 30
    window: "1s"       # 每秒 30 次
    algorithm: "token_bucket"

  - key: "ip:{client_ip}"
    endpoint: "*"
    limit: 1000
    window: "1h"       # 每小时 1000 次（全局 IP 限制）
    algorithm: "fixed_window_counter"
```
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & API Design (5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 限流器内部 API (Internal Rate Limiter API)

**限流检查 (Check Rate Limit)**

```
// 内部调用，非面向用户的外部 API
RateLimiter.check(client_key, endpoint, timestamp) -> Decision

Decision:
  allowed: boolean
  remaining: int        // 剩余可用请求数
  retry_after: int      // 被限流时，建议等待的秒数
  limit: int            // 当前窗口的总限额
```

### HTTP 响应头 (Response Headers)

**请求被允许时:**

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1712582400
```

**请求被限流时:**

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Retry-After: 37
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please retry after 37 seconds.",
  "retry_after": 37
}
```

### 核心数据模型 (Core Data Models)

**Redis 中的计数器结构 (因算法而异)**

| 算法 | Redis Key 示例 | Value 类型 | TTL |
|------|---------------|-----------|-----|
| **Fixed Window** | `rl:user:123:/api/orders:202604081530` | String (counter) | 窗口大小 + buffer |
| **Sliding Window Log** | `rl:user:123:/api/orders` | Sorted Set (timestamps) | 窗口大小 + buffer |
| **Token Bucket** | `rl:user:123:/api/orders` | Hash {tokens, last_refill_ts} | 不过期 |
| **Sliding Window Counter** | `rl:user:123:/api/orders:cur` + `:prev` | String x 2 | 窗口大小 x 2 |

### 读路径 / 限流检查流程 (Rate Limit Check Flow)

1. 客户端发送 API 请求到 **API Gateway**
2. Gateway 从请求中提取**限流 key**（user ID / API Key / IP）
3. Gateway 从**本地缓存**读取匹配的限流规则（endpoint + key pattern）
4. 根据规则指定的算法，调用 **Redis** 执行原子限流检查:
   - Token Bucket: 检查剩余令牌数，足够则扣减并放行
   - Fixed Window: 对当前窗口 key 执行 INCR，检查是否超限
   - Sliding Window Log: 向 Sorted Set 添加当前时间戳，移除窗口外的旧记录，检查集合大小
5. **允许 (Allowed)**: 设置响应头 (`X-RateLimit-*`)，将请求转发到后端服务
6. **拒绝 (Denied)**: 返回 **429 Too Many Requests** + `Retry-After` 头
7. **Redis 不可用**: **Fail-open** -- 放行请求并记录告警日志

### 写路径 / 规则更新流程 (Rule Update Flow)

1. 管理员通过**管理 API** 或直接编辑 YAML 文件更新限流规则
2. 新规则写入 **Config Store**（etcd / 文件系统）
3. **Rule Sync Worker** 检测到变更（watch 或定时轮询）
4. Worker 将新规则加载到 Gateway **本地内存缓存**
5. 后续请求使用新规则（无需重启 Gateway）
6. 规则生效延迟: watch 模式 < 1 秒，轮询模式 < 30 秒

### 异步路径 (Async Path): 限流日志与监控

1. 每次限流决策（无论 allow/deny）生成日志事件
2. 日志异步写入 **Kafka** -> 消费后写入 **Elasticsearch** 或 **ClickHouse**
3. 用于：
   - 实时监控限流命中率（哪些 API 被频繁限流）
   - 告警（某用户持续触发限流 -> 可能是爬虫或攻击）
   - 限流规则调优（某 API 限额设置过低 -> 正常用户受影响）
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms (Back-of-Envelope Estimation -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

**流量估算 (Traffic Estimation)**

- **DAU (Daily Active Users)**: 5000 万
- **每用户每日平均 API 请求数**: 200 次
- **每日总请求数**: $5 \times 10^7 \times 200 = 10^{10}$（100 亿次）
- **平均 QPS**: $\frac{10^{10}}{86400} \approx 115{,}000$ QPS
- **峰值 QPS**: $115{,}000 \times 3 \approx 350{,}000$ QPS
- **每次限流检查**: 1 次 Redis 调用（原子操作）
- **Redis QPS 需求**: 350K QPS（峰值）-- 单 Redis 节点约 10 万 QPS，需要 4+ 分片

**存储估算 (Storage Estimation)**

- **限流 key 数量**: 假设 5000 万用户 x 平均 5 个限流维度 = 2.5 亿个 key
- **每个 key 大小**:
  - Fixed Window: key (~60 bytes) + counter (8 bytes) = ~68 bytes
  - Token Bucket: key (~60 bytes) + hash fields (16 bytes) = ~76 bytes
  - Sliding Window Log: key (~60 bytes) + sorted set (每请求 16 bytes x 窗口内请求数)
- **Fixed Window 总内存**: $2.5 \times 10^8 \times 68 = 17$ GB
- **Token Bucket 总内存**: $2.5 \times 10^8 \times 76 = 19$ GB
- **Redis 集群内存需求**: **~20-30 GB**（含 overhead 和副本）

**带宽估算 (Bandwidth Estimation)**

- 每次限流检查的 Redis 命令大小: ~100 bytes（请求） + ~50 bytes（响应）
- **Redis 网络带宽**: $350{,}000 \times 150 = 52.5$ MB/s（峰值）-- 非瓶颈

**缓存估算 (Cache / Memory Estimation)**

- 限流规则数量: 假设 100-1000 条规则
- 每条规则大小: ~200 bytes
- **规则缓存内存**: < 200 KB -- 完全可以放在 Gateway 本地内存

### 核心算法对比 (Rate Limiting Algorithms)

#### 算法 1: 令牌桶 (Token Bucket)

**原理**: 桶中持有令牌，每个请求消耗一个令牌。令牌以固定速率补充。桶满时多余令牌丢弃。

- **参数**: 桶容量 $b$（最大突发量），令牌补充速率 $r$（每秒补充数）
- **允许条件**: 当前令牌数 $\geq 1$

**令牌计算（惰性补充）**:

$$\text{tokens} = \min\left(b, \; \text{tokens\_prev} + r \times (t_{\text{now}} - t_{\text{last\_refill}})\right)$$

```python
def token_bucket_check(key, capacity, rate):
    # Check if request is allowed under token bucket
    now = time.time()
    # Redis HASH: {tokens: float, last_refill: float}
    data = redis.hgetall(key)
    tokens = float(data.get("tokens", capacity))
    last_refill = float(data.get("last_refill", now))

    # Refill tokens
    elapsed = now - last_refill
    tokens = min(capacity, tokens + rate * elapsed)

    if tokens >= 1:
        tokens -= 1
        redis.hset(key, mapping={"tokens": tokens, "last_refill": now})
        return True  # Allowed
    else:
        redis.hset(key, mapping={"last_refill": now})
        return False  # Denied
```

**优点**: 允许突发流量（burst）；内存高效（每 key 仅 2 个值）

**缺点**: 参数调优不直观（capacity 和 rate 的关系）

#### 算法 2: 固定窗口计数器 (Fixed Window Counter)

**原理**: 将时间划分为固定大小的窗口（如每分钟一个窗口），每个窗口维护一个计数器。

$$\text{window\_key} = \text{client\_id} + \text{":"}  + \left\lfloor \frac{t_{\text{now}}}{\text{window\_size}} \right\rfloor$$

$$\text{allowed} = (\text{counter}[\text{window\_key}] < \text{limit})$$

```
# Redis 命令（原子操作）
INCR  rl:user:123:202604081530    # 自增计数器
EXPIRE rl:user:123:202604081530 60  # 设置 60 秒过期
```

**优点**: 实现极简单（Redis INCR + EXPIRE）；内存高效

**缺点**: **窗口边界问题** -- 用户可以在窗口交界处发出 2 倍限额的请求。例如，限额 100/min，用户在 0:59 发 100 个请求，在 1:00 又发 100 个请求 -- 实际 2 秒内通过了 200 个请求。

#### 算法 3: 滑动窗口日志 (Sliding Window Log)

**原理**: 在 Redis Sorted Set 中记录每个请求的时间戳，每次检查时移除窗口外的旧记录，检查集合大小是否超限。

$$\text{allowed} = \left\lvert \{ ts \in \text{log} \mid ts > t_{\text{now}} - w \} \right\rvert < \text{limit}$$

```
# Redis 命令
ZREMRANGEBYSCORE rl:user:123 0 (now - window_size)   # 移除过期记录
ZADD rl:user:123 now now                              # 添加当前请求
ZCARD rl:user:123                                     # 统计窗口内请求数
EXPIRE rl:user:123 window_size                        # 设置过期
```

**优点**: 精确，无窗口边界问题

**缺点**: 内存消耗大（每个请求存一个时间戳）；高 QPS 时 Sorted Set 操作较慢

#### 算法 4: 滑动窗口计数器 (Sliding Window Counter) -- 推荐

**原理**: 结合固定窗口和滑动窗口的优点。维护当前窗口和前一个窗口的计数器，用加权计算近似滑动窗口的请求数。

$$\text{count} = \text{count\_prev} \times (1 - \text{elapsed\_ratio}) + \text{count\_curr}$$

其中:

$$\text{elapsed\_ratio} = \frac{t_{\text{now}} - t_{\text{window\_start}}}{\text{window\_size}}$$

**示例**: 限额 100/min，上一分钟有 80 个请求，当前分钟已过 40 秒（elapsed_ratio = 40/60 = 0.667）有 30 个请求:

$$\text{count} = 80 \times (1 - 0.667) + 30 = 80 \times 0.333 + 30 = 26.67 + 30 = 56.67$$

当前估算请求数 ~57，低于 100，允许通过。

**优点**: 近似精确（误差 < 1%）；内存高效（每 key 仅 2 个计数器）；无窗口边界突刺

**缺点**: 是近似值而非精确值

### 算法选择总结 (Algorithm Comparison)

| 维度 | Token Bucket | Fixed Window | Sliding Log | Sliding Counter |
|------|-------------|-------------|-------------|-----------------|
| 精确度 | 精确 | 有边界问题 | 精确 | 近似（误差 < 1%） |
| 内存 | 低（2 值/key） | 低（1 值/key） | 高（每请求 1 记录） | 低（2 值/key） |
| 突发流量 | 允许（可控） | 边界突刺 | 不允许 | 不允许 |
| 实现复杂度 | 中等 | 极低 | 中等 | 低 |
| **推荐场景** | API Gateway 全局限流 | 内部服务间限流 | 需要精确审计 | **通用场景（推荐）** |
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Deep Dive - Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints & Deep Dive)

### 具体规模数据 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 5000 万 |
| 峰值 QPS（API 请求） | 350,000 |
| 限流检查延迟（P99） | < 1ms |
| 活跃限流 key 数 | ~2.5 亿 |
| Redis 集群内存 | ~20-30 GB |
| Redis 分片数 | 4-8 个 |
| 限流规则数 | 100-1000 条 |
| 规则更新延迟 | < 1 秒（watch 模式） |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **Redis 主节点** | 限流计数丢失，短暂超限 | Redis Sentinel 自动切换（< 30 秒），切换期间 fail-open |
| **API Gateway** | 全部流量中断 | 多实例 + LB 健康检查，自动摘除故障实例 |
| **Rule Config Store** | 无法更新规则，但不影响现有限流 | Gateway 本地缓存兜底，Config Store 故障时使用最后一次同步的规则 |
| **Redis Cluster 整体不可用** | 所有限流检查失败 | **Fail-open**: 放行所有请求 + 紧急告警 + 本地内存限流降级 |

### 多数据中心 / 跨区域 (Multi-Datacenter Considerations)

**方案 A: 本地限流（每 DC 独立）-- 推荐**

- 每个数据中心有独立的 Redis 集群
- 限流配额按 DC 拆分（如全局限额 1000/min，3 个 DC 各分 333/min）
- **优点**: 无跨 DC 网络调用，延迟最低
- **缺点**: 用户在不同 DC 间切换时，限额不共享（可能多用或少用）
- 适合场景: 大多数 API 限流（精度要求非严格）

**方案 B: 全局限流（跨 DC 同步）**

- 所有 DC 共享一个逻辑 Redis 集群
- 使用 **CRDTs (Conflict-free Replicated Data Types)** 或 **Gossip 协议** 同步计数器
- **优点**: 全局精确
- **缺点**: 跨 DC 网络延迟（50-200ms），可能使限流检查延迟超出 1ms SLA
- 适合场景: 安全敏感的全局限流（如登录尝试限制）

**实际做法: 混合方案**

- 大部分 API: **本地限流**（性能优先）
- 安全相关（登录、密码重置）: **全局限流**（精确性优先）
- 使用 **异步同步** 定期（每 5-10 秒）跨 DC 汇总计数，做到"大致全局精确"

### 高并发处理 (High Concurrency Handling)

**竞态条件 (Race Condition)**

多个 Gateway 实例并发读写同一个 key 时，可能出现 TOCTOU (Time-of-Check-Time-of-Use) 问题:

```
Thread A: GET counter -> 99
Thread B: GET counter -> 99
Thread A: SET counter -> 100 (allowed, limit=100)
Thread B: SET counter -> 100 (allowed, but should be denied!)
```

**解决方案: Redis Lua 脚本**

将检查和更新合并为**原子操作**:

```lua
-- sliding_window_counter.lua (原子执行)
local key_curr = KEYS[1]
local key_prev = KEYS[2]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local curr_count = tonumber(redis.call("GET", key_curr) or "0")
local prev_count = tonumber(redis.call("GET", key_prev) or "0")

local window_start = math.floor(now / window) * window
local elapsed_ratio = (now - window_start) / window
local estimated = prev_count * (1 - elapsed_ratio) + curr_count

if estimated < limit then
    redis.call("INCR", key_curr)
    redis.call("EXPIRE", key_curr, window * 2)
    return {1, limit - math.ceil(estimated) - 1}  -- {allowed, remaining}
else
    return {0, 0}  -- {denied, remaining=0}
end
```

**连接池 (Connection Pooling)**
- 每个 Gateway 实例到 Redis 的连接池: 50-100 个连接
- 使用 pipeline 批量发送命令，减少 RTT

**本地缓存热点限流 (Local Cache for Hot Keys)**
- 对于高频限流 key（如系统级全局限额），在 Gateway 本地维护计数器
- 定期（每 100ms）与 Redis 同步，减少 Redis 压力
- 本地计数可能导致 1-2% 的精度损失，对大多数场景可接受

### 监控与告警 (Monitoring & Alerting)

| 指标 | 正常范围 | 告警阈值 |
|------|----------|----------|
| 限流检查 P99 延迟 | < 1ms | > 5ms |
| Redis 分片 CPU | < 40% | > 70% |
| 限流拒绝率（429 比例） | < 1% | > 5%（规则可能过严或遭受攻击） |
| Redis 可用性 | 100% | 任何分片不可用 |
| 规则同步延迟 | < 1s | > 10s |
| 内存使用率 | < 60% | > 80% |
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| 限流算法 | Token Bucket | Sliding Window Counter | **Sliding Window Counter** -- 近似精确（误差 < 1%），内存高效，无窗口边界问题；Token Bucket 适合需要控制突发流量的场景 |
| 计数器存储 | Redis | 本地内存 | **Redis** -- 分布式环境下多 Gateway 实例需要共享计数器；本地内存仅适合单实例部署或极端低延迟场景 |
| 故障模式 | Fail-open | Fail-closed | **Fail-open** -- 限流器故障时放行请求，避免所有用户受影响；后端服务本身应有过载保护作为兜底 |
| 规则存储 | 文件 (YAML) | 配置中心 (etcd) | **etcd** -- 支持运行时热更新和 watch 通知（< 1 秒生效）；YAML 文件需要重启或信号触发重载 |
| 限流粒度 | 全局精确 | 每 DC 独立 | **每 DC 独立 + 安全场景全局** -- 大部分 API 限流不需要跨 DC 精确，性能优先；登录等安全场景用全局限流保证精确 |

### 一致性 vs. 可用性 (Consistency vs. Availability)

限流器是一个典型的 **AP 优先** 系统（**CAP 定理 (CAP Theorem)** 应用）：

- **可用性优先**: 限流器故障时放行（fail-open），宁可短暂超限也不拒绝正常用户
- **允许近似**: 分布式环境下，多 Gateway 并发检查同一 key 可能导致实际放行量比限额多 1-3%，这在大多数场景可接受
- **安全场景例外**: 登录尝试等安全限流需要更强的一致性（全局 Redis 或强一致 counter），宁可误拒也不放行

### 成本 vs. 性能 (Cost vs. Performance)

- **Redis vs. 本地内存**: Redis 增加了网络 RTT（~0.5ms），但提供分布式一致性。对于单实例服务，本地内存限流零延迟且零成本。
- **Lua 脚本 vs. 多次 Redis 调用**: Lua 脚本原子执行减少竞态，但增加 Redis 服务端 CPU。对于简单场景（Fixed Window），单次 INCR 就够了。
- **日志记录**: 每次请求都写限流日志成本高（IO + 存储），可改为采样记录（1% 采样）或只记录被拒绝的请求。

### 复杂度 vs. 简洁性 (Complexity vs. Simplicity)

- **算法选择**: Sliding Window Counter 比 Fixed Window 稍复杂，但消除了窗口边界问题。如果精度不重要（内部服务间限流），Fixed Window 的 `INCR + EXPIRE` 两行命令就够了。
- **规则引擎**: 简单场景只需 `{key, limit, window}` 三元组；复杂场景需要条件规则（不同用户等级不同限额），引入规则引擎增加了延迟和维护成本。

### 10x / 100x 规模下的变化 (What Changes at Scale)

**10x (5 亿 DAU, 350 万 QPS)**:
- 单 Redis Cluster 不够 -> 按 key hash 分成多个独立 Redis Cluster
- 规则数增长 -> 规则匹配从线性扫描改为 **Trie 树 / 前缀匹配**，O(n) -> O(k)
- 限流日志量爆增 -> 改为采样记录 + 只记录 deny 事件

**100x (50 亿 DAU, 3500 万 QPS)**:
- Redis 延迟不可接受 -> 核心路径改为 **本地内存限流** + 定期 Redis 同步
- 引入 **两级限流**: L1 = 本地内存（亚微秒），L2 = Redis（亚毫秒，用于兜底精确）
- 规则引擎独立为微服务，Gateway 只持有编译后的规则（状态机 / 位图）
"""

# ---------------------------------------------------------------------------
# S7: Defense Q&A (Interviewer Follow-up)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

**Q: 如果 Redis 完全宕机了，你的限流器会怎样？后端服务会被打垮吗？**

> **承认局限**: Redis 不可用时，所有限流检查都会失败，如果选择 fail-closed 则所有
> 用户被拒绝，如果选择 fail-open 则后端失去流量保护。
>
> **缓解措施**: 分层防御:
>
> 1. **Fail-open + 本地降级**: Redis 不可用时切换到**本地内存计数器**。每个
>    Gateway 实例独立限流，精度下降（无法跨实例统计）但基本保护仍在。
>    配额按实例数均分：全局限额 1000/min，10 个实例则每实例 100/min。
> 2. **Redis Sentinel 自动切换**: 主节点故障在 < 30 秒内切换到从节点
> 3. **后端自我保护**: 后端服务应有自己的过载保护（如线程池满时拒绝、
>    **Circuit Breaker (熔断器)** 等），限流器是第一道防线而非唯一防线
>
> **数据**: Redis Sentinel 切换通常 < 15 秒完成。本地限流降级模式下，限流精度
> 下降约 N 倍（N = Gateway 实例数），但仍能阻止极端滥用。

---

**Q: 滑动窗口计数器的误差有多大？在什么情况下误差会变得不可接受？**

> **承认局限**: 滑动窗口计数器使用上一窗口的计数做线性加权，假设请求在窗口内
> 均匀分布。如果请求集中在窗口末尾，实际误差可能较大。
>
> **缓解措施**:
>
> 1. **理论最大误差**: Cloudflare 的研究表明，滑动窗口计数器的误差上限约为
>    $\frac{\text{limit}}{N}$，其中 $N$ 是窗口的细分数。单窗口近似时最大误差 < 限额的 1%。
> 2. **实际影响**: 对于限额 100/min 的规则，最大多放 1 个请求。对于限额 10/min 的
>    严格规则（如密码重置），误差比例更高 -> 建议改用 **Sliding Window Log**（精确）。
> 3. **可调精度**: 将一个大窗口拆成多个子窗口（如 1 分钟拆成 6 个 10 秒窗口），
>    用多段加权代替两段加权，精度提升但内存和计算成本也增加。
>
> **数据**: 在 Cloudflare 的生产数据中，滑动窗口计数器的实际误差 < 0.003%，远低于
> 理论上限。

---

**Q: 恶意用户不断更换 IP 来绕过限流怎么办？**

> **承认局限**: IP 限流确实容易被 VPN、代理、Tor 网络绕过。单纯按 IP 限流
> 无法对抗分布式攻击。
>
> **缓解措施**: 多维度组合限流:
>
> 1. **IP + 用户 ID 组合**: 已登录用户按 user ID 限流（无法通过换 IP 绕过）
> 2. **设备指纹 (Device Fingerprint)**: 基于浏览器/设备特征生成指纹，
>    即使换 IP 也能关联到同一设备
> 3. **行为分析**: 异常流量模式检测 -- 短时间内来自不同 IP 但请求模式相同
>    （如相同 User-Agent、相同 API 调用序列）-> 标记为可疑并限流
> 4. **CAPTCHA 降级**: 触发限流的请求不直接拒绝，而是要求验证码验证
> 5. **上游防护**: 真正的 DDoS 攻击应由 **CDN/WAF** 层处理（如 Cloudflare、
>    AWS Shield），限流器处理的是应用层滥用
>
> **数据**: 多维度组合限流可将绕过成功率从 IP-only 的 ~30% 降低到 < 2%。

---

**Q: 如果某天流量突然 10 倍增长（如产品上了热搜），限流器会不会把正常用户也拦住？**

> **承认局限**: 静态限流规则无法适应流量突增，可能在流量高峰时误拒正常用户。
>
> **缓解措施**:
>
> 1. **动态限流 (Dynamic / Adaptive Rate Limiting)**: 基于后端服务的实时健康指标
>    （CPU、延迟、队列深度）动态调整限额。后端健康时放宽限额，后端过载时收紧。
> 2. **限额预案 (Rate Limit Profiles)**: 预定义多套限流规则（normal / high / emergency），
>    通过管理 API 一键切换。运营团队在预期流量高峰前提前切换。
> 3. **突发容忍 (Burst Tolerance)**: Token Bucket 算法天然支持短时突发。
>    设置合理的桶容量（如限额 100/min，桶容量设为 200），允许短时 2 倍突发。
> 4. **优先级限流 (Priority-based)**: 付费用户和核心 API 享有更高限额，
>    流量高峰时优先保障高优先级流量。
>
> **数据**: 动态限流在 Netflix 的实践中，将高峰期误拒率从 3.2% 降低到 0.1%，
> 同时后端过载事件减少 85%。

---

**Q: 如何测试限流器的正确性和性能？上线前怎么验证？**

> **承认局限**: 限流器的边界条件多（窗口边界、并发竞态、时钟偏差），单元测试
> 难以覆盖所有场景。
>
> **缓解措施**:
>
> 1. **Shadow Mode (影子模式)**: 上线初期限流器只记录不拒绝，对比实际流量和
>    限流决策，验证规则是否合理。观察 1-2 周后再切换到 enforce 模式。
> 2. **Canary 发布**: 先在 5% 的 Gateway 实例上启用限流，观察 429 率和
>    用户投诉，逐步扩大到 100%。
> 3. **压力测试**: 使用 **wrk** / **Locust** 模拟 50 万 QPS，验证限流精度
>    和 Redis 延迟。重点测试窗口边界（时钟刚好跨窗口时的行为）。
> 4. **混沌测试 (Chaos Testing)**: 故意断开 Redis 连接，验证 fail-open 行为
>    和本地降级是否正常工作。
>
> **数据**: Shadow Mode 通常运行 7-14 天，期间发现的规则问题平均 3-5 个（限额
> 过严或过松）。上线后 429 误拒率目标 < 0.1%。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "Rate Limiter 的核心目标是保护后端服务免受流量过载和滥用。我想先确认几点：
> 限流器部署在哪里？我假设是在 API Gateway 层。需要支持哪些维度的限流？
> 按用户、IP、还是 API 端点？对精度的要求是什么？允许在分布式环境下有 1-2%
> 的误差吗？限流器故障时是 fail-open 还是 fail-closed？"
>
> 列出 FR: 请求计数、限流决策、规则引擎、HTTP 429 响应头、多维度限流。
> 列出 NFR: 99.99% 可用性、P99 < 1ms、允许轻微不精确、fail-open。
> 明确 Out of Scope: DDoS 防护（CDN/WAF 层）、用户认证、计费系统。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "架构很简洁: Client -> LB -> API Gateway (内嵌 Rate Limiter Middleware)
> -> Backend Services。限流计数器存在 Redis Cluster 里，规则存在 etcd 配置中心，
> Gateway 本地缓存规则。每次请求: 提取 key，查本地规则，调 Redis 原子检查。
> Redis 不可用时 fail-open，降级到本地内存限流。"
>
> "选择 Redis 因为需要亚毫秒级原子操作（INCR + EXPIRE）且多 Gateway 实例
> 需要共享计数器。规则用 etcd 因为需要热更新能力。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: 限流算法对比与选择 (8-10 分钟)**
> "四种主流算法: Token Bucket、Fixed Window、Sliding Window Log、Sliding
> Window Counter。Fixed Window 最简单但有窗口边界问题 -- 用户可以在窗口交界处
> 突发 2 倍流量。Token Bucket 允许受控突发。Sliding Window Log 精确但内存消耗大。
> 我推荐 Sliding Window Counter -- 用当前和上一窗口的计数加权近似，误差 < 1%，
> 内存只需 2 个计数器/key，无窗口边界突刺。"

**重点 2: 分布式竞态条件与解决 (5-8 分钟)**
> "多个 Gateway 并发检查同一 key 时有 TOCTOU 问题。解决方案是 Redis Lua 脚本，
> 将 GET + 判断 + INCR 合并为原子操作。Redis 单线程模型保证 Lua 脚本执行期间
> 无并发干扰。对于极高 QPS 的热点 key，在 Gateway 本地维护计数器，定期同步到
> Redis，牺牲 1-2% 精度换取零网络延迟。"

**重点 3: 故障处理与多 DC 部署 (5-8 分钟)**
> "Redis 宕机时 fail-open + 本地内存降级。后端自身应有过载保护作为兜底。
> 多 DC 部署: 大部分 API 限流用本地独立 Redis（性能优先），安全敏感限流（如
> 登录尝试）用全局 Redis 或异步同步。混合方案兼顾性能和安全。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: 精确性 vs 性能（Sliding Counter 牺牲 < 1% 精度换取低内存和高性能），
> fail-open vs fail-closed（选 fail-open，后端有兜底保护），本地限流 vs 全局限流
> （混合方案）。10x 规模需要多 Redis Cluster 分片和本地缓存。100x 规模需要
> 两级限流（本地 + Redis）和规则引擎独立化。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 动态自适应限流（基于后端健康指标动态调整限额），
> (2) 限流日志分析管道（用于规则调优和异常检测），(3) 多租户限流隔离（不同租户
> 的限流不相互影响）。"

### 55-60 分钟: 向面试官提问

> "你们在生产中使用哪种限流算法？有没有遇到过限流误拒影响用户体验的情况？
> 你们怎么处理突发流量和限流规则的动态调整？"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计 API 限流器 -- 保护后端免受过载和滥用。P99 < 1ms，
   分布式环境，fail-open。

2. **(60 秒) 架构**: API Gateway 内嵌限流中间件。Redis Cluster 存计数器（原子 INCR），
   etcd 存规则（热更新）。Redis Lua 脚本解决竞态。Redis 故障时降级到本地内存限流。

3. **(60 秒) 核心算法**: 推荐 Sliding Window Counter -- 两个计数器加权近似滑动窗口，
   误差 < 1%，内存 O(1)/key。备选 Token Bucket 用于需要突发控制的场景。

4. **(30 秒) 扩展**: 多 DC 用本地 Redis（API 限流）+ 全局 Redis（安全限流）。
   10x 规模加分片和本地缓存，100x 规模引入两级限流（本地 + Redis）。
"""


def populate_interview_rate_limiter() -> None:
    """Create or update the interview-rate-limiter record with all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

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

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_interview_rate_limiter()
