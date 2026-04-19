# ML Infrastructure Design (L5 Platform Spine)

这一题的外皮是"给我设计一个 ML 平台，让公司 100-1000 位工程师能快速跑实验、稳定上线、持续监控"，与 id=92/id=198 那种"单个产品系统"不同，本题的重心是**平台即产品**——用户不是终端消费者而是公司内部 ML 工程师，SLO 不是用户延迟而是**迭代速度** (想法到 A/B 的时间)、**上线安全** (回滚与超配不超投) 与**多租户公平** (GPU 配额不互相踩)。本题考察的是"能不能把 Experiment Tracking / Feature Store / Training Orchestrator / Model Registry / Deployment Service / Feature Serving / Monitoring / Lineage 八条链路在 PB/day 流量下摆清楚，并给出每一层的选型拐点"。两个分水岭：一是训练-服务偏差 (Training-Serving Skew) 是否从架构层被闭环消除、二是多租户配额与 GPU 抢占能否同时保证公平性与利用率。答不清楚这两点只能拿 L4。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=92 Marketplace & Logistics](/kg?node=n92)、[id=198 Real-Time Recommendation](/kg?node=n198)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 pick + ≥3 候选 + why-not + 切换条件 + 常见追问五元组) 是本题所有 deep dive 的评分标尺。再读 id=92 的理由是：那篇把"按读写 + SLA + 一致性切服务"的范式走过一遍、本题把这个范式应用到"平台工程"——平台服务切分同样遵守 SLA + 一致性 + 多租户边界。最后读 id=198 的理由是：那篇里的 Feature Store 在线层 (Redis / RocksDB / Memcached 选型) 与本题 Feature Serving 子模块直接连通，复用其数字与选型结论。本题读者应对 **Directed Acyclic Graph** (DAG, 有向无环图)、**Distributed Data Parallel** (DDP, 分布式数据并行)、**Fully Sharded Data Parallel** (FSDP, 全分片数据并行)、**Kullback-Leibler Divergence** (KL Divergence, KL 散度)、**Population Stability Index** (PSI, 群体稳定性指数)、**Click-Through Rate** (CTR, 点击率) 这些概念有基础认识，否则分布式训练选型、模型漂移监控、多租户设计都会卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把产品经理的话抄一遍"，而是把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一个答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套平台的瓶颈落在 GPU 集群调度的 gang-scheduling 与 Feature Store 在线 p99 读延迟、强一致只出现在 Model Registry 的 stage promotion 与 Budget/Quota 扣减、跨 region 只做异步 metadata 复制不做同步训练"。

**Functional requirements (功能需求)** 主流程是 ML 工程师提交实验 → Orchestrator 调度训练作业 → Training 写特征快照 + 指标到 Experiment Tracker → 产出 artifact 推 Model Registry → Deployment Service 按金丝雀策略上线 → Feature Serving + Model Serving 接在线流量 → Monitoring 持续采集漂移与业务指标 → 触发重训或回滚。辅流程包括特征 pipeline 注册 (Feature Store 写端)、Lineage 记录 (数据→模型→部署的全链路血缘)、多租户资源配额、成本归因、合规审计 (谁训了什么模型、用了什么数据、上了哪个 endpoint)。平台级功能含 A/B 分桶平台、Shadow Deployment 流量镜像、Canary Release 灰度、Circuit Breaker 熔断回退。这些功能归成四组——Orchestration、Data/Feature、Serving/Deployment、Observability——后面 deep dive 按这四组的建模选型逐一展开。

**Non-functional requirements (非功能需求)** 规模取公司 100-1000 位 ML 工程师、日均训练作业 **10K jobs/day** (含 pipeline 子任务)、日均推理部署变更 **100K deployments/day** (含灰度步进)、特征日志流 **1 PB/day** (曝光/点击/转化/特征快照)、在线 Feature Serving **100M QPS** 峰值 (聚合所有在线模型)、训练集群常驻 **~10K GPU** + 弹性 30K、推理集群 **~5K GPU + 50K CPU core**；延迟 Feature Serving p99 < 2ms、Model Serving p99 < 50ms (与业务无关的平台基线)、Experiment metadata 写入 < 500ms (不阻塞训练循环)、Model Registry stage promotion < 10s；一致性除 Model Registry stage promotion 与 Quota 扣减强一致 (防超配 / 防并发双写) 外其他 eventual (metrics 允许秒级延迟、日志回流允许分钟级)；可用性 Feature Serving 99.99% (月度 4 分钟)、Orchestrator / Registry 99.9% (月度 40 分钟——工程师可以等但不能全天黑)；新鲜度训练-服务偏差窗口 < 1h (特征写入后最长 1h 必须出现在在线 serving)、模型注册后可 < 15 分钟达到 100% 流量 (Canary 完整跑完)。

**Out-of-scope (排除项)** 深入的业务模型算法 (另开 id=90/91/97/198)、数据仓库/数据湖自身的 ETL 工程 (专题另开)、非 ML 的通用 DevOps / SRE 工具、端上 ML (on-device) 的完整训练循环 (专题另开)、广告/推荐系统的业务 KPI 归因。排除不是"忽略"而是主动声明——面试官问模型算法时我知道这超范围、可以明确"这是 platform-only 设计"。

**必问五问的本题答**：Q1 规模 10K 训练作业/day + 100K 部署变更/day + 1 PB/day 特征日志 + 100M QPS Feature Serving；Q2 读写比 Feature Serving 读远大于写——单 inference 10-50 feature lookup、在线读 > 1B reads/s、特征写 < 10M events/s；Q3 延迟 Feature Serving 2ms / Model Serving 50ms 是整篇最硬的数字；Q4 一致性 Model Registry stage promotion 与 Quota 扣减强一致、其他 eventual；Q5 地域 多 region active-active、跨 region 走异步 metadata 复制，训练作业只在单 region 跑避免跨 region 数据传输成本。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，Feature Serving 2ms 与 Model Registry 强一致是两个最硬的约束，任何子系统选型都要反向追溯到"因为需求里说过……"。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个建模与基础设施决策找实在的瓶颈锚点——哪条路径是真有压力、数字背后绑着哪个技术拐点。我按训练集群 → 在线特征 → 事件回流 → 模型存储四条链路走一遍，每一段除了给数字还给出对应的选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### 训练集群规模 (10K jobs/day × 平均 4h × 8 GPUs = 320K GPU-hours/day)

