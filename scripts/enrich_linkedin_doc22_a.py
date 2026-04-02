"""Enrich LinkedIn doc#22 (System Design) -- Questions 1-4.

Adds API Design, Scalability Analysis, and Key Metrics sections
to questions 1-4. Expands remaining acronyms.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def enrich_q1_typeahead(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q1 Typeahead."""
    insertion = """
### API Design (API 设计)

```
# Core endpoint
GET /api/v1/typeahead/suggest?query={prefix}&limit={K}&user_id={uid}

Response:
{
  "suggestions": [
    {"text": "software engineer", "type": "job_title", "score": 0.95},
    {"text": "Software Development", "type": "skill", "score": 0.88},
    ...
  ],
  "latency_ms": 12
}

# Admin/offline endpoints
POST /api/v1/typeahead/index/rebuild   # Trigger trie rebuild
GET  /api/v1/typeahead/health          # Health check
```

- query 参数支持 Unicode (UTF-8 encoding)，实现多语言搜索
- limit 默认 5，最大 20
- 返回结果包含 type 字段区分不同类别（人名、公司、职位、技能）

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 假设 500M 用户，平均每人每天 10 次搜索，每次搜索平均输入 5 个字符
- QPS (Queries Per Second，每秒查询数) = 500M * 10 * 5 / 86400 = ~290K QPS
- Peak QPS = 3x average = ~870K QPS

**Bottleneck Analysis (瓶颈分析)**:
- **内存**: Trie 存储所有候选词 + top-K precomputation。假设 10M 唯一搜索词，平均长度 20 bytes，Trie 节点开销约 100 bytes -> ~1GB per shard。可控。
- **网络**: 每个请求/响应约 500 bytes，870K QPS -> ~435 MB/s。需要多台 serving 节点 + load balancer (LB，负载均衡器)。
- **Trie 更新**: 热门搜索词的变化不频繁，每小时 rebuild 一次足够。使用 blue-green deployment (蓝绿部署): 新 Trie 构建完成后原子切换。

**Scaling Strategy (扩展策略)**:
- **Horizontal scaling (水平扩展)**: 按 prefix 首字母分片到不同 shard，每个 shard 独立提供查询服务
- **Read replicas (读副本)**: 热门 prefix shard 增加副本数
- **CDN (Content Delivery Network，内容分发网络) caching**: 对最热门的 prefix 结果做 edge caching，减少回源请求
- **Graceful degradation (优雅降级)**: 当系统过载时，fallback 到全局热门词，跳过个性化排序

### Key Metrics (关键指标)

**System Metrics (系统指标)**:
- P50/P99 latency (延迟): 目标 P50 < 20ms, P99 < 100ms
- QPS throughput (吞吐量): 每秒成功处理的查询数
- Trie rebuild duration (重建耗时): 目标 < 10 min
- Cache hit rate (缓存命中率): 目标 > 95%

**Business Metrics (业务指标)**:
- CTR (Click-Through Rate，点击率): 用户点击建议结果的比率
- MRR (Mean Reciprocal Rank，平均倒数排名): 用户最终选择的结果在建议列表中的位置倒数
- Suggestion acceptance rate (建议采纳率): 用户接受补全建议而非自行输入的比例
- Zero-result rate (无结果率): 无法返回任何建议的查询比例，目标 < 5%

"""
    anchor = "### 面试话术\n\n> \"我会从两个维度来设计这个系统: serving path 和 data pipeline。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q2_recommendation(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q2 Recommendation System."""
    insertion = """
### API Design (API 设计)

```
# Feed request
GET /api/v1/feed/videos?user_id={uid}&count={N}&session_id={sid}

Response:
{
  "videos": [
    {"video_id": "v123", "creator": "user456", "score": 0.92, "reason": "similar_to_liked"},
    ...
  ],
  "session_context": {"refresh_count": 3}
}

# Feedback reporting
POST /api/v1/feed/feedback
Body: {"user_id": "u1", "video_id": "v123", "action": "swipe_away", "watch_duration_ms": 1200}

# Real-time session signal
POST /api/v1/feed/session/signal
Body: {"session_id": "sid", "signals": [{"video_id": "v1", "action": "complete", "ts": 1234567890}]}
```

- count 默认 20，前端 prefetch 下一批
- session_id 用于追踪 session 内行为，支持实时调整
- feedback endpoint 异步写入 Kafka，不阻塞用户体验

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 10M DAU (Daily Active Users，日活跃用户)，每人每天刷 50 次 feed
- QPS = 10M * 50 / 86400 = ~5.8K QPS (read)，Peak = ~17K QPS
- 视频库: 100M 视频，每个视频 embedding 128 维 float32 = 48GB (可放入内存的 ANN (Approximate Nearest Neighbor，近似最近邻) index)

**Bottleneck Analysis (瓶颈分析)**:
- **Recall 层**: 多路召回并行，最慢的一路决定总延迟。使用 timeout + fallback: 如果某路超时，用其他路的结果补齐。
- **Ranking 模型推理**: Deep model inference 是延迟瓶颈。优化: 模型量化 (INT8)、batch inference、GPU serving (TensorRT/Triton)。
- **Feature Store 读取**: 每次 ranking 需要读取 user features + 1000 个 item features。使用 Redis cluster 做 feature store，batch get 减少 round trip。

**Scaling Strategy (扩展策略)**:
- **Recall 层**: 每路召回独立 scale，ANN index 可分 shard
- **Ranking 层**: GPU inference server 做 horizontal scale，使用 model parallelism (模型并行) 和 batch scheduling
- **Feature Store**: Redis cluster 按 user_id/item_id hash 分片
- **Pre-compute (预计算)**: 对活跃用户预计算 candidate list (每小时更新)，减少实时计算压力

### Key Metrics (关键指标)

**Online Metrics (线上指标)**:
- Video completion rate (完播率): 用户看完视频的比率，核心体验指标
- Engagement rate (互动率): (likes + comments + shares) / impressions
- Session duration (会话时长): 用户单次打开 feed 的停留时间
- Swipe-away rate (划走率): 快速划走的视频比例，越低越好

**Model Metrics (模型指标)**:
- AUC (Area Under ROC Curve，ROC 曲线下面积): 排序模型的区分能力
- NDCG (Normalized Discounted Cumulative Gain，归一化折损累计增益): 列表排序质量
- Calibration (校准度): 预测概率与实际概率的一致性

**System Metrics**:
- E2E (End-to-End) latency: 目标 P99 < 200ms
- Recall coverage (召回覆盖率): 多路召回合并后候选集的多样性
- Model freshness (模型新鲜度): 模型最近一次训练距今的时间

"""
    anchor = "### 面试话术\n\n> \"推荐系统我会用经典的多段式架构:"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q3_monitoring(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q3 Metrics Monitoring."""
    insertion = """
### API Design (API 设计)

```
# Write metrics (via SDK, batched)
POST /api/v1/metrics/ingest
Body: {
  "metrics": [
    {"name": "api.request.count", "tags": {"service": "feed", "endpoint": "/feed"},
     "value": 42, "type": "counter", "timestamp": 1234567890},
    ...
  ]
}

# Query metrics
GET /api/v1/metrics/query?name=api.request.count&tags=service:feed&start=1234567000&end=1234567890&granularity=1m

Response:
{
  "series": [
    {"timestamp": 1234567800, "value": 123.5},
    {"timestamp": 1234567860, "value": 130.2},
    ...
  ]
}

# Exception monitoring variant
GET /api/v1/exceptions/topk?k=10&window=1h&service=feed

Response:
{
  "exceptions": [
    {"type": "NullPointerException", "count": 1523, "stack_hash": "abc123",
     "sample_message": "...", "first_seen": "...", "last_seen": "..."},
    ...
  ]
}
```

- ingest endpoint 支持 batch (批量) 上传减少 HTTP overhead
- query endpoint 的 granularity 参数控制返回数据的时间粒度 (1s/1m/1h/1d)
- topk endpoint 的 window 参数支持 1m/5m/1h/1d/7d

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 10K 台机器，每台每秒上报 100 个 metric data points
- Write QPS = 10K * 100 = 1M data points/sec
- 每个 data point 约 100 bytes -> 写入吞吐 ~100 MB/s
- 存储: 保留 30 天高精度数据 -> 1M * 100B * 86400 * 30 = ~250 TB (需降采样)

**Bottleneck Analysis (瓶颈分析)**:
- **写入吞吐**: 1M points/sec 是 TSDB (Time Series Database，时序数据库) 写入的主要挑战。解决: Agent 端预聚合 (10s 窗口) 可将写入量降低 10x
- **高基数 (High Cardinality)**: 当 tag 组合数量爆炸时（如 user_id 作为 tag），索引膨胀。限制: 禁止高基数 tag，或使用 sampling
- **查询热点**: 所有人看同一个 dashboard -> 缓存查询结果 (TTL (Time To Live，存活时间) = 10s)

**Scaling Strategy (扩展策略)**:
- **写入**: Kafka partition 按 metric_name hash，消费端 sharded aggregation workers
- **存储**: TSDB 按时间分区 (如每天一个 partition)，旧分区自动降采样后迁移到冷存储 (如 S3/HDFS)
- **查询**: 查询 fan-out 到多个存储 shard，parallel merge 结果

### Key Metrics (关键指标)

**System Health (系统健康度)**:
- Ingestion lag (摄入延迟): 从 metric 产生到可查询的时间差，目标 < 30s
- Write success rate (写入成功率): 目标 > 99.99%
- Query P99 latency: 目标 < 1s for 1-hour window queries
- Data completeness (数据完整性): 实际写入 vs 预期写入的比率

**Exception Monitoring Metrics**:
- Detection latency (异常检测延迟): 从异常发生到出现在 top-K dashboard 的时间
- Alert precision (告警精准率): 有意义的告警 / 总告警数
- MTTD (Mean Time To Detect，平均检测时间): 从问题发生到被发现的平均时间

"""
    anchor = "### 面试话术\n\n> \"这个系统的核心挑战是高吞吐写入和灵活的多维查询。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q4_scheduler(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q4 Job Scheduler."""
    insertion = """
### API Design (API 设计)

```
# Create a scheduled task
POST /api/v1/tasks
Body: {
  "task_type": "recurring",
  "cron_expression": "0 9 * * 1",
  "payload": {"url": "https://internal-api/run-report", "method": "POST"},
  "priority": 5,
  "max_retries": 3,
  "idempotency_key": "weekly-report-team-abc"
}

Response: {"task_id": "uuid-123", "next_execution_time": "2026-04-07T09:00:00Z"}

# Query upcoming tasks (dashboard follow-up)
GET /api/v1/tasks/upcoming?hours=4&status=scheduled&limit=100&offset=0

Response: {
  "tasks": [
    {"task_id": "uuid-123", "next_execution_time": "...", "priority": 5, "status": "scheduled"},
    ...
  ],
  "total_count": 342
}

# Task status
GET /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}     # Cancel a task
POST /api/v1/tasks/{task_id}/pause  # Pause a recurring task
POST /api/v1/tasks/{task_id}/resume
```

- idempotency_key 防止重复创建（客户端重试安全）
- upcoming endpoint 就是 follow-up question 的核心: 利用 B-Tree index 高效查询
- pause/resume 针对 recurring task，暂停后不计算新的 next_execution_time

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 1M 个定时任务，其中 100K 是 recurring (分钟/小时级)
- 每分钟触发的任务数: 假设均匀分布，100K 个 recurring tasks / 平均 60min 间隔 = ~1.7K 任务/min
- Peak: 整点 (如每小时第0分钟) 触发量可能是平均的 10x = ~17K 任务/min

**Bottleneck Analysis (瓶颈分析)**:
- **DB Polling**: 每分钟扫描即将到期的任务，如果任务量大，扫描可能慢。优化: B-Tree index on (next_execution_time, status) 保证 range scan 高效
- **整点风暴 (Thundering Herd)**: 大量 cron job 设置在整点执行 -> 瞬时负载激增。解决: 自动 jitter (抖动): 在 next_execution_time 上加随机 0-30s 偏移，打散执行时间
- **Worker 容量**: 如果任务执行时间长，Worker 可能被占满。解决: 异步执行 + 超时机制 + Worker auto-scaling (自动扩容)

**Scaling Strategy (扩展策略)**:
- **Scheduler**: 多实例 + 分布式锁 (ZooKeeper/Redis) 保证只有一个实例执行 polling
- **Task Store**: DB sharding by task_id hash range。或按 next_execution_time range 分区 (时间分区)
- **Worker Pool**: 按任务类型分 queue，不同 queue 独立扩容 (如 HTTP callback queue vs heavy computation queue)
- **二级调度**: Scheduler 只负责把任务推入 queue，Worker 自行从 queue pull -- 解耦调度和执行

### Key Metrics (关键指标)

**Reliability Metrics (可靠性指标)**:
- Task execution rate (任务执行率): 成功执行的任务 / 总调度任务，目标 > 99.9%
- Schedule accuracy (调度精度): 实际执行时间与预定时间的偏差，目标 P99 < 5s
- Duplicate execution rate (重复执行率): 同一任务被执行多次的比率，目标 0%
- Retry success rate (重试成功率): 重试后成功的比例

**Performance Metrics (性能指标)**:
- Polling cycle time: DB scan + enqueue 的耗时，目标 < 5s per cycle
- Queue depth (队列深度): Priority Queue 中等待执行的任务数量
- Worker utilization (Worker 利用率): 忙碌 Worker / 总 Worker，目标 60-80%
- Task execution latency: 任务从入队到开始执行的等待时间

"""
    anchor = "### 面试话术\n\n> \"我会把 Job Scheduler 分为调度层和执行层。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def main() -> None:
    """Enrich doc#22 questions 1-4."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id = 22")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#22 not found", file=sys.stderr)
        sys.exit(1)

    content = row[0]
    original_len = len(content)

    content = enrich_q1_typeahead(content)
    content = enrich_q2_recommendation(content)
    content = enrich_q3_monitoring(content)
    content = enrich_q4_scheduler(content)

    cur.execute("UPDATE company_documents SET content = ? WHERE id = 22", (content,))
    conn.commit()

    new_len = len(content)
    print(f"Doc#22 enriched (Q1-Q4): {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    conn.close()


if __name__ == "__main__":
    main()
