# Computer Vision Systems (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个生产级计算机视觉系统"——图像分类、目标检测、语义分割、视觉搜索、内容审核、OCR、自动驾驶感知都能套。与 id=93 NLP & LLM Systems 讲"encoder-heavy 判别式 NLP + LLM 作 fallback"不同，本题的重心是**高维像素输入 + 严格实时性 + 多硬件端并存**：单张 1080p 图像约 600 万像素、模型计算密集度远超文本、自动驾驶/AR 场景需要 30fps+、服务端与端侧 (手机/IoT/车载芯片) 的部署路径必须在同一条选型链上同时讲清。考官会盯着两个分水岭：一是 backbone 的"精度 × 延迟 × 数据效率"三角 (ResNet / EfficientNet / ViT / ConvNeXt / Swin)、二是"server-GPU 推理 vs on-device 小模型"的拆分决策；答不清楚这两点就只能拿到 L4。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=90 Recommendation Systems](/kg?node=n90)、[id=93 NLP & LLM Systems](/kg?node=n93)、[id=95 Fraud & Trust Safety](/kg?node=n95)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问这五元组) 是本题所有 deep dive 的评分标尺。再读 id=90 的理由是：视觉搜索管道复用召回/精排漏斗范式，只是把文本 embedding 换成视觉 embedding、ANN 索引查询模式完全一致。读 id=93 的理由是：视觉领域也有类似 NLP 的"基础模型演化链条" (ResNet → EfficientNet → ViT → ConvNeXt → Swin 对应 BERT → RoBERTa → DeBERTa → DistilBERT)，两篇的蒸馏/量化部分相互参照可减少重复。id=95 对内容审核类 CV 场景的 label delay / 决策可解释性有独立覆盖。本题读者应对 **Convolutional Neural Network** (CNN, 卷积神经网络)、**Vision Transformer** (ViT, 视觉变换器)、**Approximate Nearest Neighbor** (ANN, 近似最近邻)、**Intersection over Union** (IoU, 交并比)、**Non-Maximum Suppression** (NMS, 非极大值抑制)、**Knowledge Distillation** (知识蒸馏) 这些概念有基础认识，否则 backbone 与检测头选型环节容易卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把产品经理的话抄一遍"，而是把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一个答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈落在 backbone GPU 推理、图像解码 IO、多任务头的调度、以及端/云模型一致性；强一致只出现在审核结果与计费归因一瞬"。

**Functional requirements (功能需求)** 主流程是用户/设备上传图像 → 图像预处理 (解码、resize、归一化) → Backbone 特征提取 → 任务头 (分类/检测/分割/embedding) 并发推理 → 后处理 (NMS、掩码融合、Top-K) → 结果返回/落库。针对 Pinterest / Instagram 级图片社交产品，产品功能含 (a) 图片分类打标 (主体 / 场景 / 情绪 / NSFW 审核)、(b) 目标检测 (商品识别 / 人脸检测 / 标志识别)、(c) 语义/实例分割 (背景替换 / 图像编辑 / AR 特效)、(d) 视觉搜索 (以图搜图 / Shop-the-look 商品定位)、(e) OCR 文本抽取、(f) 内容审核 (色情/暴力/血腥过滤)。辅流程包括模型冷启动 (新商品/创作者类目)、训练数据回流 (**Data Flywheel** 数据飞轮)、**Active Learning** (主动学习) 选样、**Auto-labeling** (自动标注) 与人审闭环。这些功能归成四组——Ingestion、Backbone/Heads、Post-processing/Search、Feedback/Labeling——后面 deep dive 按这四组展开。

**Non-functional requirements (非功能需求)** 规模取 Pinterest/Instagram 量级：日上传图像 5 亿张、峰值 **Queries Per Second** (QPS, 每秒查询数) 10K 图像理解请求、每张图平均走 3-5 个任务头 (分类 + 检测 + embedding + NSFW)、请求到达模型服务的实际 invocation 约 40K/s；延迟 p99 < 200ms 端到端 (解码 30ms + preprocess 10ms + GPU 推理 80ms + post-process 20ms + 网络 + serialization 60ms)；对自动驾驶/AR 这类子场景延迟预算再收紧到 30ms (去掉 cloud hop、全部 on-device)；特征查询 p99 < 5ms；一致性除审核结论与计费事件强一致外其他 eventual；可用性月度 99.9% 即 40 分钟 budget；新鲜度新创作者内容 10 分钟内纳入索引、商品类目更新 1 小时生效。

**Out-of-scope (排除项)** 视频时序建模 (另开 id=Video Understanding)、生成式图像 (另开 id=97 GenAI)、3D 重建/NeRF、医学影像合规栈 (独立 PACS 工作流)、广告投放拍卖 (见 id=91)。排除不是"忽略"而是主动声明——面试官问视频理解时我知道这超范围、可以明确"这是单帧图像理解设计"。

**必问五问的本题答**：Q1 规模 QPS=10K 图像请求、40K invocations/s、日新增图像 5 亿张、embedding 向量库 100 亿条；Q2 读写比 读略高于写但 embedding 检索放大 500× (以图搜图)、GPU 算力是主瓶颈；Q3 延迟 端到端 p99<200ms 为服务端基线、on-device 子场景 30ms；Q4 一致性 审核结论 + 计费事件强一致，embedding 索引与分类结果 eventual；Q5 地域 多 region active-active、embedding 索引按 region 分片、审核决策只在主 region 做再同步到副本。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，200ms 延迟预算与审核强一致是两个最硬的约束，任何建模选型都要反向追溯到"因为需求里说过……"。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个建模与基础设施决策找实在的瓶颈锚点——哪条路径是真有压力、数字背后绑着哪个技术拐点。我按模型推理 → 特征层 → 事件总线 → 训练数据四条链路走一遍，每一段除了给数字还给出对应的选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### GPU 推理调用链 (10K QPS × 4 heads → 40K invocations/s → 200+ A100)

请求峰值 10K QPS × 每张图平均 4 个任务头 → 推理 invocations 峰值 **40K/s**。这个数字把服务端推理直接压进"必须 GPU + dynamic batching + 共享 backbone"的硬件边界。单张 A100 对 ViT-Base + 4 个任务头 batch=16 ≈ 200 QPS 图像、40K invocations/s 换算约 200 张 A100 + 20% headroom。

