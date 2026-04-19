# Generative AI Systems (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个生成式 AI 系统"——ChatGPT 风格对话、Midjourney 风格文生图、GitHub Copilot 风格代码补全、Sora 风格文生视频、Jasper 风格营销文案都能套。与 id=90 Recommendation Systems 讲"多阶段漏斗排序范式"、id=91 Ads & Click Prediction 讲"三方博弈 + 拍卖经济学"不同，本题的重心是**开放输出 + 生成质量 + 推理成本 + 安全对齐的四方拉锯**：输出没有唯一 ground truth、评估方法本身就是系统设计的一部分、单次推理成本比判别式 ML 高 3-4 个数量级、且滥用/越狱/幻觉的风险触及法律合规红线。本题不是"调一个 LLM API"，而是"能把 Router / Safety / Retrieval / Generation / Post-processing / Billing 这六条链路与推理栈的 inference engine、KV cache、quantization、speculative decoding、RAG、agent framework 选型摆成一个能过面试的工具箱"。考官会盯着三个分水岭：一是首 token 延迟 (**Time To First Token**, TTFT) p99 < 1s 与 token 间隔 p99 < 50ms 的推理优化组合；二是 RAG vs 长上下文 vs 微调三条知识注入路径的 tradeoff；三是越狱/幻觉/有毒输出的多层防御设计。答不清楚这三点就只能拿到 L4。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=90 Recommendation Systems](/kg?node=n90)、[id=198 Real-Time Recommendation System](/kg?node=n198)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问这五元组) 是本题所有 deep dive 的评分标尺。再读 id=90 的理由是：那篇把召回/粗排/精排/重排与特征工程讲过一遍、本题复用"多路召回 + 融合"范式做 RAG 检索。最后读 id=198 的理由是：那篇的部署数字 (100M DAU / 70K QPS / 350K ranking invocations) 与本题 ChatGPT-scale 生成式场景的 1M 并发连接、100K tokens/s 聚合解码吞吐、数 PB 训练语料属于同量级。本题读者应对 **Transformer** (注意力自回归骨架)、**Large Language Model** (LLM, 大语言模型)、**Approximate Nearest Neighbor** (ANN, 近似最近邻)、**Reinforcement Learning from Human Feedback** (RLHF, 基于人类反馈的强化学习)、**Retrieval-Augmented Generation** (RAG, 检索增强生成) 这些概念有基础认识，否则推理优化与知识注入环节容易卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节不是"把产品经理的话抄一遍"，而是把五个必问 (规模、读写、延迟、一致性、跨地域) 答清楚，每一个答案都会在后面某个架构决策里被引用。目标是离开这一节时，面试官能预判到"这套系统的瓶颈落在 GPU 推理显存与 KV cache 容量、强一致只出现在计费扣费一瞬、跨 region 不做同步 KV cache 同步只做异步归因"。

**Functional requirements (功能需求)** 主流程是用户 prompt → 安全过滤 → RAG 检索 (可选) → LLM 推理流式解码 → 输出安全分类 → 流式返回用户 → 使用记录计费。辅流程包括对话历史持久化、多轮上下文管理、用户定制 system prompt、工具调用 (function calling / ReAct agent)、多模态输入 (图像/音频)、输出可复制/分享、用户反馈 (点赞/点踩) 回流改进。平台级功能含模型路由 (根据查询复杂度选模型)、语义缓存、批量离线任务 (文档摘要/代码分析)、fine-tuning 自定义模型、审核后台人工标注、API SDK 与速率限制。这些功能归成四组——Routing、Retrieval、Generation、Safety & Billing——后面 deep dive 按这四组展开。

**Non-functional requirements (非功能需求)** 规模取峰值 **1M** 并发连接 (ChatGPT 高峰量级)、聚合解码吞吐 **100K tokens/s**、单用户请求平均 500 input tokens + 500 output tokens、日均 10B tokens generated；延迟端到端 TTFT p99 < **1 秒** 是流式对话最硬的数字、inter-token p99 < **50ms** 保证顺滑阅读体验、简单请求端到端 < 3 秒、复杂 agent 任务可到 30 秒但必须流式反馈中间步骤；一致性除计费扣费与 fine-tuning job 创建强一致外其他 eventual (对话历史最终一致允许秒级延迟、使用统计允许分钟级)；可用性月度 99.9% 即约 45 分钟/月 downtime budget；新鲜度新文档接入 RAG 10 分钟内可检索、新微调模型分钟级可切换。

**Out-of-scope (排除项)** 基础模型预训练 (假定模型已训好、本题只做 serving 与 post-training)、多模态图像生成流水线的底层扩散模型训练 (**Diffusion** 部分作为子专题只讲 serving)、端上小模型独立分发 (另开)、AI 声音克隆/换脸的伦理与版权专题、跨国数据主权合规的完整法律流程。排除不是"忽略"而是主动声明——面试官问基础模型预训练时我知道这超范围、可以明确"预训练是 $10M+ 8 周级的专题，此处假定 checkpoint 已就绪"。

**必问五问的本题答**：Q1 规模 并发=1M、聚合吞吐=100K tokens/s、日均 10B tokens；Q2 读写比 读远大于写——RAG 每请求 10+ 向量查询 + 20+ document fetch，写只有对话历史 + 使用日志；Q3 延迟 TTFT p99 < 1s + inter-token p99 < 50ms 是整篇最硬的数字；Q4 一致性 计费与 fine-tuning 强一致、其他 eventual；Q5 地域 多 region active-active、KV cache 本 region 独立、跨 region 走异步归因与对话历史最终一致。这五个答案是后面每一节的锚点。

这一节 takeaway：所有后续决策从这五问推出，TTFT p99 < 1 秒与 GPU 显存/KV cache 预算是两个最硬的约束，任何建模与 serving 选型都要反向追溯到"因为需求里说过……"。

## 2. Capacity Estimation (5m)

