# Marketplace & Logistics (L5 Gold-Standard Design)

这一题的外皮是打车 / 外卖 / 双边物流平台——Uber / DoorDash / Lyft 这一类。与"简单的 CRUD + 排序"系统根本不同的是它有三条同时在跑的轴线：地理绑定决定了所有服务都必须带 location 维度做 sharding、实时匹配决定了核心数据路径不能进落盘数据库、动态定价决定了离线训练管道和在线决策必须实时联动。所以本题的考点不是"会不会设计一个 service"，而是"能不能把这三条轴线在同一个架构里各自安家、边界清晰、降级路径互不牵扯"。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)

先读 id=18 的理由是：L5 通过范式以及 Appendix A.1.v2 给出的 Writing Discipline（每个技术选择都要触发 Pick + 3 候选 + why-not + 切换条件 + 常见追问这五元组）是本题所有 deep dive 的评分标尺；id=18 Stage 3 "按 read/write + SLA 切服务" 的样例正是取自打车系统，所以反过来读回本题时可以直接对照范式。如果跳过 id=18，下面每个选型块看起来都像"多写一段字"而不像"闭合一个必考追问"。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把用户想要的功能抄一遍"，而是要把五个必问（规模、读写、延迟、一致性、跨地域）答清楚，因为每一问的答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈一定落在 matching 和 location 上、强一致只出现在派单那一瞬间、跨 region 不是兜底"。

**Functional requirements (功能需求)**：端到端主流程是乘客下单→平台匹配司机→实时追踪→到达后支付；辅流程包括司机上下线、接受 / 拒绝派单、行程导航、收入结算；平台级功能含动态定价 (surge)、地理范围调度、异常单 (取消 / 改派) 处理。这些功能我归成三组——交易、位置、定价——后面服务拆分按这三组读写特征走。

**Non-functional requirements (非功能需求)**：规模上取 **Daily Active Users** (DAU, 日活用户) 10M 乘客 + 1M 司机，单城峰值 600 在线司机；延迟上匹配 p95 < 30s、p99 < 2min，位置更新 p95 < 500ms，支付 < 3s；一致性上"同一司机同时只能被派一单"是整个系统唯一硬一致点、其他 (位置、**Estimated Time of Arrival** (ETA, 预计到达时间)、历史轨迹) 都 eventual；可用性 99.9% 平台级、但单城允许分钟级全量降级——因为地理绑定业务中 San Francisco 挂了 New York 兜底没有业务意义；频率上位置上报 5s 一次、匹配峰值 30K **Queries Per Second** (QPS, 每秒查询数)、位置更新峰值 200K QPS。

**Out-of-scope (排除项)**：拼车多乘客、跨城长途、商家供应链、信用评分、广告系统。排除不是"忽略"，是要主动声明——面试官问拼车细节时我知道是超范围题、可以明确"这是个多目标组合优化题，设计 30 分钟内我不深挖，但可以谈顶层思路"。

**必问五问的本题答**：Q1 规模 DAU=10M+1M；Q2 读写比 读远大于写——Redis GEOSEARCH 是真正的战场；Q3 延迟 秒级——匹配 30s、位置 5s；Q4 一致性 派单强一致、其他 eventual——支付前唯一强一致点集中在 CAS 一瞬；Q5 地域 单 region 内多 **Availability Zone** (AZ, 可用区)，多 region 只作为城市粒度的隔离——不跨城做事务。这五个答案是后面每一节的锚点，§2 的数字要回到 Q1 Q3，§3 的服务切分要回到 Q2 Q4，§5 的可用性要回到 Q5。

这一节的 takeaway 是：所有后续决策都从这五问推出，任何选型都要能反向追溯到"因为需求里说过……"——这是 L5 与 L4 的分水岭。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个架构决策找实在的瓶颈锚点——哪条路径是真有压力、哪条是虚的、数字背后绑着哪个架构拐点。我按 **Daily Active Users** (DAU, 日活用户) → **Queries Per Second** (QPS, 每秒查询数) → Storage → Bandwidth 四条链路走一遍，每一段除了给数字还给出对应的技术选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### 乘客侧请求链 (1.2K QPS → 30K geo-search QPS)

乘客 DAU 10M × 人均 2 次下单/天 → 下单 230 QPS 平均、5× 峰值 ≈ **1.2K QPS**。但真正压侧的不是下单本身，而是匹配阶段——每单向外扇出 25 个候选司机做半径搜索，峰值 geo-search 约 **30K QPS** 且业务要求亚秒返回。这个数字决定了 Matching Service 必须独立、挂在一个内存级地理索引上。

地理索引层我选 **Redis GEO**，因为它单机 100K QPS 级读吞吐加亚毫秒 p99、覆盖 30K QPS 还留 3× headroom，GEOADD/GEOSEARCH 原生支持 "N km 内 Top-K 司机" 的语义。

候选一是 **PostGIS**——PostGIS 挂在 PostgreSQL 之上、单节点读只到 5K QPS，要上 30K 必须读写分离加多副本、运维成本翻 3 倍，所以不用；只有需要多边形交并或事务性原子化时 PostGIS 才更合适。候选二是 **Google S2**——S2 是分层细胞几何库、适合跨城全球化路由，但只提供库不带服务、自己得补缓存+服务层，前期开发量大于收益，淘汰。候选三是 **Uber H3**——H3 六边形网格离散化误差更小，但同样只是算法库没有成品服务；H3 更合适的位置是 "索引算法选型" 而不是 "数据库选型"，所以不用。切换触发：当单机 Redis 内存占用 >50% 或出现跨城路由时，迁到按 `city_id` 分片的 S2 + 自建服务层，H3 替换 GEO 的 z-order 曲线做网格算法。

> **常见追问**:
> 1. "Redis GEO 精度够不够？" —— 内部 Geohash 52-bit 编码、赤道精度约 0.6m，远高于 ride-hailing 需要的 50m 级。
> 2. "Redis 重启 RDB 回放慢？" —— 位置数据 TTL 60s 内就重写一遍，冷启动只影响一分钟；怕就开 AOF everysec。
> 3. "30K QPS 需要 cluster 吗？" —— 单机富余 3×，cluster 反而引入跨 slot 问题；保持单机主从，规模起来再上 cluster。

