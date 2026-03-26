# System Design: Replication, Partitioning & Consistency (DDIA Ch10-15)

## Overview

DDIA Part II covers how data is distributed across multiple machines: replication for redundancy and availability, partitioning for scalability, and transactions for correctness. For MLE interviews, these chapters provide the core vocabulary for discussing distributed data systems -- understanding when to sacrifice consistency for availability, how quorum systems work, why partition strategies matter, and what isolation levels actually guarantee. This is the foundation for any system design answer involving databases at scale.

## Core Concepts

### Scaling Strategies

**Shared-Nothing Architecture** (horizontal scaling) is the dominant approach for modern distributed systems:
- Each node uses its own CPUs, RAM, and disks independently
- Coordination happens at the software level over conventional network
- Enables multi-region deployment for latency reduction and fault tolerance
- Trade-off: increased complexity, constrained data model expressiveness

Two complementary strategies for distributing data:
- **Replication**: keeping copies of the same data on multiple nodes (redundancy, availability)
- **Partitioning** (sharding): splitting data into non-overlapping subsets across nodes (scalability)

These are orthogonal and often combined: each partition is replicated across multiple nodes.

### Leader-Based Replication

The most common replication model. One replica is the **leader** (primary); others are **followers** (secondaries).

**Write path**: client -> leader (local write) -> replication log/change stream -> followers (apply in order)
**Read path**: client -> leader OR any follower

**Usage**: PostgreSQL (9.0+), MySQL, Oracle Data Guard, MongoDB, Kafka, RabbitMQ HA queues

**Synchronous vs Asynchronous replication**:

| Aspect | Synchronous | Asynchronous | Semi-Synchronous |
|--------|------------|--------------|-----------------|
| Durability | Strong (follower confirmed) | Weak (leader-only until replicated) | 1 follower guaranteed |
| Availability | Blocked if follower down | Leader continues regardless | Balanced |
| Latency | Higher (wait for follower ACK) | Lower (fire-and-forget) | Moderate |
| Common use | Rare as fully synchronous | Default for most systems | Recommended production setting |

**Semi-synchronous**: one follower is synchronous (guaranteeing 2 up-to-date copies), rest are asynchronous. If the synchronous follower fails, an asynchronous one is promoted.

### Replication Log Implementations

| Method | Mechanism | Pros | Cons |
|--------|-----------|------|------|
| Statement-based | Forward SQL statements (INSERT, UPDATE, DELETE) | Compact | Non-deterministic functions (RAND), ordering issues, side effects |
| WAL shipping | Send append-only write-ahead log bytes | Simple, proven (PostgreSQL, Oracle) | Coupled to storage engine; blocks zero-downtime upgrades |
| Logical (row-based) | Sequence of row-level change records | Decoupled from engine; backward compatible; enables CDC | Slightly more complex |
| Trigger-based | Application-level triggers write to separate table | Maximum flexibility (subset replication, cross-DB) | Higher overhead, more bugs |

**Key insight**: Logical replication (MySQL binlog in row mode) decouples the replication format from the storage engine, enabling:
- Zero-downtime version upgrades (upgrade followers first, then failover)
- **Change Data Capture (CDC)**: feeding data warehouses, building custom indexes/caches from the replication stream

### Setting Up Followers and Failover

**Adding a follower without downtime**:
1. Take a consistent snapshot of leader (without full lock)
2. Copy snapshot to new follower node
3. Follower connects to leader, requests changes since snapshot position (PostgreSQL: log sequence number; MySQL: binlog coordinates)
4. Follower processes backlog until caught up

**Automatic failover process**:
1. **Detect failure**: timeout-based (e.g., 30s no response -> assumed dead)
2. **Elect new leader**: consensus among replicas, or appointed by controller node; best candidate = most up-to-date replica
3. **Reconfigure system**: redirect client writes to new leader; demote old leader if it returns

**Failover risks**:
- **Data loss**: asynchronous followers may lack latest writes from old leader
- **Split brain**: two nodes both believe they are leader -> both accept writes -> data corruption. Safety mechanism: shut down one node (but risky if both get shut down)
- **ID reuse**: GitHub incident -- promoted follower reused auto-increment primary keys -> inconsistency between MySQL and Redis -> private data leak
- **False failovers**: too-short timeouts cause unnecessary failovers during load spikes

