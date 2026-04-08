"""Populate interview-url-shortener system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a URL Shortener.
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

SLUG = "interview-url-shortener"
TITLE = "Design a URL Shortener"
DISPLAY_ORDER = 100

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **TinyURL** / **bit.ly** 的短链接服务：用户提交一个长 URL，系统
返回一个唯一的短 URL；当访问短 URL 时，系统将请求重定向到原始长 URL。

### 功能性需求 (Functional Requirements)

1. **URL 缩短 (Shorten)**：给定一个长 URL，生成一个唯一的短链接
2. **URL 重定向 (Redirect)**：访问短链接时，重定向到原始长 URL
3. **自定义别名 (Custom Alias)**：用户可选择自定义短链接后缀（如 `short.url/my-brand`）
4. **过期 / TTL**：短链接可设置过期时间，过期后返回 404
5. **分析统计 (Analytics)**：记录每次点击的基本信息（时间、来源、地理位置）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（重定向是核心路径，必须极高可用）
- **延迟 (Latency)**：重定向 P99 < 10ms（读路径）；缩短 P99 < 100ms（写路径）
- **一致性 (Consistency)**：短链接创建后必须立即可用（强一致）；分析数据可接受最终一致
- **可扩展性 (Scalability)**：支撑 1 亿 DAU，读写比 100:1
- **持久性 (Durability)**：短链接一旦创建，在 TTL 内不可丢失

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 短链接长度有限制吗？** -- WHY: 决定编码空间大小和哈希策略。7 字符 Base62 = $62^7 \approx 3.5 \times 10^{12}$ 个唯一值，足够使用数十年。

2. **Q: 是否需要支持同一长 URL 的去重（相同长 URL 返回相同短链接）？** -- WHY: 如果需要去重，需要额外的长 URL -> 短 URL 反向索引，增加写路径复杂度。

3. **Q: 重定向应使用 301 还是 302？** -- WHY: **301 (Moved Permanently)** 浏览器会缓存，减少服务端流量但丢失分析数据；**302 (Found)** 每次都回到服务端，保留完整分析。如果分析重要，选 302。

4. **Q: 短链接是否需要支持删除/更新？** -- WHY: 如果支持更新，缓存失效策略会更复杂（需要主动清除 CDN 缓存）。

5. **Q: 分析需要实时还是近实时？** -- WHY: 实时分析需要流处理（如 Kafka + Flink）；近实时可用批处理（更简单）。

6. **Q: 预期的 URL 创建速率是多少？** -- WHY: 影响 ID 生成器的吞吐量需求和数据库写入压力。

7. **Q: 是否需要防滥用（恶意 URL 检测）？** -- WHY: 如果需要，写路径需要集成 URL 安全检查服务（如 Google Safe Browsing API），增加写延迟。

### 范围外 (Out of Scope)

- 用户认证 / 账户系统（假设已有）
- 付费计划 / 配额管理
- URL 内容预览（Open Graph 元数据获取）
- 多语言 / 国际化界面
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Client (Browser/App)
    |
    v
[Load Balancer / API Gateway]
    |
    +---> [URL Shortening Service]  (Write Path)
    |         |
    |         v
    |     [ID Generator]
    |         |
    |         v
    |     [Database - Primary]
    |
    +---> [Redirect Service]  (Read Path)
              |
              v
          [Cache Layer (Redis)]
              |  (cache miss)
              v
          [Database - Replica]
```

### 服务划分 (Service Breakdown)

| 服务 | 职责 | 特点 |
|------|------|------|
| **API Gateway** | 路由、限流、认证 | 无状态，水平扩展 |
| **URL Shortening Service** | 接收长 URL，生成短链接，写入 DB | 写路径，低 QPS |
| **Redirect Service** | 接收短链接请求，查找原始 URL，返回重定向 | 读路径，高 QPS，对延迟极敏感 |
| **ID Generator** | 生成全局唯一短链接 ID | 核心组件，决定短链接格式 |
| **Analytics Service** | 异步记录点击事件，生成报表 | 异步处理，最终一致 |

### 数据库选择 (Database Choice)

**主存储: 关系型数据库 (MySQL / PostgreSQL)**
- 理由：URL 映射是简单的 KV 结构，但需要强一致性保证（创建后立即可读）
- 短链接列加唯一索引，保证无冲突
- 如果规模极大（数十亿条记录），可考虑 **NoSQL (DynamoDB / Cassandra)** 以获得更好的水平扩展性

**缓存层: Redis**
- 热门短链接缓存，减少 DB 读取
- 读写比 100:1，缓存命中率预期 > 80%

**分析存储: 列式数据库 / 消息队列**
- 点击事件先写入 **Kafka**，通过流处理写入 **ClickHouse** 或 **Cassandra**
- 支持高写入吞吐量和时间范围查询

### 通信模式 (Communication Patterns)

- **写路径**: 同步 REST API（创建短链接后同步返回结果）
- **读路径**: 同步 HTTP 重定向（302）
- **分析**: 异步消息队列（Kafka）-- 重定向服务发出点击事件，Analytics Service 异步消费

### 数据分区策略 (Data Partitioning)

- **分区键**: 短链接 hash 的前几位（均匀分布）
- **范围分区 vs. 哈希分区**: 哈希分区更适合（短链接本身已是 hash，天然均匀分布）
- 避免热点：热门短链接通过缓存层吸收流量，不会压垮单个分区
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & API Design (5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (API Endpoints)

**1. 创建短链接 (Create Short URL)**

```
POST /api/v1/urls
Content-Type: application/json

Request:
{
  "long_url": "https://example.com/very/long/path?param=value",
  "custom_alias": "my-link",     // optional
  "expires_at": "2026-12-31T23:59:59Z"  // optional
}

Response: 201 Created
{
  "short_url": "https://short.url/aB3kF9x",
  "long_url": "https://example.com/very/long/path?param=value",
  "expires_at": "2026-12-31T23:59:59Z",
  "created_at": "2026-04-08T10:00:00Z"
}

Error: 409 Conflict (custom alias already taken)
Error: 400 Bad Request (invalid URL format)
```

**2. 重定向 (Redirect)**

```
GET /{short_code}

Response: 302 Found
Location: https://example.com/very/long/path?param=value

Error: 404 Not Found (short code not found or expired)
```

**3. 获取分析数据 (Get Analytics)**

```
GET /api/v1/urls/{short_code}/stats

Response: 200 OK
{
  "short_code": "aB3kF9x",
  "total_clicks": 15234,
  "clicks_by_day": [...],
  "top_referrers": [...],
  "top_countries": [...]
}
```

### 核心数据模型 (Core Data Models)

**urls 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | BIGINT (PK) | 自增主键 |
| `short_code` | VARCHAR(10) | 短链接编码，唯一索引 |
| `long_url` | TEXT | 原始长 URL |
| `user_id` | BIGINT | 创建者（可为空） |
| `expires_at` | TIMESTAMP | 过期时间（可为空） |
| `created_at` | TIMESTAMP | 创建时间 |

**click_events 表**（分析用，写入量大）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | BIGINT (PK) | 事件 ID |
| `short_code` | VARCHAR(10) | 被点击的短链接 |
| `clicked_at` | TIMESTAMP | 点击时间 |
| `ip_address` | VARCHAR(45) | 客户端 IP |
| `user_agent` | TEXT | 浏览器信息 |
| `referrer` | TEXT | 来源页面 |
| `country` | VARCHAR(2) | 地理位置（GeoIP 解析） |

### 读路径 (Read Path): 短链接重定向

1. 客户端发送 `GET /aB3kF9x` 请求
2. **API Gateway** 路由到 Redirect Service
3. Redirect Service 在 **Redis 缓存** 中查找 `short_code -> long_url`
4. **缓存命中**: 直接返回 302 重定向（P99 < 5ms）
5. **缓存未命中**: 查询 **DB 读副本**，获取 `long_url`
6. 检查 `expires_at`：如果已过期，返回 404
7. 将结果写入 Redis 缓存（TTL = 24h）
8. 返回 302 重定向
9. **异步**: 发送点击事件到 **Kafka** 队列（不阻塞重定向响应）

### 写路径 (Write Path): 创建短链接

1. 客户端发送 `POST /api/v1/urls` 请求
2. **输入校验**: 验证 URL 格式、长度限制
3. **自定义别名处理**:
   - 如果提供了 `custom_alias`：检查唯一性，可用则使用
   - 如果未提供：调用 **ID Generator** 生成短码
4. **ID 生成**（详见 formulas 部分）:
   - 方案 A: 分布式自增 ID -> Base62 编码
   - 方案 B: 长 URL 的 MD5/SHA256 hash 取前 7 字符
5. 写入 **主数据库**（带唯一约束）
6. 如果写入冲突（hash 碰撞），重试（附加随机后缀或重新生成）
7. **预热缓存**: 将新映射写入 Redis
8. 返回 201 响应

### 异步路径 (Async Path): 分析管道

1. Redirect Service 每次重定向后发送点击事件到 **Kafka**
2. **Stream Processor (Flink/Spark Streaming)** 消费事件
3. 实时聚合（按分钟/小时窗口）写入 **ClickHouse**
4. 批量聚合（按天/周）写入 **分析数据库** 供 Dashboard 查询
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms (Back-of-Envelope Estimation -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

**流量估算 (Traffic Estimation)**

- **DAU (Daily Active Users)**: 1 亿
- **每用户每日创建短链接数**: 0.1（大部分用户只读）
- **每日写入 QPS**: $\frac{1 \times 10^8 \times 0.1}{86400} \approx 116$ QPS
- **峰值写入 QPS**: $116 \times 3 \approx 350$ QPS（3 倍峰值系数）
- **读写比**: 100:1
- **每日读取 QPS**: $116 \times 100 = 11{,}600$ QPS
- **峰值读取 QPS**: $11{,}600 \times 3 \approx 35{,}000$ QPS

**存储估算 (Storage Estimation)**

- 每条 URL 记录大小:
  - `short_code`: 7 bytes
  - `long_url`: 平均 200 bytes
  - `user_id` + `timestamps` + 其他: ~50 bytes
  - **每条记录: ~257 bytes, 取 ~500 bytes（含索引开销）**
- **每日新增记录**: $1 \times 10^8 \times 0.1 = 10^7$（1000 万条）
- **每日存储增长**: $10^7 \times 500 = 5$ GB/天
- **5 年存储**: $5 \times 365 \times 5 = 9.125$ TB
- 加上副本和索引，总存储约 **30 TB**

**带宽估算 (Bandwidth Estimation)**

- 读请求平均响应大小: ~500 bytes（302 响应 + headers）
- **读带宽**: $35{,}000 \times 500 = 17.5$ MB/s（峰值）
- **写带宽**: $350 \times 500 = 175$ KB/s（峰值）-- 写带宽可忽略

**缓存估算 (Cache / Memory Estimation)**

- **80-20 法则**: 20% 的 URL 承载 80% 的流量
- 每日不同 URL 访问量: 假设 1000 万个不同短链接被访问
- 缓存 20% 热门 URL: $10^7 \times 0.2 \times 500 = 1$ GB
- Redis 集群内存需求: **~2-5 GB**（含 overhead）-- 非常小，完全可行

### 核心算法: 短链接 ID 生成 (Short URL ID Generation)

#### 方案 A: 自增 ID + Base62 编码 (推荐)

使用分布式 ID 生成器（如 **Snowflake** 风格）生成全局唯一自增 ID，然后进行 Base62 编码。

**Base62 编码**: 使用字符集 `[0-9a-zA-Z]`，共 62 个字符。

$$\text{encoded} = \text{Base62}(\text{unique\_id})$$

- 7 字符 Base62 的地址空间: $62^7 = 3{,}521{,}614{,}606{,}208 \approx 3.5 \times 10^{12}$
- 以每日 1000 万条的速率，可使用 $\frac{3.5 \times 10^{12}}{10^7 \times 365} \approx 960$ 年

**Base62 编码算法**:

```python
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num: int) -> str:
    if num == 0:
        return CHARSET[0]
    result = []
    while num > 0:
        result.append(CHARSET[num % 62])
        num //= 62
    return "".join(reversed(result))
```

**优点**: 无冲突（ID 唯一），短码长度可预测，天然递增（可选择是否暴露顺序）

**缺点**: 需要分布式 ID 生成器（单点、协调开销）；顺序 ID 可能被猜测

#### 方案 B: Hash + 截断

对长 URL 进行 hash（**MD5** 或 **SHA-256**），取前 7 个字符作为短码。

$$\text{short\_code} = \text{Base62}(\text{MD5}(\text{long\_url})[:43\text{bits}])$$

- 43 bits 对应 $2^{43} \approx 8.8 \times 10^{12}$ 个值，映射到 7 字符 Base62
- **碰撞概率** (Birthday Problem): 当有 $n$ 个 URL 时，碰撞概率约为:

$$P(\text{collision}) \approx 1 - e^{-\frac{n^2}{2 \times 62^7}}$$

- 当 $n = 10^9$（10 亿条）时: $P \approx 1 - e^{-\frac{10^{18}}{7 \times 10^{12}}} \approx 1 - e^{-143} \approx 1$
- **结论**: 10 亿条时碰撞几乎必然发生，必须有碰撞处理机制

**碰撞处理**: DB 写入时检查唯一约束，冲突则追加随机字符重试（最多 3 次）

**优点**: 无需中央 ID 生成器，完全无状态

**缺点**: 碰撞处理增加写延迟和复杂度；相同长 URL 总是生成相同短码（可能是优点也可能是缺点）

#### 方案选择

| 维度 | 方案 A (ID + Base62) | 方案 B (Hash) |
|------|---------------------|---------------|
| 碰撞 | 零碰撞 | 需处理碰撞 |
| 去重 | 不同 ID 对应不同短码 | 天然去重 |
| 可预测性 | 顺序可猜测（可洗牌） | 不可预测 |
| 依赖 | 需要 ID 生成器 | 无状态 |
| **推荐场景** | **通用场景（推荐）** | 需要去重且写入量低时 |

### 分布式 ID 生成器设计 (Distributed ID Generator)

推荐使用 **Snowflake** 风格的 ID 生成器:

```
| 1 bit (unused) | 41 bits (timestamp) | 5 bits (datacenter) | 5 bits (machine) | 12 bits (sequence) |
```

- **41 bits timestamp**: 支持约 69 年
- **5 + 5 bits**: 最多 32 个数据中心 x 32 台机器 = 1024 个节点
- **12 bits sequence**: 每毫秒每节点 4096 个 ID
- **总吞吐**: $1024 \times 4096 \times 1000 = 4.2 \times 10^9$ ID/秒 -- 远超需求
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Deep Dive - Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints & Deep Dive)

### 具体规模数据 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 1 亿 |
| 峰值读 QPS | 35,000 |
| 峰值写 QPS | 350 |
| 总 URL 记录数（5 年） | ~18 亿条 |
| 总存储（含副本） | ~30 TB |
| 缓存大小 | 2-5 GB (Redis) |
| 服务器数量 | 读服务 ~10 台，写服务 ~3 台 |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **ID Generator** | 无法创建新短链接 | 多节点 Snowflake（每节点独立 worker ID） |
| **Database Primary** | 写入中断 | 主从切换（自动 failover），如 MySQL Group Replication |
| **Redis Cache** | 读延迟飙升（回落到 DB） | Redis Sentinel / Redis Cluster（多节点） |
| **Load Balancer** | 全部流量中断 | 双活 LB + DNS 健康检查 |
| **Kafka** | 分析事件丢失 | 多 broker 集群 + 副本因子 3 |

### 多数据中心 / 跨区域 (Multi-Datacenter Considerations)

**部署模式: Active-Active（双活）**

- **读路径**: 每个数据中心有本地 Redis 缓存 + DB 读副本，用户就近读取
- **写路径**: 写入路由到最近的数据中心，通过 **异步复制** 同步到其他数据中心
- **数据复制策略**: **异步复制**（写入后不等待其他数据中心确认）
  - 理由：短链接创建后用户通常不会立即在另一个大洲使用它；99.9% 的读取发生在创建后数秒以上，此时异步复制已完成
  - 复制延迟预期: < 200ms（跨洋）

**DNS 路由: GeoDNS**

- 使用 **GeoDNS** 将用户路由到最近的数据中心
- 健康检查: 如果某个数据中心不可用，DNS 自动切换到备用

**冲突解决 (Conflict Resolution)**

- 短链接 ID 由 Snowflake 生成，含 datacenter ID，保证全局唯一
- 自定义别名冲突: **Last-Write-Wins (LWW)** 不适用（用户体验差）；使用 **先到先得** + 跨 DC 同步检查
- 实际做法: 自定义别名创建走 **单一主 DC**，通过同步 RPC 确认全局唯一性

### 高并发处理 (High Concurrency Handling)

**连接池 (Connection Pooling)**
- DB 连接池: 每个服务实例维护 20-50 个连接
- Redis 连接池: 每个实例 50-100 个连接
- 使用 **PgBouncer** 或应用内连接池

**限流 (Rate Limiting)**
- API Gateway 层: 每用户每分钟最多 100 次创建请求
- 全局限流: 使用 Redis 实现的令牌桶 (**Token Bucket**) 或滑动窗口
- 读路径不做用户级限流（但有全局 QPS 上限保护后端）

**熔断器 (Circuit Breaker)**
- DB 连续失败 5 次 -> 熔断器打开 -> 30 秒内直接返回缓存/降级响应
- 外部 API（如 URL 安全检查）超时 -> 跳过检查，记录日志后续补扫

**优雅降级 (Graceful Degradation)**
- Redis 不可用 -> 直接查 DB（延迟升高但服务不中断）
- 分析管道故障 -> 重定向不受影响（分析是异步的）
- DB 主节点故障 -> 暂停写入，读取从副本继续

### 监控与告警 (Monitoring & Alerting)

| 指标 | 正常范围 | 告警阈值 |
|------|----------|----------|
| 重定向 P99 延迟 | < 10ms | > 50ms |
| 缓存命中率 | > 80% | < 60% |
| DB 主从延迟 | < 100ms | > 1s |
| ID 生成器响应时间 | < 1ms | > 10ms |
| 写入错误率 | < 0.01% | > 0.1% |
| Kafka 消费者 lag | < 10K | > 100K |
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| ID 生成 | Hash 截断 | Snowflake + Base62 | **Snowflake + Base62** -- 零碰撞，省去碰撞处理的复杂度和额外 DB 查询；虽需要分布式 ID 生成器，但 Snowflake 是成熟方案 |
| 重定向状态码 | 301 Permanent | 302 Found | **302 Found** -- 保留完整分析数据（每次请求回到服务端）；如果分析不重要且要最大化性能，选 301 |
| 缓存策略 | Cache-Aside | Read-Through | **Cache-Aside** -- 应用控制缓存逻辑，灵活处理过期 URL 和缓存预热；Read-Through 更简单但缓存层需要知道 DB 访问逻辑 |
| 数据库 | SQL (MySQL/PG) | NoSQL (DynamoDB) | **SQL 起步，DynamoDB 备选** -- 初期规模 SQL 足够，事务保证更强；超过单库容量时迁移到 DynamoDB（KV 模式天然适合） |
| 分析管道 | 同步写入 | 异步 Kafka | **异步 Kafka** -- 重定向是延迟敏感的核心路径，同步写分析会增加 P99 延迟；Kafka 解耦后分析管道故障不影响核心功能 |

### 一致性 vs. 可用性 (Consistency vs. Availability)

本系统是一个 **AP 偏好** 的系统（**CAP 定理 (CAP Theorem)** 应用）：

- **读路径**: 优先可用性。即使数据中心间复制有短暂延迟，也允许从本地缓存/副本返回。极端情况下可能返回 "not found"（刚创建的链接尚未复制到当前 DC），但这比整个服务不可用好。
- **写路径**: 短链接 ID 的唯一性需要强一致性保证（不能两个用户拿到相同短码）。通过 Snowflake ID 设计（含 datacenter + machine ID）在不需要分布式锁的情况下保证唯一性。
- **分析数据**: 最终一致即可，延迟几秒到几分钟都可接受。

### 成本 vs. 性能 (Cost vs. Performance)

- **缓存大小**: 缓存越大命中率越高，但 Redis 内存成本高。80-20 法则下缓存 20% 热门 URL 已能达到 80%+ 命中率，成本效益最优。
- **多 DC 部署**: 双活部署成本翻倍，但延迟降低 50%+。对于全球用户群是值得的；如果用户集中在单个区域，单 DC + CDN 更经济。

### 复杂度 vs. 简洁性 (Complexity vs. Simplicity)

- **ID 生成**: Snowflake 比简单自增 ID 复杂，但消除了单点故障和分布式协调需求。复杂度是值得的。
- **分析管道**: Kafka + Flink 比直接写 DB 复杂得多，但将分析从核心读路径解耦。如果分析不是必需的，可以大幅简化架构。

### 10x / 100x 规模下的变化 (What Changes at Scale)

**10x (10 亿 DAU, 350K 读 QPS)**:
- 单 Redis 集群不够 -> **Redis Cluster** 分片（按 short_code hash 分片）
- DB 单主节点写入瓶颈 -> 按 short_code hash 范围**分库分表 (Sharding)**
- 多 DC 变为必需（而非可选）

**100x (100 亿 DAU, 3.5M 读 QPS)**:
- 需要 **CDN 层** 缓存热门重定向（在边缘节点完成 302，不回源）
- 重定向状态码改为 **301**（减少回源流量，牺牲部分分析精度）
- 存储层迁移到 **DynamoDB / Cassandra**（PB 级）
- ID 生成器需要更多 bits 的 sequence 号（或更多节点）
"""