容量估算这一节的目的不是炫耀算术，而是给后面每一个推理栈与基础设施决策找实在的瓶颈锚点——哪条路径是真有压力、数字背后绑着哪个技术拐点。我按 GPU 显存 → KV cache → RAG 向量库 → 事件总线 → 训练语料五条链路走一遍，每一段除了给数字还给出对应的选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### GPU 推理显存 (70B 模型 × FP16 = 140GB)

70B 参数模型 FP16 占 140GB 显存、单卡 A100-80GB 放不下必须 2 卡 **Tensor Parallelism** (张量并行) 或量化；聚合 100K tokens/s × 单 token 2×param FLOPs ≈ 14 PFLOPs/s 推理算力需求、按 A100 312 TFLOPs/s (FP16 Tensor Core) 算理论下限 45 卡 + 实际留 3× headroom 约 135 卡集群。

推理引擎我选 **vLLM**，因为 PagedAttention 把 KV cache 分页化 + Continuous Batching (连续批处理) 让 GPU 利用率从 30% 冲到 80%、与 HuggingFace 生态零缝对接、开源迭代最快、社区 issue 响应成熟。候选一是 **TensorRT-LLM** (NVIDIA)——融合 kernel 粒度更细、单请求延迟比 vLLM 低 10-15%、FP8 支持原生，但编译流程复杂、每换模型要重新生成 engine、开发迭代慢，TensorRT-LLM 更合适的位置是模型稳定 + 单延迟极致优化的场景 (金融低延迟对话/专用 API)，所以不用。候选二是 **SGLang**——RadixAttention 做前缀缓存共享、对 agent/工具调用场景 prefix reuse 命中率高、结构化输出 (JSON schema) 原生支持，但生态比 vLLM 小、运维工具链不成熟，SGLang 更合适的位置是 agent workflow 占比 > 50% 的工具调用密集场景，淘汰作主引擎。候选三是 **llama.cpp**——CPU/Metal/CUDA 多后端、端上推理最强、GGUF 量化格式灵活，但 GPU 并发吞吐远低于 vLLM、batching 弱，llama.cpp 更合适的位置是端侧或单机小规模推理，淘汰。候选四是 **Hugging Face TGI** (Text Generation Inference)——生产级成熟、企业支持好，但吞吐比 vLLM 低 20-30%、社区迭代比 vLLM 慢，TGI 更合适的位置是 HF 栈深度绑定的团队。切换触发：当 agent workflow + prefix cache 命中率 > 40% 时叠 SGLang 做子集路径；模型锁定且追求极致延迟时评估 TensorRT-LLM。

> **常见追问**:
> 1. "为什么 vLLM 比传统 batching 高 3 倍吞吐？" —— Continuous batching 允许每个时间步动态替换已完成序列、避免短请求卡在长请求尾部、GPU 无空转；PagedAttention 把 KV cache 按 block 分页允许不同长度序列共享显存。
> 2. "70B 模型两卡 TP 通信开销大吗？" —— 每层 all-reduce 约 2 × hidden × batch / bandwidth，NVLink 600GB/s 下单步 0.2-0.5ms、相对 token 解码 20-30ms 占比 < 5%；跨节点 TP 要避免。
> 3. "如何做模型热切换？" —— vLLM 支持 LoRA adapter 动态加载、base model 不动、每用户切 adapter 零冷启；全模型切换用蓝绿部署双份 GPU 池。

### KV Cache 与长上下文 (100K token 序列 = 40GB per user)

70B 模型 80 层 × 8K hidden × 2 (K+V) × 2 bytes (FP16) × 100K tokens ≈ 40GB KV cache per 100K-token 会话；1M 并发 × 平均 4K token 活跃 session ≈ 1.6TB 聚合 KV cache 需求必须跨 GPU 分页管理。

KV cache 管理我选 **PagedAttention** (vLLM 默认)，因为分页粒度 16 token/block 显存碎片率 < 5%、复制 copy-on-write 支持 beam search / parallel sampling 共享前缀、已被工业验证 > 12 个月。候选一是 **RadixAttention** (SGLang)——前缀树共享 prefix KV、system prompt / few-shot example 跨请求复用命中率 60-80%、agent 场景尤其划算，但实现复杂、需要改推理引擎、与 vLLM 不兼容，RadixAttention 更合适的位置是前缀重复率极高的场景 (system prompt 固定 / RAG 固定 instruction)，保留作备选。候选二是 **Block-sparse Attention** (块稀疏注意力) / FlashAttention-2——不是 cache 管理而是 attention kernel 优化、与 PagedAttention 正交可叠加、降 prefill 延迟 2×，但不解决 cache 容量问题，Block-sparse 更合适的位置是 prefill 延迟瓶颈场景，不替代 paging。候选三是 **Vanilla Contiguous KV Cache**——连续预分配、实现最简，但显存碎片率 60-80%、长序列 OOM 频发，Vanilla 更合适的位置是研究 baseline 或单 session 独占 GPU 场景，所以不用。候选四是 **CPU Offloading** (将冷 KV 下沉到 CPU/NVMe)——显存压力立减但 token 延迟炸到 500ms+，CPU offload 更合适的位置是极长上下文 (> 1M token) 的 batch 离线任务。切换触发：prefix 重用率 > 40% 时试 RadixAttention；单 session > 200K token 时评估 CPU offload 做 tier 2。

> **常见追问**:
> 1. "100K token 上下文 TTFT 能做到多少？" —— Prefill 阶段 attention 是 O(n²)、100K token 单卡约 15-25 秒；要做到 < 3 秒必须 sequence parallelism + FlashAttention-3 + 多卡分片，或降到 32K 上下文 + RAG 动态注入。
> 2. "session 级 KV cache LRU 淘汰策略？" —— 空闲 > 5 分钟的 session KV 下沉 CPU 内存、> 30 分钟 evict 到 Redis snapshot、新请求若命中远端 snapshot 则流式重建前缀；命中率监控 > 70%。
> 3. "同一 system prompt 跨用户能共享吗？" —— PagedAttention 不能跨 session 共享 (安全隔离)、RadixAttention 可按 prefix hash 共享但需合规审核确认 prompt 无用户数据；生产默认不跨用户共享。

