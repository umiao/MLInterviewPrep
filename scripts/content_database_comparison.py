"""Populate database-comparison system design module with all 8 sections.

Usage:
    python scripts/content_database_comparison.py

Covers Cassandra, HBase, DynamoDB, ScyllaDB, CockroachDB, TiDB, MongoDB.
Idempotent: overwrites existing content for the database-comparison slug.
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

OVERVIEW = r"""## Overview & Motivation

### Why Database Selection Matters

In system design interviews, the database choice is rarely just a technology
preference -- it is a **fundamental architectural decision** that constrains
every downstream design choice: consistency guarantees, failure modes, scaling
strategy, and operational cost. Interviewers use "why did you choose X over Y?"
to probe whether you understand the trade-offs or are just name-dropping.

### The Selection Framework

Database selection is a **constraint satisfaction problem**:

| Constraint | Question |
|-----------|----------|
| **Data model** | Is the data relational, key-value, document, or wide-column? |
| **Consistency** | Do we need linearizable reads, or is eventual consistency acceptable? |
| **Scale** | What are the write/read QPS targets? Data volume? |
| **Latency** | What are p50/p99 latency budgets? |
| **Operational** | Self-hosted vs. managed? Team expertise? |
| **Cost** | Predictable capacity vs. pay-per-request? |

### The Databases in This Module

This module compares seven distributed databases across two CAP categories:

**AP Systems (Availability + Partition Tolerance):**
- **Cassandra**: Ring topology, tunable consistency, LSM-tree storage
- **ScyllaDB**: Cassandra-compatible, C++ shard-per-core rewrite
- **DynamoDB**: Fully managed AWS, provisioned/on-demand capacity

**CP Systems (Consistency + Partition Tolerance):**
- **HBase**: Master-slave, HDFS-backed, Hadoop ecosystem
- **CockroachDB**: Distributed SQL, Raft consensus, serializable isolation
- **TiDB/TiKV**: Raft-based MVCC, MySQL-compatible, HTAP

**Hybrid:**
- **MongoDB**: Document model, replica sets, configurable consistency

### What This Module Covers

Not a feature comparison spreadsheet. This module focuses on the **architectural
reasons** behind each database's design, the **trade-offs** those designs force,
and how to **articulate those trade-offs** in an interview setting. Every section
connects back to the interview question: "Given your requirements, why this
database and not that one?"
"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## Architecture Deep Dive

### Cassandra

**Topology**: Peer-to-peer ring with consistent hashing. No single master --
every node can serve reads and writes. Virtual nodes (vnodes) distribute
token ranges across physical nodes for balanced load.

**Storage**: LSM-tree engine. Writes go to a commit log (WAL) and an in-memory
memtable. When the memtable reaches threshold, it flushes to an immutable
SSTable on disk. Background compaction merges SSTables.

**Replication**: Configurable replication factor (RF). Data is replicated to
RF nodes determined by the partitioner's token ring placement. Supports
rack-aware and datacenter-aware replication strategies.

**Consistency**: Tunable per-query. Consistency levels: ONE, QUORUM, ALL,
LOCAL_QUORUM, EACH_QUORUM. The quorum formula `R + W > N` determines
whether a given read/write combination provides strong consistency.

**Gossip Protocol**: Nodes exchange state information (liveness, token
ownership, schema version) via periodic gossip rounds. Failure detection
uses an accrual failure detector (phi accrual) rather than binary heartbeats.

---

### HBase

**Topology**: Master-slave. HMaster coordinates region assignment and schema
operations. RegionServers host data regions. ZooKeeper provides leader
election and distributed coordination.

**Storage**: Column-family model on HDFS. Writes go to a WAL (on HDFS) and
an in-memory MemStore. MemStore flushes to HFiles (immutable, sorted).
Compaction merges HFiles. HDFS provides durability through 3x block replication.

**Consistency**: Strong consistency by design -- each region is served by
exactly one RegionServer. All reads and writes for a given row go through
the same server. No eventual consistency mode.

**Failure Handling**: If a RegionServer fails, HMaster detects via ZooKeeper
session timeout, then reassigns the region to another server. Recovery
replays the WAL from HDFS. Recovery time: typically 30s-2min.

---

### DynamoDB

**Topology**: Fully managed, partition-based. AWS handles all replication,
sharding, and failure recovery. Data is distributed across partitions based
on the partition key hash.

