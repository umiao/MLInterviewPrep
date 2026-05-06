# Pinterest SD: Catalog Bulk Update (500M records, S3 + Async Fan-out)

> Pinterest System Design Interview Prep (2025-11 round)
> Scope: 从外部 catalog (~500M 行) 批量更新内部下游系统 — ingestion, partition, retry, fan-out, monitoring, tradeoffs
> Format: 45-min onsite SD loop (clarify 5m, high-level 5m, ingestion 8m, partition+retry 10m, fan-out 10m, monitor+tradeoff 5m, follow-up 2m)

---

## 0. Clarifying Questions (前 5 分钟必问)

面试官抛出 "Design a catalog bulk update pipeline" 时, 先澄清 scope. 500M 记录 + 下游 fan-out 意味着这是一个 data-platform 问题, 不是简单 CRUD.

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| 数据规模 | 500M 是 total 还是 daily delta? 单条大小? | 决定带宽 (500M * 2KB = 1TB) 与存储选型 |
| 更新频率 | 全量 daily / hourly delta / realtime upsert? | 决定 pipeline 架构 (batch vs streaming) |
| 数据来源 | 卖家上传? 第三方 feed? 内部爬虫? | 决定 ingestion 接口 (S3 drop vs API vs Kafka) |
| 下游系统 | 有几个? 各自延迟容忍? 数据格式一致吗? | 决定 fan-out 策略 (Kafka topic 粒度) |
| 一致性要求 | 下游最终一致即可, 还是需强一致? | 决定 exactly-once vs at-least-once |
| Schema | 是否演化? 字段类型有冲突? | 决定是否需要 schema registry (Avro/Protobuf) |
| 失败处理 | 单行错误丢弃还是整 batch 回滚? SLA 是什么? | 决定 **Dead Letter Queue** (DLQ, 死信队列) 粒度与 checkpoint 策略 |
| 回放能力 | 下游重建时要不要能 replay 历史? | 决定是否保留 S3 raw + Kafka retention |

**假设 (本设计默认)**:
- 500M records = daily full catalog, 每日凌晨卖家侧 upload 一次 S3 zipped **Newline-Delimited JSON** (NDJSON, 行分隔 JSON), 单条 ~2KB, 总 ~1TB
- 下游 7 个系统: search index, ads serving, home-feed candidate store, recommender feature store, shopping graph, policy/safety, analytics warehouse
- SLA: T+6h (凌晨 2 点 S3 drop, 早 8 点前所有下游可见)
- 一致性: 下游 eventual consistency, exactly-once 不强制但 duplicate 要 idempotent
- 失败处理: 单行解析错误进 DLQ, batch 失败可 partition-level 重试

---

## 1. High-Level Architecture

```
  [Seller / 3rd-party vendor]
           |
           v  daily zipped NDJSON upload
  +-----------------------------+
  |   S3 raw zone               |   s3://catalog-raw/dt=YYYY-MM-DD/part-*.ndjson.gz
  +-----------------------------+
           |
           v  S3 event -> SQS (Simple Queue Service, AWS 简单队列) trigger
  +-----------------------------+
  |   Ingestion Coordinator     |   Airflow DAG / Flink job manager
  |   - validate manifest       |
  |   - split into N partitions |
  |   - register run in meta DB |
  +-----------------------------+
           |
           v  fan-out to workers
  +-----------------------------+      +----------------------+
  | Partition Workers (Spark/   |----->|  Schema Registry     |
  |  Flink, 200 executors)      |      |  (Confluent/Avro)    |
  | - parse, validate, normalize|      +----------------------+
  | - diff vs previous snapshot |
  | - emit change events        |
  +-----------------------------+
           |
           v  Kafka (partitioned by catalog_id hash)
  +-----------------------------+
  |  catalog-change-events      |   7 partitions * replication=3, retention=7d
  +-----------------------------+
           |
     +-----+-----+-----+-----+-----+-----+-----+
     v           v     v     v     v     v     v
  [search]  [ads] [feed] [feat] [graph] [policy] [warehouse]
   consumer consumer ...                         (each with own consumer group)
           |
           v  per-consumer DLQ on failure
  +-----------------------------+
  | catalog-change-events.DLQ   |
  +-----------------------------+
           |
           v
  +-----------------------------+
  | Monitoring / Alerting       |   Prometheus + Grafana + PagerDuty
  | - lag, error-rate, RPO, RTO |
  +-----------------------------+
```

