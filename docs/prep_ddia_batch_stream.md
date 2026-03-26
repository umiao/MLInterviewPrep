# System Design: Batch & Stream Processing (DDIA Ch18-19)

## Overview

DDIA Part III covers the two fundamental paradigms for processing data at scale: batch processing (bounded datasets, high throughput) and stream processing (unbounded datasets, low latency). For MLE interviews, these chapters provide essential vocabulary for designing data pipelines, feature stores, and real-time ML serving systems -- understanding MapReduce vs modern dataflow engines, join strategies, message broker trade-offs, windowing semantics, and exactly-once processing guarantees.

## Core Concepts

### System Classification

Three categories of data systems by response pattern:
- **Services (online systems)**: Request-response. Latency and availability are key metrics.
- **Batch processing (offline systems)**: Run periodically over bounded input. Throughput is key metric.
- **Stream processing (near real-time)**: Continuous processing of unbounded input. Latency + throughput both matter.

### Unix Philosophy and Batch Design

The Unix pipe model is the conceptual ancestor of batch processing:

1. Each program does **one thing** well
2. Output of every program becomes input to another (composability)
3. Rapid prototyping and incremental iteration
4. Standard interface: **files** (ordered byte sequences) connect programs

Key properties inherited by batch systems:
- **Separation of logic and wiring**: Programs are agnostic to their data source/sink
- **Immutable inputs**: Input files are never modified; safe to retry
- **Inspectability**: Intermediate results can be examined for debugging
- **Restartability**: Later stages can restart without rerunning the entire pipeline

### HDFS and Distributed Filesystems

**HDFS (Hadoop Distributed File System)** follows the shared-nothing principle:
- Commodity hardware with data redundancy for fault tolerance
- **NameNode**: Central server tracking which file blocks reside on which machines
- **Daemon processes** on each node expose network file access
- Similar model: Amazon S3, Azure Blob Storage, GFS (Google File System)

### MapReduce

The distributed analogue of Unix pipelines, operating on HDFS:

**Two callback functions**:
- **Mapper**: Called once per input record. Extracts key-value pairs. Stateless.
- **Reducer**: Receives all values for a given key. Produces output.

**Execution flow**:
1. Mappers process input partitions, emit $(key, value)$ pairs
2. Framework **partitions** by hash of key (same key goes to same reducer)
3. Key-value pairs are **sorted** by key within each partition
4. **Shuffle**: Reducers download sorted files from mappers and merge them
5. Reducers process all values for each key sequentially

**Critical property**: Reducers process one key's records at a time, keeping only **one record in memory** -- no network requests needed during processing. This separates **physical network communication** from **application logic**.

**Chained MapReduce** writes intermediate results to disk between jobs (like temporary files between Unix commands). This is a major performance bottleneck -- Hadoop writes to disk excessively.

### Join Patterns in MapReduce

#### Reduce-Side Joins (Sort-Merge Join)

Full table scan approach (no indexes). Steps:
1. Multiple mappers extract $(join\_key, value)$ from different tables
2. Framework groups all records by join key
3. Reducer sees all records for a key adjacently (sorted)

**Secondary sort**: Ensures reducer sees dimension table record (e.g., user profile) before fact records (e.g., activity events), within each key group.

#### Map-Side Joins

Avoid expensive shuffle/sort by exploiting input structure:

| Strategy | Requirement | Mechanism |
|----------|------------|-----------|
| **Broadcast hash join** | One input fits in memory | Each mapper loads small table into hash map |
| **Partitioned hash join** | Both inputs partitioned identically | Hash join per partition independently |
| **Map-side merge join** | Both inputs partitioned AND sorted by same key | Mapper merges sorted streams |

For broadcast joins where the small table is slightly too large for memory, store it as a **read-only index on local disk**.

### Handling Skew (Hot Keys)

MapReduce must wait for all tasks in a stage to complete. Hot keys (e.g., celebrity user IDs) create stragglers.

**Mitigation strategies**:
1. **Sampling** to detect hot keys at runtime
2. Send hot key records to **multiple reducers** (not just one determined by hash)
3. **Replicate** the other join input to all reducers handling the hot key
4. Aggregate partial results from multiple reducers
5. If hot keys are known in advance, store them separately

### Dataflow Engines (Spark, Flink, Tez)

Modern alternatives that treat the entire workflow as **one job** with a DAG of operators:

**Key differences from MapReduce**:

