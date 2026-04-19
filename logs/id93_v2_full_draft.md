# NLP & LLM Systems (L5 Concepts & Design Spine)

这一题的外皮是"给我设计一个自然语言处理生产系统"——客服工单路由、商品评论情感分析、简历实体抽取、搜索查询改写、机器翻译、文档摘要都能套。与 id=97 Generative AI Systems 讲"开放生成 + 推理成本 + 对齐"不同，本题的重心是**编码器 (encoder) 为主的判别式 NLP 流水线 + LLM 作为单点组件的混合系统**：百万 QPS 的工单/评论/搜索 query 实时过编码器模型、单次推理 p99 < 30ms、批量抽取任务下 p99 < 100ms、LLM 只在少量复杂长尾请求触发做 zero-shot / few-shot。本题不是"调一个 LLM API"也不是"搭 ChatGPT 聊天窗"，而是"把 Tokenizer / Encoder / Classifier / Sequence Labeler / MT / Summarization / LLM-fallback 这七条链路按 **Machine Learning Engineer** (MLE, 机器学习工程师) 选型工具箱摆清、让面试官在任意一层深挖都不卡壳"。考官会盯着三个分水岭：一是百万 QPS 下编码器吞吐 + 蒸馏 + 量化组合把 p99 压到 30ms 以内；二是 encoder 判别式 vs LLM 生成式两条路线在分类/NER/MT/摘要每个子任务里的取舍；三是多语言 + 领域迁移 + 标签噪声的长尾问题。答不清楚这三点就只能拿 L4。

## Prerequisites

→ 参见 [id=18 System Design Framework](/kg?node=n18)、[id=97 Generative AI Systems](/kg?node=n97)、[id=89 Search & Retrieval](/kg?node=n89)

先读 id=18 的理由是：L5 范式与 Appendix A.1.v2 Writing Discipline (每个技术选择都要 Pick + ≥3 候选 + why-not + 切换条件 + 常见追问这五元组) 是本题所有 deep dive 的评分标尺。再读 id=97 的理由是：那篇把 LLM 推理栈 (vLLM / KV cache / **Continuous Batching** (连续批处理) / **Time To First Token** (TTFT, 首 Token 延迟) / speculative decoding / Semantic Cache (语义缓存) / RAG 检索 / **Hallucination** (幻觉) 治理 / **Reinforcement Learning from Human Feedback** (RLHF, 基于人类反馈的强化学习) 对齐) 讲过一遍、本题会把它当作"生成式组件"引用但不重复展开。读 id=89 Search & Retrieval 的理由是：召回/精排、**Cross-encoder** rerank 与 query 改写范式直接影响本题"搜索 NLP"子场景的管线拆分。本题读者应对 **Transformer** (注意力自回归骨架)、**Encoder-Only Architecture** (BERT 式双向编码器)、**Tokenization** (分词)、**Named Entity Recognition** (NER, 命名实体识别)、**Sequence Labeling** (序列标注) 这些概念有基础认识，否则 deep dive 4b/4c 环节会卡住。

## 1. Requirements Clarification (5m)

需求澄清这一节的目标是把"NLP 系统"的业务场景锁死、不要跟 id=97 的开放式生成混淆。客服工单路由是 10 分类多标签 + 30ms p99、商品评论情感分析是 3 分类 + 10ms p99、简历实体抽取是 NER 序列标注 + 100ms p99 可批量、搜索 query 改写是短文本 seq2seq + 50ms p99、机器翻译是长文 seq2seq + 500ms p99 可流式、文档摘要是长文 encoder-decoder + 2s 可异步。目标是离开这一节时面试官能预判到"这套系统的瓶颈落在编码器吞吐 + 长尾 LLM 成本 + 多语言标签噪声"。

**Functional requirements (功能需求)** 主流程按用户请求类型分成五条：(a) 短文本分类——query 进 Tokenizer → Encoder → Softmax 头输出类别分布；(b) 实体抽取——长文进 Tokenizer → Encoder → Token-level 标签头 → BIO/Span 解码；(c) 机器翻译——源文进 Tokenizer → seq2seq 解码；(d) 摘要抽取/生成——长文进 Tokenizer → 抽取式或 seq2seq 生成；(e) LLM fallback——置信度低于阈值或 zero-shot 场景由 LLM 统一组件兜底 (指向 id=97)。辅流程包括多语言自动检测路由、领域自适应在线微调、label drift 监控告警、低置信度 case 走人工审核队列。平台级功能含批量离线推理任务 (evening batch 全量语料重标)、A/B 测试框架 (多版本 encoder 灰度)、人工标注工具接入、模型注册表与版本回滚。这些功能归成四组——Preprocessing、Classification/Labeling、Generation (MT+Summ)、Post-processing——后面 deep dive 按这四组展开。

**Non-functional requirements (非功能需求)** 规模取峰值 **2M** QPS 聚合 (客服 500K + 评论 800K + 搜索 500K + 其他 200K)、每 query 平均 128 token 输入、单条短文本分类平均 20 token、长文 NER 平均 512 token；延迟短文本分类 p99 < **30ms**、NER 长文批量 p99 < **100ms**、MT 短句 p99 < **500ms**、LLM fallback 退化到 p99 < **2s** 流式首 token < **300ms**；一致性模型版本灰度必须原子切换、标签定义变更必须强一致广播；可用性月度 99.95% 即约 20 分钟/月 downtime；新鲜度 label 定义变更 1 小时内全集群生效、模型新版本灰度 10% → 100% 不超过 24 小时。

**Out-of-scope (排除项)** 基础模型预训练 (假定 BERT/RoBERTa/T5 checkpoint 已就绪、不讲 10TB 语料 MLM 训练)、ChatGPT 风格开放对话 (指向 id=97)、RAG 知识库检索 (指向 id=97 §4b)、语音识别/语音合成 (ASR/TTS 另开题)、跨模态图文融合。排除不是"忽略"而是主动声明——面试官问预训练时我知道这超范围、可以明确"预训练是 $1M+ 级别的专题、此处假定 checkpoint 已到位只做 serving + 微调"。

