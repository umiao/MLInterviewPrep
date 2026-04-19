## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀数学，而是给后面的每一个架构决策找一个 anchor——哪条瓶颈是实的、哪条是假的。我按 **Daily Active Users** (DAU, 日活) → **Queries Per Second** (QPS, 每秒查询) → Storage → Bandwidth 四段链路走一遍，每一步都明确说出"这个数字驱动了哪个架构决策"，而不是停在纯算数上。

乘客侧 10M DAU × 人均 2 次下单/天得到下单 230 QPS 平均、峰值 5× 约 **1.2K QPS**。但真正压侧的不是下单本身，而是匹配阶段——每单往外扇出约 25 个候选司机做地理搜索，峰值 geo-search 约 **30K QPS**。这个数字决定了 Matching Service 必须独立出来并挂在一个内存级地理索引上，我因此选 **Redis GEO**，因为单机 100K QPS 级读能力与亚毫秒延迟能直接覆盖 30K QPS 的头部负载。候选方案是 **PostGIS** 和 **S2**：PostGIS 适合需要持久化和复杂多边形查询的场景，但本题只做 radius 查询且允许近似一致；S2 是跨城全球化的升级路径。当单机 Redis 内存占用过半或出现跨城路由需求时，我切换到 S2 并按 `city_id` 级 sharding。

司机侧 1M DAU × 每 5s 一次位置上报 × 平均 10h 在线得到持续 **140K write QPS**、峰值 **200K write QPS**。这个量级立刻把 MySQL 从候选里排除——因为单机 MySQL 写能力只到 10K QPS 量级、与 200K 差 20 倍。位置热写层我选 Redis，因为它单机写吞吐同样在 100K 量级，而 GEOADD 原子覆盖语义恰好对上"只保留最新位置"的业务需求。候选是 **Cassandra**（**Log-Structured Merge-tree** (LSM, 日志结构合并树) 写吞吐大，但 p99 写延迟 10ms 量级、对高频上报过重）和 **DynamoDB**（托管方便但单位成本 5-10×）。当单 Redis 实例 CPU 饱和或内存溢出时，我按城市维度 key-hash sharding、每城一主若干从。

存储侧按冷热分层是本题的决策核心。Trip record 约 500 字节 × 20M trips/day ≈ **10GB/day** 的结构化数据我选 **PostgreSQL**，因为行程状态机需要 **Atomicity / Consistency / Isolation / Durability** (ACID, 事务四性)、二级索引和 **Compare-And-Swap** (CAS, 比较并交换) 原子语义。候选是 MySQL（PostGIS 扩展薄弱）和 CockroachDB（跨 region 事务强但运维重）；当真的出现跨 region 事务再切 CockroachDB。位置轨迹约 6KB/s × 1M drivers × 10h ≈ **200GB/day** 时序数据不走关系库——我选 **Kafka → S3** 作为冷存，因为时序数据写密集、读稀疏，S3 单字节价是 PostgreSQL 的 1/20。候选 Cassandra 更适合"写后 5 分钟要查"的热窗口场景，但本题只做离线回放和训练数据回灌，所以 S3 更经济。当出现"近窗口要实时查"需求时，我在 S3 前补一层 Cassandra 做 **Time-To-Live** (TTL, 存活期) 5 分钟的热表。

带宽侧相对轻：30K QPS × 200 字节 WebSocket push 行程状态 ≈ **6MB/s** 出网，单负载均衡器够用。但一旦分 region 部署，必须用 sticky session 把同一乘客绑到同一 WebSocket 网关，因为长连接的会话状态绑在建立它的进程里、不会自动迁移。

这一节的 takeaway 是：200K write QPS 把存储路径天然分成 Redis + PostgreSQL + S3 三层，30K geo QPS 把匹配路径独立成 Redis GEO 服务——这两个数字直接把 §3 的服务拆分边界划好了。