**Storage**: Abstracted -- AWS manages the underlying storage engine. Each
partition is replicated across 3 AZs. Storage nodes use a combination of
B-trees and SSTable-like structures internally.

**Capacity**: Two modes: provisioned (fixed RCU/WCU) and on-demand
(pay-per-request). Auto-scaling adjusts provisioned capacity based on
traffic patterns. Burst capacity absorbs short spikes.

**Consistency**: Default is eventually consistent reads (faster, cheaper).
Strongly consistent reads available per-request (doubles RCU cost). DynamoDB
Transactions provide ACID across up to 100 items.

**DAX**: In-memory caching layer (DynamoDB Accelerator). Microsecond read
latency for cached items. Write-through cache.

---

### ScyllaDB

**Topology**: Same ring topology as Cassandra -- CQL-compatible, same
drivers, same operational model.

**Key Difference**: Written in C++ with a shard-per-core architecture.
Each CPU core owns a dedicated shard of data and runs in a shared-nothing
model (Seastar framework). No JVM, no garbage collection pauses.

**Performance**: Eliminates Cassandra's two main latency sources: JVM GC
pauses (can cause 100ms+ p99 spikes) and cross-core contention. ScyllaDB
achieves 2-5x throughput per node with lower tail latency.

**Automatic Memory Management**: Instead of JVM heap tuning, ScyllaDB
manages memory at the application level with explicit allocation pools.
No stop-the-world pauses.

---

### CockroachDB

**Topology**: Symmetric nodes, no master. Data is divided into ranges
(default 512MB). Each range is a Raft consensus group with a leaseholder
that serves reads and proposes writes.

**Storage**: Pebble (LSM-tree engine, Go implementation inspired by
RocksDB). MVCC for multi-version concurrency control. Timestamps are
hybrid-logical clocks (HLC).

**Consistency**: Serializable isolation by default -- the strongest standard
SQL isolation level. Every transaction appears to execute atomically at a
single point in time.

**Geo-partitioning**: Ranges can be pinned to specific regions for data
residency compliance (e.g., EU data stays in EU). Follower reads allow
non-leaseholder replicas to serve historical reads.

**SQL Compatibility**: PostgreSQL wire protocol. Most PostgreSQL ORMs and
tools work with minimal changes.

---

### TiDB / TiKV

**Topology**: Separate compute (TiDB) and storage (TiKV) layers. TiKV is
a distributed key-value store using Raft for replication. TiDB is a
stateless SQL layer that parses MySQL-protocol queries and pushes
computation down to TiKV.

**Storage**: TiKV uses RocksDB (LSM-tree) per node. Data is split into
Regions (default 96MB). Each Region is a Raft group.

**HTAP**: TiFlash is a columnar storage engine that replicates data from
TiKV via Raft learner replicas. This enables real-time OLAP queries on
OLTP data without ETL pipelines.

**Consistency**: Raft-based replication provides strong consistency. MVCC
with snapshot isolation (SI) or repeatable read (RR).

---

### MongoDB

**Topology**: Replica sets (primary + secondaries) for HA. Sharding
distributes data across multiple replica sets using a shard key.

**Storage**: WiredTiger engine (B-tree + LSM hybrid, default is B-tree).
Document-level concurrency control. Journaling for durability.

**Data Model**: BSON documents -- flexible schema, nested objects, arrays.
No JOINs at the storage level (application-level `$lookup` aggregation).

**Consistency**: Configurable write concern (w:1, w:majority, w:all) and
read concern (local, majority, linearizable, snapshot). With w:majority +
read concern majority, provides causal consistency.

**Transactions**: Multi-document ACID transactions since 4.0. Cross-shard
transactions since 4.2. Performance overhead is significant -- design to
minimize transaction scope.
"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## Data Flow & Key Components

### Write Path Comparison

#### Cassandra / ScyllaDB (LSM-tree)

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

**Key insight**: Writes are sequential I/O (append to log + memtable insert).
This makes LSM-tree databases write-optimized. The cost is paid later during
compaction (write amplification) and reads (must check multiple SSTables).

#### HBase (WAL + MemStore on HDFS)

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

**Key difference from Cassandra**: HBase WAL is on HDFS (network I/O for
durability), not local disk. This adds latency but provides stronger durability
guarantees. Single-master-per-region means no conflict resolution needed.

#### CockroachDB / TiDB (Raft consensus)

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

