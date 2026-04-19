# Recommendation Systems (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个推荐系统"——信息流、商品、内容发现、短视频、音乐、新闻、电商首页都能套。与 id=198 Real-Time Recommendation 不同，本题的重心不是"把一个完整 end-to-end 系统的服务拆分全讲一遍"，而是"把推荐系统的通用建模范式与选型脉络讲透"：多阶段漏斗为什么是召回/粗排/精排/重排四段、每一段的算法选型有哪些主流候选、候选之间的 why-not 是什么、什么时候应该切换。简言之 id=198 回答"怎么把这套系统在 100M DAU 下部署"，id=90 回答"推荐系统每一层有哪些可选的建模工具、各自的适用边界在哪里"。本题考点不是"跑一个 DCN"，而是"能不能把 Two-Tower / FAISS / DLRM / MMR / Thompson 这些工具在同一条时间轴上摆清楚并给出可落地的切换触发条件"。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=198 Real-Time Recommendation System](/kg?node=n198)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问这五元组) 是本题所有 deep dive 的评分标尺。再读 id=198 的理由是：那篇把"100M DAU + 70K QPS + 350K ranking invocations/s"的部署细节讲过一遍，本题在 §2 给出容量时不重复推导细节，而是直接引用 id=198 的数字并聚焦建模层的选型差异。本题的读者对 **Approximate Nearest Neighbor** (ANN, 近似最近邻) 内积/余弦、**Hierarchical Navigable Small World** (HNSW, 分层可导航小世界图)、**Inverted File with Product Quantization** (IVF-PQ, 倒排文件+乘积量化)、**Click-Through Rate** (CTR, 点击率) 与 **Conversion Rate** (CVR, 转化率) 都应有基础认识，否则容易在精排模型对比环节卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把用户想要的功能抄一遍"，而是要把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一问的答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈落在召回扇出与精排 GPU 推理、强一致只出现在 A/B 分桶与计费归因一瞬、跨 region 只做异步容灾不做同步推理"。

**Functional requirements (功能需求)** 主流程是用户请求推荐→召回→粗排→精排→重排→返回物品列表；辅流程包括曝光/点击/停留/转化事件上报、实时行为回流、新物品入库、用户兴趣补全问卷、作者物料审核过料。平台级功能含多目标融合 (点击 + 停留 + 转化 + 长期留存)、多样性约束、冷启动硬配额 slot、广告与自然结果混排接口。这些功能归成三组——召回、排序、反馈——后面 deep dive 按这三组的建模选型走。

**Non-functional requirements (非功能需求)** 规模取 **Daily Active Users** (DAU, 日活用户) 100M、人均 2 session × 10 request/day、物品库 500M、召回扇出 500、峰值请求 **Queries Per Second** (QPS, 每秒查询数) 70K、精排调用 350K invocations/s；延迟端到端 p99 < 200ms 分摊到召回 30ms + 粗排 20ms + 精排 100ms + 重排 20ms + 序列化 30ms；特征查询 p99 < 5ms；一致性除 A/B 分桶与计费归因强一致外其他全 eventual (CTR 统计允许秒级延迟、行为回流允许分钟级延迟)；可用性月度 99.9% 约 43 分钟 budget；新鲜度新物品 10 分钟内可召回、会话行为 1 分钟内可影响下次请求。

**Out-of-scope (排除项)** 广告拍卖细节 (另开 id=91 Ads & Click Prediction)、深入的内容审核流 (CSAM/暴力过滤)、作者 creator growth、跨端 session 同步、多模态 CLIP-style 预训练。排除不是"忽略"而是主动声明——面试官问广告细节时我知道这超范围、可以明确"这是拍卖 + 排序的组合题、本篇不深挖"。

**必问五问的本题答**：Q1 规模 DAU=100M、物品 500M、精排调用 350K/s；Q2 读写比 读远大于写——单请求 500+ 模型推理、特征查询 > 700K reads/s、点击/曝光写 < 300K/s；Q3 延迟 端到端 200ms 是整篇最硬的数字；Q4 一致性 分桶强一致、其他 eventual；Q5 地域 单 region 多 **Availability Zone** (AZ, 可用区)、跨 region 只做 feature store 异步复制做灾备。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，任何选型都能反向追溯到"因为需求里说过……"——这是 L5 与 L4 的分水岭。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个建模决策找实在的瓶颈锚点——哪条路径是真有压力、哪条是虚的、数字背后绑着哪个建模拐点。我按请求扇出 → 向量索引 → 特征层 → 事件总线四条链路走一遍，每一段除了给数字还给出对应的建模选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### 召回扇出链 (70K req/s → 350K ranker invocations/s)