**必问五问的本题答**：Q1 规模 聚合 QPS=2M、日均请求 170B、每请求 128 token 均值；Q2 读写比 读远大于写——推理每秒 2M、写只有标注数据 + 反馈日志约 1K/s；Q3 延迟 分类 p99 30ms + NER 100ms + MT 500ms 三条 SLA 错开；Q4 一致性 模型灰度与 label 定义强一致、其他 eventual；Q5 地域 多 region active-active、模型 artifact 同步异步、标注数据统一归仓。这五个答案是后面每一节的锚点。

这一节 takeaway：NLP 系统的主流量是 encoder 判别式、LLM 只在长尾兜底；2M QPS 与 30ms p99 是两个最硬的约束、任何模型与 serving 选型都要反向追溯到"因为需求里说过……"。

## 2. Capacity Estimation (5m)

容量估算这一节的目的是给后面每一个模型与基础设施决策找实在的瓶颈锚点。我按 GPU 推理显存 → Tokenizer CPU → 事件总线 → 特征/标签存储 → 标注数据五条链路走一遍，每一段除了给数字还给出对应的选型块：一个 pick、三个候选 + 逐个 why-not、一个切换触发条件、以及三条最常见的追问。

### GPU 推理显存 (DistilBERT-base × 2M QPS)

DistilBERT-base (66M 参数) FP16 占 140MB 显存、单卡 A10-24GB 可并行 40+ 实例、batch 64 × 128 token 单次前向 8ms；聚合 2M QPS ÷ (batch 64 × 100 QPS/实例) ≈ 300 实例 ≈ 8 卡 A10；若全量 BERT-base (110M) 同配下约需 12 卡、若用 RoBERTa-large (355M) 约 50 卡。NER/MT/摘要各走独立小集群、按任务 QPS 分摊。

推理引擎我选 **NVIDIA Triton Inference Server**，因为 Triton 支持 dynamic batching + multi-model serving + TensorRT / ONNX / PyTorch / TensorFlow 多后端统一接入、企业级监控与 metrics 暴露成熟、与 K8s 原生对接。候选一是 **TorchServe** (PyTorch 官方)——PyTorch 栈零迁移成本、模型封装最简单，但 dynamic batching 成熟度不如 Triton、多模型并发调度弱、企业用量较少，TorchServe 更合适的位置是纯 PyTorch 单模型小规模场景，所以不用。候选二是 **TensorFlow Serving**——TF 生态深度绑定、gRPC 成熟，但 PyTorch checkpoint 要转 SavedModel / ONNX 绕一层、Transformer 生态已转 PyTorch 为主，TF Serving 更合适的位置是 TF2 全量栈的遗留系统。候选三是 **BentoML**——Python 原生灵活、与 MLflow 集成好，但高并发吞吐明显弱于 Triton、GPU dynamic batching 能力浅，BentoML 更合适的位置是中小团队 MVP / 原型阶段。候选四是 **Hugging Face TGI**——transformers 生态最顺、开箱即用，但更聚焦 LLM 生成、encoder 判别式场景吞吐不如 Triton、不适合多任务多模型共置。切换触发：纯单任务单模型时退 TorchServe；已有 TF 全栈时退 TF Serving；LLM fallback 占比超 20% 时引入 TGI 做专用集群。

> **常见追问**:
> 1. "Triton dynamic batching 的参数怎么调？" —— 按模型 p99 目标反推 max_batch_size 与 max_queue_delay，短文本 30ms SLA 下取 batch=64 + delay=4ms，NER 100ms SLA 下 batch=32 + delay=20ms；拿 real trace replay 验证。
> 2. "FP16 转 INT8 什么时候做？" —— Triton + TensorRT INT8 校准可把吞吐再升 1.5-2×、但需要校准数据集 (1K-10K 样本) 与 per-tensor scale，评估集精度下降 < 1% 才上线。
> 3. "多模型共置 GPU 显存够吗？" —— 单 A10-24GB 可同时挂 DistilBERT (140MB) + RoBERTa-base (500MB) + 轻量 NER head + reserve 2GB PagedAttention for seq2seq；超过 20GB 就拆卡分组。

### Tokenizer CPU (2M QPS × 128 token)

Tokenizer 每 query 128 token × 2M QPS = 256M token/s；Rust-based Tokenizers 单 CPU core 约 500K token/s 吞吐、所以需 512 core ≈ 16 台 32-core CPU 服务器、独立于 GPU 推理集群部署避免 GPU 等 CPU。

Tokenizer 我选 **Hugging Face tokenizers (Rust)** 的 **SentencePiece + BPE**，因为 HF tokenizers 的 Rust 实现吞吐碾压 Python、SentencePiece 天然多语言无需预分词、与绝大多数 encoder checkpoint 一致、支持 fast batching。候选一是 **WordPiece** (BERT 原生)——英文为主领域兼容性最好、subword 边界稳定，但多语言场景在中日韩上分词密度不均、不如 SentencePiece 通用，WordPiece 更合适的位置是纯英文领域或已有 BERT 生态深度绑定的旧系统，所以不用。候选二是 **Unigram** (SentencePiece 内嵌模式之一)——基于概率选 subword、OOV 处理最稳，但训练 tokenizer 阶段开销大、工业部署 BPE 更普遍，Unigram 更合适的位置是研究迭代阶段探索 subword 质量。候选三是 **Byte-Pair Encoding** (BPE 纯粹模式)——GPT 系默认、字节级回退保证零 OOV，但对 CJK 分词效果不如 SentencePiece unigram，BPE 更合适的位置是代码/多语言混合纯字节处理场景。候选四是 **Character-level tokenizer**——最简单、零词表，但序列长度爆炸、transformer 吃不消，淘汰作默认。切换触发：纯英文单语言领域时可退 WordPiece；代码生成场景下叠字节级 BPE。