### 司机侧上报链 (140K → 200K write QPS)

司机 DAU 1M × 每 5 秒一次位置上报 × 平均在线 10h 得到持续 **140K write QPS**、峰值 **200K write QPS**。这个量级直接把关系型写层排除——**MySQL** 单机写上限只到 8-10K QPS、与 200K 相差 20 倍，sharding 到 20 实例是运维灾难，MySQL 第一轮淘汰。

位置热写层我选 **Redis**，因为它单机写吞吐同样在 100K QPS 量级、而 GEOADD "原子覆盖最新位置" 语义正好对上业务需求 (司机只要 last-known-location、不需要历史)。

候选一是 **Cassandra**——Cassandra 的 **Log-Structured Merge-tree** (LSM, 日志结构合并树) 写吞吐也到 100K QPS，但 p99 写延迟 10ms 级、对高频上报过重，每次位置变动多写一行、存储占用 10× 于 Redis 的覆盖语义，所以不用。候选二是 **DynamoDB**——托管省运维但单位成本 5-10× 于自建 Redis、on-demand 写在持续高写下账单不可控，淘汰。候选三是 **ScyllaDB**——写吞吐比 Cassandra 高 2-3×，但仍是落盘数据库，在 "只要最新一份" 的业务下落盘成本是浪费，ScyllaDB 更合适的位置是冷存层而不是热写层。切换触发：当单 Redis CPU >70% 或内存溢出时按 `city_id` key-hash 分片；当业务升级为 "要查任意历史时刻位置" 时在热层旁补一份 ScyllaDB、Redis 继续做 last-known 覆盖。

> **常见追问**:
> 1. "Redis 单点宕机位置全丢？" —— 主从 + Sentinel、位置 TTL 5 分钟，即使切主丢的只是 300 秒窗口。
> 2. "GEOADD 覆盖是不是丢了 5 秒前那次上报？" —— 故意的：业务只要最新，历史轨迹由 Kafka → S3 异步管道处理。
> 3. "为什么不把最新位置挂 WebSocket 进程内？" —— 进程重启就全丢、跨 gateway 节点无法跨进程查询，必须有独立数据层。

### 存储分层 (10GB/day + 200GB/day)

存储侧按冷热分层是本题的决策核心。Trip record 约 500 字节 × 20M trips/day ≈ **10GB/day** 结构化；位置轨迹约 6KB/s × 1M drivers × 10h ≈ **200GB/day** 时序。两条路径访问 pattern 完全不同、不能走同一个数据库。

行程事务层我选 **PostgreSQL**，因为行程状态机 (requested → matched → picking → on_trip → completed) 需要 **Atomicity / Consistency / Isolation / Durability** (ACID, 事务四性)、二级索引查询、**Compare-And-Swap** (CAS, 比较并交换) 原子语义来处理司机抢单并发。候选一是 **MySQL**——也能跑 ACID 但地理扩展 (PostGIS) 弱，后续 "半径内可用司机" 辅助查询挂 trip 侧时 MySQL 不如 PostgreSQL 成熟，所以不用。候选二是 **CockroachDB**——原生跨 region 强一致、是 region 真跨之后的升级路径，但当前单城部署、跨 region 强一致是 over-spec、运维复杂度不值，淘汰。候选三是 **MongoDB**——写吞吐高但多文档事务性能差，对抢单这类严格单行 CAS 场景不合适，MongoDB 更合适的位置是用户画像/订单历史这类弱一致读场景。切换触发：当订单 volume 翻 10× 或跨 region 事务出现时，从 PostgreSQL 迁到 CockroachDB；在此之前 PostgreSQL 完全够用。

> **常见追问**:
> 1. "10GB/day 一年 3.6TB，PostgreSQL 扛不扛？" —— 按 `city_id` 分表、热数据保留 3 个月，冷数据走逻辑复制归档。
> 2. "抢单的 race condition 怎么保证？" —— `UPDATE trips SET driver_id=? WHERE id=? AND driver_id IS NULL` 靠行锁 + CAS 天然排它。
> 3. "为什么不拿 Redis 做抢单层？" —— Redis 没有持久事务 semantics，重启丢的状态让订单状态机不可审计。

位置轨迹冷存我选 **Kafka** → **S3**：Kafka 做 append-only 吞吐缓冲、S3 做对象存储落盘，因为时序数据写密集读稀疏、S3 单字节价 $0.023/GB/月、只有 PostgreSQL 自建盘的 1/20。候选一是 **Cassandra**——适合 "写完 5 分钟要查" 的热窗口，但本题位置数据以离线回放和训练回灌为主、热查询极低，Cassandra 存储成本远高于 S3，淘汰。候选二是 **HDFS**——适合批处理但 NameNode 单点运维重，云原生方向 S3 生态工具链更全 (Athena、Glue、Presto 直读)；HDFS 更合适的位置是私有云，公有云下不用。候选三是 **BigQuery**——按字节扫描计费，离线训练常做全表 scan、账单快速上升，淘汰；真要 ad-hoc 分析时可以叠一层 BigQuery 挂在 S3 上做 federated query。切换触发：当出现 "近 5 分钟窗口要实时查轨迹" 时，在 S3 前补一层 Cassandra 做 **Time-To-Live** (TTL, 存活期) 5 分钟的热表。

> **常见追问**:
> 1. "Kafka 会不会成为瓶颈？" —— 单 partition 20-30MB/s，200GB/day ≈ 2.3MB/s，按 city_id 分 10 partition 完全富余。
> 2. "S3 写成本会不会炸？" —— 靠 Flink/Spark 5 分钟微批聚合后再落、单次 PUT 1-5MB，PUT $0.005/1000 次，月账单 30 美元量级。
> 3. "Exactly-once 怎么保证？" —— Kafka transactional producer + S3 multipart + sink idempotent commit。