| Aspect | MapReduce | Dataflow Engines |
|--------|-----------|-----------------|
| Intermediate state | Written to HDFS (materialized) | In-memory or local disk |
| Operator flexibility | Strict map then reduce | Arbitrary operator graph (DAG) |
| Sorting | Always performed | Only where required |
| Stage boundaries | Must wait for full stage completion | Operators start when input is ready |
| JVM reuse | New JVM per task | Reuse existing JVMs |
| Locality optimization | Limited | Explicit data dependencies enable co-location |

**How operators connect**:
- **Repartition and sort** by key (like MapReduce shuffle)
- **Repartition without sorting** (hash partition only)
- **Broadcast**: Send one operator's output to all partitions of the next

### Fault Tolerance in Batch Processing

**MapReduce**: Tolerates individual task failures by retrying. Intermediate data on HDFS is durable. Suitable for large, long-running jobs. Batch jobs are lower priority and may be **preempted**, making recovery valuable.

**Dataflow engines (Spark, Flink, Tez)**:
- Intermediate state is NOT on HDFS -- lost when a machine fails
- **Recompute** from available data (prior stage output or original HDFS input)
- **Spark RDD (Resilient Distributed Dataset)**: Tracks lineage (ancestry) of each data partition for recomputation
- **Flink**: Periodic operator state **checkpoints**
- **Determinism requirement**: Non-deterministic computation (e.g., random iteration order) may produce contradictions between old and recomputed data. Use fixed seeds for pseudorandom numbers.
- For expensive computations with small output, still **materialize** to files

**Trade-off analogy**: MapReduce = writing to temporary files between stages; Dataflow = Unix pipes passing data in-stream.

### Graph Processing (Pregel / BSP)

For algorithms like PageRank that require iterative graph traversal:

**Bulk Synchronous Parallel (BSP)** model:
1. Each vertex can **send messages** to adjacent vertices along edges
2. In each iteration, a function is called per vertex with all incoming messages
3. Vertex **retains state in memory** between iterations -- only processes new messages
4. If no messages in a subgraph, no computation needed (sparse activation)

**Limitation**: Difficult to partition graphs so adjacent vertices are co-located. Cross-machine communication overhead is high. Prefer **single-machine** execution when the graph fits.

### Event Streams

A **stream** is data incrementally available over time. An **event** is a small, self-contained, immutable object with a timestamp. Produced by a **producer** (publisher), consumed by one or more **consumers** (subscribers). Related events are grouped into **topics**.

**Polling** for new events is expensive when most requests return empty. Better: **push notification** via messaging systems.

### Message Brokers

A message broker (message queue) is a database optimized for message streams:

| Aspect | Message Broker | Database |
|--------|---------------|----------|
| Delivery | Messages deleted after acknowledgement | Data persists |
| Working set | Assumed small (queue is short) | Arbitrary size |
| Query model | Subscribe to topic patterns | Arbitrary queries with indexes |
| Notification | Push to consumers on data change | Snapshot isolation for reads |

**Multiple consumer patterns**:
- **Load balancing**: Each message to one consumer (shared work)
- **Fan-out**: Each message to all consumers (broadcast)
- Can be combined

**Acknowledgement**: Consumer must ACK before broker deletes message. If consumer crashes before ACK, message is **redelivered** to another consumer. Load balancing + redelivery causes **message reordering** -- avoid load balancing when causal dependencies exist.

### Log-Based Message Brokers (Kafka)

Combines durability of databases with low-latency notification:

**Architecture**:
- Producers append to end of log; consumers read sequentially
- Log partitioned by topic across machines for higher throughput
- Each message has a **monotonically increasing offset** within its partition
- **Total ordering** within a partition; **no ordering** across partitions

**Consumer model**:
- Supports **fan-out** natively (consumers read log independently)
- Load balancing at **partition level** (coarse-grained); single-threaded per partition
- Consumer maintains **offset** as checkpoint; on failure, another node resumes from that offset
- Append-only log enables **replay** and **recovery**

**Limitations**:
1. Max consumers per topic = number of partitions
2. Single slow message blocks all subsequent messages in that partition

**Disk management**: Log divided into **segments**; old segments deleted or archived. Effectively a **bounded circular buffer**. Throughput is more constant than memory-based brokers since all writes go to disk anyway.

### Change Data Capture (CDC)

**Problem**: Multiple derived systems (OLTP, cache, index, warehouse) need to stay in sync. **Dual writes** (writing to each system explicitly) are prone to race conditions and partial failures.

**Solution**: Make one database the **leader**; use its change log to update derived **followers** via a log-based message broker.

**Implementation details**:
- Derived systems are just different **views** on the same data
- Database triggers can implement CDC (but with poor performance)
- **Log compaction**: Discard duplicates, keep only latest value per key. Deleted keys marked with **tombstone** then removed.
- **Initial snapshot** for new consumers must correspond to a known log **offset**
- With log compaction, new consumers can scan from the beginning without a separate snapshot

