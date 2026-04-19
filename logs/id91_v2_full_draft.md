# Ads & Click Prediction (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个广告点击预测系统"——社交 feed 广告、搜索广告、信息流广告、电商展示广告、视频贴片都能套。与 id=90 Recommendation Systems 讲"通用多阶段漏斗建模范式"不同，本题的重心是**收入导向三方博弈**：用户体验、广告主 **Return on Investment** (ROI, 投资回报率)、平台收入必须在毫秒级拍卖里同时被 ML 建模与经济学机制共同决定。本题不是"只跑一个 CTR 模型"，而是"能把 Ad Retrieval / **Click-Through Rate** (CTR, 点击率) / **Conversion Rate** (CVR, 转化率) / Auction / Budget Pacing / Attribution 这六条链路在同一条时间轴上摆清楚并给出可落地的切换触发条件"。考官会盯着两个分水岭：一是校准 (calibration) 与区分度 (AUC) 的 tradeoff、二是拍卖机制设计 (GSP / First-price / VCG) 与 ML 预测的耦合；答不清楚这两点就只能拿到 L4。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=90 Recommendation Systems](/kg?node=n90)、[id=198 Real-Time Recommendation System](/kg?node=n198)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问这五元组) 是本题所有 deep dive 的评分标尺。再读 id=90 的理由是：那篇把召回/粗排/精排/重排的建模范式讲过一遍、本题复用其中的 Two-Tower 召回与 DLRM 精排骨架，只是把"相关性"换成"收入期望 × 相关性 × 质量"。最后读 id=198 的理由是：那篇的部署数字 (100M DAU / 70K QPS / 350K ranking invocations) 与本题广告场景的 100M QPS 级峰值请求、<30ms p99 serving SLA、billions of training events/day 属于同量级。本题读者应对 **Approximate Nearest Neighbor** (ANN, 近似最近邻)、**Logistic Regression** (LR, 逻辑回归)、**Gradient Boosted Decision Trees** (GBDT, 梯度提升决策树)、**Area Under the Curve** (AUC, ROC 曲线下面积)、**Second-price auction (第二价格拍卖, GSP)** 这些概念有基础认识，否则精排选型与拍卖设计环节容易卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把产品经理的话抄一遍"，而是把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一个答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈落在拍卖排序的 GPU 推理与全局预算一致性、强一致只出现在计费归因与预算扣减一瞬、跨 region 只做异步归因不做同步竞价"。

**Functional requirements (功能需求)** 主流程是用户请求广告位 → Ad Retrieval 拉候选池 → CTR/CVR 预测 → eCPM 排序 → Auction 出清 → 曝光 → 点击/转化上报 → 模型更新；辅流程包括广告主投放工具 (预算设定、出价策略、创意上传)、审核流水线 (创意合规 + 落地页检测)、频次控制 (同用户同广告 N 次内曝光)、归因统计与计费对账。平台级功能含多目标融合 (CTR × bid × 质量分 × quality factor)、广告与自然结果混排接口、冷启动 ads 的探索配额、隐私合规保留策略。这些功能归成四组——Retrieval、Prediction、Auction、Feedback——后面 deep dive 按这四组的建模选型逐一展开。

**Non-functional requirements (非功能需求)** 规模取峰值请求 **Queries Per Second** (QPS, 每秒查询数) 100M 级 (Meta/Google 量级)、广告库 10M active campaigns × 100 creatives = 1B creatives、每请求召回 1000 候选 → 精排 200 → Auction 20 slot；延迟端到端 p99 < 30ms 是典型 **Real-time Bidding (RTB, 实时竞价)** 场景的延迟预算、分摊到 Retrieval 8ms + CTR 10ms + Auction 5ms + Logging 2ms + 网络 5ms；特征查询 p99 < 2ms；一致性除预算扣减与分桶 A/B 强一致 (防超投) 外其他 eventual (CTR 统计允许秒级延迟、转化回流允许分钟级延迟)；可用性月度 99.99% 即 4 分钟 budget——广告系统每分钟 downtime 对应数十万美元直接收入损失；新鲜度新广告 5 分钟内可被召回、会话行为 10 秒内可影响下次请求。

**Out-of-scope (排除项)** 推荐系统的自然结果部分 (另开 id=90/198)、深入的广告创意自动生成 (**Generative AI** 部分另开 id=97)、跨端 user identity 打通 (privacy/IDFA 专题)、广告市场经济学的供需均衡建模、creator/广告主侧 growth。排除不是"忽略"而是主动声明——面试官问自然结果混排时我知道这超范围、可以明确"这是 ads-only 设计"。

**必问五问的本题答**：Q1 规模 QPS=100M、创意=1B、精排 invocations 20B/s；Q2 读写比 读远大于写——单请求 1000+ 候选 × 10+ feature lookup、特征查询 > 10B reads/s、曝光/点击写 < 500M/s；Q3 延迟 端到端 30ms 是整篇最硬的数字；Q4 一致性 预算扣减强一致、其他 eventual；Q5 地域 多 region active-active、跨 region 走异步归因，预算扣减只在主 region 做。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，30ms 延迟预算和强一致预算扣减是两个最硬的约束，任何建模选型都要反向追溯到"因为需求里说过……"。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个建模与基础设施决策找实在的瓶颈锚点——哪条路径是真有压力、数字背后绑着哪个技术拐点。我按请求扇出 → 特征层 → 事件总线 → 模型服务四条链路走一遍，每一段除了给数字还给出对应的选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### 精排调用链 (100M QPS × 200 candidates → 20B invocations/s)