日均 10K 训练作业、平均 4 小时 × 8 GPU = 每作业 32 GPU-hours、日均 **320K GPU-hours**、峰值并发 **~10K GPU 常驻 + 30K 弹性抢占**。这个数字把集群调度直接压进"必须 **Gang Scheduling** (组调度) + Preemption 抢占式配额 + 多租户隔离"的硬件边界。

训练集群编排我选 **Kubeflow + Volcano batch scheduler**，因为 Kubeflow 在 Kubernetes 原生、Volcano 提供 Gang Scheduling + Preemption + fairshare、与 PyTorchJob / TFJob / MPIJob 这些 CRD 原生对齐、社区活跃 + 大厂 (Bloomberg / NVIDIA) 线上规模验证过。候选一是 **Slurm**——HPC 界黄金标准、gang-scheduling 成熟、优先级队列完善，但容器化支持弱、CI/CD 集成差、与 Kubernetes 生态割裂，Slurm 更合适的位置是科研 HPC 而非云原生 ML 平台，所以不用。候选二是 **YARN + Submarine**——与 Hadoop 生态融合好、大数据团队熟悉，但 GPU 抢占语义弱、Kubernetes 才是新的标准，YARN 更合适的位置是还在 HDFS + Spark 主栈的遗留系统，淘汰。候选三是 **Ray Cluster**——actor 模型灵活、分布式 RL / hyperparam tuning 原生支持，但作为整体 batch scheduler 还不成熟、多租户隔离弱于 Volcano，Ray 更合适的位置是 inner-loop 分布式训练框架而非 cluster-level scheduler；保留作 training job 内部的 task-level 编排。候选四是 **Nomad**——部署简单、资源模型通用，但 GPU-aware 调度能力远弱于 Volcano、社区 ML workload 经验少，Nomad 更合适的位置是混合型基础设施调度而非 ML 专用栈。切换触发：当公司主栈从 Kubernetes 切回 HPC 时评估 Slurm；当 Ray 在 cluster-level scheduling 能力成熟时可替换 Volcano。

> **常见追问**：
> 1. "GPU 怎么抢占？" —— Volcano preemption policy 定 priority class，高优先级作业可抢低优先级、被抢作业从 checkpoint 恢复 (依赖训练框架写 checkpoint 的纪律)；配合 spot/preemptible instances 节省 60-80% 成本。
> 2. "多租户 quota 怎么分？" —— 按团队 → 业务线 → 项目三层 namespace 配额，hard quota 防超用 + soft quota 允许抢占；Volcano queue capacity 定静态分配 + burst policy 定动态借用。
> 3. "Gang scheduling 的队头阻塞 (head-of-line blocking) 怎么办？" —— backfill 策略：大作业等齐时允许小作业插队，前提是不延后大作业预计启动时间；Volcano 的 fairshare 插件自动做。

### 在线 Feature Serving 规模 (100M QPS × 20 lookup = 2B reads/s)

聚合公司所有在线模型、Feature Serving 峰值 100M QPS × 每次推理 20 个特征 lookup ≈ **2B reads/s**，热存 **1B 用户 × 500 特征 × 20B = 10 TB**，p99 < 2ms。

在线热层我选 **Redis Cluster 512 节点 + RocksDB 持久化兜底**，因为 Redis 单节点 100K QPS 读、512 节点合计 50M reads/s 留 25× headroom (上文 2B/s 需分层缓存 L1 本地 + L2 Redis + L3 DB)、RocksDB 兜底重启雪崩、与线上推理服务的 feature fetch gRPC 客户端池成熟。候选一是 **DynamoDB**——托管省运维、multi-AZ 自动冗余，但 on-demand 单价 5-10× Redis 自建、10 TB × 2B reads/s 的月账单直接破千万美元，DynamoDB 更合适的位置是中小流量或按量付费场景，所以不用。候选二是 **Memcached**——纯 KV 延迟更低、协议简单，但不持久化、重启全冷启 > 60 分钟、一致性哈希漂移导致连接抖动，Memcached 更合适的位置是完全无状态 page cache 而非特征读，淘汰。候选三是 **Cassandra**——LSM 写吞吐高、持久化稳健，但 p99 read 10-20ms 撞 2ms SLA、命中率低于 Redis，Cassandra 更合适的位置是 warm 层/offline 训练 feature join 而非在线 hot 层。候选四是 **ScyllaDB**——C++ 重写 Cassandra 性能提升 5-10×、shard-per-core 架构先进，但社区规模仍小于 Redis、多语言客户端成熟度不足，ScyllaDB 更合适的位置是大吞吐写偏重的场景；保留作 warm 层备选。切换触发：流量再涨 2× 时扩到 1024 节点；当成本比 > 40% 时评估 ScyllaDB 承接 warm 层。

> **常见追问**：
> 1. "Redis 重启 10TB 怎么办？" —— AOF everysec + RocksDB 同步写、重启从 RocksDB 预热、冷启 < 10 分钟；极端场景流量降级到只读 Cassandra 跑 50% 流量。
> 2. "Train-serve skew 怎么防？" —— 同一份 Feature Store schema (Feast 或 Tecton) 同时出训练与 serving；训练 point-in-time join 与 serving 走同一套 feature transform 代码。
> 3. "新特征注册到上线多久？" —— schema registry 注册 (< 5 分钟) → 回填 offline store (小时级) → 启用 online sync (< 15 分钟延迟) → 灰度给一两个 endpoint 验证 → 全量，端到端 1-2 小时。

### 事件回流规模 (1 PB/day = 12 GB/s 持续)

特征日志 (曝光/点击/转化/feature snapshot) **1 PB/day ≈ 12 GB/s 持续**、峰值 40 GB/s。

