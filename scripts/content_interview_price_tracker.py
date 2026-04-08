"""Populate interview-price-drop-tracker system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Price Drop
Tracker (CamelCamelCamel) -- scraping pipeline, price history time-series,
alert system, anti-scraping countermeasures, product matching/dedup, and
scaling to millions of products.
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

SLUG = "interview-price-drop-tracker"
TITLE = "Design a Price Drop Tracker (CamelCamelCamel)"
DISPLAY_ORDER = 114

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**价格追踪与降价提醒系统 (Price Drop Tracker)**，类似
CamelCamelCamel 或 Keepa。用户可以添加电商平台 (Amazon, Walmart, Best Buy
等) 的商品链接，系统定期抓取价格数据，存储完整的价格历史，并在价格降至
用户设定的目标价以下时发送通知。

核心挑战在于：(1) 大规模网页抓取的效率与反爬虫对抗，(2) 海量时间序列数据
的高效存储与查询，(3) 百万级别的价格变更事件驱动实时通知，
(4) 跨平台商品匹配与去重。

### 功能性需求 (Functional Requirements)

1. **商品追踪 (Product Tracking)**: 用户提交商品 URL，系统解析并开始
   追踪该商品的价格变化
2. **价格历史 (Price History)**: 存储完整的价格时间序列数据，支持历史
   价格图表展示 (日/周/月/年视图)
3. **降价提醒 (Price Alert)**: 用户设定目标价格，当商品价格降至目标价
   以下时通过 Email/Push/SMS 发送通知
4. **价格趋势分析 (Price Trend)**: 显示历史最低价、平均价、当前价格
   相对于历史的百分位
5. **商品搜索 (Product Search)**: 按商品名、类别搜索已追踪商品的价格信息
6. **多平台支持 (Multi-Platform)**: 支持 Amazon, Walmart, Best Buy,
   Target 等主流电商平台

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.9% -- 短暂不可用可接受，但不能丢失用户的
  提醒配置
- **延迟 (Latency)**: 价格查询 P99 < 200ms；通知延迟 < 30 min (从价格变化
  到用户收到通知)
- **一致性 (Consistency)**: 最终一致 -- 价格数据允许短暂延迟 (通常 1-6 小时
  抓取间隔)；提醒配置强一致 (用户修改后立即生效)
- **可扩展性 (Scalability)**: 支持 1000 万用户，追踪 5000 万商品，
  每日 5 亿次价格抓取
- **数据持久性 (Durability)**: 价格历史数据永久保存，99.999% 持久性

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 支持哪些电商平台? 是否需要实时 API 接入还是纯网页抓取?**
   -- WHY: 有些平台提供 **Product Advertising API** (如 Amazon PA-API)，
   可直接获取价格; 其他平台只能通过 HTML 解析，架构和合规性完全不同

2. **Q: 价格抓取的频率要求是什么? 实时 vs 定期?**
   -- WHY: 实时监控 (秒级) 需要 **WebSocket/SSE** + 平台 Webhook;
   定期抓取 (小时级) 用 **Cron + 分布式任务队列** 即可。
   CamelCamelCamel 通常每 1-6 小时抓取一次

3. **Q: 需要支持多少种价格类型? 新品价、二手价、第三方卖家价?**
   -- WHY: Amazon 一个商品可能有 10+ 个价格点 (Buy Box, 新品最低价,
   二手最低价, Warehouse Deals)。每种价格都需要独立追踪曲线

4. **Q: 是否需要检测"假降价" (先涨后降的促销套路)?**
   -- WHY: 需要长期价格基线算法，涉及统计分析模块。这是高级功能，
   可以作为 Deep Dive 展开

5. **Q: 用户可以追踪多少个商品? 是否有免费/付费层级?**
   -- WHY: 影响系统规模。免费用户追踪 50 个 vs 付费用户追踪 5000 个，
   付费用户可能要求更高频率的抓取 (1 小时 vs 6 小时)

6. **Q: 需要支持哪些通知渠道? Email, Push, SMS, Browser Extension?**
   -- WHY: Email 可以批量发送，成本低; Push/SMS 需要实时推送基础设施;
   Browser Extension 可以在用户浏览商品页面时直接显示价格历史

7. **Q: 是否需要处理商品下架/缺货的情况?**
   -- WHY: 缺货商品的 URL 可能返回 404 或跳转到搜索页面，
   需要区分"价格变化"和"商品状态变化"

### 范围界定 (Out of Scope)

- 电商平台爬虫的法律合规分析 -- 假设已获授权
- 浏览器扩展开发 -- 聚焦后端系统
- 商品推荐引擎 (基于用户追踪的商品推荐相似商品)
- 价格预测 (机器学习预测未来价格走势)
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构 (High-Level Architecture)

### 组件总览 (Component Overview)

系统分为三大子系统：**数据采集层 (Data Collection Layer)**、
**数据处理与存储层 (Processing & Storage Layer)**、
**用户服务层 (User-Facing Layer)**。

```
[User] --> [API Gateway / LB]
               |
     +---------+---------+---------+
     |         |         |         |
[Product   [Alert    [Price     [Search
 Service]   Service]  History    Service]
     |         |      Service]     |
     |         |         |         |
     v         v         v         v
[Product DB] [Alert DB] [TSDB]  [Elasticsearch]
(PostgreSQL) (PostgreSQL)(InfluxDB/ (Product Index)
                        TimescaleDB)
               |
        [Message Queue]
          (Kafka/SQS)
               |
     +---------+---------+
     |                   |
[Notification        [Scraping
 Worker]              Orchestrator]
     |                   |
[Email/Push/SMS]    [Proxy Pool]
                        |
                   [Scraper Workers]
                   (Headless Chrome
                    / HTTP Parsers)
```

### 核心服务及职责 (Core Services)

#### 1. Scraping Orchestrator (抓取编排器)

整个系统的数据引擎，负责调度和管理价格抓取任务：

- **任务调度 (Task Scheduling)**: 根据商品的热度和平台限制，动态调整抓取频率
  - 高关注商品 (>100 个 watcher): 每 1 小时抓取
  - 中关注商品 (10-100 个 watcher): 每 3 小时抓取
  - 低关注商品 (<10 个 watcher): 每 6 小时抓取
  - 新添加商品: 立即触发首次抓取
- **分布式任务队列**: 使用 **Celery + Redis** 或 **AWS SQS** 分发抓取任务
  到 Worker 集群
- **平台限流 (Rate Limiting)**: 每个目标平台维护独立的令牌桶
  (**Token Bucket**)，确保不触发反爬虫机制
  - Amazon: ~1 req/s per IP
  - Walmart: ~2 req/s per IP
  - 使用 **Rotating Proxy Pool (轮换代理池)** 分散请求源 IP

#### 2. Scraper Workers (抓取工作节点)

实际执行网页解析的无状态工作节点：

- **多策略解析 (Multi-Strategy Parsing)**:
  - **API 优先**: 如果平台提供 API (Amazon PA-API, Walmart API)，优先使用
  - **HTML 解析**: 使用 **CSS Selectors** / **XPath** 提取价格元素
  - **Headless Browser**: 对于 JavaScript 渲染的页面 (SPA)，使用
    **Puppeteer** / **Playwright** 渲染后提取
- **反爬虫对抗 (Anti-Scraping Countermeasures)**:
  - **User-Agent 轮换**: 从真实浏览器 UA 列表中随机选取
  - **请求间隔随机化**: 在基准间隔上添加 +/- 30% 的随机抖动 (**Jitter**)
  - **Cookie/Session 管理**: 模拟真实浏览行为，维护 session 状态
  - **CAPTCHA 检测**: 检测到 CAPTCHA 后标记该 IP，切换代理并降速
  - **Fingerprint 多样化**: 随机化 viewport size, language, timezone 等
    浏览器指纹
- **数据验证 (Validation)**:
  - 价格合理性检查: 与历史均价偏差 > 80% 时标记为可疑，等待二次抓取确认
  - 货币一致性: 确保抓取的价格货币与商品所在市场一致
  - 缺货检测: 区分"价格=0"和"商品缺货"

#### 3. Product Service (商品服务)

管理商品元数据和跨平台商品匹配：

- **URL 解析 (URL Parsing)**: 从电商 URL 中提取商品 ID
  (如 Amazon ASIN, Walmart Item ID)
- **商品去重 (Product Dedup)**: 同一商品在不同平台的匹配
  - 基于 **UPC (Universal Product Code)** / **EAN** 条码匹配
  - 基于商品名称的**模糊匹配 (Fuzzy Matching)** (Levenshtein 距离 / TF-IDF)
  - 人工审核队列处理低置信度匹配
- **商品状态管理**: 活跃、缺货、下架、URL 失效

#### 4. Alert Service (提醒服务)

管理用户的降价提醒规则：

- **规则引擎 (Rule Engine)**: 支持多种提醒条件
  - 价格低于目标价
  - 价格较历史最高价降幅 > X%
  - 价格达到历史新低
  - 价格低于过去 N 天均价的 X%
- **通知去重**: 同一商品在同一价格区间内不重复通知 (冷却期 24 小时)
- **批量评估 (Batch Evaluation)**: 每次价格更新后，批量检查该商品的
  所有关联提醒规则

#### 5. Price History Service (价格历史服务)

管理时间序列价格数据的存储和查询：

- **降采样 (Downsampling)**: 原始数据保留 90 天，之后按天聚合
  (最低/最高/平均)，降低存储成本
- **统计计算**: 历史最低价、平均价、中位价、百分位排名
- **图表 API**: 返回指定时间范围内的价格序列，前端渲染折线图

### 数据库选择与理由 (Database Choices)

| 数据类型 | 数据库 | 理由 |
|---------|--------|------|
| 商品元数据 | PostgreSQL | 关系型, 支持 JSONB (不同平台的异构属性), 全文搜索 |
| 价格时间序列 | TimescaleDB / InfluxDB | 时间序列优化, 自动分区, 内置降采样, 高写入吞吐 |
| 用户提醒规则 | PostgreSQL (同商品库) | 与商品数据强关联, ACID 保证 |
| 商品搜索索引 | Elasticsearch | 全文搜索 + 模糊匹配 + faceted search |
| 任务队列 | Redis + SQS | 分布式任务调度, 高吞吐, 持久化 |
| 代理池状态 | Redis | 高频读写, IP 健康状态, TTL 自动过期 |

### 通信模式 (Communication Patterns)

- **用户请求 -> API 服务**: 同步 REST (商品添加, 查询价格历史)
- **抓取调度 -> Worker**: 异步消息队列 (Kafka/SQS), 保证 at-least-once delivery
- **价格更新 -> 提醒评估**: 事件驱动 (Kafka topic: `price-updates`),
  Alert Service 作为 consumer 实时消费
- **提醒触发 -> 通知发送**: 异步消息队列 (SQS -> Notification Worker),
  支持重试和 DLQ (Dead Letter Queue)
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点 (REST API Endpoints)

#### 商品追踪 (Product Tracking)

```
POST /api/v1/products/track
Body: { "url": "https://www.amazon.com/dp/B09V3KXJPB", "target_price": 299.99 }
Response: 201 Created
{
  "product_id": "prod_abc123",
  "title": "Sony WH-1000XM5",
  "current_price": 348.00,
  "platform": "amazon",
  "tracking_status": "active",
  "alert_id": "alert_xyz789"
}

GET /api/v1/products/{product_id}
Response: 200 OK
{
  "product_id": "prod_abc123",
  "title": "Sony WH-1000XM5",
  "platform": "amazon",
  "current_price": 348.00,
  "lowest_price": 278.00,
  "highest_price": 399.99,
  "average_price": 332.50,
  "price_percentile": 72,  // 当前价格高于 72% 的历史价格
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### 价格历史 (Price History)

```
GET /api/v1/products/{product_id}/prices?range=90d&granularity=daily
Response: 200 OK
{
  "product_id": "prod_abc123",
  "range": "90d",
  "granularity": "daily",
  "data_points": [
    { "timestamp": "2024-01-15", "price": 348.00, "in_stock": true },
    { "timestamp": "2024-01-14", "price": 348.00, "in_stock": true },
    { "timestamp": "2024-01-13", "price": 329.99, "in_stock": true },
    ...
  ],
  "statistics": {
    "min": 278.00, "max": 399.99, "avg": 332.50, "median": 339.00
  }
}
```

#### 提醒管理 (Alert Management)

```
POST /api/v1/alerts
Body: {
  "product_id": "prod_abc123",
  "condition": "price_below",
  "threshold": 299.99,
  "channels": ["email", "push"]
}
Response: 201 Created
{ "alert_id": "alert_xyz789", "status": "active" }

GET /api/v1/users/{user_id}/alerts
Response: 200 OK
{
  "alerts": [
    {
      "alert_id": "alert_xyz789",
      "product_id": "prod_abc123",
      "product_title": "Sony WH-1000XM5",
      "condition": "price_below",
      "threshold": 299.99,
      "current_price": 348.00,
      "status": "watching",
      "last_triggered": null
    }
  ]
}
```

### 核心数据模型 (Core Data Models)

#### Products 表

```sql
CREATE TABLE products (
    product_id     UUID PRIMARY KEY,
    platform       VARCHAR(32) NOT NULL,     -- amazon, walmart, bestbuy
    platform_id    VARCHAR(128) NOT NULL,    -- ASIN, item_id, SKU
    url            TEXT NOT NULL,
    title          VARCHAR(512),
    category       VARCHAR(128),
    image_url      TEXT,
    current_price  DECIMAL(10,2),
    currency       VARCHAR(3) DEFAULT 'USD',
    in_stock       BOOLEAN DEFAULT TRUE,
    upc            VARCHAR(32),              -- cross-platform dedup
    metadata       JSONB,                    -- platform-specific fields
    scrape_priority INT DEFAULT 50,          -- 0=highest, 100=lowest
    last_scraped_at TIMESTAMPTZ,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform, platform_id)
);
```

#### Price History 表 (TimescaleDB Hypertable)

```sql
CREATE TABLE price_history (
    product_id   UUID NOT NULL REFERENCES products(product_id),
    recorded_at  TIMESTAMPTZ NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    in_stock     BOOLEAN DEFAULT TRUE,
    seller_type  VARCHAR(32),              -- buy_box, 3rd_party, used
    source       VARCHAR(32) DEFAULT 'scrape'  -- scrape, api, user_report
);
-- TimescaleDB hypertable, partitioned by time (7-day chunks)
SELECT create_hypertable('price_history', 'recorded_at',
       chunk_time_interval => INTERVAL '7 days');
CREATE INDEX idx_ph_product_time ON price_history (product_id, recorded_at DESC);
```

#### Alerts 表

```sql
CREATE TABLE alerts (
    alert_id     UUID PRIMARY KEY,
    user_id      UUID NOT NULL REFERENCES users(user_id),
    product_id   UUID NOT NULL REFERENCES products(product_id),
    condition    VARCHAR(32) NOT NULL,       -- price_below, pct_drop, all_time_low
    threshold    DECIMAL(10,2),
    channels     VARCHAR(64)[] DEFAULT '{email}',
    status       VARCHAR(16) DEFAULT 'active',  -- active, paused, triggered, expired
    cooldown_until TIMESTAMPTZ,             -- anti-spam: no repeat within cooldown
    last_triggered TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_alerts_product ON alerts (product_id, status)
    WHERE status = 'active';
```

### 写入路径: 价格抓取 -> 提醒触发 (Write Path)

1. **Scraping Orchestrator** 从 Redis 优先队列中取出到期的抓取任务
2. 任务发送到 **SQS/Kafka** 分发给 **Scraper Worker**
3. Worker 访问目标页面 (通过 **Proxy Pool**)，解析价格数据
4. Worker 对价格做**合理性验证** (与历史均价偏差 < 80%)
5. 验证通过后，写入 **TimescaleDB** (price_history 表)
6. 同时更新 **Products 表**的 current_price 和 last_scraped_at
7. 发布 **price-update 事件**到 Kafka topic
8. **Alert Service** 消费事件，查询该 product_id 的所有 active alerts
9. 对每条 alert 评估条件 (current_price < threshold?)
10. 满足条件且不在冷却期的 alert -> 发送通知任务到 **Notification Queue**
11. **Notification Worker** 通过 Email (SES) / Push (FCM/APNs) / SMS (Twilio)
    发送通知，更新 alert.last_triggered

### 读取路径: 价格历史查询 (Read Path)

1. 用户请求 `GET /products/{id}/prices?range=90d`
2. **API Gateway** 路由到 **Price History Service**
3. 先查询 **Redis Cache** (缓存热门商品的最近 7 天价格)
4. Cache miss -> 查询 **TimescaleDB**，利用 hypertable 分区裁剪
   只扫描相关时间范围的 chunk
5. 对于长时间范围 (>90 天)，使用 **Continuous Aggregate** (预计算的
   日级聚合视图)，避免扫描原始数据
6. 计算统计指标 (min, max, avg, percentile) 并返回
7. 热门商品结果缓存到 Redis (TTL = 下次抓取间隔)
"""