**Key insight**: Every write requires consensus (Raft majority). This is the
price of strong consistency. Write latency is bounded by the slowest member
of the majority, plus network round trips.

#### DynamoDB (Managed)

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

### Read Path Comparison

#### LSM-tree Read (Cassandra, ScyllaDB, HBase)

```
Client Read
  |-> Check Memtable/MemStore (most recent data)
  |-> Check Bloom filters for each SSTable/HFile
  |   (Bloom filter: false positive ~1%, no false negatives)
  |-> Read matching SSTables (may need to check multiple levels)
  |-> Merge results (latest timestamp wins)
  |-> Return to client
```

**Read amplification**: In the worst case, a key might exist in multiple
SSTables across multiple levels. Leveled compaction reduces this by
ensuring each key exists in at most one SSTable per level.

#### B-tree Read (CockroachDB, MongoDB)

```
Client Read
  |-> Traverse B-tree index: root -> internal -> leaf
  |-> Direct page read (no multiple-file search)
  |-> Return to client
```

**Advantage**: Predictable read performance -- O(log N) page reads.
No compaction-related read amplification.

### Consistency Models

| Model | Guarantee | Databases |
|-------|----------|-----------|
| **Eventual** | Replicas converge over time | Cassandra (CL=ONE), DynamoDB (default) |
| **Tunable** | Per-query consistency level | Cassandra (R+W>N), DynamoDB (per-read) |
| **Strong (single-leader)** | All reads see latest write | HBase, MongoDB (w:majority + read:linearizable) |
| **Serializable** | Transactions appear serial | CockroachDB, TiDB |
| **Causal** | Respects happens-before | MongoDB (sessions), Cassandra (LWTs) |

### Anti-Entropy Mechanisms (Cassandra/ScyllaDB)

- **Read repair**: On read at QUORUM, if replicas disagree, the coordinator
  sends the latest version to stale replicas (background repair)
- **Hinted handoff**: If a target replica is down during write, the
  coordinator stores a "hint" and forwards it when the replica recovers
- **Anti-entropy repair**: Full Merkle-tree comparison between replicas
  to detect and fix divergence (scheduled, resource-intensive)
"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## Formulas & Algorithms

### Consistent Hashing

Standard hash function maps keys to a ring of size $2^{128}$ (or $2^{64}$).
Each node owns a contiguous range of tokens on the ring.

**Problem with naive consistent hashing**: Adding/removing a node only affects
its immediate neighbor, but load distribution is uneven with few nodes.

**Virtual nodes (vnodes)**: Each physical node owns $V$ virtual positions on
the ring (Cassandra default: $V = 256$). This provides:
- Even load distribution across nodes
- Incremental rebalancing when nodes join/leave
- Heterogeneous hardware support (more vnodes for bigger machines)

**Token assignment**: For $N$ nodes with $V$ vnodes each:
$$\text{Total tokens} = N \times V$$
$$\text{Expected data per node} = \frac{\text{Total data}}{N}$$

### Replication Factor and Quorum

For replication factor $RF$ (typically 3):

$$\text{Quorum} = \lfloor RF / 2 \rfloor + 1$$

For strong consistency, reads ($R$) and writes ($W$) must satisfy:

$$R + W > RF$$

Common configurations:
| Config | R | W | Consistency | Availability |
|--------|---|---|-------------|--------------|
| **ONE/ONE** | 1 | 1 | Eventual | Highest (tolerates RF-1 failures) |
| **QUORUM/QUORUM** | 2 | 2 | Strong | Moderate (tolerates 1 failure with RF=3) |
| **ONE/ALL** | 1 | 3 | Strong reads | Write availability suffers |
| **ALL/ONE** | 3 | 1 | Strong writes | Read availability suffers |

### Bloom Filter

Space-efficient probabilistic data structure. For $n$ items and desired false
positive rate $p$:

$$m = -\frac{n \ln p}{(\ln 2)^2}$$

where $m$ is the number of bits. Optimal number of hash functions:

$$k = \frac{m}{n} \ln 2$$

**Cassandra usage**: One Bloom filter per SSTable. Before reading an SSTable,
check the Bloom filter. If it says "not present," skip the SSTable entirely.
Reduces read amplification from $O(\text{num SSTables})$ to $O(1)$ expected.

### Merkle Trees for Anti-Entropy