> **常见追问**:
> 1. "tokenizer 缓存怎么做？" —— 高频 query (搜索/客服) 前 1% query 占流量 30%+，用 LRU 缓存 token id 数组命中率 30-40%、CPU 压力直接减三分之一。
> 2. "多语言路由在 tokenizer 前还是后？" —— 前置——fastText langid / CLD3 在字节层面 1ms 判断语言、按语言分流到对应 tokenizer (中文 char-mix + SentencePiece / 英文 BPE)、避免单 tokenizer 处理多语言分词不均。
> 3. "模型 embedding 词表变了怎么办？" —— 词表冻结是硬约束、改词表必须重训模型；新增 special token 可热加载但需扩充 embedding 矩阵并微调。

### 事件总线与反馈回流 (2M QPS × 1KB = 2GB/s)

推理结果 + 原文 + label + 置信度约 1KB/条、2M QPS × 1KB = 2GB/s 入事件总线、日均 170TB raw 事件需分 sink 到 online 监控 (1% 采样) + 训练集 (按标签均衡下采) + DLQ (死信队列存低置信度样本走人工标注)。

事件总线我选 **Apache Kafka 128 partitions**，因为 Kafka 单 partition 20-30MB/s、128 partition 合计 3GB/s 留 1.5× headroom、exactly-once 语义保 label 回流不重复、与 Flink / Spark Streaming 原生集成、多消费组隔离训练 sink 与实时分析。候选一是 **Apache Pulsar**——多租户 + tiered storage 把冷日志下沉 S3、无缝 Functions，但运维复杂度高、社区规模弱于 Kafka、NLP 团队惯用 Kafka 栈，Pulsar 更合适的位置是强多租户 SaaS 平台场景，所以不用。候选二是 **AWS Kinesis**——托管省运维、Lambda 无缝整合，但 shard 上限低、跨云锁定、成本 3× Kafka 自建，Kinesis 更合适的位置是纯 AWS Lambda 栈场景，淘汰。候选三是 **Redpanda** (Kafka 兼容重写)——低延迟、C++ 实现、无 ZooKeeper，但生态成熟度与工具链不如 Kafka、企业支持较新，Redpanda 更合适的位置是对延迟极敏感且愿意押新栈的团队。候选四是 **NATS JetStream**——轻量云原生、边缘友好，但工具链与 Flink/Spark 集成不如 Kafka 成熟，NATS 更合适的位置是微服务事件总线而非 NLP 主流水线。切换触发：多团队强隔离 sink 时迁 Pulsar；全栈 serverless 化时评估 Kinesis。

### 特征与标签存储 (2M QPS × metadata + 历史标签库)

每 query 需读用户画像/历史/上下文 metadata (KV 存取 p99 < 5ms)、2M QPS × 读 3 key = 6M QPS；标签库 (gold label + 历史预测) 支持离线训练拉取、日均 2B 条增量、保留 90 天 = 180B 条 ≈ 30TB。

在线特征 KV 我选 **Redis Cluster**，因为单节点 100K-200K QPS、集群分片可线性扩到 10M QPS、p99 < 2ms 满足 5ms 预算、数据结构支持 hash/set 方便多字段读取。候选一是 **DynamoDB**——托管无运维、region 级 active-active、按需计费，但单位 QPS 成本 5-10× Redis 自建、跨 region 强一致延迟高、不适合超高 QPS 场景，DynamoDB 更合适的位置是中小团队或强合规托管场景，所以不用。候选二是 **Memcached**——单节点吞吐略高、内存使用紧凑，但无持久化 + 无复制 + 数据结构贫乏，Memcached 更合适的位置是纯缓存无状态场景，淘汰作默认。候选三是 **Aerospike**——NVMe 友好混合 SSD + 内存成本低、吞吐近 Redis，但学习曲线陡 + 社区规模小、运维工具链成熟度略低，Aerospike 更合适的位置是超大规模特征存储 (> 100TB hot) 的团队。候选四是 **ScyllaDB**——Cassandra 兼容 + 高吞吐，但 < 5ms p99 需要仔细调优，ScyllaDB 更合适的位置是时序特征或强一致需求场景。切换触发：规模 > 10M QPS 且 hot set > 100TB 时评估 Aerospike；跨 region 强一致需求时迁 DynamoDB/CockroachDB。

### 标注数据与离线训练语料 (100M labeled + 10B weak-label)

gold label 100M 条 × 2KB (文本+标签+metadata) = 200GB、weak-label (distill / self-training) 10B 条压缩后约 5TB、预训练额外参考数据 100TB。

标注数据湖我选 **S3 + Parquet + Iceberg**，因为 S3 字节成本 $0.023/GB/月、Parquet 列存压缩比 4-5×、Iceberg time-travel 让标签定义变更可复现追溯、与 Spark / Ray / PyTorch DataLoader 兼容性好。候选一是 **HDFS + Hive**——批处理适合但 NameNode 单点运维重、云原生方向工具链转 S3，HDFS 更合适的位置是私有云强合规场景，所以不用。候选二是 **Delta Lake**——ACID + schema evolution、时间旅行强，但 Databricks 绑定略重、云中立稍弱，Delta Lake 更合适的位置是 Databricks 深度用户。候选三是 **GCS + BigQuery**——GCP 原生 + 分析强，但跨云锁定、与 PyTorch connector 一层间接，GCS 更合适的位置是 Google Cloud 全家桶团队。候选四是 **自建对象存储 + 元数据层**——灵活度极高，但研发成本大、收益有限，自建更合适的位置是 FAANG 规模团队。切换触发：强 ACID 多作者写入时迁 Delta Lake；跨团队强合规数据域时自建元数据层。

这一节 takeaway：DistilBERT 300 实例推出 Triton + 8 卡 A10、Tokenizer 512 core 推出 HF Rust tokenizers、2GB/s 事件推出 Kafka 128p、Redis 10M QPS 推出在线特征 KV、S3+Iceberg 推出标注数据湖——这五个数字把 §3 的服务拆分边界画好。

## 3. High-Level Architecture (15m)

