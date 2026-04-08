"""Populate database-comparison system design module with all 8 sections.

Usage:
    python scripts/content_database_comparison.py

Covers Cassandra, HBase, DynamoDB, ScyllaDB, CockroachDB, TiDB, MongoDB.
Idempotent: overwrites existing content for the database-comparison slug.

SOURCE OF TRUTH: Chinese. All content is in Chinese with English technical
terms preserved. This script IS the authoritative content -- DB content
that diverges from this script will be overwritten on next run.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

# ---------------------------------------------------------------------------
# Section 1: Overview & Motivation
# ---------------------------------------------------------------------------

OVERVIEW = r"""## 概述与动机 (Overview & Motivation)

### 数据库选型的重要性

在系统设计面试中，数据库的选择绝不仅仅是技术偏好——它是一个**根本性的架构决策**，会制约后续所有的设计选择：一致性保证、故障模式、扩展策略和运维成本。面试官通过"为什么选 X 而不选 Y？"来考察你是否真正理解其中的权衡取舍，还是仅仅在堆砌名词。

### 选型框架

数据库选型本质上是一个**约束满足问题 (Constraint Satisfaction Problem)**：

| 约束维度 | 核心问题 |
|-----------|----------|
| **数据模型** | 数据是关系型、键值型、文档型还是宽列型？ |
| **一致性** | 需要线性一致性读取，还是最终一致性即可？ |
| **规模** | 读写 QPS 目标是多少？数据总量多大？ |
| **延迟** | p50/p99 延迟预算是多少？ |
| **运维** | 自建还是托管？团队技术栈是什么？ |
| **成本** | 按容量预留还是按请求付费？ |

### 本模块涵盖的数据库

本模块在两个 **CAP (Consistency, Availability, Partition tolerance)** 分类下比较七种分布式数据库：

**AP 系统 (Availability + Partition Tolerance，可用性优先)：**
- **Cassandra**：环形拓扑，可调一致性，**LSM (Log-Structured Merge-tree)** 存储引擎
- **ScyllaDB**：兼容 Cassandra，C++ 实现的 shard-per-core 架构重写
- **DynamoDB**：AWS 全托管，支持预留/按需容量模式

**CP 系统 (Consistency + Partition Tolerance，一致性优先)：**
- **HBase**：主从架构，基于 **HDFS (Hadoop Distributed File System)**，Hadoop 生态
- **CockroachDB**：分布式 SQL，**Raft** 共识协议，可序列化隔离
- **TiDB/TiKV**：基于 Raft 的 **MVCC (Multi-Version Concurrency Control)**，兼容 MySQL，支持 **HTAP (Hybrid Transactional/Analytical Processing)**

**混合型：**
- **MongoDB**：文档模型，副本集，可配置一致性

### 本模块的核心关注点

这不是一份功能对比表格。本模块聚焦于每种数据库设计背后的**架构原因**、这些设计所带来的**权衡取舍**，以及如何在面试中**清晰表达这些权衡**。每个章节都回扣面试核心问题："给定你的需求，为什么选这个数据库而不是那个？"
"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## 架构深入解析 (Architecture Deep Dive)

### Cassandra

**拓扑结构**：基于一致性哈希的对等环形架构。没有单一主节点——每个节点都能处理读写请求。**虚拟节点 (vnodes)** 将 token 范围分配到物理节点上，实现负载均衡。

**存储引擎**：**LSM-tree (Log-Structured Merge-tree)** 引擎。写入先进入 commit log（**WAL, Write-Ahead Log**）和内存中的 memtable。当 memtable 达到阈值后，刷写为不可变的 **SSTable (Sorted String Table)**。后台压缩合并 SSTable。

**副本复制**：可配置的复制因子（**RF, Replication Factor**）。数据根据分区器在 token 环上的位置复制到 RF 个节点。支持机架感知和数据中心感知的副本策略。

**一致性**：每次查询可调。一致性级别包括 ONE、QUORUM、ALL、LOCAL_QUORUM、EACH_QUORUM。仲裁公式 `R + W > N` 决定了给定的读/写组合是否提供强一致性。

**Gossip 协议**：节点通过定期 gossip 轮次交换状态信息（存活性、token 归属、schema 版本）。故障检测使用累积故障检测器（phi accrual）而非二元心跳。

---

### HBase

**拓扑结构**：主从架构。HMaster 负责 Region 分配和 schema 操作。RegionServer 承载数据 Region。ZooKeeper 提供选主和分布式协调。

**存储引擎**：基于 **HDFS (Hadoop Distributed File System)** 的列族模型。写入先进入 WAL（在 HDFS 上）和内存中的 MemStore。MemStore 刷写为 HFile（不可变、有序）。压缩合并 HFile。HDFS 通过 3 倍块副本提供持久性。

**一致性**：设计上即为强一致性——每个 Region 只由一个 RegionServer 服务。对给定行的所有读写都通过同一台服务器。没有最终一致性模式。

**故障处理**：当 RegionServer 宕机时，HMaster 通过 ZooKeeper 会话超时检测，然后将 Region 重新分配给其他服务器。恢复过程从 HDFS 回放 WAL。恢复时间通常为 30 秒至 2 分钟。

---

### DynamoDB

**拓扑结构**：全托管、基于分区。AWS 处理所有副本复制、分片和故障恢复。数据根据分区键哈希值分布到各分区。

**存储引擎**：对用户透明——AWS 管理底层存储引擎。每个分区跨 3 个 **AZ (Availability Zone，可用区)** 复制。存储节点内部使用 B-tree 和类 SSTable 结构的组合。

**容量模式**：两种模式——预留模式（固定 **RCU/WCU, Read/Write Capacity Unit**）和按需模式（按请求付费）。Auto-scaling 根据流量模式调整预留容量。突发容量可吸收短期峰值。

**一致性**：默认为最终一致性读取（更快、更便宜）。可按请求选择强一致性读取（RCU 消耗翻倍）。DynamoDB Transactions 提供跨最多 100 个项目的 **ACID (Atomicity, Consistency, Isolation, Durability)** 保证。