请求峰值 100M QPS × 每请求精排 200 候选 → 精排 invocations 峰值 **20B/s**。这个数字把精排模型直接压进"必须 GPU + dynamic batching + model-parallel embedding"的硬件边界。

精排建模我选 **DLRM** (Deep Learning Recommendation Model, 深度学习推荐模型)，因为它稀疏 embedding + dense tower 的工业结构与 MLPerf 推荐基准对齐、支持 sparse/dense feature 交叉、Meta 广告线上万亿参数规模验证过、与 PyTorch/Triton 生态最成熟。候选一是 **DCN-v2** (Deep & Cross Network v2, 第二代深度交叉网络)——显式高阶特征交叉 block 表达力强、在 dense feature 为主的搜索广告 CTR 场景 (Google Ads) 已在用，但稀疏 embedding 端的分布式训练 benchmark 弱于 DLRM，DCN-v2 更合适的位置是 dense feature 占比 > 70% 的场景，所以不用。候选二是 **Wide & Deep**——Wide 端 cross-product 记忆 + Deep MLP 泛化的 Google Play 经典范式、可解释性好，但 Wide 端需要重度人工特征工程、与 sparse embedding 融合不如 DLRM 原生顺滑，淘汰；Wide & Deep 更合适的位置是 dense feature 中小规模场景。候选三是 **DIN** (Deep Interest Network, 深度兴趣网络) / **DIEN** (Deep Interest Evolution Network, 深度兴趣演化网络)——attention over user 行为序列建模长兴趣强，但 sparse tower 工业化弱于 DLRM，DIN 更合适的位置是 DLRM 之上叠加的 attention block 而非独立精排；保留作融合增强。候选四是 **DeepFM**——FM 显式二阶交叉 + DNN 高阶交叉、部署门槛低，但百亿参数以上 scale 受限、工业 benchmark 少于 DLRM，DeepFM 更合适的位置是中小规模 CTR baseline。切换触发：当用户历史序列成为主导信号时叠 DIN block；当 dense feature 占比 > 70% 时评估 DCN-v2；当团队规模小且参数量 < 10B 时直接用 DeepFM 省运维。

> **常见追问**:
> 1. "20B invocations 用多少卡？" —— A100 batch=64 单卡吞吐 ≈ 5K qps (dynamic batching + FP16)、约 4M A100 过多，实际做法是 embedding 表 sharded 到 data-parallel ranks + 前置 candidate selection 把 200 候选压到精排前 50、GPU 卡数降到 80K 量级 + 20% headroom。
> 2. "训练更新频率？" —— 增量训练分钟级 (online learning)、日级全量 + 灾备 checkpoint 回滚 < 10 分钟、小流量新模型用 shadow mode 跑 24h 再切主。
> 3. "DLRM 与 DIN 谁先上？" —— 单点 DLRM 打 CTR 基线 → 用户序列特征成熟后叠 DIN attention block；两者共存不冲突。

### Feature Store 分层 (10 TB hot + 50 TB/day cold)

在线热特征 1B users × 500 feats × 20B ≈ **10 TB**、每请求 500+ reads、p99 < 2ms；离线训练每日新增 **50 TB** (曝光 + 点击 + 转化 + 特征快照)、Spark/Flink 对齐 point-in-time。

Online 热层我选 **Redis Cluster 256 节点 + RocksDB 持久层**，因为 Redis 单节点 100K QPS 读、256 节点 25M reads/s 留 10× headroom、RocksDB 兜底重启雪崩、与 DLRM 在线推理的 embedding fetch 耦合成熟。候选一是 **DynamoDB**——托管省运维、multi-AZ 自动冗余，但 on-demand 单价 5-10× Redis 自建、500+ reads/req × 100M QPS 账单失控，DynamoDB 更合适的位置是中小流量或按量付费场景，所以不用。候选二是 **Memcached**——纯 KV 延迟更低、协议简单，但不持久化、重启全冷启 > 60 分钟、一致性哈希漂移导致连接抖动，Memcached 更合适的位置是完全无状态 page cache，淘汰。候选三是 **Cassandra**——LSM 写吞吐高、持久化稳健，但 p99 read 10-20ms 撞 2ms SLA、命中率低于 Redis，Cassandra 更合适的位置是 warm 层而非 hot 层。候选四是 **FoundationDB**——ACID 事务 + 高吞吐，但部署复杂度高、社区规模小于 Redis，FoundationDB 更合适的位置是强事务场景 (计费/预算) 而非 feature fetch。切换触发：流量再涨 2× 时扩到 512 节点；当成本比 > 40% 时评估 FoundationDB 承接 budget 扣减 + Redis 只做 read-heavy 特征。

> **常见追问**:
> 1. "Redis 重启 10TB 怎么办？" —— AOF everysec + RocksDB 同步写、重启从 RocksDB 预热、冷启 < 10 分钟；极端场景流量回源降级到只读 Cassandra 跑 50% 流量。
> 2. "热 key 怎么防？" —— 热门广告本地 Ristretto LRU cache、命中率 70%+ 后再去 Redis、热点 RPS 降 70%；SSD-backed L2 cache 兜底。
> 3. "online/offline 特征怎么对齐？" —— Iceberg snapshot + point-in-time join、训练 job 读 `@as_of_timestamp`、物理 key 是 request_id+user_id+ad_id+event_time。

