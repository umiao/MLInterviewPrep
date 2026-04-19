# Real-Time Recommendation System (L5 Design)

这一题的外皮是 feed / 首页 / 搜索落地页的实时个性化推荐——Meta、TikTok、Pinterest、YouTube 这一类。与"设计一个商品展示页"根本不同的是它有三个同时在跑的维度：多阶段漏斗决定了召回/粗排/精排/重排每一层都要独立选型并绑延迟预算、会话级新鲜度决定了特征链路必须贯穿离线训练到在线服务两端、多目标学习决定了单指标优化一定踩坑、必须以多目标融合为默认起点。本题考点不是"跑一个 DCN"，而是"把这三条维度装进同一个系统并为每一层给出三候选 + why-not 的工程级选型"。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问五元组) 是本题 deep dive 的评分标尺；id=18 Stage 4 "多阶段漏斗 + 服务按 SLA 切"样例就是从推荐系统抽出来的。多阶段漏斗召回→粗排→精排→重排四段分层、向量检索 **Approximate Nearest Neighbor** (ANN, 近似最近邻) 内积/余弦及 **Hierarchical Navigable Small World** (HNSW, 分层可导航小世界图)/**Inverted File with Product Quantization** (IVF-PQ, 倒排文件+乘积量化) 基础、梯度排序 (**Wide & Deep**、**DeepFM**、**Deep & Cross Network v2** (DCN-v2, 第二代深度交叉网络)、**Multi-Gate Mixture of Experts** (MMoE, 多门混合专家)) 判别门槛、feature store online/offline 双写与 point-in-time correctness、A/B 的 **Controlled experiment Using Pre-Experiment Data** (CUPED, 基于前期数据的对照实验) 与 **Minimum Detectable Effect** (MDE, 最小可检测效应)——这五块在本篇每节都会被引用。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把用户想要的功能抄一遍"，而是要把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一问的答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈一定落在召回与特征查询、强一致只出现在 A/B 分桶与计费归因一瞬、跨 region 不是兜底只是容灾"。

**Functional requirements (功能需求)** 端到端主流程是用户请求 feed → 召回 → 粗排 → 精排 → 重排 → 返回物品列表；辅流程包括曝光/点击/转化/停留事件上报、实时行为回流到特征、新物品上架进索引、用户冷启问卷/兴趣补全、作者侧审核过的物料进料池。平台级功能含多目标融合 (点击 + 停留 + 转化 + 次日留存)、多样性与合规重排、广告与自然结果混排、冷启动硬配额 slot。这些功能归成三组——检索、排序、回流——后面服务拆分按这三组的读写特征与 **Service Level Agreement** (SLA, 服务等级协议) 对齐。

**Non-functional requirements (非功能需求)** 规模上取 **Daily Active Users** (DAU, 日活用户) 100M、峰值请求 **Queries Per Second** (QPS, 每秒查询数) 70K、物品库 500M、人均 2 session × 10 req/day；延迟上端到端 p99 < 200ms (召回 30ms + 粗排 20ms + 精排 100ms + 重排 20ms + 网络序列化 30ms)、特征查询 p99 < 5ms、召回 p99 < 30ms；一致性上"A/B 分桶与计费归因"是整个系统唯一硬一致点、其他 (**Click-Through Rate** (CTR, 点击率) 统计、行为回流、特征写) 都 eventual；可用性 99.9% 月度 43min budget、单城允许分钟级全量降级 (地理绑定业务跨 region 兜底意义有限)；频率上召回扇出 500 候选、精排扇出 300 候选、**Ranking** 推理 QPS 峰值 **350K invocations/s**；新鲜度要求新物品上架 10 分钟可召回、用户会话行为 1 分钟可影响下次请求。

**Out-of-scope (排除项)** 本轮不设计广告系统 (ads ranking 是独立漏斗带拍卖机制)、内容审核 (**Child Sexual Abuse Material** (CSAM)/暴力过滤是前置 ETL)、支付与下单 (电商转化后另有独立 flow)、作者侧 creator growth、跨 App/Web/mobile session 同步 (独立 **Single-Source-of-Truth** (SoT, 真源) 服务)、多模态图像理解 (CLIP-style 预训练是更上层能力)。排除不是"忽略"，是主动声明——面试官问广告细节时我知道这是超范围题、可以明确"这是拍卖+排序的组合题，30 分钟内不深挖，但可以谈顶层思路"。

**必问五问的本题答**：Q1 规模 DAU=100M、物品 500M、峰值 70K QPS；Q2 读写比 读远大于写——每次请求 500+ model invocations，特征查询 > 700K reads/s；Q3 延迟 端到端 p99 < 200ms 是整篇最硬的数字；Q4 一致性 分桶强一致、其他 eventual——CTR 统计允许秒级延迟；Q5 地域 单 region 多 **Availability Zone** (AZ, 可用区)，跨 region 只做 feature store 异步复制做灾备、不跨 region 做推理。这五个答案是后面每一节的锚点，§2 的数字要回到 Q1 Q3，§3 的服务切分要回到 Q2 Q4，§5 的可用性要回到 Q5。

这一节 takeaway：所有后续决策从这五问推出，任何选型都能反向追溯到"因为需求里说过……"——这是 L5 与 L4 的分水岭。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个架构决策找实在的瓶颈锚点——哪条路径是真有压力、哪条是虚的、数字背后绑着哪个架构拐点。我按 **Daily Active Users** (DAU, 日活用户) → **Queries Per Second** (QPS, 每秒查询数) → Storage → Bandwidth 四条链路走一遍，每一段除了给数字还给出对应的技术选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### 请求链与召回扇出 (23K → 70K request QPS, 350K ranker invocations/s)

DAU 100M × 人均 2 session × 10 request/session ≈ **23K avg QPS / 70K peak QPS**。但真正压侧的不是请求本身，而是召回扇出——每请求触发 500+ candidate 的多阶段推理：two-tower 用户塔实时编码 1 次、ANN 检索 1 次 (返回 1000)、粗排推理 1000 次、精排推理 300 次，所以 **Ranking invocations 峰值 ≈ 350K/s**。这个数字决定了精排必须有独立 GPU 推理集群而不是 CPU 共跑。

精排在线推理层我选 **TensorFlow Serving + GPU batching**，因为它支持动态 batch size (攒 50-200ms 凑满再推)、GPU 在 batch=32 以上吞吐随批大小近线性、TF-Serving 原生支持多模型版本热加载与 A/B 分流，覆盖 350K invocations 只需 400 张 A100 还留 30% headroom。候选一是 **NVIDIA Triton Inference Server**——多后端 (TF/PyTorch/ONNX) 统一部署、dynamic batcher 更成熟，但运维工具链偏 NVIDIA 生态、与团队现有 Kubeflow 整合成本高；Triton 更合适的位置是多模型框架混部场景，纯 TF 栈不用。候选二是 **TorchServe**——PyTorch 原生友好、但 GPU batching 文档与稳定性不如 TF-Serving、吞吐上限在同等硬件下低 20-30%，淘汰。候选三是 **Ray Serve**——Python 直写服务、Actor 模型灵活，但每次推理走 Ray 层多一跳延迟、p99 比 TF-Serving 高 5-10ms，Ray Serve 更合适的位置是需要与 RL 训练 workloads 共享集群的研发环境。切换触发：当平台同时服务 3+ 框架 (TF/PyTorch/ONNX) 模型时迁 Triton；当推理场景嵌进 RL 训练管道时迁 Ray Serve。

> **常见追问**:
> 1. "GPU 批处理延迟会不会把 p99 打爆？" —— batch window 20ms 是上限、A100 推理本身 < 50ms，p99 合计 < 100ms 仍在精排预算内。
> 2. "400 卡 A100 成本扛不扛？" —— 按 on-demand $3/hr 算年成本 ≈ $10M，对 100M DAU 的业务 CPC 模型收入完全可回本。
> 3. "模型热加载会不会掉请求？" —— TF-Serving 双 buffer 加载、流量灰度 0 → 100% 过渡，0 掉请求。

### Embedding 与物品库 (256 GB → ANN sharded 32 份)

物品侧 500M items × 128d × float32 = **256 GB** embedding、单机内存不够 (A100 机型一般 256-512GB，加上索引结构开销实际放不下)；用户侧 100M users × 128d × 4B = **51 GB**、可单机 Redis。这个 256GB 直接把 ANN 选型压到"必须分片"。

ANN 索引我选 **HNSW sharded 32 份**，因为它图结构构建后检索 QPS 最高、支持在线 insert (新物品 10 分钟内可入索引)、召回 recall@100 ≈ 0.95 在 ride-level 数据集上稳定；单 shard 8GB 可在单 64GB 机器上驻留留出 2× 工作内存。候选一是 **IVF-PQ (FAISS 实现)**——倒排 + 乘积量化、内存占用是 HNSW 的 1/4、适合 B 级物品库，但量化带精度损失 (recall@100 ≈ 0.85)、且静态索引 rebuild 成本高不利于新物品实时入库，IVF-PQ 更合适的位置是十亿级 + 离线召回 (如 Pinterest 图像 feed)。候选二是 **ScaNN (Google)**——各向异性量化 + 分区搜索、在高召回区间精度最好、Google 线上验证过，但开源版本对 Python-only 集群友好度差、与 Kubernetes 部署工具链整合成本高，ScaNN 更合适的位置是 GCP 原生 Vertex AI 栈。候选三是 **Faiss Flat**——暴力内积检索、精度 100%，但 500M 规模下单查询 10+ms 撞召回 p99 30ms 预算，Flat 更合适的位置是 < 10M 的离线小库精度基线。切换触发：当物品库升到 B 级时迁 IVF-PQ 换内存；当接入跨场景多模态 embedding (CLIP/CLAP 维度 >512) 时评估 ScaNN。

> **常见追问**:
> 1. "HNSW 增量 insert 会不会让图结构退化？" —— 单批插入 < 1% 的 M 值时图质量几乎不变；日级全量 rebuild 做兜底。
> 2. "32 shards 怎么路由？" —— 按 item_id hash 均匀分片、query 时 fan-out 32 shards 取 top-K 合并，召回扇出放大 32× 但单 shard 检索毫秒级。
> 3. "跨 shard 合并会不会丢精度？" —— 每 shard 返回 top-50 × 32 = 1600 候选、再按精确内积 rerank 到 top-500，全局 recall@500 ≈ 0.97。

### Feature Store 分层 (1TB 在线热 + 5TB/day 离线)

特征存储侧按冷热分层是本题的决策核心。Online hot 100M users × 200 features × 50B ≈ **1 TB**、每请求 100+ 读、p99 < 5ms 是 SLA；offline 每日新增 **5 TB** 训练特征、Spark/Flink 离线拉取对齐 point-in-time。两条路径访问 pattern 完全不同、不能走同一个数据库。

Online 热特征层我选 **Redis Cluster 32 节点 + RocksDB 持久化 tier**，因为 Redis Cluster 单节点 100K QPS 读、32 节点覆盖 700K reads/s 还留 4× headroom、RocksDB 做溢出兜底防重启雪崩。候选一是 **DynamoDB**——托管省运维、单位容量弹性好，但 on-demand 单价 5-10× 自建 Redis、100+ reads/req 的账单不可控，DynamoDB 更合适的位置是 QPS 波动极大的小流量业务。候选二是 **Memcached**——纯 in-memory KV、延迟更低，但不支持持久化、重启全冷启 30 分钟、Cluster 一致性哈希漂移会断连接，Memcached 更合适的位置是完全无状态的 session/page cache。候选三是 **Cassandra**——LSM 写吞吐高、持久化稳健，但 p99 read 10-20ms 撞 5ms SLA、内存命中率低于 Redis，Cassandra 更合适的位置是 warm 层不是 hot 层。切换触发：当单节点 Redis 内存超 50% 时扩至 64 节点；当成本占模型成本比例 > 30% 时评估 **Feast + RocksDB** 的自管开源方案。

> **常见追问**:
> 1. "Redis 重启 1TB 数据怎么办？" —— AOF everysec + RocksDB 同步写、Redis 重启从 RocksDB 预热、冷启 < 5 分钟。
> 2. "Cluster 节点失效怎么处理？" —— Cluster 自动切主、业务感知 < 10 秒；写请求走 write-through RocksDB 保护数据。
> 3. "热点 key 怎么防？" —— 热门 user/item 独立 local LRU (Ristretto) 命中率 60%+ 后再转 Redis，热点 RPS 降 60%。

Offline 批量特征层我选 **S3 + Parquet + Apache Iceberg**，因为 S3 单字节 $0.023/GB/月、Parquet 列存压缩比 5:1、Iceberg 提供 time-travel 让训练可复现任意历史时刻的特征快照 (point-in-time correctness 的工程落地)。候选一是 **HDFS**——适合批处理但 NameNode 单点运维重、云原生方向 S3 生态工具链更全 (Athena、Glue、Presto 直读)，HDFS 更合适的位置是私有云。候选二是 **BigQuery**——按字节扫描计费、离线训练常做全表 scan、账单快速上升、与 Spark 训练 pipeline 集成需 connector，BigQuery 更合适的位置是 ad-hoc 分析而非训练数据底层。候选三是 **Delta Lake (Databricks)**——ACID 事务、Schema evolution 更完整，但需 Databricks 或 Spark 强绑定、跨团队工具链迁移成本高，Delta Lake 更合适的位置是 Databricks 全家桶团队。切换触发：当跨团队需要 ACID 事务写入特征表时迁 Delta Lake；当 ad-hoc 分析成为主场景时叠 BigQuery 联邦查询在 S3 上。

> **常见追问**:
> 1. "5TB/day 写量会不会撑爆 S3 PUT 配额？" —— Flink 5min 微批合并 → 单次 PUT 1-5MB、月账单控制在数百美元量级。
> 2. "训练时对齐 point-in-time 怎么做？" —— Iceberg snapshot + 训练 job 读 `@as_of_timestamp`，物理 join key 是 event_time 与 user_id、item_id。
> 3. "特征回填怎么处理？" —— 回填写新 snapshot、训练指向老 snapshot，永不原地改写保证可复现。

### Event Log 与带宽 (8 TB/day log, 1.4 GB/s 出网)

事件日志 70K QPS × 3 events/req × 500B ≈ **100 MB/s → 8 TB/day**；端到端带宽 70K × 20 items/response × 1KB ≈ **1.4 GB/s 出网**，单 region 多 AZ LB 完全够，静态资源走 **Content Delivery Network** (CDN, 内容分发网络) 不经推荐 path。

事件总线我选 **Kafka 64 partitions**，因为单 partition 吞吐 20-30MB/s、64 partition 总吞吐 > 1 GB/s 有 10× headroom，原生 exactly-once 语义加消费组可以让训练 sink 与实时分析 sink 互不干扰。候选一是 **Apache Pulsar**——多租户隔离好、Segmented storage 更灵活，但运维复杂度高、社区工具链不如 Kafka 成熟、团队学习成本大，Pulsar 更合适的位置是需要强多租户隔离的 SaaS 平台。候选二是 **AWS Kinesis**——托管省运维、与 S3/Athena 原生集成，但单 shard 1MB/s 上限低、rescaling 需手动、成本 3× Kafka 自建，Kinesis 更合适的位置是非 K8s 的 Lambda-only 栈。候选三是 **RabbitMQ**——传统消息队列、事务语义丰富，但吞吐上限 200MB/s 远不够 100MB/s 持续写的 10× headroom 要求，RabbitMQ 更合适的位置是业务事件扇出的 RPC-like 场景。切换触发：当需要多团队强隔离 sink 时迁 Pulsar；当平台全栈转 AWS Lambda 时评估 Kinesis。

> **常见追问**:
> 1. "Kafka 消息丢失怎么办？" —— `acks=all + min.insync.replicas=2`、消费端手动 commit、丢失率 < 1e-6 符合推荐链容忍度。
> 2. "消费滞后怎么监控？" —— Burrow 或 Kafka-lag-exporter，滞后 > 10K 条触发 P2、> 100K 条 P1。
> 3. "训练与实时分析消费会不会冲突？" —— 独立消费组读同一 topic，互不干扰；训练组可回溯 earliest，实时组 latest。

这一节 takeaway：350K invocations 推出 GPU 批推集群、256GB embedding 推出 HNSW sharded 32 份、1TB+5TB 特征推出 Redis hot+S3 cold、8TB/day log 推出 Kafka 64p+S3 sink——这四个数字直接把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节有两件事必须当面讲清：一是服务怎么切——不按模块切 (Candidate / Ranker / Reranker) 而按 read-write pattern + SLA 切，二是数据怎么流——端到端的 feed 请求必须能让面试官听一遍就画出来。切分逻辑不是审美偏好，是 §2 给出的瓶颈数字直接推出来的结论：特征查询 700K reads/s 与精排 GPU 批推 350K invocations/s 不能共用线程池和数据层。

服务拆分策略我选 **read-write + SLA 切分**，因为特征服务 p99 < 5ms 与精排 GPU 推理 p99 < 100ms 不能共用进程：共用就是慢路径拖垮快路径、尾延迟互相污染。候选一是按**模块切分** (Candidate Generation / Ranking / Reranking)——把检索、打分、重排各放一个服务，界面上整齐；但这样 Feature Store 被每个模块各自访问、特征一致性与缓存命中率都要单独维护，模块切分更合适的位置是没有共享依赖的独立管线。候选二是**按物品域切分** (Feed / Search / Notification)——比模块切合理、可独立扩展，但会把 Orchestrator 这类"跨多个域的编排逻辑"塞成胖 orchestrator，反而违反单一职责；物品域切分更合适的位置是业务线边界极清晰且完全不共享模型的多产品平台。候选三是**按客户端切分** (iOS/Android/Web)——容易重复代码 (三端都要查特征)、双写同步是灾难，淘汰。切换触发：当业务线完全独立 (如 feed 和 shop 彻底分裂) 时才切分物品域；当团队增长到 200+ 且模型框架显著分化时才按框架切分。

> **常见追问**:
> 1. "Orchestrator 是不是单点？" —— Orchestrator 无状态、K8s 200 实例分 region 部署，单实例挂 < 1% 流量受影响。
> 2. "服务切多了 RPC 延迟累加？" —— 单 hop gRPC p99 < 2ms、5 hops 累加 10ms 仍在端到端 200ms 预算内。
> 3. "跨服务 schema 演进怎么保证？" —— Protobuf 作为唯一 schema 源、只加不删字段、tag 编号不复用。

按这套原则切出下面 9 个服务，每个服务的独立理由都回到 §2 的瓶颈数字或 §1 的 SLA 要求：

| Service | 读写类型 | p99 SLA | 存储/计算 | 独立原因 |
|---|---|---|---|---|
| API Gateway | 转发+鉴权 | 20 ms | 无状态+JWT cache | 流量入口独立限流/熔断 |
| Rec Orchestrator | 高读编排 | 200 ms E2E | 无状态+local cache | 跨召回并行+超时合并 |
| User Tower | CPU/GPU 推理 | 15 ms | TF-Serving+session cache | embedding 实时编码 |
| ANN Index | 读密集 | 20 ms | HNSW, 32 shards | 256 GB 需 sharded in-memory |
| Feature Store | 低延迟 KV | 5 ms | Redis Cluster+RocksDB | 每请求 100+ 读专门 sharding |
| Ranking | GPU 批推 | 50-100 ms | TF-Serving GPU+batcher | GPU 批处理经济性 |
| Re-Ranker | 读+业务规则 | 20 ms | 无状态+配置 pubsub | 规则频繁变更独立发布 |
| Experiment/Flag | 低 QPS | 30 ms cache | Unleash/LaunchDarkly | 分桶决策、强一致要求低 |
| Event/Log Bus | 高写 async | loss-tolerant | Kafka 64p → S3 | 解耦训练与服务 |

端到端数据流按 10 步编号讲，用户 feed 请求到返回 20 items 是必讲主干，其他分支作为简答：

```
(1)  Client           → API Gateway          (JWT + rate limit)
(2)  Gateway          → Rec Orchestrator      (request_id, user_id, context)
(3)  Orchestrator     → User Tower            (session seq → user_emb)
(4)  Orchestrator     → Feature Store         (user features, ctx features)
(5)  Orchestrator     → ANN Index (fan-out 32) (user_emb → 1000 candidates)
(5a) Orchestrator     → Item-CF store         (co-visit top-200)
(5b) Orchestrator     → Hot-pool store        (cold-start top-100)
(6)  Orchestrator     → Pre-Ranker            (1000 → 300 via small MLP)
(7)  Orchestrator     → Ranking GPU           (300 items batch infer)
(8)  Orchestrator     → Re-Ranker             (MMR + 业务规则 + 广告)
(9)  Orchestrator     → Client                (20 items + impression_id)
(10) Client events    → Kafka → Feature Store (online) & S3 (offline)
```

服务间通讯我选 **异步事件 + 同步 gRPC 双协议**，同步走 **gRPC** (feed 请求链要立刻拿结果)、异步走 **Kafka** (事件回流、模型训练 sink、特征离线对齐)。候选一是**纯同步 REST**——请求链长了 p99 累加、一跳挂全链挂、JSON 序列化开销大，候选一淘汰。候选二是**纯异步 EventBus**——简单的查询类请求 (如拉特征) 也要发消息等回调，开发效率低且用户向 p99 拉不下来；纯异步更合适的位置是全链路后台批处理。候选三是 **GraphQL**——适合聚合多源查询但不解决低延迟排序场景、本题 Feature Store 的 p99 5ms 用 GraphQL 过一层解析器会崩，GraphQL 更合适的位置是前端聚合 API 层。切换触发：当服务数翻倍且事件驱动场景超过调用场景时，把同步 RPC 下沉为事件 + 查询分离的 **Command Query Responsibility Segregation** (CQRS, 命令查询责任分离)。

> **常见追问**:
> 1. "gRPC 与 Kafka 并存不会有两套 schema？" —— Proto 文件作为唯一 schema 源、Kafka 消息体直接序列化 proto、单源双协议。
> 2. "Kafka 消息丢了推荐会卡？" —— feed 链是同步 gRPC、Kafka 只承载事件回流、即使 Kafka 抖动用户感知为零。
> 3. "gRPC 跨版本兼容怎么办？" —— Proto 规范只加字段不删字段、tag 编号不复用、新字段默认值向后兼容。

本节 takeaway：服务切分回到 §2 的数字、调用链以同步 gRPC 为骨架、异步 Kafka 走非关键路径；下面 §4 开始针对 two-tower retrieval、ranking、re-ranking、cold start 四条核心算法展开 deep dive。

## 4. Deep Dives (25m)

deep dive 这一节是 L5 vs L4 的分水岭，面试官通常会在四个主题里挑 2-3 个问深：two-tower retrieval、ranking 深度模型与多任务、re-ranking 多样性、cold start 探索与利用。每个主题我按 id=18 的 5-step 结构走 (essence / options / pick+why / scale-out / edges)，但在 A.1.v2 下每个 pick 必须展开 3 候选 + why-not + 切换触发 + 常见追问——纯列 tradeoff 表在 L5 面试里会被追问到失分。

### 4a. Two-Tower Retrieval + ANN (召回核心)

召回的本质是从 500M 物品中亚毫秒筛出 1000 个候选、优化 **Recall** (召回率) 而非精度，因为精度由后续 ranking 负责；难点在于物品侧表示要足够紧凑 (128d float32) 以支持 HNSW 索引并保持在线更新。我选 **Two-Tower + HNSW** 做主召回，因为用户塔与物品塔独立编码解耦了"用户实时上下文"与"物品静态属性"，内积 + HNSW 组合让亚毫秒 top-1000 检索成为可能、Google/YouTube/TikTok 线上验证多年。

候选一是 **item2item Collaborative Filtering (item-CF)**——用 co-visit 矩阵直接离线算 "看过 A 的人也看过 B"，实现简单、无模型训练依赖，但对新物品零召回、对长尾物品召回质量差、交互特征建模能力弱，item-CF 更合适的位置是 two-tower 的多路召回旁路而非主干。候选二是 **Graph Neural Network (GraphSAGE / PinSage)**——图神经网络在高阶邻居上传播信号、Pinterest PinSage 线上验证 +30% recall，但图构建成本高、embedding 训练 epoch 慢、GPU 资源占用大、物品更新需要图重算，GNN 更合适的位置是 social/follow 密集型场景 (Pinterest、LinkedIn)。候选三是 **Sequential Recommendation (SASRec / BERT4Rec)**——Transformer 在用户行为序列上建模长期兴趣、短序列即可预测，但单次推理 > 20ms 撞召回延迟预算、serving-time 序列长度受限、冷启无序列则退化，SASRec 更合适的位置是短视频/新闻这种序列依赖极强的场景做辅助召回。切换触发：当 UGC 社交关系丰富时叠 GNN 做 edge-enriched 召回；当短视频场景用户序列特征主导时把 SASRec 升为主召回。

> **常见追问**:
> 1. "两塔没有交叉特征怎么办？" —— 多路召回补 item-CF 与 SASRec、用户塔融入长期画像、交叉靠后续精排 DCN-v2 专门建模。
> 2. "用户塔实时编码是否太贵？" —— 用户塔模型 2-3 层 MLP、batch=100 的 CPU 推理 5ms、GPU 可再降 2×。
> 3. "新物品进索引的延迟？" —— 新物品 → Flink 5min 微批 → 物品塔打 embedding → HNSW 增量 insert，端到端 < 10 分钟满足新鲜度要求。

Two-Tower 训练必须用 log-Q 纠正的 **sampled softmax** 否则热门 item 梯度被稀释到无法收敛：

$$\mathcal{L} = -\log \frac{\exp(s(u, i^+) - \log Q(i^+))}{\sum_{i \in B} \exp(s(u, i) - \log Q(i))}$$

其中 $s(u, i) = \langle E_u(u), E_i(i) \rangle$ 是内积打分、$Q(i)$ 是热门度估计 (全库点击次数的归一化)。这个 log-Q correction 是 Google YouTube 2019 论文的核心贡献、没有它热门物品会被过度采样、模型退化成"只推 top-100 爆款"。

负采样策略选 **mixed negative sampling** (batch-neg + 全局采样 + hard neg 三路混合)，因为 random 负样本过易、模型欠挑战；in-batch 自带热门偏置必须 log-Q 纠正；hard negatives (从上一轮召回结果里取高分但非点击) 显著提升 top-K 精度但训练不稳定；mixed 是工业推荐的稳健选择。

> **常见追问**:
> 1. "log-Q 的 Q 怎么估？" —— Kafka 消费全库点击事件、滚动窗口 24h 累积计数、线上 Flink 实时更新。
> 2. "Hard negative 比例多少合适？" —— 80% easy + 20% hard 是通用起点、超过 30% 训练 loss 震荡、低于 10% recall 提升消失。
> 3. "Batch size 对 in-batch neg 的影响？" —— batch >= 1024 时 in-batch neg 足够、< 256 需外加全局负采样。

ANN 扩容路径按 item_id hash 分 32 shards、每 shard 8GB 内存、检索 fan-out 32 × top-50 → 合并精确 rerank top-500；边缘场景上新物品走 incremental HNSW、日级全量 rebuild 兜底、shard 失效时用其他 31 shards 降级召回保持主流程不中断。

### 4b. Ranking: Deep Models + Multi-Task Learning (精排)

精排的本质是在 300 个候选上精确预测用户行为概率 (CTR、CVR、Dwell、Save)、并把多概率按业务权重融合成排序分；难点在多任务间的**负迁移 (negative transfer)**——CTR 和 CVR 的最优表示往往不同、shared-bottom 强制共享会让某些任务掉点。我选 **DCN-v2 + MMoE** 组合做精排，因为 DCN-v2 的显式交叉 (bit-wise + vector-wise) 在 CTR 上稳健、MMoE 的"共享专家 + 任务独立 gate"让每个任务学到适合自己的专家权重分布，这个组合是 2022+ 工业界的默认起点。

候选一是 **Wide & Deep**——Google 2016 的经典、易调优，但 Wide 侧需要手工交叉特征、特征工程成本高，Wide & Deep 更合适的位置是特征专家团队充足但建模复杂度要求低的场景。候选二是 **DeepFM**——FM 自动二阶交叉 + DNN，无需手工交叉；但二阶交叉在高维稀疏场景表达力不够、三阶及以上需要堆 DNN 层、调参成本高于 DCN-v2，DeepFM 更合适的位置是广告出价模型这类高维特征但交叉阶次低的场景。候选三是 **Transformer-based (DIN/BST)**——注意力对用户历史行为序列做动态加权、短视频/新闻类场景显著优于 DCN，但训练成本 3-5× DCN、推理延迟高 2×、在 CTR 绝对提升上只有 +0.5-1% 相对基线，Transformer 排序更合适的位置是序列特征主导的场景。切换触发：当业务出现强序列依赖 (短视频/新闻 feed 连续消费) 时把 DIN/BST 加到用户侧塔；当监管要求模型完全线性可解释时回退 GBDT。

> **常见追问**:
> 1. "DCN-v2 比 DCN-v1 强在哪？" —— v2 的交叉层用 matrix 而非 vector 参数化、表达力 + 调优稳健性都更高、Google 2021 论文验证。
> 2. "MMoE 和 PLE 选哪个？" —— 任务数 ≤ 4 用 MMoE、≥ 5 用 **Progressive Layered Extraction** (PLE, 渐进分层抽取) 效果更稳定。
> 3. "多任务 loss 怎么加权？" —— GradNorm 或 uncertainty weighting 自适应学习、手工调权做起点。

MMoE 任务 $k$ 的输出由 $n$ 个共享专家 + 任务独立 gate 组合：

$$y_k = h_k\left(\sum_{j=1}^{n} g_k(x)_j \cdot E_j(x)\right)$$

其中 $g_k$ 是任务 $k$ 的 gate 网络 (softmax 输出 n 维权重)、$E_j$ 是第 $j$ 个共享专家、$h_k$ 是任务特定输出层；不同任务通过独立 gate 选择不同的专家组合缓解负迁移。

多目标融合打分 (DoorDash Universal Ranker 风格)：

$$\text{score}(u, i) = \sum_{k=1}^{K} w_k \cdot \phi_k(\hat{p}_k(u, i))$$

其中 $\phi_k$ 是对每个目标概率的校准/非线性变换 (如 sigmoid 温度调节或 logit 空间加权)、$w_k$ 由业务方案决定 (CTR 0.5 + CVR 0.3 + Dwell 0.2 常见起点)、可通过 online A/B 扫描网格或 multi-gradient descent 自动学习 (Pareto frontier)。

**Calibration** 是多目标融合前的硬前置——未校准的 sigmoid 输出不能按 `w_k · p_k` 直接加权、因不同任务的预测置信度尺度不同。常用 **Platt scaling** 或 **isotonic regression** 对 holdout 集拟合映射到真实概率。

**CVR 样本选择偏差**是 ranking 第二个必答点：CVR 标签只在点击后有、直接用点击样本训练会让模型只学"点击了的转化"、无法外推到未点击空间。用 **Enhanced Space Sampling Model** (ESMM, 增强样本空间模型) 在全空间训练 pCTR × pCVR|CTR、联合约束解决这个问题。

**Delayed feedback** 是 ranking 第三个必答点：转化事件可能在曝光后 7 天才发生、直接用当天样本训练会把**未转化**的样本当负样本、梯度全错。用 **Delayed Feedback Model** (DFM, 延迟反馈模型, Criteo 2014) 学习转化延迟分布、或用 **importance weighting** 修正。

> **常见追问**:
> 1. "Calibration 需要多大 holdout？" —— 10K 样本起步、1M 以上时 isotonic 稳定、小样本用 Platt 防过拟合。
> 2. "多任务权重怎么 A/B？" —— 每次 A/B 固定 K-1 个权重、扫一个、排除相互干扰；或用 multi-armed bandit 在线搜索。
> 3. "ESMM 的 pCTR × pCVR 会不会 double-count？" —— 联合损失 $L_{CTR} + L_{CTCVR}$ 独立优化、数学上是链式分解不是 double-count。

扩容路径是 GPU 批推集群 400 张 A100 + TF-Serving dynamic batcher (20ms window)；边缘场景上单模型崩溃回退粗排 MLP 打分、批推延迟超 200ms 触发熔断走粗排兜底、特征缺失走默认值 (训练时学过的 imputation token)、线上训练 NaN 触发自动回滚到上一稳定版本。

### 4c. Re-Ranking: 多样性 / 业务规则 / 合规

重排的本质是在精排排序结果上应用整页上下文约束——多样性、业务规则、合规、新鲜度——纯按精排分排列一定会出现"10 条同店商品连续"这种用户体验灾难。我选 **MMR (λ=0.7) + 规则层 + 广告混排** 做主重排，因为 MMR 贪心形式 O(N·K) 可控延迟、λ 参数稳定可调、与业务规则层解耦利于独立发布。

候选一是 **Determinantal Point Process** (DPP, 行列式点过程)——用行列式量化子集多样性、理论最优、不易陷入局部贪心；但矩阵求逆 O(N³) 复杂度高、实现调优成本大、推理延迟 50-100ms 撞重排 20ms 预算，DPP 更合适的位置是离线 reranking 或 N ≤ 100 的小 list。候选二是 **Personalized Re-ranking Model** (PRM, 个性化重排模型)——Transformer encoder 对整页候选做 self-attention 再打分、端到端可学，但需独立训练 pipeline、训练数据需全页曝光日志、工程复杂度高，PRM 更合适的位置是头部公司有专职 reranker 团队时。候选三是 **Deep Listwise Context Model** (DLCM, 深度列表语境模型)——LSTM 对候选序列编码再打分、比 MMR 精度高，但序列顺序敏感、训练-serving 一致性难维护，DLCM 更合适的位置是搜索场景 query 依赖强时。切换触发：当业务特别强调多样性指标时迁 DPP；当团队能承担独立 reranker pipeline 时迁 PRM。

> **常见追问**:
> 1. "MMR 的 λ 怎么调？" —— λ=0.7 起步、A/B 测试多样性熵与 CTR 的 Pareto 前沿、典型最优 0.6-0.8。
> 2. "广告混排位置怎么定？" —— 按 **Generalized Second-Price** (GSP, 广义二价) 拍卖独立排序、插入位置 1/5/10 固定、自然结果与广告分开计 p-value。
> 3. "合规过滤做哪一层？" —— 黑白名单在召回前置 filter、成人内容按 user age gate、品牌互斥在精排后 re-rerank。

MMR 贪心更新规则 ($\lambda \in [0, 1]$ 控制多样性权重)：

$$\text{MMR}(i) = \lambda \cdot \text{rel}(u, i) - (1 - \lambda) \cdot \max_{j \in S} \text{sim}(i, j)$$

其中 $\text{rel}(u, i)$ 是精排分、$\text{sim}(i, j)$ 是物品间相似度 (可用 item embedding 余弦)、$S$ 是当前已选子集；贪心每步选 MMR 分最高的物品加入结果集。

规则层按优先级堆叠：黑白名单 (合规硬约束) > 品牌互斥 (奢侈品不紧邻折扣) > 店家多样性 (同店 ≤ 2) > 类别配比 (各类至少 1) > 新鲜度 boost (new item `score + α · exp(-age)`) > 广告混排 (每 5 位插 1 ad)。每条规则独立 feature flag、可单独 rollout 与回滚。

> **常见追问**:
> 1. "规则冲突怎么办？" —— 合规规则不可违反、业务规则按优先级；冲突时按优先级保高优先级规则。
> 2. "新鲜度 boost α 过大会不会打爆 CTR？" —— α=0.1 起步、A/B 看 CTR 与新物品曝光份额双指标、典型 α ∈ [0.05, 0.3]。
> 3. "广告混排影响主指标怎么办？" —— 广告位独立 holdout、自然结果与广告分开归因、避免 ad-cannibalization。

扩容路径是无状态 K8s + 配置 pubsub (规则更新 1 秒内全集群生效)；边缘场景上规则库不可用时退化为精排直排、广告系统挂时不插入广告但保留位置 (防用户感知页面结构变化)、合规黑名单每日全量 + 增量 diff 双更新。

### 4d. Cold Start & Exploration (冷启动与探索)

冷启动的本质是 CTR 预估在零交互物品上退化成先验均值、这类物品永远排不上去、形成"马太效应"；难点在业务硬约束 (新作者/新商家必须被曝光) 与模型排序逻辑的冲突。我选 **硬配额 slot (k=2/page) + content pretrain + online 快更** 三管齐下，因为单用某一种都有漏洞：硬配额保底限流、content pretrain 让零交互物品有初始 embedding、online 快更让冷→热过渡自然。

候选一是 **Upper Confidence Bound** (UCB, 上置信界)——在 ranking score 加 `c · sqrt(log(T) / n_i)` bonus 强制探索，理论最优 regret bound、实现简单；但 UCB 只解决"单物品曝光次数"维度、对"类别冷启"和"user 冷启"无能为力，UCB 更合适的位置是物品库规模小且用户 cold 占比低的场景。候选二是 **Thompson Sampling (Beta 分布采样)**——从后验 $Beta(\alpha_i, \beta_i)$ 采样 CTR 再排序、概率性探索更自然、工程实现友好；但每物品需维护 $(\alpha, \beta)$ 状态、500M 物品需独立 Redis 表、内存成本高，Thompson Sampling 更合适的位置是物品库 < 10M 且需强探索的场景。候选三是 **Meta-learning (MAML)**——对稀疏历史 user 做 few-shot 适配、理论优雅；但训练复杂度高、需要 task-level 支持集构造、工业落地成本大，MAML 更合适的位置是研究向项目或 few-shot 强需求场景 (医疗、教育个性化)。切换触发：当物品规模缩到 < 10M 时迁 Thompson；当用户 cold 占比 > 30% 时加 meta-learning 专攻稀疏历史用户。

> **常见追问**:
> 1. "硬配额 k=2/page 会不会伤 CTR？" —— 首周 CTR 降 0.5-1%，但第 3 周因新物品加入收敛后净正 +0.3% 且新物品曝光份额 +5%。
> 2. "Content pretrain 怎么打 embedding？" —— 文本过 **Sentence-BERT** + 图像过 **ResNet-50 / CLIP**、拼接后过 MLP 映射到召回空间。
> 3. "冷物品的 online learning 怎么防过拟合？" —— 独立高学习率 + 小 batch + EMA 对齐线上模型、探索衰减 n_i > 100 时回归主模型。

扩容路径按用户冷/热分桶并行训练两套 user tower (cold tower 依赖 demographics + lookalike、hot tower 依赖行为序列)；边缘场景上冷用户 session 内行为少于 5 条时强制落到 cold tower、新开城市首日全量热门兜底 + 24h 后启用探索策略、新物品 1-3 天走硬配额、3-30 天走探索 bonus、30 天+ 按正常排序。

探索与利用的显式公式 (UCB 分支)：

$$\text{score}'(u, i) = \text{score}(u, i) + c \cdot \sqrt{\frac{\log T}{n_i + 1}}$$

其中 $T$ 是全局累计请求数、$n_i$ 是物品 $i$ 累计曝光数、$c$ 控制探索强度 (典型 0.5-2.0 视业务容忍度)。

> **常见追问**:
> 1. "c 参数怎么定？" —— A/B 扫描 c ∈ {0.5, 1.0, 2.0}、看 CTR 与新物品曝光份额的 Pareto；典型 c=1.0 稳健。
> 2. "与 Thompson Sampling 混用？" —— 冷物品用 Thompson (需强探索)、过度阶段用 UCB、热物品回正常 ranking。
> 3. "探索成本怎么向业务解释？" —— "每页 2 个 slot 让新物品进来、长期冷物品池健康度是平台护城河"。

四个 deep dive 共同组成精排漏斗的骨架：two-tower 负责宽召回、DCN-v2+MMoE 负责精排多目标、MMR 负责重排多样性、硬配额+content pretrain 负责冷启防埋没，四段一起回到 §2 的延迟预算数字上形成闭环。

## 5. Reliability & Monitoring (5m)

可靠性和监控这一节要证明系统在故障面前有"防御层级"——不是单点熔断、而是按失效域分成四层 (基础设施 / 服务 / 依赖 / 数据)、每一层有独立的防护手段和降级路径。监控同样不只是技术 SLO、还要有业务 SLO (CTR、多样性、负反馈、新物品曝光)——推荐系统这种在线学习系统、业务指标崩了比 p99 抖动严重得多：一个模型 bug 几小时可能让 CTR 掉 5%、远超技术告警敏感度。

四层 failure domain 的设计意图：基础设施层用多 AZ 部署覆盖机房/AZ 级故障、跨 region 只做 feature store 异步复制灾备 (推理跨 region 延迟撞 200ms 预算、且模型一致性难维护)——这一点是 L6 级 signal；服务层用熔断限流保护自身和下游、Ranking 单实例 OOM 时 K8s 自动替换；依赖层对 Feature Store、ANN Index 的抖动靠 local cache + 降级；数据层对特征缺失、embedding drift、label delay 靠默认值 + 监控告警 + 回滚。

| Layer | 失效样例 | 防护手段 |
|---|---|---|
| Infrastructure | 机房断电 / AZ 挂 | 多 AZ 部署；跨 region 只做 feature 异步复制不做推理兜底 |
| Service | Ranking OOM | 熔断 / 限流 / 超时 / K8s replica |
| Dependency | Feature Store 抖动 | local LRU cache + 默认值 |
| Data | 特征缺失 / embedding drift | imputation token + PSI 告警 + 模型回滚 |

降级表的核心思想是"哪里都能降、就不会全挂"——精排超时跳过用粗排分、粗排超时用召回分、召回超时用热门兜底、**永远不要返回空结果**。每一步降级都在 log 里打 tag (`degraded_stage=rank|pre_rank|retrieval|hot_pool`)、oncall dashboard 实时统计降级率。

| 场景 | 正常 | 降级 |
|---|---|---|
| 精排超时 (> 100ms) | MMoE 多任务打分 | 粗排小 MLP 打分直出 |
| 粗排超时 (> 20ms) | MLP 1000 → 300 | 召回分直排 top-300 |
| 召回超时 (> 30ms) | Two-tower + HNSW | 热门池 top-500 兜底 |
| Feature Store 超时 | Redis KV 查询 | 默认值 + 缺失率告警 |
| ANN 单 shard 挂 | 32 shard fan-out | 31 shard 降级召回 |
| Ranking 模型 NaN | 当前版本 | 自动回滚到上一稳定版本 |

**Service Level Objectives** (SLOs, 服务级目标) 双轨：技术 SLO 保证端到端可用性 99.9% (月度 43min budget)、召回 p99 < 30ms、精排 p99 < 100ms、端到端 p99 < 200ms、Feature Store 读 p99 < 5ms；业务 SLO 要求 CTR 滚动降幅 < 0.5% (触发实验回滚)、新物品曝光份额 > 3%、embedding drift **Kullback-Leibler divergence** (KL 散度) < 0.1、负反馈率 < 1.5% 同比。

SLO 表 9 条双指标如下 (L5 要求 SLO 同时含技术指标和业务指标、纯技术 dashboard = L4)：

| # | SLO | 阈值 | 违反后果 | 层 |
|---|---|---|---|---|
| 1 | 端到端可用性 | 99.9% (月 43 min budget) | 全站降级到热门+缓存 | 技术 |
| 2 | 召回 p99 | < 30 ms | 熔断到 item-CF 单路 | 技术 |
| 3 | 精排 p99 | < 100 ms | 跳过精排用粗排 | 技术 |
| 4 | 端到端 p99 | < 200 ms | 触发降级链 + oncall 告警 | 技术 |
| 5 | Feature Store 读 p99 | < 5 ms | 默认值 + 缺失率告警 | 技术 |
| 6 | CTR 滚动降幅 | < 0.5% | 自动回滚实验分桶 | 业务 |
| 7 | 新物品曝光份额 | > 3% | 调高冷启 slot 配额 | 业务 |
| 8 | Embedding drift (KL) | < 0.1 | 强制模型回滚 | 质量 |
| 9 | 负反馈率 | < 1.5% 同比 | 升级 oncall + 暂停 rollout | 业务 |

Drift 监测是推荐系统的命门指标——训练-服务偏差比线上 bug 更隐蔽。每小时计算 training 分布 vs serving 分布的 **Population Stability Index** (PSI) 与 KL divergence，阈值 PSI > 0.25 告警、> 0.5 强制回滚。PSI 公式 (分 $B$ 个桶比较基线 $p$ 与当前 $q$)：

$$\text{PSI} = \sum_{b=1}^{B} (q_b - p_b) \cdot \ln \frac{q_b}{p_b}$$

PSI 值越小说明分布越接近、通常 PSI < 0.1 表示分布基本一致、0.1-0.25 表示轻微漂移需注意、> 0.25 需立即告警。告警分级：P0 (SLO 全破)、P1 (业务 2σ)、P2 (drift)、季度级 chaos 演练验证降级链可用。

本节 takeaway：推理跨 region 不做兜底是 L6 级论断、embedding drift PSI 直接绑定 SLO #8 触发模型强制回滚是 L5 硬指标、业务 SLO 与技术 SLO 双轨告警是区分 L4/L5 的关键。

## 6. Summary & Tradeoffs (5m)

做到这一步核心决策有五条：服务按 read/write + SLA 切九块——因为 Feature Store p99 5ms 与 Ranking 100ms GPU 推理不能共享线程池；召回选 two-tower + HNSW + 多路并联——因为 item-CF 补 long-tail、热门兜底保延迟下限，而纯 GraphSAGE 淘汰 (图重算成本太高)；精排选 DCN-v2 + MMoE——因为显式交叉解决 CTR、MMoE 多任务 gate 缓解负迁移，而 Wide&Deep/DeepFM 更合适特征工程充足的团队但本题不用；冷启三管齐下——硬配额+content pretrain+online 快更分别解决限流/初始化/过渡；训练 offline full + online incremental 双轨 (shadow → A/B (CUPED) → 10/25/50/100 渐进 rollout + 长期 holdback 1-2%)。

四组显式 tradeoff：延迟 vs 精度——精排 300 items 而非 500 (+0.8% CTR 换 +80ms p99 不值)；多样性 vs CTR——MMR λ=0.7 (λ<0.5 CTR 直降 3%)；新鲜度 vs 稳定性——online incremental 30min 而非 5min (更短训练噪声大、更长跟不上热点)；探索 vs 利用——硬配额 k=2/page (低于 k=1 曝光不够、高于 k=3 首周 CTR 掉太多)。

未覆盖点：多模态 (CLIP 图文联合建模)、长尾因果公平 (causal uplift ranking)、联邦学习与 **Differential Privacy Stochastic Gradient Descent** (DP-SGD, 差分隐私随机梯度下降)、多场景统一 (multi-domain ranking)、在线强化学习。如果再给 30 分钟会深挖多模态 + 多场景统一。

明显缺点 + 缓解：依赖大量行为日志冷启/隐私受限——content pretrain + meta-learning 补；Two-tower 无交叉特征——多路召回补 SASRec/item-CF、精排 DCN-v2 建交叉；MMoE gate 解释性差——offline 可视化 gate weight、分任务 AUC 看板；在线增量训练有 catastrophic forgetting——EMA 对齐 + online validation 兜底、异常回滚到最近 offline checkpoint。

## Interview Q&A

这一题的外延题族都能靠本骨架 (§3 服务表 + §4 四 deep dive + §5 降级) 解掉、按面试官问法调整重点即可。下面列 6 个最常见变种的主干映射、每题 10 分钟可答完。

第一类是短视频 feed。主干不变、§4a 的 two-tower 要替换为 SASRec + two-tower 双路召回、因为短视频用户行为序列极强、单塔会丢短期兴趣；精排侧加 **Behavior Sequence Transformer** (BST, 行为序列 Transformer) head 建序列。

第二类是新闻 feed。主干不变、§4a 加强**新鲜度 boost** (新闻 time-decay 比一般物品严格 10×)、§4b 加**疲劳度惩罚** (同主题连续 > 3 篇降权)、§4c 的 MMR 把 sim 改为主题 embedding 余弦。

第三类是电商推荐。§4b 多任务包含 CVR (ESMM) 和 GMV 回归 head、§4c 加**库存约束**与**品牌混排** (奢侈品不紧邻折扣)、§4d 冷启 content pretrain 改为图像+标题+类目 hierarchical embedding。

第四类是广告推荐。广告漏斗独立管线 (拍卖+排序双阶段)、只在 §4c"广告混排"触点耦合；**Generalized Second Price** (GSP, 广义二价) 拍卖先算 eCPM = bid × pCTR × pCVR、按 eCPM 排再二价计费、最后与自然结果融合。

第五类是搜索推荐混合。§4a 的 two-tower 扩成 (query_emb + user_emb) × item_emb 内积、§4c 的 MMR sim 改为 query-aware 相似度、精排特征加 query-item 语义匹配 (BM25 + BERT semantic score)。

第六类是冷启动专题。这题只问 §4d 的深挖，扩 30 分钟会加 cross-domain transfer (成熟城市 fine-tune 新城市 user tower)、lookalike modeling (demographics cluster)、MAML meta-learning (对稀疏历史用户 few-shot 适配)。

> **常见追问**:
> 1. "面试官问广告与自然混排如何归因？" —— impression_id 里打 ad_slot flag、点击/转化归因用因果推断 (PSM / IV) 分离。
> 2. "面试官问推荐的 bias amplification (同质化)？" —— 定期分析用户长期 exposure diversity、触发 forced exploration 打破 bubble。
> 3. "面试官问多场景 (feed / search / detail page) 模型复用？" —— 共享 embedding table + 场景独立 ranking head、MMoE 可扩展到场景作为任务维度。

以上六类变种共性：主干 (§3 服务表 + §4 四 deep dive + §5 降级) 不变，只替换算法模块或加约束即可覆盖 80% 推荐外延题。

## Self-Check (面试前必过)

Topic-level pass 要求面试前能独立回答 12 项硬核问题：画端到端 funnel 图并说出每阶段延迟预算、解释 two-tower 的 in-batch neg 为何需要 log-Q correction、区分 HNSW/IVF-PQ/ScaNN 选型依据、说明 MMoE 缓解负迁移的机制与 PLE 的改进、写出多目标融合公式并解释校准必要性、给出至少 3 种冷启动对策、列 5 种延迟-精度权衡技术、画降级链精排→粗排→召回→热门、解释 PSI 阈值 0.1/0.25 的意义、讲清 shadow→A/B(CUPED)→gradual rollout+holdback 流程、识别 A/B 5 项常见陷阱、解释 delayed feedback 与 ESMM 各自适用场景。

7-Category Pass-Bar 按 id=18 L5 打分表逐项过——Requirements 功能/非功能/排除齐全、Capacity 每数字绑定决策 (256GB→ANN sharding、350K→GPU、8TB/day→Kafka+S3)、Architecture 9 服务按 SLA 切 (§3)、Deep Dive 四个深挖含 log-Q/MMoE gate/MMR/PSI/ESMM/DFM 公式、Reliability 4 层 failure domain+降级链、Monitoring SLO 9 条双轨+P0/P1/P2 分级、Communication 3 大 tradeoff 主动提。7 类全硬 → strong L5，最具区分度的展示点是 §3 service-by-SLA 表、§5 SLO 双指标表、§6 四组显式 tradeoff。

## L5 Tradeoff Matrix (7 行决策矩阵)

| # | 决策点 | Pick | 为什么 | 何时换 |
|---|---|---|---|---|
| 1 | 召回策略 | Two-tower + ANN 主 + item-CF 辅 + 热门兜底 | Two-tower 学交互；item-CF 补 long-tail；兜底保延迟下限 | 物品 < 1M 可 brute-force 全量 GBDT；社交图主导切 GraphSAGE |
| 2 | 排序模型 | DCN-v2 (CTR) + MMoE (多任务) | DCN-v2 稳健 + MMoE 共享表征缓解负迁移 | 需 long-range 序列 → BST；极低延迟 → GBDT fallback |
| 3 | 冷启动 | 硬配额 slot (k=2/page) + content pretrain + online 快更 | 三管齐下防长尾埋没 | 业务容忍度高可单走探索式策略；冷启 > 30% 需独立冷启模型 |
| 4 | 探索算法 | ε-greedy (ε=0.05) + UCB 新物品 | 简单稳定 + 主动探索冷物 | 大规模 context → LinUCB；长期 reward → RL-based 重排 |
| 5 | 服务模式 | 同步在线 (E2E < 200ms) | 体验 + 新鲜度会话级 | 可容忍 T+1 预生成则异步降成本 10× |
| 6 | 特征新鲜度 | online 5-min (Redis) + offline day (S3) | 热度感知 + 训练对齐 | 容忍 10min 全 offline；要亚秒 → Flink 实时 |
| 7 | 模型 rollout | Shadow → A/B → 10/25/50/100 + Holdback 1-2% | 每步回滚按钮 + 长期归因 | 低风险微调跳 shadow；高风险加 bandit 自动切换 |

阅读法则：先 Pick+理由、再主动"何时换"——L5 信号就是不等追问就暴露 tradeoff。