**DAX (DynamoDB Accelerator)**：内存缓存层。缓存命中时读延迟为微秒级。写透缓存模式。

---

### ScyllaDB

**拓扑结构**：与 Cassandra 相同的环形拓扑——兼容 **CQL (Cassandra Query Language)**，使用相同的驱动和运维模型。

**核心差异**：用 C++ 编写，采用 shard-per-core 架构。每个 CPU 核心拥有专属的数据分片，运行在无共享模型下（Seastar 框架）。没有 JVM，没有垃圾回收停顿。

**性能**：消除了 Cassandra 的两大延迟来源：JVM **GC (Garbage Collection)** 停顿（可导致 100ms+ 的 p99 尖刺）和跨核竞争。ScyllaDB 在每节点吞吐量上达到 2-5 倍提升，同时具备更低的尾部延迟。

**自动内存管理**：不同于 JVM 堆调优，ScyllaDB 在应用层通过显式分配池管理内存。没有全局停顿（stop-the-world）。

---

### CockroachDB

**拓扑结构**：对称节点，无主节点。数据被划分为 Range（默认 512MB）。每个 Range 是一个 **Raft** 共识组，由一个 leaseholder 负责服务读请求并提议写请求。

**存储引擎**：Pebble（受 RocksDB 启发的 Go 语言 LSM-tree 引擎）。**MVCC (Multi-Version Concurrency Control)** 实现多版本并发控制。时间戳采用 **HLC (Hybrid-Logical Clock，混合逻辑时钟)**。

**一致性**：默认可序列化隔离——最强的标准 SQL 隔离级别。每个事务看起来都在单一时间点原子执行。

**地理分区**：Range 可以固定到特定区域以满足数据驻留合规要求（例如 EU 数据留在 EU）。Follower reads 允许非 leaseholder 副本服务历史读取。

**SQL 兼容性**：支持 PostgreSQL 线协议。大多数 PostgreSQL ORM 和工具只需最小改动即可使用。

---

### TiDB / TiKV

**拓扑结构**：计算层（TiDB）和存储层（TiKV）分离。TiKV 是基于 Raft 副本的分布式键值存储。TiDB 是无状态的 SQL 层，解析 MySQL 协议查询并将计算下推到 TiKV。

**存储引擎**：TiKV 每个节点使用 RocksDB（LSM-tree）。数据被划分为 Region（默认 96MB）。每个 Region 是一个 Raft 组。

**HTAP (Hybrid Transactional/Analytical Processing)**：TiFlash 是列式存储引擎，通过 Raft learner 副本从 TiKV 复制数据。这使得无需 **ETL (Extract, Transform, Load)** 流水线即可对 OLTP 数据执行实时 OLAP 查询。

**一致性**：基于 Raft 的副本复制提供强一致性。MVCC 配合快照隔离（**SI, Snapshot Isolation**）或可重复读（**RR, Repeatable Read**）。

---

### MongoDB

**拓扑结构**：副本集（主节点 + 从节点）提供高可用。分片通过 shard key 将数据分布到多个副本集。

**存储引擎**：WiredTiger 引擎（B-tree + LSM 混合，默认 B-tree）。文档级并发控制。日志（journaling）保证持久性。

**数据模型**：**BSON (Binary JSON)** 文档——灵活 schema、嵌套对象、数组。存储层不支持 JOIN（应用层通过 `$lookup` 聚合实现）。

**一致性**：可配置的写关注级别（w:1, w:majority, w:all）和读关注级别（local, majority, linearizable, snapshot）。当 w:majority 配合 read concern majority 时，提供因果一致性。

**事务**：自 4.0 起支持多文档 ACID 事务。自 4.2 起支持跨分片事务。性能开销显著——应尽量缩小事务范围。
"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 写入路径比较

#### Cassandra / ScyllaDB（LSM-tree）

```
Client Write
  |-> Coordinator node (any node, determined by token)
  |-> Send to RF replica nodes in parallel
  |   |-> Each replica:
  |   |     1. Append to Commit Log (WAL) -- sequential disk I/O
  |   |     2. Write to Memtable (in-memory sorted structure)
  |   |     3. Ack to coordinator
  |-> Coordinator waits for CL-level acks (e.g., QUORUM = RF/2+1)
  |-> Return success to client
  |
  [Background] Memtable full -> flush to SSTable (immutable, sorted)
  [Background] Compaction merges SSTables (size-tiered or leveled)
```

**核心洞察**：写入是顺序 I/O（追加日志 + memtable 插入）。这使得 **LSM-tree (Log-Structured Merge-tree)** 数据库天然是写优化的。代价在后续的压缩（写放大）和读取（需检查多个 **SSTable (Sorted String Table)**）时支付。

#### HBase（WAL + MemStore on HDFS）

```
Client Write
  |-> RegionServer for the target region
  |   1. Append to WAL (on HDFS -- 3x replicated)
  |   2. Write to MemStore (in-memory)
  |   3. Ack to client
  |
  [Background] MemStore full -> flush to HFile on HDFS
  [Background] Compaction merges HFiles
```

**与 Cassandra 的关键区别**：HBase 的 WAL 位于 **HDFS (Hadoop Distributed File System)** 上（持久性依赖网络 I/O），而非本地磁盘。这增加了延迟但提供了更强的持久性保证。单主/Region 模式意味着无需冲突解决。

#### CockroachDB / TiDB（Raft 共识）

```
Client Write (SQL)
  |-> Parse SQL -> Determine affected ranges
  |-> For each range:
  |   1. Leaseholder proposes write to Raft group
  |   2. Raft leader replicates to majority of followers
  |   3. On majority ack -> commit to local engine (Pebble/RocksDB)
  |   4. Ack to SQL layer
  |-> Transaction coordinator commits (2PC for multi-range txns)
  |-> Return success to client
```

**核心洞察**：每次写入都需要共识（**Raft** 多数派确认）。这是强一致性的代价。写入延迟取决于多数派中最慢成员的响应时间加上网络往返。

#### DynamoDB（托管服务）