**关键决策**:
- S3 作为 source-of-truth, Kafka 只是 change-event bus (retention 7d, 重建走 S3 replay)
- 上游 Spark/Flink 做 heavy-lifting (parse/diff/validate), 下游 consumer 只做 apply
- Schema registry 保证 producer/consumer 解耦, 字段演化可控

---

## 2. Ingestion Layer

### 2.1 为何选 S3 bulk, 而不是 API / Kafka direct

| 方案 | 优点 | 缺点 | 何时用 |
|------|------|------|--------|
| **S3 bulk drop** (本设计) | 卖家侧简单 (一个 put), 天然支持 replay, 成本低 | 延迟高 (batch) | 日级全量, 500M+ 规模 |
| **Sync API (REST bulk upsert)** | 低延迟, 立刻可见 | 1TB 数据 → 需 seller-side 分批 + 重试, API server 压力大 | 小规模 (< 1M), 实时要求 |
| **Quick-async API** (API + work queue) | 可背压, 卖家侧简单 | server 需维持大量 in-flight job | 中等规模 (1M–10M), 准实时 |
| **Kafka direct producer** | 低延迟 + 有 replay | 卖家侧复杂 (需 Kafka client + schema) | 内部系统, 不适合外部 vendor |

→ 500M daily 全量, 卖家是外部方 → S3 bulk 是唯一正解. API / Kafka 方案留给 **delta upsert** (未来 section 10 follow-up).

### 2.2 S3 layout 与 manifest 协议

```
s3://catalog-raw/
  dt=2026-04-13/
    _SUCCESS                      # 卖家 upload 完成后写入
    manifest.json                 # {row_count, sha256, part_count, schema_version}
    part-00000.ndjson.gz          # 1GB each, ~500 parts
    part-00001.ndjson.gz
    ...
```

- `_SUCCESS` marker: 触发 S3 event → SQS → Airflow, 避免读到半写文件
- `manifest.json`: ingestion coordinator 先校验 row_count & sha256 再启动
- part 粒度 ~1GB: Spark task 级并行单位, 一个 part 失败只需重跑该 part

### 2.3 Sync vs async tradeoff (interview 常问)

**Sync (API 立即返回写入结果)**:
- 优: 卖家立刻知道成功/失败, 数据立刻生效
- 劣: 1TB 写入 tail latency 无法忍受, server-side 需要巨大 in-memory buffer, 不 survive crash
- 适用: < 10K records one-shot upsert

**Async (S3 + event-driven)**:
- 优: 解耦生产者消费者, 天然背压 (coordinator 控制启动节奏), replay 便宜
- 劣: 卖家不知道何时完成 → 需要 callback / status API
- 适用: > 1M records, 日级或小时级全量

→ 本设计选 async. 给卖家一个 **status API** `GET /v1/catalog-import/{run_id}` 查询 (ingested / parsing / fanning-out / done / failed)

---

## 3. Partition Strategy

500M 条数据 / 500 个 1GB part = 每 part 约 1M 条. 每条 2KB → 200 个 Spark executor * 4 cores = 800 task 并行, 单 task 处理 ~625K 条, 可在 10 分钟内完成. Partition 策略决定 **diff 正确性** 与 **下游 fan-out 顺序**.

### 3.1 三种 partitioning 方式对比

| 方式 | 规则 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **Range** (按 catalog_id 范围) | `id in [0, 1M), [1M, 2M), ...` | 好 debug, 便于 re-run 单 partition | 热点 (新 id 集中在尾部), seller 扩容后分布不均 | 静态 id, 均匀分布 |
| **Hash** (`hash(id) % N`) | mod N | 负载均匀, 实现简单 | N 固定死, rehash 要全量重跑 | N 稳定, 无扩缩容 |
| **Consistent-hash** (ring) | 分 virtual nodes, id 落在 ring 上 | N 变化时只 rehash 一小部分, 适合扩容 | 实现复杂, debug 难 | 长期演化, N 动态 |