### 带宽与连接 (6MB/s 出网)

最后看带宽。WebSocket push (行程状态) ≈ 200 字节 × 30K QPS ≈ **6MB/s** 出网，单一负载均衡器完全够；但分 region 部署后必须处理会话亲和。

推送通道我选 **WebSocket**，因为行程状态要毫秒级下推、HTTP 长轮询延迟不可控，而 WebSocket 单连接复用 TCP、头部开销小、浏览器与原生 App SDK 生态成熟。候选一是 **Server-Sent Events** (SSE)——单向 server → client、简单，但不支持 client 主动回推 (司机端要回发位置)、只能覆盖一半链路，所以不用。候选二是 **HTTP Long-Poll**——每次响应后重建连接，30K 长连接下 TCP + TLS 握手炸 CPU，不合适；HTTP Long-Poll 更合适的位置是连接数 < 1K 的小流量场景。候选三是 **GRPC Streaming**——底层 HTTP/2 多路复用、延迟与 WebSocket 相当，但浏览器端必须过代理、本题要 Web 后台支持，淘汰。切换触发：跨 App/Web/SDK 多端一致时保持 WebSocket；纯 App 场景且强类型 schema 需求时迁到 GRPC Streaming。

> **常见追问**:
> 1. "连接数超过 30K，LB 扛不扛？" —— 单 Nginx/HAProxy 可撑 100K 长连接，分 region 每 region 一台 LB 就够。
> 2. "客户端掉线怎么办？" —— 心跳 30s、三次未响应触发重连，重连后通过 trip_id 拉最新状态 reconcile。
> 3. "WebSocket over TLS 的握手成本？" —— 初次 200-300ms、后续复用长连接无额外握手，总平均可忽略。

多 region 长连接路由我选 **Sticky Session**，因为 WebSocket 长连接状态绑在具体进程上、跨进程查询状态成本高，stickiness 把同一用户路由到固定 gateway 最省事。候选一是 **Redis Session Store**——连接状态写 Redis、任何 gateway 都能读，但 30K 连接 × 每条消息读 Redis 加 1ms p99、而且 Redis 又是热写层被复用、串扰严重，Redis Session Store 更合适的位置是连接数低但跨进程协调多的场景，所以不用。候选二是 **Client-side Routing Token**——客户端记住自己连哪个 gateway、reconnect 带 token，无状态 LB 就能路由；但客户端实现复杂、老版本兼容成本大，淘汰。候选三是 **Consistent-hash LB**——按 user_id 一致性哈希、相同用户始终路由同一后端；但扩缩容时哈希环漂移会断 3-10% 连接，对长连接业务不合适。切换触发：gateway 滚动升级或扩缩容频繁时迁到 Client-side Routing Token；当 gateway 完全无状态 (WebSocket 状态 offload 到 Redis) 时直接用无状态 LB。

> **常见追问**:
> 1. "sticky 之后 gateway 挂了？" —— 客户端触发 reconnect、LB 按健康检查路由到新 gateway，用户感知 < 2 秒。
> 2. "跨 region DNS 路由？" —— GeoDNS 把用户路由到最近 region，region 内部再做 sticky；region 间只传异步事件不传长连接。
> 3. "sticky 是否会单 gateway 过热？" —— LB 初次按 round-robin 均衡，sticky 只维持已建立连接，新连接仍均衡分配。

这一节的 takeaway 是：200K write QPS 把存储路径天然切成 Redis + PostgreSQL + Kafka+S3 三层，30K geo-search QPS 把匹配路径独立成 Redis GEO 服务，6MB/s 推送要 WebSocket + Sticky Session——这四个数字直接把 §3 要做的服务拆分边界画好了。

## 3. High-Level Architecture (15m)

架构这一节有两件事必须当面讲清：一是服务怎么切——不按模块切 (Trip / Driver / User) 而按 read-write pattern + **Service Level Agreement** (SLA, 服务等级协议) 切，二是数据怎么流——端到端的派单流必须能让面试官听一遍就画出来。切分逻辑不是审美偏好，是 §2 给出的瓶颈数字直接推出来的结论：位置写 QPS 是行程写 QPS 的 100 倍，放一个服务里一定互相拖垮。

服务拆分策略我选 **read-write + SLA 切分**，因为位置服务 200K write QPS 与 Payment 2s p99 SLA 不能共用线程池和数据层、共用就是延迟互相牵连；按模块切 (Trip / Driver / Rider) 只是把界面实体抄到后端，完全忽略了这些实体在读写特征上的差别。候选一是按**模块切分**——Driver Service 同时持有位置、状态、审计，读写混合；这样一个热 key (某司机瞬时位置) 会拖慢对同一司机的订单状态更新，候选一淘汰。候选二是按**数据域切分** (Location / Trip / Payment)——比模块切合理，但会把 Matching 这类"跨多个域的编排逻辑"塞成胖 orchestrator，反而违反单一职责；数据域切分更合适的位置是纯 **Online Transaction Processing** (OLTP, 联机事务处理) 系统。候选三是**按客户端切分** (Rider-facing / Driver-facing)——容易重复代码 (两边都要查位置)、双写同步是灾难，不用。切换触发：当 read/write 量比例在两个服务间趋同 (差距 < 3×) 时可以合并；反之一旦出现新的数量级差异就再切一刀。

> **常见追问**:
> 1. "Matching 跨多个数据域怎么算单一职责？" —— Matching 的职责是"把一单派给一个司机"，它消费 Location + Trip 但自身只产出派单事件，不存数据。
> 2. "服务越切越多运维怎么办？" —— K8s 管 replica、按 city_id 分 namespace，运维成本随服务数 log 增长而非线性。
> 3. "单调用链深了会不会加延迟？" —— 派单链 3 跳 p99 加 5-10ms，远小于匹配算法本身 100ms，可忽略。

按这套原则切出下面 5 个服务，每个服务的独立理由都回到 §2 的瓶颈数字或 §1 的 SLA 要求：