### RAG 向量库 (1B documents × 1536-dim embedding = 6TB)

企业知识库 1B chunks × 1536-dim × 4 bytes (FP32) = 6TB、量化为 FP16 降到 3TB、PQ 压缩到 512GB；每请求 top-20 召回 + 3-5 chunk 入 context、100K QPS 向量查询 p99 < 50ms。

向量库我选 **Milvus**，因为分布式部署 K8s-native、HNSW + IVF-PQ 双索引、filtered search 支持 metadata 预过滤、1B 级规模工业案例多 (Zilliz/蚂蚁/字节都有线上)。候选一是 **Pinecone** (托管)——零运维 + auto-scaling + 企业 SLA，但单位价格 5-10× Milvus 自建、向量维度受限 (最大 2048)、锁定云厂商，Pinecone 更合适的位置是小团队 MVP 或强合规托管场景，所以不用。候选二是 **Weaviate**——GraphQL API + 模块化 embedder 集成 + hybrid search 内置 BM25，但 QPS 头部案例少于 Milvus、Java/Go 混合栈运维复杂度高，Weaviate 更合适的位置是 schema 复杂 + 混合检索需求强的团队，淘汰作主库。候选三是 **FAISS** (库形式)——单机 QPS 最高、算法最全，但不带分布式 + 不带 metadata filter + 不带 CRUD，FAISS 更合适的位置是离线批量检索或做 Milvus 内核不直接部署。候选四是 **Elasticsearch + dense_vector**——已有 ES 栈可零新增组件、hybrid 搜索原生，但 ANN 性能弱于专用向量库 10-20%、大规模索引占用高，ES 更合适的位置是已有 ES 重度使用且向量只是辅助信号的场景。切换触发：规模 > 10B documents 时评估自建向量引擎；hybrid BM25+vector 成主检索信号时迁 Weaviate/ES。

### 事件总线与对话历史 (10B tokens/day × 4B/token = 40GB/day)

日均 10B tokens × 平均 4 bytes 压缩后 = 40GB/天生成内容 + 对话元数据 + 使用日志合计约 120GB/天；事件流峰值 100K tokens/s × 4 bytes = 400KB/s token 事件、加上元数据约 5MB/s；对话历史 1B messages 存储总量 2TB/年。

事件总线我选 **Kafka 64 partitions**，因为单 partition 20-30MB/s 合计 1.5GB/s 留 300× headroom、exactly-once 语义保计费准确、消费组隔离训练 sink 与实时分析、与 Flink 原生集成。候选一是 **Apache Pulsar**——多租户 + tiered storage 把冷日志下沉 S3、无缝对接 Functions，但运维复杂度高、社区规模弱于 Kafka，Pulsar 更合适的位置是强多租户隔离的 SaaS 平台场景，所以不用。候选二是 **AWS Kinesis**——托管省运维、Lambda 无缝整合，但单 shard 上限低、跨云锁定、成本 3× Kafka 自建，Kinesis 更合适的位置是纯 AWS Lambda 栈，淘汰。候选三是 **NATS JetStream**——轻量 + at-most-once 配置灵活、云原生部署简单，但生态工具链与 Flink/Spark 集成不如 Kafka 成熟，NATS 更合适的位置是边缘场景或微服务事件总线而非生成式 AI 主流水线。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈 serverless 化时评估 Kinesis。

### 训练语料与微调存储 (预训练 10TB token / 微调 100GB/day)

基础模型语料 10TB token = 约 40TB 原始文本、微调数据日增 100GB (RLHF 偏好对 + SFT pair)、checkpoint 单份 140GB × 保留 30 版 = 4.2TB。

训练语料存储我选 **S3 + Parquet + Iceberg**，因为 S3 字节成本 $0.023/GB/月、Parquet 列存压缩比 4-5:1、Iceberg time-travel 让 RLHF 偏好对训练可复现、与 Spark/Ray 预处理管线兼容。候选一是 **HDFS**——批处理适合但 NameNode 单点运维重、云原生方向工具链转 S3，HDFS 更合适的位置是私有云强合规场景，所以不用。候选二是 **GCS + BigQuery**——GCP 原生 + 分析能力强，但与 PyTorch 训练栈 connector 一层、跨云锁定，GCS 更合适的位置是 Google Cloud 全家桶团队，淘汰。候选三是 **Delta Lake**——ACID + schema evolution，但 Databricks 绑定较重，Delta Lake 更合适的位置是 Databricks 深度用户。切换触发：跨团队要强 ACID 写入时迁 Delta Lake；合规要求独立数据域时自建元数据层。

这一节 takeaway：70B × FP16 = 140GB 推出 vLLM + 多卡 TP、KV cache 40GB/100K-token 推出 PagedAttention、1B embedding 推出 Milvus、10B tokens/day 推出 Kafka 64p、10TB 语料推出 S3+Iceberg——这五个数字把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按生成流水线层 + SLA + 一致性要求切、而不是按业务域切；数据怎么流——端到端 Router → Safety → Retrieval → Generation → Post-processing → Billing 的管线要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：Generation 的 GPU 层和 Safety 的 CPU 层不能混部署、Billing 强一致性必须独立、RAG 向量查询的 50ms 预算要和 Generation 的 TTFT 预算错开。

