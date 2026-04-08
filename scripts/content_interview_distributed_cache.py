"""Populate interview-distributed-cache system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design a Distributed Cache
-- consistent hashing with virtual nodes, LRU/LFU/TTL eviction policies,
cache-aside vs write-through vs write-behind patterns, cache stampede prevention,
hot key mitigation, cache invalidation strategies, and replication for HA.
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

SLUG = "interview-distributed-cache"
TITLE = "Design a Distributed Cache"
DISPLAY_ORDER = 119

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**分布式缓存系统 (Distributed Cache System)**，类似 Memcached / Redis
Cluster，为大规模 Web 应用提供低延迟、高吞吐的键值数据缓存服务。系统需要在
多台机器间分散存储热点数据，在单机故障时保持可用性，并提供灵活的缓存失效
(Cache Invalidation) 机制。

核心挑战在于：(1) **数据分布** -- 如何将海量键值对均匀分布到 N 台缓存节点，
且在节点增减时最小化数据迁移；(2) **缓存一致性** -- 数据库更新后如何及时
使缓存失效，避免读到过期数据 (Stale Data)；(3) **热点问题 (Hot Key)** --
某些极高访问频率的键集中在单台节点上导致过载；(4) **缓存穿透/击穿/雪崩** --
缓存未命中时如何保护后端数据库不被压垮。

### 功能性需求 (Functional Requirements)

1. **GET(key)**: 根据键获取缓存值，P99 延迟 < 1ms
2. **PUT(key, value, TTL)**: 写入键值对并设置过期时间 (Time-To-Live)
3. **DELETE(key)**: 显式删除缓存条目
4. **批量操作 (Multi-GET / Multi-PUT)**: 一次请求获取或写入多个键
5. **自动过期 (TTL Expiration)**: 到期后自动清除，支持懒删除 (Lazy Expiration)
   与主动清理 (Active Expiration)
6. **缓存淘汰 (Eviction)**: 内存不足时按策略 (LRU / LFU / TTL) 淘汰数据

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 缓存不可用会导致所有请求直接打到
  数据库，可能引发级联故障 (Cascading Failure)
- **延迟 (Latency)**: 读 P99 < 1ms (同数据中心)；写 P99 < 5ms
- **吞吐 (Throughput)**: 单节点 100K+ QPS；集群支持数百万 QPS
- **一致性 (Consistency)**: 最终一致性 (Eventual Consistency)，可接受短暂
  过期数据窗口 (通常 < 数秒)
- **可扩展性 (Scalability)**: 支持 TB 级缓存容量，节点可在线扩缩容
  (无需停机)
- **容错性 (Fault Tolerance)**: 单节点故障不影响整体可用性，数据自动
  重新分布

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 缓存的数据模型是纯键值对 (Key-Value) 还是需要支持复杂数据结构
   (如 List, Set, Sorted Set)?**
   -- WHY: 纯 KV 可以用 Memcached 风格的简单哈希表实现；支持复杂结构
   则需要类似 Redis 的多数据结构引擎，显著增加内存管理和序列化复杂度

2. **Q: 是否需要持久化 (Persistence)? 缓存重启后数据是否需要恢复?**
   -- WHY: 如果需要持久化则要引入 AOF / RDB 快照机制，增加磁盘 I/O
   和恢复时间；纯内存缓存可以更简单，但重启后需要预热 (Cache Warming)

3. **Q: 客户端感知缓存拓扑 (Client-side Routing) 还是通过代理层路由
   (Proxy-based Routing)?**
   -- WHY: 客户端路由 (如 Redis Cluster) 性能更好但客户端更复杂；
   代理路由 (如 Twemproxy / Envoy) 客户端简单但多一跳延迟

4. **Q: 缓存失效策略以 TTL 为主还是需要主动推送失效 (Active Invalidation)?**
   -- WHY: 纯 TTL 实现简单但有过期数据窗口；主动失效需要变更捕获管道
   (Change Data Capture, CDC)，架构更复杂但一致性更强

5. **Q: 是否存在明显的热点键 (Hot Key)? 例如热搜、爆款商品?**
   -- WHY: 热点键决定是否需要本地缓存 (Local Cache / L1 Cache) 或
   键复制 (Key Replication) 策略来分散单节点压力

6. **Q: 缓存的值大小范围? 是 KB 级小对象还是有 MB 级大对象?**
   -- WHY: 大对象需要分片存储 (Chunking)、压缩、以及不同的内存分配策略；
   小对象则需要关注内存碎片和元数据开销

7. **Q: 多数据中心部署还是单数据中心?**
   -- WHY: 多 DC 需要考虑跨区域复制延迟、一致性窗口、以及是否需要
   每个 DC 独立缓存层

### 不在设计范围内 (Out of Scope)

- 持久化存储引擎 (假设纯内存缓存，如需持久化用 Redis AOF/RDB)
- 复杂数据结构支持 (仅设计 KV 存储，不涉及 List/Set/SortedSet)
- 事务支持 (单键操作原子性即可)
- 全文搜索或二级索引
- 客户端 SDK 的具体实现
"""

# ---------------------------------------------------------------------------
# S2: Architecture (High-Level Design -- 10 min)
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 高层架构设计 (High-Level Architecture)

### 系统组件概览 (Component Overview)

