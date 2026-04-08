"""Populate interview-chat-system system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Chat System
(Messenger/WhatsApp). Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-chat-system"
TITLE = "Design a Chat System (Messenger/WhatsApp)"
DISPLAY_ORDER = 107

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **WhatsApp / Facebook Messenger** 的**即时通讯系统 (Chat System)**。
用户可以进行一对一私聊和群组聊天，消息需要实时送达，系统需要支持数亿级用户
在线并发、消息持久存储、以及离线消息投递。

### 功能性需求 (Functional Requirements)

1. **一对一聊天 (1:1 Chat)**：两个用户之间的实时文本消息收发，支持文字、
   图片、视频、文件等多种消息类型
2. **群组聊天 (Group Chat)**：支持最多 500 人的群组，群主可以管理成员，
   消息扇出给所有群成员
3. **在线状态 (Online Presence)**：展示用户是否在线、最后上线时间，
   通过心跳机制维护
4. **消息送达与已读回执 (Delivery & Read Receipts)**：消息状态三态：
   已发送 (Sent) -> 已送达 (Delivered) -> 已读 (Read)
5. **离线消息 (Offline Messages)**：用户离线时收到的消息在其上线后立即投递
6. **消息历史与同步 (Message History & Sync)**：支持多设备同步，用户换设备
   后可以拉取历史消息

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（通讯是核心体验，宕机 = 用户流失到竞品）
- **延迟 (Latency)**：消息端到端延迟 P99 < 300ms（同区域）；跨区域 < 1s
- **吞吐量 (Throughput)**：峰值消息发送 QPS ~600,000（参考 WhatsApp 日均
  1000 亿条消息）
- **一致性 (Consistency)**：消息不丢失 (**at-least-once delivery**)，
  客户端去重 (**idempotent processing**)；消息顺序在单个会话内保证
- **可扩展性 (Scalability)**：10 亿注册用户、5 亿 DAU、同时在线 ~1 亿
  **WebSocket** 连接

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 系统需要支持端到端加密 (E2E Encryption) 吗？** -- WHY: E2E 加密意味着
   服务器看不到消息明文，无法做服务端搜索/过滤，且密钥管理 (**Signal Protocol**)
   增加显著复杂度。如果需要，架构上需要引入 **Key Distribution Service**。

2. **Q: 群组的最大人数上限是多少？** -- WHY: 如果群上限 500 人（WhatsApp 模式），
   消息扇出可以同步完成；如果支持 10 万人频道（Telegram 模式），需要异步扇出
   + 分层推送策略，复杂度级别完全不同。

3. **Q: 是否需要支持多设备同时在线？** -- WHY: 多设备同步需要维护每设备独立的
   消息队列和同步游标 (**sync cursor**)，消息路由从"推到用户"变成"推到用户的
   每个设备"，写放大倍数 = 设备数。

4. **Q: 消息需要持久存储多久？** -- WHY: 如果永久存储（Facebook Messenger），
   需要冷热数据分离 + 压缩；如果限时存储（Snapchat 模式），可以用 TTL 自动清理，
   存储成本大幅降低。

5. **Q: 是否需要支持大文件传输（视频、文档）？** -- WHY: 大文件不能走
   WebSocket 消息通道，需要独立的上传服务 + **CDN** 分发 + 消息中嵌入
   文件链接。影响带宽和存储架构。

6. **Q: 消息送达率 (Delivery Rate) 的 SLA 是多少？** -- WHY: 99.9% 送达率
   可以容忍偶尔丢消息用重试补偿；99.99% 送达率需要写前日志 (**WAL, Write-Ahead
   Log**) + 多副本确认 + 客户端确认机制，显著增加系统复杂度。

7. **Q: 是否需要"正在输入" (Typing Indicator) 功能？** -- WHY: Typing
   indicator 是高频低价值信号（每次按键触发），如果要求实时推送，会产生大量
   WebSocket 流量。通常可以降低频率（每 3 秒一次）或仅对活跃会话启用。

### 范围声明 (Out of Scope)

- 语音/视频通话 (**VoIP / WebRTC**)
- 朋友圈 / Stories / 动态
- 支付 / 红包功能
- 消息内容审核与合规
- 机器人 / 自动回复 (Chatbot)
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

即时通讯系统的核心架构围绕**长连接管理 (WebSocket)**、**消息路由**和
**持久化存储**三大支柱构建。

### 核心服务与职责

| 服务 | 职责 |
|------|------|
| **Gateway Service (网关服务)** | 管理客户端 WebSocket 连接，负责协议解析、认证、连接保活 (heartbeat)、消息的序列化/反序列化 |
| **Chat Service (聊天服务)** | 核心业务逻辑：接收消息、验证、生成消息 ID、写入存储、触发扇出 |
| **Message Router (消息路由器)** | 确定消息接收方当前连接的 Gateway 节点，将消息推送到正确的 WebSocket 连接 |
| **Presence Service (在线状态服务)** | 维护用户在线/离线状态，处理心跳 (heartbeat)，广播状态变更给关注者 |
| **Group Service (群组服务)** | 群组元数据管理、成员列表维护、群消息扇出到所有成员 |
| **Sync Service (同步服务)** | 处理离线消息投递、多设备同步、历史消息拉取 |
| **Notification Service (推送服务)** | 对离线用户发送 **APNs (Apple Push Notification service)** / **FCM (Firebase Cloud Messaging)** 推送通知 |
| **Media Service (媒体服务)** | 图片/视频/文件上传存储，缩略图生成，通过 CDN 分发 |

### 数据库选型与理由

| 数据 | 存储选型 | 理由 |
|------|----------|------|
| 消息 (Messages) | **Cassandra** 或 **HBase** | 写密集型 (600K+ writes/s)、按会话 ID + 时间戳范围查询、水平扩展、无需跨分区事务 |
| 用户资料 (User Profile) | **MySQL** | 结构化数据、需要事务一致性、读多写少 |
| 群组元数据 (Group Metadata) | **MySQL** | 成员关系需要事务保护（加入/退出原子操作） |
| 在线状态 (Presence) | **Redis** | 极高读写频率 (心跳)、TTL 自动过期、内存数据库适合临时状态 |
| 消息队列 (Offline Queue) | **Redis List** 或 **Kafka** | 离线消息暂存、上线时批量拉取 |
| 媒体文件 (Media) | **S3 / Object Storage** + **CDN** | 大文件存储 + 全球分发 |

### 通信模式

- **WebSocket (双向长连接)**：客户端 <-> Gateway Service（实时消息收发的主通道）
- **HTTP REST**：客户端 -> Chat Service（历史消息拉取、群组管理等非实时操作）
- **内部 gRPC**：服务间通信（Chat Service -> Message Router、Chat Service -> Group Service）
- **异步消息队列 (Kafka)**：Chat Service -> Notification Service（离线推送）、
  Chat Service -> Sync Service（多设备同步）

### WebSocket 连接管理：核心架构决策

这是 Chat System 设计中**最核心的讨论点**。

#### 连接建立流程

```
1. Client -> Load Balancer (L4, 基于 IP hash)
2. Load Balancer -> Gateway Server (sticky session)
3. Gateway: WebSocket handshake + JWT 认证
4. Gateway: 在 Redis 中注册: user_id -> {gateway_id, connection_id}
5. 连接建立完成, 开始心跳 (每 30s 一次 ping/pong)
```

#### 连接映射 (Connection Registry)

Redis 中维护用户到 Gateway 的映射：

```
Key: "conn:{user_id}"
Value: {
  "gateway_id": "gw-us-east-042",
  "connection_id": "ws-abc123",
  "connected_at": 1705312000,
  "last_heartbeat": 1705315600,
  "device_type": "mobile"
}
TTL: 90s (3x heartbeat interval, auto-expire if heartbeat stops)
```

多设备场景下，每个设备一条记录：
```
Key: "conn:{user_id}:{device_id}"
```

#### 消息路由流程

```
User A sends message to User B:
1. A's device -> A's Gateway (via WebSocket)
2. A's Gateway -> Chat Service (gRPC)
3. Chat Service:
   a. 生成全局唯一消息 ID (Snowflake)
   b. 写入 Message Store (Cassandra)
   c. 查询 Redis: B 的 Gateway 地址
   d. 如果 B 在线: 通过 gRPC 推送到 B 的 Gateway -> B 的 WebSocket
   e. 如果 B 离线: 写入 offline queue + 发送 Push Notification
4. B's Gateway -> B's device (via WebSocket)
5. B's device -> ACK (已收到) -> Chat Service 更新消息状态
```

### 数据分区策略

- **Message Store (Cassandra)**：按 `conversation_id` 分区，同一会话的消息
  在同一分区内按 `message_id` (时间有序) 排列
- **User Profile (MySQL)**：按 `user_id` 哈希分片
- **Presence (Redis)**：按 `user_id` 一致性哈希分片
- **Connection Registry (Redis)**：按 `user_id` 分片，与 Presence 共用集群或独立集群
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### WebSocket 消息协议

Chat 系统的核心通信走 WebSocket，消息格式采用二进制 **Protocol Buffers** 或
JSON（取决于性能需求）。

#### 发送消息 (Client -> Server)

```json
{
  "type": "message.send",
  "request_id": "req_abc123",
  "data": {
    "conversation_id": "conv_789",
    "content": "Hey, are you free tonight?",
    "content_type": "text",
    "client_message_id": "cm_xyz456"
  }
}
```

#### 接收消息 (Server -> Client)

```json
{
  "type": "message.new",
  "data": {
    "message_id": "msg_1705315600_001",
    "conversation_id": "conv_789",
    "sender_id": "user_alice",
    "content": "Hey, are you free tonight?",
    "content_type": "text",
    "sent_at": "2024-01-15T18:00:00Z"
  }
}
```

#### 消息确认 (Client -> Server)

```json
{
  "type": "message.ack",
  "data": {
    "message_id": "msg_1705315600_001",
    "status": "delivered"
  }
}
```

### REST API 端点

#### 1. 拉取历史消息

```
GET /v1/conversations/{conversation_id}/messages?cursor=<cursor>&limit=50
Authorization: Bearer <token>

Response: 200 OK
{
  "messages": [
    {
      "message_id": "msg_1705315600_001",
      "sender_id": "user_alice",
      "content": "Hey!",
      "content_type": "text",
      "sent_at": "2024-01-15T18:00:00Z",
      "status": "read"
    }
  ],
  "next_cursor": "cursor_msg_1705315500",
  "has_more": true
}
```

#### 2. 创建群组

```
POST /v1/groups
Authorization: Bearer <token>

Request Body:
{
  "name": "Weekend Hiking",
  "member_ids": ["user_bob", "user_carol", "user_dave"],
  "avatar_url": "https://cdn.example.com/group_avatar.jpg"
}

Response: 201 Created
{
  "group_id": "grp_abc789",
  "name": "Weekend Hiking",
  "member_count": 4,
  "created_at": "2024-01-15T18:30:00Z"
}
```

#### 3. 更新在线状态

```
POST /v1/presence/heartbeat
Authorization: Bearer <token>

Request Body:
{
  "status": "online",
  "device_id": "dev_iphone_001"
}

Response: 200 OK
{
  "next_heartbeat_in_seconds": 30
}
```

### 核心数据模型

#### Message 表 (Cassandra)

```
CREATE TABLE messages (
    conversation_id TEXT,
    message_id      BIGINT,   -- Snowflake ID (time-ordered)
    sender_id       TEXT,
    content         TEXT,
    content_type    TEXT,      -- text, image, video, file
    media_url       TEXT,
    status          TEXT,      -- sent, delivered, read
    created_at      TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

#### Conversation 表 (MySQL)

```sql
CREATE TABLE conversations (
    conversation_id  VARCHAR(64) PRIMARY KEY,
    type             ENUM('direct', 'group'),
    created_at       DATETIME,
    updated_at       DATETIME,
    last_message_id  BIGINT,
    last_message_at  DATETIME
);

CREATE TABLE conversation_members (
    conversation_id  VARCHAR(64),
    user_id          VARCHAR(64),
    joined_at        DATETIME,
    last_read_id     BIGINT,      -- cursor for read receipts
    muted            BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (conversation_id, user_id)
);
```

### 读路径 (Read Path)：获取历史消息

```
1. Client:
   a. 发送 GET /v1/conversations/{conv_id}/messages?cursor=xxx&limit=50

2. Chat Service:
   a. 验证用户是该会话的成员 (查 conversation_members)
   b. 从 Cassandra 按 conversation_id 分区查询:
      SELECT * FROM messages
      WHERE conversation_id = ? AND message_id < ?
      ORDER BY message_id DESC LIMIT 50
   c. 批量获取发送者信息 (User Profile Cache)
   d. 组装响应, 生成 next_cursor

3. 返回给客户端
```

### 写路径 (Write Path)：发送消息

```
1. Client -> Gateway (WebSocket):
   a. 发送 message.send 包含 client_message_id (客户端去重 ID)

2. Gateway -> Chat Service (gRPC):
   a. 校验参数、鉴权、检查用户是会话成员
   b. 幂等检查: 用 client_message_id 查 Redis 是否已处理 (防重复提交)
   c. 生成全局唯一 message_id (Snowflake ID)

3. Chat Service -> Message Store:
   a. 写入 Cassandra (messages 表)
   b. 更新 conversations.last_message_id (MySQL, 异步可)

4. Chat Service -> Message Router:
   a. 1:1 聊天: 查 Redis 获取接收方 Gateway 地址, 推送消息
   b. 群聊: 查群成员列表 -> 批量查各成员 Gateway -> 逐一推送
   c. 离线成员: 写入 offline_queue (Redis List) + 触发 Push Notification

5. 接收方 Client -> ACK:
   a. Client 收到消息后发送 message.ack (status=delivered)
   b. Chat Service 更新 messages.status = 'delivered'
   c. 推送 delivery receipt 给发送方
```

### 异步路径

- **离线推送**：Chat Service -> Kafka "push.notification" -> Notification Service
  -> APNs / FCM（每条消息一条推送，或批量合并"N 条新消息"）
- **媒体处理**：Client -> Media Service (HTTP upload) -> S3 -> 返回 media_url
  -> Client 在 WebSocket 消息中附带 media_url
- **已读回执**：Client 打开会话 -> 发送 message.read (last_read_id) ->
  Chat Service 更新 conversation_members.last_read_id -> 推送 read receipt 给对方
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 基础数据假设

| 指标 | 数值 |
|------|------|
| 注册用户 | 10 亿 |
| DAU | 5 亿 |
| 同时在线 (Peak) | 1 亿 |
| 每用户日均消息数 | 40 条 (发送 + 接收) |
| 日均消息总量 | 1000 亿条 (WhatsApp 参考数据) |
| 平均消息大小 | 100 bytes (纯文本) |
| 媒体消息比例 | 15% (平均大小 200 KB) |
| 平均群组大小 | 10 人 |
| 每用户平均会话数 | 20 个 |

### QPS 估算

**消息写入 QPS**:

$$Q_{write} = \frac{100{,}000{,}000{,}000}{86{,}400} \approx 1{,}157{,}000 \text{ QPS (avg)}$$

$$Q_{write\_peak} = 1{,}157{,}000 \times 3 \approx 3{,}500{,}000 \text{ QPS (peak)}$$

注意：上述是全局消息投递量（含群聊扇出）。实际**发送** QPS 约为:

$$Q_{send} = \frac{100B \div 2.5 \text{ (avg fan-out)}}{86{,}400} \approx 460{,}000 \text{ QPS (avg send)}$$

$$Q_{send\_peak} = 460{,}000 \times 1.5 \approx 690{,}000 \text{ QPS}$$

**WebSocket 连接数**:

$$C_{websocket} = 100{,}000{,}000 \text{ concurrent connections (peak)}$$

每个 Gateway 服务器可维持约 50,000 个 WebSocket 连接：

$$N_{gateway} = \frac{100{,}000{,}000}{50{,}000} = 2{,}000 \text{ Gateway servers}$$

### 存储估算

**消息存储 (Cassandra)**:

文本消息:

$$S_{text} = 100B \times 0.85 \times 100 \text{ bytes} = 8.5 \text{ TB/day}$$

媒体消息元数据（媒体文件本身在 S3）:

$$S_{media\_meta} = 100B \times 0.15 \times 200 \text{ bytes} = 3 \text{ TB/day}$$

$$S_{messages\_daily} = 8.5 + 3 = 11.5 \text{ TB/day}$$

$$S_{messages\_yearly} = 11.5 \times 365 = 4.2 \text{ PB/year}$$

**媒体文件存储 (S3)**:

$$S_{media} = 100B \times 0.15 \times 200 \text{ KB} = 3 \text{ PB/day}$$

$$S_{media\_yearly} = 3 \times 365 \approx 1{,}095 \text{ PB/year} \approx 1.1 \text{ EB/year}$$

（WhatsApp 实际数据：约 55B 条图片/天 x 100-300 KB = ~10 PB/day）

**连接状态 (Redis)**:

$$S_{presence} = 100{,}000{,}000 \times 256 \text{ bytes} = 25.6 \text{ GB}$$

**离线消息队列 (Redis)**:

假设平均 10% 用户离线时有 50 条待投递消息:

$$S_{offline} = 50{,}000{,}000 \times 50 \times 200 \text{ bytes} = 500 \text{ GB}$$

### 带宽估算

**WebSocket 入站 (Client -> Server)**:

$$BW_{in} = 690{,}000 \times 200 \text{ bytes} = 138 \text{ MB/s} \approx 1.1 \text{ Gbps}$$

**WebSocket 出站 (Server -> Client)**:

包含群聊扇出的放大效应:

$$BW_{out} = 3{,}500{,}000 \times 200 \text{ bytes} = 700 \text{ MB/s} \approx 5.6 \text{ Gbps}$$

### 核心算法

#### Snowflake ID 生成

64-bit 消息 ID，天然有序:

```
| 1 bit (unused) | 41 bits (timestamp ms) | 10 bits (machine ID) | 12 bits (sequence) |
```

- 41 bits timestamp: 可用约 69 年
- 10 bits machine ID: 最多 1024 个 ID 生成器节点
- 12 bits sequence: 每毫秒每节点 4096 个 ID
- 总容量: $4096 \times 1000 \times 1024 = 4.19B \text{ IDs/sec}$

#### 消息去重 (Idempotency)

客户端为每条消息生成 `client_message_id` (UUID)，服务端使用 Redis 做幂等检查:

```
SETNX "dedup:{client_message_id}" 1 EX 300
```

如果 SETNX 返回 0 (key 已存在)，说明是重复消息，跳过处理。TTL 5 分钟覆盖
网络重试窗口。

#### 心跳与在线状态判定

```
Client: 每 30s 发送 ping
Server: 回复 pong, 更新 Redis TTL

Redis key: "presence:{user_id}"
  value: {"status": "online", "last_seen": timestamp, "gateway_id": "gw-042"}
  TTL: 90s (3x heartbeat interval)

判定逻辑:
- Key 存在且 status=online -> 在线
- Key 存在且已过期 -> 刚刚离线 (show "last seen X ago")
- Key 不存在 -> 离线
```

### 服务器数量估算

| 组件 | 计算 | 数量 |
|------|------|------|
| Gateway (WebSocket) | 100M connections / 50K per server | ~2,000 服务器 |
| Chat Service | 690K QPS / 20K per instance | ~35 实例 |
| Message Router | 3.5M deliveries/s / 50K per instance | ~70 实例 |
| Cassandra (Messages) | 11.5 TB/day, RF=3 | ~300 节点 |
| Redis (Presence + Offline) | 26 GB + 500 GB, 64 GB/node | ~10 节点 |
| MySQL (User/Group) | 读多写少, 8 shards | ~16 实例 (含副本) |
| Media Service | 峰值 150K uploads/s | ~30 实例 |

### 月度成本估算

| 项目 | 月度费用 |
|------|----------|
| Gateway 2000 台 (c6g.xlarge) | ~300,000 USD |
| Cassandra 300 节点 (i3.2xlarge) | ~250,000 USD |
| Redis 10 节点 (r6g.2xlarge) | ~3,000 USD |
| MySQL 16 实例 (r6g.xlarge) | ~4,000 USD |
| S3 (3 PB/day, lifecycle) | ~2,000,000+ USD |
| CDN (媒体分发) | ~500,000 USD |
| 计算 (Chat/Router/Media) | ~20,000 USD |
| **总计** | **~3,000,000+ USD/月** |

（注意: 这是 WhatsApp 规模估算。WhatsApp 以极精简团队著称，实际通过 Erlang/OTP
的高并发能力和自研存储大幅降低了硬件需求。中型应用可缩减 2-3 个数量级）
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints -- Scale & Reliability)

### 具体规模参数

| 指标 | 数值 |
|------|------|
| 注册用户 | 10 亿 |
| DAU | 5 亿 |
| 同时在线 (Peak) | 1 亿 |
| WebSocket 连接数 | 1 亿 |
| 消息发送 QPS (峰值) | ~690,000 |
| 消息投递 QPS (含扇出, 峰值) | ~3,500,000 |
| Message Store 日增 | 11.5 TB |
| 媒体存储日增 | ~3 PB |

### 单点故障分析 (SPOF Analysis)

| 组件 | 风险 | 缓解措施 |
|------|------|----------|
| Gateway (WebSocket) | 单台 Gateway 宕机断开 50K 连接 | 客户端自动重连 + L4 LB 重新分配到健康节点；连接映射 TTL 90s 自动清理 |
| Chat Service | 服务宕机消息无法处理 | 无状态服务, K8s 自动扩缩容, 多副本 |
| Message Store (Cassandra) | 节点宕机 | RF=3 (三副本), 一致性级别 QUORUM: 容忍 1 节点故障 |
| Redis (Presence) | 实例宕机导致在线状态丢失 | Redis Sentinel 自动故障转移; 状态丢失后客户端下次心跳自动恢复 |
| Kafka | Broker 宕机 | 3 副本 + ISR, 单 Broker 故障不丢消息 |
| MySQL (User/Group) | 主库宕机 | 每分片 1 主 2 从, 半同步复制, 自动故障转移 < 30s |

### 多数据中心 / 跨区域 (Multi-DC)

**架构: Active-Active (双活/多活)**

- **DNS 层**: **GeoDNS** 将用户路由到最近的数据中心
- **WebSocket 连接**: 用户连接到最近 DC 的 Gateway，连接映射在全局 Redis 中注册
- **消息路由 (跨 DC)**:
  - 同 DC 消息: Gateway -> Chat Service -> local Router -> local Gateway (延迟 < 50ms)
  - 跨 DC 消息: Chat Service 发现接收方在其他 DC -> 通过**跨 DC 消息总线
    (Inter-DC Message Bus)** 转发到目标 DC 的 Router -> 目标 Gateway
  - 跨 DC 延迟: 额外 50-150ms (取决于地理距离)
- **数据复制**:
  - Cassandra: 天然多 DC 支持 (**NetworkTopologyStrategy**, 每 DC 3 副本)
  - MySQL: 跨 DC 异步复制 (主 DC 写入, 其他 DC 延迟 < 500ms)
  - Redis: 每个 DC 独立 Redis 集群 (Presence 是本地状态，不需要跨 DC 同步)

**故障切换 (Failover)**:
- 单 DC 故障时，DNS 权重自动切换到其他 DC (TTL=30s)
- 用户 WebSocket 断开后自动重连到新 DC
- 消息不丢失: Cassandra 跨 DC 副本保证持久性
- 在线状态短暂丢失: 用户重连后自动恢复 (心跳重建)

### 高并发处理

1. **连接管理优化**:
   - 使用 **epoll** (Linux) / **IOCP** (Windows) 实现高效事件驱动 I/O
   - 每台 Gateway 50K 连接，使用 Netty / Go goroutine / Erlang process
   - 内存优化: 每连接内存控制在 10-20 KB (50K connections = 500 MB - 1 GB)

2. **速率限制 (Rate Limiting)**:
   - 消息发送: 30 messages/sec/user (防刷屏)
   - 群组消息: 20 messages/sec/user/group
   - 连接建立: 5 connections/min/IP (防 DDoS)
   - 全局限流: Kafka 消费速率按 consumer group 限制

3. **熔断器 (Circuit Breaker)**:
   - Cassandra 写入延迟 > 500ms -> 熔断, 消息暂存 Kafka 稍后重试
   - Notification Service 超时 -> 熔断, 离线推送延迟发送
   - Media Service 故障 -> 文本消息正常, 媒体上传返回"稍后重试"

4. **优雅降级 (Graceful Degradation)**:
   - **Level 1**: Ranking/推荐功能降级（群推荐、联系人推荐关闭）
   - **Level 2**: 在线状态服务降级（不显示在线/离线，但消息正常收发）
   - **Level 3**: 已读回执降级（消息仍然送达，但不更新 read receipts）
   - **Level 4**: 媒体消息暂停（只允许文本消息，减少带宽和存储压力）

### 监控与告警 (Monitoring & Alerting)

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 消息端到端延迟 P99 | > 300ms | P1 (Warning) |
| 消息端到端延迟 P99 | > 2s | P0 (Critical) |
| WebSocket 断连率 | > 1%/min | P1 |
| Cassandra 写入延迟 P99 | > 100ms | P1 |
| 离线消息队列深度 | > 1M messages | P1 |
| Gateway 连接数 | > 45K/server (90% capacity) | P2 (Scale-up) |
| 消息送达率 | < 99.9% | P0 |
| Redis 内存使用率 | > 80% | P1 |

### 消息送达保证 (Delivery Guarantee)

实现 **at-least-once delivery** + 客户端去重:

1. **发送方 -> Server**: 客户端发送消息后等待 Server ACK；未收到则重试
   (带 `client_message_id` 去重)
2. **Server -> 接收方**: Server 推送消息后等待 Client ACK (`delivered` status)；
   未收到则定期重推 (指数退避, 最多 5 次)
3. **离线补偿**: 用户上线后，Sync Service 拉取 offline_queue 中所有待投递消息，
   批量推送
4. **最终兜底**: 客户端定期 (每 5 min) 向 Server 发送同步请求，比较本地
   最新 message_id 与 Server 端，拉取缺失消息
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **传输协议** | HTTP Long Polling | WebSocket | **WebSocket**: 全双工低延迟，适合聊天场景。Long Polling 每次请求建立新连接开销大，延迟高 (~1s vs ~50ms)。WebSocket 的缺点是连接管理复杂，但对于聊天系统这是值得的投资 |
| **消息存储** | MySQL (分库分表) | Cassandra (NoSQL) | **Cassandra**: 写吞吐量需求极高 (3.5M/s)，MySQL 即使分片也难以承受。Cassandra 天然水平扩展、按 partition key 有序存储、多 DC 复制内置支持。缺点是不支持复杂查询，但聊天消息的查询模式简单 (按 conversation_id + time range) |
| **送达保证** | At-most-once (Fire and forget) | At-least-once + Dedup | **At-least-once + Dedup**: 聊天消息丢失对用户体验是灾难性的。虽然 at-least-once 需要客户端去重逻辑 (基于 client_message_id)，但实现成本远低于消息丢失带来的用户信任损失 |
| **群消息扇出** | 写时扇出 (Write) | 读时扇出 (Read) | **写时扇出**: 群上限 500 人，每条消息最多 500 次写入可接受。读时扇出需要每个读者查询群消息表 + 合并，延迟高且计算密集。500 人 x 写放大 vs 百万次/天 x 读放大，写放大更可控 |
| **在线状态方案** | 实时广播 | 延迟聚合 | **延迟聚合 + 按需查询**: 实时广播每次状态变更通知所有好友 (如 200 好友)，流量巨大。改为: 用户打开会话时查询对方状态，列表页每 30s 批量查询可见好友状态。牺牲少许实时性，节省 >90% 状态推送流量 |

### CAP 定理应用

Chat System 选择 **AP (Availability + Partition Tolerance)**:

- **Partition 发生时**: 两个 DC 各自继续服务消息收发。同 DC 用户间消息正常；
  跨 DC 消息暂时无法投递，暂存在发送方 DC 的 Kafka 中
- **Partition 恢复后**: Kafka 跨 DC 同步自动补发积压消息；Cassandra 跨 DC
  副本通过 **read repair** 和 **anti-entropy** 最终一致
- **不选 CP 的原因**: 如果为了一致性拒绝服务（聊天功能不可用），用户会立即
  转向竞品。一条消息延迟几秒送达远好于"服务暂不可用"

**唯一的强一致性需求**: 消息 ID 生成。每条消息的 Snowflake ID 必须全局唯一且
单调递增（在同一节点内）。这通过本地时钟 + 序列号保证，不依赖分布式共识。

### 成本 vs 性能

| 层次 | 低成本方案 | 高性能方案 | 我们的平衡点 |
|------|-----------|-----------|-------------|
| WebSocket 连接 | HTTP Long Polling (无状态, 便宜) | WebSocket (有状态, 需要更多服务器) | WebSocket: 延迟差异是 50ms vs 1s，聊天场景必须选 WebSocket |
| 消息存储 | HDD + 压缩 (便宜但慢) | SSD + 内存缓存 (快但贵) | 热数据 (7 天) SSD + 冷数据 (>7 天) HDD + 压缩。90% 查询命中热数据 |
| 在线状态 | 按需查询 (无额外成本) | 实时推送 (高 WebSocket 流量) | 延迟聚合: 列表页 30s 轮询，聊天页按需查询 |
| 媒体存储 | 原始文件直存 S3 | 多分辨率 + CDN 预热 | 3 种分辨率 (缩略图/标准/原图)，热门媒体 CDN 缓存 |

### 10x / 100x 扩展时的变化

**10x (50 亿 DAU, 10 亿同时在线)**:
- Gateway 需要 20,000 台 -> 考虑用 Erlang/BEAM VM（WhatsApp 路线, 单机 200 万连接）
- Cassandra 集群需要 3000+ 节点 -> 按区域分集群，会话数据只存本区域
- 群聊扇出对大群组 (>100 人) 改为异步 + Kafka，小群组 (<100) 保持同步
- 需要自研消息存储引擎替代 Cassandra（参考 Facebook 用 MyRocks）

**100x (全球级 + 超级群/频道)**:
- 支持 10 万人频道需要完全不同的架构: 发布-订阅模式 + CDN 式消息分发
- 媒体存储成为天文数字 -> 自建存储 + P2P 分发 (如 IPFS 概念)
- 消息存储考虑分层: 热 (SSD, 7天) -> 温 (HDD, 1年) -> 冷 (Glacier, 永久)
- 各国数据合规要求不同 -> 需要按国家/区域做数据隔离 (Data Residency)
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个 Gateway 服务器突然宕机，50K 用户的连接断开，会发生什么？

**承认影响**: 50K 用户会瞬间断连，短暂无法收发消息。

**缓解措施**:
1. **客户端自动重连**: 移动端 SDK 内置指数退避重连逻辑 (1s, 2s, 4s, 8s...)，
   L4 Load Balancer 将重连请求分配到其他健康 Gateway
2. **连接映射自动清理**: Redis 中的连接注册 TTL=90s，宕机 Gateway 的映射
   自然过期，不需要主动清理
3. **消息不丢失**: 断连期间发给这些用户的消息进入 offline_queue，
   用户重连后 Sync Service 立即投递
4. **平滑运维**: 计划维护时用 **Connection Draining (连接排空)**: 先停止
   新连接接入，等现有连接心跳超时后自然释放，再下线服务器

**恢复时间**: 多数用户在 3-10 秒内自动重连成功。

### Q2: 一个 500 人群里同时发消息，消息顺序如何保证？

**关键洞察**: 我们保证**单个发送者的消息顺序**，但**不保证不同发送者之间的全局顺序**。

**原因**:
1. 不同用户的消息到达服务器的时间本身就是不确定的（网络延迟不同）
2. 强制全局排序需要分布式共识（如 Paxos/Raft），延迟会从 ms 级升到 100ms 级
3. 实际用户体验中，聊天消息不需要严格全局顺序——用户感知的"顺序"是看到消息
   的先后，而非绝对时间戳

**我们的保证**:
1. **单发送者顺序**: 同一用户的连续消息使用递增的 Snowflake ID，存储时按
   message_id 排序，天然保序
2. **因果顺序 (Causal Ordering)**: 回复消息携带 `reply_to_id`，客户端渲染时
   保证被回复消息在回复之前显示
3. **客户端排序**: 群消息按 `message_id` (包含时间戳) 排序，不同发送者的消息
   按到达服务器的时间交错显示

### Q3: 如何处理消息送达失败的情况？比如用户设备网络差，消息一直送不到。

**多层保障机制**:

1. **即时重试 (Server-side)**:
   - 推送消息后等待 Client ACK，5 秒未收到则重试
   - 指数退避: 5s, 10s, 20s, 40s, 80s，最多 5 次
   - 每次重试携带相同的 `message_id`，客户端根据 ID 去重

2. **离线队列 (Offline Queue)**:
   - 5 次重试失败 -> 消息放入 offline_queue (Redis List)
   - 同时发送 Push Notification (APNs/FCM) 提醒用户

3. **上线同步 (Online Sync)**:
   - 用户重连后，Sync Service 批量拉取 offline_queue
   - 按 message_id 顺序投递，每条等待 ACK 后再发下一条

4. **定期同步 (Periodic Sync)**:
   - 客户端每 5 分钟发送同步请求: "我最新的消息 ID 是 X"
   - Server 比较后推送所有 > X 的消息
   - 这是最终兜底机制，确保即使前面所有机制失败也能最终送达

**送达率 SLA**: 通过以上四层机制，消息送达率 > 99.99%。

### Q4: 如果流量突然暴增 10 倍（比如新年倒计时全民发消息），系统怎么应对？

**预防措施 (事前)**:
1. **预扩展**: 已知的流量高峰 (新年、世界杯)，提前 2 小时扩容 Gateway 和
   Chat Service 到预期 2 倍容量
2. **压力测试**: 每季度进行一次全链路压测，验证 3 倍峰值承载能力
3. **容量缓冲**: 正常运行时保持 40% 余量 (60% utilization target)

**实时应对 (事中)**:
1. **自动扩缩容**: K8s HPA (Horizontal Pod Autoscaler) 基于 CPU/连接数自动扩容，
   扩容延迟 < 2 分钟
2. **流量限流**: 超过阈值时触发限流 —— 非核心功能限流 (typing indicator, online
   presence broadcast)，核心消息收发不限流
3. **消息队列缓冲**: Kafka 作为缓冲层，峰值消息先进 Kafka，Cassandra 按自身
   能力消费，允许写入延迟从 10ms 升到 100ms
4. **降级策略**: 极端情况下依次关闭: 已读回执 -> 在线状态 -> 媒体消息 ->
   只保留纯文本消息

### Q5: 端到端加密 (E2E Encryption) 如何影响系统架构？

**核心变化**: 服务器变成"盲转发者"——无法读取消息明文。

**实现方案 (Signal Protocol)**:
1. **密钥交换**: 使用 **X3DH (Extended Triple Diffie-Hellman)** 建立会话密钥
2. **消息加密**: 使用 **Double Ratchet Algorithm** 逐条消息加密，每条消息
   使用不同的对称密钥
3. **密钥存储**: 每个设备生成 Identity Key Pair，公钥注册到 **Key Distribution
   Server**；私钥只存在设备本地

**架构影响**:
- 服务器存储的是加密后的密文 -> 大小增加约 10-20% (加密开销 + IV + MAC)
- **无法做服务端搜索**: 搜索历史消息需要在客户端本地进行
- **无法做内容审核**: 需要依赖用户举报而非自动扫描
- **多设备同步复杂化**: 每个设备需要独立的加密会话，消息需要为每个设备
  分别加密 (写放大 = 设备数)
- **群聊加密**: 使用 **Sender Keys** 方案——群主分发共享密钥，
  每条群消息只需加密一次
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1h Interview Pacing)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 1 小时面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清

"即时通讯系统的核心挑战是**长连接管理**、**消息可靠送达**和**在线状态维护**。
让我先确认几个关键约束。"

- 确认用户规模（亿级 DAU）和同时在线数 -> 决定 WebSocket Gateway 架构
- 确认是否需要 E2E 加密 -> 影响服务器角色（明文处理 vs 盲转发）
- 确认群聊规模上限 -> 影响消息扇出策略（同步 vs 异步）
- 确认消息持久化需求 -> 影响存储选型和成本
- 确认多设备同步需求 -> 影响消息路由复杂度

功能需求: 1:1 聊天、群聊、在线状态、送达/已读回执、离线消息、多设备同步。
非功能需求: 99.99% 可用性、P99 < 300ms、5 亿 DAU、1 亿并发连接。
明确排除: 语音/视频通话、Stories、支付。

### 5-15 分钟: 高层架构

画出核心组件:
- **长连接层**: Client <-> L4 LB <-> Gateway (WebSocket) <-> Redis (Connection Registry)
- **消息层**: Gateway -> Chat Service -> Cassandra (Messages) + Router -> Gateway -> Client
- **辅助服务**: Presence Service, Group Service, Notification Service, Sync Service

**核心架构决策 -- WebSocket 连接管理**:
"每台 Gateway 维持约 50K WebSocket 连接，1 亿并发需要 2000 台 Gateway。
用户连接时在 Redis 注册 user_id -> gateway_id 映射，TTL 90s 随心跳刷新。
发消息时通过 Redis 查找接收方的 Gateway，直接 gRPC 推送。这比消息队列模式
延迟低 (50ms vs 200ms+)，因为省去了队列消费的额外跳转。"

数据库选型:
- Cassandra 存消息 (写密集 + 水平扩展 + 多 DC)
- MySQL 存用户和群组 (结构化 + 事务)
- Redis 存连接映射 + 在线状态 + 离线队列 (低延迟 + TTL)
- S3 + CDN 存媒体文件

### 15-40 分钟: 深入设计 (选 2-3 个重点)

**重点 1: 消息送达保证 (10 min)**
- At-least-once delivery + 客户端去重 (client_message_id)
- 四层保障: 即时推送 -> 重试 (指数退避, 5次) -> 离线队列 -> 定期同步
- Snowflake ID 保证消息有序 + 全局唯一
- 幂等处理: Redis SETNX dedup:{client_message_id} EX 300

**重点 2: 群聊消息扇出 (8 min)**
- 群上限 500 人 -> 写时扇出可行 (每条消息最多 500 次推送)
- 扇出流程: Chat Service -> Group Service (获取成员列表) ->
  批量查 Redis 连接映射 -> 在线成员直推，离线成员入 offline_queue
- 优化: Pipeline 批量查 Redis，并行推送到多个 Gateway
- 群消息只存一份 (Cassandra，partition key = conversation_id)，不做每用户副本

**重点 3: 在线状态服务 (7 min)**
- 心跳机制: 客户端每 30s ping，Redis key TTL=90s
- 延迟聚合策略: 不实时广播状态变更，改为按需查询 + 列表页 30s 轮询
- 流量节省: 200 好友 x 每次状态变更广播 vs 打开聊天页时单次查询，节省 >90% 流量
- 大规模优化: 只维护"双向好友"的状态订阅，非好友不推送

### 40-50 分钟: 容量估算与权衡

容量: 5 亿 DAU, 1000 亿条/天, 2000 台 Gateway, 300 节点 Cassandra。

关键权衡:
1. **传输协议**: WebSocket 是唯一合理选择 (50ms vs 1s)
2. **存储**: Cassandra 写吞吐优势明显 (3.5M writes/s)
3. **送达保证**: At-least-once + dedup (消息不丢 > 去重成本)
4. **在线状态**: 延迟聚合节省 90%+ 流量
5. **成本**: ~3M USD/月在 WhatsApp 规模

### 50-55 分钟: 总结与改进方向

"如果有更多时间，我会进一步优化:
1. **E2E 加密**: Signal Protocol (X3DH + Double Ratchet)
2. **消息搜索**: 全文搜索需要在客户端本地实现 (E2E 场景) 或用 Elasticsearch (非 E2E)
3. **超级群/频道**: 10 万人频道需要 pub-sub 架构 + CDN 式消息分发
4. **消息撤回**: 软删除 + 推送撤回通知给已接收的客户端"

监控: 消息 P99 延迟、送达率、WebSocket 断连率、Cassandra 写延迟、离线队列深度。

### 55-60 分钟: 向面试官提问

准备 2-3 个展示系统设计深度的问题。

---

### 3 分钟电梯演讲版本

"Chat System 的核心是**WebSocket 长连接管理**和**消息可靠送达**。
1 亿并发连接分布在 2000 台 Gateway 上，每台 50K 连接。
用户连接时在 Redis 注册映射 (user_id -> gateway_id, TTL=90s)。

发消息时 Chat Service 生成 Snowflake ID、写入 Cassandra (partition by conversation_id)，
然后查 Redis 找到接收方 Gateway 直接 gRPC 推送。离线用户消息进 Redis 队列 +
APNs/FCM 推送通知。

消息送达用 at-least-once + 客户端去重: 即时推送 -> 重试 -> 离线队列 -> 定期同步，
四层保障实现 99.99%+ 送达率。

群聊 (上限 500) 用写时扇出，查成员列表后批量推送。
在线状态用 Redis TTL 心跳 + 延迟聚合，节省 90% 推送流量。

规模: 5 亿 DAU, 1000 亿消息/天, 11.5 TB/day Cassandra, 3 PB/day 媒体。
多 DC Active-Active + AP 一致性。月度成本约 3M USD (WhatsApp 规模)。"
"""


def populate_interview_chat_system() -> None:
    """Create or update the interview-chat-system record with all 8 sections."""
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
    populate_interview_chat_system()