| Service | 读写类型 | SLA (p99) | 存储 | 独立原因 |
|---|---|---|---|---|
| Location Service | 高写高读 | 200ms | Redis GEO + Kafka→S3 | 写 QPS 200K、和其他服务差 100× |
| Matching Service | 读密集，写轻 | 500ms | in-memory + Redis | 低延迟派单，强一致只在 CAS 瞬间 |
| Trip Service | 强一致写 | 1s | PostgreSQL | 订单状态机事务性 |
| Payment Service | 强一致写 + 审计 | 2s | PostgreSQL + WAL + 对账 | 绝对一致性 + 外部依赖 |
| Notification Service | 高扇出，可丢 | 500ms | WebSocket + Redis pubsub | 长连接 push，独立伸缩 |

端到端数据流按 8 步编号讲，乘客下单到司机接受是必讲主干，其他分支作为简答：

```
(1) 乘客 App → API Gateway
(2) Gateway → Trip Service:  trip.create(rider_id, pickup, drop)
(3) Trip → Matching Service: match.find(trip_id, pickup_geo)
(4) Matching → Location:     GEOSEARCH BYRADIUS 3km (50 candidates)
(5) Matching CAS:            UPDATE drivers SET status='pending_accept'
(6) Matching → Notification: push to driver (15s TTL)
(7) Driver accepts → Trip:   trip.status='active', Matching 释放其他候选
(8) Location Service relay:  司机位置 → WebSocket → 乘客 App (5s 周期)
```

服务间通讯我选 **异步事件 + 同步 RPC 双协议**，同步走 **gRPC** (派单、CAS 等要求立刻拿结果)、异步走 **Kafka** (位置落库、账务审计、模型训练 sink)。候选一是**纯同步 REST**——请求链长了 p99 累加、一跳挂全链挂，候选一淘汰。候选二是**纯异步 EventBus**——简单的查询类请求 (如拉 trip 状态) 也要发消息等回调，开发效率低且面向用户的 p99 拉不下来；纯异步更合适的位置是全链路后台批处理。候选三是 **GraphQL**——适合聚合多源查询但不解决背压和订阅问题，本题 Notification 的长连接场景它还是要转底层 WebSocket，不用。切换触发：当服务数翻倍且事件驱动场景超过调用场景时，把同步 RPC 都下沉为事件 + 查询分离的 **Command Query Responsibility Segregation** (CQRS, 命令查询责任分离)。

> **常见追问**:
> 1. "gRPC 与 Kafka 并存不会有两套 schema？" —— Proto 文件作为唯一 schema 源，Kafka 消息体直接序列化 proto，单源双协议。
> 2. "Kafka 消息丢了派单会卡？" —— 派单链是同步 gRPC，Kafka 只承载位置落库和审计；即使 Kafka 抖动用户感知为零。
> 3. "gRPC 跨版本兼容怎么办？" —— proto 规范只加字段不删字段、tag 编号不复用，新字段默认值向后兼容。

本节 takeaway：服务切分回到 §2 的数字、调用链以同步 gRPC 为骨架、异步 Kafka 走非关键路径；下面 §4 开始针对 Matching / Surge / ETA 三条核心算法展开 deep dive。

## 4. Deep Dives (25m)

deep dive 这一节是 L5 vs L4 的分水岭，面试官通常会在三个主题里挑 2-3 个问深：dispatch matching、surge pricing、ETA prediction，外加一个跨越三者的地理索引与多目标约束。每个主题我按 id=18 的 5-step 结构走 (essence / options / pick+why / scale-out / edges)，但在 A.1.v2 下每个 pick 必须展开 3 候选 + why-not + 切换触发 + 常见追问——纯列 tradeoff 表在 L5 面试里会被追问到失分。

### 4a. Dispatch Matching Algorithm

派单匹配的本质是给每个新订单在 50 个候选司机里挑一个，目标是全局"单位时间成单数 × 乘客满意度"最大化；难点在于贪心策略延迟低但会把远处司机白白分配给容易接单的订单，而批量优化质量高但增加乘客等待。我选 **2s-batch Hungarian Algorithm** (匈牙利算法) 做匹配，因为 2s 的 pickup 延迟代价远小于 10-20% 的匹配效率提升，而 Hungarian 在 50×50 成本矩阵上 O(n³) 每批 ≈ 30ms、延迟可控。

候选一是**贪心最近司机**——单次匹配 O(K) p99 <100ms、实现简单，但遇到订单簇发时会把远处稀缺司机浪费在最先到的订单上、全局利用率低 15-20%，贪心更合适的位置是司机密度极高的一线城市核心区或 Dispatch 降级路径。候选二是 **Deep Reinforcement Learning** (DRL, 深度强化学习策略)——长期奖励建模理论最优但训练离线成本高、线上可解释性差、监管审计难，DRL 更合适的位置是已跑通 Hungarian 后做 A/B lift 的第二期项目。候选三是 **Integer Linear Programming** (ILP, 整数线性规划)——可把公平性、fairness 作为硬约束求精确最优，但求解时间 O(指数)、30K QPS 下不可行，ILP 更合适的位置是离线场景 (比如 DoorDash 晚高峰预派)。切换触发：当单 city 峰值 > 5× 当前规模或司机供给稀疏到需要跨 cell 协同时，切到 DRL + Hungarian 混合 (DRL 做 cell 间路由、Hungarian 做 cell 内精匹配)；当监管要求完全可解释时回退贪心。

> **常见追问**:
> 1. "Hungarian 2s 批一批，订单等 2s 不是变慢？" —— 2s 是批周期上限，平均等待 1s；匹配效率 +15% 换 1s 等待，乘客体验净正。
> 2. "50×50 矩阵怎么构造？" —— 成本函数 = α·pickup_ETA + β·接单率 + γ·surge，α/β/γ 线上 A/B 调参。
> 3. "Hungarian 怎么防司机被多单抢？" —— 批次结束统一发 CAS，同一司机在同批只能被一单选中，跨批靠数据库 CAS 兜底。