请求峰值 70K QPS × 每请求召回 500 候选 → 粗排 1000 次 → 精排 300 次，精排调用峰值 **350K invocations/s**。这个数字把精排模型直接压进"必须 GPU + dynamic batching"的硬件边界。

精排建模我选 **Deep Learning Recommendation Model** (DLRM, 深度学习推荐模型)，因为它在稀疏 embedding + dense tower 的工业结构下与 MLPerf 推荐基准对齐、支持 sparse/dense feature 交叉、Meta 线上 100+ 模型规模验证过、与 TF-Serving / NVIDIA Merlin 生态最成熟。候选一是 **Deep & Cross Network v2** (DCN-v2, 第二代深度交叉网络)——显式高阶特征交叉 block 表达能力强、但稀疏 embedding 端的分布式训练 benchmark 弱于 DLRM，DCN-v2 更合适的位置是以 dense feature 为主的场景 (CTR 型搜索广告已在用)，所以不用。候选二是 **XGBoost**——梯度提升树训练快、解释性强、在百万样本以下冷启基线无人能敌，但 O(100B) 样本 + 高维 embedding 特征用不起来、GPU 加速受限、不用；XGBoost 更合适的位置是精排之后的 calibrator 或 rule-based filter 分支。候选三是 **Multi-Gate Mixture of Experts** (MMoE, 多门混合专家)——专为多目标设计、每个 target 独立 gate，但训练稳定性不如 DLRM、调参门槛高，淘汰；MMoE 更合适的位置是 DLRM 跑通之后的"多目标升级版"——先 DLRM 打单点击目标基线，业务接入停留/转化后再迁 MMoE。切换触发：当同时建模 3+ 目标且单目标模型融合后仍看得到 reward hacking 时迁 MMoE；当稀疏特征减少、dense feature 成主场景时迁 DCN-v2。

> **常见追问**:
> 1. "DLRM 与 DIN 谁先上？" —— DIN 的 attention 对用户行为序列建模强、但 sparse tower 不如 DLRM 工业化，两者可叠加 (DLRM + DIN attention block)，单点基线先 DLRM。
> 2. "350K invocations 用多少卡？" —— A100 batch=32 单卡吞吐 ≈ 1K qps，400 卡 + 20% 冗余足够覆盖峰值。
> 3. "训练更新频率？" —— 小时级增量训练 + 日级全量、增量 checkpoint 回滚 < 10 分钟。

### 向量索引层 (500M items × 128d = 256 GB embedding)

物品侧 500M × 128 × 4B = **256 GB** embedding、单机内存吃紧；用户侧 100M × 128 × 4B = 51 GB。这个 256GB 把 ANN 选型直接压到"必须分片"。

ANN 索引我选 **HNSW (hnswlib 实现) sharded 32 份**，因为它图结构检索 QPS 最高、支持 online insert (新物品 10 分钟入索引)、recall@100 ≈ 0.95 稳定、单 shard 8GB 可在 64GB 机型留 2× 工作内存。候选一是 **FAISS IVF-PQ**——倒排 + 乘积量化、内存只用 HNSW 的 1/4、适合 B 级物品库，但量化损 recall 到 0.85、静态索引 rebuild 开销大不利于实时入库，IVF-PQ 更合适的位置是 B 级物品 + 离线召回 (Pinterest 图像 feed)，所以不用。候选二是 **ScaNN** (Google)——各向异性量化精度最好、Google 线上验证过，但与 Kubernetes 部署工具链整合成本高、Python-only 友好度差，淘汰；ScaNN 更合适的位置是 GCP Vertex AI 原生栈。候选三是 **Milvus**——分布式向量数据库、K8s-native 部署、支持多租户，但延迟比 hnswlib 原生库多一跳 5-10ms、运维重、QPS 头部案例远少于自建 HNSW；Milvus 更合适的位置是多租户 SaaS 场景而非单业务高 QPS。候选四是 **Pinecone**——SaaS 向量库运维 0 成本，但按 QPS + 存储双计费、100M DAU 账单不可控、私有化限制多，Pinecone 更合适的位置是 < 1K QPS 早期阶段。切换触发：物品库升到 B 级时迁 IVF-PQ；多业务共用向量基础设施时评估 Milvus；早期 MVP 阶段可直接 Pinecone 起步。

