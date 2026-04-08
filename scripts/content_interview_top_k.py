"""Populate interview-top-k-heavy-hitters system design with all 8 markdown sections.

Content covers a classic system design interview topic: Design Top-K Heavy Hitters --
finding the most frequently occurring elements in a massive data stream using
Count-Min Sketch, Space-Saving algorithm, MapReduce, and multi-level aggregation.
Idempotent: creates record if missing, overwrites existing.

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

SLUG = "interview-top-k-heavy-hitters"
TITLE = "Design Top-K Heavy Hitters"
DISPLAY_ORDER = 110

# ---------------------------------------------------------------------------
# S1: Overview (Requirements Clarification -- 5 min)
# ---------------------------------------------------------------------------
OVERVIEW = r"""## 需求澄清 (Requirements Clarification)

### 问题陈述 (Problem Statement)

设计一个**Top-K Heavy Hitters** 系统，能够在海量数据流中实时或近实时地找出
出现频率最高的 K 个元素。典型应用场景包括：最热门搜索词 (trending searches)、
最高频 API 端点 (hot endpoints)、最活跃 IP 地址 (DDoS detection)、最畅销商品
(best sellers)、最热门 hashtag 等。

核心挑战是数据量太大无法精确计数——单台机器内存放不下所有元素的计数器，且数据
以流式到达，不能假设可以多次遍历。因此需要在**精确性、内存、延迟**三者之间
做权衡。

### 功能性需求 (Functional Requirements)

1. **Top-K 查询 (Top-K Query)**: 给定时间窗口 (最近 1 分钟 / 1 小时 / 1 天)，
   返回出现频率最高的 K 个元素及其近似计数
2. **数据摄入 (Data Ingestion)**: 持续接收高吞吐量事件流
   (每秒数十万到数百万事件)，每个事件包含一个可哈希的 key (字符串/ID)
3. **多时间粒度 (Multi-granularity)**: 支持不同时间窗口的 Top-K
   (1 min / 5 min / 1 hour / 1 day)
4. **近实时更新 (Near Real-time)**: 新的热门元素在秒级到分钟级内反映在结果中
5. **历史查询 (Historical Query)**: 支持查询过去任意时间段的 Top-K

### 非功能性需求 (Non-Functional Requirements)

- **可用性 (Availability)**: 99.9% -- Top-K 结果通常用于监控大屏和告警，
  短暂不可用可接受但不应超过几分钟
- **延迟 (Latency)**: 查询 P99 < 50ms -- Top-K 结果通常预计算好，
  查询只是读取缓存
- **吞吐量 (Throughput)**: 写入 1M+ events/sec (峰值)，读取 10K QPS
- **精确度 (Accuracy)**: 允许近似计数 -- 排名误差在 top-K 边界附近
  可接受 (例如第 10 名和第 11 名可能交换)，但 top-3 必须高度准确
- **可扩展性 (Scalability)**: 支持数十亿不同 key 的基数
  (cardinality)，水平扩展
- **一致性 (Consistency)**: 最终一致 -- 不同节点的 Top-K 结果允许
  短暂不一致 (秒级收敛)

### 向面试官提出的澄清问题 (Clarification Questions)

1. **Q: 元素的基数 (cardinality) 有多大？是百万级还是十亿级不同 key？**
   -- WHY: 如果基数小 (< 1M)，可以用精确 **HashMap** 计数；
   如果基数大 (> 1B)，必须用概率数据结构
   (**Count-Min Sketch / HyperLogLog**)

2. **Q: 对精确度的要求有多高？能否接受概率性的近似结果？**
   -- WHY: 精确 Top-K 需要 $O(n)$ 内存 (n = 不同 key 数)；
   近似 Top-K 用 **Count-Min Sketch** 只需 $O(\frac{1}{\epsilon} \ln \frac{1}{\delta})$
   内存，差距可达 1000x

3. **Q: 需要支持哪些时间窗口？是固定窗口还是滑动窗口？**
   -- WHY: 固定窗口 (tumbling) 只需在窗口结束时聚合；滑动窗口需要
   维护过期元素的逐出逻辑，复杂度更高。分钟级滑动窗口可用
   **环形缓冲区 (Ring Buffer)** 实现

4. **Q: 数据源是单一流还是多个异构流？**
   -- WHY: 单一流可以在一个管道处理；多个异构流需要
   **多级聚合 (Multi-level Aggregation)**: 每个流先本地 Top-K，
   再全局合并

5. **Q: 是否需要支持"突发检测"——识别频率突然飙升的元素？**
   -- WHY: 突发检测需要与历史基线对比 (Z-Score / 移动平均)，
   不仅仅是绝对频率排名。这会增加一个统计检测层

6. **Q: Top-K 结果的消费者是谁？是实时大屏、告警系统还是离线分析？**
   -- WHY: 实时大屏需要推送 (WebSocket/SSE)，告警系统需要阈值触发，
   离线分析只需批量导出。消费模式决定输出管道设计