架构这一节要讲清两件事：服务怎么切——按 NLP 流水线层 + SLA + 模态切、而不是按业务域切；数据怎么流——端到端 Preprocessing → Classification/Labeling → Generation → Post-processing 的管线要让面试官一眼画出来。切分逻辑不是审美偏好而是 §2 数字直接推出：Tokenizer 的 CPU 层和 Encoder 的 GPU 层不能混部署、LLM fallback 的 2s 延迟不能拖垮 30ms 主路、MT 与摘要的 seq2seq 推理要独立于 encoder 集群。

服务拆分策略我选 **按 NLP 流水线层 + SLA + 模态切分**，因为 Text Preprocessor 2ms (CPU 归一化 / langid / 敏感词过滤) / Tokenizer 3ms (CPU subword) / Encoder Inference 20ms (GPU 编码器前向) / Task-specific Head 5ms (CPU softmax / CRF 解码) / Post-processor 5ms (CPU 结构化 + 脱敏) / LLM fallback 1-2s (GPU 大模型异步路径) 是六个独立 SLA + 两种资源类型 (CPU/GPU)，每层允许独立扩缩容、独立模型热加载、独立 A/B 分流；把这六层塞一个 "NLP Service" 会出现 LLM 尾延迟把 30ms 主路拖垮的级联故障。候选一是按 **业务域切分** (客服/评论/搜索/简历)——界面业务抄到后端、完全忽略 CPU vs GPU 与 SLA 差异、四条业务域独立部署会造成 encoder 模型重复加载、基础设施浪费 3-4×，淘汰。候选二是按 **模态切分** (短文本/长文本/多语言)——短文本 vs 长文本推理 batch 策略确实不同，但可以在 Encoder 层内部用多模型池表达、不值得全链路复制，模态切更适合已有成熟文本栈再扩展多模态 (图/音) 的阶段。候选三是按 **客户端切分** (Web/Mobile/API)——服务对客户端透明、客户端差异在 API Gateway 层解决即可，淘汰。切换触发：某 NLP 子任务 (如 MT) 流量占比 > 30% 时在 Encoder/Head 内拆出专用子集群；LLM fallback 占比 > 20% 时把 fallback 独立成 Tier-2 服务。

> **常见追问**:
> 1. "Tokenizer 和 Encoder 可以合并部署吗？" —— 不合适；Tokenizer 是 CPU-bound 且高并发 IO、Encoder 是 GPU-bound、共部署会造成 CPU 等 GPU 或 GPU 等 CPU、资源利用率双低；独立部署走 gRPC / Triton 内部通信 < 1ms 足够。
> 2. "LLM fallback 怎么判断何时触发？" —— 主路 encoder 输出 softmax 置信度 < 0.6 或 top-2 margin < 0.15 时走 fallback；fallback 路径异步 + 结果落库 + 回写主路训练反馈。
> 3. "多语言模型是单多语言 encoder 还是多个单语言 encoder？" —— XLM-R / mBERT 单多语言 encoder 在中低资源语言上表现更好、运维也简单；高资源单语言 (英/中) 可叠专用 single-language encoder 做精度冲刺、按 langid 路由。

端到端数据流：用户请求进 API Gateway → Rate Limit + Auth → Text Preprocessor (归一化 / 去噪 / langid) → Tokenizer (按语言路由 SentencePiece/BPE) → Encoder Inference (Triton dynamic batching + TensorRT) → Task-specific Head (分类 softmax / NER BIO 解码 / seq2seq decoder) → Post-processor (PII 脱敏 / 结构化 JSON / 引用回写) → 返回用户；异步 Kafka 记录原文 + 预测 + 置信度 → 低置信度样本入 DLQ 走人工标注队列 → 高置信度反馈入训练集；LLM fallback 作为独立子路径由 Router 触发。这条链路的关键不是"谁在前谁在后"，而是**每层都有独立 fallback**——Encoder 挂了走规则 / 上一版本回退、Head 挂了走 softmax argmax 简化、Post-processor 挂了走粗粒度正则脱敏、LLM fallback 挂了直接回 low-confidence + 默认类、完整链路允许 2 层同时降级仍返回可用结果。

这一节 takeaway：NLP 系统的服务边界不是业务边界而是 NLP 流水线层 + SLA + 资源类型边界；任一层必须自带 fallback、LLM fallback 的 2s 延迟与主路 30ms SLA 的隔离是整条链路最大的耦合点。

## 4. Deep Dives

这一节把 NLP 核心四块 (Tokenization / Encoder / Task Heads / Generation + Distillation) 逐一展开，每一块给出默认 pick、三个候选方案、逐个 why-not、切换触发条件与常见追问。读完这四个子节，可以把"NLP 系统每层选型"的工具箱摆清楚、回答面试官任意单层深挖不卡壳。整章编排顺序贴合在线 serving 调用顺序：Tokenization 是入口底座、Encoder 是共享骨架、Task Heads 决定任务输出、Generation + Distillation 决定长尾与成本。

### 4a. Encoder Architecture (编码器骨架)

编码器的任务是把 tokenized 文本压成稠密表示、供下游分类/标注/seq2seq 头使用。主流选型在 BERT-family (encoder-only) 与 encoder-decoder / decoder-only LLM 之间，判别式 NLP 主路默认 encoder-only。

