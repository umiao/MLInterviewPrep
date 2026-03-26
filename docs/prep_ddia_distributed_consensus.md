# System Design: Distributed Systems & Consensus (DDIA Ch16-17)

## Overview

DDIA Part II concludes with the hardest problems in distributed systems: unreliable networks, clock synchronization, process pauses, and achieving consensus across fallible nodes. For MLE interviews, these chapters provide the vocabulary for discussing failure modes, consistency guarantees, and coordination primitives -- understanding why distributed agreement is hard, how CAP constrains your choices, and when to reach for consensus algorithms vs. simpler coordination tools like ZooKeeper.

## Core Concepts

### Faults and Partial Failures

A single computer operates under an idealized model: instructions execute correctly or the machine crashes entirely. Distributed systems introduce **partial failures** -- some components break unpredictably while others continue working.

Key distinction between computing paradigms:
- **HPC (High-Performance Computing)**: Treats the cluster like one big computer. On failure, checkpoint and restart the entire workload. Uses shared memory, RDMA, specialized hardware, nodes physically close together.
- **Cloud Computing**: Prioritizes high availability. Uses commodity hardware, IP/Ethernet, Clos topologies. Embraces fault tolerance: rolling upgrades, kill-and-restart VMs.

**Design principle**: Fault handling must be part of the software design. You can build reliable systems from unreliable components (e.g., error-correcting codes over noisy channels, TCP over unreliable IP), but each layer has limits on how much error it can absorb.

### Unreliable Networks

In a shared-nothing distributed system, nodes communicate by sending packets over the network. There is **no guarantee** when (or whether) a packet arrives.

Failure modes for a single message send:
1. Request lost in transit
2. Request queued, waiting to be delivered
3. Remote node has crashed
4. Remote node temporarily stopped responding (overloaded, GC pause)
5. Response lost in transit
6. Response delayed in the network

The sender **cannot distinguish** these cases -- it only knows it hasn't received a response. The usual approach: declare failure after a **timeout**.

**Network congestion** causes: multiple nodes sending to the same destination (switch queue overflow), OS-level queueing on the receiving machine, CPU contention in virtualized environments, TCP flow control/backpressure adding sender-side queueing.

**TCP vs UDP**: TCP provides reliability via retransmission (application sees latency, not loss). UDP skips retransmission -- used in latency-sensitive applications (video conferencing) where delayed data is worthless.

### Timeouts and Failure Detection

Setting timeout values involves fundamental trade-offs:

| Timeout Too Short | Timeout Too Long |
|-------------------|------------------|
| Falsely declares nodes dead | Slow failure detection |
| Actions performed twice | Extended service degradation |
| Extra load on remaining nodes | Users wait for unresponsive node |
| Risk of cascading failure | Delayed failover |

With bounded network delay $d$ and processing time $r$, timeout = $2d + r$. But most real systems have **unbounded delays**, making static timeouts unreliable.

### Phi Accrual Failure Detector

Rather than a fixed heartbeat timeout, the Phi Accrual detector models heartbeat intervals as a probability distribution and computes a suspicion level:

$$\phi(t_{\text{now}}) = -\log_{10}\left(P_{\text{later}}(t_{\text{now}} - T_{\text{last}})\right)$$

where:

$$P_{\text{later}}(t) = \frac{1}{\sigma\sqrt{2\pi}} \int_t^{+\infty} e^{-\frac{(x - \mu)^2}{2\sigma^2}} dx$$

Parameters $\mu$ and $\sigma$ are estimated from a **sliding window** of observed heartbeat intervals using maximum likelihood estimation.

Properties:
- If node is dead: $\lim_{t \to \infty} \phi(t) = \infty$ (suspicion grows without bound)
- If node is alive: $\phi(t)$ remains bounded and eventually returns to 0
- Each node can set its own threshold for declaring failure

This approach **adapts** to network conditions automatically, unlike fixed timeouts.

### Unreliable Clocks

Machines have two types of clocks:
- **Time-of-day clock** (wall clock): Returns calendar time (seconds since epoch). Can jump backward on NTP sync. Not suitable for measuring durations.
- **Monotonic clock**: Measures elapsed time. Never jumps backward. NTP may adjust its rate (up to 0.05% drift). Suitable for measuring durations.

