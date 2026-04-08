"""Populate interview-ad-click-aggregator system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design an Ad Click Aggregator --
real-time aggregation of ad click/impression events for billing, analytics, and fraud
detection using Kafka, Flink, exactly-once semantics, watermarks, and lambda architecture.
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

SLUG = "interview-ad-click-aggregator"
TITLE = "Design an Ad Click Aggregator"
DISPLAY_ORDER = 111

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**广告点击聚合系统 (Ad Click Aggregator)**，能够实时统计广告的
点击量和展示量，为广告主提供计费依据 (billing)、为运营团队提供实时分析面板
(analytics dashboard)、并支持点击欺诈检测 (click fraud detection)。

这是在线广告系统的核心基础设施之一。广告主按 **CPC (Cost Per Click，按点击付费)**
或 **CPM (Cost Per Mille，按千次展示付费)** 模型付费，系统必须保证：
(1) 每次合法点击都被准确计数 (不丢不重)，(2) 聚合结果在分钟级内可用，
(3) 欺诈点击被识别并排除在计费之外。

### 功能性需求 (Functional Requirements)

1. **事件摄入 (Event Ingestion)**: 接收来自广告 SDK / 网页像素的点击 (click)
   和展示 (impression) 事件，每个事件包含 ad_id, user_id, timestamp,
   device_info, ip, referrer 等字段
2. **实时聚合 (Real-time Aggregation)**: 按 ad_id + 时间窗口 (1 分钟 / 1 小时 /
   1 天) 聚合点击数和展示数，计算 **CTR (Click-Through Rate，点击率)**
3. **多维度切片 (Multi-dimensional Slicing)**: 支持按 ad_id, campaign_id,
   advertiser_id, country, device_type 等维度查询聚合数据
4. **计费结算 (Billing Settlement)**: 每小时 / 每天生成广告主的计费报表，
   精确到每个 ad_id 的有效点击数 x 单价
5. **欺诈检测 (Fraud Detection)**: 识别并标记异常点击模式
   (同一 IP 高频点击、机器人流量、点击农场)

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 广告计费是营收核心，停机直接影响收入
- **延迟 (Latency)**: 实时聚合端到端延迟 < 1 分钟；查询 API P99 < 200ms
- **吞吐量 (Throughput)**: 写入峰值 1M clicks/sec + 10M impressions/sec；
  读取 50K QPS (dashboard + API)
- **精确度 (Accuracy)**: 计费相关数据必须**精确** (不接受近似)；
  分析面板可接受秒级延迟的最终一致
- **持久性 (Durability)**: 原始事件保留 90 天 (审计需求)；
  聚合数据保留 2 年
- **一致性 (Consistency)**: 计费路径 **exactly-once** 语义；
  分析路径最终一致

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 点击事件和展示事件的比例大约是多少？**
   -- WHY: 影响存储和处理容量规划。典型 CTR 约 1-2%，
   意味着展示量是点击量的 50-100 倍，展示事件流量远大于点击

2. **Q: 计费模型是 CPC、CPM 还是两者都有？**
   -- WHY: CPC 只需精确计数点击；CPM 需要精确计数展示。
   两者都有意味着两条独立的聚合管道

3. **Q: 广告主需要多快看到点击数据？秒级还是分钟级？**
   -- WHY: 秒级需要流式推送 (WebSocket/SSE)；分钟级可以用轮询。
   这决定了聚合窗口大小和结果推送机制

4. **Q: 欺诈检测的误判容忍度是多少？宁可放过还是宁可误杀？**
   -- WHY: 误判 (false positive) 意味着合法点击被扣除，广告主投诉；
   漏判 (false negative) 意味着广告主为无效点击付费。
   两个方向的权衡决定检测阈值

5. **Q: 是否需要支持"回溯修正"？比如发现昨天的欺诈后重新计算计费？**
   -- WHY: 回溯修正需要可重放的事件流 + 可重算的聚合管道，
   架构必须支持 **reprocessing** (重处理)

6. **Q: 广告投放跨多少地理区域？是否需要多数据中心？**
   -- WHY: 多区域意味着事件产生地和聚合中心可能不同，
   需要考虑跨区域数据传输延迟和合规 (如 GDPR 数据本地化)

7. **Q: 聚合粒度最细需要到什么程度？**
   -- WHY: 只需 ad_id 级别聚合较简单；如果需要 ad_id + country + device
   的组合维度，状态空间会爆炸式增长

### 范围声明 (Out of Scope)

- 广告投放决策系统 (Ad Serving / Bidding) -- 只负责事件后的聚合
- 用户画像和定向 (User Targeting / Profiling)
- 广告创意管理 (Creative Management)
- 前端 SDK 的埋点实现
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

广告点击聚合系统采用 **Lambda Architecture (Lambda 架构)**，将数据处理分为
三条路径:

1. **实时路径 (Speed Layer)**: Kafka -> Flink -> 聚合结果写入 OLAP 存储，
   延迟 < 1 分钟
2. **批处理路径 (Batch Layer)**: Kafka -> S3/HDFS -> Spark/Hive，
   每小时生成精确聚合，用于计费结算
3. **服务层 (Serving Layer)**: OLAP 引擎 (如 **Druid / ClickHouse**)
   提供多维度查询

### 核心组件与职责

| 组件 | 职责 |
|------|------|
| **Event Gateway (事件网关)** | 接收来自 SDK/Pixel 的 HTTP 请求，校验签名，写入 Kafka。无状态，部署在 CDN 边缘节点 |
| **Kafka Cluster (消息队列)** | 持久化原始事件流。按 ad_id 分区，保证同一广告的事件有序。保留 7 天 |
| **Flink Streaming (流处理引擎)** | 消费 Kafka，执行窗口聚合 (1min/1h/1d)、去重、欺诈检测。维护精确计数状态 |
| **Fraud Detector (欺诈检测器)** | Flink 内的子管道，基于规则引擎 + ML 模型标记可疑点击 |
| **OLAP Store (分析存储)** | **ClickHouse / Apache Druid** 存储聚合结果，支持亚秒级多维查询 |
| **Billing Aggregator (计费聚合器)** | Spark 批处理每小时计算精确计费数据，写入 **PostgreSQL** (事务性存储) |
| **Raw Event Archive (原始事件归档)** | S3/HDFS 存储原始事件 (Parquet 格式)，90 天保留，支持审计和重处理 |
| **Query API (查询接口)** | 无状态 REST/GraphQL API，从 OLAP 读取分析数据，从 PostgreSQL 读取计费数据 |
| **Dashboard (实时面板)** | 前端可视化，WebSocket 推送实时聚合更新 |

### 数据库选型与理由

| 用途 | 选型 | 理由 |
|------|------|------|
| 事件流 | **Apache Kafka** | 高吞吐、持久化、可重放、天然分区 |
| 实时聚合 | **ClickHouse** | 列式存储、向量化执行、亚秒级聚合查询 |
| 计费数据 | **PostgreSQL** | ACID 事务、强一致、适合金融级别精确度 |
| 原始归档 | **S3 + Parquet** | 低成本、列式压缩、Spark 直接读取 |
| 缓存 | **Redis** | 热点查询缓存、实时 Top-N 广告排行 |

### 通信模式

- **SDK -> Event Gateway**: HTTPS POST (JSON/Protobuf)，批量上报 (每 5 秒)
- **Event Gateway -> Kafka**: 异步写入，acks=all (确保持久化)
- **Kafka -> Flink**: 消费者组 (Consumer Group)，at-least-once + 幂等去重
- **Flink -> ClickHouse**: 批量写入 (每 10 秒刷盘)
- **Flink -> Redis**: 实时 Top-N 更新 (pub/sub 推送到 Dashboard)
- **Spark -> PostgreSQL**: JDBC 批量写入，事务保护
"""