> **常见追问**:
> 1. "HNSW 增量 insert 会不会让图退化？" —— 单批 < 1% M 值时图质量几乎不变、日级全量 rebuild 兜底。
> 2. "32 shards 路由？" —— 按 item_id hash 均匀分片、query fan-out 32 后 merge top-K。
> 3. "向量召回之外还有哪些召回路径？" —— **Collaborative Filtering** (协同过滤)、倒排 tag 召回、热门 trending 召回、社交关注召回，多路并集送粗排。

### Feature Store 分层 (1 TB hot + 5 TB/day cold)

在线热特征 100M users × 200 feats × 50B ≈ **1 TB**、每请求 100+ 读、p99 < 5ms；离线训练每日新增 **5 TB**、Spark/Flink 对齐 point-in-time。

Online 热层我选 **Redis Cluster 32 节点 + RocksDB 持久层**，因为 Redis 单节点 100K QPS 读、32 节点 700K reads/s 留 4× headroom、RocksDB 兜底重启雪崩。候选一是 **DynamoDB**——托管省运维，但 on-demand 单价 5-10× Redis 自建、100+ reads/req 账单失控，DynamoDB 更合适的位置是 QPS 波动大的小流量业务，所以不用。候选二是 **Memcached**——纯 KV 延迟更低，但不持久化、重启全冷启 30 分钟、一致性哈希漂移断连接，Memcached 更合适的位置是完全无状态的 page cache，淘汰。候选三是 **Cassandra**——LSM 写吞吐高、持久化稳健，但 p99 read 10-20ms 撞 5ms SLA、命中率低于 Redis，Cassandra 更合适的位置是 warm 层而非 hot 层。候选四是 **Feast + RocksDB**——开源 feature store、与 ML pipeline 集成好，但吞吐上限低于 Redis Cluster、SLA 响应在高 QPS 下不稳；Feast 更合适的位置是团队规模小 + 想要开源一体化的中流量场景。切换触发：流量再涨 2× 时扩到 64 节点；当成本比 > 30% 时评估 Feast + RocksDB 的自管方案。

> **常见追问**:
> 1. "Redis 重启 1TB 怎么办？" —— AOF everysec + RocksDB 同步写、重启从 RocksDB 预热、冷启 < 5 分钟。
> 2. "热 key 怎么防？" —— 热门 user/item 本地 Ristretto LRU、命中率 60%+ 后再去 Redis、热点 RPS 降 60%。
> 3. "online/offline 特征怎么对齐？" —— Iceberg snapshot + point-in-time join、训练 job 读 `@as_of_timestamp`、物理 key 是 event_time+user_id+item_id。

Offline 冷层我选 **S3 + Parquet + Iceberg**，因为 S3 单字节 $0.023/GB/月、Parquet 列存压缩比 5:1、Iceberg time-travel 让训练可复现任意历史快照、与 Spark/Presto/Athena 生态全兼容。候选一是 **HDFS**——适合批处理但 NameNode 单点运维重、云原生方向 S3 工具链更全，HDFS 更合适的位置是私有云，淘汰。候选二是 **BigQuery**——按字节扫描计费、全表 scan 账单快速上升、与 Spark 训练 pipeline 需 connector，BigQuery 更合适的位置是 ad-hoc 分析而非训练数据底层。候选三是 **Delta Lake**——ACID 事务 + Schema evolution 完整，但需 Databricks/Spark 强绑定、跨团队迁移成本高，Delta Lake 更合适的位置是 Databricks 全家桶团队。切换触发：跨团队要 ACID 写入时迁 Delta Lake；ad-hoc 分析成主场景时叠 BigQuery 联邦查询。

### 事件总线 (100 MB/s → 8 TB/day)

事件流 70K QPS × 3 events/req × 500B ≈ **100 MB/s**、日 8 TB。

