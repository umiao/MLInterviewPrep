"""Populate interview-search-autocomplete system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design Search Autocomplete
(Typeahead) -- real-time prefix-based query suggestions with ranking, caching,
and data collection pipeline. Idempotent: creates record if missing, overwrites existing.

Chinese translation with English technical terms preserved (bold + first-use
explanation). Formulas and code blocks kept as-is.
"""
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "interview-search-autocomplete"
TITLE = "Design Search Autocomplete"
DISPLAY_ORDER = 109

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个类似 **Google Search / Bing / Amazon** 的**搜索自动补全系统 (Search
Autocomplete / Typeahead)**。当用户在搜索框中输入字符时，系统实时返回以当前
输入为前缀的热门查询建议列表（通常 5-10 条），帮助用户快速完成输入、减少拼写
错误、引导用户发现热门内容。

### 功能性需求 (Functional Requirements)

1. **前缀匹配建议 (Prefix Suggestions)**: 用户每输入一个字符，系统返回以当前
   输入为前缀的 top-K (K=5~10) 热门查询建议
2. **排序与排名 (Ranking)**: 建议按照综合得分排序，考虑查询频率、时效性、
   个性化因素和趋势热度
3. **数据收集 (Data Collection)**: 持续收集用户搜索查询，更新查询频率统计，
   反映最新热点趋势
4. **多语言支持 (Multi-language)**: 支持英文、中文、日文等多语言前缀匹配
5. **不雅过滤 (Profanity Filter)**: 过滤掉不适合展示的查询建议（色情、暴力、
   仇恨言论）

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.99% -- 搜索自动补全是用户体验的入口，不可用
  直接影响搜索流量和收入
- **延迟 (Latency)**: P99 < 100ms -- 超过 100ms 用户感知到明显延迟，
  200ms 以上用户开始放弃自动补全直接按回车搜索
- **吞吐量 (Throughput)**: 峰值 100K+ QPS (每次按键触发一次请求，
  假设 10 亿 DAU，平均每用户 6 次搜索，每次搜索 4 次按键触发)
- **一致性 (Consistency)**: **最终一致 (Eventually Consistent)**。新的热门查询
  出现后，允许几分钟延迟才反映在建议中。非实时一致性对用户体验影响极小
- **可扩展性 (Scalability)**: 支持 100 亿+ 不同查询前缀，全球部署

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 是否只需要前缀匹配，还是也需要支持中间匹配 / 模糊匹配？** -- WHY:
   纯前缀匹配可以用 **Trie (前缀树)** 高效解决 (O(p) 查找，p 为前缀长度)。
   如果需要中间匹配或拼写纠错，则需要 **Inverted Index** 或 **Edit Distance**
   计算，复杂度和延迟大幅增加。

2. **Q: 返回多少条建议？** -- WHY: K 值影响每次查询返回的数据量和排序复杂度。
   K=5 只需维护一个小堆；K=100 需要更复杂的排序和更多网络传输。

3. **Q: 建议列表需要多快更新？热点事件（如 breaking news）多久反映在建议中？**
   -- WHY: 如果需要秒级反映，必须用实时流处理 (**Flink / Kafka Streams**)
   更新 Trie。如果分钟级可接受，可以用批处理 (**MapReduce**) 定期重建。

4. **Q: 是否需要个性化？不同用户看到不同的建议？** -- WHY: 无个性化可以
   全局缓存（相同前缀 -> 相同结果，CDN 缓存友好）。个性化需要按用户维护
   查询历史，缓存命中率大幅下降。

5. **Q: 是否需要支持中文/日文等非空格分隔语言的自动补全？** -- WHY: 英文以
   空格分词，前缀匹配自然。中文没有空格分隔，需要分词器 (**Jieba / ICU**)
   预处理，且用户可能输入拼音前缀匹配汉字。

6. **Q: 查询数据的规模是多少？每天有多少不重复查询？** -- WHY: 10 亿不重复
   查询需要 ~100 GB 内存存储 Trie；如果 1000 亿则需要分片或磁盘辅助。

7. **Q: 是否需要支持付费推广建议 (Sponsored Suggestions)？** -- WHY: 如果有
   付费建议，排序逻辑需要混合自然热度和竞价排名，增加排序管道复杂度。

### 范围声明 (Out of Scope)

- 搜索结果排序 (Search Ranking) -- 只设计自动补全，不设计搜索本身
- 拼写纠错 (Spell Correction) -- "Did you mean X?" 是独立系统
- 语音搜索 (Voice Search)
- 图片搜索建议
- 广告竞价系统
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

Search Autocomplete 的核心是两条独立的管道:
1. **查询服务管道 (Query Serving Pipeline)**: 用户按键 -> 返回建议，要求超低延迟 (< 100ms)
2. **数据收集管道 (Data Collection Pipeline)**: 收集查询日志 -> 更新频率统计 -> 重建/更新 Trie，可接受分钟级延迟

两条管道通过 **Trie 数据结构** 在中间汇合：查询管道读 Trie，数据收集管道写 Trie。

### 核心服务与职责