# ---------------------------------------------------------------------------
# S3: Data Flow (API Design + Data Flow)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点

#### 事件上报

```
POST /v1/events/click
Content-Type: application/json
Authorization: Bearer <sdk_token>

{
  "ad_id": "ad_12345",
  "impression_id": "imp_67890",
  "user_id": "u_abc",
  "timestamp": 1712567890123,
  "device": {"type": "mobile", "os": "iOS", "browser": "Safari"},
  "ip": "203.0.113.42",
  "referrer": "https://example.com/article",
  "signature": "hmac_sha256_..."
}

Response: 202 Accepted
{"status": "received", "event_id": "evt_xyz"}
```

#### 聚合查询

```
GET /v1/analytics/clicks?ad_id=ad_12345&granularity=1h&from=2026-04-08T00:00:00Z&to=2026-04-08T12:00:00Z
Authorization: Bearer <api_token>

Response: 200 OK
{
  "ad_id": "ad_12345",
  "granularity": "1h",
  "data": [
    {"timestamp": "2026-04-08T00:00:00Z", "clicks": 1523, "impressions": 98712, "ctr": 0.0154},
    {"timestamp": "2026-04-08T01:00:00Z", "clicks": 1201, "impressions": 87234, "ctr": 0.0138}
  ]
}
```

#### 计费报表

```
GET /v1/billing/report?advertiser_id=adv_001&period=2026-04-07
Authorization: Bearer <billing_token>

Response: 200 OK
{
  "advertiser_id": "adv_001",
  "period": "2026-04-07",
  "campaigns": [
    {
      "campaign_id": "camp_100",
      "ads": [
        {"ad_id": "ad_12345", "valid_clicks": 35210, "fraud_clicks": 412, "cost_usd": 1760.50},
        {"ad_id": "ad_12346", "valid_clicks": 22100, "fraud_clicks": 98, "cost_usd": 1105.00}
      ],
      "total_cost_usd": 2865.50
    }
  ],
  "total_cost_usd": 2865.50
}
```

### 核心数据模型

#### 原始事件 (Raw Event) -- Kafka / S3

| 字段 | 类型 | 说明 |
|------|------|------|
| event_id | STRING | 全局唯一 ID (UUID v7, 时间有序) |
| event_type | ENUM | click / impression |
| ad_id | STRING | 广告 ID |
| campaign_id | STRING | 广告系列 ID |
| advertiser_id | STRING | 广告主 ID |
| impression_id | STRING | 展示 ID (用于点击-展示关联) |
| user_id | STRING | 用户 ID (可能匿名) |
| timestamp | INT64 | 事件发生时间 (毫秒) |
| server_timestamp | INT64 | 服务器接收时间 |
| ip | STRING | 客户端 IP |
| device_type | STRING | mobile / desktop / tablet |
| country | STRING | GeoIP 解析的国家 |
| is_fraud | BOOLEAN | 欺诈标记 (流处理后回填) |

