"""Populate interview-ride-sharing system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Ride-sharing
System (Uber/Lyft). Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-ride-sharing"
TITLE = "Design a Ride-sharing System (Uber)"
DISPLAY_ORDER = 103

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**打车系统 (Ride-sharing System)**，类似 **Uber** / **Lyft**。系统需要
实时匹配乘客和附近司机、计算预估到达时间 (**ETA**, Estimated Time of Arrival)、
动态定价、追踪行程状态、处理支付结算。系统需要支持数百万并发用户和数十万活跃司机。

### 功能性需求 (Functional Requirements)

1. **乘客叫车 (Ride Request)**：乘客输入起点和终点，系统显示预估价格和 ETA，
   乘客确认后发起叫车请求
2. **司机匹配 (Driver Matching)**：系统根据距离、ETA 和供需状态将请求分配给
   最合适的附近司机
3. **实时位置追踪 (Real-time Location Tracking)**：行程中持续更新司机位置，
   乘客可在地图上实时查看
4. **动态定价 (Dynamic Pricing / Surge Pricing)**：根据供需比实时调整价格倍率
5. **行程管理 (Trip Management)**：行程状态流转 -- requested -> matched ->
   driver_en_route -> arrived -> in_progress -> completed
6. **支付结算 (Payment & Settlement)**：行程结束后自动计费、扣款、司机分成
7. **评价系统 (Rating System)**：乘客和司机互评（1-5 星）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（叫车服务不可用直接影响收入和用户信任）
- **延迟 (Latency)**：叫车匹配 < 5 秒；位置更新 < 1 秒端到端延迟；
  ETA 计算 < 500ms
- **吞吐量 (Throughput)**：峰值 100 万活跃司机同时上报位置（每 3 秒一次 ->
  ~333K 位置更新/秒）
- **一致性 (Consistency)**：一个行程只能匹配一个司机（强一致），位置数据可
  最终一致
- **可扩展性 (Scalability)**：从单城市扩展到全球数百个城市

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 是否需要支持拼车 (Ride Pool/Share)？** -- WHY: 拼车需要路径匹配算法
   和动态路线规划，复杂度远高于单人行程。如果支持，需要额外的 route-matching
   引擎和 detour 计算逻辑。

2. **Q: 匹配策略是就近匹配还是全局最优？** -- WHY: 就近匹配 (Greedy) 实现简单
   但可能不是全局最优（如司机 A 距乘客 X 最近但 A 顺路去乘客 Y）。全局最优需要
   **批量匹配 (Batch Matching)** 算法（如 Hungarian Algorithm），计算复杂度高。

3. **Q: 位置更新频率是多少？精度要求？** -- WHY: GPS 每秒更新 vs 每 3-5 秒更新，
   对系统吞吐量影响巨大。100 万活跃司机 x 每秒更新 = 100 万 QPS；每 3 秒更新
   = 33 万 QPS。精度要求影响 Geospatial 索引粒度。

4. **Q: 支持哪些交通工具类型？** -- WHY: 如果支持 UberX / UberXL / UberBlack /
   UberPool，匹配逻辑需要按车型过滤，定价模型也不同。

5. **Q: 是否需要支持预约叫车 (Scheduled Rides)？** -- WHY: 预约叫车需要调度器
   提前分配司机，与实时叫车的即时匹配逻辑完全不同。

6. **Q: 定价是否需要考虑路线距离还是直线距离？** -- WHY: 路线距离需要调用
   **路径规划 API** (Routing API)，依赖外部地图服务（Google Maps / OSRM）；
   直线距离用 **Haversine 公式**即可计算。

### 范围外 (Out of Scope)

- 地图渲染和导航（假设使用第三方地图服务如 Google Maps / Mapbox）
- 司机注册审核和背景调查
- 客服和纠纷处理系统
- 拼车 / 顺风车（单人行程即可）
- 预约叫车调度
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Rider App                      Driver App
   |                               |
   v                               v
[API Gateway / Load Balancer]  <-- HTTP/WebSocket
   |         |          |
   v         v          v
Ride Svc   Location    Pricing
           Svc         Svc
   |         |          |
   v         v          v
Trip DB   Location    Surge
(Postgres) Store      Cache
          (Redis      (Redis)
           Geospatial)
              |
              v
         Matching Svc
              |
              v
       Notification Svc
       (Push to Driver/Rider)
```

### 组件职责 (Component Responsibilities)

| 组件 | 职责 | 技术选型 |
|------|------|----------|
| **API Gateway** | 认证、限流、请求路由 | Kong / Envoy |
| **Ride Service** | 行程生命周期管理（创建、状态流转、完成） | Python/Go 微服务 |
| **Location Service** | 接收和存储司机实时位置，提供附近司机查询 | Go 微服务 (高并发) |
| **Matching Service** | 将乘客请求与最优司机匹配 | Go/Java 微服务 |
| **Pricing Service** | 计算预估价格、动态定价倍率 | Python 微服务 |
| **Notification Service** | 向司机推送叫车请求、向乘客推送状态更新 | WebSocket + Push |
| **Payment Service** | 行程结算、扣款、司机分成 | Java 微服务 |
| **Trip DB** | 行程记录持久化 | PostgreSQL (ACID) |
| **Location Store** | 司机实时位置索引 | Redis (Geospatial) |
| **Surge Cache** | 动态定价倍率缓存 | Redis |

### 核心流程 (Core Flow)

**叫车流程 (Ride Request Flow)**:

1. 乘客输入起终点 -> **Pricing Service** 计算预估价格（基础费 + 距离费 + 时间费）
   x **Surge Multiplier**
2. 乘客确认叫车 -> **Ride Service** 创建 Trip 记录（状态: `REQUESTED`）
3. **Ride Service** 调用 **Matching Service** 寻找最优司机
4. **Matching Service** 查询 **Location Service** 获取附近空闲司机列表
5. **Matching Service** 按 ETA 排序，选择最优司机，发送请求
6. **Notification Service** 推送叫车请求到司机 App（WebSocket / Push）
7. 司机接受 -> Trip 状态更新为 `MATCHED`，通知乘客
8. 司机拒绝或超时 -> 重新匹配下一个司机

**位置更新流程 (Location Update Flow)**:

1. 司机 App 每 3-5 秒通过 WebSocket 上报 GPS 坐标 `(lat, lng, timestamp)`
2. **Location Service** 更新 Redis Geospatial 索引
3. 行程中，**Location Service** 同时推送位置到乘客 App（通过 WebSocket）

### 关键设计决策 (Key Design Decisions)

1. **位置存储选 Redis Geospatial** -- 内存级延迟（< 1ms），原生支持
   `GEOADD` / `GEOSEARCH` / `GEODIST`。百万级司机位置数据约 200MB 内存。
2. **WebSocket 用于实时通信** -- 位置更新和行程状态变更需要服务端主动推送，
   HTTP 轮询浪费带宽且延迟高。
3. **匹配和行程分离** -- Matching Service 是无状态计算服务，可独立扩缩容。
   Ride Service 管理有状态的行程生命周期，需要 DB 事务保证一致性。
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API & Data Schema)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与接口设计 (Dataflow & API Design)

### 核心 API (Core APIs)

**1. 价格预估 (Price Estimate)**

```
POST /api/v1/rides/estimate
{
  "pickup_lat": 37.7749,
  "pickup_lng": -122.4194,
  "dropoff_lat": 37.3382,
  "dropoff_lng": -121.8863,
  "vehicle_type": "UberX"
}
Response:
{
  "estimated_price_min": 25.50,
  "estimated_price_max": 32.00,
  "surge_multiplier": 1.5,
  "estimated_duration_min": 35,
  "estimated_distance_km": 48.2,
  "eta_pickup_min": 4
}
```

**2. 发起叫车 (Request Ride)**

```
POST /api/v1/rides
{
  "rider_id": "R-12345",
  "pickup": {"lat": 37.7749, "lng": -122.4194},
  "dropoff": {"lat": 37.3382, "lng": -121.8863},
  "vehicle_type": "UberX",
  "payment_method_id": "pm_abc123"
}
Response:
{
  "trip_id": "TRIP-98765",
  "status": "REQUESTED",
  "estimated_price": 28.50,
  "surge_multiplier": 1.5
}
```

**3. 司机接受/拒绝 (Driver Accept/Decline)**

```
PUT /api/v1/rides/{trip_id}/respond
{
  "driver_id": "D-67890",
  "action": "accept"  // or "decline"
}
```

**4. 位置上报 (Location Update -- WebSocket)**

```
WS /ws/location
{
  "driver_id": "D-67890",
  "lat": 37.7751,
  "lng": -122.4180,
  "heading": 45,
  "speed_kmh": 30,
  "timestamp": 1712345678
}
```

**5. 行程状态更新 (Trip Status Update)**

```
PUT /api/v1/rides/{trip_id}/status
{
  "status": "DRIVER_ARRIVED"  // PICKUP -> IN_PROGRESS -> COMPLETED
}
```

### 数据模型 (Data Schema)

**Trip 表 (PostgreSQL)**

| 字段 | 类型 | 说明 |
|------|------|------|
| trip_id | UUID (PK) | 行程唯一 ID |
| rider_id | UUID (FK) | 乘客 ID |
| driver_id | UUID (FK, nullable) | 匹配的司机 ID |
| status | ENUM | REQUESTED / MATCHED / DRIVER_EN_ROUTE / ARRIVED / IN_PROGRESS / COMPLETED / CANCELLED |
| pickup_lat / pickup_lng | DECIMAL | 上车点 |
| dropoff_lat / dropoff_lng | DECIMAL | 下车点 |
| vehicle_type | VARCHAR | UberX / UberXL / UberBlack |
| surge_multiplier | DECIMAL | 动态定价倍率 |
| estimated_price | DECIMAL | 预估价格 |
| actual_price | DECIMAL | 实际价格（行程结束后计算） |
| started_at | TIMESTAMP | 行程开始时间 |
| completed_at | TIMESTAMP | 行程结束时间 |
| created_at | TIMESTAMP | 订单创建时间 |

**Driver Location (Redis Geospatial)**

```
GEOADD drivers:active {lng} {lat} {driver_id}
GEOSEARCH drivers:active FROMLONLAT {lng} {lat} BYRADIUS 5 km ASC COUNT 20
```

每个 driver_id 同时在 Redis Hash 中存储元数据：

```
HSET driver:{driver_id} status "available" vehicle_type "UberX"
    rating 4.8 current_trip ""
```

**Surge Pricing (Redis Hash per Geohash Cell)**

```
HSET surge:{geohash_prefix} multiplier 1.5 demand 150 supply 80
    updated_at 1712345678
```

### 状态机 (Trip State Machine)

```
REQUESTED --(driver matched)--> MATCHED
MATCHED --(driver en route)--> DRIVER_EN_ROUTE
DRIVER_EN_ROUTE --(driver arrived at pickup)--> ARRIVED
ARRIVED --(rider picked up, trip starts)--> IN_PROGRESS
IN_PROGRESS --(reach destination)--> COMPLETED

Any state --(rider/driver cancels)--> CANCELLED
REQUESTED --(no driver found in timeout)--> CANCELLED
MATCHED --(driver cancels)--> REQUESTED (re-match)
```
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Core Algorithms & Data Structures)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 核心算法与数据结构 (Core Algorithms & Data Structures)

### 算法 1: 附近司机查询 -- Geospatial Indexing

**方案: Redis Geospatial (底层使用 Sorted Set + Geohash)**

Redis 的 `GEOADD` 将经纬度编码为 52-bit **Geohash**，存储在 Sorted Set 中。
`GEOSEARCH` 利用 Geohash 的前缀匹配特性快速查找范围内的点。

```python
# 添加司机位置
redis.geoadd("drivers:active", lng, lat, driver_id)

# 查询半径 5km 内最近的 20 个司机
nearby = redis.geosearch(
    "drivers:active",
    longitude=pickup_lng, latitude=pickup_lat,
    radius=5, unit="km",
    sort="ASC", count=20,
)
```

**时间复杂度**: $O(\log N + K)$，其中 $N$ 是总司机数，$K$ 是返回结果数。
100 万司机中查询附近 20 个，耗时 < 1ms。

**替代方案对比**:

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Redis Geospatial** | 内存级延迟，API 简单 | 单机内存限制 |
| **QuadTree** | 自适应密度分区 | 需自己实现，更新代价高 |
| **Geohash + DB** | 持久化，支持复杂查询 | 延迟高（磁盘 IO） |
| **S2 Geometry** (Google) | 精确球面计算 | 复杂度高 |
| **H3** (Uber) | 六边形网格，均匀分区 | 学习成本高 |

### 算法 2: 司机匹配 (Driver Matching)

**方案: 贪心匹配 + 评分函数 (Greedy with Scoring)**

对每个候选司机计算匹配得分，选择得分最高的司机：

$$\text{score}(d) = w_1 \cdot \frac{1}{\text{ETA}(d)} + w_2 \cdot \text{rating}(d) + w_3 \cdot \text{acceptance\_rate}(d)$$

其中 $w_1 = 0.6$（ETA 权重最高），$w_2 = 0.2$（司机评分），$w_3 = 0.2$（接单率）。

**匹配流程**:

1. 从 Location Service 获取附近 $K$ 个空闲司机（$K = 10-20$）
2. 并行调用 Routing API 计算每个司机到上车点的 **ETA**
3. 按 $\text{score}(d)$ 排序，选择得分最高的司机
4. 向该司机发送请求，等待 15 秒回复
5. 若拒绝或超时，选下一个司机（最多尝试 3 轮）

**进阶: 批量匹配 (Batch Matching)**

高峰期同一区域可能有多个乘客同时叫车。全局最优匹配使用
**二部图匹配 (Bipartite Matching)**：

- 左边节点: 待匹配的乘客请求
- 右边节点: 附近空闲司机
- 边权重: 匹配得分 $\text{score}(d, r)$
- 使用 **Hungarian Algorithm** 求最大权匹配（$O(N^3)$，$N$ 通常 < 50）

Uber 实际使用的是每 2 秒一批的 **Batch Matching**，在局部区域内全局优化，
兼顾实时性和全局最优。

### 算法 3: 动态定价 (Surge Pricing)

**目标**: 供不应求时提高价格以激励更多司机上线，同时抑制需求。

**实现**:

将城市划分为 **Geohash Cell**（约 1km x 1km），每个 cell 独立计算供需比：

$$\text{surge\_multiplier} = \max\left(1.0,\ \min\left(S_{\max},\ \alpha \cdot \frac{D}{S + \epsilon}\right)\right)$$

其中：
- $D$ = 该 cell 过去 5 分钟的叫车请求数（**demand**）
- $S$ = 该 cell 当前空闲司机数（**supply**）
- $\alpha$ = 调节系数（通常 1.2-2.0，由城市运营团队配置）
- $S_{\max}$ = 最大倍率上限（通常 3.0-5.0）
- $\epsilon$ = 防止除零的小常数

**更新频率**: 每 1-2 分钟重新计算一次，存入 Redis，Pricing Service 读取。

**价格计算**:

$$\text{price} = (\text{base\_fare} + \text{distance} \times \text{per\_km} + \text{duration} \times \text{per\_min}) \times \text{surge\_multiplier}$$

### 算法 4: ETA 估算

**方案: 分层 ETA 计算**

1. **粗估 (Straight-line)**：Haversine 公式计算直线距离，除以平均车速：

$$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1 \cdot \cos\phi_2 \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

$$\text{ETA}_{\text{rough}} = \frac{d}{\text{avg\_speed}} \times 1.4$$

乘以 1.4 是 **routing factor**（实际道路距离通常是直线距离的 1.2-1.6 倍）。

2. **精估 (Routing API)**：调用 Google Maps / OSRM 获取实际路线距离和时间。
   只对 top-K 候选司机做精估（减少 API 调用次数）。

3. **ML 模型 (Production)**：用历史行程数据训练模型，输入 (时间段, 天气, 路段拥堵度,
   起终点 geohash)，输出 ETA。比 Routing API 更准确且不依赖外部服务。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability -- Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产约束与深度解析 (Production Constraints & Deep Dive)

### 具体规模数字 (Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU (乘客) | 2000 万 |
| 日活司机 | 100 万 |
| 日订单量 | 1500 万 |
| 峰值叫车 QPS | ~5,000 |
| 位置更新 QPS | ~333,000 (100 万司机 x 每 3 秒一次) |
| WebSocket 并发连接 | ~150 万 (100 万司机 + 50 万行程中乘客) |
| Redis 内存 (位置索引) | ~200 MB (100 万司机 x ~200 bytes/entry) |
| Trip DB 日增量 | ~1500 万行/天 |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **Location Service** | 无法查询附近司机，匹配失败 | 多实例 + Redis Cluster (6 节点 3 主 3 从) |
| **Redis Geospatial** | 位置索引丢失 | Redis Cluster + AOF 持久化，故障时从 DB 重建 |
| **Matching Service** | 新叫车无法匹配 | 无状态多实例，故障实例自动移除 |
| **WebSocket Gateway** | 位置更新和推送中断 | 多实例 + sticky session (基于 connection ID) |
| **Trip DB (Postgres)** | 行程数据不可读写 | 主从复制 + 自动 failover (Patroni) |
| **Pricing Service** | 无法计算价格 | 多实例 + 降级到上次已知价格 |

### 位置数据的高并发处理

**问题**: 100 万司机每 3 秒上报位置 = 33 万 QPS 写入。

**解决方案**:

1. **WebSocket 连接层**: Go 编写的 WebSocket Gateway，单实例支持 10 万并发连接
   （利用 Go 的 goroutine 和 epoll）。10-15 个实例覆盖 100 万连接。

2. **批量写入 Redis**: 不逐条写入，而是在 Gateway 层攒批 -- 每 100ms 将
   积累的位置更新批量 pipeline 写入 Redis（`GEOADD` 支持一次添加多个成员）。
   批量大小 ~100-500 条/批。

3. **位置数据分片**: 按城市/区域分片到不同 Redis 实例。匹配查询只查本城市的 Redis。

4. **位置历史异步写入**: 实时索引只存最新位置（Redis），位置历史轨迹异步写入
   **时序数据库** (InfluxDB / TimescaleDB) 用于行程回放和 ETA 模型训练。

### 多城市 / 跨区域部署 (Multi-Region Deployment)

**方案: 按城市分片 (City-based Sharding)**

- 每个城市（或城市群）一个独立的 Location Service + Redis 实例
- 叫车请求根据 pickup 坐标路由到对应城市的服务实例
- Trip DB 可以全局共享（跨城市行程较少）或按区域分片
- **Config Service** 管理城市配置（基础费率、surge 参数、营业时间）

**全球化部署**:

- 美国、欧洲、亚太各一个 Region，每个 Region 独立运行完整服务栈
- 用户账户和支付信息全局复制（跨 Region 同步，延迟 < 5 秒）
- 用户在不同城市打车时，请求路由到当地 Region

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 | 含义 |
|------|----------|------|
| 匹配成功率 | < 90% | 供需严重失衡或匹配算法异常 |
| 匹配耗时 P99 | > 10s | Matching Service 性能下降 |
| WebSocket 断连率 | > 5%/min | 网络或 Gateway 异常 |
| 位置更新延迟 P99 | > 3s | Location Service 积压 |
| Trip DB 写延迟 P99 | > 100ms | 数据库压力过大 |
| Surge 计算延迟 | > 5s | Pricing Service 异常 |
| 乘客取消率 | > 30% | 等待时间过长或价格过高 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|------------------|
| **位置存储** | Redis Geospatial (内存) | PostGIS (磁盘) | **Redis** -- 33 万 QPS 的写入和亚毫秒查询需求，PostGIS 延迟 5-10ms 无法满足。Redis 100 万条目仅 200MB 内存，成本可接受。 |
| **实时通信** | WebSocket (长连接) | HTTP Long Polling / SSE | **WebSocket** -- 双向通信（位置上报 + 状态推送），延迟最低。Long Polling 有连接开销，SSE 是单向的。 |
| **匹配算法** | 贪心 (Greedy: 最近司机) | 批量最优 (Batch Matching) | **混合** -- 低峰期用 Greedy（响应快），高峰期用 Batch Matching（2 秒一批，全局优化供需分配）。 |
| **ETA 计算** | 自有 ML 模型 | Google Maps API | **分层** -- 粗筛用 Haversine (免费、快速)，top-K 用 Routing API (准确)，Production 逐步迁移到自有 ML 模型 (成本可控)。 |
| **Trip DB** | PostgreSQL (关系型) | DynamoDB (NoSQL) | **PostgreSQL** -- 行程涉及多表关联（rider, driver, payment），ACID 事务保证一致性。DynamoDB 适合简单 KV 查询但不适合复杂关联。 |
| **动态定价粒度** | 全城市统一 | 按 Geohash Cell 分区 | **按 Cell 分区** -- 避免"机场需求高导致全城涨价"的问题。每个 1km x 1km cell 独立计算供需比。 |

### 一致性 vs 可用性 (Consistency vs Availability)

**强一致性区域**:

- **行程-司机匹配**: 一个行程只能匹配一个司机。使用 Redis 分布式锁 +
  PostgreSQL 行锁，确保不会出现两个乘客同时匹配到同一个司机。
  ```
  SETNX lock:driver:{driver_id} {trip_id} EX 30
  ```
  获取锁成功才能进行匹配。

- **支付扣款**: 幂等 key + DB 事务，确保一次行程只扣款一次。

**最终一致性区域**:

- **位置数据**: 司机位置更新有 1-3 秒延迟可以接受。乘客看到的司机位置可能
  略有偏差，不影响核心功能。
- **Surge 定价**: 1-2 分钟更新一次，短时间内定价可能不完全反映最新供需。
- **评分**: 行程结束后评分异步更新，P99 在 5 秒内生效。

### 成本 vs 性能 (Cost vs Performance)

| 组件 | 高性能方案 | 低成本替代 | 性能差距 |
|------|-----------|-----------|----------|
| 位置索引 | Redis Cluster (6 节点) | PostgreSQL + PostGIS | 延迟: 0.5ms vs 5-10ms |
| ETA 计算 | Google Maps API (5 USD/1000 请求) | 自有 Haversine + 路网模型 | 精度: 95% vs 80% |
| WebSocket | 自建 Go Gateway | 托管服务 (AWS API Gateway WS) | 成本: 低（自建运维成本高）vs 高（按连接计费） |
| 匹配算法 | GPU 加速批量匹配 | CPU Greedy 匹配 | 速度: 50ms vs 5ms (但 Greedy 质量低 10%) |

### 10 倍 / 100 倍规模变化 (What Changes at 10x / 100x Scale)

**当前规模 (1x): 100 万日活司机，1500 万日单**

**10x (1000 万日活司机，1.5 亿日单)**:
- Location Service: Redis Cluster 60+ 节点，按城市分片
- WebSocket Gateway: 100+ 实例 (每实例 10 万连接)
- Matching Service: 必须全面切换到 Batch Matching
- Trip DB: 分库分表（按 city_id sharding），日增 1.5 亿行
- 引入 **ML 路径定价**: 基于实时路况的精确定价，取代简单公式

**100x (1 亿日活司机，15 亿日单)**:
- 位置存储从 Redis 迁移到专用的 **Geospatial Engine** (如 Uber 自研的 H3 + 内存索引)
- Matching 使用 **强化学习 (RL)** 模型全局优化调度
- 引入 **自动驾驶调度层**: 混合管理人类司机和自动驾驶车辆
- Trip DB 使用 **分布式 NewSQL** (TiDB/CockroachDB)
- 位置历史存入 **数据湖** (S3 + Parquet) 供离线分析
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

**Q: 如果两个乘客同时叫车，只有一个附近空闲司机，你怎么保证不会把同一个司机
分配给两个乘客？**

> **承认局限**: 在高并发场景下，两个 Matching Service 实例可能同时查到同一个
> 空闲司机并尝试匹配，导致冲突。
>
> **缓解措施**:
>
> 1. **Redis 分布式锁 (Distributed Lock)**：匹配前对司机加锁：
>    `SETNX lock:driver:{driver_id} {trip_id} EX 30`。只有获取锁成功的请求
>    才能完成匹配。锁失败的请求自动选择下一个候选司机。
> 2. **DB 层乐观锁 (Optimistic Locking)**：Trip 表使用 `driver_id` 唯一约束 +
>    version 字段。即使 Redis 锁因网络问题失效，DB 写入时会冲突。
> 3. **两阶段确认 (Two-Phase Accept)**：Matching Service 先"预锁"司机
>    （Redis lock），然后等待司机 App 确认。司机真正点击"接受"后才写入 DB。
>    这 15 秒等待窗口内，该司机不会出现在其他匹配查询中。
>
> **数据**: Redis lock + DB 唯一约束的方案可将双重匹配的概率降低到 < 0.001%。

---

**Q: 高峰时段很多乘客叫不到车，ETA 显示 15 分钟但实际要等 30 分钟，怎么办？**

> **承认局限**: 供需严重失衡时，简单的就近匹配会导致大量乘客等待。ETA 基于
> 当前状态预测，未考虑排队效应。
>
> **缓解措施**:
>
> 1. **动态定价 (Surge Pricing)**：价格上涨 1.5-3x，一方面抑制非刚需需求，
>    另一方面激励更多司机上线（司机 App 显示"附近有高倍率区域"）
> 2. **供给侧优化**：
>    - **热力图推荐 (Heatmap)**：向空闲司机推荐高需求区域
>    - **目的地预测**：预测即将完成行程的司机，提前将其纳入匹配候选
>    - **连环派单 (Chained Dispatch)**：行程即将结束的司机提前匹配下一单
> 3. **ETA 诚实化**：ETA 计算加入排队模型 -- 如果该区域当前有 10 个待匹配请求
>    和 3 个空闲司机，告知用户"预计等待 12 分钟"而非司机到达时间。
> 4. **需求转移**：建议用户步行到附近更多空闲司机的位置，或推荐其他出行方式
>    （公交、自行车）
>
> **数据**: Surge pricing 通常能在 5-10 分钟内使供给增加 20-30%。连环派单
> 可将高峰时段的平均等待时间降低 15-25%。

---

**Q: 司机 GPS 信号不好（隧道、地下停车场），位置数据不准确或缺失怎么办？**

> **承认局限**: GPS 精度在城市峡谷 (urban canyon) 中可能偏差 50-100 米，
> 在隧道/地下完全丢失信号。不准确的位置会导致错误匹配和 ETA 偏差。
>
> **缓解措施**:
>
> 1. **位置数据过滤 (Location Filtering)**：
>    - 丢弃精度 > 100m 的 GPS 点
>    - 丢弃速度异常点（如 1 秒内移动 500m = 1800km/h，不可能）
>    - 使用 **Kalman Filter** 平滑轨迹，融合 GPS + WiFi + 基站定位
> 2. **位置超时机制**：如果司机 30 秒没有上报位置（信号丢失），将其标记为
>    `LOCATION_STALE`，从匹配候选中移除
> 3. **Map Matching (路网吸附)**：将 GPS 坐标"吸附"到最近的道路上，
>    修正偏离道路的位置点。使用 **Hidden Markov Model (HMM)** + 路网图
>    推断最可能的道路位置
> 4. **乘客侧确认**：司机到达上车点时，App 弹出"确认已到达"按钮，
>    不完全依赖 GPS 触发状态变更
>
> **数据**: Kalman Filter + Map Matching 可将城市环境下的定位误差从
> 50-100m 降低到 5-10m。

---

**Q: 行程中乘客的 App 崩溃了，或者手机没电了，行程怎么办？**

> **承认局限**: 行程状态存储在服务端，乘客 App 断开不影响行程继续进行。
> 但可能导致乘客无法查看行程进度或手动结束行程。
>
> **缓解措施**:
>
> 1. **行程状态服务端权威**: 行程的状态机在 Ride Service（服务端）管理，
>    不依赖客户端。司机 App 正常的情况下，行程继续进行。
> 2. **司机端控制**: 行程开始/结束由司机 App 触发（点击"开始行程"/"到达目的地"）。
>    乘客 App 只是观察者，不影响行程流转。
> 3. **自动完成**: 如果司机到达目的地附近（GPS 围栏 100m 内），App 弹出
>    "完成行程"按钮。司机点击后自动计费。
> 4. **异常行程兜底**: 行程超过预计时间 3 倍仍未完成时，系统自动标记为
>    `ABNORMAL`，触发客服介入。
> 5. **重连恢复**: 乘客重新打开 App 时，自动查询服务端活跃行程状态并恢复显示。
>
> **数据**: < 0.1% 的行程因双端 App 异常需要客服介入。

---

**Q: 你的动态定价会不会被乘客骂？怎么让定价更公平？**

> **承认局限**: Surge pricing 是 Uber 最具争议的功能之一。暴雨/紧急事件时
> 价格飙升会引发社交媒体负面反应和监管压力。
>
> **缓解措施**:
>
> 1. **价格上限 (Price Cap)**：设置最大 surge 倍率（如 3x-5x），极端情况下
>    不无限涨价
> 2. **价格透明**: 叫车前明确告知"当前为高峰时段，预估价格为 $X（正常价格的 2 倍）"。
>    乘客在确认前已知价格，减少行程后的纠纷
> 3. **渐进式涨价**: 不跳跃式涨价（1x -> 3x），而是平滑过渡（1x -> 1.5x -> 2x），
>    给司机上线时间
> 4. **紧急事件豁免**: 自然灾害、大规模事件期间自动关闭 surge pricing
>    （Uber 在 Sandy 飓风后增加了此政策）
> 5. **订阅计划 (Uber Pass/One)**：会员用户享受 surge 折扣或 surge 上限，
>    增加用户粘性同时缓解定价焦虑
>
> **数据**: 设置 5x 上限 + 紧急事件豁免后，相关投诉减少 40%。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "打车系统的核心是实时匹配乘客和附近司机，并管理行程的完整生命周期。
> 我想先确认几点：是否需要支持拼车？匹配策略是就近还是全局最优？
> 位置更新频率大概是多少？我假设 100 万日活司机、每 3 秒上报一次位置。
> 是否需要预约叫车功能？"
>
> 列出 FR: 叫车请求、司机匹配、实时位置追踪、动态定价、行程管理、支付结算、评价。
> 列出 NFR: 99.99% 可用性、匹配 < 5 秒、位置更新 < 1 秒、峰值 33 万位置 QPS。
> 明确 Out of Scope: 拼车、预约叫车、地图导航、客服。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "核心组件: Ride Service (行程管理) + Location Service (位置索引) +
> Matching Service (司机匹配) + Pricing Service (动态定价) + WebSocket Gateway
> (实时通信)。位置数据存 Redis Geospatial -- 100 万司机 33 万 QPS 的写入
> 需要内存级延迟。行程数据存 PostgreSQL -- 需要 ACID 事务。
> 司机通过 WebSocket 实时上报位置，乘客通过 WebSocket 接收位置更新和状态推送。"
>
> "匹配流程: 乘客叫车 -> Matching Service 查询附近空闲司机 (Redis GEOSEARCH) ->
> 按 ETA/评分排序 -> 向最优司机推送请求 -> 司机接受/拒绝 -> 更新行程状态。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: 位置服务与高并发 (8-10 分钟)**
> "100 万司机每 3 秒上报 = 33 万 QPS。WebSocket Gateway 用 Go 实现，单实例
> 支持 10 万并发连接，10-15 个实例。Gateway 层每 100ms 批量 pipeline 写入
> Redis GEOADD。按城市分片到不同 Redis 实例。位置历史异步写入时序数据库。
> GPS 信号差时用 Kalman Filter 平滑 + Map Matching 路网吸附。"

**重点 2: 匹配算法与公平性 (8-10 分钟)**
> "低峰期用 Greedy -- 取附近 10 个空闲司机，并行算 ETA，选最优。
> 高峰期用 Batch Matching -- 每 2 秒一批，构建二部图，用 Hungarian Algorithm
> 求全局最优匹配。防止双重匹配: Redis 分布式锁 + DB 唯一约束。
> 司机 15 秒不响应自动轮转到下一个候选。"

**重点 3: 动态定价 (5-8 分钟)**
> "城市按 1km x 1km 的 Geohash Cell 分区。每个 cell 独立计算供需比，
> 每 1-2 分钟更新一次 surge multiplier。公式: alpha x (demand / supply)，
> clamp 到 [1.0, 5.0]。价格 = (base + distance x per_km + duration x per_min)
> x surge。叫车前向乘客透明展示 surge 倍率和预估总价。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: Redis vs PostGIS (延迟 vs 持久化)，Greedy vs Batch Matching
> (响应速度 vs 全局最优)，WebSocket vs Long Polling (复杂度 vs 实时性)。
> 10x 规模: Redis Cluster 60+ 节点，WebSocket 100+ 实例，全面 Batch Matching，
> Trip DB 按城市分片。100x: 自研 Geospatial Engine，RL 调度模型，
> 自动驾驶车辆混合调度。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 拼车匹配算法 -- 实时路径匹配和 detour 计算，
> (2) 预约叫车调度 -- 提前锁定司机资源并处理取消和冲突，
> (3) 反欺诈 -- 识别虚假位置、刷单和 GPS 欺骗。"

### 55-60 分钟: 向面试官提问

> "你们的匹配算法用的是 Greedy 还是 Batch Matching？切换过程中遇到了什么挑战？
> 动态定价的参数是怎么调优的？有没有用 ML 模型替代规则引擎？
> 位置服务用的是什么 Geospatial 引擎？"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计打车系统 -- 实时匹配乘客和附近司机，100 万日活司机，
   33 万 位置更新 QPS，匹配 < 5 秒。

2. **(60 秒) 架构**: Location Service + Redis Geospatial 存储司机实时位置。
   WebSocket Gateway (Go) 处理位置上报和状态推送。Matching Service 查询附近
   空闲司机 (GEOSEARCH)，按 ETA/评分排序匹配。Pricing Service 按 Geohash Cell
   计算 surge multiplier。Trip 生命周期存 PostgreSQL。

3. **(60 秒) 关键算法**: 匹配得分 = 0.6/ETA + 0.2*rating + 0.2*accept_rate。
   低峰 Greedy，高峰 2 秒一批 Batch Matching (Hungarian Algorithm)。
   防双重匹配: Redis SETNX 锁 + DB 唯一约束。GPS 过滤: Kalman Filter +
   Map Matching。

4. **(30 秒) 扩展**: 按城市分片 Redis 和 Location Service。WebSocket Gateway
   10 万连接/实例，批量 pipeline 写入。10x 需 Batch Matching 全面切换；
   100x 需自研 Geospatial Engine + RL 调度。
"""


def populate_interview_ride_sharing() -> None:
    """Create or update the interview-ride-sharing record with all 8 sections."""
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
    populate_interview_ride_sharing()