→ 本设计选 **hash by catalog_id mod 500** (对齐 1GB part). 500M/500=1M per part, 负载均匀. 扩缩容需求低 (pipeline 一次性全量 rebuild, 不是长 running shard). 不选 consistent-hash 因为没有 online shard 扩缩容的需求.

→ **但 Kafka partition 必须用 consistent-hash-by-catalog_id**: 保证同一 catalog_id 的 update 按顺序到达下游 consumer, 否则 "create 后 delete" 可能变成 "delete 后 create" 的灾难.

### 3.2 为什么 diff 要 partition-local

下游不关心全量, 只关心 **change-events**: `{catalog_id, op: UPSERT|DELETE, before, after, version}`.

Diff 算法:
```
for each partition p:
    prev = read snapshot(dt-1, p)          # S3 Parquet
    curr = read raw(dt, p)                 # NDJSON
    outer_join(prev, curr, on=catalog_id)
    emit UPSERT if curr.hash != prev.hash
    emit DELETE if catalog_id missing in curr
    write new snapshot(dt, p)
```

Partition-local diff 关键: 前一天的 snapshot 也按同一 hash-mod-500 partition, 今天 diff 时只需读对应 partition. 不然要 shuffle 500M rows.

### 3.3 Tombstone / soft-delete 处理

卖家不会显式标记 delete — 行消失即代表 delete. Diff 发现 `prev 有, curr 无` → emit `{op: DELETE, catalog_id, version=dt}`. 下游收到后执行 tombstone (search index 删 doc, ads 停投). 保留 7 天 snapshot 便于 rollback.

---

## 4. Retry, Idempotency, DLQ

500M 规模下, 单次 run 必然有 failure. 三层容错:

### 4.1 Partition-level retry

Spark/Flink job 的 task 原生支持 retry (default 4 次). 单个 1GB part 失败:
- 重试 up to 4 次, 指数退避
- 仍失败 → write to `s3://catalog-raw/dt=.../_FAILED/part-X/` + 上报 meta DB 状态 `partition_failed`
- Coordinator 不 block 整个 run, 其他 part 继续. 运营可 replay 单 part: `airflow trigger --partition 00037`

### 4.2 At-least-once + idempotency (核心!)

Kafka producer 用 `acks=all, enable_idempotence=true, transactional_id=<partition_id>` → at-least-once + exactly-once-per-producer-session. 但 partition retry 跨 session → 仍可能 duplicate.

→ 下游必须 **idempotent**. 关键字段: `(catalog_id, version)` 其中 version = ingestion date + partition + row_num (全局单调). 下游 apply 前查 `last_applied_version`, 若 event.version <= last → skip.

**幂等实现**:
- Search index: use `catalog_id` as doc _id, ES bulk API upsert (天然幂等)
- Ads serving: RocksDB `put(catalog_id, value)` (最后写赢, 但必须 version check 防 out-of-order)
- Feature store: 同上 + version column
- Analytics warehouse: MERGE INTO (Iceberg/Delta) on catalog_id, version

### 4.3 DLQ (Dead Letter Queue)

三类 failure 路由到不同 DLQ:
1. **Parse error** (source side): 进 `s3://catalog-dlq/parse/dt=.../`, 卖家可查
2. **Schema validation error** (producer side): 进 `catalog-change-events.parse-dlq` Kafka topic, schema team 每日审
3. **Downstream apply error** (consumer side): per-consumer DLQ, e.g., `catalog-change-events.search-dlq`, search oncall 处理

DLQ 不是垃圾桶 — 每个 DLQ 有 **SLA + owner + runbook**. 超过 24h 未处理触发 PagerDuty.

### 4.4 Checkpoint

Coordinator 维持 meta DB (PostgreSQL):
```sql
CREATE TABLE catalog_import_run (
  run_id        UUID PRIMARY KEY,
  dt            DATE,
  status        VARCHAR(32),  -- INGESTING | PARSING | FANNING_OUT | DONE | FAILED
  total_parts   INT,
  done_parts    INT,
  failed_parts  INT,
  started_at    TIMESTAMP,
  finished_at   TIMESTAMP
);
CREATE TABLE catalog_import_partition (
  run_id        UUID,
  part_id       INT,
  status        VARCHAR(32),  -- PENDING | RUNNING | DONE | FAILED
  attempt       INT,
  last_error    TEXT,
  PRIMARY KEY (run_id, part_id)
);
```