派单瞬间是整个系统唯一强一致点，其他所有状态都 eventual，所以这里必须用 **Compare-And-Swap** (CAS) 而非分布式锁——分布式锁 (ZooKeeper / etcd) 的审计成本、故障切换成本在本业务下完全不值，事务型数据库的行锁天然排它就够了：

```sql
-- 派单瞬间的强一致 CAS (唯一强一致点)
UPDATE drivers
   SET status = 'pending_accept', locked_trip_id = :trip_id, lock_expires = NOW() + INTERVAL '15 seconds'
 WHERE driver_id = :driver_id
   AND status = 'available';
-- 受影响行数 = 1 → 派单成功；= 0 → 并发失败，回退候选列表
```

扩容路径上，单 region 300K QPS 时按 **Uber H3** res=7 **cell** (六边形网格单元) 做 sharding，每个 cell 独立 matching worker、cell 边界用"双边收听"避免切单；边缘场景方面 CAS 失败回退最近次优候选、15s **Time-To-Live** (TTL) 过期自动释放防死锁、司机拒单回退候选队列并记入接单率模型、跨 cell 订单由 gateway cell 裁决所有权。

> **常见追问**:
> 1. "为什么不用 ZooKeeper 做派单锁？" —— ZK 适合配置协调，不适合业务 hot path；行锁 + CAS 已经达到微秒级。
> 2. "CAS 失败率高怎么办？" —— 失败率 > 5% 说明候选池过小，向外扩半径 (3→5km) 重新召回。
> 3. "双派怎么防？" —— CAS 是单行约束，数据库层面保证同一 driver 同一时刻最多一个 active trip。

### 4b. Dynamic Pricing (Surge) Loop

Surge 的本质是通过价格信号把供给往需求热点引流、同时抑制部分低价值需求；闭环周期 60s 是因为更短会抖动、更长跟不上峰谷。难点是可解释性 (监管和 PR 双要求)、抗震荡 (价格突涨引发乘客流失)、公平性 (不同人群价格不能显著歧视)。我选 **log-linear 回归** (对数线性回归) 做核心定价模型，因为它在三条约束上都能同时拿分：可解释 (系数有经济学含义)、可审计 (Switchback 实验能隔离价格弹性因果)、易 A/B (参数线性可 rollback)。

候选一是**规则式 D/S 阈值**——最简单，直接按需求/供给比 > 1.5 就涨价；但阈值切换会产生价格悬崖、乘客流失率陡增，规则式更合适的位置是冷启动前三周的 bootstrap。候选二是 **Deep Reinforcement Learning** (DRL, 深度强化学习)——长期奖励最大化理论最优，但不可解释、监管机构会直接否决、PR 灾难概率高，DRL 更合适的位置是供需已稳定的二线城市做 A/B lift 实验。候选三是 **Gradient-Boosted Decision Tree** (GBDT, 梯度提升树)——能捕非线性特征，但可解释性仍不如对数线性、且模型产出的价格不满足"价格对 D/S 倍数单调"这一业务硬约束，GBDT 更合适的位置是 ETA 预测这类目标明确但非价格的回归任务。切换触发：当需要模型解释"瞬时峰值弹性"且监管放行时转 GBDT；当平台跨多国监管差异大时分国家模型独立 rollout。

> **常见追问**:
> 1. "对数线性怎么保证价格非负？" —— 对 log(price) 建模、exp 还原天然正数，形式稳健。
> 2. "特征里加天气、事件会不会过拟合？" —— L1 正则 + 月滚动重训，过拟合体现在月维度 **Mean Absolute Error** (MAE) 上涨，报警阈值 2× 基线。
> 3. "价格震荡怎么防？" —— 跳变上限 1.5×/分钟 + 7 日滑动均值平滑，防用户感知"忽高忽低"。

保留现有 ML 公式作为对数线性的具体实现：

```python
# 对数线性 surge 模型 - 保留 V1 ML 内容
import numpy as np

def surge_multiplier(
    demand_rate: float, supply_rate: float,
    min_surge: float = 1.0, max_surge: float = 3.0,
) -> float:
    if supply_rate <= 0:
        return max_surge
    ratio = demand_rate / supply_rate
    surge = min_surge + (max_surge - min_surge) * max(0, ratio - 1)
    return min(max_surge, max(min_surge, surge))
```

完整的对数线性形式：$\log(\text{price}) = \beta_0 + \beta_1 \log(D/S) + \beta_2 \cdot \text{features}$，保证价格非负且"变化率与倍数成正比"。

扩容路径按 H3 cell 下沉，每个 cell 本地聚合 D/S → region aggregator 统一定价；热点 cell 打散到 key-suffix 防 Redis 单 key 热点。边缘场景上价格跳变上限 ×1.5/分钟防震荡、紧急事件 (灾害/大型活动) 强制封顶防 PR 风险、新司机/新乘客施加公平约束避免价格歧视。

> **常见追问**:
> 1. "紧急事件封顶逻辑放哪里？" —— 事件流 Kafka → Surge Service 消费并写 flag → 定价链路读 flag 封顶，审计留痕。
> 2. "公平性约束怎么做？" —— 按 user segment (新/老、收入分层) 抽样 **Causal Impact** 估计弹性差异，差异 > 阈值触发人工 review。
> 3. "模型发散 fallback 策略？" —— Surge 模型发散时回退到上一小时稳定值 + 人工封顶，先用后改。

### 4c. ETA Prediction (feature freshness)

**ETA** (Estimated Time of Arrival) 的本质是三段时长之和 $\text{ETA} = \text{routing\_time} + \text{pickup\_time} + \text{preparation\_time}$，**Mean Absolute Error** (MAE, 平均绝对误差) 即业务 **Key Performance Indicator** (KPI)——高估乘客等不住流失、低估到达后发现还没到则差评。特征新鲜度是 L5 答题里最容易丢分的点：静态特征 (道路类型、历史均值) 解决不了晚高峰的即时拥堵。我选 **组件回归模型** (component-wise regression) 做 ETA 预测，因为它把三段独立建模、任何一段失败可独立降级，且每段 feature engineering 可针对性优化。