服务拆分策略我选 **按生成流水线层 + SLA + 一致性切分**，因为 Router 1ms (CPU 路由决策) / Safety 10ms (CPU/小模型分类) / Retrieval 50ms (向量查询) / Generation TTFT 1s + 50ms/token (GPU 推理) / Post-processing 10ms (安全 + 脱敏) / Billing 5ms (强一致扣费) 是六个独立 SLA + 两种一致性要求，每层允许独立扩缩容、独立 A/B 分流、独立模型热加载；把这六层塞一个 "GenAI Service" 会出现任一层流量飙升把整个服务打崩的级联故障。候选一是按 **业务域切分** (User / Conversation / Document)——界面实体抄到后端、完全忽略 GPU vs CPU 资源与 SLA 差异，GPU 推理与 CPU 安全过滤放一起互相拖垮，淘汰。候选二是按 **模态切分** (Text / Image / Audio)——模态确实需要不同推理栈但 Router/Safety/Billing 三层完全可共用、按模态切分会造成基础设施重复建设，模态切分更合适的位置是已有成熟文本栈再扩展多模态的阶段。候选三是按 **客户端切分** (Web / Mobile / API)——广告服务对客户端透明、本题同样不按客户端切，淘汰。切换触发：当多模态成为主流量 (> 30%) 时在 Generation 内部按模态子切；当某层流量下降到与邻层差距 < 2× 时可合并省运维。

> **常见追问**:
> 1. "Router / Safety 可以合并吗？" —— 不合适；Router 是 1ms 本地逻辑决策、Safety 是 10ms 带模型推理、共合会把 Safety 的尾延迟传染到每个请求；但 Safety 与 Post-processing 可复用同一套分类器模型 + 不同触发路径。
> 2. "RAG 检索放同步链还是异步预取？" —— 复杂查询同步检索、简单闲聊 (分类器判)直接跳过 RAG 走 LLM 内生知识；异步预取用在 agent 工具调用场景。
> 3. "Billing Service 用什么数据库？" —— 独立强一致服务，PostgreSQL (ACID + row-level locking) 或 CockroachDB (跨 region 强一致)，绝不能放 Redis 或 DynamoDB 最终一致存储。

端到端数据流：用户 prompt 进 API Gateway → Rate Limit + Auth → Router 决定 (模型 size / 要不要检索 / 要不要 agent) → Prompt Safety Classifier 过滤 (越狱 / 有害 / PII) → RAG Retrieval 从 Milvus 取 top-k 文档 + rerank (若 Router 判定需要) → Prompt 组装 (system + retrieved context + user query) → vLLM 推理集群流式解码 → Output Safety Classifier 每 N token 检查 + 违规截断 → Post-processing (PII 脱敏 / 格式化 / 引用回写) → 流式 SSE 返回用户；异步通过 Kafka 记录 token usage → Billing Service 扣费 → 对话历史持久化到 PostgreSQL + S3。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——Retrieval 挂了走纯 LLM 内生知识、Safety Classifier 挂了走规则兜底 + 降级模型 / 拒绝高风险、Post-processing 挂了走粗粒度正则脱敏、Billing 挂了走本地缓存累加 + 事后对账、完整链路允许 2 层同时降级仍返回可用回复。

这一节 takeaway：生成式 AI 系统的服务边界不是业务边界而是生成流水线层 + SLA + 一致性边界；任一层必须自带 fallback，Billing 的强一致性与 Generation 的 GPU 资源隔离是整条链路最大的耦合点。

## 4. Deep Dives

这一节把生成式 AI 核心四块 (Inference Stack / Knowledge Injection / Safety & Alignment / Evaluation & Cost) 逐一展开，每一块给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"生成式 AI 系统每层选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章编排顺序贴合在线 serving 调用顺序：Inference Stack 是底座、Knowledge Injection 决定答案内容、Safety & Alignment 决定答案可上线、Evaluation & Cost 决定答案能否迭代。

### 4a. Inference Stack & Throughput (推理栈与吞吐优化)

推理栈的任务是在 1M 并发连接、100K tokens/s 聚合吞吐下把单用户 TTFT p99 压到 1 秒、inter-token p99 压到 50ms。推理优化的组合拳由 continuous batching + KV cache paging + quantization + speculative decoding 四件套组成，每件都有 2-3× 吞吐或延迟收益、叠加后总体提升 10-30×。

量化方案我选 **INT8 Weight-Only Quantization** (默认基线)，因为权重从 FP16 降到 INT8 显存减半、70B 模型可单卡 A100-80GB + 20GB headroom 放下、质量损失 < 1% MMLU/HumanEval 评测、工业部署最稳。候选一是 **AWQ** (Activation-aware Weight Quantization)——基于激活分布保留 salient weight 的 INT4 方案、显存再降一半、质量损失可控 2-3%，但 kernel 支持比 INT8 弱、vLLM AWQ 分支稳定性略低，AWQ 更合适的位置是显存极紧 (单卡放多模型) 且可接受 2% 质量下降的场景，所以 INT8 作主路径。候选二是 **GPTQ** (Post-Training Quantization)——4-bit 权重 + 校准数据集逐层量化、显存收益同 AWQ、推理 kernel 最成熟，但校准数据选取影响大、部分任务 (数学/代码) 质量损失更明显 3-5%，GPTQ 更合适的位置是对话类任务且校准数据匹配的场景，淘汰作默认。候选三是 **FP8** (NVIDIA H100/H200)——硬件原生支持 + 训练-推理同精度、质量几乎无损、TensorRT-LLM 原生优化，但需要 H100+ 硬件、集群成本高、A100 不支持，FP8 更合适的位置是 H100 全量部署的新集群，保留作升级路径。候选四是 **INT4 Weight + INT8 Activation**——极致量化、显存再降、端侧场景友好，但质量损失 > 5% 对复杂推理任务不可接受，INT4 更合适的位置是端侧 (llama.cpp / mobile) 离线推理。切换触发：集群升级到 H100 时迁 FP8 拿无损加速；显存极紧且允许 2% 质量降时迁 AWQ。