### 事件总线 (1 GB/s → 80 TB/day)

事件流 100M QPS × 3 events/req (曝光/点击/conversion) × 500B ≈ **1 GB/s**、日 80 TB。

事件总线我选 **Kafka 512 partitions**，因为单 partition 20-30MB/s、512 partition 合计 > 10 GB/s 留 10× headroom、exactly-once 语义 + 消费组隔离让训练 sink 与实时分析互不干扰、与 Flink 流处理原生集成。候选一是 **Apache Pulsar**——多租户隔离好、Segmented storage 灵活、tiered storage 把冷数据下沉 S3，但运维复杂度高、社区生态规模仍弱于 Kafka，Pulsar 更合适的位置是需要强多租户隔离的 SaaS 场景，所以不用。候选二是 **AWS Kinesis**——托管省运维、与 Lambda 无缝整合，但单 shard 1MB/s 上限低、rescaling 手动、成本 3× Kafka 自建、跨云供应商锁定，Kinesis 更合适的位置是纯 AWS Lambda-only 栈，淘汰。候选三是 **RabbitMQ**——事务语义丰富、消息路由灵活，但吞吐上限约 200MB/s、远不够 10× headroom 要求，RabbitMQ 更合适的位置是事件扇出的 RPC-like 场景而非大规模流式摄入。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈 serverless 化时评估 Kinesis。

### Training Data 回流 (80 TB/day → 30 PB active training set)

每日新增 80 TB 曝光/点击/转化日志，3 个月活训练集约 30 PB、训练 job 每小时 scan top-500 feature column 约 2 TB。

训练数据底层我选 **S3 + Parquet + Iceberg**，因为 S3 单字节 $0.023/GB/月、Parquet 列存压缩比 5:1、Iceberg time-travel 让训练可复现任意历史快照、与 Spark/Flink/Presto 训练 pipeline 全兼容、scan 2TB/h 用 c5.12xlarge Spark cluster 50 节点 20 分钟跑完。候选一是 **HDFS**——适合批处理但 NameNode 单点运维重、云原生方向工具链逐渐转 S3，HDFS 更合适的位置是私有云强合规场景，所以不用。候选二是 **BigQuery**——按字节扫描计费、ad-hoc 分析快，但 PB 级训练 scan 账单快速上升、与 Spark 训练 pipeline 需 connector、与 DLRM PyTorch 训练栈隔离一层，BigQuery 更合适的位置是 ad-hoc 分析而非训练数据底层，淘汰。候选三是 **Delta Lake**——ACID 事务 + Schema evolution 完整，但需 Databricks/Spark 强绑定、跨团队工具链不如 Iceberg 中立，Delta Lake 更合适的位置是 Databricks 全家桶团队。切换触发：跨团队要强 ACID 写入时迁 Delta Lake；ad-hoc 分析成主场景时叠 BigQuery 做联邦查询。

这一节 takeaway：20B invocations 推出 DLRM + GPU 批推、10TB hot 推出 Redis Cluster 256 节点、1GB/s 事件流推出 Kafka 512p、30PB 训练集推出 S3+Iceberg——这四个数字把 §3 的建模服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按拍卖漏斗 + SLA + 一致性要求切、而不是按业务域切；数据怎么流——端到端 Retrieval → CTR Prediction → Auction → Logging 的 fan-out 结构要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：CTR 精排 20B invocations 的 GPU 层和 Auction 100M QPS 的 CPU 层不能共用线程池、Budget Pacing 的强一致预算扣减必须独立出来不能挂在任一推理服务内。

服务拆分策略我选 **按拍卖漏斗层 + SLA + 一致性切分**，因为 Retrieval 8ms (CPU ANN) / CTR 10ms (GPU 批推) / Auction 5ms (strongly-consistent budget) / Logging 2ms (fire-and-forget) 是四个独立 SLA + 两种一致性要求，每层允许独立扩缩容、独立 A/B 分流、独立模型热加载；把这四层塞一个 "Ads Service" 会出现任一层流量飙升把整个服务打崩的级联故障。候选一是按 **业务域切分** (User / Advertiser / Creative)——界面实体抄到后端，完全忽略 read/write + SLA 差异，热门广告 QPS 与历史转化 QPS 差 10×、放一起互相拖垮，淘汰。候选二是按 **数据管道切分** (Retrieval / Ranking 为一体, Feature / Embedding 为一体)——比业务域合理但把 Retrieval 和 CTR Ranking 打包成一块仍会让 ANN 查询与 GPU 推理耦合；数据管道切分更合适的位置是纯 ETL 系统而非在线广告服务。候选三是按 **客户端切分** (Web / Mobile / Native App) ——与本题无关，广告服务对客户端透明，淘汰。切换触发：当某层流量下降到与邻层差距 < 2× 时可合并；当出现新数量级 SLA 差异时再切一刀 (例如引入 LLM 创意生成后 p99 拉到 200ms 必须拆一层)。