```
Client Write (PutItem)
  |-> Router determines partition
  |-> Write to leader replica in target partition
  |   1. Persist to local storage
  |   2. Replicate to 2 other AZ replicas
  |   3. On majority ack -> return success
  |
  [Internal] Storage compaction, partition splitting -- all managed
```

### 读取路径比较

#### LSM-tree 读取（Cassandra, ScyllaDB, HBase）

```
Client Read
  |-> Check Memtable/MemStore (most recent data)
  |-> Check Bloom filters for each SSTable/HFile
  |   (Bloom filter: false positive ~1%, no false negatives)
  |-> Read matching SSTables (may need to check multiple levels)
  |-> Merge results (latest timestamp wins)
  |-> Return to client
```

**读放大**：最坏情况下，一个键可能存在于多个层级的多个 SSTable 中。分层压缩（Leveled Compaction）通过确保每个键在每一层最多存在于一个 SSTable 来减少读放大。

#### B-tree 读取（CockroachDB, MongoDB）

```
Client Read
  |-> Traverse B-tree index: root -> internal -> leaf
  |-> Direct page read (no multiple-file search)
  |-> Return to client
```

**优势**：可预测的读性能——O(log N) 次页面读取。没有压缩相关的读放大。

### 一致性模型

| 模型 | 保证 | 适用数据库 |
|------|------|-----------|
| **最终一致性 (Eventual)** | 副本随时间收敛 | Cassandra (CL=ONE), DynamoDB (默认) |
| **可调一致性 (Tunable)** | 每次查询可调一致性级别 | Cassandra (R+W>N), DynamoDB (按请求) |
| **强一致性-单主 (Strong, single-leader)** | 所有读取看到最新写入 | HBase, MongoDB (w:majority + read:linearizable) |
| **可序列化 (Serializable)** | 事务表现为串行执行 | CockroachDB, TiDB |
| **因果一致性 (Causal)** | 尊重 happens-before 关系 | MongoDB (sessions), Cassandra (LWTs) |

### 反熵机制（Cassandra/ScyllaDB）

- **读修复 (Read Repair)**：在 QUORUM 读取时，若副本间数据不一致，协调节点将最新版本发送给过期副本（后台修复）
- **提示切换 (Hinted Handoff)**：写入时若目标副本宕机，协调节点暂存"提示"，待副本恢复后转发
- **反熵修复 (Anti-Entropy Repair)**：副本间的完整 **Merkle tree（默克尔树）** 比较，检测并修复数据分歧（定期调度，资源密集型）
"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 一致性哈希 (Consistent Hashing)

标准哈希函数将键映射到大小为 $2^{128}$（或 $2^{64}$）的哈希环上。每个节点拥有环上一段连续的 token 范围。

**朴素一致性哈希的问题**：添加/移除节点只影响其紧邻节点，但在节点数较少时负载分布不均匀。

**虚拟节点 (vnodes)**：每个物理节点拥有 $V$ 个虚拟位置（Cassandra 默认 $V = 256$）。这提供了：
- 跨节点的均匀负载分布
- 节点加入/离开时的增量再均衡
- 对异构硬件的支持（性能更强的机器分配更多 vnodes）

**Token 分配公式**：对于 $N$ 个节点、每个节点 $V$ 个 vnodes：
$$\text{Total tokens} = N \times V$$

$$\text{Expected data per node} = \frac{\text{Total data}}{N}$$

### 复制因子与仲裁 (Replication Factor and Quorum)

对于复制因子 $RF$（通常为 3）：

$$\text{Quorum} = \lfloor RF / 2 \rfloor + 1$$

要实现强一致性，读取次数 ($R$) 和写入次数 ($W$) 必须满足：

$$R + W > RF$$

常见配置：
| 配置 | R | W | 一致性 | 可用性 |
|------|---|---|--------|--------|
| **ONE/ONE** | 1 | 1 | 最终一致 | 最高（可容忍 RF-1 个故障） |
| **QUORUM/QUORUM** | 2 | 2 | 强一致 | 中等（RF=3 时可容忍 1 个故障） |
| **ONE/ALL** | 1 | 3 | 强一致读 | 写可用性受限 |
| **ALL/ONE** | 3 | 1 | 强一致写 | 读可用性受限 |

### 布隆过滤器 (Bloom Filter)

空间高效的概率数据结构。对于 $n$ 个元素和期望误判率 $p$：

$$m = -\frac{n \ln p}{(\ln 2)^2}$$

其中 $m$ 是所需的位数。最优哈希函数数量：

$$k = \frac{m}{n} \ln 2$$

**Cassandra 中的应用**：每个 **SSTable (Sorted String Table)** 维护一个布隆过滤器。读取 SSTable 前先检查布隆过滤器，若返回"不存在"，则直接跳过该 SSTable。将读放大从 $O(\text{num SSTables})$ 降低到期望 $O(1)$。

### 默克尔树用于反熵修复 (Merkle Trees for Anti-Entropy)

每个副本为给定 token 范围的数据构建默克尔树：
- 叶节点：单行数据的哈希值
- 内部节点：子节点哈希的哈希值
- 根节点：代表整个数据集的单一哈希值

**比较过程**：两个副本交换根哈希。若匹配，则数据一致。若不匹配，则递归进入子树定位具体分歧行。复杂度：在 $N$ 行数据中找到 $k$ 行分歧的比较次数为 $O(\log N)$。

### Raft 共识算法（CockroachDB, TiKV）

**选主 (Leader Election)**：候选节点请求投票。候选者获得多数票（$N$ 个节点中的 $\lfloor N/2 \rfloor + 1$ 票）即当选。

**日志复制 (Log Replication)**：Leader 将条目追加到自己的日志并复制给 follower。当多数节点持久化该条目后，该条目即为已提交。

**延迟**：写入延迟至少为 2 次网络往返：
1. Client -> Leader（提议）
2. Leader -> Followers -> Leader（复制 + 多数派确认）
3. Leader -> Client（提交确认）

对于跨地域部署：
$$\text{Write latency} \geq 2 \times \text{RTT to farthest majority member}$$

### 分区键设计 (Partition Key Design)

**热分区问题**：若所有流量集中在少数分区键上，无论集群有多少节点，这些分区都会成为瓶颈。