Speculative Decoding (推测解码) 我选 **Medusa** (多头推测)，因为 Medusa 在基座模型上加 3-4 个预测头、自回归预测接下来 3-4 token、基座模型并行验证、零额外 draft model、训练轻量 (1-2 小时微调头)、吞吐提升 2-3×。候选一是 **Draft Model Speculative Decoding** (EAGLE/vanilla)——用小 draft 模型 (1-7B) 预测后大模型验证、实现清晰、吞吐 2-3×，但需额外部署 draft model、显存占用 + 调度复杂、对 prompt 分布敏感，Draft Model 更合适的位置是已有成熟小模型可直接复用的场景，所以不用。候选二是 **Lookahead Decoding**——无需训练 draft/head、利用 n-gram 预测、纯算法改动，但只对代码/重复文本 speedup 明显 1.5-2×、对自由对话场景效果弱，Lookahead 更合适的位置是代码生成/结构化输出密集任务。候选三是 **EAGLE-2** (Extrapolation Algorithm for Greater Language-model Efficiency)——EAGLE 的改进、动态 draft tree、吞吐提升 3-5×，但实现复杂、社区集成成熟度略低，EAGLE-2 更合适的位置是团队有 research 能力自行集成的场景。切换触发：代码/JSON 占比 > 50% 时试 Lookahead；团队 research 能力强且追求极致加速时迁 EAGLE-2。

> **常见追问**:
> 1. "continuous batching 的理论上限？" —— GPU 计算饱和时 (batch > 64)、吞吐接近 HBM 带宽 / token 显存读取 ≈ 2TB/s / 4MB = 500K tokens/s per card 理论上限、实际 50-60% 利用率；量化把 token 显存占用降一半即翻倍吞吐。
> 2. "量化后质量怎么验证？" —— 跑 MMLU (知识) / GSM8K (数学) / HumanEval (代码) / MT-Bench (对话) 四项基准、任一项下降 > 2% 回退；生产再接 LLM-as-judge 抽样监控。
> 3. "Speculative decoding 与 continuous batching 冲突吗？" —— 不冲突可叠加、但调度复杂度上升 2×、实现需谨慎；vLLM 0.4+ 支持 Medusa + continuous batching 联合优化。

多模态 (图像/视频) 生成的 serving 与 LLM 差异大但可共用同一推理栈架构。图像生成扩散模型 (Stable Diffusion / DALL-E / Midjourney) 的架构演进：最初的 **U-Net** 卷积骨干 → **Diffusion Transformer** (DiT, 扩散 Transformer) 用 Transformer 替代卷积、大规模训练可扩展性更好 → **Multi-Modal Diffusion Transformer** (MM-DiT, 多模态扩散 Transformer) 把文本与图像 token 放同一 Transformer 联合处理、Stable Diffusion 3 与 FLUX 采用。核心优化：**Latent Diffusion** (潜空间扩散) 在低维潜空间做扩散大幅减少计算量、**Classifier-Free Guidance** (无分类器引导) 通过 guidance scale $w$ 控制生成与文本条件一致性、**Denoising Diffusion Implicit Models** (DDIM, 去噪扩散隐式模型) 采样把 1000 步推理压到 20-50 步。视频生成 (Sora) 用 **Spacetime Patches** (时空分块) 把视频切成 3D token 序列、Transformer 建模时空关系；挑战在时序一致性、长程依赖、计算成本 (token 数 = 时间 × 空间)。多模态推理栈选型原则与 LLM 类似：batch 化、量化、前缀/prompt 缓存、kernel 融合都可复用；不同点在 U-Net/DiT 的推理 kernel 需要专用融合 (如 FlashAttention 图像版本)。

### 4b. Knowledge Injection & RAG (知识注入与检索增强)

生成式 AI 的"答案内容"由三条路径共同决定：模型参数内生知识、RAG 外部知识、长上下文对话状态。三条路径互补但成本结构不同——内生知识零推理成本但更新周期长 (月级)、RAG 检索成本线性增但可分钟级更新、长上下文无需检索但 prefill O(n²) 延迟炸。选型本质是"每次请求用哪条路"的路由决策。

知识注入主路径我选 **RAG (Retrieval-Augmented Generation)**，因为外部知识可分钟级更新、事实性错误可追溯到具体文档、企业私有知识库无需训练就能接入、成本可控 (向量查询 + context 扩展 < 30% 额外推理成本)。候选一是 **长上下文 In-Context Learning** (100K-1M token)——把全部文档塞进 context、无需向量库、实现简单，但 prefill 延迟随 n² 爆炸 (100K token prefill 15-25s)、KV cache 显存线性增、每请求重复读全库浪费、长上下文 "lost in the middle" 质量衰减，长上下文 ICL 更合适的位置是少量文档 (< 50K token) 且固定重复查询 (前缀缓存命中) 的场景，所以不用。候选二是 **Fine-tuning / Continual Pre-training**——把知识烘进模型参数、推理零额外成本、内生融合最自然，但更新周期长 (训练 + 评估数天)、灾难性遗忘、私有数据训练有合规风险，Fine-tuning 更合适的位置是知识相对稳定且推理延迟极敏感的领域任务 (医疗术语/法律条文)，淘汰作默认。候选三是 **GraphRAG** (图谱检索)——基于实体关系图做多跳推理、适合复杂关系查询，但图谱构建成本高、覆盖窄、工业案例少、Neo4j/TigerGraph 集成复杂度高，GraphRAG 更合适的位置是强关系查询 (客户关系/供应链) 且图谱已构建的场景，淘汰作主路径。候选四是 **Tool Use / Function Calling**——知识通过工具 API 实时拉取 (股价/天气/数据库查询)、信息最新且结构化，Tool Use 更合适的位置是"实时动态信息"而非"静态知识库检索"；两者常共存。切换触发：固定高频 prompt + 小文档集合时试长上下文 + RadixAttention 前缀共享；静态专业领域时微调特定 adapter；实时数据查询叠 Tool Use。