候选一是**静态历史均值**——查 `(pickup_cell, drop_cell, hour_of_week)` 的历史 p50，响应快、0 成本，但无法捕捉当前流量，误差 5-10 分钟不合格；静态均值更合适的位置是冷启动 + 组件模型全挂时的最后降级。候选二是**端到端序列模型** (Transformer / LSTM on 轨迹+天气+事件)——理论表达力最强，但单次推理 > 100ms 超 SLA、训练数据需求 10× 于组件模型、且任一输入源抖动会让整个输出失效，端到端更合适的位置是离线"精细化 ETA 重估"做事后复盘。候选三是 **Graph Neural Network** (GNN, 图神经网络) on 路网图——能捕路口级别拥堵传播，但图结构更新成本高、推理需 GPU、对 ETA 这类分钟级精度是过度工程，GNN 更合适的位置是物流调度 (多跳路径优化) 而非点对点 ETA。切换触发：当组件回归的 **Root Mean Squared Error** (RMSE) 跨业务场景差异 > 30% 时转端到端；当路网数据实时化后评估 GNN。

> **常见追问**:
> 1. "特征新鲜度 5 秒怎么落地？" —— Hot store Redis 窗口 5s 聚合、特征 Service 热查 < 10ms；warm Kafka 1h、cold offline 7d。
> 2. "任一段失败怎么降级？" —— routing 失败 → 历史路径均值；pickup 失败 → 历史 match-to-pickup 均值；preparation 失败 → 商户类别均值。
> 3. "模型怎么监控漂移？" —— 按日计算 MAE / **Mean Absolute Percentage Error** (MAPE)，跨过 2× 基线发 Slack 报警；每周做 **Population Stability Index** (PSI) 检查特征分布漂移。

扩容路径是特征平台分层——hot 在 Redis 5s 窗口、warm 在 Kafka 1h 窗口、cold 在离线 S3；serving 路径 p99 < 20ms 是硬约束，靠本地 LRU 缓存加 Redis 热查命中率 95% 达成。边缘场景上地图 API 超时回退历史 ETA 均值、跨 cell 订单按首段 cell 的 ETA 模型、司机/商家/天气任一段失败返回保守上界 (上界让乘客"早到"好于"晚到")。

### 4d. Geospatial Index & 多目标约束（ML 内容归档）

地理索引选型和多目标约束是上面三个 deep dive 的公共依赖：matching 需要"半径内 Top-K"、surge 需要"cell 粒度 D/S"、ETA 需要"路段级 id"。我选 **Uber H3** (六边形分层网格索引) 做主索引算法，因为六边形邻居距离均匀 (优于正方形的对角距离失真)、res 参数从 0 到 15 支持不同尺度聚合、有成熟开源实现且 Uber 线上验证过。

候选一是 **Google S2**——基于球面几何、全球一致 cell id、跨地域路由稳健；但 S2 cell 形状是正方形有对角距离失真、邻居计算复杂度高，S2 更合适的位置是跨洲级全球化 (航空、国际物流) 而非打车这种单城尺度。候选二是 **GeoHash**——字符串前缀长度 = 精度、支持按前缀索引快速裁剪；但 GeoHash 在高纬度和边界处有已知精度坍塌问题、邻居 cell 不连续，GeoHash 更合适的位置是粗粒度日志标签和冷存分区键。候选三是 **kd-tree / R-tree**——内存数据结构支持任意多边形查询；但分布式扩展难、插入重构成本高、不适合每秒 200K 位置更新的写密集场景，kd-tree 更合适的位置是离线 batch GIS 分析。切换触发：当平台扩到跨洲多国时叠一层 S2 做顶层路由，H3 继续做 cell 内精细匹配；当索引场景简化到只做日志分区时退回 GeoHash 省依赖。

> **常见追问**:
> 1. "H3 res=7 的 cell 多大？" —— 约 1.2 km²，相当于一个密集商业街区，单城市按这个切 50-500 cells 合适。
> 2. "跨 cell 订单怎么处理？" —— origin cell 持有订单主权、destination cell 只读收听，避免同一订单被多 cell worker 重复处理。
> 3. "H3 邻居查询成本？" —— `h3ToNeighbors` O(1)、ring-2 O(6)、对 50 候选召回毫秒级。

保留 V1 的贪心伪代码作为 "Option A baseline" 备选，面试时如果面试官问"最简单怎么做"这段直接可用：

```python
def greedy_dispatch(order_locs, driver_locs):
    assignments, available = [], set(range(len(driver_locs)))
    for oi in range(len(order_locs)):
        best_d, best_dist = -1, float("inf")
        for di in available:
            dist = float(np.linalg.norm(order_locs[oi] - driver_locs[di]))
            if dist < best_dist:
                best_d, best_dist = di, dist
        if best_d >= 0:
            assignments.append((oi, best_d))
            available.discard(best_d)
    return assignments
```

多目标 **Pareto frontier** (帕累托前沿) 形式化为 $\min_\theta [\text{ETA Error}, -\text{Gross Merchandise Value (GMV)}, \text{Wait Time}]$；实践中次要目标转为硬约束 (如 "ETA 误差 ≤ 2 分钟") 而非软加权，因为加权系数稳定不下来、A/B 实验 confound。Price elasticity $\epsilon = \partial \ln Q / \partial \ln P$ 是定价回归的主输入；Fairness Constraints 避免地区/人群歧视属于监管硬约束；**Vehicle Routing Problem** (VRP, 车辆路径问题) style order batching 是外卖侧 NP-hard、贪心启发式 + ML-based tolerance 预测近似求解。Key Metrics 表列 5 项：转化率、ETA MAE、供给利用率、缺陷率 (取消 + 退货)、**Take Rate** (Take Rate, 收入/GMV)。

本小节 takeaway：H3 是"算法选型"答 deep dive 的正确抽象层；多目标约束要说出"次要目标转硬约束而非加权"这一实战经验才是 L5 信号。

## 5. Reliability & Monitoring (5m)