**NTP (Network Time Protocol)** synchronization:
- Hierarchical stratum system: Stratum 0 = atomic clocks/GPS, Stratum 1 = directly synced, etc.
- Uses Bellman-Ford shortest-path spanning tree to minimize round-trip delay
- Offset estimation: given timestamps $T_1$ (client send), $T_2$ (server receive), $T_3$ (server send), $T_4$ (client receive):

$$\text{delay} = \frac{(T_4 - T_1) - (T_3 - T_2)}{2}, \quad \text{offset} = T_3 + \text{delay} - T_4$$

**Clock synchronization challenges**:
1. Quartz drift (~17s/day without resync)
2. Clock may refuse NTP sync if drift too large (forced reset)
3. NTP accuracy limited by network delay
4. Leap seconds (59 or 61 seconds in a minute; NTP smearing spreads adjustment)
5. VM clock virtualization causes jumps on pause/resume
6. End-user device clocks are untrustworthy

**Consequence**: Last-Write-Wins (LWW) with wall-clock timestamps silently drops data when clocks are skewed. Clock readings should be treated as **confidence intervals**, not point values.

**Logical clocks** (incrementing counters) are preferred for ordering events, as they measure relative ordering without relying on physical time synchronization.

### Synchronized Clocks for Global Snapshots

Snapshot isolation requires monotonically increasing transaction IDs reflecting causality.

- **Google Spanner's TrueTime API**: Reports clock confidence interval $[t_{\text{earliest}}, t_{\text{latest}}]$. Transactions wait the length of the confidence interval before committing, ensuring non-overlapping timestamps.
- Only practical at Google's scale with dedicated GPS/atomic clock infrastructure in every datacenter.

### Process Pauses

Even with correct clocks, a node can experience unexpected pauses that break timing assumptions:

| Cause | Impact |
|-------|--------|
| Stop-the-world Garbage Collection (GC) | All threads frozen (ms to seconds) |
| VM suspension (live migration) | Entire OS paused |
| Context switches / steal time | CPU time consumed by other VMs |
| Disk I/O / paging (thrashing) | Process blocked on slow storage |
| Device suspension (laptops) | Execution halted indefinitely |

**Fencing tokens** solve the split-brain problem caused by pauses: every lock/lease grant includes a monotonically increasing token number. The storage service rejects writes with tokens lower than the highest it has already seen. ZooKeeper's `zxid` or `cversion` can serve as fencing tokens.

### Timing Assumption Models

| Model | Assumption | Realism |
|-------|-----------|---------|
| Synchronous | Bounded delay, bounded pauses, bounded clock error | Not realistic for most systems |
| Partially synchronous | Usually bounded, occasionally exceeds bounds | Most practical model |
| Asynchronous | No timing assumptions, no clocks | Most general, hardest to design for |

**Node failure models**:
- **Crash-stop**: Node crashes and never recovers
- **Crash-recovery**: Node may recover; stable storage survives, in-memory state lost (most practical)
- **Byzantine**: Node can behave arbitrarily, including maliciously

**Safety vs Liveness**:
- **Safety**: Nothing bad happens (can be violated at a specific point in time; violation is permanent)
- **Liveness**: Something good eventually happens (may not hold now, but hope remains)
- Distributed algorithms require safety to hold **always** and liveness to hold **if a majority of nodes survive**

### Byzantine Faults

A node that sends contradictory or malicious messages causes a **Byzantine fault**. Tolerating Byzantine faults requires $n \geq 3f + 1$ nodes where $f$ is the number of faulty nodes.

Most datacenter systems assume **honest but unreliable** nodes and do not implement Byzantine fault tolerance. Protection relies on authentication, access control, encryption, and firewalls. Byzantine fault tolerance is mainly relevant for blockchain/cryptocurrency and aerospace systems.

### Linearizability

The strongest single-object consistency guarantee: the system behaves as if there is only **one copy** of the data with **no replication lag**.

**Definition**: Every operation appears to take effect atomically at some point between its invocation and completion. Once a new value is written or read, all subsequent reads return that value (recency guarantee).

**Compare-and-set (CAS)**: Atomic operation that writes a new value only if the current value matches the expected old value. Essential for implementing distributed locks and uniqueness constraints.

**Linearizability vs Serializability**:

| Property | Linearizability | Serializability |
|----------|----------------|-----------------|
| Scope | Single object (register) | Multi-object (transactions) |
| Guarantee | Recency (real-time ordering) | Equivalent to some serial execution |
| Concurrent ops | Totally ordered | May reorder non-conflicting txns |
| Combined | Strict serializability (strong-1SR) | -- |

2PL and actual serial execution are typically linearizable. **Serializable Snapshot Isolation (SSI) is NOT linearizable** -- reads come from a consistent snapshot that may not include the most recent writes.

### Implementations of Linearizability

| Approach | Linearizable? | Notes |
|----------|--------------|-------|
| Single replica | Yes | No fault tolerance |
| Single-leader replication | Potentially | Only if reading from leader or sync'd follower; beware delusional leaders |
| Consensus algorithms | Yes | Raft, Paxos, ZAB |
| Multi-leader replication | No | Async replication requires conflict resolution |
| Leaderless (Dynamo-style) | Probably not | Even with quorum ($w + r > n$), concurrent reads can return stale values |
| Last-write-wins (clock-based) | No | Clock skew breaks ordering |

**Quorum non-linearizability example**: With $n=3, w=3, r=2$: write new value to A, client X reads {A,B} and gets new value, client Y reads {B,C} and gets old value. Y reads after X but sees older data.

### CAP Theorem

When a **network partition** occurs:
- **CP (Consistent + Partition-tolerant)**: Replicas must wait or return errors until partition heals. Preserves linearizability.
- **AP (Available + Partition-tolerant)**: Replicas process requests independently, even when disconnected. Sacrifices linearizability (e.g., multi-leader replication).

**CAP limitations**: Partitions are not a choice -- they happen as faults. CAP is really "during a partition, choose consistency or availability." It ignores network delays, dead nodes, and other practical trade-offs. Better to reason about specific consistency/availability trade-offs for your system.

**Performance reality**: Even without partitions, most systems abandon linearizability for **performance**. Response time for linearizable operations is at least proportional to network delay uncertainty. Even multi-core CPU RAM is not linearizable (each core has its own cache with async writeback).

### Causal Consistency and Ordering

**Causality** imposes a partial order: cause before effect, question before answer, creation before update.

| Ordering Type | Definition | Example |
|--------------|-----------|---------|
| Total order | Any two elements are comparable | Linearizable systems |
| Partial order | Some elements are incomparable (concurrent) | Causally consistent systems |

**Linearizability implies causal consistency** (stronger guarantee), but causal consistency is the **strongest consistency model** that does not degrade performance under network delays and remains available under network failures.

Tracking causal dependencies: **version vectors** or **logical clocks**.

### Lamport Timestamps

A method for generating sequence numbers consistent with causality.

**Format**: $(counter, nodeID)$ -- counter determines order, nodeID breaks ties.

**Algorithm**:
1. Each node maintains a counter
2. Every request/response includes the sender's maximum known counter
3. On receiving a value greater than local counter, node updates to that maximum
4. Increment counter for each local operation

**Limitation vs version vectors**: Lamport timestamps enforce **total ordering** but cannot distinguish concurrent operations from causally dependent ones. Version vectors can detect concurrency but are less compact.

### Total Order Broadcast

Lamport timestamps alone cannot resolve conflicts like "two users claiming the same username" because a node cannot know if concurrent requests exist at other nodes. **Total order broadcast** (atomic broadcast) solves this.

**Requirements**:
- **Reliable delivery**: If delivered to one node, delivered to all nodes
- **Totally ordered delivery**: All nodes receive messages in the same order