RAG 检索策略我选 **Hybrid Retrieval (dense vector + BM25 sparse + rerank)**，因为 dense embedding 捕获语义相似度、BM25 兜底关键词精确匹配、cross-encoder rerank 提升 top-5 准确率 20-30%、工业最佳实践已稳定 2 年+。候选一是 **纯 Dense Retrieval** (单塔向量)——实现最简单、延迟最低，但对罕见术语 / 专有名词召回弱 (embedding 训练覆盖不足)、BM25 能补的点它补不上，Dense-only 更合适的位置是 query 全部是自然语言对话的聊天场景，所以不用。候选二是 **纯 BM25 / Elasticsearch**——关键词精确匹配强、无需 GPU embedding 推理、成本低，但对同义词 / 语义重述召回弱，BM25-only 更合适的位置是结构化文档检索 (产品目录 / 法规条文) 或作为 dense 的兜底。候选三是 **GraphRAG multi-hop**——已分析过，工业成熟度不够。候选四是 **ColBERT** (Late Interaction Retrieval)——token-level 匹配精度高于 single-vector dense，但索引体积 10-20× + 推理成本高，ColBERT 更合适的位置是 top-100 精排阶段而非召回层。切换触发：罕见专有名词占比 > 30% 时提升 BM25 权重；top-5 准确率成为核心指标时升 ColBERT rerank。

> **常见追问**:
> 1. "chunk size 怎么定？" —— 默认 512 token / overlap 50 token，太小语义不全 / 太大命中精度低；表格/代码用语义分块 (按 markdown heading / function boundary 切)，不机械按长度切。
> 2. "RAG 的 hallucination 怎么控？" —— 强制 grounded generation (prompt 指示"基于提供文档回答、未命中直接说不知道") + 引用回写 (每段答案带文档 ID) + LLM-as-judge 抽样事实性打分。
> 3. "Agent 多步工具调用如何缓存？" —— 工具调用结果走语义缓存 (query-embedding LRU)、同 session 内工具结果 in-memory 直接复用；跨 session 共享需考虑用户隔离。

### 4c. Safety, Alignment & Guardrails (安全、对齐与防护栏)

生成式 AI 的安全防线是多层纵深：**Input Filter** (输入过滤) 做 prompt safety 分类拦截越狱、模型侧 RLHF/DPO 对齐、**Output Filter** (输出过滤) 做 content safety 分类 + NSFW 检测 + 版权检查拦截有害、检索侧 PII 脱敏、**Watermarking** (水印) 在生成内容中嵌入不可见信号追踪来源。任一层失守都可能把平台拖进公关/法律风险。

Safety Classifier 我选 **Llama Guard** (Meta 开源 7B safety 模型)，因为专门针对 safety 场景训练、多分类 (violence / sexual / self-harm / PII / jailbreak 等 14 类)、开源可微调、输入输出双向可用、与 LLM 栈同生态易部署。候选一是 **OpenAI Moderation API**——开箱即用、质量高、持续更新，但闭源不可微调、按次付费长期成本高、合规上数据传给 OpenAI 有审查，Moderation API 更合适的位置是小流量 MVP 或不涉及敏感数据的场景，所以不用。候选二是 **自建 BERT-based classifier**——针对业务场景可深度定制、推理成本低、私有数据可控，但需要标注数据 10万+ 条、多类别覆盖不如预训练 safety 模型，自建 BERT 更合适的位置是领域专用 (金融/医疗) 且有充足标注预算的团队，淘汰作默认。候选三是 **Rule-based + Regex**——零延迟、可解释、规则透明，但对语义变体 / 越狱 prompt 召回弱、只能兜底不能主防，Rule-based 更合适的位置是 Llama Guard 之后的最终兜底层。候选四是 **Perspective API** (Google)——毒性评分成熟、多语言覆盖，但主要针对评论场景毒性、对 LLM 越狱/jailbreak 召回弱，Perspective 更合适的位置是社交评论审核场景。切换触发：私有数据不能出域时自建 BERT；多语言覆盖成为瓶颈时叠 Perspective。

对齐训练方法我选 **Direct Preference Optimization** (DPO, 直接偏好优化)，因为它直接从偏好对 $(x, y_w, y_l)$ 优化 $\pi_\theta$ 与参考模型 $\pi_{\text{ref}}$ 的 log-ratio 差、无需训练单独的 reward model、实现流程比 RLHF PPO 少一半、训练稳定性高、学术与工业 2024 年起已成主流。候选一是 **RLHF PPO** (Reinforcement Learning from Human Feedback with PPO)——经典三阶段 (SFT + RM + PPO)、对齐效果经过 ChatGPT 工业验证、可控性强，但训练基础设施复杂、reward hacking 风险高、RM 质量瓶颈显著，RLHF 更合适的位置是需要细粒度 reward shaping 且基础设施团队成熟的场景，所以不用。候选二是 **RLHF with Constitutional AI** (Anthropic)——AI feedback 替代人类标注 (RLAIF)、可规模化、覆盖广，但宪法设计本身是艺术、跨领域迁移不直接，Constitutional 更合适的位置是 helpful+harmless 双目标复杂度高的前沿研究，淘汰作默认。候选三是 **KTO** (Kahneman-Tversky Optimization)——用单样本 binary feedback (好/坏) 而非偏好对、标注门槛更低，但信号密度低、质量略低于 DPO，KTO 更合适的位置是偏好对标注成本过高的场景。候选四是 **SFT Only** (纯监督微调)——流程最简单、冷启用、训练快，但无法建立"更好于其他回复"的对比信号、易过拟合，SFT Only 更合适的位置是冷启或领域微调的第一阶段、不是最终对齐方案。切换触发：精细 reward shaping 需求时退 RLHF PPO；标注预算极紧时试 KTO；数据量极小时退 SFT。

> **常见追问**:
> 1. "越狱 (jailbreak) prompt 怎么防？" —— 多层防御：Llama Guard 分类 + prompt injection 检测器 (rebuff / promptsafe) + 输出侧再分类 + 定期红队演练；单层防御迟早被绕。
> 2. "DPO 与 PPO 的 β 如何调？" —— β 控制 KL 正则强度，β 小模型漂移大、β 大对齐不足；默认 0.1-0.3、观察 KL divergence 曲线 + 人工评估输出多样性调优。
> 3. "PII 脱敏的时机？" —— Output 生成后 regex + NER 双路 + LLM 二次检查最稳；训练语料预处理阶段也要脱敏避免 memorization。