Each replica builds a Merkle tree over its data for a given token range:
- Leaf nodes: hash of individual row data
- Internal nodes: hash of child hashes
- Root: single hash representing the entire dataset

**Comparison**: Two replicas exchange root hashes. If they match, data is
consistent. If not, recurse into subtrees to identify the specific divergent
rows. Complexity: $O(\log N)$ comparisons to find $k$ divergent rows in a
dataset of $N$ rows.

### Raft Consensus (CockroachDB, TiKV)

**Leader election**: Candidates request votes. A candidate wins if it
receives votes from a majority ($\lfloor N/2 \rfloor + 1$ of $N$ nodes).

**Log replication**: Leader appends entries to its log and replicates to
followers. An entry is committed when a majority of nodes have persisted it.

**Latency**: Write latency is at least 2 network round trips:
1. Client -> Leader (propose)
2. Leader -> Followers -> Leader (replicate + ack from majority)
3. Leader -> Client (commit confirmation)

For geo-distributed deployments:
$$\text{Write latency} \geq 2 \times \text{RTT to farthest majority member}$$

### Partition Key Design

**Hot partition problem**: If all traffic goes to a few partition keys, those
partitions become bottlenecks regardless of the number of nodes.

**Compound partition key**: Combine multiple fields to distribute load.
Example: instead of `user_id`, use `(user_id, date_bucket)` to spread a
single user's data across multiple partitions.

**Write sharding formula**: For a hot key with throughput $T$ and target
per-shard throughput $t$:
$$\text{Shard count} = \lceil T / t \rceil$$

Append a shard suffix `0..shard_count-1` to the partition key. Reads must
scatter-gather across all shards.
"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## Production Constraints

### Latency Profiles by Workload

| Database | p50 Read | p99 Read | p50 Write | p99 Write | Notes |
|----------|---------|---------|-----------|-----------|-------|
| **Cassandra** | 1-2ms | 5-15ms | 0.5-1ms | 3-10ms | JVM GC can cause p99.9 spikes to 100ms+ |
| **ScyllaDB** | 0.5-1ms | 2-5ms | 0.3-0.5ms | 1-3ms | No GC pauses; predictable tail latency |
| **DynamoDB** | 2-5ms | 8-15ms | 3-5ms | 10-20ms | Network overhead; DAX reduces reads to <1ms |
| **HBase** | 1-3ms | 10-30ms | 1-2ms | 5-20ms | HDFS hop adds latency; hot regions spike |
| **CockroachDB** | 2-5ms | 10-25ms | 5-10ms | 15-40ms | Raft consensus adds write latency |
| **TiDB** | 2-5ms | 10-25ms | 5-10ms | 15-30ms | Similar to CockroachDB; TiFlash for analytics |
| **MongoDB** | 0.5-2ms | 5-15ms | 1-3ms | 5-20ms | WiredTiger cache hit = fast; cache miss = slow |

### Operational Complexity

| Database | Deployment | Expertise Required | Key Pain Points |
|----------|-----------|-------------------|-----------------|
| **Cassandra** | Self-hosted or managed (Astra) | Medium-High | Compaction tuning, tombstone management, repair scheduling |
| **ScyllaDB** | Self-hosted or ScyllaDB Cloud | Medium | Fewer JVM knobs, but still need compaction strategy |
| **DynamoDB** | Fully managed | Low | Capacity planning, hot partition detection, cost control |
| **HBase** | Self-hosted (Hadoop ecosystem) | High | ZooKeeper management, HDFS operations, region splitting |
| **CockroachDB** | Self-hosted or Cockroach Cloud | Medium | Range rebalancing, leaseholder placement, clock skew |
| **TiDB** | Self-hosted or TiDB Cloud | High | Multi-component deployment (PD, TiKV, TiDB, TiFlash) |
| **MongoDB** | Self-hosted or Atlas | Medium | Shard key selection (immutable!), balancer tuning |

### Cost Models

#### Self-Hosted (Cassandra/HBase/ScyllaDB)
- **Compute**: 3-9 nodes minimum (RF=3, multi-rack)
- **Storage**: Local SSDs for Cassandra/ScyllaDB; HDFS cluster for HBase
- **Ops team**: 0.5-1 FTE for a small cluster, 2-3 FTE for 100+ nodes
- **Cost**: $5K-$50K/month depending on scale (excluding personnel)