#### 聚合表 (Aggregated Clicks) -- ClickHouse

| 字段 | 类型 | 说明 |
|------|------|------|
| ad_id | STRING | 广告 ID |
| window_start | DATETIME | 窗口起始时间 |
| window_size | ENUM | 1min / 1h / 1d |
| clicks | INT64 | 有效点击数 |
| impressions | INT64 | 展示数 |
| fraud_clicks | INT64 | 欺诈点击数 |
| unique_users | INT64 | 去重用户数 (HyperLogLog 近似) |
| country | STRING | 国家 (维度列) |
| device_type | STRING | 设备类型 (维度列) |

### 写入路径 (Write Path)

```
1. 用户点击广告 -> 广告 SDK 发送 HTTPS POST 到 Event Gateway
2. Event Gateway 校验签名 + 限流 -> 生成 event_id -> 写入 Kafka (key=ad_id)
3. Kafka 持久化 (3 副本, acks=all)
4. Flink 消费 Kafka:
   a. 解析事件 -> 按 event_id 去重 (Bloom Filter, 1 小时窗口)
   b. Fraud Detector 评估 -> 标记 is_fraud
   c. 窗口聚合 (TumblingWindow 1min):
      - 有效点击 += 1 (if !is_fraud)
      - 展示 += 1
   d. 窗口触发 -> 写入 ClickHouse (批量 INSERT)
5. 同时: 原始事件异步归档到 S3 (Parquet, 按日期分区)
```

### 读取路径 (Read Path)

```
1. 用户请求 -> Query API -> 解析查询参数 (ad_id, 时间范围, 粒度)
2. 检查 Redis 缓存 -> 命中则直接返回
3. 缓存未命中 -> 查询 ClickHouse:
   SELECT ad_id, window_start, sum(clicks), sum(impressions)
   FROM ad_click_agg
   WHERE ad_id = ? AND window_start BETWEEN ? AND ?
   GROUP BY ad_id, window_start
   ORDER BY window_start
4. 结果写入 Redis 缓存 (TTL = 30 秒)
5. 返回 JSON 响应
```

### 计费路径 (Billing Path)

```
1. Spark 批处理每小时启动:
   a. 读取 S3 原始事件 (过去 1 小时)
   b. 精确去重 (基于 event_id, 非 Bloom Filter)
   c. 应用离线欺诈模型 (更复杂的 ML 模型, 可回溯)
   d. 精确聚合: ad_id -> valid_clicks, fraud_clicks
   e. 与广告主出价表 JOIN -> 计算费用
   f. 写入 PostgreSQL billing_records 表 (事务)
2. 每日凌晨: 生成日报表 -> 发送给广告主
```
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Estimation & Core Algorithms)

### 容量估算 (Capacity Estimation)

**假设**:
- DAU = 5 亿 (广告覆盖用户)
- 每用户每天平均看到 20 条广告 -> 展示量 = $5 \times 10^8 \times 20 = 10^{10}$ (100 亿/天)
- 平均 CTR = 1.5% -> 点击量 = $10^{10} \times 0.015 = 1.5 \times 10^8$ (1.5 亿/天)

**QPS 计算**:

$$\text{展示 QPS (avg)} = \frac{10^{10}}{86400} \approx 115\text{K/sec}$$

$$\text{展示 QPS (peak)} = 115\text{K} \times 3 \approx 350\text{K/sec}$$

$$\text{点击 QPS (avg)} = \frac{1.5 \times 10^8}{86400} \approx 1700\text{/sec}$$

$$\text{点击 QPS (peak)} = 1700 \times 5 \approx 8500\text{/sec}$$

**存储估算**:

每条原始事件约 500 bytes (JSON):

$$\text{日存储} = (10^{10} + 1.5 \times 10^8) \times 500\text{B} \approx 5\text{TB/天 (原始)}$$

$$\text{Parquet 压缩} \approx 5\text{TB} \times 0.15 = 750\text{GB/天}$$

$$\text{90 天归档} = 750\text{GB} \times 90 \approx 67\text{TB}$$

聚合数据 (ClickHouse):

$$\text{聚合行数 (1min)} = 100\text{万广告} \times 1440\text{min/天} = 14.4 \times 10^8\text{行/天}$$

$$\text{每行约 100 bytes} \to 14.4 \times 10^8 \times 100 = 144\text{GB/天}$$

**带宽估算**:

$$\text{入口带宽} = 350\text{K/sec} \times 500\text{B} = 175\text{MB/sec} \approx 1.4\text{Gbps}$$

**内存 (Flink 状态)**:

- 去重 Bloom Filter: 每小时 ~$10^{10}/24 \approx 4 \times 10^8$ 事件,
  误报率 0.01% -> 约 1.5 GB
- 窗口聚合状态: 100 万活跃广告 x 200 bytes = 200 MB
- 欺诈检测特征: 1 亿活跃 IP x 50 bytes = 5 GB
- **Flink 总内存 $\approx$ 7 GB (可控)**