Airflow DAG crash → 重启后读 meta DB 从 last checkpoint 继续, 不重跑已 DONE 的 partition.

---

## 5. Fan-out (Kafka)

### 5.1 Topic 设计

单一 topic `catalog-change-events`, 用 **schema-on-event** (每条消息带 schema_version). 下游 7 个 consumer group 独立消费:
- `search-indexer` (compacted)
- `ads-serving-updater`
- `feed-candidate-store-updater`
- `feature-store-updater`
- `shopping-graph-updater`
- `policy-safety-checker`
- `analytics-ingestor`

为什么 **不** 拆多 topic: (1) 7 份存储冗余 (2) 上游 producer 要写 7 次, 失败组合爆炸 (3) schema 演化要同步 7 份. 单一 topic + consumer-group 模式是 Kafka 的惯用法.

### 5.2 Partition 数 & 并行度

- Topic partition = 200 (匹配下游最高 consumer 并行度 search-indexer 的 200 个 shard writer)
- Kafka key = `catalog_id` → 同一 id 严格 FIFO, 保证 "先 create 后 delete" 不乱
- Replication = 3, min.insync.replicas = 2, acks = all
- Throughput 估算: 500M rows * 2KB = 1TB / 6h = ~47 MB/s — 轻松. 峰值 (压缩前) 100 MB/s, 200 partition 每个 ~0.5 MB/s, 单 broker 轻载.

### 5.3 Backpressure / Flow control

上游 Spark emit 速率远高于下游 consumer apply 速率 → Kafka buffer 会膨胀. 三层 backpressure:

1. **Producer 端**: `max.in.flight.requests.per.connection=5`, `linger.ms=20`, `batch.size=64KB` → 批量小 latency 低. 当 broker not-acks → 自动退避.
2. **Broker 端**: `log.retention.bytes` 限每 partition, 超出触发上游告警 (但 retention=7d 已很宽).
3. **Consumer 端**: 若 lag > threshold (e.g., 10M events), PagerDuty 叫 consumer team 扩容 / 优化 apply.

**关键: producer 不应因 consumer 慢而停止**. Kafka 的价值就是解耦 — broker 充当 shock absorber. 7 天 retention = 最长容忍 consumer 完全 down 7 天.

### 5.4 Schema evolution (Avro + Registry)

```avro
record CatalogChangeEvent {
  string catalog_id;
  string op;                    // UPSERT | DELETE
  long   version;
  int    schema_version;
  union { null, CatalogRecordV2 } before = null;
  union { null, CatalogRecordV2 } after  = null;
}
```

Schema Registry 强制 `BACKWARD` compat: 新 producer 可加 optional 字段, 不可删或改类型. Consumer 旧版本仍能解析新消息 (忽略未知字段).

---

## 6. Monitoring & SLO

### 6.1 四类核心指标

| 类别 | 指标 | 阈值 | Action |
|------|------|------|--------|
| **Ingestion** | S3 `_SUCCESS` latency (vs 02:00 expected) | >1h delay | Page seller oncall |
| | Manifest sha256 mismatch | any | Abort run, alert |
| **Partition** | failed_parts / total_parts | >1% | Page data-platform |
| | per-part p99 processing time | >15min | Investigate skew |
| **Kafka fan-out** | producer error rate | >0.1% | Page |
| | consumer lag per group | >30min worth | Page consumer team |
| | DLQ rate | >100 events/hour | Investigate schema drift |
| **Apply (下游)** | apply success rate | <99.9% | Per-team page |
| | end-to-end freshness (S3 drop → search visible) | >6h | Cross-team war-room |

### 6.2 RPO / RTO

- **Recovery Point Objective** (RPO, 恢复点目标 / 数据丢失容忍): 1 天 (因为每日全量 re-ingest, 丢一天可下一次补). 但如果连 S3 都丢, seller 需重传.
- **Recovery Time Objective** (RTO, 恢复时间目标 / 服务恢复时长): 2h. 机制: Airflow retry + partition-level replay + S3 历史保留 30 天.

### 6.3 关键 dashboard