> **常见追问**:
> 1. "Retrieval、CTR、Auction 可以共用一个模型吗？" —— 不行，Retrieval 追求 recall + 低延迟 (< 8ms) 走 ANN、CTR 追求 calibration + 特征交叉 (10ms 预算) 走 DLRM、Auction 是强一致预算扣减不是 ML 模型，目标与延迟不匹配。
> 2. "Budget Pacing 放哪个服务？" —— 独立强一致服务，被 CTR Ranking (出价微调) 与 Auction (预算硬截断) 共写、必须 Raft/Paxos 保证全局扣减不超投，绝不能塞进任一推理服务。
> 3. "Experiment Service 算独立服务吗？" —— 算，A/B 分桶需要强一致性、与推理完全不同 SLA (读 < 0.5ms 写 < 5ms)，放独立服务便于收入归因与审计。

端到端数据流：用户请求进 Gateway → 查 Experiment Service 决定本次 A/B 桶 → Ad Retrieval 多路召回 (Two-Tower ANN + Content-based + 倒排 tag + Trending) 并集 1000 候选 → Coarse Ranker 粗排到 500 → Fine Ranker 精排到 50 并产出 CTR/CVR 预测 → Auction 用 eCPM 排序、查 Budget Service 做预算检查、GSP 定价 → 选 top-k slot → 返回 20 给用户；同时曝光事件通过 Kafka 流回 Feature Store 做准实时特征更新、训练事件批落 S3 供离线训练、Budget Service 扣减本次曝光对应的预计花费。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——ANN 挂了走 content-based 倒排、精排挂了走粗排分、Auction Budget Service 挂了走本地缓存估算 + 容忍 5% 超投 + 事后对账、完整链路允许 2 层同时降级仍返回可用广告。

这一节 takeaway：广告系统的服务边界不是业务边界而是建模层 + SLA + 一致性边界；任一层必须自带 fallback，Budget Pacing 的强一致性是整条链路最大的耦合点。

## 4. Deep Dives

这一节把广告核心四块 (Retrieval / CTR Prediction & Calibration / Auction / Budget & Exploration) 逐一展开，每一块给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"广告系统每层选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章编排顺序与在线 serving 数据流一致：Retrieval 在前、CTR 在中、Auction 在后、Budget 与探索贯穿全程。

### 4a. Ad Retrieval (候选召回)

Ad Retrieval 的本质是在 1B creatives 里快速圈出 1000 候选、追求 recall@1000 ≥ 0.98、延迟 p99 < 8ms。广告库动态性远大于推荐 (平均广告生命周期 < 7 天、新广告 5 分钟内要可召回)，所以召回路径必须实时可增量更新。

主召回我选 **Two-Tower Model** (双塔模型)，因为它用户塔与广告塔完全解耦、广告侧 embedding 可离线批量预计算 + 在线增量更新、在线只做用户塔推理 + ANN 查询、平均 RT 3-5ms、与 HNSW 工具链完美对齐、Meta/Google 广告均有线上 paper 背书。候选一是 **Cross-Encoder (BERT-style)**——用户与广告同 Transformer 共编码、精度高 5-10% 但延迟炸到 50ms、无法预计算广告 embedding、1000 候选跑不完，Cross-Encoder 更合适的位置是精排而非召回，淘汰。候选二是 **Content-based Retrieval**——广告创意文本/图片 embedding + 用户兴趣标签匹配、冷启广告友好 (无需历史点击)，但对热门广告召回率不如 Two-Tower，Content-based 更合适的位置是 Two-Tower 的补充召回路径；保留。候选三是 **Inverted Index on tags (倒排标签召回)**——按广告主设定的类目/关键词倒排、精确匹配可控性强，但表达力弱、长尾 query 覆盖差，倒排召回更合适的位置是业务硬约束场景 (如广告主定向城市/性别) 的过滤层。候选四是 **GNN** (Graph Neural Network, 图神经网络)——图结构信号丰富、长尾广告召回强，但训练 + 部署基础设施复杂、单次迭代 > 8 小时、运维工具链不成熟，GNN 更合适的位置是 Two-Tower 成熟后的"召回增强"而非主路。切换触发：当长尾广告召回率 < 0.5 时叠 GNN；当冷启广告占比 > 30% 时补 Content-based 独立召回路。

ANN 索引底层我选 **HNSW (hnswlib 实现) sharded 32 份**，因为它图结构检索 QPS 最高、支持 online insert (新广告 5 分钟入索引)、recall@1000 ≈ 0.95 稳定、单 shard 20GB 可在 128GB 机型留 2× 工作内存。候选一是 **FAISS IVF-PQ**——倒排 + 乘积量化、内存只用 HNSW 的 1/4、适合 B 级物品库，但量化损 recall 到 0.85、静态索引 rebuild 开销大不利于广告 5 分钟新鲜度要求，IVF-PQ 更合适的位置是 B 级物品 + 离线召回，所以不用。候选二是 **ScaNN** (Google)——各向异性量化精度最好、Google 线上验证过，但与 K8s 部署工具链整合成本高、Python-only 工具链成熟度差，淘汰；ScaNN 更合适的位置是 GCP Vertex AI 原生栈。候选三是 **Milvus**——分布式向量数据库、K8s-native 部署，但延迟比 hnswlib 原生库多 5-10ms 一跳、QPS 头部案例少于自建 HNSW；Milvus 更合适的位置是多租户 SaaS 场景。切换触发：广告库升到 10B 级时迁 IVF-PQ；多业务共用向量基础设施时评估 Milvus。