编码器我选 **DistilBERT + 按任务蒸馏到领域**，因为 DistilBERT 在 GLUE 公开基准上保留 BERT-base 97% 质量、参数量仅 66M (40% of BERT-base)、推理吞吐 2× BERT-base、与 HF / Triton 生态无缝、单卡 A10 可并发 40+ 实例、满足 2M QPS × 30ms 预算。候选一是 **BERT-base** (110M 原始双向编码)——精度最稳、公开 checkpoint 最成熟，但 2× DistilBERT 的推理成本、对 2M QPS 场景直接翻倍集群规模，BERT-base 更合适的位置是精度极度敏感且 QPS 较低 (< 500K) 的领域 NLP，所以不用。候选二是 **RoBERTa** (更大批量 + 更长训练的 BERT 改进)——精度比 BERT-base 高 1-2 个点、下游任务稳定，但参数量与推理成本同 BERT-base、对在线 serving 成本敏感场景性价比低，RoBERTa 更合适的位置是离线批量任务或头部精度要求极高的核心链路。候选三是 **DeBERTa-v3** (Disentangled Attention + ELECTRA 式预训练)——精度领先开源榜单 2-3 个点，但参数量 184M、推理成本高、kernel 优化成熟度略低，DeBERTa 更合适的位置是头部业务精度追求极致 + 可以接受 3× 成本的场景。候选四是 **Electra-small** (replaced token detection 预训练)——参数 14M 极小、推理极快，但下游任务精度下限比 DistilBERT 低 1-2 个点、多语言覆盖差，Electra-small 更合适的位置是端侧或极低延迟 (p99 < 5ms) 场景。候选五是 **XLM-RoBERTa** (多语言 100 种语言)——多语言迁移最好，但参数 270M、单语场景浪费，XLM-R 更合适的位置是真正的多语言业务 (翻译 / 跨语言检索)。切换触发：多语言场景主路换 XLM-R；端侧 / 边缘部署降到 Electra-small；精度红线摇摆时从 DistilBERT 升 RoBERTa/DeBERTa。

> **常见追问**:
> 1. "DistilBERT 蒸馏原理是什么？" —— 学生模型在 BERT 教师模型的 soft logits (带温度 T 的 softmax) + hard label + cosine embedding 三重损失下训练；蒸馏不等于简单剪枝、知识传递质量高。
> 2. "DistilBERT 与 TinyBERT 谁更好？" —— TinyBERT 参数更少 (14.5M)、推理更快，但蒸馏流程复杂 (两阶段) + 适配新领域需要重跑；DistilBERT 工程实用性更高、默认首选；极端资源约束下退 TinyBERT。
> 3. "如何在线持续更新编码器？" —— 金丝雀灰度 + shadow 流量比较预测差异 + PSI/KS 漂移监控 + 标签回流 delta 触发再训练；encoder 参数变化要一并灰度 task head (head 依赖 encoder 特征空间)。

### 4b. Classification & Sequence Labeling (分类与序列标注)

分类头决定"短文本单标签/多标签"的输出、序列标注头决定"NER/SRL/POS"的输出。这两类任务是判别式 NLP 的主力、占聚合流量 > 80%。选型本质是"编码器 hidden state → 任务输出"的解码层。

多分类头我选 **标准 Linear + Softmax 头**，因为 Linear + Softmax 是 transformer 判别式 NLP 默认、配合 label smoothing 与 class-weighted cross-entropy 可以处理 90% 常规多分类场景、实现最简单、推理最快。候选一是 **Prototypical Network** (原型网络)——少样本泛化好、embedding 空间显式、新类零样本迁移，但标签全量微调场景收益有限、实现复杂度高，Prototype 更合适的位置是类目频繁新增且样本稀缺的场景 (如商品类目)，所以不用。候选二是 **Contrastive Learning Head** (对比学习头)——embedding 质量好、用 InfoNCE 训练，但需要成对样本构造、离线训练 pipeline 更重，Contrastive 更合适的位置是检索式分类或 embedding 复用给下游搜索的场景，淘汰作默认。候选三是 **Label-embedding Attention** (LEAM / LAAT)——把标签本身做 embedding 与文本交互、支持 zero-shot 新类，但推理更慢、工程复杂度高，LEAM 更合适的位置是极端多标签 (1M+ 标签) 场景。候选四是 **Zero-shot NLI-based Classifier** (如 bart-large-mnli)——把分类转 entailment 推理、无需标注，但推理延迟 5-10× 常规 head、精度不如有监督，Zero-shot 更合适的位置是冷启或长尾无标注类目、作 LLM fallback 一部分。切换触发：类目频繁变动时引入 Prototype/Zero-shot 混合；多标签极端规模时迁 LEAM。

序列标注我选 **Span-based Classification Head + nested NER 支持**，因为 span-based head 在每对 (start, end) token pair 上做 softmax 输出实体类别、天然支持嵌套实体 (nested NER)、避免 BIO 解码的标注歧义、主流 SOTA (2022+) 已从 BIO 切到 span。候选一是 **BIO / BILOU Tagging + CRF** (经典序列标注)——实现最成熟、工具链稳定，但不支持嵌套实体、BIO 解码阶段需要 Viterbi 额外 5-10ms 延迟、对复杂实体边界处理弱，BIO+CRF 更合适的位置是简单平坦实体场景 (如人名/地名/组织) 或已有 CRF 训练基建的旧系统，所以不用。候选二是 **Pointer Network / Boundary Detection**——直接预测每个实体的 (start, end) 指针对、训练目标清晰，但对密集实体场景训练不稳，Pointer 更合适的位置是每文档实体数较少且边界清晰的场景，淘汰作默认。候选三是 **Transformer-CRF** (CRF 接在 Transformer 上面)——比纯 softmax 序列标注精度稍高、全局归一化，但训练推理都慢 3-5×、Span-based 已接近或超越精度，Transformer-CRF 更合适的位置是标签数极多且需全局依赖的场景。候选四是 **LLM Prompt-based NER** (zero-shot)——无需微调、新实体零样本迁移，但推理延迟 100× span-based、不适合 100K+ QPS 主路，LLM prompt NER 更合适的位置是冷启或极长尾新实体类别。切换触发：嵌套实体占比 < 5% 且标注成熟时可退 BIO+CRF 省延迟；LLM 推理成本下降 10× 后考虑 zero-shot fallback。

> **常见追问**:
> 1. "class imbalance 10:1 以上怎么办？" —— focal loss (γ=2) + class-weighted 采样 + threshold calibration (Platt scaling) 三件套；评估用 PR-AUC 而非 accuracy / F1；极端头部类目 downsample + 长尾类目 SMOTE-BERT。
> 2. "标签噪声 gold label 本身 5-10% 错怎么办？" —— 软标签 + label smoothing + Co-teaching (两模型互训丢弃高 loss 样本) + confident learning 滤错标；高噪声领域引入 noise-aware loss (GCE / SCE)。
> 3. "Span-based NER 怎么加速推理？" —— 只枚举长度 ≤ 16 的 span (覆盖 99% 实体)、全对候选 O(n × 16) 线性、推理时间 < 30ms；超长实体 (法律条文 / 合同) 提升到 64。