#### Managed (DynamoDB)
- **Provisioned**: $0.00065/WCU/hour, $0.00013/RCU/hour
- **On-demand**: $1.25/million WRU, $0.25/million RRU
- **Storage**: $0.25/GB/month
- **Trap**: A naive schema with hot partitions can cost 10-50x what a
  well-designed schema costs for the same workload
- **Break-even**: DynamoDB is cheaper for <1M requests/day; self-hosted
  Cassandra wins at scale (>10M requests/day)

#### Managed SQL (CockroachDB Serverless, TiDB Cloud)
- **CockroachDB Serverless**: Pay per Request Unit (RU), free tier available
- **TiDB Cloud**: Per-node pricing, similar to RDS
- **Cost**: 2-5x higher per-query than Cassandra/DynamoDB for equivalent
  throughput, but saves engineering time on consistency guarantees

### Scaling Limits

| Database | Max Cluster Size | Max Data/Node | Scaling Model |
|----------|-----------------|---------------|---------------|
| **Cassandra** | 1000+ nodes | 1-2TB recommended | Linear horizontal |
| **ScyllaDB** | 1000+ nodes | 2-5TB (better per-node) | Linear horizontal |
| **DynamoDB** | Unlimited (managed) | 10GB/partition | Auto-partitioning |
| **HBase** | 200+ RegionServers | 1-2TB/RS | Horizontal (limited by ZK) |
| **CockroachDB** | 200+ nodes (tested) | No hard limit | Horizontal, range-based |
| **MongoDB** | 1000+ shards | No hard limit | Horizontal, shard-based |
"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## Trade-off Analysis

### CAP Theorem: Practical Application

The CAP theorem states that a distributed system can provide at most two of
three guarantees: Consistency, Availability, Partition tolerance. Since network
partitions are inevitable, the real choice is **AP vs. CP**.

**When to choose AP (Cassandra, ScyllaDB, DynamoDB):**
- User-facing systems where latency matters more than perfect consistency
- Metrics, logging, time-series data (last-write-wins is acceptable)
- Shopping carts, social feeds, recommendation stores
- Multi-datacenter deployments where cross-DC latency makes strong consistency
  impractical
- High write throughput requirements (>100K writes/sec)

**When to choose CP (HBase, CockroachDB, TiDB):**
- Financial transactions, payment processing
- Inventory management (overselling is unacceptable)
- User authentication / authorization state
- Any domain where "stale read -> wrong action -> irreversible consequence"
- Regulatory requirements for data consistency

### Schema Flexibility vs. Query Power

| Dimension | Wide-Column (Cassandra) | Document (MongoDB) | Relational (CockroachDB) |
|-----------|------------------------|-------------------|--------------------------|
| **Schema** | Fixed column families, flexible columns | Flexible (schemaless) | Rigid (DDL required) |
| **Queries** | Primary key only (no ad-hoc) | Rich queries, aggregation | Full SQL, JOINs, subqueries |
| **Indexes** | Limited secondary indexes | Secondary indexes, text search | Standard B-tree indexes |
| **Joins** | Not supported | Client-side `$lookup` | Native JOINs |
| **Evolution** | Add columns freely, no ALTER TABLE | Add fields freely | ALTER TABLE (may lock) |

**Key trade-off**: Cassandra's query limitations are by design -- the data model
must be designed around the query patterns. If you need ad-hoc queries, you need
to maintain multiple denormalized tables (one per query pattern). This is the
price of write performance and horizontal scalability.

### Operational Burden vs. Feature Richness

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

**DynamoDB** has the lowest operational burden (fully managed) but the least
flexibility (vendor lock-in, partition key constraints, cost at scale).

**HBase/TiDB** have the highest operational burden (multi-component deployments,
Hadoop/PD dependencies) but offer powerful features (strong consistency,
secondary indexes, HTAP).

### Write-Optimized vs. Read-Optimized

| Storage Engine | Write Performance | Read Performance | Space Amplification |
|---------------|-------------------|------------------|---------------------|
| **LSM-tree** (Cassandra, ScyllaDB, HBase) | Excellent (sequential I/O) | Good (Bloom filters help) | Moderate (compaction manages) |
| **B-tree** (MongoDB, CockroachDB internal) | Good (random I/O) | Excellent (direct lookup) | Low (in-place updates) |

**Write amplification** (LSM): Data is written multiple times as SSTables are
compacted through levels. Leveled compaction: write amp ~10-30x. Size-tiered:
write amp ~4-8x.