Grafana 分 3 行:
1. **Pipeline health**: 当日 run status, per-part latency heatmap, DLQ 速率
2. **Kafka**: producer/consumer lag by group, error rate, partition skew
3. **下游 apply**: 7 个 consumer 各自 apply QPS + success rate + freshness (p50/p99)

---

## 7. Tradeoffs (interview 必考)

### 7.1 Sync vs Async ingestion

| | Sync | Async (本设计) |
|---|------|----------------|
| 延迟 | 秒级 | 小时级 |
| 吞吐 | 受限 (1TB 不现实) | 高 (S3 scale) |
| 复杂度 | 卖家复杂 (分批 + 重试) | server 复杂 (coordinator) |
| Replay | 贵 (re-send) | 便宜 (S3 重读) |
| 适用规模 | < 1M | > 1M, 日级 |

→ 500M 只能选 async. 若未来加 **delta update** (<100K/次, 准实时), 可加条 "quick-async" API: API 接收 + 写 Kafka 直接到 change-events topic, bypass S3, 5 秒内可见.

### 7.2 Exactly-once vs At-least-once

| | Exactly-once | At-least-once + idempotent (本设计) |
|---|------|------|
| 实现 | Kafka transactions + **Two-Phase Commit** (2PC, 两阶段提交) 下游 | producer idempotent + consumer 幂等 apply |
| 延迟 | 高 (transaction commit) | 低 |
| 复杂度 | 极高 (跨系统) | 中 |
| 正确性 | 真 exactly-once (消息级) | 最终 exactly-once (业务级) |
| 适用 | 金融级, 每条消息必须 1 次 | 大多数业务场景 |

→ 选 at-least-once + version-based idempotency. 500M 规模下 exactly-once 的额外复杂度与收益不匹配 — 只要下游 apply 是 `INSERT OR UPDATE WHERE incoming_version > current_version`, duplicate 无副作用.

### 7.3 Partition strategy tradeoff

Range vs Hash 见 3.1. 另一个隐藏 tradeoff: **partition 数 vs 并行度**:
- 太少 (50): 单 part 10GB, 单 task 慢, 失败重跑贵
- 太多 (5000): coordinator overhead 大, meta DB 表爆炸, Spark scheduler 开销
- 500 是 sweet spot (对齐 1GB S3 part)

### 7.4 Single topic vs per-consumer topic

单 topic (本设计): producer 写一次, schema 管理集中, storage 少. 缺点: consumer 必须自己过滤 (但本设计所有 consumer 都要所有 event, 无过滤需求).

Per-consumer topic: producer 写 7 次, 每个下游有自己的 retention + schema, 解耦更彻底. 缺点: 存储 x7, producer 失败组合复杂.

→ 选单 topic. 若未来某下游需独立 retention (e.g., warehouse 要 30d), 可加 **mirrored topic** (用 **Kafka MirrorMaker**, 跨集群镜像复制工具).

---

## 8. Failure Modes & Mitigations

| 失败 | 检测 | Mitigation |
|------|------|----------|
| 卖家 upload 半夜断连 | S3 缺 `_SUCCESS` > 1h | Alert seller, 用前一天 snapshot, 标记下游 "stale" |
| Manifest sha256 mismatch | coordinator 校验 | 拒绝本次 run, 不污染 snapshot |
| 某 part 持续失败 (脏数据) | 3 次 retry 后 FAILED | 隔离该 part, 其他 part 继续, DLQ 行级错误 |
| Schema drift (卖家加字段) | schema registry BACKWARD check | 若 compatible 自动升级, 否则拒绝 |
| Kafka broker 挂 | producer error rate spike | min.insync.replicas=2 保证可用, 自动 failover |
| 下游 consumer crash loop | lag 暴涨 + error rate | 暂停 consumer, 查 poison-pill → DLQ 该 offset 继续 |
| 下游 apply 把脏数据写入 (bad rollout) | 下游业务指标异常 | Kafka retention 7d → rewind consumer offset replay |
| 整个 pipeline 延迟 > 6h | freshness SLO 告警 | war-room, 可降级 (只 fan-out 最关键 3 个下游) |

---

## 9. Capacity Planning

