"""Populate interview-live-comments system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design Facebook Live
Comments -- real-time comment streaming for live video with millions of
concurrent viewers. Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-live-comments"
TITLE = "Design Facebook Live Comments"
DISPLAY_ORDER = 108

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **Facebook Live / YouTube Live / Instagram Live** 的**直播评论系统
(Live Comments System)**。当主播进行直播时，数百万观众可以实时发送评论，所有在线
观众几乎同时看到评论流。系统需要处理极高的写入吞吐量（热门直播 100K+ 评论/秒）
并以极低延迟将评论分发给所有观众。

### 功能性需求 (Functional Requirements)

1. **实时评论发送 (Post Comment)**：观众在直播间发送文字评论，所有在线观众
   在 1-2 秒内看到
2. **评论流展示 (Comment Stream)**：观众端实时滚动展示最新评论，支持自动滚动
   和手动暂停浏览
3. **评论审核 (Moderation)**：自动过滤违规内容（敏感词、spam），主播/管理员
   可以手动删除或禁言用户
4. **表情/贴纸反应 (Reactions)**：观众可以发送预设表情反应（如爱心、笑脸），
   系统聚合显示反应计数
5. **置顶评论 (Pinned Comment)**：主播可以置顶一条评论，所有观众看到

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.9%（直播评论短暂不可用可容忍，不如聊天系统严格）
- **延迟 (Latency)**：评论从发送到对其他观众可见 P99 < 2s
- **吞吐量 (Throughput)**：热门直播间峰值 100,000+ 评论/秒写入，
  1000 万并发观众需要接收
- **一致性 (Consistency)**：**最终一致 (Eventually Consistent)**。不同观众可能
  短暂看到不同的评论顺序，这是可接受的。评论不需要全局严格排序
- **可扩展性 (Scalability)**：平台同时进行 10,000+ 场直播，总并发观众 1 亿+

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 热门直播的峰值并发观众数是多少？** -- WHY: 10 万观众和 1000 万观众的
   架构完全不同。10 万可以用单个 pub-sub 频道；1000 万需要多级扇出
   (**Fan-out Tree**)，每级聚合后再分发。

2. **Q: 评论是否需要持久存储？直播结束后还能回看吗？** -- WHY: 如果只需实时
   展示（阅后即焚），评论可以纯内存分发不落盘；如果需要回看，则需要写入持久
   存储并支持分页查询。

3. **Q: 是否需要支持评论回复（thread）还是扁平评论流？** -- WHY: 扁平评论流
   只需要按时间排序的 append-only 流，复杂度低。Thread 回复需要维护父子关系
   和嵌套展示，显著增加数据模型和渲染复杂度。

4. **Q: 评论审核的严格程度？是否需要实时 ML 审核？** -- WHY: 简单关键词过滤
   延迟 < 1ms，对主流程无影响；ML 模型审核延迟 10-50ms，可能成为瓶颈。如果
   审核必须在展示前完成（pre-moderation），则审核延迟直接加到端到端延迟中。

5. **Q: 观众是否看到完全相同的评论流？** -- WHY: 如果允许不同观众看到不同
   子集（采样），热门直播可以做评论抽样（每个观众只看到 30% 的评论），大幅降低
   扇出压力。这是 Facebook Live 的实际做法。

6. **Q: 是否需要支持慢速模式（slow mode，限制发言频率）？** -- WHY: 慢速模式
   是控制评论洪峰的关键手段。如果支持，需要在 Gateway 层做每用户速率限制。

7. **Q: 表情反应需要精确计数还是近似计数？** -- WHY: 精确计数需要原子操作
   或分布式计数器，成本高。近似计数（如 **HyperLogLog**）精度 ~1% 误差但
   节省大量资源，对用户体验无感知差异。

### 范围声明 (Out of Scope)

- 视频流传输 (**HLS / DASH / WebRTC**)
- 打赏 / 送礼 / 电商购物功能
- 私信 / 一对一聊天
- 直播间推荐算法
- 回放视频中的评论时间轴同步
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

直播评论系统的核心挑战是**高扇出 (High Fan-out)**: 一条评论需要分发给数百万
观众。与 Chat System (1:1 或小群扇出) 不同，Live Comments 的扇出比可达
1:10,000,000。这要求架构从"点对点路由"转变为"广播式分发"。

### 核心服务与职责

| 服务 | 职责 |
|------|------|
| **Comment Gateway (评论网关)** | 管理观众的长连接 (**WebSocket** 或 **SSE, Server-Sent Events**)，负责评论下发和心跳维护 |
| **Comment Ingestion Service (评论摄入服务)** | 接收观众发送的评论，验证参数、鉴权、速率限制，写入消息队列 |
| **Moderation Service (审核服务)** | 对评论进行实时审核：关键词过滤 + ML 模型分类（spam、hate speech、NSFW），阻断或标记违规评论 |
| **Comment Dispatcher (评论分发服务)** | 从消息队列消费审核通过的评论，按直播间分组，推送到 Fan-out 层 |
| **Fan-out Tree (扇出树)** | 多级分发架构：Root -> Regional Relays -> Edge Nodes -> Client。每级节点聚合评论后批量推送给下级 |
| **Reaction Aggregator (反应聚合器)** | 收集表情反应事件，按时间窗口聚合计数，定期推送聚合结果（不逐条推送） |
| **Comment Store (评论存储)** | 异步持久化评论到数据库，支持直播结束后的回看和分析 |

### 数据库选型与理由

| 数据 | 存储选型 | 理由 |
|------|----------|------|
| 评论持久化 | **Cassandra** | 写密集型 (100K+ writes/s)、按直播间 ID + 时间戳分区查询、水平扩展 |
| 直播间元数据 | **MySQL** | 结构化数据（主播信息、直播状态、配置），读多写少 |
| 实时评论分发 | **Redis Pub/Sub** 或 **Kafka** | 评论从 Ingestion 到 Dispatcher 的消息管道，解耦生产和消费 |
| 反应计数 | **Redis** (INCRBY) | 高频写入、原子递增、内存数据库适合实时计数 |
| 审核词库 | **Redis** (Set/Bloom Filter) | 关键词快速匹配，低延迟 |
| 用户禁言名单 | **Redis** (Set) | 快速查询用户是否被禁言 |

### 通信模式

- **SSE (Server-Sent Events)** 或 **WebSocket**：Gateway -> 观众客户端
  （评论下发的主通道）。SSE 更轻量（单向、HTTP 兼容、自动重连），适合评论
  这种服务器到客户端的单向推送场景
- **HTTP POST**：观众 -> Comment Ingestion Service（发送评论）
- **Kafka**：Ingestion Service -> Moderation Service -> Dispatcher（异步管道）
- **内部 gRPC**：Dispatcher -> Fan-out Tree 各节点间通信

### Fan-out Tree: 核心架构决策

这是直播评论系统**最核心的设计**，解决"一条评论如何在 2 秒内到达 1000 万观众"
的问题。

#### 三级扇出结构

```
Level 0: Comment Dispatcher (1 instance per live stream)
    |
Level 1: Regional Relays (5-10 per stream, 每个负责一个地理区域)
    |
Level 2: Edge Nodes (100-500 per stream, 每个维护 ~20K WebSocket/SSE 连接)
    |
Level 3: Client (观众设备)
```

#### 扇出计算

以 1000 万观众为例:
- Level 0 -> Level 1: 1 -> 10 (10x fan-out)
- Level 1 -> Level 2: 10 -> 500 (50x fan-out per relay)
- Level 2 -> Level 3: 500 -> 10,000,000 (20,000x fan-out per edge node)

每级的扇出比控制在可管理的范围内（< 50x 内部, < 20K 客户端连接/节点）。

#### 评论批处理 (Batching)

为减少网络开销，评论不逐条推送，而是**按时间窗口批处理**:
- Edge Node 每 **200-500ms** 收集评论，批量打包后推送给客户端
- 客户端收到批量评论后动画式逐条展示，用户感知为"实时滚动"
- 批处理将网络请求从 100K/s 降低到 2-5 requests/s per client

### 数据分区策略

- **Kafka**: 按 `live_stream_id` 分区，同一直播间的评论在同一 partition 中，
  保证消费顺序
- **Cassandra**: 按 `(live_stream_id, time_bucket)` 分区。`time_bucket` 按
  5 分钟分桶，避免单分区过大
- **Fan-out Tree**: 按地理区域分区，用户连接到最近的 Edge Node
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 发送评论 API

```
POST /v1/live/{stream_id}/comments
Authorization: Bearer <token>

Request Body:
{
  "content": "This is amazing!",
  "client_comment_id": "cc_abc123",
  "type": "text"
}

Response: 202 Accepted
{
  "comment_id": "cmt_1705315600_042",
  "status": "pending_moderation"
}
```

返回 **202 Accepted** 而非 201 Created，因为评论需要异步审核后才正式发布。

### 获取评论流 (SSE)

```
GET /v1/live/{stream_id}/comments/stream
Authorization: Bearer <token>
Accept: text/event-stream

Response: 200 OK
Content-Type: text/event-stream

event: comment_batch
data: {
  "comments": [
    {
      "comment_id": "cmt_1705315600_042",
      "user_id": "user_alice",
      "username": "Alice",
      "avatar_url": "https://cdn.example.com/alice.jpg",
      "content": "This is amazing!",
      "type": "text",
      "created_at": "2024-01-15T18:00:00.123Z"
    },
    {
      "comment_id": "cmt_1705315600_043",
      "user_id": "user_bob",
      "username": "Bob",
      "avatar_url": "https://cdn.example.com/bob.jpg",
      "content": "Love this stream!",
      "type": "text",
      "created_at": "2024-01-15T18:00:00.456Z"
    }
  ]
}

event: reaction_update
data: {
  "reactions": {"heart": 15234, "laugh": 3421, "wow": 892},
  "delta": {"heart": 42, "laugh": 8, "wow": 3},
  "window_ms": 500
}

event: pinned_comment
data: {
  "comment_id": "cmt_1705315600_001",
  "user_id": "user_streamer",
  "content": "Welcome everyone! Drop your questions below.",
  "pinned_at": "2024-01-15T17:55:00Z"
}
```

### 发送反应 API

```
POST /v1/live/{stream_id}/reactions
Authorization: Bearer <token>

Request Body:
{
  "reaction_type": "heart"
}

Response: 200 OK
```

反应不返回具体计数（避免 read-after-write 一致性问题），客户端通过 SSE
的 `reaction_update` 事件获取聚合计数。

### 审核操作 API

```
DELETE /v1/live/{stream_id}/comments/{comment_id}
Authorization: Bearer <token>  (需要主播/管理员权限)

Response: 204 No Content
```

删除评论后，通过 SSE 推送 `comment_deleted` 事件，客户端移除该评论。

### 核心数据模型

#### Comment 表 (Cassandra)

```
CREATE TABLE live_comments (
    stream_id    TEXT,
    time_bucket  TEXT,       -- e.g., "2024-01-15T18:05" (5-min bucket)
    comment_id   BIGINT,    -- Snowflake ID (time-ordered)
    user_id      TEXT,
    username     TEXT,
    avatar_url   TEXT,
    content      TEXT,
    type         TEXT,       -- text, sticker, gift
    moderation   TEXT,       -- approved, rejected, pending
    created_at   TIMESTAMP,
    PRIMARY KEY ((stream_id, time_bucket), comment_id)
) WITH CLUSTERING ORDER BY (comment_id DESC);
```

#### LiveStream 表 (MySQL)

```sql
CREATE TABLE live_streams (
    stream_id      VARCHAR(64) PRIMARY KEY,
    streamer_id    VARCHAR(64),
    title          VARCHAR(255),
    status         ENUM('live', 'ended', 'scheduled'),
    started_at     DATETIME,
    ended_at       DATETIME,
    viewer_count   INT DEFAULT 0,
    comment_count  BIGINT DEFAULT 0,
    config         JSON,   -- slow_mode, moderation_level, etc.
    INDEX idx_status (status)
);
```

### 写路径 (Write Path): 发送评论

```
1. Client -> Comment Ingestion Service (HTTP POST):
   a. 鉴权 (JWT token)
   b. 速率限制检查 (Redis: INCR rate:{user_id}:{stream_id} EX 60, limit=5/min)
   c. 参数校验 (内容长度 <= 200 chars, 非空)
   d. 幂等检查 (Redis: SETNX dedup:{client_comment_id} EX 300)
   e. 生成 comment_id (Snowflake ID)

2. Ingestion -> Kafka (topic: "live-comments-raw"):
   a. Key = stream_id (保证同一直播间评论在同一 partition)
   b. Value = 完整评论对象

3. Moderation Service (Kafka consumer):
   a. 关键词过滤 (Redis Bloom Filter, < 1ms)
   b. ML 审核模型 (spam/hate detection, ~10ms)
   c. 检查用户是否被禁言 (Redis Set)
   d. 通过 -> 写入 Kafka "live-comments-approved"
   e. 拒绝 -> 写入 Kafka "live-comments-rejected", 通知发送者

4. Comment Dispatcher (Kafka consumer for "approved"):
   a. 异步写入 Cassandra (comment store, 非关键路径)
   b. 推送到 Fan-out Tree Level 0 (Root)

5. Fan-out Tree 分发:
   a. Root -> Regional Relays (gRPC streaming)
   b. Relays -> Edge Nodes (gRPC streaming)
   c. Edge Nodes: 收集 200-500ms 窗口内评论 -> 批量推送 SSE

6. Client 收到评论批次:
   a. 追加到评论列表, 动画展示
   b. 如果列表过长 (>500 条), 裁剪旧评论释放内存
```

### 读路径 (Read Path): 加入直播间

```
1. Client:
   a. GET /v1/live/{stream_id} -> 获取直播间信息 + 置顶评论
   b. GET /v1/live/{stream_id}/comments?limit=50 -> 获取最近 50 条评论
   c. GET /v1/live/{stream_id}/comments/stream -> 建立 SSE 连接

2. Edge Node:
   a. 将客户端注册到对应 stream_id 的订阅列表
   b. 后续评论通过 Fan-out Tree 自动推送

3. Client 断连后:
   a. SSE 自动重连 (内置机制, Last-Event-ID 用于断点续传)
   b. 重连后拉取断连期间的评论 (如果需要)
```

### 异步路径

- **评论持久化**: Dispatcher -> Kafka "comments-persist" -> Comment Store Writer
  -> Cassandra (异步, 不阻塞实时分发)
- **反应聚合**: Client -> Reaction Aggregator -> Redis INCRBY ->
  每 500ms 读取 delta 推送给 Edge Nodes
- **审核日志**: 所有审核决策写入 Kafka "moderation-log" -> 离线分析 + 审计
- **观众计数**: Edge Node 定期上报连接数 -> 中心聚合 -> 更新 viewer_count
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 基础数据假设

| 指标 | 数值 |
|------|------|
| 平台同时直播数 | 10,000 场 |
| 总并发观众 | 1 亿 |
| 热门直播平均观众 | 1000 万 |
| 普通直播平均观众 | 5,000 |
| 热门直播评论速率 | 100,000 条/秒 |
| 普通直播评论速率 | 50 条/秒 |
| 全平台评论写入 QPS (峰值) | ~500,000 条/秒 |
| 平均评论大小 | 200 bytes (含用户名、头像 URL) |
| 表情反应速率 (热门直播) | 500,000 次/秒 |
| 日均直播时长 | 2 小时/场 |

### QPS 估算

**评论写入 QPS (Ingestion)**:

$$Q_{write} = 500{,}000 \text{ QPS (peak across platform)}$$

**评论分发 QPS (Fan-out)**:

以单个热门直播间为例 (1000 万观众, 100K 评论/秒):

$$Q_{fanout} = 100{,}000 \times 10{,}000{,}000 = 10^{12} \text{ messages/sec (naive)}$$

显然不可能逐条推送。批处理后:

$$Q_{fanout\_batched} = \frac{10{,}000{,}000}{200\text{ms batch}} = 50{,}000{,}000 \text{ batches/sec}$$

但每个 batch 包含 ~50 条评论 (100K/s x 0.5s / 1000 edge nodes = ~50):

$$Q_{edge\_push} = \frac{10{,}000{,}000}{20{,}000 \text{ conn/node}} = 500 \text{ Edge Nodes}$$

每个 Edge Node 每 500ms 推送一次 batch 给 20K 客户端:

$$Q_{per\_edge} = \frac{20{,}000}{0.5s} = 40{,}000 \text{ pushes/sec per edge node}$$

### WebSocket/SSE 连接数

$$C_{total} = 100{,}000{,}000 \text{ concurrent connections (platform-wide)}$$

每个 Edge Node 维持约 20,000 个 SSE 连接:

$$N_{edge} = \frac{100{,}000{,}000}{20{,}000} = 5{,}000 \text{ Edge Nodes}$$

### 存储估算

**评论存储 (Cassandra)**:

$$S_{comments\_daily} = 500{,}000 \text{ QPS} \times 86{,}400 \times 200 \text{ bytes} = 8.64 \text{ TB/day}$$

保留 90 天:

$$S_{comments\_total} = 8.64 \times 90 = 777.6 \text{ TB} \approx 0.78 \text{ PB}$$

**反应计数 (Redis)**:

每个直播间 ~10 种反应类型, 每个 8 bytes:

$$S_{reactions} = 10{,}000 \text{ streams} \times 10 \times 8 \text{ bytes} = 800 \text{ KB (negligible)}$$

**速率限制 + 去重 (Redis)**:

$$S_{rate\_limit} = 100{,}000{,}000 \text{ users} \times 64 \text{ bytes} = 6.4 \text{ GB}$$

### 带宽估算

**评论分发出站带宽 (Edge Nodes -> Clients)**:

每个 batch ~50 条评论 x 200 bytes = 10 KB, 每 500ms 推送一次:

$$BW_{per\_client} = \frac{10 \text{ KB}}{0.5\text{s}} = 20 \text{ KB/s per client}$$

$$BW_{total} = 10{,}000{,}000 \times 20 \text{ KB/s} = 200 \text{ GB/s}$$

分摊到 5000 个 Edge Nodes:

$$BW_{per\_edge} = \frac{200 \text{ GB/s}}{5{,}000} = 40 \text{ MB/s per node}$$

40 MB/s 对单台服务器完全可行 (标准 10 Gbps NIC)。

### 核心算法

#### 评论采样 (Comment Sampling)

热门直播 100K 评论/秒全部展示会导致客户端卡顿。实际做法是**采样**:

- 每个观众只看到 30-50% 的评论 (随机采样)
- 采样策略: **Reservoir Sampling** 变体，每个 500ms 窗口内从 N 条评论中
  均匀采样 K 条

$$P(\text{comment shown}) = \min\left(1, \frac{K}{N}\right)$$

其中 $K$ 是目标展示速率 (如 30 条/秒), $N$ 是实际评论速率。

客户端感知: 评论流始终保持 ~30 条/秒的舒适速度，不会因评论过多而无法阅读。

#### 反应聚合 (Reaction Aggregation)

不逐条推送反应事件，而是按时间窗口聚合:

```
Window: 500ms
Input: [heart, heart, laugh, heart, wow, heart, laugh]
Output: {"heart": 4, "laugh": 2, "wow": 1}
```

使用 Redis pipeline 批量 INCRBY:

```
MULTI
INCRBY reactions:{stream_id}:heart 4
INCRBY reactions:{stream_id}:laugh 2
INCRBY reactions:{stream_id}:wow 1
EXEC
```

每 500ms 读取当前计数推送给客户端。

#### Snowflake ID 生成

与 Chat System 相同, 64-bit 有序 ID:

```
| 1 bit (unused) | 41 bits (timestamp ms) | 10 bits (machine ID) | 12 bits (sequence) |
```

单节点 4096 IDs/ms, 多节点并行可支持 500K+ IDs/sec。

### 服务器数量估算

| 组件 | 计算 | 数量 |
|------|------|------|
| Edge Nodes (SSE) | 100M connections / 20K per node | ~5,000 节点 |
| Regional Relays | 5000 edges / 50 per relay | ~100 节点 |
| Comment Ingestion | 500K QPS / 50K per instance | ~10 实例 |
| Moderation Service | 500K QPS / 20K per instance (ML 延迟) | ~25 实例 |
| Comment Dispatcher | 500K QPS / 100K per instance | ~5 实例 |
| Reaction Aggregator | 聚合所有反应事件 | ~10 实例 |
| Cassandra (Storage) | 8.64 TB/day, RF=3 | ~50 节点 |
| Redis (Rate limit + Reactions) | ~10 GB, 高 QPS | ~5 节点 |
| Kafka Brokers | 500K msg/s, 3 topics | ~15 brokers |

### 月度成本估算

| 项目 | 月度费用 |
|------|----------|
| Edge Nodes 5000 台 (c6g.large) | ~350,000 USD |
| Regional Relays 100 台 (c6g.xlarge) | ~15,000 USD |
| Cassandra 50 节点 (i3.xlarge) | ~40,000 USD |
| Redis 5 节点 (r6g.xlarge) | ~2,000 USD |
| Kafka 15 brokers (m6g.xlarge) | ~8,000 USD |
| Ingestion + Moderation + Dispatcher | ~5,000 USD |
| CDN (头像等静态资源) | ~50,000 USD |
| **总计** | **~470,000 USD/月** |

(注意: 这比 Chat System 便宜得多，因为评论不需要持久送达保证、
不需要离线队列、单向推送比双向 WebSocket 更轻量)
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints -- Scale & Reliability)

### 具体规模参数

| 指标 | 数值 |
|------|------|
| 平台同时直播数 | 10,000 场 |
| 总并发观众 | 1 亿 |
| 热门直播峰值观众 | 1000 万 |
| 评论写入 QPS (峰值) | 500,000 |
| 评论分发: Edge Node 总数 | 5,000 |
| 评论持久化: Cassandra 日增 | 8.64 TB |
| 出站带宽 (总计) | ~200 GB/s |

### 单点故障分析 (SPOF Analysis)

| 组件 | 风险 | 缓解措施 |
|------|------|----------|
| Edge Node | 单台宕机断开 20K 连接 | SSE 内置自动重连 (Last-Event-ID)；L7 LB 将重连分配到健康节点；20K 断连对 1000 万观众影响 < 0.2% |
| Regional Relay | 宕机导致一个区域评论延迟 | 每区域 2+ Relay 互为备份；故障时流量自动切到备用 Relay |
| Comment Dispatcher | 宕机导致评论分发停止 | Kafka consumer group 自动 rebalance, 其他 Dispatcher 实例接管 partition |
| Kafka Broker | 单 Broker 故障 | RF=3, ISR 保证单 Broker 故障不丢消息 |
| Moderation Service | 审核停止导致评论积压 | 设置 Kafka consumer lag 告警；极端情况下 bypass 审核直接放行 (降级) |
| Redis | 速率限制失效 | Redis Sentinel 自动故障转移；Redis 不可用时 fallback 到本地令牌桶 |

### 多数据中心 / 跨区域 (Multi-DC)

**架构: 按观众地理位置分层分发**

- **DNS 层**: **GeoDNS** 将观众路由到最近的 Edge Node 集群
- **直播源 DC**: 主播所在区域的 DC 运行 Ingestion + Moderation + Dispatcher
- **评论分发**: Dispatcher 通过跨 DC 专线推送到各区域的 Regional Relay
  - 延迟: 同区域 < 50ms, 跨区域 < 200ms
- **数据复制**:
  - Cassandra: **NetworkTopologyStrategy**, 每 DC 2 副本
  - Kafka: 跨 DC 不做镜像（评论实时性强，跨 DC 复制延迟不可接受；
    改为 Dispatcher 直接推送到各 DC 的 Relay）

**Region 分布示例**:
- US-East: 2000 Edge Nodes, 40 Relays
- US-West: 1000 Edge Nodes, 20 Relays
- EU: 1000 Edge Nodes, 20 Relays
- Asia: 800 Edge Nodes, 15 Relays
- Other: 200 Edge Nodes, 5 Relays

### 高并发处理

1. **评论洪峰控制 (Comment Storm)**:
   - **用户级速率限制**: 每用户每分钟最多 5 条评论 (Redis INCR + EX)
   - **直播间级速率限制**: 评论速率超过 100K/s 时自动开启慢速模式
     (slow mode, 每用户 30s 发一条)
   - **全局限流**: Kafka 消费速率限制防止下游过载

2. **评论采样 (Comment Sampling)**:
   - 评论速率 > 50/s 时，Edge Node 开始采样
   - 不同观众看到不同随机子集，但每个人看到的评论速率 ~30/s
   - 采样率 = min(1, 30 / actual_rate)
   - 确保主播的评论不被采样掉 (白名单机制)

3. **SSE 背压 (Backpressure)**:
   - 如果客户端消费速度 < 推送速度 (如弱网)，Edge Node 丢弃该客户端的旧 batch
   - 客户端只需展示最新评论，错过的评论不需要补发
   - 与 Chat System 的 at-least-once 不同: 直播评论是 **at-most-once** 语义

4. **熔断器 (Circuit Breaker)**:
   - Cassandra 写入延迟 > 500ms -> 熔断持久化, 评论仍然实时分发 (内存路径)
   - Moderation Service 延迟 > 100ms -> 降级为仅关键词过滤 (跳过 ML 模型)
   - 单个直播间评论 > 200K/s -> 触发全局采样, 减少到 50K/s

5. **优雅降级 (Graceful Degradation)**:
   - **Level 1**: 反应聚合频率降低 (500ms -> 2s)
   - **Level 2**: 评论采样率提高 (只展示 10% 评论)
   - **Level 3**: ML 审核关闭, 仅关键词过滤
   - **Level 4**: 评论持久化关闭 (纯内存分发)
   - **Level 5**: 新评论提交暂停, 仅展示已有评论流

### 监控与告警 (Monitoring & Alerting)

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 评论端到端延迟 P99 | > 2s | P1 (Warning) |
| 评论端到端延迟 P99 | > 5s | P0 (Critical) |
| Kafka consumer lag | > 100K messages | P1 |
| Edge Node 连接数 | > 18K/node (90% capacity) | P2 (Scale-up) |
| Moderation Service 延迟 P99 | > 50ms | P1 |
| 评论写入 QPS | > 400K (80% capacity) | P2 |
| Edge Node 推送失败率 | > 5% | P1 |
| SSE 断连率 | > 2%/min | P1 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **传输协议** | WebSocket (双向) | SSE (单向) | **SSE**: 评论分发是服务器到客户端的单向推送。SSE 比 WebSocket 更轻量：基于 HTTP (兼容 CDN/proxy)、内置自动重连 (Last-Event-ID)、服务器资源占用更低。评论发送走独立的 HTTP POST，不需要双向通道。WebSocket 的双向能力在此场景下是多余的 |
| **评论一致性** | 所有观众看到相同评论 | 不同观众看到不同子集 (采样) | **采样**: 热门直播 100K 评论/s 全量展示导致客户端卡顿且用户无法阅读。每个观众看到 ~30 条/s 的随机子集，用户体验更好。代价是观众间无法引用同一条评论讨论，但直播评论的交互性本就较弱 |
| **送达保证** | At-least-once (可靠送达) | At-most-once (尽力送达) | **At-most-once**: 与 Chat System 不同，错过一条直播评论对用户体验影响极小。At-least-once 需要客户端 ACK + 服务端重试，大幅增加 Edge Node 复杂度和状态管理。直播评论是"信息流"而非"对话"，丢失可容忍 |
| **审核策略** | Pre-moderation (审核后展示) | Post-moderation (展示后审核) | **Pre-moderation**: 虽然增加 10-50ms 延迟，但可以阻止违规内容传播。对于大规模直播，一条违规评论被 1000 万人看到的风险远大于额外延迟成本。通过关键词快速过滤 (<1ms) + ML 异步审核 (~10ms) 的两级策略控制延迟 |
| **评论存储** | 实时写入 DB | 异步批量写入 | **异步批量写入**: 评论持久化不在实时分发的关键路径上。Cassandra 写入在 Kafka consumer 中异步完成，即使 Cassandra 暂时不可用，评论仍然实时分发。代价是如果在持久化前系统崩溃，少量评论可能丢失 (可接受) |

### CAP 定理应用

Live Comments 选择 **AP (Availability + Partition Tolerance)**:

- **Partition 发生时**: 各区域的 Edge Node 继续向本区域观众推送评论。
  跨区域的评论可能短暂不可见（如亚洲观众暂时看不到美国观众的评论），
  但本区域的评论流不中断
- **Partition 恢复后**: Kafka 跨 DC 同步自动补发积压评论；但由于评论
  时效性强，超过 30s 的旧评论可能被客户端丢弃
- **不选 CP 的原因**: 直播评论的价值在于"实时性"。如果为了一致性暂停服务，
  观众在直播最精彩的时刻无法评论，这比短暂的评论不一致严重得多

### 成本 vs 性能

| 层次 | 低成本方案 | 高性能方案 | 我们的平衡点 |
|------|-----------|-----------|-------------|
| 传输 | HTTP Long Polling (无状态) | SSE/WebSocket (有状态) | SSE: 比 Long Polling 延迟低 10x, 比 WebSocket 资源省 30% |
| 评论分发 | 全量推送 (简单) | 采样 + 批处理 (复杂) | 采样 + 500ms 批处理: 网络开销降低 100x, 用户体验更好 |
| 审核 | 纯关键词 (便宜, < 1ms) | ML 模型 (贵, ~10ms) | 两级: 关键词快速过滤 + ML 异步审核, 平衡精度和延迟 |
| 存储 | 不存储 (纯实时) | 全量持久化 (贵) | 异步持久化 90 天, 冷数据压缩 + lifecycle 策略 |
| Edge Nodes | 共享节点 (多直播共用) | 专用节点 (每直播独占) | 共享: 普通直播共用节点, 热门直播动态分配专用节点池 |

### 10x / 100x 扩展时的变化

**10x (10 亿并发观众, 5M 评论/s)**:
- Edge Nodes 扩展到 50,000 台 -> 考虑将 Edge 层下沉到 **CDN 边缘节点**，
  利用 CDN 的全球分布（如 Cloudflare Workers / AWS CloudFront Functions）
- Fan-out Tree 增加第 4 级 (Super-Regional Hubs)
- 评论采样更激进 (每个观众只看到 10% 评论)
- Kafka 无法承受 5M QPS -> 改用自研 in-memory pub-sub (参考 Facebook 的
  **Wormhole**)

**100x (全球级超大事件, 如世界杯决赛)**:
- 完全放弃服务端评论路由, 改为 **CDN 边缘计算 + P2P 分发**
- 评论流变成"直播频道"概念, 用类似视频 HLS 的分段分发
  (每 1s 一个评论 segment, CDN 缓存分发)
- 审核: 预训练 edge-side ML 模型在 CDN 节点本地审核, 不回源
- 成本模型从"服务器数量"变为"CDN 带宽费用"
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个热门直播突然从 10 万观众暴增到 1000 万观众，系统怎么应对？

**承认挑战**: 100 倍观众增长意味着 Edge Node 需求从 5 台暴增到 500 台，
如果不提前准备会导致现有节点过载、评论延迟飙升。

**缓解措施**:
1. **预热机制 (Pre-warming)**: 对预告型直播（如明星直播预告），提前根据预约
   人数分配 Edge Node 池。算法: 预分配 = 预约数 x 1.5 / 20K 连接
2. **弹性扩缩容**: K8s HPA 基于 SSE 连接数自动扩容 Edge Node，
   扩容延迟 < 90s (容器启动 + 预热)
3. **溢出保护**: 单个 Edge Node 连接数 > 18K 时拒绝新连接，
   L7 LB 将新用户路由到刚扩容的节点
4. **即时降级**: 评论速率 > Edge Node 处理能力时自动开启采样，
   保证已连接观众的评论体验不受影响
5. **Fan-out Tree 动态调整**: 自动在过载区域插入新的 Regional Relay 节点

**恢复时间**: 从检测到过载到扩容完成通常 2-3 分钟。期间通过采样和降级
保证评论流不中断。

### Q2: 不同观众看到不同的评论（因为采样），这会不会影响用户体验？

**关键洞察**: 直播评论的消费模式与聊天不同——观众主要是"浏览"而非"对话"。

**为什么可接受**:
1. **阅读速度限制**: 人类最快阅读速度约 5 条/秒，100K 条/秒全量展示
   反而降低体验（评论闪过太快无法阅读）
2. **社交验证 (Social Proof)**: 观众需要的是"很多人在评论"的感觉，
   而非看到每一条具体评论。30 条/s 的滚动速度已经传达了"热闹"的信号
3. **无引用需求**: 不同于聊天中"你说的那条消息"的场景，直播评论几乎不存在
   跨评论引用。观众不会发现自己看到的评论集和邻座不同

**保底措施**:
- 主播的评论、管理员的评论、置顶评论不受采样影响 (白名单)
- 被 @ 的评论对被 @ 的用户保证可见
- 采样算法保证每个用户的评论被展示的概率公平（不会系统性偏向某些用户）

### Q3: 审核延迟 10-50ms 看起来不多，但 100K 评论/秒时审核服务会不会成为瓶颈？

**分析**:
- 审核服务需要处理 100K QPS, 每条 10-50ms
- 单实例只能处理 ~1000 QPS (假设 ML 推理 ~10ms, CPU bound)
- 需要 100 个审核实例

**实际策略是两级审核**:
1. **快速路径 (< 1ms)**: 关键词 Bloom Filter + 正则匹配，过滤 5% 明显违规
2. **ML 路径 (~10ms)**: GPU 批处理推理，对剩余 95% 评论做语义分析
3. **ML 批处理优化**: 不逐条推理，而是每 50ms 收集一批评论 (约 5000 条)
   打包进 GPU 批次，吞吐量从 1000 QPS/instance 提升到 10K QPS/instance
4. **最终需要 ~10 个 GPU 实例** (100K / 10K)

**极端情况降级**: 审核积压 > 5 秒时，跳过 ML 审核仅用关键词过滤放行。
宁可漏审少量软违规，也不能让评论流停滞。

### Q4: SSE 连接断了，用户重连后错过的评论怎么办？

**设计决策: 不补发**。理由:

1. **时效性**: 直播评论的价值在"当下"。30 秒前的评论对重新连接的用户
   几乎没有意义
2. **简化架构**: 不需要为每个客户端维护消费游标 (offset)，
   Edge Node 无状态化
3. **SSE Last-Event-ID**: 虽然 SSE 协议支持断点续传 (Last-Event-ID)，
   我们故意不实现它。重连后从当前最新评论开始推送

**用户体验优化**:
- 重连后先拉取最近 20 条评论 (HTTP GET /comments?limit=20)
  作为"上下文补充"
- 然后接入实时 SSE 流
- 重连过程对用户是透明的 (SSE 自动重连, < 3 秒)

### Q5: 如果审核系统误判，一条正常评论被删除了，怎么处理？

**承认**: ML 审核不可能 100% 准确。典型误判率 (false positive) 约 0.1-0.5%。

**处理机制**:
1. **用户申诉**: 被删评论的用户可以点击"申诉"按钮，触发人工审核队列
2. **审核日志**: 所有审核决策 (通过/拒绝/原因/模型版本) 写入 Kafka audit log，
   支持事后分析和模型改进
3. **Shadow Mode 上线**: 新审核模型上线时先用 shadow mode (新模型判断但不执行)，
   比对新旧模型差异，确认 false positive 率可接受后再切换
4. **分级严格度**: 不同直播间可配置审核严格度 (strict/normal/relaxed)，
   教育类直播用 strict，游戏直播用 relaxed

**量化影响**: 0.1% false positive x 100K 评论/s = 100 条/s 被误删。
看起来不少，但每个用户发言频率低 (5 条/分钟)，被误删的概率很低。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1h Interview Pacing)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 1 小时面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清

"直播评论系统的核心挑战是**极高的扇出比**——一条评论需要在 2 秒内到达数百万
观众。这与聊天系统（1:1 或小群扇出）的架构完全不同。让我先确认几个关键约束。"

- 确认热门直播峰值观众数 -> 决定 Fan-out Tree 层级
- 确认是否允许评论采样 -> 影响客户端评论流速度
- 确认审核策略 (pre/post moderation) -> 影响端到端延迟
- 确认评论是否需要持久存储 -> 影响是否需要 Cassandra 写入
- 确认表情反应是否需要精确计数 -> 影响 Redis 使用方式

功能需求: 实时评论发送/接收、审核过滤、表情反应聚合、置顶评论。
非功能需求: 99.9% 可用性、P99 < 2s 延迟、100K 评论/s 写入、1000 万并发观众。
明确排除: 视频流传输、打赏、私信。

### 5-15 分钟: 高层架构

画出核心组件:
- **写入路径**: Client -> Ingestion Service -> Kafka -> Moderation -> Dispatcher
- **分发路径**: Dispatcher -> Fan-out Tree (Root -> Relays -> Edge Nodes) -> Client (SSE)
- **辅助路径**: Reaction Aggregator, Comment Store (async)

**核心架构决策 -- Fan-out Tree**:
"1000 万观众不可能用单层推送。我采用三级扇出树:
Root (1) -> Regional Relays (10) -> Edge Nodes (500) -> Clients (10M)。
每级扇出比控制在 50x 以内。Edge Node 每 500ms 批量推送一次评论，
将网络请求从 100K/s 降低到 2 pushes/s per client。"

**为什么选 SSE 而非 WebSocket**:
"评论分发是单向的（服务器到客户端）。SSE 比 WebSocket 轻量——基于 HTTP、
兼容 CDN 和 proxy、内置自动重连。评论发送走独立 HTTP POST。"

数据库选型:
- Kafka 作为评论管道 (解耦 ingestion 和 dispatch)
- Cassandra 异步持久化 (按 stream_id + time_bucket 分区)
- Redis 做速率限制、反应计数、去重

### 15-40 分钟: 深入设计 (选 2-3 个重点)

**重点 1: Fan-out Tree + 评论批处理 (10 min)**
- 三级扇出: Root -> Relay -> Edge -> Client
- 批处理: 500ms 窗口, ~50 条评论/batch, 10 KB/push
- 动态扩缩: 热门直播自动分配更多 Edge Node
- 出站带宽: 200 GB/s 分摊到 5000 Edge Node = 40 MB/s per node (可行)

**重点 2: 评论审核管道 (8 min)**
- 两级审核: 关键词 (<1ms) + ML 批处理 (~10ms)
- ML GPU 批处理: 50ms 窗口收集 5000 条, 10K QPS/instance
- 降级策略: 审核积压 > 5s 时跳过 ML, 仅关键词过滤
- 误判处理: 申诉 + audit log + shadow mode

**重点 3: 评论采样与用户体验 (7 min)**
- 100K 评论/s 全量展示导致客户端卡顿 + 不可阅读
- 采样算法: 每 500ms 窗口 Reservoir Sampling, 目标 30 条/s
- 白名单: 主播评论、被 @ 评论不采样
- 用户感知: 始终保持舒适的滚动速度, 不同观众看不同子集

### 40-50 分钟: 容量估算与权衡

容量: 1 亿并发, 500K 评论/s, 5000 Edge Nodes, 200 GB/s 出站带宽。

关键权衡:
1. **SSE vs WebSocket**: SSE 单向更轻量, 适合评论推送场景
2. **At-most-once vs at-least-once**: 直播评论可容忍丢失, 简化架构
3. **采样 vs 全量**: 采样提升用户体验且降低成本
4. **Pre-moderation vs post-moderation**: 审核延迟 10ms 可接受, 防止违规扩散
5. **成本**: ~470K USD/月, 比 Chat System (3M USD/月) 便宜 85%

### 50-55 分钟: 总结与改进方向

"如果有更多时间，我会进一步优化:
1. **CDN 边缘计算**: 将 Edge Node 逻辑下沉到 CDN (Cloudflare Workers),
   利用全球 200+ 边缘节点零部署扩展
2. **Personalized 评论流**: 基于用户兴趣/社交关系优先展示好友评论
3. **评论情感分析**: 实时统计评论的正面/负面情感比例,
   给主播展示观众情绪仪表盘
4. **评论高亮**: 自动识别高质量评论 (如提问) 并高亮展示"

监控: 评论 P99 延迟、Kafka consumer lag、Edge Node 连接数、审核延迟、
采样率、SSE 断连率。

### 55-60 分钟: 向面试官提问

准备 2-3 个展示系统设计深度的问题。

---

### 3 分钟电梯演讲版本

"Live Comments 的核心挑战是**极高扇出比**——一条评论要在 2 秒内到达 1000 万观众。

写入路径: Client -> Ingestion (HTTP POST, 速率限制) -> Kafka -> Moderation
(关键词 + ML 两级审核, ~10ms) -> Dispatcher。

分发路径: 三级 **Fan-out Tree** -- Dispatcher -> Regional Relays (10) ->
Edge Nodes (500) -> Clients (10M, SSE)。每级扇出比 < 50x。
Edge Node 每 500ms 批量推送评论, 将网络开销从 100K/s 降到 2 pushes/s per client。

关键设计决策:
- **SSE 而非 WebSocket**: 评论是单向推送, SSE 更轻量且兼容 CDN
- **评论采样**: 100K 条/s 全量展示不可阅读。每个观众看到 ~30 条/s 随机子集
- **At-most-once**: 错过一条评论可接受, 简化 Edge Node (无状态)
- **Pre-moderation**: 10ms 审核延迟 < 违规评论传播 1000 万人的风险

规模: 1 亿并发, 500K 评论/s, 5000 Edge Nodes, 200 GB/s 出站带宽,
~470K USD/月 (比 Chat System 便宜 85%, 因为 at-most-once 且单向推送)。"
"""


def populate_interview_live_comments() -> None:
    """Create or update the interview-live-comments record with all 8 sections."""
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
    populate_interview_live_comments()
