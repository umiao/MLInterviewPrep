"""Enrich LinkedIn doc#22 (System Design) -- Questions 5-8.

Adds API Design, Scalability Analysis, and Key Metrics sections
to questions 5-8. Expands remaining acronyms.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def enrich_q5_kvstore(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q5 KV Store."""
    insertion = """
### API Design (API 设计)

```python
class KVStore:
    def put(self, key: bytes, value: bytes) -> None:
        \"\"\"Write key-value pair. Append to active segment, update index.\"\"\"

    def get(self, key: bytes) -> Optional[bytes]:
        \"\"\"Read value by key. Returns None if key not found or deleted.\"\"\"

    def delete(self, key: bytes) -> None:
        \"\"\"Delete key by appending tombstone marker.\"\"\"

    def compact(self) -> None:
        \"\"\"Background compaction: merge old segments, remove tombstones.\"\"\"

    def recover(self) -> None:
        \"\"\"Crash recovery: rebuild index from hint file + segment replay.\"\"\"
```

- 单机系统，不需要 REST API -- 提供 library-level interface
- put/get/delete 是面试讨论的核心，API 简单但实现细节丰富
- compact 应该是后台线程自动执行，不阻塞读写
- recover 在进程重启时自动调用

### Scalability Analysis (单机性能优化)

**Capacity Estimation (容量估算)**:
- 1 billion keys，平均 key size = 32 bytes，平均 value size = 1 MB
- 总数据量 = 1B * 1MB = ~1 PB -- 单机显然放不下这么多数据
- 面试中需要澄清: "1 billion keys 是总 key 空间，活跃数据可能远小于此"
- Index size: 1B * (32B key + 16B metadata) = ~48 GB -- 这是内存的主要挑战

**Bottleneck Analysis (瓶颈分析)**:
- **内存索引过大**: 48 GB HashMap 可能超出单机内存。解决方案:
  - LSM-tree (Log-Structured Merge-tree，日志结构合并树): memtable (内存表) 限制在 64MB，满了 flush 到磁盘 SSTable (Sorted String Table，有序字符串表)
  - Bloom Filter (布隆过滤器): 每个 SSTable 配一个 Bloom Filter，查询时先检查 key 是否可能在该 SSTable 中，避免无效磁盘读
  - Bloom Filter 参数: 1% FPR (False Positive Rate，误报率)，每个 key 约 10 bits -> 1B keys = ~1.2 GB，可接受

- **写放大 (Write Amplification)**: Compaction 过程中，同一份数据被反复读写。LSM-tree 的写放大通常在 10-30x。优化: leveled compaction 比 size-tiered compaction 写放大更低

- **读放大 (Read Amplification)**: 如果 key 不在 memtable 中，可能需要查多层 SSTable。优化:
  - Bloom Filter 排除大部分不包含该 key 的 SSTable
  - Block cache (块缓存): 缓存热门 SSTable 的 data blocks
  - Compaction 减少层数

**性能特征对比**:

| 操作 | Bitcask 模型 | LSM-tree 模型 |
|------|-------------|---------------|
| Write | O(1) append | O(1) amortized (memtable + flush) |
| Read (cache hit) | O(1) hash lookup + 1 disk read | O(1) memtable lookup |
| Read (cache miss) | O(1) hash lookup + 1 disk read | O(L) 查 L 层 SSTable |
| Space overhead | Index 在内存，受限 | Index 可以放磁盘 |
| 适用场景 | Key 数量适中 (< 1B) | 超大 key 空间 |

### Key Metrics (关键指标)

**Performance Metrics (性能指标)**:
- Read latency P99: Bitcask = ~1ms (1 disk seek), LSM = ~5ms (多层查找)
- Write latency P99: 两者均 < 0.1ms (顺序 append)
- Write throughput (写入吞吐): 目标 > 100K ops/sec (受限于 fsync 频率)
- Read throughput: 目标 > 50K ops/sec

**Storage Metrics (存储指标)**:
- Space amplification (空间放大): 实际磁盘占用 / 有效数据量，目标 < 2x
- Write amplification: 实际磁盘写入量 / 用户写入量，目标 < 20x
- Compaction throughput: 后台 compaction 的处理速度 (MB/s)

**Reliability Metrics (可靠性指标)**:
- Recovery time (恢复时间): 从 crash 到可服务的时间。Hint file 方案: < 10s; Full scan 方案: ~10min for 1B keys
- Data durability (数据持久性): fsync policy 决定最多丢失多少数据 (per-write fsync vs batched fsync)

"""
    anchor = "### 面试话术\n\n> \"在 append-only 和单机约束下，我会采用 Bitcask 模型:"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q6_inmail(content: str) -> str:
    """Add Scalability, Metrics to Q6 InMail (already has implicit API design)."""
    insertion = """
### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- LinkedIn 有 ~50K active recruiters 使用 InMail
- 每个 recruiter 每天生成 ~20 封 InMail
- 生成 QPS = 50K * 20 / 86400 = ~12 QPS (低流量，但每个请求 compute-heavy)
- Peak: 工作日上午 10-11 点，约 5x average = ~60 QPS

**Bottleneck Analysis (瓶颈分析)**:
- **LLM 推理延迟**: 大模型生成 200 字约 2-5s。Streaming (流式输出) 让用户感知延迟降到 TTFT (Time To First Token，首 token 时间) < 500ms
- **Context 组装**: 并行调用 3 个数据源 (candidate, job, recruiter history)，取决于最慢的一个。设 timeout = 500ms + fallback 默认值
- **LLM 成本**: GPT-4 级别模型每次调用约 $0.03-0.10。Fine-tuned 小模型每次 < $0.005
- **并发 LLM 请求**: 60 QPS * 3s per request = ~180 concurrent LLM requests -> 需要 GPU cluster 或 API rate limit management

**Scaling Strategy (扩展策略)**:
- **模型分层**: 简单消息用 fine-tuned 7B 模型 (低成本、低延迟)，复杂/高价值候选人用大模型
- **Prompt caching (提示缓存)**: 同一 recruiter 对同一职位的 system prompt + job info 部分可以缓存，减少 token 消耗
- **Batch generation (批量生成)**: Recruiter 可以选择多个候选人批量生成，后台队列处理
- **A/B testing framework**: 支持同时运行多个 prompt 版本和模型版本的对比实验

### Key Metrics (关键指标)

**Quality Metrics (质量指标)**:
- Reply rate (回复率): 收到 AI-generated InMail 的候选人的回复比例，核心业务指标
- Edit distance (编辑距离): Recruiter 编辑 AI 草稿的改动量，越少说明生成质量越好
- Factual accuracy (事实准确率): 生成内容中引用候选人信息的准确率，人工抽检
- Tone compliance (语气合规率): 生成内容是否符合 recruiter 选择的 tone

**System Metrics (系统指标)**:
- TTFT (Time To First Token): 目标 < 500ms
- E2E generation time (端到端生成时间): 目标 < 5s for 200 words
- LLM cost per InMail: 目标 < $0.01 (fine-tuned model)
- Retrieval pipeline latency: 3 个数据源的 P99 响应时间

**Safety Metrics (安全指标)**:
- PII (Personally Identifiable Information，个人可识别信息) leak rate: AI 泄露非目标候选人信息的比率，目标 0%
- Content safety violation rate: 生成歧视性/不当内容的比率
- Hallucination rate (幻觉率): 生成不存在的候选人经历的比率

"""
    anchor = "### 面试话术\n\n> \"我会用 retrieval pipeline + LLM generation 的架构。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q7_topk(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q7 Top K Search Words."""
    insertion = """
### API Design (API 设计)

```
# Query top-K search words
GET /api/v1/search/topk?k=10&window=1h

Response:
{
  "window": "1h",
  "timestamp": "2026-04-01T10:00:00Z",
  "top_words": [
    {"word": "machine learning", "count": 152340, "trend": "rising"},
    {"word": "software engineer", "count": 148200, "trend": "stable"},
    ...
  ]
}

# Ingest search event (internal, from search service)
POST /api/v1/search/events
Body: {"query": "machine learning", "user_id": "u1", "timestamp": 1234567890}
```

- window 支持 5m/15m/1h/6h/1d/7d
- trend 字段表示该词频率相对前一个同等窗口的变化趋势
- 内部 ingest endpoint 走 Kafka，这里是 backup/debug 用

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 1M search QPS
- 每个搜索事件约 100 bytes -> Kafka 吞吐 ~100 MB/s
- 唯一搜索词数量: 假设 10M 不同的搜索词（long tail 分布）
- CMS (Count-Min Sketch，计数最小草图) 空间: w=10000, d=7, 每个 counter 4 bytes = 280 KB per bucket
- 60 个 1-min buckets (1 小时窗口) = ~16.8 MB total -- 极其紧凑

**Bottleneck Analysis (瓶颈分析)**:
- **Kafka consumer throughput**: 1M events/sec，单个 consumer 处理不过来。解决: 多 partition + consumer group，每个 consumer 处理 ~100K events/sec
- **CMS accuracy vs memory**: CMS 的误差 epsilon = e/w (e 是自然常数)。w=10000 时 epsilon ~= 0.027%，对 top-K 来说精度足够
- **Window 合并**: 查询 "past 1 hour" 需要合并 60 个 min-buckets 的 CMS。优化: 预计算常用窗口 (5m, 15m, 1h) 的 merged CMS

**Scaling Strategy (扩展策略)**:
- **Horizontal partitioning**: 按 search word 首字母 hash 分 partition，每个 partition 独立维护 CMS + Heap
- **Hierarchical aggregation (层级聚合)**: 每台 Flink worker 维护局部 top-K，定期汇总到 coordinator 做全局 top-K
- **Approximate 兜底**: 如果要求精确 top-K，可以用两阶段: Phase 1 用 CMS 找 candidate set (top-2K)，Phase 2 对 candidates 精确计数

### Key Metrics (关键指标)

**Accuracy Metrics (精度指标)**:
- Top-K precision (精确率): 近似 top-K 与精确 top-K 的重叠比例，目标 > 95%
- Count error rate (计数误差率): CMS 估算频率与真实频率的偏差，目标 < 5%
- Rank correlation (排名相关性): 近似排名与精确排名的 Spearman correlation，目标 > 0.95

**System Metrics (系统指标)**:
- Processing latency: 从搜索事件发生到 top-K 更新的延迟，目标 < 30s
- Memory usage: CMS + Heap 的总内存占用，目标 < 100 MB
- Dashboard refresh latency: Redis 读取 top-K 的响应时间，目标 < 10ms

"""
    anchor = "### 面试话术\n\n> \"核心挑战是在大规模流数据上做实时 top-K 统计。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q8_ranking(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q8 Ranking System."""
    insertion = """
### API Design (API 设计)

```
# Job search with ranking
GET /api/v1/jobs/search?query=ML+Engineer&location=San+Francisco&page=1&size=20

Response:
{
  "results": [
    {"job_id": "j123", "title": "Senior ML Engineer", "company": "LinkedIn",
     "relevance_score": 0.95, "freshness_days": 2, "salary_range": "$180K-$250K"},
    ...
  ],
  "total": 1245,
  "facets": {"seniority": {"senior": 340, "mid": 620, ...}, "remote": {"yes": 400, ...}}
}

# Feedback for model training
POST /api/v1/jobs/feedback
Body: {"user_id": "u1", "job_id": "j123", "action": "apply", "position": 3}
```

- facets 返回聚合信息，用于 UI 上的 filter 面板
- feedback 中的 position 字段记录用户点击/申请的 job 在列表中的位置 (用于训练 LTR (Learning To Rank，学习排序) 模型)
- 支持 filter 参数: salary_min, salary_max, remote_only, posted_within_days

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 20M job postings (活跃)，500M 用户
- Search QPS: 假设 10M DAU，每人每天 5 次搜索 -> ~580 QPS，Peak ~1.7K QPS
- 每次搜索: Retrieval 从 ES (ElasticSearch) 返回 ~500 candidates，Ranking model 对 500 个打分

**Bottleneck Analysis (瓶颈分析)**:
- **Feature 构建延迟**: 每次 ranking 需要为 500 个 (user, job) pair 构建特征向量。批量从 Feature Store 获取: 1 次 user features + 500 次 job features -> batch get 优化到 < 10ms
- **Model inference**: LambdaMART (500 samples) < 5ms; Neural LTR 可能 20-50ms -> 需要模型量化或 GPU inference
- **ES 查询**: 全文搜索 + 多条件 filter，复杂查询可能 > 50ms -> 优化 ES index schema，pre-filter 减少候选

**Scaling Strategy (扩展策略)**:
- **Retrieval**: ES cluster sharded by job_id range, read replicas for hot queries
- **Feature Store**: Redis cluster，user features 和 job features 分开存储，独立扩容
- **Model Serving**: 使用 TF Serving / Triton，horizontal scale GPU workers
- **Result Cache**: 对相同 query + filters 的搜索结果缓存 (TTL = 5 min)，减少重复计算

### Key Metrics (关键指标)

**Business Metrics (业务指标)**:
- Apply rate (申请率): 搜索结果页面的申请转化率
- NDCG@10 (前 10 个结果的归一化折损累计增益): 排序质量的核心离线指标
- MRR (Mean Reciprocal Rank，平均倒数排名): 用户第一次点击的位置倒数
- Job fill rate (职位填充率): 通过搜索推荐成功招到人的职位比例

**Model Metrics (模型指标)**:
- Offline AUC: 目标 > 0.75
- Online A/B test: apply rate lift > 2% 才上线新模型
- Feature importance (特征重要性): 定期审查，淘汰贡献低的特征

**System Metrics (系统指标)**:
- E2E search latency P99: 目标 < 200ms (含 retrieval + ranking + re-ranking)
- Ranking model P99 latency: 目标 < 30ms
- Feature Store P99 latency: 目标 < 10ms

"""
    anchor = "### 面试话术\n\n> \"Job ranking 的核心是 feature engineering 和 Learning to Rank。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def main() -> None:
    """Enrich doc#22 questions 5-8."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id = 22")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#22 not found", file=sys.stderr)
        sys.exit(1)

    content = row[0]
    original_len = len(content)

    content = enrich_q5_kvstore(content)
    content = enrich_q6_inmail(content)
    content = enrich_q7_topk(content)
    content = enrich_q8_ranking(content)

    cur.execute("UPDATE company_documents SET content = ? WHERE id = 22", (content,))
    conn.commit()

    new_len = len(content)
    print(f"Doc#22 enriched (Q5-Q8): {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    conn.close()


if __name__ == "__main__":
    main()