事件总线我选 **Kafka 64 partitions**，因为单 partition 20-30MB/s、64 partition 合计 > 1 GB/s 留 10× headroom、exactly-once 语义 + 消费组隔离让训练 sink 与实时分析互不干扰。候选一是 **Apache Pulsar**——多租户隔离好、Segmented storage 灵活，但运维复杂、社区生态弱于 Kafka，Pulsar 更合适的位置是 SaaS 多租户场景。候选二是 **AWS Kinesis**——托管省运维，但单 shard 1MB/s 上限低、rescaling 手动、成本 3× Kafka，Kinesis 更合适的位置是 Lambda-only 栈，淘汰。候选三是 **RabbitMQ**——事务语义丰富，但吞吐上限 200MB/s、远不够 10× headroom 要求，RabbitMQ 更合适的位置是事件扇出的 RPC-like 场景。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈转 Lambda 时评估 Kinesis。

这一节 takeaway：350K invocations 推出 GPU 批推、256GB embedding 推出 HNSW sharded 32 份、1TB+5TB 推出 Redis hot + S3 cold、8TB/day log 推出 Kafka 64p——这四个数字把 §3 的建模服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按建模职责 + SLA 切、而不是按业务域 (User / Item / Feed) 切；数据怎么流——端到端召回→粗排→精排→重排的 fan-out 结构要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：精排 350K invocations/s 的 GPU 层和重排 70K QPS 的 CPU 层不能共用线程池、feature store 700K reads/s 必须独立出来不能挂在任何单一推理服务内。

服务拆分策略我选 **按漏斗层 + SLA 切分**，因为召回 30ms / 粗排 20ms / 精排 100ms / 重排 20ms 是四个独立 SLA，每层允许独立扩缩容、独立 A/B 分流、独立模型热加载；把这四层塞一个"Recommendation Service"会出现任一层流量飙升把整个服务打崩的级联故障。候选一是按**业务域切分** (User / Item / Interaction)——界面实体抄到后端，完全忽略 read/write + SLA 差异，热门物品 QPS 和历史交互 QPS 差 10×、放一起互相拖垮，淘汰。候选二是按**数据管道切分** (Retrieval / Ranking 为一体, Feature / Embedding 为一体)——比业务域合理但把召回和粗排/精排打包成一块仍然会让推理 GPU 与 Redis 查询耦合；数据管道切分更合适的位置是纯 ETL 系统不是在线服务。候选三是按**客户端切分** (Rider-facing / Driver-facing) ——与本题无关，推荐系统单向产出不存在双边用户；淘汰。切换触发：当某层流量下降到与邻层差距 < 2× 时可合并；当出现新的数量级 SLA 差异时再切一刀 (例如引入 LLM 重排后 p99 拉到 500ms 必须拆一层)。

> **常见追问**:
> 1. "召回、粗排、精排可以共用同一个模型吗？" —— 不行，召回追求 recall + 低延迟 (< 30ms)、精排追求 calibration + 多特征交叉 (100ms 预算)、目标与延迟不匹配。
> 2. "Feature Store 放进哪个服务？" —— 独立服务，被召回 (粗粒度 user/item embedding)、精排 (dense context feature)、重排 (多样性统计) 共读，绝不能塞进任一推理服务。
> 3. "Experiment Service 算独立服务吗？" —— 算，A/B 分桶需要强一致性、与推理完全不同 SLA (读 < 1ms 写 < 10ms)，放独立服务便于审计归因。

端到端数据流：用户请求进 Gateway → 查 Experiment Service 决定本次 A/B 桶 → Retrieval Service 多路召回 (ANN + CF + Trending + Social) 并集 500 候选 → Coarse Ranker 粗排到 300 → Fine Ranker 精排到 50 → Re-Ranker 做多样性 + 冷启配额 + 广告混排 → 返回 20 给用户；同时曝光事件通过 Kafka 流回 Feature Store 做准实时特征更新、训练事件批落 S3 供离线训练。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——ANN 挂了走 CF、精排挂了走粗排分、重排挂了走精排分 round-robin、完整链路允许 2 层同时降级仍返回可用结果。

这一节 takeaway：推荐系统的服务边界不是业务边界，而是建模层 + SLA 边界；任一层必须自带 fallback，链路级降级比单点高可用更关键。

## 4. Deep Dives