# ---------------------------------------------------------------------------
# S7: Defense Q&A (Interviewer Follow-up)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

**Q: 如果 ID Generator 所在的机器宕机了怎么办？短链接创建会完全中断吗？**

> **承认局限**: 如果只有一台 ID Generator，确实会成为单点故障。
>
> **缓解措施**: Snowflake 设计中，每台应用服务器可以有自己的 worker ID（从
> ZooKeeper 或启动配置获取）。ID 生成是**本地操作**（时间戳 + worker ID +
> 序列号），不需要网络调用。因此宕机一台只影响该台的请求，其他服务器继续正常
> 生成 ID。
>
> **数据**: 即使 10 台服务器中宕机 1 台，写入容量仅下降 10%。ZooKeeper 在
> 30 秒内重新分配 worker ID 给替补节点。期间可用性仍 > 99.9%。

---

**Q: 如果某个短链接突然病毒式传播（比如被知名博主分享），流量从 100 QPS 瞬间涨到 100 万 QPS，你的系统能扛住吗？**

> **承认局限**: 单个热门 URL 的流量可能超过单个 Redis 节点或 DB 分片的处理能力。
>
> **缓解措施**: 多层缓存策略:
>
> 1. **应用本地缓存 (Local Cache)**: 每个服务实例维护 LRU 缓存（100MB），
>    热门 URL 在进程内直接返回，无需网络调用（< 1ms）
> 2. **Redis 缓存**: 所有实例共享，TTL 设为 24h
> 3. **CDN 边缘缓存**: 对于极端热门链接，在 CDN 层缓存 302 重定向响应
>    （TTL = 5 分钟，平衡分析精度和性能）
>
> **数据**: 三层缓存下，100 万 QPS 的热门链接实际到达 DB 的请求 < 10 QPS
> （CDN 吸收 99%，Redis 吸收剩余 99%）。本地缓存 + Redis 的组合在模拟测试
> 中支撑了单链接 200 万 QPS。