# ---------------------------------------------------------------------------
# S4: Formulas / Capacity Estimation
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

#### 用户与商品规模 (User & Product Scale)

| 指标 | 数值 |
|------|------|
| 总注册用户 | 1000 万 |
| DAU (Daily Active Users) | 100 万 |
| 追踪商品总数 | 5000 万 |
| 每用户平均追踪商品 | 20 |
| 活跃提醒规则 | 2 亿条 (5000 万商品 x 平均 4 条/商品) |

#### 抓取 QPS (Scraping QPS)

每个商品平均每 4 小时抓取一次:

$$
\text{Daily Scrapes} = 50M \times \frac{24}{4} = 300M \text{ scrapes/day}
$$

$$
\text{Average QPS} = \frac{300M}{86400} \approx 3{,}472 \text{ QPS}
$$

$$
\text{Peak QPS} = 3{,}472 \times 3 \approx 10{,}400 \text{ QPS}
$$

需要约 **10,000 个代理 IP** (每个 IP 平均 1 req/s) 或利用平台 API
减少 HTML 抓取量。

#### 存储估算 (Storage Estimation)

**价格时间序列数据**:

每条记录约 50 bytes (product_id 16B + timestamp 8B + price 8B + flags 2B
+ overhead 16B):

$$
\text{Daily New Records} = 300M \text{ records}
$$