7. **Q: 是否需要按维度切分？例如"每个国家的 Top-K"或"每个设备类型的 Top-K"？**
   -- WHY: 维度切分意味着需要为每个维度组合维护独立的 Top-K 数据结构，
   内存和计算成本按维度数量线性增长

### 范围声明 (Out of Scope)

- 去重计数 (Count Distinct / HyperLogLog) -- 只关心频率排名，不关心唯一计数
- 异常检测 (Anomaly Detection) -- 只提供频率排名数据，异常判定由下游系统负责
- 全文搜索 / 自动补全 -- 独立系统
- 数据采集端 SDK 设计
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## 架构深度解析 (Architecture Deep Dive)

### 整体架构概览

Top-K Heavy Hitters 系统采用**三层聚合架构**:
1. **本地聚合层 (Local Aggregation)**: 每个应用主机在内存中维护本地计数器，
   定期 flush 到中间层
2. **分区聚合层 (Partition Aggregation)**: 按 key 哈希分区，每个分区独立
   维护 Count-Min Sketch + Min-Heap
3. **全局合并层 (Global Merge)**: 从所有分区收集局部 Top-K，合并为全局 Top-K

这种分层设计将 1M+ events/sec 的写入压力逐层分解，避免单点瓶颈。

### 核心组件与职责

| 组件 | 职责 |
|------|------|
| **Event Collector (事件采集器)** | 接收原始事件流，写入 **Kafka** 主题。无状态，水平扩展 |
| **Local Counter (本地计数器)** | 应用主机内嵌的轻量级 HashMap，每 5 秒 flush 一次部分聚合结果到 Kafka |
| **Stream Processor (流处理器)** | **Flink / Kafka Streams** 消费 Kafka，按 key 哈希分区，维护 Count-Min Sketch |
| **Top-K Aggregator (Top-K 聚合器)** | 每个分区维护一个大小为 K 的 **Min-Heap (最小堆)**，只保留频率最高的 K 个元素 |
| **Global Merger (全局合并器)** | 定期 (每 5-10 秒) 从所有分区收集局部 Top-K，执行全局合并排序 |
| **Result Cache (结果缓存)** | **Redis** 存储最新的 Top-K 结果，供查询 API 读取。TTL 与聚合周期匹配 |
| **Query API (查询接口)** | 无状态 REST API，从 Redis 读取预计算的 Top-K 结果返回 |
| **Batch Pipeline (批处理管道)** | **Spark / MapReduce** 每小时/每天跑一次精确 Top-K，用于校准和历史查询 |

### 数据结构详解

#### Count-Min Sketch (CMS)

**Count-Min Sketch** 是一个二维计数器数组，用 $d$ 个独立哈希函数将每个 key
映射到 $w$ 列中的一个位置。

**结构**:
- $d$ 行 (哈希函数数量)，$w$ 列 (每行的桶数)
- 总内存 = $d \times w \times$ 4 bytes (32-bit 计数器)

**操作**:
- **Add(key)**: 对每行 $i$，计算 $h_i(\text{key}) \mod w$，将对应计数器 +1
- **Query(key)**: 返回 $\min_{i=1}^{d} \text{CMS}[i][h_i(\text{key}) \mod w]$

**误差保证**:
- 设 $\epsilon$ 为相对误差，$\delta$ 为失败概率
- $w = \lceil e / \epsilon \rceil$, $d = \lceil \ln(1/\delta) \rceil$
- 真实计数 $f(\text{key}) \le \hat{f}(\text{key}) \le f(\text{key}) + \epsilon N$
  其中 $N$ 是总事件数
- CMS 只会**高估**，不会低估 (单向误差)

**典型配置**: $\epsilon = 0.001$, $\delta = 0.01$
-> $w = 2718$, $d = 5$ -> $2718 \times 5 \times 4 = 54$ KB

#### Space-Saving Algorithm

**Space-Saving** 是另一种流式 Top-K 算法，维护一个固定大小 $m$ 的计数器集合:

1. 如果 key 已在集合中: 计数器 +1
2. 如果 key 不在集合中且集合未满: 添加 key，计数器 = 1
3. 如果 key 不在集合中且集合已满: 找到计数最小的 key，替换为新 key，
   计数器 = 原最小计数 + 1

**优点**: 精确追踪 heavy hitters (频率 > $N/m$ 的元素保证在集合中)
**缺点**: 替换操作需要找最小值，用 Min-Heap 实现为 $O(\log m)$

#### CMS + Min-Heap 组合 (本系统采用)

本系统采用 **Count-Min Sketch + Min-Heap** 的组合策略:
- **CMS** 负责近似计数 (内存固定，与 key 基数无关)
- **Min-Heap** (大小 K) 维护当前 Top-K 候选

**流程**: 每个事件到达 -> CMS.Add(key) -> 估计频率 $\hat{f}$ = CMS.Query(key)
-> 如果 $\hat{f}$ > heap.min() 或 heap 未满，则将 (key, $\hat{f}$) 插入 heap
(替换堆顶最小元素)

### 流式 vs 批处理双轨架构

系统同时运行两条管道:

| 维度 | 流式管道 (Streaming) | 批处理管道 (Batch) |
|------|---------------------|-------------------|
| 技术 | Flink / Kafka Streams | Spark / MapReduce |
| 延迟 | 5-10 秒 | 1-24 小时 |
| 精确度 | 近似 (CMS) | 精确 (全量 HashMap) |
| 用途 | 实时大屏、告警 | 历史查询、校准 |
| 内存 | 固定 (~100 MB/分区) | 与数据量成正比 |

批处理结果定期覆盖流式结果，防止 CMS 误差累积 (**Lambda Architecture** 的
核心思想)。

### 反馈与校准回路

批处理管道每小时产出精确 Top-K，与流式 Top-K 对比:
- 如果流式 Top-K 的排名误差 > 阈值 (例如前 10 名中有 3 个不一致)，
  触发 CMS 参数调优告警
- 校准结果写入 Redis，覆盖流式结果
- 监控指标: **Rank Correlation (Kendall's $\tau$)** 衡量流式 vs 批处理
  排名一致性，目标 $\tau > 0.9$
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## 数据流与关键组件 (Data Flow & Key Components)

### 写入路径 (Write Path)

```
Application Hosts (应用主机, 数千台)
  |
  | 每台主机内嵌 Local Counter (HashMap)
  | 每 5 秒 flush 部分聚合: {key: count} 批量发送
  |
  v
Kafka (按 key 哈希分区, 例如 64 分区)
  |
  v
Flink Stream Processor (每个分区一个 Task)
  |
  | 1. CMS.Add(key, count)  -- 更新 Count-Min Sketch
  | 2. freq = CMS.Query(key) -- 获取近似频率
  | 3. MinHeap.updateIfLarger(key, freq) -- 维护 Top-K
  |
  v
Top-K Snapshot (每 5 秒输出一次)
  |
  v
Global Merger (合并所有分区的局部 Top-K)
  |
  | 1. 收集 P 个分区各自的 Top-K (共 P x K 个候选)
  | 2. 合并排序, 取全局 Top-K
  | 3. 写入 Redis
  |
  v
Redis (预计算结果缓存)
  Key: "topk:{window}:{granularity}" -> Sorted Set
  例如: "topk:2024-01-15-14:00:1h" -> [(key1, 50000), (key2, 48000), ...]
```

### 读取路径 (Read Path)

```
Client Request: GET /api/topk?window=1h&k=10
  |
  v
Query API (无状态, 负载均衡)
  |
  v
Redis Lookup: ZREVRANGE "topk:current:1h" 0 9 WITHSCORES
  |
  v
Response: [{key: "trending_topic_1", count: 50000}, ...]
  延迟: < 5ms (Redis 内存读取)
```

### API 设计

**查询 Top-K**:
```
GET /api/v1/topk
  ?window=1h          // 时间窗口: 1m, 5m, 1h, 1d
  &k=10               // 返回前 K 个
  &dimension=country   // 可选: 按维度切分
  &value=US            // 可选: 维度值

Response 200:
{
  "window": "1h",
  "timestamp": "2024-01-15T14:00:00Z",
  "k": 10,
  "approximate": true,
  "items": [
    {"key": "search_term_A", "count": 50234, "rank": 1},
    {"key": "search_term_B", "count": 48102, "rank": 2},
    ...
  ]
}
```

**报告事件 (内部)**:
```
POST /api/v1/events
Content-Type: application/json

{
  "events": [
    {"key": "search_term_A", "timestamp": 1705312800000},
    {"key": "search_term_B", "timestamp": 1705312800001},
    ...
  ]
}

Response 202 Accepted
```

### 核心数据模型

**Kafka Event Schema**:
```json
{
  "source_host": "app-server-042",
  "flush_timestamp_ms": 1705312800000,
  "window_start_ms": 1705312795000,
  "window_end_ms": 1705312800000,
  "counts": {
    "search_term_A": 142,
    "search_term_B": 89,
    "search_term_C": 67
  }
}
```

**Redis 存储结构**:
- **Sorted Set**: `topk:{window_id}:{granularity}` -> member=key, score=count
- **Hash**: `topk:meta:{window_id}` -> total_events, cms_epsilon, last_updated
- **TTL**: 1m 窗口 TTL=10min, 1h 窗口 TTL=25h, 1d 窗口 TTL=8d

### 多时间窗口实现

采用**层级时间轮 (Hierarchical Time Wheel)** 聚合:

```
秒级计数器 (5s 桶)
  |-- 12 个桶聚合 -> 1 分钟 Top-K
      |-- 12 个桶聚合 -> 5 分钟 Top-K  (注意: CMS 可直接相加)
          |-- 12 个桶聚合 -> 1 小时 Top-K
              |-- 24 个桶聚合 -> 1 天 Top-K
```

**CMS 的可加性**: 两个 CMS (相同参数 $d$, $w$) 可以逐元素相加，得到的新 CMS
等价于在合并数据流上直接构建的 CMS。这使得时间窗口聚合非常高效——只需将多个
短窗口的 CMS 矩阵相加即可得到长窗口的 CMS。

**滑动窗口实现**: 用**环形缓冲区 (Ring Buffer)** 存储最近 N 个短窗口的 CMS。
滑动时加入新窗口的 CMS、减去过期窗口的 CMS。减法可能产生负值，需 clamp 到 0。
"""

# ---------------------------------------------------------------------------
# S4: Formulas (Capacity Estimation + Core Algorithms)
# ---------------------------------------------------------------------------
FORMULAS = r"""## 容量估算与核心算法 (Capacity Estimation & Core Algorithms)

### 容量估算 (Back-of-Envelope Estimation)

**假设**:
- 1 亿 DAU (Daily Active Users)
- 每用户每天产生 50 个事件 (搜索、点击、页面访问等)
- 平均每个事件 key 长度 = 30 bytes

**写入 QPS**:
- 日总事件 = $10^8 \times 50 = 5 \times 10^9$ (50 亿)
- 平均写入 QPS = $\frac{5 \times 10^9}{86400} \approx 58K$
- 峰值 QPS (3x) = $\sim 170K$ events/sec
- 经过本地聚合 (5s 窗口, 1000 台主机): 实际到 Kafka 的 QPS
  = $\frac{1000}{5} = 200$ batches/sec (每批含数千 key-count 对)

**读取 QPS**:
- Top-K 查询: $\sim 10K$ QPS (大屏刷新 + API 调用)
- 全部命中 Redis 缓存，无需回源

**Count-Min Sketch 内存**:
- 参数: $\epsilon = 0.001$, $\delta = 0.01$
- $w = \lceil e / 0.001 \rceil = 2718$
- $d = \lceil \ln(1/0.01) \rceil = 5$
- 单个 CMS = $2718 \times 5 \times 4$ bytes $= 54$ KB
- 每个时间窗口 1 个 CMS: 1m + 5m + 1h + 1d = 4 个 CMS $= 216$ KB
- 64 个分区 x 4 个 CMS = $64 \times 216$ KB $= 13.5$ MB (极小)

**Min-Heap 内存**:
- K = 1000 (维护 Top-1000)
- 每个条目 = 30 bytes (key) + 8 bytes (count) + 8 bytes (heap pointer) = 46 bytes
- 单个 Heap = $1000 \times 46 = 46$ KB
- 64 分区 x 4 窗口 = $64 \times 4 \times 46$ KB $= 11.5$ MB

**总流式内存**: CMS + Heap $\approx 25$ MB (可轻松放入单机)

**Kafka 存储**:
- 每条消息 ~500 bytes (批量聚合后)
- 200 batches/sec x 500 bytes = 100 KB/sec = $\sim 8.6$ GB/day
- 保留 7 天: $\sim 60$ GB

**批处理存储 (HDFS)**:
- 原始事件: $5 \times 10^9 \times 30$ bytes/day $= 150$ GB/day (压缩后 ~30 GB)
- 保留 90 天: $\sim 2.7$ TB

**总成本估算**:
- Flink 集群: 3 台 (16 core, 64GB RAM) $\approx$ $2,400/月
- Kafka 集群: 3 broker (8 core, 32GB, 500GB SSD) $\approx$ $1,800/月
- Redis: 1 台 (8GB RAM, 主从) $\approx$ $300/月
- Spark (每小时批处理): 按需实例 $\approx$ $500/月
- 总计: $\sim$ $5,000/月

### 核心算法

#### Count-Min Sketch 误差分析

设总事件数为 $N$，CMS 参数为 $(w, d)$:

$$\Pr[\hat{f}(\text{key}) - f(\text{key}) > \epsilon N] < \delta$$

其中 $\epsilon = e/w$, $\delta = e^{-d}$。

**实际误差示例**: $N = 5 \times 10^9$ (一天总事件), $\epsilon = 0.001$
-> 最大过估计 = $0.001 \times 5 \times 10^9 = 5 \times 10^6$

对于 Top-K 中频率 > $10^7$ 的元素，误差 < 50%，排名准确。
对于频率 $\sim 10^6$ 的边界元素，误差可能导致排名波动。

#### 多分区合并的正确性

每个分区只看到 key 空间的一个子集 (按哈希分区)。关键洞察:
**相同 key 的所有事件被路由到同一分区** (Kafka key-based partitioning)。

因此每个分区的 CMS 对其负责的 key 子集给出独立的近似计数，
全局 Top-K = 合并所有分区的局部 Top-K 后取前 K。

**合并误差**: 每个分区独立维护 Top-K，合并时可能遗漏"跨分区"的 heavy hitters。
但由于按 key 分区，不存在跨分区的 key——每个 key 恰好属于一个分区。
合并的唯一误差来源是 CMS 本身的过估计。

#### Min-Heap 维护

```python
import heapq

class TopKTracker:
    def __init__(self, k: int) -> None:
        self.k = k
        self.heap: list[tuple[int, str]] = []  # (count, key)
        self.key_set: set[str] = set()

    def update(self, key: str, count: int) -> None:
        if key in self.key_set:
            # 已在 heap 中: 需要更新 (简化版: 删除后重新插入)
            self.heap = [(c, k) for c, k in self.heap if k != key]
            heapq.heapify(self.heap)
            heapq.heappush(self.heap, (count, key))
        elif len(self.heap) < self.k:
            heapq.heappush(self.heap, (count, key))
            self.key_set.add(key)
        elif count > self.heap[0][0]:
            removed = heapq.heapreplace(self.heap, (count, key))
            self.key_set.discard(removed[1])
            self.key_set.add(key)
```
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints (Scale & Reliability)
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## 规模与可靠性 (Scale & Reliability)

### 具体规模数字

| 指标 | 数值 |
|------|------|
| DAU | 1 亿 |
| 日事件量 | 50 亿 |
| 峰值写入 QPS | 170K events/sec |
| 读取 QPS | 10K |
| 不同 key 基数 | ~5 亿 |
| 流式内存 | ~25 MB |
| Kafka 日存储 | 8.6 GB |
| 批处理日存储 | 30 GB (压缩) |
| Top-K 查询延迟 | P99 < 5ms |

### 单点故障分析 (SPOF Analysis)

| 组件 | 风险 | 缓解措施 |
|------|------|----------|
| **Kafka** | Broker 宕机 | 3 副本 + ISR (In-Sync Replicas)，min.insync.replicas=2 |
| **Flink** | TaskManager 崩溃 | Checkpoint 每 30 秒，故障后从 checkpoint 恢复，CMS 状态可序列化 |
| **Redis** | 主节点宕机 | Redis Sentinel 自动故障切换，从节点秒级提升为主 |
| **Global Merger** | 进程崩溃 | 无状态 (从分区读取 + 写入 Redis)，K8s 自动重启 |
| **Batch Pipeline** | Spark job 失败 | 重试 3 次 + 告警；流式结果仍可用作降级 |

### 多数据中心部署

**策略: 每区独立聚合 + 异步全局合并**

```
Region A (US-East)          Region B (EU-West)
  |                           |
  | Local Top-K               | Local Top-K
  |                           |
  v                           v
Regional Redis A            Regional Redis B
  |                           |
  +------> Async Merge <------+
              |
              v
         Global Redis (Primary Region)
```

- 每个区域独立运行完整的流式管道 (Kafka -> Flink -> Redis)
- **Global Merger** 通过跨区域 Kafka MirrorMaker 或直接 Redis 读取
  合并各区域的 Top-K
- 本地查询命中本区域 Redis (延迟 < 5ms)，全局查询命中 Primary Redis
  (延迟 ~50ms)

**冲突解决**: Top-K 合并是**幂等且交换的** (取 max count)。
两个区域对同一 key 报告不同 count，取较大值即可。

### 高并发处理

**写入侧 (数据摄入)**:
- **本地聚合 (Client-side Batching)**: 应用主机每 5 秒 flush，将 1000 台
  主机的 170K events/sec 聚合为 200 batches/sec
- **Kafka 分区**: 64 分区，每分区 ~2700 events/sec (聚合后)
- **Flink 并行度**: 与 Kafka 分区数匹配，每个 Task 处理一个分区

**读取侧 (查询)**:
- **Redis 缓存**: 所有查询命中 Redis，不回源
- **Rate Limiting**: 每客户端 100 QPS 限制
- **Circuit Breaker**: Redis 不可用时返回上一次缓存的结果 (stale but available)

### 优雅降级 (Graceful Degradation)

当系统压力过大时，按优先级逐步降级:

1. **Level 1**: 增加本地聚合窗口 (5s -> 15s)，减少 Kafka 压力
2. **Level 2**: 降低 CMS 精度 ($\epsilon$ 放大 2x)，减少内存和计算
3. **Level 3**: 关闭非核心时间窗口 (只保留 1h 和 1d)
4. **Level 4**: 切换为纯批处理模式，流式管道暂停

### 监控与告警

**关键指标**:
- **Kafka Consumer Lag**: > 5 分钟告警，> 15 分钟触发降级
- **CMS 精度**: 流式 vs 批处理的 Kendall's $\tau$ < 0.85 告警
- **Flink Checkpoint 耗时**: > 30 秒告警 (正常 < 5 秒)
- **Redis 内存使用率**: > 80% 告警
- **Top-K 查询 P99 延迟**: > 10ms 告警
- **事件丢弃率 (Drop Rate)**: > 0.1% 告警
"""

# ---------------------------------------------------------------------------
# S6: Trade-offs
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## 权衡分析 (Trade-off Discussion)

### 关键设计决策

| 决策 | 选项 A | 选项 B | 我们的选择与原因 |
|------|--------|--------|------------------|
| 计数方法 | **精确 HashMap** (准确, 内存 $O(n)$) | **Count-Min Sketch** (近似, 内存 $O(1/\epsilon)$) | **CMS**: 5 亿 key 的 HashMap 需要 ~30 GB; CMS 只需 54 KB, 差 500000x。Top-K 场景下近似排名足够 |
| 流式框架 | **Kafka Streams** (轻量, 嵌入式) | **Apache Flink** (重量级, 独立集群) | **Flink**: 需要有状态窗口聚合 + checkpoint, Flink 的 RocksDB state backend 和 exactly-once 保证更成熟。Kafka Streams 适合更简单的无状态转换 |
| 架构模式 | **Kappa Architecture** (只有流) | **Lambda Architecture** (流 + 批) | **Lambda**: 流式 CMS 有累积误差, 批处理每小时校准。Kappa 更简单但精确度无保证 |
| 分区策略 | **按 key 哈希** | **按时间范围** | **按 key 哈希**: 确保相同 key 的所有事件到达同一分区, CMS 计数准确。按时间分区会导致同一 key 分散在多个分区, 合并复杂 |
| Top-K 数据结构 | **Min-Heap** ($O(\log K)$ 更新) | **Sorted Array** ($O(K)$ 插入) | **Min-Heap**: K=1000 时 $\log K = 10$, 比线性扫描快 100x。且堆顶即最小值, 可快速判断是否需要插入 |

### CAP 定理应用

Top-K Heavy Hitters 系统选择 **AP (可用性 + 分区容忍)**:

- **分区 (Partition)**: Kafka + Flink 天然分布式, 网络分区不可避免
- **可用性 (Availability)**: Top-K 结果过时几秒可接受, 不可用不可接受
  (监控大屏空白 = 运维盲区)
- **一致性 (Consistency)**: 不同节点的 Top-K 允许短暂不一致。
  一个区域看到的 #1 热搜可能在另一个区域排 #3, 几秒后收敛

### 成本 vs 性能权衡

| 方案 | 月成本 | 延迟 | 精确度 |
|------|--------|------|--------|
| 纯批处理 (Spark 每小时) | $500 | 1 小时 | 精确 |
| 纯流式 (Flink + CMS) | $2,400 | 5 秒 | ~95% |
| **Lambda (流 + 批)** | **$5,000** | **5 秒** | **~95% 实时, 100% 每小时校准** |
| 精确流式 (Flink + HashMap) | $15,000+ | 5 秒 | 精确 |

我们选择 Lambda 架构: 成本适中, 实时性好, 且每小时有精确校准防止误差累积。

### 10x / 100x 规模变化

**10x (10 亿 DAU, 500 亿日事件)**:
- Kafka 分区从 64 扩展到 256
- Flink 集群从 3 台扩展到 12 台
- CMS 参数不变 (内存仍然极小)
- 本地聚合窗口从 5s 增加到 10s 以减少 Kafka 压力
- 增加一层**区域聚合** (每个数据中心先局部 Top-K)

**100x (100 亿 DAU, 5000 亿日事件)**:
- 需要**分层采样**: 对低频事件进行采样 (例如 10% 采样)，只精确追踪频率 > 阈值的 key
- Kafka 替换为自建的日志系统 (类似 LinkedIn 的 Kafka 起源)
- 批处理从 Spark 迁移到专用 OLAP 引擎 (如 **ClickHouse / Druid**)
- CMS 可能替换为 **Learned Heavy Hitters** (机器学习模型预测哪些 key 是 heavy hitter,
  对预测为 heavy 的用精确计数, 其余用 CMS)
"""

# ---------------------------------------------------------------------------
# S7: Defense (Interviewer Follow-up Q&A)
# ---------------------------------------------------------------------------
DEFENSE = r"""## 面试官追问 (Interviewer Follow-up Q&A)

### Q1: Count-Min Sketch 的过估计会不会导致 Top-K 结果完全不可信？

**承认局限**: CMS 确实只会过估计, 且对低频 key 的过估计比例更大。
当多个 key 哈希冲突时, 它们的计数会相互"污染"。

**缓解措施**:
1. **Conservative Update**: 只更新 CMS 中值最小的行, 减少过估计:
   对每行 $i$, 只在 $\text{CMS}[i][h_i(key)] = \min_j \text{CMS}[j][h_j(key)]$
   时才 +1。这将平均误差降低约 50%
2. **Count-Min-Log Sketch**: 用对数计数器替代线性计数器,
   牺牲少量精度换取更小内存
3. **批处理校准**: 每小时的精确 Top-K 覆盖流式结果, 误差不会累积超过 1 小时
4. **只关心相对排名**: Top-K 的消费者通常关心"谁是前 10"而非精确计数。
   CMS 的过估计是均匀的, 对相对排名影响较小

**数据支撑**: 在 $\epsilon = 0.001$ 配置下, 对于频率 > $N/1000$ 的 heavy hitters
(即出现次数占总事件数 0.1% 以上), 排名准确率 > 98%。

### Q2: 如果 Flink 集群宕机, 流式 Top-K 完全不可用怎么办？

**承认影响**: Flink 宕机意味着流式管道停止, 新事件不再被处理。
但 Redis 中的上一次 Top-K 结果仍然可读。

**缓解措施**:
1. **Stale Result Serving**: Redis 中的 Top-K 带时间戳, 查询 API 返回时附带
   "data_age" 字段。如果 age > 5 分钟, 客户端显示"数据可能过时"警告
2. **Checkpoint 恢复**: Flink checkpoint 每 30 秒, 故障后从最近 checkpoint
   恢复, 丢失最多 30 秒数据
3. **Kafka 持久化**: 事件在 Kafka 中保留 7 天, Flink 恢复后可以回放
   (replay) 丢失的窗口
4. **降级到批处理**: 如果 Flink 长时间不可用 (> 30 分钟), 触发紧急 Spark job
   处理最近数据

### Q3: 本地聚合 (5 秒窗口) 会不会导致短时突发被平滑掉？

**承认局限**: 是的, 5 秒聚合窗口意味着任何持续时间 < 5 秒的突发事件
在本地聚合时会被平均化, 峰值被削平。

**缓解措施**:
1. **动态窗口**: 当本地计数器检测到某个 key 的增长率超过阈值
   (例如 5 秒内增长 10x), 立即 flush 该 key 的计数, 不等窗口结束
2. **采样旁路**: 对随机 1% 的事件绕过本地聚合, 直接发送到 Kafka,
   作为突发检测的"哨兵信号"
3. **双精度策略**: 对已知的 Top-K 候选 key (上一轮的 Top-1000),
   在本地不聚合, 直接发送。对长尾 key 才聚合

**权衡**: 更短的聚合窗口 (如 1 秒) 能捕获更细粒度的突发,
但 Kafka 写入量增加 5x。需要根据业务对"突发敏感度"的需求调整。

### Q4: 这个系统能否处理"突然一个全新的 key 变成 Top-1"的场景？

**场景**: 一个之前从未出现过的 key (例如突发新闻关键词) 在几秒内收到海量事件。

**分析**:
1. **CMS 无冷启动问题**: CMS 不需要"注册" key, 任何 key 都可以直接 Add + Query,
   新 key 的计数从 0 开始正常累积
2. **Min-Heap 快速反应**: 只要新 key 的 CMS 估计频率超过堆顶最小值,
   它就会被插入 Top-K。在 5 秒聚合 + 5 秒合并周期内, 最快 10 秒内出现在全局 Top-K
3. **本地聚合延迟**: 如果新 key 只出现在少数主机上, 本地聚合后的 count
   可能不够大。但如果是全局热点 (多台主机同时看到), 聚合后 count 会很高

**最坏情况延迟**: 新 key 出现 -> 5 秒本地聚合 -> Kafka -> Flink 处理 -> 5 秒
Top-K 快照 -> Global Merge -> Redis 写入。**总延迟 ~10-15 秒**。

### Q5: 如果我们需要精确的 Top-K (不接受近似), 架构会如何变化？

**方案调整**:
1. **替换 CMS 为分布式 HashMap**: 用 **Redis Sorted Set** 或
   **分布式 HashMap (如 Hazelcast)** 对每个 key 精确计数
2. **内存代价**: 5 亿 key x (30 bytes key + 8 bytes count) = ~19 GB,
   需要分片到多台 Redis 实例
3. **写入放大**: 每个事件需要一次 Redis ZINCRBY, 170K events/sec
   需要 Redis 集群 (而非单机)
4. **保留批处理**: 批处理管道不变, 但不再作为"校准"而是"验证"
5. **成本增加**: 从 $5K/月 增加到 ~$15K/月 (主要是 Redis 集群成本)

**面试建议**: 先提出近似方案 (CMS), 然后主动说"如果业务要求精确, 可以替换为
分布式 HashMap, 但成本增加 3x"。这展示了你理解权衡。
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (1-Hour Interview Pacing Guide)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## 面试节奏指南 (1-Hour Interview Pacing Guide)

### 3 分钟电梯演讲版 (Elevator Pitch)

"Top-K Heavy Hitters 的核心挑战是: 数据量太大无法精确计数所有元素。
我的方案采用三层架构:
1) **本地聚合** -- 应用主机每 5 秒 flush 部分计数, 将百万级 QPS 降到百级
2) **分区流处理** -- Flink 按 key 哈希分区, 每个分区用 **Count-Min Sketch** 近似计数
   + **Min-Heap** 维护局部 Top-K, 全部只需 25 MB 内存
3) **全局合并** -- 每 5 秒合并所有分区的 Top-K, 写入 Redis 供查询

近似精度 ~95%, 端到端延迟 ~10 秒。每小时跑一次精确的批处理 Top-K 作为校准,
防止 CMS 误差累积。这就是经典的 **Lambda Architecture**。"

### 完整 1 小时面试节奏

#### 0-5 分钟: 需求澄清

**开场**: "Top-K Heavy Hitters 有两个关键维度需要先确认:
规模和精确度要求。"

**必须澄清的问题**:
1. "元素基数多大？百万级可以精确 HashMap, 十亿级需要概率数据结构"
2. "能接受近似结果吗？CMS 可以将内存从 30 GB 降到 54 KB"
3. "需要多少时间窗口？每增加一个窗口, 状态存储线性增长"
4. "结果消费者是实时大屏还是离线分析？决定延迟要求"

**画出需求框架**:
```
FR: Top-K 查询, 多时间窗口, 近实时更新
NFR: 170K writes/sec, <50ms 查询延迟, ~95% 精确度
```

#### 5-15 分钟: 高层架构

**画三层图**: "我的设计分三层——本地聚合、分区流处理、全局合并"

**逐层解释**:
- **本地聚合**: "为什么不直接发到 Kafka？因为 1000 台主机 x 170K/sec
  = Kafka 压力太大。本地先按 key 聚合 5 秒, 将事件流压缩 1000x"
- **分区流处理**: "为什么按 key 分区？确保同一 key 的所有事件到达同一分区,
  CMS 计数才准确"
- **全局合并**: "为什么需要全局合并？每个分区只知道自己负责的 key 的 Top-K,
  全局 Top-K 需要跨分区合并"

**数据库选型**: "流式状态在 Flink 内存 (RocksDB backend),
结果缓存在 Redis (Sorted Set), 历史数据在 HDFS (Parquet)"

#### 15-40 分钟: 深入讨论 (选 2-3 个最有趣的组件)

**深入点 1: Count-Min Sketch** (~8 分钟)
- 画出 $d \times w$ 矩阵
- 解释 Add 和 Query 操作
- 推导误差界: $\Pr[\hat{f} - f > \epsilon N] < \delta$
- 讨论 Conservative Update 优化
- "面试技巧: 提到 CMS 的局限——只能过估计, 不能低估。
  如果需要无偏估计, 可以用 Count Sketch (允许负值的变体)"

**深入点 2: 多时间窗口聚合** (~8 分钟)
- 解释 CMS 的可加性 (两个 CMS 逐元素相加)
- 画出层级时间轮: 5s -> 1m -> 5m -> 1h -> 1d
- 滑动窗口: 加入新 CMS + 减去过期 CMS (环形缓冲区)
- "关键洞察: CMS 的可加性使得时间窗口聚合几乎零额外成本"

**深入点 3: Lambda Architecture 与校准** (~8 分钟)
- 为什么需要批处理? CMS 误差会累积
- 批处理如何校准: 每小时精确 Top-K 覆盖 Redis
- Kendall's $\tau$ 监控: 流式 vs 批处理排名一致性
- "如果 $\tau < 0.85$, 说明 CMS 参数需要调优"

#### 40-50 分钟: 权衡与扩展讨论

**主动提出**: "让我讨论三个关键权衡"

1. **精确 vs 近似**: "CMS 用 54 KB 替代 30 GB HashMap,
   代价是 ~5% 的排名误差。对 Top-K 场景, 这是值得的"
2. **Lambda vs Kappa**: "我选 Lambda 因为 CMS 有累积误差需要校准。
   如果用精确计数 (HashMap), 可以用 Kappa (纯流式)"
3. **本地聚合窗口**: "5s 窗口将 Kafka 压力降低 1000x,
   但可能平滑掉 <5s 的突发。可以用动态窗口缓解"

**10x/100x 规模**: "10x 主要是水平扩展 (更多 Kafka 分区 + Flink 并行度)。
100x 需要分层采样 + 可能替换 CMS 为 Learned Heavy Hitters"

#### 50-55 分钟: 收尾

**我会改进什么**:
- 添加**维度切分** (per-country, per-device Top-K)
- 实现 **Learned Heavy Hitters** 替代 CMS, 用 ML 模型预测哪些 key 是 heavy hitter
- 添加**突发检测层** (Z-Score 异常检测)

**监控清单**:
- Kafka consumer lag
- CMS 精度 (Kendall's $\tau$)
- Flink checkpoint 耗时
- Redis 内存使用率

#### 55-60 分钟: 向面试官提问

- "你们的 Top-K 系统目前用的是精确计数还是概率数据结构？"
- "数据量级大概是什么量级？日事件量在什么范围？"
- "Top-K 结果的下游消费者主要是什么？实时大屏还是异常检测系统？"

---

### 面试核心要点总结

关键设计决策:
- **CMS 而非 HashMap**: 内存从 30 GB 降到 54 KB, 代价是 ~5% 排名误差
- **三层聚合**: 本地 (降压 1000x) -> 分区 (CMS + Heap) -> 全局 (合并 Top-K)
- **Lambda Architecture**: 流式 (5s 延迟, 近似) + 批处理 (1h, 精确校准)
- **按 key 哈希分区**: 确保同一 key 的所有事件在同一分区, CMS 计数准确
- **CMS 可加性**: 多个时间窗口的 CMS 可直接相加, 零额外成本

规模: 1 亿 DAU, 50 亿日事件, 170K 峰值 QPS, 25 MB 流式内存,
~$5K/月 (极低成本)。"
"""


def populate_interview_top_k() -> None:
    """Create or update the interview-top-k-heavy-hitters record with all 8 sections."""
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
    populate_interview_top_k()