---

**Q: 两个用户同时尝试创建相同的自定义别名怎么办？**

> **承认局限**: 并发写入确实可能导致竞态条件（Race Condition）。
>
> **缓解措施**: 依赖数据库的**唯一约束 (UNIQUE constraint)**:
>
> 1. 两个请求同时到达，各自生成 INSERT 语句
> 2. DB 的唯一索引保证只有一个 INSERT 成功
> 3. 失败的那个收到唯一约束冲突错误（MySQL: 1062, PG: 23505）
> 4. 服务端捕获错误，返回 **409 Conflict** 给第二个用户
>
> 这比使用分布式锁更简单且更可靠。分布式锁（如 Redis SETNX）有锁超时、死锁
> 等问题，而 DB 唯一约束是原子性的、零额外延迟的。
>
> **数据**: 在日均 1000 万条创建中，自定义别名冲突率 < 0.01%。DB 唯一约束
> 检查的额外开销 < 0.1ms。

---

**Q: 过期 URL 的清理怎么做？数据库不会无限膨胀吗？**

> **承认局限**: 如果不清理过期 URL，5 年后数据库会有数十亿条无用记录，浪费存储
> 并拖慢查询。
>
> **缓解措施**: **惰性删除 (Lazy Deletion)** + **定期清理 (Periodic Cleanup)**:
>
> 1. **惰性删除**: 读取时检查 `expires_at`，如果已过期返回 404（不立即删除）
> 2. **定期清理**: 后台 cron job 每天凌晨低峰期批量删除过期超过 30 天的记录
>    - 使用 `DELETE FROM urls WHERE expires_at < NOW() - INTERVAL 30 DAY LIMIT 10000`
>    - 分批删除（每次 10K 条），避免长事务锁表
> 3. **归档**: 将已删除的记录移入冷存储（S3），保留审计追踪
>
> **数据**: 假设 30% 的 URL 设置了过期时间，平均 TTL 为 90 天。定期清理使活跃
> 记录数稳定在约 15 亿条（而非无限增长的 50 亿+）。