这一节把漏斗四层 (召回 / 精排 / 重排 / 冷启与探索) 逐一展开，每一层给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"推荐系统每层算法选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章的编排顺序与在线 serving 数据流一致：召回在前、精排在中、重排在后、探索贯穿全程。

### 4a. Candidate Generation (召回)

召回的本质是在 500M 物品库里快速圈出 500 候选、追求 recall@500 ≥ 0.98、延迟 p99 < 30ms。单路召回覆盖率不够，多路并集是工业标配。

主召回我选 **Two-Tower Model** (双塔模型)，因为它用户塔与物品塔完全解耦、物品侧 embedding 可以离线批量预计算、在线只做用户塔推理 + ANN 查询、平均 RT 5-10ms、与 HNSW 工具链完美对齐、Google YouTube / Pinterest / Meta 均有线上 paper 背书。候选一是 **Cross-Encoder (BERT-style)**——用户和物品同 Transformer 共编码，精度高 5-10% 但延迟炸到 50ms、无法预计算物品 embedding、500 候选跑不完，Cross-Encoder 更合适的位置是精排而非召回，淘汰。候选二是 **Item-based Collaborative Filtering** (ItemCF)——基于共现矩阵、冷启项死穴，但对热门项召回率高、无需 embedding 训练、5min 内可上线，ItemCF 更合适的位置是 Two-Tower 的补充召回路；保留。候选三是 **Matrix Factorization** (矩阵分解)——$\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \mathbf{q}_i$ 的经典 SVD / BPR 训练，损失 $\mathcal{L} = \sum_{(u,i) \in \mathcal{K}} (r_{ui} - \hat{r}_{ui})^2 + \lambda(\|\mathbf{p}_u\|^2 + \|\mathbf{q}_i\|^2 + b_u^2 + b_i^2)$，早期推荐系统的基线，但无法融合内容特征、冷启差，MF 更合适的位置是离线 baseline 和 ItemCF 的 embedding 源；淘汰。候选四是 **Graph Neural Network** (GNN, 图神经网络, 如 PinSage)——图结构信号丰富、长尾召回强，但训练 + 部署基础设施复杂、单次迭代 > 8 小时、运维工具链不成熟，GNN 更合适的位置是 Two-Tower 成熟后的"召回增强"而非主路。切换触发：当长尾物品召回率 < 0.5 时叠 GNN；当冷启用户占比 > 30% 时补 Content-based + Two-Tower Cold Start tower。

> **常见追问**:
> 1. "**Bayesian Personalized Ranking** (BPR, 贝叶斯个性化排序) 损失和 Pointwise 损失怎么选？" —— 召回侧优先 BPR pairwise $\mathcal{L} = -\sum_{(u,i,j)} \log \sigma(\hat{r}_{ui} - \hat{r}_{uj})$ 直接优化排序、训练更稳；Pointwise 适合 CTR 校准。
> 2. "负样本怎么采？" —— In-batch negative 默认、难负例 (hard negative mining) 从历史曝光未点击 pool 挑、全局热门 + 用户无交互作为 easy negative。
> 3. "Two-Tower 训练怎么防塌缩？" —— 温度系数 + L2 归一化 + 大 batch、避免 softmax sum 退化到 1。

### 4b. Ranking Models (精排)

精排的任务是在 300 候选里做精准 CTR/CVR 预测、延迟 p99 < 100ms、关键是特征交叉与多目标融合。

精排我选 **DLRM** (§2 已给过部署选型，这里补建模 why-not 给面试闭环)，因为它 sparse embedding + dense tower 的工业架构与 Meta 生产线规模对齐、支持数十亿参数 sharded embedding、与 TF-Serving / Triton 推理栈天然对齐、MLPerf 推荐基准有稳定 benchmark。候选一是 **Wide & Deep**——Wide 端 cross-product 记忆 + Deep MLP 泛化的 Google 经典范式、小规模特征好用，但 Wide 端需要重度人工特征工程、与 sparse embedding 融合不如 DLRM 原生顺滑，Wide & Deep 更合适的位置是 dense feature 为主的中小规模 CTR 场景，所以不用。候选二是 **DCN-v2**——显式高阶交叉 block 表达力强、特征交叉解释性好，但 sparse 端分布式训练 benchmark 弱于 DLRM、在 B 级 embedding 规模下 scale 吃力，DCN-v2 更合适的位置是以 dense feature 为主的搜索广告 CTR；淘汰。候选三是 **DIN** (Deep Interest Network, 深度兴趣网络)——attention over user sequence 建模长兴趣强，但 sparse tower 工业化不足、独立精排 benchmark 数据不稳，DIN 更合适的位置是与 DLRM 叠加做 attention block 而非独立精排；保留作融合增强。切换触发：当多目标 > 3 且单头模型出现 reward hacking 时迁 MMoE/PLE；当 dense feature 占比 > 70% 时评估 DCN-v2；当用户历史序列成为主导信号时叠 DIN block。整体演进链条仍是 Wide & Deep → DCN-v2 → DIN → DLRM → MMoE → PLE；DIN 的关键贡献是 attention 对用户序列动态加权、DLRM 的贡献是 sparse + dense 工业化、MMoE 的贡献是多目标独立 gate 减少负迁移。

