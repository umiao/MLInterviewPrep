"""Populate distributed-task-queue system design module with all 8 sections.

Usage:
    python scripts/content_distributed_task_queue.py

Covers failure modes, idempotency, exactly-once semantics, broker comparison.
Idempotent: overwrites existing content for the distributed-task-queue slug.

Source of truth: Chinese content. All sections in Chinese with English terms.
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

### 什么是分布式任务队列？ (What Is a Distributed Task Queue?)

分布式任务队列将**工作提交**与**工作执行**解耦。
其核心契约包含四个角色：

| 角色 | 职责 |
|------|------|
| **Producer** (生产者) | 提交任务（API 服务器、调度器、Webhook 处理器） |
| **Broker** (消息代理) | 持久化存储待处理任务的队列（Redis、RabbitMQ、SQS、Kafka） |
| **Worker** (工作进程) | 出队、执行并确认任务完成 |
| **Result Backend** (结果后端) | 存储执行结果（数据库、Redis、S3） |

### 为什么"发送即忘"在生产环境中会失败？ (Why "Fire and Forget" Breaks in Production)

天真的方案——入队并假设任务完成——会失败，原因如下：

1. **Worker 崩溃。** **OOM (Out of Memory)** kill、硬件故障和 SIGKILL 会使任务处于半执行状态，没有清理机会。
2. **网络分区。** 即使任务成功完成，确认消息也可能丢失，导致 Broker 重新投递。
3. **Broker 重启。** 内存队列（Redis RDB）在快照间隔内会丢失未确认的任务。
4. **任务毒害队列。** 永久失败的任务会无限重试，消耗 Worker 容量，饿死健康任务。
5. **部署引入版本偏差。** 滚动部署意味着旧版本和新版本的 Worker 共存，产生序列化不匹配。

### 这个模块为什么对面试重要？ (Why This Module Matters for Interviews)

分布式任务队列几乎出现在每个涉及异步处理的系统设计面试中：邮件投递、支付处理、图片缩放、ML 推理管道、通知扇出。面试官测试的不是你是否了解 Celery 的 API——他们想听你**推理故障模式**并**清晰表述恢复策略**。

关键洞察：**可靠性不是 Broker 的功能——它是 Producer、Broker、Worker 和 Consumer 在故障条件下交互方式的涌现属性。** 一个"可靠的" Broker（带有持久队列的 RabbitMQ）在 ack 丢失时仍然会产生重复。一个"不可靠的" Broker（带 RDB 的 Redis）如果消费者是幂等的且系统容忍重新处理，也可以做到安全。

### 核心问题 (The Central Question)

> "在任何组件随时都可能失败的分布式系统中，如何确保每个任务**恰好执行一次**？"

答案是：你做不到。你实现的是**至少一次投递 (at-least-once delivery)**，配合**幂等消费者 (idempotent consumers)**，从而达成**有效一次处理 (effectively-once processing)**。
本模块将逐一讲解驱动这一设计的每个故障场景。"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## 架构深入分析 (Architecture Deep Dive)

### 核心组件 (Core Components)

```
Producer ──enqueue──> Broker ──dequeue──> Worker Pool
                        |                    |
                        |                    ├── execute task
                        |                    ├── write to DB / external system
                        |                    └── ack back to broker
                        |
                   Result Backend <── result stored
```

### Broker 选型 (Broker Options)

#### Redis（Celery 默认）

**持久化模式：**
- **RDB (snapshotting，快照)：** 定期将数据转储到磁盘。快照间隔内入队的任务在崩溃时会丢失。默认：当 1000+ 个 key 发生变更时每 60 秒转储一次。
- **AOF (Append-Only File，追加写日志)：** 记录每次写操作。`fsync` 策略决定持久性：
  - `always`：每次写操作后 fsync（最安全，最慢）
  - `everysec`：每秒 fsync 一次（1 秒数据丢失窗口）
  - `no`：由操作系统决定（快速，最多 30 秒数据丢失）
- **没有原生确认机制。** Celery 通过 `BRPOPLPUSH` 到"未确认"列表来实现 ack。如果 Worker 死亡，任务留在未确认列表中，必须被回收（可见性超时模式）。

**权衡：** 超低延迟，但持久性需要仔细调优。最适合偶尔任务丢失可以接受或幂等重新执行成本低廉的工作负载。

#### RabbitMQ

**持久性栈：**
1. **持久队列 (Durable queue)：** 队列元数据在 Broker 重启后存活。
2. **持久消息 (Persistent messages)：** 消息写入磁盘（delivery_mode=2）。
3. **发布确认 (Publisher confirms)：** Broker 在持久化后向 Producer 回复确认。
4. **消费者确认 (Consumer acks)：** Worker 在处理完成后显式确认。

**高可用性：**
- **镜像队列（经典模式）：** 完整队列复制到 N 个节点。已弃用。
- **Quorum 队列（现代模式）：** 基于 **Raft** 共识算法。当大多数节点完成持久化后写入才被提交。故障时自动选主。

**权衡：** 强持久性保证，丰富的路由（交换器、绑定），但延迟高于 Redis。最适合需要可靠投递和复杂路由的工作流。

#### SQS（AWS 托管服务）

- **可见性超时 (Visibility timeout)：** 消费者读取消息后，该消息对其他消费者在可配置时长内不可见。如果在超时内未被删除（确认），消息会重新出现。
- **死信队列 (Dead Letter Queue, DLQ)：** 内置支持。在 N 次接收尝试后，消息自动移至 **DLQ (Dead Letter Queue)**。
- **至少一次投递 (At-least-once delivery)：** 消息可能被投递多次。SQS **FIFO (First In, First Out)** 队列在 5 分钟去重窗口内提供恰好一次投递。
- **无需管理 Broker。** 自动伸缩，按请求付费。

**权衡：** 零运维开销，但每条消息延迟较高（约 10-50ms），局限于 AWS 生态系统。

#### Kafka

- **基于日志的架构：** 消息追加到分区化、副本化的日志中。消费者通过偏移量追踪自身位置。
- **消费者组 (Consumer groups)：** 分区分配给组内的消费者。消费者故障时触发重平衡。
- **恰好一次语义 (Exactly-Once Semantics, EOS)：** Kafka 事务允许原子性地生产消息和提交消费者偏移量。
- **消息回放：** 消费者可以 seek 到任意偏移量并重新读取。

**权衡：** 最高吞吐量，内置回放能力，但运维模型复杂。最适合以事件流为主、任务队列为辅的场景。

### Worker 池架构 (Worker Pool Architecture)

Worker 通常是长运行进程，具有以下特征：
- **预取计数 (Prefetch count)：** 提前拉取的任务数量（分摊网络往返开销，但增加崩溃时丢失工作的风险）。
- **并发模型：** 进程（Celery 默认）、线程或异步（gevent）。基于进程的隔离避免 **GIL (Global Interpreter Lock)** 竞争并提供内存隔离。
- **心跳 (Heartbeat)：** Worker 定期向 Broker 发送心跳。缺失的心跳触发任务重新分配。
- **优雅关闭：** 收到 SIGTERM 时，停止接受新任务，完成当前正在执行的任务，发送 ack，然后退出。收到 SIGKILL 时，无法执行任何清理。

### 结果后端 (Result Backend)

存储任务结果以供 Producer 或其他消费者检索：
- **Redis：** 快速但易失。结果在 **TTL (Time To Live)** 之后过期。
- **数据库（PostgreSQL/MySQL）：** 持久、可查询，但写入较慢。
- **S3 / 对象存储：** 用于大型结果（生成的文件、ML 模型输出）。
- **无后端：** 不需要结果检索的即发即忘型任务。"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 正常路径 (Happy Path)

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

### 故障场景 1：Worker 在执行中崩溃 (Failure Scenario 1: Worker Crash During Execution)

**设定：** Worker 出队任务，开始处理，然后崩溃（OOM、SIGKILL、硬件故障）。

**事件链：**
1. Worker 接收任务，开始执行
2. Worker 写入了部分副作用（例如插入了行、发送了邮件）
3. Worker 进程被 kill——没有 `finally` 块，没有 `atexit`，没有 ack
4. Broker 的可见性超时到期（SQS 默认 30 秒；Celery：`acks_late` + `visibility_timeout`）
5. Broker 将任务标记为未确认并重新投递给另一个 Worker
6. 新 Worker 获取同一任务
7. **问题：** 步骤 2 中的部分副作用已经存在

**解决方案：** 幂等执行（见场景 2）。

### 故障场景 2：实现幂等性 (Failure Scenario 2: Implementing Idempotency)

**幂等性工具箱：**

1. **每个任务的幂等键（UUID）：**
   每个任务在创建时获得一个唯一 ID。执行前检查该 ID 是否已被处理：
   ```
   IF NOT EXISTS (SELECT 1 FROM processed_tasks WHERE task_id = ?) THEN
       execute_task()
       INSERT INTO processed_tasks (task_id, result, completed_at)
   END
   ```

2. **数据库唯一约束作为天然幂等性：**
   如果任务的效果是"插入订单 #12345"，order_id 上的唯一约束即使没有显式去重检查也能防止重复。

3. **条件写入（乐观锁）：**
   ```
   UPDATE accounts SET balance = balance - 100
   WHERE id = ? AND version = ?
   ```
   如果版本已改变（另一次执行已运行），更新影响 0 行，重复被安全忽略。

4. **比较并交换 (Compare-and-Swap, CAS)：**
   原子的读-改-写操作。只有当前值匹配期望值时写入才会成功。DynamoDB 条件表达式、Cassandra 轻量级事务。

5. **发件箱模式实现多系统一致性 (Outbox Pattern)：**
   当任务必须同时更新数据库并发送消息（例如更新订单状态 + 通知用户）时，将数据库更新和待发消息写入同一个数据库事务。一个单独的中继进程读取发件箱表并发布消息，失败时重试。

### 故障场景 3：超时 + 双重执行 (Failure Scenario 3: Timeout + Dual Execution)

**设定：** Worker A 获取了任务但变慢了（GC 暂停、网络分区、CPU 饥饿）。

**事件链：**
1. Worker A 出队任务，开始处理
2. Worker A 变慢（Full GC、网络分区）
3. Broker 的可见性超时到期
4. Broker 将任务分配给 Worker B
5. Worker A 恢复并完成执行
6. **A 和 B 现在都执行了同一任务**

**竞态条件：**
- 谁的 ack 有效？Worker A 的 ack 引用了一个 Broker 已经重新分配的任务。
- 如果两个 Worker 写入同一数据库行，最后写入者胜出会导致数据损坏。

**解决方案：防护令牌 (Fencing Tokens)（租约 ID）**

每次任务分配包含一个单调递增的防护令牌：
```
Assignment 1: task_id=T1, fence=42 -> Worker A
Assignment 2: task_id=T1, fence=43 -> Worker B (after timeout)
```

写入结果时，Worker 携带其防护令牌。结果后端仅接受 fence >= 当前 fence 的写入：
```
UPDATE results SET value = ?, fence = 43
WHERE task_id = 'T1' AND fence < 43
```

Worker A 的 fence=42 写入被拒绝。Worker B 的 fence=43 写入成功。

### 故障场景 4：任务成功但 Ack 丢失 (Failure Scenario 4: Task Succeeds but Ack Lost)

**设定：** Worker 完成任务、发送 ack，但 ack 在传输中丢失（网络丢包、Broker 超时）。

**事件链：**
1. Worker 成功执行任务
2. Worker 向 Broker 发送 ack
3. 网络丢弃了 ack 数据包
4. Broker 从未收到 ack，将任务视为失败
5. Broker 将任务重新投递给另一个 Worker

**影响：** 从幂等性角度看，与场景 1 完全相同。任务会被再次执行。如果没有幂等消费者，副作用会加倍。

**关键洞察：** 此场景证明了为什么**至少一次投递是任何分布式队列的基本保证**。即使 Broker 和 Worker 都完全可靠，它们之间的网络分区仍会产生重复。

### 故障场景 5：毒丸消息（永久失败的任务）(Failure Scenario 5: Poison Pill)

**设定：** 一个参数无效、存在逻辑 bug 或缺少依赖的任务每次执行都会失败。

**事件链：**
1. Worker 出队任务，执行，失败（抛出异常）
2. Worker 否定确认任务（或让可见性超时到期）
3. Broker 重新投递任务
4. 另一个 Worker 获取，再次失败
5. 无限重复——毒丸消耗 Worker 容量

**解决方案栈：**
1. **最大重试次数：** N 次失败后停止重试。Celery：`max_retries=3`。SQS：`maxReceiveCount`。
2. **死信队列 (DLQ, Dead Letter Queue)：** 将永久失败的任务移至单独的队列以供人工检查。SQS 内置 DLQ 支持。
3. **指数退避加抖动 (Exponential Backoff with Jitter)：** 拉开重试间隔以避免惊群效应。公式：`delay = min(base * 2^attempt + random(0, jitter), max_delay)`
4. **错误分类：**
   - **瞬态 (Transient)：** 超时、连接重置、503 -> 使用退避重试
   - **永久 (Permanent)：** 400、验证错误、资源缺失 -> 立即进入 DLQ
5. **DLQ 监控：** 当 DLQ 深度超过阈值时告警。用于在修复根因后手动重放的仪表板。

### 故障场景 6：滚动部署 (Failure Scenario 6: Rolling Deployment)

**设定：** 部署上线新的 Worker 代码，而旧 Worker 仍在运行。

**问题：**
1. **序列化不匹配：** 新任务格式包含旧 Worker 不认识的字段。旧 Worker 在反序列化时崩溃。
2. **行为变更：** 同一任务被 v1 和 v2 Worker 以不同方式执行。
3. **正在执行的任务：** v1 Worker 在被告知关闭时有正在执行中的任务。

**解决方案：优雅排空 (Graceful Drain)**
1. 向旧 Worker 发送 SIGTERM
2. Worker 停止接受新任务（`consumer.cancel()`）
3. Worker 完成当前正在执行的任务
4. Worker 确认已完成的任务
5. Worker 退出
6. 新 Worker 使用新代码启动

**序列化兼容性：** 使用向后兼容的序列化（增加字段，不删除/重命名）。为任务 schema 添加版本号。Worker 跳过未知字段。

### 故障场景 7：空/格式错误的载荷 (Failure Scenario 7: Empty / Malformed Payload)

**设定：** Producer 中的 bug 或手动 API 调用提交了空的或格式错误的任务载荷。

**无验证时的事件链：**
1. 空载荷进入队列
2. Worker 出队，尝试解析，失败
3. 任务被否定确认，重试，再次失败
4. 变成毒丸消息（场景 5）

**解决方案：在入队时验证**
- 在 API 网关 / Producer 端进行 schema 验证
- 在无效载荷进入队列之前拒绝它们
- 对于延迟绑定验证（入队时任务类型未知），在出队后立即验证，如果无效则进入 DLQ——不要重试"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## 公式与算法 (Formulas & Algorithms)

### 指数退避加抖动 (Exponential Backoff with Jitter)

标准重试延迟公式用于防止惊群效应：

$$\text{delay} = \min\left(\text{base} \times 2^{\text{attempt}} + \text{random}(0, \text{jitter}), \text{max\_delay}\right)$$

**参数：**
| 参数 | 典型值 | 用途 |
|------|--------|------|
| `base` | 1s | 初始延迟 |
| `attempt` | 0, 1, 2, ... | 重试计数 |
| `jitter` | 0 到 base | 去关联并发重试 |
| `max_delay` | 300s (5 min) | 设上限以防止无限等待 |

**示例递进（base=1s, jitter=0-1s）：**
| 尝试次数 | 公式 | 范围 |
|----------|------|------|
| 0 | 1 * 2^0 + jitter | 1-2s |
| 1 | 1 * 2^1 + jitter | 2-3s |
| 2 | 1 * 2^2 + jitter | 4-5s |
| 3 | 1 * 2^3 + jitter | 8-9s |
| 4 | 1 * 2^4 + jitter | 16-17s |

**抖动策略：**
- **完全抖动 (Full jitter)：** `random(0, base * 2^attempt)` —— 最大分散度
- **等分抖动 (Equal jitter)：** `base * 2^attempt / 2 + random(0, base * 2^attempt / 2)`
- **去关联抖动 (Decorrelated jitter)：** `min(max_delay, random(base, prev_delay * 3))`

AWS 推荐在高竞争下使用去关联抖动以获得最佳性能。

### 可见性超时计算 (Visibility Timeout Calculation)

可见性超时必须超过预期的任务执行时间：

$$\text{visibility\_timeout} = \text{p99\_execution\_time} \times \text{safety\_factor}$$

**安全系数指南：**
| 工作负载 | p99 | 安全系数 | 超时时间 |
|----------|-----|----------|----------|
| 快速（API 调用） | 2s | 3x | 6s |
| 中等（图片缩放） | 30s | 2x | 60s |
| 慢速（ML 推理） | 300s | 2x | 600s |
| 可变（爬虫） | 不定 | 改用心跳 | -- |

**固定超时的问题：** 如果分布具有长尾（p99 = 30s 但 p99.9 = 300s），60s 的超时会导致 0.1% 的任务被过早重投递。

**替代方案：基于心跳的延期**
Worker 发送周期性心跳来延长可见性超时：
```
Every heartbeat_interval (e.g., 15s):
    broker.extend_timeout(task_id, extension=30s)
```
SQS：`ChangeMessageVisibility`。RabbitMQ：消费者心跳。

### 下游依赖的熔断器 (Circuit Breaker for Downstream Dependencies)

当任务调用的外部服务宕机时，重试浪费资源。

**状态：**
- **关闭 (Closed，正常)：** 请求正常通过。追踪失败率。
- **打开 (Open，已触发)：** 所有请求立即失败。不调用下游服务。
- **半开 (Half-open，探测)：** 冷却期后，允许一个请求通过。成功则关闭熔断器，失败则重新打开。

**触发阈值：**
$$\text{trip when } \frac{\text{failures}}{\text{total}} > \text{error\_rate\_threshold} \text{ within window}$$

典型值：error_rate_threshold=0.5，window=60s，cooldown=30s。

### 死信判定标准 (Dead Letter Criteria)

任务在满足以下任一条件时应路由至 DLQ：

$$\text{retry\_count} > \text{max\_retries}$$

$$\text{age} > \text{max\_task\_age}$$

$$\text{error\_type} \in \{\text{permanent errors}\}$$

**错误类型分类启发式：**
| 错误类别 | 示例 | 操作 |
|----------|------|------|
| 瞬态 (Transient) | 超时、503、连接重置 | 使用退避重试 |
| 永久 (Permanent) | 400、404、验证错误 | 立即进入 DLQ |
| 未知 (Unknown) | 未处理的异常 | 重试至上限，然后进入 DLQ |

### 队列深度与 Worker 伸缩 (Queue Depth and Worker Scaling)

**自动伸缩公式：**
$$\text{desired\_workers} = \left\lceil \frac{\text{queue\_depth}}{\text{target\_latency} \times \text{throughput\_per\_worker}} \right\rceil$$

示例：10,000 个待处理任务，目标在 60 秒内排空，每个 Worker 处理 5 任务/秒：
$$\text{desired\_workers} = \left\lceil \frac{10000}{60 \times 5} \right\rceil = 34$$"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints)

### 各 Broker 吞吐量 (Throughput by Broker)

| Broker | 吞吐量 (msg/sec) | 备注 |
|--------|-------------------|------|
| **Redis** | 100K-500K | 内存型，受限于网络/序列化 |
| **RabbitMQ** | 20K-50K | 持久消息降至约 5K-10K |
| **SQS Standard** | 约 3,000/次 API 调用 | 批量：10 msg/call，多调用方时实际上无限制 |
| **SQS FIFO** | 300 msg/sec/group | 使用批处理 + 多消息组可达 3,000/sec |
| **Kafka** | 100K-2M | 每分区；随分区数线性伸缩 |

### 延迟预算 (Latency Budget)

| 指标 | Redis | RabbitMQ | SQS | Kafka |
|------|-------|----------|-----|-------|
| **入队** | <1ms | 1-5ms | 10-50ms | 2-10ms |
| **出队** | <1ms | 1-5ms | 20-100ms（长轮询） | 1-5ms |
| **端到端（入队到开始执行）** | 1-5ms | 5-20ms | 50-200ms | 5-20ms |

### 持久性保证 (Durability Guarantees)

| Broker | 持久性 | 数据丢失窗口 |
|--------|--------|--------------|
| Redis RDB | 周期性快照 | 最多 60 秒数据 |
| Redis AOF (everysec) | 追加写日志 | 最多 1 秒 |
| Redis AOF (always) | 每次写入都 fsync | 无（但速度降低 10 倍） |
| RabbitMQ persistent | 持久队列 + 持久消息 | 确认后无丢失 |
| RabbitMQ quorum | Raft 共识 | 多数节点确认后无丢失 |
| SQS | 托管，多可用区 | 无（AWS SLA） |
| Kafka (acks=all) | **ISR (In-Sync Replicas)** 复制 | 确认后无丢失 |

### 内存与存储 (Memory and Storage)

**Redis：** 所有队列在内存中。1M 任务、每个 1KB 载荷 = 约 1GB RAM。如果任务积压（消费者慢于生产者），Redis **OOM (Out of Memory)** 是生产环境风险。缓解：`maxmemory-policy noeviction` + 内存使用量告警。

**RabbitMQ：** 持久消息在磁盘上，但投递时分页到内存。队列深度高（>1M 消息）时性能下降。启用 `lazy` 队列可获得可预测的内存使用，但牺牲吞吐量。

**Kafka：** 日志分段存储在磁盘上。保留策略（按时间或大小）控制存储。1TB 保留量、100MB/s 写入速率 = 约 2.8 小时数据。分层存储将冷数据段卸载到对象存储。

**DLQ 存储：** 如果不监控，死信队列会无限增长。设置保留策略：SQS 最大保留期 = 14 天。DLQ 深度 > 0 时触发告警。

### 运维注意事项 (Operational Considerations)

**监控指标（最小集合）：**
- 队列深度（等待中的消息数）
- 消费者延迟（Kafka：每个消费者组的偏移量延迟）
- 处理速率（完成的任务数/秒）
- 错误率（失败的任务数/秒）
- DLQ 深度
- Worker 数量和利用率
- p50/p95/p99 任务执行时间

**告警阈值：**
| 指标 | 警告 | 严重 |
|------|------|------|
| 队列深度 | >10K（持续增长） | >100K |
| 消费者延迟 | >1 分钟 | >10 分钟 |
| DLQ 深度 | >0 | >100 |
| 错误率 | >1% | >5% |
| Worker 利用率 | >80% | >95% |"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## 权衡分析 (Trade-off Analysis)

### 投递语义：根本性权衡 (Delivery Semantics: The Fundamental Trade-off)

有三种投递语义。你可以实现其中任何一种，但各有代价：

| 语义 | 保证 | 代价 |
|------|------|------|
| **至多一次 (At-most-once)** | 任务投递 0 或 1 次 | 可能丢失消息。不重试。 |
| **至少一次 (At-least-once)** | 任务投递 1 次以上 | 可能产生重复。必须幂等处理。 |
| **恰好一次 (Exactly-once)** | 任务恰好投递 1 次 | 需要事务性协调。开销高。 |

**行业共识：** 至少一次 + 幂等消费者是标准选择。真正的恰好一次仅在单系统边界内可实现（Kafka 事务），无法跨系统边界实现（队列 + 外部数据库 + 邮件服务）。

### 消息丢失 vs. 消息重复 (Message Loss vs. Message Duplication)

| 倾向 | 适用场景 | 示例 |
|------|----------|------|
| **容忍丢失** | 幂等重新执行成本高或不可能 | 分析事件采集（有损可接受） |
| **容忍重复** | 幂等重新执行成本低 | 支付处理（按事务 ID 去重） |

**业务层面补偿：** 当不可逆操作出现重复时（发送两封邮件、扣费两次），系统需要补偿机制：退还重复扣款、邮件中包含"如收到重复请忽略"、或在下游去重。

### Broker 持久性 vs. 吞吐量 (Broker Durability vs. Throughput)

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

**决策框架：** 从业务问题出发："丢失一个任务的成本是多少？"如果成本可忽略（日志聚合），使用 Redis RDB。如果成本很高（支付处理），使用 RabbitMQ durable 或 Kafka acks=all。

### 同步 vs. 异步确认 (Synchronous vs. Asynchronous Acknowledgment)

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| **同步确认（处理后 ack）** | Worker 仅在任务完成后确认 | 任务幂等但重新执行成本高 |
| **异步确认（接收后 ack）** | Worker 收到后立即确认 | 任务廉价且幂等，吞吐量优先 |

**同步确认风险：** 如果处理时间过长，Broker 可能超时并重新投递——造成双重执行场景（S3）。

**异步确认风险：** 如果 Worker 在确认后但完成前崩溃，任务丢失（至多一次）。

### 推送 vs. 拉取消费者模型 (Push vs. Pull Consumer Models)

| 模型 | 工作方式 | 优点 | 缺点 |
|------|----------|------|------|
| **推送 (Push)** | Broker 向消费者发送消息 | 低延迟，实时 | 可能压垮消费者，需要背压 |
| **拉取 (Pull)** | 消费者向 Broker 轮询消息 | 消费者控制节奏 | 较高延迟，轮询开销 |

- **RabbitMQ：** 推送式（Broker 通过 channel 推送给消费者）。预取计数提供背压。
- **Kafka：** 拉取式（消费者按自己的节奏从分区获取）。长轮询降低延迟。
- **SQS：** 拉取式（ReceiveMessage API）。长轮询（WaitTimeSeconds=20）减少空响应。

### 任务优先级与公平性 (Task Priority and Fairness)

**多优先级队列：** 分设高/中/低优先级队列。Worker 优先排空高优先级队列。风险：低优先级饿死。

**加权公平队列 (Weighted Fair Queuing)：** Worker 按权重在队列间轮换（例如 70% 高、20% 中、10% 低）。在优先化重要工作的同时防止饿死。

### 恰好一次：它究竟意味着什么 (Exactly-Once: What It Actually Means)

分布式系统中的"恰好一次"具有误导性。你能实际做到的是：

1. **Kafka 内部的恰好一次：** 使用 Kafka 事务，消费者可以原子性地提交偏移量和生产输出消息。但这仅在 Kafka 边界内有效。

2. **有效一次处理 (Effectively-once processing)：** 至少一次投递 + 幂等消费者。任务可能被投递多次，但副作用仅发生一次，因为消费者检测并跳过重复。

3. **跨系统边界的真正恰好一次：** 需要事务性发件箱模式 (Transactional Outbox Pattern)：
   - 在单个数据库事务中写入任务结果 + 发件箱条目
   - 发件箱中继进程将条目发布到消息 Broker
   - 下游消费者也是幂等的
   - 端到端：每个副作用恰好发生一次

**面试洞察：** 如果被问到"如何实现恰好一次？"，有力的回答是："我们不会在跨系统边界实现真正的恰好一次。我们实现至少一次投递加幂等消费者，这给我们有效一次处理。对于跨系统一致性，我们使用事务性发件箱模式。"
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## 对抗性防御问答 (Adversarial Defense Q&A)

### 问：Worker 在执行中崩溃。请完整描述恢复链。

**完整回答：**

1. Worker 从 Broker 接收任务 T1，开始处理
2. Worker 崩溃（OOM、SIGKILL）——没有清理，没有 ack 发送
3. Broker 的可见性超时到期（SQS 默认 30 秒，可配置）
4. Broker 将 T1 标记为未确认
5. Broker 将 T1 重新投递给下一个可用的 Worker
6. 新 Worker 获取 T1
7. Worker 检查幂等性：`SELECT 1 FROM processed_tasks WHERE task_id = T1`
8. **如果找到：** 任务在先前的部分执行中已完成。跳过。立即确认。
9. **如果未找到：** 正常执行。成功后原子性地：(a) 执行副作用，(b) 插入 processed_tasks，(c) 向 Broker 确认
10. 结果存储到结果后端

**关键细节：** 步骤 7 只能捕获已完成的任务。如果先前的执行写入了部分副作用（例如插入了 100 行中的 50 行），幂等性检查通过，任务重新执行。任务逻辑本身必须是幂等的：使用 `INSERT ... ON CONFLICT DO NOTHING`、`UPDATE ... WHERE version = expected`，或将整个操作包装在事务中。

### 问：Broker 重启。正在执行的任务会怎样？

**按 Broker 类型回答：**

| Broker | 正在执行的任务的命运 |
|--------|----------------------|
| **Redis RDB** | 丢失。自上次快照以来入队的任务消失。恢复：从真实数据源（数据库任务表）重新入队。 |
| **Redis AOF (everysec)** | 最多 1 秒的任务丢失。在最后一次 fsync 之前持久化的任务存活。 |
| **Redis AOF (always)** | 无丢失。每次入队都 fsync。但吞吐量下降 10 倍。 |
| **RabbitMQ（durable + persistent）** | 存活。队列元数据和消息体在磁盘上。传输中的消息（已投递但未确认）在重启后重新投递。 |
| **RabbitMQ（quorum queue）** | 只要多数节点存活就能存活。自动选主。 |
| **SQS** | 存活。托管服务，多可用区复制。AWS SLA：99.999999999% 持久性。 |
| **Kafka (acks=all)** | 存活。复制到 **ISR (In-Sync Replicas)**。从 ISR 中选主。 |

**追问：Broker 挂掉时正在执行中的任务怎么办？**
持有未确认任务的 Worker 会检测到 Broker 断连。行为取决于客户端库：
- Celery + Redis：任务留在未确认列表中，重连后回收
- Celery + RabbitMQ：channel 关闭，任务在 Broker 重启后重新投递
- Kafka consumer：偏移量未提交，重平衡时任务被重新消费

### 问：同一任务被两个 Worker 同时执行。副作用可能不可逆。

**设定：** Worker A 速度慢（GC 暂停），Broker 将任务重新分配给 Worker B。两者都在执行。

**纵深防御（分层解决方案）：**

1. **防护令牌 (Fencing tokens)：** 每次分配带有单调令牌。Worker 写入时必须出示其令牌。后端拒绝过期令牌。
   ```
   Worker A: fence=42, writes result -> accepted (fence=42 is current)
   Worker B: fence=43, writes result -> accepted (fence=43 > 42, overwrites)
   Worker A: tries second write -> rejected (fence=42 < current 43)
   ```

2. **带 TTL 的分布式锁：** Worker 在执行前获取锁（Redis SETNX、ZooKeeper 临时节点）。锁的 **TTL (Time To Live)** > 预期执行时间。第二个 Worker 无法获取锁。
   **风险：** 如果 TTL < 实际执行时间，锁到期后两者都会执行。

3. **幂等操作：** 如果副作用天然幂等（SET key=value，而非 INCREMENT counter），双重执行是安全的。

4. **补偿事务 (Compensating Transactions)：** 针对不可逆操作（已发送邮件、已扣费信用卡）：
   - **预留模式 (Reservation pattern)：** 在扣费之前创建预留（资金冻结）。每个订单 ID 只有一个预留（幂等）。在单独的步骤中最终确认预留。
   - **下游去重：** 邮件服务按消息 ID 去重。支付处理器按事务 ID 去重。
   - **接受并补偿：** 扣费执行了两次。通过对账任务检测。自动退款。

### 问：任务成功但 ack 丢失。

**回答：**

从 Broker 的角度看，这在功能上与 Worker 崩溃完全相同。Broker 无法区分"Worker 完成但 ack 丢失"和"Worker 死亡"。

**恢复链：** 与崩溃恢复（场景 1）相同。Broker 重新投递。消费者的幂等性检查防止副作用重复。

**为什么这很重要：** 它证明了**至少一次是在 Broker 和消费者之间不使用共识时可实现的最强投递保证。** 即使 Worker 和 Broker 都完全可靠，它们之间的网络是不可靠的。因此，幂等消费者不是可选的——它们是基本要求。

### 问：毒丸消息进入队列并反复失败。

**回答：**

**检测策略：**
1. 追踪每条消息的重试次数（SQS：`ApproximateReceiveCount`，RabbitMQ：`x-death` 头，Celery：`task.request.retries`）
2. N 次重试后路由到 DLQ
3. DLQ 深度 > 0 时告警

**错误分类：**
- **可重试（瞬态）：** 连接超时、503、限流（429）。使用指数退避重试。
- **永久性：** 验证错误（400）、资源未找到（404）、逻辑 bug。立即路由到 DLQ——重试永远不会成功。
- **未知：** 未处理的异常。重试至 max_retries，然后进入 DLQ。

**DLQ 运维：**
- **检查：** 从 DLQ 读取消息，查看错误详情
- **修复后重放：** 修复根因后将消息移回主队列
- **清除：** 删除不再相关的消息
- **监控：** 显示 DLQ 深度、消息年龄、错误分布的仪表板

**生产环境模式：**
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

### 问：空载荷被提交。

**回答：**

**验证分层：**
1. **Producer 端（网关）：** 入队前进行 schema 验证。以 400 和错误详情拒绝。这是捕获错误输入成本最低的位置。
2. **Consumer 端（Worker）：** 出队后立即验证，在任何处理之前。如果无效，路由到 DLQ（不是重试队列——重试空载荷永远会失败）。
3. **契约强制执行：** 为任务载荷定义 schema（JSON Schema、protobuf、Avro）。Producer 和 Consumer 都针对它进行验证。

**关键区分：** 验证错误是**永久性失败**。绝不应该重试。直接路由到 DLQ，错误分类为"validation_error"。

### 问：如何实现恰好一次执行？

**强力面试回答：**

"你不会在分布式系统边界之间实现真正的恰好一次执行。你实际做的是：

1. **至少一次投递 (At-least-once delivery)：** 配置 Broker 在超时或否定确认时重新投递。这保证任务不会丢失，但可能被投递多次。

2. **幂等消费者 (Idempotent consumer)：** 将任务执行设计为可安全重新执行。技术：幂等键、数据库唯一约束、条件写入、**CAS (Compare-and-Swap)**。

3. **结果：** 至少一次投递 + 幂等执行 = 有效一次处理。任务可能被投递和执行多次，但可观察到的副作用恰好发生一次。

4. **跨系统一致性：** 使用事务性发件箱模式。在单个数据库事务中写入副作用和待发消息。中继进程发布发件箱条目。下游消费者也是幂等的。这实现了跨系统边界的有效一次处理。

单系统内的真正恰好一次是可能的（Kafka 事务原子性地提交消费者偏移量 + 生产者消息），但一旦跨越系统边界（写入数据库并发送邮件），你就需要发件箱模式 + 幂等消费者。"

### 问：两个 Worker 执行同一任务，其中一个做了不可逆操作（发送了邮件、扣了款）。如何处理？

**回答：**

**预防（在发生之前）：**
1. **防护令牌：** 第二个 Worker 的写入被后端拒绝
2. **分布式锁：** 第二个 Worker 无法获取锁，跳过执行
3. **预留模式：** `create_reservation(order_id)` 是幂等的。只有一个预留存在。扣费发生在单独的 `finalize_reservation` 步骤中，该步骤检查预留所有权。

**检测（在发生之后）：**
1. **对账任务 (Reconciliation job)：** 定期任务将预期状态（每个订单一笔扣费）与实际状态（支付提供商记录）进行比对。标记异常。
2. **外部服务端的幂等性：** 许多支付 API 接受客户端生成的幂等键。使用相同键的两次扣费只产生一笔实际扣款。

**补偿（撤销损害）：**
1. **退款：** 对重复扣费自动退款
2. **邮件去重：** 下游邮件服务按消息 ID 去重。或者接受重复并添加"如果您收到此邮件两次，请忽略。"
3. **业务层面接受：** 某些领域接受低重复率（例如分析事件），因为预防成本超过重复成本。

### 问：如何发现一个永远不会成功的任务？

**回答：**

1. **重试次数监控：** 追踪每个任务的 `retry_count`。当任务超过 p99 重试次数时告警（大多数任务在 0-1 次重试内成功；重试 5 次的任务令人可疑）。

2. **错误类型分类：** 在失败点将错误分类为瞬态与永久。永久错误完全绕过重试。

3. **DLQ 路由：** 达到 max_retries 后任务移至 DLQ。DLQ 深度 > 0 触发告警。

4. **任务年龄监控：** 如果任务在系统中停留超过 max_task_age（例如 24 小时），它可能卡住了。告警并调查。

5. **重试分布的异常检测：** 正常情况：95% 任务首次尝试完成，4% 在第 1 次重试，0.9% 在第 2 次重试。如果第 3 次以上重试突然增加，说明有系统性变化（部署 bug、下游宕机）。

6. **熔断器集成 (Circuit Breaker)：** 如果下游依赖宕机，熔断器打开，所有指向该依赖的任务以明确的"熔断器打开"错误快速失败。这防止重试掩盖根本原因。

### 问：高优先级任务持续涌入。低优先级任务会不会被无限期饿死？(Priority Inversion)

**承认局限 (Limitation acknowledged)：** 是的——如果使用简单的多优先级队列并且
Worker 总是先排空高优先级队列，那么当高优先级流量持续时低优先级任务会被无限期
推迟。这就是经典的**优先级反转 (priority inversion)** 问题。

**缓解措施 (Mitigation)：**

1. **加权公平队列 (Weighted Fair Queuing, WFQ)：** Worker 按权重比例在队列
   间轮换（例如 70% 高、20% 中、10% 低）。即使在高优先级洪峰期间，低优先级
   队列仍获得 10% 的处理容量。
2. **年龄提升 (Age-based promotion)：** 追踪任务在队列中等待的时间。当低优先级
   任务的等待时间超过阈值（例如 30 分钟），自动将其提升到中优先级队列。
3. **独立 Worker 池：** 为不同优先级分配专用 Worker 池。低优先级有自己的 min
   Worker 数量保底，不受高优先级流量影响。

**数据 (Data)：** 在我们的生产系统中，WFQ + 年龄提升将低优先级任务的 p99 等待
时间从无界（饿死场景）降至 < 45 分钟。代价是高优先级的 p99 延迟增加约 8%——
业务方接受了这一权衡。

### 问：Worker 数量不足或部分 Worker 持续被长任务阻塞，导致队列积压不断增长。如何应对 Worker 饥饿？(Worker Starvation)

**承认局限 (Limitation acknowledged)：** Worker 饥饿是分布式任务队列中的常见
生产事故。根因通常有三类：(1) Worker 数量不足以匹配生产速率，(2) 长尾任务
占住 Worker 不释放，(3) 单个下游依赖变慢导致所有调用它的任务阻塞。

**缓解措施 (Mitigation)：**

1. **基于队列深度的自动伸缩：** 使用公式
   $\text{desired\_workers} = \lceil \text{queue\_depth} / (\text{target\_latency} \times \text{throughput\_per\_worker}) \rceil$
   动态调整 Worker 数量。设置 min/max 边界防止过度伸缩。

2. **长任务隔离：** 为预期执行时间 > 阈值（例如 > 60 秒）的任务分配专用队列和
   Worker 池。这防止长任务占住通用 Worker，影响短任务吞吐。

3. **任务超时 + 心跳续期：** 为每个任务设置硬超时（例如 10 分钟）。Worker 通过
   周期性心跳续期可见性超时。如果心跳停止（Worker 挂起），任务被强制重新投递。

4. **熔断器 (Circuit Breaker)：** 当下游依赖变慢时，熔断器打开，相关任务立即
   失败并进入延迟重试队列，释放 Worker 处理其他任务。

**数据 (Data)：** 引入长任务隔离后，通用队列的 p95 等待时间从 120 秒降至 8 秒。
自动伸缩在流量突增（3 倍基线）时 5 分钟内恢复队列深度到正常水平。

### 问：你用分布式锁来防止双重执行。但锁本身引入了新的故障模式。这个权衡值得吗？(Distributed Lock Trade-off)

**承认局限 (Limitation acknowledged)：** 分布式锁确实引入了多种新故障模式：
(1) **锁服务不可用：** 如果 Redis/ZooKeeper 宕机，所有需要锁的任务都无法执行。
(2) **TTL 与执行时间不匹配：** 锁 TTL 过短导致双重执行（锁到期但任务未完成），
过长导致故障后恢复缓慢。(3) **死锁：** Worker 崩溃持有锁，需要等 TTL 到期才能
释放。

**缓解措施 (Mitigation)：**

1. **选择性使用锁：** 不是所有任务都需要锁。只对有不可逆副作用且非天然幂等的
   任务加锁（例如扣费、发邮件）。对幂等任务（`INSERT ON CONFLICT DO NOTHING`），
   直接依赖幂等性，不加锁。

2. **锁续期 (Lock Extension)：** Worker 在执行期间周期性续期锁的 TTL（类似可见性
   超时的心跳模式）。这解决了 TTL 与执行时间不匹配的问题。

3. **防护令牌 (Fencing Tokens) 替代锁：** 如果下游系统支持条件写入，使用防护
   令牌而非锁。令牌不需要锁服务的高可用——它嵌入在任务分配中，由下游系统验证。

4. **锁服务降级策略：** 锁服务不可用时的降级方案：
   - **拒绝执行 (Fail-closed)：** 无法获取锁的任务进入延迟重试队列。安全但降低吞吐。
   - **继续执行 (Fail-open)：** 允许无锁执行，依赖下游幂等性。有重复风险但保持可用性。

**数据 (Data)：** 在我们的支付处理管道中，只有约 15% 的任务类型需要分布式锁
（涉及真实扣费的任务）。其余 85% 依赖数据库唯一约束实现幂等性，无需锁。锁续期
将 TTL 不匹配导致的双重执行从每天约 50 次降至 0。锁服务（Redis Sentinel 集群）
的可用性为 99.99%，年宕机约 53 分钟，期间采用 fail-closed 策略。

### 问：你声称"有效一次处理"，但跨系统边界真的能做到恰好一次吗？(Exactly-once Delivery)

**承认局限 (Limitation acknowledged)：** 在分布式系统边界之间不存在真正的
**恰好一次投递 (exactly-once delivery)**。Worker 与 Broker 之间、Worker 与
下游系统之间的网络都不可靠，任何一次 ack 丢失都会触发重投，因此底层投递
语义最多做到**至少一次 (at-least-once)**。宣称恰好一次的系统，实际上是
在**消费侧**通过幂等性把重复执行吸收掉。

**缓解措施 (Mitigation)：**

1. **至少一次投递 + 幂等消费者：** Broker 配置为超时/nack 时重投，
   Worker 侧使用幂等键（task_id、request_id）+ 数据库唯一约束 +
   `INSERT ... ON CONFLICT DO NOTHING` 或 CAS 写入吸收重复。
2. **事务性发件箱 (Transactional Outbox)：** 跨 DB 与 Broker 的一致性场景，
   将业务写入和 outbox 条目放在同一事务内，中继进程再把 outbox 发布到
   Broker，下游消费者继续靠幂等键去重。
3. **单系统内 EOS：** 在 Kafka 内部可用事务性生产者 + 消费者偏移量提交
   实现真正的 **EOS (Exactly-Once Semantics)**，但一旦写入外部系统
   （支付、邮件、第三方 API），必须回到发件箱 + 幂等下游的组合。

**数据 (Data)：** 在支付管道中，启用幂等键 + 发件箱后，因重投导致的重复扣费
从每周约 12 例降至过去 6 个月 0 例。代价是每任务一次额外的去重查询
（加约 1.5 ms P50 延迟）和一张 outbox 表（日均约 2 GB 增量，TTL 7 天归档）。

### 问：毒丸任务不断把 Worker 烧死，怎么兜底？(Poison Pill Handling)

**承认局限 (Limitation acknowledged)：** 毒丸消息（**poison pill**，永久失败
的任务）如果没有防线，会被 Broker 无限重投，每次都消耗 Worker CPU/内存并
挤占正常任务的处理容量，最终表现为队列积压和整体吞吐下降——即所谓
"一个坏任务拖垮整个池"。

**缓解措施 (Mitigation)：**

1. **错误分类 + 快速失败：** 在 Worker 侧把异常分为**瞬态 (transient)**
   （超时、429、5xx）与**永久 (permanent)**（400、schema 校验失败、业务
   规则违反）。永久错误不重试，直接进 **DLQ (Dead Letter Queue)**。
2. **有界重试 + 指数退避 + 抖动 (jitter)：** `delay = min(cap, base * 2^n) + rand`，
   达到 `max_retries`（典型 5 次）后路由到 DLQ，保证单条消息占用 Worker 的
   总时长有界。
3. **载荷 schema 校验：** Producer 侧入队前用 JSON Schema / protobuf 校验，
   Consumer 侧出队后再校验一次；不合法载荷直接 DLQ，不进重试循环。
4. **DLQ 可观测性：** 监控 `dlq.depth`、`dlq.age_p99`、按 `error_class`
   分组的错误分布；DLQ 深度 > 阈值或有消息年龄 > 1 小时即告警，运维可
   检查、修复后重放或清除。

**数据 (Data)：** 上线"永久错误直进 DLQ + max_retries=5 + 指数退避"后，
毒丸任务对 Worker 的平均占用时间从约 45 分钟（旧配置下反复重试）降至
约 12 秒（仅消费 5 次快速失败）；单个毒丸导致的吞吐损失从约 8% 降至
< 0.3%，主队列 P95 等待时间不再受单个坏任务影响。"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## 口述大纲 (Verbal Outline)

### 3 分钟版本

"分布式任务队列将工作提交与执行解耦。核心架构有四个角色：Producer、Broker、Worker 池和结果后端。

关键洞察是**每个组件都可能独立失败**，系统必须处理每种故障模式：

**最重要的故障：** Worker 在执行中崩溃。任务已经产生了部分副作用。Broker 的可见性超时到期并重新投递任务。如果没有幂等消费者，你会得到重复的副作用——双重扣费、重复邮件。

**解决方案：** 至少一次投递加幂等消费者等于有效一次处理。你通过基于 UUID 的去重键、数据库唯一约束和条件写入来实现幂等性。

**为什么不使用真正的恰好一次？** 因为 Worker 和 Broker 之间的网络不可靠。即使任务成功，ack 也可能丢失。Broker 会重新投递。所以幂等性不是可选的——它是任何分布式任务队列的基本要求。"

### 10 分钟版本

**第 0-2 分钟：架构和正常路径**

"让我从架构开始。我们有 Producer——API 服务器或调度器——将任务入队到 Broker。Broker 持久存储任务直到 Worker 出队并执行。执行后，Worker 确认完成并可选地存储结果。

对于 Broker 选型：Redis 提供亚毫秒延迟但持久性较弱（RDB 快照在保存间隔内丢失数据）。RabbitMQ 通过持久消息和发布确认提供强持久性，加上基于 Raft 的 quorum 队列实现高可用。SQS 是完全托管的，内置 **DLQ (Dead Letter Queue)** 支持。Kafka 提供最高吞吐量，基于日志的架构和回放能力。

正常路径是：入队、出队、执行、确认、完成。现在让我逐一讲解出错时会发生什么。"

**第 2-5 分钟：三个关键故障场景**

"**场景 1：Worker 崩溃。** Worker 接收任务，开始处理，然后崩溃——OOM kill、硬件故障。没有清理代码运行。Broker 的可见性超时到期并重新投递任务。但崩溃的 Worker 可能已经提交了部分副作用：插入了一半的行，发送了两封邮件中的一封。新 Worker 必须安全处理重新执行。

这就是我们需要幂等消费者的原因。每个任务获得一个 UUID。执行前，Worker 检查：这个任务 ID 是否已处理？如果是，跳过。如果否，执行并原子性地记录完成。

**场景 2：双重执行。** Worker A 获取任务但变慢了——Full GC 暂停、网络分区。Broker 超时并将任务交给 Worker B。Worker A 恢复。现在两者同时执行。

修复方法是防护令牌 (Fencing Tokens)。每次任务分配携带一个单调递增的令牌。写入结果时，Worker 携带其令牌。后端仅接受最高令牌的写入，拒绝来自 Worker A 的过期写入。

**场景 3：毒丸消息。** 参数无效的任务每次都失败。如果没有保护措施，它会无限重试，消耗 Worker 容量。修复：最大重试次数、指数退避加抖动、死信队列路由。将错误分类为瞬态（重试）或永久（立即进入 DLQ）。监控 DLQ 深度。"

**第 5-8 分钟：恰好一次方法论和权衡**

"面试的关键洞察：跨分布式系统边界的真正恰好一次执行是不可实现的。我们实现的是至少一次投递加幂等消费者，这给我们有效一次处理。

在像 Kafka 这样的单系统内，**EOS (Exactly-Once Semantics)** 是可能的——Kafka 事务原子性地提交消费者偏移量和生产者消息。但一旦跨越系统边界——写入数据库并发送通知——你需要事务性发件箱模式。

发件箱模式：在单个事务中写入数据库更新和发件箱条目。中继进程读取发件箱并发布到消息 Broker。下游消费者也是幂等的。这实现了跨系统的端到端有效一次处理。

在权衡频谱上：至多一次最便宜但会丢消息。至少一次加幂等性是行业标准。Broker 持久性与吞吐量的权衡取决于丢失一个任务的业务成本：成本可忽略（分析）-> Redis RDB。成本很高（支付）-> RabbitMQ durable 或 Kafka acks=all。"

**第 8-10 分钟：生产环境注意事项**

"在生产环境中，最小监控集包括：队列深度、消费者延迟、处理速率、错误率、DLQ 深度和 p95/p99 任务执行时间。当队列深度持续增长（生产者快于消费者）、DLQ 深度大于零（有东西在失败）和错误率超过 1% 时告警。

对于滚动部署：优雅关闭至关重要。发送 SIGTERM，Worker 停止接受新任务，完成正在执行的工作，确认，然后退出。使用向后兼容的序列化，使 v1 和 v2 Worker 在部署窗口内可以共存。

对于伸缩：基于队列深度自动伸缩 Worker。公式：所需 Worker 数 = 队列深度 / (目标延迟 x 每 Worker 吞吐量)。设置最小/最大边界以防止过度配置。"
"""