```
Client Application
    |
    v
[Client Library / Smart Client]
    |  (consistent hashing -> route to correct node)
    v
+--------------------------------------------------+
|           Distributed Cache Cluster               |
|                                                   |
|  [Node 1]  [Node 2]  [Node 3]  ... [Node N]     |
|   (primary)  (primary)  (primary)                 |
|      |          |          |                      |
|  [Replica 1a] [Replica 2a] [Replica 3a]          |
|                                                   |
+--------------------------------------------------+
    |                          |
    v                          v
[Configuration Service]    [Monitoring / Metrics]
  (ZooKeeper / etcd)         (Prometheus + Grafana)
    |
    v
[Origin Data Store]
  (MySQL / PostgreSQL / DynamoDB)
```

### 核心组件与职责 (Core Components)

**1. Client Library / Smart Client (客户端库)**
- 维护一致性哈希环 (Consistent Hash Ring) 的本地副本
- 根据 key 计算哈希值，路由到对应的 Primary 节点
- 内置连接池 (Connection Pool)、重试逻辑、故障转移 (Failover) 到 Replica
- 可选: 内置 **L1 本地缓存 (Local Cache)** 拦截超热键，减少网络请求

**2. Cache Node (缓存节点)**
- 每个节点是一个独立进程，管理一片内存哈希表 (Hash Table)
- 内存数据结构: **开放寻址哈希表** (Open Addressing Hash Table) 或
  **链式哈希表** (Chained Hash Table) + **双向链表** (Doubly Linked List)
  用于 LRU 淘汰
- 支持多线程或 IO 多路复用 (epoll/kqueue) 处理并发请求
- 过期清理: 懒删除 (访问时检查) + 定期扫描 (每 100ms 随机抽样 20 个键)

**3. Consistent Hashing Ring (一致性哈希环)**
- 将 key 和 node 都映射到 $[0, 2^{32})$ 的哈希环上
- 每个物理节点对应 100-200 个**虚拟节点 (Virtual Nodes / VNodes)**，
  保证数据分布均匀
- 添加/移除节点时，只有相邻节点的数据需要迁移 (平均迁移 $1/N$)

**4. Replication Manager (复制管理器)**
- 每个 Primary 节点异步复制到 1-2 个 Replica 节点
- 复制方式: **异步复制 (Async Replication)** -- 写入 Primary 后立即返回
  客户端成功，后台推送到 Replica
- 故障检测: 心跳 (Heartbeat) + Gossip Protocol

**5. Configuration Service (配置服务)**
- 使用 **ZooKeeper** 或 **etcd** 存储集群拓扑 (节点列表、哈希环映射、
  Replica 分配)
- 节点加入/离开时，更新拓扑并通知所有 Client Library 刷新本地哈希环
- 提供 Leader Election 用于协调数据迁移

### 数据库选型 (Storage Choices)

| 数据类型 | 存储方案 | 理由 |
|---------|---------|------|
| 缓存数据 | **内存哈希表** | 亚毫秒读写，O(1) 查找 |
| 集群拓扑 | **ZooKeeper / etcd** | 强一致性、Watch 机制通知变更 |
| 监控指标 | **Prometheus TSDB** | 时序数据高效存储、PromQL 查询 |
| 源数据 | **MySQL / PostgreSQL** (外部) | 缓存的数据来源，非缓存系统本身管理 |

### 通信模式 (Communication Patterns)

- **同步 (TCP + 自定义二进制协议)**: Client <-> Cache Node 的 GET/PUT/DELETE
  操作，使用类似 Memcached 二进制协议或 Redis RESP 协议
- **异步 (Replication Stream)**: Primary -> Replica 的数据复制，基于操作日志
  (Operation Log) 流式推送
- **Pub/Sub (配置变更)**: ZooKeeper Watch / etcd Watch 通知 Client 和 Node
  集群拓扑变化
