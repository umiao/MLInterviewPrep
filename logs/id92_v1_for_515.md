# Marketplace & Logistics (L5 Gold-Standard Design)

> 打车 / 外卖 / 双边物流平台 —— Uber / DoorDash / Lyft 风格。地理绑定 + 实时匹配 + 动态定价 是这一类系统的三条主轴。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)

> 本题是"**地理绑定 + 实时匹配 + 动态定价**"系统的代表题。建议先读 id=18（L5 通过范式 + Appendix A 骨架）再回到本题；Stage 3 的"按 read/write + SLA 切服务"的经典样例就取自打车系统。

## 1. Requirements Clarification (5m)

**Functional requirements (功能需求)**：

- 乘客下单 → 平台匹配司机 → 实时追踪 → 到达后支付 端到端流程。
- 司机上下线、接受 / 拒绝派单、行程导航、收入结算。
- 平台动态定价（surge）、地理范围调度、异常单（取消 / 改派）处理。

**Non-functional requirements (非功能需求)**：

- Scale：**DAU = 10M 乘客 + 1M 司机**（单城市级 600 司机在线峰值）。
- Latency：匹配 **p95 < 30s**、p99 < 2min；位置更新 p95 < 500ms；支付 < 3s 可接受。
- Consistency：**司机派单一致性强**（同一司机同时只能被派一单——这是支付前唯一的强一致点）；位置、ETA、历史轨迹 eventual。
- Availability：99.9% 平台级；单城市级允许分钟级全量降级（因为地理绑定业务，SF 挂了 NYC 兜底没意义）。
- Frequency：位置上报 **5s 一次**；匹配峰值 **30K QPS**；位置更新峰值 **200K QPS**。

**Out-of-scope (排除项)**：拼车 / 多乘客、跨城长途、商家供应链、信用评分、广告系统。

**必问五问的本题答**：Q1 DAU=10M+1M；Q2 读远大于写（geo 查询是真正战场）；Q3 秒级（匹配 30s、位置 5s）；Q4 派单强一致 + 其他 eventual；Q5 单 region 内多 AZ（多 region 只作为城市粒度的隔离，不跨城事务）。

## 2. Capacity Estimation (5m)

**链式推导**：

- 乘客 DAU 10M × 人均 2 次下单/天 → 下单 QPS 平均 **230**，峰值 5x ≈ **1.2K QPS**；匹配侧叠加候选 geo 查询（~25 候选司机/单）≈ **30K QPS geo-search peak** → 驱动"Matching 服务独立、使用 in-memory Redis GEO"的决策。
- 司机 DAU 1M × 位置上报 5s 一次 × 10h 在线 / 86400 ≈ **140K 持续写 QPS**，峰值 **200K QPS write** → 驱动"Location 服务独立 + Redis 单机 GEO 足够 + 按城市 shard"的决策（MySQL 单机 10K write QPS 直接淘汰）。
- Storage：trip record ~500 bytes × 20M trips/day ≈ **10GB/day** 结构化；位置 6KB/s/driver × 1M drivers × 10h ≈ **200GB/day** 时序 → 驱动"trip → PostgreSQL、location-history → Cassandra / Kafka→S3 冷存"的分层决策。
- Bandwidth：WebSocket push（行程更新）~200 bytes × 30K QPS ≈ **6MB/s** 出网 → 单 LB 足够，但分 region 后需 sticky session。

**关键句式：每个数字绑定一个架构决策**——纯算数不绑定决策 = L4。

## 3. High-Level Architecture (15m)

**服务拆分（按 read/write + SLA 切，不按模块切）**：