推理服务我选 **Triton Inference Server**，因为它对多模型多后端 (TensorRT / ONNX Runtime / PyTorch / TensorFlow) 统一封装、dynamic batching 在 ViT 这种 Transformer-heavy backbone 上延迟摊薄最佳、ensemble scheduler 原生支持"共享 backbone → 多任务头"DAG、NVIDIA 生态与 TensorRT 编译产物零拷贝对接、DALI 图像预处理 pipeline 可与推理在同一 CUDA stream 里链起来。候选一是 **TorchServe**——PyTorch 原生、开发者友好，但 dynamic batching 成熟度弱于 Triton、多任务头共享 backbone 的 DAG 要手写 handler、吞吐 benchmark 约 Triton 的 70%，TorchServe 更合适的位置是小团队 PyTorch-only 栈，所以不用。候选二是 **TensorFlow Serving**——TF 官方推出、gRPC 成熟，但多任务头 DAG 弱、与 PyTorch 训练栈打通要走 ONNX 转换、TF-only 场景才值得，淘汰；TF-Serving 更合适的位置是 TF 训练 + 部署一体化的老团队。候选三是 **BentoML**——Python-first DX 好、跨语言打包简单，但生产级大规模 GPU 并发调度能力弱于 Triton、dynamic batching 不如 Triton 成熟，BentoML 更合适的位置是中小流量或快速原型迭代。候选四是 **Ray Serve**——与 Ray 生态强绑定、autoscaling 灵活，但 GPU dynamic batching 需要自己写、不如 Triton 开箱即用，Ray Serve 更合适的位置是需要与 Ray Train / Ray Tune 深度耦合的 workflow。切换触发：全栈 PyTorch-only 且团队 < 5 MLE 时用 TorchServe；与 Ray 训练集成成核心诉求时迁 Ray Serve；纯 TF 团队保留 TF-Serving。

> **常见追问**:
> 1. "多任务头怎么共享 backbone？" —— Triton ensemble scheduler 定义 DAG、backbone 一次前向、classification / detection / embedding / NSFW heads 并发消费 feature map、节省 70% backbone 重复计算。
> 2. "dynamic batching 窗口多少？" —— p99 < 200ms 预算下 batching window 3-5ms、batch=16 最优、再大延迟撞顶；窗口内等不满就先发、不硬凑。
> 3. "GPU 利用率多少合理？" —— 在线 60-70% 留 headroom、峰值可到 85%；> 90% 时任意 spike 都会打爆 p99、必须扩容。

### Feature Store / Embedding Store (100 亿向量 + 热特征)

视觉搜索 embedding 向量库 100 亿条 (5 亿图 × 过去 5 年 + 新鲜流量)、每条 512 维 float32 ≈ 2KB → 20TB、加倒排 metadata 约 **40TB**；在线热特征 (用户侧视觉兴趣画像 + 商品创建时 metadata) 5 亿 × 200 feats × 16B ≈ **1.6 TB**、每请求 20-50 reads、p99 < 5ms。

Embedding 索引层我选 **HNSW (hnswlib 实现) sharded 64 份**，因为它图结构检索 QPS 最高 (单 shard > 10K)、recall@100 稳定 0.95+、支持 online insert 新广告/新商品 5 分钟入索引、与 Two-Tower 视觉 embedding 离线批产线兼容，工业视觉搜索 (Pinterest Lens / Google Lens) 均有线上 paper 背书。候选一是 **FAISS IVF-PQ**——倒排 + 乘积量化、内存只用 HNSW 的 1/4、适合 10B+ 规模，但量化损 recall 到 0.88、静态索引 rebuild 6-12 小时不利于 5 分钟新鲜度，IVF-PQ 更合适的位置是 B 级库 + 离线召回 + 对延迟容忍度高的长尾场景，所以不用。候选二是 **ScaNN** (Google)——各向异性量化精度最好、Google 线上验证过，但与 K8s 部署工具链整合成本高、Python-only 工具链差，ScaNN 更合适的位置是 GCP Vertex AI 原生栈，淘汰。候选三是 **Milvus**——分布式向量数据库、K8s-native 部署，但延迟比 hnswlib 原生库多 5-10ms 一跳、QPS 头部案例少于自建 HNSW，Milvus 更合适的位置是多租户 SaaS 场景。候选四是 **Pinecone / Weaviate** 托管向量库——省运维、跨团队 API 友好，但成本 3-5× 自建、数据锁在第三方、合规风险高，托管向量库更合适的位置是早期项目或中小流量。切换触发：库规模升到 100B 级时迁 IVF-PQ；多业务共享向量基础设施时评估 Milvus；早期小团队用 Pinecone。

热特征层我选 **Redis Cluster 128 节点 + RocksDB 持久层**，因为 Redis 单节点 100K QPS 读、128 节点 12M reads/s 留 10× headroom、RocksDB 兜底重启雪崩、与视觉推理在线 embedding 查询耦合成熟。候选一是 **DynamoDB**——托管省运维、multi-AZ 自动冗余，但 on-demand 单价 5-10× Redis 自建、500+ reads/req 账单快速失控，DynamoDB 更合适的位置是中小流量或按量付费场景，所以不用。候选二是 **Memcached**——纯 KV 延迟更低，但不持久化、重启冷启 > 30 分钟、一致性哈希漂移导致连接抖动，Memcached 更合适的位置是完全无状态 page cache，淘汰。候选三是 **Cassandra**——LSM 写吞吐高、持久化稳健，但 p99 read 10-20ms 撞 5ms SLA、命中率低于 Redis，Cassandra 更合适的位置是 warm 层而非 hot 层。候选四是 **Aerospike**——SSD-optimized KV、p99 < 1ms、混合内存/SSD 架构成本低，但许可证费用 + 运维复杂度高，Aerospike 更合适的位置是超大规模 + 强合规场景。切换触发：流量再涨 2× 时扩到 256 节点；成本占比 > 35% 时评估 Aerospike。

> **常见追问**:
> 1. "HNSW 100 亿向量单机装不下怎么办？" —— 按 creator_id / category shard 到 64 机、客户端 scatter-gather 合并 top-K；单 shard 内存约 15GB embedding + 图结构 overhead。
> 2. "新图 5 分钟入索引怎么做？" —— 生产者管道把新图 embedding 写 Kafka、消费者把 embedding 增量 insert 到对应 shard (HNSW 单次 insert < 10ms)、日级全量 rebuild 兜底图质量。
> 3. "跨 region 索引一致吗？" —— 主 region 写、异步复制到副本；允许 1-2 分钟滞后，视觉搜索是 eventual-consistency 场景可接受。

### 事件总线 (原图 250MB/s + 标签事件 80MB/s)

原图流入 Kafka binary channel 5 亿/日 × 500KB ≈ **250MB/s** 峰值、标签/审核事件流约 80MB/s、日均事件 80TB。