### 4d. Evaluation & Cost Optimization (评估与成本优化)

生成式 AI 的评估难题是"没有 ground truth"——同一问题多个答案都可能合理、人工评估慢且贵、自动指标 (BLEU/ROUGE) 与用户感受相关性低。评估方案是"多维度组合 + 成本分层"——自动指标做回归检测、LLM-as-judge 做抽样评估、人工 pairwise 做发布门禁。成本优化的核心杠杆是 model routing (按复杂度选模型) + semantic caching (相似 query 复用) + prompt engineering (减少 token)。

评估方法我选 **LLM-as-Judge + 人工 pairwise + Elo 排序** 的三层组合，因为 LLM-as-judge (用 GPT-4/Claude 评分) 做 offline 回归批量评估覆盖率高、人工 pairwise 做线上 A/B 每周抽样保底质量、Elo 排序把多版本模型放 Arena 对打 crowdsource 评估；三者 tradeoff 清楚、成本可控。候选一是 **纯 LLM-as-Judge**——全自动、可扩展、成本低，但评判模型本身 bias 明显 (偏好长答案 / 同风格答案 / 首位答案)、位置偏见需要 swap 验证，LLM-as-judge 更合适的位置是大规模回归测试而非最终发布门禁，所以不作唯一依据。候选二是 **纯人工 annotator**——质量最高、多样本平均可信，但成本 $5-20/条、延迟 48-72h、覆盖率低，人工评估更合适的位置是发布前最终 gate 而非日常迭代。候选三是 **BLEU/ROUGE/METRIC 自动评估**——实现最简、无外部依赖，但与用户感受相关系数低 (< 0.4)、只能做"不崩溃"底线检测，BLEU/ROUGE 更合适的位置是机器翻译等有 reference answer 场景而非开放对话。候选四是 **LMSYS Chatbot Arena Elo** (公开榜)——公众参与覆盖广、真实偏好，但更新慢、自家模型需要上榜、不适合私有业务场景，Arena 更合适的位置是外部公开模型比较。切换触发：偏好对积累 > 100K 时训自建 reward model 替代 LLM-judge；发布频率升高时降低人工抽样密度用 LLM-judge 兜底。

Cost 优化策略我选 **Model Cascade + Semantic Cache + Prompt Compression 三件套**，因为 Model Cascade (简单请求用 7B / 中等用 13B / 复杂用 70B) 节省 40-60% 推理成本、Semantic Cache 对相似 query 复用答案命中率 15-30% 再降成本、Prompt Compression (LLMLingua / selective context) 裁 context 30-50% 降 token 成本。候选一是 **只靠 Quantization 降成本**——显存减半即成本减半，但质量必有损、单策略天花板低 (单次降 2×)，仅量化 更合适的位置是已跑满其他优化后的二阶段。候选二是 **只靠提价转嫁成本**——商业上直接、实施无需研发，但竞品压力 + 用户流失风险，提价 更合适的位置是成本优化完成后的定价层，淘汰。候选三是 **Distillation** (蒸馏)——把大模型能力蒸馏到小模型、小模型推理成本 5-10× 降，但训练成本高、领域泛化弱、质量损失因任务而异，Distillation 更合适的位置是稳定业务场景且训练预算充裕时的长期优化。切换触发：请求分布有明显 query 重复 (> 20% 重复率) 时优先上 Semantic Cache；头部 20% 复杂任务可独立部署大模型集群 + 其余 80% 用蒸馏小模型。

> **常见追问**:
> 1. "LLM-as-judge 的 bias 怎么降？" —— Swap 两个候选位置 × 2 次评估求一致性、用多个 judge 模型投票、避免 judge 和被评模型同系列。
> 2. "Semantic cache TTL 怎么定？" —— 事实类 query (今天天气) TTL = 1 小时、稳定知识 (历史事件) TTL = 7 天、用户个性化 query 不缓存；新鲜度监控命中错误率 < 1%。
> 3. "A/B 测试生成质量怎么设计？" —— 双盲 pairwise + 人均对话轮次 / retention / thumbs-up rate 做主指标、GSM8K / MMLU 做回归保底、避免单指标优化导致过拟合。

这一节 takeaway：生成式 AI 系统不是一个模型、而是四块 (Inference / Retrieval / Safety / Evaluation) 算法候选池的组合；每块默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

生成式 AI 系统的可靠性不是"100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量 + 不把用户数据泄到不该去的地方"的分层容错。生成式 AI 与传统 ML 的关键差异在于输出的开放性——同一失败路径可能被输出表现得不明显 (幻觉/无害回避) 却已违反合规。

监控策略我选 **四象限监控 + 生成质量专项**，因为系统/推理/内容/业务四个维度要分开看、生成质量专项独立于传统指标。系统层对接 **Prometheus + Grafana** 采集 p99 TTFT、inter-token 延迟、GPU 利用率、KV cache 占用；推理层采集 token throughput、batch size 分布、speculative decoding 接受率、量化质量回归；内容层监控输出分类分布 (safety category rates)、PII 泄漏、hallucination rate (LLM-judge 抽样)、refusal rate (over-refusal 是常见坑)；业务层看 session 时长、重试率、人均消息数、thumbs-up/down 比、订阅转化。候选一是 **Datadog APM 单栈统一中台**——工具链简化但跨维度语义损失、生成质量维度看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize / WhyLabs 独立 ML 监控**——ML 专用指标全、embedding drift 分析成熟，但与系统监控割裂、告警链路双头，Arize 更合适的位置是 ML ops 团队独立于平台团队时，淘汰作默认。候选三是 **Fiddler 独立 ML 监控**——可解释性专精 + 公平性审计完整，但许可证费用高、开源生态集成成本高，Fiddler 更合适的位置是强合规场景 (金融/医疗)。候选四是 **自建 full-stack 监控**——灵活度最高但研发成本巨大，自建更合适的位置是 FAANG 规模团队。切换触发：生成质量监控成核心故障源时补 Arize/Fiddler；团队规模 > 100 MLE 时考虑自建核心栈。

