## 2. Capacity Estimation (5m)

**链式推导**：

- 乘客 DAU 10M × 人均 2 次下单/天 → 下单 QPS 平均 **230**，峰值 5x ≈ **1.2K QPS**；匹配侧叠加候选 geo 查询（~25 候选司机/单）≈ **30K QPS geo-search peak** → 驱动"Matching 服务独立、使用 in-memory Redis GEO"的决策。
- 司机 DAU 1M × 位置上报 5s 一次 × 10h 在线 / 86400 ≈ **140K 持续写 QPS**，峰值 **200K QPS write** → 驱动"Location 服务独立 + Redis 单机 GEO 足够 + 按城市 shard"的决策（MySQL 单机 10K write QPS 直接淘汰）。
- Storage：trip record ~500 bytes × 20M trips/day ≈ **10GB/day** 结构化；位置 6KB/s/driver × 1M drivers × 10h ≈ **200GB/day** 时序 → 驱动"trip → PostgreSQL、location-history → Cassandra / Kafka→S3 冷存"的分层决策。
- Bandwidth：WebSocket push（行程更新）~200 bytes × 30K QPS ≈ **6MB/s** 出网 → 单 LB 足够，但分 region 后需 sticky session。

**关键句式：每个数字绑定一个架构决策**——纯算数不绑定决策 = L4。