事件总线我选 **Kafka 384 partitions**，因为单 partition 20-30MB/s、384 partition 合计 > 10 GB/s 留 30× headroom、exactly-once 语义让训练 sink 与实时分析互不干扰、与 Flink 流处理原生集成、大图二进制对 Kafka 消息大小 (默认 1MB) 需要 tuning 成 5MB max.message.bytes。候选一是 **Apache Pulsar**——多租户隔离好、tiered storage 把冷数据下沉 S3，但运维复杂度高、社区生态规模仍弱于 Kafka，Pulsar 更合适的位置是强多租户隔离的 SaaS 场景，所以不用。候选二是 **AWS Kinesis**——托管省运维、与 Lambda 无缝整合，但单 shard 1MB/s 上限低、大图二进制需要分片成本高、跨云供应商锁定，Kinesis 更合适的位置是纯 AWS Lambda-only 栈，淘汰。候选三是 **Redpanda**——C++ 重写的 Kafka 兼容实现、延迟低、no ZooKeeper 运维简，但社区规模仍小于 Kafka、大图场景工业案例少，Redpanda 更合适的位置是对 p99 延迟要求极端的金融交易流场景。候选四是 **Amazon S3 + SQS 直传**——大图直接 S3、SQS 只传 S3 key、避免 Kafka 消息大小限制，但训练 pipeline 需重写、流式处理延迟差，S3+SQS 更合适的位置是纯批量 pipeline。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈 serverless 化时评估 Kinesis；图像流量占 > 80% 时可考虑 S3+SQS 旁路。

### Training Data 回流 (5 亿图/日 → 单数据集 50-200 TB)

每日新增 5 亿张图、平均 500KB、日 **250TB** 原图 + 标签/meta 10TB；活训练集约 6 个月 = 45PB、单次训练 job 按类别抽样 50-200TB。

训练数据底层我选 **S3 + Parquet (for meta) + WebDataset (.tar shards for images) + Iceberg 元数据目录**，因为 S3 单字节 $0.023/GB/月、Parquet 列存 meta 查询快、WebDataset 连续读取大图吞吐远超 random-access、Iceberg 做时间旅行让训练可复现任意历史快照、与 PyTorch DataLoader 的 `IterableDataset` 原生匹配。候选一是 **HDFS**——适合批处理但 NameNode 单点运维重、云原生方向工具链逐渐转 S3，HDFS 更合适的位置是私有云强合规场景，所以不用。候选二是 **直接存 TFRecord in GCS**——与 TPU 训练对齐、序列化高效，但与 PyTorch 训练栈隔离一层、工具链锁定 TF，TFRecord 更合适的位置是纯 TPU/TF 训练栈，淘汰。候选三是 **Delta Lake**——ACID 事务 + Schema evolution 完整，但对大图二进制 binary column 支持弱、更擅长结构化表数据，Delta Lake 更合适的位置是训练元数据表 (非原图) 且有 Databricks 深度绑定。候选四是 **BigQuery**——按字节扫描计费、ad-hoc 分析快，但 45PB 训练 scan 账单快速上升、原图 binary 不适合 BQ 场景，BigQuery 更合适的位置是 ad-hoc 分析 + 小数据场景。切换触发：跨团队要强 ACID 写入的结构化 meta 时叠 Delta Lake；ad-hoc 分析成主场景时叠 BigQuery 做联邦查询；TPU-only 训练栈保留 TFRecord 路径。

这一节 takeaway：40K invocations/s 推出 Triton + GPU 批推、100 亿 embedding 推出 HNSW sharded 64、250MB/s 原图流推出 Kafka 384p + max.message 5MB tuning、45PB 训练集推出 S3+WebDataset+Iceberg——这四个数字把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按 pipeline 层 + SLA + 硬件资源类型切、而不是按业务域切；数据怎么流——端到端 Ingestion → Preprocess → Backbone → Heads → Post-process → Feedback 的 DAG 结构要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：Image Decode 是 CPU-bound (libjpeg-turbo / nvJPEG)、Backbone 是 GPU-bound、Post-process (NMS / 掩码合并) 又回到 CPU-bound、Embedding 索引查询是内存+CPU、审核决策是强一致 + 低 TPS；把这五层塞一个"CV Service"会出现任一层流量飙升把整个服务打崩的级联故障。

服务拆分策略我选 **按 pipeline 层 + SLA + 硬件资源类型切分**，因为 Image Ingester (CPU + 高带宽网卡) / Preprocessor (CPU/GPU mixed, DALI) / Backbone Inference (GPU, TensorRT) / Task-head Service (GPU, dynamic batching) / Post-processor (CPU, NMS/掩码) / Visual Search (CPU + 内存, HNSW) / Moderation (CPU, 强一致) 是七个独立 SLA + 至少三种硬件类型，每层允许独立扩缩容、独立 A/B、独立模型热加载；把这些塞一起会让 GPU 空转等 CPU。候选一是按 **业务域切分** (Feed / Shop / Story / AR)——界面实体抄到后端、完全忽略硬件资源差异、热门业务与冷门业务 GPU 抢占严重，淘汰。候选二是按 **数据模态切分** (Image-only / Image+Text 多模态 / Video)——对多模态业务合理但把 backbone 与 task heads 打包、仍会让 GPU 推理与 CPU NMS 耦合；数据模态切分更合适的位置是纯 research infra 实验平台。候选三是按 **客户端切分** (Web / Mobile / Native / AR 眼镜)——与本题无关，视觉服务对客户端透明，淘汰；客户端切分更合适的位置是 BFF 聚合层。候选四是按 **任务类型切分** (Classification / Detection / Segmentation 各独立服务)——每任务独立看似干净，但共享 backbone 完全白浪费、每任务复制一份 ViT 推理成本 × 4 不可接受，任务类型切分更合适的位置是早期 MVP 三任务各不共享 backbone 的验证阶段。切换触发：出现新硬件 (AI ASIC / NPU) 维度时再切一刀；业务域 QPS 差距 < 2× 可适度合并。

> **常见追问**:
> 1. "Backbone 与 Task heads 怎么部署？" —— 同一 GPU pod 里用 Triton ensemble、backbone 一次前向输出 feature map、多个 head 并发消费；避免跨网络拷贝 feature tensor。
> 2. "Image Ingester 为什么独立？" —— 图像解码是 CPU/IO-bound、与 GPU 推理资源需求完全不同；放一起会让 GPU 空转等解码，单独 ingester 用 libjpeg-turbo/nvJPEG 跑满 CPU/PCIe 才是最优。
> 3. "Moderation 为什么独立强一致？" —— 审核结论直接影响用户内容可见性 + 广告计费 + 法律合规，必须 ACID 持久化 + 幂等重试；推理链路其他部分全部 eventual。

端到端数据流：客户端上传图 → CDN 就近落 S3 → Image Ingester 写 metadata DB + 发 Kafka 事件 → Preprocessor 消费事件做解码/resize/归一化 + 发下游请求 → Backbone Service (ViT/ResNet) GPU 批推 → Task-head Services (classification / detection / segmentation / embedding / NSFW) 并发消费 feature → Post-processor 做 NMS / 掩码合并 / Top-K → 结果写回 metadata DB + embedding 写 HNSW 索引 + 审核命中的图送 Moderation 服务人审队列；同时曝光/点击等用户行为事件 (id=90 推荐侧) 通过 Kafka 流回 Feature Store 做准实时特征更新。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——GPU 推理挂了走 CPU ResNet-50 降级 + 小流量；HNSW 挂了走类目倒排召回；Moderation 挂了走保守策略 (待审状态) 防误发；完整链路允许 2 层同时降级仍返回可用结果。

