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