**基础设施成本 (月)**:

| 组件 | 规格 | 月成本 |
|------|------|--------|
| Kafka | 30 brokers, 500 分区 | ~$15,000 |
| Flink | 20 TaskManagers, 各 16 GB | ~$8,000 |
| ClickHouse | 6 节点集群, 各 500 GB SSD | ~$12,000 |
| S3 归档 | 67 TB, Glacier IA | ~$1,500 |
| PostgreSQL | 2 节点 HA | ~$2,000 |
| Redis | 3 节点 Sentinel | ~$1,500 |
| Event Gateway | 50 台 (边缘部署) | ~$10,000 |
| **总计** | | **~$50,000/月** |

### 核心算法

#### Exactly-Once 语义实现

广告计费要求 **exactly-once (恰好一次)** 语义——既不丢失也不重复计数。
实现分三层:

1. **At-least-once 传输 + 幂等去重**:
   - Kafka producer 开启 `enable.idempotence=true` (基于 PID + sequence number)
   - Kafka consumer 使用 `read_committed` 隔离级别
   - Flink 使用 event_id 做幂等去重 (Bloom Filter + 精确 Set)

2. **Flink Checkpoint + 两阶段提交**:
   - Flink 开启 **Checkpoint** (间隔 30 秒)
   - Sink 使用 **TwoPhaseCommitSinkFunction**:
     a. 预提交 (pre-commit): 数据写入 ClickHouse 临时表
     b. Checkpoint 完成 -> 提交 (commit): 将临时表数据合并到主表
     c. 故障恢复 -> 回滚 (abort): 丢弃临时表
   - 保证: 即使 Flink 崩溃恢复，每条事件恰好被写入一次

3. **端到端 exactly-once 流程**:

```
Producer (idempotent) -> Kafka (transactional) -> Flink (checkpoint)
    -> ClickHouse (2PC sink)
```

#### 去重算法: Bloom Filter + Spillover Set

对于每小时 $4 \times 10^8$ 事件的去重:

$$\text{Bloom Filter 大小} = -\frac{n \ln p}{(\ln 2)^2}$$

其中 $n = 4 \times 10^8$, $p = 0.0001$ (0.01% 误报率):

$$\text{Size} = -\frac{4 \times 10^8 \times \ln 0.0001}{(\ln 2)^2} \approx 1.5\text{GB}$$

**两级去重策略**:
1. **第一级 (Bloom Filter)**: 快速判断"可能重复" vs "绝对不重复"
2. **第二级 (RocksDB 精确 Set)**: 仅对 Bloom Filter 报告"可能重复"的
   event_id 进行精确查找。命中率 ~0.01%，精确 Set 大小极小

#### 时间窗口与水位线 (Watermark)

移动端网络不稳定导致事件可能延迟到达。使用 **Watermark (水位线)** 处理:

$$\text{Watermark}(t) = \max(\text{event\_time}) - \text{allowed\_lateness}$$

**策略**: allowed_lateness = 5 分钟

- 窗口 [00:00, 00:01) 在事件时间 00:06 时关闭
- 在 00:01 - 00:06 之间到达的属于该窗口的事件仍被计入
- 00:06 之后到达的**迟到事件 (Late Event)** 被发送到 **Side Output** (侧输出):
  - 写入专用 Kafka topic `late_events`
  - 批处理管道会包含这些迟到事件 (最终一致)

#### 点击欺诈检测算法

**规则引擎 (Rule-based, 实时)**:

| 规则 | 条件 | 置信度 |
|------|------|--------|
| IP 高频点击 | 同一 IP 对同一 ad_id, 1 分钟内 > 10 次点击 | 高 |
| 用户高频点击 | 同一 user_id, 1 小时内 > 50 次不同广告点击 | 中 |
| 无展示点击 | click 事件找不到对应的 impression_id | 高 |
| 地理异常 | 用户 10 分钟内从两个不同大洲发出点击 | 中 |
| 设备指纹聚集 | 同一 device_fingerprint 关联 > 100 个 user_id | 高 |

**ML 模型 (离线增强)**:
- 特征: 点击间隔分布、鼠标移动模式、页面停留时间、IP 信誉分
- 模型: **Gradient Boosted Trees** (XGBoost)，每日离线训练
- 应用: 批处理管道中对实时规则标记的"中置信度"事件进行二次判定
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性 (Scale & Reliability)

### 具体规模数字

| 指标 | 数值 |
|------|------|
| DAU | 5 亿 |
| 日展示量 | 100 亿 |
| 日点击量 | 1.5 亿 |
| 峰值展示 QPS | 350K/sec |
| 峰值点击 QPS | 8.5K/sec |
| 活跃广告数 | ~100 万 |
| 原始日存储 (压缩后) | 750 GB |
| 聚合日存储 | 144 GB |
| Flink 状态内存 | ~7 GB |
| 端到端延迟 (实时路径) | < 1 分钟 |

### 单点故障分析 (SPOF Analysis)

