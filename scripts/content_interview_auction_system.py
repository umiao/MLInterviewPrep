"""Populate interview-auction-system system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design an Auction System
(eBay) -- real-time bidding via WebSocket, bid ordering with monotonic timestamps,
auction state machine, sniping protection (soft close), payment escrow, reserve
price, and distributed concurrency control.
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

SLUG = "interview-auction-system"
TITLE = "Design an Auction System (eBay)"
DISPLAY_ORDER = 118

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 eBay 的**在线拍卖系统 (Online Auction System)**，支持用户创建
拍卖商品、实时出价竞拍、自动延时防狙击 (Sniping Protection)、以及拍卖结束后
的支付与履约流程。系统需要在高并发出价场景下保证数据一致性，同时为用户提供
实时的出价更新体验。

核心挑战在于：(1) **并发控制** -- 热门拍卖可能在结束前数秒内收到数千次出价，
必须保证出价排序的正确性和原子性；(2) **实时性** -- 出价者需要立即看到当前
最高价变化，延迟超过 1-2 秒会严重影响用户体验；(3) **公平性** -- 防止在最后
几秒狙击出价 (Bid Sniping)，给所有出价者公平的反应时间；(4) **支付安全** --
拍卖结束后必须确保赢家付款、卖家收款的可靠性。

### 功能性需求 (Functional Requirements)

1. **创建拍卖 (Create Auction)**: 卖家上传商品信息 (标题、描述、图片)，设置
   起拍价 (Starting Price)、保留价 (Reserve Price，可选)、拍卖时长
2. **出价 (Place Bid)**: 买家提交出价，系统验证出价金额大于当前最高价 +
   最小加价幅度 (Minimum Increment)
3. **自动代理出价 (Proxy Bidding)**: 买家设置最高出价上限，系统自动以最小
   增量代其出价，直到达到上限
4. **实时出价更新 (Real-time Bid Updates)**: 所有关注该拍卖的用户实时收到
   最新出价通知
5. **防狙击延时 (Anti-Sniping / Soft Close)**: 拍卖结束前 N 分钟内有新出价
   则自动延长拍卖时间
6. **拍卖结束与结算 (Auction Close & Settlement)**: 自动判定赢家、触发支付
   流程、通知买卖双方

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 拍卖系统宕机直接导致交易损失，
  不可接受长时间不可用
- **延迟 (Latency)**: 出价请求 P99 < 200ms (写入)；出价更新推送 P99 < 500ms
  (WebSocket 推送)
- **一致性 (Consistency)**: 出价排序**强一致性** -- 不允许出现两个用户同时
  认为自己是最高出价者的情况
- **可扩展性 (Scalability)**: 支持 1 亿 DAU (Daily Active Users)，
  峰值 50 万并发拍卖，单个热门拍卖 10,000+ 并发出价者
- **持久性 (Durability)**: 出价记录零丢失 -- 每一次合法出价都必须被永久记录
- **安全性 (Security)**: 防止 Shill Bidding (托儿出价)、出价篡改、重放攻击

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 支持哪些拍卖类型? 仅英式拍卖 (English Auction) 还是也包括荷兰式
   (Dutch Auction) / 密封出价 (Sealed Bid)?**
   -- WHY: 不同拍卖类型的出价逻辑、状态机和并发控制策略完全不同。
   英式拍卖需要实时更新，密封出价则只在结束时揭晓

2. **Q: 是否需要支持代理出价 (Proxy Bidding)?**
   -- WHY: 代理出价要求系统在收到新出价时自动触发代理竞价逻辑，
   增加写路径的复杂度和延迟

3. **Q: 拍卖结束时间是硬截止 (Hard Close) 还是软关闭 (Soft Close)?**
   -- WHY: 软关闭需要动态延长结束时间的机制，影响调度器设计和并发控制

4. **Q: 支付是平台托管 (Escrow) 还是买卖双方直接交易?**
   -- WHY: 托管模式需要与支付网关集成、冻结资金、处理退款等额外基础设施

5. **Q: 单个拍卖的最大并发出价者规模?**
   -- WHY: 决定是否需要单独的热点拍卖 (Hot Auction) 隔离策略，
   如专用实例或出价排队机制

6. **Q: 是否需要实时出价历史 (Bid History) 展示?**
   -- WHY: 公开出价历史影响反欺诈策略 (Shill Bidding 检测)，
   同时需要考虑隐私保护 (是否显示出价者身份)

7. **Q: 平台收取的费用模型是什么? 固定费率还是阶梯费率?**
   -- WHY: 费用计算逻辑影响结算服务的设计复杂度

### 不在设计范围内 (Out of Scope)

- 商品搜索和推荐引擎 (独立系统)
- 用户注册和身份认证 (假设已有 Auth 服务)
- 商品物流和配送追踪
- 卖家信誉评分系统
- 国际化多币种支持 (假设单一币种)
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 系统组件概览 (Component Overview)

```
Client (Web/Mobile App)
    |
    v
[API Gateway / Load Balancer]
    |
    +---> [Auction Service]  -- 拍卖 CRUD、状态机管理
    |         |
    |         +--> [Auction DB: PostgreSQL] -- 拍卖元数据、状态
    |
    +---> [Bid Service]  -- 出价验证、排序、代理出价
    |         |
    |         +--> [Bid DB: PostgreSQL]  -- 出价记录 (append-only)
    |         +--> [Redis Cluster]  -- 当前最高价缓存、分布式锁
    |
    +---> [WebSocket Service]  -- 实时出价推送
    |         |
    |         +--> [Redis Pub/Sub]  -- 跨实例消息广播
    |
    +---> [Scheduler Service]  -- 拍卖开始/结束调度
    |         |
    |         +--> [Delay Queue: Redis ZSET / RabbitMQ]
    |
    +---> [Settlement Service]  -- 结算、支付、通知
    |         |
    |         +--> [Payment Gateway]  -- Stripe / PayPal
    |         +--> [Escrow DB]  -- 资金托管记录
    |
    +---> [Notification Service]  -- 邮件/推送/SMS
              |
              +--> [Kafka]  -- 异步通知队列
```

### 核心服务与职责 (Core Services)

**1. Auction Service (拍卖服务)**
- 管理拍卖生命周期：创建 -> 待开始 -> 进行中 -> 即将结束 -> 已结束 -> 结算中 -> 完成
- 拍卖状态机 (Auction State Machine) 的唯一写入者
- 验证卖家权限、商品信息完整性

**2. Bid Service (出价服务)**
- 核心写路径：验证出价 -> 获取分布式锁 -> 比较当前最高价 -> 写入出价记录 -> 更新缓存 -> 释放锁
- 代理出价 (Proxy Bidding) 引擎：收到新出价后，检查是否有其他用户的代理出价上限更高，自动触发竞价
- 出价幂等性保证 (Idempotency Key)

**3. WebSocket Service (实时推送服务)**
- 维护每个拍卖的订阅者列表 (Channel per Auction)
- 通过 **Redis Pub/Sub** 实现跨 WebSocket 实例的消息广播
- 推送内容：最新出价金额、出价者 (匿名化)、剩余时间、防狙击延长通知

**4. Scheduler Service (调度服务)**
- 使用 **Redis Sorted Set** (ZSET) 作为延迟队列，score = 拍卖结束时间戳
- 定时轮询到期拍卖，触发 Auction Close 事件
- 防狙击延长：收到延时事件后，更新 ZSET 中对应拍卖的 score

**5. Settlement Service (结算服务)**
- 拍卖结束后：确定赢家 -> 冻结赢家资金 (Escrow) -> 通知卖家发货 -> 确认收货后放款
- 处理流拍 (未达到保留价)、赢家不付款 (Second-chance Offer) 等异常情况

### 数据库选型 (Database Choices)

| 数据类型 | 存储方案 | 理由 |
|---------|---------|------|
| 拍卖元数据 | **PostgreSQL** | 需要事务保证、复杂查询 (搜索、筛选)、关系建模 |
| 出价记录 | **PostgreSQL** (分区表) | Append-only, 按 auction_id 分区; 需要强一致性和事务 |
| 当前最高价 | **Redis** | 低延迟读写 (< 1ms)，原子操作 (WATCH/MULTI) |
| 实时推送 | **Redis Pub/Sub** | 跨实例消息广播，低延迟 |
| 拍卖结束调度 | **Redis ZSET** | 高效的到期轮询 (ZRANGEBYSCORE)，O(log N) 插入 |
| 支付记录 | **PostgreSQL** | ACID 事务，审计日志 |
| 异步事件 | **Kafka** | 高吞吐、持久化、解耦结算和通知 |

### 通信模式 (Communication Patterns)

- **同步 (REST/gRPC)**: 出价提交 (需要即时响应)、拍卖 CRUD
- **异步 (Kafka)**: 结算触发、通知发送、反欺诈分析
- **实时双向 (WebSocket)**: 出价更新推送、拍卖倒计时同步
- **定时 (Scheduler)**: 拍卖开始/结束事件
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 核心 API 端点 (REST API Endpoints)

#### 1. 创建拍卖 (Create Auction)
```
POST /api/v1/auctions
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "title": "Vintage Rolex Submariner 1968",
  "description": "Original condition, all papers...",
  "category_id": 281,
  "images": ["s3://auction-img/abc123.jpg", ...],
  "starting_price": 5000.00,
  "reserve_price": 15000.00,       // optional, hidden
  "min_increment": 100.00,
  "duration_hours": 168,            // 7 days
  "soft_close_window_min": 5        // anti-sniping: 5 min
}

Response (201 Created):
{
  "auction_id": "AUC-20260408-X7K9",
  "status": "SCHEDULED",
  "start_time": "2026-04-08T18:00:00Z",
  "end_time": "2026-04-15T18:00:00Z",
  "current_price": 5000.00
}
```

#### 2. 提交出价 (Place Bid)
```
POST /api/v1/auctions/{auction_id}/bids
Authorization: Bearer {token}
Idempotency-Key: {uuid}

Request:
{
  "amount": 5200.00,
  "max_proxy_amount": 8000.00    // optional: proxy bidding
}

Response (201 Created):
{
  "bid_id": "BID-9F3A2B",
  "auction_id": "AUC-20260408-X7K9",
  "status": "ACCEPTED",
  "your_bid": 5200.00,
  "current_price": 5200.00,
  "is_highest_bidder": true,
  "end_time": "2026-04-15T18:00:00Z"  // may extend if soft close triggered
}

Error (409 Conflict):
{
  "error": "BID_TOO_LOW",
  "current_price": 5300.00,
  "min_next_bid": 5400.00
}
```

#### 3. 获取拍卖详情 (Get Auction Details)
```
GET /api/v1/auctions/{auction_id}

Response (200):
{
  "auction_id": "AUC-20260408-X7K9",
  "title": "Vintage Rolex Submariner 1968",
  "status": "ACTIVE",
  "current_price": 12500.00,
  "bid_count": 47,
  "start_time": "2026-04-08T18:00:00Z",
  "end_time": "2026-04-15T18:03:27Z",  // extended by soft close
  "reserve_met": true,
  "time_remaining_sec": 3207,
  "highest_bidder": "u***r42"  // anonymized
}
```

#### 4. 获取出价历史 (Get Bid History)
```
GET /api/v1/auctions/{auction_id}/bids?page=1&limit=20

Response (200):
{
  "bids": [
    {"bid_id": "BID-9F3A2B", "bidder": "u***r42", "amount": 12500.00,
     "timestamp": "2026-04-15T17:58:27Z", "is_proxy": false},
    ...
  ],
  "total_bids": 47,
  "page": 1
}
```

#### 5. WebSocket 实时订阅 (Real-time Subscribe)
```
WS /ws/auctions/{auction_id}

Server -> Client messages:
{
  "type": "NEW_BID",
  "current_price": 12600.00,
  "bidder": "u***r15",
  "bid_count": 48,
  "timestamp": "2026-04-15T18:01:05Z"
}

{
  "type": "TIME_EXTENDED",
  "new_end_time": "2026-04-15T18:06:05Z",
  "reason": "SOFT_CLOSE"
}

{
  "type": "AUCTION_ENDED",
  "winner": "u***r42",
  "final_price": 12600.00,
  "reserve_met": true
}
```

### 核心数据模型 (Core Data Models)

```sql
-- 拍卖表 (Auctions)
CREATE TABLE auctions (
    auction_id      VARCHAR(24) PRIMARY KEY,
    seller_id       BIGINT NOT NULL REFERENCES users(id),
    title           VARCHAR(256) NOT NULL,
    description     TEXT,
    category_id     INT NOT NULL,
    starting_price  DECIMAL(12,2) NOT NULL,
    reserve_price   DECIMAL(12,2),          -- NULL = no reserve
    min_increment   DECIMAL(12,2) NOT NULL DEFAULT 1.00,
    current_price   DECIMAL(12,2) NOT NULL,
    bid_count       INT NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED',
        -- SCHEDULED -> ACTIVE -> ENDING -> CLOSED -> SETTLING -> COMPLETED / CANCELLED
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,
    original_end    TIMESTAMPTZ NOT NULL,   -- before soft-close extensions
    soft_close_min  INT NOT NULL DEFAULT 5,
    winner_id       BIGINT REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version         INT NOT NULL DEFAULT 0  -- optimistic locking
);
CREATE INDEX idx_auctions_status_end ON auctions(status, end_time);
CREATE INDEX idx_auctions_seller ON auctions(seller_id);

-- 出价表 (Bids) -- append-only, partitioned by auction_id hash
CREATE TABLE bids (
    bid_id          VARCHAR(16) PRIMARY KEY,
    auction_id      VARCHAR(24) NOT NULL REFERENCES auctions(auction_id),
    bidder_id       BIGINT NOT NULL REFERENCES users(id),
    amount          DECIMAL(12,2) NOT NULL,
    max_proxy       DECIMAL(12,2),          -- NULL = no proxy
    is_proxy_auto   BOOLEAN DEFAULT FALSE,  -- auto-placed by proxy engine
    idempotency_key UUID UNIQUE,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACCEPTED',
        -- ACCEPTED, OUTBID, WINNING, WON, RETRACTED
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY HASH (auction_id);
CREATE INDEX idx_bids_auction_amount ON bids(auction_id, amount DESC);

-- 支付托管表 (Escrow)
CREATE TABLE escrow (
    escrow_id       BIGSERIAL PRIMARY KEY,
    auction_id      VARCHAR(24) NOT NULL REFERENCES auctions(auction_id),
    buyer_id        BIGINT NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
        -- PENDING -> AUTHORIZED -> CAPTURED -> RELEASED / REFUNDED
    payment_intent  VARCHAR(64),            -- Stripe payment intent ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 写路径: 出价流程 (Write Path: Bid Flow)

1. **客户端** 提交出价 `POST /api/v1/auctions/{id}/bids`
2. **API Gateway** 路由到 **Bid Service** 实例
3. **Bid Service** 验证:
   - 拍卖状态 = ACTIVE 或 ENDING
   - 出价者 != 卖家 (防止 Shill Bidding)
   - 幂等性检查: `idempotency_key` 未被使用过
4. **获取分布式锁**: `Redis SETNX auction:{id}:lock` (TTL = 2s)
5. **读取当前最高价**: `Redis GET auction:{id}:current_price`
6. **验证出价**: `amount >= current_price + min_increment`
7. **写入出价记录**: `INSERT INTO bids ...`
8. **更新拍卖状态**: `UPDATE auctions SET current_price = ..., bid_count = bid_count + 1`
9. **更新 Redis 缓存**: `SET auction:{id}:current_price {amount}`
10. **释放锁**: `DEL auction:{id}:lock`
11. **发布事件**: `Redis PUBLISH auction:{id} {bid_event_json}`
12. **代理出价检查**: 如果存在其他用户的代理出价上限 > 当前出价，自动触发步骤 4-11
13. **防狙击检查**: 如果距离结束时间 < `soft_close_min`，延长 `end_time`，更新调度器

### 读路径: 拍卖详情 (Read Path: Auction Details)

1. **客户端** 请求 `GET /api/v1/auctions/{id}`
2. **API Gateway** 路由到 **Auction Service**
3. **先查 Redis 缓存**: `GET auction:{id}:detail` -- 缓存命中则直接返回 (TTL = 5s)
4. **缓存未命中**: 查询 PostgreSQL `auctions` 表
5. **写入缓存**: `SETEX auction:{id}:detail 5 {json}` -- 短 TTL 因为价格频繁变化
6. **返回结果**: 包含计算字段 `time_remaining_sec`、`reserve_met` (布尔，不暴露具体保留价)
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Capacity Estimation)

**基础假设:**
- DAU = 1 亿 (100M)
- 日活跃拍卖数 = 5000 万 (50M)
- 日新建拍卖 = 500 万 (5M)
- 平均每个拍卖收到 20 次出价
- 平均拍卖时长 = 7 天

**QPS 计算:**

$$
\text{日总出价数} = 50M \times 20 / 7 \approx 143M \text{ bids/day}
$$

$$
\text{平均出价 QPS} = \frac{143M}{86400} \approx 1,655 \text{ bids/sec}
$$

$$
\text{峰值出价 QPS} = 1,655 \times 5 \approx 8,275 \text{ bids/sec}
$$

$$
\text{拍卖详情读 QPS} = 1,655 \times 50 \approx 82,750 \text{ reads/sec (50:1 read-write ratio)}
$$

$$
\text{峰值读 QPS} = 82,750 \times 3 \approx 248,250 \text{ reads/sec}
$$

**存储估算:**

$$
\text{单条出价记录} \approx 200 \text{ bytes}
$$

$$
\text{日出价存储} = 143M \times 200B = 28.6 \text{ GB/day}
$$

$$
\text{年出价存储} = 28.6 \times 365 \approx 10.4 \text{ TB/year}
$$

$$
\text{单条拍卖记录} \approx 2 \text{ KB (含图片 URL)}
$$

$$
\text{日拍卖存储} = 5M \times 2KB = 10 \text{ GB/day}
$$

**带宽估算:**

$$
\text{出价写入带宽} = 8,275 \times 500B \approx 4.1 \text{ MB/s (peak)}
$$

$$
\text{读取带宽} = 248,250 \times 2KB \approx 496 \text{ MB/s (peak)}
$$

**内存 (Redis 缓存):**

$$
\text{活跃拍卖缓存} = 50M \times 500B \approx 25 \text{ GB}
$$

$$
\text{热门拍卖详情缓存 (top 1\%)} = 500K \times 5KB = 2.5 \text{ GB}
$$

$$
\text{Redis 总需求} \approx 30 \text{ GB (4 个 Redis 节点, 每节点 8GB)}
$$

**WebSocket 连接数:**

$$
\text{峰值并发 WebSocket} \approx 1\% \times 100M = 1M \text{ connections}
$$

$$
\text{WebSocket 服务器数} = \frac{1M}{50K \text{ conn/server}} = 20 \text{ servers}
$$

### 核心算法: 代理出价 (Proxy Bidding Algorithm)

代理出价 (Proxy Bidding) 是 eBay 的核心创新之一。买家设置一个**最高出价上限
(Maximum Bid)**，系统自动以最小增量代其出价:

```python
def process_proxy_bid(auction_id: str, new_bid_amount: float,
                      new_bidder_id: str, new_max_proxy: float | None):
    # Process a new bid and trigger proxy bidding if applicable.
    current_highest = get_current_bid(auction_id)

    # Find the highest proxy bid among other bidders
    other_proxies = get_active_proxies(auction_id, exclude=new_bidder_id)
    best_proxy = max(other_proxies, key=lambda p: p.max_proxy, default=None)

    if best_proxy and best_proxy.max_proxy > new_bid_amount:
        # Existing proxy outbids the new bid
        auto_amount = min(
            best_proxy.max_proxy,
            new_bid_amount + auction.min_increment
        )
        place_auto_bid(auction_id, best_proxy.bidder_id, auto_amount)
    elif new_max_proxy and new_max_proxy > new_bid_amount:
        # New bidder's proxy will defend against future bids
        # Current price stays at new_bid_amount (no need to auto-raise)
        pass
```

### 核心算法: 防狙击软关闭 (Anti-Sniping Soft Close)

$$
\text{剩余时间} = t_{end} - t_{now}
$$

$$
\text{如果 } \text{剩余时间} < W_{soft} \text{ 且收到新出价, 则: } t_{end}' = t_{now} + W_{soft}
$$

其中 $W_{soft}$ 是软关闭窗口 (Soft Close Window)，通常为 5-10 分钟。这确保
每次出价后，所有参与者至少有 $W_{soft}$ 时间做出回应。

**最大延长时间约束:**

$$
t_{end}' \leq t_{original} + T_{max\_ext}
$$

其中 $T_{max\_ext}$ 通常为原拍卖时长的 50% (例如 7 天拍卖最多延长 3.5 天)，
防止无限延长。

### 出价排序: 单调时间戳 (Monotonic Timestamps)

在分布式系统中，多个 Bid Service 实例的系统时钟可能存在偏差。使用
**Snowflake ID** 或 **单调递增序列号 (Monotonic Sequence)** 来保证出价排序:

$$
\text{bid\_order} = (\text{timestamp\_ms} \ll 22) \mid (\text{node\_id} \ll 12) \mid \text{sequence}
$$

这保证: 即使两个出价在同一毫秒到达不同节点，也能通过 node_id 和 sequence
区分先后顺序。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性深入分析 (Scale & Reliability Deep Dive)

### 具体规模数字 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 1 亿 |
| 日活跃拍卖 | 5000 万 |
| 峰值出价 QPS | 8,275 |
| 峰值读 QPS | 248,250 |
| WebSocket 并发连接 | 1M |
| Redis 集群总内存 | 30 GB |
| 日出价存储 | 28.6 GB |
| Bid Service 实例数 | 20-30 (水平扩展) |
| WebSocket 服务器数 | 20 |
| PostgreSQL 节点 | 1 主 + 3 只读副本 (出价表分区) |

### 单点故障分析 (Single Point of Failure Analysis)

**1. Redis (当前最高价缓存) 故障**
- **风险**: 无法读取当前最高价，所有出价验证失败
- **缓解**: Redis Sentinel / Cluster 模式，自动故障转移 (< 30s)
- **降级策略**: 回退到 PostgreSQL 直接读取 (延迟增加 ~5ms，仍可接受)

**2. Bid Service 实例故障**
- **风险**: 部分出价请求失败
- **缓解**: 无状态设计，Load Balancer 自动摘除不健康实例
- **恢复时间**: < 10s (健康检查间隔)

**3. Scheduler Service 故障**
- **风险**: 拍卖无法按时结束
- **缓解**: 多实例部署 + **Leader Election** (ZooKeeper / etcd)，
  只有 Leader 执行调度，Follower 待命。Leader 故障后 < 5s 切换
- **兜底**: 拍卖详情 API 自行检查 `end_time` 并标记过期

**4. PostgreSQL 主库故障**
- **风险**: 无法写入出价记录
- **缓解**: 同步复制到至少 1 个 Standby，自动 Failover (Patroni)
- **RPO**: 0 (同步复制，零数据丢失)；**RTO**: < 30s

### 多数据中心设计 (Multi-Datacenter Considerations)

**架构选择: Active-Passive (主动-被动)**

拍卖出价需要**强一致性** (不能出现两个数据中心同时接受冲突的出价)，因此不适合
Active-Active 架构。

| 方面 | 设计 |
|------|------|
| **写入** | 所有出价路由到主数据中心 (Primary DC) |
| **读取** | 就近读取 (本地 DC 的只读副本)，接受短暂延迟 (< 1s) |
| **复制** | PostgreSQL 异步流复制到备用 DC (RPO < 1s) |
| **故障转移** | DNS Failover + 手动确认 (避免脑裂)，RTO 约 2-5 分钟 |
| **WebSocket** | 每个 DC 独立的 WebSocket 集群，通过 Kafka 跨 DC 同步事件 |

**跨区域延迟优化:**
- 美国西部用户出价到美东主 DC 增加约 60-80ms 网络延迟
- 使用 **Edge POP (接入点)** 进行 TLS 终止和请求预验证 (格式检查、
  频率限制)，减少无效请求到主 DC 的流量
- 拍卖详情页的静态内容 (图片、描述) 通过 **CDN** 就近缓存

### 高并发出价处理 (High Concurrency Bid Handling)

**热门拍卖隔离 (Hot Auction Isolation):**

当单个拍卖在短时间内收到大量出价 (如名人物品拍卖)，可能造成:
- Redis 锁争用严重
- PostgreSQL 单行频繁更新导致锁等待

**解决方案: 分层出价管道 (Tiered Bid Pipeline)**

```
Layer 1: Edge Rate Limiting
    每用户每拍卖每秒最多 1 次出价
    |
Layer 2: Bid Queue (Kafka partition by auction_id)
    热门拍卖的出价先进入队列，串行处理
    保证同一拍卖的出价被路由到同一 Consumer
    |
Layer 3: Sequential Bid Processor
    从队列中顺序读取出价，逐个验证和写入
    无需分布式锁 (因为已是单线程处理)
    |
Layer 4: Batch Update + Broadcast
    每 100ms 批量更新 Redis + 广播 WebSocket
```

**优势**: 热门拍卖被隔离到专用 Kafka 分区，不影响其他普通拍卖的实时出价处理。

**速率限制 (Rate Limiting):**
- 全局: 每用户 100 次出价/分钟
- 每拍卖: 每用户每拍卖 1 次出价/秒
- 使用 **Token Bucket** 算法，Redis `INCR` + `EXPIRE` 实现

**熔断器 (Circuit Breaker):**
- 当 Bid Service -> PostgreSQL 的错误率超过 30%，触发熔断
- 熔断期间返回 503，引导用户稍后重试
- 半开状态: 每 5 秒放行 1 个请求探测恢复

**优雅降级 (Graceful Degradation):**
- PostgreSQL 延迟高时: 出价先写入 Kafka，异步落库 (最终一致性)
- Redis 不可用时: 回退到数据库直接读取最高价
- WebSocket 服务过载时: 降级为长轮询 (Long Polling)，增大推送间隔至 2-3 秒

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 | 原因 |
|------|----------|------|
| 出价 P99 延迟 | > 500ms | 影响用户体验和竞价公平性 |
| Redis 锁等待时间 | > 100ms | 锁争用严重，可能需要启用热门拍卖隔离 |
| WebSocket 连接失败率 | > 1% | 用户无法接收实时更新 |
| 拍卖结束延迟 | > 30s (相对于 end_time) | 调度器可能故障 |
| 出价写入失败率 | > 0.1% | 数据库或锁服务异常 |
| Kafka Consumer Lag | > 10,000 messages | 结算或通知服务处理缓慢 |
| Escrow 结算超时 | > 1 小时 | 支付网关或结算服务异常 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|------------------|
| **并发控制** | 乐观锁 (Optimistic Lock, version 字段) | 分布式锁 (Redis SETNX) | **Redis 分布式锁**。乐观锁在高争用场景 (热门拍卖) 下重试率极高 (>50%)，而分布式锁保证每次获锁后一定成功，P99 延迟更可预测。对于超热门拍卖进一步升级为 Kafka 串行化 |
| **实时推送** | WebSocket (全双工, 长连接) | SSE (Server-Sent Events, 单向) | **WebSocket**。虽然 SSE 更简单、对 HTTP/2 友好，但拍卖场景需要客户端发送心跳、重连确认等双向通信；且 WebSocket 的每连接内存开销 (~50KB) 在 1M 连接规模下仍可接受 (~50GB, 20 台服务器) |
| **出价存储** | 实时写入 PostgreSQL | 先写 Kafka 后异步落库 | **正常拍卖实时写 PG，热门拍卖异步写**。出价记录是核心资产，正常情况下同步写入 PG 保证强一致性 (出价者立即确认)。只有当 PG 延迟超过阈值时，降级为 Kafka 缓冲 |
| **拍卖结束检测** | 定时轮询 (Scheduler pull) | 事件驱动 (Delay Queue push) | **Redis ZSET 延迟队列 + 定时轮询**。纯事件驱动在调度器重启时可能丢失事件；ZSET 具有持久性 (RDB/AOF) 且支持高效范围查询，10ms 内可获取所有到期拍卖 |
| **数据中心策略** | Active-Active (双活) | Active-Passive (主备) | **Active-Passive**。出价的强一致性需求使双活的冲突解决成本极高 (两个 DC 同时接受"最高价"出价怎么裁决?)。牺牲写延迟 (跨区 +60-80ms) 换取数据正确性 |

### 一致性 vs 可用性 (Consistency vs Availability)

**CAP 定理在拍卖系统中的体现:**

出价路径选择**CP (一致性优先)**:
- 绝不允许两个用户同时认为自己是最高出价者
- 在网络分区期间，备用 DC 的出价功能不可用 (返回 503)
- 代价: 主 DC 故障时出价暂停 2-5 分钟

拍卖浏览路径选择**AP (可用性优先)**:
- 允许只读副本上的价格信息延迟 < 1 秒
- 用户可以继续浏览拍卖列表、查看商品详情
- 代价: 短暂看到的"当前价格"可能不是最新值

### 成本 vs 性能 (Cost vs Performance)

| 优化策略 | 性能提升 | 成本增加 | 选择 |
|----------|----------|----------|------|
| Redis Cluster (8 节点) | 读延迟 < 1ms | 约 3,000 美元/月 | 采用 -- 出价延迟直接影响收入 |
| WebSocket 专用集群 (20 节点) | 实时推送 < 500ms | 约 8,000 美元/月 | 采用 -- 核心用户体验 |
| PostgreSQL 出价表分区 (16 partitions) | 写入吞吐 4x | DBA 维护复杂度 | 采用 -- 必要的扩展手段 |
| 全球多 DC (3 region) | 读延迟 -50ms | 3x 基础设施成本 | 暂缓 -- 先用 CDN + Edge POP 缓解 |

### 10x / 100x 规模变化 (Scaling Analysis)

**10x 规模 (10 亿 DAU, 5 亿活跃拍卖):**
- PostgreSQL 出价表需要分库分表 (Sharding by auction_id)，单库无法承受
  80K+ 写 QPS
- Redis 集群扩展到 40+ 节点
- WebSocket 连接数 10M，需要 200+ 台服务器
- 引入 **Auction Partitioning**: 不同拍卖分配到不同的 Bid Service 集群，
  减少跨拍卖的资源争用

**100x 规模 (100 亿交互, 全球多区域):**
- 必须转向 Active-Active 多主架构:
  - 每个区域独立处理本区域拍卖的出价
  - 跨区域拍卖使用 **CRDT (Conflict-free Replicated Data Type)** 解决冲突
  - 或者限制热门拍卖只能在一个 "Home Region" 出价
- 出价存储迁移到分布式数据库 (如 **CockroachDB** / **TiDB**)
- Kafka 替换为全球分布式消息系统 (如 **Pulsar** with Geo-replication)
- 引入 ML 模型预测"热门拍卖"，提前分配更多资源
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果 Redis 集群整体宕机怎么办? 出价系统能否继续工作?

**承认局限**: Redis 全集群故障确实会严重影响出价延迟和 WebSocket 推送。

**缓解措施**:
1. **出价路径降级**: Bid Service 直接查询 PostgreSQL 获取当前最高价。
   延迟从 < 1ms 增加到 ~5ms，仍在可接受范围内。使用 **SELECT ... FOR UPDATE**
   替代 Redis 分布式锁实现行级锁
2. **WebSocket 降级**: 切换为客户端 **Long Polling** (每 2 秒轮询一次)。
   用户体验降级但功能不中断
3. **数据恢复**: Redis 配置 AOF (每秒 fsync)，重启后自动加载最近的持久化数据；
   缓存可以从 PostgreSQL 重建 (全量拍卖状态同步需约 5 分钟)

**数据支撑**: AWS ElastiCache Redis 的 SLA 为 99.99%，年停机时间 < 52 分钟。
配合 Multi-AZ 部署和自动故障转移，全集群不可用的概率极低。

### Q2: 如果拍卖结束前最后 1 秒有 10,000 个出价同时到达怎么办?

**承认局限**: 这是典型的"雷群效应 (Thundering Herd)"问题，直接处理会导致
锁争用和大量重试。

**缓解措施**:
1. **Kafka 串行化**: 热门拍卖的出价先进入 Kafka 分区 (keyed by auction_id)，
   单个 Consumer 顺序处理。将 10,000 并发请求转化为 10,000 顺序请求
2. **批处理优化**: Consumer 每 50ms 批量读取出价，取最高的一个写入 DB，
   其余直接标记为 `OUTBID`。10,000 个出价实际只需约 200 次 DB 写入
3. **Soft Close 兜底**: 即使部分出价来不及处理，Soft Close 延长 5 分钟
   给了充足的缓冲时间

**数据支撑**: Kafka 单分区可以处理 100K+ msg/s，处理 10,000 个出价仅需 ~100ms。

### Q3: 两个用户在同一毫秒提交相同金额的出价，如何裁定谁是赢家?

**承认局限**: 在分布式系统中，"谁先到"是一个具有哲学意味的问题。时钟同步
(NTP) 的精度通常只有毫秒级。

**缓解措施**:
1. **唯一排序键**: 使用 **Snowflake ID** 作为出价序号。即使时间戳相同，
   `node_id` 和 `sequence` 字段保证全局唯一排序
2. **先到先得 (FIFO)**: 当金额相同时，`bid_order` 更小的出价胜出。
   在 Kafka 串行化方案中，消息进入分区的顺序就是最终裁决顺序
3. **透明规则**: 用户出价时显示"相同金额以先提交者为准"的提示，
   管理用户预期

**设计选择**: eBay 实际使用代理出价 (Proxy Bidding) 而非"同价先到"——
如果两个用户出价相同金额，代理出价更早设置的用户胜出。这减少了对时间戳
精度的依赖。

### Q4: 如何防止 Shill Bidding (卖家或同伙自己出价抬高价格)?

**承认局限**: Shill Bidding 是拍卖系统中最难完全消除的欺诈行为之一。

**缓解措施**:
1. **规则引擎 (实时)**:
   - 禁止卖家对自己的拍卖出价 (seller_id != bidder_id)
   - 禁止同一 IP / 设备指纹的不同账户在同一拍卖中互相竞价
   - 检测"总是出价但从不赢"的账户模式
2. **ML 异常检测 (离线)**:
   - 社交图谱分析: 关联出价者之间的 IP 重叠、收货地址重叠、支付方式关联
   - 出价模式分析: 出价金额总是恰好比上一个出价高最小增量 (自动化脚本特征)
   - 时间序列异常: 某卖家的拍卖总是在最后几秒被"不同用户"推高价格
3. **处罚机制**: 确认 Shill Bidding 后: 冻结账户、取消交易、罚款

**数据支撑**: eBay 每年处理数十亿次出价，其 Trust & Safety 团队使用
200+ 个信号进行实时欺诈检测，误判率 < 0.01%。

### Q5: 如果突然有一个超级热门拍卖 (如名人慈善拍卖)，流量是平常的 100 倍怎么办?

**承认局限**: 突发的极端流量是预案之外的，预先扩容的资源可能不够。

**缓解措施**:
1. **预热机制**: 高关注度拍卖提前标记为"热门"，预分配更多 Kafka 分区、
   Redis 缓存、WebSocket 连接槽
2. **自动扩缩容 (Auto-scaling)**: Bid Service 和 WebSocket Service 基于
   CPU / 连接数自动水平扩展 (Kubernetes HPA, 扩容时间 < 2 分钟)
3. **出价排队 + 响应降级**: 超过处理能力时，出价进入排队 (Kafka)，
   返回 202 Accepted (而非 201 Created)，异步通知结果
4. **WebSocket 分级推送**: 出价频率极高时，不再逐笔推送，改为每秒
   汇总推送 (当前价、出价次数、倒计时)，减少消息量 90%+
5. **CDN 缓存拍卖页面**: 拍卖详情的静态部分 (标题、描述、图片) 缓存在
   CDN，仅动态数据 (价格、出价数) 通过 WebSocket 更新
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试口述大纲 (1-Hour Interview Pacing Guide)

### 三分钟电梯演讲版 (3-Minute Elevator Pitch)

"设计拍卖系统的核心挑战是**在高并发下保证出价的强一致性和实时性**。
我的方案分三层:

**第一层: 出价管道**。正常拍卖使用 Redis 分布式锁 + PostgreSQL 实时写入，
P99 延迟 < 200ms。热门拍卖自动升级为 Kafka 串行化管道，将并发出价转为
顺序处理，避免锁争用。

**第二层: 实时推送**。通过 WebSocket + Redis Pub/Sub 实现跨实例的实时
出价广播。1M 并发连接用 20 台服务器承载。高峰期降级为批量汇总推送。

**第三层: 拍卖生命周期管理**。Redis ZSET 延迟队列驱动拍卖开始/结束调度。
Soft Close 防狙击机制确保公平性。结算通过 Kafka 异步触发，Escrow 模式
保障支付安全。

整个系统选择 Active-Passive 多 DC 架构，出价路径 CP 优先保证一致性，
浏览路径 AP 优先保证可用性。"

---

### 完整一小时面试节奏 (Full 1-Hour Pacing)

#### 0-5 分钟: 需求澄清 (Requirements Clarification)
- **开场**: "拍卖系统的核心是保证出价排序的正确性和实时用户体验。让我先
  澄清几个关键需求。"
- 确认拍卖类型: 英式拍卖 (递增出价, 公开)
- 确认是否需要代理出价 (Proxy Bidding) -- 增加复杂度但是 eBay 核心特性
- 确认结束策略: Hard Close vs Soft Close (防狙击)
- 确认支付模式: 平台托管 (Escrow)
- 列出 FR / NFR:
  - FR: 创建拍卖、出价、代理出价、实时更新、防狙击、结算
  - NFR: 99.99% 可用性, P99 出价 < 200ms, 强一致出价排序
- 明确 Out of Scope: 搜索推荐、物流、多币种

#### 5-15 分钟: 高层架构 (High-Level Architecture)
- 画出 5 个核心服务: Auction Service, Bid Service, WebSocket Service,
  Scheduler Service, Settlement Service
- **数据库选型理由**:
  - PostgreSQL: 事务保证 (出价记录 ACID), 复杂查询
  - Redis: 当前最高价缓存 (< 1ms), 分布式锁, Pub/Sub, 延迟队列
  - Kafka: 解耦结算和通知、热门拍卖出价缓冲
- **通信模式**: REST (出价提交), WebSocket (实时推送),
  Kafka (异步事件)

#### 15-25 分钟: 深入出价管道 (Deep Dive: Bid Pipeline)
- 走通出价的完整写路径 (12 个步骤)
- **重点讨论**:
  - 并发控制: Redis 分布式锁 vs 乐观锁 vs DB 行锁
  - 代理出价引擎的触发逻辑
  - 幂等性设计 (Idempotency Key)
- **热门拍卖隔离**: Kafka 串行化方案
  - 为什么选 Kafka 而不是内存队列: 持久性 + 分区隔离

#### 25-35 分钟: 深入实时推送与防狙击 (Deep Dive: Real-time & Anti-Sniping)
- **WebSocket 架构**:
  - Channel per Auction 模型
  - Redis Pub/Sub 跨实例广播
  - 连接数计算: 1M connections, 20 servers
- **Soft Close 机制**:
  - 剩余时间 < 5min 时有新出价则延长至 5min
  - 最大延长限制 (50% 原时长)
  - Scheduler 如何动态更新 ZSET score

#### 35-40 分钟: 容量估算 (Capacity Estimation)
- 快速走一遍关键数字:
  - 出价 QPS: 平均 1,655, 峰值 8,275
  - 读 QPS: 平均 82K, 峰值 248K
  - 存储: 出价 10.4 TB/年
  - Redis: 30 GB
  - WebSocket: 20 台服务器

#### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)
- 一致性 vs 可用性: 出价路径 CP, 浏览路径 AP
- Active-Passive 多 DC: 牺牲跨区写延迟换取一致性
- 10x 规模: 分库分表, WebSocket 200+ 台
- 100x 规模: Active-Active + CRDT / Home Region

#### 50-55 分钟: 收尾 (Wrap-up)
- **如果有更多时间我会改进什么**:
  - ML 实时欺诈检测 (Shill Bidding)
  - 全球 Active-Active 架构 (CRDT for bids)
  - 拍卖推荐引擎 (个性化首页)
- **监控优先级**: 出价 P99 延迟, 锁争用率, WebSocket 连接成功率
- **最大风险**: 热门拍卖的雷群效应 -- 已通过 Kafka 串行化缓解

#### 55-60 分钟: 提问环节 (Questions for Interviewer)
- "在你们的系统中，类似的高并发写入场景 (如抢购/竞拍) 是如何处理的?"
- "你们在实时推送方面选择了 WebSocket 还是 SSE? 运维上有什么经验?"
"""


# ---------------------------------------------------------------------------
# Main: Populate DB
# ---------------------------------------------------------------------------
def populate_interview_auction_system() -> None:
    """Insert or update the interview-auction-system SystemDesign record."""
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
    populate_interview_auction_system()