$$
\text{Daily Storage} = 300M \times 50B = 15 \text{ GB/day}
$$

$$
\text{Annual Raw Storage} = 15 \text{ GB} \times 365 = 5.5 \text{ TB/year}
$$

降采样后 (90 天原始 + 日级聚合):

$$
\text{Raw (90d)} = 15 \text{ GB} \times 90 = 1.35 \text{ TB}
$$

$$
\text{Aggregated (remaining)} = 50M \times 50B \times 275 \text{ days} = 688 \text{ GB}
$$

$$
\text{Total Active Storage} \approx 2 \text{ TB}
$$

**商品元数据**:

$$
\text{Product Metadata} = 50M \times 2 \text{ KB} = 100 \text{ GB}
$$

#### 带宽估算 (Bandwidth)

抓取入站带宽 (HTML 页面平均 200 KB, 但只需价格片段约 5 KB):

$$
\text{Inbound} = 10{,}400 \times 5 \text{ KB} = 52 \text{ MB/s (peak)}
$$

用户查询出站带宽 (平均响应 2 KB):

$$
\text{User QPS} = \frac{1M \times 10 \text{ requests}}{86400} \approx 116 \text{ QPS}
$$

$$
\text{Outbound} = 116 \times 2 \text{ KB} = 232 \text{ KB/s}
$$