多目标融合策略我选 **学习式 fusion head (learned-fusion MLP)**——DLRM/MMoE 输出 [CTR, CVR, dwell_time] 三个 logit、下游一个 2-layer MLP 学加权，权重随业务指标动态调整，比线性加权更稳。候选一是 **线性加权 (Hand-tuned weighted sum)** $\text{score} = w_1 \cdot \hat{CTR} + w_2 \cdot \hat{CVR} + w_3 \cdot \hat{dwell}$——可解释性强、冷启易调，但权重漂移需手动；hand-tuned 更合适的位置是 MVP 阶段、作为 learned-fusion 的基线。候选二是 **Pareto Front Selection**——多目标不融合、返回 Pareto 前沿让业务按场景挑，但推荐场景单一返回需求下 Pareto 选择逻辑复杂、不直接可服务，淘汰；Pareto 更合适的位置是广告拍卖多目标优化。候选三是 **Reinforcement Learning based fusion** (RL 融合)——直接优化长期 reward，但线上样本效率低、policy 稳定性差，RL 更合适的位置是 off-policy evaluation 跑通后的下一阶段升级。切换触发：线上指标出现 CTR↑ 但 retention↓ 时从 learned-fusion 升级到 RL-fusion。

> **常见追问**:
> 1. "DIN / DIEN 与 DLRM 能共存吗？" —— 可以，DLRM sparse tower + DIN attention block 叠 user sequence feature 是工业常见组合。
> 2. "如何避免 position bias？" —— 训练时把 position 作为 bias feature 输入、服务时置零 (PAL 做法) 或模型并行估计。
> 3. "模型刷新频率？" —— 增量训练小时级、全量训练日级、重大特征改造周级灰度。

### 4c. Re-Ranking & Diversity (重排与多样性)

重排的任务是在 50 个精排候选里做最终列表构造、考虑多样性、新鲜度、广告 slot、冷启 slot、用户合规偏好、p99 < 20ms。

重排策略我选 **Maximal Marginal Relevance** (MMR, 最大边际相关性) + slot-based diversity 混合，因为 MMR 贪心选择兼顾相关性和多样性、实现简单 O(K²)、可解释、$\text{MMR} = \arg\max_{d_i \in R \setminus S} [\lambda \cdot \text{Sim}(d_i, q) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j)]$、业务侧可按品类预留固定 slot 保证内容覆盖。候选一是 **Determinantal Point Process** (DPP, 行列式点过程)——基于核矩阵的概率采样、理论保证子集多样性最优，但 O(K³) 或近似 O(K²) 实现复杂、kernel 调参门槛高，DPP 更合适的位置是大 slate (> 20 items) 且对多样性理论最优有强诉求的场景，淘汰。候选二是 **Learned Re-Rank (Listwise)**——把整 list 作为 input 送 Transformer 直接预测最终顺序、端到端优化多目标，但训练 label 稀疏 (只有展示后点击)、模型复杂度高、线上首次迭代难收敛；Learned Re-Rank 更合适的位置是 MMR + slot 跑通后的"下一阶段优化"。候选三是 **Rule-based (hand-tuned)**——全手写规则 (每 3 item 插 1 广告、热榜保 1 slot)，可解释极高但规则膨胀后维护灾难；rule-based 更合适的位置是冷启前两周的 MVP。切换触发：slate 升到 20+ 或多样性指标下滑时迁 DPP；上线 learned listwise 做 end-to-end 优化时迁 Learned Re-Rank。