| Service | 读写类型 | SLA (p99) | 存储 | 独立原因 |
|---|---|---|---|---|
| Location Service | 高写高读 | 200ms | Redis GEO + Kafka→S3 | 写 QPS 量级 200K，和其他服务差 100× |
| Matching Service | 读密集，写轻 | 500ms | in-memory + Redis | 低延迟派单，强一致只在 CAS 瞬间 |
| Trip Service | 强一致写 | 1s | PostgreSQL | 订单状态机事务性 |
| Payment Service | 强一致写 + 审计 | 2s | PostgreSQL + WAL + 对账 | 绝对一致性 + 外部依赖 |
| Notification Service | 高扇出，可丢 | 500ms | WebSocket + Redis pubsub | 长连接 push，独立伸缩 |

**编号数据流**（端到端 8 步）：

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

**存储选型**：

| 需求 | 选型 | 理由 |
|---|---|---|
| 司机热位置 | Redis GEO | GEOADD / GEOSEARCH 单机 100K QPS |
| 司机历史轨迹 | Cassandra / Kafka→S3 | 时序批量写 + 低查询 QPS |
| 订单主表 | PostgreSQL | ACID + 索引 + CAS 语义 |
| 支付流水 | PostgreSQL + WAL + 审计表 | 事务 + 合规 |
| 用户 profile | PostgreSQL + Redis cache | 读多写少 |

## 4. Deep Dives (25m)

面试官通常会点 2-3 个：dispatch matching、surge pricing、ETA。每个用 id=18 的 5-step 结构（essence / options / pick+why / scale-out / edges）。

### 4a. Dispatch Matching Algorithm

- **Essence**：在 K=50 候选司机中选一位派给订单 i，使"全局单位时间成单数 × 乘客满意度"最大化；核心矛盾是"贪心 latency 低 vs 批量优化质量高"。
- **Options**：(A) 贪心最近司机（O(K) 单次、p99<100ms）；(B) 批量 **Hungarian Algorithm** (匈牙利算法)（O(n³) 每 2s 一批、提升 10-20%）；(C) 深度强化学习策略（<100ms 推理但离线训练成本高）。
- **Pick + Why**：单城市级峰值 30K QPS 下选 **(B) 2s-batch Hungarian**，因为 2s 的 pickup 延迟增量 << 10-20% 匹配效率提升；配合 CAS 原子锁防双派：

```sql
-- 派单瞬间的强一致 CAS（唯一强一致点）
UPDATE drivers
   SET status = 'pending_accept', locked_trip_id = :trip_id, lock_expires = NOW() + INTERVAL '15 seconds'
 WHERE driver_id = :driver_id
   AND status = 'available';
-- 受影响行数 = 1 → 派单成功；= 0 → 并发失败，回退候选列表
```

- **Scale-out 10×**：单 region 300K QPS 时，按 H3 res=7 cell sharding，每个 cell 独立 matching worker，cell 边界用"双边收听"避免切单。
- **Edges**：CAS 失败回退最近次优候选；15s TTL 过期自动释放（防死锁）；司机拒单 → 回退候选队列 + 记入司机 acceptance-rate（供 reliability 模型用）；跨 H3 cell 的订单由 gateway cell 裁决所有权。

### 4b. Dynamic Pricing (Surge) Loop

- **Essence**：通过价格信号把供给往需求热点引流，同时抑制部分低价值需求，**闭环周期 60s**。
- **Options**：(A) 规则式 D/S 阈值；(B) log-linear 回归（可解释 + 快）；(C) RL 长期奖励最大化（风险高、可解释性差）。
- **Pick + Why**：选 **(B) log-linear**（保留现有 ML 内容）—— 可解释、可受监管审计、易 A/B。
- **Scale-out 10×**：按 H3 cell 下沉计算，local cell 聚合 → region aggregator；热点 cell 打散到 key-suffix 避免 Redis 单 key 热点。
- **Edges**：价格跳变上限 × 1.5/分钟防震荡；紧急事件（灾害/大型活动）强制封顶（PR 风险 + 监管）；新司机/新乘客施加公平约束避免价格歧视。