用户侧流量很低，瓶颈在抓取侧。

#### 缓存估算 (Cache Sizing)

缓存热门商品价格历史 (top 20% = 1000 万商品, 每个缓存 7 天 x 6 点/天
x 50B = 2.1 KB):

$$
\text{Cache Size} = 10M \times 2.1 \text{ KB} = 21 \text{ GB}
$$

一台 Redis 实例 (64 GB) 即可承载。

### 核心算法 (Core Algorithms)

#### 1. 抓取优先级算法 (Scraping Priority)

使用加权评分决定抓取频率:

$$
\text{Priority}(p) = w_1 \cdot \text{WatcherCount}(p) + w_2 \cdot \text{PriceVolatility}(p) + w_3 \cdot \text{Recency}(p)
$$

其中:
- $\text{WatcherCount}$: 关注该商品的用户数 (归一化到 0-1)
- $\text{PriceVolatility}$: 过去 30 天价格标准差/均价 (越不稳定越需要频繁抓取)
- $\text{Recency}$: 距上次抓取的时间 (越久优先级越高)
- 权重: $w_1 = 0.5, w_2 = 0.3, w_3 = 0.2$

#### 2. 价格异常检测 (Price Anomaly Detection)

使用 **Z-Score** 检测可疑价格变化:

$$
Z = \frac{P_{\text{new}} - \mu_{30d}}{\sigma_{30d}}
$$

- $\lvert Z \rvert > 3$: 标记为可疑，触发二次抓取验证
- $\lvert Z \rvert > 5$: 高度可疑，可能是页面解析错误或数据异常

#### 3. 降采样算法 (Downsampling)

90 天后的原始数据按天聚合:

```python
# TimescaleDB Continuous Aggregate
CREATE MATERIALIZED VIEW price_daily
WITH (timescaledb.continuous) AS
SELECT
    product_id,
    time_bucket('1 day', recorded_at) AS day,
    MIN(price) AS low,
    MAX(price) AS high,
    AVG(price) AS avg,
    LAST(price, recorded_at) AS close,
    FIRST(price, recorded_at) AS open
FROM price_history
GROUP BY product_id, time_bucket('1 day', recorded_at);
```

#### 4. 通知冷却算法 (Notification Cooldown)

防止用户在价格波动期间收到大量重复通知:

$$
\text{ShouldNotify} = (P_{\text{current}} < T_{\text{threshold}}) \wedge (t_{\text{now}} - t_{\text{last\_notify}} > \Delta t_{\text{cooldown}})
$$

默认冷却期 $\Delta t_{\text{cooldown}} = 24$ 小时。如果价格继续下降
(新价格 < 上次通知价格的 95%)，则忽略冷却期立即通知。

### 容量总结 (Capacity Summary)

| 资源 | 规格 |
|------|------|
| 抓取 QPS (峰值) | ~10,400 |
| 代理池 | ~10,000 IP |
| TSDB 存储 (活跃) | ~2 TB |
| 商品元数据 | ~100 GB |
| Redis 缓存 | ~21 GB (1 实例) |
| 通知吞吐 | ~5M notifications/day |
| 抓取带宽 (峰值) | ~52 MB/s |
| 用户 API QPS | ~116 QPS |
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints -- Scale & Reliability)

### 规模参数 (Scale Parameters)

| 维度 | 数值 |
|------|------|
| 追踪商品数 | 5000 万 |
| 每日抓取次数 | 3 亿 |
| 活跃提醒规则 | 2 亿 |
| 每日通知量 | ~500 万 |
| TimescaleDB 日写入 | 3 亿行 / 15 GB |
| 代理池大小 | 10,000+ IP |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 缓解措施 |
|------|---------|---------|
| Scraping Orchestrator | 所有抓取停止 | 多实例 Active-Passive + Leader Election (etcd/ZooKeeper) |
| TimescaleDB | 价格历史不可查 | Primary + Synchronous Replica; WAL streaming |
| PostgreSQL (Product DB) | 商品和提醒不可用 | Multi-AZ RDS; Read Replicas |
| Kafka | 价格事件丢失 | 3-broker cluster, replication factor=3, min.insync.replicas=2 |
| Redis (Cache) | 缓存穿透, 查询延迟上升 | Redis Sentinel 或 Cluster; 应用层 fallback 到 DB |
| Proxy Pool | 抓取失败率飙升 | 多供应商 (Luminati, Oxylabs, SmartProxy); 健康检查 + 自动切换 |
| Notification Service | 通知延迟或丢失 | SQS + DLQ; 重试机制; 多通道冗余 (email + push) |

### 多数据中心策略 (Multi-Datacenter Strategy)

对于 Price Tracker，**抓取层**和**用户服务层**有不同的部署策略：

**抓取层 (Active-Active, 按地域分片)**:
- US-East: 负责 Amazon.com, Walmart.com, BestBuy.com
- EU-West: 负责 Amazon.co.uk, Amazon.de
- AP-Southeast: 负责 Amazon.co.jp, Lazada
- 每个区域独立的 Scraper 集群 + Proxy Pool
- 抓取结果通过 **Kafka Cross-Cluster Replication** (MirrorMaker 2)
  汇聚到中心 TSDB

**用户服务层 (Active-Passive)**:
- Primary: US-East (承载所有写入)
- Secondary: EU-West (Read Replica, 灾备切换)
- **GeoDNS** 将用户路由到最近的读节点
- 写操作始终路由到 Primary (跨区域延迟 ~100ms，可接受)

### 高并发处理 (High Concurrency Handling)

#### 抓取侧并发

- **背压控制 (Backpressure)**: 当目标平台响应变慢 (延迟 > 5s)，
  自动降低该平台的并发抓取数
- **Circuit Breaker (断路器)**: 连续 10 次抓取失败后，暂停该平台 30 分钟
  - Half-Open: 30 分钟后尝试 1 次，成功则恢复
- **Bulkhead (舱壁模式)**: 每个平台独立的线程池，Amazon 故障不影响
  Walmart 抓取

#### 用户侧并发

- **Connection Pooling**: PgBouncer 管理 PostgreSQL 连接池
  (200 connections, transaction mode)
- **Rate Limiting**: 每用户 100 req/min (Token Bucket)
- **API 层缓存**: 热门商品价格缓存 (Redis, TTL = scrape interval)

### 抓取可靠性 (Scraping Reliability)

抓取是系统的核心，需要特别的可靠性保障:

- **多层重试 (Retry Strategy)**:
  - L1: 换代理 IP，重试 1 次 (间隔 5s)
  - L2: 换解析策略 (HTML -> Headless Browser)，重试 1 次
  - L3: 标记为失败，下个周期优先重试
- **解析器版本管理**: 每个平台的 HTML 解析器独立版本化;
  页面结构变化时可以快速发布新版本，不影响其他平台