事件总线我选 **Kafka 1024 partitions + MirrorMaker2 跨 region 异步复制**，因为单 partition 20-30 MB/s、1024 partition 合计 > 25 GB/s 留 2× headroom (峰值 40 GB/s 需要扩到 2048)、exactly-once 语义 + 消费组隔离让训练 sink、实时监控与回流 S3 互不干扰、MirrorMaker2 做跨 region 灾备复制。候选一是 **Apache Pulsar**——多租户隔离好、Segmented storage 灵活、tiered storage 把冷数据下沉 S3，但运维复杂度高、社区生态规模仍弱于 Kafka、ML 团队学习曲线陡，Pulsar 更合适的位置是需要强多租户隔离的 SaaS 场景，所以不用。候选二是 **AWS Kinesis**——托管省运维、与 Lambda 无缝整合，但单 shard 1 MB/s 上限低、rescaling 手动、成本 3× Kafka 自建、跨云供应商锁定，Kinesis 更合适的位置是纯 AWS Lambda-only 栈，淘汰。候选三是 **RabbitMQ**——事务语义丰富、消息路由灵活，但吞吐上限约 200 MB/s、远不够 GB/s 级回流，RabbitMQ 更合适的位置是 RPC-like 事件扇出而非大规模流式摄入。候选四是 **NATS JetStream**——轻量、低延迟、云原生，但 exactly-once 语义与 Kafka 比不成熟、大规模持久化生态弱，NATS 更合适的位置是微服务间的轻量事件流。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈 serverless 化时评估 Kinesis。

### 模型存储规模 (100K deployments/day × 50MB = 5TB/day + 30 day retention = 150 TB)

日均 100K 模型版本 (含灰度步进) × 平均 50 MB artifact ≈ **5 TB/day**，30 天保留 **150 TB**，推理服务冷启需 30s 内拉起最新 artifact。

模型存储底层我选 **S3 + Delta Lake 元数据 + CloudFront CDN 推理热缓存**，因为 S3 $0.023/GB/月存 150 TB 仅 $3500/月、Delta Lake 做 ACID 版本控制 + schema evolution + time-travel、CloudFront 让推理副本冷启从 30s 压到 < 5s。候选一是 **HDFS**——适合批处理但 NameNode 单点运维重、云原生方向工具链逐渐转 S3，HDFS 更合适的位置是私有云强合规场景，所以不用。候选二是 **MinIO (S3-compatible self-hosted)**——与 S3 API 兼容、自托管降成本，但运维复杂度高、多 region 复制工具链不如 S3 原生，MinIO 更合适的位置是单 region 强合规团队，淘汰。候选三是 **GCS + BigQuery metadata**——与 Vertex AI 原生集成、分析友好，但跨云供应商锁定、BigQuery scan 成本随 model registry 查询增长，GCS 更合适的位置是 GCP 全栈团队。切换触发：跨云团队需要对等存储时评估 MinIO；GCP 主栈时迁 GCS+Vertex。

这一节 takeaway：320K GPU-hours/day 推出 Kubeflow + Volcano、2B reads/s 推出 Redis 512 节点、12 GB/s 事件推出 Kafka 1024p、150 TB 模型存储推出 S3+Delta——这四个数字把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按**平台能力层 + SLA + 一致性**切、而不是按组件名切；数据怎么流——端到端 Experiment → Training → Artifact → Registry → Deployment → Serving → Monitoring 的 fan-out 结构要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：Training Orchestrator 的 hours 级作业 SLA 和 Feature Serving 的 ms 级 SLA 不能共用线程池、Model Registry 的强一致 stage promotion 必须独立出来不能挂在任一 serving 内。

服务拆分策略我选 **按平台能力层 + SLA + 一致性切分**，因为 Orchestration (hour 级 batch) / Feature Serving (ms 级 sync) / Model Serving (ms 级 sync, GPU) / Monitoring (second 级 streaming) 是四个独立 SLA + 两种一致性要求，每层允许独立扩缩容、独立 A/B 分流、独立故障域；把这四层塞一个 "ML Platform" monolith 会出现任一层流量飙升把整个平台打崩的级联故障。候选一是按 **业务域切分** (Recommendation team / Ads team / Fraud team)——每个 team 自建一份完整平台、完全忽略复用，平台割裂、训练-服务偏差无法集中解决、GPU 利用率分散，候选一更合适的位置是初创期团队 < 10 人直接上托管 SageMaker，淘汰。候选二是按 **模型生命周期阶段切分** (Train / Eval / Serve)——看似合理但忽视多阶段共享的 Feature Store 与 Lineage，候选二更合适的位置是小规模 MVP 平台，而非 100-1000 工程师量级。候选三是按 **客户端切分** (Python SDK / CLI / Web UI) ——与本题无关，平台服务对客户端透明，淘汰。候选四是按 **数据温度切分** (Hot / Warm / Cold)——适合纯存储系统，但 ML 平台切分维度应是能力而非温度，Hot/Cold 在 Feature Store 内部才是合理粒度。切换触发：当某层流量下降到与邻层差距 < 2× 时可合并；当出现新数量级 SLA 差异时再切一刀 (例如引入 LLM inference 后 p99 拉到 500ms 必须拆一层)。

> **常见追问**：
> 1. "Experiment Tracking 放哪？" —— 独立 metadata 服务，写 < 500ms 不阻塞训练循环；MLflow / W&B 都可内嵌 SDK 让训练代码直接 log，平台侧只负责后端 metadata store。
> 2. "Feature Store 是一个服务还是两个？" —— 两个，写端 (batch/streaming ingestion) 与读端 (online serving) SLA 差 1000×、必须分开部署；共享 schema registry。
> 3. "Deployment Service 怎么调度灰度？" —— 独立 controller，按策略 (shadow / canary / blue-green) 生成流量分配状态；与 Istio / Envoy 的路由规则联动执行。

端到端数据流：ML 工程师提交 experiment → Orchestrator 调度 DAG → Training job 从 Feature Store offline 读特征 → 写指标 + checkpoint 到 Experiment Tracker 与 S3 → 产出 model artifact 注册到 Model Registry (Staging stage) → Deployment Service 按策略 (Shadow 先、Canary 后) 推到 Model Serving 集群 → Feature Serving 与 Model Serving 一起接在线流量 → 推理结果 + 特征快照流回 Kafka → Monitoring 实时消费 Kafka 做漂移检测 → 触发阈值时通知 Deployment Service 自动回滚到上一版本 → Lineage 持续记录从 raw data → feature → experiment → model → deployment 的全链路血缘。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——Feature Serving 挂了走 per-feature default / 7 天滑动均值、Model Serving 挂了走上一版本快照、Orchestrator 挂了训练作业可延后 1h 不影响在线、Monitoring 挂了 Deployment 暂停灰度而不是强推。