**Read amplification** (LSM): A point query may need to check multiple SSTables.
Leveled compaction limits this to 1 SSTable per level. Bloom filters reduce
unnecessary reads.

**Trade-off**: If your workload is >80% writes (logging, metrics, IoT), LSM-tree
databases win. If your workload is >80% reads with random access patterns, B-tree
databases provide more predictable performance.

### Vendor Lock-In

| Database | Lock-in Risk | Migration Path |
|----------|-------------|----------------|
| **DynamoDB** | **High** -- proprietary API, no self-hosted option | Migrate to Cassandra/ScyllaDB (different data model) |
| **Cassandra** | **Low** -- open source, CQL is portable | ScyllaDB (drop-in), DataStax Astra (managed) |
| **ScyllaDB** | **Low** -- Cassandra-compatible | Cassandra (reverse migration), ScyllaDB Cloud |
| **HBase** | **Medium** -- tied to Hadoop/HDFS ecosystem | Cassandra (different model), cloud BigTable (API-compatible) |
| **CockroachDB** | **Low** -- PostgreSQL-compatible | PostgreSQL (single-node), other NewSQL |
| **TiDB** | **Low** -- MySQL-compatible | MySQL (single-node), other NewSQL |
| **MongoDB** | **Medium** -- proprietary BSON, Atlas features | DocumentDB (partial), self-hosted Mongo |
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## Adversarial Defense Q&A

---

**Q: Why not just use PostgreSQL with read replicas?**

> PostgreSQL with read replicas works well up to a point. The limitations are:
>
> 1. **Write scaling**: Single-writer architecture. All writes go through one
>    primary. If you need >50K writes/sec, you hit the ceiling. Sharding
>    PostgreSQL is possible (Citus) but adds significant complexity.
>
> 2. **Replication lag**: Streaming replication is asynchronous by default.
>    Read replicas can be seconds behind. Synchronous replication exists but
>    adds write latency proportional to the slowest replica.
>
> 3. **Geographic distribution**: PostgreSQL replicas in multiple regions mean
>    cross-region write latency (50-200ms) for every write. Cassandra handles
>    this with LOCAL_QUORUM -- writes are fast locally, replicate asynchronously
>    to remote DCs.
>
> 4. **Operational scaling**: Adding read replicas is easy. Adding write capacity
>    requires application-level sharding, connection routing, and cross-shard
>    query handling. Cassandra/CockroachDB handle this transparently.
>
> **When PostgreSQL IS the right answer**: If your data fits on one beefy machine
> (up to ~10TB), you need complex queries with JOINs, your write throughput is
> moderate (<10K/sec), and you have a team experienced with PostgreSQL -- use
> PostgreSQL. Adding unnecessary distributed complexity is the bigger mistake.

---

**Q: Cassandra has no transactions -- how do you handle X?**

> First, Cassandra does have Lightweight Transactions (LWTs) using Paxos for
> compare-and-swap operations. They are 4-10x slower than normal writes but
> provide linearizable consistency for single-partition operations.
>
> For broader transaction needs, the patterns are:
>
> 1. **Idempotent writes**: Design operations to be safe to retry. Use
>    `INSERT IF NOT EXISTS` for deduplication. Use `UPDATE ... IF column = expected`
>    for optimistic concurrency.
>
> 2. **Saga pattern**: For multi-step operations, implement compensating
>    transactions. Each step has an undo action. If step 3 fails, undo steps
>    2 and 1.
>
> 3. **Outbox pattern**: Write the event and the state change to the same
>    partition (single-partition write = atomic in Cassandra). A separate process
>    reads the outbox and publishes events.
>
> 4. **Accept eventual consistency**: For many use cases (counters, last-write-wins
>    state), eventual consistency is actually fine. The business can tolerate a
>    shopping cart that shows a slightly stale state for 100ms.
>
> **Honest limitation**: If you need multi-row, multi-table ACID transactions,
> Cassandra is the wrong database. Use CockroachDB, TiDB, or PostgreSQL.

---

**Q: When would you NOT use Cassandra?**