这一节 takeaway：CV 系统的服务边界不是业务边界而是 pipeline 层 + 硬件资源 + SLA 边界；任一层必须自带 fallback，Moderation 强一致与 GPU 推理资源隔离是整条链路两大耦合点。

## 4. Deep Dives

这一节把 CV 核心四块 (Ingestion & Preprocessing / Backbone & Task Heads / Detection & Segmentation / Edge Deployment & Compression) 逐一展开，每一块给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"视觉系统每层选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章编排顺序与在线 serving 数据流一致：Ingestion 在前、Backbone 在中、Detection/Segmentation 在核心、Edge Deployment 收尾。

### 4a. Image Ingestion & Preprocessing (图像摄取与预处理)

图像摄取与预处理的本质是把原图从客户端/CDN 高效送进 GPU 显存、追求 JPEG 解码 p99 < 30ms、resize 归一化 < 10ms、整段 CPU-GPU 带宽打满。视觉系统里这一段常被忽视，但其实 30-40% 的 p99 预算都在这里——backbone 推理再快，解码瓶颈也会把整体拖慢。

图像解码/预处理栈我选 **NVIDIA DALI + nvJPEG GPU 解码 pipeline**，因为它把 JPEG 解码直接搬到 GPU、避免 CPU→GPU 拷贝、DALI graph 把 resize/normalize/crop 融进同一个 CUDA stream、单 GPU 吞吐 > 3000 img/s、与 Triton 推理零拷贝对接。候选一是 **Pillow-SIMD + torchvision transforms**——PyTorch 生态原生、调试友好，但纯 CPU 解码 + CPU→GPU 拷贝、吞吐约 DALI 的 1/5、GPU 等解码是常见反模式，Pillow-SIMD 更合适的位置是训练离线数据预处理或低 QPS prototype，所以不用。候选二是 **OpenCV + libjpeg-turbo (CPU)**——libjpeg-turbo 用 SIMD 加速解码、OpenCV 算子丰富，但仍是 CPU-only、大 batch 时 CPU 核心抢占、无法与 GPU 推理共享 CUDA stream，OpenCV 更合适的位置是预处理逻辑极复杂或算子 DALI 不支持的场景，淘汰。候选三是 **FFmpeg + libvips**——libvips 对大图 streaming 处理内存友好，但仍 CPU-only、与 GPU 推理 pipeline 割裂，libvips 更合适的位置是超大图 (> 100MP) 或 DZI 切片场景。候选四是 **AWS Lambda 预处理**——serverless 弹性伸缩、按需计费，但冷启动慢、GPU 预处理无法做、跨 cloud-vendor 锁定，Lambda 更合适的位置是低频 + 高峰值的中小流量。切换触发：GPU 成本占比过高时退 libjpeg-turbo CPU-only；预处理逻辑涉及自定义算子 DALI 无法覆盖时用 OpenCV；超大图场景用 libvips。

数据增强策略我选 **Mosaic + Mixup + RandAugment 三件套**，因为 Mosaic 把 4 张图拼接 (YOLO v4 引入) 增强目标尺度多样性、Mixup 线性插值两张图及标签增强分类平滑、RandAugment 自动搜索 14 种增强组合减少手调工作、在 ImageNet/COCO/Open Images benchmark 上均有稳定涨点。候选一是 **AutoAugment**——用 RL 在代理任务上搜索增强策略、理论最优，但搜索成本极高 (数千 GPU 小时)、迁移到新数据集需重搜，AutoAugment 更合适的位置是 Google-scale 资源 + 一次搜索多次复用的旗舰模型，所以不用。候选二是 **CutMix**——把一张图的区域替换到另一张 + 对应标签加权，精度略高于 Mixup 但实现复杂度更高、对 detection/segmentation 标签处理繁琐，CutMix 更合适的位置是纯分类任务且追求 SOTA 的 fine-tuning，淘汰。候选三是 **Random Erasing**——随机遮挡局部区域模拟遮挡场景、对检测 robust，但信号弱于 Mosaic + Mixup 组合、单独用涨点小，Random Erasing 更合适的位置是 Mosaic 的补充而非替代。候选四是 **TrivialAugment**——固定一条简单增强链条、无超参调优，但 benchmark 不如 RandAugment、研究 vs 工业倾向不同，TrivialAugment 更合适的位置是追求极简 + 复现性的学术对比。切换触发：纯分类任务且 Mixup 已饱和时叠 CutMix；资源充足且追求 SOTA 时考虑 AutoAugment；极简 + 可复现场景用 TrivialAugment。

> **常见追问**:
> 1. "JPEG 解码为什么放 GPU？" —— 大 batch 下 CPU 解码成瓶颈、nvJPEG 把解码放 GPU 后 PCIe 只传 encoded 字节、拷贝量减 10×、吞吐提 5×。
> 2. "Resize 要不要保持 aspect ratio？" —— 分类任务中心裁剪即可、检测任务必须保 aspect ratio + padding (letterbox) 否则 bbox 几何失真。
> 3. "训练/推理 preprocess 对齐吗？" —— 必须严格对齐、否则分布漂移；把 preprocess 代码封成库 + 训练/推理共享、CI 测有对 pixel-level equality。

### 4b. Backbone & Task Heads (骨干网络与任务头)

Backbone 选型是视觉系统最关键的分水岭——backbone 决定了后续所有任务头的特征质量、计算成本、训练数据量需求。CV 骨干网络演化链条 CNN (ResNet → ResNeXt → EfficientNet) → Transformer (ViT → DeiT → BEiT → MAE) → Hybrid (ConvNeXt → Swin → CoAtNet)，核心线索是归纳偏置从强到弱 + 数据效率从高到低 + 全局感受野从局部到全局。

主 backbone 我选 **ViT-Base/16 (Vision Transformer, patch=16)**，因为 ViT 在 ImageNet + 100M+ 内部数据上预训练后精度超过同参数 ResNet-152 约 2%、全局注意力对多任务头共享 feature 表达更强 (分类/检测/分割/embedding 都能受益)、MAE 自监督预训练让 data 稀缺场景也能用、HuggingFace transformers / timm 工具链成熟。候选一是 **ResNet-50**——CNN 归纳偏置强、小数据集效果好、推理快 (A100 batch=1 ≈ 2ms)，但全局感受野不足、在大数据集精度天花板低于 ViT 约 2-3%，ResNet 更合适的位置是训练数据 < 1M、资源受限、或 CPU-only 推理场景，所以不用。候选二是 **EfficientNet-B4**——compound scaling + NAS 搜到的参数/精度帕累托最优、**Depthwise Separable Convolution** (深度可分离卷积) 把标准卷积的计算量降到 1/8 左右、移动端也能跑，但 depthwise-conv 在 TensorRT 里融合效率不如 ResNet、GPU 推理实际吞吐不如其参数规模暗示，EfficientNet 更合适的位置是移动端 + 精度敏感场景，淘汰。候选三是 **ConvNeXt-Tiny**——纯 CNN 精度追平 Swin、保留 CNN 所有硬件友好性、训练 recipe 简单 (7×7 depthwise + GELU + LN)，但在 100M+ 数据上仍不如 ViT-Large，ConvNeXt 更合适的位置是"我要 Transformer 精度但部署全栈 CNN-only"的过渡方案。候选四是 **Swin-Tiny**——shifted window attention 兼顾局部与全局、对 detection/segmentation dense prediction 友好，但工程复杂度高于 ViT + 非标准 attention 实现在 TensorRT 里需要自定义 plugin，Swin 更合适的位置是 detection/segmentation 为主任务的场景。切换触发：训练数据 < 1M 时退 ResNet-50 / ConvNeXt；部署端为移动端时用 EfficientNet / MobileNetV3；主任务为 dense prediction 时迁 Swin。