- 数据量: 500M * 2KB = **1 TB/day** raw, 压缩后 ~250GB
- S3 存储: 30 天 retention = 30 * 250GB = **7.5 TB** (+ 历史 snapshot 30 天 Parquet ~150GB/day 压缩 → 4.5TB, 总 12 TB, S3 成本 < $300/mo)
- Spark: 200 executor * (4 core, 16GB) = 800 core, 3.2TB RAM. On-demand 2h/day = $500/mo
- Kafka: 1TB raw * retention 7d + replica 3 = **21 TB cluster**. 5 broker * (i3.2xlarge 1.9TB SSD) = 9.5TB? → 上 i3.4xlarge 3.8TB * 6 broker. $3000/mo
- Meta DB: 500 partition/day * 365 day = 180K rows/yr, 单 RDS t3.medium 足够.

---

## 10. Follow-ups (面试官会追问)

1. **加 realtime delta upsert** — 卖家实时改库存: 加 quick-async API → 直接写 Kafka change-events, bypass S3, 走同一 fan-out. 主 pipeline 每日做 reconciliation 兜底.
2. **Multi-region** — 卖家在 EU, 下游在 US: S3 cross-region replication + MirrorMaker 2 对 Kafka 做 topic mirror. 注意 RPO 因跨区延迟变大 (15min → 2h).
3. **GDPR delete** — 用户撤回授权: 单独 `gdpr-delete` topic, 高优先级 consumer 强制覆盖 upsert. Snapshot 里的 PII 字段做 hash.
4. **Schema 不兼容升级** (大版本) — 用 **dual-write** 过渡: producer 同时写 v1 + v2 topic, consumer 按自己节奏迁移, 双写 1 周后停 v1.
5. **下游要 point-in-time query** (e.g., "2 周前这个 product 的价格") — 保留 event log (Kafka compaction=false, 长期归档 S3), consumer 另写 temporal table (Iceberg with row-history).
6. **卖家特别大 (Amazon 级, 1B records)** — 分 sub-catalog manifest, 允许 part-level seller upload (streaming), coordinator 累积 7 天内所有 part 构成一次完整 run.
7. **Consumer apply 很慢 (search 每条要 1ms)** — consumer 内 batch + async apply, 或加一层 fan-in worker pool. Watch out: batch 不能破坏 catalog_id-FIFO 顺序.

---

## 11. 45-min 时间分配 cheat sheet

| 时间 | 内容 | 关键输出 |
|------|------|--------|
| 0-5m | Clarifying | 规模 / 频率 / 下游数 / 一致性 (4 个关键假设) |
| 5-10m | High-level arch | S3 -> coordinator -> partition workers -> Kafka -> N consumer + DLQ |
| 10-18m | Ingestion (why S3, sync vs async, manifest 协议) | S3 layout + `_SUCCESS` + async 原因 |
| 18-28m | Partitioning + retry + idempotency | hash-mod-500 + version-based idempotent + partition-level replay + DLQ |
| 28-38m | Fan-out (topic 设计 + backpressure + schema) | 单 topic + Avro + Schema Registry + per-consumer group |
| 38-43m | Monitoring + RPO/RTO + 2 个核心 tradeoff | SLO 表 + sync/async + exactly-once/at-least-once |
| 43-45m | Follow-ups (挑 2 个) | realtime delta + GDPR |

---

## 附录 A: Sync vs Quick-async vs Async 三种 API 对比

- **Sync**: `POST /catalog/bulk-upsert` 阻塞到写完. 适合 < 10K rows.
- **Quick-async**: `POST /catalog/bulk-upsert` 立刻返回 `{job_id}`, 后台 Kafka enqueue, 秒级可见. 适合 1K–100K rows, 需实时性.
- **Async (S3 bulk)**: Seller upload S3, 服务端日级 batch. 适合 1M+, 日级 SLA.

真实系统往往三路并存, 同一 event schema, 不同入口.

## 附录 B: 关键数字背诵

- 500M rows * 2KB = 1TB/day raw, 250GB 压缩
- 500 partition, 1M rows/part, 1GB 压缩/part
- Spark 200 executor, 4 core, 10min/part
- Kafka 200 partition, repl=3, retention 7d = 21TB cluster
- SLO: T+6h freshness, RPO=1d, RTO=2h
- DLQ < 100 events/hour, consumer lag < 30min