> Cassandra is a poor fit when:
>
> 1. **Ad-hoc queries**: Cassandra requires you to design tables around query
>    patterns. If your queries are unpredictable (BI, analytics, exploration),
>    use a database with flexible querying (PostgreSQL, TiDB, or a data warehouse).
>
> 2. **Small data / low traffic**: Below ~1TB or ~10K QPS, Cassandra's operational
>    overhead is not justified. A single PostgreSQL or MongoDB instance is simpler,
>    cheaper, and provides richer query capabilities.
>
> 3. **Strong consistency required for ALL operations**: While Cassandra can do
>    QUORUM reads/writes, it was designed for AP workloads. If every operation
>    needs serializable consistency, CockroachDB or TiDB is a better fit.
>
> 4. **Heavy read-modify-write**: Cassandra is write-optimized. Patterns like
>    "read a row, modify it, write it back" require LWTs or external locking,
>    which negate Cassandra's performance advantages.
>
> 5. **Small number of large blobs**: Cassandra has a 2GB theoretical cell limit
>    but performs poorly with values >1MB. Use object storage (S3) for large
>    blobs and store references in Cassandra.

---

**Q: How do you handle secondary indexes at scale?**

> Cassandra's native secondary indexes (2i) are **local indexes** -- each node
> indexes only its own data. A query on a secondary index must scatter to ALL
> nodes (fan-out), making it O(N) where N is cluster size. This is acceptable
> for low-cardinality columns on small clusters but does not scale.
>
> **Better approaches**:
>
> 1. **Materialized views / denormalized tables**: Create a separate table with
>    the query column as the partition key. Trade write amplification (maintain
>    multiple tables) for read performance. This is the Cassandra-native pattern.
>
> 2. **SAI (Storage-Attached Indexes)**: Newer Cassandra feature (5.0+). More
>    efficient than 2i -- uses a per-SSTable index structure. Still local, but
>    with better performance characteristics.
>
> 3. **External search index**: Write to Cassandra for primary storage, replicate
>    to Elasticsearch/Solr for search queries. Use CDC (Change Data Capture) or
>    dual-write with idempotency.
>
> 4. **ScyllaDB approach**: ScyllaDB's secondary indexes also scatter, but the
>    shard-per-core architecture handles the fan-out more efficiently. Still not
>    recommended for high-QPS secondary index queries.

---

**Q: DynamoDB is expensive. How do you control costs?**

> DynamoDB cost traps and mitigations:
>
> 1. **Hot partitions**: A single hot partition key can consume all provisioned
>    capacity. Monitor `ConsumedCapacity` per partition. Solution: write sharding
>    (append random suffix to hot keys) or switch to on-demand mode.
>
> 2. **Scan operations**: A full table scan consumes RCUs proportional to table
>    size, not result size. Never scan in production code. Use GSIs or redesign
>    the access pattern.
>
> 3. **Over-provisioning**: Provisioned mode requires predicting traffic. Use
>    auto-scaling with target utilization of 70%. For unpredictable workloads,
>    on-demand mode eliminates waste (but costs more per-request at high volume).
>
> 4. **GSI proliferation**: Each Global Secondary Index replicates the entire
>    table's data. Five GSIs = 5x storage cost + 5x write cost. Design GSIs
>    carefully -- each one should serve a high-value access pattern.
>
> 5. **Reserved capacity**: For steady-state workloads, reserved capacity (1-year
>    or 3-year) reduces cost by 50-75%.
>
> **Break-even analysis**: At ~500M requests/month with predictable traffic,
> self-hosted Cassandra on reserved EC2 instances typically costs 60-80% less
> than DynamoDB provisioned mode.

---

**Q: CockroachDB claims to be "NewSQL" -- is it actually faster than PostgreSQL?**

> No. For single-node performance, CockroachDB is **slower** than PostgreSQL.
> Every write requires Raft consensus (even with RF=1 in development, the code
> path includes consensus overhead). Simple queries run 2-5x slower than
> PostgreSQL on equivalent hardware.
>
> CockroachDB's value is **horizontal scalability with strong consistency**.
> When your dataset exceeds what one PostgreSQL node can handle, CockroachDB
> scales out without application-level sharding. The per-query cost is higher,
> but total system throughput scales linearly with nodes.
>
> **When CockroachDB wins over PostgreSQL**:
> - Dataset >5TB (beyond single-node PostgreSQL)
> - Write throughput >20K/sec (beyond single-writer)
> - Multi-region deployment requiring local reads with global consistency
> - Need to scale without re-architecting the application
>
> **When PostgreSQL wins**:
> - Data fits on one machine
> - You need the PostgreSQL extension ecosystem (PostGIS, pg_vector, etc.)
> - Maximum single-query performance matters
> - Team expertise is in PostgreSQL
"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## Verbal Outline