任务头设计我选 **共享 backbone + 轻量 head 的多任务架构**，因为 backbone 跑一次输出 feature map、多个 head (classification 全连接 / detection YOLO head / segmentation U-Net decoder / embedding pooled vector / NSFW sigmoid) 并发消费、节省 70% 重复计算、Triton ensemble 原生 DAG 调度。候选一是 **任务独立完整模型 (每任务一套 backbone+head)**——训练/部署解耦、各任务可单独调优，但推理成本 × N、GPU 显存/算力浪费，独立完整模型更合适的位置是任务差异巨大 (如医疗影像 vs 自然图像) 或 SLA 要求不同的场景，所以不用。候选二是 **Hard Parameter Sharing MT-Learning**——所有任务完全共享 backbone + 任务头独立、训练时 loss 加权，但跨任务 loss 冲突 (classification 梯度 vs detection 梯度反向) 导致"负迁移"，Hard Sharing 更合适的位置是任务语义高度相关 (分类 + 属性识别)，淘汰。候选三是 **Soft Parameter Sharing (Cross-stitch Networks)**——每任务独立 backbone + 通过 cross-stitch units 交互特征，但参数量接近 N× 独立模型、复杂度高，Soft Sharing 更合适的位置是学术研究或资源充足的精度追求。候选四是 **Mixture-of-Experts (MoE) Backbone**——稀疏激活 experts、按 input 路由、总参数量大但 FLOPs 低，但路由稳定性差 + 训练复杂、工业成熟度低，MoE 更合适的位置是超大规模 foundation model 研究。切换触发：任务间负迁移明显时退 Hard Sharing 改独立模型；资源充足追求精度时评估 Soft Sharing；十亿参数以上 backbone 考虑 MoE。

> **常见追问**:
> 1. "为什么 ViT 需要大数据预训练？" —— ViT 归纳偏置弱 (没有 CNN 的平移等变)、需要从数据里学到空间结构、100M+ 数据量才能把这层不足补上；小数据直接上 ViT 会比 CNN 差。
> 2. "多任务训练怎么平衡 loss？" —— GradNorm / Uncertainty weighting 自动调整每任务 loss 权重、防止某任务梯度 dominate；或分阶段训练 (先分类 + 检测、后加分割)。
> 3. "backbone 更新频率？" —— 季度级大改 (数据积累 + 架构升级)、月级微调 (新类目加入)、周级线上蒸馏回流。

### 4c. Detection & Segmentation (目标检测与语义分割)

Detection 与 Segmentation 是视觉系统的两大 "dense prediction" 任务——不像分类只需输出一个标签、而要对图像每个位置都产生预测。算法选型核心是"精度 × 推理速度 × 训练稳定性"的三角。

目标检测我选 **YOLOv8 (single-stage anchor-free detection)**，因为它 CSPNet backbone + decoupled head + anchor-free 设计让训练稳定性好、单阶段推理延迟低 (A100 FP16 < 10ms)、COCO mAP@[.5:.95] ≈ 53.9 已接近两阶段 SOTA、Ultralytics 工具链工业级、与 TensorRT 导出一键式。候选一是 **Faster R-CNN + ResNet-50 FPN**——两阶段 region proposal + RoI-pooling 精度最高 (COCO mAP ≈ 40)，但推理 40ms+、延迟是 YOLO 的 4×、工业级实时场景不可用，Faster R-CNN 更合适的位置是精度优先 + 实时性不苛刻的场景 (卫星图像、医学影像)，所以不用。候选二是 **DETR (Detection Transformer)**——set prediction 消除 NMS 后处理、端到端可学习，但收敛慢 (需 500 epochs+)、小目标精度弱、生产部署工具链不如 YOLO，DETR 更合适的位置是研究探索或无法容忍 NMS 手动调阈值的场景，淘汰。候选三是 **RT-DETR (Real-Time DETR)**——DETR 改进版 + hybrid encoder、推理速度接近 YOLOv8、精度略高，但工具链年轻度 < 2 年、工业生产案例少，RT-DETR 更合适的位置是团队愿意承担技术债去追 SOTA 的场景。候选四是 **CenterNet / FCOS (anchor-free single-stage)**——anchor-free 简化训练、CenterNet 把目标看成 heatmap 中心点，但 mAP 略低于 YOLOv8 1-2%、社区活跃度低于 YOLO 系列，CenterNet 更合适的位置是学习 anchor-free 原理的教学性实现。切换触发：精度最优 + 实时性不重要时迁 Faster R-CNN；愿意承担工具链风险追 SOTA 时用 RT-DETR；教学/研究场景评估 CenterNet。

NMS 后处理我选 **Soft-NMS (Gaussian weighted)**，因为传统 NMS 硬删除重叠框在密集场景 (人群计数、重叠商品) 会误删真框、Soft-NMS 用高斯函数衰减分数而非删除、mAP 提升 1-2%、实现简单替换 NMS 即可。候选一是 **Standard NMS (hard)**——实现简单、速度快，但在密集场景误删真框、工业使用比例逐年下降，NMS 更合适的位置是稀疏目标场景 + 对 mAP 不敏感，所以不用。候选二是 **DIoU-NMS**——用 Distance-IoU 代替 IoU 考虑框中心距离、在拥挤场景表现好，但计算成本高于标准 NMS、实现复杂度中等，DIoU-NMS 更合适的位置是自动驾驶这类拥挤行人检测场景，淘汰。候选三是 **Matrix NMS (SOLO v2 提出)**——并行化 NMS、GPU-friendly，但精度略低于 Soft-NMS、主要价值是加速，Matrix NMS 更合适的位置是对 NMS 延迟敏感的超大 batch 场景。候选四是 **Set Prediction (DETR)**——彻底去除 NMS、端到端预测，但只在 DETR 系列模型里生效，Set Prediction 更合适的位置是 DETR/RT-DETR 家族内部。切换触发：拥挤场景 (人群/人脸) 升 DIoU-NMS；NMS 本身成为延迟瓶颈时 Matrix NMS；选了 DETR backbone 自动免 NMS。