Many teams prefer **manual failover** due to these risks.

### Chain Replication (CRAQ)

A variant of synchronous replication used in **Microsoft Azure Storage**:

**Basic chain**: HEAD -> Node1 -> ... -> TAIL
- Writes go to HEAD, propagate down the chain; TAIL sends ACK back
- Reads from TAIL (guarantees reading committed data on all nodes)
- Tolerates up to $n-1$ node failures
- Limitation: TAIL is a read bottleneck

**CRAQ (Chain Replication with Apportioned Queries)**: improves read throughput by allowing reads from any node:
- Each node maintains multiple versions per key, marked **clean** or **dirty**
- When TAIL commits a version, ACK propagates back; nodes mark version clean and discard older versions
- Read from any node: if latest version is clean, return it; if dirty, ask TAIL for last committed version
- Read performance scales **linearly** with node count for read-heavy workloads
- Provides **strong consistency** (can be relaxed to eventual/bounded-eventual)

### Replication Lag Problems

With asynchronous replication, followers may serve stale data. Three consistency guarantees address this:

**Read-After-Write (Read-Your-Writes) Consistency**:
- Guarantee: users always see their own submitted changes immediately
- Implementation: read from leader for recently-modified data (track by timestamp or logical sequence number); route to leader within 1 minute of user's last write

**Monotonic Reads**:
- Guarantee: subsequent reads never see data go backward in time
- Problem: reading from different replicas with different lag shows comments appearing then disappearing
- Implementation: always route same user to same replica (hash user ID)

**Consistent Prefix Reads**:
- Guarantee: causally related writes appear in correct order
- Problem: in partitioned databases, no global ordering -> answer may appear before question
- Implementation: write causally related data to the same partition

### Multi-Leader Replication

Allows multiple nodes to accept writes, each acting as leader to others.

**Use cases**:
- Multi-datacenter deployment: each DC has a leader; inter-DC replication between leaders; intra-DC uses regular leader-follower
- Offline-capable apps (e.g., calendar): each device is a local leader, synced when online (CouchDB)
- Collaborative editing (Google Docs, Etherpad): concurrent edits with conflict resolution

**Advantages**: better perceived latency (writes go to local DC), datacenter independence, better network fault tolerance

**Conflict resolution strategies**:

| Strategy | Mechanism | Data Loss Risk |
|----------|-----------|---------------|
| Last Write Wins (LWW) | Highest timestamp wins | Yes -- concurrent writes discarded |
| Replica priority | Higher-numbered replica wins | Yes |
| Value merging | Concatenate/merge conflict values | No, but may produce unexpected results |
| Application-level | Record conflict, resolve later (prompt user) | No |
| CRDTs | Conflict-free replicated data types (auto-merge) | No |
| Operational transformation | Algorithm for ordered list editing (Google Docs) | No |

**Conflict avoidance** (route all writes for a record to same leader) is the recommended first approach.

**Replication topologies** (for 3+ leaders):
- **Circular**: each leader forwards to next; single point of failure risk
- **Star**: central leader relays; single point of failure risk
- **All-to-all**: every leader connects to every other; most general, but ordering issues possible

### Leaderless Replication (Dynamo-Style)

Any replica directly accepts writes. Used by **Riak**, **Cassandra**, **Voldemort** (inspired by Amazon Dynamo).

**Quorum protocol**: with $n$ replicas, write to $w$ nodes, read from $r$ nodes.

$$w + r > n \implies \text{at least one read node has the latest write}$$

- Typically $r$ and $w$ are majority ($> n/2$), but only the overlap matters
- Even with quorum, edge cases allow stale reads (sloppy quorum, concurrent writes, partial write success)

**Consistency mechanisms**:
- **Read repair**: client detects stale value during parallel reads, writes back to stale replica (good for frequently-read data)
- **Anti-entropy**: background process compares replicas, copies missing data (no ordering guarantee, high latency)

**Sloppy quorum and hinted handoff**:
- When network issues prevent reaching home nodes, writes go to non-home nodes (sloppy quorum)
- **Hinted handoff**: once network recovers, temporarily-accepted writes are forwarded to home nodes
- Trade-off: guarantees durability ($w$ nodes stored the data) but not read visibility until handoff completes