### Event Sourcing

Store all state changes as an **immutable, append-only event log** at the application level.

**CDC vs Event Sourcing**:

| Aspect | Change Data Capture | Event Sourcing |
|--------|-------------------|----------------|
| Level | Low-level (DB change logs) | Application-level (domain events) |
| Mutability | Application uses DB mutably | Events are immutable |
| Awareness | Application unaware of CDC | Application designed around events |
| History | Can discard old events (compaction) | Typically retains full history |
| Example event | "Row X updated to value Y" | "Student cancelled enrollment" |

**Benefits**: Events capture **intent** (why something happened), not just side effects. New side effects can be chained off existing events.

**Command vs Event**: A user request starts as a **command** (may fail validation). Once accepted, it becomes an immutable **event**. Validation happens before the command becomes an event.

**CQRS (Command Query Responsibility Segregation)**: Derive multiple **read-optimized views** from the same event log. Breaks the assumption that data must be written in the same form it is queried. Helps resolve normalization vs denormalization debates.

**Limitation**: Event log to read view is typically **asynchronous** -- reads may see stale data. Mitigation: synchronous view updates or total order broadcast.

**Immutability trade-offs**:
- High update/delete rate on small dataset: History grows large; **compaction/GC** performance is critical
- Privacy/compliance (**excision/shunning**): May need to truly delete data by rewriting history

### Stream Processing Operators

A stream processor (operator/job) consumes input in **read-only** fashion and writes output **append-only**.

**Applications**:

| Use Case | Description | Key Detail |
|----------|------------|------------|
| Complex Event Processing (CEP) | Pattern matching across event streams | Queries are long-lived; state machines detect patterns |
| Stream Analytics | Aggregations over time windows | Probabilistic algorithms (Bloom filters, HyperLogLog) |
| Materialized View Maintenance | Derive query-optimized views from events | May need unbounded history (no windowing) |
| Search on Streams | Match events against stored queries | Elasticsearch percolator: index queries, not documents |
| Monitoring | Detect anomalies and correlations | Real-time alerting on pattern matches |

### Window Types

Windows define the time boundaries for stream aggregation:

| Window Type | Fixed Length? | Overlap? | Implementation | Use Case |
|-------------|-------------|----------|----------------|----------|
| **Tumbling** | Yes | No (each event in exactly 1 window) | Round timestamp down to interval | Fixed-interval metrics (per-minute counts) |
| **Hopping** | Yes | Yes (overlapping windows) | Multiple tumbling windows offset | Smoothed aggregations |
| **Sliding** | Yes | Yes (event-triggered) | Buffer + expire old events | "Events within last 5 minutes of each other" |
| **Session** | No (variable) | No | Group by user activity; gap = boundary | User session analytics |

**Clock challenge**: No unified reliable clock. Mitigation: log three timestamps -- device clock at event time, device clock at send time, server clock at receive time. Estimate device-server offset from the latter two.

### Stream Joins

| Join Type | Description | State Required | Example |
|-----------|------------|----------------|---------|
| **Stream-stream** (window join) | Join two streams within a time window | Buffered events from both streams | Link search queries to click events by session ID |
| **Stream-table** (enrichment) | Enrich stream events with table data | Local copy of table (updated via CDC) | Add user profile to activity events |
| **Table-table** (materialized view) | Maintain a view joining two tables | Full materialized state | Sync celebrity tweets to all followers' timelines |

**Time dependency**: Joined data can change over time (e.g., tax rates). **Slowly Changing Dimension (SCD)**: Use a unique identifier per version of the record. Makes joins deterministic but prevents log compaction.

### Fault Tolerance in Stream Processing

**Challenge**: Stream is infinite -- cannot wait until "finished" to produce output.

**Exactly-once semantics** (effectively-once): Even if tasks fail and retry, the visible effect is as if processed once.

**Approaches**:

| Strategy | Mechanism | Trade-off |
|----------|-----------|-----------|
| **Microbatching** | Break stream into small blocks; treat each as mini batch | Implicit tumbling window; latency = batch interval |
| **Checkpointing** | Periodic snapshots of operator state to durable storage | Recovery replays from last checkpoint |
| **Idempotent operations** | Design writes so repeating them has same effect as doing once | Most flexible; requires careful design |
| **Distributed transactions (2PC)** | Atomic commit across stream processor + external sink | High latency; external systems (e.g., email) cannot roll back |

**Key insight**: For external side effects (sending emails, charging credit cards), checkpoints alone are insufficient. Prefer **idempotent** design where possible.