| 组件 | 风险 | 缓解措施 |
|------|------|----------|
| **Event Gateway** | 入口宕机 | 多台无状态实例 + L7 负载均衡 + 多区域部署，健康检查自动摘除 |
| **Kafka** | Broker 宕机 | 3 副本 + ISR, min.insync.replicas=2, 跨机架部署 |
| **Flink** | JobManager 宕机 | HA 模式 (ZooKeeper 选主), Checkpoint 每 30 秒, 自动恢复 |
| **Flink TaskManager** | 单个 TM 崩溃 | Flink 自动重新分配 subtask, 从最近 checkpoint 恢复, 丢失 < 30 秒 |
| **ClickHouse** | 节点宕机 | ReplicatedMergeTree 引擎, 2 副本, ZooKeeper 协调 |
| **PostgreSQL** | 主库宕机 | 同步流复制 + 自动故障切换 (Patroni) |
| **Redis** | 主节点宕机 | Redis Sentinel 自动故障切换, 从节点秒级提升 |

### 多数据中心部署

**策略: 就近摄入 + 集中聚合**

```
Region A (US-East)              Region B (EU-West)
  |                                |
  | Event Gateway (边缘)          | Event Gateway (边缘)
  |                                |
  v                                v
Local Kafka A                   Local Kafka B
  |                                |
  +---> MirrorMaker 2.0 ---------+
  |                                |
  v                                v
         Central Kafka (US-East)
              |
              v
         Flink Cluster
              |
         +----+----+
         v         v
    ClickHouse  PostgreSQL
```

- **事件网关部署在边缘**: 用户点击就近上报到最近区域的 Gateway，
  降低上报延迟 (< 50ms)
- **MirrorMaker 2.0 跨区域复制**: EU 的 Kafka 事件异步复制到 US-East
  中心集群，延迟 ~100ms
- **集中聚合**: 所有事件在中心区域的 Flink 集群统一处理，
  避免跨区域聚合的复杂性
- **GDPR 合规**: EU 用户的 PII (user_id, ip) 在 EU 区域脱敏后再复制。
  原始 PII 保留在 EU-West 的本地存储

**为什么不用每区域独立聚合？**
广告计费需要全局精确去重——同一用户可能在 US 看到广告、在 EU 点击。
独立聚合会导致去重不完整，影响计费精确度。

### 高并发处理

**写入侧 (事件摄入)**:
- **SDK 端批量上报**: 移动 SDK 每 5 秒聚合一次事件批量发送，
  减少 HTTP 连接数
- **Event Gateway 限流**: 每 IP 100 req/sec, 每 SDK token 10K req/sec
- **Kafka 分区**: 500 分区, 按 ad_id 哈希。每分区 ~700 events/sec (均匀)
- **背压 (Backpressure)**: Flink 消费速率 < Kafka 生产速率时，
  Flink 自动向上游传递背压信号，Gateway 开始丢弃低优先级展示事件

**读取侧 (查询)**:
- **ClickHouse 预聚合表**: 使用 **AggregatingMergeTree** 引擎，
  查询时直接读取预计算结果，避免全表扫描
- **Redis 缓存**: 热门广告 (Top-1000) 的最近 1 小时聚合数据缓存在 Redis，
  命中率 ~80%
- **Rate Limiting**: 每 API token 100 QPS
- **Circuit Breaker**: ClickHouse 响应 > 2 秒时熔断，
  返回 Redis 缓存的旧数据 (stale but available)

### 优雅降级 (Graceful Degradation)

| 级别 | 触发条件 | 动作 |
|------|---------|------|
| Level 1 | Kafka lag > 5 分钟 | 增加 Flink 并行度 (auto-scaling) |
| Level 2 | Kafka lag > 15 分钟 | 关闭展示事件的实时聚合 (只处理点击) |
| Level 3 | Flink 持续背压 > 30 分钟 | 对展示事件进行 10% 采样聚合 |
| Level 4 | Flink 集群不可用 | 切换为批处理模式 (每 15 分钟 Spark job) |

### 监控与告警

