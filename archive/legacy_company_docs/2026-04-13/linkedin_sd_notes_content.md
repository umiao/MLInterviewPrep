# LinkedIn 系统设计面试准备笔记 (一亩三分地面经整理)

> **来源**: 一亩三分地面经整理 + Discord 补充
> **公司**: LinkedIn
> **适用岗位**: MLE / Software Engineer / Senior SDE
> **难度**: Onsite System Design Round (30-45 min)

---

## 目录

1. [Typeahead / Autocomplete System](#1-typeahead--autocomplete-system)
2. [Recommendation System (Short Video)](#2-recommendation-system-short-video)
3. [Metrics Monitoring / Exception Monitoring](#3-metrics-monitoring--exception-monitoring)
4. [Job Scheduler](#4-job-scheduler)
5. [KV Store (Single Machine)](#5-kv-store-single-machine)
6. [Personalized InMail (LLM-powered)](#6-personalized-inmail-llm-powered)
7. [Top K Search Words](#7-top-k-search-words)
8. [Ranking System](#8-ranking-system)
9. [isMalicious API](#9-ismalicious-api)
10. [LinkedIn Skills (Data Mining)](#10-linkedin-skills-data-mining)
11. [Inverted Document Search](#11-inverted-document-search)

---

## 1. Typeahead / Autocomplete System

### 题目描述

设计一个 typeahead suggestions 系统。当用户在搜索框中输入字符时，实时返回可能的补全建议（如搜索人名、公司、职位等）。LinkedIn 面试中出现频率较高，属于经典题。

### 需求分析

**Functional Requirements (功能需求)**:
- 用户输入 prefix 后，返回 top-K（通常 K=5~10）最相关的补全建议
- 支持按热度/个性化排序
- 返回结果需包含不同类型（人、公司、职位、技能）
- 支持多语言输入

**Non-Functional Requirements (非功能需求)**:
- **低延迟**: P99 < 100ms，用户每输入一个字符就要返回结果
- **高可用**: 99.99% availability
- **实时性**: 热点搜索词应在分钟级别被收录
- **规模**: 数亿用户，每秒百万级查询

### 架构设计

系统分为两大部分: **Data Collection Pipeline** 和 **Serving Layer**。

```
用户输入 -> API Gateway -> Typeahead Service -> Trie Cache (in-memory)
                                              -> Personalization Service
                                              -> Result Blender (merge + rank)

离线:  Search Logs -> Aggregation Pipeline -> Trie Builder -> Deploy to Trie Cache
```

**Data Collection Pipeline**: 收集搜索日志，按时间窗口（如过去7天）聚合搜索词频率，构建/更新 Trie。

**Serving Layer**: 接收用户请求，在内存中的 Trie 上做 prefix matching，结合个性化信号排序后返回。

### 核心组件

- **Trie (前缀树)**: 存储所有候选搜索词。每个节点存储字符，叶节点或标记节点存储完整词和对应的全局热度分数。为了加速查询，可以在每个节点预存 top-K 结果（空间换时间）。
- **Ranking Module**: 对 Trie 返回的候选词进行排序。排序因子包括: 全局热度（search volume）、个性化分数（用户历史搜索、connections、行业）、时效性（trending）。
- **Trie Cache Layer**: 使用分布式缓存（如 Redis cluster），每台机器持有一部分 prefix range（按首字母分片）。热门 prefix 可以 replicate 到多台机器。
- **Aggregation Pipeline**: 离线/近实时 pipeline（Kafka + Spark/Flink），聚合搜索日志，周期性（每小时/每天）重建 Trie 并推送到 serving 节点。

### 数据流

1. 用户在搜索框输入 "sof"
2. 前端 debounce 50ms 后发送请求到 API Gateway
3. API Gateway 路由到 Typeahead Service
4. Typeahead Service 查询 Trie Cache，获取 prefix="sof" 的 top-20 候选词
5. 结合用户画像（行业、地理位置、搜索历史）做个性化 re-rank
6. 返回 top-5 结果: ["software engineer", "software developer", "Sofi", ...]
7. 前端渲染下拉建议列表

### 关键设计决策

| 决策点 | 选项 A | 选项 B | 选择与理由 |
|--------|--------|--------|-----------|
| 数据结构 | Trie | Sorted set (Redis) | Trie: prefix match 是 O(L)，且可预存 top-K |
| 更新策略 | 实时更新 | 批量重建 | 批量重建 + 增量更新混合: 避免实时更新带来的锁竞争 |
| 分片策略 | 按 prefix 分片 | 按 hash 分片 | 按 prefix 分片: 保证同一 prefix 的数据在同一节点 |
| 个性化 | 查询时计算 | 预计算 | 混合: 全局排序预计算，个性化在查询时叠加 |

### 面试话术

> "我会从两个维度来设计这个系统: serving path 和 data pipeline。Serving path 的核心是一个分布式的 Trie，每个节点预存 top-K 结果以保证 O(L) 的查询延迟。Data pipeline 使用 Kafka 收集搜索日志，Flink 做近实时聚合，每小时重建一次 Trie 并通过 blue-green deployment 推送到 serving 节点。个性化方面，我会在查询时结合用户画像做轻量级 re-rank，而不是为每个用户维护独立的 Trie。"

---

## 2. Recommendation System (Short Video)

### 题目描述

设计一个 short video 推荐系统。面试中多次出现，LinkedIn 面试官会要求从 label 定义、数据收集、feature engineering 一直讲到推荐系统的三段式架构（recall/ranking/re-rank），并详细讨论 offline evaluation 方法。面经中提到"划走=negative feedback"是一个关键信号。出现频率最高(5次)。

### 需求分析

**Functional Requirements**:
- 用户打开 feed 时，推荐个性化的 short video 列表
- 支持多种隐式反馈: 播放完成率、点赞、评论、分享、划走（swipe away）
- 新用户冷启动
- 内容安全过滤

**Non-Functional Requirements**:
- **低延迟**: 推荐列表生成 < 200ms
- **吞吐**: 支持百万级 DAU 的并发请求
- **实时性**: 用户最近行为应在秒级影响后续推荐（session-based 实时调整）

### 架构设计

经典的三段式 (Multi-stage) 推荐架构:

```
用户请求 -> Recall (召回, ~1000 candidates)
         -> Pre-ranking (粗排, ~200)
         -> Ranking (精排, ~50)
         -> Re-ranking (重排/多样性/业务规则, ~20)
         -> 返回给用户
```

### 核心组件

- **Recall (召回层)**: 多路召回并行执行
  - **Collaborative Filtering 路**: 基于 user-item 交互矩阵，使用 ALS 或 item2vec
  - **Content-based 路**: 基于视频内容特征（标题、标签、视觉特征）与用户画像的相似度
  - **热门/Trending 路**: 近期高互动视频，解决冷启动问题
  - **Social 路**: 用户 connections 看过/点赞的视频（LinkedIn 特色）
  - 合并去重后约 1000 个候选

- **Ranking (排序层)**: 使用 deep learning 模型（如 Wide & Deep, DeepFM, 或 multi-task model）
  - **Features**: user features（行业、职级、活跃度）、item features（视频时长、创建者、标签）、context features（时间、设备）、cross features（用户-视频交互历史）
  - **Label 定义**: 这是面试重点
    - **Positive**: 播放完成率 > 70%、点赞、评论、分享
    - **Negative**: 划走（swipe away / skip < 2s）、"不感兴趣" 按钮
    - **Weighted**: 不同行为赋予不同权重，如 share > like > complete > click
  - **Multi-task**: 同时预测 P(click), P(complete), P(like), P(share)，最终分数为加权组合

- **Re-ranking (重排层)**: 业务规则和多样性保证
  - 多样性打散: 同一创作者的视频不连续出现
  - 内容安全过滤
  - 广告插入位 (ad slot)
  - 新内容 exploration（epsilon-greedy 或 Thompson Sampling）

- **实时信号处理**: 用户 session 内的行为（如连续划走3个美食视频）应实时调整推荐
  - 使用 Kafka stream + feature store（如 Redis）实时更新用户 session features
  - Ranking model 的输入中包含 "最近5分钟行为" 类特征

### 数据流

1. 用户打开 video feed
2. 请求发送到 Recommendation Service
3. 多路 Recall 并行执行，合并约 1000 候选
4. 从 Feature Store 获取 user features + item features
5. Ranking model 打分排序，取 top-50
6. Re-ranking 做多样性打散和业务规则过滤
7. 返回 top-20 给前端，前端预加载前3个视频
8. 用户行为（播放、划走等）实时写入 Kafka -> 更新 Feature Store

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Label 定义 | Multi-label weighted | 单一 label（如 click）无法捕捉用户真实偏好深度 |
| 划走信号 | 作为 explicit negative | 划走是用户主动行为，信号强于单纯的"未点击" |
| 实时 vs 离线 | 混合 | 模型离线训练，特征实时更新；平衡效果与成本 |
| 冷启动 | 热门 + content-based | 新用户无交互历史，依赖内容特征和全局热门 |

### 面试话术

> "推荐系统我会用经典的多段式架构: 召回层做多路召回保证覆盖率，排序层用 multi-task deep model 预测多个目标（点击率、完播率、互动率），重排层做多样性和业务规则。Label 定义是关键 -- 我会把划走作为强 negative signal，播放完成率>70% 作为 positive。实时性方面，用户 session 内的行为通过 Kafka 实时更新 Feature Store，确保下一次刷新就能反映用户最新偏好。"

---

## 3. Metrics Monitoring / Exception Monitoring

### 题目描述

设计一个 metrics monitoring 平台（类似 Datadog / Prometheus），用于收集、聚合和展示系统指标。面经中也出现了 exception monitoring 的变体: 设计一个系统向 oncall 显示 top-K 异常。面试官特别关注**如何收集 exception** 以及 **DB schema 设计**。出现频率高(3次，含 exception monitoring 变体)。

### 需求分析

**Functional Requirements**:
- 各服务通过 SDK 上报 metrics（counter, gauge, histogram, timer）
- 支持多维度查询: 按 service、host、region、时间范围
- Dashboard 展示: 时间序列图表
- Exception monitoring 变体: 实时显示 top-K 异常类型及其频率
- 不需要 alerting（面经明确说明）

**Non-Functional Requirements**:
- **写入吞吐**: 每秒百万级 metrics 数据点
- **查询延迟**: Dashboard 查询 < 1s
- **数据保留**: 近期数据高精度（秒级），历史数据降采样（分钟/小时级）
- **高可用**: 监控系统本身不能挂

### 架构设计

```
服务集群 -> Metrics Agent (per-host) -> Kafka -> Aggregation Service -> TSDB
                                                                     -> Dashboard Service -> Web UI
Exception 变体:
服务集群 -> Exception Collector -> Kafka -> Stream Processor (count + top-K) -> Redis -> Dashboard
```

### 核心组件

- **Metrics Agent (采集端)**: 每台机器上运行的轻量级 agent，负责本地预聚合（如10秒窗口内的 count/sum/avg），然后批量发送到 Kafka。预聚合可以显著减少网络传输量。技术选型: StatsD / Telegraf。

- **Kafka (消息队列)**: 解耦采集端和存储端。按 metric name hash 分 partition，保证同一 metric 的数据有序。

- **Aggregation Service (聚合层)**: 消费 Kafka 数据，做进一步聚合:
  - 时间维度: 将秒级数据聚合为分钟级
  - 空间维度: 将同一 service 的多台 host 数据合并
  - 降采样 (downsampling): 超过7天的数据从分钟级降为小时级，超过30天降为天级

- **TSDB (时序数据库)**: 存储聚合后的 metrics。技术选型:
  - InfluxDB / TimescaleDB (PostgreSQL extension) / 自研（LinkedIn 实际使用自研方案）
  - Schema 设计: `(metric_name, tags, timestamp, value)` -- tags 是 key-value pairs，如 `{service: "feed", host: "host-123", region: "us-west"}`

- **Exception Monitoring 特殊组件**:
  - **Exception Collector**: 接收各服务抛出的异常，提取 exception type + stack trace fingerprint
  - **Stream Processor**: 使用滑动窗口（如过去1小时）统计每种异常的出现次数，维护 top-K 堆
  - **DB Schema** (面试官特别关注):
    ```
    exceptions (
        id BIGINT PRIMARY KEY,
        service_name VARCHAR,
        exception_type VARCHAR,
        stack_trace_hash VARCHAR,  -- fingerprint
        message TEXT,
        host VARCHAR,
        timestamp TIMESTAMP,
        count INT  -- 预聚合后的计数
    )
    exception_aggregates (
        exception_type VARCHAR,
        time_bucket TIMESTAMP,  -- 按分钟/小时聚合
        count INT,
        PRIMARY KEY (exception_type, time_bucket)
    )
    ```

### 数据流

1. 服务代码中调用 SDK: `metrics.increment("api.request.count", tags={"endpoint": "/feed"})`
2. Agent 在本地缓存，每10秒 flush 一次到 Kafka
3. Aggregation Service 消费 Kafka，按 (metric_name, tags, minute) 聚合
4. 写入 TSDB
5. Dashboard 查询: "过去1小时 feed service 的 QPS" -> 查询 TSDB 并渲染图表

Exception 变体:
1. 服务抛出异常，Exception SDK 捕获并发送到 Exception Collector
2. Collector 提取 exception_type + stack_trace_hash，发送到 Kafka
3. Stream Processor 消费，更新滑动窗口内的 count
4. 维护 min-heap (size K) 来追踪 top-K 异常
5. 结果写入 Redis，Dashboard 轮询 Redis 展示 top-K

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 预聚合位置 | Agent 端 + Server 端两级聚合 | Agent 端减少网络流量，Server 端做跨机器聚合 |
| 存储 | TSDB (非关系型DB) | 时序数据的写入和范围查询模式完美匹配 TSDB 的列式存储 |
| 降采样 | 自动分层 | 近期高精度、历史低精度，平衡存储成本和查询需求 |
| Top-K 实现 | Stream + Min-Heap | 数据量大，精确 top-K 比 approximate 更适合 monitoring 场景 |

### 面试话术

> "这个系统的核心挑战是高吞吐写入和灵活的多维查询。我会分三层设计: 采集层用 per-host agent 做本地预聚合减少网络开销；传输层用 Kafka 解耦并保证可靠性；存储层用时序数据库做分层存储和自动降采样。对于 exception monitoring 变体，关键是定义好 exception 的 fingerprint（按 stack trace hash），然后用滑动窗口 + min-heap 维护实时 top-K。"

---

## 4. Job Scheduler

### 题目描述

设计一个 Job Scheduler 系统，支持定时任务调度和分布式执行。Follow-up 问题: 如何高效查询未来 N 小时内要执行的任务（用于构建 realtime dashboard）。出现频率较高(2次)，面试官问得非常细致。

### 需求分析

**Functional Requirements**:
- 用户可以创建一次性定时任务或周期性任务 (cron-like)
- 支持任务优先级
- 任务执行失败后可重试（configurable retry policy）
- 查询未来 N 小时内将执行的任务列表（dashboard）
- 任务执行状态追踪

**Non-Functional Requirements**:
- **可靠性**: 任务不能丢失，不能重复执行（at-least-once with idempotency）
- **可扩展**: 支持百万级定时任务
- **低延迟调度**: 任务应在预定时间的秒级精度内被触发
- **高可用**: scheduler 本身不能成为单点故障

### 架构设计

```
用户/API -> Scheduler Service -> Task Store (DB)
                              -> Time-based Partitioner
                              -> Priority Queue (per-partition)
                              -> Worker Pool (执行集群)
                              -> Status Tracker -> Dashboard
```

### 核心组件

- **Scheduler Service (调度服务)**: 无状态服务，接收任务创建/查询请求。核心逻辑:
  - 将任务写入 Task Store
  - 周期性（每分钟）扫描"即将到期"的任务，推入执行队列
  - 使用分布式锁（如 ZooKeeper/Redis）避免多个 Scheduler 实例重复扫描

- **Task Store (任务存储)**:
  ```
  tasks (
      task_id UUID PRIMARY KEY,
      owner_id VARCHAR,
      task_type ENUM('one_time', 'recurring'),
      cron_expression VARCHAR,  -- for recurring tasks
      next_execution_time TIMESTAMP,  -- 关键字段，建立索引
      payload JSON,
      priority INT,
      status ENUM('scheduled', 'queued', 'running', 'completed', 'failed'),
      retry_count INT DEFAULT 0,
      max_retries INT DEFAULT 3,
      created_at TIMESTAMP,
      updated_at TIMESTAMP
  )
  INDEX idx_next_exec ON tasks(next_execution_time, status)
  ```
  **Follow-up 关键**: `next_execution_time` 上建 B-Tree 索引，查询 "未来 N 小时内的任务" 就是 `WHERE next_execution_time BETWEEN now() AND now() + N hours AND status = 'scheduled'`，利用索引可以高效执行。

- **Priority Queue**: 从 DB 扫描出来的任务按 priority 放入内存优先队列（可用 Redis Sorted Set，score = priority * 权重 + timestamp）。Worker 从队列中 pull 任务。

- **Worker Pool (执行集群)**: 无状态 worker 节点，从 Priority Queue 中获取任务并执行。执行完成后更新 Task Store 中的 status。失败时根据 retry policy 决定是否重新入队。

- **Recurring Task 处理**: 任务完成后，Scheduler 根据 cron_expression 计算 next_execution_time，更新 DB 记录。

### 数据流

1. 用户创建任务: `POST /tasks {cron: "0 9 * * 1", payload: {...}}`
2. Scheduler 计算 next_execution_time，写入 Task Store
3. Scheduler 的 polling loop 每分钟执行: `SELECT * FROM tasks WHERE next_execution_time <= now() + 1min AND status = 'scheduled'`
4. 匹配的任务 status 更新为 'queued'，推入 Priority Queue
5. Worker pull 任务，status 更新为 'running'
6. 执行完成 -> status = 'completed'；如果是 recurring，计算新的 next_execution_time
7. 执行失败 -> 如果 retry_count < max_retries，重新入队；否则 status = 'failed'

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 调度方式 | DB polling + 内存队列 | 简单可靠；DB 保证持久化，内存队列保证低延迟 |
| 去重 | 分布式锁 + status 状态机 | 多个 Scheduler 实例通过锁协调，避免重复推送 |
| 查询优化 | B-Tree index on next_execution_time | Follow-up 的关键答案；range query 在 B-Tree 上是 O(log N + K) |
| 失败处理 | Exponential backoff retry | 避免对下游服务造成额外压力 |

### 面试话术

> "我会把 Job Scheduler 分为调度层和执行层。调度层的核心是一个 polling-based scheduler，每分钟扫描 DB 中 next_execution_time 即将到期的任务，推入 Redis Sorted Set 作为优先队列。执行层是无状态的 Worker Pool，通过竞争消费队列中的任务。对于 follow-up 的 dashboard 查询，关键是在 next_execution_time 上建 B-Tree 索引，这样 range query 就是 O(log N + K)，可以高效支持'查看未来 N 小时任务'的需求。"

---

## 5. KV Store (Single Machine)

### 题目描述

设计一个单机的 key-value store。注意: **不是分布式系统**，只有单机。只允许使用 map 来实现一个 low-level KV store。文件系统可用于持久化，支持创建/删除 file，每个 file append-only，file 总数不超过 100K，但要支持 1 billion keys。Value 是 MB 级别，不可全部 persist 在 memory 中。出现频率高(3次)。

### 需求分析

**Functional Requirements**:
- `put(key, value)`: 写入 key-value pair
- `get(key)`: 读取 value
- `delete(key)`: 删除 key
- 数据需要持久化（重启后不丢失）
- 支持 1 billion keys，value 大小为 MB 级别

**Non-Functional Requirements**:
- **写入性能**: 高吞吐（append-only write 天然高效）
- **读取性能**: 尽可能低延迟
- **空间效率**: value 太大无法全放内存，但 key 的索引可以放内存
- **崩溃恢复**: 系统崩溃后能恢复数据

**Constraints (约束条件)**:
- 单机，非分布式
- File 总数 <= 100K
- 每个 file 只能 append
- 可以使用 map（HashMap）

### 架构设计

核心思路: **LSM-tree 的简化版** -- Bitcask 模型。

```
内存: HashMap<key, (file_id, offset, size)>  -- 索引
磁盘: Segment Files (append-only)

Write: append (key, value) to active segment file, update in-memory index
Read:  lookup index -> (file_id, offset) -> seek & read from file
Delete: append tombstone record, update index
```

### 核心组件

- **In-Memory Index (内存索引)**: 一个 HashMap，key 是用户的 key，value 是 `(file_id, byte_offset, value_size)`。1 billion keys, 每个 entry 约 (key avg 32B + metadata 24B) = ~56B，总计约 56GB -- 这太大了。
  - **优化**: 如果 key 太多放不下内存，可以用 **hash-partitioned index**: 将 key hash 到多个 partition，每个 partition 的索引文件存磁盘，只 cache 热门 partition 的索引。
  - 或者使用 **LSM-tree with SSTable**: 将内存索引限制在一定大小（memtable），满了就 flush 到磁盘形成 SSTable，查询时先查 memtable，再查各层 SSTable（使用 Bloom Filter 减少无效磁盘读取）。

- **Segment Files (数据文件)**: Append-only 的数据文件。每个 file 的格式:
  ```
  [key_size (4B)] [value_size (4B)] [key] [value] [CRC checksum (4B)]
  [key_size (4B)] [value_size (4B)] [key] [value] [CRC checksum (4B)]
  ...
  ```
  当一个 segment file 达到一定大小（如 256MB），关闭它并创建新的 active segment。

- **Compaction (合并压缩)**: 后台进程定期合并旧的 segment files:
  - 遍历多个旧 segment，对同一 key 只保留最新的 value
  - 移除 tombstone 标记的已删除 key
  - 生成新的合并后的 segment file
  - 原子替换索引中的指针，然后删除旧 segment files

- **Crash Recovery (崩溃恢复)**:
  - 方案1: 启动时遍历所有 segment files 重建内存索引（慢但简单）
  - 方案2: 定期将内存索引 snapshot 写到磁盘（hint file），启动时从 snapshot 恢复 + replay 最新 segment

### 数据流

**Write path**:
1. 将 (key, value) 序列化后 append 到当前 active segment file
2. 记录该条记录在文件中的 offset
3. 更新内存 HashMap: `index[key] = (active_file_id, offset, value_size)`

**Read path**:
1. 查内存 HashMap 获取 `(file_id, offset, size)`
2. 打开对应的 segment file，seek 到 offset，读取 size 字节
3. 反序列化得到 value

**Delete path**:
1. Append 一条 tombstone 记录到 active segment
2. 从内存 HashMap 中移除该 key

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 写入模式 | Append-only | 顺序写远快于随机写；天然支持崩溃恢复（不会写一半损坏数据）|
| 索引策略 | Hash index in memory | 1 billion keys 的 hash index 内存占用大，需要讨论 LSM-tree 优化 |
| B-tree vs LSM | LSM-tree | Append-only 约束下无法使用 B-tree（需要 in-place update）|
| Compaction | Size-tiered | 简单有效；写放大可接受 |

### 面试话术

> "在 append-only 和单机约束下，我会采用 Bitcask 模型: 所有写操作 append 到 segment file，内存中维护一个 HashMap 作为索引指向每个 key 在磁盘上的位置。由于有 1 billion keys，纯内存 HashMap 可能放不下，我会进一步讨论 LSM-tree 方案: 用 memtable + SSTable 分层存储索引，配合 Bloom Filter 减少不必要的磁盘查找。后台 compaction 负责合并旧 segment 并回收空间。"

---

## 6. Personalized InMail (LLM-powered)

### 题目描述

设计一个 AI-powered 的个性化 InMail 系统: recruiter 登录后看到候选人列表，选择一个候选人，系统拉取候选人信息、职位信息、recruiter 历史发送的消息，综合生成个性化的招聘消息。要求做整体 E2E 设计，包括 UI。出现频率(2次)。面经中提到楼主使用了"7步框架，包括 retrieval pipeline + LLM generation"。

### 需求分析

**Functional Requirements**:
- Recruiter 在 UI 上选择候选人和职位
- 系统自动生成个性化的 InMail 草稿
- Recruiter 可以编辑、预览、发送
- 支持多种 tone/style（formal, casual, technical）
- 生成内容需引用候选人的具体信息（如技能、经历、学校）

**Non-Functional Requirements**:
- **生成延迟**: < 3s（流式输出 streaming response）
- **质量**: 生成内容准确、个性化、不出现 hallucination
- **安全**: 不泄露其他候选人信息，不生成歧视性内容
- **成本**: LLM 调用成本需可控

### 架构设计

```
Recruiter UI -> API Gateway -> InMail Generation Service
                                 |-> Retrieval Pipeline:
                                 |     -> Candidate Profile Service (基本信息、技能、经历)
                                 |     -> Job Posting Service (职位要求)
                                 |     -> Recruiter History Service (历史消息、模板、成功案例)
                                 |     -> Context Assembler (组装 prompt context)
                                 |
                                 |-> LLM Generation:
                                 |     -> Prompt Builder (system prompt + context + instructions)
                                 |     -> LLM Service (GPT-4 / Claude / fine-tuned model)
                                 |     -> Streaming Response
                                 |
                                 |-> Post-processing:
                                       -> Content Safety Filter
                                       -> PII Check
                                       -> Grammar/Tone Validator
```

### 核心组件

- **Retrieval Pipeline (信息检索管道)**:
  - **Candidate Profile Service**: 从 LinkedIn 用户数据库拉取候选人的: 当前职位、工作经历、教育背景、技能列表、近期活动（发帖、互动）、shared connections
  - **Job Posting Service**: 获取职位的: JD 描述、required skills、company info、team info
  - **Recruiter History Service**: 获取该 recruiter 的: 历史 InMail 模板、过去成功的消息（高回复率的）、该 recruiter 的 writing style
  - **Context Assembler**: 将以上信息结构化组装，控制总 token 数不超过 context window 限制

- **Prompt Engineering**:
  ```
  System Prompt: 你是 LinkedIn 的招聘消息助手。根据以下信息生成个性化的 InMail。
  要求: 1) 提到候选人的具体技能和经历 2) 说明为什么这个职位适合他
  3) 保持 {tone} 风格 4) 长度控制在 200 字以内

  Candidate Info: {structured_candidate_info}
  Job Info: {structured_job_info}
  Recruiter Style Reference: {past_successful_messages}

  生成招聘消息:
  ```

- **LLM Service**:
  - 可选方案: 使用通用大模型 (GPT-4) vs fine-tuned 小模型
  - Fine-tuned 模型优势: 成本低、延迟低、更符合 LinkedIn tone
  - 训练数据: 历史高回复率的 InMail，recruiter 编辑后的最终版本（recruiter 修改量少的说明生成质量好）
  - **Streaming**: 使用 SSE (Server-Sent Events) 实现流式输出，提升用户体验

- **UI 设计** (面试要求讲 UI):
  - 左侧: 候选人列表 + 基本信息卡片
  - 右侧上方: 候选人详细信息 + 职位信息
  - 右侧下方: 生成的 InMail 草稿（支持实时编辑）
  - 工具栏: tone 选择（formal/casual）、regenerate 按钮、template 选择
  - 底部: 发送按钮 + 预览按钮

### 数据流

1. Recruiter 选择候选人 Alice 和职位 "Senior ML Engineer"
2. 前端发送请求: `POST /generate-inmail {candidate_id, job_id, tone: "professional"}`
3. InMail Service 并行调用三个数据源，获取候选人/职位/历史数据
4. Context Assembler 组装 prompt（控制在 4K tokens 以内）
5. 调用 LLM Service，使用 streaming 返回
6. 每个 token 经过 Content Safety Filter 检查
7. 流式推送到前端，UI 实时显示生成的文字
8. Recruiter 编辑后点击发送
9. 记录 recruiter 的编辑量（用于后续 fine-tuning 数据收集）

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| LLM 选型 | Fine-tuned 小模型 + 大模型 fallback | 小模型处理大部分请求（低成本），复杂场景 fallback 到大模型 |
| Context 组装 | 结构化模板 | 比 RAG 更可控，减少 hallucination |
| 流式输出 | SSE | 用户感知延迟从 3s 降到 <1s（第一个 token 时间）|
| 质量保证 | Recruiter 编辑追踪 | 编辑量作为隐式质量信号，用于持续改进模型 |

### 面试话术

> "我会用 retrieval pipeline + LLM generation 的架构。Retrieval 阶段并行拉取候选人信息、职位信息和 recruiter 的历史成功消息，组装成结构化的 prompt context。Generation 阶段使用 fine-tuned 模型生成初稿，通过 SSE 流式输出到前端。Post-processing 包括 content safety filter 和 PII check。关键的质量循环是: 追踪 recruiter 对生成内容的编辑量，编辑量少的样本作为 positive training data 持续 fine-tune 模型。"

---

## 7. Top K Search Words

### 题目描述

设计一个系统来找出 top-K 的搜索词。面经中有多个变体: 实时 top-K、过去1小时/1天的 top-K。有时与 exception monitoring 的 top-K 结合考察。出现频率高(3次)。

### 需求分析

**Functional Requirements**:
- 实时统计搜索词频率
- 返回过去 N 分钟/小时/天的 top-K 搜索词
- 支持 dashboard 实时展示

**Non-Functional Requirements**:
- **吞吐**: 每秒百万级搜索事件
- **近实时**: top-K 结果延迟 < 1min
- **准确度**: 可以接受近似解（approximate）但误差需可控
- **内存**: 不能存所有搜索词的精确计数

### 架构设计

```
Search Events -> Kafka -> Stream Processor (Flink/Spark Streaming)
                            |-> Count-Min Sketch (approximate counting)
                            |-> Min-Heap (size K, 维护 top-K)
                            |-> 定期 snapshot 到 Redis
Dashboard <- Redis
```

### 核心组件

- **Count-Min Sketch (近似计数器)**: 一种概率数据结构，使用 d 个 hash 函数和 w 列的 2D 数组来近似统计每个元素的出现次数。
  - 空间: O(w * d)，通常 w=2000, d=7，总共约 56KB 即可处理百万级不同搜索词
  - 查询某个词的频率: 取 d 个 hash 位置的最小值（因为 CMS 只会高估不会低估）
  - 误差: 与 w 成反比，可根据需求调整

- **Min-Heap (最小堆)**: 大小为 K 的最小堆，维护当前 top-K
  - 每来一个搜索词，在 CMS 中更新计数
  - 如果新计数 > 堆顶元素的计数，替换堆顶并 heapify
  - 堆中保存 (count, word) pair

- **Sliding Window (滑动窗口)**: 为了支持"过去 N 分钟的 top-K"，使用多个时间桶:
  - 每分钟一个 CMS + Heap
  - 查询时合并最近 N 个桶的数据
  - 过期的桶可以丢弃

- **精确方案 (小规模)**: 如果数据量不大，直接用 HashMap 计数 + 排序即可。面试中需要先问清规模。

### 数据流

1. 用户搜索 "machine learning"
2. 搜索事件写入 Kafka
3. Flink 消费事件:
   a. 更新当前时间桶的 Count-Min Sketch
   b. 获取该词的近似频率
   c. 如果频率 > 堆顶，更新 Min-Heap
4. 每秒将 top-K 结果 snapshot 到 Redis
5. Dashboard 从 Redis 读取展示

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 计数方式 | Count-Min Sketch | 空间效率极高，适合大规模流数据；只高估不低估 |
| Exact vs Approximate | Approximate | 精确方案需要 O(N) 空间；CMS 的误差在实践中可接受 |
| 时间窗口 | 分桶 (bucketed) | 比真正的滑动窗口实现简单，精度足够 |
| 存储 | Redis | 低延迟读取，适合 dashboard 轮询 |

### 面试话术

> "核心挑战是在大规模流数据上做实时 top-K 统计。我会用 Count-Min Sketch + Min-Heap 的组合: CMS 提供 O(1) 的近似计数更新，Min-Heap (size K) 维护当前 top-K。为了支持时间窗口查询，我会按分钟分桶，每个桶一个独立的 CMS + Heap。这个方案的空间复杂度是 O(w*d + K) per bucket，非常紧凑。如果面试官要求精确解，我会改用 HashMap + 定期全排序，但需要更多内存。"

---

## 8. Ranking System

### 题目描述

设计一个找工网 (LinkedIn Jobs) 的 ranking system，对 job posting 进行排序。面经提到时间紧凑，20分钟快速讲解。需要讨论 features、freshness vs relevance 的权衡。

### 需求分析

**Functional Requirements**:
- 用户搜索或浏览 jobs 时，返回按相关性排序的 job 列表
- 考虑用户的技能、经验、地理位置、偏好等个性化因素
- 支持多种排序维度的混合（relevance, freshness, salary match, etc.）

**Non-Functional Requirements**:
- **延迟**: 排序 < 100ms（在搜索请求的关键路径上）
- **规模**: 百万级 job postings，亿级用户
- **实时性**: 新发布的 job 应在分钟内可被搜索到

### 架构设计

```
用户搜索 "ML Engineer" -> Search Service -> Retrieval (ES) -> ~500 candidates
                                         -> Ranking Model -> top-50 ranked results
                                         -> Business Rules -> final list -> UI
```

### 核心组件

- **Feature Engineering (特征工程)**: 这是面试的核心讨论点
  - **User Features**: 技能列表、工作经验年限、教育背景、期望薪资范围、地理位置、行业偏好、历史申请记录、历史点击记录
  - **Job Features**: 职位标题、JD 关键词、公司规模/行业、薪资范围、发布时间、申请人数、required skills
  - **Cross Features (交叉特征)**: user_skills 与 required_skills 的重叠度、user_location 与 job_location 的距离、user_experience 与 job_seniority 的匹配度、user 的 connections 在该公司的数量
  - **Context Features**: 搜索时间（工作日 vs 周末）、设备类型、搜索 query

- **Ranking Model**:
  - **架构**: Learning to Rank (LTR) 模型，如 LambdaMART 或 neural LTR
  - **目标**: 预测 P(apply | user, job)，或使用 pairwise/listwise loss
  - **Freshness 处理**: 加入 time_decay 特征，如 `1 / (1 + hours_since_posted / 24)`
  - **Online Learning**: 用户的点击/申请行为实时反馈，定期更新模型

- **Freshness vs Relevance 权衡**: 这是面试常见 follow-up
  - 纯 relevance: 老 posting 如果匹配度高会一直排在前面 -> 用户体验差
  - 纯 freshness: 新 posting 不一定相关 -> 搜索质量差
  - 解决方案: 在模型特征中加入 freshness signal，让模型自己学习权衡；同时设置 hard rule (如 >90 天的 posting 降权)

### 数据流

1. 用户搜索 "ML Engineer in San Francisco"
2. Retrieval: ElasticSearch 检索匹配的 ~500 个 job postings
3. Feature Service: 为每个 (user, job) pair 构建特征向量
4. Ranking Model: 打分排序
5. Business Rules: 过滤已申请的、已过期的；sponsored jobs 按规则插入
6. 返回 top-20 给前端

### 面试话术

> "Job ranking 的核心是 feature engineering 和 Learning to Rank。Features 分三类: user features、job features、和关键的 cross features（如技能重叠度、地理距离）。Freshness vs relevance 的权衡我会通过 time_decay 特征让模型自动学习，同时设置硬规则（如90天以上降权）。模型用 LambdaMART 或 neural LTR，优化 P(apply | user, job)。"

---

## 9. isMalicious API

### 题目描述

设计一个 `isMalicious(request)` API，判断一个请求是否是恶意的。面试官没有刁难，把基本功说清楚就行。

### 需求分析

**Functional Requirements**:
- 接收一个 API request，返回 `{is_malicious: bool, confidence: float, reason: string}`
- 检测类型: 恶意爬虫、DDoS 攻击、账号盗用、垃圾信息发送
- 支持 rule-based 和 ML-based 两种检测模式

**Non-Functional Requirements**:
- **低延迟**: < 10ms（在请求关键路径上，不能阻塞正常请求）
- **高准确率**: 误报率 (false positive) < 0.1%（不能误杀正常用户）
- **实时**: 攻击模式变化时，规则需要能快速更新

### 架构设计

```
Incoming Request -> API Gateway -> isMalicious Service
                                     |-> Rule Engine (快速规则检查)
                                     |-> Rate Limiter (频率检查)
                                     |-> ML Model (复杂模式检测)
                                     |-> Decision Aggregator -> allow / block / challenge

异步: Request Logs -> Feature Pipeline -> ML Model Training -> Model Update
```

### 核心组件

- **Rule Engine (规则引擎)**: 快速检查硬编码规则
  - IP 黑名单 (known malicious IPs)
  - User-Agent 黑名单 (known bot signatures)
  - Request pattern 匹配 (如 SQL injection patterns in URL)
  - 速度快 (< 1ms)，但只能捕捉已知模式

- **Rate Limiter (频率限制器)**: 基于滑动窗口的请求频率检查
  - 维度: per-IP, per-user, per-endpoint
  - 实现: Redis + Lua script (Token Bucket 或 Sliding Window Counter)
  - 阈值: 如 100 req/min per IP, 1000 req/min per user

- **IP Reputation Service**: 维护 IP 信誉分数
  - 数据源: 历史恶意行为记录、第三方 IP 信誉数据库、ASN/地理信息
  - 存储: Redis (IP -> reputation_score)
  - 更新: 异步批量更新

- **ML Model (机器学习模型)**: 检测复杂的恶意模式
  - **Features**: request rate, time_of_day, geo_location, user_age, session_duration, request_pattern_similarity (与已知攻击模式的相似度)
  - **Model**: Gradient Boosted Trees (XGBoost) -- 训练快、推理快、可解释
  - **推理**: 模型需要 < 5ms 内返回结果，可以用 ONNX Runtime 加速
  - **更新**: 每天/每周重训练，通过 A/B test 上线

- **Decision Aggregator (决策聚合)**: 综合 Rule Engine + Rate Limiter + ML 的结果
  - Rule Engine 命中 -> 直接 block (hard block)
  - Rate Limiter 超限 -> 返回 429 + challenge (如 CAPTCHA)
  - ML score > threshold -> block or challenge
  - 如果多个信号弱 positive，综合判断

### 数据流

1. Request 到达 API Gateway
2. 并行调用: Rule Engine, Rate Limiter, ML Model (扇出)
3. Rule Engine: 检查 IP 黑名单、UA 黑名单 (< 1ms)
4. Rate Limiter: 查 Redis 获取该 IP/user 的近期请求数 (< 2ms)
5. ML Model: 构建特征向量，模型推理 (< 5ms)
6. Decision Aggregator: 综合三个结果，返回 allow/block/challenge
7. 异步: 将请求日志写入 Kafka -> 供 ML 训练和人工审核

### 面试话术

> "我会设计一个混合系统: Rule Engine 处理已知威胁（速度快），Rate Limiter 防止暴力攻击，ML Model 检测未知的复杂攻击模式。三个组件并行执行，总延迟控制在 10ms 以内。关键 trade-off 是准确率 vs 延迟: Rule Engine 和 Rate Limiter 延迟低但只能检测简单模式，ML Model 能检测复杂模式但需要更多计算。Decision Aggregator 综合多个信号做最终判断。"

---

## 10. LinkedIn Skills (Data Mining)

### 题目描述

设计 LinkedIn Skills 系统: 从用户信息中挖掘和识别技能（如 "Python", "Machine Learning", "Project Management"）。面经提到这是一个 open-ended 的 data mining 问题，需要讨论如何收集 token、如何 parse resume、如何建 model 去 predict 一个 token 是否是 skill。

### 需求分析

**Functional Requirements**:
- 从用户 profile（标题、工作描述、教育背景）中自动提取技能
- 构建和维护一个 skill taxonomy（技能分类体系）
- 为每个用户生成 skill 列表及 proficiency level
- 支持新技能的自动发现

**Non-Functional Requirements**:
- **准确率**: Precision > 90%（不能把非技能词识别为技能）
- **覆盖率**: Recall > 80%（不遗漏重要技能）
- **规模**: 数亿用户 profile，需要批量处理
- **时效性**: 新兴技能（如 "LLM Fine-tuning"）应在月级内被发现

### 架构设计

```
用户 Profile 数据 -> ETL Pipeline -> Text Preprocessing
                                   -> Skill Extraction Model
                                   -> Skill Normalization (去重/标准化)
                                   -> Skill Taxonomy Update
                                   -> User Skill Store

新技能发现:
Job Postings + Profiles -> Token Frequency Analysis -> New Skill Candidate Detection
                        -> Human Review -> Taxonomy Update
```

### 核心组件

- **Text Preprocessing (文本预处理)**:
  - 从 profile 的多个字段提取文本: headline, summary, experience descriptions, education, certifications
  - Tokenization: 不仅要 unigram，还要 bigram/trigram（如 "machine learning", "project management"）
  - 清洗: 去标点、统一大小写、去 stop words

- **Skill Extraction Model (技能提取模型)**: 这是核心
  - **方案1: NER (Named Entity Recognition)**: 将 skill 当作一种实体类型，使用 sequence labeling 模型（BiLSTM-CRF 或 BERT-based NER）来识别文本中的 skill spans
  - **方案2: Classification**: 对每个 n-gram token，使用 binary classifier 判断是否为 skill
    - Features: token 本身的 embedding、上下文 embedding、在 job postings 中的出现频率、是否出现在已知 skill list 中
  - **方案3: Weak Supervision + Pattern Matching**: 利用已有的 skill endorsement 数据作为 weak labels，结合 pattern matching（如 "proficient in X", "experienced with X"）
  - **推荐**: 混合方案 -- 先用 pattern matching + 已知 skill list 做高 precision 的初步提取，然后用 NER model 扩展 recall

- **Skill Normalization (技能标准化)**:
  - 将同义词映射到标准 skill: "ML" -> "Machine Learning", "JS" -> "JavaScript"
  - 使用 embedding similarity 发现近义 skill
  - 维护 skill alias table

- **Skill Taxonomy (技能分类体系)**:
  - 层级结构: Category -> Subcategory -> Skill
  - 例: "Engineering" -> "Software Development" -> "Python"
  - 新技能发现: 监控 job posting 和 profile 中的新兴 n-gram，频率超过阈值且不在已有 taxonomy 中的，标记为候选新技能，人工审核后加入

- **Proficiency Estimation (熟练度估算)**:
  - 信号: 工作年限中使用该技能的时间、endorsement 数量、相关认证、skill quiz 成绩
  - 输出: beginner / intermediate / advanced / expert

### 数据流

1. 用户更新 profile，添加新的工作经历描述
2. 变更事件触发 Skill Extraction Pipeline
3. 从描述文本中提取候选 skill tokens (n-grams)
4. NER model 对每个候选打分，过滤低置信度的
5. 通过 Skill Normalization 映射到标准 skill name
6. 更新 User Skill Store
7. 如果发现不在 taxonomy 中的高频 token，标记为候选新技能

### 面试话术

> "LinkedIn Skills 是一个 data mining 问题，我会分三个阶段设计。第一阶段是 token 收集: 从用户 profile 的多个文本字段中提取 n-grams。第二阶段是 skill extraction: 使用混合方案 -- pattern matching + 已知 skill list 做高 precision 提取，NER model 做高 recall 扩展。第三阶段是 taxonomy maintenance: 监控新兴技能的出现频率，自动发现候选新技能。关键的数据飞轮是: endorsement 数据作为 weak labels 持续改进 extraction model。"

---

## 11. Inverted Document Search

### 题目描述

设计一个 inverted document search 系统。给定多个关键词，返回包含所有关键词的文档。面经中给出了具体例子:
```
orange: [1, 13, 20, 25, 74, 99]
juice: [13, 14, 15, 25, 100, 99, 111123]
搜索 "orange juice" -> 返回 [13, 25, 99]
```
Follow-up: 设计分布式版本。

### 需求分析

**Functional Requirements**:
- 支持多关键词搜索，返回包含所有关键词的文档 ID 列表
- 结果按相关性排序
- 支持新文档的索引更新

**Non-Functional Requirements**:
- **查询延迟**: < 100ms
- **索引规模**: 数十亿文档
- **更新延迟**: 新文档在分钟内可搜索
- **高可用**: 查询服务高可用

### 架构设计

```
单机版:
Document Corpus -> Indexer -> Inverted Index (HashMap<term, sorted_doc_list>)
Query "orange juice" -> Tokenizer -> [orange, juice]
                     -> Index Lookup -> posting_list(orange), posting_list(juice)
                     -> Intersection -> result doc_ids

分布式版:
Documents -> Partition by doc_id_range -> Shard 1, 2, ... N (each has full inverted index for its docs)
Query -> Scatter to all shards -> each shard returns local results -> Gather & merge
```

### 核心组件

- **Inverted Index (倒排索引)**: 核心数据结构
  - 结构: `HashMap<String, List<Integer>>`，key 是 term，value 是包含该 term 的 document ID 的有序列表 (posting list)
  - Posting list 按 doc_id 升序排列，方便做 intersection
  - 存储优化: 使用 delta encoding + variable-length encoding 压缩 posting list

- **Posting List Intersection (求交集算法)**: 这是面试核心
  - **基本方法: Two-pointer merge**: 两个有序列表同时遍历，O(m+n)
  - **多个列表的 intersection**: 先按 posting list 长度排序（短的在前），两两 intersect
  - **优化1: Skip pointers (跳表)**: 在长的 posting list 上每隔 sqrt(n) 个元素设置一个 skip pointer，可以跳过大段不匹配的区间
  - **优化2: 从最短的 posting list 开始**: 减少 intermediate result 的大小
  ```python
  def intersect(list_a, list_b):
      result = []
      i, j = 0, 0
      while i < len(list_a) and j < len(list_b):
          if list_a[i] == list_b[j]:
              result.append(list_a[i])
              i += 1
              j += 1
          elif list_a[i] < list_b[j]:
              i += 1
          else:
              j += 1
      return result
  ```

- **Indexer (索引构建器)**:
  - 遍历文档，tokenize，对每个 token 更新对应的 posting list
  - 批量构建: 使用 MapReduce -- Map 阶段输出 (term, doc_id)，Reduce 阶段合并为 posting list
  - 增量更新: 新文档的 terms 追加到对应的 posting lists（需要 merge sort）

- **分布式设计 (Follow-up)**:
  - **Document Partitioning**: 按 doc_id range 分片，每个 shard 持有一部分文档的完整倒排索引
  - **Query Execution**: scatter-gather 模式 -- query 广播到所有 shards，每个 shard 返回 local 结果，coordinator 合并
  - **Replication**: 每个 shard 有 2-3 个 replicas，读请求可以 load balance 到 replicas
  - **对比 Term Partitioning**: 按 term 分片（term "apple" 在 shard A，"banana" 在 shard B）-- 优点是单个 term 的查询只需一个 shard；缺点是多 term 查询需要 cross-shard join，复杂度高。通常 document partitioning 更实用。

### 数据流

1. 用户搜索 "orange juice thorn spikes"
2. Tokenizer 分词: ["orange", "juice", "thorn", "spikes"]
3. 按 posting list 长度排序（最短的在前）
4. 从 Index 中获取每个 term 的 posting list
5. 两两 intersect: 先 intersect 最短的两个，结果再与第三个 intersect，以此类推
6. 返回最终的 doc_id 列表
7. (可选) 按 TF-IDF 或 BM25 排序

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| Intersection 算法 | Sorted merge + skip pointers | O(m+n) 基础上用 skip pointers 优化实际性能 |
| 分片策略 | Document partitioning | 比 term partitioning 更均衡，避免 cross-shard join |
| 压缩 | Delta + VarInt encoding | Posting list 压缩率可达 3-5x |
| 更新策略 | 批量 + 增量混合 | 批量构建离线索引，增量更新近实时索引，定期 merge |

### 面试话术

> "倒排索引的核心是 posting list 的 intersection。对于多个关键词的搜索，我会先按 posting list 长度排序，从最短的开始两两 intersect，使用 sorted merge 算法（O(m+n)），配合 skip pointers 优化跳过大段不匹配区间。分布式版本我会用 document partitioning -- 每个 shard 持有一部分文档的完整倒排索引，query 通过 scatter-gather 并行查询所有 shards。这比 term partitioning 更均衡，避免了 multi-term 查询的 cross-shard join 问题。"

---

## 附录: LinkedIn SD 面试通用策略

### 时间分配 (30-45分钟)

| 阶段 | 时间 | 内容 |
|------|------|------|
| Clarification | 3-5 min | 确认需求范围、约束条件、核心 use case |
| High-level Design | 10-15 min | 画出主要组件及其交互，数据流 |
| Deep Dive | 10-15 min | 面试官选择 1-2 个组件深入讨论 |
| Follow-up | 5-10 min | 扩展问题（scalability, trade-offs, failure handling）|

### 面试官关注点 (根据面经总结)

1. **需求澄清能力**: 不要上来就画图，先问清楚 scope
2. **Trade-off 分析**: 每个设计决策都要说清楚 pros/cons
3. **实际经验映射**: 结合自己做过的类似系统来讲
4. **DB Schema 设计**: LinkedIn 面试官喜欢问 schema 细节和 column 命名
5. **Follow-up 应对**: 准备好 "如何 scale"、"如何 handle failure"、"如何 query efficiently" 的回答

### 面经教训

- "面试官一直纠结于如何收集 exception" -- 不要跳过数据收集层，面试官关心端到端
- "面试官管我的 component x 一直叫 y" -- 尽早 clarify 术语，diagram 上的命名要清晰
- "时间紧凑，最后快速20min讲了讲" -- ranking system 要能20分钟讲完要点，练习精简版
- "面试官也没经验" -- 有些面试官在摸索，保持主动引导节奏