降级预案：Generation 主模型挂了 fallback 到次要模型 (70B → 13B) 或同模型备份 region；RAG Retrieval 挂了走纯 LLM 内生知识 + prompt 提示"检索服务暂不可用"；Safety Classifier 挂了启用保守 mode——直接拒绝高风险类别 + 正则兜底；Post-processing 挂了走粗粒度正则脱敏；Billing 挂了走本地缓存累加 + 事后对账。每条 fallback 路径必须独立演练、月度 game day 强制跑一次、safety 事故 PIR 48h 内出。隐私合规方面，对话历史加密存储 + 按用户 opt-out 策略可清除、训练数据 PII 脱敏 + differential privacy 防 memorization 攻击、输出侧 watermarking 追踪 AI 生成内容来源；GDPR 要求的被遗忘权必须支持按用户 ID 级联清除 (含 fine-tuning 训练集中的样本)。

这一节 takeaway：reliability 不在单点高可用而在分层可降级 + safety 强合规；四象限监控 + 每层独立 fallback + 隐私合规三者缺一不可。

## 6. Summary & Tradeoffs

本题核心 takeaway 是生成式 AI 的四方拉锯思维：开放输出、生成质量、推理成本、安全对齐必须在 1 秒 TTFT + 50ms/token 的流式窗口里同时被推理优化与安全管线平衡。推理栈默认 vLLM + PagedAttention + INT8 + Medusa speculative decoding、知识注入默认 Hybrid RAG、对齐默认 DPO、评估默认 LLM-judge + 人工 pairwise + Elo、成本默认 Model Cascade + Semantic Cache。基础架构演进链条 Transformer → decoder-only GPT → MoE → multi-modal；对齐演进链条 SFT → RLHF PPO → DPO → KTO；推理演进链条 static batching → continuous batching → speculative decoding → disaggregated prefill-decode。

三个最常被错答的 tradeoff：一是"RAG 还是长上下文"——不是谁更好，而是知识更新频率 + prefill 成本的 tradeoff，动态知识库 RAG 胜、小固定文档 ICL 胜；二是"DPO 还是 RLHF"——DPO 是默认起点、RLHF 是精细 reward shaping 需求时才上；三是"LLM-as-judge 够不够评估"——不够，必须配人工 pairwise + Elo，judge bias 是真坑。长期优化依赖**评估飞轮**：人工反馈→偏好数据→更好 reward/DPO→更好输出→更多用户→更多反馈；同时警惕"指标过拟合" (优化 MMLU 牺牲对话体验)、"over-refusal" (过度安全导致用户流失)、"hallucination drift" (长尾场景事实性漂移)。

工程 vs 建模的决策拉锯主要在三处：一是推理引擎在 vLLM 与 TensorRT-LLM 之间取舍——灵活度与极致延迟的 tradeoff；二是 safety 在 Llama Guard 与 OpenAI Moderation 之间取舍——开源可控与开箱即用的 tradeoff；三是对齐训练在 DPO 与 RLHF 之间取舍——流程简洁与 reward 细粒度的 tradeoff。选型的真正判据不是"谁更先进"，而是"当前业务的并发量级、知识更新频率、合规强度、评估闭环成熟度落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："你这套系统上线后用户抱怨回答越来越短、越来越保守，怎么办？"——这是典型 over-refusal 问题。答案思路：一是排查 Safety Classifier 阈值是否过严、false positive rate 上升；二是 DPO/RLHF 训练数据是否"refusal 偏好"过多导致模型学会保守；三是 system prompt 是否过度强调 safety 压制有用性；四是 A/B 不同版本看 helpful-harmless tradeoff 曲线、业务侧把 "helpful 且不违规" 作为核心 SLO 而非单维度 safety 得分。

第二题："如何让新文档加入 RAG 后 10 分钟内可被检索到？"——这是向量库实时增量的核心课题。答案思路：一是 Milvus 支持 streaming insert (数据先进可搜内存索引 + 后台合并到持久索引)、10 分钟 SLA 可达；二是 embedding 阶段用 batch 推理 + Kafka 异步管线；三是增量文档需要过 safety/PII 管线才入索引；四是监控 ingest-to-searchable latency p99 + 文档覆盖率。

第三题："1M 并发用户如何规划 GPU 集群？"——这是容量规划的硬题。答案思路：一是聚合吞吐 100K tokens/s ÷ 单卡 500 tokens/s (INT8 + continuous batching + Medusa 后有效吞吐) ≈ 200 卡基础需求；二是高峰/低谷比 3× 留弹性、多 region 独立集群；三是 TP=2 shard 70B 模型、DP 横向扩；四是 KV cache 预算按并发 × 平均 token × 40GB/100K token 估算、留 30% headroom 避免 OOM；五是每 region 需留 20% 冗余容灾、支持 region-fail-over 切换 < 5 分钟。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) TTFT p99 < 1s 与 inter-token p99 < 50ms 的延迟分配到 Router/Safety/Retrieval/Generation/Post-processing 五段的预算分摊；(2) 每层默认模型与它的 3 个候选 + why-not；(3) vLLM / TensorRT-LLM / SGLang / llama.cpp 四种推理引擎的 tradeoff 与切换触发；(4) INT8 / AWQ / GPTQ / FP8 四种量化的切换条件；(5) PagedAttention / RadixAttention / Block-sparse / CPU offload 四种 KV cache 管理策略的适用场景；(6) RAG / 长上下文 / Fine-tuning / Tool Use 四条知识注入路径的 tradeoff；(7) DPO / RLHF PPO / KTO / SFT-only 四种对齐方法的切换条件；(8) LLM-judge / 人工 pairwise / Elo / BLEU 四种评估方法的组合策略。八个都能答对就可以去白板了。