- **Golden Test (黄金测试)**: 保存每个平台的样本页面 HTML，
  CI 中验证解析器正确性。页面结构变化时测试失败，触发告警

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 |
|------|---------|
| 抓取成功率 (per platform) | < 95% -> P2 告警; < 80% -> P1 告警 |
| 抓取延迟 (P99) | > 10s -> P2 |
| 价格更新延迟 (scrape-to-DB) | > 5 min -> P1 |
| 通知发送延迟 (trigger-to-send) | > 30 min -> P1 |
| TimescaleDB 写入延迟 | > 100ms P99 -> P2 |
| Kafka consumer lag | > 100K messages -> P1 |
| 代理池可用率 | < 70% healthy IPs -> P1 |
| 异常价格比率 | > 5% flagged -> P2 (可能是页面结构变化) |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|----------------|
| 抓取方式 | **平台 API** (Amazon PA-API): 稳定、合规, 但有 QPS 限制和数据延迟 | **HTML 解析**: 灵活、实时, 但脆弱且面临反爬虫风险 | **混合策略**: API 为主 + HTML 为辅。API 覆盖 ~60% 流量 (Amazon), HTML 覆盖无 API 的平台。降低反爬虫风险的同时保持覆盖广度 |
| 价格存储 | **关系型 DB** (PostgreSQL): 成熟、ACID, 但时间序列查询性能差 | **时间序列 DB** (TimescaleDB/InfluxDB): 写入优化、自动分区, 但生态较小 | **TimescaleDB** (PostgreSQL 扩展): 兼具 PostgreSQL 生态和时间序列性能。降采样、连续聚合内置, 无需单独运维 TSDB。比 InfluxDB 更适合关系型查询 |
| 通知延迟 | **实时** (每次抓取后立即评估): 延迟 < 1 min, 但计算成本高 | **批量** (每小时批量评估所有 alerts): 计算效率高, 但延迟最高 1 小时 | **事件驱动实时评估**: 价格更新事件触发该商品的 alert 评估, 只处理有变化的商品 (约 10% 每次抓取有价格变化)。延迟 < 5 min, 计算量可控 |
| 商品去重 | **严格匹配** (仅 UPC/EAN): 精确但覆盖低 (很多商品无 UPC) | **模糊匹配** (名称 + 属性): 覆盖高但有误匹配风险 | **分层匹配**: UPC 完全匹配 > 名称高置信度匹配 (Jaccard > 0.9) > 低置信度候选 (人工审核队列)。自动化处理 ~85% 的匹配, 剩余 15% 人工处理保证质量 |
| 代理策略 | **自建代理池**: 成本低, 但运维重, IP 质量难保证 | **商业代理服务** (Luminati): 质量高, 但成本 500-5000 USD/月 | **商业代理 + 弹性扩展**: 日常使用商业代理 (稳定), 大促期间 (Black Friday) 临时扩展。成本 ~2000 USD/月, 但抓取成功率 > 98% |

### 一致性 vs 可用性 (CAP Theorem Application)

价格追踪系统对**可用性**的要求高于**强一致性**:

- **价格数据**: 最终一致 -- 不同用户看到的价格可能有几分钟的差异，
  这在"每 1-6 小时抓取一次"的模型下完全可接受
- **提醒配置**: 强一致 -- 用户修改提醒规则后必须立即生效。
  使用 PostgreSQL Primary 处理所有写操作
- **通知 at-least-once**: 宁可重复通知也不能漏通知。
  使用 SQS + DLQ 保证消息不丢失

### 成本 vs 性能 (Cost vs Performance)

| 维度 | 低成本方案 | 高性能方案 | 我们的平衡 |
|------|----------|----------|----------|
| 抓取频率 | 每 24 小时 | 每 1 小时 | 动态: 热门商品 1h, 冷门商品 6h |
| 存储 | 只保留聚合数据 | 保留全部原始数据 | 90 天原始 + 之后日级聚合 |
| 代理 | 免费代理 (不稳定) | 商业代理 (2000 USD/月) | 商业代理 + 弹性扩展 |
| 通知 | 仅 Email (免费) | Email + Push + SMS | Email 免费 + Push 低成本; SMS 仅付费用户 |

### 10x / 100x 规模变化 (What Changes at Scale)

**10x (5 亿商品)**:
- TimescaleDB 需要 **多节点 (Multi-Node)** 集群, 按 platform 分片
- 代理池扩展到 100K+ IP, 需要自建代理基础设施 + 商业代理混合
- Scraping Orchestrator 从单一调度器改为 **分布式调度**
  (Airflow / Temporal)
- 价格历史查询引入 **Materialized View** 缓存层

**100x (50 亿商品)**:
- 抓取 QPS 达到 ~1M, 需要 **全球分布式抓取网络**
- 存储迁移到 **对象存储 (S3 Parquet)** + 查询引擎 (Presto/Trino)
  替代 TimescaleDB
- 商品去重使用 **ML Embedding** 模型 (Sentence-BERT) 替代规则匹配
- 通知系统需要 **多区域推送** + 本地化 (时区感知的通知时间)
- 引入 **数据湖** 架构: 实时层 (Kafka + Flink) + 批处理层 (Spark)
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果目标电商网站突然改版，所有抓取都失败了怎么办?

**承认局限**: 网页结构变化是 scraping 系统的最大风险, 无法完全预防。

**缓解措施**:

1. **Golden Test 自动检测**: CI 中保存每个平台的样本 HTML, 解析器每次部署前
   必须通过 golden test。页面结构变化导致测试失败时, 立即触发 P1 告警
2. **多策略降级**: HTML 解析失败后自动尝试 API (如果可用);
   API 也不可用时切换到 **Headless Browser** 模式