**复合分区键**：组合多个字段以分散负载。例如：用 `(user_id, date_bucket)` 替代 `user_id`，将单个用户的数据分散到多个分区。

**写分片公式**：对于吞吐量为 $T$ 的热键和目标单分片吞吐量 $t$：
$$\text{Shard count} = \lceil T / t \rceil$$

在分区键后追加分片后缀 `0..shard_count-1`。读取时必须对所有分片进行 scatter-gather。

### 容量规划公式 (Capacity Planning)

**存储容量估算**：对于日增 $D$ GB 数据，复制因子 $RF$，压缩开销因子 $C$（通常 1.5-2.0），保留天数 $T$：

$$\text{Total storage} = D \times RF \times C \times T$$

**节点数估算**：对于目标每节点数据量 $S_{\text{node}}$（推荐值见扩展上限表）：

$$N_{\text{nodes}} = \left\lceil \frac{\text{Total storage}}{S_{\text{node}}} \right\rceil$$

**吞吐量估算**：对于目标 QPS 为 $Q$，每节点安全吞吐 $q$：

$$N_{\text{throughput}} = \left\lceil \frac{Q \times RF_{\text{write}}}{q} \right\rceil$$

最终集群大小取 $\max(N_{\text{nodes}}, N_{\text{throughput}})$，再加上至少 30% 的余量应对峰值和运维操作（如滚动升级时一个节点离线）。
"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

### 各工作负载的延迟特征

| 数据库 | p50 读 | p99 读 | p50 写 | p99 写 | 备注 |
|--------|--------|--------|--------|--------|------|
| **Cassandra** | 1-2ms | 5-15ms | 0.5-1ms | 3-10ms | JVM **GC (Garbage Collection)** 可导致 p99.9 飙升至 100ms+ |
| **ScyllaDB** | 0.5-1ms | 2-5ms | 0.3-0.5ms | 1-3ms | 无 GC 停顿；尾部延迟可预测 |
| **DynamoDB** | 2-5ms | 8-15ms | 3-5ms | 10-20ms | 网络开销；**DAX (DynamoDB Accelerator)** 可将读降至 <1ms |
| **HBase** | 1-3ms | 10-30ms | 1-2ms | 5-20ms | HDFS 跳转增加延迟；热 Region 导致尖刺 |
| **CockroachDB** | 2-5ms | 10-25ms | 5-10ms | 15-40ms | Raft 共识增加写延迟 |
| **TiDB** | 2-5ms | 10-25ms | 5-10ms | 15-30ms | 与 CockroachDB 类似；TiFlash 用于分析 |
| **MongoDB** | 0.5-2ms | 5-15ms | 1-3ms | 5-20ms | WiredTiger 缓存命中 = 快；缓存未命中 = 慢 |

### 运维复杂度

| 数据库 | 部署方式 | 所需专业度 | 主要痛点 |
|--------|----------|-----------|----------|
| **Cassandra** | 自建或托管 (Astra) | 中高 | 压缩调优、墓碑管理、修复调度 |
| **ScyllaDB** | 自建或 ScyllaDB Cloud | 中 | 较少 JVM 调优项，但仍需压缩策略 |
| **DynamoDB** | 全托管 | 低 | 容量规划、热分区检测、成本控制 |
| **HBase** | 自建 (Hadoop 生态) | 高 | ZooKeeper 管理、HDFS 运维、Region 分裂 |
| **CockroachDB** | 自建或 Cockroach Cloud | 中 | Range 再均衡、leaseholder 放置、时钟偏移 |
| **TiDB** | 自建或 TiDB Cloud | 高 | 多组件部署（**PD (Placement Driver)**, TiKV, TiDB, TiFlash） |
| **MongoDB** | 自建或 Atlas | 中 | shard key 选择（不可变！）、均衡器调优 |

### 成本模型

#### 自建方案（Cassandra/HBase/ScyllaDB）
- **计算资源**：最少 3-9 个节点（RF=3，多机架）
- **存储**：Cassandra/ScyllaDB 使用本地 SSD；HBase 需要 HDFS 集群
- **运维团队**：小集群需 0.5-1 名全职人员，100+ 节点需 2-3 名
- **成本**：$5K-$50K/月，视规模而定（不含人员成本）

#### 托管方案（DynamoDB）
- **预留模式**：$0.00065/WCU/小时, $0.00013/RCU/小时
- **按需模式**：$1.25/百万 WRU, $0.25/百万 RRU
- **存储**：$0.25/GB/月
- **陷阱**：设计不当的 schema 若产生热分区，成本可能是优化 schema 的 10-50 倍
- **盈亏平衡点**：DynamoDB 在 <100 万请求/天时更便宜；Cassandra 自建在大规模（>1000 万请求/天）时更划算

#### 托管 SQL（CockroachDB Serverless, TiDB Cloud）
- **CockroachDB Serverless**：按 **RU (Request Unit)** 计费，有免费层
- **TiDB Cloud**：按节点计费，类似 RDS
- **成本**：同等吞吐量下每查询成本比 Cassandra/DynamoDB 高 2-5 倍，但节省了一致性保证的工程投入

### 扩展上限

| 数据库 | 最大集群规模 | 每节点最大数据量 | 扩展模型 |
|--------|-------------|-----------------|----------|
| **Cassandra** | 1000+ 节点 | 推荐 1-2TB | 线性水平扩展 |
| **ScyllaDB** | 1000+ 节点 | 2-5TB（单节点性能更强） | 线性水平扩展 |
| **DynamoDB** | 无限制（托管） | 10GB/分区 | 自动分区 |
| **HBase** | 200+ RegionServer | 1-2TB/RS | 水平扩展（受 ZK 限制） |
| **CockroachDB** | 200+ 节点（已验证） | 无硬性限制 | 水平扩展，基于 Range |
| **MongoDB** | 1000+ 分片 | 无硬性限制 | 水平扩展，基于 shard |
"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### CAP 定理：实际应用

**CAP (Consistency, Availability, Partition tolerance)** 定理指出，分布式系统最多只能同时满足三项保证中的两项：一致性、可用性、分区容错性。由于网络分区不可避免，实际选择就是 **AP vs. CP**。