---

**Q: 如果有人恶意创建大量短链接（垃圾链接攻击），你怎么防范？**

> **承认局限**: 不受限制的创建 API 确实容易被滥用。
>
> **缓解措施**: 多层防御:
>
> 1. **API 限流 (Rate Limiting)**: 每个 API Key / IP 每分钟最多 100 次创建
> 2. **URL 安全检查**: 写入前调用 **Google Safe Browsing API** 检测恶意 URL
>    （已知钓鱼/恶意软件站点），命中则拒绝创建
> 3. **验证码 (CAPTCHA)**: 匿名用户创建时要求通过验证码
> 4. **黑名单 (Blocklist)**: 维护已知恶意域名/IP 黑名单，直接拒绝
> 5. **异步后扫描**: 对已创建的 URL 定期批量扫描，发现恶意内容则标记并停用
>
> **数据**: 多层防御在类似服务中将恶意 URL 创建率降低到 0.001% 以下。Safe
> Browsing API 调用增加约 50ms 写延迟，但可异步化（先创建，后扫描）。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "URL Shortener 的核心功能是: 缩短 URL 和重定向。我想先确认几个关键需求:
> 读写比是多少? 我假设 100:1 -- 读远大于写。我们需要分析功能吗? 如果需要，
> 这决定了重定向用 301 还是 302。短链接是否需要过期功能? 预期的 DAU 大概是
> 多少量级?"
>
> 列出 FR: 缩短、重定向、自定义别名、TTL、分析。
> 列出 NFR: 99.99% 可用性、P99 < 10ms 读延迟、强一致写、100:1 读写比。
> 明确 Out of Scope: 用户系统、付费计划。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "架构分为读和写两条路径。写路径: Client -> API Gateway -> Shortening Service
> -> ID Generator -> DB。读路径: Client -> API Gateway -> Redirect Service ->
> Redis Cache -> DB (cache miss)。分析是异步的: Redirect Service 发事件到
> Kafka，Stream Processor 消费后写入分析存储。"
>
> "数据库选 MySQL/PostgreSQL -- URL 映射是简单 KV，但需要唯一约束和事务。
> 缓存用 Redis -- 读写比 100:1 意味着缓存收益巨大。ID 生成用 Snowflake
> 风格 -- 分布式、无碰撞、每节点本地生成。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: ID 生成策略 (5-8 分钟)**
> "两个主要方案: Hash 截断和 Snowflake + Base62。Hash 截断的问题是碰撞 --
> 10 亿条时碰撞概率接近 100%，需要重试逻辑。Snowflake 零碰撞，每节点本地
> 生成不需要网络调用。7 字符 Base62 给我们 3.5 万亿个地址，按每天 1000 万
> 条可用 960 年。我推荐 Snowflake + Base62。"