```python
# 现有 ML 公式保留，归到本 deep dive 的 Pick+Why 项
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

对数线性形式：$\log(\text{price}) = \beta_0 + \beta_1 \log(D/S) + \beta_2 \cdot \text{features}$，保证价格非负且"变化率与倍数成正比"。

### 4c. ETA Prediction (feature freshness)

- **Essence**：ETA 由三段组成 $\text{ETA} = \text{routing\_time} + \text{pickup\_time} + \text{preparation\_time}$；高估流失、低估差评，MAE 即业务 KPI。
- **Options**：(A) 静态历史均值；(B) 组件回归（各段独立模型，保留现有 ML 内容）；(C) 端到端序列模型（NN on 轨迹+天气+事件）。
- **Pick + Why**：选 **(B) 组件回归**，特征 5 分钟滚动窗口 + 长期 embedding；独立可解释、单段失败可降级。
- **Scale-out**：特征平台分层（hot in Redis 5s 窗口、warm in Kafka 1h 窗口、cold in offline），serving 路径 <20ms。
- **Edges**：地图 API 超时 → 降级为历史 ETA 均值；跨 cell 订单按首段 cell 的 ETA 模型；司机/商家/天气任一段失败 → 返回保守上界。

### 4d. Geospatial Index & 多目标约束（ML 内容归档）

- **H3**（Uber 开源六边形网格，res 0-15，邻居距离均匀）、**S2**（Google 球面 cell，全球一致 id）、**GeoHash**（字符串前缀长度 = 精度）。单城市选 H3 res=7（约 1.2km²/cell），全球均衡选 S2。
- 现有 Greedy 伪代码保留作 "Option A baseline"：

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

- **Multi-Objective (Pareto)**：$\min_\theta [\text{ETA Error}, -\text{GMV}, \text{Wait Time}]$；实践中次要目标转为约束（如"ETA 误差 ≤ 2 分钟"为硬约束）。
- **Price elasticity** $\epsilon = \partial \ln Q / \partial \ln P$、**Fairness Constraints** 避免地区/人群歧视、**VRP-style order batching**（外卖 NP-hard，贪心启发式 + ML-based tolerance 预测近似求解）。
- **Key Metrics 表**：转化率、ETA MAE、供给利用率、缺陷率（取消 + 退货）、Take Rate (收入/GMV)。

## 5. Reliability & Monitoring (5m)

**4 层失效域**：

| Layer | 失效样例 | 防护手段 |
|---|---|---|
| Infrastructure | 机房断电 / AZ 挂 | 多 AZ 部署（城市内）；**跨 region 是为了覆盖不是为了兜底**——SF 挂了 NYC 无意义 |
| Service | Matching 单实例 OOM | 熔断 / 限流 / 超时 / K8s replica |
| Dependency | 地图 API 超时 / Redis GEO 抖动 | 缓存 + 降级（下方降级表） |
| Data | 脏司机状态 / 热点 cell / 重派 | CAS + idempotency key + 对账 |

**降级表**：

| 场景 | 正常 | 降级 |
|---|---|---|
| Payment Gateway 超时 | 同步扣款 | 异步 pre-auth + 事后对账 |
| Matching 过载 | 最优匹配 | 拒单返回"附近暂无车"（保护下游） |
| Location 服务失联 | Redis GEO 精确 5s | 30s 粗粒度 geohash 广播 |
| 地图 API 不可用 | 实时路径 | 历史 ETA 均值 + 保守上界 |
| Surge 模型发散 | log-linear 预测 | 回退到上一小时稳定值 + 人工封顶 |

**SLOs（技术 + 业务双指标）**：

- 匹配 p95 < 30s、p99 < 2min（技术）
- 位置上报成功率 > 99.95%（技术）
- **双派率 (duplicate dispatch rate) < 0.01%**（业务一致性）
- **Match rate > 92%**（业务 —— 单可成比例）
- **Cancel rate < 8%**（业务 —— 体验）
- 平台整体可用率 99.9%（技术）

**关键监控**：供需比 (supply/demand ratio) 仪表盘即平台命根，实时 H3 cell 级热力 + 异常 cell 告警是 reliability 之本。

## 6. Summary & Tradeoffs (5m)

**核心决策**：(1) 按 read/write + SLA 切 5 个服务（不按模块切）；(2) 派单唯一强一致点 = CAS，其他 eventual；(3) 2s 批量匈牙利换 10-20% 匹配效率；(4) surge 用 log-linear（可解释 + 合规）；(5) ETA 组件回归（可降级、可 debug）。

**关键 tradeoff**：批量派单 (batched Hungarian) 增 2s 延迟 vs +15% 匹配率 —— 值得；CAS over ZooKeeper —— 业务锁不用协调服务，轻量；H3 res=7 单城市 OK，全球取舍 H3 cell 跨区拼接 vs S2 全局 id。

**未覆盖点**：拼车多乘客分单、跨城长途、商家端供应链（多转单 / 改派拓展）、广告与排序。如果再给 30 分钟会深挖拼车的组合优化 + 司机 fairness 的因果评估（Switchback 实验框架）。

**明显缺点 + 缓解**：单 region 内 cell sharding 的跨 cell 订单需要仲裁 —— 通过"origin cell 持有单、destination cell 只读收听"缓解；感知 surge 的玩家可能 game 系统（多账号等） → 用设备/支付指纹限制。

## Interview Q&A

- [ ] 设计一个外卖配送派单系统（DoorDash/Uber Eats）—— 按上述 6 步，重点在 Section 4 VRP batching。
- [ ] 如何为打车平台构建动态定价？—— Section 4b 完整 loop，强调 log-linear 可解释 + Switchback 实验。
- [ ] 设计一个带实时更新的 ETA 预测系统 —— Section 4c 组件回归 + 特征平台分层。
- [ ] 如何处理交易市场中的供需失衡？—— Section 4b surge loop + 公平性约束。
- [ ] 设计 Airbnb 房源搜索排序系统 —— 地理搜索 + 排序（本题的 variant）。
- [ ] 双派（同一司机同时接两单）怎么防？—— Section 4a CAS 伪 SQL。
- [ ] 为什么不用 ZooKeeper 做派单锁？—— 业务锁 vs 协调服务；L5 信号题。
- [ ] Surge 在紧急事件期间怎么防 PR 灾难？—— 强制封顶 + 监管 hook（社会责任 + 品牌）。

## Self-Check (按 id=18 7 类 pass-bar)

- [x] **Requirements**：功能/非功能/排除项齐全 （DAU 10M+1M、p95<30s、派单强一致、单 region 多 AZ）；关键数字 + out-of-scope 主动声明。
- [x] **Capacity**：QPS avg+peak、storage/day、bandwidth 均给出 + **每个数字绑定架构决策** （200K 写 QPS→Redis 非 MySQL；10GB/day→分层存储）。
- [x] **Architecture**：5 服务按 read/write+SLA 切 ；8 步编号数据流 ；存储选型表有理由 。
- [x] **Deep Dive**：3 个（dispatch / surge / ETA）+ 1 个 nested ML 归档 ；每个按 5-step（essence/options/pick+why/scale-out/edges） ；含 SQL (CAS) + Python (surge, greedy) 。
- [x] **Reliability**：4 层 failure domain ；5 行降级表 ；熔断 / 限流 / CAS / idempotency 齐全 ；**"多 region 是覆盖不是兜底"** 是 L6 级 signal。
- [x] **Monitoring**：SLO 技术（p95/p99/avail）+ 业务（match-rate / cancel-rate / dup-dispatch）双指标 ；供需比热力仪表盘为平台命根。
- [x] **Communication**：tradeoff 主动表达（批量 vs 贪心、CAS vs ZK、H3 vs S2）；缺点主动提（跨 cell 订单、surge gaming）；未覆盖点明确（拼车、跨城、供应链）。

7 类全硬 → strong L5。若时间紧，优先展示 Section 3 服务表 + Section 4a CAS + Section 5 SLO 三处，这是 L5 vs L4 的分水岭区域。