> **常见追问**:
> 1. "多样性与 CTR 如何平衡？" —— λ 参数调节相关性与多样性权重，A/B 试验找到 CTR 与次日留存联合最大点。
> 2. "广告 slot 和自然结果怎么混排？" —— 广告走独立拍卖通道、按 **effective Cost Per Mille** (eCPM, 千次有效曝光成本) 与自然结果联合排序、按业务配额插入固定 slot。
> 3. "冷启动物品如何保证曝光？" —— 硬配额：每 20-position slate 预留 2 slot 给 < 7 天的新品、配合探索 (见 4d)。

### 4d. Cold Start & Exploration (冷启与探索)

冷启分用户冷启和物品冷启，前者通过引导问卷 + Content-based 补召回、后者通过探索预算保曝光。核心矛盾是 exploration-exploitation tradeoff。

探索策略我选 **Thompson Sampling** (汤普森采样)，因为它 Bayesian 后验采样自然平衡探索与利用、收敛快、参数只需 prior 分布、在线可直接 incremental 更新。候选一是 **ε-Greedy**——以 ε 概率随机探索、1-ε 选当前最优、实现极简，但固定 ε 无法自适应、冷启期探索不够、稳定期探索浪费，ε-Greedy 更合适的位置是 MVP 阶段或探索预算固定场景。候选二是 **Upper Confidence Bound** (UCB)——按 $\hat{\mu}_a + c\sqrt{\ln t / N_a}$ 选臂、确定性策略方便调试，但 UCB 需要精确知道奖励分布且对 reward scaling 敏感、推荐 reward 稀疏下表现不如 Thompson，UCB 更合适的位置是 A/B 分桶这种 reward 密集的场景，淘汰。候选三是 **Linear UCB** (LinUCB) / **Contextual Bandits**——把 user/item context 作为特征线性预测 reward + UCB bound，适合 contextual arm、但冷启时特征稀疏、线性假设限制表达，LinUCB 更合适的位置是 context 丰富且线性建模够用的广告场景。候选四是 **Deep Contextual Bandits**——DNN 预测 reward + bootstrap posterior，表达力强但训练不稳、off-policy 评估复杂，Deep CB 更合适的位置是 Thompson 跑通后需要非线性 context 的升级阶段。切换触发：冷启量 < 5% 时退回 ε-Greedy 省运维；context 信号强且需要精细归因时迁 LinUCB。

> **常见追问**:
> 1. "探索预算怎么定？" —— 通常 5-10% slate slot 给探索、Thompson 的后验宽度自动控制探索强度。
> 2. "冷启用户如何处理？" —— 引导问卷获取 3-5 个兴趣标签、Content-based 补召回、首日后快速收敛到 Two-Tower + 历史兴趣。
> 3. "如何评估探索效果？" —— 长期留存 + 新用户 D7 retention、分桶对照、Interleave 同场比较。

这一节 takeaway：推荐系统不是一个模型、而是四层算法候选池的组合；每层默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

推荐系统的可靠性不是"整条链路 100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量"的分层容错。

监控策略我选 **四象限监控 + 分层 SLO**，因为系统/模型/业务/实验四个维度要分开看、分层 SLO 让降级决策可编程。系统层对接 **Prometheus** + **Grafana** 采集 p99 延迟、error rate、资源利用率；模型层引入 **Evidently** 或 **Arize** 采集 CTR/CVR 预测分布漂移、特征 null rate、embedding 退化 (cos sim 飘离基线 > 0.1)；业务层接入内部 BI 看 session CTR、停留、次日留存 (D1 retention)；实验层采集分桶平衡、SRM (Sample Ratio Mismatch)、novelty effect。候选一是 **Datadog 单栈统一中台**——工具链简化但跨维度语义损失、模型漂移细节看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize 独立 ML 监控平台**——ML 专用指标全、SHAP 解释内嵌，但与系统监控割裂、告警链路双头，Arize 独立栈更合适的位置是模型 ops 团队独立于平台团队；淘汰。候选三是 **Fiddler 独立 ML 监控平台**——可解释性专精、模型公平性审计完整，但与开源 Prometheus 生态整合成本高、许可证费用贵，Fiddler 更合适的位置是强合规场景的金融/医疗。候选四是 **自建 full-stack 监控**——灵活度最高但研发成本巨大，自建更合适的位置是 FAANG 规模需要深度定制。切换触发：模型漂移成为核心故障源时补 Arize；团队规模 > 100 MLE 时考虑自建核心监控栈。