- **Gossip (节点健康)**: 节点间 Gossip Protocol 传播健康状态和故障信息
"""

# ---------------------------------------------------------------------------
# S3: Dataflow (API Design + Data Flow -- 5 min)
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 核心 API 端点 (Cache API)

#### 1. 读取缓存 (GET)
```
GET /cache/{key}

Response (200 OK -- Cache Hit):
{
  "key": "user:profile:12345",
  "value": "{\"name\": \"Alice\", \"avatar\": \"...\"}",
  "ttl_remaining_sec": 287,
  "version": 42
}

Response (404 Not Found -- Cache Miss):
{
  "key": "user:profile:12345",
  "status": "MISS"
}
```

#### 2. 写入缓存 (PUT)
```
PUT /cache/{key}
Content-Type: application/octet-stream

Request:
{
  "value": "{\"name\": \"Alice\", \"avatar\": \"...\"}",
  "ttl_sec": 3600,
  "flags": 0
}

Response (201 Created):
{
  "key": "user:profile:12345",
  "status": "STORED",
  "version": 43
}
```

#### 3. 删除缓存 (DELETE)
```
DELETE /cache/{key}

Response (200 OK):
{
  "key": "user:profile:12345",
  "status": "DELETED"
}
```

#### 4. 批量读取 (Multi-GET)
```
POST /cache/mget
{
  "keys": ["user:profile:12345", "user:profile:67890", "product:info:ABC"]
}

Response (200 OK):
{
  "results": {
    "user:profile:12345": {"value": "...", "ttl_remaining_sec": 287},
    "user:profile:67890": {"value": "...", "ttl_remaining_sec": 1024},
    "product:info:ABC": null   // cache miss
  },
  "hit_count": 2,
  "miss_count": 1
}
```

### 核心数据模型 (Data Model)

```
CacheEntry {
  key:        string       // 缓存键 (max 250 bytes)
  value:      bytes        // 缓存值 (max 1 MB)
  flags:      uint32       // 客户端自定义标志 (如压缩标记)
  ttl:        uint32       // 过期时间 (秒), 0 = 永不过期
  created_at: uint64       // 创建时间戳 (Unix ms)
  expire_at:  uint64       // 过期时间戳 (Unix ms), 0 = 永不过期
  version:    uint64       // 版本号 (用于 CAS 操作)
  cas_token:  uint64       // Compare-And-Swap token
  access_ts:  uint64       // 最后访问时间 (LRU 用)
  access_cnt: uint32       // 访问计数 (LFU 用)
}
```

### 读路径: Cache-Aside 模式 (Read Path)

**Cache-Aside (旁路缓存)** 是最常见的缓存模式，应用层负责协调缓存和数据库:

1. 客户端发起读请求 `GET user:profile:12345`
2. Client Library 计算 `hash("user:profile:12345") mod ring` 定位 Primary 节点
3. 向 Primary 节点发送 GET 请求 (TCP 连接池复用)
4. **Cache Hit**: 节点在内存哈希表中找到键，更新 LRU 链表位置 (移到头部)，
   返回 value + TTL
5. **Cache Miss**: 节点返回 MISS
6. 应用层查询 Origin DB (MySQL): `SELECT * FROM users WHERE id = 12345`
7. 应用层将结果写回缓存: `PUT user:profile:12345 {data} TTL=3600`
8. 返回结果给用户

```
Client --> [Cache: GET key] --> HIT? --> return value
                            --> MISS --> [DB: SELECT] --> [Cache: PUT key] --> return value
```

### 写路径: Write-Through vs Write-Behind (Write Path)

**方案 A: Cache-Aside (写时不更新缓存)**
1. 应用层写入 DB: `UPDATE users SET name='Bob' WHERE id=12345`
2. 应用层删除缓存: `DELETE user:profile:12345`
3. 下次读取时触发 Cache Miss，从 DB 重新加载 (Lazy Repopulation)

**方案 B: Write-Through (同步写穿)**
1. 应用层写入缓存 + DB (原子操作，先 DB 后缓存)
2. 缓存和 DB 始终一致，但写延迟增加 (多一次缓存写入)

**方案 C: Write-Behind / Write-Back (异步回写)**
1. 应用层仅写入缓存，立即返回
2. 缓存异步批量刷到 DB (Coalesce 合并多次写入)
3. 写性能最好，但存在数据丢失风险 (缓存节点故障时)

**设计选择**: 本系统默认使用 **Cache-Aside** 模式 -- 实现最简单、应用层
控制力最强、不引入写入耦合。对于写密集场景提供可选的 Write-Behind 模式。

### 异步路径: 缓存失效管道 (Cache Invalidation Pipeline)

对于需要强一致性的场景，引入 **CDC (Change Data Capture)** 驱动的主动失效:

1. DB 写入产生 binlog 变更事件
2. **Debezium** CDC 连接器捕获变更，发送到 Kafka topic
3. Cache Invalidation Consumer 消费事件，提取受影响的 cache key
4. 向对应的 Cache Node 发送 DELETE 命令
5. 下次读取触发 Cache Miss，从 DB 重新加载最新数据

```
[DB Write] --> [Binlog] --> [Debezium CDC] --> [Kafka] --> [Invalidation Consumer] --> [Cache DELETE]
```

这种方案将失效延迟控制在 **100-500ms**，远优于纯 TTL (可能数分钟)。
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Back-of-Envelope Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

**基础假设:**
- DAU: 5000 万
- 每用户每天平均 100 次缓存读取，10 次缓存写入
- 平均 value 大小: 1 KB
- 缓存命中率目标: 95%+
- 读写比: 10:1

**QPS 估算:**

$$
\text{读 QPS} = \frac{50M \times 100}{86400} \approx 57,870 \text{ QPS}
$$

$$
\text{峰值读 QPS} = 57,870 \times 3 \approx 173,600 \text{ QPS}
$$

$$
\text{写 QPS} = \frac{50M \times 10}{86400} \approx 5,787 \text{ QPS}
$$

$$
\text{峰值写 QPS} = 5,787 \times 3 \approx 17,360 \text{ QPS}
$$

**存储估算:**

$$
\text{每日新增数据} = 50M \times 10 \times 1\text{ KB} = 500 \text{ GB/day (写入量)}
$$

$$
\text{缓存容量 (去重后热数据)} = 50M \times 20 \text{ keys/user} \times 1\text{ KB} = 1 \text{ TB}
$$

考虑到缓存命中率 95%，实际需要缓存的热数据约为全量数据的 20%:

$$
\text{有效缓存容量} = 1\text{ TB} \times 20\% = 200 \text{ GB}
$$

**内存冗余 (含元数据开销):**

$$
\text{实际内存需求} = 200\text{ GB} \times 1.5 \text{ (元数据 + 碎片开销)} = 300 \text{ GB}
$$

**节点数估算:**

$$
\text{节点数 (按内存)} = \frac{300\text{ GB}}{64\text{ GB/node}} \approx 5 \text{ 节点}
$$

$$
\text{节点数 (按 QPS)} = \frac{173,600}{100,000 \text{ QPS/node}} \approx 2 \text{ 节点}
$$

取内存和 QPS 中的较大值，考虑 Replica 和冗余:

$$
\text{总节点数} = \max(5, 2) \times 2 \text{ (Primary + Replica)} = 10 \text{ 节点}
$$

**带宽估算:**

$$
\text{入带宽} = 17,360 \times 1\text{ KB} = 17 \text{ MB/s}
$$

$$
\text{出带宽} = 173,600 \times 1\text{ KB} = 170 \text{ MB/s}
$$

### 核心算法: 一致性哈希 (Consistent Hashing)

传统取模法 `hash(key) % N` 在节点数 $N$ 变化时，几乎所有键的映射都会改变
(需迁移 $(N-1)/N$ 的数据)。一致性哈希通过将键和节点都映射到同一个哈希环上
来解决这个问题。

**哈希环映射:**

$$
\text{position}(x) = \text{hash}(x) \mod 2^{32}
$$

其中 $x$ 可以是 cache key 或 node ID。键被映射到哈希环上**顺时针方向的
第一个节点**。

**虚拟节点 (Virtual Nodes):**

每个物理节点创建 $V$ 个虚拟节点 (通常 $V = 100 \sim 200$):

$$
\text{vnode}_{i,j} = \text{hash}(\text{node}_i + \text{"#"} + j), \quad j \in [0, V)
$$

虚拟节点的好处:
- 数据分布更均匀 (标准差从 $\sigma \propto 1/\sqrt{N}$ 降低到 $\sigma \propto 1/\sqrt{NV}$)
- 节点增减时，迁移数据量更稳定 (接近理想的 $1/N$)
- 可以根据节点配置 (内存大小) 分配不同数量的虚拟节点 (加权分配)

**数据迁移量:**

添加一个新节点到 $N$ 节点集群:

$$
\text{迁移比例} = \frac{1}{N+1}
$$

### 核心算法: LRU 淘汰 (LRU Eviction)

使用 **哈希表 + 双向链表 (HashMap + Doubly Linked List)** 实现 O(1) 的
GET / PUT / EVICT:

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[str, Node] = {}  # key -> DLL node
        self.head = Node("HEAD", None)    # most recently used
        self.tail = Node("TAIL", None)    # least recently used
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: str) -> bytes | None:
        if key not in self.cache:
            return None  # cache miss
        node = self.cache[key]
        self._move_to_head(node)  # mark as recently used
        return node.value

    def put(self, key: str, value: bytes) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                self._evict_lru()  # remove least recently used
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)

    def _evict_lru(self) -> None:
        lru_node = self.tail.prev
        self._remove(lru_node)
        del self.cache[lru_node.key]
```

时间复杂度:
- GET: $O(1)$ -- 哈希表查找 + 链表移动
- PUT: $O(1)$ -- 哈希表插入 + 链表头部添加
- EVICT: $O(1)$ -- 链表尾部移除 + 哈希表删除

### 核心算法: LFU 近似 -- TinyLFU

**TinyLFU** 是 Caffeine (Java 高性能缓存库) 使用的准入策略。它结合了
**Count-Min Sketch** (频率估计) 和 **Segmented LRU** (淘汰):

$$
\text{准入条件: } f_{\text{new}} > f_{\text{victim}}
$$

其中 $f$ 是通过 Count-Min Sketch 估算的访问频率。只有当新键的估算频率
大于即将被淘汰的键时，才允许新键进入缓存。

Count-Min Sketch 空间复杂度:

$$
\text{空间} = w \times d \times 4 \text{ bytes}
$$

其中 $w$ = 宽度 (通常 = 缓存容量的 10 倍)，$d$ = 深度 (通常 4 行)。
对于 100 万键的缓存，CMS 仅需 ~40 MB。

### 缓存穿透防护: 布隆过滤器 (Bloom Filter)

对于不存在于数据库中的键的查询 (缓存穿透, Cache Penetration)，使用
**Bloom Filter** 在缓存层前置过滤:

$$
\text{误判率} = \left(1 - e^{-kn/m}\right)^k
$$

其中 $n$ 是元素数量，$m$ 是 bit 数组大小，$k$ 是哈希函数个数。

对于 1 亿个键、1% 误判率:

$$
m = -\frac{n \ln p}{(\ln 2)^2} = -\frac{10^8 \times \ln 0.01}{(\ln 2)^2} \approx 958 \text{ MB} \approx 114 \text{ MB}
$$

$$
k = \frac{m}{n} \ln 2 = \frac{958 \times 10^6}{10^8} \times 0.693 \approx 7
$$
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability Deep Dive)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性深入分析 (Scale & Reliability Deep Dive)

### 具体规模数字 (Concrete Scale Numbers)

| 指标 | 数值 |
|------|------|
| DAU | 5000 万 |
| 峰值读 QPS | 173,600 |
| 峰值写 QPS | 17,360 |
| 缓存命中率 | 95%+ |
| 有效缓存容量 | 200 GB (300 GB 含元数据) |
| 集群节点数 | 10 (5 Primary + 5 Replica) |
| 单节点内存 | 64 GB |
| 出带宽 | 170 MB/s |
| 读延迟 P99 | < 1ms (同 DC) |
| 写延迟 P99 | < 5ms |

### 单点故障分析 (Single Point of Failure)

**1. Cache Node 故障**
- **检测**: Gossip Protocol 心跳超时 (3 秒) + Client 连接失败重试
- **自动故障转移**: Client Library 检测到 Primary 不可达后，自动切换到 Replica
  读取；Configuration Service 将 Replica 提升为新 Primary
- **数据恢复**: 新 Primary 从同步的 Replica 数据中恢复；缺失的部分通过
  Cache Miss 从 DB 重新加载 (Lazy Recovery)
- **影响**: 故障转移期间 (< 5 秒) 部分请求可能出现额外延迟或 Cache Miss

**2. Configuration Service 故障 (ZooKeeper / etcd)**
- **缓解**: ZooKeeper 本身是 3-5 节点集群，容忍少数派故障
- **降级**: 配置服务不可用时，Client 和 Node 使用本地缓存的拓扑继续工作；
  但无法进行扩缩容或故障转移

**3. 网络分区 (Network Partition)**
- **设计选择**: 优先可用性 (AP) -- 分区期间各侧继续服务，可能出现
  短暂数据不一致
- **恢复**: 分区愈合后，通过版本号 (version) 解决冲突 -- 保留最新版本

### 多数据中心考虑 (Multi-Datacenter)

**架构选择: 每 DC 独立缓存层 (Independent Cache per DC)**

```
[DC-East]                    [DC-West]
  App --> Cache Cluster        App --> Cache Cluster
      |                            |
      v                            v
  [DB Primary] ---replication--> [DB Replica]
```

- 每个 DC 有独立的缓存集群，不做跨 DC 缓存复制
- 缓存失效通过 **Kafka 跨 DC 复制** (MirrorMaker2) 传播失效事件
- 优点: 缓存读取完全本地化 (< 1ms)，不受跨 DC 延迟 (~50ms) 影响
- 缺点: 缓存冷启动 (DC 故障恢复后需要预热)、失效延迟约 100-500ms

**跨 DC 失效传播:**
1. DC-East 写入 DB 并删除本地缓存
2. CDC 事件通过 Kafka 同步到 DC-West
3. DC-West 的 Invalidation Consumer 删除对应缓存
4. 失效延迟 = Kafka 跨 DC 复制延迟 (~100ms) + Consumer 处理延迟 (~50ms)

### 高并发处理 (High Concurrency Handling)

**1. 连接池 (Connection Pooling)**
- Client Library 维护每个 Cache Node 的 TCP 连接池 (默认 10-50 连接)
- 使用 Pipeline 模式批量发送请求 (减少 RTT 开销)
- 连接复用减少 TCP 握手开销

**2. 缓存击穿防护 (Cache Stampede Prevention)**

当热键过期，大量并发请求同时触发 Cache Miss，全部打到 DB:

**解法 A: 分布式锁 (Distributed Lock / Singleflight)**
```python
def get_with_singleflight(key: str) -> bytes:
    value = cache.get(key)
    if value is not None:
        return value

    # Only one request per key rebuilds the cache
    lock_key = f"lock:{key}"
    if cache.setnx(lock_key, "1", ttl=5):
        try:
            value = db.query(key)
            cache.put(key, value, ttl=3600)
        finally:
            cache.delete(lock_key)
        return value
    else:
        # Wait and retry (other request is rebuilding)
        time.sleep(0.05)
        return get_with_singleflight(key)
```

**解法 B: 提前续期 (Early Refresh / Probabilistic Early Expiration)**

$$
\text{should\_refresh} = (t_{now} > t_{expire} - \text{TTL} \times \beta \times \ln(\text{random}()))
$$

其中 $\beta$ 是衰减因子 (通常 0.5-1.0)。TTL 到期前，少量请求会被
概率性地选中去刷新缓存，避免所有请求在过期瞬间同时触发重建。

**3. 热键处理 (Hot Key Mitigation)**

单个键的 QPS 可能达到单节点极限:

- **L1 本地缓存 (Local Cache)**: 应用进程内维护一个小型 LRU 缓存
  (如 Caffeine, 1000 个键)，拦截超热键。TTL 极短 (1-5 秒) 防止过期数据
- **键复制 (Key Replication)**: 将热键复制到 K 个额外节点:
  `hash(key + "#" + i), i in [0, K)`。读请求随机路由到 K+1 个副本之一
- **流量控制 (Rate Limiting)**: 对单键 QPS 设上限，超出部分返回缓存的
  稍旧版本 (Serve Stale)

**4. 缓存雪崩防护 (Cache Avalanche Prevention)**

大量键同时过期导致 Cache Miss 风暴:

$$
\text{jittered\_ttl} = \text{base\_ttl} + \text{random}(0, \text{jitter\_range})
$$

例如 base TTL = 3600 秒, jitter = 300 秒。每个键的实际过期时间在
3600-3900 秒之间随机分布，避免集体过期。

### 监控与告警 (Monitoring & Alerting)

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| 缓存命中率 | < 90% | P1 Critical |
| 读延迟 P99 | > 5ms | P2 Warning |
| 写延迟 P99 | > 20ms | P2 Warning |
| 内存使用率 | > 85% | P2 Warning |
| 内存使用率 | > 95% | P1 Critical (大量淘汰即将发生) |
| 淘汰速率 (eviction/s) | > 1000/s | P2 Warning |
| 连接数 | > 80% of max | P2 Warning |
| 节点不可达 | 任何节点 | P1 Critical |
| 复制延迟 | > 1s | P2 Warning |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs (Trade-off Discussion -- 10 min)
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 关键权衡讨论 (Trade-off Discussion)

### 核心设计决策 (Key Design Decisions)

| 决策点 | 方案 A | 方案 B | 我们的选择与理由 |
|--------|--------|--------|----------------|
| 缓存模式 | **Cache-Aside** (应用层管理) | **Write-Through** (缓存代理写入 DB) | **Cache-Aside** -- 应用层控制力最强，实现简单，不引入写入耦合；Write-Through 对写延迟影响大且需缓存层有 DB 写权限 |
| 数据分布 | **一致性哈希 + 虚拟节点** | **Range-based 分区** | **一致性哈希** -- 节点增减时迁移数据量最小 ($1/N$)；Range 分区在热点范围集中时容易不均匀 |
| 路由方式 | **Client-side 路由** (Smart Client) | **Proxy 路由** (Twemproxy/Envoy) | **Client-side** -- 少一跳网络延迟 (~0.5ms)，适合对延迟极敏感的缓存场景；Proxy 更适合客户端多语言且无法维护 Smart Client 的情况 |
| 复制方式 | **异步复制** | **同步复制** | **异步复制** -- 写延迟不增加 (不等 Replica ACK)；可接受故障时丢失最近几秒的写入。同步复制将写延迟翻倍且降低可用性 (Replica 故障阻塞写入) |
| 淘汰策略 | **LRU** (最近最少使用) | **LFU** (最不经常使用) | **LRU 为默认，可选 LFU** -- LRU 实现简单、通用性好；LFU 在扫描型访问模式下表现更好但实现复杂。提供 TinyLFU 作为高级选项 |

### 一致性 vs 可用性 (CAP Trade-off)

本系统选择 **AP (可用性优先)**:
- 缓存是性能优化层，不是数据的唯一来源 (Source of Truth)
- 短暂过期数据 (Stale Data) 可接受 -- 最差情况下等 TTL 过期即可
- 如果选 CP，缓存故障就会导致请求失败，违背缓存"提升可用性"的初衷

**一致性窗口 (Consistency Window):**
- 纯 TTL 模式: 最大不一致窗口 = TTL 值 (如 1 小时)
- CDC 主动失效: 最大不一致窗口 = 100-500ms
- Write-Through: 最大不一致窗口 = 0 (但降低写性能和可用性)

### 成本 vs 性能 (Cost vs Performance)

| 维度 | 低成本方案 | 高性能方案 | 平衡点 |
|------|-----------|-----------|--------|
| 内存 | 小容量 + 高淘汰率 | 大容量 + 低淘汰率 | 内存使用率 70-85% 为甜蜜点 |
| 复制 | 无 Replica (省 50% 内存) | 每 Primary 2 个 Replica | 1 Replica 兼顾 HA 和成本 |
| 序列化 | JSON (人类可读) | Protobuf / MessagePack | Protobuf -- 体积减少 30-50%，解析速度快 3-5x |
| 压缩 | 不压缩 (CPU 省) | LZ4/Snappy 压缩 | 对 > 1KB 的 value 启用 LZ4 (压缩率 50%，CPU 开销 < 1%) |

### 10x / 100x 规模扩展

**当前规模 (1x):** 5 Primary + 5 Replica, 200 GB 缓存, 173K 读 QPS

**10x 规模 (5 亿 DAU, 1.7M 读 QPS):**
- 节点扩展: 50 Primary + 50 Replica
- 引入 **L1 本地缓存**: 每个应用实例 1 GB 本地 LRU，拦截 30-50% 热请求
- 引入 **Proxy 层** (Envoy): 统一管理连接池，避免 Client 直连所有节点
  (连接数爆炸: 100 个 App 实例 x 50 个 Cache Node x 50 连接 = 250K 连接)
- CDC 失效管道: 多 Consumer 并行，按 key 哈希分区处理

**100x 规模 (50 亿 DAU, 17M 读 QPS):**
- **多层缓存 (Multi-tier Cache)**: L1 (进程内) -> L2 (同 DC 共享) -> L3 (跨 DC)
- **定制硬件**: DPDK 用户态网络栈绕过内核 TCP，减少 context switch
- **Active-Active 多 DC**: 每个 DC 独立缓存，通过 Kafka 事件流同步失效
- **分层 TTL**: 热数据短 TTL + 频繁刷新; 温数据长 TTL; 冷数据不缓存
- **可能需要定制缓存引擎** (如 Facebook 的 CacheLib): 统一 DRAM + SSD
  两层存储，SSD 作为 DRAM 的溢出层 (spill-over)
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问与防御 (Interviewer Follow-up Q&A)

### Q1: 如果一个缓存节点完全宕机，该节点上的所有数据丢失怎么办?

**承认局限**: 纯内存缓存在节点故障时确实会丢失该节点的所有数据。对于异步复制，
Replica 可能缺少最近几秒的写入。

**缓解措施**:
1. **自动故障转移 (Automatic Failover)**: Client Library 检测到 Primary 不可达
   (3 次重试超时，共 ~1 秒)，自动切换到 Replica 读取。Configuration Service
   将 Replica 提升为新 Primary (< 5 秒完成)
2. **Lazy Recovery**: 缺失的数据通过正常的 Cache Miss 路径从 DB 重新加载。
   对于热数据，重建速度很快 (高访问频率 = 快速缓存预热)
3. **Cache Warming (预热)**: 对于可预测的热数据 (如 Top 1000 商品)，新节点
   启动时主动从 DB 加载，减少冷启动期间的 DB 压力
4. **流量整形**: 故障恢复期间，对从新节点返回 MISS 的请求进行速率限制
   (Rate Limiting)，防止所有请求同时打到 DB (即缓存雪崩)

**数据支撑**: 在 10 节点集群中，单节点故障仅影响 ~10% 的键。95% 命中率在
故障后短暂降至 ~85%，但在 2-5 分钟内随着热数据重建恢复到 93%+。

### Q2: 缓存和数据库的数据不一致怎么办? 用户更新了数据但还是看到旧值?

**承认局限**: Cache-Aside 模式下，DB 写入和缓存删除之间存在时间窗口。在
高并发下，还可能出现经典的"双写不一致" (Double-Write Inconsistency) 问题。

**缓解措施**:
1. **延迟双删 (Delayed Double Delete)**:
   - 步骤: 删除缓存 -> 写入 DB -> 等 500ms -> 再次删除缓存
   - 第二次删除解决了"先删缓存、另一个请求读到旧 DB 值并写回缓存"的竞态
2. **CDC 兜底 (Change Data Capture)**:
   - Binlog 是 DB 变更的权威来源，CDC 管道保证最终一致性
   - 即使应用层删除缓存失败，CDC 也会在 100-500ms 内补删
3. **版本号校验 (Version Check)**:
   - 每次写入 DB 时递增 version 字段
   - 缓存写入时携带 version，使用 CAS (Compare-And-Swap): 仅当缓存中的
     version < 新 version 时才更新，防止旧值覆盖新值
4. **业务层容忍**: 对于非关键场景 (如用户头像)，短暂不一致可接受；
   对于关键场景 (如余额)，绕过缓存直读 DB

**设计选择**: 默认使用 TTL + CDC 双保险。TTL 保证最终过期 (兜底)，
CDC 保证快速失效 (常态)。极端一致性场景直读 DB。

### Q3: 如果某个键突然变得极度热门 (如微博热搜)，QPS 从 100 飙升到 10 万怎么办?

**承认局限**: 一致性哈希将同一个键固定路由到同一个节点，单节点最多承受
~100K QPS，极端热键可能导致该节点过载。

**缓解措施**:
1. **L1 本地缓存 (Local Cache)**:
   - 应用进程内 LRU 缓存 (如 Caffeine)，容量 1000-5000 键
   - TTL 极短 (1-5 秒)，既减轻远程缓存压力又限制过期窗口
   - 100 个应用实例各自缓存 = 有效分散 100 倍负载
2. **键复制 (Key Replication)**:
   - 自动检测热键 (QPS > 阈值 K)，复制到 R 个额外节点
   - 客户端读取时随机选择一个副本: `node = hash(key + "#" + random(0, R))`
   - R = 5 时，单键承载能力提升 6 倍
3. **热键发现 (Hot Key Detection)**:
   - 每个 Cache Node 维护一个 Top-K Heavy Hitters 统计 (Count-Min Sketch)
   - 每 10 秒上报热键列表到 Configuration Service
   - Configuration Service 广播热键列表到所有 Client，触发本地缓存

**数据支撑**: Twitter 的 Cache 层使用 L1 + L2 二级缓存架构，L1 在应用实例内
拦截约 40% 的请求。微博热搜场景下，L1 命中率可达 80%+。

### Q4: 如何应对缓存穿透 -- 大量查询数据库中不存在的键?

**承认局限**: Cache-Aside 对不存在的键永远返回 MISS，每次都查 DB。恶意攻击者
可以用随机不存在的键发起大量请求，绕过缓存直接压垮 DB。

**缓解措施**:
1. **Bloom Filter 前置过滤**:
   - 在缓存层前放置 Bloom Filter，存储所有有效键的指纹
   - 查询时先检查 Bloom Filter: 如果返回"不存在"则 100% 不存在，直接返回 MISS
   - 1 亿键 + 1% 误判率仅需 ~114 MB 内存
2. **空值缓存 (Cache Null / Negative Caching)**:
   - 对 DB 查询结果为空的键，缓存一个特殊空值，TTL 较短 (如 30-60 秒)
   - 防止同一个不存在的键反复查 DB
3. **请求校验 (Input Validation)**:
   - 在 API Gateway 层校验 key 格式 (如 `user:profile:\d+`)
   - 不符合格式的 key 直接拒绝，不到达缓存层
4. **速率限制 (Rate Limiting)**:
   - 对单个客户端的 Cache Miss 率进行监控
   - Miss 率异常高的客户端 (> 50%) 触发限流

**数据支撑**: Bloom Filter + 空值缓存的组合可将穿透请求减少 99.9%+。
Google 的 Bigtable 在每个 SSTable 中使用 Bloom Filter 减少无效磁盘读取。

### Q5: 集群需要从 10 节点扩容到 20 节点，如何做到不停机、不丢数据?

**承认局限**: 一致性哈希保证只迁移约 $1/N$ 的数据，但迁移过程中如果处理不当，
可能出现"双写"或"读不到"的问题。

**缓解措施**:
1. **两阶段迁移 (Two-Phase Migration)**:
   - **Phase 1 (双写)**: 新节点加入哈希环，但旧节点仍保留被迁移的数据。
     写入同时写到新旧节点 (双写); 读取优先从新节点读，Miss 时回退到旧节点
   - **Phase 2 (清理)**: 确认迁移完成后 (新节点已有完整数据)，从旧节点
     删除已迁移的键，更新路由表
2. **后台数据迁移 (Background Migration)**:
   - 旧节点启动后台任务，逐批扫描并发送属于新节点的键
   - 限速迁移 (如每秒 1000 键)，避免影响正常流量
3. **版本化路由表 (Versioned Routing)**:
   - 每次拓扑变更生成新版本的路由表
   - Client Library 原子切换到新路由表 (CAS 更新)
   - 短暂的路由不一致通过"新节点 Miss -> 旧节点回退"解决

**数据支撑**: Redis Cluster 的 resharding 支持在线迁移 slot (类似 VNode)。
对于 10 -> 20 节点扩容，迁移约 50% 的数据 (每个旧节点迁出一半)，
在 100Mbps 限速下，迁移 100 GB 数据约需 15 分钟。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试口述大纲 (1-Hour Interview Pacing Guide)

### 三分钟电梯演讲版 (3-Minute Elevator Pitch)

"设计分布式缓存的核心挑战是**在节点动态变化的集群中，提供亚毫秒级的数据
访问，同时保证数据分布均匀和高可用**。我的方案有三个关键设计:

**第一: 数据分布**。使用**一致性哈希 + 虚拟节点** (每个物理节点 150 个 VNode)
将键均匀分布到集群中。节点增减时只需迁移约 $1/N$ 的数据，配合两阶段在线
迁移实现无停机扩缩容。

**第二: 多层防护**。缓存穿透用 Bloom Filter 前置过滤; 缓存击穿用 Singleflight
分布式锁保证只有一个请求重建缓存; 缓存雪崩用 TTL 抖动 (Jitter) 打散过期
时间; 热键用 L1 本地缓存 + 键复制分散压力。

**第三: 一致性保障**。默认 Cache-Aside 模式配合 TTL 兜底。关键业务引入
CDC 管道 (Debezium -> Kafka -> Invalidation Consumer)，将缓存失效延迟
控制在 100-500ms。极端场景使用延迟双删消除竞态条件。

整体架构 AP 优先，5 Primary + 5 Replica 异步复制，承载 200 GB 缓存、
173K 峰值读 QPS，故障转移 < 5 秒。"

---

### 完整一小时面试节奏 (Full 1-Hour Pacing)

#### 0-5 分钟: 需求澄清 (Requirements Clarification)
- **开场**: "分布式缓存的核心目标是用内存空间换取访问延迟和数据库压力。
  让我先澄清几个关键需求。"
- 确认数据模型: 纯 KV 还是复杂结构 (本设计聚焦 KV)
- 确认是否需要持久化 (本设计假设纯内存，重启需预热)
- 确认路由方式: Client-side vs Proxy (本设计选 Client-side)
- 列出 FR / NFR:
  - FR: GET/PUT/DELETE, 批量操作, TTL 自动过期, LRU 淘汰
  - NFR: 99.99% 可用性, 读 P99 < 1ms, 单节点 100K+ QPS
- 明确 Out of Scope: 持久化引擎、复杂数据结构、事务

#### 5-15 分钟: 高层架构 (High-Level Architecture)
- 画出 4 个核心组件: Client Library, Cache Nodes, Replication, Config Service
- **一致性哈希环**:
  - 为什么不用简单取模: 节点变化时迁移 $(N-1)/N$ 数据
  - 虚拟节点: 每个物理节点 150 个 VNode，解决数据倾斜
  - 加权分配: 大内存节点多分 VNode
- **数据存储**: 内存哈希表 + LRU 双向链表
- **通信协议**: 二进制协议 (类 RESP)，TCP 长连接 + 连接池

#### 15-25 分钟: 深入缓存模式与一致性 (Deep Dive: Caching Patterns)
- **Cache-Aside 读写路径**: 7 步走通
- **缓存失效三种策略**: TTL (简单)、应用层删除 (主动)、CDC (强一致)
- **重点讨论双写不一致问题**:
  - 场景: 线程 A 删缓存 -> 线程 B 读 DB (旧值) 写缓存 -> 线程 A 写 DB
  - 解法: 延迟双删、CDC 兜底、版本号 CAS
- Write-Through vs Write-Behind: 何时选择，各自代价

#### 25-35 分钟: 深入防护机制 (Deep Dive: Cache Protection)
- **缓存穿透**: Bloom Filter (误判率公式、空间计算)、空值缓存、输入校验
- **缓存击穿**: Singleflight 分布式锁、概率提前刷新 (PER 公式)
- **缓存雪崩**: TTL Jitter、集群健康检查、降级策略 (返回过期数据)
- **热键**: L1 本地缓存、键复制、热键自动发现 (CMS Top-K)
- 这四个场景是面试高频追问点，每个用一句话总结防护策略

#### 35-40 分钟: 容量估算 (Capacity Estimation)
- 快速走一遍关键数字:
  - 读 QPS: 平均 57K, 峰值 173K
  - 写 QPS: 平均 5.7K, 峰值 17K
  - 缓存容量: 200 GB (300 GB 含元数据)
  - 节点: 5 Primary + 5 Replica (64 GB 每节点)
  - 带宽: 入 17 MB/s, 出 170 MB/s

#### 40-50 分钟: 权衡与扩展 (Trade-offs & Scaling)
- 一致性 vs 可用性: AP 优先，缓存不是 Source of Truth
- Client-side vs Proxy 路由: 延迟 vs 运维复杂度
- 异步 vs 同步复制: 写延迟 vs 数据安全
- 10x 规模: 50+50 节点, L1 本地缓存, Proxy 层
- 100x 规模: 多层缓存 (L1/L2/L3), 定制引擎 (CacheLib), DPDK

#### 50-55 分钟: 收尾 (Wrap-up)
- **如果有更多时间我会改进什么**:
  - DRAM + NVMe SSD 两层存储 (CacheLib 风格)，成本降低 60%
  - 自适应淘汰策略 (根据工作负载自动选择 LRU/LFU/ARC)
  - 热键自动发现 + 自动复制 (无人工干预)
- **监控优先级**: 命中率、P99 延迟、淘汰速率、复制延迟
- **最大风险**: 缓存雪崩 (大面积过期) -- 已通过 TTL Jitter + 降级缓解

#### 55-60 分钟: 提问环节 (Questions for Interviewer)
- "你们的缓存集群规模和命中率大概是多少? 有没有遇到过热键问题?"
- "你们使用 Redis Cluster 还是自研缓存? 选择的主要考虑是什么?"
"""


# ---------------------------------------------------------------------------
# Main: Populate DB
# ---------------------------------------------------------------------------
def populate_interview_distributed_cache() -> None:
    """Insert or update the interview-distributed-cache SystemDesign record."""
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
    populate_interview_distributed_cache()