这一节 takeaway：ML 平台的服务边界不是组件边界而是能力层 + SLA + 一致性边界；任一层必须自带 fallback，Model Registry 的强一致性与 Feature Store 的在线热读是整条链路两大耦合点。

## 4. Deep Dives

这一节把 ML 平台核心四块 (Training Orchestration / Feature Store & Data / Model Serving & Deployment / Monitoring & Lineage) 逐一展开，每一块给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"ML 平台每层选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章编排顺序与平台生命周期一致：Training 在前、Feature 贯穿训练与 serving、Deployment 承接 Training 产物、Monitoring 闭环反哺。

### 4a. Training Orchestration & Distributed Compute

Training Orchestration 的本质是在 10K jobs/day 规模下做"可靠调度 + 资源隔离 + 故障恢复"三件事。除了 §2 给的 Kubeflow + Volcano (scheduler 层) 之外，还需要**作业级工作流编排**与**分布式训练策略**两个配套决策。

作业级工作流编排我选 **Airflow 2.x (with KubernetesExecutor)**，因为它 DAG 表达力成熟、调度引擎久经考验、与 Python-first 工作流原生兼容、100K+ DAG 规模在 Airbnb / Lyft / 各大厂都有公开案例。候选一是 **Prefect**——Pythonic API 更现代、动态 DAG 支持好、UI 更清爽，但社区规模仍小于 Airflow、大规模案例有限、企业功能部分闭源，Prefect 更合适的位置是纯 Python 团队的新项目 MVP 阶段，所以不用。候选二是 **Dagster**——asset-based 抽象优雅、data contract 原生集成，但学习曲线比 Airflow 陡、社区规模中等、需要 re-model 现有 DAG，Dagster 更合适的位置是新团队从零建设 + 愿意投入重构的场景，淘汰。候选三是 **Argo Workflows**——Kubernetes-native、YAML 表达 workflow、与 Kubeflow 同栈，但 YAML DAG 表达力弱于 Python、参数化与条件分支支持差、ML 工程师学习成本高，Argo 更合适的位置是容器化 CI/CD pipeline 而非 ML 工作流。候选四是 **Flyte**——Linked In 出品、type-safe Python API、容器化 ML workflow 专用，但工具链成熟度 + 插件生态小于 Airflow、与 Kubeflow 部分功能重叠，Flyte 更合适的位置是 type-safety 强要求 + 团队愿意绑定单一生态。候选五是 **Metaflow**——Netflix 出品、human-friendly API、科研-to-production 平滑迁移，但集群规模化能力中等、多租户支持弱，Metaflow 更合适的位置是中等规模数据科学团队 (50-200 人)。切换触发：团队规模 < 50 + 强 Pythonic 倾向时迁 Prefect；type-safety 成为核心诉求时迁 Flyte；数据科学为主 + 运维资源紧张时迁 Metaflow。

> **常见追问**：
> 1. "DAG 失败重试怎么做？" —— Airflow 原生 retries + retry_delay + exponential backoff，失败任务保留上游依赖状态；结合 S3 artifact caching 避免无谓重跑。
> 2. "DAG 之间依赖怎么管？" —— ExternalTaskSensor + Datasets API，或使用 Airflow 2.4+ 的 Data-aware scheduling；跨 DAG 依赖本质是 data contract。
> 3. "运维 10K 作业 Airflow scheduler 顶得住吗？" —— KubernetesExecutor 横向扩展、多 scheduler 架构 2.2+ 支持、metadata DB (Postgres) 分库分表后千万级任务可持。

分布式训练策略我选 **PyTorch DDP + FSDP 按模型大小自动切换**，因为 DDP 在模型可放入单 GPU (< 10B 参数) 时 throughput 最高、FSDP 在模型超 GPU 容量 (10B-100B) 时 memory-efficient、两者在 PyTorch 2.x 里 API 一致易切换、与 MLPerf benchmark 对齐、与 Triton / TorchServe 下游部署无缝。候选一是 **DeepSpeed (ZeRO Stage 2/3)**——显存优化最激进、ZeRO-Infinity 支持 trillion 参数、与 Hugging Face Transformers 原生集成，但学习曲线陡、调参空间大、部分优化器不兼容，DeepSpeed 更合适的位置是超大 LLM 预训练 (100B-1T 参数)，在公司通用 ML 平台属于专项优化不是默认。候选二是 **Horovod (NCCL-backed)**——MPI 风格、跨 framework 通用 (PyTorch/TF/MXNet)、大规模 all-reduce 优化成熟，但 PyTorch 场景下 DDP 已足够成熟、Horovod 的 double-hop 往往多 5-10% 开销，Horovod 更合适的位置是多 framework 混用 + 跨 framework 团队协作，淘汰。候选三是 **Megatron-LM**——NVIDIA 出品、tensor parallelism + pipeline parallelism 极致优化、Trillion 参数训练 benchmark 最优，但 code-base 侵入性强、需要深度改动训练脚本，Megatron 更合适的位置是专门的 LLM 训练团队而非通用平台。候选四是 **Ray Train**——与 Ray Cluster 原生集成、fault tolerance 好，但成熟度仍在快速演进、与 PyTorch 生态整合不如 DDP 原生，Ray Train 更合适的位置是 Ray 全栈团队。切换触发：模型超 100B 参数时上 DeepSpeed ZeRO-3 / Megatron；多 framework 共存时评估 Horovod。

> **常见追问**：
> 1. "Pipeline Parallelism 什么时候用？" —— 模型超单节点 8 GPU 总显存时、通常百亿参数以上；按层切分 + micro-batch 减少 pipeline bubble。
> 2. "Checkpoint 频率与 recovery 时间？" —— 大作业按 epoch / 每 30 分钟出一次增量 checkpoint，recovery 从最近 checkpoint 恢复 <5 分钟；checkpoint 写 S3 + 本地 SSD 双份。
> 3. "Preemption 对训练影响大不大？" —— 有 checkpoint 的训练作业抢占代价 5-10 分钟恢复、可接受；无 checkpoint 的 RL 或 online training 需要 priority class 标记不可抢占。

### 4b. Feature Store & Data

Feature Store 是 ML 平台里最直接影响精度的组件——训练-服务偏差 (Training-Serving Skew) 的根源几乎全在这里。本子节覆盖 Feature Store 技术选型与 point-in-time join 两条核心决策，Feature Serving 在线热层 (Redis vs DynamoDB vs Cassandra) 已在 §2 给出，此处不重复。