| 服务 | 职责 |
|------|------|
| **Autocomplete Service (自动补全服务)** | 接收用户前缀查询，在 Trie 中查找 top-K 建议并返回。无状态，水平扩展 |
| **Trie Node (Trie 节点服务)** | 内存中持有 Trie 分片，提供前缀查找接口。有状态，按前缀范围分片 |
| **Data Collection Service (数据收集服务)** | 从 Kafka 消费搜索查询日志，按时间窗口聚合频率，写入 **Query Frequency Store** |
| **Trie Builder (Trie 构建器)** | 定期 (每 15 分钟或每小时) 从 Query Frequency Store 读取数据，重建 Trie 快照并分发到 Trie Node |
| **Trending Service (趋势检测服务)** | 实时检测突发查询 (如 breaking news)，将趋势查询快速注入 Trie，不等待批量重建周期 |
| **Filter Service (过滤服务)** | 维护不雅词库 / 敏感词库，对建议列表做最终过滤后再返回给用户 |
| **Personalization Service (个性化服务)** | 可选。基于用户搜索历史对建议做个性化重排 |

### 数据库选型与理由

| 数据 | 存储选型 | 理由 |
|------|----------|------|
| Trie 数据结构 | **内存 (In-Memory)** | 每次查询 < 1ms 查找时间，是延迟的核心瓶颈。Trie 序列化后持久化到 S3/HDFS 做备份 |
| 查询频率统计 | **Cassandra** 或 **DynamoDB** | 写密集型 (聚合后 ~10K writes/s)，按查询字符串做 partition key，支持按时间窗口 TTL |
| 搜索日志原始数据 | **Kafka -> HDFS/S3** | 原始查询日志写入 Kafka (高吞吐)，再 sink 到 HDFS/S3 做长期存储和离线分析 |
| 用户搜索历史 | **Redis** | 个性化所需，按 user_id 存储最近 N 条查询历史，LRU 淘汰 |
| 不雅词库 | **Redis Set** 或内存 **Bloom Filter** | 快速匹配过滤，低延迟 |
| Trie 快照 | **S3 / HDFS** | Trie 序列化后的二进制快照，用于新节点启动时加载 |

### 通信模式

- **HTTP/REST**: 客户端 -> Autocomplete Service (简单请求-响应，CDN 缓存友好)
- **gRPC**: Autocomplete Service -> Trie Node (内部低延迟通信)
- **Kafka**: 搜索日志 -> Data Collection Service -> Trie Builder (异步管道)
- **S3**: Trie Builder -> Trie Nodes (快照分发，新快照就绪后 Trie Node 拉取加载)

### Trie: 核心数据结构设计

这是 Search Autocomplete **最核心的设计**，直接决定查询延迟和内存效率。

#### 基础 Trie vs Compressed Trie

基础 Trie 每个字符一个节点，大量单子节点浪费内存。
**Compressed Trie (Patricia Trie / Radix Tree)** 将单链路径压缩为单个节点:

```
基础 Trie:          Compressed Trie:
  r                    r
  |                    |
  e                   "edis"
  |
  d
  |
  i
  |
  s
```

压缩后节点数减少 60-80%，内存占用大幅下降。

#### Trie 节点结构

```python
class TrieNode:
    children: dict[str, TrieNode]   # 子节点映射
    is_end: bool                     # 是否是完整查询的终点
    top_k: list[tuple[str, float]]   # 预计算的 top-K 建议 + 分数
    frequency: int                    # 该前缀的查询频率 (如果是完整查询)
```

关键优化: 每个节点预存 **top-K 建议列表**。这样查询时只需遍历到前缀节点，
直接返回预存的 top-K，无需遍历整棵子树。

#### 查询时间复杂度

- **不带 top-K 预存**: O(p) 定位前缀节点 + O(n) 遍历子树收集所有查询 + O(n log K) 排序取 top-K
  (n 为子树中的查询数量，可能很大)
- **带 top-K 预存**: O(p) 定位前缀节点 + O(1) 返回预存结果
  代价: 更新 Trie 时需要自底向上传播更新 top-K，构建时间增加

#### Trie 分片策略

单台机器内存有限，需要将 Trie 分布到多台机器:

- **按前缀范围分片**: Shard 1 = [a-f], Shard 2 = [g-n], Shard 3 = [o-z]
- **不均匀分布处理**: 某些前缀 (如 "s", "c") 查询量远大于其他，
  用**一致性哈希 (Consistent Hashing)** 按热度动态分片
- **每个分片 2-3 副本** 提供高可用，读请求在副本间负载均衡

### 缓存策略 (多级缓存)

这是延迟优化的**第二大关键**:

1. **浏览器缓存**: 短 TTL (60s)，相同前缀 60s 内不重复请求
2. **CDN 缓存**: 热门前缀 (如 "how to", "what is") 的结果缓存在 CDN 边缘节点，
   TTL 5 分钟。命中率可达 30-40% (头部查询高度集中)
3. **Application Cache (Redis/Memcached)**: Autocomplete Service 前置缓存，
   缓存最近 100 万个查询前缀的结果，TTL 15 分钟
4. **Trie 内存**: 最后一级，直接内存查找 < 1ms

请求命中顺序: 浏览器 -> CDN -> Application Cache -> Trie Node
"""

# ---------------------------------------------------------------------------
# S3: API Design + Data Flow
# ---------------------------------------------------------------------------
DATAFLOW = r"""## API 设计与数据流 (API Design & Data Flow)

### 自动补全 API

```
GET /v1/autocomplete?prefix=how+to+m&limit=5&lang=en&user_id=u123
Authorization: Bearer <token>

Response: 200 OK
{
  "prefix": "how to m",
  "suggestions": [
    {"query": "how to make money online", "score": 0.95, "type": "trending"},
    {"query": "how to make pasta", "score": 0.88, "type": "popular"},
    {"query": "how to meditate", "score": 0.82, "type": "popular"},
    {"query": "how to motivate yourself", "score": 0.75, "type": "personalized"},
    {"query": "how to meal prep", "score": 0.71, "type": "popular"}
  ],
  "took_ms": 12
}
```