### Concurrent Write Handling

**Last Write Wins (LWW)**: simple but causes data loss for concurrent writes. Safe only if keys are written once (e.g., UUID keys in Cassandra).

**Version vectors** for tracking causality:
1. Server maintains a version number per key, incremented on each write
2. Client reads all versions, must merge before writing back
3. Server overwrites versions $\le$ included version number, keeps higher (concurrent) versions
4. Deletion requires a **tombstone** marker to prevent reappearance after merge

**Dotted Version Vector (DVV)**: tracks version per replica per key:

$$((i_1, n), [(i_1, m), (i_2, l), (i_3, k), \ldots])$$

The dot $(i_1, n)$ is the event version; the vector $[(i_1, m), \ldots]$ captures state before that event. Enables causal ordering; otherwise, events are **concurrent**.

### Partitioning (Sharding)

Splits data into non-overlapping subsets across nodes for horizontal scalability.

**Partition by key range**:
- Assign continuous key ranges to partitions (like encyclopedia volumes)
- Enables efficient range queries and sorted scans
- Risk: access patterns can create **hot spots** (e.g., timestamp-keyed data)
- Used by: HBase, old Bigtable

**Partition by hash of key**:
- Hash function distributes keys uniformly across partitions
- Eliminates hot spots from skewed key distribution
- Cannot do efficient range queries (must scatter/gather across all partitions)
- **Compound primary key**: hash first column for partition assignment, use remaining columns as sorted concatenated index within partition (e.g., `(user_id, timestamp)` -> all posts by one user in one partition, sorted by time)

**Relieving hot spots**: even hash partitioning cannot prevent hot spots when many writes target the same key (e.g., celebrity user). Application-level solution: append random salt to hot keys (trade-off: reads must query all salted variants).

### Secondary Indexes on Partitioned Data

| Approach | Aka | Write Cost | Read Cost | Consistency |
|----------|-----|-----------|-----------|-------------|
| Document-partitioned | Local index | Low (update local index only) | High (scatter/gather all partitions) | Immediate |
| Term-partitioned | Global index | High (distributed transaction across partitions) | Low (single partition lookup) | Often asynchronous |

### Partition Rebalancing

When nodes are added/removed, data must be redistributed.

| Strategy | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| Fixed partition count | Create many more partitions than nodes; move whole partitions | Simple, low data movement | Must choose count upfront |
| Dynamic partitioning | Split when partition exceeds size threshold; merge when small | Adapts to data volume | Starts with 1 partition (use pre-splitting) |
| Proportional to nodes | Fixed partitions per node; new node splits random existing partitions | Balanced automatically | Can produce unfair splits |

**Never use** `hash mod N` -- changing $N$ moves almost all data.

**Request routing** (service discovery): (1) any-node forwarding, (2) routing tier / partition-aware load balancer, (3) client-side partition awareness. **ZooKeeper** often serves as the coordination service.

### Transactions and ACID

Transactions group reads and writes into a logical unit that commits or aborts atomically.