Feature Store 平台我选 **Feast (open-source) + 自建 schema registry**，因为 Feast 在 online/offline dual-store 抽象上是业界事实标准、与 S3 + Redis + BigQuery 多后端原生兼容、schema 注册机制支持 point-in-time join、社区活跃 + 大厂 (Gojek / Shopify / Twitter) 公开案例多、与 Kubeflow / MLflow 集成成熟。候选一是 **Tecton (commercial managed)**——SaaS 省运维、streaming feature pipelines 原生、monitoring 内置，但年许可费 > $1M、跨云锁定、深度定制困难，Tecton 更合适的位置是中等规模团队愿意付 managed 溢价 + 业务场景标准化强，所以不用。候选二是 **Hopsworks**——Java/Scala 栈完整、与 Spark + Hive 紧耦合、欧洲合规友好，但 Python-first 工具链弱、与 PyTorch/MLflow 集成不如 Feast 原生，Hopsworks 更合适的位置是 JVM-heavy 主栈或强合规场景，淘汰。候选三是 **自建 (home-grown) Feature Store**——完全可控、与内部系统深度整合，但需要 5-10 人团队持续投入 2-3 年建成、维护成本极高、版本落后社区 1-2 年，自建更合适的位置是 FAANG 规模 (Meta FBL / Airbnb Zipline / Uber Michelangelo) 的深度定制。候选四是 **Databricks Feature Store**——与 Delta Lake 深度集成、Spark-native，但与 Databricks 生态锁定、脱离 Databricks 无法使用，Databricks FS 更合适的位置是 Databricks 主栈团队。切换触发：规模到达 FAANG 级 + 强差异化诉求时评估自建；标准化业务场景 + 预算宽裕时迁 Tecton。

Point-in-time join 策略我选 **Iceberg time-travel snapshot + as-of-timestamp 物理 key join**，因为 Iceberg 原生支持时间快照、与 Spark / Flink / Presto / Trino 全兼容、避免传统 Hive 分区的"T-1 特征混入训练集"污染、实现简单。候选一是 **Delta Lake time-travel**——ACID 事务更严格、schema evolution 完整，但与 Databricks 强绑定、跨云工具链不如 Iceberg 中立，Delta 更合适的位置是 Databricks 全家桶，所以不用。候选二是 **Hive partition-based snapshot**——遗留系统成熟、SQL 原生，但分区粒度粗 (日级/小时级)、无法精确到秒级、易混入未来数据，Hive 更合适的位置是传统数据仓库兼容场景，淘汰。候选三是 **自建 snapshot 表 + event_time 字段 filter**——完全可控，但需要实现 ACID + schema evolution + compaction，造 Iceberg 轮子成本高，自建更合适的位置是历史遗留系统无法换底层时。切换触发：跨团队要强 ACID 写入时迁 Delta Lake；遗留 Hive 主栈时过渡期用 Hive partition；完全无外部依赖诉求时考虑自建。

> **常见追问**：
> 1. "Train-serve skew 闭环怎么做？" —— 同一份 Feature Store schema 出训练与 serving、feature transform 代码共享 (Feast 的 Feature View)、CI 跑 skew check (same input → same output)。
> 2. "特征新鲜度怎么保证？" —— Streaming feature (Kafka → Flink → Redis) 做秒级更新、Batch feature (S3 → Spark → Redis) 做小时级更新、on-demand feature (请求时计算) 做毫秒级；按新鲜度 SLA 路由。
> 3. "多模型共用特征怎么避免互相污染？" —— Feature namespace + tag 隔离、schema 注册时声明 owner team、feature deprecation 必须经过 30 天 sunset 期。

### 4c. Model Serving & Deployment

Model Serving 的任务是把 Model Registry 里的 artifact 高效、稳定、可灰度地推到在线流量。延迟 p99 < 50ms、100K deployments/day 变更、同时服务千级模型。

Model Serving 引擎我选 **NVIDIA Triton Inference Server**，因为 Triton 支持多框架 (PyTorch / TF / ONNX / TensorRT) 统一推理栈、dynamic batching + model ensemble + concurrent execution 三合一、GPU 利用率可推到 70%+、与 Kubernetes HPA + NVIDIA GPU Operator 原生集成、社区活跃 + 大厂 (NVIDIA / Meta / Snap) 公开案例多。候选一是 **TorchServe**——PyTorch 原生、部署路径短，但多框架支持弱、batching 策略灵活度低、GPU 利用率不如 Triton，TorchServe 更合适的位置是纯 PyTorch 团队 MVP 阶段，所以不用。候选二是 **TensorFlow Serving**——TF 原生、久经生产考验，但 framework 绑定、与 PyTorch 模型融合需要 ONNX 转换、新架构 (Transformer 变种) 支持滞后，TF Serving 更合适的位置是遗留 TF 主栈团队，淘汰。候选三是 **Seldon Core**——Kubernetes-native、Explainability + A/B 原生内置、企业级工作流完整，但运行时性能不如 Triton (GPU 利用率低 10-20%)、学习曲线陡，Seldon 更合适的位置是解释性与合规为核心诉求的场景。候选四是 **BentoML**——Python-first、打包分发体验好、与 Hugging Face 集成原生，但集群规模化能力中等、GPU 推理优化不如 Triton，BentoML 更合适的位置是 ML 工程师 quick-prototype + 中等规模部署。候选五是 **KServe (原 KFServing)**——Kubeflow 全家桶一致、serverless 模式支持，但底层仍需要 Triton / TF Serving 承载，KServe 更合适的位置是 Kubeflow 深度集成团队的上层抽象。切换触发：纯 PyTorch 单 framework 时可 TorchServe 省运维；强解释性合规场景时评估 Seldon。