语义分割我选 **Mask R-CNN + ResNet-50 FPN (instance segmentation)**，因为它在 Faster R-CNN 基础上加 mask head、COCO mask mAP ≈ 37、实例级分割工业标杆、Detectron2 框架生产就绪、与现有 detection pipeline 直接复用。候选一是 **U-Net**——encoder-decoder + skip connection 对医学影像小数据友好，但只能做 semantic segmentation 不能区分实例、对自然场景多实例无能为力，U-Net 更合适的位置是医学影像 / 卫星图像 / 工业缺陷检测的二分类 mask，所以不用。候选二是 **SAM (Segment Anything Model)**——Meta 大规模预训练、zero-shot 分割任意对象、prompt-based 交互，但推理慢 (单图 > 100ms)、计算成本高、更适合交互式标注而非批量生产推理，SAM 更合适的位置是"人标注工具" (auto-labeling 闭环) 或低 QPS AR 应用，淘汰。候选三是 **Mask2Former**——统一 panoptic/instance/semantic 的 Transformer 架构、精度 SOTA，但训练收敛慢、推理成本是 Mask R-CNN 2×，Mask2Former 更合适的位置是学术追 SOTA 或对 panoptic 分割有强需求 (自动驾驶场景理解)。候选四是 **YOLACT**——实时实例分割 (30+ FPS)，但精度比 Mask R-CNN 低 3-5 mAP，YOLACT 更合适的位置是移动端实时 AR 分割。切换触发：医学/卫星单类分割用 U-Net；auto-labeling 闭环用 SAM；需要 panoptic 时迁 Mask2Former；移动端实时用 YOLACT。

> **常见追问**:
> 1. "anchor-based vs anchor-free 怎么选？" —— anchor-based 对小目标 recall 高但调参多 (anchor scale / aspect ratio / IoU 阈值)、anchor-free 省调参但需要更强 backbone；工业新项目优先 anchor-free。
> 2. "NMS 阈值怎么定？" —— 类别相关：人脸 IoU=0.5、商品 IoU=0.45、行人 (密集) 用 Soft-NMS 或 DIoU-NMS；验证集 grid search 找最优。
> 3. "如何处理长尾类别？" —— Focal Loss / Class-balanced Loss 放大少数类梯度、Data Resampling 过采样、或 Decoupled Training 先训练 backbone 后微调 classifier。

### 4d. Edge Deployment & Compression (端侧部署与模型压缩)

端侧部署是 CV 与 NLP 最大的差异点——视觉场景大量需要端侧推理 (手机 AR / 自动驾驶 / IoT 摄像头 / AR 眼镜)，整条模型优化链 (量化 + 蒸馏 + 剪枝 + NAS) 在 CV 更成熟。

服务端推理编译器我选 **TensorRT (NVIDIA)**，因为它对 CUDA GPU 优化最深、算子融合 + INT8 calibration + kernel auto-tuning 三板斧把 ViT-Base 推理从 20ms 降到 5ms、与 Triton 原生对接、PyTorch → ONNX → TensorRT 工具链成熟。候选一是 **ONNX Runtime**——跨硬件兼容性最广 (GPU/CPU/NPU/ARM)、开源社区活跃，但 GPU 上峰值吞吐不如 TensorRT 专精优化、图优化算法较保守，ONNX Runtime 更合适的位置是 multi-backend 混合部署或无法绑定 NVIDIA 栈的场景，所以不用。候选二是 **OpenVINO (Intel CPU/iGPU)**——Intel CPU/iGPU 上 SOTA、量化工具链完善，但 GPU server 场景与 CUDA 割裂、多数 CV 工业部署仍 NVIDIA GPU 占主，OpenVINO 更合适的位置是 Intel CPU-only 数据中心或边缘 x86 场景，淘汰。候选三是 **TVM (Apache)**——auto-tuning 生成特化 kernel、跨硬件后端、编译优化前沿，但学习曲线陡、debugging 工具链弱、大团队维护成本高，TVM 更合适的位置是研究 + 定制硬件后端。候选四是 **JAX/XLA**——Google TPU 生态最优、编译优化深，但 CV 工业部署主流仍 PyTorch + NVIDIA，JAX/XLA 更合适的位置是 TPU-only 栈或纯 research。切换触发：multi-backend 或非 NVIDIA 硬件时迁 ONNX Runtime；Intel CPU-heavy 场景用 OpenVINO；研究/定制硬件评估 TVM；TPU 栈走 JAX。

端侧推理运行时我选 **CoreML (iOS) + TFLite (Android) 双路线**，因为 iOS 必须用 CoreML 才能吃到 Neural Engine (NPU) 的硬件加速、Android 主流设备对 TFLite 驱动支持最好、Apple/Google 官方工具链直接对接训练框架导出。候选一是 **NCNN (腾讯)**——纯 C++ 无依赖、ARM CPU 优化极致，但 NPU 加速支持弱、新算子适配慢，NCNN 更合适的位置是超低端 Android 设备 + 纯 CPU 场景，所以不用。候选二是 **MNN (阿里)**——跨平台 + 支持 OpenCL/Vulkan GPU，但社区规模小于 TFLite/CoreML、工具链成熟度低一档，MNN 更合适的位置是国内 Android 生态 + 阿里系产品栈，淘汰。候选三是 **ExecuTorch (PyTorch)**——PyTorch 官方端侧方案、与训练栈无缝，但工具链年轻度 < 1 年、NPU 支持还在建设中，ExecuTorch 更合适的位置是 PyTorch-only 团队愿意承担早期风险。候选四是 **ONNX Runtime Mobile**——跨平台统一、与服务端对齐，但性能弱于平台原生运行时、NPU 加速需专门 EP，ONNX Runtime Mobile 更合适的位置是 cross-platform SDK 需要统一 API 的场景。切换触发：超低端 Android CPU-only 设备退 NCNN；阿里生态内用 MNN；PyTorch-only 团队评估 ExecuTorch。

量化策略我选 **INT8 Post-training Quantization (PTQ) + 代表性数据集 calibration**，因为 PTQ 不需要重训、部署快、ViT/ResNet 精度损失 < 1%、TensorRT/CoreML/TFLite 全支持、工业 CV 部署默认起点。候选一是 **FP16 (half precision)**——TensorCore 原生支持、精度几乎无损、吞吐翻倍，但模型大小 × 2 vs INT8、带宽/存储成本高、端侧资源紧张时不够，FP16 更合适的位置是服务端 GPU + 对精度极敏感 (医疗/金融) 场景。候选二是 **Quantization-Aware Training (QAT)**——训练时插入 fake-quant 节点、精度损失比 PTQ 小 (尤其 INT4/二值场景)，但训练成本翻倍、部署流水线复杂，QAT 更合适的位置是 PTQ 精度掉太多 + 有训练资源的情况，淘汰。候选三是 **INT4 量化 (AWQ / GPTQ)**——模型体积再缩一半、NPU 上更快，但精度损失明显 + 工具链成熟度低、CV 领域 (相比 NLP) 普及度低，INT4 更合适的位置是超极端端侧场景 + 允许精度妥协。候选四是 **Binary Neural Network (BNN)**——权重二值化极致压缩、CPU-only 也能快，但精度损失巨大 + 只适合少数简单任务，BNN 更合适的位置是学术/极端嵌入式研究。切换触发：PTQ 精度掉 > 2% 时升 QAT；体积必须再缩一半时评估 INT4；纯 FP16 保精度场景维持 FP16。

