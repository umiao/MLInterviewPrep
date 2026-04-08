"""Populate interview-ticket-reservation system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design Ticketmaster /
Hotel Reservation -- seat inventory management, distributed locking for
concurrent bookings, payment hold TTL, overbooking strategies, waitlist,
flash sale virtual queue, and idempotency.
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

SLUG = "interview-ticket-reservation"
TITLE = "Design Ticketmaster / Hotel Reservation"
DISPLAY_ORDER = 116

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**票务/预订系统 (Ticket Reservation System)**，类似 Ticketmaster (演出票务)
或 Hotel Reservation (酒店预订)。用户可以浏览活动/房间、选择座位/日期、完成预订
并支付。系统需要在高并发场景 (热门演唱会开票瞬间数百万人抢票) 下保证**不超卖
(No Overselling)**，同时提供流畅的用户体验。

核心挑战在于：(1) 库存的强一致性 -- 同一个座位/房间不能卖给两个人，
(2) 高并发下的性能 -- 热门活动开票瞬间 QPS 可达百万级，
(3) 支付流程的容错 -- 用户选座后需要预留时间完成支付，超时自动释放，
(4) 公平性 -- 防止黄牛 (scalper) 和机器人抢票。

### 功能性需求 (Functional Requirements)

1. **活动/房间浏览 (Browse Events/Rooms)**: 用户搜索和浏览可用活动或酒店房间，
   查看座位图 (seat map) 或房间类型、价格、可用性
2. **座位选择与预留 (Seat Selection & Hold)**: 用户选择座位/房间后系统临时锁定
   (hold)，给予有限时间 (如 10 分钟) 完成支付
3. **支付与确认 (Payment & Confirmation)**: 集成支付网关，支付成功后生成确认订单
   和电子票/预订凭证
4. **取消与退款 (Cancellation & Refund)**: 用户可在规定时间内取消预订并获得退款
5. **等待列表 (Waitlist)**: 热门活动售罄后用户可加入等待列表，有退票时自动通知
6. **库存管理 (Inventory Management)**: 活动主办方/酒店管理员管理座位图、
   定价策略、批量释放库存

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 票务系统宕机直接造成收入损失；
  开票时段要求零计划内停机
- **延迟 (Latency)**: 座位可用性查询 P99 < 200ms；预留座位 P99 < 500ms；
  浏览页面 P99 < 100ms (CDN 缓存)
- **一致性 (Consistency)**: 座位库存**强一致 (Strong Consistency)** --
  绝不允许同一座位卖给两个人；订单状态最终一致即可
- **可扩展性 (Scalability)**: 支持 5000 万注册用户，日均 500 万次搜索，
  热门活动开票瞬间 100 万+ 并发用户
- **持久性 (Durability)**: 支付成功的订单零丢失；预留状态可容忍极端情况下
  的短暂不一致 (TTL 超时自动修复)

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 座位是固定编号 (assigned seating) 还是通用入场 (general admission)?**
   -- WHY: 固定编号需要精确到每个座位的锁定逻辑 (seat-level lock)；通用入场
   只需计数器 (counter-based)，并发控制策略完全不同

2. **Q: 预留时间 (hold TTL) 是多长? 是否可配置?**
   -- WHY: TTL 太短导致用户支付失败体验差，太长导致库存被大量占用；
   这影响超时释放机制和库存利用率的设计

3. **Q: 是否需要支持动态定价 (dynamic pricing / surge pricing)?**
   -- WHY: 动态定价需要实时需求信号 (当前预订速率、剩余库存比例) 反馈到定价
   引擎，增加读写路径的复杂度

4. **Q: 热门活动是否需要虚拟排队 (virtual queue)?**
   -- WHY: 百万并发直接打到选座页会压垮系统；虚拟队列可以控制同时在线选座
   的用户数 (如每批放入 5000 人)，从根本上限制并发

5. **Q: 是否允许超售 (overbooking)? 例如酒店行业通常超售 5-10%。**
   -- WHY: 超售策略直接影响库存模型 -- 简单计数器 vs 概率模型 (预测
   no-show 率)；超售需要补偿机制 (升级房型、赔偿)

6. **Q: 支付失败后座位是否立即释放还是有重试窗口?**
   -- WHY: 立即释放可能导致用户反复尝试支付时座位被抢走；重试窗口占用库存
   但提升用户体验

7. **Q: 是否需要防黄牛/机器人机制?**
   -- WHY: 热门活动机器人可在毫秒级完成抢票，需要 CAPTCHA、设备指纹、
   购买频率限制等反作弊措施

### 不在范围内 (Out of Scope)

- 社交功能 (评论、分享、好友一起买票)
- 推荐引擎 (个性化推荐活动)
- 二手转票市场 (resale marketplace)
- 活动创建和场馆管理的完整 CMS
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Design)

### 核心服务与职责 (Core Services)

```
用户 (Browser/App)
  |
  v
[CDN] -- 静态资源 + 活动详情页缓存
  |
  v
[API Gateway / Load Balancer]
  |-- 限流 (Rate Limiting)、认证 (Auth)、路由 (Routing)
  |
  +---> [Event Service]          -- 活动/房间 CRUD、搜索、座位图
  +---> [Inventory Service]      -- 座位库存管理、预留/释放、锁定
  +---> [Booking Service]        -- 订单生命周期 (创建 -> 支付 -> 确认/取消)
  +---> [Payment Service]        -- 支付网关集成、幂等支付处理
  +---> [Queue Service]          -- 虚拟排队、流量整形
  +---> [Notification Service]   -- 确认邮件/短信、等待列表通知
  +---> [User Service]           -- 用户认证、个人信息、购买历史
```

### 数据库选型与理由 (Database Choices)

| 存储 | 技术选择 | 理由 |
|------|----------|------|
| **活动/房间元数据** | **PostgreSQL** | 结构化数据，需要复杂查询 (按日期/地点/价格筛选)，事务保证 |
| **座位库存** | **PostgreSQL** + 行级锁 | 强一致性要求；`SELECT ... FOR UPDATE` 保证不超卖 |
| **订单数据** | **PostgreSQL** | 事务性写入，支付审计需要 ACID |
| **座位可用性缓存** | **Redis** | 高频读取的座位图状态；写入仍走 PostgreSQL 保证一致性 |
| **虚拟队列** | **Redis Sorted Set** | 排队位置天然有序；O(log N) 入队/出队 |
| **会话/临时预留** | **Redis** (TTL) | 预留座位的临时状态，TTL 自动过期释放 |
| **搜索索引** | **Elasticsearch** | 活动全文搜索、地理位置搜索、多维度筛选 |

### 通信模式 (Communication Patterns)

- **同步 REST/gRPC**: 用户 -> API Gateway -> 各服务的请求-响应路径
- **异步消息队列 (Kafka)**: 支付结果回调 -> Booking Service；库存变更事件 ->
  通知 Waitlist 用户；订单事件 -> 分析管道
- **WebSocket / SSE**: 虚拟排队位置实时更新；座位图实时状态变更 (其他用户
  选了哪些座位)
- **定时任务 (Cron)**: 预留超时释放扫描 (兜底机制，Redis TTL 是主要机制)

### 数据分区策略 (Data Partitioning)

- **按活动 ID 分片 (Shard by Event ID)**: 同一活动的所有座位和订单在同一分片，
  保证事务局部性
- 热门活动 (热点分片) 通过**读写分离** + **Redis 缓存**缓解
- 跨活动查询 (用户订单历史) 通过**异步物化视图**或**CQRS** 模式处理
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (REST API Endpoints)

**活动浏览:**
```
GET  /api/v1/events?city=NYC&date=2026-05-01&page=1
     -> 200: { events: [...], pagination: {...} }

GET  /api/v1/events/{event_id}
     -> 200: { event_details, venue, seat_map_url }

GET  /api/v1/events/{event_id}/seats?section=A
     -> 200: { seats: [{ id, row, number, status, price }] }
```

**预订流程:**
```
POST /api/v1/reservations/hold
     Body: { event_id, seat_ids: ["A1", "A2"], user_id }
     -> 201: { hold_id, expires_at, total_price }
     -> 409: { error: "seats_unavailable", unavailable: ["A1"] }

POST /api/v1/reservations/{hold_id}/confirm
     Body: { payment_token, idempotency_key }
     -> 200: { booking_id, confirmation_code, e_ticket_url }
     -> 410: { error: "hold_expired" }
     -> 402: { error: "payment_failed", retry_allowed: true }

DELETE /api/v1/reservations/{hold_id}
     -> 200: { released_seats: ["A1", "A2"] }
```

**等待列表:**
```
POST /api/v1/events/{event_id}/waitlist
     Body: { user_id, desired_seats: 2, max_price: 150 }
     -> 201: { waitlist_position: 42 }
```

### 核心数据模型 (Core Data Models)

```sql
-- 活动表
CREATE TABLE events (
    id          BIGSERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    venue_id    BIGINT REFERENCES venues(id),
    start_time  TIMESTAMPTZ NOT NULL,
    status      VARCHAR(20) DEFAULT 'draft',  -- draft/on_sale/sold_out/completed
    total_seats INT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 座位库存表 (核心 -- 每个座位一行)
CREATE TABLE seats (
    id          BIGSERIAL PRIMARY KEY,
    event_id    BIGINT REFERENCES events(id),
    section     VARCHAR(10),
    row_label   VARCHAR(5),
    seat_number INT,
    status      VARCHAR(20) DEFAULT 'available',
    -- available / held / booked / blocked
    price       DECIMAL(10, 2),
    hold_id     UUID,           -- 当前持有的预留 ID
    hold_expires TIMESTAMPTZ,   -- 预留过期时间
    version     INT DEFAULT 0,  -- 乐观锁版本号
    UNIQUE(event_id, section, row_label, seat_number)
);
CREATE INDEX idx_seats_event_status ON seats(event_id, status);

-- 预留表
CREATE TABLE reservations (
    hold_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT NOT NULL,
    event_id        BIGINT NOT NULL,
    seat_ids        BIGINT[] NOT NULL,
    status          VARCHAR(20) DEFAULT 'held',
    -- held / confirmed / cancelled / expired
    total_price     DECIMAL(10, 2),
    hold_expires_at TIMESTAMPTZ NOT NULL,
    payment_id      VARCHAR(100),
    idempotency_key VARCHAR(100) UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at    TIMESTAMPTZ
);
```

### 写路径：预留座位 (Write Path: Hold Seats)

```
1. 用户选座 -> POST /reservations/hold
2. Booking Service 生成 hold_id + idempotency_key
3. Inventory Service 开启 DB 事务:
   a. SELECT id, status, version FROM seats
      WHERE event_id = ? AND id IN (?) AND status = 'available'
      FOR UPDATE;                          -- 行级排他锁
   b. 检查返回行数 == 请求座位数 (否则 409)
   c. UPDATE seats SET status = 'held',
      hold_id = ?, hold_expires = NOW() + INTERVAL '10 min',
      version = version + 1
      WHERE id IN (?) AND version = ?;     -- 乐观锁二次校验
   d. INSERT INTO reservations (...);
   e. COMMIT;
4. 同时在 Redis 设置 TTL key: hold:{hold_id} -> seat_ids (10 min TTL)
5. 返回 201 { hold_id, expires_at }
```

### 写路径：确认支付 (Write Path: Confirm Payment)

```
1. 用户支付 -> POST /reservations/{hold_id}/confirm
2. Booking Service 校验 idempotency_key (防重复支付)
3. 检查 hold 是否过期 (hold_expires_at > NOW())
4. 调用 Payment Service (异步):
   a. Payment Service 调用第三方支付网关
   b. 返回支付结果 (成功/失败)
5. 支付成功:
   a. UPDATE seats SET status = 'booked' WHERE hold_id = ?;
   b. UPDATE reservations SET status = 'confirmed',
      payment_id = ?, confirmed_at = NOW();
   c. 删除 Redis TTL key
   d. 发送确认通知 (Kafka -> Notification Service)
6. 支付失败:
   a. 保留 hold 状态，返回 402 允许重试
   b. hold 最终超时后自动释放
```

### 读路径：座位可用性 (Read Path: Seat Availability)

```
1. GET /events/{event_id}/seats
2. 先查 Redis 缓存 (seat_map:{event_id})
3. 缓存未命中 -> 查 PostgreSQL，结果写入 Redis (TTL 5s, 短 TTL 保证新鲜度)
4. 返回座位列表 + 状态 (available/held/booked)
5. 热门活动: WebSocket 推送实时座位状态变更 (减少轮询)
```

### 预留超时释放 (Hold Expiration)

```
主要机制: Redis TTL 过期事件 (Keyspace Notification)
  -> 触发 Inventory Service 释放座位
  -> UPDATE seats SET status = 'available', hold_id = NULL
     WHERE hold_id = ? AND status = 'held';
  -> 更新 reservation 状态为 'expired'
  -> 检查 waitlist，通知下一位用户

兜底机制: 定时任务每分钟扫描
  SELECT * FROM seats WHERE status = 'held'
    AND hold_expires < NOW();
  -> 批量释放过期座位
```
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Capacity Estimation)

**用户规模假设:**
- 注册用户: 5000 万
- **DAU (Daily Active Users)**: 200 万 (搜索浏览为主)
- 日均订单: 50 万笔
- 热门活动同时在线: 100 万+

**QPS 估算:**

$$\text{搜索 QPS} = \frac{200\text{万} \times 5\text{次搜索/用户}}{86400} \approx 116 \text{ QPS (平均)}$$

$$\text{搜索峰值 QPS} = 116 \times 5 \approx 580 \text{ QPS}$$

$$\text{订单写 QPS} = \frac{50\text{万}}{86400} \approx 6 \text{ QPS (平均)}$$

**热门活动开票瞬间 (Flash Sale):**

$$\text{并发用户} = 1{,}000{,}000$$

$$\text{第一秒请求量} \approx 500{,}000 \text{ (假设 50\% 用户在第一秒刷新)}$$

$$\text{虚拟队列吞吐} = 5{,}000 \text{ 用户/批次} \times 6 \text{ 批次/分钟} = 30{,}000 \text{ 用户/分钟}$$

$$\text{实际选座 QPS} = 5{,}000 \text{ 并发选座用户} \times 3 \text{ 请求/用户} = 15{,}000 \text{ QPS}$$

**存储估算:**

| 数据类型 | 单条大小 | 日增量 | 年存储 |
|----------|----------|--------|--------|
| 活动元数据 | ~2 KB | 500 条 | ~365 MB |
| 座位记录 | ~200 B | 500 万条 (新活动) | ~365 GB |
| 订单记录 | ~500 B | 50 万条 | ~91 GB |
| 支付记录 | ~300 B | 50 万条 | ~55 GB |

$$\text{年总存储} \approx 365 + 91 + 55 \approx 511 \text{ GB (不含索引)}$$

**带宽估算:**

$$\text{搜索响应} = 580 \text{ QPS} \times 5 \text{ KB} = 2.9 \text{ MB/s}$$

$$\text{座位图响应} = 1{,}000 \text{ QPS} \times 50 \text{ KB} = 50 \text{ MB/s}$$

**缓存估算 (Redis):**

$$\text{热门活动座位缓存} = 1{,}000 \text{ 活动} \times 50{,}000 \text{ 座位} \times 200\text{B} = 10 \text{ GB}$$

$$\text{预留 TTL Key} = 100{,}000 \text{ 并发预留} \times 200\text{B} = 20 \text{ MB}$$

$$\text{虚拟队列} = 1{,}000{,}000 \text{ 用户} \times 100\text{B} = 100 \text{ MB}$$

### 核心算法 (Core Algorithms)

#### 1. 分布式座位锁定 (Distributed Seat Locking)

使用 **PostgreSQL 行级锁 + 乐观锁** 双重保护：

```sql
-- 悲观锁: 防止并发读取同一座位
SELECT * FROM seats WHERE id IN (101, 102)
  AND status = 'available' FOR UPDATE SKIP LOCKED;

-- 乐观锁: 防止 ABA 问题
UPDATE seats SET status = 'held', version = version + 1
  WHERE id IN (101, 102) AND version = expected_version;
```

**`FOR UPDATE SKIP LOCKED`** 的关键优势: 如果座位已被其他事务锁定，立即跳过
而不是等待，避免高并发下的锁等待超时。

#### 2. 虚拟队列公平排序 (Virtual Queue Fair Ordering)

```python
# Redis Sorted Set: score = 进入时间戳
ZADD queue:{event_id} {timestamp} {user_id}

# 每批放入 N 人
users = ZRANGEBYSCORE queue:{event_id} -inf +inf LIMIT 0 5000
# 发放临时选座令牌 (JWT, TTL=10min)
for user in users:
    issue_selection_token(user, event_id, ttl=600)
ZREM queue:{event_id} *users
```

#### 3. 超售概率模型 (Overbooking Probability Model) -- 酒店场景

$$P(\text{no-show}) = \frac{\text{历史 no-show 数}}{\text{历史总预订数}}$$

$$\text{超售数} = \text{总房间} \times P(\text{no-show}) \times \alpha$$

其中 $\alpha$ 为风险系数 (保守 0.5, 激进 1.0)。期望补偿成本:

$$E[\text{补偿}] = \sum_{k=\text{超售数}+1}^{n} \binom{n}{k} p^k (1-p)^{n-k} \times C_{\text{upgrade}}$$

当 $E[\text{补偿}] < \text{超售收入}$ 时, 超售策略是盈利的。

#### 4. 幂等性保证 (Idempotency)

```
idempotency_key = SHA256(user_id + event_id + seat_ids + timestamp_bucket)

-- 支付确认前检查
SELECT * FROM reservations WHERE idempotency_key = ?;
-- 如果已存在且 status = 'confirmed', 直接返回成功 (幂等)
-- 如果已存在且 status = 'held', 继续支付流程
-- 如果不存在, 拒绝 (hold 可能已过期)
```
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Deep Dive -- Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性深度解析 (Scale & Reliability Deep Dive)

### 具体规模数据 (Concrete Scale Numbers)

| 指标 | 值 | 上下文 |
|------|-----|--------|
| **注册用户** | 5000 万 | 全球市场 |
| **DAU** | 200 万 | 主要为浏览和搜索 |
| **日均订单** | 50 万笔 | 含票务和酒店 |
| **平均搜索 QPS** | ~120 | 读多写少，缓存友好 |
| **热门活动并发** | 100 万+ | 开票瞬间流量突增 100x |
| **虚拟队列吞吐** | 3 万用户/分钟 | 每批 5000 人，每 10 秒一批 |
| **选座写 QPS (峰值)** | 15,000 | 虚拟队列控制后的实际并发 |
| **PostgreSQL 实例** | 3 节点主从 (per shard) | 按活动 ID 分片，热门活动独立分片 |
| **Redis 集群** | 6 节点 (3 主 3 从) | 队列 + 座位缓存 + 预留 TTL |
| **年存储增长** | ~500 GB | 不含索引和备份 |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 缓解措施 |
|------|---------|---------|
| **PostgreSQL 主库** | 无法写入预留/订单 | 自动故障转移 (Patroni/PgBouncer), RTO < 30s |
| **Redis 主节点** | 队列和缓存不可用 | Redis Sentinel 自动切换; 降级为直接查 DB |
| **支付网关** | 无法完成支付 | 多支付渠道 (Stripe + PayPal + Adyen); 自动切换 |
| **API Gateway** | 全站不可用 | 多 AZ 部署 + DNS 故障转移; 健康检查 + 自动摘除 |
| **Kafka** | 异步通知延迟 | 3 副本, ISR >= 2; 降级为同步通知 |

### 多数据中心考量 (Multi-Datacenter Considerations)

**架构选择: Active-Passive (主动-被动)**

- **理由**: 座位库存要求强一致性，多活写入会导致超卖。票务系统的写入集中在
  开票时段，active-active 的复杂性不值得。

- **数据复制**: PostgreSQL 流复制 (Streaming Replication)，异步复制延迟
  < 100ms。故障转移时可能丢失最近 100ms 的预留 (可接受 -- TTL 会自动修复)。

- **DNS 路由**: 使用 **Route 53** 健康检查 + 故障转移策略。正常流量全部
  路由到主 DC；主 DC 不可达时 30 秒内切换到备 DC。

- **跨区域读取**: 搜索和浏览走就近 CDN + 只读副本；预订写入统一路由到主 DC。

**酒店场景变体 (Active-Active 可行):**

酒店预订可以按地区分片 (北美酒店 -> US-East, 欧洲酒店 -> EU-West)，
每个分片内 active-passive，跨分片查询走联邦查询。

### 高并发处理 (High Concurrency Handling)

#### 连接池 (Connection Pooling)
- **PgBouncer** 在应用层和 PostgreSQL 之间: 每个应用实例 20 连接 -> PgBouncer
  复用为 PostgreSQL 的 200 个连接
- 避免 PostgreSQL 连接数耗尽 (默认 max_connections = 100)

#### 流量整形 (Traffic Shaping)
- **API Gateway 限流**: 每用户 10 req/s (搜索)，1 req/s (预留)
- **虚拟队列**: 热门活动开启排队模式，控制实际并发选座人数 <= 5000
- **渐进式放量**: 开票前 30 分钟开启队列，避免瞬间流量冲击

#### 熔断器 (Circuit Breaker)
- 支付网关故障率 > 50% 时触发熔断，暂停新预留 (避免大量 hold 占用库存)
- 熔断期间返回 "系统繁忙请稍后" + 延长现有 hold 的 TTL

#### 优雅降级 (Graceful Degradation)
- Redis 不可用: 降级为 DB 直查 (延迟增加但功能正常)
- 搜索引擎不可用: 降级为 DB 基础查询 (无全文搜索)
- 通知服务不可用: 订单确认同步返回，邮件/短信异步重试

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 | 含义 |
|------|---------|------|
| **预留成功率** | < 95% | 可能存在锁竞争或 DB 瓶颈 |
| **支付成功率** | < 90% | 支付网关可能故障 |
| **hold 超时释放率** | > 30% | TTL 可能太短或支付流程太慢 |
| **座位不一致数** | > 0 | 预留状态与 DB 不一致 (严重) |
| **虚拟队列等待时间** | > 30 min | 需要增加每批放入人数或缩短批次间隔 |
| **DB 锁等待时间 P99** | > 500ms | 热点座位竞争过激 |
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

| 决策 | 方案 A | 方案 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| **库存锁定** | 悲观锁 (SELECT FOR UPDATE) | 乐观锁 (version check) | **悲观锁 + SKIP LOCKED** -- 高竞争场景下乐观锁冲突重试率高 (热门座位可能 90%+ 冲突)；SKIP LOCKED 避免等待 |
| **预留状态存储** | 纯 DB | DB + Redis TTL 双写 | **双写** -- Redis TTL 提供精确过期释放 + 高性能读取；DB 作为持久化真相源；双写一致性由 TTL 兜底 |
| **虚拟队列 vs 直接抢** | 先到先得 (无队列) | 虚拟排队 + 批量放入 | **虚拟队列** -- 直接抢在百万并发下系统必然崩溃；队列以牺牲 "即时性" 换取系统稳定性和公平性 |
| **超售策略** | 禁止超售 (票务) | 允许超售 (酒店) | **按业务场景** -- 演唱会票固定座位绝不超售；酒店可根据历史 no-show 率超售 5-8%，补偿成本 < 空房损失 |
| **支付集成** | 同步支付 (hold 期间完成) | 异步支付 (先确认后扣款) | **同步支付** -- 票务场景库存珍贵，必须支付成功才确认；异步支付会导致 "已确认但未付款" 的尴尬状态 |

### 详细分析: 悲观锁 vs 乐观锁

**为什么悲观锁在此场景胜出:**

- 热门座位的竞争比 (contention ratio) 极高: 100 人同时抢同一区域 10 个座位
- 乐观锁: 100 人同时读取 version=1，99 人的 UPDATE 失败需要重试，
  重试时可能座位已售罄 -> 大量无效重试 + 差用户体验
- 悲观锁 + `SKIP LOCKED`: 第一个拿到锁的人成功，其他人立即得到
  "座位不可用" 响应 (不等待、不重试)

**乐观锁仍有用武之地:**
- 非热门活动 (竞争低) 或通用入场 (counter-based) 场景
- 订单状态更新 (held -> confirmed) -- 只有持有人自己操作，无竞争

### 详细分析: 虚拟队列的取舍

**优势:**
- 将 100 万并发降低为 5000 并发选座 -- 系统可以从容处理
- 用户看到 "您是第 42,000 位" 比 "503 Service Unavailable" 体验好
- 可以实施公平策略 (FIFO, 会员优先, 抽签)

**代价:**
- 增加用户等待时间 (100 万人 / 3 万人/分钟 = ~33 分钟清空队列)
- 需要 WebSocket/SSE 实时推送队列位置
- 排在后面的用户可能等到前面已售罄

### 10x / 100x 规模下的变化

**10x (5 亿用户, 1000 万日活):**
- PostgreSQL -> **TiDB** 或 **CockroachDB** (分布式 SQL, 自动分片)
- 座位库存缓存: Redis Cluster 扩展到 30+ 节点
- 虚拟队列: 多级队列 (先按地区分流, 再按活动排队)
- CDN: 座位图实时更新通过 Edge Compute (Cloudflare Workers) 处理

**100x (50 亿用户, 1 亿日活):**
- 全球多区域部署, 每个区域独立数据平面
- 座位库存: **CRDT (Conflict-free Replicated Data Type)** 计数器
  (仅适用于通用入场; 固定座位仍需单主)
- 支付: 按区域对接本地支付网关 (支付宝/微信支付, UPI, M-Pesa)
- 队列: 分布式队列 (Kafka Streams) 替代 Redis Sorted Set
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果 Redis 宕机了怎么办? 预留的 TTL 还能正常过期吗?

**承认局限**: Redis 宕机意味着 TTL 过期事件丢失, 座位可能被永久锁定。

**缓解措施**:
1. **兜底定时任务**: 每分钟扫描 `seats` 表中 `status = 'held' AND hold_expires < NOW()`
   的记录并释放。即使 Redis 完全不可用, DB 中的 `hold_expires` 字段保证最终释放。
2. **Redis Sentinel**: 自动故障转移, 通常 5-15 秒完成切换, 丢失的 TTL 事件
   由兜底任务在下一分钟补偿。
3. **双源校验**: 确认支付时同时检查 Redis TTL 和 DB `hold_expires`, 任一过期
   即拒绝确认。

**数据/证据**: Ticketmaster 的实际架构也采用 DB 兜底 + 缓存层加速的双重模式,
确保单层故障不会导致库存不一致。

### Q2: 如果热门活动流量突然 10x (从 100 万到 1000 万) 怎么办?

**承认局限**: 虚拟队列的清空时间会线性增长, 用户体验下降。

**缓解措施**:
1. **弹性扩容**: 提前 30 分钟基于队列长度触发自动扩容 --
   Kubernetes HPA + 预热 pod 池 (warm pool)
2. **多级限流**: API Gateway 层 (全局限流) + 服务层 (per-event 限流) +
   DB 层 (连接池限制)
3. **渐进式放票**: 分批释放库存 (先放 50% 座位, 1 小时后放剩余),
   将峰值压力分散到更长时间窗口
4. **静态化降级**: 活动详情页完全 CDN 缓存, 座位图改为 "估算可用"
   (非实时), 只有实际选座时才查实时库存

**数据/证据**: 以 Taylor Swift Eras Tour 为例, Ticketmaster 在 2022 年处理了
1400 万并发用户, 最终采用了 "Verified Fan" 预注册 + 随机抽签 + 分批放票
的组合策略, 而非纯 FIFO 队列。

### Q3: 两个用户同时选了同一个座位会发生什么?

**承认局限**: 这是系统最核心的竞争场景。

**缓解措施 (三层防护)**:
1. **前端乐观锁定**: WebSocket 实时推送座位状态变更, 用户 A 选座后其他用户
   立即看到该座位变灰。但这只是 UI 层面的软保护, 不能保证一致性。
2. **Redis 原子操作**: `SET seat:{id}:hold {user_id} NX EX 600` -- NX 保证
   只有第一个请求成功, 原子性由 Redis 单线程保证。
3. **PostgreSQL 行级锁**: `SELECT ... FOR UPDATE SKIP LOCKED` -- 即使 Redis
   层竞争通过, DB 层仍然保证只有一个事务能锁定该座位。

**结果**: 第一个到达 DB 层的用户成功预留, 第二个用户在 < 100ms 内收到
"座位已被选" 的响应, 可以选择其他座位。零超卖。

### Q4: 黄牛用机器人批量抢票怎么办?

**承认局限**: 完全防止机器人是不可能的, 但可以大幅提高成本。

**缓解措施**:
1. **排队阶段**: Verified Fan 预注册 (实名 + 购买历史验证) + CAPTCHA
2. **选座阶段**: 设备指纹 (TLS fingerprint + Canvas hash) + 行为分析
   (鼠标轨迹, 点击间隔)
3. **支付阶段**: 每用户限购 (如最多 4 张) + 信用卡去重 (同一卡号限 2 笔)
4. **事后追溯**: 异常订单检测 (同一 IP/设备大量下单) + 取消可疑订单

**数据/证据**: Ticketmaster 的 Verified Fan 程序在 2023 年标记了约 15% 的
注册为可疑 bot, 有效减少了黄牛抢票量。

### Q5: 如何保证支付的幂等性? 用户连续点击两次 "支付" 会发生什么?

**承认局限**: 支付幂等性是分布式系统最常见的陷阱之一。

**缓解措施**:
1. **客户端**: 点击后立即禁用按钮 + 生成 `idempotency_key`
   (基于 hold_id + timestamp_bucket)
2. **服务端**: `reservations` 表中 `idempotency_key` 字段设置 UNIQUE 约束,
   第二次请求直接返回第一次的结果 (幂等响应)
3. **支付网关**: Stripe/PayPal 原生支持 `Idempotency-Key` header,
   重复请求返回相同结果而不会重复扣款

```
请求 1: idempotency_key = "abc123" -> 创建支付 -> 成功 -> 返回 booking_id
请求 2: idempotency_key = "abc123" -> 查到已有记录 -> 直接返回 booking_id (不重复扣款)
```
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

"这道题我想确认几个关键点:

首先, 座位模式 -- 是固定编号 (assigned seating) 还是通用入场 (general admission)?
这决定了库存模型是 per-seat lock 还是 counter-based。我先假设**固定编号**, 因为
这是更复杂也更常考的场景。

然后, 并发规模 -- 是否有 flash sale 场景? 比如热门演唱会开票瞬间百万人同时抢?
如果是, 我会加入虚拟队列来控制并发。

非功能性需求方面, 我认为最关键的是:
- 座位库存**强一致** -- 绝不超卖
- 可用性 99.99% -- 开票宕机直接损失收入
- 预留座位的 TTL 机制 -- 给用户支付窗口但不永久锁定库存

核心功能: 浏览活动、选座预留、支付确认、取消退款、等待列表。"

### 5-15 分钟: 高层架构 (High-Level Architecture)

"架构分为 6 个核心服务:

**Event Service** 管理活动和房间元数据, 读多写少, CDN 缓存友好。
**Inventory Service** 是核心 -- 座位级别的库存管理, 用 PostgreSQL 行级锁
保证不超卖。
**Booking Service** 管理订单生命周期: held -> confirmed -> cancelled。
**Payment Service** 对接支付网关, 幂等处理。
**Queue Service** 在热门活动开票时启动虚拟排队。
**Notification Service** 发送确认和等待列表通知。

数据库选择: PostgreSQL 作为主存储 -- 座位库存需要 ACID 事务。Redis 做三件事:
(1) 座位可用性缓存, (2) 预留 TTL 管理, (3) 虚拟队列。
Elasticsearch 做活动搜索。

数据分片按活动 ID -- 同一活动的所有座位和订单在同一分片, 保证事务局部性。"

### 15-40 分钟: 深度解析 (Deep Dive)

**深度话题 1: 分布式座位锁定 (10 分钟)**

"这是系统最关键的部分。并发选座的核心挑战是: 100 人同时想买同一区域的座位。

我的方案是 PostgreSQL `SELECT ... FOR UPDATE SKIP LOCKED`:
- 悲观锁保证同一时刻只有一个事务能操作某个座位
- `SKIP LOCKED` 是关键优化 -- 座位已被锁定时不等待, 立即返回 '不可用'
- 前端通过 WebSocket 实时显示座位状态, 减少无效请求

预留流程: 选座 -> DB 行级锁 -> 写入 held 状态 + TTL -> Redis TTL key ->
返回 hold_id + 过期时间。支付成功 -> held 转 booked; 超时 -> Redis TTL
触发释放 + DB 兜底扫描。"

**深度话题 2: 虚拟队列 (8 分钟)**

"100 万人同时涌入会压垮任何系统。虚拟队列的思路是:

进入方式: 用户访问活动页 -> 自动加入 Redis Sorted Set (score = 时间戳)。
批量放入: 每 10 秒从队列头部取出 5000 人, 发放临时选座令牌 (JWT, TTL=10分钟)。
只有持有有效令牌的用户才能调用选座 API。

这样实际选座并发被控制在 5000 人, 系统可以从容处理。用户看到排队进度条
(通过 SSE 实时推送), 比 503 错误体验好得多。"

**深度话题 3: 支付容错与幂等 (7 分钟)**

"支付是最容易出问题的环节:

幂等性: 客户端生成 idempotency_key, 服务端 UNIQUE 约束, 支付网关也支持
Idempotency-Key。三层保证不会重复扣款。

超时处理: hold TTL = 10 分钟。支付网关超时不等于支付失败 -- 可能网关已扣款
但回调丢失。处理方式: (1) 异步轮询支付状态, (2) 支付网关 webhook 回调,
(3) 对账定时任务 (每小时全量对账)。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

"几个关键权衡:

1. 悲观锁 vs 乐观锁 -- 选悲观锁 + SKIP LOCKED, 因为热门座位竞争比极高
2. 虚拟队列 vs 直接抢 -- 选队列, 牺牲即时性换稳定性
3. 超售 -- 票务禁止, 酒店允许 (基于 no-show 概率模型)

10x 规模: PostgreSQL -> 分布式 SQL (TiDB); Redis 扩展到 30+ 节点
100x 规模: 多区域部署; 通用入场用 CRDT 计数器; 按区域分片"

### 50-55 分钟: 总结 (Wrap-up)

"如果有更多时间, 我会深入:
- 动态定价引擎 (基于需求曲线实时调价)
- 反黄牛系统 (设备指纹 + 行为分析 + 限购策略)
- 二手转票市场 (原价上限 + 身份绑定)
- 全球化 (多时区、多币种、本地支付网关)"

### 55-60 分钟: 向面试官提问

"关于这个系统, 我想了解:
- 贵公司实际使用的库存锁定策略是什么?
- 在 flash sale 场景下遇到过哪些意外的挑战?"

---

### 3 分钟电梯演讲版 (3-Minute Elevator Pitch)

"设计票务/预订系统的核心挑战是**高并发下的座位强一致性**。

架构分为三层防护:
1. **流量层**: 虚拟队列控制并发 -- 百万用户排队, 每批 5000 人选座
2. **库存层**: PostgreSQL 行级锁 (`FOR UPDATE SKIP LOCKED`) 保证不超卖
3. **支付层**: 预留 TTL + 幂等 key 保证支付容错

用户流程: 排队等候 -> 获得选座令牌 -> 选座预留 (10 分钟 TTL) -> 支付确认。
超时自动释放, Redis TTL 主导 + DB 定时任务兜底。

关键设计选择: 悲观锁而非乐观锁 (高竞争场景), 虚拟队列而非直接抢 (系统稳定性),
同步支付而非异步 (库存珍贵)。"
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def populate_interview_ticket_reservation() -> None:
    """Insert/update all 8 sections for the Ticket Reservation system design."""
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
    populate_interview_ticket_reservation()
