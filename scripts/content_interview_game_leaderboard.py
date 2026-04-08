"""Populate interview-game-leaderboard system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Real-time
Game Leaderboard. Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-game-leaderboard"
TITLE = "Design a Real-time Game Leaderboard"
DISPLAY_ORDER = 105

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**实时游戏排行榜系统 (Real-time Game Leaderboard)**，类似
**Steam Leaderboard** / **Clash Royale 排行榜** / **PUBG 排名系统**。
系统需要支持数百万玩家的实时积分更新、全局排名查询 (Top-K)、
单个玩家排名查询 (Rank Lookup)、以及按日/周/赛季的多时间维度排行榜。
排名需要在积分更新后秒级生效。

### 功能性需求 (Functional Requirements)

1. **积分上报 (Score Update)**：游戏服务器在对局结束后上报玩家积分变化，
   系统实时更新玩家总分
2. **全局 Top-K 查询 (Global Top-K)**：查询排行榜前 N 名（如 Top-100），
   返回玩家 ID、昵称、积分、排名
3. **玩家排名查询 (Rank Lookup)**：查询某个玩家当前在排行榜中的精确排名
4. **相对排名 (Relative Ranking)**：查询某个玩家前后各 N 名玩家（"我周围的人"）
5. **多时间维度 (Time-based Boards)**：支持日榜、周榜、赛季榜（all-time），
   日榜/周榜在周期结束后自动归档重置

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**：99.99%（排行榜是核心游戏体验，不可用影响用户留存）
- **延迟 (Latency)**：积分更新 P99 < 50ms；Top-K 查询 P99 < 100ms；
  Rank Lookup P99 < 100ms
- **吞吐量 (Throughput)**：峰值积分更新 QPS ~50,000；排名查询 QPS ~100,000
- **一致性 (Consistency)**：排名需最终一致，积分更新后 < 1 秒内反映到排行榜
- **可扩展性 (Scalability)**：支撑 5000 万注册玩家、500 万 DAU、多个独立排行榜

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 排行榜的玩家规模是多少？** -- WHY: 如果是百万级，单机 Redis
   **Sorted Set** 即可应对；如果是十亿级，需要分片 (Sharding) 策略，
   系统复杂度截然不同。

2. **Q: 积分是单调递增的还是可以减少？** -- WHY: 单调递增可以用更简单的数据结构
   （如 **Segment Tree**），如果积分可增可减则必须用支持任意更新的有序集合。

3. **Q: 排名需要实时还是可以有延迟？延迟容忍度是多少？** -- WHY: 如果容忍
   5-10 秒延迟，可以用批量异步计算；如果要求亚秒级实时，需要 Redis Sorted Set
   这样的 O(log N) 在线更新方案。

4. **Q: 是否需要支持同分排序 (Tie-breaking)？** -- WHY: 如果两个玩家分数相同，
   是并列同名次，还是先达到的排前面？决定了积分编码方式和排序策略。

5. **Q: 是否有多个独立排行榜（不同游戏/模式/区服）？** -- WHY: 多排行榜意味着
   数据隔离需求，影响 Redis key 设计和分片策略。

6. **Q: 日榜/周榜的重置逻辑是怎样的？** -- WHY: 如果需要归档历史数据以供回看，
   重置不能简单删除，需要快照 + 新建。

7. **Q: 排行榜需要展示多少额外信息（头像、战绩等）？** -- WHY: 如果 Top-K
   查询需要返回丰富的玩家资料，排行榜层只存 ID+分数，详情需要额外查询用户服务，
   影响查询链路设计。

### 范围外 (Out of Scope)

- 游戏匹配系统 (Matchmaking)
- 积分计算逻辑（假设游戏服务器已计算好积分变化量）
- 反作弊系统（假设上报积分已经过验证）
- 社交功能（好友排行榜暂不考虑）
- 奖励发放系统
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 核心组件 (Core Components)

```
Game Servers (积分上报源)
        |
        v
[API Gateway / Load Balancer]
        |
   +----+----+-----------+
   |         |           |
   v         v           v
Score      Rank        User
Ingestion  Query       Profile
Service    Service     Service
   |         |           |
   v         v           v
Score      Redis       User DB
Queue      Sorted      (MySQL)
(Kafka)    Set
   |         |
   v         |
Score       |
Processor --+
(Consumer)
```

### 组件职责 (Component Responsibilities)

| 组件 | 职责 | 技术选型 |
|------|------|----------|
| **API Gateway** | 认证、限流、请求路由 | Kong / Envoy |
| **Score Ingestion Service** | 接收游戏服务器的积分上报，写入消息队列 | Go 微服务 |
| **Score Processor** | 消费 Kafka 消息，更新 Redis Sorted Set | Go 微服务 |
| **Rank Query Service** | 处理 Top-K、Rank Lookup、相对排名查询 | Go 微服务 |
| **User Profile Service** | 玩家资料（昵称、头像、段位等） | Java 微服务 |
| **Score Queue (Kafka)** | 积分更新消息缓冲，削峰填谷 | Kafka Cluster |
| **Redis Sorted Set** | 排行榜数据存储，O(log N) 排名操作 | Redis Cluster |
| **User DB** | 玩家基础信息持久化 | MySQL (主从) |
| **Score Archive DB** | 历史排行榜快照、赛季归档 | MySQL / S3 (Parquet) |

### 核心流程 (Core Flow)

**积分更新流程 (Score Update Flow)**:

1. 游戏服务器对局结束，调用 Score Ingestion API: `POST /scores {player_id, score_delta, game_id, timestamp}`
2. **Score Ingestion Service** 做基本校验后写入 **Kafka** topic `score-updates`
3. **Score Processor** 消费消息，执行 Redis 命令:
   - `ZINCRBY leaderboard:{board_id} {score_delta} {player_id}` (原子递增积分)
   - 同时更新日榜/周榜的 key: `ZINCRBY daily:{date}:{board_id} ...`
4. 积分变更同步写入 **MySQL** 做持久化备份（异步批量写入，不在关键路径）

**Top-K 查询流程 (Top-K Query Flow)**:

1. 客户端请求: `GET /leaderboard/{board_id}/top?k=100`
2. **Rank Query Service** 执行 Redis 命令:
   - `ZREVRANGE leaderboard:{board_id} 0 99 WITHSCORES` -- O(log N + K)
3. 拿到 player_id 列表后，批量查询 **User Profile Service** 获取昵称、头像
4. 组装返回结果 `[{rank, player_id, nickname, avatar, score}, ...]`

**玩家排名查询 (Rank Lookup Flow)**:

1. 客户端请求: `GET /leaderboard/{board_id}/rank/{player_id}`
2. **Rank Query Service** 执行:
   - `ZREVRANK leaderboard:{board_id} {player_id}` -- O(log N)
   - `ZSCORE leaderboard:{board_id} {player_id}` -- O(1)
3. 返回 `{rank: rank+1, score: score}` (ZREVRANK 从 0 开始，转为 1-based)

### 关键设计决策 (Key Design Decisions)

1. **Kafka 削峰**: 游戏高峰期（如赛季结算）积分上报可能瞬间飙升到 10 万+ QPS。
   Kafka 作为缓冲层，Score Processor 按可控速率消费，保护 Redis 不被打爆。

2. **Redis Sorted Set 作为排行榜引擎**: Sorted Set 天然支持 `ZADD/ZINCRBY`
   (积分更新)、`ZREVRANGE` (Top-K)、`ZREVRANK` (排名查询)，全部 O(log N)。
   5000 万玩家的 Sorted Set 约占 ~2-3 GB 内存，单机可承受。

3. **读写分离**: 积分更新走 Kafka -> Score Processor -> Redis (写路径)；
   排名查询直接读 Redis Replica (读路径)。读写比约 2:1，但读延迟要求更严格。

4. **多维度排行榜用独立 key**: `daily:2026-04-08:board1`、`weekly:2026-W15:board1`、
   `season:s12:board1`。每个维度独立 Sorted Set，日榜/周榜用 TTL 自动过期。
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### REST API 设计

**积分上报 API** (游戏服务器调用，非玩家直接调用):
```
POST /api/v1/scores
Authorization: Bearer {server_api_key}
Content-Type: application/json

{
  "player_id": "p_12345",
  "board_id": "ranked_season12",
  "score_delta": 25,
  "game_id": "g_98765",
  "timestamp": "2026-04-08T14:30:00Z"
}

Response 202 Accepted:
{ "status": "queued", "message_id": "msg_abc123" }
```

**Top-K 查询 API**:
```
GET /api/v1/leaderboard/{board_id}/top?k=100&period=all

Response 200:
{
  "board_id": "ranked_season12",
  "period": "all",
  "updated_at": "2026-04-08T14:30:05Z",
  "entries": [
    {"rank": 1, "player_id": "p_001", "nickname": "ProGamer", "score": 98500, "avatar_url": "..."},
    {"rank": 2, "player_id": "p_042", "nickname": "DragonSlayer", "score": 97200, "avatar_url": "..."},
    ...
  ]
}
```

**玩家排名查询 API**:
```
GET /api/v1/leaderboard/{board_id}/rank/{player_id}

Response 200:
{
  "player_id": "p_12345",
  "board_id": "ranked_season12",
  "rank": 15234,
  "score": 42100,
  "total_players": 5000000,
  "percentile": 99.7
}
```

**相对排名 API (我周围的人)**:
```
GET /api/v1/leaderboard/{board_id}/around/{player_id}?range=5

Response 200:
{
  "player_id": "p_12345",
  "my_rank": 15234,
  "my_score": 42100,
  "neighbors": [
    {"rank": 15229, "player_id": "p_999", "nickname": "...", "score": 42150},
    ...
    {"rank": 15234, "player_id": "p_12345", "nickname": "Me", "score": 42100},
    ...
    {"rank": 15239, "player_id": "p_777", "nickname": "...", "score": 42050}
  ]
}
```

### 核心数据模型

**Redis Sorted Set 数据**:

| Key Pattern | Member | Score | 用途 |
|-------------|--------|-------|------|
| `lb:all:{board_id}` | player_id | 总积分 | 赛季/全局排行榜 |
| `lb:daily:{date}:{board_id}` | player_id | 日积分 | 日榜 (TTL: 48h) |
| `lb:weekly:{week}:{board_id}` | player_id | 周积分 | 周榜 (TTL: 14d) |

**MySQL 持久化表** (Score Archive):

```sql
CREATE TABLE score_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    player_id VARCHAR(32) NOT NULL,
    board_id VARCHAR(64) NOT NULL,
    score_delta INT NOT NULL,
    game_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_board (player_id, board_id),
    INDEX idx_board_time (board_id, created_at)
) ENGINE=InnoDB;

CREATE TABLE leaderboard_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    board_id VARCHAR(64) NOT NULL,
    period_type ENUM('daily', 'weekly', 'season') NOT NULL,
    period_key VARCHAR(32) NOT NULL,
    snapshot_data JSON NOT NULL,  -- Top-1000 at period end
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_board_period (board_id, period_type, period_key)
) ENGINE=InnoDB;
```

### 读路径 (Read Path)

```
Client -> API Gateway -> Rank Query Service
  -> Redis ZREVRANGE / ZREVRANK (O(log N))
  -> (batch) User Profile Service (Redis cache / MySQL)
  -> Response assembly -> Client
```

延迟分解: Redis 查询 ~1ms + 用户资料批量查询 ~10ms + 序列化 ~1ms = **P99 < 50ms**

### 写路径 (Write Path)

```
Game Server -> API Gateway -> Score Ingestion Service
  -> Kafka produce (async, ~5ms)
  -> Return 202 to Game Server

Score Processor (Kafka consumer):
  -> Consume message
  -> ZINCRBY (Redis, ~1ms)
  -> Batch insert MySQL (async, every 1s or 100 events)
```

端到端延迟: API 接收 ~2ms + Kafka produce ~5ms + consume lag ~50-200ms
+ Redis update ~1ms = **积分在 < 500ms 内反映到排行榜**

### 异步路径 (Async Paths)

1. **日榜/周榜重置**: Cron Job 在 UTC 00:00 触发，(a) 对当天日榜 Top-1000
   执行 `ZREVRANGE` 生成快照写入 MySQL，(b) 创建新的日榜 key，旧 key 设置
   TTL 48h 后自动删除。

2. **赛季结算**: 赛季结束时，(a) 全量导出排行榜到 S3 (Parquet 格式)，
   (b) 通知奖励系统发放赛季奖励，(c) 重置 Redis Sorted Set。

3. **MySQL 持久化**: Score Processor 维护内存 buffer，每秒或每 100 条
   批量 INSERT 到 MySQL，确保 Redis 故障时可从 MySQL 重建排行榜。
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms -- 5 min)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

**基础数据**:
- 注册玩家: 5000 万
- DAU: 500 万
- 每个玩家日均对局: 10 场
- 每场对局产生 1 次积分更新

**QPS 估算**:

$$\text{日均积分更新} = 500 \text{万} \times 10 = 5000 \text{万次/天}$$

$$\text{平均 QPS} = \frac{50{,}000{,}000}{86{,}400} \approx 580 \text{ QPS}$$

$$\text{峰值 QPS (10x)} \approx 5{,}800 \text{ QPS}$$

考虑赛季结算等特殊事件的极端峰值:

$$\text{极端峰值 QPS} \approx 50{,}000 \text{ QPS}$$

**排名查询 QPS**:

$$\text{日均排名查询} \approx 500 \text{万 DAU} \times 5 \text{ 次查看/天} = 2500 \text{万次/天}$$

$$\text{平均查询 QPS} \approx 290 \text{ QPS}$$

$$\text{峰值查询 QPS (10x)} \approx 2{,}900 \text{ QPS}$$

### 存储估算

**Redis 内存**:

每个 Sorted Set member: player_id (16 bytes) + score (8 bytes) + skiplist overhead (~64 bytes) = ~88 bytes/member

$$\text{全局排行榜 (50M 玩家)} = 50{,}000{,}000 \times 88 \text{ bytes} \approx 4.4 \text{ GB}$$

$$\text{日榜 (活跃 5M)} = 5{,}000{,}000 \times 88 \text{ bytes} \approx 440 \text{ MB}$$

$$\text{周榜 (活跃 10M)} = 10{,}000{,}000 \times 88 \text{ bytes} \approx 880 \text{ MB}$$

$$\text{总 Redis 内存} \approx 4.4 + 0.44 + 0.88 \approx 5.7 \text{ GB}$$

5.7 GB 对于单台 Redis 实例（通常 64-128 GB 内存）完全可承受。

**MySQL 存储 (积分事件归档)**:

$$\text{每条积分事件} \approx 100 \text{ bytes}$$

$$\text{日增量} = 5000 \text{万条} \times 100 \text{ bytes} = 5 \text{ GB/天}$$

$$\text{年存储} = 5 \times 365 \approx 1.8 \text{ TB}$$

超过 90 天的历史数据可归档到 S3 (Parquet)，MySQL 只保留近 90 天热数据 (~450 GB)。

### 带宽估算

$$\text{Top-100 响应} = 100 \times 200 \text{ bytes (含昵称头像)} = 20 \text{ KB}$$

$$\text{峰值带宽 (查询)} = 2{,}900 \times 20 \text{ KB} = 58 \text{ MB/s}$$

### 核心算法: Redis Sorted Set (Skip List)

**Redis Sorted Set** 内部使用 **Skip List (跳表)** + **Hash Table** 实现:

- **Skip List**: 有序链表的多层索引结构。每层以概率 $p = 0.25$ 提升节点。
  期望层数 $\mathbb{E}[\text{levels}] = \frac{1}{1-p} = \frac{4}{3}$。

- **时间复杂度**:

| 操作 | Redis 命令 | 复杂度 | 含义 |
|------|-----------|--------|------|
| 插入/更新积分 | `ZADD` / `ZINCRBY` | $O(\log N)$ | 跳表插入 |
| 查询玩家排名 | `ZREVRANK` | $O(\log N)$ | 跳表查找 + 节点排名 |
| 查询玩家积分 | `ZSCORE` | $O(1)$ | Hash Table 直接查找 |
| Top-K 查询 | `ZREVRANGE 0 K-1` | $O(\log N + K)$ | 定位起点 + 遍历 K 个 |
| 相对排名 | `ZREVRANGE start end` | $O(\log N + K)$ | 定位玩家 + 遍历范围 |
| 删除玩家 | `ZREM` | $O(\log N)$ | 跳表删除 |

**同分排序 (Tie-breaking)**: Redis Sorted Set 中同分成员按字典序排列。
若需要"先到先得"规则 (同分情况下先达到的排前面)，可以将时间戳编码进 score:

$$\text{composite\_score} = \text{actual\_score} \times 10^{13} + (10^{13} - \text{timestamp\_ms})$$

高位是真实分数（分数越高排名越前），低位是时间戳的反转（越早达到该分数，反转值越大，
排名越前）。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability -- Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产约束与深度解析 (Production Constraints & Deep Dive)

### 具体规模数字 (Scale Numbers)

| 指标 | 数值 |
|------|------|
| 注册玩家 | 5000 万 |
| DAU | 500 万 |
| 同时在线峰值 (PCU) | 50 万 |
| 日均积分更新 | 5000 万次 |
| 峰值积分更新 QPS | ~5,800 (极端 50,000) |
| 峰值排名查询 QPS | ~2,900 |
| Redis 内存 | ~5.7 GB |
| MySQL 日增量 | ~5 GB |
| 独立排行榜数量 | 10-50 个 |

### 单点故障分析 (Single Point of Failure Analysis)

| 组件 | 故障影响 | 消除方案 |
|------|----------|----------|
| **Redis Master** | 排行榜不可写入，查询走 Replica | Redis Sentinel 自动 failover (30s)；1 主 2 从 |
| **Kafka** | 积分更新暂时不可入队 | Kafka 3-broker 集群，replication factor=3 |
| **Score Processor** | 积分更新延迟增大 | 多实例消费者组 (Consumer Group)，挂一个其余自动 rebalance |
| **Rank Query Service** | 排名查询不可用 | 无状态服务，多实例 + LB 健康检查 |
| **MySQL** | 历史数据不可查，不影响实时排行 | 主从复制 + MHA 自动 failover |

### Redis 分片策略 (当玩家超过 1 亿时)

当单个 Sorted Set 超过 1 亿 member (~8.8 GB)，单机 Redis 虽然内存够，
但 `ZREVRANK` 的 O(log N) 常数项变大，延迟可能超过 10ms。此时需要分片。

**方案: 分数区间分片 (Score Range Partitioning)**:

```
Shard 0: 积分 0 - 999        (底部玩家, 数量多)
Shard 1: 积分 1000 - 4999    (中等玩家)
Shard 2: 积分 5000 - 19999   (高级玩家)
Shard 3: 积分 20000+         (顶尖玩家, 数量少但查询多)
```

**Top-K 查询**: 从最高分 Shard 开始取，不够再从下一个 Shard 补充。
Top-100 通常只需查 Shard 3。

**Rank Lookup**: 玩家在自己 Shard 内的排名 + 所有更高分 Shard 的总人数:

$$\text{global\_rank} = \text{rank\_in\_shard} + \sum_{i > \text{my\_shard}} \text{ZCARD}(\text{shard}_i)$$

`ZCARD` 是 O(1) 操作，额外开销极小。

**分数边界迁移**: 当 Shard 内人数不均衡时（如大量玩家积分集中在某个区间），
可以动态调整分数边界。使用 **ZooKeeper / etcd** 存储当前分片配置，
Score Processor 定期检查并执行 rebalance。

### 多数据中心部署 (Multi-Region)

**场景**: 全球化游戏，北美、欧洲、亚洲各有数据中心。

**方案: 全局主排行榜 + 区域缓存**:

1. **全局 Redis 主集群**: 部署在核心区域（如 US-East），存储所有排行榜数据
2. **区域 Redis 只读副本**: 各区域部署 Redis Replica，通过 **Redis Replication**
   异步同步（延迟 ~100-500ms）
3. **积分写入**: 各区域的 Score Processor 都写入全局 Kafka -> 全局 Redis 主集群
4. **排名查询**: 各区域从本地 Redis Replica 读取，延迟更低

**一致性权衡**: 玩家在不同区域看到的排名可能有 ~500ms 差异，
对游戏排行榜场景可以接受。

### 高并发处理 (High Concurrency)

1. **Kafka 削峰**: 极端峰值 50K QPS 先入 Kafka（Kafka 单 partition 可承受
   100K+ msg/s），Score Processor 按 Redis 可承受的速率消费（~10K/s per instance）

2. **Redis Pipeline**: Score Processor 不逐条执行 `ZINCRBY`，而是攒一批
   (如 100 条) 用 Redis Pipeline 批量发送，减少 RTT:

```
# 伪代码: Pipeline 批量更新
pipe = redis.pipeline()
for event in batch:
    pipe.zincrby(f"lb:all:{event.board_id}", event.score_delta, event.player_id)
    pipe.zincrby(f"lb:daily:{today}:{event.board_id}", event.score_delta, event.player_id)
pipe.execute()  # 一次 RTT 执行所有命令
```

3. **连接池 (Connection Pooling)**: Rank Query Service 维护固定大小的 Redis
   连接池 (如 50 连接/实例)，避免连接风暴。

4. **限流 (Rate Limiting)**: API Gateway 对每个游戏服务器的积分上报限流
   (如 1000 QPS/server)，防止异常服务器打爆系统。

5. **Circuit Breaker**: 如果 Redis 响应延迟 > 50ms，触发熔断，
   直接返回缓存的最近一次 Top-K 结果（可能延迟几秒的数据），避免雪崩。

### 监控与告警 (Monitoring & Alerting)

| 指标 | 正常范围 | 告警阈值 |
|------|----------|----------|
| Redis 内存使用 | < 10 GB | > 15 GB |
| Redis 操作延迟 P99 | < 2ms | > 10ms |
| Kafka consumer lag | < 1000 messages | > 10,000 messages |
| Score update 端到端延迟 | < 500ms | > 2s |
| Rank Query P99 | < 50ms | > 200ms |
| Redis Sorted Set ZCARD | ~50M | 突变 > 10% (可能数据异常) |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策 (Key Design Decisions)

| 决策 | 方案 A | 方案 B | 我们的选择与理由 |
|------|--------|--------|------------------|
| **排行榜引擎** | Redis Sorted Set | 自建 Segment Tree / B-Tree | **Redis Sorted Set** -- 开箱即用，O(log N) 全功能 (ZADD/ZREVRANK/ZREVRANGE)，5000 万玩家仅 ~4.4 GB，运维成熟。自建引擎开发成本高，除非有极特殊需求（如需要支持复合排序键），否则不值得。 |
| **积分写入方式** | 同步写 Redis | 通过 Kafka 异步写 | **Kafka 异步** -- 同步写 Redis 在正常负载下更简单（延迟更低），但无法应对赛季结算等极端峰值。Kafka 提供削峰能力和事件重放能力（Redis 故障后可从 Kafka 重放恢复）。代价是增加 ~200ms 端到端延迟，对排行榜场景可接受。 |
| **持久化策略** | Redis RDB/AOF 持久化 | Redis + MySQL 双写 | **Redis + MySQL 双写** -- 仅靠 Redis 持久化有数据丢失风险（RDB 快照有窗口，AOF 有 fsync 延迟）。MySQL 作为持久化备份，Redis 故障时可从 MySQL 全量重建。代价是额外写入开销，但积分事件是追加写入，MySQL 轻松承受。 |
| **多维度排行榜** | 单 Sorted Set + 过滤 | 每个维度独立 Sorted Set | **独立 Sorted Set** -- 日榜/周榜/赛季榜使用独立的 Redis key。虽然多写几次（每次积分更新写 3 个 key），但查询时无需过滤，O(log N) 直达。单 Sorted Set + 时间过滤无法用 Redis 原生命令实现，需要额外逻辑。 |
| **同分排序** | 并列同名次 | 时间戳编码 tie-breaking | **时间戳编码** -- 将时间戳编码进 score 低位，先到先得。虽然增加了积分解码复杂度，但解决了"10 万人同分时排名无意义"的问题，提升用户体验。 |

### CAP 定理应用 (CAP Theorem Application)

排行榜系统选择 **AP (可用性 + 分区容忍性)**:

- **可用性优先**: 排行榜不可用直接影响游戏体验。即使网络分区导致排名数据
  短暂不一致（如不同区域看到略不同的排名），也比排行榜完全不可用好。
- **最终一致**: 积分更新通过 Kafka -> Redis 的异步管道，允许 ~500ms-1s 的延迟。
  多区域 Redis Replica 有 ~100-500ms 的复制延迟。
- **强一致例外**: 赛季结算奖励发放时需要冻结排行榜 + 读取最终一致的排名，
  此时可以短暂停止写入（2-3 秒），等 Kafka lag 清零后取 Redis 快照。

### 成本 vs 性能

- **Redis 内存成本**: 5.7 GB Redis 内存在 AWS ElastiCache r6g.xlarge 上约 $300/月。
  极低成本换来亚毫秒级排名查询。
- **Kafka 成本**: 3-broker MSK 集群约 $500/月，但提供了关键的削峰和事件重放能力。
- **MySQL 成本**: 积分事件 1.8 TB/年，90 天热数据 ~450 GB，db.r6g.2xlarge
  约 $800/月。超过 90 天归档到 S3 (约 $10/TB/月)。

总基础设施成本约 **$1,600/月**，支撑 5000 万玩家的实时排行榜。

### 10x / 100x 规模变化

**10x (5 亿玩家)**:
- Redis 内存 ~44 GB，仍可单机承受（128 GB 实例），但推荐分片
- 按分数区间分 4-8 个 Shard，每个 Shard ~5-10 GB
- Kafka 扩展 partition 数量，Score Processor 增加消费者实例
- MySQL 按 board_id 分表

**100x (50 亿玩家)**:
- Redis 分片必须，~440 GB 总内存，需要 16-32 个 Shard
- 考虑混合方案: Top-10000 用 Redis (精确排名)，其余用近似排名算法
  (如 **Count-Min Sketch** + 分段统计)
- 引入 **percentile-based ranking**: 不返回精确排名 "第 42,381,567 名"，
  而是返回 "Top 15.3%"，大幅降低精确排名的计算压力
- 积分事件流用 **Apache Flink** 实时处理，替代简单的 Kafka Consumer
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

---

**Q: Redis 挂了怎么办？排行榜数据会丢失吗？**

> **承认风险**: Redis 是内存数据库，如果主从同时挂掉（虽然概率极低），
> 内存中的排行榜数据会丢失。
>
> **缓解措施**:
>
> 1. **Redis Sentinel + 1 主 2 从**: 主节点故障时 Sentinel 在 30 秒内自动
>    promote 从节点为新主。两个从节点确保即使一主一从同时挂掉仍有一个从可用。
> 2. **Redis RDB 快照**: 每 5 分钟生成一次 RDB 快照到磁盘。最坏情况丢失
>    5 分钟数据。
> 3. **MySQL 完整备份**: 所有积分事件都持久化到 MySQL。Redis 全部丢失后，
>    可以从 MySQL 重建排行榜:
>    ```sql
>    SELECT player_id, SUM(score_delta) as total_score
>    FROM score_events
>    WHERE board_id = 'ranked_season12'
>    GROUP BY player_id
>    ORDER BY total_score DESC;
>    ```
>    5000 万行 SUM 查询约 5-10 分钟完成，批量 `ZADD` 回 Redis 再需 2-3 分钟。
>    **全量恢复时间 < 15 分钟**。
> 4. **Kafka 事件重放**: 如果 MySQL 也延迟了，还可以将 Kafka retention 设为
>    7 天，从 Kafka 重放所有积分事件重建 Redis。
>
> **数据**: 三重保障 (Sentinel + RDB + MySQL) 使数据永久丢失的概率接近零。
> 即使发生灾难性故障，最多 15 分钟可完全恢复。

---

**Q: 赛季结算时流量暴增 10 倍怎么办？比如所有玩家同时完成最后一场排位赛。**

> **承认挑战**: 赛季结算的最后 1 小时可能出现 50K+ QPS 的积分更新，
> 同时排名查询量也会飙升（玩家频繁刷新查看最终排名）。
>
> **缓解措施**:
>
> 1. **Kafka 削峰**: 50K QPS 的积分更新先入 Kafka。Kafka 单 topic
>    16 个 partition 可承受 200K+ msg/s，提供充足缓冲。
> 2. **Score Processor 弹性伸缩**: 预估峰值提前扩容消费者实例。
>    正常 4 实例 -> 赛季结算前扩到 16 实例。Auto-scaling 基于 Kafka
>    consumer lag 指标。
> 3. **查询结果缓存**: 赛季最后阶段，Top-100 查询结果在应用层缓存 2 秒
>    (正常不缓存)，减少 Redis 读压力。
> 4. **赛季结算冻结**: 赛季结束时间到后:
>    (a) 停止接收新的积分更新 (API 返回 "赛季已结束")
>    (b) 等待 Kafka lag 清零 (通常 < 5 秒)
>    (c) 执行排行榜快照 + 奖励计算
>    (d) 开启新赛季的排行榜 key
> 5. **降级策略**: 如果 Redis 延迟超过阈值，Rank Query Service 返回
>    "排名计算中，请稍后刷新"，而不是超时错误。
>
> **数据**: Kafka + 弹性伸缩可将积分更新延迟从 >10s (无缓冲) 控制在 < 2s，
> 查询缓存可将 Redis 读 QPS 降低 60-80%。

---

**Q: 如果有两个玩家同时更新积分导致并发冲突怎么办？**

> **实际上不存在此问题**: Redis 是单线程模型，所有命令串行执行。
> `ZINCRBY` 是原子操作，两个玩家同时更新不会产生竞态条件。
>
> 即使 50K QPS 的积分更新并发到达 Redis，Redis 按序逐个执行 `ZINCRBY`，
> 每个操作 ~1 微秒，单线程可处理 100K+ 命令/秒。
>
> **真正需要注意的并发问题**:
>
> 1. **同一玩家的重复积分上报**: 网络抖动可能导致同一场对局的积分被上报两次。
>    解决方案: Score Processor 维护已处理 game_id 的 **Redis Set**
>    (`SADD processed:{game_id}`)，收到重复 game_id 直接跳过。
>    Set 的 key 设置 TTL 24h 自动过期。
>
> 2. **读写一致性**: 玩家更新积分后立刻查排名，可能因为 Kafka 延迟看到旧排名。
>    解决: 在积分更新 API 返回中附带预估的新排名（基于 `ZSCORE + ZCOUNT`
>    近似计算），客户端优先展示这个预估排名，后台异步刷新。

---

**Q: 5000 万玩家的 Sorted Set，`ZREVRANK` 真的能在 10ms 内返回吗？
有性能测试数据吗？**

> **Redis 官方基准**: Redis 6.0 在 c5.xlarge 实例上，5000 万 member 的
> Sorted Set:
> - `ZADD`: ~0.8 微秒 (P99)
> - `ZREVRANK`: ~2.5 微秒 (P99)
> - `ZREVRANGE 0 99`: ~8 微秒 (P99)
>
> 这远低于 10ms 的要求。实际生产环境加上网络 RTT (~0.5ms) 和序列化开销，
> 端到端 P99 仍在 **< 5ms**。
>
> **跳表 (Skip List) 的排名查询原理**: Redis Sorted Set 的跳表在每个
> forward pointer 上维护了 `span` (跨越的节点数)。`ZREVRANK` 沿跳表
> 从高层到低层查找目标节点，累加路径上的 span 即为排名，无需遍历全部节点。
> 时间复杂度 O(log N)，50M 节点约 25 次比较。
>
> **实测建议**: 在上线前用 `redis-benchmark` 或自定义脚本插入 5000 万
> 随机 member，测试 `ZREVRANK` 的 P99 延迟。如果超过 5ms，
> 考虑 Score Range Partitioning 分片。

---

**Q: 日榜、周榜的重置过程中，用户查询排行榜会受影响吗？**

> **不会受影响**: 重置采用"创建新 key + 旧 key 设 TTL"的方式，不是删除重建。
>
> **具体流程**:
>
> 1. UTC 00:00，Cron Job 触发日榜轮转
> 2. 对旧日榜 `lb:daily:2026-04-08:board1` 执行 `ZREVRANGE 0 999 WITHSCORES`，
>    生成 Top-1000 快照写入 MySQL
> 3. 新的积分更新自动写入新 key `lb:daily:2026-04-09:board1`
>    (Score Processor 使用当天日期作为 key 的一部分)
> 4. 旧 key 设置 TTL 48h，48 小时后自动删除
> 5. 用户查询日榜时，Rank Query Service 总是查询当天日期的 key
>
> 全程无锁、无停机、无用户感知。
>
> **边界情况**: 在 00:00 前后几秒内，可能有极少数请求查到空的新日榜
> （还没有积分写入）。解决: 如果当天日榜为空，fallback 显示昨天的日榜，
> 并标注"新日榜数据加载中"。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清 (Requirements Clarification)

> "实时游戏排行榜的核心是让玩家看到自己和全球其他玩家的排名。
> 我先确认几点: 玩家规模大概多少？积分是单调递增还是可增可减？
> 排名需要实时还是可以有几秒延迟？是否有多个独立排行榜（不同游戏模式）？
> 同分怎么排？需要日榜/周榜吗？
> 我假设 5000 万玩家，500 万 DAU，排名 < 1 秒延迟，多维度排行榜。"
>
> 列出 FR: 积分上报、Top-K、排名查询、相对排名、多时间维度。
> 列出 NFR: 99.99% 可用性、积分更新 P99 < 50ms、查询 P99 < 100ms。
> 明确 Out of Scope: 匹配系统、积分计算、反作弊、社交排行。
> 关键特征: **写入峰值高（赛季结算）、读多写少、排名必须精确**。

### 5-15 分钟: 高层架构 (High-Level Architecture)

> "核心选型: **Redis Sorted Set** 作为排行榜引擎。理由:
> `ZADD` O(log N) 更新积分，`ZREVRANK` O(log N) 查排名，
> `ZREVRANGE` O(log N + K) 查 Top-K。5000 万玩家只需 ~4.4 GB 内存。"
>
> "写路径: 游戏服务器 -> Score Ingestion Service -> **Kafka** (削峰)
> -> Score Processor -> Redis `ZINCRBY`。读路径: 客户端 ->
> Rank Query Service -> Redis `ZREVRANGE/ZREVRANK` -> 批量查用户资料。
> 持久化: Score Processor 异步批量写入 MySQL 备份。"
>
> "多维度排行榜: 每个维度独立 Redis key。`lb:all:board1` (赛季总榜)、
> `lb:daily:2026-04-08:board1` (日榜, TTL 48h)、
> `lb:weekly:2026-W15:board1` (周榜, TTL 14d)。
> 每次积分更新同时写 3 个 key。"

### 15-40 分钟: 深度讨论 (Deep Dive -- 选 2-3 个重点)

**重点 1: Redis Sorted Set 内部原理 (8-10 分钟)**
> "Sorted Set 内部是 **Skip List + Hash Table**。Skip List 是多层有序链表，
> 每层以概率 0.25 提升节点。查询从顶层开始，逐层下降定位目标。
> 关键: 每个 forward pointer 维护 `span` (跨越节点数)，所以 `ZREVRANK`
> 不需要遍历，沿查找路径累加 span 即为排名。
> 5000 万节点约 25 次比较，< 3 微秒。
> 同分处理: 将时间戳编码进 score 低位实现先到先得。
> `composite_score = actual_score * 10^13 + (10^13 - timestamp_ms)`。"

**重点 2: Kafka 削峰与高并发处理 (8-10 分钟)**
> "赛季结算可能 50K QPS 瞬间涌入。Kafka 16 partition 可承受 200K+ msg/s。
> Score Processor 用 Consumer Group，正常 4 实例消费，峰值扩到 16 实例。
> Redis Pipeline 批量更新: 攒 100 条用一次 RTT 发送，吞吐提升 10x。
> 赛季结算冻结流程: 停收积分 -> 等 lag 清零 -> 快照 -> 发奖 -> 开新赛季。"

**重点 3: 容量估算 (5-8 分钟)**
> "5000 万玩家 x 88 bytes/member = 4.4 GB (Redis)。
> 500 万 DAU x 10 场/天 = 5000 万积分更新/天。
> 峰值 QPS ~5800，极端 ~50000。
> MySQL: 100 bytes/event x 5000 万/天 = 5 GB/天，年 1.8 TB。
> 90 天热数据 450 GB，其余归档 S3。
> 总成本约 $1600/月 -- Redis $300 + Kafka $500 + MySQL $800。"

### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)

> "核心权衡: Redis Sorted Set vs 自建数据结构 (成熟度 vs 定制性)，
> Kafka 异步 vs 同步直写 (削峰能力 vs 延迟)，
> Redis 单 Sorted Set vs 分片 (简单性 vs 超大规模)。
> 10x: 按分数区间分 4-8 个 Redis Shard。
> 100x: Top-10K 精确排名 + 其余用 percentile 近似排名。"

### 50-55 分钟: 总结 (Wrap-up)

> "如果给我更多时间，我会深入: (1) 好友排行榜 -- 从好友关系图中筛选
> Sorted Set 子集，或维护独立的 per-user 好友排行 key，
> (2) 反作弊集成 -- 异常积分检测（如单场积分偏离均值 3 个标准差自动
> 标记人工审核），(3) 排行榜可视化 -- 历史排名趋势图、积分分布直方图。"

### 55-60 分钟: 向面试官提问

> "你们的排行榜用 Redis Sorted Set 还是自建方案？
> 同分排序用什么策略？赛季结算的峰值有多高、怎么处理的？
> 有没有遇到 Redis 大 key 问题？分片方案是怎样的？"

---

### 3 分钟电梯简述版 (Elevator Pitch)

1. **(30 秒) 问题**: 设计实时排行榜 -- 5000 万玩家，500 万 DAU，
   积分更新 < 1 秒反映到排名，日榜/周榜/赛季榜。

2. **(60 秒) 架构**: **Redis Sorted Set** 作为排行榜引擎。
   `ZINCRBY` O(log N) 更新积分，`ZREVRANK` O(log N) 查排名。
   5000 万玩家仅 4.4 GB 内存。写路径通过 **Kafka** 削峰，
   Score Processor 消费后批量 `ZINCRBY`。MySQL 异步备份所有积分事件。
   多维度排行榜用独立 Redis key + TTL 自动过期。

3. **(60 秒) 关键设计**: 同分排序 -- 时间戳编码进 score 低位实现先到先得。
   赛季结算 -- Kafka 16 partition 承受 50K QPS，Score Processor
   弹性伸缩 4->16 实例。Redis 故障恢复 -- MySQL 全量重建 < 15 分钟。
   分片策略 -- 超过 1 亿玩家时按分数区间分 Shard，`global_rank =
   rank_in_shard + SUM(higher_shards_ZCARD)`。

4. **(30 秒) 扩展**: 10x 按分数分 4-8 Shard。100x Top-10K 精确 +
   其余 percentile 近似。全球化用全局 Redis 主集群 + 区域只读副本。
   成本约 $1,600/月 支撑 5000 万玩家。
"""


def populate_interview_game_leaderboard() -> None:
    """Create or update the interview-game-leaderboard record with all 8 sections."""
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
    populate_interview_game_leaderboard()