**Properties**:
- Order is **fixed at delivery time** -- no retroactive insertion (stronger than timestamp ordering)
- Equivalent to appending to a shared log that all nodes read in the same sequence
- Fencing tokens = sequence numbers in the log (ZooKeeper's `zxid`)
- Asynchronous: guaranteed order, but no guarantee on delivery **timing**

**Equivalence**: Total order broadcast $\equiv$ consensus. Both are equivalent to a linearizable compare-and-set register.

**State machine replication**: If every replica processes the same writes in the same order from the total order broadcast log, replicas remain consistent.

### Two-Phase Commit (2PC)

Ensures atomic commit across multiple nodes: all commit or all abort.

**Protocol**:
1. Application requests globally unique transaction ID
2. Application performs reads/writes on each participant, tagged with transaction ID
3. **Phase 1 (Prepare)**: Coordinator asks all participants "Can you commit?" Participant writes all data to disk, checks constraints. "Yes" = surrenders right to abort.
4. **Phase 2 (Commit)**: If all voted yes, coordinator writes commit decision to its log (**commit point**), then sends commit request to all. Retries forever on failure.

**Two points of no return**:
1. Participant votes "yes" -- promises to commit if asked
2. Coordinator decides -- decision is irrevocable

**Coordinator failure problem**: If coordinator crashes after participants vote "yes" but before sending commit/abort, participants are **in doubt** -- they cannot abort (already promised) or commit (no instruction). They must wait for coordinator recovery. This makes 2PC a **blocking** protocol.

**3PC**: Proposed as non-blocking alternative, but requires bounded network delay and bounded response times. Without a perfect failure detector, 3PC cannot guarantee atomicity. 2PC remains dominant.

### XA Transactions

**X/Open XA (eXtended Architecture)**: Standard C API for 2PC across heterogeneous systems (different databases, message brokers).

**Limitations**:
1. Coordinator is a single point of failure (usually a library in the application process)
2. In-doubt transactions hold locks indefinitely until coordinator recovers
3. Breaks stateless application model (coordinator logs are stateful)
4. Lowest common denominator: cannot use SSI, cannot detect cross-system deadlocks
5. Orphaned in-doubt transactions may require manual administrator intervention
6. **Heuristic decisions** (emergency unilateral commit/abort) break atomicity guarantees

### Fault-Tolerant Consensus

**Properties** a consensus algorithm must satisfy:
1. **Uniform agreement**: No two nodes decide differently
2. **Integrity**: No node decides twice
3. **Validity**: Decided value was proposed by some node
4. **Termination**: Every non-crashed node eventually decides (requires majority quorum)

A dictator satisfies 1-3 but not termination (no fault tolerance). 2PC satisfies 1-3 but not termination (blocks on coordinator failure).

**FLP impossibility result**: No algorithm can guarantee consensus in an asynchronous system where nodes may crash (no clocks, no timeouts). With timeouts or randomization, consensus becomes solvable.

**Major algorithms**: Viewstamped Replication (VSR), Paxos, Raft, ZAB. All decide on a **sequence of values**, making them total order broadcast algorithms.

### Epoch Numbering and Quorums

Consensus protocols use a leader, but leadership is itself determined by consensus.

**Mechanism**:
1. Each epoch (term/ballot/view) has a unique, monotonically increasing number
2. Within each epoch, the leader is unique
3. If leaders from different epochs conflict, higher epoch number wins
4. Leader must get **quorum** approval for each proposal
5. A node votes for a proposal only if unaware of a higher-epoch leader
6. **Two rounds of voting**: one for leader election, one for proposals. Quorums must **overlap** -- at least one node in the proposal quorum also participated in the latest leader election

**Limitations of consensus**:
- Proposal voting is **synchronous replication** -- data loss possible if leader fails before replication
- Requires **strict majority** (fixed node set; adding/removing nodes needs dynamic membership extensions)
- **Network-sensitive**: relies on timeouts for failure detection; unstable networks cause frequent leader elections

### ZooKeeper and Distributed Coordination

ZooKeeper (and similar: etcd, Consul) provides distributed coordination primitives built on fault-tolerant total order broadcast:

| Feature | Mechanism |
|---------|-----------|
| Linearizable atomic operations | Consensus-backed writes (locks, CAS) |
| Failure detection | Long-lived sessions with heartbeats; session timeout releases ephemeral nodes |
| Change notifications | Clients watch for changes (no polling needed) |
| Leader election | Via ephemeral nodes + sequential ordering |
| Service discovery | Register services as znodes |
| Partition assignment | Coordinate shard ownership |

**Characteristics**: Runs on fixed number of nodes with majority voting; supports large number of clients; manages slow-changing configuration/coordination data (not runtime application state).

## Implementation

### Failure Detection Decision Framework

```python
def choose_failure_detector(
    network_variability: str,  # "low", "medium", "high"
    false_positive_cost: str,  # "low", "medium", "high"
) -> str:
    """Select failure detection strategy based on system characteristics."""
    if network_variability == "low" and false_positive_cost == "low":
        return "fixed_timeout"  # Simple, predictable networks (e.g., single datacenter)
    elif network_variability == "high" or false_positive_cost == "high":
        return "phi_accrual"  # Adaptive: learns from heartbeat distribution
    else:
        return "sliding_window_timeout"  # Moderate: adjust timeout periodically
    # Key insight: Phi Accrual adapts per-connection, not globally.
    # Each monitored node has its own distribution parameters.
```

### Consistency Model Selection

```python
def choose_consistency_model(
    use_case: str,
    partition_tolerance_required: bool = True,
) -> dict:
    """Guide consistency model selection for distributed systems."""
    models = {
        "distributed_lock": {
            "model": "linearizable",
            "implementation": "consensus (Raft/Paxos via ZooKeeper/etcd)",
            "reason": "Lock correctness requires recency guarantee",
        },
        "user_feed": {
            "model": "eventual_consistency",
            "implementation": "leaderless or multi-leader replication",
            "reason": "Availability > strict ordering for social feeds",
        },
        "bank_transfer": {
            "model": "strict_serializability",
            "implementation": "2PL or serial execution + linearizable storage",
            "reason": "Both transaction isolation and recency required",
        },
        "collaborative_editing": {
            "model": "causal_consistency",
            "implementation": "CRDTs or operational transform with version vectors",
            "reason": "Strongest model that stays available under partitions",
        },
        "config_management": {
            "model": "linearizable",
            "implementation": "ZooKeeper / etcd (consensus-backed)",
            "reason": "All nodes must see same config; slow-changing data",
        },
    }
    return models.get(use_case, {
        "model": "causal_consistency",
        "reason": "Default: strongest model without availability sacrifice",
    })
```

### 2PC vs Consensus Comparison

```python
def atomic_commit_strategy(
    participants_homogeneous: bool,
    coordinator_reliability: str,  # "low", "medium", "high"
    latency_budget_ms: int,
) -> dict:
    """Select distributed commit strategy."""
    if not participants_homogeneous:
        return {
            "strategy": "XA/2PC",
            "reason": "Heterogeneous systems require standard 2PC protocol",
            "warning": "Coordinator is SPOF; in-doubt txns hold locks",
            "mitigation": "Minimize transaction scope; use heuristic decisions as last resort",
        }
    if coordinator_reliability == "high" and latency_budget_ms > 100:
        return {
            "strategy": "2PC_internal",
            "reason": "Homogeneous DB with reliable coordinator; simpler than consensus",
        }
    return {
        "strategy": "consensus_based",
        "reason": "Raft/Paxos tolerate leader failure without blocking",
        "trade_off": "Requires majority quorum; higher message complexity",
    }
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| "What happens if the network partitions?" | Any distributed system design | Must choose CP or AP; explain which and why for your system |
| "How do you detect node failure?" | Leader election, load balancing | Fixed timeouts vs Phi Accrual; trade-off between false positives and detection speed |
| "Why not just use timestamps?" | Ordering events, conflict resolution | Wall clocks have unbounded skew; use logical clocks (Lamport/vector) for causality |
| "How do you prevent split brain?" | Leader-based systems | Fencing tokens: monotonically increasing token rejected if stale |
| "Linearizability vs serializability?" | Database consistency discussions | Linearizability = single-object recency; serializability = multi-object transaction isolation |
| "When would you use ZooKeeper?" | Coordination, leader election | Slow-changing config/coordination data; not for runtime state |
| "What if the 2PC coordinator crashes?" | Distributed transactions | Participants stuck in-doubt; blocking protocol; consider consensus-based alternatives |

### Common Interview Questions

- [ ] Explain the CAP theorem. What are its practical limitations?
- [ ] What is linearizability? How does it differ from serializability?
- [ ] How does the Raft consensus algorithm work? (Leader election, log replication, safety)
- [ ] What happens when a 2PC coordinator crashes mid-transaction?
- [ ] When would you choose causal consistency over linearizability?
- [ ] How do fencing tokens prevent split-brain scenarios?
- [ ] Why is ZooKeeper used for leader election and service discovery?
- [ ] What is the Phi Accrual failure detector and when would you use it?
- [ ] Explain total order broadcast and its relationship to consensus
- [ ] Why do most real systems sacrifice linearizability? (performance, availability)
- [ ] What are the trade-offs between 2PC and consensus-based atomic commit?
- [ ] How do Lamport timestamps work? What can't they tell you that version vectors can?

## Comparisons

### Consistency Models

| Model | Guarantee | Availability Under Partition | Performance Cost | Use Case |
|-------|----------|------------------------------|-----------------|----------|
| Linearizability | Recency (single object) | No (must wait or error) | High (proportional to network delay) | Locks, uniqueness constraints |
| Causal consistency | Cause-before-effect ordering | Yes | Moderate (track dependencies) | Collaborative editing, social feeds |
| Eventual consistency | Convergence (eventually) | Yes | Low | Caches, DNS, session data |
| Strict serializability | Linearizable + serializable | No | Highest | Financial transactions |

### Failure Detection Approaches

| Approach | Adaptiveness | False Positive Rate | Complexity | Best For |
|----------|-------------|--------------------:|------------|----------|
| Fixed timeout | None | High in variable networks | Low | Stable, low-latency networks |
| Sliding window | Low (periodic adjustment) | Medium | Medium | Moderate variability |
| Phi Accrual | High (per-connection) | Low (tunable threshold) | Medium | Cross-datacenter, variable latency |

### Distributed Commit Protocols

| Aspect | 2PC | 3PC | Consensus (Raft/Paxos) |
|--------|-----|-----|----------------------|
| Blocking? | Yes (coordinator failure) | No (bounded delay assumed) | No (leader re-election) |
| Fault tolerance | Coordinator is SPOF | Requires perfect failure detector | Tolerates $f < n/2$ failures |
| Message rounds | 2 | 3 | 2+ (depends on algorithm) |
| Practical use | XA transactions, heterogeneous systems | Rarely used | ZooKeeper, etcd, CockroachDB |
| Assumption | Coordinator eventually recovers | Bounded network delay | Majority quorum available |

### Clock Types

| Type | Source | Monotonic? | Accuracy | Use For |
|------|--------|-----------|----------|---------|
| Time-of-day (wall clock) | NTP sync | No (can jump) | ms to 100ms+ | Human-readable timestamps |
| Monotonic clock | Local oscillator | Yes | ns resolution | Measuring durations, timeouts |
| Logical clock (Lamport) | Counter + node ID | Yes (total order) | Exact causal order | Event ordering in distributed systems |
| Vector clock | Counter per node | N/A (partial order) | Detects concurrency | Conflict detection, version vectors |
| TrueTime (Google) | GPS + atomic clocks | Yes (with interval) | ~7ms confidence | Global snapshot isolation (Spanner) |

### Timing Models vs Node Failure Models

| Timing Model | Node Failure Model | Consensus Possible? | Practical Example |
|-------------|-------------------|--------------------:|-------------------|
| Synchronous | Crash-stop | Yes (trivially) | Theoretical only |
| Partially synchronous | Crash-recovery | Yes (Raft, Paxos) | Most production systems |
| Asynchronous | Crash-stop | No (FLP result) | Requires randomization or timeouts |
| Partially synchronous | Byzantine ($f < n/3$) | Yes (PBFT) | Blockchain, aerospace |

## Key Takeaways

- [ ] Distributed systems have **partial failures** -- you cannot tell if a message was lost or delayed; design for uncertainty
- [ ] Timeouts are the only reliable failure detection method, but static values cause either false positives or slow detection; prefer adaptive approaches like Phi Accrual
- [ ] **Wall clocks are unreliable** for ordering events -- use logical clocks (Lamport timestamps, version vectors) for causal ordering
- [ ] **Linearizability** (recency guarantee on single objects) is distinct from **serializability** (transaction isolation); combining them gives strict serializability
- [ ] **CAP theorem**: during a network partition, choose consistency (wait/error) or availability (serve stale data); most systems sacrifice linearizability for performance even without partitions
- [ ] **Causal consistency** is the strongest model that remains available under network failures -- prefer it over linearizability unless recency is truly required
- [ ] **2PC is blocking**: coordinator failure leaves participants stuck in-doubt holding locks; consensus algorithms (Raft/Paxos) provide non-blocking alternatives
- [ ] **Fencing tokens** prevent split-brain: the storage layer rejects writes with tokens lower than the highest it has seen