**何时选择 AP（Cassandra, ScyllaDB, DynamoDB）：**
- 面向用户的系统，延迟比完美一致性更重要
- 指标、日志、时序数据（last-write-wins 可接受）
- 购物车、社交信息流、推荐存储
- 多数据中心部署，跨数据中心延迟使强一致性不切实际
- 高写入吞吐需求（>100K writes/sec）

**何时选择 CP（HBase, CockroachDB, TiDB）：**
- 金融交易、支付处理
- 库存管理（超卖不可接受）
- 用户认证/授权状态
- 任何"读到旧数据 -> 做出错误操作 -> 不可逆后果"的场景
- 数据一致性的监管要求

### Schema 灵活性 vs. 查询能力

| 维度 | 宽列型 (Cassandra) | 文档型 (MongoDB) | 关系型 (CockroachDB) |
|------|-------------------|-----------------|---------------------|
| **Schema** | 固定列族，灵活列 | 灵活（无 schema 约束） | 严格（需 DDL） |
| **查询** | 仅主键查询（无即席查询） | 丰富查询、聚合 | 完整 SQL、JOIN、子查询 |
| **索引** | 有限的二级索引 | 二级索引、全文搜索 | 标准 B-tree 索引 |
| **关联查询** | 不支持 | 客户端 `$lookup` | 原生 JOIN |
| **Schema 演进** | 自由添加列，无需 ALTER TABLE | 自由添加字段 | ALTER TABLE（可能锁表） |

**核心权衡**：Cassandra 的查询限制是设计使然——数据模型必须围绕查询模式设计。若需即席查询，需要维护多张反范式化表（每个查询模式一张表）。这是写性能和水平扩展能力的代价。

### 运维负担 vs. 功能丰富度

```
                    Low Ops -------- High Ops
                       |               |
  DynamoDB -----+                      |
                |                      |
  MongoDB  -----+------+              |
                       |              |
  ScyllaDB ----+------+------+       |
                              |       |
  CockroachDB +------+------+       |
                              |       |
  Cassandra ---+------+------+------+
                                     |
  HBase ------+------+------+------+
                                     |
  TiDB -------+------+------+------+
```

**DynamoDB** 运维负担最低（全托管），但灵活性最差（厂商锁定、分区键约束、大规模下成本高）。

**HBase/TiDB** 运维负担最高（多组件部署、Hadoop/PD 依赖），但功能强大（强一致性、二级索引、**HTAP (Hybrid Transactional/Analytical Processing)**）。

### 写优化 vs. 读优化

| 存储引擎 | 写性能 | 读性能 | 空间放大 |
|----------|--------|--------|----------|
| **LSM-tree (Log-Structured Merge-tree)**（Cassandra, ScyllaDB, HBase） | 优秀（顺序 I/O） | 良好（布隆过滤器辅助） | 中等（压缩控制） |
| **B-tree**（MongoDB, CockroachDB 内部） | 良好（随机 I/O） | 优秀（直接查找） | 低（原地更新） |

**写放大**（LSM）：数据在 SSTable 跨层压缩过程中被多次写入。分层压缩：写放大约 10-30 倍。大小分层压缩：写放大约 4-8 倍。

**读放大**（LSM）：点查询可能需要检查多个 SSTable。分层压缩将每层限制为最多 1 个 SSTable。布隆过滤器减少不必要的读取。

**权衡**：若工作负载 >80% 为写入（日志、指标、IoT），LSM-tree 数据库胜出。若工作负载 >80% 为随机访问读取，B-tree 数据库提供更可预测的性能。

### 厂商锁定

| 数据库 | 锁定风险 | 迁移路径 |
|--------|----------|----------|
| **DynamoDB** | **高**——专有 API，无自建选项 | 迁移至 Cassandra/ScyllaDB（不同数据模型） |
| **Cassandra** | **低**——开源，CQL 可移植 | ScyllaDB（直接替换）, DataStax Astra（托管） |
| **ScyllaDB** | **低**——兼容 Cassandra | Cassandra（反向迁移）, ScyllaDB Cloud |
| **HBase** | **中**——绑定 Hadoop/HDFS 生态 | Cassandra（不同模型）, Cloud BigTable（API 兼容） |
| **CockroachDB** | **低**——兼容 PostgreSQL | PostgreSQL（单节点）, 其他 NewSQL |
| **TiDB** | **低**——兼容 MySQL | MySQL（单节点）, 其他 NewSQL |
| **MongoDB** | **中**——专有 BSON, Atlas 专属功能 | DocumentDB（部分兼容）, 自建 MongoDB |

### 数据库迁移策略 (Database Migration Strategy)

生产数据库迁移是高风险操作。三种主流策略按风险从低到高排列：

#### 1. 双写 + 影子读 (Dual-Write + Shadow Read)

```
Application
  |-> Write to OLD database (primary)
  |-> Write to NEW database (shadow)
  |
  Read path:
  |-> Read from OLD (serve to user)
  |-> Read from NEW (compare, log diff, discard)
```

**阶段**：
1. **影子写入期**（2-4 周）：双写，仅从旧库读取，比对新旧库结果。指标：不一致率 <0.01% 才进入下一阶段。
2. **影子读取期**（1-2 周）：双读，仍以旧库结果为准，验证新库延迟和正确性。
3. **切换**：将读流量切到新库。旧库保持只读 48 小时作为回退窗口。
4. **下线**：停止对旧库的写入，归档数据。

**适用场景**：Cassandra -> ScyllaDB（schema 兼容）、MongoDB -> DynamoDB（需数据模型转换层）。

**代价**：迁移期间写吞吐翻倍，需要额外的比对和差异修复流水线。

#### 2. CDC 流式迁移 (Change Data Capture Streaming)

使用 **CDC (Change Data Capture)** 捕获旧库变更，通过流处理（Kafka/Debezium）同步到新库：

```
Old DB -> CDC stream -> Kafka -> Consumer -> New DB
         (binlog/WAL)         (transform)
```

