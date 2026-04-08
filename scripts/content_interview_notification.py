"""Populate interview-notification-system system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Notification System.
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

SLUG = "interview-notification-system"
TITLE = "Design a Notification System"
DISPLAY_ORDER = 102

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**通知系统 (Notification System)**：支持多渠道（**Push Notification**、
**SMS**、**Email**）向用户发送通知。系统需要处理不同优先级的消息、支持模板渲染、
用户偏好管理、送达追踪和失败重试。日均发送量达到**数亿条**通知。

### 功能性需求 (Functional Requirements)

1. **多渠道发送 (Multi-channel Delivery)**：支持 Push（**APNs** (Apple Push Notification
   service) / **FCM** (Firebase Cloud Messaging)）、SMS（通过 **Twilio** / **AWS SNS** 等）、
   Email（通过 **SES** (Simple Email Service) / **SendGrid** 等）
2. **模板引擎 (Template Engine)**：支持通知模板，通过变量替换生成个性化内容
3. **用户偏好管理 (User Preferences)**：用户可选择接收渠道、免打扰时段、通知类别开关
4. **优先级队列 (Priority Queue)**：紧急通知（如安全告警、OTP）优先于营销通知发送
5. **送达追踪 (Delivery Tracking)**：记录每条通知的状态（sent / delivered / failed / read）
6. **失败重试 (Retry with Backoff)**：发送失败时指数退避重试，最终失败进入**死信队列
   (DLQ, Dead Letter Queue)**
7. **限流 (Rate Limiting)**：防止对单个用户的通知轰炸（如每小时最多 N 条营销通知）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（通知系统是所有业务的依赖方，不可用会影响全局）
- **延迟 (Latency)**：紧急通知从触发到送达 < 5 秒；普通通知 < 30 秒；营销通知分钟级可接受
- **吞吐量 (Throughput)**：峰值 10 万条/秒（大促、突发事件时更高）
- **可靠性 (Reliability)**：关键通知（OTP、安全告警）**至少送达一次 (at-least-once)**，
  不可丢失
- **可扩展性 (Scalability)**：日发送量从千万级增长到十亿级时水平扩展
- **幂等性 (Idempotency)**：重试不会导致用户收到重复通知

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 支持哪些通知渠道？是否需要支持 in-app notification？** -- WHY: 不同渠道的
   技术栈完全不同（Push 需要设备 token 管理，SMS 需要运营商对接，Email 需要域名认证）。
   In-app 通知可以用 WebSocket 实时推送，架构差异大。

2. **Q: 通知的发送方是谁？单个服务还是多个微服务？** -- WHY: 如果多个服务都会触发
   通知（订单服务、支付服务、营销服务），需要统一的 API Gateway 和事件驱动架构，
   避免各服务直接调第三方 API 导致的耦合和重复。

3. **Q: 对通知送达率的要求是多少？不同类型是否不同？** -- WHY: OTP 短信要求 99.9%+
   送达率，可能需要多运营商 failover；营销 push 95% 即可。送达率目标影响重试策略
   和冗余设计。

4. **Q: 是否需要支持通知的撤回或修改？** -- WHY: Email/SMS 一旦发出无法撤回，
   但 Push 可以更新或删除。如果需要撤回能力，通知需要持久化存储且客户端需要同步机制。

5. **Q: 用户偏好的粒度是什么？按类别、按渠道、还是按时间段？** -- WHY: 精细的偏好
   管理（如"仅在工作日 9-18 点接收营销 push"）需要复杂的规则引擎和调度逻辑。
   粗粒度（"关闭所有营销通知"）实现简单得多。

6. **Q: 有多少种通知模板？模板是否支持多语言？** -- WHY: 多语言模板需要 i18n 框架
   和用户语言偏好存储。模板数量多时需要版本管理和 A/B 测试支持。

7. **Q: 峰值流量是什么量级？有没有突发场景（如全站公告、大促开始）？** -- WHY:
   突发场景下百万用户同时触发通知，需要消息队列削峰和发送端限流，否则第三方
   API（APNs/FCM/Twilio）会被打垮或触发限流。

### 范围外 (Out of Scope)

- 通知内容审核 / 反垃圾（假设上游服务已审核）
- 第三方渠道的账号注册和配置（假设已完成 APNs 证书、Twilio 账号等设置）
- A/B 测试框架（通知内容优化属于营销系统职责）
- 用户认证和权限管理（由上游服务处理）
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Upstream Services (Order, Payment, Marketing, Security...)
    |
    v  (event / API call)
[Notification API Service]
    |
    |-- (validate, deduplicate, enrich)
    v
[Priority Message Queue]  (Kafka / RabbitMQ)
    |
    |-- Priority 0: Critical (OTP, security alerts)
    |-- Priority 1: Transactional (order confirmation, shipping)
    |-- Priority 2: Marketing (promotions, recommendations)
    v
[Notification Workers]  (consumer group, auto-scaling)
    |
    |-- (check user preferences)
    |-- (render template)
    |-- (rate limit check)
    |
    +----+----+----+
    |    |    |    |
    v    v    v    v
 [Push] [SMS] [Email] [In-App]
 (APNs  (Twilio (SES/   (WebSocket
  /FCM)  /SNS)  SendGrid) /SSE)
    |    |    |    |
    v    v    v    v
[Delivery Tracker]  (status callback)
    |
    v
[Analytics & DLQ]
```

### 服务划分 (Service Breakdown)

| 服务 | 职责 | 技术选型 |
|------|------|----------|
| **Notification API** | 接收通知请求、参数校验、幂等去重、写入消息队列 | REST API (Go/Java)、Redis (幂等 key) |
| **Priority Queue** | 按优先级缓冲和分发通知任务 | **Kafka** (高吞吐持久化) 或 **RabbitMQ** (优先级队列原生支持) |
| **Notification Workers** | 消费队列消息、查偏好、渲染模板、调用渠道 API 发送 | Worker pool，按渠道分组，支持独立扩缩容 |
| **Template Service** | 存储和渲染通知模板（变量替换、多语言） | 模板存储用 DB/S3，渲染用 Jinja2/Mustache |
| **User Preference Store** | 存储用户通知偏好（渠道选择、免打扰、类别开关） | **MySQL/PostgreSQL** + Redis 缓存 |
| **Device Registry** | 存储用户设备 token（Push 需要）、手机号、邮箱 | MySQL/PostgreSQL，一个用户可有多个设备 |
| **Delivery Tracker** | 接收渠道回调（delivery receipt）、更新通知状态 | 事件驱动，写入 **ClickHouse/Elasticsearch** 用于分析 |
| **DLQ Processor** | 处理最终失败的通知（告警、人工介入、渠道切换） | 从 DLQ topic 消费，写入运营面板 |

### 数据库选型理由 (Database Choices)

- **关系型 DB (MySQL/PostgreSQL)**：用户偏好、设备注册、模板元数据 -- 结构化数据，
  需要事务保证和复杂查询
- **Redis**：幂等 key 缓存、用户偏好热缓存、限流计数器 -- 低延迟读取
- **Kafka**：通知任务队列 -- 高吞吐、持久化、支持消费者组和回溯重放
- **ClickHouse**：送达日志和分析 -- 列式存储，适合大量写入和聚合查询
- **S3/OSS**：Email 模板附件、富媒体 Push 图片 -- 对象存储

### 通信模式 (Communication Patterns)

- **上游 -> Notification API**：同步 REST（需要即时确认接收）或异步事件（Kafka
  topic，上游服务 publish 事件，Notification 服务 subscribe）
- **API -> Workers**：异步消息队列（Kafka），按优先级分 topic/partition
- **Workers -> 渠道 API**：同步 HTTP（APNs/FCM/Twilio/SES 都是 REST API）
- **渠道回调 -> Delivery Tracker**：异步 webhook（渠道服务回调通知状态）
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (REST API Endpoints)

**发送通知 (Send Notification)**

```
POST /api/v1/notifications
Content-Type: application/json
X-Idempotency-Key: <uuid>

{
  "recipient_id": "user_12345",
  "type": "order_confirmation",
  "priority": 1,
  "channels": ["push", "email"],       // optional, default from user prefs
  "template_id": "order_confirmed_v2",
  "template_vars": {
    "order_id": "ORD-98765",
    "total": "129.99 USD",
    "eta": "2026-04-10"
  },
  "schedule_at": null                   // null = immediate, or ISO timestamp
}

Response 202 Accepted:
{
  "notification_id": "ntf_abc123",
  "status": "queued",
  "channels": ["push", "email"]
}
```

**查询通知状态 (Query Notification Status)**

```
GET /api/v1/notifications/{notification_id}

Response 200:
{
  "notification_id": "ntf_abc123",
  "status": "partially_delivered",
  "channels": [
    {"channel": "push", "status": "delivered", "delivered_at": "..."},
    {"channel": "email", "status": "sent", "sent_at": "..."}
  ]
}
```

**更新用户偏好 (Update User Preferences)**

```
PUT /api/v1/users/{user_id}/notification-preferences
{
  "channels": {
    "push": true,
    "sms": false,
    "email": true
  },
  "quiet_hours": {"start": "22:00", "end": "08:00", "timezone": "Asia/Shanghai"},
  "categories": {
    "marketing": {"enabled": false},
    "transactional": {"enabled": true},
    "security": {"enabled": true, "force": true}   // cannot be disabled
  }
}
```

### 核心数据模型 (Core Data Models)

**notifications 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT (Snowflake ID) | 主键 |
| recipient_id | VARCHAR(64) | 接收者用户 ID |
| type | VARCHAR(64) | 通知类型 (order_confirmation, otp, promo...) |
| priority | TINYINT | 0=critical, 1=transactional, 2=marketing |
| template_id | VARCHAR(64) | 模板 ID |
| template_vars | JSON | 模板变量 |
| idempotency_key | VARCHAR(128) UNIQUE | 幂等键 |
| status | ENUM | queued / processing / sent / delivered / failed |
| created_at | TIMESTAMP | 创建时间 |
| scheduled_at | TIMESTAMP | 计划发送时间 (null=immediate) |

**notification_deliveries 表**（每个渠道一条记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| notification_id | BIGINT | 关联 notifications.id |
| channel | ENUM | push / sms / email / in_app |
| provider | VARCHAR(32) | apns / fcm / twilio / ses |
| status | ENUM | pending / sent / delivered / failed |
| provider_msg_id | VARCHAR(128) | 第三方返回的消息 ID |
| attempts | INT | 已重试次数 |
| last_error | TEXT | 最近一次错误信息 |
| sent_at | TIMESTAMP | 发送时间 |
| delivered_at | TIMESTAMP | 送达时间 |

**user_devices 表**

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | VARCHAR(64) | 用户 ID |
| device_token | VARCHAR(512) | Push token (APNs/FCM) |
| platform | ENUM | ios / android / web |
| last_active_at | TIMESTAMP | 最后活跃时间 |

### 写入路径 (Write Path -- 发送通知)

1. **上游服务** 调用 `POST /api/v1/notifications`，附带 `X-Idempotency-Key`
2. **Notification API** 校验参数，用 Redis `SETNX` 检查幂等 key（TTL 24h）
   - 重复请求直接返回之前的 notification_id
3. 写入 `notifications` 表（状态 = queued）
4. 发布消息到 **Kafka** 对应优先级的 topic（`notifications.p0`、`notifications.p1`、
   `notifications.p2`）
5. 返回 `202 Accepted` + notification_id

### 读取路径 (Read Path -- Worker 处理)

1. **Notification Worker** 从 Kafka 消费消息（高优先级 topic 分配更多 consumer）
2. 查询 **User Preference Store**（Redis 缓存 -> DB fallback）：
   - 用户是否关闭了该类别的通知？
   - 当前是否在免打扰时段？（是 -> 延迟到免打扰结束时发送）
   - 用户选择了哪些渠道？
3. 查询 **Device Registry**：获取用户的设备 token（Push）、手机号（SMS）、邮箱（Email）
4. 调用 **Template Service** 渲染通知内容（变量替换、多语言）
5. **限流检查**：该用户在当前时间窗口内是否已超过通知上限？
6. 对每个目标渠道，调用对应的第三方 API 发送：
   - Push: APNs (iOS) / FCM (Android) HTTP/2 API
   - SMS: Twilio REST API
   - Email: SES/SendGrid SMTP 或 REST API
7. 写入 `notification_deliveries` 表（状态 = sent）
8. 等待渠道回调更新状态为 delivered 或 failed

### 异步路径 (Async Paths)

- **延迟发送**：`scheduled_at` 非空的通知由定时任务扫描，到期后投递到 Kafka
- **重试队列**：发送失败的通知进入 retry topic，指数退避后重新消费
- **DLQ**：达到最大重试次数（如 3 次）仍失败的通知进入 Dead Letter Queue，
  触发告警并写入运营面板
- **渠道回调**：APNs/FCM/Twilio 的 delivery receipt 通过 webhook 回调 Delivery
  Tracker，异步更新通知状态
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 流量估算 (Traffic Estimation)

假设一个中大型应用（如电商/社交平台）：

| 指标 | 估算值 |
|------|--------|
| **DAU** (Daily Active Users) | 1 亿 |
| 每用户每天平均收到通知数 | 5 条 |
| **日发送总量** | $1 \times 10^8 \times 5 = 5 \times 10^8$ (5 亿条/天) |
| **平均 QPS** | $\frac{5 \times 10^8}{86400} \approx 5{,}787$ 条/秒 |
| **峰值 QPS** (5x multiplier) | $5{,}787 \times 5 \approx 29{,}000$ 条/秒 |
| 大促峰值 (10x) | $\sim 58{,}000$ 条/秒 |

渠道分布（假设）：

| 渠道 | 占比 | 日发送量 | 峰值 QPS |
|------|------|----------|----------|
| Push | 60% | 3 亿条 | ~17,400 |
| Email | 25% | 1.25 亿条 | ~7,250 |
| SMS | 10% | 5,000 万条 | ~2,900 |
| In-App | 5% | 2,500 万条 | ~1,450 |

### 存储估算 (Storage Estimation)

**notifications 表**：

$$
\text{单条记录} \approx 500 \text{ bytes (ID + metadata + template\_vars JSON)}
$$

$$
\text{日增量} = 5 \times 10^8 \times 500 \text{ B} = 250 \text{ GB/天}
$$

$$
\text{年存储 (保留 90 天)} = 250 \times 90 = 22.5 \text{ TB}
$$

**notification_deliveries 表**（每条通知平均 1.5 个渠道）：

$$
\text{日增量} = 5 \times 10^8 \times 1.5 \times 300 \text{ B} = 225 \text{ GB/天}
$$

**总存储需求**（90 天保留）：

| 数据类型 | 日增量 | 90 天总量 |
|----------|--------|-----------|
| notifications | 250 GB | 22.5 TB |
| deliveries | 225 GB | 20.3 TB |
| 送达日志 (ClickHouse) | 100 GB | 9 TB |
| Redis 缓存 | ~50 GB (热数据) | -- |
| **合计** | ~625 GB/天 | ~52 TB |

### 带宽估算 (Bandwidth Estimation)

$$
\text{入站} = 29{,}000 \text{ req/s} \times 1 \text{ KB (avg request)} \approx 29 \text{ MB/s}
$$

$$
\text{出站 (to providers)} = 29{,}000 \times 2 \text{ KB (avg payload)} \approx 58 \text{ MB/s}
$$

### 内存估算 (Memory -- Redis Cache)

$$
\text{用户偏好缓存} = 1 \times 10^8 \times 200 \text{ B} = 20 \text{ GB}
$$

$$
\text{幂等 key 缓存 (24h TTL)} = 5 \times 10^8 \times 50 \text{ B} = 25 \text{ GB}
$$

$$
\text{限流计数器} = 1 \times 10^8 \times 32 \text{ B} = 3.2 \text{ GB}
$$

$$
\text{总 Redis 需求} \approx 48 \text{ GB} \to 4 \text{ 节点 (16GB each, with headroom)}
$$

### 核心算法: 指数退避重试 (Exponential Backoff Retry)

发送失败时的重试间隔：

$$
\text{delay} = \min(\text{base\_delay} \times 2^{\text{attempt}}, \text{max\_delay}) + \text{jitter}
$$

其中 $\text{base\_delay} = 1\text{s}$，$\text{max\_delay} = 300\text{s}$，
$\text{jitter} \in [0, 0.5 \times \text{delay}]$。

| 重试次数 | 延迟 (无 jitter) | 累计等待 |
|----------|------------------|----------|
| 1 | 2s | 2s |
| 2 | 4s | 6s |
| 3 | 8s | 14s |
| 4 (max) | 16s | 30s |
| 超过 4 次 | -> DLQ | -- |

### 核心算法: 优先级调度 (Priority Scheduling)

**Weighted Fair Queuing** 策略：

| 优先级 | 权重 | 含义 |
|--------|------|------|
| P0 (Critical) | 8 | OTP、安全告警，立即发送 |
| P1 (Transactional) | 4 | 订单确认、发货通知 |
| P2 (Marketing) | 1 | 促销、推荐，可延迟 |

Worker 消费比例：每消费 8 条 P0，消费 4 条 P1，消费 1 条 P2。当 P0 队列有积压时，
P2 的发送几乎暂停，确保关键通知不被营销通知阻塞。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability -- Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产约束与深度解析 (Production Constraints & Deep Dive)

### 具体规模数字 (Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 1 亿 |
| 日发送量 | 5 亿条 |
| 峰值 QPS | ~30,000 条/秒 (大促 ~60,000) |
| Kafka partitions | 30-60 per topic (3 topics by priority) |
| Notification Workers | 50-100 实例 (按渠道分组) |
| Redis 节点 | 4-8 个 |
| 通知模板数 | 500-2000 个 |
| 设备 token 总量 | ~2 亿 (部分用户多设备) |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **Notification API** | 新通知无法入队 | 多实例 + LB，API 无状态可水平扩展 |
| **Kafka Broker** | 消息积压或丢失 | 3 副本 (replication factor=3)，ISR 机制保证持久性 |
| **Redis** | 幂等检查失败、偏好缓存失效 | Redis Sentinel/Cluster，故障时降级到 DB 直读 |
| **Worker 实例** | 该实例负责的 partition 暂停消费 | Consumer group rebalance 自动将 partition 转移给存活实例 |
| **APNs/FCM** | Push 通知无法送达 | 队列积压 + 重试，渠道恢复后自动消化积压 |
| **Twilio/SES** | SMS/Email 无法发送 | 多提供商 failover (Twilio -> Vonage, SES -> SendGrid) |

### 多数据中心 / 跨区域 (Multi-Datacenter Considerations)

**方案: Active-Active 多 DC 部署**

- 每个 DC 有完整的 Notification 服务栈（API + Workers + Redis + Kafka）
- **DNS/GeoDNS** 将上游服务的通知请求路由到最近的 DC
- Kafka 使用 **MirrorMaker 2** 跨 DC 复制关键 topic（如 `notifications.p0`），
  确保 critical 通知在主 DC 故障时能在备 DC 继续处理
- 用户偏好和设备信息通过 **MySQL 主从复制** 跨 DC 同步（异步复制，延迟 < 1 秒）
- **幂等 key** 使用全局 Redis（或 key 中包含 DC 标识），防止跨 DC 重复发送

**跨区域用户路由**：

- 用户的设备 token 注册在哪个 DC，Push 通知就从哪个 DC 发送（减少与 APNs/FCM 的
  网络延迟）
- SMS/Email 无地域限制，从任一 DC 发送均可
- 免打扰时段计算需要用户的本地时区（存储在 user preferences 中）

### 高并发处理 (High Concurrency Handling)

**问题 1: 突发通知风暴（如全站公告 -> 1 亿用户同时触发通知）**

解决方案：
1. **消息队列削峰 (Peak Shaving)**：所有通知先进 Kafka，Workers 按自身处理能力消费。
   即使瞬间涌入 1 亿条，Kafka 能持久化缓冲，Workers 平稳处理。
2. **渠道限流 (Provider Rate Limiting)**：APNs 对并发连接有限制，FCM 对 QPS 有限制。
   Worker 端维护**令牌桶 (Token Bucket)**，控制对每个 provider 的调用频率。
3. **分批发送 (Batch Sending)**：全站公告不需要每个用户独立请求一次 API，
   Notification API 接收一个"广播"请求，后台按 batch 生成个人化通知任务。

**问题 2: 热点用户（某用户被 @了 1000 次，触发 1000 条通知）**

解决方案：
1. **用户级限流**：每用户每小时最多 N 条同类型通知（如 N=10 条 mention 通知）
2. **聚合通知 (Notification Aggregation)**：将多条同类型通知聚合为一条
   （"张三和其他 999 人提到了你"）。在 Worker 端维护短时间窗口（如 5 分钟），
   窗口内的同类通知合并为一条。

**问题 3: Consumer Lag（Workers 消费速度跟不上生产速度）**

解决方案：
1. **监控 Consumer Lag**：通过 Kafka 的 `consumer_lag` 指标实时监控
2. **Auto-scaling Workers**：当 lag 超过阈值时自动扩容 Worker 实例
   （基于 Kubernetes HPA 或自定义 autoscaler）
3. **优先级保障**：即使 P2 (营销) 严重积压，P0 (critical) 仍正常消费
   （独立 consumer group 和独立 worker pool）

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 | 含义 |
|------|----------|------|
| Kafka Consumer Lag | > 10,000 (P0), > 100,000 (P1) | Worker 消费速度不足 |
| 通知送达率 | < 99% (P0), < 95% (P1/P2) | 渠道异常或大量失败 |
| 第三方 API 延迟 | P99 > 2s (APNs), > 5s (SES) | Provider 性能下降 |
| DLQ 积压量 | > 1,000 条/小时 | 大量通知最终失败，需人工介入 |
| Redis 命中率 | < 90% (偏好缓存) | 缓存失效，DB 压力上升 |
| 重复通知率 | > 0.1% | 幂等机制失效 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|------------------|
| **消息队列** | RabbitMQ (原生优先级队列) | Kafka (高吞吐持久化) | **Kafka** -- 日发 5 亿条需要高吞吐，RabbitMQ 在高负载下优先级队列性能下降。Kafka 用 3 个 topic 按优先级分开，Worker 用加权消费模拟优先级。 |
| **推送模型 vs 拉取模型** | Push (服务端主动推送到各渠道) | Pull (客户端轮询) | **Push** -- 实时性要求高（OTP < 5 秒），Pull 模型的轮询间隔无法满足。In-app 通知用 WebSocket 保持长连接。 |
| **通知持久化** | 全量持久化 (所有通知存 DB) | 仅持久化失败和未读 | **全量持久化 90 天** -- 用于送达率分析、用户投诉排查、审计合规。90 天后归档到冷存储 (S3)。 |
| **模板渲染位置** | API 入口处渲染 | Worker 端渲染 | **Worker 端渲染** -- API 入口只做轻量校验和入队，模板渲染放在 Worker 端，解耦模板服务和入口服务，且 Worker 可以按需加载模板缓存。 |
| **多渠道发送策略** | 并行发送所有渠道 | 按优先级瀑布式 (先 Push，失败再 SMS) | **混合策略** -- 紧急通知 (P0) 并行发送所有渠道确保送达；普通通知 (P1/P2) 先 Push，Push 失败或用户 7 天未活跃时降级到 SMS/Email。节省成本（SMS 费用远高于 Push）。 |

### 一致性 vs 可用性 (Consistency vs Availability)

**CAP 定理在通知系统中的应用**：

通知系统是一个典型的**可用性优先 (AP)** 系统：

- **偶尔重复 > 丢失通知**：at-least-once 语义，宁可用户收到 2 条 OTP，
  也不能一条都收不到。幂等 key 尽量去重，但 Redis 故障时允许极少量重复。
- **最终一致**：通知状态（sent -> delivered）可能有几秒延迟（等待渠道回调），
  查询 API 返回的状态可能不是最新的，但最终会一致。
- **用户偏好的缓存一致性**：用户修改偏好后，Redis 缓存可能还是旧值（TTL 未过期）。
  使用 **Cache-Aside + 写时失效** 策略：写 DB 成功后主动删除 Redis 缓存，
  下次读取时回源 DB 并重新缓存。

### 成本 vs 性能 (Cost vs Performance)

| 渠道 | 每条成本 | 送达率 | 适用场景 |
|------|----------|--------|----------|
| Push | 接近免费 | 70-90% (取决于用户是否授权/打开通知) | 日常通知首选 |
| SMS | 0.01-0.05 USD | 95-99% | OTP、紧急通知、Push 失败降级 |
| Email | 0.0001-0.001 USD | 80-95% (进垃圾箱则无效) | 非紧急、内容丰富的通知 |

**优化策略**：
- Push 优先，失败或用户长期不活跃时降级到 SMS
- 营销通知只走 Push + Email，不走 SMS（成本控制）
- 批量 SMS 使用长码 (long code) 而非短码 (short code)，降低单价

### 10 倍 / 100 倍规模变化 (What Changes at 10x / 100x Scale)

**当前规模 (1x): 5 亿条/天，~30K 峰值 QPS**

**10x (50 亿条/天，~300K QPS)**：
- Kafka 需要更多 partition（100+ per topic）和更多 broker（15-20 台）
- Worker 实例 500+，按渠道拆分为独立微服务
- Redis 需要 Cluster 模式（16+ 节点）
- 引入**通知聚合层**（相似通知合并）减少实际发送量
- 第三方 provider 需要专属通道 / 更高 SLA 的企业计划

**100x (500 亿条/天，~3M QPS)**：
- 单个 Kafka 集群不够，需要 **federated Kafka**（按地区分集群）
- Worker 层需要 **serverless** 架构（如 AWS Lambda）实现秒级弹性扩缩容
- 引入**智能路由层**：基于用户行为预测最佳渠道（ML 模型），减少无效发送
- 存储层从 MySQL 迁移到 **分布式 NewSQL**（如 TiDB/CockroachDB）
- 通知内容 CDN 化（邮件图片、Push 富媒体）
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

**Q: 如果 APNs 或 FCM 服务宕机了，你的系统会怎样？百万条 Push 通知积压怎么办？**

> **承认局限**: APNs/FCM 是外部依赖，宕机时 Push 通知完全无法送达。如果积压
> 百万条消息，恢复后的突发重传可能进一步导致 provider 限流。
>
> **缓解措施**:
>
> 1. **渠道降级 (Channel Fallback)**：APNs/FCM 连续失败超过阈值时，自动将
>    关键通知（P0/P1）降级到 SMS 或 Email 渠道送达
> 2. **积压处理策略**：渠道恢复后不是立即全量重传，而是**渐进式 drain**：
>    按优先级排序，P0 先发，P2 可能直接丢弃（已过时效的营销通知无需发送）
> 3. **TTL (Time-to-Live)**：每条通知设置 TTL，过期的通知标记为 expired，
>    不再尝试发送。OTP 的 TTL 通常 5-10 分钟，营销通知 24 小时。
> 4. **熔断器 (Circuit Breaker)**：对每个 provider 维护 circuit breaker，
>    连续失败 N 次后自动 open，停止调用该 provider，定期 half-open 探测恢复
>
> **数据**: APNs 的历史可用性约 99.95%（年均宕机 ~4.4 小时）。渠道降级策略
> 可将 P0 通知的整体送达率从依赖单渠道的 99.95% 提升到多渠道的 99.99%。

---

**Q: 大促开始瞬间要给 1 亿用户发促销通知，怎么避免把第三方 API 打垮？**

> **承认局限**: 1 亿条通知如果不加控制地发送，APNs/FCM 的 QPS 限制会导致
> 大量 429 错误，Twilio/SES 也有发送速率限制。
>
> **缓解措施**:
>
> 1. **提前预热 (Pre-warming)**：大促前 15-30 分钟开始预热发送通道，
>    逐步提升 QPS（从 10% -> 50% -> 100%），让 provider 适应流量增长
> 2. **令牌桶限流 (Token Bucket per Provider)**：每个 Worker 维护
>    per-provider 的令牌桶，控制对每个 provider 的最大 QPS。
>    APNs 建议 ~50,000 req/s，FCM ~500,000 req/s，Twilio ~100 msg/s
> 3. **分批发送 (Staggered Sending)**：1 亿用户不需要在同一秒收到通知。
>    按用户分片（如 user_id % 100），每批 100 万用户，100 批 x 30 秒间隔
>    = 50 分钟完成全量发送
> 4. **优先级升级 (Priority Boost)**：大促通知临时升级为 P1（而非 P2 营销），
>    获得更多 Worker 资源
>
> **数据**: 分批发送策略下，1 亿用户的全量推送可在 30-60 分钟内完成，
> 第三方 API 的 429 错误率 < 0.1%。

---

**Q: 两个服务同时给同一个用户发送相同的通知（如订单服务和物流服务都发"已发货"），
怎么去重？**

> **承认局限**: 分布式系统中，不同服务可能基于同一事件独立触发通知，
> 导致用户收到重复消息。
>
> **缓解措施**:
>
> 1. **幂等 key (Idempotency Key)**：每条通知请求必须携带唯一的幂等 key
>    （如 `order:ORD-98765:shipped`），Notification API 用 Redis `SETNX`
>    检查。24 小时内重复的 key 直接返回已存在的 notification_id。
> 2. **事件驱动解耦**：推荐上游服务不直接调 Notification API，而是发布
>    领域事件到 Kafka（如 `order.shipped`）。Notification 服务订阅事件
>    并触发通知。同一事件只被消费一次（Kafka consumer offset 保证）。
> 3. **通知去重窗口**：即使幂等 key 不同，Worker 端也维护一个短时去重窗口
>    （如同一用户 + 同一模板 + 5 分钟内 = 去重）。
>
> **数据**: 幂等 key + 事件驱动架构将重复通知率从 ~2% 降低到 < 0.01%。

---

**Q: 如果流量突然 10 倍增长（如突发新闻推送），Kafka 和 Worker 能撑住吗？**

> **承认局限**: 10 倍突发超出常规容量规划，Kafka 的 partition 数和 Worker 数
> 可能不足，导致 consumer lag 急剧上升，通知延迟从秒级变成分钟级。
>
> **缓解措施**:
>
> 1. **Kafka 弹性 partition**：预分配足够的 partition 数（如 60 个/topic），
>    平时 30 个 Worker，突发时可扩到 60 个 Worker（每 Worker 消费 1 个 partition）
> 2. **Worker Auto-scaling**：基于 Kafka consumer lag 的 HPA (Horizontal Pod
>    Autoscaler)，lag > 10,000 时开始扩容，扩容时间 < 2 分钟（预热容器镜像）
> 3. **优先级隔离**：P0/P1/P2 使用独立的 consumer group 和 worker pool。
>    即使 P2 严重积压，P0 的通知延迟不受影响。
> 4. **背压 (Backpressure)**：当 Worker 处理不过来时，Notification API
>    对低优先级请求返回 **HTTP 503**，让上游服务自行重试或放弃。
>
> **数据**: 预分配 60 partition + HPA 可在 3 分钟内将处理能力从 30K QPS
> 扩展到 60K+ QPS。P0 通知在 10x 突发下的延迟仍 < 10 秒。

---

**Q: 用户投诉说通知太多、太烦，你怎么在系统层面解决？**

> **承认局限**: 通知系统的目标是"送达"，但过度发送会导致用户关闭通知权限
> 甚至卸载 App，长期来看适得其反。这是一个产品和技术都需要解决的问题。
>
> **缓解措施**:
>
> 1. **用户级频率上限 (Per-user Rate Limit)**：
>    - P0 (critical): 无上限
>    - P1 (transactional): 每小时 20 条上限
>    - P2 (marketing): 每天 3 条上限
> 2. **智能聚合 (Smart Aggregation)**：同类型通知在 5 分钟窗口内聚合
>    （"你收到了 12 条新消息" vs 12 条独立通知）
> 3. **免打扰 (Quiet Hours)**：尊重用户设置的免打扰时段，营销通知延迟
>    到免打扰结束后发送（P0 例外）
> 4. **疲劳度模型 (Notification Fatigue Model)**：跟踪用户的通知交互率
>    （打开率、关闭率）。交互率持续下降的用户自动降低推送频率。
> 5. **偏好中心 (Preference Center)**：提供细粒度的通知控制面板，
>    让用户自主选择接收哪些类别的通知
>
> **数据**: 引入用户级频率上限和智能聚合后，通知打开率提升 35%，
> 用户关闭通知权限的比率下降 20%。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "通知系统的核心是多渠道、可靠、可扩展地将消息送达用户。我想先确认几点：
> 支持哪些渠道？我假设 Push、SMS、Email，是否还需要 In-app？
> 通知的发送方是单一服务还是多个微服务？对不同优先级的送达延迟要求是什么？
> OTP 这类紧急通知我假设 < 5 秒，营销通知分钟级可接受。"
>
> 列出 FR: 多渠道发送、模板引擎、用户偏好、优先级队列、送达追踪、重试+DLQ、限流。
> 列出 NFR: 99.99% 可用性、at-least-once 送达、日发 5 亿条、峰值 30K QPS。
> 明确 Out of Scope: 内容审核、第三方配置、A/B 测试。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "整体流程: 上游服务 -> Notification API (校验+去重+入队) -> Kafka (3 个
> priority topic) -> Notification Workers (查偏好+渲染模板+限流+调渠道 API)
> -> APNs/FCM/Twilio/SES -> Delivery Tracker (回调更新状态)。"
>
> "选 Kafka 因为日发 5 亿条需要高吞吐持久化，RabbitMQ 在这个规模下性能不够。
> 用 3 个 topic 按优先级分开，Worker 用加权消费保证 P0 优先。
> 用户偏好存 MySQL + Redis 缓存，幂等 key 存 Redis (SETNX + 24h TTL)。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: 可靠送达与重试机制 (8-10 分钟)**
> "通知发送失败时，指数退避重试: base 1s, 最多 4 次 (2s, 4s, 8s, 16s)。
> 每次重试从 retry topic 消费，不阻塞主队列。超过最大重试次数进 DLQ，
> 触发运营告警。对 P0 通知，失败后立即触发渠道降级 -- Push 失败转 SMS。
> 每条通知设 TTL，过时效的通知不再发送（OTP 5 分钟，营销 24 小时）。"

**重点 2: 优先级调度与流量控制 (5-8 分钟)**
> "3 个 Kafka topic 对应 3 个优先级。Worker 用 Weighted Fair Queuing 消费:
> P0:P1:P2 = 8:4:1。P0 队列有积压时，P2 几乎暂停。对第三方 provider
> 维护令牌桶限流，防止超过 APNs/FCM 的 QPS 限制。大促场景用分批发送:
> 1 亿用户分 100 批，每批间隔 30 秒。"

**重点 3: 去重与幂等 (5-8 分钟)**
> "三层去重: (1) API 入口的 idempotency key + Redis SETNX; (2) Kafka
> consumer 的 offset 保证; (3) Worker 端的同用户+同模板+5 分钟去重窗口。
> 推荐上游服务用事件驱动而非直接 API 调用，减少重复触发。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: Kafka vs RabbitMQ (吞吐 vs 原生优先级)，Push-first vs 全渠道并行
> (成本 vs 送达率)，全量持久化 vs 仅失败记录 (可审计 vs 存储成本)。
> 10x 规模需要 100+ Kafka partitions、500+ Workers、独立渠道微服务。
> 100x 规模需要 serverless Workers、ML 智能路由、federated Kafka。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 通知疲劳度模型 -- 基于用户行为动态调整
> 推送频率，(2) A/B 测试框架 -- 测试不同通知文案/时机的效果，
> (3) 国际化 -- 多语言模板和时区感知的发送时间优化。"

### 55-60 分钟: 向面试官提问

> "你们的通知系统日发送量是什么级别？遇到过哪些最棘手的问题？
> 你们怎么处理用户通知疲劳的问题？有没有用 ML 模型优化发送时机？"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计多渠道通知系统 -- Push/SMS/Email，日发 5 亿条，
   紧急通知 < 5 秒送达，at-least-once 保证。

2. **(60 秒) 架构**: 上游服务 -> Notification API (幂等去重) -> Kafka
   (3 个 priority topic) -> Workers (偏好查询+模板渲染+限流) -> 渠道 API。
   Redis 做幂等 key、偏好缓存、限流计数。Kafka 持久化缓冲削峰。

3. **(60 秒) 可靠性**: 指数退避重试 (4 次 max) + DLQ。渠道降级 (Push 失败 -> SMS)。
   三层去重 (幂等 key + consumer offset + 模板窗口去重)。
   通知 TTL 防止过期消息发送。

4. **(30 秒) 扩展**: Kafka partition 预分配 + Worker HPA 自动扩缩容。
   P0/P1/P2 独立隔离，互不影响。大促用分批发送 + provider 预热。
"""


def populate_interview_notification() -> None:
    """Create or update the interview-notification-system record with all 8 sections."""
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

        # Check for Chinese characters
        import re
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
            # Find $ ... | ... $ patterns (bare pipe in inline math)
            in_math = False
            for i, ch in enumerate(content):
                if ch == "$" and (i == 0 or content[i - 1] != "\\"):
                    in_math = not in_math
                if in_math and ch == "|" and (i == 0 or content[i - 1] != "\\"):
                    # Check it's not \mid
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
    populate_interview_notification()