### 4c. MT, Summarization & LLM Fallback (翻译、摘要与 LLM 兜底)

生成式子任务 (机器翻译 / 摘要 / query 改写) 走 seq2seq 路径、与 encoder 判别式主路分集群。LLM fallback 是主路置信度不足时的统一兜底 (细节指向 id=97、本节只讲触发与路由)。LLM fallback 上由 id=97 的 vLLM Continuous Batching + KV cache 把 TTFT 压到 < 300ms、叠 Semantic Cache 把重复问答命中率 15%+、prompt 里用 **Few-shot** 示例 + **Chain-of-Thought** 提示减少 Hallucination (幻觉)、流式返回走 **Server-Sent Events** (SSE, 服务器发送事件) 保持顺滑感知、复杂推理在 prompt 前叠 Chain-of-Thought "先拆解再回答"、领域定制走 **LoRA** adapter 按业务热切换。

MT / 摘要骨架我选 **Flan-T5-base** (encoder-decoder 多任务指令微调)，因为 Flan-T5 在翻译/摘要/改写多任务上 SOTA 级别、指令驱动减少任务切换开销、参数量 220M 可单卡部署、与 HF 生态深度兼容、multilingual 版本覆盖 100+ 语言。候选一是 **Marian MT** (专精 MT 小模型)——纯 MT 速度极快、每对语言独立模型，但任务不通用、摘要/改写需要另外模型、维护 O(语言对数) 个模型成本高，Marian 更合适的位置是 MT 极致速度且只做几对主流语言 (en-zh / en-ja) 的场景，所以不用。候选二是 **BART-large** (encoder-decoder 重建式预训练)——摘要任务默认强、精度高，但参数 400M、推理慢、不带多任务指令微调，BART 更合适的位置是纯摘要且离线批量的场景。候选三是 **LLM Prompt (Llama-3-8B / GPT-4)**——zero-shot 能力强、无需微调、覆盖面广，但推理延迟 10-100× T5、成本数量级高，LLM 更合适的位置是长尾/低 QPS/复杂 reasoning 任务 (作 fallback)。候选四是 **mT5-small** (多语言 T5 小模型)——多语言覆盖好、参数 300M，但精度不如 Flan-T5、未做指令微调，mT5 更合适的位置是强多语言 + 资源紧的场景。切换触发：单对语言极致速度时退 Marian；长尾任务覆盖不足时叠 LLM fallback (走 id=97 集群)。

LLM fallback 路由我选 **置信度阈值 + task-complexity classifier 双闸门**，因为单阈值 0.6 易把"本来就不确定"的样本都灌 LLM、成本爆炸；叠一个轻量 complexity classifier (判断"是否值得走 LLM") 可以把 fallback 流量从 15% 压到 3-5%、成本可控。候选一是 **纯置信度阈值**——实现最简、逻辑清晰，但对 encoder 过度自信 / miscalibrated 样本无能为力，纯阈值 更合适的位置是 calibrated encoder + 任务复杂度均匀的场景，所以不叠一层用。候选二是 **Random Sampling**——随机 5% 走 LLM 做质量采样，但随机对 low-confidence 与 high-confidence 样本无区分、大部分 LLM 调用浪费，Random 更合适的位置是 LLM-as-Judge 监督抽样而非主路兜底。候选三是 **Cascade Model** (多级小模型逐层放行)——每级按阈值放行，但运维复杂度 3-5×、每级均需训练评估，Cascade 更合适的位置是已有成熟多级 ensemble 生态的团队。候选四是 **Temperature Scaling Only**——对 softmax 做温度校准、改善置信度分布，但只改输出分布不改路由、仍需外层路由决策，Temperature 是必备基础但不独立作 fallback 决策。切换触发：流量扩大到成本敏感阶段加 complexity classifier；A/B 显示随机抽样 LLM 质量差异大时加权重采样。

> **常见追问**:
> 1. "如何评估 MT 质量？" —— chrF++ / COMET (神经评估) 作主指标、BLEU 作 legacy 对比 + 人工 pairwise 抽样校验；注意 reference-free COMET-22 对低资源语言的 bias。
> 2. "摘要 extract vs abstract 怎么选？" —— 高合规要求 (法律/医疗/新闻) 走 extractive 保证 faithfulness、商品描述/博客走 abstractive 保流畅；abstractive 必须叠 NLI 事实性打分监控。
> 3. "LLM fallback 走哪个模型？" —— 指向 id=97 的 vLLM 集群；生产 70B 作精度上限、13B 作主力 fallback、7B 作批量补全；LLM 结果回写训练集蒸馏回 DistilBERT 闭环。

### 4d. Distillation, Serving & Evaluation (蒸馏、服务化与评估)

持续把 LLM 的推理能力蒸馏回小 encoder 是 NLP 系统成本可持续的核心杠杆。评估侧除了传统 F1/AUC 要补上 calibration / drift / robustness 三项。

蒸馏策略我选 **Task-specific Distillation + Pseudo-label from LLM**，因为这套策略把 LLM (教师) 在未标注语料上生成 pseudo-label → DistilBERT (学生) 监督微调 → 灰度替换老版本的闭环 8 周内可跑通、成本 / 质量 tradeoff 清晰。候选一是 **General Knowledge Distillation** (通用蒸馏、TinyBERT 风格)——学生模拟教师中间层 hidden state 与 attention map、通用性好，但训练流程复杂 (两阶段) + 下游任务仍需微调，General KD 更合适的位置是基础模型压缩而非任务适配，所以不用。候选二是 **Self-Distillation** (同架构小模型互教)——无教师依赖、训练简单，但天花板受限于自己、收益有限，Self-Distill 更合适的位置是模型大小相近互补场景。候选三是 **Quantization Aware Training (QAT)**——保持精度 + INT8 推理、吞吐 2×，但训练成本高、与蒸馏正交可叠加，QAT 更合适的位置是精度敏感 + 推理成本敏感双约束场景 (可与 distillation 叠)。候选四是 **Pruning** (结构化剪枝)——参数减半吞吐升，但 transformer 结构化剪枝成熟度低 + 精度下降明显，Pruning 更合适的位置是研究或后处理阶段而非主路径。切换触发：精度红线与推理成本双紧时叠 QAT + Distillation；极限瘦身端侧部署时评估 Pruning。