| Property | Guarantee |
|----------|-----------|
| **Atomicity** | All-or-nothing: if any part fails, entire transaction is rolled back |
| **Consistency** | Application-defined invariants are preserved (application's responsibility) |
| **Isolation** | Concurrent transactions don't interfere with each other |
| **Durability** | Committed data survives crashes (written to non-volatile storage or replicated) |

**BASE** (Basically Available, Soft state, Eventual consistency) is the alternative philosophy for systems prioritizing availability over strong consistency.

**Transaction retry pitfalls**:
- Network failure after commit -> retry causes duplicate (need deduplication)
- Overload-caused errors -> retry worsens load (use exponential backoff)
- Only retry transient errors (deadlock, failover), not permanent ones (constraint violation)
- Side effects outside DB (emails) may fire even if transaction aborts

### Isolation Levels

| Level | Prevents | Does NOT Prevent | Implementation |
|-------|----------|-----------------|----------------|
| Read Uncommitted | Nothing | Dirty reads, dirty writes, everything else | Rarely used |
| Read Committed | Dirty reads, dirty writes | Non-repeatable reads, lost updates, write skew | Row-level locks (write); return old committed value (read) |
| Snapshot Isolation (Repeatable Read) | Dirty reads/writes, non-repeatable reads | Write skew, phantoms in read-write txns | MVCC |
| Serializable | All anomalies | Nothing | Serial execution, 2PL, or SSI |

### Multi-Version Concurrency Control (MVCC)

The implementation behind snapshot isolation:
- Each transaction gets a unique, always-increasing **txid**
- Each row has `created_by` and `deleted_by` txid fields (deletion is a soft-delete marker)
- Garbage collection removes rows no longer visible to any active transaction

**Visibility rules** for a transaction with txid $T$:
1. Ignore writes from transactions still in progress at $T$'s start
2. Ignore writes from aborted transactions
3. Ignore writes from transactions with txid $> T$ (even if committed)
4. All other writes are visible

No lock contention between readers and writers -- readers never block writers and vice versa.

**Index strategies for MVCC**:
- Point index entries to all versions; filter by visibility at query time
- Append-only / copy-on-write B-trees: each write creates a new tree root (consistent snapshot per root)

### Preventing Lost Updates

When concurrent read-modify-write cycles collide:

| Technique | Mechanism | Replicated DB? |
|-----------|-----------|---------------|
| Atomic write operations | Exclusive lock on object during read (cursor stability) | Yes (if commutative) |
| Explicit application lock | `SELECT ... FOR UPDATE` | No |
| Automatic detection | Transaction manager detects and retries | No |
| Compare-and-set | Write only if value unchanged since read | No |
| Conflict resolution | Allow concurrent writes, merge siblings later | Yes (required approach) |

### Write Skew and Phantoms

**Write skew**: two transactions read the same data, then each writes to different rows, together violating a constraint. Example: two doctors both check that 2 doctors are on-call, each decides to go off-call -> 0 doctors on-call.

Not prevented by snapshot isolation. Solutions:
- `SELECT ... FOR UPDATE` to lock dependent rows
- **Materializing conflicts**: create explicit lock objects in the database
- **Serializable isolation** (preferred)

**Phantom**: a write in one transaction changes the result of a search query in another transaction. Cannot lock rows that don't exist yet (e.g., booking a meeting room that has no existing bookings).

### Serializability Approaches

**1. Actual Serial Execution**:
- Run all transactions on a single thread (feasible now: RAM is cheap, OLTP transactions are short)
- Requires: stored procedures (submit entire transaction as code, no interactive multi-statement), in-memory dataset
- Throughput limited to single CPU; cross-partition transactions are expensive
- Used by: VoltDB, Redis

**2. Two-Phase Locking (2PL)** (pessimistic):
- Readers acquire shared locks; writers acquire exclusive locks (blocks both readers and writers)
- **Phase 1**: acquire locks during execution; **Phase 2**: release all locks at commit/abort
- **Predicate locks**: lock all objects matching a search condition (even non-existent ones), preventing phantoms
- **Index-range locks** (next-key locking): simplified predicate locking using indexes; locks broader range but easier to implement
- Risk: deadlocks (detected and resolved by aborting one transaction), performance degradation under contention
- Used by: MySQL InnoDB (serializable), SQL Server, DB2 (repeatable read)

**3. Serializable Snapshot Isolation (SSI)** (optimistic):
- Based on snapshot isolation + conflict detection algorithm
- Allow transactions to execute without blocking; detect serialization conflicts at commit time; abort and retry if conflict found
- Detects: (a) reads of stale MVCC versions (uncommitted write before the read), (b) writes that affect data read by another transaction
- Better performance than 2PL when contention is low; degrades under high contention
- Used by: PostgreSQL (since 9.1), FoundationDB

## Implementation

### Replication Strategy Decision Framework

```python
def choose_replication_strategy(
    num_datacenters: int,
    write_availability: str,  # "high", "medium", "low"
    consistency_requirement: str,  # "strong", "eventual", "read-your-writes"
    conflict_tolerance: bool,
) -> str:
    """Guide for choosing replication strategy in system design interviews."""
    # Single datacenter, simple consistency
    if num_datacenters == 1 and consistency_requirement == "strong":
        return "Single-leader (semi-synchronous)"

    # Multi-DC with strong consistency needs
    if num_datacenters > 1 and not conflict_tolerance:
        return "Single-leader with cross-DC followers (higher write latency)"

    # Multi-DC, can tolerate conflicts
    if num_datacenters > 1 and conflict_tolerance:
        return "Multi-leader (one leader per DC, async cross-DC replication)"

    # Maximum write availability, eventual consistency OK
    if write_availability == "high" and consistency_requirement == "eventual":
        return "Leaderless (Dynamo-style, quorum W+R>N)"

    return "Single-leader (safe default)"
```

### Quorum Parameter Selection

```python
def quorum_analysis(n: int, w: int, r: int) -> str:
    """Analyze quorum configuration trade-offs."""
    overlap = w + r - n
    result = f"n={n}, w={w}, r={r}\n"
    result += f"Read-write overlap: {overlap} node(s)\n"

    if w + r > n:
        result += "Strong quorum: guaranteed to read latest write\n"
    else:
        result += "Weak quorum: may read stale data (higher availability)\n"

    if w > n // 2:
        result += "Write quorum: no conflicting writes can both succeed\n"
    if r > n // 2:
        result += "Read quorum: always reads from majority\n"

    # Common configurations
    # n=3, w=2, r=2: balanced (tolerates 1 failure for both reads and writes)
    # n=3, w=3, r=1: fast reads, slow writes (all nodes must confirm write)
    # n=3, w=1, r=3: fast writes, slow reads (write to any 1, read all 3)
    return result
```

### Isolation Level Selection

```python
def choose_isolation_level(
    has_write_skew_risk: bool,
    read_heavy: bool,
    cross_row_constraints: bool,
    latency_sensitive: bool,
) -> str:
    """Guide for choosing transaction isolation level."""
    # Need full serializability
    if has_write_skew_risk or cross_row_constraints:
        if latency_sensitive:
            return "SSI (optimistic, good for low contention)"
        return "2PL or actual serial execution"

    # Read-heavy, need consistent snapshots
    if read_heavy:
        return "Snapshot isolation / MVCC (no read-write blocking)"

    # Basic protection sufficient
    return "Read committed (default in PostgreSQL, Oracle)"
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Replication topology trade-off | "How would you replicate across data centers?" | Single-leader = simple + consistent; multi-leader = better latency + availability but conflicts; leaderless = highest availability |
| Quorum math | "How does a distributed DB ensure consistency?" | $w + r > n$ guarantees overlap; but sloppy quorum, concurrent writes, and partial failures can still cause staleness |
| Consistency spectrum | "What consistency guarantees does your system need?" | Eventual -> read-your-writes -> monotonic reads -> consistent prefix -> linearizable; each has cost |
| Partition strategy | "How would you shard this database?" | Hash for even distribution (no range queries); range for sorted access (hot spot risk); compound keys for best of both |
| MVCC explanation | "How does snapshot isolation work?" | Each txn sees a frozen snapshot via versioned rows; readers never block writers; GC cleans old versions |
| Write skew detection | "What can go wrong with snapshot isolation?" | Two txns read same rows, write different rows, violate a constraint together; need serializable isolation |
| Conflict resolution | "How do you handle conflicts in multi-leader?" | Avoidance first; then LWW (lossy), CRDTs (automatic), or application-level merge |
| Failover risks | "What can go wrong during leader failover?" | Split brain, data loss from async replication, ID reuse (GitHub incident), cascading failures from false detection |

### Common Interview Questions

- [ ] "Compare single-leader, multi-leader, and leaderless replication: when would you use each?"
- [ ] "Explain the quorum condition W+R>N. What happens when it's not satisfied?"
- [ ] "What is read-after-write consistency and how would you implement it?"
- [ ] "What is split brain and how do you prevent it?"
- [ ] "Hash partitioning vs range partitioning: trade-offs?"
- [ ] "Explain MVCC and snapshot isolation."
- [ ] "What is write skew? Give an example and explain how to prevent it."
- [ ] "Compare 2PL, serial execution, and SSI for achieving serializability."
- [ ] "What are CRDTs and when would you use them?"
- [ ] "How does chain replication (CRAQ) achieve strong consistency with high read throughput?"
- [ ] "Explain sloppy quorum and hinted handoff."
- [ ] "What are the ACID properties? How does BASE differ?"

## Comparisons

### Replication Strategy Comparison

| Aspect | Single-Leader | Multi-Leader | Leaderless (Dynamo) |
|--------|--------------|-------------|-------------------|
| Write target | One leader only | Multiple leaders (one per DC) | Any replica |
| Consistency | Strong (with sync replication) | Eventual (conflicts possible) | Eventual (quorum-dependent) |
| Write availability | Leader is SPOF | High (each DC independent) | Highest (no single point of failure) |
| Conflict handling | None needed | Required (LWW, CRDTs, app-level) | Required (version vectors, LWW) |
| Failover | Complex (split brain risk) | Per-DC failover | No failover needed |
| Read scaling | Add followers | Followers per DC | Any node serves reads |
| Use case | Most applications | Multi-DC, offline apps | Shopping carts, session stores |
| Examples | PostgreSQL, MySQL | Tungsten, BDR, GoldenGate | Riak, Cassandra, Voldemort |

### Partition Strategy Comparison

| Aspect | Key Range | Hash of Key | Compound Key |
|--------|-----------|-------------|-------------|
| Distribution | May be skewed | Uniform | Uniform across partitions |
| Range queries | Efficient (sorted) | Not possible (scatter/gather) | Within-partition only |
| Hot spots | Risk from access patterns | Risk from popular keys only | Reduced (per-entity partitioning) |
| Rebalancing | Split at range boundaries | Split at hash boundaries | Same as hash |
| Examples | HBase, old Bigtable | Cassandra, DynamoDB | Cassandra (user_id, timestamp) |

### Isolation Level Comparison

| Aspect | Read Committed | Snapshot Isolation | 2PL (Serializable) | SSI (Serializable) |
|--------|---------------|-------------------|--------------------|--------------------|
| Dirty reads | Prevented | Prevented | Prevented | Prevented |
| Non-repeatable reads | Possible | Prevented | Prevented | Prevented |
| Lost updates | Possible | Prevented (with detection) | Prevented | Prevented |
| Write skew | Possible | Possible | Prevented | Prevented |
| Phantoms (read-write) | Possible | Possible | Prevented (predicate locks) | Prevented |
| Reader blocks writer | No | No | Yes | No |
| Performance | Best | Good | Poor under contention | Good (low contention) |
| Default in | PostgreSQL, Oracle | PostgreSQL (repeatable read) | MySQL InnoDB (optional) | PostgreSQL 9.1+ (optional) |

### Serializability Implementation Comparison

| Aspect | Actual Serial Execution | Two-Phase Locking (2PL) | SSI |
|--------|------------------------|------------------------|-----|
| Approach | Pessimistic (extreme) | Pessimistic | Optimistic |
| Concurrency | None (single thread) | Limited (lock-based) | High (detect at commit) |
| Throughput | Low (single CPU) | Medium (contention-limited) | High (low contention) |
| Latency | Low per txn | Variable (lock waits) | Low (abort cost on conflict) |
| Deadlocks | Impossible | Possible (detect + abort) | Impossible |
| Cross-partition | Expensive (lock-step) | Supported (distributed locks) | Supported |
| Data must fit in | Memory | Disk OK | Disk OK |
| Examples | VoltDB, Redis | MySQL InnoDB, SQL Server | PostgreSQL, FoundationDB |

## Key Takeaways

- [ ] Replication comes in three models: single-leader (simple, consistent), multi-leader (multi-DC, conflicts), leaderless (highly available, quorum-based) -- choose based on consistency vs availability needs
- [ ] Semi-synchronous replication (1 sync follower + N async) is the practical default: balances durability (2 copies guaranteed) with availability
- [ ] Quorum $w + r > n$ is necessary but not sufficient for strong consistency -- sloppy quorums, concurrent writes, and network partitions can still cause staleness
- [ ] Conflict resolution in multi-leader/leaderless systems: prefer avoidance first, then CRDTs for automatic merge, LWW only when data loss is acceptable
- [ ] Partitioning: hash for even distribution (no range queries), range for sorted access (hot spot risk), compound keys to get both
- [ ] MVCC enables snapshot isolation without read-write lock contention: each transaction sees a frozen point-in-time view via versioned rows
- [ ] Snapshot isolation prevents most anomalies but NOT write skew (two txns read same rows, write different rows, violate constraint) -- need serializable isolation
- [ ] Three paths to serializability: actual serial execution (simple but single-threaded), 2PL (pessimistic, deadlock-prone), SSI (optimistic, best for low-contention workloads)