**重点 2: 缓存策略与热点处理 (5-8 分钟)**
> "三层缓存: 应用本地 LRU -> Redis Cluster -> CDN。80-20 法则下缓存 20%
> 热门 URL 只需 1GB 内存。病毒式传播场景: CDN 吸收 99% 流量，Redis 吸收
> 剩余 99%，到 DB 的请求 < 10 QPS。Cache-Aside 策略，缓存未命中时查 DB
> 并回填。过期 URL 通过惰性检查处理。"

**重点 3: 多 DC 部署与一致性 (5-8 分钟)**
> "Active-Active 双活部署，GeoDNS 就近路由。读路径完全本地化（本地 Redis +
> DB 副本）。写路径异步复制到其他 DC，延迟 < 200ms。Snowflake ID 含
> datacenter ID 保证跨 DC 唯一。自定义别名走单主 DC 保证全局唯一。
> CAP 角度这是 AP 系统 -- 优先可用性，接受短暂的跨 DC 不一致。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: 301 vs 302（性能 vs 分析），SQL vs NoSQL（一致性 vs 扩展性），
> 缓存大小（成本 vs 命中率）。10x 规模需要 Redis Cluster 分片和 DB 分库。
> 100x 规模需要 CDN 层和可能改用 301 减少回源。存储迁移到 DynamoDB 处理
> PB 级数据。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 分析管道的精确架构（Flink 窗口聚合），
> (2) 安全层（恶意 URL 检测、防滥用），(3) 数据库迁移策略（从 MySQL 到
> DynamoDB 的渐进式迁移方案）。"

### 55-60 分钟: 向面试官提问

> "我很好奇你们实际使用的 ID 生成方案是什么? 在实际生产中遇到过哪些这个
> 设计没覆盖到的挑战?"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计短链接服务 -- 核心是缩短和重定向。读写比 100:1，
   99.99% 可用性，P99 < 10ms。

2. **(60 秒) 架构**: 读写分离。写路径: Snowflake ID -> Base62 编码 -> 写入
   MySQL（唯一约束防冲突）。读路径: Redis 缓存优先（80%+ 命中率），miss 才
   查 DB。分析异步: Kafka -> ClickHouse。

3. **(60 秒) 核心算法**: 7 字符 Base62 = 3.5 万亿地址空间。Snowflake ID
   本地生成、零碰撞。三层缓存（本地 + Redis + CDN）处理热点。

4. **(30 秒) 扩展**: Active-Active 双活，GeoDNS 就近路由。10x 规模加分库分表，
   100x 加 CDN 层并可能改 301 减少回源。
"""


def populate_interview_url_shortener() -> None:
    """Create or update the interview-url-shortener record with all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            # Create the record
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
    populate_interview_url_shortener()