> **常见追问**:
> 1. "新广告 5 分钟入索引怎么做？" —— Two-Tower 广告塔在广告创建时离线出 embedding、写入 HNSW 增量 insert (单批 < 1% M 值)、日级全量 rebuild 兜底图质量。
> 2. "广告主定向条件 (城市/年龄/性别) 怎么融？" —— 在 ANN 结果上套 tag-filter 过滤层、或直接用带 filter 的 ANN (HNSW-filtered / Milvus with metadata filter)。
> 3. "冷启广告怎么保召回？" —— Content-based 独立召回路 + 倒排硬量保底；前 24h 不依赖历史 CTR。

### 4b. CTR Prediction & Calibration (CTR/CVR 建模与校准)

CTR/CVR 精排的任务是在 500 候选里做精准概率预测、延迟 p99 < 10ms、关键是特征交叉、校准准确性、以及 position bias 去偏。CTR 模型经历了五代演进：LR → GBDT+LR → Wide & Deep → DCN-v2/DLRM → DIN/DIEN/MMoE，核心线索是特征交互从手工到自动、再到注意力序列建模。

精排建模 (§2 已给 DLRM 的部署选型，此处补建模层多目标融合与 position bias 去偏的完整链) CTR 概率估计公式 $P(\text{click}|\text{user, ad, context})$ 后再用 $\text{eCPM} = \text{CTR} \times \text{bid} \times 1000$ 作为排序信号；**effective Cost Per Mille** (eCPM, 有效千次展示成本) 同时考虑相关性 (CTR 反映用户兴趣) 与商业价值 (bid 反映广告主意愿)。多目标融合我选 **学习式 fusion head (learned-fusion MLP)**，因为 DLRM 输出 [CTR, CVR, quality_score, dwell_time] 四个 logit 下游接 2-layer MLP 学加权更稳、权重随业务指标可再训练。候选一是 **线性加权 (Hand-tuned weighted sum)** $\text{score} = w_1 \cdot \hat{CTR} + w_2 \cdot \hat{CVR} + w_3 \cdot \hat{quality}$——可解释性强、冷启易调，但权重漂移需手动调参；hand-tuned 更合适的位置是 MVP 阶段、learned-fusion 的基线。候选二是 **Multi-gate Mixture of Experts** (MMoE, 多门混合专家)——每个 target 独立 gate 减少负迁移，但训练稳定性不如 learned-fusion、调参门槛高，MMoE 更合适的位置是目标 > 3 且 reward hacking 明显时的下一阶段升级，淘汰。候选三是 **Reinforcement Learning based fusion** (RL 融合)——直接优化长期 reward、理论最优，但线上样本效率低、policy 稳定性差、off-policy evaluation 门槛高，RL 更合适的位置是 learned-fusion 线上跑通且团队有 RL infra 后的升级阶段。切换触发：目标数升至 4+ 且 reward hacking 明显时升 MMoE；长期 LTV 指标成为核心 SLO 时迁 RL。

校准策略我选 **Isotonic Regression (保序回归)**，因为它是非参数化、不对分布做假设、直接学习预测→真实概率的单调映射函数、训练只需几分钟、与 DLRM 在线推理解耦易灰度。候选一是 **Platt Scaling (普拉特缩放)**——在预测 logit 上再套一层 sigmoid 学 $P_{\text{cal}} = \sigma(a \cdot \hat{p} + b)$、参数只有 2 个、训练极快，但假设单一 sigmoid 形状、校准曲线呈 S-curve 时拟合不够灵活，Platt 更合适的位置是数据量极少 (< 10K 样本) 的冷启或 A/B 评估场景，所以不用。候选二是 **Conformal Prediction**——不仅校准、还给预测区间 + 理论 coverage 保证，但在线推理开销高、工业广告 serving 很少需要 confidence interval，Conformal 更合适的位置是医疗/金融决策场景，淘汰。候选三是 **Temperature Scaling**——在 logit 前乘一个温度系数 $T$，单参数、训练最快，但只适用于多分类 softmax、二分类 CTR 场景退化为 Platt 的一个参数版本，Temperature 更合适的位置是多分类蒸馏或知识迁移场景。切换触发：数据量 > 10M 时用 Isotonic；数据量 < 100K 或 A/B 快速评估时退 Platt。

Position bias 去偏我选 **Position-aware Learning** (PAL 做法, Huawei/Alibaba 广告在用)，因为训练时把 position 作为独立 bias feature 输入 + inference 时置零 position feature、与主模型解耦、实现简单不破坏 DLRM 结构。候选一是 **Inverse Propensity Scoring** (IPS, 逆倾向性加权)——用历史 position 概率 $\pi(p)$ 逆向加权训练样本，理论严格但 propensity 估计噪声大、长尾 position 方差爆炸，IPS 更合适的位置是有精确 position 分布的搜索广告而非信息流，所以不用。候选二是 **Causal Uplift Modeling**——训练 uplift tree / causal forest 直接建模 treatment effect，但训练复杂度高 + 样本需求大，Causal 更合适的位置是广告主归因 (marketing mix modeling) 而非 CTR 去偏，淘汰。候选三是 **Counterfactual Learning from Logged Bandit Feedback**——用 doubly robust estimator 做离线评估 + 训练，但需要详细的 propensity logging 与 bandit policy 记录，复杂度高、implementations 成熟度低，Counterfactual 更合适的位置是研究阶段而非工业标配。切换触发：线上 position bias 漂移明显 (A/B 跨位置 CTR 差距大) 时评估 IPS；有完整 bandit logging infra 后可迁 Counterfactual。