评估与监控我选 **F1 + ECE (Expected Calibration Error) + PSI drift + robustness (TextAttack) 四件套**，因为 F1 是分类 SOTA 指标、ECE 捕捉 miscalibration (softmax 过度自信)、PSI (Population Stability Index) 监控标签与特征分布漂移、TextAttack 对抗样本测试鲁棒性；四件套覆盖准确性 / 可信度 / 稳定性 / 抗扰四维。候选一是 **纯 F1 / accuracy**——最直观、工业默认，但对 miscalibration 与漂移完全看不见、单指标坑多，纯 F1 更合适的位置是 MVP 阶段基线，所以不用。候选二是 **AUC 主导**——类不均衡场景 AUC 稳定，但多分类扩展 AUC 成 macro-AUC 可解释性下降、无法替代 calibration，AUC 更合适的位置是二分类主场景 (点击预测 / 欺诈)。候选三是 **LLM-as-Judge 抽样评估**——对生成式子任务 (MT/摘要) 质量评估好，但对判别式分类过度杀鸡用牛刀，LLM-judge 更合适的位置是生成式输出质量监控 (见 id=97 §4d)。候选四是 **Model Drift 单维监控 (KS/JSD)**——drift 敏感但对 calibration 盲、与 PSI 功能重叠，单维 drift 更合适的位置是补充 PSI 异常诊断。切换触发：生成式子任务占比上升 (MT/摘要 > 20%) 时叠 LLM-as-Judge；calibration 红线持续失守时升级为独立 calibration 仪表板 + Temperature Scaling 训练。

> **常见追问**:
> 1. "蒸馏后精度和教师差多少可接受？" —— 通用经验 2-4% 绝对下降可接受 (DistilBERT-base vs BERT-base)、超过 5% 说明学生容量或训练不足；关键业务指标 (e.g. F1) 单项不得降超过 1.5%。
> 2. "ECE 大于多少需要告警？" —— 二分类 ECE > 0.05 (5%) 开始关注、> 0.08 必须温度校准、> 0.12 线下重训 + temperature scaling；多分类看 macro-ECE。
> 3. "drift 检测 PSI 阈值？" —— 单特征 PSI > 0.1 关注、> 0.25 必须重训；聚合多特征加权看整体 PSI；label drift 看预测分布 PSI 配合 gold label 样本抽查。

这一节 takeaway：NLP 系统不是单模型、而是四块 (Encoder / Task Heads / Seq2seq + LLM / Distillation + Eval) 算法候选池的组合；每块默认方案都得搭配至少 3 个候选 + why-not + 切换条件，才算真正"讲透选型"。

## 5. Reliability (Monitoring & DR, 5m)

NLP 系统的可靠性不是"100% 不挂"，而是"每一层都有独立 fallback、整体降级到可接受质量 + 标签定义强一致广播、不把用户 PII 泄到不该去的地方"的分层容错。NLP 与通用 ML 的关键差异在于输入数据是自然语言文本——用户输入含有 Prompt Injection / jailbreak 攻击 / PII / 多语言噪声、输出若错分类会直接影响客服路由 / 搜索召回等下游业务。

监控策略我选 **四象限监控 + 数据分布专项**，因为系统/模型/内容/业务四个维度要分开看、数据分布专项独立于传统指标。系统层对接 **Prometheus + Grafana** 采集 p99 延迟、QPS、GPU 利用率、Tokenizer queue depth；模型层采集 F1/AUC/ECE、漂移 PSI、shadow vs prod 预测差异、LLM fallback 率；内容层监控输出分类分布、PII 泄露率、jailbreak 检测命中率、多语言路由错配率；业务层看客服工单误路由率、评论情感与销量相关性、搜索 CTR、人工审核队列长度。候选一是 **Datadog APM 单栈统一中台**——工具链简化但跨维度语义损失、模型质量维度看不出，Datadog 更合适的位置是中小团队省运维，所以不用。候选二是 **Arize / WhyLabs 独立 ML 监控**——ML 专用指标全、embedding drift 分析成熟，但与系统监控割裂、告警链路双头，Arize 更合适的位置是 ML ops 团队独立于平台团队时，淘汰作默认。候选三是 **Evidently AI** (开源 drift 监控)——免费、开源、drift 指标全，但缺少系统侧 SLA 监控与告警路由，Evidently 更合适的位置是补充到现有栈做 drift 专项。候选四是 **自建 full-stack 监控**——灵活度最高但研发成本大，自建更合适的位置是 FAANG 规模团队。切换触发：生成式子任务占比上升时叠 Arize/Fiddler；drift 成核心故障源时引入 Evidently 专项。

降级预案：Encoder 主模型挂了 fallback 到上一版本模型或规则基线；Task Head 挂了走 encoder-only embedding + 最近邻检索兜底；LLM fallback 挂了走拒绝返回 low-confidence；Post-processor 挂了走粗粒度正则脱敏；Tokenizer 挂了走字符级回退 tokenize；每条 fallback 路径必须独立演练、月度 game day 强制跑一次、PII/safety 事故 PIR 48h 内出。隐私合规方面：PII 脱敏在 Post-processor + Pre-inference 双路 (NER 检出 PII → mask 后再进 encoder 避免 memorization attack)、训练数据 PII 扫描 + differential privacy 防 extraction attack、label 回流先经审核后入训练集；GDPR 被遗忘权要求按用户 ID 级联清除含 fine-tuning 数据集样本；多语言合规按 region 独立 label set 避免跨境敏感分类 (如政治/宗教) 扩散。安全侧 **Red Teaming** (红队测试) 周期性演练 jailbreak / prompt injection 攻击面、LLM fallback 路径叠一层输出分类器防止 Hallucination 与有害内容流出。