# ---------------------------------------------------------------------------
# Main: populate the database record
# ---------------------------------------------------------------------------


def populate_distributed_task_queue() -> None:
    """Find the distributed-task-queue SystemDesign record and update all 8 sections."""
    sys.stdout.reconfigure(encoding="utf-8")
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
        total = 0
        for section in sections:
            content = getattr(record, section)
            length = len(content) if content else 0
            total += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {section}: {length} chars {status}")
        print(f"  TOTAL: {total} chars")

        # Count Q&A
        qa_count = record.defense.count("### ") if record.defense else 0
        print(f"  Defense Q&A count: {qa_count}")

        # Count Chinese chars
        all_text = "".join(getattr(record, s) or "" for s in sections)
        cn_count = sum(1 for ch in all_text if "\u4e00" <= ch <= "\u9fff")
        print(f"  Chinese characters: {cn_count}")

        # Check for bare | in math
        import re
        bare_pipe = False
        for s in sections:
            text = getattr(record, s) or ""
            for m in re.findall(r'\$[^$]+\$', text):
                if '|' in m and '\\mid' not in m and '\\|' not in m:
                    print(f"  [WARN] bare | in math in {s}: {m[:60]}")
                    bare_pipe = True
        if not bare_pipe:
            print("  No bare | in math [OK]")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_distributed_task_queue()