Deployment 策略我选 **Shadow → Canary → Full，三阶段自动推进**，因为 Shadow Deployment 先复制流量到新模型不影响线上、验证预测一致性 (避免全面翻车)、Canary Release 再逐步扩大流量 1% → 5% → 25% → 100% 每步验证关键指标、全程自动化减少人为失误。候选一是 **Blue-Green Deployment (两套集群瞬时切换)**——回滚极快 (秒级)、无灰度复杂度，但资源占用 2×、无法按流量比例灰度、业务指标需要时间回流才能判断新模型质量，Blue-Green 更合适的位置是非 ML 的传统 web 服务或低频变更场景，所以不用。候选二是 **A/B Testing Only (直接上 50/50 对比)**——科学严谨、指标置信区间有理论保证，但缺乏 Shadow 的第一道验证、坏模型可能直接影响 50% 用户、业务代价高，A/B only 更合适的位置是纯科研评估而非生产 rollout。候选三是 **Manual Rollout**——完全人工控制、灵活度高，但 100K deployments/day 根本跑不动、人为失误代价大，Manual 更合适的位置是季度一次的重大架构变更，淘汰。切换触发：回滚 SLA < 10s 时可用 Blue-Green 并行 (高成本场景)；A/B 变成核心评估手段时嫁接在 Canary 的 5% 阶段。

Circuit Breaker 回退我选 **基于业务 SLO 的自动熔断**，因为业务 SLO (CTR 比基线跌 > 2σ、延迟 p99 超 SLA) 是唯一可观察的下游反馈、用之作为触发条件对 false positive 有天然鲁棒性、与 Canary 的指标监控天然同轨。候选一是 **基于错误率的熔断 (5xx > 1%)**——简单直接、与通用 SRE 工具链兼容，但 ML 故障往往不是 HTTP 5xx 而是"预测分布漂移但延迟正常"，错误率熔断更合适的位置是传统 web 服务，在 ML 场景不够。候选二是 **基于延迟的熔断 (p99 > 2× 基线)**——资源耗尽能抓到，但无法识别 silent accuracy 退化，延迟熔断更合适的位置是资源型故障监控、作为辅助维度保留。候选三是 **人工熔断**——完全可控，但 30 分钟反应太慢、100K deployments/day 扛不住、不适合 L5 平台，人工熔断更合适的位置是初创期运维负责人亲力亲为阶段，淘汰。切换触发：业务 SLO 监控未上线时退回错误率 + 延迟混合熔断；SLO 监控全链路上线后切自动。

> **常见追问**：
> 1. "Canary 从 1% 升到 100% 用多久？" —— 按业务可接受的 A/B 显著性所需样本量决定，通常 24-48h 过完；高流量场景 6-12h 也够。
> 2. "Rollback 多快？" —— Model Registry 保留最近 5 个稳定版本，回滚从 Deployment Service 下发路由变更到 Envoy 生效 < 30s；与 Circuit Breaker 联动自动触发。
> 3. "多模型版本共存 GPU 怎么分？" —— Triton model priority + weighted scheduling，老版本缩减 GPU 配额 + 新版本渐增；K8s HPA 按 QPS + GPU util 双维度扩缩。

### 4d. Monitoring & Lineage

Monitoring 的任务是让模型漂移、特征漂移、业务指标退化三类信号在第一时间被发现；Lineage 的任务是任何故障发生时能从 deployment 倒查到 feature + training data + code commit 的全链路证据。

模型漂移监控策略我选 **四象限监控 + 分层 SLO**，因为 system / model / data / business 四个维度要分开看、分层 SLO 让降级决策可编程，与广告 / 推荐 / 电商跨业务场景都通用。系统层对接 **Prometheus + Grafana** 采集 p99 延迟、error rate、资源利用率；模型层引入 **Evidently AI** 采集 CTR/CVR 预测分布漂移 (PSI > 0.2 触发)、特征分布漂移 (KS Test p < 0.01)、embedding 退化 (cos sim 飘离基线 > 0.1)、校准比 drift；数据层采集特征 null rate、schema violation、freshness lag、duplicate rate；业务层接入内部 BI 看业务 KPI (CTR / CVR / GMV / retention)。候选一是 **Datadog 单栈统一中台**——工具链简化但跨维度语义损失、模型漂移细节看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize AI**——ML 专用指标全、embedding drift + SHAP 解释内嵌，但与系统监控割裂、告警链路双头、年许可 $500K-2M，Arize 更合适的位置是模型 ops 团队独立于平台团队 + 预算充裕时，淘汰。候选三是 **WhyLabs**——lightweight profiling 思路优雅、数据契约原生，但企业功能不如 Arize 深、生态规模中等，WhyLabs 更合适的位置是数据科学团队 MVP 阶段。候选四是 **Fiddler**——可解释性专精、公平性审计完整，但与开源 Prometheus 生态整合成本高、许可证费用贵，Fiddler 更合适的位置是强合规场景 (金融/医疗)。候选五是 **自建 full-stack 监控**——灵活度最高但研发成本巨大，自建更合适的位置是 FAANG 规模深度定制。切换触发：模型漂移成为核心故障源时补 Arize；团队规模 > 100 MLE 时考虑自建核心监控栈。

漂移指标选择我选 **PSI (预测分布) + KS Test (特征分布) + 业务 SLO**，因为 PSI 是工业界事实标准 (信用评分业至少用了 20 年)、KS Test 非参数化对分布假设弱、业务 SLO 是最终兜底。候选一是 **KL Divergence (KL 散度) 单用**——信息论严谨、数学优雅，但对零概率桶敏感 (需要 smoothing) + 不对称、工业上不如 PSI 直观，KL 更合适的位置是理论分析或研究场景，所以不用。候选二是 **Jensen-Shannon Divergence**——KL 的对称化版本、平滑性好，但仍对桶划分敏感、工业 adoption 少于 PSI，JSD 更合适的位置是 NLP 分布对比场景。候选三是 **Wasserstein Distance (EMD)**——连续分布几何直观、对零概率鲁棒，但计算开销大 + 对桶无要求但需要定 metric、工业 ML monitor 用得少，Wasserstein 更合适的位置是图像生成质量评估 (FID)。切换触发：业务对概率分布严谨度要求极高时补 JSD + Wasserstein 做 triple-check；快速 MVP 阶段 PSI 单用就够。