可靠性和监控这一节要证明系统在故障面前有"防御层级"——不是单点熔断，而是按失效域分成四层 (基础设施 / 服务 / 依赖 / 数据)，每一层有独立的防护手段和降级路径。监控同样不只是技术 SLO，还要有业务 SLO (match-rate、cancel-rate、双派率)——因为打车这种双边市场，业务指标崩了比 p99 抖动严重得多。

四层 failure domain 的设计意图：基础设施层用多 AZ 部署覆盖机房 / AZ 级故障、但跨 region 不做兜底 (SF 故障时 NYC 无法接手 SF 的订单)、因为地理绑定业务跨 region 没有意义——这一点是 L6 级 signal；服务层用熔断限流保护自身和下游、Matching 单实例 OOM 时 K8s 自动替换；依赖层对地图 API、Redis GEO 抖动靠缓存 + 降级；数据层脏司机状态、热点 cell、重派靠 CAS + **idempotency key** + 对账。

| Layer | 失效样例 | 防护手段 |
|---|---|---|
| Infrastructure | 机房断电 / AZ 挂 | 多 AZ 部署；**跨 region 是覆盖不是兜底**——SF 挂了 NYC 无意义 |
| Service | Matching 单实例 OOM | 熔断 / 限流 / 超时 / K8s replica |
| Dependency | 地图 API 超时 / Redis GEO 抖动 | 缓存 + 降级 (下方降级表) |
| Data | 脏司机状态 / 热点 cell / 重派 | CAS + idempotency key + 对账 |

降级表的核心思想是"哪里都能降、就不会全挂"——支付超时转异步 pre-auth + 事后对账而非拒单、Matching 过载返回"附近暂无车"保护下游、位置服务失联从 5s 精确退化到 30s geohash 粗广播、地图 API 不可用回退历史 ETA + 保守上界、Surge 模型发散回退上小时稳定值 + 人工封顶。每一行都是"减功能不减主流程"。

| 场景 | 正常 | 降级 |
|---|---|---|
| Payment Gateway 超时 | 同步扣款 | 异步 pre-auth + 事后对账 |
| Matching 过载 | 最优匹配 | 拒单返回"附近暂无车" (保护下游) |
| Location 服务失联 | Redis GEO 精确 5s | 30s 粗粒度 geohash 广播 |
| 地图 API 不可用 | 实时路径 | 历史 ETA 均值 + 保守上界 |
| Surge 模型发散 | log-linear 预测 | 回退到上一小时稳定值 + 人工封顶 |

**Service Level Objectives** (SLOs, 服务级目标) 双轨：技术 SLO 保证匹配 p95 < 30s、p99 < 2min，位置上报成功率 > 99.95%，平台整体可用率 99.9%；业务 SLO 要求双派率 (duplicate dispatch rate) < 0.01%、match rate > 92%、cancel rate < 8%。其中双派率是唯一一个"一出事就 PR 灾难"的硬业务红线，直接挂在 CAS 成功率指标上实时报警；match rate 和 cancel rate 按小时聚合，走日报和周回顾而不是实时告警。

关键监控仪表盘是 supply/demand ratio 实时 H3 cell 级热力图——平台命根，运营和定价同事每天盯的是这张图而不是技术 p99。异常 cell (供给骤降、需求骤升、surge 异常) 触发分级告警：L1 自动降级、L2 推 on-call、L3 推产品 + PR 团队。

本节 takeaway：多 region 不做兜底是 L6 级论断、双派率直接挂在 compare-and-swap 成功率上报警是 L5 硬指标、供需比热力图是业务人感知平台健康的唯一仪表。

## 6. Summary & Tradeoffs (5m)

做到这一步核心决策有五条：服务按 read/write + SLA 切五块 (Location 200K write QPS 与 Payment 2s SLA 不能共享线程池)、派单唯一强一致点由 CAS 承担 (分布式锁的审计开销在微秒级 hot path 上不划算)、匹配用 2s 批量 Hungarian (平均等待 1s 换 +15% 匹配率)、surge 选 log-linear (显式放弃 DRL 的长期最优换监管过关与 Switchback 实验可行)、ETA 组件回归 (任一段失败走静态均值兜底避免全链挂)。

四组显式 tradeoff：批量 Hungarian +2s 延迟 vs +15% 匹配率——对乘客感知净正因为减少白跑；CAS over ZooKeeper——业务热路径用行锁避开 ZK 的 session lease 复杂度；H3 res=7 (1.2 km²/cell) vs S2——单城 H3 拓扑邻居均匀，跨洲扩展叠 S2 顶层路由；log-linear vs GBDT/DRL——放弃非线性表达力换"价格对 D/S 单调"的业务硬约束与线性系数的经济学可解释。

未覆盖点：拼车多乘客分单 (组合优化 + 司机公平性约束)、跨城长途 (跨 region 事务的一致性与迁移成本)、商家端供应链 (多次转单 / 改派的状态机复杂度)、广告与排序 (LTR + 拍卖机制)。如果再给 30 分钟会深挖拼车的组合优化 + 司机 fairness 的 Switchback 因果评估框架。

明显缺点 + 缓解：单 region cell sharding 的跨 cell 订单需要仲裁、通过 origin cell 持单 / destination cell 只读收听解决；感知 surge 的玩家可能 game 系统 (多账号、多 IP 注册)、用设备指纹 + 支付实名 + 黑名单库三层限制；H3 res=7 固定粒度在供给稀疏区 (郊县) 召回数太少、动态 res 升级到 res=6 (8.5 km²) 或扩大搜索半径到 10 km 解决；Payment 外部依赖链挂断时同步扣款走异步 pre-auth + 分钟级对账。

## Interview Q&A

这一题的外延题族都能靠本骨架 (§3 服务表 + §4 的三 deep dive + §5 降级) 解掉，只是按面试官问法调整重点。下面列出 8 个最常见的变种和对应的主干映射，每题都能在 10 分钟内用本题骨架给出完整答案。

第一类是外卖派单变种。主干不变，§4a 的派单算法要替换为 Vehicle Routing Problem (VRP) 批量路径优化，因为外卖一个司机可以同时送 2-3 单，派单从"单对单"升级成"单对多"，组合爆炸让贪心不够用。