3. **解析器热更新**: 解析器代码与主服务解耦, 可以独立部署。
   新版解析器灰度发布 (5% 流量验证后逐步放量)
4. **历史数据回填**: 新解析器上线后, 对失败期间的商品补充抓取。
   价格历史中标记"数据缺失"的时间段

**数据支撑**: CamelCamelCamel 平均每年遇到 2-3 次 Amazon 页面大改版,
通常 24-48 小时内修复解析器。

### Q2: 如果 Black Friday 期间流量暴增 10 倍怎么办?

**承认挑战**: 大促期间价格变化频繁 + 用户活跃度暴增, 双重压力。

**应对策略**:

1. **提前预案 (Pre-scaling)**:
   - 大促前 3 天预扩展 Scraper Worker 到 3x 正常容量
   - 代理池从 10K 扩展到 30K IP (提前采购)
   - 临时增加所有商品的抓取频率到 1 小时
2. **优先级分流 (Priority Triage)**:
   - P0: 有 active alert 且接近目标价的商品 (最高优先级抓取)
   - P1: 高关注商品 (>100 watchers)
   - P2: 其他商品 (可以降低抓取频率到 12 小时)
3. **通知批量发送优化**:
   - 相似商品合并通知 ("你追踪的 5 款耳机都降价了")
   - 通知队列独立扩展 (SQS 自动扩展)
4. **降级策略**: 极端情况下关闭新用户注册和商品添加,
   集中资源服务现有用户

### Q3: 两个用户同时设置了不同的目标价, 价格同时满足两者, 如何保证两个通知都发出?

**核心保障**: 通知系统使用 **at-least-once delivery**:

1. **Alert 评估是无状态的**: 每次价格更新, 独立评估该商品的每条 alert 规则。
   不同用户的 alert 之间无竞争
2. **Notification Queue 幂等性**: 每条通知有唯一 ID
   (alert_id + product_id + price + timestamp)。Worker 发送前检查去重表,
   保证 exactly-once semantics
3. **DLQ (Dead Letter Queue)**: 发送失败的通知进入 DLQ,
   自动重试 3 次。超过 3 次的进入人工审查队列
4. **多通道冗余**: Email + Push 同时发送。如果 Email 服务 (SES) 故障,
   Push (FCM) 仍然可以送达

**结论**: 不同用户的 alert 是完全独立的, 没有竞争条件。
关键是保证消息队列的可靠性和 Worker 的幂等性。

### Q4: 如何防止商家"先涨后降"的虚假促销?

**检测策略**:

1. **价格基线算法 (Price Baseline)**:
   - 计算过去 90 天的**加权移动平均价 (Weighted Moving Average)**:

$$
\text{Baseline}_{90d} = \frac{\sum_{i=1}^{90} w_i \cdot P_i}{\sum_{i=1}^{90} w_i}
$$

   其中 $w_i$ 随时间衰减 (近期权重更高)

2. **涨价检测**: 如果促销前 14 天内价格上涨 > 20%, 标记为"可疑涨价"
3. **历史最低价对比**: 显示"当前价格 vs 历史真实最低价", 而不是"当前价格
   vs 涨价后的原价"
4. **用户 UI 提示**: 在价格图表上标记可疑涨价时段, 用户可以自行判断

**数据支撑**: 研究表明约 15-20% 的"折扣"存在先涨后降行为 (尤其在 Black
Friday 期间)。CamelCamelCamel 的价格历史图表就是用户识别虚假促销的主要工具。

### Q5: 如果 TimescaleDB 写入延迟突然飙升怎么办?

**诊断步骤**:

1. 检查是否触发了 **chunk compression** (TimescaleDB 自动压缩旧 chunk
   时会消耗 I/O)
2. 检查 **WAL 堆积** -- Replica 延迟可能导致 WAL 无法回收
3. 检查是否有慢查询锁表 (长时间运行的 `SELECT` 阻塞 `INSERT`)

**缓解措施**:

1. **写入缓冲**: 在 Kafka 和 TSDB 之间加一层 **Batch Writer**,
   批量写入 (每 1000 条或每 5 秒)，降低 WAL 压力
2. **Chunk 压缩调度**: 将自动压缩迁移到低峰时段 (UTC 6:00-10:00)
3. **写入分片**: 按 platform 分片, 不同平台写入不同 hypertable
4. **降级方案**: 极端情况下, 新抓取数据暂存到 Kafka, TSDB 恢复后补写
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试口述大纲 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

"Price Drop Tracker 的核心是**三个子系统的协调**: 大规模网页抓取、
时间序列价格存储、事件驱动的提醒通知。让我先确认一些关键需求..."

- 确认支持的电商平台范围 (Amazon 为主? 还是 10+ 平台?)
- 确认抓取频率要求 (小时级够用? 还是需要分钟级?)
- 确认规模: 追踪商品数量级 (千万级? 亿级?)
- 确认通知渠道 (Email only? 还是需要 Push/SMS?)
- 明确不做: 价格预测、实时价格监控、浏览器扩展

**FR**: (1) 商品追踪, (2) 价格历史, (3) 降价提醒, (4) 价格趋势分析, (5) 搜索

**NFR**: 99.9% 可用性, 通知延迟 < 30min, 最终一致性, 5000 万商品

### 5-15 分钟: 高层架构 (High-Level Architecture)

"系统分为三层: 数据采集层、数据处理与存储层、用户服务层。
最有挑战性的是**数据采集层** -- 需要在反爬虫对抗和平台合规之间找到平衡。"