模型压缩我选 **Knowledge Distillation (KD, 知识蒸馏) 为主 + Channel Pruning 为辅**，因为 KD 用大 teacher (ViT-Large) 指导小 student (ViT-Small / MobileNetV3) 保留 95%+ 精度、通用性最强、与量化正交可叠加；Channel Pruning 砍冗余通道再 fine-tune、在特定硬件 (ARM) 上实测延迟降 20-30%。候选一是 **Layer/Structured Pruning (only)**——砍整层或整块、硬件友好，但精度损失较大 + 需要人工判断哪层可砍，Pruning only 更合适的位置是已有成熟 KD 流程的场景外作为补充，所以不用。候选二是 **Low-rank Factorization**——用 SVD 分解权重矩阵、降参数，但 ViT/CNN 权重矩阵 rank 结构不好、实际加速有限，Low-rank 更合适的位置是 Embedding 层或 FC 层占主导的模型，淘汰。候选三是 **Weight Sharing (HashedNet)**——多个位置共享同一权重、极大压缩，但训练复杂度高、精度损失明显，Weight Sharing 更合适的位置是超极端端侧 + 学术研究。候选四是 **Neural Architecture Search (NAS) for Compression**——自动搜索最优压缩架构、理论最优 (EfficientNet / MobileNetV3 就是 NAS 产物)，但搜索成本极高 (千 GPU 天)、迁移性差，NAS 更合适的位置是有大量资源 + 长期复用的旗舰模型。切换触发：仅限层级压缩的简化场景退 Structured Pruning；Embedding 主导模型评估 Low-rank；超极端嵌入式考虑 Weight Sharing；资源充足的旗舰模型评估 NAS。

视觉搜索评估策略我选 **Recall@K + NDCG + Inference Latency + Coverage 四维评估**，因为 Recall@K 衡量召回质量、NDCG 衡量排序质量 (用户点击/购买作 relevance label)、Latency 是硬 SLA、Coverage 看新商品/长尾能否被召回；四维一起看才能防止"recall 高但长尾全丢"或"NDCG 高但延迟爆"这类局部最优陷阱。候选一是 **Recall@K only**——简单易算，但忽略排序质量 + 延迟 + 长尾，Recall-only 更合适的位置是离线 sanity-check，所以不用。候选二是 **Offline mAP only**——COCO-style 评估全面、学术通用，但与真实用户行为脱节、无延迟维度，mAP 更合适的位置是模型研发阶段的基准对比，淘汰。候选三是 **仅线上 A/B 指标 (CTR / 转化率)**——最真实但反馈慢 (周级)、无法批量对比候选模型、回滚成本高，纯 A/B 更合适的位置是最终决策 gate 而非中间评估。候选四是 **LLM-as-Judge (GPT-4V) 判视觉质量**——把 GPT-4V 当评委判图像输出好坏、0-shot 泛化强，但成本高 (每次评估 $0.01)、存在模型 bias、只适合子采样评估，LLM-as-Judge 更合适的位置是离线 spot-check 或 SFT 数据质量把关。切换触发：研发早期用 mAP 快速迭代；上线前必须跑线上 A/B 落地；对生成/美学质量做评估时叠 LLM-as-Judge。

> **常见追问**:
> 1. "端侧模型多大能跑？" —— iOS NPU 可跑 50MB 量级模型 < 50ms；Android 高端机 TFLite + GPU delegate 30MB < 100ms；低端机需 < 10MB + CPU-only。
> 2. "蒸馏时 teacher 多大合适？" —— teacher 应比 student 大 5-10× (ViT-Large 蒸 ViT-Small / ResNet-152 蒸 MobileNetV3)；差距过大反而蒸不进去 (capacity gap 问题)。
> 3. "PTQ vs QAT 怎么选？" —— 先上 PTQ 看精度、掉 < 2% 就用 PTQ；掉更多就上 QAT；INT4 或二值化直接从 QAT 起。

这一节 takeaway：CV 系统不是一个模型、而是四块 (Ingestion/Backbone/Detection-Segmentation/Edge-Compression) 候选池的组合；每块默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

CV 系统的可靠性不是"整条链路 100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量 + 不误发有害内容"的分层容错。CV 与其它 ML 系统的关键差异在于 Moderation 审核的强一致性——漏审一条儿童不宜/血腥/仇恨内容直接对应法律/监管风险与平台下架风险。

监控策略我选 **四象限监控 + 分层 SLO**，因为系统/模型/业务/实验四个维度要分开看、分层 SLO 让降级决策可编程。系统层对接 **Prometheus** + Grafana 采集 p99 延迟、GPU utilization、error rate、图像解码失败率；模型层引入 **Evidently** 或 **Arize** 采集分类分布漂移、mAP slice-level 变化、embedding 退化 (cos sim 飘离基线 > 0.1)、校准比 drift、对抗样本检出率；业务层接入内部 BI 看视觉搜索 CTR、商品发现率、审核准确率/召回率；实验层采集分桶平衡、Sample Ratio Mismatch、novelty effect。候选一是 **Datadog 单栈统一中台**——工具链简化但跨维度语义损失、模型漂移细节看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize 独立 ML 监控平台**——ML 专用指标全、SHAP 解释内嵌，但与系统监控割裂、告警链路双头，Arize 更合适的位置是模型 ops 团队独立于平台团队时，淘汰。候选三是 **Fiddler 独立 ML 监控平台**——可解释性专精、公平性审计完整，但与开源 Prometheus 生态整合成本高、许可证费用贵，Fiddler 更合适的位置是强合规场景 (金融/医疗)。候选四是 **自建 full-stack 监控**——灵活度最高但研发成本巨大，自建更合适的位置是 FAANG 规模深度定制。切换触发：模型漂移成为核心故障源时补 Arize；团队规模 > 100 MLE 时考虑自建核心监控栈；对抗攻击/对抗样本频发时单独接 FoolBox + Adversarial monitoring 模块。