> **常见追问**:
> 1. "AUC 高但 calibration 差会怎样？" —— 广告定价错误，高估 CTR 广告主过度支付、低估 CTR 平台收入损失；校准比 $\text{Calibration} = \frac{\text{Predicted avg CTR}}{\text{Observed avg CTR}}$ 必须严格 ≈ 1.0。
> 2. "延迟转化 (Delayed Conversion) 怎么办？" —— 转化事件 T+1 到 T+30 天才到达，训练用 importance weighting + 负样本重标，或直接建模 delay distribution (TTL-based re-weighting)。
> 3. "模型刷新频率？" —— 增量训练分钟级 (online learning)、日级全量、周级大改灰度。

### 4c. Auction & Bidding (拍卖机制)

拍卖是广告系统的经济学核心，决定了广告主激励结构与平台收入的 tradeoff。拍卖机制与 CTR 模型的耦合点是"用哪个出价信号排序、怎么定价"，因此拍卖设计不是独立模块而是与 CTR/CVR 预测联动的决策链。

拍卖机制我选 **Generalized Second-price Auction (GSP, 广义第二价格拍卖)**，因为它在单 slot 退化为 Vickrey 第二价格拍卖、诚实出价近似最优、工业工具链最成熟、与 eCPM 排序天然兼容；支付公式 $\text{payment} = \frac{\text{eCPM}_{\text{2nd}}}{\text{CTR}_{\text{winner}}}$ 把"按相关性 + 支付意愿"双重信号耦合进 **Cost Per Click** (CPC, 每次点击成本)。候选一是 **First-price auction (第一价格拍卖)**——胜出者支付自己出价、收入更可预测 (广告主必须谨慎出价而不做 shading 博弈)，Google Ad Manager 2019 年切换到 First-price 就是出于这个动机；但诚实出价不是占优策略、广告主需要复杂的 bid-shading 算法 (**Bid Shading** 模型预测最优出价)，First-price 更合适的位置是 header bidding 多 SSP 竞价的透明环境，保留作备选。候选二是 **Vickrey-Clarke-Groves Auction** (VCG 拍卖)——多 slot 场景下严格激励相容、理论最优，但支付计算复杂度 O(n²)、广告主难以理解报价策略，VCG 更合适的位置是学术设定或少量 slot 的高端 premium 拍卖，淘汰。候选三是 **Myerson Optimal Auction**——从平台收入最大化推导出的最优 reserve price + 排序规则，但需要广告主 value 分布先验估计、实操参数化困难，Myerson 更合适的位置是小市场单品拍卖而非广告这种海量 creatives 场景。切换触发：当 header bidding 透明度成为核心诉求时迁 First-price + Bid Shading；当平台有可靠 value 分布估计时做 Myerson reserve price。

Reserve price 设定我选 **Dynamic Reserve based on historical floor CTR**，因为按每个广告 slot 的历史成交价分位数动态设置保底价、平衡收入与填充率、A/B 可渐进调整。候选一是 **Fixed Reserve Price**——简单易懂，但无法响应需求弹性、高景气时机会成本大、低景气时广告主流失，Fixed 更合适的位置是冷启期前两个月的 MVP。候选二是 **Personalized Reserve (按用户价值分层)**——高价值用户高保底、低价值用户低保底，但需要精确的 user LTV 估计、容易引起公平性质疑，Personalized 更合适的位置是高端 premium 广告场景，淘汰。候选三是 **No Reserve (零保底)**——最大填充率，但平台收入下限不可控、劣质广告涌入，No Reserve 更合适的位置是填充率优先的流量变现早期场景。切换触发：收入 vs 填充率矩阵出现显著弹性拐点时迁 Dynamic；启动期 < 3 个月用 Fixed 省运维。

> **常见追问**:
> 1. "GSP 与 VCG 谁更赚？" —— 理论上 VCG 在对抗性均衡下收入略低于 GSP，实务上 GSP 占优因为广告主行为更趋近诚实出价；GAFA 除 FB Audience Network 试过 VCG 之外大多仍 GSP。
> 2. "Bid Shading 怎么做？" —— 用 LightGBM 训练 $\hat{p}(\text{win}|\text{bid})$ 预测赢率、再优化 $\text{bid}^* = \arg\max_b \hat{p}(\text{win}|b) \cdot (\text{value} - b)$；Amazon/Xandr 有公开 paper。
> 3. "Click fraud / invalid traffic 怎么过？" —— 独立 Anti-Fraud 服务过滤 bot 流量、异常 click pattern 去重、结算前二次审计；不放进拍卖链路。

### 4d. Budget Pacing & Exploration (预算调控与冷启探索)

Budget Pacing 与 Exploration 的目标分别是"避免广告主预算提前花完" 与 "让新广告/新创意获得足够曝光学习"，两者共享同一条基础设施 (探索预算/pacing 系数都以 multiplier 形式注入出价)。

