"""Populate interview-proximity-service system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Proximity
Service (Yelp / Google Places). Idempotent: creates record if missing,
overwrites existing.

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

SLUG = "interview-proximity-service"
TITLE = "Design a Proximity Service (Yelp)"
DISPLAY_ORDER = 104

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**附近搜索服务 (Proximity Service)**，类似 **Yelp** / **Google Places** /
**大众点评**。用户可以根据当前位置搜索附近的商家（餐厅、咖啡馆、加油站等），
查看商家详情、评价和照片。系统需要支持高并发的地理位置搜索查询，商家信息的
增删改查，以及按距离、评分等维度排序的搜索结果。

### 功能性需求 (Functional Requirements)

1. **附近商家搜索 (Nearby Search)**：用户输入当前位置和搜索半径（或使用默认半径），
   系统返回范围内的商家列表，支持按距离、评分、热度排序
2. **商家详情查看 (Business Detail)**：点击商家查看详细信息 -- 地址、营业时间、
   电话、照片、菜单、价格区间、用户评价
3. **商家信息管理 (Business CRUD)**：商家主可以添加、更新、删除自己的商家信息
4. **搜索过滤 (Search Filtering)**：按类别（餐厅、咖啡馆、健身房等）、评分范围、
   价格区间、营业状态（是否正在营业）过滤搜索结果
5. **评价系统 (Review System)**：用户可以对商家发表评价（文字 + 星级 1-5）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（搜索功能是核心路径，不可用直接影响用户体验）
- **延迟 (Latency)**：附近搜索 P99 < 200ms；商家详情页 P99 < 100ms
- **吞吐量 (Throughput)**：峰值搜索 QPS ~5,000；商家详情 QPS ~10,000
- **一致性 (Consistency)**：搜索结果可最终一致（新商家入驻后 1-5 分钟内可搜到
  即可），商家信息更新需较快生效（< 1 分钟）
- **可扩展性 (Scalability)**：支撑 2 亿商家、5000 万 DAU

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 搜索半径范围是多少？是否支持用户自定义？** -- WHY: 搜索半径决定 Geospatial
   索引的查询粒度。如果最大半径 50km（跨城市搜索），索引策略和查询效率会截然不同
   于 5km（步行范围）。

2. **Q: 商家数据是否需要支持多语言？** -- WHY: 多语言需要额外的本地化存储和搜索
   适配（如中文分词 vs 英文 tokenization），影响搜索引擎选型。

3. **Q: 商家信息的更新频率大概是多少？** -- WHY: 如果商家很少更新（一天几百次全量），
   可以用预计算索引 + 定时重建；如果频繁更新（每分钟上千次），需要增量索引更新方案。

4. **Q: 搜索结果需要考虑个性化吗（基于用户历史偏好）？** -- WHY: 个性化排序需要
   用户画像服务和推荐模型，大幅增加系统复杂度。先确认是否只需基于距离和评分的
   通用排序。

5. **Q: 是否需要支持"正在营业"过滤？** -- WHY: 营业状态是动态属性（随时间变化），
   不能简单存为静态字段。需要根据商家营业时间表和当前时间实时计算，或引入定时更新
   缓存。

6. **Q: 照片和评价数据量大概多少？** -- WHY: 如果每个商家平均 50 张照片 + 200 条
   评价，2 亿商家就是 100 亿照片 + 400 亿条评价，存储和 CDN 策略需要单独设计。

7. **Q: 是否需要支持地图视图（在地图上显示 pin）？** -- WHY: 地图视图需要在用户
   拖动地图时实时查询新区域的商家，QPS 会更高且查询区域不规则（矩形 bounding box
   而非圆形半径）。

### 范围外 (Out of Scope)

- 用户社交功能（关注好友、好友推荐）
- 商家广告和竞价排名
- 预约和点餐下单功能
- 照片上传和 CDN 存储细节（假设已有图片服务）
- 评价的反垃圾 / 反刷评机制
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Mobile App / Web Client
        |
        v
[API Gateway / Load Balancer]  -- HTTP REST
        |
   +---------+-----------+-----------+
   |         |           |           |
   v         v           v           v
Search    Business    Review     User
Service   Service     Service    Service
   |         |           |
   v         v           v
Geo Index  Business    Review
(Geohash   DB          DB
 + Cache)  (MySQL)     (MySQL)
   |
   v
Search Cache (Redis)
```

### 组件职责 (Component Responsibilities)

| 组件 | 职责 | 技术选型 |
|------|------|----------|
| **API Gateway** | 认证、限流、请求路由、协议转换 | Kong / Envoy |
| **Search Service (LBS)** | 接收用户位置和过滤条件，返回附近商家列表 | Java/Go 微服务 |
| **Business Service** | 商家信息 CRUD，商家主管理后台 | Python/Go 微服务 |
| **Review Service** | 评价的增删改查，评分聚合计算 | Python 微服务 |
| **User Service** | 用户注册/登录、用户画像 | Go 微服务 |
| **Geo Index** | 地理位置索引，支持范围查询 | Geohash + Redis / QuadTree |
| **Business DB** | 商家信息持久化 | MySQL (主从复制) |
| **Review DB** | 评价数据持久化 | MySQL (分表) |
| **Search Cache** | 缓存热门区域和搜索结果 | Redis Cluster |

### 核心流程 (Core Flow)

**附近搜索流程 (Nearby Search Flow)**:

1. 用户发送搜索请求 `(lat, lng, radius, filters)`
2. **API Gateway** 认证 + 限流后路由到 **Search Service (LBS)**
3. **Search Service** 将 `(lat, lng)` 转换为 **Geohash** 前缀，计算需要查询的
   Geohash cell 集合（中心 cell + 周围 8 个邻居 cell）
4. 先查 **Redis Cache** -- 如果该 Geohash 区域的商家列表已缓存且未过期，直接返回
5. Cache miss 时查 **Business DB** -- 按 Geohash 前缀查询 + 距离过滤 +
   应用筛选条件（类别、评分等）
6. 计算每个商家到用户的精确距离（**Haversine** 公式），按距离/评分排序
7. 返回分页结果，同时回写 Redis 缓存（TTL: 5 分钟）

**商家信息更新流程 (Business Update Flow)**:

1. 商家主通过管理后台提交信息更新
2. **Business Service** 更新 MySQL 主库
3. 异步通知 **Search Service** 更新 Geohash 索引和缓存
4. 缓存失效策略: 更新时主动 invalidate 该商家所在 Geohash cell 的缓存

### 关键设计决策 (Key Design Decisions)

1. **读写分离**: 搜索是读密集型（读写比 ~99:1）。Business DB 使用主从复制，
   Search Service 从 replica 读取 + Redis 缓存，写入走主库。
2. **Geohash 作为索引基础**: 将二维空间查询转换为一维前缀匹配，可以利用 B-Tree
   索引高效查询。Geohash 精度 6 位 (~1.2km x 0.6km cell) 对大多数搜索半径适用。
3. **搜索和商家管理分离**: Search Service 是无状态计算密集型服务，可独立扩缩容。
   Business Service 负责数据管理，变更频率低，不需要同等规模。
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API & Data Schema)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与接口设计 (Dataflow & API Design)

### 核心 API (Core APIs)

**1. 附近搜索 (Nearby Search)**

```
GET /api/v1/search/nearby
    ?lat=37.7749
    &lng=-122.4194
    &radius=5000          // meters, default 5000
    &category=restaurant  // optional filter
    &min_rating=4.0       // optional filter
    &sort_by=distance     // distance | rating | review_count
    &page=1
    &page_size=20

Response:
{
  "businesses": [
    {
      "id": "biz_abc123",
      "name": "Joe's Pizza",
      "category": "restaurant",
      "lat": 37.7751,
      "lng": -122.4180,
      "distance_m": 150,
      "rating": 4.5,
      "review_count": 328,
      "price_level": 2,
      "is_open": true,
      "thumbnail_url": "https://cdn.example.com/biz_abc123/thumb.jpg"
    }
  ],
  "total": 85,
  "page": 1,
  "has_next": true
}
```

**2. 商家详情 (Business Detail)**

```
GET /api/v1/businesses/{business_id}

Response:
{
  "id": "biz_abc123",
  "name": "Joe's Pizza",
  "category": "restaurant",
  "address": "123 Main St, San Francisco, CA",
  "lat": 37.7751,
  "lng": -122.4180,
  "phone": "+1-415-555-0123",
  "website": "https://joespizza.com",
  "hours": {
    "mon": "11:00-22:00",
    "tue": "11:00-22:00",
    "sat": "10:00-23:00",
    "sun": "closed"
  },
  "rating": 4.5,
  "review_count": 328,
  "price_level": 2,
  "photos": ["url1", "url2", "url3"],
  "attributes": ["outdoor_seating", "delivery", "wifi"]
}
```

**3. 商家创建/更新 (Business CRUD)**

```
POST /api/v1/businesses
{
  "name": "Joe's Pizza",
  "category": "restaurant",
  "lat": 37.7751,
  "lng": -122.4180,
  "address": "123 Main St, San Francisco, CA",
  "phone": "+1-415-555-0123",
  "hours": { ... }
}
Response: { "id": "biz_abc123", "status": "created" }

PUT /api/v1/businesses/{business_id}
{ "phone": "+1-415-555-9999", "hours": { ... } }
Response: { "status": "updated" }
```

**4. 发表评价 (Submit Review)**

```
POST /api/v1/businesses/{business_id}/reviews
{
  "user_id": "user_xyz",
  "rating": 5,
  "text": "Best pizza in SF! The crust is perfectly crispy.",
  "photos": ["url1"]
}
Response: { "review_id": "rev_001", "status": "created" }
```

### 数据模型 (Data Schema)

**Business 表 (MySQL)**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT (PK) | 商家唯一 ID |
| name | VARCHAR(255) | 商家名称 |
| category | VARCHAR(64) | 商家类别 |
| lat | DECIMAL(9,6) | 纬度 |
| lng | DECIMAL(9,6) | 经度 |
| geohash | VARCHAR(12) | 预计算的 Geohash（建索引） |
| address | TEXT | 地址 |
| phone | VARCHAR(20) | 电话 |
| website | VARCHAR(255) | 网站 |
| hours_json | JSON | 营业时间 JSON |
| rating | DECIMAL(2,1) | 平均评分（异步聚合更新） |
| review_count | INT | 评价总数 |
| price_level | TINYINT | 价格等级 1-4 |
| is_active | BOOLEAN | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 最后更新时间 |

**索引**: `INDEX idx_geohash (geohash)`, `INDEX idx_category_geohash (category, geohash)`

**Geohash Index (Redis)**

```
// 每个 Geohash cell 存储该区域内的商家 ID 列表
SET geohash:9q8yyk -> {biz_001, biz_002, biz_003, ...}

// 或使用 Redis Geospatial
GEOADD businesses {lng} {lat} {business_id}
GEOSEARCH businesses FROMLONLAT {lng} {lat} BYRADIUS 5 km ASC COUNT 50
```

**Review 表 (MySQL -- 按 business_id 分表)**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT (PK) | 评价 ID |
| business_id | BIGINT (FK) | 商家 ID |
| user_id | BIGINT (FK) | 用户 ID |
| rating | TINYINT | 评分 1-5 |
| text | TEXT | 评价文本 |
| photos | JSON | 评价附带照片 URL 列表 |
| created_at | TIMESTAMP | 发表时间 |

### 缓存策略 (Cache Strategy)

| 缓存层 | Key 格式 | Value | TTL | 失效方式 |
|--------|---------|-------|-----|----------|
| **搜索结果缓存** | `search:{geohash6}:{category}:{sort}` | 排序后的商家 ID 列表 | 5 min | 商家更新时 invalidate |
| **商家详情缓存** | `biz:{business_id}` | 完整商家信息 JSON | 30 min | 商家更新时 invalidate |
| **热门区域缓存** | `hot:{geohash4}` | 该区域 Top-50 商家 | 10 min | 定时刷新 |
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Core Algorithms & Data Structures)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 核心算法与数据结构 (Core Algorithms & Data Structures)

### 算法 1: Geohash -- 空间索引的核心

**原理**: 将二维的经纬度坐标编码为一个一维字符串。编码过程是交替对经度和纬度
做二分查找，每一步将区间一分为二，取 0 或 1，最后将二进制编码转为 Base32 字符串。

**关键属性**:
- **前缀匹配 = 空间邻近**: 两个位置的 Geohash 共享的前缀越长，它们在空间上越接近
- **精度可调**: Geohash 长度越长，对应的 cell 面积越小

| Geohash 长度 | Cell 宽度 | Cell 高度 | 适用场景 |
|:---:|:---:|:---:|:---|
| 4 | ~39.1 km | ~19.5 km | 城市级粗筛 |
| 5 | ~4.9 km | ~4.9 km | 社区级搜索 |
| 6 | ~1.2 km | ~0.6 km | 默认搜索半径 (推荐) |
| 7 | ~153 m | ~153 m | 精细搜索 |

**搜索半径与 Geohash 长度的映射**:

$$\text{geohash\_length} = f(\text{radius}) = \begin{cases} 4 & \text{if } r > 20\text{km} \\ 5 & \text{if } 5\text{km} < r \leq 20\text{km} \\ 6 & \text{if } 1\text{km} < r \leq 5\text{km} \\ 7 & \text{if } r \leq 1\text{km} \end{cases}$$

**边界问题 (Edge Case)**: 两个物理上相邻的位置可能落在不同的 Geohash cell 中
（边界效应）。解决方案: 不仅查询中心 cell，还要查询 **8 个邻居 cell**，共 9 个
cell 的结果合并后再做精确距离过滤。

```python
import geohash2

def get_search_cells(lat: float, lng: float, precision: int = 6) -> list[str]:
    "Return center + 8 neighbor geohash cells for search."
    center = geohash2.encode(lat, lng, precision)
    neighbors = geohash2.neighbors(center)  # returns 8 neighbors
    return [center] + neighbors  # 9 cells total
```

### 算法 2: Haversine 公式 -- 精确距离计算

搜索结果中需要计算每个商家到用户的精确距离（Geohash 只做粗筛，精排需要精确距离）:

$$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1 \cdot \cos\phi_2 \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

其中:
- $R = 6371$ km（地球平均半径）
- $\phi_1, \phi_2$ = 两点的纬度（弧度）
- $\Delta\phi = \phi_2 - \phi_1$（纬度差）
- $\Delta\lambda = \lambda_2 - \lambda_1$（经度差）

```python
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    "Calculate distance in meters between two lat/lng points."
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lng2 - lng1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))
```

### 算法 3: 替代方案 -- QuadTree

**QuadTree** 是另一种常见的空间索引结构。将二维空间递归地四等分，直到每个叶子
节点包含的点数 <= 阈值（如 100）。

**QuadTree vs Geohash 对比**:

| 维度 | Geohash | QuadTree |
|------|---------|----------|
| 索引类型 | 一维字符串，可用 B-Tree | 树结构，需内存存储 |
| 密度自适应 | 固定 cell 大小 | 密集区域自动细分 |
| 更新代价 | O(1) 插入/删除 | O(log N) 可能触发 rebalance |
| 查询 | 前缀匹配 + DB 索引 | 树遍历 + 范围查询 |
| 持久化 | 直接存 DB | 需序列化/反序列化 |
| 适合场景 | 商家密度较均匀 | 密度差异大（市中心 vs 郊区） |

**本设计选择 Geohash** -- 2 亿商家数据量大，需要利用 DB 的 B-Tree 索引高效查询。
QuadTree 更适合内存中的实时数据（如打车系统的司机位置）。

### 容量估算 (Capacity Estimation)

**DAU & QPS 估算**:

$$\text{DAU} = 5000 \text{ 万} = 50{,}000{,}000$$

$$\text{搜索 QPS} = \frac{50{,}000{,}000 \times 5 \text{ (日均搜索次数)}}{86{,}400} \approx 2{,}900 \text{ QPS}$$

$$\text{峰值搜索 QPS} = 2{,}900 \times 2 \approx 5{,}800 \text{ QPS}$$

$$\text{商家详情 QPS} \approx 2 \times \text{搜索 QPS} = 11{,}600 \text{ QPS (每次搜索点击 2 家)}$$

**存储估算**:

$$\text{商家数} = 2 \text{ 亿} = 200{,}000{,}000$$

$$\text{单条商家记录} \approx 1 \text{ KB (含索引)}$$

$$\text{商家数据总量} = 200{,}000{,}000 \times 1 \text{ KB} = 200 \text{ GB}$$

$$\text{评价数} = 200{,}000{,}000 \times 50 \text{ (平均每家 50 条)} = 100 \text{ 亿条}$$

$$\text{评价存储} = 10{,}000{,}000{,}000 \times 0.5 \text{ KB} = 5 \text{ TB}$$

**缓存估算 (80/20 法则)**:

$$\text{热门区域} = \text{总区域} \times 20\% \approx 200{,}000 \text{ 个 Geohash-6 cell}$$

$$\text{缓存大小} = 200{,}000 \times 50 \text{ (每 cell 50 个商家)} \times 200 \text{ bytes} = 2 \text{ GB}$$

**带宽估算**:

$$\text{搜索响应} \approx 20 \text{ 个商家} \times 500 \text{ bytes} = 10 \text{ KB/请求}$$

$$\text{峰值搜索带宽} = 5{,}800 \times 10 \text{ KB} = 58 \text{ MB/s}$$
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability -- Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产约束与深度解析 (Production Constraints & Deep Dive)

### 具体规模数字 (Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 5000 万 |
| 商家总数 | 2 亿 |
| 日均搜索量 | 2.5 亿次 |
| 峰值搜索 QPS | ~5,800 |
| 商家详情 QPS | ~11,600 |
| 商家信息更新 QPS | < 100 (极低频) |
| Business DB 总量 | ~200 GB |
| 评价 DB 总量 | ~5 TB |
| Redis 缓存 | ~2 GB (热门区域) |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **Search Service** | 附近搜索不可用 | 多实例无状态部署 (10+ 实例) + LB 健康检查 |
| **Business DB (MySQL)** | 商家数据不可读写 | 主从复制 + MHA 自动 failover；从库用于搜索读取 |
| **Redis Cache** | 搜索延迟飙升（回源 DB） | Redis Cluster (6 节点 3 主 3 从) + 本地 L1 缓存 |
| **Geo Index** | 无法执行空间查询 | Geohash 索引与 Business DB 共存，DB 可用即可查询 |
| **Review Service** | 评价功能不可用 | 与搜索服务解耦，评价不可用时搜索仍正常（降级显示"评价加载中"） |

### 读密集型优化策略

**问题**: 读写比 99:1，5800 QPS 搜索 vs < 100 QPS 更新。

**多级缓存架构**:

```
Client
  |
  v
CDN (静态资源: 商家照片、图标)
  |
  v
API Gateway (限流 + 路由)
  |
  v
L1: 本地缓存 (Caffeine, TTL 30s)
  |  miss
  v
L2: Redis Cluster (TTL 5min)
  |  miss
  v
L3: MySQL Replica (Geohash 索引查询)
```

- **L1 本地缓存 (Caffeine / Guava Cache)**：每个 Search Service 实例本地缓存热门
  Geohash 区域的搜索结果。TTL 30 秒，减少 Redis 网络 RTT。命中率约 40-60%。
- **L2 Redis Cluster**：分布式缓存，所有实例共享。TTL 5 分钟。命中率约 80-90%。
- **L3 MySQL Replica**：最终回源。搜索走从库，减轻主库压力。

**预计缓存效果**: L1 + L2 命中率 > 95%，实际打到 DB 的 QPS < 300。

### 索引构建与更新

**方案: 增量更新 + 定时全量重建**

1. **实时增量更新**: 商家信息更新时，通过 **消息队列 (Kafka)** 异步通知
   Search Service 更新 Redis 中对应 Geohash cell 的索引
2. **定时全量重建**: 每天凌晨低峰时段，从 Business DB 全量导出商家数据，
   重新计算 Geohash 索引，写入 Redis。作为增量更新的兜底机制，修复可能的不一致

```
Business DB (写) -> Kafka -> Search Indexer -> Redis (Geohash Index)
                                    |
                                    v
                              Cache Invalidation (对应 cell 的缓存清除)
```

### 多区域部署 (Multi-Region Deployment)

**方案: 按地理区域分片 + 就近路由**

- 用户请求通过 **GeoDNS** 路由到最近的数据中心
- 每个区域（美洲、欧洲、亚太）部署完整服务栈
- 商家数据按国家/城市分区，存储在对应区域的 DB 中
- 跨区域搜索（极少数场景，如旅行搜索）通过跨区域 API 调用实现

**数据同步策略**:

| 数据类型 | 同步方式 | 延迟 |
|----------|----------|------|
| 商家基础信息 | 异步复制 (Kafka cross-region) | < 5 min |
| 评价数据 | 异步复制 | < 10 min |
| 用户账户 | 强一致 (Raft-based) | < 1s |

### 监控与告警 (Monitoring & Alerting)

| 指标 | 告警阈值 | 含义 |
|------|----------|------|
| 搜索 P99 延迟 | > 500ms | Search Service 性能下降或缓存失效 |
| 缓存命中率 | < 80% | 缓存容量不足或 TTL 设置不合理 |
| DB 从库延迟 | > 5s | 主从复制延迟，搜索结果可能过期 |
| Geohash 索引覆盖率 | < 98% | 增量更新丢失数据 |
| 搜索空结果率 | > 10% | 索引异常或数据问题 |
| API 5xx 错误率 | > 0.1% | 服务异常 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|------------------|
| **空间索引** | Geohash (一维编码 + B-Tree) | QuadTree (内存树结构) | **Geohash** -- 2 亿商家需要持久化存储和 DB 索引。Geohash 可直接利用 MySQL B-Tree 索引做前缀查询，不需要额外的内存索引服务。QuadTree 更适合实时更新频繁的场景（如司机位置）。 |
| **搜索引擎** | 自建 Geohash + MySQL | Elasticsearch (倒排 + Geo) | **自建 Geohash** -- 附近搜索的查询模式简单（半径范围 + 过滤），Geohash + MySQL 索引足够高效。ES 适合全文搜索 + 复杂过滤，但运维成本高，对于纯 Geo 查询是杀鸡用牛刀。 |
| **缓存层级** | 单层 Redis 缓存 | L1 本地 + L2 Redis 多级缓存 | **多级缓存** -- L1 本地缓存消除网络 RTT（0.5ms vs 2ms），40-60% 命中率意味着过半请求不需要访问 Redis。每实例额外内存 < 200MB，代价很小。 |
| **商家更新同步** | 同步更新索引 | 异步更新 (Kafka) + 定时全量 | **异步 + 定时** -- 商家更新频率极低 (< 100 QPS)，1-5 分钟延迟可接受。异步解耦使写入不阻塞主流程，定时全量重建作为一致性兜底。 |
| **数据库选型** | MySQL (关系型) | MongoDB (文档型) | **MySQL** -- 商家数据结构稳定，评价数据需要聚合查询（AVG rating, COUNT reviews），关系型 DB 更适合。MongoDB 的 Geo 查询虽然方便，但大规模聚合查询性能不如 MySQL。 |
| **搜索结果排序** | 纯距离排序 | 综合评分 (距离 + 评分 + 热度) | **综合评分** -- 纯距离排序可能把低质量商家排在前面。加权公式兼顾距离和质量。 |

### 一致性 vs 可用性 (Consistency vs Availability)

**最终一致性设计** (整体偏 AP):

- **搜索结果**: 新商家入驻后 1-5 分钟内可搜到（Kafka 异步索引延迟）。用户可以
  接受轻微延迟 -- 不会因为搜不到一家刚注册 1 分钟的新餐厅而投诉。
- **评分聚合**: 新评价提交后 rating 异步重新计算，P99 在 30 秒内生效。
  用户不会注意到"我刚打了 5 星但平均分没立刻变"的延迟。
- **缓存一致性**: 缓存 TTL 5 分钟意味着最坏情况下用户看到 5 分钟前的数据。
  对于商家信息（营业时间、电话等变更频率极低）完全可接受。

**需要强一致性的地方**:

- **商家主编辑**: 商家主更新自己的信息后，立即刷新应看到最新值。
  解决方案: 写入后 invalidate 缓存，下次读取从主库获取。
- **评价去重**: 一个用户对同一商家不能提交两条评价。
  解决方案: DB 唯一约束 `(user_id, business_id)` + 应用层校验。

### 成本 vs 性能 (Cost vs Performance)

| 组件 | 高性能方案 | 低成本替代 | 性能差距 |
|------|-----------|-----------|----------|
| 空间索引 | Redis Geospatial (内存) | MySQL Geohash (磁盘) | 延迟: 0.5ms vs 5ms |
| 全文搜索 | Elasticsearch | MySQL LIKE + Geohash | 搜索能力: 强大 vs 有限 |
| 缓存 | Redis Cluster 6 节点 | 单节点 Redis + 本地缓存 | 可用性: 高 vs 中 |
| CDN | 全球 CDN (CloudFront) | 自建边缘缓存 | 覆盖范围: 全球 vs 区域 |

### 10 倍 / 100 倍规模变化 (What Changes at 10x / 100x Scale)

**当前规模 (1x): 2 亿商家，5000 万 DAU，5800 QPS**

**10x (20 亿商家，5 亿 DAU，58K QPS)**:
- MySQL 按 Geohash 前缀分库分表（每个分片 < 5 亿行）
- Redis Cluster 扩展到 20+ 节点，按区域分片
- 引入 **Elasticsearch** 支持复杂搜索（自然语言查询、模糊匹配）
- Search Service 100+ 实例，引入服务网格 (Istio) 管理流量
- 评价数据迁移到 **分布式 NoSQL** (Cassandra / DynamoDB)

**100x (200 亿 POI，50 亿 DAU，580K QPS)**:
- 从 Geohash 迁移到 **S2 Geometry** (Google) 或 **H3** (Uber)，
  更好的均匀分区和多分辨率查询
- 自建分布式空间索引引擎，替代 MySQL + Redis 方案
- 引入 **ML 排序模型**: 基于用户画像、上下文（时间、天气、历史偏好）
  个性化排序搜索结果
- 预计算 + 实时混合: 对热门区域预计算搜索结果存入边缘节点，
  长尾区域实时查询
- 评价存入 **数据湖** (S3 + Parquet) 供离线分析和推荐模型训练
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

**Q: Geohash 的边界问题怎么解决？两个物理上很近的商家可能在不同的 Geohash cell
里，搜索时会不会漏掉？**

> **承认局限**: 这是 Geohash 最知名的缺陷。相邻 cell 的 Geohash 编码可能完全
> 不同（如经度 180 度跳变），导致前缀匹配无法覆盖所有邻近区域。
>
> **缓解措施**:
>
> 1. **查询 9 个 cell**: 不仅查中心 cell，还查周围 8 个邻居 cell。标准库
>    (如 `geohash2.neighbors()`) 可直接获取邻居列表。这确保搜索半径内的商家
>    不会因为落在相邻 cell 而被遗漏。
> 2. **精确距离过滤**: 从 9 个 cell 获取候选商家后，用 Haversine 公式计算
>    每个商家到用户的精确距离，丢弃超出搜索半径的结果。Geohash 只负责粗筛，
>    精确距离保证最终结果正确。
> 3. **精度选择**: 搜索半径越大，Geohash 精度越低（cell 越大），边界效应的
>    影响越小。根据 radius 动态选择 Geohash 精度。
>
> **数据**: 9-cell 查询 + Haversine 精确过滤的方案可以保证 0 漏检率，
> 代价是多查 8 个邻居 cell（每个 cell 的 DB 查询可并行执行）。

---

**Q: 如果曼哈顿市中心一个 Geohash cell 里有 5000 家商家，但郊区一个 cell
只有 3 家，怎么处理这种密度不均的问题？**

> **承认局限**: Geohash 是固定精度划分，不会根据密度自适应细分，导致城市核心区域
> 单个 cell 内商家过多，查询结果集大，排序和过滤开销高。
>
> **缓解措施**:
>
> 1. **多精度索引**: 同时维护 Geohash-5 和 Geohash-6 两个精度的索引。
>    低密度区域查 Geohash-5（大 cell），高密度区域查 Geohash-6（小 cell）。
>    根据 cell 内商家数动态选择精度。
> 2. **分页 + 预过滤**: 数据库查询时用 `WHERE geohash LIKE 'prefix%'` +
>    `AND category = ? AND rating >= ?` 在 DB 层过滤，减少返回结果集大小。
>    配合 `LIMIT 50` 分页，避免一次性加载 5000 条记录。
> 3. **热门区域预计算**: 对已知的高密度区域（市中心、商业区），预计算并缓存
>    各类别的 Top-50 商家。搜索时直接从缓存读取，不走 DB。
> 4. **考虑 QuadTree 混合**: 对极端高密度区域，在内存中维护 QuadTree 索引，
>    提供比 Geohash 更好的密度自适应查询。
>
> **数据**: 多精度索引 + 预计算方案可将高密度区域的 P99 查询延迟从 150ms
> 降低到 30ms。

---

**Q: 搜索结果中显示"距离你 500 米"，但用户走过去发现实际要走 1.2 公里
（因为要绕路），怎么办？**

> **承认局限**: Haversine 公式计算的是**直线距离 (as the crow flies)**，不是
> **步行/驾车距离 (walking/driving distance)**。城市环境中实际步行距离通常是
> 直线距离的 1.2-1.6 倍。
>
> **缓解措施**:
>
> 1. **显示标注**: UI 上明确标注"直线距离 500m"，而非暗示可达距离。
>    Google Maps 的做法是"500m away"不保证步行距离。
> 2. **路网距离 API**: 对搜索结果 Top-20 调用路径规划 API（Google Directions
>    / OSRM），获取实际步行/驾车距离和时间。但这会增加延迟（每次调用 50-100ms）
>    和成本（API 调用费）。
> 3. **经验系数**: 对直线距离乘以一个 **routing factor**
>    ($\approx 1.3$-$1.5$)，得到更接近实际的预估距离。不同城市、不同区域
>    （网格街道 vs 弯曲道路）的系数不同，可以用历史数据训练。
> 4. **混合策略**: 粗排用直线距离（快速），精排对 Top-10 用路网距离（准确）。
>    这样只对最终展示的结果做精确计算，平衡延迟和准确性。
>
> **数据**: routing factor 1.4 在网格型城市（曼哈顿）的误差 < 15%，
> 在弯曲道路城市误差可达 30%，此时需要真实路网距离。

---

**Q: 如果 Redis 缓存全部失效了（冷启动或 Redis 故障恢复后），所有搜索请求
直接打到 MySQL，DB 能扛住吗？**

> **承认局限**: 缓存雪崩 (**Cache Avalanche**) 是缓存架构的经典风险。
> 5800 QPS 全部回源到 MySQL，数据库可能直接被打挂。
>
> **缓解措施**:
>
> 1. **L1 本地缓存兜底**: 即使 Redis 全挂，每个 Search Service 实例的本地
>    缓存 (Caffeine) 仍然可用。L1 命中率 40-60%，可将打到 DB 的 QPS
>    降低到 2000-3500。
> 2. **请求限流 (Rate Limiting)**：对 DB 层设置限流器，最多允许 1000 QPS
>    回源查询。超出的请求返回降级结果（如展示上次缓存的结果或"搜索繁忙请稍后"）。
> 3. **缓存预热 (Cache Warming)**：Redis 恢复后，不等用户请求触发回填，
>    而是主动从 DB 批量加载热门区域数据预热缓存。预热脚本可在 5-10 分钟内
>    恢复 80% 的缓存数据。
> 4. **TTL 随机化 (Jitter)**：缓存 TTL 不设固定值（如 5 分钟），而是
>    `5min + random(0, 60s)`，避免大量 key 同时过期导致瞬间缓存穿透。
> 5. **互斥锁防击穿 (Mutex Lock)**：同一个 Geohash cell 只允许一个请求
>    回源 DB，其他请求等待或返回过期数据 (stale-while-revalidate)。
>
> **数据**: L1 兜底 + 限流 + 预热可将 Redis 故障恢复时间从 30 分钟缩短到 5 分钟，
> 期间搜索可用性维持 > 90%。

---

**Q: 你的设计如何处理"用户正在移动"的场景？比如用户坐在公交车上搜索附近餐厅，
位置在不断变化。**

> **承认局限**: 当前设计假设用户位置在单次搜索中是静态的。如果用户快速移动，
> 搜索结果可能在用户到达时已经不再"附近"。
>
> **缓解措施**:
>
> 1. **客户端节流 (Debounce)**：不在用户每次位置变化时都发搜索请求。
>    只有当位置变化超过阈值（如 200m 或 30 秒内无新位置）时才触发新搜索。
> 2. **扩大搜索半径**: 检测到用户在移动时（通过连续位置的速度判断），
>    自动将搜索半径扩大到 `radius + speed x 5min`，预加载前方区域的商家。
> 3. **缓存复用**: 如果用户新位置仍在同一个 Geohash cell 内，直接复用
>    上次的搜索结果，无需重新查询。Geohash-6 的 cell 约 1.2km 宽，步行
>    速度下可以复用较长时间。
> 4. **方向感知**: 如果用户在移动，优先展示移动方向前方的商家（结合
>    heading 信息），而非身后已经路过的商家。
>
> **数据**: 位置变化 debounce + Geohash cell 内复用可减少 70% 的重复搜索请求，
> 在移动场景下既节省服务器资源又保证结果相关性。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "附近搜索服务的核心是让用户根据当前位置快速找到附近的商家。
> 我想先确认几点: 搜索半径最大是多少？是否需要支持'正在营业'过滤？
> 商家信息的更新频率大概是什么量级？是否需要个性化排序？
> 我假设 2 亿商家，5000 万 DAU，搜索默认半径 5km。"
>
> 列出 FR: 附近搜索、商家详情、商家 CRUD、搜索过滤、评价系统。
> 列出 NFR: 99.99% 可用性、搜索 P99 < 200ms、峰值 ~5800 搜索 QPS。
> 明确 Out of Scope: 社交功能、广告竞价、预约点餐、照片 CDN。
> 关键特征: **读密集型系统 (read-heavy)，读写比 99:1**。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "这是一个典型的读密集型系统，读写比约 99:1。核心组件:
> Search Service (LBS) 负责附近搜索 + Business Service 负责商家 CRUD +
> Review Service 负责评价管理。
> 空间索引用 **Geohash** -- 将二维坐标编码为一维字符串，利用 MySQL B-Tree
> 索引做前缀查询。缓存用 **多级架构**: L1 本地缓存 (Caffeine, 30s TTL) +
> L2 Redis Cluster (5min TTL) + L3 MySQL Replica。
> 商家更新通过 Kafka 异步通知 Search Service 更新索引和缓存。"
>
> "搜索流程: 用户 (lat, lng, radius) -> 计算 Geohash 前缀 -> 查 9 个 cell
> (中心 + 8 邻居) -> L1/L2 缓存查询 -> DB 回源 -> Haversine 精确距离
> -> 排序过滤 -> 返回 Top-20。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: Geohash 索引与搜索算法 (8-10 分钟)**
> "Geohash 将经纬度交替二分编码为 Base32 字符串。精度 6 对应约 1.2km x 0.6km
> 的 cell。搜索时根据半径选择合适的 Geohash 精度: 5km 用精度 6，20km 用精度 5。
> 边界问题: 查询中心 cell + 8 个邻居 cell = 9 个 cell，避免遗漏跨 cell 边界
> 的商家。Geohash 做粗筛，Haversine 精确距离做精排。
> 替代方案: QuadTree 密度自适应但需要内存，不适合 2 亿商家的持久化索引;
> R-Tree 查询强但更新代价高。Geohash + B-Tree 是最佳平衡。"

**重点 2: 多级缓存与读优化 (8-10 分钟)**
> "读写比 99:1，缓存是性能关键。L1 本地缓存 (Caffeine): 每实例 200MB，
> TTL 30s，命中率 40-60%，消除 Redis 网络 RTT。L2 Redis Cluster:
> 6 节点 3 主 3 从，TTL 5min，命中率 80-90%。最终打到 DB 的 QPS < 300。
> 缓存 key 设计: `search:{geohash6}:{category}:{sort}`。
> 失效策略: 商家更新时通过 Kafka 异步 invalidate 对应 cell 的缓存。
> 防雪崩: TTL 加 jitter，互斥锁防穿透，预热脚本快速恢复。"

**重点 3: 容量估算 (5-8 分钟)**
> "5000 万 DAU，日均 5 次搜索 = 2.5 亿次/天。峰值 QPS ~5800。
> 2 亿商家 x 1KB = 200GB 存储。评价 100 亿条 x 0.5KB = 5TB。
> 缓存: 20% 热门区域 x 50 商家/cell x 200 bytes = 2GB Redis。
> 带宽: 5800 QPS x 10KB = 58 MB/s，常规服务器可承受。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: Geohash vs QuadTree (持久化 vs 自适应密度)，
> 自建 Geohash+MySQL vs Elasticsearch (简洁 vs 全文搜索能力)，
> 多级缓存 vs 单层缓存 (复杂度 vs 延迟)。
> 10x 规模: MySQL 按 Geohash 分库分表，引入 ES 支持复杂查询，
> 评价迁移到 Cassandra。100x: 迁移到 S2/H3 空间索引，
> 自建分布式空间引擎，ML 个性化排序。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 个性化排序 -- 基于用户历史偏好和
> 上下文(时间/天气/场景)的 ML 排序模型，(2) 商家搜索 SEO -- 全文搜索
> + 自然语言查询支持，(3) 实时热度 -- 基于当前客流量的动态热度排序。"

### 55-60 分钟: 向面试官提问

> "你们的空间索引用的是 Geohash、QuadTree 还是 S2/H3？迁移过程中
> 遇到了什么挑战？搜索排序模型有引入 ML 吗？缓存架构是几层的？
> 高密度城市区域有什么特殊处理？"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计附近搜索服务 -- 2 亿商家，5000 万 DAU，
   读写比 99:1，搜索 P99 < 200ms。

2. **(60 秒) 架构**: Search Service + Geohash 空间索引。经纬度编码为
   Geohash 字符串，利用 MySQL B-Tree 前缀查询。搜索时查中心 + 8 邻居
   共 9 个 cell，Haversine 精排。多级缓存: L1 本地 (Caffeine, 30s)
   + L2 Redis Cluster (5min)，L1+L2 命中率 > 95%。商家更新通过
   Kafka 异步通知索引和缓存。

3. **(60 秒) 关键设计**: Geohash 精度根据搜索半径动态选择 (4-7 位)。
   边界问题用 9-cell 查询解决。高密度区域多精度索引 + 预计算 Top-50。
   缓存防雪崩: TTL jitter + 互斥锁 + 预热脚本。排序公式综合距离 + 评分
   + 热度。

4. **(30 秒) 扩展**: 10x 分库分表 + Elasticsearch。100x 迁移到 S2/H3
   空间索引 + 自建空间引擎 + ML 排序。按地理区域分片 + GeoDNS 就近路由。
"""


def populate_interview_proximity_service() -> None:
    """Create or update the interview-proximity-service record with all 8 sections."""
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
    populate_interview_proximity_service()