## Implementation

### Batch vs Stream Processing Decision Framework

```python
def choose_processing_model(
    latency_requirement: str,  # "seconds", "minutes", "hours", "daily"
    input_bounded: bool,
    reprocessing_needed: bool,
) -> dict:
    """Select batch vs stream processing based on requirements."""
    if input_bounded and latency_requirement in ("hours", "daily"):
        return {
            "model": "batch",
            "engine": "Spark (batch mode) or Flink (batch mode)",
            "reason": "Bounded input + relaxed latency = batch is simpler",
        }
    elif latency_requirement in ("seconds", "minutes"):
        return {
            "model": "stream",
            "engine": "Flink or Kafka Streams",
            "reason": "Low latency requires continuous processing",
            "fault_tolerance": "checkpointing + idempotent sinks",
        }
    else:
        return {
            "model": "lambda_or_kappa",
            "batch_engine": "Spark",
            "stream_engine": "Flink",
            "reason": "Medium latency with reprocessing: consider unified engine",
            "note": "Kappa (stream-only with replay) preferred if Kafka retains full history",
        }
```

### Join Strategy Selection

```python
def choose_join_strategy(
    small_table_fits_memory: bool,
    inputs_co_partitioned: bool,
    inputs_sorted: bool,
    is_streaming: bool,
) -> str:
    """Select optimal join strategy for batch or stream processing."""
    if is_streaming:
        # Stream joins are fundamentally different
        return "stream_join (window/enrichment/materialized_view)"
    # Batch join strategies (MapReduce / dataflow)
    if small_table_fits_memory:
        return "broadcast_hash_join (map-side; load small table in each mapper)"
    if inputs_co_partitioned and inputs_sorted:
        return "map_side_merge_join (sorted merge per partition)"
    if inputs_co_partitioned:
        return "partitioned_hash_join (hash join per partition)"
    return "reduce_side_sort_merge_join (shuffle + sort + merge)"
    # Key insight: map-side joins avoid shuffle but require input guarantees.
    # Reduce-side joins always work but are most expensive.
```

### Window Type Selection

