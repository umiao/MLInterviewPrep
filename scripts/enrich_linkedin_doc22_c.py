"""Enrich LinkedIn doc#22 (System Design) -- Questions 9-11.

Adds API Design, Scalability Analysis, and Key Metrics sections
to questions 9-11. Expands remaining acronyms.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def enrich_q9_ismalicious(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q9 isMalicious API."""
    insertion = """
### API Design (API 设计)

```
# Synchronous check (on request path)
POST /api/v1/security/check
Body: {
  "request_id": "req-uuid",
  "ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "user_id": "u123",          // null for unauthenticated
  "endpoint": "/api/feed",
  "method": "GET",
  "headers": {"Accept": "...", "Referer": "..."},
  "payload_hash": "sha256:abc..."  // hash, not raw payload (privacy)
}

Response:
{
  "is_malicious": false,
  "confidence": 0.12,
  "action": "allow",           // allow | block | challenge
  "reason": null,              // "ip_blacklist" | "rate_limit" | "ml_model" | null
  "challenge_type": null       // "captcha" | "2fa" | null
}

# Rule management (admin)
POST /api/v1/security/rules      // Add/update rule
GET  /api/v1/security/rules      // List active rules
DELETE /api/v1/security/rules/{id}

# Feedback for ML model
POST /api/v1/security/feedback
Body: {"request_id": "req-uuid", "label": "malicious", "reviewed_by": "analyst-1"}
```

- check endpoint 必须 < 10ms，在 API Gateway 的 critical path (关键路径) 上
- payload 只传 hash (不传原文)，保护用户隐私
- feedback endpoint 用于人工审核后标注，改善 ML 模型

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 所有 API 请求都需要过 isMalicious 检查
- Total QPS: 假设 LinkedIn 全站 500K QPS
- 每个 check < 10ms -> 需要的 compute: 500K * 10ms = 5000 CPU-seconds/sec -> ~5000 cores (大量并行)

**Bottleneck Analysis (瓶颈分析)**:
- **延迟预算**: 10ms 内完成 Rule Engine + Rate Limiter + ML 三路并行检查
  - Rule Engine: IP/UA 黑名单查 HashSet -> < 0.1ms
  - Rate Limiter: Redis INCR + EXPIRE (Lua 原子操作) -> < 2ms
  - ML Model: Feature 构建 + inference -> < 5ms (需要预计算 features)
  - Decision Aggregator: < 0.5ms
  - 总延迟 (并行): max(Rule, Rate, ML) + Aggregator = ~6ms (ok)

- **ML Feature 计算**: 实时构建 features (如 "过去 5 分钟该 IP 的请求数") 需要 streaming infrastructure。Feature Store (Redis) 预计算这些聚合特征。

- **IP 黑名单更新**: 需要分钟级更新 (新攻击 IP 快速入库)。使用 Pub/Sub (发布/订阅) 将黑名单更新推送到所有 isMalicious 实例的本地缓存。

**Scaling Strategy (扩展策略)**:
- **Stateless check service**: 水平扩展，每个实例本地缓存 Rule Engine 规则
- **Rate Limiter**: Redis cluster，按 IP hash 分片
- **ML Model**: 使用 ONNX Runtime (开放神经网络交换格式运行时)，CPU inference，每实例本地部署模型避免 RPC (Remote Procedure Call，远程过程调用) 延迟
- **Async path**: 所有请求日志异步写 Kafka -> 用于 ML 训练和事后分析，不影响 real-time path

### Key Metrics (关键指标)

**Detection Metrics (检测指标)**:
- True positive rate / Recall (召回率): 成功检测到的恶意请求比例，目标 > 95%
- False positive rate / FPR (误报率): 正常请求被错误拦截的比例，目标 < 0.1%
- Precision (精确率): 被拦截请求中确实是恶意的比例，目标 > 90%
- F1 Score: Precision 和 Recall 的调和平均数

**Operational Metrics (运营指标)**:
- Check latency P99: 目标 < 10ms
- Rule update propagation time (规则传播时间): 从规则更新到所有实例生效，目标 < 1 min
- ML model refresh cycle: 目标每天重训练并上线
- Challenge success rate (验证成功率): 被 challenge 的用户通过验证的比例 (反映误报)

**Business Impact (业务影响)**:
- Blocked attack volume (拦截攻击量): 每天拦截的恶意请求总数
- Account takeover prevention rate (账号盗用防御率): 成功阻止的账号盗用尝试比例
- User friction rate (用户摩擦率): 正常用户被要求额外验证的比例，目标 < 0.5%

"""
    anchor = "### 面试话术\n\n> \"我会设计一个混合系统: Rule Engine 处理已知威胁"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q10_skills(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q10 LinkedIn Skills."""
    insertion = """
### API Design (API 设计)

```
# Get user skills
GET /api/v1/users/{user_id}/skills

Response:
{
  "skills": [
    {"skill_id": "s123", "name": "Machine Learning", "proficiency": "advanced",
     "endorsement_count": 42, "sources": ["experience", "endorsement", "certification"]},
    ...
  ]
}

# Trigger skill extraction for a user (internal)
POST /api/v1/skills/extract
Body: {"user_id": "u1", "text_fields": ["headline", "summary", "experience"]}

Response:
{
  "extracted_skills": [
    {"name": "Python", "confidence": 0.98, "source_field": "experience", "span": "5 years of Python"},
    {"name": "TensorFlow", "confidence": 0.85, "source_field": "summary", "span": "built models in TensorFlow"},
    ...
  ]
}

# Skill taxonomy management (admin)
GET  /api/v1/skills/taxonomy?category=Engineering
POST /api/v1/skills/taxonomy/candidates/review  // Human review of new skill candidates
```

- extract endpoint 是内部 API，由 profile update event 触发
- 返回 confidence 分数和来源字段，支持 explainability (可解释性)
- taxonomy 有层级结构: Category -> Subcategory -> Skill

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 900M+ 用户 profiles，每个 profile 平均 5 个文本字段
- Initial build (全量提取): 900M * 5 = 4.5B 个文本字段需要处理
- 增量处理: 每天约 10M 用户更新 profile -> 10M * 5 = 50M 个文本字段/天
- NER 模型推理: 每个字段平均 200 tokens，BERT-based NER 推理 ~10ms -> 50M * 10ms = ~140 GPU-hours/day

**Bottleneck Analysis (瓶颈分析)**:
- **全量处理**: 4.5B 字段 * 10ms = ~520 GPU-days -> 需要 GPU cluster + MapReduce 并行
- **NER 模型精度 vs 速度 trade-off**: BERT-based NER 准确但慢；distilled (蒸馏) 模型快但精度降低。解决: 两阶段 -- 快速模型做初筛 + 精确模型做 verify
- **新技能发现延迟**: 新兴技能 (如 "RAG (Retrieval-Augmented Generation，检索增强生成)") 从出现到被发现，依赖于频率监控的灵敏度

**Scaling Strategy (扩展策略)**:
- **Batch processing**: 全量和每日增量处理使用 Spark/Flink batch job，按 user_id range 分 partition
- **Model serving**: GPU cluster with Triton Inference Server，支持 dynamic batching (动态批处理)
- **Taxonomy**: 使用 graph database (图数据库) 存储 skill taxonomy 的层级关系，支持快速查询 "子技能" 和 "相关技能"
- **Caching**: 用户的 extracted skills 缓存在 Redis 中，profile 变更时 invalidate (使缓存失效)

### Key Metrics (关键指标)

**Model Metrics (模型指标)**:
- Precision (精确率): 提取出的 skill 确实是 skill 的比例，目标 > 90%
- Recall (召回率): 真实 skill 被成功提取的比例，目标 > 80%
- F1 Score: 综合 Precision 和 Recall，目标 > 0.85
- New skill discovery rate (新技能发现率): 每月成功加入 taxonomy 的新技能数量

**System Metrics (系统指标)**:
- Extraction pipeline latency: 从 profile 更新到 skill 列表更新的时间，目标 < 1 hour
- Throughput: NER 推理吞吐量 (texts/sec)
- GPU utilization: 目标 > 70%

**Business Metrics (业务指标)**:
- Skill coverage (技能覆盖率): 有 >= 3 个 extracted skills 的用户比例
- Endorsement correlation (背书相关性): extracted skills 与用户收到的 endorsement 的重叠度
- Job matching improvement (职位匹配提升): 使用 extracted skills 后的 job recommendation 点击率提升

"""
    anchor = "### 面试话术\n\n> \"LinkedIn Skills 是一个 data mining 问题，我会分三个阶段设计。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def enrich_q11_inverted_search(content: str) -> str:
    """Add API Design, Scalability, Metrics to Q11 Inverted Document Search."""
    insertion = """
### API Design (API 设计)

```
# Search documents
GET /api/v1/search?q=orange+juice&limit=20&offset=0&sort=relevance

Response:
{
  "results": [
    {"doc_id": 13, "score": 0.92, "snippet": "...fresh orange juice recipe..."},
    {"doc_id": 25, "score": 0.88, "snippet": "...organic orange juice brand..."},
    {"doc_id": 99, "score": 0.75, "snippet": "...orange juice benefits..."},
  ],
  "total": 3,
  "query_time_ms": 12
}

# Index a document
POST /api/v1/documents
Body: {"doc_id": 1001, "content": "This is a new document about orange farming.", "metadata": {"author": "...", "category": "..."}}

# Bulk index (offline)
POST /api/v1/documents/bulk
Body: {"documents": [{"doc_id": 1001, "content": "..."}, ...]}
```

- 搜索结果包含 snippet (摘要片段) 和 relevance score
- 支持分页 (offset/limit) 和排序方式 (relevance / recency)
- bulk index 用于全量构建或批量导入

### Scalability Analysis (可扩展性分析)

**Capacity Estimation (容量估算)**:
- 10B 文档，平均每个文档 1000 个 unique terms
- Inverted index size: 10B docs * 1000 terms * (8 bytes per doc_id entry) = ~80 TB
- 压缩后 (delta + VarInt encoding): ~16-25 TB
- Query QPS: 假设 100K QPS

**Bottleneck Analysis (瓶颈分析)**:
- **Posting list intersection**: 热门词 (如 "the") 的 posting list 可能有数十亿条 doc_id。优化:
  - Stop word (停用词) 过滤: 常见词不建索引
  - Skip pointers 间隔: sqrt(n) 或 128 个元素设一个 skip pointer
  - SIMD (Single Instruction, Multiple Data，单指令多数据流) 加速: 利用 CPU 向量指令加速 sorted merge

- **分布式 fan-out**: query 广播到 N 个 shard，coordinator 等最慢的 shard -> tail latency 问题。优化:
  - Hedged requests (对冲请求): 同时发给同一 shard 的两个 replica，取先返回的
  - Timeout + partial results: 如果某个 shard 超时，返回部分结果 + 提示

- **Index 更新延迟**: 新文档从写入到可搜索的延迟。解决: 使用 near-realtime (NRT，近实时) index -- 新文档先写入内存 buffer，每秒 flush 一次到 searchable segment

**Scaling Strategy (扩展策略)**:
- **Document partitioning**: 按 doc_id range 分 shard (已在正文讨论)
- **Index 存储**: 每个 shard 的 inverted index 放 SSD (Solid State Drive，固态硬盘)，热门 posting lists 缓存到内存
- **Query routing**: 根据 query terms 预判哪些 shards 可能有结果 (partition pruning，分区裁剪)，减少 fan-out
- **Tiered index**: 将 index 分为 hot tier (SSD, 最近 30 天文档) 和 warm tier (HDD/S3, 历史文档)

### Key Metrics (关键指标)

**Search Quality (搜索质量)**:
- Precision@10 (前 10 个结果的精确率): 目标 > 0.8
- Recall@100: 目标 > 0.9
- MRR (Mean Reciprocal Rank): 用户第一次点击结果的排名倒数
- Zero-result rate (无结果率): 目标 < 2%

**Performance Metrics (性能指标)**:
- Query latency P50/P99: 目标 P50 < 20ms, P99 < 100ms
- Indexing throughput: 新文档的索引速度 (docs/sec)
- Index freshness (索引新鲜度): 从文档写入到可搜索的延迟，目标 < 1s (NRT)

**System Metrics (系统指标)**:
- Index size on disk: 压缩率目标 > 3x
- Cache hit rate for posting lists: 目标 > 90% for hot terms
- Shard balance (分片均衡度): 各 shard 的文档数量和查询负载的标准差

"""
    anchor = "### 面试话术\n\n> \"倒排索引的核心是 posting list 的 intersection。"
    if anchor in content:
        content = content.replace(anchor, insertion + anchor)
    return content


def main() -> None:
    """Enrich doc#22 questions 9-11."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id = 22")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#22 not found", file=sys.stderr)
        sys.exit(1)

    content = row[0]
    original_len = len(content)

    content = enrich_q9_ismalicious(content)
    content = enrich_q10_skills(content)
    content = enrich_q11_inverted_search(content)

    cur.execute("UPDATE company_documents SET content = ? WHERE id = 22", (content,))
    conn.commit()

    new_len = len(content)
    print(f"Doc#22 enriched (Q9-Q11): {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    conn.close()


if __name__ == "__main__":
    main()
