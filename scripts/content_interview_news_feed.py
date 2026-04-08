"""Populate interview-news-feed system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a News Feed
(Instagram/Facebook). Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-news-feed"
TITLE = "Design a News Feed (Instagram)"
DISPLAY_ORDER = 106

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **Instagram / Facebook** 的**信息流系统 (News Feed System)**。
用户可以发布图文内容 (Post)，系统需要为每位用户生成一个个性化的、按相关性
排序的动态首页 (Home Feed)，展示其关注的人和推荐内容。系统需要支持数亿级
用户和每秒数十万次 Feed 请求。

### 功能性需求 (Functional Requirements)

1. **发布内容 (Publish Post)**：用户可以发布文字、图片、视频内容，内容被
   持久化存储并分发给粉丝
2. **获取信息流 (Get Feed)**：用户打开首页时获取个性化排序的内容流，包含
   关注者的最新帖子以及系统推荐内容
3. **实时更新 (Real-time Update)**：当关注的人发布新内容时，用户的 Feed
   应在合理时间内更新（不要求严格实时，但需要"新鲜感"）
4. **排序与个性化 (Ranking & Personalization)**：Feed 不是简单的时间倒序，
   而是根据用户兴趣、帖子质量、社交亲密度等因素综合排序
5. **分页加载 (Pagination)**：支持下拉刷新 (Pull-to-refresh) 和无限滚动
   (Infinite Scroll) 两种分页模式

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（Feed 是核心用户体验，不可用 = 用户流失）
- **延迟 (Latency)**：Feed 获取 P99 < 500ms（包含排序和个性化）；发帖
  P99 < 200ms（写入确认）
- **吞吐量 (Throughput)**：峰值 Feed 读取 QPS ~300,000；发帖写入
  QPS ~5,000
- **一致性 (Consistency)**：最终一致。用户发帖后自己立即可见 (Read-your-own-writes)，
  粉丝在几秒到几分钟内看到
- **可扩展性 (Scalability)**：支撑 5 亿注册用户、2 亿 DAU

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 用户的平均关注数量是多少？是否有"名人"用户？** -- WHY: 关注数决定了
   **Fan-out (扇出)** 策略。如果平均关注 200 人，Fan-out on Write 可行；
   如果有粉丝数 > 1000 万的名人，Fan-out on Write 对名人不可行，需要混合策略。

2. **Q: Feed 是纯时间倒序还是需要排序/推荐？** -- WHY: 纯时间序只需要
   归并排序，复杂度低；如果需要推荐排序则需引入 ML 排序模型，架构上需要
   一个独立的 **Ranking Service (排序服务)**。

3. **Q: 内容类型有哪些？是否包含视频？** -- WHY: 视频涉及转码、CDN 分发、
   自适应码率 (**ABR, Adaptive Bitrate**) 等额外复杂度，影响存储和带宽估算。

4. **Q: 是否需要支持"发现/探索"页面 (Explore Feed)？** -- WHY: Explore Feed
   是推荐系统驱动的，不依赖关注关系，需要完全不同的数据源和排序逻辑。
   如果包含在范围内会显著增加系统复杂度。

5. **Q: 用户发帖后多久需要在粉丝 Feed 中出现？** -- WHY: 如果要求 < 1 秒
   "实时"，需要 push-based 架构 + WebSocket；如果容忍 10-30 秒延迟，
   可以用更高效的批量处理。

6. **Q: 是否需要支持"关闭推荐"只看关注？** -- WHY: 这决定了是否需要维护两套
   Feed 生成逻辑（纯关注 vs. 混合推荐），影响缓存策略和 Feed 组装服务的设计。

7. **Q: Feed 中是否需要展示广告？** -- WHY: 广告插入影响 Feed 组装逻辑，
   需要一个独立的 **Ad Insertion Service (广告插入服务)**，且需要考虑广告
   与有机内容的混排策略。

### 范围声明 (Out of Scope)

- 评论 / 点赞 / 转发系统（假设已有独立服务）
- 用户注册 / 登录 / 社交图谱管理
- 内容审核 / 违规检测
- 消息推送通知 (Push Notification)
- 具体的 ML 模型训练流程（只讨论推理接口）
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

信息流系统分为**写路径 (Write Path)** 和**读路径 (Read Path)** 两条核心链路，
加上**排序服务 (Ranking Service)** 作为智能层。

### 核心服务与职责

| 服务 | 职责 |
|------|------|
| **Post Service (帖子服务)** | 接收用户发帖请求，存储帖子元数据到 PostDB，将媒体上传至 Object Storage，发送事件到 Fan-out Queue |
| **Fan-out Service (扇出服务)** | 消费发帖事件，将帖子 ID 写入粉丝的 Feed 缓存 (Fan-out on Write)，对名人帖子做标记不扇出 |
| **Feed Service (信息流服务)** | 处理 Feed 请求：从缓存获取 Fan-out 结果 + 拉取名人帖子 (Fan-out on Read)，合并后送排序 |
| **Ranking Service (排序服务)** | 对候选帖子集合进行个性化排序（ML 模型推理），返回排序后的帖子 ID 列表 |
| **Social Graph Service (社交图谱服务)** | 维护关注/粉丝关系，提供 "用户 X 关注了谁" 和 "用户 X 的粉丝列表" 查询 |
| **Media Service (媒体服务)** | 图片/视频上传、转码、缩略图生成，通过 CDN 分发 |
| **Cache Layer (缓存层)** | Redis 集群：存储 Feed 缓存、帖子缓存、用户画像缓存 |

### 数据库选型与理由

| 数据 | 存储选型 | 理由 |
|------|----------|------|
| 帖子元数据 (PostDB) | **MySQL** (分库分表) | 结构化数据、需要事务、按 user_id 分片 |
| 社交关系 (Social Graph) | **MySQL** 或 **Graph DB (TAO)** | Facebook 用 TAO (MySQL 之上的图缓存)，关注关系是典型的图结构 |
| Feed 缓存 | **Redis** (List / Sorted Set) | 高吞吐低延迟，Feed 是热数据，天然适合内存缓存 |
| 媒体文件 | **S3 / Object Storage** + **CDN** | 大文件存储 + 全球分发 |
| 用户画像/特征 | **Redis** + **Cassandra** | Redis 放热特征用于实时排序，Cassandra 放完整画像 |

### 通信模式

- **同步 REST/gRPC**：客户端 -> Feed Service（获取 Feed）、客户端 -> Post Service（发帖）
- **异步消息队列 (Kafka)**：Post Service -> Fan-out Service（发帖事件）、
  Fan-out Service -> Feed Cache（批量写入）
- **WebSocket**（可选）：Feed Service -> 客户端（实时新帖通知，"有 N 条新内容"）

### Fan-out 策略：核心架构决策

这是 News Feed 系统设计面试中**最核心的讨论点**。

#### Fan-out on Write (Push Model)

用户发帖时，系统立即将帖子 ID 推送到**每个粉丝**的 Feed 缓存中。

```
User A publishes post P1
  -> Fan-out Service reads A's follower list: [B, C, D, ...]
  -> For each follower, LPUSH post_id to their feed cache
  -> B opens app -> read from cache -> instant feed
```

**优点**：读取极快（预计算好的），Feed 获取 = 一次 Redis 读取。
**缺点**：名人发帖时 Fan-out 代价巨大（1000 万粉丝 = 1000 万次写入）。

#### Fan-out on Read (Pull Model)

用户请求 Feed 时，系统实时拉取其关注的所有人的最新帖子，合并排序后返回。

```
User B requests feed
  -> Feed Service reads B's following list: [A, C, E, ...]
  -> For each following, fetch their recent posts
  -> Merge + sort + return top N
```

**优点**：发帖零延迟，无写放大。
**缺点**：读取慢（如果关注 500 人，需要 500 次查询 + 合并）。

#### Hybrid Model (混合模型) -- 我们的选择

- **普通用户** (粉丝 < 10,000)：Fan-out on Write，发帖时推送到粉丝缓存
- **名人用户** (粉丝 >= 10,000)：**不做 Fan-out**，在读取时实时拉取
- Feed 获取时：读缓存（普通关注者的帖子）+ 拉取名人帖子 -> 合并 -> 排序

**名人阈值 (Celebrity Threshold)** 是可调参数，通常设为 10,000 - 100,000。
Facebook 实际使用约 **5,000** 作为阈值。

### 数据分区策略

- **PostDB**：按 `user_id` 分片 (Range/Hash)，同一用户的帖子在同一分片
- **Feed Cache (Redis)**：按 `user_id` 一致性哈希 (Consistent Hashing) 分片
- **Social Graph**：按 `user_id` 分片，关注关系以邻接表形式存储
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 端点

#### 1. 发布帖子

```
POST /v1/posts
Authorization: Bearer <token>

Request Body:
{
  "content": "Beautiful sunset at the beach!",
  "media_ids": ["img_abc123", "img_def456"],
  "location": {"lat": 34.0195, "lng": -118.4912},
  "tags": ["sunset", "beach"]
}

Response: 201 Created
{
  "post_id": "post_7821934",
  "created_at": "2024-01-15T18:30:00Z",
  "status": "published"
}
```

#### 2. 获取信息流

```
GET /v1/feed?cursor=<cursor>&limit=20
Authorization: Bearer <token>

Response: 200 OK
{
  "posts": [
    {
      "post_id": "post_7821934",
      "author": {"user_id": "u_123", "username": "alice", "avatar_url": "..."},
      "content": "Beautiful sunset...",
      "media": [{"url": "https://cdn.example.com/img_abc123.jpg", "type": "image"}],
      "metrics": {"likes": 1523, "comments": 87},
      "created_at": "2024-01-15T18:30:00Z",
      "ranking_score": 0.92
    }
  ],
  "next_cursor": "eyJsYXN0X3Njb3JlIjowLjg1fQ==",
  "has_more": true
}
```

#### 3. 刷新 Feed（下拉刷新）

```
GET /v1/feed/refresh?since=<timestamp>
Authorization: Bearer <token>

Response: 200 OK
{
  "new_count": 12,
  "posts": [...]
}
```

### 核心数据模型

**Post Table** (MySQL, 按 user_id 分片):

| 字段 | 类型 | 说明 |
|------|------|------|
| post_id | BIGINT (Snowflake ID) | 全局唯一，包含时间戳，天然有序 |
| user_id | BIGINT | 发帖人，分片键 |
| content | TEXT | 文字内容 |
| media_urls | JSON | 媒体文件 CDN 地址列表 |
| location | POINT | 地理位置（可选） |
| created_at | DATETIME | 发布时间 |
| status | ENUM | published / deleted / hidden |

**Social Graph Table** (MySQL, 按 follower_id 分片):

| 字段 | 类型 | 说明 |
|------|------|------|
| follower_id | BIGINT | 关注者 |
| followee_id | BIGINT | 被关注者 |
| created_at | DATETIME | 关注时间 |

**Feed Cache** (Redis Sorted Set, key = `feed:{user_id}`):

- Member: `post_id` (字符串)
- Score: 发布时间戳 (Unix timestamp) 或排序分数

### 写路径：用户发帖 (Write Path)

```
1. Client -> API Gateway -> Post Service
2. Post Service:
   a. 生成 Snowflake ID
   b. 写入 PostDB (MySQL)
   c. 如果有媒体: 异步通知 Media Service 处理（转码/缩略图）
   d. 发布事件到 Kafka topic: "post.published"
   e. 返回 201 给客户端（不等待 Fan-out 完成）

3. Fan-out Service (Kafka Consumer):
   a. 消费 "post.published" 事件
   b. 查询 Social Graph: 获取发帖人的粉丝列表
   c. 检查发帖人是否为名人 (follower_count >= 10,000)
      - 如果是名人: 跳过 Fan-out，仅标记到 celebrity_posts 集合
      - 如果不是: 对每个粉丝，执行 Redis ZADD feed:{follower_id} <timestamp> <post_id>
   d. 限制每个用户的 Feed 缓存大小 (ZREMRANGEBYRANK, 保留最近 500 条)

4. 发帖人自己的 Feed: 立即可见 (Write-through to own cache)
```

### 读路径：获取 Feed (Read Path)

```
1. Client -> API Gateway -> Feed Service
2. Feed Service:
   a. 从 Redis 读取 feed:{user_id} (Sorted Set, ZREVRANGE)
      -> 得到普通关注者的帖子 ID 列表 (已由 Fan-out 预填充)
   b. 获取用户关注的名人列表 (Social Graph Service)
   c. 对每个名人，从 celebrity_posts:{celebrity_id} 拉取最近帖子
   d. 合并两个列表 -> 去重 -> 得到候选集 (约 200-500 条)

3. Ranking Service:
   a. 接收候选帖子 ID 列表 + 用户特征
   b. 批量获取帖子特征 (Redis 帖子缓存)
   c. 运行 ML 排序模型 (特征: 作者亲密度, 帖子年龄, 互动率, 内容类型...)
   d. 返回排序后的帖子 ID 列表 + 排序分数

4. Feed Service:
   a. 按排序结果取 top-N (分页大小, 通常 20)
   b. 批量获取帖子详情 (Post Cache -> PostDB fallback)
   c. 组装响应 (hydrate with author info, media URLs, metrics)
   d. 生成 cursor (基于排序分数或位置偏移)
   e. 返回给客户端
```

### 异步路径

- **媒体处理**：Post Service -> Kafka "media.process" -> Media Service
  (转码/缩略图) -> 更新 PostDB 中的 media_urls
- **指标聚合**：用户互动 (点赞/评论) -> Kafka "engagement" -> Metrics Service
  -> 更新帖子的 engagement_score (用于排序)
- **Feed 预热**：用户上线通知 -> 预先为即将活跃的用户刷新 Feed 缓存
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 基础数据假设

| 指标 | 数值 |
|------|------|
| 注册用户 | 5 亿 |
| DAU | 2 亿 |
| 平均关注数 | 200 人 |
| 日均发帖用户比例 | 5%（1000 万用户发帖） |
| 每人日均发帖 | 2 条 |
| 日均新帖总量 | 2000 万条 |
| 平均每条帖子大小 | 1 KB（元数据） + 500 KB（媒体均值） |
| Feed 请求：每 DAU 日均 | 10 次 |

### QPS 估算

**写入 QPS (发帖)**:

$$Q_{write} = \frac{20{,}000{,}000}{86{,}400} \approx 230 \text{ QPS (avg)}$$

$$Q_{write\_peak} = 230 \times 3 \approx 700 \text{ QPS (peak, 3x multiplier)}$$

**读取 QPS (Feed 请求)**:

$$Q_{read} = \frac{200{,}000{,}000 \times 10}{86{,}400} \approx 23{,}000 \text{ QPS (avg)}$$

$$Q_{read\_peak} = 23{,}000 \times 5 \approx 115{,}000 \text{ QPS (peak)}$$

**Fan-out 写入 QPS**:

每条帖子平均 Fan-out 给 200 个粉丝（排除名人）:

$$Q_{fanout} = 230 \times 200 = 46{,}000 \text{ Redis writes/sec (avg)}$$

$$Q_{fanout\_peak} = 700 \times 200 = 140{,}000 \text{ Redis writes/sec (peak)}$$

### 存储估算

**帖子元数据 (MySQL)**:

$$S_{posts} = 20{,}000{,}000 \text{ posts/day} \times 1 \text{ KB} \times 365 \text{ days} = 7.3 \text{ TB/year}$$

**媒体存储 (S3)**:

$$S_{media} = 20{,}000{,}000 \times 500 \text{ KB} \times 365 = 3.65 \text{ PB/year}$$

（实际中: 80% 图片经压缩后约 200 KB，20% 视频约 5 MB）

**Feed 缓存 (Redis)**:

每个活跃用户缓存 500 条帖子 ID（每条 8 bytes + Sorted Set 开销约 16 bytes）:

$$S_{feed\_cache} = 200{,}000{,}000 \times 500 \times 24 \text{ bytes} = 2.4 \text{ TB}$$

实际只缓存最近活跃用户（30 天内活跃约 3 亿），非活跃用户 Feed 在请求时重建:

$$S_{feed\_active} = 300{,}000{,}000 \times 500 \times 24 = 3.6 \text{ TB Redis}$$

### 带宽估算

**Feed 读取出站带宽**:

每次 Feed 请求返回 20 条帖子，每条约 2 KB（元数据 + 缩略图 URL，不含实际图片）:

$$BW_{feed} = 115{,}000 \times 20 \times 2 \text{ KB} = 4.6 \text{ GB/s (peak, metadata only)}$$

媒体文件通过 CDN 分发，不经过 Feed Service。

### 核心算法：Feed 排序模型

**EdgeRank (Facebook 早期排序公式)**:

$$\text{Score}(e) = \sum_{e} w_e \times d_e \times a_e$$

其中:
- $w_e$ = **亲密度 (Affinity)**：用户与帖子作者的互动频率
- $d_e$ = **时间衰减 (Decay)**：帖子越旧分数越低，$d_e = e^{-\lambda \cdot \Delta t}$
- $a_e$ = **边权重 (Edge Weight)**：互动类型的权重（评论 > 点赞 > 浏览）

**现代 ML 排序模型 (Multi-objective)**:

$$\text{Score} = w_1 \cdot P(\text{click}) + w_2 \cdot P(\text{like}) + w_3 \cdot P(\text{comment}) + w_4 \cdot P(\text{share}) - w_5 \cdot P(\text{hide})$$

使用 **GBDT (Gradient Boosted Decision Trees)** 或 **DNN (Deep Neural Network)**
预测每个互动概率，加权求和得到最终排序分数。

**典型特征维度**:
- **用户特征**: 年龄、地域、历史兴趣标签、活跃时段
- **帖子特征**: 内容类型、已有互动量、发布时间、作者粉丝数
- **交叉特征**: 用户-作者亲密度、用户-内容类型偏好、上下文时间

### Cursor 分页算法

使用基于排序分数的 **Cursor-based Pagination (游标分页)**，避免 OFFSET 性能问题:

```
cursor = encode(last_item_score, last_item_id)
next_page = items WHERE score < last_score OR (score = last_score AND id < last_id)
            ORDER BY score DESC, id DESC LIMIT page_size
```

优点: O(1) 翻页性能，不受页码深度影响。

### 服务器数量估算

| 组件 | 计算 | 数量 |
|------|------|------|
| Feed Service | 115K QPS / 5K per instance | ~25 实例 |
| Post Service | 700 QPS / 1K per instance | ~2 实例 |
| Fan-out Service | 140K writes/s / 10K per worker | ~15 workers |
| Ranking Service (GPU) | 115K QPS, batch 50, 10ms/batch | ~25 GPU 实例 |
| Redis (Feed Cache) | 3.6 TB / 64 GB per node | ~60 节点 |
| MySQL (PostDB) | 7.3 TB/yr, 16 shards | ~32 实例 (含副本) |

### 月度成本估算

| 项目 | 月度费用 |
|------|----------|
| Redis 60 节点 (r6g.2xlarge) | ~18,000 USD |
| MySQL 32 实例 (r6g.xlarge) | ~8,000 USD |
| GPU (Ranking, g5.xlarge x 25) | ~25,000 USD |
| S3 (3.65 PB 含生命周期) | ~50,000 USD |
| CDN (CloudFront, 高流量) | ~100,000+ USD |
| 计算 (Feed/Post/Fanout) | ~5,000 USD |
| **总计** | **~206,000 USD/月** |

（注意: 这是 Instagram 规模的估算，中小规模可削减 1-2 个数量级）
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints -- Scale & Reliability)

### 具体规模参数

| 指标 | 数值 |
|------|------|
| 注册用户 | 5 亿 |
| DAU | 2 亿 |
| Feed QPS (峰值) | 115,000 |
| Fan-out Redis QPS (峰值) | 140,000 |
| Feed 缓存总量 | 3.6 TB (Redis) |
| 每日新帖 | 2000 万条 |
| 媒体存储年增 | 3.65 PB |

### 单点故障分析 (SPOF Analysis)

| 组件 | 风险 | 缓解措施 |
|------|------|----------|
| Feed Cache (Redis) | 缓存宕机导致 Feed 不可用 | Redis Cluster (3 主 3 从 per shard)，自动故障转移 |
| PostDB (MySQL) | 主库宕机 | 每个分片 1 主 2 从，半同步复制，MHA 自动切换 < 30s |
| Fan-out Service | 消费者宕机 | Kafka Consumer Group 自动重平衡，积压可容忍短暂延迟 |
| Ranking Service | ML 模型推理失败 | 降级策略: 回退到基于时间的简单排序 (chronological fallback) |
| Kafka | Broker 宕机 | 3 副本 + ISR，单 Broker 故障不丢数据 |

### 多数据中心 / 跨区域 (Multi-DC)

**架构: Active-Active (双活)**

- **DNS 层**: **GeoDNS** 将用户路由到最近的数据中心
- **数据复制**: MySQL 跨 DC 异步复制（延迟 < 100ms），Redis 使用
  **CRDT (Conflict-free Replicated Data Type)** 或定期同步
- **写冲突处理**: 帖子写入只路由到用户主 DC (Home DC)，通过 Kafka
  跨 DC 镜像 (**MirrorMaker 2**) 同步到其他 DC
- **Feed 一致性**: 用户的 Feed 缓存在其 Home DC 维护。当用户跨 DC 访问时，
  优先读取 Home DC 缓存（可容忍稍高延迟），或读取本地缓存（可能稍有延迟）

**故障切换 (Failover)**:
- DC 整体故障时，DNS 权重切换到存活 DC（TTL = 30s）
- Feed 缓存在目标 DC 可能冷启动，需要从 PostDB 重建（10-30s）

### 高并发处理

1. **连接池 (Connection Pooling)**：
   - MySQL: 每个 Feed Service 实例维护连接池 (max 50 connections/shard)
   - Redis: Pipelining + 连接池 (max 200 connections/node)

2. **速率限制 (Rate Limiting)**：
   - 发帖: 100 posts/hour/user（防刷）
   - Feed 请求: 600 requests/min/user（正常使用约 10 req/min）
   - Fan-out: 每秒最多处理 500K Redis writes（超出则排队）

3. **熔断器 (Circuit Breaker)**：
   - Ranking Service 延迟 > 200ms -> 熔断，降级到时间排序
   - Social Graph Service 超时 -> 用缓存的关注列表
   - Media Service 故障 -> 返回帖子文字内容，媒体展示占位符

4. **优雅降级 (Graceful Degradation)**：
   - **Level 1**: Ranking Service 降级 -> 时间倒序 Feed
   - **Level 2**: Feed Cache 部分失效 -> 从 PostDB 重建（延迟升高到 2-3s）
   - **Level 3**: 极端负载 -> 返回最近缓存的 Feed 快照（可能不是最新的）

### 监控与告警 (Monitoring & Alerting)

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| Feed P99 延迟 | > 500ms | P1 (Warning) |
| Feed P99 延迟 | > 2s | P0 (Critical) |
| Fan-out Kafka lag | > 100K messages | P1 |
| Redis 内存使用率 | > 80% | P1 |
| Feed Cache 命中率 | < 90% | P2 (Investigation) |
| Ranking Service 错误率 | > 5% | P1 (auto-degrade) |
| PostDB 主从延迟 | > 5s | P1 |

### Celebrity Fan-out 优化

名人发帖是系统的最大流量峰值来源。优化策略:

1. **热点检测 (Hotspot Detection)**：维护"名人列表"缓存（粉丝数 > 10K 的用户），
   Fan-out Service 在处理前检查，名人帖子走 Pull 路径
2. **批量 Fan-out**：非名人的 Fan-out 使用 Redis Pipeline，每批 1000 个
   ZADD 命令打包发送，减少网络往返
3. **优先级 Fan-out**：先推送给最近 7 天活跃的粉丝，其余粉丝延迟推送或
   在他们上线时按需拉取
4. **Fan-out 限流**：单条帖子的 Fan-out 速率限制为 50K writes/s，
   防止一条帖子耗尽 Redis 写入带宽
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **Fan-out 策略** | Fan-out on Write (Push) | Fan-out on Read (Pull) | **混合模型 (Hybrid)**：普通用户 Push，名人 Pull。纯 Push 对名人不可行（1000 万粉丝写放大），纯 Pull 读延迟过高（关注 500 人需 500 次查询）。混合模型在 99% 场景下享受 Push 的低读延迟，仅对 1% 名人内容做 Pull |
| **Feed 缓存存储** | Redis Sorted Set | Redis List | **Sorted Set**：虽然内存开销比 List 大 ~30%，但支持按分数范围查询、去重、以及排序后插入，适配排序模型的输出。List 只能 LPUSH/RPOP，不支持按分数插入 |
| **排序 vs 时间序** | ML 排序模型 | 纯时间倒序 (Chronological) | **ML 排序模型**：数据表明排序 Feed 的用户停留时间比时间序高 30-50%。但保留"切换到时间序"选项作为用户偏好和降级策略 |
| **一致性模型** | 强一致 | 最终一致 | **最终一致**：Feed 不需要强一致，用户容忍几秒延迟。唯一例外是 Read-your-own-writes：用户发帖后自己必须立即看到（通过写入自己的 Feed 缓存保证） |
| **帖子 ID 生成** | UUID | Snowflake ID | **Snowflake ID**：64-bit，包含时间戳（天然有序，利于数据库索引和范围查询），包含 machine_id（无需协调），比 UUID 节省 50% 存储空间 |

### CAP 定理应用

News Feed 系统选择 **AP (Availability + Partition Tolerance)**:

- **Partition 发生时**：两个 DC 各自继续服务 Feed 请求，使用本地缓存数据。
  Fan-out 可能暂停（Kafka 跨 DC 同步中断），但用户看到的 Feed 仍然可用
  （只是可能稍旧）
- **Partition 恢复后**：Kafka 自动补发积压消息，Feed 缓存逐步收敛到一致状态
- **不选 CP 的原因**：如果为了一致性而拒绝服务（Feed 返回错误），用户体验
  灾难性下降。一个"稍微过时"的 Feed 远好于一个"不可用"的 Feed

### 成本 vs 性能

| 层次 | 低成本方案 | 高性能方案 | 我们的平衡点 |
|------|-----------|-----------|-------------|
| Feed 缓存 | 只缓存 DAU 用户 | 缓存所有用户 | 缓存 30 天活跃用户（3 亿），覆盖 95%+ 请求 |
| 排序模型 | CPU 推理 (慢但便宜) | GPU 推理 (快但贵) | GPU 用于前 200 候选精排，CPU 用于 1000 -> 200 粗排 |
| 媒体存储 | 单份存储 | 多分辨率 + CDN 预热 | 3 种分辨率 (缩略图/标准/原图)，热门内容 CDN 预热 |

### 10x / 100x 扩展时的变化

**10x (20 亿 DAU)**:
- Feed Cache 需要 36 TB Redis -> 按区域分片，用户只缓存在 Home Region
- Fan-out 需要更激进的分层策略：活跃粉丝实时 Push，非活跃 7 天以上的完全 Pull
- Ranking Service 需要更轻量的模型或 two-stage ranking (粗排 + 精排)
- 考虑使用 **Thrift/gRPC** 替代 REST 减少序列化开销

**100x (图片/视频平台转型)**:
- 媒体存储成为主要成本 -> 自建存储集群替代 S3
- CDN 费用爆炸 -> 自建 PoP (Point of Presence) 节点或 P2P 分发
- Feed 排序需要考虑视频完播率、观看时长等更复杂的信号
- 可能需要从 MySQL 迁移到自研存储引擎（参考 Facebook TAO, Instagram Cassandra）
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果 Fan-out Service 完全宕机，会发生什么？

**承认影响**: Fan-out Service 宕机意味着新帖子不会被推送到粉丝的 Feed 缓存中。
用户的 Feed 会"冻结"在最后一次成功 Fan-out 的状态。

**缓解措施**:
1. **Kafka 消息持久化**: Fan-out 事件在 Kafka 中保留 72 小时。Fan-out Service
   恢复后自动从上次消费位点继续处理，不会丢失任何帖子
2. **降级到 Pull 模式**: 在 Fan-out Service 宕机期间，Feed Service 临时切换到
   对所有关注者做 Fan-out on Read（延迟升高到 1-2s 但功能可用）
3. **恢复后追赶 (Catch-up)**: Fan-out Service 重启后以高吞吐消费积压消息，
   同时 Feed Service 逐步从 Pull 模式切回正常模式

**设计启示**: 这就是为什么我们用 Kafka 作为 Post Service 和 Fan-out Service
之间的缓冲——它既是消息队列，也是持久化的重放日志。

### Q2: 一个拥有 5000 万粉丝的超级名人发帖，系统如何应对？

**场景分析**: 如果用 Fan-out on Write，一条帖子需要 5000 万次 Redis 写入，
按 50K writes/s 限流需要 1000 秒（~17 分钟），这对于"实时"来说完全不可接受。

**我们的设计已处理此场景**:
1. 粉丝数 >= 10,000 的用户被标记为名人，**不做 Fan-out on Write**
2. 名人发帖只写入 `celebrity_posts:{user_id}` (Redis Sorted Set)，O(log N) 一次写入
3. 粉丝请求 Feed 时，Feed Service 从 `celebrity_posts` 实时拉取名人帖子，
   与缓存中的普通帖子合并后排序

**额外优化**:
- 名人帖子的 `celebrity_posts` 加大缓存 TTL（7 天），因为访问频率极高
- 排序时对名人帖子做轻微加权提升 (boost)，因为用户通常更关注名人内容
- 客户端做本地缓存 + 增量刷新，减少重复请求

### Q3: 如果两个用户同时发帖，粉丝 Feed 中的顺序如何保证？

**关键洞察**: 我们**不需要保证全局严格顺序**。

**原因**:
1. Feed 经过 ML 排序后已经不是时间顺序了，绝对时间序无意义
2. 不同用户发帖到达 Fan-out Service 的顺序本身就是不确定的（网络延迟、
   Kafka 分区分配等）
3. 用户实际上无法感知两条在 1 秒内发布的帖子谁先谁后

**保证的是**:
- **单个用户内的帖子顺序**: 同一用户的帖子按 Snowflake ID 严格有序
  （因为 Snowflake ID 包含时间戳，且单 Worker 内单调递增）
- **Read-your-own-writes**: 用户自己发的帖子立即出现在自己的 Feed 顶部
- **最终收敛**: 所有粉丝最终会看到所有帖子，只是顺序可能因排序模型略有不同

### Q4: 如果流量突然 10 倍增长（比如某个全球事件），系统如何应对？

**自动扩展策略**:
1. **Feed Service / Post Service**: 无状态服务，基于 CPU/QPS 指标自动横向扩展
   (Auto-scaling Group)，从 25 实例扩展到 100+ 实例（约 3-5 分钟）
2. **Redis**: 短期内无法自动扩展（需要 resharding），靠预留 30% 缓冲容量吸收
3. **Kafka**: 提前配置足够的 partition 数（如 128），Consumer 自动重平衡

**降级策略**:
- **Stage 1**: 关闭 ML 排序，返回时间倒序 Feed（节省 GPU 资源）
- **Stage 2**: 减少 Fan-out 范围（只推送给 3 天内活跃的粉丝）
- **Stage 3**: 返回缓存的 Feed 快照（可能几分钟前的数据）
- **Stage 4**: 对非核心功能限流（Explore Feed、推荐、广告插入）

**经验数据**: Instagram 在超级碗期间流量约为平时 5 倍，通过预扩展 +
自动扩展在 15 分钟内稳定。

### Q5: 如何防止 Feed 质量问题（低质量内容、垃圾帖子泛滥）？

**多层防御**:
1. **发帖时 (Pre-publish)**：内容审核模型检测垃圾内容 / 违规内容，
   阻止发布或标记为待审核
2. **排序时 (Ranking)**：排序模型包含质量信号（举报率、负面互动率），
   低质量帖子自然排到底部
3. **用户反馈 (Feedback Loop)**：用户"不感兴趣"/"举报"操作实时回传，
   降低该类内容在该用户 Feed 中的权重
4. **限流 (Rate Limit)**：单用户发帖频率限制（100 posts/hour），
   防止机器人刷屏

**指标**: 核心观测指标是 **"有意义的互动率" (Meaningful Social Interaction, MSI)**，
而非简单的停留时间。如果某类内容增加停留时间但降低 MSI（如 clickbait），
排序模型会逐步降低其权重。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1h Interview Pacing)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 1 小时面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清

"信息流系统的核心挑战是**扇出策略的选择**和**个性化排序**。让我先确认几个关键约束。"

- 确认用户规模（亿级 DAU）和是否有名人用户 -> 决定 Fan-out 策略
- 确认 Feed 是时间序还是排序 -> 决定是否需要 Ranking Service
- 确认内容类型（图文/视频）-> 影响存储和带宽估算
- 确认实时性要求 -> 影响 Push vs Pull 选择

功能需求: 发帖、获取 Feed、实时更新、排序、分页。
非功能需求: 99.99% 可用性、P99 < 500ms、2 亿 DAU。
明确排除: 评论/点赞、用户管理、内容审核。

### 5-15 分钟: 高层架构

画出核心组件:
- **写路径**: Client -> Post Service -> Kafka -> Fan-out Service -> Redis Feed Cache
- **读路径**: Client -> Feed Service -> Redis Cache + Celebrity Posts -> Ranking Service -> Response

**核心架构决策 -- Fan-out 混合模型**:
"这是整个设计中最关键的决策。纯 Push 对名人不可行（5000 万粉丝 = 5000 万次写入），
纯 Pull 读延迟过高。我们用混合模型: 99% 的普通用户 Push（保证读取快），1% 的名人 Pull（避免写放大）。
阈值设为 10,000 粉丝，这是 Facebook 的实际做法。"

数据库选型:
- MySQL 分片存帖子 (结构化 + 事务)
- Redis 存 Feed 缓存 (低延迟)
- S3 + CDN 存媒体 (大文件 + 全球分发)
- Kafka 做异步解耦 (Fan-out + 媒体处理)

### 15-40 分钟: 深入设计（选 2-3 个重点）

**重点 1: Fan-out 机制详解 (10 min)**
- 普通用户发帖: Kafka event -> Fan-out Service -> Redis ZADD (Pipeline, 1000/batch)
- 名人发帖: 只写 celebrity_posts set，读时实时拉取
- 优化: 优先推送给 7 天活跃粉丝，限流 50K writes/s/post
- Read-your-own-writes: 发帖时同步写入自己的 Feed 缓存

**重点 2: Feed 排序流水线 (8 min)**
- 两阶段排序: 粗排 (1000 -> 200, 轻量模型) + 精排 (200 -> 20, 深度模型)
- 特征: 作者亲密度、帖子年龄、互动率、内容类型、上下文
- 降级: 排序服务不可用时回退到时间倒序
- Cursor 分页: 基于排序分数，O(1) 翻页

**重点 3: 缓存与降级策略 (7 min)**
- Feed Cache 结构: Redis Sorted Set, member=post_id, score=timestamp/ranking_score
- 缓存大小: 每用户 500 条，30 天活跃用户约 3.6 TB
- Cache Miss: 从 PostDB 重建（查询关注者最近帖子 + 排序）
- 三级降级: ML 排序 -> 时间序 -> 缓存快照

### 40-50 分钟: 容量估算与权衡

容量: 2 亿 DAU, 115K QPS (read), 3.6 TB Redis, 3.65 PB/yr 媒体。

关键权衡:
1. **Fan-out 策略**: Hybrid 是最优解（解释 Push/Pull/Hybrid 对比）
2. **一致性**: AP 优于 CP（旧 Feed > 不可用 Feed）
3. **排序 vs 简单**: ML 排序 +30-50% 停留时间，值得复杂度
4. **成本**: ~200K USD/月在 Instagram 规模，通过分层缓存和冷热数据分离优化

### 50-55 分钟: 总结与改进方向

"如果有更多时间，我会进一步优化:
1. **Explore Feed**: 基于协同过滤的推荐系统，不依赖关注关系
2. **视频 Feed**: 加入完播率信号、自适应码率选择
3. **隐私与合规**: GDPR 数据删除在 Feed 缓存中的传播
4. **实验平台**: A/B 测试不同排序策略的框架"

监控: Feed P99 延迟、Cache 命中率、Fan-out Kafka lag、Ranking 错误率。

### 55-60 分钟: 向面试官提问

准备 2-3 个展示系统设计深度的问题。

---

### 3 分钟电梯演讲版本

"News Feed 系统的核心是**混合 Fan-out 策略**: 99% 的普通用户用 Push 模型，
发帖时通过 Kafka -> Fan-out Service 将帖子 ID 写入每个粉丝的 Redis Sorted Set 缓存，
保证读取一次 Redis 即可获得 Feed。对 1% 的名人用户用 Pull 模型，
读取时实时拉取名人最新帖子与缓存合并。

获取 Feed 时经过两阶段 ML 排序: 粗排 1000 -> 200 候选，
精排 200 -> 20 展示，考虑亲密度、时间衰减、互动率等特征。
使用 Cursor 分页保证 O(1) 翻页性能。

规模: 2 亿 DAU, 115K QPS, 3.6 TB Redis Feed 缓存。
多 DC Active-Active + AP 一致性。三级降级:
ML 排序 -> 时间序 -> 缓存快照。月度成本约 200K USD。"
"""


def populate_interview_news_feed() -> None:
    """Create or update the interview-news-feed record with all 8 sections."""
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
    populate_interview_news_feed()
