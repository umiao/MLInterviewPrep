"""Populate distributed-task-queue system design module with all 8 sections.

Usage:
    python scripts/content_distributed_task_queue.py

Covers failure modes, idempotency, exactly-once semantics, broker comparison.
Idempotent: overwrites existing content for the distributed-task-queue slug.
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

### What Is a Distributed Task Queue?

A distributed task queue decouples **work submission** from **work execution**.
The core contract has four actors:

| Actor | Role |
|-------|------|
| **Producer** | Submits a task (API server, scheduler, webhook handler) |
| **Broker** | Durably stores pending tasks in a queue (Redis, RabbitMQ, SQS, Kafka) |
| **Worker** | Dequeues, executes, and acknowledges completion |
| **Result Backend** | Stores execution results (DB, Redis, S3) |

### Why "Fire and Forget" Breaks in Production

The naive approach -- enqueue and assume completion -- fails because:

1. **Workers crash.** OOM kills, hardware failures, and SIGKILL leave tasks
   half-executed with no cleanup opportunity.
2. **Networks partition.** An acknowledgment can be lost even though the task
   completed successfully, causing the broker to redeliver.
3. **Brokers restart.** In-memory queues (Redis RDB) lose unacknowledged tasks
   between snapshots.
4. **Tasks poison the queue.** A permanently failing task retries forever,
   consuming worker capacity and starving healthy tasks.
5. **Deployments introduce version skew.** Rolling deploys mean old-version
   and new-version workers coexist, creating serialization mismatches.

### Why This Module Matters for Interviews

Distributed task queues appear in nearly every system design interview that
involves asynchronous processing: email delivery, payment processing, image
resizing, ML inference pipelines, notification fanout. The interviewer is not
testing whether you know Celery's API -- they want to hear you **reason about
failure modes** and **articulate recovery strategies**.

The key insight: **reliability is not a feature of the broker -- it is an
emergent property of how the producer, broker, worker, and consumer interact
under failure conditions.** A "reliable" broker (RabbitMQ with durable queues)
still produces duplicates if the ack is lost. An "unreliable" broker (Redis
with RDB) can be made safe if the consumer is idempotent and the system
tolerates reprocessing.

### The Central Question

> "How do you ensure each task is executed **exactly once** in a distributed
> system where any component can fail at any time?"

The answer: you don't. You achieve **at-least-once delivery** with
**idempotent consumers**, which produces **effectively-once processing**.
This module walks through every failure scenario that motivates this design.
"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## Architecture Deep Dive

### Core Components

```
Producer ──enqueue──> Broker ──dequeue──> Worker Pool
                        |                    |
                        |                    ├── execute task
                        |                    ├── write to DB / external system
                        |                    └── ack back to broker
                        |
                   Result Backend <── result stored
```

### Broker Options

#### Redis (Celery Default)

**Persistence modes:**
- **RDB (snapshotting):** Periodic dumps to disk. Tasks enqueued between
  snapshots are lost on crash. Default: dump every 60s if 1000+ keys changed.
- **AOF (append-only file):** Logs every write. `fsync` policy determines
  durability:
  - `always`: fsync after every write (safest, slowest)
  - `everysec`: fsync once per second (1s data loss window)
  - `no`: OS decides (fast, up to 30s data loss)
- **No native acknowledgment.** Celery implements ack via `BRPOPLPUSH` into
  an "unacked" list. If the worker dies, the task stays in the unacked list
  and must be reclaimed (visibility timeout pattern).

**Trade-off:** Ultra-low latency, but durability requires careful tuning.
Best for workloads where occasional task loss is acceptable or idempotent
re-execution is cheap.

#### RabbitMQ

**Durability stack:**
1. **Durable queue:** Queue metadata survives broker restart.
2. **Persistent messages:** Messages written to disk (delivery_mode=2).
3. **Publisher confirms:** Broker acks back to producer after persisting.
4. **Consumer acks:** Worker explicitly acks after processing.

**High availability:**
- **Mirrored queues (classic):** Full queue replicated to N nodes. Deprecated.
- **Quorum queues (modern):** Raft-based consensus. Write is committed when
  a majority of nodes persist it. Automatic leader election on failure.

**Trade-off:** Strong durability guarantees, rich routing (exchanges, bindings),
but higher latency than Redis. Best for workflows requiring reliable delivery
and complex routing.

#### SQS (AWS Managed)

- **Visibility timeout:** After a consumer reads a message, it becomes
  invisible to other consumers for a configurable duration. If not deleted
  (acked) within the timeout, the message reappears.
- **Dead letter queue (DLQ):** Built-in. After N receive attempts, messages
  are automatically moved to a DLQ.
- **At-least-once delivery:** Messages may be delivered more than once.
  SQS FIFO queues add exactly-once delivery within a 5-minute dedup window.
- **No broker to manage.** Auto-scaling, pay-per-request.

**Trade-off:** Zero operational overhead, but higher per-message latency
(~10-50ms), limited to AWS ecosystem.

#### Kafka

- **Log-based architecture:** Messages are appended to partitioned,
  replicated logs. Consumers track their position via offsets.
- **Consumer groups:** Partitions are assigned to consumers in a group.
  Rebalancing on consumer failure.
- **Exactly-once semantics (EOS):** Kafka transactions allow producing
  and committing consumer offsets atomically.
- **Message replay:** Consumers can seek to any offset and re-read.

**Trade-off:** Highest throughput, built-in replay, but complex operational
model. Best for event streaming with task queue as a secondary use case.

### Worker Pool Architecture

Workers are typically long-running processes with:
- **Prefetch count:** Number of tasks fetched ahead of execution (amortizes
  network round-trips, but increases risk of lost work on crash).
- **Concurrency model:** Processes (Celery default), threads, or async
  (gevent). Process-based isolation prevents GIL contention and provides
  memory isolation.
- **Heartbeat:** Workers send periodic heartbeats to the broker. Missing
  heartbeats trigger task reassignment.
- **Graceful shutdown:** On SIGTERM, stop accepting new tasks, finish
  current in-flight tasks, ack, then exit. On SIGKILL, no cleanup possible.

### Result Backend

Stores task results for retrieval by the producer or other consumers:
- **Redis:** Fast but volatile. Results expire after a TTL.
- **Database (PostgreSQL/MySQL):** Durable, queryable, but slower writes.
- **S3 / object store:** For large results (generated files, ML model outputs).
- **No backend:** Fire-and-forget tasks that don't need result retrieval.
"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## Data Flow & Key Components

### Happy Path

```
1. Producer creates task with UUID, serializes payload
2. Producer sends to broker (with publisher confirm if RabbitMQ)
3. Broker persists task to queue
4. Worker dequeues task (BRPOPLPUSH for Redis, basic.get for RabbitMQ)
5. Worker executes task logic
6. Worker writes result to result backend
7. Worker sends ack to broker
8. Broker removes task from queue
```

### Failure Scenario 1: Worker Crash During Execution

**Setup:** Worker dequeues task, begins processing, then crashes (OOM, SIGKILL,
hardware failure).

**Chain of events:**
1. Worker receives task, starts execution
2. Worker writes partial side-effects (e.g., inserts row, sends email)
3. Worker process killed -- no `finally` block, no `atexit`, no ack
4. Broker's visibility timeout expires (SQS: 30s default; Celery: `acks_late`
   + `visibility_timeout`)
5. Broker marks task as unacknowledged and redelivers to another worker
6. New worker picks up same task
7. **Problem:** Partial side-effects from step 2 already exist

**Solution:** Idempotent execution (see Scenario 2).

### Failure Scenario 2: Implementing Idempotency

**The idempotency toolkit:**

1. **Idempotency key per task (UUID):**
   Every task gets a unique ID at creation. Before executing, check if this
   ID has already been processed:
   ```
   IF NOT EXISTS (SELECT 1 FROM processed_tasks WHERE task_id = ?) THEN
       execute_task()
       INSERT INTO processed_tasks (task_id, result, completed_at)
   END
   ```

2. **Database unique constraints as natural idempotency:**
   If the task's effect is "insert order #12345," a unique constraint on
   order_id prevents duplicates even without an explicit dedup check.

3. **Conditional writes (optimistic locking):**
   ```
   UPDATE accounts SET balance = balance - 100
   WHERE id = ? AND version = ?
   ```
   If the version changed (another execution already ran), the update
   affects 0 rows and the duplicate is safely ignored.

4. **Compare-and-swap (CAS):**
   Atomic read-modify-write. The write succeeds only if the current value
   matches the expected value. DynamoDB conditional expressions, Cassandra
   lightweight transactions.

5. **Outbox pattern for multi-system consistency:**
   When a task must update a database AND send a message (e.g., update order
   status + notify user), write both the DB update and the outgoing message
   to the same database transaction. A separate relay process reads the
   outbox table and publishes messages, retrying on failure.

### Failure Scenario 3: Timeout + Dual Execution

**Setup:** Worker A takes a task but becomes slow (GC pause, network partition,
CPU starvation).

**Chain of events:**
1. Worker A dequeues task, begins processing
2. Worker A becomes slow (full GC, network partition)
3. Broker's visibility timeout expires
4. Broker assigns task to Worker B
5. Worker A recovers and finishes its execution
6. **Both A and B have now executed the same task**

**Race conditions:**
- Whose ack is valid? Worker A's ack references a task the broker already
  reassigned.
- If both workers write to the same database row, last-write-wins causes
  data corruption.

**Solution: Fencing tokens (lease IDs)**

Each task assignment includes a monotonically increasing fencing token:
```
Assignment 1: task_id=T1, fence=42 -> Worker A
Assignment 2: task_id=T1, fence=43 -> Worker B (after timeout)
```

When writing results, the worker includes its fencing token. The result
backend only accepts writes with fence >= current fence:
```
UPDATE results SET value = ?, fence = 43
WHERE task_id = 'T1' AND fence < 43
```

Worker A's write with fence=42 is rejected. Worker B's write with fence=43
succeeds.

### Failure Scenario 4: Task Succeeds but Ack Lost

**Setup:** Worker completes task, sends ack, but the ack is lost in transit
(network drop, broker timeout).

**Chain of events:**
1. Worker executes task successfully
2. Worker sends ack to broker
3. Network drops the ack packet
4. Broker never receives ack, treats task as failed
5. Broker redelivers task to another worker

**Impact:** Identical to Scenario 1 from the idempotency perspective. The task
will be executed again. Without idempotent consumers, side-effects are doubled.

**Key insight:** This scenario demonstrates why **at-least-once delivery is
the fundamental guarantee** of any distributed queue. Even with a perfectly
reliable broker and worker, network partitions between them create duplicates.

### Failure Scenario 5: Poison Pill (Permanently Failing Task)

**Setup:** A task with invalid parameters, a logic bug, or a missing
dependency fails every time it executes.

**Chain of events:**
1. Worker dequeues task, executes, fails (exception)
2. Worker nacks task (or lets visibility timeout expire)
3. Broker redelivers task
4. Another worker picks up, fails again
5. Repeat forever -- poison pill consumes worker capacity

**Solution stack:**
1. **Max retry count:** After N failures, stop retrying. Celery:
   `max_retries=3`. SQS: `maxReceiveCount`.
2. **Dead letter queue (DLQ):** Move permanently-failed tasks to a separate
   queue for manual inspection. SQS has built-in DLQ support.
3. **Exponential backoff with jitter:** Space out retries to avoid thundering
   herd. Formula: `delay = min(base * 2^attempt + random(0, jitter), max_delay)`
4. **Error classification:**
   - **Transient:** Timeout, connection reset, 503 -> retry with backoff
   - **Permanent:** 400, validation error, missing resource -> DLQ immediately
5. **DLQ monitoring:** Alert when DLQ depth exceeds threshold. Dashboard for
   manual replay after root cause is fixed.

### Failure Scenario 6: Rolling Deployment

**Setup:** A deployment rolls out new worker code while old workers are still
running.

**Problems:**
1. **Serialization mismatch:** New task format includes fields old workers
   don't know. Old workers crash on deserialization.
2. **Behavior change:** Same task executed differently by v1 vs v2 workers.
3. **In-flight tasks:** v1 workers have tasks mid-execution when they're
   told to shut down.

**Solution: Graceful drain**
1. Send SIGTERM to old workers
2. Workers stop accepting new tasks (`consumer.cancel()`)
3. Workers finish current in-flight tasks
4. Workers ack completed tasks
5. Workers exit
6. New workers start with new code

**Serialization compatibility:** Use backward-compatible serialization
(add fields, don't remove/rename). Version the task schema. Workers skip
unknown fields.

### Failure Scenario 7: Empty / Malformed Payload

**Setup:** A bug in the producer or a manual API call submits an empty or
malformed task payload.

**Chain of events without validation:**
1. Empty payload enters the queue
2. Worker dequeues, attempts to parse, fails
3. Task nacked, retried, fails again
4. Becomes a poison pill (Scenario 5)

**Solution: Validate at enqueue time**
- Schema validation at the API gateway / producer
- Reject invalid payloads before they enter the queue
- For late-bound validation (task type unknown at enqueue), validate
  immediately after dequeue and DLQ if invalid -- do NOT retry
"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## Formulas & Algorithms

### Exponential Backoff with Jitter

The standard retry delay formula prevents thundering herd:

$$\text{delay} = \min\left(\text{base} \times 2^{\text{attempt}} + \text{random}(0, \text{jitter}), \text{max\_delay}\right)$$

**Parameters:**
| Parameter | Typical Value | Purpose |
|-----------|--------------|---------|
| `base` | 1s | Initial delay |
| `attempt` | 0, 1, 2, ... | Retry count |
| `jitter` | 0 to base | Decorrelates concurrent retries |
| `max_delay` | 300s (5 min) | Cap to prevent unbounded waits |

**Example progression (base=1s, jitter=0-1s):**
| Attempt | Formula | Range |
|---------|---------|-------|
| 0 | 1 * 2^0 + jitter | 1-2s |
| 1 | 1 * 2^1 + jitter | 2-3s |
| 2 | 1 * 2^2 + jitter | 4-5s |
| 3 | 1 * 2^3 + jitter | 8-9s |
| 4 | 1 * 2^4 + jitter | 16-17s |

**Jitter strategies:**
- **Full jitter:** `random(0, base * 2^attempt)` -- widest spread
- **Equal jitter:** `base * 2^attempt / 2 + random(0, base * 2^attempt / 2)`
- **Decorrelated jitter:** `min(max_delay, random(base, prev_delay * 3))`

AWS recommends decorrelated jitter for best performance under contention.

### Visibility Timeout Calculation

The visibility timeout must exceed the expected task execution time:

$$\text{visibility\_timeout} = \text{p99\_execution\_time} \times \text{safety\_factor}$$

**Safety factor guidelines:**
| Workload | p99 | Safety Factor | Timeout |
|----------|-----|---------------|---------|
| Fast (API call) | 2s | 3x | 6s |
| Medium (image resize) | 30s | 2x | 60s |
| Slow (ML inference) | 300s | 2x | 600s |
| Variable (scraping) | varies | use heartbeat instead | -- |

**Problem with fixed timeouts:** If the distribution has a long tail (p99 = 30s
but p99.9 = 300s), a 60s timeout causes premature redelivery for 0.1% of tasks.

**Alternative: heartbeat-based extension**
Worker sends periodic heartbeats to extend the visibility timeout:
```
Every heartbeat_interval (e.g., 15s):
    broker.extend_timeout(task_id, extension=30s)
```
SQS: `ChangeMessageVisibility`. RabbitMQ: consumer heartbeat.

### Circuit Breaker for Downstream Dependencies

When a task calls an external service that is down, retrying wastes resources.

**States:**
- **Closed (normal):** Requests pass through. Track failure rate.
- **Open (tripped):** All requests fail immediately. No calls to downstream.
- **Half-open (probe):** After cooldown, allow one request. If it succeeds,
  close. If it fails, re-open.

**Thresholds:**
$$\text{trip when } \frac{\text{failures}}{\text{total}} > \text{error\_rate\_threshold} \text{ within window}$$

Typical values: error_rate_threshold=0.5, window=60s, cooldown=30s.

### Dead Letter Criteria

A task should be routed to the DLQ when ANY of:

$$\text{retry\_count} > \text{max\_retries}$$
$$\text{age} > \text{max\_task\_age}$$
$$\text{error\_type} \in \{\text{permanent errors}\}$$

**Error type classification heuristic:**
| Error Category | Examples | Action |
|---------------|----------|--------|
| Transient | Timeout, 503, connection reset | Retry with backoff |
| Permanent | 400, 404, validation error | DLQ immediately |
| Unknown | Unhandled exception | Retry up to max, then DLQ |

### Queue Depth and Worker Scaling

**Autoscaling formula:**
$$\text{desired\_workers} = \left\lceil \frac{\text{queue\_depth}}{\text{target\_latency} \times \text{throughput\_per\_worker}} \right\rceil$$

Example: 10,000 pending tasks, target drain in 60s, each worker processes
5 tasks/sec:
$$\text{desired\_workers} = \left\lceil \frac{10000}{60 \times 5} \right\rceil = 34$$
"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## Production Constraints

### Throughput by Broker

| Broker | Throughput (msg/sec) | Notes |
|--------|---------------------|-------|
| **Redis** | 100K-500K | In-memory, limited by network/serialization |
| **RabbitMQ** | 20K-50K | Persistent messages reduce to ~5K-10K |
| **SQS Standard** | ~3,000 per API call | Batch: 10 msgs/call, effectively unlimited with multiple callers |
| **SQS FIFO** | 300 msg/sec per group | 3,000/sec with batching + multiple message groups |
| **Kafka** | 100K-2M | Per partition; scales linearly with partitions |

### Latency Budget

| Metric | Redis | RabbitMQ | SQS | Kafka |
|--------|-------|----------|-----|-------|
| **Enqueue** | <1ms | 1-5ms | 10-50ms | 2-10ms |
| **Dequeue** | <1ms | 1-5ms | 20-100ms (long poll) | 1-5ms |
| **End-to-end (enqueue-to-start)** | 1-5ms | 5-20ms | 50-200ms | 5-20ms |

### Durability Guarantees

| Broker | Durability | Data Loss Window |
|--------|-----------|------------------|
| Redis RDB | Periodic snapshot | Up to 60s of data |
| Redis AOF (everysec) | Append-only log | Up to 1s |
| Redis AOF (always) | Every write fsynced | None (but 10x slower) |
| RabbitMQ persistent | Durable queue + persistent msg | None after confirm |
| RabbitMQ quorum | Raft consensus | None after majority ack |
| SQS | Managed, multi-AZ | None (AWS SLA) |
| Kafka (acks=all) | ISR replication | None after ack |

### Memory and Storage

**Redis:** All queues in memory. 1M tasks with 1KB payload = ~1GB RAM.
If tasks accumulate (consumers slower than producers), Redis OOM is a
production risk. Mitigate: `maxmemory-policy noeviction` + alerting on
memory usage.

**RabbitMQ:** Messages on disk when persistent, but paged into memory for
delivery. High queue depth (>1M messages) degrades performance. Enable
`lazy` queues for predictable memory usage at cost of throughput.

**Kafka:** Log segments on disk. Retention policy (time or size) controls
storage. 1TB retention with 100MB/s ingress = ~2.8 hours of data. Tiered
storage offloads cold segments to object storage.

**DLQ storage:** Dead letter queues grow unboundedly if not monitored. Set
retention policies: SQS max retention = 14 days. Alert on DLQ depth > 0.

### Operational Considerations

**Monitoring metrics (the minimum set):**
- Queue depth (messages waiting)
- Consumer lag (Kafka: offset lag per consumer group)
- Processing rate (tasks/sec completed)
- Error rate (tasks/sec failed)
- DLQ depth
- Worker count and utilization
- p50/p95/p99 task execution time

**Alerting thresholds:**
| Metric | Warning | Critical |
|--------|---------|----------|
| Queue depth | >10K (growing) | >100K |
| Consumer lag | >1 min | >10 min |
| DLQ depth | >0 | >100 |
| Error rate | >1% | >5% |
| Worker utilization | >80% | >95% |
"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## Trade-off Analysis

### Delivery Semantics: The Fundamental Trade-off

There are three delivery semantics. You can implement any one, but each has
costs:

| Semantic | Guarantee | Trade-off |
|----------|-----------|-----------|
| **At-most-once** | Task delivered 0 or 1 times | Message loss possible. No retries. |
| **At-least-once** | Task delivered 1+ times | Duplicates possible. Must handle idempotently. |
| **Exactly-once** | Task delivered exactly 1 time | Requires transactional coordination. Expensive. |

**Industry consensus:** At-least-once + idempotent consumer is the standard
choice. True exactly-once is achievable only within a single system boundary
(Kafka transactions), not across system boundaries (queue + external DB +
email service).

### Message Loss vs. Message Duplication

| Favor | When | Example |
|-------|------|---------|
| **Tolerate loss** | Idempotent re-execution is expensive or impossible | Analytics event ingestion (lossy is OK) |
| **Tolerate duplication** | Idempotent re-execution is cheap | Payment processing (dedup by transaction ID) |

**Business-level compensation:** When duplicates of irreversible actions occur
(two emails sent, two charges made), the system needs a compensation mechanism:
refund the duplicate charge, include "ignore if duplicate" language, or dedup
downstream.

### Broker Durability vs. Throughput

```
                 Throughput
                    ^
                    |
    Redis RDB ------X  (500K msg/s, data loss risk)
                    |
    Redis AOF ------X  (100K msg/s, 1s loss window)
                    |
    Kafka acks=1 ---X  (200K msg/s, leader-only)
                    |
    RabbitMQ -------X  (20K msg/s, durable)
                    |
    Kafka acks=all -X  (50K msg/s, ISR replicated)
                    |
                    +-------------------------> Durability
```

**Decision framework:** Start with the business question: "What is the cost
of losing one task?" If the cost is negligible (log aggregation), use Redis
RDB. If the cost is high (payment processing), use RabbitMQ durable or Kafka
with acks=all.

### Synchronous vs. Asynchronous Acknowledgment

| Mode | Behavior | Use When |
|------|----------|----------|
| **Sync ack (ack after processing)** | Worker acks only after task completes | Task is idempotent but expensive to re-execute |
| **Async ack (ack before processing)** | Worker acks immediately on receive | Task is cheap and idempotent, throughput is critical |

**Sync ack risk:** If processing takes too long, the broker may time out and
redeliver -- causing the dual execution scenario (S3).

**Async ack risk:** If the worker crashes after acking but before completing,
the task is lost (at-most-once).

### Push vs. Pull Consumer Models

| Model | How It Works | Pros | Cons |
|-------|-------------|------|------|
| **Push** | Broker sends messages to consumers | Low latency, real-time | Consumer overwhelm, backpressure needed |
| **Pull** | Consumer polls broker for messages | Consumer controls pace | Higher latency, polling overhead |

- **RabbitMQ:** Push-based (broker pushes to consumer via channel).
  Prefetch count provides backpressure.
- **Kafka:** Pull-based (consumer fetches from partitions at its own pace).
  Long polling reduces latency.
- **SQS:** Pull-based (ReceiveMessage API). Long polling (WaitTimeSeconds=20)
  reduces empty responses.

### Task Priority and Fairness

**Multiple priority queues:** Separate high/medium/low priority queues.
Workers drain high-priority first. Risk: low-priority starvation.

**Weighted fair queuing:** Workers alternate between queues with weights
(e.g., 70% high, 20% medium, 10% low). Prevents starvation while
prioritizing important work.

### Exactly-Once: What It Actually Means

"Exactly-once" in distributed systems is misleading. What you can achieve:

1. **Exactly-once delivery within Kafka:** Using Kafka transactions, a
   consumer can atomically commit its offset and produce output messages.
   But this only works within the Kafka boundary.

2. **Effectively-once processing:** At-least-once delivery + idempotent
   consumer. The task may be delivered multiple times, but the side-effect
   happens only once because the consumer detects and skips duplicates.

3. **True exactly-once across system boundaries:** Requires the transactional
   outbox pattern:
   - Write task result + outbox entry in a single DB transaction
   - Outbox relay publishes the outbox entry to the message broker
   - Downstream consumer is also idempotent
   - End-to-end: each side-effect happens exactly once

**Interview insight:** If asked "how do you achieve exactly-once?", the
strong answer is: "We don't achieve true exactly-once across systems. We
implement at-least-once delivery with idempotent consumers, which gives us
effectively-once processing. For cross-system consistency, we use the
transactional outbox pattern."
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## Adversarial Defense Q&A

### Q: Worker crashes during execution. Walk through the full recovery chain.

**Complete answer:**

1. Worker receives task T1 from broker, begins processing
2. Worker crashes (OOM, SIGKILL) -- no cleanup, no ack sent
3. Broker's visibility timeout expires (default 30s for SQS, configurable)
4. Broker marks T1 as unacknowledged
5. Broker redelivers T1 to the next available worker
6. New worker picks up T1
7. Worker checks idempotency: `SELECT 1 FROM processed_tasks WHERE task_id = T1`
8. **If found:** Task already completed in previous partial execution. Skip.
   Ack immediately.
9. **If not found:** Execute normally. On success, atomically:
   (a) perform side-effect, (b) insert into processed_tasks, (c) ack broker
10. Result stored in result backend

**Key nuance:** Step 7 only catches completed tasks. If the previous execution
wrote partial side-effects (e.g., inserted 50 of 100 rows), the idempotency
check passes and the task re-executes. The task logic itself must be idempotent:
use `INSERT ... ON CONFLICT DO NOTHING`, `UPDATE ... WHERE version = expected`,
or batch the entire operation in a transaction.

### Q: Broker restarts. What happens to in-flight tasks?

**Answer by broker type:**

| Broker | In-Flight Task Fate |
|--------|-------------------|
| **Redis RDB** | Lost. Tasks enqueued since last snapshot are gone. Recovery: re-enqueue from source of truth (database job table). |
| **Redis AOF (everysec)** | Up to 1 second of tasks lost. Tasks persisted before the last fsync survive. |
| **Redis AOF (always)** | No loss. Every enqueue is fsynced. But throughput drops 10x. |
| **RabbitMQ (durable + persistent)** | Survives. Queue metadata and message bodies are on disk. Messages in transit (delivered but unacked) are redelivered after restart. |
| **RabbitMQ (quorum queue)** | Survives as long as majority of nodes are up. Leader election happens automatically. |
| **SQS** | Survives. Managed service, multi-AZ replication. AWS SLA: 99.999999999% durability. |
| **Kafka (acks=all)** | Survives. Replicated to ISR (in-sync replicas). Leader election from ISR. |

**Follow-up: What about tasks that were mid-execution when the broker died?**
Workers holding unacked tasks will detect the broker disconnect. Behavior
depends on client library:
- Celery + Redis: task stays in unacked list, reclaimed on reconnect
- Celery + RabbitMQ: channel closes, task is redelivered by broker after restart
- Kafka consumer: offset not committed, task re-consumed on rebalance

### Q: Same task executed by two workers simultaneously. Side effects may be irreversible.

**Setup:** Worker A is slow (GC pause), broker reassigns to Worker B. Both execute.

**Defense in depth (layered solutions):**

1. **Fencing tokens:** Each assignment has a monotonic token. Worker must
   present its token when writing. Backend rejects stale tokens.
   ```
   Worker A: fence=42, writes result -> accepted (fence=42 is current)
   Worker B: fence=43, writes result -> accepted (fence=43 > 42, overwrites)
   Worker A: tries second write -> rejected (fence=42 < current 43)
   ```

2. **Distributed lock with TTL:** Worker acquires a lock (Redis SETNX,
   ZooKeeper ephemeral node) before executing. Lock has TTL > expected
   execution time. Second worker fails to acquire lock.
   **Risk:** If TTL < actual execution time, lock expires and both execute.

3. **Idempotent operations:** If the side-effect is naturally idempotent
   (SET key=value, not INCREMENT counter), dual execution is safe.

4. **Compensating transactions:** For irreversible actions (sent email,
   charged credit card):
   - **Reservation pattern:** Before charging, create a reservation
     (hold on funds). Only one reservation per order ID (idempotent).
     Finalize the reservation in a separate step.
   - **Downstream dedup:** Email service deduplicates by message ID.
     Payment processor deduplicates by transaction ID.
   - **Accept and compensate:** Charge goes through twice. Detect via
     reconciliation job. Issue automatic refund.

### Q: Task succeeds but ack is lost.

**Answer:**

This is functionally identical to a worker crash from the broker's perspective.
The broker has no way to distinguish "worker completed but ack was lost" from
"worker died."

**Recovery chain:** Same as crash recovery (Scenario 1). Broker redelivers.
Consumer's idempotency check prevents duplicate side-effects.

**Why this matters:** It proves that **at-least-once is the strongest delivery
guarantee achievable without consensus between broker and consumer.** Even with
a perfectly reliable worker and broker, the network between them is unreliable.
Therefore, idempotent consumers are not optional -- they are a fundamental
requirement.

### Q: Poison pill enters the queue and fails repeatedly.

**Answer:**

**Detection strategy:**
1. Track retry count per message (SQS: `ApproximateReceiveCount`, RabbitMQ:
   `x-death` header, Celery: `task.request.retries`)
2. After N retries, route to DLQ
3. Alert on DLQ depth > 0

**Error classification:**
- **Retriable (transient):** Connection timeout, 503, rate limit (429).
  Retry with exponential backoff.
- **Permanent:** Validation error (400), resource not found (404), logic bug.
  Route to DLQ immediately -- retrying will never succeed.
- **Unknown:** Unhandled exception. Retry up to max_retries, then DLQ.

**DLQ operations:**
- **Inspect:** Read messages from DLQ, examine error details
- **Fix and replay:** After fixing root cause, move messages back to main queue
- **Purge:** Delete messages that are no longer relevant
- **Monitoring:** Dashboard showing DLQ depth, message age, error distribution

**Production pattern:**
```
try:
    execute_task(payload)
except PermanentError:
    route_to_dlq(reason="permanent")
    ack()  # Remove from main queue
except TransientError:
    if retry_count < max_retries:
        nack(requeue=True, delay=backoff(retry_count))
    else:
        route_to_dlq(reason="max_retries_exceeded")
        ack()
```

### Q: Empty payload submitted.

**Answer:**

**Validation layering:**
1. **Producer-side (gateway):** Schema validation before enqueue. Reject
   with 400 and error details. This is the cheapest place to catch bad input.
2. **Consumer-side (worker):** Validate immediately after dequeue, before
   any processing. If invalid, route to DLQ (not retry queue -- retrying
   an empty payload will always fail).
3. **Contract enforcement:** Define a schema (JSON Schema, protobuf, Avro)
   for task payloads. Both producer and consumer validate against it.

**Key distinction:** Validation errors are **permanent failures**. They
should never be retried. Route directly to DLQ with error classification
"validation_error."

### Q: How do you achieve exactly-once execution?

**Strong interview answer:**

"You don't achieve true exactly-once execution across distributed system
boundaries. Here is what you actually do:

1. **At-least-once delivery:** Configure the broker to redeliver on timeout
   or nack. This guarantees the task is not lost, but may be delivered
   multiple times.

2. **Idempotent consumer:** Design the task execution to be safe for
   re-execution. Techniques: idempotency keys, database unique constraints,
   conditional writes, compare-and-swap.

3. **Result:** At-least-once delivery + idempotent execution = effectively-
   once processing. The task may be delivered and executed multiple times,
   but the observable side-effect happens exactly once.

4. **For cross-system consistency:** Use the transactional outbox pattern.
   Write the side-effect and outgoing message in a single DB transaction.
   A relay process publishes the outbox entry. Downstream consumers are
   also idempotent. This gives you effectively-once across system boundaries.

True exactly-once within a single system is possible (Kafka transactions
commit consumer offset + producer messages atomically), but the moment you
cross a system boundary (write to a database AND send an email), you need
the outbox pattern + idempotent consumers."

### Q: Two workers execute same task, one does irreversible action (sent email, charged card). How to handle?

**Answer:**

**Prevention (before it happens):**
1. **Fencing tokens:** Second worker's write is rejected by backend
2. **Distributed lock:** Second worker cannot acquire lock, skips execution
3. **Reservation pattern:** `create_reservation(order_id)` is idempotent.
   Only one reservation exists. Charge happens in a separate
   `finalize_reservation` step that checks reservation ownership.

**Detection (after it happens):**
1. **Reconciliation job:** Periodic job compares expected state (one charge
   per order) with actual state (payment provider records). Flags anomalies.
2. **Idempotency at the external service:** Many payment APIs accept a
   client-generated idempotency key. Two charges with the same key result
   in one actual charge.

**Compensation (undo the damage):**
1. **Refund:** Automatic refund for the duplicate charge
2. **Email dedup:** Downstream email service deduplicates by message ID.
   Or accept the duplicate and add "if you received this email twice,
   please disregard."
3. **Business-level acceptance:** Some domains accept a low duplicate rate
   (e.g., analytics events) because the cost of prevention exceeds the
   cost of duplicates.

### Q: How do you discover a task that will never succeed?

**Answer:**

1. **Retry count monitoring:** Track `retry_count` per task. Alert on tasks
   exceeding p99 retry count (most tasks succeed in 0-1 retries; a task
   at retry 5 is suspicious).

2. **Error type classification:** Classify errors as transient vs permanent
   at the point of failure. Permanent errors bypass retry entirely.

3. **DLQ routing:** After max_retries, task moves to DLQ. DLQ depth > 0
   triggers an alert.

4. **Task age monitoring:** If a task has been in the system longer than
   max_task_age (e.g., 24 hours), it is likely stuck. Alert and investigate.

5. **Anomaly detection on retry distributions:** Normal: 95% of tasks
   complete on first attempt, 4% on retry 1, 0.9% on retry 2. If retry 3+
   suddenly increases, something systemic changed (deployment bug, downstream
   outage).

6. **Circuit breaker integration:** If a downstream dependency is down,
   circuit breaker opens and all tasks targeting that dependency fail fast
   with a clear "circuit open" error. This prevents retries from masking
   the root cause.
"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## Verbal Outline

### 3-Minute Version

"A distributed task queue decouples work submission from execution. The core
architecture has four actors: producer, broker, worker pool, and result
backend.

The critical insight is that **every component can fail independently**, and
the system must handle each failure mode:

**The most important failure:** Worker crashes mid-execution. The task has
already produced partial side-effects. The broker's visibility timeout
expires and redelivers the task. Without idempotent consumers, you get
duplicate side-effects -- double charges, duplicate emails.

**The solution:** At-least-once delivery plus idempotent consumers equals
effectively-once processing. You implement idempotency through UUID-based
dedup keys, database unique constraints, and conditional writes.

**Why not true exactly-once?** Because the network between the worker and
broker is unreliable. Even if the task succeeds, the ack can be lost. The
broker redelivers. So idempotency is not optional -- it is a fundamental
requirement of any distributed task queue."

### 10-Minute Version

**Minutes 0-2: Architecture and Happy Path**

"Let me start with the architecture. We have producers -- API servers or
schedulers -- that enqueue tasks to a broker. The broker durably stores
tasks until workers dequeue and execute them. After execution, workers
acknowledge completion and optionally store results.

For broker selection: Redis offers sub-millisecond latency but weaker
durability (RDB snapshots lose data between saves). RabbitMQ provides
strong durability with persistent messages and publisher confirms, plus
Raft-based quorum queues for HA. SQS is fully managed with built-in DLQ
support. Kafka gives the highest throughput with log-based architecture
and replay capability.

The happy path is: enqueue, dequeue, execute, ack, done. Now let me walk
through what happens when things go wrong."

**Minutes 2-5: Three Critical Failure Scenarios**

"**Scenario 1: Worker crash.** The worker receives a task, starts processing,
and crashes -- OOM kill, hardware failure. No cleanup code runs. The broker's
visibility timeout expires and redelivers the task. But the crashed worker
may have already committed partial side-effects: inserted half the rows,
sent one of two emails. The new worker must handle re-execution safely.

This is why we need idempotent consumers. Every task gets a UUID. Before
executing, the worker checks: has this task ID been processed? If yes,
skip. If no, execute and record completion atomically.

**Scenario 2: Dual execution.** Worker A takes a task but becomes slow --
full GC pause, network partition. The broker times out and gives the task
to Worker B. Worker A recovers. Now both execute simultaneously.

The fix is fencing tokens. Each task assignment carries a monotonically
increasing token. When writing results, the worker includes its token.
The backend only accepts writes with the highest token, rejecting stale
writes from Worker A.

**Scenario 3: Poison pill.** A task with invalid parameters fails every
time. Without safeguards, it retries forever, consuming worker capacity.
The fix: max retry count, exponential backoff with jitter, and dead letter
queue routing. Classify errors as transient (retry) or permanent (DLQ
immediately). Monitor DLQ depth."

**Minutes 5-8: Exactly-Once Methodology and Trade-offs**

"The key insight for interviews: true exactly-once execution across
distributed system boundaries is not achievable. What we implement is
at-least-once delivery plus idempotent consumers, which gives us
effectively-once processing.

Within a single system like Kafka, exactly-once semantics are possible --
Kafka transactions atomically commit consumer offsets and producer messages.
But the moment you cross a system boundary -- write to a database AND send
a notification -- you need the transactional outbox pattern.

The outbox pattern: write the database update and an outbox entry in a
single transaction. A relay process reads the outbox and publishes to the
message broker. The downstream consumer is also idempotent. This gives
end-to-end effectively-once across systems.

On the trade-off spectrum: at-most-once is cheapest but loses messages.
At-least-once with idempotency is the industry standard. The broker
durability vs throughput trade-off depends on business cost of losing a
task: negligible cost (analytics) -> Redis RDB. High cost (payments) ->
RabbitMQ durable or Kafka acks=all."

**Minutes 8-10: Production Considerations**

"In production, the minimum monitoring set is: queue depth, consumer lag,
processing rate, error rate, DLQ depth, and p95/p99 task execution time.
Alert on queue depth growing (producers outpacing consumers), DLQ depth
above zero (something is failing), and error rate above 1%.

For rolling deployments: graceful shutdown is essential. Send SIGTERM,
workers stop accepting new tasks, finish in-flight work, ack, and exit.
Use backward-compatible serialization so v1 and v2 workers can coexist
during the deploy window.

For scaling: autoscale workers based on queue depth. Formula: desired
workers = queue depth / (target latency * throughput per worker). Set
min/max bounds to prevent over-provisioning."
"""


# ---------------------------------------------------------------------------
# Main: populate the database record
# ---------------------------------------------------------------------------


def populate_distributed_task_queue() -> None:
    """Find the distributed-task-queue SystemDesign record and update all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == "distributed-task-queue")
            .first()
        )

        if record is None:
            print("[FAIL] No SystemDesign record with slug='distributed-task-queue' found.")
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
        print("[DONE] Updated all 8 sections for distributed-task-queue.")

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
    populate_distributed_task_queue()