使用 **GET** 而非 POST，因为:
- GET 请求可以被 CDN 和浏览器缓存
- 查询是幂等的只读操作
- URL 参数便于调试和日志分析

### 搜索日志上报 API

```
POST /v1/search/log
Authorization: Bearer <token>

Request Body:
{
  "query": "how to make pasta",
  "session_id": "sess_abc123",
  "selected_suggestion_index": 2,
  "characters_typed": 8,
  "timestamp": "2024-01-15T10:30:00Z"
}

Response: 202 Accepted
```

记录用户最终搜索的完整查询及是否选择了建议。这些数据反馈到数据收集管道，
用于更新查询频率。

### 核心数据模型

#### 查询频率表 (Cassandra)

```sql
CREATE TABLE query_frequency (
    query_prefix  TEXT,            -- 查询字符串 (也是前缀的终点)
    time_window   TEXT,            -- e.g., "2024-01-15T10" (1h window)
    frequency     COUNTER,         -- 该窗口内的查询次数
    PRIMARY KEY (query_prefix, time_window)
) WITH default_time_to_live = 7776000;  -- 90 days TTL
```

#### 趋势查询表

```sql
CREATE TABLE trending_queries (
    query_text    TEXT,
    detected_at   TIMESTAMP,
    score         DOUBLE,          -- 趋势分数 (增长速率)
    category      TEXT,            -- news, entertainment, sports, etc.
    PRIMARY KEY (query_text)
) WITH default_time_to_live = 86400;   -- 24h TTL
```

### 读路径: 用户按键到建议返回

```
Step 1: 用户在搜索框输入 "how to m"
Step 2: 前端 debounce 50-100ms 后发起 GET /v1/autocomplete?prefix=how+to+m
Step 3: CDN 检查缓存 (命中则直接返回, TTL 5min)
Step 4: Autocomplete Service 查 Application Cache (Redis, TTL 15min)
Step 5: Cache miss -> 根据前缀首字母路由到对应 Trie Node 分片
Step 6: Trie Node 执行前缀查找, O(p) 遍历到 "how to m" 节点
Step 7: 返回该节点预存的 top-K 建议列表
Step 8: (可选) Personalization Service 基于 user_id 重排
Step 9: Filter Service 过滤不雅建议
Step 10: 结果写入 Application Cache, 返回给客户端
```

端到端延迟预算:
- CDN / 浏览器缓存命中: < 5ms
- Application Cache 命中: ~10ms (网络 RTT)
- Trie Node 查询: ~1ms (内存操作)
- 个性化重排: ~5ms (可选)
- 总计 Trie 路径: ~20-30ms (远低于 100ms 预算)

### 写路径: 搜索查询到 Trie 更新

```
Step 1: 用户完成搜索 -> 搜索日志写入 Kafka topic "search_queries"
Step 2: Data Collection Service 消费 Kafka, 按查询字符串聚合
Step 3: 每 5 分钟 flush 聚合结果到 Query Frequency Store (Cassandra)
Step 4: Trie Builder 每 15 分钟读取 Frequency Store, 按以下步骤重建 Trie:
        a) 按频率降序取 top-N (N=1000万) 查询
        b) 逐条插入 Compressed Trie
        c) 自底向上计算每个节点的 top-K 建议
        d) 序列化 Trie 为二进制快照, 上传 S3
Step 5: Trie Node 检测到新快照 -> 下载并加载到内存 (热切换, zero-downtime)
Step 6: 热门趋势走快速路径: Trending Service 检测到突发查询
        -> 直接注入 Trie Node 内存中的 Trie (不等待批量重建)
```

### 前端优化

- **Debounce**: 用户连续按键时不逐键请求，等待 50-100ms 无新输入后发起请求
- **预取 (Prefetch)**: 当用户聚焦搜索框时预加载热门前缀
- **乐观渲染**: 先展示本地缓存的建议，后台请求最新结果后 diff 更新
- **请求取消**: 新按键触发时取消上一个未完成的请求 (**AbortController**)
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### QPS 估算

$$
\text{DAU} = 1 \times 10^9
$$

$$
\text{Average searches per user per day} = 6
$$

$$
\text{Average keystrokes per search triggering autocomplete} = 4
$$

$$
\text{Total daily autocomplete requests} = 10^9 \times 6 \times 4 = 2.4 \times 10^{10}
$$

$$
\text{Average QPS} = \frac{2.4 \times 10^{10}}{86400} \approx 278{,}000 \text{ QPS}
$$

$$
\text{Peak QPS} = 278{,}000 \times 3 \approx 834{,}000 \text{ QPS}
$$

需要约 **800K QPS** 的服务能力。通过多级缓存 (CDN 40% + App Cache 30%)，
实际到达 Trie Node 的 QPS 约:

$$
\text{Trie QPS} = 800{,}000 \times (1 - 0.4) \times (1 - 0.3) \approx 336{,}000 \text{ QPS}
$$

### 存储估算

假设维护 **5000 万** 个不同的查询建议:

$$
\text{Average query length} = 20 \text{ bytes (UTF-8)}
$$

$$
\text{Trie node overhead} = 100 \text{ bytes (pointers, top-K list, metadata)}
$$

$$
\text{Compressed Trie nodes} \approx 5 \times 10^7 \times 0.4 = 2 \times 10^7 \text{ (60\% compression)}
$$

$$
\text{Trie memory} = 2 \times 10^7 \times 100 = 2 \text{ GB}
$$