预算调控 **Budget Pacing (预算调控)** 策略我选 **PID Control (比例-积分-微分控制)**，因为 PID 对预算消耗速度与目标差形成闭环反馈、抗突发流量扰动强、参数 $K_p, K_i, K_d$ 可按广告主调整、与 $\text{pacing\_multiplier} = \frac{\text{remaining\_budget}}{\text{ideal\_remaining\_budget}}$ 这个核心公式天然契合。候选一是 **Linear Pacing (线性分摊)**——把预算按 24h 等分、每小时固定花费上限，但对突发流量抵抗力差、高景气时段预算分配不足、Linear 更合适的位置是预算极小的新手广告主 MVP，所以不用。候选二是 **Model Predictive Control (MPC)**——用历史流量预测 + 滚动优化窗口提前规划消耗曲线，但训练 + 预测复杂度高、对流量预测误差敏感，MPC 更合适的位置是预算 > $10K/day 的头部广告主且有成熟流量预测模型的场景。候选三是 **Dual-based Bid Shading**——从 LP 对偶推出最优 pacing multiplier，理论最优但需要全局 LP 求解、计算开销大、实时性差，Dual 更合适的位置是小时级 batch pacing 而非 sub-second 实时，淘汰。切换触发：广告主量级 > 10K/day 且有流量预测 infra 时迁 MPC；头部超大广告主 (Walmart/Amazon scale) 评估 Dual-based。

探索策略我选 **Thompson Sampling (汤普森采样)**，因为它 Bayesian 后验采样自然平衡探索与利用、收敛快、参数只需 prior 分布、对广告冷启场景 (新创意/新广告主) 在线可直接 incremental 更新。候选一是 **ε-Greedy**——以 ε 概率随机探索、1-ε 选当前最优、实现极简，但固定 ε 无法自适应、冷启期探索不够、稳定期探索浪费，ε-Greedy 更合适的位置是预算固定且不需要精细归因的探索场景。候选二是 **Upper Confidence Bound (UCB)**——按 $\hat{\mu}_a + c\sqrt{\ln t / N_a}$ 选臂、确定性策略方便调试，但 UCB 需要精确奖励分布 + reward scale 假设、广告 reward 稀疏 (点击率 ~1-5%) 时收敛慢，UCB 更合适的位置是 A/B 分桶这种 reward 密集场景，淘汰。候选三是 **Linear UCB / Contextual Bandits**——把 user/ad context 作为特征线性预测 reward + UCB bound，适合 contextual arm、但冷启时特征稀疏、线性假设限制表达，LinUCB 更合适的位置是 context 丰富且线性建模够用的搜索广告场景。切换触发：冷启量 < 5% 时退 ε-Greedy 省运维；context 信号强且需要精细归因时迁 LinUCB。

> **常见追问**:
> 1. "PID 系数怎么调？" —— $K_p$ 先单独上线、观察超调量 < 10% 再加 $K_i$ 消除稳态误差、$K_d$ 只在流量抖动大时加；广告主类别分组共享系数。
> 2. "转化归因 (Attribution) 怎么设计？" —— **Data-driven Attribution** (基于 Shapley Value / ML 模型) 是默认做法，备选 **Last-click (末次点击)** 简单但忽略上游触点、**First-click (首次点击)** 忽略下游、**Linear (线性归因)** 均分不区分重要性；做 **Multi-Touch Attribution (MTA)** 要联动用户跨设备打通。
> 3. "Creative Optimization (广告创意优化) 怎么做？" —— **Multi-Armed Bandit (多臂老虎机)** 对标题/图片/CTA 多组合动态分流、Thompson Sampling 跑满前期探索、后期收敛到最优组合；大规模组合探索需降维聚类压缩臂数。

这一节 takeaway：广告系统不是一个模型、而是四块 (Retrieval/CTR/Auction/Budget) 算法候选池的组合；每块默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

广告系统的可靠性不是"整条链路 100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量 + 不超投预算"的分层容错。广告与推荐的关键差异在于 Budget Service 的强一致性——预算超投直接对应广告主财务损失 + 法律风险。

监控策略我选 **四象限监控 + 分层 SLO**，因为系统/模型/业务/实验四个维度要分开看、分层 SLO 让降级决策可编程。系统层对接 **Prometheus + Grafana** 采集 p99 延迟、error rate、资源利用率；模型层引入 **Evidently** 或 **Arize** 采集 CTR/CVR 预测分布漂移、特征 null rate、embedding 退化 (cos sim 飘离基线 > 0.1)、校准比 drift；业务层接入内部 BI 看 session eCPM、填充率、广告主 ROI、平台收入；实验层采集分桶平衡、**Sample Ratio Mismatch** (SRM)、novelty effect。候选一是 **Datadog 单栈统一中台**——工具链简化但跨维度语义损失、模型漂移细节看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize 独立 ML 监控平台**——ML 专用指标全、SHAP 解释内嵌，但与系统监控割裂、告警链路双头，Arize 更合适的位置是模型 ops 团队独立于平台团队时，淘汰。候选三是 **Fiddler 独立 ML 监控平台**——可解释性专精、公平性审计完整，但与开源 Prometheus 生态整合成本高、许可证费用贵，Fiddler 更合适的位置是强合规场景 (金融/医疗)。候选四是 **自建 full-stack 监控**——灵活度最高但研发成本巨大，自建更合适的位置是 FAANG 规模深度定制。切换触发：模型漂移成为核心故障源时补 Arize；团队规模 > 100 MLE 时考虑自建核心监控栈。