降级预案：精排挂了 fallback 到粗排分；粗排挂了 fallback 到召回分 + 热度分；重排挂了返回精排原始顺序；特征缺失用 per-feature default (如 7 天滑动均值) 兜底；ANN 索引挂了 fallback 到 CF / 倒排 / 热榜多路并集。每条 fallback 路径必须独立演练、月度 game day 强制跑一次。

这一节 takeaway：reliability 不在单点高可用而在分层可降级，四象限监控 + 每层独立 fallback 是推荐系统高可用的必选项。

## 6. Summary & Tradeoffs

本题核心 takeaway 是推荐系统的分层思维：召回/粗排/精排/重排四层各有独立算法候选池，每层选型都伴随 Pick + 3 候选 + why-not + 切换条件五元组。召回默认 Two-Tower、精排默认 DLRM、重排默认 MMR + slot、探索默认 Thompson；多目标升级路径 MMoE/PLE，大 slate 升级路径 DPP。

三个最常被错答的 tradeoff：一是"召回能否和精排合并"——不能，目标与延迟不匹配；二是"多样性对 CTR 有损是否放弃"——短期 CTR 损但次日留存收益通常更大；三是"冷启用哪层兜底"——不是单一冷启模型，而是多路召回 + 探索预算 + slot 配额三者组合。长期优化依赖 **Data Flywheel** (数据飞轮)：行为训练模型→更好推荐吸引更多交互→更多数据反哺模型；同时警惕 Filter Bubble (过滤气泡) 风险。

工程 vs 建模的决策拉锯主要在两处：一是 feature store 热层在 Redis 与 Feast 之间取舍——小团队 Feast 运维省、大流量 Redis 吞吐稳；二是 ANN 索引在 HNSW 与 IVF-PQ 之间取舍——精度优先 HNSW、成本优先 IVF-PQ。选型的真正判据不是"谁更先进"，而是"当前业务的 DAU、物品规模、成本敏感度落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："你这套系统上线后 CTR 涨了但 D7 retention 跌了，怎么办？"——这是典型的短期指标胜长期指标失败。答案思路：一是先判断是否是 novelty effect (新鲜度短期刷 CTR)；二是做多目标融合升级 (CTR + retention 联合 loss 或 MMoE 多头)；三是重排 slot 加"探索性内容"保证兴趣拓展；四是业务侧监控 D7 作为核心 SLO 而非 CTR 单指标。

第二题："长尾物品 (尾部 90% 物品贡献 20% 流量) 曝光怎么保障？"——长尾曝光是推荐生态的核心课题。答案思路：一是召回侧 GNN/Content-based 补长尾召回路径；二是精排侧用 position bias 修正 (Inverse Propensity Scoring) 让长尾物品不被历史曝光分压制；三是重排侧 slot 保量 (每 slate 预留 N 个长尾 slot)；四是评估 **Coverage** (覆盖率) 与 **Gini 指数** 作为生态指标。

第三题："如何避免 Filter Bubble (过滤气泡)？"——这是推荐系统长期价值问题。答案思路：一是多样性重排 (MMR/DPP) 约束类目分布；二是主动探索 (Thompson Sampling) 为新兴趣分配曝光；三是 Serendipity 指标 (用户意想不到但喜欢的比例) 作为辅助 SLO；四是业务侧引导 (推荐首页固定"为你发现"入口)。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) 多阶段漏斗每一层的延迟预算和目标指标；(2) 每层默认模型和它的 3 个候选 + why-not；(3) 多目标融合 (CTR+CVR+dwell) 三种做法 (hand-tuned / learned-fusion / RL) 的切换条件；(4) Two-Tower vs Cross-Encoder 的延迟与精度 tradeoff；(5) HNSW / IVF-PQ / ScaNN / Milvus 的内存 vs 精度 tradeoff 曲线；(6) MMR 公式 + DPP 的 why-not；(7) Thompson Sampling vs ε-Greedy vs LinUCB 的适用场景；(8) 四象限监控 + 每层 fallback 的降级预案。八个都能答对就可以去白板了。