Lineage 追踪我选 **MLflow + DVC + Airflow Dataset API 三件套**，因为 MLflow 管 model lineage (artifact → run → experiment)、DVC 管 data lineage (dataset → commit → pipeline)、Airflow 2.4+ Dataset API 管 DAG-level 数据依赖、三者互补、全栈开源、配合自建 blame service 可 30 秒内从 deployment 溯源到 data commit。候选一是 **Weights & Biases (W&B)**——UI 最现代、 artifact tracking 原生、团队协作好，但 W&B 管 model 那一段强、data lineage 弱、年许可 $500K-2M、企业合规需要私有化部署，W&B 更合适的位置是 ML 研究团队 + 预算充裕，所以不用。候选二是 **Neptune**——metadata store 灵活、定制化强，但生态规模小、社区不如 MLflow 活跃，Neptune 更合适的位置是强定制化 metadata 场景，淘汰。候选三是 **Pachyderm**——Git-for-data 思路彻底、versioning 严谨，但运维复杂度高、与通用 Airflow 栈整合成本大、社区规模小，Pachyderm 更合适的位置是生物信息 / 基因组学等强 data versioning 场景。候选四是 **自建 lineage service**——完全可控、与内部系统整合深，但造轮子成本极高，自建更合适的位置是 FAANG 规模 (LinkedIn DataHub / Uber Databook)。切换触发：研究团队主场 + 预算宽裕时补 W&B；data versioning 成为核心诉求时评估 Pachyderm。

> **常见追问**：
> 1. "漂移告警误报率怎么控？" —— 阈值学自历史 (至少 30 天滑窗) + 双阈值 (warning / critical) + 告警抑制 (相同类型 1h 内不重复) + 业务侧 SLO 兜底避免指标误杀。
> 2. "模型性能静默退化怎么发现？" —— 业务 KPI 滑动 7 天 vs 7 天对比、A/B 持续 mini-holdout (1% 流量永远跑老模型作为参照基线)、offline replay (用当天真实流量回放新老模型对比 AUC)。
> 3. "Lineage 查询时间线？" —— MLflow run → artifact → Feature View → Iceberg snapshot → data commit 一条链 30 秒内可查；配合 Airflow Dataset API 追溯到 DAG task 失败节点。

这一节 takeaway：ML 平台不是单件工具、而是四块 (Orchestration / Feature / Serving / Monitoring) 算法与工具候选池的组合；每块默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Multi-tenancy, DR & Cost, 5m)

平台可靠性的关键是**多租户隔离 + 分层降级 + 成本可归因**三件事。与业务系统可靠性相比，平台故障的影响面是 1-N 个业务线同时受损，所以 blast radius containment 比 RTO / RPO 更关键。

多租户 quota 策略我选 **三层 namespace (team → business → project) + hard/soft quota 混合**，因为层级 namespace 符合组织架构、hard quota 防超用、soft quota 允许空闲时借用。候选一是 **无 quota (free-for-all)**——简单粗暴、ML 工程师体验好，但强势团队吞所有 GPU、弱势团队饿死，无 quota 更合适的位置是 < 10 人初创期，所以不用。候选二是 **按用户独占 quota**——公平透明，但颗粒度过细、GPU 碎片化严重、利用率掉到 30% 以下，独占 quota 更合适的位置是个别高敏感实验 (带 HIPAA 数据的医疗模型)，淘汰。候选三是 **按业务线固定预算 (Static budget)**——年度预算可预测，但无法响应突发需求、抢占灵活度差，Static 更合适的位置是预算严格受控的 regulated industry。切换触发：公司规模 < 20 人时退无 quota；强合规 / 高敏感场景切独占 quota。

GPU 集群可靠性我选 **按作业优先级分三级 queue + preemption + spot instance 混用**，因为三级 queue (prod-critical / prod-batch / experimental) 对应不同 SLA + 不同 preemption 敏感度、spot instance 为 experimental queue 降 60-80% 成本。候选一是 **全 on-demand 独占**——最稳但最贵、利用率也低，全 on-demand 更合适的位置是 < 100 GPU 小集群，所以不用。候选二是 **全 spot**——成本最低但稳定性差、prod 不可靠，全 spot 更合适的位置是纯实验性研究集群，淘汰。候选三是 **Reserved Instance + Spot 混合**——年预算锁定部分 reserved + 剩下 spot 兜底、成本介于中间，Reserved + Spot 更合适的位置是中等规模 + 预算可预测团队。切换触发：训练作业稳定性要求 > 99.9% 时切全 on-demand；完全实验性研究时切全 spot。

降级预案：Feature Serving 挂了走 per-feature default (7 天滑动均值) 兜底；Model Serving 挂了 fallback 到上一版本快照或基线模型 (rule-based fallback)；Orchestrator 挂了训练作业可延后 1h 不影响在线 (**训练-服务解耦** 是平台设计的核心原则)；Monitoring 挂了 Deployment 暂停灰度等手工确认；Model Registry 挂了 Deployment 不允许 stage promotion 但已部署的继续服务。隐私合规方面，**GDPR** (通用数据保护条例) 与 **CCPA** (加州消费者隐私法) 要求数据脱敏与用户 opt-out、**Differential Privacy** (差分隐私) 在训练梯度添加噪声保证个体隐私、**Federated Learning** (联邦学习) 把训练留在用户设备只传梯度——这三个合规路径由平台统一封装为 SDK 避免各业务线重复造轮子。每条 fallback 路径必须独立演练、月度 game day 强制跑一次、关键服务故障 PIR 48h 内出。

成本归因我选 **按 namespace 精细 tagging + showback (先通告、后扣预算)**，因为 tagging 让每个 GPU-hour 可追溯到业务线 + 项目、showback 让各团队看到账单压力但不立即扣钱、避免一上来就 chargeback 引起政治风险。候选一是 **全公司合并账单**——运维省事，但各团队没有成本意识、浪费严重，合并账单更合适的位置是早期 < 100 人团队，所以不用。候选二是 **立即 chargeback (直接扣预算)**——成本纪律最强，但政治阻力大、引发"平台团队是收费部门"敌意，立即 chargeback 更合适的位置是 FinOps 成熟度高 + 组织架构稳定的阶段。候选三是 **按使用量粗分配 (quarterly true-up)**——折中、季度对账一次，但时效差、激励信号弱，粗分配更合适的位置是过渡期。切换触发：FinOps 成熟度高 + 组织稳定时可切立即 chargeback。

这一节 takeaway：平台可靠性不在单点高可用而在**分层可降级 + 多租户隔离 + 成本可归因**；三层 quota + spot/reserved 混合 + 四象限监控 + 每层独立 fallback + 隐私合规 SDK 是平台级可靠性的完整拼图。

## 6. Summary & Tradeoffs