降级预案：CTR 精排挂了 fallback 到粗排分；粗排挂了 fallback 到 Retrieval 分 + 热度分；Auction Budget Service 挂了走本地缓存估算 + 容忍 5% 超投 + 事后对账；特征缺失用 per-feature default (如 7 天滑动均值) 兜底；ANN 索引挂了 fallback 到 content-based / 倒排。隐私合规方面，**General Data Protection Regulation** (GDPR, 通用数据保护条例) 与 **California Consumer Privacy Act** (CCPA, 加州消费者隐私法) 要求数据脱敏与用户 opt-out；**Privacy Sandbox** 推动 **Federated Learning** (联邦学习) 与 **Differential Privacy** (差分隐私) 在保持广告效果的同时保护个体数据；**On-device Learning** (端上学习) 在用户设备做个性化推理、避免个人数据传输到服务器，是后 Cookie 时代的主路径。每条 fallback 路径必须独立演练、月度 game day 强制跑一次、超投事故 PIR 48h 内出。

这一节 takeaway：reliability 不在单点高可用而在分层可降级 + Budget 强一致；四象限监控 + 每层独立 fallback + 隐私合规三者缺一不可。

## 6. Summary & Tradeoffs

本题核心 takeaway 是广告系统的三方博弈思维：用户体验、广告主 ROI、平台收入必须在 30ms 拍卖窗口里同时被 ML 预测与经济学机制平衡。Retrieval 默认 Two-Tower + HNSW、CTR 精排默认 DLRM + Isotonic 校准、Auction 默认 GSP、Budget Pacing 默认 PID、探索默认 Thompson。模型演进链条 LR → GBDT → Wide & Deep → DCN-v2/DLRM → DIN/DIEN/MMoE；拍卖演进链条 GSP → First-price + Bid Shading → VCG/Myerson。

三个最常被错答的 tradeoff：一是"AUC 高还是 Calibration 好更重要"——两者都重要但 calibration 错会直接把广告主的钱算错，AUC 高但 calibration 差会让平台收入扭曲；二是"Second-price 还是 First-price"——不是谁更好，而是透明度与收入可预测性的 tradeoff，header bidding 场景 First-price 更合适；三是"Budget Pacing 强一致还是最终一致"——强一致是硬约束，超投就是直接财务损失，不能为性能妥协，必须独立高可用服务 + 本地缓存 + 事后对账组合解决。长期优化依赖**数据飞轮**：点击反馈训练更好 CTR 模型→更精准竞价→更高 eCPM→吸引更多广告主→更多数据反哺模型；同时警惕"劣币驱逐良币"的拍卖失衡 (短期高出价劣质广告吞掉曝光) 与隐私监管风险。

工程 vs 建模的决策拉锯主要在三处：一是 feature store 在 Redis 与 DynamoDB 之间取舍——小团队 DynamoDB 运维省、大流量 Redis 吞吐稳；二是 ANN 索引在 HNSW 与 IVF-PQ 之间取舍——精度优先 HNSW、成本优先 IVF-PQ；三是拍卖在 GSP 与 First-price 之间取舍——广告主行为可控 GSP、header bidding 透明度 First-price。选型的真正判据不是"谁更先进"，而是"当前业务的 QPS、广告主量级、隐私合规强度、渠道透明度诉求落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："你这套系统上线后短期 CTR 涨了但 advertiser ROI 跌了，怎么办？"——这是典型短期指标胜长期指标失败。答案思路：一是排查 CTR 模型是否优化偏狭 (只对 click 而无 post-click conversion 信号)、是否需要切 ESMM (Entire Space Multi-task Model) 多目标融合；二是 Calibration 是否漂移、导致 bid 溢价；三是 Attribution 链路 (last-click vs data-driven) 是否导致广告主误判转化源；四是业务侧把 advertiser ROI 作为核心 SLO 而非 CTR 单指标。

第二题："如何保证新广告 (创建后 < 24h) 的冷启曝光？"——长尾与新广告曝光是广告生态的核心课题。答案思路：一是 Retrieval 侧 Content-based 独立召回路避免 Two-Tower 历史 bias；二是 CTR 侧用广告主历史 CTR / 类目 CTR 做 prior 平滑、避免冷启 $\hat{p}$ 方差爆炸；三是 Auction 侧 Thompson Sampling 探索预算 + reserve price 保底；四是评估 **Coverage** (覆盖率) 与新广告 D1 曝光率作为生态指标。

第三题："在 Post-Cookie 时代 (IDFA 受限、Safari 默认 ITP) 如何保持 CTR 模型精度？"——这是广告行业结构性问题。答案思路：一是 **Federated Learning** 把用户行为特征保留在端上、只传梯度；二是 **Differential Privacy** 在训练梯度添加噪声保证个体隐私；三是 **On-device Learning** 本地小模型 + 云端大模型二阶段推理；四是 Contextual signal (页面内容、时间、地域) 替代个体 ID 驱动的信号；五是第一方数据 (用户在平台内行为) 优先于第三方 tracking。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) 30ms 端到端延迟分配到 Retrieval/CTR/Auction/Logging 四段的预算分摊；(2) 每层默认模型与它的 3 个候选 + why-not；(3) Second-price (GSP) / First-price / VCG 三种拍卖的激励相容性与收入可预测性对比；(4) AUC vs Calibration 的 tradeoff 与 Isotonic/Platt/Temperature 三种校准方法的切换条件；(5) eCPM = CTR × bid × 1000 公式的经济学含义 + Calibration 误差对计费的传导路径；(6) Budget Pacing PID 与 Linear / MPC / Dual-based 的切换条件；(7) Thompson Sampling vs ε-Greedy vs LinUCB 的冷启场景适用边界；(8) Post-Cookie 时代 Federated Learning / Differential Privacy / On-device 三条隐私合规路径的 tradeoff。八个都能答对就可以去白板了。