### 3-Minute Version

**Target**: Elevator pitch when asked "how would you choose a database for this
system?"

1. **(30s) Framework**: Database selection is a constraint satisfaction problem.
   The key dimensions are: data model, consistency requirements, scale targets,
   latency budget, and operational capacity. CAP theorem forces a choice between
   AP (availability) and CP (consistency) under partition.

2. **(45s) AP Systems**: For high-throughput, latency-sensitive workloads --
   user-facing services, metrics, time-series -- choose Cassandra or ScyllaDB.
   Ring topology, LSM-tree storage, tunable consistency. ScyllaDB eliminates
   JVM GC pauses with C++ shard-per-core. DynamoDB if you want zero ops but
   accept vendor lock-in and higher cost at scale.

3. **(45s) CP Systems**: For transactional workloads -- payments, inventory,
   auth -- choose CockroachDB or TiDB. Raft consensus, serializable isolation,
   SQL compatibility. Trade-off: higher write latency (consensus round trips)
   and lower throughput per node. HBase for Hadoop-native strong consistency.

4. **(30s) Key Trade-offs**: Write-optimized (LSM) vs. read-optimized (B-tree).
   Schema flexibility vs. query power. Operational burden vs. managed simplicity.
   The right answer depends on the specific requirements -- there is no
   universally best database.

5. **(30s) Selection Rule**: Start with the simplest option that meets
   requirements (often PostgreSQL). Only move to distributed databases when
   single-node limits are hit: >10TB data, >20K writes/sec, or multi-region
   requirements.

### 10-Minute Version

**Target**: Deep-dive system design round where database choice is a key
component.

1. **(1.5 min) Problem Statement & Selection Framework**
   - Why database choice matters: it constrains consistency, failure modes,
     scaling strategy, and cost
   - The six-dimension framework: data model, consistency, scale, latency,
     operational, cost
   - CAP theorem as practical AP vs. CP decision, not theoretical constraint

2. **(2 min) Architecture Comparison**
   - Cassandra: ring + consistent hashing + gossip + LSM-tree
   - CockroachDB: symmetric nodes + Raft per range + Pebble LSM
   - DynamoDB: managed partitions + auto-scaling
   - Key architectural difference: peer-to-peer vs. consensus-based vs. managed
   - How each architecture handles node failure and recovery

3. **(2 min) Write & Read Path Deep Dive**
   - LSM-tree write path: WAL -> Memtable -> SSTable -> compaction
   - Raft write path: propose -> replicate to majority -> commit
   - Read amplification in LSM vs. direct lookup in B-tree
   - Bloom filters, compaction strategies (size-tiered, leveled, TWCS)

4. **(1.5 min) Consistency Models**
   - Eventual, tunable (R+W>N), strong (single-leader), serializable (consensus)
   - Anti-entropy: read repair, hinted handoff, Merkle tree repair
   - Quorum math with concrete examples

5. **(1.5 min) Production Constraints**
   - Latency profiles: p50/p99 by database and workload type
   - Operational complexity spectrum: DynamoDB (zero ops) to HBase (full-time DBA)
   - Cost analysis: managed vs. self-hosted break-even points

6. **(1.5 min) Trade-off Analysis & Selection Criteria**
   - AP for user-facing, latency-sensitive, high-write workloads
   - CP for transactional, consistency-critical workloads
   - Schema flexibility vs. query power trade-off
   - "Start with PostgreSQL" rule and when to graduate to distributed

### Transition Phrases for Interview Flow

When connecting to other system design topics:

- **From a specific design**: "For the message queue metadata, I would use
  Cassandra because we need high write throughput and can tolerate eventual
  consistency for message acknowledgments."
- **To justify a choice**: "The reason I chose CockroachDB over Cassandra here
  is that inventory management requires serializable transactions -- overselling
  a product is worse than slightly higher write latency."
- **When challenged on choice**: "You're right that PostgreSQL could handle this
  at our current scale. The reason I'm designing with Cassandra is the 10x growth
  projection -- at 500K writes/sec, we would need to shard PostgreSQL manually,
  which adds the same operational complexity as running Cassandra but without the
  built-in multi-DC replication."
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
        for section in sections:
            content = getattr(record, section)
            length = len(content) if content else 0
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {section}: {length} chars {status}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_database_comparison()