**优势**：无需应用层双写，减少代码侵入。支持schema 转换和过滤。**风险**：CDC 延迟导致新旧库短暂不一致；需处理 CDC 消费者的幂等性和乱序。

#### 3. 停机迁移 (Stop-the-World Migration)

适用于数据量 <1TB 且允许停机的场景。导出旧库 -> 转换 -> 导入新库。简单可靠但需计划停机窗口（通常安排在流量低谷）。

### 迭代与评估：我们如何验证选型 (Iteration & Evaluation)

数据库选型不是一次性决策——系统上线后需要持续验证选型假设。这是区分中级和 Staff+ 级别回答的关键环节。

#### 评估方法论 (Evaluation Methodology)

| 层级 | 方法 | 周期 | 用途 |
|------|------|------|------|
| **基准测试 (Benchmark)** | YCSB / 自定义负载生成器 | 选型前 + 季度 | 验证吞吐/延迟假设 |
| **影子流量测试 (Shadow Traffic)** | 生产流量复制到候选库 | 1-4 周 | 验证真实工作负载下的性能 |
| **金丝雀部署 (Canary)** | 1-5% 流量切到新库 | 天级 | 发现长尾问题（热分区、GC 尖刺） |
| **全量 A/B** | 按用户分流 | 1-2 周 | 端到端业务指标（延迟、错误率、成本） |

#### 关键监控指标 (Key Metrics to Monitor)

选型后的持续验证关注以下指标的趋势：

- **p99 延迟趋势**：随数据量增长，LSM-tree 数据库的读延迟是否在压缩策略下保持稳定？
- **写放大比率**：通过 `compaction_bytes_written / user_bytes_written` 监控，若 >20x 需调优压缩策略
- **热分区检测**：分区级 QPS 分布的基尼系数（Gini coefficient），$G > 0.8$ 表示严重倾斜
- **容量利用率**：磁盘使用 >70% 时需扩容（LSM 压缩需要临时空间）
- **Raft 选举频率**（CP 系统）：频繁选举暗示网络不稳或时钟偏移

#### 典型失败模式与修复 (Typical Failure Modes & Fixes)

1. **脑裂 (Split Brain)**：在网络分区期间，AP 系统的不同分区各自接受写入，
   分区恢复后产生冲突数据。**根因**：使用 CL=ONE 写入且无冲突解决策略。
   **修复**：(a) 使用 LWW (Last-Write-Wins) 时间戳解决——接受"最后一次写入
   获胜"语义。(b) 对不可接受 LWW 的场景（如计数器），使用 **CRDT (Conflict-free
   Replicated Data Type)** 如 PN-Counter。(c) 关键路径改用 QUORUM 或 LOCAL_QUORUM
   一致性级别。

2. **压缩风暴导致写暂停 (Compaction Storm Write Stall)**：LSM-tree 数据库
   在 L0 SSTable 积压时触发写暂停（write stall），等待压缩追上写入速度。
   表现为写延迟突然从 <1ms 飙升至秒级。**根因**：写入速率超过压缩能力，
   或压缩线程资源不足。**修复**：(a) 增加压缩并发线程数（Cassandra:
   `concurrent_compactors`）。(b) 切换压缩策略：写密集场景使用 **STCS
   (Size-Tiered Compaction Strategy)**，读密集场景使用 **LCS (Leveled
   Compaction Strategy)**。(c) ScyllaDB 的 shard-per-core 架构通过每核独立
   压缩缓解此问题。

3. **热分区级联故障 (Hot Partition Cascade)**：单个热分区键消耗节点大部分
   资源，导致该节点上的其他分区也受影响，触发连锁延迟升高。在 DynamoDB 中，
   热分区可消耗所有预留容量，导致其他分区被限流。**根因**：分区键设计不当
   （如用日期作为分区键，所有当天写入集中在一个分区）。**修复**：(a) 写分片：
   在分区键后追加随机后缀（0..N-1），读时 scatter-gather。(b) DynamoDB：
   开启按需模式或使用 **DAX** 缓存热读。(c) 监控：设置分区级 QPS 告警，
   基尼系数 $G > 0.8$ 时触发。
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## 对抗性问答防御 (Adversarial Defense Q&A)

---

**Q: 为什么不直接用 PostgreSQL 加读副本？**

> PostgreSQL 加读副本在一定规模内运作良好。其局限性在于：
>
> 1. **写扩展**：单写架构。所有写入经过一个主节点。若需 >50K writes/sec，就会触及天花板。PostgreSQL 分片是可行的（Citus），但显著增加复杂度。
>
> 2. **副本延迟**：流式复制默认异步。读副本可能落后数秒。同步复制存在但会增加与最慢副本成正比的写延迟。
>
> 3. **地理分布**：多区域的 PostgreSQL 副本意味着每次写入都有跨区域延迟（50-200ms）。Cassandra 通过 LOCAL_QUORUM 解决——本地写入快速完成，异步复制到远程数据中心。
>
> 4. **运维扩展**：添加读副本很容易。增加写容量需要应用层分片、连接路由和跨分片查询处理。Cassandra/CockroachDB 透明地处理这些。
>
> **何时 PostgreSQL 才是正确答案**：若数据能放在一台高配机器上（最多约 10TB），需要复杂的 JOIN 查询，写吞吐适中（<10K/sec），且团队熟悉 PostgreSQL——就用 PostgreSQL。引入不必要的分布式复杂性才是更大的错误。

---

**Q: Cassandra 没有事务——如何处理 X？**

> 首先，Cassandra 确实有 **LWT (Lightweight Transaction，轻量级事务)**，使用 Paxos 实现比较并交换操作。它们比普通写入慢 4-10 倍，但为单分区操作提供线性一致性。
>
> 对于更广泛的事务需求，常用模式包括：
>
> 1. **幂等写入**：将操作设计为可安全重试。使用 `INSERT IF NOT EXISTS` 做去重。使用 `UPDATE ... IF column = expected` 做乐观并发。
>
> 2. **Saga 模式**：对于多步操作，实现补偿事务。每一步都有对应的撤销操作。若第 3 步失败，撤销第 2 步和第 1 步。
>
> 3. **Outbox 模式**：将事件和状态变更写入同一分区（Cassandra 中单分区写入是原子的）。独立进程读取 outbox 并发布事件。
>
> 4. **接受最终一致性**：对很多场景（计数器、last-write-wins 状态），最终一致性实际上是可以接受的。业务可以容忍购物车显示一个稍显过时的状态持续 100ms。
>
> **坦诚的局限**：若需要多行、多表的 ACID 事务，Cassandra 是错误的选择。应使用 CockroachDB、TiDB 或 PostgreSQL。