加上 top-K 预存列表 (每节点 top-5, 每条建议 ~50 bytes):

$$
\text{Top-K storage} = 2 \times 10^7 \times 5 \times 50 = 5 \text{ GB}
$$

$$
\text{Total Trie memory} = 2 + 5 = 7 \text{ GB per shard replica}
$$

分 4 个 shard，每 shard 3 副本:

$$
\text{Total memory} = 7 \times 4 \times 3 = 84 \text{ GB}
$$

### 带宽估算

$$
\text{Average response size} = 5 \text{ suggestions} \times 50 \text{ bytes} = 250 \text{ bytes}
$$

$$
\text{Peak bandwidth} = 800{,}000 \times 250 = 200 \text{ MB/s} \approx 1.6 \text{ Gbps}
$$

### 搜索日志存储

$$
\text{Daily search queries} = 10^9 \times 6 = 6 \times 10^9
$$

$$
\text{Average log entry} = 200 \text{ bytes}
$$

$$
\text{Daily log volume} = 6 \times 10^9 \times 200 = 1.2 \text{ TB/day}
$$

$$
\text{90-day retention} = 1.2 \times 90 = 108 \text{ TB}
$$

### 核心排序算法

#### 综合评分公式

每条查询建议的排序分数:

$$
\text{Score}(q) = w_1 \cdot f_{\text{freq}}(q) + w_2 \cdot f_{\text{fresh}}(q) + w_3 \cdot f_{\text{trend}}(q) + w_4 \cdot f_{\text{personal}}(q)
$$

其中:
- $f_{\text{freq}}(q) = \log_{10}(\text{frequency} + 1)$ : 频率分数 (对数平滑)
- $f_{\text{fresh}}(q) = e^{-\lambda \cdot \Delta t}$ : 时效衰减 ($\lambda$ = 衰减系数，$\Delta t$ = 距最后查询的时间)
- $f_{\text{trend}}(q) = \frac{f_{\text{current\_window}} - f_{\text{prev\_window}}}{f_{\text{prev\_window}} + \epsilon}$ : 趋势增长率
- $f_{\text{personal}}(q)$ : 用户历史查询中该 query 的出现比例

典型权重: $w_1 = 0.5, w_2 = 0.2, w_3 = 0.2, w_4 = 0.1$

#### 趋势检测: Z-Score 方法

$$
Z(q) = \frac{f_{\text{current}} - \mu_{\text{historical}}}{\sigma_{\text{historical}}}
$$

当 $Z(q) > 3$ (超过历史均值 3 个标准差)，标记为趋势查询。

#### Trie 构建时间复杂度

$$
T_{\text{build}} = O(N \times L)
$$

其中 $N$ = 查询总数 (5000 万)，$L$ = 平均查询长度 (20 字符)。

$$
T_{\text{build}} = 5 \times 10^7 \times 20 = 10^9 \text{ operations} \approx 3\text{-}5 \text{ seconds (single thread)}
$$

Top-K 传播:

$$
T_{\text{topk}} = O(M \times K \times \log K)
$$

其中 $M$ = Trie 节点数 (2000 万)，$K$ = 每节点 top-K (5)。

$$
T_{\text{topk}} = 2 \times 10^7 \times 5 \times \log_2 5 \approx 2.3 \times 10^8 \text{ ops} \approx 1 \text{ second}
$$

总构建时间约 **5-10 秒**，每 15 分钟重建一次完全可行。

### 成本估算

| 资源 | 规格 | 数量 | 月费用 |
|------|------|------|--------|
| Trie Node (r6g.2xlarge, 64GB RAM) | 4 shards x 3 replicas | 12 台 | $4,800 |
| Autocomplete API (c6g.xlarge) | 处理 800K QPS | 40 台 | $8,000 |
| Application Cache (ElastiCache r6g.xlarge) | 100 万 key | 6 节点 | $3,600 |
| Kafka Cluster | 搜索日志管道 | 6 broker | $3,600 |
| Cassandra (i3.xlarge) | 查询频率存储 | 6 节点 | $4,800 |
| S3 | 日志存储 108 TB | -- | $2,500 |
| CDN (CloudFront) | 40% 命中率分担 | -- | $5,000 |
| **合计** | | | **~$32,300/月** |

对比搜索广告收入 (Google 搜索广告年收入 ~$160B)，自动补全系统的成本微不足道。
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 生产环境约束 (Production Constraints -- Scale & Reliability)

### 具体规模数字

- **DAU**: 10 亿
- **峰值 QPS**: ~800K (原始请求), ~336K (到达 Trie Node)
- **Trie 内存**: 7 GB per shard (总 84 GB across 12 nodes)
- **搜索日志**: 1.2 TB/天
- **不同查询数**: 5000 万 (维护在 Trie 中)
- **Trie 重建周期**: 15 分钟 (批量)，秒级 (趋势注入)

### 单点故障分析

| 组件 | 故障影响 | 缓解措施 |
|------|----------|----------|
| Trie Node 单节点宕机 | 该分片 33% 容量丢失 | 每分片 3 副本，读请求自动路由到存活副本 |
| 整个 Trie 分片丢失 | 该前缀范围无法服务 | Application Cache 仍可服务热门查询 (15min TTL)，同时从 S3 快照快速恢复 |
| Autocomplete Service 节点故障 | 部分请求失败 | 无状态服务，L7 LB 自动摘除故障节点 |
| Kafka 集群故障 | 数据收集管道中断 | Trie 仍可用旧快照服务 (数据滞后但不中断服务)；Kafka 3 副本跨 AZ |
| Trie Builder 故障 | 新快照无法生成 | 继续使用旧快照，趋势注入仍走独立路径 |
| Redis Cache 故障 | 缓存穿透，Trie QPS 增加 | Trie Node 有足够容量处理全量请求，CDN 缓存仍有效 |