本题核心 takeaway 是 ML 平台的四轴思维：迭代速度 (想法到 A/B)、上线安全 (回滚与渐进)、多租户公平 (配额与抢占)、成本可控 (归因与优化) 必须在同一条时间轴上平衡。默认栈 Orchestrator = Kubeflow + Volcano + Airflow、Training = PyTorch DDP/FSDP、Feature Store = Feast + Iceberg、Serving = Triton + Canary/Shadow、Monitoring = Prometheus + Evidently、Lineage = MLflow + DVC。演进链条 Airflow → Prefect/Dagster (Pythonic)、DDP → FSDP → DeepSpeed (模型规模)、Shadow → Canary → Blue-Green (回滚速度)、Prometheus → Arize/WhyLabs 做 ML-专用监控、MLflow → W&B 做 UI 体验升级、DVC → Pachyderm 做 data versioning 严谨度升级。

三个最常被错答的 tradeoff：一是"自建还是用开源"——平台核心能力 (Orchestration / Feature Store / Monitoring) 默认用开源 + 薄自建 adapter、FAANG 规模才全自建；二是"管理成本 vs 灵活度"——Tecton / W&B 等 managed 省运维但年费破百万、开源 Feast / MLflow 省钱但运维投入大、关键是团队 ML 成熟度与运维资源匹配；三是"快速迭代 vs 上线安全"——Shadow + Canary 看似慢 24-48h，但平台一个 bad rollout 影响 1-N 个业务线、收益远大于速度。持续训练路径由 **Continuous Training** pipeline 接管：监控发现分布漂移 → 自动触发重训 → Shadow Deployment 验证 → Canary Release 渐进 → Automatic Rollback 兜底。长期优化依赖**平台飞轮**：好用的平台吸引更多工程师→更多实验→更好的模型→更多业务价值→更多预算投入平台；同时警惕"平台自我膨胀"(功能过载没人用) 与"模型 factory 陷阱" (只优化训练量而忽视业务效果)。

工程 vs 建模的决策拉锯主要在四处：一是 Feature Store 在 Feast 与 Tecton 之间取舍——开源运维 vs 付费省事；二是 Serving 在 Triton 与 TorchServe 之间取舍——多 framework 与 GPU 利用率 vs 单 framework 简单；三是 Orchestrator 在 Airflow 与 Flyte 之间取舍——成熟度 vs type-safety；四是 Monitoring 在开源栈 (Prometheus + Evidently) 与 ML-native (Arize) 之间取舍——成本 vs 功能。选型的真正判据不是"谁更先进"，而是"当前团队的规模、预算、ML 成熟度、合规强度落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："训练-服务偏差 (Training-Serving Skew) 怎么从架构层彻底消除？"——这是 ML 平台最核心、最不可绕开的问题。答案思路：一是同一份 Feature Store schema 同时出训练与 serving、避免两套 transform 代码漂移；二是 feature transform 代码用同一套 library (Feast 的 Feature View 就是这种设计)、CI 跑 skew check (same input → same output) 作为硬 gate；三是训练用 point-in-time join (Iceberg time-travel) 避免未来特征混入、serving 必须用与训练同一份历史特征快照做回放评估；四是 Lineage 全链路追踪让任何一次偏差都能倒查到哪次 feature 变更导致、MLflow + DVC + Airflow Dataset 三件套承担这个功能；五是组织上把 feature ownership 归给特征发布团队而非单一模型 team、避免"我只关心自己的模型"导致的特征污染。

第二题："100K deployments/day 怎么保证不爆炸？"——这是 Deployment Service 的扩展性考题。答案思路：一是绝大部分 deployments 不是新模型而是 canary 步进 (1% → 5% → 25% → 100% 每次都是一次 deployment)、吞吐量主要来自灰度步进自动化；二是 Deployment Service 本身做水平扩展 + state machine 而非 monolith；三是 Canary 失败时自动回退 < 30s 且不重入 (idempotent)；四是 Shadow Deployment 先跑 24h 才进 canary 能挡掉 80% 坏模型；五是与 Circuit Breaker 联动 (业务 SLO 跌 > 2σ 直接回退) 构成三层防护；六是 model registry 保留最近 5 个稳定版本作为秒级回滚依据。

第三题："ML 平台如何同时服务 TikTok 规模 (100M QPS) 的业务与 startup 规模 (< 1K QPS) 的业务？"——这是多租户架构的考题。答案思路：一是分服务层级 (prod-critical / prod-batch / experimental) 的三级 quota + preemption、小流量业务不能独占资源；二是 Feature Store 按 namespace 隔离 + 跨 namespace 共享高热特征的 global namespace (减少重复存储)；三是 Serving 层按 traffic tier 分池 (高流量有独立 GPU 池 + dedicated capacity、低流量共享 spot 池) 实现成本 + 稳定性的双重控制；四是 Monitoring 按 tier 定不同告警阈值 (高流量秒级、低流量分钟级) 避免小业务刷屏；五是成本 showback 让每个业务看到自己的账单、激励自优化；六是 platform 平权：核心能力 (Orchestrator / Feature Store / Registry / Serving) 是 shared infra，业务差异化在应用层。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) ML 平台八大子系统 (Orchestrator / Feature Store / Training / Registry / Deployment / Serving / Monitoring / Lineage) 与它们的 SLA 分层；(2) Kubeflow + Volcano vs Slurm vs YARN 三种集群编排的 tradeoff 与切换条件；(3) Airflow vs Prefect vs Flyte vs Argo vs Metaflow 五种工作流引擎的 tradeoff；(4) DDP vs FSDP vs DeepSpeed ZeRO vs Megatron vs Horovod 五种分布式训练策略的参数规模边界；(5) Feast vs Tecton vs Hopsworks vs Databricks FS 四种 Feature Store 的 make/buy 决策；(6) Triton vs TorchServe vs TF Serving vs Seldon vs BentoML 五种 serving 引擎的 GPU 利用率与多 framework 支持对比；(7) Shadow → Canary → Full 与 Blue-Green 四种部署策略的回滚速度与资源成本；(8) PSI vs KL Divergence vs KS Test vs Wasserstein 四种漂移指标的适用场景；(9) MLflow + DVC + Airflow Dataset vs W&B vs Neptune vs Pachyderm 四种 lineage 方案的 data 与 model 维度覆盖；(10) Training-Serving Skew 闭环消除的五步法 (同 schema + 同 transform 代码 + CI gate + point-in-time join + Lineage 溯源)。十个都能答对就可以去白板了。