降级预案：GPU 推理挂了 fallback 到 CPU ResNet-50 + 采样推理；backbone 挂了 fallback 到缓存上次 embedding + 类目/规则打标；HNSW 索引挂了 fallback 到类目倒排召回；Moderation 挂了走保守策略 (标记为待审 + 不对公发布) 防误发；图像解码失败走缩略图兜底 + 异步重试。对抗鲁棒性方面，**Adversarial Training** (对抗训练) 把 PGD 生成的对抗样本加入训练集提升模型鲁棒性；**Input Transformation Defense** (输入变换防御) 如 JPEG 压缩 + 随机 resize 在推理前打断对抗扰动的频域信号；**Detection-based Defense** (检测式防御) 用独立检测器识别对抗输入并走保守路径。隐私合规方面，**General Data Protection Regulation** (GDPR, 通用数据保护条例) 与 **California Consumer Privacy Act** (CCPA, 加州消费者隐私法) 要求脱敏 + 用户 opt-out；人脸识别类场景必须接人脸/生物识别专门合规流 (Illinois BIPA 等州法)、未成年人图像需要 COPPA 特殊处理；**Federated Learning** (联邦学习) 与 **Differential Privacy** (差分隐私) 让部分端侧场景无需上传原图、只传梯度/embedding。每条 fallback 路径必须独立演练、月度 game day 强制跑一次、漏审/误审事故 PIR 48h 内出。

这一节 takeaway：reliability 不在单点高可用而在分层可降级 + Moderation 强一致 + 对抗鲁棒性；四象限监控 + 每层独立 fallback + 隐私合规三者缺一不可。

## 6. Summary & Tradeoffs

本题核心 takeaway 是 CV 系统的"精度 × 延迟 × 部署端"三角思维：backbone 选型、任务头共享、端/云拆分、量化蒸馏策略必须在同一条选型链上联动推导，不能单点最优。服务端推理默认 Triton + TensorRT、backbone 默认 ViT-Base (大数据场景) / ResNet-50 (小数据场景)、检测默认 YOLOv8 + Soft-NMS、分割默认 Mask R-CNN、embedding 默认 HNSW sharded、端侧默认 CoreML/TFLite + INT8 PTQ + KD 压缩。模型演进链条 ResNet → EfficientNet → ViT → ConvNeXt → Swin；检测演进链条 Faster R-CNN → SSD → YOLO v1-v8 → DETR/RT-DETR；分割演进链条 FCN → U-Net → Mask R-CNN → SAM/Mask2Former。

三个最常被错答的 tradeoff：一是"ViT 还是 ResNet 做 backbone"——数据量 > 10M 且预训练成熟时 ViT 优、< 1M 数据或 CPU 部署时 ResNet 优，不是谁更先进而是数据量与部署端的 match；二是"端侧推理还是云端推理"——延迟 < 50ms + 隐私敏感走端侧、精度优先 + 大模型走云端，Tesla 这种 safety-critical 场景必须端侧兜底；三是"训练用 mAP 还是 Recall@K"——mAP 是学术通用但与工业指标 (CTR / 转化率 / 审核准确率) 脱节、Recall@K + 业务指标双跟踪才有落地意义。长期优化依赖**Data Flywheel** (数据飞轮)：部署模型 → 用户反馈 + 主动学习 (**Active Learning** 选最不确定样本) + 自动标注 (**Auto-labeling** 用大模型给小模型打伪标) → 人工复核困难样本 → 加入训练集重训 → 部署更强模型；Tesla 自动驾驶全球车队、Meta 审核数据回流都是这条飞轮的落地。

工程 vs 建模的决策拉锯主要在三处：一是推理编译在 TensorRT 与 ONNX Runtime 之间取舍——峰值吞吐 TensorRT 优、multi-backend 兼容 ONNX 优；二是端侧运行时在 CoreML/TFLite 与跨平台框架之间取舍——原生 NPU 加速 vs 统一 API；三是压缩策略在 KD 与 Pruning 之间取舍——通用性 KD 优、特定硬件 Pruning 优。选型的真正判据不是"谁更先进"，而是"当前业务的 QPS、硬件栈、数据规模、延迟预算落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："你的检测模型上线后 mAP 涨了但实际业务 CTR 跌了，怎么办？"——这是典型离线指标与线上指标不一致的失败模式。答案思路：一是排查 slice-level 性能 (热门类目/冷门类目/新类目分别看 mAP 变化)、二是检查 Calibration 是否漂移 (mAP 涨但置信度分布变了导致下游排序失真)、三是做 interventional A/B 看 detection 输出变化对用户交互链路 (点击/收藏/购买) 的因果影响、四是把业务指标作为核心 SLO 而非 mAP 单指标。

第二题："如何构建对抗鲁棒的审核系统？"——对抗攻击是内容审核的核心威胁。答案思路：一是 **Adversarial Training** 基于 PGD/FGSM 生成对抗样本加训练集、二是 **Input Transformation Defense** 推理前叠 JPEG 压缩 + 随机 resize 打断对抗扰动、三是 **Detection-based Defense** 独立检测器识别对抗输入走保守路径、四是多模型集成 (ResNet + ViT + ConvNeXt 投票) 让攻击者很难同时骗过多个架构、五是人审闭环兜底 (置信度低的必人审)。

第三题："Pinterest Lens / Google Lens 这类以图搜图怎么设计？"——经典视觉搜索问题。答案思路：一是 Two-Tower 视觉 embedding 模型 (CLIP / SigLIP / EVA-CLIP 作骨架、对比学习训练)、二是 HNSW sharded 索引 (100B 级向量) + 类目倒排硬过滤、三是二阶段 coarse-to-fine (ANN 粗召 1000 → cross-encoder 精排 50)、四是跨域泛化 (自然图 → 商品图的 domain shift、需要 domain adaptation 或商品侧 synthetic augmentation)、五是**评估**以 Recall@1/5/10 + 点击/购买 CTR 双跟踪为核心。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) 200ms 端到端延迟分配到 Decode / Preprocess / Backbone / Heads / Post-process 五段的预算分摊；(2) 每层默认模型与它的 3 个候选 + why-not；(3) ViT vs ResNet vs EfficientNet vs ConvNeXt vs Swin 五种 backbone 的数据效率/硬件友好性/精度三角对比；(4) YOLOv8 vs Faster R-CNN vs DETR vs RT-DETR 四种检测器的精度/延迟/训练稳定性对比；(5) Mask R-CNN vs U-Net vs SAM vs Mask2Former 四种分割方法的适用场景；(6) TensorRT vs ONNX Runtime vs OpenVINO vs TVM 四种推理编译器的切换条件；(7) INT8 PTQ vs QAT vs FP16 vs INT4 四种量化策略的精度/速度/体积对比；(8) KD vs Pruning vs Low-rank vs NAS 四种压缩方法的适用场景与正交性；(9) 对抗鲁棒性 Adversarial Training / Input Transform / Detection-based / Ensemble 四条防御路径的 tradeoff；(10) Data Flywheel 里 Active Learning + Auto-labeling + 人审闭环的协作范式。十个都能答对就可以去白板了。