### 多数据中心 / 跨区域部署

#### 部署策略: 主动-主动 (Active-Active) + 区域独立 Trie

```
US-East: [Trie Nodes (full)] [Autocomplete API] [CDN Edge]
US-West: [Trie Nodes (full)] [Autocomplete API] [CDN Edge]
EU:      [Trie Nodes (full)] [Autocomplete API] [CDN Edge]
APAC:    [Trie Nodes (full)] [Autocomplete API] [CDN Edge]
```

- 每个区域持有**完整的 Trie 副本** (7 GB per shard 足够小)
- Trie Builder 在中心区域 (US-East) 构建快照，上传到各区域 S3 桶
- 各区域 Trie Node 独立从本区域 S3 拉取快照
- **用户请求由 GeoDNS 路由到最近的区域**，不跨区域调用

#### 区域定制化

- 全球共享基础 Trie (英文热门查询)
- 每个区域叠加**区域特有查询** (如 APAC 区域有中文/日文查询)
- Trie 合并: Global Trie + Regional Trie -> Region-specific Trie

#### 数据同步

- 搜索日志通过 **跨区域 Kafka MirrorMaker** 同步到中心集群
- 中心集群计算全局频率 + 区域频率
- Trie 快照按区域生成后分发

### 高并发处理

1. **前端 Debounce (50-100ms)**:
   - 用户连续按键时不逐键请求，等待输入停顿后才发起
   - 将实际 QPS 从理论值降低 50-70%

2. **请求合并 (Request Coalescing)**:
   - Application Cache 层: 多个相同前缀的并发请求，只有第一个穿透到 Trie Node
   - 后续请求等待第一个请求的结果 (**singleflight pattern**)

3. **速率限制 (Rate Limiting)**:
   - 每用户每秒最多 10 次自动补全请求 (Token Bucket)
   - 异常高频请求 (bot) 返回缓存结果不查 Trie

4. **熔断器 (Circuit Breaker)**:
   - Trie Node 响应 P99 > 50ms -> 熔断，直接返回 Application Cache / 空结果
   - Personalization Service 不可用 -> 降级为非个性化结果

5. **优雅降级 (Graceful Degradation)**:
   - **Level 1**: 关闭个性化，全部返回全局热门建议 (提高缓存命中率到 80%+)
   - **Level 2**: 减少返回建议数 (10 -> 5)
   - **Level 3**: 增加 CDN TTL (5min -> 30min)，容忍数据陈旧
   - **Level 4**: 仅返回静态热门查询列表 (硬编码 top-1000)

### 监控与告警 (Monitoring & Alerting)

| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 自动补全 P99 延迟 | > 100ms | P1 (Warning) |
| 自动补全 P99 延迟 | > 200ms | P0 (Critical) |
| Trie Node 查询延迟 P99 | > 10ms | P1 |
| CDN 缓存命中率 | < 30% | P2 (Investigation) |
| Application Cache 命中率 | < 50% | P2 |
| Trie 快照年龄 | > 1 小时 | P1 |
| Kafka consumer lag | > 10M messages | P1 |
| 搜索日志丢失率 | > 0.1% | P2 |
| Trie Node 内存使用率 | > 85% | P2 (Scale-up) |
| Autocomplete API 5xx 率 | > 0.1% | P0 |
"""

# ---------------------------------------------------------------------------
# S6: Tradeoffs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡讨论 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与理由 |
|------|--------|--------|-----------------|
| **数据结构** | Trie (前缀树) | Inverted Index (倒排索引) | **Trie**: 专为前缀匹配设计，O(p) 查找时间。Inverted Index 更适合全文搜索和模糊匹配，但前缀匹配效率不如 Trie。如果未来需要模糊匹配，可以加一层 Edit Distance 预计算 |
| **Trie 更新策略** | 实时更新 (每次查询即时更新 Trie) | 定期批量重建 (每 15 分钟) | **批量重建**: 实时更新 Trie 需要复杂的并发控制 (读写锁 / CAS)，而且每秒 278K 写入直接打到 Trie 上不现实。批量重建简单可靠，15 分钟延迟用户不感知。趋势查询走独立快速注入路径弥补时效性 |
| **缓存一致性** | 强一致 (Trie 更新即清缓存) | 最终一致 (TTL 过期自然更新) | **TTL 最终一致**: 自动补全不需要实时一致。CDN 5min + App Cache 15min 的 TTL 策略足够。强一致需要发布/订阅清缓存，复杂且增加延迟 |
| **个性化实现** | 服务端实时计算 | 客户端本地历史 | **混合**: 服务端返回全局 top-K，客户端用本地搜索历史做二次混排 (前 2 条来自历史，后 3 条来自全局)。纯服务端个性化破坏 CDN 缓存效果 |
| **多语言支持** | 统一 Trie (所有语言混合) | 分语言 Trie | **分语言 Trie**: 中文和英文的分词方式完全不同。统一 Trie 无法高效处理中文拼音前缀。每种语言独立 Trie，请求时根据 Accept-Language 路由 |

### CAP 定理应用

Search Autocomplete 选择 **AP (Availability + Partition Tolerance)**:

- **Partition 发生时**: 各区域用本地 Trie 独立服务。建议列表可能暂时不反映
  其他区域的查询趋势，但本区域功能完全正常
- **Partition 恢复后**: 跨区域搜索日志同步，下一次 Trie 重建自动合并全球数据
- **不选 CP 的原因**: 自动补全的核心价值是"快速响应"。如果为了全球一致性
  而阻塞请求或返回空结果，用户体验远差于返回稍陈旧但有用的建议

### 成本 vs 性能

| 层次 | 低成本方案 | 高性能方案 | 我们的平衡点 |
|------|-----------|-----------|-------------|
| 数据结构 | 数据库 LIKE 查询 (无额外内存) | In-memory Trie (84 GB) | Trie: LIKE 查询 ~50ms, Trie < 1ms。84 GB 内存成本 ~$500/月，相对搜索广告收入微不足道 |
| 缓存 | 仅 Application Cache | CDN + App Cache + 浏览器 | 三级缓存: CDN 分担 40% 流量，月增 $5K 但节省大量 Trie Node 成本 |
| Trie 更新 | 实时更新 (强一致) | 定期重建 (弱一致) | 15 分钟重建 + 秒级趋势注入: 平衡时效性和工程复杂度 |
| 个性化 | 无个性化 (全局缓存) | 全量服务端个性化 | 客户端混排: 不破坏缓存，个性化在客户端完成 |
| 过滤 | 构建时过滤 (Trie 中不含不雅词) | 查询时过滤 | 构建时过滤: 运行时零开销，但更新不雅词库需要等下次 Trie 重建 |

### 10x / 100x 扩展时的变化

**10x (100 亿 DAU, 8M QPS)**:
- Trie 分片从 4 个增加到 40 个，每分片仍 ~7 GB
- CDN 缓存策略更激进 (TTL 延长到 15 分钟)，缓存命中率提升到 60%
- 前端 debounce 窗口从 100ms 增加到 200ms，进一步降低 QPS
- 考虑**边缘计算**: 将 Trie 小型副本 (top-10K 热门前缀) 部署到 CDN 边缘节点，
  热门查询不回源

**100x (全球极端规模)**:
- **分层 Trie**: Level 1 (CDN 边缘) 持有 top-1% 热门前缀 (内存 < 100 MB)，
  处理 80% 请求；Level 2 (区域中心) 持有完整 Trie，处理长尾查询
- **预测性预取**: ML 模型预测用户下一个字符，提前计算建议并推送到客户端
- Trie 重建从集中式改为**流式增量更新** (Flink 直接维护分布式 Trie 状态)，
  消除批量重建的延迟窗口
- 存储从内存 Trie 切换到 **SSD-based B+ Trie** (如 RocksDB 自定义格式)，
  降低内存成本
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: 如果一个突发新闻事件 (如名人去世) 导致某个查询从零暴增到百万 QPS，系统怎么处理？

**承认挑战**: 批量 Trie 重建周期为 15 分钟，如果完全依赖它，新闻事件发生后
15 分钟内搜索框不会出现相关建议，这是不可接受的。

**缓解措施**:
1. **趋势检测服务 (Trending Service)** 以 **10 秒窗口** 计算每个查询的 Z-Score。
   当 Z > 3 (频率突然增长 3 个标准差以上)，标记为趋势查询
2. **快速注入路径**: 趋势查询直接通过 gRPC 推送到所有 Trie Node，
   **在内存中动态插入 Trie** 节点，无需等待批量重建
3. **注入延迟**: 从事件发生到建议出现约 **30-60 秒**
   (10s 检测窗口 + 处理时间 + 分发到各区域)
4. **CDN 缓存绕过**: 趋势查询触发 CDN 缓存失效 (purge) 或设置短 TTL (30s)，
   确保用户看到最新建议
5. **安全阀**: 趋势查询注入前经过 Filter Service 审核，防止不当内容
   被放大展示

### Q2: Trie 内存不够了怎么办？查询量从 5000 万增长到 5 亿怎么扩展？

**分析**: 5 亿查询的 Trie 内存约 70 GB per shard，单机仍可承受
(AWS r6g.4xlarge 128 GB)。但进一步增长需要更根本的方案。

**扩展策略**:
1. **短期 -- 增加分片数**: 从 4 分片增加到 20 分片，每分片 ~14 GB。
   分片路由基于前缀哈希
2. **中期 -- 长尾剪枝**: 80% 的查询只占 1% 的流量。维护**两级 Trie**:
   - Hot Trie (内存): top-5000 万高频查询
   - Cold Trie (SSD, RocksDB): 剩余 4.5 亿低频查询，按需加载
3. **长期 -- 近似数据结构**: 对极低频查询 (< 10 次/天)，
   不存入 Trie，而是用 **Count-Min Sketch** 做概率性频率估计，
   只有频率超过阈值才"晋升"到 Trie 中

### Q3: 用户输入拼写错误时 (如 "googel" 而非 "google")，自动补全怎么处理？

**设计决策**: Autocomplete 不直接做拼写纠错 -- 这是 **Spell Correction** 系统的职责。
但有几个方式提供友好体验:

1. **历史查询已包含常见拼写错误**: 如果很多用户搜索过 "googel"，
   它作为热门查询会出现在 Trie 中，建议列表会包含 "google" (纠正后的)
   因为 "googel" -> "google" 的纠正频率被计入
2. **Edit Distance 预计算**: 对 top-100 万查询，离线计算 Edit Distance <= 2
   的变体，在 Trie 中为这些变体添加指向原始查询的指针
3. **客户端拼写检查**: 浏览器的拼写检查 API 可以在前端提供下划线提示
4. **组合方案**: 当前缀无 Trie 匹配时 (dead-end)，fallback 到
   Spell Correction 服务获取纠正建议

### Q4: 两个用户同时搜索相同前缀但看到不同建议（因为个性化），这合理吗？

**完全合理**，理由:

1. **搜索引擎的标准做法**: Google 的自动补全已高度个性化。
   开发者搜 "python" 看到 "python list comprehension"，
   宠物爱好者看到 "python snake care"
2. **信息检索理论基础**: 查询意图的歧义 (**Query Ambiguity**) 是搜索的核心挑战。
   个性化建议本质上是在做 **Query Intent Disambiguation (查询意图消歧)**
3. **用户体验测量**: A/B 实验通常显示个性化建议的点击率 (CTR) 比全局建议
   高 15-25%

**实现注意事项**:
- 个性化权重不应过高 ($w_4 = 0.1$)，避免"信息茧房"
- 前 1-2 条建议可以个性化，后面仍以全局热门为主
- 用户可以清除搜索历史来重置个性化

### Q5: 自动补全系统挂了（完全不可用），对搜索业务影响多大？怎么做容灾？

**影响评估**:
- 搜索本身仍然可用 (用户可以手动输入完整查询并按回车)
- 但搜索量预计下降 **10-15%** (部分用户依赖建议发现查询)
- 搜索广告收入相应下降
- **结论**: 高影响但非灾难性，需要尽快恢复而非 100% 永不故障

**容灾策略**:
1. **静态 Fallback**: 预计算 top-1000 热门前缀的建议，硬编码为 JSON 文件
   部署在 CDN。Autocomplete 服务不可用时，前端切换到 CDN 静态文件
2. **多区域独立部署**: 单区域故障不影响其他区域
3. **快速恢复**: Trie Node 从 S3 快照恢复，冷启动时间 < 2 分钟
   (下载 7 GB 快照 + 反序列化加载)
4. **降级模式**: 即使只有 Application Cache 存活，仍可服务 30% 的热门查询
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1h Interview Pacing)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 1 小时面试节奏指南 (1-Hour Interview Pacing Guide)

### 0-5 分钟: 需求澄清

"Search Autocomplete 的核心挑战是在 **100ms 内** 从数十亿候选查询中返回以用户输入
为前缀的 top-K 建议。延迟超过 100ms 用户就会感知到卡顿。让我先确认几个关键约束。"

- 确认是否只需前缀匹配 -> 决定数据结构 (Trie vs Inverted Index)
- 确认是否需要个性化 -> 影响缓存策略 (个性化会破坏 CDN 缓存)
- 确认热点事件的时效性要求 -> 影响 Trie 更新频率
- 确认多语言需求 -> 影响分词和 Trie 设计
- 确认查询规模 -> 影响 Trie 内存和分片数量

功能需求: 前缀匹配建议 (top-5)、排序 (频率 + 时效 + 趋势)、数据收集管道。
非功能需求: 99.99% 可用性、P99 < 100ms、~800K QPS (峰值)。
明确排除: 搜索结果排序、拼写纠错、语音搜索。

### 5-15 分钟: 高层架构

画出两条管道:
- **查询服务管道**: Client -> CDN -> Autocomplete API -> App Cache -> Trie Node -> 返回 top-K
- **数据收集管道**: Search Log -> Kafka -> Aggregation -> Frequency Store -> Trie Builder -> S3 Snapshot -> Trie Node

**核心数据结构 -- Compressed Trie**:
"用 Compressed Trie (也叫 Radix Tree) 存储查询。每个节点预存 top-K 建议列表，
查询时 O(p) 遍历到前缀节点直接返回，p 是前缀长度。压缩后节点数减少 60%。"

**为什么选 Trie 而非数据库 LIKE 查询**:
"LIKE 'prefix%' 在数据库中需要全表扫描或 B-tree 范围查询，延迟 ~50ms。
内存 Trie 查找 < 1ms，差 50 倍。对于 P99 < 100ms 的要求，Trie 是唯一选择。"

数据库选型:
- Trie 全内存 (7 GB per shard，4 shards, 3 replicas)
- Cassandra 存查询频率 (写密集)
- Kafka 做搜索日志管道
- Redis 做 Application Cache + 个性化历史

### 15-40 分钟: 深入设计 (选 2-3 个重点)

**重点 1: Trie 数据结构 + 分片策略 (10 min)**
- Compressed Trie 结构: 单链压缩, 每节点预存 top-K
- 查询: O(p) 时间, ~1ms
- 分片: 4 shards 按前缀范围, 一致性哈希处理热点
- 内存: 7 GB per shard, 84 GB total (12 nodes with replicas)
- 更新: 每 15 分钟批量重建, 热切换 zero-downtime

**重点 2: 多级缓存架构 (8 min)**
- 浏览器缓存 (60s TTL) -> CDN (5min, 40% 命中) -> App Cache (15min, 30% 命中) -> Trie
- CDN 是关键: 热门前缀 ("how to", "what is") 高度集中, CDN 命中率高
- Request Coalescing: 相同前缀并发请求只穿透一次 (singleflight)

**重点 3: 数据收集 + 趋势检测 (7 min)**
- 搜索日志 -> Kafka -> 5 分钟窗口聚合 -> Frequency Store
- Trie Builder 每 15 分钟重建快照, 上传 S3
- 趋势检测: 10 秒窗口 Z-Score > 3 -> 快速注入 Trie (30-60s 延迟)
- 排序公式: 频率 (0.5) + 时效衰减 (0.2) + 趋势 (0.2) + 个性化 (0.1)

### 40-50 分钟: 容量估算与权衡

容量: 10 亿 DAU, ~800K QPS (峰值), Trie 84 GB, 日志 1.2 TB/天,
~$32K/月 (相对搜索广告收入微不足道)。

关键权衡:
1. **Trie vs Inverted Index**: Trie 专为前缀匹配, O(p) vs O(n log n)
2. **批量重建 vs 实时更新**: 批量简单可靠, 趋势走快速路径补时效
3. **TTL 缓存 vs 强一致缓存**: TTL 简单, 自动补全不需要实时一致
4. **客户端混排 vs 服务端个性化**: 客户端不破坏 CDN 缓存
5. **分语言 Trie vs 统一 Trie**: 分语言更高效, 中英分词完全不同

### 50-55 分钟: 总结与改进方向

"如果有更多时间，我会进一步优化:
1. **ML 排序模型**: 用 Learning to Rank (LTR) 替代线性加权公式,
   考虑更多特征 (用户设备、时间、地理位置)
2. **Query Reformulation**: 不只匹配前缀, 而是理解查询意图
   (如输入 'ny' 建议 'New York restaurants')
3. **联合建议**: 同时展示查询建议 + 实体建议 (如搜 'obama' 同时
   展示人物卡片 + 相关查询)
4. **边缘计算 Trie**: 将 hot Trie (top-10K 前缀) 部署到 CDN 边缘节点,
   热门查询 ~5ms 响应"

监控: 自动补全 P99 延迟、CDN/Cache 命中率、Trie 快照年龄、
Kafka consumer lag、5xx 错误率。

### 55-60 分钟: 向面试官提问

准备 2-3 个展示系统设计深度的问题。

---

### 3 分钟电梯演讲版本

"Search Autocomplete 的核心是在 **100ms 内** 返回 top-K 前缀匹配建议。

数据结构: **Compressed Trie** (Radix Tree)，每节点预存 top-K 建议。查询
O(p) 遍历到前缀节点, 直接返回预存结果, ~1ms。5000 万查询, Trie 压缩后 ~7 GB,
分 4 个 shard, 每 shard 3 副本, 总 84 GB。

两条管道:
- **查询管道**: Client -> CDN (40% 命中) -> App Cache (30% 命中) -> Trie Node (< 1ms)。
  端到端 P99 < 50ms。
- **数据收集管道**: Search Log -> Kafka -> 5 min 窗口聚合 -> Frequency Store
  -> Trie Builder (每 15 min 重建) -> S3 Snapshot -> Trie Node (热切换)。

关键设计决策:
- **Trie 而非 DB LIKE**: Trie < 1ms vs LIKE ~50ms, 差 50x
- **批量重建 + 趋势快速注入**: 15 min 批量重建平衡一致性和复杂度,
  Breaking news 30-60s 内通过趋势检测快速注入
- **多级缓存**: CDN + App Cache 分担 70% 流量, Trie Node 只处理 30%
- **客户端个性化混排**: 不破坏 CDN 缓存的前提下提供个性化

规模: 10 亿 DAU, ~800K QPS, 84 GB Trie, 1.2 TB/天日志,
~$32K/月 (相对搜索广告收入微不足道)。"
"""