画出核心组件:
- **Scraping Orchestrator**: 任务调度 + 优先级队列 + 平台限流
- **Scraper Workers**: 无状态抓取节点, 多策略解析 (API/HTML/Headless)
- **Proxy Pool**: 10K+ IP 轮换, 多供应商
- **TimescaleDB**: 价格时间序列 (PostgreSQL 扩展, 内置降采样)
- **PostgreSQL**: 商品元数据 + 用户提醒规则
- **Kafka**: 价格更新事件流, 解耦抓取和通知
- **Alert Service**: 事件驱动的规则评估引擎
- **Notification Workers**: Email (SES) + Push (FCM) + SMS (Twilio)

DB 选择理由: "TimescaleDB 而不是 InfluxDB, 因为它是 PostgreSQL 扩展,
可以和商品元数据在同一个生态内查询; 降采样和连续聚合是内置功能。"

### 15-40 分钟: 深入设计 (Deep Dive, 选 2-3 个)

**Deep Dive 1: 抓取系统 (Scraping Pipeline)** (最独特的组件)

"这是系统最大的技术挑战。需要解决三个问题:
反爬虫对抗、页面解析稳定性、抓取优先级。"

- 反爬虫: UA 轮换 + 请求间隔抖动 + Cookie 管理 + Fingerprint 多样化
- 平台限流: 每个平台独立 Token Bucket, Circuit Breaker
- 优先级调度: 加权评分 (watcher count x 0.5 + volatility x 0.3 + recency x 0.2)
- 异常检测: Z-Score 检测可疑价格变化, 自动触发二次验证
- 解析器版本管理: 每个平台独立, Golden Test CI 验证

**Deep Dive 2: 价格存储与查询 (Price History)**

"时间序列数据的核心挑战是 write-heavy workload + 长时间范围查询。"

- TimescaleDB hypertable: 按 7 天分区, 自动 chunk 管理
- 降采样: 90 天原始 -> 日级聚合, 存储从 5.5 TB/年降至 ~2 TB
- Continuous Aggregate: 预计算日级 OHLC (Open/High/Low/Close)
- 查询优化: 分区裁剪 + 聚合视图, P99 < 50ms

**Deep Dive 3: 提醒与通知 (Alert & Notification)**

"事件驱动架构, 只处理有价格变化的商品 (~10% per scrape cycle)。"

- Kafka consumer: Alert Service 订阅 price-update topic
- 批量规则评估: 该 product_id 的所有 active alerts
- 冷却机制: 24h 冷却期, 但价格继续下降 (< 95% of last notified price) 可突破
- at-least-once: SQS + DLQ + 幂等去重

### 40-50 分钟: 权衡与扩展讨论 (Trade-offs & Scaling)

"几个关键权衡..."

1. **API vs HTML 抓取**: 混合策略 -- API 为主 (~60% 覆盖), HTML 为辅
2. **抓取频率 vs 成本**: 动态频率 (1h-6h), 基于 watcher count 和 volatility
3. **通知实时性 vs 计算成本**: 事件驱动, 只处理有变化的 ~10%
4. **CAP 选择**: 价格数据 AP (最终一致), 提醒配置 CP (强一致)

10x 规模: TimescaleDB 多节点, 分布式调度 (Temporal), 代理池 100K+
100x 规模: S3 Parquet + Trino, ML embedding 去重, 全球分布式抓取网络

### 50-55 分钟: 总结与改进 (Wrap-up)

"如果有更多时间, 我会改进..."

1. **价格预测**: 基于历史数据用 LSTM/Prophet 预测价格走势, "建议等待,
   预计下周降价" 功能
2. **智能提醒**: "这个商品即将到达历史最低价" 的主动通知
3. **社交功能**: 公开的 wishlist, 用户可以分享降价发现
4. **A/B 测试框架**: 不同抓取策略和通知方式的效果对比

### 3 分钟电梯演讲版 (Elevator Pitch)

"Price Drop Tracker 是一个**抓取驱动的事件系统**: Scraping Orchestrator
调度 10K+ 代理 IP 从多个电商平台抓取 5000 万商品的价格; 价格数据存入
TimescaleDB (自动降采样, 90 天原始 + 日级聚合); 每次价格更新发布到
Kafka, Alert Service 实时评估 2 亿条提醒规则, 触发 Email/Push 通知。
关键设计: 动态抓取频率 (1h-6h) 平衡成本和时效; 反爬虫对抗 (UA 轮换 +
指纹多样化 + Circuit Breaker); Z-Score 价格异常检测防止脏数据;
通知冷却机制防止用户打扰。"

### 容量速记卡 (Quick Reference)

| 指标 | 数值 |
|------|------|
| 追踪商品 | 5000 万 |
| 每日抓取 | 3 亿次 |
| 抓取峰值 QPS | ~10,400 |
| TSDB 日写入 | 15 GB |
| 活跃存储 | ~2 TB |
| 代理池 | 10K IP |
| 活跃 Alerts | 2 亿 |
| 日通知量 | ~500 万 |
| 用户 API QPS | ~116 |
| 缓存 (Redis) | 21 GB |
| 代理成本 | ~2K USD/月 |

规模: 1000 万用户, 5000 万商品, 3 亿次/日抓取,
2 亿活跃 alerts, ~500 万通知/日。
"""


def populate_interview_price_tracker() -> None:
    """Create or update the interview-price-drop-tracker record with all 8 sections."""
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
    populate_interview_price_tracker()