---

**Q: 什么时候不应该使用 Cassandra？**

> Cassandra 不适合以下场景：
>
> 1. **即席查询**：Cassandra 要求围绕查询模式设计表。若查询不可预测（BI、分析、探索性查询），应使用灵活查询的数据库（PostgreSQL、TiDB 或数据仓库）。
>
> 2. **小数据量/低流量**：低于约 1TB 或约 10K QPS 时，Cassandra 的运维开销不划算。单个 PostgreSQL 或 MongoDB 实例更简单、更便宜，且提供更丰富的查询能力。
>
> 3. **所有操作都需强一致性**：虽然 Cassandra 可以做 QUORUM 读写，但它本质为 AP 工作负载设计。若每个操作都需可序列化一致性，CockroachDB 或 TiDB 更合适。
>
> 4. **大量读-改-写操作**：Cassandra 是写优化的。"读一行、修改、写回"的模式需要 LWT 或外部锁，这会抵消 Cassandra 的性能优势。
>
> 5. **少量大型二进制对象**：Cassandra 理论上单 cell 限制为 2GB，但值 >1MB 时性能很差。大型对象应使用对象存储（S3），在 Cassandra 中只存引用。

---

**Q: 大规模下如何处理二级索引？**

> Cassandra 原生二级索引（2i）是**本地索引**——每个节点只索引自己的数据。对二级索引的查询必须散射到所有节点（fan-out），复杂度为 O(N)（N 为集群大小）。这对小集群上的低基数列可以接受，但无法扩展。
>
> **更好的方案**：
>
> 1. **物化视图/反范式化表**：创建单独的表，以查询列作为分区键。用写放大（维护多张表）换取读性能。这是 Cassandra 原生模式。
>
> 2. **SAI (Storage-Attached Indexes，存储附加索引)**：Cassandra 较新的特性（5.0+）。比 2i 更高效——使用按 SSTable 的索引结构。仍为本地索引，但性能特征更优。
>
> 3. **外部搜索索引**：写入 Cassandra 作为主存储，通过 **CDC (Change Data Capture，变更数据捕获)** 或幂等双写复制到 Elasticsearch/Solr 做搜索查询。
>
> 4. **ScyllaDB 方案**：ScyllaDB 的二级索引同样需要散射，但 shard-per-core 架构更高效地处理 fan-out。仍不建议用于高 QPS 的二级索引查询。

---

**Q: DynamoDB 很贵。如何控制成本？**

> DynamoDB 的成本陷阱及应对：
>
> 1. **热分区**：单个热分区键可能消耗所有预留容量。通过 `ConsumedCapacity` 监控每个分区。解决方案：写分片（给热键追加随机后缀）或切换到按需模式。
>
> 2. **Scan 操作**：全表扫描消耗的 RCU 与表大小成正比，而非结果大小。生产代码中绝不要使用 Scan。使用 **GSI (Global Secondary Index)** 或重新设计访问模式。
>
> 3. **过度预留**：预留模式需要预估流量。使用 auto-scaling 并设置 70% 目标利用率。对不可预测的工作负载，按需模式消除浪费（但大流量下每请求成本更高）。
>
> 4. **GSI 膨胀**：每个 GSI 复制整张表的数据。5 个 GSI = 5 倍存储成本 + 5 倍写成本。谨慎设计 GSI——每个都应服务于高价值的访问模式。
>
> 5. **预留容量**：对稳定负载，预留容量（1 年或 3 年）可降低 50-75% 的成本。
>
> **盈亏平衡分析**：在约 5 亿请求/月且流量可预测的情况下，使用预留 EC2 实例自建 Cassandra 通常比 DynamoDB 预留模式便宜 60-80%。

---

**Q: CockroachDB 自称"NewSQL"——它真的比 PostgreSQL 快吗？**

> 不。在单节点性能上，CockroachDB **慢于** PostgreSQL。每次写入都需要 Raft 共识（即使在开发环境中 RF=1，代码路径仍包含共识开销）。简单查询在同等硬件上比 PostgreSQL 慢 2-5 倍。
>
> CockroachDB 的价值在于**强一致性下的水平扩展能力**。当数据集超出单个 PostgreSQL 节点的承载能力时，CockroachDB 无需应用层分片即可横向扩展。每查询成本更高，但系统总吞吐量随节点数线性增长。
>
> **CockroachDB 胜出的场景**：
> - 数据集 >5TB（超出单节点 PostgreSQL 能力）
> - 写吞吐 >20K/sec（超出单写节点能力）
> - 多区域部署，需要本地读取和全局一致性
> - 需要扩展但不想重构应用架构
>
> **PostgreSQL 胜出的场景**：
> - 数据可放在单台机器上
> - 需要 PostgreSQL 扩展生态（PostGIS, pg_vector 等）
> - 单查询最大性能很重要
> - 团队专长在 PostgreSQL
"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## 口述大纲 (Verbal Outline)

### 3 分钟版本

**目标**：被问到"你会如何为这个系统选择数据库？"时的电梯演讲。

1. **(30s) 框架**：数据库选型是一个约束满足问题。关键维度包括：数据模型、一致性需求、规模目标、延迟预算和运维能力。**CAP (Consistency, Availability, Partition tolerance)** 定理在分区发生时强制在 AP（可用性优先）和 CP（一致性优先）之间做出选择。

2. **(45s) AP 系统**：对于高吞吐、延迟敏感的工作负载——面向用户的服务、指标、时序数据——选择 Cassandra 或 ScyllaDB。环形拓扑，**LSM-tree (Log-Structured Merge-tree)** 存储，可调一致性。ScyllaDB 通过 C++ shard-per-core 消除 JVM **GC (Garbage Collection)** 停顿。如果希望零运维但接受厂商锁定和大规模下更高成本，选 DynamoDB。