这一节 takeaway：reliability 不在单点高可用而在分层可降级 + 数据分布监控 + PII 合规三者缺一不可；四象限监控 + 每层独立 fallback + 标签定义强一致广播是 NLP 系统的可靠性铁三角。

## 6. Summary & Tradeoffs

本题核心 takeaway 是 NLP 系统的"encoder 判别式主路 + LLM 兜底长尾"双路径思维：2M QPS × 30ms 主路靠 DistilBERT + Triton + 蒸馏，长尾 15% 复杂请求由 LLM fallback 兜底不过主路。编码器默认 DistilBERT、Tokenizer 默认 HF Rust + SentencePiece、多分类默认 Softmax、NER 默认 Span-based、MT/摘要默认 Flan-T5、LLM fallback 路由默认置信度 + complexity classifier 双闸门、蒸馏默认 Pseudo-label KD、评估默认 F1+ECE+PSI+robustness。基础架构演进链条 Word2vec → BERT → DistilBERT → LLM-augmented 判别式；任务头演进链条 BIO+CRF → Span-based → LLM Prompt；评估演进链条 Accuracy → F1 → ECE/Drift/Robustness 多维。

三个最常被错答的 tradeoff：一是"encoder 判别式还是 LLM 生成式做分类"——不是谁先进，而是 QPS × 延迟 × 成本的 tradeoff，2M QPS 主路 encoder 胜、长尾复杂场景 LLM 胜；二是"BIO+CRF 还是 Span-based NER"——不是新就好，Span 处理嵌套实体更稳但若实体扁平 BIO+CRF 省延迟 5-10ms；三是"Fine-tune 还是 Prompt 做新任务"——成熟业务 fine-tune 胜、冷启或长尾 prompt 胜、两者可共存用 complexity classifier 路由。长期优化依赖**闭环飞轮**：低置信度样本 → 人工标注 → 训练集 → 重训 encoder → 替换、LLM pseudo-label → 蒸馏回 encoder → 长期降低 fallback 率；同时警惕"指标过拟合" (F1 高但 calibration 差)、"多语言不均衡" (高资源语言吃掉优化)、"标签定义漂移" (业务侧悄悄改了定义没广播)。

工程 vs 建模的决策拉锯主要在三处：一是编码器在 DistilBERT 与 RoBERTa/DeBERTa 之间取舍——推理成本与精度红线的 tradeoff；二是序列标注在 BIO+CRF 与 Span-based 之间取舍——延迟与嵌套实体支持的 tradeoff；三是长尾在 LLM fallback 与 zero-shot classifier 之间取舍——成本与质量的 tradeoff。选型的真正判据不是"谁更先进"，而是"当前业务的 QPS 量级、SLA 预算、标签成熟度、多语言覆盖需求落在哪个拐点"。

## Interview Q&A

下面三个问题是本题高频被追问的边界题，每个都有典型陷阱：

第一题："客服工单分类上线后运营反馈新品类漏召回、旧品类误判上升怎么办？"——这是典型 label drift + concept drift 混合问题。答案思路：一是以 PSI 指标监控特征分布漂移 + 预测分布漂移、定位是输入 drift 还是 label 定义变了；二是拉取最近 7 天低置信度样本 + 人工复审 → 新品类可能是真漂移、旧品类可能是标签定义业务侧改了没广播；三是紧急方案 temperature scaling + threshold re-tune 先稳住召回、长期重训 + 扩充新类样本；四是建立标签定义变更的 PR Review 流程 + 自动化下游通知。

第二题："多语言 NER 在低资源语言 (斯瓦希里 / 越南 / 印地) 的 F1 掉 20 个点怎么办？"——这是跨语言迁移的硬题。答案思路：一是检查 XLM-R / mBERT 训练语料在这些语言的占比 (通常 < 1%)；二是做 cross-lingual transfer learning + 高资源语言标注数据 zero-shot / few-shot 迁移；三是主动标注 1K-10K 条低资源样本做微调、配合 data augmentation (back-translation / synonym substitution)；四是长期推动 multilingual data collection pipeline + 社区众包；五是部署上用单语言小模型 + 多语言 XLM-R 混合路由、按 langid 选择。

第三题："2M QPS 下 DistilBERT 集群 GPU 利用率只有 30%、p99 延迟却已到 SLA 边缘怎么办？"——这是 serving 调优的经典题。答案思路：一是检查 Triton dynamic batching 配置、max_batch_size 与 max_queue_delay 是否合理、目标 GPU 利用率 70%+；二是排查 CPU 预处理瓶颈 (tokenizer / serialization) 把 GPU 饿着、独立 CPU 扩容；三是量化 FP16 → INT8 借 TensorRT 推理吞吐 2×；四是 TensorRT kernel fusion + sequence padding 对齐;五是长尾长 query 独立 batch 池避免尾延迟拖累短 query；六是监控 batch-size 分布 + queue depth + GPU SM 利用率三张图定位瓶颈。

## Self-Check

自检清单：我离开白板之前，对着下面八个问题能不看稿答对吗？(1) 主路 encoder 判别式 vs LLM 生成式的路由闸门 + 触发条件；(2) 每层默认模型与它的 3 个候选 + why-not；(3) DistilBERT / BERT-base / RoBERTa / DeBERTa / XLM-R 五种编码器的 tradeoff 与切换触发；(4) HF Rust Tokenizers / WordPiece / Unigram / BPE 四种 tokenizer 的切换条件；(5) Linear-Softmax / Prototype / Contrastive / Zero-shot NLI 四种分类头的适用场景；(6) BIO+CRF / Span-based / Pointer / LLM Prompt 四种 NER 方法的 tradeoff；(7) Flan-T5 / Marian / BART / LLM Prompt 四种 seq2seq 方法的切换条件；(8) F1 / ECE / PSI / TextAttack 四种评估维度的组合策略。八个都能答对就可以去白板了。