```python
def choose_window_type(
    fixed_interval: bool,
    needs_overlap: bool,
    event_driven: bool,
    user_session_based: bool,
) -> dict:
    """Select appropriate window type for stream aggregation."""
    if user_session_based:
        return {
            "type": "session",
            "impl": "Group events per user; gap threshold defines boundary",
            "note": "Variable length; ends on user inactivity",
        }
    if event_driven:
        return {
            "type": "sliding",
            "impl": "Buffer events; expire when outside interval",
            "note": "Window moves with each event, not wall clock",
        }
    if fixed_interval and needs_overlap:
        return {
            "type": "hopping",
            "impl": "Multiple offset tumbling windows",
            "note": "Provides smoothing; each event in multiple windows",
        }
    return {
        "type": "tumbling",
        "impl": "Round timestamp down to nearest interval boundary",
        "note": "Simplest; each event in exactly one window",
    }
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| "Design a real-time feature pipeline" | ML system design | Stream for low-latency features; batch for historical recomputation; CDC to sync feature store |
| "MapReduce vs Spark: key differences?" | Data engineering fundamentals | Spark avoids materializing intermediate state to HDFS; DAG execution; in-memory processing |
| "How does Kafka guarantee ordering?" | Message broker design | Total ordering within a partition via monotonic offsets; no cross-partition ordering guarantee |
| "Tumbling vs sliding window?" | Stream aggregation design | Tumbling: fixed, non-overlapping, simple. Sliding: event-triggered, overlapping, captures proximity |
| "How do you achieve exactly-once processing?" | Fault tolerance discussion | Idempotent writes preferred; microbatching + checkpointing for internal state; 2PC only as last resort |
| "Broadcast join vs shuffle join?" | Query optimization | Broadcast when one table fits in memory (avoids shuffle); shuffle (reduce-side) is general-purpose |
| "How do you handle hot keys?" | Skew in distributed systems | Detect via sampling; split to multiple reducers; replicate other input; aggregate partial results |

### Common Interview Questions

- [ ] Explain the MapReduce execution model. What are its main bottlenecks?
- [ ] When would you use a map-side join vs a reduce-side join?
- [ ] How does Spark improve on MapReduce? What is an RDD?
- [ ] Compare Kafka (log-based) with traditional message brokers. When to use which?
- [ ] What is Change Data Capture? How does it keep derived systems in sync?
- [ ] Explain Event Sourcing and CQRS. When would you use them?
- [ ] What are the four window types in stream processing? Give a use case for each.
- [ ] Describe the three types of stream joins with examples.
- [ ] How does exactly-once processing work in Flink vs Spark Streaming?
- [ ] What is the Pregel/BSP model for graph processing?
- [ ] Design a system that computes real-time click-through rates for search queries.
- [ ] How would you handle a data pipeline that needs both real-time and historical reprocessing?

## Comparisons

### Batch vs Stream Processing

| Aspect | Batch Processing | Stream Processing |
|--------|-----------------|-------------------|
| Input | Bounded (finite dataset) | Unbounded (continuous) |
| Latency | Minutes to hours | Milliseconds to seconds |
| Throughput | Very high (optimized for it) | Moderate (trade-off with latency) |
| Fault tolerance | Retry failed tasks; input is durable | Checkpointing + idempotent writes |
| State management | Implicit (between stages) | Explicit (operator state, windows) |
| Use case | ETL, model training, reports | Alerting, real-time dashboards, feature serving |

### MapReduce vs Dataflow Engines

| Aspect | MapReduce | Spark | Flink |
|--------|-----------|-------|-------|
| Execution model | Map then reduce (rigid) | DAG of arbitrary operators | DAG with streaming-first design |
| Intermediate state | HDFS (disk) | Memory (spill to disk) | Memory + checkpoints |
| Fault tolerance | Task retry (data on HDFS) | RDD lineage recomputation | Operator state checkpoints |
| Sorting | Always (every shuffle) | Only when needed | Only when needed |
| Streaming support | No (batch only) | Microbatch (Spark Streaming) | True streaming (event-at-a-time) |
| Latency | High (disk I/O) | Medium | Low |

### Message Broker Architectures

| Aspect | Traditional (RabbitMQ) | Log-Based (Kafka) |
|--------|----------------------|-------------------|
| Delivery model | Push to consumers | Consumers pull from log |
| Message retention | Deleted after ACK | Retained (configurable TTL / compaction) |
| Ordering | Per-consumer (with caveats) | Per-partition (strict) |
| Replay | Not possible | Replay by resetting offset |
| Consumer scaling | Per-message load balancing | Per-partition assignment |
| Throughput | Lower (per-message overhead) | Higher (sequential I/O) |
| Best for | Task queues, request routing | Event streaming, CDC, analytics |

### Join Strategies

| Strategy | Type | Requirement | Cost | When to Use |
|----------|------|------------|------|-------------|
| Broadcast hash join | Map-side | Small table fits in memory | Low (no shuffle) | Dimension table enrichment |
| Partitioned hash join | Map-side | Co-partitioned inputs | Low (per-partition) | Pre-partitioned datasets |
| Map-side merge join | Map-side | Co-partitioned + sorted | Low (streaming merge) | Pre-sorted datasets |
| Reduce-side sort-merge | Reduce-side | None (general purpose) | High (shuffle + sort) | Default when no structure guarantees |

### CDC vs Event Sourcing vs Dual Writes

| Aspect | Dual Writes | CDC | Event Sourcing |
|--------|------------|-----|----------------|
| Consistency | Prone to race conditions | Consistent (single leader) | Consistent (append-only log) |
| Implementation | Application writes to each system | Capture DB change log | Application emits domain events |
| History | No history | Compactable | Full history preserved |
| Complexity | Low (but fragile) | Medium (infrastructure) | High (domain modeling) |
| Failure handling | Partial writes possible | Log replay on failure | Event replay on failure |

## Key Takeaways

- [ ] **Unix philosophy** applies to batch processing: composable operators, immutable inputs, separation of logic and wiring enable safe retries and debugging
- [ ] **MapReduce** separates physical communication (shuffle) from application logic (map/reduce), but materializing all intermediate state to HDFS is its main bottleneck
- [ ] **Map-side joins** (broadcast, partitioned, merge) avoid expensive shuffles but require input structure guarantees; **reduce-side joins** always work but cost more
- [ ] **Dataflow engines** (Spark, Flink) improve on MapReduce by avoiding unnecessary materialization, supporting arbitrary operator DAGs, and keeping intermediate state in memory
- [ ] **Kafka** (log-based broker) provides total ordering per partition, consumer replay via offsets, and durable retention -- fundamentally different from traditional message queues
- [ ] **CDC** keeps derived systems in sync via a single source-of-truth database's change log; **Event Sourcing** captures domain intent as immutable events with CQRS for read optimization
- [ ] **Window types** match different aggregation needs: tumbling (fixed/disjoint), hopping (fixed/overlapping), sliding (event-triggered), session (activity-based)
- [ ] **Exactly-once processing** is best achieved through **idempotent operations** rather than distributed transactions; microbatching and checkpointing handle internal state recovery