3. **(45s) CP 系统**：对于事务型工作负载——支付、库存、认证——选择 CockroachDB 或 TiDB。**Raft** 共识，可序列化隔离，SQL 兼容。权衡：更高的写延迟（共识往返）和更低的单节点吞吐。HBase 适用于 Hadoop 原生的强一致性场景。

4. **(30s) 核心权衡**：写优化（LSM）vs. 读优化（B-tree）。Schema 灵活性 vs. 查询能力。运维负担 vs. 托管便捷性。正确答案取决于具体需求——没有放之四海而皆准的最佳数据库。

5. **(30s) 选型法则**：从满足需求的最简方案开始（通常是 PostgreSQL）。只有在单节点达到瓶颈时才引入分布式数据库：数据 >10TB、写入 >20K/sec，或多区域需求。

### 10 分钟版本

**目标**：深入的系统设计面试轮次，数据库选型是关键组成部分。

1. **(1.5 min) 问题陈述与选型框架**
   - 数据库选型为何重要：它制约一致性、故障模式、扩展策略和成本
   - 六维框架：数据模型、一致性、规模、延迟、运维、成本
   - CAP 定理作为实际的 AP vs. CP 决策，而非纯理论约束

2. **(2 min) 架构对比**
   - Cassandra：环形 + 一致性哈希 + gossip + LSM-tree
   - CockroachDB：对称节点 + 每 Range Raft + Pebble LSM
   - DynamoDB：托管分区 + auto-scaling
   - 核心架构差异：对等式 vs. 共识式 vs. 托管式
   - 各架构如何处理节点故障和恢复

3. **(2 min) 读写路径深入**
   - LSM-tree 写路径：WAL -> Memtable -> SSTable -> compaction
   - Raft 写路径：propose -> 复制到多数派 -> commit
   - LSM 的读放大 vs. B-tree 的直接查找
   - 布隆过滤器、压缩策略（size-tiered, leveled, **TWCS (Time-Window Compaction Strategy)**）

4. **(1.5 min) 一致性模型**
   - 最终一致、可调一致（R+W>N）、强一致（单主）、可序列化（共识）
   - 反熵机制：读修复、提示切换、默克尔树修复
   - 仲裁数学配合具体示例

5. **(1.5 min) 生产环境约束**
   - 延迟特征：按数据库和工作负载类型的 p50/p99
   - 运维复杂度谱：DynamoDB（零运维）到 HBase（全职 DBA）
   - 成本分析：托管 vs. 自建的盈亏平衡点

6. **(1.5 min) 权衡分析与选型标准**
   - AP 适用于面向用户、延迟敏感、高写入的工作负载
   - CP 适用于事务型、一致性关键的工作负载
   - Schema 灵活性 vs. 查询能力的权衡
   - 迁移策略：双写影子读、CDC 流式、停机迁移的选择标准
   - "从 PostgreSQL 开始"法则及何时升级到分布式方案

### 面试过渡用语

在与其他系统设计话题衔接时：

- **从具体设计出发**："对于消息队列的元数据，我会选 Cassandra，因为我们需要高写入吞吐，且消息确认可以容忍最终一致性。"
- **论证选择**："我在这里选 CockroachDB 而非 Cassandra 的原因是，库存管理需要可序列化事务——超卖产品比稍高的写延迟后果严重得多。"
- **被质疑时**："你说得对，以我们目前的规模 PostgreSQL 完全可以胜任。我设计时选择 Cassandra 是因为 10 倍增长预期——在 500K writes/sec 时，我们需要手动分片 PostgreSQL，这带来的运维复杂度与运行 Cassandra 相当，却没有内置的多数据中心复制能力。"
"""


# ---------------------------------------------------------------------------
# Main: update the database record
# ---------------------------------------------------------------------------

def populate_database_comparison() -> None:
    """Find the database-comparison SystemDesign record and update all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == "database-comparison")
            .first()
        )

        if record is None:
            print("[FAIL] No SystemDesign record with slug='database-comparison' found.")
            print("       Run scripts/seed_system_designs.py first to create the record.")
            sys.exit(1)

        record.overview = OVERVIEW
        record.architecture = ARCHITECTURE
        record.dataflow = DATAFLOW
        record.formulas = FORMULAS
        record.production_constraints = PRODUCTION_CONSTRAINTS
        record.tradeoffs = TRADEOFFS
        record.defense = DEFENSE
        record.verbal_outline = VERBAL_OUTLINE

        db.commit()
        print("[DONE] Updated all 8 sections for database-comparison.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            "overview", "architecture", "dataflow", "formulas",
            "production_constraints", "tradeoffs", "defense", "verbal_outline",
        ]
        total = 0
        for section in sections:
            content = getattr(record, section)
            length = len(content) if content else 0
            total += length
            cn_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {section}: {length} chars, {cn_chars} CN chars {status}")

        print(f"\n  TOTAL: {total} chars")

        # Count display math, Q&A, failure modes
        all_content = "\n".join(
            getattr(record, s) or "" for s in sections
        )
        display_math = all_content.count("$$")
        qa_count = all_content.count("**Q:")
        failure_count = len(
            [line for line in all_content.split("\n")
             if "**修复**" in line or "Fixes)" in line]
        )
        bare_pipe_in_math = 0
        in_math = False
        for line in all_content.split("\n"):
            if "$$" in line:
                in_math = not in_math
            elif in_math and "|" in line and "\\mid" not in line:
                bare_pipe_in_math += 1
            elif "$" in line:
                # inline math check
                parts = line.split("$")
                for i in range(1, len(parts), 2):
                    if "|" in parts[i] and "\\mid" not in parts[i]:
                        bare_pipe_in_math += 1

        print(f"  Display math ($$): {display_math // 2} blocks")
        print(f"  Q&A: {qa_count}")
        print(f"  Failure modes: {failure_count}")
        print(f"  Bare | in math: {bare_pipe_in_math}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database_comparison()