- [ ] "设计一个外卖配送派单系统 (DoorDash / Uber Eats)"——主干 + §4a 替换 VRP。

第二类是动态定价题。主干就是 §4b 的完整闭环，强调 log-linear 的可解释性加 Switchback 实验框架隔离因果；普通 A/B 在价格题上会污染控制组 (价格差异引发用户自组)，所以需要 Switchback 按时间片强制切换。

- [ ] "如何为打车平台构建动态定价？"——§4b 闭环 + Switchback 实验。

第三类是 ETA 预测题。主干对应 §4c 组件回归，重点讲特征平台的分层 (hot / warm / cold) 和任一段失败时的降级路径——静态历史均值做最后兜底。

- [ ] "设计一个带实时更新的 ETA 预测系统"——§4c 组件回归 + 特征平台分层 + 降级树。

第四类是供需失衡题。回到 §4b 的 surge loop 加 §5 的公平性约束和紧急事件封顶逻辑，强调监管与 PR 风险是第一优先级而非最大化收益。

- [ ] "如何处理交易市场中的供需失衡？"——surge loop + 公平性约束 + 紧急封顶。

第五类是房源搜索排序题，是本题的 variant——地理搜索复用 §3 加 §4d 的 H3 选型，但排序要补一层 learning-to-rank，且还要考虑稀疏库存下的 exploration-exploitation 平衡。

- [ ] "设计 Airbnb 房源搜索排序系统"——地理搜索复用主干 + 排序层补 LTR。

第六类是双派防护题。直接讲 §4a 的 CAS 伪 SQL 加行锁唯一强一致点——这是面试官确认你能把"一致性"落实到数据库层的关键信号。

- [ ] "双派 (同一司机同时接两单) 怎么防？"——行锁 + CAS 原子化。

第七类是业务锁 vs 协调服务题。协调服务更适合配置与选主、业务热路径则由数据库行锁承担——分布式锁的运维与审计成本过高、在派单这类微秒级 hot path 上不划算，这是 L5 signal 题。

- [ ] "为什么要避开 ZooKeeper 做派单锁？"——业务锁 vs 协调服务的分层。

第八类是紧急事件 PR 防护题。强制封顶加监管 hook 加事件流实时 feed，把社会责任和品牌风险作为第一优先级而非边界补丁——这体现候选人是否具备 L5 级的业务敏感度。

- [ ] "Surge 在紧急事件期间怎么防 PR 灾难？"——强制封顶 + 监管 hook + 事件流 feed。

本节 takeaway：上面 8 题都能映射回主干 4 条 (§3 服务表 / §4a 匹配 / §4b 定价 / §4c ETA)，差异只在 deep dive 里替换一两块。

## Self-Check (按 id=18 7 类 pass-bar)

自检这一节按 id=18 Appendix A 的 7 类 pass-bar 逐条过，把本题在每一类上的证据列出来——不是打勾，而是说清"凭什么在这一类上达到 L5"。

第一类 Requirements 考的是功能 / 非功能 / 排除项是否齐全。本题 DAU 10M+1M、匹配 p95<30s、派单强一致、单 region 多 AZ，关键数字 + out-of-scope 都主动声明——面试官不用追问就已覆盖。

- [x] **Requirements**：§1 完整覆盖五问 + out-of-scope。

第二类 Capacity 考的是数字是否绑定决策。本题 QPS average+peak、storage/day、bandwidth 都有数字，每个数字都在 §2 里绑定了具体架构决策——200K write QPS 淘汰 MySQL、10GB/day 结构化定 PostgreSQL、200GB/day 时序定 Kafka+S3 分层。

- [x] **Capacity**：§2 四段数字链 + 选型块 + 常见追问。

第三类 Architecture 考的是服务切分逻辑是否能经受追问。本题 5 个服务按 read/write+SLA 切、不按模块，8 步编号数据流、存储选型表每行都有独立理由——是 L5 的基本功盘。

- [x] **Architecture**：§3 5 服务 + 8 步数据流 + 选型表理由齐全。

第四类 Deep Dive 考的是能不能在 2-3 个主题上展示深度。本题 3 个主题 (dispatch / surge / ETA) + 1 个嵌套 ML 归档 (geospatial + 多目标优化)，每个按 5-step (essence / options / pick+why / scale-out / edges) 展开，含 SQL (CAS) + Python (surge, greedy) 代码是 L5 标配。

- [x] **Deep Dive**：§4a-d 四块 + 完整 5-step + 代码嵌入。

第五类 Reliability 考的是能否谈清防御层级。本题 4 层 failure domain + 5 行降级表 + 熔断 / 限流 / CAS / idempotency 齐全；"多 region 是覆盖不是兜底"是 L6 级 signal，讲出来就直接拉升 band。

- [x] **Reliability**：§5 四层防御 + 降级表 + L6 signal。

第六类 Monitoring 考的是能否区分技术 SLO 和业务 SLO。本题同时列了 p95/p99/availability 的技术指标和 match-rate / cancel-rate / 双派率的业务指标，供需比热力仪表盘是平台命根——讲业务语言不只是技术语言是 L5 与 L4 的分界。

- [x] **Monitoring**：§5 双指标 SLO + 供需比仪表盘。

第七类 Communication 考的是主动表达 tradeoff 的能力。本题 tradeoff 主动表达 (批量 vs 贪心、CAS vs ZK、H3 vs S2)、缺点主动提 (跨 cell 订单、surge gaming)、未覆盖点明确 (拼车、跨城、供应链)——体现的是 senior 级沟通能力而非"答题"姿态。

- [x] **Communication**：§6 summary + tradeoff + 未覆盖点主动声明。

7 类全硬 → strong L5。时间紧时优先展示 §3 服务表 + §4a 的 CAS + §5 的 SLO 双指标——这三处是本题 L5 与 L4 的分水岭区域，讲清楚这三处其他内容就算略过也仍能拿 meet bar。