def populate_interview_search_autocomplete() -> None:
    """Create or update the interview-search-autocomplete record with all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            record = SystemDesign(
                slug=SLUG,
                title=TITLE,
                display_order=DISPLAY_ORDER,
            )
            db.add(record)
            db.flush()
            print(f"[DONE] Created SystemDesign record: slug='{SLUG}', title='{TITLE}'")
        else:
            print(f"[INFO] Found existing record for slug='{SLUG}', updating...")

        record.overview = OVERVIEW
        record.architecture = ARCHITECTURE
        record.dataflow = DATAFLOW
        record.formulas = FORMULAS
        record.production_constraints = PRODUCTION_CONSTRAINTS
        record.tradeoffs = TRADEOFFS
        record.defense = DEFENSE
        record.verbal_outline = VERBAL_OUTLINE

        db.commit()
        print(f"[DONE] Updated all 8 sections for '{SLUG}'.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            ("overview", record.overview),
            ("architecture", record.architecture),
            ("dataflow", record.dataflow),
            ("formulas", record.formulas),
            ("production_constraints", record.production_constraints),
            ("tradeoffs", record.tradeoffs),
            ("defense", record.defense),
            ("verbal_outline", record.verbal_outline),
        ]
        total_chars = 0
        for name, content in sections:
            length = len(content) if content else 0
            total_chars += length
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")
        print(f"  Total: {total_chars} chars")

        # Check for Chinese characters
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        for name, content in sections:
            if content and chinese_pattern.search(content):
                print(f"  [OK] {name}: Chinese chars present")
            else:
                print(f"  [WARN] {name}: No Chinese chars found!")

        # Check for bare | in math
        bare_pipe = False
        for name, content in sections:
            if not content:
                continue
            in_math = False
            for i, ch in enumerate(content):
                if ch == "$" and (i == 0 or content[i - 1] != "\\"):
                    in_math = not in_math
                if in_math and ch == "|" and (i == 0 or content[i - 1] != "\\"):
                    before = content[max(0, i - 4):i]
                    if "\\mid" not in before and "\\vert" not in before:
                        bare_pipe = True
                        print(f"  [WARN] {name}: bare | found in math near position {i}")

        if not bare_pipe:
            print("  [OK] No bare | in math formulas")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_interview_search_autocomplete()