**关键指标**:
- **端到端延迟**: 事件产生到聚合结果可查询的时间。目标 < 1 分钟，> 3 分钟告警
- **Kafka Consumer Lag**: 每分钟采样。> 5 分钟告警
- **Flink Checkpoint 耗时**: 正常 < 10 秒, > 30 秒告警
- **去重碰撞率**: Bloom Filter 的误报率。> 0.1% 告警 (可能需要扩容)
- **欺诈率**: 每小时的 fraud_clicks / total_clicks。突然变化 > 2x 告警
- **计费一致性**: 实时聚合 vs 批处理聚合的差异。> 1% 告警
- **ClickHouse 查询延迟**: P99 > 1 秒告警
"""

# ---------------------------------------------------------------------------
# S6: Trade-offs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| 架构模式 | **Kappa Architecture** (纯流式) | **Lambda Architecture** (流 + 批) | **Lambda**: 计费需要精确数据, 流式管道的 Bloom Filter 去重有 0.01% 误报, 批处理提供精确校准。Kappa 对分析足够但不满足计费精确度 |
| 聚合精度 | **近似聚合** (CMS/HLL, 内存小) | **精确聚合** (HashMap, 内存大) | **精确聚合**: 广告计费不能用近似值。100 万活跃广告的 HashMap 只需 200 MB, 在可控范围内。HLL 仅用于 unique_users 这类非计费指标 |
| OLAP 引擎 | **Apache Druid** (实时摄入优) | **ClickHouse** (查询性能优) | **ClickHouse**: 我们的查询模式以 ad_id + 时间范围聚合为主, ClickHouse 的向量化执行在这类查询上比 Druid 快 2-3x。Druid 的实时摄入优势被 Flink 预聚合抵消 |
| 去重策略 | **Bloom Filter** (内存小, 有误报) | **精确 Set** (内存大, 零误报) | **两级去重**: Bloom Filter 做第一级快速过滤, RocksDB Set 做第二级精确验证。兼顾性能和精确度 |
| 欺诈检测 | **纯规则引擎** (可解释, 延迟低) | **ML 模型** (精确度高, 延迟高) | **混合**: 实时路径用规则引擎 (< 10ms), 批处理路径用 ML 模型回溯判定。规则捕获明显欺诈, ML 捕获隐蔽模式 |

### CAP 定理应用

广告点击聚合系统选择 **CP (一致性 + 分区容忍)**:

- **一致性 (Consistency)**: 计费数据必须精确, 不能因为分区导致重复计费
  或漏计。Kafka 的 min.insync.replicas=2 + Flink exactly-once 保证强一致
- **分区容忍 (Partition Tolerance)**: 分布式系统必须容忍网络分区
- **可用性 (Availability)**: 在网络分区时, 宁可暂停聚合 (数据在 Kafka 缓冲)
  也不产生不一致的计费数据。Kafka 的 7 天保留提供缓冲

**注**: 分析路径 (dashboard) 选择 AP -- 返回过时数据优于不可用。
计费路径和分析路径的 CAP 选择不同。

### 成本 vs 性能权衡

| 方案 | 月成本 | 实时延迟 | 计费精确度 |
|------|--------|---------|-----------|
| 纯批处理 (每小时 Spark) | $20,000 | 1 小时 | 100% |
| 纯流式 (Flink, 近似去重) | $30,000 | < 1 分钟 | ~99.99% |
| **Lambda (流 + 批)** | **$50,000** | **< 1 分钟** | **100% (批校准)** |
| 纯流式 (Flink, 精确去重) | $80,000+ | < 1 分钟 | 100% |

我们选择 Lambda: 实时路径提供分钟级分析能力, 批处理路径保证计费 100% 精确。
成本比纯精确流式方案节省 40%。

### 复杂度 vs 简洁度

Lambda 架构的主要批评是**维护两套管道的复杂度**:
- 流式管道 (Flink) 和批处理管道 (Spark) 的聚合逻辑必须一致
- 测试负担翻倍: 两套代码都需要单元测试和集成测试

**缓解措施**:
- 使用 **Apache Beam** 统一编程模型: 一份代码同时编译为 Flink Runner
  和 Spark Runner, 减少逻辑不一致风险
- 每日自动化对账: 对比流式和批处理的聚合结果, 差异 > 0.1% 自动告警

### 10x / 100x 规模变化

**10x (50 亿 DAU, 1000 亿日展示)**:
- Kafka 分区从 500 扩展到 2000
- Flink 集群从 20 台扩展到 80 台
- ClickHouse 从 6 节点扩展到 24 节点 (4 个 shard x 2 副本 x 3 节点)
- 引入 **Kafka Tiered Storage**: 冷数据自动迁移到 S3, 减少 Kafka 存储成本
- Event Gateway 从 50 台扩展到 200 台, 部署到全球 10+ 边缘 POP

**100x (500 亿 DAU, 1 万亿日展示)**:
- 需要**分层聚合**: 边缘节点先做本地预聚合 (每 10 秒), 再发送到中心
- ClickHouse 替换为 **Apache Pinot** 或自建 OLAP (更好的多租户隔离)
- 计费从 PostgreSQL 迁移到分布式数据库 (**CockroachDB / TiDB**)
- 引入**采样 + 推断**: 对长尾广告 (日点击 < 100) 进行采样聚合,
  统计推断补偿。头部广告仍精确计数
- 月成本从 $50K 增长到 ~$2M (非线性, 因为分层聚合有压缩效果)
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个大广告主的所有广告同时上线, 导致某些 Kafka 分区热点怎么办？

**承认局限**: 按 ad_id 哈希分区时, 如果某个 advertiser_id 下有数万个
ad_id, 这些 ad_id 可能均匀分布在各分区。但如果是按 campaign_id
分区, 一个大 campaign 的所有事件会集中到一个分区。

**缓解措施**:
1. **分区策略**: 按 ad_id (而非 campaign_id) 分区, 因为 ad_id
   的基数更大 (~100 万), 更均匀
2. **热点检测 + 动态重分区**: 监控每个分区的流量。
   如果某分区 QPS > 平均值 5x, 触发动态拆分:
   对该分区的 ad_id 追加随机后缀 (如 ad_12345_0, ad_12345_1),
   分散到多个分区。聚合时合并同前缀的结果
3. **Kafka 分区数足够多**: 500 分区可以容纳大部分场景的均匀分布

**数据支撑**: 100 万 ad_id 分布到 500 分区, 平均每分区 2000 个 ad_id。
即使最热门的广告 (如 Super Bowl 广告) 也只占总流量的 ~1%,
不会造成严重倾斜。

### Q2: Bloom Filter 去重有 0.01% 误报, 这意味着广告主会被少收费？

**承认影响**: 0.01% 误报意味着每 1 万次合法点击中有 1 次被错误地
判定为"重复"而丢弃。对日点击 10 万的广告主, 每天少收约 10 次点击的费用。

**缓解措施**:
1. **两级去重**: Bloom Filter 误报的 event_id 会进入 RocksDB 精确 Set
   二次验证, 误报率降至接近零
2. **批处理校准**: 每小时的 Spark 精确去重会修正流式去重的误差。
   最终计费基于批处理结果, 非流式结果
3. **Bloom Filter 定期重建**: 每小时创建新的 Bloom Filter,
   旧的 filter 随窗口关闭销毁。防止误报率随时间累积

**关键点**: 实时路径的 Bloom Filter 去重用于**分析面板** (容许微小误差);
计费路径用**批处理精确去重** (零误差)。两条路径的精确度要求不同。

### Q3: 如果广告主质疑计费数据, 你如何提供审计证据？

**审计能力设计**:
1. **原始事件不可变归档**: 所有原始事件以 Parquet 格式归档到 S3,
   保留 90 天。每个事件有全局唯一的 event_id
2. **处理血缘 (Lineage)**: 每条聚合记录附带 metadata:
   - 源 Kafka topic + partition + offset 范围
   - 处理时间戳
   - 欺诈检测结果和依据
3. **可重放 (Replayable)**: 给定时间范围, 可以从 S3 原始数据
   重新运行聚合管道, 得到可比对的结果
4. **计费争议流程**: 广告主通过 API 提交争议 -> 系统自动从原始数据
   重算该时间段的聚合 -> 对比差异 -> 人工审核

### Q4: 如果 Flink 集群需要升级或迁移, 如何做到零停机？

**蓝绿部署 (Blue-Green Deployment)**:
1. 启动新 Flink 集群 (Green), 从 Kafka 最新 offset 开始消费
2. 新旧集群**并行运行** 10 分钟, 两者同时写入 ClickHouse (不同的临时表)
3. 对比两个集群的输出: 差异 < 0.01% 视为验证通过
4. 切换: Green 的输出写入正式表, Blue 优雅停止
5. Blue 的最终 checkpoint 保留 24 小时 (回滚保险)

**关键**: Kafka 允许多个消费者组同时消费同一 topic,
因此蓝绿两套 Flink 可以并行运行不冲突。

### Q5: 如果流量突然 10x (比如黑色星期五), 系统会如何表现？

**自动扩缩容策略**:
1. **Event Gateway**: 无状态, K8s HPA 基于 CPU 自动扩容,
   1 分钟内扩容完成
2. **Kafka**: 短期内分区数不变 (扩分区需要 rebalance),
   但 broker 数量可以扩展。7 天数据保留提供缓冲
3. **Flink**: 支持 Reactive Mode, 自动增加并行度。
   但 rescale 需要从 checkpoint 恢复, 约 1-2 分钟中断
4. **ClickHouse**: 短期依赖查询队列排队; 中期增加副本数分担读取

**降级方案** (如果扩容不够快):
- 展示事件 10% 采样 (点击事件仍然全量处理)
- 关闭非核心维度的实时聚合 (只保留 ad_id 级别)
- Dashboard 查询结果缓存 TTL 从 30 秒延长到 5 分钟

**准备措施**: 对于可预期的流量高峰 (黑色星期五、Super Bowl),
提前 24 小时手动扩容 2x, 并设置告警阈值为平时的 50% (提早预警)。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 3 分钟电梯演讲版 (Elevator Pitch)

"广告点击聚合的核心挑战是: 每天 100 亿展示 + 1.5 亿点击, 需要同时满足
分钟级实时分析和计费级精确度。我的方案采用 **Lambda Architecture**:

1) **实时路径**: Event Gateway -> Kafka (按 ad_id 分区) -> Flink 流处理
   (窗口聚合 + Bloom Filter 去重 + 规则引擎欺诈检测) -> ClickHouse (OLAP 查询)
2) **批处理路径**: S3 原始归档 -> Spark 每小时精确去重 + ML 欺诈检测
   -> PostgreSQL (计费结算)

关键设计:
- **Exactly-once**: Kafka 幂等 + Flink checkpoint + 两阶段提交
- **两级去重**: Bloom Filter (快, 0.01% 误报) + RocksDB 精确 Set (零误报)
- **欺诈检测**: 实时规则引擎 (高召回) + 离线 ML (高精度), 互补

规模: 5 亿 DAU, 350K 峰值 QPS, Flink 状态仅 7 GB, 月成本约 $50K。"

### 完整 1 小时面试节奏

#### 0-5 分钟: 需求澄清

**开场**: "广告点击聚合有两个核心需求维度:
精确度 (计费 vs 分析) 和延迟 (实时 vs 批量)。让我先确认几个关键问题。"

**必须澄清的问题**:
1. "计费模型是 CPC 还是 CPM？CPC 聚焦点击精确度, CPM 聚焦展示计数"
2. "广告主需要多快看到数据？分钟级实时面板 + 小时级精确计费是否足够？"
3. "欺诈检测是内置还是独立系统？我倾向内置, 因为欺诈标记直接影响计费"
4. "展示量和点击量的数量级？我按 100 亿/天展示、1.5 亿/天点击估算"

**画出需求框架**:
```
FR: 事件摄入, 实时聚合, 多维查询, 计费结算, 欺诈检测
NFR: 350K peak QPS, <1min 实时延迟, exactly-once 计费, 99.99% 可用
```

#### 5-15 分钟: 高层架构

**画 Lambda Architecture 图**: "我的设计分两条路径——实时分析和精确计费"

**逐层解释**:
- **事件网关**: "为什么需要 Gateway 层？限流、签名验证、GeoIP 解析
  都在这里完成, 不让脏数据进入 Kafka"
- **Kafka**: "为什么按 ad_id 分区？保证同一广告的事件有序,
  Flink 去重和聚合才正确"
- **双路径**: "为什么不用纯流式？因为 Bloom Filter 去重有 0.01% 误报,
  计费不能容忍。批处理每小时精确校准"

**数据库选型**: "分析用 ClickHouse (列式, 快), 计费用 PostgreSQL (事务, 准),
归档用 S3 + Parquet (便宜, 可重放)"

#### 15-40 分钟: 深入讨论 (选 2-3 个最有趣的组件)

**深入点 1: Exactly-Once 语义** (~8 分钟)
- 解释三层保证: Kafka 幂等 -> Flink checkpoint -> 两阶段提交
- 画出故障恢复流程: Flink 崩溃 -> 从 checkpoint 恢复 -> 重放 Kafka
- "关键洞察: exactly-once 不是说每条消息只处理一次,
  而是说处理效果等价于只处理一次。Flink 可能重复处理, 但输出去重"
- 讨论 Flink 的 barrier alignment 机制

**深入点 2: 欺诈检测** (~8 分钟)
- 解释实时规则引擎: IP 频率、无展示点击、地理异常
- 画出规则评估流程 (Flink CEP / 复杂事件处理)
- "为什么需要离线 ML？规则引擎只能捕获已知模式,
  ML 可以发现新型欺诈 (如分布式点击农场)"
- 讨论误判 (false positive) 对广告主信任的影响

**深入点 3: 多维度聚合与 ClickHouse** (~8 分钟)
- 解释 ClickHouse 的 AggregatingMergeTree
- Flink 预聚合 (1min) + ClickHouse 二次聚合 (任意维度)
- "为什么 Flink 只做 1 分钟聚合？因为更细粒度的多维组合状态太大。
  ClickHouse 擅长在查询时做 ad-hoc 聚合"

#### 40-50 分钟: 权衡与扩展讨论

**主动提出**: "让我讨论三个关键权衡"

1. **Lambda vs Kappa**: "Lambda 增加了维护复杂度 (两套管道),
   但计费精确度是硬性需求。我用 Apache Beam 统一编程模型来缓解"
2. **精确 vs 近似**: "计费用精确 HashMap, 分析用 HyperLogLog。
   不是非此即彼, 不同路径可以选不同精度"
3. **集中聚合 vs 分布式聚合**: "我选集中聚合因为去重需要全局视野。
   如果 GDPR 要求数据本地化, 需要在 EU 区域做本地聚合 + 脱敏后汇总"

**10x/100x 规模**: "10x 主要是水平扩展 (更多 Kafka 分区 + Flink 并行度
+ ClickHouse shard)。100x 需要分层聚合 + 边缘预聚合 + 采样推断"

#### 50-55 分钟: 收尾

**我会改进什么**:
- 添加 **A/B 测试框架**: 不同的欺诈检测策略可以在线实验
- 实现 **预算控制**: 广告主设置日预算, 系统实时扣减, 余额不足时停止展示
- 添加 **归因模型**: 多次展示后的点击归因给哪次展示？
  (Last-click vs multi-touch attribution)

**监控清单**:
- 端到端延迟 (event_time 到 ClickHouse 可查询)
- Kafka consumer lag
- 实时 vs 批处理聚合差异
- 欺诈率突变

#### 55-60 分钟: 向面试官提问

- "你们的广告系统目前用什么架构做点击聚合？是 Lambda 还是 Kappa？"
- "计费结算的频率是什么？实时扣费还是日结？"
- "欺诈检测的误判率目前在什么水平？广告主反馈如何？"

---

### 面试核心要点总结

关键设计决策:
- **Lambda Architecture**: 实时路径 (分析) + 批处理路径 (计费), 各取所长
- **Exactly-once**: Kafka 幂等 + Flink checkpoint + 两阶段提交, 三层保证
- **两级去重**: Bloom Filter (快速过滤) + RocksDB 精确 Set (零误报)
- **混合欺诈检测**: 实时规则引擎 (低延迟高召回) + 离线 ML (高精度), 互补
- **ClickHouse**: 列式 OLAP, 向量化执行, 亚秒级多维查询

规模: 5 亿 DAU, 100 亿日展示, 350K 峰值 QPS, 7 GB Flink 状态,
~$50K/月。"
"""


def populate_interview_ad_click() -> None:
    """Create or update the interview-ad-click-aggregator record with all 8 sections."""
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
    populate_interview_ad_click()
